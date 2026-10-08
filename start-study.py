#!/usr/bin/env python3
"""Portable launcher for Windows, Linux, and macOS (Python 3.9+)."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
REPO = ROOT / 'linux'
SOURCE = 'https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git'
COMMIT = 'adc218676eef25575469234709c2d87185ca223a'

def git_executable():
    explicit = os.environ.get('STUDY_GIT')
    if explicit:
        candidate = shutil.which(explicit)
        if candidate:
            return candidate
        raise RuntimeError('STUDY_GIT에 지정한 Git 실행 파일을 찾을 수 없습니다.')
    candidates = []
    if sys.platform == 'darwin':
        candidates.extend(['/opt/homebrew/bin/git', '/usr/local/bin/git'])
    candidates.append(shutil.which('git'))
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            result = subprocess.run([candidate, '--version'], capture_output=True)
            if result.returncode == 0:
                return candidate
    raise RuntimeError('Git이 필요합니다. Git을 설치하고 터미널을 다시 열어주세요. README.md의 설치 방법을 참고하세요.')

def prepare(git):
    if not (REPO / '.git').is_dir():
        if REPO.exists() and any(REPO.iterdir()):
            raise RuntimeError('linux 폴더에 기존 파일이 있습니다. 내용을 확인한 뒤 다른 이름으로 옮겨주세요. 자동으로 덮어쓰지 않습니다.')
        print('처음 실행: 공식 Linux v6.12 전체 소스를 다운로드합니다. 인터넷 연결이 필요합니다.', flush=True)
        subprocess.run([git, 'clone', '--depth', '1', '--branch', 'v6.12', '--no-checkout', SOURCE, str(REPO)], check=True)
    actual = subprocess.run([git, '-C', str(REPO), 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
    if actual != COMMIT:
        raise RuntimeError('linux 폴더의 커널 버전이 학습 기준 v6.12와 다릅니다. 기존 소스를 보존하고 README.md의 새 설치 방법을 따라주세요.')
    os.environ['STUDY_GIT'] = git

def main():
    if sys.version_info < (3, 9):
        raise RuntimeError('Python 3.9 이상이 필요합니다.')
    parser = argparse.ArgumentParser(description='Linux 소스 학습실 실행')
    parser.add_argument('--port', type=int, default=None)
    parser.add_argument('--setup-only', action='store_true', help='소스만 준비하고 서버는 실행하지 않음')
    args = parser.parse_args()
    port = args.port if args.port is not None else int(os.environ.get('PORT', '8765'))
    if not 1 <= port <= 65535:
        raise RuntimeError('포트는 1부터 65535 사이로 지정해주세요.')
    prepare(git_executable())
    if args.setup_only:
        print('소스 준비 완료. 학습 서버를 실행할 수 있습니다.', flush=True)
        return 0
    return subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'tools' / 'study.py'), '--port', str(port)], cwd=ROOT).returncode

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('\n학습 서버를 종료했습니다.')
        sys.exit(0)
    except (RuntimeError, ValueError, OSError, subprocess.CalledProcessError) as error:
        print('실행하지 못했습니다: ' + str(error), file=sys.stderr)
        sys.exit(1)
