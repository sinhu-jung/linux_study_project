"""Whole-file PCI ECAM window allocation, per-bus maps and operation tables."""
ROWS = [dict(
    path='drivers/pci/ecam.c', title='PCI ECAM: 전체 창과 버스별 매핑·비트 오프셋',
    intro='설정 공간 생성·해제, 버스 추가·제거, 주소 계산과 세 연산 테이블 전체를 분석합니다.',
    principle='주소 공간 여유에 따라 매핑 단위를 달리하되 버스 번호를 창 시작 기준으로 정규화해야 합니다.',
    use='지연 자원 할당, 배열 인덱스 정규화, 비트 필드 주소 계산과 공통 오류 정리를 학습합니다.',
    area='PCI ECAM · 가상 주소 · MMIO · 자원 관리 · 비트 연산',
    sections=[
        ('아키텍처별 매핑 전략', 'GPL-2.0 파일은 device,io,kernel,module,pci,pci-ecam,slab을 포함합니다. per_bus_mapping은 !IS_ENABLED(CONFIG_64BIT)입니다. 64비트에서는 넓은 가상 주소 공간을 이용해 전체 설정 창을 한 번 매핑하고, 그 외에는 버스마다 따로 매핑한다는 주석이 있습니다. 두 방식은 배열 winp와 단일 win 포인터로 구분됩니다.'),
        ('생성과 유효 범위', 'pci_ecam_create는 busr.start>end이면 ERR_PTR(-EINVAL),cfg kzalloc 실패면 ERR_PTR(-ENOMEM)입니다. ops->bus_shift가0이면 PCIE_ECAM_BUS_SHIFT를 기본으로 선택하고 부모·ops·버스 범위·플래그·유효 shift를 cfg에 저장합니다. 요구 버스 수와 cfgres 크기>>shift로 계산한 수용 가능 수를 비교해 초과하면 end를 start+줄인 개수-1로 바꾸고 경고합니다. 수용 가능 수가0인지 별도 검사하거나 임의 bus_shift의 유효 범위를 검증하는 코드는 없습니다.'),
        ('물리 자원 예약과 초기 매핑', 'bsz=1<<bus_shift로 버스당 크기를 구합니다. cfg->res는 cfgres의 전체 시작·끝을 복사하고 MEM|BUSY와 PCI ECAM 이름을 설정합니다. iomem_resource에 request_resource_conflict로 예약하며 충돌이면 -EBUSY와 로그 후 공통 정리입니다. 버스 범위를 줄였더라도 물리 예약 범위 자체는 원래 cfgres 전체입니다. 버스별 방식은 포인터 배열만 kcalloc하고 실제 버스 창은 아직 매핑하지 않습니다. 전체 방식은 bus_range*bsz 크기를 pci_remap_cfgspace합니다.'),
        ('추가 초기화와 실패 정리', 'ops->init이 있으면 기본 예약·배열 또는 전체 매핑 뒤에 호출하고 오류를 전파합니다. 성공하면 cfg를 반환합니다. 전체 매핑 실패는 로그 후 -ENOMEM,배열 실패도 -ENOMEM이며 모든 이들 오류는 pci_ecam_free 후 ERR_PTR(err)로 나갑니다. 성공 포인터와 오류 포인터를 구분해야 하며 NULL만 검사하는 반환 계약이 아닙니다.'),
        ('전체 해제', 'pci_ecam_free는 버스별 배열이 있으면 현재 busr 크기만큼 순회해 각 비NULL 매핑을 iounmap하고 배열을 kfree합니다. 전체 방식에서는 win이 있으면 한 번 unmap합니다. res.parent가 있을 때만 물리 resource를 release하고 cfg를 해제합니다. cfg 자체가 NULL인지 검사하지 않습니다. ops->init이 추가로 만든 모든 외부 자원을 이 함수가 자동으로 안다는 뜻도 아닙니다.'),
        ('버스별 추가와 제거', 'add_bus는 전체 매핑 방식이면 범위 검사 전에0을 반환합니다. 버스별 방식은 bus 번호 범위를 검사한 뒤 시작 번호를 빼 상대 인덱스로 만들고 res.start+인덱스*bsz를 매핑해 winp에 넣습니다. 기존 슬롯이 이미 매핑되었는지 확인하는 코드는 없습니다. remove_bus는 버스별 방식과 유효 범위에서만 작동하며 해당 슬롯이 있으면 unmap 후 NULL로 지웁니다. 이후 전체 free가 같은 슬롯을 다시 unmap하지 않게 하는 상태 변경입니다.'),
        ('설정 주소의 기준점', 'map_bus는 범위 밖 버스면 NULL입니다. 안쪽이면 시작 버스 번호를 빼고 버스별 방식에서는 base=winp[상대번호],busn=0으로 바꿉니다. 전체 방식에서는 base=win이며 상대 busn을 유지합니다. 버스별 base에 이미 버스 오프셋이 반영되므로 다시 busn을 더하지 않는 구조입니다. base가 NULL인지 별도로 검사하지 않으므로 add_bus 성공 등 호출 수명 전제를 함께 확인해야 합니다.'),
        ('사용자 shift와 기본 ECAM 식', 'map_bus는 cfg->bus_shift가 아니라 원래 cfg->ops->bus_shift가0인지로 분기합니다. 0이 아니면 bus_offset=(busn&BUS_MASK)<<bus_shift,devfn_offset=(devfn&DEVFN_MASK)<<(bus_shift-8),where&=REG_MASK로 만들고 비트 OR한 값을 base에 더합니다. 0이면 PCIE_ECAM_OFFSET 매크로에 위임합니다. 시작에 계산하는 unsigned devfn_shift는 ops shift가0일 때에도 존재하지만 그 값으로 시프트하는 분기는 실행되지 않습니다. 임의의 비표준 shift에서 필드가 겹치지 않는지까지 검사하는 코드는 없습니다.'),
        ('세 연산 테이블', 'pci_generic_ecam_ops는 add/remove/map을 공통 함수로,read/write를 generic_config_read/write로 지정합니다. bus_shift는 명시하지 않아 기본0입니다. ACPI와 PCI_QUIRKS가 모두 정의되면 pci_32b_ops는 read32/write32를, pci_32b_read_ops는 read32와 일반 write를 사용합니다. 후자의 read only라는 주석은 쓰기 금지를 뜻하지 않고 읽기 접근 방식만32비트로 제한하는 테이블입니다. create/free/map과 generic ops는 GPL export이고 이 파일의 두 quirk 테이블에는 export 문장이 없습니다.'),
        ('전체 범위와 검증 한계', '전역 매핑 정책, 생성·해제, 두 버스 콜백, map 함수, 공통 및 조건부 테이블 전체를 대조했습니다. B개 버스의 개별 매핑 해제는 O(B),주소 계산 자체는 O(1)이고 전체 매핑의 실제 비용은 하위 매핑 구현에 의존합니다. 실제 ECAM 접근, 비표준 장치 설정이나 커널 빌드는 수행하지 않았습니다.')
    ], questions=[
        ('버스별 방식에서 create가 각 버스 설정 공간까지 즉시 매핑하는가?', '아니다. 포인터 배열을 만들고 add_bus에서 개별 매핑한다', '그렇다. create가 항상 모든 버스를 한 번에 매핑한다', 'create의 per_bus 분기는 kcalloc뿐입니다. 실제 pci_remap_cfgspace 호출은 해당 방식의 add_bus에 있습니다.'),
        ('버스별 map_bus에서 busn을0으로 바꾸는 이유는?', '선택한 버스의 base에 이미 그 버스 위치가 반영되어 있기 때문이다', '항상 실제 버스 번호가0이기 때문이다', 'winp 인덱스로 선택한 매핑은 개별 버스 창입니다. 버스 오프셋을 다시 적용하면 같은 변위를 중복 계산하게 됩니다.'),
        ('요구 버스 수를 줄이면 cfg->res의 물리 예약 범위도 같이 줄이는가?', '아니다. cfgres 전체 시작·끝을 복사한다', '그렇다. 반드시 줄인 버스 수만큼 res.end를 수정한다', '줄이는 필드는 cfg->busr.end와 bus_range입니다. cfg->res.end는 cfgres->end를 그대로 받으므로 버스 범위와 예약 범위를 구분해야 합니다.'),
        ('pci_32b_read_ops에는 write 함수가 없는가?', '아니다. 일반 pci_generic_config_write가 지정되어 있다', '그렇다. 읽기 전용이라 모든 쓰기를 금지한다', '이름과 주석의32비트 읽기 전용 제한은 접근 폭 선택을 뜻합니다. 테이블에는 쓰기 콜백이 실제로 있습니다.'),
        ('버스 제거 후 winp 슬롯을 NULL로 만드는 이유는?', '후속 free가 해제된 매핑을 다시 처리하지 않도록 상태를 지운다', '물리 자원 예약 전체를 동시에 해제하기 위해서다', 'remove_bus는 개별 iounmap과 슬롯 초기화만 합니다. 전체 물리 예약 해제는 pci_ecam_free의 별도 단계입니다.'),
        ('create 실패 반환을 NULL 여부만으로 판정해도 되는가?', '아니다. ERR_PTR에 음수 오류를 담아 반환한다', '그렇다. 모든 실패는 NULL이다', 'EINVAL,ENOMEM,EBUSY 및 init 오류가 오류 포인터로 반환됩니다. 정상 포인터와 오류 포인터를 구별하는 계약을 따라야 합니다.'),
        ('map_bus의 기본 오프셋 분기는 어떤 shift를 검사하는가?', '원래 ops->bus_shift가0인지 검사한다', '항상 기본값으로 보정된 cfg->bus_shift만 검사한다', 'create는 cfg에 유효 shift를 저장하지만 map은 ops의 원래 값으로 표준 매크로 사용 여부를 선택합니다. 두 필드를 같은 값으로 가정하면 분기 해석이 틀립니다.')
    ]
)]
