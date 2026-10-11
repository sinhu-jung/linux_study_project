"""Whole RT mutex API and PI-futex proxy lifecycle."""
ROWS = [dict(
    path='kernel/locking/rtmutex_api.c',
    title='RT mutex API 전체: 일반 획득, PI futex 대리 대기와 RT mutex 연결',
    intro='RT mutex 공개 함수, PI futex의 proxy 획득·정리, 우선순위 조정과 PREEMPT_RT의 일반 mutex API 연결을 구현합니다.',
    principle='실제 우선순위 상속 알고리즘과 API wrapper를 구분합니다. 대리 대기가 오류로 돌아와도 정리 중 소유권을 얻을 수 있어 최종 상태를 확인해야 합니다.',
    use='대리 획득의 시작·대기·정리 반환값을 각각 구분합니다. 이 파일을 읽었다고 포함되는 rtmutex.c의 모든 알고리즘까지 학습 완료로 세지 않습니다.',
    area='우선순위 상속 · futex · 대리 소유권 · RT · 잠금 진단',
    sections=[
        ('전체 구성과 포함 방식', 'GPL-2.0-only, spinlock/export 포함, RT_MUTEX_BUILD_MUTEX 정의 뒤 rtmutex.c를 직접 포함합니다. 이어 chain 한계, 일반 RT API, futex와 proxy API, PI 조정·postunlock·진단, PREEMPT_RT mutex wrapper가 있습니다. 실제 핵심 알고리즘은 포함되는 파일의 helper를 이용하며 두 소스 파일의 학습 범위는 별개입니다.'),
        ('체인 한계와 빠른 경로', 'max_lock_depth는1024로 초기화된 전역 int입니다. 주석은 우선순위 상승 체인 순회 제한을 설명하며 이 파일 자체에 전체 체인 루프가 있지는 않습니다. 디버그나 아키텍처 cmpxchg 지원에 따라 빠른 원자 경로가 사라질 수 있다는 설명도 포함됩니다.'),
        ('RT 공통 획득', '__rt_mutex_lock_common은 might_sleep, mutex_acquire_nest 진단 기록, __rt_mutex_lock 호출 순서입니다. 실패 ret이면 mutex_release로 진단 획득을 되돌립니다. 진단 기록이 실제 잠금 소유권을 주는 것은 아니며 반환값은 핵심 함수에서 옵니다.'),
        ('기본 초기화와 공개 획득', 'rt_mutex_base_init은 __rt_mutex_base_init을 호출하고 일반 export입니다. DEBUG_LOCK_ALLOC이면 nested와 nest_lock wrapper, 아니면 일반 rt_mutex_lock이 TASK_UNINTERRUPTIBLE로 공통 획득을 호출합니다. interruptible/killable은 각각 상태를 바꾸고 성공0, 신호 중단 -EINTR 계약입니다. 이 공개 rt_mutex 획득 계열은 GPL export합니다.'),
        ('trylock과 해제', 'rt_mutex_trylock은 DEBUG_RT_MUTEXES에서 비태스크 문맥이면 경고 후0입니다. 핵심 trylock 성공에만 lockdep 획득을 기록하고 성공1·경합0을 반환합니다. 주석은 태스크 문맥의 atomic region은 가능하지만 hard/soft IRQ 문맥은 안 된다고 구분합니다. unlock은 진단 release 뒤 핵심 unlock을 호출합니다.'),
        ('Futex trylock 분리', 'rt_mutex_futex_trylock은 rt_mutex_slowtrylock, 밑줄 버전은 __rt_mutex_slowtrylock으로 전달합니다. 주석은 futex 변형이 빠른 경로를 사용해서는 안 된다고 명시합니다. 이름이 비슷해도 일반 rt_mutex_trylock으로 바꾸면 동일한 계약이라고 가정할 수 없습니다.'),
        ('Futex 잠금 아래 해제', '__rt_mutex_futex_unlock은 wait_lock 보유를 assert하고 debug unlock을 수행합니다. 대기자가 없으면 owner=NULL 뒤 false, 있으면 mark_wakeup_next_waiter를 호출한 뒤 true입니다. 이 bool은 해제 성공 여부가 아니라 이후 postunlock이 필요한지입니다. 주석은 깨우기 전 역전을 막기 위해 유지한 선점 금지와 postunlock의 짝을 설명합니다.'),
        ('Futex 외부 해제', 'rt_mutex_futex_unlock은 wake queue를 만들고 irqsave wait_lock 아래 내부 해제를 호출합니다. 잠금을 풀고 IRQ를 복원한 뒤 필요한 경우 rt_mutex_postunlock을 호출합니다. 큐 표시와 실제 깨우기를 잠금 밖 단계로 나누며 false인 무대기 경로에도 해제는 이미 이루어졌습니다.'),
        ('RT 객체 초기화', '__rt_mutex_init은 보유 잠금 메모리 재초기화를 검사하고 base 초기화, LD_WAIT_SLEEP lockdep map 초기화를 수행합니다. 잠긴 객체의 재초기화는 문서상 금지입니다. 객체 메모리 할당이나 수명 참조 획득을 대신하는 함수는 아닙니다.'),
        ('Proxy 초기 소유자', 'rt_mutex_init_proxy_locked는 base를 초기화하고 PI futex 전용 static key를 wait_lock class에 지정한 뒤 proxy_owner를 설정합니다. PI 상태가 아직 다른 태스크에 공개되지 않아 경쟁이 없다는 전제이며 자체 외부 직렬화는 하지 않습니다. RT에서 futex hashbucket 잠금과 관련된 lockdep 재귀 오탐을 피하려 별도 class를 둔다는 주석이 있습니다.'),
        ('Proxy 최종 해제', 'rt_mutex_proxy_unlock은 debug proxy unlock과 owner clear만 합니다. 주석은 더 이상 다른 태스크에 보이지 않고 해제될 PI 상태의 정리용이라고 설명합니다. 살아 있는 경쟁 큐를 일반 unlock처럼 처리하거나 호출자 직렬화 없이 사용하는 API가 아닙니다.'),
        ('Proxy 시작 내부 함수', '__rt_mutex_start_proxy_lock은 wait_lock 보유를 요구합니다. 지정 task가 즉시 try_to_take에 성공하면1입니다. 아니면 task_blocks_on_rt_mutex에 FULL_CHAINWALK를 전달해 대기와 교착 검사를 진행합니다. 오류가 났지만 체인 순회 중 owner가 사라졌다면 ret0으로 바꿔 대기 측이 다시 해결하도록 합니다. 반환0은 대기 중,1은 해당 task의 획득,음수는 오류입니다.'),
        ('Proxy 시작 wrapper와 정리 차이', 'rt_mutex_start_proxy_lock은 lock_irq로 내부 함수를 호출하고 ret이0이 아니면 remove_waiter를 실행한 뒤 잠금을 풉니다. 주석은 내부 버전과 달리 실패 대기자를 정리한다고 설명하지만 실제 조건은 음수뿐 아니라 양수1도 포함합니다. 내부 시작은 실패에서 대기자를 제거하지 않으므로 wait 또는 cleanup의 후속 절차가 필요합니다.'),
        ('Proxy 실제 대기', 'rt_mutex_wait_proxy_lock은 wait_lock을 잡고 TASK_INTERRUPTIBLE로 설정한 뒤 rt_mutex_slowlock_block에 waiter와 선택적 hrtimer_sleeper를 전달합니다. 타이머가 있으면 이미 시작되어 있어야 한다는 문서 조건이 있습니다. 이후 fixup_rt_mutex_waiters(lock,true)로 waiter bit를 정리하고 잠금을 풀어 성공0 또는 -EINTR/-ETIMEDOUT을 반환합니다.'),
        ('Proxy cleanup의 역설적 반환', 'rt_mutex_cleanup_proxy_lock은 잠금 아래 무조건 try_to_take_rt_mutex를 시도합니다. 이어 실제 owner가 current가 아니면 remove_waiter하고 cleanup=true, 소유자가 되었다면 false입니다. 마지막에 fixup_rt_mutex_waiters(lock,false)를 실행합니다. false는 정리 실패로 무시할 값이 아니라 획득했으므로 앞선 wait 오류를 버려야 한다는 의미입니다.'),
        ('오류 뒤에도 소유권을 얻는 이유', '대기 함수가 오류로 반환해도 항목이 제거되기 전까지 인계 대상일 수 있습니다. 해제가 owner를 NULL로 둔 중간 상태도 cleanup의 trylock이 처리합니다. timeout 반환 하나만 보고 waiter 메모리를 버리면 큐와 소유권을 잘못 처리할 수 있어 최종 정리 결과를 확인해야 합니다.'),
        ('우선순위 변경 후 PI 재검사', 'rt_mutex_adjust_pi는 task->pi_lock을 irqsave로 잡고 pi_blocked_on을 확인합니다. 대기자가 없거나 waiter tree 정보가 현재 태스크의 정보와 같으면 종료합니다. 아니면 다음 lock을 얻고 잠금을 푼 뒤 get_task_struct로 참조를 확보하여 MIN_CHAINWALK 조정 함수에 넘깁니다. 주석은 그 참조가 체인 함수에서 반납된다고 명시합니다.'),
        ('postunlock과 태스크 종료 진단', 'rt_mutex_postunlock은 rt_mutex_wake_up_q를 호출해 앞서 준비한 깨우기를 수행하며 선점 재활성화 계약과 연결됩니다. DEBUG_RT_MUTEXES의 rt_mutex_debug_task_free는 pi_waiters 트리가 비었는지와 pi_blocked_on이 남았는지 경고합니다. 태스크 메모리를 실제 free하는 함수는 아닙니다.'),
        ('RT 일반 mutex 초기화와 공통 획득', 'PREEMPT_RT 부분의 __mutex_rt_init은 메모리 검사와 lockdep map 초기화만 하며 base 초기화는 공개 헤더의 __mutex_init 매크로와 연결됩니다. __mutex_lock_common은 진단 획득 후 __rt_mutex_lock을 호출하고 실패는 release, 성공은 lock_acquired를 기록합니다. 실제 API 호출 위치 ip를 인자로 받아 진단에 전달합니다.'),
        ('RT 일반 mutex wrapper 전체', 'DEBUG_LOCK_ALLOC이면 nested/nest_lock/interruptible_nested/killable_nested/io_nested가 있고 아니면 일반 lock/interruptible/killable/io가 있습니다. 각각 대응 태스크 상태와 subclass를 전달합니다. IO 변형은 io_schedule_prepare의 token을 받아 공통 획득 후 io_schedule_finish로 마무리합니다. 상태와 회계만 바꾸고 별도 잠금 자료구조를 만들지 않습니다.'),
        ('RT 일반 mutex trylock과 unlock', 'mutex_trylock도 디버그 문맥 확인, 핵심 trylock, 성공 시 진단 기록을 수행합니다. mutex_unlock은 진단 release 뒤 핵심 unlock입니다. 일반 이름의 export와 rt_mutex 이름의 GPL export 등 심볼 공개 정책은 원문의 각 선언에 따릅니다. 이 파일의 RT 구현을 비RT mutex.c의 모든 빠른 경로와 동일하다고 설명하지 않습니다.'),
        ('CS 연결과 검증 범위', '우선순위 상속과 호출 계층, 대리 소유자, 시작·대기·취소의 다단계 프로토콜, 깨우기 지연, lockdep class와 실제 잠금의 분리, 태스크 참조 수명을 학습합니다. 이 수업은 API 파일의 모든 경로를 설명하며 포함된 PI 핵심 알고리즘 전체나 모든 futex 경쟁을 검증한 결과는 아닙니다.')
    ],
    questions=[
        ('proxy 시작의1과 proxy 대기의0은 각각 무엇인가?', '둘 다 각 단계에서의 획득 성공이다', '둘 다 시간 초과이다', 'start는1획득·0대기·음수오류이고 wait는0성공·음수오류입니다. 함수별 반환 규약을 하나로 섞으면 획득 여부를 잘못 판단합니다.'),
        ('proxy wait가 timeout 오류를 반환하면 즉시 waiter를 버려도 되는가?', '아니다. cleanup에서 최종 소유권과 큐 제거를 확인해야 한다', '그렇다. 오류 반환이 항상 모든 대기 정리를 끝낸다', '대기자는 제거되기 전까지 소유권을 받을 수 있습니다. cleanup이 false이면 이미 획득한 것이므로 앞선 wait 오류를 무시해야 합니다.'),
        ('rt_mutex_cleanup_proxy_lock의 false는?', '현재 태스크가 잠금을 획득했다는 의미이다', '정리가 성공했고 잠금을 소유하지 않는다는 의미이다', 'owner가 current가 아닌 경우만 제거 후 cleanup=true입니다. 소유자가 된 경우에는 false로 돌아가 호출자에게 획득 사실을 알립니다.'),
        ('내부 futex unlock의 false는 해제 실패인가?', '아니다. 대기자가 없어 postunlock이 필요 없다는 뜻이다', '그렇다. 다시 unlock해야 한다', '무대기 경로는 owner=NULL로 바꾸고 false입니다. 외부 wrapper는 이 bool로 잠금 밖 깨우기 후처리가 필요한지만 결정합니다.'),
        ('proxy 초기 소유자 설정 함수가 경쟁 접근을 자체 잠금으로 직렬화하는가?', '아니다. 아직 공개되지 않은 PI 상태라는 전제와 호출자 직렬화가 필요하다', '그렇다. 항상 전역 futex lock을 자동 획득한다', '원문은 No locking과 미공개 pi_state 전제를 명시합니다. 일반 경쟁 중 소유자 변경 API처럼 사용할 수 없습니다.'),
        ('RT trylock이 비대기 함수이면 hard IRQ에서도 사용할 수 있는가?', '아니다. 문서는 태스크 문맥만 허용한다', '그렇다. 잠들지 않는 함수는 모두 IRQ 안전하다', 'rt_mutex_trylock 문서는 atomic region과 interrupt context를 구별합니다. DEBUG_RT_MUTEXES에서는 !in_task도 검사합니다.'),
        ('RT 일반 mutex의 IO 획득 wrapper는 무엇을 추가하는가?', 'io_schedule_prepare/finish로 IO 대기 회계를 감싼다', '잠금 획득 대신 디스크 요청을 직접 제출한다', 'token을 보존해 획득 전후 회계 처리를 연결합니다. 실제 획득은 동일한 __mutex_lock_common과 RT mutex core를 사용합니다.')
    ]
)]
