"""Whole ARM delay interface and timer-selection implementation."""
ROWS = [dict(
    path='arch/arm/include/asm/delay.h',
    title='ARM 지연 헤더 전체: 고정소수점 변환과 상수 검사',
    intro='마이크로초를 loop 또는 tick 수로 바꾸는 정수 산술과 구현 선택 테이블을 읽습니다.',
    principle='작은 분수를 정수 곱셈과 시프트로 표현하되 중간값의 폭과 지원 범위를 함께 제한합니다.',
    use='공통 delay.h의 MAX_UDELAY_MS가 ARM에서2로 바뀌는 이유를 계산식과 연결합니다.',
    area='고정소수점 · 정수 오버플로 · 함수 포인터 · 컴파일 상수 · 타이머',
    sections=[
        ('전체 구성', 'GPL-2.0·저작권·guard 뒤 page.h와 HZ용 param.h를 포함합니다. 변환식 주석과 상수는 어셈블리에서도 볼 수 있고 C 분기 안에 timer 구조체,연산 테이블,매크로,loop 함수와 등록 함수 선언을 둡니다. 실제 대기 루프 본문은 이 파일에 없습니다.'),
        ('단위 변환 식', '기본 식은 loops_per_jiffy*HZ*delay_us/1000000입니다. 분수 HZ/1000000을2^31만큼 확대해 정수 곱셈에 사용하고 마지막에31비트 이동합니다. UDELAY_MULT는2147*HZ+483648*HZ/1000000이며 UDELAY_SHIFT는31입니다. 이 정수식은 소수2147.483648*HZ의 분해와 연결됩니다.'),
        ('폭의 제한', '주석은 HZ<=1000,delay_us<=2000일 때 delay_us*UDELAY_MULT가32비트에서 넘치지 않는 최대 scale shift가31이라고 설명합니다. MAX_UDELAY_MS는2입니다. 이 조건 밖의 임의 입력에 같은 안전성 증명을 적용할 수 없습니다. 정수 나눗셈의 절삭과 하드웨어 지연 정확성은 별도로 구분합니다.'),
        ('타이머와 연산 테이블', 'delay_timer는 unsigned long을 반환하는 read_current_timer callback과 freq를 가집니다. arm_delay_ops는 delay,const_udelay,udelay 함수 포인터와 ticks_per_jiffy를 가집니다. __delay,__udelay,__const_udelay는 대응 포인터에 위임합니다. 테이블의 이름이 같아도 전달량은 원래 us 또는 미리 배율을 적용한 값으로 다릅니다.'),
        ('상수 인자 검사', 'udelay(n)은 compiler가 n을 상수로 판단하면2000us 초과에 __bad_udelay를 호출하고 그 이하면 n*UDELAY_MULT를 const_udelay에 넘깁니다. __bad_udelay는 의도적으로 존재하지 않아 잘못된 상수 사용을 드러냅니다. 런타임 변수 경로는 __udelay(n)이며 동일한 크기 검사를 추가하지 않습니다. 따라서 런타임 큰 값이 안전하게 거부된다고 설명하면 틀립니다.'),
        ('선언과 기능 표시', '__loop_delay,__loop_udelay,__loop_const_udelay는 loop 구현 선언입니다. ARCH_HAS_READ_CURRENT_TIMER는 기능 매크로이고 register_current_timer_delay는 timer 구조체의 const 포인터를 받습니다. 선언만으로 등록된 callback의 수명이나 주파수 정확도를 보증하지 않습니다.'),
        ('CS 연결', '시간 단위와 정수 scale,중간 곱의 폭,상수 접기와 런타임 경로,전략 테이블을 통한 구현 교체를 학습합니다. 주석의 계산 유도와 실제 asm loop의 실행 정확성을 같은 검증으로 세지 않습니다.')
    ],
    questions=[
        ('ARM MAX_UDELAY_MS의 값은?', '2이다', '항상 공통 기본값5이다', '아키텍처 헤더에서2를 정의하므로 공통 delay.h의 #ifndef 기본5가 적용되지 않습니다.'),
        ('udelay의 런타임 변수 경로도2000us 초과를 검사하는가?', '아니다. __udelay(n)에 위임한다', '그렇다. 모든 입력은 __bad_udelay로 검사한다', '__builtin_constant_p가 참인 분기에만 크기 조건이 있습니다. 상수 검사와 런타임 검사를 혼동하지 않아야 합니다.'),
        ('UDELAY_SHIFT=31의 목적은?', '확대한 고정소수점 곱을 다시 축소하는 것이다', '타이머 인터럽트를31번 기다리는 것이다', '2^31 scale을 정수 곱에 사용하므로 마지막 오른쪽 이동으로 단위를 복원합니다. 인터럽트 횟수 상수가 아닙니다.')
    ]
), dict(
    path='arch/arm/lib/delay.c',
    title='ARM 지연 구현 전체: timer 선택과 보정 이후 동결',
    intro='기본 loop 구현에서 적합한 타이머 기반 busy wait로 교체하는 경로를 해설합니다.',
    principle='타이머 해상도와 등록 시기를 검사해 더 나은 구현을 선택하고,보정 후에는 교체하지 않습니다.',
    use='delay.h의 함수 포인터와 fixed-point 값을 실제 tick 대기로 연결합니다.',
    area='타이머 해상도 · busy wait · 고정소수점 · 초기화 상태 기계 · 함수 포인터',
    sections=[
        ('전체 구성과 기본 전략', 'GPL-2.0-only·OpenRISC 기반 설명·저작권 뒤 clocksource/delay/init/kernel/module/timex 헤더를 포함합니다. arm_delay_ops는 __ro_after_init이며 초기 세 callback은 __loop 계열입니다. static delay_timer,delay_calibrated,delay_res로 선택 상태를 관리합니다. 초기화 후 읽기 전용 지정과 부팅 중 선택을 구분합니다.'),
        ('현재 타이머 조회', 'read_current_timer는 등록된 delay_timer가 없으면 -ENXIO입니다. 있으면 callback 결과를 *timer_val에 저장하고0을 반환합니다. GPL 심벌로 export하며 출력 포인터의 NULL 검사는 없습니다. 실패 시 출력값을0으로 초기화하는 본문도 없습니다.'),
        ('주기에서 나노초', 'cyc_to_ns는 (cyc*mult)>>shift로 변환합니다. 등록 단계에서 clocks_calc_mult_shift에 입력 주파수,출력 NSEC_PER_SEC,3600을 전달해 계수를 구한 뒤1cycle의 정수 ns를 계산합니다. 이 값은 선택 기준의 해상도 추정이며 실제 함수 호출 지연 전체를 측정한 값이 아닙니다.'),
        ('타이머 busy wait', '__timer_delay는 get_cycles의 시작값을 저장하고 현재 값과의 차이가 요청 cycles보다 작은 동안 cpu_relax합니다. sleep이나 스케줄러 타이머 대기는 아닙니다. wraparound와 큰 요청의 안전성은 counter 폭·호출 범위와 함께 판단해야 하며 임의 길이를 무제한 지원한다고 설명하지 않습니다.'),
        ('고정소수점 값 처리', '__timer_const_udelay는 unsigned long xloops를 unsigned long long으로 확대하고 ticks_per_jiffy를 곱한 뒤 UDELAY_SHIFT만큼 이동한 값으로 __timer_delay를 호출합니다. __timer_udelay는 usecs*UDELAY_MULT를 먼저 계산해 이 함수에 넘깁니다. 뒤에서64비트로 확장하더라도 그 전에 수행된 곱셈의 폭 제한이 자동으로 없어지는 것은 아닙니다.'),
        ('해상도 상한 검사', 'register_current_timer_delay는1tick의 res가1000ns보다 크면 오류 메시지 후 반환합니다. 정확히1000ns이면 이 검사만으로 거부하지 않습니다. 주파수0이나 callback NULL 등의 별도 유효성 검사는 이 본문에 없으므로 적합한 timer 구조체를 제공해야 합니다.'),
        ('더 좋은 timer 선택', 'delay_calibrated가 거짓이고 delay_res가0이거나 새 res가 더 작을 때 선택합니다. 같은 비0 해상도는 개선으로 세지 않습니다. 선택하면 포인터,lpj_fine=timer->freq/HZ,delay_res를 기록하고 ticks_per_jiffy에 lpj_fine의 개인 복사본을 둡니다. 주석은 cpufreq가 loops_per_jiffy를 조정할 수 있어 별도 값을 보존한다고 설명합니다.'),
        ('함수 포인터 교체', '선택 성공 시 delay,const_udelay,udelay를 모두 timer 기반 함수로 바꿉니다. 구조체 자체를 복사하는 대신 timer 포인터를 보관하므로 제공 객체와 callback의 수명이 이후 사용을 견뎌야 합니다. 조건에 맞지 않으면 중복·늦은 등록을 무시한다는 메시지를 남깁니다.'),
        ('보정 종료 상태', 'calibrate_delay_is_known은 delay_calibrated=true로 만든 뒤 lpj_fine을 반환합니다. 이름과 달리 상태를 전혀 바꾸지 않는 순수 조회 함수가 아닙니다. calibration_delay_done도 true를 설정합니다. 이후 더 작은 res가 등록돼도 선택 조건의 !delay_calibrated를 통과하지 못합니다.'),
        ('CS 연결과 검증 범위', '초기 전략 교체,상태 기반 등록 차단,정수 변환 계수와 해상도 비교,단위 변환의 중간 폭,borrowed 포인터 수명,조회 API의 부작용을 학습합니다. 이 해설은 실제 ARM cycle counter 속도나 모든 wraparound 시나리오를 측정한 결과가 아닙니다.')
    ],
    questions=[
        ('timer가 없을 때 read_current_timer의 결과는?', '-ENXIO이며 출력값을 새로 쓰지 않는다', '0을 반환하고 출력값도0이다', '첫 분기에서 즉시 오류를 반환합니다. 출력 대입은 timer가 있는 경로에만 있습니다.'),
        ('새 해상도가 정확히1000ns이면 상한 검사에서 거부되는가?', '아니다.1000보다 클 때 거부한다', '그렇다.1000 이상을 모두 거부한다', '조건은 res>1000입니다. 이후 보정 상태와 기존 해상도 비교 조건은 별도로 만족해야 합니다.'),
        ('보정 완료 뒤 더 정밀한 timer를 등록하면?', '현재 선택을 바꾸지 않는다', '항상 더 정밀한 timer로 교체한다', '등록 선택에는 !delay_calibrated가 필요합니다. 보정 종료 함수들이 이 상태를true로 설정합니다.'),
        ('타이머 기반 지연은 CPU를 수면시키는가?', '아니다. get_cycles를 반복 확인하는 busy wait이다', '그렇다. msleep을 호출한다', '루프는 counter 차이와 cpu_relax를 사용합니다. timer를 기준으로 측정한다는 것과 sleep은 별개입니다.'),
        ('calibrate_delay_is_known은 단순한 무부작용 조회인가?', '아니다. delay_calibrated를true로 바꾼다', '그렇다. lpj_fine만 읽는다', '반환 전에 보정 상태를 갱신하며 후속 timer 등록의 선택 가능성에 영향을 줍니다.')
    ]
)]
