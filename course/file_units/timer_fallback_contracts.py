"""Whole generic timer fallback and RISC-V CLINT sharing contract."""
ROWS = [dict(
    path='include/asm-generic/timex.h',
    title='공통 timex 전체: 카운터 부재를 나타내는 기본값',
    intro='실제 counter가 없는 기본 구현과 보정 기능 표시의 차이를 읽습니다.',
    principle='인터페이스가 존재하는 것과 유효하게 증가하는 시간 값을 제공하는 것은 다릅니다.',
    use='실제 TIME/CLINT를 읽는 RISC-V timex 구현과 대비합니다.',
    area='아키텍처 fallback · 전처리기 · 시간 카운터 · 부팅 보정',
    sections=[
        ('파일 전체 구성', 'GPL-2.0·guard 뒤 cycles_t typedef,조건부 get_cycles 기본 함수,보정 관련 주석과 기능 매크로 해제가 전부입니다. 헤더 자체에 하드웨어 접근이나 주기적인 값 증가,타이머 초기화 코드는 없습니다.'),
        ('타입과 상수 반환', 'cycles_t는 unsigned long입니다. get_cycles 매크로가 없으면 같은 이름의 inline 함수를 정의해 항상0을 반환합니다. 이0은 boot 이후 시간이0이라는 측정 결과도 아니고 errno 형식의 오류 반환도 아닙니다. 실제 counter를 제공하지 않는 fallback 본문입니다.'),
        ('전처리 검사의 범위', '#ifndef get_cycles는 매크로 정의 여부를 검사합니다. C 함수 선언의 존재를 compiler처럼 검색하는 검사가 아닙니다. 다른 아키텍처 헤더의 자기참조 get_cycles 매크로가 이런 방식의 override 탐지에 쓰일 수 있습니다. typedef 자체는 get_cycles 조건 밖에 있습니다.'),
        ('현재 timer 기능 해제', 'ARCH_HAS_READ_CURRENT_TIMER를 조건 없이 #undef합니다. 주석은 아키텍처가 read_current_timer와 기능 표시를 구현하면 부팅 중 비싼 delay loop 보정을 피할 수 있다고 권장합니다. 하지만 이 공통 파일은 해당 함수를 구현하거나 그 기능을 켜지 않습니다. 포함 순서에 따라 기존 매크로도 해제된다는 본문을 그대로 읽어야 합니다.'),
        ('CS 연결과 사용 범위', 'fallback 의미,정수 타입과 실제 시간원,전처리 선언 탐지,선택적 capability,부팅 비용을 학습합니다. 상수0을 증가하는 counter로 가정해 양수 차이를 기다리면 진행할 수 없으므로 호출자는 인터페이스 존재만으로 시간원 가용성을 가정하면 안 됩니다. 이 파일만으로 모든 호출자의 방어 처리를 검증한 것은 아닙니다.')
    ],
    questions=[
        ('기본 get_cycles는 호출마다 증가하는가?', '아니다. 항상0이다', '그렇다. unsigned long 값이 자동 증가한다', '본문은 return 0뿐입니다. 타입과 함수 이름이 실제 counter를 생성하지 않습니다.'),
        ('#ifndef get_cycles가 검사하는 것은?', '전처리 매크로 정의 여부이다', '모든 C 함수 선언의 존재 여부이다', '전처리기는 C 심벌 테이블을 조회하지 않습니다. 자기참조 매크로로 구현 존재를 표시하는 패턴과 연결됩니다.'),
        ('이 파일은 ARCH_HAS_READ_CURRENT_TIMER를 어떻게 하는가?', '해제한다', '항상 활성화한다', '주석의 구현 권장과 실제 #undef를 구분해야 합니다. 공통 fallback은 timer 기반 보정 기능을 제공하지 않습니다.')
    ]
), dict(
    path='arch/riscv/include/asm/clint.h',
    title='RISC-V CLINT 헤더 전체: 직접 MMIO 시간 접근의 계약',
    intro='드라이버가 제공하는 시간 레지스터 포인터와 그 이름에 담긴 플랫폼 가정을 읽습니다.',
    principle='ISA가 보장하는 속성과 특정 장치 배치·접근 순서의 가정은 구분해야 합니다.',
    use='timex.h의 clint_time_val 직접 읽기를 선언과 주석의 전제로 연결합니다.',
    area='MMIO · ISA와 플랫폼 · extern 공유 상태 · 주소공간 타입',
    sections=[
        ('파일 범위', 'GPL-2.0-only·저작권·guard 뒤 linux/types.h와 asm/mmio.h를 포함합니다. CONFIG_RISCV_M_MODE 안의 설명과 extern u64 __iomem *clint_time_val 선언이 전부입니다. 매핑 설치,변수 정의,read/write 함수,초기화 루틴은 없습니다.'),
        ('드라이버와 직접 접근', '주석은 포인터가 CLINT 드라이버에 존재하지만 MMIO timer 읽기의 overhead를 피하려고 timex.h에서 직접 사용한다고 설명합니다. 이 헤더의 extern 선언이 드라이버를 로드하거나 주소를 자동으로 초기화하는 것은 아닙니다.'),
        ('ISA의 보장과 추가 전제', '주석은 mtime을 일정 주파수로 증가하는64비트 메모리 매핑 레지스터라고 설명합니다. 동시에 이 사용 방식에 필요한 순서 제약과 메모리 배치 등은 ISA 정의만으로 충족되지 않을 수 있다고 명시합니다. 그래서 일반적인 riscv_mtime 대신 clint_time_val이라는 이름을 사용해 CLINT 관련 추가 가정을 드러냅니다.'),
        ('타입과 구성', 'u64는 가리키는 레지스터의 논리 폭이고 __iomem은 I/O 주소공간 주석입니다. 포인터 타입만으로32비트 CPU의64비트 단일 원자 읽기가 보장되지는 않습니다. M-mode가 아니면 이 선언도 제공되지 않으며 timex.h의 다른 모드 경로는 TIME CSR을 사용합니다.'),
        ('CS 연결과 검증 범위', '선언과 저장 공간,공유 포인터 수명,MMIO와 일반 RAM,ISA와 장치 통합 계약,빠른 접근의 전제 조건을 학습합니다. 이 파일을 읽은 것으로 CLINT 드라이버 전체나 실제 장치의64비트 접근 순서를 검증했다고 세지 않습니다.')
    ],
    questions=[
        ('extern clint_time_val 선언이 MMIO 매핑을 생성하는가?', '아니다. 주소를 담는 외부 심벌의 선언이다', '그렇다. 헤더를 포함하면 자동 매핑된다', '저장 공간과 초기화는 다른 구현의 역할입니다. timex.h는 준비된 포인터를 사용하므로 호출 시점도 중요합니다.'),
        ('이름이 일반 riscv_mtime이 아닌 이유를 주석은 어떻게 설명하는가?', 'ISA 밖의 배치·순서 가정이 필요함을 드러내기 위해서이다', '레지스터가32비트이기 때문이다', '주석은64비트 mtime을 설명하면서 추가 플랫폼 제약을 구분합니다. 이름을 통해 그 전제를 나타냅니다.'),
        ('u64 __iomem 포인터가 단일64비트 원자 접근을 보증하는가?', '아니다. 실제 accessor와 CPU·장치 계약을 확인해야 한다', '그렇다. 타입이 버스 동작을 강제한다', 'RISC-V timex의32비트 경로는 두 word와 재검사를 사용합니다. 논리 데이터 폭과 실제 접근 방식은 별개입니다.')
    ]
)]
