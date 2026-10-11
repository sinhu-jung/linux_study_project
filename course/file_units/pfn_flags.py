"""Whole tagged PFN helpers and configuration-dependent page table constructors."""
ROWS = [dict(
    path='include/linux/pfn_t.h',
    title='PFN 플래그 전체: 페이지 존재와 장치 매핑의 구분',
    intro='pfn_t의 상위 비트 플래그,페이지 변환과 구성별 devmap·special 판별을 해설합니다.',
    principle='플래그로 표현한 의미,물리 PFN 유효성,페이지 테이블 엔트리 생성은 서로 다른 검사와 동작입니다.',
    use='pfn.h의 u64 wrapper에 실제 플래그와 변환 helper를 연결합니다.',
    area='태그된 정수 · 비트 마스크 · 장치 메모리 · 페이지 테이블 · 구성별 기능',
    sections=[
        ('전체 구성', 'GPL-2.0·guard와 mm.h 포함 뒤 플래그 및 trace 이름,PFN/주소/page 변환,유효성 판별,구성별 PTE/PMD/PUD 생성,devmap·special 조건으로 끝납니다. 실제 메모리 할당이나 페이지 테이블에 엔트리를 설치하는 본문은 없습니다.'),
        ('상위 비트 배치', 'PFN_FLAGS_MASK는 PAGE_MASK의 낮은 비트 보수를 u64로 바꿔 BITS_PER_LONG_LONG-PAGE_SHIFT만큼 이동합니다. 보통64비트 값에서 SG_CHAIN,SG_LAST,DEV,MAP,SPECIAL은 각각63~59번 비트입니다.4KiB 페이지에서는 mask가 상위12비트를 덮으므로 다섯 이름 붙은 플래그만 OR한 것과는 다릅니다.'),
        ('플래그의 설명', '주석은 SG_CHAIN을 다음 scatterlist 항목 포인터,SG_LAST를 마지막 페이지 항목,DEV를 기본 system memmap 비포함,MAP을 드라이버가 동적으로 page mapping을 마련함으로 설명합니다. SPECIAL은 FS_DAX_LIMITED에서 XIP를 허용하되 get_user_pages는 허용하지 않는 용도입니다. 설명은 사용 문맥이며 이 헤더가 scatterlist나 DAX 동작 전체를 구현하지는 않습니다.'),
        ('Trace와 생성', 'PFN_FLAGS_TRACE는 SPECIAL,SG_CHAIN,SG_LAST,DEV,MAP에 대응하는 출력 이름 목록입니다. __pfn_to_pfn_t는 pfn과 flags&PFN_FLAGS_MASK를 OR합니다. flags는 mask로 제한하지만 입력 pfn의 상위 비트를 별도로 제거하거나 충돌 검사하지 않습니다. 유효한 PFN 범위를 호출자가 제공해야 합니다.'),
        ('기본 변환의 전제', 'pfn_to_pfn_t는 flags0으로 내부 생성 함수를 호출합니다. 주석은 pfn_valid한 입력을 가정한다고 명시하며 실제 pfn_valid 호출은 이 경로에 없습니다. phys_to_pfn_t는 addr를 PAGE_SHIFT만큼 내려 PFN을 만들고 flags와 조합합니다. 페이지 내부 offset은 사라집니다.'),
        ('Page가 있다는 판별', 'pfn_t_has_page는 MAP 비트가 있거나 DEV 비트가 없으면 참입니다. DEV만 있으면 거짓,DEV|MAP이면 참,플래그0도 참입니다. 모든 플래그를 검사하는 전역 유효성 함수가 아니며 실제 pfn_valid 확인과 구분해야 합니다.'),
        ('플래그 제거와 page 반환', 'pfn_t_to_pfn은 val&~PFN_FLAGS_MASK를 unsigned long으로 반환합니다. pfn_t_to_page는 has_page가 참이면 이 PFN으로 pfn_to_page를 호출하고 아니면NULL입니다. 이 함수가 별도로pfn_valid를 호출하지는 않습니다. 플래그 의미와 입력의 유효성 전제가 모두 맞아야 합니다.'),
        ('주소·page 역변환과 valid', 'pfn_t_to_phys는 플래그를 제거한 PFN에 PFN_PHYS를 적용합니다. page_to_pfn_t는 page_to_pfn 결과를 기본 flags0 변환에 넘깁니다. pfn_t_valid는 플래그 제거 후pfn_valid를 호출하며 has_page를 먼저 검사하지 않습니다. 따라서 두 함수의 질문과 조건식을 같다고 외우면 틀립니다.'),
        ('엔트리 생성 조건', 'CONFIG_MMU이면 pfn_t_pte가 pfn_pte에 PFN과pgprot를 전달합니다. THP이면 pfn_t_pmd,그 안에서 HAVE_ARCH_TRANSPARENT_HUGEPAGE_PUD까지 있으면 pfn_t_pud를 제공합니다. 모두 플래그를 제거하고 대응 엔트리 값을 구성하는 wrapper입니다. DEV 플래그만으로 자동 pte_mkdevmap 호출을 추가하지 않습니다.'),
        ('Devmap 판별', 'ARCH_HAS_PTE_DEVMAP이면 DEV|MAP 두 비트가 모두 있어야pfn_t_devmap이 참입니다. 해당 구성이 없으면 항상false입니다. 후자 분기에는pte_mkdevmap,pmd_mkdevmap 선언과 THP/PUD 조건부pud_mkdevmap 선언이 있지만 본문은 없습니다. 선언의 존재를 작동하는 devmap 구현으로 해석하지 않습니다.'),
        ('Special 판별', 'ARCH_HAS_PTE_SPECIAL이면 SPECIAL 비트를 검사하고 없으면false입니다. 값에 비트가 들어 있다는 사실만으로 모든 구성에서pfn_t_special이 참인 것은 아닙니다. 해석 가능한 아키텍처 기능과 저장된 태그를 구분합니다.'),
        ('CS 연결과 범위', '값과 metadata의 비트 분할,타입 폭과 단위 변환,전제 기반 helper와 명시적 검증,구성별 기능 판별,엔트리 생성과설치의분리를 학습합니다. 원본대응·구조 검사는 장치 메모리의 수명이나 모든 페이지 테이블 동작을 실행 검증한 것이 아닙니다.')
    ],
    questions=[
        ('DEV만 있고MAP은 없을 때 pfn_t_has_page는?', '거짓이다', 'DEV가 있으므로 반드시 참이다', '조건은 MAP이 있거나DEV가 없는 경우입니다. DEV|MAP이면 참이지만 DEV만 있으면 둘 다 만족하지 않습니다.'),
        ('pfn_to_pfn_t가 pfn_valid를 실제 호출하는가?', '아니다.주석이 유효한 입력을 전제로 한다', '그렇다.실패하면NULL을 반환한다', '본문은flags0의 내부 생성 호출입니다. 반환형도pfn_t이며 검증 실패 분기가 없습니다.'),
        ('4KiB 페이지의 PFN_FLAGS_MASK는 다섯 플래그 비트만 덮는가?', '아니다.상위12비트를 덮는다', '그렇다.다섯 비트를 OR한 식이다', 'PAGE_SIZE-1의12비트를64-12만큼 옮기는 식입니다. 이름 붙은 플래그 집합과 보존 영역 mask의 폭은 다릅니다.'),
        ('ARCH_HAS_PTE_DEVMAP이 없으면 DEV|MAP 값의 pfn_t_devmap 결과는?', 'false이다', '항상true이다', '구성 없는 분기는 인자와 무관하게false를 반환합니다. 저장된 플래그와 기능 지원 판별을 구분합니다.'),
        ('pfn_t_pte가 DEV 플래그를 보고 자동 devmap 표시까지 하는가?', '아니다.플래그를 제거한 PFN으로 pfn_pte를 호출한다', '그렇다.항상pte_mkdevmap을추가 호출한다', '본문에는 pfn_pte(pfn_t_to_pfn(pfn),pgprot)만 있습니다. 별도의 속성 설정을 추측해 추가하지 않습니다.')
    ]
)]
