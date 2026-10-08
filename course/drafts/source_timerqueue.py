"""Whole timerqueue declarations and cached red-black timer ordering library."""
def register(topic,q,detail):
 types='include/linux/timerqueue_types.h';h='include/linux/timerqueue.h';c='lib/timerqueue.c'
 def lesson(title,path,symbol,why,principle,use,reading,qa,cards):
  topic(title,'시간',path,symbol,why,principle,use,reading,*(q(*x) for x in qa),details=[detail(*x) for x in cards])
 lesson('타이머 노드·만료값과 연결용 트리 멤버',types,'timerqueue_node',
  '타이머 자체와 만료 순서에 넣는 연결 정보를 한 객체에 담는 방식을 배웁니다.',
  'timerqueue_node는 struct rb_node node와 ktime_t expires를 담습니다. expires는 정렬할 나노초 숫자이고 node는 트리 연결·색·부모 정보입니다. 별도 데이터 포인터 배열보다 객체에 연결 멤버를 넣는 방식입니다. 이 선언에는 callback 함수나 실행 코드가 없습니다.',
  '노드를 초기화하고 같은 clock 의미의 expires를 설정해 큐에 넣습니다. 저장된 객체의 주소·수명을 유지하고 사용 중인 연결 멤버를 다른 트리에도 동시에 넣지 않습니다.',
  '두 멤버의 역할과 hrtimer의 timer->node 사용을 연결하세요.',
  [('expires와node의역할은?','만료 정렬값과트리 연결 정보다','둘 다별도CPU시간대 이름이다','데이터값과자료구조연결을분리합니다.연결은객체안에포함됩니다.'),('구조체선언만으로callback이실행되는가?','아니며만료값과연결형식만정의한다','expires를쓰면즉시callback이호출된다','데이터배치와타이머실행시스템은다른계층입니다.')],
  [('단위','ktime_t숫자의clock도메인은자료형내부에들어있지않습니다.'),('주소 안정성','큐에있는노드를복사·이동·해제하면포인터연결이깨질수있습니다. caller가수명을관리합니다.')])
 lesson('타이머 큐 head·가장왼쪽 노드를따로 캐시',types,'timerqueue_head',
  '가장빠른만료를매번트리탐색하지않고바로조회하는방법을배웁니다.',
  'timerqueue_head는rb_root_cached를담습니다. 트리는expires순서를균형있게관리하고캐시rb_leftmost는가장빠른노드를가리킵니다. cached삽입·삭제API가이캐시를갱신합니다. 첫노드조회는포인터읽기O(1),일반삽입·삭제는균형트리O(log n)입니다.',
  'head초기화뒤cached연산을사용합니다. 일반rb_erase만쓰고캐시를갱신하지않으면getnext가잘못된노드를가리킬수있어timerqueueAPI를통해변경합니다.',
  'rb_root_cached형식과timerqueue_getnext의rb_first_cached를연결하세요.',
  [('왼쪽최소노드를캐시하는이점은?','첫만료후보를O(1)포인터로얻는다','모든타이머삽입이무조건O(1)이된다','최소값조회와트리삽입·삭제의비용은다릅니다.캐시는조회한단계를줄입니다.'),('일반트리삭제만하고캐시를유지하지않으면?','getnext가오래된포인터를가리킬수있다','캐시가항상자동으로변수를추적한다','캐시는별도필드입니다.자료구조의연산이함께갱신해야합니다.')],
  [('읽기 일관성','잠금없는동시조회안전성을캐시필드하나로보장하지않습니다.'),('자료구조 연결','레드블랙트리의회전·삭제·cachedfirst수업과함께읽습니다.')])
 lesson('타이머 초기화·empty마커와실제queued상태',h,'timerqueue_init',
  '노드가 큐에 연결돼 있는지 표시하는 초기 마커와 초기화 순서를 이해합니다.',
  'timerqueue_init은RB_CLEAR_NODE로연결부모마커를자기노드주소에맞춥니다. timerqueue_node_queued는!RB_EMPTY_NODE를반환합니다. 초기화는expires를설정하지않고callback도등록하지않습니다. live큐안노드를초기화만해서정상삭제한것으로만들수는없습니다.',
  '새노드에init을한뒤expires를설정합니다. 이미queued인노드는timerqueue_del로제거하고필요하면다시넣으며queued상태에서init으로연결을숨기지않습니다.',
  'RB_CLEAR_NODE와queued의empty부정검사를읽으세요.',
  [('init직후queued반환은?','false다','true다','empty마커를설정했으므로queued검사는그부정인false입니다.'),('init이expires값까지0으로초기화하는가?','아니며연결마커만초기화한다','모든멤버를memset0한다','실제본문은RB_CLEAR_NODE하나입니다. 만료값은caller가설정해야합니다.')],
  [('삭제와초기화','연결된트리에서정상삭제하는연산과empty마커설정은같은작업이아닙니다.'),('상태관찰','queued는노드마커검사입니다.어떤head에속하는지검색해반환하는함수는아닙니다.')])
 lesson('빈타이머 큐 시작·head초기화와기존노드',h,'timerqueue_init_head',
  '새큐의root·최소값캐시를함께빈상태로만드는방법을배웁니다.',
  'timerqueue_init_head는RB_ROOT_CACHED를head->rb_root에대입해트리root와leftmost를빈포인터로만듭니다. 기존큐의노드를하나하나삭제하거나해제하지않습니다. 노드별empty마커도자동갱신하지않아기존head를무조건reset하는것은정상정리가아닙니다.',
  '새head에초기화하고큐에노드가있으면각노드를API로제거한뒤객체수명정책에따라정리합니다. head초기화를메모리해제로해석하지않습니다.',
  'RB_ROOT_CACHED대입과노드init의차이를읽으세요.',
  [('head초기화직후getnext는?','NULL이다','임의로가장큰expires를반환한다','root와cached최소포인터가비어있으므로노드가없습니다.'),('기존큐head를reset하면모든노드가해제되는가?','아니며노드삭제·수명정리가별도다','자동으로모든객체free가호출된다','본문에순회·free가없습니다.접근루트를덮는것과자원정리는다릅니다.')],
  [('두초기화','head와개별node는서로다른초기화대상입니다.'),('사용순서','headinit→nodeinit→expires설정→add→getnext→del의흐름을직접그립니다.')])
 lesson('만료비교 함수·container로객체를 되찾기',c,'__timerqueue_less',
  '범용트리의연결포인터에서타이머객체와정렬값을찾는방법을배웁니다.',
  '__node_2_tq는rb_entry로rb_node멤버에서timerqueue_node주소를복구합니다. __timerqueue_less는두객체expires의엄격한<만비교합니다. 포인터주소·callback·등록번호를키로추가하지않으며같은expires에서는less가false입니다.',
  'rb_node가실제timerqueue_node의node멤버라는계약을지킵니다. 큐안expires를제자리변경하면기존트리순서가깨질수있으므로삭제후변경·재삽입합니다.',
  '멤버주소복구와strictless를읽으세요.',
  [('expires가같으면less결과는?','false다','항상true다','엄격한<비교입니다.같은키를작다고하지않습니다.'),('queuedexpires를직접바꾸면?','트리정렬과최소캐시가틀릴수있다','캐시가자동으로전체트리를재정렬한다','트리위치는삽입시비교로정해졌습니다.키변경은삭제·재삽입을통해반영합니다.')],
  [('container 원리','객체내멤버의offset을빼바깥객체주소를구하는방식입니다.임의포인터에는적용하지않습니다.'),('정렬 의미','유효한같은clock도메인의signed나노초숫자를정렬합니다.서로다른clock시각의의미는caller가맞춥니다.')])
 lesson('타이머add의boolean·새최소후보인가',c,'timerqueue_add',
  '삽입 반환값이 성공 여부가 아니라 새 첫 만료 여부라는 API 계약을 배웁니다.',
  'add는노드empty여부를WARN_ON_ONCE로검사하고rb_add_cached에맡깁니다. rb_add_cached가새leftmost노드포인터면booltrue,NULL이면false입니다. 따라서false여도삽입됐을수있습니다. 빈큐나더이른expires를넣으면true,기존최소와같거나뒤이면false입니다.',
  '초기화되고연결안된노드를caller직렬화아래삽입합니다. false를할당실패로취급해동일노드를다시add하지않습니다. 새최소이면상위타이머시스템이재프로그램필요성을판단할수있습니다.',
  'WARN뒤실제삽입호출과pointer→bool반환을읽으세요.',
  [('현재첫만료10에expires20을add해false이면?','정상삽입됐지만새최소가아니다','삽입이실패했으므로같은노드를다시넣는다','반환계약은새첫만료여부입니다. 일반성공·실패boolean과구분합니다.'),('빈큐에첫노드를넣으면?','true다','첫노드는최소판정없이false다','새노드가leftmost가되어반환포인터가있습니다.')],
  [('상위사용','hrtimer.c의enqueue_hrtimer가timerqueue_add결과를사용합니다.큐는직접clockevent를설정하지않습니다.'),('할당','이라이브러리는노드메모리를할당하지않고caller가준비한객체를연결합니다.')])
 lesson('같은만료시각의타이머·동률과순회순서',c,'timerqueue_add',
  '같은키를여러개넣는자료구조에서최소값과개별노드정체성을구분합니다.',
  '같은expires면less가false라rb_add_cached는오른쪽경로로삽입합니다. 회전은inorder를보존하므로고정v6.12구현에서같은키노드의삽입순서가순회에남습니다. 기존첫노드와동률인새노드는leftmost가아니라addfalse입니다. 이관찰을독립된외부우선순위계약으로확대하지않습니다.',
  '동률을실험할때A·B·C객체를구분합니다. 동일키를같은객체중복등록과혼동하지않고만료실행정책은상위타이머시스템의규칙도확인합니다.',
  'strictless·equal오른쪽분기·회전의inorder보존을연결하세요.',
  [('expires7의A뒤B를넣으면B의add반환은?','false이며B도큐에들어간다','true이며A를자동덮어쓴다','같은키도별도노드로들어가며새leftmost가아닙니다.키중복과노드중복은다릅니다.'),('같은expires노드를삭제할때사용하는것은?','그노드의주소다','expires값만넘기면모든동률이삭제된다','del은node포인터를받습니다.동률객체의정체성을보존합니다.')],
  [('버전 관찰','동률순회는현재본문으로검산한관찰입니다.모든다른큐구현의추가안정성계약이라고하지않습니다.'),('실험','동률3개순차삽입·getnext·삭제로원문결과를확인합니다.')])
 lesson('타이머del의boolean·삭제후큐에남은노드',c,'timerqueue_del',
  'add와del이서로다른boolean의미를반환하는점을배웁니다.',
  'del은empty노드경고뒤rb_erase_cached로삭제하고RB_CLEAR_NODE로empty마커를복구합니다. 마지막!RB_EMPTY_ROOT는삭제후큐에노드가남았는지를반환합니다. 마지막노드삭제는정상처리되어도false입니다. 객체free나callback취소대기를수행하지않습니다.',
  '해당head에실제로연결된노드를caller직렬화아래삭제합니다. false를삭제실패로읽지않고노드수명·실행중callback과의관계는상위API규칙을따릅니다.',
  'cached삭제·clear·root부정검사의순서를읽으세요.',
  [('마지막1개노드를정상del하면반환은?','false다','정상삭제이므로무조건true다','반환은삭제후비어있지않은가입니다. 성공여부boolean이아닙니다.'),('del후node_queued값은?','false다','메모리를안free했으므로true다','연결상태와메모리생존상태는별개입니다. clear마커로큐에서제거됐음을표시합니다.')],
  [('재사용','삭제한노드는유효객체인동안expires를설정하고다시삽입할수있습니다.'),('캐시','최소노드를삭제하면cached삭제API가다음최소포인터도갱신합니다.')])
 lesson('가장이른만료조회·빈큐NULL과비소모조회',h,'timerqueue_getnext',
  '첫 후보를 얻는 조회와 큐에서 빼는 연산의 차이 및 빈 큐 처리를 배웁니다.',
  'getnext는rb_first_cached로leftmost포인터를읽고rb_entry_safe로타이머노드주소를얻습니다. 빈포인터면NULL입니다. 읽은노드를삭제하거나expired조건을판정하지않습니다. 현재시각보다뒤인미래노드도첫후보로반환합니다.',
  'caller직렬화와객체수명을확인하고now와expires의조건을상위계층에서검사합니다. 반환값을사용한뒤처리정책에따라del을호출합니다.',
  'cached읽기·safecontainer와본문에삭제가없는점을읽으세요.',
  [('getnext를두번부르면첫노드가자동소비되는가?','아니며조회만하므로같은노드일수있다','항상첫호출에서삭제된다','큐변경연산이없습니다.조회와제거를구분합니다.'),('미래expires의노드도반환하는가?','그노드가첫후보이면반환한다','현재시각을자동읽어만료된노드만반환한다','getnext에는now인수나clock읽기코드가없습니다. 만료판정은상위계층의역할입니다.')],
  [('NULL 안전','safeentry는빈큐에서바깥객체주소계산을하지않고NULL을돌립니다.'),('실험','초기빈큐·마지막삭제·더이른삽입에서최소캐시를정렬배열참조와비교합니다.')])
 lesson('다음타이머순회·rb_next와동시변경조건',c,'timerqueue_iterate_next',
  '정렬순서의다음노드를찾는순회와안전한수명관찰의조건을배웁니다.',
  'node가NULL이면NULL을반환합니다. rb_next로inorder후속연결을얻고없으면NULL,있으면container_of로timerqueue_node로복구합니다. expires순서로읽는기능이며함수안에잠금·참조획득·snapshot복사가없습니다.',
  '순회동안큐변경을직렬화하고노드의수명을보호합니다.현재노드를삭제·해제한뒤그포인터로다음을찾는패턴을안전한순회라고하지않습니다.변경이필요한순회는계약에맞춘별도전략을사용합니다.',
  'NULL두분기·rb_next·container복구를읽으세요.',
  [('마지막노드의다음반환은?','NULL이다','다시첫노드로순환한다','레드블랙inorder순회는끝에서NULL입니다.원형리스트처럼자동순환하지않습니다.'),('이함수가동시삭제되는노드의수명을획득하는가?','아니며caller가직렬화·수명을보호한다','호출만하면영구참조가추가된다','본문에잠금이나참조카운트증가가없습니다.포인터조회와수명보호를구분합니다.')],
  [('순서','다음은expires정렬상의다음이며등록시간의다음이라는일반의미가아닙니다.'),('독립검산','전체순회를expires·삽입순서로정렬한참조배열과비교합니다.')])
 lesson('타이머큐직렬화·경고가잘못된호출을막지는않음',c,'timerqueue_add',
  '라이브러리의 경고와 실제 잠금·입력 거절을 구분해 안전한 사용 조건을 배웁니다.',
  '파일주석은모든함수를직렬화해야하며이라이브러리는잠금을하지않는다고명시합니다. 이미queued인노드add나empty노드del에서WARN_ON_ONCE가있어도그뒤트리변경을계속합니다. 정상안전계약을깨는호출을복구하는오류API가아닙니다.',
  'head를사용하는상위시스템의잠금아래조회·추가·삭제·순회를조정합니다.경고실험을하려고live트리에중복삽입하거나잘못삭제하지않습니다.보유락의문맥·callback수명은상위타이머코드에서따로읽습니다.',
  '파일직렬화주석과WARN뒤바로연산이이어지는본문을읽으세요.',
  [('중복add경고후안전하게호출이취소되는가?','아니며본문은트리삽입을계속한다','자동으로에러false만반환해트리를보존한다','WARN는경고입니다. 입력거절분기return이없으므로계약을지켜야합니다.'),('timerqueue라이브러리안에자동mutex가있는가?','없으며caller가직렬화한다','모든함수가head내부mutex를자동획득한다','파일주석과head필드에자동잠금이없습니다.상위호출경로가경쟁을처리합니다.')],
  [('검증 범위','실제원문트리와함께10만정상변경의균형·최소·상태·반환을확인합니다.실제동시hrtimer/clockevent실행증명은아닙니다.'),('전체 파일','timerqueue형식·헤더·C전체를해설합니다.이자료구조를사용하는hrtimer전체상태기계는별도해설대상입니다.')])
