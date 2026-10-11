"""Whole-file x86 and ARM64 vDSO processor wait hints."""
ROWS = [dict(
    path='arch/x86/include/asm/vdso/processor.h',
    title='X86 cpu_relax: PAUSE 힌트와 컴파일러 메모리 효과',
    intro='rep_nop·cpu_relax와 getcpu 원형을 포함한 헤더 전체를 분석합니다.',
    principle='busy-wait 힌트는 대기 루프의 실행 특성을 돕지만 락 획득이나 스레드 수면을 대신하지 않습니다.',
    use='인라인 어셈블리의 volatile·memory clobber와 동기화 연산을 구별합니다.',
    area='Busy waiting · PAUSE · 인라인 어셈블리 · 컴파일러 장벽 · 전방 선언',
    sections=[
        ('전체 구성과 조건', 'GPL-2.0-only와 include guard 아래 !__ASSEMBLY__ 구역에 두 함수, 구조체 전방 선언, 함수 원형을 둡니다. 별도 include는 없습니다. __always_inline과 notrace는 포함 문맥에 의존하며 assembly 문맥에는 이 C 선언들을 제공하지 않습니다.'),
        ('Rep nop 구현', 'rep_nop은 static __always_inline void 함수이며 asm volatile("rep; nop" ::: "memory")를 실행합니다. 원본 주석은 이를 REP NOP (PAUSE)라고 부르고 busy-wait 루프에 유용한 힌트라고 설명합니다. C 반복문이나 조건 검사는 이 함수 내부에 없고 호출할 때마다 해당 어셈블리 문장을 제공합니다.'),
        ('Volatile과 memory의 범위', 'volatile은 이 어셈블리의 부작용을 컴파일러가 고려하도록 하고 memory clobber는 메모리 접근 순서에 대한 컴파일러 가정을 제한합니다. 본문에 하드웨어 메모리 fence 명령이나 atomic read-modify-write는 없습니다. 따라서 다른 CPU의 쓰기가 모두 완료되거나 어떤 공유 플래그가 true가 될 때까지 기다리는 기능이라고 해석하지 않습니다.'),
        ('Cpu relax wrapper', 'cpu_relax도 static __always_inline void이고 rep_nop()만 호출합니다. syscall, scheduler 진입, timeout, CPU migration 금지, lock 획득은 없습니다. 실제 대기 조건과 종료 가능성은 호출하는 루프가 관리해야 합니다. 원자적 변수와 필요한 메모리 순서 프로토콜 없이 cpu_relax만 넣는 것으로 올바른 동기화가 완성되는 것은 아닙니다.'),
        ('Getcpu 관련 선언', 'struct getcpu_cache는 전방 선언만 제공합니다. notrace long __vdso_getcpu(unsigned *cpu,unsigned *node,struct getcpu_cache *unused)는 원형이며 구현 본문은 별도 vgetcpu.c에 있습니다. 포인터 선언에는 구조체 전체 배치가 필요하지 않지만 이 헤더의 전방 선언만으로 sizeof(getcpu_cache)를 구할 수는 없습니다.'),
        ('CS 연결과 검증 범위', '두 힌트 함수와 모든 선언·조건을 다뤘습니다. CPU 실행 힌트, 컴파일러 메모리 효과, 공유 상태의 원자성, scheduler 수면의 차이를 학습합니다. 실제 CPU별 성능·전력·명령 실행 시간을 측정한 것은 아니므로 일정 시간만큼 쉰다는 수치 보장을 제시하지 않습니다.')
    ],
    questions=[
        ('이 cpu_relax가 스레드를 scheduler의 수면 상태로 바꾸는가?', '아니다. rep_nop 힌트를 실행한다', '그렇다. 내부에서 대기 syscall을 호출한다', '본문에는 rep_nop 호출만 있습니다. busy-wait 루프와 scheduler가 관리하는 sleep은 다른 방식입니다.'),
        ('memory clobber가 있으므로 PAUSE가 완전한 하드웨어 메모리 fence인가?', '아니다. 컴파일러 메모리 효과와 하드웨어 fence를 구분해야 한다', '그렇다. memory라는 문자열이 fence 명령을 자동 생성한다', '실제 어셈블리 문자열은 rep; nop입니다. clobber는 컴파일러 계약이며 동기화에 필요한 하드웨어 순서를 별도로 판단해야 합니다.'),
        ('getcpu_cache의 전체 배치 없이 함수 원형에 그 포인터를 쓸 수 있는가?', '그렇다. 구조체 전방 선언으로 포인터 자료형을 선언할 수 있다', '아니다. 모든 멤버가 이 헤더에 있어야 한다', '포인터를 받는 함수 선언과 구조체 멤버 접근은 필요한 타입 정보가 다릅니다. 이 파일에는 전방 선언만 있습니다.')
    ]
), dict(
    path='arch/arm64/include/asm/vdso/processor.h',
    title='ARM64 cpu_relax: YIELD 명령과 스케줄러 양보의 차이',
    intro='짧은 cpu_relax 구현 전체의 전처리 조건과 어셈블리 계약을 분석합니다.',
    principle='명령 이름이 yield라고 해서 운영체제 scheduler에 실행권을 넘기는 API와 같지는 않습니다.',
    use='아키텍처 공통 helper 이름 아래 다른 CPU 힌트를 제공하는 구조를 이해합니다.',
    area='ARM64 YIELD · busy waiting · 인라인 함수 · 컴파일러 메모리 효과 · 추상화',
    sections=[
        ('전체 파일', 'GPL-2.0-only와 __ASM_VDSO_PROCESSOR_H guard 안의 !__ASSEMBLY__ 구역에 static inline void cpu_relax(void) 하나가 있습니다. include나 외부 변수·getcpu 선언은 없습니다. x86의 같은 이름 헤더가 제공하는 모든 API를 이 파일에도 있다고 가정하지 않습니다.'),
        ('실제 명령과 함수 범위', '본문은 asm volatile("yield" ::: "memory")입니다. ARM64의 CPU 실행 힌트를 제공하며 조건을 읽거나 반복하는 코드가 아닙니다. 호출부가 기다리는 값과 루프 종료 조건을 관리합니다. 함수는 반환값이 없는 inline 후보이며 x86 원본의 __always_inline 표기와 다르게 단순 inline입니다.'),
        ('Scheduler와 메모리 순서', '이 명령을 sched_yield syscall이나 sleep 호출과 동일시하면 안 됩니다. svc 명령도 scheduler 함수 호출도 없습니다. memory clobber는 컴파일러의 메모리 효과 선언이며 DMB·DSB·ISB 같은 명시적 장벽 명령을 여기서 실행하는 것은 아닙니다. 락·원자성·공유 데이터 가시성의 계약은 별도로 필요합니다.'),
        ('아키텍처 추상화와 범위', '공통 vDSO 코드는 cpu_relax 이름을 사용하고 선택된 아키텍처 헤더는 ARM64 YIELD 또는 x86 PAUSE 같은 구현을 제공합니다. 동일 이름이 동일 명령이나 정확히 같은 지연 시간을 뜻하지는 않습니다. 전체 조건과 본문을 대조했으며 실제 ARM64 명령 실행·성능 측정은 하지 않았습니다.')
    ],
    questions=[
        ('ARM64 cpu_relax의 yield는 sched_yield 시스템 호출인가?', '아니다. 어셈블리 CPU 힌트 명령이다', '그렇다. 운영체제 실행 큐에서 현재 task를 항상 뒤로 옮긴다', '본문은 yield 하나이며 syscall 진입 svc나 scheduler 호출이 없습니다. 이름의 유사성과 실행 의미를 구분해야 합니다.'),
        ('이 함수 하나만으로 대기 조건이 충족될 때까지 반복하는가?', '아니다. 조건과 반복은 호출부가 담당한다', '그렇다. 모든 공유 변수가 안정될 때까지 내부에서 무한 반복한다', '함수에는 루프나 공유 변수 읽기가 없습니다. 재시도 루프가 호출할 힌트를 제공하는 작은 구성 요소입니다.')
    ]
)]
