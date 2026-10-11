"""Whole-file tick scheduler state and configuration-dependent declarations."""
ROWS = [dict(
    path='kernel/time/tick-sched.h',
    title='Tick scheduler 상태: idle 플래그와 시간 집계 필드',
    intro='장치 모드, 상태 비트 여섯 개, tick_sched의 모든 필드와 조건부 인터페이스를 읽습니다.',
    principle='CPU의 idle 상태, tick 중단, 실제 수면 집계와 tick 의존성은 서로 다른 정보로 저장됩니다.',
    use='tickless 코드를 읽을 때 비슷한 이름의 시각·계수·상태 비트를 혼동하지 않습니다.',
    area='상태 모델 · CPU별 데이터 · 비트 마스크 · 통계 · seqcount · atomic · stub',
    sections=[
        ('파일 전체와 포함 문맥', 'GPL-2.0과 guard, hrtimer include 뒤 tick_device_mode, tick_device, 여섯 TS_FLAG 상수, tick_sched 구조체와 함수 선언·stub이 있습니다. 상태 구조를 정의하지만 실제 idle 진입·이탈 알고리즘이나 per-CPU 객체 저장소를 여기서 정의하지는 않습니다.'),
        ('Tick 장치 모드', 'enum의 PERIODIC은 첫 값 0, ONESHOT은 다음 값 1입니다. tick_device는 clock_event_device *evtdev와 enum mode만 가집니다. 장치 포인터와 소프트웨어 tick 모드를 연결하는 구조이며 hrtimer queue나 이벤트 callback 구현을 직접 내장하지 않습니다.'),
        ('Idle 관련 세 비트', 'TS_FLAG_INIDLE=BIT(0)은 tick idle 모드, STOPPED=BIT(1)은 idle tick 중단, IDLE_ACTIVE=BIT(2)는 실제로 idle 시간 집계가 활성인 상태를 나타내며 IRQ 처리 중에는 해제된다는 주석이 있습니다. 따라서 INIDLE과 IDLE_ACTIVE를 같은 비트로 합쳐 읽거나 idle 진입이 항상 tick 중단을 뜻한다고 추정하면 안 됩니다.'),
        ('나머지 상태 비트', 'DO_TIMER_LAST=BIT(3)은 idle에 들어가기 전 마지막 do_timer 담당 CPU였음을, NOHZ=BIT(4)는 NO_HZ 활성, HIGHRES=BIT(5)는 고해상도 tick 모드를 나타냅니다. flags 필드는 unsigned long이며 이 헤더에는 비트 set/clear 함수가 없습니다. 각 비트의 전이는 실제 tick-sched.c에서 확인해야 합니다.'),
        ('Jiffies 정체 감지 필드', 'stalled_jiffies는 unsigned int로 tick 사이에 감지한 정체를 세고 last_tick_jiffies는 unsigned long으로 마지막 tick에서 본 jiffies를 보관합니다. 뒤의 last_jiffies와 이름이 비슷하지만 목적이 다릅니다. 구조체 선언만으로 정체 판정 임계값이나 복구 정책까지 알 수는 없습니다.'),
        ('Tick 처리 필드 전체', 'sched_timer는 고해상도 모드의 주기적 tick을 예약하는 hrtimer입니다. last_tick은 nohz 수면을 위해 timer를 바꾸기 전 마지막 만료 시각을 보존하여 복귀 시 원래 시간축을 이어 가기 위한 ktime_t이고 next_tick은 dynticks의 다음 tick입니다. idle_jiffies는 idle 진입 시 jiffies, idle_waketime은 idle 중단 시각, got_idle_tick은 idle 중 timer 함수가 실행되었음을 기록하는 unsigned int입니다. 주석의 @inidle 언급에 대응하는 상태는 현재 구조에서는 flags에 있으며 별도 inidle 멤버는 없습니다.'),
        ('Idle 진입과 일관성', 'idle_sleeptime_seq는 데이터 일관성을 위한 seqcount_t이고 idle_entrytime은 진입 시각 ktime_t입니다. seqcount 객체가 있다는 것만으로 구조체 전체가 자동으로 보호되거나 reader가 잠금을 잡는 것은 아닙니다. 실제 writer begin/end와 reader retry 구간은 구현에서 결정합니다.'),
        ('다음 만료 계산 상태', 'last_jiffies는 다음 이벤트를 마지막 계산할 때의 기준 jiffies입니다. timer_expires_base는 monotonic 기준 시간, timer_expires는 tick 중단 시 예상 timer 만료 시간이며 둘 다 u64입니다. next_timer는 다음 timer 만료 시각 u64, idle_expires는 다음 idle tick의 ktime_t이고 두 필드는 주석상 디버깅 목적입니다. 디버그 값이 실제 예약 장치 상태의 유일한 권위라고 가정하지 않습니다.'),
        ('Idle 횟수와 기간', 'idle_calls와 idle_sleeps는 unsigned long이며 각각 전체 idle 호출 수와 scheduler tick을 중단한 idle 호출 수입니다. idle_exittime은 idle 종료 시각, idle_sleeptime은 tick을 중단한 idle 수면 합, iowait_sleeptime은 IO가 남아 있던 해당 수면 합을 나타내는 ktime_t입니다. 횟수와 기간, 단일 시각과 누적량을 구분합니다.'),
        ('Full dynticks와 clock 변경', 'tick_dep_mask는 atomic_t이며 누군가 tick을 필요로 할 때 설정하는 의존성 mask입니다. check_clocks는 clocksource 변경 알림용 unsigned long입니다. 하나가 atomic이라고 주변의 다른 필드까지 원자적인 스냅샷이 되는 것은 아닙니다. 개별 mask bit 의미나 알림 소비 코드는 이 파일에 없습니다.'),
        ('공통 함수 선언', 'tick_get_tick_sched(int cpu)는 해당 CPU 상태 포인터를 반환하는 외부 선언이고 tick_setup_sched_timer(bool hrtimer)는 timer 설정의 외부 선언입니다. CPU 번호 검사, 포인터 수명, hrtimer bool에 따른 모든 분기는 본문이 없으므로 이 헤더만으로 보장하지 않습니다.'),
        ('Oneshot 종료 분기', 'CONFIG_TICK_ONESHOT이 정의되어 있으면 tick_sched_timer_dying(int cpu)를 선언하고 아니면 빈 void inline을 제공합니다. 비활성 경로에서도 호출 코드를 유지할 수 있지만 실제 timer 정리를 수행한다는 뜻은 아닙니다. inline 함수이므로 인자의 관측 가능한 부작용은 빈 매크로와 달리 평가 규칙을 따릅니다.'),
        ('Broadcast 비활성은 성공이 아님', 'CONFIG_GENERIC_CLOCKEVENTS_BROADCAST이면 __tick_broadcast_oneshot_control(enum tick_broadcast_state)을 외부 int 함수로 선언합니다. 아니면 stub은 -EBUSY를 반환합니다. 모든 비활성 stub이 0이나 성공을 반환한다는 가정은 틀립니다. 이 함수는 비활성 기능에서 요청을 수락하지 않는 결과를 명시합니다.'),
        ('CS와 검증 범위', '모든 필드와 설정 분기를 다뤘습니다. 상태 머신의 여러 차원을 별도 비트로 보존하는 이유, 누적량과 순간값의 구분, 구조체 타입과 동시성 계약의 차이, 실패하는 stub을 학습합니다. tick-sched.c 전체 실행이나 실제 CPU idle 측정을 검증한 결과는 아닙니다.')
    ],
    questions=[
        ('INIDLE과 IDLE_ACTIVE는 항상 같은 의미인가?', '아니다. IDLE_ACTIVE는 IRQ 처리 중 해제될 수 있다', '그렇다. 같은 비트를 이름만 바꾸어 정의한다', 'BIT(0)과 BIT(2)로 분리되어 있으며 주석이 IRQ 처리 중의 차이를 설명합니다.'),
        ('idle_calls와 idle_sleeps의 차이는?', '전체 idle 호출과 tick을 중단한 idle 호출을 각각 센다', '하나는 초, 다른 하나는 나노초로 같은 시간을 저장한다', '둘 다 횟수입니다. 실제 수면 기간 합계는 별도의 ktime_t 필드들에 있습니다.'),
        ('last_tick_jiffies와 last_jiffies는 같은 목적의 복제 필드인가?', '아니다. tick 정체 관측과 다음 이벤트 계산 기준이라는 목적이 다르다', '그렇다. 어느 쪽을 읽어도 항상 같은 값이어야 한다', '구조체 주석과 필드 묶음이 역할을 구분합니다. 값의 일치 여부를 이름의 유사성만으로 가정하지 않습니다.'),
        ('Broadcast가 비활성일 때 control stub의 반환값은?', '-EBUSY이다', '0이다', '이 비활성 stub은 요청을 성공으로 처리하지 않습니다. 각 stub 본문의 반환값을 직접 확인해야 합니다.'),
        ('atomic_t tick_dep_mask가 있으므로 tick_sched 전체 읽기가 원자적인가?', '아니다. 다른 필드와 함께 읽는 일관성은 별도 계약이 필요하다', '그렇다. 구조체에 atomic 멤버가 하나라도 있으면 전체가 atomic이다', 'atomic 타입은 해당 객체의 지원 연산에 관한 것입니다. 여러 시각·계수의 스냅샷을 자동 보장하지 않습니다.')
    ]
)]
