"""Whole pinned x86 PAT guide and its tables."""
ROWS = [dict(
    path='Documentation/arch/x86/pat.rst',
    title='PAT 지침 전체: 캐시 속성 alias와 드라이버 책임',
    intro='페이지 단위 캐시 속성,API별 용도,MTRR 조합,진단과 초기화 표를 해설합니다.',
    principle='같은 물리 메모리의 여러 가상 매핑이 모순된 캐시 속성을 갖지 않도록 요청과 최종 속성 및 수명을 함께 관리합니다.',
    use='앞서 읽은 memtype 구간 트리와 iomap의 속성 예약을 문서의 드라이버 계약에 연결합니다.',
    area='PAT · MTRR · alias · RAM과MMIO · 메모리 타입 · 초기화 구성',
    sections=[
        ('도입과 두 메커니즘', 'GPL-2.0 문서입니다. PAT는 페이지 단위 속성,MTRR은 물리 범위의 타입 설정을 제공하며 상호 보완적이라고 설명합니다. PAT는 MTRR처럼 제한된 수의 범위 레지스터에 의존하지 않는 유연성이 있지만 페이지 테이블·메모리 자원이 무한하다는 뜻은 아닙니다. 동일 물리 메모리의 alias 일관성이 핵심입니다.'),
        ('기본 모드 이름', '문서의 주요 표는 WB write-back,UC uncached,WC write-combined,WT write-through,UC- uncached minus를 소개합니다. UC와UC-를 같은 문자열로 취급하지 않습니다. 앞서 내부 cattr_name에 WP도 있었지만 이 도입 표가 모든 구현 enum 값을 나열하는 것은 아닙니다.'),
        ('API 표 읽기', '표는 RAM,ACPI 등,Reserved/Holes 세 범주를 나눕니다. --는 제안하지 않는 용도이며 일부는 커널이 강제하고 일부는 이 문서 시점에서 강제하지 않을 수 있다고 주석이 설명합니다. 빈칸을 자동 성공이나 모든 경우의 런타임 거부로 해석하지 않습니다. 문서의 reserve_memtype/free_memtype 이름은 앞서 읽은 헤더의 memtype_reserve/free와 이름 순서가 달라 실제 호출 추적은 소스 이름을 기준으로 합니다.'),
        ('Ioremap 표', '표에서 ioremap은ACPI와예약 영역에UC-,ioremap_cache는WB,ioremap_uc는UC를 제시하고RAM 용도에는--입니다. ioremap_wc와wt는예약/홀 영역의WC와WT이며ACPI도--입니다. 이 표는 캐시 속성 요청의 의도된 용도를 설명하며 기존 alias로 인해 실제 속성이 더 제한될 수 있다는 후속 설명까지 함께 읽어야 합니다.'),
        ('RAM 속성 변경 표', 'RAM에는 set_memory_uc/wc/wt를 사용하고 set_memory_wb와 짝지어 원복하도록 설명합니다. uc 항목의 표기 속성은UC-입니다. set_memory_wb 자체가UC-를 만든다는 뜻이 아니라 변경·복원 쌍을 같은 행에 나타낸 것입니다. 일반 RAM과PCI BAR의 API를 교환 가능하다고 가정하지 않습니다.'),
        ('PCI 사용자 인터페이스', 'sysfs resource는UC-,prefetch resource_wc는WC를 제시합니다. proc PCI는PCIIOC_WRITE_COMBINE이 없으면UC-,있으면WC로 표기합니다. 이것을 모든 resource가write-combining에 적합하다는 허가로 확대하지 않습니다.'),
        ('Dev mem 표', '/dev/mem read/write는WB/WC/UC- 가능성을 나열합니다. mmap의SYNC는UC-,비SYNC이며alias가 있으면기존alias의WB/WC/UC-를 따릅니다. alias가 없고MTRR WB이면WB,예약 영역에서MTRR이WB가 아니면UC-를 제시합니다. 이 표의RAM 열은--이며 주소별 권한·접근 가능성 전체를 보증하는 표가 아닙니다.'),
        ('사용자 공간에 I/O 내보내기', '문서는 mmap에서 pgprot_noncached 또는 pgprot_writecombine으로 속성을 정하고 io_remap_pfn_range/remap_pfn_range/vmf_insert_pfn으로 매핑하는 흐름을 설명합니다. 뒤 단계가 타입을 추적해 충돌을 방지한다고 서술합니다. 문서의 memtype list라는 표현은 앞서 본 실제 구간 트리 구현과 구분합니다.'),
        ('RAM 내보내기의 추가 책임', 'RAM을 내보낼 때는 앞 단계로 set_memory_uc 또는wc를 수행하고 페이지 사용을 추적하며 free pool에 반환하기 전에 set_memory_wb로 복원해야 한다고 명시합니다. 사용자 매핑만 지우면 물리 페이지의 캐시 속성까지 자동으로 원복됐다고 가정하지 않습니다.'),
        ('MTRR 사용 방향', '문서는 mtrr_add 대신 arch_phys_wc_add를 권장하며 PAT 활성 시스템에서 후자는no-op이라고 설명합니다. 적용 범위는 먼저ioremap_wc/set_memory_wc로WC 매핑 또는PAT 속성이 준비돼 있어야 합니다. 과거/향후 전환 문구는 이 고정 버전 지침이며 현재 모든 드라이버의 마이그레이션 완료 주장으로 사용하지 않습니다.'),
        ('혼합 영역의 예외적 전략', 'UC를 유지할 영역과WC가 필요한 영역이 섞인 장치에서ioremap_uc 후선별 set_memory_wc를 고려할 수 있다고 설명하지만,효과가implementation-defined라 권장하지 않으며 크기 제약이 있는 최후 수단의 문맥입니다. 문서의 예외를 일반적인 기본 설정으로 제시하지 않습니다.'),
        ('WC MTRR 조합 표 전체', 'MTRR=WC일 때 표의WB 요청은비PAT/PAT 모두WC입니다. WC 요청은비PAT에서WC*·PAT에서WC,UC- 요청은비PAT에서WC*·PAT에서UC,UC 요청은둘 다UC입니다. 별표는구현 정의이며비권장입니다. 동일 요청 이름이PAT 유무에 따라다른 결과를 낼 수 있다는 표를읽고,이를모든 MTRR 타입의 전체 조합표로확대하지 않습니다.'),
        ('기존 alias와 최종 타입', '문서는ioremap 및sysfs/proc PCI 접근이기존alias 때문에더제한적인 타입을돌려줄 수있다고 설명합니다. 기존uncached 매핑이있으면새 ioremap_wc가uncached가될 수있는 예를듭니다. 요청 성공만으로반드시WC라고 가정하지않고 속성추적의 계약을확인합니다.'),
        ('진단 인터페이스', 'CONFIG_DEBUG_FS에서debugfs를마운트하고 x86/pat_memtype_list를읽는 예제가있습니다. 출력은물리 범위와접근캐시 타입을나열하며예시 주소는실제 사용자시스템의 측정치가아닙니다. debugpat 부팅옵션은dmesg에더상세한진단을남기는방법입니다. 이번작업에서호스트에마운트하거나부팅설정을변경하지않습니다.'),
        ('초기화 표의 정상·CPU 비지원', '표는MTRR과PAT CPU 기능이모두E이면MTRR→PAT init으로Enabled·OS 설정이라설명합니다. MTRR E/PAT D는Disabled·MSR표시없음,MTRR D/PAT E는disable·BIOS 유지,둘 다D는Disabled·표시없음입니다. 이표의BIOS는펌웨어설정유지라는의미이며PAT 기능이없다는문자와동일하지않습니다.'),
        ('부팅옵션과 빌드 구성', 'nopat(np)이있으면PAT E에서도Disabled·BIOS 유지,PAT D에서는Disabled·MSR표시없음입니다. CONFIG_X86_PAT가없는!P/E의경우MTRR E나D 모두Disabled·BIOS 유지이고,CONFIG_MTRR도없는!M,!P/E는MTRR stub→PAT disable입니다. 문서는Linux가WC·WT 지원을위해PAT MSR을갱신해야하며Xen은guest용WC를활성화한다고덧붙입니다. 표를임의의가상화환경전체의증명으로확장하지않습니다.'),
        ('CS 연결과 범위', '물리메모리alias의일관성,요청정책과유효속성,자원반납전상태복원,하드웨어기능·빌드구성·부팅옵션의조합,관측용debug 목록을학습합니다. 이문서전체의해설과원본대응검사는실제PAT MSR이나장치캐시동작의실행검증이아닙니다.')
    ],
    questions=[
        ('표의 --는무엇을뜻하는가?', '해당API에제안하지않는용도이며강제여부는항목에따라다르다', '모든경우무조건성공한다', '문서주석이일부는강제하고일부는그렇지않을수있다고설명합니다. 범주별사용지침과실행결과를구분합니다.'),
        ('WC로바꾼RAM을free pool에돌려주기전필요한복원은?', 'set_memory_wb이다', '아무복원없이사용자주소만잊으면된다', '문서는페이지사용추적과WB 복원을드라이버책임으로설명합니다. 매핑주소수명과물리페이지속성수명은별개입니다.'),
        ('WC MTRR 표에서UC- 요청의비PAT/PAT 결과는?', '각각WC*와UC이다', '둘다항상WB이다', '별표WC는구현정의·비권장입니다. PAT 유무에따른동일요청의효과차이를보여줍니다.'),
        ('기존uncached alias가있는데ioremap_wc가성공하면반드시WC인가?', '아니다.더제한적인uncached일수있다', '그렇다.함수이름이최종모드를보증한다', '문서는이경우를명시적인예로듭니다. 속성충돌방지를위한예약·조정경로와연결됩니다.'),
        ('pat_memtype_list의출력주소는무슨주소인가?', '물리주소범위이다', '항상사용자프로세스가상주소이다', '문서는물리범위와해당범위접근속성을나열한다고설명합니다. 예시출력을현재호스트실측으로표현해서는안됩니다.'),
        ('PAT CPU 지원이있어도nopat이면초기화표상상태는?', 'Disabled이며BIOS 설정을유지한다', '항상Enabled로OS 설정을쓴다', 'CPU 기능만으로활성화가결정되지않습니다. 부팅옵션과빌드구성도함께읽어야합니다.')
    ]
)]
