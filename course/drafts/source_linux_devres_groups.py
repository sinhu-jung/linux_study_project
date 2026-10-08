"""Devres allocation, lookup, iteration and group unwinding."""
ROWS = [('Devres 할당: 크기 넘침·정렬·0 초기화의 서로 다른 역할',
  '장치와 하드웨어',
  'drivers/base/devres.c',
  '__devres_alloc_node',
  '사용자 데이터 앞에는 목록과 해제 함수 같은 관리 헤더가 필요합니다. 헤더 크기와 데이터 크기를 더한 값이 정수 범위를 넘어 작아지면 실제로 필요한 것보다 작은 메모리를 할당할 수 있어 덧셈 '
  '검사부터 해야 합니다.',
  'check_dr_size는 sizeof(struct devres)+size를 check_add_overflow로 검사하고 넘치면 false입니다. 정상 크기는 '
  'kmalloc_size_roundup으로 할당 버킷 크기에 맞춥니다. alloc_dr는 총 크기로 지정 node에 할당하고 실패면 NULL입니다. __GFP_ZERO가 없을 때만 data 앞까지 '
  'memset해 헤더를0으로 만듭니다. 목록 head를 초기화하고 release를 저장합니다. 공개 __devres_alloc_node는 항상 __GFP_ZERO를 더해 호출하고 진단 이름·요청 '
  '크기를 기록한 뒤 data 주소를 반환합니다.',
  '설명용8비트 크기 값에서 헤더32+데이터240=272를 검사 없이 저장하면16이 됩니다. 실제 커널은 size_t 범위로 검사하며 이런 작아진 크기로 진행하지 않습니다. struct의 data[]는 '
  'ARCH_DMA_MINALIGN 정렬을 요구해 일부 아키텍처의 DMA 정렬 요구에 맞춥니다. 정렬은 크기 넘침 검사나 자동 장치 등록을 대신하지 않습니다.',
  '왜 반환 포인터에 곧바로 kfree하면 안 되나',
  '반환은 관리 할당의 시작 dr이 아니라 내부 data입니다. devres_free는 container_of로 dr을 복원하고 목록에 아직 연결돼 있으면 BUG_ON 뒤 kfree합니다. NULL은 '
  '무시합니다. 새로 할당했다는 것과 devres_add로 장치에 등록했다는 것도 다릅니다. 공개 allocator는 데이터를0으로 만들지만 내부 alloc_dr를 모든 호출에서 같은 의미의 zero '
  'allocator라고 일반화하면 안 됩니다.',
  ('공개 __devres_alloc_node는 __GFP_ZERO를 강제로 더하나요?',
   '그렇습니다. gfp | __GFP_ZERO로 호출합니다.',
   '아닙니다. 헤더만 항상 초기화합니다.',
   '공개 wrapper와 내부 allocator의 조건을 구별해야 합니다.'),
  ('크기 덧셈이 넘치면 작은 값으로 계속 할당하나요?',
   '아닙니다. 검사가 실패해 NULL로 끝납니다.',
   '그렇습니다. wrap된 값이 실제 요청 크기입니다.',
   'check_add_overflow가 오류를 알리고 alloc_dr가 조기 반환합니다.')),
 ('Devres get: 검색과 추가를 하나의 잠금 구간으로 묶기',
  '장치와 하드웨어',
  'drivers/base/devres.c',
  'devres_get',
  '자원이 없으면 새로 넣는 작업을 검색과 추가 두 단계로 따로 하면 다른 CPU도 같은 결론을 내려 중복 항목을 넣을 수 있습니다. 하나의 잠금 구간 안에서 존재 여부를 결정하고 추가해야 합니다.',
  'devres_get은 새 관리 객체의 release 함수를 검색 조건으로 삼습니다. IRQ 상태 저장과 함께 devres_lock을 잡고 find_dr를 호출합니다. 기존 항목이 없으면 '
  'add_dr로 새 항목을 붙이고 new_res를 NULL로 만듭니다. 있으면 기존 항목을 선택합니다. 잠금을 푼 뒤 devres_free(new_res)를 호출해 쓰지 않은 새 할당만 해제하고 '
  '선택된 data를 반환합니다. find_dr는 뒤에서부터 release와 선택적 match를 검사합니다.',
  'A와 B가 같은 조건의 자원을 준비했다면 먼저 잠금 안에서 추가한 A가 남고 B는 그 기존 data를 받아 자기 새 관리 할당을 해제할 수 있습니다. 따라서 호출 뒤에도 입력 new_res가 항상 '
  '자기 소유로 살아 있다고 가정하면 안 됩니다. match가 NULL이면 release가 같은 최신 항목이 대상입니다.',
  '왜 find와 get의 포인터가 참조 카운터 증가를 뜻하지 않나',
  'devres_find는 같은 잠금 아래 찾고 잠금을 푼 뒤 data 또는 NULL을 반환할 뿐 별도 자원 참조를 늘리지 않습니다. get도 이 API 이름의 get이 일반 refcount get과 '
  '동일하다는 뜻이 아닙니다. 장치 정리와 경쟁하지 않는 사용 수명 계약은 필요합니다. 중복으로 버리는 new_res에는 release callback을 호출하지 않고 devres_free만 하므로 그 '
  '데이터가 별도 외부 자원을 소유했다면 정리 책임을 신중히 설계해야 합니다.',
  ('기존 항목을 찾으면 전달한 새 관리 할당은?',
   '해제되고 기존 data를 반환합니다.',
   '항상 두 항목을 모두 등록합니다.',
   'new_res가 그대로 남아 unlock 후 devres_free 대상이 됩니다.'),
  ('devres_find의 반환이 자동 참조 획득인가요?',
   '아닙니다. 잠금 보호 검색 결과 포인터입니다.',
   '그렇습니다. 모든 find는 refcount를 늘립니다.',
   '본문에 자원 참조 증가가 없으며 수명은 장치 관리 계약으로 보장해야 합니다.')),
 ('Devres 순회 callback: safe_reverse가 잠금을 풀어 주지는 않는다',
  '장치와 하드웨어',
  'drivers/base/devres.c',
  'devres_for_each_res',
  '관리 자원들을 검사할 때 목록이 변하는 것을 막아야 하지만, callback 실행 문맥이 어떤지도 함께 알아야 합니다. 반복 매크로에 safe라는 이름이 있어도 어떤 동작이든 허용된다는 뜻은 '
  '아닙니다.',
  'devres_for_each_res는 fn이 NULL이면 바로 반환합니다. 그 외에는 devres_lock을 IRQ 상태 저장과 함께 잡고 뒤에서부터 safe_reverse로 순회합니다. '
  'release 함수가 다르면 건너뛰고 match가 있으며0이면 건너뜁니다. 일치하면 fn(dev,data,사용자data)을 잠금 안에서 호출합니다. 마지막에 unlock합니다. fn은 void여서 '
  '반환값으로 순회를 중단하는 인터페이스가 아닙니다.',
  'A,B,C 순으로 등록된 정상 자원은 조건이 모두 맞으면 C,B,A 순으로 callback이 호출됩니다. fn에서 같은 devres_lock을 얻는 devres_add/remove를 재호출하면 자기 '
  '잠금과 충돌할 수 있습니다. 잠드는 작업도 이 spinlock 보유 문맥에 맞지 않습니다.',
  '왜 일반 class_for_each_device와 구별하나',
  '둘 다 callback을 받지만 실제 잠금 범위가 다릅니다. 이전 장치 클래스 순회는 각 장치 참조를 유지하며 callback을 호출하는 구조이고 여기서는 자원 목록 spinlock을 계속 '
  '보유합니다. safe_reverse는 다음 순회 위치를 임시 저장하는 매크로 성질이지 callback의 자유로운 재진입·수면을 보장하는 선언이 아닙니다. match callback도 같은 잠금 아래 '
  '실행됩니다.',
  ('fn 안에서 잠들어도 되나요?',
   '이 함수의 spinlock 보유 문맥에서는 안 됩니다.',
   'safe_reverse이므로 무엇이든 가능합니다.',
   'fn 호출이 spin_lock_irqsave와 unlock 사이에 있습니다.'),
  ('fn이 반환값7로 순회를 멈출 수 있나요?',
   '아닙니다. fn의 반환형은 void입니다.',
   '그렇습니다. 모든 순회 callback은 비0 중단입니다.',
   'API의 callback 타입과 본문에 중단 검사 여부를 함께 확인해야 합니다.')),
 ('Devres 그룹 경계: close와 remove는 자원 해제가 아니다',
  '장치와 하드웨어',
  'drivers/base/devres.c',
  'devres_open_group',
  '복잡한 초기화의 한 단계에서 얻은 자원들만 실패 시 되돌리고 싶다면 목록에 시작과 끝 경계를 둘 수 있습니다. 그룹은 별도 목록에 자원을 복사하는 대신 같은 자원 목록에 표식을 넣습니다.',
  'devres_open_group은 그룹 객체를 할당해 open/close 두 노드의 식별용 release 함수를 정하고 각각 빈 목록으로 초기화합니다. 진단 이름은 grp<와 grp>이고 크기는0, '
  'color=0입니다. id가 NULL이면 그룹 주소를 id로 쓰고 아니면 전달 id를 씁니다. 잠금 아래 open 노드만 추가해 id를 반환합니다. close는 find_group으로 찾아 '
  'close 노드를 추가하며 없으면 경고입니다.',
  'find_group은 뒤에서 open 표식을 찾습니다. id가 주어지면 주소가 같은 id를, NULL이면 close 노드가 아직 목록에 없는 최신 열린 그룹을 선택합니다. G를 열고 A,B를 추가해 '
  '닫으면 G의 경계 안에 A,B가 놓입니다. close는 A,B를 해제하지 않습니다. remove_group은 두 표식을 떼고 그룹 객체만 해제하므로 A,B는 장치 관리 자원으로 남습니다.',
  '왜 close를 여러 번 호출하면 안 되나',
  'add_dr는 이미 목록에 연결된 노드를 다시 넣으면 BUG_ON입니다. 명시적 id로 이미 닫은 그룹을 다시 찾아 close 노드를 넣는 것을 정상 사용으로 생각하면 안 됩니다. 그룹 표식의 '
  'release 함수들은 실제 자원 해제 동작이 없는 식별자이며 node_to_group이 두 함수 주소를 비교해 어떤 표식인지 알아냅니다. remove 실패는 경고 후 NULL을 kfree하는 '
  '흐름이고 자동 전체 자원 해제로 바뀌지 않습니다.',
  ('remove_group을 호출하면 안의 A,B도 해제되나요?',
   '아닙니다. 그룹 표식과 그룹 객체만 제거합니다.',
   '그렇습니다. remove는 항상 전체 release입니다.',
   '원문은 다른 자원에 영향을 주지 않는다고 명시하며 표식만 list_del_init합니다.'),
  ('id=NULL 검색은 가장 최근 닫힌 그룹도 선택하나요?',
   '아닙니다. 가장 최근 열린 그룹입니다.',
   '그렇습니다. 마지막 그룹이면 상태와 무관합니다.',
   'close 노드의 list_empty 조건을 확인합니다.')),
 ('Devres 그룹 해제: 두 번 순회하며 포함 관계를 판정하기',
  '장치와 하드웨어',
  'drivers/base/devres.c',
  'devres_release_group',
  '선택한 범위 안에 일반 자원뿐 아니라 중첩 그룹의 시작·끝 표식도 있습니다. 범위에 완전히 포함된 그룹만 제거하려면 표식 하나만 보고 판단하지 말고 두 경계의 포함 여부를 확인해야 합니다.',
  'release_group은 잠금 아래 그룹을 찾고 범위를 open 표식부터 닫힌 그룹의 close 다음까지, 아직 열렸으면 목록 끝까지로 정합니다. remove_nodes 첫 순회는 일반 자원을 '
  'todo에 옮겨 개수를 세고 그룹 표식의 color를0으로 만듭니다. 두 번째 순회는 표식마다 color를 올리며 닫는 표식이 아직 없는 열린 그룹은 한 번 더 올립니다. color가2인 그룹만 '
  'open을 todo로 옮기고 close를 제거합니다. 정상 color 범위를 벗어나면 BUG_ON입니다.',
  '닫힌 중첩 그룹의 open과 close가 둘 다 범위에 있으면 color가1→2가 되어 그룹을 제거할 수 있습니다. 하나만 있으면1이라 완전히 포함된 것으로 처리하지 않습니다. 열린 그룹은 open '
  '하나가 범위에 있으면 추가1로2입니다. 함수는 잠금을 풀고 release_nodes를 실행하며 반환 개수는 표식이 아닌 일반 자원 수입니다.',
  '왜 자원 callback은 잠금 밖에서 역순 실행하나',
  'release_nodes는 todo를 뒤에서 순회하며 release(dev,data)를 부르고 관리 객체를 kfree합니다. 일반 자원은 첫 순회에서 원래 순서대로 todo에 이동했으므로 일반 자원 '
  '간에는 최근 것부터 해제됩니다. 그룹 표식의 식별용 callback은 아무 작업도 하지 않습니다. 선택 그룹을 찾지 못하면 경고하고 cnt의 초기값0을 반환하므로0만 보고 찾은 빈 그룹과 미발견을 '
  '구별할 수는 없습니다.',
  ('반환값에 그룹 open/close 표식 개수도 포함되나요?',
   '아닙니다. 일반 자원 수만 셉니다.',
   '그렇습니다. 목록 노드 전부를 셉니다.',
   'cnt 증가는 첫 순회의 일반 자원 분기에만 있습니다.'),
  ('닫힌 그룹 표식 하나만 범위에 있으면 완전 포함인가요?',
   '아닙니다. color1로 남습니다.',
   '그렇습니다. 어떤 표식이든 하나면 충분합니다.',
   '닫힌 그룹은 두 표식의 관찰로 color2가 필요하며 열린 그룹만 추가 가산합니다.')),
 ('Devres 전체 반환: 목록에서 분리한 뒤 역순 정리하기',
  '장치와 하드웨어',
  'drivers/base/devres.c',
  'devres_release_all',
  '드라이버 분리 시 후반에 얻은 자원이 앞서 얻은 자원에 의존할 수 있습니다. 일반 자원을 등록 역순으로 정리하면 이런 의존성을 풀 수 있고, callback을 목록 spinlock 밖에서 실행하면 '
  '긴 정리가 잠금 구간에 들어가지 않습니다.',
  'devres_release_all은 devres_head.next가 NULL이면 경고와 -ENODEV입니다. 빈 목록이면0입니다. 그 외에는 IRQ-safe 잠금 아래 전체 범위를 '
  'remove_nodes로 todo에 분리하고 잠금을 푼 뒤 release_nodes로 정리합니다. 반환은 해제한 일반 자원 수입니다. 그룹 노드도 같은 정리 경로에서 다뤄지지만 식별용 '
  'release는 아무 동작도 하지 않습니다.',
  'A를 얻고 그 위에 B, 다시 C를 얻었다면 일반 자원 callback 순서는 C→B→A입니다. 반환3은 errno3이라는 뜻이 아니라 자원 세 개를 처리했다는 뜻입니다. callback이 해제할 '
  '실제 하드웨어 상태와 외부 할당은 각 release 구현의 책임이며 관리 객체 메모리는 이후 kfree됩니다.',
  '왜 목록이 비었다는 관찰과 장치 전체 경쟁 해결은 다른가',
  '첫 빈 목록 검사는 잠금 밖이고 실제 정리는 잠금 안에서 목록을 분리합니다. 드라이버 분리·초기화와 새 자원 등록의 전체 수명 규칙까지 이 helper 하나로 자동 해결되는 것은 아닙니다. 특히 '
  '등록 중인 장치에 임의로 이 함수를 호출해도 안전하다고 확대하면 안 됩니다. 해제 callback의 순서와 대상 수를 추적하는 모델로 먼저 이해해야 합니다.',
  ('자원 세 개를 정상 처리하면 반환3은 오류인가요?',
   '아닙니다. 일반 자원 개수입니다.',
   '그렇습니다. 0 이외는 항상 errno입니다.',
   '본문은 remove_nodes가 센 cnt를 반환합니다.'),
  ('release callback은 devres_lock 안에서 실행하나요?',
   '아닙니다. todo로 분리하고 잠금을 푼 뒤 실행합니다.',
   '그렇습니다. 모든 devres callback은 잠금 안입니다.',
   'for_each와 release_all은 callback의 잠금 문맥이 다릅니다.'))]

def register(topic,q,detail):
    for title,area,path,symbol,why,principle,use,dt,body,qa,qb in ROWS:
        topic(title,area,path,symbol,why,principle,use,"등록·조회·분리·해제와 잠금 범위 및 반환값의 단위를 구분하세요.",q(title+" · "+qa[0],*qa[1:]),q(title+" · "+qb[0],*qb[1:]),details=[detail(dt,body),detail("검토 범위","Linux v6.12 devres.c의 할당·검색·그룹 분리 및 반환 코드를 대조했습니다. 실제 드라이버 분리 경쟁이나 메모리 고갈을 실행한 검증은 아닙니다.")])
