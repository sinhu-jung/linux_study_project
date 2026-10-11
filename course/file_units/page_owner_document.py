"""Whole page owner guide with v6.12 parser discrepancies documented."""
ROWS = [dict(
    path='Documentation/mm/page_owner.rst',
    title='Page owner 사용법: 할당 이력 집계와 문서·도구 대조',
    intro='수집 목적, 초기 페이지의 한계, stack 집계와 정렬·선택 문법을 문서 전체에서 학습합니다.',
    principle='할당 횟수와 기본 페이지 수를 구분하고, 문서의 옵션을 동일 버전 실행 도구의 파서와 대조합니다.',
    use='메모리 누수와 대량 할당 원인을 찾을 때 진단 자료를 수집하고 집계 기준을 선택합니다.',
    area='할당 추적 · 집계 · 다중 키 정렬 · 관측 비용 · 문서 검증',
    sections=[
        ('문서 전체와 진단 목적', 'Introduction, Usage, STANDARD FORMAT SPECIFIERS로 구성됩니다. 할당 시 call stack과 order 등의 정보를 페이지별로 보존하여 누수나 메모리 대량 사용자를 조사합니다. 이력에서 할당 지점을 찾는 것과 그 할당이 실제 누수라고 증명하는 것은 다릅니다. gfp 정보로 단편화 통계를 얻는 용도와 stack별 현재 할당 기본 페이지 수를 보는 용도도 소개합니다.'),
        ('Tracepoint 방식과 비용', '문서는 할당·해제 trace를 이용하면 사용자 프로그램 시작 전 버퍼 덮어쓰기를 막을 크기와 지속적인 수집이 필요하고 시스템 동작에 영향을 줄 수 있다고 설명합니다. page owner는 메모리에 이력을 보관하는 접근입니다. 비활성 시 소유 정보 저장 메모리가 필요 없고 allocator hotpath의 unlikely 분기 비용이 작다고 설명하지만 빌드된 코드 크기까지 0이라는 뜻은 아닙니다. 활성 시 기록 비용이 없다는 주장도 아닙니다.'),
        ('활성화와 초기 할당의 한계', 'page owner를 포함한 커널에서 page_owner=on 부팅 옵션으로 활성화합니다. sparse memory에서는 page extension 초기화 전에 이미 할당된 페이지가 있어 초기화 때 조사해 할당 상태를 표시합니다. 이는 원래 정확한 call stack을 복원한다는 뜻이 아닙니다. 문서의 2GB x86-64 VM에서 13,343개를 발견한 사례는 특정 측정 예이며 모든 시스템의 고정 수치가 아닙니다.'),
        ('사용 절차와 파일', 'tools/mm에서 make page_owner_sort로 helper를 빌드하고 기능을 켠 뒤 조사할 workload를 실행합니다. debugfs의 page_owner_stacks/show_stacks를 읽으면 stack과 nr_base_pages를 볼 수 있고 page_owner를 덤프한 뒤 page_owner_sort 입력파일 출력파일 형식으로 분석합니다. 이 학습은 절차를 설명하며 현재 호스트 커널을 재부팅하거나 옵션을 변경한 것은 아닙니다.'),
        ('Stack 집계와 threshold', 'show_stacks 예제는 stack별 기본 페이지 수 16 또는 20,824를 보여 줍니다. count_threshold에 7000을 쓰는 예는 큰 집계를 추리는 용도입니다. 관련 stack_print를 대조하면 nr_base_pages가 1 미만이거나 threshold보다 작을 때 숨기므로 정확히 7000이면 통과합니다. 단위는 할당 호출 수나 바이트가 아닌 기본 페이지 수입니다. 실제 메모리 크기를 계산하려면 기본 페이지 크기를 곱해야 합니다.'),
        ('PFN으로 시작 위치 지정', '문서는 전체 PFN 덤프와 fseek(fp,pfn_start,SEEK_SET) 예를 제시합니다. 구현의 read_page_owner는 파일 위치 0이면 min_low_pfn, 아니면 위치 자체를 PFN으로 사용하고 다음 위치를 pfn+1로 저장합니다. 일반적인 바이트 offset 파일이나 kpageflags의 PFN*8 레코드와 다릅니다. 같은 proc/debugfs 계열이라는 이유로 단위를 통일해서 해석하지 않습니다.'),
        ('기본 집계의 정보 손실', 'page_owner_sort는 PFN 줄을 제외하고 나머지 블록을 모아 order를 추출하며 동일한 집계 조건의 횟수와 페이지 수를 합칩니다. 따라서 정렬 결과만으로 모든 원래 PFN을 복원할 수는 없습니다. 예를 들어 order 0 블록 10개는 기본 페이지 10개이고 order 3 블록 2개는 16개여서 횟수 순위와 페이지 수 순위가 다를 수 있습니다.'),
        ('짧은 정렬 옵션 전체', '문서는 -a 할당 시각, -m 총 메모리, -p pid, -P tgid, -n task 이름, -r 해제 시각, -s stack, -t 횟수 기본 정렬을 열거합니다. v6.12 소스의 getopt_long 짧은 옵션 문자열은 admnpstP여서 -r은 포함하지 않습니다. 문서에 있는 -f 해제된 블록 제외 옵션도 파서에 없습니다. 이 두 항목을 지원되는 명령으로 안내하지 않습니다.'),
        ('다중 정렬 문법과 키', '--sort는 [+|-]key를 쉼표로 이어 쓰며 기본 방향은 오름차순입니다. 예제 --sort=n,+pid,-tgid는 이름, pid 오름차순, tgid 내림차순의 우선순위를 뜻하고 --sort=at는 할당 시각을 뜻합니다. 표는 p/pid, tg/tgid, n/name, st/stacktrace, T/txt, ft/free_ts, at/alloc_ts, ator/allocator를 나열합니다. 실제 get_arg_type과 parse_sort_args에는 ft/free_ts가 없어 해당 문서 항목은 v6.12 도구와 맞지 않습니다. 짧은 옵션의 기본 정렬과 --sort의 기본 방향을 혼동하지 않습니다.'),
        ('Cull은 집계 기준', '--cull은 동일하다고 묶을 필드를 선택합니다. 구현은 선택 필드를 비교해 정렬한 뒤 같으면 횟수와 페이지 수를 합칩니다. 문서의 stacktrace 및 st,pid,name 예는 이 개념을 보여 줍니다. 표의 p/pid, tg/tgid, n/name, st/stacktrace, ator/allocator는 파서의 비교 조건과 연결됩니다. 하지만 f/free는 파서에서 인정되지 않아 문서 예 --cull=n,f도 그대로 사용할 수 없습니다. 본문의 multi-letter라는 표현만으로 단축 키를 금지한다고 읽지 않습니다.'),
        ('선택과 집계는 별개', '--pid, --tgid, --name은 쉼표로 나열한 값에 해당하는 블록을 선택합니다. 문서는 --pid=1, --tgid=1,2,3, --name name1,name2를 예로 듭니다. 선택은 어떤 입력을 남길지, cull은 남은 입력 중 무엇을 같은 그룹으로 묶을지, sort는 결과를 어떤 순서로 보여 줄지의 문제입니다. 세 단계의 역할을 한 종류의 필터로 뭉뚱그리지 않습니다.'),
        ('CS와 검증 범위', '이력 보존과 event stream 수집의 절충, 집계에 따른 정보 손실, 가중치가 다른 빈도 통계, 다중 키 비교와 그룹화, 버전별 문서·구현 차이를 학습합니다. 이 문서 전체와 관련 파서 일부를 대조했으며 page_owner.c나 page_owner_sort.c 전체를 완료한 것으로 계산하지 않습니다. 이 호스트에서 Linux debugfs 수집을 실행 검증한 것도 아닙니다.')
    ],
    questions=[
        ('order 0 블록 10개와 order 3 블록 2개 중 기본 페이지 수가 더 많은 것은?', 'order 3 블록 2개로 총 16페이지이다', '호출 횟수가 많은 order 0 블록 10개이다', '각 order k 블록은 2^k 기본 페이지입니다. 횟수와 메모리 크기 기준의 순위는 다를 수 있습니다.'),
        ('초기화 전 할당 페이지를 나중에 표시하면 원래 할당 stack도 정확히 복원되는가?', '아니다. 할당 여부 보완과 정확한 원래 이력 복원은 다르다', '그렇다. 모든 과거 호출을 완전히 재구성한다', '문서는 초기 페이지가 정확한 owner 정보를 갖는다는 뜻은 아니라고 명시합니다. 사례의 페이지 수도 특정 시스템의 측정치입니다.'),
        ('문서의 --cull=n,f를 v6.12 도구에서 그대로 신뢰해도 되는가?', '아니다. 파서는 f/free cull 키를 지원하지 않는다', '그렇다. 문서 예제는 어떤 버전에서도 반드시 동작한다', 'get_arg_type과 parse_cull_args를 대조하면 지원 키에 free가 없습니다. 문서와 동일 버전의 구현 사이에도 차이가 있을 수 있습니다.'),
        ('count_threshold=7000일 때 현재 기본 페이지 수가 정확히 7000인 stack은?', '출력 대상이다', '7000을 초과하지 않으므로 제외된다', '비교는 nr_base_pages<threshold입니다. threshold와 같은 값은 제외 조건에 들어가지 않습니다.'),
        ('page_owner 파일에서 시작 PFN을 fseek할 때 kpageflags처럼 8을 곱하는가?', '아니다. 이 인터페이스의 위치는 PFN 자체로 해석된다', '그렇다. 모든 페이지 정보 파일은 항상 PFN*8이다', 'read_page_owner는 0을 특별 처리하고 나머지 위치를 PFN으로 사용합니다. 파일별 위치 단위 계약을 확인해야 합니다.')
    ]
)]
