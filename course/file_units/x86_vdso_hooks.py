"""Whole-file x86 vDSO mode and generic override hooks."""
ROWS = [dict(
    path='arch/x86/include/asm/vdso/clocksource.h', title='x86 vDSO 모드 목록: TSC·PV clock·Hyper-V clock',
    intro='아키텍처 열거자 목록 매크로와 지원 표식을 전체 범위로 읽습니다.',
    principle='플랫폼별 열거자 목록을 공통 enum에 삽입하면 공통 인터페이스와 아키텍처별 종류를 분리할 수 있습니다.',
    use='x86 clock mode의 정의 위치와 실제 실행 가능성의 차이를 이해합니다.',
    area='전처리 매크로 · 열거형 확장 · 아키텍처 추상화 · 기능 표식',
    sections=[
        ('파일 전체', 'GPL-2.0과 include guard 안에 VDSO_ARCH_CLOCKMODES와 HAVE_VDSO_CLOCKMODE_HVCLOCK 두 매크로만 있습니다. include, 함수, enum 정의 자체는 없습니다. 하드웨어 clock을 읽거나 활성화하는 코드는 아닙니다.'),
        ('열거자 목록 삽입', 'VDSO_ARCH_CLOCKMODES는 TSC, PVCLOCK, HVCLOCK 세 열거자 이름을 쉼표로 연결합니다. 공통 include/vdso/clocksource.h의 enum 안에서 사용되며 일반적인 해당 확장에서는 NONE=0 뒤에 1,2,3으로 들어가고 MAX는 4가 됩니다. 이 헤더 단독으로 세 이름을 정수 매크로로 정의하는 것은 아닙니다.'),
        ('지원 표식', 'HAVE_VDSO_CLOCKMODE_HVCLOCK은 대체 토큰 없이 정의됩니다. 따라서 #ifdef로 이름의 정의 여부를 확인하는 표식이지 숫자 값 1이 대입된 변수가 아닙니다. 표식이 있다고 현재 VM이 Hyper-V이거나 그 clock이 선택됐다는 뜻은 아닙니다.'),
        ('정의와 실행의 경계', 'TSC·PV clock·Hyper-V clock 모드의 이름을 제공하지만 사용 가능한 CPU 기능, clocksource 선택, 읽기 실패와 fallback은 다른 구현에서 판단합니다. 전체 파일 학습을 x86 시간 조회 구현 전체 검증으로 세지 않습니다.')
    ],
    questions=[
        ('이 헤더만 포함하면 TSC 모드가 정수 #define으로 만들어지는가?', '아니다. 공통 enum에 삽입할 열거자 목록을 제공한다', '그렇다. 각 이름에 독립적으로 #define 1이 붙는다', 'VDSO_ARCH_CLOCKMODES의 확장 위치가 enum이므로 열거자가 됩니다. 전처리 목록과 최종 C 선언을 구분합니다.'),
        ('HAVE_VDSO_CLOCKMODE_HVCLOCK 정의가 현재 Hyper-V clock 사용을 증명하는가?', '아니다. 모드 정의의 존재를 나타내는 표식이다', '그렇다. 모든 x86 시스템이 즉시 Hyper-V clock을 사용한다', '빌드 시 정의와 런타임 선택은 별개입니다. 이 파일에는 clock 선택 코드가 없습니다.')
    ]
), dict(
    path='arch/x86/include/asm/vdso/vsyscall.h', title='x86 vDSO 커널 주소 hook: 시간 배열과 RNG 객체',
    intro='두 주소 getter, 공통 이름 별칭과 generic fallback 포함 순서를 분석합니다.',
    principle='아키텍처가 구현한 hook을 먼저 매크로로 알리고 공통 헤더가 나머지 기본 동작을 보충하게 합니다.',
    use='공통 update 코드가 x86 공유 데이터를 얻는 경로와 override 규약을 이해합니다.',
    area='헤더 계층 · 함수 별칭 · 전처리 override · 포인터 · 공유 데이터',
    sections=[
        ('전체 구성', 'GPL-2.0과 guard 안에서 __ASSEMBLY__가 아닐 때 timekeeper_internal, datapage, asm/vgtod, asm/vvar를 포함합니다. 두 static __always_inline getter와 매크로 별칭 뒤 asm-generic/vdso/vsyscall.h를 포함합니다. assembly 경로에는 이 include와 함수들이 노출되지 않습니다.'),
        ('시간 데이터 주소', '__x86_get_k_vdso_data는 struct vdso_data *를 반환하며 본문은 return _vdso_data입니다. 배열 이름이 첫 원소 포인터로 쓰입니다. __arch_get_k_vdso_data 매크로를 이 함수 이름으로 연결하여 공통 시간 갱신 구현이 아키텍처별 함수 이름을 직접 알 필요 없게 합니다.'),
        ('RNG 데이터 주소', '__x86_get_k_vdso_rng_data는 &_vdso_rng_data를 반환하고 __arch_get_k_vdso_rng_data 별칭을 정의합니다. 이 심볼은 단일 RNG 메타데이터 객체여서 명시적으로 주소를 취합니다. 난수를 생성하거나 reseed를 실행하는 함수가 아니라 커널이 사용할 데이터 주소를 제공하는 함수입니다.'),
        ('정의 뒤 generic include', '주석은 generic 헤더를 위 정의들 뒤에 포함해야 한다고 명시합니다. generic 헤더는 __arch_get_k_vdso_data 매크로가 없을 때 NULL getter를 정의하므로 x86의 별칭을 먼저 보여야 기본 정의를 피할 수 있습니다. C 함수 이름이 존재하는 것만으로 #ifndef가 이를 자동 탐지하는 것은 아닙니다.'),
        ('보충 hook과 범위', '이 x86 파일은 __arch_update_vsyscall이나 __arch_sync_vdso_data를 직접 정의하지 않습니다. generic 헤더는 앞선 문맥에서 해당 매크로가 없다면 빈 기본 함수를 제공합니다. RNG getter의 generic fallback이 같은 헤더에 반드시 있다고 추정하지 않습니다. 전체 주소 연결을 읽었지만 사용자 vDSO의 하드웨어 읽기 코드 전체를 검증한 것은 아닙니다.')
    ],
    questions=[
        ('두 getter가 시간과 RNG를 직접 갱신하는가?', '아니다. 기존 데이터의 주소를 반환한다', '그렇다. 호출마다 새 시각과 난수를 생성한다', '본문은 return만 있습니다. 주소 제공과 데이터 계산·게시를 구분합니다.'),
        ('generic 헤더를 아키텍처 별칭 정의 뒤에 포함하는 이유는?', '매크로 존재 검사로 기본 getter 정의를 건너뛰게 하기 위해서이다', 'include 순서는 언제나 전처리 결과에 영향을 주지 않기 때문이다', 'generic의 #ifndef는 그 시점에 보이는 매크로를 검사합니다. 정의 순서는 override 규약의 일부입니다.'),
        ('시간 getter와 RNG getter의 반환식 차이는?', '배열 _vdso_data와 단일 객체의 주소 &_vdso_rng_data이다', '둘 다 새 메모리를 할당해 반환한다', '배열 이름의 포인터 변환과 단일 객체의 주소 연산을 사용합니다. 동적 할당은 없습니다.')
    ]
), dict(
    path='include/asm-generic/vdso/vsyscall.h', title='vDSO 기본 hook: NULL getter와 빈 update·sync',
    intro='세 개의 독립적인 매크로 조건과 기본 inline 동작을 전체 범위로 읽습니다.',
    principle='기본 hook이 존재한다는 사실과 모든 사용 문맥에서 유효한 기능을 제공한다는 것은 다릅니다.',
    use='플랫폼 override가 필요한 함수와 선택적인 빈 hook을 구분합니다.',
    area='조건부 컴파일 · fallback · NULL 계약 · 인터페이스 · 선언 문맥',
    sections=[
        ('전체 파일과 문맥', 'GPL-2.0과 guard, __ASSEMBLY__ 제외 조건 안에 세 #ifndef와 static inline 기본 함수가 있습니다. 자체 include는 없으므로 타입과 NULL, __always_inline을 포함 문맥이 제공해야 합니다. 세 함수의 대체 여부를 각각 독립적으로 검사합니다.'),
        ('기본 데이터 getter', '__arch_get_k_vdso_data 매크로가 없으면 같은 이름의 함수가 NULL을 반환합니다. 공유 데이터 저장소를 자동 할당하는 fallback이 아닙니다. 반환 포인터를 곧바로 역참조하는 공통 구현과 연결하려면 실제 아키텍처 데이터 제공 및 구성 조건이 맞아야 합니다.'),
        ('빈 추가 갱신', '__arch_update_vsyscall 매크로가 없으면 vdso_data *와 timekeeper *를 받는 빈 void inline을 제공합니다. 추가 플랫폼 작업이 없는 경우의 기본 동작입니다. 포인터 인자를 받는다고 반드시 필드를 복사하거나 NULL 검사를 하는 것은 아닙니다.'),
        ('빈 데이터 동기화', '__arch_sync_vdso_data 매크로가 없으면 vdso_data *를 받는 빈 void inline을 제공합니다. 여기에는 CPU memory barrier나 cache flush가 없습니다. 필요한 플랫폼별 동기화는 override와 상위 게시 규약에서 확인해야 합니다.'),
        ('매크로 검사와 포함 순서', '#ifndef는 C 함수 정의를 검색하지 않습니다. 아키텍처가 구현을 제공하면 generic 포함 전에 대응 매크로도 준비하여 기본 함수를 생략시키는 규약입니다. 이 파일은 RNG 데이터 getter나 vdso_update_begin/end를 정의하지 않으므로 비슷한 이름의 다른 헤더 범위와 혼동하지 않습니다.')
    ],
    questions=[
        ('기본 __arch_get_k_vdso_data는 무엇을 반환하는가?', 'NULL이다', '자동 할당된 데이터 페이지 주소이다', '실제 본문은 return NULL입니다. fallback 존재가 데이터 준비 완료를 뜻하지 않습니다.'),
        ('기본 __arch_sync_vdso_data에 메모리 장벽이 있는가?', '없다. 빈 함수이다', '있다. sync라는 이름이 장벽 명령을 자동 생성한다', '함수 이름과 실제 구현을 구분해야 합니다. 플랫폼 요구는 override를 확인합니다.'),
        ('아키텍처 getter만 override하면 update와 sync의 기본 정의도 모두 사라지는가?', '아니다. 각각 별도 #ifndef로 선택된다', '그렇다. 하나의 override가 전체 기본 구현을 비활성화한다', '세 독립 조건문이 있으므로 필요한 hook만 대체하고 다른 기본값은 유지할 수 있습니다.')
    ]
)]
