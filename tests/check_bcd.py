"""Actual BCD macros/functions over the complete valid two-digit domain."""
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
typedef uint8_t u8;
#ifndef __attribute_const__
#define __attribute_const__ __attribute__((const))
#endif
#define EXPORT_SYMBOL(x)
'''
MAIN = r'''
static unsigned checks;
#define CHECK(c) do {checks++;if(!(c)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#c);return 1;}}while(0)
int main(void) {
    unsigned valid=0;
    for(unsigned x=0;x<256;x++) {
        unsigned tens=x/16,units=x%16;
        int expected=tens<=9 && units<=9;
        CHECK(bcd_is_valid(x)==expected);
        CHECK(_bcd2bin(x)==tens*10+units);
        if(expected)valid++;
    }
    CHECK(valid==100);
    for(unsigned x=0;x<100;x++) {
        unsigned expected=(x/10)*16+x%10;
        volatile unsigned dynamic=x;
        CHECK(_bin2bcd(x)==expected);
        CHECK(bin2bcd(dynamic)==expected);
        CHECK(const_bin2bcd(x)==expected);
        volatile u8 byte=expected;
        CHECK(bcd2bin((unsigned)byte)==x);
        CHECK(_bcd2bin(_bin2bcd(x))==x);
    }
    CHECK(bin2bcd(42)==0x42);CHECK(bcd2bin(0x42)==42);
    CHECK(_bcd2bin(0xfa)==160);CHECK(!bcd_is_valid(0xfa));
    printf("PASS: %u BCD checks\n",checks);return 0;
}
'''


def main():
    cc = os.environ.get('CC') or shutil.which('gcc') or shutil.which('clang')
    if not cc:
        raise SystemExit('C compiler required')
    parts = [PREFIX]
    for path in ['include/linux/bcd.h', 'lib/bcd.c']:
        source = subprocess.check_output(['git', '-C', str(ROOT/'linux'), 'show', SHA+':'+path]).decode()
        parts.append(re.sub(r'^\s*#include[^\n]*\n', '', source, flags=re.M))
    with tempfile.TemporaryDirectory() as folder:
        source = Path(folder)/'bcd.c'
        binary = Path(folder)/('bcd.exe' if os.name == 'nt' else 'bcd')
        source.write_text('\n'.join(parts+[MAIN]), encoding='utf-8')
        subprocess.run([cc, '-std=gnu11', '-Wall', '-Wextra', '-Werror', '-O2', str(source), '-o', str(binary)], check=True)
        subprocess.run([str(binary)], check=True)


if __name__ == '__main__':
    main()
