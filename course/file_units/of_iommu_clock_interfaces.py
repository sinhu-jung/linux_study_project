"""Whole-file OF IOMMU and clock helper contracts."""
ROWS = [dict(
    path='include/linux/of_iommu.h', title='OF IOMMU 헤더: 설정 오류와 예약 영역 목록의 계약',
    intro='두 IOMMU API의 활성 선언과 비활성 본문 전체를 분석합니다.',
    principle='출력 목록을 인수로 받는다는 사실은 그 목록을 초기화하거나 채운다는 보장이 아닙니다.',
    use='불완전 구조체 타입, 선택 ID 포인터, 연결 리스트 출력과 오류 코드를 학습합니다.',
    area='IOMMU · DMA · 연결 리스트 · 조건부 컴파일 · 인터페이스',
    sections=[
        ('헤더와 의존 타입', 'GPL-2.0과 __OF_IOMMU_H guard 아래 device, device_node, iommu_ops를 전방 선언합니다. 이 파일에는 include 지시문이 없습니다. u32와 ENODEV의 정의를 여기서 제공하지 않으며 list_head의 파일 범위 전방 선언도 없습니다. 따라서 다른 타입·매크로가 어떤 포함 순서에서 공급되는지 확인해야 합니다. iommu_ops는 전방 선언되지만 이 헤더의 두 함수 시그니처에는 사용되지 않습니다.'),
        ('설정 API', 'CONFIG_OF_IOMMU가 정의되면 of_iommu_configure는 device *dev, device_node *master_np, const u32 *id를 받고 int를 반환하는 외부 선언입니다. id는 u32 정수 값 자체가 아니라 그 값을 가리키는 포인터입니다. NULL 인수의 상세 의미나 장치 식별자 변환 규칙, probe 지연 처리는 이 선언만으로 확정할 수 없습니다. 실제 DMA 매핑을 수행하는 코드도 이 헤더에는 없습니다.'),
        ('예약 영역 목록 API', 'of_iommu_get_resv_regions는 device와 list_head 포인터를 받아 void를 반환합니다. 연결 리스트를 전달하는 형태지만 어떤 노드를 추가하는지, 노드의 소유권과 해제 책임이 누구에게 있는지는 실제 구현을 확인해야 합니다. 이 헤더에는 리스트 원소 구조체나 삽입 루프가 없습니다. 출력 인수의 타입과 자료구조를 조작하는 구현을 구분하는 사례입니다.'),
        ('비활성 경로와 전체 범위', 'CONFIG_OF_IOMMU가 없으면 configure는 입력을 검사하지 않고 -ENODEV를 반환합니다. get_resv_regions는 빈 본문이므로 list를 초기화하거나 비우거나 원소를 추가하지 않습니다. 이미 들어 있던 내용을 지우는 코드도 없습니다. guard, 세 전방 선언, 두 활성 선언과 두 inline stub 전체를 대조했으며 IOMMU 하드웨어 동작이나 구성별 컴파일을 실행하지 않았습니다.')
    ], questions=[
        ('OF_IOMMU 비활성 configure가 반환하는 값은?', '-ENODEV', '아무 설정 없이 항상 성공 0', '비활성 본문은 return -ENODEV입니다. 같은 OF 계열의 다른 configure stub이 0을 반환하더라도 이 함수의 계약에 적용하면 안 됩니다.'),
        ('비활성 get_resv_regions는 전달받은 연결 리스트를 빈 목록으로 초기화하는가?', '아니다. 빈 본문이라 목록에 쓰지 않는다', '그렇다. 항상 INIT_LIST_HEAD를 호출한다', '본문에 리스트 조작이 없습니다. 호출자는 이 호출이 목록 초기화를 대신했다고 가정할 수 없습니다.'),
        ('이 헤더에서 const u32 *id는 u32 값 자체와 같은가?', '아니다. u32를 가리키는 포인터 인수다', '그렇다. 항상 장치 번호 0을 뜻한다', '포인터와 값은 전달 방식과 NULL 표현 가능성에서 다릅니다. NULL의 구체적인 처리까지 알려면 외부 구현을 확인해야 합니다.')
    ]
), dict(
    path='include/linux/of_clk.h', title='OF 클록 헤더: 부모 개수·이름 조회와 초기화 조건',
    intro='클록 도우미 세 API와 두 CONFIG의 논리곱 조건을 전체 대조합니다.',
    principle='부모의 개수, 특정 부모의 이름, 공급자 초기화는 서로 다른 결과를 갖는 API입니다.',
    use='의존 기능의 논리곱, 문자열 포인터의 소유권, 무동작 초기화와 조회 실패를 학습합니다.',
    area='클록 · 장치 트리 · 조건부 컴파일 · 문자열 포인터',
    sections=[
        ('파일 구성과 활성 조건', 'GPL-2.0, OF clock helpers 주석과 __LINUX_OF_CLK_H guard 아래 device_node와 of_device_id를 전방 선언합니다. include 지시문은 없습니다. 활성 조건은 defined(CONFIG_COMMON_CLK) && defined(CONFIG_OF)로 두 이름이 모두 정의되어야 합니다. 둘 중 하나라도 없으면 세 API가 비활성 inline으로 바뀝니다.'),
        ('부모 조회 두 API', 'of_clk_get_parent_count는 const device_node *np에서 unsigned int를 반환합니다. of_clk_get_parent_name은 같은 노드와 int index에서 const char *를 반환합니다. 개수는 문자열 목록 자체가 아니고, 이름 포인터가 const라는 사실만으로 동적 할당 여부나 참조 수명 규칙을 알 수는 없습니다. 인덱스 범위 검사와 이름 선택 방식도 이 헤더에는 구현되어 있지 않습니다.'),
        ('초기화 API와 매칭 테이블', 'of_clk_init은 const of_device_id *matches를 받는 void 함수입니다. 활성 경로는 선언만 제공하므로 여기서 매칭 테이블을 순회하거나 클록을 등록하는 코드는 보이지 않습니다. 표의 종료 조건이나 등록 순서, 부모 준비 여부에 따른 알고리즘은 외부 구현의 검토 대상입니다.'),
        ('비지원 반환값과 전체 범위', '비활성 parent_count는 0, parent_name은 NULL을 반환하고 init은 빈 함수입니다. 세 본문은 노드나 index나 matches를 읽지 않습니다. 0과 NULL은 서로 다른 타입의 조회 결과이며 빈 init 호출로 클록 공급자가 실제 등록되었다고 주장할 수 없습니다. 주석과 guard, 전방 선언, 세 활성 선언·대체 본문 모두를 대조했으며 클록 하드웨어와 구성별 커널 빌드는 실행하지 않았습니다.')
    ], questions=[
        ('COMMON_CLK만 정의되고 OF가 없으면 어느 분기를 사용하는가?', '비활성 inline 세 함수를 사용한다', 'COMMON_CLK 하나만으로 활성 외부 선언을 사용한다', '조건은 논리합이 아니라 논리곱입니다. 두 defined 조건을 모두 만족해야 활성 선언 블록으로 들어갑니다.'),
        ('비활성 부모 개수·부모 이름 조회의 결과는?', '각각 0과 NULL', '각각 -ENODEV와 빈 문자열 버퍼', 'count는 unsigned int 0이고 name은 NULL 포인터입니다. 길이 0의 유효 문자열을 생성하거나 반환하는 코드는 없습니다.'),
        ('const char * 반환 선언만으로 호출자가 이름 메모리를 해제해야 한다고 결론 내릴 수 있는가?', '없다. 소유권과 수명 계약은 별도로 확인해야 한다', '있다. const 포인터는 항상 호출자가 free해야 한다', 'const는 이 포인터를 통한 문자 변경의 타입 제약입니다. 할당 주체와 해제 책임을 지정하는 소유권 표기가 아닙니다.')
    ]
)]
