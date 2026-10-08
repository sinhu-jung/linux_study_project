"""Linux v6.12 irqdomain.c 1604–1713, main allocation and reverse-map repair."""
ROWS=[
('계층 IRQ 주 할당: descriptor 재사용과 단계별 실패 정리','irq_domain_alloc_irqs_locked',
 'IRQ 하나를 준비하려면 번호 객체·부모 데이터·컨트롤러 자원이 차례로 필요합니다. 앞 단계까지만 성공했을 때는 성공한 단계에 맞춰 정리해야 합니다.',
 'realloc이 참이고 irq_base>=0이면 기존 descriptor 번호를 사용합니다. 그 외에는 hwirq 힌트 0으로 irq_domain_alloc_descs를 호출하고 음수 실패를 그대로 반환합니다. 이어 부모 데이터를 만들며 실패하면 ret=-ENOMEM으로 out_free_desc에 갑니다. 계층 alloc 콜백이 음수를 반환하거나 trim이 0 아닌 값을 반환하면 out_free_irq_data로 갑니다. 이 레이블은 부모 데이터를 정리한 다음 아래 out_free_desc로 이어져 descriptor 범위도 반납합니다. realloc 경로도 이 마지막 반납을 건너뛰는 조건은 없습니다.',
 '번호 할당 실패·부모 할당 실패·콜백 실패·trim 실패 네 경우에 도착하는 레이블을 표로 쓰세요. 기존 descriptor를 쓴 경우에도 뒤 실패 시 irq_free_descs가 호출된다는 점을 표시하세요.',
 '왜 정리 레이블이 두 개이고 fall-through하는가','부모 데이터 할당 helper는 자체 실패 시 이미 만든 부모를 스스로 정리하므로 caller는 descriptor 정리로 바로 갑니다. 부모 구성이 성공한 뒤 실패하면 부모를 먼저 비워야 합니다. 레이블 다음에는 자동 return이 없으므로 부모 정리 뒤 descriptor 정리로 실행이 이어집니다. 단, 이 오류 경로에는 domain->ops->free를 직접 호출하는 코드가 없습니다. 하드웨어 자원까지 항상 자동 복구된다고 확대하지 말고 alloc 콜백의 오류 정리 계약과 trim 실패의 전제 위반을 따로 확인해야 합니다.',
 ('realloc=true로 기존 descriptor를 썼으면 이후 실패에서도 반드시 보존되나요?','아닙니다. 공통 실패 경로는 irq_free_descs를 호출합니다.','그렇습니다. 이름이 realloc이면 반납하지 않습니다.','원문에는 마지막 free_descs를 realloc 조건으로 감싸는 분기가 없습니다.'),
 ('out_free_irq_data에서 부모 데이터만 정리하고 반환하나요?','아닙니다. 다음 레이블의 descriptor 반납까지 이어집니다.','그렇습니다. 레이블 끝에서 자동 반환됩니다.','C 레이블은 점프 위치이며 뒤 코드로 이어지는 실행을 자동 차단하지 않습니다.')),
('계층 IRQ 공개 순서: 모든 trim이 성공한 뒤 매핑 설치','irq_domain_alloc_irqs_locked',
 '여러 IRQ 중 일부만 검증한 상태에서 외부 검색 표에 공개하면 뒤쪽 실패 때 이미 공개된 연결까지 되돌려야 합니다.',
 '부모 데이터와 계층 alloc 콜백이 준비되면 첫 루프가 전체 nr_irqs에 대해 trim을 수행합니다. 모든 trim이 성공해야 두 번째 루프에서 각 IRQ의 역매핑을 insert합니다. 성공 반환은 시작 virq이고 nr_irqs나 항상 0이 아닙니다. 콜백 결과는 ret<0을 실패로 검사하지만 trim 결과는 ret 자체를 검사합니다. 이름의 locked는 이 함수가 mutex를 직접 잡는다는 뜻이 아니라 호출자가 root mutex를 보유한 문맥에서 사용하는 내부 helper라는 뜻입니다.',
 '100·101·102 중 102의 trim이 실패하면 앞의 100과 101도 아직 역매핑을 설치하지 않았음을 순서도로 그리세요. 다만 앞 trim에서 사슬 일부가 이미 잘렸을 가능성은 구분하세요.',
 '검증 전후를 나누는 효과와 한계','등록을 나중으로 미루면 검증 실패가 공개된 역매핑을 남기는 문제를 줄입니다. 하지만 trim은 읽기 검사만 하는 함수가 아니라 필요 없는 부모를 잘라 해제할 수도 있습니다. 따라서 첫 루프 전체를 상태를 전혀 바꾸지 않는 검사라고 설명하면 틀립니다. 실패하면 남아 있는 부모 사슬을 공통 정리 helper가 처리합니다.',
 ('첫 IRQ의 trim 성공 직후 그 IRQ의 역매핑을 등록하나요?','아닙니다. 모든 IRQ의 trim이 끝난 뒤 별도 루프에서 등록합니다.','그렇습니다. trim과 insert를 번호마다 묶습니다.','두 개의 독립된 for 루프가 전체 검증과 전체 공개의 순서를 만듭니다.'),
 ('성공하면 항상 0을 반환하나요?','아닙니다. 할당한 시작 virq를 반환합니다.','그렇습니다. 커널 함수의 성공은 모두 0입니다.','마지막 성공 return은 virq이며 호출자마다 성공값의 계약을 확인해야 합니다.')),
('IRQ 공개 할당 진입점: 기본 domain과 root mutex','__irq_domain_alloc_irqs',
 '같은 IRQ 계층의 여러 domain에서 동시에 연결을 바꾸면 공유 사슬과 역매핑의 상태가 서로 어긋날 수 있습니다.',
 'domain 인자가 NULL이면 irq_default_domain을 사용하고 그것도 없으면 경고 후 -EINVAL입니다. 유효한 domain이면 domain->root->mutex를 잡고 locked helper에 나머지 인자를 전달한 뒤 잠금을 풀고 결과를 반환합니다. 하위 helper의 음수 오류와 성공 번호를 이 wrapper가 다른 값으로 변환하지 않습니다. 각 자식마다 별도 잠금을 잡는 것이 아니라 계층의 root가 가진 mutex를 사용하며 이 본문은 하드웨어 activate 함수를 호출하지 않습니다.',
 '입력 domain 없음·기본 domain 있음과 둘 다 없음 두 경로를 그리세요. 하위 할당 결과가 -ENOMEM이어도 mutex_unlock을 거친 뒤 반환됨을 확인하세요.',
 '왜 자원 확보와 하드웨어 활성화를 나누나','원문은 먼저 descriptor와 필요한 하드웨어 자원을 확보하고 이후 irq_domain_activate_irq로 미리 확보한 자원을 하드웨어에 적용한다고 설명합니다. 여러 자원을 확보하다 실패했을 때 아직 활성화하지 않은 준비 상태를 정리하는 편이 전체 동작을 시작한 뒤 복구하는 것보다 관리하기 쉽습니다. alloc 콜백의 모든 부수 효과가 없다는 뜻은 아니며 이 함수의 성공을 곧바로 장치 인터럽트 처리 시작으로 읽으면 안 됩니다.',
 ('NULL domain이면 무조건 즉시 실패하나요?','아닙니다. 기본 domain을 먼저 사용해 봅니다.','그렇습니다. 기본 domain은 이 경로에서 사용하지 않습니다.','NULL 분기에서 irq_default_domain을 대입하고 그것도 없을 때만 -EINVAL입니다.'),
 ('하위 helper가 오류를 반환하면 root mutex를 잡은 채 나가나요?','아닙니다. 결과를 저장하고 unlock한 뒤 반환합니다.','그렇습니다. 오류가 자동으로 함수를 중단합니다.','호출 결과가 ret에 저장된 뒤 공통 unlock과 return이 실행됩니다.')),
('IRQ 데이터 이동 후 역매핑 복구: 주소와 키의 차이','irq_domain_fix_revmap',
 'IRQ 번호가 같아도 irq_data 객체가 다른 메모리 위치로 옮겨지면 검색 표가 예전 주소를 계속 가리킬 수 있습니다.',
 'root mutex 보유를 lockdep_assert_held로 확인하고 NOMAP domain이면 반환합니다. hwirq<revmap_size이면 배열 슬롯에 rcu_assign_pointer로 새 data 주소를 기록합니다. 그 외에는 radix_tree_lookup_slot으로 기존 키의 슬롯을 찾아 있을 때만 replace_slot을 호출합니다. 트리에 슬롯이 없으면 새 노드를 삽입하지 않습니다. 이 함수는 hwirq·mapcount를 변경하거나 이전 객체를 free하지 않으며 mutex를 스스로 획득하는 코드도 없습니다.',
 '키 7이 주소 A를 가리키다 데이터가 B로 이동한 경우 슬롯 값만 B로 바뀌는 모습을 그리세요. revmap_size=8이면 키 7은 배열, 키 8은 트리이며 트리 슬롯이 없는 경우와 있는 경우를 나누세요.',
 '왜 assert와 lock은 다르나','lockdep_assert_held는 필요한 잠금이 이미 잡혀 있는지 진단하는 장치입니다. 잠금을 새로 잡거나 기다려 주는 mutex_lock과 다릅니다. RCU 포인터 공개 역시 이전 객체의 수명을 자동으로 영구 보장하지 않으므로 이동·해제 절차와 호출 문맥의 보호를 함께 읽어야 합니다.',
 ('트리에 해당 키가 없으면 이 함수가 새 매핑을 삽입하나요?','아닙니다. 슬롯이 있을 때만 교체합니다.','그렇습니다. lookup 실패가 자동 insert입니다.','if (slot) 안에서만 replace하며 삽입 함수 호출은 없습니다.'),
 ('lockdep_assert_held가 root mutex를 직접 잡나요?','아닙니다. 이미 보유한 잠금에 대한 진단입니다.','그렇습니다. mutex_lock과 같은 기능입니다.','호출자는 잠금 전제를 충족해야 하며 assertion은 동기화 획득을 대신하지 않습니다.')),
]
def register(topic,q,detail):
 for title,symbol,why,principle,use,dt,body,qa,qb in ROWS:
  topic(title,'장치·드라이버','kernel/irq/irqdomain.c',symbol,why,principle,use,'실패 레이블에 도달할 때 이미 확보된 자원을 적고 실제 정리 호출과 대조하세요. 번호·포인터·역매핑 키·활성화 상태를 서로 다른 값으로 추적하세요.',q(title+' · '+qa[0],*qa[1:]),q(title+' · '+qb[0],*qb[1:]),details=[detail(dt,body),detail('검토 범위','고정 Linux v6.12 irqdomain.c 1604–1713행의 주 할당·공개 wrapper·이동 후 역매핑 복구를 읽었습니다. 실제 장치 IRQ를 실행한 검증은 아니며 1714–2135행의 계층 push/pop·활성화·해제·진단은 미완료입니다.')])
