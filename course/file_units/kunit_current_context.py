"""Whole-file KUnit current-task hooks and Rust bridge."""
ROWS = [dict(
    path='include/kunit/test-bug.h', title='KUnit 현재 문맥 hook: static key·task 포인터·비활성 stub',
    intro='일반 커널 코드가 테스트 문맥을 조회하거나 실패를 알리는 인터페이스 전체를 분석합니다.',
    principle='시스템에 테스트가 실행 중이라는 전역 조건과 현재 task가 테스트에 속한다는 조건은 서로 다릅니다.',
    use='static branch, 함수 포인터 hook, 가변 인수 매크로와 설정별 no-op을 학습합니다.',
    area='KUnit · static key · task 문맥 · callback · 조건부 컴파일',
    sections=[
        ('전체 헤더와 설정', 'GPL-2.0 guard 안에서 NULL용 stddef를 포함합니다. IS_ENABLED(CONFIG_KUNIT) 구역에서는 jump_label과 sched를 포함하며 비활성 구역에서는 간단한 stub을 제공합니다. 테스트 코드 외부에서도 사용할 hook API라는 파일 주석이 있습니다. KUnit 설정을 켜는 자체 구현이나 테스트 runner는 아닙니다.'),
        ('전역 실행 key', 'DECLARE_STATIC_KEY_FALSE(kunit_running)으로 기본 false static key를 선언합니다. kunit_get_current_test는 static_branch_unlikely가 false이면 NULL로 즉시 반환합니다. 이 헤더에는 key 정의·enable·disable 동작이 없으며 실행 중 테스트가 있는지의 빠른 조건을 소비합니다. static key가 일반 함수 포인터와 같은 자료형이라고 설명하지 않습니다.'),
        ('현재 task의 포인터', 'key가 true이면 current->kunit_test를 그대로 반환합니다. 다른 task의 테스트 포인터를 찾아오거나 현재 task에 포인터를 설치하지 않습니다. 전역 key가 true여도 현재 task가 테스트 문맥에 없으면 반환값은 NULL일 수 있습니다. getter는 참조 수 증가나 수명 연장 작업을 따로 수행하지 않습니다.'),
        ('두 함수 포인터 hook', 'extern kunit_hooks 객체의 구조체에는 fail_current_test와 get_static_stub_address가 있습니다. 첫 callback은 const char *,int,const char *,...를 받고 __printf(3,4)로 세 번째 format과 네 번째부터의 인수를 검사하도록 표시합니다. 둘째는 struct kunit *와 real function void *를 받아 void *를 반환합니다. 이 헤더에서 stub 주소를 조회하는 inline 본문은 없습니다. 주석상 KUnit이 로드될 때 테이블을 채웁니다.'),
        ('실패 매크로의 활성 경로', 'kunit_fail_current_test는 do-while(0) 안에서 static key가 true일 때 hook에 __FILE__,__LINE__,fmt,가변 인수를 전달합니다. ##__VA_ARGS__는 인수가 없을 때의 쉼표 처리를 위한 형태입니다. 주석은 key가 true이면 hook이 NULL이 아니라고 보장하는 계약을 적습니다. macro 자체가 current->kunit_test의 NULL 여부를 직접 검사하는 것은 아니며 실제 실패 처리는 callback에 위임합니다.'),
        ('인수 평가와 비활성 stub', '활성 설정에서도 key가 false이면 callback 인수 표현식은 호출되지 않아 평가되지 않습니다. CONFIG_KUNIT가 비활성일 때 getter는 NULL만 반환하고 fail macro는 빈 do-while입니다. 이 경우 fmt와 추가 인수도 실행되지 않습니다. 진단 인수에 필수 부작용을 의존시키면 설정과 실행 상태에 따라 동작이 사라질 수 있습니다.'),
        ('검토 범위', 'static key 선언, hook 구조체 전체, 활성 getter·macro,비활성 getter·macro,설정과 guard를 모두 대조했습니다. 실패 매크로는 이 헤더에서 직접 BUG나 panic을 호출하지 않으며 callback 구현의 종료 동작까지 여기서 단정하지 않습니다. 실제 static key 패치·모듈 로드·다중 task 테스트 실행을 검증한 것은 아닙니다.')
    ], questions=[
        ('kunit_running이 true이면 getter는 반드시 non-NULL인가?', '아니다. 현재 task의 kunit_test가 NULL일 수 있다', '그렇다. 다른 task 테스트라도 자동 반환한다', '전역 실행 조건과 현재 task 문맥을 구분해야 합니다. getter는 current 필드만 반환합니다.'),
        ('CONFIG_KUNIT가 꺼졌을 때 getter의 반환은?', 'NULL', '오류 포인터 -ENOSYS', '비활성 stub은 단순 NULL 반환입니다. 호출자가 없는 테스트 문맥으로 해석할 수 있습니다.'),
        ('실패 매크로가 비활성일 때 가변 인수의 함수 호출도 실행되는가?', '아니다. 매크로 본문에 인수가 사용되지 않는다', '그렇다. C가 항상 먼저 모든 매크로 인수를 실행한다', '매크로는 함수와 다르게 토큰을 치환합니다. 빈 do-while에는 해당 인수 평가가 남지 않습니다.'),
        ('__printf(3,4)의 의미는?', '세 번째 인수는 format, 네 번째부터 format 인수다', '세 번째 CPU에서 네 번 출력한다', 'fail callback의 파일명·줄 번호 뒤에 format이 옵니다. 컴파일러의 format 검사 annotation입니다.'),
        ('kunit_fail_current_test가 자체적으로 하는 일은?', 'key 조건에 따라 위치 정보와 메시지를 hook에 전달한다', '항상 현재 kernel을 panic시킨다', '이 macro 본문에는 panic·BUG 호출이 없습니다. 실제 callback 동작과 인터페이스를 분리해 읽습니다.')
    ]
), dict(
    path='rust/helpers/kunit.c', title='Rust KUnit helper: C inline getter를 호출 가능한 함수로 연결',
    intro='한 함수로 이루어진 C bridge의 전체 포함 관계와 반환 계약을 분석합니다.',
    principle='언어 경계를 넘을 때 inline API의 의미를 유지하는 얇은 wrapper로 접근 지점을 제공할 수 있습니다.',
    use='FFI bridge, 포인터 반환과 원본 API 위임을 구분합니다.',
    area='Rust/C FFI · wrapper · KUnit 문맥',
    sections=[
        ('전체 파일', 'GPL-2.0 주석 뒤 kunit/test-bug.h와 linux/export.h를 포함합니다. rust_helper_kunit_get_current_test(void)는 struct kunit *를 반환하는 전역 C 함수 하나입니다. 인수를 받지 않고 추가 자료구조나 정적 저장 객체를 정의하지 않습니다.'),
        ('정확한 위임', '함수 본문은 return kunit_get_current_test() 한 줄입니다. 따라서 static key와 current task에 따른 NULL 반환 계약을 그대로 따릅니다. NULL을 예외로 바꾸거나 새 테스트를 생성하거나 참조를 증가시키지 않습니다. helper라는 이름만으로 별도의 안전한 소유권 객체를 반환한다고 설명하면 안 됩니다.'),
        ('연결과 범위', '헤더의 static inline getter를 C 함수 경계에서 사용할 수 있게 연결합니다. export.h를 포함하지만 이 파일 본문에는 EXPORT_SYMBOL 호출이 없습니다. 전체 함수와 include를 검토했으며 Rust binding 생성·심볼 재명명·최종 링크의 전체 규칙은 별도 빌드 코드의 책임입니다. 실제 ABI 호출 실행을 검증한 것은 아닙니다.')
    ], questions=[
        ('helper가 getter의 NULL을 받으면?', '그대로 NULL을 반환한다', '새 struct kunit을 할당한다', '본문은 단일 return 호출입니다. 별도 할당이나 오류 변환이 없습니다.'),
        ('export.h include만으로 이 파일에 EXPORT_SYMBOL 호출이 있다고 할 수 있는가?', '아니다. 실제 macro 사용은 없다', '그렇다. 모든 전역 함수를 자동 export한다', '헤더 포함과 export 선언 실행은 별개입니다. 파일 본문의 실제 범위를 확인합니다.')
    ]
)]
