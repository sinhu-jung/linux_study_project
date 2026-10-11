"""Whole RISC-V counter-based delay implementation and declarations."""
ROWS = [dict(
    path='arch/riscv/lib/delay.c',
    title='RISC-V 지연 전체: counter 차이와 두 가지 단위 변환',
    intro='마이크로초·나노초를 counter tick으로 바꾸고 busy wait하는 세 함수를 해설합니다.',
    principle='고정소수점 변환과 직접 주파수 변환은 다른 경로이며 계산 중간값의 타입 폭도 결과에 영향을 줍니다.',
    use='ARM의 상수 제한 및 지연 연산 테이블과 달리 이 구현이 큰 usecs를 어떻게 처리하는지 비교합니다.',
    area='Counter · 고정소수점 · 정수 나눗셈 · 타입 승격 · 모듈러 산술',
    sections=[
        ('파일 구성', 'GPL-2.0-only·저작권 뒤 delay/math/param/timex/types/export와 processor 헤더를 포함합니다. 두 단위의 변환 상수·HZ 검사와 __delay,udelay,ndelay 구현 및 EXPORT_SYMBOL이 전체입니다. sleep이나 타이머 인터럽트 등록은 없습니다.'),
        ('마이크로초 고정소수점', 'ARM 유래 주석은 loops_per_jiffy*HZ*usecs/1000000을2^31 scale로 계산하는 유도를 설명합니다. UDELAY_MULT는2147UL*HZ+483648UL*HZ/1000000UL,SHIFT는31,MAX_UDELAY_US는2000,MAX_UDELAY_HZ는1000입니다. HZ가 상한을 넘으면 #error입니다. 실제 함수는 보정값으로 lpj_fine을 사용합니다.'),
        ('나노초 상수와 제한', 'NDELAY_MULT는2199ULL*HZ+23255550ULL*HZ/1000000000ULL을 unsigned long long으로 표현하고 SHIFT는41입니다. HZ 상한은 마이크로초와 같아 별도 #error가 있습니다. MAX_NDELAY_NS는1ULL<<42로 정의되지만 ndelay에서 검사하거나 큰 입력을 분할하는 데 사용하지 않습니다. 주석의 긴 시간이라 overflow를 검사하지 않는다는 설명을 검사 구현으로 오인하면 안 됩니다.'),
        ('Counter 차이를 기다리기', '__delay는 get_cycles 값을 u64 t0에 저장하고 (unsigned long)(get_cycles()-t0)가 요청 cycles보다 작은 동안 cpu_relax합니다. 비교 전에 unsigned long으로 변환하므로 실제 비교 폭은 아키텍처 word 크기에 영향을 받습니다. 요청0에서는 조건이 처음부터 거짓입니다. counter가 진행한다는 전제와 폭 제한 없이 임의 길이를 보장하는 함수가 아닙니다.'),
        ('짧은 udelay', 'udelay는 (u64)usecs*lpj_fine*UDELAY_MULT를 u64 ucycles에 계산합니다. usecs가2000 이하이면 이를31비트 이동해 __delay로 넘깁니다. 맨 앞 cast가 중간 곱셈도64비트로 수행되게 한다는 점을 단순히 결과 변수의 타입이64비트라는 사실과 구분합니다.'),
        ('큰 udelay의 직접 변환', 'usecs>2000이면 n=(u64)usecs*riscv_timebase를 구하고 do_div(n,1000000)으로 n을 몫으로 갱신합니다. __delay(n) 후 반환하므로 고정소수점 경로는 사용하지 않습니다. 정확히2000은 짧은 경로입니다. ARM 헤더의 잘못된 상수 호출 감지와 달리 이 파일은 큰 입력용 실행 분기를 가집니다.'),
        ('Ndelay 계산 순서의 주의', 'ndelay는 unsigned long long ncycles=nsecs*lpj_fine*NDELAY_MULT를 계산해41비트 이동합니다. nsecs와 lpj_fine은 unsigned long이므로 C의 왼쪽 결합상 첫 곱은 그 타입에서 먼저 계산되고 이후 NDELAY_MULT의64비트 타입과 결합합니다. 특히32비트에서 결과 변수만64비트라고 첫 곱의 overflow까지 자동 방지되는 것은 아닙니다. 이 본문에는 overflow 검사나 긴 입력용 대체 분기가 없습니다.'),
        ('Tick·시간·원자성 구별', '세 함수는 counter 기반 busy wait이며 CPU를 sleep시키지 않습니다. 반환할 때 장치 상태를 확인하거나 메모리 장벽을 추가하는 코드도 없습니다. counter 주파수와 lpj_fine이 적절해야 시간 변환이 의미 있고 정수 절삭·호출 비용·실행 환경 때문에 정확한 실제 시간 보장을 이 식만으로 증명할 수 없습니다.'),
        ('CS 연결과 검증 범위', '단위 분석,고정소수점 scale,큰 입력의 별도 알고리즘,do_div의 인자 갱신,타입 승격 시점,word 폭과 counter 차이를 학습합니다. 이 자료는 원본 기반 해설이며 실제 RISC-V counter나32/64비트 하드웨어 시간을 측정한 결과가 아닙니다.')
    ],
    questions=[
        ('udelay(2001)은 어떤 변환을 사용하는가?', 'riscv_timebase 곱을1000000으로 나누는 경로이다', '항상 UDELAY_SHIFT 경로만 사용한다', '조건은 usecs>2000입니다. 큰 요청은 직접 주파수 변환 뒤 __delay를 호출하고 반환합니다.'),
        ('MAX_NDELAY_NS가 실제 입력 거부 조건에 쓰이는가?', '아니다. 상수는 있지만 ndelay에 검사가 없다', '그렇다. 초과하면 오류 코드를 반환한다', '함수는 곱셈·이동·__delay만 수행하며 반환형도void입니다. 주석과 상수 존재를 실행 검사로 혼동하지 않아야 합니다.'),
        ('ndelay의64비트 결과 변수만으로 nsecs*lpj_fine 첫 곱의32비트 overflow를 막는가?', '아니다. 첫 곱의 피연산자 타입과 평가 순서를 봐야 한다', '그렇다. 대입 대상이 모든 중간식을64비트로 바꾼다', 'C는 대입 대상 타입을 거슬러 올라가 중간 곱의 타입을 변경하지 않습니다. udelay의 맨 앞 u64 cast와 차이가 있습니다.'),
        ('__delay(0)은 반복 대기하는가?', '아니다. unsigned 차이가0보다 작을 수 없다', '그렇다. counter 한 바퀴를 기다린다', '루프 조건이 unsigned 비교의 <cycles이므로 cycles0이면 처음 검사에서 종료됩니다.')
    ]
), dict(
    path='arch/riscv/include/asm/delay.h',
    title='RISC-V 지연 헤더 전체: 독립 함수와 기능 표시',
    intro='timebase 선언과 세 지연 함수,공통 fallback을 막는 매크로를 읽습니다.',
    principle='자기참조 매크로는 함수 호출을 재귀로 바꾸는 것이 아니라 전처리 정의 여부를 표시할 수 있습니다.',
    use='공통 delay.h의 ndelay fallback과 RISC-V 전용 구현 선택을 연결합니다.',
    area='전처리기 · extern 선언 · 시간 단위 · 아키텍처 인터페이스',
    sections=[
        ('파일 전체 구성', 'GPL-2.0-only와 두 저작권,guard 뒤 extern unsigned long riscv_timebase,udelay·ndelay의 자기참조 매크로와 함수 선언,__delay 선언이 전부입니다. 실제 변수 정의·초기화나 counter 접근 명령은 없습니다.'),
        ('단위와 타입', 'udelay는 unsigned long usecs,ndelay는 unsigned long nsecs,__delay는 unsigned long cycles를 받으며 모두void입니다. 같은 정수 타입을 쓰더라도 입력 단위는 다릅니다. riscv_timebase의 실사용은 구현의 큰 udelay 주파수 변환에서 확인할 수 있습니다.'),
        ('자기참조 매크로', '#define udelay udelay와 ndelay 대응은 전처리 단계에서 해당 이름의 제공 여부를 알립니다. 공통 delay.h의 #ifndef ndelay fallback이 생기지 않도록 하는 효과가 있습니다. 이 매크로 자체가 무한 재귀 호출이나 함수 본문을 생성하지 않습니다.'),
        ('선언의 한계', '이 헤더에는 ARM과 같은 MAX_UDELAY_MS 재정의,상수 입력 검사,함수 포인터 테이블이 없습니다. 선언만으로 큰 값의 overflow나 정확한 지연 시간을 보증할 수 없으며 lib/delay.c의 분기와 계산을 함께 읽어야 합니다.')
    ],
    questions=[
        ('ndelay 자기참조 매크로가 공통 헤더에 미치는 효과는?', 'ndelay가 제공됐음을 표시해 fallback 정의를 막는다', '실행 중 무한 재귀를 만든다', '전처리 #ifndef가 정의 여부를 봅니다. 실제 실행은 별도로 선언·정의한 함수의 본문입니다.'),
        ('__delay와 udelay의 인자 단위는 같은가?', '아니다. 각각 cycles와 마이크로초이다', '그렇다. 둘 다 항상 나노초이다', '헤더의 인자 이름과 구현의 변환 과정을 연결합니다. 같은 unsigned long 타입이라고 같은 물리 단위는 아닙니다.')
    ]
)]
