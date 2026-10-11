"""Idle tracking user documentation and complete implementation."""
ROWS = [dict(
    path='Documentation/admin-guide/mm/idle_page_tracking.rst',
    title='Idle 페이지 측정: 관측 구간과 working set 추정',
    intro='idle 비트맵을 설정하고 관찰한 뒤 읽는 절차와 측정 대상·오차 요인을 학습합니다.',
    principle='idle은 영구적인 페이지 속성이 아니라 표시한 시점 이후의 관측 결과이며 비트 수와 메모리 크기는 다릅니다.',
    use='프로세스와 memory cgroup의 메모리 사용을 분석할 때 측정값을 올바르게 해석합니다.',
    area='비트맵 · working set · 관측 구간 · 계측 간섭 · 메모리 회수',
    sections=[
        ('문서 전체와 목적', 'Motivation, User API, Implementation Details의 세 부분과 두 교차 참조 anchor로 구성됩니다. CONFIG_IDLE_PAGE_TRACKING=y가 기능을 활성화합니다. working set 추정은 workload 설정, memory cgroup 제한, 클러스터 배치 판단에 활용할 수 있다고 설명하지만 특정 제한값을 자동 계산하는 정책은 제시하지 않습니다.'),
        ('비트맵의 주소 체계', '/sys/kernel/mm/page_idle/bitmap은 8바이트 정수 배열이며 PFN i는 원소 i/64의 비트 i%64에 대응합니다. 바이트 순서는 native입니다. 예를 들어 PFN 130은 세 번째 원소의 비트 2이며 파일의 해당 8바이트 원소 시작 위치는 16입니다. PFN을 프로세스 가상 페이지 번호로 해석해서는 안 됩니다.'),
        ('표시와 0 쓰기의 의미', '비트 1은 페이지가 idle임을 뜻하며 사용자가 1을 써서 측정 시작 상태를 표시합니다. 문서는 쓰기 값을 기존 값에 OR한다고 설명합니다. 따라서 0을 쓴다고 그 페이지의 idle을 지우는 API가 아닙니다. 실제 구현은 선택된 페이지에 대해 기존 PTE 참조 정보를 처리한 다음 idle을 설정하므로 단순 메모리 배열 OR만 하는 함수와는 다릅니다.'),
        ('대상과 huge page', '문서는 프로세스 매핑, page cache와 buffer, swap cache 등 사용자 메모리 페이지를 대상으로 들고 SLAB 등은 표시 시도를 무시한다고 설명합니다. huge page에서는 head에만 idle이 표시되므로 kpageflags로 크기와 유형을 함께 해석해야 합니다. head 비트 하나를 기본 페이지 한 개의 바이트 수로만 환산하면 큰 페이지의 유휴 용량을 과소 계산할 수 있습니다.'),
        ('정렬과 끝 경계', '읽기·쓰기 위치가 8바이트 정렬이 아니거나 길이가 8의 배수가 아니면 EINVAL입니다. 문서는 최대 PFN을 넘는 쓰기에 ENXIO를 설명합니다. 구현을 대조하면 시작 PFN이 max_pfn 이상일 때 ENXIO이고, 시작은 유효하나 요청 끝이 넘는 경우에는 끝을 잘라 처리합니다. 읽기의 시작이 범위 밖이면 0을 반환합니다. 요청 범위의 일부 초과와 시작 위치 초과를 구분합니다.'),
        ('측정의 세 단계', '먼저 workload 페이지를 찾아 해당 비트를 1로 표시하고, workload가 working set에 접근할 관찰 시간을 둔 다음 비트맵을 읽어 남은 1을 셉니다. 프로세스는 /proc/pid/pagemap, cgroup은 /proc/kpagecgroup으로 소속을 확인하고 /proc/kpageflags로 mlocked 등 제외할 유형을 걸러낼 수 있습니다. tools/mm의 page-types가 표시와 후속 관측을 도울 수 있으며 상세 proc 인터페이스는 pagemap.rst를 참조합니다. 이 문서 자체가 모든 권한·도구 옵션을 설명하지는 않습니다.'),
        ('접근의 의미', '프로세스 주소 공간의 PTE Accessed와 커널의 명시적인 accessed 표식을 사용합니다. 문서는 read/write 시스템 호출, 파일시스템 메타데이터 buffer 사용, get_user_pages를 이용한 드라이버 접근을 예로 듭니다. 회수나 dirty 한도 때문에 dirty 페이지를 swap 또는 disk에 쓰는 행위 자체는 referenced로 표시하지 않는다고 구분합니다. 모든 하드웨어 버스 트랜잭션을 세는 기능은 아닙니다.'),
        ('Young로 계측 간섭 완화', '새로운 접근을 감지하려면 기존 PTE Accessed를 지워야 하지만 reclaim도 이 정보를 이용합니다. 관측 과정에서 참조를 지울 때 Young을 보존해 reclaimer가 추가 Accessed 표식처럼 해석하도록 합니다. 구현에서는 실제 참조를 발견한 경우 idle을 지우고 young을 설정합니다. idle 해제는 CPU 접근 순간 즉시 실행되는 trap이라는 뜻이 아니며 비트맵 읽기 때 PTE 참조를 확인하는 경로도 있습니다.'),
        ('측정의 한계와 CS', 'LRU에 없는 페이지와 일시적으로 격리된 페이지는 제외될 수 있고 잠긴 페이지의 참조 확인도 건너뛸 수 있습니다. 관측 기간, 대상 변화, huge page 단위, 필터가 결과에 영향을 주므로 비트 수를 절대적인 working set 정답으로 취급하지 않습니다. 비트 압축, 물리 주소 식별, 표본 누락, 관측이 원래 알고리즘에 끼치는 간섭을 연결해 학습합니다.')
    ],
    questions=[
        ('PFN 130의 비트맵 원소 시작 바이트 위치와 비트 번호는?', '16바이트 위치, 비트 2이다', '130바이트 위치, 비트 0이다', '130/64=2이므로 0부터 센 원소 번호는 2이고 2*8=16입니다. 나머지 2가 원소 안 비트 번호입니다.'),
        ('비트맵에 0을 쓰면 해당 페이지 idle이 해제되는가?', '아니다. 0인 비트는 표시 대상으로 선택하지 않는다', '그렇다. 기존 비트맵 전체를 덮어쓴다', '쓰기 인터페이스는 1로 선택된 페이지를 idle로 표시합니다. 기존 상태 전체를 대입하는 연산이 아닙니다.'),
        ('Huge page의 head idle 비트 하나를 기본 페이지 하나로 세면 충분한가?', '아니다. kpageflags 등을 이용해 큰 페이지 단위를 해석해야 한다', '그렇다. 모든 하위 페이지에 각각 동일한 idle 비트가 반환된다', '문서는 head에만 표시한다고 명시합니다. 비트 개수와 유휴 바이트 수를 구분해야 합니다.'),
        ('관측 과정에서 Young 표식을 유지하는 이유는?', 'PTE 참조 비트를 지워도 reclaim이 참조 정보를 잃지 않도록 하기 위해서다', 'idle 페이지를 절대로 회수할 수 없게 고정하기 위해서다', 'Young은 회수기의 참조 판단에 쓰이는 보완 정보입니다. pin이나 영구 회수 금지 표시가 아닙니다.')
    ]
), dict(
    path='mm/page_idle.c',
    title='Idle 추적 구현: folio 수명, 역매핑 순회와 sysfs 비트맵',
    intro='PFN을 folio로 얻는 경로부터 PTE 참조 수집, 비트맵 읽기·쓰기, sysfs 등록까지 전체 구현을 해설합니다.',
    principle='비트맵 읽기도 페이지 참조 상태를 갱신하며, 수명 보호와 상태 재검사 및 비차단 잠금이 관측의 정확도와 비용을 결정합니다.',
    use='idle 사용자 인터페이스가 실제 커널 자료구조와 어떻게 연결되는지 추적합니다.',
    area='역매핑 · 원자적 참조 획득 · 경쟁 상태 · 비트맵 직렬화 · sysfs',
    sections=[
        ('파일 전체와 단위', 'GPL-2.0, 메모리·sysfs·rmap·notifier·idle 관련 include 및 internal.h 뒤에 folio 조회, 참조 제거, 읽기·쓰기, 속성 등록이 있습니다. BITMAP_CHUNK_SIZE는 sizeof(u64), CHUNK_BITS는 그 값에 BITS_PER_BYTE를 곱한 값으로 각각 8바이트와 64비트입니다. 이 파일은 별도의 사용자 프로세스마다 비트맵을 할당하지 않습니다.'),
        ('PFN에서 관측 가능한 folio 얻기', 'page_idle_get_folio는 pfn_to_online_page가 실패하거나 PageTail이면 NULL입니다. page_folio로 얻은 folio가 LRU에 있고 folio_try_get이 성공해야 계속합니다. 참조를 얻은 뒤 page_folio(page)가 여전히 같은지와 LRU 여부를 재검사합니다. 실패하면 folio_put하고 NULL로 바꿉니다. 최초 검사와 참조 획득 사이의 상태 변화에 대응하는 패턴이며, 성공 결과는 호출자가 put해야 합니다.'),
        ('VMA 안의 매핑 순회', 'page_idle_clear_pte_refs_one은 DEFINE_FOLIO_VMA_WALK로 순회를 준비하고 page_vma_mapped_walk로 각 매핑을 방문합니다. PTE이면 ptep_clear_young_notify, 그렇지 않고 THP 구성이면 pmdp_clear_young_notify를 호출해 참조 여부를 누적합니다. THP 구성이 없는 예상 밖 PMD 경로는 WARN_ON_ONCE입니다. PTE로 나뉘어 매핑된 THP도 하위 한 페이지의 참조가 전체 folio 참조로 집계됩니다.'),
        ('참조를 발견한 뒤의 상태', '매핑 중 하나라도 young이었으면 folio_clear_idle과 folio_set_young을 실행합니다. 전자는 관측 결과를 갱신하고 후자는 reclaim의 참조 판단을 보존합니다. callback은 항상 true를 반환하며 첫 참조 발견만으로 전체 순회를 끝내는 break는 없습니다. 이 파일은 notifier helper를 사용하지만 notifier 내부 구현까지 포함하지는 않습니다.'),
        ('역매핑과 잠금 분기', 'page_idle_clear_pte_refs의 static rmap_walk_control에는 rmap_one callback과 folio_lock_anon_vma_read가 들어갑니다. 주석은 try_lock 필드를 사용하지 않아 제어 구조가 사실상 불변이므로 static으로 둔다고 설명합니다. folio가 매핑되어 있지 않거나 raw_mapping이 없으면 반환합니다. 파일 folio 또는 KSM이면 folio_trylock이 필요하고 실패하면 기다리지 않고 반환합니다. 보통의 anonymous folio는 이 folio 잠금을 생략하지만 anon_vma 잠금 callback까지 없다는 뜻은 아닙니다. 순회 후 획득한 folio 잠금만 해제합니다.'),
        ('입출력 공통 경계 처리', 'read/write는 pos와 count가 각각 8의 배수인지 먼저 검사하여 아니면 EINVAL입니다. 시작 PFN은 pos*BITS_PER_BYTE, 끝은 시작+count*BITS_PER_BYTE이며 끝이 max_pfn보다 크면 잘립니다. 시작이 max_pfn 이상이면 read는 0, write는 ENXIO입니다. 매개변수의 산술 오버플로를 별도로 검사하는 코드가 이 본문에 있는 것은 아닙니다.'),
        ('읽기: 조회하면서 참조 갱신', '각 PFN의 bit=pfn%64가 0이면 현재 출력 u64를 0으로 초기화합니다. 유효한 folio가 있고 idle이 이미 설정되어 있을 때만 참조 확인 함수를 실행하고, 다시 idle을 확인해 남아 있으면 출력 비트를 OR합니다. 마지막에 folio_put합니다. 따라서 읽기는 저장된 비트만 복사하는 순수한 조회가 아니며 PTE young 및 folio 상태를 바꿀 수 있습니다.'),
        ('쓰기: 선택된 PFN만 표시', '현재 입력 u64의 해당 비트가 1일 때만 folio를 얻습니다. 성공하면 먼저 기존 PTE 참조를 처리하고 이후 folio_set_idle을 실행한 뒤 put합니다. 참조 확인 과정에서 idle을 지웠더라도 최종적으로 다시 표시하여 새 관측을 시작합니다. folio 잠금 실패로 참조 확인 함수가 일찍 반환한 경우에도 바깥의 set_idle은 실행되므로 모든 표시가 항상 PTE 참조 제거 성공을 의미하지는 않습니다.'),
        ('청크 진행과 반환 바이트 수', 'read의 out과 write의 in은 비트 63을 처리했을 때만 다음 u64로 이동합니다. 반환값은 이동한 포인터와 원래 buf의 바이트 차이입니다. max_pfn이 요청을 청크 중간에서 자르면 마지막 부분 청크의 포인터는 이동하지 않아 반환 길이에 포함되지 않습니다. 예를 들어 시작 PFN 0, max_pfn 70, 요청 16바이트이면 순회는 70개 PFN을 방문하지만 반환 길이는 8바이트입니다. 단순히 방문 PFN 수를 8로 나눈 값을 반환하는 식이 아닙니다.'),
        ('스케줄링과 관측 비용', '각 PFN 처리 뒤 cond_resched를 호출하여 긴 스캔 중 재스케줄 기회를 제공합니다. 범위 PFN을 순서대로 검사하므로 기본 루프 비용은 범위 길이에 비례하며, 선택된 folio의 역매핑 순회 비용이 추가됩니다. 입력 비트가 0이어도 write는 그 PFN의 루프와 cond_resched 지점을 지나갑니다. 모든 페이지의 상태를 한 시점에 원자적으로 촬영하는 전역 잠금은 없습니다.'),
        ('Sysfs 등록과 실패', 'bitmap bin_attribute는 권한 0600, 읽기·쓰기 callback, 크기 필드 0으로 정의됩니다. NULL로 끝나는 bin_attrs 배열을 page_idle 이름의 그룹에 연결합니다. page_idle_init은 mm_kobj 아래 sysfs_create_group을 호출하고 실패하면 오류 로그 후 같은 오류를 반환하며 성공하면 0입니다. subsys_initcall로 등록하며 이 파일에 별도의 종료·그룹 제거 함수는 없습니다.'),
        ('CS 연결과 검증 범위', '검사 후 참조 획득과 재검사, 수명 보호와 잠금의 차이, 물리 PFN을 비트 스트림으로 직렬화하는 방식, 비차단 관측의 누락, read의 부수효과를 학습합니다. 위 내용은 전체 소스 대조에 근거하며 실제 커널의 hotplug·동시 접근·THP 환경 실행 시험을 완료했다는 주장은 아닙니다.')
    ],
    questions=[
        ('folio_try_get 성공 후 같은 folio인지와 LRU 상태를 다시 보는 이유는?', '최초 검사와 참조 획득 사이 상태 변화에 대응하기 위해서다', '동일한 검사를 두 번 하면 참조 횟수가 자동으로 두 배가 되기 때문이다', '참조 획득 이전의 관측만으로 계속 같은 folio와 상태라고 단정할 수 없습니다. 재검사 실패 경로는 획득한 참조를 put합니다.'),
        ('idle 비트맵 읽기는 기존 비트만 복사하는가?', '아니다. idle folio의 PTE 참조를 확인·제거하고 상태를 재검사한다', '그렇다. 어떤 메모리 상태도 변경하지 않는다', 'read는 page_idle_clear_pte_refs를 호출할 수 있습니다. 접근을 발견하면 idle을 지우고 reclaim용 young을 설정합니다.'),
        ('참조 확인의 folio_trylock이 실패하면 바깥 쓰기 경로도 idle 표시를 취소하는가?', '아니다. 참조 확인 함수 반환 뒤 set_idle을 실행한다', '그렇다. 실패 코드가 전달되어 write 전체가 중단된다', '참조 확인 함수는 void이며 조기 반환합니다. write에는 그 실패를 조건으로 set_idle을 건너뛰는 분기가 없습니다.'),
        ('시작 PFN 0, max_pfn 70, 요청 16바이트에서 반환 길이는?', '8바이트이다', '방문한 모든 PFN을 포함하여 항상 16바이트이다', '포인터는 64번째 PFN을 마칠 때 한 청크만 전진합니다. 잘린 마지막 6개 PFN 처리 뒤에는 비트 63에 도달하지 않아 두 번째 청크가 반환 길이에 들어가지 않습니다.'),
        ('유효 범위 밖의 시작 위치에서 read와 write의 결과는?', 'read는 0, write는 ENXIO이다', '둘 다 반드시 EINVAL이다', '8바이트 정렬 검사를 통과한 뒤의 범위 조건을 묻는 문제입니다. 정렬 오류와 끝 범위 처리 및 읽기 EOF를 구분해야 합니다.')
    ]
)]
