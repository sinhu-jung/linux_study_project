"""Compare pinned rational C against exhaustive bounded integer candidates.

Small-domain optimality checks do not establish overflow safety at ULONG_MAX.
Runs userspace source bodies, not the in-kernel KUnit suite.
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
#include <limits.h>
#include <stdio.h>
#include <stdint.h>
#define min(a,b) ((a)<(b)?(a):(b))
#define EXPORT_SYMBOL(x)
#define MODULE_DESCRIPTION(x)
#define MODULE_LICENSE(x)
'''
MAIN = r'''
static unsigned checks;
#define CHECK(c) do { checks++;if(!(c)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#c);return 1;} }while(0)
static uint64_t error_numerator(unsigned long a,unsigned long b,unsigned long p,unsigned long q) {
    uint64_t left=(uint64_t)a*q,right=(uint64_t)p*b;
    return left>right?left-right:right-left;
}
int main(void) {
    const unsigned long cases[][6]={
        {1230,10,100,20,100,1},{34567,100,120,20,120,1},
        {1,30,100,10,0,1},{1,19,100,10,1,10},{27,32,16,16,11,13},
        {1155,7735,255,255,33,221},{87,32,70,32,68,25},
        {14533,4626,15000,2400,7433,2366}};
    unsigned long n,d;
    for(unsigned i=0;i<8;i++) {
        const unsigned long *c=cases[i];
        rational_best_approximation(c[0],c[1],c[2],c[3],&n,&d);
        CHECK(n==c[4] && d==c[5]);
    }
    for(unsigned long a=0;a<=24;a++)for(unsigned long b=1;b<=24;b++)
    for(unsigned long mn=1;mn<=8;mn++)for(unsigned long md=1;md<=8;md++) {
        rational_best_approximation(a,b,mn,md,&n,&d);
        CHECK(n<=mn && d>=1 && d<=md);
        uint64_t e=error_numerator(a,b,n,d);
        for(unsigned long p=0;p<=mn;p++)for(unsigned long q=1;q<=md;q++)
            CHECK(e*q<=error_numerator(a,b,p,q)*d);
    }
    rational_best_approximation(3,2,10,10,&n,&d);CHECK(n==3 && d==2);
    rational_best_approximation(1,0,10,10,&n,&d);CHECK(n==1 && d==0);
    printf("PASS: %u rational checks (small bounded domain; no overflow proof)\n",checks);
    return 0;
}
'''


def main():
    cc = os.environ.get('CC') or shutil.which('gcc') or shutil.which('clang')
    if not cc:
        raise SystemExit('C compiler required')
    parts = [PREFIX]
    for path in ['include/linux/rational.h', 'lib/math/rational.c']:
        source = subprocess.check_output(['git', '-C', str(ROOT/'linux'), 'show', SHA+':'+path]).decode()
        parts.append(re.sub(r'^\s*#include[^\n]*\n', '', source, flags=re.M))
    parts.append(MAIN)
    with tempfile.TemporaryDirectory() as folder:
        source = Path(folder)/'rational.c'
        binary = Path(folder)/('rational.exe' if os.name == 'nt' else 'rational')
        source.write_text('\n'.join(parts), encoding='utf-8')
        subprocess.run([cc, '-std=gnu11', '-Wall', '-Wextra', '-Werror', '-O2', str(source), '-o', str(binary)], check=True)
        subprocess.run([str(binary)], check=True)


if __name__ == '__main__':
    main()
