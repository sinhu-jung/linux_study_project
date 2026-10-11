"""Compare pinned base64 C with Python encoding; expose permissive decoding."""
import base64
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SHA = 'adc218676eef25575469234709c2d87185ca223a'


def main():
    cc = os.environ.get('CC') or shutil.which('gcc') or shutil.which('clang')
    if not cc:
        raise SystemExit('C compiler required')
    parts = []
    for path in ['include/linux/base64.h', 'lib/base64.c']:
        part = subprocess.check_output(['git', '-C', str(ROOT/'linux'), 'show', SHA+':'+path]).decode()
        parts.append(re.sub(r'^\s*#include[^\n]*\n', '', part, flags=re.M))
    source = '\n'.join(parts)
    rng = random.Random(4648)
    inputs = [b'', b'f', b'fo', b'foo', b'foob', b'fooba', b'foobar']
    inputs += [bytes([n]) for n in range(256)]
    inputs += [bytes(rng.randrange(256) for _ in range(n)) for n in range(257)]
    cases = []
    for data in inputs:
        encoded = base64.b64encode(data).decode()
        raw = ''.join('\\x%02x' % n for n in data)
        cases.append('ROUND("%s", %d, "%s");' % (raw, len(data), encoded))
    prefix = r'''
#include <stdint.h>
#include <string.h>
#include <stdio.h>
typedef uint8_t u8; typedef uint32_t u32;
#define EXPORT_SYMBOL_GPL(x)
#define DIV_ROUND_UP(n,d) (((n)+(d)-1)/(d))
'''
    main_code = r'''
static unsigned checks;
#define CHECK(c) do {checks++;if(!(c)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#c);return 1;}}while(0)
#define ROUND(raw,n,expected) do { \
    memset(out,0xa5,sizeof(out));memset(back,0xa5,sizeof(back)); \
    int got=base64_encode((const u8*)raw,n,out); \
    CHECK(got==(int)strlen(expected));CHECK(memcmp(out,expected,got)==0); \
    CHECK((unsigned char)out[got]==0xa5); \
    CHECK(base64_decode(out,got,back)==n);CHECK(memcmp(back,raw,n)==0); \
    CHECK(back[n]==0xa5); \
}while(0)
int main(void) {
char out[1024];u8 back[1024];
'''
    tail = r'''
CHECK(BASE64_CHARS(1)==2);CHECK(BASE64_CHARS(2)==3);CHECK(BASE64_CHARS(3)==4);
CHECK(base64_decode("====",4,back)==0);
CHECK(base64_decode("A",1,back)==0);
CHECK(base64_decode("Zg",2,back)==1&&back[0]=='f');
CHECK(base64_decode("Zg==A",5,back)==1&&back[0]=='f');
CHECK(base64_decode("Zh",2,back)==-1);
CHECK(base64_decode("Zg==\n",5,back)==-1);
CHECK(base64_decode("Zg\0=",4,back)==-1);
memset(back,0xa5,sizeof(back));
CHECK(base64_decode("Zm9v!",5,back)==-1);CHECK(memcmp(back,"foo",3)==0);
printf("PASS: %u Base64 checks; permissive cases and partial output verified\n",checks);
return 0;
}
'''
    with tempfile.TemporaryDirectory() as folder:
        src = Path(folder)/'base64.c'
        exe = Path(folder)/('base64.exe' if os.name == 'nt' else 'base64')
        src.write_text(prefix+source+main_code+'\n'.join(cases)+tail, encoding='utf-8')
        subprocess.run([cc, '-std=gnu11', '-Wall', '-Wextra', '-Werror', '-O2', str(src), '-o', str(exe)], check=True)
        subprocess.run([str(exe)], check=True)


if __name__ == '__main__':
    main()
