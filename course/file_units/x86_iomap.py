"""Whole x86 32-bit iomap implementation and its interface header."""
ROWS = [dict(
    path='arch/x86/mm/iomap_32.c',
    title='x86 I/O 매핑 전체: 캐시 속성 예약과 local PFN 매핑',
    intro='물리 주소 제한 검사,WC 예약 결과와 PTE 보호값,비PAT fallback을 해설합니다.',
    principle='캐시 속성 예약과 실제 가상 페이지 매핑은 별도 단계이며 요청한 WC와 선택된 최종 모드를 구분합니다.',
    use='io-mapping.h의 iomap_create_wc/free 및 local helper 호출을 실제 구현과 연결합니다.',
    area='PAE · 물리 주소 폭 · PAT와 MTRR · 캐시 모드 · PTE 마스크',
    sections=[
        ('전체 구성', 'GPL-2.0-or-later·저작권 뒤 iomap/memtype/export/highmem 헤더를 포함합니다. 내부 주소 가능성 검사,공개 create/free/local map 세 함수와 각각의 GPL export가 전부입니다. 사용자 VMA 매핑이나 장치 read/write 동작은 이 파일에 없습니다.'),
        ('PAE 없는 주소 한계', 'is_io_mapping_possible은 X86_PAE가 없고 PHYS_ADDR_T_64BIT가 있을 때 base+size>0x100000000이면0입니다. 끝이 정확히2^32이면 이 비교만으로 거부하지 않습니다. 나머지 구성이나 범위는1을 반환합니다. 크기0·덧셈 overflow·페이지 정렬을 별도로 검사하는 일반 검증 함수는 아닙니다.'),
        ('WC 요청과 예약', 'iomap_create_wc는 pcm을 WC로 시작합니다. 가능성 검사가 실패하면 -EINVAL,아니면 memtype_reserve_io(base,base+size,&pcm)를 호출합니다. 실패 코드는 그대로 반환합니다. pcm을 포인터로 전달하므로 이후 보호값은 함수가 돌려준 모드에 기반하며 요청 상수 WC를 무조건 다시 강제하지 않습니다.'),
        ('보호값 생성', '예약 성공 뒤 *prot=__pgprot(__PAGE_KERNEL|cachemode2protval(pcm))를 만듭니다. 이어 pgprot_val(*prot)에 __default_kernel_pte_mask를 AND해 지원하지 않는 비트를 제거하고0을 반환합니다. 이 단계는 출력 보호값 생성이며 여기서 가상주소를 반환하거나 PTE를 설치하지 않습니다.'),
        ('범위 예약 해제', 'iomap_free는 memtype_free_io(base,base+size)에 위임합니다. 구조체를 kfree하거나 특정 local 주소를 kunmap하는 함수가 아닙니다. 예약 범위의 수명과 한 번의 페이지 매핑 수명을 공통 io_mapping 인터페이스와 함께 구분해야 합니다.'),
        ('비PAT의 비WB 처리', '__iomap_local_pfn_prot는 PAT가 비활성이고 prot의 캐시 모드가 WB가 아니면 prot를 __PAGE_KERNEL|UC_MINUS 모드로 새로 구성합니다. 기존 보호값에 bit 하나만 덧붙이는 형태가 아닙니다. 주석은 직접 PWT를 설정한 호출까지 고려하고 MTRR과 결합해 사용자의 WC 가능 시 WC,그렇지 못하면 UC 의도를 처리하려는 설명을 제공합니다. UC_MINUS를 모든 구성에서 무조건 WC와 같다고 해석하지 않습니다.'),
        ('필터 후 local 매핑', '분기 여부와 무관하게 최종 prot에 기본 PTE mask를 AND한 뒤 __kmap_local_pfn_prot(pfn,prot)를 호출합니다. 반환값을 __force __iomem 포인터로 변환합니다. 입력은 물리 byte 주소가 아니라 PFN이며 byte offset 복원을 이 함수가 수행하지 않습니다. local 매핑의 상세 스택·TLB 동작은 하위 helper 범위입니다.'),
        ('CS 연결과 한계', '주소 폭과 하드웨어 변환 능력,반열린 물리 범위,요청과 협상된 캐시 모드,PTE bit 필터,자원 예약과 주소 생성의 분리,구성별 fallback을 학습합니다. 실제 PAT/MTRR 하드웨어 조합과 모든 오류 경로의 실행 시험을 수행한 것은 아닙니다.')
    ],
    questions=[
        ('비PAE·64비트 물리주소 타입에서 base+size가 정확히2^32이면 해당 검사에서 거부되는가?', '아니다.2^32보다 클 때 거부한다', '그렇다.같거나 크면 거부한다', '본문은 > 비교입니다. 이것은 해당 검사의 경계이며 다른 제약까지 모두 만족한다는 뜻은 아닙니다.'),
        ('iomap_create_wc가 반환하는 성공 결과는?', '0이며 출력 prot에 보호값을 기록한다', '매핑된 가상 포인터 자체이다', '반환형은int이고 prot 포인터가 출력입니다. 실제 local 주소는 별도 함수에서 얻습니다.'),
        ('예약 뒤 보호값은 항상 원래 상수 WC만 쓰는가?', '아니다.예약 함수가 반환한 pcm을 사용한다', '그렇다.pcm 출력은 무시한다', 'memtype_reserve_io가 &pcm을 받고 이후 cachemode2protval(pcm)을 사용합니다. 요청 모드와 최종 모드를 구별합니다.'),
        ('PAT가 없고 요청 모드가 비WB이면 local helper는?', 'UC_MINUS 기반 보호값으로 재구성한 뒤 필터한다', '어떤 경우든 요청 prot를 그대로 둔다', '조건부 대입 다음 공통 mask 적용이 있습니다. WB 요청에는 이 대입이 적용되지 않습니다.')
    ]
), dict(
    path='arch/x86/include/asm/iomap.h',
    title='x86 I/O 매핑 선언 전체: 예약·해제·페이지 매핑의 분리',
    intro='세 함수의 인자 단위와 반환형으로 역할을 구분합니다.',
    principle='주소를 만드는 함수와 캐시 속성 자원을 예약하는 함수를 같은 연산으로 취급하지 않습니다.',
    use='공통 io_mapping 헤더와 x86 iomap_32.c 사이의 인터페이스를 읽습니다.',
    area='C 선언 · PFN · 물리 범위 · 출력 인자 · 자원 수명',
    sections=[
        ('파일 전체', 'GPL-2.0-or-later·guard·저작권 뒤 fs/mm/uaccess/highmem/cacheflush/tlbflush 헤더를 포함하고 세 함수만 선언합니다. 함수 본문·전역 객체·초기화 코드는 없습니다.'),
        ('Local PFN 매핑', '__iomap_local_pfn_prot는 unsigned long pfn과 pgprot_t를 받아 void __iomem 포인터를 반환합니다. PFN 단위와 물리 byte 주소를 구분하며 보호 속성을 인자로 받아 사용하는 인터페이스입니다.'),
        ('범위 예약과 해제', 'iomap_create_wc는 resource_size_t base,unsigned long size,pgprot_t 출력 포인터를 받고int를 반환합니다. iomap_free는 같은 base/size를 받아void입니다. 성공·실패 코드와 보호값 출력은 주소 반환과 다르며 정확한 동작은 구현에서 확인합니다.'),
        ('CS 연결과 범위', '단위가 다른 정수 인자,주소공간 주석,포인터 출력값,선언과 구현을 구분합니다. 헤더에 포함된 다른 API까지 이 파일의 구현으로 세지 않으며 이 선언만으로 매핑의 성공이나 캐시 속성을 확정하지 않습니다.')
    ],
    questions=[
        ('__iomap_local_pfn_prot의 첫 인자 단위는?', 'PFN이다', '항상 물리 byte 주소이다', '선언의 pfn과 구현의 __kmap_local_pfn_prot 호출을 연결합니다. byte 주소라면 먼저 적절한 PFN 변환이 필요합니다.'),
        ('iomap_create_wc의 prot 인자는?', 'pgprot_t 결과를 받는 포인터이다', '반드시 매핑된 사용자 가상주소이다', '선언은 pgprot_t *prot이며int 반환과 별도의 출력 채널입니다. 사용자 VMA 매핑 API와 다릅니다.')
    ]
)]
