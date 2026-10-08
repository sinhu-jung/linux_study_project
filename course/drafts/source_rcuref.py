"""Whole rcuref source contracts, state zones and RCU deconstruction race."""
ROWS = [('Rcuref biased count·내부0이 참조1을 뜻하는 이유',
  'include/linux/rcuref.h',
  'rcuref_init',
  'rcuref_init은 cnt-1을 내부 atomic refcnt에 저장합니다. 보통 참조1로 시작하므로 내부 값은 RCUREF_ONEREF=0입니다. 마지막 참조 감소는 '
  '내부0에서 unsigned 표현0xffffffff인 NOREF로 넘어가 negative 결과의 slowpath를 선택합니다. 살아 있는 일반 구간의 read는 내부 값+1입니다. '
  '일반 refcount의 숫자와 내부 저장값을 그대로 비교하면1만큼 다릅니다.',
  '참조 수와 내부 상태값을 두 줄로 나누어 적습니다. 객체가 완전히 초기화되고 수명이 유효한 조건에서 공개합니다. 내부0을 즉시 해제 가능 상태라고 오해하지 않습니다.',
  [('초기 참조1의 내부 값은?', '0이다', '1이다', 'init은 cnt-1을 저장합니다. 내부0은 한 참조가 살아 있는 상태입니다.'),
   ('마지막 감소의 내부0은 어디로 이동하는가?',
    'NOREF인0xffffffff다',
    '자동으로 DEAD를 바로 저장한다',
    '무조건 decrement가 먼저 NOREF를 만들고 slowpath의 CAS가 DEAD전이를 시도합니다.')],
  [('원문과 상태 전이', 'init1..10000의 저장값과 read 결과를 별도로 비교했습니다. 초기cnt0과 이미dead 표시된 객체는 같은 상태가 아닙니다.'),
   ('검사 범위',
    '완전한 header와 lib body를 직렬 unsigned32 atomic·RCU·preempt·warning·ordering hook 모델로 검사했습니다. 실제 grace '
    'period나 동시 실행 및 LKMM의 증명은 아닙니다.')]),
 ('Rcuref read·일반 count와 dead-zone 조회',
  'include/linux/rcuref.h',
  'rcuref_read',
  'read는 내부 값을 unsigned로 읽습니다. c>=RELEASED=0xc0000000이면0을 반환하고 그보다 작으면 c+1입니다. MAXREF=0x7fffffff의 '
  'read는0x80000000으로 내부 biased 값과 다릅니다. 포화구간에도 일반 숫자+1 경로가 적용되지만 그 객체는 해제하지 않는 포화 상태이므로 반환을 정상적인 실제 보유자 '
  '수의 정밀 측정으로 사용하지 않습니다.',
  '조회는 순간 관측값이며 객체 수명을 획득하지 않습니다. DEAD와 SATURATED 구간을 원문 상수와 함께 해석합니다. 조회한0만으로 독립적으로free하지 말고 마지막 put의 '
  '반환 계약을 사용합니다.',
  [('내부 MAXREF의 read 숫자는?',
    '0x80000000이다',
    '0x7fffffff 그대로다',
    '일반구간 read는 저장값+1입니다. 내부 포화 경계와 외부 숫자 표현을 구분합니다.'),
   ('rcuref_read가 새 참조를 획득하는가?',
    '아니며 상태를 읽는다',
    '항상 get도 같이 실행한다',
    '본문은 atomic_read와 구간 판정입니다. 객체 수명을 확보하는 get과 다른 역할입니다.')],
  [('원문과 상태 전이', 'dead구간의0조회와 일반 biased 조회를 독립적으로 검사했습니다.'),
   ('검사 범위',
    '완전한 header와 lib body를 직렬 unsigned32 atomic·RCU·preempt·warning·ordering hook 모델로 검사했습니다. 실제 grace '
    'period나 동시 실행 및 LKMM의 증명은 아닙니다.')]),
 ('Rcuref get fast path·무조건 증가와 수명 전제',
  'include/linux/rcuref.h',
  'rcuref_get',
  'get은 atomic_add_negative_relaxed(1)을 먼저 수행합니다. 새 내부 값의 signed negative 여부가 false이면 성공 true 입니다. '
  'negative이면 saturation/dead slowpath로 갑니다. get 자체의 ordering은 relaxed이며 호출자가 RCU 등으로 객체 메모리의 안정성과 포인터 '
  '획득 ordering을 보장해야 합니다. 성공의 control dependency가 미래 store를 정렬하는 계약은 일반 acquire load와 다릅니다.',
  'RCU 읽기 구간 등에서 유효 포인터를 얻고 get 성공 뒤에만 새 참조로 객체를 사용합니다. 실패 시 객체를 수정하지 않습니다. 이미free된 주소에 get을 호출하여 수명을 '
  '복구할 수 있다고 가정하지 않습니다.',
  [('get fast path가 증가 전에 항상 CAS로0을 검사하는가?',
    '아니며 무조건 증가 후 결과를 검사한다',
    '모든 get이 inc-not-zero CAS loop 다',
    '이 기술은 큰 상태 구간으로 잠깐의 증감을 허용하고 결과를 판정하여 흔한 경로의 경쟁 비용을 줄입니다.'),
   ('get 자체가 일반 acquire ordering을 제공하는가?',
    '아니며 relaxed와 외부 포인터 획득 규약이다',
    '항상 모든payload를 acquire 한다',
    '헤더는 get의 no-ordering전제와 control dependency를 구분합니다. 올바른 포인터 획득 프로토콜이 필요합니다.')],
  [('원문과 상태 전이',
    '원문 설명은 경쟁하는 inc-not-zero CAS loop와의 scalability 차이를 제시합니다. 이 fixture가 실제 성능 benchmark를 한 것은 아닙니다.'),
   ('검사 범위',
    '완전한 header와 lib body를 직렬 unsigned32 atomic·RCU·preempt·warning·ordering hook 모델로 검사했습니다. 실제 grace '
    'period나 동시 실행 및 LKMM의 증명은 아닙니다.')]),
 ('Rcuref get slowpath·dead 거절과 saturation 복구',
  'lib/rcuref.c',
  'rcuref_get_slowpath',
  'slowpath는 새 관측 cnt>=RELEASED이면 DEAD로 되돌리고 false를 반환합니다. 그 아래 cnt>MAXREF이면 warning 조건을 확인하고 '
  'SATURATED=0xa0000000으로 복구하며 true를 반환합니다. 다른 연산과의 경쟁으로 다시 일반 구간을 관측하면 true이며 그대로 둡니다. 포화는 객체를 영원히 '
  '해제하지 않는 누수를 선택하여 위험한 참조 wraparound를 방지합니다.',
  'dead 실패와 포화 성공을 다른 수명 상태로 읽습니다. 포화 성공을 정상적으로 참조 수가 무한정 정확하다는 뜻으로 해석하지 않습니다. 진단과 누수의 의도를 문서의 overflow '
  '방지 설명과 연결합니다.',
  [('dead구간 get slowpath의 반환과 복구는?',
    'false,DEAD 복구다',
    'true,SATURATED로 바꾼다',
    'dead와 saturation 구간은 경계로 구분합니다. 죽은 객체의 참조 획득은 실패해야 합니다.'),
   ('포화 객체의 get slowpath가 false 여서 바로free하도록 하는가?',
    '아니며 true이고해제를막는다',
    '모든negative 결과는즉시free다',
    '포화구간은누수를감수하며overflow의수명손상을막습니다. dead구간의실패와 다릅니다.')],
  [('원문과 상태 전이', '검사 WARN 모델은 true 조건을매번반환하고조건횟수를기록합니다. 실제 WARN_ONCE의출력횟수와같은수치가아닙니다.'),
   ('검사 범위',
    '완전한 header와 lib body를 직렬 unsigned32 atomic·RCU·preempt·warning·ordering hook 모델로 검사했습니다. 실제 grace '
    'period나 동시 실행 및 LKMM의 증명은 아닙니다.')]),
 ('Rcuref put helper·release 감소와 RCU-safe 전제',
  'include/linux/rcuref.h',
  '__rcuref_put',
  '__rcuref_put은 RCU 읽기 보호도 없고 선점 가능한 문맥이면 LOCKDEP warning 조건을 확인합니다. 그 뒤 '
  'atomic_add_negative_release(-1)를 수행합니다. 새값이 일반 구간이면 false로 아직 마지막이 아님을 알립니다. negative이면 slowpath가 '
  '마지막 참조나 포화/dead를 판단합니다. 이 helper는 직접 호출하지 않는 내부 API입니다.',
  '외부에서는 일반rcuref_put 또는 조건이 맞는 put_rcusafe를 선택합니다. 반환 false에서 객체를 해제하지 않습니다. release decrement와 마지막 성공 '
  '뒤 acquire 단계의 역할을 구분합니다.',
  [('일반구간에 머무는 put의 false는?',
    '해제허가가아니다',
    '항상마지막 참조해제성공이다',
    'false는활성참조나경쟁등으로파괴하면안된다는뜻입니다. 실제마지막전이는 slowpath에서판정합니다.'),
   ('__rcuref_put을임의문맥에서직접 호출하는것이정상 사용법인가?',
    '아니며내부 helper 다',
    '모든context에서직접권장한다',
    '헤더는 직접 호출하지말라고명시합니다. 외부 wrapper가문맥 보호와 preempt 계약을제공합니다.')],
  [('원문과 상태 전이', 'RCU-safe조건이 맞는경로와의도적으로보호가없는모델경로의warning조건을비교했습니다. kernellockdep를실행한것은아닙니다.'),
   ('검사 범위',
    '완전한 header와 lib body를 직렬 unsigned32 atomic·RCU·preempt·warning·ordering hook 모델로 검사했습니다. 실제 grace '
    'period나 동시 실행 및 LKMM의 증명은 아닙니다.')]),
 ('Rcuref 마지막 put·NOREF를 DEAD로 CAS 확정',
  'lib/rcuref.c',
  'rcuref_put_slowpath',
  'cnt==NOREF이면 atomic_try_cmpxchg_release로 NOREF에서 DEAD로바꾸려합니다. 성공하면 smp_acquire__after_ctrl_dep 후 '
  'true를반환하여호출자가파괴를예약할수있음을알립니다. CAS 실패는동시 get이일반값으로되돌렸거나다른 put이이미 DEAD를확정했을수있습니다. 이경우재시도없이 false 입니다. '
  '함수자체가free를호출하지는않습니다.',
  'true인호출만마지막처리와제거및 RCU 해제프로토콜을진행합니다. false인호출은상태를다시강제로 DEAD로만들거나중복free하지않습니다. CAS의기대값갱신과실패 '
  '뒤무재시도계약을읽습니다.',
  [('마지막 CAS가실패하면다시성공할때까지반복하는가?',
    '아니며 false를반환한다',
    '항상무한재시도한다',
    '동시획득이나다른해제가유효한상태입니다. 이호출에는파괴권한을주지않고종료합니다.'),
   ('true를반환하는함수본문이객체를직접free하는가?',
    '아니며호출자에게마지막처리를허용한다',
    '즉시allocator를호출한다',
    '본문은 상태 전이와 ordering 단계입니다. 메모리 해제는호출자의 RCU 관리프로토콜에있습니다.')],
  [('원문과 상태 전이', '직렬 모델의강제 CAS 실패에서 ONEREF 또는 DEAD를관측하고 false와acquirehook미실행을검사했습니다.'),
   ('검사 범위',
    '완전한 header와 lib body를 직렬 unsigned32 atomic·RCU·preempt·warning·ordering hook 모델로 검사했습니다. 실제 grace '
    'period나 동시 실행 및 LKMM의 증명은 아닙니다.')]),
 ('Rcuref NOREF 경쟁창·dead 확정 전의 참조 재획득',
  'lib/rcuref.c',
  'rcuref_put_slowpath',
  '마지막decrement는내부0을 NOREF로만듭니다. 아직 DEAD CAS전이면다른 get의무조건증가가 NOREF를 ONEREF로되돌려성공할수있습니다. 이후마지막 put의 '
  'CAS는실패하여파괴하지않습니다. DEAD로확정한뒤의 get은 DEAD+1로dead구간에머물러 false 입니다. 그래서 NOREF와 DEAD를같은완료상태로설명하면경쟁규약을놓칩니다.',
  'RCU로메모리가안정된경쟁창에서만이전이를해석합니다. get/put의사건순서를표로그리고최종파괴허가를받은호출을찾습니다. 임의메모리 해제 뒤의재획득을허용하는규칙으로확대하지않습니다.',
  [('NOREF에서 DEAD CAS전에 get이증가하면?',
    'ONEREF로돌아와성공할수있다',
    '언제나dead실패다',
    '0xffffffff에1을더하면내부0입니다. 죽음확정전의경쟁창과확정된 DEAD를구분합니다.'),
   ('DEAD 확정후 get이곧바로일반값0으로돌아가는가?',
    '아니며dead구간에서거절된다',
    '한 번증가하면항상 ONEREF 다',
    '큰dead구간은잠깐의증가가상태경계를넘지않도록합니다. slowpath는 DEAD로복구합니다.')],
  [('원문과 상태 전이', 'NOREFget복귀와강제 CAS 실패를개별상태모델로확인했습니다. 실제 scheduler경쟁을재현한검사는아닙니다.'),
   ('검사 범위',
    '완전한 header와 lib body를 직렬 unsigned32 atomic·RCU·preempt·warning·ordering hook 모델로 검사했습니다. 실제 grace '
    'period나 동시 실행 및 LKMM의 증명은 아닙니다.')]),
 ('Rcuref saturation과 imbalanced put·파괴를 거절하는 복구',
  'lib/rcuref.c',
  'rcuref_put_slowpath',
  'NOREF 마지막처리를제외한cnt>=RELEASED는균형이맞지않는 put으로warning조건을확인하고 DEAD로복구한뒤 false 입니다. saturation구간은 '
  'SATURATED로돌려놓고 false 입니다. 경쟁으로일반구간을관측하면변경없이 false 입니다. '
  'false는active참조,경쟁,포화,불균형등여러원인이가능하며모두이호출자가파괴하지말라는계약입니다.',
  'put은 보유한참조에한 번씩대응시킵니다. warning을무시하여반복 put으로포화객체를억지로해제하지않습니다. false에서특정숫자상태하나만추론하지않고프로토콜을확인합니다.',
  [('SATURATED의 put이객체파괴 true를반환하는가?',
    '아니며 SATURATED 복구와 false 다',
    '한 번감소하면항상마지막이다',
    '포화객체는수명손상을막기위해해제하지않는상태입니다. 감소로정상참조 수를복구하는것과다릅니다.'),
   ('put의 false를active참조가반드시있다는뜻으로만볼수있는가?',
    '아니며포화나경쟁등도가능하다',
    '항상활성보유자가정확히하나있다',
    '반환은 이호출의파괴권한입니다. 가능한상태와실패원인은여러개입니다.')],
  [('원문과 상태 전이', 'dead불균형과saturation복구를상태값및반환으로검사했습니다. unsafefree는실행하지않았습니다.'),
   ('검사 범위',
    '완전한 header와 lib body를 직렬 unsigned32 atomic·RCU·preempt·warning·ordering hook 모델로 검사했습니다. 실제 grace '
    'period나 동시 실행 및 LKMM의 증명은 아닙니다.')]),
 ('Rcuref put_rcusafe·grace period를 막는 호출 문맥',
  'include/linux/rcuref.h',
  'rcuref_put_rcusafe',
  'put_rcusafe는__rcuref_put을그대로호출합니다. 마지막감소뒤 slowpath가 get/put 쌍과경쟁하는동안객체를해제할grace '
  'period가완료되지않는문맥이필요합니다. RCU 읽기 보호구간과atomic문맥이그조건을만족할수있습니다. release 감소와마지막성공의 acquire '
  'ordering은메모리접근순서이고grace period차단은객체 수명보호라는다른역할입니다.',
  '현재문맥이유효한 RCU 읽기 보호또는atomic조건을갖는지확인합니다. 이름의safe만보고선점가능한임의문맥에적용하지않습니다. true뒤에도 RCU 관리객체의해제예약규칙을지킵니다.',
  [('put_rcusafe가자체적으로항상preempt_disable하는가?',
    '아니며호출문맥의보호를요구한다',
    '항상일반 put과같이disable한다',
    'wrapper는 내부 helper로바로연결됩니다. 외부문맥이grace period경쟁을막는조건을제공해야합니다.'),
   ('release/acquire만있으면객체 수명보호도자동으로충분한가?',
    '아니며 RCU 문맥 조건도필요하다',
    'ordering과수명은항상같다',
    '접근순서를보장하는것과메모리가해제되지않도록하는것은다른조건입니다.')],
  [('원문과 상태 전이', 'RCUheld모델에서마지막 put 성공과warning없음을검사했습니다. 실제 grace period가실행된것은아닙니다.'),
   ('검사 범위',
    '완전한 header와 lib body를 직렬 unsigned32 atomic·RCU·preempt·warning·ordering hook 모델로 검사했습니다. 실제 grace '
    'period나 동시 실행 및 LKMM의 증명은 아닙니다.')]),
 ('Rcuref 일반 put·slowpath 동안 선점 금지와 수명 경합',
  'include/linux/rcuref.h',
  'rcuref_put',
  '일반 put은 preempt_disable한뒤__rcuref_put을수행하고preempt_enable하여원래깊이를복구합니다. 문서는 마지막감소와 DEAD 확정사이에선점되어다른 '
  'get/put 쌍의 RCU 해제가완료되면첫 put의 CAS가해제된메모리를접근할수있는경쟁을설명합니다. 이구간보호가그race를막습니다. 기존깊이가2이면호출 '
  '뒤2이며무조건0으로만들지않습니다.',
  '임의정상문맥에서는일반 wrapper를사용하고반환 true인경우에만파괴예약을진행합니다. preempt 균형과 RCU 해제수명규칙을같이읽습니다. '
  '모델의카운터검사를실제kernel의grace period증명으로보고하지않습니다.',
  [('일반 put의 preempt 보호가감싸는구간은?',
    '감소와 slowpath의마지막판정전체다',
    '반환한뒤free만이다',
    'wrapper는 내부 helper 호출 전disable하고후enable합니다. 마지막 CAS를포함하는보호구간입니다.'),
   ('원래 preempt 깊이2에서일반 put뒤깊이는?', '2다', '언제나0이다', 'disable로3이되고enable로2로돌아옵니다. 상태복구와무조건활성화를구분합니다.')],
  [('원문과 상태 전이',
    'lib의deconstruction race도표,포화와메모리 ordering 설명을원문전체로읽었습니다. fastpath 성능주장을실측benchmark와구분합니다.'),
   ('검사 범위',
    '완전한 header와 lib body를 직렬 unsigned32 atomic·RCU·preempt·warning·ordering hook 모델로 검사했습니다. 실제 grace '
    'period나 동시 실행 및 LKMM의 증명은 아닙니다.')])]

def register(topic,q,detail):
 for title,path,symbol,principle,use,qa,cards in ROWS:
  topic(title,"동기화",path,symbol,"RCU 관리 객체의 참조 카운터 상태와 마지막 해제의 경쟁을 실제 소스로 읽어 수명 보호 기술의 원리를 배웁니다.",principle,use,"내부값과 실제참조수,반환값과파괴권한을나누어표로적고경쟁의사건순서를추적하세요.",*(q(*x) for x in qa),details=[detail(*x) for x in cards])
