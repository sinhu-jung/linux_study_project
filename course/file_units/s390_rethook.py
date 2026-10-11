"""Whole s390 return hook C adapter and local header."""
ROWS = [dict(
    path='arch/s390/kernel/rethook.c',
    title='s390 rethook C 경로: GPR14 복귀점과 GPR15 frame',
    intro='준비·복귀 보정·callback의 세 함수와 probe 금지 표시를 전체 파일에서 학습합니다.',
    principle='원래 반환 주소 보존과 실제 복귀 register 보정은 별개의 시점에 수행됩니다.',
    use='x86·RISC-V·LoongArch와 비교하여 s390의 반환 후킹 계약을 이해합니다.',
    area='레지스터 ABI · 반환 주소 · 아키텍처 어댑터 · callback · 진단 재진입',
    sections=[
        ('전체 범위', 'GPL-2.0-or-later, 공통 rethook/kprobes와 로컬 헤더 include 뒤 prepare, fixup, callback이 있습니다. 마지막에는 외부 assembly trampoline도 NOKPROBE_SYMBOL로 표시합니다. 이 C 파일에 assembly trampoline 본문이나 PSW를 읽고 쓰는 코드가 들어 있지는 않습니다.'),
        ('준비 단계', 'arch_rethook_prepare는 regs->gprs[14]를 rh->ret_addr에, gprs[15]를 rh->frame에 저장합니다. 이후 gprs[14]를 arch_rethook_trampoline 주소로 바꿉니다. 원래 복귀점은 교체 전에 보관됩니다. bool mcount는 이 본문에서 사용하지 않습니다. register snapshot의 수정과 실제 CPU 복원은 구분해야 합니다.'),
        ('실제 복귀점 보정', 'arch_rethook_fixup_return은 correct_ret_addr를 gprs[14]에 대입합니다. node를 다시 할당하거나 frame 값을 갱신하는 코드가 아니며 stack 주소를 직접 역참조해 쓰는 x86 fixup과 다릅니다. 반환형은 void이고 수정 결과는 regs에 남습니다.'),
        ('공통 handler 연결', 'callback은 rethook_trampoline_handler(regs,regs->gprs[15])의 결과를 unsigned long으로 그대로 반환합니다. 준비 단계에서 보관했던 frame 기준과 같은 GPR15 값을 전달합니다. 이 C 파일만으로 assembly가 callback의 반환 register와 수정된 pt_regs를 어떤 순서로 적용하는지까지 확인한 것으로 계산하지 않습니다.'),
        ('수명과 호출 전제', '세 함수 모두 NOKPROBE_SYMBOL 대상이고 trampoline도 동일하게 제외됩니다. 이 함수들에는 NULL 확인, node pool 수명 관리, 반환 주소 유효성 검사나 잠금이 없습니다. 공통 계층 및 호출 문맥이 마련한 유효한 인자를 사용하는 어댑터입니다.'),
        ('CS 연결과 검증 범위', '호출 규약별 register 번호의 의미, 원래 값 저장 후 치환, 포인터 인자를 통한 부수효과와 별도 반환값의 차이, 계측 대상에서 내부 구현을 제외하는 재진입 경계를 학습합니다. 전체 C 파일 대조는 s390의 PSW 전환과 assembly 복귀 경로까지 실행 검증한 것은 아닙니다.')
    ],
    questions=[
        ('원래 반환 주소와 frame에 대응하는 슬롯은?', '각각 gprs[14]와 gprs[15]이다', '각각 gprs[15]와 gprs[14]이다', 'prepare의 두 저장문과 callback의 frame 인자를 함께 확인하면 두 역할을 구분할 수 있습니다.'),
        ('fixup은 실제 복귀 주소를 어디에 쓰는가?', 'regs->gprs[14]에 쓴다', 'rh->frame만 수정한다', 'fixup에는 node 인자가 없고 correct_ret_addr를 반환 register snapshot에 대입합니다.'),
        ('이 C 파일의 callback이 PSW를 직접 변경하는가?', '아니다. 공통 handler를 호출하고 결과를 반환한다', '그렇다. PSW 주소 필드를 직접 덮어쓴다', '본문에는 PSW 접근이 없습니다. 아키텍처의 일반적 지식을 해당 파일에 없는 동작으로 덧붙이지 않습니다.')
    ]
), dict(
    path='arch/s390/kernel/rethook.h',
    title='s390 rethook 로컬 헤더: 단일 callback 선언',
    intro='한 개의 외부 함수 선언과 guard로 이루어진 로컬 헤더를 전체 해설합니다.',
    principle='작은 헤더의 선언 범위와 실행 구현의 범위를 구분합니다.',
    use='assembly가 부르는 callback의 타입 계약과 포함 문맥을 확인합니다.',
    area='헤더 guard · 함수 시그니처 · 타입 의존성',
    sections=[
        ('전체 내용', 'GPL-2.0-only, __S390_RETHOOK_H guard와 arch_rethook_trampoline_callback 선언 하나뿐입니다. include, 변수, inline 함수, prepare/fixup의 별도 선언은 이 파일에 없습니다. 관련 C 파일과 license 표기가 다르므로 저장소 전체의 표기를 임의로 통일하지 않습니다.'),
        ('타입 계약', 'callback은 struct pt_regs 포인터를 받고 unsigned long을 반환합니다. pt_regs의 필드 정의를 이 헤더가 제공하는 것은 아니며 필요한 타입 문맥은 포함 경로에서 준비해야 합니다. 반환형을 void로 이해하면 C 구현이 공통 handler의 결과를 전달하는 계약을 놓칩니다.'),
        ('CS 연결과 범위', 'guard는 같은 번역 단위의 반복 포함을 막는 장치입니다. 함수가 실행되거나 반환 주소를 바꾸는 동작은 선언 자체에 없습니다. 이 파일을 완료했다는 것은 단일 인터페이스 전체를 설명했다는 뜻이며 다른 assembly 파일의 동작 완료를 의미하지 않습니다.')
    ],
    questions=[
        ('이 헤더에 선언된 callback의 반환형은?', 'unsigned long이다', 'void이다', '정의와 선언의 타입이 일치해야 합니다. 공통 handler 결과를 돌려주는 C 함수와 연결됩니다.'),
        ('이 파일만으로 pt_regs의 GPR 배열 배치를 알 수 있는가?', '아니다. 구조체 정의는 다른 곳에 있다', '그렇다. 포인터 인자 선언에 전체 레이아웃이 포함된다', '구조체 포인터를 함수 인자로 쓰는 선언과 필드 배치를 정의하는 구조체 본문은 다릅니다.')
    ]
)]
