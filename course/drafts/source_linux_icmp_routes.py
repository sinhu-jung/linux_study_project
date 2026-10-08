"""ICMP reply routing, XFRM relookup and NAT quotation ownership."""
ROWS = [
('ICMP Reply 경로: 요청 출발지로 돌아가는 주소와 옵션 만들기', 'icmp_reply',
 '응답은 단순히 받은 IP 헤더의 두 주소만 바꾸어 보내는 것으로 끝나지 않습니다. namespace·보안 분류·mark·source route 옵션과 어느 L3 영역의 route를 찾을지 함께 고려해야 올바른 출력 경로를 선택할 수 있습니다.',
 'icmp_reply는 ip_options_echo 실패면 종료하고 BH를 끈 뒤 전역 제한과 CPU 소켓을 획득합니다. checksum을0으로 초기화하고 요청 tos와 reply mark를 설정합니다. 기본 목적지는 원본 출발지이며 출발지는 fib_compute_spec_dst 결과입니다. source route 옵션이 있으면 route 조회 목적지는 옵션의 faddr로 바뀝니다. flow를0으로 초기화하고 주소·mark·uid·DSCP·ICMP protocol·L3 master oif를 채웁니다.',
 '요청의 출발지 A,목적지 B라고 해서 이 함수가 무조건 saddr=B를 대입하는 것은 아닙니다. saddr helper의 결과와 route 결정을 사용합니다. 옵션이 없는 일반 경우 route 목적지는 A지만 source route가 있으면 옵션의 다음 경유 주소로 조회할 수 있습니다. security_skb_classify_flow 후 route를 얻고 목적지 제한을 통과해야 push_reply를 호출합니다.',
 '오류 송신의 추가 주소 정책',
 '__icmp_send는 별도로 로컬 목적지이면 원본 daddr를 saddr 후보로 사용합니다. 그렇지 않으면 설정에 따라 입력 인터페이스 주소를 선택하거나0으로 둡니다. 오류 type의 tos에는 INTERNETCONTROL 우선순위를 조합합니다. route 조회 후에도 fl4.saddr가0이면 INADDR_DUMMY로 대체합니다. 입력 loopback일 때 전역 제한 호출을 건너뛰면 초기 apply_ratelimit=false가 유지되므로 실제 목적지 제한 함수도 조기 통과합니다. 근처 주석만 보고 peer 제한이 반드시 작동한다고 설명하면 코드의 조건과 어긋납니다.',
 ('일반 reply의 saddr는 항상 원본 목적지 주소를 그대로 복사하나요?', '아닙니다.fib_compute_spec_dst 결과를 사용합니다.', '그렇습니다.어떤 route나 옵션도 관여하지 않습니다.', '응답 주소 선택과 route 조회는 원본 헤더 단순 교환보다 복잡합니다.'),
 ('입력 loopback이라 전역 검사 호출을 생략하면 apply_ratelimit은?', '초기 false가 유지되어 목적지 제한도 조기 통과합니다.', '자동으로 true가 되어 peer 제한이 반드시 실행됩니다.', '호출을 건너뛰면 값을 설정하는 부수 효과도 발생하지 않습니다.')),
('ICMP XFRM Route 재조회: 처음 찾은 Route와 역방향 정책의 선택', 'icmp_route_lookup',
 '보안 변환이 적용된 패킷에 대한 오류 응답은 일반 출력 route뿐 아니라 원본 세션의 역방향 정책도 고려할 수 있습니다. 첫 route 조회 실패와 보안 정책의 EPERM,재조회 실패를 모두 같은 결과로 처리하면 원래 가능한 경로를 잃을 수 있습니다.',
 'icmp_route_lookup은 source route 옵션 또는 원본 saddr를 목적지로 하고 saddr·mark·uid·DSCP·type·code·L3 master oif를 채워 route를 얻습니다. 첫 xfrm_lookup이 다른 route를 성공 반환하면 바로 사용합니다. 동일 route이면 역방향 session을 decode합니다. 첫 XFRM 오류가 EPERM이면 rt를 NULL로 두고 재조회하며,다른 오류는 즉시 반환합니다.',
 '역방향 decode의 saddr가 로컬이면 __ip_route_output_key를 사용합니다. 로컬이 아니면 그 주소로 출력 route를 구해 장치를 정한 뒤 ip_route_input을 호출합니다. 이때 skb의 기존 _skb_refdst를 저장하고 잠시 NULL로 바꾸며 새 입력 route를 얻은 뒤 기존 값을 복원합니다. 패킷의 원래 route와 재조회용 route를 구분하기 위한 임시 상태 변경입니다.',
 '두 번째 XFRM과 실패 시 선택',
 '두 번째 xfrm_lookup은 XFRM_LOOKUP_ICMP를 사용합니다. 성공하면 기존 route를 놓고 역방향 flow를 fl4로 복사해 새 route를 선택합니다. 두 번째 EPERM은 기존 route가 있으면 놓고 오류를 반환합니다. 다른 재조회 실패는 기존 rt가 남아 있으면 그것을 반환하고,없으면 err의 오류 포인터를 반환합니다. lookup 장치 선택은 skb->dev 우선,없으면 skb_dst의 dev입니다. 이 호출부의 참조 인계는 XFRM helper 계약을 따라야 하며 모든 실패에서 같은 포인터를 무조건 두 번 해제하면 안 됩니다.',
 ('재조회가 실패해도 기존 rt가 남아 있으면 어떻게 하나요?', 'relookup_failed는 기존 rt를 반환할 수 있습니다.', '항상 기존 rt까지 버리고 같은 오류를 반환합니다.', 'fallback 가능 여부는 첫 조회에서 유효 route가 남았는지에 달려 있습니다.'),
 ('두 번째 XFRM 성공 때 route만 바꾸고 flow는 그대로 두나요?', '아닙니다.역방향 fl4_dec도 fl4로 복사합니다.', '그렇습니다.route와 flow는 서로 무관합니다.', '선택한 보안 경로와 그에 맞는 flow 정보를 함께 갱신합니다.')),
('ICMP NAT 인용 복구: 주소를 잠시 바꿨다가 반드시 되돌리기', 'icmp_ndo_send',
 '송신 장치에서 오류를 만들 때 패킷의 출발지 주소가 이미 NAT로 바뀌었을 수 있습니다. 오류에 포함할 원본 관점을 맞추려면 conntrack의 원래 주소를 사용하되 다른 사용자가 보는 skb를 함부로 영구 변경하지 않아야 합니다.',
 'CONFIG_NF_NAT의 icmp_ndo_send는 conntrack이 없거나 SRC_NAT 상태가 아니면 바로 __icmp_send를 호출합니다. NAT 대상 skb가 공유되면 GFP_ATOMIC으로 clone합니다. skb 존재·네트워크 헤더 범위·헤더까지 writable 확보를 검사하고 실패하면 정리합니다. 원래 saddr를 저장하고 conntrack 원래 방향 tuple의 출발지로 바꿔 __icmp_send를 호출한 뒤 저장값으로 복원합니다.',
 'NAT 후 출발지 B가 담긴 skb에서 원래 주소 A를 잠시 사용해 ICMP 오류를 구성하고,함수 종료 전 다시 B로 돌립니다. clone은 모든 패킷 데이터를 무조건 깊게 복사한다는 뜻이 아니므로 skb_ensure_writable 검사도 필요합니다. 원본이 공유되지 않았다면 원본 skb를 잠시 변경하되 주소 복원은 동일하게 수행합니다.',
 '누가 어떤 SKB를 소비하는가',
 'cloned_skb는 clone을 만든 경우에만 비NULL이고 끝에서 consume_skb에 넘깁니다. 원본 skb를 이 함수가 무조건 소비하는 구조가 아닙니다. 빈 ip_options를 준비해 호출하며 주소를 바꾸는 이 wrapper 자체에는 원본 IP checksum을 다시 계산하는 대입이 없습니다. 이를 NAT 패킷 자체를 새 주소로 영구 재송신하는 기능이라고 설명하지 않습니다. 실제 NAT·conntrack tuple 유지 전체는 별도 구현입니다.',
 ('공유 skb를 clone하면 writable 검사를 생략해도 되나요?', '아닙니다.clone 뒤에도 writable 확보를 검사합니다.', '그렇습니다.clone은 언제나 모든 데이터를 독립 복사합니다.', 'skb 객체 복제와 데이터 버퍼 쓰기 가능성은 서로 다른 문제입니다.'),
 ('이 함수는 원본 skb를 항상 consume하나요?', '아닙니다.마지막에는 따로 만든 cloned_skb만 소비합니다.', '그렇습니다.입력 skb는 공유 여부와 무관하게 무조건 해제합니다.', '별도 clone 포인터를 추적해 자신이 획득한 객체의 소유권을 정리합니다.')),
]

def register(topic,q,detail):
    for title,symbol,why,principle,use,dt,body,qa,qb in ROWS:
        topic(title,'네트워크','net/ipv4/icmp.c',symbol,why,principle,use,
              '원본 route·재조회 route·flow·skb 임시 변경·clone 소유권을 각각 따라가세요.',
              q(title+' · '+qa[0],*qa[1:]),q(title+' · '+qb[0],*qb[1:]),
              details=[detail(dt,body),detail('검토 범위','Linux v6.12 icmp.c의 reply·route lookup·오류 송신 주소 정책·NAT wrapper를 대조했습니다. XFRM·FIB·conntrack 전체와 실제 route/NAT 정책 실험은 별도 범위입니다.')])
