"""Whole-file PCI stop/remove traversal and resource lifetimes."""
ROWS = [dict(
    path='drivers/pci/remove.c', title='PCI 제거: 두 단계 후위 순회와 SR-IOV 역순 정리',
    intro='장치·버스·호스트 브리지의 중지와 제거 함수 전체를 분석합니다.',
    principle='자식부터 정리하는 순서뿐 아니라 중지와 객체 제거를 나누는 단계도 자원 수명의 일부입니다.',
    use='트리 후위 순회, 안전한 연결 리스트 반복, 참조 카운트와 잠금 범위를 학습합니다.',
    area='PCI · 자료구조 · 트리 · 연결 리스트 · 자원 수명 · 동시성',
    sections=[
        ('파일 구성과 자원 해제', 'GPL-2.0 파일은 PCI,module,OF,OF platform,platform device와 내부 pci.h를 포함합니다. pci_free_resources는 장치의 모든 resource를 순회하면서 parent가 있는 것만 release_resource합니다. 이 본문에는 resource 구조체 자체의 kfree가 없습니다. 자원 트리에서 예약을 해제하는 것과 자료구조 메모리를 해제하는 것을 구분해야 합니다.'),
        ('플랫폼 전원 제어 장치 정리', 'pci_pwrctl_unregister 콜백은 data를 PCI 노드로 보고 현재 device의 OF 노드를 얻습니다. 플랫폼 장치이면서 노드가 존재하고 같은 포인터일 때 of_device_unregister 후 OF_POPULATED 플래그를 지웁니다. 항상 0을 반환하므로 특정 일치 항목을 처리했다고 전체 탐색 중단을 요청하지 않습니다. 이름이나 compatible 문자열 비교가 아니라 노드 포인터 동일성 비교입니다.'),
        ('장치 중지 단계', 'pci_stop_dev는 added 여부와 무관하게 먼저 pci_pme_active(dev,false)를 호출합니다. added 장치이면 dev->dev.parent의 자식들을 대상으로 같은 OF 노드의 플랫폼 장치를 정리하고, device_release_driver, proc 분리, sysfs 파일 제거, 동적 OF 노드 제거 순서로 진행합니다. 마지막에 added 상태를 false로 설정합니다. 이 단계에서 bus_list를 제거하거나 마지막 device 참조를 put하는 것은 아닙니다.'),
        ('장치 객체 제거 단계', 'pci_destroy_dev는 dev->dev.kobj.parent가 없으면 즉시 반환합니다. 나머지는 NPEM 제거, device_del, pci_bus_sem 쓰기 잠금 아래 bus_list 삭제, DOE 제거, ASPM 링크 상태 종료, bridge D3 갱신, resource 해제, put_device 순서입니다. pci_bus_sem은 목록 삭제 구간만 감싸며 함수 전체를 감싸지 않습니다. put_device는 참조를 내려놓는 동작이므로 다른 참조가 있더라도 즉시 모든 메모리가 사라진다고 설명해서는 안 됩니다.'),
        ('버스 제거', 'pci_remove_bus는 proc 분리 후 pci_bus_sem 쓰기 잠금 안에서 bus->node를 삭제하고 버스 번호 자원을 해제합니다. 잠금을 푼 뒤 legacy 파일을 제거하고 bus->ops->remove_bus가 있으면 호출합니다. 그다음 pcibios_remove_bus와 device_unregister입니다. 이 함수 자체는 bus->devices를 순회해 자식 장치를 먼저 없애지 않으므로 상위 제거 경로의 순서가 중요합니다.'),
        ('중지의 역순 후위 순회', 'pci_stop_bus_device는 subordinate 버스가 있으면 devices를 list_for_each_entry_safe_reverse로 순회해 각 자식을 재귀 중지한 뒤 현재 장치를 중지합니다. 주석은 SR-IOV PF를 중지하면 관련 VF 제거로 목록이 바뀔 수 있어 VF를 먼저, PF를 나중에 처리하도록 역순을 사용한다고 설명합니다. safe 반복자만 있다는 사실이 순서 의존성을 없애지는 않습니다. 재귀는 자식 우선의 후위 순회입니다.'),
        ('제거의 정방향 후위 순회', 'pci_remove_bus_device는 subordinate 자식을 list_for_each_entry_safe로 정방향 재귀 제거합니다. 그 후 subordinate 버스를 제거하고 dev->subordinate=NULL로 바꾼 뒤 현재 장치를 destroy합니다. 정상 트리의 장치 수 N과 높이 H라면 순회 자체는 O(N), 재귀 스택은 O(H)이고 실제 시간에는 드라이버와 하위 정리 함수 비용이 더해집니다. 역순 중지와 정방향 제거의 두 목록 순서를 혼동하면 안 됩니다.'),
        ('전체 중지 뒤 전체 제거', 'pci_stop_and_remove_bus_device는 먼저 pci_stop_bus_device 전체 호출을 마치고 pci_remove_bus_device를 호출합니다. 각 장치를 중지하자마자 그 객체를 제거하며 한 번만 순회하는 구조가 아닙니다. locked wrapper는 pci_lock_rescan_remove와 unlock 사이에서 이 두 단계 전체를 호출합니다. 기본 함수 안에 이 rescan/remove 잠금을 자동으로 취득하는 코드는 없습니다.'),
        ('루트 버스 중지', 'pci_stop_root_bus는 root가 아니면 반환합니다. host bridge를 구해 루트의 자식들을 safe_reverse로 중지하고 마지막에 호스트 브리지의 드라이버를 release합니다. 루트 버스나 호스트 객체 자체의 device_del을 여기서 호출하지 않습니다. 루트 중지와 제거는 별도 API로 드러납니다.'),
        ('루트 제거와 도메인 번호', 'pci_remove_root_bus도 root가 아니면 반환합니다. 자식들을 safe 정방향으로 제거하고 PCI_DOMAINS_GENERIC일 때 host_bridge->domain_nr가 PCI_DOMAIN_NR_NOT_SET인 경우만 동적으로 할당된 bus->domain_nr를 반환합니다. 이어 pci_remove_bus, host_bridge->bus=NULL, host bridge device_del 순서입니다. 이 함수에 stop_root_bus 호출이나 host bridge put_device 호출은 없습니다. 호출 계층의 중지·참조 관리와 이 본문의 역할을 구분해야 합니다.'),
        ('전체 범위와 한계', '세 내부 자원·플랫폼·중지 도우미, 장치 destroy, bus 제거, 두 재귀 함수, 두 장치 제거 진입점, 두 루트 함수 전체를 대조했습니다. remove_bus와 일반 stop_and_remove는 일반 export, locked wrapper와 두 root API는 GPL export입니다. 실제 hotplug, SR-IOV VF 제거, 드라이버 종료 또는 동시성 실행은 검증하지 않았습니다.')
    ], questions=[
        ('중지 순회에서 safe_reverse가 필요한 이유는?', 'PF 중지가 VF를 제거해 목록을 바꾸므로 VF를 먼저 처리하기 위해서다', '역순이면 어떤 동시 접근에도 잠금 없이 안전하기 때문이다', '주석은 SR-IOV의 PF/VF 제거 순서 문제를 설명합니다. safe 반복자는 삭제 중 다음 위치 보존을 돕지만 모든 동시성이나 순서 의존성을 해결하지 않습니다.'),
        ('stop_and_remove는 각 장치를 중지 즉시 제거하는 단일 순회인가?', '아니다. 전체 중지 재귀가 끝난 뒤 제거 재귀를 시작한다', '그렇다. 중지와 제거를 각 노드마다 교대로 호출한다', '두 개의 최상위 호출이 순서대로 배치되어 있습니다. 함수 이름만으로 한 번의 순회라고 추정하지 말고 단계 경계를 확인해야 합니다.'),
        ('pci_destroy_dev에서 pci_bus_sem이 보호하는 구간은?', 'bus_list 삭제 구간', '함수 시작부터 최종 put_device까지 전부', 'down_write와 up_write 사이에는 list_del이 있습니다. 드라이버나 DOE·ASPM·자원 정리까지 동일 잠금 범위라고 주장하면 안 됩니다.'),
        ('pci_remove_bus가 자식 PCI 장치를 직접 재귀 제거하는가?', '아니다. 그 작업은 상위 pci_remove_bus_device 등에서 먼저 한다', '그렇다. 함수 내부가 devices 목록 전체를 재귀 순회한다', 'remove_bus 본문에는 자식 장치 순회가 없습니다. 호출 순서의 전제와 단일 함수의 기능 범위를 구분해야 합니다.'),
        ('parent 없는 resource도 pci_free_resources가 release하는가?', '아니다. res->parent가 있을 때만 release_resource를 호출한다', '그렇다. 모든 항목을 kfree한다', '코드는 자원 트리에 연결된 항목만 해제합니다. release_resource와 해당 구조체 메모리의 kfree를 같은 작업으로 해석하면 틀립니다.'),
        ('root 제거 함수가 동적 도메인 번호를 반환하는 조건은?', 'GENERIC 도메인 지원에서 host_bridge->domain_nr가 NOT_SET일 때', '언제나 호스트의 모든 도메인 번호를 반환한다', '조건은 호스트 필드의 sentinel이고 실제 반환 대상은 bus->domain_nr입니다. 고정 지정된 도메인까지 무조건 반환하는 경로가 아닙니다.'),
        ('pci_remove_root_bus가 호출되면 호스트 드라이버 중지도 자동으로 이 함수가 수행하는가?', '아니다. 중지는 별도 pci_stop_root_bus에서 수행한다', '그렇다. 제거 함수 첫 줄이 stop_root_bus 호출이다', '제거 함수에 그 호출은 없습니다. 중지와 제거 API를 연결하는 책임은 호출 경로에서 확인해야 합니다.'),
        ('두 재귀 순회의 자료구조 비용은 정상 트리에서 어떻게 표현하는가?', '각 순회의 방문 O(N), 재귀 스택 O(H)', '방문 O(1), 스택이 항상 0', '각 장치를 한 번 방문하지만 깊이에 따라 호출 프레임이 쌓입니다. 이 표현은 하위 드라이버 정리 비용을 제외한 순회 자체의 비용입니다.')
    ]
)]
