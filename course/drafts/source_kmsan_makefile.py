"""Manually authored full KMSAN runtime Kbuild Makefile."""
ROWS=[
('KMSAN runtime Makefile·여섯 object의 역할','obj-y',
 'Makefile은 C 함수가 아니라 빌드 규칙과 변수입니다. obj-y에 core·instrumentation·init·hooks·report·shadow 여섯 object를 나열해 해당 directory의 kernel build 대상으로 지정합니다. 각 이름은 앞에서 읽은 C 구현군에 연결되며 실제 최상위 Kbuild가 directory를 포함하는 조건은 별도로 읽습니다.',
 'source.c→object.o→kernel link 흐름을 그리세요. GNUmake 모델은 여섯 이름의 확장을 확인하며 실제 kernel compiler·linker·전체 dependency graph는 실행하지 않았습니다.',
 [('obj-y의 .o 목록은 무엇을 나타내나요?','이 directory에서 빌드할 object 목록입니다.','C 함수의 실행 순서입니다.','object 목록과 runtime 함수 호출 순서는 다른 단계입니다. Makefile을 C 코드처럼 읽지 않습니다.'),('여섯 .o 목록 확인이 실제 kernel link 성공을 뜻하나요?','아닙니다. 변수 확장 검증입니다.','그렇습니다. 모든 compiler·linker가 완료됐습니다.','GNUmake의 문자열 결과와 실제 compile·link 작업을 구별합니다. 검수 범위를 명확히 읽습니다.')]),
('KMSAN 자기 runtime의 세 계측 제외','KMSAN_SANITIZE',
 'KMSAN_SANITIZE·KCOV_INSTRUMENT·UBSAN_SANITIZE를 모두 n으로 지정합니다. 검사 runtime 자체를 같은 검사와 coverage로 계측하면 재진입과 추가 side effect가 생길 수 있으므로 빌드에서 제외하는 정책입니다. 별도 userspace source fixture에서 ASan·UBSan을 사용하는 검수와 actual kernel build 설정은 다른 문맥입니다.',
 '세 변수 n과 test object의 KMSAN override y를 나란히 읽으세요. GNUmake 모델은 값만 검증하고 실제 Kbuild 계측 pass·coverage callback은 실행하지 않았습니다. 실험 sanitizer 결과를 원본 build와 혼동하지 않습니다.',
 [('원본 runtime directory의 UBSAN_SANITIZE 값은 무엇인가요?','n입니다.','항상 y입니다.','실험에서 UBSan으로 원문 모델을 검사한 것과 실제 kernel runtime build 설정을 구별합니다.'),('검사 runtime 자신에게 같은 계측을 피하는 주요 이유는 무엇인가요?','재진입과 runtime side effect를 줄이려는 것입니다.','모든 kernel 코드의 검사를 없애려는 것입니다.','해당 directory의 runtime 정책입니다. 검사 대상 일반 코드와 runtime 자체의 책임을 나누어 이해합니다.')]),
('KMSAN compiler option 탐지와 += 변수 누적','CC_FLAGS_KMSAN_RUNTIME',
 'runtime flag는 -fno-stack-protector로 시작해 cc-option이 지원하면 -fno-conserve-stack을 더하고 DISABLE_BRANCH_PROFILING 정의를 추가합니다. :=의 즉시 확장과 +=의 누적을 읽으며 cc-option은 Kbuild helper라는 점을 확인합니다. 모델 helper는 지원 여부를 명시해 반환할 뿐 실제 compiler option 탐지 구현은 아닙니다.',
 '지원0/1 두 경우의 flag 목록을 비교하세요. -D는 C 전처리 정의를 compiler에 넘기고 Makefile 자체의 함수 실행과 다릅니다. 실제 cc-option helper 정의와 compiler 진단은 후속 원문에 연결합니다.',
 [('cc-option 미지원 모델에서 -fno-conserve-stack이 포함되나요?','아닙니다. 그 option은 생략됩니다.','그렇습니다. 모든 경우 강제합니다.','조건부 helper 반환과 += 결과를 확인합니다. 실제 compiler 지원 탐지를 이 모델이 수행한 것은 아닙니다.'),('-DDISABLE_BRANCH_PROFILING은 어떤 단계에 전달하나요?','C compiler 전처리 정의로 전달합니다.','runtime마다 문자열을 출력합니다.','-D flag의 목적과 Makefile 변수 확장을 구별합니다. source의 조건부 compilation과 연결합니다.')]),
('KMSAN ftrace 제거와 재귀 호출 방지','CFLAGS_REMOVE_core.o',
 '여섯 runtime object마다 CC_FLAGS_FTRACE를 CFLAGS_REMOVE에 지정합니다. ftrace가 함수 진입을 추적하는 계측을 붙이면 runtime 내부에서도 tracing 경로가 재귀로 들어올 수 있어 제외합니다. 삭제할 flag와 최종 runtime flag의 추가는 서로 다른 Kbuild 변수 역할입니다.',
 '모델의 ftrace flag -pg·-mfentry가 여섯 remove 변수에 모두 있는지 확인하세요. 실제 function tracer·patching·ring buffer는 이 Makefile 확장 검수에 포함되지 않으며 후속 기술 수업에서 읽습니다.',
 [('여섯 runtime object의 CFLAGS_REMOVE는 무엇을 대상으로 하나요?','CC_FLAGS_FTRACE입니다.','항상 모든 include path입니다.','실제 변수명을 확인합니다. 원문 주석의 recursion 이유를 tracing 계측과 연결합니다.'),('remove 변수 확인만으로 실제 ftrace runtime을 실행했나요?','아닙니다. 빌드 flag 정책만 확인했습니다.','그렇습니다. 실제 모든 함수 trace를 재현했습니다.','컴파일 계측 선택과 kernel tracing 실행은 다른 단계입니다. 기술의 사용 조건을 빌드부터 연결합니다.')]),
('KMSAN 여섯 object의 공통 CFLAGS 적용','CFLAGS_core.o',
 'core·hooks·init·instrumentation·report·shadow 각각의 CFLAGS를 공통 runtime flag로 지정합니다. 이름을 하나씩 반복해 적용 누락을 피해야 하며 object-specific 변수는 directory 계측 제외와 함께 최종 compiler 명령에 영향을 줍니다. 실제 compiler 명령 구성은 Kbuild의 상위 규칙을 따라야 합니다.',
 'GNUmake 모델에서 여섯 CFLAGS 값과 여섯 remove 값을 독립 예상 목록에 대조하세요. 네 설정 조합44개 변수 검사가 통과했지만 실제 object compile을 수행한 검증과 구별합니다.',
 [('CFLAGS_core.o와 CFLAGS_shadow.o는 이 원문에서 무엇을 받나요?','같은 CC_FLAGS_KMSAN_RUNTIME 값입니다.','항상 서로 반대 sanitizer 설정입니다.','두 대입과 나머지 네 object의 동일 패턴을 확인합니다. 적용 대상을 누락 없이 비교합니다.'),('object-specific flag가 실제 최종 compiler 명령에 쓰이는 규칙은 어디서 더 읽나요?','상위 Kbuild 규칙에서 읽습니다.','Makefile이 C runtime에서 직접 실행합니다.','directory 변수와 compiler 명령 생성의 계층을 구별합니다. 이 파일의 역할 범위를 명확히 합니다.')]),
('KMSAN KUnit test의 조건부 빌드와 계측 재활성화','obj-$(CONFIG_KMSAN_KUNIT_TEST)',
 'CONFIG_KMSAN_KUNIT_TEST가 y이면 obj-y에 kmsan_test.o가 추가되고 n이면 obj-n에 놓입니다. test object는 KMSAN_SANITIZE_kmsan_test.o=y로 directory 제외를 덮고 uninitialized compiler warning을 끕니다. 미초기화 탐지를 테스트할 코드와 안전하게 동작해야 하는 runtime의 빌드 정책이 다릅니다.',
 '테스트 설정0/1의 obj-y와 obj-n을 비교하세요. GNUmake 모델은 조건부 목록과 warning flag를 확인하며 실제 kmsan_test.c·KUnit assertion·의도된 미초기화 실행은 수행하지 않았습니다. 테스트 구현을 별도 수업으로 읽어야 합니다.',
 [('KUnit 설정n에서 kmsan_test.o는 obj-y에 포함되나요?','아닙니다. obj-n에 놓입니다.','그렇습니다. 항상 kernel에 링크됩니다.','obj-$(CONFIG...)의 변수 이름 확장을 확인합니다. 모델의 목록 검증과 실제 상위 link 선택을 구별합니다.'),('test object의 KMSAN_SANITIZE 값은 무엇인가요?','y로 재활성화합니다.','runtime의 n만 적용합니다.','per-object override를 확인합니다. 검사를 제공하는 runtime과 검사 대상 test 코드의 역할이 다릅니다.')])]

def register(topic,q,detail):
 for title,symbol,principle,use,questions in ROWS:
  topic(title,'빌드·초기화','mm/kmsan/Makefile',symbol,
   'Linux 검사 runtime의 실제 빌드 대상·계측 제외·compiler flag·tracing 재귀 방지·테스트 조건을 Makefile 원문으로 배웁니다.',principle,use,
   'C 언어·GNUmake 변수·Kbuild helper·compiler option·전처리 정의·runtime 실행의 단계를 구별하며 한 줄씩 주석을 달아 보세요.',
   *(q(*x) for x in questions),details=[
    detail('원문 범위','고정 mm/kmsan/Makefile 34행 전체의 여섯 object·세 계측 제외·공통 flag·여섯 ftrace 제거·여섯 flag 대입·KUnit 조건·계측 override·warning 설정을 해설과 문제로 연결했습니다.'),
    detail('변수 확장 실험','원본 Makefile을 GNUmake로 include하고 cc-option·cc-disable-warning·ftrace flag만 명시한 helper 모델을 주었습니다. option 지원0/1과 KUnit0/1의 네 조합에서44개 변수를 독립 예상 값과 대조해 통과했습니다. 실제 kernel compile·link·Kbuild option 탐지·tracing·KUnit test는 실행하지 않았습니다.')])
