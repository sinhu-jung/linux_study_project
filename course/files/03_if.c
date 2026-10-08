#include <stdio.h>

int main(void) {
    int fd = -1;
    if (fd < 0) {
        printf("open failed\n");
        return 1;
    }
    printf("open succeeded\n");
    return 0;
}
