"""Exercise pinned C bodies, with userspace allocation and numeric shims.

Numeric tests use bounded decimal inputs only: libc conversions are not a
substitute for validation of kernel simple_strtoull's complete grammar.
Does not execute uaccess, faults, concurrent writes or kernel allocation.
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
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <assert.h>
typedef unsigned gfp_t;
#define GFP_KERNEL 0
#define KMALLOC_MAX_SIZE 1048576
#define EXPORT_SYMBOL(x)
#define EXPORT_SYMBOL_GPL(x)
#define fallthrough __attribute__((fallthrough))
static int allocations, fail_at, live;
static void *kmalloc_array(size_t n,size_t s,gfp_t g) {
    (void)g;
    if (++allocations == fail_at || (s && n > SIZE_MAX/s)) return NULL;
    void *p=malloc(n*s); if(p) live++; return p;
}
static void kfree(void *p) { if(p) { live--; free(p); } }
static char *kstrndup(const char *s,size_t max,gfp_t g) {
    size_t n=0; while(n<max && s[n]) n++;
    char *p=kmalloc_array(n+1,1,g);
    if(p) { memcpy(p,s,n);p[n]=0; } return p;
}
static unsigned long long simple_strtoull(const char *s,char **e,unsigned b) { return strtoull(s,e,b); }
static long simple_strtol(const char *s,char **e,unsigned b) { return strtol(s,e,b); }
static char *skip_spaces(const char *s) { while(isspace((unsigned char)*s))s++;return (char *)s; }
'''
MAIN = r'''
static unsigned checks;
#define CHECK(c) do { checks++;if(!(c)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#c);return 1;} }while(0)
int main(void) {
    int objects[4]={10,20,30,40};
    for(int na=0;na<=4;na++) for(int nb=0;nb<=4;nb++) {
        void *a[5]={0},*b[5]={0};
        for(int i=0;i<na;i++) a[i]=&objects[i];
        for(int i=0;i<nb;i++) b[i]=&objects[3-i];
        void **v=__memcat_p(a,b);CHECK(v!=NULL);CHECK(v[na+nb]==NULL);
        for(int i=0;i<na;i++) CHECK(v[i]==a[i]);
        for(int i=0;i<nb;i++) CHECK(v[na+i]==b[i]);
        kfree(v);CHECK(live==0);
    }
    void *empty[]={NULL};allocations=0;fail_at=1;
    CHECK(__memcat_p(empty,empty)==NULL);CHECK(live==0);fail_at=0;
    int argc=-1;char input[]="  alpha\t beta\n";
    char **v=argv_split(0,input,&argc);
    CHECK(v && argc==2 && !strcmp(v[0],"alpha") && !strcmp(v[1],"beta") && !v[2]);
    CHECK(!strcmp(input,"  alpha\t beta\n"));argv_free(v);CHECK(live==0);
    v=argv_split(0,"\"a b\"",&argc);
    CHECK(v && argc==2 && !strcmp(v[0],"\"a") && !strcmp(v[1],"b\""));argv_free(v);
    v=argv_split(0," \t\n",&argc);CHECK(v && argc==0 && !v[0]);argv_free(v);
    for(int failure=1;failure<=2;failure++) {
        allocations=0;fail_at=failure;argc=77;
        CHECK(argv_split(0,"a b",&argc)==NULL);CHECK(argc==77);CHECK(live==0);
    }
    fail_at=0;
    char *p;int n;char num[]="12,tail";p=num;
    CHECK(get_option(&p,&n)==2 && n==12 && !strcmp(p,"tail"));
    char minus[]="-";p=minus;CHECK(get_option(&p,&n)==0 && p==minus+1);
    int values[8]={0};p=get_options("1-3,7",8,values);
    CHECK(!*p && values[0]==4 && values[1]==1 && values[2]==2 && values[3]==3 && values[4]==7);
    int short_values[4]={-9,-9,-9,123456};p=get_options("1-5",3,short_values);
    CHECK(short_values[0]==4 && short_values[1]==1 && short_values[2]==2);
    CHECK(short_values[3]==123456 && !strcmp(p,"5"));
    p=get_options("1-5",0,values);CHECK(values[0]==5 && !*p);
    CHECK(memparse("1KB",&p)==1024 && !strcmp(p,"B"));
    CHECK(memparse("2M",&p)==2097152 && !*p);
    CHECK(parse_option_str("a=b,c","c"));CHECK(!parse_option_str("a=b,c","a"));
    CHECK(!parse_option_str("abc,def","ab"));CHECK(!parse_option_str("a, c","c"));
    char args[]="my-key=\"a b\"   flag";char *param,*val;
    p=next_arg(args,&param,&val);
    CHECK(!strcmp(param,"my-key") && !strcmp(val,"a b") && !strcmp(p,"flag"));
    p=next_arg(p,&param,&val);CHECK(!strcmp(param,"flag") && !val && !*p);
    CHECK(live==0);
    printf("PASS: %u pointer, allocation-failure and parser checks (userspace shims)\n",checks);
    return 0;
}
'''


def main():
    cc = os.environ.get('CC') or shutil.which('gcc') or shutil.which('clang')
    if not cc:
        raise SystemExit('C compiler required')
    parts = [PREFIX]
    for path in ['lib/memcat_p.c', 'lib/argv_split.c', 'lib/cmdline.c']:
        source = subprocess.check_output(['git', '-C', str(ROOT/'linux'), 'show', SHA+':'+path]).decode()
        parts.append(re.sub(r'^\s*#include[^\n]*\n', '', source, flags=re.M))
    parts.append(MAIN)
    with tempfile.TemporaryDirectory() as folder:
        source = Path(folder)/'strings.c'
        binary = Path(folder)/('strings.exe' if os.name == 'nt' else 'strings')
        source.write_text('\n'.join(parts), encoding='utf-8')
        subprocess.run([cc, '-std=c11', '-Wall', '-Wextra', '-Werror', '-O2', str(source), '-o', str(binary)], check=True)
        subprocess.run([str(binary)], check=True)


if __name__ == '__main__':
    main()
