"""Whole reference-counter ordering migration document."""
ROWS = [dict(
    path='Documentation/core-api/refcount-vs-atomic.rst',
    title='참조 계수 전환 문서 전체: atomic에서 refcount로 바뀌는 메모리 순서',
    intro='일반 원자 정수를 참조 계수 API로 바꿀 때 유지되거나 달라지는 메모리 순서를 일곱 경우로 분류한 문서입니다.',
    principle='이름이 비슷한 함수로 바꾸어도 장벽의 강도가 같다는 보장은 없습니다. 객체 포인터 획득, 참조 획득, 마지막 해제의 순서 요구를 각각 확인해야 합니다.',
    use='atomic_t 기반 참조 수를 refcount_t로 전환하는 코드 검토에 사용합니다. 이 문서는 메모리 순서 비교에 초점이 있으며 포화·오용·잠금 계약은 실제 구현과 함께 확인합니다.',
    area='동시성 · 메모리 모델 · 원자성 · API 전환',
    sections=[
        ('문서 전체 구성', '제목과 지역 목차 지시문 뒤 Introduction, 관련 메모리 순서 설명, 일곱 함수 비교 사례로 구성됩니다. 서론은 최소 참조 계수 API와 일반 원자 연산의 순서 차이를 소개하며 LKMM 설명, memory-barriers와 atomic_t 문서를 배경으로 가리킵니다. 이 수업은 현재 문서 전체를 다루지만 링크된 다른 문서까지 학습 완료로 세지 않습니다.'),
        ('원자성과 unordered', 'unordered 원자 연산은 해당 원자적 접근과 모델의 프로그램 순서 관계를 제공하지만 주변의 모든 일반 메모리 접근을 다른 CPU에 같은 순서로 보이게 하지 않습니다. 원문의 단일 CPU program order 설명을 실제 CPU가 모든 명령을 물리적으로 순차 완료한다는 뜻으로 확대하지 않습니다. 원자성만으로 객체 데이터의 공개 순서가 완성되지 않습니다.'),
        ('full 순서', '문서는 full ordering을 앞선 읽기·쓰기와 뒤따르는 접근 사이의 강한 순서로 설명하고 smp_mb를 예로 듭니다. 다른 CPU에서 전파되어 온 쓰기까지 포함하는 A-cumulative 성질도 언급합니다. 이를 단순히 해당 계수 값만 원자적으로 바뀐다는 성질과 구별해야 합니다. 구체적 실행의 허용 여부는 실제 동기화 관계와 LKMM에 따라 판단합니다.'),
        ('release와 acquire', 'release는 그 연산보다 앞선 읽기·쓰기를, acquire는 그 연산보다 뒤따르는 읽기·쓰기를 정렬하는 방향성이 있습니다. 문서는 release의 예로 smp_store_release, acquire의 예로 smp_acquire__after_ctrl_dep를 사용합니다. 이것이 모든 acquire 연산의 유일한 구현이라는 뜻은 아닙니다. 참조 계수 감소 성공 경로가 어떤 형태로 이 보장을 제공하는지 구현에 대응해 읽습니다.'),
        ('성공 제어 의존성', '참조 획득이 성공했다는 결과에 의존하는 이후 저장은 성공 경로와 순서 관계를 가집니다. 문서는 명시적 장벽 대신 저장 추측 실행에 대한 제약을 설명하며 이 관계만으로 다른 CPU 전체에 대한 보장이 생기지 않는다고 강조합니다. 성공 검사 없이 무조건 객체를 수정하거나 제어 의존성을 일반적인 후속 읽기 acquire로 간주하면 안 됩니다.'),
        ('사례1: set과 read', 'atomic_set/read에서 refcount_set/read로 전환할 때 둘 다 unordered라 메모리 순서 변화가 없다고 설명합니다. 그러나 refcount_read는 참조 획득이 아니므로 관측 직후 객체가 살아 있다는 예약은 아닙니다. 초기화 값의 의미와 공유 포인터 공개 절차는 별도 검토 대상입니다.'),
        ('사례2: 반환 없는 증가', 'atomic_inc/add와 refcount_inc/add는 모두 unordered라 이 분류에서는 장벽 변화가 없습니다. 그렇다고 기능 전체가 동일한 것은 아닙니다. 실제 refcount 구현에는 포화와0 증가 경고가 있고, 객체의 기존 참조 또는 적절한 수명 보호가 필요합니다.'),
        ('사례3: 반환 없는 감소', 'atomic_dec에서 refcount_dec로 전환하면 unordered에서 release로 순서가 강화됩니다. 하지만 refcount_dec는 정상 마지막 해제 결과를 알려주는 API가 아닙니다. v6.12 실제 헤더는 이전 값1 이하를 DEC_LEAK 경고·포화로 처리하므로 이 순서 비교표만 보고 마지막 참조 감소까지 단순 치환하면 안 됩니다.'),
        ('사례4: 결과 있는 증가', 'atomic_inc_not_zero에서 refcount_inc_not_zero로 옮길 때 문서는 full ordering에서 성공 시 저장에 대한 제어 의존성으로 바뀐다고 설명합니다. refcount_add_not_zero에는 표에서 대응하는 atomic 함수를 두지 않습니다. 핵심 주석은 객체 포인터를 얻는 과정에서 필요한 순서가 이미 제공되어야 한다는 것입니다. 이를 참조 증가의 반환값 검사만으로 대체할 수 없습니다.'),
        ('사례5: 결과 있는 일반 감소', 'atomic_dec_and_test/sub_and_test에서 refcount 버전으로 바뀌면 full ordering 대신 release와 성공 시 acquire입니다. 실패 경로까지 항상 full barrier라고 기대했던 코드는 다시 검토해야 합니다. 실제 헤더에서 정상 마지막 감소 조건을 만족할 때 smp_acquire__after_ctrl_dep를 실행하는 부분과 대응합니다.'),
        ('사례6: 특수 조건부 감소', 'dec_if_one에는 직접 대응하는 atomic API가 없고, atomic_add_unless(var,-1,1)는 refcount_dec_not_one으로 비교합니다. 문서는 release와 제어 의존성으로 설명하며 atomic_add_unless의 full ordering도 성공 시에만 있다는 주의를 붙입니다. 실패한 비교 교환을 성공한 release와 같게 읽거나 모든 false 경로에 강한 장벽을 가정하지 않습니다. 포화·언더플로 조기 반환 같은 예외는 실제 lib/refcount.c도 확인합니다.'),
        ('사례7: 잠금 결합 감소', 'atomic_dec_and_lock/mutex_lock에서 refcount 버전으로 옮기는 경우 release, 제어 의존성, 성공 시 잠금 보유를 설명합니다. 마지막 표의 spin_lock 표현은 mutex 사례까지 열거한 문맥에서 읽어야 하며 실제 mutex 버전은 mutex를 보유합니다. 잠금을 잡은 채 true로 돌아오는 함수의 호출자는 정리 이후 적절한 unlock을 수행해야 합니다.'),
        ('문서와 현재 구현의 대조', '서론은 일반 구현을 lib/refcount.c로 소개하지만 v6.12의 기본 가감 연산 상당수는 include/linux/refcount.h의 inline입니다. lib에는 포화 경고와 특수 감소·잠금 helper가 있습니다. 설명 문서의 개괄과 현재 구현 배치를 함께 읽고, 이 파일에 없는 irqsave 변형이나 포화 분기까지 비교표가 전부 증명한다고 주장하지 않습니다.'),
        ('CS 연결과 적용 절차', '먼저 코드가 참조 수인지 일반 동기화 카운터인지 구별하고, 포인터를 얻는 순서, 성공·실패 경로의 후속 읽기·쓰기, 마지막 해제, 잠금 해제 책임을 확인합니다. 그 뒤 전환 API와 포화 동작을 대응합니다. 이 수업은 문서·구현 독해이며 모든 약한 메모리 실행을 litmus test로 검증한 결과는 아닙니다.')
    ],
    questions=[
        ('atomic_inc_not_zero를 refcount_inc_not_zero로 바꿀 때 주변 읽기의 순서도 자동으로 동일한가?', '아니다. 객체 포인터 획득 측에서 필요한 순서를 제공하는지 확인해야 한다', '그렇다. 함수 이름이 같으면 장벽도 항상 같다', '사례4는 full ordering에서 성공 시 저장 제어 의존성으로 바뀜을 설명합니다. 제어 의존성만으로 일반적인 후속 읽기 acquire를 대체할 수 없습니다.'),
        ('refcount_dec_and_test가 false인 경로도 문서상 성공 경로와 동일한 acquire를 보장하는가?', '아니다. 추가 acquire는 정상 마지막 감소 성공에 붙는다', '그렇다. 반환값에 관계없이 언제나 full ordering이다', '사례5의 계약은 release와 성공 시 acquire입니다. 실제 헤더도 마지막 감소 조건을 만족한 경로에서만 acquire helper를 실행합니다.'),
        ('atomic_dec에서 refcount_dec로 바꾸면 메모리 순서가 어떻게 달라지는가?', 'unordered에서 release로 강화된다', 'full ordering에서 unordered로 약해진다', '사례3의 비교입니다. 다만 장벽 강화와 별개로 refcount_dec의 마지막 감소 오용 경고를 확인해야 하며 기능 전체가 단순 치환 가능한 것은 아닙니다.'),
        ('비교표의 hold spin_lock 표현 때문에 mutex helper도 spinlock을 보유한다고 해석해도 되는가?', '아니다. 실제 mutex helper는 mutex를 보유한 채 성공한다', '그렇다. 모든 refcount 잠금은 내부적으로 같은 spinlock이다', '사례7은 두 잠금 API를 함께 비교합니다. lib/refcount.c의 mutex 버전은 mutex_lock을 사용하고 성공 시 풀지 않으므로 구체적인 잠금 종류는 해당 구현을 따라야 합니다.'),
        ('set/read 전환에서 메모리 순서 변화가 없으면 read가 객체 수명을 확보하는가?', '아니다. 관측과 참조 획득은 다른 연산이다', '그렇다. unordered read도 객체를 자동으로 붙잡는다', '사례1은 순서 보장 변화만 비교합니다. 값 관측은 다른 CPU의 마지막 해제를 막지 않아 별도 참조 또는 외부 보호가 필요합니다.')
    ]
)]
