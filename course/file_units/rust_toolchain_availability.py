"""Whole-file Rust availability checks and the two bindgen probe inputs."""
ROWS = [dict(
    path='scripts/rust_is_available.sh', title='Rust 빌드 가능성 검사: 버전·libclang·core 소스·경고',
    intro='환경 입력부터 compiler·bindgen·libclang 검증과 core 소스 확인까지 모든 경로를 분석합니다.',
    principle='도구 존재, 실행 성공, 버전 적합성, 구성 요소 일치, 라이브러리 소스 존재는 독립된 검증 조건입니다.',
    use='probe 설계, stdout·stderr 분리, 종료 trap, 경고와 실패의 차이를 학습합니다.',
    area='Rust 빌드 · 도구 검증 · shell · 오류 처리 · libclang',
    sections=[
        ('공통 helper와 실행 문맥', '#!/bin/sh, GPL-2.0, set -e를 사용하고 같은 디렉터리 min-tool-version.sh를 참조합니다. get_canonical_version은 100000*major+100*minor+patch로 계산합니다. 이 함수는 rustc뿐 아니라 이 파일의 bindgen·libclang 비교에도 사용됩니다. 주석의 미래 minor 증가 설명은 원본의 설계 배경이며 현재 release 일정 검증이 아닙니다.'),
        ('문서 안내와 EXIT trap', 'print_docs_reference는 Quick Start 문서 경로를 stderr에 출력합니다. print_kbuild_explanation은 Kbuild의 rustavailable target 사용을 안내하고 exit 1합니다. warning=0으로 시작하고 EXIT trap은 종료 상태가 0이 아니거나 warning이 0이 아니면 문서 안내를 출력합니다. 경고가 있다는 이유만으로 이 trap이 명시적으로 exit 1을 실행하지는 않습니다.'),
        ('필수 환경 변수의 존재', 'RUSTC,BINDGEN,CC 각각에 ${변수+x}를 사용해 unset인지 검사합니다. 빈 문자열로 설정한 경우와 unset은 다릅니다. 누락이면 변수 이름 진단과 Kbuild 안내 후 종료합니다. 다음 command -v 검사는 RUSTC와 BINDGEN에만 있으며 CC에 대한 동일한 존재 검사 블록은 여기 없습니다. 도구 발견이 실패하면 진단 후 exit 1입니다.'),
        ('Rust compiler 실행과 형식', 'LC_ALL=C "$RUSTC" --version의 stdout을 저장하고 stderr는 버립니다. 실패 상태는 ||로 별도 code 변수에 기록해 코드·출력을 진단하고 종료합니다. 성공해도 첫 줄에서 rustc와 숫자.숫자.숫자를 추출하지 못하면 형식 오류로 종료합니다. 정규식의 뒤 .* 덕분에 -dev 같은 접미사가 있어도 세 수치 구성요소를 추출할 수 있습니다.'),
        ('Rust compiler 최소 버전', 'min-tool-version.sh rustc의 결과와 실제 버전을 같은 canonical 함수로 바꿔 -lt로 비교합니다. 실제가 작으면 현재·최소 버전을 표시하고 1로 종료합니다. 같거나 크면 다음 검사로 갑니다. 최신 버전을 설치하거나 자동 변경하는 동작은 없습니다.'),
        ('Bindgen 버전 요청과 호환 인수', 'BINDGEN --version 뒤 workaround-for-0.69.0이라는 인수를 추가합니다. 주석은 0.69.0 동작을 지원하는 우회이고 0.69.1에서 수정되었다고 설명합니다. 실행 실패·첫 줄의 bindgen 버전 추출 실패·최소 bindgen 버전 부족을 각각 진단 후 종료합니다. 이 인수는 이 단계에서 실제 커널 헤더 파일 경로를 지정하는 것이 아닙니다.'),
        ('Bindgen 0.66의 실제 probe', 'canonical 값이 6600 또는 6601이면 rust_is_available_bindgen_0_66.h를 bindgen에 입력합니다. stdout은 버리고 실패 시 알려진 문제와 배포판 patch 가능성을 안내하며 warning=1입니다. 즉 이 두 버전은 번호만으로 무조건 실패시키지 않습니다. probe 실패 뒤에도 libclang 등 나머지 검사를 계속합니다.'),
        ('Libclang 진단 캡처의 리다이렉션 순서', 'bindgen에 rust_is_available_bindgen_libclang.h를 주고 2>&1 >/dev/null 순서로 리다이렉션합니다. stderr가 먼저 명령 치환의 기존 stdout으로 연결되고 stdout만 /dev/null로 바뀌므로 진단 출력을 캡처하고 생성된 binding 출력은 버립니다. >/dev/null 2>&1과 같은 결과가 아닙니다. bindgen 실패는 code와 캡처 진단을 출력하고 종료합니다.'),
        ('실제 libclang 버전 판별', '캡처 출력에서 clang version 숫자.숫자.숫자를 sed로 추출합니다. 이 식에는 첫 줄 제한이 없어 여러 줄 진단 중 해당 문구를 찾을 수 있습니다. 추출 결과가 비면 형식 오류, llvm 최소 버전보다 작으면 오래된 libclang 오류입니다. bindgen 실행 파일 버전과 bindgen이 로드한 libclang 버전은 다른 검사항목입니다.'),
        ('C Clang과 libclang 비교', 'cc-version.sh $CC 결과의 첫 필드를 cut으로 읽고 Clang일 때만 $CC --version의 첫 줄에서 버전을 추출합니다. 그것이 libclang의 수치 버전 문자열과 다르면 경고하고 warning=1로 합니다. 다른 compiler일 때는 이 일치 비교를 수행하지 않습니다. suffix와 빌드 전체 fingerprint를 비교하는 검증은 아닙니다. 이 pipeline에 pipefail 설정은 없으므로 앞 도구 실패 전파를 과장하지 않습니다.'),
        ('Rust sysroot와 core 소스', '"$RUSTC" $KRUSTFLAGS --print sysroot로 sysroot를 구합니다. KRUSTFLAGS를 넘기는 이유는 사용자가 --sysroot를 지정할 수 있어서입니다. RUST_LIB_SRC가 비어 있지 않으면 우선하고 아니면 sysroot/lib/rustlib/src/rust/library를 선택합니다. 그 아래 core/src/lib.rs의 -e 존재 검사에 실패하면 경로 진단 후 1입니다. 읽기 가능성이나 core 전체 소스의 완전성을 모두 검사하는 것은 아닙니다.'),
        ('성공과 범위', '마지막 존재 검사를 통과하면 별도의 성공 문구 출력 없이 끝납니다. warning만 있었던 경우 문서 안내를 남기더라도 그 자체를 명시적 실패로 바꾸지 않습니다. 이 검사는 환경 적합성 probe이지 실제 커널 Rust 코드를 전부 빌드한 결과가 아닙니다. 모든 helper·환경 검사·도구 오류 분기·경고·소스 검사와 trap을 원본에 대조했습니다. 이 호스트에서 실제 Rust toolchain을 실행 검증하지는 않았습니다.')
    ], questions=[
        ('필수 변수 검사는 unset과 빈 값 설정을 구분하는가?', '그렇다. ${변수+x}로 존재 여부를 검사한다', '아니다. 둘 다 무조건 누락 처리한다', '빈 값도 설정된 변수입니다. 이후 도구 발견 단계에서 실패할 수 있지만 첫 검사와는 다른 조건입니다.'),
        ('Bindgen 0.66.0이면 즉시 무조건 실패하는가?', '아니다. 보조 헤더 probe 실패도 경고로 기록한다', '그렇다. 버전 번호만으로 exit 1한다', '배포판이 문제를 patch했을 수 있어 실제 probe를 사용합니다. 실패 분기는 warning=1이며 뒤 검사를 계속합니다.'),
        ('2>&1 >/dev/null의 이 호출에서 캡처되는 것은?', 'stderr 진단', '생성된 binding stdout만', 'stderr를 기존 stdout에 먼저 연결한 뒤 stdout을 버립니다. 리다이렉션 순서는 결과를 바꿉니다.'),
        ('libclang 버전 정규식이 첫 줄에만 적용되는가?', '아니다. 줄 주소 1이 없다', '그렇다. rustc 버전 probe와 동일하다', 'pragma 진단이 출력 첫 줄에 없을 수 있어 전체 진단 중 패턴을 찾습니다.'),
        ('C compiler가 Clang이고 libclang 버전과 다르면?', '경고를 기록하고 나머지 검사를 계속한다', '즉시 compiler를 교체한다', 'warning=1만 설정합니다. 도구를 설치하거나 교체하는 명령은 없습니다.'),
        ('RUST_LIB_SRC가 빈 문자열이면 core 소스 기준은?', 'sysroot 아래 기본 library 경로', '현재 디렉터리의 빈 경로', '${변수:-기본값}은 unset과 빈 값 모두 기본값을 사용합니다. 앞 필수 변수의 존재 검사와 다른 확장입니다.'),
        ('core 소스 확인이 실제로 검사하는 것은?', 'core/src/lib.rs 경로의 존재', 'Rust 라이브러리 전체의 빌드 성공', '-e 파일 검사는 전체 source와 compiler 조합의 실행 가능성을 증명하지 않습니다.')
    ]
), dict(
    path='scripts/rust_is_available_bindgen_0_66.h', title='Bindgen 0.66 probe: NUL 문자열 매크로 하나',
    intro='버전별 호환성 문제를 드러내는 최소 입력 파일 전체를 분석합니다.',
    principle='작은 재현 입력은 도구 버전 문자열만으로 알 수 없는 patch 적용 상태를 시험할 수 있습니다.',
    use='C 문자열 escape와 toolchain 기능 probe의 관계를 학습합니다.',
    area='C 문자열 · 최소 재현 입력 · bindgen',
    sections=[
        ('정의 전체', 'GPL-2.0 주석 뒤 A를 NUL escape가 들어 있는 문자열로 정의하는 매크로 한 줄뿐입니다. 함수·include guard·변수 정의는 없습니다. 문자열 안의 명시적 NUL과 C 문자열 끝에 추가되는 종료 문자를 구분해야 하며 매크로 자체가 런타임 명령을 실행하지 않습니다.'),
        ('문자열의 저장 의미', '이 C 문자열을 실제 표현식에 사용하면 명시적 NUL 하나와 암시적 종료 NUL을 담은 char 배열 표현이 됩니다. 문자열 길이와 배열 저장 크기는 다를 수 있다는 예입니다. 다만 이 파일은 매크로 정의만 하므로 반드시 데이터 section에 배열 객체가 생성된다고 주장하지 않습니다.'),
        ('호출 문맥', 'rust_is_available.sh는 bindgen 0.66.0·0.66.1일 때 이 파일을 입력으로 주고 종료 상태를 봅니다. 성공 여부로 해당 문제의 patch 가능성을 구분하며 실패는 경고입니다. 이 파일 자체가 버전을 검사하거나 Rust 코드를 컴파일하지 않습니다. 전체 한 매크로와 주석을 검토했습니다.')
    ], questions=[
        ('이 파일이 도구를 검사하는 방법은?', '자체 검사 대신 bindgen에 줄 최소 입력을 제공한다', 'main 함수에서 compiler 버전을 계산한다', '파일은 매크로 한 줄입니다. probe의 실행과 결과 처리는 상위 shell 스크립트가 담당합니다.'),
        ('명시적 NUL이 든 C 문자열에서 길이와 저장 크기는 같은가?', '아니다. 종료 NUL과 명시적 NUL의 저장 공간을 구분한다', '항상 같다. NUL은 저장되지 않는다', 'C 문자열에는 암시적 종료 문자도 있습니다. 이 매크로를 해석할 때 byte 배열 크기와 문자열 길이를 혼동하지 않습니다.')
    ]
), dict(
    path='scripts/rust_is_available_bindgen_libclang.h', title='Libclang 버전 probe: pragma 진단으로 매크로 노출',
    intro='bindgen이 사용하는 Clang의 버전 문자열을 진단에 내보내는 파일 전체를 분석합니다.',
    principle='전처리 매크로를 진단으로 노출하면 실행 파일의 표시 버전과 실제 로드한 parser 버전을 구별할 수 있습니다.',
    use='pragma message, 인접 문자열, 도구 진단 캡처를 학습합니다.',
    area='전처리 · Clang · pragma · 진단 출력',
    sections=[
        ('전체 구현', 'GPL-2.0 주석과 #pragma message 한 줄로 구성됩니다. clang version이라는 문자열과 __clang_version__을 연결해 진단 메시지로 노출합니다. 사용자 공간 함수나 전역 배열을 정의하는 코드가 아니며 include guard도 없습니다.'),
        ('진단은 실행 중 출력과 다르다', 'pragma는 헤더를 처리하는 도구에 대한 지시입니다. 생성된 커널 프로그램이 부팅하면서 printf로 버전을 출력하는 구현이 아닙니다. __clang_version__이 정의되는 parser를 전제로 하며 이 헤더에는 다른 compiler용 fallback 문자열이 없습니다.'),
        ('진단과 파서 연결', '상위 스크립트가 bindgen으로 이 헤더를 처리할 때 사용하는 libclang의 매크로가 드러납니다. 상위 스크립트는 stderr를 캡처하고 clang version 뒤 수치 3요소를 찾습니다. 진단에 파일명·위치 등 다른 줄이 섞일 수 있어 첫 줄만 보지 않습니다. 이 헤더가 독립적으로 최소 버전을 판정하지는 않습니다. 실제 toolchain 실행 대신 원본과 호출 흐름을 대조했습니다.')
    ], questions=[
        ('이 헤더가 노출하는 버전의 출처는?', '헤더를 처리하는 Clang의 __clang_version__ 매크로', 'Rust compiler의 --version 문자열', 'bindgen 자체 버전과 libclang 버전은 다릅니다. pragma 진단으로 실제 parser의 정보를 얻는 probe입니다.'),
        ('pragma message는 커널 부팅 때 실행되는 출력 함수인가?', '아니다. 헤더를 처리하는 도구의 진단 지시다', '그렇다. printk 호출을 자동 생성한다', '파일에는 런타임 함수 본문이 없습니다. 컴파일 과정의 진단과 실행 중 출력을 구분합니다.')
    ]
)]
