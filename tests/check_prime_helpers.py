"""Pinned pure helpers and iteration macros, with explicit dependency stubs.

Does not execute allocation, cache publication, RCU, mutexes or kernel selftest.
Both initial bitmap literals are independently checked against trial division.
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
#include <stdio.h>
#include <limits.h>
static unsigned long int_sqrt(unsigned long x) {
    unsigned long r=0;while(r+1<=x/(r+1))r++;return r;
}
#define roundup(x,d) ((((x)+(d)-1)/(d))*(d))
static void __clear_bit(unsigned long bit,unsigned long *p) {
    p[bit/(sizeof(long)*CHAR_BIT)]&=~(1UL<<(bit%(sizeof(long)*CHAR_BIT)));
}
'''
MAIN = r'''
static unsigned checks;
#define CHECK(c) do { checks++;if(!(c)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#c);return 1;} }while(0)
static bool reference_prime(unsigned long n) {
    if(n<2)return false;
    for(unsigned long d=2;d<=n/d;d++)if(n%d==0)return false;
    return true;
}
/* Independent stub for testing header iteration, not the public cache path. */
unsigned long next_prime_number(unsigned long n) {
    while(n<ULONG_MAX){n++;if(reference_prime(n))return n;}return n;
}
int main(void) {
    CHECK(!slow_is_prime_number(0));CHECK(slow_is_prime_number(1));
    for(unsigned long n=2;n<2000;n++) {
        CHECK(slow_is_prime_number(n)==reference_prime(n));
        CHECK(slow_next_prime_number(n)==next_prime_number(n));
    }
    CHECK(slow_next_prime_number(ULONG_MAX)==ULONG_MAX);
    unsigned long bits[4];
    for(unsigned long step=2;step<=17;step++) {
        for(unsigned i=0;i<4;i++)bits[i]=~0UL;
        CHECK(clear_multiples(step,bits,32,100)==step);
        for(unsigned i=0;i<128;i++) {
            bool actual=(bits[i/(sizeof(long)*CHAR_BIT)]>>(i%(sizeof(long)*CHAR_BIT)))&1;
            bool removed=(i>=32 && i<100 && i>=2*step && i%step==0);
            CHECK(actual==!removed);
        }
    }
    unsigned long p,values[8];unsigned n=0;
    for_each_prime_number(p,10)values[n++]=p;
    CHECK(n==4 && values[0]==2 && values[1]==3 && values[2]==5 && values[3]==7);
    n=0;for_each_prime_number_from(p,4,10)values[n++]=p;
    CHECK(n==3 && values[0]==4 && values[1]==5 && values[2]==7);
    n=0;for_each_prime_number(p,1)n++;CHECK(n==0);
    printf("PASS: %u prime helper/macro checks; no cache or RCU runtime coverage\n",checks);
    return 0;
}
'''


def extract_function(source, name):
    start = source.rfind('static ', 0, source.index(name))
    if start < 0:
        raise ValueError('Missing signature: ' + name)
    opening = source.index('{', source.index(name))
    depth = 0
    for end in range(opening, len(source)):
        if source[end] == '{':
            depth += 1
        elif source[end] == '}':
            depth -= 1
            if depth == 0:
                return source[start:end+1]
    raise ValueError(name)


def main():
    cc = os.environ.get('CC') or shutil.which('gcc') or shutil.which('clang')
    if not cc:
        raise SystemExit('C compiler required')
    read = lambda p: subprocess.check_output(['git', '-C', str(ROOT/'linux'), 'show', SHA+':'+p]).decode()
    source = read('lib/math/prime_numbers.c')
    blocks = re.findall(r'static const struct primes small_primes = \{(.*?)\n\};', source, re.S)
    for size, block in zip([64, 32], blocks):
        actual = [int(n) for n in re.findall(r'BIT\((\d+)\)', block)]
        expected = [n for n in range(2, size) if all(n % d for d in range(2, n))]
        assert actual == expected
    assert len(blocks) == 2
    # Locate each signature directly; preceding comments/variables are excluded.
    helpers = []
    for name in ['slow_is_prime_number', 'slow_next_prime_number', 'clear_multiples']:
        pos = source.index(name+'(')
        start = source.rfind('static ', 0, pos)
        tail = source[start:]
        helpers.append(extract_function(tail, name))
    header = re.sub(r'^\s*#include[^\n]*\n', '', read('include/linux/prime_numbers.h'), flags=re.M)
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder)/'prime.c'
        binary = Path(folder)/('prime.exe' if os.name == 'nt' else 'prime')
        path.write_text('\n'.join([PREFIX, header, *helpers, MAIN]), encoding='utf-8')
        subprocess.run([cc, '-std=gnu11', '-Wall', '-Wextra', '-Werror', '-O2', str(path), '-o', str(binary)], check=True)
        subprocess.run([str(binary)], check=True)


if __name__ == '__main__':
    main()
