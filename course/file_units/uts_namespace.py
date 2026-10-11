"""Whole-file UTS ABI, kernel interface and namespace lifecycle."""
ROWS = [dict(
    path='include/uapi/linux/utsname.h', title='UTS 사용자 구조체: 세 세대의 고정 길이 문자열 ABI',
    intro='oldold·old·new utsname 구조체의 모든 필드와 배열 길이를 비교합니다.',
    principle='이전 ABI 구조체를 유지하면서 새 구조체를 별도로 정의하면 기존 사용자 프로그램의 메모리 배치를 보존할 수 있습니다.',
    use='고정 길이 배열, 문자열 종료 공간, 필드 추가와 ABI 호환성을 학습합니다.',
    area='C 배열 · 문자열 · 사용자 ABI · 호환성',
    sections=[
        ('전체 구성', 'GPL-2.0 WITH Linux-syscall-note guard 안에 길이 상수 두 개와 구조체 세 개가 있습니다. 외부 include, 함수, 할당이나 문자열 복사 구현은 없습니다. 이 파일은 사용자 공간과 공유하는 데이터 배치를 선언합니다.'),
        ('가장 오래된 구조체', '__OLD_UTS_LEN은 8이며 oldold_utsname은 sysname,nodename,release,version,machine 다섯 char[9] 필드를 둡니다. 배열 선언에는 상수 이름 대신 9가 직접 쓰입니다. 8글자와 종료 문자 공간을 표현할 수 있지만 선언 자체가 NUL을 써 주지는 않습니다.'),
        ('이전 확장 구조체', '__NEW_UTS_LEN은 64이고 old_utsname은 같은 다섯 필드를 char[65]로 둡니다. old라는 이름이 가장 짧은 9바이트 필드 구조체를 뜻하는 것은 아닙니다. char 배열만 있으므로 일반 Linux C ABI에서 두 구형 구조체의 크기는 각각 45,325바이트입니다.'),
        ('현재 구조체와 domainname', 'new_utsname은 같은 다섯 필드에 domainname을 추가하고 모든 배열 길이를 __NEW_UTS_LEN+1로 표현합니다. 여섯 개의 65바이트 배열이므로 크기는 390바이트입니다. nodename과 domainname은 별도 필드이며 이 선언이 DNS 설정이나 네트워크 주소를 자동 변경하지 않습니다. 숫자 포인터나 가변 길이 배열 대신 값 자체를 담습니다.'),
        ('검토 범위', '상수와 세 구조체의 전체 필드·순서·길이를 확인했습니다. 각 syscall이 어떤 구조체를 얼마나 복사하는지, 호환 아키텍처가 값을 어떻게 수정하는지는 별도 구현의 책임입니다. 구조체 선언만으로 사용자 문자열의 실제 길이와 종료 상태를 보장한다고 설명하지 않습니다.')
    ], questions=[
        ('old_utsname과 new_utsname의 필드 차이는?', 'new에 domainname이 추가된다', 'new에서 machine이 삭제된다', '기존 다섯 필드를 유지하고 여섯 번째 domainname을 둡니다. 배열은 모두 65바이트입니다.'),
        ('new_utsname의 배열 총 크기는?', '390바이트', '384바이트', '문자열 공간은 64만이 아니라 종료 공간을 포함한 65입니다. 6×65=390입니다.'),
        ('char[65] 선언만으로 64번째 뒤 NUL이 자동 기록되는가?', '아니다. 실제 초기화·복사 코드의 책임이다', '그렇다. C의 char 배열은 항상 자동 종료된다', '배열 크기는 저장 공간을 제공할 뿐 문자열 내용을 자동으로 만들지 않습니다.')
    ]
), dict(
    path='include/linux/utsname.h', title='UTS 커널 헤더: namespace 구조·참조 helper·설정별 stub',
    intro='UTS 객체의 데이터와 소유권, 현재 namespace 접근, 설정에 따른 API 동작을 모두 분석합니다.',
    principle='포인터를 얻는 helper와 객체 수명을 보유하는 helper, 데이터 잠금은 서로 다른 책임입니다.',
    use='refcount, 조건부 컴파일, 내부 구조체와 사용자 ABI 구조체의 차이를 이해합니다.',
    area='객체 수명 · 조건부 컴파일 · namespace · 참조 카운팅',
    sections=[
        ('포함과 proc 항목 enum', 'GPL-2.0 guard 안에서 sched,nsproxy,ns_common,err,UAPI utsname을 포함합니다. uts_proc enum은 ARCH,OSTYPE,OSRELEASE,VERSION,HOSTNAME,DOMAINNAME 순서로 0부터 시작합니다. 이는 new_utsname의 필드 메모리 순서와 같은 목록이 아니므로 enum 숫자를 구조체 offset처럼 쓰면 안 됩니다.'),
        ('UTS 객체 전체', 'uts_namespace는 new_utsname name, owner user_ns, 자원 회계 ucounts, 공통 ns_common ns를 보관하고 __randomize_layout가 붙습니다. init_user_ns와 init_uts_ns는 extern입니다. name만이 사용자 ABI 데이터이며 owner·참조 수까지 사용자 uname 결과로 복사하는 구조가 아닙니다.'),
        ('활성 설정의 수명 API', 'CONFIG_UTS_NS일 때 get_uts_ns는 count를 증가시키고 void를 반환합니다. put_uts_ns는 감소 결과가 0이면 free_uts_ns를 호출합니다. copy_utsname,free_uts_ns,uts_ns_init의 구현은 외부 선언입니다. get/put에는 NULL 검사가 없고 refcount가 name 필드의 동시 수정 자체를 잠그는 것은 아닙니다.'),
        ('비활성 설정', 'UTS_NS가 없으면 get/put/init은 빈 함수입니다. copy_utsname은 CLONE_NEWUTS가 있으면 ERR_PTR(-EINVAL), 없으면 old_ns를 그대로 반환합니다. 이 경우 참조를 증가시키지 않으며 없는 격리 기능을 성공으로 가장하지 않습니다. 다른 flag가 있다는 이유만으로 여기서 모두 거부하는 코드는 아닙니다.'),
        ('Sysctl 통지 설정', 'CONFIG_PROC_SYSCTL이면 uts_proc_notify(enum uts_proc)를 extern 선언하고 아니면 빈 inline을 제공합니다. UTS_NS와 PROC_SYSCTL은 서로 다른 조건부 구역입니다. 통지 함수의 존재와 namespace 복제 지원을 같은 설정으로 혼동하지 않습니다.'),
        ('현재 값과 초기 값 접근', 'utsname()은 &current->nsproxy->uts_ns->name, init_utsname()은 &init_uts_ns.name을 반환합니다. 복사본을 할당하거나 get_uts_ns를 호출하지 않고 내부 포인터를 제공합니다. 마지막 uts_sem은 rw_semaphore extern 선언이며 getter 자체가 그 잠금을 잡지는 않습니다. 이름 데이터의 읽기·쓰기 동기화는 실제 호출 문맥에서 확인해야 합니다.')
    ], questions=[
        ('UTS_NS가 없을 때 CLONE_NEWUTS를 요청하면?', 'ERR_PTR(-EINVAL)', '항상 init_uts_ns를 새 객체처럼 반환', '비활성 stub도 요청 flag를 검사합니다. 지원하지 않는 새 격리를 명시적으로 거부합니다.'),
        ('utsname()은 namespace 참조 수를 증가시키는가?', '아니다. 현재 객체의 name 주소를 반환한다', '그렇다. get_uts_ns를 호출한다', '본문에는 주소 계산만 있습니다. 포인터 접근과 수명 획득을 구분합니다.'),
        ('UTS_PROC_ARCH=0은 name의 첫 필드가 machine임을 뜻하는가?', '아니다. enum과 구조체 배치는 별개다', '그렇다. enum은 byte offset이다', 'UAPI 구조체 첫 필드는 sysname입니다. proc 항목 분류값을 메모리 배치로 해석하면 안 됩니다.'),
        ('put_uts_ns에서 마지막 참조를 놓을 때 호출하는 함수는?', 'free_uts_ns', 'uts_proc_notify', '활성 구현은 refcount_dec_and_test가 true일 때 해제 함수를 호출합니다. sysctl 통지와 수명 관리는 다릅니다.')
    ]
), dict(
    path='kernel/utsname.c', title='UTS namespace 구현: 복제·소유권·이름 복사 잠금',
    intro='모든 함수와 operation 테이블, slab 초기화 및 실패 경로를 분석합니다.',
    principle='복제는 기존 값을 일관되게 읽고 새 객체의 회계·식별자·참조를 준비하는 여러 단계로 구성됩니다.',
    use='자원 획득의 역순 정리, read semaphore, 참조를 먼저 얻는 교체 순서를 학습합니다.',
    area='namespace · slab · refcount · rwsem · 오류 포인터 · 자원 회계',
    sections=[
        ('전체 구성과 cache', 'GPL-2.0-only 파일은 export,uts,utsname,err,slab,cred,user namespace,proc namespace,task 헤더를 포함합니다. uts_ns_cache 포인터는 __ro_after_init입니다. create_uts_ns는 cache에서 GFP_KERNEL로 객체를 할당하고 성공 시 ns.count만 1로 설정합니다. 객체 전체를 0으로 만드는 할당이 아닙니다.'),
        ('개수 회계와 복제 시작', 'inc_uts_namespaces는 owner user namespace,current_euid(),UCOUNT_UTS_NAMESPACES를 inc_ucount에 전달하고 dec helper는 같은 종류를 감소시킵니다. clone_uts_ns는 회계 획득 실패를 -ENOSPC, 객체 할당 실패를 -ENOMEM으로 처리합니다. 이어 ns_alloc_inum 오류를 그대로 보존합니다. 함수 위 주석의 ENOMEM 설명만 보고 모든 실패가 같은 오류라고 단정하면 안 됩니다.'),
        ('성공 설정과 이름 복사', 'inum 준비가 성공하면 ucounts와 ops=&utsns_operations를 지정합니다. down_read(&uts_sem) 아래 old_ns->name 전체를 memcpy하고 owner user_ns를 get_user_ns로 보유한 뒤 up_read합니다. 여기서 전체 new_utsname을 복사하므로 nodename 하나만 복제하는 것이 아닙니다. 이름을 읽는 쪽이므로 read 잠금을 쓰며 이 파일에는 hostname 변경 syscall 본문이 없습니다.'),
        ('실패 자원 회수', 'inum 할당 실패는 cache 객체를 해제한 뒤 회계 감소, 객체 할당 실패는 회계 감소만 수행합니다. 회계 획득 실패는 곧바로 ERR_PTR(err)입니다. owner 참조는 실패 가능한 준비 단계가 끝난 후 얻으므로 이 실패 라벨에 put_user_ns가 없습니다. 아직 얻지 않은 자원을 반환하지 않는 순서입니다.'),
        ('공유와 복제의 임시 참조', 'copy_utsname은 BUG_ON(!old_ns) 후 먼저 get_uts_ns(old_ns)를 합니다. NEWUTS가 없으면 증가한 참조와 함께 같은 객체를 반환합니다. 있으면 clone_uts_ns를 호출하고 성공·실패 모두 old_ns를 put한 뒤 결과를 반환합니다. clone 실패가 기존 namespace 보유 참조를 임의로 잃게 만드는 구조가 아니라 이 함수에서 추가한 임시 참조를 균형 있게 놓습니다.'),
        ('해제와 공통 객체 변환', 'free_uts_ns는 개수 회계 감소, owner put, inode 번호 해제, slab 반환 순서입니다. count 감소 자체는 header의 put helper 책임입니다. to_uts_ns는 container_of로 ns_common에서 바깥 객체를 얻습니다. 공통 객체를 별도 할당하거나 데이터 복사로 변환하지 않습니다.'),
        ('Task에서 참조 얻기', 'utsns_get은 task_lock 아래 task->nsproxy를 확인하고 있으면 uts_ns를 선택해 get한 뒤 unlock합니다. 결과는 &ns->ns 또는 NULL입니다. get이 잠금 안에 있어 task의 포인터를 읽는 시점과 객체 수명 획득을 연결합니다. utsns_put은 역변환 후 put_uts_ns에 위임합니다.'),
        ('설치 권한과 교체 순서', 'utsns_install은 대상 owner와 nsset->cred->user_ns 양쪽에서 CAP_SYS_ADMIN을 검사하고 하나라도 없으면 -EPERM입니다. 통과하면 새 ns를 먼저 get하고 준비 proxy의 옛 uts_ns를 put한 뒤 포인터를 대입합니다. 같은 객체를 다시 설치하는 경우에도 먼저 얻는 순서가 중요합니다. 이 함수는 nsset의 준비 상태를 바꾸며 current의 전체 proxy를 직접 전환하지 않습니다.'),
        ('Owner와 operation 테이블', 'utsns_owner는 owner 포인터를 반환합니다. utsns_operations는 name=uts,type=CLONE_NEWUTS와 get,put,install,owner를 연결합니다. real_ns_name과 get_parent는 명시 초기화하지 않아 NULL입니다. 이 테이블에 parent callback이 있다고 가정하면 nsfs PARENT ioctl 분석도 틀려집니다.'),
        ('Usercopy cache 초기화', 'uts_ns_init은 kmem_cache_create_usercopy에 객체 전체 크기, align=0, SLAB_PANIC|SLAB_ACCOUNT를 전달합니다. 사용자 복사 허용 구역은 offsetof(uts_namespace,name)에서 sizeof_field(...,name)만큼이며 마지막 ctor는 NULL입니다. 객체 전체가 사용자 복사 데이터라고 선언하지 않습니다. offsetof를 사용하므로 구조체 배치 randomization 문맥에서도 name의 실제 위치로 구역을 지정합니다.'),
        ('검토 범위', '회계·할당·복제·copy·free·공통 변환·get/put/install/owner·작업 테이블·초기화를 모두 원본과 대조했습니다. 이름 데이터의 동시 접근 잠금과 객체 수명의 refcount, 사용자별 namespace 회계는 별도의 메커니즘입니다. 실제 UTS clone·setns·할당 실패 주입을 실행 검증한 것은 아닙니다.')
    ], questions=[
        ('clone_uts_ns에서 namespace 개수 회계 획득 실패 오류는?', '-ENOSPC', '항상 -ENOMEM', 'err는 처음 -ENOSPC이며 회계 획득 뒤에 -ENOMEM으로 바뀝니다. 주석보다 실제 분기와 대입을 확인해야 합니다.'),
        ('UTS 복제에서 memcpy 보호에 쓰는 잠금은?', 'uts_sem의 read 잠금', 'uts_sem의 write 잠금', '이 함수는 기존 이름을 읽어 새 객체로 복사하므로 down_read/up_read를 사용합니다.'),
        ('copy_utsname에서 NEWUTS가 없는 경우 반환은?', '참조를 하나 늘린 기존 객체', '매번 새로 할당한 독립 객체', 'get_uts_ns는 flag 검사보다 먼저 실행됩니다. 공유 경로는 그 참조를 반환 계약으로 넘깁니다.'),
        ('새 namespace를 설치할 때 get과 옛 put의 순서는?', '새 참조 획득 후 옛 참조 해제', '옛 참조 해제 후 새 객체를 검사 없이 사용', '같은 객체를 다시 설치할 가능성도 고려하면 먼저 수명을 보유하는 순서가 중요합니다.'),
        ('UTS cache의 usercopy 허용 구역은?', 'name 필드 구역', 'user_ns와 ucounts를 포함한 객체 전체', 'offset과 길이를 name 필드로 지정합니다. 사용자 ABI 데이터와 커널의 소유권 메타데이터를 구분합니다.'),
        ('utsns_operations가 get_parent를 제공하는가?', '아니다. 명시되지 않아 NULL이다', '그렇다. 항상 init_uts_ns를 반환한다', '테이블은 get,put,install,owner만 연결합니다. 실제 제공하지 않는 계층 API를 추정해서는 안 됩니다.')
    ]
)]
