"""Complete page-table check wrapper header and design documentation."""
ROWS = [dict(
    path='include/linux/page_table_check.h',
    title='페이지 테이블 검사 hook: 빌드 구성과 static key',
    intro='할당·해제·엔트리 변경 지점에서 검사 구현으로 들어가는 아홉 wrapper 전체를 해설합니다.',
    principle='검사 기능을 빌드에 포함하는 것과 런타임에 검사 경로를 활성화하는 것은 별개입니다.',
    use='페이지 테이블 변경 경로의 선택적 진단 기능과 비용 제어를 이해합니다.',
    area='조건부 컴파일 · static key · 인터페이스 분리 · 불변식 검사',
    sections=[
        ('전체 범위', 'GPL-2.0, 저작권과 작성자 주석, guard 뒤 PAGE_TABLE_CHECK 분기가 있습니다. 활성 분기는 jump_label.h를 포함하고 static key와 page_ext_operations를 extern으로 선언하며 내부 함수 선언과 inline wrapper를 제공합니다. 비활성 분기는 같은 외부 호출 이름의 빈 inline 함수들입니다. 이 헤더가 모든 매핑 검사 알고리즘을 구현하지는 않습니다.'),
        ('Disabled라는 key의 방향', 'page_table_check_disabled는 struct static_key_true입니다. 모든 활성 wrapper는 static_branch_likely(&page_table_check_disabled)가 참이면 즉시 반환하고 거짓이면 내부 검사 함수를 호출합니다. key가 참이라는 사실은 검사가 활성이라는 뜻이 아닙니다. 관련 구현의 초기화는 검사를 켤 때 이 disabled key를 disable합니다. 헤더에는 key를 변경하는 본문이 없습니다.'),
        ('Alloc과 free의 공통 검사', 'page_table_check_alloc과 free는 page와 unsigned int order를 받아 둘 다 __page_table_check_zero로 전달합니다. 이름의 zero를 메모리 내용 memset으로 해석하면 틀립니다. 해당 구현을 대조하면 페이지별 anon/file 매핑 카운터가 0인지 확인하고 0이 아니면 BUG_ON합니다. order는 검사할 2의 거듭제곱 페이지 범위와 연결되며 이 wrapper가 페이지를 할당하거나 해제하지는 않습니다.'),
        ('세 clear wrapper', 'pte_clear, pmd_clear, pud_clear는 mm 포인터와 각각의 엔트리 값을 받아 대응 __page_table_check_*_clear에 전달합니다. 엔트리 포인터가 아닌 값이 입력이라는 점을 확인합니다. 이 wrapper 본문에는 실제 페이지 테이블 엔트리에 0을 쓰거나 TLB를 flush하는 코드가 없습니다. 변경 지점의 검사 hook과 변경 작업 자체를 구분합니다.'),
        ('Set wrapper의 모양', 'ptes_set은 mm, pte_t 포인터 ptep, 새 pte 값, unsigned int nr를 전달합니다. pmd_set과 pud_set은 각각 mm, 엔트리 포인터, 새 값만 전달하고 nr 인자는 없습니다. PTE 묶음 인터페이스의 범위를 PMD/PUD 함수에도 임의로 추가해서 설명하지 않습니다. 이 wrapper들은 공통 static key 검사 뒤 인자를 그대로 내부 함수에 넘깁니다.'),
        ('PTE 범위 clear', 'pte_clear_range는 mm, unsigned long addr, pmd_t 값을 받습니다. 주소 끝이나 nr를 받는 형태가 아닙니다. 대응 내부 함수에 세 인자를 전달할 뿐 이 헤더 안에서 PTE 배열을 순회하지 않습니다. 실제 범위와 매핑 조건은 구현에서 확인해야 합니다.'),
        ('기능 미포함 분기', 'CONFIG_PAGE_TABLE_CHECK가 없으면 alloc, free, 세 clear, ptes_set, pmd_set, pud_set, clear_range의 아홉 함수 모두 void 빈 본문입니다. 이 분기에 __ 함수 선언, static key, operations 선언을 다시 제공하지 않습니다. 호출 경로의 소스 형태를 유지하되 기능을 없애는 방식입니다. 빈 inline 함수라는 사실만으로 인자로 전달한 C 표현식의 부수효과까지 언어 차원에서 사라진다고 단정하지 않습니다.'),
        ('CS 연결과 검증 범위', '빌드 시 기능 제거와 런타임 빠른 분기, 검사 hook과 실제 쓰기 분리, 전달 인자의 타입과 범위, 할당 시 불변식 검사를 학습합니다. mm/page_table_check.c의 일부 구현 대조는 그 파일 전체 완료로 계산하지 않으며, 모든 아키텍처의 hook 연결을 시험한 것도 아닙니다.')
    ],
    questions=[
        ('page_table_check_disabled key가 참이면 wrapper는 무엇을 하는가?', '즉시 반환하여 내부 검사를 건너뛴다', '검사 기능이 활성이라고 판단하여 내부 함수를 호출한다', '조건은 disabled key에 대한 static_branch_likely입니다. 변수 이름과 분기의 방향을 함께 읽어야 합니다.'),
        ('alloc/free가 부르는 __page_table_check_zero는 무엇을 확인하는가?', '관련 페이지의 매핑 카운터가 0인지 확인한다', '페이지 데이터 바이트를 전부 0으로 덮어쓴다', '해당 구현은 anon_map_count와 file_map_count에 BUG_ON 검사를 수행합니다. zero라는 이름만으로 초기화 함수라고 추정하면 안 됩니다.'),
        ('pte_clear wrapper가 실제 PTE 값을 0으로 쓰는가?', '아니다. 엔트리 값을 내부 검사 함수에 전달한다', '그렇다. 이름에 clear가 있으므로 직접 PTE를 지운다', '인자는 pte_t 값이며 wrapper에는 엔트리 저장 명령이 없습니다. 호출 지점의 실제 변경과 진단을 구분합니다.'),
        ('nr 인자를 받는 set wrapper는?', 'page_table_check_ptes_set이다', '세 set wrapper가 모두 nr를 받는다', 'PTE 묶음 함수에만 unsigned int nr가 명시됩니다. PMD/PUD는 엔트리 포인터와 값만 추가로 받습니다.')
    ]
), dict(
    path='Documentation/mm/page_table_check.rst',
    title='페이지 테이블 검사 설계: 잘못된 공유와 독립적인 검증',
    intro='검사 목적, 중복 매핑 규칙표, 활성화 조건과 MM 상태에 대한 독립성을 문서 전체에 걸쳐 해설합니다.',
    principle='일부 잘못된 공유를 동기적으로 발견하는 검증은 메모리 안전성 전체를 증명하는 것과 다릅니다.',
    use='페이지 매핑 관련 커널 오류를 진단할 때 검사 범위와 비용을 이해합니다.',
    area='메모리 격리 · 접근 권한 · 불변식 · 독립 검증 · 진단 비용',
    sections=[
        ('문서 구성과 목적', 'GPL-2.0 표시 뒤 Introduction, Double mapping detection logic, Enabling, Implementation notes의 네 부분이 있습니다. 사용자 공간이 페이지에 접근 가능하도록 PTE·PMD 등을 추가하는 시점에 검사하여 일부 메모리 손상을 방지하는 기능입니다. 모든 메모리 오류·커널 버그를 포괄하는 검증이라고 설명하지 않습니다.'),
        ('동기적인 진단과 비용', '대부분의 검출된 손상에서는 커널을 중단시키며, 잘못된 매핑 시점에 발견하면 훨씬 뒤에 발생하는 손상 증상보다 원인을 찾기 쉽다고 설명합니다. 추가 성능·메모리 비용이 있어 기본적으로 꺼져 있으며 강화 효과와 비용을 비교하여 활성화합니다. 모든 위반이 동일한 경고나 동일한 복구 경로로 처리된다는 뜻은 아닙니다.'),
        ('엔트리 플래그 조합 검사', '문서는 userfaultfd의 write-protect 비트와 writable 플래그의 불법 조합을 경고하는 용도를 설명합니다. 즉시 데이터가 훼손되지 않아도 읽기 전용이어야 하는 내용을 쓸 수 있게 되면 나중에 손상될 수 있습니다. 상태 조합의 오류와 실제 데이터 쓰기로 발생하는 결과 사이에 시간 차이가 있습니다.'),
        ('규칙표의 다섯 행', 'Anonymous→Anonymous 읽기 매핑은 허용, 읽기/쓰기 매핑은 금지입니다. Anonymous→Named와 Named→Anonymous는 권한과 무관하게 금지, Named→Named는 권한과 무관하게 허용입니다. 이 표는 이미 존재하는 매핑과 새 매핑 사이의 검사 규칙이며 anonymous 메모리에 대한 모든 쓰기를 전역 금지한다는 뜻은 아닙니다. Named는 여기서 매핑 분류이며 파일 이름 문자열을 비교하는 알고리즘은 제시하지 않습니다.'),
        ('활성화 절차', 'PAGE_TABLE_CHECK=y로 빌드하고 page_table_check=on으로 부팅합니다. 해당 플랫폼에 ARCH_SUPPORTS_PAGE_TABLE_CHECK가 있어야 구성할 수 있습니다. PAGE_TABLE_CHECK_ENFORCED를 빌드하면 별도 부팅 매개변수 없이 기본 활성화를 얻을 수 있다고 설명합니다. 이 문서만으로 모든 아키텍처가 기능을 지원한다고 추정하지 않습니다.'),
        ('ENFORCED 이름의 해석', '관련 v6.12 구현을 대조하면 ENFORCED는 초기 enabled 값에 반영되고 early parameter는 kstrtobool로 같은 값을 파싱합니다. 문서의 별도 매개변수 없이 활성화한다는 설명을 어떤 명령행 설정으로도 절대 변경할 수 없다는 주장으로 확대하지 않습니다. 문서 학습 중 구현을 대조한 부분이며 구현 파일 전체 완료를 뜻하지는 않습니다.'),
        ('VMA와 독립된 상태', '검사는 VMA 정보를 의도적으로 사용하지 않고 제한된 struct page 정보 외에는 MM 상태에 의존하지 않으려 한다고 설명합니다. 기존 MM과 별도의 상태 기계를 두어 잘못된 사용자 페이지 공유를 확인합니다. 검증 대상의 동일한 잘못된 상태를 그대로 믿으면 독립 검증 효과가 약해진다는 설계 관점과 연결할 수 있습니다.'),
        ('EXCLUSIVE_SYSTEM_RAM 의존 이유', '이 구성이 없으면 /dev/mem으로 임의 물리 메모리를 매핑할 수 있고 사용자 매핑이 남은 동안 페이지가 anonymous에서 named 등으로 바뀌어 검사에 손상으로 나타날 수 있다고 설명합니다. EXCLUSIVE_SYSTEM_RAM이 있어도 I/O 페이지의 /dev/mem 매핑은 허용될 수 있지만 항상 named로 취급되어 표의 논리를 깨지 않는다고 합니다. 이를 모든 I/O 매핑을 차단한다는 뜻으로 읽지 않습니다.'),
        ('CS 연결과 범위', '접근 권한과 별칭, 상태 전이의 허용 표, 별도 검증 상태 기계, 오류를 원인 가까이에서 발견하는 동기 진단, 비용과 관측 범위를 학습합니다. 문서와 해당 버전 소스 대조는 커널을 실제로 오류 매핑으로 중단시키는 실행 시험과는 구분합니다.')
    ],
    questions=[
        ('규칙표에서 Named→Named의 중복 매핑은?', '권한과 무관하게 허용한다', '쓰기 권한이 있으면 무조건 금지한다', '표의 마지막 행은 Any/Allow입니다. anonymous 중복 쓰기 제한을 모든 유형에 동일하게 적용하지 않습니다.'),
        ('PAGE_TABLE_CHECK=y만 설정하면 문서의 기본 활성화 절차가 끝나는가?', '아니다. 보통 page_table_check=on 또는 ENFORCED 설정이 필요하다', '그렇다. 빌드 포함과 활성화는 항상 같다', '문서는 빌드 옵션과 부팅 옵션을 나누어 설명하고 ENFORCED를 대안으로 제시합니다.'),
        ('VMA 정보를 사용하지 않으려는 설계 이유는?', '검증 대상 MM 상태에 지나치게 의존하지 않는 별도 검사를 두기 위해서다', '페이지 테이블 검사가 어떤 페이지 정보도 읽지 않기 때문이다', '문서는 제한된 struct page 정보는 사용한다고 명시합니다. 독립성은 모든 입력이 없다는 뜻이 아닙니다.'),
        ('EXCLUSIVE_SYSTEM_RAM은 문서에서 모든 I/O /dev/mem 매핑을 금지하는가?', '아니다. 허용될 수 있는 I/O 페이지는 named로 취급한다고 설명한다', '그렇다. I/O 예외는 전혀 없다', '마지막 문단은 I/O 매핑 가능성과 named 분류가 검사 논리와 양립하는 이유를 다룹니다.')
    ]
)]
