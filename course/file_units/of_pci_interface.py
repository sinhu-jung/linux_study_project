"""Whole-file OF PCI declaration and disabled-configuration contracts."""
ROWS = [dict(
    path='include/linux/of_pci.h', title='OF PCI 인터페이스: 독립적인 설정 조건과 반환 계약',
    intro='헤더 전체의 네 API와 두 조건부 컴파일 블록을 대조합니다.',
    principle='같은 헤더에 있는 API라도 활성화 조건과 비지원 반환값은 서로 다릅니다.',
    use='전방 선언, 논리곱 조건, 포인터·오류 코드·IRQ 번호의 구분을 학습합니다.',
    area='PCI · 장치 트리 · 인터럽트 · 조건부 컴파일 · 인터페이스 설계',
    sections=[
        ('의존성과 전방 선언', 'GPL-2.0 표기와 __OF_PCI_H guard 아래 linux/types.h와 linux/errno.h를 포함합니다. pci_dev와 device_node는 전방 선언만 합니다. 포인터 인수를 선언할 때 구조체의 필드 배치 전체를 알 필요가 없으므로 이 헤더 안에는 해당 구조체 정의가 없습니다. u8은 IRQ API의 slot과 pin 타입에 사용됩니다.'),
        ('PCI 조회의 활성 조건', '첫 블록은 IS_ENABLED(CONFIG_OF) && IS_ENABLED(CONFIG_PCI)입니다. 두 조건이 모두 참일 때 find_child_device, get_devfn, check_probe_only의 외부 선언을 제공합니다. find_child_device는 부모 노드와 unsigned int devfn을 받아 device_node 포인터를 반환하고 get_devfn은 노드 포인터에서 int 결과를 반환합니다. 이 선언만으로 검색 순서, devfn 추출 알고리즘, 반환 노드의 참조 소유권을 결정할 수는 없습니다.'),
        ('조회 비지원 경로', '첫 조건이 거짓이면 find_child_device는 입력을 사용하지 않고 NULL을 반환하며 get_devfn은 -EINVAL을 반환합니다. 포인터 결과 부재와 음수 오류 코드는 서로 다른 반환 타입에 맞춘 계약입니다. 비활성 get_devfn의 -EINVAL이 전달된 노드 내용을 검사했다는 의미는 아닙니다. 본문에는 검사가 전혀 없습니다.'),
        ('probe 정책 함수', 'check_probe_only는 인수도 반환값도 없는 void API입니다. 활성 구성에서는 외부 구현을 선언하고 비활성 구성에서는 빈 static inline 본문을 제공합니다. 따라서 이 헤더의 비지원 경로는 정책 값을 읽거나 갱신하지 않습니다. 활성 구현이 어떤 속성이나 전역 상태를 사용하는지는 이 파일 밖에서 확인해야 합니다.'),
        ('독립적인 IRQ 조건', '두 번째 블록은 첫 블록의 #endif 뒤에 있으며 IS_ENABLED(CONFIG_OF_IRQ)만 검사합니다. 활성일 때 of_irq_parse_and_map_pci(const struct pci_dev *dev, u8 slot, u8 pin)를 int 반환 외부 함수로 선언합니다. 첫 블록의 OF와 PCI 논리곱 안에 중첩된 조건이 아닙니다. 실제로 허용되는 커널 설정 조합은 별도 Kconfig 제약도 확인해야 하며 이 헤더의 전처리 조건만으로 모두 가능하다고 주장할 수 없습니다.'),
        ('IRQ 대체 함수와 전체 범위', 'OF_IRQ 비활성에서는 parse_and_map_pci가 아무 매핑 작업 없이 0을 반환합니다. 이 값은 이 본문에서 IRQ 파싱이나 매핑이 성공했다는 증거가 아닙니다. get_devfn의 -EINVAL과 혼동해 모든 비지원 int API가 음수 오류를 준다고 가정하면 안 됩니다. 네 API의 활성 선언과 비활성 본문, 두 조건, 포함 파일과 guard 전체를 대조했으며 실제 PCI 탐색·IRQ 매핑이나 구성별 커널 빌드는 실행하지 않았습니다.')
    ], questions=[
        ('PCI 조회 API의 활성 조건과 IRQ API의 활성 조건은 같은가?', '아니다. 첫 블록은 OF와 PCI의 논리곱, 두 번째는 OF_IRQ이다', '그렇다. IRQ 블록도 첫 논리곱 안에 중첩되어 있다', '첫 #endif가 조회 블록을 닫은 뒤 새 #if가 나옵니다. 전처리 블록의 경계를 읽어야 하며 Kconfig에서의 설정 의존 관계와도 구분해야 합니다.'),
        ('첫 블록 비활성 시 find_child_device와 get_devfn은 무엇을 반환하는가?', '각각 NULL과 -EINVAL', '둘 다 정수 0이며 정상 장치를 의미한다', '전자는 포인터를, 후자는 int를 반환합니다. 비활성 본문은 입력 노드를 검사하거나 탐색하지 않고 해당 상수를 바로 돌려줍니다.'),
        ('OF_IRQ 비활성에서 반환된 0으로 실제 IRQ 매핑 수행을 입증할 수 있는가?', '없다. 대체 함수는 반환문만 실행한다', '있다. 본문이 IRQ 테이블을 만들고 성공을 보고한다', '코드에는 파싱, 할당, 등록이 없습니다. 반환값의 표면적 형태와 실제 부수 효과를 구별해야 합니다.'),
        ('이 헤더만으로 활성 find_child_device의 검색 알고리즘과 참조 소유권을 확정할 수 있는가?', '없다. 활성 경로는 함수 선언만 제공한다', '있다. 전방 선언이 깊이 우선 탐색과 참조 증가를 보장한다', '전방 선언은 타입 이름을 사용할 수 있게 할 뿐 구현을 제공하지 않습니다. 알고리즘과 자원 수명 계약은 실제 구현 및 관련 문서에서 확인해야 합니다.')
    ]
)]
