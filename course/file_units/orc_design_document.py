"""Whole ORC design guide with version-specific sorting correction."""
ROWS = [dict(
    path='Documentation/arch/x86/orc-unwinder.rst',
    title='ORC 설계 문서: 빌드 분석과 빠른 실행 시점 복원',
    intro='ORC 생성 과정, frame pointer 및 DWARF와의 비교, 병렬 배열과 빠른 검색 구조를 문서 전체에서 학습합니다.',
    principle='복잡한 분석을 빌드 시점에 수행하고 실행 시점에는 단순한 메타데이터를 조회하는 시간·공간 절충입니다.',
    use='ORC의 설계 선택과 문서의 역사적 측정값 및 현재 버전 구현 차이를 이해합니다.',
    area='정적 분석 · 메타데이터 · 캐시 지역성 · 이진 검색 · 병렬 배열 · 도구 의존성',
    sections=[
        ('문서 전체의 범위', 'GPL-2.0 표시 뒤 Overview, frame pointer 비교, DWARF 비교, table generation, implementation details, etymology와 세 참고 링크가 있습니다. CONFIG_UNWINDER_ORC로 기능을 선택하며 DWARF와 개념적으로 비슷하지만 자료 형식을 단순화했다고 설명합니다. 문서의 비교와 주장, 해당 버전 소스에서 확인한 동작을 구분해 읽습니다.'),
        ('Objtool 생성 경로', '문서는 objtool이 컴파일된 .o의 코드 경로와 instruction별 stack 상태를 분석하여 .orc_unwind와 .orc_unwind_ip section을 만든다고 설명합니다. 분석 기반으로 compile-time stack metadata validation을 듭니다. 실행 중 모든 함수가 매번 전체 코드를 다시 분석하는 방식은 아닙니다. 코드 주소와 복원 규칙의 관계가 별도 데이터로 저장됩니다.'),
        ('링크·정렬 설명의 버전 차이', '문서는 object section을 링크 때 합치고 부팅 때 정렬한다고 설명합니다. 하지만 v6.12 unwind_init의 주석과 본문은 기본 커널 테이블이 sorttable 도구로 이미 빌드 시점에 정렬되어 이진 검색 준비가 되었다고 명시합니다. 모듈의 unwind_module_init에는 별도 sort 호출이 있습니다. 따라서 모든 ORC 테이블이 오직 부팅 시점에 정렬된다고 안내하지 않습니다. 관련 함수 대조는 unwind_orc.c 전체 완료가 아닙니다.'),
        ('Frame pointer의 비용 비교', '문서는 frame pointer 계측으로 .text가 약 3.2% 커지고 일부 workload에서 5~10% 느려졌다는 과거 측정을 인용합니다. ORC 자료는 실행 명령 밖에 있어 frame pointer를 유지하는 hotpath 비용을 피할 수 있다는 설계 장점입니다. 이를 현재 모든 시스템의 동일한 성능 차이나 실제 unwind 실행 비용이 0이라는 뜻으로 읽으면 안 됩니다. 인용된 cache locality 논의는 코드 크기 감소가 명령 캐시 사용량을 줄일 수 있다는 인과 설명입니다.'),
        ('Interrupt와 메모리 절충', '문서는 frame pointer가 저장되기 전 interrupt나 leaf 함수에서 caller가 빠질 수 있는 반면 ORC가 interrupt·exception 경계를 더 신뢰성 있게 추적할 수 있다고 설명합니다. 대가는 unwind table 메모리이며 2~4MB라는 수치는 커널 구성에 따른 문서상의 대략적인 예입니다. 형식 자체가 정확한 모든 입력과 오류 없는 생성 도구를 무조건 보장한다는 뜻은 아닙니다.'),
        ('DWARF 대비 단순성', 'ORC는 복잡한 CFI 상태 기계와 불필요한 register 추적을 줄여 oops 처리 같은 진단 경로를 단순하게 만들려 합니다. perf와 lockdep처럼 자주 stack을 수집하는 곳에서는 조회 비용도 중요합니다. 문서는 out-of-tree DWARF 비교 실험의 약 20배와 이후 개선을 반영한 약 40배 가능성을 언급합니다. 이는 문서가 설명하는 특정 과거 비교이며 이 프로젝트가 재현한 benchmark는 아닙니다.'),
        ('DWARF 대비 저장량과 표현력', '문서는 ORC table이 DWARF eh_frame보다 약 50% 더 많은 RAM, 한 x86 defconfig 예에서 1.3MB 추가를 사용한다고 설명합니다. 단순한 표현이 더 작은 표현과 항상 같은 것은 아닙니다. 향후 compiler 최적화가 더 복잡한 stack 변형을 만들면 현재 표현이 부족해질 가능성도 논의합니다. 필요한 register를 늘리더라도 형식을 통제하고 복잡한 상태 기계를 피하려는 설계 의도를 제시합니다.'),
        ('DWARF 변환만으로 부족한 이유', '문서는 DWARF를 ORC로 바꾸는 도구도 생각할 수 있지만 커널의 assembly, inline assembly, exception table 등 특수 경로 때문에 불완전할 수 있다고 설명합니다. assembly .cfi와 별도 inline assembly annotation은 유지보수와 정확성에 부담을 줄 수 있습니다. objtool도 특수 entry 코드 같은 경우 annotation이 필요하므로 annotation이 완전히 없어졌다고 이해하면 안 됩니다.'),
        ('Objtool 의존성과 대안', '자동 분석은 적은 annotation으로 자료를 만들고 일부 toolchain 문제에서 독립성을 얻는 대신 compiler의 코드 흐름을 추적하는 objtool 능력에 의존합니다. 복잡한 최적화가 이를 깨면 compiler와 조정, DWARF를 추가 입력으로 사용, compiler plugin 등의 대안을 고려할 수 있다고 문서는 제시합니다. 이는 가능한 미래 대안 목록이며 이미 모두 구현된 기능 목록이 아닙니다.'),
        ('병렬 배열과 검색 범위 축소', 'orc_entry 배열과 그에 대응하는 instruction 주소 배열을 나누면 검색 대상인 .orc_unwind_ip가 작아집니다. 두 배열은 같은 인덱스의 대응을 유지하며 정렬되어야 합니다. 실행 시 생성하는 빠른 lookup table은 주소를 ORC 인덱스의 좁은 범위와 연결해 전체 대신 일부를 검색하도록 합니다. 자료 분리로 캐시 접근량을 줄이고 보조 인덱스로 검색 범위를 줄이는 별개의 최적화입니다.'),
        ('이름과 참고 자료', 'ORC는 Oops Rewind Capability의 약자입니다. 문서는 판타지의 orc와 dwarf 관계를 이용한 이름의 유래를 설명하며 frame pointer 성능 메일, DWARF 비교 메일, 민속 캐릭터 관련 링크를 각주로 둡니다. 비유를 기술적 정확성의 근거로 사용하지 않습니다. 여기서는 저장된 문서를 해설했으며 링크된 외부 자료를 새로 읽거나 원문 전체를 검증한 것은 아닙니다.'),
        ('CS 연결과 완료 범위', '빌드 시 정적 분석과 실행 시 검색의 분리, 정보 표현의 단순성과 압축률의 차이, instruction cache, 병렬 배열 정렬의 대응 불변식, 인덱스를 통한 검색 범위 축소를 학습합니다. 전체 문서 대조는 성능 수치를 현재 하드웨어에서 재현하거나 모든 compiler 코드를 검증했다는 뜻은 아닙니다.')
    ],
    questions=[
        ('ORC가 별도 메타데이터를 사용하면 실제 unwind 연산 비용도 0인가?', '아니다. frame pointer 유지 비용을 피하는 것과 unwind 조회 비용은 다르다', '그렇다. 어떠한 조회나 메모리 접근도 필요하지 않다', '실행 시 unwinder는 자료를 검색하여 프레임을 복원합니다. hotpath 계측 비용과 진단 실행 비용을 구분해야 합니다.'),
        ('v6.12 기본 커널 ORC 테이블은 unwind_init에서 처음 정렬되는가?', '아니다. 해당 구현은 빌드 시 sorttable로 정렬되었다고 명시한다', '그렇다. 문서의 부팅 정렬 설명이 모든 버전에 그대로 적용된다', '문서와 현재 소스의 차이를 확인했습니다. 모듈에는 별도 정렬 경로가 있으므로 객체 종류도 구분해야 합니다.'),
        ('ORC 데이터를 두 배열로 나눈 핵심 이유는?', '검색하는 instruction 주소 배열을 더 작고 조밀하게 유지하기 위해서다', '같은 인덱스 사이의 대응을 제거하기 위해서다', '검색 후 대응 orc_entry를 찾으려면 인덱스 관계를 보존해야 합니다. 데이터 분리와 의미 분리는 다릅니다.'),
        ('Objtool은 annotation이 전혀 필요 없는가?', '아니다. 특수한 stack 동작에는 일부 annotation이 필요하다', '그렇다. 모든 assembly의 의미를 언제나 자동 증명한다', '문서는 특히 entry 코드 같은 특수 경우의 annotation과 compiler 흐름 분석 의존성을 명시합니다.'),
        ('단순한 ORC 형식은 반드시 DWARF보다 적은 RAM을 사용하는가?', '아니다. 문서는 오히려 더 큰 table 저장량 예를 제시한다', '그렇다. 알고리즘이 단순하면 표현 크기도 항상 작다', '실행 비용, 해석 복잡도, 저장량은 서로 다른 축입니다. 이 설계는 빠른 조회를 위해 더 많은 메모리를 사용할 수 있습니다.')
    ]
)]
