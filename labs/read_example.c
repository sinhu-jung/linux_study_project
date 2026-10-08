#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>
int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "/etc/hostname";
    int fd = open(path, O_RDONLY);
    if (fd < 0) { perror("open"); return 1; }
    char buffer[256];
    ssize_t n;
    while ((n = read(fd, buffer, sizeof(buffer))) > 0) {
        ssize_t sent = 0;
        while (sent < n) {
            ssize_t count = write(STDOUT_FILENO, buffer + sent, (size_t)(n - sent));
            if (count <= 0) { perror("write"); close(fd); return 1; }
            sent += count;
        }
    }
    if (n < 0) { perror("read"); close(fd); return 1; }
    return close(fd) < 0 ? 1 : 0;
}
