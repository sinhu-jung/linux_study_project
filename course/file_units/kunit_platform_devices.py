"""Whole-file platform-device allocation, registration and probe notification."""
ROWS = [dict(
    path='lib/kunit/platform.c', title='KUnit 플랫폼 장치: 참조 이전과 probe 완료 알림',
    intro='장치 할당·등록, probe 알림 준비, 드라이버 등록과 두 문서 예제를 전체 분석합니다.',
    principle='등록 전후 자원 상태에 따라 cleanup 함수를 바꾸면 동일 참조를 두 번 반환하는 오류를 피할 수 있습니다.',
    use='상태 전이, 참조 카운팅, notifier, completion과 실패 보상 동작을 학습합니다.',
    area='장치 모델 · 동기화 · 소유권 · callback · 실패 회수',
    sections=[
        ('파일 구성과 할당 context', 'GPL-2.0 파일은 completion,device bus/driver,platform_device와 KUnit platform/resource를 포함합니다. alloc_params는 name과 id를 저장합니다. resource init은 이를 platform_device_alloc에 넘기고 NULL이면 -ENOMEM,성공이면 res->data=pdev와 0을 반환합니다. alloc_exit은 platform_device_put으로 할당 참조를 반환합니다.'),
        ('공개 할당 helper', 'kunit_platform_device_alloc은 지역 params를 만들고 kunit_alloc_resource에 init,exit,GFP_KERNEL과 params 주소를 넘깁니다. init은 등록 과정에서 실행되므로 지역 params를 장기간 보관하지 않습니다. 성공 반환은 resource 자체가 아니라 data인 platform_device 포인터이며 실패 계약은 NULL입니다. 장치 core에 추가하는 작업은 별도 add 함수입니다.'),
        ('종료 callback과 자원 식별', 'add_exit은 platform_device_unregister를 실행합니다. alloc_match는 res->data가 pdev와 같은지,free callback이 alloc_exit인지 둘 다 검사합니다. 포인터만 같은 다른 종류 자원을 오인하지 않도록 동작 종류까지 비교합니다. test 인수는 이 비교에서 사용하지 않습니다. 별도 action wrapper도 platform_device_unregister를 감쌉니다.'),
        ('등록 실패와 참조 이전', 'add는 먼저 platform_device_add를 호출하고 실패하면 그 오류를 바로 반환합니다. 따라서 managed 할당 자원의 free는 기존 put 경로로 남습니다. 성공 후 해당 alloc 자원을 찾으면 free를 add_exit으로 교체하고 find의 추가 참조를 put합니다. 새 put cleanup과 unregister cleanup을 둘 다 추가하는 방식이 아닙니다. unregister도 put을 포함하므로 중복 반환을 피하는 상태 전이입니다.'),
        ('외부 할당 장치의 보상', '일치하는 managed alloc 자원이 없으면 add_action_or_reset으로 unregister를 예약합니다. 예약 실패 시 즉시 unregister가 수행되고 오류가 반환됩니다. 예약 성공은 0입니다. 따라서 platform_device_add 자체가 성공했어도 helper 전체는 cleanup 예약 실패를 보고할 수 있습니다. 이 경로에서 실패 후 장치 포인터를 무조건 다시 put하면 안 되며 소유권 이동을 확인해야 합니다.'),
        ('Probe 알림 구조와 필터', 'probe_nb는 completion 포인터 x,대상 dev,embedded notifier_block을 보관합니다. notifier callback은 container_of로 바깥 객체를 얻고 event가 BUS_NOTIFY_BOUND_DRIVER이면서 data 장치가 대상과 같을 때만 complete(x),NOTIFY_OK를 반환합니다. 다른 이벤트나 다른 장치는 NOTIFY_DONE입니다. 제거 callback은 platform bus에서 notifier를 unregister합니다.'),
        ('준비 함수의 이미 bound인 경로', 'prepare_wait_for_probe는 managed kzalloc으로 knb를 만들고 실패하면 -ENOMEM입니다. callback,dev,x를 저장한 뒤 device_lock 아래 device_is_bound를 확인합니다. 이미 bound이면 unlock,complete(x),kunit_kfree(knb),0 반환 순서입니다. 이 함수는 completion을 init하거나 reinit하지 않으므로 호출자가 미리 초기화해야 합니다.'),
        ('등록과 검사 사이의 경쟁', '아직 bound가 아니면 device lock을 유지한 채 bus_register_notifier를 호출하고 unlock한 뒤 notifier 제거 action을 add_action_or_reset으로 예약합니다. 같은 장치의 binding 상태 확인과 알림 구독 사이 틈을 줄이려는 잠금 배치입니다. 다만 bus_register_notifier의 반환값은 검사하지 않습니다. 따라서 마지막 action 등록이 성공했다고 notifier 등록 자체의 모든 실패까지 처리했다고 주장할 수 없습니다.'),
        ('Completion과 context 수명', '제거 action은 knb 할당보다 나중에 등록되므로 정상 역순 cleanup에서 notifier 제거 후 knb 메모리 회수가 가능합니다. action 등록 실패 시에도 reset callback이 즉시 notifier를 제거합니다. x와 dev 포인터 자체를 복제하거나 별도 get하는 코드는 없습니다. 알림이 올 수 있는 동안 대상 저장소의 수명을 유지해야 하며 completion은 미래의 모든 probe 성공을 저장하는 무제한 이벤트 로그가 아닙니다.'),
        ('첫 문서 예제의 순서', '예제는 DECLARE_COMPLETION_ONSTACK으로 comp를 초기화하고 managed 장치를 alloc/add합니다. 이어 managed driver를 할당해 probe,name,owner를 설정하고 prepare_wait_for_probe를 먼저 호출한 뒤 driver_register합니다. 마지막 wait_for_completion_timeout은 3*HZ로 기다려 0이 아닌지 검사합니다. prepare 함수 자체가 기다리거나 3초 timeout을 강제하는 것은 아닙니다.'),
        ('드라이버 등록과 두 번째 예제', 'driver_register helper는 platform_driver_register 오류를 즉시 반환하고 성공하면 unregister action을 add_action_or_reset으로 예약한 결과를 반환합니다. 두 번째 예제는 platform_driver를 테스트 context 구조체 안에 embed하고 pdev->dev.driver를 to_platform_driver로 변환한 뒤 container_of로 context를 찾습니다. probe가 ctx->data를 기록하고 테스트가 probe 완료 후 확인하는 패턴입니다. context를 별도 전역 변수로 전달할 필요를 줄입니다.'),
        ('전체 범위와 검증', '할당 init/exit,공개 alloc,add_exit와 match,두 action wrapper,add의 두 cleanup 경로,notifier 구조·콜백·제거,prepare의 두 상태,두 문서 예제,driver_register와 네 GPL export를 대조했습니다. allocator helper 내부 실패 회수는 별도 resource 강의의 범위이며 이 파일만으로 모든 OOM 회수가 완전하다고 보장하지 않습니다. 실제 bus binding이나 동시 probe 실험은 실행하지 않았습니다.')
    ], questions=[
        ('Managed alloc 장치를 add하는 데 성공하면 자원 free는 어떻게 바뀌는가?', 'put callback에서 unregister callback으로 교체된다', 'put callback은 유지하고 동일 put을 하나 더 추가한다', 'unregister는 put도 수행합니다. 동일 할당 참조를 두 번 반환하지 않도록 종료 동작을 교체합니다.'),
        ('platform_device_add 자체가 실패하면 기존 managed alloc cleanup은?', 'put을 수행하는 기존 상태로 남는다', '반드시 unregister callback으로 교체된다', '실패 시 자원 검색보다 먼저 반환합니다. 성공 이후의 상태 전이 코드는 실행되지 않습니다.'),
        ('외부 할당 장치에서 cleanup 예약이 실패하면?', 'or_reset이 즉시 unregister하고 오류를 반환한다', '장치를 등록 상태로 둔 채 성공을 반환한다', '장치 등록 성공과 helper 전체 성공을 구분해야 합니다. 후속 cleanup 예약 실패도 반환 오류가 될 수 있습니다.'),
        ('어떤 notifier 이벤트가 completion을 완료하는가?', '대상 장치의 BUS_NOTIFY_BOUND_DRIVER', '플랫폼 bus의 모든 장치에 대한 모든 이벤트', '이벤트 종류와 장치 주소 두 조건을 동시에 검사합니다. 다른 항목은 NOTIFY_DONE입니다.'),
        ('prepare_wait_for_probe가 completion도 초기화하는가?', '아니다. 호출자가 초기화한 completion을 전달해야 한다', '그렇다. 항상 reinit_completion부터 실행한다', '본문은 포인터 저장과 조건부 complete만 합니다. 예제의 DECLARE_COMPLETION_ONSTACK이 초기화 역할을 맡습니다.'),
        ('bus_register_notifier의 오류값을 prepare 함수가 직접 검사하는가?', '아니다. 반환값을 사용하지 않는다', '그렇다. 오류면 반드시 같은 값을 반환한다', '최종 반환은 action 등록 결과입니다. 각 호출의 반환값이 검사되는지를 별도로 추적해야 합니다.'),
        ('두 번째 예제에서 embedded driver로 테스트 context를 찾는 기법은?', 'to_platform_driver와 container_of를 차례로 사용한다', '드라이버 이름을 해시 테이블에서 검색한다', '멤버 주소로 바깥 구조체 주소를 복원하는 intrusive 구조 패턴입니다. 예제에는 이름 기반 context 조회가 없습니다.')
    ]
), dict(
    path='include/kunit/platform_device.h', title='KUnit 플랫폼 장치 선언: 할당·등록·대기의 분리',
    intro='네 공개 함수 선언과 헤더의 타입 의존성을 전체 확인합니다.',
    principle='할당,등록,완료 알림 준비는 반환 타입과 인수가 서로 다른 단계입니다.',
    use='전방 선언,prototype scope와 호출자의 동기화 책임을 학습합니다.',
    area='C 타입 · 인터페이스 · 자원 수명 · 동기화',
    sections=[
        ('구성과 전방 선언', 'GPL-2.0 헤더의 guard 이름은 파일명 device와 달리 _KUNIT_PLATFORM_DRIVER_H입니다. kunit,platform_device,platform_driver를 전방 선언하고 include는 없습니다. 포인터 인수와 반환 선언에는 해당 구조체의 전체 정의가 필요하지 않습니다.'),
        ('네 단계의 선언', 'alloc은 test,name,id로 platform_device *를 반환합니다. add는 test,pdev로 int를 반환합니다. prepare_wait_for_probe는 test,pdev,completion *x를 받고 int를 반환합니다. driver_register는 test,platform_driver *로 int를 반환합니다. 대기 함수 자체나 timeout 인수는 이 헤더에 선언되지 않습니다.'),
        ('Completion 타입 의존성', 'struct completion을 별도로 전방 선언하거나 그 정의 헤더를 포함하지 않은 채 함수 인수에서 사용합니다. 이전에 해당 태그가 보이지 않는 포함 순서에서는 prototype scope의 태그 선언 문제가 생길 수 있으므로 완전히 자급적인 헤더라고 단정하지 않습니다. 구현 파일은 completion.h를 먼저 포함합니다. 이 파일에는 CONFIG 분기나 비활성 no-op stub도 없습니다.'),
        ('검토 범위', 'SPDX,guard,세 전방 선언,네 함수 선언과 끝 guard를 모두 대조했습니다. 반환 실패가 NULL인지 errno인지 등 구체적 동작은 구현 문서와 함께 확인해야 하며 이 선언만으로 객체 소유권 이전이나 cleanup 실행을 증명할 수 없습니다.')
    ], questions=[
        ('prepare_wait_for_probe 선언에 timeout 인수가 있는가?', '없다. completion 포인터만 전달한다', '있다. 항상 3*HZ를 강제한다', '3*HZ는 구현 문서의 별도 wait 예제에 등장합니다. 준비 API와 실제 대기를 구분합니다.'),
        ('이 헤더가 struct completion을 파일 범위에서 별도로 전방 선언하는가?', '아니다. 앞의 전방 선언 목록에는 없다', '그렇다. 세 번째 선언이 completion이다', '전방 선언된 것은 kunit,platform_device,platform_driver입니다. 다른 태그가 앞서 보이는지 포함 순서를 살펴야 합니다.')
    ]
)]
