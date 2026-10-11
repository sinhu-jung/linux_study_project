"""Whole-file timer migration hierarchy types and configuration contracts."""
ROWS = [dict(
    path='kernel/time/timer_migration.h',
    title='Timer migration 계층: 자식 mask와 원자적 상태 묶음',
    intro='이벤트·그룹·CPU 구조체와 상태 union, 모든 조건부 선언을 필드별로 분석합니다.',
    principle='계층별 다음 이벤트와 활성 자식 상태를 요약하면 idle CPU의 timer 처리를 다른 CPU에 맡기는 결정을 구성할 수 있습니다.',
    use='timer migration 코드에서 hotplug 중 부모 연결, NUMA 배치, 원격 처리와 상태 전파 경쟁을 이해합니다.',
    area='계층 자료구조 · timerqueue · 비트 마스크 · 원자적 CAS · NUMA · hotplug · 엔디언',
    sections=[
        ('전체 파일과 포함 전제', 'GPL-2.0-only와 guard 뒤 그룹 용량 상수, tmigr_event/group/cpu 세 구조체, tmigr_state union, 설정별 함수 선언·stub이 있습니다. 자체 include가 없으므로 timerqueue_node, raw_spinlock_t, atomic_t, list_head와 정수 타입 등을 포함 문맥이 준비해야 합니다. 실제 migration 알고리즘은 timer_migration.c에 있습니다.'),
        ('그룹 용량과 mask', 'TMIGR_CHILDREN_PER_GROUP는 8이며 주석은 2의 거듭제곱이어야 한다고 명시합니다. 자식의 활동과 migrator를 u8 mask로 표현하는 구조와 연결됩니다. 이 헤더가 8개 초과 삽입을 자동 거부하는 코드까지 제공하는 것은 아니며 num_children과 setup 구현이 규칙을 지켜야 합니다.'),
        ('이벤트 구조체 전체', 'tmigr_event는 timerqueue_node nextevt, unsigned int cpu, bool ignore를 가집니다. node는 부모 큐에 넣는 이벤트, cpu는 소속 CPU입니다. ignore는 CPU나 그룹이 active이면 무시할 수 있음을 나타내는 힌트입니다. ignore=true 자체가 큐에서 물리적으로 삭제되었다는 뜻은 아닙니다.'),
        ('그룹 잠금과 부모 연결', 'tmigr_group의 lock은 이벤트 정보와 setup 중 계층 정보를 보호하는 raw spinlock입니다. parent는 CPU가 처음 online되어 새 계층이 필요할 때 연결될 수 있으며 한 번 설정되면 제거하거나 다른 부모로 바꾸지 않는다는 계약입니다. NULL에서 부모가 생길 가능성과 이미 설정된 포인터의 불변성을 구분합니다.'),
        ('부모의 잠금 없는 관측', '주석은 전파를 중단할지 결정하는 lockless parent 관측의 최악 결과를 불필요하거나 이른 CPU 깨우기로 설명합니다. 그러나 같은 activation/deactivation/remote expiry 동작 안에서 lock 없이 parent를 여러 번 읽지 말라고 합니다. 한 동작 중 NULL과 새 포인터를 섞어 관측할 수 있기 때문입니다. 포인터가 언젠가 불변이 된다는 이유만으로 모든 반복 읽기가 안전하지는 않습니다.'),
        ('그룹 이벤트와 최단 만료', 'groupevt는 그룹이 비활성일 때 부모 timerqueue에 들어가는 다음 이벤트이며 active이면 ignore가 켜집니다. events는 자식 이벤트의 timerqueue_head입니다. next_expiry는 monotonic 기준 u64 만료 시각으로 원격 처리가 필요한지 lockless로 확인하는 데 사용되며 주석은 그 판단에 신뢰할 수 있는 값이라고 설명합니다. 이것이 그룹 전체 필드의 원자적 스냅샷을 보장한다는 뜻은 아닙니다.'),
        ('그룹의 setup 필드', 'level은 계층 레벨, numa_node는 낮은 계층을 CPU와 NUMA local하게 배치하기 위한 정보입니다. 주석상 level<tmigr_crossnode_level이면 NUMA 노드, 상위에서는 NUMA_NO_NODE입니다. num_children은 용량 관리용 unsigned int입니다. groupmask는 부모 안에서 자신의 비트인 u8로 setup 뒤 바뀌지 않아 lockless로 읽을 수 있습니다. list는 레벨별 tmigr_level_list에 연결하는 setup용 list_head입니다.'),
        ('그룹 상태 저장', 'migr_state는 atomic_t이며 뒤의 tmigr_state union은 원자적으로 읽고 cmpxchg할 결합값과 개별 필드 해석을 연결합니다. 실제 저장 객체가 union 변수 하나만인 것처럼 읽으면 안 됩니다. atomic_t 한 필드가 있다고 parent와 event queue까지 같은 원자적 연산으로 바뀌는 것도 아닙니다.'),
        ('CPU 구조체의 상태', 'tmigr_cpu의 lock은 해당 CPU의 migration 정보를 보호합니다. online은 단순 scheduler 활동 여부와 다르며 top-level migrator가 offline될 때 다른 online CPU로 역할을 넘기는 판단에 필요합니다. 주석은 CPU가 migration hotplug 단계에 도달하기 전에 idle할 수 있고 그때는 자신의 global timer를 처리하며 migrator로 행동하지 않아야 한다고 설명합니다. idle은 계층에서 idle인 상태, remote는 자신의 timer가 원격 만료 처리되는 상태를 나타냅니다.'),
        ('CPU의 연결과 다음 깨우기', 'tmgroup은 부모 그룹 포인터, groupmask는 부모 안의 u8 비트, cpuevt는 부모 큐에 들어갈 수 있는 CPU 이벤트입니다. u64 wakeup은 계층 전체가 idle이고 원격 만료 처리가 끝난 경우의 첫 timer를 저장하여 idle 경로의 timer 코드에 반환할 때 사용합니다. 일반적인 모든 CPU 깨우기 요청을 저장하는 전역 큐라고 설명하지 않습니다.'),
        ('State union 전체', 'union tmigr_state의 결합 표현은 u32 state입니다. 익명 packed 구조체는 u8 active, u8 migrator, u16 seq입니다. active는 활성 자식 비트들을, migrator는 담당 자식의 mask를 가집니다. migrator를 곧바로 CPU 번호나 자식 배열 인덱스로 읽으면 안 됩니다.'),
        ('엔디언과 sequence 목적', '주석은 결합 state를 atomic read/cmpxchg에만 쓰고 정보 갱신은 개별 구조체 필드로 하여 엔디언에 독립적으로 유지하라고 합니다. packed는 불필요한 필드 간 배치를 피하지만 모든 플랫폼에서 active가 숫자 state의 같은 하위 비트에 있다는 선언은 아닙니다. seq는 상태 갱신마다 증가시켜 자식 그룹에서 온 갱신이 다른 순서로 전파될 때의 경쟁을 막는 데 사용됩니다. 상세 경쟁 시나리오는 구현 파일의 별도 설명 대상이며 16비트 sequence가 무한 증가하는 카운터라는 뜻은 아닙니다.'),
        ('활성 구성의 여섯 함수', 'CONFIG_SMP와 CONFIG_NO_HZ_COMMON이 모두 정의되면 tmigr_handle_remote(void), bool tmigr_requires_handle_remote(void), tmigr_cpu_activate(void), u64 tmigr_cpu_deactivate(u64 nextevt), u64 tmigr_cpu_new_timer(u64 nextevt), u64 tmigr_quick_check(u64 nextevt)를 선언합니다. 처리·질의·활성화·다음 이벤트 전달의 반환형을 구분하며 구체적인 u64 sentinel 정책은 이 선언만으로 확정하지 않습니다.'),
        ('비활성 구성의 일부 stub', 'else에는 handle_remote와 cpu_activate의 빈 void inline, requires_handle_remote의 false 반환만 있습니다. deactivate/new_timer/quick_check의 비활성 stub은 이 헤더에 없습니다. 따라서 활성 분기의 여섯 함수를 어떤 구성에서도 전부 호출할 수 있게 만든 헤더라고 설명하면 안 됩니다.'),
        ('CS와 검증 범위', '전체 타입·필드·주석 계약·설정 분기를 설명했습니다. 계층 요약, intrusive timerqueue, 불변 setup 정보, hotplug 수명, CAS용 상태 묶음, 엔디언과 전파 순서의 구분을 학습합니다. timer_migration.c 전체 구현이나 실제 CPU hotplug·원격 만료 동작을 검증한 결과는 아닙니다.')
    ],
    questions=[
        ('그룹의 migrator 필드는 CPU 번호인가?', '아니다. 담당 자식의 mask이다', '그렇다. 전역 CPU 번호를 u8로 저장한다', 'union 주석은 child mask라고 명시합니다. 상위 그룹의 자식은 또 다른 그룹일 수도 있어 CPU 번호와 같다고 볼 수 없습니다.'),
        ('parent를 lock 없이 같은 동작에서 여러 번 읽어도 항상 같은가?', '아니다. setup 중 NULL에서 부모 포인터로 바뀔 수 있다', '그렇다. 한 번 설정되면 불변이라는 설명이 모든 관측을 보장한다', '설정 이후 불변과 처음 연결되는 시점은 다릅니다. 주석은 같은 action에서 반복 관측하지 말라고 명시합니다.'),
        ('ignore=true이면 해당 이벤트가 큐에서 반드시 삭제된 상태인가?', '아니다. 무시 가능 여부의 힌트이다', '그렇다. bool 대입이 timerqueue에서 자동 삭제한다', '큐 node와 ignore 필드는 별개입니다. 실제 제거·선택 동작은 구현이 수행합니다.'),
        ('packed state에서 active를 숫자 state의 하위 8비트로 직접 갱신해도 모든 엔디언에서 같은가?', '아니다. 주석은 개별 필드로 갱신하라고 요구한다', '그렇다. packed는 모든 엔디언을 little endian으로 바꾼다', 'packed와 바이트 순서는 다릅니다. 결합값은 atomic 비교용이고 필드 접근으로 의미를 유지합니다.'),
        ('SMP 또는 NO_HZ_COMMON이 꺼져도 여섯 API 모두 stub이 있는가?', '아니다. 세 개만 제공된다', '그렇다. 선언한 모든 함수는 자동으로 빈 구현이 된다', 'else에는 handle_remote, requires_handle_remote, cpu_activate만 있습니다. 나머지 호출은 해당 구성 조건을 따져야 합니다.'),
        ('seq는 왜 상태 갱신마다 증가시키는가?', '자식 그룹 갱신이 다른 순서로 전파되는 경쟁을 구분하기 위해서이다', '경과한 나노초를 직접 저장하기 위해서이다', '주석은 상태 전파 순서 경쟁 방지를 설명합니다. 만료 시각은 next_expiry 등 다른 필드에 있습니다.')
    ]
)]
