"""Whole completion interface and scheduler implementation."""
ROWS = []


def add(path, title, intro, principle, use, sections, questions):
    ROWS.append(dict(path=path, title=title, intro=intro, principle=principle,
                     use=use, area='동기화 · 대기 큐 · 스케줄링 · 객체 수명',
                     sections=sections, questions=questions))


add('include/linux/completion.h', 'Completion 헤더 전체: 완료 상태와 대기 인터페이스',
    '완료 신호를 기다리는 스레드들이 공유하는 상태와 초기화·대기·알림 API를 선언합니다.',
    'done과 단순 대기 큐를 묶어 완료 통지를 저장합니다. 처음 초기화와 재사용을 위한 상태 초기화는 서로 다른 작업입니다.',
    '대기 API는 잠들 수 있으므로 적절한 실행 문맥과 객체 수명을 확보해야 합니다. 스택 선언 매크로가 비동기 작업 종료를 자동 보장하지 않습니다.',
    [('전체 구성', 'GPL-2.0, guard와 저작권, swait.h 포함, completion 구조체, map 및 acquire/release helper, 초기화 매크로와 LOCKDEP 분기, init/reinit inline, 대기·관측·완료 함수 선언으로 구성됩니다. 실제 스케줄링과 done 소비는 kernel/sched/completion.c에 있습니다.'),
     ('상태 자료구조', 'completion은 unsigned int done과 swait_queue_head wait로 구성됩니다. 주석은 대기 스레드를 FIFO로 큐에 넣는다고 설명합니다. done은 스레드 수나 완료시각 필드가 아니며 구체적인 누적 신호와 전체 완료 표식 의미는 구현이 정합니다.'),
     ('정적 초기화', 'COMPLETION_INITIALIZER(work)는 done0과 work.wait를 가리키는 swait 초기화식을 만듭니다. DECLARE_COMPLETION은 이를 사용해 구조체를 선언·초기화합니다. 단순한0 메모리 채우기만으로 대기 큐 초기화가 모두 대체되는 것은 아닙니다.'),
     ('스택과 lockdep', 'CONFIG_LOCKDEP가 켜지면 ONSTACK 변형은 statement expression에서 init_completion을 실행하는 비상수 초기화를 사용합니다. 꺼져 있으면 DECLARE_COMPLETION으로 매핑됩니다. ONSTACK_MAP도 해당 분기를 따르지만 이 버전의 init_completion_map(x,m)은 init_completion(x)으로 정의되어 map 인자를 실질적으로 사용하지 않습니다.'),
     ('이름과 실제 동작', 'complete_acquire와 complete_release는 이 헤더에서 빈 inline 함수입니다. 이름에 acquire/release가 있다는 이유만으로 이 함수들이 하드웨어 메모리 장벽을 실행한다고 설명하면 안 됩니다. 실제 상태 동기화는 구현의 잠금과 깨우기 경로를 확인해야 합니다.'),
     ('init과 reinit', 'init_completion은 done0 설정과 init_swait_queue_head를 모두 실행합니다. reinit_completion은 done만0으로 바꾸며 잠금을 잡거나 대기 큐를 다시 만들지 않습니다. 재사용 전에 이전 대기·알림 작업과 경쟁하지 않음을 보장해야 하며 특히 complete_all 뒤의 재사용에서 필요합니다.'),
     ('대기 함수군', '일반 및 IO 대기는 void, interruptible/killable/state는 int입니다. 비인터럽트 timeout과 IO timeout은 unsigned long, interruptible/killable timeout은 long입니다. 음수 인터럽트 오류를 표현해야 하는 변형과 단순 timeout 반환 형식의 차이를 구분합니다. 시간 단위와 성공 반환값은 구현 문서를 함께 읽습니다.'),
     ('비대기와 알림 선언', 'try_wait_for_completion과 completion_done은 bool이며 소비 시도와 관측의 차이가 있습니다. complete, complete_on_current_cpu, complete_all은 void 알림 함수입니다. 헤더는 함수 선언만 제공하며 complete_all 뒤 모든 대기자의 후속 처리까지 끝났다는 보증을 주지 않습니다.'),
     ('CS 연결', '상태와 대기 큐의 결합, 정적·동적 초기화, 조건부 컴파일, 반환형의 오류 표현, 스택 객체와 비동기 수명을 학습합니다. 일부 선언만 연결한 수업이 아니라 이 파일의 매크로와 inline도 함께 다룹니다.')],
    [('reinit_completion이 대기 큐까지 다시 초기화하는가?', '아니다. done만0으로 설정한다', '그렇다. init_completion과 본문이 같다', 'init_completion은 큐 초기화도 하지만 reinit은 단일 저장뿐입니다. 재사용 시 남은 대기자·알림자와의 경쟁을 호출자가 해결해야 합니다.'),
     ('이 버전의 complete_acquire는 실제 장벽을 실행하는가?', '아니다. 빈 inline이다', '그렇다. 이름만으로 acquire 장벽이 보장된다', '실제 본문이 비어 있습니다. 상태 동기화는 completion.c의 잠금과 깨우기 절차에서 확인해야 합니다.'),
     ('interruptible_timeout의 반환형이 long인 이유와 연결되는 동작은?', '시간 초과0·성공 양수 외에 음수 인터럽트 오류를 반환할 수 있다', '완료된 스레드 주소를 반환한다', '인터럽트 가능한 대기는 -ERESTARTSYS를 반환할 수 있습니다. 이를 unsigned로만 해석하면 오류와 큰 양수 성공을 혼동할 수 있습니다.')])

add('kernel/sched/completion.c', 'Completion 구현 전체: 신호 소비와 대기 경쟁',
    '완료 알림을 누적하고 대기 큐를 깨우며, 시간 초과·신호 중단·비대기 소비를 처리합니다.',
    'done과 큐를 같은 raw spinlock으로 보호하고 잠들기 전에 잠금을 놓습니다. UINT_MAX는 소비되지 않는 전체 완료 표식이며 성공 반환과 timeout을 구별합니다.',
    'completion은 보통 상호 배제보다 동기화 지점입니다. 기다리기가 끝나거나 시간이 초과되어도 다른 실행 주체가 구조체를 더 사용할 수 있으므로 별도의 수명 계약이 필요합니다.',
    [('전체 구성', 'GPL-2.0과 설계 주석 뒤 알림 공통 함수, current CPU/일반/전체 알림, 공통 대기 내부 함수와 스케줄러 선택, 아홉 대기 wrapper, try_wait와 completion_done이 있습니다. public 함수들은 EXPORT_SYMBOL을 사용하지만 이 파일의 complete_on_current_cpu에는 별도 EXPORT_SYMBOL이 없습니다. 원문 자체에는 include 행이 없어 단독 사용자 공간 소스처럼 컴파일하는 파일로 해석하지 않습니다.'),
     ('일반 완료 알림', 'complete_with_flags는 wait.lock을 raw_spin_lock_irqsave로 잡습니다. done이 UINT_MAX가 아니면1 증가시키고 swake_up_locked로 한 대기자를 깨운 뒤 IRQ 상태를 복원합니다. 대기자가 아직 없어도 done이 남아 나중의 대기가 소비할 수 있습니다. complete는 wake_flags0, complete_on_current_cpu는 WF_CURRENT_CPU를 전달하며 완료 대상을 다른 completion으로 바꾸는 함수가 아닙니다.'),
     ('전체 완료 알림', 'complete_all은 RT 문맥 lockdep 검사를 수행하고 잠금 안에서 done=UINT_MAX, swake_up_all_locked를 실행합니다. 이후 대기들도 표식을 소비하지 않아 계속 통과할 수 있습니다. 재사용은 모든 이전 대기자가 깨어나 완료한 것을 별도로 보장한 뒤 reinit해야 합니다. complete_all 호출만으로 그들이 이미 CPU에서 후속 작업을 끝냈다는 뜻은 아닙니다.'),
     ('대기 공통 진입', '__wait_for_common은 might_sleep, 빈 complete_acquire hook, raw_spin_lock_irq, do_wait_for_common, unlock_irq, 빈 release hook 순서입니다. 기다리는 경로는 잠들 수 있고 IRQ 저장·복원이 아닌 lock_irq/unlock_irq를 쓰므로 IRQ를 꺼둔 문맥에서 무심코 호출해서는 안 됩니다. 알림 경로의 irqsave 사용과 구별합니다.'),
     ('큐 등록과 수면', 'done이0이면 지역 swait 항목을 선언합니다. 반복에서 signal_pending_state를 확인한 뒤 큐 등록, current 상태 설정, 잠금과 IRQ 해제, action(timeout)으로 수면, 잠금 재획득 순서로 진행합니다. done이 없고 timeout이 남으면 반복합니다. 큐 등록과 상태 확인을 같은 잠금 아래 수행해 알림과 수면 진입 사이의 경쟁을 조정합니다.'),
     ('대기 정리와 반환', '루프가 끝나면 __finish_swait로 항목을 정리합니다. 여전히 done이0이면 timeout 또는 -ERESTARTSYS를 반환합니다. done이 있으면 UINT_MAX가 아닌 경우 하나 감소시키고 timeout ?: 1을 반환합니다. 시간 잔여량이0이어도 완료 상태를 소비했다면1을 돌려 timeout0과 구별합니다.'),
     ('신호 검사와 완료 상태', '신호 확인은 done0으로 대기 루프에 들어왔을 때 수행합니다. 이미 완료 신호가 준비되어 있으면 루프를 건너뛰어 소비하므로 pending signal이 있다는 사실만으로 모든 호출이 반드시 -ERESTARTSYS가 되는 것은 아닙니다. 정상적인 잠금 규칙 아래 신호 중단과 완료 소비 중 어느 상태를 확인했는지에 따라 반환을 이해합니다.'),
     ('스케줄러 동작 선택', 'wait_for_common은 schedule_timeout, wait_for_common_io는 io_schedule_timeout을 action으로 전달합니다. IO 변형은 호출자를 IO 대기로 회계 처리하는 점이 다르며 다른 형태의 완료 객체나 별도 done 알고리즘을 만들지 않습니다.'),
     ('비인터럽트 wrapper', 'wait_for_completion과 io는 MAX_SCHEDULE_TIMEOUT과 TASK_UNINTERRUPTIBLE을 사용하고 결과를 반환하지 않습니다. timeout 및 io_timeout은 지정 jiffies와 같은 태스크 상태를 사용해0이면 시간 초과, 양수이면 완료를 반환합니다. 양수는 남은 jiffies 또는 최소1이지 소요 시간이나 완료한 스레드 수가 아닙니다.'),
     ('인터럽트·killable·state wrapper', 'interruptible은 TASK_INTERRUPTIBLE, killable은 TASK_KILLABLE, state는 전달한 상태를 사용합니다. 시간 제한 없는 세 함수는 공통 결과가 -ERESTARTSYS이면 그 오류를, 아니면0을 반환합니다. timeout 두 변형은 공통 long 결과를 그대로 반환해 음수 중단·0초과·양수 완료를 구별합니다. killable은 일반적인 모든 신호와 동일한 중단 조건으로 해석하지 않습니다.'),
     ('비대기 소비', 'try_wait_for_completion은 READ_ONCE(done)가0이면 잠금 없이 false입니다. 양수 관측이면 irqsave 잠금을 잡고 다시 done을 검사해 경쟁 소비를 확인합니다. 여전히 양수이면 UINT_MAX를 제외하고 감소한 뒤 true입니다. 첫 관측 직후 새 알림이 와도 이번 호출이 false일 수 있으며 이는 미래 상태를 예약하는 API가 아닙니다.'),
     ('completion_done의 실제 의미', '이 함수는 READ_ONCE(done)가0이면 false, 아니면 wait.lock을 한 번 잡았다 놓고 true입니다. done을 감소시키지 않고 잠금 안에서 다시 읽지도 않으며 대기 큐 길이를 검사하지 않습니다. kernel-doc의 대기자 유무 설명을 실제 대기자 수 검사로 해석하면 틀립니다. 특히 complete_all 뒤 true여도 이전 대기자가 아직 진행 중일 수 있습니다.'),
     ('관측과 객체 해제의 경계', 'completion_done의 잠금 왕복은 완료를 기록한 complete가 아직 해당 잠금 아래 구조체를 만지는 구간을 지나도록 동기화하려는 목적이라는 주석이 있습니다. 그렇다고 미래 알림자·다른 대기자·소비자를 모두 종료시키는 수명 장벽은 아닙니다. 경쟁 소비 후에도 재검사 없이 true일 수 있으므로 성공한 try_wait와도 다릅니다.'),
     ('깨우기 순서와 공정성', 'complete 문서는 큐에 들어간 순서대로 한 대기자를 깨운다고 설명합니다. 깨우기 순서가 곧 모든 CPU에서 후속 작업까지 끝나는 순서는 아니며 새 비대기 소비자와의 경쟁도 별도입니다. 주석의 깨울 때 태스크 상태 접근 전 full barrier 설명은 실제 wakeup 경로에 관한 것이고 빈 acquire/release hook이 그 장벽이라는 뜻은 아닙니다.'),
     ('CS 연결과 검증 범위', '누적 알림과 일회성 이벤트의 차이, 조건 검사와 수면 등록, 소비 경쟁, 특수 표식, timeout의 경계 반환, wakeup과 실행 완료의 차이, 비동기 객체 수명을 학습합니다. 이 파일의 전체 경로를 읽어 해설했으며 실제 스케줄러·IRQ·RT의 모든 경쟁 실행을 실험한 결과는 아닙니다.')],
    [('대기자가 없을 때 complete를 두 번 호출하면 뒤의 일반 대기 두 번은?', 'done에 남은 두 알림을 각각 소비할 수 있다', '깨울 스레드가 없었으므로 두 알림은 모두 사라진다', 'complete는 큐를 깨우기 전에 done을 증가시킵니다. 일반 성공 대기는 하나씩 감소하므로 먼저 온 완료 신호도 보존됩니다.'),
     ('complete_all 뒤 성공한 대기가 done을 하나씩 줄이는가?', '아니다. UINT_MAX 표식은 감소하지 않는다', '그렇다. 마지막 대기자 뒤 자동으로0이 된다', '공통 대기와 try_wait 모두 UINT_MAX를 감소 대상에서 제외합니다. 이후 재사용에는 안전한 시점의 reinit이 필요합니다.'),
     ('timeout 잔여량이0인데 잠금을 다시 잡았을 때 완료를 소비했다면 반환은?', '최소1로 성공을 나타낸다', '반드시0으로 실패를 나타낸다', '성공 끝부분은 timeout ?: 1입니다. 완료를 소비한 호출과 완료 없이 시간만 지난 호출을 반환값0으로 혼동하지 않게 합니다.'),
     ('try_wait가 첫 관측에서 양수를 보았으면 잠금 뒤 무조건 성공하는가?', '아니다. 다른 소비자가 가져갔을 수 있어 다시 검사한다', '그렇다. READ_ONCE가 완료 신호를 예약한다', '잠금 안에서 done0이면 false로 바꿉니다. 관측은 소비 권한 확보가 아니며 실제 감소는 잠금 아래 수행합니다.'),
     ('completion_done이 true이면 complete_all로 깨운 모든 스레드가 실행을 끝냈는가?', '아니다. 대기자 종료 여부를 검사하지 않는다', '그렇다. 내부에서 모든 스레드 종료를 기다린다', '함수는 done 관측과 잠금 왕복만 합니다. complete_all은 UINT_MAX를 남기므로 아직 깨어나 처리 중인 대기자가 있어도 true일 수 있습니다.'),
     ('interruptible_timeout 반환을 단순 if(ret)로 성공 판정해도 되는가?', '안 된다. 음수 -ERESTARTSYS도 참으로 해석된다', '된다.0이 아닌 모든 값은 완료 성공이다', '이 변형은 음수 중단,0시간 초과,양수 완료의 세 범주입니다. 부호와0 여부를 구분해야 합니다.'),
     ('IO 대기 변형이 사용하는 핵심 차이는?', '수면 action을 io_schedule_timeout으로 선택해 IO 대기로 회계 처리한다', 'done 대신 별도의 파일 디스크립터를 기다린다', '공통 완료 상태와 대기 루프는 공유합니다. IO 변형은 스케줄러에 전달하는 수면 함수가 다릅니다.')])
