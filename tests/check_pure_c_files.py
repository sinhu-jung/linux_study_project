"""Compile actual pinned pure-C helpers with minimal userspace type shims.

Not a kernel runtime/concurrency test. Source bodies are copied unchanged;
kernel includes, symbol exports and module metadata use userspace shims.
"""
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
SHA='adc218676eef25575469234709c2d87185ca223a'
FILES=['include/linux/crc4.h','include/linux/crc7.h','include/linux/crc8.h',
       'include/linux/crc16.h','include/linux/crc-ccitt.h','include/linux/crc-itu-t.h',
       'include/linux/iommu-helper.h','lib/crc4.c','lib/crc7.c','lib/crc8.c',
       'lib/crc16.c','lib/crc-ccitt.c','lib/crc-itu-t.c','lib/clz_tab.c','lib/net_utils.c',
       'lib/devmem_is_allowed.c']
PREFIX=r'''
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <assert.h>
typedef uint8_t u8;
typedef uint16_t u16;
typedef uint64_t u64;
#define EXPORT_SYMBOL(x)
#define EXPORT_SYMBOL_GPL(x)
#define MODULE_DESCRIPTION(x)
#define MODULE_AUTHOR(x)
#define MODULE_LICENSE(x)
#define ETH_ALEN 6
#define BUG_ON(x) assert(!(x))
#define is_power_of_2(x) ((x) && !((x)&((x)-1)))
#define DIV_ROUND_UP(x,d) (((x)+(d)-1)/(d))
static size_t study_strnlen(const char *s,size_t n) { size_t i=0; while(i<n && s[i])i++; return i; }
#define strnlen study_strnlen
static int hex_to_bin(char c) { if(c>='0'&&c<='9')return c-'0';if(c>='a'&&c<='f')return c-'a'+10;if(c>='A'&&c<='F')return c-'A'+10;return -1; }
static int fake_exclusive, fake_ram;
static unsigned long observed_phys, observed_pfn;
#define PFN_PHYS(pfn) ((pfn)<<12)
static int iomem_is_exclusive(unsigned long phys) { observed_phys=phys;return fake_exclusive; }
static int page_is_ram(unsigned long pfn) { observed_pfn=pfn;return fake_ram; }
'''
MAIN=r'''
static unsigned checks;
#define CHECK(condition) do { checks++; if(!(condition)) { fprintf(stderr,"FAIL at %d: %s\n",__LINE__,#condition); return 1; } } while(0)
int main(void) {
    unsigned i,split; u8 t[256]; u8 mac[6], before[6];
    const u8 msg[]="123456789";
    const u8 pair[]={1,0}; const u8 ccitt_pair[]={1,0x89};const u8 itu_pair[]={1,0x10};
    CHECK(crc4(0,0xab,8)==0xb);CHECK(crc4(0,0xab,5)==8);CHECK(crc4(7,0xab,0)==7);
    CHECK(crc7_be(0,msg,9)==0xea);
    CHECK(crc16(0,pair,2)==0x9001);CHECK(crc_ccitt(0,ccitt_pair,2)==0x11);CHECK(crc_itu_t(0,itu_pair,2)==0x2100);
    CHECK(crc16_byte(0x1234,0x34)==0x12);CHECK(crc_ccitt_byte(0xabcd,0xcd)==0xab);CHECK(crc_itu_t_byte(0x1234,0x12)==0x3400);
    CHECK(crc16(0,msg,9)==0xbb3d);CHECK(crc_ccitt(0,msg,9)==0x2189);CHECK(crc_itu_t(0,msg,9)==0x31c3);
    for(split=0;split<=9;split++) {
        CHECK(crc16(crc16(0,msg,split),msg+split,9-split)==0xbb3d);
        CHECK(crc_ccitt(crc_ccitt(0,msg,split),msg+split,9-split)==0x2189);
        CHECK(crc_itu_t(crc_itu_t(0,msg,split),msg+split,9-split)==0x31c3);
    }
    CHECK(crc16(0x5678,NULL,0)==0x5678);CHECK(crc7_be(0x12,NULL,0)==0x12);
    crc8_populate_msb(t,7);CHECK(t[0]==0);CHECK(t[1]==7);CHECK(t[2]==14);CHECK(t[3]==9);
    {const u8 two[]={1,2}; CHECK(crc8(t,two,2,0)==0x1b);}
    for(i=0;i<256;i++) {
        u8 complement=(u8)(i^255);CHECK(crc8(t,&complement,1,(u8)i)==CRC8_GOOD_VALUE(t));
        unsigned v=i,n=0;while(v){n++;v>>=1;}CHECK(__clz_tab[i]==n);
    }
    CHECK(iommu_device_max_index(16,8,19)==12);
    CHECK(!iommu_is_span_boundary(5,3,0,8));CHECK(iommu_is_span_boundary(6,3,0,8));
    CHECK(iommu_num_pages(4095,2,4096)==2);CHECK(iommu_num_pages(4096,4096,4096)==1);CHECK(iommu_num_pages(1,0,4096)==1);
    memset(mac,0xa5,6);memcpy(before,mac,6);
    CHECK(!mac_pton("aa:bb:cc:dd:gg:ff",mac));CHECK(!memcmp(mac,before,6));
    CHECK(!mac_pton("aa:bb",mac));CHECK(!memcmp(mac,before,6));
    CHECK(!mac_pton("aa-bb:cc:dd:ee:ff",mac));CHECK(!memcmp(mac,before,6));
    CHECK(mac_pton("Af:01:23:45:67:89",mac));CHECK(mac[0]==0xaf);CHECK(mac[5]==0x89);
    CHECK(mac_pton("aa:bb:cc:dd:ee:ffXYZ",mac));CHECK(mac[5]==0xff);
    for(fake_exclusive=0;fake_exclusive<2;fake_exclusive++) {
        for(fake_ram=0;fake_ram<2;fake_ram++) {
            observed_phys=observed_pfn=~0UL;
            CHECK(devmem_is_allowed(7)==(!fake_exclusive&&!fake_ram));
            CHECK(observed_phys==(7UL<<12));
            CHECK(observed_pfn==(fake_exclusive?~0UL:7UL));
        }
    }
    printf("PASS: %u checks on actual C helper bodies (userspace shims; no kernel concurrency claims)\n",checks);
    return 0;
}
'''


def main():
    cc=os.environ.get('CC') or shutil.which('gcc') or shutil.which('clang')
    if not cc:raise SystemExit('C compiler required for actual-source helper validation')
    parts=[PREFIX]
    for name in FILES:
        source=subprocess.check_output(['git','-C',str(ROOT/'linux'),'show',SHA+':'+name]).decode()
        parts.append(re.sub(r'^\s*#include[^\n]*\n','',source,flags=re.M))
    parts.append(MAIN)
    with tempfile.TemporaryDirectory() as folder:
        source=Path(folder)/'helpers.c';binary=Path(folder)/('helpers.exe' if os.name=='nt' else 'helpers')
        source.write_text('\n'.join(parts),encoding='utf-8')
        subprocess.run([cc,'-std=c11','-Wall','-Wextra','-Werror','-O2',str(source),'-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)


if __name__=='__main__':main()
