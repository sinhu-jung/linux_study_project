"""Whole-file OF Kconfig dependency and test-selection analysis."""
ROWS = [dict(
    path='drivers/of/Kconfig', title='OF 구성 그래프: depends on·select·default와 테스트 조건',
    intro='DTC와 OF 메뉴,모든 하위 설정의 타입·조건·기본값 및 도움말을 분석합니다.',
    principle='설정의 의존성,다른 설정을 선택하는 관계,기본값과 메뉴 표시 조건은 서로 다른 기능입니다.',
    use='의존성 그래프,조건 논리,빌드 구성과 실행 전제의 차이를 학습합니다.',
    area='Kconfig · 의존성 그래프 · 논리식 · 테스트 구성',
    sections=[
        ('파일과 상위 메뉴', 'GPL-2.0 파일은 prompt 없는 bool DTC를 먼저 정의하고 bool menuconfig OF를 Device Tree and Open Firmware support라는 이름으로 제공합니다. 도움말은 필요한 플랫폼의 자동 선택과 unittest,overlay,compile coverage를 위한 수동 선택을 설명합니다. 이후 설정은 if OF 영역에 속하고 마지막 endif로 닫힙니다. DTC 자체는 이 if 바깥에 있습니다.'),
        ('기존 runtime unittest', 'OF_UNITTEST는 bool이며 OF_EARLY_FLATTREE에 depends on하고 IRQ_DOMAIN과 OF_RESOLVE를 select합니다. 도움말은 부팅 때 한 번 실행하고 콘솔에 결과를 출력한다고 설명합니다. TAINT_TEST,의도적인 오류·경고·스택 출력과 트리 손상 가능성도 이 테스트 설정의 문서에 명시됩니다. 로그를 scripts/dtc/of_unittest_expect로 처리하도록 안내하며 KUnit 설정과 같은 테스트 집합이라고 볼 수 없습니다.'),
        ('기본 OF KUnit 테스트', 'OF_KUNIT_TEST는 tristate이고 KUNIT에 의존하며 기본값은 KUNIT_ALL_TESTS입니다. prompt 뒤 if !KUNIT_ALL_TESTS는 메뉴 표시 조건이며 테스트 기능 전체를 끄는 depends on과 다릅니다. 도움말은 OF 기반 KUnit 테스트를 빌드한다고 설명합니다. EARLY_FLATTREE를 이 항목에서 직접 depends on하거나 select하지 않으므로 실행 helper의 별도 skip 조건을 함께 봐야 합니다.'),
        ('전체 DTB 빌드', 'OF_ALL_DTBS는 bool이며 COMPILE_TEST에 의존하고 DTC를 select합니다. 설명은 현재 아키텍처에서 가능한 DTB를 모두 빌드한다는 것입니다. 모든 아키텍처의 모든 DTB를 한꺼번에 빌드하거나 런타임 트리에 모두 설치하는 의미가 아닙니다.'),
        ('Flattened tree 기반', 'OF_FLATTREE는 prompt 없는 bool이고 DTC,LIBFDT,CRC32를 select합니다. OF_EARLY_FLATTREE는 def_bool로 OF이면서 SPARC,ALPHA,HEXAGON,M68K,PARISC,S390 중 어느 것도 아닌 조건을 기본값으로 둡니다. HAS_DMA와 HAS_IOMEM이 모두 있으면 DMA_DECLARE_COHERENT를 select하고 OF_FLATTREE를 select합니다. def_bool 기본 논리를 별도의 명시적 depends on 목록으로 바꿔 읽으면 안 됩니다.'),
        ('PROM과 sysfs 표현', 'OF_PROMTREE는 bool만 선언된 내부 설정입니다. OF_KOBJ는 def_bool SYSFS로 기본값을 정합니다. 여기에는 실제 kobject 생성 코드나 PROM 순회 알고리즘이 없습니다. 해당 기능의 object 선택과 실행 코드는 다른 파일에서 정의됩니다.'),
        ('동적 트리의 표시 조건', 'OF_DYNAMIC은 bool이며 prompt는 OF_UNITTEST일 때 표시되고 OF_KOBJ를 select합니다. 도움말은 일부 플랫폼의 런타임 트리 수정과 테스트 커버리지를 설명합니다. prompt가 숨겨졌다고 다른 설정의 select가 불가능한 것은 아닙니다. OF_OVERLAY가 이 설정을 선택하는 관계가 아래에 있습니다.'),
        ('주소·IRQ·예약 메모리', 'OF_ADDRESS는 def_bool y이지만 !SPARC && (HAS_IOMEM || UML)에 depends on합니다. OF_IRQ도 def_bool y이고 !SPARC && IRQ_DOMAIN에 의존합니다. OF_RESERVED_MEM은 def_bool OF_EARLY_FLATTREE입니다. 기본 y라는 표현만 보고 의존성이 거짓인 구성에서도 켜진다고 해석하면 안 됩니다.'),
        ('Resolver와 overlay', 'OF_RESOLVE는 prompt 없는 bool입니다. OF_OVERLAY는 사용자 prompt가 있는 bool이며 OF_DYNAMIC,OF_FLATTREE,OF_RESOLVE를 select합니다. 도움말은 동적으로 로드된 데이터로 커널 트리 일부를 수정하는 방법이라고 설명합니다. OF_FLATTREE 선택과 OF_EARLY_FLATTREE 선택은 같은 것이 아니며 이 항목은 EARLY를 직접 select하지 않습니다.'),
        ('Overlay KUnit과 NUMA', 'OF_OVERLAY_KUNIT_TEST는 tristate,prompt if !KUNIT_ALL_TESTS,depends on KUNIT,default KUNIT_ALL_TESTS를 갖고 OF_OVERLAY를 select합니다. 그러므로 overlay 선택을 통해 dynamic·flattree·resolve로 관계가 이어집니다. 마지막 OF_NUMA는 prompt 없는 bool입니다. 이 파일 자체에 OF_NUMA의 기본값이나 별도 select는 없습니다.'),
        ('그래프와 검토 범위', 'DTC,OF와 모든 하위 설정,도움말 및 조건을 대조했습니다. 의존성 그래프를 읽을 때 depends on은 허용 조건,select는 다른 심볼 선택,default는 기본값,prompt if는 표시 조건으로 구분합니다. Kconfig 처리 전체를 실행한 것은 아니며 다른 파일에서의 선택과 아키텍처 설정까지 이 한 파일로 확정할 수 없습니다.')
    ], questions=[
        ('OF_KUNIT_TEST의 prompt if !KUNIT_ALL_TESTS는 무엇을 제어하는가?', '메뉴 prompt의 표시 조건', 'KUNIT_ALL_TESTS가 켜지면 테스트를 무조건 비활성화하는 조건', '테스트의 default는 오히려 KUNIT_ALL_TESTS입니다. prompt 조건과 depends on을 구분해야 합니다.'),
        ('OF_OVERLAY가 직접 선택하는 세 설정은?', 'OF_DYNAMIC,OF_FLATTREE,OF_RESOLVE', 'OF_EARLY_FLATTREE,OF_NUMA,OF_PROMTREE', '실제 select 목록을 따라야 합니다. FLATTREE와 EARLY_FLATTREE는 서로 다른 심볼입니다.'),
        ('OF_ALL_DTBS의 도움말상 빌드 범위는?', '현재 아키텍처의 가능한 DTB', '항상 모든 아키텍처의 모든 DTB', '현재 architecture라는 범위가 명시되어 있습니다. 빌드와 런타임 적용도 구분합니다.'),
        ('OF_ADDRESS의 기본 y는 모든 플랫폼에서 무조건 y를 보장하는가?', '아니다. !SPARC와 HAS_IOMEM 또는 UML 조건에 의존한다', '그렇다. depends on은 아무 영향이 없다', '기본값을 적용할 수 있는 범위는 의존성으로 제한됩니다.'),
        ('OF_DYNAMIC prompt가 숨겨지면 OF_OVERLAY가 선택할 수 없는가?', '아니다. prompt 표시와 select 관계는 별개다', '그렇다. 숨겨진 설정은 절대 켤 수 없다', 'OF_OVERLAY에는 OF_DYNAMIC select가 실제로 있습니다. 사용자 메뉴 노출과 내부 선택 가능성을 구분합니다.'),
        ('OF_UNITTEST와 OF_KUNIT_TEST가 동일 설정인가?', '아니다. 타입·의존성과 실행 설명이 다른 항목이다', '그렇다. 이름만 다른 alias다', '전자는 부팅 runtime unittest용 bool,후자는 KUNIT 의존 tristate입니다. 두 테스트 집합을 혼동하지 않습니다.')
    ]
)]
