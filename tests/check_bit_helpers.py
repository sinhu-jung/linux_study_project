"""Actual source bit-reversal/popcount tests; compile each configuration branch."""
from pathlib import Path
import os
import re
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
SHA='adc218676eef25575469234709c2d87185ca223a'
PREFIX=r'''
#include <stdint.h>
#include <stdio.h>
typedef uint8_t u8;typedef uint16_t u16;typedef uint32_t u32;typedef uint64_t __u64;
#define EXPORT_SYMBOL(x)
#define EXPORT_SYMBOL_GPL(x)
#define MODULE_AUTHOR(x)
#define MODULE_DESCRIPTION(x)
#define MODULE_LICENSE(x)
#define swab32(x) __builtin_bswap32(x)
'''
MAIN=r'''
static unsigned checks;
#define CHECK(x) do {checks++;if(!(x)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x);return 1;}}while(0)
static unsigned pop(uint64_t x){unsigned r=0;while(x){r+=(unsigned)(x&1);x>>=1;}return r;}
static uint32_t rev(uint32_t x,unsigned bits){uint32_t r=0;while(bits--){r=(r<<1)|(x&1);x>>=1;}return r;}
int main(void){
    unsigned i;uint32_t state=1;
    for(i=0;i<256;i++){
        volatile u8 x=(u8)i;
        CHECK(byte_rev_table[i]==rev(i,8));CHECK(bitrev8(x)==rev(i,8));
        CHECK(__constant_bitrev8(i)==rev(i,8));CHECK(byte_rev_table[byte_rev_table[i]]==i);
        CHECK(__sw_hweight8(i)==pop(i));
    }
    for(i=0;i<65536;i++){
        volatile u16 x=(u16)i;CHECK(bitrev16(x)==rev(i,16));CHECK(__sw_hweight16(i)==pop(i));
    }
    for(i=0;i<4096;i++){
        state=state*1664525u+1013904223u;
        volatile u32 x=state;uint64_t wide=((uint64_t)state<<32)|(state^0xa5a5a5a5u);
        uint32_t by_byte=(rev(x&255,8))|(rev((x>>8)&255,8)<<8)|(rev((x>>16)&255,8)<<16)|(rev((x>>24)&255,8)<<24);
        CHECK(bitrev32(x)==rev(x,32));CHECK(__constant_bitrev32(x)==rev(x,32));
        CHECK(bitrev8x4(x)==by_byte);CHECK(__constant_bitrev8x4(x)==by_byte);
        CHECK(__sw_hweight32(x)==pop(x));CHECK(__sw_hweight64(wide)==pop(wide));
    }
    CHECK(bitrev32(0x01020408u)==0x10204080u);CHECK(bitrev8x4(0x01020408u)==0x80402010u);
    CHECK(__sw_hweight8(0xb5)==5);CHECK(__sw_hweight64(UINT64_C(0x8000000100000001))==3);
    CHECK(__sw_hweight64(UINT64_MAX)==64);CHECK(__sw_hweight64(0)==0);
    printf("PASS: %u checks; BITS_PER_LONG=%d\n",checks,BITS_PER_LONG);return 0;
}
'''


def main():
    cc=os.environ.get('CC') or shutil.which('gcc') or shutil.which('clang')
    if not cc:raise SystemExit('C compiler required')
    parts=[PREFIX]
    for name in ['include/linux/bitrev.h','lib/bitrev.c','lib/hweight.c']:
        raw=subprocess.check_output(['git','-C',str(ROOT/'linux'),'show',SHA+':'+name]).decode()
        parts.append(re.sub(r'^\s*#include[^\n]*\n','',raw,flags=re.M))
    parts.append(MAIN)
    with tempfile.TemporaryDirectory() as folder:
        source=Path(folder)/'bits.c';source.write_text('\n'.join(parts),encoding='utf-8')
        for width in [32,64]:
            for fast in [False,True]:
                binary=Path(folder)/('bits.exe' if os.name=='nt' else 'bits')
                flags=[f'-DBITS_PER_LONG={width}']+(['-DCONFIG_ARCH_HAS_FAST_MULTIPLIER'] if fast else [])
                subprocess.run([cc,'-std=gnu11','-Wall','-Wextra','-Werror','-O2',*flags,str(source),'-o',str(binary)],check=True)
                print(f'fast_multiplier={fast}',flush=True)
                subprocess.run([str(binary)],check=True)


if __name__=='__main__':main()
