#include <stdio.h>

int twice(int value) {
    return value * 2;
}

int main(void) {
    int (*operation)(int) = twice;
    printf("%d\n", operation(3));
    return 0;
}
