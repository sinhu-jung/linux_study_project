"""Whole ARM highmem and fixed mapping interface headers."""
ROWS = [dict(
    path='arch/arm/include/asm/highmem.h',
    title='ARM highmem 전체: 기존 매핑 유지와 TLB 제약',
    intro='영구 kmap 영역 계산, 기존 매핑 재사용 조건, local 매핑 전후 hook을 읽습니다.',
    principle='페이지의 물리적 존재와 현재 사용할 수 있는 커널 가상 주소는 별개이며 매핑의 사용 수명과 TLB 상태를 함께 관리해야 합니다.',
    use='flush.c의 kmap_high_get 반환값 검사와 local 매핑 흐름을 이 아키텍처 계약에 연결합니다.',
    area='highmem · 가상 주소 · 참조 수명 · IRQ와 IPI · TLB · 캐시',
    sections=[
        ('파일 구조와 주소 계산', 'GPL-2.0과 guard 뒤 cachetype.h·fixmap.h를 포함합니다. PKMAP_BASE는 PAGE_OFFSET-PMD_SIZE, LAST_PKMAP은 PTRS_PER_PTE, MASK는 그 수에서1을 뺀 값입니다. PKMAP_NR는 기준 주소와의 차이를 PAGE_SHIFT만큼 이동하고 PKMAP_ADDR는 인덱스를 페이지 크기로 확대해 기준에 더합니다. 이 산술 매크로에는 범위 검사나 실제 PTE 설치가 없습니다.'),
        ('Kmap 캐시와 테이블', 'flush_cache_kmaps는 VIVT인 경우에만 flush_cache_all을 호출합니다. pkmap_page_table은 pte_t 포인터의 extern 선언이며 테이블의 할당·초기화 본문은 없습니다. 이 hook 하나가 모든 캐시 종류의 모든 유지보수 작업을 나타내는 것은 아닙니다.'),
        ('기존 매핑 사용 수명', '주석은 kmap_high_get이 atomic 문맥에서 이미 존재하는 가상 매핑을 사용하는 동안 사용 수가0이 되지 않도록 하는 목적을 설명합니다. VIVT에는 필수적이고 VIPT에는 새 매핑을 만드는 비용을 줄이는 최적화라고 구분합니다. 반환 포인터를 얻는 것과 별도의 새 매핑을 항상 만드는 것을 혼동하지 않습니다.'),
        ('SMP와 TLB 방송 제약', 'ARCH_NEEDS_KMAP_HIGH_GET을 먼저 정의하지만 CONFIG_SMP와 CONFIG_CPU_TLB_V6가 함께 있으면 해제합니다. 주석은 hardware TLB maintenance broadcast가 없는 플랫폼에서 관련 잠금이 IRQ도 막아야 하며 global TLB 작업의 IPI와 양립하지 않는다고 설명합니다. 이 조건 안에서 HIGHMEM과 CPU_CACHE_VIVT까지 함께 있으면 #error로 빌드를 거부합니다.'),
        ('Erratum 구성', 'CONFIG_ARM_ERRATA_798181도 ARCH_NEEDS_KMAP_HIGH_GET을 해제합니다. 주석은 kmap의 TLB invalidation을 broadcast할 수 있어야 한다는 이유를 제시합니다. 이 파일은 erratum의 하드웨어 세부 조건이나 완화 알고리즘 전체를 구현하지 않습니다.'),
        ('지원되는 get hook', 'ARCH_NEEDS_KMAP_HIGH_GET이 남으면 kmap_high_get을 extern 선언하고 arch_kmap_local_high_get을 정의합니다. DEBUG_HIGHMEM이 켜지고 VIVT가 아니면 NULL을 반환하며 아니면 kmap_high_get에 위임합니다. 같은 이름의 자기참조 매크로로 generic 코드가 아키텍처 hook 존재를 탐지할 수 있게 합니다.'),
        ('지원되지 않는 경로', 'ARCH_NEEDS_KMAP_HIGH_GET이 없으면 kmap_high_get 자체를 항상 NULL을 반환하는 inline 함수로 제공합니다. 이 분기에는 앞의 arch_kmap_local_high_get 정의가 없습니다. NULL은 현재 helper로 재사용할 주소를 얻지 못했다는 의미이며 page가 존재하지 않는다는 판정은 아닙니다.'),
        ('Local 매핑 전후', 'arch_kmap_local_post_map은 local_flush_tlb_kernel_page(vaddr)를 호출하며 형식 인자 pteval은 본문에서 사용하지 않습니다. pre_unmap은 VIVT일 때 주소의 PAGE_SIZE에 __cpuc_flush_dcache_area를 적용합니다. post_unmap은 다시 local TLB flush입니다. 여기에는 다른 모든 CPU로 IPI를 직접 보내는 코드가 없습니다.'),
        ('CS 연결과 범위', '페이지 단위 주소 변환, 사용 수 기반 수명 보호, IRQ와 IPI의 상호 제약, 구성 조합의 compile-time 거부, 매핑 변경과 TLB·캐시 유지보수를 학습합니다. 실제 kmap 할당 알고리즘과 잠금 구현은 다른 파일에 있으며 이 헤더만으로 전부 검증한 것으로 세지 않습니다.')
    ],
    questions=[
        ('PKMAP_NR(PKMAP_ADDR(3))의 정상 범위 계산 결과는?', '3이다', 'PAGE_SIZE이다', '주소는 BASE+3*PAGE_SIZE이고 기준을 빼 PAGE_SHIFT만큼 오른쪽 이동하므로3입니다. 매크로 자체가 잘못된 입력의 범위를 검사하는 것은 아닙니다.'),
        ('DEBUG_HIGHMEM이면 arch_kmap_local_high_get은 항상 NULL인가?', '아니다. VIVT가 아닌 경우에 NULL이다', '그렇다. 캐시 종류를 확인하지 않는다', '조건은 IS_ENABLED(DEBUG_HIGHMEM) && !cache_is_vivt()입니다. VIVT의 기존 매핑 사용 요구를 구분합니다.'),
        ('ARCH_NEEDS_KMAP_HIGH_GET이 해제됐을 때 kmap_high_get은?', '항상 NULL을 반환하는 inline 함수이다', '항상 새 매핑을 할당한다', '대체 본문은 return NULL뿐입니다. 호출자는 재사용 가능한 주소를 얻었다고 가정할 수 없습니다.'),
        ('local pre_unmap에서 모든 캐시 종류를 무조건 flush하는가?', '아니다. VIVT일 때만 D-cache 영역을 flush한다', '그렇다. 매번 전체 시스템 캐시를 flush한다', '조건은 cache_is_vivt이며 범위는 vaddr의 PAGE_SIZE입니다. post_unmap의 local TLB flush와도 별개입니다.')
    ]
), dict(
    path='arch/arm/include/asm/fixmap.h',
    title='ARM fixmap 전체: 슬롯 배치와 부팅 단계별 재사용',
    intro='고정 매핑 영역의 인덱스, kmap과 early_ioremap의 공유, 페이지 보호 속성을 읽습니다.',
    principle='같은 주소 자원을 동시에 쓰지 않는 수명 구간에 재사용하며 인덱스 경계와 실제 페이지 보호 속성을 따로 관리합니다.',
    use='highmem.h가 포함하는 fixed mapping 인터페이스와 초기 부팅의 임시 I/O 매핑을 연결합니다.',
    area='주소 공간 배치 · 열거형 · 수명에 따른 재사용 · PTE 보호 · MMU',
    sections=[
        ('영역과 포함 관계', 'GPL-2.0과 guard 뒤 FIXADDR_START=0xffc80000, END=0xfff00000, TOP=END-PAGE_SIZE를 정의합니다. linux/pgtable.h와 asm/kmap_size.h를 포함합니다. TOP은 END 자체가 아니라 마지막 페이지의 시작 주소이며 페이지 크기에 의존합니다.'),
        ('상시 슬롯과 kmap', 'fixed_addresses의 첫 값 FIX_EARLYCON_MEM_BASE는0이고 다음 영구 영역 끝 경계는1입니다. FIX_KMAP_BEGIN은 그 경계, END는 BEGIN+KM_MAX_IDX*NR_CPUS-1로 양끝 포함 범위를 정의합니다. 슬롯 수는 CPU 수와 CPU별 최대 매핑 인덱스 수의 곱입니다. 경계 이름을 별도의 사용 슬롯으로 더 세면 off-by-one이 됩니다.'),
        ('텍스트 수정 슬롯', 'KMAP_END 뒤에 FIX_TEXT_POKE0와1, 그리고 __end_of_fixmap_region이 이어집니다. 주석은 kprobes·jump labels 등이 읽기 전용 커널 텍스트를 쓰기 위해 사용한다고 설명합니다. enum 선언 자체가 커널 텍스트를 수정하거나 잠금을 잡지는 않습니다.'),
        ('초기 I/O 매핑 공간', 'NR_FIX_BTMAPS=32, FIX_BTMAPS_SLOTS=7이므로 TOTAL은224입니다. FIX_BTMAP_END는 영구 영역 끝과 같고 BEGIN은 END+224-1입니다. 초기 영역 끝 경계는 그 다음 값입니다. BEGIN/END라는 단어의 숫자 대소를 kmap 구간과 같게 추측하면 안 됩니다. 여기서는 BEGIN의 인덱스 값이 더 큽니다.'),
        ('겹치는 주소의 수명', '주석은 early_ioremap은 paging_init 이전, kmap은 이후에만 사용할 수 있어 kmap 영역을 공유해도 충돌하지 않는다고 설명합니다. 실제 자원 재사용의 근거는 잠금으로 동시 접근을 직렬화하는 것이 아니라 사용 시기의 분리입니다. __end_of_fixed_addresses는 두 영역 끝의 합이 아니라 큰 값을 선택합니다.'),
        ('페이지 속성 조합', 'FIXMAP_PAGE_COMMON은 YOUNG|PRESENT|XN|DIRTY입니다. NORMAL은 pgprot_kernel|XN, RO는 NORMAL|RDONLY입니다. IO는 COMMON에 MT_DEV_SHARED와 SHARED를 더하며 NOCACHE도 IO와 같습니다. 이 파일에서 nocache 이름은 일반 RAM의 모든 캐시 정책을 포괄하는 독립 모드가 아니라 장치 매핑용 별칭입니다.'),
        ('MMU 구성과 초기화', '__early_set_fixmap은 __set_fixmap의 별칭입니다. CONFIG_MMU이면 idx·phys·prot를 받는 __set_fixmap과 __init early_fixmap_init을 선언하고 asm-generic/fixmap.h를 포함합니다. 비MMU 분기에서는 빈 early_fixmap_init만 정의합니다. 이 파일의 선언만으로 PTE 쓰기나 TLB 무효화의 구체적 구현을 설명할 수는 없습니다.'),
        ('CS 연결과 범위', '닫힌 인덱스 범위와 끝 경계, 배열 크기의 곱, 서로 다른 수명에 따른 저장 공간 공유, bitwise 보호 속성 조합, 선언과 구현의 분리를 학습합니다. 주소 상수만으로 모든 구성의 영역 적합성이나 MMU 동작을 실행 검증한 것은 아닙니다.')
    ],
    questions=[
        ('초기 boot mapping의 TOTAL_FIX_BTMAPS는?', '224이다', '39이다', '32개와7슬롯의 곱32*7=224입니다. 두 상수의 합을 사용하는 식이 아닙니다.'),
        ('__end_of_fixed_addresses는 두 영역 끝을 어떻게 결합하는가?', '둘 중 큰 값을 선택한다', '두 값을 더한다', '동일 주소 공간을 시간에 따라 재사용하므로 조건식으로 최대 경계를 선택합니다. 별도 연속 영역처럼 합산하지 않습니다.'),
        ('early_ioremap과 kmap 영역 공유의 주석상 근거는?', 'paging_init을 기준으로 사용 시기가 나뉜다', '이 enum이 항상 전역 잠금을 획득한다', 'early_ioremap은 이전, kmap은 이후라는 수명 조건입니다. enum에는 잠금 실행이 없습니다.'),
        ('FIXMAP_PAGE_NOCACHE는 이 파일에서 무엇인가?', 'FIXMAP_PAGE_IO의 별칭이다', '읽기 전용 NORMAL과 완전히 같다', '주석은 set_fixmap_io와 nocache가 모두 장치 매핑 목적이라고 설명하며 매크로도 IO로 정의합니다.')
    ]
)]
