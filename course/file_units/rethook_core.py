"""Complete generic return-hook pool, RCU lifecycle and shadow list."""
ROWS = [dict(
    path='kernel/trace/rethook.c',
    title='Rethook 공통 구현: 중첩 후킹 리스트와 지연 해제',
    intro='할당부터 정지·재활용·원래 주소 검색·handler 실행·task 종료 정리까지 전체 구현을 추적합니다.',
    principle='handler 실행 중에는 주소 복원을 위한 리스트를 유지하고, 정지 표시와 실제 저장소 해제는 분리합니다.',
    use='각 아키텍처 trampoline이 호출하는 공통 수명 관리와 반환 주소 검색을 이해합니다.',
    area='객체 풀 · RCU · 연결 리스트 · 중첩 호출 · 오류 포인터 · 수명 관리',
    sections=[
        ('전체 구성', 'GPL-2.0, rethook 로그 접두어와 include 뒤 task 정리, RCU 해제, 관리 객체 할당, node 재활용·획득, hook 추가, 주소 검색, weak fixup과 trampoline handler가 있습니다. 실제 register 치환은 arch 함수에 맡기고 공통 코드는 task별 rethooks 리스트와 objpool을 관리합니다.'),
        ('종료 task의 남은 node', 'rethook_flush_task는 __llist_del_all로 task의 리스트를 떼고 각 node를 container_of로 복구합니다. 다음 포인터를 먼저 저장한 뒤 재활용마다 preempt_disable/enable로 감쌉니다. 주석은 죽은 task가 호출했지만 다시는 반환하지 않을 함수의 남은 instance를 정리한다고 설명합니다. 이 경로는 사용자 handler를 실행하지 않습니다.'),
        ('Stop과 free의 차이', 'stop은 rcu_assign_pointer로 handler를 NULL로 만듭니다. 진행 중 handler 종료까지 기다리는 동작은 아니므로 필요하면 stop 뒤 RCU 대기를 하고 free하라는 계약입니다. free는 stop 후 call_rcu를 예약하며 callback이 objpool_fini를 호출합니다. 호출자는 free 후 rh를 만지면 안 되고 data의 별도 수명도 고려해야 합니다. free 호출 즉시 모든 대여 node가 사라지는 것은 아닙니다.'),
        ('Pool callback과 객체 해제', 'node 초기화 callback은 node->rethook=context를 설정하고 0을 반환합니다. pool 최종 callback은 context인 관리 객체를 kfree하고 0을 반환합니다. 관리 객체가 다른 구조체에 embedding되면 안 된다는 헤더 계약이 이 해제 경로와 연결됩니다. rethook_get_handler는 RCU 읽기 조건을 확인하는 rcu_dereference_check로 함수 포인터를 얻습니다.'),
        ('Alloc 실패와 반환형', 'handler가 NULL, num<=0, size가 node 구조보다 작으면 ERR_PTR(-EINVAL)입니다. 관리 객체 kzalloc 실패는 ERR_PTR(-ENOMEM)입니다. 성공하면 data와 handler를 저장하고 GFP_KERNEL로 objpool_init을 호출합니다. pool 초기화가 실패하면 rh를 해제하고 반환 원인과 관계없이 ENOMEM 오류 포인터로 돌립니다. 이 함수의 실패를 단순 NULL 검사만으로 처리하면 안 됩니다.'),
        ('재활용의 두 경로', 'recycle은 handler가 아직 있으면 objpool_push로 node를 돌려줍니다. handler가 NULL이면 node의 rcu_head로 callback을 예약하고 그 callback에서 objpool_drop을 수행합니다. stop 상태와 data 포인터 NULL 여부를 혼동하지 않습니다. 지연 해제 callback은 node->rethook으로 pool에 접근하므로 전체 수명 설계가 연결되어 있습니다.'),
        ('Try get의 호출 문맥', 'try_get 주석은 호출자가 preemption을 꺼야 한다고 명시합니다. 함수 자체가 그 책임을 대신 수행하지 않습니다. handler가 NULL이면 NULL이며, FTRACE_VALIDATE_RCU_IS_WATCHING 또는 KPROBE_EVENTS_ON_NOTRACE 구성에서는 rcu_is_watching이 아니어도 NULL입니다. 그 외 objpool_pop 결과를 반환하므로 pool 소진도 NULL이 될 수 있습니다. 호출 때마다 새 node를 GFP_KERNEL로 할당하는 경로가 아닙니다.'),
        ('함수 진입 hook', 'hook은 arch_rethook_prepare로 원래 반환 주소를 보존·교체한 뒤 __llist_add로 current의 리스트에 node를 넣습니다. 주석은 실제 함수 진입 시점의 regs가 필요하며 ftrace mcount 문맥이면 mcount=true, 실제 진입 kprobe 문맥이면 false를 전달하라고 합니다. 일부 아키텍처가 이 인자를 사용하지 않더라도 공통 API의 문맥 계약은 남아 있습니다.'),
        ('내부 원래 주소 검색', '__rethook_find_ret_addr는 *cur가 NULL이면 리스트 처음, 아니면 그 다음 node에서 시작합니다. ret_addr가 trampoline인 node들을 건너뛰고 첫 실제 주소를 찾으면 *cur를 그 node로 갱신해 반환합니다. 없으면 0이며 실패 경로에서 cursor를 NULL로 초기화하지 않습니다. 같은 함수에 여러 hook이 쌓이면 앞선 hook이 보관한 주소가 trampoline일 수 있다는 구조와 연결됩니다.'),
        ('외부 검색의 frame 조건', 'rethook_find_ret_addr는 cur 자체가 NULL이면 WARN_ON_ONCE 후 0이고, 다른 task가 task_is_running이면 0입니다. 내부 검색을 반복해 실제 주소를 가진 node의 frame이 요청 frame과 같을 때 반환합니다. 첫 호출의 *cur는 NULL이어야 합니다. task 상태 검사만으로 대상의 실행 상태를 잠금으로 고정하는 것은 아니며 호출자는 current 또는 실행하지 않는 task라는 전제를 지켜야 합니다.'),
        ('기본 fixup', 'weak arch_rethook_fixup_return은 빈 본문입니다. 주석은 handler 안의 stacktrace를 위해 stack에 있는 실제 반환 주소를 보정해야 하는 아키텍처가 구현할 수 있다고 설명합니다. 공통 handler는 이 hook을 호출하지만 모든 아키텍처가 반드시 같은 위치에 저장한다는 뜻은 아닙니다.'),
        ('Trampoline의 주소 결정', 'trampoline handler는 내부 검색으로 current 리스트에서 첫 실제 복귀 주소와 해당 node를 찾습니다. 없으면 오류 로그 후 BUG_ON입니다. 주소가 있으면 instruction_pointer_set으로 regs의 IP를 먼저 설정하고 preempt_disable_notrace로 이후 rh 접근과 리스트 처리를 보호합니다. 실제 반환값과 regs snapshot 변경이 모두 존재합니다.'),
        ('사용자 handler 실행 중 리스트 유지', '리스트 처음부터 실제 주소를 가진 node까지 각 handler를 실행합니다. frame이 다르면 WARN_ON_ONCE 후 handler 실행 루프를 멈춥니다. handler가 NULL이면 호출을 생략합니다. 인자는 node, rh->data, correct_ret_addr, regs입니다. 이때 리스트를 미리 unlink하지 않는 이유는 handler 안의 stackdump가 원래 주소를 복원할 수 있어야 하기 때문입니다.'),
        ('Fixup·분리·재활용 순서', 'handler 루프 뒤 arch fixup을 수행하고 current 리스트 head를 검색된 node의 다음으로 옮긴 뒤 node->next를 NULL로 잘라 사용 구간을 분리합니다. 처음부터 그 구간 전체를 recycle하고 preempt_enable_notrace 후 실제 주소를 반환합니다. frame 경고로 앞 루프가 멈춰도 뒤의 fixup과 분리·재활용은 계속됩니다. 경고가 함수 전체의 즉시 반환이라고 설명하면 틀립니다.'),
        ('CS 연결과 검증 범위', '연결 리스트를 shadow stack처럼 사용하는 방법, null handler를 통한 정지 상태, 오류 포인터와 NULL의 차이, RCU 유예와 objpool의 결합, 관측을 위해 제거를 늦추는 순서를 학습합니다. 여러 helper는 NOKPROBE_SYMBOL로 재계측을 막습니다. 전체 원본 대조는 실제 handler/free 경쟁이나 모든 아키텍처의 중첩 후킹 실행 시험을 대신하지 않습니다.')
    ],
    questions=[
        ('rethook_alloc 실패를 NULL 검사만으로 충분히 판별하는가?', '아니다. ERR_PTR로 오류를 반환한다', '그렇다. 모든 할당 API는 실패하면 NULL이다', '인자 오류는 EINVAL, 메모리·pool 실패는 ENOMEM을 오류 포인터에 담습니다. try_get의 NULL 반환과 구분해야 합니다.'),
        ('rethook_stop이 이미 실행 중인 handler 종료를 기다리는가?', '아니다. handler를 NULL로 게시하며 대기는 별도 계약이다', '그렇다. stop 반환 뒤 모든 callback이 반드시 종료되어 있다', '주석은 기다려야 한다면 stop 뒤 RCU 대기 후 free하라고 명시합니다. 정지 표시와 실행 완료 대기는 다릅니다.'),
        ('handler 실행 전에 리스트를 unlink하지 않는 이유는?', 'handler 안의 stackdump가 원래 반환 주소를 찾을 수 있어야 해서다', '연결 리스트는 실행 중에는 읽을 수 없는 자료구조라서다', '원본 주석의 목적입니다. 먼저 callback들을 수행하고 fixup 뒤 사용 구간을 분리합니다.'),
        ('주소 검색 cursor는 성공 때 어떻게 갱신되는가?', '실제 반환 주소를 가진 node를 가리키게 된다', '항상 해당 node의 다음으로 미리 이동한다', '다음 검색은 저장된 node의 next에서 시작합니다. 성공 시 저장 위치와 다음 호출의 출발점을 구분합니다.'),
        ('try_get은 내부에서 preemption을 끄는가?', '아니다. 호출자가 꺼야 한다', '그렇다. 함수 이름의 try가 자동 보호를 뜻한다', '주석이 caller must disable preemption이라고 명시하며 본문에 disable 호출은 없습니다.'),
        ('frame 불일치 경고가 나면 trampoline handler 전체가 즉시 반환하는가?', '아니다. handler 루프만 중단하고 뒤 정리 경로는 계속한다', '그렇다. 남은 node를 그대로 두고 0을 반환한다', '조건 안의 break는 while 루프를 끝냅니다. 이후 fixup, 사용 리스트 분리, recycle과 실제 주소 반환이 이어집니다.')
    ]
)]
