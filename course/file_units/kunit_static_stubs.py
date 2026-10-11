"""Whole-file KUnit static redirection API, resources and global hooks."""
ROWS = [dict(
    path='include/kunit/static_stub.h', title='KUnit static stub API: 함수 시작부의 조건부 대체 호출',
    intro='redirect와 activate 매크로, 해제 선언 및 설정별 범위를 분석합니다.',
    principle='함수 대체는 원래 함수에 삽입한 명시적 분기와 현재 테스트의 등록 상태로 동작할 수 있습니다.',
    use='매크로의 return 범위, 함수 타입 검사, task별 테스트 문맥을 학습합니다.',
    area='KUnit · 테스트 대역 · C macro · 함수 포인터',
    sections=[
        ('설정 분기 전체', 'GPL-2.0 guard에서 CONFIG_KUNIT가 비활성이면 KUNIT_STATIC_STUB_REDIRECT만 빈 do-while로 정의합니다. 활성 구역에는 test,test-bug,compiler,sched 헤더와 API가 있습니다. 비활성 구역에 activate·deactivate의 같은 형태 no-op API가 모두 제공된다고 가정하면 안 됩니다.'),
        ('현재 테스트와 대체 조회', 'redirect 매크로는 typeof(&real_fn_name) replacement와 현재 테스트 포인터를 얻습니다. 현재 테스트가 없으면 do-while을 break해 원래 함수 본문을 계속합니다. 있으면 kunit_hooks.get_static_stub_address(current_test,&real_fn_name)를 호출합니다. 임의 함수 코드를 런타임 패치하는 구현이 아니라 함수 시작에 이 매크로가 있어야 동작합니다.'),
        ('Return의 범위와 인수', 'replacement가 있으면 return replacement(args)를 실행합니다. return은 매크로를 포함하는 원래 함수에서 반환하므로 그 아래 정상 본문은 실행되지 않습니다. 없으면 정상 본문으로 진행합니다. real_fn_name은 문자열이 아니라 함수 식별자이며 args는 전달할 인수 표현식입니다. 원래 함수를 replacement 안에서 다시 호출하면 같은 redirect가 다시 적용될 가능성을 고려해야 합니다.'),
        ('활성화와 타입 검사', 'kunit_activate_static_stub은 typecheck_fn(typeof(&replacement_addr),real_fn_addr) 뒤 __kunit_activate_static_stub을 호출합니다. 주석은 실제 함수와 대체 함수 타입이 같아야 하므로 void *를 받는 내부 helper 대신 매크로 사용을 권장합니다. 커널 함수 어디에나 prologue 없이 적용되는 범용 detour API는 아닙니다.'),
        ('해제와 문서 예제', 'kunit_deactivate_static_stub(test,real_fn_addr)는 외부 구현 선언입니다. 예제는 정상 함수가 0을 반환하지만 replacement가 42를 반환하고 활성화된 테스트 안에서 42를 기대합니다. 현재 테스트 문맥에서 간접 호출도 redirect될 수 있습니다. 전체 매크로·선언·예제·설정 구역을 검토했으며 실제 C 테스트 실행을 검증한 것은 아닙니다.')
    ], questions=[
        ('대체 함수가 있으면 원래 함수 본문도 뒤이어 실행되는가?', '아니다. return replacement(args)로 원래 함수에서 반환한다', '그렇다. 대체 함수는 로그만 남긴다', '매크로 안의 return은 enclosing function에 적용됩니다. do-while 블록만 끝내는 break와 다릅니다.'),
        ('아무 함수나 prologue 없이 활성화만 하면 바뀌는가?', '아니다. 원래 함수에 redirect 매크로가 필요하다', '그렇다. 기계어를 자동 패치한다', '조회와 대체 호출은 매크로가 삽입한 명시적인 분기입니다.'),
        ('KUnit 비활성에서 이 헤더가 제공하는 no-op은?', 'redirect 매크로', '모든 activate·deactivate 함수까지 전부', '비활성 구역에는 redirect 정의 하나만 있습니다. 설정별 선언 범위를 확인해야 합니다.')
    ]
), dict(
    path='lib/kunit/static_stub.c', title='Static stub 자원 구현: 주소 매칭·참조 반환·갱신·해제',
    intro='두 함수 주소를 KUnit 자원으로 관리하는 전체 구현과 오류 경로를 분석합니다.',
    principle='테스트 대역 등록도 객체 수명과 식별 규칙이 필요하며 주석의 의도보다 실제 인수 전달이 동작을 결정합니다.',
    use='resource callback, 포인터 식별, 참조 획득·반환, 실패 경로 분석을 학습합니다.',
    area='KUnit 자원 · 함수 대역 · refcount · 오류 경로',
    sections=[
        ('자료형과 free callback', 'GPL-2.0 파일은 test,static_stub,내부 hooks-impl을 포함합니다. kunit_static_stub_ctx는 real_fn_addr와 replacement_addr 두 void *를 보관합니다. free callback은 res->data를 kfree합니다. 이 callback 자체가 함수의 실행 코드나 원래 함수 객체를 해제하는 것은 아닙니다.'),
        ('자원 종류와 주소 매칭', 'match callback은 먼저 res->free가 static stub free callback과 같은지 확인하고 아니면 false입니다. 같은 종류일 때만 ctx->real_fn_addr와 요청 주소를 비교합니다. res->data를 ctx 변수에 넣는 것과 필드를 역참조하는 시점을 구분해야 합니다. test 인수는 본문에서 사용하지 않습니다. 별도 enum type tag 대신 free callback 동일성을 자원 종류 검사로 사용합니다.'),
        ('대체 주소 조회', '__kunit_get_static_stub_address_impl은 kunit_find_resource로 같은 real 주소의 자원을 찾고 없으면 NULL입니다. 있으면 replacement 주소를 로컬 변수로 복사한 뒤 kunit_put_resource로 찾기에서 얻은 참조를 놓고 주소값을 반환합니다. 자원 포인터 자체를 호출자에게 새 소유권으로 넘기는 함수가 아닙니다.'),
        ('명시적 해제', 'kunit_deactivate_static_stub는 real_fn_addr가 NULL이 아닌지 assertion하고 자원을 찾습니다. 없는 등록도 assertion 실패입니다. 찾은 경우 kunit_remove_resource로 테스트 자원 목록에서 제거하고 kunit_put_resource로 조회 참조를 놓습니다. 주석의 두 참조 반환은 remove의 소유권 처리와 별도 put을 함께 의미하며 코드에 put 호출이 두 줄 연속 있는 것은 아닙니다. 이 함수는 GPL export됩니다.'),
        ('활성화의 NULL 경로 불일치', '__kunit_activate_static_stub는 real 주소를 먼저 NULL 검사합니다. replacement가 NULL이면 주석은 해제를 의도하지만 실제 호출은 kunit_deactivate_static_stub(test,replacement_addr)입니다. 따라서 NULL을 전달해 해제 함수의 NULL assertion에 도달합니다. real_fn_addr로 정상 해제된다고 설명하면 원본과 다릅니다. 이 코드를 학습하기 위해 임의로 수정하지 않으며 제어 흐름 대조 결과를 명시합니다.'),
        ('기존 등록 갱신', 'replacement가 non-NULL이면 기존 real 주소의 자원을 조회합니다. 있으면 ctx->replacement_addr만 새 값으로 바꾸고 조회 참조를 put합니다. 새 ctx를 항상 추가해 같은 real 주소의 등록을 계속 쌓는 구조가 아닙니다. 이 파일 자체에는 갱신을 둘러싼 별도 explicit lock이 없으므로 임의 다중 task 갱신의 안전성을 이 본문만으로 보장하지 않습니다.'),
        ('신규 등록', '없으면 GFP_KERNEL로 ctx를 kmalloc하고 NOT_ERR_OR_NULL assertion 뒤 두 주소를 저장합니다. kunit_alloc_resource에는 init callback NULL,static stub free callback,GFP_KERNEL,ctx를 넘깁니다. 반환 res를 이 분기에서 별도 검사하는 코드가 없으므로 모든 자원 등록 실패를 여기서 반드시 검출한다고 단정하지 않습니다. 내부 helper도 GPL export되며 문서는 타입 검사를 위해 매크로 사용을 요구합니다.'),
        ('검토 범위', '구조체와 free·match·lookup·deactivate·activate 전체, 두 export 및 NULL·기존·신규 분기를 대조했습니다. 자원 목록 세부 알고리즘은 kunit_find_resource 구현의 책임이고 여기서 hash lookup이라고 추정하지 않습니다. 실제 NULL assertion·할당 실패·동시 접근을 실행 검증한 것은 아닙니다.')
    ], questions=[
        ('자원이 static stub인지 확인하는 직접 조건은?', 'free callback 포인터 동일성', 'ctx의 두 주소가 같은지 여부', '종류를 먼저 확인한 뒤 real 주소 필드를 비교합니다. 데이터 형식이 다른 자원의 필드 역참조를 피합니다.'),
        ('대체 주소 조회 성공 뒤 자원 참조는?', '주소값을 복사한 뒤 put한다', '항상 영구적으로 보유한다', '찾기에서 얻은 참조를 반환하고 replacement 주소값만 돌려줍니다.'),
        ('이 원본에서 replacement=NULL로 내부 activate를 부르면?', 'NULL을 deactivate에 전달해 NULL assertion 경로에 도달한다', 'real 함수의 등록을 정상 해제한다', '실제 인수는 real_fn_addr가 아니라 replacement_addr입니다. 주석의 의도와 호출을 구분합니다.'),
        ('기존 real 주소 등록을 다시 활성화하면?', 'replacement 주소를 갱신하고 조회 참조를 놓는다', '매번 별도 등록을 무조건 추가한다', 'res가 존재하는 분기에서 ctx의 한 필드를 갱신합니다. 신규 할당은 res가 없는 else입니다.')
    ]
), dict(
    path='lib/kunit/hooks.c', title='KUnit 전역 hook 저장소: built-in key와 함수 테이블',
    intro='KUnit이 모듈이어도 필요한 공통 저장 객체 두 개와 export를 분석합니다.',
    principle='옵션 모듈이 제공하는 동작과 built-in 코드가 참조하는 공통 저장소를 분리할 수 있습니다.',
    use='선언과 정의, 정적 초기화, symbol export와 callback 설치의 차이를 학습합니다.',
    area='모듈 · static key · 함수 테이블 · 심볼 export',
    sections=[
        ('파일 목적', 'GPL-2.0 주석은 KUnit 자체가 모듈로 빌드되어도 이 코드와 구조체는 built-in이어야 한다고 설명합니다. kunit/test-bug.h를 포함하고 함수 본문은 없습니다. 실제 어떤 빌드 목록에 들어가는지는 별도 Makefile의 책임입니다.'),
        ('Key 정의와 export', 'DEFINE_STATIC_KEY_FALSE(kunit_running)로 앞 헤더에서 선언한 key를 실제 정의하고 EXPORT_SYMBOL(kunit_running)을 사용합니다. 기본 false 상태이며 이 파일에는 테스트 시작 시 key를 enable하는 코드가 없습니다. 선언용 DECLARE 매크로와 저장 객체 정의용 DEFINE을 구분합니다.'),
        ('Hook 테이블 저장소', 'struct kunit_hooks_table kunit_hooks를 정의하고 EXPORT_SYMBOL로 내보냅니다. 지정 초기화가 없는 정적 저장 객체이므로 포인터 필드는 처음 0입니다. 이 파일 자체가 fail_current_test나 get_static_stub_address callback을 채우지 않습니다. 두 객체와 두 export 전체를 검토했으며 동적 hook 설치 순서는 별도 구현과 연결해야 합니다.')
    ], questions=[
        ('이 파일이 처음부터 hook callback들을 지정하는가?', '아니다. 저장 객체만 정의해 초기 포인터는 0이다', '그렇다. 모든 callback을 같은 함수로 채운다', '테이블에 initializer가 없으며 함수 구현도 없습니다. 저장소와 동작 설치를 구분합니다.'),
        ('kunit_running의 최초 정의 상태는?', 'false static key', '항상 true인 task 포인터', 'DEFINE_STATIC_KEY_FALSE입니다. 실행 중 테스트 문맥 포인터와 다른 전역 상태입니다.')
    ]
)]
