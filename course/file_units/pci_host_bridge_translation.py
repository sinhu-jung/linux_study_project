"""Whole-file PCI host bridge lookup and window offset translation."""
ROWS = [dict(
    path='drivers/pci/host-bridge.c', title='PCI 호스트 브리지: 참조 획득과 자원 창 오프셋 변환',
    intro='루트 조회, 객체 수명 도우미, 해제 콜백 설정과 양방향 주소 변환을 전체 분석합니다.',
    principle='주소 변환은 해당 범위를 포함하는 첫 창의 오프셋을 적용하며, 창을 못 찾으면 이 구현은 항등 변환을 합니다.',
    use='부모 체인 순회, 구간 포함 관계, 선형 검색, 가역 변환의 전제와 참조 카운트를 학습합니다.',
    area='PCI · 메모리 주소 · 구간 알고리즘 · 참조 수명',
    sections=[
        ('루트 버스 조회', 'GPL-2.0 파일은 kernel,pci,module 및 내부 pci.h를 포함합니다. find_pci_root_bus는 parent가 있는 동안 부모로 올라가 최상단 버스를 반환합니다. 입력 NULL이나 부모 사이클을 검사하지 않으며 정상 트리를 전제로 합니다. 높이 H에서 O(H) 방문과 O(1) 추가 공간입니다. pci_find_host_bridge는 그 root_bus->bridge를 to_pci_host_bridge로 변환할 뿐 새 참조를 얻는 코드는 없습니다.'),
        ('객체 참조와 해제 콜백', 'pci_get_host_bridge_device는 장치 버스에서 루트를 찾아 bridge의 kobj에 kobject_get을 호출한 뒤 device 포인터를 반환합니다. pci_put_host_bridge_device는 같은 종류의 kobj에 kobject_put을 합니다. find 함수의 단순 포인터 조회와 get 함수의 수명 연장을 구분해야 합니다. pci_set_host_bridge_release는 release_fn과 release_data를 구조체 필드에 저장할 뿐 콜백을 즉시 실행하지 않습니다. 이전 데이터 해제나 잠금도 이 본문에는 없습니다.'),
        ('자원에서 버스 주소로', 'pcibios_resource_to_bus는 호스트 windows 목록을 순서대로 훑고 resource_contains(window->res,res)가 참인 첫 창의 offset을 선택합니다. 시작 offset은 0이며 못 찾으면 그대로입니다. 결과 region.start/end는 res.start/end에서 offset을 각각 뺀 값입니다. 이 함수 본문에는 별도 resource_type 비교가 없고 포함 판정 세부 사항은 resource_contains에 위임합니다. region 이외의 속성을 수정하거나 실패 코드를 반환하지 않습니다.'),
        ('버스 구간 포함 조건', '내부 region_contains는 바깥 start<=안쪽 start와 바깥 end>=안쪽 end를 모두 요구합니다. 일부만 겹치는 구간을 허용하는 교집합 검사가 아닙니다. 빈 구간이나 start>end의 유효성을 따로 검사하지 않으며 타입·플래그도 비교하지 않습니다. 같은 시작·끝의 동일 구간은 포함으로 판정됩니다.'),
        ('버스 주소에서 자원으로', 'pcibios_bus_to_resource는 출력 res의 현재 resource_type과 창의 타입이 다르면 건너뜁니다. 같은 타입의 창을 버스 좌표로 바꾸기 위해 start/end에서 그 창의 offset을 뺀 뒤 region_contains로 전체 입력 구간 포함을 확인합니다. 첫 일치 offset을 선택하고 res.start/end에 region.start/end+offset을 씁니다. 따라서 호출자는 res의 타입 정보를 미리 준비해야 하며 이 함수가 타입을 채우는 것은 아닙니다. 일치 창이 없으면 offset=0으로 주소를 그대로 씁니다.'),
        ('순서·복잡도와 산술 한계', '두 변환 모두 첫 일치에서 break하므로 겹치는 창의 선택은 목록 순서에 의존합니다. 루트 깊이 H와 창 수 W에 대해 본문의 검색 비용은 O(H+W)입니다. 두 끝점에 같은 오프셋을 적용해 범위 길이는 정상적인 비오버플로 산술에서 유지됩니다. 다만 덧셈·뺄셈 오버플로 검사, 복수 창을 잇는 구간 분할, 오류 보고는 없습니다. 같은 창이 양방향으로 선택된다는 전제 없이 모든 입력의 왕복 변환이 보장된다고 단정하면 안 됩니다.'),
        ('전체 검토 범위', '루트 helper, find/get/put, release setter, 두 주소 변환과 포함 helper까지 모든 여덟 함수를 대조했습니다. find_host_bridge와 release setter는 GPL export, 두 주소 변환은 일반 export입니다. 창 목록의 잠금은 이 두 함수 안에 보이지 않습니다. 실제 PCI 주소 접근, 장치 제거 중 동시 호출이나 커널 빌드는 실행하지 않았습니다.')
    ], questions=[
        ('자원 범위 0x1100..0x11ff에 offset=0x1000인 창을 선택하면 버스 범위는?', '0x100..0x1ff', '0x2100..0x21ff', 'resource_to_bus는 두 끝점에서 offset을 뺍니다. 반대 방향 함수에서 더하는 것과 방향을 구분해야 합니다.'),
        ('어느 창에도 전체 구간이 포함되지 않으면 변환 함수는 어떻게 하는가?', 'offset=0으로 주소를 그대로 기록한다', '항상 -EINVAL을 반환하고 출력을 건드리지 않는다', '두 함수는 void이며 offset의 초기값 0을 유지합니다. 실패를 반환하는 API라고 가정하면 실제 동작을 놓칩니다.'),
        ('bus_to_resource 호출 전 res의 flags는 무관한가?', '아니다. resource_type(res)를 창 타입과 비교한다', '그렇다. 함수가 모든 flags를 새로 채운다', '첫 필터에서 출력 resource의 기존 타입을 읽습니다. 본문 마지막에는 start/end만 쓰므로 타입 준비는 호출자의 전제입니다.'),
        ('find_host_bridge와 get_host_bridge_device가 같은 참조 수명 동작을 하는가?', '아니다. get 함수에는 kobject_get이 있고 find에는 없다', '그렇다. 둘 다 무조건 새 참조를 얻는다', '단순 검색 포인터와 수명을 연장하는 참조 획득을 구분해야 합니다. get으로 얻은 device는 대응하는 put 도우미로 내려놓습니다.'),
        ('[100,200]이 [150,250]을 region_contains로 포함하는가?', '아니다. 끝점 250이 바깥 끝점 200보다 크다', '그렇다. 일부라도 겹치면 포함이다', '포함은 두 부등식이 모두 참이어야 합니다. 겹침과 전체 포함은 다른 구간 관계입니다.'),
        ('서로 다른 offset의 두 창이 모두 포함 조건을 만족하면?', '목록에서 먼저 만난 창을 선택한다', '자동으로 두 offset의 평균을 낸다', '첫 일치에서 offset을 저장하고 break합니다. 우선순위 정렬이나 최소 창 선택 알고리즘은 이 파일에 없습니다.')
    ]
)]
