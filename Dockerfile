FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential clang llvm lld bison flex bc libssl-dev libelf-dev \
    python3 ripgrep git gdb strace cpio busybox-static qemu-system-arm \
    ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /work
CMD ["bash"]
