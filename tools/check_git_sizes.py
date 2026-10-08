#!/usr/bin/env python3
"""Reject oversized current files before committing; respects .gitignore."""
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
LIMIT = 50 * 1024 * 1024

def main():
    git = os.environ.get('STUDY_GIT') or ('/opt/homebrew/bin/git' if Path('/opt/homebrew/bin/git').exists() else shutil.which('git'))
    if not git:
        raise SystemExit('Git이 필요합니다.')
    paths = subprocess.check_output([git, 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT).decode('utf-8').split('\0')
    large = []
    for name in set(paths) - {''}:
        path = ROOT / name
        if path.is_file() and path.stat().st_size >= LIMIT:
            large.append((path.stat().st_size, name))
    for size, name in sorted(large, reverse=True):
        print(f'{size / 1024 / 1024:.2f} MiB: {name}')
    if large:
        print('50 MiB 이상 파일을 분할하거나 생성 캐시를 Git에서 제외하세요.')
        return 1
    print('PASS: Git에 올릴 현재 파일은 모두 50 MiB 미만입니다.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
