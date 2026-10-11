"""Whole-file OF networking interface and PHY/MAC retrieval implementation."""
ROWS = [dict(
    path='include/linux/of_net.h', title='OF 네트워크 계약: 출력 인수와 비지원 stub',
    intro='PHY·MAC 조회 및 netdevice 검색 선언과 대체 구현 전체를 분석합니다.',
    principle='오류를 반환하는 stub이 출력 저장소까지 초기화한다고 가정하면 안 됩니다.',
    use='조건부 API,출력 포인터와 NULL·errno 반환을 구분합니다.',
    area='네트워크 · 장치 트리 · 인터페이스 · 구성',
    sections=[
        ('헤더와 조건', 'GPL-2.0-only guard에서 phy.h를 포함합니다. CONFIG_OF와 CONFIG_NET이 모두 정의된 경우 of.h를 포함하고 net_device를 전방 선언합니다. 하나라도 없으면 대체 inline 영역을 사용합니다.'),
        ('다섯 API', 'get_phy_mode는 node와 phy_interface_t 출력 포인터,get_mac_address와 nvmem 변형은 node와 u8 버퍼,get_ethdev_address는 node와 net_device를 받아 int를 반환합니다. find_net_device_by_node는 net_device *를 반환합니다. 헤더에는 조회 알고리즘이나 MAC 버퍼 크기 검사가 직접 구현되어 있지 않습니다.'),
        ('비활성 출력 계약', '네 int 함수는 모두 -ENODEV를 반환하고 출력 포인터에 값을 쓰지 않습니다. 검색 함수만 NULL을 반환합니다. 활성 PHY 구현이 interface를 NA로 초기화하더라도 이 stub은 같은 초기화를 하지 않습니다. 반환 오류 후 출력값을 사용하기 전에 호출자 계약을 확인해야 합니다.'),
        ('전체 범위', 'include,전방 선언,다섯 선언과 다섯 stub,조건·guard를 모두 확인했습니다. netdevice 검색 함수의 구현까지 이 헤더로 검토한 것은 아닙니다. 실제 네트워크 장치 조회나 구성별 컴파일은 수행하지 않았습니다.')
    ], questions=[
        ('OF만 켜고 NET이 없으면 활성 선언 영역을 쓰는가?', '아니다. 두 설정이 모두 필요하다', '그렇다. NET은 검사하지 않는다', '전처리 조건은 두 defined의 AND입니다.'),
        ('비지원 get_phy_mode는 출력 interface를 NA로 초기화하는가?', '아니다. -ENODEV 반환문만 있다', '그렇다. 모든 구성에서 같은 대입을 한다', '활성 구현과 stub의 실제 쓰기 동작은 다릅니다. 이름이 같아도 출력 보장을 별도로 확인합니다.')
    ]
), dict(
    path='net/core/of_net.c', title='OF PHY·MAC 조회: 우선순위와 NVMEM 소유권',
    intro='PHY 모드 해석,MAC 속성 검증,NVMEM fallback과 netdevice 갱신 전체를 분석합니다.',
    principle='우선순위 조회는 속성의 존재뿐 아니라 유효성에 따라 다음 후보로 진행할 수 있습니다.',
    use='문자열 검색,실패 전파,자원 참조와 성공 시에만 상태 변경하는 패턴을 학습합니다.',
    area='네트워크 · MAC · PHY · NVMEM · 오류 처리',
    sections=[
        ('구성과 PHY 초기값', 'GPL-2.0-only 파일은 etherdevice,kernel,OF net/platform,platform_device,phy,export,device,nvmem-consumer를 포함합니다. get_phy_mode는 먼저 *interface=PHY_INTERFACE_MODE_NA로 둡니다. phy-mode 문자열 읽기 오류이면 phy-connection-type을 읽고 그마저 오류면 반환합니다.'),
        ('모드 선형 검색과 fallback 한계', '읽은 문자열은 0부터 PHY_INTERFACE_MODE_MAX 미만까지 phy_modes(i)와 strcasecmp로 비교합니다. 첫 일치의 인덱스를 저장하고 0,없으면 -ENODEV입니다. phy-mode를 읽었지만 알 수 없는 문자열인 경우에는 phy-connection-type을 다시 시도하지 않습니다. 속성 읽기 실패와 값 인식 실패의 fallback 위치가 다릅니다.'),
        ('MAC 속성 검증', '내부 get_mac_addr는 해당 속성이 있고 길이가 ETH_ALEN이며 is_valid_ether_addr가 참일 때만 ETH_ALEN바이트를 복사하고 성공합니다. 아니면 -ENODEV입니다. 주석은 특히 부트로더가 채우지 않은 all-zero 속성을 거부해야 한다고 설명합니다. 존재한다는 사실만으로 그 후보를 선택하지 않습니다.'),
        ('NVMEM의 device 경로', 'get_mac_address_nvmem은 먼저 of_find_device_by_node로 platform device를 찾습니다. 있으면 nvmem_get_mac_address를 호출하고 put_device한 뒤 결과를 그대로 반환합니다. 이 경로가 실패했다고 뒤의 OF cell 조회로 계속 진행하지는 않습니다. device lookup에 연결된 nvmem_cell_lookup을 사용할 수 있다는 주석이 있습니다.'),
        ('OF cell 경로의 자원 정리', 'platform device가 없을 때 of_nvmem_cell_get(np,"mac-address")를 호출하고 오류 포인터면 PTR_ERR입니다. cell_read 뒤에는 성공 여부와 무관하게 cell_put을 실행합니다. 읽기 결과가 오류 포인터면 반환하고,길이 또는 주소 유효성이 맞지 않으면 읽은 버퍼를 kfree하고 -EINVAL입니다. 성공이면 복사 후 같은 버퍼를 kfree합니다. cell 참조와 읽은 데이터 버퍼 수명은 별개입니다.'),
        ('MAC 후보의 순서', '공개 get_mac_address는 np=NULL이면 -ENODEV입니다. mac-address,local-mac-address,구형 address 순으로 내부 helper를 호출해 첫 유효 결과를 반환하고 모두 실패하면 NVMEM을 조회합니다. address는 원래 레지스터의 가상 주소 의미지만 일부 DTS의 과거 사용을 지원한다는 문서가 있습니다. 앞 후보가 존재해도 길이나 값이 부적절하면 다음을 시도합니다.'),
        ('Netdevice 갱신', 'get_ethdev_address는 지역 ETH_ALEN 배열에 주소를 조회하고 성공한 경우에만 eth_hw_addr_set(dev,addr)를 호출합니다. 오류면 장치 주소를 이 함수에서 바꾸지 않고 같은 ret을 반환합니다. 이 동작은 패킷 송신이나 인터페이스 활성화를 수행하는 것이 아닙니다.'),
        ('Export와 검토 범위', 'PHY helper는 EXPORT_SYMBOL_GPL이고 NVMEM MAC,일반 MAC,ethdev 주소 함수는 EXPORT_SYMBOL입니다. 내부 속성 helper와 공개 함수 네 개,문서 및 모든 실패 경로를 확인했습니다. 헤더의 of_find_net_device_by_node 구현은 이 파일에 없습니다. 실제 NVMEM·PHY 하드웨어 조회나 MAC 변경을 실행하지 않았습니다.')
    ], questions=[
        ('phy-mode를 읽었지만 모드 이름이 미지원이면 두 번째 속성도 시도하는가?', '아니다. 모드 검색 실패는 -ENODEV다', '그렇다. 어떤 실패든 항상 두 번째 속성으로 간다', 'fallback은 문자열 읽기 오류 직후에만 있습니다. 파싱 성공과 의미 인식 성공을 구분합니다.'),
        ('MAC 후보 속성이 있지만 모두 0이면 다음 후보를 보는가?', '그렇다. 유효 주소 검사에 실패해 다음으로 진행한다', '아니다. 존재하는 첫 속성을 무조건 선택한다', '길이와 주소 유효성이 함께 필요합니다. 부트로더가 초기화하지 않은 속성 사례가 문서에 있습니다.'),
        ('Platform device 경로의 NVMEM 조회가 실패하면 OF cell 경로로 이어지는가?', '아니다. device 참조 반환 후 즉시 그 오류를 반환한다', '그렇다. 모든 NVMEM 경로를 끝까지 시도한다', 'pdev가 존재하는 분기에 return ret이 있습니다. 경로 선택과 실패 fallback은 다릅니다.'),
        ('cell_read 오류에서도 cell 참조를 반환하는가?', '그렇다. IS_ERR(mac) 검사 전에 cell_put한다', '아니다. 성공할 때만 cell_put한다', '읽은 버퍼와 cell 자체는 서로 다른 자원입니다. 각각의 해제 위치를 추적합니다.'),
        ('MAC 조회 실패 시 get_ethdev_address가 장치 주소를 0으로 지우는가?', '아니다. 성공할 때만 주소를 설정한다', '그렇다. 모든 실패가 기존 주소를 지운다', 'eth_hw_addr_set은 !ret 조건 안에 있습니다. 실패 시 출력 대상 상태 보존을 확인할 수 있습니다.')
    ]
)]
