"""Whole RCU string and reference-counter interfaces."""
ROWS = []


def add(path, title, intro, principle, use, sections, questions):
    ROWS.append(dict(path=path, title=title, intro=intro, principle=principle,
                     use=use, area='메모리 수명 · RCU · 참조 계수 · 오류 정리',
                     sections=sections, questions=questions))


add('fs/btrfs/rcu-string.h', 'Btrfs RCU 문자열 전체: 복사와 지연 해제',
    '문자열 바이트와 RCU 해제용 헤드를 한 객체에 저장하는 작은 helper입니다.',
    '복사는 새 메모리에 하고 해제는 kfree_rcu로 지연합니다. 독자가 포인터를 읽는 문맥과 객체를 새 값으로 공개하는 과정은 호출자가 관리합니다.',
    '참조 계수 객체가 아니며 reader가 임의로 문자열을 수정해도 안전해지는 것은 아닙니다. rcu_str_deref가 NULL을 검사하거나 읽기 임계구역을 열어주지는 않습니다.',
    [('전체 구성', 'SPDX·저작권·guard와 types/string/slab/rcupdate/printk 포함 뒤에 rcu_string 구조체, strdup/free inline, 출력 wrapper 두 개, 문자열 역참조 매크로와 endif가 있습니다. 구조체는 rcu_head와 flexible char str[]이며 참조 카운터나 문자열 길이 필드는 없습니다.'),
     ('할당과 복사', 'rcu_string_strdup은 strlen(src)+1을 계산해 헤더와 NUL 포함 문자열 공간을 kzalloc합니다. 실패하면 NULL을 반환합니다. 성공 후 strscpy로 len 한도 내 복사하고 음수이면 WARN_ON, kfree, NULL 반환으로 정리합니다. 할당 마스크는 인자로 받습니다. NULL 원문이나 유효하지 않은 문자열을 자동 방어하는 API는 아닙니다.'),
     ('예상치 못한 잘림', '주석은 길이 측정 뒤 복사에서 예상치 못하게 잘리는 경우를 경고하려는 목적을 설명합니다. 이 검사가 원문의 동시 변경을 동기화하거나 일관된 스냅샷을 보장하지는 않습니다. 호출자는 strlen과 복사 동안 원문이 유효하게 유지되도록 해야 합니다.'),
     ('지연 해제', 'rcu_string_free는 NULL이면 아무것도 하지 않고 비NULL이면 kfree_rcu(str,rcu)를 호출합니다. 즉시 free와 달리 기존 RCU 독자가 끝난 뒤 회수하도록 맡깁니다. 그러나 이 helper는 공유 포인터에서 객체를 제거하거나 새 객체를 공개하지 않으므로 호출자의 교체 절차와 결합해야 합니다.'),
     ('출력 wrapper', 'printk_in_rcu는 rcu_read_lock, printk, rcu_read_unlock을 do-while0으로 묶습니다. ratelimited 버전은 같은 보호 구간에서 printk_ratelimited를 호출합니다. 가변 인자를 그대로 전달하며 RCU를 잡았다는 사실이 로그 내용의 정확성이나 rate limit 외의 보안 정책을 보장하지 않습니다.'),
     ('문자열 역참조', 'rcu_str_deref는 rcu_dereference 결과를 지역 __str에 한 번 담고 __str->str을 반환하는 GNU statement expression입니다. 읽기 잠금을 직접 잡지 않고 NULL도 검사하지 않습니다. 반환 char 포인터를 RCU 보호 밖에서 계속 사용할 권한을 주는 것은 아닙니다.'),
     ('CS 연결', 'flexible array의 한 번 할당, 측정과 복사 사이의 전제, 실패 시 즉시 정리와 공개 후 지연 회수의 차이, 읽기 보호와 값 변경의 분리를 학습합니다. 이 파일에는 교체 함수가 없으므로 문자열 교체 전체를 이 helper 하나의 기능으로 세지 않습니다.')],
    [('rcu_string에 참조 카운터가 있는가?', '없다. rcu_head와 문자열 배열만 있다', '있다. 독자마다 자동 증가한다', 'RCU 읽기 보호와 참조 계수는 다른 수명 관리 방식입니다. 이 구조체에는 계수 필드가 없습니다.'),
     ('rcu_str_deref가 NULL 입력을 안전하게 NULL 문자열로 바꾸는가?', '아니다. 읽은 객체의 str에 바로 접근한다', '그렇다. 내부 NULL 검사가 있다', '매크로는 rcu_dereference 후 __str->str을 반환합니다. 포인터 유효성과 읽기 보호 문맥은 호출자가 지켜야 합니다.'),
     ('복사 실패 경로에서 새 객체를 kfree_rcu로 해제하는가?', '아니다. 아직 반환하지 않은 객체를 kfree로 정리한다', '그렇다. 모든 메모리는 반드시 지연 해제한다', 'strscpy 음수 경로에는 kfree(ret)가 있습니다. 공개되지 않은 실패 객체와 독자가 볼 수 있는 객체의 회수 조건을 구분합니다.')])

add('include/linux/rcuref.h', 'Rcuref 헤더 전체: 편향된 참조 수와 RCU 안전한 마지막 put',
    'RCU로 메모리 안정성을 보장하는 사용처를 위한 참조 수 인터페이스입니다.',
    '저장값은 일반 참조 수보다1 작고 음수 영역에 포화·해제 상태를 둡니다. 빠른 경로는 원자 가감 후 부호로 분기하며 예외 상태는 외부 slowpath가 처리합니다.',
    'get 전에 객체 메모리가 유효하다는 보장이 필요합니다. put의 true는 수명 정리 권한을 알리는 결과이며 함수 자체가 메모리를 해제하지 않습니다.',
    [('전체 구성', 'SPDX·guard, atomic/bug/limits/lockdep/preempt/rcupdate 포함 뒤에 상태 상수 여섯 개, init/read, get slowpath 선언과 get, put slowpath 선언과 내부 put, rcusafe/일반 put wrapper, endif가 있습니다. slowpath의 상태 전이 구현은 lib/rcuref.c에 있어 이 헤더만으로 모든 경합 경로를 확인했다고 세지 않습니다.'),
     ('상태 인코딩', 'ONEREF0, MAXREF0x7fffffff, SATURATED0xa0000000, RELEASED0xc0000000, DEAD0xe0000000, NOREF0xffffffff입니다. rcuref_init(cnt)는 cnt-1을 atomic_set합니다. 예를 들어 초기 참조1은 저장0입니다. 이 상수들을 모두 일반적인 참조 개수라고 해석하면 안 됩니다.'),
     ('관측 함수', 'read는 저장값을 unsigned로 읽고 RELEASED 이상이면0, 아니면 c+1을 반환합니다. 이는 상태를 일반 개수로 해석하는 helper이지 다른 CPU의 이후 get/put을 막는 예약이나 잠금이 아닙니다. 별도의 초기 count 범위 검증 분기는 없습니다.'),
     ('get 빠른 경로', 'rcuref_get은 atomic_add_negative_relaxed(1)을 수행하고 결과가 음수가 아니면 true입니다. 음수이면 get_slowpath로 갑니다. 이 함수는 객체 메모리가 RCU 등으로 이미 안정적이라고 가정하며 acquire 읽기 장벽을 제공하는 일반 객체 공개 primitive가 아닙니다. 문서는 성공 제어 의존성이 이후 저장을 정렬한다고 설명합니다.'),
     ('put 내부 경로', '__rcuref_put은 RCU 읽기 보호도 없고 선점 가능하면 lockdep 경고를 냅니다. atomic_add_negative_release(-1)의 결과가 음수가 아니면 false이고 마지막 참조 또는 포화·dead 영역은 slowpath로 넘깁니다. 문서상 release는 앞선 읽기·쓰기를 정렬하고 최종 해제 성공에는 acquire 정렬도 필요합니다. 그 성공 처리는 헤더에 없는 slowpath와 함께 이해해야 합니다.'),
     ('rcusafe의 문맥 조건', 'rcuref_put_rcusafe는 내부 put을 그대로 호출합니다. 마지막 감소와 경쟁 get/put의 slowpath 사이에 객체를 회수할 grace period가 완료되지 않는 문맥이 필요하며 RCU 읽기 구역과 atomic 문맥을 예로 듭니다. 함수 이름이 호출자를 자동으로 RCU 읽기 구역에 넣지는 않습니다.'),
     ('일반 put의 선점 보호', 'rcuref_put은 preempt_disable, 내부 put, preempt_enable 순서로 released 값을 받아 반환합니다. 모든 문맥에서 호출할 수 있도록 내부 감소 처리 구간을 보호하는 wrapper입니다. 선점 금지는 다른 CPU의 원자적 참조 변경을 막는 전역 잠금이 아닙니다.'),
     ('결과와 수명 책임', 'put의 true는 마지막 참조를 해제해 이후 참조 획득이 불가능한 상태로 정리할 수 있다는 신호입니다. false는 활성 참조가 남았거나 경쟁 get/put으로 정리를 맡을 수 없다는 뜻입니다. 객체가 RCU 독자에게 노출되는 사용 방식이라면 해당 회수 규칙도 계속 지켜야 하며 이 헤더에 free 함수는 없습니다.'),
     ('CS 연결', '편향 카운터, 포화 영역, relaxed와 release/acquire의 역할, 제어 의존성, 선점과 CPU 간 동시성의 차이, 참조 획득 전에 필요한 포인터 수명 보장을 학습합니다. 실행 검증 없이 모든 경쟁 조합의 안전성을 별도로 증명했다고 주장하지 않습니다.')],
    [('참조 수1로 init하면 내부 저장값은?', '0이다', '1이다', 'rcuref_init은 cnt-1을 저장합니다. 이 편향 때문에 일반 원자 가감의 부호로 경계 경로를 구분할 수 있습니다.'),
     ('get이 이미 해제된 임의 포인터의 메모리를 안전하게 만드는가?', '아니다. 호출 전에 메모리 안정성을 보장해야 한다', '그렇다. 원자 증가가 모든 use-after-free를 방지한다', '원문은 RCU 등으로 객체 메모리가 안정적이라는 전제를 명시합니다. 카운터에 접근하려면 그 카운터 자체가 살아 있어야 합니다.'),
     ('put_rcusafe가 내부에서 rcu_read_lock을 호출하는가?', '아니다. 적합한 문맥은 호출자가 제공한다', '그렇다. 함수가 항상 읽기 구역을 자동 생성한다', 'wrapper는 __rcuref_put만 호출합니다. 일반 put도 RCU 읽기 잠금 대신 선점을 잠시 금지하는 구조입니다.'),
     ('put이 true이면 그 함수가 객체 메모리까지 해제한 것인가?', '아니다. 호출자에게 정리 가능 상태를 알린다', '그렇다. 내부 kfree가 완료되었다', '참조 수 함수는 객체 포인터와 destructor를 받지 않습니다. 반환값에 따라 사용자가 정리 절차를 수행합니다.')])
