"""Complete public RT mutex header."""
ROWS = [dict(
    path='include/linux/rtmutex.h',
    title='RT mutex 헤더 전체: 우선순위 대기 트리와 기본 잠금 표현',
    intro='우선순위 상속을 지원하는 수면 잠금의 기본 구조체와 진단 wrapper, 초기화 및 공개 API를 선언합니다.',
    principle='대기자를 cached red-black tree로 관리하는 base와 lockdep 정보를 더한 공개 객체를 분리합니다. 잠김 상태 관측과 소유권 획득은 다릅니다.',
    use='PI 알고리즘의 인터페이스를 읽는 수업입니다. 실제 트리 비교 기준·우선순위 전파·대리 획득은 구현 파일에 있어 이 헤더만으로 검증하지 않습니다.',
    area='우선순위 상속 · 레드블랙 트리 · 잠금 초기화 · 조건부 API',
    sections=[
        ('전체 구성', 'GPL-2.0과 저작권·guard, compiler/linkage/rbtree_types/spinlock_types_raw 포함, max_lock_depth 선언, base 구조체·초기화·관측, 공개 rt_mutex, 전방 선언·진단 hook, 동적·정적 초기화, lockdep별 획득과 일반 API 선언으로 끝납니다.'),
        ('기본 구조체', 'rt_mutex_base는 raw_spinlock_t wait_lock, rb_root_cached waiters, task_struct 포인터 owner를 가집니다. 대기자를 FIFO 리스트가 아니라 우선순위 순서의 트리에 넣고 최상위인 왼쪽 끝을 캐시한다는 주석이 있습니다. 이 헤더 자체에는 비교 함수나 우선순위를 전파하는 루프는 없습니다.'),
        ('기본 초기화와 관측', '__RT_MUTEX_BASE_INITIALIZER는 wait_lock 해제 상태, RB_ROOT_CACHED, ownerNULL을 만듭니다. rt_mutex_base_is_locked는 READ_ONCE(owner)!=NULL만 확인합니다. owner 표현의 내부 표식을 해석하거나 현재 태스크가 소유자인지 검사하지 않습니다. true가 곧 특정 태스크에 대한 소유권 증명인 것은 아닙니다.'),
        ('공개 객체와 문서 필드', 'rt_mutex는 base rtmutex를 포함하고 DEBUG_LOCK_ALLOC이면 dep_map을 추가합니다. 앞의 kernel-doc은 wait_lock/waiters/owner를 설명하지만 현재 표현에서는 그 필드가 base 내부에 있습니다. 문서의 설명과 실제 멤버 접근 경로를 구분합니다. rt_mutex_waiter와 hrtimer_sleeper는 전방 선언만 있습니다.'),
        ('진단과 체인 설정', 'max_lock_depth는 sysctl용 extern int이며 실제 초기값은 API 구현 파일에 있습니다. DEBUG_RT_MUTEXES이면 task-free 진단 함수를 선언하고 아니면 빈 inline입니다. 빈 inline에 전달하는 C 인자 표현의 평가는 빈 전처리 매크로와 같은 의미로 단정하면 안 됩니다. 이 파일에는 태스크 free 구현이 없습니다.'),
        ('동적 초기화 이름', 'rt_mutex_init은 매크로 위치의 static lock_class_key와 __func__를 __rt_mutex_init에 전달합니다. 일반 mutex_init의 문자열화한 인자 이름과 달리 이 매크로의 name은 호출 함수 이름입니다. 진단 이름과 실제 메모리 초기화·잠금 소유권을 혼동하지 않습니다.'),
        ('정적 초기화', 'DEBUG_LOCK_ALLOC이면 dep_map에 문자열화한 mutexname과 LD_WAIT_SLEEP을 추가합니다. __RT_MUTEX_INITIALIZER는 base initializer와 이 조각을 묶고 DEFINE_RT_MUTEX는 구조체를 선언합니다. 설정에 따라 dep_map 멤버가 사라지므로 구조체 크기를 외부 고정 ABI로 가정하지 않습니다.'),
        ('lockdep별 획득', 'DEBUG_LOCK_ALLOC이면 rt_mutex_lock은 subclass0의 nested 호출입니다. nest_lock 변형은 dep_map 형식을 검사하고 _rt_mutex_lock_nest_lock에 전달합니다. 비활성에서는 nested와 nest_lock이 일반 lock으로 바뀌며 부가 인자를 사용하지 않습니다. nested 진단 정보가 동일 잠금의 재귀 획득을 허용하지는 않습니다.'),
        ('남은 공개 API', 'interruptible/killable/trylock은 int, unlock은 void로 선언됩니다. 이 헤더의 해당 선언에는 __must_check 표기가 없지만 실제 실패를 무시해도 안전하다는 뜻은 아닙니다. rtmutex_api.c의 성공·오류 반환 규약을 확인하고 성공한 경우에만 소유권을 행사해야 합니다.'),
        ('CS 연결과 범위', '우선순위 큐용 cached tree, base와 진단 wrapper 분리, 상태 관측, 이름·lock class의 초기화, 조건부 매크로 인터페이스를 학습합니다. 이 파일에 없는 owner 비트 조작이나 PI 체인 전체를 작성 완료로 세지 않습니다.')
    ],
    questions=[
        ('rt_mutex의 대기 자료구조는 단순 FIFO list인가?', '아니다. base 안의 cached red-black tree이다', '그렇다. 항상 도착 순서만으로 선택한다', 'waiters는 rb_root_cached이고 주석은 우선순위 순서와 왼쪽 끝 캐시를 설명합니다. 실제 동률 비교 규칙은 별도 구현을 확인해야 합니다.'),
        ('rt_mutex_init의 진단 name 인자는 무엇인가?', '호출 위치의 __func__이다', '언제나 mutex 인자를 문자열화한 이름이다', '동적 매크로는 __rt_mutex_init(mutex,__func__,&__key)를 호출합니다. 정적 initializer의 #mutexname과 구별합니다.'),
        ('rt_mutex_base_is_locked가 현재 태스크의 소유권까지 확인하는가?', '아니다. owner의 비NULL 여부만 관측한다', '그렇다. owner와 current를 비교한다', '본문에는 READ_ONCE와 NULL 비교만 있습니다. 잠김 관측을 소유권 획득 또는 소유자 일치 확인으로 사용할 수 없습니다.'),
        ('interruptible 선언에 __must_check가 없으면 반환 오류를 무시해도 되는가?', '아니다. annotation과 실제 API 계약은 별개다', '그렇다. annotation 없는 함수는 언제나 획득에 성공한다', '중단 가능한 API는 구현상 실패를 반환할 수 있습니다. 정적 진단 표기가 없다고 실패 후 잠금을 소유한 것처럼 접근해도 되는 것은 아닙니다.')
    ]
)]
