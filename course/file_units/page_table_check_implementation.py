"""Complete mapping-accounting and flag checks in page_table_check.c."""
ROWS = [dict(
    path='mm/page_table_check.c',
    title='페이지 테이블 검사 구현: 독립 카운터와 권한 불변식',
    intro='확장 메타데이터 등록, 매핑 증감, 할당 검사, 엔트리별 hook과 범위 순회를 전체 소스로 학습합니다.',
    principle='검사 카운터는 실제 페이지 테이블과 별도로 갱신되며, 원자적 증감과 여러 조건을 묶은 전역 원자성은 구분해야 합니다.',
    use='중복 매핑 진단이 어떤 입력을 검사하고 어떤 경로를 건너뛰는지 이해합니다.',
    area='원자적 카운터 · 불변식 · 페이지 확장 · 사용자 접근 권한 · 범위 순회',
    sections=[
        ('전체 구조와 저장소', 'GPL-2.0, 작성자 주석과 include 뒤 pr_fmt 접두어를 page_table_check로 정의합니다. struct page_table_check는 atomic_t anon_map_count와 file_map_count 두 개를 가집니다. 기존 page의 참조 카운터나 mapcount를 재사용하는 것이 아니라 page_ext의 client 데이터에 검사 정보를 둡니다. 이후 초기화, 공통 clear/set/zero, 엔트리별 hook, 범위 clear가 이어집니다.'),
        ('활성화와 등록', '초기 bool은 CONFIG_PAGE_TABLE_CHECK_ENFORCED 여부이고 early_param page_table_check는 kstrtobool로 값을 파싱합니다. DEFINE_STATIC_KEY_TRUE의 disabled key는 처음 참이며 외부 심볼로 export합니다. need callback은 bool을 반환하고 init callback은 활성일 때만 disabled key를 꺼 검사 경로를 엽니다. operations는 size=검사 구조체 크기, 두 callback, need_shared_flags=false이며 offset은 확장 시스템이 정합니다.'),
        ('Client 포인터와 접근 수명', 'get_page_table_check는 NULL page_ext에 BUG_ON하고 page_ext_data로 client 주소를 계산합니다. 공통 clear/set은 먼저 pfn_valid를 검사하고 실패하면 반환합니다. 유효하면 시작 page의 page_ext_get을 호출하며 NULL이면 검사 없이 돌아옵니다. 성공한 순회는 page_ext_next로 레코드 간격만큼 이동한 뒤 page_ext_put으로 접근을 마칩니다. 순회에서 포인터가 전진해도 put의 해당 구현은 포인터를 역참조하여 카운터를 줄이는 함수가 아니라 RCU 구간 해제라는 점을 함께 이해해야 합니다.'),
        ('분류와 범위 전제', 'clear와 set은 확장 정보를 얻은 뒤 시작 page가 slab이면 BUG_ON하고 PageAnon으로 익명 여부를 한 번 결정합니다. pgcnt 전체를 그 분류로 순회하며 각 PFN마다 pfn_valid나 PageAnon을 다시 확인하지 않습니다. 호출자가 넘긴 연속 범위의 구조와 종류에 전제가 있습니다. 이 함수만으로 임의의 섞인 PFN 목록을 안전하게 검사한다고 설명하지 않습니다.'),
        ('Clear의 불변식', 'anonymous이면 file_map_count가 0인지 검사하고 anon_map_count를 atomic_dec_return하여 음수인지 검사합니다. named 경로는 반대로 anon이 0인지 확인하고 file 카운터를 감소시켜 음수인지 확인합니다. 잘못된 해제를 발견하면 카운터를 복구하고 오류 코드를 반환하는 것이 아니라 BUG_ON으로 진단합니다. 실제 PTE 저장을 지우는 명령은 이 함수에 없습니다.'),
        ('Set의 비대칭 조건', 'anonymous이면 file 카운터가 0인지 검사하고 anon을 증가시킨 결과가 1보다 크면서 새 매핑 rw가 참이면 BUG_ON합니다. 읽기 전용 추가는 그 조건에 해당하지 않습니다. file 경로는 anon이 0인지 검사하고 file을 증가시킨 결과가 음수인지 확인합니다. 카운터에 기존 매핑별 쓰기 권한 목록을 저장하지 않으므로 rw를 기존 모든 매핑의 권한까지 다시 순회한 결과라고 설명해서는 안 됩니다.'),
        ('Zero는 검증이지 초기화가 아님', '__page_table_check_zero는 시작 page의 slab 여부를 먼저 검사한 뒤 page_ext를 얻습니다. NULL이면 반환하고, 있으면 1UL<<order개 레코드에서 두 카운터가 모두 0인지 BUG_ON으로 확인합니다. 카운터에 0을 대입하거나 페이지 데이터를 지우지 않습니다. clear/set과 달리 slab 검사가 확장 정보 획득보다 앞에 있다는 순서 차이도 있습니다.'),
        ('PTE·PMD·PUD clear hook', '세 함수 모두 mm이 &init_mm이면 반환하고 각 수준의 user_accessible_page 조건이 참일 때만 공통 clear를 호출합니다. 페이지 수는 각각 PAGE_SIZE, PMD_SIZE, PUD_SIZE를 PAGE_SHIFT만큼 내려 구하며 PTE는 한 페이지입니다. present라는 단일 조건과 user_accessible_page 판별을 임의로 동일시하지 않습니다. 세 clear 함수는 EXPORT_SYMBOL로 노출됩니다.'),
        ('Swap에 저장된 쓰기 정보', 'swap_cached_writable은 writable device exclusive, writable device private, writable migration entry 중 하나인지를 OR합니다. 단순히 swap 엔트리이면 writable로 간주하지 않습니다. PTE 플래그 검사는 present이고 uffd_wp이면 pte_write를 WARN_ON_ONCE하고, 아니면 swap PTE이면서 swap uffd_wp일 때 이 helper 결과를 경고합니다. 중복 매핑의 BUG_ON과 같은 처리 수준은 아닙니다.'),
        ('묶음 PTE set의 순서', '__page_table_check_ptes_set은 init_mm을 제외하고 새 pte 플래그를 한 번 검사합니다. 이후 nr개의 기존 ptep+i를 ptep_get으로 읽어 각각 clear 검사하고, 새 pte가 사용자 접근 가능하면 시작 PFN부터 nr개를 같은 pte_write 값으로 set 검사합니다. 기존 엔트리들의 실제 PFN은 각각에서 읽지만 새 범위는 연속 PFN을 전제로 합니다. 이 함수 자체가 새 PTE를 배열에 저장하지는 않습니다.'),
        ('PMD와 PUD set의 차이', 'PMD는 present/uffd_wp 또는 swap/uffd_wp의 writable 조합을 PTE와 유사하게 검사한 뒤 *pmdp의 이전 매핑을 clear하고 새 매핑을 set합니다. PUD는 이전 매핑 clear와 새 매핑 set은 수행하지만 이 파일에 별도 PUD flags 검사 함수나 호출은 없습니다. 두 함수는 큰 매핑의 기본 페이지 개수를 전달하며 EXPORT_SYMBOL 대상입니다. PTE set도 export하지만 모든 함수가 동일하게 export되는 것은 아닙니다.'),
        ('PTE 테이블 범위 검사', 'clear_range는 init_mm이면 반환하고 pmd가 bad도 leaf도 아닐 때 pte_offset_map(&pmd,addr)을 호출합니다. NULL이면 WARN_ON 후 반환합니다. 성공하면 PTRS_PER_PTE번 ptep_get과 PTE clear 검사를 수행하고 주소를 PAGE_SIZE, 포인터를 한 엔트리씩 증가시킵니다. 마지막에는 원래 포인터를 ptep-PTRS_PER_PTE로 복구해 pte_unmap합니다.'),
        ('범위와 정렬 책임', 'clear_range는 addr를 내부에서 PMD 경계로 내림하거나 남은 엔트리 개수를 계산하지 않습니다. pte_offset_map이 가리키는 지점부터 전체 PTRS_PER_PTE를 순회하므로 호출 문맥의 정렬 전제가 중요합니다. bad/leaf 검사 외의 모든 가능한 PMD 유효성 검사를 이 본문이 수행한다고 덧붙이지 않습니다. 엔트리들을 검사할 뿐 실제 clear 저장이나 TLB flush를 실행하는 함수는 아닙니다.'),
        ('CS 연결과 검증 범위', '별도 상태 기계로 계수 불변식을 검증하는 방법, 읽기/쓰기 공유의 비대칭, 원자적 카운터와 여러 필드 검사 사이의 차이, 호출자 범위 전제, 오류와 경고의 구분을 학습합니다. 원본 전체 대조와 학습 데이터 검사는 실제 커널에서 BUG_ON을 유발하거나 모든 동시 매핑 시나리오를 시험한 결과와 구분합니다.')
    ],
    questions=[
        ('anonymous 카운터가 증가 후 2이고 새 매핑 rw가 참이면?', 'BUG_ON 조건에 해당한다', 'file 카운터가 0이면 무조건 허용한다', '서로 다른 유형의 동시 매핑 검사와 별개로, 증가 결과가 1보다 크고 새 매핑이 writable이면 중단 조건입니다.'),
        ('공통 clear가 음수 카운터를 발견하면 자동 복구하는가?', '아니다. 감소 결과에 BUG_ON 검사를 수행한다', '그렇다. 다시 증가시키고 EINVAL을 반환한다', 'clear는 void이고 복구 분기가 없습니다. 이 기능은 오류를 감추는 보정기가 아니라 불변식 위반 진단입니다.'),
        ('새 PTE nr개를 검사할 때 기존 PFN과 새 PFN을 어떻게 다루는가?', '기존 엔트리는 각각 읽고, 새 매핑은 시작 PFN부터 연속 nr개로 처리한다', '기존 첫 엔트리 하나만 읽고 나머지는 모두 같은 페이지라고 가정한다', '기존 clear 루프는 ptep_get(ptep+i)이며 새 set은 pte_pfn(pte), nr, pte_write(pte)를 전달합니다.'),
        ('이 파일에서 PUD set도 PTE·PMD와 같은 uffd_wp flags 검사를 호출하는가?', '아니다. 별도의 PUD flags 검사 호출은 없다', '그렇다. 세 수준의 코드가 완전히 같다', 'PUD 함수는 init_mm 제외, 이전 매핑 clear, 새 매핑 set으로 구성됩니다. 비슷한 함수의 코드를 보지 않고 복제해 설명하면 안 됩니다.'),
        ('clear_range가 임의 addr를 PMD 시작으로 자동 정렬하는가?', '아니다. 받은 주소로 매핑한 뒤 PTRS_PER_PTE개를 순회한다', '그렇다. 함수 첫 줄에서 항상 ALIGN_DOWN한다', '코드에 정렬 보정은 없습니다. 전체 테이블을 순회하는 인터페이스이므로 호출 문맥이 필요한 전제를 만족해야 합니다.'),
        ('카운터가 atomic_t이면 모든 검사 조건이 하나의 원자적 트랜잭션인가?', '아니다. 각 원자 연산과 여러 조건을 묶은 전역 원자성은 다르다', '그렇다. 다른 카운터를 읽는 조건까지 자동으로 하나가 된다', 'atomic_read와 증감은 별도 호출입니다. 원자 타입 두 개의 존재만으로 모든 조건과 갱신을 묶는 전역 잠금이 생기지는 않습니다.')
    ]
)]
