"""Whole mutex public representation and API headers."""
ROWS = []


def add(path, title, intro, principle, use, sections, questions):
    ROWS.append(dict(path=path, title=title, intro=intro, principle=principle,
                     use=use, area='상호 배제 · 소유권 · 조건부 컴파일 · 자원 수명',
                     sections=sections, questions=questions))


add('include/linux/mutex_types.h', 'Mutex 타입 전체: 소유권 규칙과 RT별 표현',
    'mutex의 사용 규칙과 빌드 설정별 구조체 표현을 선언합니다.',
    '잠금 소유자 규칙은 자료구조와 API가 함께 지킵니다. PREEMPT_RT 여부에 따라 내부 구현 표현이 달라지므로 공개 API를 통해 사용해야 합니다.',
    'mutex를 단순 메모리 복사나 memset으로 초기화하지 않습니다. 잠금이 저장된 메모리와 소유 태스크의 수명도 규칙의 일부입니다.',
    [('전체 구성', 'GPL-2.0과 guard, atomic/lockdep_types/osq_lock/spinlock_types/types 포함 뒤 PREEMPT_RT 분기로 나뉩니다. 일반 분기에 의미 규칙 주석과 mutex 구조체, RT 분기에 rtmutex.h 포함과 대체 구조체가 있습니다. 이 파일은 획득·해제 함수 본문을 제공하지 않습니다.'),
     ('소유권 규칙', '한 번에 한 태스크만 소유하고 소유자만 unlock할 수 있으며 반복 unlock과 재귀 잠금을 금지합니다. 소유한 채 태스크가 종료해서도 안 됩니다. 이는 count1인 세마포어의 소유자 없는 up 계약과 다르며 잠금 성공 여부를 확인하지 않은 채 unlock하는 사용도 올바르지 않습니다.'),
     ('객체와 실행 문맥', 'API로 초기화해야 하고 memset 또는 복사로 초기화하면 안 됩니다. 보유된 잠금을 담은 메모리를 free하거나 보유된 mutex를 재초기화하면 안 됩니다. 하드웨어·소프트웨어 인터럽트, tasklet·timer 문맥 사용도 금지하는 규칙을 명시합니다. 원자 필드가 들어 있다는 사실이 잠들 수 없는 문맥에서의 사용 허가가 아닙니다.'),
     ('일반 표현', '일반 mutex는 atomic_long_t owner, raw_spinlock_t wait_lock, list_head wait_list를 가집니다. MUTEX_SPIN_ON_OWNER이면 MCS spinner용 optimistic_spin_queue osq가 추가됩니다. owner의 구체적 플래그 인코딩과 낙관적 스핀 알고리즘은 이 타입 선언만으로 정의되지 않으므로 구현을 따로 확인해야 합니다.'),
     ('진단 필드와 주석 범위', 'DEBUG_MUTEXES이면 magic, DEBUG_LOCK_ALLOC이면 dep_map이 추가됩니다. 주석은 이름·획득 지점·소유자·재귀·교착 관련 디버깅 기능을 설명합니다. 이 구조체 파일 자체가 그 검사를 실행하는 것은 아니며 개별 디버그 함수 하나만으로 모든 기능을 보장한다고 읽지 않습니다.'),
     ('RT 표현', 'PREEMPT_RT에서는 rt_mutex_base rtmutex와 선택적 dep_map으로 표현합니다. 일반 분기의 owner/wait_list를 모든 빌드에 직접 접근하는 코드는 맞지 않습니다. 조건부 필드는 크기와 배치를 바꾸므로 내부 구조체를 고정된 외부 ABI처럼 취급하지 않습니다.'),
     ('CS 연결', '상호 배제와 소유권, 잠금과 객체 수명, 잠들 수 있는 문맥, 표현을 바꾸면서 API 계약을 유지하는 추상화, 설정별 메모리 배치를 학습합니다.')],
    [('mutex를 소유한 태스크와 다른 태스크가 unlock해도 되는가?', '안 된다. 소유자만 해제해야 한다', '된다. 세마포어 up과 완전히 같다', '이 헤더의 규칙은 소유자 해제를 명시합니다. 세마포어와 mutex를 모두 이진 상태로만 보면 이 차이를 놓치게 됩니다.'),
     ('일반 mutex의 owner 필드는 PREEMPT_RT에서도 같은 위치에 존재하는가?', '아니다. RT 분기는 rt_mutex_base 중심의 다른 표현이다', '그렇다. 모든 설정에서 필드와 크기가 고정된다', '조건부 구조체 정의가 서로 다릅니다. 공개 API를 사용해야 하며 일반 분기 필드 직접 접근을 모든 설정에 적용하면 안 됩니다.'),
     ('mutex 메모리를0으로 채우면 API 초기화와 같은가?', '아니다. 문서는 memset이나 복사 초기화를 금지한다', '그렇다. 비트가0이면 언제나 올바른 unlocked 상태다', '대기 리스트·잠금·진단 구조가 함께 초기화되어야 합니다. 구조체의 한 상태값만0으로 만드는 것으로 전체 불변식을 대체할 수 없습니다.')])

add('include/linux/mutex.h', 'Mutex 공개 헤더 전체: 초기화·잠금 변형·자동 정리',
    '일반·RT 초기화와 진단 설정을 연결하고 여러 획득 방식과 scope guard를 선언합니다.',
    '같은 API 이름을 빌드 설정에 맞는 구현으로 연결합니다. 획득 성공 판정과 잠금 해제 책임을 유지하면서 진단 메타데이터만 조건부로 확장합니다.',
    '실제 경쟁 알고리즘은 kernel/locking의 구현을 함께 읽습니다. mutex_is_locked는 관측이지 현재 호출자의 소유권 획득이 아닙니다.',
    [('전체 구성', 'GPL-2.0과 guard, current/list/spinlock_types/lockdep/atomic/processor/osq/debug_locks/cleanup/mutex_types 포함, device 전방 선언 뒤 진단 초기화·destroy, init, RT별 정적·동적 초기화, devm 초기화, lockdep별 획득 선언, trylock/unlock/원자 감소 helper, guard 정의가 있습니다.'),
     ('진단 초기화 조각', 'DEBUG_LOCK_ALLOC이면 dep_map의 문자열 이름과 LD_WAIT_SLEEP을 초기화식에 추가합니다. DEBUG_MUTEXES이면 magic에 객체 주소를 넣고 외부 mutex_destroy를 선언합니다. 비활성에서는 이 초기화 조각이 사라지고 mutex_destroy가 빈 inline이 됩니다. destroy가 모든 빌드에서 실제 메모리를 free하는 함수라는 뜻은 아닙니다.'),
     ('동적 초기화와 key', 'mutex_init은 매크로 호출 위치의 static lock_class_key와 문자열화한 이름을 __mutex_init에 전달합니다. mutex_init_with_key는 호출자가 지정한 key를 사용합니다. 주석은 이미 잠긴 mutex를 초기화하지 말라고 명시합니다. lockdep class 지정은 실제 상호 배제 연산의 대체가 아닙니다.'),
     ('일반 커널 초기화', '비RT __MUTEX_INITIALIZER는 owner0, unlocked wait_lock, 자기 연결 wait_list와 조건부 진단 필드를 초기화합니다. DEFINE_MUTEX는 이를 사용해 구조체를 선언합니다. 이 분기의 __mutex_init과 mutex_is_locked는 외부 선언입니다. 타입 헤더의 optional osq처럼 명시하지 않은 멤버는 C 초기화 규칙도 함께 고려해야 합니다.'),
     ('RT 초기화와 상태 관측', 'RT 정적 초기화는 __RT_MUTEX_BASE_INITIALIZER와 조건부 dep_map을 사용합니다. 동적 __mutex_init 매크로는 rt_mutex_base_init 다음 __mutex_rt_init을 호출합니다. mutex_is_locked는 rt_mutex_base_is_locked로 연결합니다. 잠금 여부 관측 결과로 다른 CPU의 이후 동작을 막거나 소유자를 예약할 수는 없습니다.'),
     ('장치 관리 초기화 순서', 'devm_mutex_init은 typeof 임시 mutex_에 포인터 표현을 저장해 한 번 평가한 뒤 mutex_init을 실행하고 __devm_mutex_init의 결과를 반환합니다. DEBUG_MUTEXES이면 외부 함수가 destroy action 등록을 담당합니다. 비활성이면 등록 helper가0을 반환하여 불필요한 devm action을 만들지 않지만 앞선 실제 mutex 초기화는 그대로 수행합니다.'),
     ('lockdep 활성 획득', 'DEBUG_LOCK_ALLOC이면 nested 계열과 _mutex_lock_nest_lock을 선언합니다. 일반 lock/interruptible/killable/io는 subclass0의 nested 함수로 매핑됩니다. mutex_lock_nest_lock은 nest_lock의 dep_map 포인터 형식을 typecheck하고 해당 map을 전달합니다. subclass와 nest 정보는 잠금 관계의 진단을 위한 것이며 같은 mutex의 재귀 획득을 허용하는 옵션이 아닙니다.'),
     ('lockdep 비활성 획득', '비활성에서는 일반 함수들을 직접 선언하고 nested/nest_lock/io_nested를 해당 일반 함수로 치환합니다. subclass 또는 nest_lock 인자는 매크로 본문에서 사용되지 않으므로 거기에 필수 부작용을 넣으면 설정에 따라 실행되지 않을 수 있습니다. 조건부 진단 메타데이터와 필수 프로그램 동작을 분리해야 합니다.'),
     ('반환 계약과 외부 helper', 'interruptible과 killable 획득은 __must_check int로 결과 검사를 요구합니다. trylock은 성공1, 경합0이며 down_trylock과 반대라는 주석을 둡니다. unlock은 void입니다. atomic_dec_and_mutex_lock도 선언하지만 감소와 최종 잠금의 구체적 경합 처리는 여기서 구현하지 않습니다.'),
     ('자동 정리 guard', 'DEFINE_GUARD(mutex)는 획득 mutex_lock과 정리 mutex_unlock을 연결합니다. 조건부 _try는 mutex_trylock 결과를, _intr는 mutex_lock_interruptible==0을 성공 조건으로 사용합니다. 두 획득 API의 성공값이 달라 조건식도 다릅니다. guard의 scope 정리 기능이 객체 자체의 메모리 수명이나 IRQ 사용 규칙을 없애지는 않습니다.'),
     ('CS 연결과 범위', '조건부 API 매핑, 정적 initializer 조각, lock class, 포인터 표현의 단일 평가, return convention을 정규화한 조건부 자원 획득, scope 기반 정리를 학습합니다. 이 헤더 전체를 다뤘지만 mutex.c의 획득 알고리즘까지 완료로 세지 않습니다.')],
    [('디버그 비활성 devm_mutex_init은 실제 mutex 초기화도 생략하는가?', '아니다. mutex_init은 수행하고 cleanup 등록 helper만0을 반환한다', '그렇다. 전체 매크로가 빈 문장이다', '매크로는 먼저 mutex_init을 실행합니다. 설정으로 달라지는 부분은 뒤의 __devm_mutex_init이며 destroy가 빈 동작이면 별도 devm 등록을 생략합니다.'),
     ('mutex_trylock과 interruptible guard의 성공 판정이 다른 이유는?', 'trylock은1, interruptible 획득은0이 성공이기 때문이다', '두 API 모두 음수만 성공이기 때문이다', 'DEFINE_GUARD_COND의 _try는 반환값을 그대로, _intr는 ==0을 사용합니다. 성공 규약을 혼동하면 획득하지 않은 잠금을 소유한 것처럼 처리할 수 있습니다.'),
     ('mutex_lock_nested가 같은 mutex의 재귀 잠금을 허용하는가?', '아니다. subclass는 lockdep 진단 정보이다', '그렇다. nested라는 이름이면 재귀 획득이 안전하다', '비활성 빌드에서는 일반 mutex_lock으로 치환됩니다. mutex의 재귀 금지 규칙은 유지되며 서로 다른 잠금 인스턴스의 중첩 관계와 구별해야 합니다.'),
     ('mutex_is_locked가 false이면 바로 보호 데이터에 접근해도 되는가?', '아니다. 관측은 잠금 획득이 아니다', '그렇다. false 반환이 현재 태스크에게 소유권을 준다', '헤더는 잠김 여부를 조회하는 기능만 제공합니다. 실제 획득 API를 거치지 않으면 다른 CPU가 즉시 잠금을 잡을 수 있습니다.')])
