"""Whole MMIO write-barrier tracking interfaces and RISC-V hook."""
ROWS = [dict(
    path='include/asm-generic/mmiowb.h',
    title='MMIOWB 추적 전체: 잠금 중 쓰기 표시와 해제 장벽',
    intro='잠금 보호 영역의 장치 쓰기 순서를 이어 주는 상태 추적과 구성별 no-op을 해설합니다.',
    principle='CPU 사이의 잠금 전달 순서와 장치가 관찰하는 쓰기 순서를 연결하기 위해 필요한 장벽만 해제 시 실행합니다.',
    use='RISC-V writel의 mmiowb_set_pending 호출이 이후 잠금 hook과 어떻게 이어지는지 추적합니다.',
    area='Spinlock · MMIO 순서 · CPU별 상태 · 중첩 카운터 · 조건부 장벽',
    sections=[
        ('목적과 통합 계약', 'GPL-2.0·guard와 주석은 서로 다른 CPU의 spinlocked 구역에서 나온 장치 쓰기가 lock handover 순서로 관찰되지 않는 아키텍처를 대상으로 합니다. mmiowb 구현,필요하면 상태 hook,쓰기 accessor의 pending 호출,ARCH_HAS_MMIOWB 선택과 헤더 통합이 필요하다고 설명합니다. 이 헤더 포함만으로 모든 쓰기 함수를 자동 계측하지 않습니다.'),
        ('구성 분기', '실제 inline 추적은 CONFIG_MMIOWB 안에 있습니다. 그렇지 않으면 set_pending,spin_lock,spin_unlock 세 매크로가 빈 do-while입니다. 아키텍처가 기능을 선택하는 이름 ARCH_HAS_MMIOWB와 이 파일의 활성 분기 CONFIG_MMIOWB를 동일한 토큰으로 읽지 않습니다.'),
        ('상태를 얻는 방법', 'arch_mmiowb_state 매크로가 없으면 percpu·smp 헤더를 포함하고 __mmiowb_state라는 per-CPU 구조체를 선언합니다. 함수형 __mmiowb_state() 매크로는 raw_cpu_ptr로 현재 CPU 상태를 얻습니다. 아키텍처 hook이 있으면 그 함수형 매크로를 사용합니다. 여기의 DECLARE_PER_CPU는 저장 공간 정의가 아닙니다.'),
        ('Pending 기록', 'mmiowb_set_pending은 nesting_count가0이 아닐 때 pending에 현재 깊이를 대입합니다. 단순히 항상1로 설정하는 본문은 아니며 깊이0에서는 아무것도 하지 않습니다. 이 호출 자체는 mmiowb 장벽을 실행하지 않습니다.'),
        ('잠금 진입 hook', 'mmiowb_spin_lock은 nesting_count를1 증가시킵니다. 실제 spinlock을 획득하는 명령이나 락 주소 인자는 없습니다. 따라서 이 helper만 호출해서 공유 자원이 보호되는 것은 아니며 실제 잠금 동작과 올바르게 연결돼야 합니다.'),
        ('해제 hook의 순서', 'mmiowb_spin_unlock은 pending이0이 아니면 먼저0으로 지우고 mmiowb를 호출합니다. 그 다음 nesting_count를1 줄입니다. pending에 저장된 깊이와 현재 깊이를 비교하거나 최외곽 깊이에서만 장벽을 실행하는 조건은 없습니다. 숫자로 깊이를 저장하더라도 소비 조건은 비0 여부입니다.'),
        ('중첩 예제', '초기 count0,pending0에서 두 lock hook 뒤 count2가 됩니다. 쓰기 pending은2로 기록되고 첫 unlock hook은 pending을0으로 지우며 장벽 후 count1로 만듭니다. 추가 쓰기가 없으면 두 번째 unlock은 장벽 없이 count0입니다. 첫 unlock 뒤 바깥 구역에서 다시 쓰면 pending1이 되어 마지막 unlock에도 장벽을 실행합니다.'),
        ('사용 전제와 한계', '상태는 잠금 객체별 테이블이 아니라 CPU별 상태 또는 아키텍처 제공 상태입니다. 현재 CPU 상태를 안전하게 사용하는 문맥과 균형 잡힌 진입·해제가 필요합니다. 카운터 underflow/overflow 검사나 잠금 종류 검증은 본문에 없고 likely/unlikely도 조건의 의미를 바꾸지 않습니다.'),
        ('CS 연결과 검증 범위', '지연된 동기화,pending 상태 기계,중첩 깊이와 bool 소비 조건의 차이,per-CPU 자료구조,아키텍처 hook과 공통 코드의 분업을 학습합니다. 장벽을 호출하는 것은 모든 장치 동작 완료나 범용 memory ownership을 자동 보증하는 것으로 확대하지 않습니다.')
    ],
    questions=[
        ('count2에서 pending이 기록된 뒤 첫 unlock은 장벽을 실행하는가?', '그렇다. pending 비0이면 즉시 실행한다', '아니다. 반드시 count0까지 기다린다', 'unlock 조건에는 깊이 비교가 없습니다. pending0으로 초기화하고 장벽을 실행한 뒤 count를 줄입니다.'),
        ('count0에서 mmiowb_set_pending을 호출하면?', 'pending을 새로 설정하지 않는다', '항상 pending1과 full barrier를 만든다', 'if(nesting_count) 안에서만 대입합니다. 이 함수에는 mmiowb 호출도 없습니다.'),
        ('mmiowb_spin_lock 자체가 실제 spinlock을 획득하는가?', '아니다. 상태의 중첩 카운터만 올린다', '그렇다. 모든 장치 접근을 잠근다', '락 주소도 받지 않습니다. 실제 잠금의 부가 추적 hook이라는 역할을 구분해야 합니다.'),
        ('CONFIG_MMIOWB가 없으면 세 추적 API는?', '빈 do-while 매크로이다', '항상 per-CPU 상태를 갱신한다', '전체 inline 구현은 CONFIG_MMIOWB 분기 안에 있습니다. 비활성 분기에는 상태 접근이 없습니다.')
    ]
), dict(
    path='include/asm-generic/mmiowb_types.h',
    title='MMIOWB 상태 타입 전체: 두16비트 필드',
    intro='장벽 추적의 중첩 깊이와 pending 상태를 저장하는 최소 구조체를 읽습니다.',
    principle='자료형 정의는 상태의 표현을 제공하며 실제 갱신 규칙과 동기화는 사용 코드가 정합니다.',
    use='mmiowb.h의 증가·대입·초기화·감소 연산을 필드 폭과 연결합니다.',
    area='C 구조체 · 정수 폭 · 상태 표현 · 선언과 저장 공간',
    sections=[
        ('파일 범위', 'GPL-2.0·guard·linux/types.h 포함 뒤 struct mmiowb_state 하나를 정의합니다. 함수,전역 인스턴스,초기화 목록은 없습니다.'),
        ('두 필드', 'nesting_count와 mmiowb_pending은 모두 u16입니다. 첫 필드는 잠금 hook의 깊이,둘째는 쓰기 시 기록된 깊이에 사용됩니다. pending은 타입상 bool이 아니며 공통 소비 코드가 비0 여부를 검사합니다.'),
        ('폭과 수명', 'u16의 표현 범위는0~65535입니다. 구조체 정의는 underflow·overflow를 방지하지 않으며 count0에서 감소하면 해당 폭의 변환 결과로65535가 될 수 있습니다. 선언 자체가 실제 과도한 nesting을 지원한다는 의미는 아닙니다.'),
        ('저장과 동기화의 분리', '필드에 atomic_t나 잠금이 들어 있지 않습니다. per-CPU 인스턴스 또는 아키텍처 상태 배치와 호출 문맥은 별도 헤더가 정합니다. 구조체 정의만으로 여러 CPU가 같은 인스턴스를 안전하게 갱신한다고 볼 수 없습니다.')
    ],
    questions=[
        ('mmiowb_pending의 타입은?', 'u16이다', 'bool이다', '두 필드 모두u16이며 실제 기록값은 깊이일 수 있습니다. 사용 시 비0 검사와 자료형의 표현 범위를 구분합니다.'),
        ('이 헤더가 per-CPU 인스턴스를 직접 할당하는가?', '아니다. 구조체 타입만 정의한다', '그렇다. 모든 CPU의 상태 배열을 초기화한다', '실제 선언·배치는 사용 계층의 역할입니다. 타입 선언과 저장 공간 생성은 별개입니다.')
    ]
), dict(
    path='arch/riscv/include/asm/mmiowb.h',
    title='RISC-V MMIOWB 전체: 장치 출력에서 잠금 쓰기로',
    intro='공통 pending 추적이 호출하는 아키텍처 장벽의 접근 집합을 읽습니다.',
    principle='장치 출력과 잠금 해제 메모리 쓰기 사이에 필요한 방향의 순서를 설정합니다.',
    use='mmio.h의 쓰기 뒤 pending 표시와 generic unlock hook을 이 fence에 연결합니다.',
    area='RISC-V fence · 장치 출력 · 메모리 쓰기 · 공통 hook',
    sections=[
        ('파일 전체 구조', 'GPL-2.0·guard 뒤 설명 주석,mmiowb 매크로,linux/smp.h와 asm-generic/mmiowb.h 포함으로 끝납니다. 독립적인 상태 변수나 장치 레지스터 읽기 함수는 없습니다.'),
        ('FENCE 집합', 'mmiowb는 RISCV_FENCE(o,w)입니다. predecessor o는 장치 출력,successor w는 메모리 쓰기입니다. 주석은 장치 쓰기가 spinlock 쓰기의 commit보다 앞서도록 하는 데 충분하다고 설명합니다. iorw,iorw의 모든 접근을 대상으로 하는 full fence 정의와 같지 않습니다.'),
        ('통합 경로', 'RISC-V 일반 MMIO 쓰기는 pending을 기록하고 활성화된 공통 spin unlock 추적은 pending이 있으면 이 매크로를 호출합니다. 이 헤더 자체가 unlock을 실행하거나 자동으로 모든 raw accessor 뒤에 장벽을 붙이지 않습니다. RISCV_FENCE 정의가 보이는 포함 문맥도 필요합니다.'),
        ('범위와 제한', '장벽의 순서 계약을 실제 장치 명령의 기능적 완료나 저장 매체 영속성 보증으로 일반화하지 않습니다. 실제 장치 protocol과 CPU 메모리 모델은 별도로 확인해야 하며 이 파일에는 readback이나 상태 완료 비트 polling이 없습니다.')
    ],
    questions=[
        ('RISC-V mmiowb의 FENCE 집합은?', 'o,w이다', 'r,r이다', '앞선 장치 출력과 뒤의 메모리 쓰기를 연결합니다. spinlock 해제 쓰기와 장치 출력의 순서를 위한 정의입니다.'),
        ('이 헤더가 장치 완료 비트를 반복해서 읽는가?', '아니다. fence 정의와 공통 추적 포함만 있다', '그렇다. 모든 쓰기에 polling을 추가한다', '함수 본문이나 상태 레지스터 접근이 없습니다. 순서 장벽과 장치 protocol 완료 확인을 구분해야 합니다.')
    ]
)]
