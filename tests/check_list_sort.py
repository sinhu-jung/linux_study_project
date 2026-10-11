"""Pinned list mergesort with simple userspace list/type shims.

Checks stable order, node identity and restored links, not concurrency.
"""
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SHA = 'adc218676eef25575469234709c2d87185ca223a'
PREFIX = r'''
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <assert.h>
typedef uint8_t u8;
struct list_head {struct list_head *next,*prev;};
#define likely(x) (x)
#define unlikely(x) (x)
#define EXPORT_SYMBOL(x)
'''
MAIN = r'''
struct node {int key,id;struct list_head link;};
struct context {int boolean;unsigned same;};
static struct node *entry(const struct list_head *p) {return (struct node *)((char *)p - offsetof(struct node,link));}
static int compare(void *priv,const struct list_head *a,const struct list_head *b) {
    struct context *c=priv;struct node *x=entry(a),*y=entry(b);
    if(a==b)c->same++;
    else assert(x->id<y->id);
    return c->boolean?(x->key>y->key):(x->key>y->key)-(x->key<y->key);
}
static unsigned checks,same_callbacks;
#define CHECK(c) do { checks++;if(!(c)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#c);return 1;} }while(0)
static int one(unsigned n,unsigned pattern,int boolean) {
    struct node nodes[4096];struct list_head head={&head,&head};
    uint32_t state=12345;struct context context={boolean,0};
    for(unsigned i=0;i<n;i++) {
        state=state*1664525U+1013904223U;
        nodes[i].id=i;
        nodes[i].key=pattern==0?(int)(state%17):pattern==1?(int)i:pattern==2?(int)(n-i):7;
        nodes[i].link.prev=head.prev;nodes[i].link.next=&head;
        head.prev->next=&nodes[i].link;head.prev=&nodes[i].link;
    }
    list_sort(&context,&head,compare);same_callbacks+=context.same;
    unsigned seen=0;struct list_head *previous=&head;
    for(struct list_head *p=head.next;p!=&head;p=p->next) {
        CHECK(seen++<n);CHECK(p->prev==previous);
        struct node *current=entry(p);
        CHECK(current->id>=0 && (unsigned)current->id<n);
        CHECK(current==&nodes[current->id]);
        if(previous!=&head) {
            struct node *before=entry(previous);
            CHECK(before->key<=current->key);
            if(before->key==current->key)CHECK(before->id<current->id);
        }
        previous=p;
    }
    CHECK(seen==n && head.prev==previous);
    seen=0;struct list_head *next=&head;
    for(struct list_head *p=head.prev;p!=&head;p=p->prev) {
        CHECK(seen++<n);CHECK(p->next==next);next=p;
    }
    CHECK(seen==n && head.next==next);
    return 0;
}
int main(void) {
    for(unsigned pattern=0;pattern<4;pattern++)for(int boolean=0;boolean<2;boolean++) {
        for(unsigned n=0;n<=128;n++)CHECK(!one(n,pattern,boolean));
        unsigned lengths[]={255,256,257,1023,1024,1025,2049,4096};
        for(unsigned i=0;i<sizeof(lengths)/sizeof(lengths[0]);i++)CHECK(!one(lengths[i],pattern,boolean));
    }
    CHECK(same_callbacks>0);
    printf("PASS: %u linked-list checks, same-node callbacks=%u\n",checks,same_callbacks);
    return 0;
}
'''


def main():
    cc = os.environ.get('CC') or shutil.which('gcc') or shutil.which('clang')
    if not cc:
        raise SystemExit('C compiler required')
    parts = [PREFIX]
    for path in ['include/linux/list_sort.h', 'lib/list_sort.c']:
        source = subprocess.check_output(['git', '-C', str(ROOT/'linux'), 'show', SHA+':'+path]).decode()
        parts.append(re.sub(r'^\s*#include[^\n]*\n', '', source, flags=re.M))
    parts.append(MAIN)
    with tempfile.TemporaryDirectory() as folder:
        source = Path(folder)/'list-sort.c'
        binary = Path(folder)/('list-sort.exe' if os.name == 'nt' else 'list-sort')
        source.write_text('\n'.join(parts), encoding='utf-8')
        subprocess.run([cc, '-std=gnu11', '-Wall', '-Wextra', '-Werror', '-O2', str(source), '-o', str(binary)], check=True)
        subprocess.run([str(binary)], check=True)


if __name__ == '__main__':
    main()
