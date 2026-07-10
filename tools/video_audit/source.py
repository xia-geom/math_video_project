from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path


BOOKMARK_RE = re.compile(r"<bookmark\s+mark=[\"']([^\"']+)[\"']\s*/?>")
WAIT_RE = re.compile(r"wait_until_bookmark\(\s*[\"']([^\"']+)[\"']")
CAPTION_RE = re.compile(r"[\"']caption[\"']\s*:\s*([\"'])(.*?)\1", re.DOTALL)


@dataclass
class SourceInfo:
    path: Path
    text: str
    tree: ast.Module | None
    lines: list[str]
    bookmarks: list[str]
    waits: list[str]
    captions: list[tuple[str, int]]


def load_source(path: Path) -> SourceInfo:
    text = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text)
    except SyntaxError:
        tree = None
    lines = text.splitlines()
    bookmarks = BOOKMARK_RE.findall(text)
    waits = WAIT_RE.findall(text)
    captions = [(match.group(2), _line_number(text, match.start())) for match in CAPTION_RE.finditer(text)]
    return SourceInfo(path=path, text=text, tree=tree, lines=lines, bookmarks=bookmarks, waits=waits, captions=captions)


def has_class(source: SourceInfo, class_name: str) -> bool:
    if source.tree is None:
        return False
    return any(isinstance(node, ast.ClassDef) and node.name == class_name for node in source.tree.body)


def class_line(source: SourceInfo, class_name: str) -> int | None:
    if source.tree is None:
        return None
    for node in source.tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return node.lineno
    return None


def first_line_matching(source: SourceInfo, pattern: str) -> int | None:
    regex = re.compile(pattern)
    for idx, line in enumerate(source.lines, start=1):
        if regex.search(line):
            return idx
    return None


def has_call_or_name(source: SourceInfo, name: str) -> bool:
    if source.tree is None:
        return name in source.text
    for node in ast.walk(source.tree):
        if isinstance(node, ast.Name) and node.id == name:
            return True
        if isinstance(node, ast.Attribute) and node.attr == name:
            return True
    return False


def count_animation_calls(source: SourceInfo) -> int:
    return len(re.findall(r"\bself\.(?:play|play_paced)\(", source.text))


def has_final_wait(source: SourceInfo) -> bool:
    if _construct_has_final_wait(source):
        return True

    code_lines = [
        line
        for line in source.lines
        if line.strip() and not line.lstrip().startswith("#")
    ]
    tail = "\n".join(code_lines[-120:])
    return (
        re.search(r"\bself\.wait\(\s*(?:1(?:\.0)?|[2-9](?:\.\d+)?)\s*\)", tail)
        is not None
        or re.search(r"\bself\.wait_paced\(\s*(?:1(?:\.0)?|[2-9](?:\.\d+)?)\s*\)", tail)
        is not None
    )


def _construct_has_final_wait(source: SourceInfo) -> bool:
    if source.tree is None:
        return False
    for node in ast.walk(source.tree):
        if not isinstance(node, ast.FunctionDef) or node.name != "construct":
            continue
        if not node.body:
            continue
        last_statement_line = getattr(node.body[-1], "lineno", 0)
        end_line = getattr(node, "end_lineno", last_statement_line)
        final_region_start = max(last_statement_line, end_line - 35)
        for child in ast.walk(node):
            if getattr(child, "lineno", 0) < final_region_start:
                continue
            if _is_wait_call_at_least_one_second(child):
                return True
    return False


def _is_wait_call_at_least_one_second(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if not isinstance(func, ast.Attribute) or func.attr not in {"wait", "wait_paced"}:
        return False
    if not isinstance(func.value, ast.Name) or func.value.id != "self":
        return False
    if not node.args:
        return False
    first = node.args[0]
    if isinstance(first, ast.Constant) and isinstance(first.value, (int, float)):
        return float(first.value) >= 1.0
    return False


def has_plain_caption_source(source: SourceInfo) -> bool:
    text = source.text
    return bool(source.captions) or any(
        pattern in text
        for pattern in (
            "subcaption=",
            "_show_caption(",
            "add_subcaption(",
        )
    )


def has_ssml_narration(source: SourceInfo) -> bool:
    return (
        re.search(r"[\"']ssml[\"']\s*:", source.text) is not None
        or re.search(r"\btts\.ssml\(", source.text) is not None
        or re.search(r"\bssml\s*=\s*tts\.ssml\b", source.text) is not None
        or re.search(r"\bssml\(", source.text) is not None
    )


def has_manual_pacing(source: SourceInfo) -> bool:
    text = source.text
    return "narrated(" in text and any(
        pattern in text
        for pattern in (
            "play_paced(",
            "wait_paced(",
            "_wait_for_voice_end(",
            "_show_caption(",
        )
    )


def has_external_audio_workflow(source: SourceInfo) -> bool:
    return "add_sound(" in source.text or "audio_candidates" in source.text


def _line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1
