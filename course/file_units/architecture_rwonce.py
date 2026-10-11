"""Whole ARM64 and Alpha overrides of the generic read-once primitive."""
ROWS = [dict(
    path='arch/arm64/include/asm/rwonce.h',
    title='ARM64 READ_ONCE 전체: LTO와 주소 의존성 보호',
    intro='LTO 구성에서 RCpc acquire 읽기를 제공하는 크기별 asm과 generic 계층 연결을 해설합니다.',
    principle='compiler 변환이 주소 의존성을 약하게 만들 수 있는 상황을 아키텍처 읽기 명령으로 보완합니다.',
    use='공통 rwonce.h와 비교하며 모든 ARM64 빌드에 동일한 override가 적용되는 것은 아님을 확인합니다.',
    area='LTO · 주소 의존성 · RCpc acquire · 인라인 asm · 타입 크기',
    sections=[
        ('파일 구성과 세 조건', 'GPL-2.0·저작권·guard 뒤 CONFIG_LTO이면서 비어셈블리일 때 compiler_types.h와 alternative-macros.h를 포함합니다. 그 안에서도 BUILD_VDSO가 아닐 때만 명령 생성과 __READ_ONCE를 정의합니다. 마지막 asm-generic/rwonce.h 포함은 이 조건들 밖에 있습니다. 비LTO 또는 VDSO에서는 이 파일의 override가 생기지 않습니다.'),
        ('LTO에 대한 설계 이유', '주석은 LTO에서 READ_ONCE가 시작한 주소 의존성을 compiler가 제어 의존성으로 바꿀 위험이 커진다고 설명합니다. CPU가 허용하는 순서가 달라져 문제가 될 수 있으므로 LTO 빌드의 읽기에 RCpc acquire 의미를 제공합니다. 주석은 위험의 증가를 설명하며 모든 LTO 최적화가 반드시 이런 변환을 한다고 단정하지 않습니다.'),
        ('명령 선택의 두 단계', 'CONFIG_AS_HAS_LDAPR가 있으면 __LOAD_RCPC는 기본 ldar와 rcpc 확장 지정 뒤 ldapr를 ALTERNATIVE로 구성하며 ARM64_HAS_LDAPR를 기능 조건으로 사용합니다. assembler 지원 구성과 실제 CPU 기능 선택은 다른 단계입니다. assembler 지원이 없으면 ldar 문자열만 생성합니다. 컴파일 옵션 하나만으로 모든 CPU에서 ldapr를 실행한다고 설명하면 틀립니다.'),
        ('주소와 결과 보관', '__READ_ONCE는 &(x)를 typeof(&(x))의 __x에 보관하고 int atomic을1로 초기화합니다. 결과 union은 원래 값의 한정자를 제거한 __val과 char __c[1] 뷰를 가집니다. union의 전체 크기는 char 배열 길이1만으로 정해지는 것이 아니라 다른 멤버까지 반영합니다. atomic이라는 이름은 여기의 지역 분기 표지이며 atomic_t 객체나 런타임 원자성 검사가 아닙니다.'),
        ('1·2바이트 읽기', 'sizeof(x)가1이면 b 접미사와 %w0를,2이면 h 접미사와 %w0를 사용합니다. 출력은 __u.__c를 각각 __u8·__u16 포인터로 보아 기록합니다. 입력은 Q 제약의 *__x, 출력은 레지스터 제약, clobber는 memory입니다. volatile asm과 명령 선택이 실제 접근을 표현합니다.'),
        ('4·8바이트 읽기', '4바이트는 접미사 없이 %w0와 __u32 결과 뷰를 사용하고8바이트는 %0와 __u64를 사용합니다. 네 경우 모두 성공 분기에서 break합니다. 최종 conditional expression은 atomic이 참이면 union의 __val을 원래 대상 타입으로 변환하여 반환합니다. 별도의 값 재읽기는 하지 않습니다.'),
        ('그 밖의 크기와 generic 검사', 'default는 atomic=0으로 바꿉니다. 이때 마지막 식의 다른 피연산자인 (*(volatile typeof(__x))__x)를 선택하므로 그 경로에는 __LOAD_RCPC 명령이 없습니다. 이 표현의 typeof(__x)는 포인터 타입이라는 점도 유의해야 합니다. 모든 fallback이 같은 acquire 보장을 준다고 설명하지 않습니다. public READ_ONCE는 뒤에 포함한 generic 헤더의 크기 검사를 거치며 내부 __READ_ONCE 직접 사용과 구별해야 합니다.'),
        ('공통 계층과 분업', 'generic 헤더는 __READ_ONCE가 이미 있으면 이를 유지하고 public READ_ONCE와 WRITE_ONCE 등의 공통 인터페이스를 제공합니다. 이 ARM64 파일은 WRITE_ONCE를 별도로 재정의하지 않습니다. 읽기 구현이 강화됐다고 저장도 자동으로 release가 된다고 추론하면 안 됩니다.'),
        ('CS 연결과 범위', '주소 의존성과 제어 의존성, 링크 시간 최적화, assembler와 CPU 기능 분리, union 표현, 조건부 평가와 명령 폭을 학습합니다. 이 소스 해설은 모든 ARM64 CPU에서 실행한 시험이나 RCpc를 full barrier와 동일시하는 설명이 아닙니다.')
    ],
    questions=[
        ('CONFIG_LTO가 켜져도 BUILD_VDSO이면 이 파일의 __READ_ONCE override가 정의되는가?', '아니다. BUILD_VDSO가 아닌 경우만 정의한다', '그렇다. LTO 조건 하나로 충분하다', '바깥 LTO·비어셈블리 조건 안에 별도의 #ifndef BUILD_VDSO가 있습니다. 마지막 generic 헤더는 계속 포함됩니다.'),
        ('CONFIG_AS_HAS_LDAPR가 있으면 기본 명령도 무조건 ldapr인가?', '아니다. ldar와 ldapr 대체를 CPU 기능 조건과 함께 구성한다', '그렇다. 모든 ldar 문자열을 제거한다', 'ALTERNATIVE의 첫 문자열은 ldar이며 ARM64_HAS_LDAPR 조건의 대체 문자열이 ldapr입니다. assembler 지원과 CPU 지원은 구분해야 합니다.'),
        ('8바이트 경로의 출력 레지스터 표기는?', '%0이다', '%w0이다', '1·2·4바이트 경로는 %w0,8바이트 경로는 %0입니다. 출력 저장 뷰도 각각 크기에 맞춰 __u8/__u16/__u32/__u64를 사용합니다.'),
        ('지역 변수 atomic이0이 되는 것은 무엇을 의미하는가?', '크기 switch의1·2·4·8에 해당하지 않았다는 뜻이다', 'CPU가 원자성 실패를 런타임으로 보고했다는 뜻이다', 'default에서만0을 대입합니다. 메모리 경쟁 검출 결과나 원자 연산 반환값이 아니라 구현 경로 선택용 표지입니다.')
    ]
), dict(
    path='arch/alpha/include/asm/rwonce.h',
    title='Alpha READ_ONCE 전체: 주소 의존 읽기 뒤 장벽',
    intro='SMP Alpha에서 관찰값을 읽은 뒤 mb를 붙이는 짧은 아키텍처 override를 해설합니다.',
    principle='주소 의존성을 유지하는 compiler 접근만으로 부족한 하드웨어에는 추가 순서 장벽이 필요할 수 있습니다.',
    use='ARM64의 LTO 조건부 acquire 읽기 및 공통 volatile 접근과 대조합니다.',
    area='주소 의존성 · SMP · 메모리 장벽 · volatile · 계층별 재정의',
    sections=[
        ('파일 전체 구조', 'GPL-2.0·저작권·guard 뒤 CONFIG_SMP에서 asm/barrier.h를 포함하고 __READ_ONCE를 재정의합니다. CONFIG_SMP 조건이 끝난 다음 asm-generic/rwonce.h를 포함합니다. 별도의 쓰기 매크로나 함수 정의는 없습니다.'),
        ('설계 근거 주석', '일부 Alpha CPU 구현은 주소 의존 읽기를 재정렬할 수 있으므로 READ_ONCE에 memory barrier를 추가한다고 주석이 설명합니다. 주석에 추가 읽을거리로 perfbook 링크가 있지만 이 학습 단위는 로컬 소스의 설명과 본문을 근거로 하며 외부 책 전체를 검토한 것으로 세지 않습니다.'),
        ('값을 먼저 보관', '매크로는 __unqual_scalar_typeof(x)의 __x에 volatile 포인터 역참조로 읽은 값을 저장합니다. 다음 mb를 실행하고 마지막에 저장한 __x를 typeof(x)로 변환하여 반환합니다. mb 다음 대상을 다시 읽는 것이 아니므로 값 관찰 시점은 장벽 앞입니다.'),
        ('SMP 조건과 generic 연결', 'SMP에서는 generic 헤더가 이미 정의된 __READ_ONCE를 보존하고 public READ_ONCE의 타입 크기 검사 등과 조합합니다. 비SMP에서는 여기의 override가 없으므로 generic 기본값으로 이어집니다. 이 파일만으로 mb의 실제 명령 바이트를 확인한 것은 아니며 해당 정의는 asm/barrier.h에 있습니다.'),
        ('CS 연결', 'compiler 접근 보존과 CPU 의존성 순서, 관찰값의 지역 보관, 메모리 모델 차이에 따른 override를 학습합니다. READ_ONCE 뒤 장벽이 있다는 사실이 복합 read-modify-write를 원자적으로 만들거나 대상 객체 수명을 보장하지는 않습니다.')
    ],
    questions=[
        ('SMP Alpha 매크로에서 mb는 실제 읽기 전인가 뒤인가?', 'volatile 읽기 뒤이다', '읽기 전에만 있다', '읽은 값을 __x에 담은 다음 mb를 수행하고 저장한 값을 반환합니다. 반환 직전에 다시 읽지 않습니다.'),
        ('비SMP Alpha에도 이 파일이 같은 __READ_ONCE를 강제하는가?', '아니다. 재정의는 CONFIG_SMP 안에 있다', '그렇다. generic 헤더 포함이 항상 SMP 정의를 만든다', '조건 밖에서는 generic 헤더를 포함할 뿐이며 이 아키텍처 override는 정의되지 않습니다.'),
        ('장벽 뒤 반환하는 값은?', '장벽 전에 보관한 __x이다', '대상 메모리를 다시 읽은 값이다', '마지막 식은 (typeof(x))__x입니다. memory barrier의 존재와 재읽기를 혼동하지 않아야 합니다.')
    ]
)]
