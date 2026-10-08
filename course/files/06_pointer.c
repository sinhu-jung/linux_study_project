#include <stdio.h>

int main(void) {
    int value = 7;
    int *p = &value;
    *p = 9;
    printf("%d\n", value);
    return 0;
}
