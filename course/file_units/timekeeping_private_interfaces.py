"""Whole-file private timekeeping and NTP interface contracts."""
ROWS = [dict(
    path='kernel/time/timekeeping.h', title='Timekeeping 내부 선언: offset 갱신·수명·공유 tick 상태',
    intro='offset 조회, 고해상도 조건, suspend/resume, 시간 갱신과 공유 동기화 객체 선언 전체를 읽습니다.',
    principle='내부 인터페이스는 반환값뿐 아니라 포인터로 전달하는 상태와 설정별 stub의 계약도 포함합니다.',
    use='timer와 timekeeping 코드가 어떤 기능을 호출하고 어떤 데이터를 공유하는지 경계를 파악합니다.',
    area='내부 API · 출력 인자 · 캐시 무효화 · 조건부 stub · 동기화 객체',
    sections=[
        ('전체 파일과 포함 문맥', 'GPL-2.0과 guard 뒤 kernel/time 내부 인터페이스라는 주석, 함수 선언과 설정별 inline, 두 extern 객체, CS_NAME_LEN 상수가 있습니다. 자체 include는 없으므로 ktime_t, u64, raw_spinlock_t, seqcount_raw_spinlock_t 등을 사용할 수 있는 문맥에서 포함해야 합니다. 외부 사용자 ABI 헤더가 아닙니다.'),
        ('현재 시간과 offset 인터페이스', 'ktime_get_update_offsets_now는 unsigned int *cwsseq와 ktime_t *offs_real/*offs_boot/*offs_tai를 받고 ktime_t를 반환합니다. 관련 timekeeping.c 본문 일부를 대조하면 monotonic 현재값을 반환하고 clock_was_set_seq가 달라졌을 때 저장된 sequence와 세 offset을 갱신합니다. 포인터들이 매번 무조건 처음부터 채워지는 출력 전용 인자라고 가정하면 안 됩니다.'),
        ('Offset 갱신의 예외와 일관성', '해당 구현은 seqcount로 읽기를 재시도하며 윤초 삽입 경계를 넘으면 offs_real에 추가 보정을 할 수 있습니다. 따라서 sequence가 같으면 어떤 출력도 절대 바뀌지 않는다고 요약하는 것도 부정확합니다. 이 헤더는 시그니처만 선언하며 관련 구현 일부의 확인을 timekeeping.c 전체 작성으로 집계하지 않습니다.'),
        ('고해상도와 최대 지연 선언', 'timekeeping_valid_for_hres는 int, timekeeping_max_deferment는 u64 반환입니다. 관련 구현은 각각 현재 clocksource의 VALID_FOR_HRES flag 값과 max_idle_ns를 일관되게 읽습니다. 첫 함수의 true 결과가 꼭 숫자 1이라는 계약은 아니며 두 번째의 단위는 나노초입니다. 함수 이름만으로 전체 시스템의 timer 정확도를 실측한다고 해석하지 않습니다.'),
        ('Timekeeping 수명과 warp', 'timekeeping_warp_clock는 void, timekeeping_suspend는 int, timekeeping_resume는 void인 외부 선언입니다. 이 파일에는 시계 이동량이나 suspend 상태 저장 구현이 없습니다. do_sys_settimeofday64의 초기 timezone 경로처럼 호출자는 필요에 따라 이 인터페이스를 이용합니다.'),
        ('Sched clock 설정 분기', 'CONFIG_GENERIC_SCHED_CLOCK이면 sched_clock_suspend와 resume를 각각 int/void 외부 함수로 선언합니다. 꺼지면 suspend는 0을 반환하고 resume는 아무것도 하지 않는 inline을 제공합니다. 비활성 기능에서 공통 호출 코드를 유지할 수 있게 하며 suspend 0이 실제 hardware 저장 작업을 수행했다는 증거는 아닙니다.'),
        ('Tick 갱신의 분리', 'update_process_times(int user), do_timer(unsigned long ticks), update_wall_time(void)를 별도로 선언합니다. CPU 사용 문맥을 전달하는 함수, 경과 tick 수를 전달하는 함수, wall time 갱신은 인자 형태부터 다릅니다. 이 헤더 자체가 이들을 특정 순서로 호출하거나 묶어서 잠그지는 않습니다.'),
        ('공유 잠금과 상수', 'jiffies_lock은 extern raw_spinlock_t, jiffies_seq는 extern seqcount_raw_spinlock_t입니다. 선언이므로 여기서 새 객체가 할당되는 것이 아닙니다. 마지막 CS_NAME_LEN은 32라는 길이 상수이며 이 선언만으로 문자열 복사·종단·잘림 정책까지 정의되지는 않습니다.'),
        ('검증 범위', '모든 선언과 두 inline stub을 설명했습니다. 이름만 있는 외부 구현의 전체 알고리즘이나 모든 호출 순서까지 학습 완료로 세지 않습니다. 상태를 함께 주고받는 인터페이스, 설정별 기능 대체와 반환값 의미, 선언·정의의 차이가 핵심 CS입니다.')
    ],
    questions=[
        ('ktime_get_update_offsets_now의 offset 포인터를 매번 무조건 새로 채우는 출력이라고 가정해도 되는가?', '아니다. sequence 기반 갱신과 윤초 보정을 이해해야 한다', '그렇다. 포인터 인자는 언제나 모든 호출에서 완전 초기화된다', '관련 구현은 clock_was_set_seq 변화로 캐시 갱신을 결정하며 별도 윤초 보정도 합니다. 시그니처만으로 초기화 정책을 추정하면 안 됩니다.'),
        ('GENERIC_SCHED_CLOCK이 꺼졌을 때 sched_clock_suspend는?', '아무 작업 없이 0을 반환한다', '외부 심볼이 없어 반드시 링크 오류가 난다', '비활성 분기에 inline stub이 있습니다. 공통 호출 형식을 유지하는 방식입니다.'),
        ('timekeeping_valid_for_hres의 참 결과는 반드시 1인가?', '아니다. 관련 구현은 flag 비트 값을 반환한다', '그렇다. 반환형 int는 bool과 같아 0이나 1만 가능하다', '호출자는 보통 0/비0로 해석해야 합니다. 반환형과 실제 return 식을 함께 확인합니다.'),
        ('extern jiffies_lock 선언이 이 헤더를 포함할 때마다 잠금을 새로 만드는가?', '아니다. 다른 곳에 정의된 객체를 참조하도록 선언한다', '그렇다. 각 include마다 별도 잠금이 생긴다', '공유 객체의 선언과 저장소 정의는 다릅니다. 실제 획득·해제도 호출 코드에 있어야 합니다.')
    ]
), dict(
    path='kernel/time/ntp_internal.h', title='NTP 내부 인터페이스: 분수 tick·윤초·CMOS 알림',
    intro='NTP 초기화·보정·PPS·윤초 선언과 설정별 CMOS 알림을 전체 범위로 읽습니다.',
    principle='정밀 시간 조정은 단순 초 정수만으로 표현하지 않으며 위상·주파수·외부 시계 동기화의 인터페이스를 분리합니다.',
    use='timekeeping과 NTP 구현 사이의 타입·단위·출력 포인터 및 설정 조건을 이해합니다.',
    area='NTP · 고정 소수점 · 윤초 · PPS · 내부 API · 조건부 컴파일',
    sections=[
        ('전체 파일과 타입 전제', 'GPL-2.0과 guard 뒤 일곱 개의 NTP 관련 외부 함수 선언, 설정별 ntp_notify_cmos_timer 선언 또는 inline이 전부입니다. 자체 include가 없어 u64, ktime_t, time64_t, s32, bool과 관련 구조체 선언을 포함 문맥이 제공해야 합니다. 실제 NTP 상태 기계나 PPS 필터는 여기에 없습니다.'),
        ('초기화와 초기 상태 복원', 'ntp_init과 ntp_clear는 인자도 반환값도 없는 외부 함수 선언입니다. 두 이름이 비슷해도 헤더에는 본문이 없으므로 동일 작업이나 사용자 시각을 0으로 만드는 기능이라고 단정하지 않습니다. 초기화·상태 정리의 구체적인 필드 변경은 ntp.c를 확인해야 합니다.'),
        ('분수 tick 길이', 'ntp_tick_length는 u64를 반환하며 주석의 단위는 ns/2^NTP_SCALE_SHIFT입니다. 반환 숫자가 정수 나노초 자체가 아니라 그보다 작은 단위의 개수라는 의미입니다. 실제 ns로 읽으려면 스케일을 고려해야 하며, NTP_SCALE_SHIFT가 이 파일에서 정의되는 것은 아닙니다. 관련 구현은 저장된 tick_length를 그대로 반환합니다.'),
        ('다음 윤초와 초 경계 처리', 'ntp_get_next_leap는 ktime_t, second_overflow는 time64_t secs를 받아 int를 반환합니다. 관련 ntp.c 일부에서 next_leap는 CLOCK_REALTIME 기준이며 TIME_INS와 STA_INS가 모두 충족되면 예정 초를 ktime으로 바꾸고 아니면 KTIME_MAX입니다. 따라서 이 반환을 항상 실제 예약 시각이라고 보거나 삽입·삭제를 모두 같은 식으로 반환한다고 일반화하지 않습니다. second_overflow의 전체 상태 기계는 이 헤더에 없습니다.'),
        ('Adjtimex 내부 인자', '__do_adjtimex는 __kernel_timex *txc, const timespec64 *ts, s32 *time_tai, audit_ntp_data *ad를 받고 int를 반환합니다. 현재 시각 입력은 const이고 조정 구조체·TAI·감사 데이터는 비const 포인터입니다. 비const라는 사실만으로 모든 모드에서 모든 필드를 반드시 쓴다고 단정할 수는 없지만 입출력 경계의 차이는 읽을 수 있습니다.'),
        ('PPS의 두 관측값', '__hardpps는 const timespec64 *phase_ts와 *raw_ts를 받는 void 함수입니다. 위상 기준 관측과 raw 관측을 별도로 전달하는 시그니처입니다. 이 파일에는 두 값을 생성하는 장치 읽기나 filter 식이 없으며 포인터가 const인 것은 이 인터페이스가 그 입력 객체를 수정하지 않는다는 뜻입니다.'),
        ('CMOS 알림의 OR 조건', 'CONFIG_GENERIC_CMOS_UPDATE 또는 CONFIG_RTC_SYSTOHC 중 하나라도 정의되면 ntp_notify_cmos_timer(bool offset_set)는 외부 함수입니다. 둘 다 없으면 같은 인자를 받는 빈 inline 함수입니다. OR를 AND로 읽으면 빌드 조건이 달라집니다. 빈 매크로와 달리 inline 함수 인자로 전달한 표현식의 부작용은 언어 규칙상 유지되어야 합니다.'),
        ('알림 인자와 관련 구현 경계', '관련 ntp.c 일부를 대조하면 offset_set이 true일 때 sync_hrtimer를 취소하고, 동기화 상태이며 타이머가 대기 중이 아니면 work를 queue합니다. 이름만으로 즉시 CMOS를 직접 쓰는 함수라고 설명하지 않습니다. 이 본문 일부 대조는 ntp.c 전체의 상태·worker·동기화 알고리즘 검증이 아닙니다.'),
        ('학습 범위', '전체 선언과 조건부 대체를 설명합니다. fixed-point의 단위 해석, 시간 좌표계, sentinel, const 인자, 논리 OR와 비활성 inline의 평가 의미가 핵심입니다. NTP 서버 통신이나 실제 하드웨어 시계 조정은 수행하지 않았습니다.')
    ],
    questions=[
        ('ntp_tick_length의 반환 숫자를 그대로 정수 ns로 읽어도 되는가?', '아니다. 단위가 ns/2^NTP_SCALE_SHIFT인 값을 뜻한다', '그렇다. u64이면 단위는 항상 ns이다', '자료형 폭과 고정 소수점 스케일은 별개입니다. 헤더 주석의 단위를 먼저 확인해야 합니다.'),
        ('CMOS 알림 외부 구현을 선택하는 설정 조건은?', 'GENERIC_CMOS_UPDATE 또는 RTC_SYSTOHC 중 하나이다', '두 설정이 반드시 동시에 활성화되어야 한다', '전처리 식은 ||입니다. 둘 다 없을 때만 빈 inline을 제공합니다.'),
        ('비활성 CMOS 알림 inline에 f()를 인자로 전달하면 부작용도 항상 사라지는가?', '아니다. 함수 인자 평가의 부작용은 유지되어야 한다', '그렇다. 함수 본문이 비었으므로 빈 매크로와 같다', '컴파일러는 관측 가능한 부작용을 임의로 없앨 수 없습니다. 인자를 통째로 제거하는 빈 매크로와 구분합니다.'),
        ('관련 구현에서 next_leap가 KTIME_MAX이면 실제 그 시각에 윤초가 예정되었다는 뜻인가?', '아니다. 해당 삽입 조건에서 반환할 예정 윤초가 없다는 sentinel이다', '그렇다. 항상 먼 미래의 유효한 달력 시각이다', 'TIME_INS와 STA_INS 조건이 아니면 KTIME_MAX를 반환합니다. 특수값과 실제 타임스탬프를 구분합니다.')
    ]
)]
