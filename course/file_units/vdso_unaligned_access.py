"""Whole-file typed unaligned access primitives for vDSO code."""
ROWS = [dict(
    path='include/vdso/unaligned.h',
    title='vDSO unaligned 접근: packed 멤버와 표현식 매크로',
    intro='읽기·쓰기 매크로 전체를 분석하고 주소 정렬, byte order, 원자성을 구별합니다.',
    principle='정렬 요구를 완화한 자료형 접근은 주소 유효성 검사나 endian 변환, 원자적 접근을 대신하지 않습니다.',
    use='GNU C statement expression과 do-while 매크로, 익명 packed 구조체를 해석합니다.',
    area='메모리 정렬 · packed · GNU C · typeof · 매크로 · endian · 원자성',
    sections=[
        ('파일 전체와 의존성', 'GPL-2.0과 __VDSO_UNALIGNED_H guard 아래 __get_unaligned_t와 __put_unaligned_t 두 매크로만 있습니다. include나 함수 정의는 없습니다. __packed와 GNU C 확장 문법을 제공하는 컴파일 문맥에 의존합니다. 이 파일만으로 범용 표준 C 라이브러리 인터페이스가 되는 것은 아닙니다.'),
        ('읽기 매크로의 임시 포인터', '__get_unaligned_t(type,ptr)는 ({ ... }) statement expression 안에 const struct { type x; } __packed *__pptr를 선언합니다. ptr를 typeof(__pptr)로 변환하여 그 포인터에 저장합니다. __pptr는 호출자의 원래 포인터 변수를 바꾸는 것이 아니라 매크로 내부의 임시 변수입니다. 입력 ptr 식은 초기화 위치에 한 번 나타납니다.'),
        ('읽기 결과와 const', 'statement expression의 마지막 표현식 __pptr->x가 읽은 값을 돌려줍니다. 따라서 x의 자료형은 명시한 type입니다. const는 이 포인터를 통한 멤버 쓰기를 금지하는 타입 제약이며 다른 주체가 메모리를 바꾸지 못하게 잠그는 속성이 아닙니다. 매크로는 NULL 검사나 접근 가능한 길이 확인을 하지 않습니다.'),
        ('쓰기 매크로와 문장 형태', '__put_unaligned_t(type,val,ptr)는 const가 없는 packed 구조체 포인터를 만들고 __pptr->x=(val)을 수행합니다. do { ... } while (0)로 감싸 호출 뒤 세미콜론을 붙이는 하나의 문장처럼 사용합니다. 읽기 매크로처럼 값 반환 표현식이 아니며 val 식도 본문에서 한 번만 사용됩니다. type에 맞는 대입 변환은 발생할 수 있습니다.'),
        ('Packed의 역할', '멤버가 하나인 packed 구조체를 통해 컴파일러에 자연 정렬을 가정할 수 없는 접근임을 표현합니다. 출력 명령이 항상 단일 load/store라는 보장은 없으며 아키텍처와 컴파일러에 따라 필요한 접근을 선택할 수 있습니다. packed가 잘못된 주소를 유효하게 만들거나 페이지 fault를 방지하는 것은 아닙니다.'),
        ('Endian과 원자성은 별개', '이 매크로는 type의 native 표현으로 읽고 씁니다. little-endian이나 big-endian 변환 함수를 호출하지 않습니다. 예를 들어 메모리 바이트 01 02를 u16으로 읽는 숫자는 시스템 byte order에 따라 달라집니다. atomic 연산·READ_ONCE·WRITE_ONCE·메모리 장벽도 없으므로 여러 스레드와 공유한 값을 원자적으로 읽는다는 보장을 만들지 않습니다.'),
        ('난수 복사와 범위', '확인한 lib/vdso/getrandom.c는 이 helper로 u64·u32·u16·u8 값을 복사한 뒤 원본에 0을 기록합니다. 같은 native type으로 읽어 같은 type으로 쓰므로 이 사용에서는 byte order를 바꾸려는 목적이 아닙니다. 복사 길이 반복과 원본 지우기는 호출부가 구현합니다. 두 매크로 전체를 대조했으며 실제 비정렬 주소의 아키텍처별 명령·동시 접근·fault 동작을 실행 검증한 결과는 아닙니다.')
    ],
    questions=[
        ('__get_unaligned_t(u16,p)가 항상 little-endian 숫자를 반환하는가?', '아니다. 별도 endian 변환 없이 native type으로 읽는다', '그렇다. unaligned라는 이름이 little-endian을 뜻한다', '주소 정렬과 byte order는 다른 문제입니다. 본문에는 byte swap이나 le 변환이 없습니다.'),
        ('__packed를 사용하면 다른 CPU와의 접근도 원자적인가?', '그렇게 보장할 수 없다. 이 매크로에는 atomic 연산이나 장벽이 없다', '그렇다. packed는 구조체 전체를 자동으로 잠근다', 'packed는 배치와 정렬 가정을 다룹니다. 동시성의 원자성·가시성은 별도 계약이 필요합니다.'),
        ('읽기와 쓰기 매크로의 형태는 어떻게 다른가?', '읽기는 값을 내는 statement expression이고 쓰기는 do-while 문장이다', '둘 다 ssize_t를 반환하는 외부 함수이다', '읽기의 마지막 표현식이 결과가 됩니다. 쓰기는 대입을 수행하는 문장으로 감싸져 있으며 별도 함수 심볼을 정의하지 않습니다.')
    ]
)]
