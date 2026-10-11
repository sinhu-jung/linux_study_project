"""Whole-file RISC-V instruction-cache, sigreturn, and hwprobe stubs."""
ROWS = [dict(
    path='arch/riscv/kernel/vdso/flush_icache.S',
    title='RISC-V 명령 캐시 동기화: SMP syscall과 단일 CPU fence.i',
    intro='설정별 명령열과 공통 반환·CFI를 전체 분석합니다.',
    principle='명령어 스트림의 동기화는 데이터 메모리 접근과 다르며, 여러 CPU의 실행 문맥을 다룰 때 커널의 관리가 필요할 수 있습니다.',
    use='CONFIG_SMP에 따른 빌드 분기와 실제 레지스터 쓰기 범위를 설명합니다.',
    area='명령 캐시 · self-modifying code · SMP · fence.i · syscall · CFI',
    sections=[
        ('전체 인터페이스', 'GPL-2.0-only 표기 뒤 linux/linkage.h와 asm/unistd.h를 포함하고 .text에 __vdso_flush_icache 심볼을 정의합니다. 주석의 원형은 int 함수이며 start·end 포인터와 unsigned long flags를 받습니다. SYM_FUNC_START/END와 활성 .cfi_startproc/.cfi_endproc가 범위를 감쌉니다.'),
        ('SMP 빌드의 경로', 'CONFIG_SMP이면 a7에 __NR_riscv_flush_icache를 넣고 ecall합니다. 함수는 start·end·flags 인수를 별도 복사하거나 파싱하지 않고 전달받은 호출 문맥을 사용합니다. syscall 결과를 0으로 덮지 않고 뒤 ret로 반환합니다. 원격 CPU 처리 정책 자체는 이 짧은 파일에 구현되어 있지 않습니다.'),
        ('비SMP 경로', 'else에서는 fence.i를 실행하고 li a0,0으로 성공 결과를 설정합니다. start·end·flags를 읽어 범위를 순회하거나 검증하는 명령이 없습니다. 따라서 이 분기가 요청한 주소 구간만 하나씩 flush하는 구현이라고 설명하면 안 됩니다. fence.i는 명령어 fetch와 관련한 동기화이며 단순한 C 컴파일러 memory clobber와 다릅니다.'),
        ('빌드 선택과 공통 반환', '#ifdef CONFIG_SMP는 빌드 시 두 명령열 중 하나를 선택합니다. 매 호출마다 실제 온라인 CPU 수를 세어 분기를 고르는 코드가 아닙니다. 두 경로 뒤 공통 ret가 있고 CFI를 닫습니다. syscall 경로의 오류 처리와 직접 경로의 0 반환을 구분해야 합니다.'),
        ('CS 연결과 검증 범위', '전체 명령과 전처리·CFI·심볼 범위를 설명했습니다. 생성·수정한 코드를 실행할 때의 명령 가시성, 로컬 명령과 OS 관리의 차이가 핵심입니다. 실제 RISC-V 코드 수정 실행, 다중 CPU 캐시 동기화, syscall flags 검증을 재현한 시험은 하지 않았습니다.')
    ],
    questions=[
        ('CONFIG_SMP가 꺼진 경로에서 실행하는 핵심 명령은?', 'fence.i이며 이어 a0=0을 설정한다', '항상 __NR_riscv_flush_icache의 ecall이다', '원본의 else는 직접 명령 동기화와 성공값 설정입니다. SMP 경로만 syscall 번호를 a7에 넣습니다.'),
        ('현재 온라인 CPU가 하나면 SMP 빌드도 자동으로 직접 fence.i 경로로 바뀌는가?', '아니다. 선택은 CONFIG_SMP 전처리 조건이다', '그렇다. 함수가 매번 온라인 CPU 수를 검사한다', '파일에는 런타임 CPU 수 검사 명령이 없습니다. 빌드 설정과 실행 중 상태를 구분해야 합니다.'),
        ('비SMP 경로가 start부터 end까지 주소를 순회하는가?', '아니다. 두 포인터를 읽는 명령이나 반복문이 없다', '그렇다. fence.i가 C 인수의 start/end를 자동 해석한다', '명령열은 fence.i, 성공값 설정, ret입니다. 함수 인수의 존재가 본문에서 범위별 처리를 한다는 증거는 아닙니다.')
    ]
), dict(
    path='arch/riscv/kernel/vdso/rt_sigreturn.S',
    title='RISC-V 시그널 복귀: signal-frame CFI와 ecall',
    intro='시그널 복귀 진입점의 두 명령과 활성 unwind 메타데이터를 분석합니다.',
    principle='시그널에서 중단 문맥으로 돌아오는 과정은 일반 함수의 ret와 다른 시스템 호출 계약을 사용합니다.',
    use='CFI 지시문과 CPU 실행 명령을 구분하고 파일에 없는 반환 명령을 가정하지 않습니다.',
    area='시그널 · syscall · 중단 문맥 · DWARF CFI · 함수 경계',
    sections=[
        ('파일 전체', 'GPL-2.0-only와 저작권 뒤 linux/linkage.h·asm/unistd.h를 포함하고 .text에서 SYM_FUNC_START(__vdso_rt_sigreturn)를 사용합니다. 별도 인수 가공·조건부 설정·fallback 함수는 없습니다.'),
        ('활성 signal-frame 정보', '.cfi_startproc와 .cfi_signal_frame은 실제 지시문이며 주석 처리되어 있지 않습니다. signal-frame 표시는 unwinder용 정보로, 직접 레지스터를 복원하는 CPU 명령이 아닙니다. ARM64 시그널 복귀 파일의 비활성 CFI를 이 파일에도 그대로 적용하면 안 됩니다.'),
        ('실제 복귀 경로', 'li a7,__NR_rt_sigreturn과 ecall을 실행한 뒤 .cfi_endproc, SYM_FUNC_END로 끝납니다. 일반 syscall stub와 달리 이 파일에는 ret가 없습니다. 정상적인 rt_sigreturn의 목적은 커널에서 시그널 프레임을 처리하고 중단 문맥으로 복귀하는 것이므로 일반 함수 반환과 구별해야 합니다. 잘못된 프레임의 처리 전체는 별도 커널 구현 범위입니다.'),
        ('범위와 CS 연결', '전체 심볼·CFI·명령을 분석했습니다. 메타데이터와 실행 동작, 정상 함수 호출과 비동기 시그널 문맥 복원의 차이가 핵심입니다. 실제 시그널 전달·복귀나 unwinder 동작을 실행 검증한 결과는 아닙니다.')
    ],
    questions=[
        ('이 rt_sigreturn stub는 ecall 뒤에 ret 명령이 있는가?', '없다', '있다. 모든 vDSO 어셈블리 함수는 ret로 끝나야 한다', '원본은 ecall 뒤 CFI와 심볼을 닫습니다. 시그널 복귀의 제어 흐름을 일반 함수 반환 규칙으로 추정하지 않습니다.'),
        ('.cfi_signal_frame이 실제로 레지스터를 복원하는 명령인가?', '아니다. unwinder가 사용할 frame 메타데이터 지시문이다', '그렇다. 그 한 줄이 모든 저장 레지스터를 복원한다', '실행 명령은 li와 ecall입니다. CFI 정보 생성과 커널의 시그널 문맥 복원은 다른 역할입니다.')
    ]
), dict(
    path='arch/riscv/kernel/vdso/sys_hwprobe.S',
    title='RISC-V hwprobe syscall stub: 얇은 전달 계층',
    intro='하드웨어 정보 조회 syscall 연결 함수의 전체 명령열을 분석합니다.',
    principle='하드웨어 정보를 조회하는 이름의 함수라도 실제 탐지 알고리즘 대신 커널 호출 연결만 담당할 수 있습니다.',
    use='심볼 이름과 syscall 번호, 결과 전달과 별도 검증의 차이를 설명합니다.',
    area='RISC-V syscall ABI · stub · 하드웨어 조회 · CFI',
    sections=[
        ('전체 파일과 심볼', 'GPL-2.0과 Rivos 저작권 뒤 linux/linkage.h·asm/unistd.h를 포함합니다. .text에서 SYM_FUNC_START(riscv_hwprobe)를 사용합니다. 이 파일의 심볼은 __vdso_hwprobe가 아니라 riscv_hwprobe입니다. 공개 동적 ABI 여부는 링크 규칙과 호출부도 함께 확인해야 합니다.'),
        ('실행 명령과 전달', '활성 .cfi_startproc 안에서 a7에 __NR_riscv_hwprobe를 넣고 ecall, ret를 수행합니다. 입력 인수 레지스터를 재배치하거나 결과를 검사·변환하는 본문이 없습니다. 실제 하드웨어 feature 열거와 사용자 입력 검증은 syscall 처리에 위임합니다.'),
        ('메타데이터와 범위', '.cfi_endproc와 SYM_FUNC_END가 끝을 표시합니다. 별도 오류 문자열·fallback 분기·CPU 명령 feature 검출은 없습니다. 전체 짧은 stub를 분석했으며 이 파일만으로 hwprobe.c의 빠른 처리 알고리즘이나 syscall의 모든 조회 키를 완료 집계하지 않습니다.')
    ],
    questions=[
        ('sys_hwprobe.S가 정의하는 함수 이름은?', 'riscv_hwprobe이다', '__vdso_hwprobe이다', '파일 이름이나 관련 인터페이스 이름으로 추정하지 않고 SYM_FUNC_START의 인수를 확인해야 합니다.'),
        ('이 stub가 하드웨어 feature를 직접 순회하여 판단하는가?', '아니다. syscall 번호를 설정하고 ecall한다', '그렇다. CSR를 전부 읽어 feature 테이블을 만든다', '본문은 li, ecall, ret입니다. 정보 조회의 실제 알고리즘과 호출 연결 계층을 구별합니다.')
    ]
)]
