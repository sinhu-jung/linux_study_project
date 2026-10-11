"""Whole-file compiler/linker detection and pinned minimum tool versions."""
ROWS = [dict(
    path='scripts/cc-version.sh', title='C 컴파일러 판별: 전처리 매크로와 수치 버전 비교',
    intro='컴파일러 탐지, 버전 정규화, 최소 버전 조회와 실패 출력 전체를 분석합니다.',
    principle='호환 매크로를 제공하는 도구는 판별 순서가 중요하며 버전 비교에는 문자열 순서 대신 정규화한 수치를 사용할 수 있습니다.',
    use='전처리 probe, 여러 단어의 명령 전달, shell 인수 재설정과 버전 인코딩을 학습합니다.',
    area='컴파일러 · 전처리 · 버전 비교 · shell',
    sections=[
        ('입력과 probe', '#!/bin/sh, GPL-2.0와 set -e 뒤 get_c_compiler_info를 정의합니다. heredoc의 C 전처리 코드를 "$@" -E -P -x c -에 pipe로 전달하며 도구 stderr를 버립니다. -E는 전처리, -P는 line marker 억제, -x c와 마지막 -는 stdin C 입력을 지정합니다. 실행 가능한 커널 프로그램을 빌드·실행하는 probe가 아닙니다.'),
        ('Clang 우선 검사', '먼저 __clang__을 검사해 Clang과 major,minor,patchlevel을 출력하고 그 다음 __GNUC__이면 GCC와 세 버전 매크로를 출력합니다. 둘 다 없으면 unknown입니다. Clang이 GCC 호환 매크로를 제공할 수 있으므로 순서를 뒤집으면 판별이 달라질 수 있습니다. --version 문자열의 배포판 표기를 직접 파싱하지 않습니다.'),
        ('원래 명령과 새 위치 인수', 'orig_args에 원래 인수 표현을 저장한 뒤 probe 출력을 set --로 분리해 name=$1로 읽습니다. "$@"를 사용하므로 ccache와 gcc처럼 여러 단어로 전달한 명령을 호출할 수 있습니다. 하나의 문자열을 eval하는 구조가 아닙니다. 명령 치환을 set의 인수로 사용하는 코드이므로 set -e 선언만으로 모든 probe 실패를 즉시 전파한다고 확대하지 않습니다.'),
        ('최소 버전 선택과 알 수 없는 도구', '스크립트 dirname 경로의 min-tool-version.sh를 호출합니다. GCC는 gcc 기준, Clang은 llvm 기준을 얻고 version=$2.$3.$4를 만듭니다. 다른 name이면 원래 명령과 unknown C compiler 진단을 stderr에 쓰고 exit 1입니다. 실제 컴파일러 지원 판단과 이 두 이름에 대한 매크로 판별 범위를 구분합니다.'),
        ('수치 버전 표현', 'get_canonical_version은 IFS=.으로 세 구성요소를 분리해 10000*major+100*minor+patch를 출력합니다. 13.0.1은 130001,5.1.0은 50100입니다. 이름상 5·6자리라는 설명은 해당 도구 버전 범위의 관례이며 출력 폭을 printf로 강제하지 않습니다. compiler probe는 세 필드를 제공한다는 계약이고 여기에는 linker helper처럼 누락 필드 기본값 처리가 없습니다.'),
        ('경계 비교와 반환', '실제 수치가 최소 수치보다 작으면 현재·최소 버전을 포함한 오류 블록을 stderr에 출력하고 1로 끝납니다. 같은 값은 허용합니다. 통과하면 name과 canonical version을 공백으로 구분해 stdout에 출력합니다. 이 probe는 모든 kernel 설정의 컴파일 성공을 검증하는 전체 빌드가 아닙니다. 모든 함수·분기·출력을 대조했습니다.')
    ], questions=[
        ('Clang 검사를 GCC 매크로보다 먼저 하는 이유는?', 'Clang도 GCC 호환 매크로를 제공할 수 있기 때문이다', 'GCC는 C 전처리를 지원하지 않기 때문이다', '호환성 매크로 때문에 더 구체적인 식별을 먼저 합니다. __GNUC__ 존재만으로 GCC라고 결론내리면 안 됩니다.'),
        ('13.0.1의 canonical 값은?', '130001', '1301', '10000×13+100×0+1입니다. 단순 문자열 연결이나 pahole probe의 방식과 다릅니다.'),
        ('현재 버전이 최소 버전과 같으면?', '통과한다', '반드시 실패한다', '조건은 -lt입니다. 경계값은 거부하지 않습니다.'),
        ('이 probe가 컴파일러에 전달하는 주요 작업은?', 'stdin C 코드의 전처리', '완성한 커널 이미지의 실행', '-E -P -x c -로 버전 매크로를 얻습니다. cross compiler로 빌드한 프로그램을 호스트에서 실행할 필요가 없습니다.')
    ]
), dict(
    path='scripts/ld-version.sh', title='링커 판별: GNU BFD·LLD·gold와 버전 문자열 정리',
    intro='첫 버전 출력 줄의 파싱, 도구별 분기와 숫자 정규화 전체를 분석합니다.',
    principle='텍스트 기반 도구 탐지는 지원하는 출력 형식을 명시하고 누락·접미 표기 규칙을 별도로 처리해야 합니다.',
    use='IFS 변경, 토큰 이동, shell 패턴 제거와 버전 비교를 학습합니다.',
    area='링커 · shell parsing · 버전 정규화 · 도구 호환성',
    sections=[
        ('전체 입력과 첫 줄', '#!/bin/sh, GPL-2.0와 set -e를 사용합니다. orig_args를 보존한 뒤 IFS를 newline으로 바꾸고 LC_ALL=C "$@" --version의 출력을 위치 인수로 분리합니다. 이후 IFS를 공백으로 바꾸어 첫 줄인 $1을 다시 분리합니다. 전체 출력 모든 줄에서 무작정 LLD를 검색하는 구조가 아닙니다. command substitution과 set의 종료 상태를 구분해야 합니다.'),
        ('GNU BFD와 gold', '첫 두 토큰이 GNU ld이면 마지막 토큰을 version으로 고르고 binutils 최소 버전, 출력 name=BFD,표시 이름 GNU ld를 설정합니다. GNU gold이면 커널 본체 링크를 지원하지 않는다는 진단을 출력하고 1로 종료합니다. gold가 binutils 계열이라는 이유만으로 BFD와 동일한 지원 경로로 진행하지 않습니다.'),
        ('LLD 토큰 탐색', '나머지 경로는 인수가 하나보다 많고 첫 토큰이 LLD가 아닐 동안 shift합니다. LLD를 찾으면 바로 다음 토큰을 version으로 쓰고 llvm 최소 버전을 조회합니다. 찾지 못하면 원래 명령과 unknown linker를 stderr에 쓰고 1입니다. 앞에 배포판 이름 등이 붙은 첫 줄에서도 LLD 토큰을 찾을 수 있지만 임의 출력 형식 전체를 이해하는 parser는 아닙니다.'),
        ('배포판 접미사 제거', 'version에서 숫자와 점이 아닌 첫 문자부터 뒤를 제거하는 %% 패턴을 사용합니다. 2.34-4.fc32는 2.34처럼 정리됩니다. 처음부터 숫자가 아닌 형식이면 빈 값이 될 수 있으며 별도의 풍부한 형식 검증은 없습니다. 부호나 prerelease 우선순위를 해석하는 semantic version 라이브러리가 아닙니다.'),
        ('누락 구성요소와 추가 날짜', 'get_canonical_version은 점으로 분리한 뒤 10000*첫째+100*둘째+셋째를 계산합니다. 둘째·셋째가 없거나 비면 0을 쓰고 넷째부터 무시합니다. 2.35.1.20201116은 23501,2.35는 23500입니다. 첫 구성요소까지 임의 기본값으로 교체하는 코드는 아닙니다.'),
        ('최소 버전과 출력', '실제와 최소 canonical 값을 -lt로 비교해 오래되면 현재·최소 버전 진단 후 1, 아니면 BFD 또는 LLD와 정수값을 출력합니다. 최소값은 같은 디렉터리의 min-tool-version.sh가 제공합니다. 여기서 설치된 linker를 업그레이드하거나 선택을 자동 변경하지 않습니다. 함수·세 도구 분기·정리·검사를 모두 대조했으며 도구별 실행 검증은 하지 않았습니다.')
    ], questions=[
        ('GNU gold 버전이 매우 높아도 이 스크립트는?', '지원하지 않는다고 종료한다', 'BFD로 이름을 바꿔 항상 통과시킨다', 'GNU gold는 버전 비교 전에 별도 거부 분기입니다. 도구 종류 지원과 최소 버전은 다른 조건입니다.'),
        ('2.35.1.20201116의 canonical 값은?', '23501', '2350120201116', '네 번째 snapshot 날짜 필드를 무시합니다. major·minor·patch 세 필드만 수치화합니다.'),
        ('2.34-4.fc32의 버전 비교 대상은?', '2.34', '4.fc32', '숫자·점이 아닌 첫 문자부터 뒤를 제거합니다. 배포판 package release를 kernel 최소 linker 버전의 patch로 쓰지 않습니다.'),
        ('LLD 검색 대상은?', '첫 --version 출력 줄의 공백 토큰', '파일시스템의 모든 linker 바이너리', 'newline으로 분리한 첫 줄만 다시 토큰화합니다. 도구 검색이나 설치 목록 탐색이 아닙니다.')
    ]
), dict(
    path='scripts/min-tool-version.sh', title='Linux v6.12 최소 도구 버전 표: 아키텍처별 예외',
    intro='지원 도구 다섯 종류와 ARCH·SRCARCH 조건, 오류 처리를 전체 분석합니다.',
    principle='최소 지원 버전은 고정 소스 버전과 대상 아키텍처의 정책이며 현재 설치된 도구 버전과 다릅니다.',
    use='case dispatch, 입력 개수 검사와 아키텍처별 빌드 제약을 학습합니다.',
    area='빌드 정책 · 버전 요구사항 · 조건부 분기',
    sections=[
        ('입력 개수와 범위', '#!/bin/sh, GPL-2.0-only와 set -e 뒤 인수 개수가 정확히 1인지 확인합니다. 아니면 usage를 stderr에 출력하고 1입니다. 주석은 최소 버전을 올릴 때 Documentation/process/changes.rst도 갱신하라고 설명합니다. 아래 숫자는 이 고정 Linux v6.12 원본의 정책이며 현재 최신 커널의 요구사항이라고 일반화하지 않습니다.'),
        ('Binutils와 GCC', 'binutils는 2.25.0을 출력합니다. gcc는 ARCH가 정확히 parisc64이면 12.0.0, 그 외에는 5.1.0입니다. gcc 분기는 SRCARCH가 아니라 ARCH를 읽습니다. 실제 gcc를 실행하거나 설치 여부를 검사하지 않습니다.'),
        ('LLVM의 세 경로', 'llvm은 SRCARCH=s390이면 15.0.0,loongarch이면 18.0.0,그 외에는 13.0.1입니다. 두 조건은 if/elif/else이며 다른 아키텍처에 첫 예외를 적용하지 않습니다. 이 llvm 기준을 cc-version과 ld-version이 각각 Clang·LLD에 사용합니다.'),
        ('Rust와 bindgen·알 수 없는 이름', 'rustc는 1.78.0,bindgen은 0.65.1을 출력합니다. 나머지 이름은 unknown tool 진단 후 1입니다. 출력은 점으로 구분된 버전 문자열이고 여기서 canonical 정수로 바꾸지 않습니다. 다섯 case와 두 아키텍처 분기를 모두 검토했으며 실제 toolchain 설치 상태를 확인한 자료는 아닙니다.')
    ], questions=[
        ('GCC의 parisc64 예외는 어떤 변수를 검사하는가?', 'ARCH', 'SRCARCH', 'GCC 분기는 ARCH를 사용하지만 LLVM 분기는 SRCARCH를 사용합니다. 비슷한 변수명을 구분해야 합니다.'),
        ('이 원본에서 loongarch LLVM 최소 버전은?', '18.0.0', '모든 아키텍처와 동일한 13.0.1', 'SRCARCH=loongarch의 별도 elif 분기가 있습니다. 이 답은 v6.12 고정 원본 기준입니다.'),
        ('지원 도구 이름을 주면 이 스크립트가 직접 확인하는 것은?', '요구 최소값을 선택해 출력한다', '도구를 실행해 현재 버전과 비교한다', '현재 버전 probe는 다른 스크립트가 수행합니다. 이 파일은 정책 값을 제공하는 역할입니다.')
    ]
)]
