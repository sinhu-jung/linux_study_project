"""Whole array sizing, containing-object recovery and alignment interfaces."""
ROWS = []


def add(path, title, intro, principle, use, sections, questions):
    ROWS.append(dict(path=path, title=title, intro=intro, principle=principle,
                     use=use, area='객체 배치 · 배열·포인터·컴파일 시 검사',
                     sections=sections, questions=questions))


add('include/linux/array_size.h', '배열 길이 헤더 전체: sizeof 비율과 포인터 오용 검출',
    '배열 저장 크기를 원소 크기로 나누되 포인터를 배열로 착각하는 사용을 막습니다.',
    'ARRAY_SIZE(arr)는 sizeof(arr)/sizeof(arr[0])에 __must_be_array(arr)를 더합니다. 정상 배열에서는 검사 항이 결과 길이를 바꾸지 않고,포인터 오용을 컴파일 단계에서 진단하도록 연결합니다.',
    '함수 매개변수의 int a[]는 포인터로 조정되므로 호출자의 배열 길이를 이 매크로로 복원할 수 없습니다. 포인터와 별도 길이를 전달하는 인터페이스가 필요합니다.',
    [('파일 전체', 'SPDX,_LINUX_ARRAY_SIZE_H guard,compiler.h include,API 주석,매크로 하나,#endif가 전부입니다. __must_be_array의 구현은 포함 계층에 있고 이 파일에는 없습니다.'),
     ('정상 예제', 'int a[7]이면 배열 전체 sizeof는 원소 sizeof의7배라 결과7입니다. int matrix[3][4]이면 첫 차원의 원소가 int[4]라 결과는3이며 전체 정수 개수12가 아닙니다.'),
     ('타입과 실행 범위', '이 매크로는 종료 표식이나 할당 메타데이터를 읽지 않습니다. 문자열 배열에 적용하면 NUL 저장 슬롯도 원소 수에 포함되고,동적 할당 포인터에서는 길이를 알 수 없습니다. sizeof 식의 의미와 배열에서 포인터로의 변환을 구분하는 학습 사례입니다.')],
    [('int matrix[3][4]의 ARRAY_SIZE는?', '3', '12', 'sizeof(matrix[0])은 한 행 int[4]의 크기입니다. 전체 크기를 행 크기로 나눠 첫 차원 길이를 구합니다.'),
     ('malloc으로 받은 포인터만으로 ARRAY_SIZE가 할당 길이를 찾는가?', '아니다. 포인터는 배열 타입 정보와 길이를 보존하지 않는다', '그렇다. 매크로가 할당 헤더를 읽는다', '원문은 sizeof와 컴파일 타입 검사입니다. 런타임 할당 크기를 조회하는 코드가 없습니다.'),
     ('char text[]="abc"의 원소 수는?', '4', '3', '배열은 a,b,c와 종료 NUL을 저장합니다. 문자 길이와 저장 원소 수를 구분합니다.')])

add('include/linux/container_of.h', '포함 객체 주소 복원 전체: 멤버 오프셋과 const 보존',
    '구조체에 내장된 링크나 멤버의 주소에서 바깥 구조체 주소를 복원합니다.',
    'container_of는 멤버 포인터를 임시 void*에 저장하고 타입을 검사한 뒤 offsetof만큼 뺍니다. container_of_const는 _Generic으로 입력의 const 성질에 맞는 반환 타입을 선택합니다.',
    '포인터가 실제 해당 구조체의 지정 멤버를 가리켜야 합니다. 타입이 맞는다는 사실만으로 객체 소유권·수명·멤버 위치까지 증명되지 않습니다.',
    [('파일 전체', 'SPDX,guard,build_bug/stddef include,typeof_member,container_of,container_of_const와 관련 주석,#endif로 구성됩니다. 객체 할당이나 포인터 유효성 런타임 검사는 없습니다.'),
     ('typeof_member', 'typeof(((T*)0)->m)은 구조체 타입 T의 멤버 m 타입을 얻는 표현입니다. 일반 멤버 타입을 조사하는 이 문맥에서 실제 NULL 객체를 생성하거나 읽는 코드로 해석하지 않습니다. 타입 조사와 평가되는 메모리 접근을 구분합니다.'),
     ('타입 검사와 주소 계산', 'static_assert는 ptr가 가리키는 타입과 멤버 타입이 같거나 void 타입이면 허용합니다. 타입이 다르면 컴파일 오류를 유도합니다. __mptr-offset 계산은 GNU void* 바이트 산술을 사용합니다. offsetof는 패딩을 포함한 실제 멤버 위치를 반영하므로 필드 크기를 수동으로 더해 추측할 필요가 없습니다.'),
     ('const 차이', '일반 container_of는 주석대로 const를 잃을 수 있습니다. container_of_const는 const 멤버 포인터이면 const type*를 반환하도록 _Generic 선택을 사용합니다. const를 보존한다고 객체가 유효한지 검사하거나 동시 수정을 막는 것은 아닙니다.'),
     ('침투형 자료구조와 전제', '하나의 객체에 list_head 같은 노드를 내장하면 링크 순회에서 본래 객체를 찾는 데 사용합니다. 같은 타입의 독립 변수 주소를 넘겨도 타입 검사만 통과할 수 있으므로 객체 관계 전제가 중요합니다. 해제된 객체의 멤버,임의 NULL 포인터,잘못된 멤버 지정의 안전성을 보장하지 않습니다.')],
    [('container_of의 타입 검사가 객체 수명까지 확인하는가?', '아니다. 실제 멤버 관계와 수명은 호출자의 전제다', '그렇다. 해제된 객체도 자동 검출한다', 'static_assert는 컴파일 시 타입 관계를 검사합니다. 런타임 할당 상태나 소유권 추적은 없습니다.'),
     ('const 멤버 포인터에서 const 구조체 포인터를 유지하려면?', 'container_of_const를 사용한다', '일반 container_of가 항상 const를 유지한다', '일반 버전은 const를 잃는다는 경고가 있습니다. const 버전은 _Generic으로 반환 형식을 선택합니다.'),
     ('구조체 패딩이 있으면 주소 복원이 불가능한가?', '아니다. offsetof가 실제 멤버 오프셋을 반영한다', '그렇다. 구조체는 packed여야만 한다', '공식은 멤버 주소에서 실제 오프셋을 뺍니다. 연속된 필드 크기 합을 직접 추측하지 않습니다.')])

add('include/linux/align.h', '정렬 경계 헤더 전체: 숫자·포인터 올림과 배수 조건',
    '주소나 크기를 정해진2의 거듭제곱 경계에 맞추는 인터페이스입니다.',
    'ALIGN과 ALIGN_DOWN은 공통 상수 헤더의 정렬식을 사용합니다. 포인터 버전은 unsigned long으로 변환해 계산한 뒤 원래 포인터 타입으로 되돌립니다. IS_ALIGNED는 하위 비트가0인지 검사합니다.',
    'a는 양의2의 거듭제곱이어야 하고 연산 범위도 유효해야 합니다. 주소를 맞췄다고 그 위치에 사용 가능한 저장소가 자동으로 생기는 것은 아닙니다.',
    [('파일 전체', 'SPDX,guard,linux/const.h include,배수 전제 주석,ALIGN/ALIGN_DOWN/__ALIGN_MASK/PTR_ALIGN/PTR_ALIGN_DOWN/IS_ALIGNED의6개 매크로,#endif입니다. 메모리 할당·복사·권한 검사 코드는 없습니다.'),
     ('숫자 예제', 'ALIGN(13,8)은16,ALIGN_DOWN(13,8)은8입니다. 이미 맞는16은 두 식 모두16입니다. IS_ALIGNED(16,8)은참,IS_ALIGNED(13,8)은거짓입니다. 내부 mask는a-1이며 임의 배수6에 같은 비트 공식을 적용하는 계약이 아닙니다.'),
     ('포인터와 타입 폭', 'PTR_ALIGN은 주소를 unsigned long으로 바꾸어 올림한 뒤 typeof(p)로 반환합니다. 대상 커널의 포인터·long 표현 관례가 전제이며 Windows LLP64 같은 다른 ABI에서 그대로 안전하다고 일반화하지 않습니다. 정렬된 반환 주소가 원래 객체 범위를 벗어나지 않는지는 별도 확인해야 합니다.'),
     ('경계와 평가 횟수', '정렬식은 x+mask 등의 산술과 a의 반복 사용을 포함할 수 있습니다. 오버플로·0 배수·부수효과 있는 인자를 자동 검출하지 않습니다. IS_ALIGNED는 단순 비트 검사라 조건이 참이어도 주소 유효성·버퍼 길이·접근 권한은 알 수 없습니다.')],
    [('ALIGN(13,8)과 ALIGN_DOWN(13,8)은?', '16과8', '둘 다13', '양의2의 거듭제곱 배수의 다음·이전 경계를 구합니다. 이미 맞는 값이면 그대로입니다.'),
     ('PTR_ALIGN이 정렬된 주소에 메모리를 할당하는가?', '아니다. 주소값만 계산한다', '그렇다. 필요한 차이만큼 자동 확장한다', '매크로에는 할당이나 버퍼 확장이 없습니다. 정렬 후에도 객체 범위가 충분한지 확인해야 합니다.'),
     ('IS_ALIGNED가 참이면 유효한 읽기 주소라는 뜻인가?', '아니다. 하위 비트 조건만 확인한다', '그렇다. 메모리 매핑까지 검사한다', '주소의 정렬성과 메모리 접근 가능성은 다른 성질입니다. 단순 비트식에는 페이지나 권한 조회가 없습니다.')])
