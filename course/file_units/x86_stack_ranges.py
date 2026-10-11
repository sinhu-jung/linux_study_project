"""Complete x86 stack categories, range checks and frame pointer interface."""
ROWS = [dict(
    path='arch/x86/include/asm/stacktrace.h',
    title='x86 스택 범위: 종류·guard 후보·프레임 시작점',
    intro='스택 종류와 경계 구조체, guard 판별, 객체 범위 검사와 register 기반 시작점 선택을 해설합니다.',
    principle='주소 하나의 소속, 길이를 포함한 범위 검사, guard 후보 판별은 서로 다른 조건이며 출력 구조체의 변경도 추적해야 합니다.',
    use='x86 unwinder가 task·IRQ·exception stack을 구분하는 인터페이스를 이해합니다.',
    area='구간 산술 · 조건부 타입 · 호출 프레임 · guard page · 출력 인자',
    sections=[
        ('전체 구성과 종류', 'GPL-2.0, 저작권, guard, uaccess/ptrace와 x86 진입·context switch 관련 include 뒤 stack_type, stack_info, 탐색 선언과 helper, frame 구조 및 출력 선언이 있습니다. enum은 UNKNOWN=0, TASK=1, IRQ=2, SOFTIRQ=3, ENTRY=4, EXCEPTION=5로 이어지고 EXCEPTION_LAST는 첫 exception 값에 N_EXCEPTION_STACKS-1을 더합니다. exception 종류 수를 고정된 하나로 해석하면 안 됩니다.'),
        ('경계 구조와 탐색 선언', 'stack_info는 type과 unsigned long 포인터 begin, end, next_sp를 갖습니다. in_task_stack, in_entry_stack은 bool이며 get_stack_info는 task와 visit_mask 포인터를 포함해 int를 반환하고 noinstr 버전은 visit_mask 없이 bool입니다. stack_type_name은 const char 포인터를 반환합니다. 이 헤더에는 탐색 구현이나 visit_mask 갱신 알고리즘이 없으므로 선언만으로 임의의 방문 규칙을 단정하지 않습니다.'),
        ('Guard 후보 확인의 두 단계', 'get_stack_guard_info는 먼저 현재 주소를 current의 알려진 stack에서 찾고 성공하면 false를 반환합니다. 실제 stack 내부는 guard가 아니기 때문입니다. 찾지 못하면 주소에 PAGE_SIZE를 더해 다시 탐색한 결과를 반환합니다. 즉 인식되는 stack의 한 페이지 아래에 있는 주소라는 관계를 검사하며 페이지 테이블의 접근 권한을 직접 조사하지 않습니다. info는 내부 탐색에 전달되는 출력이라 false를 반환했다고 전혀 변경되지 않았다고 가정하면 안 됩니다.'),
        ('전체 범위 검사 on_stack', 'on_stack은 종류가 UNKNOWN이 아니고 addr가 begin 이상 end 미만이며 addr+len이 begin보다 크고 end 이하여야 참입니다. 양의 길이의 정상적인 범위는 마지막 바이트가 end 직전까지 들어갈 수 있습니다. addr==end이면 len이 0이어도 거짓입니다. 길이가 0일 때 addr==begin도 거짓이지만 내부 주소 begin<addr<end라면 조건을 통과합니다. 단순한 반열린 구간 포함이라는 설명만으로 이 특수 경계를 지우면 안 됩니다.'),
        ('산술과 입력 전제', 'on_stack은 주소와 길이를 더하는 표현을 사용하며 별도의 체크된 덧셈 API나 errno 반환이 없습니다. 이 검사가 임의의 손상된 info와 모든 정수·포인터 조합에 대한 메모리 안전성을 보장한다고 설명하지 않습니다. 앞서 task_stack.h의 object_is_on_stack과 달리 여기서는 길이를 받지만 stack 수명을 pin하거나 내용을 읽어 검증하지는 않습니다.'),
        ('표시 단위와 frame pointer', 'STACKSLOTS_PER_LINE은 X86_32이면 8, 아니면 4입니다. 페이지 크기나 stack 할당 크기가 아니라 한 줄의 표시 슬롯 상수입니다. FRAME_POINTER이면 get_frame_pointer는 regs가 있으면 regs->bp, 대상이 current이면 __builtin_frame_address(0), 다른 task이면 task->thread.sp의 inactive_task_frame에 있는 bp 필드 주소를 반환합니다. 마지막 경로는 저장된 bp 값을 읽는 것과 다릅니다. FRAME_POINTER가 없으면 모든 입력에 NULL입니다.'),
        ('Stack pointer 선택', 'get_stack_pointer는 regs가 있으면 regs->sp를 먼저 사용합니다. 그렇지 않고 current면 __builtin_frame_address(0), 다른 task이면 task->thread.sp를 포인터로 반환합니다. current 경로도 소스상 frame 주소 builtin이므로 언제나 CPU의 현재 SP 레지스터를 직접 읽는 함수라고 설명하지 않습니다. 이 함수는 FRAME_POINTER 구성과 무관하게 정의됩니다.'),
        ('두 frame 구조와 출력 선언', 'stack_frame은 다음 frame 포인터와 unsigned long 반환 주소를 가집니다. stack_frame_ia32는 두 필드를 u32로 표현합니다. native 포인터 폭과 별개로 32비트 형태를 나타내는 구조입니다. 이 정의 자체가 체인을 순회하거나 순환을 검사하지는 않습니다. show_opcodes와 show_ip는 pt_regs와 const char log level을 받아 void를 반환하는 외부 선언이며 출력 본문은 여기에 없습니다.'),
        ('CS 연결과 검증 범위', '여러 stack을 같은 경계 구조로 추상화하는 방법, 산술 판별과 실제 메모리 속성의 차이, 0 길이 구간의 경계 사례, 저장 값과 그 필드 주소의 차이를 학습합니다. 헤더 전체 대조는 guard fault나 모든 context switch 상태를 실제 CPU에서 시험했다는 뜻이 아닙니다.')
    ],
    questions=[
        ('get_stack_guard_info의 첫 stack 탐색이 성공하면 결과는?', 'false이다. 주소가 stack 내부이기 때문이다', 'true이다. stack을 찾았으므로 guard이다', 'guard 후보 판별은 현재 주소가 실제 stack에 속하지 않고 PAGE_SIZE 위가 stack에 속하는 관계를 확인합니다.'),
        ('알려진 stack의 begin 주소와 길이 0을 on_stack에 넣으면?', 'false이다', '길이 0이므로 항상 true이다', 'addr+len>begin 조건이 성립하지 않습니다. 반면 엄격히 내부인 주소에서 길이 0은 통과할 수 있습니다.'),
        ('다른 task의 get_frame_pointer가 반환하는 inactive frame 관련 값은?', 'bp 필드의 주소이다', 'bp 필드 안에 저장된 값을 역참조한 결과이다', '식은 &((struct inactive_task_frame *)task->thread.sp)->bp입니다. 주소 연산자의 존재를 확인해야 합니다.'),
        ('current의 get_stack_pointer는 항상 SP 레지스터를 직접 읽는가?', '아니다. regs가 없으면 __builtin_frame_address(0)을 사용한다', '그렇다. 모든 경로에서 같은 SP 읽기 명령을 실행한다', 'regs가 있으면 regs->sp가 우선이고 current 기본 경로는 frame 주소 builtin입니다. 소스의 실제 분기를 구분합니다.')
    ]
)]
