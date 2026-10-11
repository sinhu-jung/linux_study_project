"""Whole-file top-level PCI Kbuild selections and ordering."""
ROWS = [dict(
    path='drivers/pci/Makefile', title='PCI 상위 빌드: 공통 객체·조건 범위·초기화 순서',
    intro='상위 PCI Makefile의 모든 객체·디렉터리와 디버그 플래그를 대조합니다.',
    principle='조건부 블록의 범위와 목록 순서는 빌드 그래프의 의미를 결정합니다.',
    use='설정과 빌드 대상의 매핑, 의존 계층, 초기화 순서와 전처리 플래그를 학습합니다.',
    area='Kbuild · PCI · 조건부 빌드 · 초기화 · 디버그',
    sections=[
        ('PCI 공통 객체 전체', 'GPL-2.0 Makefile은 CONFIG_PCI로 access.o,bus.o,probe.o,host-bridge.o,remove.o,pci.o,pci-driver.o,search.o,rom.o,setup-res.o,irq.o,vpd.o,setup-bus.o,vc.o,mmap.o,devres.o의16개 객체를 선택합니다. 줄 끝 역슬래시는 같은 논리 줄을 이어주는 것으로 별도 조건을 추가하지 않습니다. 이전에 작성한 검색·제거·ROM·IRQ·mmap 자료가 이 공통 선택 묶음에 연결됩니다.'),
        ('PCI 하위 디렉터리', 'CONFIG_PCI는 msi/,pcie/,pwrctl/도 각각 추가합니다. 디렉터리를 포함한다고 안의 모든 선택적 기능이 자동으로 활성화되는 것은 아니며 하위 Makefile의 조건을 확인해야 합니다. obj 목록은 빌드 대상을 정하고 실제 장치 탐색이나 드라이버 probe를 직접 실행하지 않습니다.'),
        ('ifdef PCI 안의 네 선택', 'ifdef CONFIG_PCI 안에서 PROC_FS→proc.o,SYSFS→pci-sysfs.o와 slot.o,ACPI→pci-acpi.o,GENERIC_PCI_IOMAP→iomap.o를 추가합니다. 따라서 이 블록에서는 PCI의 존재와 해당 개별 설정이 함께 중요합니다. SYSFS가 두 객체를 같은 줄에서 선택하는 반면 PROC_FS는 proc.o 하나입니다. endif 뒤 항목까지 이 텍스트 블록 안에 있다고 해석하면 안 됩니다.'),
        ('독립된 기능 선택 앞부분', '블록 밖에서 OF→of.o,PCI_QUIRKS→quirks.o,HOTPLUG_PCI→hotplug/,PCI_ATS→ats.o,PCI_IOV→iov.o,PCI_BRIDGE_EMUL→pci-bridge-emul.o,PCI_LABEL→pci-label.o,X86_INTEL_MID→pci-mid.o,PCI_SYSCALL→syscall.o입니다. 모든 설정 이름에는 CONFIG_ 접두사가 붙습니다. 실제 허용 구성은 Kconfig 의존도 적용되므로 이 위치만으로 PCI 없이 모든 객체가 유효하게 빌드된다고 단정할 수 없습니다.'),
        ('독립된 기능 선택 뒷부분', 'PCI_STUB→pci-stub.o,PCI_PF_STUB→pci-pf-stub.o,PCI_ECAM→ecam.o,PCI_P2PDMA→p2pdma.o,XEN_PCIDEV_FRONTEND→xen-pcifront.o,VGA_ARB→vgaarb.o,PCI_DOE→doe.o,PCI_DYNAMIC_OF_NODES→of_property.o,PCI_NPEM→npem.o입니다. OF의 of.o와 동적 OF 노드용 of_property.o는 다른 설정에 연결됩니다. 이름이 비슷하더라도 두 stub 역시 별도 객체입니다.'),
        ('endpoint 순서와 공통 방문', 'PCI_ENDPOINT로 endpoint/를 추가하고 그 뒤 controller/,switch/를 obj-y에 추가합니다. 주석은 endpoint 라이브러리가 사용자보다 먼저 초기화되어야 한다고 이 배치의 이유를 설명합니다. 디렉터리 순서를 무의미한 정렬 목록으로 취급하면 안 됩니다. 다만 개별 하위 파일의 모든 실행 순서까지 이 한 줄로 증명되는 것은 아니며 링크·초기화 단계도 함께 확인해야 합니다.'),
        ('디버그 플래그와 전체 범위', '마지막 subdir-ccflags-$(CONFIG_PCI_DEBUG) := -DDEBUG는 디렉터리 계층의 컴파일 플래그를 설정하는 줄입니다. 런타임에 DEBUG 문자열을 출력하거나 별도 debug.o를 추가하는 줄이 아닙니다. 모든16개 공통 객체,설정별 객체·디렉터리,ifdef 범위,endpoint 순서와 디버그 지정까지 대조했습니다. 실제 커널 빌드나 개별 기능의 동작 검증은 수행하지 않았습니다.')
    ], questions=[
        ('CONFIG_SYSFS가 ifdef PCI 블록 안에서 추가하는 객체는?', 'pci-sysfs.o와 slot.o', 'proc.o 하나', 'SYSFS 줄의 두 객체와 PROC_FS 줄의 proc.o는 서로 다릅니다. 설정별 사용자 인터페이스 구성을 구분해야 합니다.'),
        ('of.o와 of_property.o는 같은 설정에 묶이는가?', '아니다. 각각 OF와 PCI_DYNAMIC_OF_NODES에 연결된다', '그렇다. 둘 다 OF 한 줄에 함께 나열된다', '일반 OF 연동과 동적 속성 생성의 객체 선택이 분리되어 있습니다. 앞서 작성한 두 구현의 빌드 조건을 연결하는 근거입니다.'),
        ('endpoint 디렉터리가 controller보다 앞에 있는 이유로 주석이 제시하는 것은?', 'endpoint 라이브러리를 사용자보다 먼저 초기화하기 위해서다', '파일 이름을 사전순으로 정렬하기 위해서다', '원문은 초기화 순서를 명시합니다. 빌드 목록 순서가 모두 임의라고 가정하지 않아야 합니다.'),
        ('PCI_DEBUG 줄은 어떤 종류의 설정인가?', '하위 디렉터리에도 적용되는 컴파일 플래그 -DDEBUG 지정', '실행 중 모든 IRQ를 켜는 하드웨어 명령', 'subdir-ccflags는 빌드 플래그 변수입니다. 객체 추가나 런타임 장치 조작 코드와 다릅니다.'),
        ('ifdef PCI가 끝난 뒤의 OF 줄을 해석할 때 필요한 주의는?', 'Makefile 블록 범위와 별도 Kconfig 의존성을 구분한다', '이 위치만으로 PCI와 무관한 모든 구성이 허용된다고 확정한다', '텍스트 조건 밖이라는 사실은 설정 시스템의 전체 제약이 없다는 뜻이 아닙니다. 빌드 선택과 구성 유효성은 관련 파일을 함께 봐야 합니다.')
    ]
)]
