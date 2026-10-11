"""Compile-pass/fail checks for pinned object-layout and build macros.

compiler.h dependencies are minimal shims; compiletime_assert uses C11 static
assertion, so optimizer-dependent BUILD_BUG elimination is NOT covered.
Pointer/long ABI-dependent PTR_ALIGN and ERR_PTR are deliberately not emulated.
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
#include <stddef.h>
#define __force
#define __same_type(a,b) __builtin_types_compatible_p(typeof(a),typeof(b))
#define compiletime_assert(c,m) _Static_assert(c,m)
#define __must_be_array(a) BUILD_BUG_ON_ZERO(__same_type((a), &(a)[0]))
'''
GOOD = r'''
struct sample {char tag;int key;long payload;};
static_assert(sizeof(int)>=2);
static_assert(sizeof(char)==1,"byte is one C byte");
static int initialized=7+BUILD_BUG_ON_ZERO(0);
int main(void) {
    int a[7], matrix[3][4];char text[]="abc";
    if(ARRAY_SIZE(a)!=7 || ARRAY_SIZE(matrix)!=3 || ARRAY_SIZE(text)!=4)return 1;
    struct sample s={0};const struct sample cs={0};
    if(container_of(&s.key,struct sample,key)!=&s)return 2;
    if(container_of_const(&cs.key,struct sample,key)!=&cs)return 3;
    static_assert(__same_type(container_of_const(&cs.key,struct sample,key),(const struct sample *)0));
    static_assert(__same_type(container_of_const(&s.key,struct sample,key),(struct sample *)0));
    static_assert(__same_type(container_of(&cs.key,struct sample,key),(struct sample *)0));
    static_assert(__same_type((typeof_member(struct sample,key))0,0));
    BUILD_BUG_ON(0);BUILD_BUG_ON_NOT_POWER_OF_2(8U);
    __BUILD_BUG_ON_NOT_POWER_OF_2(0U);
    ASSERT_STRUCT_OFFSET(struct sample,tag,0);
    int x=5;BUILD_BUG_ON_INVALID(x++);if(x!=5 || initialized!=7)return 4;
    for(unsigned x=0;x<1024;x++)for(unsigned a=1;a<=64;a*=2) {
        if(ALIGN(x,a)!=(x/a+(x%a!=0))*a)return 5;
        if(ALIGN_DOWN(x,a)!=x/a*a)return 6;
        if(IS_ALIGNED(x,a)!=(x%a==0))return 7;
    }
    return 0;
}
'''
BAD = {
    'array_pointer': 'int main(void){int *p=0;return ARRAY_SIZE(p);}',
    'member_type': 'struct s{int key;};int main(void){long value=0;(void)container_of(&value,struct s,key);}',
    'false_static_assert': 'static_assert(0,"expected false assertion");int main(void){return 0;}',
    'nonconstant_static_assert': 'int main(int argc,char **argv){(void)argv;static_assert(argc>0);}',
    'true_zero_check': 'int x=BUILD_BUG_ON_ZERO(1);int main(void){return x;}',
    'zero_power': 'int main(void){BUILD_BUG_ON_NOT_POWER_OF_2(0U);}',
    'non_power': 'int main(void){BUILD_BUG_ON_NOT_POWER_OF_2(3U);}',
    'bad_offset': 'struct s{int key;};int main(void){ASSERT_STRUCT_OFFSET(struct s,key,1);}',
}


def main():
    cc = os.environ.get('CC') or shutil.which('gcc') or shutil.which('clang')
    if not cc:
        raise SystemExit('C compiler required')
    parts = [PREFIX]
    for path in ['include/linux/build_bug.h', 'include/linux/array_size.h', 'include/linux/container_of.h',
                 'include/uapi/linux/const.h', 'include/linux/align.h']:
        source = subprocess.check_output(['git', '-C', str(ROOT/'linux'), 'show', SHA+':'+path]).decode()
        parts.append(re.sub(r'^\s*#include[^\n]*\n', '', source, flags=re.M))
    common = '\n'.join(parts)
    with tempfile.TemporaryDirectory() as folder:
        source = Path(folder)/'contracts.c'
        binary = Path(folder)/('contracts.exe' if os.name == 'nt' else 'contracts')
        command = [cc, '-std=gnu11', '-Wall', '-Wextra', '-Werror', '-O2', str(source), '-o', str(binary)]
        source.write_text(common+'\n'+GOOD, encoding='utf-8')
        subprocess.run(command, check=True)
        subprocess.run([str(binary)], check=True)
        for name, body in BAD.items():
            source.write_text(common+'\n'+body, encoding='utf-8')
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode == 0:
                raise AssertionError('Invalid program unexpectedly compiled: '+name)
        source.write_text('#define __CHECKER__\n'+common+'\nint main(void){return BUILD_BUG_ON_ZERO(1);}', encoding='utf-8')
        subprocess.run(command, check=True)
        subprocess.run([str(binary)], check=True)
    print('PASS: valid layout/array/alignment examples, 8 rejected programs, CHECKER override')


if __name__ == '__main__':
    main()
