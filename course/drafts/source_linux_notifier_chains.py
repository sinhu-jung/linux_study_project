"""Notifier core, ordering, rollback and synchronization variants."""
ROWS = [('Notifier 등록: 우선순위 정렬과 같은 항목의 중복 방지',
  '동기화',
  'kernel/notifier.c',
  'notifier_chain_register',
  '여러 하위 시스템이 같은 이벤트를 받고 싶을 때 호출 목록을 하드코딩하면 기능을 추가할 때마다 발행자를 수정해야 합니다. callback을 목록에 등록하고 우선순위대로 호출하면 발행자와 수신자를 '
  '분리할 수 있습니다.',
  'notifier_block은 callback·next·priority를 가집니다. core 등록 함수는 포인터를 가리키는 포인터 nl로 연결 위치를 찾습니다. 같은 block 주소를 만나면 경고와 '
  '-EEXIST입니다. 새 priority가 현재보다 크면 그 앞에서 멈춥니다. priority가 같고 unique_priority이면 -EBUSY입니다. 아니면 next로 진행하므로 일반 등록은 '
  '같은 우선순위의 기존 항목 뒤에 삽입합니다. n->next를 정하고 rcu_assign_pointer로 연결한 뒤 trace와 0입니다.',
  'A=100,B=50인 목록에 C=75를 넣으면 A→C→B입니다. D=75를 일반 등록하면 C 뒤, unique 등록이면 C를 만나 -EBUSY입니다. core 삭제는 같은 주소를 찾아 앞 링크를 '
  'n->next로 연결하고 trace 후0이며 끝까지 없으면 -ENOENT입니다. 등록된 priority나 next를 임의 변경하지 않는 정상 목록 계약이 필요합니다.',
  '왜 core 함수의 RCU 대입이 전체 동기화를 대신하지 않나',
  '등록·삭제 core 자체에는 spinlock이나 rwsem을 얻는 코드가 없습니다. atomic/blocking/SRCU wrapper나 raw 호출자가 보호를 제공합니다. '
  'rcu_assign_pointer는 객체 공개 순서에 필요하지만 여러 writer가 동시에 같은 링크를 고쳐도 안전하게 만들어 주는 만능 잠금이 아닙니다. 등록 함수는 block이나 callback '
  '코드를 복사·할당하지 않으므로 호출자는 등록 기간의 객체와 코드 수명을 유지해야 합니다.',
  ('100,50 목록에 75를 등록하면?', '100→75→50입니다.', '75→100→50입니다.', '더 큰 priority가 앞에 오도록 현재보다 큰 위치에서 삽입합니다.'),
  ('같은 priority를 일반 등록하면 항상 -EBUSY인가요?',
   '아닙니다. unique_priority일 때만 거절합니다.',
   '그렇습니다. 모든 목록의 priority는 유일해야 합니다.',
   '일반 wrapper는 false를 넘겨 동일 우선순위 뒤로 이동합니다.')),
 ('Notifier 호출: 마지막 반환값과 STOP 비트의 의미',
  '동기화',
  'kernel/notifier.c',
  'notifier_call_chain',
  '여러 callback의 결과를 합산할지, 한 callback이 후속 호출을 막을지 정해져 있어야 발행자가 결과를 해석할 수 있습니다. notifier는 마지막 반환값과 STOP 비트를 사용하며 일반 '
  'errno와 같은 숫자 규칙이 아닙니다.',
  'notifier_call_chain은 ret=NOTIFY_DONE에서 시작해 next를 미리 읽고 callback(nb,val,v)을 부릅니다. nr_calls가 있으면 실제 호출 수를 증가시킨 뒤 '
  'STOP_MASK가 있으면 중단합니다. 계속하면 다음 노드로 가고 nr_to_call을 줄입니다. 0은 호출 없음, -1은 제한 없이 목록을 돌기 위한 계약입니다. '
  'CONFIG_DEBUG_NOTIFIERS에서 함수 포인터가 kernel text가 아니면 경고 후 다음 노드로 건너뛰며 호출 수와 제한을 줄이지 않습니다.',
  'A가 OK=1, B가 DONE=0이면 최종 결과는1이 아니라 마지막 B의0입니다. B가 STOP=0x8001이면 B까지 호출하고 멈춥니다. BAD=0x8002와 STOP은 모두 중단 비트가 있지만 '
  'BAD의 거부 의미와 STOP의 정상 중단 의미가 다릅니다. 아무 callback도 없으면 DONE=0입니다.',
  '왜 -EINVAL을 그대로 notifier 반환값처럼 쓰면 안 되나',
  'notifier.h는 errno를 STOP_MASK|(OK-err)로 감싸는 notifier_from_errno와 반대로 복원하는 notifier_to_errno를 제공합니다. 예를 들어 '
  '-EPERM=-1이면 0x8002가 되고 복원하면 -1입니다. 일반 errno의 음수 비트를 그대로 반환하는 것과 같은 규약이 아닙니다. val과 v는 수정 없이 callback에 전달되며 데이터의 '
  '타입과 수명은 이벤트별 계약입니다.',
  ('A=OK,B=DONE이고 둘 다 호출하면 최종 결과는?', 'DONE입니다.', 'OK를 누적 보관합니다.', 'ret을 callback마다 덮어써 마지막 반환값을 돌려줍니다.'),
  ('STOP은 반드시 BAD와 같은 오류 거부인가요?',
   '아닙니다. 정상 중단 STOP과 거부 BAD를 구분합니다.',
   '그렇습니다. STOP 비트는 모두 같은 errno입니다.',
   '두 값은 중단 비트를 공유하지만 하위 결과 값이 다릅니다.')),
 ('Robust notifier 복구: 실패한 항목을 빼고 앞에서 다시 호출',
  '동기화',
  'kernel/notifier.c',
  'notifier_call_chain_robust',
  '이벤트 처리 중 일부 수신자가 상태를 바꾼 뒤 후속 수신자가 중단을 요청하면 앞의 수신자에게 되돌림 이벤트를 알려야 할 수 있습니다. 어떤 항목까지 복구할지 호출 수로 기록합니다.',
  'robust core는 up 이벤트를 제한 없이 호출하며 nr를 셉니다. 결과에 STOP_MASK가 있으면 동일 목록의 처음부터 down 이벤트를 최대 nr-1개에 호출합니다. 마지막에 반환하는 '
  '값은 원래 up 결과입니다. 중단을 낸 callback 자체는 nr에 포함되므로1을 빼 복구 대상에서 제외합니다. 복구는 역순이 아니라 같은 순서이고 down도 STOP을 반환하면 더 일찍 멈출 수 '
  '있습니다.',
  'A,B가 진행하고 C가 STOP이면 up 호출 수3입니다. 복구는 down(A),down(B)이며 C와 뒤 D는 제외합니다. C가 BAD가 아니라 정상 STOP이어도 이 구현의 조건은 '
  'STOP_MASK이므로 복구 경로에 들어갑니다. 첫 A가 중단하면 nr-1=0이라 down 호출은 없습니다.',
  '왜 목록이 두 순회 사이에 바뀌면 안 되나',
  '같은 개수만 다시 호출해도 중간에 등록·삭제가 있으면 다른 객체에 down을 보낼 수 있습니다. 원문은 두 순회 동안 정확히 같은 callback 목록을 유지해야 하므로 RCU만의 보호를 사용할 수 '
  '없다고 설명합니다. blocking robust wrapper는 rwsem 읽기 잠금을 두 순회 전체에 걸고 raw robust는 이 책임을 호출자에게 맡깁니다. 이 함수가 자동으로 모든 상태를 '
  '복구하는 것은 아니며 down 이벤트 처리의 의미도 callback이 구현합니다.',
  ('A,B 성공 뒤 C가 중단하면 복구 순서는?', 'A→B입니다.', 'B→A→C입니다.', '처음부터 nr-1개를 호출하는 구현이며 역순 stack unwind가 아닙니다.'),
  ('down callback이 STOP을 반환해도 나머지를 무조건 복구하나요?',
   '아닙니다. down도 일반 call_chain의 중단 규칙을 따릅니다.',
   '그렇습니다. robust는 STOP을 무시합니다.',
   '복구 호출도 같은 notifier_call_chain 함수를 사용합니다.')),
 ('Atomic notifier: writer 잠금과 RCU 독자의 수명',
  '동기화',
  'kernel/notifier.c',
  'atomic_notifier_chain_unregister',
  '인터럽트나 원자 문맥에서 이벤트를 전달할 때 callback 실행 중 잠드는 잠금을 잡을 수 없습니다. 목록 변경은 짧은 spinlock으로 보호하고 실행은 RCU 읽기로 보호하는 구조를 '
  '사용합니다.',
  'atomic 등록과 unique 등록은 spin_lock_irqsave 아래 core 등록에 각각 false/true를 전달합니다. 해제는 같은 잠금 아래 core 삭제를 하고 unlock 뒤 '
  'synchronize_rcu를 호출한 다음 ret을 반환합니다. 이벤트 호출은 rcu_read_lock 안에서 제한 없는 core 순회를 수행합니다. empty 확인은 '
  '!rcu_access_pointer(head)이며 목록을 영구 고정하는 참조를 얻지 않습니다.',
  '해제 대상이 없어 core가 -ENOENT라도 이 wrapper는 synchronize_rcu를 거친 뒤 반환합니다. 삭제로 새 순회가 객체에 도달하지 않게 하고, 이미 객체를 읽고 실행하던 RCU '
  '구간이 끝나기를 기다리는 단계가 별도입니다. callback은 block하면 안 되며 callback 안에서 이 unregister를 호출해서는 안 됩니다.',
  '왜 atomic이라는 이름이 unregister의 무대기를 보장하지 않나',
  '등록의 IRQ-safe spinlock과 해제 후 grace-period 대기는 다른 동작입니다. unregister 본문에 synchronize_rcu가 있으므로 이름만 보고 어떤 원자 문맥에서나 '
  '즉시 끝난다고 추정하면 안 됩니다. 이미 진행 중인 callback을 자기 자신 안에서 기다리는 설계도 성립하지 않습니다. 잠금 종류, 읽기 문맥, 제거 후 대기를 각각 확인해야 합니다.',
  ('대상을 못 찾아도 이 unregister는 RCU 대기를 하나요?',
   '그렇습니다. ret 검사 없이 synchronize_rcu를 호출합니다.',
   '아닙니다. 실패이면 즉시 반환합니다.',
   '잠금을 푼 다음 대기하고 마지막에 ret을 반환하는 순서입니다.'),
  ('empty 결과 false/true를 읽으면 이후 목록도 고정되나요?',
   '아닙니다. 순간의 head 관찰입니다.',
   '그렇습니다. 확인 함수가 모든 writer를 막습니다.',
   'rcu_access_pointer는 여기서 writer 잠금이나 장기 참조를 얻지 않습니다.')),
 ('Blocking notifier: 읽기·쓰기 잠금과 부팅 중 예외',
  '동기화',
  'kernel/notifier.c',
  'blocking_notifier_call_chain',
  'callback이 잠들 수 있는 이벤트는 원자 notifier와 다른 보호가 필요합니다. 실행 중 목록 변경을 막되 여러 실행자가 동시에 목록을 읽는 것은 허용하는 rwsem으로 역할을 나눕니다.',
  '일반 상태의 등록·unique 등록은 내부 wrapper에서 down_write 후 core 등록, up_write입니다. 삭제도 write 잠금입니다. SYSTEM_BOOTING에는 task '
  '전환이 아직 준비되지 않은 상황을 위해 잠금 호출 없이 core로 직접 갑니다. 일반 호출과 robust 호출은 head를 먼저 관찰하고 비어 있지 않으면 down_read 후 각각 core를 '
  '실행하고 up_read합니다. 비어 있으면 DONE입니다.',
  '잠금 전 head가 있더라도 잠금을 얻기 전에 삭제될 수 있습니다. core가 잠금 안에서 head를 다시 읽으므로 빈 목록으로 처리할 수 있습니다. 반대로 처음 관찰이 비어 있으면 곧바로 '
  'DONE일 수 있으므로 동시에 등록된 새 callback까지 반드시 이번 이벤트를 받는다는 보장은 아닙니다.',
  '왜 callback에서 등록·삭제하면 문제가 되나',
  '실행 중에는 읽기 잠금을 가지고 있으므로 같은 체인을 수정하려고 쓰기 잠금을 요구하면 자기 실행이 끝나기를 기다리는 문제가 생길 수 있습니다. 헤더는 call chain 안에서 unregister를 '
  '하지 말라고 명시합니다. 또 rwsem 읽기 잠금은 여러 독자를 허용하므로 callback끼리 무조건 한 번에 하나만 실행된다고 생각해서는 안 됩니다. callback 내부 공유 데이터의 동기화는 '
  '별도로 필요합니다.',
  ('읽기 잠금이면 callback 실행자가 항상 한 명뿐인가요?',
   '아닙니다. 여러 독자 실행이 가능하므로 별도 공유 상태 보호가 필요합니다.',
   '그렇습니다. down_read는 전체 실행을 단일화합니다.',
   'rwsem의 읽기 보호와 writer 배제는 독자끼리의 직렬화와 다릅니다.'),
  ('SYSTEM_BOOTING 등록은 down_write를 수행하나요?',
   '아닙니다. core로 직접 갑니다.',
   '그렇습니다. 부팅에서도 동일하게 잠듭니다.',
   '본문의 조기 반환은 초기 부팅에서 잠드는 잠금 호출을 피합니다.')),
 ('Raw notifier: 보호를 호출자에게 맡기는 네 wrapper',
  '동기화',
  'kernel/notifier.c',
  'raw_notifier_call_chain',
  '일부 하위 시스템은 이미 자신만의 잠금과 수명 규칙을 갖고 있습니다. 그 상황에 추가 잠금 모델을 강제하지 않고 공통 목록·호출 알고리즘만 쓰도록 raw 인터페이스가 있습니다.',
  'raw 등록은 core 등록에 unique=false, 삭제는 core 삭제, 일반 호출은 core call_chain에 nr_to_call=-1과 nr_calls=NULL을 전달합니다. '
  'robust 호출은 up/down 두 순회의 core를 직접 호출합니다. 네 wrapper 모두 자체 spinlock·rwsem·RCU 읽기 구간을 만들지 않습니다.',
  '외부 mutex가 목록 등록·삭제와 두 번의 robust 순회 전체를 보호한다면 호출자가 요구된 불변 목록 계약을 구성할 수 있습니다. 하지만 아무 보호 없이 다른 CPU가 삭제·해제하면 raw '
  '함수가 대신 기다려 주지 않습니다. callback이 잠들 수 있는지도 실제 외부 문맥에 따라 결정해야 합니다.',
  '왜 raw를 가장 빠른 안전한 기본값이라고 고르면 안 되나',
  '잠금 비용이 없다는 것은 안전성 조건이 없어졌다는 뜻이 아니라 책임이 외부에 있다는 뜻입니다. 특히 core에서 next를 먼저 읽는다고 해서 그 다음 객체가 해제돼도 안전한 것은 아닙니다. 보호 '
  '범위·callback 재진입·등록 해제 시점과 코드 수명을 설계한 호출자에게 맞는 인터페이스입니다.',
  ('raw unregister가 기존 독자의 종료를 자동 기다리나요?',
   '아닙니다. core 삭제만 호출합니다.',
   '그렇습니다. 모든 notifier 삭제는 synchronize_rcu입니다.',
   '종류별 wrapper가 다르며 raw에는 그 대기 호출이 없습니다.'),
  ('raw robust에서 두 순회 사이 목록 안정성의 책임은?',
   '호출자에게 있습니다.',
   '함수 이름 robust만으로 자동 보장됩니다.',
   'wrapper는 보호 없이 core로 바로 위임합니다.')),
 ('SRCU notifier: 잠드는 독자와 제거 후 대기',
  '동기화',
  'kernel/notifier.c',
  'srcu_notifier_chain_unregister',
  'callback이 잠들어야 하지만 이벤트 호출은 잦고 등록 해제는 드문 경우, 읽기 쓰기 semaphore 대신 sleepable RCU로 실행 구간을 보호할 수 있습니다. 삭제 후 독자를 기다리는 '
  '비용과 호출 경로의 비용을 다르게 배치합니다.',
  'SRCU 등록·삭제는 일반 상태에서 mutex로 core 변경을 보호합니다. 삭제는 mutex를 푼 뒤 synchronize_srcu를 호출하고 ret을 반환합니다. 부팅 중에는 두 함수 모두 '
  'core로 직접 가므로 삭제의 이 대기도 건너뜁니다. 호출은 srcu_read_lock이 돌려준 idx를 보관하고 core 순회 뒤 같은 idx로 srcu_read_unlock합니다. '
  'callback은 process 문맥에서 block할 수 있습니다.',
  'srcu_init_notifier_head는 mutex를 초기화하고 init_srcu_struct가 음수면 BUG를 내며 head=NULL로 둡니다. void 함수라 초기화 실패를 errno로 '
  '반환하지 않습니다. 동적으로 초기화한 head를 해제할 때는 SRCU cleanup이 먼저 필요하다는 주석이 있습니다. 여러 호출자가 동시에 독자가 될 수 있어 callback 내부의 공유 상태까지 '
  '직렬화되는 것은 아닙니다.',
  '왜 자기 callback에서 삭제하면 안 되나',
  '삭제 후 synchronize_srcu는 이미 진행 중인 읽기 구간이 끝나기를 기다립니다. 자신의 callback이 그 읽기 구간 안이라면 스스로 끝나기를 기다리는 구조가 됩니다. 헤더는 '
  'unregister를 call chain 내부에서 하지 말라고 명시합니다. 이 구조는 잠들 수 있는 읽기를 지원하지만 임의 삭제·재진입·수명 규칙을 없애 주지는 않습니다.',
  ('SRCU read unlock에는 어떤 idx를 넘기나요?',
   '해당 read_lock이 반환한 idx입니다.',
   '항상 0입니다.',
   '지역 변수 idx를 얻은 뒤 같은 값을 unlock에 전달합니다.'),
  ('SRCU 초기화 실패는 -ENOMEM으로 반환되나요?',
   '아닙니다. 이 void helper는 BUG를 호출합니다.',
   '그렇습니다. 반환값을 errno로 검사하면 됩니다.',
   '함수 시그니처와 음수 분기의 BUG를 함께 읽어야 합니다.')),
 ('Die notifier: 스택 이벤트 데이터와 원자 callback',
  '관찰·디버깅',
  'kernel/notifier.c',
  'notify_die',
  '예외 관련 정보에 관심 있는 기능을 고정 호출 목록 대신 이벤트 체인으로 연결할 수 있습니다. 다만 전달하는 레지스터 포인터와 스택 데이터의 수명은 이벤트 실행 범위와 맞아야 합니다.',
  'notify_die는 die_args에 regs,str,err,trapnr,signr을 채웁니다. RCU가 watching 상태가 아니면 RCU_LOCKDEP_WARN을 기록하도록 하고, '
  'die_chain의 atomic notifier를 val과 args 주소로 호출해 결과를 반환합니다. 이 경고를 독립적인 error return이나 자동 RCU 초기화라고 볼 수는 없습니다. '
  'register_die_notifier와 unregister_die_notifier는 각각 atomic 등록·해제 wrapper에 위임합니다.',
  'args 자체는 notify_die의 스택 객체이므로 callback이 그 주소를 저장한 채 함수 반환 뒤 비동기 작업에서 읽으면 안 됩니다. 필요한 값을 이후에 쓰려면 각 필드가 가리키는 대상의 '
  '수명까지 고려해 안전하게 복사·참조해야 합니다. atomic callback 규칙상 잠드는 동작도 허용되지 않습니다.',
  '체인과 진단 코드의 구성',
  'die_chain은 정적 ATOMIC_NOTIFIER_HEAD이고 reboot_notifier_list는 별도의 BLOCKING_NOTIFIER_HEAD입니다. 종료 시 DMA 정리 등 호출을 위한 '
  'reboot 목록과 die 목록은 같은 객체가 아닙니다. CREATE_TRACE_POINTS와 notifier trace 헤더는 등록·해제·실행 관찰 지점을 정의합니다. notify_die와 일부 '
  '호출 함수의 NOKPROBE 표시는 probe 대상으로 쓰지 않도록 선언하며 notrace도 추적 관련 제약입니다. SPDX는 GPL-2.0-only이고 export 매크로는 외부에서 사용할 '
  'helper를 내보냅니다.',
  ('callback이 &args를 저장해 notify_die 반환 뒤 그대로 읽어도 되나요?',
   '아닙니다. args는 이 호출의 스택 객체입니다.',
   '그렇습니다. 이벤트 포인터는 항상 영구 전역입니다.',
   '로컬 struct die_args 주소를 동기 호출에 전달합니다.'),
  ('die notifier와 reboot notifier는 같은 종류의 한 목록인가요?',
   '아닙니다. 각각 atomic과 blocking의 별도 목록입니다.',
   '그렇습니다. 모든 전역 notifier는 하나로 합쳐집니다.',
   '정의된 head 이름과 타입이 다릅니다.'))]

def register(topic,q,detail):
    for title,area,path,symbol,why,principle,use,dt,body,qa,qb in ROWS:
        topic(title,area,path,symbol,why,principle,use,"등록 순서·반환 규약·callback 문맥·제거 후 수명을 함께 추적하세요.",q(title+" · "+qa[0],*qa[1:]),q(title+" · "+qb[0],*qb[1:]),details=[detail(dt,body),detail("검토 범위","Linux v6.12 kernel/notifier.c 전체와 notifier.h의 자료형·계약·반환값을 대조했습니다. 실제 인터럽트·예외 또는 callback 경쟁을 실행한 검증은 아닙니다.")])
