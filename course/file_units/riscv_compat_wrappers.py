"""Whole-file compat source wrappers, with individual roles and questions."""
ROWS = [dict(
    path='arch/riscv/kernel/compat_vdso/compat_vdso.S',
    title='Compat 이미지 포함: 경계 심볼과 입력 ELF 경로 교체',
    intro='세 매크로와 공통 어셈블리 포함 전체를 분석합니다.',
    principle='소스 재사용 전에 식별자와 입력 경로를 재정의하면 별도 이미지 객체를 만들 수 있습니다.',
    use='이미지 경계 심볼과 이미지 내부 함수 이름을 구별합니다.',
    area='전처리 · 심볼 이름 · incbin · 소스 재사용',
    sections=[
        ('전체 매크로', 'GPL-2.0-only 뒤 vdso_start를 compat_vdso_start, vdso_end를 compat_vdso_end로 정의합니다. __VDSO_PATH는 arch/riscv/kernel/compat_vdso/compat_vdso.so 문자열입니다. 이어 ../vdso/vdso.S를 포함합니다. 이 파일에 다른 함수나 실행 명령은 없습니다.'),
        ('포함 결과의 의미', '공통 vdso.S가 페이지 정렬·globl·시작과 끝 라벨·incbin을 제공하므로 여기서는 compat 이름의 경계와 compat ELF를 포함하는 객체가 됩니다. 미리 정의한 __VDSO_PATH가 공통 파일의 #ifndef 기본값을 막습니다. 내부 ELF 함수 이름을 모두 compat로 바꾸는 매크로는 아닙니다.'),
        ('범위', '시작·끝 경계는 포함된 바이너리 영역을 가리키며 페이지 padding을 포함할 수 있습니다. 실제 사용자 주소 매핑은 이 wrapper의 책임이 아닙니다. 전체 소스를 대조했으며 포함 대상은 이미 별도 학습으로 다룬 범위이고 여기서 중복 완료 집계하지 않습니다.')
    ],
    questions=[
        ('이 wrapper가 바꾸는 경계 심볼은?', 'vdso_start/end를 compat_vdso_start/end로 바꾼다', '모든 __vdso 함수에 자동으로 compat를 붙인다', '매크로는 명시된 두 식별자에만 적용됩니다. 포함 바이너리 내부의 모든 심볼을 재작성하는 도구가 아닙니다.'),
        ('공통 파일의 기본 vdso.so 대신 compat 이미지를 사용하는 이유는?', 'include 전에 __VDSO_PATH를 정의하기 때문이다', '파일 이름에 compat가 있으면 assembler가 자동으로 경로를 바꾸기 때문이다', '공통 파일의 #ifndef와 사전 정의가 함께 입력 경로를 선택합니다.')
    ]
), dict(
    path='arch/riscv/kernel/compat_vdso/compat_vdso.lds.S',
    title='Compat 링커 스크립트 wrapper: 공통 배치와 빌드 정의',
    intro='단일 include가 실제 링크 규칙을 가져오는 구조를 분석합니다.',
    principle='같은 링커 스크립트라도 외부 전처리 매크로와 링크 모드에 따라 다른 ABI 이미지를 만들 수 있습니다.',
    use='파일 내부 정의와 Makefile에서 공급하는 조건을 구별합니다.',
    area='링커 스크립트 · 조건부 컴파일 · ABI 재사용',
    sections=[
        ('파일 전체', 'GPL-2.0-only 표기와 #include "../vdso/vdso.lds.S" 한 줄이 전부입니다. 여기서 OUTPUT_ARCH·SECTIONS·PHDRS를 새로 작성하지 않고 공통 파일의 내용을 사용합니다.'),
        ('Compat 조건의 출처', '이 wrapper 자체에는 #define COMPAT_VDSO가 없습니다. 확인한 compat Makefile이 -DCOMPAT_VDSO를 전처리 옵션으로 공급하므로 공통 VERSION의 hwprobe 공개 항목이 제외됩니다. 32비트 ELF 링크 모드도 Makefile의 -melf32lriscv에서 제공됩니다. include 한 줄만 보고 빌드 문맥을 생략하면 안 됩니다.'),
        ('전체 범위', '공통 파일의 주소·섹션·권한 규칙을 재사용하는 연결 파일입니다. 파일 내용이 짧아도 포함 대상과 빌드 옵션의 조합이 역할을 결정합니다. 실제 compat ELF 링크 검증은 수행하지 않았습니다.')
    ],
    questions=[
        ('COMPAT_VDSO는 이 wrapper 안에서 직접 정의되는가?', '아니다. compat Makefile의 전처리 옵션이 공급한다', '그렇다. include 지시문이 자동으로 해당 매크로를 만든다', '원본에는 SPDX와 include뿐입니다. 실제 설정의 출처를 구분해야 합니다.'),
        ('이 파일은 독립된 섹션 배치 규칙을 복사해 갖고 있는가?', '아니다. 공통 vdso.lds.S를 포함한다', '그렇다. 전체 규칙을 별도로 하드코딩한다', '코드 중복 대신 전처리 포함으로 같은 소스를 재사용합니다.')
    ]
), dict(
    path='arch/riscv/kernel/compat_vdso/getcpu.S',
    title='Compat getcpu: 공통 syscall 진입점 재사용',
    intro='단일 어셈블리 include의 역할을 분석합니다.',
    principle='호환 ABI용 객체는 소스 복사 없이 다른 컴파일 옵션으로 같은 명령열을 사용할 수 있습니다.',
    use='소스 이름과 실제 함수 심볼을 구별합니다.',
    area='소스 재사용 · syscall · ABI · 빌드 옵션',
    sections=[
        ('전체 내용', 'GPL-2.0-only와 #include "../vdso/getcpu.S"만 있습니다. 함수 이름을 바꾸는 매크로나 추가 CPU 탐지 코드는 없습니다.'),
        ('포함되는 동작', '공통 파일은 __vdso_getcpu 심볼, CFI, a7에 __NR_getcpu 설정, ecall, ret를 제공합니다. 이 wrapper가 별도 __compat_vdso_getcpu 본문을 정의하는 것은 아닙니다. compat Makefile의 RV32·ilp32 옵션 아래 별도 객체로 빌드됩니다.'),
        ('범위', '출력 포인터 처리와 CPU 조회는 syscall에 위임됩니다. 단순 include를 분석했다고 커널 getcpu 구현 전체를 완료 처리하지 않습니다. 실제 32비트 호출 실행 검증은 수행하지 않았습니다.')
    ],
    questions=[
        ('이 wrapper가 함수 이름을 __compat_vdso_getcpu로 바꾸는가?', '아니다. 이름 재정의 없이 공통 소스를 포함한다', '그렇다. 디렉터리 이름만으로 심볼이 바뀐다', '전처리 매크로나 별도 정의가 없으므로 경로 이름만으로 함수 이름을 추정하면 안 됩니다.'),
        ('가져오는 공통 getcpu의 핵심 처리 방식은?', 'ecall로 getcpu syscall을 호출한다', 'CPU 번호를 CSR에서 직접 읽어 항상 0을 반환한다', '공통 어셈블리의 실제 명령열과 연결해 읽어야 합니다.')
    ]
), dict(
    path='arch/riscv/kernel/compat_vdso/flush_icache.S',
    title='Compat 명령 캐시 flush: 공통 SMP 분기의 재사용',
    intro='공통 flush_icache 어셈블리에 연결하는 파일 전체를 분석합니다.',
    principle='소스를 공유하면 조건부 동작도 공유되며, 호환 ABI라는 이유로 별도 알고리즘이 자동 추가되지는 않습니다.',
    use='CONFIG_SMP 조건의 위치와 역할을 파악합니다.',
    area='명령 캐시 · 전처리 · SMP · 코드 공유',
    sections=[
        ('전체 내용', 'GPL-2.0-only 뒤 ../vdso/flush_icache.S를 include합니다. 이 파일에는 별도의 매크로 정의나 명령열이 없습니다.'),
        ('공통 분기', '포함된 소스는 CONFIG_SMP이면 riscv_flush_icache syscall, 아니면 fence.i와 a0=0을 수행하고 ret합니다. 조건과 구현은 공통 파일에 있으며 이 wrapper가 매번 CPU 수를 검사하는 코드를 추가하지 않습니다.'),
        ('범위', '호환 빌드가 같은 동작 소스를 별도 ISA·ABI 옵션으로 조립하도록 연결합니다. 실제 원격 CPU 동기화나 주소 범위 검증은 이 wrapper에서 구현하지 않습니다. 전체 파일은 include 연결로 설명되며 실제 실행 시험은 하지 않았습니다.')
    ],
    questions=[
        ('SMP 여부에 따른 분기는 어디에 있는가?', '포함되는 공통 flush_icache.S에 있다', '이 wrapper에 독립적인 runtime CPU 수 루프가 있다', 'wrapper는 include 한 줄입니다. 실제 조건부 명령열은 포함 대상에서 제공됩니다.'),
        ('비SMP 공통 경로는 무엇을 수행하는가?', 'fence.i 후 a0을 0으로 설정한다', '항상 ecall만 한다', '소스 재사용은 공통 파일의 설정별 분기도 그대로 가져옵니다.')
    ]
), dict(
    path='arch/riscv/kernel/compat_vdso/rt_sigreturn.S',
    title='Compat 시그널 복귀: 공통 trampoline 연결',
    intro='시그널 복귀 소스 재사용 파일 전체를 분석합니다.',
    principle='호환 빌드의 진입점도 실제 제어 흐름은 포함된 어셈블리와 커널 ABI 계약을 따라야 합니다.',
    use='signal-frame CFI와 ret 부재를 구분합니다.',
    area='시그널 · CFI · syscall · 소스 포함',
    sections=[
        ('전체 내용', 'GPL-2.0-only 표기 뒤 ../vdso/rt_sigreturn.S를 include합니다. 별도 심볼 이름 치환이나 직접적인 시그널 프레임 해석은 없습니다.'),
        ('가져오는 동작', '공통 __vdso_rt_sigreturn은 활성 .cfi_signal_frame을 두고 a7에 __NR_rt_sigreturn을 넣어 ecall합니다. 일반 함수 반환용 ret는 그 본문에 없습니다. wrapper가 ret를 뒤에 추가하는 것도 아닙니다.'),
        ('범위', '호환 ABI의 실제 시그널 프레임 처리는 커널 syscall 구현과 빌드 문맥에 속합니다. 이 파일은 그 진입점 소스를 재사용하며 자체 복원 알고리즘을 갖지 않습니다. 실제 compat signal 실행 검증은 수행하지 않았습니다.')
    ],
    questions=[
        ('이 wrapper가 공통 ecall 뒤에 ret를 추가하는가?', '아니다. 별도 명령 없이 공통 파일만 포함한다', '그렇다. 모든 compat 함수는 자동으로 ret가 붙는다', '전처리 include는 임의의 반환 명령을 자동 추가하지 않습니다.'),
        ('이 파일에서 시그널 프레임의 모든 레지스터를 직접 복원하는가?', '아니다. 공통 syscall 진입점에 연결한다', '그렇다. include가 프레임 복원을 수행하는 CPU 명령이다', '소스 포함과 실제 runtime 동작을 구분해야 합니다. 복귀는 syscall 계약을 따릅니다.')
    ]
), dict(
    path='arch/riscv/kernel/compat_vdso/note.S',
    title='Compat ELF note: 공통 Linux 버전 메타데이터 포함',
    intro='공통 note 소스를 사용하는 짧은 파일 전체를 분석합니다.',
    principle='메타데이터 생성 소스도 여러 ABI 빌드에서 재사용할 수 있습니다.',
    use='포함한 note 내용과 wrapper 자체의 내용을 구분합니다.',
    area='ELF note · 메타데이터 · 전처리 재사용',
    sections=[
        ('전체 파일', 'wrapper에는 GPL-2.0-only 표기와 ../vdso/note.S include만 있습니다. 포함 대상에는 별도의 GPL-2.0-or-later 표기가 있습니다. 파일별 원문 표기를 구별하며 법적 호환성 판단을 이 기술 설명으로 대신하지 않습니다.'),
        ('버전 note', '공통 note는 Linux 이름, type 0, .long LINUX_VERSION_CODE description을 생성합니다. 이 wrapper가 type 번호를 바꾸거나 build salt를 추가하는 구문은 없습니다. 실행 함수가 아니라 ELF 메타데이터입니다.'),
        ('범위', 'note가 최종 PT_NOTE에 들어가는 배치는 공통 링커 스크립트와 빌드 결과를 함께 봐야 합니다. 전체 include 역할을 설명했으며 실제 compat ELF의 note 추출 검증은 수행하지 않았습니다.')
    ],
    questions=[
        ('이 wrapper가 공통 note에 추가하는 별도 build salt가 있는가?', '없다', '있다. compat 전용 난수를 생성한다', '원본은 include만 있으며 포함되는 RISC-V note도 버전 note 하나를 명시합니다.'),
        ('가져오는 Linux note의 description은?', 'LINUX_VERSION_CODE의 정수 값이다', '현재 실행 CPU 번호이다', '공통 note 소스의 .long 값을 그대로 재사용합니다. runtime CPU 조회 동작은 없습니다.')
    ]
)]
