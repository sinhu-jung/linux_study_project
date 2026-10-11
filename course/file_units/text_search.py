"""Text search infrastructure and KMP, each reviewed as a whole file."""
ROWS = []


def add(path, title, intro, principle, use, sections, questions):
    ROWS.append(dict(path=path, title=title, intro=intro, principle=principle,
                     use=use, area='문자열 검색 · KMP · 함수 포인터 · 모듈 수명',
                     sections=sections, questions=questions))


add('lib/ts_kmp.c', 'KMP 전체 구현: 접두사 표와 블록 경계를 넘는 검색',
    '이미 맞춘 접두사 정보를 재사용해 입력을 뒤로 되돌리지 않는 문자열 검색 알고리즘입니다.',
    'prefix_tbl은 각 패턴 접두사의 가장 긴 진접두사이면서 접미사인 길이를 저장합니다. 불일치하면 그 길이로 상태를 줄이고 현재 문자를 다시 비교합니다.',
    '공통 prepare 경로가 길이 0을 거부한다는 전제와 할당 메모리가 0으로 초기화된다는 전제를 함께 읽어야 합니다. 이 파일의 init만 따로 호출하는 계약으로 오해하지 않습니다.',
    [('전체 파일 구조', 'GPL SPDX, 작성자와 KMP·전이 함수 설명, module/types/string/ctype/textsearch 포함 뒤에 사설 구조체와 검색·접두사 전처리·초기화·조회 함수가 있습니다. kmp_ops가 이 함수들을 연결하고 init/exit에서 공통 등록 API를 호출합니다. 모듈 설명과 GPL 라이선스도 포함됩니다.'),
     ('사설 데이터의 메모리 배치', 'ts_kmp은 패턴 포인터, 패턴 길이, flexible array인 unsigned int prefix_tbl[]을 가집니다. 할당 크기는 구조체+표+패턴 데이터이며 패턴은 표 바로 뒤에 둡니다. 한 번의 공통 할당으로 관리하므로 별도 destroy 콜백이 없습니다. prefix_tbl_len이 unsigned int 곱셈이라는 점 때문에 임의의 거대한 길이까지 산술 안전성이 보장된다고 해석하면 안 됩니다.'),
     ('접두사 표 계산', 'compute_prefix_tbl은 q=1부터 진행합니다. pattern[k]와 pattern[q]가 다르면 k=prefix_tbl[k-1]로 더 짧은 후보를 찾고 같으면 k를 늘립니다. prefix_tbl[q]=k입니다. 예를 들어 ababaca의 표는 0,0,1,2,3,0,1입니다. q0을 직접 쓰지 않으며 alloc_ts_config의 kzalloc 초기화로 첫 원소 0이 제공됩니다.'),
     ('대소문자 무시의 일관성', 'TS_IGNORECASE면 표를 만들 때 양쪽 문자를 toupper로 비교하고 저장 패턴도 대문자로 바꿉니다. 검색할 때는 입력 문자만 변환해 저장 패턴과 비교합니다. 따라서 접두사 표와 실제 비교가 같은 동등성 규칙을 사용합니다. 이 처리는 커널의 바이트 문자 분류이며 유니코드 정규화나 locale 전체 규칙은 아닙니다.'),
     ('검색 상태 q', 'q는 현재까지 일치한 패턴 앞부분의 길이입니다. 불일치 시 prefix_tbl[q-1]로 줄이고 같은 현재 입력 문자를 재평가합니다. 일치하면 q를 하나 늘려 패턴 길이에 도달했는지 검사합니다. 한 입력 문자에서 여러 감소가 있어도 전체 감소는 앞선 증가로 상쇄되므로 전처리 O(m), 검색 O(n), 표 공간 O(m)입니다.'),
     ('블록 경계를 넘는 이유', 'q는 바깥 블록 반복 전에 한 번만 0으로 초기화합니다. 블록을 다 읽은 뒤 consumed만 text_len만큼 늘리고 다음 블록에서도 q를 유지합니다. 패턴 abc가 첫 블록의 ab와 다음 블록의 c에 걸쳐 있어도 찾을 수 있습니다. get_next_block이 0을 반환하면 종료하고 UINT_MAX를 반환합니다.'),
     ('성공 위치와 다음 검색', '성공 시 state->offset=consumed+i+1로 일치 끝 다음 위치를 저장하고 시작 위치는 offset-pattern_len으로 반환합니다. 다음 kmp_find 호출은 q0과 이 offset에서 시작하므로 겹치는 일치를 자동으로 모두 열거하지 않습니다. ababa에서 aba를 찾은 뒤 next를 호출하면 offset3에서 시작하므로 위치2의 겹친 aba는 건너뜁니다. 실패 경로는 state->offset을 별도 갱신하지 않습니다.'),
     ('초기화와 오류', 'kmp_init은 필요한 크기로 alloc_ts_config를 호출하고 IS_ERR면 그대로 반환합니다. 성공하면 flags, 길이, 표, 패턴 포인터와 복사 데이터를 설정합니다. 패턴은 길이로 다루며 NUL 종료 문자열만 지원하는 것은 아닙니다. get_pattern은 저장된 패턴 주소를, get_pattern_len은 길이를 돌려줍니다.'),
     ('등록과 수명', 'kmp_ops의 이름은 kmp이며 owner는 THIS_MODULE, list는 LIST_HEAD_INIT으로 초기화합니다. init_kmp은 textsearch_register 결과를 반환하고 exit_kmp은 unregister합니다. 설정 메모리의 할당·해제와 알고리즘 모듈 참조는 공통 textsearch 코드와 결합해 관리됩니다.'),
     ('CS 연결', '실패 함수, 상태 전이의 지연 계산, 분할 입력 처리, flexible array 배치, 콜백 기반 알고리즘 교체, 초기화 전제를 학습합니다. 원본 대조는 실제 커널의 동시성·할당 실패 전체를 실행 검증한 것과 다릅니다.')],
    [('ababaca의 접두사 표는?', '0,0,1,2,3,0,1이다', '0,1,2,3,4,5,6이다', 'ababa의 가장 긴 진접두사이자 접미사는 aba여서 3입니다. c를 붙이면 적절한 후보가 없어 0, 마지막 a에서는 1입니다.'),
     ('입력 블록이 바뀔 때 q를 0으로 초기화하는가?', '아니다. 유지하여 경계를 넘는 패턴을 찾는다', '그렇다. 각 블록은 독립 검색이다', 'q 초기화는 바깥 무한 반복 전에 있습니다. 새 블록을 받더라도 앞 블록에서 맞춘 접두사 상태를 유지합니다.'),
     ('ababa에서 aba를 찾고 바로 next를 호출하면 위치2도 찾는가?', '아니다. 첫 일치 끝 다음인 위치3에서 재시작한다', '그렇다. 모든 겹치는 일치를 자동 열거한다', '성공 시 offset을 일치 끝 다음으로 저장하고 새 호출에서 q0으로 시작합니다. 겹치는 일치의 열거와는 다른 계약입니다.'),
     ('prefix_tbl[0]을 명시적으로 쓰지 않아도 0인 근거는?', '공통 할당 함수가 kzalloc으로 메모리를 0 초기화한다', 'flexible array는 C 언어에서 자동으로 0이 된다', '동적 배열의 문법 자체가 초기화를 보장하지 않습니다. include/linux/textsearch.h의 alloc_ts_config 구현과 함께 확인해야 합니다.')])

add('include/linux/textsearch.h', 'Textsearch 헤더 전체: 전략 콜백·검색 상태·사설 할당',
    '검색 알고리즘과 데이터 공급자를 분리하는 공통 자료구조와 inline API입니다.',
    'ts_config는 재사용할 설정과 콜백을, ts_state는 개별 검색의 offset과 제어 버퍼를 보관합니다. 알고리즘 구현은 ts_ops를 통해 교체됩니다.',
    '공유 설정과 검색별 상태를 구분하고, 콜백이 보관하는 데이터의 수명과 동시 사용 조건을 보장해야 합니다.',
    [('전체 선언', 'SPDX와 guard 뒤에 types/list/kernel/err/slab 의존성이 있습니다. module과 config 전방 선언, TS_AUTOLOAD=1과 TS_IGNORECASE=2, state/ops/config 구조체, 검색·조회 inline 네 개, 공통 외부 API 다섯 개, 사설 메모리 정렬·할당·조회 함수로 끝납니다.'),
     ('검색별 상태', 'ts_state는 unsigned int offset과 char cb[48]을 가집니다. offset은 다음 검색 시작점이고 cb는 get_next_block이 지속 정보를 저장하는 공간입니다. find는 offset만 0으로 만들며 cb 전체를 지우지 않습니다. 데이터 공급자가 필요한 필드를 초기화해야 합니다.'),
     ('전략과 수명 정보', 'ts_ops는 이름, init/find/destroy/get_pattern/get_pattern_len 함수 포인터, owner 모듈과 연결 리스트 노드를 가집니다. 공통 계층은 같은 인터페이스로 알고리즘을 다룹니다. destroy는 선택적 콜백이며 알고리즘별 추가 자원이 없을 수 있습니다.'),
     ('데이터 공급 콜백', 'config는 ops와 flags 외에 get_next_block과 finish를 가집니다. 공급자는 consumed에 해당하는 다음 데이터 주소를 *dst에 넣고 길이를 반환하며 0으로 끝을 알립니다. consumed0은 새 검색을 뜻하고 cb를 활용할 수 있습니다. 입력이 여러 블록으로 나뉘어도 알고리즘이 필요한 상태를 유지할 수 있습니다.'),
     ('inline 호출 순서', 'textsearch_next는 ops->find를 호출한 뒤 finish가 있으면 결과가 성공이든 실패든 호출하고 저장한 검색 결과를 반환합니다. find는 offset0으로 설정한 뒤 next로 넘깁니다. get_pattern과 get_pattern_len은 해당 ops 콜백을 그대로 호출합니다. UINT_MAX는 미발견 표식입니다.'),
     ('8바이트 경계와 0 초기화', 'TS_PRIV_ALIGN은 길이를 8의 배수로 올립니다. alloc_ts_config는 정렬된 config 크기+payload를 kzalloc하고 실패하면 ERR_PTR(-ENOMEM)을 반환합니다. ts_config_priv는 config 주소를 바이트 포인터로 바꿔 동일한 정렬 크기만큼 더합니다. 이 함수가 모든 정렬 요구나 payload 산술 오버플로를 검사하는 것은 아닙니다.'),
     ('CS 연결', '전략 패턴, 함수 포인터, 제어 상태와 공유 설정 분리, 외부 입력 공급, 오류 포인터와 소유권을 연결합니다. finish는 검색 호출 후 정리이며 config 자체의 destroy와 역할이 다릅니다.')],
    [('textsearch_find가 cb[48]도 0으로 지우는가?', '아니다. offset만 0으로 설정한다', '그렇다. ts_state 전체를 초기화한다', 'inline 구현은 state->offset=0 한 줄 뒤에 next를 호출합니다. cb 초기화는 데이터 공급 방식이 책임집니다.'),
     ('미발견이어도 finish 콜백을 호출하는가?', '그렇다. 콜백이 있으면 find 결과와 관계없이 호출한다', '아니다. 성공한 경우만 호출한다', 'textsearch_next는 find 반환값을 저장하고 finish 존재 여부만 검사합니다. 검색 결과의 값으로 분기하지 않습니다.'),
     ('alloc_ts_config 실패는 NULL로만 표현되는가?', '아니다. ERR_PTR(-ENOMEM)을 반환한다', '그렇다. kzalloc 결과를 그대로 반환한다', 'kzalloc의 NULL을 오류 포인터로 바꾸는 분기가 있습니다. 호출자는 IS_ERR 계약을 따라야 합니다.')])

add('lib/textsearch.c', 'Textsearch 공통 계층 전체: 등록 목록·RCU·설정 수명',
    '알고리즘 등록과 선택, 모듈 참조, 연속 데이터 공급을 담당하는 공통 구현입니다.',
    '수정은 스핀락으로 직렬화하고 조회는 RCU 목록에서 수행합니다. 선택한 알고리즘의 모듈 참조를 확보해 설정이 살아 있는 동안 유지합니다.',
    '설정은 prepare 후 사용하고 destroy로 해제합니다. 각 검색에는 별도 상태가 필요하며 설정 콜백을 동시에 바꾸는 사용까지 자동 안전해지는 것은 아닙니다.',
    [('전체 파일과 문서', 'SPDX와 작성자 뒤에 소개·아키텍처 ASCII 그림·사용법·chicken 검색 예제가 있습니다. 의존 헤더 뒤에 전역 ops 리스트와 스핀락, 조회·등록·해제, 연속 입력 상태와 콜백, 연속 검색·prepare·destroy 구현 및 export가 있습니다. 문서의 finish 단계는 실제 헤더의 next wrapper까지 함께 보면 호출 주체가 명확해집니다.'),
     ('이름 조회와 모듈 참조', 'lookup_ts_algo는 rcu_read_lock 안에서 이름을 strcmp로 비교합니다. 일치한 항목은 try_module_get(owner)이 성공해야 반환하며 실패하면 NULL입니다. RCU 읽기 보호는 목록 접근 동안, 모듈 참조는 이후 사용 동안의 수명과 관련됩니다. 이름만 찾았다고 모듈 수명이 확보되는 것은 아닙니다.'),
     ('등록 검증과 중복', 'textsearch_register는 name과 find/init/get_pattern/get_pattern_len 누락을 -EINVAL로 거부합니다. destroy는 필수 조건에 없습니다. 락 안에서 같은 이름을 찾으면 -EEXIST, 없으면 list_add_tail_rcu로 추가합니다. ops 포인터 자체는 유효해야 하며 NULL 포인터를 자동 방어하는 함수가 아닙니다.'),
     ('등록 해제의 범위', 'unregister는 락 아래에서 이름이 아니라 ops 포인터 동일성을 찾아 list_del_rcu하고 성공합니다. 없으면 -ENOENT입니다. 이 함수 자체에는 synchronize_rcu나 메모리 해제가 없습니다. 따라서 반환 즉시 임의의 ops 메모리를 재사용해도 된다는 근거로 삼지 말고 모듈·RCU 수명 규칙까지 확인해야 합니다.'),
     ('연속 데이터 어댑터', 'ts_linear_state는 len과 data를 가지며 state->cb 안에 놓입니다. get_linear_data는 consumed<len이면 data+consumed와 남은 길이를 반환하고 아니면 0입니다. find_continuous는 config의 get_next_block을 이 함수로 설정하고 cb의 두 필드를 쓴 뒤 textsearch_find를 호출합니다. len은 바이트 길이이므로 데이터 중간의 NUL도 입력에 포함될 수 있습니다.'),
     ('공유 설정의 전제', '소개는 별도 ts_state를 주면 설정을 반복·병렬 사용한다고 설명합니다. 그러나 find_continuous는 conf->get_next_block을 쓰므로 서로 다른 공급 방식으로 설정을 동시에 재구성하는 경우까지 그 설명을 확장하면 안 됩니다. 콜백과 데이터 수명이 안정된 사용 조건을 구분해야 합니다.'),
     ('prepare와 자동 로딩', 'len0은 ERR_PTR(-EINVAL)로 먼저 거부합니다. 이름 조회 후 CONFIG_MODULES이고 TS_AUTOLOAD 플래그가 켜져 있을 때만 request_module("ts_%s",algo)를 요청하고 다시 조회합니다. 찾지 못하면 -ENOENT입니다. 주석은 NFS 등에 있는 모듈 요청이 교착을 일으킬 수 있는 문맥 때문에 항상 자동 로딩하지 않는다고 설명합니다.'),
     ('초기화 실패와 성공의 소유권', '조회 성공 후 ops->init을 호출합니다. 오류 포인터면 해당 오류 번호를 보관하고 확보한 모듈 참조를 module_put으로 반환합니다. 성공하면 conf->ops를 채우고 설정을 반환하며 모듈 참조를 유지합니다. 검색 알고리즘마다 패턴 형식이 다를 수 있다는 문서 경고도 있습니다.'),
     ('destroy의 순서', 'conf->ops가 있으면 선택적 알고리즘 destroy를 먼저 부르고 module_put을 수행합니다. 마지막에 공통 설정 메모리를 kfree합니다. 알고리즘의 추가 자원 정리와 공통 메모리 정리는 별도 단계입니다. 오류 포인터를 이 함수에 넘겨도 된다는 계약은 없습니다.'),
     ('CS 연결', '플러그인 레지스트리, 읽기와 쓰기의 동기화 차이, 모듈 참조 계수, 어댑터 콜백, 두 단계 정리와 오류 전파를 학습합니다. 문서·헤더·알고리즘의 경계를 함께 대조했으며 실제 RCU 경쟁과 모듈 로딩의 실행 검증은 별도입니다.')],
    [('등록 시 같은 이름의 다른 ops가 있으면?', '-EEXIST를 반환한다', '기존 항목을 자동 교체한다', '락 안에서 이름을 비교해 errout으로 이동합니다. 기존 항목을 삭제하거나 교체하지 않습니다.'),
     ('unregister는 무엇으로 항목을 찾는가?', '등록했던 ops 포인터의 동일성으로 찾는다', 'name 문자열만 같으면 어느 구조체든 제거한다', '삭제 루프의 조건은 o==ops입니다. 등록의 이름 중복 검사와 삭제의 식별 기준은 다릅니다.'),
     ('알고리즘 init이 실패하면 이미 잡은 모듈 참조는?', '오류 경로에서 module_put으로 반환한다', '성공 여부와 관계없이 영구 유지한다', 'errout은 ops가 있으면 module_put을 호출합니다. 성공한 설정만 참조를 유지하다 destroy에서 돌려줍니다.'),
     ('자동 모듈 로딩은 항상 수행되는가?', '아니다. 모듈 설정과 TS_AUTOLOAD 조건이 필요하다', '그렇다. 알고리즘 이름을 못 찾으면 무조건 요청한다', 'CONFIG_MODULES 조건 안에서 ops==NULL과 TS_AUTOLOAD를 확인합니다. 호출 문맥에 따른 교착 위험을 피하려는 정책입니다.')])
