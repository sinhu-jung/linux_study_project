"""Complete mutex debugging implementation."""
ROWS = [dict(
    path='kernel/locking/mutex-debug.c',
    title='Mutex 디버그 구현 전체: 대기자 오염 표식과 수명 검사',
    intro='mutex와 대기자에 진단용 상태를 기록하고 잘못된 사용을 경고하는 구현입니다.',
    principle='자기 주소 magic, 메모리 패턴, task의 blocked_on을 사용해 수명과 연결 상태의 불일치를 드러냅니다. 검사 함수가 실제 잠금 획득·리스트 삽입·메모리 해제를 대신하는 것은 아닙니다.',
    use='mutex 본체와 진단 hook의 책임을 구분하는 데 사용합니다. 경고가 없다는 사실만으로 모든 경쟁이나 교착 상태가 없다고 증명할 수는 없습니다.',
    area='잠금 진단 · 연결 리스트 · 메모리 수명 · 장치 자원 관리',
    sections=[
        ('전체 구성', '기여자·저작권·GPL 설명, mutex/delay/device/export/poison/sched/spinlock/kallsyms/interrupt/debug_locks 및 내부 mutex.h 포함, 대기자 진단 함수 다섯 개, unlock/init 검사, 장치 관리 해제 callback과 등록, mutex_destroy로 구성됩니다. __devm_mutex_init과 mutex_destroy만 이 파일에서 GPL export합니다.'),
        ('대기자 진단 초기화', 'debug_mutex_lock_common은 wait_lock 보유를 전제로 waiter 전체를 MUTEX_DEBUG_INIT 패턴으로 채운 뒤 magic을 자기 주소로, list를 빈 자기 연결로, ww_ctx를 MUTEX_POISON_WW_CTX로 설정합니다. task 등 나머지 실제 동작 필드는 이 함수가 완성하지 않습니다. memset이 유효한 대기자 초기화의 모든 단계를 대체한다고 보면 안 됩니다.'),
        ('깨우기 직전 검사', 'debug_mutex_wake_waiter는 wait_lock 보유를 lockdep_assert_held로 확인하고, mutex 대기 목록이 비었는지, waiter magic이 자기 주소인지, waiter list가 비었는지를 경고 조건으로 검사합니다. 태스크를 실제 깨우거나 큐에서 제거하지 않습니다. 이 불변식들은 호출 위치에서 성립해야 하는 조건입니다.'),
        ('대기자 종료 패턴', 'debug_mutex_free_waiter는 항목이 아직 연결되어 있으면 경고하고 전체를 MUTEX_DEBUG_FREE로 덮습니다. 이름에 free가 있지만 allocator에 메모리를 반환하는 호출은 없습니다. 스택 또는 다른 저장 영역의 대기자 재사용 오류를 드러내는 진단 처리와 물리적 해제를 구별합니다.'),
        ('등록 진단', 'debug_mutex_add_waiter는 wait_lock 보유를 검사하고 task->blocked_on=waiter를 기록합니다. 본문에는 list_add가 없습니다. 실제 큐 연결과 진단용 blocked_on 기록은 서로 다른 단계이며 함수 이름만으로 자료구조 변경 범위를 추정하지 않습니다.'),
        ('제거 진단', 'debug_mutex_remove_waiter는 waiter list가 빈 상태인지, waiter->task가 인자 task와 다른지, task->blocked_on이 waiter와 다른지 검사합니다. 이후 blocked_on=NULL, waiter list 자기 연결 초기화, waiter->task=NULL을 설정합니다. INIT_LIST_HEAD는 이웃 노드를 이어주는 list_del의 대체가 아니므로 실제 목록 연결 수정은 호출 측 절차와 함께 확인해야 합니다.'),
        ('unlock 진단의 정확한 조건', 'debug_locks가 켜져 있으면 lock->magic!=lock을 검사하고 wait_list.prev와 next가 둘 다 NULL인 경우를 경고합니다. 이 조건은 논리 AND이므로 한쪽만 NULL인 모든 손상을 검출하는 포괄적 검사라고 설명하면 안 됩니다. 본문에 소유자 변경이나 spin unlock은 없습니다.'),
        ('mutex 진단 초기화', 'CONFIG_DEBUG_LOCK_ALLOC이면 debug_check_no_locks_freed로 해당 메모리 범위의 보유 잠금 재초기화를 검사하고 lockdep_init_map_wait에 name/key와 LD_WAIT_SLEEP을 전달합니다. 설정과 무관하게 마지막에는 lock->magic=lock을 기록합니다. mutex의 모든 본체 필드를 초기화하는 일반 mutex_init과 역할이 다릅니다.'),
        ('장치 관리 정리 등록', 'devm_mutex_release는 void 포인터를 mutex_destroy에 넘기는 callback입니다. __devm_mutex_init은 devm_add_action_or_reset에 이 callback과 lock을 등록하고 반환값을 그대로 전달합니다. 이 함수 자체에는 mutex_init 호출이 없으며 이름만 보고 mutex 본체 초기화까지 담당한다고 오해하면 안 됩니다. 자원 정리 등록과 실제 잠금 초기화를 구별합니다.'),
        ('destroy의 의미', 'mutex_destroy는 mutex_is_locked이면 경고한 뒤 magic=NULL로 표시합니다. 문서는 호출 시 잠겨 있지 않아야 하고 이후 사용은 금지라고 명시합니다. 잠금을 기다려 해제하거나 대기자를 깨우거나 mutex 메모리를 free하지 않습니다. 경고가 떴다고 함수가 조기 반환하는 코드도 아닙니다.'),
        ('CS 연결과 검증 범위', '오염 패턴, 자기 주소 불변식, 태스크와 대기자 간 교차 참조, 자료구조 조작과 진단의 분리, 조건부 컴파일, 장치 수명과 cleanup callback을 학습합니다. 이 수업은 원문 각 함수의 검사 범위를 설명하며 실제 모든 오용을 실행하여 검출률을 증명한 것은 아닙니다.')
    ],
    questions=[
        ('debug_mutex_free_waiter는 kfree로 대기자 메모리를 해제하는가?', '아니다. 연결 상태를 검사하고 진단 패턴으로 덮는다', '그렇다. 이름이 free이므로 allocator에 반환한다', '함수 본문은 DEBUG_LOCKS_WARN_ON과 memset뿐입니다. 진단용 수명 종료 표시와 실제 저장 영역의 해제를 구분해야 합니다.'),
        ('debug_mutex_add_waiter는 목록에 항목을 삽입하는가?', '아니다. 잠금 보유 확인과 blocked_on 기록을 한다', '그렇다. 내부 list_add_tail로 삽입한다', '이 함수에는 리스트 삽입 호출이 없습니다. 실제 mutex 알고리즘과 진단 hook이 맡는 역할을 따로 추적해야 합니다.'),
        ('unlock 진단이 prev 또는 next 중 하나만 NULL인 경우도 해당 조건으로 검출하는가?', '아니다. 두 포인터가 모두 NULL인지 AND로 검사한다', '그렇다. OR로 어느 한쪽 NULL도 검사한다', '원문 조건은 !prev && !next입니다. 검사 범위를 실제 논리식보다 넓게 설명하면 경고가 없는 상태의 안전성을 과대평가하게 됩니다.'),
        ('잠긴 mutex를 mutex_destroy에 넘기면 자동으로 잠금을 풀어주는가?', '아니다. 경고하고 magic을 NULL로 만든다', '그렇다. 소유자가 해제할 때까지 기다린다', '문서는 잠기지 않은 상태에서 호출할 것을 요구합니다. 함수에 대기·unlock·free가 없으며 경고가 사용 계약을 복구해주지는 않습니다.'),
        ('__devm_mutex_init 본문에서 mutex 본체도 초기화하는가?', '아니다. 장치 관리 cleanup action을 등록한다', '그렇다. mutex_init을 호출한 뒤 등록한다', '본문은 devm_add_action_or_reset 결과를 반환하는 한 호출입니다. 함수 이름과 전체 호출 절차를 혼동하지 말아야 합니다.')
    ]
)]
