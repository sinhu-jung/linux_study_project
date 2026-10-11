"""Whole-file UTS sysctl handler and default name macros."""
ROWS = [dict(
    path='kernel/utsname_sysctl.c', title='UTS sysctl: namespace 필드 재배치·임시 버퍼·변경 통지',
    intro='여섯 sysctl 항목과 문자열 handler의 읽기·쓰기·잠금·통지 경로 전체를 분석합니다.',
    principle='공유 데이터를 잠금 아래 복사하고 잠금 밖에서 처리하면 긴 잠금을 줄일 수 있지만 읽기부터 쓰기까지의 원자성은 별도 문제입니다.',
    use='필드 offset, 지역 복사본, 부분 쓰기의 경합과 operation 결과 처리 순서를 학습합니다.',
    area='sysctl · namespace · rwsem · 부분 쓰기 · 버퍼 · poll 통지',
    sections=[
        ('전체 구성과 설정 분기', 'GPL-2.0-only 파일은 export·uts·utsname·random·sysctl·wait·rwsem을 포함합니다. CONFIG_PROC_SYSCTL이면 get_uts와 proc_do_uts_string을 구현하고 아니면 proc_do_uts_string을 NULL 매크로로 둡니다. 항목 테이블과 poll 객체, 등록 함수는 이 조건 밖에 있습니다. 설정이 없을 때 파일 전체가 전처리로 사라지는 것은 아닙니다.'),
        ('현재 namespace 필드 주소 계산', 'get_uts는 table->data를 char 포인터로 보고 init_uts_ns의 시작 주소를 빼 필드 byte offset을 얻습니다. 그 offset을 current->nsproxy->uts_ns 시작 주소에 더합니다. 테이블은 초기 객체 필드를 기준점으로 쓰지만 실제 접근 대상은 현재 task의 UTS 객체입니다. hard-coded 숫자 offset이 아니며 동일 구조체 안의 필드를 가리킨다는 테이블 계약에 의존합니다.'),
        ('지역 ctl_table과 65바이트 버퍼', 'proc_do_uts_string은 원본 ctl_table 전체를 지역 uts_table에 memcpy하고 data만 char tmp_data[__NEW_UTS_LEN+1]로 바꿉니다. 원본 테이블의 data 포인터를 현재 task별로 직접 수정하지 않습니다. 길이·모드 등 나머지 설정을 복사한 채 기존 문자열 handler를 재사용하는 방식입니다.'),
        ('읽기와 쓰기 모두 기존 값 복사', 'down_read(&uts_sem) 아래 현재 namespace 필드의 65바이트를 tmp_data로 복사하고 up_read합니다. write 요청에서도 이 읽기를 생략하지 않습니다. 주석은 부분 쓰기를 지원하려면 기존 값이 필요하다고 설명합니다. 이후 proc_dostring을 잠금 없이 호출해 반환값 r을 저장합니다. 사용자 입력 처리 전체 동안 uts_sem을 잡고 있지 않습니다.'),
        ('쓰기 후속 처리와 반환 순서', 'write가 참이면 add_device_randomness(tmp_data,sizeof(tmp_data))를 호출하고, write 잠금 아래 65바이트 전체를 현재 필드로 다시 복사한 뒤 unlock하고 proc_sys_poll_notify(table->poll)를 호출합니다. 조건은 write뿐이며 r==0인지 별도 검사하지 않습니다. 마지막에 r을 반환하므로 proc_dostring 오류가 있다고 후속 복사·통지가 항상 생략된다고 설명하면 안 됩니다. randomness 호출 자체를 특정 엔트로피 비트 수 보장으로 확대하지 않습니다.'),
        ('부분 쓰기 경합', '주석은 read와 write 잠금 사이에 잠금을 놓기 때문에 같은 sysctl의 0이 아닌 offset에 두 writer가 병렬 쓰기하면 결과가 부정확할 수 있다고 명시합니다. 두 writer가 같은 이전 문자열을 복사하고 각자 수정한 전체 버퍼를 다시 쓰면 앞선 변경이 뒤의 복사에 덮일 수 있습니다. write 잠금은 각 복사 구간을 보호하지만 전체 읽기-수정-쓰기 절차를 하나의 원자적 동작으로 만들지는 않습니다.'),
        ('여섯 테이블 항목과 순서', 'uts_kern_table은 arch→machine, ostype→sysname, osrelease→release, version→version, hostname→nodename, domainname→domainname 순서입니다. 각 data는 init_uts_ns.name의 해당 배열이고 maxlen은 그 배열 sizeof입니다. 앞 네 항목은 mode=0444, 뒤 두 항목은 0644이며 모두 같은 handler를 사용합니다. 주석은 enum uts_proc를 테이블 변경과 함께 맞추라고 요구합니다.'),
        ('Poll 객체와 외부 통지', 'hostname_poll과 domainname_poll을 static DEFINE_CTL_TABLE_POLL로 정의하고 해당 두 항목만 poll 포인터를 지정합니다. CONFIG_PROC_SYSCTL의 uts_proc_notify는 enum proc를 배열 index로 바로 사용한 뒤 poll notify를 호출합니다. 이 함수 안에는 enum 범위 검사나 문자열 이름 검색이 없습니다. 호출자는 올바른 항목을 지정해야 합니다. 이 파일의 poll 객체가 namespace마다 별도 할당된다고 추정하지 않습니다.'),
        ('등록과 검토 범위', '__init utsname_sysctl_init은 register_sysctl("kernel",uts_kern_table)을 호출하고 반환값을 검사하지 않은 채 0을 반환합니다. device_initcall로 등록합니다. 여섯 항목·두 설정 분기·전체 helper·등록을 대조했습니다. 실제 사용자 권한 판정의 세부 정책과 proc_dostring의 문자열 파싱은 다른 구현에 있으며 이 자료는 실제 sysctl 경합 실행 결과를 측정한 것은 아닙니다.')
    ], questions=[
        ('테이블 data가 init_uts_ns를 가리키면 모든 task가 초기 이름만 접근하는가?', '아니다. 필드 offset을 현재 UTS 객체에 적용한다', '그렇다. namespace는 이 handler에서 무시된다', 'get_uts는 초기 객체 기준의 상대 주소를 현재 객체 기준 주소로 옮깁니다. 테이블의 기준점과 실제 접근 대상을 구분합니다.'),
        ('write 요청도 기존 문자열을 먼저 읽는 이유는?', '부분 쓰기를 위해 변경하지 않는 부분을 보존하려고', 'write일 때는 문자열 handler를 호출하지 않으려고', '기존 값을 tmp_data에 복사한 뒤 proc_dostring이 그 복사본을 처리합니다. read와 write 모두 이 단계가 있습니다.'),
        ('proc_dostring이 오류를 반환하면 write 후속 처리는 무조건 생략되는가?', '아니다. 후속 분기는 r이 아니라 write만 검사한다', '그렇다. if (r==0) 조건이 있다', '실제 소스는 if (write)입니다. 오류 반환과 부작용 유무를 같은 것으로 단정하지 않습니다.'),
        ('write 잠금이 있어도 두 부분 쓰기의 변경이 덮일 수 있는 이유는?', '처음 읽은 뒤 최종 쓰기까지 잠금이 계속 유지되지 않기 때문이다', 'rwsem은 쓰기 잠금을 전혀 제공하지 않기 때문이다', '각 복사 구간은 보호하지만 그 사이 지역 버퍼를 처리합니다. 전체 read-modify-write의 원자성과 개별 임계 구역 보호는 다릅니다.'),
        ('uts_proc_notify가 항목을 찾는 방식은?', 'enum 값을 테이블 index로 직접 사용한다', 'procname 문자열을 해시 검색한다', '범위 검사 없이 uts_kern_table[proc]를 사용하므로 enum과 테이블 순서를 맞춰야 합니다.'),
        ('hostname과 앞 네 읽기 전용 항목의 mode 차이는?', 'hostname은 0644, 앞 네 항목은 0444', '모두 0777', '테이블에는 hostname·domainname만 0644와 poll 포인터를 지정합니다. 실제 접근 판정 전체를 mode 숫자만으로 확대하지 않습니다.')
    ]
), dict(
    path='include/linux/uts.h', title='UTS 초기 이름 매크로: 기본값과 전처리 재정의',
    intro='uname 계열 이름의 세 기본 매크로와 각 ifndef 조건을 분석합니다.',
    principle='컴파일 시 기본값을 정의하는 헤더와 실행 중 namespace 데이터를 바꾸는 함수는 역할이 다릅니다.',
    use='전처리 fallback, 설정 값 참조, 문자열 초기값을 구분합니다.',
    area='전처리 · 빌드 설정 · 문자열 초기값',
    sections=[
        ('헤더 전체', 'GPL-2.0 include guard 안에 주석과 세 조건부 매크로 정의만 있습니다. 함수·객체·외부 include가 없으며 uname이 반환할 값의 기본 정의라는 주석이 있습니다. release·version·machine에 대한 기본값은 여기서 정의하지 않습니다.'),
        ('세 기본값과 독립 조건', 'UTS_SYSNAME이 미정의이면 문자열 Linux, UTS_NODENAME이 미정의이면 CONFIG_DEFAULT_HOSTNAME, UTS_DOMAINNAME이 미정의이면 문자열 (none)을 정의합니다. 세 #ifndef는 각각 독립적이어서 이미 정의된 항목은 보존하고 나머지만 기본값을 공급합니다. UTS_NODENAME은 CONFIG_DEFAULT_HOSTNAME이라는 글자 자체를 따옴표로 저장하는 정의가 아닙니다.'),
        ('초기값과 실행 중 변경', 'nodename과 domainname 옆 주석은 각각 sethostname·setdomainname으로 설정됨을 설명합니다. 이 매크로 헤더가 시스템 호출을 실행하거나 현재 namespace 이름을 직접 수정하지는 않습니다. 실행 중 바뀌는 것은 UTS 객체의 데이터이고 전처리 매크로는 빌드 시 토큰 치환입니다. 세 정의와 guard 전체를 검토했습니다.')
    ], questions=[
        ('UTS_NODENAME의 기본 정의는?', 'CONFIG_DEFAULT_HOSTNAME', '항상 문자열 localhost', '헤더는 빌드 설정 매크로를 참조합니다. 그 설정의 실제 값은 이 파일에 고정되어 있지 않습니다.'),
        ('UTS_SYSNAME이 이미 정의되어 있으면?', '그 값을 유지하고 이 기본 정의를 건너뛴다', '무조건 Linux로 덮는다', '#ifndef 조건이 있어 기본값을 제공할 뿐 선행 정의를 덮지 않습니다. 다른 두 매크로 조건과도 독립적입니다.')
    ]
)]
