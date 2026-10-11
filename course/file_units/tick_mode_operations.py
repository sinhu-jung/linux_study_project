"""Whole-file legacy tick and oneshot event management."""
ROWS = [dict(
    path='kernel/time/tick-legacy.c', title='Legacy tick: 시간 유지와 CPU 집계의 분리',
    intro='legacy_timer_tick 함수 전체에서 잠금 범위와 ticks=0 경로를 분석합니다.',
    principle='전역 시간 진행과 CPU별 프로세스 집계는 같은 interrupt 경로에 있어도 실행 조건이 다릅니다.',
    use='generic clockevents가 없는 플랫폼에서 누가 시간을 진행시키고 누가 CPU 사용을 집계하는지 이해합니다.',
    area='인터럽트 · raw spinlock · seqcount · 시간 집계 · 조건부 실행',
    sections=[
        ('전체 구성과 대상', 'GPL-2.0과 여러 아키텍처에서 공통화했다는 주석, irq/profile/timekeeper_internal과 tick-internal include 뒤 legacy_timer_tick 하나가 전부입니다. generic clockevents로 전환하지 않은 플랫폼을 위한 함수이며 Makefile은 LEGACY_TIMER_TICK으로 이 파일을 선택합니다.'),
        ('호출자 전제', '인자 ticks는 마지막 호출 뒤 경과한 tick 수이고 주석은 interrupts disabled 상태로 호출해야 한다고 명시합니다. 함수 자체가 local_irq_disable을 호출하지는 않습니다. raw_spin_lock을 사용한다고 interrupt 비활성 전제까지 자동으로 충족되는 것은 아닙니다.'),
        ('전역 시간 갱신 보호', 'ticks가 0이 아니면 jiffies_lock을 잡고 jiffies_seq의 write 구간을 연 뒤 do_timer(ticks)를 호출합니다. 이어 seqcount 구간을 닫고 spinlock을 풉니다. lock은 writer 직렬화, seqcount는 일관된 reader 관측에 연결되는 별도 역할이며 단순히 둘 중 하나를 불필요한 중복이라고 판단하면 안 됩니다.'),
        ('Wall time 갱신 위치', 'update_wall_time은 같은 if(ticks) 안에 있지만 jiffies_lock을 해제한 뒤 호출합니다. 따라서 함수 전체가 jiffies_lock 아래 실행된다고 설명하면 틀립니다. 여러 경과 tick을 do_timer에 전달하는 것과 후속 함수 호출 횟수를 ticks만큼 반복하는 것도 다릅니다.'),
        ('Ticks가 0이어도 하는 일', 'if 뒤의 update_process_times(user_mode(get_irq_regs()))와 profile_tick(CPU_PROFILING)은 항상 한 번 호출합니다. ticks=0은 이 CPU가 timekeeping을 담당하지 않는다는 주석의 경우이며 전체 함수가 아무 일도 하지 않는다는 뜻이 아닙니다. 프로세스 집계에 넘기는 user 여부는 interrupt register 문맥에서 얻습니다.'),
        ('검증 범위', '파일 전체의 분기와 호출 순서를 다뤘습니다. do_timer, update_wall_time, update_process_times의 내부 구현까지 이 파일 안에 있다고 세지 않습니다. 실제 interrupt 발생이나 시간 변경을 실행한 테스트도 아닙니다.')
    ],
    questions=[
        ('ticks=0이면 프로세스 시간 집계도 건너뛰는가?', '아니다. 프로세스 집계와 profiling은 실행한다', '그렇다. 함수가 즉시 반환한다', '두 호출은 if(ticks) 밖에 있습니다. 전역 timekeeping 참여 여부와 CPU 집계는 다른 조건입니다.'),
        ('update_wall_time은 jiffies_lock을 잡은 상태에서 호출하는가?', '아니다. 잠금을 해제한 뒤 호출한다', '그렇다. 모든 후속 집계까지 같은 잠금 아래 실행한다', 'write_seqcount_end와 raw_spin_unlock 다음에 위치합니다. 호출 순서뿐 아니라 잠금 경계를 함께 확인해야 합니다.'),
        ('인터럽트 비활성화는 누가 보장해야 하는가?', '호출자가 보장해야 한다', '이 함수가 항상 local_irq_disable을 실행한다', '주석에 호출 조건으로 명시되어 있고 본문에 해당 disable 호출은 없습니다.')
    ]
), dict(
    path='kernel/time/tick-oneshot.c', title='Oneshot tick: 다음 이벤트 예약과 장치 상태 전환',
    intro='이벤트 예약, resume/setup, 모드 전환·조회와 highres 진입 함수 전체를 읽습니다.',
    principle='장치 기능, 소프트웨어 tick 모드, 다음 만료 시각은 연결되어 있지만 서로 다른 상태입니다.',
    use='고해상도·tickless 경로에서 장치 정지와 재개, 모드 변경과 실제 이벤트 예약을 구분합니다.',
    area='상태 기계 · CPU별 데이터 · clockevent · sentinel · 인터럽트 · 오류 전달',
    sections=[
        ('전체 파일', 'GPL-2.0과 저작권 주석, 관련 include 뒤 program_event, resume_oneshot, setup_oneshot, switch_to_oneshot, mode_active, 조건부 init_highres의 여섯 함수가 있습니다. 현재 CPU의 tick_cpu_device 또는 전달된 clock_event_device를 조작하며 타이머 큐 자체의 삽입·삭제는 구현하지 않습니다.'),
        ('이벤트가 없다는 sentinel', 'tick_program_event는 현재 CPU evtdev를 읽습니다. expires==KTIME_MAX이면 clockevents_switch_state로 ONESHOT_STOPPED로 바꾸고 next_event=KTIME_MAX를 저장한 뒤 0입니다. 가장 먼 실제 시각의 하드웨어 이벤트를 예약하는 대신 장치를 더 이상 필요하지 않은 상태로 처리하는 특수 값입니다.'),
        ('정지 장치의 재개와 예약', '그 외 expires에서는 장치가 oneshot stopped인지 확인하고 맞으면 ONESHOT으로 전환합니다. 다음 clockevents_program_event(dev,expires,force)의 결과를 그대로 반환합니다. force는 호출자가 전달한 값이며 이 wrapper가 항상 true로 바꾸지는 않습니다. dev NULL 검사도 여기에는 없습니다.'),
        ('Resume의 의미', 'tick_resume_oneshot은 현재 CPU 장치를 ONESHOT으로 바꾸고 ktime_get() 시각으로 force=true 예약을 호출합니다. 이전 next_event를 읽어 같은 값을 복원하는 함수가 아닙니다. 반환형 void이며 program_event의 결과를 호출자에게 전달하지 않습니다.'),
        ('새 장치 설정', 'tick_setup_oneshot은 전달된 newdev의 event_handler를 저장하고 ONESHOT 상태로 전환한 뒤 전달된 next_event를 force=true로 예약합니다. 이 함수도 void입니다. 현재 CPU tick_device.mode를 직접 대입하거나 장치의 ONESHOT feature를 검사하는 코드는 이 함수 본문에 없습니다.'),
        ('모드 전환의 유효성 검사', 'tick_switch_to_oneshot은 현재 CPU tick_device와 evtdev를 얻고 장치가 없거나 ONESHOT feature가 없거나 functional하지 않으면 로그 후 EINVAL입니다. 장치가 없으면 별도 문구, 존재하지만 functional하지 않으면 해당 문구, 나머지는 oneshot 미지원 문구를 출력합니다. feature와 functional이 동시에 문제이면 로그는 functional 여부를 먼저 설명합니다.'),
        ('성공 전환의 순서', '성공하면 td->mode=TICKDEV_MODE_ONESHOT, dev->event_handler=handler를 대입하고 장치를 ONESHOT 상태로 바꾼 다음 tick_broadcast_switch_to_oneshot을 호출합니다. 이후 0을 반환합니다. 이 함수는 clockevents_program_event로 구체적인 다음 만료 시각을 직접 예약하지 않습니다. 상태 전환과 예약 함수를 구분합니다.'),
        ('로컬 모드 조회', 'tick_oneshot_mode_active는 local_irq_save로 interrupt 상태를 저장하고 비활성화한 구간에서 현재 CPU mode가 ONESHOT인지 비교한 뒤 local_irq_restore로 원래 상태를 복구합니다. 주석은 시스템의 nohz/highres 상태를 설명하지만 실제 읽는 대상은 현재 CPU의 mode 필드입니다. 모든 CPU를 순회하거나 장치 feature 비트를 조회하지 않습니다.'),
        ('Highres 진입', 'CONFIG_HIGH_RES_TIMERS일 때만 tick_init_highres를 정의하며 tick_switch_to_oneshot(hrtimer_interrupt)의 결과를 반환합니다. 주석은 interrupts disabled 호출 조건을 명시합니다. 이 함수 자체가 인터럽트를 끄거나 새로운 clockevent 장치를 할당하지는 않습니다.'),
        ('호출자 책임과 결과 전달', '유효 장치 확인은 switch 함수에 있고 다른 helper들에 동일하게 반복되지 않습니다. program_event와 switch/init_highres는 int 결과를 전달하지만 resume/setup은 void입니다. 상태 전환 API 호출과 설정 대입을 전부 rollback하는 트랜잭션도 이 파일에는 없습니다. 호출 문맥과 하위 helper 계약을 함께 읽어야 합니다.'),
        ('CS와 검증 범위', 'ONESHOT과 ONESHOT_STOPPED 상태, KTIME_MAX sentinel, CPU별 설정과 전체 시스템 설명의 차이, 상태 조회 중 interrupt 보호, 콜백 교체와 이벤트 예약의 분리를 학습합니다. 전체 소스 설명이며 실제 highres 전환이나 장치 interrupt를 실행 검증한 자료는 아닙니다.')
    ],
    questions=[
        ('tick_program_event의 expires가 KTIME_MAX이면?', '장치를 ONESHOT_STOPPED로 바꾸고 next_event에도 KTIME_MAX를 저장한다', '그 시각까지 반드시 하드웨어 카운터를 예약한다', '특수 값 분기는 일반 program_event 호출 없이 0을 반환합니다. 데이터 값이 제어 의미도 가집니다.'),
        ('tick_switch_to_oneshot은 구체적인 다음 만료 시각까지 직접 예약하는가?', '아니다. 모드·handler·장치 상태와 broadcast를 전환한다', '그렇다. 항상 next_event를 지금 시각으로 예약한다', '실제 예약 호출은 program_event, resume, setup에 있습니다. switch의 성공 반환과 이벤트 예약 완료를 구분합니다.'),
        ('mode_active는 모든 CPU의 mode를 조사하는가?', '아니다. interrupt를 보호하며 현재 CPU mode를 읽는다', '그렇다. 시스템 전체 CPU 목록을 순회한다', '__this_cpu_read 한 번으로 비교합니다. 주석의 상위 수준 설명보다 실제 접근 범위를 확인해야 합니다.'),
        ('resume_oneshot이 예약에 사용하는 시각과 force는?', 'ktime_get()과 true이다', '이전 next_event와 false이다', '본문은 현재 시각을 새로 읽어 강제 예약을 요청합니다. 과거 예약의 복구와 동일하지 않습니다.'),
        ('tick_init_highres에 전달되는 이벤트 handler는?', 'hrtimer_interrupt이다', 'NULL이며 이후 언제나 자동 생성된다', '조건부 wrapper가 tick_switch_to_oneshot에 이 함수를 직접 전달하고 그 결과를 반환합니다.')
    ]
)]
