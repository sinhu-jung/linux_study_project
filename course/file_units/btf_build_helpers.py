"""Whole-file size/version probes and version-specific BTF flags."""
ROWS = [dict(
    path='scripts/file-size.sh', title='파일 크기 helper: ls 결과를 위치 인수로 해석하기',
    intro='두 줄의 shell 본문에서 입력·출력·실패 처리의 실제 계약을 분석합니다.',
    principle='도구 출력의 필드 위치를 이용하는 작은 helper도 출력 형식과 종료 상태에 의존합니다.',
    use='위치 인수 재설정, 명령 치환과 파일 metadata 크기를 학습합니다.',
    area='shell · 파일 metadata · 명령 치환',
    sections=[
        ('전체 동작', '#!/bin/sh, GPL-2.0 뒤 set -- $(ls -dn "$1")와 printf 두 명령이 있습니다. -d는 디렉터리 자체 정보를, -n은 숫자 UID·GID를 사용하는 긴 목록 정보를 요청합니다. 최초 첫 인수는 ls에 따옴표로 전달하지만 그 출력은 따옴표 없는 명령 치환으로 단어 분리하여 새 위치 인수로 설정합니다.'),
        ('다섯 번째 필드', 'printf는 새 $5를 문자열로 출력하고 newline을 붙입니다. 일반 파일의 긴 ls 출력에서 권한·링크 수·UID·GID 다음의 byte 크기 필드에 해당합니다. 파일 내용을 읽어 직접 세는 알고리즘은 아닙니다. 모든 특수 파일 유형의 긴 출력이 동일한 크기 필드 의미를 가진다고 확대하지 않습니다. link-vmlinux.sh는 생성된 kallsyms 객체 파일 크기 비교에 사용합니다.'),
        ('오류와 범위', '인수 개수 검사, set -e, ls 실패의 명시적 상태 검사, 숫자 검증이 없습니다. ls 실패 후에도 printf가 빈 문자열 등을 출력하고 성공할 수 있으므로 helper 출력만으로 대상 존재를 확인하는 API가 아닙니다. 전체 원본을 검토했으며 Windows 호스트의 ls로 Linux 파일 크기 동작을 대신 검증하지 않았습니다.')
    ], questions=[
        ('set -- 실행 뒤 $5는 무엇을 의미하는가?', 'ls 출력에서 분리된 다섯 번째 필드', '스크립트 실행 시의 다섯 번째 입력 인수', 'set --가 위치 인수 전체를 다시 설정합니다. 최초 인수와 이후 인수의 의미가 달라집니다.'),
        ('이 스크립트가 크기를 얻는 방식은?', '긴 ls 출력의 metadata 필드 사용', '파일 내용을 한 byte씩 읽고 합산', '본문에는 ls와 printf만 있습니다. 특수 파일까지 동일 계약을 가정하지 말고 실제 호출 대상인 객체 파일과 연결합니다.')
    ]
), dict(
    path='scripts/pahole-version.sh', title='Pahole 버전 probe: 실행 파일 확인과 문자열 치환',
    intro='도구 발견 실패와 버전 출력 가공의 전체 제어 흐름을 분석합니다.',
    principle='버전 문자열을 정수처럼 표현하는 규칙과 실제 산술 변환은 서로 다를 수 있습니다.',
    use='command -v, 실행 가능 검사, 전체 인수 전달, sed 치환 범위를 학습합니다.',
    area='도구 탐지 · shell · 버전 인코딩 · 문자열 치환',
    sections=[
        ('용도와 사전 검사', '#!/bin/sh, GPL-2.0 주석은 pahole 경로를 인수로 받고 v1.19를 119처럼 출력한다고 설명합니다. command -v "$@"의 결과에 -x 검사를 적용합니다. 실행 가능 파일로 확인하지 못하면 stdout에 0을 출력하고 exit 1입니다. 오류 sentinel과 실패 종료 상태를 함께 반환합니다.'),
        ('도구 실행과 치환', '검사를 통과하면 "$@" --version으로 전달받은 명령과 인수를 실행하고 sed -E로 v(숫자).(숫자)를 두 그룹의 단순 연결로 바꿉니다. v1.19는 119지만 v1.9는 19이며 세 자리로 zero padding하는 산술 변환은 아닙니다. 버전 문자열 시작·끝 앵커가 없어 접두·접미의 다른 문자를 전부 지우는 식도 아닙니다.'),
        ('실패 처리의 한계', '버전 형식이 맞지 않으면 sed가 원문을 남길 수 있고 숫자만인지 다시 검사하지 않습니다. set -e나 pipefail이 없으며 pipeline의 앞 도구 실패를 별도로 검사하지 않습니다. command -v로 실행 가능성을 확인한 사실과 --version 실행 성공은 별개입니다. 전체 파일을 검토했으며 실제 pahole을 이 환경에서 실행한 검증은 아닙니다.')
    ], questions=[
        ('실행 가능한 pahole을 찾지 못하면 출력과 종료 상태는?', '0 출력, 종료 상태 1', '아무 출력 없이 성공 0', 'if 분기에 echo 0과 exit 1이 모두 있습니다. 값만 읽고 성공으로 오해하면 안 됩니다.'),
        ('치환식이 v1.9에 적용되면 결과는?', '19', '109', '두 숫자 그룹을 그대로 연결합니다. 주석의 세 자리 예시는 한 자리 minor에 대한 padding 구현이 아닙니다.'),
        ('버전 출력에 다른 접미사가 있으면 자동으로 모두 제거되는가?', '아니다. 일치하는 v숫자.숫자 부분만 치환한다', '그렇다. 출력 전체를 정수 parser가 처리한다', 'sed 식에는 전체 줄을 감싸는 앵커나 정수 검증이 없습니다. 치환과 검증을 구분합니다.')
    ]
), dict(
    path='scripts/Makefile.btf', title='Pahole 버전별 BTF 옵션: 개별 플래그에서 feature 목록으로',
    intro='모든 버전 경계·외부 모듈 조건·언어 제외 조건과 export를 분석합니다.',
    principle='도구 기능의 세대 차이는 버전별 분기와 선택적인 기능 목록으로 빌드 계약에 반영됩니다.',
    use='Make 조건식, 설정 기반 변수 선택, 최소·최대 버전 경계를 비교합니다.',
    area='Kbuild · 도구 호환성 · BTF · 조건부 변수',
    sections=[
        ('입력과 기본 변수', 'GPL-2.0 Makefile은 pahole-ver := CONFIG_PAHOLE_VERSION으로 이미 탐지된 값을 받고 pahole-flags-y를 빈 값으로 초기화합니다. 이 파일에서 pahole-version.sh를 직접 실행하지 않습니다. test-le·test-ge helper 결과 y를 변수 이름과 조건식에 사용합니다.'),
        ('1.18부터 1.21의 변수 인코딩 회피', '바깥 조건은 버전<=125이며 그 안에서 <=121인 경우 >=118에 --skip_encoding_btf_vars를 추가합니다. 즉 118,119,120,121 구간입니다. 주석은 해당 버전이 크기 0인 per-CPU 변수를 처리하지 못하는 이유를 설명합니다. 단순히 모든 1.25 이하에 이 옵션을 적용하지 않습니다.'),
        ('기존 옵션 누적', '같은 <=125 구역에서 >=121이면 --btf_gen_floats, >=122이면 -j, >=125이면 --skip_encoding_btf_inconsistent_proto와 --btf_gen_optimized를 추가합니다. 121은 변수 회피와 float 옵션을 동시에 얻습니다. 125는 122의 병렬 옵션과 float 옵션도 함께 얻지만 118~121 전용 변수 회피는 받지 않습니다.'),
        ('1.26 이후 feature 목록', '>125 경로에서 >=126이면 pahole-flags-y에 -j와 --btf_features=encode_force,var,float,enum64,decl_tag,type_tag,optimized_func,consistent_func,decl_tag_kfuncs를 설정합니다. 이전 개별 옵션들을 똑같이 모두 추가하는 형태가 아닙니다. 기능 이름 목록의 순서와 항목을 그대로 읽으며 이 파일이 각 BTF 기능의 내부 인코딩 알고리즘을 구현하지는 않습니다.'),
        ('외부 모듈과 언어 제외', '새 버전 구역 안에서 KBUILD_EXTMOD가 비어 있지 않으면 >=126의 module-pahole-flags-y에 --btf_features=distilled_base를 더합니다. 바깥 두 버전 경로가 끝난 뒤 CONFIG_PAHOLE_HAS_LANG_EXCLUDE가 y이면 공통 pahole-flags-y에 --lang_exclude=rust를 추가합니다. 외부 모듈 전용 옵션과 공통 언어 제외 옵션은 서로 다른 변수와 조건입니다.'),
        ('Export와 경계 예제', 'PAHOLE_FLAGS := pahole-flags-y와 MODULE_PAHOLE_FLAGS := module-pahole-flags-y를 export합니다. 전자는 공통 옵션, 후자는 모듈 전용 추가 옵션입니다. 여기서 둘을 자동으로 하나의 문자열로 합쳐 내보내지 않습니다. 전체 조건·변수 대입·export를 검토했고 실제 pahole 버전별 BTF 산출물을 실행 비교한 것은 아닙니다.')
    ], questions=[
        ('버전 121에서 동시에 선택되는 옵션은?', '변수 인코딩 회피와 float 생성', '오직 -j 하나', '<=121와 >=118 조건 및 >=121 조건이 동시에 참입니다. -j는 122부터입니다.'),
        ('버전 125가 --skip_encoding_btf_vars를 받는가?', '아니다. 그 옵션은 118~121 구간이다', '그렇다. 125 이하 모두 받는다', '중첩된 <=121 조건을 빠뜨리면 범위를 잘못 읽게 됩니다.'),
        ('distilled_base가 모듈 옵션에 추가되는 조건은?', '외부 모듈 빌드이며 버전 126 이상', '모든 커널과 모든 pahole 버전', 'KBUILD_EXTMOD 비어 있지 않음과 새 버전 분기 안의 >=126 조건을 모두 확인해야 합니다.'),
        ('CONFIG_PAHOLE_HAS_LANG_EXCLUDE가 y이면 어느 언어를 제외하는가?', 'rust', '모든 C 코드', '공통 옵션에 --lang_exclude=rust를 추가합니다. 새 버전 분기 밖에 있어 별도의 기능 탐지 설정으로 제어됩니다.')
    ]
)]
