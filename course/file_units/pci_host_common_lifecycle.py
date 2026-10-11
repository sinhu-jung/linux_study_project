"""Whole-file common DT PCI host probe and removal integration."""
ROWS = [dict(
    path='drivers/pci/controller/pci-host-common.c', title='공통 PCI 호스트: ECAM 관리 작업과 probe/remove 연결',
    intro='두 내부 도우미와 공개 probe/remove 전체를 기존 ECAM·루트 제거 자료에 연결합니다.',
    principle='자원 획득을 관리형 해제 작업에 등록하는 시점과 실패 시 즉시 정리 여부를 함께 추적해야 합니다.',
    use='오류 포인터, 콜백 어댑터, 관리형 자원 수명과 잠금 안의 두 단계 제거를 학습합니다.',
    area='PCI 호스트 · ECAM · devres · probe · 자원 수명',
    sections=[
        ('파일 역할과 해제 어댑터', 'GPL-2.0 파일은 kernel,module,OF,OF address,OF PCI,pci-ecam,platform_device를 포함합니다. gen_pci_unmap_cfg는 void *를 pci_config_window *로 캐스팅해 pci_ecam_free에 전달하는 어댑터입니다. 관리 작업의 일반 포인터 콜백 형태를 ECAM 전용 해제 함수와 연결하며 이 함수에서 별도 객체를 할당하지 않습니다.'),
        ('설정 공간 입력과 버스 자원', 'gen_pci_init은 of_address_to_resource(dev->of_node,0,&cfgres)로 첫 주소 자원을 구합니다. 실패하면 missing reg 로그와 ERR_PTR(err)를 반환합니다. 해당 로그만으로 모든 실패 원인이 반드시 속성 부재라고 단정할 수는 없습니다. bridge->windows에서 IORESOURCE_BUS인 첫 항목을 찾고 없으면 ERR_PTR(-ENODEV)입니다. 이 함수가 창 목록을 새로 파싱하는 것은 아니며 이미 마련된 버스 자원을 사용합니다.'),
        ('생성 후 관리형 정리 등록', 'pci_ecam_create(dev,&cfgres,bus->res,ops)의 오류 포인터는 그대로 반환합니다. 성공하면 devm_add_action_or_reset에 해제 어댑터와 cfg를 등록합니다. 이 API는 작업 등록 실패 시 reset 동작으로 해제 콜백을 실행하므로 이 경로에서 별도의 pci_ecam_free를 중복 호출하지 않습니다. 등록 실패는 ERR_PTR(err),성공은 cfg입니다. ECAM 매핑 수명이 device의 관리 자원 정리와 연결되는 시점입니다.'),
        ('probe의 선행 조건과 저장', 'pci_host_common_probe는 of_device_get_match_data로 pci_ecam_ops를 얻고 NULL이면 -ENODEV입니다. devm_pci_alloc_host_bridge(dev,0) 실패면 -ENOMEM이며 성공한 bridge는 platform_set_drvdata로 저장합니다. 이후 of_pci_check_probe_only를 호출하므로 정책 확인은 ECAM 생성 이전입니다. 이 파일에는 probe 실패 때 drvdata를 명시적으로 NULL로 되돌리는 코드가 없습니다.'),
        ('호스트 코어로 넘기는 상태', 'gen_pci_init 실패는 PTR_ERR로 정수 오류를 반환합니다. 성공하면 bridge->sysdata=cfg,bridge->ops=(struct pci_ops *)&ops->pci_ops,bridge->msi_domain=true로 설정하고 pci_host_probe 결과를 그대로 반환합니다. const 테이블 안의 pci_ops 주소를 캐스팅해 저장하지만 여기서 테이블 내용을 수정하지는 않습니다. msi_domain 플래그 설정만으로 모든 장치의 MSI 벡터 할당이 완료되었다고 설명해서는 안 됩니다.'),
        ('remove 순서와 잠금', 'remove는 drvdata의 bridge를 가져와 pci_lock_rescan_remove를 잡고 stop_root_bus,remove_root_bus를 차례로 호출한 뒤 잠금을 풉니다. 중지를 먼저 마치고 제거한다는 앞선 remove.c의 계약을 실제 호출부에서 확인할 수 있습니다. 이 remove 본문은 pci_ecam_free를 직접 부르지 않으며 그것은 등록된 관리 작업이 담당합니다. bridge나 bridge->bus의 NULL 검사는 여기 없으므로 정상 probe 뒤 제거라는 수명 전제를 확인해야 합니다.'),
        ('전체 범위와 실행 한계', 'gen_pci_unmap_cfg,gen_pci_init,probe,remove 네 함수와 두 GPL export,Generic PCI host common driver 설명 및 GPL v2 메타데이터를 대조했습니다. 별도 platform_driver 객체나 모듈 등록 함수는 이 파일에 없습니다. 실제 호스트 장치 바인딩,ECAM 접근,관리 자원 해제 또는 커널 빌드는 수행하지 않았습니다.')
    ], questions=[
        ('ECAM 생성 후 devm_add_action_or_reset 등록이 실패하면 별도 free가 필요한가?', '이 경로에서는 reset 동작이 해제 콜백을 호출하므로 중복 free하면 안 된다', '그렇다. 콜백은 등록 성공 때만 어떤 경우에도 실행될 수 있다', 'or_reset 계약은 등록 실패 시 전달한 정리 함수를 즉시 실행하는 것입니다. 이 본문은 오류 포인터만 반환하며 추가 free를 하지 않습니다.'),
        ('gen_pci_init이 사용하는 BUS 자원은 어디서 오는가?', 'bridge->windows의 첫 IORESOURCE_BUS 항목', '이 함수가 항상 새로 할당한0..255 배열', 'resource_list_first_type으로 기존 창 목록을 조회합니다. 없으면 -ENODEV이고 기본 버스 범위를 여기서 합성하지 않습니다.'),
        ('remove에서 ECAM을 직접 해제한 다음 루트 장치를 제거하는가?', '아니다. 잠금 아래 중지·제거하고 ECAM은 관리 작업으로 정리한다', '그렇다. 첫 줄이 pci_ecam_free다', '본문의 명시적 순서는 drvdata 조회,잠금,stop,remove,unlock입니다. 관리 자원 정리와 직접 호출을 구분해야 합니다.'),
        ('msi_domain=true 설정만으로 모든 MSI IRQ가 이미 할당되었다고 볼 수 있는가?', '없다. 호스트 상태 플래그를 설정하고 코어 probe에 넘긴다', '있다. 이 대입이 벡터 전체를 할당한다', '대입 직후 pci_host_probe를 호출할 뿐 이 파일에 벡터 할당 루프나 IRQ 요청은 없습니다.'),
        ('이 파일 자체가 platform_driver를 등록하는가?', '아니다. 공통 probe/remove를 내보내는 역할이다', '그렇다. module_platform_driver 호출을 포함한다', '네 함수와 export 및 모듈 메타데이터가 전체입니다. 공통 도우미와 이를 사용하는 실제 플랫폼 드라이버를 구분해야 합니다.')
    ]
)]
