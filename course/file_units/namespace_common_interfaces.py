"""Whole-file namespace common metadata, proc operations and task proxy APIs."""
ROWS = [dict(
    path='include/linux/ns_common.h',
    title='ns_common: 서로 다른 네임스페이스의 공통 객체 인터페이스',
    intro='네 필드의 공통 구조체와 전방 선언이 구체적인 namespace 구현을 어떻게 연결하는지 살펴봅니다.',
    principle='공통 메타데이터를 구체적인 객체 안에 포함하면 C에서도 공통 인터페이스와 타입별 동작을 조합할 수 있습니다.',
    use='구조체 포함, 함수 포인터 테이블, 참조 수와 파일시스템 식별자를 구분합니다.',
    area='C 구조체 포함 · 간접 호출 · 참조 카운팅 · 파일시스템 식별',
    sections=[
        ('헤더 전체와 타입 의존성', 'GPL-2.0 include guard 안에서 linux/refcount.h를 포함하고 proc_ns_operations를 전방 선언합니다. 함수 구현이나 매크로 함수는 없고 ns_common 구조체 하나를 정의합니다. ops가 포인터이므로 여기서 operation 구조체의 전체 필드를 알 필요는 없습니다. 전방 선언과 include 의존성의 차이를 보여 줍니다.'),
        ('Dentry와 operation 포인터', 'stashed는 struct dentry 포인터, ops는 const struct proc_ns_operations 포인터입니다. 교차 확인한 nsfs는 &ns->stashed를 path_from_stashed에 전달하므로 이 필드는 namespace의 파일시스템 경로 연결에 사용됩니다. 이 헤더 자체에는 dentry 생성·해제 코드가 없습니다. const는 ops가 가리키는 테이블에 적용되며 ns_common의 모든 필드가 불변이라는 뜻은 아닙니다.'),
        ('식별자와 수명', 'inum은 unsigned int로 namespace inode 식별자를 보관하고 count는 refcount_t입니다. inum은 메모리 주소도 task PID도 아닙니다. count는 객체 참조 수를 표현하지만 이 헤더에는 증가·감소·마지막 해제 helper가 없습니다. 구체적인 namespace의 get/put이 이를 사용하며 숫자 필드를 선언한 것만으로 소유권 처리가 자동 수행되지는 않습니다.'),
        ('포함 구조체와 검토 범위', '예를 들어 time_namespace는 ns_common ns를 내장하고 공통 callback에 &object->ns를 넘깁니다. 다시 container_of로 구체 객체를 얻는 패턴과 연결됩니다. 이 헤더에 모든 namespace의 전체 데이터나 owner 필드가 모인 것은 아닙니다. 네 필드·포함 관계·선언을 모두 검토했으며 구조체 크기와 padding은 대상 ABI 없이 고정 숫자로 가정하지 않습니다.')
    ],
    questions=[
        ('ns_common의 inum과 count의 역할은?', '파일시스템 식별자와 객체 참조 수', '현재 PID와 CPU 사용 시간', 'inum은 unsigned int, count는 refcount_t입니다. 객체의 식별과 수명 관리는 서로 다른 개념입니다.'),
        ('proc_ns_operations 전체 정의 없이 ops 멤버를 선언할 수 있는 이유는?', '불완전 타입에 대한 포인터이기 때문이다', '컴파일러가 callback 구현을 자동 생성하기 때문이다', '포인터 필드는 대상 구조체의 내부 크기를 요구하지 않습니다. 실제 callback 필드 접근에는 완전한 정의가 필요합니다.'),
        ('이 헤더가 count의 마지막 감소에서 직접 수행하는 해제는?', '없다. 구체적인 get/put 구현에서 관리한다', '모든 namespace 객체를 자동으로 kfree한다', '파일에는 구조체와 선언만 있고 해제 함수 본문은 없습니다. 데이터 표현과 수명 관리 실행 코드를 구분합니다.')
    ]
), dict(
    path='include/linux/proc_ns.h',
    title='proc_ns: namespace 작업 테이블·inode 번호·경로 API',
    intro='공통 callback의 시그니처, 초기 inode 상수, CONFIG_PROC_FS별 helper와 외부 경로 API 전체를 분석합니다.',
    principle='작업 테이블은 타입별 정책을 연결하고 공통 helper는 동일한 저장 형태와 호출 계약을 제공합니다.',
    use='callback 시그니처와 실제 구현을 구분하고 비활성 설정의 반환값을 정확히 읽습니다.',
    area='함수 포인터 · 조건부 컴파일 · inode · callback · 인터페이스 계약',
    sections=[
        ('선언과 테이블의 메타데이터', 'GPL-2.0 guard 안에 ns_common 헤더를 포함하고 pid_namespace·nsset·path·task_struct·inode를 전방 선언합니다. proc_ns_operations의 name과 real_ns_name은 const char 포인터이고 type은 int입니다. 구조체에는 __randomize_layout가 붙어 모든 빌드의 필드 byte offset이 고정이라고 가정할 수 없습니다.'),
        ('다섯 callback의 시그니처', 'get(task)는 ns_common 포인터, put(ns)는 void, install(nsset,ns)는 int, owner(ns)는 user_namespace 포인터, get_parent(ns)는 ns_common 포인터를 반환합니다. install이 받는 준비 상태 nsset과 조회 대상 task가 다른 인수라는 점이 중요합니다. get_parent 포인터 필드가 존재해도 모든 namespace 테이블이 이를 채운다는 보장은 이 선언에 없습니다. 실제 사용 전 지원 여부 처리는 호출부 책임입니다.'),
        ('외부 작업 테이블 목록', 'netns,utsns,ipcns,pidns,pidns_for_children,userns,mntns,cgroupns,timens,timens_for_children의 열 개 const operation 객체를 extern으로 선언합니다. 자식용 PID·시간 namespace가 별도 조회 테이블을 가진다는 점이 드러납니다. 이 헤더의 extern 선언만으로 특정 설정에서 모든 객체 정의가 링크된다고 증명되지는 않습니다.'),
        ('항상 정의되는 초기 inode 번호', '설정 조건 밖 enum에 PROC_ROOT_INO=1, IPC=0xEFFFFFFF, UTS=0xEFFFFFFE, USER=0xEFFFFFFD, PID=0xEFFFFFFC, CGROUP=0xEFFFFFFB, TIME=0xEFFFFFFA가 있습니다. 모두 동적 할당 함수의 반환값 목록이 아니라 초기 객체에 쓰는 상수입니다. 여기에 NET·MNT용 같은 이름의 초기 상수가 정의되어 있다고 추정해서는 안 됩니다.'),
        ('CONFIG_PROC_FS와 stub', 'PROC_FS가 있으면 proc_alloc_inum(unsigned int *)와 proc_free_inum(unsigned int)은 외부 함수입니다. 없으면 alloc이 *inum=1로 쓰고 0을 반환하며 free는 빈 함수입니다. 비활성 stub은 호출마다 고유한 번호를 생성하지 않습니다. 여기서 0은 할당 helper의 성공 상태이고 실제 출력 번호는 1입니다.'),
        ('공통 할당·해제 helper', 'ns_alloc_inum은 WRITE_ONCE(ns->stashed,NULL)를 먼저 수행한 뒤 proc_alloc_inum(&ns->inum)의 결과를 반환합니다. 따라서 번호 할당 실패 가능성과 별개로 stashed 초기화는 먼저 일어납니다. ops와 count는 이 helper에서 초기화하지 않습니다. ns_free_inum 매크로는 (ns)->inum을 proc_free_inum에 넘길 뿐 namespace 메모리나 refcount를 직접 해제하지 않습니다.'),
        ('Inode에서 namespace 얻기', 'get_proc_ns(inode)는 inode->i_private를 struct ns_common 포인터로 cast하는 매크로입니다. namespace 타입 검사, NULL 검사, 참조 수 증가는 없습니다. 이 저장 규약을 지키는 inode에 사용해야 하며 임의 inode를 안전한 namespace 객체로 변환하는 검증 함수는 아닙니다.'),
        ('경로와 callback 타입', 'ns_get_path(path,task,ns_ops)는 task와 operation 테이블로 경로를 얻는 외부 API입니다. ns_get_path_helper_t는 void *를 받고 ns_common *를 반환하는 함수 타입 typedef입니다. ns_get_path_cb의 해당 함수 타입 인수는 C의 함수 매개변수 규칙에 따라 callback 포인터로 사용되고 private_data를 함께 전달합니다. 헤더에는 callback 호출 횟수나 참조 소비의 구현이 없으므로 시그니처만으로 이를 단정하지 않습니다.'),
        ('이름·식별 비교·초기화 선언', 'ns_match(ns,dev,ino)는 bool이며 비교에 device와 inode 두 값을 받습니다. 교차 확인한 nsfs 구현은 ns->inum과 ino뿐 아니라 nsfs superblock의 s_dev도 비교합니다. ns_get_name은 buf,size,task,ns_ops를 받고 int를 반환하고 nsfs_init은 void입니다. 전체 선언과 inline·매크로를 검토했으며 nsfs의 전체 파일 구현을 이 헤더 완료에 포함하지 않습니다.')
    ],
    questions=[
        ('CONFIG_PROC_FS가 없을 때 proc_alloc_inum의 출력과 반환값은?', '*inum=1, 반환 0', '*inum=0, 반환 -ENOSYS', 'stub은 성공 상태 0과 출력 번호 1을 분리합니다. 설정 비활성이라고 모든 API가 오류를 반환하는 것은 아닙니다.'),
        ('ns_alloc_inum이 번호 할당 전에 하는 일은?', 'stashed를 WRITE_ONCE로 NULL 초기화한다', 'count와 ops를 모두 자동 설정한다', '본문은 stashed 초기화와 proc_alloc_inum 호출뿐입니다. 객체 참조 수와 operation 테이블은 별도로 설정해야 합니다.'),
        ('get_proc_ns를 호출하면 참조 수가 증가하는가?', '아니다. i_private를 cast할 뿐이다', '그렇다. 항상 get callback을 호출한다', '매크로에는 callback 호출이나 refcount 연산이 없습니다. 포인터 획득과 수명 보유는 다른 작업입니다.'),
        ('ns_get_path_helper_t는 어떤 callback 타입인가?', 'void *를 받아 struct ns_common *를 반환하는 함수 타입', 'struct path를 값으로 반환하는 정수형 함수 타입', 'typedef는 함수 형태로 쓰여 있고 API의 함수 매개변수에서는 포인터처럼 전달됩니다. 반환 대상은 path가 아니라 namespace 객체입니다.'),
        ('Namespace 식별 비교에 inode 번호만으로 충분하다고 이 API가 말하는가?', '아니다. ns_match는 device 번호도 받는다', '그렇다. dev 인수는 선언에도 없다', '시그니처에 dev_t dev와 ino_t ino가 모두 있으며 확인한 구현도 두 값을 비교합니다. 파일시스템 식별 범위를 고려해야 합니다.')
    ]
), dict(
    path='include/linux/nsproxy.h',
    title='nsproxy: namespace 묶음 공유·설치 상태·접근 규칙',
    intro='task가 공유하는 namespace 포인터 묶음과 nsset, 타입 선택 매크로, 참조 helper를 모두 살펴봅니다.',
    principle='컨테이너 객체의 참조 수와 그 안에 든 개별 객체의 참조 수는 서로 다른 공유 관계를 표현합니다.',
    use='객체 그래프의 수명, 현재 task와 다른 task 접근의 잠금 규칙, 조건부 가변 자격 증명을 학습합니다.',
    area='공유 객체 그래프 · 참조 카운팅 · task 잠금 · C _Generic · scope cleanup',
    sections=[
        ('포함과 구조체 전체', 'GPL-2.0 guard 안에 refcount·spinlock·sched를 포함하고 여러 namespace와 fs_struct를 전방 선언합니다. nsproxy는 refcount_t count와 uts_ns,ipc_ns,mnt_ns,pid_ns_for_children,net_ns,time_ns,time_ns_for_children,cgroup_ns 여덟 포인터를 보관합니다. init_nsproxy는 extern 선언입니다. user namespace 포인터가 이 묶음의 직접 필드로 들어 있다고 가정하면 안 됩니다.'),
        ('공유와 두 종류의 참조 수', '주석은 모든 namespace를 공유하는 task들이 nsproxy도 공유하며 하나의 namespace를 clone하거나 unshare하면 nsproxy를 복사한다고 설명합니다. nsproxy의 count는 이를 보유하는 task 참조를, 각 namespace의 count는 해당 객체를 가리키는 nsproxy 등 보유 참조를 관리합니다. 같은 namespace를 가리키는 필드가 여러 개면 그 보유 관계도 구분해야 합니다. get_nsproxy는 묶음 count만 증가시키므로 호출할 때마다 여덟 namespace를 전부 get하는 함수가 아닙니다.'),
        ('자식용 PID와 시간 포인터', '주석은 현재 활성 PID namespace를 task_active_pid_ns로 얻으며 이 구조체에는 자식용 PID namespace를 보관한다고 명시합니다. 시간은 time_ns와 time_ns_for_children을 둘 다 보관합니다. 포인터 이름에서 현재 실행 문맥과 향후 자식의 설정을 구분해야 합니다. 이 헤더가 fork 시 실제 포인터 교체를 구현하는 것은 아닙니다.'),
        ('컴파일 시 타입 선택', 'to_ns_common은 C _Generic으로 cgroup,ipc,net,pid,mnt,time,user,uts namespace 포인터 여덟 타입에 대해 &(__ns->ns)를 선택합니다. runtime type tag를 검사하는 switch가 아닙니다. default 항목이 없으므로 목록 밖의 포인터 타입을 임의로 받아들이는 API가 아닙니다. 호출 지점에는 대상 구조체의 ns 멤버를 해석할 수 있는 정의가 필요하며 const-qualified 대상 포인터 등을 자동으로 폭넓게 지원한다고 가정하지 않습니다.'),
        ('설치 준비 상태 nsset', 'nsset은 unsigned flags, nsproxy 포인터, fs_struct 포인터, const cred 포인터를 묶습니다. 부분적이거나 완전한 namespace 집합 설치에 필요한 상태입니다. 주석은 새 user namespace 요청일 때 cred가 수정 가능한 자격 증명을 가리키며 가변 포인터가 필요하면 nsset_cred를 사용하고 결과를 검사하라고 설명합니다. 구조체 필드가 const이므로 모든 경우에 무조건 cast해서 수정하는 계약은 아닙니다.'),
        ('nsset_cred의 정확한 조건', 'nsset_cred는 flags&CLONE_NEWUSER이면 (struct cred *)set->cred를 반환하고 아니면 NULL입니다. 함수 내부에 새 cred 할당, 복사, 참조 수 증가, CAP 검사, set->cred NULL 검사는 없습니다. 조건에 맞게 준비된 nsset이라는 계약을 사용하며 반환 결과를 검사해야 합니다. CLONE_NEWTIME만 있는 요청은 이 helper에서 가변 cred를 받는 조건이 아닙니다.'),
        ('접근 규칙: 현재 task와 변경', '주석상 tsk->nsproxy 또는 그 안의 포인터 변경은 current task만 허용하며 tsk->nsproxy를 바꿀 때 task_lock이 필요합니다. 현재 task의 namespace를 읽는 경우에는 포인터를 직접 따라갈 수 있다고 설명합니다. 이것을 namespace 객체의 모든 내부 필드가 무잠금 수정 가능하다는 의미로 확대하지 않습니다. 내부 객체 데이터는 별도 동기화 규칙을 가질 수 있습니다.'),
        ('다른 task의 namespace 접근', '주석의 패턴은 task_lock(task), nsproxy=task->nsproxy, NULL이 아니면 필요한 namespace 사용 또는 참조 획득, task_unlock 순서입니다. NULL은 종료에 가까운 task 상태일 수 있습니다. 포인터를 얻은 뒤 lock 밖에서 계속 사용하려면 해당 객체의 수명 보유 계약을 지켜야 합니다. 읽기라는 이유로 다른 task의 nsproxy를 잠금 없이 임의 접근하는 패턴과 다릅니다.'),
        ('외부 수명·전환 API 전체', 'copy_namespaces(flags,tsk)는 int, exit_task_namespaces(tsk)와 switch_task_namespaces(tsk,new)는 void, exec_task_namespaces(void)는 int입니다. free_nsproxy(ns)는 void이고 unshare_nsproxy_namespaces는 flags,nsproxy 이중 포인터,cred,fs를 받아 int를 반환합니다. nsproxy_cache_init은 __init int 선언입니다. 실제 복사 순서·오류 코드·객체별 해제는 이 헤더 밖 구현에 있습니다.'),
        ('참조 helper와 자동 정리 정의', 'put_nsproxy는 refcount_dec_and_test가 true일 때 free_nsproxy를 호출하고 get_nsproxy는 refcount_inc를 수행하며 반환형은 void입니다. 두 helper 자체에는 NULL 검사가 없습니다. 마지막 DEFINE_FREE(put_nsproxy,struct nsproxy *,if (_T) put_nsproxy(_T))는 cleanup 용도의 동작을 정의하며 그 동작은 NULL을 건너뜁니다. 이 정의만으로 모든 nsproxy 지역 변수에 자동 cleanup이 붙는 것은 아닙니다. 호출부에서 해당 cleanup 방식을 사용해야 합니다.'),
        ('검토 범위와 예제', '두 task가 하나의 nsproxy를 함께 보유하다 한 task가 다른 namespace 집합을 준비하면 묶음의 공유 관계와 개별 namespace 재사용 관계를 따로 추적해야 합니다. 이 파일의 구조체 두 개, 타입 선택 매크로, 외부 선언, inline helper, cleanup 정의와 접근 규칙을 모두 검토했습니다. 실제 clone·unshare·setns 실행이나 모든 경합 상황을 테스트한 결과는 아닙니다.')
    ],
    questions=[
        ('nsproxy의 PID 포인터가 나타내는 namespace는?', '자식들이 사용할 PID namespace', '항상 현재 task의 활성 PID namespace', '주석은 현재 활성 PID namespace를 task_active_pid_ns로 얻는 예외를 명시합니다. 필드 이름도 pid_ns_for_children입니다.'),
        ('get_nsproxy가 직접 증가시키는 참조 수는?', 'nsproxy 묶음의 count 하나', '여덟 namespace 객체 각각의 count', '본문에는 refcount_inc(&ns->count)만 있습니다. 묶음 참조 증가와 내부 객체를 새 묶음에 연결하는 절차를 구분합니다.'),
        ('to_ns_common은 언제 대상 타입을 선택하는가?', '컴파일 시 _Generic으로 선택한다', '실행 시 namespace 이름 문자열을 비교한다', '타입 association 목록으로 선택하며 default도 없습니다. 문자열이나 runtime type 태그를 읽는 동작이 아닙니다.'),
        ('CLONE_NEWTIME만 있는 nsset의 nsset_cred 반환은?', 'NULL', '무조건 수정 가능한 cred 포인터', '검사하는 비트는 CLONE_NEWUSER입니다. 새 시간 namespace와 새 user namespace 요청은 서로 다릅니다.'),
        ('다른 task의 nsproxy를 읽는 주석상 절차는?', 'task_lock 아래 NULL을 검사하고 필요하면 참조를 획득한다', '읽기이므로 아무 잠금 없이 포인터만 저장한다', '다른 task는 종료 등으로 상태가 바뀔 수 있습니다. 현재 task 읽기 규칙을 다른 task에도 그대로 적용해서는 안 됩니다.'),
        ('put_nsproxy 자체와 DEFINE_FREE의 NULL 처리 차이는?', 'helper 자체는 NULL 검사 없이 사용하고 cleanup 동작은 NULL을 건너뛴다', '둘 다 반드시 NULL 역참조를 수행한다', 'inline 함수에는 검사 없이 ns->count를 읽지만 DEFINE_FREE 본문에는 if (_T)가 있습니다. wrapper와 내부 helper 계약이 다릅니다.')
    ]
)]
