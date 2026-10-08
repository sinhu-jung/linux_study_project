"""Detailed generic library algorithms from the fixed v6.12 source."""
def register(topic,q,detail):
    topic('Union-Find·경로 압축과 Rank','자료구조·알고리즘','lib/union_find.c','uf_find',
      '항목들이 같은 집합에 속하는지 반복 확인하고 집합을 합치는 문제에 빠른 자료구조가 필요합니다.',
      '각 노드는 parent를 가지며 root의 parent는 자기 자신입니다. Find는 parent를 따라 root를 찾으며 경로를 짧게 만듭니다. Union은 root의 rank를 비교해 낮은 쪽을 높은 쪽에 붙이고 같을 때만 새 root rank를 증가시킵니다. v6.12 find는 조부모로 parent를 바꾸면서 원래 parent로 진행합니다.',
      '각 노드를 자기 parent·초기 rank 0으로 준비하고 uf_find·uf_union으로 집합을 관리합니다. 연결 관계 판정에 쓰되 집합 분리는 같은 구조로 바로 처리되지 않습니다. 동시 변경은 별도 동기화가 필요합니다.',
      'uf_find 전체 while와 uf_union의 같은 root·작은 rank·같은 rank 세 경로를 읽으세요.',
      q('Rank 2와 Rank 4의 서로 다른 root를 합치면 어느 쪽을 붙이는가?','Rank 2 root를 Rank 4 root에 붙인다','Rank 4를 Rank 2에 붙이고 두 rank를 모두 올린다','낮은 rank를 높은 쪽에 연결해 트리가 깊어지는 것을 줄입니다. Rank가 다를 때 높은 root rank는 그대로입니다.'),
      q('같은 root를 가진 두 노드를 union하면 rank는 어떻게 되는가?','같은 집합이므로 바로 반환하고 증가하지 않는다','같은 root도 매번 rank가 두 배가 된다','uf_union의 첫 root 비교가 참이면 return입니다. 같은 집합을 반복 합친다고 깊이 정보가 늘지는 않습니다.'),
      details=[detail('Find를 한 줄씩 읽기','while(node->parent!=node)는 root에 도착할 때까지입니다. parent=node->parent로 기존 부모를 보관합니다. node->parent=parent->parent는 현재 노드를 조부모에 연결합니다. node=parent는 보관한 기존 부모로 이동합니다. 루프 뒤 root를 반환합니다.'),detail('경로 압축 예','A→B→C→C에서 find(A)는 A.parent를 C로 바꾸고 B로 이동합니다. B는 C에 연결된 채 C로 진행해 root C를 반환합니다. 이후 A의 root 탐색 경로는 A→C로 짧아집니다.'),detail('Union을 한 줄씩 읽기','root1·root2를 find로 얻습니다. 같으면 이미 한 집합입니다. rank가 작으면 그 root의 parent를 큰 쪽으로 바꿉니다. 같으면 root2를 root1에 붙이고 root1.rank++합니다. Rank는 매 호출마다 실제 높이를 다시 세는 값이 아닙니다.'),detail('복잡도와 한계','Rank 연결과 경로 압축 계열은 반복 연산에서 매우 작은 상각 비용을 제공합니다. Parent pointer의 수명과 동시 쓰기는 이 함수들 자체가 lock으로 보호하지 않습니다. 빠른 집합 판정이 임의 삭제·분할까지 해결하는 것은 아닙니다.')])

    topic('KMP·실패 함수와 선형 검색','자료구조·알고리즘','lib/ts_kmp.c','kmp_find',
      '문자열에서 패턴이 부분 일치하다 실패할 때 이미 비교한 정보를 재사용하면 중복 비교를 줄일 수 있습니다.',
      'KMP의 prefix table은 패턴 각 접두 구간에서 가장 긴 proper prefix이면서 suffix인 길이를 기록합니다. 불일치하면 q를 prefix[q-1]로 줄이고 같은 입력 문자를 다시 검사합니다. 텍스트 블록 사이에도 q를 유지해 조각 경계에 걸친 일치를 찾을 수 있습니다.',
      'textsearch_prepare로 kmp 패턴을 준비하고 block 공급과 state offset 규약을 따릅니다. 대소문자 옵션·패턴 길이·반환 UINT_MAX·다음 탐색 offset을 확인합니다.',
      'kmp_find의 q·prefix_tbl[q-1]와 get_next_block 반복 바깥 q 선언을 읽으세요.',
      q('패턴 ABAB의 prefix table은?','0,0,1,2','0,1,2,3','A는 proper prefix가 없고 AB도 없습니다. ABA의 A는 길이 1, ABAB의 AB는 길이 2로 양끝에서 같습니다.'),
      q('텍스트 블록 끝에서 패턴이 일부 일치했다면 KMP가 q를 유지하는 이유는?','다음 블록에 이어지는 패턴을 검사하기 위해','모든 블록을 독립 파일로 처리하기 위해','q는 외부 루프 전에 선언되어 블록 공급이 바뀌어도 부분 일치 길이를 유지합니다. 조각 경계를 건너는 일치를 찾을 수 있습니다.'),
      details=[detail('실패 때 재사용','패턴 ABABAC에 ABABA까지 맞다가 입력 B를 보았다면 현재 q와 prefix table로 더 짧은 유효 prefix를 찾습니다. 처음부터 이전 텍스트를 전부 다시 비교하지 않습니다.'),detail('반환 위치','소스는 일치 끝 offset을 consumed+i+1로 저장하고 pattern_len을 빼 시작 위치를 반환합니다. 길이와 위치, 다음 검색의 state offset을 구분해야 off-by-one을 피합니다.')])

    topic('Boyer-Moore·뒤에서 비교와 건너뛰기','자료구조·알고리즘','lib/ts_bm.c','bm_find',
      '패턴 끝에서 불일치한 정보를 활용하면 텍스트 위치를 한 칸씩 옮기지 않고 여러 칸 건너뛸 수 있습니다.',
      'BM은 패턴 뒤쪽부터 비교하고 bad-character·good-suffix 표로 다음 정렬 위치를 정합니다. Linux v6.12 ts_bm은 공급받은 블록 안에서 검색하므로 여러 블록에 걸친 일치를 놓칠 수 있습니다. 모든 형태의 스트림에서 KMP와 같은 탐색 계약이라고 가정할 수 없습니다.',
      'textsearch의 bm을 선택할 때 조각 경계의 일치 허용 조건을 확인합니다. 보안 필터처럼 놓치면 안 되는 조각 간 탐색에는 이 구현의 제약을 고려해 KMP 등의 적합한 방식을 선택합니다.',
      'bm_find의 matchpat·bad_shift·good_shift와 파일 첫 block 경계 경고를 읽으세요.',
      q('패턴 ABC가 텍스트 조각 AB와 C로 나뉘면 이 Linux BM 구현은 반드시 찾는가?','블록 경계 일치를 놓칠 수 있다','모든 조각에 대해 항상 찾는다','파일 주석이 오른쪽부터 블록별 비교하므로 여러 블록에 걸친 일치를 놓칠 수 있다고 명시합니다. 알고리즘 이름만으로 계약을 추정하지 않습니다.'),
      q('BM의 bad-character 표는 어떤 정보를 활용하는가?','불일치 문자의 패턴 내 위치','파일 시스템 inode 수','텍스트의 불일치 문자가 패턴 어느 위치에 있는지 활용해 정렬을 건너뜁니다. Good-suffix 규칙도 함께 고려합니다.'),
      details=[detail('오른쪽 비교','matchpat은 text-i와 pattern-i를 비교합니다. 끝에서 맞은 suffix 길이 i를 얻고 두 이동 후보 중 큰 값을 사용합니다. 각 규칙의 전처리가 틀리면 유효 일치를 건너뛸 수 있습니다.'),detail('Bad-character 예','패턴 ABC의 끝 C와 텍스트 끝 X가 다르고 X가 패턴에 없다면 그 정렬의 여러 위치를 건너뛸 수 있습니다. 실제 이동은 이전 suffix 일치와 good_shift까지 반영합니다.')])

    topic('Genalloc·일반 주소 풀과 비트맵 할당','자료구조·알고리즘','lib/genalloc.c','gen_pool_alloc_algo_owner',
      '일반 RAM allocator가 아닌 장치 메모리나 정해진 주소 범위에서도 작은 조각을 할당할 수 있어야 합니다.',
      'Genpool은 등록 chunk의 주소 범위를 최소 단위의 비트맵으로 표현합니다. 크기를 단위 수로 올림하고 first-fit·best-fit 등 선택 알고리즘으로 연속 빈 bit를 찾습니다. 동시 bit 획득의 실패는 재시도하며 반환 주소의 의미는 등록한 pool 자원에 따릅니다.',
      'gen_pool_create→add→alloc→free→destroy 수명을 따릅니다. Min alloc order·주소 단위·실패 반환·동시성 문맥을 확인합니다. 반환값을 모든 장치의 DMA 주소로 곧바로 취급하지 않습니다.',
      'gen_pool_alloc_algo_owner의 nbits 올림식·chunk avail·algo·bit set 재시도를 읽으세요.',
      q('min_alloc_order=4인 pool에서 33바이트 요청은 몇 단위를 요구하는가?','3단위','2단위','단위는 2^4=16바이트이고 ceil(33/16)=3입니다. 48바이트 공간을 확보해야 요청을 담습니다.'),
      q('Genpool 주소가 어떤 주소 공간인지 판단할 기준은?','등록한 chunk와 pool의 자원 규약','항상 모든 CPU·장치에서 같은 가상 주소','Pool은 여러 종류의 주소 범위를 관리할 수 있습니다. CPU 가상·물리·장치 주소의 변환 규약을 따로 확인합니다.'),
      details=[detail('선택 정책','First-fit은 먼저 맞는 범위를, best-fit은 요청에 가까운 빈 범위를 찾습니다. 검색 비용과 남는 조각 형태가 다릅니다. 어떤 정책이 좋은지는 요청 분포와 자원 제약에 달려 있습니다.'),detail('올림과 원복','선택한 연속 bit를 얻는 도중 다른 할당이 경쟁할 수 있습니다. 일부 획득 실패 시 이전 bit를 되돌리고 다시 찾아야 이중 할당이나 누수를 막습니다.')])

    topic('SipHash·키 기반 해시와 충돌 공격','자료구조·알고리즘','lib/siphash.c','siphash_1u64',
      '외부 입력으로 해시 테이블 bucket을 고를 때 공개 해시의 고의 충돌 입력에 대응할 필요가 있습니다.',
      'SipHash는 비밀 key를 사용한 ARX 혼합으로 짧은 입력의 해시를 계산합니다. SipHash-2-4는 message word당 두 압축 round와 마지막 네 round를 사용합니다. Key가 공개되는 단순 checksum과 달리 공격자의 결과 예측을 어렵게 하지만 유한 출력의 충돌 가능성 자체는 사라지지 않습니다.',
      '테이블 등의 목적에 맞게 난수 key를 준비하고 siphash 입력 형식·길이 규약을 따릅니다. 암호화·긴 파일의 collision-resistant digest·password hash와 역할을 구분합니다.',
      'siphash_1u64의 PREAMBLE·두 SIPROUND·POSTAMBLE과 byte 입력 함수를 읽으세요.',
      q('SipHash의 비밀 key를 모든 곳에 공개 고정값으로 두면 무엇을 잃는가?','입력 결과를 숨겨 충돌 공격을 어렵게 하는 전제','출력 bit 수가 자동으로 늘어남','공격자가 같은 key로 결과를 계산할 수 있습니다. 해시 테이블 방어 목적의 비밀·무작위 key 규약을 유지해야 합니다.'),
      q('64비트 해시값이 같으면 원본 키도 반드시 같은가?','실제 키 비교가 필요하다','유한 해시에는 충돌이 없다','64비트 출력에는 서로 다른 입력의 충돌 가능성이 있습니다. 해시 테이블은 후보를 찾은 뒤 실제 키를 비교합니다.'),
      details=[detail('ARX와 Round','덧셈·회전·XOR로 네 64비트 상태를 섞습니다. 길이와 마지막 남은 byte도 최종 계산에 반영됩니다. 입력 크기 전용 helper는 특정 길이의 규약을 최적화한 것입니다.'),detail('키 수명','Key 초기화 전에 테이블을 공개하거나 매 조회마다 다른 key를 쓰면 검색 계약이 깨집니다. 초기화·변경·테이블 재배치의 동기화를 설계합니다.')])

    topic('XXHash·빠른 비암호 해시','자료구조·알고리즘','lib/xxhash.c','xxh64',
      '데이터 후보를 빠르게 비교하거나 오류를 찾는 용도에는 암호학적 보장과 다른 빠른 해시가 쓰입니다.',
      'XXH64는 긴 입력을 네 accumulator로 8바이트씩 섞고 짧은 tail과 길이를 반영한 뒤 avalanche를 수행합니다. 정수 곱·rotate·shift·XOR로 값 분산을 만들지만 적대적 충돌 저항·인증을 목표로 하는 암호 해시는 아닙니다.',
      '입력 length·seed·endianness·unaligned 규약을 확인합니다. 후보 필터 뒤 실제 비교가 필요한 곳과 보안 검증이 필요한 곳을 구분하고 인증에 XXHash만 사용하지 않습니다.',
      'xxh64의 len>=32·v1…v4·tail 처리와 avalanche를 읽으세요.',
      q('XXHash만으로 공격자가 바꾼 파일의 진위를 보장할 수 있는가?','암호 인증 목적에는 적합한 별도 규약이 필요하다','어떤 보안 서명도 대체한다','빠른 비암호 해시는 적대적 변조 인증을 제공하지 않습니다. 신뢰 digest·서명·MAC의 목적과 다릅니다.'),
      q('XXH64의 긴 입력 한 반복에서 네 8바이트 word가 차지하는 길이는?','32바이트','64바이트','4×8=32바이트입니다. len>=32의 경로는 네 accumulator를 사용해 이 묶음을 처리합니다.'),
      details=[detail('Avalanche','마지막 shift·XOR·곱셈으로 작은 입력 차이가 출력 여러 bit에 퍼지게 합니다. 좋은 분산과 암호학적 비예측·충돌 저항은 같은 성질이 아닙니다.'),detail('Streaming 상태','전체 입력을 한 번에 hash하는 함수와 update·digest 상태 API를 구분합니다. Seed·길이·누적 accumulator·남은 byte buffer를 일관되게 유지해야 같은 출력이 나옵니다.')])

    topic('Generic B-tree·노드 분할과 다중 키','자료구조·알고리즘','lib/btree.c','btree_lookup',
      '노드에 여러 key와 value를 묶으면 포인터를 따라가는 단계 수를 줄이며 정렬된 대응을 관리할 수 있습니다.',
      'Generic B-tree는 geometry가 정한 key 폭과 노드의 여러 key/value 쌍을 사용합니다. Lookup은 내부 경로로 내려가 leaf의 key를 비교하고 insert는 공간 부족 시 분할을 처리합니다. 각 파일시스템의 영구 저장 B-tree와 이 메모리 library는 구현·정렬 규약이 다를 수 있습니다.',
      'btree_head·btree_geo와 key 저장 폭을 맞추고 insert·lookup·remove의 반환·객체 수명을 처리합니다. 비교 순서와 동시 접근 lock을 확인하고 value 포인터의 소유권을 정합니다.',
      'btree_lookup_node→btree_lookup의 keycmp와 btree_insert의 split을 읽으세요.',
      q('B-tree에서 노드가 여러 key를 담는 장점 중 하나는?','큰 분기수로 탐색 깊이를 줄일 수 있다','어떤 비교도 하지 않는다','노드 안 비교가 필요하지만 한 단계에 많은 범위를 나눌 수 있습니다. cache 배치와 노드 크기를 함께 고려합니다.'),
      q('Generic btree에 value 포인터를 넣으면 가리키는 객체 수명이 영구 보장되는가?','호출자가 객체 수명과 동기화를 관리해야 한다','포인터 값만으로 모든 해제를 차단한다','매핑 저장과 객체 참조 획득은 별도입니다. 탐색 중 해제 경쟁을 막을 lock·참조 규약이 필요합니다.'),
      details=[detail('Geometry','key가 차지하는 unsigned long 수와 노드당 쌍 수는 배치·비교 비용을 정합니다. 32비트와 64비트 CPU의 word 크기를 고려해야 key 배열을 정확히 읽습니다.'),detail('분할의 효과','가득 찬 노드의 항목을 나눠 새 노드를 만들고 부모 경계 key를 갱신합니다. 부모도 가득 차면 위로 분할이 이어집니다. 메모리 할당 실패를 포함해 불변식을 유지해야 합니다.')])

    topic('Associative Array·키 조각과 압축 경로','자료구조·알고리즘','lib/assoc_array.c','assoc_array_find',
      '커널 keyring 등에서 긴 키와 객체 대응을 관리할 때 키의 조각으로 후보를 좁히는 구조를 사용할 수 있습니다.',
      'Associative array는 ops가 제공하는 key chunk와 비교를 사용해 node·shortcut·leaf를 탐색합니다. 경로를 압축한 shortcut은 공통 prefix의 중간 단계를 줄입니다. 마지막 leaf의 실제 객체 비교와 RCU 읽기 보호, edit 적용·지연 해제를 구분합니다.',
      'assoc_array_ops의 key 추출·차이·객체 비교·해제 계약을 구현합니다. Find는 RCU read lock 또는 더 강한 보호가 필요하며 반환 객체를 밖에서 쓸 때 수명을 따로 확보합니다.',
      'assoc_array_find의 walk·terminal node·leaf 비교와 edit commit을 읽으세요.',
      q('키 조각 경로가 후보 node에 도달하면 실제 객체 비교는 생략 가능한가?','leaf의 compare_object로 실제 키를 확인한다','후보 위치가 곧 완전 동일성이다','탐색은 후보를 좁히고 마지막 실제 비교가 동일성을 확인합니다. Shortcut과 node 상태만으로 임의 객체를 반환하지 않습니다.'),
      q('Find 반환 포인터를 RCU 구간 밖에 저장하면 자동으로 수명이 연장되는가?','필요한 참조·lock을 별도로 확보한다','포인터 복사는 자동 refcount 증가다','RCU 탐색 보호와 객체의 장기 소유는 다른 규약입니다. 읽기 구간이 끝난 뒤 제거·해제될 수 있습니다.'),
      details=[detail('Tagged pointer','Node·shortcut·leaf를 포인터의 표시 bit 등으로 구분합니다. Raw pointer를 곧바로 객체로 dereference하지 말고 종류 검사·변환 helper를 사용해야 합니다.'),detail('Edit 준비와 적용','변경을 준비한 edit를 적용하는 단계와 실패 시 취소를 구분합니다. 새 node 할당·공개·옛 node 정리의 순서가 동시 독자의 안전한 탐색을 유지합니다.')])

    topic('Llist·CAS 기반 연결과 소비자 규약','자료구조·알고리즘','lib/llist.c','llist_add_batch',
      '짧은 지연 작업 목록을 여러 CPU에서 추가할 때 공유 mutex 없이 연결을 갱신하는 규약이 쓰입니다.',
      'Llist add는 새 목록의 끝을 기존 head에 붙이고 cmpxchg로 head를 교환합니다. 경쟁으로 head가 바뀌면 다시 시도합니다. Lockless라는 이름은 임의 다중 소비자·해제를 항상 허용한다는 뜻이 아니며 del_first와 del_all의 동시성 조건을 구분합니다.',
      'llist_add·add_batch와 적합한 소비 방식의 문서를 따릅니다. 소비한 객체의 수명·재사용·ABA 위험을 관리합니다. v6.12 주석의 del_first는 다중 소비자에 별도 lock이 필요하다는 제약을 확인합니다.',
      'llist_add_batch의 READ_ONCE→new_last->next→try_cmpxchg 루프와 del_first 주석을 읽으세요.',
      q('llist_add_batch의 cmpxchg가 실패하면 무엇을 해야 하는가?','갱신된 head에 맞춰 next를 다시 연결하고 재시도','실패를 성공으로 간주','다른 CPU가 head를 바꿨으므로 새 목록의 끝을 그 head에 연결해야 합니다. 재시도는 최신 값과 일치해야 합니다.'),
      q('Lockless 이름만 보고 del_first를 여러 소비자가 무조건 동시에 호출해도 되는가?','해당 API의 소비자 제약과 ABA 조건을 확인한다','어떤 조합도 항상 안전하다','파일 주석은 del_first의 다중 소비자 제약을 명시합니다. add·del_all의 가능한 조합과 객체 재사용 수명도 다릅니다.'),
      details=[detail('배치 추가','새 목록 new_first…new_last의 내부 연결을 먼저 준비합니다. 끝의 next를 old first에 두고 head를 새 first로 공개합니다. 실패하면 old first가 바뀌어 연결을 다시 맞춥니다.'),detail('ABA','Head pointer 값이 A→B→A로 돌아오면 주소만 비교해서 중간 변경을 놓칠 수 있습니다. Object reuse와 next 값의 변경까지 포함한 API 계약으로 안전성을 판단해야 합니다.')])

    topic('Sbitmap·분산 비트맵과 대기 큐','자료구조·알고리즘','lib/sbitmap.c','sbitmap_get',
      '높은 동시성의 tag 할당에서 한 비트맵 word와 하나의 대기 큐에 경쟁이 집중될 수 있습니다.',
      'Sbitmap은 bit를 여러 word에 나누고 CPU별 allocation hint 등으로 검색을 분산합니다. Sbitmap queue는 가용 bit가 없을 때 대기와 해제 후 wake를 연결합니다. Shallow depth는 특정 요청이 각 word의 일부만 사용하도록 제한하며 전체 tag 수를 무조건 줄이는 것과 다릅니다.',
      'init·get·clear·wake·free 수명을 따릅니다. 반환 음수는 할당 실패로 처리하고 bit 해제와 대기자 깨움 순서를 확인합니다. blk-mq tag의 실제 사용과 이 library의 bit 소유를 연결합니다.',
      'sbitmap_get의 alloc hint와 __sbitmap_get, queue wake·clear를 읽으세요.',
      q('가용 tag bit가 없어 get이 실패했는데 임의의 0을 성공 tag로 사용해도 되는가?','실패를 처리하고 대기·재시도 규약을 따른다','0은 항상 빈 tag다','이미 사용 중인 tag를 중복 사용하면 요청 식별과 수명이 깨집니다. 음수 반환과 가용성의 경쟁을 처리해야 합니다.'),
      q('분산 allocation hint의 목적 중 하나는?','검색·경쟁이 한 word에 집중되는 것을 줄인다','모든 bit를 같은 CPU에만 저장한다','CPU별 시작 힌트로 같은 처음 영역에만 접근하는 부담을 줄일 수 있습니다. 정답 여부는 bit의 원자 획득 규약에 따릅니다.'),
      details=[detail('Hint와 소유','Hint는 어디서 찾아볼지의 추천이며 bit 소유 자체가 아닙니다. 실제 atomic bit 획득이 성공해야 사용할 수 있습니다. 오래된 hint여도 안전성이 유지되어야 합니다.'),detail('Wake 배치','해제할 때 모든 대기자를 매번 깨우면 경쟁이 커질 수 있어 wake batch와 여러 wait state를 관리합니다. 성능 정책과 wake 누락 방지를 함께 확인합니다.')])

    topic('PerCPU Refcount·분산 참조의 종료 전환','자료구조·알고리즘','lib/percpu-refcount.c','percpu_ref_switch_to_atomic',
      '매 I/O마다 하나의 refcount cache line을 갱신하면 경쟁이 커져 지역 참조와 안전한 종료가 필요합니다.',
      'PerCPU ref는 정상 실행의 CPU별 참조 갱신과 종료를 위한 atomic 모드를 전환합니다. 전환은 기존 CPU별 접근이 지나가도록 조정한 뒤 합계를 반영합니다. Switch 호출 반환과 confirm 완료, kill과 마지막 release는 서로 다른 단계입니다.',
      'init·get/put·kill·confirm·release·exit의 규약을 따릅니다. 종료 시 새 참조가 생기는 경계를 막고 기존 참조가 끝날 때 객체를 해제합니다. 전환 중 임의 모드 변경이나 빠른 ref 직접 읽기를 하지 않습니다.',
      'percpu_ref_switch_to_atomic의 force_atomic과 __percpu_ref_switch_mode·sync wait를 읽으세요.',
      q('switch_to_atomic이 반환했으니 confirm 전에도 모든 전환 작업이 반드시 끝났는가?','비동기 전환 완료와 confirm·sync 규약을 구분한다','반환 순간 어떤 경로도 남아 있지 않다','Sync 함수는 별도로 confirm_switch 종료를 기다립니다. 호출 반환과 기존 접근 정리는 다른 경계입니다.'),
      q('종료 객체에서 분산 참조를 합치기만 하면 새로운 get을 허용해도 되는가?','새 참조의 진입 경계와 기존 참조 종료를 관리한다','집계가 언제나 영구적인 0을 만든다','계속 새 참조가 생기면 마지막 해제 판단이 깨질 수 있습니다. Kill·get_live 규약과 수명을 함께 봅니다.'),
      details=[detail('지역 합계','CPU별 갱신을 나누면 같은 cache line 경쟁을 줄입니다. 종료는 모든 지역 상태를 하나의 수명 판단에 연결해야 하므로 읽기 한 번의 합계만으로 안전한 해제 결정을 내릴 수 없습니다.'),detail('Release callback','마지막 참조를 확인한 release는 최종 정리를 연결합니다. Callback과 객체 메모리 해제, percpu 상태의 exit 순서를 맞추고 아직 참조하는 작업이 없는지 보장합니다.')])

    topic('Stack Depot·중복 스택과 Handle','자료구조·알고리즘','lib/stackdepot.c','stack_depot_save_flags',
      '많은 객체의 할당 stack을 그대로 저장하면 반복된 주소열이 큰 메모리를 쓰므로 중복을 줄일 수 있습니다.',
      'Stack depot은 stack 주소열을 해시해 bucket에서 실제 entries를 비교하고 동일 기록을 공유 handle로 참조합니다. 저장 공간 pool과 handle 인코딩·참조 수명·할당 flags를 관리합니다. Hash가 같다는 것만으로 다른 stack을 합치지 않습니다.',
      'stack_depot_save_flags와 fetch·put 지원 규약을 따릅니다. Context의 GFP·할당 허용·실패 handle을 확인하고 handle 수명 동안 해당 기록이 유지되는지 검토합니다. Interrupt stack 필터가 중복률에 영향을 줍니다.',
      'stack_depot_save_flags의 filter_irq_stacks·hash·bucket·record 비교와 pool handle을 읽으세요.',
      q('stack 해시값이 같으면 entries를 비교하지 않고 무조건 같은 기록인가?','실제 주소열을 비교해야 한다','해시 충돌은 불가능하다','유한 해시에서 충돌이 가능합니다. 동일한 stack 길이와 entries를 확인해야 올바르게 중복 제거합니다.'),
      q('Stack depot handle은 그 자체로 모든 상황의 raw stack 주소인가?','내부 기록을 식별하는 규약의 handle이다','항상 문자열 첫 byte의 포인터다','Handle을 fetch 규약으로 해석해야 기록을 찾을 수 있습니다. Pool 인코딩과 record 수명은 raw pointer와 다릅니다.'),
      details=[detail('중복 제거 계산','길이 20개의 64비트 주소열은 160바이트입니다. 같은 열을 10000번 그대로 보관하는 대신 한 기록과 handle들을 두면 반복 데이터가 줄어듭니다. 실제 비용은 metadata·pool·handle 폭도 포함합니다.'),detail('Interrupt 필터','Interrupt 이전의 임의 interrupted stack까지 모두 포함하면 같은 오류 경로의 기록이 끝없이 달라질 수 있습니다. Filter 규약은 중복 제거가 효율적으로 작동하도록 표현을 맞춥니다.')])
