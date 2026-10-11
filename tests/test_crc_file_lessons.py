"""Independent bit-at-a-time verification of tables and authored examples."""
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build_file_lessons import load_file_lessons, SHA


def source(path):return subprocess.check_output(['git','-C',str(ROOT/'linux'),'show',SHA+':'+path]).decode()


def table(path,name):
    body=re.search(r'\b'+re.escape(name)+r'\s*\[[^]]*\]\s*=\s*\{(.*?)\}',source(path),re.S).group(1)
    return [int(x,16) for x in re.findall(r'0x[0-9a-fA-F]+',body)]


def shift(value,polynomial,width,count,reflected=False):
    for _ in range(count):
        value=((value>>1)^(polynomial if value&1 else 0)) if reflected else ((value<<1)^(polynomial if value&(1<<(width-1)) else 0))
        value&=(1<<width)-1
    return value


def crc16(data,tab,state=0,reflected=True):
    for b in data:
        state=((state>>8)^tab[(state^b)&255]) if reflected else (((state<<8)^tab[((state>>8)^b)&255])&65535)
    return state


class CRCFileTests(unittest.TestCase):
    def test_every_constant_table_against_polynomial_bit_loop(self):
        cases=[('lib/crc4.c','crc4_tab',7,4,4,False),
               ('lib/crc7.c','crc7_be_syndrome_table',0x12,8,8,False),
               ('lib/crc16.c','crc16_table',0xA001,16,8,True),
               ('lib/crc-ccitt.c','crc_ccitt_table',0x8408,16,8,True),
               ('lib/crc-itu-t.c','crc_itu_t_table',0x1021,16,8,False)]
        for path,name,poly,width,bits,reflected in cases:
            actual=table(path,name)
            expected=[shift(i if reflected or width<=8 else i<<8,poly,width,bits,reflected) for i in range(16 if bits==4 else 256)]
            with self.subTest(path=path):self.assertEqual(actual,expected)

    def test_crc16_worked_examples_and_standard_check_strings(self):
        cases=[('lib/crc16.c','crc16_table',[1,0],0x9001,0xBB3D,True),
               ('lib/crc-ccitt.c','crc_ccitt_table',[1,0x89],0x11,0x2189,True),
               ('lib/crc-itu-t.c','crc_itu_t_table',[1,0x10],0x2100,0x31C3,False)]
        for path,name,data,example,check,reflected in cases:
            tab=table(path,name)
            with self.subTest(path=path):
                self.assertEqual(crc16(data,tab,reflected=reflected),example)
                self.assertEqual(crc16(b'123456789',tab,reflected=reflected),check)
                for split in range(10):
                    first=crc16(b'123456789'[:split],tab,reflected=reflected)
                    self.assertEqual(crc16(b'123456789'[split:],tab,first,reflected),check)
                self.assertEqual(crc16([],tab,0x5678,reflected),0x5678)

    def test_crc4_and_crc7_examples(self):
        tab=table('lib/crc4.c','crc4_tab')
        def crc4(c,x,bits):
            x&=(1<<bits)-1
            for i in range(((bits+3)&~3)-4,-1,-4):c=tab[c^((x>>i)&15)]
            return c
        self.assertEqual(crc4(0,0xAB,8),0xB);self.assertEqual(crc4(0,0xAB,5),8)
        self.assertEqual(crc4(7,0xAB,0),7)
        tab=table('lib/crc7.c','crc7_be_syndrome_table')
        self.assertEqual(tab[tab[1]^1],4)
        self.assertTrue(all(v%2==0 for v in tab))
        c=0
        for b in b'123456789':c=tab[c^b]
        self.assertEqual(c,0xEA)

    def test_crc8_population_against_independent_bit_loop(self):
        # Model the two source population algorithms; oracle is a separate full bit loop.
        for poly in [0x07,0xD5,0xAB]:
            msb=[None]*256;msb[0]=0;t=0x80;i=1
            while i<256:
                t=((t<<1)^(poly if t&0x80 else 0))&255
                for j in range(i):msb[i+j]=msb[j]^t
                i*=2
            self.assertEqual(msb,[shift(i,poly,8,8) for i in range(256)])
            lsb=[None]*256;lsb[0]=0;t=1;i=128
            while i:
                t=(t>>1)^(poly if t&1 else 0)
                for j in range(0,256,2*i):lsb[i+j]=lsb[j]^t
                i>>=1
            self.assertEqual(lsb,[shift(i,poly,8,8,True) for i in range(256)])
        tab=[shift(i,7,8,8) for i in range(256)]
        self.assertEqual(tab[tab[1]^2],0x1B)
        for state in range(256):self.assertEqual(tab[state^(state^255)],tab[255])

    def test_authored_lessons_have_full_pinned_source_and_nonempty_solutions(self):
        lessons=load_file_lessons(ROOT)
        self.assertGreaterEqual(len(lessons),12)
        import hashlib
        for l in lessons:
            raw=source(l['path'])
            self.assertEqual(l['annotated'],raw)
            self.assertEqual(l['source_review']['source_sha256'],hashlib.sha256(raw.encode()).hexdigest())
            self.assertGreaterEqual(len(l['deep_dive']),3)
            self.assertGreaterEqual(len(l['questions']),2)
            for q in l['questions']:
                self.assertTrue(q['explanation'].strip())
                self.assertIn(q['answer'],range(len(q['options'])))


if __name__=='__main__':unittest.main()
