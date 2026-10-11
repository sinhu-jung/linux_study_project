"""Whole-file generic PCI host compatible dispatch and DesignWare filtering."""
ROWS = [dict(
    path='drivers/pci/controller/pci-host-generic.c', title='범용 PCI 호스트: compatible 전략 선택과 중복 장치 필터',
    intro='두 로컬 연산 테이블, DesignWare 필터, 다섯 매칭 항목과 플랫폼 드라이버 등록 전체를 분석합니다.',
    principle='공통 초기화 흐름은 유지하면서 장치별 주소 접근 정책을 데이터와 함수 포인터로 선택할 수 있습니다.',
    use='전략 테이블, 비트 필드 추출, 경계 조건, 간접 호출과 선언적 장치 매칭을 학습합니다.',
    area='PCI 호스트 · CAM · ECAM · 함수 포인터 · 장치 매칭',
    sections=[
        ('목적과 CAM 연산', 'GPL-2.0 파일은 펌웨어가 초기화한 시스템과 가상 머신을 대상으로 한다는 주석과 kernel,init,module,pci-ecam,platform_device include를 갖습니다. gen_pci_cfg_cam_bus_ops는 bus_shift=16,map_bus=pci_ecam_map_bus,일반 config read/write를 지정합니다. 따라서 주소 계산을 공통 함수에 위임하되 버스 간격은 2의16승 바이트로 선택합니다. 이 로컬 테이블에는 add_bus/remove_bus/init 콜백 지정이 없습니다.'),
        ('DesignWare 유효 장치 판정', 'pci_dw_valid_device는 bus->sysdata를 pci_config_window로 보고 bus->number==cfg->busr.start이면서 PCI_SLOT(devfn)>0이면 false,그 외는 true입니다. 주석은 ECAM 모드의 DesignWare가 downstream 포트에서 장치1 이상에 대한 type0 접근을 걸러내지 않아 중복 장치처럼 보이는 문제를 설명합니다. 코드 기준은 절대 버스0이 아니라 설정 창의 시작 버스입니다. 슬롯0의 함수1 이상을 이 조건이 금지하는 것은 아닙니다.'),
        ('주소 변환 wrapper', 'pci_dw_ecam_map_bus는 위 판정이 거짓이면 NULL이고 참이면 공통 pci_ecam_map_bus에 bus,devfn,where를 그대로 전달합니다. 이 wrapper 자체가 모든 버스 범위나 레지스터 오프셋을 검증하지는 않습니다. pci_dw_ecam_bus_ops는 이 wrapper와 일반 read/write를 지정하며 bus_shift는 명시하지 않아0입니다. 앞서 본 공통 구현에서0은 표준 ECAM 경로를 선택하는 값입니다.'),
        ('다섯 compatible의 데이터 연결', 'gen_pci_of_match는 pci-host-cam-generic을 CAM 테이블에,pci-host-ecam-generic을 외부 pci_generic_ecam_ops에 연결합니다. marvell,armada8k-pcie-ecam,socionext,synquacer-pcie-ecam,snps,dw-pcie-ecam 세 항목은 모두 같은 DesignWare 필터 테이블을 가리킵니다. 끝에는 빈 sentinel이 있고 MODULE_DEVICE_TABLE(of,...)로 OF 매칭 메타데이터를 지정합니다. 각 항목이 별도 probe 함수를 만드는 것은 아닙니다.'),
        ('플랫폼 등록과 공통 수명', 'gen_pci_driver의 이름은 pci-host-generic,of_match_table은 위 배열입니다. probe는 pci_host_common_probe,remove_new는 pci_host_common_remove로 연결하고 module_platform_driver로 등록·해제 연결을 생성합니다. 앞서 본 common probe는 match data를 ops로 읽으므로 compatible에서 고른 테이블이 실제 ECAM 생성으로 전달됩니다. 파일 끝에는 드라이버 설명과 GPL v2 라이선스가 있습니다.'),
        ('전체 범위와 한계', '로컬 CAM/DW 테이블,두 함수,다섯 매칭 항목과 sentinel,플랫폼 드라이버 및 모듈 메타데이터 전체를 대조했습니다. 필터는 O(1)의 비교와 슬롯 추출이며 장치 목록을 검색하는 루프가 아닙니다. 펌웨어 초기화 내용을 생성하거나 하드웨어 링크를 훈련하는 코드도 이 파일에 없습니다. 실제 호스트 바인딩이나 중복 장치 접근 재현,커널 빌드는 수행하지 않았습니다.')
    ], questions=[
        ('창 시작 버스가0x40이면 DesignWare 필터가 특별 취급하는 버스는?', '0x40', '무조건0', '실제 조건은 cfg->busr.start와 비교합니다. 주석의 bus0 설명을 코드의 절대0 검사로 바꾸면 잘못된 해설입니다.'),
        ('시작 버스의 슬롯0,함수3은 이 로컬 필터가 거부하는가?', '아니다. 슬롯 번호가0이므로 통과한다', '그렇다. devfn이0이 아니면 모두 거부한다', 'PCI_SLOT(devfn)>0을 검사하며 함수 비트는 이 조건에 포함되지 않습니다. 다만 통과 후 공통 매핑 함수의 추가 조건은 별도로 적용됩니다.'),
        ('CAM 테이블의 버스 간격은 어떤 설정으로 선택하는가?', 'bus_shift=16', 'read 콜백을 NULL로 두는 방식', '주소 계산을 공통 map_bus에 위임하되 shift를16으로 지정합니다. 일반 read/write도 명시적으로 연결되어 있습니다.'),
        ('세 DesignWare 계열 compatible마다 독립 probe가 있는가?', '아니다. 같은 필터 ops와 공통 probe를 공유한다', '그렇다. 각 항목 안에서 별도 probe를 정의한다', '매칭 항목의 data가 같은 pci_dw_ecam_bus_ops를 가리키며 플랫폼 드라이버의 probe도 하나입니다. 데이터 기반 전략 선택의 예입니다.'),
        ('DesignWare wrapper가 거부한 장치는 공통 map_bus를 호출하는가?', '아니다. NULL로 즉시 반환한다', '그렇다. 매핑한 뒤 결과를 취소한다', '유효성 검사가 공통 함수 호출보다 먼저입니다. 불필요한 설정 접근 주소 생성 경로를 차단하는 순서입니다.')
    ]
)]
