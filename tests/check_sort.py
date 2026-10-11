"""Pinned heapsort against libc qsort, with kernel typedef/attribute shims.

Four swap configuration combinations; not a kernel ABI or performance test.
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
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef uint32_t u32;
typedef uint64_t u64;
typedef void (*swap_r_func_t)(void *,void *,int,const void *);
typedef void (*swap_func_t)(void *,void *,int);
typedef int (*cmp_r_func_t)(const void *,const void *,const void *);
typedef int (*cmp_func_t)(const void *,const void *);
#define __attribute_const__ __attribute__((const))
#ifndef __always_inline
#define __always_inline inline __attribute__((always_inline))
#endif
#define EXPORT_SYMBOL(x)
'''
MAIN = r'''
static unsigned checks,swaps;
static size_t width;
#define CHECK(c) do { checks++;if(!(c)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#c);return 1;} }while(0)
static int ordinary_cmp(const void *a,const void *b) { return memcmp(a,b,width); }
struct context {size_t width;int direction;};
static int context_cmp(const void *a,const void *b,const void *p) {
    const struct context *c=p;int r=memcmp(a,b,c->width);
    return ((r>0)-(r<0))*c->direction;
}
static void ordinary_swap(void *a,void *b,int size) {
    swaps++;for(int i=0;i<size;i++) {char t=((char *)a)[i];((char *)a)[i]=((char *)b)[i];((char *)b)[i]=t;}
}
static void context_swap(void *a,void *b,int size,const void *p) {
    (void)p;ordinary_swap(a,b,size);
}
int main(void) {
    union {u64 aligned;unsigned char bytes[1400];} storage;
    unsigned char reference[1400],input[1400];u32 state=1234567;
    for(width=1;width<=17;width++)for(size_t n=0;n<=64;n++)for(unsigned offset=0;offset<=1;offset++) {
        for(size_t i=0;i<n*width;i++) {state=state*1664525U+1013904223U;input[i]=(unsigned char)(state>>24);}
        memcpy(reference,input,n*width);qsort(reference,n,width,ordinary_cmp);
        for(unsigned mode=0;mode<4;mode++) {
            unsigned char *a=storage.bytes+offset;memcpy(a,input,n*width);
            struct context c={width,1};
            if(mode<2)sort(a,n,width,ordinary_cmp,mode?ordinary_swap:NULL);
            else sort_r(a,n,width,context_cmp,mode==3?context_swap:NULL,&c);
            CHECK(!memcmp(a,reference,n*width));
        }
        struct context descending={width,-1};unsigned char *a=storage.bytes+offset;
        memcpy(a,input,n*width);sort_r(a,n,width,context_cmp,NULL,&descending);
        for(size_t i=0;i<n;i++)CHECK(!memcmp(a+i*width,reference+(n-1-i)*width,width));
    }
    CHECK(swaps>0);
    for(size_t s=1;s<=32;s++)for(size_t j=1;j<100;j++)
        CHECK(parent(j*s,s&-s,s)==((j-1)/2)*s);
    printf("PASS: %u sort checks; custom swap calls=%u\n",checks,swaps);
    return 0;
}
'''


def main():
    cc = os.environ.get('CC') or shutil.which('gcc') or shutil.which('clang')
    if not cc:
        raise SystemExit('C compiler required')
    parts = [PREFIX]
    for path in ['include/linux/sort.h', 'lib/sort.c']:
        source = subprocess.check_output(['git', '-C', str(ROOT/'linux'), 'show', SHA+':'+path]).decode()
        parts.append(re.sub(r'^\s*#include[^\n]*\n', '', source, flags=re.M))
    parts.append(MAIN)
    with tempfile.TemporaryDirectory() as folder:
        source = Path(folder)/'sort.c'
        binary = Path(folder)/('sort.exe' if os.name == 'nt' else 'sort')
        source.write_text('\n'.join(parts), encoding='utf-8')
        for wide in [False, True]:
            for unaligned in [False, True]:
                defines = (['-DCONFIG_64BIT'] if wide else []) + (['-DCONFIG_HAVE_EFFICIENT_UNALIGNED_ACCESS'] if unaligned else [])
                subprocess.run([cc, '-std=gnu11', '-fno-strict-aliasing', '-Wall', '-Wextra', '-Werror', '-O2', *defines, str(source), '-o', str(binary)], check=True)
                subprocess.run([str(binary)], check=True)


if __name__ == '__main__':
    main()
