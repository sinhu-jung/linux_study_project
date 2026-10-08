"""Reconciliation additions for irqdomain.c debugfs conditional definitions."""
ROWS=[
('IRQ 진단 비활성 빌드: 빈 helper로 유지하는 공통 호출부','debugfs_add_domain_dir',1,
 '진단 기능을 끈 빌드에서도 domain 생성·제거 코드는 같은 helper를 호출할 수 있도록 인터페이스를 유지할 필요가 있습니다.',
 'CONFIG_GENERIC_IRQ_DEBUGFS가 켜지면 파일 앞부분은 add/remove 함수의 선언만 제공하고 뒤쪽 실제 정의가 컴파일됩니다. 꺼지면 debugfs_add_domain_dir와 debugfs_remove_domain_dir를 static inline 빈 본문으로 정의합니다. 이 빌드의 호출은 진단 파일 생성이나 삭제를 수행하지 않습니다. domain 생성·매핑 기능 전체를 끄는 것이 아니라 진단용 부수 작업을 생략하는 구조입니다. 함수가 void라 이 대체 경로에서 호출자에게 실패 코드를 돌려주지도 않습니다.',
 '설정 켜짐과 꺼짐에서 add helper의 실제 본문이 어디인지 표시하세요. 빈 helper를 호출한 뒤 domain 생성 본체는 계속 진행할 수 있는 이유를 설명하세요.',
 '왜 호출하는 곳마다 전처리 조건을 쓰지 않나','공통 호출부를 유지하고 기능 선택을 helper 정의에 모으면 생성·이름 변경·제거 경로마다 같은 #ifdef를 반복할 필요가 줄어듭니다. static은 이 번역 단위 안의 연결 범위를 나타내고 inline은 모든 호출이 반드시 특정 기계 명령으로 치환된다는 보장이 아닙니다. 학습할 핵심은 빈 본문이 관찰 가능한 debugfs 작업을 하지 않는다는 점입니다.',
 ('진단 설정을 끄면 domain 생성 자체가 항상 실패하나요?','아닙니다. 진단용 helper가 빈 동작이 됩니다.','그렇습니다. debugfs 파일이 없으면 IRQ를 만들 수 없습니다.','진단 부수 기능을 대체하는 정의이며 핵심 domain 생성 실패를 반환하는 코드가 없습니다.'),
 ('설정이 켜진 앞부분의 함수 선언이 실제 파일 생성 코드인가요?','아닙니다. 실제 정의는 뒤쪽 조건부 구간에 있습니다.','그렇습니다. 세미콜론 선언이 호출 작업을 수행합니다.','함수 선언은 서명을 알리는 역할이고 실행 본문은 중괄호 안의 정의에 있습니다.')),
('IRQ 진단 삭제 helper: 이름으로 제거하고 객체 수명은 분리하기','debugfs_remove_domain_dir',2,
 'domain의 진단 항목을 없애는 작업과 domain 메모리를 반납하는 작업은 대상과 호출 계약이 다릅니다.',
 '진단 활성 빌드의 debugfs_remove_domain_dir는 debugfs_lookup_and_remove(d->name,domain_dir)를 한 번 호출합니다. add helper에 있는 !d->name 또는 !domain_dir 검사도 이 삭제 wrapper에는 없습니다. create_file이 반환한 파일 포인터를 저장해 사용하는 구조가 아니라 부모 디렉터리와 현재 이름으로 찾아 제거하도록 위임합니다. 이 본문에는 kfree(d), 매핑 제거, IRQ 번호 반납이 없고 반환형도 void입니다. 이름 변경 경로에서는 어느 이름일 때 삭제하고 새 이름을 언제 등록하는지 순서를 함께 읽어야 합니다.',
 'domain.name이 old일 때 삭제한 뒤 new로 바꾸어 등록하는 순서를 그리세요. 이름부터 new로 바꾼 뒤 old 파일을 찾으려 하면 검색에 어떤 이름을 전달하게 되는지 비교하세요.',
 'wrapper에 없는 검사와 하위 API의 계약','이 함수 자체가 NULL이나 오류를 검사한다고 설명하면 원문과 다릅니다. 그렇다고 여기만 보고 하위 API가 어떤 입력에도 안전하다거나 즉시 충돌한다고 단정할 수도 없습니다. wrapper가 무엇을 전달하고 무엇을 보장하지 않는지 적은 뒤 하위 debugfs 구현의 입력·수명 규약을 확인하는 것이 정확한 독해입니다.',
 ('삭제 wrapper가 add와 똑같은 NULL 검사를 먼저 하나요?','아닙니다. 바로 lookup_and_remove에 위임합니다.','그렇습니다. 이름과 디렉터리가 없으면 자체 반환합니다.','add의 조건을 비슷한 이름의 remove 본문에도 있다고 가정하면 안 됩니다.'),
 ('이 함수에서 kfree(d)로 domain까지 반납하나요?','아닙니다. 진단 항목 제거만 위임합니다.','그렇습니다. 삭제라는 이름은 전체 객체 해제입니다.','단 하나의 debugfs 호출과 domain 자원 해제의 책임을 구분해야 합니다.')),
]
def register(topic,q,detail):
 for title,symbol,occ,why,principle,use,dt,body,qa,qb in ROWS:
  topic(title,'장치·드라이버','kernel/irq/irqdomain.c',symbol,why,principle,use,'함수 선언·빈 대체 정의·실제 정의를 구분하고 빌드 설정별 호출 흐름을 표시하세요. 진단 파일과 IRQ domain 객체의 수명을 따로 그리세요.',q(title+' · '+qa[0],*qa[1:]),q(title+' · '+qb[0],*qb[1:]),source_occurrence=occ,details=[detail(dt,body),detail('대조 검토의 범위','irqdomain.c의 동일 이름 정의와 보조 함수 설명을 대조하면서 추가한 수업입니다. 이 보강만으로 모든 분기의 의미 검토나 Linux 전체 구현 해설이 완료됐다고 판단하지 않습니다. 실제 커널 빌드·debugfs 실행은 수행하지 않았습니다.')])
