"""Managed string, formatted, page and per-CPU allocations."""
ROWS = [('Devm 문자열·메모리 복사: 끝의 NUL과 rodata 재사용',
  '장치와 하드웨어',
  'drivers/base/devres.c',
  'devm_kstrdup',
  'C 문자열의 길이는 끝을 표시하는0바이트를 제외합니다. 문자열로 다시 사용하려면 끝 표시까지 복사해야 하지만 일반 메모리는 중간에0이 있을 수 있어 길이를 별도로 받아야 합니다.',
  'devm_kstrdup은 입력 s가 NULL이면 NULL입니다. strlen(s)+1만큼 devm_kmalloc하고 성공하면 그 전체 크기를 memcpy하므로 끝 NUL도 복사합니다. '
  'devm_kstrdup_const는 is_kernel_rodata이면 원래 s를 그대로 반환하고 아니면 일반 문자열 복사로 갑니다. devm_kmemdup은 문자열 길이를 찾지 않고 len바이트를 '
  '할당하고 성공 시 그 길이만 복사합니다.',
  '문자열 cat은 문자3개지만 필요한 공간은 NUL까지4바이트입니다. 바이트 배열 [65,0,66]을 len3으로 kmemdup하면 세 바이트 모두 복사됩니다. strlen 기반 문자열 복사는 '
  '중간0을 끝으로 보므로 같은 작업이 아닙니다. const 복사의 rodata 경로는 새 관리 항목이나 새 문자열을 만들지 않습니다.',
  '왜 const 결과의 주소가 원본과 같을 수 있나',
  '이미 커널 읽기 전용 영역에 있는 문자열은 별도 복사 없이 사용할 수 있는 경로를 택합니다. 호출자는 반환을 수정 가능한 새 메모리로 생각하면 안 됩니다. 정상 문자열은 읽을 수 있는 NUL 종료 '
  '입력이어야 하고 kmemdup도 입력 범위를 자동 검증하지 않습니다. 길이0 kmemdup은 devm_kmalloc의 ZERO_SIZE_PTR 규칙을 따르므로 단순 NULL 실패만으로 크기 의미를 '
  '판단하지 않습니다.',
  ('cat의 문자열 복사 할당 크기는?', '4바이트입니다.', '3바이트입니다.', 'strlen의3에 끝 NUL 공간1을 더합니다.'),
  ('rodata 입력의 kstrdup_const는 항상 새 주소인가요?',
   '아닙니다. 원래 주소를 반환할 수 있습니다.',
   '그렇습니다. strdup라는 이름이면 항상 새 할당입니다.',
   '첫 분기는 is_kernel_rodata이면 즉시 s를 반환합니다.')),
 ('Devm 서식 문자열: 가변 인자를 두 번 읽기 위해 복사하기',
  '장치와 하드웨어',
  'drivers/base/devres.c',
  'devm_kvasprintf',
  '서식 문자열의 최종 길이를 알기 전에 버퍼를 정하면 너무 작게 잡거나 불필요하게 크게 잡을 수 있습니다. 먼저 필요한 길이를 계산하고 정확한 크기를 할당해 두 번째로 출력하는 방식을 씁니다.',
  'devm_kvasprintf는 va_copy로 ap를 aq에 복사하고 vsnprintf(NULL,0,fmt,aq)로 길이를 구한 뒤 aq를 va_end합니다. len+1을 devm_kmalloc하고 '
  '실패하면 NULL입니다. 성공하면 원래 ap로 실제 출력한 뒤 p를 반환합니다. devm_kasprintf는 ... 인자에 va_start를 적용해 이 helper를 부르고 va_end한 뒤 결과를 '
  '전달합니다.',
  'fmt가 dev-%d이고 정수7이면 출력 dev-7의 길이는5, 할당은 끝 NUL까지6입니다. 첫 길이 계산에 복사본 aq를 쓰는 이유는 가변 인자 순회 상태를 소비한 뒤 같은 ap를 그대로 '
  '재사용하는 실수를 피하려는 것입니다. va_list는 단순한 임의 포인터 복사와 같은 타입이라고 가정하면 안 됩니다.',
  '왜 두 번의 계산 사이 입력 안정성도 필요한가',
  '서식에 쓰이는 문자열 등 데이터가 첫 길이 계산과 실제 출력 사이에 바뀌면 첫 계산 길이가 최종 출력에 맞지 않을 수 있습니다. 두 번째 vsnprintf는 길이 제한을 받지만 이 helper는 그 '
  '반환 길이를 다시 검사해 재할당하지 않습니다. 길이는 unsigned int에 저장하고 len+1을 사용하므로 임의의 거대한 출력 길이를 안전하게 거절하는 일반 입력 파서라고 확대하면 안 됩니다. '
  '유효하고 적절한 크기의 kernel printf 규약 인자가 전제입니다.',
  ('첫 길이 계산에는 어떤 va_list를 쓰나요?',
   'va_copy로 만든 aq입니다.',
   '원본 ap만 두 번 그대로 씁니다.',
   '원문은 복사본으로 길이를 계산한 뒤 원래 목록으로 출력합니다.'),
  ('두 번째 출력 결과가 더 길어지면 자동으로 재할당하나요?',
   '아닙니다. 두 번째 반환 길이를 검사하는 루프가 없습니다.',
   '그렇습니다. 항상 완전한 출력이 될 때까지 반복합니다.',
   '입력 안정성과 제공된 크기 제한을 구분해 읽어야 합니다.')),
 ('Devm 페이지 할당: 실제 페이지와 정리 기록을 따로 얻기',
  '장치와 하드웨어',
  'drivers/base/devres.c',
  'devm_get_free_pages',
  '페이지 묶음은 해제할 때 시작 주소뿐 아니라 order도 필요합니다. 자동 정리 기록에 그 정보를 저장하면 호출자가 조기 해제 시 order를 다시 전달하지 않아도 됩니다. 대신 실제 페이지와 '
  '기록의 두 할당 실패를 모두 처리해야 합니다.',
  'devm_get_free_pages는 __get_free_pages(gfp_mask,order)를 먼저 호출하고 주소0이면 실패0입니다. 다음으로 pages_devres를 GFP_KERNEL로 '
  '할당하며 실패하면 방금 얻은 페이지를 free_pages(addr,order)하고0입니다. 성공하면 주소와 order를 기록하고 devres_add 후 주소를 반환합니다. release '
  'helper는 저장된 두 값으로 free_pages를 호출합니다. match는 주소만 비교합니다.',
  'order2는4페이지입니다. 설명용4KiB 페이지 시스템이면 총16KiB입니다. devm_free_pages는 주소를 검색 조건으로 devres_release하므로 caller가 order를 넘기지 '
  '않아도 저장된 값으로 해제합니다. 항목이 없으면 WARN_ON이며 실제 자원을 찾았다고 가정해 다른 주소를 무작정 해제하지 않습니다.',
  '왜 gfp_mask만 보고 원자 문맥용이라고 판단하면 안 되나',
  '첫 페이지 할당은 caller의 gfp_mask를 쓰지만 관리 기록 할당은 본문에 GFP_KERNEL로 고정돼 있습니다. 따라서 gfp_mask를 원자 할당용으로 줬다는 사실만으로 전체 '
  'wrapper가 잠들지 않는다고 생각하면 안 됩니다. 성공 후 직접 free_pages만 호출하고 관리 항목을 남겨도 나중 자동 정리와 중복될 수 있으므로 짝인 관리 해제 경로를 사용해야 합니다.',
  ('관리 기록 할당만 실패하면 이미 얻은 페이지는?',
   '즉시 free_pages하고 실패0을 반환합니다.',
   '장치 분리까지 기록 없이 남겨 둡니다.',
   '실패 분기가 기록을 얻지 못한 실제 자원을 직접 되돌립니다.'),
  ('관리 기록 할당도 caller의 gfp_mask를 그대로 쓰나요?',
   '아닙니다. 여기서는 GFP_KERNEL입니다.',
   '그렇습니다. 모든 내부 할당이 같은 플래그입니다.',
   '두 할당 호출의 인자를 따로 확인해야 합니다.')),
 ('Devm CPU별 메모리: 포인터를 담은 관리 기록과 실제 대상',
  '장치와 하드웨어',
  'drivers/base/devres.c',
  '__devm_alloc_percpu',
  'CPU별 메모리를 각 CPU의 작업에 나눠 사용할 수 있지만 그 메모리를 정리하려면 실제 per-CPU 할당을 반환해야 합니다. 포인터를 저장한 작은 관리 기록만 해제하면 실제 메모리가 남습니다.',
  '__devm_alloc_percpu는 __alloc_percpu(size,align)을 먼저 호출하고 실패하면 NULL입니다. 다음으로 포인터 하나 크기의 관리 기록을 GFP_KERNEL로 할당하며 '
  '실패하면 free_percpu 후 NULL입니다. 성공하면 기록 안에 pcpu 포인터를 저장하고 등록한 뒤 실제 pcpu를 반환합니다. release는 기록에서 그 포인터를 꺼내 '
  'free_percpu를 호출하고 match는 기록에 담긴 포인터와 요청 대상을 비교합니다.',
  'devm_free_percpu는 devres_release로 찾아 제거하고 실제 release까지 실행합니다. devres_destroy만 쓰면 포인터를 담은 기록만 해제되어 per-CPU 메모리가 '
  '누수되므로 원문 주석이 release 사용 이유를 명시합니다. 여기의 per-CPU 포인터는 일반 연속 버퍼처럼 임의로 역참조하는 주소와 구분해야 하며 실제 접근은 per-CPU API의 계약을 '
  '따릅니다.',
  '공통 관리 구조와 진단 정보',
  'devres_node에는 목록 entry,release,name,size가 있고 devres는 node와 정렬된 가변 data를 갖습니다. 그룹은 표식 두 개,id,color를 갖습니다. '
  'set_node_dbginfo는 이름·크기를 기록하며 devres_log는 trace를 호출하고 CONFIG_DEBUG_DEVRES 및 log 설정에 따라 debug 출력을 더합니다. add_dr는 '
  '빈 노드를 목록 뒤에 붙이고 replace_dr는 새 노드가 비었는지 확인해 기존 위치를 바꿉니다. log 모듈 매개변수는 기본0이고 S_IRUGO|S_IWUSR 권한입니다. 설정이 꺼지면 devres_dbg는 빈 do-while 매크로가 됩니다. 이런 관리·진단 기록과 실제 자원은 구분됩니다. 파일의 SPDX는 GPL-2.0이며 헤더들은 '
  '장치·slab·percpu·rodata 및 trace 기반을 연결합니다.',
  ('관리 기록만 destroy하면 실제 per-CPU 메모리도 반환되나요?',
   '아닙니다. release callback 실행이 필요합니다.',
   '그렇습니다. 기록에 주소가 있으면 자동으로 대상까지 free합니다.',
   '포인터를 담은 메모리와 포인터가 가리키는 할당은 별개입니다.'),
  ('두 번째 관리 기록 할당 실패 시에는?',
   '먼저 얻은 pcpu를 free_percpu하고 NULL입니다.',
   'pcpu를 성공으로 반환하고 정리는 생략합니다.',
   '자동 정리를 등록하지 못했으므로 실제 할당을 되돌리는 실패 경로입니다.'))]

def register(topic,q,detail):
    for title,area,path,symbol,why,principle,use,dt,body,qa,qb in ROWS:
        topic(title,area,path,symbol,why,principle,use,"실제 자원과 관리 기록의 두 할당, 길이 단위와 실패 복구를 구분하세요.",q(title+" · "+qa[0],*qa[1:]),q(title+" · "+qb[0],*qb[1:]),details=[detail(dt,body),detail("검토 범위","Linux v6.12 devres.c의 문자열·페이지·percpu wrapper와 연결 해제 함수를 대조했습니다. 실제 메모리 고갈·드라이버 분리 실험을 실행한 검증은 아닙니다.")])
