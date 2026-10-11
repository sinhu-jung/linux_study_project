"""Whole-file RISC-V embedded vDSO image and Linux version note."""
ROWS = [dict(
    path='arch/riscv/kernel/vdso/vdso.S',
    title='RISC-V vDSO 이미지 포함: incbin과 페이지 정렬 경계',
    intro='이미지 경로 선택과 시작·끝 심볼, 바이너리 포함 지시문 전체를 분석합니다.',
    principle='이미 만들어진 실행 파일을 커널 데이터로 포함하는 단계는 그 파일의 소스를 컴파일하는 단계와 다릅니다.',
    use='페이지 정렬 padding과 원래 ELF 길이의 차이를 설명합니다.',
    area='어셈블러 · incbin · 페이지 정렬 · 링크 심볼 · 빌드 산출물',
    sections=[
        ('전체 의존성', 'GPL-2.0-only와 저작권 뒤 linux/init.h, linux/linkage.h, asm/page.h를 포함합니다. 실행 함수 본문은 없고 데이터 섹션 선택·심볼 정의·이미지 포함을 수행하는 어셈블러 지시문으로 구성됩니다.'),
        ('경로 기본값과 재정의', '__VDSO_PATH가 정의되어 있지 않으면 문자열 arch/riscv/kernel/vdso/vdso.so로 정의합니다. 이미 빌드 문맥에서 제공되었다면 그 값을 유지합니다. 이것은 전처리 시 선택이며 실행 중 파일 시스템에서 경로를 검색하는 코드가 아닙니다.'),
        ('섹션과 시작 경계', '__PAGE_ALIGNED_DATA 매크로를 사용하고 .globl로 vdso_start와 vdso_end를 공개합니다. .balign PAGE_SIZE 뒤 vdso_start 라벨을 놓아 포함 이미지의 시작을 페이지 경계에 맞춥니다. 여기서 .globl의 공개는 링크 심볼 범위이며 사용자 vDSO의 동적 함수 export 목록과 다릅니다.'),
        ('바이너리 포함', '.incbin __VDSO_PATH는 지정한 파일의 바이너리 바이트를 현재 출력에 포함합니다. ELF 소스를 다시 C로 컴파일하거나 include한 내용의 명령을 실행하는 것이 아닙니다. 입력 파일 생성 의존성은 Makefile이 관리해야 하며 이 파일 자체가 vdso.so를 링크하지 않습니다.'),
        ('끝 정렬과 크기', 'incbin 뒤 .balign PAGE_SIZE를 한 번 더 수행한 다음 vdso_end 라벨을 둡니다. 따라서 vdso_end-vdso_start는 원본 파일 크기에 끝 padding을 더한 페이지 배수일 수 있습니다. 예를 들어 PAGE_SIZE=4096이고 입력이 5000바이트이면 영역은 8192바이트가 됩니다. 원본 ELF 파일 길이와 정렬된 포함 영역 길이를 구분해야 합니다.'),
        ('섹션 복구와 범위', '마지막 .previous는 이전 섹션 문맥으로 돌아갑니다. 전체 매크로·조건·라벨·지시문을 설명했습니다. 페이지를 사용자 공간에 실제 매핑하거나 권한을 설정하는 코드는 이 파일에 없습니다. 실제 RISC-V 이미지 빌드와 포함 바이트 비교를 실행한 검증 결과는 아닙니다.')
    ],
    questions=[
        ('PAGE_SIZE=4096, 입력 ELF=5000바이트라면 정렬된 시작·끝 심볼 간 거리는?', '8192바이트이다', '항상 원본과 같은 5000바이트이다', '끝 라벨이 두 번째 페이지 정렬 뒤에 있습니다. 다음 페이지 경계까지 padding이 포함됩니다.'),
        ('.incbin은 무엇을 하는가?', '이미 생성된 파일의 바이트를 출력에 포함한다', '실행 중 해당 파일을 열어 난수를 읽는다', '어셈블 단계의 데이터 포함 지시문입니다. runtime 파일 입출력이나 C 소스 컴파일과 다릅니다.'),
        ('__VDSO_PATH를 빌드 문맥에서 미리 정의하면 기본 경로가 덮어쓰는가?', '아니다. #ifndef이므로 기존 값을 유지한다', '그렇다. 항상 기본 경로로 강제한다', '전처리 조건이 사용자 제공 경로와 기본값을 구분합니다. 함수 실행 중의 조건 분기가 아닙니다.')
    ]
), dict(
    path='arch/riscv/kernel/vdso/note.S',
    title='RISC-V vDSO 버전 note: Linux type 0 메타데이터',
    intro='버전 코드 하나를 ELF note로 제공하는 파일 전체를 분석합니다.',
    principle='실행 코드의 식별 정보는 데이터 메타데이터로 제공하며 호출 가능한 함수와 구별합니다.',
    use='note 이름·type·description과 링크 단계의 역할을 설명합니다.',
    area='ELF note · 바이너리 메타데이터 · 버전 코드 · 어셈블리 매크로',
    sections=[
        ('전체 파일', 'GPL-2.0-or-later 표기와 사용자 공간에 유용한 note를 공급한다는 주석 뒤 linux/elfnote.h와 linux/version.h를 포함합니다. 이 파일에는 build-salt.h 포함이나 BUILD_SALT 호출이 없습니다. ARM64 note의 내용을 자동으로 동일하게 가정하지 않습니다.'),
        ('Note 내용', 'ELFNOTE_START(Linux,0,"a")와 ELFNOTE_END 사이에 .long LINUX_VERSION_CODE를 둡니다. 이름은 Linux, type은 0, description은 32비트 버전 코드입니다. uname release 문자열이나 함수 주소가 description인 것은 아닙니다. 헤더·문자열 크기·padding은 포함된 note 매크로가 구성합니다.'),
        ('링크와 실행의 구분', '주석은 .note.*가 vDSO text 내부의 PT_NOTE로 들어갈 목적이라고 설명합니다. 실제 output section과 program header 연결은 링커 스크립트가 결정합니다. 이 파일은 CPU에서 실행할 시간 조회나 feature 탐지 명령을 제공하지 않습니다.'),
        ('분석 범위', '전체 포함과 세 note 생성 줄을 대조했습니다. Linux라는 note 이름과 type 0의 의미, 자료형과 링크 메타데이터의 관계가 핵심입니다. 최종 ELF를 만들어 readelf로 note를 확인한 실행 검증은 포함하지 않았습니다.')
    ],
    questions=[
        ('이 파일의 note description은?', 'LINUX_VERSION_CODE의 .long 값이다', '현재 시각을 나타내는 64비트 카운터이다', '파일은 정적 버전 메타데이터를 만듭니다. type 0과 description의 버전 값을 구분해야 합니다.'),
        ('이 파일은 BUILD_SALT note도 직접 생성하는가?', '아니다. 원본에는 해당 호출이 없다', '그렇다. 모든 아키텍처 note.S가 같은 두 note를 만든다', '실제 파일 내용에 근거해야 합니다. 여기에는 Linux 버전 note 한 개만 명시되어 있습니다.')
    ]
)]
