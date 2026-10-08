"""Whole bitmap header principles and use conditions, native64 selected execution evidence."""
ROWS = [('Bitmap 헤더의 mask·word 시작과 유효 tail',
  'BITMAP_FIRST_WORD_MASK',
  'FIRST_WORD_MASK는 start의 word 안 위치부터 높은 bit까지1로 만듭니다. LAST_WORD_MASK는 nbits의 마지막 word에서 유효한 낮은 bit를 '
  '남깁니다. native64에서 start65의 첫 mask는 bit1..63이고 nbits65의 마지막 mask는 bit0 하나입니다. 마지막 미사용 bit가 항상0이라는 저장 '
  '불변식은 없습니다. Boolean과 count 조회는 유효 mask로 걸러야 합니다.',
  '배열 word 번호와 내부 bit 번호를 나누어 계산합니다. tail에 쓰레기 값이 있어도 유효 bit 결과를 구분합니다. LAST_WORD_MASK(64)는 전체 word '
  'mask이며0개 필드라는 뜻과 혼동하지 않습니다.',
  [('native64에서 nbits65의 마지막 유효 mask는?',
    'bit0 하나다',
    '두 번째 word전체다',
    '첫64bit 뒤에 하나만 더 있습니다. 마지막 word의 나머지는 유효 집합에 포함되지 않습니다.'),
   ('bitmap의 미사용 tail은 항상0인가?',
    '아니며 조회가 유효 bit를 걸러야 한다',
    '모든 연산이 항상 tail을0으로 만든다',
    '원문의 저장 계약은 tail을 항상 정리하지 않습니다. 연산 종류별 mask 적용을 확인합니다.')],
  [('원문과 사용 조건', '두 macro는 유효 길이의 몫과 나머지에 맞춰 읽습니다. 단순히 메모리 byte 길이의 mask로 해석하지 않습니다.'),
   ('검사 범위',
    'native64 little endian의 선택된 경로를 독립 bit 참조 모델로 비교했습니다. 검색·bitop·mask는 명시적인 검사 문맥 모델이며 모든 '
    'architecture의 실행 증거는 아닙니다.')]),
 ('Bitmap 크기와 zero fill·저장 word까지 초기화',
  'bitmap_zero',
  'bitmap_size는 nbits를 BITS_PER_LONG 배수로 올린 뒤 byte 수로 바꿉니다. native64의65bit는16byte입니다. '
  'small_const_nbits는 양수이며 한 word이하인 컴파일 상수일 때 한 word 직접 대입으로 최적화합니다. bitmap_zero는0을,bitmap_fill은~0UL '
  '또는0xff byte를 저장하여 유효 영역 뒤 word 경계까지 초기화합니다.',
  'bitmap_size만큼 실제 저장 공간을 마련합니다. 유효 bit만 바꾸고 같은 word의 바깥 bit를 보존해야 하면 set/clear 범위 API를 검토합니다. fill이 '
  'tail까지1로 만드는 점을 허용하는 집합 계약을 확인합니다.',
  [('native64에서 bitmap_size(65)는?',
    '16byte다',
    '9byte만 저장하면 된다',
    '실제 표현은 unsigned long 배열입니다. 두 word를 저장할 공간이 필요합니다.'),
   ('bitmap_fill은 마지막 word의 미사용 bit도 바꾸는가?',
    '그렇다',
    '유효 bit 밖을 항상 보존한다',
    'fill은 저장 word 영역을 채웁니다. 선택한 bit 범위만 변경하는 bitmap_set과 차이가 있습니다.')],
  [('원문과 사용 조건', '헤더의 overview도 zero/fill의 word 단위 효과를 별도로 설명합니다.0bit는 작은 상수 직접대입 경로에 들어가지 않습니다.'),
   ('검사 범위',
    'native64 little endian의 선택된 경로를 독립 bit 참조 모델로 비교했습니다. 검색·bitop·mask는 명시적인 검사 문맥 모델이며 모든 '
    'architecture의 실행 증거는 아닙니다.')]),
 ('Bitmap copy·저장 표현과 overlap 조건',
  'bitmap_copy',
  'bitmap_copy는 작은 양수 상수 길이면 한 word를 대입하고 그 외에는 bitmap_size(nbits) byte를 memcpy합니다. 유효 bit 뿐 아니라 마지막 저장 '
  'word의 tail도 복사합니다. 이 함수 자체는 tail을 정리하지 않습니다. 일반 memcpy 경로의 부분 겹침을 허용하는 memmove 계약은 제공하지 않습니다.',
  '원본과 목적지에 충분한 word 저장 공간을 준비합니다. 복사 뒤 tail0이 필요하면 copy_clear_tail을 선택합니다. 부분 겹침이 있는 버퍼에는 일반 복사 계약을 '
  '확인하고 이 함수의 memcpy를 memmove로 가정하지 않습니다.',
  [('bitmap_copy가 tail을 자동0으로 만드는가?',
    '아니며 저장 word를 그대로 복사한다',
    '항상 tail을 지운다',
    'tail 정리는 별도의 helper가 제공합니다. 복사 자체와 유효 bit 정규화를 구분합니다.'),
   ('일반 bitmap_copy 경로는 부분 overlap을 보장하는가?',
    '아니며 memcpy 계약이다',
    'memmove처럼 모든 overlap을 보장한다',
    '원문의 일반 경로는 memcpy입니다. 자료구조 이름으로 복사 함수의 alias 계약을 바꾸지 않습니다.')],
  [('원문과 사용 조건', '작은 상수의 한 word 대입과 일반 memcpy 경로를 각각 읽습니다. 최적화 하나의 성공을 모든 overlap 보장으로 확대하지 않습니다.'),
   ('검사 범위',
    'native64 little endian의 선택된 경로를 독립 bit 참조 모델로 비교했습니다. 검색·bitop·mask는 명시적인 검사 문맥 모델이며 모든 '
    'architecture의 실행 증거는 아닙니다.')]),
 ('Bitmap copy_clear_tail·복사 뒤 마지막 mask',
  'bitmap_copy_clear_tail',
  '먼저 bitmap_copy를 수행합니다. nbits가 word 배수가 아니면 dst[nbits/BITS_PER_LONG]에 LAST_WORD_MASK를 AND합니다. 길이65는 두 '
  'word를 복사하고 마지막 word의 bit0만 남깁니다. 길이64는 전체 word가 유효하므로 추가 정리가 없습니다. 마지막 저장 공간은 여전히 필요합니다.',
  '직렬화나 다른 변환 전에 tail0 표현이 필요할 때 사용합니다. 원본의 유효 bit와 복사 결과를 비교하고 마지막 word의 미사용 bit도 확인합니다. source와 '
  'destination 용량을 별도로 보장합니다.',
  [('길이65 복사에서 두 번째 word에 남는 bit는?',
    'bit0이다',
    'bit63만 남는다',
    '마지막 유효 bit는 논리 bit64이며 두 번째 word 내부 bit0입니다.'),
   ('길이가64면 추가 tail mask 분기를 실행하는가?',
    '아니며 word 배수다',
    '항상 다음 word까지 지운다',
    'nbits%BITS_PER_LONG이0이면 모든 저장 bit가 유효합니다. 다음 word를 정리하지 않습니다.')],
  [('원문과 사용 조건', '독립 검사에서 유효 bit 복사와 tail0 조건을 각각 비교했습니다.'),
   ('검사 범위',
    'native64 little endian의 선택된 경로를 독립 bit 참조 모델로 비교했습니다. 검색·bitop·mask는 명시적인 검사 문맥 모델이며 모든 '
    'architecture의 실행 증거는 아닙니다.')]),
 ('Bitmap copy_and_extend·작은 집합을 큰 저장 공간으로',
  'bitmap_copy_and_extend',
  'count의 저장 word 수를 구해 memcpy하고 count가 word 배수가 아니면 마지막 복사 word를 mask 합니다. 그 뒤 목표 size의 byte 크기에서 복사 '
  'word byte 수를 뺀 만큼 뒤 공간을0으로 만듭니다. count65,size128이면 첫65bit를 보존하고 나머지를0으로 정규화합니다. count가 size보다 크면 길이 '
  '차의 안전성을 자동 보장하지 않습니다.',
  '0<=count<=size와 두 배열 용량을 먼저 확인합니다. 겹치지 않는 배열을 사용합니다. 큰 집합으로 확장할 때 추가 bit가0이어야 하는 계약에 적용합니다. count와 '
  'size를 byte 수로 전달하지 않습니다.',
  [('count65,size128의 새 bit65..127은?',
    '0이다',
    '원본 tail 값을 그대로 유지한다',
    '복사 tail mask와 뒤 memset이 유효한 원본 바깥을0으로 확장합니다.'),
   ('count가 size보다 커도 함수가 안전한 오류를 반환하는가?',
    '아니며 호출자 전제가 필요하다',
    '항상 -EINVAL을 반환한다',
    '이 함수는 void이며 크기 차 검사가 없습니다. 잘못된 길이로 memset을 실행하지 않도록 호출 경계에서 검증합니다.')],
  [('원문과 사용 조건', '검사 사례는 count0..256,size320의 유효 범위만 사용했습니다. 크기 underflow는 실행하지 않았습니다.'),
   ('검사 범위',
    'native64 little endian의 선택된 경로를 독립 bit 참조 모델로 비교했습니다. 검색·bitop·mask는 명시적인 검사 문맥 모델이며 모든 '
    'architecture의 실행 증거는 아닙니다.')]),
 ('Bitmap AND OR XOR·상수 한 word와 일반 경로',
  'bitmap_and',
  'small_const_nbits이면 bitmap_and는 두 word를 AND하고 LAST_WORD_MASK를 적용한 뒤 결과가0이 아닌지 반환합니다. OR와 XOR의 작은 상수 '
  '경로는 word 연산만 수행하며 tail을 정리하지 않습니다. 일반 경로는 각 __bitmap helper로 넘어갑니다. AND의 bool은 dst 주소가 유효하다는 뜻이 아니라 '
  '유효 집합이 비어 있지 않다는 뜻입니다.',
  '교집합은 AND,합집합은 OR,서로 다른 원소는 XOR로 계산합니다. bool 반환과 저장 결과를 구분합니다. tail의 실제 숫자 대신 유효 bit를 비교하며 전체 연산의 '
  '원자성을 가정하지 않습니다.',
  [('bitmap_and의 true는 무엇인가?',
    '유효 교집합에1bit가 있다',
    'dst 포인터가 NULL이 아니다',
    '반환은 mask 된 연산 결과의 비어 있음 여부입니다. 주소 검증과 다른 계약입니다.'),
   ('작은 상수 OR가 tail을 반드시0으로 만드는가?',
    '아니며 mask를 적용하지 않는다',
    '항상 AND처럼 tail을 지운다',
    'OR와 AND의 구현은 mask 정책이 다릅니다. 모든 집합 연산을 같은 저장 불변식으로 설명하지 않습니다.')],
  [('원문과 사용 조건', 'native64의 상수13bit AND 경로를 별도로 검사했습니다. runtime 길이의 helper 경로도 독립 bit 모델과 대조했습니다.'),
   ('검사 범위',
    'native64 little endian의 선택된 경로를 독립 bit 참조 모델로 비교했습니다. 검색·bitop·mask는 명시적인 검사 문맥 모델이며 모든 '
    'architecture의 실행 증거는 아닙니다.')]),
 ('Bitmap 차집합 complement replace·mask로 집합 선택',
  'bitmap_replace',
  'bitmap_andnot은 src1&~src2로 차집합을 만들고 유효 tail을 거른 bool을 반환합니다. complement는 word를 반전하므로 tail도 바뀔 수 '
  '있습니다. replace는 old&~mask와 new&mask를 OR하여 mask0에서는 old,mask1에서는 new를 선택합니다. 작은 상수 replace도 별도 tail 정리 '
  '없이 한 word 식을 사용합니다.',
  '권한이나 자원 집합의 일부를 다른 집합으로 교체할 때 mask의 의미를 먼저 적습니다. 원본과 목적지의 유효 word 용량과 alias를 검토합니다. bit별 선택 원리와 동시 '
  'writer의 보호를 구분합니다.',
  [('replace에서 mask bit가1이면 어느 값을 택하는가?',
    'new의 해당 bit 다',
    '항상 old를 보존한다',
    'old는 mask의 NOT로 걸러지고 new는 mask로 선택됩니다. 두 부분을 OR하여 합칩니다.'),
   ('complement가 유효 tail도 언제나0으로 유지하는가?',
    '아니며 word 반전이다',
    '반전 뒤 항상 tail을 지운다',
    '본문은 ~src입니다. 유효 길이 밖의 저장 bit를 정규화하는 별도 단계와 다릅니다.')],
  [('원문과 사용 조건', '각 word 선택 식의 exact alias와 부분 overlap은 별개입니다. 원본별 덮어쓰기 순서를 검토합니다.'),
   ('검사 범위',
    'native64 little endian의 선택된 경로를 독립 bit 참조 모델로 비교했습니다. 검색·bitop·mask는 명시적인 검사 문맥 모델이며 모든 '
    'architecture의 실행 증거는 아닙니다.')]),
 ('Bitmap equal·컴파일 상수와 endian별 byte 비교',
  'bitmap_equal',
  '한 word이하 상수 길이면 XOR한 결과를 LAST_WORD_MASK로 거릅니다. 나머지 경로는 길이의 메모리 정렬 조건이 컴파일 상수일 때 memcmp(nbits/8)를 사용할 '
  '수 있습니다. little endian의 BITMAP_MEM_ALIGNMENT는8bit이고 다른 endian은8*sizeof(unsigned long)입니다. 그 외에는 '
  '__bitmap_equal로 유효 tail을 비교합니다.',
  '비교 목적은 유효 bit 집합의 같음입니다. endian에 따라 byte 단위 최적화 전제가 달라지는 이유를 저장 표현과 연결합니다. 임의 endian에서 작은 byte '
  'memcmp를 직접 적용하지 않습니다.',
  [('작은 상수 equal이 미사용 tail 차이 때문에 false가 되는가?',
    '아니며 유효 mask로 거른다',
    'tail 하나라도 다르면 항상 false 다',
    'XOR 뒤 LAST_WORD_MASK가 유효 bit만 남깁니다. 저장 tail은 비교 결과에서 제외합니다.'),
   ('메모리 정렬 최적화 조건은 모든 endian에서 같은가?',
    '아니며 little endian과 다른 경로가 다르다',
    '항상8bit 정렬만 검사한다',
    '원문은 endian 조건에 따라 BITMAP_MEM_ALIGNMENT를 정의합니다. 저장 byte와 bit 번호의 연결을 확인합니다.')],
  [('원문과 사용 조건', '16bit 컴파일 상수의 little endian byte 비교를 별도로 실행했습니다. native big endian 실행 증거는 아닙니다.'),
   ('검사 범위',
    'native64 little endian의 선택된 경로를 독립 bit 참조 모델로 비교했습니다. 검색·bitop·mask는 명시적인 검사 문맥 모델이며 모든 '
    'architecture의 실행 증거는 아닙니다.')]),
 ('Bitmap or_equal intersects subset·관계만 묻는 조회',
  'bitmap_or_equal',
  'or_equal은 (src1|src2)^src3를 유효 mask로 걸러0인지 검사합니다. intersects는 src1&src2 중 유효1bit가 있는지,subset은 '
  'src1&~src2가 유효 범위에서0인지 묻습니다. 상수 작은 길이면 word 식,그 외에는 일반 helper를 사용합니다. 이 API들은 결과 bitmap을 새로 저장하지 않는 '
  '관계 조회입니다.',
  '집합의 합이 특정 집합인지,공통 원소가 있는지,한 집합이 다른 집합 안에 포함되는지 목적에 맞춰 선택합니다. subset의 방향을 바꾸면 다른 질문이 됩니다. bool을 집합의 '
  '원소 개수로 해석하지 않습니다.',
  [('subset(A,B)는 어느 관계인가?',
    'A의 모든 원소가 B에 속한다',
    'B의 모든 원소가 A에 속한다',
    'A&~B가 비어 있는지 검사합니다. 왼쪽 집합에만 있는 원소가 없어야 합니다.'),
   ('or_equal이 dst bitmap을 갱신하는가?',
    '아니며 세 집합의 관계를 반환한다',
    '합집합을 세 번째 인자에 저장한다',
    '세 인자는 const 입력입니다. OR 결과를 저장하는 bitmap_or와 조회를 구분합니다.')],
  [('원문과 사용 조건', '각 관계를 bit별 독립 bool 누적 모델과 비교했습니다. 저장 표현의 tail 차이를 유효 관계에 포함하지 않습니다.'),
   ('검사 범위',
    'native64 little endian의 선택된 경로를 독립 bit 참조 모델로 비교했습니다. 검색·bitop·mask는 명시적인 검사 문맥 모델이며 모든 '
    'architecture의 실행 증거는 아닙니다.')]),
 ('Bitmap empty full weight·공집합과 원소 수',
  'bitmap_empty',
  'empty의 작은 상수 경로는 src&유효 mask가0인지 확인합니다. 일반 경로는 find_first_bit가 nbits를 반환하는지 비교합니다. full은 첫0bit가 '
  '없는지,weight는 유효1bit의 개수를 묻습니다. weight_and와 weight_andnot은 교집합과 차집합의 원소 수입니다. 길이0은 일반 조회에서 empty와 '
  'full이 모두 참이고 weight는0입니다.',
  '원소 존재,전체 설정,개수 중 필요한 질문을 선택합니다. 검색 함수의 nbits 종료값을 실제 bit인덱스로 사용하지 않습니다. 일반 검색 경로의 모델과 실제 '
  'architecture 검색 구현의 검증을 구분합니다.',
  [('0bit 집합의 empty와 full 결과는?',
    '둘 다 true 다',
    'empty만 true이고 full은 false 다',
    '검사할 유효 bit가 없습니다. 첫1과 첫0 검색 모두 길이0 종료값을 반환하는 빈 범위 규칙입니다.'),
   ('weight_andnot은 무엇을 세는가?',
    '첫 집합에만 있는 유효1bit 수다',
    '두 집합의 모든 bit 주소 수다',
    'src1&~src2의 설정 bit를 셉니다. 차집합의 원소 개수라는 의미입니다.')],
  [('원문과 사용 조건', '실행 검사에서는 조회와 독립 bit별 count의 관계를 비교했습니다. tail이0이라는 전제 없이 조회합니다.'),
   ('검사 범위',
    'native64 little endian의 선택된 경로를 독립 bit 참조 모델로 비교했습니다. 검색·bitop·mask는 명시적인 검사 문맥 모델이며 모든 '
    'architecture의 실행 증거는 아닙니다.')]),
 ('Bitmap set clear wrapper·한 bit mask memset 선택',
  'bitmap_set',
  '상수 길이1은 __set_bit로 처리합니다. start+길이가 작은 상수 범위면 GENMASK로 한 word를 변경합니다. start와 길이가 endian별 메모리 정렬 조건을 '
  '만족하는 상수이면 byte memset으로 채웁니다. 그 외에는 __bitmap_set 또는 __bitmap_clear입니다. clear는 mask NOT와0 byte 채우기로 '
  '같은 영역을 지웁니다.',
  'start와 길이 합이 실제 저장 범위 안인지 먼저 확인합니다.0길이는 상수 GENMASK 분기의 경계가 유효한지 별도 검토하고 안전한 호출 계약을 유지합니다. 단일 bit 경로도 '
  'non-atomic __계열임을 확인합니다.',
  [('상수 길이1인 set의 선택 경로는?',
    '__set_bit다',
    '항상 전체 bitmap memset이다',
    '가장 먼저 단일 bit 조건을 검사합니다. 하나의 bit를 바꾸는 helper로 연결합니다.'),
   ('이 wrapper가 모든 경로에서 범위와 overflow를 검사하는가?',
    '아니며 호출자가 범위를 보장한다',
    '항상 잘못된 범위에 오류를 반환한다',
    'void wrapper는 최적화 경로를 선택합니다. 객체 용량을 인자로 받아 검증하는 validator가 아닙니다.')],
  [('원문과 사용 조건', '상수 단일 bit,작은 mask,byte 정렬 범위를 별도로 검사했습니다.0길이 invalid mask 경로는 실행하지 않았습니다.'),
   ('검사 범위',
    'native64 little endian의 선택된 경로를 독립 bit 참조 모델로 비교했습니다. 검색·bitop·mask는 명시적인 검사 문맥 모델이며 모든 '
    'architecture의 실행 증거는 아닙니다.')]),
 ('Bitmap shift wrapper·작은 상수와 큰 배열 전제',
  'bitmap_shift_right',
  '작은 양수 상수 nbits이면 right는 src의 유효 mask를 적용한 뒤 shift하고 left는 shift한 뒤 유효 mask를 적용합니다. 그 외에는 '
  '__bitmap_shift helper를 사용합니다. 작은 상수의 C word shift는 shift가 word 폭 이상이면 정상 연산이 아닙니다. 일반 helper도 off와 '
  '배열 용량에 맞는 유효 범위를 지켜야 합니다.',
  'shift 값을 선택 경로의 유효 범위로 제한합니다. 원본과 목적지가 같을 때 일반 right와 left의 순회 방향을 함께 읽습니다. 임의로 큰 shift에 항상0을 반환하는 '
  'API라고 설명하지 않습니다.',
  [('작은 상수 right 경로의 mask는 shift 전인가?',
    'shift 전이다',
    'shift 뒤에만 적용한다',
    '입력 tail의 쓰레기 bit가 낮은 유효 영역으로 들어오는 것을 먼저 mask로 걸러야 합니다.'),
   ('작은 상수 word에 shift64를 무조건 전달해도 되는가?',
    '아니며 C shift 범위를 지켜야 한다',
    '항상0으로 자동 처리한다',
    '직접 word shift 표현에는 폭 이상의 shift가 허용되지 않습니다. 호출 조건과 일반 helper 선택을 따로 확인합니다.')],
  [('원문과 사용 조건', '실행 증거는 nbits 양수와 shift<=nbits의 일반 helper 영역입니다. 작은 상수 shift는 word 폭 안의 별도 전제가 필요합니다.'),
   ('검사 범위',
    'native64 little endian의 선택된 경로를 독립 bit 참조 모델로 비교했습니다. 검색·bitop·mask는 명시적인 검사 문맥 모델이며 모든 '
    'architecture의 실행 증거는 아닙니다.')]),
 ('Bitmap scatter·촘촘한 bit를 mask 위치로 배치',
  'bitmap_scatter',
  'dst를0으로 만들고 mask의 설정 위치를 낮은 번호부터 순회합니다. src의 bit0,1,2 순서대로 읽어 mask의 첫째,둘째,셋째 설정 위치에 __assign_bit합니다. '
  'mask0x1313의 설정 위치는0,1,4,8,9,12이며 src0x5a의 낮은 여섯 bit를 옮기면0x0302입니다. dst가 src나 mask와 같으면 초기 zero가 입력을 '
  '지울 수 있습니다.',
  '입력 src와 mask,출력 dst를 분리하고 실제 길이를 보장합니다. sparse 장치 필드나 자원 위치에 dense 값의 낮은 bit 들을 배치할 때 사용합니다. mask 원소 '
  '수보다 높은 src bit가 복원될 것이라고 기대하지 않습니다.',
  [('mask의 세 번째 설정 위치에는 src의 어느 bit를 놓는가?',
    'bit2다',
    'mask의 실제 bit 번호와 같은 src bit 다',
    'src의 dense 순번과 mask의 sparse 위치를 연결합니다. 두 인덱스는 다른 좌표입니다.'),
   ('dst==src로 안전한 in-place scatter를 보장하는가?',
    '아니며 먼저 dst를0으로 만든다',
    '항상 memmove처럼 처리한다',
    '초기 zero가 입력을 지울 수 있습니다. 알고리즘의 alias 조건을 먼저 확인해야 합니다.')],
  [('원문과 사용 조건', '독립 rank 기반 bit 모델로 각 출력 위치를 비교했습니다. __assign_bit는 검사 문맥의 non-atomic 모델입니다.'),
   ('검사 범위',
    'native64 little endian의 선택된 경로를 독립 bit 참조 모델로 비교했습니다. 검색·bitop·mask는 명시적인 검사 문맥 모델이며 모든 '
    'architecture의 실행 증거는 아닙니다.')]),
 ('Bitmap gather·mask 위치를 낮은 연속 bit로 모으기',
  'bitmap_gather',
  'dst를0으로 만들고 mask의 설정 위치 순서대로 src를 읽어 dst bit0,1,2에 놓습니다.0x0302를 mask0x1313으로 gather하면0x001a입니다. '
  'scatter 뒤 gather는 mask의 설정 개수만큼 낮은 src bit만 복원합니다. mask가 여섯 위치이면 src0x5a의 상위 bit6은 사라지므로 원본과 완전한 같음이 '
  '아니라 같은 scatter 결과라는 동등성이 성립합니다.',
  'mask가 선택하는 위치를 먼저 나열하고 출력 rank를 붙입니다. 입력과 출력 저장 공간을 분리합니다. 압축 과정에서 버려지는 bit 범위를 명확히 하고 roundtrip을 '
  '무조건 원본 복원으로 가정하지 않습니다.',
  [('0x5a를 여섯 위치로 scatter 후 gather하면?',
    '0x1a다',
    '항상0x5a 전체다',
    'mask는 여섯 bit만 전달합니다. bit6의 정보는 변환에 포함되지 않아 낮은 여섯 bit만 돌아옵니다.'),
   ('gather는 sparse 위치의 실제 번호를 그대로 dst 번호로 쓰는가?',
    '아니며0부터 연속 rank로 모은다',
    '항상 같은 bit 번호에 복사한다',
    '설정 위치 순서의 번호가 출력 좌표입니다. sparse와 dense의 차이를 구분합니다.')],
  [('원문과 사용 조건', '헤더의 문서가 비전단사와 동등한 scatter 결과를 설명합니다. 함수 하나의 역이라는 말을 전체 정보 복원으로 확대하지 않습니다.'),
   ('검사 범위',
    'native64 little endian의 선택된 경로를 독립 bit 참조 모델로 비교했습니다. 검색·bitop·mask는 명시적인 검사 문맥 모델이며 모든 '
    'architecture의 실행 증거는 아닙니다.')]),
 ('Bitmap 연속 set region·검색 종료값과 두 경계',
  'bitmap_next_set_region',
  'rs는 입력 검색 시작점이며 find_next_bit로 다음1bit 위치로 갱신됩니다. re는 rs+1부터 다음0bit를 찾은 결과입니다. 정상 발견한 영역은[rs,re)입니다. '
  '발견하지 못하면 rs가 end 종료값이 될 수 있습니다. 다음0 검색도 end로 제한되므로 결과를 그대로 버퍼 주소로 사용할 수는 없습니다.',
  '호출 뒤 rs<end인지 확인한 다음 반열린 구간을 처리합니다. 다음 호출의 시작점을 이전 re로 이동하여 이미 처리한 영역을 반복하지 않습니다. end와 덧셈이 표현 범위를 넘지 '
  '않는 유효 입력을 제공합니다.',
  [('영역[rs,re)에서 re의 bit도 포함하는가?',
    '아니며 re는 제외 경계다',
    '양쪽 모두 포함한다',
    're는 다음0bit 또는 종료 경계입니다. 설정된 연속 구간은 re 전까지입니다.'),
   ('rs가 end이면 실제 설정 bit를 찾은 것인가?',
    '아니며 종료값을 확인한다',
    'end 주소의 bit가 설정됐다는 뜻이다',
    '검색은 못 찾았을 때 길이를 반환합니다. 그 값을 실제 배열 인덱스로 사용하지 않습니다.')],
  [('원문과 사용 조건', '이 wrapper의 실제 helper 선택은 검색 구현에 의존합니다. 검색 종료값 계약과 caller 반복을 함께 읽습니다.'),
   ('검사 범위',
    'native64 little endian의 선택된 경로를 독립 bit 참조 모델로 비교했습니다. 검색·bitop·mask는 명시적인 검사 문맥 모델이며 모든 '
    'architecture의 실행 증거는 아닙니다.')]),
 ('Bitmap 영역 allocate release·busy 검사와 동기화',
  'bitmap_allocate_region',
  '영역 길이는 BIT(order),즉2의 order제곱입니다. allocate는[pos,pos+len)에서1bit를 검색해 있으면 -EBUSY를 반환하고 없으면 '
  'bitmap_set으로 영역을 차지한 뒤0을 반환합니다. release는 같은 길이의 bitmap_clear입니다. 확인과 설정 사이를 원자적으로 잠그는 코드가 없어 경쟁 '
  'allocator는 외부 동기화가 필요합니다.',
  'order와 pos+len을 유효한 표현 및 배열 범위로 제한합니다. 같은 자원을 사용하는 다른 allocator와 잠금 계약을 공유합니다. release에 allocate 때의 '
  '위치와 order를 전달하고 임의 영역을 해제하지 않습니다.',
  [('영역 안에 이미1bit가 있으면?',
    '-EBUSY를 반환하고 설정하지 않는다',
    '나머지0bit만 부분 할당한다',
    '원문은 먼저 전체 범위의 설정 bit를 찾습니다. busy이면 bitmap_set 전에 반환합니다.'),
   ('검색 후 set의 두 단계가 동시 할당을 자동 배제하는가?',
    '아니며 외부 동기화가 필요하다',
    '항상 하나의 atomic transaction이다',
    '일반 검색과 non-atomic 범위 갱신입니다. 두 호출자가 같은 빈 영역을 볼 수 있습니다.')],
  [('원문과 사용 조건', '검사에서는 busy 반환 뒤 전체 bitmap 보존을 확인했습니다. 실제 allocator 경쟁 동기화를 실행한 증거는 아닙니다.'),
   ('검사 범위',
    'native64 little endian의 선택된 경로를 독립 bit 참조 모델로 비교했습니다. 검색·bitop·mask는 명시적인 검사 문맥 모델이며 모든 '
    'architecture의 실행 증거는 아닙니다.')]),
 ('Bitmap find_free_region·2의 거듭제곱 크기와 정렬',
  'bitmap_find_free_region',
  'pos0부터 BIT(order) 길이 단위로 이동합니다. 각 end=pos+길이가 bits 이내일 때 allocate_region을 시도합니다. 성공하면 pos를 반환하고 모든 '
  '정렬 영역이 busy이거나 들어갈 곳이 없으면 -ENOMEM입니다. 임의 연속0 영역을 bit 마다 검색하는 것과 달리 길이와 같은 정렬 단위로만 후보를 선택합니다.',
  '요청 크기와 정렬이2의 거듭제곱인 자원 관리에 사용합니다. 반환이 음수인지 먼저 확인합니다. order의 shift 폭,덧셈 overflow와 bitmap 용량은 호출자 전제로 '
  '지킵니다.',
  [('order6에서 후보 위치 간격은?', '64bit다', '6byte다', 'BIT(6)는64입니다. order는 bit 개수 자체가 아니라 크기의 밑2 지수입니다.'),
   ('정렬 영역을 찾지 못하면 반환은?',
    '-ENOMEM이다',
    '항상 bits 주소를 반환한다',
    '이 wrapper는 errno형 음수 실패를 반환합니다. 다른 bitmap 검색의 길이 종료값과 계약이 다릅니다.')],
  [('원문과 사용 조건', '192bit 배열의 세64bit 영역을 차례로 할당하고 release 재사용과 꽉 찬 실패를 검사했습니다.'),
   ('검사 범위',
    'native64 little endian의 선택된 경로를 독립 bit 참조 모델로 비교했습니다. 검색·bitop·mask는 명시적인 검사 문맥 모델이며 모든 '
    'architecture의 실행 증거는 아닙니다.')]),
 ('Bitmap 배열 변환·u32 u64와 native word 폭',
  'bitmap_from_u64',
  'bitmap은 unsigned long 배열이므로32bit와64bit 환경의 저장 word가 다릅니다. native64의 arr32 함수는 낮은u32와 높은u32를 숫자 '
  'shift로 합칩니다. native32의 arr64 함수는 낮은 word부터 분리합니다. native64의 arr64는 copy_clear_tail macro 입니다. 입력 배열 '
  '원소는 host byte order 정수이며 이 API가 네트워크 endian 변환을 뜻하지 않습니다.',
  '변환하려는 배열의 원소 타입과 실제 용량을 확인합니다. native64 arr32는 홀수 개u32 끝을 읽을 때 u64 cast로 넘겨 읽지 않도록 별도 함수로 처리합니다. 원소 '
  '정수 순서와 byte serialization을 구분합니다.',
  [('arr32의 입력 u32는 어떤 byte order 계약인가?',
    'host byte order의 정수다',
    '항상 network big endian byte 다',
    '원문 주석은 host byte order 배열입니다. 숫자 합성과 장치 byte 포맷 변환은 다른 기술입니다.'),
   ('native64 arr32를 무조건 u64 포인터로 cast해 읽어도 되는가?',
    '아니며 끝 원소의 용량과 정렬을 확인한다',
    '홀수u32 끝도 항상 안전하다',
    '헤더는64bit cast의 마지막 경계 문제 때문에 별도 변환을 사용한다고 설명합니다. 실제 저장 폭을 지켜야 합니다.')],
  [('원문과 사용 조건',
    'native64의 실제 arr32 함수와 tail 정리를 실행했습니다. native32 arr64 분기는 원문 해설이며 해당 ABI 실행 증거는 아닙니다.'),
   ('검사 범위',
    'native64 little endian의 선택된 경로를 독립 bit 참조 모델로 비교했습니다. 검색·bitop·mask는 명시적인 검사 문맥 모델이며 모든 '
    'architecture의 실행 증거는 아닙니다.')]),
 ('Bitmap 상수 u64 initializer·ABI와 low high 원소',
  'BITMAP_FROM_U64',
  '64bit의 BITMAP_FROM_U64(n)은 n 한 원소입니다.32bit에서는 u64의 낮은32bit를 unsigned long으로 만들고 이어 높은32bit를 '
  'shift32하여 두 원소로 나열합니다. native bitmap의 bit42는 두 번째32bit word의 bit10입니다. C의 u64 메모리를 BE32에서 그대로 두 '
  'word로 해석하는 것과 다르며 숫자 분해로 순서를 명시합니다.',
  '배열 initializer 문맥에 필요한 원소 수와 타입을 확인합니다. macro 입력의 평가 횟수도 경로마다 검토하여32bit 두 표현에 부작용 인자를 넣지 않습니다. 큰 '
  'shift가 u64 cast 뒤 수행되는 이유를 읽습니다.',
  [('32bit bitmap의 bit42 위치는?',
    '두 번째 word의 bit10이다',
    '첫 word의 bit42이다',
    '42/32는1이고42%32는10입니다. 숫자 분해된 낮은 word부터 저장합니다.'),
   ('32bit initializer macro 입력이 두 표현에 사용되는가?',
    '그렇다',
    '항상 임시변수로 한 번만 평가한다',
    '원문은 낮은부분과 높은부분 두 initializer 식입니다. 부작용 입력을 단일평가 macro 라고 가정하지 않습니다.')],
  [('원문과 사용 조건', 'BE32의 byte 메모리 순서와 bitmap의 low word 우선 표현을 구분합니다. native32 실행은 별도 검증이 필요합니다.'),
   ('검사 범위',
    'native64 little endian의 선택된 경로를 독립 bit 참조 모델로 비교했습니다. 검색·bitop·mask는 명시적인 검사 문맥 모델이며 모든 '
    'architecture의 실행 증거는 아닙니다.')]),
 ('Bitmap read·word 경계를 넘는 작은 필드 조회',
  'bitmap_read',
  'nbits는1..BITS_PER_LONG의 필드 폭입니다. start의 word 번호와 내부 offset을 구하고 남은 space가 충분하면 shift와 '
  'LAST_WORD_MASK로 읽습니다. 경계를 넘으면 현재 word의 높은 조각과 다음 word의 낮은 조각을 mask 하여 offset과 space에 맞춰 합칩니다. 문서는0 '
  '또는 word 폭 초과의 반환을 undefined라고 하지만 이 원문은 조기 분기로0을 반환합니다.',
  '필드가 실제 배열 안에 있고 경계를 넘을 때 다음 word가 존재하는지 확인합니다. 문서상 유효폭을 지켜 호출합니다. 고정 버전의 invalid폭0 반환을 다른 버전의 API '
  '보장으로 확대하지 않습니다.',
  [('native64 start60,width8 필드는 몇 word를 읽는가?',
    '두 word 다',
    '언제나 한 word 다',
    '첫 word에는 네 bit 공간만 남습니다. 다음 word의 낮은 네 bit와 합칩니다.'),
   ('이 버전의 width65 분기는 실제로 무엇을 반환하는가?',
    '0이다',
    '항상 임의 다음 word를 읽는다',
    '초기 unlikely 조건이 읽기 전에0을 반환합니다. 문서의 유효 API 범위와 실제 분기 증거를 구분합니다.')],
  [('원문과 사용 조건', '독립 bit별 기대 정수와 비교했습니다.0·65폭의 실제 guard도 확인하되 문서 계약의 정상 사용을 권합니다.'),
   ('검사 범위',
    'native64 little endian의 선택된 경로를 독립 bit 참조 모델로 비교했습니다. 검색·bitop·mask는 명시적인 검사 문맥 모델이며 모든 '
    'architecture의 실행 증거는 아닙니다.')]),
 ('Bitmap write·값 폭 제한과 두 word의 바깥 bit 보존',
  'bitmap_write',
  '초기 guard가0 또는 word 폭 초과이면 쓰기 없이 반환합니다. 정상폭은 value에 LAST_WORD_MASK를 AND하여 높은 입력 bit를 버립니다. 한 word에 '
  '들어가면 shifted mask를 지우고 값을 OR합니다. 두 word이면 첫 word의 높은 구간과 다음 word의 낮은 구간을 나누어 clear/OR합니다. 범위 밖 bit는 '
  '산술상 보존하지만 변경 전체의 원자성은 없습니다.',
  '실제 배열 용량과 다음 word 접근을 보장합니다. 초과값을 오류로 거절해야 한다면 호출 전에 별도 숫자 검증을 수행합니다. 이 API의 truncation과 FIELD_PREP '
  '상수 진단을 같은 계약으로 설명하지 않습니다.',
  [('value의 nbits보다 높은 bit는 어떻게 되는가?',
    'mask로 버린다',
    '항상 오류를 반환한다',
    '본문은 value&=mask이고 반환형은void입니다. 폭 초과 숫자를 오류로 알리는 API가 아닙니다.'),
   ('0폭 write가 bitmap을 변경하는가?',
    '아니며 guard에서 반환한다',
    '첫 word전체를0으로 만든다',
    '값 mask 나 주소 갱신 전에 초기 조건을 검사합니다. fixture는 전체 배열 보존을 비교했습니다.')],
  [('원문과 사용 조건',
    'bit별 assign 참조 모델과 전체 word/canary를 비교했습니다. get_value8과 set_value8은 이 읽기·쓰기의 폭8 wrapper 입니다.'),
   ('검사 범위',
    'native64 little endian의 선택된 경로를 독립 bit 참조 모델로 비교했습니다. 검색·bitop·mask는 명시적인 검사 문맥 모델이며 모든 '
    'architecture의 실행 증거는 아닙니다.')]),
 ('Bitmap zero-area wrapper·기본 alignment offset0',
  'bitmap_find_next_zero_area',
  '이 wrapper는 map,size,start,nr,align_mask를 bitmap_find_next_zero_area_off에 전달하고 마지막 align_offset을0으로 '
  '고정합니다. align_mask는2의 거듭제곱보다1 작은 값이며0은 추가 정렬 없음입니다. 본체는 빈 시작 후보를 찾고 정렬한 뒤 nr 길이 안의 설정 bit를 확인합니다. 실패 '
  '결과는 유효한 시작 위치가 아니므로 반환과 size를 대조해야 합니다.',
  '실제 길이와 요청 nr,정렬 mask를 확인합니다. 검색은 공간을 예약하지 않으므로 반환 뒤 설정 단계와 경쟁을 외부 동기화로 보호합니다. offset이 필요한 장치 정렬은 off '
  'API를 선택합니다.',
  [('기본 wrapper가 고정하는 align_offset은?',
    '0이다',
    '항상 size다',
    '본문은 마지막 인자로0을 전달합니다. 별도 offset이 필요한 경우와 기본 정렬을 구분합니다.'),
   ('zero-area 검색 성공만으로 해당 영역이 할당되는가?',
    '아니며 검색과 예약은 별개다',
    '반환 즉시 모든 bit를1로 만든다',
    '본체의 검색은 bitmap을 예약하지 않습니다. 반환 뒤 변경과 동시성 계약이 필요합니다.')],
  [('원문과 사용 조건', '본체의 정렬과 실패 반환 해설은 기존 lib/bitmap.c 수업으로 연결됩니다. wrapper가 새 검색 알고리즘을 추가하는 것은 아닙니다.'),
   ('검사 범위',
    'native64 little endian의 선택된 경로를 독립 bit 참조 모델로 비교했습니다. 검색·bitop·mask는 명시적인 검사 문맥 모델이며 모든 '
    'architecture의 실행 증거는 아닙니다.')]),
 ('Bitmap 할당 선언과 자동 정리·header와 구현의 연결',
  'bitmap_alloc',
  '헤더는 alloc,zalloc,node별 할당과 free,devm 관리형 할당을 선언하며 struct device를 전방 선언합니다. DEFINE_FREE(bitmap, '
  'unsigned long *, if (_T) bitmap_free(_T))는 cleanup 기술에 bitmap 해제를 연결합니다. 실제 메모리 할당과 실패 정리 본체는 '
  'lib/bitmap.c입니다. 선언이 있다는 사실은 자동0초기화나 소유권 이전을 모든 API에 제공하지 않습니다.',
  '0초기화가 필요하면 zalloc과 실제 flags 계약을 선택합니다. 일반free,cleanup 관리,devm 관리의 소유권을 구분하여 중복 해제를 피합니다. node는 NUMA '
  '배치 요청이고 주소 형식의 bit 번호와 다른 개념입니다.',
  [('bitmap_alloc 선언만으로 모든 저장 bit가0인가?',
    '아니며 zalloc의 초기화 계약을 구분한다',
    'alloc과 zalloc은 항상 동일하게0이다',
    '헤더는 별도 API를 선언합니다. lib 본체에서 zalloc이 추가하는 zero flag를 확인해야 합니다.'),
   ('DEFINE_FREE에 해제 연결이 있으면 devm 객체도 직접 두 번 해제해도 되는가?',
    '아니며 소유권과 관리 수명을 확인한다',
    '모든 관리형은 중복free를 자동 무시한다',
    '자동 정리와 devm은 다른 수명 계약입니다. 실제 소유자가 누구인지 확인하여 한 번의 해제를 보장합니다.')],
  [('원문과 사용 조건',
    'include guard와 ASSEMBLY 경계,의존 헤더,전체 함수 선언은 실제 구현과 연결해 읽었습니다. allocator 실행 증거는 기존 구현 fixture 범위와 '
    '구분합니다.'),
   ('검사 범위',
    'native64 little endian의 선택된 경로를 독립 bit 참조 모델로 비교했습니다. 검색·bitop·mask는 명시적인 검사 문맥 모델이며 모든 '
    'architecture의 실행 증거는 아닙니다.')])]

def register(topic,q,detail):
 for title,symbol,principle,use,qa,cards in ROWS:
  topic(title,"라이브러리·알고리즘","include/linux/bitmap.h",symbol,"unsigned long 배열의 비트 집합을 다루는 실제 API를 읽고, 저장 표현과 유효 길이 및 사용 조건을 구분하여 배웁니다.",principle,use,"원문의 상수 분기와 일반 helper 연결을 비교하고 작은 bit 배열 예를 직접 계산하세요.",*(q(*x) for x in qa),details=[detail(*x) for x in cards])
