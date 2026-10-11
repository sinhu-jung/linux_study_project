"""Whole cancellable optimistic spin queue implementation."""
ROWS = [dict(
    path='kernel/locking/osq_lock.c',
    title='OSQ 구현 전체: 낙관적 스핀 큐의 안전한 취소',
    intro='CPU별 정적 노드로 큐를 만들고 재스케줄이나 선행 vCPU 선점 시 대기를 취소할 수 있는 MCS 계열 구현입니다.',
    principle='취소할 때 이전 연결을 끊고 다음 노드를 안정화한 뒤 양쪽을 이어야 합니다. 취소를 시작했어도 동시에 인계를 받았다면 획득 성공으로 처리합니다.',
    use='mutex·rwsem의 낙관적 스핀을 직렬화하는 보조 큐로 이해합니다. OSQ 획득이 보호할 실제 mutex까지 획득했다는 뜻은 아닙니다.',
    area='큐 잠금 · 취소 · per-CPU · 포인터 경쟁 · 메모리 순서',
    sections=[
        ('전체 구성', 'GPL-2.0, percpu/sched/osq_lock 포함, 노드와 per-CPU 저장소, CPU encode/node_cpu/decode helper, osq_wait_next, osq_lock의 진입·취소 A/B/C, osq_unlock로 구성됩니다. 별도 동적 할당이나 export 선언은 이 파일에 없습니다.'),
        ('노드 수명과 실행 전제', '노드는 next/prev, locked, 인코딩된 cpu를 갖고 DEFINE_PER_CPU_SHARED_ALIGNED로 CPU마다 하나씩 존재합니다. 주석은 수면 잠금을 IRQ에서 호출하지 않고 스핀 동안 선점이 꺼져 있다는 전제로 단일 CPU 노드 재사용을 정당화합니다. osq_lock 자체에는 preempt_disable 호출이 없으므로 호출 문맥의 계약입니다.'),
        ('CPU 인코딩', 'encode_cpu는 CPU번호+1, node_cpu는 저장값-1, decode_cpu는 인코딩값-1의 per_cpu_ptr를 반환합니다.0은 빈 큐를 위한 예약값이므로 decode_cpu(0)를 유효 CPU 해석으로 사용하지 않습니다. tail은 노드 포인터 대신 인코딩된 CPU 번호를 원자 정수로 저장합니다.'),
        ('진입과 꼬리 교환', 'osq_lock은 현재 CPU 노드의 locked0,nextNULL,cpu를 초기화한 뒤 atomic_xchg로 tail을 교체합니다. 이전 tail0이면 즉시 true입니다. 주석은 이 교환에 이전 해제와 연결되는 acquire 및 초기화 공개를 위한 release가 필요하다고 설명합니다. 무경합 성공에서 locked를1로 쓰지는 않습니다.'),
        ('선행 노드 연결 순서', '기존 꼬리가 있으면 decode한 prev를 node->prev에 기록하고 smp_wmb 후 WRITE_ONCE(prev->next,node)를 수행합니다. 취소 C단계가 같은 node->prev를 바꾸는 상황에서 저장 순서가 뒤집혀 리스트를 손상하지 않도록 하는 관계입니다. 노드가 정적 per-CPU 저장소라 prev의 메모리가 사라지지 않는 점이 일반 스택 MCS와 다릅니다.'),
        ('스핀 종료와 반환값', 'smp_cond_load_relaxed는 locked가 참이거나 need_resched 또는 선행 CPU의 vcpu_is_preempted 조건까지 기다립니다. if에서 사용하는 반환값은 읽은 locked 값이므로 취소 조건 때문에 대기가 끝났다고 자동 true가 되는 것은 아닙니다. locked가 참이면 획득 성공, 거짓이면 unqueue로 진행합니다. 주석은 need_resched의 IPI와 vCPU 선점의 polling 차이도 주의시킵니다.'),
        ('취소 A: 이전 연결 안정화', 'prev->next가 자신이면 cmpxchg로 NULL로 바꾸려 합니다. 성공하면 이전 노드의 해제·취소가 새 next를 기다리게 되어 prev를 안정화합니다. 실패 중 smp_load_acquire(locked)가 참이면 이미 인계받았으므로 true입니다. 그렇지 않으면 cpu_relax 후 node->prev를 다시 읽어 선행 노드 취소가 갱신한 prev에 대응합니다.'),
        ('공통 next 확보: 꼬리 되돌리기', 'osq_wait_next는 현재 CPU가 tail이고 비교 교환 acquire까지 성공하면 tail을 old_cpu로 바꾸고 NULL을 반환합니다. 취소에서는 old_cpu가 이전 노드의 인코딩 cpu라 큐를 이전 노드로 되돌리고, unlock에서는0이라 큐를 비웁니다. 매개변수 이름만 보고 원시 CPU 번호를 넘기는 것으로 해석하지 않습니다.'),
        ('공통 next 확보: 연결 소유권', '꼬리를 되돌릴 수 없으면 node->next를 xchg로 NULL과 교환해 안정된 next를 확보합니다. 단순 읽기로 남겨두면 후속 노드의 취소 A단계가 아직 이전 연결을 소유한다고 판단할 수 있습니다. 경쟁 취소가 먼저 진행하면 tail이 자신을 가리키거나 새로운 next가 연결될 때까지 cpu_relax로 반복합니다.'),
        ('취소 B와 C', 'B단계는 osq_wait_next(lock,node,prev->cpu)를 호출합니다. NULL이면 꼬리 복원이 끝났으므로 false로 종료합니다. next가 있으면 C단계에서 next->prev=prev 다음 prev->next=next를 WRITE_ONCE로 이어 자신을 우회시키고 false입니다. 양쪽 안정화 없이 포인터 두 개만 덮는 단순 삭제가 아닙니다.'),
        ('해제의 세 경로', 'osq_unlock은 먼저 tail이 현재 CPU이면 release 비교 교환으로0을 만들고 종료합니다. 실패하면 현재 노드 next를 xchg로 가져와 있으면 next->locked=1을 WRITE_ONCE로 인계합니다. 아직 next가 없으면 osq_wait_next의 old_cpu0 경로로 안정화하고 반환된 후속이 있을 때만 locked를 설정합니다.'),
        ('일반 MCS와 순서 차이', '경합 대기는 relaxed conditional load이고 일반 인계는 WRITE_ONCE입니다. 앞서 본 generic MCS의 acquire 대기·release 플래그 저장과 동일한 코드라고 복사해 설명하면 안 됩니다. OSQ는 수면 잠금의 spinner 제어를 위한 것이며 실제 보호 데이터의 획득·해제 순서는 상위 mutex/rwsem 구현과 함께 판단합니다.'),
        ('CS 연결과 검증 범위', 'per-CPU 노드 재사용, 예약값 인코딩, 비교 교환과 포인터 공개 순서, 취소와 성공 인계의 경쟁, doubly linked queue의 안전한 우회, 정적 메모리 수명을 학습합니다. 원본 각 경로를 설명한 수업이며 모든 가상 CPU 선점과 약한 메모리 실행을 실험 검증한 것은 아닙니다.')
    ],
    questions=[
        ('CPU0의 tail 인코딩은?', '1이다.0은 빈 큐를 뜻한다', '0이다. 빈 큐와 CPU0을 별도 구분하지 않는다', 'encode_cpu는 cpu_nr+1을 반환하고 decode는1을 뺍니다. 예약값을 확보하기 위해 원시 CPU 번호와 구별합니다.'),
        ('need_resched로 조건 대기가 끝났지만 locked가0이면 osq_lock은 곧바로 true인가?', '아니다. 취소 경로에 들어간다', '그렇다. 조건식 중 하나만 참이면 획득 성공이다', 'conditional load가 돌려주는 값은 읽은 locked 값입니다. 종료 이유와 획득 여부를 구분해야 합니다.'),
        ('취소 A단계 중 locked가 참으로 바뀌면 어떻게 처리하는가?', '인계를 받은 것으로 보고 true를 반환한다', '이미 취소를 시작했으므로 무조건 false를 반환한다', '취소와 선행 unlock이 경쟁할 수 있습니다. 획득을 관측했다면 소유권을 잃어버리지 않도록 성공으로 처리합니다.'),
        ('osq_wait_next에서 node->next를 읽기만 하지 않고 xchg로 NULL로 만드는 이유는?', '후속 취소가 이전 연결을 여전히 유효하다고 판단하는 경쟁을 조정하기 위해', '포인터 읽기는 C 언어에서 불가능하기 때문에', '후속의 A단계와 현재 해제·취소가 같은 연결에 관여합니다. 교환으로 연결을 가져와야 안정된 next를 기준으로 인계 또는 우회를 진행할 수 있습니다.'),
        ('osq_lock이 true면 실제 mutex도 획득한 것인가?', '아니다. 낙관적 spinner 큐의 획득이며 실제 mutex 획득은 별도다', '그렇다. OSQ는 mutex owner와 동일한 상태다', 'OSQ는 sleeping lock 구현을 위한 보조 큐입니다. 일반 경합 인계의 메모리 순서도 generic MCS와 다르므로 상위 잠금의 데이터 보호 계약을 함께 확인해야 합니다.')
    ]
)]
