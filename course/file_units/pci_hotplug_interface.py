"""Whole-file PCI hotplug slots, lifecycle declarations and native policy."""
ROWS = [dict(
    path='include/linux/pci_hotplug.h', title='PCI 핫플러그 헤더: 슬롯 콜백·모듈 소유자·native 정책',
    intro='두 구조체,이름 wrapper,등록 수명 API와 ACPI 분기 전체를 분석합니다.',
    principle='함수 포인터 테이블은 기능을 연결하는 계약이며 선언만으로 하드웨어 제어 순서와 수명을 확정할 수 없습니다.',
    use='콜백 다형성,출력 인수,침입형 연결 리스트,매크로 인수 전달과 단락 평가를 학습합니다.',
    area='PCI 핫플러그 · 연결 리스트 · 콜백 · 모듈 수명 · ACPI',
    sections=[
        ('기능 콜백 테이블', 'GPL-2.0+와 _PCI_HOTPLUG_H guard 아래 hotplug_slot_ops를 정의합니다. enable_slot,disable_slot은 slot에서 int를 반환합니다. set_attention_status는 u8 값을 받고 hardware_test는 u32 값을 받습니다. get_power_status,get_attention_status,get_latch_status,get_adapter_status는 u8 * 출력 인수를 받으며 int 결과를 별도로 반환합니다. 출력 상태와 함수의 성공·실패 반환은 같은 값이 아닙니다. 각 값의 인코딩은 이 헤더에서 열거형으로 정의하지 않습니다.'),
        ('reset의 선택적 계약', 'reset_slot은 slot과 bool probe를 받는 int 콜백입니다. 주석은 secondary bus reset이 불필요한 hotplug 이벤트를 만들거나 슬롯을 버스와 독립적으로 reset할 수 있을 때 사용할 선택적 override라고 설명합니다. 이 헤더에는 probe=true에서 실제로 어떤 검사를 하는지 구현이 없습니다. 테이블에 콜백 필드가 있다는 사실만으로 모든 드라이버가 이를 제공한다고 가정하면 안 됩니다.'),
        ('슬롯 구조체와 내장 리스트', 'hotplug_slot은 const hotplug_slot_ops *ops와 list_head slot_list,pci_slot *pci_slot,module *owner,const char *mod_name을 가집니다. 주석은 ops 아래 필드들을 핫플러그 코어 전용으로 지정합니다. slot_list는 객체 안에 포함된 연결 리스트 링크이며 별도 슬롯 객체 포인터 필드와 다릅니다. hotplug_slot_name은 pci_slot_name(slot->pci_slot)에 위임할 뿐 NULL 검사나 문자열 복사·할당을 수행하지 않습니다.'),
        ('등록과 단계별 수명 선언', '__pci_hp_register와 __pci_hp_initialize는 slot,bus,번호,name,owner,mod_name을 받아 int를 반환합니다. pci_hp_add도 int이며 del,destroy,deregister는 void 선언입니다. 이름이 나타내는 단계는 구분되지만 구체적인 등록 순서,실패 복구,소유권 반환은 외부 구현을 확인해야 합니다. 이 헤더에는 등록 루프나 슬롯 메모리 해제가 구현되어 있지 않습니다.'),
        ('모듈 정보를 넘기는 매크로', 'pci_hp_register와 pci_hp_initialize는 호출자가 준 네 인수 뒤에 THIS_MODULE,KBUILD_MODNAME을 붙여 내부 함수에 전달합니다. 주석은 이 값을 얻기 위한 include 연쇄를 피하려고 define을 쓴다고 설명합니다. 파일 상단에는 일반 include가 없고 u8,list_head,pci_slot_name 등의 선언은 포함 문맥에 의존합니다. 매크로가 슬롯 소유자를 임의로0으로 설정하거나 직접 모듈 참조를 증가시키는 본문은 아닙니다.'),
        ('ACPI 지원의 선언 범위', 'CONFIG_ACPI가 있으면 linux/acpi.h를 포함하고 pciehp_is_native,shpchp_is_native의 bool 선언,펌웨어 제어권 획득 함수의 int 선언,acpi_pci_check_ejectable(bus,handle)과 detect_ejectable(handle)의 int 선언을 제공합니다. 이들은 native 제어 여부와 ejectable 판단을 같은 반환 계약으로 합쳐서는 안 되는 별도 API입니다. 실제 펌웨어 호출은 이 헤더에 없습니다.'),
        ('비ACPI 기본값과 논리합', 'ACPI가 없으면 get_hp_hw_control은0,pciehp_is_native와 shpchp_is_native는 true를 반환합니다. 두 ejectable API의 대체 stub은 없습니다. 공통 hotplug_is_native는 pciehp_is_native(bridge) || shpchp_is_native(bridge)입니다. 첫 결과가 true이면 단락 평가로 두 번째를 호출하지 않으며 비ACPI에서는 항상 true입니다. 비ACPI 제어권 함수의0이 실제 펌웨어 협상을 했다는 의미는 아닙니다.'),
        ('전체 범위와 한계', '저작권과 guard,아홉 콜백,슬롯의 모든 필드,이름 inline,여섯 수명 선언,두 매크로,ACPI 선언·세 stub 및 마지막 native wrapper를 모두 대조했습니다. 실제 슬롯 전원·LED·reset·장치 제거 또는 커널 빌드는 실행하지 않았습니다.')
    ], questions=[
        ('get_power_status의 상태 값과 int 반환은 같은 통로인가?', '아니다. 상태는 u8 * 출력,함수 결과는 int 반환이다', '그렇다. int가 언제나 전원 상태 그 자체다', '함수 포인터 시그니처가 두 통로를 구분합니다. 오류 시 출력이 어떻게 되는지는 각 구현의 계약을 확인해야 합니다.'),
        ('pci_hp_register 매크로가 자동으로 더하는 인수는?', 'THIS_MODULE과 KBUILD_MODNAME', '고정된 NULL과 빈 문자열', '네 호출 인수 뒤에 모듈 소유자와 이름을 전달합니다. 직접 내부 함수를 호출할 때와 wrapper의 편의 계약을 구분해야 합니다.'),
        ('비ACPI 구성에서 hotplug_is_native 결과는?', 'true', '항상 false', '첫 pciehp_is_native stub이 true여서 논리합도 true이며 두 번째 피연산자는 단락 평가로 호출하지 않습니다.'),
        ('ACPI가 없을 때 ejectable 두 함수도 이 헤더에서 stub이 제공되는가?', '아니다. else에는 다른 세 함수의 stub만 있다', '그렇다. 모든 활성 선언이 자동으로 stub을 갖는다', '조건부 인터페이스를 함수별로 확인해야 합니다. native와 제어권 기본값을 ejectable API에 그대로 일반화할 수 없습니다.'),
        ('hotplug_slot_name이 새 이름 문자열을 복사해 반환하는가?', '아니다. pci_slot_name 결과를 그대로 반환한다', '그렇다. 항상 별도 버퍼를 할당한다', '본문은 단일 위임 return입니다. 반환 문자열의 소유권을 새 할당으로 추정하거나 임의로 해제해서는 안 됩니다.')
    ]
)]
