"""Actual pinned macros; userspace type/do_div shims, not ABI verification."""
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
typedef int8_t __s8;
typedef uint8_t __u8;
typedef int16_t __s16;
typedef uint16_t __u16;
typedef int32_t __s32;
typedef uint32_t __u32;
typedef long __kernel_long_t;
typedef unsigned long __kernel_ulong_t;
#if ULONG_MAX == 0xffffffffUL
#define BITS_PER_LONG 32
#else
#define BITS_PER_LONG 64
#endif
#define do_div(n,b) ({ uint32_t study_d=(b);uint32_t study_r=(n)%study_d;(n)/=study_d;study_r; })
'''
MAIN = r'''
static unsigned checks;
#define CHECK(c) do { checks++;if(!(c)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#c);return 1;} }while(0)
int main(void) {
    for(unsigned x=0;x<1000;x++)for(unsigned d=1;d<32;d++) {
        unsigned up=x/d+(x%d!=0);
        CHECK(roundup(x,d)==up*d);CHECK(rounddown(x,d)==x/d*d);
        CHECK(DIV_ROUND_UP(x,d)==up);CHECK(DIV_ROUND_UP_ULL(x,d)==up);
        CHECK(DIV_ROUND_DOWN_ULL(x,d)==x/d);
        CHECK(DIV_ROUND_UP_SECTOR_T(x,d)==up);
        CHECK(DIV_ROUND_CLOSEST_ULL(x,d)==x/d+((x%d)*2>=d));
        CHECK(mult_frac(x,3U,d)==x*3U/d);
        if(!(d&(d-1))) {
            CHECK(round_up(x,d)==up*d);CHECK(round_down(x,d)==x/d*d);
            CHECK(__ALIGN_KERNEL(x,d)==up*d);
        }
    }
    CHECK(DIV_ROUND_CLOSEST(5,2)==3);CHECK(DIV_ROUND_CLOSEST(-5,2)==-3);
    CHECK(DIV_ROUND_CLOSEST(5,-2)==-3);CHECK(DIV_ROUND_CLOSEST(-5,-2)==3);
    CHECK(abs(-17)==17);CHECK(abs_diff(4U,9U)==5);CHECK(abs_diff(7,7)==0);
    unsigned x=13,y=8;CHECK(round_up(x++,y++)==16);CHECK(x==14 && y==9);
    CHECK(reciprocal_scale(UINT32_C(0x80000000),10)==5);
    CHECK(reciprocal_scale(UINT32_MAX,10)==9);CHECK(reciprocal_scale(99,0)==0);
    unsigned long long q=17;CHECK(sector_div(q,5)==2);CHECK(q==3);
    CHECK(_BITUL(3)==8UL);CHECK(_BITULL(63)==UINT64_C(0x8000000000000000));
    CHECK((_BIT128(100)>>100)==1);
    CHECK(__builtin_types_compatible_p(typeof(UL(1)),unsigned long));
    CHECK(__builtin_types_compatible_p(typeof(ULL(1)),unsigned long long));
    struct u32_fract f={3,4};CHECK(f.numerator==3 && f.denominator==4);
    struct sysinfo s={0};s.loads[0]=1UL<<SI_LOAD_SHIFT;s.totalram=100;s.mem_unit=4096;
    CHECK(s.loads[0]==65536);CHECK((u64)s.totalram*s.mem_unit==409600);
    CHECK(sizeof(s._f)==20-2*sizeof(__kernel_ulong_t)-sizeof(__u32));
    printf("PASS: %u math header checks (host types and do_div shim)\n",checks);
    return 0;
}
'''


def main():
    cc = os.environ.get('CC') or shutil.which('gcc') or shutil.which('clang')
    if not cc:
        raise SystemExit('C compiler required')
    parts = [PREFIX]
    for path in ['include/uapi/linux/const.h', 'include/vdso/const.h', 'include/linux/const.h',
                 'include/uapi/linux/sysinfo.h', 'include/uapi/linux/kernel.h', 'include/linux/math.h']:
        source = subprocess.check_output(['git', '-C', str(ROOT/'linux'), 'show', SHA+':'+path]).decode()
        parts.append(re.sub(r'^\s*#include[^\n]*\n', '', source, flags=re.M))
    parts.append(MAIN)
    with tempfile.TemporaryDirectory() as folder:
        source = Path(folder)/'headers.c'
        binary = Path(folder)/('headers.exe' if os.name == 'nt' else 'headers')
        source.write_text('\n'.join(parts), encoding='utf-8')
        subprocess.run([cc, '-std=gnu11', '-Wall', '-Wextra', '-Werror', '-O2', str(source), '-o', str(binary)], check=True)
        subprocess.run([str(binary)], check=True)


if __name__ == '__main__':
    main()
