"""Whole-file overlay phandle relocation and external symbol resolution."""
ROWS = [dict(
    path='drivers/of/resolver.c', title='OF resolver: 로컬 ID 재배치와 외부 symbol fixup',
    intro='live tree 최대 ID 탐색,overlay 재배치,내부 offset 수정과 외부 label 연결 전체를 분석합니다.',
    principle='이름으로 지정된 외부 참조와 overlay 내부 숫자 참조는 서로 다른 재배치 정보를 사용합니다.',
    use='트리 재귀,심볼 테이블,바이트 offset 파싱,엔디언과 부분 갱신을 학습합니다.',
    area='장치 트리 · 링커 유사 재배치 · 문자열 파싱 · 참조 수명 · 동시성',
    sections=[
        ('구성과 최대 phandle', 'GPL-2.0 파일은 OF: resolver: 로그 접두부와 cleanup,kernel,module,OF,OF device,string,ctype,errno,slab 및 내부 헤더를 사용합니다. live_tree_max_phandle은 devtree_lock을 raw irqsave로 잡고 전체 노드의 최대 phandle을 찾되 OF_PHANDLE_ILLEGAL은 제외합니다. 초기 최대값은 0이고 탐색 후 잠금을 풉니다. 이 잠금만으로 이후 적용까지의 전체 과정을 직렬화하지는 않습니다.'),
        ('노드 ID 재배치', 'adjust_overlay_phandles는 현재 노드의 phandle이 0도 illegal도 아니면 delta를 더합니다. phandle 또는 linux,phandle 속성 중 길이가 4 이상이고 첫 값이 illegal이 아닌 속성에는 조정된 노드 필드를 big endian으로 기록합니다. 모든 속성의 모든 cell에 delta를 더하는 것이 아닙니다. 이후 자식마다 재귀 호출합니다.'),
        ('외부 fixup 문자열 복사', 'update_usages는 fixup 속성을 kmemdup하고 __free(kfree) 지역 변수로 관리하므로 정상·오류 반환에서 복제 버퍼가 해제됩니다. 값은 NUL로 구분된 path:property:offset 목록으로 처리합니다. 각 항목 길이를 strlen으로 얻고 두 colon을 NUL로 바꿔 경로·속성·offset을 나눕니다. 길이 끝 안에 NUL이 있는지 strnlen으로 확인하거나 복제 시 종료 문자를 덧붙이는 코드는 없습니다.'),
        ('외부 참조 위치의 검증', 'colon이 없으면 -EINVAL,10진 kstrtoint 오류는 해당 오류를 반환합니다. overlay의 참조를 얻어 내부 full-path 검색에 넘기고 노드가 없으면 오류 대신 다음 tuple로 continue합니다. 노드는 찾았지만 속성이 없으면 -ENOENT입니다. 찾은 노드 참조는 속성 검색 후 put하며 detached tree의 수명 보호 전제를 사용합니다. offset<0 또는 4바이트 쓰기가 속성 길이를 넘으면 -EINVAL이고 통과하면 대상 phandle을 big endian으로 기록합니다.'),
        ('Full name 비교', 'node_name_cmp는 두 노드 full_name의 kbasename을 of_node_cmp로 비교합니다. 주석은 일반 name이 @ 부분을 제거할 수 있기 때문이라고 설명합니다. node@unit-address의 suffix를 포함한 이름을 사용하여 두 하위 트리를 대응시킵니다.'),
        ('Local fixup 속성', 'local_fixups가 NULL이면 성공입니다. name,phandle,linux,phandle 자동 속성은 건너뛰고 나머지는 길이가 양수이면서 4의 배수인지 확인합니다. 대응 overlay 속성을 같은 이름으로 찾아 없으면 -EINVAL입니다. 각 big-endian u32 offset 위치의 값에 be32_add_cpu로 delta를 더합니다. off+4 경계 검사는 있지만 unsigned 덧셈 overflow나 offset 정렬을 별도로 검사하는 helper는 없습니다.'),
        ('두 트리의 병렬 재귀', 'local fixup 자식은 scoped iterator로 순회하고 각 자식마다 overlay 자식 목록에서 같은 basename을 선형 검색합니다. 매칭 자식의 순회 참조를 put한 뒤 detached overlay 안의 노드 주소로 재귀합니다. 대응 자식이 없거나 재귀가 실패하면 오류를 반환합니다. 동일 폭의 자식 목록을 매번 검색하므로 이 대응 단계는 단순한 단일 hash lookup이 아닙니다.'),
        ('공개 함수의 전제와 실제 delta', 'of_resolve_phandles는 overlay=NULL이나 OF_DETACHED가 없으면 -EINVAL입니다. delta=live_tree_max_phandle()+1을 계산해 각 기존 ID에 더합니다. 따라서 live 최대가 100이고 overlay ID가 1이면 실제 결과는 102입니다. 문서의 시작 범위 표현만으로 101이라고 계산하면 안 됩니다. 별도 overflow 검사나 유효 ID 재검증은 이 지점에 없습니다.'),
        ('Local 먼저,external 나중', '재배치 후 __local_fixups__ 자식을 첫 매칭에서 선택해 내부 참조를 조정합니다. 실패하면 out으로 갑니다. 이어 모든 자식을 순회해 __fixups__를 찾고 없으면 성공합니다. 이 함수 끝에는 local_fixups에 대한 별도 put이 보이지 않으므로 모든 탐색 참조가 같은 방식으로 정리된다고 일반화하지 않습니다. 외부 fixup이 없으면 live symbols 테이블도 필요하지 않습니다.'),
        ('Live symbol 해석', '__fixups__가 있으면 /__symbols__를 찾아 없을 때 -EINVAL입니다. fixup 속성 중 name만 건너뛰고 각 속성명을 live symbol 속성명으로 사용하여 경로 문자열을 읽습니다. 읽기 오류를 로그와 함께 전파하고 경로 노드가 없으면 -ENOENT입니다. 노드의 phandle을 저장하고 put한 뒤 해당 fixup 목록의 사용 위치들을 수정합니다.'),
        ('부분 변경과 정리', '오류이면 out에서 최종 오류 로그를 출력하고 tree_symbols 참조를 put한 뒤 err를 반환합니다. 앞서 변경한 노드 ID나 속성 값을 원래대로 복원하는 코드는 없습니다. 따라서 실패 결과의 overlay를 수정 전과 같은 객체로 보아서는 안 됩니다. 일부 external tuple의 노드 부재는 continue라는 점도 최종 0의 의미를 제한합니다.'),
        ('동시성 문서와 범위', '함수 문서는 여러 overlay의 ID 범위 충돌을 막으려면 resolve와 apply를 단일 실행 흐름으로 보호해야 한다고 설명합니다. 이 함수 자체에는 그 전체 구간을 감싸는 mutex가 없으므로 live 최대 탐색 lock만으로 충분하다고 할 수 없습니다. 호출부의 직렬화 여부는 별도 확인 대상입니다.'),
        ('전체 검토와 한계', '최대 ID,노드 재배치,external tuple 수정,이름 비교,local 재귀,공개 resolver와 GPL export 전체를 대조했습니다. 길이·offset 검사가 모든 malformed 입력을 방어한다고 주장하지 않습니다. 실제 overlay 적용·경쟁·실패 주입이나 phandle overflow 실험은 수행하지 않았습니다.')
    ], questions=[
        ('Live 최대 ID=100,overlay ID=1이면 이 코드의 재배치 결과는?', '102', '101', 'delta는 최대값+1인 101이며 원래 ID 1에 이를 더합니다. 주석의 범위 설명과 실제 식을 구분합니다.'),
        ('외부 fixup의 참조 노드가 overlay에서 안 보이면?', '해당 tuple을 건너뛰고 다음으로 진행한다', '언제나 즉시 -ENOENT를 반환한다', 'refnode가 NULL이면 continue입니다. 노드는 있지만 속성이 없는 경우의 -ENOENT와 다릅니다.'),
        ('복제한 fixup 문자열 버퍼는 오류 반환 때도 정리되는가?', '__free(kfree) 지역 변수 정리에 의해 해제된다', '아니다. 모든 오류 경로에서 영구 누수된다', '선언에 scope cleanup annotation이 있습니다. 다른 노드 참조 정리와 별개인 버퍼 수명입니다.'),
        ('Local fixup 속성의 u32 값들은 무엇인가?', '대응 속성 내부에서 phandle이 있는 바이트 offset 목록', '항상 새 phandle 번호 자체의 목록', 'off를 읽어 prop->value+off의 기존 값에 delta를 더합니다. 위치 정보와 수정할 값은 다릅니다.'),
        ('두 트리 노드 이름 비교에 full_name의 basename을 쓰는 이유는?', '@ 뒤의 unit-address를 포함한 이름을 비교하려고', '전체 경로를 무조건 파일로 열려고', '주석은 일반 name이 @ 부분을 제거하는 점을 지적합니다. 파일 I/O와는 관련 없습니다.'),
        ('중간 fixup 오류가 나면 이전 재배치를 자동 rollback하는가?', '아니다. 이 파일에는 원래 값 복원 경로가 없다', '그렇다. err 반환이 모든 메모리 쓰기를 자동 취소한다', '오류 반환과 transaction rollback은 다릅니다. 이미 수정한 객체 상태를 고려해야 합니다.'),
        ('외부 __fixups__가 없으면 live /__symbols__도 반드시 필요한가?', '아니다. symbols 조회 전에 성공 반환 경로로 간다', '그렇다. 어떤 overlay도 symbols 없이는 실패한다', '로컬 재배치와 외부 label 해결은 다른 단계입니다. 후자는 실제 외부 fixup이 있을 때 진행됩니다.'),
        ('최대 ID 탐색의 spinlock이 resolve부터 apply까지 보호하는가?', '아니다. 최대값 순회 후 바로 해제한다', '그렇다. 전체 overlay 적용이 끝날 때까지 유지한다', '보호 범위를 실제 lock/unlock 위치로 확인해야 합니다. 전체 직렬화는 호출부 계약과 관련됩니다.')
    ]
)]
