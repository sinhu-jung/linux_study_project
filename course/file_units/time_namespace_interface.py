"""Whole-file time namespace structures, helpers and disabled stubs."""
ROWS = [dict(
    path='include/linux/time_namespace.h',
    title='시간 네임스페이스 인터페이스: offset·참조 수·설정별 stub',
    intro='시간 네임스페이스의 상태 구조체, 변환 helper, 수명 관리와 CONFIG_TIME_NS 분기 전체를 분석합니다.',
    principle='동일한 헤더 API라도 설정이 꺼졌을 때 반환 계약이 함수마다 다르므로 stub을 개별적으로 읽어야 합니다.',
    use='부호 있는 시간 보정, namespace 소유권, refcount와 identity 변환을 학습합니다.',
    area='네임스페이스 · 참조 카운팅 · 시간 표현 · 조건부 컴파일 · API 계약',
    sections=[
        ('헤더와 외부 타입', 'GPL-2.0 include guard 안에서 sched·nsproxy·ns_common·err·time64를 포함합니다. user_namespace와 vm_area_struct를 전방 선언하고 init_user_ns와 init_time_ns를 extern으로 선언합니다. 헤더의 extern은 객체를 할당하거나 namespace를 초기화하는 구현이 아닙니다.'),
        ('시간 보정 데이터', 'timens_offsets에는 timespec64 monotonic과 boottime 두 필드가 있습니다. realtime offset 필드는 없습니다. 각 값은 초·나노초 표현이며 보정 대상 시계별 값을 분리합니다. 이 구조만 보고 임의 clockid를 모두 같은 보정으로 처리할 수 있다고 가정하지 않습니다.'),
        ('Namespace 객체의 상태', 'time_namespace는 user_ns, ucounts, ns_common ns, offsets, vvar_page, frozen_offsets를 보관합니다. 주석상 frozen_offsets가 설정되면 어떤 task가 참여한 뒤 offset 변경을 막습니다. 실제 변경 거부 로직은 이 헤더에 없습니다. __randomize_layout가 붙으므로 선언만으로 모든 빌드의 고정 byte offset을 가정하지 않습니다. vvar_page는 사용자 공간 주소가 아니라 struct page 포인터입니다.'),
        ('수명과 생성 API', 'TIME_NS가 있으면 get_time_ns는 ns->ns.count를 refcount_inc한 뒤 같은 ns를 반환합니다. put_time_ns는 refcount_dec_and_test가 true일 때만 free_time_ns를 호출합니다. copy_time_ns는 flags,user_ns,old_ns를 받는 외부 함수이며 실제 공유·복제 정책은 여기서 정의하지 않습니다. NULL 인수를 허용하는 검사도 get/put의 활성 구현에는 없습니다. 참조 수는 객체 수명을 관리하며 offsets 필드의 모든 동시 접근을 잠그는 mutex가 아닙니다.'),
        ('참여와 VVAR 선언', 'vdso_join_timens(task,ns)는 int, timens_commit(tsk,ns)는 void이고 timens_on_fork(nsproxy,tsk), find_timens_vvar_page(vma)도 선언합니다. 이는 VVAR 매핑과 task namespace 상태를 연결하는 구현의 접점입니다. 이 헤더에는 namespace 전환 순서나 fault 처리를 직접 구현한 본문이 없습니다.'),
        ('Proc 인터페이스', 'proc_timens_show_offsets는 task와 seq_file을 받습니다. proc_timens_offset은 int clockid와 timespec64 val로 한 설정 요청을 표현하고 proc_timens_set_offset은 file,task,offset 배열 포인터와 개수 n을 받아 int를 반환합니다. 이 선언만으로 권한 검사나 허용 clockid 검사가 끝났다고 말할 수 없습니다. 두 API와 요청 구조체는 TIME_NS 활성 구역에 있습니다.'),
        ('현재 task의 보정 더하기', 'timens_add_monotonic과 timens_add_boottime은 current->nsproxy->time_ns->offsets를 찾아 해당 offset을 timespec64_add로 더하고 *ts에 대입합니다. 입력 포인터의 값을 제자리 변경하며 별도 결과 객체를 반환하지 않습니다. 주어진 임의 namespace가 아니라 현재 task의 namespace를 사용합니다. 이 함수들에는 init_time_ns를 별도로 검사하는 분기가 없습니다.'),
        ('Boottime의 두 추가 변환', 'timens_add_boottime_ns는 u64 nsec에 timespec64_to_ns(boottime offset)를 더해 u64로 반환합니다. timens_sub_boottime은 timespec64_sub로 *ts에서 offset을 뺍니다. 별도의 overflow·underflow·포화 검사는 없습니다. ns 함수의 입력과 반환이 unsigned이므로 부호 있는 offset과 결합하는 C 산술 및 호출 계약을 고려해야 하며 음수 offset을 무조건 0으로 자른다고 설명해서는 안 됩니다.'),
        ('Ktime를 host 시간으로', 'do_timens_ktime_to_host(clockid,tim,offsets)는 외부 구현 선언입니다. inline timens_ktime_to_host는 현재 namespace가 &init_time_ns와 같은 주소이면 tim을 그대로 반환합니다. 아니면 clockid,tim,&ns->offsets를 외부 함수로 전달합니다. 어느 clockid에 어떤 offset을 적용하는지는 외부 구현의 책임이며 이 wrapper가 자체 switch로 결정하지 않습니다.'),
        ('설정 비활성: 생성과 참조 계약', 'TIME_NS가 없을 때 copy_time_ns는 flags에 CLONE_NEWTIME이 있으면 ERR_PTR(-EINVAL), 없으면 old_ns를 반환합니다. get_time_ns는 입력을 그대로 반환하지 않고 NULL을 반환하며 put_time_ns는 아무 작업도 하지 않습니다. 따라서 모든 비활성 stub을 identity 함수라고 묶을 수 없습니다. ERR_PTR은 오류를 포인터 반환형에 담은 값이며 실제 namespace 객체 주소가 아닙니다.'),
        ('설정 비활성: 참여·조회·산술', 'vdso_join_timens는 0을 반환하고 timens_commit과 timens_on_fork는 작업하지 않습니다. find_timens_vvar_page는 NULL입니다. timespec 포인터를 받는 add_monotonic·add_boottime·sub_boottime은 값을 변경하지 않으며 add_boottime_ns는 nsec, timens_ktime_to_host는 tim을 그대로 반환합니다. 비활성 구역에는 free_time_ns·proc API·do_timens_ktime_to_host의 같은 형태 stub이 따로 제공되지 않습니다.'),
        ('설정 바깥 선언과 검토 범위', '마지막 arch_get_vdso_data(void *vvar_page) 선언은 CONFIG_TIME_NS 조건 밖에 있습니다. 조건 밖에 선언이 있다는 사실만으로 모든 빌드에 동일 구현과 호출이 존재한다고 증명되지는 않습니다. 전체 타입·외부 선언·inline 활성 함수·비활성 stub을 검토했으며 실제 namespace 생성, 권한 검사, offset의 허용 범위는 이 헤더 밖 구현을 추가로 읽어야 합니다.')
    ],
    questions=[
        ('timens_offsets가 직접 보관하는 두 보정값은?', 'monotonic과 boottime', 'realtime과 CPU 사용 시간', '구조체의 실제 멤버는 timespec64 monotonic, boottime입니다. 존재하지 않는 realtime 필드를 추정해서는 안 됩니다.'),
        ('TIME_NS 활성 상태에서 put_time_ns가 free_time_ns를 부르는 조건은?', '참조 수를 감소시킨 결과 0이 되었을 때', '호출될 때마다 무조건', 'refcount_dec_and_test의 true일 때만 해제합니다. 다른 사용자가 보유한 참조가 있으면 객체를 유지합니다.'),
        ('timens_add_monotonic은 어느 namespace의 값을 쓰는가?', 'current task의 nsproxy가 가리키는 time namespace', '호출 인수로 받은 별도 namespace', '인수는 timespec64 포인터 하나입니다. namespace는 current->nsproxy->time_ns에서 얻습니다.'),
        ('TIME_NS 비활성에서 get_time_ns(ns)의 반환은?', 'NULL', '항상 입력 ns', '활성 구현은 참조 증가 후 ns를 반환하지만 비활성 stub은 NULL입니다. 함수 이름만 보고 공통 반환을 가정하지 않습니다.'),
        ('TIME_NS 비활성에서 CLONE_NEWTIME 요청의 copy_time_ns 반환은?', 'ERR_PTR(-EINVAL)', 'old_ns와 구별되지 않는 성공 반환', '새 시간 namespace 생성 요청은 지원되지 않음을 포인터 오류값으로 알립니다. 해당 flag가 없는 경우에만 old_ns를 반환합니다.'),
        ('timens_ktime_to_host가 활성 설정에서 즉시 tim을 반환하는 조건은?', '현재 namespace가 init_time_ns 객체일 때', 'clockid가 음수일 때', 'wrapper의 직접 조건은 객체 주소 비교입니다. clockid별 처리는 비초기 namespace에서 호출하는 외부 함수에 위임됩니다.'),
        ('frozen_offsets 멤버를 선언한 것만으로 이 헤더가 offset 변경을 거부하는가?', '아니다. 제한 의도는 주석에 있고 강제 구현은 다른 곳에 있다', '그렇다. bool 선언이 모든 대입을 자동으로 차단한다', '일반 bool 필드에는 접근 제한 동작이 없습니다. 상태 표현과 실제 검증 코드를 구분해야 합니다.')
    ]
)]
