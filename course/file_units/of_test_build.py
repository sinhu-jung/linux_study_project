"""Whole-file OF root tests and local test build configuration."""
ROWS = [dict(
    path='drivers/of/of_test.c', title='OF 루트 테스트: 경로 조회와 전역 포인터의 서로 다른 증거',
    intro='두 테스트와 공통 초기화,suite 등록 및 메타데이터 전체를 분석합니다.',
    principle='조회 API의 성공과 전역 상태의 존재는 별도 관찰이며,둘의 동일성까지 자동 증명하지 않습니다.',
    use='테스트 전제,skip,참조 획득·반환과 assertion 범위를 학습합니다.',
    area='장치 트리 · 테스트 설계 · 참조 카운팅 · 초기화',
    sections=[
        ('파일과 첫 테스트', 'GPL-2.0 파일은 module,OF,KUnit test와 내부 OF 헤더를 포함합니다. found_by_path는 of_find_node_by_path("/")를 호출하고 결과가 오류나 NULL이 아닌지 EXPECT한 뒤 of_node_put합니다. 검색으로 얻은 참조를 반환하며 트리 전체를 순회하거나 속성 내용을 검사하지 않습니다.'),
        ('전역 루트 검사', 'populates_of_root는 전역 of_root가 오류나 NULL이 아닌지만 EXPECT합니다. 이 경로에서 새 참조를 획득하지 않으므로 별도 put도 없습니다. 주석은 전역 접근이 제거되면 이 테스트도 제거하라고 적습니다. 첫 테스트의 조회 결과와 of_root 주소가 같은지 비교하는 assertion은 없습니다.'),
        ('초기화와 skip', 'of_dtb_test_init은 of_root_kunit_skip을 호출하고 CONFIG_OF_EARLY_FLATTREE가 비활성이면 kunit_skip합니다. 정상 진행 경로에서 0을 반환합니다. 공통 init이 전제를 확인하므로 주석의 항상 populated라는 표현을 모든 구성에 대한 무조건적인 실행 증거로 확대하면 안 됩니다.'),
        ('등록 구조', 'case 배열은 경로 조회와 전역 루트 검사 두 항목 뒤 빈 sentinel을 둡니다. of_dtb suite는 name,test_cases,init을 지정하며 kunit_test_suites로 등록합니다. 설명은 OF API용 KUnit 테스트,license는 GPL입니다. 별도 teardown callback이나 root 생성 코드는 없습니다.'),
        ('전체 범위와 검증 한계', '두 테스트,case 배열,init,suite와 등록·메타데이터 전체를 확인했습니다. 노드 이름 비교 테스트는 이 파일에 없습니다. DTB가 언제 로드되는지,모든 하위 노드가 정확한지,동시 조회가 안전한지를 직접 검사하지 않습니다. 실제 커널 KUnit 실행 결과가 아닌 소스의 검사 범위를 설명합니다.')
    ], questions=[
        ('조회 테스트에서 of_node_put을 호출하는 이유는?', '검색으로 얻은 노드 참조를 반환하기 위해서다', '전역 트리를 무조건 삭제하기 위해서다', '참조 반환과 트리 삭제는 다른 동작입니다. 조회 API가 돌려준 참조 수명을 맞춥니다.'),
        ('두 테스트가 검색 결과와 of_root의 포인터 동일성을 검사하는가?', '아니다. 각 결과의 유효성만 따로 검사한다', '그렇다. EXPECT_PTR_EQ로 두 주소를 비교한다', '실제 assertion은 NOT_ERR_OR_NULL입니다. 두 관찰이 통과했다고 작성되지 않은 비교까지 수행된 것은 아닙니다.'),
        ('EARLY_FLATTREE가 비활성이면 공통 init은?', '해당 테스트를 skip한다', '빈 루트를 직접 만들어 강제 통과시킨다', 'init에는 생성 코드가 없으며 kunit_skip을 호출합니다. 지원 조건 충족과 테스트 성공은 다릅니다.')
    ]
), dict(
    path='drivers/of/Makefile', title='OF 빌드 연결: 기능별 object와 overlay 데이터의 결합',
    intro='모든 object 선택과 중첩 조건,테스트 복합 object를 분석합니다.',
    principle='소스가 존재하는 것과 특정 구성에서 빌드 입력으로 선택되는 것은 다릅니다.',
    use='Kbuild 변수 확장,조건부 구성과 C·DTBO 링크 단위를 학습합니다.',
    area='빌드 시스템 · 조건부 컴파일 · 링킹 · 테스트 구성',
    sections=[
        ('기본 object', 'GPL-2.0 Makefile은 obj-y를 base.o,cpu.o,device.o,module.o,platform.o,property.o로 설정합니다. 이 디렉터리가 처리되는 문맥에서 기본 object 목록이며 이 파일만으로 상위 디렉터리 진입 조건까지 정의하지는 않습니다.'),
        ('트리 표현과 동적 기능', 'OF_KOBJ는 kobj.o,OF_DYNAMIC은 dynamic.o,OF_FLATTREE는 fdt.o와 empty_root.dtb.o,OF_EARLY_FLATTREE는 fdt_address.o,OF_PROMTREE는 pdt.o를 선택합니다. 빈 root DTS가 C 코드와 함께 빌드 데이터 object로 연결되는 지점이 여기입니다.'),
        ('주소와 기타 기능', 'OF_ADDRESS는 address.o,OF_IRQ는 irq.o,OF_UNITTEST는 unittest.o,OF_RESERVED_MEM은 of_reserved_mem.o,OF_RESOLVE는 resolver.o,OF_OVERLAY는 overlay.o,OF_NUMA는 of_numa.o에 대응합니다. 이 매핑은 각 기능의 알고리즘을 구현하는 코드가 아니라 빌드 대상 선택입니다.'),
        ('Kexec의 중첩 조건', 'CONFIG_KEXEC_FILE ifdef 안에 CONFIG_OF_FLATTREE ifdef가 있고 둘 다 만족하면 obj-y에 kexec.o를 더합니다. 둘 중 하나만 만족하면 이 대입은 실행되지 않습니다. ifdef 검사와 일반 C #ifdef를 혼동하지 말고 Make 변수의 문맥으로 읽어야 합니다.'),
        ('KUnit과 overlay 복합 object', 'CONFIG_KUNIT는 of_kunit_helpers.o,OF_KUNIT_TEST는 of_test.o,OF_OVERLAY_KUNIT_TEST는 overlay-test.o를 선택합니다. overlay-test-y는 overlay_test.o와 kunit_overlay_test.dtbo.o 두 입력입니다. 하이픈이 있는 최종 object 이름과 밑줄이 있는 C object 이름은 다릅니다. 테스트 코드와 내장 overlay 심볼 데이터를 같은 복합 단위로 결합합니다.'),
        ('하위 테스트 데이터와 범위', '마지막 OF_UNITTEST 선택은 unittest-data/ 하위 디렉터리를 추가합니다. 전체 대입과 두 ifdef를 모두 확인했습니다. Kconfig가 보장하는 dependency나 DTBO 생성 규칙 자체는 다른 파일의 책임이며 이 파일을 읽었다고 실제 빌드가 통과한 것은 아닙니다.')
    ], questions=[
        ('overlay-test.o를 구성하는 입력은?', 'overlay_test.o와 kunit_overlay_test.dtbo.o', 'overlay.c 하나만', 'overlay-test-y에 두 입력을 명시합니다. 실행 코드와 내장 데이터가 함께 필요합니다.'),
        ('empty_root.dtb.o가 선택되는 직접 조건은?', 'CONFIG_OF_FLATTREE', 'CONFIG_OF_KOBJ만', 'FLATTREE 줄은 fdt.o와 empty_root.dtb.o를 함께 나열합니다.'),
        ('kexec.o가 obj-y에 추가되는 조건은?', 'KEXEC_FILE과 OF_FLATTREE의 중첩 ifdef가 모두 만족한다', '둘 중 하나만 있으면 항상 추가된다', '대입은 두 조건 블록 안에 있습니다. OR가 아닌 중첩 조건입니다.')
    ]
), dict(
    path='drivers/of/.kunitconfig', title='OF KUnit 구성 조각: 네 가지 요청과 최종 설정의 차이',
    intro='파일의 네 설정 전체를 빌드 대상과 연결해 해설합니다.',
    principle='구성 조각은 필요한 설정을 요청하며 전체 커널 설정과 의존성 해결을 대신하지 않습니다.',
    use='테스트 재현 입력과 구성·빌드·실행의 단계 구분을 학습합니다.',
    area='커널 구성 · 테스트 재현성 · 빌드 입력',
    sections=[
        ('기반 두 설정', 'CONFIG_KUNIT=y와 CONFIG_OF=y를 요청합니다. 테스트 프레임워크와 DeviceTree 기반 기능의 선택이며 파일에는 다른 값이나 주석,별도 실행 명령이 없습니다.'),
        ('테스트 두 설정', 'CONFIG_OF_KUNIT_TEST=y와 CONFIG_OF_OVERLAY_KUNIT_TEST=y를 요청합니다. 대응 Makefile에서 각각 of_test.o와 overlay-test.o를 선택하는 설정입니다. 일반 OF_UNITTEST 설정은 이 파일에 직접 적혀 있지 않습니다.'),
        ('전체 범위와 한계', '네 줄 전체를 확인했습니다. OVERLAY와 EARLY_FLATTREE 등 모든 관련 dependency를 여기서 직접 나열하지는 않습니다. 최종 값은 Kconfig 처리와 전체 설정에서 확인해야 하며 이 파일이 존재한다는 사실은 테스트 실행 성공이나 모든 OF 테스트 선택을 증명하지 않습니다.')
    ], questions=[
        ('이 조각은 CONFIG_OF_UNITTEST=y도 직접 요청하는가?', '아니다. 해당 줄은 없다', '그렇다. 모든 OF 테스트 설정을 나열한다', '파일에는 KUNIT,OF,OF_KUNIT_TEST,OF_OVERLAY_KUNIT_TEST 네 줄뿐입니다.'),
        ('구성 조각만 읽고 테스트가 실행되어 통과했다고 판단할 수 있는가?', '아니다. 최종 설정·빌드·실행 증거가 별도로 필요하다', '그렇다. =y가 실행 성공을 의미한다', '설정 요청은 실행 결과와 다릅니다. 각 단계의 증거를 구분해야 합니다.')
    ]
)]
