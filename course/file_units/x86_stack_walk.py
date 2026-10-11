"""Complete x86 stack walking frontends."""
ROWS = [dict(
    path='arch/x86/kernel/stacktrace.c',
    title='x86 stack walk: 중단과 오류, 사용자 프레임 접근',
    intro='일반·신뢰성·사용자 stack 순회의 모든 함수와 callback 중단 조건을 해설합니다.',
    principle='부분 trace를 허용하는 순회와 완전성을 요구하는 순회는 같은 중단 조건에도 다른 결과를 반환합니다.',
    use='공통 stacktrace API가 x86 unwinder 및 사용자 frame pointer와 연결되는 과정을 이해합니다.',
    area='스택 프레임 · 반복 순회 · 사용자 메모리 접근 · 오류 전파 · 신뢰성',
    sections=[
        ('전체 구성과 경계', '저작권 주석과 scheduler, stacktrace, uaccess, x86 unwind 관련 include 뒤 arch_stack_walk, reliable walk, 사용자 프레임 구조와 복사 helper, user walk가 있습니다. unwind_state의 내부 알고리즘은 asm/unwind.h와 선택된 backend에 있으며 이 파일이 frame-pointer 또는 ORC unwinder 전체를 구현하는 것은 아닙니다.'),
        ('일반 walk의 시작', 'regs가 주어졌으면 regs->ip를 먼저 callback에 전달하고 false면 즉시 반환합니다. 이후 unwind_start에 task와 regs를 전달하여 상태를 준비합니다. regs가 NULL이면 첫 IP callback을 생략합니다. 이 함수의 반환형은 void이므로 호출자에게 오류 코드나 길이를 직접 돌려주지 않습니다. 길이는 공통 계층의 cookie로 관리됩니다.'),
        ('일반 walk의 반복', 'unwind_done이 아닐 동안 반환 주소를 얻고, 주소가 0이거나 callback이 false이면 중단합니다. 계속하는 경우 unwind_next_frame으로 진행합니다. 이 일반 경로에는 reliable 경로처럼 unwind_error를 별도 검사하여 음수 오류를 반환하는 코드가 없습니다. 중간에 멈춘 결과도 소비자가 이미 기록한 부분 배열로 남을 수 있습니다.'),
        ('Reliable의 진입 register 검사', 'reliable walk는 regs 인자 없이 task에서 시작하고 done도 error도 아닌 동안 반복합니다. unwind_get_entry_regs로 register frame이 보이면 user_mode일 때 즉시 0으로 성공 반환합니다. kernel-mode register가 있고 CONFIG_FRAME_POINTER이면 EINVAL입니다. 주석은 커널 내부 interrupt나 exception으로 frame pointer 추적이 신뢰하기 어려울 수 있다고 설명합니다. 모든 구성에서 kernel-mode register를 동일하게 거부하는 조건은 아닙니다.'),
        ('Reliable의 실패 조건', '반환 주소가 0이면 EINVAL이고 callback이 false여도 EINVAL입니다. 루프가 끝난 뒤 unwind_error이면 EINVAL, 아니면 0입니다. 소비자의 저장 공간이 모자라서 중단한 경우도 완전한 신뢰 trace로 성공 처리하지 않습니다. 이 함수의 0은 프레임 개수 0을 뜻하는 것이 아니라 성공 상태이며 저장 길이는 cookie에 따로 있습니다.'),
        ('이미 기록한 데이터의 처리', 'reliable 경로에서 뒤늦게 오류가 나더라도 이 함수가 이전 callback의 저장을 되돌리거나 배열을 지우지는 않습니다. 호출자는 오류를 확인하여 부분 자료를 신뢰 가능한 성공 결과로 취급하지 않아야 합니다. 일반 callback은 마지막 칸을 채우면 false이므로 가득 찬 버퍼를 reliable walk가 성공으로 받아들인다고 단정하면 안 됩니다.'),
        ('사용자 frame 구조', 'stack_frame_user는 사용자 공간의 다음 frame pointer와 unsigned long ret_addr를 담습니다. copy_stack_frame은 __access_ok로 frame 크기 범위를 확인하고 실패하면 0입니다. 통과하면 pagefault_disable 후 두 필드를 __get_user로 읽고, 어느 하나라도 실패하면 0으로 바꾼 뒤 pagefault_enable을 호출합니다. 성공은 1입니다. 주소 범위가 맞는 것과 실제 메모리 읽기 성공은 별도로 확인합니다.'),
        ('복사 순서와 fault 제어', '두 __get_user는 논리 OR로 연결되어 첫 실패 시 두 번째 읽기를 건너뛸 수 있습니다. pagefault_disable은 사용자 메모리 읽기를 반드시 성공시키거나 페이지를 영구 pin하는 동작이 아닙니다. 복사 helper의 실패는 user walk를 끝내는 신호로 사용되며 이 파일에서 메모리를 수정하는 쓰기는 없습니다.'),
        ('사용자 walk 시작과 반복', 'frame pointer는 regs->bp에서 얻고 regs->ip를 첫 callback으로 보냅니다. 반복마다 지역 frame을 NULL/0으로 초기화하고 copy_stack_frame을 호출합니다. 복사 실패, 현재 fp가 regs->sp보다 낮음, 반환 주소 0, callback false 중 하나면 멈춥니다. 통과하면 fp를 frame.next_fp로 바꿉니다. fp와 sp 비교보다 메모리 복사 호출이 먼저 있다는 순서를 보존해서 읽어야 합니다.'),
        ('체인 검증의 범위', 'user walk에는 next_fp가 현재 fp보다 커야 한다는 조건이나 방문한 주소 집합을 이용한 cycle 검출이 없습니다. 매번 현재 fp가 초기 regs->sp보다 낮은지 검사할 뿐입니다. 따라서 이 본문이 임의 사용자 frame 체인의 모든 잘못된 링크를 검출한다고 설명하면 틀립니다. 공통 수집 callback의 용량 제한은 지속되는 체인의 수집량을 제한하지만 모든 사용자 callback이 같은 제약을 갖는 것은 아닙니다.'),
        ('CS 연결과 검증 범위', 'callback으로 결과와 제어를 분리하는 반복자, 부분 결과와 성공 상태의 분리, 주소 검사와 실제 읽기 오류, linked frame 체인과 순환 검증의 차이를 학습합니다. 전체 소스 대조는 실제 x86 예외·사용자 fault·모든 unwind backend 조합을 실행 시험했다는 뜻이 아닙니다.')
    ],
    questions=[
        ('callback이 false이면 일반 walk와 reliable walk의 처리는?', '일반은 중단하고 reliable은 EINVAL을 반환한다', '둘 다 같은 성공 상태 0을 반환한다', '일반 walk는 void입니다. reliable은 불완전한 수집을 성공으로 처리하지 않는 별도 계약을 가집니다.'),
        ('reliable walk의 반환값 0은 저장 프레임이 0개라는 뜻인가?', '아니다. 성공이며 프레임 수는 cookie에 별도로 기록된다', '그렇다. 양수일 때만 stack을 얻었다는 뜻이다', '저수준 reliable 함수는 성공/오류 상태를 반환합니다. 공통 wrapper가 성공하면 cookie의 길이를 돌려주는 구조와 구분합니다.'),
        ('__access_ok가 통과하면 두 사용자 필드 읽기는 항상 성공하는가?', '아니다. __get_user의 오류도 확인한다', '그렇다. 범위 검사로 모든 fault 가능성이 사라진다', '범위 검사와 실제 접근 가능성은 다릅니다. helper는 pagefault를 비활성화한 읽기에서 실패를 감지하고 0을 반환합니다.'),
        ('user walk가 다음 frame pointer의 엄격한 증가나 순환 여부를 직접 검사하는가?', '아니다. 그런 검사는 본문에 없다', '그렇다. 방문 주소를 해시 테이블에 보관한다', '현재 fp와 regs->sp의 하한 비교만 있습니다. 실제 구현 이상의 검증을 있다고 가정하면 안 됩니다.'),
        ('reliable walk가 나중에 실패하면 앞서 callback이 저장한 배열은 자동으로 지워지는가?', '아니다. 호출자가 오류 상태를 확인해야 한다', '그렇다. 실패 직전에 전체 배열을 초기화한다', '되돌리기 코드가 없습니다. 일부 데이터가 존재한다는 사실만으로 신뢰 가능한 성공 결과라고 해석할 수 없습니다.')
    ]
)]
