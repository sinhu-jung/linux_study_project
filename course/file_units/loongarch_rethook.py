"""Complete LoongArch rethook adapter, declarations and trampoline."""
ROWS = [dict(
    path='arch/loongarch/kernel/rethook.c',
    title='LoongArch rethook: R1 반환 주소와 frame 0 계약',
    intro='두 C 함수와 probe 제한 표시를 통해 LoongArch의 공통 rethook 연결을 학습합니다.',
    principle='동일한 공통 함수라도 아키텍처가 전달하는 frame 식별값은 다릅니다.',
    use='RISC-V의 S0 기반 연결과 LoongArch의 0 전달 방식을 비교합니다.',
    area='아키텍처 어댑터 · 반환 주소 · 콜백 · 실행 계측',
    sections=[
        ('전체 구성', 'GPL-2.0과 구현 설명, kprobes/rethook 및 로컬 헤더 포함 뒤 callback, prepare, NOKPROBE 표시가 있습니다. callback과 prepare뿐 아니라 외부 assembly 심볼 arch_rethook_trampoline도 probe 금지 대상으로 표시합니다. 실제 assembly 코드는 별도 파일입니다.'),
        ('Callback', '__used callback은 regs를 받아 rethook_trampoline_handler(regs,0)의 결과를 unsigned long으로 반환합니다. 두 번째 인자는 SP나 FP를 읽은 값이 아니라 상수 0입니다. 반환값은 assembly가 실제 복귀 주소로 사용합니다. 공통 handler 내부의 검색 방식은 이 파일에 없습니다.'),
        ('준비 단계', 'prepare는 rhn->frame=0, rhn->ret_addr=regs->regs[1]을 설정하고 regs->regs[1]을 trampoline 주소로 바꿉니다. R1이 이 경로의 반환 주소 register입니다. mcount는 전달받지만 사용하지 않습니다. 직접 stack 메모리를 검색하거나 새 node를 할당하는 코드는 없습니다.'),
        ('CS와 범위', '기존 반환 주소 보존 후 실행 경로 변경, 아키텍처별 register snapshot, 공통 callback에 전달하는 계약의 차이를 학습합니다. frame이 0이라는 사실만으로 모든 아키텍처의 frame 기반 검색이 같다고 추정하지 않습니다. 전체 소스 대조는 실제 LoongArch 후킹 실행 시험이 아닙니다.')
    ],
    questions=[
        ('prepare와 callback이 사용하는 frame 식별값은?', '둘 다 0이다', '둘 다 현재 FP register 값이다', 'prepare는 node frame에 0을 쓰고 callback은 공통 handler에 0을 전달합니다.'),
        ('원래 반환 주소를 읽고 교체하는 register 슬롯은?', 'regs->regs[1]이다', 'regs->regs[3]이다', '본문의 두 대입은 R1을 대상으로 합니다. SP를 저장하는 R3 슬롯과 구분해야 합니다.')
    ]
), dict(
    path='arch/loongarch/kernel/rethook.h',
    title='LoongArch rethook 로컬 선언: callback 반환형과 준비 인자',
    intro='두 함수 선언으로 구성된 로컬 헤더 전체를 해설합니다.',
    principle='헤더는 타입 계약을 제공하며 구조체 정의나 실행 동작을 자동으로 제공하지 않습니다.',
    use='C 구현과 assembly 호출 사이의 이름·타입 연결을 확인합니다.',
    area='함수 선언 · 타입 계약 · 헤더 의존성',
    sections=[
        ('전체 내용', 'GPL-2.0, __LOONGARCH_RETHOOK_H guard와 callback 및 prepare 선언만 있습니다. include나 구조체 본문, 변수, inline 실행 코드는 없습니다.'),
        ('두 시그니처', 'callback은 pt_regs 포인터를 받고 unsigned long을 반환합니다. prepare는 rethook_node 포인터, pt_regs 포인터, bool mcount를 받아 void로 끝납니다. 같은 후킹 계열 함수라도 반환형과 역할이 다릅니다.'),
        ('포함 문맥과 CS', 'bool과 구조체 타입의 준비는 앞서 포함한 Linux 헤더 등 문맥에 의존합니다. 이 선언만으로 pt_regs 필드 배치나 register별 ABI를 알 수는 없습니다. guard의 중복 포함 방지와 실제 구현 존재 여부도 별개입니다.')
    ],
    questions=[
        ('이 헤더 자체가 레지스터를 저장하는가?', '아니다. 함수 선언만 제공한다', '그렇다. pt_regs 인자가 있으면 자동 저장된다', '실제 저장 instruction은 trampoline assembly에 있고 이 파일에는 실행 본문이 없습니다.'),
        ('callback의 반환형은 무엇인가?', 'unsigned long이다', 'void이다', 'callback 결과를 assembly가 복귀 주소로 사용하므로 준비 함수의 void 반환과 구분합니다.')
    ]
), dict(
    path='arch/loongarch/kernel/rethook_trampoline.S',
    title='LoongArch trampoline: register 저장과 CRMD 하위 비트 복원',
    intro='일반 register와 제어 상태 일부를 저장하고 callback 뒤 실제 반환 주소로 복귀하는 전체 assembly를 해설합니다.',
    principle='저장·복원 목록과 그 뒤의 제어 register 조작을 끝까지 읽어야 최종 register 상태를 알 수 있습니다.',
    use='RISC-V trampoline과 비교해 SP 기록 및 interrupt·권한 상태 처리의 차이를 이해합니다.',
    area='레지스터 ABI · 제어 레지스터 · 비트 마스크 · 스택 프레임 · 복귀 흐름',
    sections=[
        ('전체 구성', 'GPL-2.0+, linkage와 stackframe.h 포함, text section 뒤 두 매크로와 SYM_CODE trampoline이 있습니다. 진입부는 UNWIND_HINT_UNDEFINED를 둡니다. cfi_st/cfi_ld와 PT_* 및 LONG_S/L은 포함 헤더에서 정의되며 이 파일이 그 offset과 폭을 새로 정의하지는 않습니다.'),
        ('저장 목록', 'save_all_base_regs는 ra/R1, tp/R2, a0~a7/R4~R11, t0~t8/R12~R20, u0/R21, fp/R22, s0~s8/R23~R31을 저장합니다. R0와 SP/R3는 이 매크로 목록에 없습니다. 모든 부동소수점·벡터 register까지 저장한다는 뜻도 아닙니다.'),
        ('CRMD 일부 저장', '일반 register 저장 후 t0로 CRMD를 읽고 0x7과 AND하여 PLV 비트 1:0 및 IE 비트 2만 PT_CRMD에 저장합니다. CRMD 전체 값을 보존하는 것이 아닙니다. t0는 그 전에 이미 저장했으므로 이 임시 사용으로 저장 영역의 원래 t0 값이 바뀌지는 않습니다.'),
        ('Stack 확보와 SP 기록', 'trampoline은 SP에서 PT_SIZE를 빼고 저장 매크로를 실행합니다. 이후 현재 sp+PT_SIZE를 t0에 계산하여 PT_R3에 기록합니다. 이 값은 영역 확보 전 SP입니다. RISC-V의 앞선 구현과 달리 이 본문에는 원래 SP를 pt_regs 슬롯에 기록하는 명시적 단계가 있습니다.'),
        ('Callback과 RA', 'a0에 현재 sp를 넣어 pt_regs 포인터를 전달하고 bl로 callback을 호출합니다. 돌아오면 a0 결과를 ra로 옮깁니다. restore 매크로는 tp부터 s8까지 복원하지만 ra/R1은 load하지 않아 새 실제 복귀 주소를 유지합니다. a0도 저장 슬롯에서 복원하므로 callback의 반환 주소가 최종 a0 값으로 그대로 남지는 않습니다.'),
        ('복원 후 다시 바뀌는 임시 register', '일반 register load가 끝난 뒤 t0에 PT_CRMD를 읽고 t1에 0x7을 넣어 csrxchg로 CRMD의 해당 비트를 갱신합니다. 따라서 t0와 t1은 앞에서 복원된 이후 다시 임시로 사용됩니다. restore_all이라는 이름만 보고 모든 일반 register가 진입값 그대로 최종 유지된다고 설명하면 틀립니다. 제어 상태 갱신은 mask가 지정한 하위 비트에 한정됩니다.'),
        ('최종 복귀와 CS', '마지막에 SP에 PT_SIZE를 더하고 jr ra로 복귀합니다. PT_R3을 load해서 SP를 되돌리는 방식이 아닙니다. callback 인자와 결과 register 재사용, 제어 register의 부분 갱신, 중간 복원과 최종 상태의 차이를 학습합니다. 이 소스 대조는 실제 하드웨어에서 interrupt 상태와 모든 register 보존을 시험한 결과가 아닙니다.')
    ],
    questions=[
        ('PT_CRMD에 저장되는 것은 CRMD 전체인가?', '아니다. 0x7로 선택한 PLV와 IE 비트이다', '그렇다. 어떤 mask도 적용하지 않는다', 'csrrd 뒤 andi 0x7을 실행합니다. 제어 register의 부분 상태 저장입니다.'),
        ('PT_R3에 기록하는 SP는 어느 시점의 값인가?', 'PT_SIZE 영역 확보 전의 SP이다', '항상 현재의 낮아진 SP 그대로이다', '영역 확보 후 sp+PT_SIZE를 계산하여 저장합니다. 저장할 값과 현재 CPU SP를 구분해야 합니다.'),
        ('t0와 t1은 load 이후 최종 복귀까지 그대로 유지되는가?', '아니다. CRMD 복원 단계에서 다시 사용된다', '그렇다. restore 매크로 안에서는 load 외에 아무 동작도 없다', '매크로 끝까지 읽으면 t0로 상태를 읽고 t1에 mask를 넣는 추가 instruction이 있습니다.')
    ]
)]
