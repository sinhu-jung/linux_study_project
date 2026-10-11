"""Whole 32-bit ARM and Alpha barrier headers."""
ROWS = [dict(
    path='arch/alpha/include/asm/barrier.h',
    title='Alpha 장벽 전체: READ_ONCE에 포함된 acquire 순서',
    intro='세 공개 장벽, 내부 acquire 읽기와 SMP용 asm 문자열의 관계를 읽습니다.',
    principle='다른 계층에서 이미 제공하는 장벽을 이용하므로 짧은 매크로도 포함 관계와 함께 해석해야 합니다.',
    use='앞서 읽은 Alpha rwonce.h의 읽기 뒤 mb와 연결합니다.',
    area='메모리 모델 · compiler clobber · 계층별 재정의 · SMP',
    sections=[
        ('전체 구성', 'GPL-2.0과 guard 뒤 mb/rmb/wmb, __smp_load_acquire, CONFIG_SMP별 문자열, generic barrier 포함으로 끝납니다. 독립적인 저장 release 구현이나 전역 데이터는 없습니다.'),
        ('공개 장벽 명령', 'mb와 rmb는 둘 다 volatile asm의 mb 명령을 사용하고 wmb는 wmb 명령을 사용합니다. 세 정의 모두 memory clobber를 선언합니다. 읽기 장벽 이름이 다르더라도 여기서는 full 장벽과 같은 명령을 선택합니다. CPU 명령과 compiler clobber를 구분합니다.'),
        ('Acquire와 READ_ONCE 연결', '__smp_load_acquire는 compiletime_assert_atomic_type(*p) 뒤 __READ_ONCE(*p)의 결과를 반환합니다. 이 본문만 보면 mb가 없지만 SMP Alpha의 __READ_ONCE는 값을 읽고 mb를 실행한 뒤 보관한 값을 반환합니다. public READ_ONCE 대신 내부 매크로를 사용하며 타입 정적 검사는 이 acquire 본문에서 수행합니다.'),
        ('구성별 asm 문자열', '__ASM_SMP_MB는 SMP에서 탭·mb·개행 문자열이고 비SMP에서는 빈 매크로입니다. 이것만으로 독립 C asm 문이 실행되는 것이 아니라 다른 asm에 삽입할 조각입니다. 위의 공개 mb/rmb/wmb 정의는 이 CONFIG_SMP 조건 밖에 있으므로 비SMP에서 전부 사라지지 않습니다.'),
        ('공통 정의와 범위', '마지막 asm-generic/barrier.h가 이 파일에 없는 내부 SMP 기본값, release, 공개 API 등의 계층을 채웁니다. 공개 smp_load_acquire의 비SMP 기본 경로와 내부 __smp_load_acquire를 혼동하지 않습니다. 소스 읽기와 구조 검사는 실제 Alpha CPU의 모든 경쟁 실행 검증이 아닙니다.')
    ],
    questions=[
        ('Alpha mb와 rmb의 asm 명령이 서로 다른가?', '아니다. 둘 다 mb이다', '그렇다. rmb 명령 문자열을 사용한다', '두 매크로 본문이 모두 mb와 memory clobber입니다. 함수형 이름만으로 명령 이름을 추측하면 틀립니다.'),
        ('SMP의 __smp_load_acquire에서 읽기 뒤 장벽은 어디에 있는가?', 'Alpha __READ_ONCE 구현 안에 있다', '없다. 이 구현은 순서를 전혀 제공하지 않는다', 'rwonce.h의 override가 읽기 값을 보관하고 mb를 수행합니다. 현재 파일의 호출과 피호출 구현을 함께 봐야 합니다.'),
        ('비SMP에서 __ASM_SMP_MB가 비면 공개 mb도 사라지는가?', '아니다. 공개 mb는 구성 조건 밖에 정의되어 있다', '그렇다. 같은 이름의 별칭이므로 사라진다', '문자열 조각과 실행 매크로는 별개입니다. mb는 독립 volatile asm 정의를 유지합니다.')
    ]
), dict(
    path='arch/arm/include/asm/barrier.h',
    title='ARM 장벽 전체: 세대별 명령과 DMA·SMP 범위',
    intro='32비트 ARM의 아키텍처 세대, SoC 보완 장벽, 공유 범위와 투기 마스크를 해설합니다.',
    principle='장벽 종류뿐 아니라 CPU 세대와 적용 영역, 구성 조건을 함께 읽어야 실제 동작을 알 수 있습니다.',
    use='ARM64 구현과 구별하면서 generic barrier 계층으로 연결되는 정의를 추적합니다.',
    area='ARM 명령 · 조건부 컴파일 · DMA · 공유 영역 · 투기 마스크',
    sections=[
        ('파일 경계와 NOP', 'GPL-2.0·guard·비어셈블리 조건 안에 전체 C 정의가 있습니다. nop은 mov r0,r0를 volatile asm으로 사용합니다. 이 정의에는 memory clobber가 없으며 NOP를 장벽과 동일시하지 않습니다. 마지막에 asm-generic/barrier.h를 포함합니다.'),
        ('이벤트와 대기 명령', 'ARM 아키텍처7 이상 또는6이면서 CONFIG_CPU_32v6K이면 sev/wfe/wfi를 해당 명령과 memory clobber로 정의합니다. 그렇지 않은 분기에서는 wfe만 빈 do-while로 정의합니다. 세 함수 모두 항상 빈 기본값을 갖는다고 설명하면 틀립니다. 대기 명령은 특정 공유 변수 조건을 자체적으로 검사하지 않습니다.'),
        ('ARMv7 이상 장벽', 'isb/dsb/dmb는 전달 option을 문자열화해 명령 뒤에 붙이며 memory clobber를 둡니다. 개념상 명령 흐름 동기화, 완료 요구, 메모리 순서의 역할을 구분합니다. CONFIG_THUMB2_KERNEL이면 CSDB는 .inst.w 0xf3af8014이고 아니면 .inst 0xe320f014입니다. csdb()는 이 문자열을 memory clobber와 함께 asm으로 실행합니다.'),
        ('XSC3와 ARMv6', 'CONFIG_CPU_XSC3 또는 아키텍처6에서는 isb가 mcr p15,c7,c5,4, dsb가 c7,c10,4, dmb가 c7,c10,5 조합을 사용합니다. 입력 레지스터에0을 전달하고 memory clobber를 선언합니다. 이 분기의 형식 인자 x는 명령 문자열에 반영되지 않으므로 새 세대의 option 문자열 처리를 그대로 적용하면 안 됩니다.'),
        ('FA526과 그 밖의 경로', 'FA526은 isb와 dsb에 위와 같은 대응 mcr를 사용하지만 dmb는 빈 asm과 memory clobber입니다. 마지막 기본 분기는 isb와 dmb가 빈 asm, dsb만 c7,c10,4 mcr입니다. 이후 CSDB나 csdb가 아직 없으면 각각 빈 정의를 제공합니다. 빈 asm의 compiler 장벽과 하드웨어 명령은 다릅니다.'),
        ('SoC 보완 장벽', 'CONFIG_ARM_HEAVY_MB이면 soc_mb 함수 포인터와 arm_heavy_mb 함수를 extern 선언하고 __arm_heavy_mb는 dsb(x) 뒤 arm_heavy_mb()를 실행합니다. 아니면 dsb(x)만 실행합니다. 이 헤더는 soc_mb의 호출·설정 구현을 담지 않으므로 포인터가 여기서 바로 호출된다고 설명하지 않습니다.'),
        ('공개 장벽의 구성 조건', 'CONFIG_ARM_DMA_MEM_BUFFERABLE 또는 CONFIG_SMP이면 mb는 인자 없는 heavy 장벽, rmb는 dsb(), wmb는 st를 넘긴 heavy 장벽입니다. dma_rmb는 dmb(osh), dma_wmb는 dmb(oshst)입니다. 둘 다 꺼진 구성에서는 이 다섯 공개 매크로가 compiler barrier입니다. 공개 wmb 경로와 내부 SMP 쓰기 장벽의 명령 종류가 같다고 추측하지 않습니다.'),
        ('공유 영역과 SMP', '__smp_mb는 dmb(ish), __smp_rmb는 같은 내부 full 장벽, __smp_wmb는 dmb(ishst)입니다. ish는 inner-shareable, osh는 outer-shareable 범위이고 st는 저장 접근에 관련된 장벽 옵션입니다. DMA와 CPU 간 공유 영역의 선택을 구별하되 실제 장치의 일관성 계약은 별도로 확인해야 합니다.'),
        ('투기 인덱스 마스크', 'CONFIG_CPU_SPECTRE이면 unsigned long idx,sz를 받아 cmp idx,sz와 sbc mask,idx,idx 뒤 CSDB 문자열을 실행합니다. ARM의 unsigned 비교에서 idx<sz이면 carry가0이므로 idx-idx-(1-C)=-1로 모든 비트1을 얻고, idx>=sz이면 carry1로0입니다. x86 sbb의 borrow 설명을 ARM carry 의미에 그대로 대입하면 틀립니다.'),
        ('마스크 제약과 재정의 표시', 'mask 출력은 레지스터, idx도 레지스터, sz는 Ir 제약이며 cc clobber를 선언합니다. 이 asm 블록은 CSDB 문자열을 붙이며 별도 csdb() 매크로를 호출하는 것이 아닙니다. 함수 뒤 같은 이름의 자기참조 매크로를 정의해 공통 nospec 헤더의 #ifndef가 아키텍처 제공 여부를 인지하게 합니다.'),
        ('CS 연결과 범위', '명령 집합 세대별 fallback, compiler와 CPU 장벽, 공유 영역, 구성별 동작, carry를 이용한 branchless mask와 전처리 탐지를 학습합니다. 이 파일은 acquire/release 모든 API 본문을 직접 정의하지 않으며 generic 헤더가 나머지를 제공합니다. 실제 ARM 장치 실행 시험이나 모든 투기 취약점 검증을 수행한 것은 아닙니다.')
    ],
    questions=[
        ('구형 이벤트 명령 분기에서 빈 기본값을 제공하는 것은?', 'wfe만이다', 'sev/wfe/wfi 모두이다', '#else에는 wfe의 빈 do-while 정의만 있습니다. 존재하지 않는 두 기본 정의를 추측해 추가하면 소스 설명이 달라집니다.'),
        ('ARM DMA와 SMP 장벽의 공유 영역 옵션은?', 'DMA는 osh 계열, SMP는 ish 계열이다', '모두 항상 같은 ish 계열이다', 'dma_rmb/wmb는 osh/oshst, __smp_mb/wmb는 ish/ishst입니다. 구성 조건과 실제 대상 메모리도 함께 확인해야 합니다.'),
        ('CONFIG_ARM_HEAVY_MB에서 __arm_heavy_mb의 순서는?', 'dsb 후 arm_heavy_mb 함수 호출이다', '함수 호출 뒤 dsb이다', 'do-while 본문은 dsb(x); arm_heavy_mb()입니다. soc_mb 포인터를 이 매크로가 직접 호출하는 것은 아닙니다.'),
        ('ARM cmp에서 idx==sz이면 sbc 기반 mask는?', '0이다', '모든 비트1이다', '같으면 unsigned borrow가 없고 carry1입니다. sbc는 idx-idx-(1-C)이므로0입니다. idx<sz일 때 carry0으로-1이 됩니다.'),
        ('array_index_mask_nospec 자기참조 매크로는 어떤 역할인가?', '공통 헤더의 전처리 검사에 구현 존재를 알린다', '런타임에서 함수를 무한 재귀 호출한다', '같은 이름의 매크로는 #ifndef의 정의 여부 검사에 사용됩니다. C 함수 본문에 재귀 호출이 추가되는 것은 아닙니다.')
    ]
)]
