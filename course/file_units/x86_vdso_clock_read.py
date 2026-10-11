"""Whole-file x86 vDSO fallback, virtual clocks, and cycle conversion."""
ROWS = [dict(
    path='arch/x86/include/asm/vdso/gettimeofday.h',
    title='X86 vDSO 시계 읽기: syscall fallback·가상화·역행 방지',
    intro='아키텍처별 시간 조회 지원 함수 전체를 읽고 빠른 경로의 실패와 수치 경계를 분석합니다.',
    principle='빠른 사용자 공간 시간 조회도 ABI, 공유 데이터의 일관성, 잘못된 카운터 값, 정수 오버플로를 함께 다뤄야 합니다.',
    use='vDSO가 시스템 호출로 전환하는 이유와 가상화 시계 페이지의 접근 순서, TSC 역행 보정의 동작을 설명합니다.',
    area='시스템 호출 ABI · 인라인 어셈블리 · 메모리 순서 · 가상화 · 버전 재시도 · 고정소수점 · 정수 오버플로',
    sections=[
        ('파일 전체 범위', 'GPL-2.0 표기와 include guard 안에서 !__ASSEMBLY__일 때만 C 내용을 제공합니다. uapi/linux/time.h, vgtod, vvar, unistd, msr, pvclock, Hyper-V timer 헤더에 의존합니다. 이 자료는 모든 선언·매크로·fallback·시계 읽기·변환 함수를 설명하며 포함된 헤더 전체를 함께 완료 처리하지 않습니다.'),
        ('데이터 주소와 기능 표시', '__vdso_data는 VVAR(_vdso_data), __timens_vdso_data는 TIMENS(_vdso_data)로 연결합니다. VDSO_HAS_TIME과 VDSO_HAS_CLOCK_GETRES는 1입니다. 이는 공통 구현에 기능을 알리는 빌드 매크로이며 모든 clock ID가 사용자 공간에서 성공한다는 보장은 아닙니다. CONFIG_TIME_NS 아래 __arch_get_timens_vdso_data는 인수 vd를 사용하지 않고 namespace용 데이터 주소를 반환합니다.'),
        ('외부 시계 페이지 선언', 'CONFIG_PARAVIRT_CLOCK일 때 pvclock_page, CONFIG_HYPERV_TIMER일 때 hvclock_page를 hidden visibility 외부 객체로 선언합니다. 두 선언은 const가 아닙니다. 주석은 내용이 계속 바뀌므로 컴파일러가 불변 객체로 취급하게 하면 안 된다고 설명합니다. 해당 시계가 비활성이면 페이지 읽기가 fault를 낼 수 있으므로 주소가 선언되었다고 무조건 역참조하면 안 됩니다.'),
        ('Fallback 분기의 기준', '#ifndef BUILD_VDSO32는 syscall 명령을 쓰는 경로이며 else는 __kernel_vsyscall을 호출하는 32비트 경로입니다. 여기의 매크로 이름은 BUILD_VDSO32_64와 다릅니다. 함수들은 long ret를 그대로 반환하며 이 파일에서 libc의 errno를 설정하거나 음수 결과를 -1로 다시 포장하지 않습니다.'),
        ('비32비트 clock fallback 두 개', 'clock_gettime_fallback과 clock_getres_fallback은 __kernel_timespec *를 받고 각각 __NR_clock_gettime과 __NR_clock_getres를 사용합니다. a 레지스터 출력 ret와 같은 레지스터의 syscall 번호 입력을 연결하고 D에 clock ID, S에 출력 포인터를 둡니다. =m (*_ts)는 출력 메모리 피연산자이며 rcx와 r11을 clobber로 명시합니다. C 코드가 별도 복사 루프를 실행한다는 뜻은 아닙니다.'),
        ('비32비트 gettimeofday fallback', 'gettimeofday_fallback은 old_timeval 포인터와 timezone 포인터를 D와 S로 전달하고 __NR_gettimeofday를 호출합니다. 원본의 clobber 목록은 memory이며 앞의 두 clock 함수와 동일하게 적혀 있지 않습니다. memory clobber는 컴파일러에 메모리 효과를 알리는 표현이지 CPU 메모리 장벽 명령 자체가 아닙니다. 어셈블리 계약의 차이를 원본 그대로 구별해야 합니다.'),
        ('32비트 호출과 EBX 보존', '32비트의 다섯 fallback은 EBX를 EDX에 저장한 뒤 첫 인수를 EBX로 옮기고 __kernel_vsyscall을 call한 후 EBX를 복구합니다. 둘째 인수 포인터는 c 제약으로 전달하고 EDX를 clobber로 표시합니다. 이 파일이 int 0x80이나 sysenter를 직접 선택하는 것은 아닙니다. 실제 진입 방식은 호출 대상 구현의 책임입니다.'),
        ('32비트 clock_gettime의 두 ABI', 'clock_gettime_fallback은 __kernel_timespec *와 __NR_clock_gettime64를 사용합니다. clock_gettime32_fallback은 old_timespec32 *와 __NR_clock_gettime를 사용합니다. 접미사 없는 내부 fallback 함수가 이 분기에서는 time64 syscall을 사용한다는 점이 중요합니다. 두 함수 모두 =m (*_ts) 출력, clock의 g 제약, 포인터의 c 제약을 갖습니다.'),
        ('32비트 getres와 gettimeofday', 'clock_getres_fallback은 __kernel_timespec *와 __NR_clock_getres_time64, clock_getres32_fallback은 old_timespec32 *와 __NR_clock_getres를 사용합니다. gettimeofday_fallback은 __NR_gettimeofday를 사용하고 tv를 EBX, tz를 ECX에 전달하며 memory와 edx를 clobber로 표시합니다. time64 지원이 모든 구형 시간 구조체를 자동 변경하는 것은 아닙니다.'),
        ('Pvclock이 vCPU 0을 쓰는 전제', 'vread_pvclock은 pvclock_page.pvti를 가리킵니다. 주석은 사용자 공간 선점과 기반 CPU 변경을 hypervisor가 완전히 추적하지 못할 수 있다고 설명합니다. PVCLOCK_TSC_STABLE_BIT를 모든 vCPU에서 pvti가 호환되고 TSC가 동기화되었다는 전제로 해석하여 vCPU 0 페이지를 사용합니다. 현재 실행 중인 vCPU 번호를 매번 읽어 배열을 선택하는 코드는 없습니다.'),
        ('Pvclock 버전 재시도와 실패', 'do 루프에서 pvclock_read_begin으로 버전을 얻고 stable bit가 없으면 즉시 U64_MAX를 반환합니다. 안정 상태에서는 rdtsc_ordered 결과를 __pvclock_read_cycles에 넘기고 pvclock_read_retry가 참이면 다시 계산합니다. 성공 반환은 ret & S64_MAX입니다. 버전 재시도는 일관된 자료를 얻는 방식이며 writer lock을 획득하는 방식이 아닙니다. 읽기 루프의 재시도 횟수 상한은 이 함수에 없습니다.'),
        ('Hyper-V 읽기', 'vread_hvclock은 hv_read_tsc_page_tsc에 페이지와 tsc·time 출력 주소를 넘깁니다. 성공이면 time & S64_MAX, 실패면 U64_MAX를 반환합니다. 별도로 반환된 tsc를 이 함수에서 time 대신 반환하지 않습니다. 페이지의 내부 버전 프로토콜은 호출된 helper에 있습니다.'),
        ('하드웨어 카운터 선택', '__arch_get_hw_counter는 먼저 likely TSC 모드이면 rdtsc_ordered 결과를 S64_MAX로 마스킹합니다. 이후 빌드에 포함된 PVCLOCK/HVCLOCK 모드만 각각 vread_pvclock/vread_hvclock으로 보냅니다. 해당 설정이 없거나 지원하지 않는 clock_mode이면 U64_MAX입니다. vd 인수 자체는 본문에서 사용하지 않습니다.'),
        ('컴파일러 장벽의 위치', 'PVCLOCK/HVCLOCK의 모드 비교가 참인 블록 안에서 barrier() 후 페이지 읽기 함수를 호출합니다. 목적은 컴파일러가 메모리 읽기를 모드 검사 앞으로 끌어올려 비활성 페이지를 건드리는 일을 막는 것입니다. 이를 모든 CPU의 시계를 동기화하는 명령이나 일반적인 writer lock으로 설명하면 잘못입니다. TSC 경로의 rdtsc_ordered와도 역할을 구분해야 합니다.'),
        ('데이터 getter와 두 유효성 hook', '__arch_get_vdso_data는 __vdso_data를 반환합니다. arch_vdso_clocksource_ok는 vd를 검사하지 않고 true이며 vdso_clocksource_ok 매크로로 연결됩니다. 반면 arch_vdso_cycles_ok는 (s64)cycles >= 0을 검사하고 vdso_cycles_ok로 연결됩니다. 모드 검사 hook이 true여도 실제 카운터 읽기의 실패가 무시되는 것은 아닙니다. 공통 구현은 cycle 유효성을 따로 확인합니다.'),
        ('오류 sentinel과 유효 범위', 'U64_MAX는 최상위 비트가 1이므로 signed s64 검사에서 음수가 되어 거부됩니다. 검사 대상은 U64_MAX 하나만이 아니라 최상위 비트가 설정된 모든 값입니다. 성공한 TSC·PV·HV 값에서 S64_MAX 마스크로 해당 비트를 지우는 이유가 여기에 있습니다. 원시 카운터의 64비트를 모두 시간 계산에 사용하는 계약과 다릅니다.'),
        ('나노초 변환의 정상 경로', 'vdso_calc_ns는 u64 delta = cycles - vd->cycle_last를 먼저 계산합니다. delta <= max_cycles이면 ((delta * mult) + base) >> shift를 반환합니다. base는 같은 스케일의 기준 나노초 부분이며 단순한 초 단위 값이 아닙니다. 예를 들어 last=100, cycles=120, mult=3, base=400, shift=2이고 max_cycles>=20이면 (20*3+400)>>2 = 115입니다.'),
        ('역행과 unsigned 뺄셈', 'cycles가 last보다 조금 작으면 unsigned 뺄셈 결과가 아주 커져 delta > max_cycles의 드문 경로에 들어갑니다. 거기서 delta의 bit 62가 설정되었으면 base >> shift를 반환합니다. 예를 들어 last=100, cycles=99이면 delta=2^64-1이므로 bit 62가 1이고 새 경과 시간을 더하지 않습니다. 소켓 사이 TSC 오차가 거대한 미래 시간으로 바뀌는 것을 막습니다.'),
        ('Bit 62와 큰 delta의 처리', '유효 카운터 폭이 S64_MAX 마스크의 63비트이므로 역행 판정에서 사용하는 비트는 bit 63이 아니라 bit 62입니다. 실제 코드는 cycles < last를 직접 비교하는 대신 delta > max_cycles 안에서 이 비트를 검사합니다. 역행으로 분류되지 않은 큰 delta는 delta & S64_MAX, mult, base, shift를 mul_u64_u32_add_u64_shr로 전달하여 큰 곱을 처리합니다. 이 helper 호출을 오류 반환으로 오해하지 않습니다.'),
        ('공통 구현 교체와 한계', '#define vdso_calc_ns vdso_calc_ns는 자기 자신 이름의 매크로를 정의하여 공통 구현의 #ifndef 검사를 막는 선택 표식입니다. 재귀적으로 함수를 호출하는 코드가 아닙니다. 함수는 vd->mask를 사용하지 않으며 일반 공통 변환과 달리 x86의 역행·유효 비트 계약을 반영합니다. 전체 파일 설명과 원본 대조를 수행했지만 실제 x86 ABI별 실행, hypervisor 무효화 경쟁, CPU 간 TSC 오차를 재현한 시험은 아닙니다.')
    ],
    questions=[
        ('BUILD_VDSO32에서 clock_gettime_fallback이 사용하는 syscall 번호는?', '__NR_clock_gettime64이다', '__NR_clock_gettime32이다', '이 함수는 __kernel_timespec 출력 경로입니다. 구형 old_timespec32용 clock_gettime32_fallback이 __NR_clock_gettime를 사용하므로 함수 접미사와 syscall 이름을 각각 확인해야 합니다.'),
        ('가상화 시계의 모드 검사 뒤 barrier()를 두는 직접적인 이유는?', '컴파일러가 비활성 시계 페이지의 읽기를 검사 앞으로 옮기지 못하게 하기 위해서다', '모든 가상 CPU의 TSC 값을 같은 숫자로 다시 설정하기 위해서다', '비활성 페이지를 건드리면 fault가 날 수 있습니다. 컴파일러 접근 순서를 제약하는 것과 하드웨어 시계 값을 변경하는 것은 서로 다른 작업입니다.'),
        ('Pvclock의 stable bit가 없으면 vread_pvclock은 어떻게 동작하는가?', 'U64_MAX를 반환한다', '어떤 경우든 vCPU 0 자료가 정확하므로 그대로 시간을 반환한다', 'vCPU 0 자료를 다른 vCPU에서도 사용할 수 있다는 전제가 필요합니다. 이 비트가 없으면 함수가 즉시 실패 sentinel을 반환하고 공통 경로의 cycle 검사가 이를 거부합니다.'),
        ('arch_vdso_clocksource_ok가 true이면 시간 조회가 항상 성공하는가?', '아니다. 실제 cycle 읽기와 vdso_cycles_ok 검사에서 실패할 수 있다', '그렇다. 이후 U64_MAX도 정상 시간으로 처리한다', '지원하지 않는 모드나 무효화된 가상 시계는 U64_MAX를 반환할 수 있습니다. (s64)cycles >= 0 검사는 그 값의 최상위 비트 때문에 실패합니다.'),
        ('왜 성공 카운터 값에 S64_MAX를 AND하는가?', '최상위 비트를 오류 표시용으로 비워 두는 유효성 검사와 맞추기 위해서다', '나노초를 마이크로초로 바꾸는 나눗셈이기 때문이다', '마스크는 하위 63비트를 남깁니다. 단위 변환이 아니라 유효 값과 음수로 해석되는 sentinel을 구분하는 계약입니다.'),
        ('last=100, cycles=99일 때 작은 TSC 역행을 어떻게 처리하는가?', '큰 unsigned delta의 bit 62를 확인하여 base >> shift를 반환한다', '2^64-1 cycle을 정상 경과 시간으로 곱해 거대한 미래 시간을 반환한다', 'unsigned 뺄셈은 wrap되지만 max_cycles 경계와 bit 검사가 특별 처리를 선택합니다. 기준 시간에 머무르는 대신 전체 시간 값을 0으로 만드는 것은 아닙니다.'),
        ('max_cycles 이내이고 delta=20, mult=3, base=400, shift=2이면 반환값은?', '115이다', '460이다', '먼저 20*3+400=460을 구한 뒤 오른쪽으로 2비트 이동하여 115를 얻습니다. shift를 빠뜨리면 스케일이 다른 값이 됩니다.'),
        ('#define vdso_calc_ns vdso_calc_ns의 역할은?', '공통 코드가 기본 함수를 정의하지 않도록 매크로 존재를 표시한다', '같은 함수를 무한히 재귀 호출한다', '매크로 존재 검사와 함수 호출은 다릅니다. 공통 gettimeofday.c의 #ifndef vdso_calc_ns는 x86 전용 계산 함수가 제공되었음을 이 표식으로 확인합니다.')
    ]
)]
