"""Whole-file native ARM64 vDSO ELF linker script."""
ROWS = [dict(
    path='arch/arm64/kernel/vdso/vdso.lds.S',
    title='ARM64 vDSO 링크 배치: RNG·명령 대체·심볼 버전',
    intro='64비트 ARM vDSO의 섹션 배치와 세그먼트 권한, 다섯 공개 심볼을 전체 분석합니다.',
    principle='실행 코드와 메타데이터의 배치, 사용자 공간 ABI 공개, 커널이 참조할 심볼은 링커 단계에서 서로 다른 규칙으로 구성됩니다.',
    use='compat 링커 스크립트와 다른 RNG 주소·RELA·명령 대체 테이블·sigreturn 연결을 구별합니다.',
    area='ELF · 링커 스크립트 · 심볼 버전 · 정렬 · 메모리 권한 · 재배치 · 시그널 복귀',
    sections=[
        ('파일 전체와 출력 형식', 'GPL-2.0-only 표기 뒤 linux/const.h, asm/page.h, asm/vdso.h, asm/vdso/vsyscall.h, asm-generic/vmlinux.lds.h, vdso/datapage.h를 포함합니다. OUTPUT_FORMAT은 elf64-littleaarch64, elf64-bigaarch64, elf64-littleaarch64이고 OUTPUT_ARCH는 aarch64입니다. compat 파일의 elf32 ARM 출력과 다릅니다. .S의 전처리와 링커 스크립트 해석을 거쳐 매크로와 주소 식을 사용합니다.'),
        ('Vvar와 RNG 데이터 심볼', 'SECTIONS 처음에 PROVIDE로 _vdso_data = . - __VVAR_PAGES * PAGE_SIZE, _vdso_rng_data = _vdso_data + __VDSO_RND_DATA_OFFSET을 제공합니다. CONFIG_TIME_NS이면 _timens_data = _vdso_data + PAGE_SIZE도 제공합니다. 이어 위치 카운터를 VDSO_LBASE + SIZEOF_HEADERS로 설정합니다. 포함된 ARM64 vsyscall 헤더의 RNG 오프셋은 480바이트입니다. 이 식은 공유 페이지와 코드의 상대 주소 계약이며 페이지 할당이나 난수 초기화가 아닙니다.'),
        ('PROVIDE와 공개 정책의 구별', '여기는 compat 스크립트의 PROVIDE_HIDDEN과 달리 PROVIDE를 사용합니다. 그렇다고 이 데이터 심볼이 사용자에게 공개되는 다섯 ABI 함수 목록에 포함된다는 뜻은 아닙니다. VERSION의 local: *와 선언 문맥도 심볼 노출에 관여합니다. PROVIDE는 참조와 기존 정의 여부에 따라 필요한 심볼 정의를 제공하는 링커 문법이며 C 저장 객체의 본문을 만드는 것이 아닙니다.'),
        ('동적 조회 메타데이터', '.hash, .gnu.hash, .dynsym, .dynstr, .gnu.version, .gnu.version_d, .gnu.version_r를 동명 입력 섹션에서 수집합니다. .hash에 :text를 명시합니다. 이들은 동적 심볼 조회·문자열·버전 정보를 위한 부분이며 전부 실행 명령이 아닙니다. section 분류와 뒤 PHDRS의 로드 단위는 구별해야 합니다.'),
        ('Note를 버리는 순서', '첫 /DISCARD/는 .note.GNU-stack과 .note.gnu.property를 제거합니다. 주석은 GNU property가 여기서 사용되지 않으며 vDSO note와 정렬 요구가 다르다고 설명합니다. 이어 .note가 나머지 .note.*를 모아 :text와 :note에 배치합니다. 제외 대상을 먼저 처리하는 규칙을 생략하면 일반 note 패턴의 범위를 잘못 이해하게 됩니다.'),
        ('Text 정렬과 끝 심볼', '위치 카운터를 ALIGN(16)으로 맞추고 .text*를 :text에 모으며 fill 값 0xd503201f를 지정합니다. 이어 __etext, _etext, etext 세 이름을 현재 위치로 PROVIDE합니다. 이것은 같은 코드 끝 위치를 가리키는 이름들이며 서로 다른 세 함수가 아닙니다. fill 값은 필요한 채움 패턴이지 모든 명령을 해당 값으로 바꾸라는 뜻이 아닙니다.'),
        ('명령 대체와 재배치', 'ALIGN(4) 뒤 .altinstructions를 수집합니다. 이 메타데이터는 아키텍처의 명령 대체와 연결되지만 이 링커 스크립트 자체가 CPU 기능을 탐지하거나 패치 루프를 실행하지는 않습니다. .dynamic은 :text와 :dynamic에 연결합니다. .rela.dyn은 ALIGN(8)로 .rela와 .rela*를 수집합니다. compat의 .rel.dyn과 다르게 RELA 이름을 쓰며 실제 재배치 엔트리 존재 여부는 빌드 결과에서 별도로 확인해야 합니다.'),
        ('RoData와 이미지 끝', '.rodata는 .rodata*, .got, .got.plt, .plt, .plt.*, .iplt, .igot, .igot.plt를 수집해 :text에 둡니다. 단순 상수 외에 링크 관련 입력도 포함합니다. 그 뒤 _end = .로 직접 정의하고 end를 PROVIDE합니다. 앞의 etext는 text 직후이고 _end는 여기까지 배치한 내용의 끝이므로 두 위치를 무조건 같다고 가정하면 안 됩니다.'),
        ('디버그와 두 번째 discard', 'DWARF_DEBUG와 ELF_DETAILS 매크로를 사용한 뒤 두 번째 /DISCARD/에서 .data, .data.*, .gnu.linkonce.d.*, .sdata*, .bss, .sbss, .dynbss, .dynsbss, .eh_frame, .eh_frame_hdr를 제거합니다. 쓰기 가능 데이터 계열과 이 unwind 섹션들을 남기는 설계가 아닙니다. 명시한 패턴을 넘어 모든 미분류 섹션까지 자동으로 같은 정책이라고 확대해서 읽지 않습니다.'),
        ('세그먼트 권한과 로드 개수', 'text는 PT_LOAD FLAGS(5), FILEHDR PHDRS로 ELF 및 program header를 포함하는 읽기·실행 세그먼트입니다. dynamic은 PT_DYNAMIC FLAGS(4), note는 PT_NOTE FLAGS(4)로 읽기 권한만 표시합니다. 유일한 PT_LOAD를 만들고 쓰기 권한을 주지 않으려는 의도를 주석과 선언이 함께 나타냅니다. 세 program header가 세 개의 PT_LOAD라는 뜻은 아닙니다.'),
        ('공개 심볼과 시그널 trampoline', 'LINUX_2.6.39 버전 노드는 __kernel_rt_sigreturn, __kernel_gettimeofday, __kernel_clock_gettime, __kernel_clock_getres, __kernel_getrandom 다섯 이름을 global로 나열하고 나머지는 local: *로 제한합니다. 버전 노드 이름은 소스 릴리스 v6.12와 별개의 ABI 이름입니다. 끝의 VDSO_sigtramp = __kernel_rt_sigreturn은 커널이 복귀 코드 위치를 참조하도록 별도 심볼 이름을 연결합니다. 별도 시그널 복귀 함수 본문을 생성하는 식은 아닙니다.'),
        ('CS 연결과 검증 범위', '모든 명시적 섹션·주소 심볼·PHDR·VERSION·조건부 분기를 다뤘습니다. 이 파일에는 별도의 ASSERT 지시문이 없으므로 존재하지 않는 링크 검증 조건을 설명에 추가하지 않습니다. 주소 배치와 권한, 함수 정의와 공개 ABI의 구별이 핵심입니다. 원본 분석이며 실제 ARM64 ELF를 생성해 섹션·권한·심볼표를 검증한 결과는 아닙니다.')
    ],
    questions=[
        ('이 스크립트에서 __kernel_getrandom은 공개 심볼 목록에 있는가?', '그렇다. LINUX_2.6.39의 global 목록에 있다', '아니다. 시간 조회 함수 세 개만 공개한다', '목록에는 시간 함수 세 개뿐 아니라 rt_sigreturn과 getrandom도 있습니다. compat 스크립트의 네 __vdso 이름과 구분해야 합니다.'),
        ('etext와 _end가 항상 같은 주소인가?', '아니다. etext 이후에도 대체 명령 메타데이터·dynamic·rodata 등이 배치된다', '그렇다. 이름이 다를 뿐 항상 같은 줄에서 정의한다', 'etext는 .text 직후, _end는 .rodata 뒤에 정의됩니다. 위치 카운터가 그 사이의 배치로 이동하므로 같은 주소라고 일반화할 수 없습니다.'),
        ('VDSO_sigtramp = __kernel_rt_sigreturn의 역할은?', '기존 복귀 코드 위치를 커널용 심볼 이름으로 연결한다', '두 번째 시그널 복귀 함수를 새로 컴파일한다', '링커의 심볼 대입은 함수 본문 생성이 아닙니다. 주석은 커널이 sigreturn 코드를 볼 수 있게 하는 목적을 설명합니다.'),
        ('이 파일에서 명시적으로 버리는 note 입력은?', '.note.GNU-stack과 .note.gnu.property이다', '모든 .note.*이다', '해당 둘을 먼저 DISCARD한 뒤 나머지 .note.*를 .note 출력 섹션에 모읍니다. 제외 규칙과 일반 수집 규칙을 함께 읽어야 합니다.'),
        ('_vdso_rng_data는 _vdso_data와 어떤 관계인가?', '__VDSO_RND_DATA_OFFSET만큼 뒤에 있으며 여기서는 포함 헤더의 480바이트 오프셋을 쓴다', '무조건 다음 PAGE_SIZE 페이지의 첫 주소이다', 'RNG 주소는 고정 바이트 오프셋을 사용합니다. 다음 페이지를 가리키는 식은 CONFIG_TIME_NS 아래의 _timens_data입니다.')
    ]
)]
