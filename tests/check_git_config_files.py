"""Exercise authored Git patterns with Git itself in an isolated repository."""
from pathlib import Path
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
SHA='adc218676eef25575469234709c2d87185ca223a'


def main():
    with tempfile.TemporaryDirectory() as folder:
        temp=Path(folder);(temp/'lib').mkdir()
        subprocess.run(['git','init','-q',str(temp)],check=True)
        for p in ['.gitattributes','lib/.gitignore']:
            raw=subprocess.check_output(['git','-C',str(ROOT/'linux'),'show',SHA+':'+p])
            (temp/p).write_bytes(raw)
        paths=['a.c','a.h','a.cpp','board.dts','board.dtsi','board.dtso','lib.rs']
        output=subprocess.check_output(['git','-C',str(temp),'check-attr','diff','--',*paths]).decode().splitlines()
        expected=['cpp','cpp','unspecified','dts','dts','dts','rust']
        assert [line.rsplit(': ',1)[1] for line in output]==expected,output
        cases={'lib/crc32table.h':True,'crc32table.h':False,'lib/sub/crc32table.h':False,
               'lib/default.bconf':True,'lib/gen_crc64table':True,'lib/oid_registry_data.c':True,
               'lib/crc32.c':False}
        for name,expected in cases.items():
            result=subprocess.run(['git','-C',str(temp),'check-ignore','--no-index','-q','--',name])
            assert result.returncode in (0,1)
            assert (result.returncode==0)==expected,(name,result.returncode)
    print('PASS: 14 actual Git diff/ignore pattern cases; isolated temporary repository')


if __name__=='__main__':main()
