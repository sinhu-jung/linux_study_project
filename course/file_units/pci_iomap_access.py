"""Whole-file unmanaged PCI BAR mapping and conditional unmapping."""
ROWS = [dict(
    path='drivers/pci/iomap.c', title='PCI iomap: BAR 부분 범위·WC 제한·명시적 해제',
    intro='일반·WC 범위 매핑, 두 wrapper, 조건부 unmap과 문서 계약 전체를 분석합니다.',
    principle='관리형 장치 활성화를 사용했다고 모든 후속 매핑이 자동 관리되는 것은 아닙니다.',
    use='구간 자르기,0의 특별 의미,분기 우선순위,주소 공간 추상화와 자원 수명을 학습합니다.',
    area='PCI BAR · MMIO · PIO · 매핑 · 메모리 수명',
    sections=[
        ('일반 부분 매핑의 범위', 'GPL-2.0 파일은 pci.h,io.h,export.h를 포함합니다. pci_iomap_range는 resource 시작·길이·flags를 얻어 len<=offset 또는 start=0이면 NULL입니다. 나머지는 len에서 offset을 빼고 start에 offset을 더합니다. maxlen이0이 아니고 남은 len보다 작을 때만 len을 제한합니다. 따라서 maxlen=0은0바이트가 아니라 offset부터 끝까지라는 계약입니다. start+offset의 오버플로나 BAR 번호 범위를 이 본문에서 별도 검사하지 않습니다.'),
        ('PIO와 MMIO 선택', '일반 함수는 IORESOURCE_IO를 먼저 검사해 __pci_ioport_map(dev,start,len)을 반환하고,그다음 MEM이면 ioremap(start,len)을 반환합니다. 둘 다 아니면 NULL입니다. 반환값은 ioread/iowrite 계열 접근자가 사용할 __iomem 매핑 cookie라는 문서 계약입니다. 일반 메모리 포인터처럼 직접 읽어도 된다는 뜻은 아닙니다. IO와 MEM 비트가 동시에 있다면 이 본문의 분기 순서는 IO를 우선합니다.'),
        ('WC의 다른 허용 조건', 'pci_iomap_wc_range는 가장 먼저 IORESOURCE_IO면 NULL을 반환합니다. 그 뒤 길이·start 검사와 부분 범위 계산은 일반 함수와 같고 MEM이면 ioremap_wc를 호출합니다. 따라서 문서의 공통 주소 공간 설명만 보고 WC가 포트 I/O도 지원한다고 해석하면 안 됩니다. IO와 MEM이 동시에 있어도 먼저 거부합니다. 실제 write-combining의 아키텍처 동작은 ioremap_wc 구현 범위입니다.'),
        ('offset 없는 두 wrapper와 수명', 'pci_iomap은 일반 range 함수에 offset=0을, pci_iomap_wc는 WC range 함수에 offset=0을 넘깁니다. 모두 문서에서 pcim_enable_device를 사용했더라도 관리형 매핑이 아니라고 명시합니다. 일반 wrapper 문서는 자동 정리가 필요하면 pcim_iomap을 사용하라고 안내합니다. 여기에는 devm 정리 작업 등록이나 BAR resource 예약 코드가 없습니다. 일반 두 함수는 EXPORT_SYMBOL,WC 두 함수는 GPL export입니다.'),
        ('조건부 pci_iounmap', 'ARCH_WANTS_GENERIC_PCI_IOUNMAP일 때만 이 파일이 pci_iounmap을 정의합니다. ARCH_HAS_GENERIC_IOPORT_MAP도 있으면 PCI_IOBASE와 p를 uintptr_t로 바꾸어 start<=addr<start+IO_SPACE_LIMIT이면 그대로 반환합니다. 그 밖은 iounmap(p)입니다. 내부 조건이 없으면 곧바로 iounmap합니다. dev 인수는 본문에서 사용하지 않습니다. 상한은 미포함이며 코드에 +1은 없습니다.'),
        ('아키텍처 전제와 전체 범위', '주석은 GENERIC_IOMAP 구성의 unmap이 lib/iomap.c에서 제공되며 다른 아키텍처는 자체 구현을 제공할 수 있다고 설명합니다. 여기의 기본 구현은 포트 매핑이 고정 구간에 있고 ioport_unmap이 필요 없다는 전제를 갖습니다. 역사적 호환 이유에 대한 주석과 실제 조건부 본문을 구분했습니다. 다섯 함수,모든 문서·조건·export를 대조했으며 실제 BAR 접근,WC 성능이나 커널 빌드는 수행하지 않았습니다.')
    ], questions=[
        ('BAR 길이4096,offset1024,maxlen0이면 남은 매핑 길이는?', '3072바이트', '0바이트', 'len-offset=3072이고 maxlen=0이면 길이 제한 분기를 건너뜁니다. 0은 남은 전체 범위라는 특별 의미입니다.'),
        ('offset이 BAR 길이와 정확히 같으면?', 'NULL을 반환한다', '길이0인 유효 매핑을 만든다', '초기 검사는 len<=offset입니다. 끝 경계에서 시작하는 빈 범위를 허용하지 않습니다.'),
        ('WC 함수에 IORESOURCE_IO 자원을 주면?', 'NULL을 반환한다', '일반 ioport 매핑으로 자동 대체한다', 'WC 함수는 IO 플래그를 가장 먼저 거부합니다. 일반 함수의 PIO 지원과 WC 함수의 허용 범위는 다릅니다.'),
        ('pcim_enable_device 뒤 pci_iomap을 호출하면 자동 정리가 보장되는가?', '아니다. 이 매핑 API는 관리형이 아니라고 명시되어 있다', '그렇다. 장치 활성화 방식이 이후 모든 할당을 관리형으로 바꾼다', '장치 활성화와 매핑의 수명 계약은 별개입니다. 문서는 자동 정리용으로 pcim_iomap을 따로 안내합니다.'),
        ('조건부 unmap에서 addr=start+IO_SPACE_LIMIT는 생략 구간 안인가?', '아니다. 상한 비교가 엄격한 미만이다', '그렇다. 상한까지 포함한다', '실제 비교는 addr<start+IO_SPACE_LIMIT입니다. 시작 포함·끝 미포함 구간의 경계를 그대로 읽어야 합니다.')
    ]
)]
