"""Whole-file MDIO OF interface, address parser and non-DT fallbacks."""
ROWS = [dict(
    path='include/linux/of_mdio.h', title='OF MDIO 인터페이스: PHY 주소 검증과 실제 동작하는 fallback',
    intro='버스 등록 wrapper,PHY 연결 선언,주소 파서와 모든 비지원 대체 구현을 분석합니다.',
    principle='선택 기능이 꺼져도 공통 버스 등록으로 대체하여 실제 작업을 수행하는 API가 있습니다.',
    use='모듈 소유자 전달,범위 검사,callback 시그니처와 조건부 동작을 학습합니다.',
    area='MDIO · Ethernet PHY · 장치 트리 · 모듈 수명 · 입력 검증',
    sections=[
        ('파일과 조건', 'GPL-2.0-only 헤더는 device,phy,OF를 포함하고 IS_ENABLED(CONFIG_OF_MDIO)로 분기합니다. 단순한 #ifdef와 달리 built-in 또는 module 활성 상태를 고려하는 형태입니다. MDIO는 Ethernet PHY 관리 인터페이스이며 이 헤더가 패킷 데이터 전송을 구현하는 것은 아닙니다.'),
        ('모듈 소유자 전달', '활성 __of_mdiobus_register는 bus,node,owner를 받고 public inline은 THIS_MODULE을 자동 전달합니다. managed 버전도 device,bus,node,owner를 받는 내부 함수에 THIS_MODULE을 넘깁니다. public 호출자가 owner를 직접 넘기지 않아도 소유자 인수가 내부 계층에 전달되는 wrapper입니다. 실제 참조 획득·해제 로직은 외부 구현에서 확인해야 합니다.'),
        ('검색과 연결 선언', 'child_is_phy는 bool,find_device는 mdio_device *,phy_find_device는 phy_device *,find_bus는 mii_bus *를 반환합니다. of_phy_connect는 netdevice,PHY node,netdevice를 받는 void handler,flags,interface를 받습니다. get_and_connect는 netdevice,node,handler만 받는 별도 선언입니다. 같은 포인터 반환형이라고 두 함수의 설정 과정이 같다고 가정하지 않습니다.'),
        ('Fixed link와 등록', 'fixed link 등록은 int,해제는 void,판정은 bool입니다. mdiobus_phy_device_register는 bus,phy,child node,u32 addr를 받는 int 함수입니다. 이 헤더에는 fixed-link 속성 파싱이나 하드웨어 초기화 본문은 없습니다.'),
        ('PHY 주소 파서', '활성 of_mdio_parse_addr는 reg 속성을 u32로 읽고 오류이면 노드 full_name을 포함한 로그를 남긴 뒤 같은 오류를 반환합니다. 읽기 성공 후 addr>=PHY_MAX_ADDR이면 로그와 -EINVAL입니다. 주석은 유효 주소 0~31을 명시합니다. 성공 반환값 자체가 주소인 int이며 상태 0만 돌려주는 함수가 아닙니다. 따라서 주소 0은 성공값일 수 있습니다.'),
        ('비활성 버스 등록의 실제 동작', '비활성 of_mdiobus_register는 mdiobus_register(mdio)를,managed 버전은 devm_mdiobus_register(dev,mdio)를 호출합니다. node 인수는 사용하지 않습니다. 주석은 드라이버에 호환 분기를 남기지 않도록 non-DT 등록으로 대체한다고 설명합니다. 이를 단순 성공 no-op 또는 무조건 -ENOSYS라고 설명하면 안 됩니다.'),
        ('비활성 나머지 API', 'child_is_phy와 fixed_link 판정은 false입니다. MDIO device,PHY device,bus 검색과 두 connect 함수는 NULL입니다. 주소 파싱,fixed link 등록,PHY device 등록은 -ENOSYS이며 fixed link 해제는 빈 함수입니다. 이 분기에는 owner를 받는 두 내부 등록 함수 선언을 그대로 복제하지 않습니다.'),
        ('전체 범위와 한계', '활성 선언·두 owner wrapper·주소 파서,비활성의 모든 fallback과 stub을 대조했습니다. 실제 버스 등록·PHY 연결이나 주소 오류 주입을 실행하지 않았습니다. 비활성 구성이라고 어떤 부작용도 없다는 가정 대신 각 함수가 공통 구현을 호출하는지 확인해야 합니다.')
    ], questions=[
        ('OF_MDIO 비활성에서 of_mdiobus_register는?', '일반 mdiobus_register를 호출한다', '무조건 아무 작업 없이 0을 반환한다', '본문이 non-DT 등록으로 위임합니다. 비지원 stub도 실제 작업을 할 수 있습니다.'),
        ('활성 등록 wrapper가 내부 함수에 추가하는 인수는?', 'THIS_MODULE', '항상 PHY 주소 0', 'owner 인수를 자동 전달합니다. public API의 간결한 형태와 내부 함수의 소유자 계약을 연결합니다.'),
        ('주소 파서가 0을 반환하면 반드시 오류인가?', '아니다. PHY 주소 0은 유효하다', '그렇다. 모든 정상 주소는 1부터 시작한다', '주석의 범위는 0~31입니다. 음수 오류와 nonnegative 주소를 구분해야 합니다.'),
        ('reg 읽기 성공이면 범위 검사가 생략되는가?', '아니다. addr>=PHY_MAX_ADDR이면 -EINVAL이다', '그렇다. 어떤 u32도 PHY 주소로 허용한다', '문법상 정수 읽기와 도메인 범위 검증은 별도 단계입니다.'),
        ('비활성 parse_addr와 find_bus의 실패 표현은?', '-ENOSYS와 NULL', '둘 다 같은 정수 0만 반환한다', '정수 주소 반환 함수와 포인터 검색 함수는 오류 표현이 다릅니다.')
    ]
)]
