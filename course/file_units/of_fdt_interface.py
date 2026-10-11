"""Whole-file flattened device-tree boot interfaces and configuration gates."""
ROWS = [dict(
    path='include/linux/of_fdt.h', title='FDT 헤더: 부팅 스캔·콜백·초기 데이터의 인터페이스',
    intro='FDT 마커, 일반 unflatten 선언, 부팅 전용 API와 제한적인 비활성 stub 전체를 분석합니다.',
    principle='직렬화된 트리의 핸들과 동적 노드 포인터, 초기화 단계의 데이터 수명은 구분해야 합니다.',
    use='콜백과 문맥 포인터, 포인터 간접 참조, 부팅 단계 분리와 조건부 선언을 학습합니다.',
    area='부팅 · FDT · 직렬화 · 함수 포인터 · 메모리 수명',
    sections=[
        ('마커와 어셈블리 경계', 'GPL-2.0과 저작권 표기 뒤 _LINUX_OF_FDT_H guard가 있고 types, init, errno 헤더를 포함합니다. OF_DT_HEADER는 0xd00dfeed 마커 상수입니다. 이 정의 뒤의 #ifndef __ASSEMBLY__가 C 선언 영역을 감쌉니다. 상수 정의 자체가 입력 blob의 헤더나 길이를 검증하는 것은 아닙니다.'),
        ('일반 평탄 트리 지원', 'CONFIG_OF_FLATTREE가 정의되면 device_node를 전방 선언하고 of_fdt_unflatten_tree를 선언합니다. 인수는 const unsigned long *blob, device_node *dad, device_node **mynodes이며 반환은 void *입니다. 노드 이중 포인터 인수는 호출자 쪽 노드 포인터를 전달하는 인터페이스지만 이 선언만으로 반환 메모리의 소유권, 할당 방식, 실패 시 정리 규칙을 확정할 수 없습니다. 주석은 임의의 장치 트리를 임의 시점에 다루는 용도라고 구분합니다.'),
        ('초기 전역과 링크 심볼', 'dt_root_addr_cells와 dt_root_size_cells는 int __initdata extern이고 initial_boot_params는 void * extern입니다. __initdata 표기는 두 셀 수 변수가 초기화 데이터 영역에 배치됨을 나타내며 initial_boot_params에는 이 표기가 없습니다. __dtb_start와 __dtb_end는 extern char 배열 선언입니다. 여기에 실제 배열 내용이나 길이는 정의되지 않습니다. 같은 블록의 of_flat_dt_translate_address는 unsigned long node에서 u64를 반환하고 of_fdt_limit_memory는 int limit을 받는 void 선언입니다.'),
        ('두 가지 스캔 콜백', 'CONFIG_OF_EARLY_FLATTREE 블록의 of_scan_flat_dt는 node, uname, depth, data를 받는 int 콜백과 void *data를 받습니다. of_scan_flat_dt_subnodes는 시작 node와 node,uname,data를 받는 콜백 및 data를 받으며 콜백에 depth 인수가 없습니다. data는 호출자의 문맥을 전달하는 통로이고 함수 포인터 타입은 각 콜백의 인수 개수를 구분합니다. 방문 순서와 콜백 반환값에 따른 중단 규칙은 이 헤더의 선언만으로 결정할 수 없습니다.'),
        ('평탄 트리 조회', 'of_get_flat_dt_subnode_by_name은 unsigned long node와 이름에서 int를 반환합니다. of_get_flat_dt_prop은 노드와 이름, int *size 출력 인수에서 const void *를 반환합니다. is_compatible은 int, get_flat_dt_root는 unsigned long, get_flat_dt_phandle은 uint32_t 결과입니다. 이 unsigned long 노드 인수들을 device_node *와 같은 형태로 취급하면 안 됩니다. 속성 데이터의 형식·엔디언 변환·수명은 반환 타입만으로 보장되지 않습니다.'),
        ('부팅 정보와 예약 메모리', 'early_init_dt_scan_chosen은 char *cmdline에서 int, scan_memory는 인수 없이 int를 반환합니다. usable_mem_range 검사, reserved_mem 스캔, FDT 자체 예약은 각각 별도의 void API이고 chosen_stdout 스캔은 int API입니다. add_memory_arch는 u64 base와 size를 받습니다. dt_mem_next_cell은 int s와 const __be32 **cellp에서 u64를 반환하므로 셀 포인터 자체를 전달하는 이중 포인터 형태입니다. 실제 포인터 전진과 셀 해석 방법은 구현을 읽어 확인해야 합니다.'),
        ('스캔 진입점과 머신 매칭', 'early_init_dt_scan_root는 int, early_init_dt_scan과 verify는 void *params에서 bool, scan_nodes는 void 결과입니다. 머신 이름은 const char *로 반환됩니다. of_flat_dt_match_machine은 const void *default_match와 const char * const ** 인수를 받는 get_next_compat 콜백을 받으며 콜백과 상위 함수 모두 const void *를 반환합니다. 콜백을 통해 호환 문자열 목록을 전달하는 인터페이스이며 여기에는 매칭 점수나 후보 우선순위 알고리즘이 없습니다.'),
        ('트리 전개와 초기 장치 트리', 'unflatten_device_tree와 unflatten_and_copy_device_tree는 인수 없는 void 선언입니다. early_init_devtree는 void *를 받고 early_get_first_memblock_info는 void *와 phys_addr_t *를 받습니다. 이름에 copy가 있다는 이유만으로 할당 크기나 복사 범위를 이 헤더에서 확정할 수 없습니다. 일반 of_fdt_unflatten_tree와 부팅 전용 진입점들은 서로 다른 CONFIG 블록에 놓입니다.'),
        ('비활성 stub은 일부만 존재', 'EARLY_FLATTREE가 없으면 usable_mem_range, reserved_mem 스캔, reserve_self, 두 unflatten 함수는 빈 함수입니다. chosen_stdout는 -ENODEV, 머신 이름은 NULL을 반환합니다. 그 외 early scan, verify, 속성 조회, 셀 읽기, early_init_devtree 등의 대체 선언은 이 else에 없습니다. 모든 활성 API가 동일 이름의 무동작 stub을 갖는다고 일반화하면 안 됩니다. 두 설정의 실제 허용 조합은 별도 Kconfig 제약도 확인해야 합니다.'),
        ('전체 검토 범위', '헤더 guard와 어셈블리 경계, 마커, FLATTREE 블록의 선언·전역, EARLY_FLATTREE의 모든 API와 일곱 stub을 대조했습니다. 직렬화된 표현과 전개된 노드 타입, 부팅 단계의 데이터 수명, 콜백 문맥 전달을 관련 CS 주제로 연결했습니다. 실제 부팅, FDT 파싱 실행, 메모리 예약 또는 구성별 커널 빌드는 수행하지 않았습니다.')
    ], questions=[
        ('전체 평탄 트리 스캔과 하위 노드 스캔의 콜백 인수 차이는?', '전체 스캔 콜백에만 depth가 있다', '둘 다 정확히 같은 네 인수다', 'of_scan_flat_dt 콜백은 node,uname,depth,data이고 subnodes 콜백은 node,uname,data입니다. 서로 다른 함수 포인터 타입을 이름만 보고 같은 것으로 가정하면 안 됩니다.'),
        ('OF_DT_HEADER 상수를 정의한 것만으로 입력 FDT 검증이 이루어지는가?', '아니다. 상수 정의와 실행 시 검증은 별개다', '그렇다. 매크로가 모든 blob의 길이와 구조를 검사한다', '0xd00dfeed라는 값의 정의에는 검사 코드가 없습니다. 헤더에는 별도로 early_init_dt_verify 선언이 있지만 그 구현도 여기에는 없습니다.'),
        ('EARLY_FLATTREE 비활성에서 모든 부팅 API가 stub을 갖는가?', '아니다. 이 else에는 일곱 함수만 정의된다', '그렇다. scan,verify,속성 조회까지 모두 자동 생성된다', '사용 가능 범위 확인, stdout, reserved_mem, reserve_self, 머신 이름, 두 unflatten만 대체 본문을 가집니다. 조건부 선언의 부재와 무동작 구현의 존재는 다릅니다.'),
        ('__initdata가 이 헤더에서 명시된 전역은?', 'dt_root_addr_cells와 dt_root_size_cells', 'initial_boot_params와 __dtb_start만', '두 int 선언에 __initdata가 직접 붙습니다. 다른 심볼에도 같은 수명 표기가 있다고 추정하지 말고 선언 위치를 확인해야 합니다.'),
        ('부팅 전용 지원이 없을 때 chosen_stdout와 머신 이름 함수의 결과는?', '-ENODEV와 NULL', '둘 다 정상 문자열 포인터', 'stdout 스캔은 int 오류를, 이름 조회는 포인터 부재를 반환합니다. 서로 다른 결과 타입과 실패 표현을 구분해야 합니다.'),
        ('dt_mem_next_cell의 cellp 타입은 왜 단일 셀 값과 다른가?', 'const __be32 포인터 자체를 가리키는 이중 포인터다', '이미 CPU 엔디언으로 변환된 u64 값 하나다', 'const __be32 **는 셀 데이터 포인터를 간접 참조하는 타입이고 결과 u64와도 다릅니다. 실제 포인터 갱신 여부와 변환 절차는 선언만으로 확정하지 않고 구현을 확인해야 합니다.')
    ]
)]
