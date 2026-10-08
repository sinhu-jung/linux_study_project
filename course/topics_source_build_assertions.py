"""Full build_bug header and selected actual compiler optimization contracts."""
def register(topic,q,detail):
 def lesson(title,symbol,why,principle,use,reading,qa,cards,occurrence=1):
  topic(title,'라이브러리·알고리즘','include/linux/build_bug.h',symbol,why,principle,use,reading,*(q(*x) for x in qa),details=[detail(*x) for x in cards],source_occurrence=occurrence)
 lesson('정수 식 안의 빌드 검사·음수 bit field로 거절','BUILD_BUG_ON_ZERO',
  '상수 초기화나 다른 산술 식 안에서 오류 조건을 검사하면서 정상 결과0을 제공하는 GNU C 기법을 배웁니다.',
  '일반 BUILD_BUG_ON_ZERO(e)는 sizeof(struct { int:(-!!e); })를 int로 변환합니다. e가 참이면 unnamed bit field 폭이-1이 되어 컴파일이 거절됩니다. 거짓이면 폭0인 GNU 구조체 식의 크기0을 제공해 결과0입니다. 런타임 bool 오류 함수가 아니라 compiler의 상수 bit field 제약을 이용합니다. __CHECKER__ 분기는 별도로0만 정의합니다.',
  '상수 조건을 검사하며 정상 값에0을 더하는 GENMASK 같은 사용처를 연결합니다. 동적 e를 일반 분기에 넣으면 bit field 상수 조건을 만족하지 못할 수 있습니다. 표준 C 모든 구현의 빈 구조체 크기를 일반화하지 않습니다.',
  '두 조건부 정의 중 일반 bit field 정의와 -!!e를 읽으세요.',
  [('일반 분기에서 e가 참이면 bit field 폭은?','-1이라 컴파일이 거절된다','항상0이라 검사하지 않는다','!!e는 참이면1이고 그 앞의 음수가-1을 만듭니다. 음수 폭은 허용되지 않습니다.'),('정상 결과0을 제공하는 목적은?','정수 초기화·산술 식 안에 검사를 넣기 위해서다','실패 errno0을 런타임에 전달하려고다','값을 내는 식 형태로 만들어 기존 정수 결과에 영향을 주지 않으면서 상수 오류를 잡습니다.')],
  [('GNU 문맥','유효0의 크기 식은 GNU compiler 문맥에서 확인했습니다. 빈 구조체를 모든 표준 C compiler의 같은 크기라고 설명하지 않습니다.'),('실제 진단','e1과 동적 e의 별도 파일은 일반 분기에서 컴파일이 거절됐고 정상 e0은 전역 초기화에 사용할 수 있었습니다.')],2)
 lesson('표현식 유효성만 검사·sizeof로 부작용 생략','BUILD_BUG_ON_INVALID',
  '표현식을 compiler가 검사하게 하면서 실제 값 계산이나 부작용은 실행하지 않는 기법을 배웁니다.',
  'BUILD_BUG_ON_INVALID(e)는 sizeof((__force long)e)를 void로 버립니다. 표현식이 형식상 유효해야 컴파일되지만 고정 long형 sizeof 문맥이라 e의 값 실행은 없습니다. 예제의 counter++도 증가하지 않습니다. 이것은 e가 참인지 검사하는 BUILD_BUG_ON과 다른 기능이며 표현식 유효성과 실행 값의 논리 조건을 구분해야 합니다.',
  '타입·이름 유효성만 확인하고 실제 접근을 생성하지 않으려는 문맥에 사용합니다. 존재하지 않는 이름이나 허용되지 않은 표현식은 compiler가 거절합니다. 실제 데이터 값·주소 접근 안전성은 이 검사로 확인되지 않습니다.',
  'sizeof의 피연산자와 __force long 변환·void 반환을 읽으세요.',
  [('counter++를 이 고정 long sizeof 안에 넣으면 counter는?','증가하지 않는다','유효성 검사 때 한 번 증가한다','sizeof의 고정 타입 문맥은 피연산자를 실행하지 않습니다. compiler의 형식 검사와 런타임 부작용을 구분합니다.'),('존재하지 않는 이름을 e에 넣으면?','컴파일이 거절된다','실행하지 않으니 이름 오류도 무시된다','무평가 표현식이어도 구문·타입 유효성은 필요합니다. 실행 생략과 compiler 검사 생략은 다릅니다.')],
  [('전제','여기서는 long cast로 타입을 고정합니다. 모든 sizeof 표현식의 가변 배열 평가 예외까지 무평가라고 일반화하지 않습니다.'),('확인','counter0에 매크로를 적용한 뒤0이 유지됐고 존재하지 않는 이름을 쓴 파일은 컴파일이 거절됐습니다.')])
 lesson('조건 참이면 빌드 실패·MSG와 compiler 제거','BUILD_BUG_ON_MSG',
  '오류 조건이 compiler에서 남으면 진단 함수를 호출하도록 만드는 빌드 검사와 최적화의 관계를 배웁니다.',
  'BUILD_BUG_ON_MSG(cond,msg)는 compiletime_assert(!cond,msg)를 호출하고 BUILD_BUG_ON은 기본 메시지를 제공합니다. 선택 compiler_types 원문은 __OPTIMIZE__일 때 error 속성의 선언을 만들고 조건이 거짓이면 그 함수를 호출합니다. optimizer가 정상 조건의 호출을 제거하면 통과하고 남으면 compiler 진단이 납니다. 최적화가 없으면 이 helper 블록은 빈 do/while로 정의됩니다.',
  '커널의 지원 compiler·최적화 문맥에서 내부 불변조건을 검사합니다. 동적 외부 입력의 런타임 오류 처리를 이것으로 대신하지 않습니다. -O0에서도 무조건 같은 검사로 실패한다고 주장하지 않습니다.',
  'MSG→compiletime_assert와 compiler_types.h의 __OPTIMIZE__ 분기를 함께 읽으세요.',
  [('BUILD_BUG_ON의 cond가 참이면 정상 최적화 문맥에서?','빌드가 실패해야 한다','검사를 통과한다','BUILD_BUG_ON은 버그 조건이 참일 때 실패합니다. 내부 compiletime_assert에는 부정한 조건을 전달합니다.'),('선택 compiler helper에서 최적화 없는 -O0 분기는?','빈 검사로 정의된다','언제나 같은 error 함수 호출을 유지한다','원문의 __OPTIMIZE__ 조건을 확인했습니다. 지원 build 문맥과 다른 compiler 옵션의 결과를 구분합니다.')],
  [('진단 이름','선택 helper는 __COUNTER__와 token 결합으로 선언 이름을 구분합니다. 같은 매크로를 여러 번 쓰는 문맥을 지원합니다.'),('확인','-O2에서는 참 조건·명시 메시지가 거절됐고 -O0에서는 같은 BUILD_BUG_ON(1) 파일이 컴파일됐습니다. 런타임 assert 대용으로 쓰면 안 됩니다.')])
 lesson('거듭제곱 상수 검사·0을 따로 제외하는 이유','BUILD_BUG_ON_NOT_POWER_OF_2',
  '비트 연산으로2의 거듭제곱을 판별할 때0이 예외가 되는 이유와 내부·공개 helper 차이를 배웁니다.',
  '양수2의 거듭제곱 n은 비트 하나만 켜져 n&(n-1)==0입니다. 하지만0도 같은 식이0이므로 공개 BUILD_BUG_ON_NOT_POWER_OF_2는 n==0을 추가로 검사합니다. 내부 __BUILD_BUG_ON_NOT_POWER_OF_2는0 조건이 없습니다. 고정 상수의 버퍼 크기·mask 계약에 쓰는 build 검사이며 일반 런타임 값을 반환하는 판정 함수가 아닙니다.',
  '원형 버퍼·비트 mask의 상수 크기가 양수 거듭제곱인지 확인합니다. 내부 이름의 밑줄을 무시하고 같은0 처리라고 설명하지 않습니다. 상수 타입·양수 조건과 지원 build 문맥을 유지합니다.',
  '두 helper의 n&(n-1)와 공개 n==0 항을 비교하세요.',
  [('n0이 단순 n&(n-1) 식에서 거듭제곱처럼 보이는가?','식 결과0이라 별도 제외가 필요하다','결과가 항상1이어서 자동 거절된다','비트 하나라는 수학 조건에는 양수 전제가 있습니다. 0은 하나도 켜져 있지 않아 별도 검사가 필요합니다.'),('공개 helper와 내부 helper의0 처리가 같은가?','아니며 공개 helper만 n==0을 추가한다','두 정의가 문자 그대로 동일하다','원문 두 식을 비교합니다. API 이름이 비슷해도 검사 범위가 다를 수 있습니다.')],
  [('숫자 예','8의1000과7의0111을 AND하면0입니다. 6의0110과5의0101을 AND하면0100으로 실패 조건이 됩니다.'),('확인','공개 상수0·3은 거절됐고1·2·64는 통과했습니다. 내부 helper0이 통과하는 차이도 확인했습니다.')])
 lesson('도달하면 안 되는 빌드 경로·BUILD_BUG','BUILD_BUG',
  'compiler가 제거해야 하는 코드가 남으면 빌드를 막는 방식과 런타임 abort의 차이를 배웁니다.',
  'BUILD_BUG()는 BUILD_BUG_ON_MSG(1,메시지)입니다. 원문은 compiler가 제거할 것으로 기대하는 경로가 남았는지 확인하는 용도를 설명합니다. 최적화 문맥에서 도달 가능한 호출이 남으면 빌드가 실패하고 if(0)처럼 제거되는 경로는 통과합니다. 실행 중 태스크를 중단하는 BUG()나 사용자 assert와 다른 기술입니다.',
  '상수 선택·compiler가 제거해야 하는 분기의 내부 검사에 씁니다. 실행 중 발견한 잘못된 외부 입력을 처리하려면 실제 조건 분기와 오류 정책을 작성합니다. -O0 helper 차이도 함께 고려합니다.',
  'BUILD_BUG의 참 상수와 eliminated code에 관한 주석을 읽으세요.',
  [('최적화된 도달 가능 BUILD_BUG 호출은?','빌드 실패를 일으킨다','실행할 때만 errno를 반환한다','error 진단 함수 호출이 남으면 compiler가 거절합니다. 런타임 오류 반환 함수가 아닙니다.'),('if(0) 안의 BUILD_BUG가 통과할 수 있는 이유는?','compiler가 그 호출 경로를 제거하기 때문이다','BUILD_BUG가 모든 조건에서 검사0이라서다','지원 최적화 문맥에서는 불가능한 분기를 제거합니다. 남은 호출과 제거된 호출의 차이를 확인합니다.')],
  [('원리 구분','compile-time 불가능성 확인과 실행 중 불변조건 점검은 목적과 실패 시점이 다릅니다.'),('진단','원문 fixture의 if(0) 호출은 통과했고 도달 가능한 별도 호출 파일은 -O2에서 거절됐습니다.')])
 lesson('static_assert·전역 선언과 정수 상수식','static_assert',
  'C11 정적 assertion과 optimizer 기반 검사의 조건·실패 방향·사용 위치 차이를 배웁니다.',
  'static_assert는 __static_assert를 통해 _Static_assert(expr,msg)를 사용합니다. expr가 참이어야 통과하며 BUILD_BUG_ON의 버그 조건 방향과 반대입니다. 전역 scope에도 둘 수 있지만 정수 상수식이 필요합니다. 메시지를 생략하면 매크로가 expr를 문자열화한 기본 메시지를 제공합니다. optimizer가 상수로 알 수 있다는 사실만으로 C 정수 상수식 조건이 자동 충족되지는 않습니다.',
  '구조체 크기·enum 값·컴파일 상수 관계를 전역 또는 함수 문맥에서 검사합니다. 런타임 함수 인자와 일반 변수 비교는 이 static_assert에 넣지 않습니다. 메시지를 구체적으로 작성하면 실패 원인을 읽기 쉽습니다.',
  '두 단계 매크로·##__VA_ARGS__·#expr·_Static_assert를 읽으세요.',
  [('static_assert(조건)가 통과하려면 조건은?','참이어야 한다','버그 조건이라 참이면 항상 실패한다','C11 assertion은 참 조건을 요구합니다. BUILD_BUG_ON은 거절할 버그 조건을 인자로 받는다는 차이가 있습니다.'),('함수 인자의 x==1을 일반 정수 상수식처럼 쓰면?','compiler가 상수식 요구로 거절할 수 있다','실행 중 x를 기다려 검사한다','_Static_assert는 런타임 검사가 아닙니다. 상수식의 언어 조건을 만족해야 합니다.')],
  [('scope','전역 static_assert(sizeof(int)==4)는 이 compiler 문맥에서 통과했습니다. GNU statement expression의 파일 scope 제약과 별개입니다.'),('진단','false 상수와 동적 조건의 파일은 각각 거절됐습니다. 일반 compiler 최적화 on/off와 C11 상수식의 역할을 구분합니다.')])
 lesson('구조체 offset 불변조건·ABI와 패딩 보호','ASSERT_STRUCT_OFFSET',
  '파일 형식이나 내부 구조 레이아웃에서 기대 멤버 위치가 바뀌면 빌드를 막는 방법을 배웁니다.',
  'ASSERT_STRUCT_OFFSET(type,field,expected)는 offsetof(type,field)!=expected를 BUILD_BUG_ON_MSG로 검사합니다. compiler가 정렬 패딩을 포함해 정한 실제 위치를 기대값과 비교합니다. 조건이 맞지 않으면 field 위치가 바뀌었다는 진단을 냅니다. 이미 읽은 디스크 내용·사용자 메모리의 런타임 유효성을 확인하는 기능은 아닙니다.',
  '특정 ABI·포맷을 표현하는 C 구조체에서 기대 레이아웃을 확인합니다. 학습 fixture의 char 다음 int key는 이 compiler에서 offset4이며0을 기대하면 거절됩니다. 모든 architecture에 같은 패딩을 가정하지 말고 해당 ABI 계약에 맞춰 기대값을 정합니다.',
  'offsetof 비교와 메시지의 type/field 문자열 결합을 읽으세요.',
  [('offset assertion이 비교하는 것은?','compiler가 정한 실제 멤버 위치와 기대 상수다','현재 디스크 데이터의 field 값이다','형식 레이아웃의 build-time 검사입니다. 런타임 데이터 검증과 혼동하지 않습니다.'),('char 뒤 int의 offset이 모든 architecture에서 반드시 같다고 가정하는가?','아니며 실제 ABI·정렬 계약을 확인한다','필드 타입 이름만 있으면 모든 플랫폼에서 같다','compiler layout은 ABI와 타입 정렬에 의존합니다. 기대 레이아웃을 보호하는 조건을 구체적으로 작성합니다.')],
  [('사용 효과','헤더 수정이나 compiler layout 변화로 특정 계약이 깨질 때 초기 빌드 단계에서 발견할 수 있습니다.'),('확인','native long64 GNU11의 offset4는 통과했고 기대0은 거절됐습니다. 다른 ABI의 레이아웃 증명으로 확대하지 않습니다.')])
 lesson('checker 분기·분석 표식과 실제 compiler 진단','BUILD_BUG_ON_ZERO',
  '정적 분석기용 전처리 분기와 일반 C compiler가 같은 이름에 다른 정의를 쓰는 조건을 배웁니다.',
  '__CHECKER__ 분기에서는 BUILD_BUG_ON_ZERO(e)가0으로 정의됩니다. 일반 compiler의 음수 bit field 검사와 다릅니다. 이것만으로 static_assert나 모든 build 검사가 사라졌다고 일반화하면 안 됩니다. 실제 sparse 분석은 더 많은 타입 표식·검사 문맥을 사용하므로 -D__CHECKER__만 둔 일반 compiler 실행은 sparse 전체 분석을 재현하지 않습니다.',
  '어느 compiler·분석 단계가 어떤 매크로 정의를 보는지 확인합니다. 원본 결과가 compiler 옵션·전처리 조건에 따라 달라지는 이유를 기록하고 한 모델의 통과를 모든 구성의 안전성 증명으로 계산하지 않습니다.',
  'BUILD_BUG_ON_ZERO의 checker0 분기와 일반 정의를 비교하세요.',
  [('checker0 분기에서 BUILD_BUG_ON_ZERO(1)의 값은?','0이다','일반 분기와 똑같이 음수 bit field다','조건부 정의를 직접 확인합니다. 같은 API 이름이라도 전처리 선택에 따라 실제 검사 구현이 달라집니다.'),('일반 compiler에 __CHECKER__만 정의하면 sparse 전체 검사도 실행된 것인가?','아니며 특정 전처리 분기만 확인한 것이다','모든 주소 공간·타입 분석을 자동 실행한다','분기 확인과 분석기 실행은 다른 검증입니다. 실제로 사용한 도구와 검사 범위를 기록해야 합니다.')],
  [('확인','checker 분기의0을 정적 assertion으로 확인했습니다. source compiler_types의 선택 최적화 블록도 그대로 포함했습니다.'),('전체 결과','정상 사용을 최적화·ASan/UBSan에서 실행하고11종 오류 파일의 컴파일 거절을 확인했습니다. -O0 helper 생략과 checker0 차이를 포함하며 compiler 헤더 전체·sparse·runtime assertion의 검증은 아닙니다.')])
