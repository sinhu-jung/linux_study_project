"""Whole common delay and sleep API header."""
ROWS = [dict(
    path='include/linux/delay.h',
    title='지연 API 전체: busy wait와 수면의 선택',
    intro='mdelay·ndelay fallback, 수면 상태 wrapper와 fsleep의 세 구간 선택을 해설합니다.',
    principle='시간 단위의 변환, 실행 문맥의 제약, 실제 대기 방식은 별개입니다. 요청한 시간과 실제 반환 시각을 동일시하지 않습니다.',
    use='iopoll.h의 busy delay와 sleep 호출을 이 공통 API 정의에 연결합니다.',
    area='시간 단위 · 정수 올림 · compiler 상수 판별 · 스케줄링 · 지연 보정',
    sections=[
        ('파일 구조와 보정값', 'GPL-2.0·guard·저작권 뒤 지연 주석, math.h·sched.h 포함, loops_per_jiffy extern, 아키텍처 delay.h 포함으로 시작합니다. mdelay·ndelay fallback, 보정·수면 선언, inline wrapper와 fsleep까지 제공합니다. udelay의 실제 루프나 타이머 구현은 asm/delay.h에 의존합니다.'),
        ('조기 반환에 대한 주석', '주석은 ndelay/udelay/mdelay가 일찍 반환할 수 있는 원인으로 낮게 계산된 loops_per_jiffy,캐시 동작,CPU 클럭 변화를 나열합니다. 따라서 함수 이름과 요청값만으로 정밀한 최소 지연이 항상 보장된다고 설명하지 않습니다. 주석의 외부 메일 링크는 이 학습에서 해당 토론 전체를 검증했다는 뜻이 아닙니다.'),
        ('Mdelay의 목적', '큰 udelay 인자는 loops_per_jiffy가 높은 환경에서 overflow 위험이 있다는 주석입니다. MAX_UDELAY_MS는 아키텍처가 제공하지 않으면5입니다. mdelay도 기존 아키텍처 정의가 없을 때만 공통 wrapper를 제공합니다. 이5라는 값은 모든 플랫폼에서 고정인 하드웨어 한계가 아닙니다.'),
        ('상수와 반복 분기', 'mdelay(n)은 __builtin_constant_p(n)이 참이고 n<=MAX_UDELAY_MS일 때 udelay(n*1000)을 한 번 호출합니다. 그 밖은 unsigned long __ms에 n을 담고 while(__ms--) udelay(1000)을 반복합니다. 런타임 변수의 값이2여도 compiler가 상수로 판정하지 않으면 반복 경로입니다. mdelay는 msleep으로 전환하지 않습니다.'),
        ('Ndelay fallback', 'ndelay가 없으면 unsigned long 나노초 x를 DIV_ROUND_UP(x,1000)으로 마이크로초 올림하여 udelay에 전달합니다. 예를 들어1500ns는2us로 요청됩니다. 이는 실제 나노초 단위 하드웨어 타이머를 구현하는 함수가 아니며 아키텍처가 더 정밀한 ndelay를 제공하면 이 fallback은 생기지 않습니다. 자기참조 매크로는 정의 존재를 표시합니다.'),
        ('보정 인터페이스', 'lpj_fine도 extern unsigned long입니다. calibrate_delay는 void,calibrate_delay_is_known은 unsigned long을 반환하며 calibration_delay_done은 weak void 함수로 선언합니다. 이 헤더에는 보정 측정 알고리즘이나 weak hook의 호출 위치가 없습니다. 함수 이름만으로 측정 방식·오류 의미를 만들어 설명하지 않습니다.'),
        ('수면 함수 선언', 'msleep은 unsigned int 밀리초를 받아 void를 반환하고 msleep_interruptible은 unsigned long을 반환하는 별도 함수입니다. usleep_range_state는 unsigned long min/max와 unsigned int state를 받습니다. 이 선언만으로 실제 타이머 설정과 재스케줄링 루프 전체를 검증한 것은 아닙니다.'),
        ('상태를 고르는 wrapper', 'usleep_range는 TASK_UNINTERRUPTIBLE,usleep_idle_range는 TASK_IDLE을 usleep_range_state에 전달합니다. 두 wrapper가 직접 반복 지연 루프를 구현하는 것은 아닙니다. 같은 min/max라도 태스크 상태 계약이 다르므로 이름만 바꾼 완전히 동일한 호출이라고 설명하지 않습니다.'),
        ('초 단위 수면', 'ssleep은 seconds*1000을 msleep에 전달합니다. 입력은 unsigned int이며 별도 overflow 검사나 분할 루프가 없습니다. 시간 단위를 바꾼다고 무제한 큰 입력이 안전해지는 것은 아닙니다.'),
        ('Fsleep의 세 구간', '이 고정 버전의 fsleep은 usecs<=10이면 udelay,10보다 크고20000이하면 usleep_range(usecs,2*usecs),그보다 크면 msleep(DIV_ROUND_UP(usecs,1000))을 선택합니다. 예를 들어10은busy delay,11은11~22us 범위 수면 요청,20000은20000~40000us 범위,20001은21ms 요청입니다. 경계의 등호를 정확히 읽어야 합니다.'),
        ('문맥과 시간 정확도', 'fsleep은 긴 요청에서 sleep API를 사용하므로 임의의 atomic 문맥에서 모든 입력에 안전한 함수가 아닙니다. 범위 수면의 max나 msleep 요청값은 실제 반환 지연 전체의 엄격한 상한을 자동 보장하지 않습니다. 인터럽트·스케줄러·구현별 지연을 구분합니다. 이 파일에는 입력값을 보고 현재 문맥을 자동 수정하는 코드가 없습니다.'),
        ('CS 연결과 범위', '정수 단위 변환과 ceil division,compile-time 상수 판별,오버플로를 줄이는 분할,CPU 점유와 수면,상태별 wrapper,임계값 분기 분석을 학습합니다. 소스 대응·구조 검사는 실제 시간 측정이나 모든 CPU 보정 정확성의 검증을 대신하지 않습니다.')
    ],
    questions=[
        ('공통 mdelay의 큰 요청은 msleep으로 바뀌는가?', '아니다. udelay(1000)을 반복한다', '그렇다.5ms 초과는 항상 msleep이다', 'mdelay의 반복 경로는1ms busy delay를 누적합니다. fsleep의 대기 방식 선택과 혼동하지 않아야 합니다.'),
        ('공통 ndelay(1500)은 udelay에 어떤 값을 전달하는가?', '2이다', '1이다', 'DIV_ROUND_UP(1500,1000)=2입니다. 나노초 입력을 마이크로초로 올림하며 실제 나노초 정밀도를 보장하는 구현은 아닙니다.'),
        ('fsleep(20000)과 fsleep(20001)의 선택은 각각?', 'usleep_range와 msleep이다', '둘 다 udelay이다', '두 번째 분기의 조건은<=20000입니다.20001은 밀리초 올림으로21ms의 msleep을 요청합니다.'),
        ('usleep_idle_range가 전달하는 태스크 상태는?', 'TASK_IDLE이다', 'TASK_UNINTERRUPTIBLE이다', '일반 usleep_range는 TASK_UNINTERRUPTIBLE이고 idle wrapper는 TASK_IDLE입니다. 공통 state 함수를 호출하되 상태 인자가 다릅니다.'),
        ('udelay 계열이 요청보다 빨리 반환할 가능성을 원문이 인정하는가?', '그렇다. 보정값·캐시·클럭 변화를 원인으로 든다', '아니다. 모든 환경에서 정확히 같은 시간을 보장한다', '헤더 첫 주석이 세 원인을 명시합니다. 단위 변환의 산술 정확성과 실제 대기 시간 정확도를 구분해야 합니다.')
    ]
)]
