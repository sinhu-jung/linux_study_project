"""Complete refcount representation and inline operation contracts."""
ROWS = []


def add(path, title, intro, principle, use, sections, questions):
    ROWS.append(dict(path=path, title=title, intro=intro, principle=principle,
                     use=use, area='원자 연산 · 메모리 순서 · 참조 계수 · 정수 경계',
                     sections=sections, questions=questions))


add('include/linux/refcount_types.h', 'Refcount 타입 전체: 원자 정수를 소유권 계수로 구분하기',
    'refcount_t의 메모리 표현만 분리한 작은 헤더입니다.',
    'atomic_t를 필드로 가진 별도 구조체를 정의해 일반 원자 정수와 참조 계수의 사용 계약을 구분합니다. 포화는 타입 자체가 아니라 연산 구현이 지킵니다.',
    '타입만 필요한 선언에서 사용할 수 있습니다. 참조 수 연산과 초기화 상수는 refcount.h를 함께 확인해야 합니다.',
    [('전체 구성', 'GPL-2.0 표시, include guard, linux/types.h 포함, refcount_t의 kernel-doc, atomic_t refs 하나를 가진 refcount_struct와 typedef, endif가 전부입니다. 별도 잠금, destructor, 객체 포인터나 카운터 폭 필드는 없습니다.'),
     ('표현과 연산의 분리', 'refcount_t는 atomic_t 그 자체의 typedef가 아니라 atomic_t를 포함하는 구조체입니다. 따라서 일반 atomic_t API와 구별되는 인터페이스를 만들 수 있습니다. 그러나 C 구조체 필드가 공개되어 있으므로 refs를 직접 변경하는 잘못된 코드까지 언어 차원에서 금지하지는 않습니다.'),
     ('포화 계약의 위치', '주석은 REFCOUNT_SATURATED에 포화해 잘못된 순환에 따른 use-after-free를 막는다고 설명합니다. 이 파일은 그 상수를 정의하거나 포화 검사를 실행하지 않습니다. 실제 구현은 refcount.h의 연산과 lib/refcount.c의 경고·포화 경로이며, 경합 중 잠시 값이 달라졌다가 복원되는 동작까지 함께 읽어야 합니다.'),
     ('CS 연결', '표현을 공유하면서 인터페이스로 의미를 분리하는 타입 설계, 최소 의존 헤더, 원자성과 수명 안전성의 차이를 학습합니다. refcount_t 멤버를 넣었다고 구조체의 모든 필드 접근이 자동으로 원자적이거나 동기화되는 것은 아닙니다.')],
    [('refcount_t는 atomic_t의 단순 별명인가?', '아니다. atomic_t refs를 포함한 별도 구조체 타입이다', '그렇다. 두 타입의 모든 API를 구분 없이 사용한다', 'typedef 대상은 struct refcount_struct입니다. 내부 표현은 원자 카운터지만 사용자는 참조 계수의 포화와 수명 규칙을 지키는 API를 이용해야 합니다.'),
     ('이 타입 정의만으로 임의의 refs 직접 수정에도 포화가 보장되는가?', '아니다. 포화는 참조 계수 연산 구현의 책임이다', '그렇다. C 구조체가 자동으로 모든 저장을 포화시킨다', '이 파일에는 실행 코드도 REFCOUNT_SATURATED 정의도 없습니다. 타입의 문서화된 의미와 실제 연산이 그 의미를 유지하는 절차를 구별해야 합니다.')])

add('include/linux/refcount.h', 'Refcount 헤더 전체: 포화 산술과 참조 수 메모리 순서',
    '참조 수 전용 초기화·조회·증가·감소 연산과 외부 잠금 helper 선언을 제공합니다.',
    '정상 경로는 짧은 원자 연산으로 처리하고 잘못된 증가·감소는 포화시켜 조기 해제를 막습니다. 마지막 정상 감소만 true와 acquire 정렬을 제공하며 단순 감소와 구분합니다.',
    '증가 전에 객체 메모리가 유효해야 하며 증가 자체는 공개된 객체 데이터를 읽는 acquire가 아닙니다. 배치 가감은 일반적인 한 개씩의 참조 관리보다 더 신중한 사용 계약을 요구합니다.',
    [('파일 전체 구성', 'GPL-2.0 및 포화·메모리 순서 설계 주석, guard, atomic/bug/compiler/limits/refcount_types/spinlock_types 포함, mutex 전방 선언, 초기화·한계 상수와 사건 enum, 포화 경고 선언, inline 연산군, 외부 조건부 감소·잠금 함수 선언으로 끝납니다. 반복 wrapper도 각 내부 함수의 고정 인자와 oldp 전달 관계를 확인해야 합니다.'),
     ('상수와 사건 종류', 'REFCOUNT_INIT(n)은 refs를 ATOMIC_INIT(n)으로 초기화합니다. MAX는 INT_MAX, SATURATED는 INT_MIN/2이며 주석의32비트 표현으로0xc0000000입니다. ADD_NOT_ZERO_OVF, ADD_OVF, ADD_UAF, SUB_UAF, DEC_LEAK는 실패 상황을 구분하는 enum입니다. 이 포화 값은 rcuref의 SATURATED 값과 같지 않으므로 두 API의 상태 인코딩을 섞으면 안 됩니다.'),
     ('포화의 구현 모델', '모든 연산에 비교 교환 루프를 넣는 비용을 피하기 위해 일부 연산은 먼저 원자 가감하고 잘못된 값이면 포화 중심으로 복원합니다. 따라서 포화에 도달하면 의미상 더 이상 정상 개수로 돌아오지 않는다는 계약과, 경합 중 물리적 값이 잠시 변할 수 있다는 구현을 구별합니다. 포화는 정확한 소유자 수 추적을 포기하고 누수를 택해 조기 해제를 막는 방향입니다.'),
     ('포화 영역 논증의 전제', '주석은 당시 PID_MAX_LIMIT 0x400000과 포화 중심에서 순환까지의0x40000000 간격을 이용해 비율256을 계산합니다. 단일 참조 연산, 중간 oops 반복 유발 제한 등의 전제가 붙으며 큰 배치 가감에는 별도의 경합 가능성을 논의합니다. 이 계산을 임의의 큰 i, 무제한 스레드, 모든 환경에 대한 무조건적인 증명으로 확대하지 않습니다.'),
     ('설명 예제와 실제 검사', '서두의 개념 예시는 old<0 검사만 보여주지만 실제 __refcount_add는 old<0 또는 old+i<0을 검사합니다. 따라서 INT_MAX에서1을 더하는 경계를 분석할 때 실행 코드의 두 조건을 기준으로 해야 합니다. __signed_wrap 표기가 붙은 함수의 산술을 표준 사용자 공간 C에서 부호 있는 넘침이 언제나 정의된 것처럼 옮겨 쓰지 않습니다.'),
     ('set과 read', 'refcount_set은 atomic_set에 int n을 전달하고 read는 atomic_read 결과를 unsigned int로 반환합니다. set에는 별도 범위 검사나 공개용 release 연산이 없습니다. read는 관측일 뿐 참조 획득이 아니며 포화의 음수 내부 표현도 unsigned로 보입니다. 관측값이 양수라는 이유만으로 객체 접근 권한이 생기지 않습니다.'),
     ('조건부 배치 증가', '__refcount_add_not_zero는 old를 읽고0이면 루프를 벗어납니다. 아니면 old+i를 atomic_try_cmpxchg_relaxed로 저장할 때까지 경쟁 실패마다 갱신된 old로 재검사합니다. oldp가 있으면 종료 시 old를 기록합니다. old<0 또는 old+i<0이면 ADD_NOT_ZERO_OVF로 포화 처리하고 마지막에 old를 bool로 반환합니다. 반환 true는 정상 참조 개수가 정확히 i만큼 유지되었다는 보증과 다릅니다.'),
     ('무조건 배치 증가', '__refcount_add는 atomic_fetch_add_relaxed로 먼저 더하고 이전 값을 oldp에 선택적으로 기록합니다. old==0이면 ADD_UAF가 우선이고, 아니면 old<0 또는 old+i<0일 때 ADD_OVF입니다.0에서 증가해 잠시 양수가 되었어도 정상 재초기화로 인정하지 않고 포화시킵니다. public add는 oldp=NULL로 내부 함수를 호출합니다.'),
     ('한 개 증가 wrapper', '__refcount_inc_not_zero는 조건부 배치 함수에 i=1을 전달하고 public inc_not_zero는 oldp=NULL로 호출합니다. __refcount_inc와 public inc도 같은 방식으로 무조건 증가를1로 고정합니다. 일반적인 단일 참조 획득에는 이 변형들이 권장됩니다. 조건부 획득의 결과는 __must_check이며0일 때 객체 사용으로 진행하지 않아야 합니다.'),
     ('감소와 마지막 참조 검사', '__refcount_sub_and_test는 atomic_fetch_sub_release 후 oldp를 기록합니다. old>0이고 old==i이면 smp_acquire__after_ctrl_dep를 실행하고 true입니다. 그 외 old<=0 또는 old-i<0이면 SUB_UAF로 포화한 뒤 false입니다. 예를 들어 old3,i3은 정상 마지막 감소이고 old2,i3은 언더플로이며, 단순히 저장 결과의 비트가0인지 확인하는 구현과 다릅니다.'),
     ('감소 wrapper의 관계', 'public sub_and_test는 oldp=NULL, __dec_and_test는 i=1, public dec_and_test는 그 내부 함수에 oldp=NULL을 전달합니다. 따라서 마지막 참조 반환과 성공 acquire의 계약은 같은 핵심 경로에서 나옵니다. 배치 감소는 한 번에 반납할 소유권이 실제로 있는지 호출자가 보장해야 합니다.'),
     ('단순 dec의 중요한 차이', '__refcount_dec는 fetch_sub_release(1) 후 oldp를 기록하고 old<=1이면 DEC_LEAK로 포화합니다. 따라서 old1에서 단순 dec는0으로 정상 수명을 끝내는 방법이 아니며 경고·누수 방향으로 처리됩니다. 반환값 없는 public dec는 이 함수를 oldp=NULL로 호출합니다. 마지막 참조를 해제할 수 있는 사용처는 dec_and_test 같은 적절한 API와 정리 절차가 필요합니다.'),
     ('oldp의 의미', '밑줄 내부 변형들은 optional int *oldp로 이전 값을 전달합니다. fetch 연산에서는 가감 직전 값, 조건부 비교 교환에서는 성공 직전 값 또는0으로 중단한 관측값입니다. public wrapper는 이를 NULL로 숨깁니다. 포화 경고가 이후 실제 카운터를 바꿀 수 있으므로 oldp는 현재 상태나 객체 생존 보증이 아닙니다.'),
     ('증가와 메모리 순서', '증가는 relaxed이며 객체를 얻는 잠금 획득이나 RCU 의존적 읽기 등이 필요한 공개 순서를 제공한다고 가정합니다. 성공한 inc_not_zero의 제어 의존성은 이후 저장과 관련됩니다. 이것을 후속 모든 읽기를 정렬하는 일반 acquire와 혼동하지 않습니다. 객체 메모리의 안정성은 카운터를 만지기 전에 확보해야 합니다.'),
     ('감소와 메모리 순서', '감소는 release로 앞선 읽기·쓰기를 정렬하며 sub_and_test와 dec_and_test는 정상 마지막 감소 성공 시 acquire도 제공합니다. 객체를 실제 해제하고 새로 할당하는 사이의 순서는 allocator 책임이라는 주석도 있습니다. 모든 refcount 함수가 같은 강도의 완전 장벽을 제공한다고 가정하면 안 됩니다.'),
     ('외부 선언과 정적 검사', 'dec_if_one, dec_not_one, dec_and_mutex_lock, dec_and_lock, dec_and_lock_irqsave는 __must_check 외부 선언이며 구현은 lib/refcount.c입니다. 잠금 결합 세 함수에는 __cond_acquires(lock)이 붙어 성공 조건의 잠금 획득 계약을 표현합니다. 이 표기가 런타임에 잠금을 잡는 것이 아니라 실제 구현과 분석 도구가 공유하는 계약임을 구분합니다.'),
     ('CS 연결과 검증 범위', '포화 정수, 조건부 원자 갱신 루프, 실패 시 기대값 갱신, release/acquire, 제어 의존성, 객체 소유권과 메모리 유효성, API를 좁혀 오용을 줄이는 설계를 학습합니다. 소스 대조와 수업 구조 검사는 모든 아키텍처의 메모리 모델이나 경쟁 실행을 증명한 검사가 아닙니다.')],
    [('참조 수1에 refcount_dec를 호출하면 정상적인 마지막 해제가 되는가?', '아니다. DEC_LEAK 경고와 포화 경로로 간다', '그렇다. dec_and_test와 동일하게 true를 반환한다', '__refcount_dec는 old<=1이면 포화 경고를 호출하며 반환값도 없습니다. 마지막 참조 정리는 dec_and_test의 성공을 처리하는 방식과 구별해야 합니다.'),
     ('__refcount_sub_and_test에서 acquire 정렬과 true가 나오는 조건은?', 'old>0이고 old==i인 정상 마지막 감소', '가감 후 비트 패턴이 우연히0인 모든 경우', '구현은 두 조건을 명시적으로 확인한 뒤 smp_acquire__after_ctrl_dep를 실행합니다. 잘못된 계수나 언더플로 경로는 포화시키고 false로 돌아갑니다.'),
     ('refcount_inc가0을 읽었다면 객체가 정상적으로 부활하는가?', '아니다. 증가 후 ADD_UAF로 포화 처리한다', '그렇다.0에서1로 갔으므로 init과 같다', '__refcount_add는 먼저 원자 덧셈을 하지만 이전 값0을 검사해 use-after-free 의심 경로로 처리합니다. 다시 쓰려는 객체 초기화와 이미 수명이 끝난 참조 획득을 혼동하면 안 됩니다.'),
     ('inc_not_zero의 relaxed 증가만으로 객체 데이터의 공개 순서까지 해결되는가?', '아니다. 포인터 획득 측의 잠금이나 적절한 RCU 절차가 필요하다', '그렇다. 모든 참조 증가는 완전한 acquire 장벽이다', '주석은 증가에 메모리 순서를 제공하지 않는다고 명시합니다. 성공의 제어 의존성과 데이터 읽기를 위한 공개 순서는 서로 다른 요구입니다.'),
     ('조건부 증가의 비교 교환이 경쟁으로 실패하면0 여부를 다시 검사하는가?', '그렇다. 갱신된 old로 루프를 다시 시작한다', '아니다. 첫 관측이 양수이면 이후0도 무조건 증가한다', 'atomic_try_cmpxchg 실패가 기대값 old를 갱신합니다. 다음 반복에서0을 확인하므로 경쟁 중 마지막 참조가 사라진 경우0에서 증가하지 않고 false로 끝낼 수 있습니다.'),
     ('INT_MAX에서1 증가하는 경계는 실제 코드에서 무엇으로 검출하는가?', 'old+i<0 검사로 새 값의 음수 영역 진입을 확인한다', '서두 예시의 old<0만 사용하므로 언제나 검출하지 못한다', '실제 __refcount_add에는 old<0 또는 old+i<0 두 조건이 있습니다. 원문의 축약 예시와 실행되는 구현을 구별해야 합니다.'),
     ('내부 함수의 oldp는 포화 처리까지 끝난 뒤의 현재 값인가?', '아니다. 가감 이전 값 또는 조건부 획득의 종료 관측값이다', '그렇다. 항상 REFCOUNT_SATURATED 또는 최신 값이다', 'oldp 기록은 포화 검사보다 앞에 있습니다. 다른 CPU도 값을 바꿀 수 있어 oldp를 현재 참조 수나 생존 보장으로 사용할 수 없습니다.')])
