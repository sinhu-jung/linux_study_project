"""Whole PAT reservation interval tree and associated interfaces."""
ROWS = [dict(
    path='arch/x86/mm/pat/memtype_interval.c',
    title='PAT 구간 트리 전체: 겹침 충돌과 예약 축소',
    intro='물리 구간별 캐시 속성을 augmented rbtree에 저장하고 겹치는 예약의 모드를 조정합니다.',
    principle='겹침 자체는 허용하되 같은 물리 주소의 alias들이 모순된 캐시 속성을 갖지 않도록 검사합니다.',
    use='앞서 iomap_create_wc에서 요청 모드가 최종 모드와 달라질 수 있었던 이유를 구간 검사 알고리즘으로 학습합니다.',
    area='구간 트리 · 증강 red-black tree · 충돌 검사 · 오류 포인터 · 자료구조 불변식',
    sections=[
        ('전체 구조와 잠금 계약', 'GPL-2.0·작성자·헤더 포함 뒤 interval helper 생성,정적 cached root,검색·충돌·삽입·삭제·조회·debug 복사 함수를 구현합니다. 주석은 충돌 캐시 속성이 CPU cache corruption을 유발할 수 있으며 memtype_lock이 트리를 보호한다고 설명합니다. 이 파일의 함수 내부에 그 lock 획득·해제는 없으므로 호출 계층의 동기화 계약이 필요합니다.'),
        ('반열린 구간의 변환', 'memtype의 start는 그대로 사용하고 interval_end는 end-1을 반환합니다. 예약은[start,end)이지만 generic interval tree의 검색 끝은 포함형입니다. INTERVAL_TREE_DEFINE는 rb 링크,u64 끝값,subtree_max_end 보강값과 이 accessor를 사용합니다. 빈 구간이나 end0의 유효성 검사를 이 accessor가 추가하지 않습니다.'),
        ('정확 일치와 끝 일치', 'memtype_match는[start,end-1]과 겹치는 항목을 순회합니다. EXACT는 양쪽 경계가 같은 항목,END는 기존 start가 요청 start보다 작고 end가 같은 항목을 찾습니다. 임의의 중간 구간이나 시작부분 삭제를 지원하는 일반 split 검색이 아닙니다.'),
        ('충돌 없는 시작', 'memtype_check_conflict는 found_type을 요청 모드로 시작합니다. 겹침이 없으면 성공하고 출력 newtype이 있으면 요청 모드를 기록합니다. 겹침 첫 항목이 요청과 다르고 newtype이 NULL이면 즉시 -EBUSY입니다. 출력 인자 제공 여부가 단순 결과 저장 외에 허용되는 모드 조정에도 영향을 줍니다.'),
        ('모드 조정과 다중 겹침', '첫 겹침을 받아들이면 found_type을 그 항목의 type으로 바꿉니다. 이후 모든 겹침이 이 type과 같아야 성공합니다. newtype이 있더라도 서로 다른 모드의 두 기존 구간을 한 번에 받아들이지는 않습니다. 실패하면 현재 task 이름·pid·범위·모드 이름을 로그에 남기고 -EBUSY를 반환합니다.'),
        ('숫자 구간 예제', '기존[100,200)은WB,[200,300)은WC라면 두 기존 항목은 경계만 맞닿고 겹치지 않습니다. 새[150,250)은 둘과 겹쳐 일관된 found_type을 정할 수 없어 실패합니다. 반면 새[120,180)에 출력 type 포인터를 제공하면 요청이 달라도 기존WB로 조정할 수 있습니다. 실제 물리 범위의 정렬 등은 상위 계층 조건과 함께 봅니다.'),
        ('삽입 순서', 'memtype_check_insert는 먼저 충돌 검사를 수행하고 오류면 그대로 반환합니다. 성공하고 ret_type이 있으면 entry_new->type을 반환된 모드로 갱신한 뒤 interval_insert합니다. 노드의 메모리를 여기서 할당하지 않으며 같은 범위·같은 모드 항목을 반드시 하나로 병합하는 코드도 없습니다.'),
        ('삭제의 우선순위', 'memtype_erase는 정확 일치를 먼저 찾습니다. 없으면 끝 일치를 찾고 둘 다 없으면 ERR_PTR(-EINVAL)입니다. 겹치는 여러 항목이 가능하므로 정확한 예약을 우선 지우려는 구조입니다. NULL만 검사해서 성공·실패를 판단하면 오류 포인터 계약을 놓칩니다.'),
        ('완전 삭제와 축소', 'start까지 같으면 interval_remove 후 그 노드 포인터를 반환하며 메모리 해제는 여기서 하지 않습니다. 끝 일치로 찾았으면 노드를 제거하고 end=start로 줄인 뒤 재삽입하고 NULL을 반환합니다. 예를 들어 기존[100,300)에 요청[200,300)이면[100,200)을 유지합니다. 끝값과 보강값의 트리 불변식을 갱신하려고 제거·재삽입합니다.'),
        ('페이지 폭 조회', 'memtype_lookup(addr)는[addr,addr+PAGE_SIZE-1]과 첫 겹침을 반환합니다. 단일 byte 점 조회나 addr의 페이지 내림 정렬을 수행하지 않습니다. 일치 항목이 없으면 generic iterator의 NULL을 반환하며 복수 겹침 모두를 리스트로 반환하는 API는 아닙니다.'),
        ('Debug 복사', 'CONFIG_DEBUG_FS에서 memtype_copy_nth_element는1부터 세며[0,ULONG_MAX] 검색으로 pos번째 겹침 항목을 찾습니다. 찾으면 구조체 전체를 *entry_out에 복사하고0,못 찾으면1입니다. rb 링크까지 포함한 복사이므로 출력용 snapshot을 독립된 새 트리 노드로 간주하면 안 됩니다.32비트 ULONG_MAX 검색을 모든 가능한 u64 주소 전체라고 과장하지 않습니다.'),
        ('CS 연결과 범위', '구간 끝 포함 규칙 변환,보강 트리 검색,한 요청이 여러 예약을 가로지를 때의 일관성,출력 인자에 따른 정책,세 갈래 삭제 결과,출력용 snapshot을 학습합니다. source 검사와 학습 빌드는 실제 PAT 설정·잠금 경쟁·모든 구간 조합의 실행 검증이 아닙니다.')
    ],
    questions=[
        ('[100,200)과[200,300)은 이 예약 표현에서 겹치는가?', '아니다.첫 구간의 포함형 끝은199이다', '그렇다.200이 양쪽에 포함된다', 'interval_end는end-1입니다. 반열린 예약 범위를 닫힌 검색 범위로 변환합니다.'),
        ('newtype 포인터가 있으면 서로 다른 두 기존 모드와의 겹침도 허용되는가?', '아니다.모든 겹침의 모드가 같아야 한다', '그렇다.항상 새 요청 모드로 덮어쓴다', '첫 항목의 type을 found_type으로 정한 뒤 이후 항목이 다르면 실패합니다. 기존 노드의 type을 수정하는 코드도 없습니다.'),
        ('기존[100,300)에서[200,300)을 지우면 결과와 반환값은?', '기존 노드는[100,200)으로 줄고 NULL이다', '항상 노드 전체를 free하고 오류이다', '끝 일치 축소는 remove,end 갱신,insert 후NULL입니다. 노드 전체 제거는 포인터 반환,검색 실패는ERR_PTR입니다.'),
        ('memtype_lookup은 addr 한 byte만 검색하는가?', '아니다.addr부터 PAGE_SIZE 폭을 검색한다', '그렇다.다른 주소는 확인하지 않는다', '검색 범위는addr부터addr+PAGE_SIZE-1입니다. 별도의 페이지 시작 정렬도 없습니다.'),
        ('이 파일의 삽입 함수가 memtype_lock을 직접 획득하는가?', '아니다.주석의 보호 계약은 호출 계층과 맞춰야 한다', '그렇다.모든 interval 함수가 자동 잠근다', '본문에 lock 연산이 없습니다. 자료구조 자체의 안전성과 외부 동기화 계약을 구분합니다.')
    ]
), dict(
    path='arch/x86/mm/pat/memtype.h',
    title='PAT 내부 타입 전체: 구간 노드와 비활성 대체 함수',
    intro='캐시 예약 노드의 필드,진단 이름,CONFIG_X86_PAT별 인터페이스를 읽습니다.',
    principle='비활성 구성의 성공형 반환값이 실제 자료구조 변경이나 출력값 갱신을 의미하지 않을 수 있습니다.',
    use='memtype_interval.c의 node layout과 debug 출력을 연결합니다.',
    area='구조체 · 증강 트리 · enum 표시 · 조건부 stub · 진단',
    sections=[
        ('진단과 노드', 'GPL-2.0·guard 뒤 pat_debug_enable extern과 조건부 pr_info의 dprintk를 정의합니다. memtype는u64 start,end,subtree_max_end,캐시 mode type,rb_node를 가집니다. subtree_max_end는 트리 검색용 보강 정보이며 별도 예약의 끝 주소가 아닙니다.'),
        ('모드 이름', 'cattr_name은 UC/UC_MINUS/WB/WC/WT/WP를 각각 uncached/uncached-minus/write-back/write-combining/write-through/write-protected 문자열로 반환합니다. 다른 값은 broken입니다. 이 함수가 캐시 모드나 페이지 접근 권한을 변경하는 것은 아닙니다.'),
        ('PAT 활성 선언', 'CONFIG_X86_PAT이면 check_insert,erase,lookup,copy_nth_element를 extern 선언합니다. 구현에서 debug 복사는 DEBUG_FS 조건도 있으므로 선언만으로 모든 조합에서 함수를 사용할 수 있다고 추측하지 않습니다.'),
        ('PAT 비활성 본문', '비PAT에서는 insert와 copy_nth가0,erase와lookup은NULL을 반환하는 inline stub입니다. insert는 node를 트리에 넣지 않고new_type도 기록하지 않습니다. copy_nth도 out을 채우지 않습니다. 실제 구현의 성공0 의미를 stub에서 출력 초기화 보장으로 잘못 확장하지 않습니다.'),
        ('CS 연결', '자료와 인덱스 링크의 결합,보강 metadata,진단용 enum-to-string,조건부 기능 제거,출력 인자 계약을 학습합니다. 헤더가 생성한 타입과 stub만으로 실제 예약이 등록된 것으로 세지 않습니다.')
    ],
    questions=[
        ('비PAT copy_nth stub이0을 반환하면 out도 채웠는가?', '아니다.대입 없이0만 반환한다', '그렇다.유효한 첫 노드를 복사한다', 'stub 본문은return 0뿐입니다. 활성 구현의 성공 경로와 출력 부작용을 구별해야 합니다.'),
        ('알 수 없는 캐시 mode를 cattr_name에 넘기면?', 'broken 문자열이다', '자동으로WC 모드로 수정한다', 'default 반환은진단 문자열입니다. 이 함수는 입력 상태를 변경하지 않습니다.')
    ]
), dict(
    path='arch/x86/include/asm/memtype.h',
    title='x86 memtype 공개 헤더 전체: PAT 기능과 예약 API',
    intro='PAT 초기화·상태 조회,물리 범위 예약·해제,캐시 모드 변환 선언을 구분합니다.',
    principle='선언은 인자·출력·반환 타입을 제공하며 정책과 구현의 구성별 동작은 별도로 확인해야 합니다.',
    use='iomap과 PAT 내부 구간 트리 사이의 public 인터페이스를 연결합니다.',
    area='API 선언 · 물리 범위 · 출력 인자 · 캐시 모드 · PFN',
    sections=[
        ('구조와 초기화', 'GPL-2.0·guard·types와 pgtable_types 포함 뒤 pat_enabled bool 조회,pat_bp_init과pat_cpu_init void 초기화 선언을 제공합니다. 이 헤더에는CONFIG_X86_PAT 분기나 함수 본문이 없습니다.'),
        ('일반 예약 API', 'memtype_reserve는u64 start/end,요청 mode,반환 mode 포인터를 받아int를 반환합니다. memtype_free는u64 범위를 받아int입니다. memtype_kernel_map_sync는base,size,mode를 받고int를 반환합니다. 범위 경계 인자와 크기 인자의 차이를 유지하며 구현의 오류 코드·잠금은 별도입니다.'),
        ('I/O 예약 API', 'memtype_reserve_io는resource_size_t start/end와mode 포인터를 받아int를 반환합니다. memtype_free_io는같은 범위에void를 반환합니다. 일반 free가int라는 사실을IO free에도 그대로 적용하지 않습니다.'),
        ('추가 조회와 변환', 'pat_pfn_immune_to_uc_mtrr는unsigned long pfn을 받아bool,x86_has_pat_wp는bool,pgprot2cachemode는pgprot_t를 받아page_cache_mode를 반환합니다. PFN과byte 주소를 구분하며 이름만으로 예외 정책의 모든 조건을 만들어 설명하지 않습니다.'),
        ('CS 연결과 범위', '공개 선언과 내부 구현,타입에 나타나는 주소 단위,요청·반환 mode,void와오류 상태 반환을 학습합니다. 이 헤더를 읽는 것만으로PAT 지원 상태나 실제 예약 성공을 확정할 수 없습니다.')
    ],
    questions=[
        ('memtype_free와 memtype_free_io의 반환형은?', '각각int와void이다', '둘 다동일한int이다', '공개 선언이 다릅니다. 상위 호출에서 반환 상태를 확인할 수 있는지 구분해야 합니다.'),
        ('pgprot2cachemode는 무엇을 반환하는가?', 'enum page_cache_mode이다', '새로 할당한 가상주소이다', '보호값을 받아캐시 mode로 변환하는 선언입니다. 매핑 할당 API와 다릅니다.')
    ]
)]
