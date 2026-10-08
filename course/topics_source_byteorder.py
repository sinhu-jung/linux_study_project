"""Whole endian value/pointer/mutation/array/arithmetic and forwarding headers."""
def register(topic,q,detail):
 def lesson(title,path,symbol,why,principle,use,reading,qa,cards):
  topic(title,'라이브러리·알고리즘',path,symbol,why,principle,use,reading,*(q(*x) for x in qa),details=[detail(*x) for x in cards])
 def le(title,symbol,why,principle,use,reading,qa,cards):
  lesson(title,'include/uapi/linux/byteorder/little_endian.h',symbol,why,principle,use,reading,qa,cards)
 def be(title,symbol,why,principle,use,reading,qa,cards):
  lesson(title,'include/uapi/linux/byteorder/big_endian.h',symbol,why,principle,use,reading,qa,cards)
 def generic(title,symbol,why,principle,use,reading,qa,cards):
  lesson(title,'include/linux/byteorder/generic.h',symbol,why,principle,use,reading,qa,cards)
 le('LE CPU의 형식 변환·같은 순서는 유지하고 반대 순서는 교환','__cpu_to_be32',
  'CPU 내부 값과 외부 바이트 순서를 구분하고 변환이 항상 swap은 아닌 이유를 배웁니다.',
  'little-endian CPU에서 cpu_to_le16/32/64는 같은 순서이므로 폭과 형식 cast를 수행합니다. cpu_to_be16/32/64는 swab으로 byte 순서를 바꿉니다. 0x12345678을 BE32로 만든 저장 값은 이 CPU에서 0x78563412이며 메모리 byte는 12 34 56 78입니다. 읽을 때 be32_to_cpu로 해석하면 다시 숫자 0x12345678입니다.',
  '프로토콜이나 파일의 필드가 LE인지 BE인지 먼저 확인합니다. CPU에서 계산한 값을 해당 저장 형식으로 변환한 뒤 저장하고, 저장된 값을 CPU 형식으로 바꾼 뒤 계산합니다. 이름에 cpu와 목표 형식이 명시된 API를 고릅니다.',
  'LE identity cast와 BE swab, 역방향 함수를 함께 읽으세요.',
  [('LE CPU의 cpu_to_le32는 항상 byte를 뒤집는가?','아니며 같은 순서라 값은 유지한다','모든 형식 변환은 반드시 swap한다','CPU와 저장 형식의 순서가 같으면 byte 교환은 필요 없습니다. 형식과 폭을 맞추는 cast는 남습니다.'),('LE CPU에서 숫자 0x12345678을 BE32로 저장한 메모리 byte는?','12 34 56 78이다','78 56 34 12이다','LE CPU의 수치상 표현을 swap한 뒤 저장하면 외부 BE byte 순서가 됩니다. 숫자 표기와 메모리 byte를 구분합니다.')],
  [('대칭','저장과 읽기 방향의 이름은 역할을 나타냅니다. 현재의 swap은 역변환도 같은 permutation이지만 호출 방향을 바르게 표현합니다.'),('검사','LE 호스트에서 실제 메모리 byte와 독립 shift 기준도 비교했습니다. 단순 round trip만으로 검사를 끝내지 않았습니다.')])
 be('BE CPU의 형식 변환·LE 경로와 역할이 바뀐다','__cpu_to_le32',
  'CPU 순서가 바뀌면 어떤 변환이 identity이고 어떤 변환이 swap인지 직접 계산합니다.',
  'big-endian CPU에서는 cpu_to_be16/32/64가 같은 순서의 cast이고 cpu_to_le16/32/64가 swab입니다. 동일한 외부 BE32 형식이라도 LE CPU는 swap하고 BE CPU는 그대로 저장합니다. API 이름은 외부 형식 계약을 유지하고 구현이 CPU 구성에 따라 바뀝니다. 고정 폭 16·32·64와 machine long 폭을 혼동하면 안 됩니다.',
  '원본 big_endian.h와 little_endian.h를 나란히 읽어 역할 교환을 표시합니다. portable 코드에서는 현재 CPU가 무엇인지 추측해 직접 swap하지 말고 명시된 형식 변환을 사용합니다.',
  'BE identity와 LE swab 및 역방향 cast를 읽으세요.',
  [('BE CPU에서 cpu_to_be32가 선택하는 기본 변환은?','같은 순서의 폭·형식 cast다','반드시 full byteswap이다','목표 BE와 CPU BE가 같으므로 byte 교환이 필요 없습니다. LE CPU의 동작을 모든 CPU에 적용하지 않습니다.'),('LE 호스트에서 BE 헤더 분기를 검사하면 실제 BE CPU 메모리도 검증된 것인가?','아니며 선택된 숫자 변환 경로 검사다','헤더만 바꾸면 실제 CPU byte 순서도 바뀐다','전처리 헤더 선택은 호스트 하드웨어의 메모리 순서를 바꾸지 않습니다. 검증 기록에서 두 범위를 구분합니다.')],
  [('검증 범위','BE 분기는 독립적인 숫자 인코딩 기준으로 확인했습니다. native BE CPU 실행이라고 기록하지 않습니다.'),('같은 형식','외부 형식은 CPU가 달라도 같습니다. CPU가 바뀌면 형식을 만드는 내부 변환이 달라집니다.')])
 le('엔디언 타입 표식·__le와 __be 및 __force','__le32_to_cpu',
  '저장된 정수와 계산용 정수가 같은 비트 폭이어도 다른 의미를 갖는 타입 표식을 배웁니다.',
  '__le16/32/64와 __be16/32/64는 endian 형식의 정수를 표시합니다. __force cast는 Sparse의 restricted 타입 경계를 의도적으로 넘는 표식이며 byte 순서를 바꾸는 기계 명령이 아닙니다. 실제 교환은 swab 식이 담당합니다. 일반 C compiler에서 타입 표식이 약해 보이더라도 저장 값과 CPU 값을 섞어 계산할 수 있다는 뜻은 아닙니다.',
  'struct의 wire 필드는 __be32 같은 형식으로 선언하고 계산 시 be32_to_cpu를 사용합니다. __force로 경고를 억지로 없애기 전에 실제 변환이 필요한지 확인합니다. 타입 경계와 데이터 변환을 각각 읽습니다.',
  '형식 cast와 __force, swab 유무를 구분하세요.',
  [('__force cast 자체가 byte 교환을 실행하는가?','아니며 타입 검사 경계를 넘는 표식이다','반드시 bswap 명령을 실행한다','원문의 데이터 교환은 swab이 담당합니다. 타입 annotation을 runtime 변환으로 설명하지 않습니다.'),('fixture에서 __force를 비워 두면 Sparse 타입 검사까지 증명되는가?','아니며 숫자 변환 검사 범위다','모든 compiler의 restricted 타입 검사가 검증된다','검사 문맥의 타입 alias는 실제 Sparse 진단을 수행하지 않습니다. 증거 범위를 명시합니다.')],
  [('표현','형식 값을 다시 CPU 숫자로 바꾼 뒤 산술합니다. 동일한 unsigned 폭이라도 의미상 계약은 다릅니다.'),('범위','현재 fixture는 고정 폭 alias와 __force의 빈 정의를 사용합니다. Sparse 실행이나 모든 architecture 타입 검사를 대신하지 않습니다.')])
 le('상수 엔디언 변환·compile time 식과 network helpers','__constant_htonl',
  '리터럴 형식 변환과 상수식용 매크로가 선택하는 경로 및 인자 제약을 배웁니다.',
  'LE 헤더의 __constant_htonl/htons는 32/16비트 constant swab을 사용하고 ntohl/ntohs는 같은 permutation을 역방향으로 표현합니다. __constant_cpu_to_leXX는 cast이고 __constant_cpu_to_beXX는 constant swab입니다. BE 헤더에서는 이 역할이 뒤집힙니다. constant swab 식은 인자를 반복하므로 부작용 있는 인자를 넣지 않습니다.',
  '정해진 프로토콜 상수의 표현을 읽고 16/32/64 폭을 확인합니다. x++ 같은 runtime 부작용은 상수 전용 private helper에 전달하지 않습니다. 일반 변환 API와 private 상수식의 평가 계약을 구분합니다.',
  'constant network 네 함수와 constant LE/BE 여섯 쌍을 읽으세요.',
  [('LE CPU의 __constant_htonl(0x12345678) 결과는?','0x78563412다','0x12345678 그대로다','network order는 BE이며 이 CPU에서는 상수 byte 교환이 필요합니다. BE CPU 헤더에서는 같은 값이 유지됩니다.'),('private 상수식에 x++를 넣어도 일반 값 함수처럼 안전한가?','아니며 인자 반복과 평가 순서를 확인해야 한다','상수식은 부작용을 자동으로 제거한다','constant swab 내부에는 같은 인자가 반복됩니다. 부작용 없는 상수 목적에 맞게 사용합니다.')],
  [('폭','htonl의 l은 여기서 고정 32비트입니다. 64비트 unsigned long 전체를 변환하는 이름으로 해석하지 않습니다.'),('확인','16/32/64 constant 변환과 network 리터럴을 두 선택 경로의 독립 기준에 비교했습니다.')])
 le('LE 헤더의 pointer 변환·읽고 값만 돌려준다','__cpu_to_be32p',
  '포인터 변형이 원래 데이터를 변경하는지와 반환값의 형식을 구분해 배웁니다.',
  'LE CPU의 cpu_to_leXXp/leXX_to_cpup는 정렬된 포인터를 역참조하고 cast한 값만 반환합니다. BE 방향의 pointer helper는 swabXXp로 읽은 값을 교환합니다. 모든 폭 16/32/64에서 원래 저장 객체는 바꾸지 않습니다. p는 포인터 인자라는 의미이며 쓰기나 자동 unaligned 처리를 보장하는 이름이 아닙니다.',
  '읽기 전용 형식 필드의 값을 가져와 CPU 숫자로 변환할 때 사용합니다. 포인터가 유효하고 해당 타입의 정렬·수명이 맞는지 확인합니다. 원본을 변경하려면 s 변형의 별도 계약을 읽습니다.',
  'identity 역참조와 BE swabXXp, const pointer 인자를 읽으세요.',
  [('cpu_to_be32p 호출은 원본 u32를 반드시 바꾸는가?','아니며 변환된 반환값만 얻는다','원본을 BE 형식으로 덮어쓴다','p 함수는 읽어서 결과를 반환합니다. 원본을 다시 저장하는 s 함수와 다릅니다.'),('이 pointer helper 이름만으로 임의 비정렬 주소가 안전해지는가?','아니며 실제 역참조·arch 경로를 확인한다','p라는 접미사면 모든 주소를 자동 정렬한다','generic 경로는 typed pointer 역참조를 사용합니다. 비정렬 버퍼는 get_unaligned 계열의 계약을 사용합니다.')],
  [('원본 유지','fixture는 반환 결과와 호출 전후 객체 내용의 불변을 함께 검사했습니다.'),('범위','포인터가 가리키는 객체가 유효한 일반 메모리라는 전제입니다. MMIO나 수명 종료 주소를 검증한 것이 아닙니다.')])
 be('BE 헤더의 pointer 변환·반대쪽 형식만 swab','__cpu_to_le32p',
  '동일한 포인터 API에서도 CPU 구성에 따라 identity와 swab 경로가 바뀜을 배웁니다.',
  'BE CPU의 LE pointer helper는 swabXXp를 사용하고 BE pointer helper는 읽은 값의 cast입니다. __leXX_to_cpup와 __beXX_to_cpup의 입력 타입은 저장 형식을 나타냅니다. 포인터를 다른 폭으로 바꿔 읽는 함수가 아니며 16/32/64 각각의 실제 객체 크기와 정렬이 필요합니다. 결과를 반환하며 원본을 수정하지 않습니다.',
  'big_endian.h의 pointer 함수 12개를 방향별로 묶어 읽습니다. 실제 필드 폭에 맞춘 helper를 고르고 CPU에서 계산할 숫자가 필요하면 to_cpup 방향을 선택합니다.',
  'LE swabXXp와 BE identity 역참조를 읽으세요.',
  [('BE CPU에서 __be32_to_cpup가 하는 기본 동작은?','BE32 객체를 읽어 CPU u32 값으로 cast한다','항상 full byteswap 후 저장한다','CPU와 객체의 byte 순서가 같고 이 API는 반환용 읽기 함수입니다. 원본에 저장하지 않습니다.'),('16비트 helper에 64비트 필드 포인터를 cast하면 전체 필드가 변환되는가?','아니며 선택한 폭의 읽기 계약만 가진다','포인터 주소가 같으면 전체 크기를 알아낸다','helper의 타입과 폭은 고정돼 있습니다. 필드 크기를 무시한 cast는 전체 변환이나 안전성을 보장하지 않습니다.')],
  [('형식','포인터 타입은 해당 저장 표현을 알려 줍니다. 임의 cast로 경계를 지우기보다 올바른 형식을 유지합니다.'),('검사','BE 선택 분기의 16/32/64 pointer 결과와 원본 불변을 비교했습니다. 실제 BE 하드웨어 메모리 검사는 별도입니다.')])
 le('같은 순서의 in-place helper·no-op도 인자는 평가한다','__cpu_to_le32s',
  '변환할 필요가 없을 때의 no-op 매크로와 인자 평가 계약을 정확히 배웁니다.',
  'LE CPU의 cpu_to_leXXs/leXX_to_cpus는 do { (void)(x); } while (0)입니다. 데이터를 읽거나 쓰지 않지만 전달한 x 식은 한 번 평가합니다. BE CPU의 BE 방향도 같습니다. 아무 메모리 접근이 없다는 해당 분기 성질을 모든 구성의 안전성으로 확대하면 안 됩니다. 반대 순서 구성에서는 실제 역참조와 쓰기가 있습니다.',
  'portable 코드에서는 변환 대상의 유효한 writable 객체를 준비합니다. no-op이어도 포인터를 얻는 함수나 증가식의 부작용이 실행되는 것을 이해합니다. 특정 CPU에서 NULL이 접근되지 않았다고 다른 CPU에서도 허용된다고 판단하지 않습니다.',
  '(void)(x)와 do-while 형태 및 반대 구성의 s 경로를 읽으세요.',
  [('같은 순서의 s helper는 전달한 포인터 식의 부작용까지 생략하는가?','아니며 식은 한 번 평가한다','no-op이면 인자 식도 절대 실행하지 않는다','(void)(x)는 결과를 버리지만 식을 평가합니다. 메모리 변환이 없는 것과 평가가 없는 것은 다릅니다.'),('LE no-op에서 NULL 접근이 없었으므로 모든 CPU에서도 NULL을 넣어도 되는가?','아니며 반대 순서에서는 역참조할 수 있다','같은 함수 이름이면 모든 경로가 no-op이다','CPU 구성에 따라 실제 swap과 쓰기로 바뀝니다. portable 호출은 유효한 객체 계약을 지킵니다.')],
  [('확인','fixture에서 해당 no-op 분기에 한해 인자 증가식의 1회 평가와 무역참조를 검사했습니다.'),('구문','do-while은 문장처럼 사용하는 매크로 형태입니다. 다른 코드의 반복 실행이나 동기화를 의미하지 않습니다.')])
 be('반대 순서의 in-place 변환·원본을 읽고 다시 저장','__cpu_to_le32s',
  '값 반환과 원본 변경 API의 차이 및 같은 변환을 두 번 적용하는 결과를 배웁니다.',
  'BE CPU의 LE 방향 s helper는 swab16s/32s/64s입니다. 포인터에서 읽은 값을 byte 교환해 같은 위치에 저장합니다. LE CPU의 BE 방향도 같습니다. 값의 형식이 실제로 변경되므로 이미 변환된 데이터를 다시 변환하면 원래 순서로 돌아갑니다. 읽기·쓰기 묶음은 일반 C 연산이며 원자적 갱신이 아닙니다.',
  '형식이 바뀌는 버퍼 경계를 정하고 변환 완료 여부를 혼동하지 않습니다. 유효하고 정렬된 writable 객체와 필요한 외부 잠금을 준비합니다. const 객체나 MMIO를 일반 메모리처럼 넘기지 않습니다.',
  's alias에서 swabXXs의 읽기와 저장까지 연결하세요.',
  [('반대 순서의 cpu_to_le32s는 값만 반환하고 원본을 보존하는가?','아니며 같은 객체의 내용을 바꾼다','p 변형과 완전히 같은 반환 계약이다','s 변형은 원본을 읽고 변환된 값을 저장합니다. p 변형은 결과 값만 반환합니다.'),('in-place 형식 변환이 자체로 atomic update인가?','아니며 필요한 동기화는 별도로 준비한다','inline이면 CPU에서 반드시 원자적이다','일반 읽기와 쓰기의 조합입니다. inline 표식이 다른 실행 주체와의 원자성이나 잠금을 제공하지 않습니다.')],
  [('두 번 변환','각 폭에서 CPU→형식→CPU 왕복 후 원래 객체로 돌아오는지 검사했습니다.'),('소유권','원본 수정은 객체 수명과 배타적 접근 계약을 요구합니다. swap 자체가 공유 객체 보호를 대신하지 않습니다.')])
 generic('network order API·hton과 ntoh의 방향 및 고정 폭','htonl',
  '네트워크의 big-endian 표현과 host 값 변환을 함수 이름과 실제 alias로 연결합니다.',
  'generic.h는 htonl/htons를 __cpu_to_be32/16, ntohl/ntohs를 __be32/16_to_cpu에 연결합니다. hton은 host에서 network, ntoh는 network에서 host입니다. l은 여기서 32비트이고 s는 16비트이며 64비트 machine long 전체가 아닙니다. 매크로 연결은 상수 folding 경로를 유지하며 기존 이름을 undef한 뒤 정의합니다.',
  '네트워크 헤더 필드를 읽으면 ntoh 또는 beXX_to_cpu로 계산용 값을 얻습니다. 값을 보낼 때 한 번 hton을 적용합니다. 이미 network order인 값을 다시 hton해서 이중 변환하지 않습니다.',
  'undef 네 이름·___hton/ntoh 연결·공개 macro를 읽으세요.',
  [('generic htonl은 어떤 형식으로 바꾸는가?','CPU 값을 BE32 network 형식으로 바꾼다','unsigned long 전체를 현재 메모리 순서로 둔다','원문의 연결은 __cpu_to_be32입니다. 고정 폭 32와 machine unsigned long을 구분합니다.'),('이미 BE32인 값을 다시 host→network 변환하면 언제나 옳은가?','아니며 현재 표현과 변환 방향을 확인한다','같은 helper를 반복하면 자동으로 안전해진다','LE CPU에서는 반복 swap이 원래 표현으로 돌아올 수 있습니다. 각 데이터가 현재 어떤 형식인지 추적해야 합니다.')],
  [('이름','저장 방향과 읽기 방향의 역할을 이름에 드러내면 byte 순서 버그를 줄입니다.'),('검사','두 헤더 선택에서 리터럴 결과, runtime 숫자와 network 왕복을 독립 기준에 비교했습니다.')])
 generic('공개 엔디언 이름의 연결·값 p s 세 API군','le32_add_cpu',
  '수십 개의 alias를 목적별로 묶어 이해하고 원본 구현까지 따라가는 방법을 배웁니다.',
  'generic.h의 cpu_to/le_to/be_to 이름은 선택된 __cpu_to/__to_cpu 구현으로 연결됩니다. 값 API는 변환 결과를 반환하고 p API는 포인터에서 읽은 결과를 반환하며 s API는 원본을 변경합니다. 폭 16/32/64와 두 endian 방향으로 같은 구조가 반복됩니다. 이 alias는 CPU 순서를 실행 중 탐지하지 않으며 포함된 구성 헤더가 구현을 정합니다.',
  'API 이름을 방향·폭·반환 또는 원본 변경으로 나눠 읽습니다. generic 이름에서 실제 UAPI 구현과 asm/swab hook까지 이동해 현재 경로를 확인합니다. 목록의 비슷한 이름 때문에 p와 s의 변경 계약을 혼동하지 않습니다.',
  'generic.h의 36개 공개 alias와 선택된 endian 헤더를 연결하세요.',
  [('p와 s 변형의 가장 중요한 차이는?','p는 읽은 결과를 반환하고 s는 원본을 변경한다','둘 다 반드시 원본을 덮어쓴다','이름 연결만 보지 말고 포인터 getter와 mutator까지 따라가면 반환과 저장 계약이 드러납니다.'),('generic alias가 매 호출마다 CPU endian을 runtime 탐지하는가?','아니며 포함된 구성 구현으로 연결된다','항상 메모리를 읽어 CPU 순서를 추측한다','이 경로는 전처리와 헤더 포함으로 구현을 고릅니다. runtime endian 탐지 코드가 아닙니다.')],
  [('전체 읽기','값·pointer·in-place 각 12개 alias와 network 4개 이름을 읽었습니다. 일반 계산 helper와 구분합니다.'),('구성 경로','Linux little/big wrapper는 각 UAPI 헤더와 generic.h를 포함합니다. architecture의 byteorder 선택을 통해 공개 API로 연결됩니다.')])
 generic('LE 저장 필드 덧셈·decode 계산 encode','le32_add_cpu',
  '외부 형식으로 저장된 숫자를 직접 더하지 않고 세 단계를 거치는 이유를 배웁니다.',
  'le16/32/64_add_cpu는 저장된 LE 값을 CPU 숫자로 변환하고 CPU 형식 val을 더한 뒤 LE로 다시 저장합니다. 예를 들어 BE CPU에서는 저장된 LE 비트 표현에 바로 val을 더하면 숫자 의미가 달라집니다. helper는 val을 이미 CPU 숫자로 받습니다. 일반 읽기·쓰기 연산이며 atomic increment나 overflow 진단을 제공하지 않습니다.',
  'LE 형식의 카운터 필드를 갱신할 때 사용하고 필요한 동기화를 외부에서 준비합니다. val에 이미 cpu_to_leXX를 적용한 값이 아니라 CPU 숫자를 전달합니다. 범위 제한이 필요하면 먼저 별도로 검사합니다.',
  '*var 읽기→leXX_to_cpu→+val→cpu_to_leXX→저장을 읽으세요.',
  [('le32_add_cpu의 val은 어떤 표현이어야 하는가?','CPU 형식 숫자다','이미 LE로 인코딩한 저장 값이다','함수는 저장된 var만 decode하고 val과 계산합니다. val까지 다시 형식 인코딩하면 산술 의미가 어긋날 수 있습니다.'),('le32_add_cpu가 경쟁하는 writer를 자체로 보호하는가?','아니며 동기화가 별도로 필요하다','이름에 add가 있으면 atomic API다','원문은 일반 읽기·계산·저장입니다. 여러 writer의 갱신 손실을 막는 잠금이나 원자적 RMW가 없습니다.')],
  [('세 폭','16/32/64에 같은 원리가 적용됩니다. 현재 CPU와 LE가 같아도 portable 계약은 유지합니다.'),('확인','난수 입력의 decoded modular 합과 다시 인코딩한 결과를 두 선택 경로에서 비교했습니다.')])
 generic('BE 저장 필드 덧셈·network 값의 산술 경계','be32_add_cpu',
  'network 표현의 필드를 갱신할 때 저장 비트 패턴과 숫자를 구분하는 기술을 배웁니다.',
  'be16/32/64_add_cpu는 BE 저장 값을 CPU 숫자로 바꿔 CPU val을 더하고 BE로 저장합니다. LE CPU에서 BE32 숫자1의 수치상 저장 패턴은0x01000000입니다. 이 패턴에 CPU 숫자1을 직접 더한 값은 원하는 BE 숫자2가 아닙니다. 올바른 helper는 decode 후 산술하고 encode합니다.',
  'BE로 정의된 메모리 필드의 숫자를 변경할 때 사용합니다. 계산과 저장 경계를 한 곳에 모아 이중 변환을 피합니다. 이 helper는 checksum이나 네트워크 패킷 전체 갱신 규칙을 대신하지 않으므로 필요한 별도 처리를 확인합니다.',
  'be16/32/64 세 helper의 decode-add-encode를 읽으세요.',
  [('LE CPU에서 BE 저장 패턴에 CPU val을 바로 더하면 올바른 숫자 합인가?','일반적으로 아니며 먼저 decode해야 한다','같은 unsigned 폭이면 항상 옳다','비트 폭이 같아도 표현의 byte 순서가 다릅니다. 숫자로 해석한 뒤 계산해야 합니다.'),('be32_add_cpu가 network checksum도 자동 갱신하는가?','아니며 해당 필드의 형식 덧셈만 수행한다','모든 패킷 검증 값을 알아서 바꾼다','원문에는 필드 decode·합·encode만 있습니다. 다른 프로토콜 규칙은 호출자가 별도로 수행합니다.')],
  [('다른 계약','엔디언 변환과 체크섬 계산은 다른 기술입니다. 이 helper의 이름만으로 다른 필드까지 수정한다고 추측하지 않습니다.'),('대칭','LE add와 BE add는 같은 세 단계이고 선택된 CPU 경로만 달라집니다.')])
 generic('형식 덧셈의 폭·16비트 저장과 modulo wrap','be16_add_cpu',
  '반환 또는 저장 타입이 좁을 때 잘리는 비트와 overflow 검사 부재를 실제 예로 배웁니다.',
  'be16_add_cpu에서 decode한16비트 값과 val은 C 정수 승격을 거쳐 계산될 수 있지만 cpu_to_be16 변환과 최종16비트 저장에서 낮은16비트만 남습니다. 숫자65535에1을 더한 저장 결과는 BE 숫자0입니다. unsigned32/64의 덧셈도 해당 폭에서 modulo 결과를 갖습니다. helper가 범위를 검사하거나 포화시키지는 않습니다.',
  '카운터의 wrap이 의도된 계약인지 먼저 확인합니다. 제한을 넘기면 오류를 반환해야 하는 작업은 저장 전에 별도 범위 검사를 합니다. signed overflow와 이 고정 unsigned 형식의 동작을 혼동하지 않습니다.',
  '16비트 val 타입·덧셈 승격·변환 cast·최종 저장을 읽으세요.',
  [('BE16 숫자65535에 CPU val1을 더한 저장 숫자는?','0으로 wrap한다','자동으로65535에 포화된다','16비트 저장에서 낮은16비트가 남습니다. 이 helper에는 포화나 범위 초과 오류 반환이 없습니다.'),('범위를 넘으면 반드시 실패해야 할 때 add_cpu 하나만 호출하면 되는가?','아니며 별도 범위 검사가 필요하다','helper가 모든 overflow를 자동 진단한다','형식 덧셈은 표현을 올바르게 유지하는 기술입니다. 업무상의 값 범위 검사를 제공하지 않습니다.')],
  [('확인','65535+1의 BE16 wrap 사례와 난수 합의 폭별 modulo 결과를 검사했습니다.'),('일반화 제한','같은 설명을 임의 signed 타입 덧셈의 overflow 허용으로 확대하지 않습니다. 원문의 타입 계약을 지킵니다.')])
 generic('LE32 배열 변환·in-place word 수와 경계','cpu_to_le32_array',
  '배열의 일부를 같은 위치에서 변환하는 반복문과 byte 수가 아닌 원소 수를 배웁니다.',
  'cpu_to_le32_array와 le32_to_cpu_array는 u32 *buf를 받고 words개의 원소에 s helper를 적용하며 buf를 하나씩 증가시킵니다. 원본 배열을 변경하는 API입니다. words는 byte 수가 아니라32비트 원소 수입니다. words0이면 본문이 실행되지 않습니다. 같은 순서 CPU에서는 원소 변환이 no-op이고 반대 순서에서는 각 원소가 swap됩니다.',
  '실제 writable 배열의32비트 원소 개수를 전달합니다. byte 길이에서 원소 수를 구할 때 남는 byte와 정확한 필드 형식을 확인합니다. 배열 밖 접근이나 정렬 오류는 helper가 자동 검사하지 않습니다.',
  'while(words--)·__cpu_to_le32s 또는 __le32_to_cpus·buf++를 읽으세요.',
  [('16byte의 u32 배열 전체를 바꾸려면 words는?','4개 원소다','16개 원소다','이 인자는32비트 원소 수입니다. byte 수를 그대로 전달하면 실제 배열 범위를 넘어갈 수 있습니다.'),('LE32 배열 helper가 별도 dst에 결과를 써 주는가?','아니며 전달한 buf를 같은 위치에서 바꾼다','항상 새 배열을 할당한다','원문은 buf에 s helper를 적용하고 포인터를 증가시킵니다. 할당이나 별도 출력 포인터가 없습니다.')],
  [('검사','0..16개 길이에서 변환·왕복과 배열 뒤의 sentinel 보존을 두 선택 경로에서 비교했습니다.'),('폭','이 generic.h에는32비트 배열 helper가 있습니다. 모든 폭의 동일 이름 함수가 자동 존재한다고 가정하지 않습니다.')])
 generic('BE32 배열 변환·src와 dst를 분리하는 API','cpu_to_be32_array',
  '같은 이름 계열이라도 LE 배열과 BE 배열의 인자·쓰기 계약이 다름을 배웁니다.',
  'cpu_to_be32_array는 __be32 *dst와 const u32 *src, size_t len을 받습니다. 각 src[i]를 변환해 dst[i]에 저장합니다. be32_to_cpu_array는 반대 방향의 typed src/dst입니다. LE 배열 helper와 달리 출력 포인터가 별도로 있습니다. len도 byte가 아니라 원소 수이며 배열 할당·경계 검사·잠금은 수행하지 않습니다.',
  '입력 CPU 배열에서 별도의 BE 출력 버퍼를 준비할 때 사용합니다. src와 dst의 용량이 len개의 원소 이상인지 확인합니다. 이름이 비슷하다고 LE in-place helper와 같은 호출 인자를 기대하지 않습니다.',
  'const src·typed dst·size_t len·정방향 for loop를 읽으세요.',
  [('cpu_to_be32_array의 len은 무엇을 세는가?','32비트 원소 개수다','전체 byte 개수다','반복문은 i로 배열 원소를 인덱싱합니다. byte 길이가 아니라 처리할 원소 수를 전달합니다.'),('BE32 배열 API는 LE32 배열 API와 인자가 완전히 같은가?','아니며 BE 쪽은 src와 dst를 별도로 받는다','둘 다 buf와 words 두 인자뿐이다','원문의 signature가 다릅니다. 비슷한 이름이라도 in-place와 separate-output 계약을 구분합니다.')],
  [('const','src const는 이 helper가 입력을 직접 수정하지 않는 계약입니다. dst와 겹쳐 간접적으로 영향을 줄 가능성까지 제거하는 말은 아닙니다.'),('검사','0..16개 길이에서 별도 출력의 기대 표현과 출력 뒤의 canary, 역방향 결과를 비교했습니다.')])
 generic('BE 배열의 부분 겹침·정방향 loop는 memmove가 아니다','be32_to_cpu_array',
  'src와 dst가 겹칠 때 아직 읽지 않은 원소를 덮어쓰는 실패 원리를 배웁니다.',
  'BE32 배열 helper는 i0부터 증가하며 src[i]를 읽은 직후 dst[i]를 씁니다. dst가 src보다 한 원소 뒤에 겹치면 첫 저장이 다음 입력을 덮어써 이후 변환이 잘못될 수 있습니다. const src는 별칭을 통한 덮어쓰기를 막지 않습니다. 이 loop는 memmove처럼 겹침 방향을 판별하거나 임시 복사하지 않습니다.',
  '별도의 비겹침 출력 버퍼를 사용합니다. 부분 겹침이 필요하다면 명시된 상위 API 계약과 복사 전략을 검토합니다. 현재 동작에서 같은 주소 변환이 가능해 보이는 것과 일반적인 모든 겹침 허용을 구분합니다.',
  'src[i] 읽기 뒤 dst[i] 쓰기와 i 증가 순서를 그려 보세요.',
  [('dst=src+1인 겹침을 항상 안전하게 처리하는가?','아니며 다음에 읽을 원소를 먼저 덮어쓸 수 있다','const src라서 겹침이 자동으로 안전하다','정방향 저장이 미래의 src 위치와 겹칠 수 있습니다. const는 alias를 통한 저장을 자동 방지하지 않습니다.'),('이 함수는 겹침에 따라 복사 방향을 자동으로 선택하는가?','아니며 항상 정방향 loop다','memmove 구현을 자동으로 호출한다','원문은 단순 i 증가 반복입니다. 방향 선택이나 임시 버퍼를 제공하지 않습니다.')],
  [('읽기 조건','source와 destination의 용량뿐 아니라 별칭 관계도 검토합니다. array helper 이름만으로 memmove 계약을 붙이지 않습니다.'),('증거','이 위험은 원본 for loop의 읽기·쓰기 순서에서 직접 도출합니다. 비겹침 fixture 통과가 겹침 허용 증거는 아닙니다.')])
 generic('엔디언 wrapper 포함 경로·CPU 구성 불일치 경고','le32_add_cpu',
  '짧은 forwarding 헤더도 빌드 구성과 공개 API를 연결하는 역할이 있음을 배웁니다.',
  'include/linux/byteorder/little_endian.h는 UAPI little_endian.h와 generic.h를 포함하고 CONFIG_CPU_BIG_ENDIAN이 정의돼 있으면 warning을 냅니다. big_endian.h는 같은 방식의 BE 포함과 설정 부재 warning입니다. #ifdef/#ifndef는 값이 아니라 정의 여부를 검사합니다. 이 파일들은 runtime CPU 감지나 값 변환을 직접 실행하는 함수가 아닙니다.',
  'architecture byteorder 포함 경로와 CONFIG_CPU_BIG_ENDIAN 설정을 함께 확인합니다. 불일치 warning을 무시하고 임의로 두 endian 헤더를 모두 포함하지 않습니다. 공개 helper의 선택이 어떤 빌드 구성에서 온 것인지 추적합니다.',
  '두 Linux wrapper의 전체12줄, UAPI include와 generic include 및 설정 warning을 읽으세요.',
  [('LE wrapper에서 CONFIG_CPU_BIG_ENDIAN을0으로 정의하면 #ifdef는 거짓인가?','아니며 정의돼 있으므로 warning 조건이 참이다','값0이면 #ifdef도 항상 거짓이다','전처리 #ifdef는 매크로의 존재를 검사합니다. 일반 #if 식의 숫자 평가와 다릅니다.'),('짧은 wrapper의 역할은?','선택한 UAPI 구현과 공개 generic API를 연결하고 구성 불일치를 경고한다','매 호출마다 CPU를 측정해 endian을 바꾼다','실제 파일은 include와 조건부 warning으로 구성됩니다. runtime 탐지 함수가 아닙니다.')],
  [('포함 경로','LE: Linux wrapper → UAPI LE + generic. BE: Linux wrapper → UAPI BE + generic. 두 전체 파일의 guard와 warning을 읽었습니다.'),('검사 범위','fixture는 두 UAPI 선택과 generic 계산을 검증했습니다. 모든 architecture의 include 구성 빌드를 수행한 것은 아닙니다.')])
 generic('pointer 변환과 비정렬·오래된 주석보다 실제 경로 확인','le32_to_cpu_array',
  '역사적 설명을 현재 구현 계약과 대조하고 안전한 비정렬 접근 API를 고르는 방법을 배웁니다.',
  'generic.h 앞부분에는 오래된 pointer 변환과 비정렬 관련 설명이 있으며 get_unaligned 사용을 안내합니다. 현재 UAPI의 p helper는 typed pointer를 직접 역참조하거나 swabXXp를 호출합니다. generic swabXXp도 typed 읽기이므로 arbitrary 비정렬 주소의 portable 안전성을 그 주석 한 문장만으로 보장할 수 없습니다. byte 순서와 정렬 조건은 서로 다른 문제입니다.',
  '네트워크 byte 버퍼의 임의 offset은 get_unaligned_leXX/beXX 같은 정렬과 형식 계약에 맞는 helper를 사용합니다. pointer API의 실제 arch override가 무엇인지 확인합니다. 읽은 숫자의 endian 변환과 주소 정렬을 각각 검토합니다.',
  'generic.h 역사 주석과 UAPI p 함수, swab p 함수, get_unaligned 경로를 대조하세요.',
  [('endian 변환을 수행하면 주소 정렬 문제도 자동으로 해결되는가?','아니며 별도의 접근 계약이다','byte 순서만 맞으면 모든 역참조가 안전하다','주소 정렬과 숫자 표현은 다른 조건입니다. 실제 typed 역참조 경로와 접근 API를 확인해야 합니다.'),('역사 주석만으로 현재 모든 arch의 비정렬 pointer 안전성을 확정하는가?','아니며 현재 구현과 arch hook을 대조한다','같은 주석이 있으면 모든 CPU에서 증명된다','현재 경로와 실제 검증 범위를 읽어야 합니다. 문서의 역사적 설명을 현재의 일반 안전 보장으로 확대하지 않습니다.')],
  [('기술 연결','unaligned 수업은 주소 접근, byteorder 수업은 값 표현을 다룹니다. 두 조건이 함께 필요한 버퍼에서는 결합된 helper를 고릅니다.'),('확인','fixture의 pointer 입력은 유효하고 정렬된 객체입니다. 비정렬 typed 역참조의 안전성을 실험으로 주장하지 않습니다.')])
