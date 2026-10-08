"""All plist implementation/debug functions and header representation contracts."""
def register(topic, q, detail):
    def lesson(title, path, symbol, why, principle, use, reading, qa, cards):
        topic(title, '자료구조·알고리즘', path, symbol, why,
              principle, use, reading, *(q(*x) for x in qa),
              details=[detail(*x) for x in cards])

    lesson('Plist 삽입·두 Tier와 양쪽 우선순위 탐색', 'lib/plist.c', 'plist_add',
        '모든 node의 순서와 서로 다른 우선순위 대표의 순서를 따로 유지하여 삽입 후보를 찾는 원리를 배웁니다.',
        'Node_list는 모든 node를 prio 숫자가 작은 순서로 연결하고 같은 prio는 FIFO입니다. Prio_list는 서로 다른 prio의 대표들을 연결한 ring입니다. Plist_add는 앞 iter와 뒤 reverse_iter를 비교하여 새 prio의 삽입 위치를 찾습니다. 새 prio이면 대표 ring에도 연결하고 실제 node는 다음 prio 그룹 앞 또는 전체 tail에 넣습니다.',
        "Init한 비소속 node를 넣고 caller가 접근 잠금을 유지합니다. 숫자가 작을 수록 높은 우선순위라는 plist 정책을 사용합니다. Node가 이미 연결되어 있거나 prio를 연결 중 임의 변경한 경우를 올바른 입력으로 취급하지 않습니다.",
        "First/last 대표,양방향 비교,node_next,대표 삽입과 node 삽입을 읽으세요.",
        [("Prio10,21,40이 있을 때 새 prio21은 어디로 가는 가?", "기존 21 그룹의 끝이며 40 앞이다", "같은 prio의 기존 node보다항상먼저이다", "동순위는 FIFO입니다. 다음 우선순위 그룹 앞에 새 node를 넣어 기존 21 항목 뒤를 유지합니다."),
         ("새 node가기존 prio와같으면대표 ring에새대표를 추가하는 가?", "동일 prio 대표를 중복추가하지 않는 다", "모든 node를 항상대표 ring에추가한다", "Prev의 prio가 같으면 prio_list삽입을 하지 않습니다. 모든 node를 가진 node_list와 distinct-prio 대표 ring의 역할이다릅니다.")],
        [('한 종류의 Prio', '대표 ring에 원소가 하나면 그 prio_list는 self link라 list_empty처럼 보입니다. Node_list의 첫 node가 대표 시작점 역할을 하므로 prio_list의 empty만으로 모든 대표 의미를 판단하지 않습니다.'),
         ('검색 비용', 'Distinct priority 수 K에 따른 탐색이며 양쪽 비교로 양 끝에 가까운 삽입을 빠르게 찾을 수 있습니다. 모든 원소 수 N을 같은 비용으로 단순 확대하지 않으며 최악 O(K)입니다.')])

    lesson('Plist 삭제·대표를 다음 동순위에 넘기기', 'lib/plist.c', 'plist_del',
        '우선순위 대표 node가 사라져도 같은 우선순위의 나머지 node를 대표 ring에 유지하는 방법을 배웁니다.',
        "Node의 prio_list가 비 empty이면 대표 ring에 연결된 경우입니다. Node_list의 다음이 head가 아니고 그 다음 node의 prio_list가 empty이면 그 link를 현재 대표 뒤에 넣어 대표 자리를 넘깁니다. 이후 현재 prio_list와 node_list를 list_del_init으로 제거합니다. 다음이 다른 대표이면 별도 승격을 하지 않습니다.",
        '실제로 해당 head에 연결된 node를 삭제하고 caller가 동기화를 제공합니다. 마지막 node와 마지막 prio 그룹, 한 prio만 있는 ring의 self 표현을 구분합니다. 삭제된 link의 self 초기화와 데이터 객체의 실제 해제는 다른 작업입니다.',
        "대표 link 검사,next head guard,next prio_list 승격,두 del_init을 읽으세요.",
        [("같은 prio의 첫대표를 삭제하고동순위다음 node가있으면?", "다음 node의대표 link를 승격할 수있다", "그우선순위그룹의 모든 node를 삭제한다", "현재대표뒤에 다음 node의 prio_list를 연결한뒤현재대표를 제거하여나머지그룹의대표를 유지합니다."),
         ("List_del_init은 자료 object를 free하는 가?", "연결제거와 link 초기화를 한다", "항상 object전체를 allocator에반환한다", "Plist_del은 listlink를 분리합니다. 원본에는 kfree가없고바깥자료 object의 수명은 caller가관리합니다.")],
        [('다음 대표', '다음 node가 다른 우선순위의 대표이면 prio_list가 이미 연결되어 있으므로 승격 조건을 통과하지 않습니다. 해당 그룹 전체가 없어지는 경우와 같은 그룹의 대표 교체를 나눠 봅니다.'),
         ('O(1) 제거', '삭제 위치를 알고 있고 연결이 올바르면 이웃 pointer만 갱신합니다. Key 검색 비용이나 caller의 lock 대기 비용까지 모두 상수라고 보장하는 뜻은 아닙니다.')])

    lesson('Plist Requeue·동순위 끝으로 이동', 'lib/plist.c', 'plist_requeue',
        "우선순위 값은 유지하면 서 같은 순위의 순서를 회전시키는 최적화된 재배치 원리를 배웁니다.",
        "Plist_requeue는 head와 node가 비어 있으면 BUG 조건입니다. 전체 마지막 node이거나 바로 다음의 prio가 다르면 이미 그룹 끝이므로 그대로 반환합니다. 같은 prio가 뒤에 있으면 node를 del한 뒤 기존 그룹을 이어 순회하여 다음 prio 경계 또는 전체 tail 앞에 node_list만 넣습니다.",
        "연결된 node에 대해 caller lock 아래 사용합니다. Prio를 바꾸는 API가 아니라 같은 prio 안의 마지막으로 옮기는 API입니다. 삭제 과정이 대표를 넘기므로 다시 삽입한 node를 동일 prio의 중복 대표로 추가하지 않습니다.",
        '두 no-op 조건,plist_del,continue iterator,node_list 재삽입을 읽으세요.',
        [("동순위 A,B,C에서 A를 requeue하면?", 'B,C,A이다', "A의 prio 값을 가장낮게바꾼다", "같은 우선순위의 끝으로 연결만옮깁니다. 우선순위숫자를 수정하는 대입은 없습니다."),
         ("Node다음의 prio가다르면 requeue는?", "이미그룹끝이라그대로 반환한다", "반드시전체 list의 끝으로 옮긴다", "다음 node와 prio가다르면현재 node는 동순위끝입니다. 다른 우선순위그룹을 넘겨순서를 깨지않습니다.")],
        [('같은 순위 공정성', '재배치로 동일 그룹에서 먼저 처리한 node를 뒤로 보낼 수 있습니다. 어떤 작업에 공정성을 제공할지는 이 자료구조를 사용하는 정책과 실행 경로에 달려 있습니다.'),
         ('실패 계약', 'BUG 조건은 일반 사용자 입력의 반환 오류가 아닙니다. 비어 있거나 연결되지 않은 node를 넘기는 것은 API 전제 위반이며 caller가 예방해야 합니다.')])

    lesson('Plist DEBUG·Prev Next 연결 검사', 'lib/plist.c', 'plist_check_list',
        "이중 연결 리스트의 두 방향이 일치하는 지 확인하는 진단과 동기화의 차이를 배웁니다.",
        "DEBUG_PLIST의 plist_check_prev_next는 n->prev==p와 p->next==n을 확인해 어긋나면 WARN합니다. Check_list는 top에서 원형 list를 따라가며 같은 관계를 검사합니다. Check_head는 비어 있지 않으면 첫 대표의 prio_list와전체 node_list를 검사합니다. DEBUG가꺼진경로는 check_head가 no-op macro입니다.",
        "진단을 올바른자료구조와잠금문맥에서 사용합니다. 검사자체가 concurrent writer를 차단하거나 pointer를 복구하는 lock은 아닙니다. WRITE_ONCE로 localcursor를 갱신하는 부분을 sharedlist동기화획득으로 해석하지 않습니다.",
        "두방향 equality,WARN,circular 종료,DEBUG/no-op 분기를 읽으세요.",
        [("N의 prev가 P인데 P의 next가다른 node이면?", "DEBUG연결검사에서 경고조건이다", '한방향만맞으면항상정상이다', "원본은 두방향의일치를 함께검사합니다. 이중 list의이웃관계가서로맞아야합니다."),
         ("DEBUG 검사가 list의 동시수정을 잠그는 가?", "별도잠금을 획득하지 않는 다", "자동으로 globalmutex를 잡는 다", "검사 body에는 lock획득이없습니다. 자료구조진단과 caller동기화는 구분해야합니다.")],
        [('범위', '이 검사들은 주로 prev/next의 연결을 봅니다. 모든 priority 정책이나 object 수명 오류를 한 번에 증명하는 validator가 아닙니다.'),
         ('잘못된 Chain', '잘못된 연결은 warning 이후에도 순회를 깨거나 정상 종료를 막을 수 있습니다. 진단 함수에 임의 invalid pointer를 안전하게 처리하는 복구 계약을 기대하지 않습니다.')])

    lesson('Plist Test 불변식·개수 대표 Ring와순서', 'lib/plist.c', 'plist_test_check',
        '자료구조 시험에서 node 개수·우선순위·대표 연결을 서로 다른 불변식으로 확인하는 방법을 배웁니다.',
        "Plist_test_check는 빈 head이면 예상 개수 0을 요구합니다. Node_list를 순회하며 nr_expect를 감소시키고같은 prio의후속 node는 대표 link가 empty인지확인합니다. 다른 prio로넘어갈때숫자가비감소인지와현재대표의 next가다음대표인지확인합니다. 끝에서 는 남은 개수 0과마지막대표가첫대표로돌아오는 ring을 검사합니다.",
        "완성된연결만눈으로 보지않고개수·순서·대표유일성·ring닫힘을 각각검사합니다. 실제 DEBUGtest의 범위와 productionAPI의입력조건을 구분합니다. Runtime invariant 확인을 kernel의 모든 concurrent상황에대한형식증명으로 표시하지 않습니다.",
        "예상개수감소,같은 prio 분기,다른 대표 next,마지막 ring 조건을 읽으세요.",
        [("모든 node 순서는 맞지만대표 ring의마지막 next가틀리면?", "마지막 ring닫힘검사에서 실패한다", "Node 정렬만맞으면모든 검사를 통과한다", "원본은 prio_pos->prio_list.next가 first->prio_list인지별도로 검사합니다. Node 순서와대표 ring은 각각불변식입니다."),
         ("동순위후속 node에도대표 link가있으면?", '대표유일성조건위반이다', "같은 prio 대표가많을 수록항상정상이다", "같은 prio구간의후속 node는 prio_list가 empty여야합니다. Distinctpriority 대표만 ring에 두는 구조입니다.")],
        [('첫 Node', "첫 node는 대표 ring의기준입구입니다. 빈 list와한 prio만있는 selfring의특별표현을 각각처리해야합니다."),
         ('Requeue 시험', "Plist_test_requeue는 requeue 뒤전체마지막이아니면다음 node의 prio가다른 지확인합니다. 같은 prio 끝으로 갔다는 조건을 직접관찰하는 시험입니다.")])

    lesson('Plist Test 실행·결정적 입력과시간측정 범위', 'lib/plist.c', 'plist_test',
        "커널 안의 자료구조 self-test가 무작위처럼 보이는 입력과 별도 측정을 어떻게 구성하는 지 배웁니다.",
        "DEBUG_PLIST의 plist_test는 241개 test_node를 init하고 local_clock seed에서 r=r*193939%47629를 반복하여 1000회삽입·삭제를 선택합니다. 삽입 node는 prio r%99이고매회개수·대표불변식을 검사한뒤 requeue도시험합니다. 남은 node를 제거한후별도 241개증가 prio삽입의 ktime차이를 합해 debuglog로출력하고 module_init에서 등록합니다.",
        "Seed·입력·불변식·측정을 구분하여시험을 재현합니다. 주석의 worst case이름이현재양방향삽입의 모든 입력최악비용을 증명하지는 않습니다. Host의모의 clock으로 원본 test를 실행하면 실제 kernel성능측정으로 표시하지 않습니다.",
        "241개배열,1000loop,r 갱신,정리,ktime 계산,module_init을 읽으세요.",
        [("R%99와 241개증가 prio측정은 같은 입력분포인가?", "별도시험의서로다른 입력이다", "두단계가항상 0..98만사용한다", "처음은 r%99이고측정단계는 test_data[i]=i로 0..240입니다. 서로다른 목적으로 구성된입력을 구분합니다."),
         ("모의 clock에서 얻은 elapsed를 kernel성능값으로 써도되는 가?", '실제성능측정과구분해야한다', "원본 body를 썼으므로항상실제 kernel시간이다", "Clock과실행환경이모의라면제어흐름검증입니다. 원본함수복사가실제 hardware·kernel성능을 재현하지 않습니다.")],
        [('적절한 단위', "Node처리결과와각단계불변식은 정확성증거입니다. 시간이얼마나드는 지는 CPU·cache·lock·clock·입력분포를 고정한별도측정이 필요합니다."),
         ('원본의 숫자', "Header의 RTprioritylevel 설명에 99가나오지만 struct의 prio는 int이고별도측정은 241개의서로다른 값을 씁니다. 모든 genericplist가 99종류만허용하는 hardlimit으로 읽지않습니다.")])

    lesson('Plist 초기화·Head와두 Link의Self 표현', 'include/linux/plist.h', 'plist_node_init',
        '정렬 list를 쓰기 전에 head와 node의 두 연결 필드를 올바른 빈 상태로 만드는 방법을 배웁니다.',
        "Plist_head는 node_list하나이고 plist_node는 int prio와 prio_list/node_list두 link를 갖습니다. Head_init은 head의 node_list를 selfring으로, node_init은 prio를 설정하고두 link를 각각 selfring으로 만듭니다. PLIST_HEAD_INIT/HEAD와 PLIST_NODE_INIT은 같은 정적표현을 제공합니다. Node_empty는 node_list의 self여부를 봅니다.",
        "Head와 node를 init한뒤 add합니다. Prio_list와 node_list의 empty 검사역할을 나눠보고바깥 dataobject 안에 plist_node를 embedding할 수있습니다. 초기화가이미연결된 sharednode의안전한제거를 대신하지 않습니다.",
        "Struct정의,정적 macro,두 INIT_LIST_HEAD,head/node empty를 읽으세요.",
        [("Plist node가갖는 연결필드는 몇개인가?", "대표용과전체 node용두 개이다", "단일 nextpointer하나뿐이다", "Prio_list는 대표 ring,node_list는 전체순서를 위한 list_head입니다. 같은 node 안의 두연결이서로다른 역할을 합니다."),
         ("Node_init이 head에자동삽입하는 가?", "두 link를 self로초기화할뿐이다", "초기화즉시모든 head에 연결된다", "Init에는 head인자가없고연결 field를 빈표현으로 만듭니다. 실제삽입은 plist_add입니다.")],
        [('Type Header', "Include/linux/plist_types.h는 이두 struct의저장 field정의를 분리해제공합니다. 알고리즘 body와자료표현을 따로나눠포함할 수있습니다."),
         ('우선순위 값', "작은 int가높은 우선순위입니다. INT_MIN에서 INT_MAX까지의정수정책과해당호출자가사용하는 priority 범위를 구분합니다.")])

    lesson('Plist 접근자·First Last와비어있지않은전제', 'include/linux/plist.h', 'plist_first',
        '정렬 list의 양 끝 object를 찾는 container 변환과 empty guard의 책임을 배웁니다.',
        "Plist_first는 head->node_list.next를 plist_node로변환하여가장작은 prio의 node를 반환하고 last는 prev를 변환하여가장큰 prio를 반환합니다. Next/prev macro는 node_list의이웃입니다. First_entry/last_entry는 plist_node를 바깥자료 object로다시 container변환합니다. DEBUGentrymacro는 empty이면 WARN하지만안전한 NULL 반환을 새로만들지않습니다.",
        "먼저 head가비어 있지 않은 지확인합니다. Sentinelhead를 실제 node처럼 dereference하지 않습니다. DEBUGwarning이 API전제를 자동복구한다고가정하지 않으며정확한 outertype/member를 사용합니다.",
        "Next/prev field,container 변환,DEBUG WARN 뒤계산을 읽으세요.",
        [("비어 있는 head에서 first를 무조건 object로사용해도되는 가?", "비어 있지 않은 전제를 먼저확인해야한다", "DEBUG가항상 NULL을 반환하므로괜찮다", "Accessor는 sentinel의이웃주소를 container로변환합니다. 원본은 아래함수들이비 empty를 가정한다고명시합니다."),
         ("First와 last의우선순위정책은?", "First가작은 숫자의 높은 우선순위이다", "숫자가클수록항상 first로간다", "Header정책은 INT_MIN쪽이높고 INT_MAX쪽이낮습니다. 구조체숫자 방향과사용정책을 같이읽습니다.")],
        [('두 단계 Container', "Node_list link→plist_node→바깥 object의 순서로주소를 계산합니다. 자료 객체 embedding과순서 link를 혼동하지 않습니다."),
         ('경계의 Sentinel', "Next/prev는 끝에서 head를 표현하는 가상 container를 만들수있습니다. Iterator의종료검사또는 명시적경계조건을 넘어그값을 자료 node로 읽지않습니다.")])

    lesson('Plist 순회·Continue Safe와Caller Lock', 'include/linux/plist.h', 'plist_for_each_safe',
        '정렬 list의 순회 macro를 현재 위치·삭제 가능성·자료 object 타입에 맞춰 사용하는 방법을 배웁니다.',
        "Plist_for_each는 node_list의 list_for_each_entry에 연결됩니다. Continue는 현재 pos 뒤부터,Safe는 다음 node를 미리저장하여현재 node의제거에대비합니다. For_each_entry계열은 바깥 object 안의 mem.node_list를 member로사용합니다. Header는 No locking is done,up to caller라고명시하여순회와수정의동기화를 호출자에게둡니다.",
        "Currentnode를 삭제할 때 safevariant와적절한 listlock을 사용합니다. Safe는 다음 pointer 저장규약이며동시 writer와 object해제의 모든 경쟁을 없애지않습니다. Priority 변경은 필요한보호아래 del→prio 변경→add로정렬불변식을 유지합니다.",
        "기본/continue/safe와 outerentrymacro의 member경로를 비교하세요.",
        [("Continue macro는 현재 node를 다시방문하는 가?", "현재위치뒤에서 이어간다", "항상 head처음으로 돌아가다시시작한다", "Underlyinglist_for_each_entry_continue의계약을 사용합니다. Requeue에서 도현재그룹뒤를 이어찾습니다."),
         ("Safe 순회가잠금을 자동획득하는 가?", "Lock은 caller의책임이다", "Safe라는 이름으로 globalmutex를 획득한다", "Header의명시적인 No locking 규약이적용됩니다. 다음 node 저장과 sharedlist 접근보호는 별개입니다.")],
        [('삭제와 순서', "현재 node를 제거한뒤에도미리보관한다음 node를 사용할 수있어반복을 계속합니다. 그다음 node의 수명까지자동참조획득하는 것은 아닙니다."),
         ('Priority 변경', "연결된 node의 prio만바꾸면정렬순서와대표 ring의관계가어긋납니다. 값을 바꾸는 작업과연결구조유지를 함께수행해야합니다.")])
