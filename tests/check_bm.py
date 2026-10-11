"""Pinned BM algorithm against naive contiguous and per-block search."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from check_kmp import ROOT, SHA, PREFIX

MAIN = r'''
static const u8 *input;static unsigned length,chunk;
static unsigned block(unsigned used,const u8 **out,struct ts_config *c,struct ts_state *s) {
    (void)c;(void)s;if(used>=length)return 0;
    *out=input+used;return length-used<chunk?length-used:chunk;
}
static unsigned checks;
#define CHECK(c) do {checks++;if(!(c)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#c);return 1;}}while(0)
static unsigned naive(const u8 *p,unsigned n,int flags) {
    for(unsigned start=0;start<length;start+=chunk) {
        unsigned end=start+chunk<length?start+chunk:length;
        for(unsigned i=start;i+n<=end;i++) {
            unsigned j=0;
            for(;j<n;j++)if((flags?toupper(p[j]):p[j])!=(flags?toupper(input[i+j]):input[i+j]))break;
            if(j==n)return i;
        }
    }
    return UINT_MAX;
}
static void word(u8 *s,unsigned n,unsigned value) {
    for(unsigned i=0;i<n;i++)s[i]=(value&(1U<<i))?'a':'B';
}
int main(void) {
    u8 p[8],s[10];
    for(unsigned n=1;n<=5;n++)for(unsigned pv=0;pv<(1U<<n);pv++)for(int flags=0;flags<=2;flags+=2) {
        word(p,n,pv);
        struct ts_bm *bm=calloc(1,sizeof(*bm)+n*sizeof(unsigned)+n);
        CHECK(bm!=NULL);bm->patlen=n;bm->pattern=(u8 *)(bm->good_shift+n);
        for(unsigned j=0;j<n;j++)bm->pattern[j]=flags?toupper(p[j]):p[j];
        compute_prefix_tbl(bm,flags);
        struct ts_config c={bm,flags,block};
        for(length=0;length<=8;length++)for(unsigned sv=0;sv<(1U<<length);sv++) {
            word(s,length,sv);input=s;
            if(flags)for(unsigned j=0;j<length;j++)s[j]=s[j]=='a'?'A':'b';
            for(chunk=1;chunk<=8;chunk++) {
                struct ts_state state={0};
                unsigned got=bm_find(&c,&state);CHECK(got==naive(p,n,flags));
                CHECK(state.offset==0);
                if(got!=UINT_MAX)CHECK(bm_find(&c,&state)==got);
            }
        }
        free(bm);
    }
    printf("PASS: %u BM checks; bounded block-local oracle and unchanged offsets\n",checks);
    return 0;
}
'''


def main():
    cc = os.environ.get('CC') or shutil.which('gcc') or shutil.which('clang')
    if not cc:
        raise SystemExit('C compiler required')
    source = subprocess.check_output(['git', '-C', str(ROOT/'linux'), 'show', SHA+':lib/ts_bm.c']).decode()
    source = source[source.index('#define ASIZE'):source.index('static struct ts_config *bm_init')]
    prefix = PREFIX + '\n#include <stdbool.h>\n#define max_t(t,a,b) ((t)(a)>(t)(b)?(t)(a):(t)(b))\n'
    with tempfile.TemporaryDirectory() as folder:
        src = Path(folder)/'bm.c'
        exe = Path(folder)/('bm.exe' if os.name == 'nt' else 'bm')
        src.write_text(prefix+source+MAIN, encoding='utf-8')
        # Original code intentionally mixes signed candidate offsets with
        # unsigned lengths; tested values stay in their common positive range.
        subprocess.run([cc, '-std=gnu11', '-Wall', '-Wextra', '-Werror',
                        '-Wno-sign-compare', '-O2', str(src), '-o', str(exe)], check=True)
        subprocess.run([str(exe)], check=True)


if __name__ == '__main__':
    main()
