"""Whole-file PCI IRQ requests, swizzling, mapping and INTx mask control."""
ROWS = [dict(
    path='drivers/pci/irq.c', title='PCI IRQ 처리: 모듈러 swizzle·콜백·INTx 잠금',
    intro='IRQ 요청·해제, 계층별 pin 변환, 할당과 마스크 조절 및 weak 기본 함수를 전체 분석합니다.',
    principle='장치 내부 pin, 장치 상대 vector index, 시스템 IRQ 번호는 서로 다른 식별자입니다.',
    use='모듈러 산술, 트리 상향 순회, 함수 포인터, 문자열 소유권과 잠금 안의 조건부 갱신을 학습합니다.',
    area='PCI · 인터럽트 · 동시성 · 자원 수명 · 모듈러 연산',
    sections=[
        ('IRQ 요청과 이름 소유권', 'GPL-2.0 파일의 pci_request_irq는 dev,nr,handler,thread_fn,dev_id와 가변 인수 이름을 받습니다. nr는 0 기반 장치 상대 vector index이며 pci_irq_vector로 시스템 번호로 변환합니다. 기본 irqflags는 IRQF_SHARED이고 handler가 NULL이면 IRQF_ONESHOT을 추가합니다. va_start/kvasprintf/va_end로 이름을 할당하고 실패하면 -ENOMEM입니다. request_threaded_irq 실패 시 이름을 해제하고 결과를 반환합니다. 성공 시 이름을 여기서 해제하지 않습니다. 문서는 dev_id가 NULL이 아니며 전역적으로 고유해야 한다고 요구하지만 이 wrapper에 별도 검사는 없습니다.'),
        ('해제 계약', 'pci_free_irq는 같은 vector 변환과 dev_id로 free_irq를 호출하고 그 반환값을 kfree해 요청 때 만든 이름을 정리합니다. 주석은 호출 전 장치 측 인터럽트를 비활성화할 책임이 호출자에게 있고 실행 중인 IRQ가 완료될 때까지 기다리며 인터럽트 문맥에서 호출하면 안 된다고 설명합니다. 이 함수가 장치 자체의 인터럽트 발생원을 먼저 끄는 코드는 없습니다. 요청 직후부터 handler와 thread_fn이 호출될 수 있다는 요청 함수의 계약과 함께 수명을 읽어야 합니다.'),
        ('한 단계 swizzle', 'pci_swizzle_interrupt_pin은 ARI 활성 버스이면 slot=0, 아니면 PCI_SLOT(devfn)으로 구합니다. 반환식은 (((pin-1)+slot)%4)+1입니다. 1..4 pin을 0..3으로 옮겨 슬롯만큼 회전한 뒤 다시 1..4로 되돌립니다. 함수 자체는 입력 pin의 범위를 검사하지 않으므로 문서의 1..4 전제를 지켜야 합니다. ARI에서는 정상 pin이 그대로 보존됩니다.'),
        ('루트까지의 두 순회', 'pci_get_interrupt_pin은 dev->pin이 0이면 -1을 반환하고 출력 bridge를 쓰지 않습니다. 나머지는 루트 버스에 도달할 때까지 현재 장치로 swizzle하고 bus->self로 올라가 최종 dev를 *bridge에 저장합니다. pci_common_swizzle은 *pinp에서 시작해 같은 순회를 하고 변환 pin을 *pinp에 쓰며 반환값은 최상단 장치의 슬롯입니다. 후자에는 pin=0 검사도 없습니다. 주석의 3=INTD 표기는 앞 함수의 1=INTA..4=INTD 설명과 다른 오기이며 실제 계산은 네 pin의 순환입니다. 깊이 H에 대한 순회 횟수는 O(H), 추가 저장 공간은 O(1)입니다.'),
        ('IRQ 할당 콜백과 보정', 'pci_assign_irq는 호스트 브리지를 찾아 map_irq가 없으면 현재 dev->irq를 바꾸지 않고 반환합니다. 있으면 PCI_INTERRUPT_PIN을 읽는데 반환 상태는 검사하지 않습니다. pin>4는 1로 보정합니다. pin이 0이 아니면 선택적인 swizzle_irq가 pin을 바꾸고 slot을 반환하며, 콜백이 없으면 u8 slot=-1의 초기값 255를 map_irq에 넘기므로 주석대로 매핑 함수가 slot을 무시해야 합니다. map_irq 결과 중 -1만 0으로 바꾸며 모든 음수 오류를 정규화하는 코드는 아닙니다.'),
        ('할당 결과 기록', 'pin=0이면 irq 초기값 0이 유지됩니다. 최종 irq를 dev->irq에 대입하고 로그를 남긴 뒤 PCI_INTERRUPT_LINE에 바이트로 씁니다. 이 쓰기의 반환값도 검사하지 않습니다. 주석은 장치 동작을 위한 IRQ 선택이 아니라 드라이버가 실제 IRQ를 알도록 기록한다고 설명합니다. 시스템 IRQ를 보관하는 dev->irq와 바이트 설정 레지스터의 표현 폭도 동일하다고 가정하면 안 됩니다.'),
        ('command/status 한 번 읽기', 'pci_check_and_set_intx_mask는 PCI_COMMAND가 4바이트 정렬되고 STATUS가 바로 다음 2바이트 위치라는 전제를 BUILD_BUG_ON으로 검사합니다. pci_lock을 raw_spin_lock_irqsave로 잡아 로컬 IRQ 상태를 보존한 뒤 bus->ops->read로 4바이트를 읽습니다. 상위16비트의 PCI_STATUS_INTERRUPT를 bool irq_pending으로 추출하고 하위16비트를 origcmd로 사용합니다. 버스 read/write의 오류 반환은 이 함수에서 확인하지 않습니다.'),
        ('마스크 조건과 쓰기 최소화', '요청 mask와 irq_pending이 다르면 mask_updated=false로 끝내고 설정을 쓰지 않습니다. 같으면 origcmd에서 INTX_DISABLE을 지운 뒤 mask=true일 때만 다시 세웁니다. 새 값이 기존과 다를 때에만 2바이트 COMMAND 쓰기를 합니다. 잠금은 읽기·조건 검사·쓰기 전체를 감싸고 모든 경로에서 irqrestore로 풉니다. true 반환은 조건을 만족했다는 의미이며 실제 write가 반드시 수행되었다는 의미는 아닙니다.'),
        ('공개 wrapper와 weak 기본값', 'check_and_mask_intx는 pending일 때만 비활성 비트를 설정하도록 true를 넘기고 check_and_unmask_intx는 pending이 없을 때만 해제하도록 false를 넘깁니다. 두 wrapper와 common_swizzle은 GPL export이며 request/free_irq는 일반 export입니다. weak pcibios_penalize_isa_irq와 pcibios_free_irq는 빈 본문, weak pcibios_alloc_irq는 0입니다. 아키텍처가 재정의할 수 있는 기본 구현이며 기본 alloc의 성공 반환이 별도 IRQ 자원 할당을 수행했다는 증거는 아닙니다.'),
        ('전체 검토 범위', '모든 요청·해제, 세 pin 처리 함수, assign_irq, 내부 마스크 도우미와 두 wrapper, 세 weak 기본 함수를 대조했습니다. OF 구현의 map_irq 콜백이 이 할당 경로에 연결되는 점과 오류 반환 의미의 차이를 반영했습니다. 실제 인터럽트 발생·동시 실행·PCI 설정 공간 접근이나 커널 빌드는 수행하지 않았습니다.')
    ], questions=[
        ('slot=3인 장치의 pin=2를 한 단계 swizzle하면?', '1', '5', '((2-1+3)%4)+1=1입니다. 네 개 선의 순환이므로 단순 덧셈 결과를 pin 번호로 반환하지 않습니다.'),
        ('IRQ 요청에서 handler=NULL이면 어떤 플래그가 추가되는가?', '기본 SHARED에 ONESHOT이 추가된다', 'SHARED를 지우고 반드시 전용 IRQ로 바뀐다', '초깃값은 IRQF_SHARED이고 조건문은 IRQF_ONESHOT을 OR합니다. 다른 드라이버와 공유될 수 있다는 계약은 유지됩니다.'),
        ('pci_free_irq에서 kfree하는 대상은?', 'free_irq가 반환한 요청 이름 포인터', '호출자가 전달한 dev_id 자체', '본문은 kfree(free_irq(...,dev_id))입니다. 식별용 쿠키와 요청 시 할당한 이름 메모리를 구분해야 합니다.'),
        ('pci_get_interrupt_pin에서 dev->pin=0이면 bridge 출력은?', '쓰지 않고 -1을 반환한다', '항상 NULL로 초기화한다', '조기 반환이 *bridge 대입보다 앞에 있습니다. 실패 시 출력 인수가 초기화되었다고 가정하면 안 됩니다.'),
        ('map_irq가 없으면 pci_assign_irq가 dev->irq를 0으로 지우는가?', '아니다. 해당 대입 전에 반환한다', '그렇다. 지역 irq=0이 곧바로 장치에 반영된다', '지역 변수 초기화와 객체 필드 대입은 다릅니다. map_irq 검사 실패는 마지막 dev->irq 대입까지 도달하지 않습니다.'),
        ('mask=true이고 pending=false이면 INTX_DISABLE을 설정하는가?', '아니다. false를 반환하고 쓰지 않는다', '그렇다. 요청 mask 값만 보고 항상 쓴다', 'mask!=irq_pending이면 갱신을 거부합니다. 마스킹은 실제 pending인 장치에만, 언마스킹은 pending이 없는 장치에만 허용하는 조건입니다.'),
        ('INTx 마스크 함수가 true이면 설정 공간 쓰기가 반드시 있었는가?', '아니다. 이미 원하는 비트 상태면 쓰기를 생략한다', '그렇다. true는 write 횟수 1을 의미한다', 'newcmd!=origcmd일 때만 write합니다. mask_updated는 요청과 pending 상태가 맞는지를 나타내며 실제 쓰기 호출 여부를 직접 나타내지 않습니다.'),
        ('map_irq가 -2를 반환하면 assign_irq가 반드시 0으로 바꾸는가?', '아니다. 코드가 특별 취급하는 값은 -1뿐이다', '그렇다. 모든 음수 값을 0으로 정규화한다', '조건식은 irq==-1입니다. 특정 콜백 규약을 위한 값 처리와 일반 음수 errno 처리로의 확대 해석을 구분해야 합니다.')
    ]
)]
