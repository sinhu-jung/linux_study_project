"""Whole-file hrtimer-backed broadcast clockevent device."""
ROWS = [dict(
    path='kernel/time/tick-broadcast-hrtimer.c',
    title='Hrtimer broadcast: 가상 clockevent와 callback 대기 회피',
    intro='shutdown·다음 이벤트 설정·가상 장치·callback·등록의 전체 흐름을 분석합니다.',
    principle='잠금을 잡은 상태에서 그 잠금을 필요로 하는 callback의 완료를 기다리면 순환 대기가 생길 수 있습니다.',
    use='tick broadcast의 CPU 소유권과 타이머 취소·재예약 계약을 이해합니다.',
    area='타이머 · clockevent · 순환 대기 · CPU affinity · callback · 상태 관리',
    sections=[
        ('전체 구성', 'GPL-2.0과 가상 clock 장치 설명, include 뒤 정적 bctimer 하나를 둡니다. bc_shutdown, bc_set_next, ce_broadcast_hrtimer 장치 정의, bc_handler, tick_setup_hrtimer_broadcast가 전부입니다. CPU마다 별개의 bctimer 배열을 만드는 파일이 아니라 하나의 정적 타이머와 가상 장치를 연결합니다.'),
        ('Shutdown의 취소 방식', 'bc_shutdown은 evt 인자를 직접 사용하지 않고 hrtimer_try_to_cancel(&bctimer)를 호출한 뒤 0입니다. 실행 중 callback의 종료까지 기다리는 hrtimer_cancel을 사용하지 않습니다. try_to_cancel 결과도 반환하지 않으므로 shutdown이 0을 반환했다고 모든 callback이 이미 끝났다는 의미는 아닙니다.'),
        ('주석의 순환 대기 사례', 'CPU0이 broadcast lock을 잡은 동안 CPU1의 hrtimer interrupt가 bc_handler를 거쳐 broadcast handler에서 같은 lock을 기다릴 수 있습니다. CPU0이 이때 동기 취소로 callback 완료를 기다리면 서로의 진행을 기다립니다. 주석은 이를 live lock 시나리오라고 부르며 핵심은 lock 보유와 callback 대기 사이의 순환 의존입니다.'),
        ('다음 이벤트의 호출 문맥', 'bc_set_next는 가장 이른 broadcast 이벤트를 가진 CPU의 idle 진입·이탈 또는 broadcast handler에서 호출되며 주석상 항상 tick_broadcast_lock이 잡혀 있습니다. idle 경로는 앞의 순환 대기 문제, callback 경로는 자기 자신의 종료를 기다리는 문제가 있으므로 여기서도 hrtimer_cancel을 호출할 수 없다고 설명합니다.'),
        ('절대·고정 CPU·hard 모드', 'hrtimer_start에 expires와 HRTIMER_MODE_ABS_PINNED_HARD를 넘깁니다. 절대 만료 시각이며 호출 CPU에 고정해 예약하려는 모드입니다. 그러나 callback이 이미 실행 중이면 hrtimer_start가 타이머를 옮길 수 없어 기존 CPU에 남는다는 조건이 주석에 있습니다. PINNED만 보고 매번 현재 CPU로 반드시 옮겨진다고 판단하면 안 됩니다.'),
        ('실제 CPU를 bound_on에 기록', 'start 뒤 bc->bound_on에 bctimer.base->cpu_base->cpu를 저장합니다. 현재 CPU 번호를 무조건 대입하지 않는 이유는 실행 중 callback 때문에 이동하지 못한 경우를 반영하기 위해서입니다. broadcast core는 이 정보를 통해 타이머를 맡은 CPU가 deep idle에 들어가지 않도록 합니다. 주석상 broadcast lock이 base 변경을 막으므로 이 읽기에 별도의 hrtimer base lock을 잡지 않습니다.'),
        ('가상 장치의 함수와 feature', 'ce_broadcast_hrtimer의 이름은 bc_hrtimer, shutdown 함수는 bc_shutdown, 다음 ktime 설정 함수는 bc_set_next입니다. feature는 ONESHOT, KTIME, HRTIMER의 OR입니다. rating=0, 초기 bound_on=-1이며 event_handler는 이 initializer에서 직접 지정하지 않습니다. callback이 사용할 handler는 clockevent/broadcast 연결 문맥에서 준비되어야 합니다.'),
        ('장치 범위와 환산', 'min_delta_ns=1, max_delta_ns=KTIME_MAX, min_delta_ticks=1, max_delta_ticks=ULONG_MAX, mult=1, shift=0입니다. cpumask는 cpu_possible_mask입니다. 이 마스크가 각 CPU마다 동시에 타이머를 복제해 실행한다는 뜻은 아닙니다. 가능 CPU 범위와 실제 타이머를 맡은 bound_on은 서로 다른 정보입니다.'),
        ('Callback 전달과 반환', 'bc_handler는 전달된 hrtimer 포인터를 직접 쓰지 않고 ce_broadcast_hrtimer.event_handler에 가상 장치 주소를 넘겨 호출합니다. 이후 HRTIMER_NORESTART입니다. 여기서 주기적으로 forward해 자동 재시작하는 코드는 없지만, 호출한 broadcast handler가 필요에 따라 명시적으로 다음 이벤트를 설정할 수 있다는 것과 NORESTART는 구분해야 합니다.'),
        ('초기화와 등록', 'tick_setup_hrtimer_broadcast는 CLOCK_MONOTONIC과 HRTIMER_MODE_ABS_HARD로 bctimer를 초기화하고 function=bc_handler를 저장한 뒤 clockevents_register_device를 호출합니다. 초기화 모드와 실제 start의 PINNED 모드를 혼동하지 않습니다. 반환형 void이고 이 파일 안에 별도 동적 할당이나 해제 함수는 없습니다.'),
        ('CS와 검증 범위', '전체 파일의 선언과 함수들을 다뤘습니다. callback 대기와 잠금의 의존성 그래프, 요청한 CPU와 실제 base CPU의 차이, 가상 장치를 통한 handler 재사용, 취소 시도와 완료의 차이가 핵심입니다. 하위 hrtimer와 broadcast core 전체를 작성 완료로 세거나 실제 CPU idle 전환을 실행 검증한 결과로 표시하지 않습니다.')
    ],
    questions=[
        ('bc_shutdown이 hrtimer_cancel 대신 try_to_cancel을 쓰는 이유는?', 'broadcast lock을 기다리는 callback과 순환 대기가 생길 수 있기 때문이다', 'try_to_cancel이 모든 callback 종료를 더 강하게 보장하기 때문이다', '동기 취소는 callback 완료를 기다립니다. 잠금을 가진 호출자와 그 잠금이 필요한 callback 사이의 대기 관계를 피해야 합니다.'),
        ('PINNED start 뒤 bound_on을 항상 현재 CPU로 써도 되는가?', '아니다. callback 실행 중이면 타이머가 기존 CPU에 남을 수 있다', '그렇다. PINNED 플래그가 진행 중 callback도 즉시 이동시킨다', '코드는 start 뒤 실제 bctimer base의 CPU를 읽습니다. 요청 affinity와 확정된 실행 위치를 구분합니다.'),
        ('bc_handler의 반환값은?', 'HRTIMER_NORESTART이다', '매번 HRTIMER_RESTART로 주기를 자동 반복한다', '이 wrapper는 가상 장치 handler를 호출하고 NORESTART입니다. 하위 handler의 명시적 재예약 가능성과 자동 재시작 반환을 구분합니다.'),
        ('이 파일이 CPU마다 하나씩 bctimer를 정의하는가?', '아니다. 정적 bctimer 하나를 정의한다', '그렇다. cpu_possible_mask가 타이머 객체를 자동 복제한다', 'cpumask는 장치 정보이고 객체 선언은 static struct hrtimer 하나입니다. 실제 담당 CPU는 bound_on으로 별도 기록합니다.'),
        ('bc_shutdown의 0 반환으로 실행 중 callback 종료까지 확인할 수 있는가?', '아니다. try_to_cancel의 결과를 사용하지 않고 0을 반환한다', '그렇다. 0은 모든 callback 완료를 반드시 뜻한다', '반환값의 의미는 실제 본문에서 확인해야 합니다. 비동기적인 취소 시도와 완료 대기는 다릅니다.')
    ]
)]
