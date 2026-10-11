"""Whole-file RISC-V vDSO wait hint and clocksource forwarding header."""
ROWS = [dict(
    path='arch/riscv/include/asm/vdso/processor.h',
    title='RISC-V cpu_relax: 조건부 DIV와 PAUSE·컴파일러 장벽',
    intro='대기 힌트 함수의 모든 명령과 컴파일 조건을 분석합니다.',
    principle='대기 루프의 실행 힌트와 공유 데이터 동기화, 운영체제 수면은 서로 다른 역할입니다.',
    use='툴체인 ISA 매크로와 실제 명령 인코딩, 별도의 barrier를 구별합니다.',
    area='RISC-V ISA · busy waiting · 인라인 어셈블리 · 컴파일러 장벽 · 조건부 컴파일',
    sections=[
        ('전체 구성', 'GPL-2.0-only include guard 안의 !__ASSEMBLY__ 구역에서 asm/barrier.h와 asm/insn-def.h를 포함합니다. static inline void cpu_relax(void) 하나만 정의하며 외부 변수나 syscall wrapper는 없습니다.'),
        ('조건부 나눗셈', '__riscv_muldiv가 정의된 경우 int dummy와 volatile asm의 div %0,%0,zero를 사용합니다. %0는 =r 출력이고 별도 C 입력 피연산자는 없습니다. 주석은 halt 대신 긴 지연의 stall을 유도하려는 목적이라고 설명합니다. 계산 결과 dummy를 반환하거나 이후 조건 판단에 쓰지 않습니다. 이 코드를 C의 0으로 나누는 표현식과 동일한 undefined behavior라고 설명하면 안 됩니다. 어셈블리 ISA 동작의 문맥입니다.'),
        ('조건의 정확한 출처', '분기는 CONFIG_SMP나 runtime CPU 개수 검사가 아니라 컴파일러가 제공하는 __riscv_muldiv 매크로입니다. 조건이 없으면 DIV 부분만 빠지고 뒤의 PAUSE와 barrier는 남습니다. 이 함수 자체가 CPU feature를 동적으로 탐지하는 코드가 아닙니다.'),
        ('PAUSE와 실제 인코딩', '그 다음 __asm__ __volatile__(RISCV_PAUSE)를 실행합니다. 교차 확인한 insn-def.h의 RISCV_PAUSE는 문자열 .4byte 0x100000f로 해당 명령 인코딩을 내보냅니다. 소스에 pause라는 mnemonic이 직접 없어도 명령 바이트를 포함할 수 있습니다. 주석은 instruction retirement를 줄이고 PC가 바뀐다는 전제를 설명합니다. 일정한 지연 시간이나 소비 전력 수치를 보장하는 코드는 아닙니다.'),
        ('마지막 barrier의 역할', 'PAUSE 뒤에 barrier()를 따로 호출합니다. 이는 컴파일러 메모리 접근 순서에 관한 장벽이며 이 파일에서 full hardware fence나 atomic lock을 구현하는 것은 아닙니다. 앞 asm에 x86 형태의 memory clobber가 적혀 있다고 가정하지 말고 별도의 barrier 호출을 읽어야 합니다.'),
        ('대기 조건과 범위', '함수에는 공유 플래그 읽기, 반복문, scheduler 호출, timeout이 없습니다. 호출부가 대기 조건과 올바른 동기화 규칙을 관리해야 합니다. 전체 매크로 조건과 함수 본문을 설명했으며 실제 RISC-V CPU의 stall 시간·PAUSE 지원별 성능이나 실행 결과를 측정한 것은 아닙니다.')
    ],
    questions=[
        ('__riscv_muldiv가 없으면 cpu_relax 전체가 사라지는가?', '아니다. DIV만 빠지고 PAUSE와 barrier는 남는다', '그렇다. 함수에는 아무 명령도 남지 않는다', '전처리 #endif는 PAUSE 앞에 있습니다. 조건의 정확한 범위를 읽어야 합니다.'),
        ('DIV 결과 dummy를 함수가 어디에 사용하는가?', '이후 사용하지 않는다. 지연을 유도하는 명령의 출력이다', '현재 CPU 번호로 반환한다', '반환형은 void이고 dummy를 읽는 C 문장이 없습니다. 명령의 목적과 산술 결과 사용을 구분합니다.'),
        ('RISCV_PAUSE가 포함 헤더에서 제공되는 형태는?', '고정 명령 인코딩을 내보내는 .4byte 문자열이다', 'getcpu 시스템 호출 함수 주소이다', '확인한 정의는 .4byte 0x100000f입니다. 어셈블러 mnemonic 대신 바이트 인코딩을 사용할 수 있습니다.')
    ]
), dict(
    path='arch/riscv/include/asm/clocksource.h',
    title='RISC-V clocksource 헤더: vDSO 모드 정의 연결',
    intro='아키텍처 clocksource 헤더의 전체 include 구조를 분석합니다.',
    principle='헤더는 새 동작을 구현하지 않고 필요한 선언의 경로를 통일하는 역할도 합니다.',
    use='포함 관계와 직접 구현의 범위를 구분합니다.',
    area='전처리 · 헤더 의존성 · 아키텍처 인터페이스',
    sections=[
        ('전체 파일', 'GPL-2.0과 _ASM_CLOCKSOURCE_H guard 안에 asm/vdso/clocksource.h include 하나가 있습니다. 별도 함수·전역 변수·카운터 읽기 본문은 없습니다.'),
        ('포함 관계의 의미', '공통 asm/clocksource.h 경로에서 RISC-V의 vDSO clock mode 정의를 볼 수 있게 합니다. 포함 대상은 VDSO_ARCH_CLOCKMODES에 ARCHTIMER를 제공하지만 이 파일 자체가 CSR_TIME을 읽거나 clocksource 장치를 등록하는 것은 아닙니다.'),
        ('아키텍처 차이와 범위', 'x86 clocksource.h의 vclocks_used와 사용 이력 helper는 이 파일에 없습니다. 같은 파일 이름이라도 제공 내용이 다르므로 실제 소스를 확인해야 합니다. 전체 guard와 include를 대조했고 포함 대상은 기존 별도 학습 자료로 유지합니다.')
    ],
    questions=[
        ('이 파일이 직접 수행하는 카운터 읽기 동작은?', '없다. vDSO clocksource 헤더를 포함한다', 'CSR_TIME을 매번 읽어 저장한다', '헤더 이름이 동작을 뜻하지는 않습니다. 실제 본문에는 include만 있습니다.'),
        ('x86과 마찬가지로 vclocks_used 변수를 여기서 선언하는가?', '아니다. 해당 선언은 이 파일에 없다', '그렇다. 모든 아키텍처의 clocksource.h는 동일하다', '아키텍처별 확장 API는 다를 수 있습니다. 이름만으로 다른 파일의 선언을 옮겨 읽으면 안 됩니다.')
    ]
)]
