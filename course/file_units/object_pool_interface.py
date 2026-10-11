"""Complete object pool header including inline queue operations."""
ROWS = [dict(
    path='include/linux/objpool.h',
    title='Objpool: CPU별 링 배열과 객체 수명 계약',
    intro='고정 수량 객체 풀의 자료구조, inline pop/push, 순번 비교와 지연 종료 계약을 전체 헤더로 학습합니다.',
    principle='슬롯 예약과 객체 공개를 분리하고, 재사용 반환과 영구적인 참조 포기를 구분합니다.',
    use='rethook이 동적 할당 없이 node를 얻고 실행 중 node를 남긴 채 종료하는 구조를 이해합니다.',
    area='링 버퍼 · CAS · 메모리 순서 · CPU별 자료구조 · 모듈러 산술 · 참조 수명',
    sections=[
        ('전체 목적과 제약', 'GPL-2.0, guard와 타입·원자 연산·CPU·IRQ 관련 include 뒤 구조체, callback 타입, 상수, 초기화 선언, inline 큐 연산과 종료 선언이 있습니다. 주석은 CPU별 ring-array 기반 lockless MPMC 구조이며 할당 비용을 피해야 하는 문맥에 적합하다고 설명합니다. 객체 수는 생성 뒤 고정이고 CPU별 배열은 리스트보다 메모리를 더 사용할 수 있습니다. 확장성 수치를 모든 시스템에서 보장하는 것은 아닙니다.'),
        ('Slot의 순번과 인덱스', 'packed objpool_slot은 uint32_t head,tail,last,mask와 가변 길이 entries 포인터 배열입니다. head는 소비 위치, tail은 추가 예약 위치, last는 소비 가능하게 공개된 끝을 표현합니다. 실제 배열 인덱스는 sequence&mask이고 순번 자체는 32비트 범위를 돌며 진행합니다. 작은 배열 인덱스와 더 넓은 순번을 분리하는 구조입니다.'),
        ('관리 구조와 한도', 'objpool_head는 정렬된 obj_size, 총 nr_objs, 가능한 CPU 수, 슬롯당 capacity, gfp, refcount, flags, cpu_slots, release와 context를 가집니다. cpu_slots는 포인터 배열을 가리키는 이중 포인터입니다. 최대 객체 수 상수는 1UL<<24, 객체 크기 상수는 1UL<<16입니다. 상수 선언과 실제 초기화의 입력 검사·메모리 할당은 별도 구현에서 확인해야 합니다.'),
        ('초기화와 재사용 책임', 'init_obj callback은 obj와 context를 받아 int, fini callback은 pool과 context를 받아 int입니다. objpool_init은 객체를 미리 할당하고 0으로 초기화한 뒤 각 객체의 objinit을 한 번 호출하는 계약입니다. 이후 pop마다 자동으로 다시 0을 채우지 않습니다. 재사용 초기화나 push 전 정리는 호출자 책임이며 init의 성공은 0, 실패는 오류 코드입니다.'),
        ('Pop의 slot 검색', '__objpool_try_get_slot은 head를 smp_load_acquire로 읽고 head와 last가 다른 동안 검색합니다. unsigned 식 last-head-1이 nr_objs 이상이면 관측 순서가 유효하지 않을 수 있어 head를 다시 읽고 재시도합니다. 주석은 이용 가능한 거리 1~nr_objs인지 확인하는 식이라고 설명합니다. 단순한 signed 대소 비교로 바꾸면 순번 wrap 의미가 달라집니다.'),
        ('객체를 읽고 소비 확정', '유효한 후보이면 entries[head&mask]를 먼저 READ_ONCE로 읽은 뒤 try_cmpxchg_release로 head를 1 증가시킵니다. CAS 성공 때만 그 객체를 반환합니다. 실패하면 head가 갱신되어 재시도하며, 먼저 읽었다고 소유권을 얻은 것은 아닙니다. 빈 것으로 판단되면 NULL입니다. 항목 읽기와 head 이동의 순서를 뒤집어 설명하지 않습니다.'),
        ('CPU 간 pop 순회', 'objpool_pop은 raw_local_irq_save로 로컬 IRQ를 막고 현재 CPU 슬롯부터 시도합니다. 실패하면 cpumask_next_wrap으로 가능한 CPU들을 순환하며 nr_possible_cpus 횟수까지 조사합니다. 객체를 찾으면 멈추고 항상 IRQ 상태를 복원한 뒤 반환합니다. 현재 CPU에 객체가 없다고 즉시 pool 전체 소진으로 판단하지 않으며, 다른 CPU까지 전역 정지시키는 잠금은 아닙니다.'),
        ('Push 예약과 공개', '__objpool_try_add_slot은 tail snapshot을 읽고 head를 확인하면서 try_cmpxchg_acquire로 tail 위치 하나를 예약합니다. 예약 후 entries[tail&mask]에 WRITE_ONCE로 객체를 쓰고 smp_store_release로 last=tail+1을 공개합니다. tail 예약과 소비 가능 상태 공개는 별개입니다. 이 경로에서 허용되는 동시성은 CPU별 slot과 로컬 IRQ 제어를 포함한 전체 프로토콜의 전제에서 이해해야 합니다.'),
        ('주석의 실패 설명과 본문 차이', 'helper의 주석은 full이면 abort한다고 하지만 실제 본문은 tail-head>nr_objs에 WARN_ON_ONCE를 실행할 뿐 중단이나 오류 반환 분기가 없습니다. push 설명에도 오류 가능성이 적혀 있으나 이 inline helper는 끝에서 항상 0을 반환합니다. 따라서 잘못된 객체나 중복 반환을 안전하게 검증·거부하는 API라고 안내하면 안 됩니다. objpool_push는 로컬 IRQ를 막고 현재 CPU slot에 이 helper를 호출한 뒤 복원합니다.'),
        ('Drop과 강제 free', 'objpool_drop은 객체를 재사용 큐에 돌려주는 push와 달리 객체를 버리고 pool 참조를 포기하는 외부 함수입니다. 계약상 pool이 해제되면 0, 남은 객체가 있으면 EAGAIN입니다. objpool_free는 모든 객체를 강제로 해제하는 외부 선언입니다. 이름이 비슷해도 push/drop/free를 같은 재사용 동작으로 취급하지 않습니다.'),
        ('Fini와 실행 중 객체', 'fini는 남은 free 객체들을 정리하고 추가 pool 참조를 내려놓습니다. 대여된 객체가 있으면 마지막 drop까지 전체 해제가 늦어질 수 있습니다. 주석은 fini 시 진행 중 push가 없어야 한다고 요구하고 보통 RCU로 이를 보장한다고 설명합니다. fini를 호출하면 동시에 진행 중인 모든 push를 자동으로 기다린다고 오해하면 안 됩니다.'),
        ('CS 연결과 검증 범위', '고정 용량 재사용, CPU 분산으로 경쟁 지점 줄이기, 예약/게시/소비의 단계 분리, CAS 소유권 확정, unsigned 순번 wrap, 객체와 관리자의 결합 수명을 학습합니다. 전체 헤더 대조는 모든 메모리 모델에서의 lockless 알고리즘 증명이나 실제 IRQ 경쟁 부하 시험을 대신하지 않습니다.')
    ],
    questions=[
        ('objpool_pop은 객체를 반환할 때마다 내용을 0으로 초기화하는가?', '아니다. 초기화 후 재사용 정리는 호출자 책임이다', '그렇다. 미리 할당한 객체라도 매번 memset한다', '헤더 계약은 초기 할당 시 zero와 objinit 한 번을 설명합니다. inline pop에는 객체 내용 초기화가 없습니다.'),
        ('tail 예약 직후 해당 객체가 이미 소비 가능하게 공개되었는가?', '아니다. entries 기록 후 last를 release store한다', '그렇다. tail CAS가 entries 쓰기보다 뒤에 실행된다', '생산자는 위치를 예약한 다음 값을 쓰고 last를 게시합니다. 서로 다른 단계와 순서를 확인해야 합니다.'),
        ('현재 CPU 슬롯이 비면 pop은 바로 NULL을 반환하는가?', '아니다. 다른 가능한 CPU 슬롯들도 순환 조사한다', '그렇다. CPU별 pool은 외부에서 접근할 수 없다', 'nr_possible_cpus만큼 cpumask_next_wrap을 이용해 탐색합니다. 첫 슬롯의 빈 상태와 전체 실패를 구분합니다.'),
        ('push helper의 용량 이상 경고가 발생하면 즉시 오류 코드로 중단하는가?', '아니다. 본문에는 그 중단 분기가 없고 마지막 반환은 0이다', '그렇다. WARN_ON_ONCE가 자동으로 EINVAL을 반환한다', '경고 매크로와 함수 제어 흐름은 다릅니다. 주석의 abort 설명보다 실제 CAS·쓰기 경로를 확인해야 합니다.'),
        ('objpool_fini 호출자가 보장해야 하는 동시성 조건은?', '진행 중인 objpool_push가 없어야 한다', '아무 조건도 없다. fini가 모든 사용자 작업을 자동 종료한다', '주석은 보통 RCU로 진행 중 push 완료를 기다리는 책임을 설명합니다. 대여된 객체는 이후 drop될 수 있습니다.')
    ]
)]
