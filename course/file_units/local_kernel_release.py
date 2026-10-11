"""Whole-file kernel release suffix generation from files, config and Git."""
ROWS = [dict(
    path='scripts/setlocalversion', title='커널 release 생성: localversion·태그·Git 상태의 우선순위',
    intro='인수 처리, 파일 수집, 태그 선택, SCM suffix와 최종 문자열 조합 전체를 분석합니다.',
    principle='같은 출력 문자열도 입력의 존재 여부, 값의 공백 여부, 버전 관리 상태에 따라 서로 다른 경로로 만들어집니다.',
    use='shell parameter expansion, 태그 기반 버전 산정, 읽기 전용 Git 조회와 설정 우선순위를 학습합니다.',
    area='빌드 시스템 · Git · shell 분기 · 문자열 조합 · 재현 가능한 입력',
    sections=[
        ('실행 인수와 오류', '#!/bin/sh, GPL-2.0 스크립트는 처음 인수가 --no-local일 때만 그 옵션을 처리하고 선택적 srctree를 읽습니다. 기본 srctree는 현재 디렉터리입니다. 남는 인수가 있거나 srctree가 디렉터리가 아니면 usage를 stderr에 출력하고 1로 종료합니다. 일반적인 순서 무관 옵션 parser가 아닙니다. KERNELVERSION이 비어 있어도 별도 진단 후 1로 종료합니다.'),
        ('Localversion 파일 수집', 'collect_files는 전달된 경로들을 순서대로 처리합니다. 경로에 ~ 문자가 포함되면 건너뛰고 존재하면 cat의 출력을 res 뒤에 구분자 없이 붙입니다. 명령 치환은 파일 내용 끝의 newline을 제거합니다. regular file 여부를 따로 검사하지 않으며 cat 오류를 명시적으로 중단시키는 코드도 없습니다. 먼저 빌드 디렉터리 localversion*, srctree가 -ef 비교로 같은 디렉터리가 아니면 소스 쪽 localversion*를 뒤에 붙입니다.'),
        ('SCM 함수의 위치와 옵션', 'scm_version은 --short와 --no-dirty를 순회하며 bool 변수에 저장하고 srctree로 cd합니다. git rev-parse --show-cdup 결과가 비어 있지 않으면 저장소 최상위가 아니므로 반환합니다. 이어 HEAD 확인이 실패해도 출력 없이 반환합니다. 실제 호출은 명령 치환 안에 있으므로 함수의 cd가 바깥 스크립트 작업 디렉터리를 바꾸는 것으로 해석하지 않습니다. cd 자체의 실패를 검사하는 명시 분기는 없습니다.'),
        ('커널 번호에서 기본 태그로', 'version_tag는 KERNELVERSION 앞에 v를 붙이되 정규식으로 major.minor 뒤의 .0을 제거합니다. 6.2.0-rc5는 v6.2-rc5, 6.1.7은 v6.1.7입니다. 임의 위치의 모든 .0을 제거하는 치환이 아닙니다. 기본 태그를 찾는 기준과 최종 출력 KERNELVERSION 문자열은 구분합니다.'),
        ('세 단계 태그 선택', 'file_localversion에서 선두 - 하나를 제거한 값을 첫 tag 후보로 삼고 git describe --match로 조회합니다. desc가 없고 file_localversion이 있으면 version_tag+file_localversion을 두 번째 후보로 씁니다. 그래도 없으면 version_tag를 사용합니다. --tags 옵션을 추가하지 않으므로 일반적으로 annotated 태그를 대상으로 하는 describe 경로입니다. 첫 후보는 linux-next, 두 번째는 linux-rt를 예로 드는 주석이 있습니다. 파일 suffix가 단지 출력에만 쓰이는 것이 아니라 태그 선택에도 영향을 줍니다.'),
        ('정확한 태그와 긴 suffix', '선택한 tag와 desc가 같으면 해당 커밋 자체이므로 커밋 수와 hash suffix를 붙이지 않습니다. 다르면 short 모드일 때 즉시 +를 출력하고 반환합니다. 긴 모드에서는 desc가 있을 때 하이픈으로 분리한 뒤 끝에서 두 번째 필드를 커밋 수로 써 -%05d로 출력합니다. 최소 다섯 자리 zero padding이지 큰 수를 다섯 자리로 잘라내는 규칙은 아닙니다. 이어 -g와 HEAD의 앞 12글자를 붙입니다. desc가 없어도 HEAD가 있으면 -g suffix는 남습니다.'),
        ('Dirty 검사의 순서와 범위', 'no_dirty이면 변경 상태 검사 전에 반환합니다. 아니면 git --no-optional-locks status -uno --porcelain을 사용하고 실패 시 git diff-index --name-only HEAD로 fallback합니다. 둘 중 출력 한 줄을 read가 읽으면 -dirty를 붙입니다. -uno이므로 untracked 파일만 생긴 경우는 status 결과에서 제외됩니다. 주석은 소스 트리에 쓰기 시도를 피하려는 이유와 diff-index가 index를 refresh하지 않아 부정확할 수 있음을 설명합니다.'),
        ('Short 모드의 중요한 예외', 'short는 태그와 desc가 다를 때만 + 후 조기 반환합니다. 정확한 태그에서는 그 분기를 건너뛰어 no_dirty가 아니면 dirty 검사까지 진행합니다. 따라서 --short의 결과가 언제나 빈 문자열 또는 + 둘뿐이라고 설명하면 안 됩니다. 정확한 태그이지만 tracked 변경이 있으면 이 코드에서는 -dirty가 나올 수 있습니다.'),
        ('No-local 조기 출력', '--no-local이면 KERNELVERSION과 scm_version --no-dirty만 출력하고 0으로 종료합니다. 이 분기는 include/config/auto.conf 존재 검사보다 앞입니다. 파일 suffix 자체·CONFIG_LOCALVERSION·LOCALVERSION을 출력에 더하지 않고 dirty도 생략합니다. 다만 앞에서 수집한 file_localversion은 SCM 함수의 태그 후보 선택에는 여전히 쓰입니다. 모든 localversion 파일의 영향을 완전히 제거한다고 설명하면 안 됩니다.'),
        ('일반 모드의 설정 읽기', '일반 모드에서는 include/config/auto.conf가 없으면 make prepare 안내를 stderr에 출력하고 1로 끝납니다. CONFIG_LOCALVERSION= 뒤의 전체 나머지를 sed로 추출합니다. 이 코드 자체에는 따옴표를 별도로 제거하는 후처리가 없습니다. auto.conf는 작업 디렉터리 기준이며 srctree 아래의 임의 config를 자동 선택하지 않습니다.'),
        ('AUTO와 환경 변수의 존재 여부', 'auto.conf에 정확히 CONFIG_LOCALVERSION_AUTO=y 줄이 있으면 scm_version의 긴 출력을 사용합니다. 아니면 LOCALVERSION이 아예 unset일 때만 --short를 호출합니다. ${LOCALVERSION+set} 검사이므로 빈 문자열로 설정해도 unset과 다릅니다. AUTO가 켜진 경우에는 LOCALVERSION을 빈 값으로 설정했다고 SCM suffix가 꺼지지 않습니다. 일반적인 비AUTO 경로에서만 이 존재 여부 조건이 적용됩니다.'),
        ('최종 조합과 검토 범위', '최종 출력 순서는 KERNELVERSION+file_localversion+config_localversion+LOCALVERSION+scm_version이며 자동 구분자를 추가하지 않습니다. 각 입력에 필요한 - 등을 포함하는 계약입니다. 같은 이름 scm_version은 함수 호출 위치에서는 함수, ${scm_version}에서는 변수 값으로 사용됩니다. 인수·함수 두 개·모든 조기 종료·최종 분기를 원본과 대조했습니다. 실제 Git 상태별 실행 검증이나 소스 변경을 수행한 것은 아닙니다.')
    ], questions=[
        ('KERNELVERSION=6.2.0-rc5의 기본 태그 후보는?', 'v6.2-rc5', 'v6.2.0-rc5.0', '정규식이 major.minor 다음 .0을 제거하고 v를 붙입니다. 최종 출력의 원래 KERNELVERSION을 수정하는 대입은 아닙니다.'),
        ('Localversion 파일 내용을 여러 개 읽을 때 사이에 무엇을 자동 추가하는가?', '아무 구분자도 추가하지 않는다', '항상 하이픈 하나', 'res 뒤에 각 cat 결과를 직접 붙입니다. suffix 자체의 구분자는 파일 내용에서 제공해야 합니다.'),
        ('AUTO가 꺼져 있을 때 LOCALVERSION unset과 빈 문자열 설정은 같은가?', '아니다. unset일 때만 short SCM 조회를 한다', '그렇다. 둘 다 무조건 +를 붙인다', '${LOCALVERSION+set}은 변수의 존재 여부를 구분합니다. 빈 값으로 설정한 경우에도 set으로 평가됩니다.'),
        ('--short이고 정확한 태그에 tracked 변경이 있으면 가능한 suffix는?', '-dirty', '반드시 + 하나', '정확한 태그에서는 + 조기 반환 조건을 지나지 않습니다. 이후 dirty 검사로 진행할 수 있습니다.'),
        ('status가 정상 동작할 때 untracked 파일만 있으면 dirty로 잡히는가?', '아니다. -uno로 제외한다', '그렇다. 모든 미추적 파일을 나열한다', '명령 옵션이 untracked 표시를 끕니다. dirty라는 단어만으로 모든 작업 디렉터리 파일 차이를 포함한다고 가정하면 안 됩니다.'),
        ('--no-local에서도 file_localversion이 영향을 줄 수 있는 부분은?', 'SCM의 태그 후보 선택', '항상 최종 문자열 끝의 파일 내용 복사', '파일 내용은 최종 조합에서 빠지지만 수집이 먼저 이루어지고 SCM 함수가 태그 선택에 참조합니다.'),
        ('--no-local은 auto.conf가 없어도 해당 존재 검사를 건너뛰는가?', '그렇다. 그 검사 전에 출력하고 종료한다', '아니다. 모든 모드에서 config를 먼저 확인한다', 'KERNELVERSION 검사와 파일 수집 뒤 no-local 조기 반환이 있고 auto.conf 검사는 그 다음입니다.'),
        ('커밋 수의 %05d는 123456을 다섯 자리로 자르는가?', '아니다. 최소 폭이 다섯 자리일 뿐이다', '그렇다. 앞 다섯 숫자만 남는다', 'printf의 폭은 최소 출력 폭입니다. hash의 cut -c1-12와는 다른 종류의 길이 처리입니다.')
    ]
)]
