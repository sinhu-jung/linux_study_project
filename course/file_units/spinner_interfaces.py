"""Whole optimistic queue interface and generic MCS lock implementation."""
ROWS = []


def add(path, title, intro, principle, use, sections, questions):
    ROWS.append(dict(path=path, title=title, intro=intro, principle=principle,
                     use=use, area='큐 잠금 · 캐시 일관성 · 원자 교환 · 메모리 순서',
                     sections=sections, questions=questions))


add('include/linux/osq_lock.h', '낙관적 스핀 큐 헤더 전체: CPU 꼬리 인코딩',
    'mutex나 rwsem의 낙관적 스핀을 위한 MCS 계열 큐 인터페이스입니다.',
    '공유 구조체에는 큐 꼬리 CPU의 인코딩 값만 원자 정수로 저장합니다. 값 관측과 큐 획득은 서로 다른 연산입니다.',
    '일반적인 임계구역 보호 API와 동일하게 가정하지 않습니다. 구체적인 CPU 인코딩·취소·인계는 osq_lock.c 구현을 함께 읽어야 합니다.',
    [('전체 구성', 'GPL-2.0과 guard, 목적 주석, optimistic_spin_queue 구조체, unlocked 상수·초기화식·초기화 함수, lock/unlock 선언, 상태 관측과 endif가 전부입니다. 이 파일에는 include 행이 없어 atomic_t 등 필요한 정의를 가진 포함 문맥을 전제로 합니다.'),
     ('꼬리 표현', '구조체는 atomic_t tail 하나입니다. 주석은 꼬리 노드 CPU 번호의 인코딩을 저장하고 빈 큐는 OSQ_UNLOCKED_VAL이라고 설명합니다.0이 예약되어 있지만 이 헤더 자체는 CPU 번호를 어떤 산술식으로 인코딩하는지 정의하지 않습니다. tail을 원시 CPU 번호나 mutex 소유자 포인터라고 읽으면 안 됩니다.'),
     ('초기화와 선언', 'OSQ_UNLOCKED_VAL은0, OSQ_LOCK_UNLOCKED는 ATOMIC_INIT(0) 구조체 초기화식입니다. osq_lock_init은 atomic_set으로 tail을0으로 설정합니다. osq_lock은 bool, unlock은 void 외부 함수입니다. 이 헤더에는 큐 노드 메모리를 할당하거나 대기자를 정리하는 코드가 없습니다.'),
     ('관측과 소유권', 'osq_is_locked는 atomic_read(tail)!=0을 반환합니다. 순간적인 비어 있지 않음의 관측이지 현재 호출자가 큐 잠금을 소유한다는 증거가 아닙니다. 초기화도 사용 중인 큐를 안전하게 취소하는 기능이 아니므로 사용 수명과 동기화 계약을 지켜야 합니다.'),
     ('CS 연결', '공유 상태를 작은 원자 정수로 표현하기, 예약값과 인코딩, 자료구조와 구현의 분리, 관측과 획득의 구분을 학습합니다. 본문이 없는 획득·취소 알고리즘까지 이 파일 수업으로 완료 처리하지 않습니다.')],
    [('tail은 mutex 소유 태스크 포인터인가?', '아니다. 큐 꼬리 노드 CPU 번호의 인코딩이다', '그렇다. task_struct 주소를 그대로 저장한다', '이 구조체는 atomic_t 하나이고 주석이 CPU 인코딩을 명시합니다. mutex owner 표현과 낙관적 spinner 큐 표현은 다릅니다.'),
     ('osq_is_locked가 false이면 큐 잠금을 획득한 것인가?', '아니다. 빈 상태를 관측했을 뿐이다', '그렇다. 읽으면서 자동으로 소유권을 예약한다', '본문은 atomic_read와 비교뿐입니다. 다른 CPU가 직후 큐에 들어올 수 있어 획득 연산을 대신하지 못합니다.')])

add('kernel/locking/mcs_spinlock.h', 'MCS 잠금 전체: 지역 스핀과 후속 노드 연결 경쟁',
    '호출자가 제공한 노드를 큐 꼬리에 붙이고 자기 노드의 플래그에서 기다리는 MCS 잠금을 구현합니다.',
    '원자 교환으로 선행 노드를 정하고 이전 소유자가 후속 노드의 locked를 설정해 인계합니다. 꼬리 갱신과 next 연결 사이의 틈을 unlock이 명시적으로 처리합니다.',
    '획득에 사용한 동일 노드를 해제에도 전달하고 큐 참조가 끝날 때까지 유효하게 유지해야 합니다. 지역 스핀은 수면이나 자동 취소를 뜻하지 않습니다.',
    [('전체 구성', 'GPL-2.0·설계 소개·guard, asm/mcs_spinlock.h 포함, 노드 구조체, 아키텍처 대체가 없을 때의 경합 acquire/release 매크로, 메모리 순서 주의, lock/unlock inline과 endif로 구성됩니다. 이 generic 코드와 아키텍처별 구현을 구별합니다.'),
     ('노드와 공유 꼬리', 'mcs_spinlock은 next 포인터, locked 정수, qspinlock 중첩용 count를 가집니다. lock 함수의 첫 인자는 노드 포인터를 저장하는 공유 꼬리의 주소이고 두 번째는 호출자의 노드입니다. generic 획득은 locked와 next만 초기화하며 count를 갱신하지 않습니다.'),
     ('경합 acquire와 release', '기본 arch_mcs_spin_lock_contended는 smp_cond_load_acquire로 플래그가 참이 될 때까지 기다립니다. 아키텍처에 따라 단순 busy spin보다 적절한 대기 명령을 활용할 수 있다는 주석이 있습니다. 기본 unlock_contended는 smp_store_release로 후속 locked에1을 저장합니다. 이는 후속 임계구역과 앞선 임계구역의 순서를 연결합니다.'),
     ('큐 진입과 초기화 공개', 'mcs_spin_lock은 node->locked=0, next=NULL 뒤 xchg(lock,node)로 자기 노드를 꼬리에 넣고 이전 꼬리를 받습니다. 주석은 xchg의 full barrier와 전역 전이성에 의존해 초기화가 노드 관측보다 앞서고 획득 순서도 제공한다고 설명합니다. next 연결 전에 꼬리부터 바뀐다는 순서가 해제 경쟁의 핵심입니다.'),
     ('무경합 성공의 플래그', '이전 꼬리가 NULL이면 즉시 성공합니다. 이때 node->locked를1로 바꾸지 않아도 됩니다. 이 호출자는 자기 플래그에서 기다리지 않았기 때문입니다. 따라서 모든 소유자의 locked가1이라고 가정해 잠금 상태를 진단하면 무경합 소유자를 잘못 해석합니다.'),
     ('경합 연결과 지역 스핀', '선행 노드가 있으면 WRITE_ONCE(prev->next,node)로 연결하고 자기 locked에서 acquire 대기합니다. 모든 대기자가 하나의 공유 플래그를 계속 읽는 방식과 달리 각자 노드에서 기다려 캐시라인 경합을 줄이는 구조입니다. 실제 실행 완료 순서까지 항상 같은 순서라는 보증으로 확대하지 않습니다.'),
     ('후속이 안 보이는 해제', 'unlock은 READ_ONCE(node->next)로 후속을 읽습니다. 없으면 cmpxchg_release(lock,node,NULL)로 자신이 여전히 꼬리인 경우 큐를 비우고 반환합니다. 후속 포인터가 NULL이라는 첫 관측만으로 무조건 꼬리를 NULL로 덮으면 새 진입자를 잃을 수 있어 비교 교환이 필요합니다.'),
     ('꼬리와 next 사이의 틈', '비교 교환이 실패하면 다른 진입자가 이미 꼬리를 바꾸었지만 아직 prev->next를 연결하지 않았을 수 있습니다. unlock은 READ_ONCE로 next가 나타날 때까지 cpu_relax하며 기다립니다. 이 단계 없이 NULL 후속에 인계하거나 반환하면 큐 프로토콜이 깨집니다.'),
     ('후속 인계', '후속을 얻으면 arch_mcs_spin_unlock_contended로 next->locked를1로 설정합니다. 꼬리를 반드시 NULL로 만들지 않고 대기자에게 소유권을 이어줍니다. 해제 인자는 획득에 사용한 대응 노드여야 하며 호출자의 스택 노드 수명도 이 인계와 연결 정리 동안 유지되어야 합니다.'),
     ('장벽을 과대평가하지 않기', '주석은 mcs_unlock과 다음 mcs_lock의 acquire/release 쌍만으로 여러 CPU에 걸친 full barrier가 일반적으로 형성되는 것은 아니라고 경고합니다. 그런 강한 순서가 필요한 사용처는 mcs_lock 뒤 smp_mb__after_unlock_lock을 사용하라고 설명합니다. 상호 배제에 충분한 순서와 더 넓은 프로토콜이 요구하는 순서를 구분합니다.'),
     ('CS 연결과 한계', '원자 교환 큐, 지역 스핀, cacheline 이동, 분할된 공개 단계, release 인계, 노드 수명과 메모리 장벽의 범위를 학습합니다. 이 generic 파일에는 취소나 timeout 경로가 없으며 OSQ의 중도 이탈 기능이 자동 포함된다고 읽지 않습니다. 모든 CPU의 동시 실행을 실험한 검사는 아닙니다.')],
    [('무경합 mcs_spin_lock 성공 뒤 node->locked는 반드시1인가?', '아니다. 초기0 상태로도 즉시 획득에 성공한다', '그렇다. 모든 성공 경로가1을 저장한다', 'prev==NULL이면 자기 플래그에서 기다리지 않고 반환합니다. locked는 경합 인계 신호이므로 모든 소유 상태의 보편적 지표가 아닙니다.'),
     ('next가 NULL인데 꼬리를 비우는 비교 교환이 실패한 이유로 가능한 것은?', '새 진입자가 꼬리를 바꾸었지만 next 연결을 아직 마치지 않았다', '큐에는 후속이 절대로 없으므로 하드웨어 오류다', '진입자는 xchg로 꼬리를 갱신한 뒤 prev->next를 저장합니다. 두 단계 사이에 이전 소유자가 unlock을 수행하면 이 경계 상태를 관측할 수 있습니다.'),
     ('위 비교 교환 실패 후 unlock은 무엇을 하는가?', 'next 연결이 보일 때까지 기다린 뒤 후속 플래그로 인계한다', '새 꼬리를 강제로 NULL로 덮고 반환한다', '원문은 READ_ONCE(node->next) 반복과 cpu_relax를 사용합니다. 새 진입자를 잃지 않게 연결 완료를 기다리는 절차입니다.'),
     ('generic MCS 함수가 count 필드를 초기화하는가?', '아니다. locked와 next만 초기화한다', '그렇다. 매번 count를1로 만든다', 'count 주석은 qspinlock의 중첩 용도를 가리킵니다. 구조체에 필드가 있다고 이 두 generic 함수가 모두 관리하는 것은 아닙니다.'),
     ('unlock-lock 쌍이면 모든 아키텍처에서 추가 요구 없이 full barrier인가?', '아니다. 더 강한 순서가 필요한 사용처는 별도 장벽을 고려해야 한다', '그렇다. acquire와 release는 언제나 full barrier와 같다', '주석은 smp_mb__after_unlock_lock 사용이 필요한 경우를 따로 설명합니다. 임계구역 인계와 여러 CPU에 걸친 전체 순서 요구를 혼동하지 않습니다.')])
