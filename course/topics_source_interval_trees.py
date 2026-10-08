"""Generic interval tree template, instantiated implementation and span header."""
def register(topic, q, detail):
    def lesson(title, path, symbol, why, principle, use, reading, qa, cards):
        topic(title, '자료구조·알고리즘', path, symbol, why,
              principle, use, reading, *(q(*x) for x in qa),
              details=[detail(*x) for x in cards])

    lesson('Interval Tree Template·정렬 Key와 Subtree 최대 끝',
        'include/linux/interval_tree_generic.h', 'INTERVAL_TREE_DEFINE',
        '시작점으로 정렬한 tree에 각 subtree의 최대 끝을 추가하여 겹치는 구간을 찾는 원리를 배웁니다.',
        "Template은 node type,rb field,끝점 type,subtree 요약 field,시작·끝 getter,함수 prefix를 받습니다. Insert는 start 순서로 내려가며 ancestor의 최대 last를 늘립니다. 새 node의 요약은 last이고 equal start는 오른쪽에 넣습니다. MAX callback을 augmented rbtree의 삽입·삭제에 연결해 회전·제거 뒤 요약과 cached leftmost를 유지합니다.",
        "Start<=last인 inclusive 구간을 제공하고 연결된 node의 끝점을 임의로 변경하지 않습니다. 구간 tree의 요약 유지와 underlying red-black 균형 알고리즘은 별도 구현을 통해 연결됩니다. Caller가 접근과 node 수명을 보호합니다.",
        'Template 인자,insert 비교와 ancestor 갱신,remove forwarding을 읽으세요.',
        [("Subtree 요약은 어떤값인가?", "그 subtree전체구간의 최대 last이다", "현재 node의 start만복사한값이다", "ITLAST와 MAXcallback을 이용합니다. Descendant의 끝이더멀면그값을 요약에반영하여검색가지치기에사용합니다."),
         ("Equalstart인새 node는 insert에서 어느 branch로가는 가?", "Else의오른쪽 branch이다", "항상중복으로 거절한다", "원본은 start<parentstart일때왼쪽이고그외에는 오른쪽입니다. 같은 start구간을 무조건거절하는 검사는 없습니다.")],
        [('Callback의 원리', 'MAX callback은 현재 last와 두 child의 subtree 요약의 최대를 계산합니다. Rotate·copy·propagate callback과 cached rbtree 연결이 이 값을 유지합니다. 이 파일이 회전 body를 직접 모두 구현하는 것은 아닙니다.'),
         ('실제 Instantiation', 'Lib/interval_tree.c의 START/LAST는 node의 start/last field입니다. INTERVAL_TREE_DEFINE이 unsigned long,__subtree_last,interval_tree prefix로 concrete insert/remove/iter_first/iter_next를 만들고 해당 함수들을 export합니다.')])

    lesson('Interval Subtree Search·두 겹침 조건과 왼쪽 후보',
        'include/linux/interval_tree_generic.h', '_subtree_search',
        '검색 구간과 겹칠 가능성이 없는 subtree를 최대 끝으로 제외하는 탐색 원리를 배웁니다.',
        "Inclusive 겹침은 node.start<=query.last와 query.start<=node.last 두 조건입니다. Search는 query.start<=subtree_last라는 전제에서 왼쪽 child의 요약이 충분하면 먼저 내려갑니다. 현재 start가 query.last 이하면 현재 last를 검사하고 필요하면 오른쪽을 봅니다. 요약이나 시작 순서가 겹침 가능성을 없애면 NULL입니다.",
        "상위 iter_first/next가 준비한 subtree와 유효 query를 사용합니다. 요약이 잘못되면 가능한 후보를 건너뛸 수 있어 끝점 변경과 augmentation 유지 규약을 지킵니다. 내부 helper를 직접 호출할 때는 loop invariant도 확인합니다.",
        "Loop invariant,왼쪽요약,두 Cond,오른쪽요약을 읽으세요.",
        [("구간[3,5]와 query[5,8]은 겹치는 가?", "끝점 5에서 겹친다", "항상반열린구간이라겹치지않는 다", "이자료구조의 last는 포함되는 끝입니다. 3<=8과 5<=5두 조건이성립합니다."),
         ("왼쪽 subtree의 최대 last가 query.start보다작으면?", "그왼쪽의 모든 구간은 끝이너무빨라제외한다", "반드시왼쪽최소 node부터전부방문한다", "최대끝조차 query시작전에있으므로 그 subtree의어떤 node도두 번째겹침조건을 만족하지 못합니다.")],
        [('요약의 효용', "검색 key인 start만으로 는 오래전에 시작해 길게 이어지는 구간을 제외할 수 없습니다. Subtree의 최대 last가 두 번째 조건의 가능한 후보 존재를 알려 줍니다."),
         ('Leftmost의 뜻', '반환은 start 정렬 순서에서 가장 왼쪽인 겹침 후보입니다. 가장 짧은 구간이나 가장 작은 last를 선택하는 정책이 아닙니다.')])

    lesson('Interval First·전체 범위 Fast Rejection',
        'include/linux/interval_tree_generic.h', '_iter_first',
        '빈 tree와 전체 끝점 요약을 먼저 확인하여 불필요한 검색을 줄이는 방법을 배웁니다.',
        "Iter_first는 root가 없으면 NULL입니다. Root의 subtree_last<query.start이면 모든 구간의 끝이 너무 빠르므로 NULL입니다. Cached leftmost의 start>query.last이면 모든 시작이 너무 늦으므로 NULL입니다. 두 검사를 통과하면 subtree_search로 실제 왼쪽 겹침을 찾습니다.",
        "요약과 cached leftmost가 올바르게 유지된 tree를 사용합니다. Fast 검사 통과가 겹침의 확정은 아닙니다. 구간 사이에 빈 공간이 있을 수 있습니다. 반환 NULL을 확인하고 수명 보호 아래 결과를 사용합니다.",
        'Empty root,rootmax,cachedleftmost,start/last 부등식을 읽으세요.',
        [("전체최대 last가 10인데 query시작 20이면?", "Treewalk없이 NULL이다", "최소 startnode를 항상반환한다", "Root요약이모든 끝의 최대값입니다. 어떤구간도 20까지이어지지않으므로빠른거절이가능합니다."),
         ("두 fast 검사를 통과하면 반드시겹침 node가 있는 가?", "실제 subtree검색이여전히필요하다", "그즉시 root가반드시정답이다", "최소시작과최대끝사이에구간이비어있을 수있습니다. Broadbounds통과는 실제교차확인이아닙니다.")],
        [('O(1) 경계 검사', "Root 요약과 cached leftmost만 읽는 빠른 거절은 상수 개수의 field 접근입니다. 전체 query 검색이 언제나 O(1)이라는 주장은 아닙니다."),
         ('예시', '[0,2]와[8,10]만 있을 때 query[4,5]는 전체 bounds 안이지만 실제 겹침은 없습니다. Broad range와 실제 구간 union의 차이입니다.')])

    lesson('Interval Next·오른쪽 Subtree와 Parent 복귀',
        'include/linux/interval_tree_generic.h', '_iter_next',
        '이미 찾은 겹침 node 뒤의 후보를 전체 tree 재검색 없이 이어서 찾는 원리를 배웁니다.',
        "Iter_next는 현재 node의 오른쪽 subtree 요약이 query.start를 덮으면 그 안에서 왼쪽 후보를 검색합니다. 없으면 parent로 올라갑니다. 오른쪽 child에서 올라온 ancestor는 이미 지난 영역이라 계속 올라갑니다. 왼쪽에서 올라온 ancestor의 start가 query.last를 넘으면 종료하고 last 조건이 맞으면 그 ancestor를 반환합니다.",
        "같은 query에서 찾은 node를 유효한 연결과 수명 안에서 넘깁니다. 삭제했거나 동시에 수정 중인 node를 cursor로 무조건 사용하지 않습니다. Start 기준 순서이며 동일 start의 안정적인 삽입 순서를 별도로 보장하지 않습니다.",
        'Right 요약,parent loop,prev==right 조건,ancestor 겹침 검사를 읽으세요.',
        [("오른쪽 child에서 parent로올라왔을 때 parent를 다시반환하는 가?", '이미지난순서라더올라간다', "항상같은 parent를 반복반환한다", "In-order 탐색에서 parent와그왼쪽은 이미현재 cursor보다앞입니다. Prev==parentright동안상승합니다."),
         ("다음 ancestor의 start가 query.last보다크면?", "이후후보도시작이늦으므로 NULL이다", "반드시최대 last만보고반환한다", "Start 정렬순서에따라오른쪽후속 node들도 query 끝뒤에서 시작합니다. 첫 번째겹침조건을 만족할 수없습니다.")],
        [('순회 구성', 'First로 시작하고 NULL이 나올 때까지 같은 query의 next를 이어 호출합니다. 모든 tree node를 반환하는 단순 in-order iterator와 겹침 필터의 역할을 구분합니다.'),
         ('균형의 역할', '이 template는 rbtree 연결을 따라갑니다. 실제 높이 제한과 회전은 underlying rbtree의 영역이며 plain BST mock에서 검색이 맞았다고 균형 비용까지 검증된 것은 아닙니다.')])

    lesson('Interval Span Merge·겹침과 인접 구간 합치기',
        'lib/interval_tree.c', 'interval_tree_span_iter_next_gap',
        '개별 node 구간 대신 연속 사용 영역과 빈 구간을 찾을 때 union 경계를 늘리는 원리를 배웁니다.',
        "Nodes[1]에서 시작하여 nodes[0]에 현재 사용 span의 최대 last를 가진 node를 둡니다. 다음 겹침 node가 현재 last 안 또는 last+1에서 시작하면 같은 연속 span으로 합칩니다. 더 먼 끝을 발견하면 nodes[0]를 바꾸고, 처음 분리된 다음 span의 node를 nodes[1]로 남깁니다.",
        "Nodes[1]이 비NULL이라는 내부 전제와 query 양끝을 유지합니다. Inclusive 끝점의 인접 관계를 사용하므로[2,4]와[5,7] 사이에 빈 정수 위치는 없습니다. Last+1의 unsigned 경계와 query clipping을 함께 읽습니다.",
        "최대 last node 갱신,iter_next,overlap/adjacency do-loop를 읽으세요.",
        [("구간[2,4]와[5,7]은 span에서?", "연속 used[2,7]로합쳐진다", "항상중간 hole[4,5]를 만든다", "끝점은 inclusive이고 4다음위치는 5입니다. 두구간사이에덮이지 않는 정수위치가없습니다."),
         ("현재 used 끝 10에구간[3,7]이추가되면끝은?", "10으로 유지된다", "무조건현재 node의 7로줄어든다", "원본은 cur.last가더클때만 nodes[0]를 바꿉니다. 포함된짧은 구간은 union 끝을 줄이지 않습니다.")],
        [('두 Node', "Nodes[0]는 현재연속사용 span의 끝을 결정하고 nodes[1]은 다음분리된사용 span의 시작입니다. 이둘사이가 interiorhole입니다."),
         ('Greedy span', "연속해서덮인모든 node를 합쳐가장긴 usedspan을 만듭니다. 하나의 node를 그대로 반환하는 queryiterator와 다른 출력형태입니다.")])

    lesson('Interval Span First·전체 Hole와시작 Clip',
        'lib/interval_tree.c', 'interval_tree_span_iter_first',
        '검색 범위가 전혀 쓰이지 않거나 사용 구간 중간에서 시작하는 경우의 첫 span을 구성합니다.',
        "First는 query 양끝과 두 node 상태를 초기화합니다. 겹침 node가 없으면 전체 범위를 hole로 반환합니다. 첫 node.start가 query 시작 뒤이면 leading hole을 만들고 다음 used span을 merge해 준비합니다. 이미 사용 중이면 start_used=query 시작으로 clip하고 최대 끝을 last_index까지 제한합니다.",
        "First_index<=last_index인 유효 inclusive 범위를 제공합니다. Is_hole과 해당 union field를 읽습니다. Used 끝이 query 끝에 닿으면 두 node를 NULL로 만들어 다음 호출의 종료를 준비합니다. 개별 node 대신 분류된 span을 얻는 API입니다.",
        "No node,leading hole,inside used,끝 clip과 nodeNULL을 읽으세요.",
        [("Tree가비었고 query[4,9]이면 첫 span은?", 'Hole[4,9]이다', 'Used[4,9]이다', "겹침 node가없으면 wholequery가 hole입니다. 다음호출에서 종료상태로이동합니다."),
         ("Usednode[0,10]안에서 query[3,6]을 시작하면?", "Used[3,6]으로 양끝을 clip한다", "항상 node원래범위[0,10]을 반환한다", "시작을 first_index로설정하고끝이 last_index이상이면 그 query 끝으로 제한합니다. 요청범위밖을 span 출력으로 확대하지 않습니다.")],
        [('Leading Hole', "Query시작 1이고첫 node가 4에서 시작하면 첫 hole은 1..3입니다. Endinclusive라 node시작-1을 hole 끝으로 사용합니다."),
         ('CONFIG', "이 span 구현은 CONFIG_INTERVAL_TREE_SPAN_ITER 안에있습니다. Header선언만으로 모든 빌드에 body가연결된다고가정하지 않습니다.")])

    lesson('Interval Span Next·Hole Used 교대와Done',
        'lib/interval_tree.c', 'interval_tree_span_iter_next',
        '전체 요청 범위를 빈 구간과 사용 구간으로 빠짐없이 이어서 출력하는 상태 전이를 배웁니다.',
        "두 node가 NULL이면 is_hole=-1로 끝냅니다. Hole 상태에서는 last_hole+1부터 준비된 used 끝까지 출력하고 query 끝에 clip합니다. Used 상태에서 다음 span node가 없으면 현재 끝+1부터 query 끝까지 trailing hole입니다. 두 node가 모두 있으면 현재 끝+1과 다음 시작-1 사이의 interior hole을 출력하고 다음 used를 merge합니다.",
        "First로 초기화한 iterator에서 done을 확인하며 진행합니다. Is_hole의0/1/-1을 bool 하나로 단순화하지 않습니다. 출력 span이 query 전체를 이어서 덮고 같은 위치를 중복 출력하지 않는 조건을 확인합니다.",
        "두 NULL 종료,hole→used,used→trailing/interiorhole 분기를 읽으세요.",
        [("마지막 used 뒤에요청끝까지빈위치가남으면?", "Trailinghole을 한번반환한뒤 done이다", "남은 query 위치를 조용히누락한다", "원본은 nodes[1]이 없는 used 상태에서 마지막끝+1부터 last_index까지 hole을 만듭니다. 다음에는 두 nodeNULL로종료합니다."),
         ('Is_hole=-1의뜻은?', "순회 완료이다", "항상 hole이있다는 true만뜻한다", "상태는 0used,1hole,-1done세종류입니다. Boolean 검사만으로 완료상태의 field를 사용하지 않습니다.")],
        [('Inclusive 연결', "이전끝+1이다음 span의 시작입니다. Hole과 used의양끝을 정수위치로이어 query를 빠짐없이분류합니다."),
         ('전체 Hole의 종료', "First에서 겹침이없었던경우현재 hole은 전체 query이고두 node가 NULL입니다. Next는 추가 used를 만들지않고 done으로 바꿉니다.")])

    lesson('Interval Span Advance·현재범위 재사용과재검색',
        'lib/interval_tree.c', 'interval_tree_span_iter_advance',
        '이미 찾은 span 안의 새 시작점으로 이동할 때 tree를 다시 검색하지 않는 원리를 배웁니다.',
        "Done이면 그대로 반환합니다. First_index를 new_index로 갱신하고 query 끝을 넘으면 done입니다. 현재 span 안이면 공유 start field만 new_index로 바꿉니다. 현재 끝+1이면 next 한 번으로 이동하고, 그 외에는 span_first를 new_index부터 다시 호출합니다. Hole/used field가 union으로 겹친다는 점을 이용합니다.",
        "Iterator와 node 수명·tree 일관성을 유지합니다. Done 상태의 advance는 자동 restart가 아니므로 새 순회에는 first를 호출합니다. Forward 사용과 query 끝 경계를 확인하고 UL_MAX 근처의 끝+1 산술도 unsigned 조건과 함께 읽습니다.",
        "Done guard,new 끝검사,current 범위,경계+1,next/first 분기를 읽으세요.",
        [("현재 span[10,20]안의 new15로 advance하면?", "시작 field만 15로바꿀수있다", "반드시 root부터전체재검색한다", "Current 범위조건을 만족하므로공유 start_hole/start_usedfield를 바꾸고바로반환합니다."),
         ("Done 상태를 advance로새시작점에서 자동재시작하는 가?", "Done이면 그대로 반환한다", "언제나 first를 다시 호출한다", "함수처음의 is_hole==-1guard가즉시 return합니다. 새 iterator시작은 명시적인 first 호출입니다.")],
        [('Union Alias', "Start_hole과 start_used가 같은 저장 field,last_hole과 last_used도같은 field입니다. Advance는 현재종류와무관하게범위검사와시작 clip을 공통으로 수행합니다."),
         ('상태 재사용', "현재 span 끝의바로다음위치는 기존 nodes 상태에서 next로갈수있습니다. 멀리이동하면 첫겹침검색과 spanmerge를 다시실행합니다.")])

    lesson('Interval Header·Node 표현과Span Iterator Macro',
        'include/linux/interval_tree.h', 'interval_tree_span_iter_done',
        '구간 node를 반환하는 API와 빈·사용 span을 반환하는 상태 구조체의 차이를 배웁니다.',
        "Interval_tree_node는 rb 연결,start,inclusive last,__subtree_last입니다. Span_iter는 private 두 node와 query 양끝,public 시작/끝 union과 is_hole을 갖습니다. Done은 is_hole==-1을 검사합니다. For_each_span은 first로 초기화하고 done이 아닌 동안 body를 실행한 뒤 next를 호출합니다.",
        "Is_hole1이면 hole field,0이면 used field를 읽고 done이면 새 span으로 사용하지 않습니다. Private node 상태를 임의로 바꾸지 않습니다. Node query는 개별 겹침 node,span query는 그 union과 빈 구간이라는 차이를 확인합니다.",
        "두 struct,anonymousunion,done 비교,for macro의세식을 읽으세요.",
        [("개별 node가[2,5],[4,8]이면 usedspan은?", "[2,8]의 합쳐진범위이다", "반드시두 nodepointer를 그대로출력한다", "Spaniterator는 겹친 node들을 연속 used로합칩니다. Nodeiterator와반환형태가다릅니다."),
         ("For_each_span body는 done=-1에서 실행되는 가?", "Done 검사로종료하여실행되지않는 다", "Is_hole의음수값을 used로보고계속실행한다", "Macro의 조건은!interval_tree_span_iter_done입니다. 종료상태와출력 span 상태를 구분합니다.")],
        [('선언과 구현', "Header는 insert/remove/iter_first/iter_next와 spanfirst/advance/next의선언을 제공합니다. Generictemplate가 nodequery를 만들고 lib의 CONFIGspan부분이범위분류를 구현합니다."),
         ('수명과 동기화', "Rbtree연결과 privatecursor는 iterator가진행하는 동안유효해야합니다. 이자료표현이나순회 macro가 caller의락·RCU등보호를 자동대신하는 것은 아닙니다.")])
