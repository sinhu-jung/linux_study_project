"""Whole-file ARM64 compat time entry points and ELF link layout."""
ROWS = [dict(
    path='arch/arm64/kernel/vdso32/vgettimeofday.c',
    title='ARM64 compat vDSO 진입점: time32·time64와 unwind stub',
    intro='네 시간 조회 함수와 세 빈 ABI 함수의 선언·위임 관계를 분석합니다.',
    principle='32비트 사용자 ABI도 별도 시간64 진입점을 제공할 수 있으며, 함수의 존재와 실제 구현 책임을 구별해야 합니다.',
    use='자료형과 공통 함수 이름을 연결하고 빈 unwind 함수가 존재하는 빌드상의 이유를 이해합니다.',
    area='호환 ABI · time32/time64 · wrapper · 전처리 · 링킹',
    sections=[
        ('전체 구성과 선언 선택', 'GPL-2.0과 ARM64 compat userspace 주석 뒤 BUILD_VDSO32_64를 정의하고 vdso/gettime.h를 포함합니다. 이 매크로는 공통 헤더에서 old_timespec32 원형을 선택하는 조건에 참여합니다. 함수가 실행될 때 매번 ABI를 탐지하는 런타임 분기가 아닙니다. 관련 Makefile은 c-gettimeofday-y가 있을 때 -include로 공통 구현을 컴파일 문맥에 제공합니다.'),
        ('Time32 clock_gettime', '__vdso_clock_gettime(clockid_t clock, old_timespec32 *ts)는 __cvdso_clock_gettime32(clock, ts)의 int 결과를 반환합니다. 공개 함수 이름에 32가 없지만 출력은 구형 32비트 시간 구조체입니다. 이름만 보고 64비트 시간 범위를 보장한다고 해석하지 않습니다.'),
        ('Time64 clock_gettime', '__vdso_clock_gettime64는 같은 clockid_t와 __kernel_timespec *를 받고 __cvdso_clock_gettime으로 위임합니다. 공통 구현의 time64 함수 이름에는 64 접미사가 없습니다. 공개 진입점과 내부 helper 이름을 각각 확인해야 합니다. 32비트 사용자 공간의 포인터 폭과 시간 필드 폭은 별개입니다.'),
        ('Gettimeofday와 getres', '__vdso_gettimeofday는 __kernel_old_timeval *tv와 timezone *tz를 __cvdso_gettimeofday에 전달합니다. __vdso_clock_getres는 old_timespec32 *res를 __cvdso_clock_getres_time32로 전달합니다. 이 파일에는 별도의 __vdso_clock_getres64나 __vdso_time 본문은 없습니다. 네 wrapper 모두 결과를 직접 반환하며 별도 errno 설정이나 포인터 복사 루프를 갖지 않습니다.'),
        ('빈 unwind 함수 세 개', '__aeabi_unwind_cpp_pr0, __aeabi_unwind_cpp_pr1, __aeabi_unwind_cpp_pr2는 인수와 반환값이 없는 빈 함수입니다. 바로 앞 주석은 GCC가 내보내는 미해결 참조를 피하기 위한 것이라고 설명합니다. 이 함수들이 실제 예외 스택을 순회하거나 복원하는 알고리즘을 구현했다고 설명하면 안 됩니다.'),
        ('공개 함수와 링크 정책', '이 파일의 함수 정의만으로 모든 이름이 동적 공개 ABI가 되는 것은 아닙니다. 대응 vdso.lds.S는 네 __vdso 시간 함수만 global로 나열하고 나머지는 local로 처리합니다. 원본 전체의 역할은 ABI 진입점과 필요한 빈 심볼 제공이며, 공통 시간 계산·시계 모드 제한·fallback의 세부 구현은 별도 파일 범위입니다.')
    ],
    questions=[
        ('__vdso_clock_gettime64가 호출하는 공통 함수는?', '__cvdso_clock_gettime이다', '__cvdso_clock_gettime32이다', '__kernel_timespec을 사용하는 time64 진입점은 공통 기본 시간 함수를 호출합니다. 구형 old_timespec32 진입점이 32 접미사 helper를 호출합니다.'),
        ('__aeabi_unwind_cpp_pr0 등의 빈 함수가 이 파일에 있는 이유는?', 'GCC가 발생시키는 미해결 참조를 피하기 위해서다', 'C++ 예외의 완전한 스택 복원을 수행하기 위해서다', '주석의 목적은 링크 참조 해소입니다. 본문이 비어 있으므로 실제 unwind 알고리즘을 제공한다고 확대 해석해서는 안 됩니다.'),
        ('32비트 사용자 ABI에서는 time64 출력 구조체를 사용할 수 없는가?', '아니다. 별도 __vdso_clock_gettime64 진입점이 제공된다', '그렇다. 포인터 폭이 시간 필드의 폭을 항상 결정한다', '이 파일은 old_timespec32와 __kernel_timespec 진입점을 동시에 정의합니다. 주소 표현과 시간 데이터의 표현은 서로 다른 ABI 요소입니다.')
    ]
), dict(
    path='arch/arm64/kernel/vdso32/vdso.lds.S',
    title='ARM64 compat vDSO ELF 배치: 섹션·세그먼트·심볼 버전',
    intro='32비트 ARM ELF를 만드는 링커 스크립트의 데이터 주소, 섹션 목록, 권한, export를 전체 분석합니다.',
    principle='함수 구현을 바이너리 ABI로 제공하려면 주소 배치, 로드 권한, 공개 심볼의 범위를 별도로 정의해야 합니다.',
    use='ELF section과 program header의 차이, 공유 데이터의 상대 위치, 심볼 공개 제한을 설명합니다.',
    area='ELF · 링커 스크립트 · 메모리 권한 · 가상 주소 · 심볼 가시성 · 버전 ABI',
    sections=[
        ('전처리와 출력 아키텍처', 'GPL-2.0 표기 뒤 linux/const.h, asm/page.h, asm/vdso.h, asm-generic/vmlinux.lds.h를 포함합니다. OUTPUT_FORMAT은 elf32-littlearm, elf32-bigarm, elf32-littlearm 세 형식을 지정하고 OUTPUT_ARCH는 arm입니다. 디렉터리가 arm64라도 이 바이너리는 32비트 compat ARM용입니다. .S 스크립트의 매크로와 CONFIG_TIME_NS 분기는 전처리 문맥에서 해석됩니다.'),
        ('숨긴 데이터 주소와 본문 시작', 'SECTIONS 시작에서 PROVIDE_HIDDEN으로 _vdso_data = . - __VVAR_PAGES * PAGE_SIZE를 제공합니다. CONFIG_TIME_NS이면 _timens_data = _vdso_data + PAGE_SIZE도 제공합니다. 이어 위치 카운터를 VDSO_LBASE + SIZEOF_HEADERS로 설정합니다. 숨긴 주소 심볼 정의는 데이터 페이지 할당이나 초기화가 아니며, 코드 배치와 vvar 매핑 사이의 상대 위치 계약입니다.'),
        ('동적 검색과 버전 섹션', '.hash, .gnu.hash, .dynsym, .dynstr, .gnu.version, .gnu.version_d, .gnu.version_r를 각 동명 입력 섹션에서 수집합니다. .hash는 :text에 연결됩니다. 함수 이름 검색과 동적 심볼·버전 메타데이터를 담는 섹션이며 이들이 모두 C 함수 본문인 것은 아닙니다. 명시한 program header 연결은 뒤 PHDRS와 함께 읽어야 합니다.'),
        ('Note와 dynamic의 이중 소속', '.note는 .note.* 입력을 모아 :text와 :note에, .dynamic은 .dynamic 입력을 모아 :text와 :dynamic에 연결합니다. 같은 내용이 로드 세그먼트에 포함되면서 전용 ELF program header로도 설명되는 형태입니다. program header가 세 개라고 세 개의 별도 PT_LOAD가 생긴다는 뜻은 아닙니다.'),
        ('RoData 입력 목록', '.rodata는 .rodata*뿐 아니라 .got, .got.plt, .plt, .rel.iplt, .iplt, .igot.plt를 모아 :text에 둡니다. 출력 섹션 이름만으로 모든 입력이 일반 문자열 상수라고 판단하면 안 됩니다. 이 스크립트가 의도한 배치와 최종 바이너리에 실제 생기는 항목의 존재 여부는 구별해야 합니다.'),
        ('Text와 ARM 보조 코드', '.text는 .text*, .glue_7, .glue_7t, .vfp11_veneer, .v4_bx를 수집하고 :text에 연결하며 fill 값 0xe7f001f2를 지정합니다. ARM의 연결 보조 코드 섹션도 함께 배치합니다. fill 지정은 모든 명령을 해당 값으로 바꾸는 것이 아니라 출력 섹션에서 필요한 채움 패턴을 지정하는 문법입니다.'),
        ('재배치·unwind·디버그 메타데이터', '.rel.dyn은 .rel*를 수집하고 .ARM.exidx는 .ARM.exidx*를 수집합니다. 이어 DWARF_DEBUG와 ELF_DETAILS 매크로를 사용하며 .ARM.attributes는 주소 0으로 배치합니다. 디버그 매크로의 내부 구현 전체는 포함된 별도 파일에 있습니다. unwind 메타데이터가 있다는 사실만으로 앞 C 파일의 빈 unwind stub가 완전한 예외 처리를 한다고 추정하지 않습니다.'),
        ('버리는 입력 섹션', '/DISCARD/에는 .note.GNU-stack, .data와 .data.*, .gnu.linkonce.d.*, .sdata*, .bss, .sbss, .dynbss, .dynsbss를 나열합니다. 일반적인 쓰기 가능 전역 데이터 저장소를 vDSO에 그대로 넣는 구성이 아닙니다. 원본에 나열되지 않은 모든 orphan section까지 무조건 같은 정책으로 처리한다고 확대해서 읽지는 않습니다.'),
        ('세 program header와 권한', 'PHDRS의 text는 유일한 PT_LOAD이며 FLAGS(5)=PF_R|PF_X, FILEHDR PHDRS로 ELF 및 program header도 포함합니다. dynamic은 PT_DYNAMIC FLAGS(4)=PF_R, note는 PT_NOTE FLAGS(4)=PF_R입니다. 세 항목 모두 PF_W가 없지만 text에는 실행 권한이 있습니다. 주석의 read-only를 실행 불가능이라는 뜻으로 해석하면 안 됩니다.'),
        ('심볼 버전과 네 공개 이름', 'VERSION의 LINUX_2.6 노드에서 __vdso_clock_gettime, __vdso_gettimeofday, __vdso_clock_getres, __vdso_clock_gettime64를 global로 지정하고 local: *로 다른 심볼을 제한합니다. LINUX_2.6이라는 버전 이름은 지금 읽는 소스가 v2.6이라는 증거가 아닙니다. 유지되는 ABI 버전 이름과 소스 릴리스 버전은 다릅니다.'),
        ('CS 연결과 검증 범위', '모든 명시적 섹션·PHDR·심볼 규칙·전처리 분기를 다뤘습니다. 섹션은 링크할 내용의 분류이고 program header는 로더가 볼 매핑과 메타데이터를 설명합니다. 이 분석은 스크립트 원본에 근거하며 실제 compat ELF를 빌드하여 섹션 중첩·권한·심볼표를 검사한 결과는 아닙니다.')
    ],
    questions=[
        ('PHDRS에 세 항목이 있으면 PT_LOAD도 세 개인가?', '아니다. PT_LOAD는 text 하나이고 나머지는 PT_DYNAMIC과 PT_NOTE이다', '그렇다. 모든 program header는 별도 로드 가능한 코드 세그먼트이다', 'ELF program header는 종류별 역할이 다릅니다. 이 스크립트는 단일 PT_LOAD를 의도한다는 주석과 선언을 갖습니다.'),
        ('text의 FLAGS(5)가 뜻하는 권한은?', '읽기와 실행이며 쓰기는 없다', '읽기와 쓰기이며 실행은 없다', 'PF_R=4와 PF_X=1을 합한 5입니다. PF_W=2는 포함되지 않습니다. read-only라는 주석도 실행 권한 부재를 뜻하지 않습니다.'),
        ('LINUX_2.6 버전 노드가 뜻하는 것은?', '공개 심볼에 부여하는 ABI 버전 이름이다', '이 파일이 반드시 Linux v2.6 소스라는 뜻이다', '심볼 버전 이름은 호환성을 위해 유지될 수 있습니다. 이 작업의 원본은 v6.12이며 소스 버전과 심볼 버전은 구분해야 합니다.'),
        ('_timens_data는 이 스크립트에서 _vdso_data와 얼마나 떨어져 있는가?', 'CONFIG_TIME_NS일 때 한 PAGE_SIZE 뒤이다', '항상 한 바이트 앞이다', '정의는 _vdso_data + PAGE_SIZE이며 설정 조건도 있습니다. 주소 심볼 계산 자체가 페이지를 할당하는 동작은 아닙니다.')
    ]
)]
