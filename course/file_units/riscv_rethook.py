"""Complete RISC-V rethook C adapter, header and assembly trampoline."""
ROWS = [dict(
    path='arch/riscv/kernel/probes/rethook.c',
    title='RISC-V rethook C 경로: RA 교체와 S0 frame 식별',
    intro='두 함수가 공통 반환 후킹 계층과 RISC-V register 상태를 연결하는 방식을 해설합니다.',
    principle='아키텍처의 반환 주소 register를 바꾸고 원래 주소는 node에 따로 보관합니다.',
    use='x86의 stack 슬롯 교체와 RISC-V의 RA 교체를 비교합니다.',
    area='호출 규약 · 반환 주소 register · 콜백 · 아키텍처 어댑터',
    sections=[
        ('전체 파일', 'GPL-2.0-only, generic return hook 설명과 kprobes/rethook 및 로컬 헤더 include 뒤 callback과 prepare 두 함수가 있습니다. 두 함수 모두 NOKPROBE_SYMBOL로 표시됩니다. node pool 관리, handler 등록과 해제, 리스트 순회는 공통 계층에 있고 이 파일에는 없습니다.'),
        ('Callback의 반환값', '__used callback은 pt_regs를 받아 rethook_trampoline_handler(regs,regs->s0)의 반환값을 그대로 unsigned long으로 돌려줍니다. 프레임 식별 인자는 regs->sp가 아닌 s0입니다. assembly는 callback 결과를 새 RA로 사용하므로 이 반환값은 실행 복귀 경로에 실제로 사용됩니다.'),
        ('Prepare의 순서', 'prepare는 regs->ra를 rhn->ret_addr에, regs->s0를 rhn->frame에 먼저 저장합니다. 이후 regs->ra를 arch_rethook_trampoline 주소로 교체합니다. mcount 인자는 이 구현에서 읽지 않습니다. stack[0]을 직접 역참조하여 고치는 x86 경로와 같다고 설명하면 틀립니다.'),
        ('전제와 CS', '제공된 regs와 node가 유효하다는 전제를 가지며 NULL·주소 범위 검사나 새 메모리 할당은 없습니다. 원래 값 보존 후 제어 흐름 변경, register snapshot과 실제 CPU 복원의 분리, 작은 어댑터를 통한 공통 알고리즘 재사용을 학습합니다. 전체 소스 대조는 실제 RISC-V CPU에서 후킹을 실행 시험한 것은 아닙니다.')
    ],
    questions=[
        ('원래 반환 주소와 frame 값은 각각 어디에서 읽는가?', 'regs->ra와 regs->s0이다', 'stack[0]과 regs->sp이다', 'prepare의 두 대입문이 직접 보여 줍니다. 아키텍처별 호출 규약을 확인해야 합니다.'),
        ('callback의 반환값은 C 함수에서 버려지는가?', '아니다. 공통 handler 결과를 반환하여 assembly가 RA로 사용한다', '그렇다. 반환형은 void이다', '함수는 unsigned long을 반환합니다. 이어지는 trampoline의 move ra,a0가 복귀점을 설정합니다.')
    ]
), dict(
    path='arch/riscv/kernel/probes/rethook.h',
    title='RISC-V rethook 로컬 헤더: assembly와 C의 함수 계약',
    intro='짧은 헤더 전체의 선언과 include 문맥 의존성을 학습합니다.',
    principle='함수 선언은 호출 형태를 연결하지만 필요한 타입 정의와 실행 본문을 대신하지 않습니다.',
    use='assembly callback과 아키텍처 준비 함수의 타입 계약을 확인합니다.',
    area='헤더 경계 · 함수 시그니처 · 번역 단위 · 타입 의존성',
    sections=[
        ('전체 내용', 'GPL-2.0-only와 __RISCV_RETHOOK_H guard 안에 함수 선언 두 개만 있습니다. include, inline 함수, 변수, 구조체 본문은 없습니다. guard는 같은 번역 단위에서 중복 포함을 막으며 두 실행 함수의 코드는 rethook.c에 있습니다.'),
        ('Callback 선언', 'arch_rethook_trampoline_callback은 struct pt_regs 포인터를 받고 unsigned long을 반환합니다. 반환값이 assembly의 복귀 주소로 이어지는 경로이므로 void callback으로 임의 변경할 수 없습니다. 이 헤더 자체는 실제 인자 register와 호출 instruction을 정의하지 않습니다.'),
        ('Prepare 선언과 문맥', 'arch_rethook_prepare는 rethook_node와 pt_regs 포인터, bool mcount를 받고 void입니다. 필요한 구조체 tag와 bool은 포함 문맥에서 확보해야 하며 이 파일이 직접 정의하지 않습니다. 대응 C 파일은 Linux 헤더들을 먼저 포함합니다. 선언의 매개변수 존재와 실제 본문에서 그 인자를 사용한다는 사실은 별개입니다.'),
        ('CS 연결', '작은 인터페이스가 C 구현과 assembly 소비자를 연결하는 방식을 학습합니다. 이 파일 전체를 읽어도 node 수명이나 register 저장 레이아웃을 알 수 없으며 관련 구현 파일에서 확인해야 합니다.')
    ],
    questions=[
        ('이 헤더가 pt_regs 구조체 전체를 정의하는가?', '아니다. 함수 인자에서 포인터 타입으로 사용한다', '그렇다. 두 함수 선언 안에 모든 register 레이아웃이 들어 있다', '실제 필드 배치는 다른 헤더에 있습니다. 인터페이스와 데이터 정의의 책임을 구분합니다.'),
        ('callback과 prepare의 반환형은 같은가?', '아니다. callback은 unsigned long, prepare는 void이다', '그렇다. 둘 다 void이다', 'callback의 결과는 trampoline이 복귀점을 얻는 데 사용되고 prepare는 저장된 register 상태를 수정합니다.')
    ]
), dict(
    path='arch/riscv/kernel/probes/rethook_trampoline.S',
    title='RISC-V trampoline: 저장된 A0와 새 RA의 분리',
    intro='register 저장·복원 매크로와 trampoline의 전체 assembly 실행 순서를 해설합니다.',
    principle='후킹 handler의 반환값은 복귀 주소로 쓰되 원래 함수의 A0 값은 저장 영역에서 복원합니다.',
    use='함수 반환 후 callback을 호출하면서 반환값과 일반 register를 보존하는 방식을 이해합니다.',
    area='어셈블리 · 레지스터 보존 · ABI · 스택 영역 · 제어 흐름',
    sections=[
        ('전체 형식', 'GPL-2.0+, 작성자, linkage와 asm/asm-offsets include 뒤 text와 altmacro 설정, 저장·복원 매크로, SYM_CODE_START/END trampoline이 있습니다. REG_S와 REG_L 및 PT_* offset은 포함 헤더에서 제공하며 실제 register 폭과 구조 배치에 맞춰 사용됩니다. 이 파일은 offset 숫자를 직접 중복 정의하지 않습니다.'),
        ('저장하는 register 전체', 'save_all_base_regs는 x1 RA, x3 GP, x4 TP, x5~x7 T0~T2, x8~x9 S0~S1, x10~x17 A0~A7, x18~x27 S2~S11, x28~x31 T3~T6를 각각 pt_regs 슬롯에 저장합니다. x0와 x2 SP는 이 매크로에 없습니다. 이름에 all이 있어도 부동소수점·벡터·CSR까지 모두 저장하는 매크로는 아닙니다.'),
        ('영역 확보와 인자', 'trampoline은 SP에서 PT_SIZE_ON_STACK을 빼 저장 영역을 만들고 저장 매크로를 실행합니다. a0에 현재 sp를 옮겨 pt_regs 포인터로 callback을 호출합니다. 저장된 원래 A0는 callback 인자를 위해 a0를 바꿔도 메모리에 남습니다. 일반 예외 진입의 모든 pt_regs 필드가 여기서 초기화된다고 가정하면 안 됩니다. 이 본문에는 PT_SP나 status 같은 필드를 쓰는 별도 instruction이 없습니다.'),
        ('Callback 결과의 목적지', 'callback 직후 a0에 있는 결과를 ra로 옮깁니다. 이후 restore_all_base_regs는 x3~x31을 대응 슬롯에서 복원하지만 저장해 둔 x1 RA는 load하지 않습니다. 따라서 새로 찾은 실제 복귀 주소가 유지됩니다. A0는 복원 대상이므로 callback이 반환한 주소가 원래 함수의 사용자 반환값으로 남는 것은 아닙니다.'),
        ('SP와 최종 ret', '복원 후 SP에 PT_SIZE_ON_STACK을 더하여 영역을 해제하고 ret합니다. SP는 저장 슬롯에서 load하는 것이 아니라 동일 크기의 산술로 회복합니다. 저장했던 RA를 무조건 다시 불러오면 trampoline 경로로 되돌아갈 수 있으므로 RA를 복원 목록에서 제외한 점이 중요합니다.'),
        ('CS 연결과 검증 범위', '한 register가 호출 전후에 인자·반환값으로 재사용되는 ABI, 원래 값과 handler 결과의 분리, 대칭 stack 산술과 비대칭 register 복원, 부분 register snapshot을 학습합니다. 전체 assembly 대조는 실제 RISC-V 하드웨어나 emulator에서 register 보존을 시험한 결과와는 구분합니다.')
    ],
    questions=[
        ('RA를 저장했는데 복원 매크로에서 다시 읽지 않는 이유는?', 'callback이 돌려준 실제 복귀 주소를 RA에 유지하기 위해서다', 'RA는 하드웨어가 모든 호출 뒤 자동으로 원래 값으로 돌려놓기 때문이다', 'move ra,a0 뒤 복원 목록에 x1은 없습니다. 의도적으로 새 복귀점을 유지합니다.'),
        ('callback 결과가 최종 A0에 그대로 남는가?', '아니다. 결과는 RA로 옮기고 A0는 저장 슬롯에서 복원한다', '그렇다. 원래 함수 반환값은 항상 handler 주소로 바뀐다', 'restore 목록에 x10/PT_A0가 있습니다. callback 반환 주소와 원래 함수의 반환 register를 분리합니다.'),
        ('이 trampoline은 SP를 PT_SP 슬롯에서 복원하는가?', '아니다. 확보한 PT_SIZE_ON_STACK을 다시 더한다', '그렇다. restore 매크로가 x2를 load한다', 'x2는 저장·복원 목록에 없고 진입과 종료의 addi가 SP를 조절합니다.')
    ]
)]
