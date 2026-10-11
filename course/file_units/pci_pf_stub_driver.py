"""Whole-file fixed-ID SR-IOV PF stub driver."""
ROWS = [dict(
    path='drivers/pci/pci-pf-stub.c', title='PCI PF stub: 고정 ID와 SR-IOV 구성 콜백',
    intro='고정 장치 목록, probe, SR-IOV 콜백 연결과 모듈 등록 전체를 분석합니다.',
    principle='장치를 바인딩하는 최소 드라이버와 가상 기능 구성의 공통 구현을 분리할 수 있습니다.',
    use='sentinel 테이블, 함수 포인터 위임, 모듈 매칭과 기능 소유권을 학습합니다.',
    area='PCI · SR-IOV · PF/VF · 드라이버 매칭 · 콜백',
    sections=[
        ('목적과 범위', 'GPL-2.0 파일의 주석은 자체 전용 드라이버는 필요 없지만 SR-IOV 기능을 제공하는 장치를 위한 PF stub이라고 설명합니다. module.h와 pci.h를 포함합니다. 모든 PCI 물리 기능을 무조건 지원하는 코드가 아니라 특정 장치 목록에 바인딩해 공통 SR-IOV 구성 경로를 제공하는 최소 드라이버입니다.'),
        ('고정 ID 테이블', 'pci_pf_stub_whitelist는 const pci_device_id 배열이며 실제 항목은 PCI_VDEVICE(AMAZON,0x0053) 하나입니다. 마지막 {0}은 필수 종료 항목으로 주석이 표시되어 있습니다. vendor 매크로와 device 값을 별개의 식별 요소로 읽어야 합니다. MODULE_DEVICE_TABLE(pci,...)는 이 테이블의 PCI 모듈 매칭 메타데이터를 연결하며 그 문장 자체가 VF를 생성하는 것은 아닙니다.'),
        ('probe와 SR-IOV 위임', 'pci_pf_stub_probe는 claimed by pci-pf-stub 로그를 출력하고0을 반환합니다. BAR 할당이나 IRQ 요청,VF 개수 설정 코드는 이 본문에 없습니다. pf_stub_driver는 이름 pci-pf-stub,id_table에 고정 목록,probe에 이 함수를 연결하고 sriov_configure에 외부 pci_sriov_configure_simple을 지정합니다. 따라서 SR-IOV 구성 요청의 실제 처리는 외부 공통 함수에 위임되며 VF 생성·제거와 오류 규칙은 그 구현에서 확인해야 합니다.'),
        ('등록과 일반 stub과의 차이', 'module_pci_driver로 PCI 드라이버의 등록·해제 연결을 생성합니다. 설명 메타데이터는 별도 기능 없는 SR-IOV PF stub,라이선스는 GPL입니다. 앞서 본 pci-stub.c는 id_table=NULL과 초기 ids 문자열 파싱을 갖지만 이 파일은 고정 ID 테이블과 sriov_configure 콜백을 갖습니다. 이 파일에는 ids 매개변수 파서,별도 remove 함수,driver_managed_dma 지정이 없습니다. 드라이버 코어가 일반적으로 제공하는 기능까지 없다고 확대 해석하지는 않습니다.'),
        ('전체 범위와 실행 한계', '목적 주석,두 include,한 ID와 sentinel,모듈 테이블,probe,드라이버 구조체,등록 매크로 및 메타데이터 전체를 대조했습니다. 선언적 테이블이 대상 장치를 고르고 함수 포인터가 공통 기능을 연결하는 구조를 학습합니다. 실제 PF 바인딩,VF 생성·제거 또는 모듈 로드는 실행하지 않았습니다.')
    ], questions=[
        ('이 파일의 고정 매칭 목록에서 실제 장치 항목은 몇 개인가?', '1개이며 마지막0 항목은 종료 표시다', '2개이며 마지막0도 일반 장치 ID다', 'AMAZON의0x0053 항목 뒤 {0}이 있습니다. sentinel을 실제 지원 장치로 세면 테이블의 범위를 잘못 해석하게 됩니다.'),
        ('probe가 성공하면 이 본문이 VF 개수를 직접 설정한 것인가?', '아니다. probe는 로그와0 반환뿐이다', '그렇다. probe가 항상 최대 VF를 생성한다', '실제 구성은 sriov_configure에 연결한 외부 pci_sriov_configure_simple 경로의 역할입니다. 바인딩 성공과 VF 생성 요청을 구분해야 합니다.'),
        ('일반 pci-stub와 이 PF stub의 명시적 연결 차이는?', 'PF stub은 고정 ID 테이블과 sriov_configure 콜백을 지정한다', '둘 다 반드시 id_table=NULL이고 같은 ids 파서를 포함한다', '이 파일에는 문자열 파서가 없고 목록 주소와 공통 SR-IOV 구성 함수가 구조체에 지정됩니다. 이름이 stub이라는 이유로 구현을 같다고 가정하면 안 됩니다.')
    ]
)]
