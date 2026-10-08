"""Whole local lock public/internal headers; nonRT/RT distinctions and guards."""
ROWS = [('Local lock API·CPU별 상태의 보호와 공통 wrapper',
  'include/linux/local_lock.h',
  'local_lock',
  'local_lock은 CPU별자료를보호하는이름있는API입니다. '
  'public헤더의init/lock/irq/irqsave/unlock/restore/nestedBH는internal구현으로연결됩니다. 일반kernel과 '
  'PREEMPT_RT는같은public이름에다른구현을선택합니다. 현재 CPU의자료를보호하는것이지서로다른 CPU의모든자료에하나의global잠금을잡는것은아닙니다.',
  '실제변수는per-CPU 저장으로준비하고같은 CPU 자료를접근하는실행 문맥사이의보호조건을정합니다. 사용 CONFIG와 IRQ/BH문맥을확인합니다. 다른 '
  'CPU의자료를직접변경하는경로에local보호만충분하다고가정하지않습니다.',
  [('local_lock이기본적으로연결하는보호대상은?',
    '현재 CPU의local자료다',
    '모든 CPU의한globalmutex다',
    'this_cpu_ptr로현재 CPU의lock을고릅니다. per-CPU와global직렬화의차이를구분합니다.'),
   ('같은public이름이RT와일반 구성에서항상같은명령을실행하는가?',
    '아니며 CONFIG별구현을선택한다',
    '언제나preempt_disable하나뿐이다',
    'publicwrapper는 internal선택을감쌉니다. RT의 migration/spin경로와일반 preempt 경로가다릅니다.')],
  [('전제와 연결', 'public헤더전체의 wrapper와guard연결,includeguard를함께읽었습니다.'),
   ('검사 범위',
    '원본 public/internal 두 헤더를 직렬 CPU·IRQ·preempt·migration·spin·lockdep 모델에서 검사했습니다. 실제 IRQ,RT '
    'scheduler,lockdep 탐지나 cleanup guard 생성 실행 증거는 아닙니다.')],
  1),
 ('Local lock 타입·일반 debug 구성과 빈 구조체',
  'include/linux/local_lock_internal.h',
  'local_lock_acquire',
  'PREEMPT_RT가아니면local_lock_t는구조체입니다. DEBUG_LOCK_ALLOC이있을때dep_map과owner를포함하고없으면GNU C의빈구조체가됩니다. '
  'debug없는실행에서 acquire/release/debug_init은빈함수입니다. 정상보호는 preempt 나 IRQ 문맥제어에서오며debug필드가없다고문맥 '
  '보호까지없어지는것은아닙니다.',
  '자료크기와실행보호를구분합니다. kernel의GNU C빌드문맥을확인하고빈구조체를임의ISO C환경에서동일하게지원한다고가정하지않습니다. lockdep필드의존코드를 '
  'CONFIG와함께읽습니다.',
  [('일반debug없는local_lock_t에반드시물리 spinlock 필드가있는가?',
    '아니며빈구조체일수있다',
    '항상64bitatomiclock필드가있다',
    'nonRTtypedef는debug필드만조건부로가집니다. 일반보호는문맥제어로구현됩니다.'),
   ('빈 acquire 함수이면local_lock이아무문맥 보호도하지않는가?',
    '아니며 wrapper의 preempt 제어가있다',
    '모든보호가사라진다',
    '내부 acquire와상위__local_lock의동작은다릅니다. wrapper의선점제어를함께읽습니다.')],
  [('전제와 연결', 'fixture의debug_no_locks_freed모델이size0을거절하던가정을고쳤습니다. 원문타입을수정하지않았습니다.'),
   ('검사 범위',
    '원본 public/internal 두 헤더를 직렬 CPU·IRQ·preempt·migration·spin·lockdep 모델에서 검사했습니다. 실제 IRQ,RT '
    'scheduler,lockdep 탐지나 cleanup guard 생성 실행 증거는 아닙니다.')],
  1),
 ('Local lock debug acquire·owner와 lockdep map',
  'include/linux/local_lock_internal.h',
  'local_lock_acquire',
  'debugacquire는lock_map_acquire를알리고기존owner가있으면warning조건을확인한뒤current를owner로저장합니다. '
  'release는owner가current와다르면warning조건을확인하고owner=NULL로만든뒤map을 release 합니다. 이표시는잘못된보유관계를분석하는기술이며그자체가 CPU '
  '간실제 spinlock 획득을대신하지않습니다.',
  'acquire와 release의owner전이를정상 짝으로추적합니다. warning을일반동기화수단으로쓰지않습니다. 다른 '
  'task의해제나재귀획득이경고될수있는조건을actual문맥규약과연결합니다.',
  [('debugacquire후owner는?',
    'current다',
    '항상 NULL이다',
    '원문은 기존owner확인후현재 task 포인터를기록합니다. 해제에서 NULL로되돌립니다.'),
   ('lockdepowner표시자체가global실제lock을획득하는가?',
    '아니며분석표시다',
    '모든 CPU를직접직렬화한다',
    '문맥제어와실제RTspinlock은다른실행 경로입니다. 분석map을동기화명령으로해석하지않습니다.')],
  [('전제와 연결', '두 CPU의debug모델에서map5000회짝과owner복구를검사했습니다. 실제lockdep분석기가실행된것은아닙니다.'),
   ('검사 범위',
    '원본 public/internal 두 헤더를 직렬 CPU·IRQ·preempt·migration·spin·lockdep 모델에서 검사했습니다. 실제 IRQ,RT '
    'scheduler,lockdep 탐지나 cleanup guard 생성 실행 증거는 아닙니다.')],
  1),
 ('Local lock 초기화·정적 이름과 runtime class key',
  'include/linux/local_lock_internal.h',
  '__local_lock_init',
  'INIT_LOCAL_LOCK의debuginitializer는name문자열,wait_type_inner와PERCPUlock_type,ownerNULL을설정합니다. '
  'runtime__local_lock_init은staticlock_class_key를만들고debug_check_no_locks_freed와lockdep_init_map_type을호출한뒤owner를초기화합니다. '
  '__spinlock_nested_bh_init은비슷하지만LD_LOCK_NORMAL을연결합니다. 정적 초기화와활성잠금의임의재초기화는같은사용법이아닙니다.',
  '객체가공개되기전에맞는init경로를선택합니다. 잠금 보유중재초기화하거나수명을끝내지않습니다. initmacro가사용되는빌드조건과분석 '
  'helper의compiled-away동작을함께확인합니다.',
  [('runtime init의classkey는자동임시변수인가?',
    '아니며static이다',
    '매번stack수명만가진다',
    'macro 안에서staticstructlock_class_key를선언합니다. 분석분류키의수명과임시stack값을구분합니다.'),
   ('nestedBH분석init의lock_type은?',
    'LD_LOCK_NORMAL이다',
    '언제나LD_LOCK_PERCPU만이다',
    '두initmacro는 마지막locktype인자가다릅니다. 이름이비슷해도설정값을직접대조합니다.')],
  [('전제와 연결', '원문의initializermacro와두runtime init전체를읽었습니다. fixture는lockdepmap등록전체효과를모델링하지않습니다.'),
   ('검사 범위',
    '원본 public/internal 두 헤더를 직렬 CPU·IRQ·preempt·migration·spin·lockdep 모델에서 검사했습니다. 실제 IRQ,RT '
    'scheduler,lockdep 탐지나 cleanup guard 생성 실행 증거는 아닙니다.')],
  1),
 ('일반 Local lock·preempt disable와 현재 CPU 선택',
  'include/linux/local_lock_internal.h',
  '__local_lock',
  'nonRT__local_lock은preempt_disable한뒤this_cpu_ptr(lock)의local_lock_acquire를호출합니다. unlock은해당 CPU의 '
  'release뒤preempt_enable입니다. 같은 CPU에서다른선점가능실행이보호 자료를동시에사용하지못하게하는문맥규약입니다. 실제다른 '
  'CPU와경쟁하는globalspinRMW가추가된구현은아닙니다.',
  '보유 구간동안잠들거나 CPU가달라지는사용을하지않고맞는해제를수행합니다. 현재 CPU의자료를접근하는코드가 IRQ 나softirq에서도실행된다면해당문맥과맞는variant를검토합니다.',
  [('nonRTplainlock의순서는?',
    'preemptdisable뒤현재 CPUacquire다',
    'CPU 선택뒤항상migrationenable다',
    '원문은 먼저선점을막고현재 CPU의분석획득을연결합니다. 사용 CPU와문맥 보호순서를읽습니다.'),
   ('plainlocal_lock만으로hardIRQ재진입까지항상막는가?',
    '아니며IRQvariant와문맥규약을확인한다',
    '항상모든 IRQ도disable한다',
    'plain경로에는local_irq_disable이없습니다. 선점제어와 IRQ 제어를같은것으로보지않습니다.')],
  [('전제와 연결', '깊이2에서획득3,해제2의균형을직렬 모델로검사했습니다.'),
   ('검사 범위',
    '원본 public/internal 두 헤더를 직렬 CPU·IRQ·preempt·migration·spin·lockdep 모델에서 검사했습니다. 실제 IRQ,RT '
    'scheduler,lockdep 탐지나 cleanup guard 생성 실행 증거는 아닙니다.')],
  1),
 ('일반 Local IRQ lock·disable와 save restore의 차이',
  'include/linux/local_lock_internal.h',
  '__local_lock_irqsave',
  'nonRTirq경로는local_irq_disable후현재 CPUacquire이고unlock_irq는 release후local_irq_enable입니다. irqsave는기존 '
  'flags를저장하면서disable하고irqrestore는그저장값을복원합니다. 이미 IRQ가꺼져있던상태를유지해야하면save/restore의짝이의미가있습니다. '
  'restore는무조건enable과다릅니다.',
  '획득전 IRQ 상태를복구해야하는중첩문맥은irqsave/restore의 flags 변수를맞게사용합니다. 다른호출의 flags를혼용하지않습니다. IRQ 꺼짐구간의문맥제약을지킵니다.',
  [('기존IRQoff상태에서irqsave후restore하면?',
    'off로복구된다',
    '항상on이된다',
    'save는이전상태를보존합니다. irqrestore는그상태로돌아가며무조건enable하지않습니다.'),
   ('nonRTunlock_irq와irqrestore는항상동일한가?',
    '아니며enable와저장상태복구가다르다',
    '언제나같은값을쓴다',
    'plainirqvariant는enable합니다. save/restore는호출 전 flags를유지하는별도계약입니다.')],
  [('전제와 연결', '모델에서이전 IRQ 상태0과1을각각검사했습니다. 실제hardwareIRQflags를실행한검사는아닙니다.'),
   ('검사 범위',
    '원본 public/internal 두 헤더를 직렬 CPU·IRQ·preempt·migration·spin·lockdep 모델에서 검사했습니다. 실제 IRQ,RT '
    'scheduler,lockdep 탐지나 cleanup guard 생성 실행 증거는 아닙니다.')],
  1),
 ('RT Local lock·migration 고정과 per-CPU spinlock',
  'include/linux/local_lock_internal.h',
  '__local_lock',
  'PREEMPT_RT의local_lock_t는spinlock_t입니다. __local_lock은migrate_disable뒤현재 CPU의 spin_lock을획득합니다. '
  'unlock은spin_unlock뒤migrate_enable입니다. 원문은 criticalsection이선점가능하게유지된다고설명합니다. '
  'CPU이동을막는것과선점을모두막는것은다른제어이며이경로를nonRTpreemptdisable과동일하게설명하면안됩니다.',
  'RT의잠금및실행 문맥규칙에맞는사용을확인합니다. 보호 자료는 CPU별이며보유중선점가능성과 migration 고정의차이를읽습니다. '
  'spinlock이라는이름만으로nonRT명령과같다고가정하지않습니다.',
  [('RTplainlocal_lock의먼저수행하는제어는?',
    'migrate_disable이다',
    '항상preempt_disable이다',
    '원문RTmacro는 migration을고정하고현재 CPUspinlock을획득합니다. 일반 구성의선점disable와다릅니다.'),
   ('RT해제에서migrationenable은spinunlock전인가?',
    '아니며spinunlock뒤다',
    '항상unlock전에 CPU이동을허용한다',
    '보호잠금을해제한후 migration 고정을풀어현재 CPU 자원의짝을유지합니다.')],
  [('전제와 연결', '직렬RTspin모델에서 preempt 깊이유지와migration1→0,spin획득/해제짝을검사했습니다.'),
   ('검사 범위',
    '원본 public/internal 두 헤더를 직렬 CPU·IRQ·preempt·migration·spin·lockdep 모델에서 검사했습니다. 실제 IRQ,RT '
    'scheduler,lockdep 탐지나 cleanup guard 생성 실행 증거는 아닙니다.')],
  2),
 ('RT Local IRQ variant·flags0과 IRQ 의미의 변화',
  'include/linux/local_lock_internal.h',
  '__local_lock_irqsave',
  'RT__local_lock_irq는plainlocal_lock에연결됩니다. irqsave는 flags 타입을unsignedlong으로확인하고 '
  'flags=0으로만든뒤plainlock을호출합니다. unlock_irqrestore는plainunlock에연결되어 flags를사용하지않습니다. 이RT소스는일반 구성처럼 IRQ '
  '상태를직접disable/save/restore하는명령을추가하지않습니다.',
  'RT에서irq이름만보고hardIRQ가꺼진다고판단하지않습니다. 실제공유자료와interrupt문맥의보호조건을별도로검토합니다. publicflags인자의정확한타입을지키며일반 '
  '구성과RT를구분합니다.',
  [('RTirqsave가 flags에저장하는값은?',
    '0이다',
    '언제나실제 IRQ 상태다',
    '원문은 typecheck후 flags=0을대입합니다. nonRTlocal_irq_save와다른선택입니다.'),
   ('RTirqrestore가 flags로hardwareIRQ상태를복원하는가?',
    '아니며plainunlock에연결된다',
    '항상local_irq_restore를실행한다',
    'RTmacro의연결을직접읽습니다. 같은public이름의 CONFIG별효과를구분해야합니다.')],
  [('전제와 연결', '모델의이전 IRQ 상태0/1은RT경로에서유지되고flags0을확인했습니다. 실제RTIRQ정책전체를검증한것은아닙니다.'),
   ('검사 범위',
    '원본 public/internal 두 헤더를 직렬 CPU·IRQ·preempt·migration·spin·lockdep 모델에서 검사했습니다. 실제 IRQ,RT '
    'scheduler,lockdep 탐지나 cleanup guard 생성 실행 증거는 아닙니다.')],
  2),
 ('Local nested BH·softirq 문맥의 전제',
  'include/linux/local_lock_internal.h',
  '__local_lock_nested_bh',
  'nonRTnestedBH는lockdep_assert_in_softirq후현재 CPU의local_lock_acquire를호출하고해제는local_lock_release입니다. '
  '자체적으로새preemptdisable이나IRQdisable을추가하지않습니다. RT는lockdep_assert_in_softirq_func후현재 CPUspinlock을잡고해제합니다. '
  'nested이름은필요한softirq실행 문맥이이미갖춰진사용규약을읽어야한다는뜻입니다.',
  'softirq문맥이아닌임의코드에서이variant를보호대용으로사용하지않습니다. 기존BH문맥의 CPU이동및선점조건을확인합니다. 일반plainlock처럼모든문맥을자체적으로준비하는 '
  'wrapper 라고가정하지않습니다.',
  [('nonRTnestedBH가처음에확인하는문맥은?',
    'softirq다',
    '언제나사용자processcontext다',
    '원문은 lockdep_assert_in_softirq를호출합니다. API의문맥전제를먼저확인합니다.'),
   ('RTnestedBH가plainRTlock처럼자체migrate_disable을추가하는가?',
    '아니며해당 macro에는없다',
    '언제나 migration 깊이를하나늘린다',
    'RTnestedmacro는 assert와 spin_lock 입니다. 상위문맥의조건과내부명령을구분합니다.')],
  [('전제와 연결', 'fixture는softirq모델문맥에서정상획득/해제만검사했습니다. 실제BH문맥전체의동기화증명은아닙니다.'),
   ('검사 범위',
    '원본 public/internal 두 헤더를 직렬 CPU·IRQ·preempt·migration·spin·lockdep 모델에서 검사했습니다. 실제 IRQ,RT '
    'scheduler,lockdep 탐지나 cleanup guard 생성 실행 증거는 아닙니다.')],
  1),
 ('Local lock guard·범위 종료에 대응 해제 연결',
  'include/linux/local_lock.h',
  'local_lock_irqsave',
  'public헤더는 DEFINE_GUARD로plain/irq/nestedBH획득과해제쌍을cleanup기술에연결합니다. irqsave는DEFINE_LOCK_GUARD_1에 flags '
  '필드를추가하고획득시저장한 flags를해제의irqrestore에전달합니다. scope 종료에해제를연결하는선언이며이local_lockfixture는guard생성 '
  'macro를빈모델로취급하여생성코드를실행하지는않았습니다.',
  '이미작성한cleanup기술수업과연결하여guard객체 수명과해제순서를확인합니다. 하나의획득을manualunlock과automaticcleanup으로두 번해제하지않습니다. '
  'irqsaveguard가보관하는 flags를다른 scope와혼용하지않습니다.',
  [('irqsaveguard에추가로보관하는상태는?',
    'unsignedlongflags다',
    '항상bitmap원소수다',
    'DEFINE_LOCK_GUARD_1의추가필드는 flags 입니다. 대응restore에같은획득의상태를전달합니다.'),
   ('이번local_lockfixture가guard생성코드까지실행했는가?',
    '아니며생성 macro는 명시적빈모델이다',
    '모든cleanupdestructor를실행했다',
    '원문연결을읽고설명했지만실행검사범위는다릅니다. 해설과선택된 fixture 증거를구분합니다.')],
  [('전제와 연결',
    'public의네guard선언과일곱기본 wrapper,두nestedwrapper전체를읽었습니다. cleanup의일반생성원리는기존전체cleanup수업으로연결합니다.'),
   ('검사 범위',
    '원본 public/internal 두 헤더를 직렬 CPU·IRQ·preempt·migration·spin·lockdep 모델에서 검사했습니다. 실제 IRQ,RT '
    'scheduler,lockdep 탐지나 cleanup guard 생성 실행 증거는 아닙니다.')],
  1)]

def register(topic,q,detail):
 for title,path,symbol,principle,use,qa,cards,occ in ROWS:
  topic(title,"동기화",path,symbol,"CPU별자료를보호하는문맥제어와RT잠금의다른구현을실제소스에서읽어사용조건과동작원리를배웁니다.",principle,use,"publicwrapper에서선택된CONFIG구현까지연결하고획득전상태와해제후복구를비교하세요.",*(q(*x) for x in qa),details=[detail(*x) for x in cards],source_occurrence=occ)
