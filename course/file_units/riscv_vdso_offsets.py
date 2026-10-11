"""Whole-file RISC-V offset extraction and symbol address interfaces."""
ROWS = [dict(
    path='arch/riscv/kernel/vdso/gen_vdso_offsets.sh',
    title='RISC-V vDSO offset 생성: 선행 0과 심볼 필터',
    intro='짧은 sed 스크립트의 모든 실행 줄과 입력 계약을 분석합니다.',
    principle='텍스트 변환 도구가 허용하는 주소 표현은 숫자의 의미뿐 아니라 정규식 형식에도 제한됩니다.',
    use='캡처·앵커·반복자를 읽고 실제 nm 파이프라인과 생성 헤더의 관계를 설명합니다.',
    area='셸 · sed · 정규식 · nm · 생성 헤더 · 빌드 계약',
    sections=[
        ('전체 구성', '#!/bin/sh와 GPL-2.0 뒤 LC_ALL=C 대입, sed -n -e 명령 하나가 전부입니다. 파일 인수가 없으므로 stdin을 읽고 stdout에 정의를 출력합니다. 확인한 Makefile이 nm 출력과 이 helper, LC_ALL=C sort를 연결하여 헤더에 저장합니다. 스크립트 자체가 ELF를 열거나 정렬하지 않습니다.'),
        ('주소의 선행 0 조건', '정규식 시작은 ^[0]\\+ 뒤 캡처 (0[0-9a-fA-F]*)입니다. 따라서 앞부분에서 적어도 하나의 0을 소비하고 캡처도 0으로 시작해야 합니다. 합쳐 최소 두 개의 선행 0이 있는 주소 표현을 요구합니다. 모든 임의 길이 16진수 표기를 수용하는 parser가 아니며 고정 폭 nm 출력 문맥을 전제로 읽어야 합니다.'),
        ('심볼과 type 선택', '주소 뒤 공백·임의 한 글자·공백을 기대하고 __vdso_로 시작하는 영문·숫자·밑줄 이름을 캡처합니다. type 자리는 .이므로 T만 검사하지 않습니다. 끝의 $는 후행 텍스트가 있는 줄을 제외합니다. ARM64 스크립트의 VDSO_ 접두어와 다르므로 두 도구를 같은 필터라고 설명하면 안 됩니다.'),
        ('출력 예시', '매칭되면 #define 이름_offset, tab, 0x주소 형태로 치환하고 p로 출력합니다. 예를 들어 0000000000000120 T __vdso_getcpu는 #define __vdso_getcpu_offset 뒤 tab과 0x0120을 생성합니다. -n 때문에 매칭되지 않는 일반 줄은 출력하지 않습니다. 주소에서 불필요한 앞 0을 줄이지만 캡처의 첫 0은 남습니다.'),
        ('문법과 한계', '\\+ 반복자와 치환의 \\t는 사용한 sed가 지원해야 합니다. LC_ALL 대입에는 명시적 export가 없으므로 자식 환경 전달은 기존 export 상태도 고려해야 합니다. 별도 compat 접두어를 붙이는 코드, 중복 제거, 주소 범위 검사, 헤더 guard는 없습니다. 전체 식을 분석했으며 실제 셸 실행과 생성 ELF offset 대조는 수행하지 않았습니다.')
    ],
    questions=[
        ('이 스크립트가 선택하는 심볼 접두어는?', '__vdso_이다', 'VDSO_이다', '두 아키텍처 도구의 필터가 다릅니다. 이 정규식은 __vdso_ 이름을 그대로 캡처하여 뒤에 _offset을 붙입니다.'),
        ('0120 T __vdso_getcpu처럼 선행 0이 하나뿐인 줄은 이 식과 맞는가?', '아니다. 앞 반복 부분과 캡처 시작에 각각 0이 필요하다', '그렇다. 모든 유효 16진수 표기는 허용된다', '^[0]\\+가 한 개 이상을 소비하고 캡처도 0으로 시작합니다. 숫자가 유효하다는 것과 텍스트 패턴에 맞는다는 것은 다릅니다.'),
        ('스크립트 안에서 compat__vdso_ 이름을 생성하는 분기가 있는가?', '없다. 입력 심볼에 _offset을 붙이는 한 식뿐이다', '있다. 실행 CPU가 32비트이면 자동으로 compat를 붙인다', 'runtime CPU 탐지나 인수 분기가 없습니다. compat 변환이 필요하면 별도의 빌드 문맥을 확인해야 합니다.')
    ]
), dict(
    path='arch/riscv/include/asm/vdso.h',
    title='RISC-V vDSO 주소 API: MMU·compat 조건과 생성 offset',
    intro='조건부 상수·매크로·이미지 경계 선언 전체를 분석합니다.',
    principle='주소 계산용 API의 존재 자체도 빌드 설정에 따라 달라지며, 생성된 심볼 offset과 실행 기준 주소가 함께 필요합니다.',
    use='native·compat 이름 결합과 MMU 조건의 범위를 구분합니다.',
    area='가상 메모리 · MMU · ABI 호환성 · 토큰 결합 · 주소 산술',
    sections=[
        ('전체 MMU 조건', 'GPL-2.0-only include guard 안에서 CONFIG_MMU가 정의되어야 내용이 제공됩니다. 주석은 MMU 없는 시스템에서 공유 라이브러리와 vDSO를 지원하지 않는다고 설명합니다. __VVAR_PAGES=2도 이 조건 안이지만 !__ASSEMBLY__보다 앞입니다. 따라서 MMU가 꺼지면 이 헤더가 그 상수를 제공하지 않습니다.'),
        ('Native 주소 매크로', 'C 구역은 generated/vdso-offsets.h를 포함하고 VDSO_SYMBOL(base,name)을 (void __user *)((unsigned long)base+__vdso_##name##_offset)로 정의합니다. name은 runtime 문자열이 아니라 토큰 결합에 쓰입니다. base 식은 한 번 나타나며 결과 주소를 역참조하지 않습니다. offset=0x120, base=0x70000000이면 주소는 0x70000120입니다.'),
        ('Compat 분기', 'CONFIG_COMPAT이면 generated/compat_vdso-offsets.h를 추가 포함하고 COMPAT_VDSO_SYMBOL은 compat__vdso_##name##_offset을 사용합니다. compat_vdso_start·compat_vdso_end 외부 char 배열도 이 안에 선언합니다. 기본 offset에 이름만 다르게 붙여도 같은 이미지라고 가정하면 안 됩니다. 별도의 생성 헤더와 이미지 경계입니다.'),
        ('기본 이미지 경계와 사용자 주소', 'vdso_start·vdso_end 외부 char 배열은 compat 조건 밖이지만 C와 MMU 조건 안입니다. 배열 선언 자체가 이미지를 생성하지는 않습니다. void __user *는 사용자 주소 공간의 포인터라는 코드 계약을 나타내며 주소 범위 검사나 fault 복구를 자동 수행하는 연산은 아닙니다.'),
        ('범위와 CS 연결', '모든 조건·상수·생성 헤더·매크로·외부 선언을 설명했습니다. MMU 기반 주소 공간, native와 compat 이미지 구분, 생성 offset과 실제 매핑 기준의 합이 핵심입니다. 이 파일에 페이지 매핑·ASLR 선택·사용자 포인터 유효성 검사는 없으며 실제 매핑 실행 검증은 수행하지 않았습니다.')
    ],
    questions=[
        ('CONFIG_MMU가 없으면 __VVAR_PAGES=2를 이 헤더에서 제공하는가?', '아니다. 해당 정의도 CONFIG_MMU 안에 있다', '그렇다. 모든 빌드에서 항상 정의된다', 'include guard뿐 아니라 내부 설정 조건의 범위를 확인해야 합니다.'),
        ('COMPAT_VDSO_SYMBOL이 사용하는 offset 이름은?', 'compat__vdso_이름_offset이다', '항상 native의 __vdso_이름_offset이다', 'compat 전용 생성 헤더와 매크로를 사용합니다. 두 이미지의 offset이 언제나 같다고 가정할 수 없습니다.'),
        ('VDSO_SYMBOL은 계산한 주소의 내용을 읽는가?', '아니다. 기준 주소와 offset의 합을 포인터로 반환한다', '그렇다. 함수 코드를 즉시 실행한다', '주소 계산, 역참조, 함수 실행은 별개입니다. 이 매크로에는 메모리 읽기나 호출 연산이 없습니다.')
    ]
)]
