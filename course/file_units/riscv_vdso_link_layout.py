"""Whole-file RISC-V vDSO linker layout and symbol versioning."""
ROWS = [dict(
    path='arch/riscv/kernel/vdso/vdso.lds.S',
    title='RISC-V vDSO ELF 배치: unwind 보존과 조건부 export',
    intro='모든 섹션·program header·공개 심볼 조건을 분석합니다.',
    principle='입력 섹션 이름, 출력 섹션 배치, 로드 권한과 공개 ABI는 서로 다른 링커 규칙으로 결정됩니다.',
    use='데이터 입력의 rodata 수집과 unwind 보존, native·compat 심볼 차이를 설명합니다.',
    area='ELF · 링커 스크립트 · 메모리 권한 · unwind · 심볼 버전 · 전처리',
    sections=[
        ('전체 형식과 의존성', 'GPL-2.0-only 주석 뒤 asm/page.h·asm/vdso.h를 포함하고 OUTPUT_ARCH(riscv)를 지정합니다. 이 파일에는 별도의 OUTPUT_FORMAT 선언은 없습니다. 전처리 설정과 바깥 링크 옵션을 함께 봐야 최종 ELF 클래스 등의 빌드 문맥을 알 수 있습니다.'),
        ('공유 데이터의 상대 주소', 'SECTIONS 처음에 _vdso_data = . - __VVAR_PAGES * PAGE_SIZE를 PROVIDE합니다. CONFIG_TIME_NS이면 _timens_data를 _vdso_data + PAGE_SIZE로 제공합니다. 이어 위치 카운터를 SIZEOF_HEADERS로 옮깁니다. 상대 주소 심볼을 제공하는 식이며 공유 페이지를 실제 할당하거나 매핑하는 코드가 아닙니다.'),
        ('동적 심볼과 버전 섹션', '.hash, .gnu.hash, .dynsym, .dynstr, .gnu.version, .gnu.version_d, .gnu.version_r를 각각 수집합니다. .hash에는 :text를 지정합니다. .dynamic은 :text와 :dynamic 두 program header에 연결합니다. 이 메타데이터가 전부 실행 명령이거나 독립적인 PT_LOAD인 것은 아닙니다.'),
        ('RoData에 들어오는 입력 종류', '.rodata는 .rodata·.rodata.*·.gnu.linkonce.r.*뿐 아니라 .got.plt·.got, .data·.data.*·.gnu.linkonce.d.*, .dynbss, .bss·.bss.*·.gnu.linkonce.b.*도 모읍니다. ARM64 스크립트처럼 이 데이터 입력을 DISCARD하는 구성이 아닙니다. 입력 이름에 data나 bss가 있다는 것과 최종 program header가 쓰기 권한을 갖는지는 다른 문제입니다.'),
        ('Note와 unwind 유지', '.note는 .note.*를 :text와 :note에 배치합니다. .eh_frame_hdr는 :text와 :eh_frame_hdr에 연결하고 .eh_frame은 KEEP(*(.eh_frame))으로 보존합니다. KEEP는 section garbage collection에서 이 입력을 유지하려는 링커 규칙입니다. unwind 메타데이터를 전부 버리는 다른 아키텍처의 스크립트를 그대로 적용해 설명하면 안 됩니다.'),
        ('Text와 alternative 정렬', '여러 메타데이터 뒤 ALIGN(16)을 적용하고 .text와 .text.*를 :text에 수집합니다. 주석은 실행 코드가 실제 데이터와 떨어져 있다고 설명합니다. 이어 ALIGN(4) 뒤 .alternative 입력을 수집합니다. 이 테이블 배치 자체가 CPU 기능을 탐지하거나 명령 패치를 실행하는 것은 아닙니다.'),
        ('네 program header', 'PHDRS에서 text는 유일한 PT_LOAD로 FLAGS(5)=읽기·실행이며 FILEHDR PHDRS를 포함합니다. dynamic은 PT_DYNAMIC FLAGS(4), note는 PT_NOTE FLAGS(4)입니다. eh_frame_hdr는 PT_GNU_EH_FRAME이며 이 항목에는 FLAGS를 명시하지 않았습니다. 이를 네 개의 로드 세그먼트 또는 네 항목 모두 명시적 FLAGS(4)라고 설명하면 틀립니다.'),
        ('기본 공개 심볼', 'VERSION의 LINUX_4.15 노드는 __vdso_rt_sigreturn, __vdso_getcpu, __vdso_flush_icache를 조건 없이 global로 나열합니다. local: *가 나머지 이름의 공개 범위를 제한합니다. LINUX_4.15는 심볼 ABI 버전 이름이며 분석 대상 소스의 v6.12 버전과 구분해야 합니다.'),
        ('시간과 hwprobe의 조건부 공개', 'HAS_VGETTIMEOFDAY가 정의되어야 __vdso_gettimeofday·__vdso_clock_gettime·__vdso_clock_getres를 global 목록에 넣습니다. COMPAT_VDSO가 정의되지 않았을 때만 __vdso_riscv_hwprobe를 넣습니다. 두 조건은 독립적이며 이름의 존재 여부를 확정하려면 실제 전처리 빌드 문맥을 확인해야 합니다. 버전 목록에 이름을 적는 것은 함수 본문 생성이 아닙니다.'),
        ('CS 연결과 검증 범위', '모든 명시적 섹션·주소·정렬·PHDR·VERSION 조건을 설명했습니다. 이 스크립트에는 별도 ASSERT나 /DISCARD/ 블록이 없습니다. 입력 분류와 출력 매핑, unwind 보존, 빌드 조건에 따른 공개 ABI 차이가 핵심입니다. 실제 RISC-V ELF를 링크하여 권한·심볼·section을 검사한 결과는 아닙니다.')
    ],
    questions=[
        ('이 스크립트가 .data와 .bss 입력을 모두 버리는가?', '아니다. 명시한 data·bss 패턴을 .rodata에 수집한다', '그렇다. 모든 vDSO 링커 스크립트는 동일한 DISCARD 규칙을 쓴다', '아키텍처별 실제 규칙을 읽어야 합니다. 이 파일에는 /DISCARD/가 없고 .rodata 수집 목록에 data·bss가 있습니다.'),
        ('네 PHDR 항목 중 PT_LOAD는 몇 개인가?', '하나이다', '네 개이다', '나머지는 PT_DYNAMIC, PT_NOTE, PT_GNU_EH_FRAME입니다. program header의 존재와 로드 세그먼트의 개수는 다릅니다.'),
        ('COMPAT_VDSO가 정의되면 __vdso_riscv_hwprobe를 global 목록에 넣는가?', '아니다. 해당 이름은 #ifndef COMPAT_VDSO 안에 있다', '그렇다. HAS_VGETTIMEOFDAY만 참이면 반드시 넣는다', 'hwprobe와 시간 함수의 조건은 별개입니다. 조건부 구역의 정확한 범위를 확인해야 합니다.'),
        ('KEEP(*(.eh_frame))의 목적은?', 'section garbage collection에서 해당 unwind 입력을 유지하는 것이다', '모든 실행 명령을 .eh_frame으로 복사하는 것이다', 'KEEP는 링크 시 입력 섹션 보존에 관한 지시문입니다. 어셈블리 실행이나 함수 호출 동작이 아닙니다.')
    ]
)]
