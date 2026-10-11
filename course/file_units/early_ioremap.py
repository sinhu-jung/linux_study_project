"""Whole early mapping implementation and common declarations."""
ROWS = [dict(
    path='mm/early_ioremap.c',
    title='초기 I/O 매핑 전체: 고정 슬롯과 부팅 단계 전환',
    intro='정규 ioremap 이전에 사용하는 임시 매핑의 할당·해제·복사와 비MMU 경로를 해설합니다.',
    principle='제한된 고정 슬롯에 페이지 단위 매핑을 설치하고 원래 주소 offset과 요청 크기를 보존합니다.',
    use='앞서 읽은 ARM 및 generic fixmap의 역방향 인덱스 배치를 실제 매핑 루프와 연결합니다.',
    area='초기 부팅 · 가상 메모리 · 슬롯 할당 · 페이지 정렬 · 수명 검증',
    sections=[
        ('전체 구성', 'GPL-2.0·설명·저작권과 관련 kernel/mm/io/fixmap 헤더 뒤 CONFIG_MMU 분기에서 관리 상태·설정·매핑·해제·복사를 구현합니다. 비MMU에서는 물리주소 변환과 빈 해제를 제공하며 early_memunmap 래퍼는 두 구성에 공통입니다. __init·__initdata는 초기화 단계 수명과 관련되므로 일반 런타임 할당 API처럼 사용하지 않습니다.'),
        ('진단과 보호 속성 조정', 'early_ioremap_debug 파라미터 handler는 전달 문자열을 분석하지 않고 debug=1로 설정해0을 반환합니다. weak early_memremap_pgprot_adjust의 기본 구현은 prot를 그대로 반환하며 아키텍처가 대체할 수 있습니다. 이 hook은 주소를 매핑하는 함수 자체가 아닙니다.'),
        ('Paging 단계 전환', 'early_ioremap_reset은 after_paging_init을1로 바꿉니다. 기존 슬롯을 해제하거나 배열을 초기화하는 함수가 아닙니다. 이후 설정·해제는 __late_set_fixmap/__late_clear_fixmap으로 분기합니다. 아키텍처가 이 매크로를 제공하지 않으면 기본 helper는 BUG를 발생시키므로 reset 이후 사용이 모든 환경에서 지원되는 것은 아닙니다.'),
        ('슬롯 상태와 초기화', 'prev_map은 슬롯별 반환 주소, prev_size는 요청 원래 크기, slot_virt는 슬롯의 가상 시작을 보관합니다. setup은 기존 prev_map이 있으면 경고하고 slot_virt[i]=__fix_to_virt(FIX_BTMAP_BEGIN-NR_FIX_BTMAPS*i)를 계산합니다. 이미 쓰는 슬롯을 초기화해서 비우는 본문은 없습니다. 슬롯 수와 한 슬롯의 페이지 수는 다른 상수입니다.'),
        ('누수 검사', 'late_initcall의 check_early_ioremap_leak는 NULL이 아닌 prev_map 개수를 셉니다. 남은 영역이 있으면 경고하고1,없으면0을 반환합니다. 이 검사는 누수를 보고할 뿐 남은 영역을 자동 해제하지 않습니다. debug 옵션은 map/unmap 시 WARN을 통한 추가 추적에도 쓰입니다.'),
        ('빈 슬롯 선택', '__early_ioremap은 SYSTEM_RUNNING 이상이면 경고하지만 그 경고만으로 즉시 반환하지는 않습니다. prev_map을 앞에서부터 선형 탐색해 첫 NULL 슬롯을 고릅니다. 빈 슬롯이 없으면 경고 후 NULL입니다. 별도 잠금이나 동적 슬롯 확장 코드는 없으며 일반적인 동시 런타임 allocator로 해석하면 안 됩니다.'),
        ('크기와 정렬', 'last_addr=phys_addr+size-1을 계산해 크기0 또는 last_addr<phys_addr를 거부합니다. 원래 size를 prev_size에 저장하고 offset_in_page를 보존한 뒤 phys_addr를 PAGE_MASK로 내립니다. 매핑 길이는 PAGE_ALIGN(last_addr+1)-정렬주소로 계산하며 페이지 수가 NR_FIX_BTMAPS보다 크면 거부합니다. 이 검사를 전체 물리주소 유효성 검증으로 확대하지 않습니다.'),
        ('실패 시 상태와 페이지 설치', '페이지 수 초과 실패에서는 prev_size가 이미 갱신됐지만 prev_map은 아직 NULL이므로 슬롯은 점유 상태가 되지 않습니다. 실제 설치는 슬롯 시작 idx에서 물리주소를 PAGE_SIZE씩 올리고 idx를 하나씩 내립니다. fixmap 주소는 인덱스가 작아질수록 증가하므로 연속 물리 페이지와 연속 가상 페이지가 대응합니다. 각 설치 helper의 반환값을 검사하는 rollback 루프는 없습니다.'),
        ('반환 주소와 debug 주의', '설치를 마치면 prev_map=slot_virt+offset을 기록하고 반환합니다. debug WARN에 전달하는 phys_addr는 페이지 루프에서 증가한 뒤의 값이고 size도 정렬된 길이입니다. 로그의 모든 값이 원래 호출 인자라고 설명하면 틀립니다. 원래 요청 크기는 prev_size에 따로 남아 있습니다.'),
        ('정확한 해제 입력', 'early_iounmap은 prev_map과 전달 addr가 정확히 같은 슬롯을 찾습니다. 찾지 못하거나 prev_size와 전달 size가 다르면 경고 후 반환합니다. 반환 주소의 중간 포인터나 임의로 반올림한 크기로 해제하는 API가 아닙니다. NULL도 정상 매핑 포인터처럼 사용하면 안 되며 본문에는 별도의 첫 NULL 전용 검사가 없습니다.'),
        ('해제 페이지 수와 슬롯 반환', '해제는 주소가 fix_to_virt(FIX_BTMAP_BEGIN)보다 낮으면 경고 후 반환합니다. offset+원래 size를 PAGE_ALIGN해 페이지 수를 구하고 같은 인덱스 방향으로 late clear 또는 early set(idx,0,CLEAR)를 수행합니다. 끝나면 prev_map만 NULL로 바꿉니다. prev_size와 slot_virt를0으로 지우지 않아도 슬롯 사용 여부는 prev_map으로 결정됩니다.'),
        ('속성별 매핑 API', 'early_ioremap은 FIXMAP_PAGE_IO로 직접 매핑합니다. early_memremap은 NORMAL을 pgprot_adjust에 통과시킨 뒤 주소공간 주석 타입을 __force로 변환합니다. FIXMAP_PAGE_RO가 있을 때만 ro 구현을 제공하며 역시 조정 hook을 사용합니다. CONFIG_ARCH_USE_MEMREMAP_PROT의 prot API는 __pgprot(prot_val)을 직접 넘기므로 이 조정 hook을 호출하지 않습니다.'),
        ('큰 메모리 복사', 'MAX_MAP_CHUNK는 NR_FIX_BTMAPS<<PAGE_SHIFT입니다. copy_from_early_mem은 src의 페이지 offset인 slop을 구하고 clen을 size와 MAX_MAP_CHUNK-slop 중 작은 값으로 제한합니다. 정렬된 src에 clen+slop만큼 매핑하고 p+slop에서 clen만 복사한 뒤 원래 매핑 길이로 해제합니다. dest/src를clen만큼 올리고 size를 줄여 반복합니다.'),
        ('복사 경계 예제', '가정한 슬롯 용량8192바이트, src offset100, 남은 크기9000이면 첫 복사 길이는8092이고 매핑 길이는8192입니다. 이후 src는 페이지 경계가 되며 남은908바이트를 처리합니다. 이 함수에는 early_memremap의 NULL 반환 검사나 오류 반환 경로가 없으므로 실패를 안전하게 복구하는 일반 복사 API라고 설명하면 안 됩니다. size0이면 루프에 들어가지 않습니다.'),
        ('비MMU 구현', '비MMU early_ioremap은 phys_addr를 __iomem 포인터로, memremap과 ro는 일반 포인터로 변환해 반환합니다. size 검사나 별도 매핑 설치는 없고 early_iounmap은 빈 함수입니다. 따라서 ro라는 이름만으로 이 분기가 하드웨어 읽기 전용 보호를 설치한다고 추론하면 틀립니다. 이 분기에는 앞의 chunk 복사 함수나 prot 함수 정의가 없습니다.'),
        ('공통 메모리 해제', 'early_memunmap은 일반 포인터를 __force __iomem 포인터로 바꾸어 early_iounmap에 위임합니다. 타입 주석 변환 자체가 주소 변환이나 물리 페이지 해제가 아닙니다. 실제 동작은 MMU 구성에 따라 슬롯 해제 또는 빈 함수입니다.'),
        ('CS 연결과 범위', '한정된 슬롯의 first-free 탐색, 배열 기반 메타데이터, 페이지 정렬과 offset 복원, 부팅 상태 기계, 정확한 해제 계약, bounded chunk 복사와 오류 처리의 부재를 학습합니다. 이 해설과 원본 대응 검사는 모든 아키텍처의 PTE·TLB 처리를 실행 검증한 것은 아닙니다.')
    ],
    questions=[
        ('early_ioremap_reset은 기존 매핑을 모두 해제하는가?', '아니다. after_paging_init을1로 설정한다', '그렇다. 모든 prev_map을 NULL로 만든다', 'reset 본문은 상태 변수 대입 하나입니다. 이후 요청에 late hook을 쓰도록 바꿀 뿐 기존 슬롯을 순회하지 않습니다.'),
        ('해제 시 전달해야 하는 size는?', '원래 요청 크기이다', '항상 페이지 크기로 반올림한 크기이다', '매핑 시 prev_size에는 정렬 전 size를 저장하고 해제에서 정확히 비교합니다. 실제 PTE 개수는 offset과 size로 다시 계산합니다.'),
        ('페이지 설치 루프가 idx를 감소시키는 이유는?', 'fixmap에서 인덱스 감소가 가상 주소 증가에 대응하기 때문이다', '물리주소도 감소시키기 때문이다', '물리주소는 PAGE_SIZE씩 증가합니다. __fix_to_virt는 TOP에서 인덱스의 페이지 값을 빼므로 idx 감소가 연속 증가 주소를 만듭니다.'),
        ('크기 초과로 매핑이 실패하면 prev_size 갱신 때문에 슬롯이 영구 점유되는가?', '아니다. 점유 판단은 아직 NULL인 prev_map이다', '그렇다. prev_size가0이 아니면 점유다', '빈 슬롯 검색은 !prev_map[i]만 검사합니다. prev_size의 남은 값과 실제 점유 상태를 구분해야 합니다.'),
        ('chunk 용량8192, offset100, 남은9000이면 첫 복사 길이는?', '8092바이트이다', '8192바이트이다', '매핑에는 선행 offset100도 포함돼야 하므로 복사 길이는8192-100=8092입니다. 매핑 길이는8092+100입니다.'),
        ('copy_from_early_mem이 매핑 실패를 검사하는가?', '아니다. NULL 검사 없이 memcpy를 호출한다', '그렇다. 실패하면 오류 코드를 반환한다', '본문은 매핑,복사,해제 순서이고 반환형은void입니다. 사용 가능한 부팅 자원과 유효한 입력이라는 호출 조건이 중요합니다.'),
        ('비MMU early_memremap_ro는 하드웨어 읽기 전용 PTE를 설치하는가?', '아니다. 물리주소를 포인터로 반환한다', '그렇다. 항상 RO PTE를 만든다', '해당 분기에 페이지 테이블 설정은 없고 size도 사용하지 않습니다. 이름만으로 구현에 없는 보호를 부여하면 안 됩니다.')
    ]
), dict(
    path='include/asm-generic/early_ioremap.h',
    title='초기 매핑 헤더 전체: 주소공간 타입과 초기화 계약',
    intro='초기 I/O·메모리 매핑 선언과 구성별 초기화 API 제공 여부를 읽습니다.',
    principle='선언이 보이는 것과 해당 구성에서 구현이 제공되는 것은 별개이며 타입 주석과 부팅 단계 계약을 함께 확인해야 합니다.',
    use='mm/early_ioremap.c의 구성별 구현과 이 공통 헤더를 대조합니다.',
    area='C 인터페이스 · 주소공간 타입 · 초기화 단계 · 조건부 컴파일',
    sections=[
        ('파일 전체 구성', 'GPL-2.0·guard·linux/types.h 포함 뒤 임시 초기 매핑 설명, 매핑·해제 extern 선언, 구성별 초기화와 복사 선언 또는 빈 초기화 helper를 제공합니다. 실제 슬롯 배열이나 페이지 테이블 변경은 없습니다.'),
        ('매핑과 해제 타입', 'early_ioremap은 resource_size_t 물리주소와 unsigned long 크기를 받아 void __iomem 포인터를 반환하고 iounmap도 해당 주석 포인터를 받습니다. memremap·ro·prot는 일반 void 포인터를 반환하며 prot에는 unsigned long prot_val이 추가됩니다. memunmap은 일반 포인터를 받습니다. __iomem 주석은 코드 검사를 돕는 주소공간 구분이며 그 자체로 CPU 명령을 실행하지 않습니다.'),
        ('선언과 구성', '위 매핑 선언들은 구성 조건 밖에 있습니다. 하지만 실제 mm 구현의 ro/prot는 별도 조건에 따라 존재하므로 extern 선언만으로 모든 구성에서 모든 함수를 링크할 수 있다고 추론하면 안 됩니다.'),
        ('초기화 분업', 'GENERIC_EARLY_IOREMAP과 MMU가 모두 있으면 arch-specific early_ioremap_init, 아키텍처 코드가 호출하는 generic setup, paging_init 마지막 단계에서 부르는 reset을 extern 선언합니다. reset의 주석은 이후 map/unmap 요청을 해당 단계에 맞춰 처리하기 위한 것이라고 설명합니다.'),
        ('복사와 비지원 분기', '같은 조건에서 copy_from_early_mem(dest,phys_addr_t src,size)을 선언합니다. 조건이 아니면 init/setup/reset 세 함수만 빈 inline으로 제공합니다. 복사 함수에 빈 대체 구현을 정의하는 분기는 없습니다. 비지원 초기화의 no-op과 데이터 복사 가능 여부는 다릅니다.'),
        ('CS 연결', '물리주소와 커널 가상주소, I/O와 일반 메모리 타입, 선언·정의·링크 가용성, 아키텍처 초기화와 공통 코드의 분업을 학습합니다. early라는 이름은 정규 ioremap이 아직 동작하지 않는 부팅 시기의 임시 사용이라는 주석과 연결됩니다.')
    ],
    questions=[
        ('GENERIC_EARLY_IOREMAP과 MMU 조건이 거짓일 때 빈 함수로 제공하는 것은?', 'init/setup/reset 세 함수이다', '모든 매핑과 복사 함수이다', '#else에는 세 초기화 함수만 있습니다. 매핑 선언이나 복사 기능을 모두 no-op으로 바꾸는 코드가 아닙니다.'),
        ('early_ioremap과 early_memremap 반환 타입의 차이는?', '전자는 __iomem 주소공간 주석이 있다', '전자는 정수 크기를 반환한다', '둘 다 포인터지만 I/O 접근 타입 주석을 구별합니다. 실제 매핑은 별도 구현의 역할입니다.'),
        ('prot 함수의 extern 선언이 항상 링크 가능한 구현을 보장하는가?', '아니다. 구현의 구성 조건도 확인해야 한다', '그렇다. 선언이 함수 본문을 자동 생성한다', 'mm 구현은 CONFIG_ARCH_USE_MEMREMAP_PROT 같은 조건을 사용합니다. C 선언과 정의의 존재는 별개입니다.')
    ]
)]
