"""Pinned ring arithmetic versus independently walked slots; no concurrency test."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SHA = 'adc218676eef25575469234709c2d87185ca223a'
MAIN = r'''
#include <stdio.h>
static unsigned checks;
#define CHECK(c) do { checks++;if(!(c)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#c);return 1;} }while(0)
int main(void) {
    for(int size=2;size<=256;size*=2)for(int head=0;head<size;head++)for(int tail=0;tail<size;tail++) {
        int count=0,read=0,p=tail;
        while(p!=head){count++;if(p>=tail)read++;p=(p+1)%size;}
        int space=0,write=0;p=head;
        while((p+1)%size!=tail){space++;if(p>=head)write++;p=(p+1)%size;}
        CHECK(CIRC_CNT(head,tail,size)==count);
        CHECK(CIRC_SPACE(head,tail,size)==space);
        CHECK(CIRC_CNT_TO_END(head,tail,size)==read);
        CHECK(CIRC_SPACE_TO_END(head,tail,size)==write);
        CHECK(count+space==size-1);
    }
    int h=2,t=6;
    CHECK(CIRC_CNT_TO_END(h++,t++,8)==2);CHECK(h==3 && t==7);
    h=6;t=2;CHECK(CIRC_SPACE_TO_END(h++,t++,8)==2);CHECK(h==7 && t==3);
    printf("PASS: %u ring arithmetic checks; no synchronization claims\n",checks);
    return 0;
}
'''


def main():
    cc = os.environ.get('CC') or shutil.which('gcc') or shutil.which('clang')
    if not cc:
        raise SystemExit('C compiler required')
    header = subprocess.check_output(['git', '-C', str(ROOT/'linux'), 'show', SHA+':include/linux/circ_buf.h']).decode()
    with tempfile.TemporaryDirectory() as folder:
        source = Path(folder)/'ring.c'
        binary = Path(folder)/('ring.exe' if os.name == 'nt' else 'ring')
        source.write_text(header+'\n'+MAIN, encoding='utf-8')
        subprocess.run([cc, '-std=gnu11', '-Wall', '-Wextra', '-Werror', '-O2', str(source), '-o', str(binary)], check=True)
        subprocess.run([str(binary)], check=True)


if __name__ == '__main__':
    main()
