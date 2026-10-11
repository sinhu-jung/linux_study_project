"""Whole stddef layers, mirrored members and flexible-array wrappers."""
ROWS = []


def add(path, title, intro, principle, use, sections, questions):
    ROWS.append(dict(path=path, title=title, intro=intro, principle=principle,
                     use=use, area='구조체 배치 · union·가변 길이 배열·언어 확장',
                     sections=sections, questions=questions))


add('include/linux/stddef.h', '커널 stddef 전체: 멤버 범위와 구조체 그룹',
    '널 포인터·불리언 상수·멤버 오프셋과 여러 멤버를 하나의 영역으로 다루는 매크로입니다.',
    'UAPI stddef를 포함하고 NULL,false/true,offsetof를 정의합니다. sizeof_field와 offsetofend는 멤버 크기·끝 위치를 구하고 struct_group 계열은 같은 저장소에 직접 접근과 그룹 이름 접근을 제공합니다.',
    '배치 정보를 구하는 매크로는 메모리를 할당하거나 크기를 검사하는 실행 함수가 아닙니다. 패딩과 가변 배열의 저장 공간은 별도로 고려해야 합니다.',
    [('전체 구성', 'SPDX,guard,UAPI include,NULL 재정의,익명 enum의 false0/true1,offsetof 재정의,멤버 크기·끝 위치,struct_group/attr/tagged,DECLARE_FLEX_ARRAY wrapper로 끝납니다. bool typedef 자체는 이 파일에 없습니다.'),
     ('멤버 크기와 끝', 'sizeof_field(T,m)은 해당 멤버 타입의 sizeof이며 일반 멤버에서는 NULL 객체를 실제 읽지 않습니다. offsetofend는 멤버 시작 오프셋과 그 크기의 합입니다. 구조체 뒤쪽 패딩이나 다음 멤버까지의 간격을 더하지 않으므로 항상 sizeof(T)와 같은 것은 아닙니다. bit-field나 불완전 배열처럼 sizeof를 적용할 수 없는 대상에 무조건 사용할 수 없습니다.'),
     ('그룹의 두 접근 방법', 'struct_group(NAME,MEMBERS)는 UAPI __struct_group에 빈 tag와 attributes를 전달합니다. 익명 구조체를 통한 obj.field 접근과 이름 있는 구조체를 통한 obj.NAME.field 접근은 같은 저장소를 가리킵니다. 멤버 데이터를 두 벌 저장하는 구조가 아닙니다.'),
     ('속성과 재사용 태그', 'struct_group_attr는 attributes를 전달하고 struct_group_tagged는 이름 있는 구조체에 재사용할 tag를 전달합니다. 속성은 정렬·배치에 영향을 줄 수 있으므로 그룹 크기를 필드 크기의 단순 합으로 가정하지 않습니다. tag와 객체의 멤버 이름은 서로 다른 역할입니다.'),
     ('유연 배열 선언', 'DECLARE_FLEX_ARRAY는 UAPI __DECLARE_FLEX_ARRAY에 위임합니다. union 안 등에서 유연 배열을 표현하도록 포장하지만 추가 원소 저장 공간을 할당하지 않습니다. 실제 객체 생성 시 필요한 꼬리 공간과 수명·길이 계약을 호출자가 관리합니다.')],
    [('offsetofend가 항상 구조체 전체 sizeof와 같은가?', '아니다. 뒤쪽 멤버와 패딩이 남을 수 있다', '그렇다. 구조체 끝을 무조건 반환한다', '정의는 지정 멤버의 시작 오프셋에 그 멤버 크기만 더합니다. 구조체 전체 크기와는 다릅니다.'),
     ('struct_group의 두 접근 경로는 데이터를 두 번 저장하는가?', '아니다. union 안의 같은 저장소를 공유한다', '그렇다. 동기화된 복사본 두 개를 만든다', '그룹은 이름 없는 구조체와 이름 있는 구조체를 union으로 겹칩니다. 자동 복사나 동기화 코드는 없습니다.'),
     ('DECLARE_FLEX_ARRAY가 필요한 원소 수만큼 메모리를 확보하는가?', '아니다. 선언 형식만 제공한다', '그렇다. 매크로가 동적 배열을 할당한다', '배열 원소 타입·이름만 받는 선언 매크로입니다. 실제 크기 계산과 할당은 다른 코드의 책임입니다.')])

add('include/uapi/linux/stddef.h', 'UAPI stddef 전체: 구조체 그룹과 C·C++ 가변 배열 차이',
    '구조체 배치를 표현하는 공통 매크로와 지원되지 않는 속성의 대체 정의입니다.',
    '__struct_group은 익명·명명 구조체를 union에 겹칩니다. __DECLARE_FLEX_ARRAY는 C와 C++에 서로 다른 확장 문법을 사용하고 counted_by 계열은 미정의인 경우 빈 매크로로 둡니다.',
    '언어 확장과 컴파일러 기능에 의존하므로 모든 ISO C/C++ 컴파일러에 보편적으로 이식되는 자료구조 선언으로 해석하지 않습니다.',
    [('전체 구성', 'SPDX syscall note,guard,compiler_types include,__always_inline fallback,__struct_group,C++/C 유연 배열 분기,__counted_by/__counted_by_le/__counted_by_be fallback,#endif입니다. 런타임 함수는 없습니다.'),
     ('그룹 매크로 전개', 'MEMBERS를 가진 익명 구조체와 TAG 및 NAME이 있는 구조체를 같은 union 안에 선언합니다. ATTRS는 두 구조체와 바깥 union 모두에 붙습니다. 멤버 선언을 두 번 쓰지만 저장 공간은 union의 겹침 규칙을 따릅니다.'),
     ('C와 C++ 분기', 'C 경로는 이름 있는 빈 구조체 멤버 __empty_NAME과 TYPE NAME[]를 가진 익명 구조체로 감쌉니다. C++에서는 빈 구조체의 크기가1이므로 이 경로를 쓰지 않고 T member[0]을 사용합니다.0길이 배열도 구현 확장 문법이며 실제 배열 원소 저장소를 제공하지 않습니다.'),
     ('fallback 속성', '__always_inline이 없으면 inline만 정의합니다. 강제 인라인 속성을 새로 만들어 붙이는 것이 아닙니다. counted_by,le,be도 이미 정의되어 있으면 보존하고 없을 때만 빈 매크로를 제공합니다. 빈 대체 정의는 런타임 길이 검사나 엔디언 변환을 수행하지 않습니다.'),
     ('CS 연결', '전처리 기능 탐지,언어별 객체 크기 차이,익명 union의 공유 배치,속성 지원과 실제 검사의 차이를 학습합니다. 소스가 컴파일된다는 사실만으로 길이 추적 기능이 활성화되었다고 주장하지 않습니다.')],
    [('C++ 경로에서 C의 빈 구조체 포장을 그대로 쓰지 않는 이유는?', '빈 구조체 크기가1이어서 같은 배치를 만들지 못하기 때문이다', 'C++에는 어떤 구조체도 없기 때문이다', '원문 주석이 sizeof(struct{})의 차이를 설명하고0길이 배열 경로를 따로 둡니다.'),
     ('빈 __counted_by fallback이 배열 길이를 런타임에 검사하는가?', '아니다. 지원되지 않을 때 문법을 수용하는 빈 정의다', '그렇다. 모든 접근마다 검사 함수를 호출한다', '매크로 본문이 비어 있습니다. 실제 속성 지원 여부와 선언의 존재를 구분해야 합니다.'),
     ('이미 __always_inline이 정의되어 있으면 덮어쓰는가?', '아니다. #ifndef로 기존 정의를 보존한다', '그렇다. 반드시 단순 inline으로 바꾼다', 'fallback은 정의가 없는 경우에만 적용됩니다. 다른 계층이 제공한 속성을 유지합니다.')])
