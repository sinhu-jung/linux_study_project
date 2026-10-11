"""Whole-file vDSO time declarations and compile-time ABI selection."""
ROWS = [dict(
    path='include/vdso/gettime.h',
    title='vDSO 시간 함수 선언: 불완전형과 빌드별 시간 ABI',
    intro='시간 조회 함수 원형 전체와 CONFIG_64BIT·BUILD_VDSO32_64의 선택 조건을 읽습니다.',
    principle='함수 선언은 호출 규약의 자료형 계약이며 구현이나 내보낸 심볼의 존재 자체를 보장하지 않습니다.',
    use='호환 vDSO를 빌드할 때 같은 함수 이름의 포인터 자료형이 왜 달라지는지 설명합니다.',
    area='C 선언 · 불완전형 · 전처리 논리 · ABI · time32/time64',
    sections=[
        ('전체 구성과 중복 포함 방지', 'GPL-2.0 표기 뒤 _VDSO_GETTIME_H include guard가 파일 전체를 감쌉니다. linux/types.h를 포함하고 구조체 전방 선언, 조건부 clock 함수 원형, 공통 원형을 배치합니다. 함수 본문·전역 저장 공간·런타임 분기·별도 __ASSEMBLY__ 조건은 없습니다.'),
        ('포인터와 불완전형', 'struct __kernel_timespec과 struct timezone을 전방 선언합니다. 함수 원형에서 구조체 포인터를 선언하는 데는 전체 멤버 배치가 필요하지 않습니다. 이 헤더만 읽고 멤버를 접근하거나 해당 구조체의 sizeof를 구할 수 있다고 추정해서는 안 됩니다. __kernel_old_timeval 태그는 포함된 자료형 헤더 문맥을 함께 확인해야 합니다.'),
        ('Time32 분기의 정확한 논리', '!defined(CONFIG_64BIT) || defined(BUILD_VDSO32_64)이 참이면 old_timespec32를 전방 선언하고 __vdso_clock_getres와 __vdso_clock_gettime의 출력 포인터를 old_timespec32 *로 선언합니다. CONFIG_64BIT 미정의이면 두 번째 매크로와 관계없이 이 분기입니다. CONFIG_64BIT가 정의되어도 BUILD_VDSO32_64가 정의되면 이 분기입니다. defined는 매크로 존재를 검사하므로 정수 값 비교와 다릅니다.'),
        ('Time64 구조체를 쓰는 반대 분기', 'else에 도달하려면 CONFIG_64BIT가 정의되고 BUILD_VDSO32_64가 정의되지 않아야 합니다. 두 함수의 출력 포인터는 __kernel_timespec *입니다. 양쪽 모두 첫 인수는 clockid_t clock, 반환형은 int로 같습니다. 같은 이름이라도 서로 다른 빌드의 선언을 혼합하면 구조체 배치에 대한 ABI 계약이 맞지 않을 수 있습니다.'),
        ('조건부 밖에 있는 세 함수', '__vdso_time은 __kernel_old_time_t *t를 받아 __kernel_old_time_t를 반환합니다. __vdso_gettimeofday는 __kernel_old_timeval *tv와 timezone *tz를 받고 int를 반환합니다. __vdso_clock_gettime64는 clockid_t와 __kernel_timespec *를 받고 int를 반환합니다. 이 세 선언은 앞 #if의 양쪽에 공통이며 old_time_t가 언제나 64비트라는 뜻은 아닙니다.'),
        ('선언과 정의·공개 심볼의 차이', '__vdso_clock_gettime64의 원형은 항상 보이지만 특정 아키텍처 vDSO가 그 함수를 항상 정의·내보낸다는 결론은 나오지 않습니다. 실제 진입점 구현과 링크용 심볼 목록을 추가로 확인해야 합니다. 이 파일에는 __vdso_clock_getres64 원형이나 clock_gettime 같은 일반 이름의 weak alias 선언이 없습니다.'),
        ('CS 연결과 범위', '전방 선언을 통한 의존성 감소, 드모르간 법칙에 따른 조건의 부정, 빌드 구성과 ABI 계약, 선언과 정의의 분리를 학습합니다. 헤더 전체 원형과 분기를 다뤘으며 반환 오류·NULL 포인터 처리·시계 선택·syscall fallback은 구현을 읽어야 알 수 있습니다. 이 자료는 여러 ABI의 실행 결과를 검증한 보고서가 아닙니다.')
    ],
    questions=[
        ('CONFIG_64BIT와 BUILD_VDSO32_64가 모두 정의되면 __vdso_clock_gettime의 출력 자료형은?', 'struct old_timespec32 *이다', 'struct __kernel_timespec *이다', '조건은 !defined(CONFIG_64BIT) OR defined(BUILD_VDSO32_64)입니다. 첫 항이 거짓이어도 두 번째 항이 참이므로 time32 분기가 선택됩니다.'),
        ('__kernel_timespec의 멤버 선언 없이 이 헤더가 그 포인터를 함수 원형에 쓸 수 있는 이유는?', '불완전 구조체형도 포인터 자료형 선언에 사용할 수 있기 때문이다', '모든 구조체가 같은 크기여서 컴파일러가 배치를 자동 추측하기 때문이다', '포인터를 받는 원형을 선언할 때 구조체 멤버 배치는 필요하지 않습니다. 멤버 접근이나 sizeof에는 완전한 정의가 필요합니다.'),
        ('__vdso_clock_gettime64 원형이 조건부 밖에 있으면 모든 vDSO에 그 심볼이 존재하는가?', '아니다. 선언과 실제 정의·내보내기는 별도로 확인해야 한다', '그렇다. 함수 원형만으로 실행 가능한 함수가 생성된다', 'C 함수 선언은 자료형 계약입니다. 함수 본문을 생성하지 않으며 아키텍처 구현과 링크 설정이 실제 심볼 존재를 결정합니다.')
    ]
)]
