"""Whole-file jiffies clocksource and build-time conversion generator."""
ROWS = [dict(
    path='kernel/time/jiffies.c', title='Jiffies 시계: 기본 clocksource와 tick 주기 보정',
    intro='기본 clocksource 등록, 32비트의 일관된 읽기, refined-jiffies 계산을 전체 소스로 분석합니다.',
    principle='기본 tick 카운터에 변환 계수를 붙여 시간을 표현하고, 폭이 큰 공유 값은 일관된 관측 방법을 사용합니다.',
    use='정밀한 하드웨어 시계가 없을 때의 대체 시계와 주파수 환산 보정의 한계를 이해합니다.',
    area='Clocksource · tick · seqcount · 고정 소수점 · 초기화 · 반올림',
    sections=[
        ('파일 전체', 'GPL-2.0+와 저작권 주석, clocksource/jiffies/module/init 및 두 내부 헤더 include 뒤 읽기 callback, 기본 clocksource, lock과 seqcount, 조건부 get_jiffies_64, 등록·기본값 함수, refined 등록 함수가 있습니다. jiffies를 증가시키는 timer interrupt 본문은 이 파일에 없습니다.'),
        ('기본 읽기 callback', 'jiffies_read는 전달된 clocksource 포인터를 사용하지 않고 jiffies를 u64로 변환하여 반환합니다. 이름이 비슷한 get_jiffies_64를 호출하지 않습니다. 기본 clocksource의 mask는 CLOCKSOURCE_MASK(32)이므로 callback 반환형이 u64라는 것만으로 64비트 전체 회전 범위를 사용한다고 설명하면 안 됩니다.'),
        ('기본 clocksource의 모든 설정', '이름은 jiffies, rating은 1, uncertainty_margin은 32*NSEC_PER_MSEC입니다. read는 앞의 callback, mask는 32비트, mult는 TICK_NSEC<<JIFFIES_SHIFT, shift는 JIFFIES_SHIFT, max_cycles는 10입니다. mult와 shift가 나노초 환산을 짝으로 표현합니다. rating=1은 주석상 가장 낮은 유효 등급이며 uncertainty_margin은 실측 오차가 항상 정확히 32ms라는 뜻이 아닙니다.'),
        ('기본 시계의 한계', '주석은 timer interrupt의 HZ와 같은 거친 해상도, 놓친 interrupt와 정확한 HZ 발생의 한계에 의한 부정확성을 설명하고 tickless 시스템에 권장하지 않는다고 합니다. 범용 대체 수단이라는 점과 정밀 시간원이라는 주장은 다릅니다. max_cycles=10을 timer가 열 번만 실행되고 멈춘다는 뜻으로 읽지 않습니다.'),
        ('공유 상태의 동기화 객체', 'jiffies_lock은 raw spinlock이며 jiffies_seq는 그 lock에 연결한 seqcount_raw_spinlock_t로 초기화됩니다. 둘 다 SMP에서 cacheline 정렬 속성을 가집니다. 이 파일은 객체를 정의하지만 매 tick의 writer 갱신 코드를 실행하는 곳은 아닙니다. 연관 lock이 있는 seqcount와 값 자체의 atomic 폭을 구분합니다.'),
        ('32비트 long에서 64비트 읽기', 'BITS_PER_LONG<64일 때 get_jiffies_64는 read_seqcount_begin으로 시작 상태를 읽고 jiffies_64를 복사한 뒤 read_seqcount_retry가 요구하면 반복합니다. 두 워드로 읽는 도중 writer 갱신이 끼어든 결과를 그대로 반환하지 않도록 합니다. reader가 jiffies_lock을 직접 잡는 코드는 아니며 지속적인 갱신 아래 항상 한 번에 끝난다는 보장도 아닙니다.'),
        ('등록과 weak 기본값', '32비트 get_jiffies_64와 jiffies는 일반 EXPORT_SYMBOL입니다. init_jiffies_clocksource는 __clocksource_register 결과를 그대로 반환하며 core_initcall로 등록됩니다. __init __weak clocksource_default_clock는 기본 객체 주소를 반환합니다. weak 기본 구현이라는 점은 다른 구현이 대체할 수 있음을 뜻하며 반환 자체가 동적 최적 시계 탐색을 수행하는 것은 아닙니다.'),
        ('Refined 객체 준비', '정적 refined_jiffies를 두고 register_refined_jiffies가 기본 clocksource 전체를 복사합니다. 이름을 refined-jiffies로 바꾸고 rating을 하나 올려 2로 만듭니다. callback과 mask 등 나머지 설정은 복사된 상태이며 하드웨어 레지스터를 새로 읽는 callback으로 바뀌지 않습니다.'),
        ('Tick당 cycle 추정', 'cycles_per_tick=(cycles_per_second+HZ/2)/HZ로 가까운 정수 cycle 수를 계산합니다. 다음 shift_hz는 (u64)cycles_per_second<<8에 cycles_per_tick/2를 더해 cycles_per_tick으로 나눕니다. 이는 실제 cycle 수를 기준으로 tick 주파수에 8비트 분수 정밀도를 주는 계산입니다. 모든 단계가 항상 정확히 HZ<<8이라는 뜻은 아닙니다.'),
        ('보정된 나노초 계수', 'nsec_per_tick=(u64)NSEC_PER_SEC<<8에 (u32)shift_hz/2를 더하고 (u32)shift_hz로 나눕니다. 그 결과를 u32로 줄여 JIFFIES_SHIFT만큼 왼쪽 이동한 값을 refined_jiffies.mult에 저장합니다. 원래 shift는 그대로 사용합니다. 두 나눗셈에서 반올림 항을 사용하지만 임의로 큰 입력의 축소·곱셈·시프트 overflow를 검사하는 코드는 없습니다.'),
        ('입력과 오류 반환의 한계', 'cycles_per_second는 long이며 양수와 계산 중 제수의 비영 조건을 별도로 검사하지 않습니다. 잘못된 작은 값이면 cycles_per_tick=0이 될 수 있으므로 정상적인 하드웨어 주파수 입력이 전제입니다. 마지막 __clocksource_register의 반환값은 버리고 함수는 0을 반환합니다. 기본 init 함수와 refined 등록 함수의 오류 전달이 같지 않습니다.'),
        ('CS와 검증 범위', '샘플 카운터의 폭, seqcount를 통한 일관된 읽기, weak 기본값, 고정 소수점 변환, 반올림과 입력 전제, 내부 오류와 공개 반환값의 차이를 학습합니다. 이 해설은 실제 시스템 시계 선택이나 IRQ 유실 실험을 실행한 결과가 아닙니다.')
    ],
    questions=[
        ('jiffies_read는 get_jiffies_64를 호출하는가?', '아니다. jiffies를 u64로 변환해 반환한다', '그렇다. 모든 경로에서 64비트 전체 카운터를 seqcount로 읽는다', 'callback 본문과 별도의 32비트 get_jiffies_64는 다른 함수입니다. clocksource mask도 32비트로 설정됩니다.'),
        ('32비트 get_jiffies_64가 갱신 중 읽은 값을 감지하면?', 'seqcount 검사에 따라 다시 읽는다', 'reader가 무조건 jiffies_lock을 획득해 writer를 종료한다', 'read_seqcount_begin/read_seqcount_retry 루프이며 reader의 직접 spin_lock 호출은 없습니다.'),
        ('refined-jiffies는 새로운 하드웨어 read callback을 설치하는가?', '아니다. 기본 객체를 복사하고 변환 계수 등을 조정한다', '그렇다. jiffies 대신 CPU cycle register를 직접 읽는다', '이 함수가 바꾸는 것은 name, rating, mult입니다. callback은 복사된 jiffies_read입니다.'),
        ('register_refined_jiffies는 내부 등록 오류를 그대로 반환하는가?', '아니다. 등록 함수를 호출한 뒤 0을 반환한다', '그렇다. init_jiffies_clocksource와 같은 반환식이다', '두 함수의 본문을 비교해야 합니다. 기본 init은 return __clocksource_register이고 refined는 결과를 사용하지 않습니다.'),
        ('uncertainty_margin=32ms는 모든 실제 측정 오차가 정확히 32ms임을 뜻하는가?', '아니다. clocksource에 설정하는 여유 값이다', '그렇다. 하드웨어가 오차를 항상 그 값으로 고정한다', '이 파일은 실측이나 보정을 통해 오차를 고정하지 않습니다. 주석은 interrupt 기반 시계의 여러 부정확성 요인을 설명합니다.')
    ]
), dict(
    path='kernel/time/timeconst.bc', title='시간 변환 상수 생성기: 최대공약수와 역수 곱셈',
    intro='bc 스크립트 전체를 읽어 HZ별 분수와 MUL·ADJ·SHR 상수가 만들어지는 과정을 학습합니다.',
    principle='빌드 시 정수 산술로 변환 계수를 계산하여 런타임 코드에서 상수 곱셈과 시프트를 사용할 수 있게 합니다.',
    use='generated/timeconst.h의 값이 어디서 오는지와 단위 변환의 반올림·정확도 전제를 이해합니다.',
    area='빌드 도구 · 유클리드 알고리즘 · 기약분수 · 고정 소수점 · 코드 생성',
    sections=[
        ('파일 전체 실행 흐름', 'GPL-2.0 표시 뒤 scale=0을 설정하고 gcd, fmul, fadj, fmuls, timeconst 다섯 함수를 정의합니다. 마지막 hz=read()로 입력을 읽어 timeconst(hz)를 호출합니다. 출력은 C 헤더 텍스트이며 스크립트가 직접 커널 시계를 변경하거나 파일 경로를 열어 쓰는 코드는 없습니다.'),
        ('정수 산술 환경', 'scale=0은 나눗셈을 정수 자리까지 계산하도록 합니다. 여기의 ^는 bc 거듭제곱이므로 2^b는 2의 b승입니다. C 언어의 XOR 연산으로 읽으면 모든 생성식을 잘못 해석하게 됩니다. C의 고정 폭 정수식과 bc의 수 계산 환경을 구분합니다.'),
        ('Gcd 유클리드 알고리즘', 'gcd는 b가 0이 될 때까지 t=b, b=a%b, a=t를 반복하고 a를 반환합니다. 양의 HZ와 단위 배율에서 분자·분모의 공통 인수를 제거하는 데 사용됩니다. 나머지가 줄어드는 유클리드 알고리즘이며 모든 약수를 선형 탐색하는 방식이 아닙니다.'),
        ('올림된 역수 곱 계수', 'fmul(b,n,d)는 (2^b*n+d-1)/d를 반환합니다. 양의 d와 비음수 분자에 대해 ceil(2^b*n/d)에 해당합니다. 런타임의 n/d 비율을 정수 곱과 오른쪽 shift로 근사할 때 사용하는 계수입니다. 이 함수 자체가 실제 입력 jiffies를 변환하지는 않습니다.'),
        ('조정 계수', 'fadj는 d를 d/gcd(n,d)로 줄인 뒤 2^b*(d-1)/d의 정수 몫을 반환합니다. 예를 들어 n/d=1000/300이면 줄인 분모는 3입니다. d가 1로 줄면 조정 계수는 0입니다. 원본 분자와 분모가 아니라 약분한 분모를 쓰는 점이 중요하며 생성된 ADJ를 어느 변환에 더하는지는 소비 코드가 정합니다.'),
        ('시프트 탐색', 'fmuls는 s=0부터 fmul(s,n,d)를 구하다 값이 2^(b-1) 이상이면 s를 반환합니다. 사용처는 b=32이므로 실제 비교 기준은 2^31입니다. 주석의 하한 표기 2^b-1을 문자 그대로 2^b에서 1을 뺀 값으로 읽으면 본문의 2^(b-1)과 다릅니다. 주석은 signed 범위의 정확성과 unsigned 상위 절반의 최대 1 오차를 설명하지만 소비 연산의 입력 범위·overflow를 모두 검증하는 함수는 아닙니다.'),
        ('출력 헤더의 자기 검증', 'timeconst는 자동 생성 주석과 사용 HZ, KERNEL_TIMECONST_H guard, linux/param.h와 types.h include를 출력합니다. 이어 #if HZ != 입력값과 #error를 출력해 다른 설정에서 생성된 헤더 사용을 막습니다. 잘못된 HZ를 런타임에 발견하는 기능이 아니라 생성물의 컴파일 단계 검사입니다.'),
        ('잘못된 HZ 분기', 'hz<2이면 Totally bogus HZ value라는 #error 줄을 출력합니다. 정상 분기의 나머지 상수와 마지막 #endif는 출력하지 않고 함수 끝 halt로 종료합니다. 잘못된 입력에서도 정상적으로 사용할 수 있는 완성 헤더를 생성하거나 자동으로 HZ를 교정하지 않습니다.'),
        ('밀리초 양방향 상수', '정상 경로는 n/d=1000/hz와 hz/1000 각각에 대해 fmuls(32,...)로 s를 구하고 MUL32, ADJ32, SHR32를 출력합니다. 이름은 HZ_TO_MSEC와 MSEC_TO_HZ입니다. 이어 gcd(hz,1000)으로 약분하여 두 방향의 NUM과 DEN을 출력합니다. HZ=300이면 정방향 분수는 10/3, 역방향은 3/10입니다.'),
        ('진법 전환', 'MUL32와 ADJ32 출력 전 obase=16으로 바꾸어 U64_C(0x...) 형태의 16진수 C 상수를 만듭니다. shift와 분수 출력에는 obase=10으로 돌아갑니다. 이는 출력 숫자의 표기를 바꾸는 것이며 HZ를 16진수로 다시 해석하거나 커널 계산 단위를 바꾸는 연산이 아닙니다.'),
        ('마이크로초와 나노초 상수', '1000000/hz와 hz/1000000에 대해 같은 MUL32/ADJ32/SHR32 및 약분한 NUM/DEN 쌍을 만듭니다. 마지막 나노초는 gcd(hz,1000000000)을 이용한 HZ_TO_NSEC와 NSEC_TO_HZ의 NUM/DEN만 출력합니다. 이 파일은 나노초용 MUL32/ADJ32/SHR32 묶음을 생성하지 않습니다.'),
        ('종료와 소비 코드 관계', '정상 분기는 헤더 guard를 닫고 timeconst 끝에서 halt합니다. read는 한 번이며 여러 HZ를 자동 순회하는 스크립트가 아닙니다. 생성 상수는 time.c나 jiffies 헤더의 설정별 식에서 사용되므로 ADJ가 생성됐다고 모든 소비 식이 반드시 ADJ를 더하는 것은 아닙니다.'),
        ('CS와 검증 범위', '빌드 시 계산과 런타임 계산의 분리, 유클리드 약분, 정수 올림, 역수 곱셈, 언어별 연산자 차이와 생성물 설정 일치 검사를 학습합니다. 전체 스크립트를 소스로 대조했지만 모든 가능한 HZ에 대해 bc 실행과 생성 C 산술을 전수 검증한 결과는 아닙니다.')
    ],
    questions=[
        ('이 스크립트의 2^b에서 ^는 무엇인가?', 'bc의 거듭제곱 연산이다', 'C와 같은 비트 XOR이다', '파일 언어는 bc입니다. 역수 곱셈 계수를 계산하려면 2의 b승이 필요합니다.'),
        ('HZ=300이면 HZ_TO_MSEC의 약분된 NUM/DEN은?', '10/3이다', '3/10이다', '1000/300을 최대공약수 100으로 나눕니다. 3/10은 밀리초에서 HZ tick으로 돌아가는 역방향입니다.'),
        ('fmuls(32,n,d)가 비교하는 실제 계수 하한은?', '2^31이다', '2^32-1이다', '본문은 2^(b-1)과 비교합니다. 주석의 괄호 없는 지수 표기를 실제 코드보다 우선해 해석하면 안 됩니다.'),
        ('나노초 변환에도 이 생성기가 MUL32/ADJ32/SHR32를 출력하는가?', '아니다. 나노초에는 약분한 NUM/DEN 쌍을 출력한다', '그렇다. 모든 단위에 동일한 매크로 묶음을 출력한다', '마지막 블록은 gcd와 네 분수 매크로만 있습니다. 반복 패턴을 보고 없는 출력을 추정하지 않습니다.'),
        ('생성 당시 HZ와 컴파일 당시 HZ가 다르면 어떻게 발견하는가?', '생성 헤더의 #if와 #error로 검사한다', '실행 중 첫 timer interrupt가 자동으로 상수를 고친다', '상수는 빌드 설정에 종속됩니다. 생성물 안에 입력 HZ를 명시하여 잘못된 재사용을 컴파일 단계에서 드러냅니다.')
    ]
)]
