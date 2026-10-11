"""Whole x86 unwind state and shared helper header."""
ROWS = [dict(
    path='arch/x86/include/asm/unwind.h',
    title='x86 unwinder 인터페이스: 상태 변형과 반환 주소 복원',
    intro='ORC·frame pointer·기본 순회의 상태 구조, register 유효 범위, hook 주소 복원과 task stack 읽기를 해설합니다.',
    principle='구성별 상태 필드와 출력 인자의 갱신 조건을 정확히 구분하고, 진단 검사 생략을 수명 보호로 오해하지 않습니다.',
    use='x86 stack walk가 공통 함수 뒤에서 어떤 상태를 전달하는지 이해합니다.',
    area='상태 기계 · 조건부 자료구조 · 출력 인자 · 계측 trampoline · 동시 관측',
    sections=[
        ('파일 전체와 IRET 범위', 'GPL-2.0, guard와 scheduler/ftrace/rethook/ptrace/stacktrace include 뒤 상태 구조, backend 선언, 공통 helper가 있습니다. IRET_FRAME_OFFSET은 pt_regs의 ip 필드 offset이고 IRET_FRAME_SIZE는 전체 구조체 크기에서 그 offset을 뺀 값입니다. 숫자를 아키텍처와 무관한 고정 바이트 수로 외우지 않습니다. 구조체 뒤쪽의 IRET frame 범위를 나타내는 표현입니다.'),
        ('공통 상태와 선택 필드', 'unwind_state의 공통 필드는 stack_info, stack_mask, task, graph_idx, error입니다. RETHOOK이면 llist_node 포인터 kr_cur도 있습니다. 이 구조체를 선언했다고 task의 stack 수명을 자동으로 pin하거나 모든 필드를 초기화하는 것은 아닙니다. graph와 rethook 관련 상태는 뒤의 반환 주소 복원 helper에 전달됩니다.'),
        ('세 가지 상태 배치', 'ORC이면 signal/full_regs bool, unsigned long sp/bp/ip, regs/prev_regs 포인터가 들어갑니다. 그렇지 않고 FRAME_POINTER이면 got_irq, unsigned long 포인터 bp/orig_sp, unsigned long ip, next_bp와 regs가 들어갑니다. 나머지 분기는 unsigned long 포인터 sp만 추가합니다. ORC의 bp 값과 frame-pointer의 bp 포인터는 타입이 다릅니다. next_bp는 유효한 저장 BP가 없는 불완전 프레임에서 다음 프레임을 찾기 위해 대신 쓸 값이라고 주석이 설명합니다.'),
        ('Backend 선언과 종료 상태', '__unwind_start, unwind_next_frame, 반환 주소 값과 그 포인터를 얻는 두 함수는 외부 선언입니다. unwind_done은 stack_info.type이 STACK_TYPE_UNKNOWN인지, unwind_error는 error 필드를 검사합니다. 종료와 오류는 별개이므로 done 자체가 무조건 성공이나 오류라는 뜻은 아닙니다. 이 헤더에는 실제 ORC 테이블 탐색이나 frame-chain 이동 본문이 없습니다.'),
        ('시작 프레임의 기본값', 'unwind_start는 first_frame이 NULL이 아니면 유지하고, NULL이면 get_stack_pointer(task,regs)를 선택하여 __unwind_start에 전달합니다. GNU C의 생략형 조건 연산자를 사용합니다. 이 wrapper가 task를 current로 강제 교체하거나 제공된 regs를 버리는 것은 아닙니다. NULL first_frame은 순회를 금지하는 표시가 아니라 기본 시작점 선택입니다.'),
        ('Entry regs와 partial 출력', 'ORC 또는 FRAME_POINTER이면 unwind_get_entry_regs는 이미 done일 때 즉시 NULL을 반환합니다. 그 외에 partial 포인터가 있으면 ORC는 !full_regs, frame-pointer는 false를 기록하고 state->regs를 반환합니다. partial이 참이면 IRET frame register만 유효하다는 계약입니다. done 경로에서는 partial을 갱신하지 않으므로 이전 값을 신뢰하면 안 됩니다. 반환 regs가 NULL일 가능성도 별도로 다뤄야 합니다.'),
        ('기본 구성의 stub과 ORC 초기화', '두 unwinder 구성이 모두 없으면 entry_regs는 NULL만 반환하고 partial을 쓰지 않습니다. ORC일 때 unwind_init과 모듈의 ORC/IP 데이터 및 크기를 받는 unwind_module_init이 외부 선언이며, 다른 구성에서는 둘 다 빈 inline입니다. 모든 아키텍처 순회가 이 함수에서 항상 테이블 초기화를 수행한다고 설명하지 않습니다.'),
        ('반환 주소 복원 순서', 'unwind_recover_ret_addr는 먼저 ftrace_graph_ret_addr에 task, graph_idx 주소, 현재 주소와 저장 위치 포인터를 전달합니다. 그 결과를 unwind_recover_rethook에 넘깁니다. RETHOOK 활성이고 주소가 rethook trampoline이면 rethook_find_ret_addr에 task, addr_p를 정수로 바꾼 값, kr_cur 주소를 전달하고 아니면 받은 주소를 그대로 반환합니다. 그래프 추적 복원 뒤 rethook 복원이라는 순서가 명시되어 있습니다. 저장된 주소를 직접 덮어쓰는 코드는 이 wrapper에 없습니다.'),
        ('다른 task의 stack 읽기', 'READ_ONCE_TASK_STACK은 task==current이면 READ_ONCE(x), 아니면 READ_ONCE_NOCHECK(x)로 unsigned long val을 만들어 반환하는 statement expression입니다. 주석은 다른 CPU에서 task가 실행되며 stack을 poison할 수 있어 다른 task 읽기의 KASAN 검사를 피한다고 설명합니다. 검사를 생략하는 것은 stack pin, task 정지, 모든 경쟁 방지와 다릅니다. 여기에는 get/put이나 잠금이 없습니다.'),
        ('다른 CPU에서 실행 중인가', 'task_on_another_cpu는 SMP이면 task!=current && task->on_cpu를 반환하고 UP이면 항상 false입니다. on_cpu를 읽는 단순 관측이며 이 결과로 task 상태를 고정하지 않습니다. 함수 이름만으로 대상의 CPU 번호를 반환한다고 해석해서도 안 됩니다. bool 판별 뒤에도 실행 상태는 바뀔 수 있습니다.'),
        ('CS 연결과 검증 범위', '서로 다른 backend 상태를 조건부 구조체로 표현하는 방법, 오류와 종료의 독립성, 출력 인자의 미갱신 경로, 계측으로 바뀐 주소의 역변환, 진단 검사와 객체 수명의 구분을 학습합니다. 전체 헤더 대조는 ORC·frame pointer 구현 전체나 실제 CPU 간 stack 관측을 시험한 결과와 구분합니다.')
    ],
    questions=[
        ('unwind_done이 참이면 unwind_error도 반드시 참인가?', '아니다. 각각 stack 종류와 별도 error 필드를 검사한다', '그렇다. 두 helper는 같은 식이다', '정상적인 순회 종료와 손상 검출은 다른 상태입니다. 실제 helper의 조건을 분리해 읽어야 합니다.'),
        ('entry_regs가 done 경로에서 NULL을 반환하면 partial도 false로 초기화되는가?', '아니다. partial을 쓰기 전에 반환한다', '그렇다. 모든 반환 경로에서 false를 기록한다', '출력 인자는 특정 경로에서만 갱신됩니다. NULL 결과를 무시하고 기존 partial 값을 사용하는 오류를 피해야 합니다.'),
        ('반환 주소 복원 helper의 순서는?', 'ftrace graph 복원 후 rethook 복원이다', 'rethook 복원 후 ftrace graph 복원이다', '먼저 graph helper의 반환값을 ret에 담고 그 값을 rethook helper로 전달합니다.'),
        ('READ_ONCE_TASK_STACK의 NOCHECK 경로가 다른 task의 stack 수명을 보호하는가?', '아니다. KASAN 검사 생략과 수명 보호는 별개이다', '그렇다. 이름에 TASK_STACK이 있으므로 자동 pin한다', '매크로는 값을 읽어 반환할 뿐 get/put이나 잠금이 없습니다. 호출 경로의 수명 조건을 별도로 만족해야 합니다.')
    ]
)]
