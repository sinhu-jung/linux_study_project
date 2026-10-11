"""Whole ARM cache flushing implementation, including alias and folio paths."""
ROWS = [dict(
    path='arch/arm/mm/flush.c',
    title='ARM 캐시 flush 전체: 별칭·folio·실행 코드 동기화',
    intro='SoC 보완 장벽에서 시작해 VIVT/VIPT 캐시, highmem folio, ptrace와 익명 페이지의 동기화 경로를 읽습니다.',
    principle='같은 물리 메모리에 여러 가상 주소가 대응하면 캐시 색과 실행 매핑에 따라 유지보수 경로가 달라집니다. D-cache 상태와 I-cache 상태도 구분합니다.',
    use='앞서 barrier.h의 arm_heavy_mb 선언을 실제 구현에 연결하고 자료구조·분기·상태 비트를 파일 전체에서 추적합니다.',
    area='가상 메모리 · 캐시 별칭 · highmem · folio · 구간 트리 · 코드 동기화',
    sections=[
        ('파일 범위', 'GPL-2.0-only와 저작권 뒤 module/mm/pagemap/highmem, ARM cache·SMP·TLB 관련 헤더, hugetlb와 로컬 mm.h를 포함합니다. 보완 장벽, VIPT alias helper와 공개 cache 함수, ptrace/uprobe 복사, folio flush와 사용자 매핑 순회, PTE 동기화, 익명 페이지 flush까지 포함합니다. 실제 저수준 __cpuc 명령 구현은 호출 대상의 범위입니다.'),
        ('SoC 보완 장벽 구현', 'CONFIG_ARM_HEAVY_MB일 때 soc_mb 함수 포인터를 정의하고 arm_heavy_mb를 export합니다. CONFIG_OUTER_CACHE_SYNC이면 outer_cache.sync가 있을 때 먼저 호출하고, 이어 soc_mb가 있으면 호출합니다. 함수 자체에는 dsb가 없으며 앞서 barrier.h의 __arm_heavy_mb가 dsb 뒤 이 함수를 호출했습니다. 없는 callback은 건너뜁니다.'),
        ('캐시 색을 맞춘 alias', 'CONFIG_CPU_CACHE_VIPT의 flush_pfn_alias는 FLUSH_ALIAS_START에 CACHE_COLOUR(vaddr)<<PAGE_SHIFT를 더한 임시 주소를 선택합니다. set_top_pte로 해당 PFN을 PAGE_KERNEL로 매핑한 뒤 mcrr로 페이지 범위, mcr로 후속 유지보수 명령을 수행합니다. 범위 끝은 to+PAGE_SIZE-1입니다. 사용자 포인터를 그대로 커널에서 역참조하는 구현이 아닙니다.'),
        ('I-cache alias의 offset', 'flush_icache_alias도 사용자 주소의 색을 맞춰 매핑하지만 vaddr의 페이지 내부 offset을 보존합니다. to=va+offset을 구한 뒤 flush_icache_range(to,to+len)을 호출합니다. PFN은 페이지를, offset은 그 안의 시작 바이트를 결정합니다. 두 alias helper의 끝 주소 표현을 같은 것으로 뭉뚱그리지 않습니다.'),
        ('mm와 범위 flush', 'flush_cache_mm은 VIVT이면 vivt helper로 넘기고 즉시 반환합니다. 아니면 VIPT aliasing에서 cache 유지보수 asm을 수행합니다. flush_cache_range도 VIVT에 위임해 반환하고 VIPT aliasing에서 같은 asm을 사용한 뒤 VM_EXEC이면 전체 I-cache를 flush합니다. 이 후자 경로는 start/end를 이용한 세밀한 부분 루프를 구현하지 않습니다.'),
        ('페이지 묶음 flush', 'flush_cache_pages는 VIVT에 user_addr,pfn,nr을 전달해 위임합니다. VIPT aliasing에서는 flush_pfn_alias(pfn,user_addr)와 전체 I-cache flush를 호출합니다. 또 VM_EXEC이면서 icache_is_vivt_asid_tagged이면 전체 I-cache를 flush합니다. 여기의 VIPT 본문에는 nr만큼 alias helper를 반복하는 루프가 없으므로 본문에 없는 반복 동작을 만들어 설명하지 않습니다. CONFIG_CPU_CACHE_VIPT가 없으면 두 내부 alias helper는 빈 매크로가 됩니다.'),
        ('Ptrace 제어 플래그', 'FLAG_PA_IS_EXEC는1, FLAG_PA_CORE_IN_MM은2입니다. flush_ptrace_access는 현재 CPU가 대상 mm_cpumask에 속하는지와 VMA의 VM_EXEC 여부를 각각 비트로 모아 내부 helper에 전달합니다. flush_uprobe_xol_access는 두 비트를 모두 설정해 같은 helper를 호출합니다. 이 비트들은 전체 전역 CPU 상태가 아니라 해당 호출의 판단 자료입니다.'),
        ('Ptrace VIVT·aliasing 경로', '__flush_ptrace_access는 VIVT에서 CORE_IN_MM일 때만 kaddr부터 len 범위의 __cpuc_coherent_kern_range를 호출하고 반환합니다. VIPT aliasing에서는 사용자 주소 색으로 PFN alias를 flush하고 전체 I-cache를 flush한 뒤 반환합니다. 두 경로 모두 아래의 non-aliasing 실행 분기로 계속 내려가지 않습니다.'),
        ('Ptrace non-aliasing 경로', '남은 VIPT non-aliasing D-cache 경로에서는 IS_EXEC일 때만 코드 동기화를 합니다. I-cache가 VIPT aliasing이면 사용자 색의 flush_icache_alias를 사용하고 아니면 커널 주소 범위의 coherent helper를 사용합니다. cache_ops_need_broadcast가 참이면 smp_call_function으로 다른 CPU의 전체 I-cache flush callback을 호출하고 wait 인자1로 완료를 기다립니다. 단순히 SMP라는 이유만으로 항상 broadcast하는 본문은 아닙니다.'),
        ('사용자 페이지에 복사', 'copy_to_user_page는 SMP일 때 preempt_disable 후 memcpy를 하고 flush_ptrace_access를 수행한 뒤 preempt_enable합니다. 주석은 현재 CPU에서 실행해야 한다고 명시합니다. 선점 방지는 이 구간의 CPU 이동 문제와 관련되며 대상 데이터를 다른 CPU가 수정하지 못하도록 하는 범용 상호 배제 잠금은 아닙니다.'),
        ('Lowmem folio', '__flush_dcache_folio는 highmem이 아니면 folio_address와 folio_size로 커널 매핑 전체를 __cpuc_flush_dcache_area에 전달합니다. folio를 항상 한 페이지라고 가정하지 않고 크기와 페이지 수를 각각 사용합니다. 이 내부 함수는 마지막의 cache alias 처리도 계속 수행합니다.'),
        ('Highmem 두 경로', 'highmem이며 VIPT non-aliasing이면 folio의 각 페이지 offset을 kmap_local_folio로 매핑하고 PAGE_SIZE만큼 flush한 뒤 kunmap_local합니다. 그 밖의 highmem 경로는 kmap_high_get으로 기존 매핑을 얻은 경우에만 PAGE_SIZE flush와 kunmap_high를 수행합니다. NULL이면 그 페이지의 해당 분기 작업을 건너뛰며 두 경로의 매핑 획득 방식을 같다고 설명하면 안 됩니다.'),
        ('파일 위치에 맞춘 색', '__flush_dcache_folio의 마지막은 mapping이 있고 VIPT aliasing이면 folio_pfn과 folio_pos를 flush_pfn_alias에 전달합니다. 주석은 페이지 캐시의 관련 사용자 색이 index와 합치되므로 해당 색의 flush를 선택한다고 설명합니다. 여기에도 folio의 모든 PFN을 반복하는 별도 alias 루프는 없습니다.'),
        ('사용자 alias 검색 자료구조', '__flush_dcache_aliases는 current->active_mm을 기준으로 pgoff=folio->index와 닫힌 끝 pgoff_end=pgoff+folio_nr_pages-1을 만듭니다. mapping 잠금 아래 i_mmap 구간 트리의 겹치는 VMA를 순회하고 현재 active_mm이 아니거나 VM_MAYSHARE가 없으면 건너뜁니다. 모든 프로세스의 모든 VMA를 무조건 flush하는 선형 전체 순회가 아닙니다.'),
        ('겹치는 범위 계산', '각 VMA에서 start는 vm_start, pfn은 folio 시작, nr은 folio 페이지 수로 시작합니다. unsigned offset=pgoff-vm_pgoff를 구해 offset>-nr이면 앞쪽이 VMA 밖인 겹침을 처리하도록 pfn-=offset,nr+=offset을 수행하고, 아니면 start+=offset*PAGE_SIZE로 VMA 내부 시작을 옮깁니다. 끝이 vm_end를 넘으면 nr을 잘라 flush_cache_pages에 전달합니다. 음수처럼 보이는 차이를 unsigned wrap으로 다루는 코드이므로 signed 비교로 임의 번역하면 안 됩니다.'),
        ('겹침 숫자 예제', 'folio index10·4페이지이고 VMA 시작 파일 offset12이면 두 페이지만 겹칩니다. 이 ARM의 unsigned 계산에서 offset은-2의 wrap 값이며 pfn-=offset은 PFN을2 올리고 nr+=offset은4를2로 줄입니다. 반대로 VMA offset8이면 offset2여서 start를2페이지 옮깁니다. 두 경우 모두 이후 vm_end에 의한 추가 절단이 가능합니다.'),
        ('PTE 설치 쪽 동기화', '아키텍처6 이상에서 __sync_icache_dcache는 VIPT non-aliasing의 비실행 PTE이면 즉시 반환합니다. 유효하지 않은 PFN과 reserved folio도 건너뜁니다. VIPT aliasing이면 folio_flush_mapping을 얻고 아니면 mapping=NULL입니다. test_and_set_bit(PG_dcache_clean)의 이전 값이0일 때만 내부 D-cache flush를 수행하며 실행 PTE이면 전체 I-cache를 flush합니다.'),
        ('Clean 비트의 읽기', 'PG_dcache_clean은 이 동기화 프로토콜의 상태 비트입니다. __sync_icache_dcache는 test-and-set으로 이미 처리된 상태를 검사하고, 쓰기 이후 flush_dcache_folio는 상황에 따라 비트를 지워 나중 작업이 다시 필요함을 표시합니다. 원자 비트 연산 하나만으로 전체 folio 데이터가 동시 수정에서 보호되는 것은 아닙니다.'),
        ('공개 folio flush의 빠른 경로', 'flush_dcache_folio는 zero PFN이면 쓰지 않는 페이지라는 주석에 따라 반환합니다. broadcast가 필요 없고 VIPT non-aliasing이면 clean 비트가 있을 때 지우고 반환합니다. 주석의 coherent라서 작업 불필요하다는 설명과 달리 상태 비트 갱신은 남아 있으며 특히 이후 실행 매핑 동기화와 함께 읽어야 합니다.'),
        ('지연 flush와 즉시 flush', '나머지 경로는 mapping을 얻습니다. broadcast가 필요 없고 mapping이 있으며 사용자 매핑이 없으면 clean 비트를 지워 지연합니다. 그렇지 않으면 __flush_dcache_folio를 실행하고 mapping+VIVT이면 사용자 aliases를, mapping이 있는 다른 경우는 전체 I-cache를 처리한 뒤 clean 비트를 설정합니다. broadcast가 필요한 구성에서는 이 지연 분기를 사용하지 않습니다.'),
        ('Page 래퍼와 export', 'flush_dcache_folio와 flush_dcache_page를 export합니다. page 래퍼는 page_folio(page)를 구해 folio 함수를 호출하므로 전달받은 작은 page 하나만의 바이트 범위를 독립 처리한다고 설명하면 틀립니다. 내부 helper들은 모두 공개 export된 것이 아닙니다.'),
        ('익명 페이지의 순서', '__flush_anon_page는 전방 선언과 정의가 함께 있습니다. VIPT non-aliasing이면 반환하고, VIVT는 flush_cache_page, 그 밖은 PFN alias와 전체 I-cache flush를 수행합니다. 이후 page_address의 PAGE_SIZE에 __cpuc_flush_dcache_area를 적용합니다. 주석의 예상 호출 순서는 get_user_pages에서 flush_anon_page, memcpy, 쓰기가 있었다면 flush_dcache_page입니다. 주석은 마지막 커널 매핑 작업이 invalidate만 필요한 의도보다 writeback+invalidate로 과도하다는 FIXME도 남깁니다.'),
        ('CS 연결과 검증 범위', '가상/물리 인덱스·태그, 같은 물리 페이지의 주소 별칭, cache colour, folio와 highmem, bit 상태 기계, 구간 트리의 겹침 검색, unsigned 모듈러 산술, 다른 CPU callback을 학습합니다. 원본 대응과 빌드 검사는 실제 ARM 캐시 일관성이나 모든 CPU 구성의 실행 검증을 대신하지 않습니다.')
    ],
    questions=[
        ('arm_heavy_mb에서 두 callback이 모두 있으면 호출 순서는?', 'outer_cache.sync 뒤 soc_mb이다', 'soc_mb 뒤 outer_cache.sync이다', 'OUTER_CACHE_SYNC 구성에서 outer callback을 먼저 검사·호출하고 이어 soc_mb를 검사합니다. dsb는 앞서 barrier.h 래퍼의 역할입니다.'),
        ('Highmem·VIPT non-aliasing folio를 내부 helper가 처리하는 방식은?', '각 페이지를 local 매핑하고 flush한 뒤 해제한다', 'folio 전체가 항상 영구 kernel 주소를 가진다고 가정한다', 'folio_nr_pages만큼 kmap_local_folio(offset),PAGE_SIZE flush,kunmap_local을 반복합니다. lowmem의 folio_address 경로와 구별합니다.'),
        ('cache_ops_need_broadcast가 참이면 mapping이 있고 미매핑인 folio도 지연 분기에 들어가는가?', '아니다. 지연 조건이 broadcast 불필요를 요구한다', '그렇다. mapping 유무만으로 지연한다', 'if 조건에 !cache_ops_need_broadcast()가 포함됩니다. 다른 CPU의 유지보수가 필요한 환경에서 지연 최적화를 무조건 적용하지 않습니다.'),
        ('folio index10·4페이지, VMA 파일 offset12이면 VMA 끝 절단 전 남은 범위는?', 'folio PFN을2 올린2페이지이다', 'folio PFN을2 내린6페이지이다', '앞의 두 페이지가 VMA 시작보다 앞입니다. unsigned offset=-2의 wrap 값을 사용한 pfn-=offset,nr+=offset이 각각+2와-2 효과를 냅니다.'),
        ('__sync_icache_dcache에서 PG_dcache_clean이 이미1이면 D-cache helper를 다시 호출하는가?', '아니다. 이전 비트가0일 때만 호출한다', '그렇다. test_and_set 결과가1일 때 호출한다', '조건은 !test_and_set_bit입니다. 다만 실행 PTE의 I-cache flush는 그 다음 별도 조건이므로 D-cache 생략과 함께 무조건 생략된다고 보면 틀립니다.'),
        ('copy_to_user_page의 preempt_disable이 제공하는 것은?', 'SMP에서 복사와 cache 처리 중 선점을 막는다', '모든 다른 CPU의 같은 페이지 쓰기를 잠금으로 막는다', '본문에는 공유 페이지 상호 배제 잠금이 없습니다. 현재 CPU에서 처리해야 한다는 주석과 선점 구간을 연결해야 합니다.'),
        ('flush_dcache_page가 folio 중 한 page를 받으면 무엇을 호출하는가?', 'page_folio로 얻은 folio의 flush 함수이다', '언제나 해당 page의1바이트만 flush한다', '래퍼는 flush_dcache_folio(page_folio(page))입니다. 실제 작업 범위와 지연 여부는 folio 처리 분기가 결정합니다.'),
        ('__flush_dcache_aliases의 VMA 필터는?', '현재 active_mm이며 VM_MAYSHARE가 있는 VMA이다', '모든 mm의 모든 VMA이다', '구간 트리의 파일 offset 겹침 검색 뒤 vm_mm과 VM_MAYSHARE를 추가 검사합니다. 범위 검색과 문맥 필터는 서로 다른 단계입니다.')
    ]
)]
