#!/usr/bin/env bash
set -euo pipefail
STUDY_ROOT="$(cd "$(dirname "$0")" && pwd)"
if [ -n "${STUDY_PYTHON:-}" ]; then
    exec "$STUDY_PYTHON" -X utf8 "$STUDY_ROOT/start-study.py" "$@"
fi
for STUDY_CANDIDATE in python3 python "$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; do
    if "$STUDY_CANDIDATE" -c 'import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)' >/dev/null 2>&1; then
        exec "$STUDY_CANDIDATE" -X utf8 "$STUDY_ROOT/start-study.py" "$@"
    fi
done
printf '%s\n' 'Python 3.9 이상이 필요합니다. README.md의 설치 방법을 참고하세요.' >&2
exit 1
