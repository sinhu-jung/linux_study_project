"""Run pinned kstrtox.c with host type and user-copy shims, not kernel faults."""
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
#include <limits.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <errno.h>
typedef uint8_t u8; typedef int8_t s8;
typedef uint16_t u16; typedef int16_t s16;
#define noinline __attribute__((noinline))
#define EXPORT_SYMBOL(x)
#define __user
#define unlikely(x) (x)
#define div_u64(a,b) ((a)/(b))
#define min(a,b) ((a)<(b)?(a):(b))
#undef _tolower
#define _tolower(c) ((c)|0x20)
#define kstrtoul _kstrtoul
#define kstrtol _kstrtol
static int fail_copy;
static size_t copy_from_user(void *dst,const void *src,size_t n) {
    if(fail_copy)return n ? n : 1;
    memcpy(dst,src,n);return 0;
}
'''
MAIN = r'''
static unsigned checks;
#define CHECK(c) do {checks++;if(!(c)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#c);return 1;}}while(0)
int main(void) {
    char text[100]; unsigned long long u; long long s;
    for(int n=-40000;n<=70000;n++) {
        snprintf(text,sizeof(text),"%d",n);
        s=123;CHECK(kstrtoll(text,10,&s)==0);CHECK(s==n);
        u=123;int rc=kstrtoull(text,10,&u);
        CHECK(rc==(n<0?-EINVAL:0));CHECK(u==(n<0?123:(unsigned long long)n));
        s8 a=42;u8 b=42;s16 c=42;u16 d=42;
        int ra=kstrtos8(text,10,&a),rb=kstrtou8(text,10,&b);
        int rca=kstrtos16(text,10,&c),rd=kstrtou16(text,10,&d);
        int oka=n>=-128&&n<=127,okb=n>=0&&n<=255;
        int okc=n>=-32768&&n<=32767,okd=n>=0&&n<=65535;
        CHECK(ra==(oka?0:-ERANGE));CHECK(a==(oka?n:42));
        CHECK(rb==(n<0?-EINVAL:okb?0:-ERANGE));CHECK(b==(okb?n:42));
        CHECK(rca==(okc?0:-ERANGE));CHECK(c==(okc?n:42));
        CHECK(rd==(n<0?-EINVAL:okd?0:-ERANGE));CHECK(d==(okd?n:42));
    }
    const char *bad[]={"","+","-1"," 1","1 ","1x","1\n\n","0x","09","++1"};
    for(unsigned i=0;i<sizeof(bad)/sizeof(*bad);i++) {
        u=17;CHECK(kstrtoull(bad[i],0,&u)==-EINVAL);CHECK(u==17);
    }
    CHECK(kstrtoull("+0Xff\n",0,&u)==0&&u==255);
    CHECK(kstrtoull("010",0,&u)==0&&u==8);
    CHECK(kstrtoull("18446744073709551615",10,&u)==0&&u==ULLONG_MAX);
    u=17;CHECK(kstrtoull("18446744073709551616",10,&u)==-ERANGE&&u==17);
    CHECK(kstrtoll("-9223372036854775808",10,&s)==0&&s==LLONG_MIN);
    CHECK(kstrtoll("9223372036854775807",10,&s)==0&&s==LLONG_MAX);
    s=17;CHECK(kstrtoll("9223372036854775808",10,&s)==-ERANGE&&s==17);
    CHECK(kstrtoll("-9223372036854775809",10,&s)==-ERANGE&&s==17);
    CHECK(_parse_integer_limit("12345",10,&u,3)==3&&u==123);
    unsigned rv=_parse_integer("18446744073709551616",10,&u);
    CHECK((rv&KSTRTOX_OVERFLOW)!=0);CHECK((rv&~KSTRTOX_OVERFLOW)==20);CHECK(u==0);
    bool flag=false;CHECK(kstrtobool("truejunk",&flag)==0&&flag);
    CHECK(kstrtobool("of-anything",&flag)==0&&!flag);
    flag=true;CHECK(kstrtobool(NULL,&flag)==-EINVAL&&flag);
    CHECK(kstrtobool("o",&flag)==-EINVAL&&flag);
    CHECK(kstrtobool_from_user("off-extra",9,&flag)==0&&!flag);
    CHECK(kstrtobool_from_user("",0,&flag)==-EINVAL&&!flag);
    u8 byte=42;
    CHECK(kstrtou8_from_user("0000000000bad",13,10,&byte)==0&&byte==0);
    fail_copy=1;byte=42;
    CHECK(kstrtou8_from_user("1",1,10,&byte)==-EFAULT&&byte==42);
    CHECK(kstrtobool_from_user("yes",3,&flag)==-EFAULT&&!flag);
    printf("PASS: %u kstrtox checks; unsigned long=%u bits; copy is a shim\n",checks,(unsigned)(sizeof(unsigned long)*CHAR_BIT));
    return 0;
}
'''


def main():
    cc = os.environ.get('CC') or shutil.which('gcc') or shutil.which('clang')
    if not cc:
        raise SystemExit('C compiler required')
    parts = [PREFIX]
    for path in ['lib/kstrtox.h', 'lib/kstrtox.c']:
        source = subprocess.check_output(['git', '-C', str(ROOT/'linux'), 'show', SHA+':'+path]).decode()
        parts.append(re.sub(r'^\s*#include[^\n]*\n', '', source, flags=re.M))
    with tempfile.TemporaryDirectory() as folder:
        source = Path(folder)/'kstrtox.c'
        binary = Path(folder)/('kstrtox.exe' if os.name == 'nt' else 'kstrtox')
        source.write_text('\n'.join(parts+[MAIN]), encoding='utf-8')
        subprocess.run([cc, '-std=gnu11', '-Wall', '-Wextra', '-Werror', '-O2', str(source), '-o', str(binary)], check=True)
        subprocess.run([str(binary)], check=True)


if __name__ == '__main__':
    main()
