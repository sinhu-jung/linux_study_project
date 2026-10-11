"""Whole-file PCI physical slot sysfs, naming and kobject lifetimes."""
ROWS = [dict(
    path='drivers/pci/slot.c', title='PCI 슬롯 객체: 이름 충돌·참조 공유·sysfs 수명',
    intro='속성 어댑터부터 슬롯 생성·해제·모듈 링크·초기화까지 파일 전체를 분석합니다.',
    principle='물리 슬롯의 식별 키와 사용자에게 보이는 이름은 다르며 destroy 호출은 참조 감소일 수 있습니다.',
    use='kobject 참조,이름 충돌 해결,연결 리스트,실패 경로 정리와 다중 잠금 범위를 학습합니다.',
    area='PCI 슬롯 · sysfs · 객체 수명 · 연결 리스트 · 문자열',
    sections=[
        ('sysfs 콜백 어댑터', 'GPL-2.0 파일은 kobject,slab,module,pci,err와 내부 pci.h를 포함하고 전역 pci_slots_kset을 GPL export합니다. pci_slot_attr_show/store는 kobject와 attribute를 슬롯 전용 타입으로 변환하고 해당 콜백이 있으면 호출하며 없으면 -EIO입니다. store에는 buf와 len을 그대로 전달합니다. pci_slot_sysfs_ops가 두 어댑터를 연결합니다.'),
        ('기본 속성 표현', 'address_read_file은 slot->number==0xff이면 domain:bus만,그 외에는 domain:bus:slot을 16진수로 출력하며 개행을 붙입니다. bus_speed_read는 pci_speed_string 결과를 sysfs_emit하고 max/cur wrapper는 slot->bus의 해당 속도를 전달합니다. 기본 읽기 전용 속성은 address,max_bus_speed,cur_bus_speed 세 개이고 NULL 종료 배열과 ATTRIBUTE_GROUPS로 연결됩니다. 일반 설명에 width가 언급되어도 이 기본 배열에 width 속성은 없습니다.'),
        ('마지막 참조의 release', 'pci_slot_release는 pci_bus_sem 읽기 잠금 아래 버스 장치들을 훑어 슬롯 번호가 같은 dev->slot을 NULL로 지웁니다. 슬롯 객체 포인터 동일성 검사가 아니라 PCI_SLOT(devfn)과 number 비교입니다. 잠금을 푼 뒤 slot->list를 삭제하고 slot을 kfree합니다. kobj_type은 이 release,sysfs_ops,기본 groups를 지정합니다. release 자체에서 pci_slot_mutex를 새로 잡지는 않으므로 호출 수명과 잠금 문맥을 함께 확인해야 합니다.'),
        ('전역 이름 충돌 해결', 'make_slot_name은 이름을 복사한 뒤 pci_slots_kset에서 같은 이름을 찾습니다. 발견한 객체 참조는 put하고 name-1,name-2 순서로 재시도합니다. dup==max인1,10,100 등의 경계에서 len을 하나 늘리고 max를10배로 하며 이전 버퍼를 해제한 뒤 새 크기로 할당합니다. 첫 충돌의 크기는 원래 이름 길이+3으로 하이픈,한 자리 숫자,NUL을 담습니다. 후보 검색 반복마다 비용이 들며 이름이 많아도 상수 시간이라고 할 수 없습니다. 정수 카운터 오버플로의 명시적 검사는 없습니다.'),
        ('rename와 장치 연결', 'rename_slot은 현재 이름과 같으면0이고 아니면 유일한 후보 이름을 만들어 kobject_rename 후 임시 문자열을 해제합니다. pci_dev_assign_slot은 pci_slot_mutex 아래 같은 버스 slots를 순회해 번호가 맞는 slot을 dev->slot에 대입합니다. 일치 뒤 break도,별도 kobject_get도 없습니다. get_slot은 이미 mutex를 보유했다는 주석 아래 버스·번호로 첫 슬롯을 찾고 kobject_get한 뒤 반환합니다.'),
        ('기존 슬롯 공유와 hotplug 이름 변경', 'pci_create_slot은 mutex를 잡고 slot_nr!=-1이면 get_slot으로 기존 객체를 찾습니다. 기존 객체가 있고 hotplug 인수가 NULL이면 새 이름을 적용하지 않고 증가한 참조를 반환합니다. hotplug 호출이면 기존 slot->hotplug가 있을 때 -EBUSY,없으면 rename을 시도합니다. 실패하면 방금 얻은 참조를 put하고 ERR_PTR(err)로 반환합니다. 이 함수가 hotplug 인수를 slot->hotplug에 직접 저장하는 문장은 없습니다.'),
        ('placeholder와 새 객체 생성', 'slot_nr=-1은 기존 슬롯 조회를 건너뛰므로 같은 버스에 여러 placeholder를 만들 수 있습니다. 새 slot을 kzalloc하고 bus,number,kset을 설정한 뒤 이름을 만듭니다. 이름 할당 실패는 아직 kobject 초기화 전이므로 slot을 직접 kfree합니다. list를 초기화해 parent->slots에 먼저 넣고 kobject_init_and_add를 호출합니다. 이 실패는 kobject_put으로 release 경로를 이용해 목록과 객체를 정리합니다. 성공하면 pci_bus_sem 읽기 잠금 아래 번호가 맞는 장치에 slot을 연결합니다.'),
        ('공통 반환과 destroy', 'create의 out 경로는 임시 이름을 해제하고 mutex를 푼 뒤 slot 또는 오류 포인터를 반환합니다. 슬롯은 버스·번호로 식별되지만 sysfs 이름은 전역 kset에서 충돌을 피합니다. pci_destroy_slot은 예상 참조 수를 로그로 남긴 뒤 mutex 아래 kobject_put합니다. 참조가 남으면 즉시 release되지 않으므로 호출 한 번이 반드시 목록 삭제나 객체 해제를 뜻하지 않습니다.'),
        ('조건부 모듈 링크', 'HOTPLUG_PCI 또는 HOTPLUG_PCI_MODULE이 정의되면 hotplug 헤더와 두 링크 함수를 포함합니다. create_module_link는 pci_slot->hotplug와 ops가 없으면 반환하고 mod_name으로 module_kset 객체를 찾습니다. 없으면 반환,있으면 module 이름의 sysfs 링크를 만들고 실패 로그 여부와 무관하게 찾은 kobject를 put합니다. remove_module_link는 같은 링크 이름을 제거합니다. 두 함수는 GPL export이며 이 코드가 모듈을 로드하는 것은 아닙니다.'),
        ('초기화와 전체 범위', 'pci_slot_init은 PCI bus kset 아래 slots kset을 만들고 실패 시 로그와 -ENOMEM,성공 시0입니다. subsys_initcall로 연결됩니다. 모든 속성 함수·테이블,이름 helper,슬롯 조회·연결·생성·destroy·release,조건부 링크 및 초기화를 대조했습니다. create/destroy도 GPL export입니다. 실제 sysfs 생성,슬롯 hotplug나 동시성 실행,커널 빌드는 수행하지 않았습니다.')
    ], questions=[
        ('같은 버스·슬롯 번호가 이미 있고 hotplug 인수가 NULL이면?', '기존 객체 참조를 늘려 반환하며 새 이름으로 바꾸지 않는다', '항상 새 슬롯 객체를 만들어 중복 등록한다', 'get_slot이 참조를 얻고 기존 객체 분기는 곧바로 out으로 갑니다. 이름 변경은 hotplug 호출의 별도 조건입니다.'),
        ('slot_nr=-1은 기존 번호 검색을 수행하는가?', '아니다. placeholder 경로로 바로 가 새 객체를 만든다', '그렇다. 모든 -1 슬롯은 하나로 합친다', '주석은 삽입 전 번호를 모르는 플랫폼에서 여러 placeholder가 필요하다고 설명합니다. 번호 없는 슬롯의 유일성 정책이 일반 슬롯과 다릅니다.'),
        ('이름 N이 이미 있으면 다음 후보는?', 'N-1부터 숫자를 증가시킨다', '같은 N을 그대로 등록한다', 'make_slot_name은 kset 검색과 참조 반환 뒤 접미 번호를 붙여 반복합니다. 물리 식별 키와 전역 표시 이름 충돌 처리를 구분해야 합니다.'),
        ('kobject_init_and_add 실패 전에 슬롯이 목록에 들어갔다면 누가 정리하는가?', 'kobject_put으로 이어지는 release 경로가 목록 삭제와 객체 해제를 한다', '실패해도 목록에 영구히 남긴다', '리스트 추가가 먼저지만 kobj_type에 release가 연결되어 있습니다. 초기화 전 이름 할당 실패의 직접 kfree 경로와 다릅니다.'),
        ('destroy_slot 한 번이 항상 즉시 메모리 해제인가?', '아니다. kobject 참조가 마지막일 때 release가 실행된다', '그렇다. 본문이 무조건 kfree(slot)을 호출한다', 'destroy는 mutex 아래 put을 수행합니다. 직접 해제는 release에 있으므로 공유 참조를 고려해야 합니다.'),
        ('기본 sysfs 속성 배열에 슬롯 width가 있는가?', '없다. address와 max/cur bus speed 세 개다', '있다. 설명에 언급되므로 자동 생성된다', '문서의 일반적 예와 실제 등록 배열을 구분해야 합니다. 속성은 배열과 groups에 연결되어야 이 기본 경로로 등록됩니다.'),
        ('pci_dev_assign_slot은 슬롯을 찾을 때 새 참조를 얻는가?', '이 본문에서는 아니다. dev->slot 대입만 한다', '그렇다. 매 대입 전에 kobject_get이 있다', '참조를 얻는 get_slot helper와 연결 포인터만 설정하는 assign 함수는 다른 역할입니다. 이름만으로 수명 계약을 같게 해석하면 안 됩니다.')
    ]
)]
