"""Whole-file architecture clocksource adapters and usage bitmap helpers."""
ROWS = [dict(
    path='arch/x86/include/asm/hyperv_timer.h',
    title='X86 Hyper-V raw timer 연결: rdtsc_ordered 매크로',
    intro='공통 Hyper-V 시계 코드가 x86의 TSC를 읽도록 연결하는 작은 헤더 전체를 분석합니다.',
    principle='공통 알고리즘의 하드웨어 의존 동작을 아키텍처 헤더의 인터페이스로 분리할 수 있습니다.',
    use='원시 카운터 읽기와 시간 단위 환산을 구별합니다.',
    area='아키텍처 추상화 · C 매크로 · TSC · 인터페이스 분리',
    sections=[
        ('파일 전체', 'GPL-2.0 표기, _ASM_X86_HYPERV_TIMER_H include guard, asm/msr.h 포함, 매크로 하나로 구성됩니다. 별도 구조체·전역 변수·설정별 stub·함수 본문은 없습니다. rdtsc_ordered 선언과 구현 문맥은 포함된 msr 헤더에 의존합니다.'),
        ('호출 형태의 매크로', '#define hv_get_raw_timer() rdtsc_ordered()는 인수가 없는 함수형 매크로입니다. 이를 호출하는 공통 코드에서는 x86의 ordered TSC 읽기로 치환됩니다. 이 선언으로 hv_get_raw_timer라는 별도 함수 심볼이 생성되는 것은 아닙니다. 단순 매크로 연결 자체가 부팅 때 하드웨어를 등록하는 코드도 아닙니다.'),
        ('카운터와 환산의 경계', '매크로는 raw TSC 값을 읽으며 Hyper-V 페이지의 scale·offset이나 sequence를 검사하지 않습니다. 공통 include/clocksource/hyperv_timer.h가 페이지를 확인하고 raw timer를 읽은 뒤 넓은 곱과 offset으로 참조 시간을 계산합니다. 따라서 여기의 반환값을 그대로 초나 나노초라고 부르지 않습니다.'),
        ('CS 연결과 범위', '공통 코드는 hv_get_raw_timer라는 인터페이스에 의존하고 아키텍처 헤더가 실제 읽기를 선택합니다. 작은 파일도 빌드 시 의존성 연결에 역할이 있습니다. 전체 텍스트를 대조했으며 rdtsc_ordered의 구체 명령 선택이나 모든 x86 CPU의 실행 결과까지 이 파일의 검증으로 간주하지 않습니다.')
    ],
    questions=[
        ('이 파일의 hv_get_raw_timer()는 어떤 값으로 직접 연결되는가?', 'rdtsc_ordered()의 원시 TSC 값이다', '이미 나노초로 환산한 Hyper-V wall clock이다', '매크로에는 scale·offset 계산이 없습니다. raw 카운터를 시간으로 바꾸는 연산은 공통 시계 코드에서 수행합니다.'),
        ('이 매크로 정의만으로 별도 hv_get_raw_timer 함수 심볼이 생성되는가?', '아니다. 호출 텍스트를 rdtsc_ordered()로 치환한다', '그렇다. 모든 함수형 매크로는 독립 ELF 함수가 된다', '전처리 매크로와 컴파일된 함수 정의는 다릅니다. 이 헤더에는 hv_get_raw_timer의 C 함수 본문이 없습니다.')
    ]
), dict(
    path='arch/x86/include/asm/clocksource.h',
    title='X86 vclock 사용 이력: 비트맵과 비원자적 갱신',
    intro='vclocks_used 외부 변수와 두 inline helper를 전체 분석합니다.',
    principle='한 번의 읽기·쓰기를 보존하는 접근 매크로와 여러 연산을 하나로 묶는 원자적 갱신은 다릅니다.',
    use='비트마스크의 사용 이력을 해석하고 경쟁 갱신에서 lost update가 생기는 조건을 설명합니다.',
    area='비트맵 · READ_ONCE · WRITE_ONCE · 경쟁 조건 · lost update · 외부 변수',
    sections=[
        ('전체 인터페이스', 'GPL-2.0 include guard 안에서 asm/vdso/clocksource.h를 포함하고 extern unsigned int vclocks_used를 선언합니다. 저장 공간을 정의하거나 0으로 초기화하는 파일은 아닙니다. 뒤에는 vclock_was_used와 vclocks_set_used 두 static inline helper만 있습니다. 자료형 bool과 접근 매크로는 포함 문맥에 의존합니다.'),
        ('특정 시계의 사용 여부', 'vclock_was_used(int vclock)는 READ_ONCE(vclocks_used) & (1U << vclock)를 bool로 반환합니다. 비트가 있으면 true, 없으면 false이며 비트마스크의 정수 크기를 그대로 외부에 반환하지 않습니다. 예를 들어 bitmap=0b1010이면 인덱스 1과 3은 true, 2는 false입니다. clock 모드 값이 비트의 인덱스 역할을 합니다.'),
        ('사용 이력 기록', 'vclocks_set_used(unsigned int which)는 READ_ONCE로 읽은 값에 (1 << which)를 OR하고 WRITE_ONCE로 기록합니다. 기존 비트를 지우는 대입이 아니라 지정 비트를 추가하는 동작입니다. 이 파일에 이력을 지우는 helper는 없습니다. 질의는 1U, 갱신은 1을 사용하는 원본 표현의 차이도 유지해 읽어야 합니다.'),
        ('입력 범위는 검사하지 않는다', '두 helper 모두 shift 인덱스를 검증하지 않습니다. 음수나 자료형 폭 이상의 이동량을 임의로 넘겨도 안전한 범용 비트셋 API가 아닙니다. 지정된 vclock 모드 인덱스 범위에서 사용해야 하며, 큰 정수 sentinel을 무조건 시계 인덱스로 넣으면 안 됩니다. 코드가 비트를 저장한다는 사실만으로 모든 int 입력을 지원한다고 추정하지 않습니다.'),
        ('원자적 OR가 아닌 이유', 'WRITE_ONCE의 값 인수는 별도 READ_ONCE와 OR로 계산됩니다. CPU A와 B가 모두 0을 읽고 각각 비트 1과 2를 설정하면 A가 2를 쓴 뒤 B가 4를 써 최종값이 6이 아닌 4가 될 수 있습니다. 이 helper 본문에는 atomic_fetch_or·CAS 반복·락이 없습니다. 호출 문맥의 직렬화 등 별도 조건을 확인해야 하며 이 예시만으로 실제 호출부에 버그가 있다고 단정하지 않습니다.'),
        ('사용 여부와 활성 여부', 'was_used라는 인터페이스와 OR 누적은 과거 사용 이력을 질의하는 형태입니다. true가 현재 선택된 clocksource라는 뜻은 아닙니다. 실제 pvclock 주소 setter는 이 질의를 경고 조건에 사용합니다. 이 파일은 현재 clocksource를 선택하거나 하드웨어를 활성화하지 않습니다.'),
        ('CS 연결과 검증 범위', '전체 변수 선언과 두 함수의 연산을 다뤘습니다. 집합의 비트 표현, bool 변환, 단일 접근과 read-modify-write 원자성의 차이가 학습 핵심입니다. 예시 경쟁은 코드 구조에 따른 분석이며 실제 커널 호출부의 동시 실행 조건까지 검증한 결과는 아닙니다.')
    ],
    questions=[
        ('vclocks_used=0b1010에서 vclock_was_used(3)의 반환은?', 'true이다', '정수 8을 그대로 반환한다', 'AND의 중간 결과는 8이지만 함수 반환형은 bool입니다. 0이 아닌 값이 true로 변환됩니다.'),
        ('두 CPU가 vclocks_set_used를 동시에 호출해도 WRITE_ONCE만으로 서로의 비트가 보존되는가?', '아니다. 읽기와 OR와 쓰기가 하나의 원자적 갱신은 아니다', '그렇다. WRITE_ONCE는 앞선 READ_ONCE와 자동으로 트랜잭션을 만든다', '둘이 같은 이전 값을 읽으면 늦은 쓰기가 먼저 설정한 다른 비트를 잃게 할 수 있습니다. 동시 호출의 허용 여부는 호출부의 직렬화 계약을 확인해야 합니다.'),
        ('vclock_was_used가 true이면 해당 시계가 지금 활성 시계인가?', '그렇게 단정할 수 없다. 이 helper는 사용 이력 비트를 조회한다', '그렇다. true를 반환할 때마다 하드웨어 시계를 활성화한다', '질의 함수에는 선택이나 하드웨어 활성화 동작이 없습니다. 이력과 현재 상태를 구분해야 합니다.')
    ]
), dict(
    path='arch/arm64/include/asm/clocksource.h',
    title='ARM64 clocksource 헤더: vDSO 모드 선언의 전달',
    intro='아키텍처 공통 이름의 헤더가 ARM64 vDSO clocksource 정의를 포함하는 구조를 읽습니다.',
    principle='헤더의 역할은 새 함수를 구현하는 것뿐 아니라 필요한 아키텍처 정의로 의존성을 연결하는 것도 포함합니다.',
    use='파일이 짧거나 같은 이름이라고 다른 아키텍처의 helper까지 제공한다고 가정하지 않습니다.',
    area='헤더 의존성 · 전처리 · 아키텍처별 인터페이스',
    sections=[
        ('전체 파일', 'GPL-2.0 표기와 _ASM_CLOCKSOURCE_H include guard 안에 #include <asm/vdso/clocksource.h> 하나가 있습니다. 이 파일 자체에는 함수, 구조체, 전역 변수, clocksource 등록 코드가 없습니다. include guard는 같은 번역 단위에서 반복 포함되는 본문을 막습니다.'),
        ('아키텍처별 차이', 'ARM64의 asm/clocksource.h를 사용하는 코드는 이 include를 통해 아키텍처 vDSO clocksource 정의에 도달합니다. 같은 경로 이름의 x86 헤더에 있는 vclocks_used, vclock_was_used, vclocks_set_used는 이 ARM64 파일에 없습니다. 이름의 유사성만으로 두 헤더의 추가 API가 동일하다고 가정해서는 안 됩니다.'),
        ('범위와 CS 연결', '이 파일 전체의 역할은 선언 의존성 전달입니다. 실제 카운터 읽기나 시간 변환은 포함 관계 밖의 구현을 찾아야 합니다. 이 헤더를 분석했다고 ARM64 시계 드라이버 전체나 포함된 vDSO 헤더까지 새로 완료 집계하지 않습니다.')
    ],
    questions=[
        ('이 ARM64 헤더가 직접 정의하는 시간 조회 함수는?', '없다. vDSO clocksource 헤더를 포함한다', 'vclock_was_used와 vclocks_set_used 두 개이다', '해당 두 helper는 x86 헤더에 있습니다. ARM64 원본은 guard와 include만으로 구성되므로 다른 아키텍처의 구현을 옮겨 읽으면 안 됩니다.'),
        ('이 파일을 읽으면 실제 ARM64 카운터 읽기 명령도 확인한 것인가?', '아니다. 이 파일에는 카운터 읽기 본문이 없다', '그렇다. 모든 clocksource.h가 카운터 명령을 직접 구현한다', '헤더 이름과 실제 정의 범위는 다릅니다. 이 파일은 포함 경로를 제공하고 실제 동작은 관련 구현에서 별도로 확인해야 합니다.')
    ]
)]
