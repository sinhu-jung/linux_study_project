"""Whole-file timer subsystem configuration and build mapping."""
ROWS = [dict(
    path='kernel/time/Kconfig', title='시간 서브시스템 설정: tick 모드와 의존성 그래프',
    intro='숨겨진 아키텍처 스위치부터 tick choice, context tracking, watchdog 한계까지 전체 설정을 읽습니다.',
    principle='빌드 기능은 독립된 체크박스 모음이 아니라 의존성·선택·기본값으로 연결된 그래프입니다.',
    use='tickless나 고해상도 타이머를 켰을 때 함께 필요한 기능과 런타임 조건을 구분합니다.',
    area='Kconfig · 의존성 그래프 · 조건부 기능 · tickless · RCU · 설정 호환성',
    sections=[
        ('전체 파일과 숨겨진 설정', 'GPL-2.0-only 표시 뒤 아키텍처가 선택할 bool 설정들, KUnit/context 설정, GENERIC_CLOCKEVENTS 조건 아래 Timers subsystem 메뉴가 있습니다. prompt 없는 bool도 다른 설정의 select나 기본값으로 활성화될 수 있습니다. 이 파일은 .config 결과 자체가 아니라 그 결과를 정하는 규칙입니다.'),
        ('Clocksource 아키텍처 스위치', 'CLOCKSOURCE_WATCHDOG는 불안정 시계 감시, ARCH_CLOCKSOURCE_DATA는 추가 데이터, ARCH_CLOCKSOURCE_INIT는 등록 시 추가 초기화, CLOCKSOURCE_VALIDATE_LAST_CYCLE은 마지막 cycle 갱신 기준 검증에 관한 bool입니다. GENERIC_TIME_VSYSCALL도 prompt 없는 bool로 선언합니다. 여기서 실제 watchdog 주기나 아키텍처 구조체 본문을 구현하지 않습니다.'),
        ('Clockevents와 broadcast', 'GENERIC_CLOCKEVENTS는 def_bool !LEGACY_TIMER_TICK입니다. ARCH_HAS_TICK_BROADCAST는 driver와 무관한 broadcast 처리 능력 스위치입니다. GENERIC_CLOCKEVENTS_BROADCAST는 GENERIC_CLOCKEVENTS에 의존하고 BROADCAST_IDLE은 BROADCAST에 의존합니다. GENERIC_CLOCKEVENTS_MIN_ADJUST와 GENERIC_CMOS_UPDATE는 각각 최소 재프로그래밍 시간 조정과 CMOS 갱신의 별도 bool입니다.'),
        ('POSIX CPU timer와 legacy tick', 'HAVE_POSIX_CPU_TIMERS_TASK_WORK는 지원 능력, POSIX_CPU_TIMERS_TASK_WORK는 POSIX_TIMERS와 해당 능력이 있을 때 default y입니다. default 조건은 depends on 선언과 같지 않으므로 두 키워드를 바꾸어 읽지 않습니다. LEGACY_TIMER_TICK help는 generic clockevents가 없는 플랫폼을 위한 helper이며 새 플랫폼은 generic을 사용하라고 설명합니다.'),
        ('KUnit 설정과 실제 연결', 'TIME_KUNIT_TEST는 KUNIT에 의존하는 tristate이고 !KUNIT_ALL_TESTS일 때 prompt가 보이며 기본값은 KUNIT_ALL_TESTS입니다. help에는 RTC library functions라고 적혀 있지만 이 디렉터리 Makefile은 time_test.o를 연결하며 그 파일은 time64_to_tm 날짜 범위 테스트입니다. 도움말 문구만으로 테스트 대상을 결정하지 않습니다.'),
        ('Context tracking의 기본층', 'CONTEXT_TRACKING은 내부 bool이고 CONTEXT_TRACKING_IDLE은 이를 select하며 RCU를 위한 idle 상태 추적이라고 설명합니다. 두 항목은 뒤의 GENERIC_CLOCKEVENTS 조건문 밖에 있습니다. 메뉴 안의 user tracking 설정과 정의 위치를 구분해야 합니다.'),
        ('메뉴 조건과 내부 oneshot', 'GENERIC_CLOCKEVENTS일 때만 Timers subsystem 메뉴의 항목들이 적용됩니다. TICK_ONESHOT은 tick 기능의 내부 스위치이며 NO_HZ_COMMON과 HIGH_RES_TIMERS가 select합니다. 주석은 일반적인 oneshot clockevent 장치 지원 자체는 이 tick 스위치와 독립적이라고 명시합니다. NO_HZ_COMMON은 bool이고 TICK_ONESHOT을 select합니다.'),
        ('Tick 처리 choice', 'Timer tick handling choice에는 HZ_PERIODIC, NO_HZ_IDLE, NO_HZ_FULL이 있습니다. NO_HZ가 참이면 choice 기본값은 NO_HZ_IDLE입니다. HZ_PERIODIC은 필요 여부와 관계없이 주기적인 tick, NO_HZ_IDLE은 idle에서 필요할 때만 timer interrupt를 발생시키는 모드이며 NO_HZ_COMMON을 select합니다. choice는 서로 다른 모드를 아무렇게나 동시에 켜는 목록이 아닙니다.'),
        ('Full dynticks의 의존성과 선택', 'NO_HZ_FULL은 SMP, HAVE_CONTEXT_TRACKING_USER, HAVE_VIRT_CPU_ACCOUNTING_GEN에 depends on입니다. NO_HZ_COMMON, RCU_NOCB_CPU, VIRT_CPU_ACCOUNTING_GEN, IRQ_WORK, CPU_ISOLATION을 select합니다. 주석은 시간 유지를 위해 적어도 한 periodic CPU가 필요하다고 설명합니다. 이 파일의 직접 select 목록에 없는 설정까지 자동으로 여기서 선택한다고 설명하지 않습니다.'),
        ('Full dynticks의 실행 조건', 'help는 CPU에서 task가 실행 중이어도 가능하면 tick을 멈추되 보통 단일 task, 사용자 공간 위주의 적은 커널 활동이 유리하다고 설명합니다. nohz_full boot parameter로 대상 CPU 범위를 지정해야 하고 없으면 NO_HZ_IDLE처럼 동작한다고 합니다. 사용자·커널 전환의 추가 비용도 명시합니다. 빌드 설정 y만으로 모든 CPU의 tick이 항상 사라지는 보장이 아닙니다.'),
        ('사용자 context 추적', 'CONTEXT_TRACKING_USER는 HAVE_CONTEXT_TRACKING_USER에 의존하고 CONTEXT_TRACKING을 select합니다. RCU와 tickless CPU 시간 집계를 위해 user/kernel 전환을 추적합니다. CONTEXT_TRACKING_USER_FORCE는 USER에 의존하고 !NO_HZ_FULL이면 default y이며, full dynticks 요구를 모두 갖추지 않은 아키텍처 backend의 테스트 용도로 모든 CPU에서 추적을 강제한다고 설명합니다. help는 개발 용도와 production 오버헤드를 구분합니다.'),
        ('구형 NO_HZ와 고해상도', 'NO_HZ는 오래된 설정 파일 호환성을 위한 bool이며 앞의 choice 기본값과 연결됩니다. HIGH_RES_TIMERS는 TICK_ONESHOT을 select하지만 하드웨어가 지원하지 않으면 이미지 크기만 늘어난다는 설명이 있습니다. 설정 가능성과 실제 하드웨어 기능 제공을 구분합니다.'),
        ('Watchdog 허용 skew', 'CLOCKSOURCE_WATCHDOG_MAX_SKEW_US는 watchdog에 의존하는 int이며 허용 범위 50..1000, 기본값 125, 단위는 마이크로초입니다. help는 반초 감시 간격과 NTP 최대 주파수 drift를 배경으로 설명합니다. 이 값은 테스트 모듈의 holdoff 초나 시계의 나노초 uncertainty_margin과 같은 단위·역할이 아닙니다.'),
        ('검증 범위와 CS 연결', '모든 설정 이름과 choice·menu·if 경계를 다뤘습니다. 전체 Kconfig 트리의 다른 파일에서 들어오는 select와 아키텍처 요구를 모두 해석해 실제 .config를 생성한 결과는 아닙니다. 의존성 그래프, default와 강제 선택의 차이, 빌드와 런타임 조건, 호환 설정의 역할을 학습합니다.')
    ],
    questions=[
        ('NO_HZ_FULL을 y로 빌드하면 nohz_full 부팅 인자 없이도 모든 CPU가 full dynticks인가?', '아니다. help는 인자가 없으면 NO_HZ_IDLE처럼 동작한다고 설명한다', '그렇다. 빌드 설정만으로 모든 CPU의 tick이 항상 사라진다', '대상 CPU 지정과 workload 조건이 별도로 필요합니다. 지원 코드 포함과 실제 동작 조건은 다릅니다.'),
        ('TICK_ONESHOT이 모든 oneshot clockevent 장치 지원의 유일한 스위치인가?', '아니다. 주석은 tick 기능의 내부 스위치라고 구분한다', '그렇다. 꺼지면 어떤 oneshot 장치도 존재할 수 없다', '해당 주석은 장치의 oneshot 지원과 tick 동작 모드를 명시적으로 나눕니다.'),
        ('Watchdog maximum skew 기본값과 단위는?', '125마이크로초이다', '125초이다', '설정 이름의 US, int prompt, help를 함께 읽습니다. 테스트 시작 지연이나 나노초 margin과 혼동하지 않습니다.'),
        ('TIME_KUNIT_TEST가 실제로 어떤 파일을 빌드하는지는 어디와 함께 확인해야 하는가?', 'Makefile의 time_test.o 연결과 해당 소스이다', 'RTC라는 도움말 단어만으로 충분하다', '이 버전 도움말과 실제 날짜 변환 테스트 사이 차이가 있습니다. 설정 설명과 빌드 대상을 대조해야 합니다.'),
        ('default y if 조건은 depends on 조건과 같은가?', '아니다. 기본값 규칙과 의존성 제한은 서로 다르다', '그렇다. 두 키워드는 완전히 같은 의미이다', 'POSIX_CPU_TIMERS_TASK_WORK는 조건부 default를 사용합니다. 설정 그래프에서 어떤 규칙이 적용되는지 실제 키워드를 확인합니다.')
    ]
), dict(
    path='kernel/time/Makefile', title='시간 서브시스템 빌드 지도: 공통 객체·stub·조건부 timer',
    intro='모든 obj-y와 obj-CONFIG 연결, 중첩 ifeq 분기를 소스 파일과 대응시킵니다.',
    principle='기능 설정은 컴파일할 파일을 선택하며, 비활성 기능에는 별도의 stub 파일이 연결될 수 있습니다.',
    use='수정한 소스가 어떤 설정에서 빌드되는지 확인하고 일부 파일의 테스트 통과를 전체 구성 검증으로 확대하지 않습니다.',
    area='Kbuild · 조건부 컴파일 · 의존성 · stub · 모듈 · 빌드 구성',
    sections=[
        ('전체 파일과 공통 객체', 'GPL-2.0 표시 뒤 공통 obj-y에 time, timer, hrtimer, timekeeping, ntp, clocksource, jiffies, timer_list, timeconv, timecounter, alarmtimer의 .o가 나열됩니다. 이 디렉터리가 빌드되는 문맥에서 기본 연결되는 객체들입니다. 파일 전체가 함수 구현이 아니라 Kbuild 입력입니다.'),
        ('POSIX timer 대체 경로', 'CONFIG_POSIX_TIMERS가 정확히 y이면 posix-timers.o, posix-cpu-timers.o, posix-clock.o, itimer.o를 obj-y에 추가합니다. 아니면 posix-stubs.o를 추가합니다. 설정이 꺼졌다고 모든 관련 인터페이스가 단순히 사라지는 것으로 추측하지 말고 stub 구현을 확인해야 합니다.'),
        ('Clockevents와 broadcast 중첩', 'CONFIG_GENERIC_CLOCKEVENTS로 clockevents.o와 tick-common.o를 선택합니다. BROADCAST가 y일 때 tick-broadcast.o를 무조건 obj-y에 추가하고 그 블록 안에서 TICK_ONESHOT에 따라 tick-broadcast-hrtimer.o를 선택합니다. 따라서 후자는 ONESHOT만으로 추가되지 않으며 바깥 BROADCAST 조건도 필요합니다.'),
        ('Sched clock과 tick 모드', 'CONFIG_GENERIC_SCHED_CLOCK은 sched_clock.o, TICK_ONESHOT은 tick-oneshot.o와 tick-sched.o, LEGACY_TIMER_TICK은 tick-legacy.o에 연결됩니다. 비슷한 이름이어도 일반 sched_clock과 tick scheduler의 빌드 조건이 다릅니다.'),
        ('SMP timer migration', 'CONFIG_SMP가 y인 ifeq 안에서 CONFIG_NO_HZ_COMMON으로 timer_migration.o를 선택합니다. NO_HZ_COMMON만 활성화되고 SMP 조건이 충족되지 않으면 이 줄은 적용되지 않습니다. 중첩 조건은 함께 읽어야 합니다.'),
        ('vDSO·debugfs·namespace', 'HAVE_GENERIC_VDSO는 vsyscall.o, DEBUG_FS는 timekeeping_debug.o, TIME_NS는 namespace.o를 선택합니다. GENERIC_TIME_VSYSCALL 같은 다른 설정 이름을 이 Makefile의 실제 조건 이름으로 바꿔 읽지 않습니다. 해당 파일의 내부 #ifdef는 여기 보이는 파일 단위 선택과 별개입니다.'),
        ('테스트 객체 세 개', 'TEST_UDELAY는 test_udelay.o, TEST_CLOCKSOURCE_WATCHDOG는 clocksource-wdtest.o, TIME_KUNIT_TEST는 time_test.o를 선택합니다. obj-$(CONFIG_...) 형식은 설정값 y/m에 따라 built-in 또는 모듈 대상으로 연결될 수 있지만 그 설정이 실제로 m을 허용하는지는 해당 Kconfig 타입과 의존성을 함께 확인해야 합니다.'),
        ('파일에 없는 생성 규칙', '같은 디렉터리의 timeconst.bc가 있어도 이 Makefile에는 그 스크립트를 실행하는 recipe가 없습니다. 여기에서 generated/timeconst.h를 만든다고 주장하려면 다른 빌드 규칙을 확인해야 합니다. 파일 목록을 보고 없는 명령을 보충해 추정하지 않습니다.'),
        ('검증 범위', '전체 객체 선택 줄과 모든 ifeq/else/endif를 다뤘습니다. 이 자료를 학습 프로그램으로 빌드한 것은 각 커널 설정 조합을 실제 컴파일했다는 뜻이 아닙니다. 빌드 행렬, 대체 구현, 중첩 조건의 AND 관계와 파일 단위·함수 단위 조건의 차이를 학습합니다.')
    ],
    questions=[
        ('POSIX_TIMERS가 y가 아닐 때 어떤 파일이 연결되는가?', 'posix-stubs.o이다', 'posix-timers.o가 항상 그대로 연결된다', '명시적인 ifeq/else가 실제 구현과 stub을 선택합니다. 기능 비활성 경로에도 소스가 존재합니다.'),
        ('tick-broadcast-hrtimer.o는 TICK_ONESHOT만 켜면 추가되는가?', '아니다. 바깥 BROADCAST=y 조건도 필요하다', '그렇다. 중첩 ifeq는 obj-CONFIG 줄에 영향을 주지 않는다', '줄 자체가 broadcast ifeq 안에 있습니다. 조건 두 개가 함께 충족되어야 합니다.'),
        ('timer_migration.o가 선택되려면 무엇이 필요한가?', 'SMP=y와 NO_HZ_COMMON 선택이 함께 필요하다', 'DEBUG_FS만 필요하다', 'SMP ifeq가 바깥 조건이고 obj-CONFIG_NO_HZ_COMMON이 안쪽 선택입니다.'),
        ('이 파일에 timeconst.bc 실행 명령이 있는가?', '없다. 생성 규칙은 다른 빌드 파일에서 찾아야 한다', '있다. 같은 디렉터리의 .bc는 자동으로 모두 실행된다', 'Makefile의 실제 본문에는 객체 선택만 있습니다. 디렉터리 위치만으로 생성 명령을 추정하지 않습니다.')
    ]
)]
