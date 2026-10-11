"""Complete simple wait queue implementation."""
ROWS = [dict(
    path='kernel/sched/swait.c',
    title='단순 대기 큐 구현 전체: 등록, 깨우기와 중단 정리',
    intro='태스크 포인터와 연결 리스트를 이용해 단순 대기 큐의 초기화·등록·깨우기·정리를 구현합니다.',
    principle='대기 항목의 연결 상태와 태스크 상태를 잠금 아래 조정합니다. 조건 자체는 호출자가 관리하며, 깨우기는 조건 검사나 실행 완료를 대신하지 않습니다.',
    use='completion 등에서 내부 함수와 잠금 wrapper를 구분해 읽습니다. IRQ 문맥에서 모든 전체 깨우기 함수를 동일하게 사용할 수 있는 것은 아닙니다.',
    area='연결 리스트 · 스케줄링 · 대기 큐 · 인터럽트 · 동시성',
    sections=[
        ('전체 구성', 'GPL-2.0과 구현 소개 뒤 큐 초기화, 잠금 보유 상태의 단일·전체 깨우기, 단일·전체 wrapper, 내부 등록과 두 등록 wrapper, 내부·외부 정리가 있습니다. __init_swait_queue_head, swake_up_locked, swake_up_one/all, prepare_to_swait_exclusive/event, finish_swait는 EXPORT_SYMBOL입니다. 나머지 내부 함수와 completion 전용 전체 깨우기는 이 파일에서 별도로 export하지 않습니다.'),
        ('초기화', '__init_swait_queue_head는 raw spinlock을 초기화하고 lockdep class와 name을 설정한 뒤 task_list를 빈 순환 리스트로 만듭니다. 여기에는 기다릴 조건의 값, 완료 신호 횟수 또는 timeout 저장이 없습니다. 호출자가 별도 조건과 큐의 수명을 관리해야 합니다.'),
        ('잠금 아래 한 명 깨우기', 'swake_up_locked는 큐가 비었으면 반환하고, 아니면 첫 항목을 선택해 TASK_NORMAL과 전달받은 wake_flags로 try_to_wake_up을 호출한 뒤 list_del_init으로 항목을 제거·자기 연결 초기화합니다. 함수 안에서 잠금을 잡지 않으므로 호출자가 이미 보유해야 합니다. 깨우기 결과가0이어도 항목은 제거합니다. 주석은 이미 실행 중인 태스크가 조건을 관측할 것이라는 프로토콜 전제를 설명합니다.'),
        ('한 명 wrapper', 'swake_up_one은 irqsave raw spinlock 아래 swake_up_locked(q,0)을 호출하고 원래 IRQ 상태를 복원합니다. 큐 뒤에 등록하고 앞에서 꺼내는 방식은 대기 항목 선택의 FIFO 순서를 형성하지만 여러 CPU에서 후속 코드가 완료되는 순서까지 보장하지 않습니다.'),
        ('completion 전용 전체 깨우기', 'swake_up_all_locked는 큐가 빌 때까지 swake_up_locked(q,0)을 반복합니다. 잠금을 직접 풀거나 IRQ를 켜지 않습니다. 원문은 completion만을 위한 인터페이스이며 일반 용도가 아니라고 명시합니다. 큐 길이에 따라 반복하므로 일반 swake_up_all의 잠금 보유 시간을 나누는 전략과 다릅니다.'),
        ('일반 전체 깨우기의 분리 목록', 'swake_up_all은 IRQ를 끄고 잠근 뒤 list_splice_init으로 당시 큐를 지역 tmp 목록으로 옮깁니다. tmp의 첫 항목마다 wake_up_state(TASK_NORMAL)와 list_del_init을 수행합니다. 더 남으면 잠금 해제와 IRQ 활성화 후 다시 잠급니다. 그 사이 원래 큐에 새로 등록된 항목은 tmp에 포함되지 않으므로 이 호출이 새 대기자까지 무한히 따라 깨우는 구조가 아닙니다.'),
        ('IRQ 계약', '일반 전체 깨우기는 irqsave가 아니라 lock_irq/unlock_irq를 사용하고 반복 중 IRQ를 열어 잠금 보유 시간을 나눕니다. 그래서 IRQ가 꺼진 상태에서 사용하면 안 된다는 주석이 있습니다. 반면 locked 전체 깨우기는 호출자가 유지하는 잠금·IRQ 문맥 안에서 동작하도록 별도로 제공됩니다. 모든 wake 함수가 같은 문맥 계약이라고 추측하면 안 됩니다.'),
        ('내부 등록', '__prepare_to_swait는 wait->task=current를 설정하고 항목이 비연결 상태일 때만 큐 꼬리에 추가합니다. 이미 등록된 항목을 반복해서 중복 삽입하지 않습니다. 자체 잠금이나 태스크 상태 변경은 없으며 적절히 초기화된 항목을 전제로 합니다. 임의의 다른 큐에 연결된 항목을 자동으로 옮기는 함수도 아닙니다.'),
        ('exclusive 등록', 'prepare_to_swait_exclusive는 irqsave 잠금 아래 내부 등록을 하고 set_current_state(state)로 태스크 상태를 지정한 뒤 복원합니다. 이 함수는 실제 schedule을 호출하지 않습니다. 준비·조건 재검사·수면·정리는 호출 측 대기 루프에서 이어져야 합니다.'),
        ('신호를 처리하는 등록', 'prepare_to_swait_event는 같은 잠금 아래 signal_pending_state를 확인합니다. 중단할 신호가 있으면 list_del_init으로 항목을 제거하고 -ERESTARTSYS를 반환하며, 그렇지 않으면 등록하고 상태를 설정한 뒤0입니다. 중단할 항목을 남겨두면 후속 swake_up_one이 그 항목을 선택할 수 있으므로 먼저 제거하는 것이 핵심입니다. 신호 분기 자체가 TASK_RUNNING을 설정하는 것은 아닙니다.'),
        ('내부 정리', '__finish_swait는 __set_current_state(TASK_RUNNING)을 수행하고 연결되어 있으면 list_del_init합니다. q 인자를 받지만 본문에서 잠금을 잡거나 q를 사용하지 않습니다. 호출자가 이미 잠금 아래인 경우를 위한 내부 처리이며 외부 wrapper와 동일한 동기화 기능이 있다고 생각하면 안 됩니다.'),
        ('외부 정리', 'finish_swait도 먼저 TASK_RUNNING으로 바꿉니다. list_empty_careful로 항목 상태를 확인하여 이미 제거되었다면 잠금을 생략하고, 아니면 irqsave 잠금 아래 list_del_init을 수행합니다. 빠른 검사 뒤 깨우기 측이 먼저 제거했어도 자기 연결된 항목의 삭제 초기화는 안전한 상태로 귀결됩니다. 이 최적화를 임의의 동시 리스트 변경에 일반화하면 안 됩니다.'),
        ('CS 연결과 한계', '침입형 순환 리스트, FIFO 선택, 큐 스냅샷 분리, 잠금 보유 시간, 태스크 상태와 실제 실행의 차이, 신호 중단 시 대기 항목 제거를 학습합니다. 이 파일은 조건을 참으로 만들지 않으며 호출자의 올바른 조건 공개와 수명 보장이 필요합니다. 원본 대조는 실제 모든 IRQ·스케줄러 경쟁을 실행 검증한 것이 아닙니다.')
    ],
    questions=[
        ('swake_up_all이 tmp로 큐를 옮긴 뒤 새로 원래 큐에 들어온 항목도 이번 tmp 반복이 깨우는가?', '아니다. 이번에 분리한 목록에 포함되지 않는다', '그렇다. 원래 큐가 영원히 빌 때까지 추적한다', 'list_splice_init은 그 시점의 항목들을 지역 목록으로 옮깁니다. 반복 대상은 tmp이며 중간에 등록된 새 항목은 원래 큐에 남습니다.'),
        ('일반 swake_up_all을 IRQ가 꺼진 상태에서 호출해도 되는가?', '안 된다. 구현은 반복 중 잠금을 풀며 IRQ를 켤 수 있다', '된다. 모든 경로가 irqsave로 원래 상태를 유지한다', '이 함수는 raw_spin_lock_irq/unlock_irq를 쓰며 보유 시간을 나누기 위해 반복 중 해제합니다. 원문도 IRQ-disabled 사용을 허용하지 않는다고 명시합니다.'),
        ('prepare_to_swait_exclusive는 호출 즉시 실제 수면까지 실행하는가?', '아니다. 큐 등록과 태스크 상태 설정만 한다', '그렇다. 내부에서 schedule을 호출한다', '함수 본문은 잠금, 등록, set_current_state, 잠금 해제입니다. 실제 수면과 조건 검사, 정리는 호출자 대기 루프의 역할입니다.'),
        ('prepare_to_swait_event가 신호 중단 시 항목을 제거하는 이유는?', '후속 단일 깨우기가 중단할 대기 항목을 선택하지 않게 하기 위해', '신호를 처리하려면 큐의 모든 다른 항목도 해제해야 하기 때문에', '해당 항목만 list_del_init하고 -ERESTARTSYS를 반환합니다. 단일 깨우기의 선택을 중단 태스크가 차지하지 않도록 큐 상태를 정리합니다.'),
        ('__finish_swait가 q의 잠금을 직접 잡는가?', '아니다. 외부 finish_swait와 달리 자체 잠금이 없다', '그렇다. q 인자가 있으므로 반드시 잠근다', '내부 함수는 태스크 상태와 항목만 변경합니다. 이름이나 인자 모양이 아니라 본문과 호출 문맥을 따라 잠금 책임을 확인해야 합니다.')
    ]
)]
