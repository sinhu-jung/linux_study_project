"""Full generic non-atomic/wrapper/typecheck/constant hweight and atomic docs."""
def register(topic,q,detail):
 def lesson(title,path,symbol,why,principle,use,reading,qa,cards):
  topic(title,'라이브러리·알고리즘',path,symbol,why,principle,use,reading,*(q(*x) for x in qa),details=[detail(*x) for x in cards])
 def bitmap(title,symbol,why,principle,use,reading,qa,cards):
  lesson(title,'include/asm-generic/bitops/generic-non-atomic.h',symbol,why,principle,use,reading,qa,cards)
 def types(title,symbol,why,principle,use,reading,qa,cards):
  lesson(title,'include/linux/typecheck.h',symbol,why,principle,use,reading,qa,cards)
 def hw(title,symbol,why,principle,use,reading,qa,cards):
  lesson(title,'include/asm-generic/bitops/const_hweight.h',symbol,why,principle,use,reading,qa,cards)
 bitmap('generic bitmap의set·word인덱스와bit mask','generic___set_bit',
  '여러 word에저장된비트맵의한 bit위치를찾아설정하는구체적인원리를배웁니다.',
  'generic___set_bit는BIT_WORD(nr)로word인덱스를구하고BIT_MASK(nr)로그word안의bit를선택합니다. p는addr에서word수만큼전진한주소이며*p|=mask로1을넣습니다. native64에서nr65는두 번째word의bit1입니다.이generic 갱신은non-atomic이고다른writer와의경쟁을보호하지않습니다.',
  '충분한크기의유효 bitmap에서nr가범위 안인지확인합니다.단일소유나외부잠금이보장된구간에서사용합니다.volatile인자가있다고원자적 RMW나ordering을보장한다고판단하지 않습니다.',
  'BIT_WORD·BIT_MASK·word포인터증가·OR대입을읽으세요.',
  [('64bit word의bitmap에서nr65는어디인가?','두 번째word의bit1이다','첫word의bit65를직접shift한다','word몫은1,word안나머지는1입니다.유효한word폭안의shift와배열 원소이동을나눕니다.'),('generic___set_bit가동시 writer를원자적으로보호하는가?','아니며non-atomic갱신이다','volatile인자이면자동으로atomic이다','본문은일반 읽기와OR저장입니다.volatile형식의인자가동시RMW계약을바꾸지않습니다.')],
  [('검사','네word bitmap의10만변경을별도256byte상태배열과비교했습니다.'),('직접 호출','원문은 generic이름을일반 코드에서직접쓰지말고선택된public wrapper로사용하라고안내합니다.')])
 bitmap('generic bitmap의clear와toggle·AND NOT와XOR','generic___clear_bit',
  'bit를0으로만드는동작과현재 값을반대로바꾸는동작의차이를배웁니다.',
  'generic___clear_bit는*p&=~mask로해당위치를0으로만듭니다. generic___change_bit는*p^=mask로0을1,1을0으로바꿉니다. clear를두 번해도0이유지되지만toggle을두 번하면원래 값입니다.두함수모두다른 bit를산술상보존하는일반non-atomic갱신입니다.',
  '무조건해제하려면clear,상태반전이목적이면change를사용합니다.불확실한이전 상태를무조건0으로만들때toggle을쓰지않습니다.동시변경은외부동기화계약을지킵니다.',
  '같은주소·mask계산에서AND~와XOR의차이를읽으세요.',
  [('현재bit가1일때change를두 번하면?','다시1이다','반드시0에머문다','XOR는매번상태를반전합니다.두 번하면원래 값으로돌아옵니다.'),('현재 값을몰라도bit를무조건0으로만들려면?','clear를사용한다','change를한 번쓰면항상0이다','clear는기존상태와무관하게해당 bit를지웁니다.toggle은기존상태에따라다른결과가됩니다.')],
  [('다른 bit','mask밖bit를보존하는수학적성질과경쟁 writer의갱신보존은다릅니다.'),('구현','writer용generic함수는volatile포인터를일반포인터로cast해사용합니다.이경로를atomicvolatile RMW로설명하지않습니다.')])
 bitmap('test-and-set과test-and-clear·이전bit를반환','generic___test_and_set_bit',
  '메모리를바꾸면서원래상태를돌려주는API의시간기준을배웁니다.',
  'generic___test_and_set_bit는word를old에읽고old|mask를저장한뒤old&mask의bool을반환합니다. test_and_clear도old&~mask저장후같은이전bit를돌려줍니다.첫set의old0이면반환false,다음set의old1이면true입니다.이__계열은non-atomic이며bool반환이lock획득을자동제공하지않습니다.',
  '단일소유또는외부잠금구간에서이전 상태가필요할때사용합니다.두writer의test-and-set을실제원자적잠금으로쓰려면정해진atomic/lock API계약을 확인합니다.',
  'old읽기·갱신저장·이전bit bool반환을읽으세요.',
  [('기존bit0에generic___test_and_set_bit를호출한반환값은?','false다','새값이1이므로true다','반환은이전old의bit입니다.새값과반환의시간기준을구분합니다.'),('이non-atomic test-and-set으로두writer의lock획득이보장되는가?','아니며둘다old0을읽을수있다','bool이반환되면언제나원자적lock이다','일반 읽기·저장사이에경쟁이가능합니다.public atomic/lock계약이나외부동기화가필요합니다.')],
  [('검사','이전bit반환과새 상태를독립 상태 배열로각각비교했습니다.'),('ordering','공식문서의atomic test_and_* ordering을__접두non-atomic함수에그대로붙이지않습니다.')])
 bitmap('test-and-change·반전결과보다이전 상태의의미','generic___test_and_change_bit',
  'toggle과이전 상태반환을결합한연산을정확히해석하는방법을배웁니다.',
  'generic___test_and_change_bit는old^mask를저장하고old&mask가0이아닌지반환합니다. old1이면새bit0이어도반환true입니다. old0이면새bit1이어도false입니다.0/1반환은전체 word값이아니라해당 bit의이전bool입니다.동작은non-atomic이고여러 writer를직렬화하지않습니다.',
  '상태반전과이전bool이함께필요한단일소유구간에서사용합니다.반환을반전후상태로해석하지않습니다.다른 bit수명이나객체의사용권한까지bool로보장하지않습니다.',
  'old^mask저장과old&mask반환을읽으세요.',
  [('oldbit1의test-and-change후새값과반환은?','새값0,반환true다','새값0,반환false다','메모리는반전되지만반환은이전 상태입니다.두결과를서로 다른시간으로해석합니다.'),('반환값이전체이전word인가?','아니며선택 bit의bool이다','word의모든bit를반환한다','본문은(old&mask)!=0입니다.다른 bit와전체 word의숫자는반환하지않습니다.')],
  [('원본 계약','헤더는이함수도non-atomic이고reorder될수있다고명시합니다.'),('검사','반환 oldbool과toggle후bitmap전체를별도 검사했습니다.')])
 bitmap('generic test_bit·volatile읽기와RMW의차이','generic_test_bit',
  'bit조회가수정연산과다른 계약을갖고volatile을유지하는이유를배웁니다.',
  'generic_test_bit는const volatile unsigned long주소의word를읽고해당 bit를낮은위치로shift해1UL과AND합니다.본문은메모리를수정하지않습니다.원문은이kernel조회가atomic이라volatile을버리지않는다고설명합니다.이것을임의 C 프로그램의volatile이모든원자성·ordering·수명 보호를제공한다는주장으로확대하면안됩니다.',
  '유효하고정렬된kernel bitmap의bit를조회합니다.읽기와다른 데이터공개순서가필요하면별도의acquire프로토콜을검토합니다.조회결과만으로객체가해제되지않는다고가정하지 않습니다.',
  'const volatile유지·word선택·shift·1UL AND를읽으세요.',
  [('generic_test_bit가원본bitmap을바꾸는가?','아니며읽어서bit값을반환한다','항상조회bit를0으로지운다','본문에는저장이없습니다.조회와test-and-clear의수정계약을구분합니다.'),('일반test_bit조회가다른payload의공개순서까지자동보장하는가?','아니며필요한ordering프로토콜을확인한다','atomic읽기라면모든앞뒤데이터도자동동기화된다','단일word조회와다른 메모리의ordering은별개입니다.acquire계열과그에대응하는공개동작을확인합니다.')],
  [('공식 문서','Documentation/atomic_bitops.txt는일반non-RMW조회의ordering과acquire예외를구분합니다.'),('검사','fixture의일반 조회는유효한serial bitmap에서검사했습니다.전체kernel memory model의증명으로기록하지않습니다.')])
 bitmap('test_bit_acquire·word를acquire로읽은뒤bit추출','generic_test_bit_acquire',
  'bit조회에acquire의미를붙이는기술과대응공개조건을배웁니다.',
  'generic_test_bit_acquire는word주소를구해smp_load_acquire로읽은뒤선택 bit를추출합니다.맞는release공개와동기화관계가성립하면이후payload읽기가앞서지않도록하는계약입니다.이동작자체가bit를설정하거나lock의상태 전이를수행하지는않습니다.원자적잠금획득API와단순acquire조회는역할이 다릅니다.',
  '동일한동기화변수의release공개와맞는프로토콜에서사용합니다.조회대상bit와실제공개상태를확인합니다. payload수명과재사용문제는상위규약으로보호합니다.',
  'smp_load_acquire(p)와조회값의shift·mask를읽으세요.',
  [('test_bit_acquire가bit0에서1로바꾸어lock을자동획득하는가?','아니며acquire읽기만수행한다','항상test-and-set도함께실행한다','원문에는load와bit추출만있습니다.조회와상태변경을구분합니다.'),('payload공개에대응하는동기화관계를무시해도acquire면충분한가?','아니며맞는공개프로토콜이필요하다','다른변수를읽어도모든payload가자동동기화된다','acquire는정해진공개관계에서의ordering입니다.같은동기화상태와수명규칙을함께확인합니다.')],
  [('fixture 모델','smp_load_acquire는GCC C11 acquire load로모델링했습니다.이모델검사가모든kernel architecture의barrier를실행한것은아닙니다.'),('전체 읽기','const alias의test_bit_acquire도이generic함수로연결됩니다.값계약과선택이름을함께읽습니다.')])
 bitmap('const_test_bit·상수최적화를위한volatile제거','const_test_bit',
  '비슷한조회helper가다른최적화전제를가지는이유를배웁니다.',
  'const_test_bit는입력const volatile주소를const unsigned long*로cast해volatile을버리고word를읽어maskbool을반환합니다.원문은non-atomic이며compile-time constants를조회하는선택경로에만쓰고일반 코드에서직접 호출하지말라고명시합니다.일반generic_test_bit와같은동시성 계약이라고보면안됩니다.',
  'public bitop선택에서compiler 상수 조건을만족한경로로읽습니다.값이runtime에경쟁 변경되는객체에직접이helper를적용하지않습니다. volatile제거를성능향상만으로보지말고전제를 확인합니다.',
  'const포인터cast·word읽기·maskbool·원문의 직접 호출제약을읽으세요.',
  [('const_test_bit가volatile을계속보존하는가?','아니며최적화용const포인터로cast한다','generic조회와항상 같은volatile접근이다','원문은volatile을버리는것을명시합니다.선택된상수문맥의전제를 확인해야합니다.'),('경쟁 변경되는bitmap에일반 조회대신직접써도되는가?','아니며상수선택용전제를지킨다','함수 이름만비슷하면모든조회와같다','이helper는non-atomic이며일반 코드의직접 호출을금지하는설명이있습니다.계약을바꾸어대체하지않습니다.')],
  [('다른const aliases','const___set/clear/change와test-and세종,const_test_bit_acquire는정해진generic함수로연결됩니다.이름의const를객체불변성선언으로해석하지않습니다.'),('비교','generic_test_bit의volatile유지와나란히읽어최적화경계의차이를확인합니다.')])
 bitmap('generic arch wrapper·이름연결과include guard','generic___set_bit',
  '짧은forwarding헤더가public선택에필요한이름계층을연결하는역할을배웁니다.',
  'non-atomic.h는arch___set/clear/change,arch___test_and세종,arch_test_bit/acquire를generic함수로연결합니다. non-instrumented-non-atomic.h는___set/clear/change와_test이름을arch계층으로연결합니다.이objectmacro들은새algorithm을실행하지않고이름을연결합니다.두전체 파일의guard와include 순서도같이읽어야 합니다.',
  'public__set_bit→bitop→___set_bit→arch___set_bit→generic의경로를그립니다.실제architecture가generic wrapper대신다른정의를사용하는지확인합니다.이fixture의non-instrumented경로를모든instrumentation실행으로기록하지않습니다.',
  '두짧은헤더전체의8개alias씩과guard·include를읽으세요.',
  [('non-instrumented wrapper가새bit별loop를실행하는가?','아니며이름을arch계층으로연결한다','alias마다별도bitmap전체검색을한다','파일은objectmacro alias입니다.연결된실제함수에서algorithm을읽습니다.'),('generic wrapper실행검사가모든arch asm도검사한것인가?','아니며선택된generic경로증거다','이름이연결되면모든CPU코드도실행된다','전처리에서선택한구현만실행합니다.다른target과instrumentation경로는별도 증거가필요합니다.')],
  [('포함 경로','generic-non-atomic.h는bitops.h에서직접포함되고단독포함에#error를냅니다.전체연결과전제를읽었습니다.'),('검사','원본두alias헤더를fixture에포함해prototype 검사와bitmap갱신을수행했습니다.')])
 bitmap('공식atomic bitops계약·갱신 반환 ordering 예외','generic_test_bit_acquire',
  '값의원자성과다른 메모리ordering을공식문서의API군별로구분해배웁니다.',
  'atomic_bitops.txt는일반test_bit와no-return atomic RMW의ordering을unordered로,반환값이있는atomic test_and_*와조건부RMW를fully ordered로설명합니다.예외로성공한test_and_set_bit_lock은acquire,clear_bit_unlock은release,test_bit_acquire는acquire입니다. __접두RMW는non-atomic입니다. __clear_bit_unlock의generic매핑주의도별도로기록합니다.',
  '실제선택한publicAPI가어느군인지확인하고객체의공개·해제순서에맞춰사용합니다.값반환이있는non-atomic함수에atomic군의ordering을붙이지않습니다.규칙의lock예외를따로읽습니다.',
  'Documentation/atomic_bitops.txt 전체의API·SEMANTICS·ORDERING과RST wrapper를읽으세요.',
  [('반환값있는atomic test_and_*규칙을__접두non-atomic함수에그대로적용하는가?','아니며atomic군과non-atomic군을구분한다','bool반환이면모든함수가fully ordered다','공식문서는__접두RMW의non-atomic차이를명시합니다.반환형만보고ordering을추측하지 않습니다.'),('공식예외중clear_bit_unlock의ordering은?','release다','항상순수unordered조회다','unlock은앞선보호데이터의공개에관한release계약입니다.단순bit조회규칙과다릅니다.')],
  [('문서 전체','일반bitmap함수의non-atomic성,API목록,oldbit반환,배리어연결,unlock매핑주의와ordering예외를모두읽었습니다.'),('RST wrapper','core-api/wrappers/atomic_bitops.rst는원문txt를literal include하고LaTeX글자크기를조정합니다.새atomic구현이나추가ordering을정의하지않습니다.')])
 types('typecheck·dummy포인터비교로타입 진단','typecheck',
  'runtime검사없이특정scalar 타입사용을compiler에확인시키는기술을배웁니다.',
  'typecheck(type,x)는type의dummy와typeof(x)의dummy를만들고그주소를비교합니다.다른타입이면compiler가서로 다른포인터비교를진단할수있습니다.식은항상1을반환합니다.일반 scalar의typeof(x)는값을평가하지않아typecheck(int,counter++)에서counter는증가하지않습니다.실제숫자범위 검사와는다릅니다.',
  '정해진타입이필요한macro경계에서사용하고warning을 error로다루는빌드문맥을확인합니다.반환1을입력값이유효하다는runtime검증으로해석하지않습니다.임의VLA확장문맥까지unevaluated라고일반화하지않습니다.',
  '두dummy·주소비교·voidcast·항상1반환을읽으세요.',
  [('일반int의typecheck(int,counter++)가counter를증가시키는가?','아니며typeof의타입문맥이다','항상한 번증가한다','원문은값을계산하지않고타입을얻습니다.fixture에서scalar의부작용없음을확인했습니다.'),('typecheck가숫자가허용범위인지검사하는가?','아니며타입 진단목적이다','반환1이면모든숫자범위가유효하다','값의범위와타입계약은다른검사입니다.항상1을반환하는식으로runtimevalidator를만들지않습니다.')],
  [('검사','unsigned long을int요구에전달한사례가-Werror에서compile 거절됐습니다.'),('한계','진단강도는compiler와빌드옵션문맥에따릅니다.모든타입·표준언어문맥의동일진단증거는아닙니다.')])
 types('typecheck_fn·함수 표현대입은실제로평가한다','typecheck_fn',
  '같은 타입 검사 이름이라도 입력 표현의 평가 계약이 달라질 수 있음을 배웁니다.',
  'typecheck_fn(type,function)은typeof(type)의임시변수를function식으로초기화하고void로사용합니다.적절한함수포인터typedef에대입하며반환형·인자signature의호환을검사합니다.여기서는function표현이실제로평가됩니다.함수포인터를돌려주는getter를넣으면getter는한 번실행됩니다.일반 scalar typecheck의typeof문맥과다릅니다.',
  '원하는함수포인터타입의typedef를정의하고callback이호환되는지확인합니다.평가부작용이필요없는경계에는단순함수 이름이나포인터를전달합니다.표현을검사에넣기전에실행될지확인합니다.',
  'typeof(type) 임시변수선언과function초기화를읽으세요.',
  [('function인자에포인터 getter를전달하면?','getter표현이한 번평가된다','이름이typecheck라항상평가되지않는다','원문은임시변수의초기화에표현을사용합니다.fixture는getter의1회실행을확인했습니다.'),('void(void)함수를int(int)포인터typedef에대입해도정상계약인가?','아니며signature불일치다','함수주소이면모든signature가같다','함수포인터의반환과인자타입이맞아야합니다.독립compile 거절사례로확인합니다.')],
  [('검사','실제pointer getter의카운터1회증가와잘못된signature의compile 진단을검사했습니다.'),('구분','typecheck_fn은callback의runtime동작이나객체수명까지검증하지않습니다.함수타입경계를확인하는기술입니다.')])
 types('typecheck_pointer·sizeof역참조로포인터형식확인','typecheck_pointer',
  '주소 유효성과포인터형식검사가별개임을구체적인macro로배웁니다.',
  'typecheck_pointer는typeof(x)의dummy를선언하고sizeof(*dummy)를사용한뒤1을반환합니다.일반포인터의대상타입을compiler문맥에서검사하며실제 메모리를역참조하지않습니다.포인터가NULL이거나해제됐는지,배열용량이충분한지확인하지않습니다.void pointer등sizeof확장은kernel의GNU C문맥을함께봐야합니다.',
  '포인터태그macro의주소인자타입을확인할때연결해읽습니다.형식검사와수명·정렬·접근권한검사를분리합니다.정수변수를포인터 변수처럼cast해전달하지않습니다.',
  'typeof dummy·sizeof(*dummy)·1반환을읽으세요.',
  [('typecheck_pointer가실제객체메모리를읽는가?','아니며sizeof의타입 검사문맥이다','대상첫byte를항상조회한다','원문은compiler의크기식입니다.유효한객체내용을읽는검사와다릅니다.'),('정수변수주소를__ptr_set_bit에전달하면정상포인터계약인가?','아니며포인터형식검사대상이다','주소형식만있으면모든정수변수도동일하다','태그macro는포인터 변수의형식을요구합니다.fixture의정수변수사례는compile 거절됐습니다.')],
  [('한계','항상1반환은runtime주소 유효성을뜻하지않습니다.상위접근계약을별도로지킵니다.'),('전체 파일','typecheck.h의세macro와include guard를모두읽고평가·진단계약을작성했습니다.')])
 hw('상수popcount·8개bit검사합과16 32 64합성','__const_hweight8',
  '계산 시간에일비트를세는식과넓은입력을작은구간으로나누는원리를배웁니다.',
  '__const_hweight8은각1ULL<<0..7을입력과AND하고!!로0/1로만든뒤더합니다.16은8bit둘의합,32는16bit둘,64는32bit둘의합입니다.처음8bithelper는낮은8bit만세므로상위 bit가있는넓은입력을넣어도그 범위는세지않습니다.16·32·64의입력shift가충분한폭에서수행되는지확인해야합니다.',
  '상수 값의설정bit수를직접각위치별로세어검산합니다.고정 폭에맞는입력을사용하고좁은값의큰shift를피합니다.하드웨어popcount명령실행과상수 표현을compiler가접는것을구분합니다.',
  '8개!!항·8/16/32shift를사용한합성을읽으세요.',
  [('__const_hweight8(0x100ULL)의결과는?','0이다','9다','켜진 bit는bit8이며helper가세는낮은8bit밖입니다.폭별계약을 확인합니다.'),('16bit상수helper의합성방법은?','낮은8과높은8의설정bit수를더한다','모든bit의위치를반전한다','popcount는개수를셉니다.bit위치를바꾸는reversal과다른알고리즘입니다.')],
  [('검사','65536개낮은16bit입력의네폭helper를독립 per-bit카운트와대조했습니다.'),('전체 입력','10만wide입력의64helper도대조했습니다.원문의합성식을참조알고리즘에복사하지않았습니다.')])
 hw('public hweight선택·상수식과arch runtime 경로','hweight64',
  'compiler가고르는상수 계산과실제runtime구현의입력평가 계약을배웁니다.',
  'hweight8/16/32/64는__builtin_constant_p(w)로private상수식을고르거나__arch_hweight계열을호출합니다.부작용있는일반runtime식은상수로판단되지않고runtime함수의인자로평가됩니다. private __const식은같은입력을여러번사용하므로직접x++같은식을넣으면비순차변경문제가될 수 있습니다.',
  '일반 값 계산은public함수를사용하고private상수식에는부작용없는맞는폭값만전달합니다.실제arch선택과software경로를확인합니다.모든macro가자동으로입력지역 변수를갖는다고가정하지 않습니다.',
  'constant_p삼항과private입력반복·arch호출을읽으세요.',
  [('private __const_hweight8에x++를직접넣는것은안전한가?','아니며입력반복의평가 계약을 확인해야한다','모든macro는입력을자동으로한 번만받는다','같은w가여러항에반복됩니다.private부작용사례는sequence-point진단으로거절하고실행하지않았습니다.'),('검사한public hweight64(count++)의증가횟수는?','한 번이다','켜진 bit수만큼증가한다','runtime경로의함수인자로한 번평가됩니다.fixture는이전count3의popcount2와이후count4를확인했습니다.')],
  [('scope','arch_hweight는fixture에서원본software __sw함수로연결됩니다.모든CPU명령실행의증거는아닙니다.'),('비교','bitrev의private상수helper는지역 변수를사용하지만이privatehweight식은입력반복입니다.실제macro정의를각각읽습니다.')])
 hw('HWEIGHT 상수 전용계열·BUILD_BUG_ON_ZERO로제약','HWEIGHT64',
  '상수용 API가일반 값API와다른입력조건을compiler로강제하는방법을배웁니다.',
  'HWEIGHT8/16/32/64는BUILD_BUG_ON_ZERO(!__builtin_constant_p(w))의0값과private카운트를더합니다. compiler 상수가아닌입력은negative bitfield검사에서진단됩니다.전역정해진초깃값에는쓸수있지만runtime증가식용helper가아닙니다.각폭의상위 bit는그폭helper의카운트에포함되지않을수있습니다.',
  '알려진상수의설정bit수를초기화식에서사용할때선택합니다.일반runtime숫자는public소문자hweight계열을사용합니다.진단을우회하려고부작용입력을숨기지않습니다.',
  '네HWEIGHT정의의상수검사와0+private카운트를읽으세요.',
  [('HWEIGHT64(x++)는runtime값의정상 사용인가?','아니며compiler 상수 조건을요구한다','어떤값이든자동으로runtime함수를부른다','대문자계열은상수 전용제약을검사합니다.소문자public선택계열과구분합니다.'),('정상BUILD_BUG_ON_ZERO항이데이터값에더하는것은?','0이다','임의의설정bit수를추가한다','검사를식안에포함하되정상결과에는0을더합니다.실제개수는private카운트가계산합니다.')],
  [('검사','모든64bit가1인알려진상수를전역초기화해64를확인했습니다.runtime입력은compile 거절을확인합니다.'),('범위','상수 전용조건이입력의모든shift폭을자동으로넓히지는않습니다.다음type-invarianthelper와연결합니다.')])
 hw('HWEIGHT의u64 cast·좁은입력의32칸shift를피하기','HWEIGHT',
  '타입 불변편의API가실제중간 연산폭을확보하는이유를배웁니다.',
  'HWEIGHT(w)는HWEIGHT64((u64)w)입니다.64bitprivate합성은w>>32를포함하므로HWEIGHT64(1U)처럼32bit입력을직접사용하면폭밖shift가진단될 수 있습니다. HWEIGHT(1U)는먼저u64로cast해이동폭을확보하고1을돌려줍니다.최종결과타입만넓다고피연산자가자동으로넓어지는것은아닙니다.',
  '알려진여러unsigned폭상수의전체값을세려면type-invariant HWEIGHT의cast를읽습니다.고정64API에는64폭입력을명확히전달합니다.64보다넓은입력의상위 bit까지이helper가세는것으로확대하지 않습니다.',
  'HWEIGHT의u64cast와private64의>>32합성을읽으세요.',
  [('HWEIGHT(1U)가64합성에서폭을확보하는방법은?','계산전에u64로cast한다','반환형이모든입력연산을자동으로바꾼다','원문은명시입력cast를사용합니다.연산시피연산자 폭과최종반환타입을구분합니다.'),('HWEIGHT64(1U)의폭문제를확인하는정상검사방법은?','compile 진단을확인하고invalidshift는실행하지않는다','undefinedshift를실행해결과가우연히1이면안전하다고한다','fixture는shift-count진단으로거절됨을확인합니다.정의되지않는입력의실행결과로안전성을판단하지 않습니다.')],
  [('검사','HWEIGHT(1U)의결과1과narrow HWEIGHT64의compile 거절을함께확인했습니다.'),('전체 header','private8/16/32/64·public네이름·constant네이름·type-invariant별칭과guard를전부읽고작성했습니다.총724,294개기록 검사를통과했습니다.')])
 lesson('UAPI kernel forwarding·정의의포함경로를찾기','include/linux/bitops.h','BITS_TO_LONGS',
  '짧은UAPI헤더를원문정의와연결해helper의출처를추적하는방법을배웁니다.',
  'include/uapi/linux/kernel.h는guard안에서linux/sysinfo.h와linux/const.h를포함합니다.이파일자체가bitmapalgorithm을구현하지는않습니다. bitops의올림식__KERNEL_DIV_ROUND_UP은const.h로연결됩니다. sysinfo포함은별도UAPI정의경로이며그구조체의의미를bitmaphelper로추측하지 않습니다.',
  'macro가현재파일에없으면include를따라정의한파일까지이동합니다.전달 헤더전체를읽고가드와두include를기록합니다.포함된모든하위파일의내용을전달 헤더한개를읽었다는이유로완료처리하지않습니다.',
  'UAPI kernel.h의전체9줄과const.h의올림정의를연결하세요.',
  [('UAPI kernel.h 자체가새bitmap loop를정의하는가?','아니며정의헤더들을포함한다','모든bitops함수가그안에구현돼있다','전체 파일은guard와두include입니다.실제algorithm정의파일을따라가야합니다.'),('전달 헤더를읽으면포함된sysinfo의모든의미도자동완료인가?','아니며그하위정의는별도로읽고작성한다','include한줄이면모든하위기술설명도완료다','파일연결을이해한것과포함된구조체·기술의해설완성은다릅니다.작성증거를각파일별로기록합니다.')],
  [('전체 파일','guard와sysinfo/const두include를모두읽고포함경로를설명했습니다.'),('수업 연결','const올림정의는이미작성한크기산술수업과연결합니다.sysinfo의전체해설은해당원본을별도로검토해야합니다.')])
