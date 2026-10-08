#include <stdio.h>

int main(void) {
    int values[3] = {10, 20, 30};
    int i = 0;
    while (i < 3) {
        printf("%d\n", values[i]);
        i++;
    }
    return 0;
}
