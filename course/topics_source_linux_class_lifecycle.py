"""Class registration, sysfs, interfaces, compatibility and release."""
ROWS = [('클래스 sysfs 속성: show·store callback과 -EIO 기본값',
  '장치와 하드웨어',
  'drivers/base/class.c',
  'class_attr_show',
  'sysfs가 공통 kobject와 attribute로 읽기·쓰기를 요청해도 실제 장치 클래스는 자신만의 속성 함수를 가지고 있습니다. 공통 객체에서 포함 구조체를 찾아 올바른 callback으로 '
  '연결하는 어댑터가 필요합니다.',
  'class_attr_show는 container_of 기반 to_class_attr로 class_attribute를 얻고 kobject에서 subsys_private를 찾습니다. ret은 -EIO로 '
  '시작하며 show가 있으면 class·attribute·buf를 전달한 결과로 바꿉니다. store도 같은 구조로 buf와 count를 추가 전달합니다. class_sysfs_ops가 두 '
  'wrapper를 연결하고 class_ktype은 이 ops, release, child_ns_type을 연결합니다. child_ns_type은 해당 class의 ns_type을 반환합니다.',
  'show callback이 없으면 빈 문자열 길이0이 아니라 -EIO입니다. store callback이3을 반환하면 wrapper도3을 반환하며 count 전부를 썼다고 자동으로 바꾸지 않습니다. '
  'show_class_attr_string은 포함 class_attribute_string을 찾아 sysfs_emit으로 문자열과 개행을 출력합니다.',
  '속성 파일 생성과 값 처리의 차이',
  'class_create_file_ns는 class_to_subsys가 실패하면 -EINVAL이며 성공하면 sysfs_create_file_ns에 kobject·attr·ns를 전달하고 sp를 '
  'put한 뒤 결과를 반환합니다. remove는 내부 객체가 없으면 그냥 반환하고 있으면 sysfs_remove_file_ns 후 put합니다. ns는 이 함수가 새 namespace를 만드는 입력이 '
  '아니라 sysfs 호출로 전달하는 식별 문맥입니다. callback 호출은 속성 데이터의 의미를 대신 검증하지 않습니다.',
  ('show callback이 없으면 어떤 결과인가요?', '-EIO입니다.', '빈 파일이므로 항상0입니다.', 'ret의 초기값이 -EIO이며 callback이 있을 때만 덮어씁니다.'),
  ('store callback이3을 반환하면 wrapper 반환은?', '3입니다.', '항상 전달받은 count입니다.', 'wrapper는 callback 결과를 그대로 전달합니다.')),
 ('클래스 등록: namespace 쌍 검사와 단계별 실패 정리',
  '장치와 하드웨어',
  'drivers/base/class.c',
  'class_register',
  '외부에 class 이름을 공개하기 전에 내부 장치 목록·잠금·sysfs 연결을 준비해야 합니다. 중간 단계가 실패했을 때 등록되지 않은 내부 메모리와 진단용 잠금 키가 남지 않도록 정리 경로도 '
  '필요합니다.',
  'class_register는 ns_type만 있거나 namespace callback만 있으면 -EINVAL입니다. 두 값이 모두 있거나 모두 없으면 진행합니다. subsys_private를 '
  'kzalloc해 실패하면 -ENOMEM이고, 장치 klist·interface 목록·glue_dirs kset·동적 lockdep key와 mutex를 초기화합니다. 이름을 설정하고 '
  'class_kset·class_ktype·class 포인터를 연결한 뒤 kset_register와 class_groups 생성 순서로 공개합니다.',
  '이름 설정이나 kset 등록 실패는 err_out으로 가 lockdep key를 해제하고 cp를 kfree합니다. group 생성 실패는 먼저 kobject_del과 이름의 kfree_const를 '
  '수행한 뒤 같은 err_out으로 갑니다. 성공은0입니다. 실패 종류마다 실제 정리 호출이 다르므로 모든 경로에서 무조건 같은 kset_unregister를 호출한다고 써서는 안 됩니다.',
  '왜 klist callback에 get_device와 put_device가 필요한가',
  'klist_class_to_dev는 class 노드를 포함한 device_private에서 device를 찾습니다. klist_class_dev_get/put은 각각 그 device의 참조를 얻고 '
  '놓으며 등록 시 klist_init에 전달됩니다. 이 연결 덕분에 장치 순회 수명과 klist 노드 수명이 함께 관리됩니다. class_register는 NULL class 검사를 하는 일반 입력 '
  '파서가 아니므로 호출자는 유효한 class와 이름·callback을 제공해야 합니다.',
  ('ns_type만 있고 namespace callback이 없으면?',
   '-EINVAL로 거절합니다.',
   '자동으로 기본 namespace를 생성합니다.',
   '두 구성 요소의 짝을 검사하는 명시적 오류 분기가 있습니다.'),
  ('class_groups 생성 실패 시 먼저 하는 정리는?',
   'kobject_del과 이름 해제 후 공통 정리입니다.',
   '성공으로 반환하고 다음 부팅에 정리합니다.',
   '그룹 생성 오류 분기에 별도 정리가 있고 err_out으로 이동합니다.')),
 ('클래스 생성·해제: ERR_PTR와 최종 release의 역할',
  '장치와 하드웨어',
  'drivers/base/class.c',
  'class_create',
  '동적으로 만든 class를 등록 목록에서 빼는 시점과 마지막 참조가 사라져 메모리를 해제하는 시점은 다를 수 있습니다. 생성용 메모리와 내부 등록 객체도 서로 다른 할당입니다.',
  'class_create는 struct class를 0으로 할당하고 name 포인터와 class_create_release callback을 설정한 뒤 class_register를 호출합니다. 실패는 '
  'cls를 kfree하고 ERR_PTR(retval)입니다. 성공은 class 포인터입니다. class_destroy는 ERR_PTR 또는 NULL을 무시하고 그 외에는 '
  'class_unregister를 호출합니다. unregister는 내부 참조를 얻어 group 제거·kset_unregister·subsys_put 순서로 정리합니다.',
  'class_release는 내부 kobject의 최종 release에서 class_release callback이 있으면 호출하고 없으면 debug 메시지를 출력합니다. 이후 내부 lockdep '
  'key와 cp를 해제합니다. class_create가 설치한 callback은 외부 cls를 kfree합니다. 따라서 class_destroy가 단순히 cls를 직접 kfree하는 구현은 아닙니다.',
  '왜 name 포인터와 등록 이름의 수명을 구별하나',
  'class_create의 cls->name=name은 문자열 포인터 대입입니다. 호출자의 임시 스택 문자열을 넣고 곧바로 없애도 안전하다고 생각하면 안 됩니다. class_register가 '
  'kobject 이름을 설정하는 과정과 외부 class->name 보유는 별도입니다. 또 class_register로 직접 만든 정적 class는 자신의 release 계약을 따르며 '
  'class_destroy는 class_create로 만든 객체용이라는 주석을 지켜야 합니다.',
  ('class_create 실패는 항상 NULL인가요?',
   '아닙니다. ERR_PTR에 오류를 담아 반환합니다.',
   '그렇습니다. 모든 생성 API는 NULL만 반환합니다.',
   '함수의 error label은 ERR_PTR(retval)을 반환합니다.'),
  ('class_destroy가 곧바로 외부 cls를 kfree하나요?',
   '아닙니다. unregister 후 release 수명 경로를 사용합니다.',
   '그렇습니다. 참조와 관계없이 직접 free합니다.',
   '본문은 class_unregister 호출이며 class_create_release가 실제 외부 객체를 해제합니다.')),
 ('클래스 인터페이스: 기존 장치 알림과 두 참조 반납',
  '장치와 하드웨어',
  'drivers/base/class.c',
  'class_interface_register',
  '장치가 생기기 전에만 callback을 등록할 수 있다면 이미 존재하는 장치를 놓칩니다. interface 등록 때 기존 장치도 순회해 알리고, interface가 살아 있는 동안 class 내부 '
  '객체를 참조해 수명을 유지합니다.',
  'class_interface_register는 인자나 class가 없으면 -ENODEV, 내부 class 조회 실패면 -EINVAL입니다. 얻은 sp 참조는 등록 기간 동안 보유합니다. sp '
  'mutex 아래 interface를 목록 뒤에 넣고 add_dev가 있으면 현재 장치를 반복해 호출합니다. 반복자를 정리하고 mutex를 푼 뒤0입니다. 헤더상 add_dev는 int 반환이지만 이 '
  '등록 함수는 결과를 검사하지 않습니다.',
  'unregister는 class를 읽고 없으면 반환하며 내부 sp를 다시 얻습니다. mutex 아래 interface 노드를 지우고 remove_dev가 있으면 현재 장치를 순회해 호출합니다. '
  '반복자 정리·unlock 뒤 sp를 두 번 put합니다. 하나는 이번 조회분, 하나는 등록 기간 소유분입니다. add_dev 하나가 음수를 반환해도 이 등록 함수는 자동 롤백하거나 그 오류를 '
  '반환하지 않습니다.',
  '왜 일반 for_each의 재진입 설명을 그대로 적용하면 안 되나',
  '여기의 add_dev/remove_dev는 sp->mutex를 보유한 상태로 실행됩니다. 같은 mutex를 다시 요구하는 등록·해제 경로를 callback에서 호출하면 잠금 문제가 생길 수 '
  '있습니다. 또 unregister는 class_intf 자체를 NULL 검사하기 전에 class 필드를 읽으므로 register와 같은 NULL 입력 허용을 가정하면 안 됩니다. 정상적으로 등록한 '
  '객체의 수명과 짝을 유지해야 합니다.',
  ('add_dev가 음수를 반환하면 이 등록 함수도 그 값을 반환하나요?',
   '아닙니다. 반환값을 확인하지 않고 계속합니다.',
   '그렇습니다. 모든 callback 오류를 자동 전파합니다.',
   '본문은 호출 결과를 변수에 저장하거나 검사하지 않습니다.'),
  ('unregister 끝의 subsys_put 두 번은 중복 오류인가요?',
   '아닙니다. 등록 보유분과 현재 조회분을 각각 반납합니다.',
   '그렇습니다. 주소 하나면 참조도 하나뿐입니다.',
   '소스 주석이 두 번 획득한 참조의 대응 관계를 설명합니다.')),
 ('클래스 호환 링크: 두 번째 생성 실패를 되돌리기',
  '장치와 하드웨어',
  'drivers/base/class.c',
  'class_compat_create_link',
  '장치 분류 방식이 바뀌어도 기존 사용자 프로그램이 예전 sysfs 경로를 찾을 수 있게 임시 호환 링크를 제공할 수 있습니다. 링크 둘을 만들다가 하나만 남으면 기대한 구조와 달라지므로 실패를 '
  '되돌립니다.',
  'class_compat_register는 작은 wrapper를 kmalloc하고 class_kset 아래 이름 있는 kobject를 만듭니다. 실패하면 wrapper를 정리하고 NULL입니다. '
  'create_link는 먼저 호환 class에서 dev 이름으로 dev kobject에 링크합니다. 실패하면 즉시 오류입니다. 선택적 device_link가 있으면 dev 아래 device라는 '
  '이름으로 그 대상에 링크하며 실패 시 첫 링크를 제거합니다. 첫 링크만 필요하고 성공했으면0입니다.',
  '첫 링크 성공, 선택 링크 실패라면 반환은 두 번째 오류이고 첫 링크는 제거됩니다. remove_link는 선택 대상이 있으면 device 링크부터 제거한 뒤 호환 class의 dev 이름 링크를 '
  '제거합니다. compat_unregister는 kobject_put 후 wrapper를 kfree하며 자체 NULL 검사는 없습니다.',
  '왜 이 링크가 장치의 복사나 드라이버 결합은 아닌가',
  'sysfs 링크는 이미 있는 kobject 사이의 이름 연결입니다. 이 코드가 장치를 복제하거나 새 드라이버를 바인딩하지 않습니다. 인자로 받은 class/device의 유효 수명과 호출 순서는 '
  '별도 전제입니다. class_create는 ERR_PTR 실패를 쓰지만 class_compat_register는 NULL 실패를 쓴다는 차이도 호출자가 구분해야 합니다.',
  ('선택적 device 링크 생성이 실패하면 첫 링크는?',
   '제거한 뒤 오류를 반환합니다.',
   '항상 남겨 두고 성공을 반환합니다.',
   '두 번째 sysfs_create_link 오류 분기에서 첫 링크를 remove합니다.'),
  ('class_compat_register의 실패 반환은?', 'NULL입니다.', '항상 ERR_PTR입니다.', '두 할당 실패 분기 모두 NULL이며 class_create와 다릅니다.')),
 ('클래스 등록 조회: 순간 상태와 보유 참조는 다르다',
  '장치와 하드웨어',
  'drivers/base/class.c',
  'class_is_registered',
  '등록 여부를 확인하는 질문과 해당 객체가 앞으로도 살아 있도록 붙잡는 것은 다른 작업입니다. boolean만 저장하고 나중에 포인터를 사용하면 사이에 등록 해제가 일어날 수 있습니다.',
  'class_is_registered는 class_to_subsys로 내부 객체를 찾아 있으면 true로 표시하고 얻었던 sp 참조를 즉시 put합니다. 없으면 false입니다. 반환 순간에는 보유 '
  '참조를 호출자에게 넘기지 않습니다. class_to_subsys는 class 또는 전역 class_kset이 없으면 NULL이고, 목록 잠금 아래 등록 항목의 class 포인터가 같은지 찾은 뒤 '
  'subsys_get한 결과를 반환합니다.',
  '현재 true를 받았더라도 다음 줄 전에 다른 경로가 unregister할 수 있으므로 true를 장기 사용 허가증처럼 쓰면 안 됩니다. 클래스 전체의 초기화 classes_init은 class라는 '
  'kset을 생성하며 실패는 -ENOMEM, 성공은0입니다. 이 전역 kset이 sysfs의 /sys/class를 위한 기반입니다.',
  '파일 구성과 정상 호출 계약',
  '정적 class_kset은 초기에는 NULL이고 초기화 성공 뒤 사용됩니다. to_class_attr는 포함 attribute에서 class_attribute를 찾는 container_of '
  '매크로입니다. class_sysfs_ops와 class_ktype은 속성 접근·release·자식 namespace callback의 연결 표입니다. include들은 장치·메모리·잠금·오류 '
  '포인터·kobject 기반을 제공하며 SPDX는 GPL-2.0입니다. 이 파일은 class를 관리하며 개별 장치 기능 전체를 구현하는 것은 아닙니다.',
  ('class_is_registered가 true이면 호출자가 sp 참조를 보유하나요?',
   '아닙니다. 함수 안에서 이미 put합니다.',
   '그렇습니다. boolean이 참조 소유권을 대신합니다.',
   '반환값은 순간 관찰이며 sp 포인터나 참조를 넘기지 않습니다.'),
  ('classes_init에서 kset 생성 실패의 결과는?', '-ENOMEM입니다.', '무조건 panic입니다.', '본문은 NULL 검사 후 오류를 반환하며 직접 panic하지 않습니다.'))]

def register(topic,q,detail):
    for title,area,path,symbol,why,principle,use,dt,body,qa,qb in ROWS:
        topic(title,area,path,symbol,why,principle,use,"반환 규약과 참조 소유, 잠금 안 callback, 부분 실패 정리를 대조하세요.",q(title+" · "+qa[0],*qa[1:]),q(title+" · "+qb[0],*qb[1:]),details=[detail(dt,body),detail("검토 범위","Linux v6.12 drivers/base/class.c와 class_interface callback 선언을 대조했습니다. 실제 sysfs 변경이나 장치 제거 경쟁을 실행한 검증은 아닙니다.")])
