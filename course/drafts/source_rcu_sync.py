"""Whole RCU-sync state machine: GP sharing, replay and callback lifetime."""
ROWS = [('RCU-sync 구조·fast reader와 updater 사이의 상태',
  'include/linux/rcu_sync.h',
  'rcu_sync',
  'rcu_sync는readerfastpath사용을조정하는구조체입니다. gp_state는IDLE/ENTER/PASSED/EXIT/REPLAY의단계이고gp_count는아직 exit '
  '하지않은 updater 수입니다. gp_wait는진입동기화와 spinlock을제공하고cb_head는graceperiod후 callback을예약합니다. 객체자료의 reader '
  '수자체를세는perCPU카운터와 updater의gp_count는다른표현입니다.',
  '한 객체의updaterenter/exit 짝과readerRCU문맥을정합니다. gp_count를자료의실제참조 수로사용하지않습니다. 구조체와예약 '
  'callback의수명을유지하고종료시dtor조건을지킵니다.',
  [('gp_count는무엇을세는가?',
    '진입후아직 exit 하지않은 updater 다',
    '모든fastreader의자료 참조 수다',
    'state전환을공유하는 updater가여럿일수있습니다. 실제읽기보유수는다른상위 자료구조에서관리합니다.'),
   ('gp_state와gp_count는같은숫자를복제한것인가?',
    '아니며단계와보유수가다르다',
    '항상같은값이어야한다',
    '상태머신의단계와활성 updater 수는독립변수입니다. EXIT에count0같은조합을해석해야합니다.')],
  [('조건과 연결', '헤더의extern선언과정적 initializer/DEFINE_RCU_SYNC,includeguard전체를함께읽었습니다.'),
   ('실행 검증 경계',
    '완전한원문 header/body를직렬spin·GP·callbackqueue·warning모델로검사했습니다. 실제 RCU,scheduler,동시실행이나 LKMM '
    '증명은아닙니다.')]),
 ('RCU-sync idle 조회·RCU 읽기 문맥과 READ_ONCE',
  'include/linux/rcu_sync.h',
  'rcu_sync_is_idle',
  'is_idle은 RCU 읽기 보호문맥이없으면LOCKDEP warning조건을확인하고 READ_ONCE(gp_state)가0인지반환합니다.0은 '
  'GP_IDLE이고readerfastpath를사용해도되는상태입니다. 조회가자체적으로 RCU 읽기잠금을획득하거나 updater를배제하지는않습니다. 상위 reader '
  '프로토콜이조회와빠른자료접근을 RCU 규약안에연결합니다.',
  '필요한flavor의 RCU 읽기구간에서사용합니다. READ_ONCE를항상 acquire 나객체 수명획득이라고설명하지않습니다. warning이없는빌드에서도문맥전제를지킵니다.',
  [('is_idle이자체적으로 RCU 읽기 보호를시작하는가?',
    '아니며호출자의보호문맥을요구한다',
    '항상rcu_read_lock을호출한다',
    '본문은 분석warning과상태조회입니다. 헤더주석이요구하는문맥을외부에서마련해야합니다.'),
   ('true가의미하는gp_state는?',
    'GP_IDLE인0이다',
    '아무negativecount나뜻한다',
    '본문은!READ_ONCE(gp_state)입니다. 상태0에서만 fastpath 허용을반환합니다.')],
  [('조건과 연결', '모델에서보호없는idle조회가warning조건을발생시킴을확인했습니다. 실제lockdep탐지실행은아닙니다.'),
   ('실행 검증 경계',
    '완전한원문 header/body를직렬spin·GP·callbackqueue·warning모델로검사했습니다. 실제 RCU,scheduler,동시실행이나 LKMM '
    '증명은아닙니다.')]),
 ('RCU-sync 초기화·정적값과 runtime 전체0 설정',
  'kernel/rcu/sync.c',
  'rcu_sync_init',
  'runtime init은구조체 전체를memset0으로만들고gp_wait를초기화합니다. GP_IDLE=0과gp_count0으로시작합니다. '
  '정적__RCU_SYNC_INITIALIZER도같은 state/count와waitqueueinitializer를연결합니다. 초기화는객체공개전단계이며이미예약 '
  'callback이있는구조체를그냥0으로덮어쓴다고안전한취소가되지는않습니다.',
  '새 객체가공개되기전맞는init경로를사용합니다. 재초기화 전활성 updater와예약 callback이없는수명 조건을보장합니다. waitqueue의 spinlock '
  '초기화를숫자state0대입만으로대체하지않습니다.',
  [('init후 state와 count는?', 'IDLE와0이다', 'PASSED와1이다', '전체0초기화와waitqueue초기화가새조정객체의시작 상태를만듭니다.'),
   ('예약 callback이있는객체를memset하면안전한 callback 취소인가?',
    '아니며수명 정리규약이필요하다',
    '메모리0이자동으로RCUqueue에서삭제한다',
    'queue에있는 callback과객체내용은별개입니다. dtor와활성사용정리없이덮어쓰면수명계약을깨뜨립니다.')],
  [('조건과 연결', 'fixture는정적 initializer와새 객체runtime init둘다시작 상태를검사했습니다.'),
   ('실행 검증 경계',
    '완전한원문 header/body를직렬spin·GP·callbackqueue·warning모델로검사했습니다. 실제 RCU,scheduler,동시실행이나 LKMM '
    '증명은아닙니다.')]),
 ('RCU-sync callback 예약·call_rcu_hurry와 실행 시점',
  'kernel/rcu/sync.c',
  'rcu_sync_call',
  'rcu_sync_call은cb_head와rcu_sync_func를call_rcu_hurry에전달합니다. 함수가즉시 callback을동기실행하는것이아니라 RCU '
  '규약에맞는graceperiod뒤의작업을예약합니다. 상태머신은EXIT중새 enter/exit이들어오는것을 callback 시점에서다시검사합니다. '
  'call과완료를같은시점으로그리면REPLAY필요성을놓칩니다.',
  '예약중cb_head의메모리를살려둡니다. callback 완료전에구조체free하거나다른목적으로cb_head를재사용하지않습니다. '
  '동기synchronize_rcu경로와비동기exitcallback을구분합니다.',
  [('rcu_sync_call이 callback을항상즉시끝내는가?',
    '아니며뒤의RCUcallback을예약한다',
    '일반직접 함수호출과같다',
    '콜백예약과graceperiod이후실행은다른사건입니다. 중간상태변화가있을수있습니다.'),
   ('예약 callback의객체 수명은언제까지보장해야하는가?',
    '완료또는정상dtor정리까지다',
    '예약함수가반환하면바로free한다',
    'cb_head는구조체안에있습니다. callback이아직구조체를접근하므로예약반환이 수명종료가아닙니다.')],
  [('조건과 연결', '모델은 명시적인pendingqueue와GP완료단계로예약과실행을분리했습니다. 실제 RCU 대기시간을측정하지않았습니다.'),
   ('실행 검증 경계',
    '완전한원문 header/body를직렬spin·GP·callbackqueue·warning모델로검사했습니다. 실제 RCU,scheduler,동시실행이나 LKMM '
    '증명은아닙니다.')]),
 ('RCU-sync 첫 enter·IDLE에서 동기 GP를 기다리기',
  'kernel/rcu/sync.c',
  'rcu_sync_enter',
  '첫 enter는waitqueuespinlockIRQ구간에서IDLE을ENTER로바꾸고gp_count를증가합니다. 잠금해제 '
  '뒤synchronize_rcu로graceperiod를기다리고rcu_sync_func를직접 호출하여PASSED로전환합니다. 반환후 reader는 fastpath를사용하지않습니다. '
  '이첫동기 경로는비동기 callback 대기대신특정조건에서더빠를수있는이유를원문이설명합니다.',
  '잠들수있는 updater 문맥과 enter/exit 짝을사용합니다. state가ENTER로바뀐시점과모든이전fastreader전환이확인된반환시점을구분합니다. '
  'spinlock을잡은채graceperiod전체를기다린다고읽지않습니다.',
  [('첫 enter가synchronize_rcu를호출할때rsslock은?',
    '이미해제했다',
    '계속잡은채전체GP를기다린다',
    'state/count 갱신은잠금아래,긴동기GP대기는잠금밖입니다. 원문의두구간을구분합니다.'),
   ('첫 enter 완료후상태는보통?',
    'GP_PASSED 다',
    '바로 GP_IDLE 다',
    '동기GP뒤 callback 처리가 count 양수를보고PASSED로만듭니다. fastreader복귀는뒤의 exit과별도GP입니다.')],
  [('조건과 연결', '모델은 첫 enter의sync1회와PASSED/count1및idlefalse를확인했습니다. 실제 graceperiod는모델사건입니다.'),
   ('실행 검증 경계',
    '완전한원문 header/body를직렬spin·GP·callbackqueue·warning모델로검사했습니다. 실제 RCU,scheduler,동시실행이나 LKMM '
    '증명은아닙니다.')]),
 ('RCU-sync 중첩 enter·count 공유와 상태 대기',
  'kernel/rcu/sync.c',
  'rcu_sync_enter',
  'IDLE이아니면gp_count를늘린뒤gp_state>=PASSED가될때까지wait_event합니다. 이미PASSED/EXIT/REPLAY이면조건이 '
  '성립하여첫GP를다시기다리지않을수있습니다. 다른첫 enter가ENTER단계에있으면GP완료의PASSED와wake를기다립니다. 여러 updater가같은 '
  'slowpath전환을공유하는최적화입니다.',
  'gp_count증가에정확한 exit 한 번을대응시킵니다. 근접한 enter/exit이같은전환을공유하는순서를표로그립니다. enter가곧자료의 writer 간단독 '
  '배제를제공한다고가정하지않습니다.',
  [('이미PASSED에서두 번째 enter가항상새synchronize_rcu를실행하는가?',
    '아니며기존전환을공유한다',
    '항상한GP씩새로기다린다',
    '비IDLE경로는상태조건을기다립니다. 이미성립한조건이 면추가동기GP가필요하지않습니다.'),
   ('rcu_sync_enter만으로여러 updater의자료 쓰기상호 배제가완성되는가?',
    '아니며상위잠금규약이필요하다',
    'gp_count가늘면자동mutex다',
    '여러 updater의 slowpath전환을공유할수있습니다. 상위perCPUrwsem은별도 block으로 writer를배제합니다.')],
  [('조건과 연결', '모델의ENTER중합류는수동으로열린GP창을만들고완료 callback을진행시켜검사했습니다. 실제thread경쟁재현은아닙니다.'),
   ('실행 검증 경계',
    '완전한원문 header/body를직렬spin·GP·callbackqueue·warning모델로검사했습니다. 실제 RCU,scheduler,동시실행이나 LKMM '
    '증명은아닙니다.')]),
 ('RCU-sync callback 우선순위·updater가 있으면 PASSED',
  'kernel/rcu/sync.c',
  'rcu_sync_func',
  'callback은 cb_head로container_of해구조체를찾고IDLE/PASSED에서의예상밖호출을warning합니다. spinlock '
  '아래gp_count가양수이면이전상태보다우선하여PASSED를저장하고대기자를깨웁니다. EXITcallback이예약된뒤새 updater가 enter '
  '했다면fastreader를IDLE로열지않고그 updater의slow전환을유지합니다.',
  'callback 시점의 count를예약시점값으로고정하지말고다시읽는이유를확인합니다. 상태와 count의잠금보호를같이읽습니다. 분석warning과실제 state전환을구분합니다.',
  [('EXITcallback 실행때새 updater의count1이면?',
    'PASSED로가고 fastpath를닫아둔다',
    'count를무시하고무조건IDLE이다',
    'callback은 현재gp_count양수분기를먼저적용합니다. 새 updater가있으면fastreader복귀를막습니다.'),
   ('container_of가찾는부모객체는?',
    'cb_head를가진rcu_sync다',
    '임의 waiter의 task 구조체다',
    'callbackhead는rcu_sync의멤버입니다. 멤버주소에서그조정객체를복원합니다.')],
  [('조건과 연결', '모델에서EXIT중 enter뒤기존 callback을완료시켜PASSED/count1을확인했습니다.'),
   ('실행 검증 경계',
    '완전한원문 header/body를직렬spin·GP·callbackqueue·warning모델로검사했습니다. 실제 RCU,scheduler,동시실행이나 LKMM '
    '증명은아닙니다.')]),
 ('RCU-sync exit·마지막 updater만 callback 시작',
  'kernel/rcu/sync.c',
  'rcu_sync_exit',
  'exit은IDLE이나count0의잘못된사용을warning하고잠금아래 count를하나줄입니다.0이아니면기존 상태를유지합니다. 마지막 exit에서상태PASSED이면EXIT로바꾸고 '
  'callback을예약합니다. EXIT중추가 enter/exit 짝의마지막 exit이면REPLAY로표시합니다. readerfastpath는 exit 호출직후바로열리지않습니다.',
  '활성 enter 한 번당 exit 한 번을수행합니다. exit의warning이불균형 count를안전하게치유하는기능이라고생각하지않습니다. 마지막count0과 '
  'state전이에따라예약효과를구분합니다.',
  [('count2에서하나 exit 하면바로IDLE인가?',
    '아니며count1과slow상태를유지한다',
    '모든 exit이무조건 fastpath를연다',
    '아직다른 updater가전환을사용합니다. 마지막 exit만복귀 callback을시작합니다.'),
   ('PASSED의마지막 exit은어느상태로가는가?',
    'EXIT와 callback 예약이다',
    '즉시IDLE이다',
    'reader가최종 writer 결과를관측할GP뒤에IDLE로돌아갑니다. exit과복귀완료는별개입니다.')],
  [('조건과 연결', '1만번의중첩두 enter/두 exit 모델에서count1유지와마지막예약을비교했습니다.'),
   ('실행 검증 경계',
    '완전한원문 header/body를직렬spin·GP·callbackqueue·warning모델로검사했습니다. 실제 RCU,scheduler,동시실행이나 LKMM '
    '증명은아닙니다.')]),
 ('RCU-sync REPLAY·뒤 exit을 포함하는 새 GP',
  'kernel/rcu/sync.c',
  'rcu_sync_func',
  'count0이며REPLAY를관측한 callback은 EXIT로바꾸고자신을다시예약합니다. 기존 callback을예약한뒤새 enter와 exit이둘다발생했으므로기존GP하나만으로그나중 '
  'exit의작업공개까지보장할수없기때문입니다. 두 번째GP완료에서추가 updater 나REPLAY가없으면IDLE로돌아갑니다. 단순delay이름이아니라사건경계의재동기화입니다.',
  '첫 exit 예약→새 enter→새 exit→첫 callback→재예약→다음 callback 순서를그립니다. 나중 writer 작업이포함되는GP경계를표시합니다. '
  '같은callbackhead의재예약은현재실행 callback의정해진프로토콜안에서읽습니다.',
  [('count0 REPLAY의첫 callback 결과는?',
    'EXIT와새 callback 예약이다',
    '무조건IDLE이다',
    '새 exit의작업을포함하는더뒤GP가필요합니다. 기존 callback 완료만으로 fastpath를열지않습니다.'),
   ('REPLAY가필요한사건은?',
    '예약GP중새 enter와 exit 짝이완료됐다',
    '처음init할때count0이었다',
    'callback 예약 뒤새로운업데이트의완료시점이있어서추가GP를요청합니다. 초기IDLE와다릅니다.')],
  [('조건과 연결', '모델은 REPLAY뒤두 callback 완료사건을분리하여첫EXITpending과다음IDLE를검사했습니다.'),
   ('실행 검증 경계',
    '완전한원문 header/body를직렬spin·GP·callbackqueue·warning모델로검사했습니다. 실제 RCU,scheduler,동시실행이나 LKMM '
    '증명은아닙니다.')]),
 ('RCU-sync 최종 IDLE·마지막 exit 이후 fastpath 복귀',
  'kernel/rcu/sync.c',
  'rcu_sync_func',
  'callback에서활성 count가없고REPLAY도아니면 WRITE_ONCE로IDLE을저장합니다. 원문은 마지막 exit이후적어도한GP가완료되어 '
  'reader가writercriticalsection을관측할수있다고설명합니다. IDLE은자료를free한다는표시가아니라fastreader사용허가입니다. '
  '상태기록과객체의상위수명은구분합니다.',
  'reader는 RCU 문맥의is_idle조회로 fastpath 복귀를판정합니다. updater 종료와 callback 완료를같은시점으로가정하지않습니다. 자료의실제 '
  'reader/writer 보유관리와수명은상위알고리즘에남아있습니다.',
  [('최종IDLE의직접의미는?',
    'readerfastpath사용허가다',
    '모든객체메모리free완료다',
    'RCU-sync는경로조정기술입니다. 자료 수명종료또는allocator해제기록이아닙니다.'),
   ('IDLE로가는 callback이 count 양수분기를무시하는가?',
    '아니며그조건은 먼저PASSED로간다',
    '항상어떤 count도0으로덮는다',
    'callback의분기우선순위를지킵니다. count 양수에서는 fastpath를열지않습니다.')],
  [('조건과 연결', '직렬GP모델의최종 callback뒤is_idletrue와예약없음을확인했습니다.'),
   ('실행 검증 경계',
    '완전한원문 header/body를직렬spin·GP·callbackqueue·warning모델로검사했습니다. 실제 RCU,scheduler,동시실행이나 LKMM '
    '증명은아닙니다.')]),
 ('RCU-sync destructor·REPLAY 정리와 callback barrier',
  'kernel/rcu/sync.c',
  'rcu_sync_dtor',
  'dtor는PASSED와활성gp_count를잘못된수명 조건으로warning합니다. 잠금아래REPLAY를EXIT로바꾸어불필요한재예약을막고현재 state를저장합니다. '
  'IDLE이아니면rcu_barrier로진행중 callback 완료를기다린뒤IDLE을확인합니다. rcu_barrier는queuedcallback '
  '완료규약이며언제나새RCUgraceperiod하나를기다리는synchronize_rcu와같은약속은아닙니다.',
  '모든 updater의 enter/exit 사용이끝난뒤객체 free전에dtor를수행합니다. warning을활성 updater 강제취소API로사용하지않습니다. callback '
  '수명과객체 수명을정리하는목적을 barrier의정확한계약과연결합니다.',
  [('dtor가REPLAY를EXIT로바꾸는목적은?',
    '종료중불필요한 callback 재등록을막는다',
    '새 updater를무조건추가한다',
    '이미사용이끝난수명 정리에서는남은 callback을완료시켜IDLE로가야합니다. replay의추가예약을정리합니다.'),
   ('rcu_barrier는항상새graceperiod를무조건기다리는가?',
    '아니며진행중 callback 완료를기다린다',
    'callback이없어도항상새GP가필수다',
    'v6.12 tree.c의공식주석은 callback이없으면즉시반환할수있다고설명합니다. synchronize_rcu와계약을구분합니다.')],
  [('조건과 연결',
    'barrier 계약은kernel/rcu/tree.c의rcu_barrier공식주석과대조했습니다. fixture는pendingcallbackqueue만flush하는모델입니다.'),
   ('실행 검증 경계',
    '완전한원문 header/body를직렬spin·GP·callbackqueue·warning모델로검사했습니다. 실제 RCU,scheduler,동시실행이나 LKMM '
    '증명은아닙니다.')])]

def register(topic,q,detail):
 for title,path,symbol,principle,use,qa,cards in ROWS:
  topic(title,"동기화",path,symbol,"RCU기반reader경로전환의상태머신과updater공유를실제원문으로읽어graceperiod기술의원리를배웁니다.",principle,use,"state와count,예약callback과GP완료를분리하여enter/exit의시간순서를추적하세요.",*(q(*x) for x in qa),details=[detail(*x) for x in cards])
