"""Complete x86 return hook trampoline and fixup implementation."""
ROWS = [dict(
    path='arch/x86/kernel/rethook.c',
    title='x86 rethook: 가짜 반환 주소와 원래 복귀점의 교체',
    intro='후킹 준비, assembly trampoline, pt_regs 보정과 실제 반환 주소 복원을 전체 파일로 학습합니다.',
    principle='일반 함수 프레임을 만들지 않는 trampoline은 명시적인 레지스터 배치와 unwinder annotation 계약에 의존합니다.',
    use='연결 리스트에 보관한 반환 주소가 실제 x86 복귀 흐름에 적용되는 과정을 이해합니다.',
    area='호출 규약 · 어셈블리 · register 보존 · 반환 주소 · 계측 재진입 방지',
    sections=[
        ('전체 구성과 역할', 'GPL-2.0-or-later와 kprobes에서 유래했다는 주석, 관련 include 및 kprobes/common.h 뒤 assembly와 네 C 함수 선언·정의가 있습니다. callback을 assembly에서 부르도록 __visible 선언하고 정의에는 __used도 붙입니다. ANNOTATE_NOENDBR이 없으면 빈 매크로로 보완합니다. SAVE_REGS_STRING 등의 실제 register 저장 순서는 포함한 공통 헤더에 있으며 여기서 임의로 새 순서를 정의하지 않습니다.'),
        ('후킹 준비', 'arch_rethook_prepare는 regs->sp를 unsigned long 포인터로 보고 stack[0]의 원래 반환 주소를 rh->ret_addr에 저장하고 regs->sp를 rh->frame에 저장합니다. 그 다음 stack[0]을 trampoline 주소로 바꿉니다. mcount 인자는 이 x86 본문에서 사용하지 않습니다. 여기에는 stack 포인터 범위 검증이나 node 할당이 없으므로 준비된 호출 문맥과 node를 전달하는 상위 계약이 필요합니다.'),
        ('Assembly 심볼과 fake 주소', 'asm 블록은 text section에 전역 function 심볼을 선언합니다. 대상 함수가 ret으로 진입하면 trampoline 자신을 가짜 반환 주소로 push하고 UNWIND_HINT_FUNC를 둡니다. 원래 실제 반환 주소는 node에 보관되어 있습니다. 이 fake 주소는 unwinder가 rethook임을 알아볼 수 있게 하는 표식이며 최종 복귀 전에 교체됩니다.'),
        ('64비트 경로', 'X86_64이면 ret에서만 진입한다는 설명과 ANNOTATE_NOENDBR을 두고 fake 주소, __KERNEL_DS, 현재 rsp, flags 순서의 준비 동작을 실행합니다. 주석상 저장되는 SP는 원래 기준보다 16바이트 낮아 callback에서 보정합니다. SAVE_REGS_STRING 후 현재 rsp를 rdi에 넣어 pt_regs 인자를 전달하고 callback을 호출합니다. 복원 매크로 뒤 rsp를 16 증가시키고 popfq한 다음 공통 ASM_RET에 도달합니다.'),
        ('32비트 경로', '32비트는 pushl fake 주소, ss, esp, flags를 사용하고 저장 SP는 8바이트 낮다고 주석이 설명합니다. 저장 매크로 후 esp를 eax에 넣어 callback으로 전달하고 복원 뒤 esp를 8 증가시키고 popfl합니다. 인자 전달 register와 슬롯 폭이 64비트 경로와 다르지만 양쪽 모두 같은 C callback과 최종 ASM_RET로 연결됩니다.'),
        ('Callback의 pt_regs 보정', 'callback은 cs=__KERNEL_CS, 32비트이면 gs=0, ip=trampoline 주소, orig_ax=~0UL로 설정합니다. sp에는 2*sizeof(long)을 더해 저장 시의 차이를 보정합니다. frame_pointer 변수는 regs+1 주소이며 regs->bp를 읽어 온 값이 아닙니다. 이 변수 이름만 보고 전형적인 frame-pointer chain의 BP라고 해석하면 틀립니다.'),
        ('Generic handler 호출과 주소 복원', 'callback은 rethook_trampoline_handler에 regs와 frame_pointer의 정수 값을 전달합니다. 그 호출의 unsigned long 반환값을 이 C 본문에서 직접 저장하지는 않습니다. 주석은 generic handler가 arch_rethook_fixup_return을 호출하여 regs 다음 fake 반환 주소 슬롯을 복원한다고 설명합니다. 실제 fixup 함수도 (regs+1)의 unsigned long 자리에 correct_ret_addr를 씁니다. regs->ip에 원래 주소를 대입하는 방식이 아닙니다.'),
        ('FLAGS를 ss 위치로 옮기는 이유', 'generic handler가 끝나면 regs->flags를 unsigned long 폭으로 regs->ss 위치에 복사합니다. assembly는 다른 슬롯을 건너뛴 뒤 이 위치의 값을 POPF로 복원하고 즉시 RET할 수 있습니다. 여기의 ss 메모리 위치는 복원 흐름을 위한 임시 저장 용도로 쓰이며, flags 값을 실제 segment selector로 로드한다는 뜻은 아닙니다.'),
        ('비표준 프레임과 probe 제한', 'trampoline은 frame pointer를 갱신하지 않아 표준 프레임을 만들지 않는다고 주석이 설명하고 STACK_FRAME_NON_STANDARD_FP로 표시합니다. 주석은 FP unwinder가 별도 hint 없이도 추적할 수 있다고 덧붙입니다. trampoline, callback, fixup, prepare는 NOKPROBE_SYMBOL로 표시되어 probe 재진입 문제를 피하는 경계가 됩니다. annotation이 assembly 내용을 대신 실행하는 코드는 아닙니다.'),
        ('CS 연결과 검증 범위', '기존 반환 주소를 보조 저장소에 보존하고 실행 흐름을 우회한 뒤 복원하는 방법, stack 슬롯과 pt_regs 배치, register 폭별 산술, callback의 부수효과와 반환값의 차이를 학습합니다. 전체 소스 대조는 실제 x86 32/64비트에서 trampoline을 실행하거나 모든 계측 기능의 조합을 시험한 결과와 구분합니다.')
    ],
    questions=[
        ('arch_rethook_prepare는 원래 반환 주소를 어디에 보존하는가?', 'node의 ret_addr에 저장한다', 'stack[0]을 덮어쓴 뒤에는 보존하지 않는다', 'stack[0]을 먼저 rh->ret_addr에 저장한 다음 trampoline 주소로 바꿉니다. 실행 흐름 우회와 원래 복귀점 보존이 함께 필요합니다.'),
        ('callback의 frame_pointer 변수는 regs->bp 값인가?', '아니다. regs 구조체 바로 다음 주소이다', '그렇다. 이름이 frame_pointer이면 항상 BP register이다', '식은 (long *)(regs+1)입니다. 변수 이름보다 실제 포인터 산술을 확인해야 합니다.'),
        ('fixup 함수가 실제 복귀점을 쓰는 곳은?', 'regs 다음의 가짜 반환 주소 슬롯이다', 'regs->ip 필드만 바꾼다', '본문은 frame_pointer=(void *)(regs+1) 후 역참조 대입입니다. callback의 ip는 trampoline으로 설정됩니다.'),
        ('flags를 ss 위치로 복사하는 것은 segment selector 변경을 위한 것인가?', '아니다. assembly의 POPF 직후 RET 순서를 위한 저장 배치이다', '그렇다. flags를 새로운 SS selector로 직접 로드한다', '주석과 assembly의 add/POPF/RET 순서가 목적을 보여 줍니다. 구조체 필드 이름만으로 이 특별한 복원 경로를 해석하면 안 됩니다.')
    ]
)]
