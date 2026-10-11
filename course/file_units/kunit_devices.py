"""Whole-file fake-device contracts and implementation, including error paths."""
ROWS = [dict(
    path='lib/kunit/device.c', title='KUnit 가상 장치: driver core 수명과 cleanup 등록의 빈틈',
    intro='KUnit bus, 드라이버와 장치의 생성·등록·해제 및 모든 오류 분기를 분석합니다.',
    principle='장치 등록 취소, 참조 반환, 메모리 회수, 테스트 cleanup 예약은 서로 다른 단계입니다.',
    use='container_of, 오류 포인터, 역순 정리, 소유권과 문서·구현 차이를 학습합니다.',
    area='장치 모델 · 참조 수명 · 오류 회수 · callback · 테스트',
    sections=[
        ('구성과 자료구조', 'GPL-2.0 파일은 device,dma-mapping 및 KUnit test,device,resource와 내부 헤더를 포함합니다. 두 action wrapper는 device_unregister와 driver_unregister를 void * callback 형태로 감쌉니다. 전역 kunit_bus_device는 root 장치이고 kunit_device는 첫 멤버 dev,소유 test 포인터 owner,자동 관리 driver 포인터를 가집니다. to_kunit_device는 container_of_const를 사용합니다. bus_type에는 name="kunit"만 지정됩니다.'),
        ('Bus 초기화', 'kunit_bus_init은 root_device_register("kunit")를 먼저 호출하고 오류 포인터면 PTR_ERR를 반환합니다. 이어 bus_register를 호출하며 실패하면 root_device_unregister를 수행합니다. 그 실패 분기에서 전역 포인터를 NULL로 지우지는 않습니다. 따라서 초기화 실패 후 shutdown을 무조건 호출해도 안전하다고 이 코드만으로 주장할 수 없습니다.'),
        ('Bus 종료와 release', 'shutdown은 전역 포인터가 IS_ERR_OR_NULL이면 반환하고,그 밖에는 bus_unregister,root_device_unregister,전역 NULL 대입 순서입니다. 장치 release callback은 바깥 kunit_device를 찾아 kfree합니다. device_unregister 호출과 마지막 장치 참조에 따른 release 실행 시점은 같지 않을 수 있습니다.'),
        ('드라이버 준비', 'driver_create는 kunit_kzalloc으로 driver를 만들고 실패하면 ERR_PTR(-ENOMEM)입니다. name은 kunit_kstrdup_const로 얻고 bus와 owner=THIS_MODULE을 지정합니다. 이름 복제 결과에 대한 NULL 검사는 없습니다. 이 파일 안에는 probe나 bus match callback을 설정하는 코드도 없습니다.'),
        ('드라이버 등록과 cleanup 오류', 'driver_register가 실패하면 kunit_kfree로 driver를 회수하고 오류 포인터를 반환합니다. 이름 저장소는 이 분기에서 직접 정리하지 않으며 관리 자원 수명을 별도로 봐야 합니다. 등록 성공 후 kunit_add_action으로 unregister를 예약하지만 반환값을 확인하지 않고 driver를 반환합니다. 따라서 cleanup action 할당 실패까지 자동 rollback이 보장된다고 설명하면 안 됩니다.'),
        ('장치 할당과 이름', 'register_internal은 일반 kzalloc으로 kunit_device를 할당하며 owner=test를 저장합니다. dev_set_name은 "%s.%s"에 test->name과 사용자 name을 넣습니다. 이름 설정 실패는 kfree와 ERR_PTR입니다. 이후 release,bus,parent를 설정합니다. managed allocation 대신 장치 release가 바깥 객체의 메모리를 회수하는 구조입니다.'),
        ('장치 등록 실패와 DMA 설정', 'device_register가 실패하면 단순 kfree 대신 put_device를 호출하고 오류를 반환합니다. 성공 후 dma_mask가 자신의 coherent_dma_mask 필드를 가리키게 하고 coherent_dma_mask=DMA_BIT_MASK(32)로 둡니다. 이는 DMA 주소 mask 설정이며 실제 DMA 버퍼 할당은 아닙니다. 이어 device unregister action을 예약하지만 여기서도 add_action 오류값은 검사하지 않습니다.'),
        ('사용되지 않는 drv 인수', 'register_internal의 drv 인수는 본문에서 사용되지 않습니다. dev.driver에 대입하거나 device와 driver를 연결하는 명시적 작업도 없습니다. with_driver는 그 인수를 helper로 넘기지만 실제 helper가 무시합니다. 공개 문서의 associate라는 의도를 근거로 이 버전에서 지정 driver와 연결되었다고 단정하지 않습니다. 자동 등록 경로의 kunit_device.driver는 cleanup용으로 나중에 저장하는 별도 필드입니다.'),
        ('외부 드라이버 wrapper', 'register_with_driver는 내부 helper를 호출하고 IS_ERR_OR_NULL이면 ERR_CAST를 반환하며 성공 시 embedded dev 주소를 반환합니다. NULL에 ERR_CAST를 적용한다고 새로운 오류 코드가 생성되는 것은 아닙니다. 일반 kzalloc으로 초기화된 cleanup용 driver 필드는 이 경로에서 계속 NULL이며 외부 driver의 자동 해제를 등록하지 않습니다.'),
        ('자동 드라이버 경로', 'register는 먼저 driver_create를 호출해 오류면 ERR_CAST합니다. 장치 helper가 실패하면 driver unregister action을 release하여 조기 정리하고 장치 오류를 반환합니다. 성공하면 dev->driver=drv로 cleanup 책임을 표시한 뒤 embedded dev 주소를 반환합니다. 정상 action 등록 순서는 driver가 먼저,device가 나중이므로 역순 cleanup은 device를 먼저 해제하도록 구성됩니다.'),
        ('조기 해제의 순서', 'unregister는 먼저 바깥 객체에서 driver 포인터를 지역 변수에 저장합니다. device release action 실행 뒤 바깥 객체를 다시 읽지 않기 위한 순서입니다. driver가 있으면 이름 주소를 저장하고 driver unregister action을 release한 뒤 kunit_kfree_const로 이름을 반환합니다. driver 구조체 자체를 이 함수에서 kunit_kfree하는 코드는 없으므로 unregister와 구조체 회수의 시점을 혼동하지 않습니다.'),
        ('전체 범위와 한계', '두 action wrapper,전역과 구조체,bus init/shutdown,release,driver 생성,장치 helper,외부·자동 driver 등록과 조기 해제,네 GPL export를 대조했습니다. owner 필드는 저장되지만 이 파일에서 소유 test 검증에 사용하지 않습니다. 실패한 cleanup 예약,초기화 실패 뒤 shutdown,사용되지 않는 drv 등은 소스상의 관찰이며 실제 커널 오류 주입이나 binding 실험을 실행한 것은 아닙니다.')
    ], questions=[
        ('device_register 실패 후 이 helper가 호출하는 것은?', 'put_device', '바깥 객체에 무조건 직접 kfree만 수행', '장치 core 등록 단계까지 갔으면 참조·release 경로로 회수합니다. 이름 설정 실패의 직접 kfree와 구분해야 합니다.'),
        ('register_internal은 drv 인수를 dev.driver에 저장하는가?', '아니다. 이 버전 본문에서 drv를 사용하지 않는다', '그렇다. helper 첫 줄에서 반드시 연결한다', '인수 이름이나 문서 의도만 보지 말고 실제 대입과 호출을 추적해야 합니다. cleanup용 kunit_device.driver도 다른 필드입니다.'),
        ('cleanup action 등록 실패를 driver_create가 반환 오류로 전달하는가?', '아니다. add_action 반환값을 검사하지 않는다', '그렇다. 즉시 driver_unregister하고 오류를 반환한다', 'driver_register 오류는 검사하지만 뒤의 add_action 오류는 검사하지 않습니다. 두 실패 지점을 별도로 분석해야 합니다.'),
        ('자동 생성 장치의 정상 역순 cleanup에서 무엇이 먼저인가?', '장치 unregister가 드라이버 unregister보다 먼저다', '드라이버 구조체가 장치보다 먼저 무조건 해제된다', 'driver cleanup을 먼저 등록하고 device cleanup을 나중에 등록합니다. action 역순 실행 계약을 적용합니다.'),
        ('unregister가 device action 실행 전에 driver 주소를 저장하는 이유는?', 'device release로 바깥 객체가 해제될 수 있기 때문이다', 'driver 이름을 숫자로 변환하기 위해서다', 'action 실행 뒤 to_kunit_device(dev)를 다시 읽으면 객체 수명이 끝났을 수 있습니다. 필요한 값을 먼저 확보합니다.'),
        ('DMA_BIT_MASK(32) 설정이 뜻하는 것은?', '장치 DMA mask를 설정한다', '32바이트 DMA 버퍼를 실제로 할당한다', '코드는 mask 필드와 포인터를 설정할 뿐 DMA allocation API를 부르지 않습니다. 비트 폭과 메모리 크기를 구분합니다.')
    ]
), dict(
    path='include/kunit/device.h', title='KUnit 장치 공개 API: 자동 소유와 외부 드라이버 계약',
    intro='조건부 선언 네 개의 문서와 소유권 계약 전체를 분석합니다.',
    principle='자동 생성한 객체와 외부에서 받은 객체는 cleanup 책임이 다릅니다.',
    use='오류 포인터와 API 문서·구현의 구분을 학습합니다.',
    area='인터페이스 · 장치 모델 · 소유권 · 조건부 컴파일',
    sections=[
        ('조건부 공개 범위', 'GPL-2.0 include guard 안에서 IS_ENABLED(CONFIG_KUNIT)일 때만 test.h include,device와 device_driver 전방 선언 및 네 함수 선언이 나타납니다. 비활성 경우 대체 inline stub을 제공하지 않습니다. 이 파일은 장치 구조체의 내부 레이아웃을 직접 정의하지 않습니다.'),
        ('드라이버와 장치 생성 계약', 'driver_create는 test와 name을 받아 KUnit bus에 붙은 managed driver를 만드는 계약입니다. device_register는 대응 driver까지 생성하고 테스트 종료 또는 조기 unregister 때 정리하는 장치 포인터를 반환하며 실패 시 오류 포인터라는 문서가 있습니다. 함수명에 register가 있어도 반환값을 NULL 검사만으로 처리하면 오류 포인터를 놓칠 수 있습니다.'),
        ('외부 드라이버와 조기 종료', 'register_with_driver는 const device_driver *drv를 받아 사용자가 제공한 driver와 장치를 연결한다는 문서를 갖습니다. unregister는 이 API들로 만든 장치를 정리하며 KUnit이 생성한 driver도 정리한다고 설명합니다. 문서상 외부 driver까지 무조건 소유하는 계약은 아닙니다. 실제 v6.12 구현 helper가 drv를 사용하지 않는 점은 별도 구현 강의에서 다루며 선언만으로 binding 완료를 증명하지 않습니다.'),
        ('검토 범위', '네 선언 모두 test 인수를 받고 장치 unregister만 void 반환입니다. 문서,조건부 영역,전방 선언과 guard를 모두 검토했습니다. 이 헤더 자체에는 allocation,driver matching,오류 회수 코드가 없으므로 문서의 의도와 실행 보장을 구분합니다.')
    ], questions=[
        ('KUnit 비활성 구성에서 이 헤더가 네 API의 no-op stub을 제공하는가?', '아니다. 조건부 영역 밖에 대체 구현이 없다', '그렇다. 항상 성공하는 inline 함수를 제공한다', 'IS_ENABLED 영역과 그 뒤를 끝까지 읽으면 else 분기가 없음을 확인할 수 있습니다.'),
        ('device_register 실패 반환 검사에서 중요한 것은?', '오류 포인터를 판별하는 것이다', '오직 NULL인지 확인하면 충분하다', '문서가 error pointer를 명시합니다. 반환 타입이 포인터라고 실패 표현이 NULL 하나인 것은 아닙니다.'),
        ('외부 driver를 받는 함수 선언만으로 실제 binding을 증명할 수 있는가?', '아니다. 구현의 인수 사용과 연결 동작을 확인해야 한다', '그렇다. 인수 이름 drv 자체가 binding을 수행한다', '문서는 계약 의도이며 실행은 구현에 있습니다. 이 버전의 unused drv는 둘을 대조할 필요를 보여줍니다.')
    ]
), dict(
    path='lib/kunit/device-impl.h', title='KUnit 내부 bus 인터페이스: 초기화와 종료의 경계',
    intro='짧은 내부 헤더의 두 선언과 사용 범위를 모두 확인합니다.',
    principle='공개 테스트 helper와 subsystem 자체의 생명주기 API는 구분할 수 있습니다.',
    use='헤더 guard,반환 계약과 내부 인터페이스의 범위를 학습합니다.',
    area='C 인터페이스 · 초기화 · 모듈 수명',
    sections=[
        ('파일과 guard', 'GPL-2.0 헤더는 KUnit 내부 driver/bus 관리용이라는 주석과 _KUNIT_DEVICE_IMPL_H guard를 가집니다. 별도 include나 구조체 정의는 없습니다. 기본 C 타입으로 표현 가능한 선언 두 개만 제공하기 때문입니다.'),
        ('초기화 선언', 'int kunit_bus_init(void)는 인수 없이 bus를 등록하는 내부 API입니다. int 반환은 구현의 성공 또는 오류를 호출자가 확인할 수 있게 합니다. 이 헤더는 함수 본문이나 오류 코드 목록,자동 호출 매크로를 제공하지 않습니다.'),
        ('종료 선언과 범위', 'void kunit_bus_shutdown(void)는 인수·반환값 없는 내부 종료 API입니다. 개별 장치를 등록하는 공개 함수와 역할이 다릅니다. 헤더를 include한다고 bus가 초기화되거나 종료되는 것은 아닙니다. 두 선언·주석·guard 전체를 대조했습니다.')
    ], questions=[
        ('이 헤더를 include하면 kunit_bus가 바로 등록되는가?', '아니다. 함수 선언만 제공한다', '그렇다. include가 등록 함수를 실행한다', '선언과 실행을 구분합니다. 실제 호출과 구현은 다른 파일에 있습니다.'),
        ('두 함수의 반환 타입 차이는?', 'init은 int,shutdown은 void다', '둘 다 장치 포인터를 반환한다', '초기화 결과 전달과 종료 동작의 인터페이스가 다릅니다. 장치 생성 API와 혼동하지 않습니다.')
    ]
)]
