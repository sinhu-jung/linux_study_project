"""Whole-file Rust-to-KUnit assertion bridge."""
ROWS = [dict(
    path='rust/kernel/kunit.rs', title='Rust KUnit assertion: 현재 task 문맥·정적 FFI 자료·실패 중단',
    intro='로그 helper 두 개와 assertion 매크로 두 개의 모든 분기·자료형·안전성 주석을 분석합니다.',
    principle='FFI로 테스트 실패를 연결할 때 포인터 수명뿐 아니라 task 문맥과 언어의 스택 정리 규칙도 고려해야 합니다.',
    use='Rust macro, C 문자열, 정적 수명과 Sync, 원본 위치 보정, abort와 Drop의 차이를 학습합니다.',
    area='Rust · FFI · KUnit · macro · 메모리 수명 · assertion',
    sections=[
        ('전체 구성과 노출 범위', 'GPL-2.0 모듈은 core의 c_void와 fmt를 사용합니다. err와 info는 pub이지만 doc(hidden)이며 생성된 KUnit 코드용이라는 문서가 있습니다. kunit_assert와 kunit_assert_eq는 macro_export 및 doc(hidden)입니다. 문서에서 숨기는 속성이 호출을 보안상 금지하거나 private 접근 제어를 만드는 것은 아닙니다.'),
        ('출력 helper와 PRINTK', 'err는 C 문자열의 제어 prefix와 3 레벨, info는 6 레벨을 써 _printk에 %pA 형식과 fmt::Arguments 주소를 c_void 포인터로 전달합니다. C 문자열은 NUL 종료이며 Rust 포맷 인수와 해당 formatter 계약을 맞춥니다. unsafe 호출 블록은 CONFIG_PRINTK일 때만 존재합니다. 설정이 없으면 이 함수 본문에 다른 fallback 출력 경로가 없습니다.'),
        ('Assertion 인수와 성공 경로', 'kunit_assert는 name literal,file literal,diff expression,condition expression과 선택적 trailing comma를 받습니다. 이름 붙은 out 블록에서 condition이 true이면 바로 break합니다. 따라서 성공 때는 현재 KUnit 포인터 조회나 실패 메시지 출력이 없습니다. condition은 if 위치에서 평가하고 stringify는 식의 텍스트를 만드는 별도 컴파일 단계입니다.'),
        ('원본 위치와 조건 텍스트', 'FILE은 c_str!(file), LINE은 core::line!() as i32-diff, CONDITION은 stringify!(condition)을 C 문자열로 바꾼 static입니다. 생성 소스의 줄과 원본 문서 줄 차이를 diff로 보정합니다. diff가 macro 패턴상 expr이라고 임의 런타임 값이 static 초기화에 허용되는 것은 아닙니다. 실제 생성기는 정적으로 계산할 수 있는 anchor 표현을 제공합니다.'),
        ('현재 task 문맥 없음', '실패하면 kunit_get_current_test를 FFI로 호출합니다. NULL이면 테스트 이름과 원본 위치, 기대 조건, KUnit에 실패를 보고하지 못했다는 세 메시지를 err로 출력하고 블록을 벗어납니다. 이 분기에는 __kunit_abort가 없습니다. 예제가 만든 다른 task나 잘못된 비테스트 호출일 수 있으며 원래 테스트 상태가 자동으로 실패하는 보장은 없습니다. PRINTK까지 꺼져 있으면 이 err 호출들의 실제 printk도 없습니다.'),
        ('정적 C 자료와 transparent wrapper', '문맥이 있으면 bindings의 kunit_loc와 kunit_unary_assert를 각각 Location,UnaryAssert #[repr(transparent)] wrapper로 다룹니다. 각 wrapper에 unsafe impl Sync가 있습니다. 안전성 주석은 정적 인스턴스의 포인터가 불변 C 문자열을 가리킨다는 구체적인 근거를 듭니다. raw pointer를 가진 모든 구조체가 일반적으로 Sync라고 자동 보장되는 것은 아닙니다.'),
        ('LOCATION과 ASSERTION 초기화', 'LOCATION은 FILE의 char 포인터와 LINE을 저장합니다. ASSERTION은 빈 공통 kunit_assert, 조건 문자열 포인터, expected_true=true를 저장합니다. 이 static들이 FFI 호출 중과 그 후에도 유효한 주소를 제공합니다. 로컬 임시 문자열의 버퍼를 C에 넘기는 패턴이 아닙니다.'),
        ('실패 보고 FFI', '__kunit_do_failed_assertion에 현재 test,LOCATION 내부 주소,KUNIT_ASSERTION 종류,ASSERTION의 공통 assert 주소,Some(kunit_unary_assert_format),NULL format 포인터를 전달합니다. addr_of!로 내부 주소를 얻습니다. 주석은 test pointer 유효성, NUL 종료 문자열, 정적 수명, 올바른 callback과 허용된 NULL format을 설명합니다. 사용자 포맷 문자열을 무검사로 실행하는 임의 호출이 아닙니다.'),
        ('중단과 명시된 안전성 한계', '실패 보고 뒤 __kunit_abort를 호출합니다. 원본 안전성 주석은 thread 중단 시 destructor를 실행하지 않는 문제와 extern C 경계를 강제 외부 unwind처럼 넘는 UB 문제를 명시합니다. 따라서 core assert의 panic을 쓰지 않는다는 사실만으로 완전히 안전한 Rust unwind라고 설명하면 안 됩니다. 주석은 stack pinning도 주의하고 KUnit의 비production 테스트 문맥에서 현재 구현을 수용하는 배경을 밝힙니다. 이 자료는 그 한계를 없다고 숨기지 않습니다.'),
        ('동등성 assertion의 구현 범위', 'kunit_assert_eq는 left==right 식을 kunit_assert로 전달합니다. 주석은 KUnit binary assertion이 몇몇 자료형만 지원해 지금은 expression assertion으로 연결한다고 설명합니다. 따라서 모든 값의 Debug 내용을 별도로 출력하는 core assert_eq와 같은 진단 구현은 아닙니다. PartialEq 기반 비교식을 사용하며 좌우 값을 여러 번 출력하기 위한 별도 평가도 없습니다.'),
        ('제어 흐름과 검토 범위', 'true는 즉시 통과, false와 NULL 문맥은 로그 후 블록 종료, false와 유효 문맥은 실패 보고와 abort로 나뉩니다. 네 항목 전체와 cfg 조건, static 자료, FFI 인수, unsafe 근거 및 제한을 원본에 대조했습니다. 실제 커널에서 assertion 실패·외부 task·Drop 동작을 실행 검증한 결과는 아닙니다.')
    ], questions=[
        ('조건이 true이면 kunit_get_current_test를 호출하는가?', '아니다. 앞에서 out 블록을 벗어난다', '그렇다. 성공해도 항상 실패 자료를 기록한다', '첫 if가 성공 경로를 끝냅니다. 뒤 문맥 조회와 FFI는 실패 경로입니다.'),
        ('조건이 false지만 현재 KUnit 포인터가 NULL이면?', '오류 메시지를 시도하고 abort 없이 블록을 종료한다', '항상 원래 부모 테스트를 abort한다', 'NULL 분기의 끝은 break out입니다. 다른 task의 실패와 원래 테스트 결과 사이의 제한을 보여 줍니다.'),
        ('LINE 계산에서 diff의 역할은?', '생성 코드 줄 번호를 원본 문서 위치로 보정한다', '조건식의 실행 시간을 계산한다', 'core::line!()에서 생성기가 제공한 차이를 뺍니다. 시간이나 CPU 정보와 무관합니다.'),
        ('unsafe impl Sync의 원본 근거는?', '정적 인스턴스의 포인터가 불변 C 문자열을 가리킨다', '모든 C raw pointer는 자동으로 thread-safe다', '구체적인 자료의 불변성과 수명에 의존하는 설명입니다. 임의 raw pointer 구조체에 일반화할 수 없습니다.'),
        ('KUnit abort가 Rust destructor를 정상 unwind처럼 모두 실행한다고 보장하는가?', '아니다. 원본 주석이 destructor 생략과 FFI unwind 문제를 명시한다', '그렇다. panic이 아니므로 모든 Drop이 보장된다', 'panic 미사용과 정상적인 Rust 스택 정리는 다른 문제입니다. 테스트 실패 경로의 제한을 함께 읽어야 합니다.'),
        ('kunit_assert_eq가 내부적으로 전달하는 것은?', 'left==right라는 boolean assertion', '모든 자료형을 별도 C binary assertion으로 직렬화한 값', '현재 구현은 kunit_assert로 위임합니다. 값별 상세 formatter를 갖춘 일반 assert_eq와 동일하다고 가정하지 않습니다.')
    ]
)]
