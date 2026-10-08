"""Class iterator and finder reference ownership."""
ROWS = [('장치 클래스 반복자: 다음으로 이동하면 이전 참조는 끝난다',
  '장치와 하드웨어',
  'drivers/base/class.c',
  'class_dev_iter_next',
  '장치 목록을 순회하는 동안 장치가 제거될 수 있으므로 잠깐 읽은 포인터만 믿고 사용하면 안 됩니다. 반복자가 현재 노드 참조를 보유하면 callback이 장치를 사용하는 동안 메모리 수명을 지킬 수 '
  '있습니다.',
  'class_dev_iter_init은 class_to_subsys로 내부 객체 참조를 얻고 start의 klist 노드 또는 NULL로 반복자를 초기화하며 type과 sp를 저장합니다. next는 '
  'klist_next로 진행하고 type이 없거나 dev->type 포인터가 같은 장치만 반환합니다. 반환 장치는 다음 이동 또는 exit까지 참조됩니다. exit는 klist 반복자를 끝내고 내부 '
  'sp 참조를 내려놓습니다. 중간에 순회를 중단해도 exit가 필요합니다.',
  'A→B→C에서 정상적으로 A를 start로 잡고 klist 참조를 얻었다면 첫 next는 A 다음 B로 진행합니다. start=NULL이면 처음부터입니다. A를 반환받은 뒤 next로 이동하면서 '
  'A의 iterator 참조는 내려갈 수 있으므로 A를 나중에 보관하려면 별도 device 참조가 필요합니다. type 검사는 타입 이름 문자열 비교가 아니라 동일한 device_type 포인터인지의 '
  '비교입니다.',
  '왜 초기화 실패를 무조건 정상 반복자로 취급하면 안 되나',
  'init은 class_to_subsys가 NULL이면 필드를 채우지 않고 반환하는 void 함수입니다. 호출자는 유효한 등록 class와 start를 제공해야 하며 실패한 초기화 뒤 임의로 '
  'next/exit를 호출하면 안 됩니다. 상위 for_each/find wrapper는 class와 내부 객체 유효성을 검사합니다. class_to_subsys 자체는 등록 class 목록을 잠금 '
  '아래 찾고 성공 시 내부 참조를 증가시키므로 그 참조와 현재 장치 참조는 별도로 정리됩니다.',
  ('next가 반환한 장치 참조는 언제까지 iterator가 보장하나요?',
   '다음 이동 또는 exit까지입니다.',
   '장치 포인터를 기억하면 프로그램 종료까지입니다.',
   '주석은 next 또는 exit에서 iterator가 참조를 놓을 수 있음을 명시합니다.'),
  ('type 필터는 device_type의 이름 문자열을 비교하나요?',
   '아닙니다. type 포인터를 비교합니다.',
   '그렇습니다. 이름만 같으면 통과합니다.',
   '조건은 iter->type == dev->type입니다.')),
 ('장치 클래스 검색: match의 비0과 추가 get_device',
  '장치와 하드웨어',
  'drivers/base/class.c',
  'class_find_device',
  '순회 중 발견한 장치를 반복자가 끝난 뒤에도 사용하려면 검색 결과에 독립적인 참조를 넘겨야 합니다. 단순 순회 callback과 검색 callback의 반환 규약도 다릅니다.',
  'class_find_device는 class 또는 내부 sp가 없으면 NULL이고, 초기화 안 된 class에는 경고를 합니다. 반복 중 match(dev,data)가 비0이면 '
  'get_device(dev)로 참조를 더하고 멈춥니다. iterator exit와 처음 얻은 sp put을 수행한 후 dev를 반환합니다. 사용자는 찾은 장치를 다 쓴 뒤 put_device해야 '
  '합니다. 찾지 못하면 next가 NULL인 상태로 반환합니다.',
  'class_for_each_device는 같은 검사와 정리를 하되 callback fn이 비0이면 멈추고 그 값을 그대로 반환합니다. match에서 -1을 오류 뜻으로 반환해도 find는 비0이라 '
  '일치로 처리합니다. fn에서 양수7을 반환하면 for_each는 중단 후7을 반환합니다. 반환값이 모두 통일된 errno 규칙이라고 생각하면 안 됩니다.',
  '왜 두 번의 내부 객체 참조 정리가 보이나',
  '상위 wrapper가 class_to_subsys로 sp를 얻고 iterator 초기화도 별도로 sp를 얻습니다. iterator exit의 subsys_put은 iterator 소유분, '
  'wrapper 끝의 subsys_put은 첫 조회 소유분입니다. 같은 내부 객체 주소여도 각 획득에 대응하는 반납이 필요합니다. callback의 재진입은 허용되지만 다른 코드에서 장치가 사라지지 '
  '않도록 보유하는 참조와 공유 데이터의 동기화는 구분해야 합니다.',
  ('match가 -1을 반환하면 find는 오류를 전파하나요?',
   '아닙니다. 비0이므로 일치로 처리합니다.',
   '그렇습니다. 모든 음수는 errno로 반환합니다.',
   '조건은 if(match(...))이고 함수는 device 포인터를 반환합니다.'),
  ('검색 결과에 get_device를 추가하는 이유는?',
   'iterator가 끝난 뒤에도 호출자가 장치를 보유하도록 하기 위해서입니다.',
   '장치의 전원을 자동으로 켜기 위해서입니다.',
   '참조 수명과 장치 전원 제어는 다른 기능입니다. 반환 뒤 put_device 책임이 생깁니다.'))]

def register(topic,q,detail):
    for title,area,path,symbol,why,principle,use,dt,body,qa,qb in ROWS:
        topic(title,area,path,symbol,why,principle,use,"iterator 소유 참조와 검색 결과 소유 참조, callback 반환 규약을 구분하세요.",q(title+" · "+qa[0],*qa[1:]),q(title+" · "+qb[0],*qb[1:]),details=[detail(dt,body),detail("검토 범위","v6.12 class_to_subsys와 클래스 반복·검색 함수 및 klist 초기화·next·exit를 대조했습니다. 실제 장치 제거 경쟁을 실행한 검증은 아닙니다.")])
