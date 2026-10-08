#!/bin/bash
set -euo pipefail
if [ ! -f /work/build/arch/arm64/boot/Image ]; then echo '먼저 tools/lab.sh build 를 실행하세요.'; exit 1; fi
mkdir -p /work/initramfs/{bin,dev,proc,sys}
cp /usr/bin/busybox /work/initramfs/bin/busybox
ln -sf busybox /work/initramfs/bin/sh
cat > /work/initramfs/init <<'INIT'
#!/bin/sh
/bin/busybox mount -t devtmpfs devtmpfs /dev
/bin/busybox mount -t proc proc /proc
/bin/busybox mount -t sysfs sysfs /sys
/bin/busybox --install -s /bin
echo 'Linux v6.12 학습 커널입니다. uname -a, dmesg 를 실행해보세요.'
exec /bin/sh
INIT
chmod +x /work/initramfs/init
(cd /work/initramfs && find . -print0 | cpio --null -o --format=newc) > /work/initramfs.cpio
exec qemu-system-aarch64 -machine virt -cpu cortex-a57 -m 1024 -smp 2 -nic none -nographic -kernel /work/build/arch/arm64/boot/Image -initrd /work/initramfs.cpio -append 'console=ttyAMA0 rdinit=/init' -no-reboot
