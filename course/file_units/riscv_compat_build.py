"""Whole-file RISC-V compat vDSO build and offset generator."""
ROWS = [dict(
    path='arch/riscv/kernel/compat_vdso/Makefile',
    title='RISC-V compat vDSO 빌드: RV32 ABI와 별도 산출물',
    intro='32비트 어셈블리 빌드·링크·심볼 처리·생성 헤더 규칙 전체를 분석합니다.',
    principle='native 소스를 재사용해도 컴파일 ISA와 ABI, ELF 링크 모드, 결과 파일 이름을 별도로 설정해야 호환 이미지를 만들 수 있습니다.',
    use='빌드 설정별 ISA 옵션과 심볼 접두어의 실제 차이를 설명합니다.',
    area='크로스 ABI · RV32 · GNU make · ELF · objcopy · 생성 헤더',
    sections=[
        ('전체 객체 목록과 도구', 'GPL-2.0-only 아래 compat_vdso-syms에 rt_sigreturn·getcpu·flush_icache 세 stem을 넣습니다. COMPAT_CC와 COMPAT_LD는 각각 기존 CC와 LD를 사용합니다. 별도의 이름을 가진 toolchain 실행 파일을 자동 검색하는 코드는 없습니다. 객체 목록은 각 .o와 note.o이며 시간·hwprobe 객체는 이 목록에 없습니다.'),
        ('ISA와 ABI 선택', 'CONFIG_TOOLCHAIN_NEEDS_EXPLICIT_ZICSR_ZIFENCEI이면 -march=rv32g -mabi=ilp32, 아니면 -march=rv32imafd -mabi=ilp32를 사용합니다. 주석은 binutils 2.35의 zifencei 지원과 20191213 ISA에서 G가 뜻하는 묶음을 설명합니다. 현재 모든 도구 버전의 동작을 이 역사적 주석 하나로 확정하지 않고 실제 조건의 두 옵션을 그대로 구분합니다. 두 경로 모두 ilp32입니다.'),
        ('링크 모드와 attribute 억제', 'COMPAT_LD_FLAGS=-melf32lriscv로 32비트 little-endian RISC-V 링크 모드를 지정합니다. cc-option으로 -mno-riscv-attribute, as-option으로 -Wa,-mno-arch-attr 지원을 확인해 컴파일 옵션에 더합니다. 주석은 attributes가 빌드를 깨뜨려 끈다고 설명합니다. 지원 검사 helper의 반환에 따라 추가되는 옵션이지 무조건 모든 도구가 수용한다고 가정하지 않습니다.'),
        ('Targets와 이미지 포함', 'targets에 객체·compat_vdso.so·compat_vdso.so.dbg·compat_vdso.lds를 저장한 뒤 객체에 $(obj)/ 접두어를 붙입니다. obj-y에는 compat_vdso.o를 넣고 이 객체가 compat_vdso.so에 의존하게 합니다. 링커 스크립트 전처리에는 -P -C -DCOMPAT_VDSO -U$(ARCH)를 주어 공유 스크립트의 compat 조건을 선택합니다.'),
        ('링크 타깃과 옵션', 'compat_vdso.so.dbg는 첫 의존성 compat_vdso.lds, 객체 목록, FORCE 순서로 if_changed,compat_vdsold를 호출합니다. LDFLAGS에는 -shared -S, soname linux-compat_vdso.so.1, sha1 build-id, 두 hash 형식, eh-frame header 옵션이 있습니다. .dbg라는 이름만 보고 디버그 정보를 모두 보존한다고 단정하면 안 되며 실제 링크에 -S가 있다는 점을 확인해야 합니다.'),
        ('어셈블과 최종 strip', '객체 목록에 적용하는 static pattern rule은 %.o가 %.S와 FORCE에 의존하고 if_changed_dep,compat_vdsoas를 호출하도록 합니다. 명령은 COMPAT_CC, a_flags, COMPAT_CC_FLAGS, -c -o $@ $<입니다. 별도로 %.so는 %.so.dbg를 objcopy -S로 처리합니다. 어셈블리 객체 생성과 이미 링크된 ELF의 strip은 다른 단계입니다.'),
        ('Offset 헤더', 'NM의 첫 의존성 출력에 gen_compat_vdso_offsets.sh를 적용하고 LC_ALL=C sort 후 타깃 파일에 저장합니다. include/generated/compat_vdso-offsets.h는 compat_vdso.so.dbg와 FORCE에 의존합니다. 이 파일에서 native vdso-offsets.h를 덮어쓰는 규칙은 없습니다.'),
        ('임시 파일과 이름 필터', 'compat_vdsold는 COMPAT_LD로 $@.tmp를 링크한 뒤 objcopy에 stem별 -G __compat_vdso_이름을 주어 $@를 만들고 임시 파일을 지웁니다. 세 단계는 &&로 연결됩니다. 그런데 확인한 재사용 getcpu.S의 실제 함수 이름은 __vdso_getcpu이고, offset 생성 스크립트도 __vdso_ 이름을 입력으로 받습니다. 따라서 objcopy 옵션의 __compat_vdso_ 접두어를 실제 소스 함수 이름이나 rename 동작이라고 단정하면 안 됩니다. -G는 이름 변경 옵션이 아닙니다.'),
        ('실행과 정의의 범위', 'FORCE와 if_changed 계열 helper를 함께 사용하므로 FORCE만 보고 매번 무조건 같은 빌드를 수행한다고 단순화하지 않습니다. 이 Makefile에는 lib/vdso/Makefile include나 cmd_vdso_check 호출이 없습니다. 전체 변수·조건·타깃·명령을 대조했으며 실제 compat 링크 후 심볼표·오프셋·도구 버전별 성공을 검증한 결과는 아닙니다.')
    ],
    questions=[
        ('두 ISA 선택 경로에서 공통으로 사용하는 ABI 옵션은?', '-mabi=ilp32이다', '-mabi=lp64이다', 'rv32g와 rv32imafd로 march가 갈리지만 mabi는 두 분기 모두 ilp32입니다.'),
        ('objcopy의 -G __compat_vdso_getcpu는 함수 이름을 그 이름으로 바꾸는가?', '아니다. -G는 심볼 global 유지 정책이며 rename 옵션이 아니다', '그렇다. 입력의 모든 __vdso 이름이 자동으로 변경된다', '실제 재사용 소스와 offset 필터는 __vdso_ 이름을 사용합니다. 옵션에 나타나는 문자열과 함수 정의를 같은 것으로 가정하면 안 됩니다.'),
        ('compat offset 결과는 어디에 생성되는가?', 'include/generated/compat_vdso-offsets.h이다', '항상 native vdso-offsets.h를 덮어쓴다', '규칙은 별도 생성 헤더와 compat dbg ELF 의존성을 명시합니다. 두 ABI 산출물을 구분해야 합니다.'),
        ('.dbg라는 파일 이름만으로 모든 디버그 정보가 보존된다고 확정할 수 있는가?', '아니다. 이 타깃 링크 옵션에도 -S가 있다', '그렇다. 확장자가 링커 옵션을 자동 무시한다', '이름은 빌드 관례일 뿐 실제 도구 옵션이 동작을 결정합니다. 최종 내용은 링크 결과로 확인해야 합니다.')
    ]
), dict(
    path='arch/riscv/kernel/compat_vdso/gen_compat_vdso_offsets.sh',
    title='Compat offset 생성: __vdso 심볼에서 compat 매크로로',
    intro='sed 입력과 출력의 서로 다른 접두어를 전체 분석합니다.',
    principle='생성 헤더 이름에 접두어를 추가하는 것과 ELF 심볼을 변경하는 것은 다른 작업입니다.',
    use='정규식 캡처와 prefix 변환을 native 생성 도구와 비교합니다.',
    area='sed · 정규식 · 텍스트 변환 · ABI 이름 공간',
    sections=[
        ('전체 실행 줄', '#!/bin/sh와 GPL-2.0 뒤 LC_ALL=C 대입과 sed -n -e 한 명령입니다. 입력 파일 인수가 없으므로 stdin의 nm 텍스트를 읽고 일치하는 정의만 stdout에 씁니다. 별도 ELF 파서나 파일 저장·정렬 명령은 없습니다.'),
        ('주소와 심볼 패턴', '시작의 [0]\\+와 0으로 시작하는 16진수 캡처 때문에 최소 두 선행 0을 가진 주소 형식을 기대합니다. 이어 공백·type 한 글자·공백과 __vdso_로 시작하는 이름을 끝까지 매칭합니다. 입력 접두어는 __compat_vdso_가 아닙니다. native 스크립트와 같은 형식 제약을 가진 텍스트 필터입니다.'),
        ('Compat 출력 이름', '치환은 #define compat와 캡처한 전체 __vdso_이름, _offset을 결합하고 tab 뒤 0x주소를 둡니다. 예를 들어 00000120 T __vdso_getcpu는 compat__vdso_getcpu_offset과 0x0120을 만드는 정의가 됩니다. 원본 바이너리의 함수 이름이나 바이트를 수정하지 않습니다.'),
        ('범위와 환경', 'LC_ALL 대입은 명시적 export가 없어 자식 전달은 기존 환경의 export 상태와도 관련됩니다. 사용한 sed의 \\+와 \\t 지원에 의존하며 잘못된 ELF·중복 정의·주소 범위를 별도로 검사하지 않습니다. 전체 식을 대조했으며 실제 셸과 compat ELF로 실행한 시험은 수행하지 않았습니다.')
    ],
    questions=[
        ('입력에서 찾는 함수 이름의 접두어는?', '__vdso_이다', '__compat_vdso_이다', 'compat는 출력 매크로 이름 앞에 붙입니다. 입력 심볼 선택과 출력 이름 변환을 구분해야 합니다.'),
        ('생성한 compat__vdso_getcpu_offset이 ELF 함수 이름을 바꾸는가?', '아니다. C 헤더의 주소 상수 이름을 만든다', '그렇다. sed가 ELF symbol table을 직접 수정한다', '이 스크립트는 nm 텍스트를 처리합니다. 바이너리 파일을 열거나 쓰지 않습니다.')
    ]
)]
