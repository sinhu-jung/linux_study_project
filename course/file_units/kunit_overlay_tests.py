"""Whole-file overlay regression tests and their two DeviceTree fixtures."""
ROWS = [dict(
    path='drivers/of/overlay_test.c', title='Overlay 회귀 테스트: live node와 platform device의 생성·제거',
    intro='세 테스트와 검색 callback,suite 및 메타데이터 전체를 분석합니다.',
    principle='트리 노드 참조와 장치 참조는 별개이며 cleanup 이후에는 다시 조회하여 상태를 관찰해야 합니다.',
    use='트리 검색,참조 수명,테스트 격리와 검증 범위를 학습합니다.',
    area='장치 트리 · 플랫폼 장치 · 회귀 테스트 · 참조 카운팅',
    sections=[
        ('구성과 식별자', 'GPL-2.0 파일은 bus,kconfig,OF,OF platform,platform_device와 KUnit OF/test,내부 OF 헤더를 포함합니다. 노드 이름 상수는 kunit-test이고 compatible은 test,empty입니다. 이름 기반 노드 검색과 compatible 기반 장치 검색은 서로 다른 관찰 기준입니다.'),
        ('Live tree 적용 테스트', 'apply 테스트는 내장 kunit_overlay_test 적용 결과 0을 ASSERT합니다. 이어 of_find_node_by_name(NULL,kunit_node_name)으로 검색한 결과가 오류나 NULL이 아닌지 EXPECT하고 of_node_put으로 참조를 반환합니다. 속성의 모든 바이트나 트리 전체 구조를 검사하는 테스트는 아닙니다.'),
        ('Platform device 연결 테스트', 'platform_device 테스트도 적용 성공을 ASSERT하고 노드를 검색합니다. 이 경로는 of_node_put_kunit을 먼저 호출한 뒤 노드 유효성을 ASSERT합니다. 이어 of_find_device_by_node(np)의 결과를 EXPECT하고 pdev가 있으면 embedded dev를 put합니다. 노드 참조는 테스트 관리 정리,장치 검색 참조는 명시적 put으로 분리됩니다.'),
        ('Compatible 검색 callback', 'bus_match_compatible은 dev->of_node와 data를 of_device_is_compatible에 전달해 반환합니다. 단순한 dev 이름 문자열 비교가 아닙니다. cleanup 검증은 platform bus 전체에서 같은 compatible인 장치가 남아 있는지를 검색하므로 다른 동일 compatible 장치가 존재하는 환경도 결과에 영향을 줄 수 있습니다.'),
        ('Cleanup 테스트 준비', 'cleanup 테스트는 root 관련 skip helper를 호출하고 EARLY_FLATTREE가 비활성이면 추가 skip합니다. 지역 fake test를 초기화해 성공 상태를 ASSERT하고 overlay는 &fake에 적용합니다. 검증 assertion은 바깥 test에 기록합니다. fake의 자동 종료를 기다리는 대신 명시적 cleanup 경계를 만들기 위한 구조입니다.'),
        ('참조를 정리하는 순서', '노드 검색 결과를 ASSERT한 뒤 &fake에 노드 put을 예약합니다. 장치를 찾아 ASSERT한 후 put_device를 호출하며 주석은 이후 pdev를 역참조하지 않는다고 명시합니다. 노드 put action은 overlay 적용 정리보다 나중에 등록되므로 정상 역순 cleanup은 노드 참조를 먼저 반환한 뒤 overlay를 제거하도록 구성됩니다.'),
        ('Cleanup 뒤 재조회', 'kunit_cleanup(&fake) 다음에 노드를 새로 검색해 NULL을 EXPECT하고 of_node_put합니다. platform bus에서는 compatible callback으로 찾아 NULL을 EXPECT하고 put_device합니다. 이미 반환한 pdev 주소의 필드를 읽어 삭제 여부를 확인하지 않습니다. 검색 결과 부재는 가시 상태 검증이며 모든 메모리 누수나 과거 참조 연산의 정확성을 증명하지 않습니다.'),
        ('Failure 경로의 한계', 'fake에 자원을 만든 뒤 여러 ASSERT가 있지만 바깥 test에 fake cleanup action을 별도로 예약하는 코드는 없습니다. 따라서 중간 ASSERT 중단의 모든 경로가 이 함수 끝의 명시적 cleanup에 도달한다고 가정하면 안 됩니다. 또한 overlay 적용 실패의 구체적 errno,부분 적용 rollback,동시 overlay 경쟁을 직접 검사하지 않습니다.'),
        ('Suite와 전체 범위', 'case 배열에는 apply,platform_device,cleanup 세 항목과 빈 sentinel이 있습니다. suite 이름은 of_overlay_apply_kunit이고 kunit_test_suites로 등록합니다. GPL license와 overlay 테스트 description을 포함합니다. 세 테스트·callback·상수·등록 전체를 대조했으며 실제 커널에서 실행한 결과를 주장하지 않습니다.')
    ], questions=[
        ('노드와 platform device 검색으로 얻은 참조는 같은 것인가?', '아니다. 각각 of_node_put과 put_device로 관리한다', '그렇다. 한 번 put하면 모든 참조가 사라진다', '서로 다른 객체 모델의 참조입니다. 각 검색 API의 수명 계약을 구분해야 합니다.'),
        ('cleanup 뒤 pdev를 다시 역참조하는가?', '아니다. 새 검색으로 노드와 장치 부재를 확인한다', '그렇다. 해제된 포인터의 필드를 읽는다', '주석도 put 이후 pdev를 역참조하지 않는다고 강조합니다. 객체 수명 종료 뒤 검증은 별도 조회로 수행합니다.'),
        ('cleanup 테스트의 장치 검색 기준은?', 'OF compatible인 test,empty', 'platform device의 메모리 주소만', 'callback은 of_device_is_compatible을 사용합니다. 이름 검색과 다른 조건이며 동일 compatible 장치의 존재도 고려해야 합니다.'),
        ('정상 fake cleanup에서 노드 put과 overlay 제거의 순서는?', '노드 put 후 overlay 제거', 'overlay 제거 후에만 노드 참조를 처음 얻는다', '노드 put이 나중에 등록되어 역순으로 먼저 실행됩니다. 자원 의존 관계와 등록 순서를 연결해 읽습니다.'),
        ('노드가 검색되지 않으면 모든 누수까지 증명한 것인가?', '아니다. 검색 가시성과 메모리 수명 전체 검증은 다르다', '그렇다. NULL이 모든 실패 경로의 회수를 증명한다', '검증하는 것은 특정 이름 및 compatible의 검색 결과입니다. 관찰 범위를 넘어선 주장을 피해야 합니다.')
    ]
), dict(
    path='drivers/of/kunit_overlay_test.dtso', title='KUnit overlay 입력: 루트에 테스트 노드 추가',
    intro='짧은 DTS overlay 전체와 C 테스트의 검색 조건을 연결합니다.',
    principle='선언형 트리 데이터는 적용 대상 경로와 추가할 노드·속성을 분리해 표현합니다.',
    use='트리 경로,노드 이름,compatible 속성과 테스트 fixture를 학습합니다.',
    area='장치 트리 · 선언형 데이터 · 테스트 입력',
    sections=[
        ('형식과 overlay 선언', 'SPDX는 GPL-2.0이며 /dts-v1/;로 DTS 형식을 선언하고 /plugin/;으로 overlay 입력임을 표시합니다. C 함수나 실행 순서를 기술하는 파일이 아니라 빌드 도구가 처리할 트리 기술입니다.'),
        ('대상 경로와 노드', '&{/}는 루트 경로를 대상으로 합니다. 그 안에 kunit-test 자식 노드를 추가하고 compatible="test,empty" 하나를 지정합니다. reg,interrupts,주소 셀이나 별도 자식 노드는 없습니다. 이름과 compatible은 서로 다른 식별 정보입니다.'),
        ('테스트와 연결', 'overlay_test.c는 kunit-test 이름으로 노드를 조회하고 test,empty compatible으로 장치를 찾습니다. 이 데이터 자체가 platform device 등록 함수를 실행하는 것은 아니며 실제 적용과 OF 동적 처리 경로가 필요합니다. 전체 선언을 대조했고 DTBO 컴파일·적용 실행은 하지 않았습니다.')
    ], questions=[
        ('이 overlay가 대상으로 삼는 경로는?', '루트 /', '/soc만', '&{/}가 명시된 대상입니다. 실제 추가 노드는 그 아래 kunit-test입니다.'),
        ('노드 이름과 compatible 값은 각각 무엇인가?', 'kunit-test와 test,empty', '둘 다 같은 kunit_overlay_test 문자열', '파일 이름·링커 심볼에 사용하는 토큰과 트리 내부 이름·속성은 다른 식별자입니다.')
    ]
), dict(
    path='drivers/of/empty_root.dts', title='빈 DeviceTree 루트: 빈 트리와 루트 부재의 차이',
    intro='최소 DTS 입력의 선언과 비어 있는 루트 블록 전체를 확인합니다.',
    principle='자식이 없는 루트 객체가 존재하는 상태와 루트 자체가 없는 상태는 다릅니다.',
    use='최소 입력 데이터,트리 구조와 전처리 없는 선언형 파일을 학습합니다.',
    area='트리 자료구조 · 장치 트리 · 최소 fixture',
    sections=[
        ('라이선스와 형식', 'SPDX는 GPL-2.0-only이고 /dts-v1/; 선언이 있습니다. /plugin/; 선언은 없으므로 앞선 overlay 입력과 같은 형식 표식을 모두 갖는 것은 아닙니다.'),
        ('루트 내용', '/ { }; 형태의 루트 블록이 있으며 내부에는 속성도 자식 노드도 없습니다. 빈 루트가 있다는 기술과 소스가 아예 없거나 런타임 of_root가 NULL인 상태를 동일하게 보면 안 됩니다.'),
        ('파일 범위와 역할', '이 파일은 최소 루트 구조를 기술할 뿐 CPU,메모리,장치 주소나 테스트 노드를 정의하지 않습니다. 입력의 전체를 검토했으며 이것만으로 어떤 런타임에 언제 루트가 설치되는지는 호출·빌드 경로를 별도로 확인해야 합니다. 실제 DTB 생성은 실행하지 않았습니다.')
    ], questions=[
        ('이 입력에는 루트 노드 기술이 있는가?', '있다. 내부가 빈 루트 블록이다', '없다. 파일 전체가 주석뿐이다', '/ 블록이 실제로 존재합니다. 자식 개수 0과 루트 부재는 다른 구조 상태입니다.'),
        ('이 파일에 plugin overlay 표식이 있는가?', '없다', '있다. /plugin/이 명시되어 있다', '선언은 /dts-v1/과 빈 루트뿐입니다. 인접한 dtso 파일의 내용을 이 파일에 추정해서는 안 됩니다.')
    ]
)]
