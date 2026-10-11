"""Whole-file assembler and Rust compiler version probes."""
ROWS = [dict(
    path='scripts/as-version.sh', title='어셈블러 검사: integrated LLVM 우회와 GNU 버전 확인',
    intro='명시적 integrated 옵션, compiler driver를 통한 GNU assembler 탐지와 버전 경계를 분석합니다.',
    principle='도구 체인의 일부는 같은 compiler 버전으로 관리되지만 외부 assembler는 별도 탐지와 검사가 필요합니다.',
    use='shell 함수의 exit, driver 옵션 전달, 접미사 제거 연산과 최소 버전 비교를 학습합니다.',
    area='어셈블러 · compiler driver · 버전 검사 · shell',
    sections=[
        ('전체 구성과 canonical 계산', '#!/bin/sh, GPL-2.0-only 및 set -e 뒤 get_canonical_version은 점으로 나눈 major·minor·patch를 10000*major+100*minor+patch로 합칩니다. 둘째·셋째가 없으면 0이고 넷째부터 무시합니다. 2.35.1.20201116은 23501입니다. 입력 형식을 범용 버전 parser처럼 검증하는 코드는 아닙니다.'),
        ('Integrated assembler 탐지', 'check_integrated_as는 전달된 인수를 하나씩 살피며 정확히 -fintegrated-as를 찾으면 LLVM 0을 출력하고 exit 0합니다. exit는 함수만 반환하는 return과 달리 이 스크립트를 끝냅니다. 실제 Clang을 실행해 기능을 탐지하기 전에 명시 옵션을 신뢰하는 경로입니다. Clang의 기본값을 명령 없이 자동 판별하지 않습니다.'),
        ('LLVM 0의 의미', '주석은 integrated assembler 버전이 Clang 버전과 같고 cc-version.sh에서 이미 검사했다고 설명합니다. 여기서 0은 실제 LLVM release가 0이라는 뜻이 아니라 별도 assembler 버전 검사를 생략하는 출력입니다. Clang이 -fno-integrated-as 없이 -Wa,--version을 처리하지 못한다는 배경 때문에 이 분기를 먼저 둡니다.'),
        ('외부 assembler 호출', 'integrated 경로가 아니면 orig_args를 보존하고 LC_ALL=C "$@" -Wa,--version -c -x assembler-with-cpp /dev/null -o /dev/null을 실행하며 stderr를 숨깁니다. compiler driver를 통해 assembler 옵션을 전달하고 빈 입력을 사용합니다. 입력과 출력 모두 /dev/null이며 커널 전체 코드를 어셈블하는 검사가 아닙니다.'),
        ('첫 줄과 GNU 판별', 'IFS를 newline으로 두어 출력을 분리한 뒤 첫 줄만 공백으로 다시 분리합니다. 첫 두 토큰이 GNU assembler이면 마지막 토큰을 버전으로 취하고 min-tool-version.sh binutils를 조회하며 name=GNU입니다. 아니면 unknown assembler invoked 진단 후 1입니다. 여기서는 다른 이름을 LLVM으로 추정하는 추가 fallback이 없습니다.'),
        ('접미사 제거의 정확한 범위', 'version=${version%-*}는 끝에 일치하는 가장 짧은 하이픈 시작 suffix를 제거합니다. 일반적인 2.34-4.fc32는 2.34가 되지만 2.34-4-extra는 2.34-4가 남습니다. 주석의 배포판 예를 모든 하이픈 뒤 내용 전체 제거로 확대하지 않습니다. ld-version.sh의 숫자·점 이외를 제거하는 %% 패턴과도 다릅니다.'),
        ('최소 검사와 결과', 'actual과 minimum을 수치화해 actual<minimum이면 현재·최소 버전을 담은 오류 블록과 exit 1, 아니면 GNU와 정수 버전을 출력합니다. 동일한 최소 버전은 허용됩니다. set -e가 있지만 명령 치환을 set의 인수로 사용하는 구조까지 고려해야 하며 모든 내부 도구 실패의 완전한 전파를 단정하지 않습니다. 전체 두 함수·탐지·비교·출력을 대조했고 실제 compiler driver 실행은 하지 않았습니다.')
    ], questions=[
        ('-fintegrated-as를 발견한 경우 출력은?', 'LLVM 0', 'GNU 0', '명시 옵션 경로에서 LLVM 0을 출력하고 스크립트를 종료합니다. 실제 release 0을 탐지한 것이 아닙니다.'),
        ('check_integrated_as 안의 exit 0은 어디까지 끝내는가?', '스크립트 실행 전체', '함수만 반환하고 GNU 검사로 계속 진행', 'exit와 return의 범위는 다릅니다. 아래 버전 호출과 최소 검사에 도달하지 않습니다.'),
        ('외부 assembler 버전 요청을 전달하는 옵션은?', '-Wa,--version', '커널 부팅 인수 --version', 'compiler driver에 -Wa로 assembler 인수를 전달합니다. 빈 assembler-with-cpp 입력을 사용합니다.'),
        ('2.34-4-extra에 ${version%-*}를 적용하면?', '2.34-4', '2.34', '단일 %는 가장 짧은 일치 suffix를 제거하므로 마지막 하이픈부터 지워집니다. 주석보다 연산자의 정확한 의미를 확인해야 합니다.')
    ]
), dict(
    path='scripts/rustc-version.sh', title='Rust 버전 정수화: minor 확장 공간과 실행 실패 처리',
    intro='Rust 버전 출력의 두 번째 토큰과 다른 도구보다 넓은 major 가중치를 분석합니다.',
    principle='버전 구성요소에 할당한 자리 수는 미래 minor 값의 증가와 비교 결과에 영향을 줍니다.',
    use='수치 인코딩, 조건식 안의 명령 치환, 실패 sentinel을 학습합니다.',
    area='버전 표현 · shell · 도구 probe',
    sections=[
        ('전체 구조와 목적', '#!/bin/sh, GPL-2.0 파일은 canonical 함수 하나와 compiler 실행의 if/else로 구성됩니다. C compiler 검사 스크립트와 달리 set -e 선언이나 최소 버전 helper 호출이 없습니다. 사용 예는 rustc 명령을 전달하는 것입니다.'),
        ('Major 가중치 차이', 'get_canonical_version은 점 구분자로 나눈 세 필드를 100000*major+100*minor+patch로 합칩니다. C 도구의 10000과 달리 major 가중치가 100000입니다. 주석은 minor가 100에 도달할 것을 고려한 추가 자리라고 설명합니다. 이는 원본 작성 당시의 설계 설명이며 현재 release 일정을 검증한 정보로 읽지 않습니다. 1.78.0은 107800,1.100.0은 110000입니다.'),
        ('명령 실행 성공과 파싱', 'if output=$("$@" --version 2>/dev/null)은 명령 실행의 종료 상태를 직접 조건으로 사용합니다. 성공하면 set -- $output으로 공백 분리하고 두 번째 토큰을 canonical 함수에 전달합니다. 첫 토큰이 정확히 rustc인지 별도 비교하지 않습니다. 여러 단어의 명령을 인수로 전달할 수 있지만 전체 버전 출력 형식을 검증하는 parser는 아닙니다.'),
        ('실패와 지원 범위', '명령 실패는 stdout에 0을 출력하고 exit 1입니다. 성공했더라도 두 번째 토큰의 세 구성요소가 없거나 수치가 아닌 경우에 대한 명시적 보정이나 prerelease suffix 제거가 없습니다. 반환 숫자만으로 최소 지원 조건 통과를 증명하지 않습니다. 모든 본문을 대조했고 실제 Rust compiler를 실행해 확인한 것은 아닙니다.')
    ], questions=[
        ('Rust 1.100.0의 canonical 값은?', '110000', '20000', '100000×1+100×100=110000입니다. C 도구의 major 가중치와 다릅니다.'),
        ('rustc --version 실행이 실패하면?', '0을 출력하고 상태 1로 종료한다', '최소 지원 버전을 대신 출력하며 성공한다', 'else 분기의 sentinel과 오류 상태를 함께 확인해야 합니다.'),
        ('이 스크립트가 최소 Rust 버전과 비교하는가?', '아니다. 버전을 추출해 숫자로 출력한다', '그렇다. min-tool-version.sh를 호출한다', '최소 버전 비교는 이 파일에 없습니다. 도구 probe와 정책 검사를 분리해서 읽습니다.')
    ]
)]
