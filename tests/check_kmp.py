"""Actual KMP prefix/search functions with bounded block-provider shims."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SHA = 'adc218676eef25575469234709c2d87185ca223a'
PREFIX = r'''
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <ctype.h>
typedef uint8_t u8;
#define TS_IGNORECASE 2
#define unlikely(x) (x)
struct ts_state {unsigned offset;};
struct ts_config {
    void *priv;int flags;
    unsigned (*get_next_block)(unsigned,const u8 **,struct ts_config *,struct ts_state *);
};
static void *ts_config_priv(struct ts_config *c){return c->priv;}
'''
MAIN = r'''
static const u8 *input;static unsigned length,chunk;
static unsigned block(unsigned used,const u8 **out,struct ts_config *c,struct ts_state *s) {
    (void)c;(void)s;if(used>=length)return 0;
    *out=input+used;return length-used<chunk?length-used:chunk;
}
static unsigned checks;
#define CHECK(c) do {checks++;if(!(c)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#c);return 1;}}while(0)
static unsigned naive(const u8 *p,unsigned n,const u8 *s,unsigned m,unsigned start,int flags) {
    for(unsigned i=start;i+n<=m;i++) {
        unsigned j=0;
        for(;j<n;j++)if((flags?toupper(p[j]):p[j])!=(flags?toupper(s[i+j]):s[i+j]))break;
        if(j==n)return i;
    }
    return UINT_MAX;
}
static void word(u8 *s,unsigned len,unsigned bits) {
    for(unsigned i=0;i<len;i++)s[i]=(bits&(1U<<i))?'a':'B';
}
int main(void) {
    u8 pattern[8],text[10];
    for(unsigned n=1;n<=5;n++)for(unsigned pv=0;pv<(1U<<n);pv++)for(int flags=0;flags<=2;flags+=2) {
        word(pattern,n,pv);
        struct ts_kmp *k=calloc(1,sizeof(*k)+n*sizeof(unsigned)+n);
        CHECK(k!=NULL);k->pattern_len=n;k->pattern=(u8 *)(k->prefix_tbl+n);
        compute_prefix_tbl(pattern,n,k->prefix_tbl,flags);
        for(unsigned q=0;q<n;q++) {
            unsigned best=0;
            for(unsigned span=1;span<=q;span++) {
                unsigned j=0;
                for(;j<span;j++)if((flags?toupper(pattern[j]):pattern[j])!=(flags?toupper(pattern[q+1-span+j]):pattern[q+1-span+j]))break;
                if(j==span)best=span;
            }
            CHECK(k->prefix_tbl[q]==best);
            k->pattern[q]=flags?toupper(pattern[q]):pattern[q];
        }
        struct ts_config c={k,flags,block};
        for(length=0;length<=8;length++)for(unsigned tv=0;tv<(1U<<length);tv++) {
            word(text,length,tv);input=text;
            /* Opposite ASCII case exercises case folding against stored pattern. */
            if(flags)for(unsigned i=0;i<length;i++)text[i]=(text[i]=='a')?'A':'b';
            for(chunk=1;chunk<=8;chunk++) {
                struct ts_state state={0};
                unsigned want=naive(pattern,n,text,length,0,flags);
                unsigned got=kmp_find(&c,&state);CHECK(got==want);
                CHECK(state.offset==(want==UINT_MAX?0:want+n));
                if(want!=UINT_MAX) {
                    unsigned start=state.offset;
                    CHECK(kmp_find(&c,&state)==naive(pattern,n,text,length,start,flags));
                }
            }
        }
        free(k);
    }
    printf("PASS: %u KMP checks; prefix oracle, block sizes 1..8, next offsets\n",checks);
    return 0;
}
'''


def main():
    cc = os.environ.get('CC') or shutil.which('gcc') or shutil.which('clang')
    if not cc:
        raise SystemExit('C compiler required')
    source = subprocess.check_output(['git', '-C', str(ROOT/'linux'), 'show', SHA+':lib/ts_kmp.c']).decode()
    # Keep the original private structure and both algorithm functions verbatim.
    source = source[source.index('struct ts_kmp\n'):source.index('static struct ts_config *kmp_init')]
    with tempfile.TemporaryDirectory() as folder:
        src = Path(folder)/'kmp.c'
        exe = Path(folder)/('kmp.exe' if os.name == 'nt' else 'kmp')
        src.write_text(PREFIX+source+MAIN, encoding='utf-8')
        subprocess.run([cc, '-std=gnu11', '-Wall', '-Wextra', '-Werror', '-O2', str(src), '-o', str(exe)], check=True)
        subprocess.run([str(exe)], check=True)


if __name__ == '__main__':
    main()
