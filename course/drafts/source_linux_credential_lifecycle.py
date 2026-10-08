"""Credential preparation, publication, temporary override and namespace relation."""
ROWS = [('자격 증명 준비: memcpy 뒤에도 참조를 따로 얻는 이유',
  '격리·보안',
  'kernel/cred.c',
  'prepare_creds',
  '이미 다른 코드에서 읽는 자격 증명 객체를 직접 고치면 검사 중 UID나 그룹 정보가 바뀔 수 있습니다. 수정할 새 객체를 준비한 뒤 공개하는 방식으로 읽는 쪽과 변경하는 쪽의 책임을 나눕니다.',
  'prepare_creds는 cred_jar에서 GFP_KERNEL로 객체를 할당하고 실패하면 NULL입니다. 실제 본문은 task->cred를 old로 읽어 struct cred 전체를 복사합니다. '
  'new의 non_rcu=0, usage=1로 초기화하고 group_info·user·user_ns의 참조를 얻습니다. CONFIG_KEYS이면 네 key 참조를 얻고 CONFIG_SECURITY이면 '
  '복사된 security 포인터를 NULL로 바꿉니다. ucounts 참조나 security_prepare_creds가 실패하면 abort_creds로 정리하고 NULL입니다. 성공은 아직 task에 '
  '설치하지 않은 new입니다.',
  'memcpy가 old의 group_info 주소를 복사해도 그 그룹 객체의 참조 수는 자동으로 늘지 않습니다. 그래서 get_group_info 등이 필요합니다. prepare 성공 후 호출자가 '
  '허용된 변경을 하고 commit하거나, 변경을 포기하면 abort해야 합니다. 이미 commit이 소비한 참조를 다시 abort해서는 안 됩니다.',
  '왜 주석의 objective라는 표현만 따라가면 안 되나',
  '준비 함수의 주석에는 objective 복사라고 쓰였지만 이 버전의 실제 대입은 old=task->cred입니다. override 중에는 task->real_cred와 다를 수 있으므로 포인터를 '
  '정확히 추적해야 합니다. abort_creds도 주석 제목에 unlock이라는 표현이 있지만 본문은 usage 검사와 put_cred이며 명시적인 task mutex unlock을 호출하지 '
  '않습니다. 참조 정리와 잠금 해제를 이름만으로 동일시하지 않습니다.',
  ('memcpy 뒤 get_group_info가 필요한 이유는?',
   '포인터 복사만으로 대상 객체의 참조 수는 늘지 않기 때문입니다.',
   'memcpy가 포인터를 복사하지 못하기 때문입니다.',
   '주소 복사와 소유 참조 획득은 서로 다른 연산입니다.'),
  ('prepare_creds가 성공하면 current의 자격 증명이 이미 교체됐나요?',
   '아닙니다. 수정할 새 객체만 준비됐습니다.',
   '그렇습니다. 성공 반환이 곧 공개입니다.',
   '설치하는 RCU 포인터 대입은 commit 등의 경로에 있습니다.')),
 ('자격 증명 공개: 두 포인터와 두 참조를 함께 바꾸기',
  '격리·보안',
  'kernel/cred.c',
  'commit_creds',
  '프로세스를 대상으로 검사할 때의 real_cred와 현재 작업에 사용하는 cred를 함께 새 자격 증명으로 바꿔야 일반 상태가 일관됩니다. 포인터만 바꾸고 참조 수를 정리하지 않으면 이전 객체가 '
  '누수되거나 새 객체가 일찍 해제됩니다.',
  'commit_creds는 old=task->real_cred이고 task->cred가 old와 다르면 BUG_ON입니다. new usage가 1 이상인지도 검사합니다. 호출자의 new 참조를 '
  '소비하고 get_cred로 주관적 포인터용 참조 하나를 추가합니다. euid·egid·fsuid·fsgid 중 하나가 다르거나 새 capability가 이전 권한의 부분집합이 아니면, mm이 있을 때 dumpability를 suid_dumpable로 바꾸고 pdeath_signal을 0으로 만든 뒤 smp_wmb를 수행합니다. '
  'fsuid/fsgid 변경은 key hook을 호출합니다. user 또는 namespace가 바뀌면 새 process count를 올리고 두 포인터를 rcu_assign_pointer로 공개한 뒤 '
  '이전 count를 내립니다. uid·euid·suid·fsuid 중 하나라도 바뀌면 UID 알림, gid·egid·sgid·fsgid 중 하나라도 바뀌면 GID 알림을 보냅니다. 마지막으로 old 참조 두 개를 내려놓고 0입니다.',
  '다른 소유자가 없다는 단순 예에서 new usage=1로 들어오면 get_cred 후 2가 되어 두 task 포인터가 소유합니다. old에도 두 task 참조가 있었다면 마지막에 2를 줄입니다. '
  '다른 독자가 가진 참조까지 강제로 제거하는 것은 아닙니다. 성공 뒤 caller가 new를 추가로 put하면 넘겨준 소유 참조를 이중으로 내려놓는 오류입니다.',
  '왜 포인터 공개 전에 dumpability를 바꾸나',
  'ID 변화와 덤프 허용 상태의 관찰 순서가 뒤집히면 경쟁하는 ptrace 검사에서 잘못 접근을 허용할 수 있습니다. 원문은 __ptrace_may_access의 읽기 barrier와 짝을 이루는 '
  'smp_wmb를 설명합니다. 두 rcu_assign_pointer는 각각의 공개이며 두 필드를 하나의 원자적 명령으로 동시에 바꾸는 것은 아닙니다. 또 이 함수가 모든 새 '
  'UID·capability의 허용 여부를 새로 판정하는 보안 정책 입구는 아니므로 준비·검사된 new를 전달하는 호출 계약이 필요합니다.',
  ('override 중 cred와 real_cred가 다르면 commit을 호출해도 되나요?',
   '아닙니다. 금지된 상태이며 BUG_ON 조건입니다.',
   '그렇습니다. commit이 자동으로 override를 되돌립니다.',
   '첫 검사에서 task->cred != old를 확인합니다.'),
  ('commit 성공 후 호출자가 넘긴 new 참조를 다시 put해야 하나요?',
   '아닙니다. commit이 그 참조를 소비합니다.',
   '그렇습니다. 매번 다시 put해야 합니다.',
   '원문 계약에 caller reference를 소비한다고 명시하며 두 task 포인터 소유로 이전합니다.')),
 ('임시 자격 증명: override와 revert의 소유권 짝',
  '격리·보안',
  'kernel/cred.c',
  'override_creds',
  '일부 커널 작업은 잠시 다른 자격으로 권한 검사를 수행한 뒤 원래 상태로 돌아가야 합니다. 프로세스 자체의 객관적 자격까지 영구 변경하면 작업 범위를 넘기므로 cred만 교체하는 별도 경로가 '
  '있습니다.',
  'override_creds는 current->cred를 old로 보관하고 get_new_cred(new)로 임시 설치에 필요한 참조를 얻습니다. current->cred만 '
  'rcu_assign_pointer로 바꾼 뒤 old를 반환합니다. get_cred와 달리 get_new_cred를 써 non_rcu 표시를 지우지 않습니다. revert_creds(old)는 현재 '
  '임시 cred를 보관하고 old를 다시 설치한 뒤 임시 cred를 put합니다. real_cred는 이 두 함수에서 바꾸지 않습니다.',
  'old=O 상태에서 A로 override한 반환값 O를 보존합니다. 다시 B로 override하면 반환값 A를 보존합니다. 종료는 revert(A)로 B의 설치 참조를 놓고, revert(O)로 '
  'A의 설치 참조를 놓는 역순입니다. 원래 old의 참조를 중간에 임의로 put하면 복귀할 객체의 수명 계약이 깨집니다.',
  '왜 get_new_cred와 get_cred를 아무렇게나 바꾸면 안 되나',
  '이 코드의 주석은 cred가 현재 스레드의 동기적 작업에 쓰이는 포인터이고 real_cred처럼 다른 스레드가 RCU로 보는 공개 위치가 아니라는 차이를 설명합니다. non_rcu 설정을 유지하는 '
  '선택에는 이런 수명 관리 이유가 있습니다. override는 새 객체를 복제하거나 보안 검사를 자동 수행하지 않습니다. 호출자는 합법적으로 소유한 자격 증명을 사용하고 성공·실패·조기 반환 모두에서 '
  '대응 revert를 해야 합니다.',
  ('override가 current->real_cred도 바꾸나요?',
   '아닙니다. current->cred만 바꿉니다.',
   '그렇습니다. 두 포인터 모두 영구 교체합니다.',
   '본문에 real_cred 대입이 없으며 그 영구 교체는 commit의 역할입니다.'),
  ('O에서 A, 다시 B로 override했다면 복귀 순서는?',
   'A로 복귀한 뒤 O로 복귀합니다.',
   'O로 먼저 복귀하고 나중에 A로 갑니다.',
   '중첩된 임시 소유 관계를 역순으로 풀어야 각 설치 참조가 올바르게 해제됩니다.')),
 ('Capability 부분집합: 같은 namespace와 조상 namespace의 다른 규칙',
  '격리·보안',
  'kernel/cred.c',
  'cred_cap_issubset',
  'capability 비트가 같은 숫자라고 해도 서로 다른 user namespace에서 의미하는 권한 범위가 같지는 않습니다. 자격 증명 변경의 권한 관계를 확인하려면 비트 집합뿐 아니라 '
  'namespace 계층과 소유자도 봐야 합니다.',
  'cred_cap_issubset(set,subset)은 namespace가 같으면 subset의 cap_permitted가 set의 cap_permitted에 포함되는지 검사합니다. 다르면 '
  'subset_ns에서 init_user_ns 전까지 부모를 따라 올라갑니다. 현재 노드의 부모가 set_ns이고 그 노드 owner가 set->euid와 같으면 true이며 끝까지 없으면 '
  'false입니다. commit_creds는 old를 set, new를 subset으로 넘기고 결과가 false인 경우에도 dumpability 변경 조건에 들어갑니다.',
  '같은 namespace에서 old={A,B},new={B}면 포함되고 new={B,C}면 포함되지 않습니다. 다른 namespace에서 P 아래 C 아래 G가 있을 때 set이 P,subset이 '
  'G이면 처음 G의 부모 C를 보고 다음 C의 부모 P를 봅니다. 이때 검사하는 owner는 C의 owner입니다. G의 owner만 같다는 이유로 P와의 조건을 통과하지 않습니다.',
  '왜 이 결과를 모든 작업의 허가 판단으로 쓰면 안 되나',
  '이 helper는 자격 증명 사이의 특정 관계를 계산합니다. namespace가 다른 분기에서는 두 cap_permitted 비트셋을 직접 대조하지 않습니다. 결과 true가 임의의 파일·장치·다른 '
  '프로세스에 접근해도 된다는 일반 허가는 아닙니다. 실제 사용은 commit의 dumpability 조건에 연결되어 있으므로 호출 목적과 반환 의미를 함께 읽어야 합니다.',
  ('같은 namespace에서 old={A,B},new={B,C}이면 부분집합인가요?',
   '아닙니다. C가 old에 없습니다.',
   '그렇습니다. B 하나라도 같으면 됩니다.',
   '부분집합은 new의 모든 원소가 old에 있어야 합니다.'),
  ('P→C→G에서 P 자격과 G 자격을 비교할 때 P 바로 아래에서 보는 owner는?',
   'C의 owner입니다.',
   '항상 G의 owner만 봅니다.',
   '부모가 set_ns인 현재 subset_ns 노드를 찾으며 루프에서 조상을 따라 올라갑니다.'))]

ROWS += [('자격 증명 해제: 참조 0 이후에도 RCU를 기다리는 이유',
  '격리·보안',
  'kernel/cred.c',
  '__put_cred',
  '참조 수를 가진 소유자는 없어졌어도 RCU 읽기 구간에서 이전 포인터를 잠시 읽는 독자가 있을 수 있습니다. 참조 0과 메모리를 즉시 재사용해도 되는 시점은 항상 같지 않습니다.',
  '__put_cred는 usage가 0인지, current의 cred와 real_cred가 해당 객체가 아닌지 BUG_ON으로 확인합니다. non_rcu가 참이면 put_cred_rcu를 직접 '
  '호출하고 그렇지 않으면 call_rcu로 예약합니다. 콜백은 usage가 여전히 0인지 검사하고 아니면 panic입니다. security hook, 네 key 참조, 조건부 group_info, '
  'user, 조건부 ucounts, user namespace를 순서대로 정리한 뒤 cred_jar에 객체를 반환합니다.',
  '마지막 put에서 usage가 1→0이 되어도 non_rcu=0이면 callback이 예약되므로 그 시점에 곧바로 slab free가 실행됐다고 가정하지 않습니다. 반대로 non_rcu 경로는 같은 '
  '해제 함수를 즉시 호출합니다. 어느 경로든 호출자가 마지막 참조를 반납한 뒤 그 포인터를 다시 읽어도 된다는 뜻은 아닙니다.',
  '종료 시 두 포인터를 먼저 비우는 이유와 참조 수',
  'exit_creds는 tsk의 real_cred와 cred를 각각 지역 변수에 보관하고 task 필드를 NULL로 만든 뒤 참조를 내립니다. 두 주소가 같으면 '
  'put_cred_many(cred,2), 다르면 각각 put_cred입니다. 주소가 같아도 소유 참조는 두 개였기 때문에 하나만 내리면 누수됩니다. CONFIG_KEYS_REQUEST_CACHE이면 '
  '캐시된 requested key도 put하고 NULL로 만듭니다. 이 정리는 정상 종료 호출 계약 안에서 이루어지며 임의 task를 비동기로 지워도 된다는 API가 아닙니다.',
  ('non_rcu=0인 마지막 put은 항상 즉시 slab free인가요?',
   '아닙니다. RCU callback으로 해제를 예약합니다.',
   '그렇습니다. 참조 0은 즉시 free와 같은 뜻입니다.',
   '__put_cred의 else는 call_rcu이며 실제 정리는 콜백에 있습니다.'),
  ('exit_creds의 두 포인터가 같은 객체이면 몇 참조를 내리나요?',
   '두 개입니다.',
   '같은 주소이므로 하나입니다.',
   '객체 개수와 포인터들이 소유한 참조 개수는 다릅니다. put_cred_many의 인자가 2입니다.')),
 ('다른 task의 자격 증명 읽기: 0을 되살리지 않는 재시도',
  '격리·보안',
  'kernel/cred.c',
  'get_task_cred',
  '다른 task가 자격 증명을 교체하는 동안 포인터만 읽고 나중에 참조를 늘리면 이미 소유자가 모두 놓은 객체를 되살리는 경쟁이 생길 수 있습니다. RCU 구간에서 읽고 0이 아닌 경우에만 참조를 '
  '늘리는 절차가 필요합니다.',
  'get_task_cred는 RCU 읽기 구간을 열고 __task_cred로 객관적 real_cred를 읽습니다. NULL이면 BUG_ON입니다. get_cred_rcu가 실패하면 새로 포인터를 '
  '읽으며 반복합니다. get_cred_rcu는 atomic_long_inc_not_zero로 참조를 얻고 성공하면 non_rcu=0으로 만듭니다. 참조 획득 뒤 RCU를 풀고 객체를 반환합니다. '
  '호출자는 사용 후 put_cred할 책임이 있습니다.',
  '처음 읽은 A의 usage가 이미 0이면 inc_not_zero는 A를 1로 살리지 않습니다. 루프가 다시 읽어 교체된 B의 유효한 참조를 얻을 수 있습니다. RCU는 이 시도 동안 이전 객체 '
  '메모리 수명을 보호하고, 성공한 참조는 RCU 구간을 나간 뒤에도 반환 객체를 보유하게 합니다. 두 수단의 보호 시간이 다릅니다.',
  '왜 task 자체의 수명 보호도 별도로 필요한가',
  '함수 주석은 호출자가 task 참조를 가지거나 tasklist_lock을 보유해 task가 사라지지 않도록 해야 한다고 명시합니다. cred 참조를 얻는 함수가 입력 task_struct의 수명까지 '
  '자동으로 확보하지 않습니다. 또한 반환 객체는 immutable한 공개 자격 증명으로 읽어야 하며 get_task_cred가 수정 가능한 복사본을 만들지는 않습니다.',
  ('inc_not_zero가 usage=0을 만나면 1로 되살리나요?',
   '아닙니다. 실패해 다시 포인터를 읽습니다.',
   '그렇습니다. RCU 구간이면 항상 되살려도 됩니다.',
   'RCU 메모리 수명과 소유 참조의 유효성은 별개라 조건부 증가를 사용합니다.'),
  ('반환 cred의 참조를 얻으면 입력 task의 수명 보호는 필요 없었나요?',
   '아닙니다. 호출 중 task 수명은 호출자가 보장해야 합니다.',
   '그렇습니다. 함수가 task 참조도 자동 획득합니다.',
   '주석의 별도 전제이며 본문에는 task 참조를 얻는 호출이 없습니다.'))]

def register(topic,q,detail):
    for title,area,path,symbol,why,principle,use,dt,body,qa,qb in ROWS:
        topic(title,area,path,symbol,why,principle,use,"포인터 두 개와 참조 소유권, 성공·실패의 정리 경로를 따라가세요.",q(title+" · "+qa[0],*qa[1:]),q(title+" · "+qb[0],*qb[1:]),details=[detail(dt,body),detail("검토 범위","Linux v6.12의 표시된 함수와 abort/revert 및 cred.h 참조 helper를 대조했습니다. 실제 자격 증명 변경이나 ptrace 경쟁을 실행한 검증은 아닙니다.")])
