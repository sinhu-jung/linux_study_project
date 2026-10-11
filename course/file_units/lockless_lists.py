"""Whole llist implementation and its concurrency contracts."""
ROWS = []


def add(path, title, intro, principle, use, sections, questions):
    ROWS.append(dict(path=path, title=title, intro=intro, principle=principle,
                     use=use, area='연결 리스트 · 원자 연산 · ABA · 소유권',
                     sections=sections, questions=questions))


add('lib/llist.c', '잠금 없는 리스트 구현 전체: CAS 재시도와 조건부 삭제',
    'NULL로 끝나는 단일 연결 리스트에 묶음을 넣거나 맨 앞 노드를 제거하는 구현입니다.',
    '헤드 포인터를 try_cmpxchg로 바꾸되 경쟁으로 값이 달라지면 새 관측값에 맞춰 재시도합니다. 임의의 소비자 조합까지 자동으로 안전한 자료구조는 아닙니다.',
    '하나의 del_first 소비자와 여러 생산자, 또는 del_all 소비자 조합 같은 명시적 계약을 지킵니다. 분리한 체인의 메모리 소유권과 재사용도 호출자가 관리해야 합니다.',
    [('전체 구성', 'GPL SPDX, NMI와 cmpxchg 제약, 저작권·작성자, kernel/export/llist 포함 뒤에 add_batch, del_first, del_first_this, reverse_order 네 함수와 GPL export가 있습니다. 노드 할당·해제와 대기 큐 처리는 이 파일의 역할이 아닙니다.'),
     ('묶음 삽입', 'llist_add_batch는 READ_ONCE로 기존 first를 읽고 new_last->next=first로 새 체인의 꼬리를 연결한 뒤 헤드를 new_first로 CAS합니다. 실패하면 try_cmpxchg가 first를 실제 관측값으로 갱신하므로 다음 반복에서 꼬리 연결도 다시 씁니다. 성공 시 !first를 반환해 그 삽입 직전에 비어 있었는지 알립니다. 이후에도 비어 있거나 혼자만 들어 있다는 보장은 아닙니다.'),
     ('묶음의 선행 조건', 'new_first에서 new_last까지의 체인은 호출자가 미리 연결해야 하며 유효한 노드를 전달해야 합니다. 함수가 중간 노드를 검사하거나 복사하지 않습니다. 단일 삽입은 헤더에서 같은 노드를 first와 last로 전달해 재사용합니다. 묶음 내부 순서는 그대로이고 기존 체인 앞에 놓입니다.'),
     ('맨 앞 삭제', 'llist_del_first는 smp_load_acquire로 entry를 읽고 NULL이면 반환합니다. entry->next를 READ_ONCE로 얻은 뒤 헤드를 next로 CAS합니다. 경쟁 실패 시 갱신된 entry에 대해 반복합니다. 성공하면 분리한 entry를 반환하지만 next를 자기 자신으로 초기화하거나 객체를 free하지 않습니다.'),
     ('소비자 제약과 ABA', '여러 생산자와 단일 del_first 소비자는 지원하지만 여러 del_first 소비자 또는 del_first와 del_all 소비자의 혼합에는 소비자 간 잠금이 필요합니다. 다른 소비자가 노드를 제거·재삽입해 헤드 주소는 같고 next는 달라지면 CAS가 변경 이력을 구분하지 못할 수 있습니다. 포인터가 원래 주소로 돌아오는 ABA와 노드 수명 문제를 연결해 이해합니다.'),
     ('특정 헤드만 삭제', 'llist_del_first_this는 acquire로 헤드를 읽고 entry!=this이면 false를 반환합니다. 같으면 next를 읽어 CAS하고 실패 시 다시 일치 여부를 검사합니다. 주석은 여러 호출자가 서로 다른 this를 제시하고 여러 add와 동시 실행하는 경우를 허용합니다. 전체 리스트에서 this를 찾아 지우는 함수가 아니며 this는 유효한 노드여야 합니다. NULL이면 빈 헤드와 같아진 뒤 next 접근이 발생할 수 있으므로 일반 실패 입력처럼 넘기지 않습니다.'),
     ('역순 변환', 'reverse_order는 new_head=NULL에서 시작해 현재 노드의 다음을 저장하고 그 노드의 next를 new_head로 돌립니다. 모든 노드를 한 번 방문하므로 시간 O(n), 추가 공간 O(1)입니다. 빈 체인은 NULL을 반환합니다. 원자 연산이 없으므로 공유 중인 활성 체인을 임의로 뒤집는 동시성 함수가 아닙니다.'),
     ('NMI와 CS 연결', '헤드 원자 연산이 가능하다는 사실만으로 NMI에서 안전한 것은 아닙니다. 주석은 ARCH_HAVE_NMI_SAFE_CMPXCHG가 없는 아키텍처의 NMI 사용을 제한합니다. CAS 성공 지점, 실패 재시도, acquire 관측, 생산자·소비자 조합, 스택 순서와 배치 소유권을 학습합니다. 소스 대조는 모든 CPU의 메모리 모델에 대한 실행 증명이 아닙니다.')],
    [('add_batch의 CAS가 실패하면 꼬리 next도 다시 쓰는가?', '그렇다. 갱신된 기존 헤드에 다시 연결한다', '아니다. 최초 관측값을 영원히 사용한다', '꼬리 연결 대입은 do 루프 안에 있습니다. 실패한 try_cmpxchg는 expected인 first를 갱신합니다.'),
     ('여러 del_first 소비자는 생산자가 있어도 무조건 잠금 없이 안전한가?', '아니다. 소비자 간 잠금이 필요한 조합이다', '그렇다. CAS가 있으므로 모든 경쟁이 해결된다', '헤드 주소가 되돌아와도 next가 바뀐 상태일 수 있습니다. 파일 주석이 단일 del_first 소비자 조건을 명시합니다.'),
     ('del_first_this는 중간에 있는 지정 노드도 찾는가?', '아니다. 현재 맨 앞이 지정 노드일 때만 제거한다', '그렇다. 일치할 때까지 체인을 순회한다', 'entry!=this이면 즉시 false입니다. 선형 탐색 루프는 없고 CAS 재시도만 있습니다.'),
     ('reverse_order는 새 노드를 할당하는가?', '아니다. 기존 next를 제자리에서 바꾼다', '그렇다. 역순 복사본을 만든다', '보조 포인터만 사용하고 기존 노드의 next를 덮어씁니다. 분리한 체인의 소유권이 중요합니다.')])

add('include/linux/llist.h', 'Llist 헤더 전체: 동시 실행 표와 분리 후 순회',
    '잠금 없는 단일 리스트의 구조체, 순회 매크로, 원자·비원자 wrapper와 사용 계약을 제공합니다.',
    '활성 리스트에서 체인을 원자적으로 분리한 뒤 순회하는 모델입니다. 헤드에는 first 하나, 노드에는 next 하나만 들어 있습니다.',
    '순회·삭제·노드 표시의 계약을 각각 확인해야 합니다. llist_on_list는 실제 특정 헤드의 구성원을 검색하는 함수가 아닙니다.',
    [('전체 구성과 동시 실행 표', 'SPDX와 guard 뒤의 긴 주석은 add/add, add/del_first, add/del_all, del_all/del_all은 잠금 없이 가능한 조합으로 설명합니다. del_first/del_first와 del_first/del_all에는 잠금이 필요합니다. 이어 atomic/container_of/stddef/types, 구조체·초기화·순회·조회·삽입·삭제 wrapper와 외부 선언이 있습니다.'),
     ('헤드와 노드 초기화의 차이', 'LLIST_HEAD_INIT과 LLIST_HEAD, init_llist_head는 헤드를 NULL로 초기화합니다. init_llist_node는 next를 자기 자신으로 설정해 off-list 표식을 만듭니다. 정상 체인의 마지막 노드는 next=NULL이므로 NULL을 off-list 표식으로 사용할 수 없습니다. 헤드 초기화는 공유 중인 데이터를 안전하게 비우는 원자 삭제와 다릅니다.'),
     ('on_list의 실제 의미', 'llist_on_list는 node->next!=node만 검사합니다. 삭제 함수가 항상 이 표식을 복구하는 것은 아니므로 분리되었어도 true일 수 있습니다. del_first_init은 삭제 성공 시 init_llist_node를 호출해 표식을 복구합니다. 어느 헤드에 있는지, 현재 다른 CPU가 접근하는지까지 판정하지 않습니다.'),
     ('객체 복원과 NULL 경계', 'llist_entry는 container_of입니다. entry 순회에서 NULL 노드를 감싼 계산상의 객체 포인터가 단순 NULL이 아닐 수 있어 member_address_is_nonnull을 사용합니다. 이 매크로는 uintptr_t 주소에 offsetof를 더해 멤버 주소가0인지 검사합니다. 실제 존재하지 않는 객체를 일반적으로 역참조해도 된다는 뜻이 아닙니다.'),
     ('네 순회 매크로', 'llist_for_each는 노드 next를 따라가고 safe는 다음 노드를 임시 n에 저장합니다. entry와 entry_safe는 포함 객체 타입과 member를 사용해 같은 역할을 합니다. 문서는 일반적으로 리스트에서 삭제·분리한 노드부터 순회하라고 요구합니다. safe는 현재 항목 정리를 돕는 것으로 활성 공유 체인의 임의 동시 수정 허가가 아닙니다.'),
     ('빈 리스트 검사와 next', 'llist_empty는 READ_ONCE(head->first)==NULL이며 문서가 최신·정확 상태를 보장하지 않는 빠른 검사라고 명시합니다. 검사 다음 순간 다른 생산자가 삽입할 수 있습니다. llist_next는 단순 next 읽기이며 독립적인 동기화나 수명 보호를 제공하지 않습니다.'),
     ('삽입 wrapper와 이중 밑줄', 'llist_add는 외부 llist_add_batch에 new를 first/last로 전달합니다. __llist_add_batch는 꼬리와 헤드를 일반 대입으로 연결하고 __llist_add는 그것을 사용합니다. 이중 밑줄 버전에는 CAS가 없어 외부 직렬화나 단독 접근 전제가 필요합니다. 원자 버전과 단순 이름 차이로만 이해하면 안 됩니다.'),
     ('전체 분리', 'llist_del_all은 xchg(&head->first,NULL)로 헤드를 원자적으로 비우고 이전 체인을 반환합니다. __llist_del_all은 일반 읽기와 쓰기만 수행합니다. 둘 다 노드를 free하지 않습니다. 단일 노드를 차례로 앞에 넣었다면 반환 순서는 최근 삽입부터이며 reverse_order로 뒤집어 오래된 순서를 만들 수 있습니다. 배치 안의 순서는 생산자가 연결한 순서입니다.'),
     ('단일 삭제와 표식 복구', 'llist_del_first는 외부 구현 선언이고 del_first_init은 결과가 비NULL일 때 자기참조 표식으로 바꿉니다. del_first_this와 reverse_order도 외부 선언입니다. 문서의 llist_init_node라는 철자와 달리 실제 wrapper가 호출하는 이름은 init_llist_node입니다. 이름보다 실행 코드를 기준으로 확인합니다.'),
     ('CS와 동기화 범위', '다중 생산자·소비자 역할, 원자 교환과 CAS의 차이, 분리된 작업 묶음의 처리, 침입형 연결 노드, 상태 표식과 실제 소속의 차이를 학습합니다. NMI 사용은 NMI-safe cmpxchg 아키텍처 조건을 지켜야 하고 lock-less가 모든 실행 문맥에서 wait-free라는 보장은 아닙니다.')],
    [('init_llist_node는 next를 무엇으로 설정하는가?', '노드 자기 자신의 주소다', '항상 NULL이다', 'NULL은 체인의 마지막 노드에도 쓰이므로 off-list를 구별하기 위해 자기참조를 사용합니다.'),
     ('del_all로 분리한 노드는 on_list가 반드시 false인가?', '아니다. 각 next를 자기참조로 바꾸지 않는다', '그렇다. 모든 노드 표식을 자동 초기화한다', 'del_all은 헤드 포인터만 교환합니다. 노드별 next는 원래 체인 연결을 유지합니다.'),
     ('__llist_add도 내부에서 CAS를 수행하는가?', '아니다. 일반 대입인 __llist_add_batch를 사용한다', '그렇다. llist_add와 원자성이 같다', '이중 밑줄 버전은 잠금 없는 동시 삽입 구현을 호출하지 않습니다. 사용 문맥의 별도 보호가 필요합니다.'),
     ('빈 리스트 검사 후 삽입이 발생하지 않았다고 단정할 수 있는가?', '없다. 관측 뒤 다른 생산자가 삽입할 수 있다', '있다. READ_ONCE가 이후 변경도 막는다', 'READ_ONCE는 잠금이나 소유권 획득이 아닙니다. 헤더도 최신성·정확성을 보장하지 않는 빠른 검사라고 설명합니다.')])
