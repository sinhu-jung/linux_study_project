"""Whole list-based return hook public kernel interface."""
ROWS = [dict(
    path='include/linux/rethook.h',
    title='Return hook 인터페이스: 연결 리스트로 보존하는 원래 반환 주소',
    intro='관리 객체와 호출별 node의 차이, handler 타입, trampoline 판별 및 아키텍처 연결 계약을 학습합니다.',
    principle='후킹을 관리하는 객체의 수명과 개별 호출의 반환 주소를 보관하는 node의 수명을 분리합니다.',
    use='unwinder가 rethook trampoline 대신 원래 반환 주소를 찾는 이유와 자료구조를 이해합니다.',
    area='연결 리스트 · shadow stack · 객체 풀 · RCU · 함수 포인터 · 아키텍처 인터페이스',
    sections=[
        ('파일 전체와 범위', 'GPL-2.0, list-based shadow stack 설명과 guard 뒤 compiler, objpool, kallsyms, llist, rcupdate를 포함합니다. handler 타입, 관리 객체와 node, 일반·아키텍처 함수 선언, trampoline 판별, task flush 분기로 구성됩니다. 여기의 shadow stack은 원래 반환 주소를 별도 리스트에 보관하는 소프트웨어 구조이며 이 헤더가 CPU의 하드웨어 shadow stack 전체를 구현하는 것은 아닙니다.'),
        ('Handler 계약', 'rethook_handler_t는 node 포인터, void 데이터 포인터, unsigned long 값, pt_regs 포인터를 받는 void 함수 포인터입니다. 구조체의 handler 멤버는 이 typedef 대신 __rcu가 붙은 원시 함수 포인터 선언을 사용합니다. 주석은 sparse 경고를 피하기 위한 표현이며 시그니처는 typedef와 같아야 한다고 명시합니다. __rcu 표기 자체가 호출 시 필요한 모든 수명 처리를 자동 실행하는 코드는 아닙니다.'),
        ('관리 객체와 오래된 주석', 'struct rethook의 실제 멤버는 사용자 data, handler, objpool_head pool, rcu_head rcu입니다. kernel-doc에는 ref라는 참조 카운터 항목이 남아 있지만 실제 구조체에는 ref 멤버가 없습니다. 주석 항목만 보고 존재하지 않는 필드를 학습 모델에 추가하지 않습니다. pool은 node를 관리하는 저장소이며 단일 호출의 반환 주소는 이 구조체에 직접 들어 있지 않습니다.'),
        ('Embedding 규칙', '관리 객체의 주석은 모든 node가 해제되면 자체 해제되는 구조이므로 다른 구조체에 embedding하지 말라고 합니다. 반면 rethook_node는 호출별 데이터를 추가할 수 있도록 확장 구조체에 embedding 가능하다고 명시합니다. 두 구조체의 이름이 비슷해도 수명과 할당 계약이 다릅니다. embedding은 포인터를 보관하는 것과도 구분해야 합니다.'),
        ('호출별 node의 필드', 'node에는 지연 해제용 rcu_head, task_struct의 rethooks에 연결되는 llist_node, 관리 객체 포인터, 실제 반환 주소 ret_addr, frame 저장값이 있습니다. ret_addr와 frame은 모두 unsigned long이지만 의미가 다릅니다. llist는 별도 linked list 연결용이며 여기에는 직접 push/pop하는 본문이나 순회 중 동기화 코드가 없습니다.'),
        ('일반 관리 API', 'alloc은 data, handler, int size와 int num을 받아 rethook 포인터를 반환합니다. stop/free는 관리 객체, try_get은 관리 객체를 받아 node 포인터, recycle은 node를 받습니다. hook은 node, regs, bool mcount를 전달받습니다. 선언만으로 각 실패 코드, 대기 여부, mcount의 아키텍처별 처리 세부를 확정할 수는 없습니다. 실제 구현에서 확인해야 합니다.'),
        ('원래 반환 주소 탐색', 'rethook_find_ret_addr는 task, unsigned long frame, llist_node 이중 포인터 cur를 받아 unsigned long을 반환합니다. 앞서 x86 unwinder는 task와 반환 주소 슬롯 위치, 보관 중인 리스트 cursor 주소를 넘깁니다. cur가 이중 포인터인 것은 탐색 상태를 호출자 쪽에 전달할 수 있는 인터페이스라는 점을 보여 줍니다. 이 헤더에는 모든 검색 경로와 일치 실패 처리 본문이 없습니다.'),
        ('Trampoline과 심볼 주소', '아키텍처는 arch_rethook_prepare와 arch_rethook_trampoline을 구현해야 합니다. is_rethook_trampoline은 입력 주소가 dereference_symbol_descriptor로 얻은 trampoline의 코드 주소와 정확히 같은지 검사합니다. 임의 함수 범위 포함이나 심볼 이름 문자열 비교가 아닙니다. 심볼 descriptor를 거치는 표현을 단순 함수 포인터 숫자 비교로 무조건 치환하지 않습니다.'),
        ('복귀 보정과 공통 handler', 'arch_rethook_fixup_return은 regs와 correct_ret_addr를 받으며 주석은 아키텍처가 필요할 때 반환 주소를 보정하는 구현을 제공하라고 설명합니다. generic rethook_trampoline_handler는 regs와 frame을 받아 unsigned long을 반환하고 아키텍처가 assembly stub을 준비해야 합니다. 이 헤더만으로 모든 stub의 저장 register나 calling convention을 알 수는 없습니다.'),
        ('Task flush의 구성 조건', 'CONFIG_RETHOOK이면 rethook_flush_task의 외부 선언이 있고 아니면 인자를 사용하지 않는 빈 do/while 매크로입니다. 이 분기만 보고 다른 모든 API도 기능 없는 stub으로 제공된다고 일반화하면 안 됩니다. 비활성 매크로는 tsk 인자를 본문에서 사용하지 않아 인자 표현식이 평가되지 않는다는 점에서 빈 inline 함수와 다릅니다.'),
        ('CS 연결과 검증 범위', '관리 객체와 호출별 객체의 분리, embedding과 자체 해제 계약, callback 타입 일치, RCU annotation, 주소 복원용 보조 자료구조를 학습합니다. 전체 헤더 대조는 실제 stop/free 경쟁이나 trampoline 실행을 시험한 결과와 구분하며 kernel/trace/rethook.c 전체를 완료한 것으로 계산하지 않습니다.')
    ],
    questions=[
        ('struct rethook에 ref 멤버가 실제로 존재하는가?', '아니다. 주석 항목은 있지만 실제 정의에는 없다', '그렇다. kernel-doc의 모든 항목은 자동으로 멤버를 만든다', 'C 구조체 정의가 실제 레이아웃의 근거입니다. 주석과 코드 사이의 차이를 확인해야 합니다.'),
        ('관리 객체와 node를 모두 다른 구조체에 embedding해도 같은 계약인가?', '아니다. 관리 객체는 금지, node는 확장 embedding을 허용한다고 주석이 명시한다', '그렇다. 둘 다 같은 방식으로 자체 해제된다', '관리 객체와 호출별 node의 수명·할당 역할이 다릅니다. 포인터로 참조하는 것과 객체를 직접 포함하는 것도 구분합니다.'),
        ('is_rethook_trampoline은 코드 구간 전체를 검사하는가?', '아니다. descriptor를 해석한 trampoline 주소와 정확히 비교한다', '그렇다. 같은 함수 안의 모든 주소이면 참이다', '본문은 addr==변환된 심볼 주소입니다. 범위의 시작과 끝을 비교하는 코드가 없습니다.'),
        ('RETHOOK 기능이 꺼졌을 때 flush 매크로에 전달한 부수효과 표현식은 실행되는가?', '아니다. 매크로 본문에서 인자를 사용하지 않는다', '그렇다. C 함수 인자처럼 항상 먼저 평가한다', '해당 분기는 함수가 아닌 빈 do/while 매크로입니다. 인자 평가를 포함한 언어적 차이를 확인해야 합니다.')
    ]
)]
