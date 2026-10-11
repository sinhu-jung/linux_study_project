"""Whole-file RISC-V time wrappers, kernel data getter, and clock mode."""
ROWS = [dict(
    path='arch/riscv/kernel/vdso/vgettimeofday.c',
    title='RISC-V 시간 진입점: 세 __vdso 함수의 공통 구현 위임',
    intro='clock_gettime·gettimeofday·clock_getres wrapper 전체를 자료형과 함께 읽습니다.',
    principle='아키텍처 진입점의 역할과 공통 시간 알고리즘의 역할을 분리하면 같은 구현을 다른 ABI에 연결할 수 있습니다.',
    use='공개 심볼 이름과 출력 구조체, 오류 전달의 실제 범위를 설명합니다.',
    area='ABI · wrapper · 코드 재사용 · 시간 구조체',
    sections=[
        ('전체 구성', 'GPL-2.0과 ARM64 소스에서 복사했다는 이력 뒤 linux/time.h, linux/types.h, vdso/gettime.h를 포함합니다. 세 함수 본문을 정의합니다. 이력상 출처가 같아도 ARM64의 __kernel 이름과 여기의 __vdso 이름을 동일하다고 읽으면 안 됩니다.'),
        ('Clock_gettime', '__vdso_clock_gettime은 clockid_t clock과 __kernel_timespec *ts를 받아 __cvdso_clock_gettime에 전달하고 int 결과를 반환합니다. 출력 구조체가 old_timespec32인 별도 분기는 이 파일에 없습니다. 공통 gettime.h의 선언 선택 및 실제 빌드 조건과 함께 사용되는 코드이지 이 파일 하나가 모든 ABI의 time32·time64를 자동 선택하지 않습니다.'),
        ('Gettimeofday', '__vdso_gettimeofday는 __kernel_old_timeval *tv와 timezone *tz를 __cvdso_gettimeofday에 그대로 전달합니다. 여기서 사용자 포인터 검증이나 timezone 계산을 따로 하지 않습니다. 공통 구현의 반환값을 그대로 내보내며 libc errno를 설정하는 본문도 없습니다.'),
        ('Clock_getres와 범위', '__vdso_clock_getres는 clockid_t clock_id와 __kernel_timespec *res로 __cvdso_clock_getres를 호출합니다. 별도의 time 함수, clock_gettime64 wrapper, weak alias 선언은 없습니다. 모든 함수·include를 대조했으며 실제 RISC-V ELF export와 사용자 프로그램 실행 검증을 수행한 것은 아닙니다.')
    ],
    questions=[
        ('이 파일의 __vdso_clock_gettime 출력 구조체는?', 'struct __kernel_timespec이다', '항상 struct old_timespec32이다', '시그니처가 __kernel_timespec 포인터를 명시합니다. 다른 compat 파일의 자료형을 여기에 적용하면 안 됩니다.'),
        ('세 wrapper가 직접 시간을 계산하고 errno를 설정하는가?', '아니다. 대응하는 __cvdso 함수에 위임하고 int 결과를 반환한다', '그렇다. 각 함수에 별도의 시간 변환 알고리즘이 있다', '각 본문은 한 번의 함수 호출 결과 반환입니다. 공통 알고리즘과 ABI 진입점의 책임을 구분해야 합니다.')
    ]
), dict(
    path='arch/riscv/include/asm/vdso/vsyscall.h',
    title='RISC-V 커널 vDSO getter: 공통 갱신 코드 연결',
    intro='외부 데이터 포인터와 hook 이름, generic 헤더 포함 순서를 분석합니다.',
    principle='전처리 hook을 먼저 제공하면 공통 구현의 기본 동작 일부만 아키텍처별로 바꿀 수 있습니다.',
    use='주소 제공과 데이터 갱신을 구분하고 기본 hook 선택을 읽습니다.',
    area='외부 포인터 · 전처리 hook · include 순서 · 공통 구현',
    sections=[
        ('전체 가시성과 선언', 'GPL-2.0 include guard 안의 !__ASSEMBLY__에서 linux/timekeeper_internal.h와 vdso/datapage.h를 포함합니다. extern struct vdso_data *vdso_data를 선언하며 여기서 데이터 저장소나 포인터 초기값을 정의하지 않습니다.'),
        ('Getter의 실제 책임', '__riscv_get_k_vdso_data는 static __always_inline 함수로 vdso_data를 반환합니다. 주변 주석은 커널 timekeeping과 데이터 페이지의 동기화를 설명하지만 이 함수 본문은 시간 필드를 갱신하지 않습니다. NULL 검사, 페이지 할당, lock·sequence 증가도 없습니다.'),
        ('Hook 연결과 포함 순서', '__arch_get_k_vdso_data 매크로를 __riscv_get_k_vdso_data에 연결한 뒤 asm-generic/vdso/vsyscall.h를 포함합니다. 주석은 이 순서를 요구합니다. generic 헤더의 #ifndef가 getter의 기본 NULL 구현을 제공하지 않게 하는 전처리 선택입니다. 런타임 함수 테이블 검색이 아닙니다.'),
        ('제공하지 않는 hook', '이 파일은 __arch_update_vsyscall이나 __arch_sync_vdso_data를 재정의하지 않습니다. 확인한 generic 헤더에서 이 둘은 빈 inline 기본 구현으로 제공됩니다. RNG getter나 ARM64의 56비트 mask 갱신도 이 파일에는 없습니다. 아키텍처 헤더 이름이 같다는 이유로 다른 파일의 동작을 복사해서 설명하지 않습니다.'),
        ('범위와 CS 연결', '전체 include·외부 선언·함수·매크로·조건을 설명했습니다. 공통 갱신 알고리즘에 저장소 주소를 알려주는 확장 지점이라는 것이 핵심입니다. 실제 공유 페이지 게시·동시 읽기 검증은 별도 구현 범위입니다.')
    ],
    questions=[
        ('__riscv_get_k_vdso_data가 직접 수행하는 작업은?', 'vdso_data 포인터 반환이다', '현재 시간 필드 전체를 갱신하고 sequence를 증가시킨다', '주석의 전체 목적과 getter 본문의 실제 동작을 구분해야 합니다. 함수에는 return 한 줄만 있습니다.'),
        ('generic 헤더보다 getter hook 매크로를 먼저 정의하는 이유는?', 'generic의 기본 getter 선택을 억제하고 RISC-V getter를 사용하기 위해서다', '함수를 런타임에 먼저 실행하기 위해서다', '선택은 #ifndef를 사용하는 전처리 단계입니다. include 순서와 실행 순서를 혼동하면 안 됩니다.')
    ]
), dict(
    path='arch/riscv/include/asm/vdso/clocksource.h',
    title='RISC-V vDSO 모드: ARCHTIMER 항목의 enum 확장',
    intro='단일 아키텍처 모드 매크로와 공통 enum의 관계를 분석합니다.',
    principle='전처리 토큰 목록으로 공통 자료형을 아키텍처별로 확장할 수 있습니다.',
    use='식별자 제공과 하드웨어 초기화의 차이를 구분합니다.',
    area='전처리 · enum · 아키텍처 모드',
    sections=[
        ('전체 정의', 'GPL-2.0과 __ASM_VDSOCLOCKSOURCE_H guard 아래 VDSO_ARCH_CLOCKMODES를 VDSO_CLOCKMODE_ARCHTIMER 토큰 하나로 정의합니다. include나 독립 enum 본문, 함수, 전역 객체는 없습니다.'),
        ('공통 enum 문맥', '공통 include/vdso/clocksource.h에서 NONE 다음 아키텍처 항목으로 삽입되면 이 ARCHTIMER 값은 1이 됩니다. 이 파일에서 직접 =1을 지정한 것은 아닙니다. ARM64의 ARCHTIMER_NOCOMPAT 같은 두 번째 항목도 여기에는 없습니다.'),
        ('범위와 의미', '모드 이름 제공이 실제 CSR_TIME 접근 허용·타이머 등록·시간 환산 성공을 보장하는 것은 아닙니다. 전체 guard와 매크로를 설명했으며 카운터 구현이나 CPU 기능 탐지까지 이 파일에 있다고 가정하지 않습니다.')
    ],
    questions=[
        ('이 헤더의 VDSO_ARCH_CLOCKMODES 항목 수는?', 'ARCHTIMER 하나이다', 'ARCHTIMER와 ARCHTIMER_NOCOMPAT 두 개이다', '두 항목을 가진 ARM64 헤더와 달리 RISC-V 원본은 하나의 토큰만 제공합니다.'),
        ('이 매크로가 실행 시 타이머를 초기화하는가?', '아니다. 공통 enum에 넣을 식별자를 제공한다', '그렇다. 포함할 때마다 CSR에 초기값을 쓴다', '전처리 정의는 실행 명령이 아닙니다. 하드웨어 초기화는 별도 구현을 찾아야 합니다.')
    ]
)]
