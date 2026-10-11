"""Whole simple wait queue declarations and wait-loop macros."""
ROWS = [dict(
    path='include/linux/swait.h',
    title='Swait 헤더 전체: 단순 대기 큐와 조건 반복 매크로',
    intro='단순 대기 큐의 자료구조·초기화·관측 함수와 상태별 조건 대기 매크로를 정의합니다.',
    principle='대기 항목을 준비한 뒤 조건을 다시 검사하고, 조건이 거짓일 때만 수면합니다. 잠금 없는 대기자 관측은 조건 공개와 짝을 이루는 메모리 순서가 필요합니다.',
    use='실시간 제약 때문에 단순 대기 큐가 필요한 사용처를 이해하는 수업입니다. 원문은 대부분의 경우 일반 wait queue를 권하며 swait를 모든 대기에 대한 빠른 대체재로 소개하지 않습니다.',
    area='대기 큐 · 매크로 · 메모리 장벽 · 시간 제한 · 실시간',
    sections=[
        ('전체 구성', 'GPL-2.0과 guard, list/stddef/spinlock/wait/current 포함, 설계 주석, 두 구조체, 초기화 매크로, 관측 inline 두 개, 외부 함수 선언, 공통 대기 매크로와 일반·interruptible·idle 각각의 무기한/timeout wrapper, endif로 구성됩니다. timeout 조건 helper와 interruptible 판정은 포함한 wait.h에 의존합니다.'),
        ('기능을 제한하는 이유', '주석은 IRQ·잠금 보유 시간을 제한하기 위해 일반 전체 깨우기 중 잠금을 나누며 IRQ-disabled 호출을 허용하지 않는다고 설명합니다. 상태별 적합한 대기자를 O(n) 검색하는 기능, 비exclusive 전체 선택, 임의 깨우기 callback을 제공하지 않습니다. 모든 깨우기는 TASK_NORMAL 대상으로 하며 일반 wait queue의 혼합 상태·callback 의미를 그대로 기대하면 안 됩니다.'),
        ('표현과 정적 초기화', 'swait_queue_head는 raw_spinlock_t lock과 task_list, 항목 swait_queue는 task 포인터와 task_list입니다. 항목 초기화는 current와 자기 연결 리스트를, head 초기화는 unlocked raw lock과 빈 리스트를 만듭니다. DECLARE_SWAITQUEUE와 DECLARE_SWAIT_QUEUE_HEAD는 각각 다른 구조체를 선언합니다. 큐에는 사용자가 기다릴 조건 자체를 저장하지 않습니다.'),
        ('동적·스택 초기화', 'init_swait_queue_head는 매크로 위치의 static lock_class_key를 만들고 q 문자열 이름과 함께 __init_swait_queue_head에 전달합니다. CONFIG_LOCKDEP의 ONSTACK 변형은 runtime 초기화를 사용하고 비활성일 때는 정적 초기화 선언으로 매핑됩니다. 초기화가 대기 큐 메모리의 수명을 자동 관리하는 것은 아닙니다.'),
        ('잠금 없는 활성 관측', 'swait_active는 단지 !list_empty를 반환합니다. 주석은 큐 잠금 아래 사용하거나, 깨우는 쪽에서 조건 저장 후 smp_mb를 수행하는 등의 올바른 동기화가 필요하다고 경고합니다. 장벽 없이 큐 읽기가 조건 저장보다 앞서 관측되면 깨우는 쪽은 빈 큐, 기다리는 쪽은 거짓 조건을 보아 알림을 놓칠 수 있습니다.'),
        ('관측 helper와 비용', 'swq_has_sleeper는 smp_mb 뒤 swait_active를 호출합니다. 기다리는 쪽의 상태 설정 장벽과 짝을 이루는 프로토콜을 전제로 합니다. 조건 값을 바꾸거나 대기자를 실제로 깨우지는 않습니다. 원문은 비경합 spinlock을 장벽으로 바꾸는 비용이 비슷할 수 있다고 설명하므로 잠금 없는 검사라는 이유만으로 성능 향상을 확정하지 않습니다.'),
        ('외부 함수 계약', 'swake_up_one/all/locked, prepare_to_swait_exclusive/event, __finish_swait/finish_swait를 선언합니다. 실제 큐 삽입·제거와 IRQ 문맥은 kernel/sched/swait.c에서 확인해야 합니다. 주석의 의사 코드 wake_up 표기를 swait 큐에 일반 wait queue 함수를 그대로 호출하라는 완성 코드로 해석하지 않습니다.'),
        ('공통 루프의 순서', '___swait_event는 GNU statement expression과 local label, 지역 __wait와 long __ret을 사용합니다. 항목 리스트를 초기화한 뒤 매 반복에서 prepare_to_swait_event, condition 확인, 중단 오류 확인, cmd 실행 순서입니다. 조건이 참이면 break 뒤 finish_swait를 호출합니다. 등록 후 재검사하므로 처음 조건 확인과 실제 수면 사이의 변화에 대응합니다.'),
        ('중단과 정리 경로', 'condition 검사가 interruptible 오류 검사보다 앞에 있습니다. 조건이 참이면 정상 정리로 끝나고, 거짓이며 상태가 interruptible이고 준비 함수가 오류를 반환하면 __ret에 오류를 넣고 __out으로 갑니다. 이 경로는 finish_swait를 건너뛰며 준비 함수가 신호 경로에서 이미 항목을 제거한다는 계약에 의존합니다. 모든 종료가 동일한 정리 함수를 실행한다고 설명하면 틀립니다.'),
        ('일반·interruptible wrapper', '일반 exclusive는 바깥에서 condition이 참이면 바로 끝나고 아니면 TASK_UNINTERRUPTIBLE, schedule을 공통 루프에 전달합니다. interruptible exclusive는 초기 반환0을 두고 조건이 거짓일 때 TASK_INTERRUPTIBLE 루프로 들어가 중단 오류를 받을 수 있습니다. 대기에서 깨어났다는 사실만으로 조건이 참이라고 가정하지 않고 반복해서 검사합니다.'),
        ('timeout wrapper', '일반과 interruptible timeout은 long __ret에 timeout을 저장하고 ___wait_cond_timeout(condition)으로 조건·만료를 판단합니다. 대기 중 cmd는 __ret=schedule_timeout(__ret)으로 잔여 시간을 갱신합니다. 조건 참 성공은 양수, 만료 후에도 거짓이면0이며 interruptible 변형은 음수 중단도 구별해야 합니다. 매크로 인자가 여러 확장에서 다시 나타나므로 timeout과 condition에 부주의한 부작용을 넣지 않습니다.'),
        ('idle 대기', 'idle 변형은 TASK_IDLE과 schedule을 사용해 시스템 부하에 기여하지 않는 대기를 표현하며 주석상 신호를 무시합니다. timeout도 같은 공통 루프와 schedule_timeout을 사용합니다. 문서는 만료 후 조건 거짓이면0, 만료 경계에서 참이면1, 그 전에 참이면 최소1의 잔여 jiffies를 명시합니다. idle이라는 이름이 busy polling을 뜻하지 않습니다.'),
        ('조건 표현과 동시성', 'condition은 처음 진입과 각 반복에서 재평가되는 C 표현입니다. 공유 값을 어떤 잠금·원자 접근·순서로 읽고 쓰는지는 호출자가 설계해야 합니다. swait 매크로가 임의 일반 변수의 데이터 경쟁이나 객체 수명 문제를 자동으로 해결하지 않습니다. 잠들 수 없는 문맥에서 이 대기 루프를 실행해서도 안 됩니다.'),
        ('CS 연결과 검증 범위', '제한된 인터페이스를 통한 지연 제어, lost wakeup 방지, 조건 변수의 재검사, GNU 매크로 지역 변수, timeout 잔여량, 정리 경로 분기를 학습합니다. 원문·구현 대조는 모든 메모리 모델의 실행을 증명하거나 실시간 지연을 측정한 결과와 다릅니다.')
    ],
    questions=[
        ('___swait_event는 큐 등록 뒤 조건과 신호 오류 중 무엇을 먼저 확인하는가?', '조건을 먼저 확인한다', '신호 오류를 먼저 확인해 조건을 보지 않는다', 'prepare_to_swait_event 뒤 condition이 참이면 break합니다. 그 다음에 interruptible 상태와 __int를 검사하므로 정상 조건 만족과 중단 처리의 우선순위를 코드 순서대로 읽어야 합니다.'),
        ('swait_active가 false이면 앞으로도 깨울 대기자가 없다고 보장되는가?', '아니다. 잠금·순서와 경쟁을 고려해야 하는 순간 관측이다', '그렇다. 호출 자체가 큐 등록을 막는다', '본문은 !list_empty뿐입니다. 주석은 조건 공개와 큐 읽기의 순서가 맞지 않으면 깨우기를 놓칠 수 있다고 경고합니다.'),
        ('swq_has_sleeper는 조건을 참으로 만들고 대기자를 깨우는가?', '아니다. 장벽을 수행하고 큐 활성 여부만 검사한다', '그렇다. 이름에 sleeper가 있으므로 내부 wakeup도 수행한다', '함수에는 smp_mb와 swait_active만 있습니다. 조건 저장과 실제 깨우기는 호출자가 수행하는 별도 단계입니다.'),
        ('공통 매크로의 신호 오류 goto 경로도 finish_swait를 호출하는가?', '아니다. prepare_to_swait_event가 항목을 정리한 경로에 의존한다', '그렇다. 모든 goto가 finish_swait 앞에 도착한다', '__out 레이블은 finish_swait 뒤에 있습니다. 오류 시 직접 레이블로 이동하므로 준비 함수의 오류 정리 계약을 함께 읽어야 합니다.'),
        ('idle timeout이 만료되는 경계에서 조건이 참이면 반환은?', '1로 성공과 시간 초과0을 구별한다', '항상0이므로 조건 만족 여부를 알 수 없다', '원문 반환 규약은 만료 후 거짓0, 경계의 참1, 이전 성공은 남은 jiffies입니다. 양수를 소요 시간으로 해석하면 안 됩니다.')
    ]
)]
