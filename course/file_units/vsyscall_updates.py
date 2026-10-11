"""Whole-file generic vDSO data publication implementation."""
ROWS = [dict(
    path='kernel/time/vsyscall.c',
    title='vDSO 시간 게시: clock별 기준값과 일관된 갱신 구간',
    intro='고해상도·coarse 데이터 작성, timezone 갱신과 아키텍처용 begin/end를 전체 소스로 읽습니다.',
    principle='사용자 공간에서 빠르게 읽을 공유 데이터는 단위와 좌표계를 맞추고 여러 필드의 일관성을 게시 규약으로 보장해야 합니다.',
    use='timekeeper의 내부 표현이 vDSO 읽기용 데이터로 바뀌는 과정과 잠금·sequence·동기화의 역할을 이해합니다.',
    area='vDSO · 공유 데이터 · 고정 소수점 · seqcount · clock 좌표계 · 아키텍처 hook',
    sections=[
        ('전체 파일', 'GPL-2.0과 ARM 저작권·x86 기반 설명, 관련 include 뒤 update_vdso_data, update_vsyscall, update_vsyscall_tz, vdso_update_begin/end가 있습니다. clock 읽기 syscall이나 사용자 vDSO reader 본문은 이 파일에 없습니다. __arch_get_k_vdso_data로 커널이 쓸 데이터 주소를 얻습니다.'),
        ('두 clocksource 데이터 묶음', 'update_vdso_data는 CS_HRES_COARSE에 tkr_mono의 cycle_last/mask/mult/shift를, CS_RAW에 tkr_raw의 같은 네 필드를 복사합니다. CONFIG_GENERIC_VDSO_OVERFLOW_PROTECT이면 각 clock의 max_cycles도 복사합니다. 이 함수는 제한값을 게시할 뿐 여기서 실제 cycle delta overflow 검사를 수행하지 않습니다.'),
        ('고해상도 monotonic 기준값', 'CLOCK_MONOTONIC의 초는 xtime_sec+wall_to_monotonic.tv_sec입니다. 나노초는 tkr_mono.xtime_nsec에 wall_to_monotonic.tv_nsec를 shift만큼 왼쪽 이동한 값을 더합니다. 1초도 NSEC_PER_SEC<<shift라는 같은 스케일로 비교·차감하고 초를 증가시켜 정상화합니다. basetime의 nsec가 이 경로에서는 평범한 정수 나노초가 아니라 shift가 적용된 값입니다.'),
        ('Boottime과 raw·TAI', '정상화한 monotonic의 초·나노초를 이어 사용하여 monotonic_to_boot를 더하고 같은 스케일로 다시 정상화한 뒤 BOOTTIME을 저장합니다. MONOTONIC_RAW는 raw_sec와 tkr_raw.xtime_nsec를 CS_RAW에 직접 복사합니다. TAI는 xtime_sec+(s64)tai_offset과 tkr_mono.xtime_nsec입니다. 서로 다른 시계가 모든 필드를 동일하게 복사하는 구조는 아닙니다.'),
        ('공개 갱신의 시작과 mode', 'update_vsyscall은 vdso_write_begin으로 갱신 구간을 시작합니다. tkr_mono.clock의 vdso_clock_mode를 읽어 HRES_COARSE와 RAW 양쪽 clock_mode에 같은 값을 넣습니다. RAW 묶음의 mode를 별도의 tkr_raw.clock에서 읽는 코드라고 추정하면 안 됩니다. 이 함수 자체에는 timekeeper_lock 획득이 없으므로 sequence 구간을 writer 간 직렬화 잠금과 동일시하지 않습니다.'),
        ('Realtime과 coarse realtime', 'REALTIME의 초는 xtime_sec, nsec는 스케일이 남은 tkr_mono.xtime_nsec입니다. 주석은 time()에도 필요하다고 설명합니다. REALTIME_COARSE는 같은 초와 xtime_nsec>>shift를 저장하여 정수 나노초로 바꿉니다. 두 항목의 nsec 필드는 이름이 같아도 저장 스케일이 다릅니다.'),
        ('Coarse monotonic 정상화', 'MONOTONIC_COARSE의 초에 wall_to_monotonic.tv_sec를 더하고, shift를 제거한 나노초에 wall_to_monotonic.tv_nsec를 더합니다. __iter_div_u64_rem으로 초 몫을 초 필드에 보태고 나머지를 nsec 필드에 직접 저장합니다. 고해상도 경로와 달리 이 단계에서는 이미 정수 나노초 단위로 계산합니다.'),
        ('해상도 필드의 개별 게시', 'hrtimer_resolution을 HRES_COARSE의 hrtimer_res에 WRITE_ONCE로 저장합니다. 주석은 clock_getres가 sequence lock 없이 읽으며 두 번째 복사본이 필요 없다고 설명합니다. WRITE_ONCE는 이 필드 접근에 대한 규약이지 모든 basetime을 한 번에 원자적으로 쓰는 연산은 아닙니다.'),
        ('VDSO를 지원하지 않는 clocksource', 'clock_mode가 VDSO_CLOCKMODE_NONE이 아닐 때만 update_vdso_data를 호출합니다. 따라서 고해상도 변환 인자와 일부 basetime 갱신은 생략할 수 있지만 앞에서 처리한 mode, REALTIME, coarse 값과 hrtimer_res까지 모두 생략하는 것은 아닙니다. mode가 데이터 사용 가능 여부를 판단하는 데 중요합니다.'),
        ('아키텍처 hook과 게시 완료', '그 뒤 __arch_update_vsyscall(vdata,tk)를 호출하고 vdso_write_end로 구간을 닫은 다음 __arch_sync_vdso_data를 호출합니다. 아키텍처 추가 데이터 갱신은 sequence 구간 안, 필요할 수 있는 데이터 동기화는 end 뒤입니다. 이 파일에서 모든 아키텍처 hook이 같은 명령을 수행한다고 단정하지 않습니다.'),
        ('Timezone만 갱신하는 경로', 'update_vsyscall_tz는 HRES_COARSE의 tz_minuteswest와 tz_dsttime에 sys_tz를 대입한 뒤 arch sync를 호출합니다. 이 함수 본문에는 vdso_write_begin/end나 timekeeper_lock 획득이 없습니다. 모든 vDSO 갱신 함수가 동일한 잠금·sequence 순서를 자동 사용한다고 설명하면 안 됩니다.'),
        ('아키텍처 갱신용 begin', 'vdso_update_begin은 데이터 주소를 얻고 raw_spin_lock_irqsave로 timekeeper_lock을 잡아 interrupt 상태를 저장합니다. 이어 vdso_write_begin을 호출하고 저장 flags를 반환합니다. 주석상 timekeeping과 아키텍처 갱신의 동시 writer를 직렬화하고 reader가 불일치 자료를 사용하지 않도록 하는 구간을 엽니다.'),
        ('대응하는 end', 'vdso_update_end는 전달받은 flags로 끝냅니다. 먼저 vdso_write_end, 다음 arch sync, 마지막 raw_spin_unlock_irqrestore입니다. end가 begin의 flags를 받아야 원래 interrupt 상태를 복원할 수 있습니다. 잠금 해제보다 동기화가 먼저라는 순서와 일반 update_vsyscall에 잠금 코드가 없다는 차이를 구분합니다.'),
        ('CS와 검증 범위', '전체 함수와 설정 분기를 다뤘습니다. 공유 자료의 표현 단위, clock 좌표계 변환, writer 직렬화와 reader 재시도 규약의 차이, 아키텍처별 게시 hook을 학습합니다. 사용자 vDSO 읽기 구현이나 실제 여러 CPU의 동시 시각 조회를 실행 검증한 결과는 아닙니다.')
    ],
    questions=[
        ('고해상도와 coarse basetime의 nsec는 항상 같은 단위 표현인가?', '아니다. 고해상도 값은 shift 스케일을 유지하고 coarse는 이를 제거한다', '그렇다. 필드 이름이 같으면 둘 다 항상 정수 ns이다', 'REALTIME에는 xtime_nsec를 그대로, REALTIME_COARSE에는 >>shift한 값을 저장합니다. reader의 해석과 맞춰야 합니다.'),
        ('VDSO_CLOCKMODE_NONE이면 모든 vDSO 데이터를 갱신하지 않는가?', '아니다. 앞의 realtime/coarse/mode/해상도 갱신은 수행한다', '그렇다. 함수 첫 줄에서 즉시 반환한다', '조건문은 update_vdso_data 호출만 둘러쌉니다. 코드의 분기 범위를 끝까지 확인해야 합니다.'),
        ('update_vsyscall_tz는 본문에서 timekeeper_lock과 sequence 구간을 여는가?', '아니다. 두 필드 대입과 arch sync만 있다', '그렇다. 모든 update 함수가 같은 wrapper를 호출한다', '일반 시간 게시와 timezone 경로의 실제 코드가 다릅니다. 이름만으로 동기화 방식을 추정하지 않습니다.'),
        ('vdso_update_end의 순서는?', 'write_end, arch sync, 잠금 해제와 IRQ 복원이다', '잠금 해제 후 write_end와 arch sync이다', '구간 완료와 아키텍처 동기화를 끝낸 뒤 writer 직렬화 잠금을 해제합니다. flags는 begin에서 받은 값을 사용합니다.'),
        ('RAW 묶음의 clock_mode는 이 파일에서 어디서 가져오는가?', 'tkr_mono.clock의 vdso_clock_mode를 양쪽에 저장한다', '반드시 tkr_raw.clock에서 별도로 읽는다', '본문은 지역 clock_mode 하나로 두 묶음을 갱신합니다. cycle_last/mult 등 다른 복사 필드의 원천과 구분해야 합니다.')
    ]
)]
