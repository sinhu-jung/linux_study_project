"""Complete PowerPC probe-driven return hook adapter."""
ROWS = [dict(
    path='arch/powerpc/kernel/rethook.c',
    title='PowerPC rethook: trap과 optprobe의 두 복귀 경로',
    intro='짧은 trampoline에 kprobe를 등록하고 NIP와 link를 함께 보정하는 전체 구현을 학습합니다.',
    principle='같은 논리적 복귀점도 trap 재개와 분기 기반 계측에서 서로 다른 register 보정이 필요합니다.',
    use='아키텍처별 rethook 구현에서 kprobe 의존성과 명령어 위치 보정을 이해합니다.',
    area='링크 레지스터 · trap · 계측 분기 · 명령어 재개 · callback 반환 계약',
    sections=[
        ('전체 구성', 'GPL-2.0-only와 kprobes에 의존한다는 주석, 두 Linux 헤더 include 뒤 assembly trampoline, pre-handler, prepare, fixup, 정적 kprobe와 초기화가 있습니다. 앞서 RISC-V의 전체 register 저장 trampoline과 달리 이 파일은 trampoline 지점에 probe를 설치해 handler를 실행하는 구조입니다.'),
        ('두 명령 trampoline', '전역 function 심볼 arch_rethook_trampoline의 assembly 본문은 nop과 blr입니다. 주석은 init_kprobes가 이곳에 probepoint를 마련하고 후킹된 함수가 돌아오면 handler가 실행된다고 설명합니다. 이 assembly 블록 안에 일반 C callback을 직접 call하거나 pt_regs 전체를 저장하는 본문은 없습니다. probe 실행 체계가 중간 연결을 담당합니다.'),
        ('Pre-handler의 결과 변환', 'trampoline_rethook_handler는 공통 handler에 regs와 regs->gpr[1]을 전달하고 그 unsigned long 결과를 논리 부정하여 int로 반환합니다. 따라서 결과가 0이면 1, 0이 아니면 0입니다. 실제 반환 주소 값을 그대로 pre-handler의 int 결과로 전달하는 코드가 아닙니다. p 인자는 이 본문에서 사용하지 않습니다.'),
        ('준비 시 보존', 'arch_rethook_prepare는 regs->link를 rh->ret_addr에, gpr[1]을 rh->frame에 저장한 뒤 link를 trampoline 주소로 바꿉니다. mcount 인자는 사용하지 않습니다. frame은 주소를 담은 GPR1에서 얻으며 별도의 FP 체인을 이 함수에서 순회하지 않습니다.'),
        ('Trap 복귀 보정', 'fixup 주석의 첫 경로는 trap→kprobe_handler입니다. trap에서 돌아갈 주소를 NIP에 맞춰야 하지만 kprobe_handler가 명령을 에뮬레이션하며 NIP를 다시 증가시키므로 regs_set_return_ip에는 orig_ret_address-4를 전달합니다. 여기서 4를 빼는 것은 최종 복귀점을 무조건 앞 명령으로 바꾸려는 목적이 아니라 이후 진행을 반영하는 보정입니다.'),
        ('Optprobe 복귀 보정', '두 번째 경로는 optprobe branch→optimized_callback→opt_pre_handler입니다. 주석은 이 경로에서 NIP가 복귀 대상으로 반영되지 않으므로 regs->link를 원래 주소로 설정하여 trampoline의 후속 blr이 올바른 위치로 가게 한다고 설명합니다. fixup은 경로를 if로 구분하지 않고 NIP용 보정과 link 대입을 모두 수행합니다.'),
        ('Probe 등록과 오류', '정적 trampoline_p는 addr를 trampoline으로, pre_handler를 위 함수로 설정합니다. arch_init_kprobes는 register_kprobe 결과를 그대로 반환합니다. 등록 실패를 무조건 0으로 바꾸거나 성공한 것으로 숨기지 않습니다. 이 파일에 별도 unregister나 종료 함수는 없습니다.'),
        ('계측 제한과 CS', 'pre-handler, prepare, fixup은 NOKPROBE_SYMBOL로 표시합니다. trampoline은 이 구현에서 실제 등록 대상이라는 점을 다른 아키텍처의 trampoline probe 금지 표시와 혼동하지 않습니다. 명령어 에뮬레이션 후 재개, 동일 기능의 두 실행 경로, callback 값의 논리 변환, 등록 오류 전파를 학습합니다. 전체 원본 대조는 실제 PowerPC trap/optprobe 동시 실행 시험이 아닙니다.')
    ],
    questions=[
        ('공통 handler가 0이 아닌 주소를 반환하면 pre-handler의 반환값은?', '0이다', '그 주소를 int로 잘라 그대로 반환한다', '본문은 논리 부정 연산 !를 사용합니다. 반환 주소와 pre-handler의 제어 결과는 다른 값입니다.'),
        ('fixup이 NIP용 주소에 4를 빼는 이유는?', '후속 명령 에뮬레이션에서 NIP가 다시 증가하는 경로를 반영하기 위해서다', '원래 함수의 마지막 명령을 항상 다시 실행하기 위해서다', '주석은 trap 경로의 kprobe_handler 진행을 이유로 설명합니다. 최종 의도된 복귀점과 중간 상태를 구분합니다.'),
        ('optprobe 경로를 위해 별도로 원래 주소를 넣는 register는?', 'link이다', 'gpr[1] frame 값만 바꾼다', '후속 blr이 link를 사용하도록 regs->link=orig_ret_address를 수행합니다.'),
        ('arch_init_kprobes는 등록 실패를 어떤 방식으로 전달하는가?', 'register_kprobe의 결과를 그대로 반환한다', '항상 0을 반환한다', '본문은 return register_kprobe(&trampoline_p)입니다. 다른 초기화 코드의 관례를 가정하지 않습니다.')
    ]
)]
