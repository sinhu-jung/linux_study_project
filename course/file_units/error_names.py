"""Whole symbolic error lookup, configuration stub and internal errno header."""
ROWS = []


def add(path, title, intro, principle, use, sections, questions):
    ROWS.append(dict(path=path, title=title, intro=intro, principle=principle,
                     use=use, area='오류 코드 · 희소 배열·설정별 인터페이스',
                     sections=sections, questions=questions))


add('lib/errname.c', '오류 이름 변환 전체: 희소 테이블과 부호 없는 문자열 재사용',
    '숫자 오류 코드를 EIO 또는 -EIO 같은 상징 이름으로 바꿉니다.',
    '정적 문자열은 모두 -로 시작합니다. 절댓값으로 테이블을 조회하고 양수 입력이면 문자열 시작을 한 글자 옮겨 부호를 생략합니다. 알려지지 않은 값은 NULL입니다.',
    '사람이 읽는 자연어 오류 설명이나 지역화된 strerror를 대신하는 함수는 아닙니다. 반환 문자열은 정적 저장소이며 호출자가 수정·해제할 메모리가 아닙니다.',
    [('파일 전체', 'SPDX,build_bug/errno/errname/kernel/math 헤더,두 번 정의·해제하는 E 매크로,두 이름 테이블,별칭 static_assert,내부 __errname,공개 errname과 export로 구성됩니다. 동적 할당이나 문자열 복사는 없습니다.'),
     ('낮은 번호 희소 배열', 'E(err)는 지정 초기화 인덱스를 err로 두고 문자열 "-" #err를 만듭니다. BUILD_BUG_ON_ZERO는0 이하 또는300 초과 번호가 들어오면 컴파일 오류를 유도합니다. 인덱스 사이의 빈 슬롯은 NULL입니다. 배열 길이는 마지막 명시 인덱스에 의해 결정되므로 오류 번호 분포가 메모리 사용량에 영향을 줍니다.'),
     ('별칭과 조건부 항목', 'EAGAIN이 EWOULDBLOCK의 대표 이름입니다. EDEADLOCK 번호가 EDEADLK와 다를 때만 별도 항목을 만듭니다. EINIT,EPROCLIM,EREMDEV,ERREMOTE는 정의된 환경에서만 추가합니다. EREFUSED/ECANCELLED 별칭은 해당 환경에서 static_assert로 대표 번호와 같은지 확인합니다. 이름이 여러 개여도 같은 번호에서 원래 사용한 토큰을 복원할 수는 없습니다.'),
     ('큰 번호의 공간 절약', 'MIPS에서는 EDQUOT를 낮은 배열에서 빼고 조회 함수의 특수 분기로 -EDQUOT를 반환합니다. 원문 주석의 번호1133 때문에 배열 전체를 그 크기까지 늘리는 낭비를 피하는 방식입니다. 나머지 아키텍처 번호를 asm-generic과 항상 같다고 가정하면 안 됩니다.'),
     ('내부 오류 구간', 'names_512는512를 뺀 상대 인덱스로512..550 범위를 검사하며 restart/probe/NFS/비동기 오류18개 이름을 저장합니다. include/linux/errno.h에 정의된 모든 이름을 반드시 포함하는 것은 아닙니다. 예를 들어ENOGRACE531은 이 표에 없으므로 현재 구현에서 NULL입니다.'),
     ('조회 순서와 반환', '__errname은 먼저 names_0 범위를 검사하고,그 다음512 이상에서 names_512의 상대 범위를 검사하며,MIPS EDQUOT 예외 뒤 NULL을 반환합니다. errname은 abs(err)의 결과를 넘기고 양수면name+1,음수면name을 반환합니다.0은 빈 슬롯이라NULL입니다. INT_MIN처럼 signed 절댓값을 표현할 수 없는 임의 입력의 안전성을 보장하는 범용 정수 변환으로 쓰지 않습니다.'),
     ('CS 연결', '지정 초기화,희소 배열의 공간 비용,구간별 테이블,문자열 리터럴 공유,컴파일 시 불변식,입력 토큰과 값의 정보 손실을 연결합니다. 일반 이름 표와 아키텍처 분기를 구분해 검증해야 하며 asm-generic 기반 실행만으로 MIPS·parisc 실행까지 검증했다고 말할 수 없습니다.')],
    [('errname(EIO)와 errname(-EIO)의 문자열 차이는?', '각각 EIO와 -EIO이며 같은 정적 문자열의 시작 위치를 다르게 쓴다', '두 호출이 별도 동적 문자열을 할당한다', '테이블에는 -EIO가 있고 양수이면name+1을 반환합니다. 별도 복사나 해제가 필요하지 않습니다.'),
     ('EWOULDBLOCK 번호로 원래 토큰 이름을 항상 복원할 수 있는가?', '없다. EAGAIN과 같은 번호여서 대표 이름이 나온다', '있다. 정수에 원래 매크로 철자가 저장된다', '전처리 후 같은 정수값에는 어느 별칭을 사용했는지 정보가 없습니다. 표는 EAGAIN을 대표로 저장합니다.'),
     ('ENOGRACE가 errno.h에 있으면 errname도 반드시 이름을 반환하는가?', '아니다. 고정 버전 이름 테이블에는 없어서 NULL이다', '그렇다. 모든 define을 런타임에 자동 검색한다', '테이블은 명시적으로 작성됩니다. 선언의 존재와 조회표 포함은 별개의 조건입니다.'),
     ('MIPS EDQUOT를 따로 처리하는 이유는?', '큰 희소 인덱스로 배열이 불필요하게 커지는 것을 피하기 위해서다', '문자열을 암호화해야 하기 때문이다', '원문은 EDQUOT1133을 특수 분기로 처리합니다. 직접 인덱스 조회의 공간 비용을 제한하는 설계입니다.')])

add('include/linux/errname.h', '오류 이름 헤더 전체: 설정 비활성화의 NULL 대체 구현',
    '호출 코드를 유지하면서 선택 기능을 제외하는 컴파일 시 인터페이스입니다.',
    'CONFIG_SYMBOLIC_ERRNAME이 정의되어 있으면 외부 errname 선언을 제공하고,없으면 항상 NULL을 반환하는 static inline 함수를 정의합니다.',
    '호출자는 알려진 번호라도 NULL을 처리해야 합니다. 기능 비활성화와 이름 없는 번호가 동일한 반환 표현을 사용합니다.',
    [('전체 파일', 'SPDX,guard,linux/stddef.h include,#ifdef 선언 또는 인라인 본문,#endif로 구성됩니다. stddef는 NULL 사용과 연결됩니다. 이름 테이블은 이 헤더에 없습니다.'),
     ('설정 분기', '활성 분기는 const char* errname(int err) 외부 선언입니다. 비활성 분기는 인자를 조회하지 않고 NULL을 반환합니다. 숫자 오류 코드를 변경하거나 오류 처리를 성공으로 바꾸는 기능은 아닙니다.'),
     ('호출자 설계', '반환형 const char*는 문자열을 수정하지 않는 사용 계약을 나타냅니다. NULL일 때 숫자를 표시하는 등 호출자가 대체 표현을 선택할 수 있습니다. 선택적 진단 기능과 실제 오류의 의미를 분리하는 예입니다.')],
    [('기능이 꺼져 있을 때 errname(EIO)는?', 'NULL', '항상 EIO 문자열', '인라인 대체 구현은 어떤 번호에도NULL을 반환합니다. 알려진 번호라는 사실만으로 문자열 존재를 가정하면 안 됩니다.'),
     ('비활성 대체 함수가 입력 오류 자체를 없애는가?', '아니다. 이름 조회만 제공하지 않는다', '그렇다. 모든 오류를 성공 코드로 변환한다', '반환값은 오류 처리 결과가 아니라 문자열 포인터입니다. 진단 표현과 프로그램 오류 제어를 구분합니다.')])

add('include/linux/errno.h', '커널 내부 오류 헤더 전체: 재시작·드라이버·NFS 상태',
    '사용자 공간 오류 번호를 포함하고 커널 내부 제어용 오류를 덧붙입니다.',
    'uapi/linux/errno.h를 포함한 뒤512..519와521..531의 내부 상수를 정의합니다.520은 이 파일에서 정의하지 않습니다.',
    '일반 사용자 공간에 그대로 남길 오류와 커널 내부에서 재시도·완료를 제어하는 값을 구분합니다. 이 헤더는 상수 선언이며 재시작이나 재시도를 직접 실행하지 않습니다.',
    [('전체 구조와 재시작 주석', 'SPDX,guard,UAPI include,내부 코드 설명,상수19개,#endif가 전부입니다. 주석은 ERESTART*를 반환하려면 signal_pending이 설정되어야 하고 ptrace가 syscall exit에서 관찰할 수 있으나 최종 사용자 프로세스에 그대로 남기지 않는다고 설명합니다.'),
     ('512부터519', 'ERESTARTSYS512,ERESTARTNOINTR513,ERESTARTNOHAND514,ENOIOCTLCMD515,ERESTART_RESTARTBLOCK516,EPROBE_DEFER517,EOPENSTALE518,ENOPARAM519입니다. 이름이 모두 같은 재시작 조건을 뜻하지 않습니다.516은 sys_restart_syscall 경유 재시작,517은 드라이버 probe 재시도 요청,518은 stale dentry 발견 등 서로 다른 경로의 신호입니다.'),
     ('521부터531', 'EBADHANDLE,ENOTSYNC,EBADCOOKIE,ENOTSUPP,ETOOSMALL,ESERVERFAULT,EBADTYPE,EJUKEBOX,EIOCBQUEUED,ERECALLCONFLICT,ENOGRACE가 차례로521..531입니다. NFS 핸들·동기화·cookie·지원 여부·버퍼·서버 오류부터 비동기 완료 대기와 회수 충돌·락 reclaim 거절까지 구분합니다. EIOCBQUEUED는 이후 완료 이벤트를 받는 상태라는 주석이 있습니다.'),
     ('유사 이름과 계층', '내부 ENOTSUPP524와 UAPI 계열 EOPNOTSUPP를 무조건 같은 번호로 간주하지 않습니다. 이 파일은 아키텍처 UAPI 번호를 재정의하지 않고 포함합니다. 코드값 정의,사용처의 제어 흐름,사용자 공간 노출 규약,errname 문자열 표는 각각 별도로 확인해야 합니다.')],
    [('EPROBE_DEFER를 define하는 것만으로 재시도가 실행되는가?', '아니다. 상수를 해석하는 드라이버 경로가 별도로 필요하다', '그렇다. 전처리 define이 스케줄러를 호출한다', '헤더에는 숫자 정의만 있습니다. 요청의 의미를 실제 동작으로 연결하는 코드는 사용처에 있습니다.'),
     ('이 파일의 내부 번호512..531은 빈틈 없이 연속인가?', '아니다.520은 정의하지 않는다', '그렇다. 모든 번호에 상수가 있다', '512..519와521..531 두 묶음입니다. 숫자 구간을 보고 자동으로 의미를 만들어내면 안 됩니다.'),
     ('내부 ENOTSUPP를 EOPNOTSUPP와 항상 같은 값으로 취급해도 되는가?', '안 된다. 서로 다른 선언과 사용 계층을 확인해야 한다', '된다. 철자가 비슷하면 같은 오류 번호다', '이 헤더는 ENOTSUPP524를 명시합니다. 다른 계층의 비슷한 이름과 숫자·의미를 혼동하지 않습니다.')])
