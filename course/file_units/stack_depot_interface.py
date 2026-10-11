"""Whole stack depot header and source-checked API caveats."""
ROWS = [dict(
    path='include/linux/stackdepot.h',
    title='Stack depot 인터페이스: 중복 제거 저장소와 압축 핸들',
    intro='호출 스택 저장소의 핸들 비트 배치, 레코드 수명, 초기화와 저장·조회·출력 API를 전체 헤더로 학습합니다.',
    principle='동일한 stack 배열을 공유하는 공간 절약과 그 공유 레코드의 수명 관리는 별개의 계약입니다.',
    use='KASAN과 page owner처럼 많은 할당 이력을 저장하는 기능의 공통 자료구조를 이해합니다.',
    area='중복 제거 · 해시 테이블 · 비트 필드 · 참조 카운트 · union 수명 · 메모리 풀',
    sections=[
        ('전체 구성과 동기', 'GPL-2.0-or-later, 저작권·작성자 설명, guard와 gfp.h 뒤 핸들 상수, 조건부 내부 구조, 저장 플래그, 초기화와 API 선언이 이어집니다. KASAN처럼 객체마다 할당·해제 stack을 저장하면 반복이 많아 공유 저장이 유리합니다. 주석의 객체당 256바이트와 약 100배 절약은 동기 설명의 예이며 모든 workload의 보장 비율이 아닙니다. 헤더에는 해시 탐색 본문이 없습니다.'),
        ('32비트 핸들 공간', 'depot_stack_handle_t는 u32이고 DEPOT_HANDLE_BITS는 sizeof(handle)*8입니다. STACK_DEPOT_EXTRA_BITS=5는 사용자가 별도 정보를 넣는 부분입니다. 이 핸들은 raw pointer가 아니며 같은 스택을 가리키는 핸들에 서로 다른 extra를 붙일 수 있습니다. 0은 저장 실패를 나타내는 값이므로 유효한 참조처럼 취급하지 않습니다.'),
        ('Pool과 offset 비트 계산', 'DEPOT_POOL_ORDER=2이므로 pool은 기본 페이지 4개, 크기는 1LL<<(PAGE_SHIFT+2)입니다. DEPOT_STACK_ALIGN=4는 구현상 1<<4, 즉 16바이트 정렬의 지수입니다. offset 폭은 2+PAGE_SHIFT-4이고 pool index 폭은 32에서 offset 폭과 extra 5를 뺍니다. 4KiB 페이지라면 pool 16KiB, offset 10비트, pool index 17비트입니다. offset 필드는 바이트 수 자체가 아니라 16바이트 단위 값을 담습니다.'),
        ('조건부 비트 필드 구조', 'CONFIG_STACKDEPOT이면 handle_parts union은 u32 handle과 pool_index_plus_1, offset, extra 비트 필드를 겹칩니다. 구현은 index에 1을 더해 넣고 복원할 때 1을 뺍니다. 이 구조는 커널 내부 표현이며 C bitfield 선언만으로 모든 아키텍처의 파일 직렬화 바이트 순서까지 같다고 주장하지 않습니다. extra를 수정하는 공인 helper를 사용해야 합니다.'),
        ('Stack record의 항목', 'stack_record에는 해시 버킷 연결용 list_head, u32 hash, u32 size, 초기화 뒤 일정한 handle, refcount_t count가 있습니다. size는 프레임 수이고 entries는 unsigned long 주소를 MAX_FRAMES개까지 담습니다. list_head가 있다고 트리나 정렬 배열이라고 해석하지 않습니다. 비교·해시 충돌 해결의 본문은 lib/stackdepot.c에 따로 있습니다.'),
        ('Union 재사용 불변식', 'entries 배열과 free_list 및 rcu_state는 union으로 같은 공간을 사용합니다. 주석은 refcount가 0인 레코드만 freelist에 넣고 그런 레코드는 유효한 stack으로 취급하지 않는다고 명시합니다. freelist에서 빠져 count가 양수가 되면 다시 반환될 때까지 free 관리 필드를 접근하면 안 됩니다. 동시 사용할 필요가 없는 두 상태의 저장 공간을 재활용하는 설계입니다.'),
        ('저장 플래그 두 개', 'depot_flags_t는 u32이며 CAN_ALLOC=1, GET=2, FLAGS_NUM=2, MASK=3입니다. CAN_ALLOC은 pool 공간이 부족할 때 GFP 인자로 보충 할당할 수 있게 하고, 꺼져 있으면 여유가 없는 새 stack 저장은 실패할 수 있습니다. GET은 기존 stack을 공유할 때 참조를 얻는 방식입니다. GFP 할당 플래그와 depot 자체의 플래그는 서로 다른 인자입니다.'),
        ('초기화의 세 경로', 'ALWAYS_INIT 구성으로 mm_init에서 초기화하거나, early_init 완료 전 부팅 초기에 request_early_init을 호출하거나, mm_init 이후 사용을 위해 stack_depot_init을 호출하는 세 방식을 설명합니다. early_init 자체는 mm_init에서만 호출해야 한다는 주석이 있습니다. 초기화 요청과 완료는 같은 동작이 아니며 save 전에 기능 구성과 초기화를 모두 보장해야 합니다.'),
        ('기능 없는 구성의 정확한 범위', 'CONFIG_STACKDEPOT이 없으면 init과 early_init은 0을 반환하는 stub이고 request_early_init은 빈 함수입니다. save/fetch/print까지 기능 없는 stub이 제공되는 것은 아닙니다. 해당 선언은 보이더라도 헤더 주석은 호출자가 기능 활성 및 초기화를 보장하라고 명시합니다. 내부 union과 record 정의도 활성 분기 안에 있습니다.'),
        ('Save_flags와 문맥 주석의 모순', 'save_flags는 entries, nr_entries, GFP와 depot flags를 받아 실패 시 0, 성공 시 핸들을 반환합니다. interrupt stack은 interrupt 진입까지의 부분만 저장한다고 설명합니다. Context 문장의 할당 불가능 문맥에서 CAN_ALLOC 설정이 필요하다는 표현은 같은 주석 앞부분 및 구현과 반대입니다. 구현은 can_alloc이 참일 때 alloc_pages를 호출할 수 있으므로 할당을 피해야 하는 호출은 CAN_ALLOC을 제외해야 합니다. 이것만으로 모든 문맥의 전체 안전성을 증명하지는 않습니다.'),
        ('Save와 GET/put의 대응', 'stack_depot_save는 GET 없이 CAN_ALLOC만 전달하는 구현입니다. GET 방식의 신규 레코드는 count=1이고 공유 시 참조를 증가시키며 필요 없어지면 put해야 합니다. GET 없는 방식의 레코드는 구현에서 포화 참조값으로 지속 보존하고, 그 방식으로 얻은 핸들에 나중에 put하는 것은 구현 주석상 잘못된 사용입니다. 헤더의 put 설명 안 stack_depot_evict라는 이름은 현재 선언된 함수명 put과 다른 오래된 표기입니다.'),
        ('Fetch와 내부 포인터', '__stack_depot_get_stack_record는 내부 용도의 record 포인터 조회입니다. fetch는 unsigned long **entries에 프레임 배열 주소를 써 주고 프레임 수를 반환합니다. 구현은 출력을 먼저 NULL로 초기화하며 실패 시 0입니다. 호출자가 준 배열에 모든 주소를 복사하는 API가 아니므로 반환된 내부 저장소의 수명을 지켜야 합니다. put 이후 사용이나 손상된 핸들을 유효하다고 가정하면 안 됩니다.'),
        ('출력 API', 'print는 핸들의 stack을 출력하고 반환형은 void입니다. snprint는 핸들, 버퍼, 버퍼 크기, 선행 공백 수를 받아 문자열 출력 길이를 int로 반환합니다. 연결된 stack_trace_snprint 구현은 snprintf의 요구 길이를 누적하므로 잘리면 실제 저장 바이트 수보다 클 수 있고, 이후 미처리 프레임의 길이까지 포함하지는 않습니다. fetch의 반환은 프레임 수이므로 단위를 혼동하지 않습니다. 출력 helper가 새로운 저장 참조를 자동으로 소유권 이전해 준다는 계약은 없습니다.'),
        ('Extra 비트의 반환값', 'set_extra_bits는 원래 핸들과 unsigned int 값을 받아 수정된 핸들을 반환하며 __must_check가 붙습니다. 입력 변수 자체를 포인터로 바꾸는 함수가 아닙니다. 구현은 핸들 0이면 그대로 0이고 extra 비트 필드에 값을 넣으므로 표현 범위는 5비트, 0~31입니다. get_extra_bits는 그 필드를 반환합니다. 임의로 더 큰 정보를 잃지 않고 저장할 수 있다고 가정하지 않습니다.'),
        ('CS 연결과 완료 범위', '동일 배열의 공유로 공간을 절약하는 중복 제거, 풀 주소를 작은 정수로 나타내는 압축, 참조 카운트와 free 상태에 따른 union 재사용, 선언 문서와 실행 코드 대조를 학습합니다. lib/stackdepot.c 일부 확인은 해당 구현 파일 전체 완료나 동시 실행 시험으로 계산하지 않습니다.')
    ],
    questions=[
        ('4KiB 기본 페이지에서 pool 크기와 offset 비트 수는?', '16KiB와 10비트이다', '4KiB와 4비트이다', 'pool order 2는 4페이지입니다. offset 폭은 2+12-4=10이고 16바이트 단위 위치를 나타냅니다.'),
        ('entries와 free_list를 같은 union 공간에 두는 전제는?', '참조가 0인 free 상태와 유효한 stack 상태에서 접근할 필드가 분리된다', '두 데이터를 동시에 쓰더라도 C가 자동으로 다른 공간에 저장한다', 'union은 공간을 겹칩니다. refcount와 freelist 상태 불변식이 있기 때문에 재사용할 수 있습니다.'),
        ('CAN_ALLOC을 켜면 메모리 할당이 불가능한 문맥에서도 할당을 피하는가?', '아니다. 이 비트는 pool 보충 할당을 허용한다', '그렇다. 헤더 Context 문장을 문자 그대로 적용하면 된다', '구현은 can_alloc이 참일 때 alloc_pages를 호출할 수 있습니다. 모순된 주석을 구현과 대조해야 합니다.'),
        ('stack_depot_fetch 반환값과 entries 출력은 각각 무엇인가?', '프레임 수와 내부 프레임 배열의 주소이다', '출력 문자열 바이트 수와 새로 복사한 문자열이다', '문자열 출력은 snprint의 역할입니다. fetch가 돌려준 주소는 저장 레코드의 수명에 종속됩니다.'),
        ('stack_depot_save로 얻은 핸들에 반드시 put해야 하는가?', '아니다. GET 방식의 참조 획득과 put을 대응시켜야 한다', '그렇다. 이름에 save가 있는 모든 호출은 무조건 put과 쌍이다', '일반 save는 CAN_ALLOC만 전달합니다. 구현은 GET 없는 지속 저장 경로와 GET의 수명 관리 경로를 구분합니다.'),
        ('set_extra_bits(handle, value)를 호출한 뒤 반환값을 버려도 handle 변수가 수정되는가?', '아니다. 반환된 새 핸들을 사용해야 한다', '그렇다. handle을 내부에서 직접 덮어쓴다', '인자는 값으로 전달되고 결과를 반환합니다. __must_check는 결과를 사용해야 한다는 계약을 강조합니다.')
    ]
)]
