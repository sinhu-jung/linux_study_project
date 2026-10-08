#!/bin/bash
set -euo pipefail
make -C /work/linux O=/work/build ARCH=arm64 LLVM=1 tinyconfig
cd /work/linux
ARCH=arm64 LLVM=1 KCONFIG_CONFIG=/work/build/.config scripts/kconfig/merge_config.sh -m -O /work/build /work/build/.config /configs/qemu-arm64.config
make O=/work/build ARCH=arm64 LLVM=1 olddefconfig
make O=/work/build ARCH=arm64 LLVM=1 prepare
