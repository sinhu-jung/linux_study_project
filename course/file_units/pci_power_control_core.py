"""Whole-file PCI power control notification and asynchronous rescan core."""
ROWS = [dict(
    path='drivers/pci/pwrctl/core.c', title='PCI 전원 제어 코어: notifier·비동기 rescan·device link',
    intro='알림 콜백,작업 큐,ready 수명과 관리형 wrapper 전체를 분석합니다.',
    principle='비동기 작업의 요청 성공은 장치 발견·바인딩 완료와 다르며 알림 해제와 작업 취소도 별개입니다.',
    use='container_of,이벤트 분기,생산자·소비자 의존 관계,작업 큐와 정리 범위를 학습합니다.',
    area='PCI · 전원 관리 · notifier · workqueue · 비동기 수명',
    sections=[
        ('알림 대상 판정', 'GPL-2.0-only 파일은 device,export,kernel,pci,pci-pwrctl,property,slab을 포함합니다. pci_pwrctl_notify는 내장 nb에서 container_of로 pwrctl을 구하고 data를 device로 봅니다. dev_fwnode(dev)와 dev_fwnode(pwrctl->dev)가 다르면 NOTIFY_DONE입니다. 문자열 이름 비교가 아니라 펌웨어 노드 포인터 동일성 비교이며 둘 다 NULL인 경우를 별도로 거부하는 조건은 없습니다.'),
        ('장치 추가와 노드 재사용', 'BUS_NOTIFY_ADD_DEVICE이면 dev->of_node_reused=true입니다. 주석은 같은 DT 노드를 사용하는 전원 제어 platform 장치와 나중에 생긴 PCI 장치가 핀 설정을 두 번 바인딩하지 않도록 한다고 설명합니다. 이 경로에서 OF 노드 자체를 새로 만들거나 전원을 직접 켜지는 않습니다. 같은 노드의 두 device 객체를 구분해 보는 사례입니다.'),
        ('드라이버 바인딩과 의존 링크', 'BOUND_DRIVER이면 device_link_add(dev,pwrctl->dev,DL_FLAG_AUTOREMOVE_CONSUMER)의 결과를 pwrctl->link에 저장하고 NULL이면 로그만 남깁니다. PCI 장치가 consumer이고 전원 제어 장치가 supplier인 인수 순서입니다. UNBOUND_DRIVER이면 link가 있을 때 device_link_remove(dev,pwrctl->dev)를 호출합니다. 이후 link=NULL 대입은 이 본문에 없습니다. 모든 알림 경로는 NOTIFY_DONE이며 링크 실패를 별도 오류 반환으로 전파하지 않습니다.'),
        ('작업 큐와 rescan 대상', 'rescan_work_func는 내장 work에서 pwrctl을 복원하고 pci_lock_rescan_remove 아래 to_pci_dev(pwrctl->dev->parent)->bus를 rescan한 뒤 unlock합니다. parent가 PCI 장치라는 전제와 해당 bus가 대상이라는 점이 중요합니다. 이 함수는 parent를 검사하거나 다른 버스를 전역 검색하지 않습니다. pci_rescan_bus 반환값도 여기서 검사하지 않습니다.'),
        ('초기화와 ready 요청', 'pci_pwrctl_init은 dev를 저장하고 INIT_WORK로 콜백을 연결합니다. 전체 구조체를 memset하거나 link/nb의 모든 필드를 초기화하는 본문은 아닙니다. set_ready는 dev가 NULL이면 -ENODEV,그 외에는 nb.notifier_call을 설정하고 PCI 버스 notifier를 등록합니다. 등록 오류는 반환하고 성공하면 schedule_work 후0입니다. schedule_work의 반환값은 검사하지 않습니다. 문서도0이 발견 완료가 아니라 비동기 rescan 시작을 뜻한다고 명시합니다.'),
        ('unset의 정리 범위', 'unset_ready는 bus_unregister_notifier만 호출합니다. 주석은 전원 제어 장치 detach 시 소비자 PCI 장치가 이미 unbind되어야 하므로 여기서 링크를 별도로 삭제할 필요가 없다고 설명합니다. 이 본문에는 cancel_work_sync,flush_work,PCI 장치 제거,전원 끄기 호출이 없습니다. notifier 해제만 보고 이미 예약한 작업이 취소되거나 완료되었다고 단정하면 안 됩니다. 완전한 수명 안전성 판단은 호출자와 장치 코어 계약도 확인해야 합니다.'),
        ('관리형 등록과 rollback 범위', 'devm unset 어댑터는 void *data를 pwrctl로 받아 일반 unset을 호출합니다. devm set_ready는 먼저 일반 set_ready를 실행하고 성공하면 devm_add_action_or_reset에 어댑터를 등록합니다. 등록 실패 시 어댑터가 실행되어 notifier는 해제되지만 앞서 schedule한 작업을 이 어댑터가 명시적으로 취소하지는 않습니다. 관리형이라는 이름만으로 모든 부수 효과가 자동 롤백된다고 확대하면 안 됩니다.'),
        ('전체 범위와 한계', 'notifier,rescan,init,set/unset,관리 어댑터와 wrapper의 일곱 함수,네 공개 GPL export,작성자·설명·GPL 메타데이터를 대조했습니다. 큐 예약과 실행 완료,알림 등록과 장치 수명 의존성을 관련 CS 주제로 연결했습니다. 실제 장치 전원,rescan,동시 작업 취소나 커널 빌드는 수행하지 않았습니다.')
    ], questions=[
        ('set_ready가0이면 PCI 드라이버 바인딩도 완료되었는가?', '아니다. 비동기 rescan 작업을 예약한 뒤 반환한다', '그렇다. 모든 장치 탐색과 probe가 끝날 때까지 기다린다', 'schedule_work 뒤 바로 반환하며 문서도 발견 완료가 아니라고 명시합니다. 비동기 요청 성공과 최종 결과를 구분해야 합니다.'),
        ('device_link_add의 consumer와 supplier는?', 'PCI 장치 dev가 consumer,전원 제어 pwrctl->dev가 supplier다', '전원 제어 장치가 consumer이고 PCI 장치가 supplier다', '호출 인수의 순서가 dev,pwrctl->dev입니다. 전원 공급 준비와 장치 사용의 의존 방향을 표현합니다.'),
        ('unset_ready가 예약된 work를 동기적으로 취소하는가?', '아니다. 본문에는 notifier 해제만 있다', '그렇다. cancel_work_sync를 호출한다', '이 파일에서 알림 등록 수명과 작업 큐 수명은 서로 다른 경로입니다. 정리 함수 이름으로 없는 동기화를 추정하면 안 됩니다.'),
        ('링크 생성 실패가 notifier의 음수 오류 반환으로 전파되는가?', '아니다. 로그 후 NOTIFY_DONE을 반환한다', '그렇다. 항상 -ENOMEM을 반환한다', 'link=NULL이면 dev_err를 호출하지만 최종 반환은 변하지 않습니다. 관측 로그와 호출자 오류 계약을 구분해야 합니다.'),
        ('pci_pwrctl_init이 구조체 전체를0으로 초기화하는가?', '아니다. dev 저장과 work 초기화만 수행한다', '그렇다. link와 모든 notifier 필드를 memset한다', '함수 본문에 두 작업만 있습니다. 호출자의 저장소 초기화 전제와 helper가 실제 수행하는 초기화를 별도로 확인해야 합니다.'),
        ('관리 작업 등록 실패 시 adapter가 모든 rescan 부수 효과까지 되돌리는가?', '아니다. adapter는 일반 unset을 호출해 notifier만 해제한다', '그렇다. 이미 발견된 장치도 제거하고 work도 취소한다', 'or_reset은 지정한 함수를 실행할 뿐 그 함수에 없는 정리를 만들어내지 않습니다. rollback의 범위는 콜백 본문으로 판정해야 합니다.')
    ]
)]
