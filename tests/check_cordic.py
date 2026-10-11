"""Pinned CORDIC on GCC-compatible host; finite angle-domain numerical checks.

Uses -fwrapv and host arithmetic signed right shifts. This does not establish
portable ISO C semantics for negative left shifts or arbitrary s32 inputs.
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
typedef int32_t s32;
#define EXPORT_SYMBOL(x)
#define MODULE_DESCRIPTION(x)
#define MODULE_AUTHOR(x)
#define MODULE_LICENSE(x)
'''
MAIN = r'''
static unsigned checks;
#define CHECK(c) do { checks++;if(!(c)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#c);return 1;} }while(0)
int main(void) {
    const double pi=acos(-1.0);double maximum=0;
    CHECK(CORDIC_NUM_ITER==18);
    CHECK(sizeof(arctan_table)/sizeof(arctan_table[0])==CORDIC_NUM_ITER);
    for(unsigned i=0;i<CORDIC_NUM_ITER;i++)
        CHECK(arctan_table[i]==(s32)floor(atan(ldexp(1.0,-(int)i))*180/pi*65536+0.5));
    CHECK(CORDIC_FIXED(1)==65536);
    CHECK(CORDIC_FLOAT(98304)==2);CHECK(CORDIC_FLOAT(-98304)==-2);
    CHECK(CORDIC_FLOAT(32767)==0);CHECK(CORDIC_FLOAT(-32767)==0);
    CHECK(CORDIC_FLOAT(32768)==1);CHECK(CORDIC_FLOAT(-32768)==-1);
    for(s32 theta=-720;theta<=720;theta++) {
        struct cordic_iq c=cordic_calc_iq(theta);
        double ei=fabs(c.i/65536.0-cos(theta*pi/180));
        double eq=fabs(c.q/65536.0-sin(theta*pi/180));
        if(ei>maximum)maximum=ei;
        if(eq>maximum)maximum=eq;
        CHECK(ei<0.0003);CHECK(eq<0.0003);
        if(theta>=-180 && theta<=180) {
            struct cordic_iq shifted=cordic_calc_iq(theta+360);
            /* Endpoint normalization can select a different rounding path. */
            CHECK(fabs((double)c.i-shifted.i)<20);
            CHECK(fabs((double)c.q-shifted.q)<20);
        }
    }
    printf("PASS: %u CORDIC checks; sampled max coordinate error %.9g\n",checks,maximum);
    return 0;
}
'''


def main():
    cc = os.environ.get('CC') or shutil.which('gcc') or shutil.which('clang')
    if not cc:
        raise SystemExit('C compiler required')
    parts = [PREFIX]
    for path in ['include/linux/cordic.h', 'lib/math/cordic.c']:
        source = subprocess.check_output(['git', '-C', str(ROOT/'linux'), 'show', SHA+':'+path]).decode()
        parts.append(re.sub(r'^\s*#include[^\n]*\n', '', source, flags=re.M))
    parts.append(MAIN)
    with tempfile.TemporaryDirectory() as folder:
        source = Path(folder)/'cordic.c'
        binary = Path(folder)/('cordic.exe' if os.name == 'nt' else 'cordic')
        source.write_text('\n'.join(parts), encoding='utf-8')
        subprocess.run([cc, '-std=gnu11', '-fwrapv', '-Wall', '-Wextra', '-Werror', '-O2', str(source), '-lm', '-o', str(binary)], check=True)
        subprocess.run([str(binary)], check=True)


if __name__ == '__main__':
    main()
