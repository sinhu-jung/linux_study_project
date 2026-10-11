"""Whole-file x86 vDSO time entry points and ABI aliases."""
ROWS = [dict(
    path='arch/x86/entry/vdso/vclock_gettime.c',
    title='X86 vDSO 시간 진입점: weak alias와 32·64비트 ABI',
    intro='gettimeofday/time과 설정별 clock_gettime/getres wrapper 전체를 분석합니다.',
    principle='공개 함수 이름이 같아도 빌드 ABI에 따라 출력 구조체와 위임하는 내부 함수가 달라집니다.',
    use='x86-64·x32·i386 시간 조회의 공통 부분과 별도 64비트 시간 진입점을 구분합니다.',
    area='ABI · 심볼 별칭 · weak linkage · 전처리 · wrapper · time32/time64',
    sections=[
        ('파일 전체와 직접 소스 포함', 'GPL-2.0-only와 저작권·compat 이력 뒤 time/kernel/types/gettime 헤더를 포함합니다. 이어 상대 경로로 lib/vdso/gettimeofday.c를 직접 include합니다. 따라서 공통 C 구현을 이 번역 단위로 가져오며 단순히 함수 원형만 참조하는 include가 아닙니다. 이 학습은 진입점 파일 전체 범위이며 포함된 공통 파일 전체를 별도 완료로 집계하지 않습니다.'),
        ('Gettimeofday 진입점', '__vdso_gettimeofday는 __kernel_old_timeval *tv와 timezone *tz를 받아 __cvdso_gettimeofday의 int 결과를 그대로 반환합니다. 사용자 포인터를 여기서 새로 복사하거나 유효성을 직접 검사하지 않습니다. 빠른 경로·fallback과 NULL 처리의 실제 정책은 공통 구현에서 확인해야 합니다.'),
        ('Time 진입점', '__vdso_time은 __kernel_old_time_t *t를 받아 __cvdso_time의 같은 자료형 결과를 반환합니다. 반환형이 time64_t로 명시된 함수가 아닙니다. old_time_t의 구체 폭과 범위는 빌드 ABI를 함께 봐야 하며 함수 이름만으로 항상 64비트 시간을 보장한다고 가정하지 않습니다.'),
        ('Weak alias의 역할', 'gettimeofday와 time은 각각 __vdso_gettimeofday와 __vdso_time의 weak alias로 선언됩니다. 다른 이름의 독립 함수 본문을 하나씩 더 호출하는 wrapper가 아닙니다. weak linkage와 alias는 심볼 연결 속성이고 호출의 시간 정확도나 메모리 접근 안전성을 의미하지 않습니다.'),
        ('64비트와 x32 선택 조건', 'CONFIG_X86_64가 정의되고 BUILD_VDSO32_64가 정의되지 않았을 때의 분기는 주석상 64비트와 x32가 함께 사용합니다. __vdso_clock_gettime은 __kernel_timespec 포인터로 __cvdso_clock_gettime을, __vdso_clock_getres는 같은 구조체로 __cvdso_clock_getres를 호출합니다. 두 일반 이름도 각각 weak alias입니다. x32를 단순히 i386 시간 구조체와 같다고 읽지 않습니다.'),
        ('I386의 구형 시간 경로', 'else 분기는 i386용입니다. __vdso_clock_gettime은 old_timespec32 *를 받고 __cvdso_clock_gettime32로 위임합니다. __vdso_clock_getres도 old_timespec32 *와 __cvdso_clock_getres_time32를 사용합니다. 공개 이름이 같아도 앞 분기와 출력 ABI가 다릅니다.'),
        ('I386의 추가 time64 진입점', '같은 else 분기는 __vdso_clock_gettime64를 별도로 정의하여 __kernel_timespec *를 __cvdso_clock_gettime에 전달합니다. clock_gettime64는 이 함수의 weak alias입니다. 이 파일에는 별도의 __vdso_clock_getres64나 clock_getres64 wrapper는 없습니다. 대칭적인 이름이 있을 것이라고 추정하지 않습니다.'),
        ('빌드 조건과 런타임의 차이', '이 #if는 빌드 시 함수 시그니처와 심볼 구성을 선택합니다. 한 함수가 매 호출마다 프로세스의 포인터 폭을 검사해 두 구조체 중 하나로 자동 출력하는 코드가 아닙니다. CONFIG_X86_64만 보고 분기를 결정하면 BUILD_VDSO32_64 예외를 놓칩니다.'),
        ('CS와 검증 범위', '모든 함수 본문과 alias, 전처리 분기를 설명했습니다. 공개 심볼과 공통 구현 분리, 동일 이름의 ABI 차이, 소스 포함과 헤더 선언의 차이를 학습합니다. 실제 vDSO ELF 심볼표나 각 ABI 실행을 검증한 결과는 아니며 이 파일에 없는 syscall fallback 구현을 확인한 것으로 표시하지 않습니다.')
    ],
    questions=[
        ('CONFIG_X86_64만 정의되어 있으면 언제나 첫 clock 분기인가?', '아니다. BUILD_VDSO32_64가 정의되면 else 분기이다', '그렇다. 두 번째 조건은 함수 선택에 영향을 주지 않는다', '조건은 두 항의 AND입니다. 64비트 커널을 위한 32비트 vDSO 빌드 문맥도 구분해야 합니다.'),
        ('이 파일에서 x32는 어느 clock_gettime 구조체 경로를 공유하는가?', '__kernel_timespec을 사용하는 64비트 쪽 경로이다', '무조건 old_timespec32만 사용하는 i386 경로이다', '주석은 첫 분기를 64-bit and x32라고 명시합니다. 포인터 폭과 시간 ABI 구조체를 동일시하면 안 됩니다.'),
        ('i386에서 clock_gettime64는 어느 공통 함수를 호출하는가?', '__cvdso_clock_gettime이다', '__cvdso_clock_gettime32이다', '추가 64비트 시간 진입점은 __kernel_timespec을 사용하고 공통 time64 구현에 위임합니다.'),
        ('weak alias인 gettimeofday가 별도의 중간 함수 본문을 가지는가?', '아니다. __vdso_gettimeofday의 다른 심볼 이름이다', '그렇다. 항상 추가 syscall을 실행하는 별도 wrapper이다', 'alias 속성이 같은 구현에 다른 이름을 연결합니다. 실제 함수 본문은 __vdso_gettimeofday에 있습니다.')
    ]
)]
