"""Whole ARM cache classification and selector header."""
ROWS = [dict(
    path='arch/arm/include/asm/cachetype.h',
    title='ARM 캐시 종류 전체: 비트 판별과 구성별 제거',
    intro='캐시 종류 비트와 compiler가 제거할 수 있는 조건, 캐시 선택·식별 레지스터 접근을 해설합니다.',
    principle='실행 중 감지한 cacheid에 빌드 구성과 최소 지원 아키텍처 정보를 결합해 가능한 캐시 종류를 판별합니다.',
    use='flush.c의 VIVT/VIPT 분기가 이 헤더의 판별식에 어떻게 연결되는지 추적합니다.',
    area='캐시 인덱스·태그 · 비트 집합 · 조건부 컴파일 · 레지스터 I/O',
    sections=[
        ('파일 구성과 저장 위치', 'GPL-2.0과 guard 뒤 CACHEID 비트, extern cacheid, 판별 매크로, 최소 아키텍처·구성 마스크, cacheid_is, 캐시 선택 상수, 비V7M/V7M 레지스터 helper를 정의합니다. cacheid는 선언만 있고 감지·초기화 본문은 이 파일에 없습니다.'),
        ('캐시 비트 집합', 'VIVT는 bit0, VIPT_NONALIASING은 bit1, VIPT_ALIASING은 bit2, ASID_TAGGED는 bit3, VIPT_I_ALIASING은 bit4, PIPT는 bit5입니다. CACHEID_VIPT는 bit1|bit2의 복합 마스크입니다. VIVT/VIPT/PIPT 이름은 가상·물리 인덱스와 태그의 조합에 연결되며 D-side alias 분류와 I-side 특성 비트가 한 집합에 들어 있습니다.'),
        ('판별 이름의 의미', 'cache_is_vivt/vipt/nonaliasing/aliasing은 대응 CACHEID를 cacheid_is에 넘깁니다. icache_is_vivt_asid_tagged는 ASID_TAGGED, icache_is_vipt_aliasing은 VIPT_I_ALIASING, icache_is_pipt는 PIPT를 검사합니다. cpu_dcache_is_aliasing은 VIVT 또는 VIPT_ALIASING의 논리 OR입니다. I-cache alias bit만 켜졌다고 이 D-cache predicate가 참이 되는 것은 아닙니다.'),
        ('최소 아키텍처 마스크', '__LINUX_ARM_ARCH__는 실행 CPU 번호가 아니라 최소 지원 아키텍처입니다.7 이상에서는 NONALIASING·ASID_TAGGED·I_ALIASING·PIPT만 남깁니다.6 이상에서는 VIVT를 제외하고, 더 낮으면 모든 비트를 통과시킵니다. 주석은 v6 이상은 VIVT가 아니며 v7 이상 D-side VIPT는 alias하지 않는다고 설명합니다. I-side alias 비트까지 제거되는 것은 아닙니다.'),
        ('빌드 구성의 항상·불가 집합', 'VIVT만 구성되고 VIPT가 없으면 ALWAYS=VIVT, NEVER=~VIVT입니다. VIPT만 구성되면 ALWAYS=0, NEVER=VIVT입니다. 그 밖, 즉 둘 다 있거나 둘 다 없으면 ALWAYS=NEVER=0입니다. VIPT만 구성됐다는 사실만으로 aliasing인지 nonaliasing인지까지 항상 참으로 정하지 않습니다.'),
        ('최종 판별 식', 'cacheid_is는 unsigned int를 반환하고 pure 속성이 붙습니다. 식은 (ALWAYS & mask) | (~NEVER & ARCH_MIN & mask & cacheid)입니다. 항상 성립하는 부분과 런타임 값에서 허용된 부분을 합칩니다. ALWAYS 항 자체에는 ARCH_MIN이 곱해지지 않으므로 식을 임의로 다시 묶으면 동작이 달라질 수 있습니다. 정상 빌드 조합의 타당성 검사는 이 함수가 담당하지 않습니다.'),
        ('반환값과 pure', 'cacheid_is의 결과는 bool0/1 정규화가 아니라 남은 비트 패턴입니다. 예를 들어 mask=VIPT, cacheid에 NONALIASING만 있고 필터가 허용하면2를 반환합니다. if문은 이를 참으로 해석합니다. pure 속성이 있어도 이 함수는 외부 cacheid를 읽으므로 실행 내내 값이 고정된 수학 함수라는 뜻은 아닙니다.'),
        ('캐시 선택 필드', 'CSSELR_ICACHE=1, DCACHE=0입니다. L1부터L7은 각각0부터6을 한 비트 왼쪽 이동한 값입니다. level-1을 bit1 이상에 놓고 bit0로 I/D를 구분하므로 I-cache L3 선택 값은(2<<1)|1=5입니다. 이 상수들은 캐시의 실제 크기나 way 수를 직접 표현하지 않습니다.'),
        ('비V7M 레지스터 접근', 'set_csselr는 mcr p15,2로 전달한 cache_selector를 쓰고 read_ccsidr는 mrc p15,1로 읽어 unsigned int를 반환합니다. asm은 volatile이지만 이 helper 본문에는 명시적 ISB나 memory clobber가 없습니다. 이름만 보고 모든 필요한 호출 간 동기화가 자동 포함된다고 설명하면 안 됩니다.'),
        ('V7M 경로와 원본의 불일치', 'V7M 구성에서는 linux/io.h와 asm/v7m.h를 포함하고 writel/readl을 사용합니다. 이 고정 버전의 set_csselr 본문은 BASEADDR_V7M_SCB+V7M_SCB_CTR에 씁니다. 연결 헤더를 확인하면 CTR은0x7c Cache Type, CSSELR는0x84 Cache size selection으로 따로 정의되어 있어 함수 이름과 실제 대상이 일치하지 않는 지점입니다. 이를 조용히 CSSELR 쓰기로 바꾸어 해설하지 않습니다. 의도한 동작의 적합성이나 수정 필요성은 별도 검증 대상으로 남깁니다. read_ccsidr는 V7M_SCB_CCSIDR인0x80을 읽습니다.'),
        ('CS 연결과 검증 범위', '비트 집합의 교집합·합집합·보수, 정적 구성에 의한 분기 제거, 술어의 비정규화 반환값, 레지스터 필드 인코딩, 이름과 실제 주소의 교차 확인을 학습합니다. v7m.h의 관련 상수를 읽은 것은 그 파일 전체를 해설 완료로 세지 않으며 실제 V7M 하드웨어 동작을 시험한 것도 아닙니다.')
    ],
    questions=[
        ('cacheid_is가 NONALIASING 비트만 통과시키면 반환값은 반드시1인가?', '아니다. 해당 비트 값2일 수 있다', '그렇다. 모든 predicate는 bool1로 변환된다', '본문은 비트 OR 결과를 unsigned int로 반환합니다. if에서 참으로 평가된다는 것과 정확한 숫자가1이라는 것은 다릅니다.'),
        ('ARMv7 최소 지원 마스크가 제거하는 alias 관련 비트는?', 'D-side VIPT_ALIASING이며 I-side alias 비트는 남는다', 'D-side와 I-side alias 비트를 모두 제거한다', 'ARCH_MIN에는 VIPT_I_ALIASING이 포함됩니다. 주석의 v7 D-side 조건을 모든 캐시에 확장하면 틀립니다.'),
        ('I-cache L3의 선택 상수 조합 값은?', '5이다', '7이다', 'L3은(2<<1)=4이고 ICACHE는1이므로 OR 결과5입니다. 레벨 번호 자체3을 그대로 왼쪽 이동하는 방식이 아닙니다.'),
        ('CONFIG_CPU_CACHE_VIPT만 켜지면 항상 aliasing VIPT라고 확정되는가?', '아니다. ALWAYS는0이고 런타임 비트를 검사한다', '그렇다. ALWAYS=VIPT_ALIASING이다', 'VIPT-only 분기는 VIVT만 NEVER로 제외합니다. aliasing/nonaliasing은 허용된 cacheid 비트를 통해 결정합니다.'),
        ('이 버전의 V7M set_csselr가 실제로 writel하는 상수는?', 'V7M_SCB_CTR이다', 'V7M_SCB_CSSELR이다', '본문의 주소는 CTR입니다. 관련 헤더에는 CSSELR 상수가 별도로 있으므로 이름의 의도와 실제 코드 주소를 구분해 기록해야 합니다.')
    ]
)]
