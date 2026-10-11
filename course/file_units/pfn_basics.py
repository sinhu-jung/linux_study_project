"""Whole common PFN wrapper and address conversion macros."""
ROWS = [dict(
    path='include/linux/pfn.h',
    title='PFN 헤더 전체: 페이지 번호와 주소의 단위 변환',
    intro='페이지 프레임 번호의 타입과 주소 정렬·올림·내림 매크로를 계산 예제로 해설합니다.',
    principle='주소와 페이지 번호는 단위가 다르며 정렬로 잃은 페이지 내부 offset은 역변환으로 복구되지 않습니다.',
    use='io_mapping의 PHYS_PFN 호출과 캐시 flush의 페이지 단위 범위를 읽는 기초로 사용합니다.',
    area='페이지 주소 · 비트 마스크 · 정수 올림 · 타입 폭 · PFN metadata',
    sections=[
        ('파일 구성', 'GPL-2.0·guard 뒤 비어셈블리 분기에 types.h와 pfn_t 정의를 둡니다. 그 밖에 다섯 변환 매크로가 있으며 함수 본문이나 페이지 할당·매핑 코드는 없습니다. PAGE_SIZE/PAGE_SHIFT/PAGE_MASK의 정의는 포함 문맥에 의존합니다.'),
        ('Pfn_t의 표현', 'pfn_t는 u64 val 한 필드를 가진 구조체 typedef입니다. 주석은 PFN이 선택적으로 memmap의 struct page에 대응하며 상위 비트의 flag로 그 여부를 나타낸다고 설명합니다. 구체적인 flag mask와 접근 helper는 이 파일에 없습니다. val 전체를 flag 제거 없이 물리주소로 이동하는 방법을 이 선언만으로 추론하면 안 됩니다.'),
        ('주소 올림 정렬', 'PFN_ALIGN은 x를 unsigned long으로 변환하고 PAGE_SIZE-1을 더한 뒤 PAGE_MASK와 AND합니다. 반환은 PFN 번호가 아니라 페이지 정렬된 주소 값입니다. 이미 정렬돼 있으면 유지되고 아닌 주소는 다음 경계로 올라갑니다. cast와 덧셈 폭을 고려해야 하며 overflow 검사는 없습니다.'),
        ('번호 올림과 내림', 'PFN_UP은 (x+PAGE_SIZE-1)>>PAGE_SHIFT로 byte 양을 페이지 단위로 올림합니다. PFN_DOWN은 x>>PAGE_SHIFT로 내림합니다. 물리 범위의 전체 포함 페이지를 구할지 완전히 들어가는 페이지를 구할지에 따라 시작·끝에 적용하는 올림 방향이 달라집니다. 이 매크로 자체가 어느 범위 정책을 선택하지는 않습니다.'),
        ('물리주소와 PFN', 'PFN_PHYS는 x를 phys_addr_t로 먼저 바꾼 뒤 PAGE_SHIFT만큼 왼쪽 이동합니다. PHYS_PFN은 입력을 오른쪽 이동한 뒤 unsigned long으로 변환합니다. 형변환의 시점과 최종 폭이 다르며 좁은 unsigned long에서 큰 PFN이 손실되지 않는다고 무조건 보장할 수 없습니다.'),
        ('4KiB 계산 예제', 'PAGE_SIZE4096,PAGE_SHIFT12에서 x=0x12345이면 PFN_ALIGN=0x13000,PFN_UP=0x13,PFN_DOWN=0x12,PHYS_PFN=0x12입니다. PFN_PHYS(0x12)=0x12000이므로 원래 offset0x345는 복원되지 않습니다. x=0x12000이면 UP과DOWN이 모두0x12입니다.'),
        ('검사 범위와 부호', '입력 주소의 유효성,PFN의 RAM 존재 여부,struct page 존재,정렬 산술 overflow를 검사하지 않습니다. PFN_UP/DOWN은 별도 unsigned cast 없이 입력 식을 사용하므로 부호와 정수 승격을 고려해야 하며 음수 주소를 정규화하는 API가 아닙니다. pfn_t 구조체와 단순 정수 PFN을 구분해야 합니다.'),
        ('CS 연결과 범위', '단위 분석,2의 거듭제곱 정렬,정수 나눗셈의 floor/ceil,정보 손실,형변환 위치,상위 비트 metadata를 학습합니다. 이 산술 변환은 MMU PTE 설치나 메모리 접근 권한 부여를 수행하지 않습니다.')
    ],
    questions=[
        ('4KiB 페이지에서 PFN_ALIGN(0x12345)는?', '0x13000이다', '0x13이다', 'ALIGN은 정렬된 주소를 반환합니다. 페이지 번호0x13은 PFN_UP의 결과입니다.'),
        ('PHYS_PFN으로 바꾼 뒤 PFN_PHYS하면 페이지 내부 offset도 돌아오는가?', '아니다.페이지 시작 주소만 얻는다', '그렇다.원래 주소가 항상 완전히 복원된다', '오른쪽 이동에서 낮은 PAGE_SHIFT 비트를 버립니다.0x12345는0x12를 거쳐0x12000이 됩니다.'),
        ('pfn_t에 struct page 포인터가 직접 들어 있는가?', '아니다.u64 val 필드 하나이며 backing 여부는 flag로 표현한다', '그렇다.모든 pfn_t는 포인터 두 개이다', '이 파일의 구조체는u64 val 하나입니다. 주석의 memmap backing과 실제 필드 타입을 구분합니다.'),
        ('PFN_PHYS가 실제 페이지를 할당하거나 PTE를 설치하는가?', '아니다.타입 변환과 비트 이동만 한다', '그렇다.호출하면 자동으로 매핑된다', '물리주소 계산과 자원 할당·주소 매핑은 별도 단계입니다. 유효성 검사도 이 매크로에 없습니다.')
    ]
)]
