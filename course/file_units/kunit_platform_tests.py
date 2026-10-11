"""Whole-file platform helper tests and the limits of their assertions."""
ROWS = [dict(
    path='lib/kunit/platform-test.c', title='KUnit 플랫폼 테스트: 상태 관찰과 수명 검증의 한계',
    intro='장치 테스트 네 개와 드라이버 테스트 두 개, 보조 함수와 suite 등록 전체를 분석합니다.',
    principle='테스트 이름이나 주석의 목표와 실제 assertion이 관찰하는 속성을 구분해야 합니다.',
    use='회귀 테스트,중복 키,참조 수명,completion 재초기화와 embedded context를 학습합니다.',
    area='테스트 설계 · 장치 모델 · 동기화 · 참조 카운팅 · 자료구조',
    sections=[
        ('구성과 단순 할당 테스트', 'GPL-2.0 파일은 platform_device 및 KUnit platform_device,test 헤더를 포함합니다. alloc_test는 이름 kunit-platform과 id=1로 managed 할당한 결과가 오류나 NULL이 아닌지만 EXPECT합니다. 장치 등록 상태나 이름·id 필드,할당 실패 분기를 직접 확인하는 테스트는 아닙니다.'),
        ('등록 후 속성 확인', 'add_test는 이름 kunit-platform-add,id=-1로 할당하고 유효 포인터를 ASSERT합니다. 이후 add 결과 0,dev_is_platform 참,pdev->name 문자열 일치,pdev->id 일치를 각각 EXPECT합니다. ASSERT는 전제 실패 시 후속 접근을 막고 EXPECT는 실패를 기록하면서 뒤 검증을 계속합니다. 비교 대상 이름은 pdev->name이며 모든 sysfs 이름 규칙을 검증하는 것은 아닙니다.'),
        ('중복 이름과 id', 'add_twice_fails_test는 동일 이름 kunit-platform-add-2와 id=-1로 서로 다른 두 객체를 할당합니다. 첫 등록 성공은 ASSERT하고 두 번째 등록은 0이 아닌지를 EXPECT합니다. 같은 포인터에 add를 두 번 호출하는 테스트가 아닙니다. 특정 errno와 동일 이름·다른 id의 성공 여부까지 확인하지 않습니다.'),
        ('이름 검색 callback', 'find_by_name은 dev_name(dev)와 data를 strcmp하여 같으면 참을 반환합니다. bus_find_device의 비교 callback으로 쓰이며 문자열 내용 비교입니다. 검색으로 획득한 device 참조는 별도로 put해야 합니다. 이름이 같다는 관찰과 같은 메모리 주소라는 관찰을 혼동하지 않습니다.'),
        ('별도 test context를 쓰는 cleanup 검증', 'add_cleans_up은 지역 struct kunit fake를 kunit_init_test로 초기화하고 fake.status가 KUNIT_SUCCESS인지 ASSERT합니다. 장치 할당·등록은 &fake에 연결하고 검증 assertion은 바깥 test에 기록합니다. bus_find_device로 등록된 장치를 찾은 뒤 put_device로 검색 참조를 놓고 kunit_cleanup(&fake)를 명시적으로 실행합니다. 바깥 테스트 종료를 기다리지 않고 cleanup 전후를 비교하려는 구성입니다.'),
        ('Cleanup 후 관찰과 한계', '같은 이름으로 다시 검색하여 NULL을 EXPECT하고 put_device를 호출합니다. 주석은 자원 free 경로 이전 실패가 추가 put을 만들 수 있지만 이미 해제된 장치의 kref를 읽어 underflow를 직접 검사할 수 없다고 설명합니다. 버스에서 사라졌다는 assertion이 메모리 누수·참조 수명 전체의 증명은 아닙니다. 또한 fake 초기화 뒤 ASSERT로 조기 중단되는 모든 경로를 자동 cleanup하도록 별도 action을 등록하는 코드는 없습니다.'),
        ('Device suite', 'kunit_platform_device_test_cases에는 alloc,add,중복 등록 실패,cleanup 네 case와 빈 종료 원소가 있습니다. suite 이름은 kunit_platform_device이며 test_cases 포인터를 지정합니다. 순서 있는 배열과 sentinel로 목록을 표현하며 개별 테스트마다 별도 name을 써 충돌을 줄입니다.'),
        ('Embedded driver context', 'kunit_platform_driver_test_context는 platform_driver pdrv와 const char *data를 갖습니다. 상수 test_data는 "test data"입니다. to_test_context는 pdev->dev.driver를 to_platform_driver로 바꾼 뒤 container_of로 바깥 context를 얻습니다. probe는 그 context의 data에 test_data를 저장하고 0을 반환합니다. 전역 문자열은 전달할 값이며 테스트별 결과 저장소는 context 필드입니다.'),
        ('Probe 실행 검증', 'driver_register_test는 managed context를 만들고 초기화된 stack completion을 선언합니다. 장치를 alloc/add한 뒤 probe,name,owner를 설정하고 prepare_wait_for_probe를 ASSERT합니다. driver 등록 결과와 3*HZ 대기의 nonzero,ctx->data 문자열 일치는 EXPECT입니다. timeout이 발생해도 EXPECT이므로 뒤 문자열 검증으로 진행할 수 있습니다. 정확한 probe 횟수나 실패 probe 재시도까지 검사하지 않습니다.'),
        ('이미 probe한 장치의 두 번째 준비', '두 번째 driver 테스트는 먼저 준비·등록·3*HZ 완료 대기를 모두 ASSERT하여 이미 probe한 상태를 확보합니다. 이어 reinit_completion으로 완료 상태를 지운 뒤 prepare_wait_for_probe를 다시 호출하고 HZ 대기의 nonzero를 EXPECT합니다. 기존 완료 신호가 남아 두 번째 호출의 동작을 가리는 것을 방지합니다. 이 경로는 이미 bound인 장치에 대해 helper가 completion을 완료하는 동작을 검증합니다.'),
        ('Driver suite와 모듈 등록', 'driver case 배열에는 두 테스트와 빈 종료 원소가 있고 suite 이름은 kunit_platform_driver입니다. kunit_test_suites에 device와 driver suite 주소를 함께 전달합니다. MODULE_LICENSE는 GPL,description은 플랫폼 드라이버 인프라 테스트임을 명시합니다. 이 파일에 별도 main이나 사용자 공간 테스트 실행기가 있는 것은 아닙니다.'),
        ('전체 범위와 실행 여부', '여섯 테스트,이름 검색,context 변환과 probe callback,두 case 배열과 suite,통합 등록 및 모듈 메타데이터를 모두 대조했습니다. 실제 kernel KUnit 실행 결과를 얻은 것은 아닙니다. 여기서의 학습 검증은 고정 소스에 어떤 assertion이 존재하는지 분석한 것이며 OOM,notifier 등록 실패,동시 probe 경쟁에 대한 실행 검증을 추가로 주장하지 않습니다.')
    ], questions=[
        ('중복 등록 실패 테스트는 같은 pdev 포인터를 두 번 등록하는가?', '아니다. 같은 이름과 id로 두 객체를 할당한다', '그렇다. 하나의 객체에 add만 두 번 호출한다', '두 번째 alloc 결과로 지역 pdev를 덮어씁니다. 객체 정체성 중복과 등록 키 중복을 구분해야 합니다.'),
        ('두 번째 등록 실패에서 특정 errno를 검사하는가?', '아니다. 반환값이 0이 아닌지만 검사한다', '그렇다. 반드시 -EEXIST인지 검사한다', 'EXPECT_NE의 비교 대상은 0입니다. 검증 강도를 코드 이상으로 확대하면 안 됩니다.'),
        ('Cleanup 테스트가 fake context를 사용하는 이유는?', '바깥 테스트가 계속 실행되면서 내부 자원의 cleanup 전후를 관찰하려고', '모든 assertion 결과를 버리려고', '자원은 fake에 붙이고 assertion은 바깥 test에 기록합니다. 명시적 kunit_cleanup으로 관찰 가능한 중간 경계를 만듭니다.'),
        ('버스 검색 결과 NULL이면 참조 underflow가 전혀 없었다고 증명되는가?', '아니다. 이미 해제된 객체의 refcount를 안전하게 직접 검사할 수 없다', '그렇다. NULL은 모든 과거 참조 연산의 정확성을 보장한다', '소스 주석도 이 한계를 명시합니다. 외부 상태 관찰과 객체 수명 내부의 완전한 검증은 다릅니다.'),
        ('두 번째 probe 준비 전에 reinit_completion을 하는 이유는?', '이전 완료 상태를 지워 새 준비 동작을 검증하려고', '드라이버를 unregister하려고', 'completion 상태만 재초기화합니다. 이전 신호가 남으면 기다림 성공이 새 prepare 호출 때문인지 구분하기 어렵습니다.'),
        ('probe callback은 테스트 context를 어떻게 찾는가?', '장치의 driver를 변환한 뒤 container_of로 바깥 context를 구한다', '장치 이름을 파일에서 검색한다', 'embedded pdrv의 주소 관계를 사용합니다. 구조체를 포함하는 intrusive 자료구조 패턴입니다.'),
        ('첫 driver 테스트에서 timeout EXPECT 실패 뒤 data 비교를 계속할 수 있는가?', '그렇다. 해당 검사는 ASSERT가 아닌 EXPECT다', '아니다. 모든 EXPECT는 즉시 테스트를 중단한다', '전제에 쓰는 ASSERT와 계속 기록하는 EXPECT의 차이가 실제 제어 흐름에 영향을 줍니다.')
    ]
)]
