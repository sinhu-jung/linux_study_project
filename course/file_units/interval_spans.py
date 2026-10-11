"""Whole general interval tree API and covered/uncovered span iterator."""
ROWS = []


def add(path, title, intro, principle, use, sections, questions):
    ROWS.append(dict(path=path, title=title, intro=intro, principle=principle,
                     use=use, area='구간 합집합 · 반복자 상태 · 경계 계산',
                     sections=sections, questions=questions))


add('include/linux/interval_tree.h', '일반 구간 트리 헤더 전체: 노드 검색과 영역 분류 API',
    'unsigned long의 닫힌 구간을 저장하고 겹치는 노드 또는 덮인 영역·빈 영역을 순회하는 인터페이스입니다.',
    '노드 순회는 개별 객체를 반환하지만 span 순회는 여러 객체의 합집합을 최대 연속 영역으로 합쳐 반환합니다.',
    '상태의 is_hole을 보고 해당 union 이름으로 경계를 읽습니다. private 노드 포인터를 직접 바꾸거나 활성 순회 중 트리를 임의 수정하지 않습니다.',
    [('전체 파일', 'SPDX·guard·rbtree 포함 뒤에 interval_tree_node, 기본 API 네 선언, span 반복자 문서와 구조체, span API 세 선언, done inline, for_each_span 매크로와 endif가 있습니다. 원본 C 파일의 span 함수는 CONFIG_INTERVAL_TREE_SPAN_ITER 조건부로 빌드된다는 점도 함께 확인합니다.'),
     ('닫힌 구간 노드', '노드는 rb와 unsigned long start,last,__subtree_last를 가집니다. last는 구간에 포함되는 마지막 위치이고 집계 필드는 서브트리의 최대 last입니다. 기본 insert/remove는 cached root를 받으며 iter_first/next는 query의 start,last에 겹치는 실제 노드를 반환합니다.'),
     ('span의 의미', 'span 반복자는 노드를 반환하지 않습니다. 어떤 노드에도 덮이지 않는 hole과 노드들의 합집합에 완전히 덮이는 used를 번갈아 내보냅니다. 겹침뿐 아니라 바로 인접한 구간도 합쳐 가능한 가장 큰 연속 영역을 만듭니다. 유효한 요청 범위 전체를 used 또는 hole로 분류합니다.'),
     ('상태 표현', 'private 영역은 nodes[2], first_index,last_index입니다. public 영역의 시작값 union은 start_hole/start_used, 끝값 union은 last_hole/last_used 두 이름이 같은 저장 공간을 공유합니다. is_hole은1이면 hole,0이면 used,-1이면 완료입니다. 단순 if(is_hole)만으로 완료 상태를 hole로 오해하지 않도록 done을 먼저 확인합니다.'),
     ('반복 API', 'first는 트리와 요청 양끝으로 시작하고 next는 저장된 상태를 진행합니다. advance는 특정 새 시작 위치로 이동할 때 트리도 받습니다. done은 is_hole==-1을 검사하며 for_each_span은 first,done,next를 for 루프에 결합합니다. 이미 완료한 상태에서 public 경계값을 새 결과처럼 사용하지 않습니다.'),
     ('CS 연결', '개별 구간과 합집합 영역의 차이, tagged union과 상태 판별, 반복자 캡슐화, 완전한 범위 분할, 선택적 커널 설정과 API 가용성을 학습합니다.')],
    [('span 순회는 삽입한 노드를 하나씩 반환하는가?', '아니다. 합쳐진 used와 hole 영역을 반환한다', '그렇다. 각 노드 주소를 공개 결과로 반환한다', '노드 순회 API와 span API는 출력 단위가 다릅니다. 서로 겹치는 여러 노드가 하나의 used로 합쳐질 수 있습니다.'),
     ('is_hole==-1은 hole을 뜻하는가?', '아니다. 반복 완료 표식이다', '그렇다. 음수도 참이므로 유효한 hole이다', 'done helper는 정확히 -1을 검사합니다. 영역을 처리하기 전에 완료 여부를 확인해야 합니다.'),
     ('start_used와 start_hole은 별도 값을 동시에 저장하는가?', '아니다. 같은 union 저장 공간의 두 이름이다', '그렇다. 모든 상태에서 서로 독립이다', '활성 상태 종류에 맞는 이름으로 해석합니다. 구현의 advance도 이 저장 공간 공유를 이용합니다.')])

add('lib/interval_tree.c', '구간 트리 구현 전체: 인접 영역 병합과 빈틈 순회',
    '일반 구간 트리를 템플릿으로 생성하고 사용·미사용 영역을 순회하는 추가 상태 머신을 구현합니다.',
    '현재 연속 구간 묶음의 최대 끝점을 추적하고 다음 묶음의 시작 전까지를 hole로 반환합니다. 요청 범위 경계에서는 결과를 잘라냅니다.',
    '유효한 first_index<=last_index 범위를 사용하고 객체 수명·외부 동기화를 유지해야 합니다. 범위 전체 분류와 특정 노드 존재 검사는 다른 작업입니다.',
    [('전체 구성', 'GPL SPDX와 interval_tree/generic/compiler/export 포함 뒤에 START/LAST 접근자를 정의하고 INTERVAL_TREE_DEFINE를 한 번 확장합니다. insert/remove/iter_first/iter_next를 GPL export합니다. CONFIG_INTERVAL_TREE_SPAN_ITER 안에는 next_gap helper와 first/next/advance 및 세 export가 있습니다.'),
     ('일반 함수 생성', '템플릿에는 interval_tree_node, rb, unsigned long, __subtree_last, 두 끝점 접근자, 빈 ITSTATIC, interval_tree 접두사를 전달합니다. 따라서 일반 외부 함수 이름을 생성하며 기본 회전·집계 로직은 generic/augmented 헤더에서 옵니다. 이 파일에 생성 함수 본문이 직접 보이지 않아도 실제 함수가 없는 것은 아닙니다.'),
     ('next_gap의 두 포인터', 'nodes[1]은 아직 합칠 묶음의 첫 노드이며 NULL이 아니어야 합니다. helper는 이를 nodes[0]으로 옮기고 겹치는 다음 노드를 순회합니다. 더 큰 last가 나오면 nodes[0]을 그 노드로 바꿉니다. nodes[0]은 마지막 방문 노드가 아니라 연속 묶음의 최대 끝점을 제공하는 노드입니다. nodes[1]에는 다음 떨어진 묶음의 첫 노드 또는 NULL을 남깁니다.'),
     ('겹침과 인접의 병합', '반복 조건은 현재 최대 끝>=다음 시작 또는 현재 최대 끝+1==다음 시작입니다. 따라서 [2,4],[4,6],[7,8]은 하나의 used[2,8]이 됩니다. 노드가 포함 관계여도 가장 긴 끝점을 유지합니다. unsigned 최대값에서 +1을 무조건 계산하는 것이 아니라 첫 >= 조건이 참이면 ||의 단락 평가로 두 번째 식을 건너뜁니다.'),
     ('first의 세 출발 상태', 'first는 query 양끝을 저장하고 첫 겹침 노드를 찾습니다. 없으면 요청 전체가 hole입니다. 첫 노드 시작이 query 시작보다 뒤라면 선행 hole을 반환하고 next_gap으로 뒤의 used 묶음을 미리 준비합니다. 이미 used 안에서 시작하면 start_used를 query 시작으로 정하고 묶음 최대 끝을 사용합니다. 끝이 query 끝 이상이면 자르고 두 private 포인터를 NULL로 만들어 마지막 span임을 표시합니다.'),
     ('next의 상태 전이', '두 private 포인터가 모두 NULL이면 is_hole=-1로 완료합니다. 현재 hole이면 last_hole+1부터 미리 준비한 묶음 끝까지 used로 전환하고 요청 끝에서 자릅니다. 현재 used이고 다음 묶음이 없으면 최대 끝+1부터 요청 끝까지 후행 hole을 반환합니다. 두 묶음이 있으면 이전 끝+1부터 다음 시작-1까지 내부 hole을 만들고 next_gap으로 다음 used를 준비합니다.'),
     ('종료 표식과 마지막 결과', '마지막 영역을 반환하면서 private 포인터를 비워도 is_hole은 그 영역의 유효한 종류입니다. 다음 next에서 -1이 됩니다. 따라서 노드가 없는 트리도 즉시 완료가 아니라 전체 query의 hole 한 개를 먼저 내놓습니다. 이 순서가 요청 범위를 빠짐없이 덮게 합니다.'),
     ('advance의 빠른 경로', '이미 완료면 아무것도 하지 않습니다. first_index를 new_index로 갱신하고 query 끝보다 크면 완료합니다. new_index가 현재 span 안이면 union의 시작값만 변경해 남은 부분을 반환합니다. 현재 끝+1이면 next로 이동하고, 그 외에는 first를 새 위치에서 다시 호출합니다. 일반 이동은 다시 검색할 수 있으므로 함수 이름을 항상 상수 시간 이동이라고 해석하지 않습니다.'),
     ('작은 예제', '저장 구간이 [2,4],[4,6],[7,8]이고 query[0,10]이면 hole[0,1],used[2,8],hole[9,10]입니다. used 상태에서 advance(5)는 used[5,8]로 자릅니다. advance(9)는 바로 다음 hole로 이동합니다. 초기 함수에는 역전 범위를 정규화하는 분기가 없으므로 잘못된 양끝을 전달하면 안 됩니다.'),
     ('CS 연결과 검증 범위', '정렬된 구간의 합집합, 두 포인터 상태, inclusive 경계의 ±1 계산, 단락 평가와 정수 wrap, 반복 종료와 마지막 결과의 분리를 학습합니다. 트리 탐색은 템플릿 구현에 의존하며 여기의 전체 소스 대조는 실제 동시 실행이나 모든 unsigned 경계값의 실행 검증과 다릅니다.')],
    [('nodes[0]은 항상 마지막 방문 노드를 가리키는가?', '아니다. 현재 묶음의 가장 큰 끝값을 가진 노드를 추적한다', '그렇다. 매 반복 무조건 현재 노드로 바꾼다', '갱신 조건은 cur->last>nodes[0]->last입니다. 안쪽에 포함된 짧은 구간을 방문하면 기존 노드를 유지합니다.'),
     ('[2,4]와 [5,7] 사이에 hole이 나오는가?', '아니다. 인접 구간이므로 used[2,7]로 합친다', '그렇다. 겹치지 않으면 반드시 hole이 있다', '닫힌 정수 구간에서4 다음 위치는5입니다. next_gap은 last+1==start도 연속으로 처리합니다.'),
     ('아무 노드가 없는 트리의 유효한 query를 순회하면?', '전체 query의 hole을 한 번 반환한 뒤 완료한다', '처음부터 결과 없이 완료한다', 'first는 is_hole1과 query 경계를 저장합니다. 다음 next에서 private 포인터가 없음을 보고 -1로 끝납니다.'),
     ('advance가 현재 span 내부의 위치로 이동하면?', '시작값만 새 위치로 잘라 기존 종류와 끝을 유지한다', '항상 트리 전체를 처음부터 순회한다', '현재 시작<=new_index<=끝이면 start_hole 저장 공간만 갱신합니다. union이어서 used 상태에도 같은 코드가 적용됩니다.')])
