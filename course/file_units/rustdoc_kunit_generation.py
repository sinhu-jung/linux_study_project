"""Whole-file rustdoc extraction and KUnit source generation."""
ROWS = [dict(
    path='scripts/rustdoc_test_builder.rs', title='Rustdoc 테스트 추출: 함수명 탐색·Result 수정·파일 저장',
    intro='rustdoc 생성 소스를 입력받아 커널 테스트 생성기가 사용할 중간 파일로 저장하는 전체 구현을 분석합니다.',
    principle='정형 metadata가 없는 도구를 연결할 때 텍스트 패턴에 의존하면 지원하는 생성 형식과 실패 조건을 명시해야 합니다.',
    use='Rust 문자열 탐색, Option 결합, 텍스트 치환과 빌드 도구의 panic을 학습합니다.',
    area='Rust · 코드 생성 · 문자열 처리 · doctest · 테스트 어댑터',
    sections=[
        ('전체 목적과 입력', 'GPL-2.0 Rust 프로그램은 std::io::Read를 사용하고 main 하나를 정의합니다. stdin을 lock한 뒤 전체 입력을 String에 read_to_string하고 unwrap합니다. 주석은 rustdoc이 구조화된 metadata를 제공하지 않아 생성 소스를 추출하는 임시 방식이라고 설명합니다. UTF-8 읽기나 I/O 실패는 이 호스트 도구의 panic으로 이어집니다.'),
        ('한 줄 안에서 함수명 찾기', 'body.lines().find_map으로 각 줄에서 fn main() { 뒤, 그 안의 fn 뒤, () 앞 부분을 split_once로 찾습니다. 어느 조각이 없으면 ?를 통해 그 줄의 후보가 None이 됩니다. 후보 문자는 is_alphanumeric 또는 밑줄만 허용하고 처음 찾은 후보를 사용합니다. 전체 Rust AST를 파싱하는 것이 아니며 문자 판정은 단순 ASCII 집합 검사와도 다릅니다. 하나도 없으면 expect 메시지로 panic합니다.'),
        ('Result 이름 충돌 방지', '찾은 함수의 정확한 반환 서명 문자열인 Result<(), impl core::fmt::Debug>를 core::result::Result로 한정합니다. 커널 prelude의 자체 Result와 충돌을 피하려는 목적입니다. String::replace는 일치하는 문자열을 치환하며 임의 whitespace·다른 반환형·모든 Result 사용을 AST 단위로 바꾸는 기능은 아닙니다.'),
        ('Unwrap 대신 테스트 실패', '생성된 함수 호출 뒤 .unwrap()을 쓰는 정확한 wrapper 문자열을 찾아 test_return_value 변수에 결과를 저장하고 assert!(...is_ok())로 바꿉니다. 의도는 커널 panic 대신 KUnit assertion 실패로 연결하는 것입니다. 실제 assertion macro 연결은 뒤 gen 도구가 제공합니다. 이 치환이 사용자 예제의 모든 unwrap을 제거한다고 말하면 안 됩니다.'),
        ('중간 이름과 저장', '함수명에서 _rust_kernel_ 첫 구분자 뒤를 얻고 rust/test/doctests/kernel/{name}에 body를 씁니다. 구분자가 없거나 쓰기가 실패하면 unwrap으로 panic합니다. 디렉터리를 생성하는 명령은 없으며 빌드가 준비한 경로를 전제로 합니다. 이 단계의 name에는 원래 파일·줄·번호 표현이 남고 줄 번호를 제외한 새 테스트 이름은 gen 단계에서 생성합니다.'),
        ('안정성의 범위', '주석은 rustdoc 이름이 파일_줄_번호이며 같은 줄의 매크로 확장에서 여러 doctest가 나올 수 있어 번호가 필요하다고 설명합니다. 줄 번호가 바뀌면 CI bisection 이름이 흔들리므로 다음 단계에서 개선하려는 설계입니다. 모든 입력 추출·두 치환·저장 경로를 원본과 대조했으며 이 환경에서 rustdoc 파이프라인을 실행한 것은 아닙니다.')
    ], questions=[
        ('함수명 탐색은 Rust 문법 전체를 AST로 해석하는가?', '아니다. 한 줄의 문자열 조각과 문자 조건을 검사한다', '그렇다. rustc parser를 호출한다', 'split_once와 find_map만 사용합니다. 생성 형식에 맞는 줄을 기대하는 계약입니다.'),
        ('Result를 core::result::Result로 바꾸는 이유는?', '커널 prelude의 같은 이름과 충돌을 피하기 위해서다', '모든 오류를 자동으로 성공으로 바꾸기 위해서다', '반환 타입을 명확히 지정하는 치환이지 오류값을 제거하는 동작은 아닙니다.'),
        ('이 단계에서 줄 번호 없는 최종 KUnit 이름을 만드는가?', '아니다. gen 도구에서 파일별 전체 목록을 보고 만든다', '그렇다. 모든 줄 번호를 여기서 삭제한다', 'builder의 저장 이름은 함수명 suffix를 사용합니다. 파일 전체의 순서를 알아야 하는 번호 재할당은 다음 단계입니다.'),
        ('생성된 wrapper의 unwrap 치환 목적은?', '결과를 assertion으로 확인해 테스트 실패로 연결하기', '원래 예제의 모든 panic 가능성을 증명상 제거하기', '특정 문자열만 치환합니다. 테스트 실패 경로 개선을 임의 코드 전체의 panic 제거로 확대할 수 없습니다.')
    ]
), dict(
    path='scripts/rustdoc_test_gen.rs', title='Doctest→KUnit 생성기: 경로 복원·안정 이름·Rust/C 연결',
    intro='재귀 경로 후보 탐색과 모든 Rust·C 코드 출력, KUnit 문맥 및 원본 위치 연결을 분석합니다.',
    principle='손실된 경로 구분 정보를 복원할 때 실제 파일시스템을 이용해 후보를 좁히고 모호성을 오류로 처리할 수 있습니다.',
    use='재귀 분할 탐색, 정렬과 그룹별 번호, 코드 생성과 FFI, 진단 위치 변환을 학습합니다.',
    area='재귀 알고리즘 · 경로 탐색 · Rust · FFI · KUnit · 코드 생성',
    sections=[
        ('전체 구성과 KUnit 문맥', 'GPL-2.0 파일은 fs,File,BufWriter,Read,Write,Path,PathBuf를 사용합니다. 문서 주석은 예제 코드에 struct kunit 포인터 전달을 요구하지 않으려고 current->kunit_test 기반 kunit_get_current_test를 사용한다고 설명합니다. 별도 task에서 실패한 assertion은 로그에 나타나도 실제 원래 테스트 실패로 반영되지 않을 수 있다는 제한도 명시합니다. per-test static 포인터만으로 해결되는 문제라고 설명하지 않습니다.'),
        ('경로 복원 입력', 'find_real_path는 전달된 valid_paths를 clear한 뒤 file의 _rs suffix를 제거하고 밑줄로 나눕니다. suffix가 없으면 unwrap panic입니다. sync_locked_by_rs 같은 이름은 sync_locked_by.rs, sync/locked_by.rs, sync_locked/by.rs, sync/locked/by.rs처럼 여러 원본 경로를 나타낼 수 있습니다. 단순히 모든 밑줄을 slash로 바꾸지 않습니다.'),
        ('재귀의 파일 후보', '내부 find_candidates는 남은 구성요소를 밑줄로 모두 합치고 .rs를 붙입니다. srctree/rust/kernel/prefix 아래에 그 파일이 is_file이면 후보에 넣습니다. 저장하는 후보는 srctree를 제외한 rust/kernel 상대 경로입니다. KTAP 출력에 빌드 머신의 절대 소스 경로를 강제로 넣지 않으려는 선택입니다.'),
        ('재귀 분할과 가지치기', 'i=1부터 남은 길이 미만까지 구성요소 prefix를 밑줄로 합쳐 디렉터리 후보를 만듭니다. 실제 is_dir일 때만 나머지 slice로 재귀 호출합니다. 분할 지점의 조합을 탐색하므로 이론상 후보 수는 구성요소 수에 따라 빠르게 늘 수 있지만 존재하지 않는 디렉터리에서 가지치기합니다. 항상 O(n)인 단일 선형 경로 복원이라고 설명하면 안 됩니다.'),
        ('모호성 거부와 참조 수명', '후보가 없으면 assert로 실패하고 둘 이상이면 모든 후보를 stderr에 표시한 뒤 rename으로 모호성을 해결하라는 panic을 냅니다. 하나면 valid_paths[0]의 UTF-8 문자열 참조를 반환합니다. 반환 수명은 벡터의 borrow에 연결되며 지역 임시 String을 반환하는 방식이 아닙니다. UTF-8 변환도 unwrap이므로 모든 OS 경로 표현을 받아들이는 것은 아닙니다.'),
        ('입력 디렉터리와 정렬', 'main은 srctree 환경 변수를 unwrap으로 얻고 rust/test/doctests/kernel의 read_dir 결과를 path 벡터로 모아 sort합니다. 정렬은 PathBuf의 순서이며 파일명에 든 줄 번호의 숫자 정렬 parser를 따로 쓰지 않습니다. 디렉터리 항목을 파일 유형으로 미리 걸러내는 filter도 없습니다. 정상 빌드가 중간 테스트 파일만 둔다는 전제를 읽어야 합니다.'),
        ('이름 해체와 그룹 번호', '각 파일명에서 오른쪽 마지막 밑줄로 원래 test number를 버리고 다시 오른쪽에서 나눠 file과 line을 얻습니다. 같은 file이 연속되면 number를 증가시키고 새 file이면 0으로 초기화합니다. 새 file에서만 find_real_path를 호출해 반복 경로 탐색을 줄입니다. KUnit 이름은 rust_doctest_kernel_{file}_{number}이며 원래 line을 넣지 않습니다.'),
        ('이름 안정성의 한계', '줄 번호를 이름에서 빼면 줄 이동에 따른 직접적인 이름 변화는 줄지만, 같은 파일 안 예제의 정렬 순서나 추가·삭제에 따라 순차 번호가 바뀔 수 있습니다. Rust item의 완전한 경로를 식별자로 보존하는 방식은 아닙니다. 원래 line은 이후 진단 metadata에 따로 사용합니다.'),
        ('본문 읽기와 위치 anchor', '재사용 body String을 clear하고 파일 전체를 읽습니다. fn main() {를 포함하는 첫 줄 전까지 세어 1을 더한 body_offset을 구합니다. 그 줄이 없는 경우를 별도 오류로 판정하는 검사는 여기 없습니다. 생성 코드의 __DOCTEST_ANCHOR는 core::line!()+body_offset+1이며 assertion에 anchor-original line 차이를 전달해 원본 위치 연결을 지원합니다.'),
        ('생성 Rust entry와 매크로', '각 테스트를 #[no_mangle] pub extern C 함수로 만들고 *mut kernel::bindings::kunit 인수를 __kunit_test라는 이름으로 받습니다. 로컬 assert!와 assert_eq! 매크로를 정의해 각각 kernel::kunit_assert!와 kunit_assert_eq!로 연결합니다. 패턴은 해당 기본 인수와 선택적 trailing comma이며 임의 사용자 메시지 인수의 모든 표준 macro overload를 재현하지 않습니다. 함수 인수 포인터를 각 예제 함수에 직접 전달하는 구조는 아닙니다.'),
        ('Prelude·위치 로그·main 호출', '생성 함수는 kernel::prelude::*를 가져오고 성공 여부와 관계없이 테스트 location metadata를 kernel::kunit::info로 출력합니다. 원본 경로와 원본 줄 번호를 담습니다. 본문을 내부 블록에 넣은 뒤 main()을 호출합니다. 주석의 KTAP v2 관련 내용은 당시 제안과 향후 이행 의도를 설명하며 현행 표준을 별도로 검증한 주장은 아닙니다.'),
        ('C 선언과 case 수집', 'Rust 함수를 만드는 각 반복에서 같은 이름의 void 함수(struct kunit *) C 선언과 KUNIT_CASE 항목을 문자열에 추가합니다. 루프 뒤 Rust 본문·C 선언·case 문자열에 trim을 적용합니다. Rust/C에서 같은 이름과 호출 규약을 사용하는 FFI 연결이며 다른 이름의 테스트를 두 번 실행하도록 만드는 목록은 아닙니다.'),
        ('두 출력 파일 전체', 'BufWriter와 File::create로 rust/doctests_kernel_generated.rs와 rust/doctests_kernel_generated_kunit.c를 씁니다. Rust 출력은 문서 주석과 NUL 종료 LOG_PREFIX, 생성 함수들입니다. C 출력은 kunit/test.h,함수 선언,빈 종료 원소가 있는 test_cases 배열,이름 rust_doctests_kernel인 suite, kunit_test_suite 등록, MODULE_LICENSE(GPL)입니다. 기존 출력 파일을 append하지 않고 생성 경로에서 덮습니다.'),
        ('오류와 검토 범위', '대부분 파일·환경·형식·쓰기 오류는 unwrap 또는 assert/panic으로 빌드 도구를 중단시킵니다. BufWriter의 명시적 flush 결과 검사는 없으며 두 출력 파일을 transaction으로 교체하는 rollback도 없습니다. 전체 재귀 함수·main의 모든 생성 문자열·출력 경로·문맥 제한을 검토했습니다. 실제 Rust 컴파일·KUnit 실행을 검증한 결과는 아닙니다.')
    ], questions=[
        ('sync_locked_by_rs의 밑줄을 모두 경로 구분자로 바꾸면 충분한가?', '아니다. 파일·디렉터리 이름 자체의 밑줄일 수 있다', '그렇다. Rust 파일명에는 밑줄을 쓸 수 없다', '실제 파일시스템을 탐색해 가능한 분할을 확인합니다. 손실된 경로 구분 정보를 복원하는 문제입니다.'),
        ('유효 경로 후보가 두 개면 생성기는?', '후보를 표시하고 panic한다', '정렬상 첫 경로를 조용히 선택한다', '모호성을 잘못된 원본 위치로 숨기지 않습니다. 이름 변경으로 해결하라는 오류를 냅니다.'),
        ('최종 KUnit 이름에 원래 줄 번호가 들어가는가?', '아니다. 파일별 새 순차 번호를 쓴다', '그렇다. 원래 file_line_number를 그대로 쓴다', '줄 정보는 진단에 따로 남습니다. 이름 안정성과 원본 추적을 분리합니다.'),
        ('입력 path 정렬은 줄 번호의 수치 정렬인가?', '아니다. PathBuf 목록을 그대로 sort한다', '그렇다. line을 정수로 parse한 뒤 정렬한다', '이름 해체는 정렬 뒤입니다. 문자열에 들어 있는 숫자가 자동으로 수치 정렬되는 것은 아닙니다.'),
        ('예제가 만든 다른 task에서 assertion 실패가 나면 원래 테스트도 반드시 실패하는가?', '아니다. 원본 주석이 현재 문맥 처리의 제한을 명시한다', '그렇다. static 포인터 하나로 모두 해결된다', '현재 task의 KUnit 문맥을 사용하는 설계입니다. 다른 task의 assertion은 로그와 실제 test 상태가 다를 수 있습니다.'),
        ('C test_cases 배열 끝의 빈 원소는?', '생성되는 case 배열의 종료 원소', '새 Rust doctest 함수 본문', '각 KUNIT_CASE 뒤 빈 원소를 추가합니다. Rust 함수 목록과 C suite 등록 구조를 구분합니다.'),
        ('생성된 assert 매크로가 표준 assert의 모든 호출 형식을 지원하는가?', '아니다. 코드에 명시된 기본 인수 패턴을 지원한다', '그렇다. 임의 메시지 인수를 자동으로 전달한다', '생성 문자열의 macro_rules 패턴을 직접 확인해야 합니다. 기본 조건·두 값과 trailing comma를 지원하는 형태입니다.')
    ]
)]
