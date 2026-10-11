"""Whole page flags compile-time field allocation contract."""
ROWS = [dict(
    path='include/linux/page-flags-layout.h',
    title='페이지 플래그 비트 예산: NUMA·영역·LRU 필드 배치',
    intro='한 unsigned long의 제한된 비트를 여러 메모리 관리 기능이 나누는 컴파일 시점의 규칙을 읽습니다.',
    principle='필드의 논리적 필요 폭과 실제 저장 폭을 구분하고, 공간 부족을 외부 조회 또는 빌드 오류로 처리합니다.',
    use='메모리 모델과 커널 구성에 따라 page->flags의 저장 정보가 달라지는 이유를 이해합니다.',
    area='비트 패킹 · 정보 표현 · 제약 조건 · NUMA · 조건부 컴파일',
    sections=[
        ('파일 전체의 역할', 'GPL-2.0 헤더이며 numa.h와 generated/bounds.h를 포함합니다. zone, section, node, KASAN tag, 마지막 CPU/PID, LRU 참조 정보의 폭을 결정합니다. 실제 struct page 정의, 필드별 비트 이동 위치, 값을 읽고 쓰는 함수, 페이지 할당 알고리즘은 이 파일에 없습니다. 상단 주석은 gfp_mask의 zone 힌트가 우선순위가 있는 zone 목록 선택에 사용된다고 설명합니다.'),
        ('Zone 수를 표현하는 폭', 'MAX_NR_ZONES가 2 미만이면 ZONES_SHIFT는 0, 2 이하이면 1, 4 이하이면 2, 8 이하이면 3입니다. 8보다 크면 전처리 오류가 납니다. 유효한 양의 zone 개수에서는 식별자 표현에 필요한 ceil(log2(N))에 해당하며 ZONES_WIDTH는 그 값을 사용합니다. 3개 zone은 2비트가 필요하고 가능한 비트 조합 하나가 남습니다. 이 헤더가 zone 수 자체를 세거나 목록을 만드는 것은 아닙니다.'),
        ('Section 번호의 논리적 폭', 'CONFIG_SPARSEMEM이면 asm/sparsemem.h를 포함하고 SECTIONS_SHIFT를 MAX_PHYSMEM_BITS-SECTION_SIZE_BITS로 정합니다. 아니면 0입니다. 물리 주소 공간 크기에서 한 section의 크기를 뺀 지수는 section 식별자에 필요한 비트 수입니다. 예를 들어 두 값이 46과 27이라면 차이는 19입니다. 이는 메모리 용량의 바이트 수가 아닙니다.'),
        ('VDSO 빌드 경계', 'BUILD_VDSO32_64가 정의되면 이후의 레이아웃 본문 전체를 건너뜁니다. 앞의 include, ZONES_SHIFT/WIDTH 및 SECTIONS_SHIFT 결정까지 없어지는 것은 아닙니다. 정의 여부를 보는 #ifndef이므로 값이 0인 매크로도 정의되어 있으면 본문을 건너뜁니다.'),
        ('메모리 모델과 저장 폭', '고전 sparsemem, 즉 SPARSEMEM이고 SPARSEMEM_VMEMMAP이 아닐 때만 SECTIONS_WIDTH가 SECTIONS_SHIFT가 됩니다. 그 밖에는 0입니다. 따라서 sparse vmemmap에서 논리적 section 번호 폭이 존재해도 page->flags에 저장하는 section 필드 폭은 0일 수 있습니다. 주석의 다섯 배치 예는 node·section 및 last_cpupid의 유무를 설명하는 개략도이며 이후 식에 나오는 KASAN/LRU 필드 전체를 그림으로 열거하지는 않습니다.'),
        ('Node 필드의 첫 번째 예산 검사', 'ZONES_WIDTH+LRU_GEN_WIDTH+SECTIONS_WIDTH+NODES_SHIFT가 BITS_PER_LONG-NR_PAGEFLAGS 이하면 NODES_WIDTH=NODES_SHIFT입니다. 공간이 모자라고 SPARSEMEM_VMEMMAP이면 빌드 오류, 그 밖에는 NODES_WIDTH=0입니다. 이 첫 검사에는 KASAN_TAG_WIDTH나 LAST_CPUPID_SHIFT가 들어가지 않습니다. 뒤의 최종 검사까지 통과해야 전체 배치가 성립합니다.'),
        ('외부 node 조회 표시', 'NODES_SHIFT가 0이 아니면서 NODES_WIDTH가 0이면 NODE_NOT_IN_PAGE_FLAGS를 값 1로 정의합니다. 주석은 IS_ENABLED로 검사할 수 있도록 값이 꼭 있어야 한다고 명시합니다. node 식별 정보가 필요 없다는 뜻이 아니라 이 필드에 넣지 못했다는 뜻입니다. 별도 조회의 구현이나 자료구조는 이 헤더에 없습니다.'),
        ('KASAN과 마지막 접근자 정보', 'KASAN_SW_TAGS 또는 KASAN_HW_TAGS이면 KASAN_TAG_WIDTH는 8, 아니면 0입니다. NUMA_BALANCING이면 LAST__PID_SHIFT=8, PID mask=255이고 CPU 폭은 NR_CPUS_BITS, CPU mask는 (1<<폭)-1입니다. LAST_CPUPID_SHIFT는 두 폭의 합입니다. NUMA_BALANCING이 없으면 합계 폭만 0으로 정의하며 이 분기에서 개별 PID/CPU 매크로까지 정의하지는 않습니다. PID 부분 8비트를 완전한 프로세스 ID 저장 공간으로 해석하면 안 됩니다.'),
        ('Last cpupid를 넣을 수 있는가', 'zone, LRU generation, section, 실제 node 폭, KASAN tag와 LAST_CPUPID_SHIFT의 합이 남은 비트 예산 이하면 LAST_CPUPID_WIDTH는 요청 폭이 됩니다. 아니면 0입니다. 요청 폭이 있는데 저장 폭이 0이면 LAST_CPUPID_NOT_IN_PAGE_FLAGS를 값 없이 정의합니다. 앞의 NODE_NOT_IN_PAGE_FLAGS와 정의 형식이 다릅니다. 이 표시가 생긴다고 이 파일 안에서 별도 저장 공간을 할당하지는 않습니다.'),
        ('필수 정보의 최종 한도', '같은 합에서 LAST_CPUPID_SHIFT 대신 실제 LAST_CPUPID_WIDTH를 사용해 남은 예산보다 큰지 검사합니다. 크면 Not enough bits in page flags 오류입니다. cpupid를 포기해도 KASAN 등을 포함한 필수 필드 합이 넘칠 수 있으므로 이 검사가 필요합니다. 예를 들어 남은 예산 20비트, zone/LRU/section/node 합계 16비트이면 첫 node 검사를 통과할 수 있지만 KASAN 8비트 추가 후 합계 24비트로 실패할 수 있습니다.'),
        ('LRU 참조 폭과 잔여 예산', 'LRU_REFS_WIDTH는 __LRU_REFS_WIDTH와 모든 앞선 필드를 뺀 잔여 비트 수 중 작은 값입니다. LRU_GEN_WIDTH와 LRU_REFS_WIDTH는 서로 다른 항목입니다. 마지막 참조 폭은 반드시 원래 요청 폭을 보장하지 않으며 잔여가 0이면 0이 됩니다. 예를 들어 잔여 3비트에 요청 5비트면 실제 3비트입니다. MAX_NR_TIERS에 관한 별도 주석을 참조하지만 이 파일에서 tier 정책 자체를 구현하지는 않습니다.'),
        ('CS 연결과 검증 범위', '제한된 저장 공간에 식별자와 메타데이터를 배치하는 문제, 논리적 폭과 물리적 폭의 차이, 선택적 필드 포기, 컴파일 시점 불변식 검사를 학습합니다. 각 구성 분기는 런타임에 메모리 여유를 보고 고르는 분기가 아닙니다. 원본 대조와 학습 데이터 검증만으로 모든 아키텍처·Kconfig 조합의 커널 빌드가 검증되었다고 말할 수는 없습니다.')
    ],
    questions=[
        ('MAX_NR_ZONES가 3이면 ZONES_WIDTH는 얼마인가?', '2비트이다', '3비트이다', '3개의 식별자를 1비트로 표현할 수는 없고 2비트이면 4개 조합이 가능합니다. 전처리 분기에서 4 이하 조건에 들어갑니다.'),
        ('SPARSEMEM_VMEMMAP에서 SECTIONS_SHIFT가 양수이면 SECTIONS_WIDTH도 반드시 양수인가?', '아니다. SECTIONS_WIDTH는 0이다', '그렇다. 두 매크로는 항상 같다', '실제 section 필드는 고전 sparsemem 분기에서만 저장합니다. 식별자에 필요한 논리적 폭과 page->flags에 할당하는 폭은 다릅니다.'),
        ('첫 node 예산 검사가 통과하면 전체 필드 배치가 보장되는가?', '아니다. KASAN 등을 포함한 최종 검사에서 실패할 수 있다', '그렇다. 이후에는 오류 조건이 없다', '첫 식에는 KASAN과 cpupid가 없습니다. cpupid 저장을 포기해도 KASAN을 포함한 합계가 한도를 넘으면 최종 #error가 발생합니다.'),
        ('LRU 참조 정보의 요청 폭이 5비트이고 최종 잔여가 3비트이면 실제 폭은?', '3비트이다', '요청을 우선하여 5비트이다', 'LRU_REFS_WIDTH는 요청 폭과 잔여 폭의 min입니다. 한 비트도 남지 않는다면 0일 수 있습니다.'),
        ('NODE_NOT_IN_PAGE_FLAGS와 LAST_CPUPID_NOT_IN_PAGE_FLAGS는 모두 값 1로 정의되는가?', '아니다. node 표시는 1이고 cpupid 표시는 값이 없다', '그렇다. 두 정의는 완전히 같다', 'node 표시는 IS_ENABLED 검사 가능성을 주석으로 명시하며 1을 부여합니다. cpupid 표시는 존재 여부를 알리는 빈 매크로입니다. 서로 다른 정의를 같은 검사 방식으로 임의 치환하면 안 됩니다.')
    ]
)]
