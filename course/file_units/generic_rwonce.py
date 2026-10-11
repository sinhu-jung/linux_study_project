"""Whole generic READ_ONCE and WRITE_ONCE header."""
ROWS = [dict(
    path='include/asm-generic/rwonce.h',
    title='READ_ONCE 전체: compiler 접근 보존과 원자성의 경계',
    intro='한 번의 관찰을 표현하는 매크로의 크기 검사, volatile 접근과 검사 제외 helper를 해설합니다.',
    principle='접근의 병합·재읽기를 막는 compiler 계약과 여러 CPU 사이의 순서·원자성은 구분해야 합니다.',
    use='앞서 읽은 acquire/release 구현에서 READ_ONCE와 WRITE_ONCE가 맡는 역할을 확인합니다.',
    area='컴파일러 최적화 · volatile · 원자성 · 타입 크기 · sanitizer',
    sections=[
        ('주석과 파일 구조', 'GPL-2.0, 목적 설명, guard와 비어셈블리 분기, compiler_types·KASAN·KCSAN 헤더, 크기 검사와 읽기·쓰기 매크로, 두 helper로 구성됩니다. 주석은 같은 CPU의 process와 IRQ/NMI 통신 및 별도 장벽·원자 명령과 함께 접근을 보존하는 용도를 듭니다.'),
        ('순서 설명의 조건', '주석은 compiler가 특정 순서를 인지할 때 연속 READ_ONCE/WRITE_ONCE의 순서를 보존한다고 설명하며 서로 다른 C 문장 배치를 예로 듭니다. 이것을 CPU의 acquire/release나 full barrier와 동일시하지 않습니다. 일반 접근까지 모두 고정하는 전역 compiler barrier 본문도 아닙니다.'),
        ('허용 크기', 'compiletime_assert_rwonce_type은 __native_word(t)이거나 sizeof(t)==sizeof(long long)인지 정적 검사합니다. 주석에 struct/union도 언급되지만 public 매크로의 크기 제한은 그대로 적용됩니다. 임의 크기 구조체를 잠금 없이 통째로 원자 복사한다고 설명하면 틀립니다.'),
        ('32비트에서64비트', '검사는32비트 아키텍처에서도64비트 크기를 허용합니다. 주석은 Armv7+LPAE 같은 원자 접근 사례와 둘의32비트 접근으로 쪼개질 수 있는 사례를 구분합니다. 따라서 크기 검사를 통과했다는 사실만으로 모든 아키텍처에서 torn read가 불가능함을 증명하지 못합니다.'),
        ('읽기 확장', '__READ_ONCE가 없으면 &(x)를 const volatile의 __unqual_scalar_typeof(x) 포인터로 변환해 역참조합니다. READ_ONCE는 크기 검사 뒤 이를 사용합니다. 내부 __READ_ONCE를 직접 쓰면 public 크기 검사를 거치지 않으며 주석도 tearing 가능성을 경고합니다. 타입 변환은 주소 유효성을 검사하지 않습니다.'),
        ('쓰기 확장', '__WRITE_ONCE는 &(x)를 volatile typeof(x) 포인터로 바꿔 val을 저장하는 do-while입니다. WRITE_ONCE는 먼저 같은 크기 검사를 합니다. 이 버전의 쓰기 매크로는 값 반환 식이 아니며 READ_ONCE와 WRITE_ONCE를 이어 붙여도 원자적 read-modify-write가 되지 않습니다.'),
        ('검사 없는 한 word 읽기', '__read_once_word_nocheck는 __no_sanitize_or_inline 속성을 사용하며 unsigned long 포인터의 __READ_ONCE 결과를 반환합니다. READ_ONCE_NOCHECK는 sizeof(x)==sizeof(unsigned long)을 정적 검사하고 helper의 결과를 typeof(x)로 변환합니다. 주석은 실행 중 프로세스의 스택 unwind처럼 KASAN/KCSAN에 알리지 않고 word를 읽는 용도를 설명합니다. NOCHECK가 타입·크기 검사까지 모두 없다는 뜻은 아닙니다.'),
        ('한 word씩 읽는 helper', 'read_word_at_a_time은 __no_kasan_or_inline 속성을 사용하고 kasan_check_read(addr,1) 뒤 unsigned long 포인터를 일반 역참조합니다. 명시적 검사는1바이트이고 반환 접근은 한 word라는 차이가 핵심입니다. 이것은 READ_ONCE_NOCHECK의 별칭도 아니며 임의의 잘못된 주소·정렬·페이지 경계를 자동으로 안전하게 만드는 함수도 아닙니다.'),
        ('CS 연결과 제한', 'lvalue 주소, 타입 한정자, volatile 접근, 정적 단언, compiler 최적화와 CPU 원자성의 차이, 계측 제외를 학습합니다. 실제 안전성 판단은 대상 아키텍처의 rwonce 재정의와 정렬·수명·호출 문맥까지 필요합니다. 이 파일 해설은 해당 조건의 전수 실행 검증이 아닙니다.')
    ],
    questions=[
        ('32비트 환경에서 READ_ONCE의64비트 크기 검사를 통과하면 반드시 단일 원자 접근인가?', '아니다. 아키텍처에 따라 나뉜 접근이 가능하다', '그렇다. 정적 검사가 CPU 명령을 새로 만든다', '허용 크기에는 long long이 포함되지만 주석은 원자성을 지원하는 사례와 분할 접근 사례를 구분합니다. 허용 여부와 하드웨어 보장은 별개입니다.'),
        ('READ_ONCE_NOCHECK가 허용하는 크기는?', 'unsigned long과 같은 크기이다', '모든 크기의 배열이다', '전용 compiletime_assert가 sizeof(x)==sizeof(unsigned long)을 요구합니다. NOCHECK는 sanitizer 관련 문맥이며 크기 제한 제거가 아닙니다.'),
        ('read_word_at_a_time의 명시적 KASAN 검사 크기와 읽기 크기는?', '검사는1바이트, 읽기는 unsigned long 크기이다', '둘 다 항상1바이트이다', 'kasan_check_read(addr,1) 다음 *(unsigned long *)addr를 반환합니다. 본문에 나타난 두 크기를 구별해야 합니다.'),
        ('WRITE_ONCE(x,READ_ONCE(x)+1)은 원자 증가 연산인가?', '아니다. 읽기와 쓰기가 분리된 연산이다', '그렇다. 두 ONCE를 합치면 자동 잠금이 생긴다', '각 접근의 compiler 처리를 제약할 뿐 결합된 read-modify-write를 제공하지 않습니다. 동시 실행에서 두 수행자가 같은 이전 값을 읽을 수 있습니다.')
    ]
)]
