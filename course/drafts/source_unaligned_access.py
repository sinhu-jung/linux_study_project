"""Complete unaligned, packed-struct and VDSO typed access headers."""
def register(topic,q,detail):
 def lesson(title,path,symbol,why,principle,use,reading,qa,cards):
  topic(title,'라이브러리·알고리즘',path,symbol,why,principle,use,reading,*(q(*x) for x in qa),details=[detail(*x) for x in cards])
 def main(title,symbol,why,principle,use,reading,qa,cards):
  lesson(title,'include/linux/unaligned.h',symbol,why,principle,use,reading,qa,cards)
 lesson('비정렬 접근·packed 멤버의 정렬 정보','include/vdso/unaligned.h','__get_unaligned_t',
  '정수 주소가 자연 정렬 경계에 있지 않은 byte buffer에서 compiler에 접근 형태를 알리는 원리를 배웁니다.',
  '__get_unaligned_t는 한 개 type x를 담은 익명 __packed 구조체 포인터로 ptr를 변환해 x를 읽습니다. packed 타입은 compiler에 낮은 정렬 제약을 알리므로 임의 정수 포인터를 직접 역참조하는 코드와 다릅니다. 실제 instruction 선택은 compiler와 CPU에 달려 있습니다. packed는 버퍼 길이·유효 주소·동시 갱신·객체 수명을 검사하지 않습니다.',
  '파일 header처럼 정렬되지 않을 수 있는 유효 byte 구간에서 적절한 타입 helper를 사용합니다. 읽을 폭만큼 메모리가 실제로 있어야 합니다. 단순한 cast만으로 모든 CPU·C 언어 문맥에서 동일한 접근 계약을 얻는다고 가정하지 않습니다.',
  '익명 packed 구조체·const pointer·멤버 읽기를 확인하세요.',
  [('packed helper가 compiler에 주는 정보는?','멤버 접근의 정렬 제약이다','포인터 주소가 항상 유효하다는 증명이다','정렬 형태를 표현합니다. 범위·매핑·수명·동시 접근의 유효성은 별도입니다.'),('packed를 쓰면 compiler가 모든 CPU에서 같은 instruction을 내는가?','아니며 CPU와 compiler에 따라 접근 코드가 달라질 수 있다','언제나 동일64비트 load만 사용한다','접근의 의미와 정렬 계약을 표현하지만 구체적인 기계어는 target에 따라 결정됩니다.')],
  [('실제 검사','GCC의 실제 packed 타입으로0..15 offset의 접근을 확인했습니다. host는 little-endian이며 모든 CPU 실행 증명은 아닙니다.'),('단위','유형 폭과 buffer 안 남은 byte 수를 맞춥니다. 정렬을 처리한다는 말은 경계 밖 읽기를 허용한다는 뜻이 아닙니다.')])
 lesson('CPU 순서 비정렬 읽기·16·32·64비트 구조체','include/linux/unaligned/packed_struct.h','__get_unaligned_cpu16',
  '고정 폭 packed 구조체로 데이터를 CPU의 native 정수로 읽는 helper와 외부 포맷 순서 변환을 구분해 배웁니다.',
  '__una_u16/u32/u64는 각각 정수 x 하나를 담은 packed 구조체입니다. __get_unaligned_cpu16/32/64는 해당 타입 포인터로 변환해 x를 반환합니다. 정렬 처리만 있으며 le_to_cpu나 be_to_cpu 변환은 없습니다. 같은 byte열이 다른 endian CPU에서는 다른 native 숫자일 수 있습니다.',
  'native 표현의 정수를 다루는 유효 buffer에서 폭에 맞춰 사용합니다. 외부 파일이나 network의 명시된 순서라면 별도 LE/BE helper를 사용합니다. 저장 순서 규약과 CPU 순서를 혼동하지 않습니다.',
  '세 packed 타입과 세 CPU getter의 동일 구조·변환 없는 반환을 읽으세요.',
  [('CPU getter가 little-endian 파일값을 모든 CPU에서 자동 변환하는가?','아니며 CPU native 읽기이고 별도 순서 변환이 없다','이름의 cpu가 모든 외부 순서를 자동 판별한다','정렬 처리는 있지만 endian 변환 함수는 없습니다. 외부 포맷 순서에 맞는 helper가 필요합니다.'),('16·32·64 getter가 읽는 byte 수는?','각각2·4·8byte다','모두 포인터 크기만큼이다','읽는 필드 형식은 u16/u32/u64입니다. 포인터 주소의 크기와 데이터 접근 폭을 구분합니다.')],
  [('표현 예','little-endian host에서 byte01,02의 native u16은0x0201입니다. BE 명시 포맷의0x0102와 구분합니다.'),('확인','실제 __una 타입의 alignment1과 CPU getter 세 개를 독립 byte 계산으로 비교했습니다.')])
 lesson('CPU 순서 비정렬 쓰기·필드 대입의 경계','include/linux/unaligned/packed_struct.h','__put_unaligned_cpu16',
  'packed 타입의 멤버 대입으로 native 폭 값을 저장하는 방법과 atomic·MMIO 계약의 차이를 배웁니다.',
  '__put_unaligned_cpu16/32/64는 packed 구조체 포인터의 x에 값을 대입합니다. 값의 native byte 표현을2·4·8byte에 씁니다. endian 변환과 잠금·원자적 공유 갱신·장치 accessor 기능은 없습니다. 특히 misaligned 접근이 여러 작은 instruction으로 나뉠 수 있어 단일 C 대입을 하드웨어 원자성 증명으로 볼 수 없습니다.',
  '쓰기 가능한 유효 메모리에 폭만큼의 공간을 준비합니다. 일반 byte buffer 저장과 장치 register의 read/write 부작용·ordering·accessor 규약을 구분합니다. concurrent 데이터에는 별도 동기화를 유지합니다.',
  '세 CPU put helper의 x=val 대입과 폭을 읽으세요.',
  [('CPU put helper가 장치 MMIO의 접근 규칙을 자동 제공하는가?','아니며 일반 메모리 helper와 장치 accessor 계약은 다르다','포인터가 장치를 가리키면 규칙을 자동 판별한다','본문은 packed 필드 대입입니다. 장치 접근 폭·순서·부작용을 처리하는 전용 규칙이 필요합니다.'),('misaligned C 대입 하나면 모든 CPU에서 atomic인가?','아니며 instruction과 동기화 계약을 확인해야 한다','한 줄 C 코드라 항상 원자적이다','compiler가 접근을 분할할 수 있고 원자성 보장도 별도입니다. 언어 표현식 수와 hardware 동작을 구분합니다.')],
  [('확인','CPU put 세 폭의 저장 byte와 getter 결과를 비교했습니다. 실제 MMIO나 concurrent torn read를 검사한 결과는 아닙니다.'),('타입 범위','인자는 해당 u16/u32/u64 폭입니다. 더 넓은 값을 좁은 형식으로 넘길 때의 변환 정책도 확인합니다.')])
 main('generic get_unaligned·포인터 대상 타입으로 읽기','get_unaligned',
  'get_unaligned가 전달 포인터의 pointee 타입으로 접근 폭과 반환형을 결정하는 GNU C 기술을 배웁니다.',
  'get_unaligned(ptr)는 typeof(*(ptr))와 ptr를 __get_unaligned_t에 전달합니다. u32*면 u32,u16*면 u16 형식의 packed 필드를 읽습니다. 타입 질의는 일반 고정 타입 문맥에서 추가 값 접근을 실행하지 않습니다. generic helper는 native 순서이며 포인터가 가리키는 자료를 자동 포맷 인식하거나 endian 탐지하지 않습니다.',
  '자료의 실제 타입과 폭을 알고 있는 커널 GNU C 문맥에서 사용합니다. 임의 buffer를 u32*로 직접 역참조하는 대신 helper의 packed 접근 계약을 확인합니다. strict aliasing·sparse·주소 공간 문맥은 사용 compiler와 커널 설정을 따릅니다.',
  'typeof 대상 타입과 __get_unaligned_t 인자를 연결하세요.',
  [('u32*를 generic get_unaligned에 주면 기본 데이터 폭은?','u32의4byte다','항상unsigned long 크기다','접근 타입은 pointee typeof로 결정됩니다. 포인터 크기나 항상 같은 word 폭을 쓰는 함수가 아닙니다.'),('generic getter가 파일의 LE/BE를 자동 판별하는가?','아니며 native 표현으로 읽는다','header magic만 보고 자동 변환한다','본문에 외부 포맷 탐지가 없습니다. 필요한 byte order를 명시한 helper와 구분합니다.')],
  [('부호','signed int32 포인터는 해당 signed 타입으로 읽습니다. 고정 bit 표현을 signed 숫자로 해석하는 문제와 byte 순서 변환은 별도입니다.'),('문맥','fixture는 GNU11·-fno-strict-aliasing 및 실제 little-endian host에서 generic unsigned/signed 읽기를 확인했습니다. 모든 표준 C alias 규칙의 보편 증명은 아닙니다.')])
 main('generic put_unaligned·쓰기 타입과 const 진단','put_unaligned',
  '저장 타입을 포인터에서 선택하는 매크로와 const 대상에 대한 compiler 오류를 배웁니다.',
  'put_unaligned(val,ptr)는 typeof(*(ptr))를 __put_unaligned_t에 전달합니다. 해당 typed packed 필드에 val을 대입하므로 저장 폭은 pointee 타입입니다. 좁은 unsigned 필드에서는 일반 형 변환으로 값이 잘릴 수 있고 범위 오류를 반환하지 않습니다. const pointee로 쓰려 하면 const 필드 대입이라 compiler가 거절합니다.',
  '쓰기 가능한 실제 타입과 값 범위를 맞춘 buffer를 제공합니다. 외부 endian 표현은 LE/BE writer를 사용합니다. 포인터·값 식은 명확하게 쓰고 인자 평가와 실제 메모리 접근을 구분합니다.',
  'generic 타입 전달·__put_unaligned_t의 do/while·필드 대입을 읽으세요.',
  [('put_unaligned의 저장 폭을 결정하는 것은?','ptr가 가리키는 타입이다','val의 최대 수학적 크기다','pointee typeof를 packed 필드 타입으로 사용합니다. 더 넓은 val을 넣어도 저장소가 자동 확장되지 않습니다.'),('const u32 대상에 generic put을 하면 fixture에서는?','읽기 전용 필드 대입으로 컴파일이 거절된다','const를 자동 제거해 항상 쓸 수 있다','매크로는 pointee 타입을 반영합니다. const 대상 쓰기의 compiler 진단을 실제 확인했습니다.')],
  [('한 번 평가','일반 고정 포인터 getter와 값 getter의 실행 횟수를 각1회로 확인했습니다. typeof 문맥을 추가 값 읽기로 혼동하지 않습니다.'),('경계','const 진단은 형식의 쓰기 허가를 확인합니다. 실제 주소 범위·매핑·수명은 별도 전제입니다.')])
 main('LE 비정렬 읽기·작은 byte 먼저 저장한 값','get_unaligned_le16',
  '파일·protocol의 little-endian 값을 정렬과 CPU 순서 차이를 함께 처리해 읽는 방법을 배웁니다.',
  'get_unaligned_le16/32/64는 __le16/32/64 packed 값을 읽은 뒤 le_to_cpu로 native 숫자를 반환합니다. little-endian byte열은 낮은8bit가 먼저 옵니다. 예를 들어44,33,22,11의32비트 값은0x11223344입니다. source helper는 실제 CPU 순서가 다른 경우에도 변환 primitive의 계약으로 대응합니다.',
  '포맷이 LE라고 명시한 buffer에서 길이2·4·8byte를 확인하고 사용합니다. host가 현재 LE라 변환이 간단하더라도 explicit helper를 쓰면 포맷 의도가 드러납니다. network 모든 필드가 LE라고 추측하지 않습니다.',
  '세 LE getter의 packed typed 읽기와 le_to_cpu를 비교하세요.',
  [('LE32의 byte44,33,22,11이 나타내는 숫자는?','0x11223344다','0x44332211이다','낮은 byte부터 저장합니다. byte 나열 순서와 정수의16진수 표기를 구분합니다.'),('LE helper가 요구하는 버퍼 길이를 검사해 주는가?','아니며 호출자가 필요한2·4·8byte를 보장한다','짧은 buffer는 자동으로0 padding된다','함수 인자에 길이가 없습니다. 접근할 메모리의 유효 범위는 caller의 책임입니다.')],
  [('형식 표식','__le 타입 표식과 변환 함수는 외부 순서의 의미를 표현합니다. fixture에서는 sparse 표식을 별도 타입 검사로 실행하지 않았습니다.'),('검증','실제 packed load와 명시한 little-endian host 변환 모델을 독립 byte reference와 비교했습니다.')])
 main('LE 비정렬 쓰기·CPU 값에서 파일 byte열로','put_unaligned_le16',
  'CPU 정수를 명시된 little-endian 저장 형식으로 바꾸고 비정렬 buffer에 기록하는 과정을 배웁니다.',
  'put_unaligned_le16/32/64는 cpu_to_le 변환 뒤 typed packed writer에 전달합니다. LE32 값0x11223344는44,33,22,11로 저장됩니다. 좁은 writer의 인자는 u16/u32로 선언되어 더 넓은 caller 값은 그 형식으로 변환됩니다. writer는 pointer를 이동시키거나 buffer 전체를 초기화하지 않습니다.',
  '포맷의 필드 offset과 폭을 정확히 계산해 쓰고 필요한 길이를 마련합니다. 연속 필드를 쓸 때 다음 offset은 caller가 조정합니다. 값 범위 검증·checksum·자원 동기화는 이 helper 밖에서 처리합니다.',
  'cpu_to_le→__put_unaligned_t와 세 폭의 선언을 읽으세요.',
  [('LE32로0x11223344를 기록한 byte 순서는?','44,33,22,11이다','11,22,33,44이다','little-endian은 낮은 byte부터 저장합니다. 숫자 표기의 높은 자리부터 쓰는 방식과 다릅니다.'),('writer가 다음 필드 offset까지 자동 이동시키는가?','아니며 전달한 위치에 해당 폭만 저장한다','항상 pointer를4byte 증가시킨다','void*p는 값으로 전달됩니다. caller의 parser/writer 위치 변수 이동을 수행하지 않습니다.')],
  [('폭','u16/u32/u64별 정확한 byte 폭을 제공합니다. 데이터 크기와 메모리 주소 크기를 구분합니다.'),('canary','전체 buffer를 비교해 지정 위치의 해당 폭 외 byte가 유지되는지 확인했습니다.')])
 main('BE 비정렬 읽기·큰 byte 먼저 저장한 값','get_unaligned_be16',
  'network와 big-endian 포맷의 높은 byte부터 저장한 값을 CPU 정수로 읽는 원리를 배웁니다.',
  'get_unaligned_be16/32/64는 packed __be 값을 읽고 be_to_cpu로 변환합니다. byte11,22,33,44의BE32는0x11223344입니다. little-endian host에서 packed native 읽기는 반대 숫자 표현이므로 변환 primitive가 순서를 맞춥니다. 외부byte 순서와 word 순서를 바꾸는 별도 알고리즘 단계는 구분해야 합니다.',
  'network header 등 실제 규격이 BE라고 정한 필드에 사용합니다. protocol 전체에 하나의 순서를 추측하지 말고 각 필드 규격을 확인합니다. unaligned 처리·endian 변환·필드 의미 검증을 별도로 읽습니다.',
  '세 BE getter의 형식 표식과 be_to_cpu를 확인하세요.',
  [('BE32의 byte11,22,33,44가 나타내는 숫자는?','0x11223344다','0x44332211이다','big-endian은 높은 byte부터 저장합니다. host native 정렬·순서와 포맷의 순서가 다를 수 있습니다.'),('BE helper가 field 의미나 protocol 유효성까지 검사하는가?','아니며 값 읽기와 순서 변환을 한다','버전·checksum·필드 범위를 모두 자동 검증한다','본문의 역할은 typed 접근과 endian 변환입니다. 규격 검증은 상위 parser가 수행합니다.')],
  [('순서 구분','암호 코드의 최종 word 재배열은 각 word의 byte 순서와 별개입니다. BE helper만으로 알고리즘의 word 위치를 바꾸지는 않습니다.'),('모델','BE byte reference와 little-endian host의 builtin swap 변환을 확인했습니다. 실제 big-endian CPU 실행을 한 것은 아닙니다.')])
 main('BE 비정렬 쓰기·wire 형식으로 저장','put_unaligned_be16',
  'CPU 정수의 높은 byte부터 외부 buffer에 저장하는 사용법과 변환 단계의 위치를 배웁니다.',
  'put_unaligned_be16/32/64는 cpu_to_be로 값을 바꾼 뒤 packed writer로 기록합니다. BE32 값0x11223344의 byte열은11,22,33,44입니다. 유효 폭의 정수만 해당 구간에 저장하며 heap 할당·pointer bounds·장치 접근 순서·동시 원자성을 제공하지 않습니다.',
  '명시된 BE 필드를 만들고 endian writer를 사용해 host 순서에 대한 추측을 줄입니다. 실제 protocol의 길이·필드 위치·체크 조건은 caller가 관리합니다. 장치 MMIO를 일반 byte buffer로 취급하지 않습니다.',
  '세 BE writer의 cpu_to_be와 typed put 연결을 읽으세요.',
  [('BE32로0x11223344를 쓰면 byte 순서는?','11,22,33,44다','44,33,22,11이다','BE는 높은 byte가 먼저입니다. CPU 내부 숫자를 외부 표현으로 바꾸는 동작입니다.'),('writer가 사용자를 위한 새로운 buffer를 할당하는가?','아니며 이미 유효한 쓰기 위치가 필요하다','함수 안에서 자동kmalloc한다','본문에는 할당이 없습니다. caller가 저장소와 길이를 제공해야 합니다.')],
  [('전체 쌍','16·32·64의 BE put/get 쌍을 각각 byte 기준과 비교했습니다. 같은 잘못된 writer/getter가 서로 맞는 것만 확인한 검사가 아닙니다.'),('범위','검사는 host 메모리의 유효 구간에 제한했습니다. 접근 불가 주소·실제 장치 bus 동작을 실행하지 않았습니다.')])
 main('24비트 읽기·세 byte의 shift와 OR','__get_unaligned_be24',
  '기본 C 정수형보다 좁은24비트 필드를 byte별로 조립하는 원리와 두 endian 변형을 배웁니다.',
  '__get_unaligned_be24는 p0<<16|p1<<8|p2,LE24는 p0|p1<<8|p2<<16입니다. 입력은 u8라 byte값이0..255이며 큰 항도0xff0000까지라 일반32비트 int 문맥의 범위 안입니다. 공개 get_unaligned_be24/le24는 void*를 이 helper에 전달합니다. 결과는 u32이며 signed24의 부호 확장은 하지 않습니다.',
  '규격이24비트인 유효3byte buffer에서 순서에 맞는 helper를 사용합니다. 32비트 packed read로 네 번째 byte까지 읽지 않습니다. signed 의미가 있다면 별도 규격에 맞게 부호 확장을 처리합니다.',
  'BE·LE의 shift 위치와 공개 wrapper를 비교하세요.',
  [('BE24의 byte12,34,56 결과는?','u32 값0x123456이다','항상 signed 음수다','높은 byte를16칸 이동해 세 byte를 OR합니다. 반환u32이며 부호 확장은 없습니다.'),('이24비트 getter가 네 번째 byte도 읽는가?','아니며 p0,p1,p2의 세 byte를 읽는다','언제나 u32 load로4byte를 읽는다','원문은 byte 조합입니다. 필드 저장 폭과 반환 정수 타입의 폭이 다릅니다.')],
  [('LE','같은 숫자0x123456은 LE byte56,34,12입니다. wrapper 두 개와 실제 조립 helper 두 개를 구분합니다.'),('타입','u8의 integer promotion과 shift 결과 범위를 확인합니다.48비트에서는 같은 방식의 int shift가 부족해 별도 cast가 필요합니다.')])
 main('24비트 쓰기·높은8비트는 저장하지 않는다','__put_unaligned_be24',
  'u32 값의 낮은24비트만 세 byte에 쓰는 방법과 caller의 값 범위 검증을 배웁니다.',
  '__put_unaligned_be24는 val>>16,>>8,그대로의 낮은byte를 &0xff로 저장하고 LE24는 반대 순서입니다. 공개 writer는 내부 helper를 호출합니다. val의31..24비트는 저장되지 않으므로0x99123456도 필드에는0x123456만 기록됩니다. 크기 초과의 오류 반환이나 포화 정책은 없습니다.',
  '3byte 저장소를 준비하고 값이24비트 범위에 있어야 하는 규격이면 먼저 검사합니다. pointer 증가가 helper 내부 지역 pointer에서 일어나므로 caller의 위치 변수가 자동 이동한 것으로 생각하지 않습니다.',
  '세 store의 shift·mask·p++와 공개 두 writer를 읽으세요.',
  [('u32 값0x99123456을BE24로 저장하면?','byte12,34,56만 저장된다','9912,34,56처럼4byte로 확장된다','writer는 낮은24비트를 세 byte에 기록합니다. 고비트가 자동 오류로 처리되는 함수가 아닙니다.'),('내부 p++가 caller의 pointer 변수도 증가시키는가?','아니며 값으로 받은 지역 pointer만 이동한다','caller의 parser 위치가 자동으로 갱신된다','pointer 인자를 값으로 전달합니다. 지역 변수 변경과 원래 pointer 변수 변경을 구분합니다.')],
  [('LE','LE24는 낮은 byte부터 세 번 기록합니다. 양쪽을 독립 byte reference와 비교했습니다.'),('길이','반환형 void는 성공 길이나 오류 status를 보고하지 않습니다. 필요한 길이와 값 조건은 caller가 보장합니다.')])
 main('BE48 읽기·shift 전에 u64로 확장','__get_unaligned_be48',
  '48비트 필드를 조립할 때 큰 shift 전에 타입 폭을 늘려야 하는 이유를 배웁니다.',
  '__get_unaligned_be48는 첫 byte 세 개를 u64로 바꾼 후40·32·24칸 shift합니다. 뒤의16·8·0칸 항은32비트 int 문맥에서 범위 안입니다. cast를 shift 뒤에 하면 이미 좁은 타입에서40칸 이동하는 잘못된 연산을 피하지 못합니다. 결과u64의 낮은48비트에 값을 담고 부호 확장은 없습니다.',
  'BE48 규격의 유효6byte를 읽습니다. 예를 들어12,34,56,78,9a,bc는0x123456789abc입니다. 연산의 중간 타입과 반환형을 모두 확인하고 최종 반환u64만 보고 모든 중간 shift가 안전하다고 추측하지 않습니다.',
  '첫 세 항의 (u64)p[i]와40·32·24 shift 순서를 읽으세요.',
  [('40칸 shift 전에 필요한 단계는?','byte값을 u64로 확장하는 것이다','shift 후에만 u64 cast를 하면 충분하다','연산은 당시 타입 폭으로 실행됩니다. 최종 cast가 이미 발생한 폭 밖 shift를 고쳐 주지는 않습니다.'),('BE48 getter가 signed48 부호 확장을 하는가?','아니며 u64 양의 bit 값으로 반환한다','최상위 byte가ff면 자동 음수가 된다','본문은 u64 bit 조합입니다. signed 해석 정책은 별도 규격 처리입니다.')],
  [('예제','첫 byteff의40칸 항은0xff0000000000입니다. u8의 int promotion 상태에서 그만큼 shift하면 필요한 폭을 확보하지 못합니다.'),('24칸의 이유','p2도 shift 전에 u64로 바꿉니다.255<<24는32비트 signed int의 양수 범위를 넘을 수 있어 shift 횟수가32보다 작다는 조건만으로 충분하지 않습니다.'),('wrapper','get_unaligned_be48는 void*를 내부 byte 조립 helper로 전달합니다. 별도 길이 인자나 오류 검사는 없습니다.')])
 main('BE48 쓰기·6byte 저장과 없는 LE48 API','__put_unaligned_be48',
  'u64의 낮은48비트를 저장하는 helper의 구현 범위와 이름만으로 대칭 API를 가정하지 않는 습관을 배웁니다.',
  '__put_unaligned_be48는40·32·24·16·8·0칸 shift한 낮은byte를 여섯 번 기록합니다. 고위16비트는 버리며 public put_unaligned_be48는 내부 helper를 호출합니다. 이 원문 헤더에는 BE48 get/put은 있지만 LE48 이름의 대응 함수는 없습니다. 다른 곳의 API 존재 여부를 대칭이라고 추측하지 않습니다.',
  'BE48 필드에 필요한6byte와 값 범위를 확인합니다. signed48이나LE48 규격은 별도 정의를 찾아 해당 정책을 적용합니다. BE48 helper를 그대로 바꿔 이름만 맞춘 사용법을 제공하지 않습니다.',
  '여섯 byte store·public wrapper와 헤더 전체 API 목록을 읽으세요.',
  [('u64의 가장 높은16비트가BE48에 저장되는가?','아니며 낮은48비트만 저장한다','항상8byte로 확대 저장된다','원문 store는 여섯 개이며40칸부터 낮은byte를 고릅니다. 별도 overflow status는 없습니다.'),('이 헤더에BE48이 있으니 LE48도 반드시 정의되어 있는가?','아니며 원문에 해당 LE48 정의는 없다','모든 폭이 자동으로 두 endian API를 생성한다','함수는 원문에 명시적으로 정의돼 있습니다. 이름 대칭만으로 없는 API를 만들었다고 설명하지 않습니다.')],
  [('전체 검사','세 원문 헤더를7,200,084회 비교해 최적화·ASan/UBSan 통과했습니다.25,000값·16offset·9폭/순서 조합의 독립 read/write와 전체 buffer 보존을 확인했습니다.'),('증거 한계','실제 GCC packed 접근과 little-endian 변환 모델입니다. 실제 big-endian CPU·sparse·원자적 공유 갱신·MMIO·주소 유효성 검증의 증거는 아닙니다.')])
