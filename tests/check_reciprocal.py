"""Pinned reciprocal setup/basic divide; explicit advanced usage model.

The advanced model is test code, not an actual kernel JIT backend.
Only supported nonzero divisors/precision paths are invoked.
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
#include <stdio.h>
#include <assert.h>
typedef uint8_t u8;
typedef uint32_t u32;
typedef uint64_t u64;
#define U32_MAX UINT32_MAX
#define fls(x) ((x)?32-__builtin_clz((u32)(x)):0)
#define min(a,b) ((a)<(b)?(a):(b))
#define max(a,b) ((a)>(b)?(a):(b))
#define EXPORT_SYMBOL(x)
#define WARN(c,...) assert(!(c))
#define do_div(n,d) do {u32 study_d=(d);(n)/=study_d;}while(0)
'''
MAIN = r'''
static unsigned checks,wide_paths,pre_paths,narrow_paths;
#define CHECK(c) do { checks++;if(!(c)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#c);return 1;} }while(0)
static u32 advanced_model(u32 n,u32 d) {
    if(d>=(1U<<31))return n>=d;
    struct reciprocal_value_adv r=reciprocal_value_adv(d,32);
    u8 exp=r.exp,pre=0;
    if(r.is_wide_m && !(d&1)) {
        pre=fls(d & -d)-1;
        r=reciprocal_value_adv(d>>pre,32-pre);
        pre_paths++;
    }
    if(d==(1U<<exp))return n>>exp;
    if(r.is_wide_m) {
        assert(!pre);wide_paths++;
        u32 t=((u64)n*r.m)>>32;
        return (((n-t)>>1)+t)>>(r.sh-1);
    }
    narrow_paths++;
    u32 result=n>>pre;
    return (u32)(((u64)result*r.m)>>32)>>r.sh;
}
int main(void) {
    struct reciprocal_value r=reciprocal_value(3);
    CHECK(r.m==1431655766U && r.sh1==1 && r.sh2==1);
    for(u32 d=1;d<=512;d++) {
        r=reciprocal_value(d);
        for(u32 n=0;n<1024;n++) {
            CHECK(reciprocal_divide(n,r)==n/d);
            CHECK(advanced_model(n,d)==n/d);
        }
        u32 edges[]={UINT32_MAX,UINT32_MAX-1,1U<<31,d-1,d};
        for(unsigned i=0;i<5;i++) {
            CHECK(reciprocal_divide(edges[i],r)==edges[i]/d);
            CHECK(advanced_model(edges[i],d)==edges[i]/d);
        }
    }
    u32 state=123456789;
    for(unsigned i=0;i<100000;i++) {
        state=state*1664525U+1013904223U;u32 n=state;
        state=state*1664525U+1013904223U;u32 d=state?state:1;
        CHECK(reciprocal_divide(n,reciprocal_value(d))==n/d);
        CHECK(advanced_model(n,d)==n/d);
    }
    CHECK(wide_paths>0 && pre_paths>0 && narrow_paths>0);
    printf("PASS: %u reciprocal checks; wide=%u pre-shift=%u narrow=%u\n",checks,wide_paths,pre_paths,narrow_paths);
    return 0;
}
'''


def main():
    cc = os.environ.get('CC') or shutil.which('gcc') or shutil.which('clang')
    if not cc:
        raise SystemExit('C compiler required')
    parts = [PREFIX]
    for path in ['include/linux/reciprocal_div.h', 'lib/math/reciprocal_div.c']:
        source = subprocess.check_output(['git', '-C', str(ROOT/'linux'), 'show', SHA+':'+path]).decode()
        parts.append(re.sub(r'^\s*#include[^\n]*\n', '', source, flags=re.M))
    parts.append(MAIN)
    with tempfile.TemporaryDirectory() as folder:
        source = Path(folder)/'reciprocal.c'
        binary = Path(folder)/('reciprocal.exe' if os.name == 'nt' else 'reciprocal')
        source.write_text('\n'.join(parts), encoding='utf-8')
        subprocess.run([cc, '-std=gnu11', '-Wall', '-Wextra', '-Werror', '-O2', str(source), '-o', str(binary)], check=True)
        subprocess.run([str(binary)], check=True)


if __name__ == '__main__':
    main()
