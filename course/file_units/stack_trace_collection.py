"""Complete stacktrace interface and generic implementation."""
ROWS = [dict(
    path='include/linux/stacktrace.h',
    title='호출 스택 인터페이스: 수집·출력·신뢰성의 계약',
    intro='아키텍처 순회 callback과 공통 수집 API, 이전 인터페이스 및 기능 미지원 경로를 전체 헤더로 학습합니다.',
    principle='프레임을 수집했다는 사실과 전체 trace가 신뢰 가능하다는 보장은 다른 계약입니다.',
    use='할당 이력이나 진단 기능에서 알맞은 stack 수집 API를 선택합니다.',
    area='콜백 · 버퍼 용량 · 아키텍처 추상화 · 수명 보호 · 오류 계약',
    sections=[
        ('전체 구성', 'GPL-2.0, guard, types.h와 asm/errno.h, task_struct와 pt_regs 전방 선언 뒤 세 구성 영역이 있습니다. ARCH_STACKWALK 영역은 아키텍처 순회, STACKTRACE 영역은 공통 저장·출력과 구형 인터페이스, 마지막 영역은 reliable 함수의 지원 여부를 다룹니다. 모두 동일한 ifdef 하나에 포함된 것이 아닙니다.'),
        ('Callback의 반환 의미', 'stack_trace_consume_fn은 cookie와 unsigned long 주소를 받는 bool 함수 포인터입니다. true는 저장했거나 건너뛰었으므로 계속할 수 있다는 뜻입니다. false는 저장 공간 부족에 따른 중단을 표현합니다. 따라서 true가 반환된 호출 수를 실제 저장된 프레임 수로 세면 안 됩니다. cookie는 호출자가 넘긴 상태 포인터이며 순회가 이를 다시 callback으로 전달합니다.'),
        ('아키텍처 순회', 'arch_stack_walk는 callback, cookie, task, regs를 받습니다. 표는 task와 NULL regs 조합으로 task stack을, current와 regs 조합으로 지정 register의 stack pointer에서 시작하는 경우를 설명합니다. 인자에 NULL이 가능하다는 설명만으로 모든 조합의 의미를 임의로 만들어서는 안 됩니다. arch_stack_walk_user는 const pt_regs와 callback을 받습니다.'),
        ('Reliable 저수준 계약', 'arch_stack_walk_reliable은 신뢰할 수 없는 stack 특성을 발견하면 오류를 반환하고 성공 시 신뢰성을 보장하는 계약입니다. current가 아닌 task라면 호출자가 task의 비활성 상태와 stack pin을 보장해야 합니다. 일반 walk와 같은 void 반환이 아닙니다. 헤더에는 실제 unwind나 오류 감지 알고리즘이 없습니다.'),
        ('공통 API의 단위', 'STACKTRACE이면 print와 snprint, 현재 task save, 지정 task save_tsk, regs 기반 save_regs, 사용자 save_user, filter_irq_stacks를 선언합니다. save 계열의 store는 unsigned long 배열이고 size는 엔트리 용량이며 반환도 프레임 수입니다. snprint의 버퍼 크기는 바이트 단위입니다. save_user에는 skipnr 인자가 없고 다른 세 일반 save에는 있습니다.'),
        ('구형 아키텍처 인터페이스', 'STACKTRACE이면서 ARCH_STACKWALK가 아니면 stack_trace 구조가 nr_entries, max_entries, entries, skip을 가지며 save_stack_trace, regs, tsk, reliable, user의 이전 함수 선언이 제공됩니다. 주석은 generic 코드에서 이 내부 인터페이스를 직접 사용하지 말라고 합니다. 공통 wrapper와 아키텍처 backend를 분리하기 위한 경계입니다.'),
        ('Reliable 미지원', 'STACKTRACE와 HAVE_RELIABLE_STACKTRACE가 둘 다 있을 때만 stack_trace_save_tsk_reliable의 외부 선언을 제공합니다. 아니면 같은 이름의 inline이 -ENOSYS를 반환합니다. 0개의 신뢰 가능한 stack과 기능 자체의 미지원은 반환값이 다릅니다. 다른 save 함수들까지 모두 같은 fallback을 갖는다고 일반화하지 않습니다.'),
        ('CS 연결', '생산자와 소비자를 callback으로 분리하는 순회, 버퍼 용량과 실제 길이, 플랫폼별 backend, 정상 빈 결과와 오류의 구분을 학습합니다. 신뢰성 보장은 호출자의 task 안정성 조건을 지켰을 때의 API 계약이며 이 헤더만으로 모든 아키텍처 구현을 검증한 것은 아닙니다.')
    ],
    questions=[
        ('consume callback의 true는 반드시 한 프레임 저장을 뜻하는가?', '아니다. 건너뛴 경우에도 true일 수 있다', '그렇다. true 횟수가 저장 길이이다', '헤더는 consumed or skipped라고 명시합니다. 계속 순회할 수 있는지와 저장량을 구분합니다.'),
        ('저수준 reliable walk로 다른 task를 조사할 때 필요한 조건은?', 'task가 비활성이고 stack이 pin되어 있어야 한다', 'task 포인터만 있으면 언제나 충분하다', '헤더의 caller 계약입니다. 객체 주소가 있다는 사실만으로 실행 상태나 stack 수명이 고정되지 않습니다.'),
        ('reliable 기능이 없는 구성에서 공통 reliable 함수는?', '-ENOSYS를 반환한다', '성공한 빈 stack인 0을 반환한다', '지원하지 않는 기능과 신뢰 가능한 빈 결과는 별개입니다. inline fallback의 음수 오류를 확인해야 합니다.')
    ]
), dict(
    path='kernel/stacktrace.c',
    title='호출 스택 공통 구현: skip·task pin·출력 잘림·IRQ 경계',
    intro='두 아키텍처 인터페이스의 wrapper, 출력 함수, 수집 callback과 interrupt 필터를 전체 구현에서 추적합니다.',
    principle='프레임 수, 출력 요구 길이, 실제 버퍼 기록량을 구분하고, stack pin과 task 실행 정지를 별개의 조건으로 봅니다.',
    use='stack depot에 전달되는 배열과 진단 문자열의 생성 과정을 이해합니다.',
    area='경계 검사 · 콜백 상태 · 문자열 잘림 · task 수명 · 조건부 backend',
    sections=[
        ('전체 구조와 출력', 'GPL-2.0-only와 작성자 주석, include 뒤 print/snprint, ARCH_STACKWALK와 이전 backend 분기, 공통 IRQ 필터가 있습니다. print는 entries가 NULL이면 WARN_ON 후 반환하고 각 주소를 %pS로 심볼 형식 출력합니다. 포맷은 %*c 폭 1+spaces로 공백 문자를 출력하므로 spaces=0이어도 선행 공백 한 개가 있습니다. 이 출력 함수와 snprint는 GPL 심볼로 export됩니다.'),
        ('Snprint의 실제 반환 길이', 'snprint는 NULL entries면 경고 후 0입니다. 각 프레임에 snprintf를 호출하고 반환값 generated를 total에 더합니다. generated가 남은 size 이상이면 남은 공간을 0으로 만들어 반복을 끝냅니다. 따라서 반환값은 실제 저장 바이트 수를 초과할 수 있고 잘린 첫 프레임까지의 요구 길이이며, 아직 시도하지 않은 나머지 프레임 전체의 요구 길이까지 계산한 것은 아닙니다. 헤더의 bytes printed라는 문구만으로 완전한 실제 기록량이라고 해석하면 안 됩니다.'),
        ('수집 상태 cookie', 'ARCH_STACKWALK에서는 store, size, skip, len을 가진 cookie를 사용합니다. 기본 callback은 len>=size이면 false, skip이 있으면 감소시키고 true, 그 밖에는 주소를 store[len++]에 기록한 뒤 len<size를 반환합니다. 마지막 빈 칸을 채운 호출은 저장에 성공하면서도 false를 반환해 순회를 멈춥니다. size=0이면 skip도 처리하기 전에 false입니다.'),
        ('Scheduler 프레임 제외', 'nosched callback은 in_sched_functions(addr)이면 true를 반환하여 저장하지 않습니다. 이 경우 기본 callback에 들어가지 않아 skip도 감소하지 않습니다. 그러므로 skipnr는 scheduler 프레임을 포함한 모든 원시 입력 주소 수와 같지 않을 수 있습니다. 이 필터는 지정 task의 일반 수집 경로에 사용됩니다.'),
        ('현재 task와 regs 수집', 'stack_trace_save는 skipnr+1로 자기 wrapper 프레임을 추가로 건너뛰고 arch_stack_walk에 current와 NULL regs를 전달합니다. save_regs는 skipnr 그대로, current와 제공된 regs를 전달합니다. 둘 다 c.len을 반환합니다. 같은 skipnr여도 시작 기준과 자동 추가 skip이 다릅니다. save는 GPL export이며 이 파일의 save_regs에는 같은 export 줄이 없습니다.'),
        ('지정 task의 일반 수집', 'save_tsk는 nosched callback을 사용하고 대상이 current일 때만 skip에 1을 더합니다. try_get_task_stack 실패 시 0이며 성공하면 walk 후 put_task_stack합니다. stack을 pin하는 것은 task를 실행 중지시키는 것과 다릅니다. 이 wrapper를 다른 task의 완전한 시점 일관성 보장 함수로 설명하지 않습니다. 이 함수도 GPL export입니다.'),
        ('Reliable 수집', 'HAVE_RELIABLE_STACKTRACE이면 일반 callback과 skip 기본 0으로 arch_stack_walk_reliable을 호출합니다. try_get_task_stack에 실패한 task는 주석상 zombie 등 stack이 없는 경우로 신뢰 가능한 빈 결과 0을 반환합니다. walk 후 pin을 해제하고 오류가 있으면 오류, 없으면 c.len을 반환합니다. 다른 task가 비활성임을 보장하는 책임은 호출자에게 남아 있습니다.'),
        ('사용자 stack', 'USER_STACKTRACE_SUPPORT이면 현재 task가 PF_KTHREAD일 때 0을 반환하고, 아니면 task_pt_regs(current)를 arch_stack_walk_user에 전달합니다. skip은 0입니다. 커널 스레드에 사용자 register 기반 stack을 무조건 적용하지 않습니다. 사용자의 임의 배열 주소를 인자로 받아 직접 순회하는 형태도 아닙니다.'),
        ('이전 backend와 weak fallback', 'ARCH_STACKWALK가 없으면 save_stack_trace_tsk와 save_stack_trace_regs의 weak 기본 구현이 한 번 경고하고 끝납니다. 실제 아키텍처 구현이 대체할 수 있습니다. 여기서 모든 backend 함수의 weak fallback을 정의하는 것은 아닙니다. generic wrapper는 stack_trace 구조를 만들고 이전 save_stack_trace 계열을 호출하여 nr_entries를 반환합니다.'),
        ('이전 wrapper의 차이', '현재 task save는 skipnr+1, task save는 skipnr+(current==task), regs save는 skipnr를 전달합니다. reliable은 backend 반환 오류를 우선하고 아니면 nr_entries입니다. user는 지원 구성에서 이전 user 함수를 호출합니다. 이 분기의 generic task wrapper에는 새 분기와 같은 try_get_task_stack이나 nosched callback이 직접 있지 않으므로 backend 동작을 읽지 않고 두 경로가 완전히 동일하다고 말하면 안 됩니다.'),
        ('IRQ 코드 구간', 'in_irqentry_text는 주소가 __irqentry_text_start 이상 end 미만이거나 softirq의 같은 반열린 구간 안에 있는지 검사합니다. 끝 주소 자체는 포함하지 않습니다. 함수 이름 문자열을 검색하는 것이 아니라 링크된 코드 영역 경계로 판단합니다.'),
        ('필터의 반환과 배열 보존', 'filter_irq_stacks는 처음 IRQ/softirq entry 영역에 해당하는 프레임을 찾으면 i+1을 반환하여 그 진입 함수 자체는 포함합니다. 없으면 원래 nr_entries입니다. entries 배열의 내용을 지우거나 재배치하지 않으며 사용자가 반환 길이를 적용해야 잘린 prefix가 됩니다. 예를 들어 0부터 센 인덱스 3에서 처음 발견하면 반환 길이는 4입니다. 이 함수는 GPL 심볼로 export됩니다.'),
        ('CS 연결과 검증 범위', '상태를 가진 callback의 중단 규칙, 공간과 길이의 구분, 라이브 객체의 pin과 실행 안정성, 구형 backend 어댑터, prefix 필터를 학습합니다. 일반 출력은 프레임 수에 비례하고 IRQ 필터는 첫 매칭까지 선형 탐색합니다. 전체 소스 대조는 실제 아키텍처 unwinder의 정확성 시험과는 별개입니다.')
    ],
    questions=[
        ('마지막 배열 칸을 채운 consume callback은 무엇을 반환하는가?', 'false로 반환하여 추가 순회를 중단한다', '저장 성공이므로 반드시 true이다', '저장 후 len<size를 반환합니다. 저장 성공과 계속 순회 여부는 같은 질문이 아닙니다.'),
        ('nosched callback이 scheduler 주소를 건너뛰면 skip도 감소하는가?', '아니다. 기본 callback에 들어가지 않고 true를 반환한다', '그렇다. 원시 프레임을 보았으므로 항상 감소한다', 'scheduler 판별이 먼저입니다. skip의 적용 대상이 필터 전 전체 입력과 같다고 가정하면 안 됩니다.'),
        ('snprint 반환값이 버퍼에 실제 저장된 문자 수보다 클 수 있는가?', '그렇다. snprintf의 요구 길이를 total에 더한다', '아니다. 항상 버퍼 크기 안의 실제 기록량이다', '잘린 프레임도 snprintf가 반환한 길이를 더합니다. 다만 그 뒤 프레임은 순회를 중단하여 전체 stack의 최종 요구 크기까지 계산하지 않습니다.'),
        ('IRQ 진입 프레임이 인덱스 3이면 filter_irq_stacks 결과는?', '4이며 진입 프레임을 포함한다', '3이며 진입 프레임은 제외한다', '본문은 i+1을 반환하고 주석도 irqentry 자체를 포함한다고 명시합니다. 배열 자체는 수정하지 않습니다.'),
        ('try_get_task_stack 성공은 task가 실행 중지되었다는 뜻인가?', '아니다. stack 수명 보호와 task 비활성 상태는 별개이다', '그렇다. stack pin이 task 실행을 자동 정지시킨다', 'reliable wrapper도 다른 task의 비활성 상태를 호출자가 보장하라고 명시합니다. pin은 그 요구를 대체하지 않습니다.')
    ]
)]
