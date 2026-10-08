#include <stdio.h>

struct File {
    int position;
};

int main(void) {
    struct File file = {0};
    struct File *p = &file;
    p->position = 4;
    printf("%d\n", file.position);
    return 0;
}
