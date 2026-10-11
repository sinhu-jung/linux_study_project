"""Whole-file OF address parser state, wrappers and configuration contracts."""
ROWS = [dict(
    path='include/linux/of_address.h', title='OF 주소 헤더: 범위 커서·BAR 선택·주소 개수 계산',
    intro='주소 파서 자료구조부터 마지막 count wrapper까지 파일 전체를 분석합니다.',
    principle='현재 커서에서 남은 범위를 세는 것과 최초 전체 개수를 보존하는 것은 다른 작업입니다.',
    use='포인터 차분, 합집합 저장소, 센티널 인수, 반복 종료 조건과 실패 표현을 학습합니다.',
    area='메모리 주소 · PCI BAR · DMA · 반복자 · 조건부 컴파일',
    sections=[
        ('헤더와 파서 상태', 'GPL-2.0 __OF_ADDRESS_H guard 아래 ioport, errno, of, io 헤더를 포함하고 of_bus를 전방 선언합니다. of_pci_range_parser는 node와 bus 포인터, const __be32 포인터 range와 end, int na/ns/pna, bool dma를 저장합니다. range는 현재 위치를 표현하며 셀 수 필드와 함께 남은 구간 해석에 쓰입니다. of_range_parser는 별도 구조체 정의가 아니라 of_pci_range_parser로 치환되는 매크로입니다.'),
        ('범위 결과와 union', 'of_pci_range는 익명 union 안의 u64 pci_addr와 bus_addr, 그 뒤의 u64 cpu_addr와 size, u32 flags로 구성됩니다. pci_addr와 bus_addr는 같은 union 저장소의 두 이름이므로 독립적인 두 주소 필드로 취급하면 안 됩니다. of_range 역시 of_pci_range의 매크로 별칭입니다. 버스 쪽 주소와 CPU 쪽 주소는 별도 필드지만 주소 변환 알고리즘은 이 자료구조 선언 자체에 없습니다.'),
        ('순회 매크로', 'for_each_of_pci_range(parser, range)는 for의 초기식과 증감식 없이 조건에서 of_pci_range_parser_one을 호출합니다. 반환 포인터가 참인 동안 본문이 실행되며 다음 상태로의 진행은 호출된 파서 구현에 의존합니다. for_each_of_range는 이 매크로의 별칭입니다. 이 매크로 자체는 초기화 함수를 호출하지 않으므로 사용 전에 파서 초기화가 필요합니다.'),
        ('남은 셀 개수 계산', 'of_range_count는 parser, node, range 중 하나가 NULL이거나 range==end이면 0을 반환합니다. 그 외에는 (end-range)/(na+pna+ns)입니다. 포인터 차이는 바이트가 아니라 __be32 원소 수이고 분모는 한 엔트리의 셀 수입니다. 현재 커서에서 계산하므로 순회 도중 또는 뒤에 호출하면 최초 개수가 아니라 남은 엔트리 수를 줍니다. end=NULL, 역전 구간, 분모 0, 나머지 셀을 별도로 검증하는 코드는 없어 정상적으로 초기화된 상태를 전제로 읽어야 합니다.'),
        ('조건 밖 DMA 선언', 'of_translate_dma_address는 노드와 빅엔디언 주소 셀 포인터를 받아 u64를 반환합니다. of_translate_dma_region은 같은 종류의 입력에 phys_addr_t *start와 size_t *length 출력 인수를 더해 const __be32 *를 반환합니다. 두 선언은 CONFIG_OF_ADDRESS 블록 밖에 있고 이 헤더는 비활성 stub을 정의하지 않습니다. 장치 공간에서 CPU 공간으로의 변환이라는 주석과 실제 구현의 위치를 구분해야 합니다.'),
        ('활성 주소·매핑 API', 'CONFIG_OF_ADDRESS 안에는 translate_address, address_to_resource, iomap, io_request_and_map, __of_get_address, property_read_reg 선언이 있습니다. __of_get_address는 index와 bar_no 둘 다 받으며 size와 flags 출력 포인터도 받습니다. property_read_reg는 idx와 u64 addr/size 출력 포인터를 받습니다. __iomem 표기는 I/O 메모리 포인터의 구분을 드러내며 선언만으로 매핑·예약 해제 수명을 확정할 수는 없습니다.'),
        ('활성 범위·자원 API', '같은 활성 블록은 일반 range와 DMA range 초기화 두 함수, parser_one, pci_address_to_resource, pci_range_to_resource, range_to_resource, dma_is_coherent를 선언합니다. PCI 주소 변환에는 bar 번호를, 일반 range 변환에는 index를 전달합니다. pci_range_to_resource는 이미 채워진 범위 구조체를 받습니다. 이 선언들은 입력 형태를 보여주지만 연속 범위 병합, 주소 플래그 해석, 캐시 일관성 판정 규칙의 구현은 제공하지 않습니다.'),
        ('OF_ADDRESS 비활성 결과', 'io_request_and_map은 IOMEM_ERR_PTR(-EINVAL), translate_address는 OF_BAD_ADDR, __of_get_address는 NULL, property_read_reg와 두 파서 init 및 세 자원 변환 함수는 -ENOSYS입니다. parser_one은 NULL이고 dma_is_coherent는 false입니다. 출력 인수나 parser를 초기화하는 코드는 없습니다. 따라서 오류 포인터, 주소 센티널, NULL, 음수 정수, false를 하나의 동일한 실패 표현으로 혼동하면 안 됩니다. 비활성 파서 init 실패 뒤 초기화되지 않은 상태를 range_count에 전달하는 것도 안전하다고 보장되지 않습니다.'),
        ('별도의 CONFIG_OF 블록', 'address_to_resource와 iomap은 뒤쪽 CONFIG_OF 블록에서 다시 외부 선언됩니다. OF가 없으면 각각 -EINVAL과 NULL을 반환하는 inline입니다. 이 두 함수의 대체 본문은 OF_ADDRESS의 else에 있지 않습니다. 실제 가능한 설정 조합은 Kconfig도 확인해야 하지만 헤더의 분기 경계를 읽을 때 두 CONFIG를 같은 조건으로 합쳐서는 안 됩니다.'),
        ('주소 선택 wrapper', 'of_range_parser_init은 pci_range_parser_init 별칭입니다. of_get_address는 __of_get_address(dev,index,-1,size,flags)를 호출하고 of_get_pci_address는 __of_get_address(dev,-1,bar_no,size,flags)를 호출합니다. -1은 사용하지 않는 선택 방식의 인수 자리에 들어가며 일반 index와 PCI BAR 번호를 구별합니다. wrapper 자체가 BAR를 index로 산술 변환하는 것은 아닙니다.'),
        ('연속 성공을 세는 루프', 'of_address_count는 지역 resource와 count=0으로 시작해 of_address_to_resource(np,count,&res)==0인 동안 count를 증가시킵니다. 첫 실패에서 종료하고 그 전까지 연속으로 성공한 개수를 반환합니다. 실패 이후 index를 건너뛰어 검색하지 않으며 실패 원인을 반환하지도 않습니다. N번 성공 뒤 실패하면 하위 호출은 N+1회입니다. 루프 자체의 추가 저장 공간은 일정하지만 전체 시간은 하위 변환 함수의 비용에도 의존합니다.'),
        ('범위와 실행 한계', '두 구조체, 별칭과 순회 매크로, count 계산, 모든 활성 선언·비활성 본문, 두 주소 선택 wrapper와 마지막 주소 개수 루프까지 대조했습니다. 실제 MMIO 매핑, DMA 변환, PCI 자원 등록, 구성별 커널 빌드는 수행하지 않았습니다. 이 자료는 헤더가 드러내는 계약과 직접 정의한 코드의 동작을 다룹니다.')
    ], questions=[
        ('na=2,pna=2,ns=1이고 end-range가 15셀이라면 of_range_count는?', '3', '15바이트를 반환한다', '분모는 엔트리당 5셀이고 포인터 차이는 15개의 __be32 원소입니다. 따라서 15/5=3이며 바이트 크기를 곱하는 코드가 아닙니다.'),
        ('range 파서 순회 도중 count를 다시 호출하면 최초 개수가 보존되는가?', '아니다. 현재 커서부터 남은 수를 계산한다', '그렇다. 초기 개수를 별도 필드에 저장해 반환한다', '본문은 현재 end-range를 사용합니다. 구조체에 초기 개수를 캐시하는 필드도 없고 주석도 순회 중·후의 결과가 남은 엔트리 수라고 경고합니다.'),
        ('pci_addr와 bus_addr에 서로 다른 두 값을 독립적으로 보관할 수 있는가?', '없다. 같은 union 저장소를 공유한다', '있다. 항상 두 개의 별도 u64 저장소다', '두 이름은 익명 union의 멤버입니다. cpu_addr와는 구분되지만 이 두 멤버끼리는 독립적인 필드 저장소가 아닙니다.'),
        ('of_get_pci_address가 __of_get_address에 전달하는 index는?', '-1', 'bar_no와 같은 값', 'PCI wrapper는 index=-1과 지정된 bar_no를 넘깁니다. 반대로 일반 wrapper는 지정된 index와 bar_no=-1을 넘겨 두 선택 방식을 구분합니다.'),
        ('주소 변환이 index 0,1에서 성공하고 2에서 실패하면 count 결과와 호출 횟수는?', '결과 2, 호출 3회', '결과 3, 호출 2회', '실패한 index의 호출은 while 조건 평가에 포함되지만 count 증가에는 포함되지 않습니다. index 3 이후는 확인하지 않습니다.'),
        ('OF_ADDRESS 비활성에서 io_request_and_map과 __of_get_address의 실패 표현은 같은가?', '아니다. 오류 I/O 포인터와 NULL이다', '그렇다. 둘 다 반드시 NULL이다', '앞은 IOMEM_ERR_PTR(-EINVAL)을, 뒤는 NULL을 반환합니다. 포인터 반환이라는 공통점만으로 동일한 오류 판정 방식을 가정하면 안 됩니다.'),
        ('of_range_count가 분모 0인 손상된 파서 상태까지 검증하는가?', '아니다. 셀 수 합에 대한 0 검사는 없다', '그렇다. 모든 잘못된 상태를 -EINVAL로 바꾼다', '가드는 parser/node/range 부재와 range==end만 확인합니다. 이후 바로 나눗셈을 수행하므로 정상적인 초기화 전제를 지켜야 하며 반환 타입이 int라는 이유로 오류 검증을 추정하면 안 됩니다.')
    ]
)]
