"""Whole counting semaphore interface and implementation."""
ROWS = []


def add(path, title, intro, principle, use, sections, questions):
    ROWS.append(dict(path=path, title=title, intro=intro, principle=principle,
                     use=use, area='세마포어 · 동기화 · 대기 큐 · 스케줄링',
                     sections=sections, questions=questions))


add('include/linux/semaphore.h', '세마포어 헤더 전체: 자원 수와 소유자 없는 반납',
    '계수형 세마포어의 구조체, 초기화와 획득·반납 함수 선언을 제공합니다.',
    '남은 획득 가능 수와 대기 목록을 raw spinlock으로 보호합니다. mutex와 달리 특정 소유자에게 반납 권한을 묶지 않습니다.',
    '멤버에 직접 접근하지 않고 API를 사용합니다. 이진 세마포어도 mutex와 같은 소유자 규칙이나 진단 기능을 갖는 것은 아닙니다.',
    [('전체 구성', 'GPL-2.0-only와 저작권, 구현 파일 안내, guard, list/spinlock 포함, semaphore 구조체, 초기화 매크로, sema_init, 여섯 외부 함수 선언과 endif가 있습니다. wait 동작과 반환값 상세는 kernel/locking/semaphore.c를 가리킵니다.'),
     ('자료구조', 'raw_spinlock_t lock, unsigned int count, list_head wait_list를 저장합니다. owner 태스크 필드는 없습니다. 주석은 직접 멤버를 접근하지 말라고 명시하며 count를 단순 읽고 별도로 줄이는 방식은 API의 원자적 획득을 대체하지 못합니다.'),
     ('초기화', '__SEMAPHORE_INITIALIZER(name,n)은 unlocked raw lock, count n, 빈 wait_list를 만듭니다. DEFINE_SEMAPHORE는 이름과 초기 수 두 인자를 받습니다. sema_init은 int val로 구조체 전체를 초기화한 뒤 static key를 이용해 lockdep map을 설정합니다. 값 검증이나 사용 중인 대기자 정리는 하지 않으므로 살아 있는 큐를 임의로 재초기화하지 않습니다.'),
     ('반납 주체와 실행 문맥', '주석은 다른 스레드에서도 up할 수 있고 down_trylock과 up은 인터럽트 문맥에서 사용할 수 있다고 설명합니다. 이 성질을 잠들 수 있는 모든 down 변형의 IRQ 안전성으로 확대하면 안 됩니다. 객체 메모리는 호출과 대기 동안 유효해야 합니다.'),
     ('함수 선언과 결과', 'down과 up은 void이며 interruptible/killable/trylock/timeout은 __must_check int입니다. timeout의 시간은 long jiffies 인자로 받습니다. 같은 int여도 trylock은 실패1, 중단 가능 함수는 음수 오류처럼 계약이 다르므로 단일 성공 판정 방식으로 묶기 전에 구현 문서를 확인해야 합니다.'),
     ('CS 연결', '자원 계수와 소유자 추적의 차이, 침입형 대기 목록, 초기화 불변식, 반환값 검사를 통한 소유권 획득 확인을 학습합니다. count1로 만들었다는 사실만으로 mutex의 모든 의미와 동일해지지는 않습니다.')],
    [('이진 세마포어의 up은 down한 스레드만 호출할 수 있는가?', '아니다. 소유자 개념이 없어 다른 스레드나 인터럽트에서도 가능하다', '그렇다. 구조체에 owner가 저장되어 검사한다', '헤더는 owner 필드를 두지 않으며 이진 세마포어도 mutex와 다르다고 명시합니다. 다만 사용자가 정한 자원 수와 수명 계약은 지켜야 합니다.'),
     ('sema_init이 현재 대기자들을 안전하게 깨우고 재사용을 준비하는가?', '아니다. 구조체를 초기화할 뿐 기존 대기 정리를 하지 않는다', '그렇다. 초기화 안에 전체 깨우기가 있다', 'sema_init은 초기화식 대입과 lockdep 설정만 수행합니다. 사용 중 객체를 초기화하면 기존 대기 목록과 동기화 상태를 잃을 수 있습니다.')])

add('kernel/locking/semaphore.c', '세마포어 구현 전체: 직접 인계와 중단 가능한 자원 획득',
    '자원이 남으면 즉시 감소시키고, 없으면 큐에서 기다리다가 반납자가 특정 대기자에게 직접 인계하는 계수형 세마포어입니다.',
    '대기자가 있을 때 up은 공개 count를 늘리지 않고 첫 대기자의 up 플래그를 설정합니다. 타임아웃·신호와 인계의 승패는 잠금 아래 상태 확인 순서로 정해집니다.',
    '획득 성공은0, 신호 중단은 -EINTR, 시간 초과는 -ETIME입니다. completion의 반환 규약과 혼동하지 않고 실제로 획득한 경우에만 해당 자원을 사용합니다.',
    [('전체 구성', 'GPL-2.0-only·저작권·설계 주석, compiler/kernel/export/sched/debug/semaphore/spinlock/ftrace/lock trace 포함, 느린 경로 전방 선언, 여섯 public API와 export, waiter 구조체, 공통 대기와 trace wrapper, 상태별 noinline 함수와 __up으로 끝납니다. 느린 경로를 분리해 빠른 획득 코드를 짧게 유지합니다.'),
     ('공통 상태와 IRQ', 'lock은 count와 wait_list를 보호하며 count는 앞으로 즉시 획득할 수 있는 수입니다.0이면 대기자가 있을 수도 있지만0이라는 사실 자체가 대기자 수는 아닙니다. trylock과 up의 IRQ 호출 때문에 irqsave를 사용하며 주석은 성공이 확실한 down의 역사적 호출도 언급합니다. 잠들 수 있는 경로에는 might_sleep이 있으므로 일반적인 IRQ 대기 허용으로 읽지 않습니다.'),
     ('기본 획득', 'down은 might_sleep 후 irqsave 잠금 아래 count>0이면 감소하고 아니면 __down으로 갑니다. 원문은 down 사용을 deprecated로 표시하고 interruptible 또는 killable을 권합니다. __down은 TASK_UNINTERRUPTIBLE과 MAX_SCHEDULE_TIMEOUT을 쓰므로 일반 신호로 기다림을 중단하지 않습니다.'),
     ('중단 가능한 획득', 'down_interruptible과 down_killable도 count가 남으면 즉시 감소하고0입니다. 없는 경우 각각 TASK_INTERRUPTIBLE, TASK_KILLABLE로 대기해 신호 또는 치명적 신호 중단 시 -EINTR입니다. 빠른 성공 경로는 pending signal을 먼저 검사하지 않으므로 신호가 있다는 이유만으로 모든 호출이 실패하는 것은 아닙니다.'),
     ('비대기 획득의 반환 반전', 'down_trylock은 잠금 아래 count-1을 int 지역변수에 계산하고 음수가 아니면 count를 갱신합니다. 반환은 count<0이므로 성공0, 실패1입니다. spin_trylock/mutex_trylock의 성공 true와 반대라는 경고가 있습니다. 여기에는 참조 계수 같은 포화 방어가 없고 임의의 거대한 초기값이나 잘못된 반납을 허용하는 검증 API가 아닙니다.'),
     ('시간 제한 획득', 'down_timeout은 먼저 count를 확인하므로 자원이 즉시 있으면 timeout이0이어도 획득할 수 있습니다. 자원이 없으면 TASK_UNINTERRUPTIBLE로 지정 jiffies 동안 기다리고 만료는 -ETIME입니다. 성공0은 완료 대기의 timeout 성공 양수와 다른 계약입니다.'),
     ('반납과 인계 분기', 'up은 irqsave 잠금 아래 wait_list가 비었으면 count를1 늘립니다. 대기자가 있으면 __up으로 가서 첫 항목을 제거하고 waiter.up=true, wake_up_process를 수행합니다. 이 경우 count를 늘리지 않으므로 대기자에게 준 몫을 새 호출자가 공개 count에서 가로채는 구조가 아닙니다.'),
     ('지역 waiter', 'semaphore_waiter는 list, task, bool up을 가지며 공통 대기의 스택에 존재합니다. 큐 꼬리에 붙이고 current와 false를 기록합니다. 이 객체를 깨우는 쪽이 접근하므로 함수 반환 전에 성공 인계 또는 실패 정리로 목록에서 반드시 빠져야 합니다.'),
     ('수면 반복', '___down_common은 잠금을 보유한 채 시작해 signal_pending_state, timeout<=0 순서로 검사합니다. 계속 기다리면 태스크 상태를 바꾸고 unlock_irq 후 schedule_timeout, lock_irq 후 waiter.up을 확인합니다. up이면 즉시0으로 성공합니다. 깨웠지만 아직 인계되지 않았다면 반복하므로 깨우기 자체만으로 획득을 인정하지 않습니다.'),
     ('경계 경쟁과 실패 정리', '수면에서 돌아와 잠금을 잡았을 때 waiter.up이면 다음 반복의 신호·만료 검사보다 성공이 먼저입니다. 아직 인계가 없고 신호 또는 만료 조건이 확인되면 list_del 후 각각 -EINTR, -ETIME입니다. 같은 잠금이 인계와 제거를 직렬화하므로 반환한 스택 waiter를 목록에 남기지 않습니다.'),
     ('계측과 상태별 wrapper', '__down_common은 trace_contention_begin(sem,0), 실제 공통 대기, trace_contention_end(sem,ret)를 연결합니다. __down/interruptible/killable/timeout은 상태와 timeout 값을 고정해 전달하는 noinline 함수입니다. 주석은 inline 핵심 함수의 상수 인자가 최적화될 수 있다고 설명하며 이 계측이 자원을 획득하는 별도 알고리즘인 것은 아닙니다.'),
     ('공정성과 소유권', '꼬리 삽입과 첫 항목 인계는 대기자 선택의 FIFO를 만듭니다. CPU에서 실제 후속 작업 완료 순서나 우선순위 상속을 보장하는 코드는 아닙니다. mutex와 달리 다른 실행 주체의 up이 가능하지만 count의 균형과 객체 수명은 호출자의 프로토콜로 유지해야 합니다.'),
     ('CS 연결과 검증 범위', '자원 토큰, 직접 인계, FIFO 큐, 스택 대기 객체의 수명, 상태 전이의 잠금 직렬화, 성공과 오류의 반환 규약을 학습합니다. 원본 대조는 실제 스케줄러와 모든 신호·IRQ 경쟁을 실행한 검사가 아닙니다.')],
    [('down_trylock이0을 반환했을 때 의미는?', '세마포어 획득 성공이다', '자원이 없어 실패했다', '구현은 감소 후보가 음수인지 반환합니다. 문서는 spin_trylock과 mutex_trylock의 성공 true 규약과 반대라고 경고합니다.'),
     ('대기자가 있을 때 up은 먼저 count를 늘리는가?', '아니다. 첫 대기자에게 up 플래그로 직접 인계한다', '그렇다. count를 늘린 뒤 모든 대기자가 경쟁하게 한다', '__up은 첫 항목 제거, up=true, wake_up_process를 수행합니다. count 증가는 대기 목록이 비어 있는 분기에만 있습니다.'),
     ('down_timeout에 timeout0을 주었지만 count가1이면?', '즉시 획득해0을 반환할 수 있다', '언제나 -ETIME이다', 'public 함수의 빠른 경로는 timeout 검사보다 먼저 count를 줄입니다. timeout 검사는 자원이 없어 느린 대기에 들어간 경우에 적용됩니다.'),
     ('수면 뒤 잠금을 다시 잡았을 때 waiter.up이 true이면 timeout이 끝났어도?', '성공0을 반환한다', '인계된 자원을 버리고 항상 -ETIME을 반환한다', '깨어난 직후 up 검사가 다음 반복의 timeout 검사보다 앞섭니다. 잠금 아래 이미 인계된 사실을 확인하면 획득 성공으로 끝납니다.'),
     ('interruptible 획득의 신호 오류는 completion과 같은 -ERESTARTSYS인가?', '아니다. 이 구현은 -EINTR이다', '그렇다. 모든 커널 대기는 같은 오류다', '___down_common의 interrupted 레이블은 대기 항목을 제거하고 -EINTR을 반환합니다. 비슷한 대기 API라도 반환 계약을 개별 확인해야 합니다.')])
