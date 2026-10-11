"""Whole common speculation-safe index interface."""
ROWS = [dict(
    path='include/linux/nospec.h',
    title='NOSPEC 인덱스 전체: 범위 검사 뒤 마스크와 타입 경계',
    intro='투기 실행 중 인덱스 사용을 제한하는 공통 마스크와 아키텍처별 재정의 지점을 읽습니다.',
    principle='분기에서 검사한 인덱스와 실제 접근에 사용하는 인덱스 사이에 데이터 의존성을 만듭니다. 정상적인 범위 검사와 객체 수명 관리는 계속 필요합니다.',
    use='x86의 cmp/sbb 마스크와 이 공통 산술 마스크를 비교하고 결과값을 실제 배열 접근에 적용하는 위치를 학습합니다.',
    area='투기 실행 · 비트 마스크 · unsigned 산술 · 타입 검사 · 선언과 구현',
    sections=[
        ('파일 구성', 'GPL-2.0, 저작권, guard 뒤 compiler.h와 asm/barrier.h를 포함하고 task_struct를 전방 선언합니다. 기본 투기 장벽, 마스크 함수, 인덱스 정제 매크로, prctl과 seccomp 관련 세 함수 선언으로 끝납니다. 제어 정책의 실제 구현은 이 파일에 없습니다.'),
        ('아키텍처 우선', 'barrier_nospec가 없을 때만 빈 do-while 기본값을 둡니다. array_index_mask_nospec 역시 아키텍처가 정의하지 않았을 때만 공통 함수를 제공합니다. 따라서 x86의 asm/barrier.h가 제공한 cmp/sbb 구현이 있으면 아래 산술 함수로 덮어쓰지 않습니다. 빈 기본 장벽을 모든 플랫폼의 투기 차단 명령이라고 설명하면 틀립니다.'),
        ('Compiler의 가정 감추기', '공통 함수는 unsigned long index,size를 받고 OPTIMIZER_HIDE_VAR(index)를 호출합니다. 주석은 compiler가 정상 실행의 bounds check로 마스크가 불필요하다고 생각해도 투기 실행의 값을 고려하지 않으므로 마스크를 계산·생성하게 해야 한다고 설명합니다. 이것은 범위 검사의 결과를 변경하는 API가 아닙니다.'),
        ('산술 식의 단계', '반환 식은 ~(long)(index | (size - 1UL - index)) >> (BITS_PER_LONG - 1)입니다. 먼저 unsigned long 산술로 남은 범위 길이 size-1-index를 만들고 index와 OR합니다. long으로 변환한 값을 반전한 뒤 커널이 사용하는 signed 산술 우측 시프트로 최상위 비트를 펼칩니다. 둘 중 최상위 비트가 켜지면 최종 mask는0이며 둘 다 꺼지면 모든 비트1입니다.'),
        ('작은 수 예제', 'size=8,index=3이면 size-1-index=4이고 OR 결과7의 부호 비트가0이라 mask는 모든 비트1입니다. index=8이면 차이가 unsigned 최대값으로 wrap되어 mask0입니다. index=0,size=0 역시 size-1이 unsigned 최대값이므로 mask0입니다. 유효 인덱스는 유지되고 범위 밖 값은 AND 결과0이 됩니다.'),
        ('전체 unsigned 범위에 대한 주의', '공통 산술 식은 index 자체의 최상위 비트도 검사합니다. 따라서 주석의 index<size 설명을 모든 unsigned long 조합에 대한 정확한 비교 함수로 일반화하면 안 됩니다. 예를 들어 index의 최상위 비트가1이면 size가 더 커도 mask0입니다. index=0,size=ULONG_MAX도 차이의 최상위 비트 때문에0입니다. 통상적인 객체 인덱스 범위에서 사용하는 보수적인 마스킹과 임의 정수 비교를 구별하고 아키텍처 재정의의 차이도 확인합니다.'),
        ('매크로의 평가와 타입', 'array_index_nospec는 typeof(index)의 _i와 typeof(size)의 _s를 각각 전달값으로 초기화하고 mask를 계산합니다. BUILD_BUG_ON은 두 타입이 long보다 크면 빌드를 막습니다. 마지막으로 _i & _mask를 원래 인덱스 타입으로 변환해 반환합니다. 크기 검사는 signed 음수나 배열 객체의 유효성을 런타임에 검사하지 않습니다.'),
        ('호출 위치와 반환값 사용', '주석 예제는 if(index<size) 안에서 index=array_index_nospec(index,size)로 대입한 뒤 array[index]를 읽습니다. 정제 함수를 호출만 하고 반환값을 버리면 뒤의 원래 인덱스 접근에 마스크가 반영되지 않습니다. out-of-bounds 값을 마지막 원소 size-1로 포화시키는 clamp가 아니라 AND로0을 만드는 방식입니다.'),
        ('빈 배열과 별도 안전 조건', 'size=0에서 반환 인덱스가0이어도 유효한 원소는 없습니다. 정상 실행의 bounds check를 없애고 무조건 array[0]에 접근해도 된다는 뜻이 아닙니다. 객체 생존 기간, 접근 권한, signed 입력의 하한 검사, 다른 투기 유출 경로도 이 매크로 하나가 해결하지 않습니다.'),
        ('제어 API 선언', 'arch_prctl_spec_ctrl_get은 task와 which를 받아 int를 반환하고 set은 ctrl 인자를 추가로 받습니다. arch_seccomp_spec_mitigate는 task를 받아 void를 반환합니다. 주석상 각각 prctl 투기 제어와 seccomp 강제 완화 관련 인터페이스입니다. 이 헤더에는 지원 값·오류 코드·완화 정책의 본문이 없으므로 선언만으로 정책이 활성화된다고 주장하지 않습니다.'),
        ('CS 연결과 범위', '모듈러 산술, signed/unsigned 변환, 부호 비트 확장, bitwise AND, 타입 폭 검사, compiler 최적화의 실행 모델과 CPU 투기의 차이를 학습합니다. 이 해설은 특정 CPU에서 모든 공격 시나리오를 검증한 보안 증명이 아닙니다.')
    ],
    questions=[
        ('size=8,index=8의 공통 산술 마스크와 정제 인덱스는?', 'mask0, 인덱스0이다', 'mask 전부1, 인덱스8이다', 'size-1-index가 unsigned 최대값으로 wrap되어 OR의 최상위 비트가 켜집니다. 반전·산술 우측 시프트 결과0이며8&0은0입니다.'),
        ('size=0에서 정제 인덱스0을 얻으면 array[0] 접근이 유효한가?', '아니다. 빈 배열에는 유효한 원소가 없다', '그렇다.0은 모든 배열에 존재한다', '마스킹은 객체를 생성하거나 크기를 늘리지 않습니다. 정상 bounds check를 유지해야 하며0 반환을 접근 허가로 해석하면 안 됩니다.'),
        ('x86이 array_index_mask_nospec를 정의했으면 공통 함수도 추가 정의되는가?', '아니다. #ifndef로 제외된다', '그렇다. 두 함수를 순서대로 호출한다', 'asm/barrier.h를 먼저 포함한 뒤 정의 존재를 검사합니다. 아키텍처 구현과 공통 fallback을 연속 실행하는 구조가 아닙니다.'),
        ('공통 함수는 최상위 비트가1인 index<size인 경우에도 항상 전부1 mask를 주는가?', '아니다. index의 최상위 비트 때문에0일 수 있다', '그렇다. 임의 unsigned 비교와 완전히 같다', 'OR에 index 자체가 포함됩니다. 이 산술 fallback은 전체 unsigned 범위에 대한 일반 비교 함수로 쓰면 안 됩니다. 아키텍처 재정의와도 차이가 있습니다.'),
        ('array_index_nospec(index,size)를 호출하고 결과를 버리면 원래 index가 수정되는가?', '아니다. 반환값을 접근에 사용해야 한다', '그렇다. 매크로가 호출자 변수를 무조건 덮어쓴다', '_i는 매크로의 지역 변수이고 마지막 식이 정제 값을 반환합니다. 원문의 예제처럼 대입하거나 반환값을 배열 인덱스로 사용해야 합니다.')
    ]
)]
