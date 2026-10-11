"""Whole-file dynamic PCI OF property construction."""
ROWS = [dict(
    path='drivers/pci/of_property.c', title='PCI 동적 속성 생성: 주소 셀·2회 순회·interrupt-map',
    intro='주소 인코딩과 모든 속성 생성 도우미, 최상위 호출 순서 전체를 분석합니다.',
    principle='직렬화용 배열은 셀 개수와 쓰기 커서가 일치해야 하며 중간 실패의 정리는 호출 계층별로 구분해야 합니다.',
    use='비트 필드, 64비트 분할, 배열 압축, 크기 계산 후 생성하는 2회 순회와 changeset 수명을 학습합니다.',
    area='PCI · 직렬화 · 비트 연산 · 배열 · 인터럽트 · 메모리 관리',
    sections=[
        ('상수와 셀 자료구조', 'GPL-2.0+ 파일은 PCI, OF, OF IRQ, bitfield, bits와 내부 pci.h를 포함합니다. 주소 셀 3개, 크기 셀 2개, 최대 INTx pin 4개를 정의합니다. of_pci_addr_pair는 주소3+크기2이고 이 파일의 of_pci_range는 자식 주소3+부모 주소3+크기2입니다. 여기의 셀 배열 구조체는 다른 주소 헤더에서 이름이 같은 CPU 주소·크기 필드 구조체와 구분해야 합니다. 호환 문자열 enum은 vendor/device, 전체 class, 하위 프로그램 인터페이스를 제외한 class의 세 항목과 개수입니다.'),
        ('주소 비트 필드', '공간 코드는 IO=1,MEM32=2,MEM64=3입니다. NONRELOC는 비트31, PREFETCH는 비트30, SS는25..24, BUS는23..16, DEV는15..11, FUNC는10..8, REG는7..0입니다. set_address는 FIELD_PREP로 버스·슬롯·함수를 첫 셀에 넣고 flags와 reg_num을 OR합니다. REG 마스크 상수는 정의되어 있지만 reg_num에 FIELD_PREP나 마스킹을 적용하는 코드는 없습니다. reloc가 거짓일 때만 NONRELOC와 주소 상·하위32비트를 씁니다. 참일 때 뒤 두 셀을 0으로 만드는 코드는 없으므로 호출자의 초기화 상태가 중요합니다.'),
        ('자원 플래그 선택과 bus-range', 'get_addr_flags는 IO, MEM_64, MEM 순서로 검사하며 어느 것도 아니면 -EINVAL입니다. 유효할 때만 출력 flags를 0으로 초기화하고 PREFETCH와 SS를 넣습니다. 실패 시 출력값 초기화는 없습니다. bus_range 도우미는 subordinate->busn_res.start와 end를 u32 배열로 만들어 changeset에 추가합니다. subordinate가 NULL인지 검사하는 코드는 이 함수에 없으며 상위 호출의 브리지 전제에 의존합니다.'),
        ('ranges 배열 압축', '브리지이면 PCI_BRIDGE_RESOURCES에서 PCI_BRIDGE_RESOURCE_NUM개, 아니면 표준 BAR 영역에서 PCI_STD_NUM_BARS개를 대상으로 kcalloc합니다. j는 원본 자원 인덱스, i는 유효 출력 엔트리 수입니다. resource_size가 0이거나 플래그 변환이 실패하면 건너뛰어 출력 배열을 빈틈없이 채웁니다. 부모 주소에는 res.start와 flags를 비재배치 주소로 씁니다. 브리지는 부모 주소 셀3개를 자식 주소에 그대로 복사하고 endpoint는 child_addr[0]=j, 나머지 두 셀은 kcalloc의 0을 유지합니다. size는 상·하위32비트입니다. i개의 8셀 엔트리만 속성에 추가하고 성공·실패 모두 임시 rp를 해제합니다.'),
        ('reg와 interrupts', 'reg 도우미는 0으로 초기화한 주소·크기 쌍에 reloc=true로 버스·슬롯·함수만 넣고 다섯 셀 전체를 추가합니다. interrupts 도우미는 PCI_INTERRUPT_PIN 읽기 오류를 반환하고 pin=0이면 속성을 만들지 않은 채 0, 나머지는 pin을 u32 속성으로 추가합니다. intr_ctrl도 같은 pin 읽기·0 검사를 한 뒤 #interrupt-cells=1과 값 없는 interrupt-controller 속성을 순서대로 추가합니다. 마지막 추가 실패 시 앞선 changeset 항목을 여기서 되돌리지는 않습니다.'),
        ('네 pin의 상위 IRQ 해석', 'intr_map은 상위 PCI 장치의 OF 노드, 없으면 버스 OF 노드를 사용하며 둘 다 없으면 -EINVAL입니다. 현재 버스 번호와 devfn으로 laddr의 첫 셀을 빅엔디언 변환하고 나머지는 0입니다. pin1..4 각각 out_irq의 부모와 한 개 인수를 설정해 raw 파싱합니다. 실패한 pin은 np=NULL로 표시하고 계속합니다. 성공 시 #address-cells 읽기를 시도하지만 오류는 검사하지 않으며 addr_sz는 최초 0으로 초기화되어 있습니다.'),
        ('interrupt-map 크기 계산', 'subordinate->devices의 각 자식에 대해 pin1..4를 swizzle하고 해당 상위 결과가 있는 경우에만 map_sz에 5+addr_sz+args_count를 더합니다. 고정5셀은 자식 주소3, pin1, 부모 phandle1입니다. map_sz는 u32이며 누적 오버플로를 직접 검사하는 코드는 없습니다. 0이면 속성을 생성하지 않고 성공하며, 이는 모든 파싱 실패뿐 아니라 자식이 없는 경우에도 가능합니다. 양수이면 그 셀 수만큼 kcalloc합니다.'),
        ('interrupt-map 쓰기 커서', '같은 자식·pin 순회로 실제 배열을 채웁니다. 자식 주소 첫 셀을 쓰고 커서를 3셀 전진시켜 나머지 두 셀의 0을 유지합니다. 원래 pin과 해석된 부모 phandle을 쓰고 addr_sz가 있으면 부모 reg의 해당 셀들을 읽어 넣습니다. 읽기 실패는 해제 경로로 갑니다. 마지막에 out_irq.args를 memcpy합니다. 크기 계산 순회와 생성 순회의 선택 조건이 맞아야 버퍼 길이와 커서가 일치하는 구조입니다. 자식 C개에 대해 두 번의 4핀 순회를 하므로 IRQ 파싱·속성 읽기 비용을 제외한 방문 수는 C에 선형입니다.'),
        ('IRQ 속성 추가와 수명 한계', '생성한 interrupt-map, #interrupt-cells=1, interrupt-map-mask={0xffff00,0,0,7}을 순서대로 추가합니다. 첫 셀 마스크는 버스·devfn 비트 영역을 포함하며 단순 슬롯만의 마스크가 아닙니다. 각 실패는 int_map 해제 후 오류를 반환하지만 이미 추가한 changeset 항목은 여기서 삭제하지 않습니다. 성공도 임시 int_map을 해제합니다. 이 도우미에는 성공한 out_irq[i].np에 대한 명시적 of_node_put 호출이 없으며 참조 수명의 완전한 판단에는 하위 파서 계약도 함께 봐야 합니다.'),
        ('compatible 문자열', 'vendor/device는 pci%x,%x, 전체 class는 pciclass,%06x, class>>8은 pciclass,%04x로 kasprintf합니다. 세 문자열을 string_array로 추가한 뒤 각각 kfree하고 그 반환값을 돌려줍니다. 개별 kasprintf 실패를 검사하고 조기에 반환하는 코드는 없습니다. 따라서 모든 포인터가 유효하다고 이 본문만으로 보장하거나 로컬에서 모든 할당 실패를 처리한다고 설명하면 안 됩니다.'),
        ('최상위 순서와 changeset', 'of_pci_add_properties는 브리지이면 device_type=pci,bus-range,interrupt-map을, endpoint이면 intr_ctrl을 먼저 수행합니다. 공통 순서는 ranges,#address-cells=3,#size-cells=2,reg,compatible,interrupts입니다. 각 단계 실패는 즉시 반환합니다. 추가 속성이 changeset destroy에서 해제된다는 주석은 있지만 이 함수 자체는 changeset을 apply하거나 destroy하지 않습니다. 앞서 작성한 of.c의 호출자는 생성·추가·apply 및 실패 정리를 담당하므로 두 파일을 연결해 수명을 읽어야 합니다.'),
        ('전체 범위', '두 셀 구조체, 모든 비트 상수와 enum, 주소·플래그 도우미, bus-range/ranges/reg/interrupts/controller/map/compatible 생성 및 최상위 함수를 모두 대조했습니다. 자원 주소를 별도 변환 없이 res.start에서 가져오는 점과 endpoint의 BAR 인덱스 보존도 반영했습니다. 실제 PCI 장치, IRQ 라우팅, 동적 트리 변경이나 커널 빌드는 실행하지 않았습니다.')
    ], questions=[
        ('ranges에서 유효 자원 j=0과 j=3만 남으면 출력 i와 endpoint child_addr[0]은?', '출력은 두 엔트리이고 child 인덱스는 0과 3이다', '출력은 네 엔트리이고 모든 인덱스를 0으로 바꾼다', 'i는 압축된 출력 위치이고 j는 원래 BAR 위치입니다. endpoint 자식 첫 셀에는 j를 저장하므로 건너뛴 자원 때문에 BAR 번호가 재부여되지 않습니다.'),
        ('set_address에서 reloc=true이면 뒤 주소 셀 두 개를 직접 지우는가?', '아니다. 뒤 두 셀을 쓰지 않는다', '그렇다. 항상 0을 대입한다', 'prop[1],prop[2] 쓰기는 !reloc 블록 안에만 있습니다. reg 호출자가 구조체를 0으로 초기화한 덕분에 결과가 0인 것과 함수가 지우는 것은 다릅니다.'),
        ('interrupt-map에서 부모 주소2셀과 IRQ 인수3셀이 필요하면 엔트리 길이는?', '10셀', '5셀', '고정5셀에 addr_sz=2와 args_count=3을 더합니다. 크기 계산과 커서 이동 모두 이 구조를 따라야 합니다.'),
        ('부모 IRQ 파싱이 성공해도 자식 장치가 하나도 없으면 map은 생성되는가?', '아니다. map_sz=0이어서 성공 반환한다', '그렇다. 항상 네 pin 엔트리를 생성한다', 'map_sz 누적은 자식 목록 순회 안에서 이루어집니다. 모든 pin 파싱 실패만이 map_sz=0의 유일한 원인은 아닙니다.'),
        ('compatible 도우미가 세 kasprintf의 NULL을 각각 검사하는가?', '아니다. 별도 검사 없이 배열 추가 함수에 전달한다', '그렇다. 첫 NULL에서 모든 이후 할당을 생략한다', '세 할당 뒤 바로 of_changeset_add_prop_string_array를 호출합니다. 후속 kfree는 있지만 개별 실패의 조기 처리는 없습니다.'),
        ('최상위 속성 추가 함수가 중간 실패할 때 이전 속성을 직접 destroy하는가?', '아니다. 오류를 반환하며 changeset 정리는 호출 계층의 책임이다', '그렇다. 내부에서 항상 apply와 destroy를 모두 수행한다', '본문은 매 단계 ret 검사 후 반환합니다. 실제 apply나 destroy 호출은 없으며 of.c의 생성 호출 경로와 함께 수명을 확인해야 합니다.'),
        ('pin=0일 때 interrupts와 interrupt-controller 도우미의 동작은?', '둘 다 속성을 추가하지 않고 0을 반환한다', '둘 다 pin0 속성을 반드시 추가한다', '설정 바이트 읽기 다음 if(!pin)return 0이 있습니다. 정상 반환과 실제 속성 생성은 동일한 사실이 아닙니다.'),
        ('interrupt-map-mask의 첫 값 0xffff00은 슬롯 번호만 비교하는가?', '아니다. 버스 번호와 devfn 영역의 비트를 포함한다', '그렇다. 모든 버스·함수 비트는 제외한다', '주소 첫 셀의 버스는23..16,장치는15..11,함수는10..8입니다. 마스크는23..8 전체를 포함하므로 슬롯만의 필터로 해석하면 틀립니다.')
    ]
)]
