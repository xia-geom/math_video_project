from pathlib import Path

from tools.video_audit.media import parse_srt


def test_parse_srt_reads_basic_entries(tmp_path: Path) -> None:
    srt = tmp_path / "demo.srt"
    srt.write_text(
        """1
00:00:01,000 --> 00:00:02,500
Bonjour

2
00:00:03,000 --> 00:00:04,000
Suite
""",
        encoding="utf-8",
    )

    entries = parse_srt(srt)

    assert entries == [(1.0, 2.5, "Bonjour"), (3.0, 4.0, "Suite")]
