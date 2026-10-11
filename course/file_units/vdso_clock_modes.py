"""Complete vDSO clock-mode and namespace-offset type headers."""
ROWS = [dict(
    path='include/vdso/clocksource.h', title='vDSO clock mode: 아키텍처 확장과 namespace sentinel',
    intro='enum의 기본값·조건부 확장·상한·특수값을 전체 소스로 읽습니다.',
    principle='일반 모드 집합의 끝을 나타내는 값과 별도 처리 경로를 지시하는 sentinel은 같은 종류의 인덱스가 아닙니다.',
    use='공유 vDSO 데이터의 clock_mode를 실제 하드웨어 선택 또는 namespace 처리로 해석하는 기준을 이해합니다.',
    area='열거형 · 조건부 컴파일 · 플랫폼 확장 · sentinel · 인덱스 범위',
    sections=[
        ('전체 파일과 의존성', 'GPL-2.0과 guard, vdso/limits.h include, 조건부 아키텍처 include와 enum vdso_clock_mode가 전부입니다. 하드웨어 counter를 읽는 함수나 mode 유효성을 검사하는 실행 코드는 없습니다. 이 파일에는 __ASSEMBLY__로 C enum을 감싸는 별도 분기도 없습니다.'),
        ('기본값과 아키텍처 확장', 'VDSO_CLOCKMODE_NONE은 첫 열거자이므로 0입니다. CONFIG_GENERIC_GETTIMEOFDAY가 정의되면 asm/vdso/clocksource.h를 포함하고 VDSO_ARCH_CLOCKMODES를 enum 안에 삽입합니다. 구체적인 하드웨어 모드 이름과 값은 아키텍처 매크로의 확장에 달려 있으므로 모든 플랫폼에서 같은 목록이라고 가정하지 않습니다.'),
        ('일반 모드 끝과 비활성 구성', 'VDSO_CLOCKMODE_MAX는 아키텍처 모드가 있으면 그 뒤에 옵니다. GENERIC_GETTIMEOFDAY가 없으면 NONE 바로 다음이어서 값은 1입니다. 이 enum의 MAX를 유효한 하드웨어 시계를 뜻하는 항목으로 자동 해석하지 않습니다. 모드 개수나 인덱스 검사는 실제 사용 코드를 확인해야 합니다.'),
        ('Namespace 특수값', 'VDSO_CLOCKMODE_TIMENS는 INT_MAX로 명시적으로 지정됩니다. 주석은 time namespace VDSO를 나타내는 표시라고 설명합니다. 일반 하드웨어 모드 목록 뒤의 연속 배열 슬롯을 할당하려는 값이 아니므로 이 값까지 배열을 확장하거나 일반 MAX 범위 검사만으로 의미를 모두 설명하면 안 됩니다. 관련 datapage 계약에서는 seq=1과 함께 namespace 처리 경로를 표시합니다.'),
        ('검증 범위', '전체 include·조건·열거자를 설명했습니다. 앞서 읽은 limits 헤더의 INT_MAX를 재사용하지만 그 파일을 새로 작성한 것으로 중복 집계하지 않습니다. 각 아키텍처 모드 정의나 사용자 reader의 모든 분기까지 검증한 자료는 아닙니다.')
    ],
    questions=[
        ('GENERIC_GETTIMEOFDAY가 없을 때 NONE과 MAX의 값은?', '각각 0과 1이다', '둘 다 INT_MAX이다', '조건부 아키텍처 열거자들이 빠지면 첫 값 0 다음의 자동 값이 1입니다. TIMENS만 INT_MAX로 명시합니다.'),
        ('VDSO_ARCH_CLOCKMODES의 모든 모드 이름은 이 공통 파일에 직접 나열되어 있는가?', '아니다. 조건부 아키텍처 헤더의 매크로가 제공한다', '그렇다. 모든 아키텍처에서 같은 하드웨어 이름을 고정한다', '전처리 확장으로 플랫폼별 모드 집합을 enum에 삽입합니다. 공통 enum 틀과 구체 구현을 구분합니다.'),
        ('TIMENS=INT_MAX를 일반 clock 배열의 마지막 슬롯 번호로 보아도 되는가?', '아니다. namespace 경로를 나타내는 특수값이다', '그렇다. INT_MAX개 clock을 지원한다는 뜻이다', '큰 명시값은 일반 모드 집합과 구분하는 표시입니다. 값의 크기를 지원 개수로 해석하면 안 됩니다.')
    ]
), dict(
    path='include/vdso/time.h', title='시간 namespace offset: signed 초와 unsigned 나노초',
    intro='timens_offset 구조체의 두 필드와 표현상의 의미를 읽습니다.',
    principle='시간차가 음수여도 초를 음수로, 나노초 부분을 비음수로 두어 정규화된 분할 표현을 만들 수 있습니다.',
    use='namespace 보정값과 절대 시각 구조체의 타입·단위를 구분합니다.',
    area='시간 좌표계 · 분할 표현 · signed/unsigned · 정규화 · 자료형',
    sections=[
        ('파일 전체', 'GPL-2.0과 guard 뒤 uapi/linux/types.h를 포함하고 timens_offset 하나를 정의합니다. 함수, 초기화 매크로, 범위 검사, namespace 생성 코드가 없습니다. 이 파일에는 별도의 assembly 제외 분기도 없습니다.'),
        ('필드와 부호', 'sec는 s64, nsec는 u64입니다. 초는 음수 보정을 표현할 수 있고 나노초 부분은 unsigned입니다. 둘 다 64비트라도 signed 여부는 다릅니다. 자료형만으로 nsec가 1초 미만이라고 자동 제한되지는 않으며 정상 범위는 값을 만드는 코드가 유지해야 합니다.'),
        ('음수 offset의 표현 예', '초와 나노초로 정상화한 -0.5초는 sec=-1, nsec=500000000으로 표현할 수 있습니다. sec=0에 음수 값을 u64 nsec로 대입하는 방식은 같은 의미가 아닙니다. 이 예는 수학적 표현을 설명하는 것이며 구조체 선언이 잘못된 입력을 자동 정규화한다는 뜻은 아닙니다.'),
        ('공유 데이터에서의 역할', '관련 datapage.h는 clock별 offset 배열의 원소 타입으로 timens_offset을 사용합니다. namespace reader가 host 시각에 보정값을 적용하는 데 필요한 저장 형식입니다. 이 두 필드만으로 대상 clock ID, 권한, 활성 namespace가 정해지는 것은 아니며 그 정보와 정책은 주변 코드에 있습니다.'),
        ('검증 범위', '전체 구조체와 포함 조건을 설명했습니다. fixed-width 표현, 부호가 다른 두 필드, 정상화와 타입 선언의 차이를 학습합니다. namespace offset 허용 범위나 사용자 입력 검사 전체를 이 짧은 헤더가 보장한다고 주장하지 않습니다.')
    ],
    questions=[
        ('timens_offset의 초와 나노초 타입은?', 's64 sec와 u64 nsec이다', '둘 다 s64이다', '전체 offset의 음수 표현과 소수 필드의 부호를 구분합니다. 같은 64비트 폭이어도 연산 규칙이 다릅니다.'),
        ('정규화된 -0.5초를 두 필드로 나타내면?', 'sec=-1, nsec=500000000이다', 'sec=0, nsec에 -500000000을 u64로 대입한다', '더 이른 정수 초에 양의 나노초를 더하면 -0.5초입니다. unsigned 필드에 음수를 대입하면 큰 unsigned 값이 되어 의도가 달라집니다.'),
        ('구조체 선언만으로 nsec<10^9이 보장되는가?', '아니다. 별도 생성·검증 코드가 필요하다', '그렇다. 필드 이름이 nsec이면 컴파일러가 범위를 강제한다', 'u64는 훨씬 큰 값도 표현합니다. 단위와 정상 범위는 자료형 이름만으로 검사되지 않습니다.')
    ]
)]
