"""Whole pageblock metadata interface and 32-bit idle flag helpers."""
ROWS = [dict(
    path='include/linux/pageblock-flags.h',
    title='페이지 블록: 이동 유형 비트와 PFN 경계',
    intro='여러 페이지에 공유되는 플래그의 폭, 블록 크기, 정렬과 compaction skip 인터페이스를 읽습니다.',
    principle='개별 페이지의 상태와 페이지 블록 전체의 상태를 구분하고, 포함 구간의 끝과 단순 올림 정렬을 구분합니다.',
    use='메모리 단편화와 compaction을 학습하기 전에 블록 메타데이터의 단위를 확립합니다.',
    area='비트맵 · 이진 정렬 · 반열린 구간 · 메모리 단편화 · 조건부 컴파일',
    sections=[
        ('전체 범위와 선언', 'GPL-2.0-only, 저작권·작성자 주석, guard와 types.h 뒤에 비트 열거형, 구성별 order, PFN 경계 매크로, get/set 선언, skip wrapper가 있습니다. 이 헤더는 메모리 압축이나 페이지 이동을 실행하지 않습니다. struct page는 전방 선언이며 실제 플래그 저장 위치와 get/set 구현은 mm/page_alloc.c에 있습니다.'),
        ('4비트 블록 레코드', 'PB_migratetype_bits는 3입니다. enum의 PB_migrate는 0, PB_migrate_end는 2, PB_migrate_skip은 3, NR_PAGEBLOCK_BITS는 4입니다. 처음 세 비트는 이동 유형, 네 번째는 compaction에서 건너뛰는 표시입니다. 3비트의 표현 가능 조합이 8개라는 사실과 실제 정의된 이동 유형 개수는 다릅니다. 주석은 레코드 비트들이 word 경계를 가로지르지 않는 배치 전제를 밝히며, 전제가 바뀌면 접근 함수를 수정해야 한다고 합니다.'),
        ('HugeTLB의 우선 분기', 'CONFIG_HUGETLB_PAGE가 먼저 검사됩니다. 그 안에서 HUGETLB_PAGE_SIZE_VARIABLE이면 pageblock_order는 extern unsigned int 변수이고 이 파일에 초기화 본문은 없습니다. 그렇지 않으면 HUGETLB_PAGE_ORDER와 MAX_PAGE_ORDER의 unsigned int 최소값입니다. 가변 크기 분기에는 이 헤더 안의 min 연산이 없으므로 변수도 여기서 자동 제한한다고 설명하면 틀립니다.'),
        ('THP와 기본 크기', 'HugeTLB 분기에 들어가지 않고 TRANSPARENT_HUGEPAGE이면 HPAGE_PMD_ORDER와 MAX_PAGE_ORDER의 최소값을 사용합니다. 둘 다 아니면 MAX_PAGE_ORDER입니다. 두 기능이 함께 켜졌을 때 두 크기를 서로 비교하는 코드가 아니라 HugeTLB 분기가 우선하는 #if/#elif 구조입니다. pageblock_nr_pages는 1UL<<pageblock_order이며 바이트 수가 아닌 페이지 수입니다.'),
        ('네 가지 경계 연산', 'pageblock_align은 PFN을 블록 크기의 배수로 올림하고 이미 정렬되어 있으면 그대로입니다. pageblock_aligned는 배수 여부를 검사합니다. pageblock_start_pfn은 내림하여 현재 블록 시작을 얻습니다. pageblock_end_pfn은 PFN에 먼저 1을 더한 뒤 올림하므로 현재 블록의 배타적 끝을 얻습니다. 크기 8이면 PFN 16에서 align=16, start=16, end=24이며 PFN 23에서도 end=24입니다. 끝값은 현재 블록에 속하지 않습니다.'),
        ('연산의 입력 전제', '경계 계산은 유효한 PFN과 적절한 order를 전제로 하며 페이지가 실제로 존재하는지 검사하지 않습니다. 특히 pfn+1이나 올림 과정의 정수 오버플로를 따로 검출하지 않습니다. 매크로 이름을 메모리 할당, PFN 유효성 판별, 범위 검사로 오해하지 않습니다.'),
        ('Masked get/set 계약', 'get_pfnblock_flags_mask는 const page 포인터, 대상 PFN, mask를 받아 unsigned long을 반환합니다. set은 page, flags, PFN, mask 순서로 받고 void입니다. 관련 구현을 대조하면 get은 word를 READ_ONCE로 읽어 블록 위치만큼 이동하고 mask를 적용합니다. set은 word의 기존 mask 영역을 지우고 flags를 OR하는 compare-exchange 재시도를 사용합니다. flags를 mask로 자동 제한하는 식은 아니므로 호출자의 flags가 적절해야 합니다. 이 구현 대조는 page_alloc.c 전체 완료를 의미하지 않습니다.'),
        ('Compaction skip 설정', 'COMPACTION이 켜지면 get_pageblock_skip은 page_to_pfn과 1<<PB_migrate_skip, 즉 8을 get에 넘깁니다. 따라서 get의 결과는 비트가 있으면 8이며 반드시 정규화된 1인 것은 아닙니다. clear는 flags=0, set은 flags=8을 mask=8과 함께 전달합니다. 이 wrapper의 page 인자는 직접 전달과 page_to_pfn에서 반복 사용되므로 부작용이 있는 표현식을 넘기지 않아야 합니다.'),
        ('기능이 꺼졌을 때', 'COMPACTION이 없으면 get은 bool false, clear/set은 빈 inline 함수입니다. 호출 코드의 형태를 유지할 수 있지만 skip 정보가 저장되지는 않습니다. 구성에 따라 활성 분기는 매크로, 비활성 분기는 함수이며 반환형과 인자 평가 방식까지 동일한 구현이라고 가정하면 안 됩니다.'),
        ('CS 관점', '고정 폭 레코드를 word 비트맵에 압축하는 공간 효율, 2의 거듭제곱 정렬, [start,end) 구간, 데이터 단위 구분, 컴파일 시 기능 제거를 연결합니다. skip 비트 하나는 전체 압축 알고리즘의 성공 여부나 영구적인 이동 불가능 판정이 아닙니다. 여기의 원본 대조는 실제 compaction 실행 테스트와 구분합니다.')
    ],
    questions=[
        ('페이지 블록의 이동 유형과 skip을 합친 NR_PAGEBLOCK_BITS는?', '4이다', '8이다', '3개 이동 유형 비트의 마지막 인덱스는 2이고 skip은 3, 다음 enum 값은 4입니다. 8은 이동 유형 3비트의 조합 수입니다.'),
        ('블록 크기 8에서 PFN 16의 pageblock_align과 pageblock_end_pfn은?', '각각 16과 24이다', '둘 다 16이다', 'align은 정렬된 입력을 유지하지만 end는 16+1을 올림하여 현재 블록의 배타적 끝 24를 반환합니다.'),
        ('HugeTLB와 THP가 모두 켜지면 두 huge page order의 최소값을 고르는가?', '아니다. 먼저 HugeTLB 분기를 따른다', '그렇다. 세 order를 항상 함께 비교한다', 'THP는 #elif입니다. HugeTLB의 가변 크기 설정 여부에 따라 extern 변수 또는 HugeTLB와 최대 order의 최소값을 사용합니다.'),
        ('COMPACTION 활성 시 get_pageblock_skip의 설정된 비트 결과는 반드시 1인가?', '아니다. mask에 해당하는 8을 반환할 수 있다', '그렇다. bool 함수이므로 항상 1이다', '활성 분기는 unsigned long get의 결과를 그대로 사용하는 매크로입니다. 비활성 분기의 bool inline 함수와 혼동하면 안 됩니다.')
    ]
), dict(
    path='include/linux/page_idle.h',
    title='32비트 페이지 idle 추적: 확장 메타데이터 접근',
    intro='page flags 공간이 부족한 구성에서 folio의 young·idle 상태를 page_ext 비트로 읽고 갱신하는 여섯 함수를 해설합니다.',
    principle='상태 조회와 원자적 test-and-clear를 구분하고, 외부 메타데이터 접근의 획득·해제 및 실패 경로를 대응시킵니다.',
    use='메모리 접근 추적 기능이 아키텍처의 비트 공간 제약을 처리하는 방식을 이해합니다.',
    area='메타데이터 간접화 · 비트 연산 · 원자적 상태 전이 · 자원 수명 · folio',
    sections=[
        ('전체 구성 조건', 'GPL-2.0과 guard 뒤에 bitops.h, page-flags.h, page_ext.h를 포함합니다. 여섯 inline 함수는 PAGE_IDLE_FLAG가 정의되어 있고 64BIT가 정의되지 않았을 때만 제공됩니다. 다른 구성에 대한 else stub은 이 파일에 없습니다. 주석은 Idle과 Young 비트를 page flags에 넣을 공간이 부족하므로 확장 플래그를 쓴다고 설명합니다.'),
        ('접근 단위와 수명', '각 함수는 &folio->page로 page_ext_get을 호출합니다. folio 전체의 각 하위 페이지를 순회하는 반복문은 없습니다. 얻은 page_ext가 NULL이면 즉시 반환하며, 성공하면 page_ext->flags의 비트에 접근한 뒤 반드시 page_ext_put을 호출합니다. 이 헤더만으로 get이 메타데이터를 새로 할당한다거나 참조 카운터 하나만 증가시킨다고 단정할 수 없습니다. 보호 방식의 구현은 별도로 읽어야 합니다.'),
        ('Young 조회와 설정', 'folio_test_young은 PAGE_EXT_YOUNG를 test_bit하고 bool 지역 변수에 저장한 뒤 put하여 반환합니다. folio_set_young은 같은 비트를 set_bit한 뒤 put합니다. 전자는 조회만 하며 비트를 지우지 않습니다. 후자는 void이고 page_ext를 얻지 못하면 오류 코드를 보고하지 않은 채 아무 동작 없이 끝납니다.'),
        ('조회하면서 지우기', 'folio_test_clear_young은 test_and_clear_bit의 이전 상태를 bool로 저장하고 put한 뒤 반환합니다. 상태를 읽고 나중에 별개의 clear_bit를 호출하는 두 동작과 다릅니다. 비트 자체의 원자적 read-modify-write를 통해 이전 값을 반환하고 지웁니다. 그러나 다른 CPU가 이후 다시 set할 수 있으므로 함수 반환 시점부터 계속 0이 유지된다는 보장은 아닙니다.'),
        ('Idle의 세 함수', 'folio_test_idle은 PAGE_EXT_IDLE를 읽어 bool로 반환합니다. folio_set_idle은 그 비트를 설정하고 folio_clear_idle은 지웁니다. clear는 이전 값을 반환하지 않습니다. 세 함수 모두 young과 같은 get/NULL 확인/비트 접근/put 패턴입니다. idle 조작이 young 비트를 함께 수정하거나 실제 페이지 테이블 accessed 비트를 직접 지우는 코드는 없습니다.'),
        ('정보 없음과 false', 'young 조회, young test-clear, idle 조회는 page_ext가 없으면 false입니다. 따라서 false만으로 메타데이터가 존재하고 해당 비트가 확실히 0이었다고 구분할 수 없습니다. setter/clearer 역시 NULL일 때 조용히 돌아옵니다. unlikely는 실패 분기에 대한 예상 힌트이며 NULL 경로를 불가능하게 만들지 않습니다.'),
        ('관측과 정책의 경계', '이 헤더의 helper들은 소프트웨어 메타데이터만 다룹니다. 실제 메모리 접근을 감지하거나 페이지 테이블을 순회하고 working set 크기를 계산하는 알고리즘은 들어 있지 않습니다. young과 idle이라는 이름만으로 둘이 항상 논리적 부정 관계라고 추정해서도 안 됩니다. 본문에는 두 비트를 함께 갱신하는 코드가 없습니다.'),
        ('CS 연결', '부족한 인라인 비트를 외부 메타데이터로 옮기는 공간·간접 접근의 절충, 성공과 실패 경로의 자원 대응, 원자적 비트 상태 전이와 장기 불변식의 차이를 학습합니다. 원본 및 데이터 구조 검증은 동시 실행이나 실제 페이지 idle 추적의 하드웨어 시험을 대신하지 않습니다.')
    ],
    questions=[
        ('이 파일의 여섯 helper가 정의되는 구성은?', 'PAGE_IDLE_FLAG가 켜지고 64BIT가 아닌 구성이다', 'PAGE_IDLE_FLAG가 켜진 모든 64비트 구성이다', '전처리 조건은 PAGE_IDLE_FLAG && !64BIT입니다. 다른 구성의 구현을 이 파일의 빈 else 함수로 설명하면 틀립니다.'),
        ('folio_test_clear_young이 true를 반환하면 무엇을 의미하는가?', 'test_and_clear_bit가 관측한 이전 young 비트가 설정되어 있었다', '이후 어떤 CPU도 young 비트를 다시 설정할 수 없다', '원자적인 조회·지우기는 그 연산의 이전 상태를 돌려줍니다. 다른 실행 주체의 뒤이은 설정을 금지하는 잠금 정책은 아닙니다.'),
        ('folio_test_idle의 false 결과로 page_ext가 존재했음을 알 수 있는가?', '아니다. page_ext_get 실패도 false로 반환한다', '그렇다. 실패하면 음수 오류를 반환한다', '반환형은 bool이고 NULL 경로에서 false를 반환합니다. 상태 비트 0과 메타데이터를 얻지 못한 경우를 결과만으로 구분할 수 없습니다.'),
        ('folio_set_idle은 young도 지우는가?', '아니다. PAGE_EXT_IDLE 비트만 설정한다', '그렇다. 두 비트를 항상 반대 값으로 유지한다', '본문은 set_bit(PAGE_EXT_IDLE, ...)과 접근 수명 처리뿐입니다. 서로 다른 두 메타데이터 비트 사이의 추가 정책을 이름만으로 추정하면 안 됩니다.')
    ]
)]
