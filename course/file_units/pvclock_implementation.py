"""Whole-file KVM/Xen shared pvclock implementation."""
ROWS = [dict(
    path='arch/x86/kernel/pvclock.c',
    title='Pvclock 커널 구현: CAS 단조성 보정과 wall clock 구성',
    intro='KVM·Xen이 공유하는 pvclock 구현의 모든 함수와 상태를 분석합니다.',
    principle='여러 CPU가 관찰한 시간의 최댓값은 단순 대입으로 유지할 수 없으며, 공유 스냅샷의 일관성과 시간의 단조성은 서로 다른 문제입니다.',
    use='버전 재시도와 compare-and-exchange의 역할을 구분하고, 가상 머신 정지 후 watchdog 처리와 시간 표현 범위를 이해합니다.',
    area='가상화 · 공유 메모리 · CAS · 단조성 · 고정소수점 역변환 · watchdog · 시간 ABI',
    sections=[
        ('파일 전체와 전역 상태', 'GPL-2.0-or-later 표기의 KVM/Xen 공통 코드입니다. clocksource·kernel·percpu·notifier·sched·gfp·memblock·nmi와 x86 fixmap·pvclock·vgtod 헤더를 포함합니다. valid_flags는 0으로 시작하는 __read_mostly u8, pvti_cpu0_va는 __read_mostly 포인터이고 정적 초기값은 NULL입니다. 뒤의 last_value는 0으로 초기화한 전역 atomic64_t입니다. __read_mostly는 이 값들을 불변이나 원자적 객체로 만드는 선언이 아닙니다.'),
        ('지원 플래그 등록', 'pvclock_set_flags는 valid_flags=flags로 대입합니다. OR로 기능을 누적하거나 각 vCPU의 src->flags를 직접 바꾸는 함수가 아닙니다. 읽은 플래그 중 kernel이 인정하는 비트를 고르는 기준을 설정합니다. 함수 본문에 별도 락·버전 변경·메모리 장벽은 없습니다.'),
        ('TSC 주파수의 역변환', 'pvclock_tsc_khz는 u64 값 1000000ULL<<32를 tsc_to_system_mul로 do_div한 뒤 shift가 음수면 왼쪽, 그 외면 오른쪽으로 이동합니다. 시간 변환에서 shift가 양수일 때 cycle delta를 늘리는 것과 반대 방향입니다. 계수=0x80000000, shift=0이면 2000000 kHz, shift=1이면 1000000 kHz입니다. 먼저 정수 나눗셈을 수행하므로 실수 연산과 같은 무한 정밀도를 갖지 않습니다.'),
        ('주파수 함수의 입력 계약', 'pvclock_tsc_khz는 unsigned long을 반환하지만 중간 계산은 u64입니다. 32비트 환경에서 반환 폭도 고려해야 합니다. 이 함수에는 0 계수 검사, 이동량 검사, 버전 재시도가 없으므로 유효하고 일관된 계수의 제공은 호출 문맥의 책임입니다. 공유 필드를 읽는 모든 함수가 자동으로 같은 스냅샷 보호를 갖는 것은 아닙니다.'),
        ('Watchdog 묶음 갱신', 'pvclock_touch_watchdogs는 touch_softlockup_watchdog_sync, clocksource_touch_watchdog, rcu_cpu_stall_reset, reset_hung_task_detector를 순서대로 호출합니다. 가상 머신이 멈춘 시간을 guest 내부 작업의 정지로 오인하는 상황에 대응하는 경로입니다. wall clock을 재설정하거나 last_value를 0으로 만드는 함수는 아닙니다.'),
        ('Resume와 보정 상태', 'pvclock_resume는 atomic64_set으로 last_value만 0으로 돌립니다. valid_flags, pvti_cpu0_va, hypervisor 공유 페이지의 system_time을 여기서 초기화하지 않습니다. 따라서 아래의 단조성 보정 설명은 이 명시적 초기화 경계를 함께 고려해야 합니다.'),
        ('플래그 읽기의 스냅샷과 마스킹', 'pvclock_read_flags는 pvclock_read_begin, src->flags 읽기, pvclock_read_retry를 반복한 후 flags & valid_flags를 반환합니다. raw flags 전체를 그대로 공개하지 않습니다. 예를 들어 src flags가 3이고 valid_flags가 1이면 반환은 1입니다. 버전 프로토콜은 공유 스냅샷의 일관성, AND는 허용 비트 선택이라는 서로 다른 목적입니다.'),
        ('시간과 플래그를 함께 읽는 루프', '__pvclock_clocksource_read(src, dowd)는 begin과 retry 사이에서 rdtsc_ordered 기반 __pvclock_read_cycles 결과 ret와 src->flags를 함께 읽습니다. 재시도가 끝난 뒤에야 watchdog 및 단조성 처리를 수행합니다. 이 단계가 전역 last_value 갱신과 같은 원자적 트랜잭션인 것은 아닙니다.'),
        ('Guest stopped 처리 조건', 'dowd가 참이고 읽은 flags에 PVCLOCK_GUEST_STOPPED가 있으면 src->flags &= ~PVCLOCK_GUEST_STOPPED로 비트를 지우고 pvclock_touch_watchdogs를 호출합니다. 이 조건은 valid_flags와 AND한 결과가 아니라 스냅샷에서 얻은 flags를 사용합니다. 따라서 valid_flags가 0이어도 일반 read 경로는 stopped 처리를 할 수 있습니다. 비트 지우기는 본문상 일반 read-modify-write이며 별도 CAS로 작성되어 있지 않습니다.'),
        ('안정된 TSC 빠른 반환', 'valid_flags와 읽은 flags 양쪽 모두 PVCLOCK_TSC_STABLE_BIT를 갖는 경우 ret를 즉시 반환합니다. 전역 last_value를 읽거나 갱신하지 않습니다. src의 stable bit 하나만 있거나 kernel 허용 비트 하나만 있는 경우에는 충분하지 않습니다. watchdog 처리는 이 빠른 반환보다 앞에서 수행됩니다.'),
        ('전역 최댓값 보정의 읽기 경로', '안정 비트 빠른 경로를 쓰지 않으면 raw_atomic64_read로 last를 얻습니다. ret<=last이면 last를 반환하여 관찰한 시간보다 뒤로 가는 작은 오차를 보정합니다. ret==last도 그대로 반환하므로 엄격히 증가하는 고유 타임스탬프를 만드는 기능은 아닙니다. 주석은 시간 차이가 작은 오차 범위에 있다는 전제를 명시합니다.'),
        ('CAS 갱신과 실패 재시도', 'ret>last이면 raw_atomic64_try_cmpxchg(&last_value, &last, ret)를 시도합니다. 성공하면 ret를 반환합니다. 실패하면 expected 인수 last가 새 관찰값으로 갱신되므로 루프 맨 위에서 ret<=last를 다시 판단합니다. 예를 들어 last=100을 본 두 CPU가 110과 105를 쓰려 할 때 110이 먼저 성공하면 105 쪽은 실패 후 last=110을 보고 110을 반환합니다. 단순 대입이라면 뒤늦은 105가 110을 덮어쓸 수 있습니다.'),
        ('단조성 보장의 정확한 범위', '주석은 last 관찰과 함수 반환 사이에 다른 CPU가 더 큰 값을 게시할 수 있음을 인정합니다. 동시 호출의 반환 순간마다 반드시 전역 최신값을 돌려준다는 보장은 아닙니다. 핵심은 보정 경로에서 last_value를 작은 값으로 덮어쓰지 않고 이미 관찰한 last보다 작은 값을 돌려주지 않는 것입니다. stable bit 빠른 경로는 외부 시계의 안정성 계약에 의존하고 resume은 상태를 명시적으로 초기화합니다.'),
        ('두 공개 read 함수', 'pvclock_clocksource_read는 공통 helper에 true를 전달합니다. noinstr pvclock_clocksource_read_nowd는 false를 전달하여 stopped 비트 지우기와 watchdog 묶음 호출을 건너뜁니다. nowd도 버전 재시도, 실제 시간 계산, stable 판정, 필요 시 CAS 보정은 수행합니다. 함수 이름을 보고 모든 검사나 보정이 빠진다고 해석하면 안 됩니다.'),
        ('Wall clock 기준 스냅샷', 'pvclock_read_wallclock은 wall_clock->version을 읽고 rmb 후 sec·nsec를 now에 복사한 뒤 다시 rmb를 실행합니다. 끝에서 현재 version이 홀수이거나 처음 version과 다르면 반복합니다. pvclock_vcpu_time_info용 begin helper를 그대로 호출하는 구현이 아니며, wall clock 구조체의 별도 버전을 사용합니다.'),
        ('Wall clock 계산과 ABI 한계', '주석은 u32 wall_clock->sec가 1970~2106년 범위만 저장할 수 있으며 더 먼 기준 시각을 위해서는 확장된 구조체와 새 hypercall 인터페이스가 필요하다고 설명합니다. 출력이 timespec64라고 입력 ABI의 초 필드까지 64비트가 되는 것은 아닙니다. 스냅샷 뒤 pvclock_clocksource_read(vcpu_time)의 부팅 이후 시간을 delta에 받고, 기준 sec*NSEC_PER_SEC+nsec를 더합니다. do_div의 몫을 now.tv_sec, 나머지를 now.tv_nsec에 배치하고 set_normalized_timespec64로 출력합니다. 예를 들어 기준 10초 900000000ns에 200000000ns를 더하면 11초 100000000ns입니다.'),
        ('CPU 0 주소 게시와 경고', 'pvclock_set_pvti_cpu0_va는 vclock_was_used(VDSO_CLOCKMODE_PVCLOCK)에 WARN_ON한 뒤 포인터를 대입합니다. 경고 조건이 참이라고 함수가 즉시 return하거나 대입을 취소하는 코드는 없습니다. getter는 저장한 포인터를 반환하며 이 파일의 EXPORT_SYMBOL_GPL은 getter에 붙습니다. setter나 다른 함수까지 모두 export된 것으로 확대해서 읽지 않습니다.'),
        ('CS 연결과 검증 범위', '전역 상태, 모든 함수, helper의 분기와 반복, export를 다뤘습니다. 버전 스냅샷은 읽는 자료의 일관성을, CAS는 경쟁하는 전역 최댓값 갱신을 해결합니다. 문제의 계산과 경쟁 예시는 원본 코드에 따른 추론이며 실제 VM 정지·resume이나 CPU 간 경쟁을 실행한 시험은 아닙니다.')
    ],
    questions=[
        ('valid_flags=0이고 src flags에 GUEST_STOPPED가 있으면 일반 pvclock_clocksource_read는 watchdog을 갱신하는가?', '그렇다. stopped 처리는 valid_flags가 아니라 raw flags와 dowd를 검사한다', '아니다. valid_flags가 0이면 모든 동작이 즉시 반환한다', '일반 read는 dowd=true입니다. stopped 분기는 valid_flags와 독립이며 stable 빠른 경로보다 먼저 수행됩니다.'),
        ('src에 TSC_STABLE_BIT만 있으면 전역 CAS 보정을 항상 건너뛰는가?', '아니다. valid_flags에도 같은 비트가 있어야 한다', '그렇다. kernel의 valid_flags는 단조성 경로와 무관하다', '빠른 반환의 조건은 두 비트 검사의 AND입니다. hypervisor 표시와 kernel이 인정하는 기능이 모두 맞아야 합니다.'),
        ('last=100에서 두 CPU의 ret가 각각 110과 105이고 110의 CAS가 먼저 성공하면 105 쪽은?', 'CAS 실패로 last=110을 다시 관찰하여 110을 반환한다', '실패 후 무조건 105를 대입해 전역 시간을 뒤로 옮긴다', 'try_cmpxchg 실패 시 expected 변수 last가 갱신됩니다. 루프 상단의 ret<=last 검사가 작은 값을 다시 쓰지 않도록 막습니다.'),
        ('pvclock_clocksource_read_nowd는 무엇을 생략하는가?', 'GUEST_STOPPED 비트 지우기와 watchdog 묶음 호출이다', '버전 재시도와 모든 단조성 보정이다', 'nowd는 공통 helper에 false만 전달합니다. snapshot 읽기와 stable/CAS 경로는 계속 수행합니다.'),
        ('mul=0x80000000이고 shift=1일 때 pvclock_tsc_khz의 결과는?', '1000000 kHz이다', '4000000 kHz이다', '먼저 (1000000*2^32)/2^31=2000000을 계산하고 양수 shift에서는 오른쪽으로 1비트 이동하여 1000000을 얻습니다. cycle-to-time 변환과 역방향임에 주의합니다.'),
        ('timespec64 출력이면 pvclock_wall_clock의 기준 sec 범위도 자동으로 넓어지는가?', '아니다. 입력 ABI의 sec는 여전히 u32이다', '그렇다. 출력형만 바꾸면 공유 메모리의 필드 폭도 64비트가 된다', '정보는 입력 구조체의 범위에 제한됩니다. 주석은 더 먼 기준 날짜를 위해 확장 ABI가 필요하다고 명시합니다.'),
        ('CPU 0 주소 setter의 WARN_ON이 발생하면 포인터 대입을 생략하는가?', '아니다. 원본은 경고 뒤에도 대입한다', '그렇다. WARN_ON은 항상 함수를 즉시 종료한다', '경고 매크로와 제어 흐름을 구별해야 합니다. 이 함수에는 조건부 return이 없으므로 경고 조건만 보고 setter 실패를 추정하면 안 됩니다.')
    ]
)]
