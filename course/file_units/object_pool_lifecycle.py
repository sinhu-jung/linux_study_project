"""Complete object pool allocation, initialization and teardown implementation."""
ROWS = [dict(
    path='lib/objpool.c',
    title='Objpool 구현: CPU별 연속 배치와 마지막 참조 해제',
    intro='객체 분배, vmalloc/kmalloc 선택, 초기화 실패와 drop/fini/free의 전체 흐름을 학습합니다.',
    principle='객체 하나의 논리적 폐기와 그 객체가 속한 메모리 블록의 실제 해제는 다른 시점입니다.',
    use='rethook node가 아직 실행 중일 때 pool 해제가 늦어지는 이유를 이해합니다.',
    area='메모리 풀 · NUMA · 나머지 분배 · 정렬 · 참조 카운트 · 실패 정리',
    sections=[
        ('전체 파일', 'GPL-2.0과 include 뒤 CPU slot 초기화 두 함수, slot 정리 함수, 공개 init/free/drop/fini가 있습니다. 공개 네 함수는 GPL 심볼로 export됩니다. pop/push의 원자적 링 연산은 objpool.h에 있으며 이 파일은 저장소 준비와 수명 종료를 담당합니다.'),
        ('입력 검사와 정렬', 'init은 객체 수와 크기가 각각 양수이며 최대 상수 이하인지 검사하고 아니면 EINVAL입니다. 크기는 sizeof(long)에 맞춰 올림합니다. capacity는 총 nr_objs를 2의 거듭제곱으로 올린 값이며 0이면 EINVAL입니다. CPU별 초기 객체 수가 아니라 전체 객체 수를 기준으로 각 ring capacity를 정합니다. pool 포인터 자체의 NULL 검사는 이 함수에 없습니다.'),
        ('관리 구조 초기화', '입력 검사가 끝나면 pool 전체를 0으로 지우고 가능한 CPU 수, 정렬 크기, capacity, context와 release를 저장합니다. 저장 gfp에서는 __GFP_ZERO를 제거합니다. cpu_slots 메모리는 kzalloc으로 마련하는데 실제 식은 nr_cpu_ids*sizeof(struct objpool_slot)입니다. 포인터 배열이므로 당연히 sizeof(pointer)를 사용한다고 고쳐 읽으면 원본과 달라집니다.'),
        ('CPU별 객체 분배', 'nr_cpu_ids 범위를 돌되 cpu_possible이 아닌 ID는 건너뜁니다. 각 가능한 CPU에는 총 객체 수/가능 CPU 수의 몫을 주고, 앞의 나머지 개 CPU에 한 개씩 더 줍니다. 예를 들어 10개를 가능한 CPU 3개에 나누면 4,3,3입니다. 객체보다 CPU가 많으면 초기 객체 0개인 slot도 생길 수 있습니다. cpu_count와 실제 CPU ID를 구분합니다.'),
        ('하나의 연속 할당 블록', 'slot 크기는 구조체와 capacity개 entry 포인터의 크기에 정렬 객체 크기*지역 객체 수를 더합니다. 객체 영역은 &slot->entries[capacity]에서 시작합니다. 따라서 pointer ring 뒤에 실제 객체들이 연속으로 배치됩니다. 크기는 int 지역 변수로 저장되며 이 파일이 모든 곱셈·합산을 별도 overflow 검사 API로 보호한다고 설명하지 않습니다.'),
        ('할당 방식과 NUMA', 'gfp mask 조건이 GFP_ATOMIC 경로에 해당하지 않으면 __vmalloc_node를 먼저 시도하고 실패하거나 건너뛰면 kmalloc_node를 사용합니다. 둘 다 cpu_to_node(i)를 전달합니다. 주석은 vmalloc의 page 단위 비용과 slab 압력 감소를 논의합니다. 성공 뒤 전체 slot과 객체 영역을 memset으로 0으로 채우고 cpu_slots[i]에 저장하므로 __GFP_ZERO 제거가 객체를 미초기화 상태로 둔다는 뜻은 아닙니다.'),
        ('각 객체 초기화와 등록', 'slot mask는 capacity-1입니다. 각 객체에서 objinit이 있으면 먼저 호출하고 오류면 즉시 그 값을 반환합니다. 성공한 객체만 entries[tail&mask]에 넣고 객체 포인터를 obj_size만큼 옮기며 tail, last, pool->nr_objs를 증가시킵니다. 초기화 도중이므로 이 단계는 외부 동시 소비를 위한 일반 push 함수를 호출하지 않습니다.'),
        ('실패 정리의 범위', 'CPU slot 준비가 실패하면 init은 마련된 모든 cpu_slots 항목을 kvfree하고 배열을 kfree하는 정리 함수를 호출한 뒤 rc를 반환합니다. 이 정리 경로에는 개별 객체 destructor나 사용자 release callback 호출이 없습니다. objinit이 외부 자원을 따로 얻었다면 자동으로 모두 되돌려 준다고 가정하면 안 됩니다. 성공하면 ref를 실제 등록 객체 수+1로 설정합니다.'),
        ('강제 free와 반복 호출 전제', 'objpool_free는 cpu_slots가 NULL이면 반환하고 아니면 모든 slot과 배열을 해제한 뒤 release가 있으면 호출합니다. release의 int 반환값은 사용하지 않습니다. 이 함수는 ref를 검사해 대여 객체가 끝날 때까지 기다리지 않으며, 정리 helper도 cpu_slots를 NULL로 다시 쓰지 않습니다. 같은 pool에 임의로 free를 반복해도 안전하다는 계약으로 읽으면 안 됩니다.'),
        ('Drop은 개별 kfree가 아님', 'drop은 obj나 pool이 NULL이면 EINVAL입니다. 그 뒤 obj 주소의 소속을 검사하거나 역참조하지 않고 pool ref를 하나 감소시킵니다. 마지막 참조이면 free 후 0, 아니면 EAGAIN입니다. 따라서 EAGAIN이어도 해당 참조는 이미 감소했으므로 같은 객체를 재시도 명목으로 다시 drop하면 안 됩니다. 객체들이 slot 블록 안에 있으므로 개별 object kfree를 하지 않습니다.'),
        ('Fini의 추가 참조', 'fini는 count=1로 시작하여 pop으로 남은 free 객체를 모두 빼낼 때마다 count를 늘립니다. 그 합을 ref에서 빼고 0이면 free합니다. 처음의 1은 pool 자체의 추가 참조입니다. 대여 객체 참조가 남으면 실제 저장소는 이후 마지막 drop까지 유지됩니다. 진행 중 push가 없어야 한다는 호출자 계약은 헤더에 설명되어 있으며 여기서 RCU 대기를 직접 실행하지 않습니다.'),
        ('CS 연결과 검증 범위', '균등 분배와 나머지 처리, 링 크기와 실제 객체 수의 차이, 저장 블록과 논리 객체 수명의 분리, 부분 초기화 정리, 참조를 소비한 뒤 반환하는 상태 코드의 의미를 학습합니다. 전체 소스 대조는 최대 입력의 모든 산술이나 실제 NUMA·메모리 부족 상황을 실행 검증한 것은 아닙니다.')
    ],
    questions=[
        ('객체 10개와 가능한 CPU 3개이면 초기 분배는?', '4개, 3개, 3개이다', '각 CPU에 10개씩 만든다', '몫은 3이고 나머지 1을 앞의 가능한 CPU에 더합니다. ring capacity와 초기 객체 분배는 별개입니다.'),
        ('drop이 EAGAIN을 반환하면 같은 객체로 다시 호출해야 하는가?', '아니다. 그 호출에서 참조는 이미 감소했다', '그렇다. 아직 아무 처리도 하지 않았다는 뜻이다', 'EAGAIN은 다른 참조가 남았다는 상태입니다. 같은 논리 참조를 두 번 포기하면 수명 계산을 망가뜨릴 수 있습니다.'),
        ('objinit 실패 정리는 사용자 release callback도 호출하는가?', '아니다. 이 경로는 slot과 배열 메모리 정리만 한다', '그렇다. 모든 callback을 자동 역순 실행한다', 'init의 오류 경로는 objpool_fini_percpu_slots를 직접 호출합니다. 사용자 release는 objpool_free에서 호출합니다.'),
        ('성공 초기화의 참조 수에 추가되는 1은 무엇인가?', 'pool 자체가 유지하는 추가 참조이다', '존재하지 않는 가짜 객체 하나이다', 'fini의 count=1이 대응합니다. 객체 참조와 pool 유지 참조를 함께 관리하여 대여 객체의 지연 종료를 지원합니다.'),
        ('objpool_drop이 개별 객체 주소의 소속을 검증하는가?', '아니다. NULL 검사 뒤 pool 참조를 감소시킨다', '그렇다. 모든 CPU slot 범위를 순회해 확인한다', '본문에는 주소 검색이나 obj 역참조가 없습니다. 유효한 객체와 단 한 번의 drop은 호출자가 지켜야 합니다.')
    ]
)]
