"""Whole page extension header, with implementation-backed lifetime notes."""
ROWS = [dict(
    path='include/linux/page_ext.h',
    title='페이지 확장 인터페이스: 가변 레코드와 RCU 접근 수명',
    intro='페이지별 부가 정보를 위한 client 계약, 공유 플래그, 메모리 모델별 초기화와 포인터 계산을 해설합니다.',
    principle='C 구조체의 정적 크기와 실제 레코드 간격을 구분하고, get/put의 이름 대신 구현으로 수명 보호 방식을 확인합니다.',
    use='page idle·page owner 등 여러 기능이 페이지 확장 공간을 함께 사용하는 구조를 이해합니다.',
    area='확장 레코드 · 콜백 · 간접 주소 지정 · RCU · 구성별 인터페이스',
    sections=[
        ('파일의 전체 경계', 'GPL-2.0, guard, types.h와 stacktrace.h 포함 및 pglist_data 전방 선언 뒤에 PAGE_EXTENSION 활성/비활성 분기가 있습니다. 활성 분기는 client 구조, 플래그, page_ext 구조, 외부 변수와 함수, 주소 계산 helper를 제공합니다. 실제 메모리 할당·hotplug 처리·조회 알고리즘 본문은 mm/page_ext.c에 있습니다.'),
        ('Client 등록 계약', 'page_ext_operations의 offset과 size는 size_t이며 각각 레코드 내부 client 데이터 위치와 크기입니다. need는 bool을 반환하는 인자 없는 함수 포인터이고 init은 void를 반환하는 선택적 함수 포인터입니다. need_shared_flags는 공용 flags 사용 여부입니다. 주석은 각 client가 page_ext_ops 배열에 operations를 등록하고 초기화 과정에서 offset을 돌려받는다고 설명합니다. 이 구조체 자체가 client 목록이나 동적 등록 함수를 구현하지는 않습니다.'),
        ('공유 플래그의 인덱스', 'page_ext_flags는 OWNER=0, OWNER_ALLOCATED=1을 정의합니다. PAGE_IDLE_FLAG && !64BIT일 때 YOUNG=2, IDLE=3이 이어집니다. 값들은 비트 마스크가 아니라 비트 인덱스입니다. 주석은 이 플래그를 사용하는 client가 need_shared_flags=true로 설정해야 한다고 요구합니다. idle 기능이 꺼져도 두 owner 인덱스는 PAGE_EXTENSION 활성 분기에서 정의됩니다.'),
        ('구조체 크기와 실제 레코드', 'struct page_ext의 명시적 멤버는 unsigned long flags 하나입니다. 그러나 전체 레코드의 간격은 외부 변수 page_ext_size이며 sizeof(struct page_ext)와 항상 같지 않습니다. 관련 구현의 invoke_need_callbacks를 대조하면 필요한 client 중 공유 플래그 사용자가 있을 때 기본 flags 공간을 확보하고, 필요한 client마다 offset을 현재 크기로 정한 뒤 size를 누적합니다. 따라서 모든 구성에서 flags 공간이 무조건 첫머리에 존재한다고 가정해서는 안 됩니다. 이 함수 대조는 page_ext.c 전체 완료가 아닙니다.'),
        ('할당 주석과 접근 가능성', '주석은 확장 mem_map 관점으로 설명하고 부팅이나 memory hotplug에서 각 page descriptor에 대응하는 공간을 할당한다고 합니다. 그렇다고 임의 페이지에 대한 get이 언제나 성공하는 것은 아닙니다. 관련 구현의 계약은 해당 페이지에 page_ext가 없으면 NULL을 반환한다고 명시합니다. 구성, 초기화와 수명 경계를 고려하여 호출자는 NULL을 처리해야 합니다.'),
        ('Early 설정과 pgdat', 'early_page_ext는 extern bool, page_ext_size는 extern unsigned long입니다. early_page_ext_enabled는 활성 구성에서 변수를 그대로 반환합니다. pgdat_page_ext_init은 pglist_data 포인터를 받는 외부 초기화 함수입니다. 이 헤더에는 early 설정을 결정하는 명령행 파서나 pgdat 초기화 본문이 없습니다. 이름만 보고 이 함수를 일반 런타임 상태 전환 API로 해석하지 않습니다.'),
        ('Sparse와 flat 초기화 경로', 'SPARSEMEM이면 page_ext_init이 외부 함수이고 page_ext_init_flatmem 및 flatmem_late는 빈 inline입니다. 비 sparse이면 반대로 두 flatmem 함수가 외부 선언이고 page_ext_init은 빈 inline입니다. 이름이 여러 개여도 모든 메모리 모델에서 세 초기화가 모두 실제 동작하는 것은 아닙니다. 분기가 공통 호출 지점에 맞는 인터페이스를 제공합니다.'),
        ('Get과 put의 실제 의미', '헤더는 const struct page 포인터를 받는 page_ext_get과 page_ext 포인터를 받는 put을 선언합니다. page_ext.c의 해당 본문을 확인하면 get은 rcu_read_lock 후 lookup하며 실패하면 즉시 unlock하고 NULL을 반환합니다. 성공한 경우에는 put이 RCU 읽기 구간을 끝냅니다. put(NULL)은 아무 동작도 하지 않습니다. get/put이라는 이름만으로 참조 카운터 증가·감소나 새 메모리 할당이라고 설명하면 틀립니다.'),
        ('접근 수명의 제한', '구현 주석은 성공한 get에서 put까지 page_ext의 유효성을 보호하며 그 사이 호출자가 잠들면 안 된다고 명시합니다. put 이후에는 확장 정보가 유효하지 않을 수 있습니다. RCU 수명 보호가 같은 flags나 client 데이터에 대한 모든 동시 쓰기를 직렬화하는 mutex라는 의미는 아닙니다. 데이터 갱신의 동시성 규칙은 각 client와 비트 연산을 별도로 확인해야 합니다.'),
        ('Client 데이터 주소', 'page_ext_data는 page_ext를 void 포인터로 변환한 후 ops->offset을 더해 반환합니다. 커널에서 사용하는 GNU C의 void 포인터 산술로 바이트 단위 이동을 표현합니다. NULL 확인, size 범위 확인, 정렬 보정은 본문에 없습니다. 올바른 operations와 초기화된 offset 및 유효한 레코드를 전달해야 하며 반환형이 void 포인터라고 데이터 타입을 런타임에 검증해 주지는 않습니다.'),
        ('다음 레코드의 주소', 'page_ext_next는 curr를 void 포인터 next에 담아 page_ext_size만큼 더하고 struct page_ext 포인터로 반환합니다. curr+1이면 구조체의 정적 크기만 이동하므로 확장 payload가 있는 레코드에서 다릅니다. 예를 들어 구조체 크기가 8바이트, 실제 간격이 40바이트면 다음 주소는 현재+40입니다. 이 helper에는 마지막 레코드 판별, 범위 검사, 새로운 RCU 구간 획득이 없습니다.'),
        ('기능이 없는 구성', 'PAGE_EXTENSION이 없으면 struct page_ext는 불완전 타입으로만 선언됩니다. early 조회는 false, pgdat와 세 초기화 함수 및 put은 빈 함수, get은 NULL입니다. 활성 분기의 operations 구조, 플래그 enum, page_ext_size와 주소 계산 helper가 이 분기에 다시 제공되는 것은 아닙니다. 공통 API가 stub으로 존재한다는 사실을 전체 자료형과 기능이 모두 사용 가능하다는 뜻으로 넓히지 않습니다.'),
        ('CS 학습 연결', '가변 payload를 가진 고정 간격 레코드 배열, client별 offset을 통한 데이터 분할, 선택적 콜백과 기능 제거, RCU 읽기 수명과 데이터 동기화의 구분을 학습합니다. 포인터 helper의 짧은 본문은 호출자 전제에 많은 책임을 맡깁니다. 원본 대응·학습 데이터 검사는 hotplug 경쟁이나 모든 커널 구성의 실행 검증이 아닙니다.')
    ],
    questions=[
        ('page_ext_next(curr)를 curr+1로 바꾸어도 항상 같은가?', '아니다. 실제 레코드 간격은 page_ext_size이다', '그렇다. struct page_ext의 크기가 모든 client 데이터를 포함한다', '구조체에는 flags만 명시되어 있고 client 공간은 별도로 누적됩니다. helper는 정적 sizeof 대신 실제 레코드 간격을 사용합니다.'),
        ('page_ext_get과 put은 참조 카운터 증가·감소인가?', '해당 구현은 RCU 읽기 구간 획득·해제이다', '항상 page_ext 안의 참조 카운터를 증가·감소한다', 'get은 rcu_read_lock 후 조회하고 실패하면 해제합니다. 성공한 포인터의 put에서 rcu_read_unlock합니다. 함수 이름만으로 보호 기법을 추측하면 안 됩니다.'),
        ('PAGE_EXT_YOUNG가 2인 구성에서 이 값은 비트 마스크 2인가?', '아니다. 2번 비트의 인덱스이다', '그렇다. 1번 비트를 뜻하는 마스크이다', 'enum은 bitops에 넘길 인덱스를 정의합니다. 해당 인덱스의 마스크를 만든다면 1UL<<2, 즉 4입니다.'),
        ('SPARSEMEM일 때 page_ext_init_flatmem은 확장 공간을 실제 초기화하는가?', '아니다. 빈 inline이며 page_ext_init이 외부 함수이다', '그렇다. 세 초기화 함수가 모두 같은 일을 한다', '헤더는 메모리 모델에 맞춰 실제 선언과 빈 helper를 교차 배치합니다. 함수 이름의 존재와 실제 동작을 구분해야 합니다.'),
        ('page_ext_data가 ops->offset의 범위와 포인터 유효성을 검사하는가?', '아니다. 바이트 offset을 더해서 반환한다', '그렇다. 범위를 벗어나면 NULL을 반환한다', '본문에는 산술과 반환만 있습니다. 유효한 레코드, 초기화된 operations, 데이터의 적절한 정렬과 범위는 호출 경로에서 보장해야 합니다.')
    ]
)]
