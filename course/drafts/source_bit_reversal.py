"""Complete bitrev header and ARM/ARM64 instruction helpers."""
def register(topic,q,detail):
 def lesson(title,path,symbol,why,principle,use,reading,qa,cards):
  topic(title,'라이브러리·알고리즘',path,symbol,why,principle,use,reading,*(q(*x) for x in qa),details=[detail(*x) for x in cards])
 def generic(title,symbol,why,principle,use,reading,qa,cards):
  lesson(title,'include/linux/bitrev.h',symbol,why,principle,use,reading,qa,cards)
 generic('8비트 reversal·256개 lookup table의 인덱스','__bitrev8',
  'byte 내부 bit 위치를 거꾸로 만드는 연산을 byte 순서 교환과 구분해서 배웁니다.',
  'generic __bitrev8은 u8 입력을 byte_rev_table[byte]의 인덱스로 사용합니다. 표의 각 값은 입력의 bit0..7을 bit7..0으로 옮긴 결과입니다. 예를 들어0x12의00010010은01001000인0x48이 됩니다. 입력 범위가256개라 표를 고정 크기로 미리 만들 수 있고 호출 때 bit별 loop를 수행하지 않습니다.',
  'bit 전송 순서가 반대인 하드웨어나 정해진 알고리즘 경계를 읽을 때 사용합니다. 바이트 순서를 바꾸려는 목적이면 swab 계열을 구분합니다. 이 연산을 모든 network endian 변환으로 무조건 적용하지 않습니다.',
  'u8 인자·const table 선언·인덱스 접근과 lib/bitrev.c의 표를 연결하세요.',
  [('bitrev8(0x12)의 결과는?','0x48이다','byte가 하나라 항상0x12이다','한 byte 내부의 bit 순서를 뒤집습니다. byte 순서 교환과 달리 한 byte에도 변화가 있습니다.'),('lookup table의 원소 수가256인 이유는?','u8 입력의 가능한 비트 패턴이256개여서다','모든 정수 폭이256비트여서다','8비트 입력은2의8승 개입니다. 각 입력을 결과 값에 직접 대응시킬 수 있습니다.')],
  [('전체 표','이미 작성된 lib/bitrev.c의256개 원소와 연결됩니다. 새 fixture도 모든 입력을 독립 bit loop와 비교했습니다.'),('수명','표는 const 정적 데이터입니다. 호출마다 결과 배열을 할당하거나 데이터를 수정하는 알고리즘이 아닙니다.')])
 generic('16비트 reversal·byte 내부 반전과 위치 교환','__bitrev16',
  '작은 reversal 두 번과 두 byte 위치 변경으로 넓은 reversal을 구성하는 원리를 배웁니다.',
  '__bitrev16은 낮은8비트와 높은8비트를 따로 __bitrev8로 뒤집습니다. 낮은byte의 결과를8칸 올리고 높은byte의 결과를 낮은 위치에 OR합니다. 두 byte 안의 bit를 반대로 하는 것에 더해 byte의 위치도 교환해야 전체16비트 순서가 뒤집힙니다.0x1234의 결과는0x2c48입니다.',
  '입력을 byte 두 개로 나눠 각각의 reversed 값과 새 위치를 그립니다. 내부 bit만 뒤집고 위치를 그대로 두는 계산과 구분합니다. 입력 타입이u16이라는 폭 계약을 확인합니다.',
  'x&0xff·x>>8·각 bitrev8·왼쪽8칸 이동과 OR를 읽으세요.',
  [('bitrev16(0x1234)의 결과는?','0x2c48이다','0x3412다','12→48,34→2c로 bit를 뒤집고 두 결과의 위치도 교환합니다.3412는 byte swap 결과입니다.'),('두 byte 내부 bit만 반전하고 위치를 유지하면 full16 reversal인가?','아니며 두 byte의 위치도 바꿔야 한다','내부 반전만으로 항상 전체 순서가 뒤집힌다','전체bit의 양끝 위치까지 반대가 되어야 합니다. byte 내부 반전과 byte 위치 변경이 모두 필요합니다.')],
  [('검사','65536개 입력을 전부 독립16bit reversal과 비교했습니다. 대표 예 하나로만 동치를 추측하지 않았습니다.'),('연결','8비트 표를 재사용하여16비트 결과를 만듭니다. 별도의65536개 table을 만들지 않습니다.')])
 generic('32비트 reversal의 재귀 합성·정수 승격도 읽기','__bitrev32',
  '두16비트 결과를 결합하는 기술과 중간 shift 타입을 원문에서 확인하는 방법을 배웁니다.',
  '__bitrev32는 낮은16비트와 높은16비트를 __bitrev16로 뒤집고 두 절반 위치를 교환합니다. 낮은 절반의 결과를16칸 올린 뒤 OR합니다. __bitrev16의 u16 반환값은 shift 식에서 int로 승격될 수 있으므로 최종 u32 반환형만 보고 중간 연산이 unsigned라고 가정하지 않습니다. 커널의 GNU compiler·옵션 맥락과 ISO C 이식성을 구분합니다.',
  '0x12345678을 두 절반으로 나눠0x1e6a2c48을 계산합니다. 이식을 연습할 때는 shift 전에 u32로 넓히는 식과 비교합니다. 원본 검사 통과를 모든 compiler 옵션에서의 표준 C 안전성 증명으로 확대하지 않습니다.',
  '__bitrev16 반환형·정수 승격·16칸 shift·OR 및 반환형을 읽으세요.',
  [('전체32 reversal을 만들 때 두16비트 절반의 위치는?','뒤집힌 뒤 서로 교환된다','항상 원래 절반 위치를 유지한다','각 절반 내부 순서와 두 절반 위치를 모두 바꿔야 전체32bit의 순서가 반대가 됩니다.'),('최종 반환형이u32이면 shift의 중간 타입도 반드시u32인가?','아니며 반환 전 식의 승격 규칙을 봐야 한다','반환형이 모든 내부 연산 타입을 자동 바꾼다','C 연산은 당시 피연산자와 정수 승격의 타입으로 계산됩니다. 최종 반환형만으로 중간 타입을 판단하지 않습니다.')],
  [('검사 문맥','generic fixture는 GNU11과 -fwrapv를 사용했고 최적화·ASan/UBSan에서 확인했습니다. 모든 ISO C 문맥의 안전성 주장으로 기록하지 않습니다.'),('독립 기준','입력의bit를 하나씩 꺼내 unsigned32로 조립하는 reference를 사용해 원문의 재귀 식을 복사하지 않았습니다.')])
 generic('상수8 reversal·4칸 2칸 1칸의 단계 교환','__constant_bitrev8',
  '병렬 mask·shift로 bit 위치를 점점 작은 구간에서 교환하는 알고리즘을 배웁니다.',
  '__constant_bitrev8은 먼저 높은4bit와 낮은4bit를 교환합니다. 다음에 CC/33 mask로2bit 묶음을 바꾸고 마지막에 AA/55로 홀수·짝수 bit 위치를 교환합니다.8→4→2→1 크기의 위치 관계를 단계적으로 반대로 만듭니다. GNU statement expression 안에서 x를 u8 지역 변수에 한 번 받아 단계 결과를 누적합니다.',
  '0x12의 bit를4개씩 나누고2개씩 나눈 뒤1개씩 바꿔 결과를 따라갑니다. 보수 NOT처럼0과1 자체를 뒤집는 연산과 bit 위치 반전을 구분합니다.',
  'u8 지역 변수·4칸 이동·CC/33·AA/55 mask를 읽으세요.',
  [('AA/55 mask 단계의 목적은?','이웃한 홀수·짝수 bit 위치를 교환한다','모든bit 값을 보수로 뒤집는다','각 mask가 서로 다른 위치의bit를 고르고1칸 이동합니다. bit 값 자체를0↔1로 바꾸는 NOT이 아닙니다.'),('이 상수8 helper는 x 식을 각 단계마다 다시 평가하는가?','아니며 처음 지역 변수에 한 번 저장한다','mask가 세 번 나오므로 입력 식도 세 번 실행한다','지역 ___x에 입력을 먼저 받습니다. 이후 계산은 지역 변수 값을 사용합니다.')],
  [('macro 비교','swab의 private 상수 식은 인자 반복이 있지만 이 bitrev helper는 지역 변수를 사용합니다. 모든 macro의 평가 계약이 같다고 추측하지 않습니다.'),('범위','GNU statement expression은 ISO C의 일반 식 구문과 다릅니다. kernel compiler 확장 맥락을 확인합니다.')])
 generic('상수16 reversal·byte 교환 후 세분화','__constant_bitrev16',
  '더 넓은 입력에서 같은 단계 교환 구조를 재사용하는 알고리즘을 배웁니다.',
  '__constant_bitrev16은 두8bit 절반을 바꾸고 F0F0/0F0F로4bit 묶음,CCCC/3333으로2bit 묶음,AAAA/5555로1bit 위치를 교환합니다. 각 mask는 전체16비트에 같은 구간 패턴을 반복합니다. 지역 변수는 u16이라 단계별 대입에서 입력 폭을 유지하고 최종 값을 반환합니다.',
  '단계마다16bit 줄을 그려 어떤 구간이 이동하는지 확인합니다. mask의 반복 패턴을 외우기보다 구간 크기와 연결합니다. 넓은 입력을 넘겼을 때 먼저 좁은 타입으로 변환되는 조건도 확인합니다.',
  '8칸 이동·반복된4/2/1bit mask·u16 대입을 읽으세요.',
  [('F0F0/0F0F mask는 어느 크기의 묶음을 교환하는가?','4bit 묶음이다','전체16bit를 한 번 더 byte swap한다','반복된 높은·낮은 nibble을 분리해4칸 이동합니다. 이어지는2bit와1bit 단계가 더 작은 구간을 교환합니다.'),('지역 u16 변수의 목적을 어떻게 읽어야 하는가?','입력과 단계 결과를16비트 폭으로 다룬다','모든 입력을64비트로 자동 확장한다','원문은 u16 ___x에 입력을 받습니다. 타입과 대입이 실제 폭을 정하며 함수 이름만으로 더 큰 폭을 기대하지 않습니다.')],
  [('확인','모든16bit 값의 상수 helper 경로도 독립 reference와 비교했습니다.'),('패턴','같은 단계 교환 원리라도 구간의 반복 횟수와 타입 폭은 다릅니다.8bit mask를 그대로 복사하지 않습니다.')])
 generic('상수32 reversal·16 8 4 2 1의 교환 네트워크','__constant_bitrev32',
  '32비트 전체 순서를 고정 수의 mask·shift 단계로 바꾸는 원리를 배웁니다.',
  '__constant_bitrev32는16비트 절반 교환을 시작으로8·4·2·1비트 구간을 교환합니다.32bit 안의 각 bit는 이 다섯 단계에서 반대편 위치로 이동합니다. 지역 변수는u32이며 각 단계는 unsigned32 mask와 shift로 이루어집니다. 결과의byte 순서는 물론 각byte 내부bit 순서까지 반대로 됩니다.',
  '각 단계의 mask가 고르는 구간을 색으로 나눠 입력bit 하나의 이동을 추적합니다.32개의 one-hot 입력으로 bit i가31-i 위치로 가는지 확인합니다. 데이터와 무관하게 단계 수가 고정인 알고리즘임을 읽습니다.',
  '16칸 절반 교환과 FF/F0/CC/AA 반복 mask를 읽으세요.',
  [('bit i 하나만 켜진32비트 입력의 reversal 결과 위치는?','31-i 위치다','항상 i+1 위치다','전체32bit의 순서를 반대로 하므로 양끝과 가운데가 서로 대응합니다. fixture는32개 one-hot 입력을 비교했습니다.'),('full32 bit reversal은 full32 byte swap과 같은가?','아니며 byte 내부bit까지 반전한다','두 연산은 모든 입력에서 같은 결과다','swab은byte 위치만 바꾸고 내부bit는 유지합니다. bitrev는 내부bit의 위치까지 바꿉니다.')],
  [('검사','10만32bit 입력의 상수 경로와 generic 경로, public 경로를 독립 reference와 대조했습니다.'),('성질','같은 폭 reversal을 두 번 하면 원래 값입니다. 해당 성질도 모든 난수 입력에서 검사했습니다.')])
 generic('8x4 reversal·byte 위치는 유지하고 내부만 반전','__bitrev8x4',
  '전체32bit 반전과 네byte 각각의bit 반전이 다른 permutation임을 배웁니다.',
  '__bitrev8x4는 __bitrev32(swab32(x))입니다. swab32로byte 위치를 한 번 바꾸고 fullbit reversal에서byte 위치가 다시 바뀌어 원래byte 위치가 유지됩니다. 각byte 내부bit만 반전됩니다.0x12345678은0x482c6a1e이며 full32 bitrev의0x1e6a2c48과 다릅니다.',
  '하드웨어가 각byte의 bit 전송 순서만 반대로 요구할 때 이 계열의 목적을 확인합니다. 데이터 포맷이byte 위치 교환도 요구하는지 구분합니다. 이름의8x4는32bit 안의8bit 단위 네 개를 뜻합니다.',
  'swab32 합성과 full __bitrev32, 각byte 결과 위치를 읽으세요.',
  [('bitrev8x4(0x12345678)의 결과는?','0x482c6a1e다','0x1e6a2c48다','각byte 안의bit만 반전하고 네byte의 위치는 유지합니다. full32 reversal과 다릅니다.'),('8x4 합성에서 swab32를 먼저 하는 이유는?','full reversal의byte 위치 교환을 상쇄하려고다','input을 암호화하려고다','byte 위치가 두 번 교환돼 원래로 돌아갑니다. byte 내부bit 반전만 남는 permutation입니다.')],
  [('확인','독립 byte별 bit loop reference와 합성식, double reversal을 함께 비교했습니다.'),('포함 계약','macro는 swab32 정의를 사용하는 경로입니다. 실제 사용 코드의 include 환경을 확인하고 다른 구성요소의 API를 암묵적으로 기대하지 않습니다.')])
 generic('상수8x4·큰 구간 교환을 생략하는 이유','__constant_bitrev8x4',
  '같은 mask 네트워크에서 필요한 단계만 남겨 다른 변환을 만드는 원리를 배웁니다.',
  '__constant_bitrev8x4는 full32와 달리16비트 절반 교환과8비트 byte 교환을 하지 않습니다.4·2·1bit mask 교환만 반복해서 각byte 내부의bit 순서를 반전합니다. 큰 구간의 위치를 움직이지 않아 네byte 순서는 유지됩니다. 지역u32에 입력을 한 번 저장한 뒤 세 단계를 실행합니다.',
  'full32 constant helper와 나란히 읽고 생략된 두 단계가 무엇을 바꾸는지 설명합니다. 같은byte별 변환을 loop나 lookup 대신 병렬 mask로 구현하는 방법을 연습합니다.',
  'F0/CC/AA mask 세 단계와 없는16/8칸 교환을 비교하세요.',
  [('상수8x4에서16bit 절반과8bit byte 교환이 빠진 이유는?','byte 위치를 유지해야 해서다','compiler가 큰 shift를 지원하지 않아서다','이 변환은byte 내부bit만 반전합니다. 큰 구간 교환을 넣으면 full32 reversal의 다른 결과가 됩니다.'),('이 helper가 입력 식을 각byte마다 네 번 평가하는가?','아니며 지역u32에 한 번 받는다','8x4라는 이름 때문에 반드시 네 번 평가한다','원문은 입력을 지역 변수에 한 번 저장합니다. 구간 개수와 인자 평가 횟수를 혼동하지 않습니다.')],
  [('검사','constant8x4와 runtime 합성 경로 모두10만 입력의 byte별 독립 reference와 비교했습니다.'),('재사용','동일한 mask 단계 구조를 필요한 구간 크기만 선택해 사용하는 알고리즘입니다.')])
 generic('공개 bitrev macro·한 번 평가와 좁은 입력 폭','bitrev32',
  '공개 API가 입력을 지역 변수에 받아 compiler 상수 판단과 runtime 경로를 선택하는 구조를 배웁니다.',
  'bitrev8/16/32/8x4는 먼저 해당u8/u16/u32 지역 __x에 입력을 한 번 받습니다. __builtin_constant_p(__x)가 참이면 constant helper,아니면 runtime helper를 고릅니다. 좁은 타입에 받은 뒤 reversal하므로 넓은 입력의 상위 bit는 그 폭에 남지 않습니다. 상수 여부는 compiler 문맥의 판단이며 모든 literal이 같은 machine instruction으로 구현된다는 보장은 아닙니다.',
  '원하는bit 폭에 맞춘 API를 선택하고 입력을 명확한 고정 폭 타입으로 준비합니다. x++의1회 평가와 private helper의 지역 변수 계약을 확인합니다. 자동 축소에 의존하기보다 필요하면 의도한 cast를 드러냅니다.',
  '지역 __x·constant_p 삼항 선택·폭별 runtime helper를 읽으세요.',
  [('bitrev32(x++)는 원문의 지역 저장 구조에서 x를 몇 번 증가시키는가?','한 번이다','32bit라32번이다','입력 식은 지역 변수의 초기화에 한 번 나타납니다. 이후 계산은 저장된 값을 사용합니다.'),('넓은 값0x112를8bit 입력으로 축소한 뒤 reversal하면?','낮은byte0x12의 결과0x48이다','전체9bit 순서를 반전한다','u8에 입력을 받는 폭 계약입니다. 상위 bit가 남지 않으며 원문 literal에는 compiler의 축소 경고가 날 수도 있습니다.')],
  [('실제 검사','public32와 constant32,public8x4에 부작용 인자를 전달한1회 평가를 검사했습니다. 넓은 runtime 입력의8bit 축소도 확인했습니다.'),('초기 진단','직접 넓은 literal을 사용한 fixture가 -Werror=overflow에서 거절돼 의도한 runtime 축소 사례로 바꿨습니다. 경고를 전체 비활성화하지 않았습니다.')])
 generic('bit reversal 구현 선택·generic table과 arch hook','__bitrev8',
  '설정에 따라 C table 경로와 architecture instruction 경로가 달라지는 구조를 배웁니다.',
  'CONFIG_HAVE_ARCH_BITREVERSE가 정의되면 asm/bitrev.h를 포함하고 __bitrev8/16/32를 __arch_bitrev 이름에 연결합니다. 없으면byte lookup과 재귀 합성을 정의합니다. public macro의 constant helper는 별도로 유지됩니다. runtime 호출의 구현 선택과 compiler가 상수식을 접는 선택은 서로 다른 층입니다.',
  '현재 architecture의 설정과 asm/bitrev.h를 확인합니다. generic table을 검사했다고 모든 architecture hook을 실행한 것으로 판단하지 않습니다. 소스 선택과 실제 machine instruction 실행 증거를 함께 기록합니다.',
  '설정 #ifdef·arch aliases·generic else·public constant 선택을 읽으세요.',
  [('CONFIG_HAVE_ARCH_BITREVERSE가 있는 runtime __bitrev32는 어디로 연결되는가?','architecture의 __arch_bitrev32다','항상256원소 table loop다','설정 분기가 architecture helper alias를 정의합니다. generic 함수 정의는 else 쪽입니다.'),('arch 선택과 constant_p 선택은 같은 하나의 조건인가?','아니며 runtime 구현 선택과 상수 경로 선택이 다르다','둘 다 같은 설정 매크로 하나만 본다','설정은 runtime helper 구현을 고르고 public macro의 compiler 상수 판단은 다른 분기입니다.')],
  [('검사','새 fixture는 generic 구성과 실제 ARM64 rbit 구성을 각각 최적화·ASan/UBSan에서 검사했습니다.'),('범위','ARM32 원문은 읽고 해설했지만 native ARM32 실행 검사는 수행하지 않았습니다. architecture별 증거를 분리합니다.')])
 lesson('ARM64 rbit·32비트 레지스터의 bit 순서 명령','arch/arm64/include/asm/bitrev.h','__arch_bitrev32',
  'C helper가 inline assembly와 레지스터 제약을 통해 한 CPU 명령을 사용하는 방법을 배웁니다.',
  'ARM64 __arch_bitrev32는 rbit %w0,%w1을 실행합니다. %w는 AArch64의32bit W 레지스터 표현이며 출력 =r(x),입력 r(x) 제약으로 compiler가 일반 레지스터를 선택합니다. x는u32이고 결과를 반환합니다. 이 명령은bit 위치를 반전하는 것이며 memory barrier나 byte endian 변환의 모든 정책을 제공하지 않습니다.',
  '해당 architecture의 asm syntax와 operand 폭,입출력 제약을 함께 읽습니다. 같은 C 이름이 실제 instruction으로 연결되는 이유를 이해합니다. instruction 하나라는 사실을 잠금이나 공유 메모리 보호와 연결하지 않습니다.',
  'rbit·%w0/%w1·=r 출력과 r 입력·u32 반환을 읽으세요.',
  [('ARM64 원문의 %w operand가 가리키는 폭은?','32bit W 레지스터 표현이다','항상64bit X 레지스터 전체다','helper는u32이고 asm template도32bit register 표기를 선택합니다. 입력·출력의 실제 폭을 확인합니다.'),('rbit 명령이 메모리 동기화를 자동 제공하는가?','아니며 값의bit 위치 변환이다','모든 앞뒤 memory access를 잠근다','원문은 레지스터 값 변환과 반환입니다. 배리어나 공유 객체 잠금 계약은 없습니다.')],
  [('실행 증거','Linux ARM64 컨테이너에서 원본 inline asm을 실제 compiler로 빌드하고 독립32bit 기준과 비교했습니다.'),('속성','__attribute_const__는 인자에 의존하는 값 함수 속성입니다. const 객체나 memory synchronization 의미로 바꾸어 설명하지 않습니다.')])
 lesson('ARM64의8·16 reversal·32반전 뒤 오른쪽 정렬','arch/arm64/include/asm/bitrev.h','__arch_bitrev16',
  '넓은 instruction을 재사용한 뒤 필요한 좁은 결과를 꺼내는 원리를 배웁니다.',
  'u16 또는u8 입력을u32로 확장하면 상위 bit가0입니다.32bit rbit를 수행하면 원래16bit의 반전 결과가 상위16bit에,8bit 결과는 상위8bit에 놓입니다. __arch_bitrev16은16칸, __arch_bitrev8은24칸 오른쪽 shift해 결과를 낮은 위치로 정렬합니다. 작은 폭에 맞는 반환 타입으로 값을 돌려줍니다.',
  '0x0012를32bit로 반전한 결과의 위치를 그린 뒤 shift로 필요한8bit를 가져옵니다. zero extension과 sign extension을 혼동하지 않습니다. 좁은 입력 타입의 폭을 유지합니다.',
  'u32 cast·32bit helper 재사용·>>16 및 >>24를 읽으세요.',
  [('ARM64의8bit helper가32bit reversal 뒤24칸 내리는 이유는?','상위8bit에 놓인 결과를 낮은8bit로 가져오려고다','원래 값을24번 반복하려고다','zero-extended 입력의 유효8bit는 full32 reversal 후 상위8bit에 놓입니다.24칸 이동하면 원하는 좁은 결과가 됩니다.'),('u8/u16 입력을u32로 올릴 때 상위 bit는?','0으로 확장된다','항상1로 확장된다','입력은 unsigned 좁은 타입입니다. signed 부호 확장과 구분해 결과 위치를 계산합니다.')],
  [('검사','실제 ARM64 helper에서256개8bit와65536개16bit 입력을 전부 독립 reference와 비교했습니다.'),('연결','원문의 세 함수 전체를 읽었습니다. 작은 폭별로 별도 lookup table을 만드는 구현이 아닙니다.')])
 lesson('ARM32 rbit helper·architecture별 asm 표기를 따로 읽기','arch/arm/include/asm/bitrev.h','__arch_bitrev32',
  '비슷한 helper라도 architecture의 operand 문법과 실행 증거가 달라짐을 배웁니다.',
  'ARM32 파일도u32 __arch_bitrev32에 rbit를 사용하지만 asm template는 rbit %0,%1입니다. ARM64 파일의%w 표기와 그대로 같지 않습니다.8·16bit helper는 같은 zero-extension→32bit reversal→24/16shift 원리를 재사용합니다. __ASM_BITREV_H guard와 inline·const 속성은 포함과 compiler 최적화 문맥을 제공합니다.',
  'architecture별 원문을 나란히 읽어 같은 수학적 계약과 다른 asm 표기를 구분합니다. 다른 target compiler에서 텍스트가 비슷하다고 native 실행 검증을 했다고 기록하지 않습니다. 필요한 instruction 지원과 빌드 설정을 확인합니다.',
  'ARM32 파일 전체의 guard·rbit operand·8/16 wrapper를 읽으세요.',
  [('ARM32의 rbit template가 ARM64의%w0 표기와 완전히 같은가?','아니며 architecture별 operand 표기를 읽어야 한다','모든 asm 문자열은 architecture와 무관하게 같다','두 파일은 같은 값 변환을 목표로 하지만 operand 문법이 다릅니다. 실제 target compiler 문맥을 확인합니다.'),('ARM64 실행 검사 통과를 native ARM32 검사로 기록해도 되는가?','아니며 native ARM32 실행은 별도 증거가 필요하다','같은 명령 이름이면 자동으로 모든 target 실행 검사다','원문을 읽고 원리를 설명한 것과 해당 target에서 실제 실행한 것은 다른 증거입니다.')],
  [('전체 파일','세 함수와 include guard,inline·const 속성을 모두 읽고 설명했습니다. 원문 검색으로 해설을 대신하지 않습니다.'),('검증 범위','native ARM32 target 실행은 아직 검사하지 않았습니다. 새 fixture의 assembly 실행 증거는 ARM64에 한정합니다.')])
