"""Whole-file logical CPU mapping, hardware IDs and idle-state node lookup."""
ROWS = [dict(
    path='drivers/of/cpu.c', title='OF CPU 연결: 하드웨어 ID와 논리 번호, idle-state 참조',
    intro='하드웨어 ID 해석,architecture hook,양방향 CPU 노드 검색과 idle-state 탐색 전체를 분석합니다.',
    principle='하드웨어 식별자와 논리 CPU 번호의 대응은 아키텍처 정책이며,조회로 얻은 노드 참조는 명시적으로 반환해야 합니다.',
    use='셀 배열 파싱,선형 탐색,weak symbol,포인터 동일성과 대체 조회 경로를 학습합니다.',
    area='CPU 토폴로지 · 장치 트리 · 자료구조 · 참조 수명 · 오류 처리',
    sections=[
        ('파일과 hardware ID', 'GPL-2.0 파일은 cpu,kernel,OF 헤더를 포함합니다. of_get_cpu_hwid는 node의 address cell 수 ac와 reg 속성·바이트 길이를 얻습니다. 속성이 없거나 ac=0이거나 요청한 thread까지 필요한 바이트가 길이를 넘으면 ~0ULL을 반환합니다. 정상 경로는 ac*thread만큼 cell 포인터를 옮겨 of_read_number로 ID를 읽습니다. 논리 CPU 번호 자체를 reg 배열 첨자로 사용하는 것이 아닙니다.'),
        ('길이와 단위', 'reg는 __be32 cell 배열이며 한 ID가 ac개의 cell로 표현됩니다. 길이 검사는 sizeof(*cell)*ac*(thread+1)로 바이트 단위에 맞춥니다. 소스에는 이 곱셈의 별도 overflow helper가 없으므로 모든 비정상 입력의 산술까지 방어한다고 단정하지 않습니다. 반환 sentinel은 errno 정수가 아니라 u64의 모든 비트가 1인 값입니다.'),
        ('Weak 기본 매칭', 'arch_match_cpu_phys_id는 __weak이며 기본 구현은 (u32)phys_id==cpu입니다. 상위 32비트를 포함한 u64 전체 동등성 비교가 아닙니다. 아키텍처 구현으로 대체할 수 있다는 주석이 있고 실제 논리·물리 mapping은 secondary core를 부팅하기 전에 구성된다는 문서가 있습니다.'),
        ('속성의 thread 순회', '__of_find_n_match_cpu_property는 임의 속성명으로 cell과 ac를 얻습니다. cell도 없고 ac도 0이며 물리 ID 0이 cpu와 매칭되면 true를 반환하는 특수 경로가 있습니다. 이 경로는 thread 출력에 값을 쓰지 않습니다. 나머지 cell 또는 ac 부재는 false입니다. 바이트 길이를 sizeof(cell)*ac로 나누어 완전한 ID 개수만 순회하고 첫 매칭 tid를 thread가 nonNULL일 때 저장합니다.'),
        ('PowerPC 우선 속성과 fallback', 'weak arch_find_n_match_cpu_physical_id는 CONFIG_PPC이면 ibm,ppc-interrupt-server#s를 먼저 검사합니다. 그 조회가 true일 때만 바로 성공하고 그 밖에는 reg를 검사합니다. 주석은 속성 부재의 fallback을 설명하지만 실제 조건은 속성이 있어도 매칭되지 않으면 reg로 진행합니다. 속성 존재와 match 성공을 구분합니다.'),
        ('CPU 노드 획득', 'of_get_cpu_node는 for_each_of_cpu_node로 노드를 선형 순회하며 아키텍처 hook의 첫 성공 노드를 반환합니다. 없으면 NULL입니다. 반환 노드는 참조를 보유하므로 사용 후 of_node_put해야 합니다. 가능한 노드 수와 각 thread ID 수에 따라 검색 비용이 누적되며 전역 hash lookup을 구현하는 함수가 아닙니다.'),
        ('CPU device의 빠른 경로', 'of_cpu_device_node_get은 get_cpu_device(cpu)가 NULL일 때만 of_get_cpu_node(cpu,NULL)로 fallback합니다. device가 있으면 그 of_node에 of_node_get을 적용해 반환합니다. device는 있지만 of_node=NULL인 경우에도 트리를 다시 검색하는 분기는 없습니다. 기존 device 연결을 사용하는 것과 항상 전체 트리를 검색하는 것은 다릅니다.'),
        ('노드에서 논리 번호로', 'of_cpu_node_to_id는 possible CPU들을 순회하며 각각 참조를 얻고 cpu_node==np의 포인터 동일성을 기록한 뒤 np를 put합니다. 같으면 cpu를 반환하고 끝까지 없으면 -ENODEV입니다. 이름이나 reg 값 자체를 여기서 비교하지 않습니다. 입력 NULL 검사가 없으므로 조회 np도 NULL이면 동등 비교가 참이 될 수 있습니다. NULL 입력을 무조건 -ENODEV로 처리한다고 가정하면 안 됩니다.'),
        ('Idle state 계층 조회', 'of_get_cpu_state_node는 power-domains의 0번 항목을 #power-domain-cells 규칙으로 파싱합니다. 성공하면 args.np의 domain-idle-states에서 요청 index를 찾고 중간 args.np 참조를 put합니다. state_node가 있으면 반환하고 없거나 첫 파싱 오류면 CPU의 cpu-idle-states에서 같은 index를 조회합니다. 임의 깊이의 power-domain 트리를 재귀 순회하는 구현은 아닙니다.'),
        ('반환 참조와 전체 범위', 'idle state 반환도 참조가 증가한 노드이므로 호출자가 put합니다. 공개 CPU 노드 get,device node get,node to id,state node 함수 네 개는 EXPORT_SYMBOL입니다. ID reader,두 weak hook,속성 helper와 네 공개 함수 전체를 대조했습니다. 이 파일에는 캐시 노드 탐색이 없으며 실제 CPU hotplug나 아키텍처별 실행 테스트를 수행하지 않았습니다.')
    ], questions=[
        ('기본 arch_match_cpu_phys_id는 phys_id의 모든 64비트를 비교하는가?', '아니다. u32로 변환한 값을 cpu와 비교한다', '그렇다. 항상 u64 완전 동등성이다', '명시적 캐스트가 있습니다. 아키텍처별 override와 기본 구현을 구분해야 합니다.'),
        ('PPC 특수 속성이 있지만 매칭되지 않으면?', 'reg 속성을 이어 검사한다', '속성이 존재한다는 이유만으로 즉시 false를 반환한다', '조건은 특수 속성 helper의 true 반환 여부입니다. 주석의 부재 설명보다 실제 분기 범위가 넓습니다.'),
        ('CPU device는 있으나 of_node가 NULL이면 다시 트리를 검색하는가?', '아니다. of_node_get(NULL)의 결과를 반환하는 경로다', '그렇다. NULL이면 항상 전체 검색한다', 'fallback 조건은 cpu_dev의 부재입니다. 내부 필드의 부재와 다른 조건입니다.'),
        ('node_to_id가 비교하는 것은?', '노드 포인터 동일성', '노드 이름 문자열만', 'cpu_node==np를 계산하고 조회 참조를 put합니다. 이름이 같다는 것과 같은 객체라는 것은 다릅니다.'),
        ('node_to_id에 NULL을 주면 반드시 -ENODEV인가?', '아니다. 조회 np도 NULL이면 비교가 참일 수 있다', '그렇다. 첫 줄에서 NULL을 거부한다', '명시적 NULL 방어가 없음을 확인해야 합니다. API의 정상 사용 전제와 실제 분기를 구분합니다.'),
        ('계층형 idle-state 조회에서 중간 power-domain 노드 참조는?', 'domain-idle-states 조회 뒤 put한다', '성공할 때마다 영구 보유한다', '중간 args.np와 반환 state_node는 별개의 참조입니다. 반환 노드는 호출자 책임으로 남습니다.'),
        ('속성도 없고 ac=0인 특수 매칭 성공 시 thread를 0으로 쓰는가?', '아니다. 그 경로에는 thread 대입이 없다', '그렇다. 모든 성공 경로가 thread=0을 보장한다', 'thread 대입은 뒤의 정상 배열 순회 매칭 안에만 있습니다. 출력 인수는 모든 반환 경로를 추적해야 합니다.')
    ]
)]
