#include <stdio.h>
#define BUFFER_SIZE 256

int main(void) {
    char buffer[BUFFER_SIZE];
    printf("%zu\n", sizeof(buffer));
    return 0;
}
