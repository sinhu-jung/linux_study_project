#!/bin/bash
set -euo pipefail
export PATH="/opt/homebrew/bin:$PATH"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE=linux-study:v6.12
VOLUME=linux-study-v612
case "${1:-shell}" in
  image) docker build -t "$IMAGE" "$ROOT" ;;
  init)
    docker volume create "$VOLUME" >/dev/null
    git -C "$ROOT/linux" archive HEAD | docker run --rm -i -v "$VOLUME:/work" -v "$ROOT/tools:/tools:ro" -v "$ROOT/configs:/configs:ro" "$IMAGE" bash -ec 'mkdir -p /work/linux; tar -x -C /work/linux; bash /tools/configure.sh'
    ;;
  configure) docker run --rm -v "$VOLUME:/work" -v "$ROOT/tools:/tools:ro" -v "$ROOT/configs:/configs:ro" "$IMAGE" bash /tools/configure.sh ;;
  defconfig) docker run --rm -v "$VOLUME:/work" "$IMAGE" make -C /work/linux O=/work/build ARCH=arm64 LLVM=1 defconfig ;;
  read) docker run --rm -v "$ROOT/labs:/labs:ro" "$IMAGE" bash -c 'cc -Wall -Wextra -Werror -g /labs/read_example.c -o /tmp/read-example; strace -e trace=openat,read,write,close /tmp/read-example' ;;
  build) docker run --rm -v "$VOLUME:/work" "$IMAGE" bash -c 'make -C /work/linux O=/work/build ARCH=arm64 LLVM=1 -j6 Image; python3 /work/linux/scripts/clang-tools/gen_compile_commands.py -d /work/build' ;;
  boot) docker run --rm -it -v "$VOLUME:/work" -v "$ROOT/tools:/tools:ro" "$IMAGE" bash /tools/boot.sh ;;
  shell) docker run --rm -it -v "$VOLUME:/work" -v "$ROOT/labs:/labs" "$IMAGE" bash ;;
  *) echo 'Usage: tools/lab.sh {image|init|configure|defconfig|read|build|boot|shell}'; exit 2 ;;
esac
