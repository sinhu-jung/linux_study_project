"""Networking interfaces beyond the original TCP/IP introduction."""
def register(topic,q,detail):
    topic('Netlink·TLV 메시지와 Dump','네트워크','net/netlink/af_netlink.c','netlink_sendmsg',
      '사용자 도구가 커널의 장치·라우팅·정책 상태를 구조화된 메시지로 조회하고 설정할 통로가 필요합니다.',
      'Netlink는 nlmsghdr와 attribute TLV로 요청·응답을 표현합니다. Sequence·portid로 통신을 구분하고 multipart dump의 끝과 오류를 처리합니다. 비동기 multicast event와 요청 응답은 역할이 다르며 dump 도중 상태 변경·손실·재시도를 고려해야 합니다.',
      '기존 ip·ss·ethtool 등 도구부터 관찰하고 직접 구현할 때 header·attribute 길이·alignment·nested policy를 검증합니다. Portid를 언제나 프로세스 PID라고 가정하지 않고 ACK·NLMSG_ERROR·DONE을 처리합니다.',
      'netlink_sendmsg의 dst_portid·dst_group·SCM 자격과 netlink dump를 읽으세요.',
      q('Netlink attribute 길이를 확인하지 않고 payload struct를 읽어도 되는가?','TLV 길이·정렬·정책을 검증한다','같은 커널이므로 모든 메시지 길이는 안전하다','메시지는 입력 경계입니다. 선언한 길이와 buffer 범위·필수 attribute·nested 정책을 확인해야 합니다.'),
      q('Netlink dump 결과를 메시지 하나만 받고 항상 완전한 목록이라고 판단하는가?','multipart 끝·오류·중단 상태를 확인한다','첫 메시지는 항상 전체 목록이다','Dump는 여러 메시지와 DONE 등으로 끝날 수 있습니다. 변경 중 일관성·중단·이벤트 손실과 재조회도 고려합니다.'),
      details=[detail('TLV와 확장','Type·length·value를 가진 attribute는 필드를 추가할 수 있게 합니다. 알 수 없는 값과 지원 정책을 맞춰 처리하되 길이 검사는 생략하지 않습니다.'),detail('통지 손실','Multicast 수신 buffer가 넘치면 event를 놓칠 수 있습니다. 상태를 복구할 snapshot 재조회와 오류 처리가 필요하며 모든 변경이 영구 event log로 전달된다고 가정하지 않습니다.')])

    topic('SCTP·Association과 다중 Stream','네트워크','net/sctp/socket.c','sctp_sendmsg',
      '메시지 경계를 유지하며 여러 stream과 경로를 하나의 통신 관계 안에서 관리할 수 있어야 합니다.',
      'SCTP association은 여러 transport 주소와 stream을 관리합니다. TSN은 전송 데이터 신뢰성을, stream의 순서는 해당 메시지 전달 규약을 추적합니다. Multihoming과 multistreaming은 다른 기능이며 socket 스타일·ordered·unordered·확장에 따라 동작이 달라집니다.',
      '지원 SCTP socket의 association·stream 선택 ancillary data와 notification을 사용합니다. Message 길이·partial delivery·재전송·경로 failover·지원 확장을 확인하고 TCP byte stream과 같은 framing이라고 가정하지 않습니다.',
      'sctp_sendmsg의 endpoint·association·sctp_transport·sndrcvinfo·parse를 읽으세요.',
      q('SCTP multistreaming과 multihoming은 같은 기능인가?','메시지 stream 분리와 여러 경로 주소를 구분한다','둘 다 항상 같은 숫자다','Stream은 전달 순서 영역이고 transport 주소는 경로·장애 대응과 관계됩니다. 별도 자료구조와 정책입니다.'),
      q('SCTP 메시지 통신은 TCP와 같은 경계 없는 byte stream인가?','메시지 경계와 전달 규약을 제공한다','항상 write 경계가 모두 사라진다','SCTP는 message-oriented입니다. Partial delivery와 socket API를 포함해 메시지 경계를 처리해야 합니다.'),
      details=[detail('TSN과 Stream 번호','Association 전체의 전송 확인과 stream별 ordered delivery를 따로 관리합니다. 한 번호를 모든 순서에 쓰는 TCP 모형으로만 설명하면 다중 stream 의미를 놓칩니다.'),detail('Chunk와 Fragment','큰 메시지는 DATA chunk 등으로 나뉠 수 있습니다. 전달 완료·부분 읽기·EOR 등의 규약을 따라 재조립된 메시지 의미를 보존합니다.')])

    topic('DCCP·신뢰성 없는 혼잡 제어','네트워크','net/dccp/proto.c','dccp_sendmsg',
      '손실 데이터의 재전송보다 최신 데이터의 적시 전달이 중요해도 네트워크 혼잡 대응은 필요합니다.',
      'DCCP는 연결·sequence·ACK·혼잡 제어를 제공하지만 애플리케이션 데이터의 TCP 같은 신뢰 재전송을 제공하지 않습니다. CCID가 혼잡 제어 방식을 정하고 packet 크기·전송 가능 시점·feature negotiation을 관리합니다.',
      '지원 DCCP 환경에서 socket 연결과 CCID·MSS·전송 오류를 확인합니다. 손실·메시지 수명은 앱 요구에 맞게 처리하며 ACK 존재만으로 모든 데이터가 재전송된다고 가정하지 않습니다.',
      'dccp_sendmsg의 mss_cache·EMSGSIZE·송신 queue와 CCID 경로를 읽으세요.',
      q('DCCP에 ACK가 있으면 손실 payload를 TCP처럼 반드시 재전송하는가?','혼잡 피드백과 신뢰 재전송은 별도다','모든 ACK 프로토콜은 항상 TCP와 같다','DCCP의 ACK는 연결·혼잡 등에 활용되지만 신뢰 데이터 전달의 같은 계약을 제공하지 않습니다.'),
      q('DCCP payload 길이가 cached MSS를 넘으면 이 진입 경로는?','-EMSGSIZE','무조건 성공으로 길이를 버린다','dccp_sendmsg의 길이 검사가 과도한 메시지를 거부합니다. 단순히 socket에 쓸 수 있다는 사실만으로 크기 제한이 사라지지 않습니다.'),
      details=[detail('CCID','Congestion control identifier는 선택된 피드백·전송률 정책을 연결합니다. 신뢰성 여부와 혼잡 제어의 목표를 따로 봅니다.'),detail('대기와 최신성','혼잡으로 queue에 오래 남은 data가 앱에는 이미 가치가 없을 수 있습니다. 전송 deadline·손실 처리와 적합한 protocol 선택은 상위 요구에 따릅니다.')])

    topic('CAN·식별자 중재와 SocketCAN','네트워크','net/can/af_can.c','can_send',
      '임베디드 bus의 broadcast frame을 여러 앱이 filter로 받으려면 TCP/IP와 다른 주소·중재 규약을 알아야 합니다.',
      'CAN은 frame identifier로 우선순위 중재와 내용 종류를 표현합니다. 동일 형식의 중재에서 dominant bit가 우선하며 숫자가 작은 identifier가 우선할 수 있습니다. SocketCAN은 network device와 PF_CAN protocol을 연결하고 classic·FD·XL frame 형식과 loopback을 구분합니다.',
      '학습용 vcan으로 PF_CAN RAW·filter·send/recv를 관찰합니다. 실제 CAN의 bitrate·termination·bus-off 조건과 다르므로 vcan 성공을 물리 bus 검증으로 세지 않습니다. Frame 크기와 can_id flags를 확인합니다.',
      'can_send의 CAN·CANFD·CANXL frame 검사와 protocol·loopback 처리를 읽으세요.',
      q('CAN identifier가 언제나 특정 대상 장치의 IP 주소와 같은가?','broadcast 내용·중재 식별자로 해석한다','항상 목적지 IP와 같다','CAN의 통신 모델은 IP unicast와 다릅니다. 여러 수신자가 같은 ID filter로 같은 frame을 받을 수 있습니다.'),
      q('Vcan에서 송수신 성공하면 실제 bus의 bitrate·termination까지 검증됐는가?','가상 경로와 물리 조건은 별도다','모든 전기 신호까지 자동 검증된다','Vcan은 socket·software 경로 학습에 적합합니다. 실제 bus의 신호·controller·error 상태 검증은 별도입니다.'),
      details=[detail('Filter 비트','can_id에는 extended·RTR·error 등의 flags가 들어갈 수 있습니다. ID 숫자와 flags mask를 구분해 filter를 구성해야 원치 않는 frame을 선택하지 않습니다.'),detail('Loopback','송신한 frame을 로컬 다른 socket도 관찰하는 규약이 있습니다. Bus에서 실제 다른 노드가 받았다는 확인과 local echo를 동일시하지 않습니다.')])

    topic('MPLS·Label Switching','네트워크','net/mpls/af_mpls.c','mpls_forward',
      '패킷을 주소 전체 대신 label로 전달할 때 label stack·다음 hop·수명 제한을 관리해야 합니다.',
      'MPLS shim은 20bit label·traffic class·bottom-of-stack·TTL을 담습니다. Forwarding은 들어온 label의 table에서 경로를 찾고 label을 push·swap·pop하며 다음 장치로 보냅니다. Label의 의미는 해당 forwarding domain의 규약이며 IP 주소와 같은 전역 값이 아닙니다.',
      '지원 kernel과 MPLS routing 설정을 확인하고 network namespace 실습에서 label path를 구성합니다. MTU·TTL·stack 끝·IPv4/IPv6 decapsulation을 구분합니다.',
      'mpls_forward의 shim decode·route lookup·TTL·new_header_size를 읽으세요.',
      q('MPLS label 20bit의 이론적 값 범위 크기는?','2^20개','20개','20개의 binary bit는 2^20 조합을 표현합니다. 일부 label은 예약 의미가 있어 모든 값을 같은 용도로 사용할 수 없습니다.'),
      q('Label stack의 bottom 표시가 필요한 이유는?','마지막 label과 그 뒤 payload 해석을 구분한다','항상 TCP 연결을 종료한다','여러 label 뒤 어떤 payload가 이어지는지 해석하려면 stack 끝을 알아야 합니다. Packet buffer 길이도 함께 검증합니다.'),
      details=[detail('TTL','루프나 과도한 전달을 막기 위해 hop에서 TTL을 처리합니다. Label 제거 후 inner IP TTL과의 연결은 규약에 따릅니다. Header 하나를 없애도 수명 제한이 사라지지 않습니다.'),detail('MTU 계산','Label 하나가 4byte 추가되므로 label stack 깊이가 늘면 frame 길이도 늘 수 있습니다. Link MTU와 재전송·fragment 경로를 확인합니다.')])

    topic('L2TP·터널과 세션','네트워크','net/l2tp/l2tp_core.c','l2tp_xmit_skb',
      '하나의 tunnel 안에 여러 링크 계층 세션을 전달할 때 식별자·encapsulation·수명을 분리해야 합니다.',
      'L2TP는 tunnel과 session ID로 encapsulated payload를 구분합니다. 버전별 header·UDP/IP transport·sequence·cookie 규약이 다르고 세션은 PPP 등 payload와 연결될 수 있습니다. 터널링 자체는 암호화나 인증을 항상 제공하는 성질이 아닙니다.',
      '지원 버전·peer ID·session·transport를 일치시키고 MTU·sequence·close·오류를 처리합니다. 비밀성이 필요하면 검토된 IPsec 등 전체 보안 구성을 사용합니다.',
      'l2tp_xmit_skb의 session·tunnel 통계와 l2tp_xmit_core header 구성을 읽으세요.',
      q('L2TP tunnel 하나에 여러 session을 두는 이유는?','각 payload 흐름을 session ID로 구분한다','모든 session이 같은 메모리 객체이기 때문','Tunnel의 통신 경계와 안의 여러 session을 구분합니다. 식별자와 참조 수명도 별도로 관리합니다.'),
      q('L2TP encapsulation만 있으면 payload가 항상 암호화되는가?','터널과 비밀성·인증은 별도다','Header가 추가되면 자동으로 암호화된다','Encapsulation은 전달 형식입니다. 안전한 전송 요구는 적합한 인증·암호 규약과 함께 설계해야 합니다.'),
      details=[detail('ID의 범위','로컬·원격 tunnel/session 식별자를 맞춰야 수신자가 올바른 context를 찾습니다. 같은 정수 하나가 양 방향에서 같은 의미라고 가정하지 않습니다.'),detail('통계와 성공','NET_XMIT_SUCCESS에 따라 packet·byte 통계가 증가하고 오류 통계가 나뉩니다. 로컬 제출 성공을 peer가 최종 payload를 처리한 확인과 동일시하지 않습니다.')])

    topic('Open vSwitch·Flow Cache와 Upcall','네트워크','net/openvswitch/datapath.c','ovs_dp_process_packet',
      '다양한 가상 switch 정책을 모든 packet마다 사용자 프로세스에서 계산하지 않고 빠른 경로로 처리할 수 있어야 합니다.',
      'Kernel OVS datapath는 flow key·mask로 cache된 action을 찾습니다. Miss면 사용자 control plane으로 upcall하고 policy 결과를 flow로 설치할 수 있습니다. Kernel flow cache와 사용자 OpenFlow policy는 서로 다른 표현이며 action 실행·port·통계를 관리합니다.',
      'ovs-vsctl·ovs-ofctl 등 환경의 control 도구와 datapath flow 조회를 구분합니다. Miss·cache hit·mask·upcall 손실·MTU를 관찰하고 control plane 실패를 고려합니다.',
      'ovs_dp_process_packet의 flow lookup·mask/cache hit·upcall·execute actions를 읽으세요.',
      q('Kernel flow cache에 없는 packet은 무조건 보통 IP route만 따라가는가?','upcall과 control plane 정책 경로를 확인한다','어떤 OVS miss도 자동으로 TCP 재전송한다','OVS datapath의 miss는 사용자 공간 통지 등 자체 경로를 가집니다. Control plane이 policy와 flow 설치를 관리합니다.'),
      q('OpenFlow 규칙 한 개와 kernel datapath flow 한 개가 항상 일대일인가?','정책 표현과 cache된 처리 flow를 구분한다','모든 mask·wildcard가 같은 객체다','사용자 정책에서 여러 실제 key·mask cache가 나올 수 있습니다. 서로 다른 계층의 통계와 규칙 수를 비교해야 합니다.'),
      details=[detail('Key와 Mask','입력 port·header field 등의 key에서 mask가 의미 있는 bit를 선택합니다. Hash 후보와 실제 masked match를 확인해야 action을 정확히 선택합니다.'),detail('Upcall 비용','Miss마다 사용자↔kernel 전달·policy 계산이 필요해 최초 packet의 비용과 hit 경로가 다릅니다. Cache 크기·갱신·control plane 상태를 함께 측정합니다.')])

    topic('TLS Offload·Record와 커널 경계','네트워크','net/tls/tls_main.c','tls_setsockopt',
      'TLS의 handshake와 record 암호 처리·socket 데이터 경로를 분리하면 어느 부분을 kernel이 맡는지 이해할 수 있습니다.',
      'Kernel TLS는 협상 뒤 제공받은 crypto state로 TLS record의 송수신 처리 일부를 담당합니다. 사용자 handshake·인증서 신뢰·key update 관리와 kernel record offload는 같은 기능이 아닙니다. Software·hardware offload·TX/RX 지원과 cipher 조건을 확인해야 합니다.',
      '지원 TLS library와 kernel의 kTLS 연결을 사용하고 protocol·cipher·방향·record sequence·오류를 처리합니다. Offload 성공만으로 peer 인증과 handshake가 자동 완료됐다고 판단하지 않습니다.',
      'tls_setsockopt의 SOL_TLS 분기와 do_tls_setsockopt, TLS_TX·TLS_RX state 준비를 읽으세요.',
      q('kTLS crypto state를 설정하면 인증서 검증과 handshake도 이 함수가 모두 수행하는가?','record offload와 사용자 handshake 경계를 구분한다','setsockopt 하나가 모든 인증을 완료한다','협상·peer 신뢰와 record 처리 state 설정은 별도입니다. 실제 library가 관리하는 전체 TLS 규약을 따라야 합니다.'),
      q('TX offload 지원이 있으면 RX도 어떤 cipher든 자동 지원되는가?','방향·cipher·device별 지원을 확인한다','한 방향 지원이면 모든 기능이 같다','지원 조합과 fallback·오류 경로가 다릅니다. Kernel TLS라는 이름만으로 모든 방향을 같다고 가정하지 않습니다.'),
      details=[detail('Record state','Key·IV·salt·sequence 등의 crypto info가 record 규약에 맞아야 합니다. Kernel에 넣은 key state와 이후 key update의 시점을 맞추지 않으면 통신 의미가 깨집니다.'),detail('Offload 비용','Software kernel 경로와 NIC 암호 처리는 다른 비용·버퍼 조건이 있습니다. CPU 사용 감소·zero-copy·record 경계의 실제 지원을 측정합니다.')])

    topic('Packet Socket·링과 링크 프레임','네트워크','net/packet/af_packet.c','packet_recvmsg',
      '링크 계층의 packet을 관찰하거나 빠르게 수집할 때 socket buffer와 공유 ring의 소유권을 알아야 합니다.',
      'AF_PACKET은 link-layer frame 접근을 제공하며 TPACKET ring은 mmap buffer에 frame·block metadata를 전달합니다. Kernel과 user의 status 전환이 소유권을 표현하고 frame 크기·snaplen·drop·padding을 확인해야 합니다. Ring 접근을 장치에서 사용자까지 무조건 복사 0이라고 설명할 수는 없습니다.',
      '권한이 필요한 capture는 학습 namespace·veth에서 수행합니다. Socket 종류·interface bind·ring version·frame/block 크기·status를 맞추고 소비 후 kernel 소유로 돌려줍니다.',
      'packet_recvmsg와 tpacket_rcv 실제 정의의 status·frame 길이·drop을 연결하세요.',
      q('Ring slot을 사용자 소유로 받은 뒤 돌려주지 않으면 어떤 문제가 생길 수 있는가?','가용 slot 고갈과 packet drop','Kernel이 같은 slot을 안전하게 무한 재사용','소유권 반환이 있어야 다시 채울 수 있습니다. Producer·consumer 상태와 capacity를 관리해야 합니다.'),
      q('Captured snaplen이 원래 frame 길이보다 작으면 buffer만으로 원본 전체를 읽는가?','보관한 길이와 원본 길이를 구분한다','길이 metadata와 관계없이 항상 모든 byte가 있다','Capture는 일부만 보관할 수 있습니다. 원래 길이와 captured length를 구분하고 실제 buffer 범위 안에서 해석합니다.'),
      details=[detail('TPACKET 버전','Frame 단위와 block 단위 retirement 등 버전의 layout·poll 의미가 다릅니다. Version에 맞는 header와 offset을 사용합니다.'),detail('Publication 순서','데이터·metadata를 쓴 뒤 ownership status를 공개해야 user가 미완성 frame을 읽지 않습니다. Shared ring의 메모리 순서와 status 접근을 규약대로 처리합니다.')])

    topic('TIPC·노드와 Service 주소','네트워크','net/tipc/socket.c','tipc_sendmsg',
      '분산 앱의 service를 위치와 독립적인 이름으로 찾고 node 변화에 대응하는 통신 모델이 필요할 수 있습니다.',
      'TIPC는 node·port와 service type·instance 등의 주소·name distribution을 지원합니다. Service lookup·bearer·link·메시지 전달과 flow control을 관리합니다. TCP의 IP:port만으로 모든 service 이름 규약을 설명할 수 없습니다.',
      '지원 TIPC 환경의 node·bearer·network ID와 socket 주소 형식을 확인합니다. Service publish·withdraw·group·message type의 지원을 따라 오류와 peer 종료를 처리합니다.',
      'tipc_sendmsg→__tipc_sendmsg와 sockaddr_tipc·name lookup을 읽으세요.',
      q('TIPC service 주소와 물리 node·port 주소는 같은 의미인가?','위치 독립 service 이름과 구체 endpoint를 구분한다','모든 service 번호는 항상 IP 주소다','Service lookup은 이름과 위치를 연결합니다. 이름 publication이 달라지면 같은 service 요청의 대상도 달라질 수 있습니다.'),
      q('Service가 사라졌는데 이전 결과만 믿고 모든 전송을 성공으로 처리해도 되는가?','변경·오류·withdraw와 전달 결과를 처리한다','조회 한 번이면 영구적으로 같은 endpoint다','분산 상태와 node·service 수명은 변할 수 있습니다. 위치와 흐름의 실패 경계를 처리해야 합니다.'),
      details=[detail('Lock과 내부 함수','tipc_sendmsg는 socket lock으로 상태를 보호한 뒤 내부 송신 함수를 호출합니다. Internal 함수가 요구하는 lock 조건과 대기 해제 규약을 확인합니다.'),detail('Name distribution','각 node의 service publication을 전달해 다른 node가 찾아볼 수 있게 합니다. 분산 이름 상태의 수렴과 실제 message delivery는 같은 순간이 아닐 수 있습니다.')])

    topic('MCTP·관리 메시지와 Tag','네트워크','net/mctp/af_mctp.c','mctp_sendmsg',
      '장치 관리 통신에서 작은 endpoint 주소와 요청·응답 tag를 이용해 메시지를 구분할 수 있어야 합니다.',
      'MCTP는 endpoint ID와 message type·tag·tag owner, 여러 binding으로 관리 메시지를 전달합니다. 큰 메시지의 packet 분할·재조립과 tag 수명을 관리합니다. Network ID는 EID의 범위를 구분하며 IP routing 주소와 같은 체계가 아닙니다.',
      '지원 AF_MCTP의 sockaddr_mctp·network·EID·type·tag bits를 설정하고 요청 tag 할당과 응답 규약을 따릅니다. Payload format과 관리 권한은 상위 프로토콜에서도 검증합니다.',
      'mctp_sendmsg의 MCTP_TAG_MASK·OWNER·PREALLOC과 route·skb 준비를 읽으세요.',
      q('MCTP tag owner와 tag 숫자는 동일한 bit 역할인가?','요청 소유 표시와 tag 값 영역을 구분한다','어떤 bit든 같은 주소를 뜻한다','Allowed tagbits가 mask·owner·prealloc으로 나뉩니다. 요청·응답의 tag 수명과 방향을 맞춰야 합니다.'),
      q('MCTP 메시지를 여러 packet으로 보내면 수신은 각 packet을 항상 별도 앱 메시지로 보는가?','분할·재조립으로 원래 메시지를 처리한다','모든 packet이 독립 원본이다','Start·end·sequence 등 규약으로 메시지 경계를 복원합니다. Buffer 크기·timeout·중복을 함께 처리해야 합니다.'),
      details=[detail('Network와 EID','같은 EID도 관리 network 범위가 다를 수 있습니다. Route 선택에서 network·interface·endpoint를 함께 고려합니다.'),detail('Tag 재사용','완료 전 같은 tag를 같은 peer에 잘못 재사용하면 응답을 혼동할 수 있습니다. Tag 할당·key 상태·timeout·해제를 연결합니다.')])

    topic('IEEE802154·저전력 MAC','네트워크','net/ieee802154/socket.c','dgram_sendmsg',
      '작은 frame과 짧은 주소를 쓰는 저전력 무선 MAC의 제한을 IP socket과 구분해야 합니다.',
      'IEEE802.15.4의 MAC은 PAN·단축 또는 확장 주소·frame control·sequence·link 보안 등을 표현합니다. Linux socket은 목적 주소와 장치·MTU를 확인해 datagram을 MAC 경로로 넘깁니다. 6LoWPAN 같은 상위 IPv6 adaptation은 별도 계층입니다.',
      '지원 radio·PAN·주소·channel을 학습 장치나 simulator에서 확인합니다. Datagram 길이·frame overhead·ACK·보안·규제 조건은 환경의 규약을 따릅니다. 일반 Wi-Fi frame과 같은 크기로 가정하지 않습니다.',
      'dgram_sendmsg의 sockaddr_ieee802154·mtu·MAC cb와 장치 선택을 읽으세요.',
      q('802.15.4 MAC과 6LoWPAN은 같은 계층 기능인가?','링크 MAC과 IPv6 adaptation을 구분한다','둘 다 항상 TCP 연결만 만든다','MAC은 frame·링크 주소를, 6LoWPAN은 그 위의 IPv6 압축·fragment adaptation을 처리합니다.'),
      q('MAC payload 길이를 계산할 때 header·보안 overhead를 무시해도 되는가?','MTU와 overhead를 함께 확인한다','모든 데이터 길이가 무제한이다','작은 frame 안에 header·보안 정보가 들어갑니다. Device MTU와 남는 payload 범위를 맞춰야 합니다.'),
      details=[detail('주소 형식','PAN과 short·extended 주소의 종류가 destination 표현을 정합니다. 숫자의 폭·endianness와 address type을 함께 확인합니다.'),detail('ACK의 범위','MAC ACK가 있더라도 앱 메시지 전체의 처리·상위 신뢰성·인증 완료와 같은 의미는 아닙니다. 어느 계층의 성공인지 구분합니다.')])

    topic('6LoWPAN·IPv6 헤더 압축','네트워크','net/6lowpan/iphc.c','lowpan_header_compress',
      'IPv6 header를 작은 링크 frame에 담기 위해 공유된 정보로 표현을 줄이는 adaptation이 필요합니다.',
      '6LoWPAN IPHC는 주소 prefix·link 주소·traffic·hop limit 등으로 재구성 가능한 IPv6 field를 줄입니다. Context ID·압축 flag가 해석 규약을 전달합니다. 압축은 데이터 암호화가 아니며 fragmentation·UDP NHC 같은 처리는 별도 형식을 갖습니다.',
      '송수신 양쪽의 context·주소·지원 NHC를 맞춥니다. 압축된 header 길이와 복원 buffer 범위를 검증하고 context가 없는 입력을 임의로 해석하지 않습니다.',
      'lowpan_header_compress의 IPv6 protocol 확인·iphc0/1·sci/dci·cid를 읽으세요.',
      q('6LoWPAN header에서 생략한 주소를 수신자가 복원하려면 무엇이 필요한가?','압축 flag와 공유 context·link 주소 등의 규약','모든 주소는 항상 0이라고 가정','전달하지 않은 field는 약속된 정보에서 복원합니다. Sender와 receiver context가 맞지 않으면 다른 packet을 만들게 됩니다.'),
      q('IPHC header가 작아졌다는 것이 내용의 비밀성을 의미하는가?','표현 압축과 암호화는 다르다','생략된 header는 항상 비밀이다','정당한 수신자가 복원하는 공개 표현 규약입니다. 보안이 필요하면 적절한 링크·상위 암호 구성을 사용합니다.'),
      details=[detail('범위 검증','압축 flag별로 입력에서 읽는 byte 수가 달라집니다. 손상 header의 길이·주소 종류·context lookup 실패를 처리해야 잘못된 buffer 읽기를 막습니다.'),detail('MTU와 Fragment','압축해도 큰 packet은 여러 frame이 필요할 수 있습니다. 재조립 식별자·offset·timeout과 제한된 메모리 비용을 함께 고려합니다.')])

    topic('NFC·접촉식 통신의 Socket','네트워크','net/nfc/af_nfc.c','nfc_sock_create',
      '근거리 무선 장치의 discovery·protocol·socket 경계를 알아야 단순 IP 통신과 구분할 수 있습니다.',
      'NFC core는 장치와 target 발견·지원 protocol·raw 또는 LLCP socket을 연결합니다. AF_NFC 생성은 protocol table·module 참조와 지원 network 조건을 검사합니다. 접촉 거리라는 특성이 자동으로 peer 인증·비밀성을 제공하는 것은 아닙니다.',
      '지원 NFC controller와 protocol·target·LLCP 조건을 확인합니다. Device 종료·target 손실·socket 수명을 관리하고 payload·상위 인증 규약을 검증합니다.',
      'nfc_sock_create의 init_net 제한·proto 범위·proto_tab·try_module_get을 읽으세요.',
      q('이 v6.12 NFC socket create가 임의 network namespace에 항상 지원되는가?','init_net 이외를 거부하는 검사가 있다','모든 namespace에서 자동 동일하다','소스는 net!=&init_net이면 -EAFNOSUPPORT를 반환합니다. 보편적인 socket 이름만으로 namespace 지원을 추정하지 않습니다.'),
      q('NFC의 짧은 거리만으로 전달 데이터가 항상 인증됐다고 볼 수 있는가?','통신 거리와 보안 인증은 별도다','가까우면 모든 payload가 신뢰된다','장치·target·상위 protocol의 인증·검증 경계를 확인해야 합니다. Transport 특성이 임의 입력을 안전하게 만들지 않습니다.'),
      details=[detail('Protocol table','Proto 번호를 검증하고 해당 module 참조를 얻어 create를 호출합니다. Protocol 지원과 device 지원은 별도이며 module 수명도 socket 경로와 연결됩니다.'),detail('Discovery와 연결','대상을 찾는 단계와 payload session을 유지하는 단계는 다릅니다. Target 사라짐·재발견·protocol 전환을 관리해야 오래된 상태를 쓰지 않습니다.')])

    topic('RDS·신뢰 데이터그램과 Transport','네트워크','net/rds/send.c','rds_sendmsg',
      '메시지 경계를 유지하는 신뢰 통신이 여러 transport 위에서 어떤 queue·연결 상태를 관리하는지 알아야 합니다.',
      'RDS는 message-oriented 전달과 flow control·connection·sequence를 관리하며 TCP·InfiniBand 등 transport가 구현을 제공합니다. RDS의 신뢰 규약과 특정 transport의 RDMA 기능은 다른 계층입니다. Socket에 대기시킨 완료와 peer 앱 처리 완료를 구분합니다.',
      '지원 RDS transport·주소·port·message 길이를 확인합니다. Ancillary RDMA operation이 필요한 경우 memory region·completion·오류 규약을 따릅니다. 모든 RDS 요청이 zero-copy RDMA라고 가정하지 않습니다.',
      'rds_sendmsg의 message·connection path·nonblock·allocated_mr와 send queue를 읽으세요.',
      q('RDS라는 socket 이름이면 모든 전송이 반드시 InfiniBand RDMA인가?','선택한 transport와 operation을 확인한다','항상 같은 hardware 경로다','RDS는 여러 transport를 사용할 수 있습니다. Message 규약과 RDMA memory operation의 지원은 따로 봅니다.'),
      q('RDS send queue에 payload가 들어갔다면 peer 앱이 이미 처리한 것인가?','로컬 제출과 원격 처리 완료는 다르다','어떤 send 성공도 앱 처리를 확정한다','연결·전송·확인·사용자 처리의 경계가 다릅니다. App acknowledgement가 필요한 요구는 상위 규약으로 설계합니다.'),
      details=[detail('Connection path','연결 상태와 여러 경로의 선택을 관리합니다. Socket의 message와 transport connection 객체는 수명·역할이 다릅니다.'),detail('Memory region','등록된 memory region·key·mapping은 RDMA 접근 권한을 표현합니다. Socket payload가 있다고 임의 포인터를 remote 접근 주소로 노출하지 않습니다.')])

    topic('SMC·공유 메모리 기반 통신','네트워크','net/smc/af_smc.c','smc_sendmsg',
      'TCP socket과 비슷한 stream API를 다른 데이터 경로로 가속할 때 협상과 fallback을 구분해야 합니다.',
      'SMC는 연결 협상 뒤 RDMA 또는 ISM 기반 공유 memory로 데이터 경로를 마련할 수 있습니다. TCP control·fallback과 SMC buffer·peer cursor는 별도 상태입니다. API 호환성과 실제 사용한 transport가 같다는 뜻은 아닙니다.',
      '지원 SMC-R·SMC-D 장치와 peer 협상을 확인하고 fallback 여부·send buffer·통계를 관찰합니다. Source의 MSG_FASTOPEN 등 미지원 조건과 오류를 처리합니다.',
      'smc_sendmsg의 use_fallback·MSG_FASTOPEN과 smc_tx_sendmsg를 연결하세요.',
      q('SMC socket 생성이 실제 data path 사용을 항상 보장하는가?','협상·device 지원과 TCP fallback을 확인한다','모든 peer가 무조건 SMC다','지원되지 않는 조건은 fallback할 수 있습니다. Socket API 이름과 실제 transport 경로를 구분해 성능을 측정합니다.'),
      q('공유 buffer를 peer가 아직 소비하지 않았는데 재사용해도 되는가?','cursor·가용 공간·flow control을 따라야 한다','copy를 줄이면 소유권이 사라진다','공유 memory에서도 producer·consumer와 peer 진행 상태가 필요합니다. 아직 읽는 byte를 덮으면 stream 내용이 손상됩니다.'),
      details=[detail('Cursor','송신 생산 위치와 peer 소비 위치를 추적해 얼마나 새 데이터를 보낼 수 있는지 계산합니다. 링 wrap과 memory publication 순서가 필요합니다.'),detail('Fallback 의미','Fallback은 같은 app API에서 다른 경로를 쓰는 처리입니다. 이후 연결 상태·error·shutdown 규약도 이어져야 하며 성능 결과를 SMC 가속으로 잘못 기록하지 않습니다.')])

    topic('RxRPC·RPC와 신뢰 UDP','네트워크','net/rxrpc/af_rxrpc.c','rxrpc_sendmsg',
      'RPC 요청·응답을 UDP 기반으로 신뢰 전달하려면 call 식별·순서·확인·보안 상태를 관리해야 합니다.',
      'RxRPC는 connection·call·packet sequence·ACK·재전송과 보안 context를 관리합니다. Socket ancillary data로 user call 식별과 RPC 동작을 연결합니다. UDP datagram 자체와 완성된 RPC message·응답 성공은 별도 경계입니다.',
      '지원 RxRPC protocol의 sockaddr_rxrpc·call ID·security key·send flags를 따릅니다. Call 완료·abort·timeout·buffer 수명을 처리하고 peer 응답 format을 검증합니다.',
      'rxrpc_sendmsg의 address validation·local/call 상태와 sendmsg 내부를 읽으세요.',
      q('UDP 기반이면 RxRPC가 신뢰성·재전송을 관리할 수 없는가?','상위 RxRPC가 ACK·sequence·재전송을 구현한다','UDP 위의 모든 protocol은 손실을 무조건 방치한다','UDP의 전달 계약 위에 추가 상태 기계를 구현할 수 있습니다. 어떤 계층에서 신뢰성을 제공하는지 구분합니다.'),
      q('RPC call abort를 성공 응답과 동일하게 처리하는가?','별도 call 종료·오류 상태로 처리한다','소켓이 열려 있으면 모든 call은 성공','연결 생존과 개별 call 결과는 다릅니다. Abort code·timeout·응답 완료를 상위 호출자에 전달해야 합니다.'),
      details=[detail('Call과 Connection','한 connection에서 여러 call의 수명을 관리할 수 있습니다. User call ID와 wire 식별자·packet sequence를 같은 정수로 가정하지 않습니다.'),detail('재전송 Buffer','확인 전 request data가 다시 필요할 수 있습니다. Buffer 참조를 유지하고 timeout·취소·ACK 뒤 정확히 해제해야 합니다.')])

    topic('HSR·이중 경로와 중복 제거','네트워크','net/hsr/hsr_forward.c','hsr_forward_skb',
      '링크 하나가 실패해도 전달을 이어가려면 이중 경로의 frame 복제와 중복 제거가 필요합니다.',
      'HSR은 두 ring 방향으로 frame을 전달하고 source node·sequence 등의 상태로 중복을 구분합니다. Port·node database·supervision·age 관리가 필요하며 label이 같은 오래된 frame과 새 frame의 sequence wrap을 고려합니다. Redundancy가 모든 앱 실패를 보장 복구하지는 않습니다.',
      '지원 HSR/PRP mode·port·MTU·topology를 확인하고 학습 namespace에서 중복·링크 장애·통계를 관찰합니다. Frame tag 처리와 host 전달·forward를 구분합니다.',
      'hsr_forward_skb의 fill_frame_info·node_src·sequence_nr·register와 forward_do를 읽으세요.',
      q('이중 경로로 같은 frame이 오면 앱에 반드시 두 번 전달해야 하는가?','중복 상태를 확인해 중복 전달을 줄인다','복제는 항상 새 메시지 두 개다','복제는 장애 대비의 전달 방식입니다. Source·sequence 추적으로 원래 frame의 중복을 구분해야 합니다.'),
      q('중복 제거에서 sequence 숫자만 보고 source node는 무시해도 되는가?','source와 sequence 범위를 함께 추적한다','모든 장치가 하나의 sequence를 영구 공유한다','서로 다른 node가 같은 번호를 쓸 수 있습니다. Node별 상태·port·시간과 wrap 조건을 확인합니다.'),
      details=[detail('RCU Node 수명','Forward 함수는 RCU 구간에서 node·port 상태를 참조합니다. DB 제거·timer 정리·다른 경로의 참조를 규약대로 처리해야 합니다.'),detail('Ring의 루프','Ring 구조에서는 중복·반복 전달을 적절히 억제해야 합니다. 일반 bridge의 동작과 HSR tag·sequence 기반 처리의 차이를 봅니다.')])

    topic('Bonding·링크 결합과 Failover','네트워크','drivers/net/bonding/bond_main.c','bond_start_xmit',
      '여러 physical link를 하나의 논리 장치로 묶을 때 선택 정책과 장애 감지·switch 협상을 관리해야 합니다.',
      'Bonding mode에 따라 active-backup·분산 선택·802.3ad aggregation 등의 전달 방식이 달라집니다. Hash 기반 분산은 한 flow를 한 link에 둘 수 있어 모든 단일 flow 대역폭이 link 합계가 되지는 않습니다. Link 감지와 peer/switch의 지원 조건도 필요합니다.',
      'Bond의 mode·slave·active link·hash·monitor 상태를 조회합니다. Lab veth에서 failover를 관찰하고 실제 switch 협상과 물리 link 상태 검증은 구분합니다.',
      'bond_start_xmit→__bond_start_xmit의 mode 선택과 slave 상태·RCU를 읽으세요.',
      q('두 1Gbps link를 bond하면 단일 hash flow가 항상 2Gbps가 되는가?','분산 정책과 flow 배치를 확인해야 한다','모든 mode의 모든 flow가 자동 두 배다','한 flow가 한 slave에 배치될 수 있습니다. 총 처리량과 한 연결의 처리량은 다른 지표입니다.'),
      q('Active-backup과 802.3ad는 같은 switch·전송 규약인가?','mode별 failover·협상·분산을 구분한다','모든 mode가 항상 동일하다','Active link 전환과 aggregation 협상은 다릅니다. Peer 설정·monitor·hash 규약을 맞춰야 합니다.'),
      details=[detail('장애 감지','Link 상태 또는 ARP monitor 등 기준으로 slave 사용 가능성을 판단합니다. 감지 시점과 기존 flow·MAC 학습 갱신의 지연을 함께 봅니다.'),detail('전송 결과','NETDEV_TX_BUSY는 전송이 받아들여지지 않은 경로입니다. skb 소유권·재큐잉과 실제 성공 처리의 return 계약을 구분합니다.')])

    topic('DSA·Switch Port와 CPU Tag','네트워크','net/dsa/tag.c','dsa_switch_rcv',
      '외부 switch의 여러 port를 Linux network device로 표현하려면 CPU port frame의 출처를 해석해야 합니다.',
      'Distributed switch architecture는 switch port를 net_device와 연결하고 conduit/CPU port를 통해 host packet을 전달합니다. Vendor tagger는 frame에서 source port·switch 정보를 해석하거나 송신 목적지를 넣습니다. Hardware bridge offload와 CPU 경유 전달을 구분해야 합니다.',
      '지원 switch·tag protocol·CPU port·user port topology를 확인합니다. VLAN·bridge·MTU·offload 표시와 packet capture 위치를 함께 관찰합니다. Tag format을 일반 Ethernet payload라고 해석하지 않습니다.',
      'dsa_switch_rcv의 tagger rcv·user device 선택과 dsa_tree_setup의 topology를 연결하세요.',
      q('DSA CPU port로 온 frame을 어느 user port에서 온 것으로 볼지 판단하는 정보는?','tagger 규약의 switch·port metadata','항상 파일 descriptor 번호','Switch와 CPU 사이의 tag가 출처·목적을 표현할 수 있습니다. Hardware별 tagger를 맞춰야 올바른 net_device로 전달합니다.'),
      q('DSA port가 Linux device로 보이면 모든 packet이 항상 CPU를 거치는가?','hardware forwarding·offload 경로를 구분한다','모든 switch packet을 CPU가 하나씩 처리한다','Switch 내부 hardware가 전달할 수 있습니다. CPU 관찰과 offload 상태를 구분해 통계·capture를 해석합니다.'),
      details=[detail('Tag와 MTU','Tag가 header 앞·뒤·중간에 붙는 형식이 다를 수 있습니다. 필요 headroom·tailroom·MTU 계산과 tag 제거 뒤 protocol 위치를 맞춥니다.'),detail('Conduit 수명','CPU/conduit device와 user device의 연결·RCU 참조·종료를 관리합니다. Switch 제거와 packet 수신이 겹칠 때 stale port를 사용하지 않아야 합니다.')])
