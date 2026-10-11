"""Whole-file PCI controller Kbuild object and subdirectory selection."""
ROWS = [dict(
    path='drivers/pci/controller/Makefile', title='PCI 컨트롤러 빌드: 설정별 객체와 ACPI 우회 선택',
    intro='모든 객체·하위 디렉터리 항목과 마지막 중첩 조건을 대조합니다.',
    principle='빌드 목록은 파일 선택을 정의하며 실제 장치 매칭과 실행 시 probe는 별도 단계입니다.',
    use='선언적 의존 관계, 조건 조합, 공통 객체 재사용과 빌드·실행 단계 구분을 학습합니다.',
    area='Kbuild · PCI 컨트롤러 · 조건부 빌드 · ACPI · 모듈',
    sections=[
        ('Kbuild 형태', 'GPL-2.0 Makefile은 obj-$(CONFIG_...) += 대상으로 선택 결과를 누적합니다. 설정이 y이면 obj-y,m이면 obj-m에 들어가는 방식이며 실제 m 허용 여부와 의존성은 Kconfig를 확인해야 합니다. 이 파일에는 컴파일러 명령을 직접 실행하는 recipe나 장치 탐색 코드는 없습니다. 객체 목록에 이름이 있다는 사실만으로 현재 구성에서 해당 드라이버가 활성이라고 할 수 없습니다.'),
        ('초기 컨트롤러와 하위 디렉터리', 'PCIE_CADENCE는 cadence/를 선택합니다. PCI_FTPCI100→pci-ftpci100.o,PCI_IXP4XX→pci-ixp4xx.o,PCI_HYPERV→pci-hyperv.o,PCI_HYPERV_INTERFACE→pci-hyperv-intf.o,PCI_MVEBU→pci-mvebu.o,PCI_AARDVARK→pci-aardvark.o,PCI_TEGRA→pci-tegra.o,PCI_RCAR_GEN2→pci-rcar-gen2.o입니다. 각 설정 이름에는 CONFIG_ 접두사가 붙습니다. Hyper-V 본체와 interface는 이 목록에서 별도 선택입니다.'),
        ('R-Car와 호스트 공통 코드', 'PCIE_RCAR_HOST는 pcie-rcar.o와 pcie-rcar-host.o를,PCIE_RCAR_EP는 같은 pcie-rcar.o와 pcie-rcar-ep.o를 추가합니다. 공통 객체를 두 경로가 참조하는 구조입니다. PCI_HOST_COMMON→pci-host-common.o,PCI_HOST_GENERIC→pci-host-generic.o,PCI_HOST_THUNDER_ECAM→pci-thunder-ecam.o,PCI_HOST_THUNDER_PEM→pci-thunder-pem.o입니다. GENERIC을 선택하는 줄 자체가 COMMON도 선택하는 것은 아니므로 상호 의존은 Kconfig에서 확인해야 합니다.'),
        ('Xilinx·X-Gene·Versatile', 'PCIE_XILINX→pcie-xilinx.o,PCIE_XILINX_NWL→pcie-xilinx-nwl.o,PCIE_XILINX_CPM→pcie-xilinx-cpm.o,PCIE_XILINX_DMA_PL→pcie-xilinx-dma-pl.o입니다. PCI_V3_SEMI→pci-v3-semi.o,PCI_XGENE→pci-xgene.o,PCI_XGENE_MSI→pci-xgene-msi.o,PCI_VERSATILE→pci-versatile.o가 이어집니다. X-Gene 본체와 MSI 지원은 서로 다른 객체 항목입니다.'),
        ('iProc·Altera·Rockchip', 'PCIE_IPROC→pcie-iproc.o,PCIE_IPROC_MSI→pcie-iproc-msi.o,PCIE_IPROC_PLATFORM→pcie-iproc-platform.o,PCIE_IPROC_BCMA→pcie-iproc-bcma.o입니다. PCIE_ALTERA→pcie-altera.o,PCIE_ALTERA_MSI→pcie-altera-msi.o도 분리됩니다. PCIE_ROCKCHIP→pcie-rockchip.o,PCIE_ROCKCHIP_EP→pcie-rockchip-ep.o,PCIE_ROCKCHIP_HOST→pcie-rockchip-host.o가 각각 있습니다. 이 Makefile은 세 Rockchip 객체를 하나의 합성 객체로 묶는 -y 목록을 정의하지 않습니다.'),
        ('나머지 개별 객체', 'PCIE_MEDIATEK→pcie-mediatek.o,PCIE_MEDIATEK_GEN3→pcie-mediatek-gen3.o,VMD→vmd.o,PCIE_BRCMSTB→pcie-brcmstb.o,PCI_LOONGSON→pci-loongson.o,PCIE_HISI_ERR→pcie-hisi-error.o,PCIE_APPLE→pcie-apple.o,PCIE_MT7621→pcie-mt7621.o입니다. 각 이름은 별도 설정값으로 선택되며 파일 이름의 유사성만으로 공통 실행 경로나 같은 하드웨어 지원이라고 단정할 수 없습니다.'),
        ('무조건 방문하는 세 디렉터리', 'dwc/,mobiveil/,plda/는 obj-y에 직접 추가됩니다. 주석은 pcie-hisi.o quirk가 PCIE_DW 없이도 필요하다고 설명합니다. 하위 디렉터리를 빌드 탐색에 포함하는 것과 그 안의 모든 드라이버 객체를 무조건 링크하는 것은 다릅니다. 구체적인 내부 선택은 각 하위 Makefile과 소스의 조건을 확인해야 합니다.'),
        ('ACPI quirk 선택 경로', '마지막은 ifdef CONFIG_ACPI 안에 ifdef CONFIG_PCI_QUIRKS가 있고 두 조건 안에서 obj-$(CONFIG_ARM64)에 pci-thunder-ecam.o,pci-thunder-pem.o,pci-xgene.o를 추가합니다. 주석은 일반 ACPI pci_root.c가 비표준 ECAM 장치의 MCFG quirk를 사용할 수 있도록 개별 DT 드라이버 설정에만 의존하지 않으려는 목적을 설명합니다. 필요한 부분만 내부 ifdef로 빌드한다고도 명시합니다. 위의 개별 설정 경로와 이 추가 경로를 함께 확인해야 합니다.'),
        ('전체 범위와 한계', '모든 CONFIG별 객체,두 R-Car 다중 객체 줄,조건부 cadence/,세 obj-y 디렉터리,ACPI·QUIRKS 중첩 조건 및 주석 전체를 대조했습니다. 설정→빌드 대상의 매핑은 의존 그래프의 일부이며 최종 플랫폼 지원 판정은 Kconfig와 해당 소스까지 필요합니다. 실제 커널 빌드나 각 컨트롤러 실행은 수행하지 않았습니다.')
    ], questions=[
        ('R-Car host와 endpoint 선택이 공통으로 추가하는 객체는?', 'pcie-rcar.o', 'pci-host-generic.o', 'HOST 줄과 EP 줄 모두 pcie-rcar.o를 포함하고 각자 host 또는 ep 전용 객체를 더합니다.'),
        ('obj-y += dwc/이면 그 안의 모든 장치 드라이버가 무조건 활성인가?', '아니다. 하위 빌드 목록과 소스 조건을 추가로 확인해야 한다', '그렇다. 모든 하위 소스가 아무 조건 없이 링크된다', '디렉터리 방문과 개별 객체 선택은 별도 단계입니다. 주석은 특정 quirk가 필요해 디렉터리를 포함하는 이유를 설명합니다.'),
        ('개별 Thunder 설정 없이도 마지막 quirk 경로가 객체를 선택할 수 있는 조건은?', 'ACPI와 PCI_QUIRKS 조건 안에서 ARM64가 선택되는 경우', 'PCI_HOST_GENERIC 하나만 활성인 경우', '두 ifdef 안의 obj-$(CONFIG_ARM64)가 해당 객체를 추가합니다. 개별 DT 드라이버 설정만 보면 이 경로를 놓칩니다.'),
        ('이 Makefile의 GENERIC 줄 자체가 COMMON 설정까지 켜는가?', '아니다. 각 객체 줄은 별도이며 설정 의존은 다른 곳에서 확인한다', '그렇다. +=가 다른 CONFIG 값을 자동 변경한다', 'obj 목록 추가는 CONFIG 변수를 활성화하는 select 문장이 아닙니다. Kconfig의 의존 관계와 Kbuild의 객체 선택을 구분해야 합니다.'),
        ('X-Gene 본체와 MSI는 같은 한 객체 항목인가?', '아니다. pci-xgene.o와 pci-xgene-msi.o가 별도 설정에 연결된다', '그렇다. 본체 선택 줄이 MSI 객체까지 항상 추가한다', 'PCI_XGENE와 PCI_XGENE_MSI가 각각 다른 객체를 선택합니다. 실제 동시 선택 여부는 설정 의존을 함께 봐야 합니다.')
    ]
)]
