"""Whole-file ARM64 sigreturn trampoline and vDSO address helpers."""
ROWS = [dict(
    path='arch/arm64/kernel/vdso/sigreturn.S',
    title='ARM64 sigreturn trampoline: 명령 패턴과 unwinder 호환성',
    intro='두 실제 복귀 명령, 앞의 NOP, 비활성 CFI 지시문과 심볼 매크로 선택을 분석합니다.',
    principle='짧은 어셈블리도 외부 도구가 명령 패턴을 인식하는 ABI 계약을 가질 수 있습니다.',
    use='주석 처리된 메타데이터와 실제 실행 코드를 구별하고 시그널 복귀를 일반 함수 반환과 구분합니다.',
    area='시그널 · 시스템 호출 · ARM64 ABI · DWARF · stack unwinding · BTI · 호환성',
    sections=[
        ('파일 전체와 목적', 'GPL-2.0-only 주석은 SA_RESTORER가 설정되지 않은 경우 시그널에서 돌아오기 위한 trampoline이라고 설명합니다. linux/linkage.h, asm/assembler.h, asm/unistd.h를 포함하고 .text로 이동합니다. 이 파일 자체가 시그널 전달 여부나 SA_RESTORER를 검사하는 분기를 실행하는 것은 아닙니다.'),
        ('CFI는 실제로 비활성이다', '.cfi_startproc, .cfi_signal_frame, .cfi_def_cfa x29,0, x29·x30의 .cfi_offset, .cfi_endproc는 모두 //로 주석 처리되어 있습니다. 이름이 소스에 등장한다고 실제 unwind 정보가 생성된다고 읽어서는 안 됩니다. 주석은 SIGCANCEL handler에서 pthread cleanup을 호출하려고 unwind할 때 libgcc의 segfault를 유발했던 이유를 설명합니다.'),
        ('주석 속 CFI의 의도와 한계', '.cfi_signal_frame의 의도는 .eh_frame의 FDE를 signal frame으로 표시하여 _Unwind_GetIPInfo 사용자가 반환 주소에서 1을 빼지 않게 하는 것입니다. x29와 x30 위치만 제공하는 정보는 stack pointer 등 다른 레지스터 복원에 불충분할 수 있다고 주석이 경고합니다. 현재는 이 지시문들을 생략하여 unwinder의 ARM64 signal-frame fallback이 sigcontext에서 레지스터를 복원하도록 유도한다는 설명입니다.'),
        ('심볼 앞의 NOP', '실제 nop 명령은 __kernel_rt_sigreturn 시작 매크로보다 앞에 있습니다. 주석은 일부 unwinder가 _Unwind_GetIP 결과에서 무조건 1을 빼 호출 함수를 찾기 때문에 이 NOP가 필요하다고 설명합니다. 이를 시간 지연이나 스레드 동기화 목적의 명령이라고 해석하지 않습니다. 명령 위치 자체가 도구 호환성과 연결됩니다.'),
        ('SYM_CODE_START 선택', 'SYM_CODE_START(__kernel_rt_sigreturn)를 사용하고 SYM_FUNC_START를 사용하지 않습니다. 주석에 따르면 후자는 BTI C를 내보내 GDB·libgcc·libunwind가 기대하는 sigreturn 명령 패턴을 깨뜨릴 수 있습니다. 이 함수는 RET를 통해서만 진입하므로 해당 landing pad 생략이 허용된다는 문맥도 명시합니다. 이를 모든 함수에서 BTI를 제거해도 된다는 일반 규칙으로 확대하지 않습니다.'),
        ('실제 복귀 명령 두 개', '본문은 mov x8, #__NR_rt_sigreturn으로 syscall 번호를 준비하고 svc #0으로 커널에 진입합니다. 시그널 프레임의 레지스터를 여기서 직접 하나씩 pop하거나 일반 ret로 끝내는 구현이 아닙니다. 세 PLEASE DO NOT MODIFY 줄은 주석이며 명령이 아닙니다. SYM_CODE_END가 심볼 범위를 닫습니다.'),
        ('끝의 feature 매크로', '마지막에 emit_aarch64_feature_1_and를 호출합니다. 이 파일에는 매크로 내부 구현이 없으며 포함된 어셈블러 정의에 의존합니다. 이 호출을 앞의 sigreturn 명령열에 BTI C를 추가하는 SYM_FUNC_START와 혼동하지 않습니다. 관련 vDSO 링커 스크립트는 .note.gnu.property를 버리므로 오브젝트 단계 메타데이터와 최종 이미지 정책도 구분해야 합니다.'),
        ('CS 연결과 범위', '모든 활성 명령·매크로와 비활성 CFI, 호환성 주석을 다뤘습니다. ABI에는 함수 인수뿐 아니라 디버거와 unwinder의 명령 패턴 인식도 영향을 줄 수 있습니다. 원본 분석이며 실제 signal handler 복귀나 C++ 취소 unwind, BTI 하드웨어 실행을 검증한 결과는 아닙니다.')
    ],
    questions=[
        ('이 파일의 .cfi_signal_frame은 현재 활성 지시문인가?', '아니다. //로 주석 처리되어 있다', '그렇다. 주석의 설명만으로 FDE가 생성된다', '실행·어셈블되는 코드와 설명을 구별해야 합니다. 주석은 지시문의 의도와 비활성 이유를 설명하지만 메타데이터를 생성하지 않습니다.'),
        ('__kernel_rt_sigreturn의 실제 복귀 방식은?', 'x8에 syscall 번호를 넣고 svc #0을 실행한다', '여기서 모든 레지스터를 직접 복원한 뒤 ret한다', '본문은 mov와 svc 두 명령입니다. 시그널 문맥 복원은 rt_sigreturn 시스템 호출 처리와 연결됩니다.'),
        ('SYM_FUNC_START 대신 SYM_CODE_START를 사용하는 이유는?', '추가 BTI C가 unwinder의 sigreturn 패턴 인식을 깨뜨리지 않도록 하기 위해서다', '함수를 사용자 공간에서 절대 실행할 수 없게 하기 위해서다', '주석은 도구의 명령열 인식과 RET 진입 문맥을 설명합니다. 단순한 성능 최적화나 실행 금지 표시가 아닙니다.'),
        ('앞의 NOP를 지워도 아무 영향이 없다고 판단할 수 있는가?', '아니다. 반환 주소에서 1을 빼는 일부 unwinder와의 호환 목적이 있다', '그렇다. NOP는 어느 위치에서나 의미 없이 삭제 가능하다', '명령이 레지스터를 바꾸지 않는 것과 바이너리 배치가 외부 도구에 영향을 주지 않는 것은 다릅니다. 이 파일의 주석은 그 위치의 이유를 명시합니다.')
    ]
), dict(
    path='arch/arm64/include/asm/vdso.h',
    title='ARM64 vDSO 주소 계산: 링크 기준과 실행 시 매핑 기준',
    intro='링크 기준 주소, vvar 페이지 수, 생성된 offset을 사용하는 심볼 주소 매크로를 분석합니다.',
    principle='위치가 바뀌는 공유 코드의 심볼 주소는 링크 시 오프셋과 실행 시 매핑 기준 주소를 합쳐 구할 수 있습니다.',
    use='VDSO_SYMBOL의 토큰 결합과 주소 산술을 해석하고 이미지 경계 선언을 구별합니다.',
    area='주소 재배치 · ASLR · 전처리 토큰 결합 · GNU C statement expression · 외부 배열 선언',
    sections=[
        ('전체 상수와 가시성', 'GPL-2.0-only include guard 아래 VDSO_LBASE=0x0, __VVAR_PAGES=2를 정의합니다. 주석은 vDSO 매핑 위치를 무작위화하므로 사전 링크 주소를 정하려는 실익이 적다고 설명합니다. 이 두 상수는 !__ASSEMBLY__ 구역보다 앞이어서 assembly 문맥에서도 보입니다. 이 파일 자체가 난수 주소를 선택하거나 페이지를 매핑하지 않습니다.'),
        ('생성 헤더와 이름 결합', 'C 구역에서는 generated/vdso-offsets.h를 포함합니다. VDSO_SYMBOL(base,name)은 vdso_offset_##name으로 생성된 offset 심볼 이름을 만듭니다. name은 런타임 문자열 검색 인수가 아니라 전처리 토큰으로 쓰입니다. 생성 헤더가 있어야 각 이름의 offset 정의를 사용할 수 있습니다.'),
        ('주소 식과 예시', '매크로는 GNU C statement expression ({ ... }) 안에서 (void *)(vdso_offset_name - VDSO_LBASE + (unsigned long)base)를 계산합니다. base가 0x70000000이고 offset이 0x120이면 현재 LBASE=0 조건에서 0x70000120입니다. 여기서 메모리를 역참조하거나 함수 호출을 실행하지 않습니다. base 식은 매크로 본문에서 한 번만 나타납니다.'),
        ('이미지 경계의 선언', 'extern char vdso_start[], vdso_end[], vdso32_start[], vdso32_end[]는 native와 compat 이미지 경계 심볼의 외부 배열 선언입니다. 배열 크기나 이미지 내용을 여기서 정의하지 않으며 메모리를 할당하지도 않습니다. 선언이 있다는 사실만으로 모든 빌드에서 모든 심볼 정의가 사용된다고 단정하지 않습니다.'),
        ('CS 연결과 범위', '전체 상수·매크로·선언·조건부 포함을 설명했습니다. 링크 기준과 실행 기준의 차이, 주소 산술과 역참조의 차이, 생성 파일 의존성이 핵심입니다. 매크로에는 이름 존재·범위·NULL 검사가 없으므로 올바른 이미지와 생성 offset을 사용하는 것은 호출 문맥의 책임입니다. 실제 무작위 매핑 실행 검증을 수행한 것은 아닙니다.')
    ],
    questions=[
        ('현재 LBASE=0, base=0x70000000, offset=0x120일 때 VDSO_SYMBOL 결과는?', '주소 0x70000120이다', '주소 0x120을 역참조한 메모리 값이다', '매크로는 실행 시 기준 주소에 offset을 더해 void *를 만듭니다. 주소 계산과 해당 주소에서 값을 읽는 연산은 다릅니다.'),
        ('VDSO_SYMBOL의 name은 런타임 함수 이름 문자열인가?', '아니다. vdso_offset_과 결합할 전처리 토큰이다', '그렇다. 매 호출마다 ELF 문자열표를 검색한다', '## 연산이 식별자를 만듭니다. 이 매크로에는 문자열 비교나 심볼 검색 루프가 없습니다.'),
        ('__VVAR_PAGES=2 선언이 실제로 두 페이지를 할당하는가?', '아니다. 레이아웃에 사용할 페이지 수 상수이다', '그렇다. 헤더를 포함할 때마다 두 페이지가 할당된다', '전처리 상수 정의는 실행 시 메모리 할당이 아닙니다. 실제 매핑과 수명은 다른 구현에서 관리합니다.')
    ]
)]
