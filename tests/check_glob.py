"""Compare actual glob matcher with DP for bounded wildcard languages."""
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SHA = 'adc218676eef25575469234709c2d87185ca223a'
PREFIX = r'''
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#define __pure __attribute__((pure))
#define MODULE_DESCRIPTION(x)
#define MODULE_LICENSE(x)
#define EXPORT_SYMBOL(x)
#define fallthrough __attribute__((fallthrough))
'''
MAIN = r'''
static unsigned checks;
#define CHECK(c) do {checks++;if(!(c)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#c);return 1;}}while(0)
static bool dp_match(const char *p,const char *s) {
    bool dp[8][8]={{false}};
    size_t n=strlen(p),m=strlen(s);dp[0][0]=true;
    for(size_t i=1;i<=n;i++) {
        if(p[i-1]=='*')dp[i][0]=dp[i-1][0];
        for(size_t j=1;j<=m;j++) {
            if(p[i-1]=='*')dp[i][j]=dp[i-1][j]||dp[i][j-1];
            else dp[i][j]=dp[i-1][j-1]&&(p[i-1]=='?'||p[i-1]==s[j-1]);
        }
    }
    return dp[n][m];
}
static void word(char *out,unsigned length,unsigned value,const char *alphabet,unsigned radix) {
    for(unsigned i=0;i<length;i++){out[i]=alphabet[value%radix];value/=radix;}
    out[length]=0;
}
int main(void) {
    char p[8],s[8];unsigned pcount=1;
    for(unsigned plen=0;plen<=5;plen++,pcount*=4) {
        for(unsigned pv=0;pv<pcount;pv++) {
            word(p,plen,pv,"ab?*",4);
            for(unsigned slen=0;slen<=6;slen++) {
                for(unsigned sv=0;sv<(1U<<slen);sv++) {
                    word(s,slen,sv,"ab",2);
                    CHECK(glob_match(p,s)==dp_match(p,s));
                }
            }
        }
    }
    CHECK(glob_match("*","a/b"));CHECK(glob_match("*",".hidden"));
    CHECK(glob_match("[^a]","a"));CHECK(glob_match("[^a]","^"));
    CHECK(!glob_match("[^a]","b"));CHECK(glob_match("[!a]","b"));
    CHECK(!glob_match("[!a]","a"));CHECK(glob_match("[]a]","]"));
    CHECK(glob_match("[]a]","a"));CHECK(!glob_match("[z-a]","m"));
    CHECK(glob_match("[abc","[abc"));CHECK(glob_match("\\*","*"));
    CHECK(!glob_match("\\*","abc"));CHECK(glob_match("[a-c]","b"));
    CHECK(!glob_match("?","\xc3\xa9"));CHECK(glob_match("??","\xc3\xa9"));
    printf("PASS: %u glob checks; bounded DP oracle and explicit class cases\n",checks);
    return 0;
}
'''


def main():
    cc = os.environ.get('CC') or shutil.which('gcc') or shutil.which('clang')
    if not cc:
        raise SystemExit('C compiler required')
    source = subprocess.check_output(['git', '-C', str(ROOT/'linux'), 'show', SHA+':lib/glob.c']).decode()
    source = re.sub(r'^\s*#include[^\n]*\n', '', source, flags=re.M)
    with tempfile.TemporaryDirectory() as folder:
        src = Path(folder)/'glob.c'
        exe = Path(folder)/('glob.exe' if os.name == 'nt' else 'glob')
        src.write_text(PREFIX+source+MAIN, encoding='utf-8')
        # Older GCC cannot infer that non-NULL back_pat implies initialized
        # back_str. Retain that diagnostic without editing the kernel source.
        warning_options = ['-Wno-error=maybe-uninitialized'] if 'gcc' in Path(cc).name.lower() else []
        subprocess.run([cc, '-std=gnu11', '-Wall', '-Wextra', '-Werror', *warning_options,
                        '-O2', str(src), '-o', str(exe)], check=True)
        subprocess.run([str(exe)], check=True)


if __name__ == '__main__':
    main()
