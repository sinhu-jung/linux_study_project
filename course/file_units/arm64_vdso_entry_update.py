"""Whole-file ARM64 time entry points and kernel vDSO update hooks."""
ROWS = [dict(
    path='arch/arm64/kernel/vdso/vgettimeofday.c',
    title='ARM64 공개 시간 함수: __kernel 이름과 공통 구현 위임',
    intro='세 함수의 원형과 본문 전체를 연결하여 공개 진입점의 책임을 구분합니다.',
    principle='공개 함수의 이름과 실제 시간 알고리즘의 구현 위치는 다를 수 있습니다.',
    use='wrapper의 반환값 전달과 빌드 단계의 공통 구현 포함을 읽습니다.',
    area='함수 원형 · wrapper · 빌드 의존성 · ABI',
    sections=[
        ('전체 파일과 포함 문맥', 'GPL-2.0과 ARM64 userspace 구현이라는 주석 뒤 세 함수 원형, 이어 세 본문이 있습니다. 소스 자체에 #include가 없습니다. 관련 Makefile은 c-gettimeofday-y가 비어 있지 않으면 vgettimeofday.o의 CFLAGS에 -include를 추가합니다. 따라서 파일 단독 텍스트만 보고 필요한 자료형과 __cvdso 함수 정의가 존재하지 않는다고 결론내리지 않고 실제 빌드 문맥을 확인해야 합니다.'),
        ('Clock_gettime', '__kernel_clock_gettime은 clockid_t clock과 __kernel_timespec *ts를 받아 __cvdso_clock_gettime(clock, ts)의 int 결과를 그대로 반환합니다. 여기서 clock ID를 따로 분류하거나 시간 구조체를 복사하지 않습니다. 실제 공유 시간 계산과 fallback 선택은 호출된 구현에 있습니다.'),
        ('Gettimeofday', '__kernel_gettimeofday는 __kernel_old_timeval *tv와 timezone *tz를 받고 __cvdso_gettimeofday(tv, tz)를 반환합니다. __kernel이라는 이름이 붙어도 이 파일의 주석과 위치는 사용자 공간 vDSO 진입점입니다. 모든 호출이 곧바로 syscall을 실행한다는 뜻은 아닙니다.'),
        ('Clock_getres와 없는 심볼', '__kernel_clock_getres는 clockid_t clock_id와 __kernel_timespec *res로 __cvdso_clock_getres를 호출합니다. 이 파일에는 __kernel_time, __kernel_clock_gettime64, 일반 이름의 weak alias 정의가 없습니다. 다른 아키텍처의 진입점 목록과 자동으로 같다고 가정하면 안 됩니다.'),
        ('CS 연결과 범위', '세 함수의 선언과 정의가 일치하고 모두 인수와 int 결과를 직접 전달합니다. 인터페이스와 공통 알고리즘 분리, 번역 단위 구성, 심볼 이름과 실행 위치의 구별이 학습 핵심입니다. 전체 파일 원본을 대조했으며 실제 ELF export 목록이나 ARM64 바이너리 실행까지 검증한 것은 아닙니다.')
    ],
    questions=[
        ('__kernel_clock_gettime이 이 파일에서 직접 구현하는 작업은?', '__cvdso_clock_gettime으로 인수를 전달하고 결과를 반환한다', '매 호출마다 svc #0을 직접 실행한다', '본문은 한 번의 함수 위임입니다. 공통 구현에서 빠른 경로와 fallback을 선택할 수 있으므로 이름만 보고 직접 syscall이라고 판단하면 안 됩니다.'),
        ('파일에 #include가 없으면 필요한 구현도 빌드에서 포함될 수 없는가?', '아니다. 빌드 플래그의 -include도 번역 단위에 내용을 제공할 수 있다', '그렇다. C 컴파일에는 소스에 적힌 #include만 존재한다', '관련 Makefile은 c-gettimeofday-y가 있을 때 -include를 추가합니다. 소스 본문과 실제 컴파일 옵션을 함께 읽어야 의존성을 파악할 수 있습니다.')
    ]
), dict(
    path='arch/arm64/include/asm/vdso/vsyscall.h',
    title='ARM64 커널 vDSO 데이터: 페이지 인덱스·RNG 오프셋·56비트 마스크',
    intro='공유 데이터 주소와 갱신 hook, asm-generic fallback 선택을 전체 분석합니다.',
    principle='고정 오프셋과 비트마스크는 데이터 배치 계약이며, 아키텍처 hook은 공통 갱신 알고리즘에 필요한 차이만 제공합니다.',
    use='시간 데이터와 RNG 데이터 주소를 구별하고 두 clocksource 슬롯의 마스크 갱신을 설명합니다.',
    area='메모리 배치 · 포인터 산술 · 비트마스크 · enum · 아키텍처 hook · 조건부 컴파일',
    sections=[
        ('가시성과 전체 구성', 'GPL-2.0 include guard 아래 __VDSO_RND_DATA_OFFSET을 480으로 정의한 뒤 !__ASSEMBLY__ 구역을 시작합니다. 따라서 이 상수는 assembly 포함 문맥에도 보이지만 C enum·함수는 제외됩니다. C 구역은 linux/timekeeper_internal.h와 vdso/datapage.h에 의존합니다.'),
        ('Vvar 페이지 enum', 'vvar_pages는 VVAR_DATA_PAGE_OFFSET=0, VVAR_TIMENS_PAGE_OFFSET=1, VVAR_NR_PAGES=2 순서입니다. 이름과 주석 문맥의 페이지 오프셋이지 0바이트와 1바이트 간격의 구조체 멤버가 아닙니다. enum 선언 자체가 페이지를 할당하거나 사용자 공간에 매핑하지는 않습니다.'),
        ('정밀도 마스크', 'VDSO_PRECISION_MASK는 ~(0xFF00ULL<<48)입니다. 괄호 안 값은 상위 8비트가 1인 0xFF00000000000000이고 이를 반전하면 0x00FFFFFFFFFFFFFF로 하위 56비트가 남습니다. 0xFF00이라는 원래 토큰만 보고 중간 8비트를 지운다고 해석하지 말고 shift를 먼저 적용해야 합니다.'),
        ('시간 데이터 포인터', 'extern struct vdso_data *vdso_data는 포인터의 외부 선언입니다. __arm64_get_k_vdso_data는 그 포인터를 반환하고 __arch_get_k_vdso_data 매크로가 이 함수 이름에 연결됩니다. 이 헤더에서 실제 저장 공간을 할당하거나 포인터가 유효한지 검사하지 않습니다.'),
        ('RNG 데이터의 바이트 오프셋', '__arm64_get_k_vdso_rnd_data는 (void *)vdso_data + __VDSO_RND_DATA_OFFSET을 반환하며 반환형은 struct vdso_rng_data *입니다. Linux가 사용하는 GNU C의 void 포인터 산술 문맥에서 480바이트를 더하는 형태입니다. vdso_data 원소 480개를 건너뛰는 연산이 아닙니다. __arch_get_k_vdso_rng_data 매크로는 이름에 rnd가 들어간 이 함수로 연결됩니다.'),
        ('갱신 hook의 정확한 쓰기 범위', '__arm64_update_vsyscall(vdata, tk)는 vdata[CS_HRES_COARSE].mask와 vdata[CS_RAW].mask를 모두 VDSO_PRECISION_MASK로 설정합니다. tk 인수는 본문에서 사용하지 않습니다. 초·나노초·seq·mult·shift를 이 함수에서 갱신한다고 확대해서 설명하지 않습니다. __arch_update_vsyscall이 이 함수 이름으로 정의됩니다.'),
        ('Generic 헤더의 포함 순서', '위 hook 매크로를 정의한 다음 asm-generic/vdso/vsyscall.h를 포함해야 한다는 주석이 있습니다. generic 헤더의 #ifndef 검사가 아키텍처 getter와 update를 보존하도록 하기 위한 순서입니다. 이 ARM64 파일에는 __arch_sync_vdso_data 재정의가 없으므로 확인한 generic 헤더의 빈 sync 함수가 제공됩니다. RNG getter까지 generic 쪽에 동일한 fallback이 있다고 추정하지 않습니다.'),
        ('CS 연결과 검증 범위', '모든 상수·enum·외부 선언·세 helper·hook 매크로·포함 순서를 다뤘습니다. 데이터 주소 산술, 정밀도 마스크, 공통 알고리즘의 확장 지점이 핵심입니다. 이 hook에는 자체 잠금이나 seq begin/end가 없으므로 동기화 책임은 호출 문맥과 함께 확인해야 합니다. 실제 ARM64 메모리 매핑과 동시 갱신 실행 시험을 수행한 것은 아닙니다.')
    ],
    questions=[
        ('VDSO_PRECISION_MASK가 남기는 유효 비트 범위는?', '하위 56비트이다', '상위 8비트이다', '0xFF00ULL<<48은 상위 8비트가 1인 값입니다. NOT 연산으로 그 8비트를 지우고 나머지 하위 56비트를 남깁니다.'),
        ('RNG getter에서 vdso_data 기준으로 더하는 거리는?', '480바이트이다', 'vdso_data 구조체 480개의 크기이다', '먼저 void *로 바꾸고 오프셋을 더합니다. GNU C의 바이트 단위 void 포인터 산술이며 구조체 포인터의 원소 단위 이동과 다릅니다.'),
        ('__arm64_update_vsyscall이 직접 갱신하는 필드는?', 'HRES_COARSE와 RAW 슬롯의 mask이다', '모든 슬롯의 seq와 현재 초·나노초 전체이다', '본문에는 mask 대입 두 개만 있고 tk도 사용하지 않습니다. 공통 시간 갱신 전체와 아키텍처 hook의 책임을 구분해야 합니다.'),
        ('asm-generic 헤더를 hook 매크로 정의 뒤에 포함하는 이유는?', 'generic의 조건부 기본 구현보다 ARM64 hook을 먼저 알리기 위해서다', 'runtime에 generic 코드가 ARM64 함수 주소를 검색하도록 하기 위해서다', '선택은 전처리 단계의 #ifndef로 이뤄집니다. 동적 함수 검색이나 실행 순서 문제가 아니라 선언을 구성하는 포함 순서 문제입니다.')
    ]
)]
