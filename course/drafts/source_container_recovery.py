"""Whole container_of header; GNU C layout/type/const/lifetime contracts."""
def register(topic,q,detail):
 def lesson(title,symbol,why,principle,use,reading,qa,cards):
  topic(title,'라이브러리·알고리즘','include/linux/container_of.h',symbol,why,principle,use,reading,*(q(*x) for x in qa),details=[detail(*x) for x in cards])
 lesson('부모 구조체 복원·멤버 주소에서 offset 빼기','container_of',
  '리스트 노드나 callback에 전달된 멤버 주소만으로 그 멤버를 담은 실제 객체를 찾는 원리를 배웁니다.',
  'container_of(ptr,type,member)는 실제 멤버 주소에서 offsetof(type,member) 바이트를 빼 부모 type*를 얻습니다. 객체가 새로 만들어지는 것이 아니라 같은 객체의 시작 주소를 복원합니다. offsetof는 compiler가 결정한 패딩·정렬을 포함한 위치입니다. 앞 필드의 sizeof를 손으로 합치면 패딩 때문에 틀릴 수 있습니다.',
  'struct item 안의 hlist_node node를 리스트가 반환하면 container_of(nodeptr,struct item,node)로 item을 찾습니다. 해당 ptr가 실제 살아 있는 item.node의 주소이고 type/member가 맞다는 전제를 지킵니다.',
  '__mptr 저장과 offsetof subtraction을 실제 메모리 배치 그림으로 읽으세요.',
  [('container_of가 새 부모 객체를 할당하는가?','아니며 기존 객체 시작 주소를 복원한다','매번 구조체를 복사해 새 주소를 만든다','연산은 offset subtraction입니다. 부모 객체의 소유권이나 새 메모리 할당을 생성하지 않습니다.'),('멤버 위치를 앞 필드 sizeof 합으로만 구하면 안전한가?','아니며 정렬 패딩을 포함한 offsetof를 사용한다','C 구조체는 모든 필드가 항상 빈틈없이 붙는다','compiler가 타입 정렬을 위해 패딩을 넣을 수 있습니다. 실제 레이아웃을 반영한 offset이 필요합니다.')],
  [('주소 예','부모 시작1000,멤버 offset16이면 실제 멤버 주소1016에서16을 빼1000을 얻습니다. 숫자는 원리 예시이며 임의 주소를 역참조하는 실행 예가 아닙니다.'),('내장 구조','자료구조가 객체마다 외부 wrapper를 만들지 않고 내장 노드로 여러 객체 타입을 연결할 수 있는 기반입니다.')])
 lesson('내장 노드·리스트가 몰라도 복원할 객체 타입','container_of',
  '범용 링크 구조와 실제 업무 데이터 구조를 분리하면서 필요한 타입을 호출자가 제공하는 설계를 배웁니다.',
  'hlist_node나 rb_node는 연결 정보만 알면 됩니다. 실제 객체는 key·payload와 내장 node를 함께 담습니다. container_of에 부모 타입과 member 이름을 전달하면 정해진 레이아웃으로 복원합니다. 객체에 여러 노드가 있으면 어느 멤버에서 온 주소인지 정확히 지정해야 합니다. 잘못된 동일 타입 멤버를 선택해도 타입 검사만으로 모두 잡을 수는 없습니다.',
  'struct item { struct hlist_node first; struct hlist_node second; ... };에서 first 주소에는 member first를 사용합니다. 한 객체를 다른 자료구조에 동시에 연결할 때 노드 필드와 소유권을 구분합니다. 매크로가 실제 어느 노드였는지 런타임 검색하지 않습니다.',
  'ptr·type·member 세 인자가 각각 어떤 정보인지 확인하세요.',
  [('같은 타입 노드 두 개 중 잘못된 member를 지정해도 항상 컴파일 오류인가?','아니며 타입이 같으면 잘못된 offset을 쓸 수 있다','매크로가 실제 필드를 자동으로 찾아 고친다','타입 검사는 형식 호환을 확인합니다. 실제 주소가 지정 멤버에 속하는지까지 런타임 검증하지 않습니다.'),('범용 리스트가 모든 부모 객체 필드를 알아야 하는가?','아니며 링크를 관리하고 호출자가 타입·멤버로 복원한다','객체 모든 필드를 리스트 노드에 복사해야 한다','내장 노드와 부모 복원이 역할을 나눕니다. 연결 구조는 node만 관리할 수 있습니다.')],
  [('적용','리스트·RB 트리·작업 callback 같은 내장 멤버 패턴에서 부모 객체를 찾습니다. 각 자료구조의 연결 및 수명 규칙은 별도로 지킵니다.'),('검증','10만 실제 객체의 정수 멤버·중첩 노드·배열 멤버 주소에서 원래 객체 주소가 복원되는지 확인했습니다.')])
 lesson('컴파일 타입 검사·void 포인터 예외의 의미','container_of',
  '정적 타입 오류를 막는 assertion과 명시적으로 타입 정보를 지운 포인터의 책임을 배웁니다.',
  'static_assert는 *(ptr) 타입이 ((type*)0)->member 타입과 같거나 void인지 검사합니다. 일반 double*를 int 멤버로 복원하면 컴파일 오류입니다. void*는 예외로 허용되므로 caller가 실제 멤버 주소임을 보장해야 합니다. __same_type 문맥의 타입 표현은 보통 실행해 NULL에서 필드를 읽는 코드가 아닙니다.',
  '정확한 멤버 포인터 타입을 유지해 잘못된 호출을 compiler가 잡도록 합니다. 배열 멤버 전체 주소 &obj.array의 타입과 첫 원소 &obj.array[0]의 타입도 구분합니다. void* 변환으로 진단을 없앴다고 호출이 안전해진 것은 아닙니다.',
  '__same_type 두 조건·static_assert 메시지와 __mptr cast를 읽으세요.',
  [('double*를 int 멤버 포인터처럼 넘기면 이 검사 문맥에서는?','static_assert로 컴파일이 거절된다','실행 시 자동으로 double을 int로 변환한다','매크로는 값 변환기가 아닙니다. 포인터가 가리키는 멤버 형식의 호환을 정적으로 확인합니다.'),('void* 예외가 실제 객체 소속까지 검증하는가?','아니며 지워진 타입 정보를 호출자가 보장해야 한다','void*이면 모든 주소를 안전하게 복원한다','타입 정보가 없는 포인터를 허용할 뿐입니다. 메모리 소속·offset·수명 책임을 없애지 않습니다.')],
  [('배열','int array[4] 멤버의 &obj.array는 배열 전체 포인터입니다. int*와 배열 타입의 차이를 무시하지 않습니다.'),('진단 검사','별도 double*→int member fixture가 예상대로 컴파일 거절됐습니다. 정상 void* 예외는 실제 유효 멤버 주소만 검사했습니다.')])
 lesson('멤버 타입 얻기·typeof_member와 실행되지 않는 표현','typeof_member',
  '실제 객체를 만들지 않고 구조체 멤버의 타입을 compiler에 질의하는 GNU C 기법을 배웁니다.',
  'typeof_member(T,m)는 typeof(((T*)0)->m)입니다. 일반 고정 멤버 타입 문맥에서 ((T*)0)->m 표현의 값은 실행해 읽지 않고 타입을 얻습니다. 따라서 이를 NULL 객체가 실제로 존재하는 실행 접근으로 설명하면 안 됩니다. typeof는 GNU C 확장이며 가변 수정 타입의 평가 같은 더 넓은 언어 예외를 모든 경우에 무평가라고 일반화하지 않습니다.',
  'typeof_member(struct item,key) 변수;처럼 실제 멤버 형식을 재사용합니다. 일반 int 멤버라면 결과 타입도 int입니다. sizeof·typeof·_Generic의 타입 문맥과 실제 포인터 역참조 연산을 구분합니다.',
  'typeof_member 한 줄에서 타입 정보로 사용되는 전체 표현을 읽으세요.',
  [('일반 int 멤버의 typeof_member가 NULL 메모리에서 값을 읽는가?','아니며 타입 정보를 구한다','반드시 NULL dereference를 실행한다','이 표현은 typeof의 타입 질의 문맥입니다. 같은 문법 조각이 실제 실행 접근과 동일한 의미를 갖는 것은 아닙니다.'),('typeof_member가 GNU C 문맥 없이 모든 언어에서 똑같은 API인가?','아니며 compiler와 언어 지원을 확인한다','모든 C++·표준 C 버전에서 동일하다','커널 compiler 환경의 확장을 사용합니다. 다른 언어·엄격한 표준 모드의 지원을 추측하지 않습니다.')],
  [('정적 확인','실제 compiler 타입 assertion으로 typeof_member(struct record,key)가 int임을 확인했습니다.'),('지원 조건','이 fixture는 -std=gnu11 GCC에서 실행합니다. 커널의 compiler helper 전체를 그대로 가져온 검사가 아니라 필요한 static_assert와 same_type 정의를 제공합니다.')])
 lesson('const 보존·container_of_const의 Generic 선택','container_of_const',
  '일반 부모 복원에서 잃는 const를 전용 helper가 다시 보존하는 타입 선택 원리를 배웁니다.',
  '일반 container_of는 __mptr를 void*로 저장하고 type*를 반환해 입력 ptr의 const를 잃는다고 경고합니다. container_of_const는 _Generic으로 const 멤버 포인터면 const type*,그 외에는 type*를 선택합니다. 런타임 객체 복사나 if가 아니라 compiler 타입 선택입니다. const는 쓰기 허가에 대한 타입 계약이며 객체 수명 보호나 메모리 불변성의 전역 증명이 아닙니다.',
  'const 멤버 주소를 받는 읽기 전용 경로에서는 container_of_const를 사용합니다. 반환 부모가 const인 상태에서 일반 필드 대입은 compiler가 거절해야 합니다. 원래 객체의 소유권·잠금·다른 writer는 별도로 관리합니다.',
  '일반 helper의 경고와 _Generic const/default 반환형을 비교하세요.',
  [('const 멤버 주소로 container_of_const를 호출한 반환형은?','const 부모 구조체 포인터다','항상 쓰기 가능한 부모 포인터다','_Generic의 const 분기가 부모 타입에도 const를 붙입니다. 일반 container_of의 const 손실과 다릅니다.'),('const 부모 반환값의 일반 필드에 대입하면?','컴파일러가 읽기 전용 대입을 거절한다','helper가 const를 자동으로 제거한다','전용 helper의 타입 보존을 실제 사용까지 유지해야 합니다. 별도 cast로 강제 우회하는 것은 이 보호와 다릅니다.')],
  [('컴파일 검사','const/nonconst/일반 helper 반환형을 정적 검사하고 const 결과에 field 대입하는 fixture의 컴파일 거절을 확인했습니다.'),('실행 없음','_Generic 제어 표현의 타입 선택은 런타임에 두 변환을 모두 실행하는 분기가 아닙니다. 선택된 표현의 값만 사용합니다.')])
 lesson('한 번 평가와 수명 전제·복원은 유효성 검사가 아니다','container_of',
  '매크로에서 인자를 여러 번 쓴 것처럼 보여도 타입 문맥과 값 평가를 구분하고 객체 수명의 한계를 배웁니다.',
  'container_of는 ptr 값을 __mptr에 한 번 저장합니다. 일반 고정 멤버 포인터의 타입 검사 표현은 추가 값 실행을 하지 않습니다. GNU statement expression으로 지역 변수와 반환식을 묶으므로 함수 안의 표현식 문맥을 사용합니다. NULL·ERR_PTR·해제된 객체·다른 객체의 멤버 주소에서 임의로 offset을 빼면 유효 부모를 보장하지 않습니다.',
  '부작용이 없는 명확한 ptr를 권장하고 실제 부모 객체 수명을 유지한 상태에서 복원합니다. NULL/오류는 먼저 처리하고 참조·RCU·잠금 계약을 지킵니다. 매크로의 타입 검사 성공을 객체가 살아 있다는 근거로 사용하지 않습니다.',
  '__mptr 값 대입과 타입 검사 문맥·statement expression 범위를 확인하세요.',
  [('타입 검사가 통과하면 부모 객체가 살아 있음을 증명하는가?','아니며 객체 수명은 별도 전제다','해제된 객체도 자동으로 되살린다','compiler는 포인터 형식을 확인합니다. 이미 해제된 메모리의 수명이나 실제 주소 소속을 복구하지 않습니다.'),('일반 고정 멤버 getter를 ptr로 넣은 정상 검사에서 값 실행 횟수는?','한 번이다','타입 검사 때문에 항상 세 번이다','값은 __mptr에 저장하고 나머지는 타입 문맥입니다. 언어 확장의 평가 규칙과 실제 값 접근을 구분합니다.')],
  [('위치 조건','독립 타입 검사를 파일 scope에 두면 GNU statement expression 사용 위치 오류가 났습니다. 해당 정적 타입 확인은 함수 내부로 옮겨 실행했습니다.'),('전체 결과','원문 header로600,002개 비교와 잘못된 타입·const 대입 컴파일 거절을 확인했습니다. native GNU C layout 문맥이며 임의 포인터 수명·native32·sparse 검증은 아닙니다.')])
