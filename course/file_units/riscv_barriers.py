"""Individually authored RISC-V memory barrier headers."""
ROWS = [dict(
    path='arch/riscv/include/asm/barrier.h',
    title='RISC-V 장벽 전체: 메모리와 장치의 순서',
    intro='FENCE의 앞뒤 접근 집합을 읽고 acquire/release와 조건부 대기를 구분합니다.',
    principle='순서 장벽은 접근의 선후 관계를 제약합니다. 잠금의 상호 배제나 값의 변경을 대신하지 않습니다.',
    use='futex의 원자 명령과 함께 읽되 이 헤더가 제공하는 순서 계약과 대기 루프를 따로 추적합니다. 실제 RISC-V 하드웨어 실행 검증은 아닙니다.',
    area='메모리 모델 · 장치 I/O · acquire/release · 조건부 대기',
    sections=[
        ('파일 경계', 'GPL-2.0-only, ARM 원본 기반 표기와 저작권, 중복 포함 guard 뒤 __ASSEMBLY__가 아닌 경우에만 C용 정의를 제공합니다. cmpxchg.h와 fence.h에 의존하고 마지막에 asm-generic/barrier.h를 포함합니다. 포함된 다른 파일의 모든 구현을 이 파일의 해설 완료로 세지 않습니다.'),
        ('NOP와 반복 문자열', 'nop은 volatile asm의 nop 명령입니다. __nops(n)은 n을 문자열화해 assembler의 .rept와 .endr 사이에 nop을 배치하고 nops가 이를 asm으로 실행합니다. C 반복문이 아니며 런타임 변수만큼 반복하는 API로 볼 수 없습니다. NOP에 memory clobber나 FENCE가 없으므로 메모리 장벽 대용이 아닙니다.'),
        ('장치와 메모리 집합', 'FENCE의 첫 집합은 앞선 접근, 두 번째는 뒤따르는 접근을 나타냅니다. i/o는 장치 입력/출력, r/w는 메모리 읽기/쓰기입니다. __mb는 iorw,iorw, __rmb는 ir,ir, __wmb는 ow,ow를 사용합니다. 읽기 장벽이 모든 앞선 쓰기까지 포괄한다고 읽으면 안 됩니다.'),
        ('SMP 장벽', '__smp_mb는 rw,rw, __smp_rmb는 r,r, __smp_wmb는 w,w입니다. 장치 접근을 포함하는 앞의 집합과 달리 메모리 순서를 대상으로 합니다. 공개 SMP API의 비SMP 처리 등은 마지막에 포함하는 generic 헤더까지 함께 읽어야 하며 여기의 내부 매크로 정의만으로 모든 구성의 최종 확장을 단정하지 않습니다.'),
        ('잠금 뒤 추가 장벽', 'smp_mb__after_spinlock은 iorw,iorw입니다. 주석의 lr.aq/sc 잠금과 lr/sc.rl 해제 예시는 AQ/RL만으로 충족하는 RCpc 순서와 요구되는 RCsc 임계 구역 순서의 차이를 설명합니다. 그 요구를 만족시키기 위해 추가 full fence를 둡니다. 이 매크로는 잠금 획득 자체를 수행하지 않습니다.'),
        ('스케줄링과 I/O', '주석은 선점 가능한 영역의 장치 쓰기가 다른 hart에서 실행 가능해지기 전에 보이도록 앞선 집합에 적어도 o가 필요하다고 설명합니다. 구현은 보수적으로 full I/O fence를 선택합니다. 두 스케줄러 사용처라는 문구는 이 버전의 설계 주석이며 실제 모든 호출 위치를 별도로 조사한 결과로 제시하지 않습니다.'),
        ('Release 저장', '__smp_store_release는 대상 타입의 원자 접근 가능성을 컴파일 시 검사하고 fence rw,w를 실행한 뒤 WRITE_ONCE로 저장합니다. 앞선 읽기와 쓰기가 뒤의 게시 저장보다 늦어지지 않도록 순서를 부여합니다. 타입 검사는 주소 유효성 검사나 객체 수명 보장이 아닙니다.'),
        ('Acquire 읽기', '__smp_load_acquire는 READ_ONCE의 값을 ___p1에 보관하고 타입 검사, fence r,rw를 거쳐 보관한 값을 반환합니다. 읽기 뒤의 읽기·쓰기를 앞서 수행하지 않도록 순서를 연결합니다. 반환 직전에 다시 읽지 않으며 release/acquire 통신은 해당 값을 관찰하는 등 메모리 모델의 조건을 함께 만족해야 합니다.'),
        ('ZAWRS 조건부 읽기', 'CONFIG_RISCV_ISA_ZAWRS가 있을 때 smp_cond_load_relaxed를 정의합니다. __PTR에 포인터를 보관하고 매회 READ_ONCE 결과를 VAL에 넣습니다. cond_expr가 참이면 종료하고 거짓이면 __cmpwait_relaxed(ptr, VAL)을 호출한 뒤 재시도합니다. 반환값은 조건의 참/거짓이 아니라 마지막 관찰값을 원래 타입으로 변환한 값입니다.'),
        ('대기 루프의 계약', '조건은 VAL을 사용할 수 있습니다. 대기 helper에는 저장된 __PTR 대신 원래 ptr 표현식이 전달되므로 부작용 있는 포인터 표현식을 항상 단 한 번 평가한다고 설명하면 틀립니다. relaxed 루프 자체에는 acquire fence가 없습니다. helper 호출 한 번이 반드시 값 변경까지 기다린다는 보장이나 유한 시간 종료 보장은 이 본문에서 얻을 수 없습니다.'),
        ('CS 연결', '전처리 문자열화와 assembler 반복, 부분 순서, 장치와 메모리의 구분, 게시/관찰 패턴, 폴링 조건과 반환값, 컴파일 시 타입 검사를 학습합니다. 소스와 해설의 대응 검사는 모든 실행 순서나 장치 프로토콜의 안전성 증명을 대신하지 않습니다.')
    ],
    questions=[
        ('__mb와 __smp_mb의 FENCE 집합 차이는?', '전자는 iorw이고 후자는 rw이다', '둘 다 항상 iorw이다', '이 파일의 __mb는 장치 접근까지 포함하고 __smp_mb는 메모리 r/w 집합입니다. 실제 API 사용에는 generic 헤더의 구성별 처리도 고려합니다.'),
        ('Release 저장의 순서는?', 'fence rw,w 다음 WRITE_ONCE이다', 'WRITE_ONCE 다음 fence r,rw이다', '앞선 읽기·쓰기를 게시 저장보다 앞에 두려는 release 방향입니다. 두 번째 선택지는 acquire 읽기의 장벽과도 동작이 다릅니다.'),
        ('ZAWRS 조건부 읽기가 반환하는 것은?', '조건을 만족한 마지막 VAL이다', '항상 정수1이다', 'cond_expr는 종료 여부를 정하지만 식의 마지막은 (typeof(*ptr))VAL입니다. 예를 들어 VAL이7일 때 조건 VAL>3이 참이면7을 반환합니다.'),
        ('nops(4)가 공유 데이터 게시용 release인가?', '아니다. NOP 반복에 FENCE가 없다', '그렇다. 네 번 쉬면 모든 순서가 보장된다', '지연과 메모리 순서는 다릅니다. 해당 asm에는 FENCE나 memory clobber가 정의되어 있지 않습니다.'),
        ('smp_cond_load_relaxed만으로 뒤의 데이터 읽기에 acquire 순서를 얻는가?', '아니다. 이 매크로에는 acquire 장벽이 없다', '그렇다. 루프 종료는 항상 acquire이다', '반복해서 값을 관찰하고 조건이 참이 되는 것과 acquire 순서는 별개입니다. 필요한 순서는 적절한 API 또는 장벽 계약으로 확보해야 합니다.')
    ]
), dict(
    path='arch/riscv/include/asm/fence.h',
    title='RISC-V FENCE 헤더 전체: 명령 문자열과 컴파일러 계약',
    intro='두 입력 집합을 명령 문자열로 만드는 매크로와 SMP 조건부 asm 조각을 읽습니다.',
    principle='CPU 순서 명령과 컴파일러 memory clobber는 서로 다른 계층의 제약입니다.',
    use='barrier.h의 RISCV_FENCE 호출이 실제로 무엇으로 확장되는지 연결합니다.',
    area='전처리기 · 인라인 어셈블리 · 메모리 순서 · 구성 조건',
    sections=[
        ('전체 범위', 'GPL-2.0-only와 guard, 두 FENCE 생성 매크로, CONFIG_SMP에 따른 세 문자열 매크로, guard 종료가 전부입니다. 함수나 전역 상태를 정의하지 않습니다.'),
        ('명령 문자열 생성', 'RISCV_FENCE_ASM(p,s)는 탭, fence, 문자열화한 p, 쉼표, 문자열화한 s, 개행을 결합합니다. RISCV_FENCE_ASM(r,rw)는 fence r,rw 명령 문자열입니다. 그 자체는 C에서 실행되는 문장이 아니라 asm 안에 넣을 문자열 조각입니다.'),
        ('실행 래퍼', 'RISCV_FENCE는 GNU statement expression 안에서 volatile inline asm을 사용합니다. 출력·입력 피연산자는 없고 memory clobber를 선언합니다. 실제 fence는 CPU 순서를, clobber는 컴파일러가 메모리 접근을 다루는 제약을 표현합니다. 이 매크로가 특정 변수 값을 반환하거나 메모리를 새 값으로 수정하는 것은 아닙니다.'),
        ('SMP 조각', 'CONFIG_SMP일 때 RISCV_ACQUIRE_BARRIER는 r,rw, RELEASE는 rw,w, FULL은 rw,rw 문자열입니다. 이 조각에는 독립적인 C asm 문이나 clobber 목록이 없으므로 이를 담는 asm의 계약까지 읽어야 합니다.'),
        ('비SMP 분기', '비SMP에서는 세 BARRIER 조각을 빈 매크로로 정의합니다. 반면 위의 RISCV_FENCE와 RISCV_FENCE_ASM은 이 조건 밖에 있으므로 사라지지 않습니다. 비SMP에서는 파일의 모든 fence가 제거된다고 일반화하면 틀립니다.'),
        ('CS 연결', '전처리 문자열화, 문자열 리터럴 결합, 조건부 컴파일, compiler와 CPU 순서의 구분을 학습합니다. 여기의 SMP FULL 조각은 rw,rw로 장치 i/o를 명시하지 않으며 이름만 보고 I/O full fence로 해석하지 않습니다.')
    ],
    questions=[
        ('비SMP 구성에서 RISCV_FENCE 자체도 빈 매크로인가?', '아니다. 세 BARRIER 조각만 비워진다', '그렇다. 헤더 전체가 빈 매크로다', 'CONFIG_SMP 분기는 ACQUIRE/RELEASE/FULL_BARRIER에만 걸려 있습니다. 실행 래퍼는 조건 밖에 정의됩니다.'),
        ('RISCV_FENCE_ASM(r,rw)만 C 문장처럼 쓰면 장벽이 실행되는가?', '아니다. asm에 삽입할 명령 문자열이다', '그렇다. 문자열화가 CPU를 실행한다', '실행 래퍼 RISCV_FENCE가 volatile asm에 문자열을 넣습니다. 문자열 생성과 명령 실행을 구분해야 합니다.'),
        ('memory clobber와 fence 명령은 같은 계층인가?', '아니다. 각각 컴파일러와 CPU 순서에 관여한다', '그렇다. 둘 다 변수에0을 저장한다', 'clobber는 컴파일러에 메모리 영향을 알리고 fence는 하드웨어 접근 순서를 제약합니다. 어느 것도 여기서 특정 변수에0을 쓰는 연산이 아닙니다.')
    ]
)]
