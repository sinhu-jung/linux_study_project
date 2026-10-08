"""Manually authored lessons from all four pinned sanitizer interface headers."""
ROWS = []
def row(path, title, symbol, principle, use, *questions):
    ROWS.append((path, title, symbol, principle, use, questions))

K = 'include/linux/kcsan-checks.h'
A = 'include/linux/kasan-checks.h'
M = 'include/linux/kmsan-checks.h'
I = 'include/linux/instrumented.h'

row(K, 'KCSAN 접근 분류·비트 플래그의 합성', '__kcsan_check_read',
    'KCSAN에 전달하는 type은 접근의 성질을 비트로 표현합니다. WRITE=1, COMPOUND=2, ATOMIC=4, ASSERT=8, SCOPED=16입니다. WRITE가 없으면 읽기입니다. 일반 read는 0, write는 1, read-write는 1|2=3이므로 숫자 3은 세 번째 함수 번호가 아니라 두 성질을 합친 값입니다. ASSERT와 SCOPED는 일반 컴파일러 계측에서 자동 생기는 플래그가 아닙니다.',
    'read, write, 복합 RMW의 플래그를 직접 이진수로 써 보세요. 플래그를 기록하는 일과 실제 데이터를 읽고 쓰는 연산을 구별합니다. 이 헤더의 검사 매크로가 데이터 접근 자체를 대신 수행하지는 않습니다.',
    ('일반 read-write의 type 값은 얼마인가요?', 'WRITE|COMPOUND인 3입니다.', 'ATOMIC 하나인 4입니다.', 'WRITE는 1, COMPOUND는 2이므로 비트 OR 결과는 3입니다. 원자성 표시는 별도 비트입니다.'),
    ('WRITE 비트가 없는 일반 접근은 어떻게 해석하나요?', '읽기로 해석합니다.', '모든 접근을 무시합니다.', '원문은 WRITE가 설정되지 않으면 read라고 명시합니다. read의 0은 검사 생략 요청이 아닙니다.'))
row(K, 'KCSAN 직접 검사·설정과 번역 단위의 차이', '__kcsan_check_access',
    'CONFIG_KCSAN이 켜지면 __kcsan_check_access는 런타임 함수로 선언됩니다. 현재 C 파일의 계측을 선택적으로 꺼도 직접 호출 경로는 남습니다. 반면 CONFIG_KCSAN이 꺼지면 같은 이름의 빈 inline 함수가 제공됩니다. 커널 전체 설정과 한 번역 단위의 컴파일 계측 여부를 따로 확인해야 호출이 검사를 수행하는지 알 수 있습니다.',
    '일반 컴파일러가 보지 못하는 접근을 명시적으로 점검할 때 주소·길이·type을 전달합니다. 원문은 __kcsan_* 직접 호출을 헤더에서 사용하지 말라고 요구합니다. 공통 헤더에는 번역 단위 설정을 따르는 공개 계층을 사용하세요.',
    ('CONFIG_KCSAN이 켜지고 현재 파일의 계측만 꺼지면 직접 __kcsan 검사 호출은 남나요?', '그렇습니다. 직접 런타임 경로는 남습니다.', '아닙니다. 항상 빈 함수가 됩니다.', '직접 API의 조건은 커널 CONFIG_KCSAN입니다. 현재 번역 단위 계측과 같은 조건이 아닙니다.'),
    ('원문은 직접 __kcsan_*를 공통 헤더에서 쓰도록 권하나요?', '아닙니다. 헤더에서는 사용하지 말라고 명시합니다.', '그렇습니다. 모든 헤더에서 강제해야 합니다.', '공통 헤더가 선택적으로 계측을 끈 번역 단위에도 포함될 수 있으므로 공개 계층을 구별합니다.'))
row(K, 'KCSAN 공개 검사·빈 inline에서도 인자는 평가된다', 'kcsan_check_access',
    '__SANITIZE_THREAD__가 정의되면 kcsan_check_access는 직접 검사 함수의 alias입니다. 그렇지 않으면 빈 inline 함수입니다. 빈 함수라도 C 함수 인자의 부수 효과를 임의로 없애는 계약은 아닙니다. 예를 들어 side_effect()를 인자로 전달했다면 그 부수 효과는 함수 본문이 빈 것과 별개입니다. 전처리로 인자 토큰을 버리는 빈 매크로와 구별해야 합니다.',
    '현재 파일이 계측되는지 확인한 뒤 공개 read·write wrapper를 추적하세요. 검사 유무에 의존하는 데이터 갱신을 인자에 숨기지 않습니다. 선택 fixture는 비계측 빈 함수의 인자 평가와 IGNORE_ATOMICS 매크로의 인자 생략을 따로 확인했습니다.',
    ('공개 검사 계층이 런타임으로 연결되는 번역 단위 표시는 무엇인가요?', '__SANITIZE_THREAD__입니다.', '언제나 CONFIG_SMP 하나입니다.', '커널 KCSAN 설정과 별도로 현재 번역 단위의 thread instrumentation 표시를 봅니다.'),
    ('빈 inline에 전달한 인자의 부수 효과도 반드시 사라지나요?', '아닙니다. 함수 호출 인자의 평가와 빈 본문은 별개입니다.', '그렇습니다. 모든 인자 토큰을 전처리에서 버립니다.', '빈 함수와 do{}while(0)로 인자를 쓰지 않는 매크로는 다른 C 구조입니다.'))
row(K, 'KCSAN 현재 문맥의 검사 중단·중첩 균형', 'kcsan_disable_current',
    'kcsan_disable_current와 kcsan_enable_current는 현재 실행 문맥의 KCSAN 검사 상태를 조절하며 중첩을 지원합니다. 중첩 disable을 한 번의 enable로 모두 해제하는 단순 bool 전환으로 해석하면 안 됩니다. enable_current_nowarn은 uaccess 영역에서도 안전하게 쓸 수 있는 별도 재활성화 경로입니다. 검사 상태를 바꾸는 것이 CPU 인터럽트를 막거나 공유 데이터 lock을 획득하는 일은 아닙니다.',
    'disable 두 번, enable 두 번의 균형을 도식으로 그리세요. 조기 반환 경로도 균형을 유지해야 합니다. 검사 중단을 실제 상호 배제 수단으로 사용하지 않고 필요한 lock·원자 연산은 별도로 유지합니다.',
    ('중첩 disable 두 번을 enable 한 번으로 모두 해제하는 계약인가요?', '아닙니다. 중첩 균형을 맞춰야 합니다.', '그렇습니다. 언제나 bool 하나만 끕니다.', '원문은 두 API가 nesting을 지원한다고 명시합니다. fixture도 중첩 상태를 따로 기록합니다.'),
    ('KCSAN 검사 중단이 공유 데이터 lock을 대신하나요?', '아닙니다. 검사 상태와 동기화는 다릅니다.', '그렇습니다. 다른 CPU의 접근이 멈춥니다.', 'API는 KCSAN의 현재 문맥 검사 동작을 조절합니다. 다른 실행 주체의 데이터 접근을 막는 API가 아닙니다.'))
row(K, 'KCSAN 번역 단위용 중단 alias·라이브러리 경계', '__kcsan_disable_current',
    '계측되는 번역 단위에서 __kcsan_disable_current는 kcsan_disable_current, __kcsan_enable_current는 enable_current_nowarn에 연결됩니다. 계측되지 않는 번역 단위에서는 둘 다 빈 inline입니다. 원문은 이 형태를 현재 번역 단위 접근의 검사를 끄는 용도로만 쓰라고 설명하며 라이브러리 호출은 여전히 검사할 수 있다고 경고합니다.',
    '호출한 helper가 다른 C 파일에 구현되어 있는지 확인하세요. 현재 파일에 들어간 alias와 라이브러리 구현의 계측 여부를 분리해서 읽습니다. 이 alias만으로 전체 call graph의 모든 검사를 껐다고 판단하지 않습니다.',
    ('계측 파일의 __kcsan_enable_current는 어느 경로인가요?', 'kcsan_enable_current_nowarn입니다.', '항상 schedule입니다.', '원문 alias는 uaccess에 안전한 nowarn 경로를 지정합니다. 이름이 비슷한 일반 enable과 구별합니다.'),
    ('현재 번역 단위용 alias로 모든 라이브러리 검사가 사라진다고 보장하나요?', '아닙니다. 라이브러리 호출은 검사할 수 있습니다.', '그렇습니다. 전체 커널을 끕니다.', '헤더 주석은 현재 compilation unit과 calls into libraries를 명시적으로 구별합니다.'))
row(K, 'KCSAN atomic 영역·중첩과 flat 프로토콜', 'kcsan_nestable_atomic_begin',
    'nestable_atomic_begin/end는 중첩 가능한 검사상 atomic 영역을 표시하고 flat_atomic_begin/end는 flat 영역을 표시합니다. 영역 내 접근을 KCSAN이 atomic으로 간주하도록 하는 주석 인터페이스입니다. 일반 load/store가 이 함수 호출 때문에 실제 CPU의 원자 RMW 명령으로 바뀌는 것은 아닙니다. 중첩 begin/end를 하나의 flat 상태 전환으로 섞지 않습니다.',
    '선택 fixture의 nestable 깊이와 flat 상태를 각각 추적하세요. 사용하는 프로토콜과 matching end를 확인합니다. 실제 원자성·순서·수명은 underlying access와 동기화 프로토콜로 충족해야 합니다.',
    ('nestable 영역 표시는 일반 load/store를 CPU 원자 RMW로 바꾸나요?', '아닙니다. KCSAN의 접근 해석을 조절합니다.', '그렇습니다. 모든 문장을 transaction으로 묶습니다.', '헤더 설명은 considered atomic이라고 합니다. 실제 데이터 접근 명령을 대신 생성하는 API가 아닙니다.'),
    ('flat begin/end를 중첩 깊이 계산과 같은 프로토콜로 섞어도 되나요?', '아닙니다. flat과 nestable을 구별합니다.', '그렇습니다. 이름만 다릅니다.', '두 별도 API의 영역 표현을 맞춰 사용해야 합니다. fixture도 상태와 중첩 깊이를 따로 모델링합니다.'))
row(K, 'KCSAN 다음 접근 개수·검사 해석의 제한된 구간', 'kcsan_atomic_next',
    'kcsan_atomic_next(n)은 현재 문맥의 다음 n번 메모리 접근을 atomic으로 간주하게 합니다. 개수 인자는 byte 수나 task 수가 아닙니다. 실제 원자성이나 이후 모든 실행 구간을 보장하는 기능도 아닙니다. 헤더의 ASSERT_EXCLUSIVE_BITS는 뒤따르는 한 접근을 낙관적으로 안전하다고 처리하기 위해 n=1을 사용합니다.',
    'n=1과 n=2가 어떤 접근 범위를 뜻하는지 다음 검사 지점을 표시해 보세요. 검사 annotation을 실제 READ_ONCE·cmpxchg 또는 lock의 대체품으로 삼지 않습니다. 음수나 임의 입력의 런타임 처리는 이 선언만으로 일반화하지 않습니다.',
    ('atomic_next(1)의 1은 무엇을 세나요?', '뒤따르는 메모리 접근 개수입니다.', '할당할 byte 수입니다.', '원문 매개변수 설명은 following memory accesses입니다. 길이 인자와 구별합니다.'),
    ('이 호출이 이후 모든 접근에 실제 원자성을 제공하나요?', '아닙니다. 정해진 검사 해석 구간입니다.', '그렇습니다. thread 전체가 원자 실행됩니다.', 'KCSAN의 분류 조절과 CPU 데이터 접근의 동기화 계약은 서로 다릅니다.'))
row(K, 'KCSAN 접근 mask·선택한 비트의 변화만 점검', 'kcsan_set_access_mask',
    'kcsan_set_access_mask(mask)는 현재 문맥에 비영 mask를 설정하면 해당 mask 비트의 값 변화만 보고하게 합니다. word 전체가 아니라 특정 bit 필드의 불변 조건을 검사하려는 목적입니다. 예를 들어 0x0f는 하위 네 비트를 선택하고 나머지 비트의 변화는 이 mask 검사에서 제외합니다. mask 0으로 다시 해제하는 상태 복구를 확인해야 합니다.',
    '공유 flags에서 lock으로 보호되는 비트와 독립적으로 갱신되는 비트를 나눠 그리세요. mask 범위를 정한다고 서로 다른 bit의 일반 read-modify-write가 자동으로 안전해지는 것은 아닙니다. 실제 갱신에는 적절한 원자 연산과 lock이 필요합니다.',
    ('mask 0x0f는 어떤 변화를 선택하나요?', '하위 네 비트의 값 변화입니다.', '상위 비트만 선택합니다.', '0x0f의 켜진 비트가 검사 대상입니다. mask는 다른 비트를 보호하는 lock이 아닙니다.'),
    ('검사 뒤 mask를 0으로 복구하는 이유는 무엇인가요?', '현재 문맥의 선택 비트 제한을 해제하기 위해서입니다.', '데이터 flags 자체를 0으로 쓰기 위해서입니다.', '접근 mask 상태와 대상 메모리의 실제 값은 별개입니다. 복구가 데이터 쓰기는 아닙니다.'))
row(K, 'KCSAN scoped 자료구조·union과 접근 위치', 'kcsan_scoped_access',
    'kcsan_scoped_access는 union 안에 list_head와 stack_depth를 둡니다. 리스트에 등록된 접근의 연결 정보와 아직 리스트 항목이 아닌 접근의 초기 stack 깊이를 같은 저장 공간의 대안으로 표현합니다. 이어서 ptr, size, type과 생성 위치 ip를 저장합니다. union 두 필드를 동시에 독립적으로 유지하는 구조로 읽으면 안 됩니다.',
    'ptr는 검사할 대상, size는 범위, ip는 설정 위치라는 역할을 주석으로 달아 보세요. 이 헤더는 자료구조의 형태와 인터페이스를 제공하며 내부 리스트 관리 알고리즘은 런타임 구현을 추가로 읽어야 합니다.',
    ('union의 list와 stack_depth는 독립 저장 공간 두 개인가요?', '아닙니다. 같은 공간의 대안입니다.', '그렇습니다. struct 두 필드와 같습니다.', '원문은 union을 사용합니다. list에 없는 접근의 초기 깊이라는 별도 역할을 주석으로 설명합니다.'),
    ('ip는 무엇을 기록하나요?', 'scoped 접근을 설정한 위치입니다.', '복사할 사용자 byte 수입니다.', '구조체의 마지막 주석은 Location where scoped access was set up이라고 설명합니다.'))
row(K, 'KCSAN scoped 등록·검사 구간과 런타임 진입', 'kcsan_begin_scoped_access',
    'begin_scoped_access는 호출자가 제공한 sa를 초기화하고 현재 실행 문맥의 내부 리스트에 등록하는 인터페이스입니다. end가 호출될 때까지 해당 범위를 scoped 검사 대상으로 유지합니다. 원문 설명의 continuously check는 런타임에 진입할 때 등록된 범위를 검사한다는 뜻이며 독립 감시 thread가 매 나노초 메모리를 읽는다고 해석하면 안 됩니다.',
    'sa의 지역 수명과 begin/end의 일치, 대상 메모리 수명을 함께 표시하세요. 선언과 주석의 계약을 이해한 뒤 실제 리스트 순회는 kernel/kcsan 구현에서 확인합니다. 선택 fixture는 begin/end 이벤트를 기록하며 실제 race detector를 실행하지 않습니다.',
    ('scoped 접근은 언제 재검사된다고 설명하나요?', 'KCSAN 런타임에 진입할 때입니다.', '항상 별도의 실시간 감시 thread에서입니다.', '주석은 내부 리스트에 추가하고 every call into the runtime에서 검사한다고 명시합니다.'),
    ('end에 전달하는 sa는 어떤 조건이 필요한가요?', '앞서 한 번 begin으로 초기화한 sa여야 합니다.', '임의 미초기화 포인터면 됩니다.', 'end의 매개변수 계약은 previously initialized struct이며 matching begin이 필요합니다.'))
row(K, 'KCSAN cleanup 속성·스코프 끝에서 종료 호출', '__ASSERT_EXCLUSIVE_SCOPED',
    '__ASSERT_EXCLUSIVE_SCOPED는 지역 sa에 __cleanup__(kcsan_end_scoped_access) 속성을 붙입니다. 지역 변수의 스코프가 끝나면 컴파일러가 종료 함수를 부릅니다. begin으로 등록하고 cleanup으로 종료하는 자원 수명 패턴입니다. 별도 dummy pointer는 begin의 반환 값을 받아 초기화를 실행하게 하며 __COUNTER__ 기반 이름은 같은 스코프의 선언 충돌을 피합니다.',
    '중괄호 안에 두 scoped 선언을 만들고 시작·끝 순서를 추적하세요. fixture에서는 실제 cleanup 속성을 실행하여 역순 종료를 확인했습니다. cleanup 호출은 KCSAN 인터페이스의 수명 관리이며 공유 객체 해제나 lock 해제를 자동으로 하지 않습니다.',
    ('cleanup 속성의 종료 함수는 어느 때 호출되나요?', '지역 변수의 스코프가 끝날 때입니다.', 'C 파일을 include할 때 한 번입니다.', '속성은 자동 지역 변수의 수명에 연결됩니다. begin/end 프로토콜을 지역 스코프로 표현합니다.'),
    ('__COUNTER__를 이름에 사용하는 목적은 무엇인가요?', '동일 스코프의 여러 선언 이름 충돌을 피합니다.', '대상 데이터에 1씩 더합니다.', '전처리 시 고유한 지역 이름을 만드는 용도이며 shared var의 값 갱신은 아닙니다.'))
row(K, 'KCSAN 비활성 구성·빈 scoped 구조체와 annotation', 'kcsan_end_scoped_access',
    'CONFIG_KCSAN이 꺼지면 scoped 구조체는 빈 구조체이고 cleanup macro는 __maybe_unused만 남습니다. begin은 전달받은 sa를 반환하며 end는 빈 inline입니다. 따라서 같은 호출 코드를 구성에 따라 컴파일할 수 있지만 런타임 검사는 제공하지 않습니다. GNU C의 빈 구조체와 조건부 전처리 구성을 표준 C의 모든 환경에 그대로 적용할 수 있다고 가정하지 않습니다.',
    '활성 분기와 비활성 분기의 같은 이름을 대응시키세요. 검사가 꺼졌다는 사실을 코드 자체의 안전성 증명으로 해석하지 않습니다. 모델은 비활성 구성도 컴파일·실행했으며 함수 호출 인자의 부수 효과는 별도로 확인했습니다.',
    ('비활성 begin의 반환 값은 무엇인가요?', '전달한 sa입니다.', '새로 할당한 검사 객체입니다.', '빈 inline 본문은 return sa입니다. 메모리를 새로 할당하거나 리스트를 관리하지 않습니다.'),
    ('KCSAN이 꺼진 구성에서 검사가 없다는 사실은 race가 없다는 증거인가요?', '아닙니다. 검사 기능이 없는 것입니다.', '그렇습니다. 모든 race가 제거됩니다.', '조건부 stub은 빌드 연결을 유지합니다. 실제 동시성 버그의 부재를 확인하는 기능이 아닙니다.'))
row(K, 'KCSAN weak memory 표시·signal fence의 재사용', '__KCSAN_BARRIER_TO_SIGNAL_FENCE',
    'WEAK_MEMORY와 번역 단위 계측이 함께 켜지면 barrier 표시 macro는 compiler barrier, __atomic_signal_fence, compiler barrier 순서입니다. thread sanitizer가 signal fence를 가로채는 경로를 이용해 KCSAN에 barrier 종류를 알립니다. mb에는 SEQ_CST, wmb에는 ACQ_REL, rmb에는 ACQUIRE, release에는 RELEASE 상수를 태그로 사용합니다. 원문은 이 대응이 임의이며 C11과 LKMM의 실제 순서 대응이 아니라고 강조합니다.',
    'compiler barrier와 KCSAN 이벤트, 아키텍처의 실제 CPU barrier를 각각 그리세요. 선택 fixture는 signal-fence 전달 이벤트와 마지막 release 태그를 검사했습니다. 그 결과로 실제 CPU 순서나 C11-LKMM 등가성을 증명했다고 주장하지 않습니다.',
    ('wmb에 사용된 ACQ_REL 상수는 C11-LKMM의 정확한 의미 대응인가요?', '아닙니다. 가로채기용 임의 태그입니다.', '그렇습니다. 두 메모리 모델이 동일하다는 증거입니다.', '헤더 주석은 mappings are arbitrary이며 실제 C11과 LKMM의 대응을 반영하지 않는다고 명시합니다.'),
    ('signal fence 양쪽의 barrier()는 어떤 층을 구별해야 하나요?', '컴파일러 장벽과 실제 CPU 장벽을 구별합니다.', '언제나 디스크 flush와 같습니다.', '이 계측 macro의 compiler barrier와 underlying asm/barrier.h의 하드웨어 동작은 별개입니다.'))
row(K, 'KCSAN weak memory 직접 hook·구성 우선순위', 'kcsan_mb',
    'WEAK_MEMORY가 켜지고 __SANITIZE_THREAD__가 없지만 __KCSAN_INSTRUMENT_BARRIERS__가 있으면 kcsan_mb/wmb/rmb/release는 직접 __kcsan_* hook의 alias가 됩니다. 앞선 signal-fence 분기가 먼저 선택되므로 두 조건을 만족하면 앞 분기가 적용됩니다. 둘 중 어느 계측 경로에도 해당하지 않으면 빈 do-while macro입니다.',
    'if, elif, else의 우선순위를 구성 표로 만드세요. 런타임 hook 유무를 실제 장벽 유무와 혼동하지 않습니다. underlying 장벽은 다른 헤더에서 제공되며 이 파일의 표시는 KCSAN에 관찰 정보를 전달합니다.',
    ('WEAK_MEMORY와 explicit 표시만 켜진 비계측 파일에서는 어떻게 연결되나요?', '직접 __kcsan barrier hook alias입니다.', '언제나 signal-fence 분기입니다.', '첫 분기는 __SANITIZE_THREAD__를 요구합니다. 없으면 explicit 분기의 조건을 확인합니다.'),
    ('어느 계측 분기도 선택되지 않으면 kcsan_mb의 본문은 무엇인가요?', '빈 do-while입니다.', '모든 CPU의 full fence를 직접 실행합니다.', 'else 분기는 빈 annotation macro입니다. 실제 arch barrier 구현과 구별합니다.'))
row(K, 'KCSAN atomic 검사·4·5·7과 IGNORE_ATOMICS', 'kcsan_check_atomic_read',
    'atomic read는 ATOMIC=4, atomic write는 ATOMIC|WRITE=5, atomic read-write는 ATOMIC|WRITE|COMPOUND=7을 전달합니다. CONFIG_KCSAN_IGNORE_ATOMICS가 켜지면 세 macro 모두 인자를 사용하지 않는 do-while입니다. 따라서 직접 macro에 쓴 부수 효과 인자도 평가하지 않습니다. 이 생략이 바깥 instrument_atomic_* 함수 호출의 인자 평가나 KASAN 검사까지 없애는 것은 아닙니다.',
    '직접 macro 호출과 instrument_atomic_read 함수 호출을 비교하세요. side_effect 인자를 annotation에 넣는 코드를 피합니다. 모델은 atomic 표시 값과 IGNORE 구성의 인자 생략, 바깥 KASAN 유지 경로를 구분해 검사했습니다.',
    ('atomic read-write의 플래그 값은 얼마인가요?', '4|1|2인 7입니다.', 'ASSERT 하나인 8입니다.', 'ATOMIC, WRITE, COMPOUND 세 비트가 함께 설정됩니다. assert는 별도 의미입니다.'),
    ('IGNORE_ATOMICS의 직접 macro 인자 side_effect()도 호출되나요?', '아닙니다. 이 macro는 인자 토큰을 사용하지 않습니다.', '그렇습니다. 빈 inline과 항상 같습니다.', '전처리에서 버리는 인자와 함수 호출 전에 평가하는 인자를 구분해야 합니다.'))
row(K, 'KCSAN 단일 writer assertion·표시된 접근의 불변 조건', 'ASSERT_EXCLUSIVE_WRITER',
    'ASSERT_EXCLUSIVE_WRITER(var)는 주소와 sizeof(var), ASSERT 플래그를 직접 검사에 전달합니다. 다른 reader는 허용하지만 concurrent writer가 없어야 한다는 불변 조건을 표현합니다. READ_ONCE/WRITE_ONCE로 표시된 접근끼리는 정상 data race로 분류되지 않아도 단일 writer 프로토콜을 위반할 수 있습니다. assertion은 그 상위 조건을 점검하며 실제 update lock은 호출자가 유지합니다.',
    '원문 writer 예제에서 spin_lock, assertion, WRITE_ONCE, unlock을 순서대로 읽으세요. reader가 lock 없이 읽을 수 있다는 사실과 둘 이상의 writer를 허용한다는 주장은 다릅니다. assertion 호출 자체가 lock을 획득하지 않습니다.',
    ('EXCLUSIVE_WRITER는 다른 concurrent reader도 금지하나요?', '아닙니다. reader는 허용합니다.', '그렇습니다. 모든 접근을 금지합니다.', '원문 계약은 no concurrent writes이며 other readers are allowed입니다.'),
    ('WRITE_ONCE로 표시한 두 writer의 프로토콜 위반도 점검하려는 이유는 무엇인가요?', '표시된 접근이라 정상 data race 분류만으로 놓칠 수 있기 때문입니다.', 'WRITE_ONCE가 모든 lock을 제공하기 때문입니다.', '접근 표시와 단일 writer라는 상위 불변 조건은 다릅니다. ASSERT는 후자를 명시합니다.'))
row(K, 'KCSAN scoped writer assertion·구간 중 상태 변경', 'ASSERT_EXCLUSIVE_WRITER_SCOPED',
    'scoped writer assertion은 ASSERT|SCOPED=24를 사용하여 선언된 스코프 동안 다른 writer가 없어야 한다는 조건을 유지합니다. 원문은 한 writer가 42를 쓴 뒤 같은 구간에서 42가 유지되어야 하지만 buggy writer가 1로 바꾸는 예를 듭니다. 한 지점의 assertion을 여러 번 넣는 것보다 명확한 구간을 덮어 탐지 가능성을 높이며 완전 탐지 보장은 아닙니다.',
    '실제 lock 구간 안의 중괄호 수명과 assertion 수명을 맞춰 보세요. 선언 위치부터 스코프 종료까지를 표시합니다. 구조체 cleanup은 assertion 등록을 끝내며 대상 메모리 값을 자동으로 원래 값에 복원하지 않습니다.',
    ('scoped writer의 기본 type 조합은 무엇인가요?', 'ASSERT|SCOPED인 24입니다.', 'WRITE|ATOMIC인 5입니다.', 'writer assertion은 다른 writer를 찾는 readlike ASSERT 형태입니다. SCOPED 16을 더합니다.'),
    ('scoped assertion이 끝나면 바뀐 shared 값도 복원하나요?', '아닙니다. 검사 등록만 종료합니다.', '그렇습니다. 자동 rollback입니다.', 'cleanup은 kcsan_end_scoped_access를 호출합니다. 데이터 transaction이나 복원 기능은 없습니다.'))
row(K, 'KCSAN 독점 access assertion·객체 재사용과 수명', 'ASSERT_EXCLUSIVE_ACCESS',
    'ASSERT_EXCLUSIVE_ACCESS는 WRITE|ASSERT=9로 reader와 writer 모두 없어야 한다는 조건을 검사합니다. 원문은 refcount가 마지막 사용자임을 나타낸 뒤 cleanup하고 객체를 재사용하는 경우를 예로 듭니다. 실제 객체를 해제한 뒤의 use-after-free 탐지는 KASAN이 더 적합하다고 설명합니다. refcount 결과나 assertion만으로 잘못된 외부 포인터까지 안전하게 만들어 주지는 않습니다.',
    '마지막 참조 판단, 독점 조건 점검, cleanup, 재사용을 구분해 주석을 달아 보세요. 실제 free와 재사용 대기를 혼동하지 않습니다. 단일 writer assertion과 달리 reader도 허용하지 않는 계약을 확인합니다.',
    ('EXCLUSIVE_ACCESS는 concurrent reader를 허용하나요?', '아닙니다. reader와 writer 모두 없어야 합니다.', '그렇습니다. writer만 금지합니다.', 'ACCESS와 WRITER는 계약이 다릅니다. ACCESS는 no readers nor writers라고 명시합니다.'),
    ('원문은 실제 free 뒤 use-after-free에 어느 도구가 더 적합하다고 하나요?', 'KASAN입니다.', '이 assertion이 객체를 다시 할당합니다.', '주석은 객체가 freed되는 경우 KASAN을 더 적합한 탐지 도구로 설명합니다.'))
row(K, 'KCSAN scoped 독점 access·25와 범위 수명', 'ASSERT_EXCLUSIVE_ACCESS_SCOPED',
    'scoped access assertion은 WRITE|ASSERT|SCOPED=25입니다. 지역 선언부터 종료까지 reader나 writer가 없어야 한다는 조건을 등록합니다. __COUNTER__로 생성한 지역 구조체와 cleanup은 동일한 구현 helper를 공유하되 writer scoped의 type 24와 구별됩니다. 독점 구간의 검사일 뿐 다른 CPU를 정지시키는 실행 제어는 아닙니다.',
    'writer scoped 24와 access scoped 25를 이진수로 비교하세요. 대상의 주소·크기와 sa 지역 수명을 함께 추적합니다. 실제 불변 조건을 충족할 동기화·참조 프로토콜이 먼저 필요합니다.',
    ('scoped access의 type 값은 얼마인가요?', 'WRITE|ASSERT|SCOPED인 25입니다.', 'ASSERT|SCOPED인 24입니다.', 'access는 writer scoped와 달리 WRITE 비트도 사용하여 다른 read를 충돌 검사 대상으로 표현합니다.'),
    ('scoped access assertion이 다른 CPU의 reader를 물리적으로 멈추나요?', '아닙니다. 독점 불변 조건을 검사합니다.', '그렇습니다. 전역 CPU 정지 API입니다.', '검사 annotation은 실행 제어 lock이 아닙니다. 별도 동기화 프로토콜이 필요합니다.'))
row(K, 'KCSAN bit assertion·mask 복구와 바로 다음 접근', 'ASSERT_EXCLUSIVE_BITS',
    'ASSERT_EXCLUSIVE_BITS는 mask 설정→주소·크기의 ASSERT 검사→mask 0 복구→atomic_next(1) 순서입니다. 선택한 비트에는 concurrent writer가 없어야 하지만 나머지 비트의 접근은 허용하는 불변 조건입니다. 바로 다음 접근이 선택 비트만 읽는다는 가정으로 낙관적 atomic 표시를 붙입니다. 원문은 compiler의 bit 최적화까지 모두 추론할 수 없어 READ_ONCE가 여전히 바람직할 수 있다고 설명합니다.',
    'flags의 READ_ONLY_MASK와 그 직후 READ_ONCE(flags)&mask를 연결하세요. 중간에 다른 메모리 접근을 넣어 다음 접근의 의미를 흐리지 않습니다. 검사 mask와 실제 cmpxchg retry, 각 bit의 lock 규칙을 따로 유지합니다.',
    ('bit assertion 뒤 mask와 다음 접근 상태는 어떤 순서인가요?', 'mask를 0으로 복구한 뒤 atomic_next(1)입니다.', 'mask를 계속 유지하고 모든 접근을 atomic으로 합니다.', 'macro 마지막 두 호출의 순서를 확인하세요. 선택 검사 상태가 뒤 코드에 계속 남는 형태가 아닙니다.'),
    ('KCSAN이 다음 접근을 낙관적으로 처리하면 READ_ONCE는 항상 불필요한가요?', '아닙니다. compiler bit 최적화 때문에 여전히 권장될 수 있습니다.', '그렇습니다. 모든 compiler 변환이 증명되었습니다.', '원문은 모든 bit manipulation 최적화를 추론할 수 없다고 설명하며 READ_ONCE 사용을 주의 깊게 권합니다.'))

row(A, 'KASAN 접근 검사·software 모드와 직접 API', '__kasan_check_read',
    '이 헤더의 접근 annotation은 compiler 계측을 쓰는 software KASAN용입니다. CONFIG_KASAN_GENERIC 또는 CONFIG_KASAN_SW_TAGS이면 __kasan_check_read/write가 bool 반환 함수로 선언되고 그 외 구성에서는 true를 반환하는 inline입니다. 직접 API는 선택적으로 계측을 끈 C 파일에서도 software KASAN 검사를 호출할 수 있지만 원문은 헤더에서 사용하지 말라고 명시합니다.',
    'generic, software tags와 hardware tags를 먼저 구분하세요. direct와 public 계층을 같은 기능으로 단정하지 않습니다. 이 수업은 접근 검사 인터페이스를 읽으며 shadow·tag 자료구조의 내부 알고리즘은 별도 구현에서 공부합니다.',
    ('직접 software KASAN 검사 선언을 선택하는 두 설정은 무엇인가요?', 'KASAN_GENERIC 또는 KASAN_SW_TAGS입니다.', 'CONFIG_SMP 하나입니다.', '전처리 조건은 generic과 software tags입니다. 하드웨어 tag 모드를 같은 분기로 묶지 않습니다.'),
    ('직접 __kasan_check_*를 헤더에서 쓰라는 계약인가요?', '아닙니다. 헤더에서는 쓰지 말라고 합니다.', '그렇습니다. 모든 헤더가 직접 검사를 강제합니다.', '원문은 Never use these in header files라고 합니다. 공개 계층의 조건과 구별합니다.'))
row(A, 'KASAN 공개 접근·번역 단위와 true stub', 'kasan_check_read',
    '__SANITIZE_ADDRESS__가 있으면 공개 kasan_check_read/write는 직접 API의 alias이고 없으면 true 반환 inline입니다. stub의 true는 검사를 실행해 주소가 유효하다고 확인했다는 뜻이 아닙니다. 해당 번역 단위에 이 annotation의 검사 경로가 없는 구성일 수 있습니다. software 모드 설정과 현재 파일의 address instrumentation 조건을 따로 읽어야 합니다.',
    '커널 설정은 켜졌지만 현재 파일의 계측만 꺼진 조합을 비교하세요. bool 반환과 실제 검사 수행 여부를 각각 기록합니다. 부수 효과 인자 평가는 빈 함수 본문과 별개이므로 검사 표현식에 데이터 갱신을 숨기지 않습니다.',
    ('공개 접근 alias를 선택하는 현재 파일 표시는 무엇인가요?', '__SANITIZE_ADDRESS__입니다.', '언제나 __SANITIZE_THREAD__입니다.', 'address와 thread sanitizer의 번역 단위 표시는 다른 매크로입니다.'),
    ('stub에서 true가 왔으면 실제 주소 검사에 통과한 것인가요?', '아닙니다. 검사 없는 구성의 반환 값일 수 있습니다.', '그렇습니다. 모든 주소의 안전성이 확인됐습니다.', 'stub 본문은 그냥 return true입니다. 검사 여부와 bool 값의 의미를 구성에 맞춰 읽습니다.'))
row(A, 'KASAN hardware tags·이 annotation의 적용 한계', 'kasan_check_write',
    '헤더 주석은 이 annotation이 hardware tag-based KASAN에서 최적화로 사라진다고 설명하고 그 모드에는 kasan_check_byte를 사용하라고 안내합니다. 같은 KASAN 이름 아래에서도 compiler 기반 software 검사와 hardware tag 동작 경로가 다릅니다. 이 헤더의 software 검사 호출을 확인했다고 hardware tag 검사 엔진 전체를 검증한 것은 아닙니다.',
    '현재 빌드의 KASAN 모드를 확인하고 모드에 맞는 인터페이스를 찾아보세요. 여기서는 kasan_check_byte의 안내만 대조하며 그 다른 함수의 내부 구현까지 완료로 표시하지 않습니다.',
    ('hardware tag 모드에서는 이 헤더 주석이 어느 검사로 안내하나요?', 'kasan_check_byte입니다.', 'kcsan_atomic_next입니다.', '원문 첫 주석은 hardware tag 모드에서 이 annotation이 사라질 수 있으므로 byte 검사 사용을 안내합니다.'),
    ('software 접근 검사 fixture가 hardware tag 엔진 검증도 끝냈나요?', '아닙니다. 서로 다른 적용 경로입니다.', '그렇습니다. 이름이 같으면 내부가 같습니다.', '선택 모델은 이 헤더의 구성 분기를 검사합니다. 실제 hardware tag 동작은 실행하지 않았습니다.'))
row(A, 'KASAN 길이 타입·unsigned int 경계와 전달', '__kasan_check_write',
    '__kasan_check_read/write의 size 매개변수는 unsigned int입니다. 바깥 instrument_*는 size_t를 받으므로 호출 시 타입 변환이 생길 수 있습니다. 64비트 모델에서 UINT_MAX+1을 recorder에 전달하면 KASAN의 길이는 0, size_t를 받는 KCSAN은 원래 큰 값을 기록했습니다. 이는 타입 경계를 드러내는 주입 검사이며 실제 거대한 버퍼 접근을 안전하게 검사한 실험이 아닙니다.',
    '호출자 size_t와 callee unsigned int의 폭을 표시하세요. 정상 객체 크기와 유효 범위 계약을 먼저 확인합니다. recorder에 전달한 비정상 큰 길이의 결과를 실제 copy의 허용 범위로 해석하지 않습니다.',
    ('이 직접 KASAN 함수의 길이 매개변수 타입은 무엇인가요?', 'unsigned int입니다.', '모든 플랫폼에서 size_t입니다.', '선언의 실제 타입을 확인하세요. 바깥 wrapper의 size_t와 같은 이름의 크기 인자라도 타입은 다릅니다.'),
    ('큰 길이 recorder 실험은 실제 거대한 접근의 안전성을 검증했나요?', '아닙니다. 타입 변환 경계만 검사했습니다.', '그렇습니다. UINT_MAX보다 큰 모든 버퍼를 검증했습니다.', 'fixture는 실제 huge access를 하지 않았습니다. 기록한 인자 변환과 실제 주소 유효성을 구별합니다.'))

row(M, 'KMSAN poison·미초기화 표시와 origin', 'kmsan_poison_memory',
    'kmsan_poison_memory는 범위를 uninitialized로 표시하는 인터페이스입니다. 오류 보고의 origin은 이 호출 위치를 가리키며 flags는 함수가 수행하는 할당의 GFP flags입니다. 초기화 여부를 추적하는 metadata와 실제 buffer byte의 값을 구별해야 합니다. poison 표시를 데이터를 특정 poison 패턴으로 쓰는 일반 memset처럼 해석하지 않습니다.',
    'address, size, flags의 역할을 각각 주석으로 달아 보세요. 실제 데이터 쓰기 이후의 초기화 상태 전달을 추적합니다. 선택 fixture는 호출 위치의 실제 origin 엔진을 실행하지 않고 주소·길이·flags 전달만 기록합니다.',
    ('flags는 무엇을 위한 인자인가요?', '이 함수의 할당에 사용할 GFP flags입니다.', '채울 buffer의 byte 값입니다.', 'kernel-doc은 GFP flags for allocations done by this function이라고 설명합니다.'),
    ('poison 인터페이스를 일반 데이터 memset으로 읽어도 되나요?', '아닙니다. 미초기화 metadata 표시를 구별합니다.', '그렇습니다. 모든 byte를 0으로 만듭니다.', '헤더 계약은 initialized 상태 추적입니다. 실제 데이터 값의 초기화와 혼동하지 않습니다.'))
row(M, 'KMSAN unpoison·초기화 표시와 실제 초기화', 'kmsan_unpoison_memory',
    'kmsan_unpoison_memory는 지정 범위를 initialized로 표시합니다. 이름에 초기화 의미가 있다고 실제 데이터 byte를 0으로 채우는 함수가 아닙니다. compiler가 보지 못한 유효한 외부 데이터 전달을 metadata에 반영할 때 쓰는 annotation입니다. 실제로 채우지 않은 범위를 무조건 unpoison하면 미초기화 사용 탐지를 가릴 수 있습니다.',
    '사용자 copy의 실제 복사 완료 길이와 unpoison 길이를 맞춰 보세요. 먼저 데이터가 유효하게 기록되고 그 사실을 추적기에 알리는 관계를 이해합니다. CONFIG_KMSAN이 없으면 빈 inline이라는 구성도 따로 확인합니다.',
    ('unpoison은 실제 대상 byte를 0으로 쓰나요?', '아닙니다. initialized metadata 표시입니다.', '그렇습니다. 보안 memset입니다.', '계약은 Mark the memory range as initialized입니다. 데이터 초기화 함수로 사용하지 않습니다.'),
    ('아직 채우지 않은 전체 버퍼를 unpoison하면 어떤 문제가 있나요?', '미초기화 사용 탐지를 가릴 수 있습니다.', '자동으로 원래 데이터를 복원합니다.', 'metadata에 거짓 초기화 상태를 알리면 실제 미초기화 byte를 추적하는 목적을 훼손합니다.'))
row(M, 'KMSAN check·일부 미초기화 byte와 범위 검사', 'kmsan_check_memory',
    'kmsan_check_memory는 범위가 initialized인지 확인하고 일부라도 uninitialized로 표시되어 있으면 오류를 보고하는 인터페이스입니다. 읽기·쓰기 race를 검사하는 KCSAN이나 주소 접근 유효성을 다루는 KASAN과 질문이 다릅니다. 이 선언은 metadata 해석 계약을 설명하며 실제 shadow 저장·origin 추적 구현은 포함하지 않습니다.',
    '같은 버퍼에 대해 주소가 유효한가, 초기화되어 있는가, 동시 접근이 안전한가를 세 질문으로 나눠 보세요. 선택 recorder는 check 요청의 인자 전달을 확인할 뿐 실제 미초기화 오류 보고를 생성하지 않습니다.',
    ('범위 일부만 미초기화여도 원문 계약상 오류인가요?', '그렇습니다. any piece가 미초기화면 보고합니다.', '아닙니다. 모든 byte가 미초기화여야 합니다.', 'kernel-doc은 any piece of the given range라고 명시합니다. 전체가 아닌 일부도 검사 대상입니다.'),
    ('이 검사와 KCSAN의 주된 질문은 같은가요?', '아닙니다. 초기화 상태와 동시 접근은 다릅니다.', '그렇습니다. 모두 lock을 자동 획득합니다.', '도구의 점검 대상과 동기화 제공 여부를 구별합니다. check 호출은 lock 획득 API가 아닙니다.'))
row(M, 'KMSAN 사용자 전달·미초기화 정보 유출과 left', 'kmsan_copy_to_user',
    'kmsan_copy_to_user(to,from,to_copy,left)는 실제 사용자 공간 전달이면 복사된 byte의 초기화 상태를 검사하여 미초기화 정보 유출을 찾습니다. left는 복사하지 못한 수입니다. 요청 8, left 3이면 실제 전달은 5입니다. compat syscall 때문에 to가 커널 공간을 가리키는 경우에는 metadata만 복사한다는 별도 계약이 있습니다.',
    'kernel from에서 user to로 향하는 화살표를 그리세요. 요청 크기와 남은 길이, 실제 전달 길이를 구별합니다. 주소 공간 판별과 leak 보고 엔진은 이 헤더의 선언 밖 구현이며 선택 모델은 인자를 기록합니다.',
    ('요청 8byte, left 3이면 실제 전달 수는 얼마인가요?', '5byte입니다.', '11byte입니다.', 'left는 미복사 수이므로 요청에서 빼야 합니다. 유효한 residual 계약은 0 이상 요청 이하입니다.'),
    ('compat 경로에서 to가 커널 공간이면 원문은 무엇을 하도록 설명하나요?', 'metadata를 복사합니다.', '항상 사용자 정보 유출로 보고합니다.', 'kernel-doc은 실제 사용자 전달과 커널 to 경로를 구별합니다. 주소 공간에 따라 목적이 달라집니다.'))
row(M, 'KMSAN memmove·데이터 복사 뒤 metadata 이동', 'kmsan_memmove',
    'kmsan_memmove는 assembly 등 비계측 memmove/memcpy가 데이터를 옮긴 뒤 KMSAN metadata를 옮기기 위해 호출하는 인터페이스입니다. 이 이름의 호출 자체가 buffer의 실제 데이터 복사를 대신하지 않습니다. source의 초기화 상태를 destination에 전달해 복사로 생긴 데이터와 추적 상태를 일치시키는 목적입니다.',
    '실제 비계측 copy와 뒤 metadata notification을 두 단계로 나눠 적으세요. 부분 copy이면 실제 이동한 범위만 반영합니다. fixture는 실제 shadow copy를 수행하지 않으므로 source 상태 전파 알고리즘 검증으로 과장하지 않습니다.',
    ('이 notification은 비계측 데이터 복사 앞인가요 뒤인가요?', '뒤에 호출합니다.', '항상 데이터 복사 전에 호출합니다.', 'kernel-doc은 Invoked after non-instrumented version이라고 설명합니다.'),
    ('kmsan_memmove 하나만 호출하면 실제 데이터 copy도 끝나나요?', '아닙니다. metadata notification을 구별합니다.', '그렇습니다. 일반 memcpy와 완전히 같습니다.', '이 API의 목적은 KMSAN metadata 복사입니다. 실제 데이터 이동은 앞의 비계측 copy가 수행합니다.'))
row(M, 'KMSAN 비활성 구성·빈 함수와 검사 부재', 'kmsan_check_memory',
    'CONFIG_KMSAN이 꺼지면 poison, unpoison, check, copy_to_user, memmove는 모두 빈 inline 함수입니다. 구성과 무관하게 호출 코드를 연결하기 위한 stub이며 미초기화 오류가 없음을 증명하는 구현이 아닙니다. 함수 인자 표현식의 부수 효과는 비활성 함수 본문과 구별해야 합니다.',
    '활성 선언 다섯 개와 else의 다섯 inline을 대응시키세요. 기능이 꺼진 실행에서 오류가 안 보였다는 결과를 버퍼 초기화 증거로 사용하지 않습니다. 선택 모델은 enabled/disabled 구성 모두 컴파일하고 전달 경로를 검사했습니다.',
    ('CONFIG_KMSAN이 없으면 check의 본문은 무엇인가요?', '빈 inline입니다.', '항상 전체 buffer를 0으로 채웁니다.', 'else 분기의 실제 본문을 확인하세요. 추적 엔진이나 데이터 초기화는 없습니다.'),
    ('비활성 구성에서 오류 보고가 없으면 초기화 검증 완료인가요?', '아닙니다. 검사 기능이 꺼져 있습니다.', '그렇습니다. 모든 source byte가 검증됐습니다.', '검사 미실행과 검사 통과를 구별해야 합니다. stub의 목적은 조건부 빌드 연결입니다.'))

row(I, '수동 접근 계측·컴파일러가 보지 못하는 경로', 'instrument_read',
    'instrumented.h는 compiler가 자동 계측을 넣을 수 없는 메모리 접근에 KASAN·KCSAN·KMSAN annotation을 연결합니다. instrument_read는 KASAN read, KCSAN read 순서이며 실제 read 전에 삽입합니다. 함수를 호출했다고 대상 데이터 값을 읽어 반환하거나 lock을 잡는 것은 아닙니다. 실제 접근과 그 접근을 알리는 hook의 역할을 분리해야 합니다.',
    'assembly나 custom primitive의 실제 접근 앞에 주소와 길이 annotation이 오는지 확인하세요. 같은 주소라도 초기화·주소 유효성·race 검사의 질문은 다릅니다. 각 sanitizer의 구성에 따라 hook이 생략될 수 있습니다.',
    ('instrument_read의 두 hook 순서는 무엇인가요?', 'KASAN read 뒤 KCSAN read입니다.', 'KMSAN 데이터 copy 하나뿐입니다.', '본문의 호출 순서를 직접 확인하세요. 실제 데이터 read는 이 함수 뒤 underlying 연산에서 발생합니다.'),
    ('이 wrapper는 실제 데이터 read의 앞에 넣나요?', '그렇습니다. 실제 read 전에 넣습니다.', '언제나 read가 끝난 뒤만 넣습니다.', 'kernel-doc은 before the actual read happens라고 명시합니다. metadata after-copy hook과 구별합니다.'))
row(I, '수동 write 계측·크기와 접근 방향', 'instrument_write',
    'instrument_write는 대상 주소에 KASAN write와 KCSAN write 검사를 알립니다. 실제 write 전에 호출하며 size는 접근 byte 수입니다. 읽기 검사와 쓰기 검사는 동일 주소에도 다른 접근 성질을 전달합니다. void wrapper는 KASAN의 bool 반환을 사용해 실제 write를 허가하거나 차단하는 분기를 만들지 않습니다.',
    'custom store의 대상과 size를 표시하고 그 앞 annotation을 대조하세요. selected fixture에서 KASAN recorder를 false로 만들어도 뒤 KCSAN 호출이 이어지는 것을 확인했습니다. 이 결과는 실제 KASAN reporting·panic 정책을 대신 모델링하지 않습니다.',
    ('instrument_write에서 KASAN bool을 검사해 KCSAN 호출을 막나요?', '아닙니다. 본문은 두 호출을 순서대로 수행합니다.', '그렇습니다. false면 return 분기가 있습니다.', '본문에는 bool 분기가 없습니다. fixture의 false recorder 결과와 실제 detector reporting 정책을 구별합니다.'),
    ('이 wrapper의 size는 무엇인가요?', '대상 write의 byte 수입니다.', '공유 객체의 참조 수입니다.', '함수 설명은 size of access입니다. 실제 접근의 주소·범위·방향을 일치시켜야 합니다.'))
row(I, '수동 read-write 계측·KASAN write와 KCSAN compound', 'instrument_read_write',
    'instrument_read_write는 KASAN에는 write 검사, KCSAN에는 read-write 검사를 전달합니다. KCSAN의 COMPOUND|WRITE는 읽고 수정해 쓰는 복합 성질을 나타내며 단순 read 검사 두 개로 대체한 구현이 아닙니다. 함수 이름이 read_write라고 KASAN read와 write를 모두 별도로 호출한다고 추측하면 틀립니다.',
    '두 detector에 전달하는 서로 다른 분류를 표로 적으세요. 실제 RMW 원자성과 보호 protocol은 underlying 연산에서 확인합니다. 계측 wrapper가 일반 load와 store를 분리 불가능한 RMW로 바꾸지 않습니다.',
    ('이 wrapper가 KASAN에 호출하는 검사는 무엇인가요?', 'write 검사입니다.', 'read와 write 두 함수를 모두 호출합니다.', '본문은 kasan_check_write 하나와 kcsan_check_read_write 하나입니다. 이름만으로 호출 수를 추측하지 않습니다.'),
    ('KCSAN에는 어느 일반 접근 type이 전달되나요?', 'COMPOUND|WRITE인 3입니다.', '읽기 전용 0입니다.', 'read-write macro는 복합 RMW 성질을 두 플래그로 표현합니다. 실제 CPU 원자성을 제공하는 hook은 아닙니다.'))
row(I, '수동 atomic 계측·KASAN 검사는 여전히 필요하다', 'instrument_atomic_read_write',
    'atomic read/write/read-write wrapper는 KASAN에는 보통 read 또는 write 주소 검사를 전달하고 KCSAN에는 atomic 분류를 전달합니다. atomic이라는 이유로 해제된 주소나 범위를 벗어난 접근이 유효해지지 않기 때문입니다. IGNORE_ATOMICS 구성은 KCSAN atomic macro를 비우지만 바깥 함수 인자 평가와 KASAN 호출은 남을 수 있습니다.',
    'atomic read, write, RMW의 KASAN 방향과 KCSAN 4·5·7을 비교하세요. 구성별로 생략되는 층을 확인합니다. 실제 접근 전에 annotation을 넣고 underlying atomic API의 ordering 계약은 별도로 공부합니다.',
    ('KCSAN이 atomic 접근을 무시하면 KASAN 주소 검사도 반드시 없어지나요?', '아닙니다. 두 sanitizer의 경로는 별개입니다.', '그렇습니다. 모든 계측을 끕니다.', 'IGNORE_ATOMICS는 KCSAN macro를 비웁니다. instrument_atomic_*의 KASAN 호출은 다른 조건을 따릅니다.'),
    ('atomic read-write wrapper의 KASAN 방향은 무엇인가요?', 'write입니다.', '주소 검사 자체가 없습니다.', '원문은 kasan_check_write와 kcsan_check_atomic_read_write를 호출합니다. 원자 접근도 유효 주소가 필요합니다.'))
row(I, '사용자 copy-out 계측·커널 source의 읽기', 'instrument_copy_to_user',
    'instrument_copy_to_user는 커널 from의 n byte를 KASAN read, KCSAN read로 알리고 KMSAN copy_to_user(to,from,n,0)를 호출합니다. 사용자 to를 커널 write 검사에 그대로 넣는 방향이 아닙니다. 이 hook은 실제 접근 전에 사용하므로 전달된 left=0은 이 annotation의 요청 형태이지 그 시점에 실제 copy가 모두 완료됐다는 증거가 아닙니다.',
    'kernel source→user destination 화살표를 그리고 검사 주소가 from임을 표시하세요. 접근 전 요청 검사와 실제 copy 반환 residual을 구별합니다. wrapper는 실제 사용자 copy를 수행하지 않습니다.',
    ('KASAN과 KCSAN에 전달하는 copy-out 검사 주소는 무엇인가요?', '커널 source인 from입니다.', '사용자 destination인 to입니다.', '본문은 check_read(from,n)입니다. 커널 memory에서 사용자에게 나가는 데이터의 읽기를 계측합니다.'),
    ('hook의 left=0이 호출 시 이미 실제 copy 완료를 증명하나요?', '아닙니다. 이 hook은 실제 접근 전에 호출합니다.', '그렇습니다. 반환된 성공 결과입니다.', '0은 annotation이 전달하는 인자입니다. 실제 copy 실행과 반환 상태를 이 hook이 대신 제공하지 않습니다.'))
row(I, '사용자 copy-in 전 계측·커널 destination의 쓰기', 'instrument_copy_from_user_before',
    'copy_from_user_before는 사용자 from에서 커널 to로 전달될 데이터를 위해 커널 to의 n byte를 KASAN write, KCSAN write로 알립니다. from은 이 wrapper 본문의 주소 검사 대상이 아닙니다. raw user pointer를 KASAN의 커널 read 검사에 넣는 형태로 이해하면 주소 공간의 방향을 거꾸로 읽은 것입니다.',
    'user source→kernel destination 화살표를 그리고 before 검사 주소와 after metadata 주소를 연결하세요. 이 annotation 자체가 사용자 주소 검증이나 실제 copy를 수행하는 uaccess 함수는 아닙니다.',
    ('copy-in before hook은 어느 주소를 write로 검사하나요?', '커널 destination인 to입니다.', '사용자 source인 from입니다.', '함수 본문은 check_write(to,n) 두 호출입니다. copy 방향과 커널 접근 방향을 같이 읽습니다.'),
    ('from 인자가 있으므로 본문이 user source의 KASAN read도 하나요?', '아닙니다. 그 호출은 없습니다.', '그렇습니다. 모든 인자를 항상 검사합니다.', '매개변수와 실제 본문의 사용을 구별하세요. 이 hook의 목적은 커널 destination write 계측입니다.'))
row(I, '사용자 copy-in 뒤 계측·n-left만 initialized', 'instrument_copy_from_user_after',
    'copy_from_user_after는 kmsan_unpoison_memory(to,n-left)를 호출합니다. 요청 8byte 중 3byte가 남으면 성공한 5byte의 initialized metadata만 반영합니다. before의 주소·race 검사와 after의 초기화 표시를 구별합니다. 이 본문은 left<=n을 내부 검사하지 않으므로 호출자의 정상 residual 계약이 필요합니다.',
    '0<=left<=n을 먼저 확인하고 완전 실패 left=n, 완전 성공 left=0, 부분 성공을 계산하세요. left>n 주입은 unsigned 뺄셈 경계를 recorder로 확인한 것이며 실제 huge unpoison을 실행한 실험은 아닙니다.',
    ('n=8, left=3에서 after가 unpoison하는 길이는 얼마인가요?', '5byte입니다.', '8byte 전부입니다.', '본문은 n-left입니다. 실제 복사하지 못한 tail의 초기화 상태까지 성공으로 표시하지 않습니다.'),
    ('after hook 안에 left<=n 검증 분기가 있나요?', '아닙니다. 호출자의 유효 residual 계약이 필요합니다.', '그렇습니다. 자동 clamp합니다.', '본문의 unsigned n-left를 확인하세요. 비정상 주입 기록은 실제 유효 copy 계약을 확장하지 않습니다.'))
row(I, '비계측 memcpy 전 hook·네 호출의 정확한 순서', 'instrument_memcpy_before',
    'memcpy_before는 KASAN destination write→KASAN source read→KCSAN destination write→KCSAN source read 순서로 접근을 알립니다. destination과 source 각각의 계측이 필요합니다. 검사 호출을 했다고 실제 데이터 copy가 실행되지는 않습니다. 사용자 copy용 before와 달리 두 주소 모두 커널 copy의 접근 대상입니다.',
    'custom assembly memcpy 앞에 네 hook의 대상·방향·순서를 주석으로 쓰세요. 검사할 n이 실제 접근 길이와 맞는지 확인합니다. 실제 복사 뒤 metadata 반영은 별도 after hook으로 연결합니다.',
    ('memcpy before의 첫 두 호출은 어떤 순서인가요?', 'KASAN destination write, source read입니다.', 'KCSAN source read만 두 번입니다.', '원문은 KASAN 두 호출 뒤 KCSAN 두 호출입니다. source와 destination 방향을 혼동하지 않습니다.'),
    ('before hook 하나가 실제 memcpy도 수행하나요?', '아닙니다. 접근 계측을 알립니다.', '그렇습니다. 일반 memcpy의 반환 값도 제공합니다.', '본문에는 데이터 copy 연산이 없습니다. underlying custom copy와 annotation을 구분합니다.'))
row(I, '비계측 memcpy 뒤 hook·복사된 길이의 상태 전파', 'instrument_memcpy_after',
    'memcpy_after는 kmsan_memmove(to,from,n-left)를 호출하여 실제 복사된 범위의 metadata를 전달합니다. n=8,left=3이면 5byte이고 left=n이면 0byte입니다. unpoison으로 모두 초기화됐다고 선언하는 사용자 copy-in과 달리 커널 source의 초기화 상태를 destination에 복사하는 계약입니다.',
    '커널 source가 미초기화일 수도 있다는 점을 고려해 unpoison과 metadata copy의 차이를 설명하세요. 정상 residual 조건을 유지하고 실제 데이터 copy가 끝난 뒤 hook을 사용합니다. recorder는 shadow 전파 엔진 자체를 실행하지 않습니다.',
    ('memcpy after는 어떤 notification을 사용하나요?', 'kmsan_memmove입니다.', '항상 kmsan_unpoison_memory입니다.', '커널 source의 초기화 상태를 옮기는 것과 destination을 무조건 초기화됐다고 표시하는 것은 다릅니다.'),
    ('n=8,left=8에서 전달하는 metadata 길이는 얼마인가요?', '0byte입니다.', '8byte입니다.', '복사된 수는 n-left입니다. 완전 미복사이면 전파할 범위도 0입니다.'))
row(I, 'get_user 계측·주소를 취할 수 없는 지역 변수', 'instrument_get_user',
    'instrument_get_user(to)는 to 값을 u64 __tmp로 잡고 그 지역 변수의 8byte를 unpoison한 뒤 다시 to에 대입합니다. to 자체의 주소를 취하지 않으므로 원문이 말하는 address-taken이 불가능한 변수에도 대응하는 형태입니다. GNU statement expression의 지역 임시값을 이용하며 실제 get_user 데이터 전달 시점은 uaccess 구현에 따라 before 또는 after일 수 있다고 설명합니다.',
    '안정적인 scalar lvalue를 대상으로 임시값→metadata→대입을 펼쳐 보세요. to 표현식은 값 읽기와 대입 위치에서 쓰이므로 부수 효과가 있는 복잡한 lvalue를 한번만 평가한다고 가정하지 않습니다. u64보다 넓은 임의 타입으로 일반화하지 않습니다.',
    ('이 macro는 to 자체의 주소를 직접 취하나요?', '아닙니다. u64 지역 __tmp의 주소를 사용합니다.', '그렇습니다. 항상 &to를 전달합니다.', '원문은 may not be address-taken 변수를 고려합니다. 임시값의 metadata를 처리한 뒤 대입합니다.'),
    ('실제 사용자 데이터 copy와 hook의 상대 시점은 항상 같나요?', '아닙니다. uaccess 구현에 따라 달라질 수 있습니다.', '그렇습니다. 모든 arch에서 무조건 after입니다.', 'kernel-doc은 get_user 계열이 fragile하며 구현에 따라 before나 after가 될 수 있다고 명시합니다.'))
row(I, 'put_user 계측·sizeof(from)과 사용하지 않는 size', 'instrument_put_user',
    'instrument_put_user(from,ptr,size)의 실제 본문은 kmsan_copy_to_user(ptr,&from,sizeof(from),0)입니다. size라는 formal 인자가 있어도 본문에서 사용하지 않습니다. 따라서 직접 호출에 넣은 size의 부수 효과 표현식도 전처리 결과에 남지 않습니다. from은 주소를 취할 수 있는 대상이어야 하고 실제 계측 길이는 sizeof(from)입니다.',
    'from이 4byte scalar이고 size 표현식이 99를 내는 경우 실제 전달 길이는 4임을 계산하세요. 주소 가능한 source와 정상 put_user 사용 문맥을 확인합니다. 이 macro도 실제 사용자 데이터 store를 대신 실행하지 않습니다.',
    ('from이 4byte 변수이고 size 인자가 99면 실제 계측 길이는 무엇인가요?', 'sizeof(from)인 4byte입니다.', '항상 size인 99byte입니다.', '매크로 본문은 formal size를 사용하지 않습니다. 선언 설명보다 실제 확장을 함께 읽어야 합니다.'),
    ('직접 size 인자에 쓴 side_effect()는 평가되나요?', '아닙니다. 본문에서 size를 사용하지 않습니다.', '그렇습니다. 일반 함수 인자처럼 반드시 평가합니다.', '전처리 매크로의 사용되지 않는 인자 토큰과 함수 호출 인자의 평가를 구별합니다.'))

def register(topic, q, detail):
    for path, title, symbol, principle, use, questions in ROWS:
        topic(title, '관찰·디버깅', path, symbol,
              '고정 Linux 소스의 접근 계측 인터페이스를 읽어 주소 유효성·동시 접근·초기화 추적의 차이와 구성·호출 순서·사용 조건을 익힙니다.',
              principle, use,
              '실제 데이터 연산, 검사 annotation, metadata 상태를 구분하여 주소·길이·방향·설정 분기·지역 수명에 직접 주석을 달아 보세요.',
              *(q(*question) for question in questions), details=[
                  detail('원문과 구현 범위', 'kcsan-checks.h 533행, kasan-checks.h 50행, kmsan-checks.h 98행, instrumented.h 216행 전체를 읽고 수업을 작성했습니다. 실제 detector 엔진의 shadow·watchpoint·origin·race 보고 알고리즘은 이 네 헤더의 구현 범위 밖이며 별도 소스 수업이 필요합니다.'),
                  detail('선택 실행의 근거', '네 원문 헤더를 명시적인 runtime recorder와 연결해 8개 구성의 최적화·ASan·UBSan 총 16빌드를 실행했습니다. 실제 cleanup 속성, 접근 플래그·인자 평가·중첩·atomic 표시·barrier 전달·부분 copy 길이를 확인했습니다. KMSAN shadow와 데이터 copy, 실제 kernel race·정보 유출·use-after-free·CPU 메모리 순서는 이 recorder 실험이 수행하지 않습니다.')])
