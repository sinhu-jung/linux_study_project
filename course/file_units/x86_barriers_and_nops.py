"""Whole x86 barrier and NOP encoding headers."""
ROWS = [dict(
    path='arch/x86/include/asm/barrier.h',
    title='x86 장벽 전체: 잠금 명령·compiler barrier·투기 제한',
    intro='32비트 대체 명령부터 nospec mask와 acquire/release까지 각 정의를 비교합니다.',
    principle='x86에서도 full ordering, compiler ordering, 투기 실행 제한은 동일한 기능이 아닙니다.',
    use='공통 barrier.h의 기본값이 이 아키텍처 정의와 결합되는 과정을 읽습니다. 실제 CPU 실행 및 모든 메모리 타입의 검증은 아닙니다.',
    area='메모리 모델 · x86 명령 · 투기 실행 · 비교 플래그 · 조건부 패치',
    sections=[
        ('전체 구조', 'GPL-2.0, include guard, alternative.h와 nops.h 포함, 기본 장벽, nospec mask, DMA/SMP 장벽, acquire/release, 원자 연산·주소 공간 전환 특례 뒤 asm-generic/barrier.h를 포함합니다. 장치 통신에는 UP에서도 엄격한 순서가 필요할 수 있다는 주석이 있습니다.'),
        ('32비트 기본 장벽', 'CONFIG_X86_32에서는 mb/rmb/wmb를 직접 정의합니다. ALTERNATIVE의 기본 문자열은 lock; addl $0,-4(%esp)이고 X86_FEATURE_XMM2 대체 문자열은 각각 mfence/lfence/sfence입니다. volatile asm은 memory와 cc clobber를 선언합니다. 별도의 C if문으로 매번 기능을 검사하는 형태가 아니며 실제 패치 메커니즘은 alternative 구현의 범위입니다.'),
        ('64비트 쪽 정의', 'CONFIG_X86_32가 아니면 __mb/__rmb/__wmb를 각각 mfence/lfence/sfence와 memory clobber로 정의합니다. 공개 이름이 아니라 내부 이름을 제공하므로 마지막 generic 헤더의 KCSAN 래퍼와 연결됩니다. 32비트 쪽과 공개 이름을 제공하는 방식부터 다릅니다.'),
        ('인덱스 타입과 unsigned 비교', 'array_index_mask_nospec는 typeof(idx+sz)로 __idx와 __sz 타입을 맞추고 unsigned long mask를 반환합니다. cmp %1,%2는 AT&T 피연산자 순서상 __idx에서 __sz를 뺀 비교 플래그를 만듭니다. sbb mask,mask는 carry가 있으면 모든 비트1,없으면0을 만듭니다. 즉 unsigned index<size에 대응하는 마스크이며 signed 음수 비교를 별도로 구현하지 않습니다.'),
        ('마스크의 경계', 'index==size이면 borrow가 없어0이고 index<size이면0에서 carry1을 빼 unsigned long의 모든 비트1입니다. 이 매크로는 배열을 읽거나 인덱스를 직접 수정하지 않습니다. 호출자가 반환 마스크를 사용해야 하며 단순히 호출하고 버리는 것으로 배열 접근을 안전하게 만들지 않습니다.'),
        ('투기 장벽', 'barrier_nospec는 기본 빈 문자열을 X86_FEATURE_LFENCE_RDTSC 조건에서 lfence로 대체하는 alternative 호출입니다. 항상 무조건 lfence를 출력하는 정의와 다릅니다. 이름이 비슷한 array_index_mask_nospec는 데이터 마스크를 생성하는 별도 방식입니다.'),
        ('DMA와 SMP', '__dma_rmb와 __dma_wmb는 compiler barrier입니다. __smp_mb는 _ASM_SP로 선택한 스택 포인터 기준 -4 위치에 lock addl0을 수행하고 memory/cc를 선언합니다. __smp_rmb는 dma_rmb를 통해 계측·기본 정의와 연결되며 __smp_wmb는 barrier입니다. 일부 장벽이 compiler barrier라는 사실을 모든 x86 메모리 접근에 순서 문제가 없다는 주장으로 확장하지 않습니다.'),
        ('저장 후 full 순서', '__smp_store_mb(var,value)는 xchg(&var,value)를 호출하고 이전 값을 void로 버립니다. var는 포인터 인자 자체가 아니라 주소를 취할 수 있는 저장 대상입니다. 이 파일은 xchg의 실제 크기별 구현을 담고 있지 않으므로 포함 의존 구현까지 별도로 확인해야 합니다.'),
        ('Release와 acquire', '__smp_store_release는 atomic type 검사, compiler barrier, WRITE_ONCE 순서입니다. __smp_load_acquire는 READ_ONCE 값을 저장하고 타입 검사와 compiler barrier를 거친 후 반환합니다. 이 본문에는 별도의 mfence가 없습니다. 하드웨어 메모리 모델과 compiler 제약을 조합하는 구현이며 READ_ONCE만으로 다른 아키텍처에서도 같은 순서를 얻는다는 뜻은 아닙니다.'),
        ('원자 연산 전후', '__smp_mb__before_atomic과 after_atomic은 빈 do-while입니다. 주석은 x86 원자 연산이 이미 필요한 직렬화 효과를 가진다는 근거를 제시합니다. 따라서 주변에 추가 명령을 넣지 않는다는 의미이지 임의의 atomic 관련 API가 전부 같은 순서 계약을 가진다는 일반 명제는 아닙니다.'),
        ('주소 공간 전환', 'smp_mb__after_switch_mm도 빈 do-while입니다. 주석은 switch_mm의 CR3 쓰기가 full memory barrier를 제공한다고 설명합니다. 이 빈 매크로 자체는 CR3를 쓰거나 주소 공간을 전환하지 않습니다.'),
        ('CS 연결', '전처리 구성, 기능 기반 명령 대체, 산술 플래그로 분기를 제거하는 마스크, 하드웨어 모델에 맞춘 compiler barrier, 교환 연산과 반환값 폐기를 학습합니다. 일반 RAM과 장치·특수 메모리의 순서 계약을 섞지 않고 각 API의 적용 범위를 함께 확인합니다.')
    ],
    questions=[
        ('이 파일의 x86 __smp_store_release에 mfence가 직접 있는가?', '없다. 타입 검사와 compiler barrier 뒤 WRITE_ONCE이다', '있다. 모든 저장 직전에 mfence이다', '아키텍처 메모리 모델과 compiler barrier를 조합하는 구현입니다. 다른 아키텍처의 FENCE 기반 구현을 그대로 대입하면 틀립니다.'),
        ('index==size일 때 nospec mask는?', '0이다', '모든 비트1이다', 'cmp에서 unsigned borrow가 없으므로 sbb의 carry 입력은0입니다. 같은 레지스터에서 자신과0을 빼 결과0을 얻습니다.'),
        ('32비트 mb의 XMM2 대체 문자열은?', 'mfence이다', 'sfence이다', 'mb/rmb/wmb의 대체 문자열은 각각 mfence/lfence/sfence입니다. 기본 문자열은 세 경우 모두 lock addl0입니다.'),
        ('__smp_store_mb는 xchg가 반환한 이전 값을 어떻게 하는가?', 'void 변환으로 버린다', '반드시 호출자에게 반환한다', 'do-while 본문에서 (void)xchg(&var,value)를 수행합니다. 저장과 순서가 목적이며 이전 값은 API 결과로 노출하지 않습니다.'),
        ('smp_mb__after_switch_mm의 빈 본문이 CR3를 쓰는가?', '아니다. switch_mm의 기존 순서 보장을 전제로 추가 작업이 없다', '그렇다. 빈 매크로가 CR3 쓰기로 변환된다', '주석은 다른 연산이 제공한 장벽을 근거로 합니다. 이 매크로 자체가 주소 공간을 전환하는 것은 아닙니다.')
    ]
), dict(
    path='arch/x86/include/asm/nops.h',
    title='x86 NOP 헤더 전체: 길이별 바이트와 명령 패치',
    intro='alternative와 tracing에 쓰는 길이별 NOP 바이트 열을 32·64비트 구성별로 읽습니다.',
    principle='명령의 바이트 길이와 명령 개수는 다릅니다. 지정한 공간에 맞는 인코딩을 선택합니다.',
    use='장벽 헤더에서 포함한 NOP 정의를 따라가며 바이트 수와 접두사 조합을 직접 계산합니다.',
    area='기계어 인코딩 · 전처리기 · 접두사 · 포인터 const',
    sections=[
        ('파일 경계', 'GPL-2.0, guard와 asm.h 포함, CONFIG_64BIT에 따른 바이트 정의, ASM_NOP 문자열 조각, C용 x86_nops 외부 선언이 전부입니다. 실제 alternative 패치나 tracing 알고리즘은 구현하지 않습니다.'),
        ('32비트 짧은 인코딩', '비64비트에서 NOP1은90, NOP2는89 f6, NOP3은8d 76 00, NOP4는8d 74 26 00입니다. 주석은 각각 nop,esi 자기복사,esi를 그대로 계산하는 lea 계열을 설명합니다. 이름의 숫자는 바이트 수이며 NOP4가 nop 명령 네 개라는 뜻이 아닙니다.'),
        ('32비트 긴 인코딩', 'NOP6은8d b6 뒤0 네 개, NOP7은8d b4 26 뒤0 네 개입니다. NOP5는 DS 접두사3e와 NOP4, NOP8은3e와 NOP7을 결합합니다. 주석은5·8 길이에 GAS가 두 nop 명령을 내보내는 경우와 달리 이 정의는 접두사를 사용한다고 설명합니다. 최대 길이는8입니다.'),
        ('64비트 기본 인코딩', 'NOP1은90, NOP2는66+NOP1입니다. NOP3/4/5는 각각0f 1f 00,0f 1f 40 00,0f 1f 44 00 00입니다. NOP6은66+NOP5이며 NOP7은0f 1f 80 뒤0 네 개, NOP8은0f 1f 84 뒤0 다섯 개입니다. 주석의 메모리 피연산자 모양만으로 일반 데이터 load와 동일시하지 않습니다.'),
        ('64비트 접두사 확장', 'NOP9는2e+NOP8, NOP10은66+NOP9, NOP11은66+NOP10입니다. 따라서11바이트 열은66 66 2e 0f 1f 84 00 00 00 00 00입니다. 최대 길이는11이고9·10·11의 ASM_NOP 정의도64비트 분기 안에만 있습니다.'),
        ('바이트에서 asm으로', 'ASM_NOP1부터8은 분기 뒤 공통으로 _ASM_BYTES(BYTES_NOPn)를 사용합니다. BYTES 계열은 쉼표로 나열한 바이트 토큰이고 ASM 계열은 asm.h의 변환 매크로를 거칩니다. 이 헤더 자체에는 임의 n을 받아 길이를 생성하는 실행 함수가 없습니다.'),
        ('외부 테이블과 const', '비어셈블리에서 extern const unsigned char * const x86_nops[]를 선언합니다. 원소는 읽기 전용 바이트를 가리키는 변경 불가능한 포인터입니다. extern 선언만 있으므로 저장 공간·원소 배치·인덱스 규칙의 실제 정의는 다른 파일에서 확인해야 합니다.'),
        ('테이블 구현과 연결', 'arch/x86/kernel/alternative.c의 실제 정의에서는 x86nops에 길이1부터 최대 길이까지 바이트를 연달아 담고 x86_nops[0]은 NULL로 둡니다. x86_nops[n]은 앞선 길이들의 합 n(n-1)/2 위치를 가리킵니다. 예를 들어 길이4는 offset6, 길이8은 offset28입니다. 이 연결은 해당 파일의 테이블 부분을 확인한 것이며 alternative.c 전체를 해설 완료로 세지 않습니다.'),
        ('CS 연결', '고정 길이 코드 패치, 인코딩의 재사용, 전처리 조건과 접두사 누적, 선언과 정의의 차이를 학습합니다. 바이트 수를 확인하는 것만으로 모든 CPU의 명령 지원이나 성능을 검증한 것은 아닙니다.')
    ],
    questions=[
        ('비64비트 BYTES_NOP5는 어떻게 구성되는가?', '0x3e와 BYTES_NOP4의 결합이다', '0x90 다섯 개이다', '정의가0x3e,BYTES_NOP4입니다.1바이트 접두사와4바이트 인코딩을 합쳐5바이트를 만듭니다.'),
        ('64비트 BYTES_NOP11은 BYTES_NOP8보다 몇 바이트 긴가?', '3바이트이다', '11바이트이다', 'NOP9에서2e, NOP10과11에서66을 하나씩 추가합니다.8+1+1+1=11입니다.'),
        ('ASM_NOP_MAX의 값은 모든 구성에서11인가?', '아니다. 비64비트8,64비트11이다', '그렇다. 구성과 무관하게11이다', 'CONFIG_64BIT 양쪽 분기에 각각 정의되어 있습니다.9~11 인코딩도64비트 쪽에서만 제공합니다.'),
        ('x86_nops extern 선언이 테이블 내용을 정의하는가?', '아니다. 내용의 정의는 다른 파일에 있다', '그렇다. extern만으로 바이트가 자동 채워진다', '이 파일에는 초기화 목록이 없습니다. const 포인터 타입과 외부 심벌을 선언할 뿐입니다.')
    ]
)]
