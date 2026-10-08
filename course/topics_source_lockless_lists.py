"""Whole llist implementation/header; individually authored contracts and macros."""
def register(topic, q, detail):
    def lesson(title, path, symbol, why, principle, use, reading, qa, cards):
        topic(title, '자료구조·알고리즘', path, symbol, why,
              principle, use, reading, *(q(*x) for x in qa),
              details=[detail(*x) for x in cards])

    lesson('Llist Batch·CAS 실패와 마지막 Link 갱신', 'lib/llist.c', 'llist_add_batch',
        '여러 노드를 이미 연결한 묶음을 shared head 앞에 한 번에 공개하는 원리를 배웁니다.',
        "먼저 READ_ONCE로 head의 first를 읽고 new_last->next를 그 first에 연결합니다. Try_cmpxchg는 head가 예상 first와 같으면 new_first를 공개하고 성공합니다. 실패하면 first를 실제 head 값으로 갱신하므로 loop에서 new_last->next도 그 값에 다시 연결합니다. 반환 !first는 성공 직전에 목록이 비어 있었는 지를 뜻합니다.",
        'New_first부터 new_last까지 올바르게 연결되고 끝이 실제 마지막인 새 묶음을 제공합니다. 같은 node를 동시에 다른 list에 넣지 않습니다. 반환 false도 삽입 성공이며 기존 목록이 있었다는 뜻입니다. 객체 초기화·수명과 NMI-safe cmpxchg 조건을 유지합니다.',
        "First의 expected 역할,실패 후 next 재연결,성공 뒤!first를 읽으세요.",
        [('Batch 삽입의 false 반환은 무엇인가?', '성공 직전 목록이 비어 있지 않았다', '묶음을 넣지 못했다는 allocation 오류이다', 'Loop는 CAS 성공까지 재시도합니다. 최종 반환은 이전 head의 NULL 여부이며 작업 실패 코드가 아닙니다.'),
         ('CAS 실패로 first가 다른 head로 바뀌면?', 'New_last의 next를 새 first에 다시 연결한다', '처음 읽은 head를 끝까지 고정한다', 'Try_cmpxchg의 expected 갱신과 do loop의 next 대입이 함께 동작합니다. 새로 들어온 목록을 잃지 않게 재연결합니다.')],
        [('C 포인터', 'Head는 목록 입구의 first pointer입니다. New_last->next는 새 묶음 끝의 link이고 &head->first는 CAS가 바꿀 저장 위치의 주소입니다. Node 내용과 head pointer 갱신을 구분합니다.'),
         ('원자성과 문맥', 'Head 공개는 atomic primitive와 연결되지만 그 사실만으로 임의 순회나 해제·재사용이 안전해지지는 않습니다. NMI 사용은 CONFIG_ARCH_HAVE_NMI_SAFE_CMPXCHG 같은 architecture 조건도 필요합니다.')])

    lesson('Llist Del First·Acquire와 단일 소비자', 'lib/llist.c', 'llist_del_first',
        '첫 노드를 하나씩 제거하는 CAS loop와 다중 소비자에서 필요한 별도 제약을 배웁니다.',
        'Smp_load_acquire로 head를 읽고 NULL이면 종료합니다. Entry->next를 READ_ONCE로 읽어 CAS의 새 head로 전달합니다. 실패하면 entry가 갱신되어 새 next를 읽습니다. 성공하면 원래 첫 entry를 반환합니다. 여러 add와 한 del_first 소비자는 가능하지만 여러 소비자가 del_first 또는 del_all을 섞으면 별도 lock이 필요하다고 원본은 규정합니다.',
        '한 소비자 규약을 지키거나 소비자끼리 잠금으로 직렬화합니다. 반환 node를 사용한 뒤 수명과 재삽입 조건을 관리합니다. CAS가 있다는 이유로 모든 pop 조합에 lock이 없어도 된다고 판단하지 않습니다.',
        "Acquire 첫 읽기,NULL guard,next와 expected retry,다중 소비자 주석을 읽으세요.",
        [("여러 소비자가 del_first를 동시에 사용해도 CAS만으로 허용되는 가?", '원본은 별도 소비자 lock을 요구한다', '원본은 모든 소비자 조합을 무조건 허용한다', 'Head가 같은 pointer로 돌아와도 next가 달라질 수 있는 interleaving이 있습니다. 원본의 다중 소비자 제약을 따라야 합니다.'),
         ("비어 있는 목록의 del_first 결과는 ?", 'NULL이다', '항상 임시 node를 새로 할당한다', 'Entry==NULL이면 즉시 반환합니다. Allocation이나 빈 placeholder node 생성은 없습니다.')],
        [('ABA와 Link', '다른 소비자가 head를 제거하고 다시 넣는 동안 주소가 같아져도 next는 바뀔 수 있습니다. Head pointer의 equality만으로 처음 읽은 next의 타당성이 보장되지 않는 것이 이 규약의 핵심입니다.'),
         ('LIFO', 'Head 앞에 새 node를 넣고 head에서 하나를 빼므로 최근 추가한 node가 먼저 나옵니다. 자동 FIFO 큐가 아니며 오래된 항목 우선 처리는 분리한 묶음을 뒤집는 방식 등으로 구성합니다.')])

    lesson('Llist Del This·첫 항목의 신원 검사', 'lib/llist.c', 'llist_del_first_this',
        '특정 node가 첫 항목인 경우에만 제거하는 연산의 조건과 concurrent caller 계약을 배웁니다.',
        'Acquire로 entry를 읽고 entry!=this이면 false입니다. 같으면 next를 읽고 head CAS로 제거합니다. CAS가 실패해 실제 head가 바뀌면 entry가 갱신되어 다시 신원 검사합니다. 성공하면 true입니다. 원본은 여러 add와 concurrent 호출이 가능하되 각 caller가 서로 다른 this를 제공하는 조건을 명시합니다.',
        "실제로 존재하고 수명이 보호되는 비 NULL node를 this로 제공합니다. 이 API가 목록 중간의 임의 node를 탐색·제거한다고 생각하지 않습니다. 여러 caller가 같은 node를 제공하는 경우까지 원본의 허용 조건으로 확대하지 않습니다.",
        "Entry!=this guard,CAS 실패 뒤 identity 재검사,다른 this 조건을 읽으세요.",
        [('This가 목록 두 번째 node이면 이 연산은?', "False로 반환하고 제거하지 않는 다", '전체 list를 탐색하여 해당 node를 제거한다', '첫 entry와 this가 다르면 즉시 false입니다. 중간 node 검색 loop는 없습니다.'),
         ('Concurrent caller 허용에 붙은 원본 조건은?', '각 caller가 서로 다른 this를 제공한다', '모든 caller가 반드시 같은 this를 제공한다', '원본 주석은 all callers offer a different this라는 조건을 명시합니다. 그것을 임의 다중 pop 허용과 섞지 않습니다.')],
        [('NULL 전제', "Head가 NULL이고 this도 NULL이면 inequality guard가 제거를 막지 못하고 next 접근으로 이어질 수 있습니다. 유효한 실제 node를 제공하는 caller 전제를 유지하며 NULL pop 대체로 쓰지 않습니다."),
         ('실패의 의미', "False는 그 확인 시점에 대상이 head가 아니라는 뜻입니다. 잠금 없이 이후에도 계속 같은 head 상태로 남는 다는 예약이나 수명 보장을 제공하지 않습니다.")])

    lesson('Llist Reverse·분리한 Chain의 Link 방향', 'lib/llist.c', 'llist_reverse_order',
        '추가 순서의 반대로 쌓인 singly linked chain을 뒤집어 오래된 항목부터 처리하는 원리를 배웁니다.',
        'New_head=NULL에서 시작하여 현재 tmp를 잡고 원래 head->next를 다음 head로 저장합니다. Tmp->next를 지금까지 뒤집은 new_head로 바꾸고 new_head=tmp로 이동합니다. 입력이 끝날 때까지 반복한 뒤 새 첫 node를 반환합니다. 원래 다음 link를 먼저 보관해야 남은 chain을 잃지 않습니다.',
        "Llist_del_all로 분리하는 등 독점적으로 다루는 유한 NULL 종료 chain에 사용합니다. 공유 head에서 다른 producer가 수정 중인 chain을 임의로 뒤집지 않습니다. 반환값을 새 chain 입구로 사용하며 empty는 NULL입니다.",
        "원래 next 보관→next 뒤집기→newhead 이동의 순서를 읽으세요.",
        [('Chain C→B→A→NULL을 reverse하면?', 'A→B→C→NULL이다', '새 node를 allocation하여 같은 순서를 복사한다', '원본 node의 next를 직접 바꿉니다. 입력 순서를 뒤집지만 새 node를 만들지는 않습니다.'),
         ('원래 next를 먼저 보관하는 이유는?', 'Link를 바꾼 뒤에도 남은 chain을 계속 읽기 위해서다', "Data 내용을 항상 0으로 초기화하기 위해서다", 'Tmp->next를 덮으면 원래 다음 node 위치를 잃습니다. Head=head->next를 먼저 수행하여 남은 chain을 보존합니다.')],
        [('복잡도', "각 node를 한 번 방문하므로 O(n)이고 local pointer 몇 개만 사용합니다. Allocation 없는 in-place link 변경입니다."),
         ('소유권', 'Lockless 삽입 primitive와 reverse의 plain next 대입은 역할이 다릅니다. 분리되어 안전하게 소유한 chain을 순회한다는 전제가 중요합니다.')])

    lesson('Llist 초기화·NULL Head와 Self Node Marker', 'include/linux/llist.h', 'init_llist_node',
        '목록의 빈 상태와 node의 비소속 표시를 서로 다른 pointer 값으로 표현하는 방법을 배웁니다.',
        'Llist_head는 first, llist_node는 next 한 필드입니다. LLIST_HEAD_INIT와 init_llist_head는 first=NULL로 빈 목록을 만듭니다. Init_llist_node는 next=node로 self marker를 만듭니다. 정상 NULL 종료 chain에 연결된 node의 next는 자신을 가리키지 않으므로 llist_on_list는 next!=node를 검사합니다.',
        'Node 소속 marker를 사용할 때 init_llist_node 규약을 지킵니다. Self marker는 실제 chain의 종단 표현이 아니므로 그 상태의 node를 chain 순회 시작으로 넘기지 않습니다. 정적 head 선언과 동적 init의 같은 빈 표현을 확인합니다.',
        "두 struct,head macro,NULL 초기화,self next 대입을 읽으세요.",
        [('초기화한 독립 node의 next 값은?', '자기 자신이다', "언제나 NULL이다", "Init_llist_node는 node->next=node로 아직 list에 있지 않다는 marker를 둡니다. 빈 head의 NULL과 다릅니다."),
         ("Chain의 마지막 node가 NULL을 가리키면 on_list는?", "Self marker가 아니므로 true이다", "NULL이므로 반드시 false이다", "검사는 node->next!=node입니다. NULL은 실제 chain 끝의 정상 link일 수 있고 비소속 self marker와 다릅니다.")],
        [('구조체 표현', '자료 객체 안에 llist_node를 넣고 container_of로 바깥 객체를 찾는 intrusive 방식입니다. Node에는 자료 내용이나 previous pointer가 없습니다.'),
         ('Include 연결', 'Include/linux/llist_api.h는 llist.h를 포함하는 한 줄의 bridge입니다. 별도의 알고리즘 구현을 중복 정의하지 않으며 실제 API와 macro는 이 header에 있습니다.')])

    lesson('Llist 상태 조회·Empty와 On List의 한계', 'include/linux/llist.h', 'llist_empty',
        "빠른 pointer 조회가 동시 변경 중 상태 예약이나 객체 수명 보호를 대신하지 않는 다는 점을 배웁니다.",
        "Llist_empty는 READ_ONCE(head->first)==NULL을 반환하고 원본은 정확하거나 최신이라는 보장을 하지 않는 다고 설명합니다. Llist_on_list는 next!=node marker를 보고 llist_next는 plain next를 반환합니다. 이 조회 함수들은 node를 제거하거나 새 소유권을 얻지 않습니다.",
        'Empty 확인 뒤 다른 CPU가 add할 수 있으므로 필요한 실제 동작의 atomic API 결과를 사용합니다. On_list는 초기화·삭제 후 marker 관리 규약에 달린 표시입니다. Next 조회는 안전하게 분리되거나 보호된 node 수명 안에서 사용합니다.',
        "Empty의 READ_ONCE와주석,on_list 비교,next 반환을 읽으세요.",
        [("Empty가 true이면 이후 del_all도 반드시 NULL인가?", "그 사이 add가 가능하여 보장되지 않는 다", "True가목록을 잠가다른 add를 막는 다", '상태 읽기는 lock 획득이 아닙니다. 동시 실행 중에는 확인과 실제 동작 사이에 목록이 바뀔 수 있습니다.'),
         ("Llist_next 호출이 객체 참조 수를 증가시키는 가?", 'Plain next를 반환할 뿐이다', '자동으로 수명 참조를 획득한다', '원본은 return node->next입니다. 조회와 수명 보호는 별개이며 caller가 유효 node를 보장합니다.')],
        [('Marker의 갱신', "일반 del_first는 반환 node의 next를 self로 초기화하지 않습니다. 제거 후 on_list 표시가 자동 false로 바뀐다고 가정하지 않고 init variant와 구분합니다."),
         ('예측과 동작', '빠른 empty 조회는 작업 필요성을 살피는 hint로 사용할 수 있습니다. 검사를 통과했다고 다음 head 상태나 detached chain의 소유권이 생기는 것은 아닙니다.')])

    lesson('Llist 비원자 Add·이중 Underscore 규약', 'include/linux/llist.h', '__llist_add_batch',
        '이름이 비슷한 helper라도 CAS가 있는 경로와 plain pointer 대입 경로의 동기화가 다름을 배웁니다.',
        "__llist_add_batch는 new_last->next=head->first와 head->first=new_first를 plain 대입하고 이전 next가 NULL인지 반환합니다. __llist_add는 같은 node를 양 끝으로 전달합니다. 일반 llist_add는 llist_add_batch의 CAS 경로에 연결됩니다. Double underscore variant에는 동시 producer retry가 없습니다.",
        "독점 접근이나 별도 보호가 있는 문맥에서 만 plain variant를 사용합니다. 같은 bool 반환이 같은 concurrency 계약을 의미하지 않습니다. 새 묶음의 연결과 유효 수명은 atomic variant와 마찬가지로 caller가 준비합니다.",
        "두 add wrapper의호출대상과 plain batch 대입을 비교하세요.",
        [("Double underscore batch가 CAS를 사용하는 가?", "Plain pointer 대입을 한다", "항상 try_cmpxchg retry를 실행한다", "Headerbody에는 단순 next와 head 대입만 있습니다. 일반 llist_add_batch와동시성계약이다릅니다."),
         ("일반 llist_add의묶음양끝은?", "같은 새 node이다", "기존목록의 first와 last이다", "Llist_add(new,head)는 llist_add_batch(new,new,head)를 호출합니다. 한 node삽입을 batchAPI로표현합니다.")],
        [('분리된 Chain', '독점으로 가진 임시 chain에는 plain helper를 사용할 수 있지만 공유 head의 producer 경쟁을 그것만으로 처리할 수는 없습니다. 함수 이름보다 실제 primitive와 보호 문맥을 봅니다.'),
         ('성공 반환', "두 batch variant의 bool은 기존 목록이 비어 있었는 지를 표현합니다. False를 할당 실패나 새 node 거절로 해석하지 않습니다.")])

    lesson('Llist Del All·Atomic Detach와 반환 Chain', 'include/linux/llist.h', 'llist_del_all',
        '전체 목록을 한 pointer 교환으로 분리하고 detached chain을 caller가 처리하는 원리를 배웁니다.',
        "Llist_del_all은 xchg(&head->first,NULL)로 shared head를 비우면서 이전 first를 반환합니다. 분리 이후 추가되는 node는 새 shared head로 들어가며 이전 chain과 구분됩니다. __llist_del_all은 first를 plain 읽고 NULL을 대입하는 별도 비원자 경로입니다. 분리된 chain의 순서는 최근 삽입이 먼저입니다.",
        '여러 producer와 여러 del_all consumer 조합은 원본의 허용 표를 따릅니다. Del_first consumer와 섞을 때는 별도 lock 조건을 확인합니다. 반환 chain의 처리·해제·재사용 수명은 caller가 관리합니다.',
        "Xchg의 old 반환과 NULL 공개,plain variant,concurrency 표를 읽으세요.",
        [("Del_all 뒤 producer가새 node를 넣으면?", "분리된 oldchain과별도 sharedhead에들어간다", "이미반환한 chain의마지막에자동 append된다", "Head는 교환시 NULL로바뀝니다. 이후삽입은 현재 head에 연결하며이미분리한 old입구를 append대상으로 삼지않습니다."),
         ("여러 del_all과 producer조합은 원본표에서 lock이 필요한가?", "그조합은 lock없이허용된다", "모든 경우하나의 globalmutex가필수이다", "원본표는 add와 del_all,del_all끼리의조합을 허용합니다. Del_first소비자와섞는 제약까지같이확인해야합니다.")],
        [('빈 결과', "빈 head를 교환하면 NULL입니다. 별도 empty선검사없이 atomic 결과로소비할 chain이 있는 지판단할 수있습니다."),
         ('재사용 전제', "반환된 node의 주소를 다른 흐름이여전히사용하는 지와 producer에다시공개하는 시점은 별도수명규약입니다. 원자 detach를 임의해제의안전증명으로 확대하지 않습니다.")])

    lesson('Llist Del First Init·제거와 Marker Reset', 'include/linux/llist.h', 'llist_del_first_init',
        '제거 결과의 pointer와 비소속 marker 갱신을 하나의 wrapper로 연결하는 방법을 배웁니다.',
        "Llist_del_first_init은 일반 del_first 결과를 n에저장합니다. N이있으면 init_llist_node(n)로 next를 self로바꾸고 n을 반환합니다. NULL 결과에서 는 초기화를 하지 않습니다. 따라서 on_list 검사는 성공제거 node에 false를 보고하지만일반 del_first의소비자제약은 그대로유지됩니다.",
        "반환 node를 다시삽입할 때새 next가구성된다는 점을 읽습니다. Initwrapper가다중 소비자 ABA 조건이나수명문제를 자동해결한다고설명하지 않습니다. NULL인지검사한후자료 객체로접근합니다.",
        "Del_first 호출,n guard,init_llist_node와 return을 읽으세요.",
        [("Initvariant로제거한 node의 on_list는?", "Selfmarker이므로 false이다", "제거전 next가남아항상 true이다", "성공결과의 next를 자기자신으로 초기화합니다. 일반 del_first와달리비소속 marker를 함께갱신합니다."),
         ("빈 목록에서 Initvariant는?", "NULL을 반환하고 node 초기화를 하지 않는 다", "NULL을 node로 dereference하여초기화한다", "If(n)guard가 NULL 결과의 init 호출을 막습니다. 정상사용의빈 목록경로입니다.")],
        [('Link 파괴', "성공 node의 이전 next는 self로바뀝니다. 그 node를 첫입구로원래 chain전체를 순회하려는 사용법과맞지않습니다. 반환된단일 node의소유권과남은 sharedchain을 구분합니다."),
         ('보호의 범위', "Wrapper는 markerreset만추가합니다. Del_first가단일 소비자또는 소비자 lock을 필요로하는 조건은 바뀌지않습니다.")])

    lesson('Llist 순회 Macro·Safe의 Next 미리 저장', 'include/linux/llist.h', 'llist_for_each_safe',
        '분리한 chain을 순회하며 현재 node를 제거하거나 해제할 때 다음 pointer를 미리 보관하는 원리를 배웁니다.',
        "일반 for_each는 현재 pos의 next로다음반복을 진행합니다. Safevariant는 body전에 n=pos->next를 저장하고 body 뒤 pos=n을 사용합니다. Pos가 NULL이면 끝입니다. Safe는 현재 node의삭제에대해다음 pointer를 보관한다는 뜻이며 sharedchain을 동시에바꾸는 모든 상황에안전하다는 표시는 아닙니다.",
        "Del_all등으로 분리한안전한 chain에서 사용합니다. 현재 node를 free하는 body에는 safevariant를 선택하고다음 node의 수명도유지합니다. 초기화 selfmarker 상태의 node를 NULL 종료 chain이라고순회하지 않습니다.",
        "For초기식,condition에서 next 저장,증가식의 pos=n을 비교하세요.",
        [("현재 pos를 body에서 해제할 때 safe가저장하는 것은?", "해제 전의 pos->next이다", "해제 후 pos메모리를 다시읽은 값이다", "반복 condition에서 n을 먼저구합니다. 증가식은 현재 node의 메모리를 다시 dereference하지 않고 n을 사용합니다."),
         ("Safe macro가 sharedhead의 동시 변경까지잠그는 가?", "별도 lock이나 snapshot을 제공하지 않는 다", "이름 safe가모든 경쟁을 자동제거한다", "Macro는 next임시저장만수행합니다. 원본은 일반적으로 분리된 entries를 안전하게순회하라는 계약을 둡니다.")],
        [('빈 Chain', "입구 NULL이면 pos가 NULL이라 body를 실행하지 않습니다. Selfmarker는 NULL이아니므로 끝없는 자기순회가될 수있어소속규약을 지킵니다."),
         ('순서', "Del_all직후의 chain은 newest→oldest입니다. 순회 macro는 그순서를 바꾸지않으며필요한 FIFO처리는 먼저 reverse합니다.")])

    lesson('Llist Entry 순회·Container 주소와 NULL Member', 'include/linux/llist.h', 'member_address_is_nonnull',
        '구조체 안의 node를 바깥 자료 객체로 바꾸는 순회 macro와 종료 주소 검사의 원리를 배웁니다.',
        "Llist_entry는 container_of로 member의 주소에서 바깥 object주소를 계산합니다. For_each_entry는 그 object를 cursor로쓰고 member_address_is_nonnull은 uintptr_t(cursor)+offsetof(type,member)!=0을 검사합니다. NULLnode에서 계산한가상 container가 NULLobject가아닐수있어 member주소의 0여부를 검사합니다. Safeentryvariant는 다음 containercursor도 body전에구합니다.",
        "실제자료 type과 member이름을 정확히지정합니다. 종료시에계산된 containercursor를 진짜 object로 dereference하지 않습니다. 이 macro의저수준주소표현을 표준 C의임의 NULL역참조허용으로 확대하지 않고원본 compiler문맥에서 읽습니다.",
        "Container_of,typeof,offsetof,integer주소합과 entrysafe 다음값을 읽으세요.",
        [("종료조건이 objectpointer!=NULL만검사하지 않는 이유는?", "NULLnode에서 계산한 container주소가 NULL이아닐수있어서다", "모든 object를 malloc으로 다시만들어야해서다", "Memberoffset을 빼면 containercursor는 0이 아닌가상주소가될 수있습니다. 실제 member주소를 다시합해 0인지검사합니다."),
         ("Entry safe의 n cursor는 언제준비되는 가?", "현재 objectbody전에 다음 member에서 계산된다", "현재 objectfree후그메모리를 다시읽는 다", "Condition에서 pos->member.next를 읽어다음 cursor를 미리구합니다. 현재 node제거뒤그현재 object를 다시읽지않도록합니다.")],
        [('Intrusive 자료구조', "연결 node를 자료 객체안에넣으므로목록용별도 wrapperallocation을 줄일 수있습니다. 대신바깥 objecttype과 memberoffset이맞아야합니다."),
         ('Macro와 함수', "Typeof와 offsetof를 이용하는 전처리 macro는 일반 C 함수와 다른 확장문맥을 갖습니다. 실제 head/node 초기화,detach,수명조건을 충족한뒤순회합니다.")])
