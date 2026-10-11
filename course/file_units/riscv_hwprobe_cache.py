"""Whole-file RISC-V hwprobe vDSO cache, comparison helpers, and data."""
ROWS = [dict(
    path='arch/riscv/kernel/vdso/hwprobe.c',
    title='RISC-V hwprobe 캐시: 값 조회와 CPU 집합 필터링',
    intro='공유된 전체 CPU 결과를 사용하는 두 빠른 경로와 syscall 전환을 분석합니다.',
    principle='모든 CPU가 같은 값을 가진다는 전제가 있으면 집합별 질의를 재사용할 수 있지만, 이질적인 집합은 별도 계산이 필요합니다.',
    use='값 조회와 조건에 맞는 CPU 선택의 차이, bitmask 포함 비교와 실패 시 출력 수정을 설명합니다.',
    area='캐싱 · 동질성 · 집합 필터 · 비트마스크 · 선형 순회 · syscall fallback',
    sections=[
        ('전체 구성', 'GPL-2.0 뒤 string·types·vDSO datapage·helpers를 포함합니다. 외부 riscv_hwprobe syscall 연결 함수를 선언하고 static 값 조회·CPU 선택 helper, 공개 __vdso_riscv_hwprobe 원형과 본문을 둡니다. 공개 원형을 따로 둔 주석의 목적은 -Wmissing-prototypes 방지입니다.'),
        ('값 조회의 캐시 조건', 'riscv_vdso_get_values는 __arch_get_vdso_data의 arch_data를 사용하고 all_cpus를 !cpusetsize && !cpus로 계산합니다. flags가 0이 아니거나, 전체 CPU 요청이 아닌데 homogeneous_cpus가 거짓이면 원래 다섯 인수로 syscall을 호출합니다. 전체 CPU의 정적 답만 저장하지만 CPU들이 동질적이면 다른 mask 요청에도 그 값을 재사용한다는 주석입니다.'),
        ('Pair 배열의 값 채우기', '빠른 경로에서는 pairs부터 pairs+pair_count까지 순회합니다. 유효 key이면 all_cpu_hwprobe_values[key]를 value에 복사하고, 무효 key이면 key=-1과 value=0으로 바꿉니다. 일부 key가 무효라고 함수 전체를 -EINVAL로 끝내지 않고 나머지 pair도 처리하여 0을 반환합니다. 이 helper에는 CPU mask 내용을 직접 스캔하는 코드가 없습니다.'),
        ('CPU 선택의 기본 검사', 'riscv_vdso_get_cpus는 cpusetsize가 0이거나 cpus가 NULL이면 -EINVAL을 반환합니다. unsigned char *c로 mask를 바이트 단위 순회하여 하나라도 0이 아닌지 확인합니다. empty_cpus, flags가 정확히 RISCV_HWPROBE_WHICH_CPUS가 아님, CPU 비동질성 중 하나면 syscall로 갑니다. 빈 mask를 단순히 성공한 빈 결과로 즉시 반환하지 않습니다.'),
        ('동질적인 CPU의 조건 비교', '유효 pair마다 같은 key와 캐시 value의 임시 t를 만들고 riscv_hwprobe_pair_cmp(&t,p)로 비교합니다. 불일치가 하나라도 있으면 clear_all=true입니다. 무효 key도 clear_all을 설정하고 해당 pair를 -1·0으로 고칩니다. clear_all 이후에도 모든 pair를 끝까지 처리하므로 첫 오류 뒤의 무효 pair도 표시할 수 있습니다.'),
        ('Mask 결과는 유지 또는 전체 제거', 'clear_all이면 cpusetsize 바이트를 전부 0으로 만들고 아니면 입력 mask를 그대로 보존합니다. 동질적인 CPU 전제에서 특정 pair 조건이 맞으면 선택된 CPU들이 함께 맞고, 하나라도 맞지 않으면 모두 제외하는 빠른 경로입니다. mask에 새로운 CPU 비트를 추가하는 코드나 온라인 CPU 여부를 하나씩 검사하는 코드는 없습니다. 그 밖의 입력 검증까지 이 파일이 보장한다고 확대하지 않습니다.'),
        ('공개 dispatch의 bit 검사', '__vdso_riscv_hwprobe는 flags & WHICH_CPUS가 참이면 CPU 선택 helper로, 아니면 값 조회 helper로 갑니다. dispatch는 bit 포함 검사지만 CPU helper의 빠른 경로는 flags가 정확히 WHICH_CPUS여야 합니다. 따라서 그 비트와 미지의 추가 비트를 함께 주면 CPU 경로로 들어가더라도 syscall로 전환합니다.'),
        ('복잡도와 동기화 범위', '값 조회는 pair_count에 비례하고 CPU 경로는 mask 바이트 수와 pair_count에 비례합니다. 각 pair마다 모든 CPU를 중첩 순회하지 않는 것이 캐시와 동질성 전제의 이점입니다. 이 파일에는 공유 정적 답을 읽는 seq 재시도 루프나 사용자 포인터 접근 fault 처리 본문이 없습니다. helpers 헤더 포함만으로 시간 조회와 같은 재시도를 한다고 가정하지 않습니다.'),
        ('검증 범위', '모든 선언·helper·루프·fallback·출력 변경을 설명했습니다. 실제 heterogeneous 시스템의 hwprobe syscall과 결과를 비교한 실행 시험은 수행하지 않았습니다. 입력 포인터·크기와 캐시 초기화의 전체 계약은 호출부와 커널 구현을 추가로 확인해야 합니다.')
    ],
    questions=[
        ('값 조회에서 all_cpus가 참이 되는 입력은?', 'cpusetsize=0이고 cpus=NULL인 경우이다', '둘 중 하나만 0이면 된다', '코드는 두 부정 조건의 AND입니다. OR로 읽으면 syscall 전환 조건을 잘못 이해하게 됩니다.'),
        ('동질 CPU 선택 경로에서 조건 하나가 불일치하면 mask는?', '전체 바이트를 0으로 만든다', '임의 CPU 하나만 제외한다', '모든 CPU가 같은 정적 값을 갖는 전제이므로 선택된 CPU들이 조건에 함께 실패합니다. clear_all로 표시한 뒤 전체 mask를 지웁니다.'),
        ('무효 key를 만나면 첫 pair에서 바로 함수가 끝나는가?', '아니다. key=-1,value=0으로 표시하고 계속 순회한다', '그렇다. 언제나 즉시 -EINVAL을 반환한다', '두 helper 모두 pair 루프를 계속합니다. CPU 선택 경로에서는 추가로 clear_all을 설정합니다.'),
        ('WHICH_CPUS 외의 추가 flag도 있으면 빠른 CPU 필터가 처리하는가?', '아니다. dispatch 후 helper의 정확한 flags 검사에서 syscall로 간다', '그렇다. dispatch에서 bit 하나가 맞으면 추가 flag는 무조건 무시한다', '진입점을 선택하는 bit 검사와 빠른 처리의 허용 조건은 별개입니다.')
    ]
), dict(
    path='arch/riscv/include/asm/hwprobe.h',
    title='RISC-V hwprobe 비교: 범위 검사와 방향 있는 부분집합',
    intro='최대 key와 세 inline helper를 전체 분석합니다.',
    principle='기능 비트의 요구 조건은 동등 비교보다 포함 관계로 표현하는 것이 적절할 수 있으며 비교 방향이 중요합니다.',
    use='범위 검사와 bitmask 분류, 비대칭 pair 비교를 설명합니다.',
    area='범위 검사 · 비트 집합 · 부분집합 · 비교 predicate',
    sections=[
        ('전체와 유효 key', 'GPL-2.0 WITH Linux-syscall-note guard 아래 uapi/asm/hwprobe.h를 포함하고 RISCV_HWPROBE_MAX_KEY=9를 정의합니다. riscv_hwprobe_key_is_valid(__s64 key)는 key>=0 && key<=9를 반환합니다. 음수와 10 이상은 제외하며 여기서는 범위 안의 모든 정수를 유효하게 봅니다.'),
        ('Bitmask key 분류', 'hwprobe_key_is_bitmask는 BASE_BEHAVIOR, IMA_EXT_0, CPUPERF_0 세 key만 true로 반환하고 나머지는 false입니다. key가 유효한지 먼저 검사하는 함수는 아니며 분류만 합니다. 값이 정수라는 이유만으로 모든 key를 bitmask로 비교하지 않습니다.'),
        ('비교의 방향', 'riscv_hwprobe_pair_cmp는 먼저 key가 다르면 false입니다. bitmask key이면 (pair->value & other_pair->value)==other_pair->value로 첫 pair가 두 번째의 모든 요구 비트를 포함하는지 봅니다. 그 외에는 value가 같은지 검사합니다. 첫 값 0b111, 요구 0b101이면 true지만 둘을 바꾸면 false이므로 일반적인 대칭 동등 비교가 아닙니다.'),
        ('범위와 계약', '세 helper는 입력 구조체를 수정하지 않습니다. pair_cmp 자체는 NULL 포인터나 key 유효 범위를 검사하지 않으므로 호출부가 필요 조건을 관리해야 합니다. 전체 정의를 설명했으며 UAPI의 모든 feature key 의미나 실제 CPU 지원 여부를 이 헤더만으로 검증하지 않습니다.')
    ],
    questions=[
        ('Bitmask key에서 첫 value=7, 두 번째 value=5이면 비교 결과는?', 'true이다. 7이 5의 모든 비트를 포함한다', 'false이다. 두 숫자가 같지 않다', '7&5=5이므로 요구 비트 포함 조건을 만족합니다. 같은 key라는 전제가 필요합니다.'),
        ('pair_cmp 자체가 key 0~9 범위 검사도 수행하는가?', '아니다. 별도의 key_is_valid helper와 구분된다', '그렇다. 모든 비교 함수가 자동으로 같은 검사를 수행한다', 'pair_cmp의 첫 검사는 두 key가 같은지입니다. 범위 검사 helper를 호출하는 코드는 없으므로 호출부 검증을 생략할 근거가 아닙니다.')
    ]
), dict(
    path='arch/riscv/include/asm/vdso/data.h',
    title='RISC-V vDSO 정적 hwprobe 답안 저장 구조',
    intro='아키텍처 공유 데이터 구조체의 두 멤버와 배열 크기를 분석합니다.',
    principle='캐시된 집계 결과와 그 결과를 다른 질의에도 재사용할 수 있는 조건을 함께 저장할 수 있습니다.',
    use='전체 CPU 답의 배열과 homogeneous 표시의 역할을 구분합니다.',
    area='배열 인덱싱 · 캐시 · 공유 데이터 · 구조체 정렬',
    sections=[
        ('전체 정의', 'GPL-2.0 include guard 아래 linux/types.h, vdso/datapage.h, asm/hwprobe.h를 포함합니다. arch_vdso_data 구조체 하나를 정의하며 함수는 없습니다. 공통 vDSO 데이터 안에 넣을 아키텍처별 내용을 제공합니다.'),
        ('값 배열과 표시', '__u64 all_cpu_hwprobe_values[RISCV_HWPROBE_MAX_KEY+1]는 전체 CPU가 선택된 정적 답을 저장합니다. 현재 MAX_KEY=9이므로 10개 u64, 80바이트의 배열입니다. __u8 homogeneous_cpus는 모든 CPU의 정적 hwprobe 값이 같은지 나타내는 Boolean 의미의 필드입니다. C 자료형은 bool이 아니라 __u8입니다.'),
        ('저장과 계산의 차이', '구조체 선언이 값들을 조회·초기화하거나 CPU 동질성을 계산하는 것은 아닙니다. 배열 뒤 1바이트가 있다고 전체 sizeof를 무조건 81로 고정하면 안 되며 ABI 정렬과 끝 padding을 고려해야 합니다. 전체 멤버와 의존성을 설명했고 실제 공유 페이지 초기화나 hotplug 정책을 검증한 것으로 표시하지 않습니다.')
    ],
    questions=[
        ('현재 all_cpu_hwprobe_values 배열의 원소 수는?', '10개이다', '9개이다', 'key 0부터 9까지를 인덱스로 사용하므로 MAX_KEY+1 원소입니다.'),
        ('homogeneous_cpus 선언만으로 모든 CPU의 값이 동일함이 보장되는가?', '아니다. 그 사실을 게시할 저장 필드일 뿐이다', '그렇다. 구조체가 CPU feature를 자동 통일한다', '데이터 표현과 이를 계산·게시하는 구현은 다릅니다. 필드를 올바르게 채우는 책임은 다른 코드에 있습니다.')
    ]
)]
