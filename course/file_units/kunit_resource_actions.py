"""Whole-file KUnit resource/action implementation and hook installation."""
ROWS = [dict(
    path='lib/kunit/resource.c', title='KUnit 자원과 cleanup action: 등록·제거·마지막 참조',
    intro='자원 목록 관리와 action 등록·취소·실행 함수 전체를 분석합니다.',
    principle='목록에서 제거하는 것과 객체의 마지막 참조를 해제하는 것은 서로 다른 수명 단계입니다.',
    use='kref, irqsave spinlock, callback 식별과 실패 시 보상 동작을 학습합니다.',
    area='자원 수명 · 참조 카운팅 · 연결 리스트 · spinlock · cleanup action',
    sections=[
        ('전체 구성과 등록 초기화', 'GPL-2.0 파일은 resource,test,kref 헤더를 포함합니다. __kunit_add_resource는 free callback을 저장하고 kref_init으로 목록이 보유할 첫 참조를 만듭니다. init이 있으면 init(res,data)를 호출해 오류를 즉시 반환하고, 없으면 res->data=data로 둡니다. should_kfree는 초기화하지 않는다는 주석이 있으므로 호출자 책임입니다.'),
        ('Init와 목록 잠금의 범위', 'init callback은 목록 spinlock을 잡기 전에 실행합니다. 성공 후 spin_lock_irqsave 아래 list_add_tail로 등록하고 irqrestore합니다. init 오류일 때 이 helper가 free callback이나 kfree를 직접 호출하지 않습니다. 완성되지 않은 객체의 회수는 호출자 계약을 확인해야 합니다. 이 함수는 GPL export됩니다.'),
        ('목록 제거와 put', 'kunit_remove_resource는 잠금 아래 node가 비어 있었는지를 was_linked로 저장하고 list_del_init으로 제거·자기 연결 초기화를 합니다. 잠금을 푼 뒤 실제로 연결되어 있었을 때만 kunit_put_resource를 호출합니다. 이미 분리된 유효 자원에 중복 호출했을 때 목록 참조를 다시 감소시키지 않으려는 구조입니다. 이미 해제된 포인터까지 안전하게 재사용할 수 있다는 보장은 아닙니다.'),
        ('Destroy의 추가 참조', 'kunit_destroy_resource는 match와 data로 찾아 없으면 -ENOENT입니다. 있으면 remove로 목록 참조를 놓고 이어 put으로 find에서 얻은 참조를 놓은 뒤 0을 반환합니다. 다른 참조가 남아 있으면 객체의 실제 최종 해제는 늦어질 수 있습니다. 교차 확인한 header의 find는 역방향 리스트 탐색 중 일치 자원을 get하므로 조회가 단순 borrowed pointer 반환이 아닙니다.'),
        ('Action wrapper와 해제 callback', 'kunit_action_ctx는 첫 멤버 kunit_resource res, action 함수 포인터 func,void *ctx를 보관합니다. __kunit_action_free는 container_of로 바깥 객체를 얻고 func(ctx)를 호출합니다. 여기서 wrapper를 직접 kfree하지 않습니다. 확인한 resource release helper가 should_kfree일 때 res를 kfree하며, 첫 멤버 배치 때문에 할당된 wrapper 시작 주소와 연결됩니다.'),
        ('Action 등록', 'kunit_add_action은 action이 NULL이 아닌지 assertion하고 kzalloc으로 wrapper를 할당합니다. 할당 실패는 -ENOMEM입니다. func·ctx를 저장하고 res.should_kfree=true로 설정한 뒤 init=NULL인 __kunit_add_resource를 호출합니다. 주석대로 이 등록 경로는 init callback 실패가 없습니다. 등록 시 action 자체를 즉시 실행하지 않고 자원 free callback으로 연결합니다.'),
        ('등록 실패 시 reset', 'kunit_add_action_or_reset은 add의 반환이 nonzero이면 action(ctx)를 즉시 실행하고 같은 오류값을 반환합니다. cleanup 등록을 못한 경우 이미 준비된 자원을 보상 처리하는 용도입니다. 성공했을 때도 action을 즉시 실행하는 함수가 아닙니다. NULL action assertion으로 비정상 중단되는 경우까지 정상적인 반환 오류처럼 설명하지 않습니다.'),
        ('Action 매칭', '__kunit_action_match는 res->free가 action free callback인지 먼저 확인한 뒤 func와 ctx 포인터가 모두 같은지 비교합니다. context가 가리키는 객체의 내용 비교나 함수 이름 문자열 비교가 아닙니다. test 인수는 본문에서 사용하지 않습니다. 같은 함수라도 다른 context는 별도 action입니다.'),
        ('Remove와 release의 차이', 'kunit_remove_action은 찾은 res->free를 NULL로 바꾼 뒤 remove와 put을 하므로 등록 action을 실행하지 않고 취소합니다. kunit_release_action은 free를 유지한 채 remove와 put을 하므로 마지막 참조 해제에서 action이 실행됩니다. 다른 참조가 보유되어 있다면 실행 시점은 그 참조 해제까지 늦어질 수 있습니다. 두 함수 모두 찾지 못하면 아무 작업도 하지 않고 void로 끝납니다.'),
        ('탐색 순서와 검토 범위', 'add는 tail에 추가하고 header의 find는 역순으로 탐색하므로 같은 func·ctx가 여러 번 등록되면 가장 최근의 일치 항목부터 찾습니다. 이 파일은 조회 helper를 호출하며 직접 별도 hash table을 구현하지 않습니다. 모든 등록·제거·destroy·action callback·reset·match·remove·release와 GPL export를 대조했습니다. header 전체를 이 파일 완료에 포함하지 않으며 실제 할당 실패·동시 접근 테스트를 실행한 것은 아닙니다.')
    ], questions=[
        ('__kunit_add_resource가 should_kfree도 초기화하는가?', '아니다. 호출자가 정한다', '그렇다. 언제나 true로 바꾼다', '주석이 명시적으로 초기화하지 않는다고 설명합니다. action wrapper는 호출 전에 true를 설정합니다.'),
        ('kunit_remove_resource의 put은 어느 잠금 구간에서 실행되는가?', '목록 spinlock을 푼 뒤', '반드시 irqsave 잠금을 잡은 채', '삭제는 임계 구역 안에서, 참조 반환은 밖에서 수행합니다. 마지막 free callback의 실행 범위와 관련됩니다.'),
        ('Destroy가 remove 뒤 다시 put하는 이유는?', 'find가 얻은 추가 참조를 놓기 위해서다', '같은 목록 참조를 실수로 두 번 감소시키기 위해서다', '목록의 참조와 조회자의 참조는 별개입니다. 두 소유권을 각각 반환합니다.'),
        ('add_action_or_reset이 action을 즉시 부르는 경우는?', '등록 함수가 오류를 반환했을 때', '항상 등록 직후', 'res가 nonzero일 때만 보상 동작을 실행합니다. 성공 경로는 후속 자원 해제에 맡깁니다.'),
        ('remove_action과 release_action의 핵심 차이는?', 'remove는 free callback을 지워 실행을 취소하고 release는 유지한다', '둘 다 반드시 action을 두 번 실행한다', '동일한 remove·put 흐름 앞에서 callback을 NULL로 만드는지 여부가 다릅니다.'),
        ('같은 action 함수에 다른 ctx 포인터를 주면 동일 등록으로 매칭되는가?', '아니다. 함수와 context가 둘 다 같아야 한다', '그렇다. 함수 이름만 비교한다', 'match는 두 포인터의 동등성을 AND로 검사합니다. 객체 내용 비교도 아닙니다.')
    ]
), dict(
    path='lib/kunit/hooks-impl.h', title='KUnit hook 설치: 두 구현 주소를 공통 테이블에 연결',
    intro='구현 함수 선언과 inline 설치 함수 전체를 분석합니다.',
    principle='공통 테이블의 저장소 정의와 실제 callback 연결은 별도 단계로 관리할 수 있습니다.',
    use='extern 함수 선언, format annotation, 포인터 대입과 실행 상태를 구분합니다.',
    area='callback · 모듈 연결 · 함수 테이블 · KUnit',
    sections=[
        ('헤더와 구현 선언', 'GPL-2.0 guard 안에 test-bug.h를 포함합니다. __kunit_fail_current_test_impl은 file,line,fmt,...를 받는 void 함수이며 __printf(3,4) annotation을 가집니다. __kunit_get_static_stub_address_impl은 test와 real 주소를 받아 void *를 반환합니다. 실제 함수 본문은 여기 없고 다른 C 파일에 있습니다.'),
        ('설치 함수 전체', 'kunit_install_hooks는 static inline void 함수이며 kunit_hooks.fail_current_test와 get_static_stub_address에 각각 구현 함수 주소를 대입합니다. callback을 즉시 호출하거나 테스트를 실행하는 코드가 아닙니다. 포인터를 0으로 초기화한 전역 저장소가 실제 동작을 가리키게 하는 연결 단계입니다.'),
        ('설치와 실행 key는 별개', '함수에는 kunit_running static key를 enable하는 명령,잠금,teardown 또는 모듈 참조 획득이 없습니다. hook을 설치한 것만으로 현재 task가 KUnit test 문맥을 갖는다고 가정하면 안 됩니다. 두 선언·포맷 annotation·대입 두 개와 guard를 모두 검토했습니다. 호출 시점과 동기화의 전체 계약은 호출부에서 확인해야 합니다.')
    ], questions=[
        ('kunit_install_hooks는 등록한 함수를 바로 실행하는가?', '아니다. 두 함수 포인터를 대입한다', '그렇다. 현재 테스트를 무조건 실패시킨다', '본문은 대입 두 줄입니다. 함수 주소 연결과 callback 호출을 구분합니다.'),
        ('설치 함수가 kunit_running도 true로 바꾸는가?', '아니다. 이 함수에는 key 갱신이 없다', '그렇다. 함수 포인터 대입이 key를 자동 변경한다', 'hook 저장소와 실행 상태 key는 별개 자료입니다. 이 파일에 없는 전환을 추정하지 않습니다.')
    ]
)]
