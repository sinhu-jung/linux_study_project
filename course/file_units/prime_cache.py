"""Complete prime bitmap cache, slow paths and iteration interface."""
ROWS = []


def add(path, title, intro, principle, use, sections, questions):
    ROWS.append(dict(path=path, title=title, intro=intro, principle=principle,
                     use=use, area='소수 체 · 비트맵·RCU·실패 대체 경로',
                     sections=sections, questions=questions))


add('lib/math/prime_numbers.c', '소수 라이브러리 전체: 확장 비트맵과 RCU 캐시 수명',
    '에라토스테네스의 체에 동적 할당과 동시 읽기 수명 관리를 결합한 파일입니다.',
    '비트 번호가 정수이고 켜진 비트가 소수를 뜻합니다. 작은 정적 표로 시작해 필요하면 새 비트맵을 만들고 배수를 지웁니다. 새 표를 공개한 뒤 이전 동적 표는 RCU 지연 해제합니다. 확장 실패 시 느린 나눗셈 탐색으로 전환합니다.',
    '공개 함수는 할당과 mutex를 사용하는 확장 경로에 들어갈 수 있습니다. RCU를 사용한다는 이유만으로 모든 호출이 잠들지 않는 문맥에 안전하다고 판단하지 않습니다.',
    [('전체 구성과 초기 표', 'SPDX,로그 접두어,module/mutex/prime_numbers/slab 헤더 다음 primes 구조체가 있습니다. rcu_head,last,sz와 flexible bitmap 배열을 담습니다.64비트 long이면0..63의 소수18개와last61,32비트이면0..31의 소수11개와last31을 정적으로 저장합니다.0과1의 비트는 꺼져 있습니다. 전역 mutex와 RCU 포인터,선택적 selftest 상한이 이어집니다.'),
     ('느린 두 함수', 'slow_is_prime_number는 int_sqrt(x)부터2까지 내려가며 약수를 찾고 최종 y==1인지 반환합니다. x=0에서는거짓,x=1에서는참이라는 내부 경계 동작이 있습니다. 공개 is_prime_number(1)은 초기 비트맵에서거짓이며 이 느린 경로를 호출하지 않습니다. slow_next_prime_number는 x를 먼저 증가시켜 검사하고 ULONG_MAX에서 멈춥니다. 마지막 ULONG_MAX는 소수 보장이 아닌 종료 sentinel입니다.'),
     ('배수 제거 helper', 'clear_multiples는2*x에서 시작하되 start보다 작으면 start를 x의 배수로 올립니다. end 미만의 비트를 x 간격으로 지우고 x를 반환합니다. x 자체를 지우지 않으면서 새 구간의 합성수만 제거하는 목적입니다. 루프 산술과 입력 구간이 유효하다는 전제까지 자동 검증하는 함수는 아닙니다.'),
     ('확장 준비와 재확인', 'expand_to_next_prime는2*x를 만들고 sz<x이면 실패하며 워드 비트 수로 올림한 뒤 새 저장소를 할당합니다. 할당 실패도거짓입니다. mutex 획득 뒤 현재 표를 다시 읽어 다른 확장이 이미 x보다 큰 last를 마련했다면 새 할당을 버리고 성공 반환합니다. 할당을 잠금 밖에서 수행한 뒤 상태를 다시 확인하는 패턴입니다.'),
     ('체 생성과 게시', '새 비트맵을 모두 켜고 기존 p->sz 비트를 복사합니다.2부터 켜진 비트를 찾아 새 영역의 배수를 지우며 last를 갱신합니다. sz를 설정하고 last>x를 BUG_ON으로 확인한 뒤 rcu_assign_pointer로 게시합니다. 정적 small_primes는 해제하지 않고 이전 동적 표만 kfree_rcu합니다. 버트런 공준은 새 범위를 두 배로 잡는 수학적 배경이며 메모리 할당 성공까지 보장하지 않습니다.'),
     ('두 공개 읽기 경로', 'next_prime_number는 x>=last일 때 RCU 읽기 잠금을 풀고 확장하며,실패하면 느린 탐색으로 갑니다. 성공 뒤 다시 RCU에 들어가 현재 포인터를 읽습니다. is_prime_number는 x>=sz일 때 같은 확장 패턴을 쓰고 범위 안이면 test_bit합니다. 주석의 범위 밖 trial division 설명만 읽으면 먼저 확장을 시도하는 실제 동작을 놓칩니다.'),
     ('last 경계의 탐색', 'next 함수의 find_next_bit는 크기를 p->last로 전달합니다. 그 앞에 켜진 비트가 없으면 API의 미발견 반환값인 size 자체가 last가 됩니다. last가 소수임을 유지하므로 이 경우에도 다음 소수를 얻습니다. 예컨대초기64비트 표에서59 다음을 찾을 때61은 검색 범위 끝 sentinel과 일치합니다.'),
     ('해제와 진단', 'free_primes는 mutex 안에서 포인터를 정적 표로 되돌리고 동적 표를 지연 해제합니다. dump_primes는 PAGE_SIZE 버퍼를 할당하고 RCU 안에서 비트맵과 last/sz 정보를 출력한 뒤 버퍼를 해제합니다. 버퍼 할당이 실패하면 변환은 건너뛰고 로그 경로로 갑니다. 이 코드 읽기는 실제 RCU 유예 기간의 실행 검증이 아닙니다.'),
     ('자체 검사와 모듈', 'selftest(max)는0이면즉시성공,아니면2<=x<max에서 느린 판정과 공개 판정을 비교합니다. 소수일 때 next_prime_number(last)도 검사합니다. 실패하면 표를 덤프하고-EINVAL을 반환합니다. init이 설정된 selftest를 실행하고 exit은표를 정리합니다. selftest 모듈 매개변수는0400 권한이며 author/description/license 메타데이터로 끝납니다.'),
     ('CS와 한계', '비트맵의 공간 효율,체의 배수 제거,캐시 확장 경쟁,읽기 수명과 writer mutex의 역할 분리,할당 실패의 대체 계산을 연결합니다.2*x의 한 overflow 검사만으로 뒤의 round_up·할당 크기·모든 극단 입력 산술 안전성까지 증명되지는 않습니다. 공개 경로·내부 helper·테스트 범위를 각각 구분합니다.')],
    [('is_prime_number(1)과 내부 slow_is_prime_number(1)은 같은 결과인가?', '아니다. 공개 함수는비트맵에서거짓,내부 helper는참이다', '그렇다. 둘 다1을소수로판정한다', '초기 표에는1의 비트가 없습니다. 내부 helper는sqrt(1)=1에서루프 없이 y==1을반환합니다. 내부 동작을공개 API 결과로 일반화하면 안 됩니다.'),
     ('왜 확장 후 이전 표를 바로 kfree하지 않는가?', '기존 RCU 독자가 이전 표를 읽고 있을 수 있기 때문이다', '새 표를 이전 표와 같은 주소로 만들기 위해서다', '포인터 게시와 독자의 이전 포인터 수명은 별개입니다. kfree_rcu는 기존 읽기 구간을 고려한 지연 해제 경로입니다.'),
     ('확장 할당이 실패하면 next_prime_number는 무조건 오류를 반환하는가?', '아니다. 느린 trial division 탐색으로 전환한다', '그렇다. 항상0을반환한다', 'expand_to_next_prime 실패 분기는 slow_next_prime_number를 호출합니다. 속도와 메모리의 절충입니다.'),
     ('ULONG_MAX 반환을 실제 소수라는 보증으로 받아도 되는가?', '안 된다. 마지막 탐색 sentinel로사용된다', '된다. 모든반환값은항상소수다', '느린 탐색은 ULONG_MAX에서멈추며 문서도 최종 sentinel이라고 명시합니다. 반복자는 이 종료조건을 고려해야 합니다.'),
     ('selftest는0과1의 내부 helper 경계도 비교하는가?', '아니다. 반복은2부터시작한다', '그렇다.0부터모든정수를비교한다', '원문 for의 초기 x=2이고 x<max까지입니다. 실제 검증 구간 밖 입력을 통과했다고 세지 않습니다.')])

add('include/linux/prime_numbers.h', '소수 헤더 전체: 시작값을 그대로 내보내는 반복 매크로',
    'API 이름만으로 반복자의 첫 값과 종료를 추측하지 않습니다.',
    'is_prime_number와 next_prime_number를 선언하고 기본 반복 매크로는 from=2인 일반 반복 매크로에 위임합니다. 일반 매크로는 prime=from을 먼저 실행한 뒤 prime<=max 동안 본문을 실행합니다.',
    '일반 반복자의 첫 값은 소수인지 검사하지 않습니다. 소수만 필요하면 유효한 시작 소수를 선택하거나 시작 전에 보정해야 합니다. max는 ULONG_MAX보다 작게 두어 sentinel 반복을 피합니다.',
    [('전체 파일', 'SPDX,guard,types.h,두 함수 선언,각 반복 매크로의문서와 정의,#endif가 전부입니다. 소수 표·할당·RCU 코드는 구현 파일에 있습니다.'),
     ('기본 반복', 'for_each_prime_number(prime,max)는 from=2로위임합니다. max=10이면2,3,5,7이 나옵니다. 조건은<=이므로max 자체가소수이면 포함합니다. max<2이면 기본 반복 본문은 실행하지 않습니다.'),
     ('일반 시작값의 의미', 'from=4,max=10이면 첫 값4가 그대로 나오고 이후5,7이 이어집니다. from=1을사용하면1도 첫항목에 포함합니다. 문서의 successive prime 표현을 첫값까지 자동검증한다는 뜻으로 읽지 않습니다.'),
     ('종료와 평가', 'next_prime_number(ULONG_MAX)는 더커지지 않는 sentinel입니다. max=ULONG_MAX이면<=조건이 계속참이 될 수 있어 문서가 이 상한을 배제합니다. max 표현식은 매조건에서 평가되므로 부수효과 없는 상한을 사용합니다. 반복 변수는 unsigned long 범위의 결과를 담을 수 있어야 합니다.')],
    [('from=4,max=10인 반복 결과는?', '4,5,7', '5,7', '초기 대입 prime=from 뒤조건을검사하고 본문을실행합니다. 첫값4에소수검사는없습니다.'),
     ('max=7인 기본 반복에7이 포함되는가?', '포함된다. 조건이prime<=max이다', '포함되지않는다. 상한은항상배타적이다', '조건의<=는포함상한입니다. 구현의다른배열크기 경계와 혼동하면 안 됩니다.'),
     ('max=ULONG_MAX를 피해야 하는 이유는?', 'sentinel이더증가하지않아반복이끝나지않을수있다', 'ULONG_MAX는항상0과같기때문이다', '최종값에서next도같은값을반환하면<=조건이영원히참입니다. 헤더문서가종료전제를 명시합니다.')])
