"""Full timerqueue interface, representation and implementation."""
ROWS = []


def add(path, title, intro, principle, use, sections, questions):
    ROWS.append(dict(path=path, title=title, intro=intro, principle=principle,
                     use=use, area='시간순 큐 · 레드블랙 트리 · 최소값 캐시',
                     sections=sections, questions=questions))


add('include/linux/timerqueue_types.h', 'Timerqueue 타입 전체: 만료값과 캐시된 트리 루트',
    '만료 순서로 정렬할 객체와 큐 헤드의 데이터 표현입니다.',
    '각 객체는 rb_node와 ktime_t expires를 가지며 헤드는 rb_root_cached를 보유합니다.',
    '이 자료형만으로 타이머가 실행되거나 만료 콜백이 등록되지는 않습니다. 시간값 설정과 실제 실행 정책은 사용자가 관리합니다.',
    [('전체 내용', 'GPL SPDX와 guard, rbtree_types/types 포함, timerqueue_node와 timerqueue_head 정의, endif로 끝납니다. 외부 함수나 정렬 코드는 없습니다.'),
     ('침입형 노드', 'timerqueue_node의 node는 레드블랙 트리 연결을 객체 안에 포함합니다. expires가 비교 키입니다. 노드가 연결된 상태에서 expires만 바꾸면 기존 트리 위치와 정렬 관계가 어긋날 수 있으므로 제거 후 수정·재삽입 같은 절차가 필요합니다.'),
     ('최소값 캐시', 'head의 rb_root_cached는 일반 루트와 가장 왼쪽 노드 캐시를 함께 표현하는 자료형입니다. 큐는 반복되는 가장 이른 만료 조회를 빠르게 하기 위해 이를 사용합니다. 캐시 일관성을 유지하는 삽입·삭제 API와 함께 사용해야 합니다.'),
     ('CS 연결', '객체 내 연결 정보, 정렬 키의 불변성, 우선순위 큐와 실행 스케줄러의 역할 차이, 자주 조회하는 최소값 캐시를 학습합니다.')],
    [('expires가 있으면 이 구조체가 자동으로 콜백을 실행하는가?', '아니다. 시간순 정렬용 데이터다', '그렇다. expires에 도달하면 구조체가 실행한다', '타입에 함수 포인터나 실행 코드가 없습니다. 실제 만료 처리 정책은 상위 사용자 코드가 담당합니다.'),
     ('연결된 노드의 expires만 바꿔도 순서가 자동 복구되는가?', '아니다. 트리 위치를 다시 관리해야 한다', '그렇다. 필드 대입이 트리 재정렬을 호출한다', '평범한 필드 대입에는 재삽입이나 회전이 없습니다. 정렬 키 변경은 자료구조 연산과 함께 관리합니다.')])

add('include/linux/timerqueue.h', 'Timerqueue 공개 헤더 전체: 최소값 조회와 노드 표시',
    '추가·삭제·후속 노드 API와 캐시된 최소값 조회, 초기화 helper를 제공합니다.',
    '큐의 첫 만료 노드는 rb_first_cached로 얻습니다. 노드 연결 여부는 RB_EMPTY_NODE 표식을 통해 확인합니다.',
    '객체의 만료값과 노드 초기화를 구분하고 큐 접근을 외부에서 직렬화해야 합니다. queued 검사는 특정 큐의 소유권을 확인하는 검색이 아닙니다.',
    [('전체 파일', 'SPDX·guard 뒤에 rbtree와 timerqueue_types를 포함합니다. add/del/iterate_next 선언 세 개, getnext/init/node_queued/init_head inline 네 개, endif가 전부입니다.'),
     ('최소값 조회', 'timerqueue_getnext는 rb_first_cached로 왼쪽 끝을 읽고 rb_entry_safe로 포함 객체를 구합니다. 빈 큐의 NULL을 안전하게 NULL 결과로 바꾸며 트리를 매번 왼쪽으로 내려가는 탐색은 하지 않습니다. 이 함수는 큐에서 노드를 제거하지 않습니다.'),
     ('노드 초기화 범위', 'timerqueue_init은 RB_CLEAR_NODE(&node->node)만 수행합니다. expires에 현재 시간이나0을 넣지 않으므로 호출자가 사용할 만료값을 지정해야 합니다. node_queued는 !RB_EMPTY_NODE이며 유효하게 초기화·삽입·삭제한 노드라는 계약 아래에서 사용합니다.'),
     ('헤드 초기화와 소유권', 'init_head는 RB_ROOT_CACHED를 대입하여 빈 루트와 캐시를 설정합니다. 이미 사용 중인 큐의 노드를 안전하게 순회·해제하는 clear 연산이 아닙니다. node_queued에는 head 인자가 없어 어느 큐에 연결되었는지 검증할 수 없습니다.'),
     ('CS 연결', '캐시 조회의 O(1) 비용, 비어 있는 포인터의 안전한 포함 객체 변환, 상태 표식과 실제 소속의 차이, 초기화와 자원 정리의 차이를 학습합니다.')],
    [('timerqueue_init이 expires를0으로 초기화하는가?', '아니다. rb_node의 미연결 표식만 설정한다', '그렇다. 구조체 전체를 지운다', '본문은 RB_CLEAR_NODE 호출 하나입니다. 시간값은 별도로 설정해야 합니다.'),
     ('getnext가 빈 큐를 받으면?', 'NULL을 반환한다', '반드시 잘못된 객체 주소를 반환한다', 'rb_first_cached 결과를 rb_entry_safe로 변환하므로 NULL을 포함 객체처럼 계산하지 않습니다.'),
     ('node_queued만으로 특정 head에 속했는지 알 수 있는가?', '없다. 함수에 head 인자가 없다', '있다. 노드의 모든 조상을 순회한다', '검사는 노드의 미연결 표식만 봅니다. 다른 큐인지 판정하는 로직은 없습니다.')])

add('lib/timerqueue.c', 'Timerqueue 구현 전체: 만료값 비교와 최소값 변경 알림',
    '캐시된 레드블랙 트리를 이용해 타이머 객체를 만료값 순서로 보관합니다.',
    '작은 expires를 왼쪽에 배치하며 추가는 새 최소값인지, 삭제는 남은 큐가 비어 있지 않은지를 반환합니다. 두 bool 반환값의 의미는 다릅니다.',
    '이 라이브러리는 잠금을 잡지 않으므로 모든 큐 접근을 호출자가 직렬화해야 합니다. 경고가 잘못된 삽입·삭제를 자동으로 중단시키지는 않습니다.',
    [('전체 구성', 'GPL SPDX와 타이머 큐 설명·외부 직렬화 경고, bug/timerqueue/rbtree/export 포함, 노드 변환 매크로, 비교 helper, add/del/iterate_next 세 함수와 GPL export로 구성됩니다. 시계 읽기나 만료 콜백 호출은 없습니다.'),
     ('비교 함수', '__node_2_tq는 rb_entry로 timerqueue_node를 얻습니다. __timerqueue_less는 a->expires < b->expires만 비교하며 같을 때 false입니다. 주소나 별도 ID는 비교하지 않습니다. 만료값이 같다고 삽입을 거부하는 중복 검사도 없습니다.'),
     ('추가와 새 최소값', 'timerqueue_add는 RB_EMPTY_NODE가 아닌 입력에 WARN_ON_ONCE를 낸 뒤 rb_add_cached를 호출합니다. 하위 함수는 less이면 왼쪽, 아니면 오른쪽으로 내려가고 오른쪽 이동 시 leftmost=false로 기록합니다. 새 왼쪽 끝이면 노드 포인터를 반환하고 아니면 NULL이므로 bool wrapper는 새 최소값 여부가 됩니다. false도 정상 삽입 결과일 수 있습니다.'),
     ('같은 만료값의 처리', '동일 expires는 비교에서 false여서 오른쪽 경로로 삽입됩니다. 기존 최소값과 같은 시각의 새 노드는 기존 최소값을 대체하는 새 왼쪽 끝으로 보고되지 않습니다. 회전은 중위 순서를 유지하므로 이 삽입 규칙을 이해할 수 있지만 시간값의 유일성을 보장한다고 해석하면 안 됩니다.'),
     ('삭제 반환값의 다른 의미', 'timerqueue_del은 미연결 노드면 경고한 후 rb_erase_cached로 제거하고 RB_CLEAR_NODE로 표식을 복구합니다. 마지막 반환은 !RB_EMPTY_ROOT로, 삭제 후 큐가 남아 있는지입니다. 삭제 노드가 최소였는지 또는 삭제 성공 여부를 나타내는 값으로 해석하면 안 됩니다. 노드 메모리와 expires 값은 해제·초기화하지 않습니다.'),
     ('후속 노드 순회', 'iterate_next는 인자 NULL이면 NULL이고, 아니면 rb_next로 중위 후속 노드를 얻어 NULL 또는 포함 객체를 반환합니다. 큐를 변경하지 않는 순회용입니다. 삭제된 노드에서 다음을 찾거나 다른 실행 주체가 자유롭게 트리를 바꾸는 상황을 지원한다고 가정하면 안 됩니다. 삭제하면서 처리할 때는 필요한 다음 위치와 수명을 별도로 관리합니다.'),
     ('비용과 동기화', '균형 트리의 삽입·삭제는 노드 수 n에 대해 O(log n)이고 캐시된 최소값 조회는 O(1)입니다. 후속 노드 한 번 찾기는 트리 높이만큼 이동할 수 있으며 전체 중위 순회는 링크를 따라 선형으로 처리할 수 있습니다. 라이브러리에는 락·RCU·객체 참조 확보가 없으므로 검색만 한다고 무조건 동시 접근이 안전한 것은 아닙니다.'),
     ('CS 연결과 검증', '우선순위 큐의 최소값, 캐시 일관성, strict 비교와 중복 키, bool 반환값의 API별 의미, 경고와 입력 검증의 차이를 학습합니다. 같은 시각의 삽입 경로는 include/linux/rbtree.h의 rb_add_cached까지 원본 대조했으며 실제 타이머 인터럽트·경쟁 실행을 시험한 것은 아닙니다.')],
    [('add가 false를 반환하면 삽입 실패인가?', '아니다. 새 최소값이 아니어도 정상 삽입된다', '그렇다. 노드를 넣지 않았다는 뜻이다', '반환값은 rb_add_cached가 새 왼쪽 끝을 만들었는지의 bool 변환입니다. 메모리 할당 실패 상태가 아닙니다.'),
     ('마지막 노드를 삭제한 del 반환값은?', 'false다', 'true다', '삭제 후 큐가 비어 있지 않은지 반환하므로 빈 큐가 되면 false입니다. 삭제 자체가 실패했다는 뜻은 아닙니다.'),
     ('기존 최소 만료값과 같은 expires를 넣으면 새 최소값으로 보고되는가?', '아니다. 같은 값은 오른쪽 경로로 간다', '그렇다. 같은 값은 항상 왼쪽에 삽입된다', 'less가 엄격한 <이므로 같은 값은 false입니다. 하위 삽입 helper는 오른쪽 이동에서 leftmost를 false로 설정합니다.'),
     ('WARN_ON_ONCE가 중복 삽입을 안전하게 중단시키는가?', '아니다. 경고 뒤에도 삽입 호출이 이어진다', '그렇다. 즉시 false로 반환한다', '경고는 진단입니다. 이 함수에 경고 조건에 따른 조기 반환은 없으므로 호출 계약을 지켜야 합니다.')])
