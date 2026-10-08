"""Reference and dirty policies in reclaim, pinned Linux v6.12."""
ROWS = [('회수 전 참조 수 검사: 큰 folio에서 기대값이 달라지는 이유',
  '메모리',
  'mm/vmscan.c',
  'is_page_cache_freeable',
  '페이지 캐시의 데이터를 읽거나 다른 곳에서 붙잡고 있는 참조까지 남아 있다면 회수하려는 쪽이 혼자라고 생각하면 안 됩니다. 반대로 큰 folio는 여러 기본 페이지를 포함하므로 참조 수가 2보다 '
  '크다는 이유만으로 외부 사용자를 단정할 수도 없습니다.',
  'is_page_cache_freeable은 folio_ref_count에서 private 표시가 있으면 1을 빼고, 그 값이 1+folio_nr_pages와 같은지 비교합니다. 주석의 기대 소유자는 '
  'folio를 격리한 호출자, 페이지 캐시, 선택적인 파일시스템 private 데이터입니다. pageout은 이 검사가 거짓이면 PAGE_KEEP을 반환합니다. helper 자체는 참조를 감소시키거나 '
  '실제 메모리를 해제하지 않습니다.',
  '기본 페이지 1개, private 없음이면 기대 참조 수는 2입니다. 기본 페이지 4개를 포함하고 private가 있으면 refcount=6에서 6-1=1+4라 통과합니다. 같은 조건에서 '
  'refcount=7이면 7-1=6으로 기대값 5와 달라 통과하지 못합니다.',
  '왜 통과만으로 즉시 free할 수 없나',
  '이 비교는 회수 경로가 기대하는 소유 관계의 한 조건입니다. dirty 여부, mapping, writeback, 잠금과 다른 회수 조건을 모두 대체하지 않습니다. 단순 helper 호출이 이후 '
  '참조 증가를 영원히 막는 것도 아닙니다. 정확한 호출 문맥에서 사용하는 검사이며 사용자가 임의 folio의 숫자만 보고 kfree할 근거가 아닙니다.',
  ('4페이지 folio, private 있음, 참조 수 6이면 이 식은?',
   '6-1=1+4로 참입니다.',
   '참조 수가 2를 넘으므로 무조건 거짓입니다.',
   '기대 캐시 참조 수는 folio_nr_pages를 반영하고 private는 별도로 1을 뺍니다.'),
  ('검사 반환값이 참이면 helper가 이미 메모리를 해제했나요?',
   '아닙니다. 참조 수의 조건만 비교했습니다.',
   '그렇습니다. true는 free 완료입니다.',
   '본문은 return 비교식뿐이며 참조 감소나 해제 호출이 없습니다.')),
 ('회수의 두 번째 기회: 접근 흔적을 지우고 다시 기록하는 이유',
  '메모리',
  'mm/vmscan.c',
  'folio_check_references',
  '페이지를 처음 메모리에 올리는 fault도 페이지 테이블에 접근 흔적을 남깁니다. 이 흔적 하나를 무조건 뜨거운 데이터로 판단하면 한 번만 사용한 데이터도 오래 남습니다. 다시 접근했는지 구분하는 '
  '두 번째 관찰이 필요합니다.',
  'folio_check_references는 folio_referenced로 페이지 테이블 접근과 vm_flags를 얻고 folio_test_clear_referenced로 기존 folio 표시를 '
  '읽으며 지웁니다. VM_LOCKED는 ACTIVATE, referenced_ptes=-1은 KEEP입니다. 양수 접근이면 표시를 다시 세우고 이전 표시가 있거나 접근 수가 1보다 크면 '
  'ACTIVATE합니다. 실행 가능한 file LRU folio도 첫 접근에서 ACTIVATE합니다. 그 외 첫 접근은 KEEP입니다. 접근이 없지만 이전 표시가 있는 file LRU면 '
  'RECLAIM_CLEAN, 나머지는 RECLAIM입니다.',
  '일반 파일 folio에 이전 표시가 없고 이번 접근 수가 1이면 표시를 세우고 KEEP입니다. 다음 회전에도 접근 수 1이 관찰되면 이전 표시가 있으므로 ACTIVATE입니다. 다음에 접근이 0이면 '
  '이전 표시를 읽어 지운 뒤 RECLAIM_CLEAN으로 내려갈 수 있습니다. -1은 음수 횟수를 세라는 뜻이 아니라 잠금 경쟁 등 원문의 특별 결과입니다.',
  '왜 RECLAIM_CLEAN과 RECLAIM이 다른가',
  '호출자는 둘 다 회수를 시도하는 경로로 진행하지만 dirty 분기에서 RECLAIM_CLEAN이면 keep_locked로 갑니다. 최근 사용 흔적이 있는 파일 folio를 회수하려고 추가 쓰기까지 '
  '강요하지 않는 선택입니다. ACTIVATE 반환도 모든 경우에 같은 활성 목록 이동을 보장한다고 확대하면 안 됩니다. VM_LOCKED 경우 원문은 unevictable 처리로 이어질 대상을 '
  '설명합니다. 이 수업은 이 helper와 직접 호출 분기의 정책입니다.',
  ('일반 파일 folio가 이전 표시 없이 접근 수 1이면?',
   '표시를 세우고 KEEP입니다.',
   '첫 접근이면 모두 즉시 ACTIVATE입니다.',
   '이전 표시, 접근 수 2 이상, 실행 파일 조건이 없으면 한 번 더 관찰합니다.'),
  ('referenced_ptes=-1이면 접근하지 않았으므로 회수하나요?',
   '아닙니다. KEEP을 반환합니다.',
   '그렇습니다. 음수는 0보다 작은 사용량입니다.',
   '코드가 -1을 별도 조건으로 검사하며 잠금 경쟁 등에서 보존하도록 처리합니다.')),
 ('회수의 dirty 판정: 출력 false가 데이터 삭제는 아니다',
  '메모리',
  'mm/vmscan.c',
  'folio_check_dirty_writeback',
  '모든 메모리가 같은 저장 경로를 쓰지는 않습니다. 파일 flusher가 처리하는 데이터와 회수 문맥에서 별도로 처리하는 익명 메모리를 같은 혼잡 기준으로 계산하면 회수를 잘못 지연할 수 있습니다.',
  'folio_check_dirty_writeback은 file LRU가 아니거나 anon이면서 swapbacked가 아닌 folio이면 출력 dirty와 writeback을 false로 쓰고 '
  '반환합니다. 주석은 익명 folio가 flusher 대상이 아니고 MADV_FREE 익명 folio가 inactive file 목록에도 들어갈 수 있음을 설명합니다. 나머지는 folio 플래그에서 '
  '값을 읽습니다. private가 없으면 끝내고, 있으면 mapping과 is_dirty_writeback callback이 있을 때 파일시스템에 출력값 재확인을 맡깁니다.',
  'private가 없는 file LRU folio의 dirty 플래그가 1, writeback이 0이면 기본 출력은 true/false입니다. private와 callback이 있으면 '
  'callback이 이 값을 보정할 수 있습니다. 익명 예외 분기에서 출력이 false/false여도 이 함수는 folio_clear_dirty를 호출하지 않습니다.',
  '왜 false를 저장장치에 기록 완료됐다는 뜻으로 읽으면 안 되나',
  '여기서 false는 해당 회수 정책에서 파일 flusher의 dirty/writeback 지연 대상으로 세지 않도록 하는 출력일 수 있습니다. 메모리 내용의 삭제, 디스크 기록 성공, folio '
  '상태 비트 해제를 뜻하지 않습니다. bool 포인터로 전달한 결과 변수와 folio 내부 상태가 서로 다른 저장 위치라는 C 기초까지 구분하면 오해를 줄일 수 있습니다.',
  ('익명 예외에서 *dirty=false이면 folio의 dirty 비트도 지웠나요?',
   '아닙니다. 출력 변수에 false를 쓴 것입니다.',
   '그렇습니다. 같은 이름이면 같은 메모리입니다.',
   '본문의 대입 대상은 bool 출력 포인터이며 folio 플래그를 지우는 helper가 없습니다.'),
  ('파일시스템 callback은 모든 folio에서 호출하나요?',
   '아닙니다. 앞선 예외를 통과하고 private·mapping·callback 조건이 필요합니다.',
   '그렇습니다. 모든 메모리는 파일시스템에 속합니다.',
   '조기 반환과 조건문을 차례로 통과해야 is_dirty_writeback 호출에 도달합니다.'))]

def register(topic,q,detail):
    for title,area,path,symbol,why,principle,use,dt,body,qa,qb in ROWS:
        topic(title,area,path,symbol,why,principle,use,"반환 분류와 실제 회수 완료를 구분하고 상태 변화를 계산하세요.",q(title+" · "+qa[0],*qa[1:]),q(title+" · "+qb[0],*qb[1:]),details=[detail(dt,body),detail("검토 범위","v6.12의 helper와 직접 호출 분기를 대조했습니다. 실제 메모리 압박이나 페이지 회수 경쟁을 실행한 실험은 아닙니다.")])
