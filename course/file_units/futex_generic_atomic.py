"""Whole generic UP futex user-memory atomic helpers."""
ROWS = [dict(
    path='include/asm-generic/futex.h',
    title='Generic futex 원자 접근 전체: 단일 CPU 대체 경로와 사용자 메모리 오류',
    intro='단일 CPU용 사용자 메모리 산술·비교 교환 helper와 아키텍처 이름 연결을 제공합니다.',
    principle='선점 금지에 의존하는 지역 read-modify-write는 여러 CPU의 동시 접근을 배제하지 못합니다. 또한 접근 성공과 비교 교환의 실제 값 교체 성공은 다른 결과입니다.',
    use='generic fallback의 빌드 조건과 출력 인자의 유효성을 확인합니다. 함수 이름이나 주석의 일반 오류 목록만으로 본문에 없는 동작을 가정하지 않습니다.',
    area='원자성 · 선점 · 사용자 메모리 · 오류 처리 · 조건부 컴파일',
    sections=[
        ('전체 구성', 'GPL-2.0·guard와 linux/futex,uaccess,asm/errno 포함 뒤 조건부 이름 매핑, futex_atomic_op_inuser_local, futex_atomic_cmpxchg_inatomic_local 두 inline과 endif가 있습니다. 아키텍처용 명령 구현이나 SMP 전역 잠금은 없습니다.'),
        ('Fallback 선택 조건', 'futex_atomic_cmpxchg_inatomic 매크로가 아직 없고 CONFIG_SMP가 아닐 때에만 표준 cmpxchg 이름과 arch_futex_atomic_op_inuser를 local 함수로 연결합니다. 두 local 함수 본문 자체는 이 조건 밖에 선언되지만 이름 매핑은 단일 CPU 조건에 제한됩니다. 아키텍처 구현을 무조건 덮어쓰는 헤더가 아닙니다.'),
        ('단일 CPU 전제', '주석은 preempt_disable로 상호 배제를 확보하는 단일 CPU용 구현임을 명시합니다. 선점 금지는 다른 CPU의 사용자 메모리 접근을 멈추지 않으므로 이 read→계산→write를 그대로 SMP 원자 연산으로 사용할 수 없습니다. 임의의 IRQ 동시 접근까지 자동 해결하는 일반 잠금이라고도 확대하지 않습니다.'),
        ('산술의 입력과 읽기', 'op helper는 이미 분리된 int op, u32 oparg, int *oval, 사용자 u32 포인터를 받습니다. preempt_disable 뒤 get_user로 이전 값을 읽고 실패하면 -EFAULT로 정리합니다. kernel-doc의 encoded_op 인자 설명과 달리 실제 함수는 packed FUTEX_OP 값을 직접 해독하는 코드가 아닙니다.'),
        ('다섯 연산', 'u32 tmp에 이전 값을 넣고 SET은 대입, ADD는 덧셈, OR는 OR, ANDN은 보수 AND, XOR는 XOR를 수행합니다. tmp와 oparg가 u32이므로 ADD의 결과는32비트 unsigned 산술입니다. 비교 조건 평가나 대기자 깨우기, OPARG_SHIFT 전처리는 이 본문에 없습니다.'),
        ('쓰기와 출력 갱신', '미지원 op는 -ENOSYS여서 put_user를 실행하지 않습니다. 지원 op의 put_user 실패는 -EFAULT입니다. 모든 종료는 preempt_enable로 균형을 맞추고 ret0일 때만 *oval에 이전 값을 기록합니다. 오류가 나면 출력 인자가 새 값으로 초기화되었다고 가정하면 안 됩니다.'),
        ('비교 교환', 'cmpxchg local은 선점 금지 아래 get_user로 val을 읽습니다. val==oldval일 때만 put_user(newval)를 시도하고 실패하면 -EFAULT입니다. 비교가 다르면 저장을 생략하지만 *uval에 관측값을 기록하고0을 반환합니다. 호출자는 반환0뿐 아니라 관측값이 기대값과 같은지도 확인해야 실제 교체 여부를 압니다.'),
        ('오류 경로와 출력 순서', 'cmpxchg의 읽기·쓰기 실패는 각각 preempt_enable 후 즉시 -EFAULT로 돌아가며 *uval은 갱신하지 않습니다. 정상 경로는 *uval=val 뒤 선점을 활성화합니다. 산술 helper는 선점 활성화 뒤 출력 저장이라는 차이가 있으나 두 함수 모두 성공 시 관측한 이전 값을 전달합니다.'),
        ('이름·주석과 실제 코드', '주석은 -EAGAIN을 열거하지만 이 두 local 본문에는 그 값을 반환하는 분기가 없습니다. out_pagefault_enable 레이블도 실제로는 preempt_enable을 실행하며 별도 pagefault_enable 호출이 없습니다. 이 레이블 이름만으로 pagefault_disable/enable 쌍이 존재한다고 설명하면 안 됩니다. 사용자 접근의 상세 fault 처리는 포함된 helper와 호출 문맥도 함께 봅니다.'),
        ('CS 연결과 검증 범위', 'UP와 SMP 원자성 전제, get_user/put_user 오류 전파, 출력 인자 계약, 비교 실패와 접근 실패의 분리, unsigned 연산, 아키텍처 fallback 선택을 학습합니다. 실제 사용자 페이지 fault나 다중 CPU 동작을 실행 검증한 수업은 아닙니다.')
    ],
    questions=[
        ('이 generic 이름 매핑은 CONFIG_SMP에서도 선점 금지만으로 원자성을 제공하는가?', '아니다. 매핑은 비SMP 조건에 제한된다', '그렇다. preempt_disable이 모든 CPU를 멈춘다', '주석과 전처리 조건은 단일 CPU용임을 명시합니다. 한 CPU의 선점 금지는 다른 CPU의 동시 메모리 갱신을 배제하지 못합니다.'),
        ('cmpxchg local이0을 반환하면 반드시 newval을 썼는가?', '아니다. 비교 불일치도 접근 성공0으로 돌아간다', '그렇다.0은 언제나 값 교체 완료이다', 'val==oldval일 때만 put_user합니다. 관측값을 *uval로 반환하므로 호출자는 이 값으로 기대값 일치 여부를 판단해야 합니다.'),
        ('지원하지 않는 산술 op는 사용자 값을 쓰는가?', '아니다. -ENOSYS로 쓰기를 생략한다', '그렇다. 기본값0을 써서 정리한다', 'default에서 ret=-ENOSYS이고 put_user는 ret0일 때만 실행됩니다. *oval도 오류 경로에서는 갱신하지 않습니다.'),
        ('주석에 -EAGAIN이 있으므로 이 본문에도 해당 분기가 있는가?', '아니다. 실제 local 함수에는 그 반환 경로가 없다', '그렇다. 모든 비교 불일치가 -EAGAIN이다', '비교 불일치는0과 관측값을 반환합니다. 주석의 일반 오류 목록을 현재 본문의 실행 경로와 대조해야 합니다.'),
        ('out_pagefault_enable 레이블은 pagefault_enable 호출을 실행하는가?', '아니다. 실제 문장은 preempt_enable이다', '그렇다. 레이블 이름이 실행할 API를 결정한다', 'C 레이블은 이동 위치의 이름일 뿐입니다. 본문에 없는 fault 제어 동작을 이름에서 추론하면 잘못된 해설이 됩니다.')
    ]
)]
