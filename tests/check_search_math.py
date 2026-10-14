"""Actual pinned search/GCD/LCM bodies against independent references.

Both GCD compile-time branches run using the host's unsigned long width.
Not a full target ABI/kernel test; tested LCM products fit the host type.
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
#include <stddef.h>
#include <limits.h>
#include <stdio.h>
typedef int (*cmp_func_t)(const void *,const void *);
#ifndef __always_inline
#define __always_inline inline __attribute__((always_inline))
#endif
#ifndef __attribute_const__
#define __attribute_const__ __attribute__((const))
#endif
#define EXPORT_SYMBOL(x)
#define EXPORT_SYMBOL_GPL(x)
#define NOKPROBE_SYMBOL(x)
#define bsearch study_bsearch
#define swap(a,b) do { unsigned long tmp=(a);(a)=(b);(b)=tmp; }while(0)
#define __ffs(x) __builtin_ctzl(x)
'''
MAIN = r'''
static unsigned checks, comparisons;
#define CHECK(c) do { checks++;if(!(c)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#c);return 1;} }while(0)
static unsigned long reference_gcd(unsigned long a,unsigned long b) {
    while(b) { unsigned long rem=a%b;a=b;b=rem; } return a;
}
static int compare(const void *key,const void *element) {
    comparisons++;int a=*(const int *)key,b=*(const int *)element;
    return (a>b)-(a<b);
}
int main(void) {
    for(unsigned long a=0;a<256;a++) for(unsigned long b=0;b<256;b++) {
        unsigned long g=reference_gcd(a,b);
        CHECK(gcd(a,b)==g);
        unsigned long expected=(a && b)?(a*b)/g:0;
        CHECK(lcm(a,b)==expected);
        CHECK(lcm_not_zero(a,b)==(expected?expected:(b?b:a)));
    }
    unsigned long edges[]={0,1,2,3,ULONG_MAX,ULONG_MAX-1,1UL<<(sizeof(long)*CHAR_BIT-1)};
    for(unsigned i=0;i<sizeof(edges)/sizeof(edges[0]);i++)
        for(unsigned j=0;j<sizeof(edges)/sizeof(edges[0]);j++)
            CHECK(gcd(edges[i],edges[j])==reference_gcd(edges[i],edges[j]));
    int a[128];for(int i=0;i<128;i++)a[i]=2*i;
    for(size_t n=0;n<=128;n++) for(int key=-1;key<=257;key++) {
        comparisons=0;int *found=study_bsearch(&key,a,n,sizeof(a[0]),compare);
        int present=(key>=0 && key%2==0 && (size_t)(key/2)<n);
        CHECK(present?(found==a+key/2):(found==NULL));
        unsigned bound=0;for(size_t k=n;k;k>>=1)bound++;
        CHECK(comparisons<=bound);
    }
    int duplicates[]={1,1,1,1},key=1;
    CHECK(study_bsearch(&key,duplicates,4,sizeof(int),compare)==duplicates+2);
    printf("PASS: %u search/math checks, unsigned long=%u bits\n",checks,(unsigned)(sizeof(long)*CHAR_BIT));
    return 0;
}
'''


def main():
    cc = os.environ.get('CC') or shutil.which('gcc') or shutil.which('clang')
    if not cc:
        raise SystemExit('C compiler required')
    parts = [PREFIX]
    for path in ['include/linux/bsearch.h', 'include/linux/gcd.h', 'include/linux/lcm.h',
                 'lib/bsearch.c', 'lib/math/gcd.c', 'lib/math/lcm.c']:
        source = subprocess.check_output(['git', '-C', str(ROOT/'linux'), 'show', SHA+':'+path]).decode()
        parts.append(re.sub(r'^\s*#include[^\n]*\n', '', source, flags=re.M))
    parts.append(MAIN)
    with tempfile.TemporaryDirectory() as folder:
        source = Path(folder)/'math.c'
        binary = Path(folder)/('math.exe' if os.name == 'nt' else 'math')
        source.write_text('\n'.join(parts), encoding='utf-8')
        for defines in [[], ['-DCONFIG_CPU_NO_EFFICIENT_FFS']]:
            subprocess.run([cc, '-std=gnu11', '-Wall', '-Wextra', '-Werror', '-O2', *defines,
                            str(source), '-o', str(binary)], check=True)
            subprocess.run([str(binary)], check=True)


if __name__ == '__main__':
    main()
