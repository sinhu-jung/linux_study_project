"""Complete x86 heuristic stack scanner backend."""
ROWS = [dict(
    path='arch/x86/kernel/unwind_guess.c',
    title='x86 guess unwinder: 커널 코드 주소 후보의 선형 검색',
    intro='프레임 정보 대신 스택 슬롯의 값을 검사하는 네 함수의 동작과 후보 판별의 한계를 학습합니다.',
    principle='값이 커널 코드 주소라는 사실은 그 슬롯이 실제 호출의 반환 주소라는 증명과 다릅니다.',
    use='정밀 unwind 정보가 없는 검색 방식의 trace를 해석할 때 허위 후보와 생략 가능성을 이해합니다.',
    area='휴리스틱 검색 · 선형 탐색 · 정렬 · 상태 초기화 · 다중 스택 순회',
    sections=[
        ('파일 전체와 역할', 'GPL-2.0-only와 scheduler/ftrace/ptrace/bitops/stacktrace/unwind include 뒤 반환 주소 조회, 주소 포인터 조회, 다음 후보 검색, 시작 함수가 있습니다. 이름의 guess처럼 frame chain이나 ORC 메타데이터를 읽는 대신 stack 슬롯에서 __kernel_text_address에 해당하는 값을 찾습니다. 실제 호출 관계를 검증하는 디스어셈블이나 return instruction 검사는 없습니다.'),
        ('현재 후보 값 조회', 'unwind_get_return_address는 done이면 0, 아니면 *state->sp를 READ_ONCE_NOCHECK로 읽고 unwind_recover_ret_addr에 주소와 슬롯 포인터를 전달합니다. 이전 헤더의 ftrace graph·rethook 복원을 이용합니다. 이 함수 본문은 읽은 값을 다시 __kernel_text_address로 검사하지 않습니다. 후보 검색 당시 값과 나중 조회 값의 일관성을 이 함수만으로 보장하지 않습니다. GPL 심볼로 export됩니다.'),
        ('포인터 조회의 의도적 빈 결과', 'unwind_get_return_address_ptr은 인자와 무관하게 NULL을 반환합니다. 내부 state->sp가 존재한다고 이를 신뢰 가능한 반환 주소 저장 위치 API로 공개하는 것은 아닙니다. 값 조회 함수가 반환 주소 후보를 내놓는다는 사실과 수정 가능한 정확한 저장 위치를 제공한다는 계약을 구분합니다.'),
        ('다음 후보 검색', 'unwind_next_frame은 done이면 false입니다. 그 외 for문의 초기 state->sp++로 현재 슬롯을 건너뛴 뒤 info->end 미만의 슬롯을 unsigned long 단위로 검사합니다. 각 값을 READ_ONCE_NOCHECK로 읽어 __kernel_text_address이면 즉시 true입니다. 그 주소가 저장된 call frame의 크기나 이전 BP와의 관계는 검사하지 않습니다. 스택에 보관된 함수 포인터 같은 값이 후보로 보일 가능성을 이해해야 합니다.'),
        ('스택 간 전환', '현재 영역 끝까지 후보가 없으면 info->next_sp를 sizeof(long)에 맞춰 올림 정렬하여 state->sp에 대입합니다. get_stack_info가 0을 반환하는 동안 do/while을 계속하며 stack_mask 주소를 함께 넘깁니다. 다음 반복의 for도 sp++로 시작하므로 전환된 시작 슬롯을 그대로 첫 검사 대상으로 삼는다고 설명하면 틀립니다. stack_mask의 구체적인 방문 방지 구현은 get_stack_info 쪽에 있고 이 파일에는 없습니다.'),
        ('시작 상태 초기화', '__unwind_start는 memset으로 전체 state를 0으로 만든 뒤 task를 저장하고 first_frame을 long 정렬한 주소를 sp로 둡니다. get_stack_info에는 정렬 전 first_frame을 전달합니다. 이 backend는 regs 인자를 본문에서 직접 사용하지 않으며 상위 unwind_start가 기본 first_frame을 선택할 수 있습니다. 이 함수 자체에는 stack 참조 획득이나 task 정지가 없습니다.'),
        ('시작 후보 검사와 정렬 전제', 'done이 아니고 first_frame이 sizeof(long) 범위로 on_stack 조건을 만족하지 않거나 *first_frame이 kernel text 주소가 아니면 next_frame을 호출합니다. OR의 단락 평가 때문에 범위 실패 시 역참조를 하지 않습니다. 다만 이 판별은 원래 first_frame을 사용하고 실제 조회 상태는 정렬된 sp를 사용하므로 둘을 무조건 같은 주소라고 설명하지 않습니다. 호출자가 유효한 시작점과 수명 조건을 마련해야 합니다.'),
        ('종료와 오류 상태', '다음 stack 탐색을 계속할 수 없으면 next_frame은 false입니다. 시작 함수는 next_frame의 bool을 따로 반환하지 않으며 자신의 반환형도 void입니다. 이 파일에는 state->error를 true로 설정하는 대입이 없습니다. 시작 시 0이었던 error만 보고 얻은 trace가 정확한 호출 chain이라고 증명할 수는 없습니다. 실제 범위 종료 판정은 공통 상태와 stack 탐색 helper를 통해 이뤄집니다.'),
        ('CS 연결과 검증 범위', '주소 분류를 이용한 휴리스틱, 첫 일치 선형 탐색, 포인터 정렬과 원래 입력의 차이, 상태 초기화, 값의 후보성과 구조적 증명의 차이를 학습합니다. 단일 영역에서 검색 비용은 검사한 슬롯 수에 비례합니다. 원본 전체 대조는 실제 커널에서 허위 후보 비율이나 동시 실행 안정성을 측정한 시험이 아닙니다.')
    ],
    questions=[
        ('__kernel_text_address가 참인 슬롯은 반드시 실제 return address인가?', '아니다. 코드 주소를 담은 다른 데이터도 후보가 될 수 있다', '그렇다. 이 함수가 전체 호출 관계를 증명한다', '검색은 값이 코드 주소 범위인지 판단합니다. 프레임 구조나 call/return 관계를 검증하는 조건은 이 코드에 없습니다.'),
        ('unwind_get_return_address_ptr은 state->sp를 반환하는가?', '아니다. 항상 NULL을 반환한다', '그렇다. 값 조회가 가능하면 포인터도 반드시 제공한다', '값 후보와 신뢰 가능한 저장 위치는 다른 계약입니다. 해당 함수의 본문은 return NULL뿐입니다.'),
        ('next_frame은 현재 state->sp 슬롯을 다시 검사하는가?', '아니다. 먼저 sp를 한 슬롯 증가시킨다', '그렇다. 현재 슬롯부터 반드시 재검사한다', 'for 초기식이 state->sp++입니다. 스택 전환 후 반복에서도 같은 초기식이 실행됩니다.'),
        ('__unwind_start가 regs->sp를 직접 읽는가?', '아니다. 이 본문은 first_frame으로 시작하며 regs를 직접 사용하지 않는다', '그렇다. first_frame 값과 관계없이 regs->sp를 우선한다', '기본 시작점 선택은 상위 wrapper에서 이뤄질 수 있습니다. backend와 wrapper의 책임을 나누어 읽어야 합니다.')
    ]
)]
