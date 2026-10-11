"""Complete proc page count, flags, and cgroup implementation."""
ROWS = [dict(
    path='fs/proc/page.c',
    title='물리 페이지 관측 파일: mapcount·flags·cgroup 출력 전체',
    intro='PFN별 u64 레코드를 사용자 버퍼로 전달하는 세 읽기 경로와 공개 플래그 합성, proc 등록을 해설합니다.',
    principle='페이지의 매핑 수·상태·cgroup 식별자는 서로 다른 관측값이며 오류 반환과 이미 진행한 파일 위치 갱신도 별도로 추적해야 합니다.',
    use='kpagecount, kpageflags, kpagecgroup을 읽는 분석 도구의 단위와 경계 조건을 이해합니다.',
    area='procfs · 바이너리 ABI · 사용자 메모리 복사 · 비트 변환 · 관측 일관성',
    sections=[
        ('전체 파일 구성', 'GPL-2.0과 메모리·proc·uaccess 관련 include 뒤 레코드 크기 상수, 최대 PFN 계산, mapcount 읽기, 플래그 합성과 읽기, MEMCG 조건부 cgroup 읽기, 초기화가 있습니다. KPMSIZE=sizeof(u64), KPMMASK=KPMSIZE-1, KPMBITS=KPMSIZE*BITS_PER_BYTE입니다. KPMBITS는 정의되지만 이 파일의 나머지 본문에서는 쓰이지 않습니다. 세 인터페이스 모두 한 PFN마다 한 u64이며 가상 주소를 직접 인덱스로 쓰지 않습니다.'),
        ('덤프 가능한 최대 PFN', 'get_max_dump_pfn은 SPARSEMEM이면 max_pfn을 PAGES_PER_SECTION 배수로 올림하고 아니면 그대로 반환합니다. 주석은 초기 section의 memmap이 section 끝까지 채워지고 online으로 표시될 수 있어 해당 descriptor를 조사하도록 범위를 넓힌다고 설명합니다. 이 범위 전체가 실제 사용 가능한 RAM이라고 결론내리면 안 됩니다. idle sysfs 구현의 max_pfn 제한과도 차이가 있습니다.'),
        ('세 읽기 함수의 공통 입구', '각 함수는 *ppos를 unsigned long src로 받고 PFN=src/KPMSIZE로 계산합니다. src와 count가 모두 8바이트 정렬이어야 하며 아니면 EINVAL입니다. 시작이 max_dump_pfn*8 이상이면 0이고, 유효한 시작에서 끝을 넘는 요청은 남은 크기로 줄입니다. 이 함수들은 임의의 1바이트 부분 레코드 읽기를 지원하지 않습니다. 산술의 타입은 실제 본문에 따른 것이며 범용 큰 정수 연산으로 바꾸어 설명하지 않습니다.'),
        ('Mapcount 출력', 'kpagecount_read는 PFN마다 pfn_to_online_page를 호출합니다. page가 없으면 mapcount=0이고 있으면 page_folio와 해당 page를 folio_precise_page_mapcount에 전달합니다. 여기서 출력하는 값은 매핑 수이며 page_count 참조 수나 그 페이지를 사용한 프로세스 수를 그대로 출력하는 것이 아닙니다. precise helper의 내부 구현은 이 파일에 없으므로 큰 folio의 계산 방식을 여기서 임의로 단순화하지 않습니다.'),
        ('사용자 복사와 부분 진행 오류', 'put_user가 성공한 뒤에만 PFN과 출력 포인터를 증가시키고 남은 count에서 8을 뺍니다. 실패하면 ret=-EFAULT로 루프를 나갑니다. 루프 후 *ppos에는 성공한 레코드의 바이트 수를 더하지만 ret가 오류이면 성공 바이트 수로 덮어쓰지 않습니다. 예를 들어 두 레코드 성공 뒤 세 번째 복사가 실패하면 위치는 16바이트 전진하면서 반환은 EFAULT입니다. 부분 성공을 항상 양수로 반환한다고 추정하면 틀립니다.'),
        ('비트 위치 변환 helper', 'kpf_copy_bit는 u64 kflags에서 kbit를 추출하여 ubit로 이동합니다. ((kflags>>kbit)&1)<<ubit이므로 내부 비트 번호와 외부 번호가 달라도 대응시킬 수 있습니다. 왼쪽 입력이 u64라는 점은 32번 이후 진단 비트를 만들 때 중요합니다. 이 helper는 모든 내부 플래그를 한 번에 외부로 복사하지 않습니다.'),
        ('NULL과 매핑 상태 합성', 'stable_page_flags는 NULL page이면 NOPAGE 비트만 반환하여 메모리 구멍과 플래그 0인 페이지를 구분합니다. 그 밖에는 folio->flags와 mapping을 읽고 page_mapped(page)로 MMAP을, mapping의 ANON 비트로 ANON을 합성합니다. KSM은 anonymous 분기 안에서 mapping의 KSM 비트를 확인합니다. 이 값들은 단순히 같은 번호의 page->flags를 복사한 결과가 아닙니다.'),
        ('Compound와 큰 페이지 분류', '입력 page가 folio의 첫 page이면 PG_head를 COMPOUND_HEAD로 복사하고 그렇지 않으면 TAIL을 설정합니다. hugetlb이면 HUGE, 그 외 large이면서 large_rmappable이면 THP, 그 다음 huge zero folio이면 ZERO_PAGE와 THP, 마지막으로 zero folio이면 ZERO_PAGE입니다. 이 순서의 else-if 구조를 보존해야 하며 THP 주석은 PMD 크기에만 한정하지 않는다고 명시합니다. 평범한 작은 folio의 첫 page라고 항상 COMPOUND_HEAD가 되는 것은 아닙니다.'),
        ('Buddy·offline·page table·slab', 'PageBuddy이면 BUDDY를 설정하고 아니어도 page_count가 0이며 is_free_buddy_page이면 BUDDY를 설정합니다. PageOffline과 PageTable은 각각 OFFLINE과 PGTABLE로, folio_test_slab은 SLAB으로 연결합니다. 상단 주석은 고차 페이지의 내부 buddy/slab 표식이 head에만 있는 점을 경고하지만 실제 공개 값은 이런 helper를 통해 합성하므로 주석만 보고 tail 출력이 항상 0이라고 단정하지 않습니다.'),
        ('Idle과 일반 상태', 'PAGE_IDLE_FLAG && 64BIT이면 저장해 둔 folio flags에서 PG_idle을 복사하고 그 외에는 folio_test_idle을 호출합니다. 이 함수는 idle sysfs 읽기처럼 역매핑을 순회해 PTE young을 갱신하지 않습니다. LOCKED, DIRTY, UPTODATE, WRITEBACK, LRU, REFERENCED, ACTIVE, RECLAIM은 대응하는 내부 비트에서 복사합니다. folio flags 한 번의 읽기와 이후 여러 helper의 결과를 조합하므로 전체 페이지 시스템의 한 시점 스냅샷을 만드는 코드라고 설명할 수 없습니다.'),
        ('Swap·회수 금지·hardware poison', 'SWAPCACHE는 PG_swapbacked와 PG_swapcache가 둘 다 있어야 설정하고 SWAPBACKED는 별도로 복사합니다. UNEVICTABLE과 MLOCKED도 각각 복사합니다. MEMORY_FAILURE이면 HUGE가 설정된 경우 folio flags에서 HWPOISON을, 아니면 입력 page->flags에서 복사합니다. head와 개별 page 중 어디의 상태를 읽는지가 조건에 따라 다릅니다.'),
        ('내부 진단 비트와 미설정 항목', 'RESERVED, OWNER_2, PRIVATE, PRIVATE_2, OWNER_PRIVATE, ARCH는 각각 PG_reserved, owner_2, private, private_2, owner_priv_1, arch_1을 복사합니다. ARCH_2와 ARCH_3은 대응 CONFIG_ARCH_USES_PG_ARCH_*일 때만 복사합니다. 공개·내부 헤더에 이름이 있다고 자동으로 출력되는 것은 아니며 이 본문에는 ERROR나 SOFTDIRTY를 설정하는 경로가 없습니다.'),
        ('Flags 읽기와 장치 메모리 한계', 'kpageflags_read는 온라인 page를 찾아 stable_page_flags 결과를 put_user합니다. 세 읽기 함수 모두 ZONE_DEVICE 지원을 위해 실제 초기화된 memmap 식별이 필요하다는 TODO를 포함합니다. 이 제한을 무시하고 모든 장치 메모리 PFN을 완전하게 지원한다고 설명하지 않습니다. 루프마다 성공적으로 한 레코드를 처리한 뒤 cond_resched로 재스케줄 기회를 줍니다.'),
        ('Cgroup 출력', 'MEMCG가 활성일 때 kpagecgroup_read와 ops가 컴파일됩니다. page가 있으면 page_cgroup_ino(ppage), 없으면 0을 u64로 출력합니다. 값은 cgroup inode 식별 정보이며 PID나 메모리 사용량이 아닙니다. 인접 PFN들이 같은 cgroup에 속한다고 압축하지 않고 각각 한 레코드를 기록합니다. helper 호출 이상의 소속 계산 본문은 이 파일에 없습니다.'),
        ('Proc 등록과 실패 처리 차이', '세 proc_ops는 PROC_ENTRY_PERMANENT, mem_lseek, 각 read callback을 지정하며 write callback은 없습니다. proc_page_init은 루트 proc 아래 kpagecount와 kpageflags, MEMCG이면 kpagecgroup을 S_IRUSR 권한으로 생성합니다. proc_create 반환값을 검사하지 않고 항상 0을 반환하며 fs_initcall로 등록합니다. 앞서 읽은 page_idle_init의 sysfs 오류 검사와 같은 실패 처리라고 설명하면 틀립니다.'),
        ('CS 연결과 검증 범위', '고정 크기 바이너리 레코드, PFN 인덱싱, 내부 표현을 외부 ABI로 변환하는 계층, 사용자 복사 실패와 부분 진행 상태, 조건부 기능과 진단 정보의 한계를 학습합니다. 본문 전체를 대조했지만 실제 커널의 메모리 hotplug·경쟁·사용자 fault 환경을 실행 검증한 것은 아닙니다.')
    ],
    questions=[
        ('/proc/kpagecount에서 PFN 100의 레코드는 어느 바이트 위치인가?', '800바이트 위치이다', '100바이트 위치이다', '각 PFN은 u64 8바이트 레코드 하나입니다. src/8이 PFN이므로 PFN*8 위치를 사용합니다.'),
        ('SPARSEMEM 구성에서 덤프 최대 PFN은 항상 max_pfn과 같은가?', '아니다. section 크기의 배수로 올림한다', '그렇다. 모든 구성에서 그대로 반환한다', '초기 section의 memmap을 조사하도록 PAGES_PER_SECTION 단위로 round_up합니다. 범위 확대를 실제 사용 가능한 RAM 증가로 해석하면 안 됩니다.'),
        ('두 레코드 복사 성공 후 다음 put_user가 실패하면 반환과 위치 갱신은?', 'EFAULT를 반환하고 위치는 16바이트 전진한다', '16을 반환하고 오류는 무조건 숨긴다', 'out은 성공한 레코드만큼 전진하고 위치 갱신은 오류와 무관하게 수행합니다. ret가 음수이면 성공 바이트 수로 바꾸는 if (!ret)에 들어가지 않습니다.'),
        ('작은 folio의 첫 page라는 이유만으로 COMPOUND_HEAD가 설정되는가?', '아니다. 해당 경로에서 PG_head를 복사한다', '그렇다. 첫 page이면 무조건 설정한다', '첫 page 여부는 분기를 선택할 뿐입니다. 설정 값은 kpf_copy_bit를 통해 PG_head에서 가져옵니다.'),
        ('kpagecount가 출력하는 것은 page 참조 카운터인가?', '아니다. folio_precise_page_mapcount를 이용한 매핑 수이다', '그렇다. page_count 결과를 그대로 출력한다', 'mapcount와 수명 관리용 참조 수는 다른 개념입니다. page_count는 이 파일의 별도 buddy 판별 조건에서 등장합니다.'),
        ('proc_page_init이 proc_create 실패를 검사해 오류를 반환하는가?', '아니다. 반환값을 검사하지 않고 0을 반환한다', '그렇다. 첫 실패에서 중단하고 오류를 전달한다', '실제 초기화 본문에는 생성 호출들과 return 0만 있습니다. 다른 등록 함수의 관례를 이 코드에 덧붙여 설명하면 안 됩니다.')
    ]
)]
