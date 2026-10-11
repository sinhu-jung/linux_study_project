"""Whole-file ARM64 vDSO notes, build salt, and offset generation."""
ROWS = [dict(
    path='arch/arm64/kernel/vdso/note.S',
    title='ARM64 vDSO ELF note: 버전과 build salt',
    intro='어셈블리로 생성하는 Linux note와 아키텍처 feature 메타데이터를 분석합니다.',
    principle='바이너리는 실행 명령 외에도 외부 프로그램이 읽을 구조화된 식별 정보를 담을 수 있습니다.',
    use='ELF note의 이름·type·description과 최종 링크 단계의 수집 정책을 구분합니다.',
    area='ELF note · 메타데이터 · 어셈블리 지시문 · 빌드 식별',
    sections=[
        ('파일 전체와 의존성', 'GPL-2.0-only 주석은 .note.*를 vDSO text의 PT_NOTE에 공급한다고 설명합니다. linux/uts.h, linux/version.h, linux/elfnote.h, linux/build-salt.h, asm/assembler.h를 포함합니다. 실행 함수나 syscall 진입점은 없습니다.'),
        ('Linux 버전 note', 'ELFNOTE_START(Linux, 0, "a")와 ELFNOTE_END 사이에 .long LINUX_VERSION_CODE를 둡니다. 이름은 Linux, type은 0, description은 32비트 버전 코드입니다. type 0 자체가 커널 버전인 것은 아닙니다. elfnote 매크로가 note 헤더와 이름·description 크기, 정렬을 구성합니다. 문자열 uname release 전체를 저장하는 구문은 아닙니다.'),
        ('Build salt와 feature', 'BUILD_SALT로 별도의 Linux build salt note를 생성하고 emit_aarch64_feature_1_and를 호출합니다. 관련 링커 스크립트는 .note.gnu.property를 버리므로 객체에 feature note를 요청하는 것과 최종 이미지에서 보존하는 것은 구별해야 합니다. 이 파일에서 암호학적 난수를 생성하거나 build salt를 runtime에 갱신하지 않습니다.'),
        ('CS 연결과 범위', '전체 매크로 호출과 포함 관계를 설명했습니다. 데이터 생성용 어셈블리와 CPU에서 실행되는 명령의 차이, ELF note 형식과 링크 정책이 핵심입니다. 실제 ELF를 빌드해 note 내용을 추출한 검증 결과는 아닙니다.')
    ],
    questions=[
        ('Linux type 0 note의 description은 무엇인가?', 'LINUX_VERSION_CODE를 담은 .long 값이다', '문자열 형태의 전체 uname 출력이다', '본문은 .long LINUX_VERSION_CODE입니다. note의 type과 description, 정수 버전과 문자열 release를 구분해야 합니다.'),
        ('이 파일이 사용자 공간에서 실행되는 시간 조회 함수를 구현하는가?', '아니다. ELF note 메타데이터를 공급한다', '그렇다. PT_NOTE가 clock_gettime 실행 코드이다', 'note는 외부 도구가 읽는 정보입니다. 함수 본문이나 시간 읽기 명령이 이 파일에 없습니다.')
    ]
), dict(
    path='arch/arm64/kernel/vdso32/note.c',
    title='ARM64 compat vDSO note: C 매크로로 메타데이터 생성',
    intro='C로 작성한 버전 note와 build salt 정의 전체를 분석합니다.',
    principle='C 소스도 함수 없이 정적 ELF 메타데이터 객체를 생성할 수 있습니다.',
    use='ELFNOTE32의 인수와 어셈블리 note의 차이를 읽습니다.',
    area='ELF · C 매크로 · 정적 데이터 · 호환 ABI',
    sections=[
        ('전체 구성', 'GPL-2.0 표기와 vDSO의 PT_NOTE에 정보를 공급한다는 주석 뒤 linux/uts.h, linux/version.h, linux/elfnote.h, linux/build-salt.h를 포함합니다. 이어 ELFNOTE32와 BUILD_SALT 두 호출만 있으며 별도 함수는 없습니다.'),
        ('C 버전 note', 'ELFNOTE32("Linux", 0, LINUX_VERSION_CODE)는 C용 elfnote 매크로를 통해 note 헤더·이름·description을 담는 정적 const 객체를 해당 note 섹션에 생성합니다. 이름은 문자열 리터럴, type은 0, 내용은 버전 코드입니다. 단순 함수 호출이나 실행 시 printf가 아닙니다. 자세한 객체 배치와 __used 속성은 포함된 매크로 정의에 있습니다.'),
        ('Build salt와 native 차이', 'BUILD_SALT도 C 분기의 note 생성 매크로로 확장됩니다. 이 파일에는 native note.S의 emit_aarch64_feature_1_and 호출이나 asm/assembler.h 포함이 없습니다. 같은 목적의 note라도 C·어셈블리 입력 형식과 아키텍처별 부가 내용이 다릅니다.'),
        ('범위', '전체 파일의 두 note 생성과 include를 설명했습니다. C 소스 파일이 반드시 함수를 구현해야 하는 것은 아니라는 점, 객체의 메타데이터와 실행 동작의 차이를 학습합니다. 실제 compat ELF note 추출 시험은 수행하지 않았습니다.')
    ],
    questions=[
        ('ELFNOTE32 호출을 실행 시 함수 호출로 읽어도 되는가?', '아니다. 정적 note 객체를 만드는 C 매크로이다', '그렇다. 프로세스가 시작할 때 버전을 출력한다', 'C용 매크로는 정적 객체와 섹션 속성으로 확장됩니다. 이 파일에는 실행 함수 본문이나 출력 동작이 없습니다.'),
        ('이 compat 파일도 emit_aarch64_feature_1_and를 직접 호출하는가?', '아니다. 버전 note와 BUILD_SALT만 있다', '그렇다. native note.S와 모든 줄이 동일하다', '두 파일은 목적 일부를 공유하지만 원본 내용은 다릅니다. native의 부가 feature 호출을 compat에도 있다고 옮겨 읽으면 안 됩니다.')
    ]
), dict(
    path='include/linux/build-salt.h',
    title='Build salt note: C와 어셈블리의 공통 식별 데이터',
    intro='Linux note type 0x100과 두 전처리 분기를 분석합니다.',
    principle='같은 바이너리 메타데이터를 언어별 생성 방식으로 제공할 수 있으며 이름이 salt여도 runtime 난수 생성과는 다릅니다.',
    use='빌드 설정 문자열이 note 내용으로 변환되는 과정을 설명합니다.',
    area='전처리 · 문자열 표현 · ELF note · 빌드 설정',
    sections=[
        ('전체 정의', '__BUILD_SALT_H guard 아래 linux/elfnote.h를 포함하고 LINUX_ELFNOTE_BUILD_SALT를 0x100으로 정의합니다. note 이름 Linux의 type 값으로 쓰며 여기서 해시 함수·난수 함수·저장 장치를 구현하지 않습니다. 별도의 파일 SPDX 표기는 원본에 없습니다.'),
        ('어셈블러 분기', '#ifdef __ASSEMBLER__에서는 BUILD_SALT를 ELFNOTE(Linux, LINUX_ELFNOTE_BUILD_SALT, .asciz CONFIG_BUILD_SALT)로 정의합니다. .asciz는 설정 문자열 뒤 NUL을 포함하는 표현입니다. CONFIG_BUILD_SALT는 빌드 문맥이 제공하며 이 헤더는 기본 문자열이나 값 검증을 따로 정의하지 않습니다.'),
        ('C 분기', 'else에서는 ELFNOTE32("Linux", LINUX_ELFNOTE_BUILD_SALT, CONFIG_BUILD_SALT)를 사용합니다. C elfnote 매크로는 description의 typeof와 sizeof를 사용하므로 문자열 데이터를 그대로 담습니다. ELFNOTE32 이름만 보고 문자열을 32비트 정수 salt로 잘라 저장한다고 해석하면 안 됩니다. note 헤더 형식 선택과 description 자료형은 다른 요소입니다.'),
        ('CS 연결과 범위', '한 BUILD_SALT 이름을 C·어셈블리 양쪽에서 사용할 수 있도록 다른 확장을 제공합니다. 이것은 빌드 시 제공된 식별 데이터이며 비밀키 생성이나 실행 시 entropy 공급 기능이 아닙니다. 전체 매크로와 분기를 설명했으며 실제 설정값이나 만들어진 바이너리의 내용을 이 파일만으로 확정하지 않습니다.')
    ],
    questions=[
        ('BUILD_SALT가 생성하는 Linux note의 type 값은?', '0x100이다', 'LINUX_VERSION_CODE 그 자체이다', '버전 note의 type 0과 build salt의 type 0x100은 별개의 항목입니다. type은 description을 구분하는 태그입니다.'),
        ('C 분기의 ELFNOTE32는 CONFIG_BUILD_SALT 문자열을 32비트 정수로 잘라 저장하는가?', '아니다. description은 매크로의 typeof와 sizeof로 문자열 데이터를 담는다', '그렇다. 이름에 32가 있으므로 항상 4바이트만 남는다', 'ELF note 헤더 선택과 description 형식은 독립적입니다. 문자열 길이는 원래 설정 문자열의 크기에 따라 결정됩니다.')
    ]
), dict(
    path='arch/arm64/kernel/vdso/gen_vdso_offsets.sh',
    title='vDSO offset 생성: nm 텍스트에서 C 정의로',
    intro='셸과 sed 두 치환으로 심볼 주소를 헤더 정의로 만드는 과정을 분석합니다.',
    principle='작은 빌드 도구도 입력 형식 계약, 선택 규칙, 출력 소유권을 정확히 구분해야 합니다.',
    use='정규식 캡처·앵커·출력 억제와 빌드 파이프라인의 역할을 이해합니다.',
    area='셸 · sed · 정규식 · 텍스트 변환 · 빌드 파이프라인 · 심볼 주소',
    sections=[
        ('전체 목적과 실행 문맥', '#!/bin/sh, GPL-2.0, 설명 주석, LC_ALL=C 대입과 sed 명령으로 구성됩니다. 주석은 VDSO_* 심볼을 상수 offset 헤더로 바꾸며 Makefile 안에 이 작업을 직접 넣으면 filter-out과 상호작용하여 매번 헤더를 재생성하는 문제가 있다고 설명합니다. 여기서 바이너리를 직접 열거나 nm를 실행하지 않습니다.'),
        ('표준 입력과 출력', 'sed에 파일 인수가 없으므로 표준 입력을 읽고 표준 출력에 결과를 씁니다. 실제 관련 Makefile은 NM 출력 → 이 스크립트 → LC_ALL=C sort → 헤더 파일 리다이렉션의 파이프라인을 구성합니다. 정렬과 파일 저장을 스크립트 자체의 기능으로 혼동하지 않습니다. sed -n은 매 줄 자동 출력을 끕니다.'),
        ('앞의 0 정규화', '첫 -e 식 s/^00*/0/은 줄 시작에서 하나 이상의 0을 하나의 0으로 줄입니다. 예를 들어 0000000000000120은 0120이 됩니다. 0을 전부 삭제하여 120으로 만드는 식이 아니며 줄 중간의 0이나 문자도 건드리지 않습니다. ^가 줄 시작을 제한하고 뒤의 0*가 추가 0들을 소비합니다.'),
        ('심볼 선택 정규식', '두 번째 식은 줄 전체가 hexadecimal 주소, 공백, 임의 한 글자 type, 공백, VDSO_, 영문·숫자·밑줄 suffix인 경우를 매칭합니다. 주소는 캡처 1, suffix는 캡처 2입니다. type 자리는 .이므로 T 같은 코드 심볼에만 제한하지 않습니다. 시작과 끝 앵커 때문에 뒤에 추가 텍스트가 있으면 매칭되지 않습니다. *가 쓰여 주소와 suffix에 엄격한 비어 있지 않음 검사까지 제공하는 것은 아닙니다.'),
        ('출력 예시와 접두어', '매칭된 줄을 #define vdso_offset_접미사 0x주소로 바꾸고 p 플래그로 출력합니다. 예를 들어 0000000000000120 T VDSO_sigtramp는 #define vdso_offset_sigtramp 0x0120이 됩니다. VDSO_가 아닌 일반 __kernel_rt_sigreturn 이름의 줄은 직접 출력하지 않습니다. native 링커의 VDSO_sigtramp 별칭과 이 생성 규칙이 연결됩니다.'),
        ('로케일과 처리 한계', 'LC_ALL=C 대입은 있지만 명시적인 export는 없습니다. sed 자식의 환경으로 전달되는지는 그 변수의 기존 export 상태도 고려해야 하므로 이 대입만으로 항상 자식 환경을 강제한다고 단정하지 않습니다. 이 스크립트는 입력 ELF 검증, 중복 심볼 검출, 주소 범위 검증, 헤더 guard 생성을 하지 않습니다. 주어진 nm 출력 형식에 맞춘 제한된 텍스트 변환입니다.'),
        ('CS 연결과 검증 범위', '모든 실행 줄과 치환식을 설명했습니다. 정규식 필터와 파서의 차이, 파이프라인 각 단계의 책임, 심볼 이름을 생성 헤더 API로 바꾸는 과정이 핵심입니다. 예시는 식을 추적한 결과이며 실제 셸에서 이 스크립트를 실행하거나 최종 ELF offset과 대조한 시험은 아닙니다.')
    ],
    questions=[
        ('00000120 T VDSO_sigtramp의 출력 정의는?', '#define vdso_offset_sigtramp 0x0120이다', '#define VDSO_sigtramp 120이다', '첫 치환이 앞 0 묶음을 한 0으로 줄이고 두 번째 치환이 이름 접두어와 0x를 추가합니다. offset 수치의 의미는 유지됩니다.'),
        ('이 스크립트가 nm와 sort를 직접 실행하는가?', '아니다. 관련 Makefile의 앞뒤 파이프라인에서 수행한다', '그렇다. sed 내부가 자동으로 ELF를 열고 정렬한다', '스크립트는 stdin에서 텍스트를 읽는 sed만 실행합니다. 바이너리 심볼 추출과 정렬·파일 저장은 호출 문맥의 역할입니다.'),
        ('심볼 type이 T가 아니면 반드시 제외되는가?', '아니다. 정규식 type 자리는 임의 한 글자 .이다', '그렇다. 함수 심볼 T만 하드코딩했다', '필터는 VDSO_ 이름과 줄 형식에 초점을 둡니다. type의 의미를 해석하는 ELF 검증 도구로 확대해서 읽으면 안 됩니다.')
    ]
)]
