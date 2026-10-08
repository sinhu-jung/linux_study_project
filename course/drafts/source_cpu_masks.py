"""Whole lib/cpumask.c reading; pending after bitmap strings unit."""
def register(topic, q, detail):
    def lesson(title, symbol, why, principle, use, reading, qa, cards):
        topic(title, 'CPU·아키텍처', 'lib/cpumask.c', symbol, why,
              principle, use, reading, *(q(*x) for x in qa),
              details=[detail(*x) for x in cards])

    lesson('CPU Mask Wrap·한 바퀴 순회와 시작점', 'cpumask_next_wrap',
        'CPU 번호 집합을 특정 위치부터 순회하고 끝에서 돌아와 중복 없이 종료하는 원리를 배웁니다.',
        'Cpumask_next_wrap은 n 다음 set CPU를 찾습니다. 끝을 넘으면 wrap=true로 바꾸고 n=-1에서 다시 찾습니다. 이미 wrap한 상태에서 n<start이고 다음 후보가 start 이상이면 nr_cpumask_bits를 반환해 종료합니다. 시작 CPU가 mask에 없어도 돌아온 탐색이 시작 경계를 넘는 조건으로 한 바퀴를 끝낼 수 있습니다.',
        '이 helper를 사용할 때 start,n,wrap의 반복 규약을 맞춥니다. 현재 header의 for_each_cpu_wrap은 별도의 find_next_bit_wrap/__for_each_wrap 경로이므로 이 lib 함수와 같은 실행 경로로 세지 않습니다. 반환 CPU가 nr_cpu_ids 미만인지 확인합니다. Mask가 비어 있는 경우와 시작 bit가 없는 경우를 다루며 순회 중 mask 변경의 동기화는 caller 문맥을 확인합니다.',
        'again label,끝에서 n=-1,wrap과 시작 경계 종료 조건을 읽으세요.',
        [('Mask가{1,4},start3이면 순회 순서는?', "4 다음 1이다", "Start3이 없으므로 아무 CPU도 순회하지 않는 다", "시작 이후 4를 찾고 끝에서 wrap하여 1을 찾습니다. 다음 4는 시작 경계를 넘으므로 한 바퀴 종료입니다."),
         ('Wrap 상태에서 시작 경계를 다시 넘으면 반환값은?', '유효 CPU 범위 밖의 종료 값이다', 'Start bit를 강제로 set한 CPU 번호이다', '원본은 nr_cpumask_bits를 반환합니다. 시작점이 mask에 실제 포함된다고 가정하지 않습니다.')],
        [('CPU 번호와 개수', 'CPU 번호가 희소할 수 있어 mask의 원소 개수와 최대 번호 경계가 다릅니다. 이 고정 버전의 header에서 nr_cpumask_bits는 nr_cpu_ids로 정의되며 작은 상수 최적화용 크기와 구분됩니다.'),
         ('현재 Header Macro', '고정 버전의 for_each_cpu_wrap은 for_each_set_bit_wrap으로 연결됩니다. 여기의 cpumask_next_wrap body를 그대로 호출하는 macro가 아닙니다. 두 순회 경로를 각각 읽고 실행 검증합니다.'),
         ('Finder의 역할', 'Cpumask_next의 n=-1은 적법한 첫 탐색 인자입니다. 이 helper는 특정 CPU를 online으로 만들거나 태스크를 그 CPU로 이동하는 함수가 아니라 번호 집합의 반복 함수입니다.')])

    lesson('CPU Mask Offstack·CONFIG에 따른 저장 수명', 'alloc_cpumask_var_node',
        '큰 CPU 집합을 stack 밖에 보관할 때 빌드 설정이 할당 API의 의미를 바꾸는 원리를 배웁니다.',
        "CONFIG_CPUMASK_OFFSTACK에서 는 cpumask_size byte를 kmalloc_node로 요청하여 *mask에 저장하고 NULL 여부를 bool로 반환합니다. DEBUG_PER_CPU_MAPS이면 실패 시 로그와 dump_stack을 호출합니다. Free_cpumask_var는 kfree입니다. Offstack이 꺼진 header 구현은 이미 배열 저장공간을 갖는 cpumask_var_t를 사용하여 alloc은 true,free는 no-op입니다.",
        "선택한 CONFIG와 cpumask_var_t 정의를 함께 읽고 실패 bool을 검사합니다. 일반 alloc은 모든 bit를 0으로 만든다는 보장이 없고 zalloc wrapper가 ZERO flag를 추가합니다. Node 요청을 반드시 그 물리 node에 배치된다는 무조건 보장으로 해석하지 않습니다.",
        'kmalloc_node 인자,*mask 반환,DEBUG 분기와 대응 free를 읽으세요.',
        [('Offstack alloc이 실패하면 *mask와 반환값은?', "NULL과 false이다", "오래된 pointer를 보존하고 true이다", '할당 결과를 바로 *mask에 대입한 뒤 *mask!=NULL을 반환합니다. 실패한 새 allocation을 성공 객체로 사용할 수 없습니다.'),
         ('Offstack이 꺼진 경우 같은 alloc API는?', "Header의 true 반환 no-op 구현이다", '언제나 같은 kmalloc_node body를 실행한다', 'CONFIG가 저장 형식과 구현을 바꿉니다. 고정 배열과 동적 pointer 경로를 같은 실제 allocation이라고 설명하지 않습니다.')],
        [('크기 계산', 'Cpumask_size는 header의 bitmap_size(large_cpumask_bits)와 연결됩니다. 최적화에 쓰는 저장 크기는 유효 nr_cpu_ids보다 클 수 있고 allocation은 필요한 저장 크기를 확보해야 합니다.'),
         ('해제 종류', '일반 kmalloc 기반 cpumask는 free_cpumask_var 경로입니다. Boot 초기의 memblock 기반 mask는 다른 해제 API를 사용합니다. 같은 bit 표현이라도 allocation 출처와 수명은 다릅니다.')])

    lesson('CPU Mask Bootmem·초기 할당 실패의 Panic', 'alloc_bootmem_cpumask_var',
        '부팅 초기의 memory 관리 API와 일반 실행 중 allocation의 서로 다른 실패 정책을 배웁니다.',
        'Offstack의 alloc_bootmem_cpumask_var는 cpumask_size와 SMP_CACHE_BYTES 정렬로 memblock_alloc을 호출합니다. NULL이면 함수명과 크기를 담아 panic합니다. 원본 문서는 성공 객체를 zero-filled로 설명합니다. Free_bootmem_cpumask_var는 동일 크기를 memblock_free로 반환하며 일반 kfree를 호출하지 않습니다.',
        "초기화 단계와 allocation 출처가 맞는 환경에서 사용합니다. 이 API는 실패 bool을 반환하는 normal alloc의 대체가 아닙니다. Offstack이 꺼진 header에서 는 boot alloc/free도 no-op이므로 빌드 경로를 구분합니다.",
        '__init,memblock alignment,NULL panic,대응 크기의 memblock_free를 읽으세요.',
        [('Bootmem allocation 실패 시 이 wrapper는?', 'Panic 경로로 들어간다', 'False를 반환해 caller가 무시할 수 있다', '반환형은 void이고 원본은 NULL이면 panic을 호출합니다. 일반 alloc의 bool 실패 계약과 다릅니다.'),
         ('Bootmem mask를 돌려주는 원본 API는?', 'memblock_free이다', "항상 kfree이다", 'Free_bootmem_cpumask_var는 memblock_free(mask,cpumask_size())를 호출합니다. Allocation 출처에 맞춰 해제합니다.')],
        [('초기 실행 단계', '__init는 초기화용 코드의 section·수명과 연결됩니다. 실제 memory 해제와 부팅 단계 제어는 memblock 및 초기화 시스템 구현의 영역이며 이 짧은 wrapper만으로 전체를 실행 검증하지 않습니다.'),
         ('정렬과 내용', 'SMP_CACHE_BYTES는 요청 alignment입니다. Zero-filled 성공 조건은 memblock_alloc 계약과 원본 주석에 연결됩니다. 일반 kmalloc_node의 비초기화 자료와 구분합니다.')])

    lesson('CPU Local Spread·NUMA 거리와 순번 Modulo', 'cpumask_local_spread',
        'CPU를 단순한 번호 순서 대신 node와의 거리 순서로 선택하고 요청 순번을 순환시키는 방법을 배웁니다.',
        "I를 num_online_cpus로 modulo한 뒤 cpu_online_mask와 node를 sched_numa_find_nth_cpu에 전달합니다. 그 helper는 NUMA 거리 단계에서 i번째 CPU를 찾고 NUMA_NO_NODE에서 는 online 교집합의 순번을 찾습니다. 반환 CPU가 nr_cpu_ids 이상이면 WARN_ON하지만 wrapper가 다른 CPU로 재시도하는 fallback은 없습니다.",
        'Online CPU가 양수이고 선택 중 topology·hotplug가 적절히 보호되는 호출 문맥을 사용합니다. 선택한 번호가 이후에도 online으로 유지된다는 예약을 이 함수만으로 얻지 않습니다. 전체 CPU 열거에는 원본 주석의 NUMA hop iterator 비용을 비교합니다.',
        "Modulo,online mask 전달,node 인자,WARN 뒤 그대로 return을 읽으세요.",
        [("Online CPU가 3개일 때 요청 i7은 helper에 어떤 순번으로 전달되는 가?", '1이다', '7을 그대로 넘긴다', "7%3은 1입니다. 이 순번은 CPU 번호 1 자체가 아니라 거리 순서에서 두 번째 후보를 뜻합니다."),
         ("Finder가 nr_cpu_ids를 반환하면 wrapper가 자동 재선택하는 가?", 'Warning 뒤 그 값을 반환한다', "항상 CPU0으로 바꿔 성공한다", '원본은 WARN_ON(cpu>=nr_cpu_ids) 후 return cpu입니다. 경고가 유효 결과를 자동 생성하지 않습니다.')],
        [('거리 순서', "Local node의 CPU가 먼저 오고 더 먼 node의 CPU가 뒤따르는 policy입니다. 단순 i를 CPU번호로 반환하는 산술이 아닙니다. NUMA finder의 topology를 host fixture에서 모의했다면 실제 NUMA 거리 검증과 구분합니다."),
         ('열거 비용', '원본은 CPU별로 반복 호출하는 방식의 O(levels*nr_cpu_ids*log(nr_cpu_ids))와 hop iterator의 O(levels*nr_cpu_ids)를 비교합니다. 한 CPU 선택과 전체 집합 열거를 같은 비용이라고 보지 않습니다.')])

    lesson('CPU 교집합 분배·Per CPU 이전 선택', 'cpumask_any_and_distribute',
        '두 조건을 모두 만족하는 CPU를 고르고 호출 CPU별 이전 위치를 기억해 선택을 분산하는 원리를 배웁니다.',
        "DEFINE_PER_CPU의 distribute_cpu_mask_prev를 __this_cpu_read로 읽고 prev+1부터 두 mask의 교집합 set bit를 wrap 탐색합니다. Next<nr_cpu_ids인 경우만 이전 선택을 갱신합니다. 초기 prev0에서 첫 탐색은 1부터 시작하므로 가능한 경우 CPU0을 건너뜁니다. 빈 교집합의 종료값은 상태를 갱신하지 않습니다.",
        '두 mask의 공통 후보와 nr_cpu_ids 미만 반환 여부를 확인합니다. Per CPU 저장이므로 전체 시스템의 하나의 round-robin counter가 아닙니다. CPU 이동·선점 및 같은 CPU의 동시 접근 조건은 __this_cpu primitive와 caller 문맥에 맞춰 확인합니다.',
        "공유 per CPU 변수,prev+1,AND wrap,유효 결과일 때만 write를 읽으세요.",
        [("두 mask 교집합이{0,2,5},초기 prev0이면 첫 선택은?", '2이다', "반드시 0이다", "Search offset은 prev+1=1입니다. 그 이상 첫 공통 bit2를 선택하고 이후 5,0으로 순환할 수 있습니다."),
         ('교집합이 비어 있을 때 이전 선택 상태는?', "갱신하지 않는 다", "반환 종료값을 항상저장한다", "원본은 next<nr_cpu_ids 조건에서 만 __this_cpu_write합니다. 빈 결과를 다음 유효 CPU로 기록하지 않습니다.")],
        [('상태의 범위', 'CPU A의 호출이 선택한 prev와 CPU B의 prev는 별도 저장공간입니다. 두 CPU가 같은 후보를 동시에 고를 수 있으므로 이 함수가 대상 CPU의 독점 예약이나 충돌 없는 분배를 보장하지 않습니다.'),
         ('CONFIG 예외', 'Header의 NR_CPUS==1 경로는 first_and를 반환하는 inline 구현입니다. 여기의 per CPU 회전 body가 모든 빌드에서 실행되는 것이 아닙니다. 전체 CPU online 여부는 입력 mask의 의미에 달려 있습니다.')])

    lesson('CPU 단일 Mask 분배·교집합 함수와 공유 Cursor', 'cpumask_any_distribute',
        '한 CPU 집합에서 회전 선택하고 다른 선택 함수와 같은 상태를 사용하는 효과를 배웁니다.',
        'Cpumask_any_distribute는 동일한 distribute_cpu_mask_prev를 읽어 prev+1부터 단일 mask를 wrap 탐색합니다. 유효 next만 상태에 저장합니다. 같은 CPU에서 AND variant와 번갈아 호출하면 두 함수가 서로의 마지막 선택 이후부터 찾습니다. 이름 any는 난수 선택을 뜻하지 않으며 실제 body는 기억한 위치 다음 탐색입니다.',
        "반환 범위를 검사하고 mask의 CPU가 실제 작업에 허용되는 지 별도로 확인합니다. Cpu_online_mask를 자동 교차하는 함수가 아니므로 offline 후보도 입력 조건에 따라 포함될 수 있습니다. Per CPU cursor를 전역 공정성·부하 측정·태스크 이동 명령으로 해석하지 않습니다.",
        "한 입력 bit wrap과 AND variant에서 읽은 같은 변수 이름을 비교하세요.",
        [("AND variant가 같은 CPU에서 5를 선택한 뒤 단일 mask{0,2,5}를 고르면?", '0으로 wrap한다', "단일 함수의 별도 초기 cursor를 사용해 2를 고른다", "두 body는 같은 per CPU 변수를 사용합니다. Prev5 뒤 후보가 없으므로 처음으로 돌아와 0을 선택합니다."),
         ("이 함수가 mask를 online CPU와 자동 교차하는 가?", '그런 교차 없이 주어진 mask를 탐색한다', '내부에서 항상 cpu_online_mask를 AND한다', '원본은 cpumask_bits(srcp)를 단일 finder에 전달합니다. Online 제한이 필요하면 caller가 입력 조건을 구성해야 합니다.')],
        [('빈 집합', 'Find helper는 set bit가 없으면 size를 반환합니다. 단일 함수의 원본 주석에 intersection이라는 단어가 있지만 실제 body에는 두 번째 입력이 없습니다. 문제와 해설은 실제 단일 mask 탐색을 따릅니다.'),
         ('동작을 읽는 순서', 'Mask라는 자료구조,wrap이라는 검색 알고리즘,per CPU라는 상태 분산 기술이 결합됩니다. 선택한 CPU 번호와 그 CPU에 작업을 실제로 배치하는 후속 API의 역할을 나누어 읽습니다.')])
