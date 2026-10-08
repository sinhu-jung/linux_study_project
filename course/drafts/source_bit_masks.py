"""Whole bits headers and constant-forwarding contracts, valid-width GNU C."""
def register(topic,q,detail):
 def lesson(title,path,symbol,why,principle,use,reading,qa,cards):
  topic(title,'라이브러리·알고리즘',path,symbol,why,principle,use,reading,*(q(*x) for x in qa),details=[detail(*x) for x in cards])
 lesson('한 비트 상수·BIT와 정수 타입의 폭','include/vdso/bits.h','BIT',
  '장치 레지스터 flag와 비트 집합에서 원하는 한 위치만 켜는 표현과 정수 타입 조건을 배웁니다.',
  'BIT(nr)는 UL(1)<<nr, BIT_ULL(nr)는 ULL(1)<<nr입니다. 1을 적절한 unsigned 폭으로 만든 뒤 shift합니다. nr는 해당 타입 폭 안의 음이 아닌 위치여야 합니다. BIT는 unsigned long 폭이므로 long32에서는64비트 표현이 아닙니다. 매크로는 음수·너무 큰 shift를 자동으로 거절하는 런타임 API가 아닙니다.',
  'BIT(3)는8로 bit3만 켭니다. 레지스터 폭에 맞춰 BIT 또는 BIT_ULL을 선택하고 |=로 flag를 켜거나 &=~mask로 끕니다. shared 갱신의 원자성은 별도 동기화 문제입니다.',
  'UL·ULL 상수와 두 shift 식을 읽으세요.',
  [('BIT(3)의 정상 숫자 결과는?','8이다','3이다','비트 번호3은2^3의 자리입니다. 번호와 해당 비트가 켜진 mask 값을 구분합니다.'),('BIT가 모든 플랫폼에서 항상64비트 mask인가?','아니며 unsigned long 폭을 따른다','이름이 BIT이면 항상u64다','상수 타입은 UL입니다. long32/64 ABI와 필요한 레지스터 폭을 확인해야 합니다.')],
  [('타입 선택','평범한 signed int 1을 큰 위치로 shift하는 것과 적절한 unsigned 상수 사용은 다릅니다. unsigned라도 폭 밖 shift는 유효하지 않습니다.'),('구현 범위','원문 VDSO bits 헤더는 두 편의 매크로만 정의합니다. VDSO 시스템 호출을 실행하는 코드가 아닙니다.')])
 lesson('비트맵 word와 mask·큰 비트 번호 나누기','include/linux/bits.h','BIT_MASK',
  '여러 machine word로 된 비트맵에서 비트 번호를 배열 원소 번호와 원소 안 위치로 분해하는 기술을 배웁니다.',
  'BIT_WORD(nr)는 nr/BITS_PER_LONG으로 word 번호를, BIT_MASK(nr)는 UL(1)<<(nr%BITS_PER_LONG)으로 그 word 안의 mask를 만듭니다. ULL 변형은 BITS_PER_LONG_LONG 폭을 사용합니다. 예를 들어 long64의 nr70은 word1,내부 bit6입니다. BIT(70)처럼 한 word를 폭 밖으로 shift하는 연산과 다릅니다. BITS_PER_BYTE는8입니다.',
  'bitmap[BIT_WORD(nr)]와 BIT_MASK(nr)를 함께 사용해 배열 내 위치를 선택합니다. bitmap 할당 길이와 nr 범위를 별도로 검사합니다. word 번호 계산이 메모리 bounds 검사를 해 주지는 않습니다.',
  'BIT_WORD·BIT_MASK·ULL 쌍·BITS_PER_BYTE를 읽으세요.',
  [('long64에서 비트 번호70의 위치는?','word1의 bit6이다','word70의 bit1이다','70=1*64+6입니다. 몫은 배열 원소 번호이고 나머지는 해당 word 안의 위치입니다.'),('BIT_WORD 계산만으로 bitmap 배열 범위가 검증되는가?','아니며 저장소 길이를 별도로 확인한다','큰 nr도 자동으로 배열을 늘린다','이 매크로는 정수 위치 계산만 합니다. 할당·확장·범위 오류 처리를 제공하지 않습니다.')],
  [('차이','BIT_MASK는 큰 비트 번호를 word 안으로 접습니다. 전체 비트 위치를 잃지 않으려면 WORD 결과와 함께 사용합니다.'),('확인','비트 번호0..99999를 word와 mask로 나눈 뒤 원래 번호가 복원되는지 실제 원문으로 검사했습니다.')])
 lesson('연속 비트 mask·아래와 위 경계의 교집합','include/uapi/linux/bits.h','__GENMASK',
  '장치 레지스터의 여러 비트 필드를 한 연속 mask로 만드는 산술·논리 조합을 배웁니다.',
  '__GENMASK(h,l)는 전체1에서(1UL<<l)을 빼고1을 더해 l보다 낮은 비트를 지운 부분과,전체1을 폭-1-h만큼 오른쪽 shift해 h보다 높은 비트를 지운 부분을 AND합니다. 결과는 l..h를 모두 포함합니다. h,l은0<=l<=h<폭을 지켜야 합니다. ULL 변형은 unsigned long long에 같은 원리를 적용합니다.',
  'GENMASK(7,4)는0xf0입니다. h가 상한,l이 하한이라는 인자 순서를 지킵니다. full width인63..0도 올바른 unsigned 타입 문맥에서 처리되며 입력 폭을 확인합니다.',
  '아래 비트 제거와 위 비트 제거의 두 부분을 별도로 계산한 뒤 AND하세요.',
  [('GENMASK(7,4)가 포함하는 위치는?','bit4,5,6,7이다','bit7 하나만이다','두 인자는 포함하는 연속 구간의 상한과 하한입니다. 단일 BIT와 여러 비트 GENMASK를 구분합니다.'),('GENMASK의 인자 순서는?','상한 h 다음 하한 l이다','하한 l 다음 상한 h다','정상 조건은 l<=h입니다. 인자 순서를 뒤집으면 정상 범위 mask 계약이 아닙니다.')],
  [('예제','8비트 그림에서11110000은0xf0입니다. 하위4자리와 bit7보다 높은 자리를 각각 제거해 이 교집합을 만듭니다.'),('독립 기준','유효64비트 모든 h,l쌍을 한 비트씩 OR한 참조와 비교해 식의 결과를 확인했습니다.')])
 lesson('GENMASK 입력 검사·상수 역순과 런타임 조건','include/linux/bits.h','GENMASK_INPUT_CHECK',
  'compiler가 알 수 있는 상수 오류를 막는 기술과 실행 중 입력 검사가 다르다는 점을 배웁니다.',
  'GENMASK_INPUT_CHECK는 __is_constexpr(l>h)와 __builtin_choose_expr로 상수 역순이면 BUILD_BUG_ON_ZERO를 통해 컴파일 오류를 냅니다. 상수식이 아니면 검사값0을 선택합니다. 공개 GENMASK와 GENMASK_ULL은 이0을 실제 mask에 더합니다. 이 검사 범위는 l>h 조건이며 음수·타입 폭 밖 h/l의 모든 오류를 checked API처럼 자동 검출하는 것은 아닙니다.',
  '상수 인자에는 compiler 진단을 활용하고 외부 동적 인자는 사용 전에0<=l<=h<폭을 검증합니다. 동적 h3,l5는 이 문맥에서 입력 검사0과 결과0이 나오지만 정상 API 의미로 사용하지 않습니다.',
  'choose_expr의 상수 선택·BUILD_BUG_ON_ZERO·GENMASK 결합을 읽으세요.',
  [('상수 GENMASK(3,5)는 검사 문맥에서?','역순 범위로 컴파일이 거절된다','실행할 때 errno를 반환한다','상수 조건에 대한 build-time 진단입니다. 오류 상태를 런타임 반환하는 함수가 아닙니다.'),('동적 인자의 모든 범위 오류도 이 매크로가 자동 처리하는가?','아니며 호출자가 유효 범위를 확인해야 한다','항상 모든 입력에 안전한 mask로 교정한다','비상수 조건은 검사0을 선택합니다. 기계 정수 shift와 논리 범위의 전제를 호출자가 유지해야 합니다.')],
  [('정적 검사','정상 mask는 상수 초기화에도 쓰일 수 있어 진단용 항이0인 정수 식 형태입니다.'),('별도 실행','상수 역순 fixture는 컴파일 거절됐고 volatile 동적 역순 사례는 런타임 검사가 없음을 확인했습니다. 유효하지 않은 폭 밖 shift는 실행하지 않았습니다.')])
 lesson('128비트 연속 mask·최상위에서 unsigned wrap','include/uapi/linux/bits.h','__GENMASK_U128',
  '큰 mask의 상단 경계 계산에서 unsigned wrap을 의도적으로 쓰는 방식과 compiler 지원을 배웁니다.',
  '__GENMASK_U128(h,l)는 (_BIT128(h)<<1)-_BIT128(l)입니다. 일반 상단은2^(h+1)에서2^l을 빼 l..h를 켭니다. h127이면 unsigned128 최상위 비트를 한 칸 더 shift해0이 되고0-2^l의 modulo2^128 결과가 l..127을 켭니다. shift의 각 횟수는 폭 안이어야 하며 signed overflow로 설명하면 안 됩니다.',
  'compiler가 unsigned __int128을 제공하는 C 문맥에서0<=l<=h<128로 사용합니다. GENMASK_U128 wrapper는 입력 검사 항을 더합니다. 이 정의는 assembly 문맥에 노출되지 않습니다.',
  '_BIT128 형식·상위 bit shift·subtraction과 C 전처리 조건을 읽으세요.',
  [('h127,l0의128비트 mask 결과는?','모든128비트가1이다','상위 shift 때문에 항상0이다','상위 항이0이 된 후 unsigned subtraction0-1이 modulo로 전체1이 됩니다. 중간값과 최종값을 구분합니다.'),('이 원문의128비트 mask가 assembly 문맥에도 제공되는가?','아니며 C 문맥으로 제한한다','모든 assembler가 같은 __int128 식을 실행한다','원문은 compiler의128비트 상수 표현 제약을 설명하고 __ASSEMBLY__ 조건으로 노출을 제한합니다.')],
  [('수학','h5,l2이면2^6-2^2=60,즉00111100입니다. 가장 높은 h는 고정폭 unsigned 산술로 처리됩니다.'),('확인','128비트 모든 정상 구간을 독립 bit OR 기준과 비교했고 full width까지 sanitizer에서 실행했습니다.')])
 lesson('UL·ULL 전달 헤더·C와 assembly 상수 문맥','include/vdso/const.h','UL',
  '짧은 헤더가 계산을 추가하기보다 다른 계층의 타입 상수 정의를 전달하는 역할을 배웁니다.',
  'vdso/const.h의 UL(x),ULL(x)는 UAPI의 _UL,_ULL로 이어집니다. C에서는 suffix가 있는 unsigned long/long long 상수로 만들고 assembly에서는 C 타입 suffix를 붙이지 않는 전처리 분기를 사용합니다. include/linux/const.h는 자신의 include guard와 vdso/const.h 포함만 제공하는 전달 헤더입니다. 헤더 경로 차이가 별도 산술 알고리즘을 뜻하지는 않습니다.',
  'BITS 헤더의 UL(1)이 어디서 실제 타입을 얻는지 include 경로를 따라갑니다. shared C/assembly 헤더의 전처리 분기를 확인하고 assembly 전처리 성공을 실제 assembler 실행 증거로 계산하지 않습니다.',
  'linux/const.h→vdso/const.h→uapi/linux/const.h 및 UL·ULL alias를 읽으세요.',
  [('include/linux/const.h가 별도 상수 계산 함수를 실행하는가?','아니며 guard와 포함으로 정의를 전달한다','모든 상수를 runtime에 재계산한다','짧은 헤더의 역할은 다른 정의를 안전하게 포함하는 것입니다. 실행 코드와 include 구성을 구분합니다.'),('assembly 전처리 검사가 실제 기계어 실행까지 검증하는가?','아니며 전처리 분기만 확인한다','전처리 성공이면 모든 assembler 구현도 증명된다','검사 단계의 범위를 구분합니다. 이 fixture는 C suffix·128매크로 노출 조건을 전처리로 확인했습니다.')],
  [('포함 경로','include/linux/const.h의 _LINUX_CONST_H guard는 중복 포함을 막고 vdso 정의로 연결합니다. vdso 헤더도 자신의 guard와 UAPI 포함 뒤 두 alias를 정의합니다.'),('원문 범위','UAPI const의 일반 alignment·round-up 정의는 앞선 상수 수업에 별도로 해설돼 있습니다. 여기서는 새 BITS 원문과 전달 경로를 연결합니다.')])
 lesson('비트 필드 수정·mask 밖 보존과 동기화 책임','include/linux/bits.h','GENMASK',
  '연속 mask로 특정 필드만 바꾸는 사용법과 read-modify-write가 자동으로 원자적이지 않은 이유를 배웁니다.',
  '필드 h..l을 바꾸는 일반 정수 예는 new=(old&~mask)|((value<<l)&mask)입니다. 첫 부분은 필드 밖 비트를 보존하고 둘째는 value를 위치에 맞춰 필드 안으로 제한합니다. 이 식은 입력값이 필드에 들어가는지 검증하지 않고 높은 비트를 자릅니다. GENMASK는 mask 값 계산일 뿐 공유 상태 갱신을 원자화하거나 장치 MMIO의 접근 규칙을 제공하지 않습니다.',
  '정상 폭·필드 범위에서 값을 준비하고 장치 register라면 문서의 예약 비트·읽기 부작용·쓰기 의미·정확한 accessor를 확인합니다. 두 CPU가 같은 old에서 각기 다른 필드를 고치면 갱신 유실이 가능하므로 잠금 또는 적절한 원자적 프로토콜이 필요합니다.',
  'GENMASK를 mask 값으로 사용한 뒤 OR·AND 식의 각 부분을 독립 계산하세요.',
  [('필드 값이 너무 크면 이 일반 mask 식은?','필드 밖 비트를 잘라 낼 수 있다','자동으로 errno를 반환한다','value shift 뒤 mask AND는 허용 비트만 남깁니다. 값 범위 검증·오류 보고는 별도입니다.'),('GENMASK를 쓴 read-modify-write는 항상 원자적인가?','아니며 공유 갱신 보호가 필요하다','mask 계산 자체가 모든 CPU를 잠근다','연산식은 읽기·계산·쓰기로 나뉩니다. mask와 동기화·MMIO 사용 규칙은 다른 문제입니다.')],
  [('정수 예제','mask0xf0,old0x03,value0xa면 new0xa3입니다. 필드 밖 하위 비트3이 보존됩니다.'),('전체 검사','524,901개 비교를 최적화·ASan/UBSan으로 확인했습니다. 정상64/128범위·BIT/WORD·10만 필드 변경·상수 오류 진단·assembly 전처리를 포함하며 native32·실제 MMIO·assembly 실행 증거는 아닙니다.')])
