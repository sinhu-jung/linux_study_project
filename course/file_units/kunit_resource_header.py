"""Whole-file resource API, ownership, matching and deferred actions."""
ROWS = [dict(
    path='include/kunit/resource.h', title='KUnit resource API: 소유권·역순 검색·타입 안전한 cleanup',
    intro='자원 구조체, 모든 inline 함수, callback 타입과 action 선언의 계약을 분석합니다.',
    principle='데이터 포인터를 받는 것과 참조를 소유하는 자원 객체를 받는 것은 서로 다른 API 계약입니다.',
    use='참조 카운팅, 연결 리스트 검색, 임계 구역, 오류 회수와 CFI를 실제 코드에 연결합니다.',
    area='자료구조 · 소유권 · 동시성 · callback · 테스트 격리',
    sections=[
        ('헤더와 데이터 구조', 'GPL-2.0 guard 안에서 test,kref,list,slab,spinlock을 포함합니다. init callback은 resource와 void context를 받아 int를 반환하고 free callback은 resource를 받아 void를 반환합니다. kunit_resource는 data,name,free와 내부 refcount,node,should_kfree를 보관합니다. 이름과 데이터는 포인터이며 구조체에 내용을 복제하는 배열이 아닙니다.'),
        ('예제의 두 할당', '문서의 kmalloc 예제는 size와 gfp를 지역 params에 넣어 init에 전달합니다. init은 kmalloc으로 data를 만들고 실패하면 -ENOMEM, 성공하면 0입니다. free는 data를 kfree합니다. params 포인터를 장기 보관하는 예제가 아니라 등록 과정에서 동기적으로 init에 전달하는 예제입니다. 자원 wrapper와 실제 data의 할당·해제는 별개입니다.'),
        ('Get과 put의 소유권', 'get은 kref_get,put은 release callback을 지정한 kref_put입니다. 목록 자체의 참조 외에 alloc_and_get 또는 find로 받은 참조를 호출자가 put해야 합니다. alloc_resource는 data만 돌려주고 자원 객체의 추가 참조를 전달하지 않습니다. data를 resource 포인터처럼 put하면 안 됩니다.'),
        ('마지막 참조의 해제 순서', 'release는 container_of로 kref의 바깥 resource를 얻고 free가 있으면 먼저 호출합니다. 이어 should_kfree를 읽어 참이면 resource 자체를 kfree합니다. 따라서 callback 이후에도 res가 유효해야 합니다. 특히 should_kfree인 경우 callback이 wrapper까지 해제하면 후속 접근과 중복 해제 문제가 생깁니다. 이 helper를 직접 호출하지 말라는 주석도 있습니다.'),
        ('외부 객체 등록', '__kunit_add_resource는 이 헤더에서 선언되며 should_kfree를 초기화하지 않는 계약입니다. init이 없으면 data를 직접 저장하고 있으면 init에 전달합니다. kunit_add_resource는 should_kfree=false를 먼저 설정해 외부 wrapper를 자동 kfree하지 않도록 합니다. name을 초기화하는 코드는 없으므로 호출자가 제공하는 구조체 상태도 중요합니다.'),
        ('이름 등록의 실패와 수명', 'add_named는 name=NULL이면 -EINVAL입니다. 기존 동일 이름을 find한 경우 얻은 참조를 put한 뒤 -EEXIST입니다. 없으면 res->name=name,should_kfree=false로 두고 내부 등록 helper를 호출합니다. strdup나 이름 해제가 없으므로 이름 저장소 수명은 호출자가 관리해야 합니다. 중복 검사와 등록을 하나의 잠금 구간으로 묶지 않으므로 동시 등록까지 원자적 유일성을 보장한다고 설명할 수 없습니다.'),
        ('Alloc and get', 'alloc_and_get은 internal_gfp로 wrapper를 kzalloc하고 실패하면 NULL입니다. should_kfree=true로 등록을 시도한 후 성공하면 get을 추가해 resource 포인터를 반환합니다. 정상적인 등록 직후에는 목록 참조와 호출자 참조가 있습니다. 호출자가 put해도 목록 참조가 남아 있으면 아직 free callback이 실행되지 않습니다.'),
        ('Alloc data와 실패 경로', 'alloc_resource도 wrapper를 kzalloc하고 should_kfree=true로 등록하지만 성공 반환은 res->data이며 추가 get은 없습니다. 두 할당 inline 함수 모두 내부 등록이 오류를 반환할 때 단순 NULL 반환이며 명시적 kfree(res)가 없습니다. 교차 확인한 resource.c도 init 오류에서 자동 free하지 않으므로 모든 실패가 완전 회수된다고 단정하면 안 됩니다. 또한 data가 NULL인 성공 등록까지 이 API가 금지하지 않으므로 NULL 결과만으로 내부 상태 전부를 추론할 수 없습니다.'),
        ('GFP와 사용자 context', 'internal_gfp는 wrapper 할당에 적용합니다. init 안에서 data를 어떻게 할당할지는 callback이 정하며 예제는 params.gfp를 별도로 사용합니다. 두 할당의 context 제약이 자동으로 같아지는 것이 아닙니다. 호출 환경에서 sleep 가능 여부 등을 만족하는 allocation flag를 선택해야 한다는 문서의 주의가 있습니다.'),
        ('이름 비교', 'match 타입은 test,res,match_data를 받아 bool을 반환합니다. name_match는 res->name이 NULL이 아닌지 먼저 확인한 뒤 strcmp==0을 검사합니다. 포인터 주소가 달라도 문자열이 같으면 일치합니다. test 인수는 여기서 사용하지 않습니다. match_name 자체의 NULL을 방어하지 않으므로 NULL 검색 이름을 안전한 조회로 가정하지 않습니다.'),
        ('역방향 선형 검색과 잠금', 'find는 test->lock을 spin_lock_irqsave로 잡고 resources를 list_for_each_entry_reverse로 순회합니다. 일치하면 get한 후 break하고 irqrestore 뒤 반환하며 없으면 NULL입니다. match callback도 잠금 안에서 실행하므로 잠들거나 같은 lock을 재획득하는 동작을 넣으면 안 됩니다. n개 원소와 비교 비용 m이면 최악 O(n*m)이며 hash 조회가 아닙니다. 역순 첫 일치가 선택됩니다.'),
        ('찾기·삭제 wrapper', 'find_named는 name_match와 이름을 일반 find에 넘깁니다. destroy_named도 같은 비교 함수를 외부 destroy 선언에 전달합니다. destroy의 문서는 못 찾으면 -ENOENT라고 설명합니다. remove 선언의 문서는 목록에서 제거해도 조회자가 참조를 갖고 있으면 즉시 해제되지 않으며 마지막 put이 필요하다고 강조합니다. 삭제와 물리적 메모리 회수는 다른 단계입니다.'),
        ('Action 타입과 CFI wrapper', 'kunit_action_t는 void(void *)라는 함수 타입 typedef이며 API 인수에서 *를 붙여 함수 포인터로 사용합니다. KUNIT_DEFINE_ACTION_WRAPPER는 static void wrapper(void *in)를 만들고 in을 arg_type 변수로 변환해 orig(arg)를 호출합니다. 하나의 pointer-sized 인수를 받는 함수에 쓰는 계약입니다. 함수 포인터 자체를 강제 캐스팅하면 CFI 타입 검사를 깨뜨릴 수 있으므로 올바른 시그니처의 wrapper를 만드는 방식입니다.'),
        ('Action 등록과 보상', 'add_action은 정상 종료나 assertion 등 조기 종료 시 cleanup을 예약하며 등록의 역순으로 실행한다는 계약입니다. add_action_or_reset은 등록할 수 없으면 action(ctx)를 즉시 호출하고 오류를 반환합니다. 성공 시 즉시 실행하는 함수가 아닙니다. 여러 자원을 A 다음 B 순서로 준비했다면 역순 B,A 해제가 의존 관계를 풀 때 유용합니다.'),
        ('취소와 조기 실행', 'remove_action은 동일 함수/context 쌍의 가장 최근 등록 하나를 취소합니다. release_action은 가장 최근 등록을 지금 실행하고 그 등록은 테스트 종료 때 다시 실행하지 않는다는 계약입니다. 중복 등록 전부를 제거하는 API가 아닙니다. 구현에서 실제 실행은 자원 마지막 참조 해제에 연결되므로 내부 resource 참조를 별도로 유지하는 경우의 수명까지 즉시 실행 문구만으로 단정하지 않습니다.'),
        ('전체 범위와 검증 한계', 'guard,예제,구조체,세 callback 타입,get/release/put,일반·이름 등록,두 할당,이름 비교와 역순 조회,이름 wrapper,삭제 선언,action wrapper와 네 action 선언을 모두 대조했습니다. 문서 계약과 코드상 오류 회수의 차이를 구분했습니다. 실제 커널의 OOM,CFI 위반 또는 동시 등록을 실행한 검증은 아닙니다.')
    ], questions=[
        ('alloc_resource와 alloc_and_get_resource의 반환·참조 차이는?', '전자는 data, 후자는 추가 참조를 가진 resource를 반환한다', '둘 다 data를 반환하며 반드시 같은 put을 호출한다', '후자만 성공 경로에서 get을 추가합니다. 반환 타입과 소유권을 함께 읽어야 하며 전자의 data에 put을 적용하면 안 됩니다.'),
        ('should_kfree=true인 resource의 free callback이 wrapper 자체도 해제해도 되는가?', '안 된다. callback 뒤 wrapper를 다시 읽고 kfree한다', '된다. callback 뒤에는 wrapper 접근이 전혀 없다', 'release는 callback 다음에 res->should_kfree를 검사합니다. data 해제와 wrapper 해제를 분리해야 합니다.'),
        ('find의 match callback에서 잠들 수 있는 작업을 해도 되는가?', '안 된다. irqsave spinlock을 잡은 상태에서 호출한다', '된다. 모든 비교 직전에 잠금을 푼다', '잠금 범위는 전체 역순 순회와 get까지 포함합니다. callback 실행 환경을 호출부에서 추적하는 문제입니다.'),
        ('동일 이름 등록 검사가 동시 등록까지 원자적 유일성을 보장하는가?', '이 코드만으로는 아니다. 조회와 등록이 분리되어 있다', '그렇다. 이름을 저장하면 자동으로 모든 경쟁이 차단된다', '기존 항목 검색과 새 항목 추가를 하나의 임계 구역으로 묶지 않습니다. 순차 중복 검출과 경쟁 없는 유일성은 구분해야 합니다.'),
        ('내부 등록이 실패하면 두 alloc helper가 wrapper를 명시적으로 회수하는가?', '아니다. 이 실패 경로에는 NULL 반환만 있다', '그렇다. 반드시 kfree 후 NULL을 반환한다', 'kzalloc 실패 경로와 kzalloc 성공 후 init 실패 경로를 나누어 읽어야 합니다. 구현에 없는 rollback을 추정하면 누수 검토를 놓칩니다.'),
        ('name_match가 비교하는 것은?', 'NULL 아닌 저장 이름과 검색 이름의 문자열 내용', '두 이름 포인터의 주소만', 'strcmp==0이 핵심입니다. 저장 이름은 NULL 방어가 있지만 검색 이름은 같은 검사를 하지 않습니다.'),
        ('Action 함수 포인터를 캐스팅하는 대신 wrapper를 만드는 이유는?', '기대하는 함수 시그니처로 호출해 CFI 계약을 지키기 위해서다', 'callback이 반드시 별도 스레드에서 실행되게 하기 위해서다', 'wrapper는 void *를 받은 뒤 인수 값을 변환하고 원래 함수를 호출합니다. 스레드 생성 코드는 없습니다.'),
        ('동일 action/context를 세 번 등록한 뒤 remove_action을 한 번 하면?', '가장 최근 일치 등록 하나가 취소된다', '세 등록이 모두 즉시 실행되고 지워진다', '문서는 가장 최근 하나를 대상으로 한다고 명시합니다. 역순 탐색의 첫 일치 선택과 연결해 이해할 수 있습니다.')
    ]
)]
