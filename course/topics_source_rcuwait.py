"""Whole rcuwait header and source wake/finish contracts; timeout and signal cases."""
ROWS = [('Rcuwait 표현·하나의 RCU task 포인터와 active 조회',
  'include/linux/rcuwait.h',
  'rcuwait',
  'rcuwait 구조체에는 RCU로 보호하는 task 포인터가 하나 있습니다. 초기값은 NULL입니다. 기다리는 task는 조건을 검사하거나 잠들어 있는 동안 이 포인터에 자신을 등록하고, '
  '대기가 끝나면 NULL로 되돌립니다. active 조회는 그 순간 포인터가 NULL인지 확인할 뿐입니다. 잠금 소유권이나 task가 실제로 잠들었는지는 보장하지 않습니다. 여러 task를 '
  '리스트에 등록하는 일반 waitqueue와 구별하세요.',
  '하나의 조건을 기다리는 단일 waiter에 사용합니다. 같은 구조체의 task 포인터 쓰기는 호출자 규약으로 직렬화하세요. active 값만으로 task 수명이나 잠금 소유권을 판단하지 '
  '말고, 여러 task를 동시에 같은 포인터에 등록하지 마세요.',
  [('rcuwait에 직접 저장되는 waiter 표현은 무엇인가요?',
    'task 포인터 하나입니다.',
    '여러 task를 담은 배열입니다.',
    '구조체의 멤버는 단일 RCU task 포인터입니다. 여러 대기자를 리스트로 관리하는 일반 waitqueue와 다릅니다.'),
   ('active가 true이면 task가 반드시 지금 잠들어 있나요?',
    '아닙니다. 조건을 검사 중일 수도 있습니다.',
    '맞습니다. 항상 schedule 중이라는 증거입니다.',
    '원문은 잠든 동안뿐 아니라 필요한 조건을 검사하는 동안에도 포인터가 등록되어 있다고 설명합니다. active는 순간 관측입니다.')],
  [('원문과 사용 조건', '헤더 전체의 guard, 초기화, 정적 초기화, 선언과 active의 직렬화 관련 주석을 읽었습니다.'),
   ('실행 검증의 범위',
    '완전한 rcuwait 헤더와 원문의 wake·finish 함수, timeout 조건 매크로를 직렬 task·signal·schedule·RCU·배리어 모델에서 검사했습니다. 실제 '
    '스케줄러 실행이나 동시성·메모리 순서의 증명은 포함하지 않습니다.')]),
 ('Rcuwait prepare·current 공개와 외부 직렬화 책임',
  'include/linux/rcuwait.h',
  'prepare_to_rcuwait',
  'prepare_to_rcuwait는 rcu_assign_pointer(w->task, current)로 현재 실행 중인 task를 등록합니다. 대기 매크로는 반복문에 들어가기 전에 이 '
  '함수를 호출합니다. 같은 포인터에 여러 task가 동시에 자신을 등록하면 단일 waiter라는 전제가 깨집니다. 헤더는 prepare와 finish를 포함한 포인터 쓰기의 직렬화를 호출자 '
  '책임으로 명시합니다. RCU 포인터 공개와 상호 배제는 서로 다른 역할입니다.',
  '같은 w를 사용하는 대기의 등록과 완료를 외부 규약으로 보호하세요. current는 현재 실행 중인 task라는 점을 먼저 확인합니다. 조건 값의 공개, task 포인터의 공개, task '
  '수명 보호를 각각 구분하여 추적하세요.',
  [('prepare가 등록하는 task는 무엇인가요?',
    '현재 task인 current입니다.',
    '항상 부모 task입니다.',
    '원문은 현재 실행 중인 task를 포인터에 저장합니다. 임의의 다른 task를 선택하는 API가 아닙니다.'),
   ('rcu_assign_pointer가 있으면 여러 waiter 등록이 자동으로 직렬화되나요?',
    '아닙니다. 호출자의 잠금 규약이 필요합니다.',
    '맞습니다. 다중 waiter 대기열이 됩니다.',
    '헤더는 task 포인터 쓰기의 직렬화를 호출자 책임으로 명시합니다. RCU 수명 보호와 상호 배제는 역할이 다릅니다.')],
  [('원문과 사용 조건', '모델은 정상적인 단일 waiter 상태의 포인터 공개를 검사했습니다. 경쟁 등록의 안전성을 증명하는 검사는 아닙니다.'),
   ('실행 검증의 범위',
    '완전한 rcuwait 헤더와 원문의 wake·finish 함수, timeout 조건 매크로를 직렬 task·signal·schedule·RCU·배리어 모델에서 검사했습니다. 실제 '
    '스케줄러 실행이나 동시성·메모리 순서의 증명은 포함하지 않습니다.')]),
 ('Rcuwait wait loop·조건 먼저 signal 다음 schedule',
  'include/linux/rcuwait.h',
  '___rcuwait_wait_event',
  '공통 대기 매크로는 반환값을 초기화하고 task를 등록합니다. 매 반복에서 set_current_state를 실행한 다음 조건을 먼저 검사합니다. 조건이 true이면 성공 경로로 끝납니다. '
  '조건이 false일 때만 signal_pending_state를 검사하여 해당 대기 상태에서 허용하는 signal이면 -EINTR로 끝냅니다. 그 외에는 schedule 같은 대기 명령을 '
  '실행하고 다시 검사합니다. 반복문을 떠나는 모든 경로는 finish를 거칩니다.',
  '조건식은 반복해서 평가해도 문제가 없도록 작성하세요. 대기 state에 따라 어떤 signal이 중단을 허용하는지 확인합니다. 한 번 깨웠다는 사실을 조건 성공으로 취급하지 말고 반복문에서 '
  '실제 조건을 다시 검사하세요.',
  [('조건이 true이고 중단 가능한 signal도 대기 중이면 무엇을 먼저 판정하나요?',
    '조건 성공을 먼저 판정합니다.',
    '항상 -EINTR을 먼저 반환합니다.',
    '본문은 조건 분기를 signal 검사보다 앞에 둡니다. 두 사건을 함께 관측했을 때의 판정 순서를 직접 읽어야 합니다.'),
   ('조건식은 매크로에서 항상 한 번만 평가되나요?',
    '아닙니다. 반복해서 검사합니다.',
    '맞습니다. 처음 값으로 고정합니다.',
    '깨어나거나 schedule에서 돌아온 뒤 조건을 다시 확인합니다. 부작용이 있는 조건식이 한 번만 실행된다고 가정하면 안 됩니다.')],
  [('원문과 사용 조건', '즉시 성공, schedule 세 번 뒤 성공, 처음부터 signal이 있는 경우와 대기 중 signal이 생기는 경우를 검사했습니다.'),
   ('실행 검증의 범위',
    '완전한 rcuwait 헤더와 원문의 wake·finish 함수, timeout 조건 매크로를 직렬 task·signal·schedule·RCU·배리어 모델에서 검사했습니다. 실제 '
    '스케줄러 실행이나 동시성·메모리 순서의 증명은 포함하지 않습니다.')]),
 ('Rcuwait 대기 state와 barrier·놓친 wake를 막는 두 관측',
  'include/linux/rcuwait.h',
  '___rcuwait_wait_event',
  'waiter는 task 포인터를 공개하고, set_current_state의 암묵적 메모리 배리어 A를 거친 뒤 조건을 읽습니다. waker는 조건을 바꾸고 메모리 배리어 B를 거친 뒤 '
  'task 포인터를 읽습니다. 이 순서는 양쪽이 서로의 변경을 놓쳐 waiter가 계속 잠드는 문제를 막는 프로토콜의 일부입니다. task 상태 쓰기와 조건 읽기를 일반 변수 대입으로 바꾸면 '
  '원문의 메모리 순서 전제가 사라집니다.',
  '조건을 실제로 바꾼 쪽에서 wake를 호출하고, task 등록과 상태 전환을 원문의 순서대로 연결하세요. 직렬 모델의 실행 결과만으로 약한 메모리 모델에서 가능한 모든 경쟁을 검증했다고 '
  '판단하지 마세요.',
  [('waiter는 배리어 A 뒤에 무엇을 읽나요?',
    '대기 조건을 읽습니다.',
    '새 task 배열의 길이를 읽습니다.',
    '원문 wake 함수의 주석 표는 waiter가 task를 공개하고 배리어 A 뒤에 조건을 읽는 순서를 설명합니다.'),
   ('waker는 배리어 B 뒤에 무엇을 읽나요?',
    '등록된 task 포인터를 읽습니다.',
    '조건을 강제로 false로 바꿉니다.',
    'waker는 조건 변경과의 공개 순서를 맞춘 뒤 task 포인터를 확인합니다. 양쪽의 두 관측을 구별하세요.')],
  [('원문과 사용 조건', '배리어 관계는 kernel/exit.c의 rcuwait_wake_up 주석과 대조했습니다. 모델은 배리어 hook의 호출을 기록합니다.'),
   ('실행 검증의 범위',
    '완전한 rcuwait 헤더와 원문의 wake·finish 함수, timeout 조건 매크로를 직렬 task·signal·schedule·RCU·배리어 모델에서 검사했습니다. 실제 '
    '스케줄러 실행이나 동시성·메모리 순서의 증명은 포함하지 않습니다.')]),
 ('Rcuwait 일반 wait·schedule 명령과 반환값',
  'include/linux/rcuwait.h',
  'rcuwait_wait_event',
  '일반 대기 매크로는 공통 매크로의 초기 반환값을 0으로, 대기 명령을 schedule()로 지정합니다. 조건을 만족하면 0을 반환합니다. 조건이 false이고 대기 상태가 signal에 '
  '의한 중단을 허용하면 -EINTR을 반환할 수 있습니다. schedule에서 돌아왔다는 사실만으로 조건을 만족한 것은 아닙니다. 조건을 다시 검사하며, 종료할 때는 finish를 통해 '
  'task 포인터를 NULL로 만들고 TASK_RUNNING 상태를 복구합니다.',
  '반환값 0을 조건 성공으로, -EINTR을 허용된 signal에 의한 중단으로 해석하세요. signal 중단 뒤에도 task 등록과 대기 상태가 정리되는지 확인합니다. 일반 대기에는 남은 '
  'timeout을 양수로 반환하는 계약이 없습니다.',
  [('일반 대기에서 조건을 만족했을 때 반환값은 무엇인가요?',
    '0입니다.',
    '언제나 남은 timeout 5입니다.',
    '일반 대기 매크로는 초기 반환값 0을 사용합니다. 시간 제한 대기 매크로의 반환 계약과 구분해야 합니다.'),
   ('schedule에서 돌아오면 조건 검사 없이 곧바로 성공하나요?',
    '아닙니다. 반복문에서 다시 검사합니다.',
    '맞습니다. 모든 wake가 조건을 true로 만듭니다.',
    '다른 이유로 실행이 재개될 수도 있습니다. 깨어났다는 사실과 실제 조건을 만족했다는 사실은 구별해야 합니다.')],
  [('원문과 사용 조건',
    'TASK_UNINTERRUPTIBLE 상태의 성공 반복문과 TASK_INTERRUPTIBLE 상태의 signal 중단을 검사했습니다. 모든 상태 조합을 실행한 것은 아닙니다.'),
   ('실행 검증의 범위',
    '완전한 rcuwait 헤더와 원문의 wake·finish 함수, timeout 조건 매크로를 직렬 task·signal·schedule·RCU·배리어 모델에서 검사했습니다. 실제 '
    '스케줄러 실행이나 동시성·메모리 순서의 증명은 포함하지 않습니다.')]),
 ('Rcuwait timeout·잔여시간 0과 성공 1의 경계',
  'include/linux/rcuwait.h',
  'rcuwait_wait_event_timeout',
  '시간 제한 대기의 바깥 매크로는 먼저 조건과 초기 timeout을 검사합니다. 이미 조건이 true이면 task를 등록하지 않고 반환할 수 있습니다. ___wait_cond_timeout은 '
  '조건이 true인데 남은 시간이 0이면 반환값을 1로 바꿉니다. 따라서 조건 성공을 시간 만료의 0과 구별합니다. 조건이 false이고 timeout도 0이면 즉시 0으로 끝납니다. 실제로 '
  '기다리는 경우에는 schedule_timeout으로 남은 시간을 갱신합니다.',
  '유효한 음수가 아닌 timeout을 전달하세요. 0은 시간 만료, 양수는 조건 성공, 음수는 signal 오류로 구분합니다. 반환값 1이 항상 정확히 한 tick 일찍 깨웠다는 뜻은 '
  '아닙니다. 즉시 반환하면 waiter 등록 자체가 생략될 수 있습니다.',
  [('timeout이 0이어도 조건이 true이면 무엇을 반환하나요?',
    '1입니다.',
    '항상 시간 만료의 0입니다.',
    '조건 helper는 성공과 시간 만료를 구분하기 위해 조건이 true일 때 반환값 0을 1로 조정합니다.'),
   ('timeout이 0이고 조건이 false이면 prepare가 반드시 실행되나요?',
    '아닙니다. 곧바로 0을 반환할 수 있습니다.',
    '맞습니다. 항상 등록 후 schedule 합니다.',
    '바깥 조건 검사에서 시간 만료가 판정되면 내부 대기를 건너뜁니다. 이 즉시 반환 경로에서는 task 등록을 하지 않습니다.')],
  [('원문과 사용 조건', 'include/linux/wait.h의 원문 ___wait_cond_timeout을 모델에 포함했습니다. wait.h 전체 해설 완료로 기록하지는 않습니다.'),
   ('실행 검증의 범위',
    '완전한 rcuwait 헤더와 원문의 wake·finish 함수, timeout 조건 매크로를 직렬 task·signal·schedule·RCU·배리어 모델에서 검사했습니다. 실제 '
    '스케줄러 실행이나 동시성·메모리 순서의 증명은 포함하지 않습니다.')]),
 ('Rcuwait timeout 대기·signal과 완료 정리',
  'include/linux/rcuwait.h',
  '__rcuwait_wait_event_timeout',
  '시간 제한 대기의 내부 매크로는 반환값을 초기 timeout으로 설정하고 조건을 ___wait_cond_timeout으로 감쌉니다. schedule_timeout(__ret)의 반환값이 새 '
  '남은 시간이 됩니다. 끝까지 조건이 false이면 시간이 0이 되었을 때 0으로 끝납니다. 그 경계에서 조건이 true이면 helper가 1로 바꾸어 성공을 표시합니다. 조건이 false일 '
  '때 허용되는 signal이 들어오면 -EINTR로 끝나며, 이 경우에도 공통 finish 경로로 정리합니다.',
  '성공과 시간 만료를 구분하여 다음 동작을 결정하세요. 조건과 signal을 함께 관측했을 때는 조건을 먼저 판정합니다. 공통 매크로의 __ret가 어디서 갱신되는지 확인하고, 반복 평가되는 '
  '조건식에 부작용을 넣지 마세요.',
  [('만료 경계에서 남은 시간이 0이고 조건이 true이면 무엇을 반환하나요?',
    '조건 성공을 뜻하는 1입니다.',
    '항상 실패를 뜻하는 0입니다.',
    'helper는 만료 경계의 조건 성공도 시간 만료와 구별합니다. 마지막 조건 검사가 필요한 이유입니다.'),
   ('중단 가능한 signal로 끝나도 finish 정리는 실행되나요?',
    '그렇습니다.',
    '아닙니다. task 포인터를 계속 남깁니다.',
    'signal 분기는 반복문을 빠져나온 뒤 공통 finish로 이동합니다. 이 경로도 포인터와 task 상태를 정리합니다.')],
  [('원문과 사용 조건', '모델은 세 tick 뒤 만료, 세 번째 검사에서 조건 성공, 처음부터 signal이 있는 경우를 검사했습니다. 실제 tick 시간을 측정하지 않았습니다.'),
   ('실행 검증의 범위',
    '완전한 rcuwait 헤더와 원문의 wake·finish 함수, timeout 조건 매크로를 직렬 task·signal·schedule·RCU·배리어 모델에서 검사했습니다. 실제 '
    '스케줄러 실행이나 동시성·메모리 순서의 증명은 포함하지 않습니다.')]),
 ('Rcuwait finish·포인터 NULL과 TASK_RUNNING 복구',
  'kernel/rcu/update.c',
  'finish_rcuwait',
  'finish_rcuwait는 RCU 포인터 대입으로 w->task를 NULL로 만들고, __set_current_state(TASK_RUNNING)으로 현재 task의 대기 상태를 '
  '정리합니다. 등록을 해제하는 것이므로 task나 rcuwait 객체를 메모리에서 해제하는 함수는 아닙니다. prepare와 finish 양쪽의 포인터 쓰기에 호출자의 직렬화 규칙이 '
  '적용됩니다. 등록 해제와 객체 해제를 구별해야 수명 문제를 피할 수 있습니다.',
  'prepare와 finish를 직접 사용하는 코드는 등록과 정리를 짝으로 수행하세요. 객체 해제와 포인터 등록 해제를 구별합니다. 완료 뒤 active가 false라는 사실만으로 과거 '
  '참조까지 안전하게 해제할 수 있다고 판단하지 마세요.',
  [('finish가 저장하는 task 포인터 값은 무엇인가요?',
    'NULL입니다.',
    'current를 계속 유지합니다.',
    '원문은 RCU 포인터 대입으로 등록을 끝냅니다. 현재 task의 메모리를 해제하거나 다른 waiter로 교체하는 동작이 아닙니다.'),
   ('finish가 복구하는 task 상태는 무엇인가요?',
    'TASK_RUNNING입니다.',
    '항상 TASK_UNINTERRUPTIBLE입니다.',
    '대기 구간을 떠나는 task의 상태를 복구합니다. 반환 뒤 상위 코드가 대기 상태를 계속 유지하지 않게 합니다.')],
  [('원문과 사용 조건', 'kernel/rcu/update.c에서 이 함수 범위의 원문을 검토했습니다. 해당 큰 파일 전체의 완료로 기록하지는 않습니다.'),
   ('실행 검증의 범위',
    '완전한 rcuwait 헤더와 원문의 wake·finish 함수, timeout 조건 매크로를 직렬 task·signal·schedule·RCU·배리어 모델에서 검사했습니다. 실제 '
    '스케줄러 실행이나 동시성·메모리 순서의 증명은 포함하지 않습니다.')]),
 ('Rcuwait wake·RCU 보호와 반환 0의 두 원인',
  'kernel/exit.c',
  'rcuwait_wake_up',
  'rcuwait_wake_up은 반환값 0으로 시작하고 RCU 읽기 보호 구간에 들어갑니다. 메모리 배리어 B 뒤에 task 포인터를 읽고, 포인터가 있으면 wake_up_process의 '
  '결과를 전달합니다. task가 NULL이면 0이며, 등록된 task가 이미 실행 가능한 상태여서 깨우지 않았어도 0일 수 있습니다. 1은 task를 깨웠다는 뜻입니다. 이 함수는 대기 '
  '조건을 직접 true로 바꾸지 않습니다.',
  '조건 변경을 원문의 메모리 순서 규약에 맞춰 공개한 뒤 wake를 호출하세요. 반환값 0만으로 waiter 포인터가 없다고 단정하지 마세요. RCU의 수명 보호와 waiter 등록 쓰기의 '
  '직렬화는 별도로 지켜야 합니다.',
  [('wake의 반환값이 0이면 task 포인터가 반드시 NULL인가요?',
    '아닙니다. 이미 실행 가능한 task여도 0일 수 있습니다.',
    '맞습니다. 등록된 task가 전혀 없습니다.',
    'wake_up_process의 결과도 반환합니다. v6.12 원문 주석은 이미 running인 task를 깨우지 않았을 때 0임을 설명합니다.'),
   ('rcuwait_wake_up이 조건을 직접 true로 바꾸나요?',
    '아닙니다. task를 깨우는 동작을 시도합니다.',
    '맞습니다. 모든 호출이 조건을 바꿉니다.',
    '함수는 조건 인자를 받지 않습니다. 조건 변경은 호출자 프로토콜에서 수행하며, 깨움과 조건 변경은 역할이 다릅니다.')],
  [('원문과 사용 조건', 'wake_up_process의 반환 계약은 kernel/sched/core.c 주석과 대조했습니다. kernel/exit.c는 이 함수 범위만 검토했습니다.'),
   ('실행 검증의 범위',
    '완전한 rcuwait 헤더와 원문의 wake·finish 함수, timeout 조건 매크로를 직렬 task·signal·schedule·RCU·배리어 모델에서 검사했습니다. 실제 '
    '스케줄러 실행이나 동시성·메모리 순서의 증명은 포함하지 않습니다.')])]

def register(topic, q, detail):
    for title, path, symbol, principle, use, qa, cards in ROWS:
        topic(title, "동기화", path, symbol,
              "단일 task가 RCU로 안전하게 기다리는 방식과 조건·signal·timeout의 판정 순서를 실제 소스에서 배웁니다.",
              principle, use,
              "등록 상태, 대기 조건, task 상태, 반환값을 구분하고 대기 반복문과 wake의 배리어 관계를 추적하세요.",
              *(q(*x) for x in qa), details=[detail(*x) for x in cards])
