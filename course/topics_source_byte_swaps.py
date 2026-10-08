"""Full swab/UAPI value/pointer/in-place/array APIs and compiler selection."""
def register(topic,q,detail):
 def lesson(title,path,symbol,why,principle,use,reading,qa,cards):
  topic(title,'라이브러리·알고리즘',path,symbol,why,principle,use,reading,*(q(*x) for x in qa),details=[detail(*x) for x in cards])
 def uapi(title,symbol,why,principle,use,reading,qa,cards):
  lesson(title,'include/uapi/linux/swab.h',symbol,why,principle,use,reading,qa,cards)
 uapi('16비트 byte 교환·mask와 위치 이동','___constant_swab16',
  '정수의 두 byte 위치를 서로 바꾸는 원리와 고정 폭 cast의 역할을 배웁니다.',
  '___constant_swab16은 낮은byte를0x00ff mask로 골라8칸 올리고 높은byte를0xff00으로 골라8칸 내려 OR합니다. 입력과 결과를 __u16으로 cast해16비트 값을 다룹니다.0x1234는0x3412입니다. 이 연산은16개의 bit를 하나씩 거꾸로 하는 bit reversal이 아니라 byte 두 개의 위치를 바꿉니다.',
  '외부 표현 변환의 기본 산술을 읽고 byte 위치를 그립니다. 입력 부호·폭 변환을 확인합니다. raw byteswap과 CPU 순서에 따라 변환을 선택하는 endian helper의 정책은 구분합니다.',
  '두 mask·shift·최종16비트 cast를 읽으세요.',
  [('16비트0x1234의 byteswap은?','0x3412다','0x4321이다','byte12와34의 위치를 바꿉니다. 각16진 digit이나 각bit를 뒤집는 연산이 아닙니다.'),('이 연산이 각 byte 내부의 bit 순서도 뒤집는가?','아니며 byte 내부 bit 배열은 유지한다','모든16bit를 순서대로 반전한다','mask와8칸 이동은 byte 단위 위치 변경입니다. bit reversal과 다른 알고리즘입니다.')],
  [('폭','상수의 U/UL/ULL과 고정 __u16/__u32/__u64 매핑을 가정하지 않도록 원문은 cast 필요성을 설명합니다.'),('확인','모든16비트 값65536개를 독립 byte 분리 기준과 비교했습니다.')])
 uapi('32비트 byte 교환·네 mask의 합성','___constant_swab32',
  '네 byte의 양끝과 가운데를 서로 이동시켜 전체 순서를 반대로 만드는 식을 배웁니다.',
  '___constant_swab32는 네byte를 각각 mask해24·8칸 올리거나8·24칸 내린 뒤 OR합니다. unsigned32 cast로 연산 폭을 맞춥니다.0x12345678은0x78563412입니다. 각각의byte 내용은 유지되고 다른 위치로 갑니다. 결과를 두 번 byteswap하면 원래 값이 되는 involution입니다.',
  '필드 위치를 byte0..3으로 나눠 이동 표를 만듭니다. byte 숫자 순서 변경과16비트 word 교환을 구분합니다. 조건 없이 swap하는 primitive를 모든 endian 변환에 무조건 적용하지 않습니다.',
  '네 mask·shift 방향·unsigned32 cast를 읽으세요.',
  [('32비트0x12345678의 full byteswap은?','0x78563412다','0x56781234다','네byte 순서를 완전히 뒤집습니다.16비트 절반 둘만 교환하는 결과와 다릅니다.'),('같은 폭 full byteswap을 두 번 하면?','원래 값으로 돌아온다','모든 값이0이 된다','각byte가 반대 위치로 갔다가 다시 돌아옵니다. 실제 난수 입력에서도 이 성질을 검사했습니다.')],
  [('unsigned','큰 left shift의 중간 타입도 unsigned32로 맞춥니다. 반환형만 넓다고 중간 식이 자동 안전해지는 것은 아닙니다.'),('참조','검사는 mask 식을 복사하지 않고 byte를 나눠 반대 순서로 다시 조립한 독립 기준을 사용했습니다.')])
 uapi('64비트 byte 교환·넓은 상수와8개 이동','___constant_swab64',
  '64비트 표현의 여덟 byte를 교환할 때 큰 mask·shift의 타입 폭을 유지하는 기술을 배웁니다.',
  '___constant_swab64는 __u64로 cast한 값에서 여덟byte를 분리해56·40·24·8칸 이동합니다. 예를 들어0x0123456789abcdef는0xefcdab8967452301입니다. 큰 상수에는 ULL 표기를 쓰고 __u64 cast로 고정 폭을 명시합니다. 폭이 넓다고64개bit의 순서를 하나씩 역전하는 연산은 아닙니다.',
  '입력 폭과 출력 byte열을 대응시킵니다.32비트 부분만 swap하고 나머지를 무시하는 계산과 구분합니다. 같은 API의 runtime fallback이64비트를32비트 조각으로 나눌 수 있다는 다음 수업을 연결합니다.',
  '여덟 mask·56/40/24/8 shift 및 __u64 cast를 읽으세요.',
  [('0x0123456789abcdef의64비트 byteswap은?','0xefcdab8967452301이다','0x89abcdef01234567이다','byte 여덟 개의 순서를 반대로 만듭니다.32비트 절반만 교환하는 연산과 다릅니다.'),('56칸 이동을 수행할 때 중간 값 타입은 왜 중요한가?','이동 당시 충분한 unsigned 폭이 필요해서다','최종 반환형이64면 모든 작은 타입 shift도 자동 안전해서다','연산은 당시 타입의 규칙으로 실행됩니다. 원문은 고정 __u64 cast와 넓은 상수로 폭을 맞춥니다.')],
  [('고정 폭','cast는 ULL의 표기 폭과 __u64 타입 매핑을 구분하는 원문 의도입니다.'),('확인','10만64비트 입력의 full swap·double swap·pointer 및 in-place 형태를 각각 비교했습니다.')])
 uapi('compiler builtin과 상수 folding·arch fallback 선택','__swab32',
  '같은 공개 API가 compiler 기능·상수 여부·아키텍처 hook에 따라 다른 구현을 선택하는 과정을 배웁니다.',
  '__HAVE_BUILTIN_BSWAP16/32/64가 정의되면 공개 __swab 함수 매크로는 builtin을 사용합니다. 없으면 __builtin_constant_p로 상수식을 고르고 비상수 값은 __fswab inline 함수에 전달합니다. __fswab는 arch hook이 있으면 이를,없으면 generic mask를 사용합니다. 값 함수의 __attribute_const__는 결과가 인자에 의존하는 compiler 속성이며 포인터 데이터 불변성 선언이 아닙니다.',
  '현재 compiler 기능 매크로와 asm/swab.h의 실제 hook을 확인합니다. generic 원문 계산과 compiler가 고른 machine instruction을 구분합니다. 상수 folding 확인을 모든 architecture 구현의 동치 증명으로 계산하지 않습니다.',
  '공개 builtin 분기·constant_p·__fswab32의 arch/generic 분기를 읽으세요.',
  [('builtin 기능 매크로가 정의됐을 때 공개 __swab32 경로는?','compiler의 bswap builtin이다','항상runtime 비트별 loop다','전처리 분기가 builtin을 선택합니다. 같은 호출 문법도 compiler 기능에 따라 실행 표현이 달라질 수 있습니다.'),('generic 검사 통과가 읽지 않은 모든 arch hook도 증명하는가?','아니며 실제 arch 구현은 별도 검토해야 한다','같은 함수 이름이면 모든 기계어가 자동 증명된다','원문 선택 조건과 실제 검증 경로를 구분합니다. 현재 fixture는 arch override를 제공하지 않았습니다.')],
  [('상수 여부','constant_p는 optimizer가 판단하는 상수 가능성 문맥입니다. C11 정수 상수식의 언어 조건과 동일한 개념으로 취급하지 않습니다.'),('구성','builtin on/off·64 split on/off·word32/64 선택을 각각 실제 전처리 구성으로 검사했습니다. word32는 long64 호스트의 조건 경로입니다.')])
 uapi('64비트 fallback 분할·32비트 둘을 swap 후 교환','__fswab64',
  '넓은 swap을 작은 연산 둘과 위치 교환으로 구현하는 원리와 cast의 위치를 배웁니다.',
  '__SWAB_64_THRU_32__이면 val의 높은32비트 h와 낮은32비트 l을 얻습니다. swap32(l)을 u64로 올린 뒤32칸 shift해 새 상위 절반으로 놓고 swap32(h)를 하위로 OR합니다.각 절반 안의 byte를 반대로 하고 절반 위치도 바꿔 전체8byte가 반대 순서가 됩니다. arch_swab64가 있으면 이 fallback보다 먼저 선택됩니다.',
  '0x1122334455667788을 h11223344,l55667788로 나눈 뒤 결과8877665544332211을 계산합니다.32비트 값을 그대로32칸 shift하지 않고 shift 전에 u64로 확장하는 이유를 확인합니다.',
  'arch 우선 분기·h/l 추출·swap 후 u64 cast·32칸 이동을 읽으세요.',
  [('분할64 swap에서 원래 낮은32비트는 어디로 가는가?','byte swap된 뒤 새 상위32비트가 된다','그대로 하위32비트에 남는다','각 절반의 byte 교환과 두 절반의 위치 교환을 모두 해야 full64 reversal이 됩니다.'),('swap32(l)을32칸 옮기기 전에 필요한 타입은?','u64로 확장한 값이다','그대로u32면 항상 안전하다','32비트 타입의32칸 shift는 폭 밖입니다. 원문은 넓게 cast한 뒤 이동합니다.')],
  [('대체 구현','generic64 mask 경로와 split32 경로를 같은 독립 reference에 대조했습니다.'),('범위','선택된 C fallback 검사의 증거입니다. CPU의 arch assembly 구현을 실행해 비교한 것은 아닙니다.')])
 uapi('machine word swap·조건부 word32와 word64','__swab',
  'unsigned long API가 word 폭에 따라 다른 고정 폭 helper를 선택하는 구조를 배웁니다.',
  '__swab은 unsigned long y를 받아 __BITS_PER_LONG64이면 __swab64,그 외32 분기에서는 __swab32를 사용합니다. kernel swab 이름은 이 함수로 alias됩니다. 일반 full64 swap과 항상 같은 API가 아니며 word32에서는32비트에 해당하는 변환입니다. 저장소 ABI 폭과 조건 매크로를 맞춰 읽어야 합니다.',
  'machine word 값을 바꾸려는 코드에서 사용하는 타입·구성을 확인합니다. protocol의 고정64비트 값은 swab64처럼 정확한 폭 API를 사용합니다. 플랫폼마다 동일64출력을 요구하는 저장 형식에 word alias를 무조건 쓰지 않습니다.',
  'unsigned long 인자·__BITS_PER_LONG 분기·kernel alias를 읽으세요.',
  [('word32 구성의 swab은 어느 고정 폭 변환을 쓰는가?','32비트 swap이다','항상64비트 swap이다','원문은 word 폭에 따른 두 경로를 제공합니다. 함수 이름만으로 고정64비트 계약을 추측하지 않습니다.'),('조건부 word32 fixture가 실제 native32 ABI를 실행한 것인가?','아니며 long64 호스트의 해당 선택 경로다','매크로 하나만 정의하면 host ABI도32비트가 된다','전처리 선택과 실제 compiler 데이터 ABI는 구분합니다. 기록한 검증 범위를 유지합니다.')],
  [('형식','외부 필드 폭이32/64로 고정이면 해당 명시 API와 자료형을 선택합니다.'),('검사','word64는 전체64 reversal,조건부 word32는 낮은32비트 reversal 기준으로 비교했습니다.')])
 uapi('swahw32·16비트 절반 교환','___constant_swahw32',
  '전체 byte reversal과32비트 값의 두16비트 절반만 바꾸는 기술을 구분해 배웁니다.',
  '___constant_swahw32는 낮은16비트를16칸 올리고 높은16비트를16칸 내려 OR합니다.0x12345678은0x56781234입니다. 각 절반 안의byte 순서는 유지합니다. 여기서 word swap은16비트 절반 두 개의 교환이며 machine unsigned long 폭과 같은 뜻이라고 가정하면 안 됩니다. 공개 macro는 상수/runtime,inline은 arch/generic을 선택합니다.',
  '특수 자료 표현이16비트 절반 교환을 요구할 때 full swab32와 구분해 사용합니다. 이름만 보고 모든 byte를 반대로 바꾼다고 설명하지 않습니다. 실제 포맷이 필요한 permutation을 확인합니다.',
  '0x0000ffff/0xffff0000 mask와16칸 이동·공개 __swahw32를 읽으세요.',
  [('swahw32의0x12345678 결과는?','0x56781234다','0x78563412다','16비트 절반을 교환하고 각각 안의byte 순서는 유지합니다. full byteswap과 다릅니다.'),('여기서 word 교환이 항상 unsigned long 교환을 뜻하는가?','아니며 이 함수는32비트의16비트 절반을 바꾼다','machine word 폭이 자동으로 입력 크기를 결정한다','원문의 mask와 shift가 실제 구간을 명시합니다. 용어만으로 폭을 추측하지 않습니다.')],
  [('성질','절반 교환을 두 번 하면 원래 값입니다. 내부byte 교환과 조합하면 full32 swap이 됩니다.'),('선택','__fswahw32와 상수 macro·pointer/in-place 변형도 같은 permutation을 제공하는 계약으로 읽습니다.')])
 uapi('swahb32·각16비트 안의 byte 교환','___constant_swahb32',
  '32비트 전체 절반 위치는 두고 각16비트 안의 높은·낮은byte만 바꾸는 permutation을 배웁니다.',
  '___constant_swahb32는0x00ff00ff로 고른 두byte를8칸 올리고0xff00ff00로 고른 두byte를8칸 내려 OR합니다.0x12345678은0x34127856입니다.16비트 절반의 위치는 바꾸지 않습니다. swahw32와 이 변환을 합치면 전체 byte reversal이며 둘은 서로 다른 단계입니다.',
  '두 절반 안의byte를 바꾸는 저장 형식을 읽을 때 사용합니다. 필요한 변환이 full byteswap인지 halfword swap인지 halfword 내부byte swap인지 실제 byte 배열로 확인합니다.',
  '교차 byte mask와8칸 이동·__swahb32 선택 경로를 읽으세요.',
  [('swahb32의0x12345678 결과는?','0x34127856다','0x56781234다','각16비트 안에서12↔34,56↔78을 바꾸고 두 절반의 위치는 유지합니다.'),('swahw32와 swahb32를 조합하면?','full swab32와 같은byte 순서가 된다','모든bit가0이 된다','절반 안의byte를 바꾸고 절반 위치도 바꾸면 네byte 전체가 반대로 됩니다. 실제 조합을 reference와 비교했습니다.')],
  [('성질','이 변환도 두 번이면 원래 값입니다. 단순 값 inversion(~x)과 다릅니다.'),('폭','결과는 u32이며16비트 범위의 연산을 두 구간에 동시에 적용합니다.')])
 uapi('pointer swap 읽기·자연 정렬은 그대로 필요','__swab32p',
  'typed 포인터에서 값을 읽고 교환해 반환하는 API와 비정렬 접근 helper의 계약 차이를 배웁니다.',
  '__swab16p/32p/64p는 arch pointer hook이 없으면 *p를 읽고 scalar swap합니다. __swahw32p/__swahb32p도 같은 구조입니다. 이름의 p는 포인터 읽기이며 저장된 원본을 바꾸지 않습니다. 원문은 naturally aligned 값을 요구하므로 임의 byte buffer를 cast한 misaligned 포인터에 쓸 수 있다고 가정하면 안 됩니다.',
  '정확한 타입과 자연 정렬·유효 범위가 있는 포인터에서 사용합니다. 비정렬 외부buffer에는 get_unaligned 계열로 읽고 필요한 값 변환을 적용합니다. const 인자와 실제 객체 수명은 별도로 지킵니다.',
  'p helper의 const typed 인자·*p 읽기·scalar 반환 및 alignment 주석을 읽으세요.',
  [('swab32p가 원래*p도 교환해 저장하는가?','아니며 변환값을 반환하고 원본은 유지한다','언제나 읽은 위치에 다시 쓴다','p 변형은 getter입니다. in-place s 변형의 대입과 구분합니다.'),('p helper가 임의 misaligned byte buffer 접근을 보장하는가?','아니며 자연 정렬 계약이 있다','이름에 pointer가 있으면 alignment를 자동 처리한다','원문 주석은 자연 정렬 포인터를 요구합니다. packed unaligned helper와 다른 전제입니다.')],
  [('전체 변형','16/32/64 full swap과 두32비트 부분 교환의 p 변형을 각각 확인했습니다.'),('arch','pointer 전용 hook이 있으면 그 경로를 선택합니다. 현재 검사는 generic dereference 경로입니다.')])
 uapi('in place swap·읽고 같은 위치에 다시 저장','__swab32s',
  '원본 정수를 교환 결과로 바꾸는 s API의 동작과 공유 read-modify-write의 한계를 배웁니다.',
  '__swab16s/32s/64s는 arch store hook이 없으면 *p=__swabXp(p)를 수행합니다. __swahw32s/__swahb32s도 부분 permutation 결과를 같은 위치에 씁니다. 반환형 void이며 원본이 변경됩니다. 자연 정렬·쓰기 가능한 유효 메모리가 필요하고 일반 read-modify-write의 원자성이나 MMIO ordering을 추가하지 않습니다.',
  '소유한 aligned 자료를 실제로 변환할 때 사용합니다. shared 값은 상위 동기화 계약을 지키고 getter p와 mutator s를 혼동하지 않습니다. readonly 자료를 강제 cast해 쓰는 용도로 사용하지 않습니다.',
  's 함수의 writable 인자·p helper·최종 대입을 읽으세요.',
  [('swab32s 호출 뒤 원본 저장 값은?','byte 교환 결과로 바뀐다','원래 값이 그대로고 결과만 반환된다','s 변형은 void 반환과 메모리 대입입니다. p getter와 부작용이 다릅니다.'),('s 변형의 한 줄 대입이 공유 갱신 원자성을 보장하는가?','아니며 별도 동기화가 필요하다','compiler가 모든 CPU를 자동 잠근다','일반 메모리 read-modify-write 표현입니다. 값 permutation과 경쟁 제어는 별도 기술입니다.')],
  [('전체 변형','다섯 s API를 값 기준과 비교하고16비트는 두 번 적용해 원래 값으로 돌아오는지 전체 입력에서 확인했습니다.'),('hook','전용 arch s 함수가 없으면 p helper와 대입으로 구현됩니다. 실제 모든 arch의 store instruction 증거는 아닙니다.')])
 lesson('swap 배열 helper·words는 byte 수가 아니다','include/linux/swab.h','swab32_array',
  '연속 정수 배열의 각 원소를 in-place 교환하는 loop와 길이 인자 단위를 배웁니다.',
  'swab16_array/32_array/64_array는 while(words--)에서 s helper를 호출하고 typed buf를 한 원소씩 증가시킵니다. words는 원소 수이며 byte 길이가 아닙니다. swab32_array(buf,4)는 네u32,총16byte를 바꿉니다.0개면 본문이 없고 실제 배열 범위는 caller가 보장합니다. kernel 헤더의 scalar/p/s 이름은 UAPI 구현으로 alias됩니다.',
  '정렬된 writable 배열의 원소 수를 전달합니다. packet의 byte 길이를 그대로 words에 넣으면 범위를 넘길 수 있으므로 타입·단위를 맞춥니다. array helper가 저장소를 할당하거나 범위 검사를 하는 기능은 없습니다.',
  '세 loop의 typed pointer 증가·words 조건과 위 alias 목록을 읽으세요.',
  [('swab32_array(buf,4)가 바꾸는 길이는?','u32 네 개,16byte다','항상4byte다','words는 데이터 원소 수입니다. 인자의 단위를 이해해야 실제 접근 범위를 계산할 수 있습니다.'),('words0에서 배열 원소를 하나라도 쓰는가?','아니며 loop 본문을 실행하지 않는다','post-decrement라 마지막 원소 하나는 바꾼다','조건의 이전 값0이 거짓이므로 본문은 없습니다. 지역 unsigned 감소와 메모리 작업 여부를 구분합니다.')],
  [('전달 이름','kernel의 swab16/32/64·swab·swahw32/swahb32·다섯p·다섯s는 UAPI helper로 연결됩니다. 별도 변환 알고리즘이 중복 정의되는 것은 아닙니다.'),('검사','0..16 원소의 세 폭 배열을 독립 기대값과 전체 canary 비교로 확인했습니다.')])
 uapi('상수 전용 식과 부작용·반복 인자 주의','___constant_swab16',
  '큰 macro가 인자를 여러 번 사용하는 것과 공개 API의 상수/runtime 선택 계약을 구분해 배웁니다.',
  '___constant_swab 계열의 mask 식은 x를 여러 번 사용합니다. x++처럼 부작용이 있는 인자를 직접 넣으면 같은 식의 여러 변경이 비순차로 나타나 C의 유효 동작이 아닐 수 있습니다. 공개 __swab는 builtin 또는 constant_p/runtime 선택을 사용합니다. 순수 상수 식과 일반 값을 다루는 public API를 구분하고 private 이름을 무조건 같은 평가 계약으로 사용하지 않습니다.',
  '상수 helper에는 안정된 상수 표현식을,일반 값에는 공개 swab 함수를 사용합니다. 가능하면 부작용을 별도 문장에 두어 값과 변환을 명확하게 만듭니다. compiler의 scalar const 속성은 변수 readonly 표식과 다른 기술입니다.',
  '같은x가 반복되는 상수 식과 공개 선택·값 inline을 비교하세요.',
  [('private constant macro에 x++를 직접 넣는 것이 안전한가?','아니며 여러 비순차 변경으로 유효하지 않을 수 있다','모든 macro가 인자를 자동 한 번만 실행한다','식의 인자 반복과 C 평가 순서를 확인해야 합니다. 상수 helper의 사용 목적을 지킵니다.'),('일반 값 변환과 private 상수식이 동일한 인자 평가 계약이라고 추측하는가?','아니며 공개 API와 실제 구현을 구분한다','같은 계산 결과 이름이면 모든 부작용도 같다','기능이 비슷해도 macro·inline·builtin의 평가 조건은 다릅니다. 부작용 없는 값을 명확히 전달합니다.')],
  [('진단','private16 macro의 x++ 사례는 -Werror=sequence-point에서 거절됐습니다. 공개 swab32(count++) 사례는1회 증가와 예상 결과를 확인했습니다.'),('전체 결과','각 구성1,162,164개 비교를 builtin on/off·64split on/off·word32/64의8구성 각각 최적화·ASan/UBSan에서 확인했습니다. arch override·native32 ABI·원자성·MMIO 검증은 아닙니다.')])
