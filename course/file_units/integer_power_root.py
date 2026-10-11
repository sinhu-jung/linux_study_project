"""Individually authored integer arithmetic, tests and build configuration."""
ROWS = []


def add(path, title, intro, principle, use, sections, questions):
    ROWS.append(dict(path=path, title=title, intro=intro, principle=principle,
                     use=use, area='정수 알고리즘 · 테스트·빌드 구성',
                     sections=sections, questions=questions))


add('lib/math/int_pow.c', '정수 거듭제곱 전체: 지수의 비트를 소비하는 반복 제곱',
    '지수 횟수만큼 반복하지 않고 이진 표현을 이용해 곱셈 수를 줄입니다.',
    'result=1에서 시작하여 exp의 최하위 비트가1이면 base를 곱합니다. exp를 오른쪽으로 한 비트 옮기고 base를 제곱하는 과정을 exp가0이 될 때까지 반복합니다.',
    'base와 결과는 u64, exp는 unsigned int입니다. 음수 지수·실수 계산·임의 정밀도는 지원하지 않습니다. u64 범위를 넘는 곱은 모듈러 산술로 순환합니다.',
    [('파일 전체', 'SPDX, pwm_bl에서 유래했다는 주석, export/math/types 헤더, int_pow 함수, GPL export가 전부입니다. 별도 상태·메모리 할당·재귀 호출이 없습니다.'),
     ('5의5승 추적', '초기(result,base,exp)=(1,5,5)입니다. 첫 반복 뒤(5,25,2), 둘째 뒤(5,625,1), 셋째 뒤(3125,390625,0)입니다. 마지막 base 제곱도 실행하지만 이후 반환에는 사용하지 않습니다.'),
     ('불변식과 비용', '반복 진입 시 result×base^exp는 원래 거듭제곱과 같습니다. 고정 폭 계산에서는 이 등식도 2^64를 법으로 해석합니다. 지수의 한 비트를 매번 없애므로 exp>0에서 반복 횟수는 floor(log2(exp))+1이고 저장 공간은 O(1)입니다.'),
     ('영 입력과 범위', 'exp=0이면 루프 없이1을 반환하므로 이 API의 int_pow(0,0)도1입니다. base=0이고 양의 지수면0입니다. int_pow(2,63)은2^63이지만 int_pow(2,64)는 u64에서0이며 오류 코드는 없습니다. 지수만큼 선형 곱셈하는 독립 구현과 비교하면 비트 분기 오류를 찾는 데 도움이 됩니다.')],
    [('int_pow(0,0)의 실제 반환값은?', '1', '오류 코드', 'result를1로 초기화하고 exp가0이면 반복에 들어가지 않습니다. 수학에서의 관례와 별개로 코드의 반환 규약입니다.'),
     ('5의5승 계산에서 exp=2인 반복은 result에 base를 곱하는가?', '아니다. 최하위 비트가0이다', '그렇다. 모든 반복에서 result를 곱한다', 'exp&1이 거짓이면 result를 유지하고 exp 시프트와 base 제곱만 수행합니다.'),
     ('u64 결과로 int_pow(2,64)는?', '0', '정확한2^64를 그대로 반환한다', 'u64의 표현 범위는0부터2^64-1입니다. unsigned 곱셈은2^64를 법으로 순환하며 별도 오버플로 오류 반환이 없습니다.')])

add('lib/math/int_sqrt.c', '정수 제곱근 전체: 4의 거듭제곱 단위로 답을 구성하기',
    '부동소수점 없이 floor(sqrt(x))를 구하는 shift-and-subtract 알고리즘입니다.',
    'x<=1을 먼저 반환하고 x 이하 최대4의 거듭제곱 m을 선택합니다. 매 반복 b=y+m을 만든 뒤 y를 반으로 줄입니다. x>=b이면 x에서 b를 빼고 y에 m을 더합니다. m은 두 비트씩 줄어듭니다.',
    '반환값 r은 원래 입력 X에 대해 r²<=X<(r+1)²를 만족하는 정수입니다. x 변수는 계산 중 잔여량으로 바뀌므로 원래 입력과 혼동하지 않습니다.',
    [('파일 전체와 폭별 구현', 'SPDX·유래 주석, export/bitops/limits/math 포함, int_sqrt와 export, BITS_PER_LONG<64 조건부 int_sqrt64와 export로 구성됩니다. 64비트 long에서는 이 C 파일에 int_sqrt64 본문이 없고 math.h의 인라인 경로가 int_sqrt를 호출합니다.'),
     ('초기 비트 선택', '__fls(x)는 가장 높은1비트의0기반 위치입니다. &~1UL은 그 위치를 짝수로 내리고 1UL을 그만큼 옮겨4^k를 만듭니다. x<=1 분기를 먼저 통과하므로 __fls(0)을 호출하지 않습니다. fls64는1기반이므로 넓은 경로에서는1을 뺀 다음 같은 처리를 합니다.'),
     ('입력10의 모든 반복', '초기 x=10,y=0,m=4입니다. b=4를 만들고 y=0, x>=4이므로 x=6,y=4,m=1이 됩니다. 다음 b=5,y=2이고 x>=5이므로 x=1,y=3,m=0입니다. 최종3은9<=10<16을 만족합니다.'),
     ('32비트 long에서64비트 입력', 'int_sqrt64는 x<=ULONG_MAX이면 int_sqrt로 위임합니다. 더 크면 u64 b,m,y를 사용하여 같은 알고리즘을 실행하고 u32를 반환합니다. 최대 u64의 정수 제곱근은2^32-1이므로 결과 타입에 들어갑니다.'),
     ('검증과 복잡도', '한 반복마다 m을2비트 줄여 비트 폭에 비례하는 시간, O(1) 공간을 씁니다. 검증에서 (r+1)*(r+1)을 같은 좁은 타입으로 계산하면 최대값 부근에서 검증식 자체가 넘칠 수 있습니다. 독립 이진 탐색 참조에서는 mid<=X/mid처럼 나눗셈 비교를 사용하면 곱 오버플로를 피할 수 있습니다.')],
    [('입력10의 반환값은?', '3', '4', '반올림이 아니라 내림 제곱근입니다.3²=9<=10이고4²=16>10입니다.'),
     ('m을 매 반복 두 비트 줄이는 이유는?', '4의 거듭제곱 단계를 하나 내려가기 때문이다', '입력 x를 무조건4로 나누기 때문이다', 'm>>=2는 후보 자리의 축소입니다. x는 조건에 따라 b를 빼는 잔여량이며 매번4로 나누지 않습니다.'),
     ('최대 u64의 int_sqrt64 결과가 u32에 들어가는가?', '들어간다. 결과는2^32-1이다', '들어가지 않는다. 결과도64비트가 필요하다', '(2^32)²은2^64로 입력 최대값보다 큽니다. 따라서 내림 제곱근의 최대값은2^32-1입니다.')])

add('lib/math/tests/int_pow_kunit.c', '거듭제곱 KUnit 파일 전체: 표 기반 검증과 커버리지 한계',
    '테스트의 존재와 모든 경계 조건의 검증을 구분합니다.',
    '입력 base·exponent·expected_result·name을 구조체 배열로 정의하고 KUNIT_ARRAY_PARAM으로 파라미터 생성기를 만듭니다. 각 실행은 param_value의 기대값과 int_pow 결과를 비교합니다.',
    '9개 명시적 사례는 지수0/1, 밑0/1,2²,2³,5⁵,최대 밑의1승,2^63입니다. 이 목록만으로 모든64비트 입력을 증명하지 않습니다.',
    [('데이터와 설명 생성', 'SPDX, kunit/test.h와 linux/math.h, test_case_params 정의, const params[9]가 있습니다. get_desc는 이름을 KUNIT_PARAM_DESC_SIZE 제한으로 strscpy하여 각 파라미터 실행의 설명을 제공합니다. 이름은 계산 결과가 아니라 출력 식별용입니다.'),
     ('실행 경로', 'KUNIT_ARRAY_PARAM(int_pow,params,get_desc)가 생성한 int_pow_gen_params를 KUNIT_CASE_PARAM에 연결합니다. int_pow_test는 test->param_value를 해당 구조체 포인터로 해석하고 KUNIT_EXPECT_EQ로 기대값과 실제 반환값을 비교합니다.'),
     ('등록과 종료 표식', 'kunit_case 배열의 빈 {}가 종료 표식입니다. math-int_pow라는 suite는 그 배열을 참조하고 kunit_test_suites로 등록됩니다. 마지막 MODULE_DESCRIPTION과 GPL MODULE_LICENSE는 모듈 메타데이터입니다.'),
     ('빠진 경계도 학습하기', '표에는0^0,2^64의 순환 결과, 여러 비트가 켜진 큰 지수의 폭넓은 조합이 없습니다. U64_MAX의1승 사례는 반환 최대값을 확인하지만 모든 오버플로 처리를 검증하지 않습니다. 실행한 테스트 수와 입력 공간 커버리지는 별개입니다.')],
    [('이 파일의 명시적 입력 사례 개수는?', '9개', '64개', 'params 배열의9개 행이 각각 base/exponent/expected/name을 담습니다. 지수64라는 값이 테스트 수64라는 뜻은 아닙니다.'),
     ('2^63 통과만으로2^64 동작도 검증했다고 할 수 있는가?', '없다. 표현 범위를 넘는 별도 경계 사례다', '있다. 가까운 입력이면 모든 경계가 같다', '2^63은 u64에 들어가지만2^64는 순환합니다. 실제 표에 없는 사례까지 통과했다고 주장할 수 없습니다.'),
     ('get_desc가 거듭제곱 기대값을 계산하는가?', '아니다. 사례의 이름을 설명 버퍼에 복사한다', '그렇다. 독립적인 거듭제곱 참조 구현이다', '기대값은 params에 직접 저장되어 있고 get_desc는 strscpy만 호출합니다.')])

add('lib/math/Makefile', '수학 라이브러리 빌드 목록 전체: 기본 객체와 설정별 객체',
    '코드가 저장소에 있다는 것과 선택한 커널에 포함된다는 것을 구분합니다.',
    'obj-y에 div64,gcd,lcm,int_log,int_pow,int_sqrt,reciprocal_div 객체를 추가합니다. 나머지는 CONFIG 값에 따라 obj-y 또는 obj-m 등에 배치됩니다.',
    '상위 lib/Makefile이 math/를 포함합니다. 이 파일은 함수 알고리즘이나 테스트 실행 결과를 정의하지 않고 Kbuild의 객체 선택을 지정합니다.',
    [('전체 기본 목록', 'SPDX 다음 기본7개 객체가 한 줄에 있습니다. 목록의 .o는 대응 소스의 빌드 산출물 이름입니다. 이 하위 디렉터리를 처리하는 빌드 문맥에서 obj-y로 선택된다는 의미입니다.'),
     ('기능 선택3개', 'CONFIG_CORDIC은 cordic.o, CONFIG_PRIME_NUMBERS는 prime_numbers.o, CONFIG_RATIONAL은 rational.o를 선택합니다. tristate가 y이면 built-in 쪽, m이면 모듈 쪽에 들어가며 비활성 설정은 활성 객체 목록에 추가되지 않습니다.'),
     ('테스트 선택4개', 'CONFIG_INT_POW_TEST는 tests/int_pow_kunit.o를 이 파일에서 직접 가리킵니다. TEST_DIV64는 test_div64.o, TEST_MULDIV64는 test_mul_u64_u64_div_u64.o, RATIONAL_KUNIT_TEST는 rational-test.o입니다. tests/Makefile의 존재만으로 이 직접 경로를 별도 테스트 두 번 실행으로 세면 안 됩니다.'),
     ('빌드와 실행 구분', '설정이 객체를 선택해도 테스트가 실행되어 성공했다는 증거는 아닙니다. 해당 설정 정의는 lib/Kconfig.debug에도 연결되어 있습니다. Makefile 목록, 최종 설정, 빌드 로그, 테스트 실행 로그는 서로 다른 단계의 증거입니다.')],
    [('int_pow.o와 int_pow_kunit.o의 선택 조건은 같은가?', '아니다. 구현은 기본 목록이고 테스트는 INT_POW_TEST 조건이다', '그렇다. 테스트를 켜야 구현도 생긴다', '기본 obj-y 줄에 int_pow.o가 있고 테스트 줄은 obj-$(CONFIG_INT_POW_TEST)입니다.'),
     ('이 Makefile을 읽으면 테스트 성공을 알 수 있는가?', '없다. 객체 선택과 테스트 실행 결과는 별개다', '있다. 목록에 테스트가 있으면 이미 통과했다', '빌드 선언은 실행 로그가 아닙니다. 성공 주장은 실제 빌드·실행 근거가 필요합니다.')])

add('lib/math/tests/Makefile', '수학 테스트 하위 Makefile 전체: 상대 경로와 빌드 진입점',
    '두 줄짜리 파일도 상위 디렉터리와의 연결을 확인해야 의미가 분명해집니다.',
    'SPDX 이후 obj-$(CONFIG_INT_POW_TEST)에 int_pow_kunit.o를 추가하는 한 규칙이 전부입니다.',
    '이 디렉터리의 Kbuild 문맥에서 읽힐 때의 규칙입니다. 상위 lib/math/Makefile은 같은 테스트를 tests/int_pow_kunit.o 경로로 직접 선택합니다.',
    [('전체 파일', '라이선스 주석, 빈 줄, 조건부 객체 추가 한 줄입니다. 별도 타깃 recipe나 셸 명령, 실행 순서, 기대 결과는 없습니다.'),
     ('경로의 문맥', '여기서는 int_pow_kunit.o이지만 부모에서는 tests/int_pow_kunit.o입니다. 파일 이름이 달라 보인다고 서로 다른 테스트 구현이 되는 것은 아닙니다. Kbuild가 어느 디렉터리의 목록을 처리하는지 함께 봐야 합니다.'),
     ('연결 검토와 CS', '부모에 obj-y += tests/가 있다고 추정해서는 안 됩니다. 고정 버전의 부모는 테스트 객체를 직접 나열합니다. 빌드 그래프의 선언과 도달 가능성을 구분하고, 중복된 경로 표현을 테스트 개수로 중복 집계하지 않습니다.')],
    [('이 파일 자체가 테스트를 실행하는 셸 명령을 포함하는가?', '아니다. 조건부 객체 목록만 있다', '그렇다. int_pow를 직접 호출한다', 'obj-$(CONFIG_INT_POW_TEST) += int_pow_kunit.o는 Kbuild 변수 추가입니다. 함수 호출이나 테스트 실행 recipe가 아닙니다.'),
     ('부모의 tests/int_pow_kunit.o와 이곳의 int_pow_kunit.o는?', '디렉터리 문맥을 고려하면 같은 테스트 객체를 가리킨다', '이름이 다르므로 반드시 서로 다른 테스트다', '상대 경로의 기준이 다릅니다. 소스 위치와 부모 규칙을 함께 대조해야 합니다.')])

add('lib/math/Kconfig', '수학 Kconfig 전체: 보이는 tristate와 숨은 라이브러리 설정',
    '선택 메뉴 문구와 설정 심벌의 존재를 구분합니다.',
    'CORDIC과 PRIME_NUMBERS는 표시 문구가 있는 tristate이고 도움말을 제공합니다. RATIONAL은 표시 문구 없는 tristate 선언만 있습니다.',
    '세 심벌은 lib/math/Makefile의 해당 객체 선택에 사용됩니다. 이 파일에 없는 의존성·기본값·테스트 설정을 추측해서 덧붙이지 않습니다.',
    [('CORDIC', 'CORDIC algorithm이라는 표시 문구와 고정소수점 계산 설명, cordic이라는 모듈 이름 설명이 있습니다. 이 도움말은 알고리즘이 부동소수점 런타임을 사용한다고 말하지 않습니다.'),
     ('PRIME_NUMBERS', 'Simple prime number generator for testing이라는 문구와 테스트 모듈용 소수 생성기 설명이 있습니다. If unsure, say N은 사용자 안내이며 별도의 default n 선언 문법은 아닙니다.'),
     ('RATIONAL과 파일 경계', 'RATIONAL에는 prompt도 help도 default도 없습니다. 따라서 이 선언만으로 사용자가 메뉴에서 직접 켜는 항목이라고 말할 수 없습니다. 다른 설정의 select 등과 빌드 사용처를 별도로 추적해야 합니다. INT_POW_TEST를 비롯한 테스트 심벌은 이 파일에 선언되어 있지 않습니다.')],
    [('이 파일의 RATIONAL에 메뉴 표시 문구가 있는가?', '없다. prompt 없는 tristate 선언이다', '있다. Rational algorithm이라고 적혀 있다', '고정 원문은 config RATIONAL 다음 tristate만 있습니다. 없는 문구를 만들어 설명하면 안 됩니다.'),
     ('PRIME_NUMBERS 도움말의 If unsure, say N은 default 문법인가?', '아니다. 도움말에 적힌 사용자 안내다', '그렇다. Kconfig의 default 선언과 같은 문법이다', 'help 블록의 자연어와 Kconfig 키워드 선언을 구분해야 합니다.')])
