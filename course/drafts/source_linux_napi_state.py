"""NAPI state, ownership and softirq budget scheduling."""
ROWS = [('NAPI 예약: 이미 실행 중인 요청을 MISSED로 기억하기',
  'napi_schedule_prep',
  '패킷마다 인터럽트에서 모든 수신 처리를 하면 한 장치가 CPU를 오래 차지할 수 있습니다. NAPI는 처리 작업을 예약해 한 번에 제한된 양을 poll합니다. 이미 예약된 작업에 새 요청이 겹칠 때 같은 인스턴스를 중복 실행하지 않으면서 새 '
  '요청도 놓치지 않아야 합니다.',
  'napi_schedule_prep는 state를 읽고 DISABLE이면 false입니다. 그렇지 않으면 SCHED를 더한 새 상태를 만들고 기존에 SCHED가 있었다면 MISSED도 더합니다. try_cmpxchg가 실패하면 갱신된 val로 '
  '다시 계산합니다. 성공 뒤 기존 SCHED가 없었을 때만 true를 반환합니다.',
  '처음 SCHED0인 상태에서 CPU A가 성공하면 SCHED1,true입니다. 이어 CPU B가 요청하면 SCHED1을 유지하면서 MISSED1로 바꾸고 false입니다. B의 false는 상태를 아무것도 바꾸지 않았다는 뜻이 아니라 새 '
  'poll 예약권은 얻지 못했지만 재요청 표시를 남겼다는 뜻입니다.',
  '비트 나눗셈 식을 논리로 풀기',
  '(val&SCHED)/SCHED는 해당 비트가 없으면0,있으면1입니다. 여기에 MISSED 비트 값을 곱해 새 상태에 OR하므로 숫자 나눗셈으로 비트 사이 조건부 전달을 표현합니다. 이 함수는 예약 가능성을 획득하는 단계이고 실제 목록 배치는 '
  '__napi_schedule 쪽입니다. 그 함수는 로컬 IRQ 상태를 저장·복원하며,irqoff 변형도 PREEMPT_RT에서는 일반 경로로 돌아가 IRQ 가정을 보완합니다.',
  ('이미 SCHED인 인스턴스에 새 예약 요청이 오면?',
   'MISSED를 남기고 false를 반환합니다.',
   '두 번째 poll을 무조건 동시에 실행합니다.',
   '중복 소유권 획득은 막으면서 이후 완료 경로에서 추가 작업을 알아볼 비트를 저장합니다.'),
  ('try_cmpxchg 실패 후 기존 새 상태를 그대로 강제로 쓰나요?',
   '아닙니다. 갱신된 val로 다시 계산합니다.',
   '그렇습니다. 다른 CPU 변경을 덮어씁니다.',
   '비교 교환 반복은 그 사이 바뀐 상태를 반영해 DISABLE과 예약 비트를 다시 판단합니다.')),
 ('NAPI 완료: MISSED 재예약과 타이머 기반 지연',
  'napi_complete_done',
  'poll이 현재 할 일을 끝내는 순간 새 수신 요청이 겹칠 수 있습니다. 그냥 SCHED를 지우면 이미 들어온 추가 작업이 남을 수 있어 완료 함수도 예약 함수와 같은 상태 전이를 조정해야 합니다.',
  'napi_complete_done은 NPSVC 또는 IN_BUSY_POLL이면 false로 바로 반환합니다. 일반 경로에서는 work_done과 GRO 상태로 timeout과 IRQ 지연 횟수를 계산하고 GRO/일반 묶음을 처리합니다. '
  'poll_list에 남아 있으면 IRQ 보호 아래 제거하고 list_owner=-1로 합니다. 비교 교환으로 SCHED,MISSED,스레드 예약,선호 busy-poll 비트를 정리하되 기존 MISSED가 있으면 SCHED를 다시 남깁니다.',
  'SCHED1,MISSED1이었다면 새 상태는 SCHED1,MISSED0이며 __napi_schedule로 다시 예약하고 false입니다. MISSED가 없다면 timeout이 있을 때 상대·CPU 고정 hrtimer를 시작합니다. IRQ 지연 '
  '횟수가 남고 timeout도 있으면 ret=false가 될 수 있으므로 false를 단일 오류 코드처럼 해석하면 안 됩니다.',
  '카운트와 timeout의 실제 적용 순서',
  'work_done이 비0이면 장치의 napi_defer_hard_irqs 값을 카운트로 새로 읽습니다. 양수 카운트는 이번 호출에서1 줄이고 gro_flush_timeout을 사용합니다. gro_bitmask가 있으면 timeout 유무를 '
  'bool로 전달해 GRO flush를 수행합니다. 이 함수 자체가 장치별 IRQ 레지스터를 직접 다시 켜는 것은 아닙니다. 완료 뒤 공유 자료에 계속 접근하면 disable 쪽 수명 계약과 충돌할 수 있다는 NAPI 문서의 주의도 함께 지켜야 '
  '합니다.',
  ('MISSED가 있었다면 완료 과정에서 SCHED도 무조건0이 되나요?',
   '아닙니다. SCHED를 남기고 다시 예약합니다.',
   '그렇습니다. 모든 완료는 모든 비트를 지웁니다.',
   '이전 MISSED를 새 SCHED로 전달하는 비교 교환식과 뒤의 재예약 분기가 연결됩니다.'),
  ('false는 항상 I/O 오류인가요?',
   '아닙니다. busy polling·재예약·IRQ 지연 등의 제어 결과입니다.',
   '그렇습니다. 실패한 패킷의 errno입니다.',
   '여러 제어 분기가 false를 반환하며 오류 번호를 담는 인터페이스가 아닙니다.')),
 ('NAPI poll 예산: 정확히 다 쓴 경우의 재처리 계약',
  '__napi_poll',
  '수신량이 많은 한 장치가 CPU를 독점하지 않도록 poll 한 번의 수신 처리량을 제한합니다. 처리량이 예산과 정확히 같은 경우에는 더 일이 남았는지 반환 숫자만으로 구분할 수 없어 특별한 약속이 필요합니다.',
  '__napi_poll은 weight를 예산으로 삼고 예약 상태일 때 드라이버 poll을 호출하며 trace와 XDP flush 확인을 수행합니다. work>weight면 경고하고 work<weight면 반환합니다. 예산을 다 썼으면 '
  'disable 대기,busy-poll 선호를 먼저 처리합니다. 그 외 GRO와 일반 목록을 정리하고 이미 재예약된 목록이면 경고 후 반환하며 아니면 repoll=true입니다.',
  '예산64에서 work20이면 빠른 반환,work64이면 계속 처리할 후보입니다. 정확히64개로 모든 일을 끝냈어도 문서는 완료를 호출하지 않고 다음 poll을 기다리거나 완료 후63을 반환하는 방식을 설명합니다. 예산0 호출에서는 '
  '수신/XDP/page-pool 처리를 하면 안 되고 napi_complete_done도 호출하지 말아야 합니다. skb 송신 완료 처리는 별도 계약으로 남습니다.',
  '드라이버의 완료 책임과 코어의 목록 책임',
  'work<weight라는 숫자만으로 코어가 자동으로 napi_complete_done을 호출하는 것은 아닙니다. 드라이버는 처리 완료 시 해당 API를 호출해야 합니다. napi_poll wrapper는 현재 poll_list 노드를 먼저 '
  '떼고 netpoll 잠금 아래 __napi_poll을 호출합니다. do_repoll이 참이면 별도 repoll 목록 뒤에 연결한 뒤 잠금을 풉니다. busy-poll 선호 경로에서는 complete_done의 결과에 따라 다시 '
  'napi_schedule하기도 합니다.',
  ('work가 예산보다 작으면 코어가 여기서 완료 API를 자동 호출하나요?',
   '아닙니다. 이 빠른 분기는 work만 반환합니다.',
   '그렇습니다. 드라이버는 완료를 알릴 필요가 없습니다.',
   '실제 조기 반환과 문서의 드라이버 완료 책임을 함께 읽어야 예약 소유권이 남는 실수를 피합니다.'),
  ('예산64를 정확히 소비했는데 모든 일이 끝났다면?',
   '문서의 정확한 예산 경계 처리 규칙을 따라야 합니다.',
   '64를 반환하면서 항상 완료하면 어떤 경우에도 동일합니다.',
   '코어는 정확한 예산 소비를 재처리 신호로 사용하므로 완료와 반환값의 조합을 조정해야 합니다.')),
 ('NAPI 비활성화: callback 반환 대신 소유권 해제를 기다리기',
  'napi_disable',
  '장치를 정리할 때 새 poll 예약을 막고 이미 가진 처리 소유권이 반환되기를 기다려야 합니다. 하지만 완료 API 호출과 드라이버 함수의 마지막 return은 같은 순간이 아니므로 기다림의 정확한 대상을 알아야 합니다.',
  'napi_disable은 might_sleep 후 DISABLE을 설정합니다. SCHED 또는 NPSVC가 남아 있으면20~200마이크로초 usleep_range로 기다리며 상태를 다시 읽습니다. 비워지면 비교 교환으로 두 비트를 직접 설정해 '
  '비활성 상태의 소유권을 잡고 THREADED와 PREFER_BUSY_POLL을 지웁니다. 타이머를 취소한 뒤 DISABLE 비트를 내립니다.',
  'DISABLE이 마지막에0이 돼도 활성 상태가 된 것은 아닙니다. SCHED와 NPSVC가 비활성화용 상태로 남습니다. napi_enable은 SCHED가 있는지 BUG_ON으로 검사하고 두 비트를 지우며 장치 threaded와 thread가 '
  '모두 있으면 THREADED를 더합니다. enable/disable을 임의로 반복해도 되는 멱등 API가 아닙니다.',
  '두 번 disable하면 왜 문제가 되나',
  '첫 disable은 SCHED와 NPSVC를 비활성 표시로 남겼습니다. enable 없이 다시 disable하면 그 비트가 풀리기를 기다리지만 정상 poll이 풀어 줄 상황이 없어 교착될 수 있습니다. 문서는 disable이 poll 함수의 '
  'return 자체가 아니라 소유권 해제를 기다린다고 명시합니다. 따라서 완료 API 뒤에도 드라이버가 해제될 자료에 계속 접근하지 않도록 수명을 설계해야 합니다. 예약 상태를 일반 실행 중 상태 하나로 단순화하면 이 계약을 놓칩니다.',
  ('disable 마지막에 DISABLE 비트를 지우면 즉시 활성인가요?',
   '아닙니다. SCHED와 NPSVC가 비활성 상태를 유지합니다.',
   '그렇습니다. DISABLE 하나만 보면 전체 상태를 알 수 있습니다.',
   '여러 비트의 조합으로 소유권과 제어 상태를 나타내므로 단일 비트 이름만으로 판단할 수 없습니다.'),
  ('enable 없이 disable을 연속 두 번 해도 안전한가요?',
   '아닙니다. 문서는 교착 가능성을 명시합니다.',
   '그렇습니다. 이미 꺼져 있으면 항상 즉시 반환합니다.',
   '제어 API는 멱등이 아니며 첫 호출이 남긴 소유권 비트 때문에 두 번째 호출이 기다릴 수 있습니다.')),
 ('NET_RX의 전역 예산: poll 뒤 검사하는 한도와 목록 공정성',
  'net_rx_action',
  '각 장치의 한 번 처리량만 제한해도 많은 장치가 차례로 처리되면 softirq가 CPU를 오래 점유할 수 있습니다. 전체 실행에 작업량과 시간 한도를 두고 남은 작업을 다음 실행으로 넘기는 조정이 필요합니다.',
  'net_rx_action은 CPU의 softnet_data에서 poll 목록을 로컬 list로 옮깁니다. 처음 설정한 budget에서 각 napi_poll의 실제 work를 빼고,0 이하이거나 현재 jiffies가 time_limit 이상이면 '
  'time_squeeze를 늘리고 멈춥니다. 한도는 netdev_budget와 netdev_budget_usecs를 READ_ONCE로 읽으며 시간은 usecs_to_jiffies로 변환합니다.',
  '설명용 전체 budget100,각 NAPI weight64에서 두 poll이64씩 처리하면100→36→-28입니다. 검사가 poll 호출 뒤여서 총128을 처리하고 멈출 수 있습니다. 남은 전체 예산36을 자동으로 다음 드라이버 예산36으로 '
  '전달하는 구조가 아닙니다. 주석의2jiffies 표현만 읽기보다 현재 본문의 설정값 기반 시간 계산을 확인해야 합니다.',
  '목록 연결과 새 요청을 놓치지 않는 종료',
  '한도 종료 시 미처리 로컬 list 뒤에 새로 예약된 sd->poll_list를 붙이고 그 뒤에 repoll을 붙여 다시 CPU 목록에 둡니다. 남았으면 NET_RX_SOFTIRQ를 다시 올리고 없으면 in_net_rx_action을 '
  '내립니다. 로컬과 repoll이 모두 비면 먼저 실행 표시를 내리고 barrier 뒤 새 poll_list를 다시 확인해 필요하면 start로 돌아갑니다. 이 재시작은 처음의 budget/time_limit을 다시 초기화하지 않습니다. '
  'deferred skb 정리를 루프에서 수행하고 RPS 대기 처리·BPF 네트워크 문맥 해제도 종료 경로에 연결됩니다.',
  ('전체 예산100에서 두 poll이64씩 처리할 수 있나요?',
   '그렇습니다. 검사 시점이 각 poll 뒤이므로128 뒤에 멈출 수 있습니다.',
   '아닙니다. 항상 정확히100개에서 드라이버 내부를 중단시킵니다.',
   '전체 예산과 개별 weight는 다른 값이며 napi_poll에 남은36을 인자로 전달하지 않습니다.'),
  ('start로 재진입하면 시간 한도를 새로 연장하나요?',
   '아닙니다. 초기화는 start label 앞에서 한 번입니다.',
   '그렇습니다. 새 요청마다 한도를 무한히 초기화합니다.',
   'goto 대상과 변수 초기화 위치를 구분하면 계속 새 요청이 와도 같은 실행 한도를 유지하는 이유가 보입니다.'))]

def register(topic,q,detail):
    for title,symbol,why,principle,use,dt,body,qa,qb in ROWS:
        topic(title,'네트워크','net/core/dev.c',symbol,why,principle,use,
              'state 비트의 이전/다음 값,반환값,목록 연결과 드라이버 책임을 나누어 추적하세요.',
              q(title+' · '+qa[0],*qa[1:]),q(title+' · '+qb[0],*qb[1:]),
              details=[detail(dt,body),detail('검토 범위','고정 Linux v6.12 net/core/dev.c의 NAPI 예약·완료·poll·enable/disable과 Documentation/networking/napi.rst의 호출 계약을 대조했습니다. 전체 dev.c 해설 완료나 실제 NIC·IRQ·패킷 부하 실험을 주장하지 않습니다.')])
