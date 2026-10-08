"""Managed kmalloc and realloc allocation-size and ownership contracts."""
ROWS = [('Devm 메모리: 0바이트 특수 포인터와 비어 있는 release',
  '장치와 하드웨어',
  'drivers/base/devres.c',
  'devm_kmalloc',
  '메모리 자체를 관리 자원에 포함하면 드라이버 분리 때 별도 free 분기를 줄일 수 있습니다. 다만 일반 kmalloc처럼 크기0과 초기화 플래그의 의미를 정확히 구분해야 합니다.',
  'devm_kmalloc은 size=0이면 ZERO_SIZE_PTR을 반환하며 실제 관리 항목을 만들지 않습니다. 나머지는 dev_to_node의 node에서 alloc_dr를 호출하고 실패는 '
  'NULL입니다. 진단 이름·크기를 기록하고 devres_add로 등록한 data를 반환합니다. release callback devm_kmalloc_release는 비어 있지만 최종 devres '
  '해제에서 관리 객체와 data가 한 할당으로 kfree되므로 메모리는 정리됩니다.',
  '진단 문자열이 devm_kzalloc_release라고 적혀 있어도 원문은 역사적 이름이라고 설명합니다. 실제0초기화는 전달 gfp와 alloc_dr의 __GFP_ZERO 처리에 달려 있으므로 '
  'devm_kmalloc이 언제나 데이터를0으로 만든다고 할 수 없습니다. ZERO_SIZE_PTR은 NULL과 다른 특별 반환값이며 정상 데이터를 역참조할 포인터가 아닙니다.',
  '조기 해제와 const 문자열의 예외',
  'devm_kfree는 kernel rodata 포인터 또는 ZERO/NULL이면 바로 반환합니다. 일반 포인터는 release 종류와 data 주소가 일치하는 항목을 devres_destroy로 '
  '찾아 관리 메모리를 해제하고 찾지 못하면 WARN입니다. devm_kstrdup_const가 rodata이면 원래 주소를 반환할 수 있기 때문에 이런 예외가 있습니다. 다른 장치 소유의 포인터를 '
  '넘기거나 원래 할당 시작 주소처럼 kfree하는 것이 같은 사용법은 아닙니다.',
  ('devm_kmalloc(dev,0,...)은 반드시 NULL인가요?',
   '아닙니다. ZERO_SIZE_PTR을 반환합니다.',
   '그렇습니다. 크기0은 항상 메모리 부족입니다.',
   '0크기 분기는 할당 실패 NULL 분기와 다릅니다.'),
  ('release callback이 비어 있으면 data가 누수되나요?',
   '이 경우 아닙니다. 관리 객체와 data를 담은 할당이 해제됩니다.',
   '그렇습니다. callback이 free를 호출하지 않으면 항상 누수입니다.',
   'devres 최종 정리의 kfree가 결합된 메모리를 해제합니다.')),
 ('Devm 재할당: 버킷 재사용과 해제 순서 보존',
  '장치와 하드웨어',
  'drivers/base/devres.c',
  'devm_krealloc',
  '버퍼를 키우거나 줄여도 자동 정리 목록에서 원래 위치를 유지해야 다른 자원과의 해제 순서가 바뀌지 않습니다. 또 요청 크기와 할당자가 실제 확보한 버킷 크기는 달라 재할당이 항상 새 메모리를 필요로 '
  '하지는 않습니다.',
  'devm_krealloc은 new_size=0이면 devm_kfree 후 ZERO_SIZE_PTR, 기존 포인터가 ZERO/NULL이면 devm_kmalloc입니다. rodata는 경고와 '
  'NULL입니다. 크기 검사를 하고 ksize로 실제 이전 할당 크기를 얻어0이면 경고와 NULL입니다. 새 총 크기가 이전 실제 크기 이하이면 포인터를 그대로 반환합니다. 더 크면 잠금 밖에서 새 '
  '객체를 할당하고 잠금 안에서 해당 장치의 이전 관리 항목을 찾습니다.',
  '이전 항목이 없으면 unlock 후 새 객체를 해제하고 경고와 NULL입니다. 찾으면 replace_dr로 기존 목록 위치에 새 노드를 넣고 unlock합니다. 이후 이전 실제 총 크기에서 data '
  'offset을 뺀 바이트를 복사하고 old_dr를 kfree해 새 data를 반환합니다. 일반 확대에서는 등록 위치를 유지하며 NULL fallback이나 크기0 제거는 예외입니다.',
  '왜 같은 포인터 반환과 잠금 범위를 주의하나',
  '실제 버킷 안에 맞으면 조기 반환하므로 이 경로는 새 영역을 따로0초기화하거나 다른 장치의 관리 목록에서 다시 검사하지 않습니다. 정상적으로 해당 dev에서 얻은 포인터를 전달해야 합니다. 목록 '
  '잠금은 링크만 보호하며 복사하는 data 자체의 동시 사용을 보호하지 않는다고 원문이 명시합니다. 실패 시 기존 포인터를 잃지 않도록 임시 변수로 결과를 받는 사용 방식이 필요합니다. 목록에서 '
  '교체된 old는 devm_kfree가 아니라 직접 kfree합니다.',
  ('new_size가 늘면 항상 새 포인터가 반환되나요?',
   '아닙니다. 실제 이전 버킷에 맞으면 같은 포인터입니다.',
   '그렇습니다. 요청 크기 증가가 반드시 재할당입니다.',
   '비교는 요청한 이전 크기가 아니라 ksize의 실제 할당 크기입니다.'),
  ('devres_lock이 data 복사 중 다른 사용자의 접근도 막나요?',
   '아닙니다. 목록 링크 보호이며 데이터 동시성은 별도입니다.',
   '그렇습니다. 모든 버퍼 사용자는 자동으로 차단됩니다.',
   '원문 주석과 unlock 후 memcpy 순서가 보호 범위를 보여줍니다.'))]

def register(topic,q,detail):
    for title,area,path,symbol,why,principle,use,dt,body,qa,qb in ROWS:
        topic(title,area,path,symbol,why,principle,use,"요청 크기와 실제 버킷 크기, 목록 위치와 데이터 보호를 구별하세요.",q(title+" · "+qa[0],*qa[1:]),q(title+" · "+qb[0],*qb[1:]),details=[detail(dt,body),detail("검토 범위","Linux v6.12 devres.c의 kmalloc·krealloc·kfree와 연결 helper를 대조했습니다. 실제 드라이버 경쟁이나 메모리 재할당 실패를 실행한 검증은 아닙니다.")])
