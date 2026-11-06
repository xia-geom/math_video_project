#!/usr/bin/env python3
"""Create hashed pip requirements from resolver reports and record native evidence.

Pip performs resolution. A projected target is checked against the report's
dependency metadata, but only a native install/test run validates that target.
Reports may contain index URLs: keep them temporary, never upload them raw.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import re
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from email.parser import Parser
from functools import lru_cache
from pathlib import Path

from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.utils import canonicalize_name

SHA256 = re.compile(r'[0-9a-f]{64}')
TARGETS = {
    'macos-arm64': {'sys_platform': 'darwin', 'platform_system': 'Darwin', 'platform_machine': 'arm64'},
    'linux-x86_64': {'sys_platform': 'linux', 'platform_system': 'Linux', 'platform_machine': 'x86_64'},
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def selected_packages(report, target, python_version):
    """Evaluate the resolved graph without pretending to resolve absent packages."""
    if report.get('version') != '1' or not isinstance(report.get('install'), list):
        raise ValueError('Expected a complete pip version-one installation report.')
    environment = {**report['environment'], **TARGETS[target]}
    environment.update(python_version=python_version, python_full_version=python_version + '.0')
    packages = {}
    pending = []
    for item in report['install']:
        metadata = item['metadata']
        name = canonicalize_name(metadata['name'])
        if item.get('is_direct') or item.get('is_yanked'):
            raise ValueError('Direct references and yanked releases cannot enter a public lock.')
        if name in packages:
            raise ValueError('Duplicate package in installation report.')
        packages[name] = item
        if item.get('requested'):
            extras = item.get('requested_extras', [])
            pending.append(Requirement(name + ('[' + ','.join(extras) + ']' if extras else '')))
    if not pending:
        raise ValueError('Report has no requested roots; regenerate with --ignore-installed.')
    selected = {}
    seen = set()
    while pending:
        requirement = pending.pop()
        name = canonicalize_name(requirement.name)
        if requirement.url:
            raise ValueError('Direct dependency references cannot enter a public lock.')
        if name not in packages:
            raise ValueError(f'Target requires {name}, absent from this report; resolve natively.')
        item = packages[name]
        metadata = item['metadata']
        version = metadata['version']
        if version not in requirement.specifier:
            raise ValueError(f'Resolved {name} does not satisfy the target dependency graph.')
        if environment['python_full_version'] not in SpecifierSet(metadata.get('requires_python', '')):
            raise ValueError(f'Resolved {name} does not support Python {python_version}.')
        extras = tuple(sorted(requirement.extras))
        selected.setdefault(name, {'version': version, 'extras': set(), 'item': item})['extras'].update(extras)
        if (name, extras) in seen:
            continue
        seen.add((name, extras))
        for value in metadata.get('requires_dist', []):
            dependency = Requirement(value)
            if dependency.marker is None or any(
                dependency.marker.evaluate({**environment, 'extra': extra}) for extra in ('', *extras)
            ):
                pending.append(dependency)
    return selected


@lru_cache(maxsize=None)
def release_hashes(name, version):
    """Fetch only public PyPI metadata; return hashes, never index or artifact URLs."""
    request = urllib.request.Request(
        f'https://pypi.org/pypi/{name}/{version}/json',
        headers={'Accept': 'application/json', 'User-Agent': 'math-video-environment-lock/1'},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)
    hashes = {item['digests']['sha256'] for item in data['urls'] if not item.get('yanked')}
    if not hashes or any(not SHA256.fullmatch(value) for value in hashes):
        raise ValueError(f'No valid release hashes for {name}.')
    return hashes


def requirement_text(name, version, extras, hashes):
    label = name + ('[' + ','.join(sorted(extras)) + ']' if extras else '')
    return label + '==' + version + ' \\\n' + ' \\\n'.join(
        '    --hash=sha256:' + value for value in sorted(hashes)) + '\n'


def report_lock(report, target, python_version, inputs=()):
    targets = tuple(TARGETS) if target == 'portable' else (target,)
    selections = [selected_packages(report, value, python_version) for value in targets]
    selected = selections[0]
    if any({name: (item['version'], item['extras']) for name, item in other.items()}
           != {name: (item['version'], item['extras']) for name, item in selected.items()}
           for other in selections[1:]):
        raise ValueError('Portable profile has platform-specific dependencies; use target locks.')
    with ThreadPoolExecutor(max_workers=8) as executor:
        hashes = dict(zip(selected, executor.map(
            lambda name: release_hashes(name, selected[name]['version']), selected)))
    for name, package in selected.items():
        resolved_hash = package['item'].get('download_info', {}).get('archive_info', {}).get('hashes', {}).get('sha256')
        if not resolved_hash or resolved_hash not in hashes[name]:
            raise ValueError(f'Resolver artifact for {name} is not a hashed PyPI release.')
    source = report['environment']
    lines = [
        '# Generated by scripts/environment_lock.py; do not edit package entries.\n',
        f'# Target: CPython {python_version}; {target}.\n',
        f"# Resolver: pip {report['pip_version']}; Python {source['python_full_version']}; "
        f"{source['platform_system']} {source['platform_machine']}.\n",
        '# Includes published wheel/sdist hashes; source builds need the separate build lock.\n',
        '# Target metadata validation is not proof of a native installation or render.\n',
    ]
    for path in inputs:
        lines.append(f'# Input-SHA256: {path.as_posix()} {digest(path)}\n')
    return ''.join(lines) + '\n' + '\n'.join(
        requirement_text(name, item['version'], item['extras'], hashes[name])
        for name, item in sorted(selected.items()))


def read_lock(path):
    packages = {}
    for line in Path(path).read_text().replace('\\\n', ' ').splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        pieces = line.split()
        requirement = Requirement(pieces[0])
        pins = list(requirement.specifier)
        if (requirement.url or requirement.marker or len(pins) != 1
                or pins[0].operator != '==' or '*' in pins[0].version
                or len(pieces) < 2 or any(not value.startswith('--hash=sha256:')
                                        or not SHA256.fullmatch(value[14:]) for value in pieces[1:])):
            raise ValueError('Lock entries must be exact versions with SHA-256 hashes only.')
        name = canonicalize_name(requirement.name)
        if name in packages:
            raise ValueError('Duplicate package in lock.')
        packages[name] = {'version': pins[0].version, 'extras': requirement.extras}
    if not packages:
        raise ValueError('Empty environment lock.')
    return packages


def wheel_lock(folder, source):
    """Bind a native wheel bundle to its resolved package set and actual bytes."""
    expected = read_lock(source)
    found = {}
    for path in sorted(Path(folder).glob('*.whl')):
        if path.is_symlink():
            raise ValueError('Wheel bundle cannot contain symlinks.')
        with zipfile.ZipFile(path) as archive:
            metadata = [name for name in archive.namelist()
                        if name.count('/') == 1 and name.endswith('.dist-info/METADATA')]
            if len(metadata) != 1:
                raise ValueError('Wheel must declare exactly one distribution.')
            record = Parser().parsestr(archive.read(metadata[0]).decode('utf-8'))
        name = canonicalize_name(record['Name'])
        if name not in expected or record['Version'] != expected[name]['version']:
            raise ValueError('Wheel bundle differs from the resolved lock.')
        found.setdefault(name, set()).add(digest(path))
    if found.keys() != expected.keys():
        raise ValueError('Wheel bundle is missing required distributions.')
    return '# Native wheel bundle; install with --no-index --require-hashes.\n\n' + '\n'.join(
        requirement_text(name, item['version'], item['extras'], found[name])
        for name, item in sorted(expected.items()))


def command_version(command):
    if not shutil.which(command[0]):
        return None
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=15, check=False)
        return result.stdout.splitlines()[0].strip() if result.returncode == 0 and result.stdout else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def native_packages():
    """Record selected package-manager versions without dumping machine state."""
    if platform.system() == 'Linux' and shutil.which('dpkg-query'):
        command = ['dpkg-query', '-W', '-f=${binary:Package}\t${Version}\n',
                   'build-essential', 'pkg-config', 'libcairo2-dev', 'libpango1.0-dev',
                   'ffmpeg', 'sox', 'patchelf', 'dvisvgm', 'texlive-latex-extra',
                   'texlive-fonts-recommended', 'texlive-fonts-extra', 'texlive-science',
                   'fonts-dejavu-core']
    elif platform.system() == 'Darwin' and shutil.which('brew'):
        command = ['brew', 'list', '--versions', 'cairo', 'pango', 'ffmpeg', 'sox',
                   'pkgconf', 'fontconfig', 'freetype']
    else:
        return {}
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30, check=False)
        return {pieces[0]: ' '.join(pieces[1:]) for line in result.stdout.splitlines()
                if len(pieces := line.split()) >= 2}
    except (OSError, subprocess.TimeoutExpired):
        return {}


def font_match(name):
    family = command_version(['fc-match', '-f', '%{family}\n', name])
    filename = command_version(['fc-match', '-f', '%{file}\n', name])
    try:
        fingerprint = digest(filename) if filename and Path(filename).is_file() else None
    except OSError:
        fingerprint = None
    matches = (name.casefold() in {value.strip().casefold() for value in family.split(',')}
               if family else None)
    return {'family': family, 'matches_requested_family': matches, 'file_sha256': fingerprint}


def python_packages():
    versions = {}
    for distribution in importlib.metadata.distributions():
        name = canonicalize_name(distribution.metadata['Name'])
        versions.setdefault(name, set()).add(distribution.version)
    selected = {name: importlib.metadata.version(name) for name in sorted(versions)}
    conflicts = {name: sorted(values) for name, values in versions.items() if len(values) > 1}
    return selected, conflicts


def inventory():
    """Allowlisted environment facts; no environment dump or direct-install URLs."""
    commands = {'ffmpeg': ['ffmpeg', '-version'], 'ffprobe': ['ffprobe', '-version'],
                'latex': ['latex', '--version'], 'dvisvgm': ['dvisvgm', '--version'],
                'sox': ['sox', '--version'], 'compiler': ['cc', '--version'],
                'meson': ['meson', '--version'], 'ninja': ['ninja', '--version'],
                'patchelf': ['patchelf', '--version']}
    packages, conflicts = python_packages()
    try:
        os_version = (platform.mac_ver()[0] if platform.system() == 'Darwin'
                      else platform.freedesktop_os_release().get('VERSION_ID'))
    except OSError:
        os_version = None
    result = {'python': platform.python_version(), 'implementation': platform.python_implementation(),
              'system': platform.system(), 'machine': platform.machine(),
              'os_version': os_version, 'kernel_release': platform.release(), 'libc': platform.libc_ver(),
              'packages': packages, 'conflicting_distribution_versions': conflicts,
              'native_tools': {name: command_version(command) for name, command in commands.items()},
              'native_packages': native_packages(),
              'native_libraries': {name: command_version(['pkg-config', '--modversion', name])
                                   for name in ('cairo', 'pango', 'pangocairo', 'fontconfig', 'freetype2')},
              'font_matches': {name: font_match(name) for name in ('DejaVu Sans', 'Roboto')}}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest='command', required=True)
    generate = subparsers.add_parser('from-report')
    generate.add_argument('--report', type=Path, required=True)
    generate.add_argument('--target', choices=(*TARGETS, 'portable'), required=True)
    generate.add_argument('--python-version', choices=('3.11', '3.13'), required=True)
    generate.add_argument('--input', type=Path, action='append', default=[])
    generate.add_argument('--output', type=Path, required=True)
    wheels = subparsers.add_parser('wheel-lock')
    wheels.add_argument('--wheel-dir', type=Path, required=True)
    wheels.add_argument('--source-lock', type=Path, required=True)
    wheels.add_argument('--output', type=Path, required=True)
    record = subparsers.add_parser('inventory')
    record.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'from-report':
        content = report_lock(json.loads(args.report.read_text()), args.target, args.python_version, args.input)
    elif args.command == 'wheel-lock':
        content = wheel_lock(args.wheel_dir, args.source_lock)
    else:
        content = json.dumps(inventory(), indent=2, sort_keys=True) + '\n'
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(content, encoding='utf-8')
    print(f'Wrote {args.output.name}.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
