"""Whole-file build counter and compile metadata shell scripts."""
ROWS = [dict(
    path='scripts/build-version', title='빌드 회차 스크립트: .version 증가·fallback·출력',
    intro='짧은 shell 스크립트 전체의 명령 연결과 파일 쓰기 오류 범위를 분석합니다.',
    principle='shell의 논리 연결은 계산값뿐 아니라 각 명령의 종료 상태에 따라 분기합니다.',
    use='명령 치환, &&와 ||, expr의 종료 상태, 지속 파일과 stdout을 구별합니다.',
    area='POSIX shell · 종료 상태 · 파일 지속성 · 경쟁 조건',
    sections=[
        ('전체 구성과 작업 디렉터리', '#!/bin/sh와 GPL-2.0-only 뒤 세 명령 묶음이 있습니다. .version은 스크립트 파일의 디렉터리가 아니라 실행하는 현재 작업 디렉터리의 상대 경로입니다. 인수나 KBUILD_BUILD_VERSION을 이 스크립트에서 직접 읽지 않습니다. 호출하는 init/Makefile이 사용자 지정 값과 자동 생성 값의 우선순위를 정합니다.'),
        ('이전 값 읽기와 단락 평가', 'prev_ver=$(cat .version 2>/dev/null)가 성공해야 && 뒤 expr를 실행합니다. cat의 진단은 버리지만 stdout은 변수로 받습니다. 파일이 없거나 읽지 못하면 || 뒤 ver=1로 갑니다. 명령 치환은 끝의 newline을 제거하며 유효한 숫자인지는 다음 expr가 판단합니다.'),
        ('숫자 증가와 expr 상태', 'ver=$(expr ${prev_ver} + 1 2>/dev/null)의 종료 상태가 성공이면 계산값을 사용하고 실패면 ver=1로 덮습니다. 예를 들어 기존 7은 8, 숫자가 아닌 값은 보통 fallback 1입니다. expr는 결과 0도 실패 상태로 반환하므로 기존 -1에서 산술 결과가 0이어도 최종 ver는 1입니다. 단순히 모든 정수를 수학적으로 1씩 증가시키는 계약이 아닙니다. prev_ver 확장은 따옴표가 없고 숫자용 내부 파일이라는 전제에 의존합니다.'),
        ('파일 갱신과 stdout은 별도', 'echo ${ver} > .version으로 기존 파일을 덮고 다음 echo ${ver}로 stdout에 출력합니다. 임시 파일 후 rename, file lock, fsync는 없습니다. 동시 호출이 같은 이전 값을 읽으면 동일한 다음 번호를 만들 수 있으므로 다중 프로세스에 대한 원자적 counter라고 할 수 없습니다.'),
        ('쓰기 실패와 최종 상태', '스크립트에는 set -e나 파일 쓰기 뒤의 명시적 오류 분기가 없습니다. .version 쓰기가 실패해도 마지막 stdout echo가 실행될 수 있고 그 성공 상태로 끝날 수 있습니다. 따라서 번호를 출력했다는 사실만으로 파일 갱신 성공을 증명하지 않습니다. 전체 제어 흐름을 검토했으며 프로젝트의 실제 .version을 변경하며 실행한 것은 아닙니다.')
    ], questions=[
        ('.version 파일이 없으면 생성하려는 번호는?', '1', '0', 'cat 실패로 증가 명령을 건너뛰고 || ver=1이 실행됩니다. 이어 파일과 stdout으로 값을 내보냅니다.'),
        ('이전 값이 -1이면 최종 출력값은?', '1', '0', 'expr의 계산 결과 0은 실패 종료 상태이므로 ||의 fallback이 ver를 1로 바꿉니다. 산술 결과와 shell 종료 상태를 함께 읽어야 합니다.'),
        ('동시에 두 번 실행하면 반드시 서로 다른 번호가 나오는가?', '아니다. 읽기와 쓰기 사이를 보호하는 lock이 없다', '그렇다. echo 리다이렉션이 전체 절차를 원자화한다', '각 실행이 같은 이전 값을 읽고 같은 다음 값을 쓸 수 있습니다. 파일 쓰기 한 번과 read-modify-write 전체의 원자성은 다릅니다.'),
        ('번호 stdout 출력이 성공하면 .version 갱신도 증명되는가?', '아니다. 쓰기 실패 뒤에도 마지막 echo가 성공할 수 있다', '그렇다. 파일 쓰기와 출력이 하나의 명령이다', '두 echo는 독립된 줄입니다. set -e와 명시적 상태 검사도 없어 최종 성공만으로 지속 상태를 보장하지 않습니다.')
    ]
), dict(
    path='scripts/mkcompile_h', title='compile.h 생성기: 빌드 사용자·호스트·도구 버전',
    intro='세 인수, 환경 변수 우선순위, linker 출력 가공과 네 매크로 출력을 모두 분석합니다.',
    principle='빌드 메타데이터는 명시적 입력과 실행 환경 탐지 결과를 조합하며 문자열 가공의 범위를 정확히 이해해야 합니다.',
    use='shell 변수, pipeline, locale, C 문자열 생성과 재현 가능한 입력을 학습합니다.',
    area='빌드 메타데이터 · shell pipeline · 환경 변수 · 문자열 생성',
    sections=[
        ('인수 계약과 호출부', '#!/bin/sh, GPL-2.0 뒤 UTS_MACHINE=$1, CC_VERSION="$2", LD=$3으로 세 인수를 받습니다. 확인한 최상위 Makefile의 filechk_compile.h는 UTS_MACHINE,CONFIG_CC_VERSION_TEXT,LD를 각각 인수로 전달합니다. 스크립트는 컴파일러 실행 파일에 --version을 호출하지 않고 이미 전달된 compiler 문자열을 사용합니다. 인수 개수 검사도 없습니다.'),
        ('빌드 사용자 선택', 'KBUILD_BUILD_USER가 빈 문자열이면 whoami 출력을 sed로 가공하고 아니면 환경 변수 값을 그대로 LINUX_COMPILE_BY로 사용합니다. sed 식은 백슬래시 하나를 두 개로 바꾸며 g flag가 없으므로 각 줄의 첫 일치만 치환합니다. 모든 C 문자열 특수문자나 모든 백슬래시를 완전히 escape하는 일반 인코더는 아닙니다. 사용자 지정 경로에는 이 sed도 적용하지 않습니다.'),
        ('빌드 호스트 선택', 'KBUILD_BUILD_HOST가 비면 uname -n 명령 치환으로 LINUX_COMPILE_HOST를 얻고 아니면 제공 값을 사용합니다. 이는 빌드를 실행하는 환경의 호스트 정보이며 만들어진 커널이 부팅될 때의 hostname을 조회하는 코드가 아닙니다. 빈 값은 기본 탐지를 선택하고 비어 있지 않은 값은 우선합니다.'),
        ('Linker 버전 처리', 'LD_VERSION은 LC_ALL=C $LD -v의 stdout에서 head -n1로 첫 줄만 고른 뒤 sed를 적용합니다. 첫 번째 compatible with 괄호 구역을 제거하고 줄 끝 공백을 제거합니다. 중간 공백을 모두 정규화하는 식은 아닙니다. $LD는 따옴표 없이 명령 위치에서 확장되므로 단일 경로뿐 아니라 단어 분리의 영향을 받는 입력이며 임의 문자열에 대한 안전한 shell quoting helper라고 설명하지 않습니다.'),
        ('Locale와 pipeline 상태 범위', 'LC_ALL=C 지정은 linker 명령 앞에 있으며 이 한 줄의 모든 후속 도구나 전체 빌드에 전역 export하는 문장이 아닙니다. 스크립트에는 set -e나 pipefail 설정이 없고 linker 실패를 별도로 검사하지 않습니다. linker 탐지 실패가 있어도 뒤 heredoc 출력이 진행될 수 있으므로 출력 생성만으로 도구 실행 성공을 인증하지 않습니다.'),
        ('네 C 매크로 출력', 'cat의 확장되는 heredoc으로 UTS_MACHINE,LINUX_COMPILE_BY,LINUX_COMPILE_HOST,LINUX_COMPILER 네 #define을 stdout에 출력합니다. COMPILER 문자열은 CC_VERSION, 쉼표와 공백, LD_VERSION을 연결합니다. 스크립트가 compile.h 경로를 직접 열거나 변경 여부를 비교하지는 않습니다. 실제 생성 파일 처리는 Makefile의 filechk 호출 문맥에서 이루어집니다.'),
        ('입력과 검토 범위', '이 스크립트에는 timestamp나 .version 증가 로직이 없습니다. 사용자·호스트를 명시하면 환경 의존 부분을 줄일 수 있지만 모든 빌드 산출물의 재현성을 이 둘만으로 보장하지 않습니다. 세 인수와 두 환경 분기, 버전 pipeline, heredoc 전체를 원본과 대조했으며 현재 호스트의 linker를 실제로 호출한 검증은 아닙니다.')
    ], questions=[
        ('컴파일러 버전 문자열의 출처는?', '두 번째 인수 CC_VERSION', '스크립트 내부의 gcc --version 호출', '스크립트는 compiler 버전을 인수로 받으며 별도로 실행하는 버전 조회는 LD -v입니다.'),
        ('KBUILD_BUILD_USER가 비어 있지 않으면 whoami를 쓰는가?', '아니다. 지정 값을 그대로 사용한다', '그렇다. 지정 값은 항상 무시된다', 'test -z가 false이면 else에서 환경 변수 값을 선택합니다. 이 경로에는 sed 가공도 없습니다.'),
        ('백슬래시 처리 sed가 모든 일치를 치환하는가?', '아니다. g flag가 없어 줄마다 첫 일치만 처리한다', '그렇다. 모든 C escape를 자동 처리한다', '정규식 치환 범위와 문자열 전체의 올바른 C 인코딩은 별개입니다. 이 스크립트의 처리 범위를 과장하면 안 됩니다.'),
        ('이 스크립트는 compile.h 파일에 직접 쓰는가?', '아니다. 매크로를 stdout으로 출력한다', '그렇다. 절대 경로 compile.h를 직접 연다', '마지막 명령은 cat heredoc이며 파일 리다이렉션이 없습니다. 호출하는 빌드 규칙이 출력 파일을 관리합니다.')
    ]
)]
