"""Pinned fixed-point logarithms against independent libm samples.

Finite sample tolerances are not a worst-case proof over all u32 inputs.
WARN_ON and kernel type helpers are userspace shims.
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
#include <stdio.h>
#include <math.h>
typedef uint32_t u32;
typedef uint64_t u64;
#define ARRAY_SIZE(x) (sizeof(x)/sizeof((x)[0]))
#define unlikely(x) (x)
#define fls(x) ((x)?32-__builtin_clz(x):0)
#define EXPORT_SYMBOL(x)
static unsigned warnings;
#define WARN_ON(x) do {if(x)warnings++;}while(0)
'''
MAIN = r'''
static unsigned checks;
static double max_error2,max_error10;
#define CHECK(c) do { checks++;if(!(c)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#c);return 1;} }while(0)
static int sample(u32 x) {
    double e2=fabs(intlog2(x)/16777216.0-log2((double)x));
    double e10=fabs(intlog10(x)/16777216.0-log10((double)x));
    if(e2>max_error2)max_error2=e2;
    if(e10>max_error10)max_error10=e10;
    CHECK(e2<0.00002);CHECK(e10<0.00002);
    return 0;
}
int main(void) {
    for(unsigned i=0;i<256;i++) {
        CHECK(logtable[i]==(unsigned)floor(log2(1.0+i/256.0)*65536.0+0.5));
        if(i)CHECK(logtable[i]>logtable[i-1]);
        u32 boundary=UINT32_C(0x80000000)+(i<<23);
        CHECK(!sample(boundary));CHECK(!sample(boundary+0x7fffff));
    }
    CHECK(((0-logtable[255])&0xffff)==185);
    CHECK((uint64_t)0x7fffff*369<((uint64_t)1<<32));
    for(unsigned i=0;i<32;i++)CHECK(intlog2((u32)1<<i)==i*(1U<<24));
    CHECK(intlog2(0)==0 && warnings==1);
    CHECK(intlog10(0)==0 && warnings==2);
    CHECK(intlog2(1)==0 && warnings==2);
    for(u32 x=1;x<100000;x++)CHECK(!sample(x));
    u32 state=123456789;
    for(unsigned i=0;i<100000;i++) {
        state=state*1664525U+1013904223U;
        if(state)CHECK(!sample(state));
    }
    printf("PASS: %u fixed-point checks; sampled max errors log2=%.9g log10=%.9g\n",checks,max_error2,max_error10);
    return 0;
}
'''


def main():
    cc = os.environ.get('CC') or shutil.which('gcc') or shutil.which('clang')
    if not cc:
        raise SystemExit('C compiler required')
    parts = [PREFIX]
    for path in ['include/linux/int_log.h', 'lib/math/int_log.c']:
        source = subprocess.check_output(['git', '-C', str(ROOT/'linux'), 'show', SHA+':'+path]).decode()
        parts.append(re.sub(r'^\s*#include[^\n]*\n', '', source, flags=re.M))
    parts.append(MAIN)
    with tempfile.TemporaryDirectory() as folder:
        source = Path(folder)/'log.c'
        binary = Path(folder)/('log.exe' if os.name == 'nt' else 'log')
        source.write_text('\n'.join(parts), encoding='utf-8')
        subprocess.run([cc, '-std=gnu11', '-Wall', '-Wextra', '-Werror', '-O2', str(source), '-lm', '-o', str(binary)], check=True)
        subprocess.run([str(binary)], check=True)


if __name__ == '__main__':
    main()
