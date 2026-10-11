"""Whole-file OF platform declarations and auxiliary match table."""
ROWS = [dict(
    path='include/linux/of_platform.h', title='OF 플랫폼 인터페이스: auxdata와 구성별 장치 생성 계약',
    intro='이름·platform_data 보조 테이블,장치 수명 API와 모든 조건부 stub을 분석합니다.',
    principle='장치 트리 기술과 Linux 내부 장치 이름을 연결하는 보조 정보는 일반적인 속성 조회와 구분됩니다.',
    use='sentinel 배열,지정 초기화,장치 생성과 등록의 분리,조건부 API를 학습합니다.',
    area='장치 트리 · 플랫폼 버스 · 테이블 · 자원 수명 · 구성',
    sections=[
        ('헤더와 자료구조', 'GPL-2.0+ guard 안에서 mod_devicetable.h를 포함하고 device,device_node,of_device_id,platform_device를 전방 선언합니다. of_dev_auxdata는 char *compatible,resource_size_t phys_addr,char *name,void *platform_data로 이루어집니다. 노드 매칭에 쓸 compatible과 레지스터 시작 주소,매칭 뒤 부여할 이름과 데이터 포인터를 분리한 구조입니다.'),
        ('Auxdata 문서 계약', '문서는 of_platform_populate 호출자가 장치 이름을 바꾸고 platform_data를 설정할 수 있다고 설명하며 테이블은 빈 항목으로 끝내라고 요구합니다. 일부 Linux 기반 구조가 장치 이름으로 대상을 찾지만 그런 이름은 DT에 기록되지 않는 상황을 연결합니다. DT 전환 시 최후 수단으로 고려하고 보통 드라이버는 익명 platform_data보다 노드에서 데이터를 얻으라는 지침도 있습니다.'),
        ('초기화 매크로와 기본 테이블', 'OF_DEV_AUXDATA는 네 인수를 구조체의 네 필드에 designated initializer로 넣는 매크로입니다. 메모리를 할당하거나 문자열을 복제하지 않습니다. of_default_bus_match_table은 const of_device_id 배열의 extern 선언이며 실제 항목들은 여기서 정의하지 않습니다.'),
        ('장치 수명 기본 API', 'of_device_alloc은 node,bus_id,parent를 받아 platform_device *를 반환합니다. add와 register는 int,unregister는 void입니다. 이 네 선언과 of_platform_bus_probe의 root,matches,parent 선언은 여기서 CONFIG_OF_ADDRESS 분기 밖에 있습니다. 선언만으로 alloc·add·register의 세부 호출 관계나 실패 회수를 동일하게 취급하면 안 됩니다.'),
        ('노드로 장치 찾기', 'of_find_device_by_node는 CONFIG_OF일 때 외부 선언이고 비활성일 때 NULL 반환 stub입니다. 이 분기는 아래의 CONFIG_OF_ADDRESS와 다릅니다. 검색 API의 활성 여부와 플랫폼 장치 생성 helper의 활성 조건을 하나로 합쳐 설명할 수 없습니다.'),
        ('주소 지원 구성의 생성·구성', 'CONFIG_OF_ADDRESS이면 create와 destroy를 선언합니다. create는 node,bus_id,parent, destroy는 device와 void *data를 받습니다. populate는 root,matches,auxdata lookup,parent를 받고 default_populate는 matches 인수 없이 나머지를 받습니다. depopulate는 parent를 받는 void 함수입니다. 헤더에는 실제 재귀 생성이나 순회 본문이 없습니다.'),
        ('Managed API와 비지원 반환', 'devm_of_platform_populate와 depopulate는 device를 받으며 각각 int,void입니다. 주소 지원 비활성 stub에서 create는 NULL,destroy·populate·default_populate·devm_populate는 -ENODEV입니다. 두 depopulate는 빈 함수입니다. 비지원 시 모두 성공하는 no-op이라고 일반화하면 안 됩니다.'),
        ('전체 범위와 한계', '구조체와 문서,초기화 매크로,기본 테이블,기본 수명 선언,검색 분기,주소 지원 분기와 대체 함수 전체를 확인했습니다. auxdata 포인터의 저장소 수명과 활성 구현의 참조 소유권은 호출부·구현에서 확인해야 합니다. 실제 플랫폼 장치 생성이나 구성별 컴파일 실험은 실행하지 않았습니다.')
    ], questions=[
        ('Auxdata 테이블의 종료 표시는?', '빈 항목', '반드시 별도 전역 길이 변수', '문서가 empty entry 종료를 명시합니다. 테이블 레이아웃과 이를 사용하는 순회 계약을 연결합니다.'),
        ('OF_DEV_AUXDATA가 이름 문자열을 복제하는가?', '아니다. 필드 초기화 표현식만 만든다', '그렇다. 내부에서 항상 kstrdup한다', '매크로에는 지정 초기화만 있습니다. 포인터 값 저장과 저장소 소유권 이전은 다릅니다.'),
        ('노드 검색과 플랫폼 생성의 조건부 설정은 동일한가?', '아니다. 검색은 OF,생성 helper는 OF_ADDRESS 분기다', '그렇다. 둘 다 KUNIT 설정만 본다', '각 #ifdef를 따로 읽어야 합니다. 상위 Kconfig 관계와 이 헤더의 직접 분기도 구분합니다.'),
        ('OF_ADDRESS 비활성일 때 populate와 depopulate는?', 'populate는 -ENODEV,depopulate는 빈 동작이다', '둘 다 성공적으로 장치를 생성한다', '작업을 수행하지 않는 것과 성공을 반환하는 것은 같지 않습니다. int와 void API의 stub이 다릅니다.')
    ]
)]
