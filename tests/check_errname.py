"""Actual lookup with pinned asm-generic errno definitions; not all architectures."""
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
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define BUILD_BUG_ON_ZERO(c) (sizeof(char[1-2*!!(c)])-1)
#define static_assert(c) _Static_assert(c,#c)
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
#define IS_ENABLED(x) 0
#define EXPORT_SYMBOL(x)
'''


def main():
    cc = os.environ.get('CC') or shutil.which('gcc') or shutil.which('clang')
    if not cc:
        raise SystemExit('C compiler required')
    read = lambda p: subprocess.check_output(['git', '-C', str(ROOT/'linux'), 'show', SHA+':'+p]).decode()
    strip = lambda s: re.sub(r'^\s*#include[^\n]*\n', '', s, flags=re.M)
    definitions = [read(p) for p in ['include/uapi/asm-generic/errno-base.h', 'include/uapi/asm-generic/errno.h', 'include/linux/errno.h']]
    names = re.findall(r'^#define\s+(E\w+)\s+', '\n'.join(definitions), re.M)
    aliases = {'EWOULDBLOCK': 'EAGAIN', 'EDEADLOCK': 'EDEADLK'}
    checks = []
    for name in names:
        if name == 'ENOGRACE':
            checks.append('if(errname(ENOGRACE)!=NULL)return 1;')
        else:
            canonical = aliases.get(name, name)
            checks.append(f'if(!errname({name}) || strcmp(errname({name}),"{canonical}"))return 1;')
            checks.append(f'if(!errname(-{name}) || strcmp(errname(-{name}),"-{canonical}"))return 1;')
    checks.append('if(errname(0)||errname(41)||errname(58)||errname(520)||errname(9999))return 1;')
    with tempfile.TemporaryDirectory() as folder:
        source = Path(folder)/'errname.c'
        binary = Path(folder)/('errname.exe' if os.name == 'nt' else 'errname')
        for enabled in [False, True]:
            parts = [PREFIX, *map(strip, definitions)]
            if enabled:
                parts.append('#define CONFIG_SYMBOLIC_ERRNAME 1')
            parts.append(strip(read('include/linux/errname.h')))
            if enabled:
                parts.append(strip(read('lib/errname.c')))
                body = '\n'.join(checks)
            else:
                body = 'if(errname(EIO)||errname(-EIO)||errname(0)||errname(EPROBE_DEFER))return 1;'
            parts.append('int main(void) {\n'+body+'\nputs("PASS: errname '+('enabled asm-generic mappings' if enabled else 'disabled stub')+'");return 0;}')
            source.write_text('\n'.join(parts), encoding='utf-8')
            subprocess.run([cc, '-std=gnu11', '-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter', '-O2', str(source), '-o', str(binary)], check=True)
            subprocess.run([str(binary)], check=True)


if __name__ == '__main__':
    main()
