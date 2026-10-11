"""Run pinned FSM search boundaries; not a general regex equivalence test."""
import os
from pathlib import Path
import re
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
static int run(struct ts_fsm_token *tokens,unsigned n,const char *text,unsigned want,unsigned offset) {
    struct ts_fsm *f=calloc(1,sizeof(*f)+n*sizeof(*tokens));CHECK(f!=NULL);
    f->ntokens=n;memcpy(f->tokens,tokens,n*sizeof(*tokens));
    for(unsigned i=0;i<n;i++)f->tokens[i].type=token_map[f->tokens[i].type];
    input=(const u8 *)text;length=strlen(text);
    struct ts_config c={f,0,block};
    for(chunk=1;chunk<=8;chunk++) {
        struct ts_state state={0};
        CHECK(fsm_find(&c,&state)==want);CHECK(state.offset==offset);
    }
    free(f);return 0;
}
int main(void) {
    struct ts_fsm_token single[]={{TS_FSM_SPECIFIC,TS_FSM_SINGLE,'a'}};
    CHECK(run(single,1,"a",0,1)==0);CHECK(run(single,1,"ab",UINT_MAX,0)==0);
    struct ts_fsm_token optional[]={{TS_FSM_SPECIFIC,TS_FSM_PERHAPS,'a'},
                                    {TS_FSM_SPECIFIC,TS_FSM_SINGLE,'a'}};
    CHECK(run(optional,2,"a",UINT_MAX,0)==0);CHECK(run(optional,2,"aa",0,2)==0);
    struct ts_fsm_token any[]={{TS_FSM_DIGIT,TS_FSM_ANY,0}};
    CHECK(run(any,1,"",UINT_MAX,0)==0);CHECK(run(any,1,"xyz",0,0)==0);
    struct ts_fsm_token multi[]={{TS_FSM_DIGIT,TS_FSM_MULTI,0}};
    CHECK(run(multi,1,"1xyz",0,1)==0);CHECK(run(multi,1,"xyz",UINT_MAX,0)==0);
    struct ts_fsm_token seq[]={{TS_FSM_SPECIFIC,TS_FSM_SINGLE,'a'},
                               {TS_FSM_SPECIFIC,TS_FSM_SINGLE,'b'},
                               {TS_FSM_SPECIFIC,TS_FSM_SINGLE,'c'}};
    CHECK(run(seq,3,"abc",0,3)==0);
    struct ts_fsm_token head[]={{TS_FSM_WILDCARD,TS_FSM_HEAD_IGNORE,0},
                                {TS_FSM_SPECIFIC,TS_FSM_SINGLE,'a'},
                                {TS_FSM_SPECIFIC,TS_FSM_SINGLE,'b'}};
    CHECK(run(head,3,"xxab",2,4)==0);CHECK(run(head,3,"aab",UINT_MAX,0)==0);
    for(unsigned b=0;b<256;b++) {
        struct ts_fsm_token t={token_map[TS_FSM_WILDCARD],0,0};CHECK(match_token(&t,b));
        t.type=token_map[TS_FSM_ASCII];CHECK(match_token(&t,b)==(b<128));
        t.type=token_map[TS_FSM_DIGIT];CHECK(match_token(&t,b)==(b>='0'&&b<='9'));
        t.type=0;t.value=b;CHECK(match_token(&t,b));CHECK(!match_token(&t,(u8)(b+1)));
    }
    printf("PASS: %u FSM checks; explicit boundaries and byte classes\n",checks);return 0;
}
'''


def main():
    cc = os.environ.get('CC') or shutil.which('gcc') or shutil.which('clang')
    if not cc:
        raise SystemExit('C compiler required')
    def read(path):
        return subprocess.check_output(['git', '-C', str(ROOT/'linux'), 'show', SHA+':'+path]).decode()
    header = re.sub(r'^\s*#include[^\n]*\n', '', read('include/linux/textsearch_fsm.h'), flags=re.M)
    ctype = '\n'.join(line for line in read('include/linux/ctype.h').splitlines()
                      if re.match(r'#define\s+_(U|L|D|C|P|S|X|SP)\s', line))
    source = read('lib/ts_fsm.c')
    source = source[source.index('struct ts_fsm\n'):source.index('static struct ts_config *fsm_init')]
    prefix = PREFIX+'\ntypedef uint16_t u16; typedef uint16_t __u16; typedef uint8_t __u8;\n#define likely(x) (x)\n#define fallthrough __attribute__((fallthrough))\n'
    with tempfile.TemporaryDirectory() as folder:
        src = Path(folder)/'fsm.c'
        exe = Path(folder)/('fsm.exe' if os.name == 'nt' else 'fsm')
        src.write_text(prefix+ctype+'\n'+header+source+MAIN, encoding='utf-8')
        subprocess.run([cc, '-std=gnu11', '-Wall', '-Wextra', '-Werror', '-O2', str(src), '-o', str(exe)], check=True)
        subprocess.run([str(exe)], check=True)


if __name__ == '__main__':
    main()
