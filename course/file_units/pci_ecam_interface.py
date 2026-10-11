"""Whole-file ECAM address macros and configuration window interface."""
ROWS = [dict(
    path='include/linux/pci-ecam.h', title='ECAM 헤더: 주소 비트 조립과 매핑 union',
    intro='주소 매크로, 두 구조체, 함수 선언과 구성별 연산 테이블 목록을 전체 분석합니다.',
    principle='마스크를 적용한 주소 조립은 입력 검증이 아니며 서로 다른 매핑 표현은 같은 union 저장소를 공유합니다.',
    use='비트 필드 인코딩, 경계값 절단, 함수 포인터, 합집합 자료형과 조건부 인터페이스를 학습합니다.',
    area='PCI ECAM · 비트 연산 · 메모리 주소 · union · 콜백',
    sections=[
        ('헤더 구성과 주소 단위', 'GPL-2.0과 Broadcom 저작권,DRIVERS_PCI_ECAM_H guard 아래 pci.h,kernel.h,platform_device.h를 포함합니다. 주석은 바이트 단위 PCI Express 설정 공간 주소의 시프트라고 설명하며 PCIe 사양 위치를 기록합니다. BUS_SHIFT=20,DEVFN_SHIFT=12,각 마스크는0xff,REG_MASK는0xfff입니다. 함수당 4096바이트 오프셋 공간과 버스당 1MiB 간격이라는 값을 이 상수에서 계산할 수 있습니다.'),
        ('주소 비트 조립', 'BUS(x)는 하위8비트를20만큼,DEVFN(x)는 하위8비트를12만큼 이동하고 REG(x)는 하위12비트만 남깁니다. OFFSET은 세 결과를 비트 OR합니다. 표준 위치가 서로 겹치지 않으므로 bus는27..20,devfn은19..12,레지스터는11..0 비트를 차지합니다. 범위 초과 입력은 오류가 아니라 마스킹으로 잘립니다. 예를 들어 bus=0x102는2,where=0x1234는0x234로 주소에 반영됩니다. 이 매크로들은 접근 폭에 맞는 정렬 검사도 하지 않습니다.'),
        ('연산 테이블 구조체', 'pci_config_window를 전방 선언한 뒤 pci_ecam_ops는 unsigned bus_shift,값으로 포함된 struct pci_ops,int 반환 init(window*) 콜백을 저장합니다. pci_ops 포인터를 저장하는 구조체가 아닙니다. init은 선택적인 초기화 함수 포인터이지만 NULL 처리나 호출 시점은 외부 구현의 책임입니다. 이 헤더만으로 버스 생성·설정 공간 읽기 순서가 실행되지는 않습니다.'),
        ('설정 창의 상태', 'pci_config_window는 resource res와 busr,unsigned bus_shift,void *priv,const pci_ecam_ops *ops,매핑 union,device *parent를 가집니다. 주석은 PCI 컨트롤러 sysdata로 사용할 구조라고 설명합니다. res와 busr는 값으로 포함된 서로 다른 자원이며 parent는 ECAM 자원이 유래한 장치입니다. union의 win은64비트 단일 I/O 매핑,winp는32비트 버스별 I/O 포인터 배열을 표현합니다. 두 멤버를 동시에 독립적으로 보관할 수 없고 이 구조체 자체에 별도 판별 태그 필드는 없습니다.'),
        ('생성·해제·주소 조회 선언', 'create는 device,cfgres,busr,ops를 받아 pci_config_window 포인터를 반환하고 free는 그 포인터를 받습니다. map_bus는 pci_bus, unsigned devfn,int where에서 __iomem 포인터를 반환합니다. 주석은 bus->sysdata가 window 인스턴스라는 전제를 명시합니다. 오류 포인터 반환이나 실제 매핑 해제의 상세 순서는 앞서 분석한 drivers/pci/ecam.c 구현에서 확인하며 선언만으로 보장된 것으로 섞지 않습니다.'),
        ('구성별 테이블과 공통 호스트 API', 'generic_ecam_ops는 조건 없이 extern const 선언됩니다. ACPI와 PCI_QUIRKS가 모두 정의되면32b_ops,32b_read_ops,hisi,thunder_pem,pci_thunder,xgene_v1,xgene_v2,al,tegra194,loongson의 열 개 테이블을 선언합니다. 선언 목록이 각 하드웨어의 실제 콜백 구현은 아닙니다. 별도로 IS_ENABLED(PCI_HOST_COMMON)이 참이면 DT ECAM용 platform_device probe와 void remove를 선언합니다. 이 두 조건부 블록에는 비활성 stub이 없습니다.'),
        ('전체 검토 범위와 계산 예', '모든 주소 상수·매크로,두 구조체의 필드,공통 함수·테이블과 조건부 선언을 대조했습니다. bus=2,devfn=0x19,where=0xabc의 OFFSET은0x219abc입니다. 입력 마스킹은 O(1) 비트 연산이며 주소를 계산할 뿐 해당 메모리에 접근하지 않습니다. 실제 ECAM 하드웨어나 구성별 빌드는 실행하지 않았습니다.')
    ], questions=[
        ('bus=2,devfn=0x19,where=0xabc의 표준 OFFSET은?', '0x219abc', '0x219000', '2<<20은0x200000,0x19<<12는0x19000이며 레지스터0xabc를 OR하면0x219abc입니다.'),
        ('where=0x1234를 REG 매크로에 주면 오류를 반환하는가?', '아니다. 하위12비트인0x234를 남긴다', '그렇다. 반드시 -EINVAL을 반환한다', '코드는 비트 AND뿐입니다. 범위 절단과 유효성 검증을 구별해야 합니다.'),
        ('win과 winp에 독립적인 두 매핑을 동시에 저장할 수 있는가?', '없다. 같은 union 저장소를 공유한다', '있다. 별도의 두 포인터 필드다', '하나는 단일 매핑,다른 하나는 매핑 배열이라는 대체 표현입니다. 어느 멤버를 사용할지는 구현의 매핑 정책에 따라야 합니다.'),
        ('pci_ecam_ops의 pci_ops 필드는 포인터인가?', '아니다. 구조체 값이 직접 포함된다', '그렇다. 항상 외부 pci_ops 객체 주소만 저장한다', '선언은 struct pci_ops pci_ops이며 별표가 없습니다. 반면 window의 ops는 const pci_ecam_ops 포인터입니다.'),
        ('PCI_HOST_COMMON 비활성 때 공통 probe의 무동작 inline이 제공되는가?', '아니다. 이 헤더에는 비활성 대체 본문이 없다', '그렇다. 항상 성공0인 stub을 제공한다', '조건 안에 두 선언이 있고 else가 없습니다. 조건부 선언 부재와 stub 존재는 다른 인터페이스입니다.')
    ]
)]
