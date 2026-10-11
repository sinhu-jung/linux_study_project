"""Pinned integer pow/sqrt C bodies versus independent arithmetic references.

Uses host unsigned long and explicit u64; no target kernel runtime claim.
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
#include <limits.h>
#include <stdio.h>
typedef uint64_t u64;
typedef uint32_t u32;
#define EXPORT_SYMBOL(x)
#define EXPORT_SYMBOL_GPL(x)
#if ULONG_MAX == 0xffffffffUL
#define BITS_PER_LONG 32
#else
#define BITS_PER_LONG 64
#endif
#define __fls(x) ((unsigned long)(sizeof(unsigned long)*CHAR_BIT-1-__builtin_clzl(x)))
#define fls64(x) ((x)?64-__builtin_clzll(x):0)
'''
MAIN = r'''
#if BITS_PER_LONG == 64
static u32 int_sqrt64(u64 x) { return (u32)int_sqrt(x); }
#endif
static unsigned checks;
#define CHECK(c) do { checks++;if(!(c)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#c);return 1;} }while(0)
static u64 power_reference(u64 b,unsigned e) {
    u64 r=1;for(unsigned i=0;i<e;i++)r*=b;return r;
}
static u64 root_reference(u64 x) {
    u64 low=0,high=UINT32_MAX,answer=0;
    while(low<=high) {
        u64 mid=low+(high-low)/2;
        if(!mid || mid<=x/mid) {answer=mid;low=mid+1;}
        else high=mid-1;
    }
    return answer;
}
int main(void) {
    for(u64 b=0;b<=100;b++) for(unsigned e=0;e<=100;e++)
        CHECK(int_pow(b,e)==power_reference(b,e));
    CHECK(int_pow(0,0)==1);CHECK(int_pow(2,64)==0);
    CHECK(int_pow(UINT64_MAX,1)==UINT64_MAX);
    CHECK(int_pow(5,5)==3125);
    for(unsigned long x=0;x<100000;x++) {
        CHECK(int_sqrt(x)==root_reference(x));
        CHECK(int_sqrt64(x)==root_reference(x));
    }
    u64 edges[]={UINT64_MAX,UINT64_MAX-1,UINT32_MAX,(u64)UINT32_MAX+1,
        (u64)UINT32_MAX*UINT32_MAX,(u64)UINT32_MAX*UINT32_MAX-1,ULONG_MAX};
    for(unsigned i=0;i<sizeof(edges)/sizeof(edges[0]);i++)
        CHECK(int_sqrt64(edges[i])==root_reference(edges[i]));
    u64 state=UINT64_C(0x123456789abcdef0);
    for(unsigned i=0;i<10000;i++) {
        state=state*UINT64_C(6364136223846793005)+1;
        CHECK(int_sqrt64(state)==root_reference(state));
        CHECK(int_sqrt((unsigned long)state)==root_reference((unsigned long)state));
    }
    printf("PASS: %u pow/sqrt checks, host unsigned long=%u bits\n",checks,(unsigned)(sizeof(long)*CHAR_BIT));
    return 0;
}
'''


def main():
    cc = os.environ.get('CC') or shutil.which('gcc') or shutil.which('clang')
    if not cc:
        raise SystemExit('C compiler required')
    parts = [PREFIX]
    for path in ['lib/math/int_pow.c', 'lib/math/int_sqrt.c']:
        source = subprocess.check_output(['git', '-C', str(ROOT/'linux'), 'show', SHA+':'+path]).decode()
        parts.append(re.sub(r'^\s*#include[^\n]*\n', '', source, flags=re.M))
    parts.append(MAIN)
    with tempfile.TemporaryDirectory() as folder:
        source = Path(folder)/'power.c'
        binary = Path(folder)/('power.exe' if os.name == 'nt' else 'power')
        source.write_text('\n'.join(parts), encoding='utf-8')
        subprocess.run([cc, '-std=gnu11', '-Wall', '-Wextra', '-Werror', '-O2', str(source), '-o', str(binary)], check=True)
        subprocess.run([str(binary)], check=True)


if __name__ == '__main__':
    main()
