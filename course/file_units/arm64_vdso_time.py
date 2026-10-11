"""Whole-file ARM64 vDSO clock modes and time access hooks."""
ROWS = [dict(
    path='arch/arm64/include/asm/vdso/clocksource.h',
    title='ARM64 vDSO 시계 모드: compat 지원의 구분',
    intro='두 아키텍처 시계 모드와 공통 enum으로의 연결을 분석합니다.',
    principle='시계 장치 종류뿐 아니라 사용자 ABI의 지원 범위도 모드 계약의 일부입니다.',
    use='32비트 호환 task와 64비트 task에 허용되는 모드를 구별합니다.',
    area='전처리 · enum 확장 · ABI 호환성 · 기능 구분',
    sections=[
        ('전체 정의', 'GPL-2.0과 __ASM_VDSOCLOCKSOURCE_H guard 아래 VDSO_ARCH_CLOCKMODES 매크로 하나를 정의합니다. 두 enum 항목 이름을 쉼표로 연결한 토큰 목록이며 여기서 독립적인 enum 형이나 변수를 선언하지 않습니다. 별도 include나 실행 함수도 없습니다.'),
        ('두 모드의 계약', 'VDSO_CLOCKMODE_ARCHTIMER는 주석상 32비트와 64비트 task 모두를 위한 모드입니다. VDSO_CLOCKMODE_ARCHTIMER_NOCOMPAT는 64비트 task만을 위한 모드입니다. NOCOMPAT를 타이머 자체가 존재하지 않는다는 의미로 읽으면 안 됩니다. 실제 사용 여부 검사와 syscall 전환은 이 매크로 바깥의 코드에서 수행합니다.'),
        ('공통 enum과 범위', 'include/vdso/clocksource.h의 공통 enum에서 NONE 뒤에 이 토큰 목록이 삽입되는 문맥에서는 ARCHTIMER가 1, ARCHTIMER_NOCOMPAT가 2가 됩니다. 이 헤더 자체가 숫자를 직접 지정한 것은 아닙니다. 전체 정의와 주석을 설명했으며 compat 구현이나 타이머 드라이버 전체를 함께 완료로 집계하지 않습니다.')
    ],
    questions=[
        ('ARCHTIMER_NOCOMPAT에 대한 이 파일의 설명은?', '64비트 task만을 위한 vDSO clocksource 모드이다', '모든 task에서 타이머를 사용하지 못한다는 모드이다', '주석은 64bit tasks only라고 구분합니다. 호환 ABI의 지원 범위와 타이머 자체의 존재 여부는 다릅니다.'),
        ('VDSO_ARCH_CLOCKMODES가 여기서 독립 enum 객체를 만드는가?', '아니다. 공통 enum에 삽입할 두 항목의 토큰 목록이다', '그렇다. 부팅 시 두 시계를 등록하는 전역 객체이다', '매크로 확장과 런타임 등록은 다른 단계입니다. 이 파일에는 enum 본문이나 등록 함수 호출이 없습니다.')
    ]
), dict(
    path='arch/arm64/include/asm/vdso/gettimeofday.h',
    title='ARM64 vDSO 시간 조회: SVC fallback과 ECV 카운터',
    intro='세 syscall fallback과 하드웨어 카운터 읽기, 시간 namespace 데이터 getter를 전체 분석합니다.',
    principle='아키텍처별 호출 규약과 명령 순서를 공통 시간 알고리즘에 연결하면서 갱신 경쟁은 공통 재시도 계약과 함께 처리합니다.',
    use='x0·x1·x8의 syscall 역할, ECV 명령 대체, 경쟁 중 반환한 0의 의미를 설명합니다.',
    area='ARM64 ABI · 시스템 호출 · 인라인 어셈블리 · 명령 순서 · CPU 기능 대체 · 버전 재시도',
    sections=[
        ('전체 구성', 'GPL-2.0 include guard와 !__ASSEMBLY__ 안에서 alternative·barrier·unistd·sysreg 헤더를 포함합니다. VDSO_HAS_CLOCK_GETRES를 1로 정의합니다. 이 파일에는 VDSO_HAS_TIME 정의나 time fallback 함수가 없습니다. 함수 시그니처의 시간 구조체와 vdso_data 등은 포함 문맥에 의존합니다.'),
        ('Gettimeofday 시스템 호출', 'gettimeofday_fallback은 __kernel_old_timeval *tv를 x0, timezone *tz를 x1, __NR_gettimeofday를 x8에 연결한 register 변수를 사용합니다. asm volatile의 svc #0 실행 결과를 x0의 long ret로 받고 int로 반환합니다. memory clobber를 명시하며 여기서 libc errno를 설정하지 않습니다. tv나 tz의 NULL 처리를 별도로 구현하지 않고 호출에 전달합니다.'),
        ('Clock_gettime 시스템 호출', 'clock_gettime_fallback은 clockid_t를 x0, __kernel_timespec *를 x1, __NR_clock_gettime를 x8에 두고 svc #0을 실행합니다. long ret를 long 반환형으로 그대로 돌려줍니다. 어느 clock ID를 빠른 경로로 처리할지는 이 fallback 본문에 없으며 실제로 호출된 경우 커널 진입을 수행합니다.'),
        ('Clock_getres와 반환형 차이', 'clock_getres_fallback은 같은 x0·x1 배치를 사용하고 syscall 번호만 __NR_clock_getres입니다. ret 레지스터 변수는 long이지만 함수 반환형은 int입니다. gettimeofday도 int, clock_gettime만 long이라는 원본 시그니처 차이를 구분합니다. 세 함수 모두 asm volatile과 memory clobber가 있지만 이것이 공유 데이터의 writer lock을 잡는다는 뜻은 아닙니다.'),
        ('카운터 읽기의 NONE 분기', '__arch_get_hw_counter(s32 clock_mode, const vdso_data *vd)는 clock_mode가 NONE이면 0을 반환합니다. 주석은 공통 코드의 모드 확인 이후 동시 갱신과 경쟁한 경우이며 공통 코드가 다시 읽어 모드 변경을 보고 syscall fallback하도록 설명합니다. 이 0을 유효한 현재 시각으로 즉시 확정하거나 x86의 U64_MAX 오류 sentinel과 동일시하지 않습니다. vd 인수는 본문에서 사용하지 않습니다.'),
        ('일반 카운터 명령과 ECV 대체', 'NONE이 아니면 ALTERNATIVE 안에서 기본 isb와 mrs cntvct_el0, ARM64_HAS_ECV일 때 nop와 SYS_CNTVCTSS_EL0 읽기라는 두 명령열을 제공합니다. 주석은 ECV의 카운터가 self-synchronizing이며 기본 경로에서는 카운터 값의 추측 실행을 막기 위해 isb가 필요하다고 설명합니다. 시간 단위 변환이나 시스템 호출 번호 선택과는 별개의 CPU 기능에 따른 명령 대체입니다.'),
        ('읽기 후 순서와 반환값', '어셈블리는 res 레지스터 출력과 memory clobber를 사용합니다. 이어 arch_counter_enforce_ordering(res)를 호출한 다음 res를 반환합니다. 이 헤더에서는 나노초로 환산하거나 scale·offset을 곱하지 않습니다. helper 내부의 구체 장벽 구현까지 이 파일에 들어 있는 것은 아닙니다. NONE 외의 모드를 하나씩 열거해서 검사하는 switch도 없습니다.'),
        ('공유 데이터 주소 getter', '__arch_get_vdso_data는 _vdso_data를 반환합니다. CONFIG_TIME_NS가 켜졌을 때 __arch_get_timens_vdso_data는 vd 인수를 사용하지 않고 _timens_data를 반환합니다. namespace 설정이 꺼진 else getter stub는 없습니다. 두 함수는 데이터 주소를 제공하며 여기서 페이지를 할당·매핑하거나 namespace offset을 더하지 않습니다.'),
        ('공통 코드와 아키텍처 경계', 'syscall 진입과 raw 카운터 읽기는 여기서 구현하고, 공유 데이터 버전 재시도·clock ID 선택·시간 계산은 공통 구현과 협력합니다. 특히 NONE 분기의 안전성을 이 함수 하나의 숫자 반환만으로 판단할 수 없습니다. compat용 ARCHTIMER_NOCOMPAT 정책도 이 파일의 명시적 분기로 구현되어 있지 않습니다.'),
        ('CS 연결과 검증 범위', '모든 함수와 전처리 분기·기능 매크로를 설명했습니다. syscall 레지스터 ABI, 명령 순서, CPU 기능별 코드 선택, 공유 데이터 재시도 계약이 핵심입니다. 원본과 설명을 대조했으며 실제 ARM64 또는 ECV 하드웨어 실행이나 compat 사용자 프로그램 실행 검증은 수행하지 않았습니다.')
    ],
    questions=[
        ('ARM64 clock_gettime fallback에서 syscall 번호와 출력 포인터는 각각 어디에 있는가?', '번호는 x8, 출력 포인터는 x1이다', '번호는 x0, 출력 포인터는 x8이다', 'x0에는 clock ID를 전달하고 반환 때 결과를 받습니다. syscall 번호는 x8로 별도 전달됩니다.'),
        ('카운터 함수가 NONE 모드에서 0을 반환하면 현재 시간이 0으로 확정되는가?', '아니다. 공통 코드의 재시도가 모드 변경을 확인하고 fallback하는 계약이다', '그렇다. 함수가 즉시 epoch 0을 사용자에게 반환한다', '함수는 원시 카운터 hook입니다. 주석은 모드 확인 후 갱신과의 경쟁을 설명하며 반환한 숫자만으로 최종 시간을 결정하지 않습니다.'),
        ('ARM64_HAS_ECV 경로는 기본 카운터 읽기와 어떻게 다른가?', 'self-synchronizing CNTVCTSS 읽기를 선택하고 기본 isb 자리는 nop이다', '항상 svc #0으로 시간을 읽는다', 'ALTERNATIVE는 기본 isb+CNTVCT 읽기와 nop+CNTVCTSS 읽기를 구분합니다. syscall fallback 함수와 다른 코드 경로입니다.'),
        ('__arch_get_timens_vdso_data가 namespace offset을 직접 시간에 더하는가?', '아니다. _timens_data 주소를 반환한다', '그렇다. vd에 offset을 더해 새 구조체를 할당한다', '본문은 주소 반환뿐이고 vd 인수도 사용하지 않습니다. 실제 offset 연산과 메모리 할당을 getter에 있다고 추정하면 안 됩니다.')
    ]
)]
