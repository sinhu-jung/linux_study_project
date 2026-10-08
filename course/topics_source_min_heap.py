"""All min_heap.h storage macros, callbacks and nine internal operations."""
def register(topic, q, detail):
    def lesson(title, symbol, why, principle, use, reading, qa, cards):
        topic(title, '자료구조·알고리즘', 'include/linux/min_heap.h', symbol,
              why, principle, use, reading, *(q(*x) for x in qa),
              details=[detail(*x) for x in cards])

    lesson('Min Heap 저장·배열과 사용자 Callback', '__min_heap_init',
        '작은 원소를 빠르게 꺼내는 heap을 배열과 비교·교환 callback으로 표현하는 방법을 배웁니다.',
        "MIN_HEAP_PREALLOCATED는 nr,size,data와 정적 preallocated 배열을 선언합니다. DEFINE_MIN_HEAP은 그 배열 길이를 0으로 둡니다. Init은 nr0과 capacity size를 설정하고 외부 data가 있으면 사용하며 없으면 preallocated를 선택합니다. Callback의 less는 순서 비교,swp는 두 원소 교환이며 args를 함께 전달받습니다.",
        '실제 storage에 맞는 capacity와 원소 type·alignment를 제공합니다. 이 API는 allocation을 대신하지 않습니다. Less는 일관된 순서를 정의하고 swp는 원소 전체를 올바르게 교환합니다. Caller가 공유 heap의 동기화와 저장 수명을 관리합니다.',
        'Struct macro,external/fallback storage,callback signature,typed wrapper를 읽으세요.',
        [("외부 data가 NULL이면 init이 malloc하는 가?", 'Preallocated 배열 위치를 선택한다', "언제나 size만큼동적 allocation한다", "원본에는 allocator 호출이없습니다. Capacity와실제 preallocated 저장길이를 caller가맞춰야합니다."),
         ("Heap callback의 args는 어디에쓰이는 가?", "Less와 swp에사용자문맥으로 전달된다", '항상원소개수로강제해석된다', "각 algorithm은 args를 opaque문맥으로 callback에넘깁니다. 그뜻은 caller의 callback설계에 달려있습니다.")],
        [('C Macro', "__minheap_obj_size는 data[0]의 sizeof이고 cast는 typeof(data[0])pointer입니다. Wrapper는 typed heap을 공통 min_heap_char 표현으로 넘깁니다. Dataobject와공통 prefixlayout 조건을 읽습니다."),
         ('저장 전제', "Fallback은 공통 charheap의 preallocated주소로계산됩니다. 임의 over-alignedtype이나큰 capacity를 자동검사·확보하는 API로설명하지 않습니다. Externalbuffer도충분한공간과 alignment가 필요합니다.")])

    lesson('Min Heap 조회·Peek와 Capacity 조건', '__min_heap_peek',
        "전체 배열이 정렬되지 않아도 최소 원소가 root에 있다는 불변식과 빈 상태의 반환을 배웁니다.",
        "Peek는 nr가있으면 data의 첫 원소 pointer,없으면 NULL을 반환합니다. Full은 nr==size입니다. Typedmacro는 peek 결과를 data 원소 type pointer로변환합니다. Heap불변식은 각 parent가 child보다크지않다는 것이며인접한배열전체의정렬을 요구하지 않습니다.",
        "Nr와 size가 0<=nr<=size로유지되고실제 storage에맞는 전제를 지킵니다. Peekpointer는 내부 storage를 가리키므로후속 push/pop/swap으로 그내용이바뀔수있습니다. 최소원소의복사와수명·잠금조건을 확인합니다.",
        "Nr ternary,data 첫주소,full equality와 cast를 읽으세요.",
        [("Peek가최소원소를 꺼내면서 nr를 감소시키는 가?", "Pointer를 조회할뿐이다", "호출할 때마다최소원소를 삭제한다", "Peekbody에는 nr 변경이없습니다. 실제제거는 pop이고조회와구분합니다."),
         ("Heap배열의 모든 인접원소가정렬되어야하는 가?", "Parent-child 조건만필요하다", '항상배열전체가오름차순이어야한다', "최소 root와 subtreeheap 조건이핵심입니다. 형제또는 서로다른 branch의인접순서를 전부정렬할 필요는 없습니다.")],
        [('Full의 한계', "Full은 equality 검사입니다. 잘못된 nr>size를 정상상태로복구하지 않으며 push의>=guard와기존상태불변식을 함께읽습니다."),
         ('반환 수명', "Peek 결과는 새 allocation이나참조획득이아닙니다. 저장배열해제·이동·동시갱신뒤같은 pointer내용을 고정 snapshot으로 사용하지 않습니다.")])

    lesson('Min Heap Sift Down·Leaf 탐색후Backtrack', '__min_heap_sift_down',
        'Root 원소를 아래로 이동시킬 때 작은 child 경로를 먼저 찾고 알맞은 위치까지 되돌아오는 원리를 배웁니다.',
        "배열 index i의 child는 2i+1과 2i+2입니다. Sift_down은 더 작은 child를 선택하여 leaf까지내려가고마지막외동 child도처리합니다. Root가후보보다작으면 parent쪽으로 backtrack합니다. 최종위치 j를 고정하고그경로의 parent와 j를 차례로 swap하여 root를 맞는 위치로옮깁니다.",
        "Pos가유효하고그아래 subtree들이 heap인상황에서 root의 순서를 복구합니다. 전체임의배열을 한번의 sift로정렬한다고생각하지 않습니다. Callback 비교·교환과 intindex산술이유효한 storage크기를 caller가보장합니다.",
        "두 child 선택,외동 child,root 비교 backtrack,고정 j swap을 읽으세요.",
        [("Sift down의 첫단계는 어떤경로를 택하는 가?", "두 child중작은 쪽으로 leaf까지간다", "항상왼쪽 child만따라간다", "Less(left,right)에따라 child를 선택합니다. Equal이면 원본 조건상오른쪽을 선택할 수있습니다."),
         ("Backtrack에서 root가후보보다작으면?", "후보위치를 parent로올린다", "Root를 무조건가장깊은 leaf에둔다", "Root가더작다면그렇게깊이내려갈필요가없습니다. i=(i-1)/2로올라가맞는 위치를 찾습니다.")],
        [('배열 표현', "완전이진 tree를 pointernode없이배열로표현합니다. Parent=(i-1)/2와 child식으로 위치를 계산하며 element size가 byte주소계산에들어갑니다."),
         ('GNU C', "Voidpointer에 byteoffset을 더하는 표현은 이 header의 GNU C문맥입니다. 모든 표준 C컴파일러가 같은 확장을 지원한다고가정하지 않습니다.")])

    lesson('Min Heap Sift Up·Parent 비교와Equal 순서', '__min_heap_sift_up',
        "마지막에 넣은 작은 원소를 parent와교환하여위로올리고같은 key의 순서조건을 구분합니다.",
        "Idx가 0이 아닌동안 parent=(idx-1)/2를 계산합니다. Less(parent,child)가 true이면 끝내고그렇지않으면 swap후 idx=parent로반복합니다. Strictless 비교에서 equal은 true가아니므로 같은 key도 swap할 수있습니다. Heap의 순서조건을 복구하지만 stable 순서는 보장하지 않습니다.",
        "Idx의 원소를 제외한 heap 관계가유효한문맥에서 사용합니다. 같은 key의 FIFO가 필요하면 key에추가순번을 포함하는 등 callback정책을 구성합니다. 임의 node의 key 변경방향에맞는 sift와외부보호를 사용합니다.",
        "Parent 계산,strictless break,swap후 idx 갱신을 읽으세요.",
        [("Parent와 child가 같은 key이면 원본 sift up이반드시멈추는 가?", "Strictless가 false이면 swap할 수있다", "Equal 조건을 따로검사하여항상멈춘다", "Break 조건은 less(parent,child)하나입니다. Equalkey의삽입순서를 보존하는 별도조건은 없습니다."),
         ("새로운최솟값을 배열끝에넣은 뒤적절한방향은?", "Parent를 따라위로 sift한다", "항상끝원소를 그대로두어 root를 읽는 다", "작은 새 원소는 parent보다작을 수있어위로옮깁니다. Root최소조건이회복되어야 peek가최소를 반환합니다.")],
        [('O(log n)', "Parent로한 level씩올라가므로 tree높이에비례합니다. Callback자체의비용까지항상상수인지는 caller의구현에 달려있습니다."),
         ('자료 의미', "Swap은 자료원소를 옮기므로외부에서 index를 object의영구식별자로사용한다면별도갱신이 필요합니다. Heapposition과 objectidentity는 같지않습니다.")])

    lesson('Min Heapify·Floyd의아래쪽부터복구', '__min_heapify_all',
        '이미 채운 임의 배열을 원소별 push보다 효율적으로 heap으로 만드는 원리를 배웁니다.',
        "Heapify_all은 i=nr/2-1부터 0까지각 subtree를 sift_down합니다. Leaf는 child가없어이미 heap이고더낮은 internalnode부터복구하면 그위 node의 childsubtree가준비됩니다. 깊은 node가많지만이동거리가짧고높은 node가적어전체작업은 O(nr)입니다.",
        "저장배열과 nr를 유효범위에맞춰이미채운뒤사용합니다. Init만한 nr0heap에서 외부배열이자동으로 원소로계산되지않습니다. Heapify와전체정렬을 구분하고최소를 반복꺼내려면 pop을 사용합니다.",
        "Nr/2-1시작과감소 loop,각 sift_down 호출을 읽으세요.",
        [("Heapify가 leaf부터개별정렬을 할 필요가 없는 이유는?", "Child가 없는 leaf는 이미 heap이다", "Leaf는 원소가아니어서항상삭제된다", "Leafsubtree에는 한 원소만있어 parent-child위반이없습니다. 마지막 internalnode부터복구하면 됩니다."),
         ('Floydheapify전체비용은?', 'O(n)이다', "모든 node를 항상 root까지올려 O(n²)이다", "각 level의 node수와하강거리를 합하면 선형입니다. 반복 push의 O(n log n)과 다른 구성방법입니다.")],
        [('Nr0·1', "Nr/2-1은 음수라 loop가실행되지않습니다. 빈 heap과한 원소 heap은 추가복구가없습니다."),
         ('원소 개수', "Capacitysize와실제 nr는 다릅니다. 외부 data를 지정하는 init는 nr0으로 시작하므로이미채운배열의 heap화에서 는 실제 nr 설정도필요합니다.")])

    lesson('Min Heap Pop·마지막 원소로Root 채우기', '__min_heap_pop',
        '최소 원소 제거 후 빈 root 자리를 마지막 원소로 채우고 heap을 복구하는 원리를 배웁니다.',
        "Nr<=0이면 WARN_ONCE후 false입니다. 성공경로는 nr를 감소시키고기존마지막 원소를 data첫 위치에 memcpy한다음 sift_down합니다. Bool은 제거성공여부이며제거한값을 별도반환하지 않습니다. 마지막한 원소의 pop은 nr0이되고 sift는 더이상 child를 읽지않습니다.",
        "값이 필요하면 pop전에 peek 원소를 적절히복사합니다. Peekpointer만저장해두면 root가덮여원래최소값을 잃을 수있습니다. Caller가상태와 storage를 보호하고 element source/destination의 memcpy전제를 유지합니다.",
        "Emptyguard,nr 감소,마지막주소와 rootcopy,sift를 읽으세요.",
        [("Pop 반환 true가제거한정수값인가?", "제거성공 bool이다", '최소원소의수치값이다', "API 반환형은 bool이고 value 출력인자가없습니다. 제거값이 필요하면 사전에 peek내용을 읽습니다."),
         ("Pop후예전 peekpointer의내용은?", "마지막 원소와 sift 결과로바뀔수있다", "언제나제거전최소값으로 고정된다", "Peek는 내부 root주소입니다. Pop이그 storage를 덮으므로 pointer를 snapshot처럼사용하지 않습니다.")],
        [('복구 방향', "마지막 원소가 root로올라오면 child보다클수있어아래로복구합니다. 최소원소를 새배열에복사하며전체정렬하는 동작은 아닙니다."),
         ('빈 요청', "False경로는 nr와자료를 수정하지 않습니다. Warning은 진단이며호출자가빈 heap을 정상적으로 구분하도록반환도제공합니다.")])

    lesson('Min Heap Pop Push·개수 유지와한번의Sift', '__min_heap_pop_push',
        '최소를 제거한 자리에 새 원소를 바로 넣어 두 번의 heap 복구를 한 번으로 줄이는 원리를 배웁니다.',
        "Pop_push는 root에 element를 memcpy하고 sift_down한번만수행합니다. Nr를 바꾸지않고 pop/push의 두복구를 합칩니다. Emptyguard나 capacity 변경은 없으므로 기존 heap에 최소원소가 있는 caller전제를 필요로합니다. Element가최소보다작아도최소교체연산의뜻으로 처리합니다.",
        "비어 있지 않은 heap과유효 sourceobject를 제공합니다. Emptyheap에새 원소를 등록하는 push대용이아닙니다. Top-K등의정책에서 는 새 원소를 교체할지 caller가결정하고 source가 copy대상과부적절하게겹치지않게합니다.",
        "Rootmemcpy,변하지 않는 nr,한 sift와 guard부재를 읽으세요.",
        [("Pop_push의 nr는?", "기존개수를 유지한다", "항상 1 증가한다", "Body에는 nr 대입이없습니다. 기존최소를 새값으로 교체하는 연산이지빈공간에추가하는 push가아닙니다."),
         ("Emptyheap을 pop_push로초기화해도되는 가?", "Caller가비 empty전제를 지켜야한다", "자동 nr1이되어정상 push이다", "Rootstorage를 덮어도 nr는 0으로 남습니다. 함수에 empty처리나원소개수증가가없습니다.")],
        [('한 번의 복구', "별도 pop은 마지막 원소를 root로올리고하강복구,push는 끝에추가하고상승복구합니다. 직접 root 교체는 하강복구한 번으로 기존개수를 유지합니다."),
         ('정책과 도구', "새 key를 받아들일지거절할지는 자료구조바깥정책입니다. 이 함수는 조건부로작은 값을 유지하는 filter를 자동실행하지 않습니다.")])

    lesson('Min Heap Push·끝에추가후상승', '__min_heap_push',
        '배열 capacity 안에 새 원소를 복사하고 parent 경로에서 순서를 복구하는 방법을 배웁니다.',
        "Nr>=size이면 WARN_ONCE후 false입니다. 성공하면 pos=nr 위치에 element를 memcpy하고 nr를 증가시킨뒤 sift_up합니다. 저장공간확장이나 allocation은 없습니다. Wrapper는 typed data의 원소크기를 전달하여 byteoffset을 계산합니다.",
        "Init한 storage와올바른 capacity,element source의 폭과수명을 제공합니다. Full실패를 검사하고필요하면 caller가외부저장정책을 결정합니다. Capacity만크게고쳐실제 buffer밖에 push하지 않습니다.",
        ">=guard,pos/nr 순서,copy크기,sift_up을 읽으세요.",
        [("Fullheap에 push하면 원본은 storage를 확장하는 가?", "False로거절하고확장하지 않는 다", "자동 realloc으로 capacity를 늘린다", "원본에는 allocation이없고 guard에서 반환합니다. 실제 storage의관리는 caller책임입니다."),
         ("Push가처음복사하는 배열위치는?", "기존 nr인끝위치이다", "항상 root0에 기존최소를 덮는 다", "Pos=heap->nr로정한뒤 copy하고 nr를 증가시킵니다. 이후 sift_up이 필요한경로로새 원소를 옮깁니다.")],
        [('원소 복사', "원소가 pointertype이면 pointer 값을 복사할뿐 pointee의자동복제나참조카운트획득을 하지 않습니다. Callback과자료수명정책을 같이설계합니다."),
         ('한 원소', "빈 heap에첫 push는 pos0이고 sift_up의 idx0이라 swap없습니다. Root가그원소이며 nr1이됩니다.")])

    lesson('Min Heap Del·임의위치와양방향복구', '__min_heap_del',
        '배열 중간 원소를 제거하고 마지막 원소로 채울 때 위와 아래의 순서 위반을 모두 처리합니다.',
        "Del은 nr<=0이면 false입니다. Nr를 감소시키고 idx가이제 nr와같으면원래마지막 원소의삭제라즉시성공합니다. 나머지는 idx와기존마지막위치를 swap하고 idx의 sift_up다음 sift_down을 수행합니다. Body에는 idx<원래 nr 범위의명시적 guard가없으므로 caller가유효 idx를 제공합니다.",
        "존재하는 index만넘기고삭제 후 index가그 object의영구위치가아님을 확인합니다. Emptyguard를 임의 out-of-rangeindex보호로 해석하지 않습니다. Swapcallback과외부참조정책을 같이관리합니다.",
        "Nr 감소,마지막 idx특별경로,swap,up→down과 idxguard부재를 읽으세요.",
        [("삭제 idx가원래마지막위치이면?", "Nr 감소후추가 swap없이성공한다", "반드시범위밖새 원소를 읽는 다", "Idx==감소한 nr 조건이마지막삭제를 특별처리합니다. 남은 자료에빈구멍을 채울필요가없습니다."),
         ("Del이모든 잘못된 idx를 검사하는 가?", "Caller가 idx 범위를 보장해야한다", "Emptyguard만으로 모든 큰 idx도안전하다", "Body의 guard는 nr<=0입니다. 비 empty 상태의 out-of-rangeidx를 일반적으로 차단하는 분기는 없습니다.")],
        [('두 방향', "마지막 원소가중간자리에오면 parent보다작거나 child보다클수있습니다. Up과 down복구를 연결하여남은 heap 조건을 유지합니다."),
         ('값의 수명', "Removedobject를 free하거나참조를 반납하는 API는 없습니다. 자료원소의소유권정책과삭제성공 후정리작업은 caller가관리합니다.")])
