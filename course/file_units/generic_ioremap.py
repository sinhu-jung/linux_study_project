"""Whole generic regular I/O mapping implementation and address classifier."""
ROWS = [dict(
    path='mm/ioremap.c',
    title='정규 I/O 매핑 전체: 가상 영역 할당과 실패 정리',
    intro='물리 I/O 범위를 커널 가상 영역에 매핑하고 페이지 offset을 보존하는 공통 구현을 해설합니다.',
    principle='가상 주소 공간 확보와 페이지 테이블 설치를 분리하고 설치 실패 시 확보한 영역을 정리합니다.',
    use='고정 슬롯을 사용하는 early_ioremap과 비교하되 정규 매핑의 slab 가용성 조건을 함께 확인합니다.',
    area='I/O 메모리 · vmalloc 영역 · 페이지 정렬 · 오류 경로 · 주소 범위',
    sections=[
        ('전체 구성', 'GPL-2.0·역사적 PC I/O 설명·저작권 뒤 vmalloc/mm/io/export/ioremap 헤더를 포함합니다. generic_ioremap_prot, 조건부 public ioremap_prot, generic_iounmap, 조건부 public iounmap이 전부입니다. 특정 PCI 장치를 탐색하거나 장치 자원의 소유권을 예약하는 코드는 없습니다.'),
        ('정규 할당 전제', 'generic_ioremap_prot는 slab_is_available가 거짓이면 WARN_ON_ONCE 후 NULL을 반환합니다. 주석은 너무 이른 플랫폼 드라이버가 이 경로에 도달할 수 있음을 설명합니다. 정규 함수가 초기 부팅 매핑으로 자동 대체되는 경로는 없습니다.'),
        ('범위 검사', 'last_addr=phys_addr+size-1을 구해 size0 또는 last_addr<phys_addr이면 NULL입니다. 물리 주소의 wraparound를 거부하려는 검사입니다. 장치 자원 소유권, 모든 메모리 타입의 적합성 또는 뒤의 정렬 산술까지 전부 검증하는 일반 유효성 증명으로 확대하지 않습니다.'),
        ('페이지 정렬과 offset', 'offset은 phys_addr의 페이지 내부 비트이고 phys_addr에서 이를 빼 페이지 시작으로 내립니다. size는 PAGE_ALIGN(size+offset)으로 확장합니다. 예를 들어4KiB 페이지에서 phys=0x12345,size=0x100이면 정렬 물리주소0x12000,offset0x345,매핑 길이0x1000입니다. 최종 반환 주소에는 offset을 다시 더합니다.'),
        ('가상 영역 확보', '__get_vm_area_caller에 정렬된 size, VM_IOREMAP, IOREMAP_START/END, 호출자 주소를 전달합니다. 실패하면 NULL입니다. 성공하면 area->addr를 vaddr로 얻고 area->phys_addr에 정렬된 물리주소를 기록합니다. 이것은 물리 장치 메모리 자체를 새로 할당하는 함수가 아닙니다.'),
        ('매핑 설치와 오류 정리', 'ioremap_page_range(vaddr,vaddr+size,phys_addr,prot)를 호출합니다. 결과가0이 아니면 free_vm_area(area) 후 NULL이며 성공하면 vaddr+offset을 __iomem 포인터로 반환합니다. 구체적인 페이지 테이블 구축과 정리 helper의 내부 동작은 다른 파일의 범위입니다. 본문에 없는 자동 재시도나 다른 캐시 속성 fallback을 추가해 설명하지 않습니다.'),
        ('보호 속성 wrapper', 'ioremap_prot가 매크로로 이미 제공되지 않았을 때만 public 함수를 정의합니다. unsigned long prot를 __pgprot로 감싸 generic 함수에 넘기고 EXPORT_SYMBOL로 공개합니다. generic 함수는 pgprot_t를 받습니다. 이 wrapper가 요청 속성을 장치별로 검증하거나 변환 정책을 새로 결정하는 것은 아닙니다.'),
        ('공통 해제', 'generic_iounmap은 전달 주소를 unsigned long으로 변환해 PAGE_MASK로 내림 정렬합니다. is_ioremap_addr(vaddr)가 참일 때만 vunmap을 호출합니다. 유효한 반환 주소의 페이지 내부 offset을 제거하는 과정이며 임의의 매핑 중간 페이지 포인터도 올바른 해제 인자라는 뜻은 아닙니다. 이 함수는 해제할 size를 받지 않습니다.'),
        ('주소 분류와 해제 경계', 'is_ioremap_addr는 별도 헤더의 영역 판별이며 실제 살아 있는 매핑의 소유권 검사와 다릅니다. 범위 밖 주소이면 여기서는 아무 작업 없이 반환하지만 범위 안의 임의 주소에 안전한 해제가 보장되는 것은 아닙니다. iounmap도 #ifndef로 조건부 정의하고 generic 함수에 위임한 뒤 EXPORT_SYMBOL로 공개합니다.'),
        ('CS 연결과 범위', '물리·가상 주소 분리, 페이지 내 offset 복원, 가상 영역 확보와 PTE 설치의 단계, 오류 cleanup, typed protection wrapper, 매크로 기반 아키텍처 대체를 학습합니다. 원본 대응 검사는 실제 MMU·장치 I/O와 모든 경쟁 실행의 검증이 아닙니다.')
    ],
    questions=[
        ('slab이 아직 없을 때 generic_ioremap_prot는?', '경고 후 NULL을 반환한다', '자동으로 early_ioremap을 호출한다', '첫 조건이 WARN_ON_ONCE(!slab_is_available())와 return NULL입니다. 초기 매핑 API로 전환하는 본문은 없습니다.'),
        ('4KiB 페이지에서 phys0x12345,size0x100의 정렬 매핑 길이는?', '0x1000이다', '0x100이다', 'size+offset=0x445를 페이지 크기로 올림합니다. 반환 주소에는0x345를 복원하지만 설치 범위는 페이지 단위입니다.'),
        ('ioremap_page_range가 실패하면 확보한 영역은?', 'free_vm_area로 정리하고 NULL을 반환한다', '성공 포인터를 반환한 뒤 나중에 해제한다', '페이지 범위 설치의 비0 결과를 실패로 처리하는 명시적 경로입니다. 호출자는 NULL을 확인해야 합니다.'),
        ('generic_iounmap은 원래 요청 size를 인자로 받는가?', '아니다. 주소를 정렬해 영역 판별 후 vunmap한다', '그렇다. early_iounmap처럼 주소와 size를 비교한다', '정규 함수의 시그니처는 주소 하나입니다. 초기 고정 슬롯 구현의 prev_size 비교를 그대로 적용하면 틀립니다.'),
        ('is_ioremap_addr가 참이면 그 주소의 매핑 소유권도 검증됐는가?', '아니다. 주소 영역 분류일 뿐이다', '그렇다. 소유자와 모든 PTE를 검사한다', '헤더의 helper는 태그 처리 후 범위 비교를 수행합니다. 살아 있는 매핑 조회나 소유권 검사는 그 본문에 없습니다.')
    ]
), dict(
    path='include/linux/ioremap.h',
    title='I/O 매핑 영역 헤더 전체: 태그 제거와 반열린 범위',
    intro='플랫폼별 I/O 가상 영역과 주소 분류 predicate를 해설합니다.',
    principle='주소가 정해진 구간에 속하는지 확인하는 것은 실제 매핑 존재 여부와 다른 질문입니다.',
    use='generic_iounmap에서 사용하는 is_ioremap_addr의 정확한 검사 범위를 확인합니다.',
    area='주소 태그 · 반열린 구간 · 구성 조건 · 플랫폼 기본값',
    sections=[
        ('파일 구성', 'GPL-2.0·guard 뒤 kasan.h, asm/pgtable.h, asm/vmalloc.h를 포함합니다. HAS_IOMEM 또는 GENERIC_IOREMAP일 때 주소 범위와 predicate를 제공하고 그렇지 않으면 false를 반환하는 같은 이름의 함수만 제공합니다. 매핑을 생성하는 함수 본문은 없습니다.'),
        ('플랫폼별 기본 영역', '주석은 ioremap이 흔히 vmalloc 영역을 쓰지만 Power 같은 아키텍처는 별도 공간일 수 있다고 설명합니다. IOREMAP_START가 아직 없을 때 START와 END를 각각 VMALLOC_START/END로 함께 정의합니다. 두 상수를 독립 #ifndef로 처리하지 않으므로 아키텍처 override의 정의 계약도 함께 읽어야 합니다.'),
        ('태그를 제거한 주소', 'is_ioremap_addr는 kasan_reset_tag(x)의 결과를 unsigned long 주소로 바꿉니다. 원래 포인터의 태그 비트를 그대로 정수 비교에 사용하는 형태가 아닙니다. 이 함수의 목적은 주소 분류이며 KASAN의 전체 객체 수명 검사를 실행하는 본문은 아닙니다.'),
        ('반열린 구간', '판별은 addr>=IOREMAP_START && addr<IOREMAP_END입니다. 시작은 포함하고 끝은 제외합니다. 실제 페이지 테이블을 순회하거나 vm_struct를 찾지 않으므로 이 범위 안에 있다고 유효한 접근 권한이나 매핑 소유권이 증명되는 것은 아닙니다.'),
        ('구성이 없는 경우', 'HAS_IOMEM과 GENERIC_IOREMAP이 둘 다 없으면 모든 입력에 false를 반환합니다. 이 분기에는 태그 제거 또는 범위 비교가 없습니다. 구성별로 함수의 구현 자체가 바뀌는 예이며 정적 최적화와 런타임 주소 검사를 구분하는 학습 자료입니다.')
    ],
    questions=[
        ('IOREMAP_END와 정확히 같은 주소는 범위에 포함되는가?', '아니다. 끝은 제외된다', '그렇다. 양끝을 모두 포함한다', '조건은 addr<END입니다. START 쪽은>=이므로 반열린 구간입니다.'),
        ('범위 비교 전 포인터에 적용하는 것은?', 'kasan_reset_tag이다', 'vunmap이다', '태그를 제거해 주소를 비교합니다. 메모리 매핑 해제는 이 predicate가 수행하지 않습니다.'),
        ('관련 두 구성 옵션이 모두 없으면 반환값은?', '모든 주소에 false이다', '모든 주소에 true이다', '#else의 inline 함수는 return false뿐입니다. I/O 영역 검사가 구성과 무관하게 항상 활성화된다고 가정하면 틀립니다.')
    ]
)]
