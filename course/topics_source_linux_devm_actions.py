"""Managed custom action registration, rollback and explicit release."""
ROWS = [('Devm 정리 동작 등록: 실패 시 or_reset이 즉시 실행되는 이유',
  '장치와 하드웨어',
  'drivers/base/devres.c',
  '__devm_add_action',
  '드라이버 초기화에서 자원을 얻은 뒤 각 오류 분기에 같은 해제 코드를 반복하면 빠뜨리기 쉽습니다. 장치의 관리 자원 목록에 정리 함수를 등록하면 표준 자원 반환 경로에서 호출할 수 있습니다. 하지만 '
  '등록 자체의 메모리 할당도 실패할 수 있습니다.',
  '__devm_add_action은 action_devres 크기의 관리 메모리를 GFP_KERNEL과 NUMA_NO_NODE로 할당하며 실패하면 -ENOMEM입니다. 성공하면 data와 action '
  '포인터를 저장하고 devres_add로 목록에 추가한 뒤0입니다. devres_add는 devres_lock을 IRQ 상태 저장과 함께 잡아 목록에 연결합니다. 실제 정리 wrapper '
  'devm_action_release는 저장한 action(data)를 호출합니다. 등록 성공 시 곧바로 action을 실행하지 않습니다.',
  '이미 확보한 자원 R의 해제 함수 free_R를 일반 add_action으로 등록하다 실패했다면 R 정리는 호출자가 해야 합니다. devm_add_action_or_reset은 내부 add가 '
  '비0이면 그 자리에서 action(data)를 실행한 후 원래 오류를 반환합니다. 성공하면 실행하지 않고 나중 정리 목록에 남습니다. 매크로의 #action은 진단용 이름 문자열을 만드는 '
  '용도입니다.',
  '왜 or_reset 실패 뒤 똑같은 정리를 다시 하면 안 되나',
  '등록 실패라도 or_reset은 action을 이미 호출했을 수 있습니다. 이를 일반 add와 동일하게 취급해 오류 분기에서 다시 free_R를 호출하면 이중 해제가 될 수 있습니다. 자동 관리가 '
  '임의 callback이나 data의 유효성을 검증해 주지도 않습니다. 장치·callback 코드·data의 적절한 수명과 정리 함수의 실행 문맥은 호출자가 지켜야 합니다.',
  ('or_reset의 등록이 실패하면 action은 언제 실행되나요?',
   '오류를 반환하기 전에 즉시 실행됩니다.',
   '실패했으므로 영원히 실행되지 않습니다.',
   'ret이 비0인 분기에서 action(data)를 부른 뒤 ret을 반환합니다.'),
  ('일반 add_action 등록 성공이 action 실행 완료인가요?',
   '아닙니다. 나중 실행할 동작을 등록한 것입니다.',
   '그렇습니다. 등록과 함께 자원을 이미 해제합니다.',
   '성공 경로는 포인터 저장과 devres_add이며 action 직접 호출이 없습니다.')),
 ('Devm remove와 release: 등록 취소와 실제 정리의 차이',
  '장치와 하드웨어',
  'drivers/base/devres.c',
  'devm_release_action',
  '장치에서 자원 소유권을 다른 곳으로 넘길 때는 자동 해제 등록만 취소하고 싶을 수 있습니다. 반대로 더 일찍 자원을 반환하고 싶을 때는 지금 정리 함수까지 실행해야 합니다. 두 동작을 구별하지 '
  '않으면 누수나 이중 해제가 생깁니다.',
  'devm_remove_action과 release_action은 action,data 쌍으로 검색 조건을 만듭니다. match는 함수 포인터와 data 포인터 모두 같은지 검사합니다. remove는 '
  'devres_destroy를 호출해 항목을 제거하고 관리 메모리만 해제합니다. release는 devres_release를 호출해 항목 제거 후 devm_action_release로 '
  'action(data)를 실행하고 관리 메모리를 해제합니다. 둘 다 찾지 못한 오류는 WARN_ON으로 표시하며 void 반환입니다.',
  '같은 함수에 data=A와 data=B가 등록되어 있으면 data=A 요청은 B와 일치하지 않습니다. 동일한 쌍이 여러 번 있다면 find_dr는 목록 뒤에서 검색하므로 가장 최근 일치 항목 하나가 '
  '대상입니다. remove 후 자원 A가 자동 해제됐다고 가정하면 안 되며 release 후 같은 항목이 나중 장치 정리에서 다시 실행되는 것도 아닙니다.',
  '왜 callback을 목록 잠금 밖에서 실행하나',
  'devres_remove는 잠금 아래 찾고 list_del_init한 뒤 잠금을 풀어 res를 반환합니다. devres_release는 그 함수가 돌아온 뒤 release를 호출합니다. 따라서 해당 '
  '목록 spinlock을 보유한 채 사용자 정리 callback을 부르는 구조가 아닙니다. devres_free는 연결된 항목이면 BUG_ON이며 정상 제거된 관리 객체를 해제합니다. data가 '
  '가리키는 실제 자원의 해제 여부는 action 구현에 달려 있습니다. 일반 devres_remove는 미발견이면 NULL을 반환하며 찾은 경우 관리 메모리 자체도 아직 해제하지 않습니다. devres_destroy와 devres_release는 미발견이면 -ENOENT, 처리 성공이면0을 반환합니다. action wrapper는 그 오류를 WARN_ON으로 표시하고 void로 끝납니다.',
  ('devm_remove_action이 action(data)를 호출하나요?',
   '아닙니다. 등록과 관리 메모리만 제거합니다.',
   '그렇습니다. remove와 release는 완전히 같은 동작입니다.',
   'destroy는 release callback을 호출하지 않는다고 주석과 본문이 명시합니다.'),
  ('action 포인터가 같고 data 포인터가 다르면 일치하나요?',
   '아닙니다. 두 포인터 모두 같아야 합니다.',
   '그렇습니다. 함수 이름만 같으면 됩니다.',
   'devm_action_match는 두 동등 비교를 AND합니다.'))]

def register(topic,q,detail):
    for title,area,path,symbol,why,principle,use,dt,body,qa,qb in ROWS:
        topic(title,area,path,symbol,why,principle,use,"등록 메모리와 실제 자원, 정리 호출 여부와 소유권 이전을 구별하세요.",q(title+" · "+qa[0],*qa[1:]),q(title+" · "+qb[0],*qb[1:]),details=[detail(dt,body),detail("검토 범위","Linux v6.12 devres.c의 action·검색·제거·해제와 device.h의 or_reset을 대조했습니다. 실제 드라이버 분리나 이중 해제를 실행한 실험은 아닙니다.")])
