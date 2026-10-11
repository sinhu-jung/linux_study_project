"""Whole-file PCI bus/device search and DMA alias iteration."""
ROWS = [dict(
    path='drivers/pci/search.c', title='PCI 검색: DFS·참조를 넘기는 반복·DMA alias',
    intro='버스·장치 검색과 ID wrapper, 존재 확인 및 DMA alias 순회 전체를 분석합니다.',
    principle='검색 결과의 존재와 객체 수명 보장은 다르며 다음 검색이 이전 참조를 소비하는 계약도 있습니다.',
    use='깊이 우선 검색, 비트맵 순회, 마스크 매칭, 참조 카운트와 관측값의 유효기간을 학습합니다.',
    area='PCI · 탐색 알고리즘 · 트리 · 비트맵 · 참조 수명',
    sections=[
        ('파일 구성과 공용 잠금', 'GPL-2.0 파일은 PCI,slab,module,interrupt와 내부 pci.h를 포함하고 DECLARE_RWSEM(pci_bus_sem)으로 읽기·쓰기 세마포어를 정의합니다. 이 잠금이 파일 전체의 모든 함수를 자동 보호하지는 않습니다. find_next_bus와 get_slot의 명시적 잠금 구간, 다른 검색의 버스 코어 호출을 각각 구분해야 합니다.'),
        ('DMA alias의 시작과 비트맵', 'pci_for_each_dma_alias는 입력 pdev를 pci_real_dma_dev로 바꾼 뒤 실제 장치 ID를 첫 콜백 인수로 전달합니다. 콜백의 int 결과가 0이 아니면 즉시 그 값을 반환하므로 음수뿐 아니라 양수도 중단입니다. dma_alias_mask가 있으면 MAX_NR_DEVFNS 범위의 설정 비트를 순회하고 같은 버스 번호와 해당 devfn을 합친 ID로 콜백을 호출합니다. 이 경로는 같은 ID가 다시 나오는 것을 따로 제거하지 않습니다.'),
        ('상위 브리지 alias 분기', '루트 버스 전까지 bus->parent로 올라가며 self 없는 가상 버스는 건너뜁니다. BRIDGE_XLATE_ROOT 플래그 브리지에서는 그 브리지를 콜백에 전달하기 전에 종료합니다. PCIe ROOT_PORT,UPSTREAM,DOWNSTREAM은 건너뛰고 PCI_BRIDGE는 subordinate 버스의 0:0 ID, PCIE_BRIDGE는 브리지 자체 ID를 전달합니다. 비PCIe 브리지는 PCIE_BRIDGE_ALIAS 플래그가 있으면 subordinate 0:0, 아니면 자체 ID입니다. PCIe switch에 명시되지 않은 타입에는 default 콜백이 없습니다. 모든 경로에서 첫 0 아닌 콜백 결과가 전파됩니다.'),
        ('버스의 선행 깊이 우선 검색', 'pci_do_find_bus는 현재 bus 번호가 같으면 먼저 반환하고 그렇지 않으면 children 목록을 재귀 검색해 첫 결과를 반환합니다. 전체 실패는 NULL입니다. 정상 트리에서 최악의 방문은 버스 수 B에 대해 O(B), 호출 스택은 높이 H에 대해 O(H)입니다. 인수 busnr는 unsigned char인데 외부 pci_find_bus의 busnr는 int이므로 내부 호출에서 타입 폭이 줄어듭니다. 이 함수들에는 정수 범위 검증이 없습니다.'),
        ('도메인과 루트 목록', 'pci_find_bus는 pci_find_next_bus로 루트를 하나씩 얻어 도메인이 같은 루트만 재귀 검색합니다. find_next_bus는 읽기 잠금 아래 from->node.next 또는 pci_root_buses.next를 선택하고 sentinel이 아니면 list_entry로 반환합니다. 문서의 알려진 PCI 버스 순회 표현과 달리 이 helper가 직접 순회하는 목록은 root_buses이며 하위 버스는 별도 DFS가 담당합니다. 반환 버스에 참조를 증가시키는 코드가 없고 읽기 잠금도 반환 전에 해제됩니다. 전체 DFS가 이 잠금 안에서 실행되는 것은 아닙니다.'),
        ('슬롯과 전체 주소 검색', 'pci_get_slot은 bus->devices를 읽기 잠금 아래 선형 검색해 devfn이 같은 장치를 고릅니다. 찾지 못하면 NULL로 만들며 공통 끝에서 pci_dev_get 후 잠금을 풉니다. 성공 참조는 호출자가 pci_dev_put해야 합니다. get_domain_bus_and_slot은 for_each_pci_dev로 전체 장치를 순회해 domain,bus number,devfn을 모두 비교합니다. 일치 시 반환된 장치 참조를 호출자가 해제해야 한다는 계약이 문서에 있습니다. 슬롯 번호만 맞는 장치를 반환하는 함수가 아닙니다.'),
        ('ID 매칭과 이전 참조 소비', 'match_pci_dev_by_id는 일반 device를 PCI 장치로 바꾸고 pci_match_one_device의 결과를 1 또는 0으로 돌려줍니다. pci_get_dev_by_id는 from이 있으면 &from->dev를 검색 시작점으로 bus_find_device에 전달합니다. 결과가 있으면 PCI 포인터로 바꾸고 성공 여부와 무관하게 pci_dev_put(from)을 호출한 뒤 반환합니다. 따라서 이전 항목을 다음 검색에 넘긴 뒤 다시 무조건 put하면 이 계약과 충돌할 수 있습니다. 조기 종료로 다음 검색을 하지 않으면 현재 보유 참조는 직접 해제해야 합니다.'),
        ('vendor와 subsystem wrapper', 'pci_get_subsys는 vendor,device,subvendor,subdevice를 지정한 지역 pci_device_id를 만들어 공통 검색에 넘깁니다. 나머지 필드는 지정 초기화의 규칙으로 0입니다. pci_get_device는 subsystem 두 값을 PCI_ANY_ID로 지정해 subsys wrapper를 호출합니다. 필터를 담은 구조체와 공통 검색 알고리즘을 분리한 형태이며 검색 때 이 지역 구조체를 별도로 heap 할당하지 않습니다.'),
        ('전체 class와 base class', 'pci_get_class는 네 ID를 ANY로, class_mask를 PCI_ANY_ID로, class를 입력값으로 설정합니다. pci_get_base_class는 네 ID는 ANY지만 class_mask=0xFF0000,class=입력<<16입니다. base class만 고르는 경우 subclass와 programming interface까지 같은지 요구하는 전체 class 검색과 결과 범위가 다릅니다. 두 함수 모두 이전 from 참조를 소비하는 공통 helper를 사용합니다.'),
        ('존재 확인과 종료 sentinel', 'pci_dev_present는 ids->vendor || ids->subvendor || ids->class_mask가 참인 동안 각 항목을 처음부터 검색합니다. device나 subdevice만 0 아닌 항목은 이 종료 조건을 통과시키지 않습니다. 찾으면 참조를 put하고 1, 끝까지 없으면 0입니다. 호출자에게 장치 참조가 전달되지 않으므로 반환 직후 제거가 일어나면 존재 관측은 오래된 정보가 됩니다. ID 수 M,장치 수 N일 때 반복 검색의 최악 방문 비용은 O(MN) 형태가 될 수 있습니다.'),
        ('전체 범위와 한계', 'DMA alias 순회, 재귀 버스 검색, 루트 순회, 슬롯·도메인 검색, 매칭 callback과 공통 ID helper, 네 ID/class wrapper, 존재 확인까지 모든 본문을 대조했습니다. find_bus/find_next_bus/get_slot/domain_bus_and_slot/subsys/device/class/base_class/dev_present에는 일반 EXPORT_SYMBOL이 있습니다. 실제 hotplug 동시 실행, DMA requester ID 전달 또는 커널 빌드는 검증하지 않았습니다.')
    ], questions=[
        ('pci_get_dev_by_id의 다음 검색이 실패하면 from 참조는 유지되는가?', '아니다. 실패해도 pci_dev_put(from)을 호출한다', '그렇다. 성공할 때만 이전 항목을 해제한다', 'put은 bus_find_device 결과 검사 뒤 공통 경로에 있습니다. NULL 결과가 이전 참조를 계속 보유한다는 뜻은 아닙니다.'),
        ('pci_find_next_bus 하나만 반복하면 모든 하위 버스도 직접 나오는가?', '아니다. 이 함수의 목록은 pci_root_buses다', '그렇다. 내부에서 children을 재귀 순회한다', '하위 버스 재귀는 pci_do_find_bus에 있습니다. 루트 목록 이동과 깊이 우선 검색을 별개의 알고리즘으로 읽어야 합니다.'),
        ('pci_dev_present가 1이면 반환 이후 장치 수명이 보장되는가?', '아니다. 찾은 참조를 내려놓고 불리언만 반환한다', '그렇다. 호출자에게 숨겨진 영구 참조를 남긴다', 'found에 pci_dev_put을 한 다음 1을 반환합니다. 존재 확인은 특정 시점의 관측이며 실제 장치 사용을 위한 참조 획득을 대신하지 않습니다.'),
        ('base class 0x02 검색의 class와 mask는?', '0x020000과 0xFF0000', '0x02와 0x0000FF', '입력 class를 16비트 왼쪽 이동해 상위 class 바이트에 놓습니다. 하위 subclass와 interface 비트는 mask에서 제외합니다.'),
        ('DMA alias 콜백이 양수 1을 반환하면 계속하는가?', '아니다. 즉시 1로 종료한다', '그렇다. 음수 오류일 때만 중단한다', '조건은 if(ret)입니다. 이 인터페이스의 중단 규칙은 0 아닌 값 전체이므로 일반 errno 전파만으로 좁혀 읽으면 안 됩니다.'),
        ('BRIDGE_XLATE_ROOT가 설정된 브리지는 alias 콜백을 호출한 뒤 멈추는가?', '아니다. 해당 브리지 콜백 분기 전에 반환한다', '그렇다. 브리지의 alias를 반드시 한 번 추가한다', '플래그 검사가 PCIe 타입 분기보다 먼저 나옵니다. 탐색 경계 자체를 결과에 포함하는지 순서를 확인해야 합니다.'),
        ('vendor=0,subvendor=0,class_mask=0이고 device만 1인 ID 항목을 present가 검색하는가?', '아니다. while 종료 조건이 거짓이다', '그렇다. 구조체의 아무 필드나 0 아니면 계속한다', '실제 sentinel 판정은 세 필드의 OR입니다. null-terminated라는 문구를 구조체 모든 필드 검사로 확대해서는 안 됩니다.'),
        ('pci_find_bus의 DFS 전체가 pci_bus_sem 읽기 잠금 아래 있는가?', '아니다. find_next_bus의 잠금은 반환 전에 풀린다', '그렇다. 모든 재귀 호출까지 잠금을 유지한다', '명시적 잠금 구간은 루트 다음 항목을 얻는 helper 안에 있습니다. 전체 순회의 동시성 보장은 호출 문맥까지 확인해야 하며 이 본문만으로 전역 잠금 보호를 주장할 수 없습니다.')
    ]
)]
