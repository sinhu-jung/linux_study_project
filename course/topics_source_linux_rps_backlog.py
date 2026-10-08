"""Receive CPU selection, ordering, bounded queues and flow pressure."""
ROWS = [
('RPS와 RFS의 CPU 선택: 해시 분산과 흐름 순서 보존','get_rps_cpu',
 '한 수신 큐가 받은 패킷을 여러 CPU에 나누면 처리 부하를 분산할 수 있습니다. 그러나 같은 흐름을 갑자기 다른 CPU로 옮기면 이전 CPU에 남은 패킷보다 새 패킷이 먼저 처리될 수 있어 CPU 선택과 순서 보존을 함께 설계해야 합니다.',
 'get_rps_cpu는 RCU 읽기 잠금을 호출자에게 요구합니다. 기록된 수신 큐 번호를 검사하고 그 큐의 flow table과 CPU map이 모두 없으면 해시 계산 없이 -1입니다. 해시가0이어도 -1입니다. 전역 socket flow table과 큐별 table이 있으면 ident와 hash의 CPU 비트 외 부분을 비교해 일치 여부를 확인하고 원하는 CPU를 뽑습니다.',
 '현재 흐름 CPU와 원하는 CPU가 다를 때 현재 CPU가 미설정·offline이거나 input_queue_head가 last_qtail에 도달한 경우에만 전환합니다. 예를 들어 같은 카운터 구간에서 마지막 꼬리120,처리 머리118이면 기존 CPU를 유지하고120이면 전환할 수 있습니다. 계산은 실제 코드에서 차이를 int로 해석하므로 임의 큰 숫자 비교로 바꾸지 말고 큐 카운터 계약을 따라야 합니다.',
 'RFS가 선택하지 못하면 일반 RPS로 돌아가기',
 '일치한 흐름의 CPU가 유효하고 online이면 rflowp에 흐름 항목을 돌려줍니다. 그렇지 못하면 map이 있을 때 reciprocal_scale(hash,map->len)으로 CPU 배열 인덱스를 선택하고 online일 때만 반환합니다. offline 후보를 만났다고 모든 CPU를 차례로 검색하는 루프는 없습니다. set_rps_cpu는 새 CPU의 queue head를 last_qtail 기준으로 저장하고 cpu를 게시합니다. RFS_ACCEL 설정의 하드웨어 큐 유도는 별도 조건과 callback 성공 여부를 거쳐 흐름 항목을 바꿀 수 있으며,이 수업은 소프트웨어 선택과 순서 판단 범위를 설명합니다.',
 ('이전 CPU의 마지막 꼬리120,머리118이면 바로 옮기나요?','다른 전환 사유가 없으면 아직 기존 CPU를 유지합니다.','그렇습니다. 원하는 CPU가 바뀌면 무조건 즉시 이동합니다.','이전 흐름 패킷이 큐에서 모두 빠졌는지 확인하는 조건이 순서 뒤바뀜을 줄입니다.'),
 ('CPU map이 고른 후보가 offline이면 다른 후보를 전부 순회하나요?','아닙니다. 이 본문에는 그런 탐색 루프가 없습니다.','그렇습니다. online CPU를 찾을 때까지 자동 순환합니다.','일반 RPS 분기는 한 후보의 online 검사 후 선택하지 못하면 초기 실패값으로 끝날 수 있습니다.')),
('CPU backlog 등록: 잠금 전 관찰과 잠금 뒤 재검사','enqueue_to_backlog',
 '원격 CPU의 패킷 큐에 여러 송신자가 동시에 추가할 수 있으므로 길이를 보고 괜찮다고 판단한 순간과 실제 삽입 순간의 상태가 다를 수 있습니다. 빠른 거절용 관찰과 잠금 아래 최종 판정을 분리해야 합니다.',
 'enqueue_to_backlog는 장치가 running이 아니면 DEV_READY 이유로 폐기합니다. 대상 CPU 큐 길이를 lockless로 읽어 max_backlog 초과면 거절합니다. 그 외에는 backlog 잠금을 잡아 길이를 다시 읽고 qlen<=max_backlog이며 flow limit에 걸리지 않을 때 추가합니다. 빈 큐이면 SCHED 비트를 검사·설정해 backlog 처리를 예약하고 skb를 꼬리에 넣어 queue tail을 증가시킵니다.',
 'max_backlog100이고 잠금 안 길이가100이면 조건이 <=이므로 한 개를 더 넣어101이 될 수 있습니다. 길이가101이면 거절됩니다. 반환 SUCCESS는 큐 등록 성공이며 프로토콜 처리나 애플리케이션 전달 완료가 아닙니다. 실패는 skb를 kfree_skb_reason으로 해제하므로 호출자가 같은 패킷을 다시 자유롭게 사용하면 안 됩니다.',
 '통계와 원격 예약의 위치',
 'CPU backlog 실패는 대상 sd->dropped와 장치 rx_dropped를 올립니다. 장치가 running이 아닌 첫 거절은 대상 sd를 아직 정하지 않아 장치 통계만 올립니다. 성공한 tail 값은 잠금을 푼 뒤 qtail에 저장합니다. napi_schedule_rps는 자기 CPU이면 로컬 backlog를 예약하고 원격이면 backlog thread 경로 또는 송신 CPU의 rps_ipi_list에 연결하는 경로를 택합니다. 원격 등록 자체가 그 자리에서 원격 패킷 처리를 완료한다는 뜻은 아닙니다.',
 ('한도가100이고 잠금 안 길이가100이면 새 패킷은?','flow limit 등 다른 조건이 통과하면101개로 늘 수 있습니다.','반드시 거절됩니다. 비교는 < 입니다.','코드는 <=을 사용하므로 정책 수치와 실제 비교 경계를 구체적으로 읽어야 합니다.'),
 ('NET_RX_SUCCESS가 애플리케이션 수신 완료인가요?','아닙니다. backlog 등록이 성공했다는 뜻입니다.','그렇습니다. 모든 네트워크 계층 처리가 끝났습니다.','큐 삽입과 나중 NAPI 소비가 다른 단계이므로 반환 결과의 범위를 제한해서 해석해야 합니다.')),
('Flow limit: 최근 해시 버킷 기록으로 한 흐름의 독점 줄이기','skb_flow_limit',
 '큐가 붐빌 때 특정 흐름이 최근 패킷의 대부분을 차지하면 다른 흐름의 패킷도 함께 밀릴 수 있습니다. 최근 흐름 분포를 작은 이력 배열로 근사해 한 버킷이 과도하게 차지하는 경우를 제한합니다.',
 'CONFIG_NET_FLOW_LIMIT에서 qlen이 max_backlog의 절반보다 작으면 즉시 false입니다. 그 외 현재 CPU의 flow_limit을 RCU로 읽습니다. 있으면 hash&(num_buckets-1)로 새 버킷을 정하고 순환 이력의 옛 버킷을 새 값으로 교체합니다. history_head를 증가시킨 뒤 마스크로 순환시키며 옛 버킷 계수가 양수일 때1을 빼고 새 버킷에1을 더합니다.',
 '설명용 이력 길이H=8이면 새 버킷 계수가4일 때는 통과하고5가 되면 H/2 초과라 true입니다. true일 때 fl->count도 증가합니다. 옛 버킷과 새 버킷이 같고 계수가 양수이면 빼고 더해 같은 값이 됩니다. 실제 이력 길이는 FLOW_LIMIT_HISTORY 상수이며 H=8은 계산용 예입니다.',
 '근사 집계와 호출 CPU를 구분하기',
 '버킷 충돌 때문에 이 계수는 고유한 연결마다 완전히 독립된 정확한 카운터가 아닙니다. flow_limit 객체가 없거나 설정이 꺼지면 false입니다. 이 함수는 this_cpu_ptr를 쓰므로 enqueue_to_backlog의 대상 sd와 무조건 같은 CPU라고 생각하면 안 됩니다. true 반환은 제한 판정이며 실제 패킷 해제는 호출자의 실패 경로가 담당합니다. 이미 기록한 이력은 이번 패킷을 거절하더라도 이전 상태로 rollback하지 않습니다.',
 ('설명용 H8에서 새 버킷 계수4이면 제한하나요?','아닙니다.5처럼 절반을 초과해야 합니다.','그렇습니다. 절반 이상이면 항상 제한합니다.','조건은 > 이므로 정확한 절반과 그 초과를 나누어 계산해야 합니다.'),
 ('버킷 계수가 정확히 고유 연결 한 개의 개수인가요?','항상 그렇지는 않습니다. 해시 충돌로 공유할 수 있습니다.','그렇습니다. 해시 마스크는 충돌을 완전히 없앱니다.','제한된 버킷 수로 최근 분포를 근사하는 자료구조이므로 정확한 연결별 집계와 구분합니다.')),
]

def register(topic,q,detail):
    for title,symbol,why,principle,use,dt,body,qa,qb in ROWS:
        topic(title,'네트워크','net/core/dev.c',symbol,why,principle,use,
              '처리 CPU와 등록 CPU,큐의 머리/꼬리,잠금과 반환값의 범위를 나누어 읽으세요.',
              q(title+' · '+qa[0],*qa[1:]),q(title+' · '+qb[0],*qb[1:]),
              details=[detail(dt,body),detail('검토 범위','Linux v6.12 net/core/dev.c의 get_rps_cpu·set_rps_cpu 연결·napi_schedule_rps·enqueue_to_backlog·skb_flow_limit 본문을 대조했습니다. 전체 파일 해설 완료나 실제 CPU migration·NIC·패킷 부하 시험은 아닙니다.')])
