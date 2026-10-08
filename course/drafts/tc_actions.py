"""Individually authored packet action contracts from Linux v6.12."""
def register(topic, q, detail):
    def lesson(name, file, symbol, why, principle, use, observation, questions, cards):
        topic(name, '트래픽 제어 알고리즘', 'net/sched/act_'+file+'.c', symbol,
              why, principle, use, observation,
              *(q(*item) for item in questions),
              details=[detail(*item) for item in cards])

    lesson('TC Action 실행기·PIPE와 제한된 제어 흐름', 'api', 'tcf_action_exec',
      '여러 패킷 처리 행동을 연결하려면 다음 행동으로 진행하는 결과와 전체 실행을 끝내는 결과를 구분해야 합니다.',
      '실행기는 등록한 action 배열을 순서대로 처리합니다. Software를 건너뛰는 action은 제외하고 TC_ACT_PIPE면 다음 action으로 진행합니다. REPEAT는 같은 action을 재실행하지만 32회 제한을 두며, 소진하면 OK로 pipeline을 끝냅니다. JUMP에는 별도 TTL과 범위 검사, GOTO_CHAIN에는 대상 chain 존재 검사가 있습니다.',
      '격리된 network namespace에서 tc filter에 action 목록을 연결하고 각 action의 control 결과를 확인합니다. 앞에서 OK나 SHOT으로 끝나면 뒤의 수정·집계 action이 실행되지 않을 수 있으므로 순서와 PIPE를 함께 설계합니다.',
      'tcf_action_exec의 repeat_ttl·jmp_ttl·skip_sw·ret!=TC_ACT_PIPE를 읽으세요.',
      [('PIPE를 반환하면 실행기는 어떻게 진행하는가?', '다음 action을 실행한다', '항상 즉시 전체 pipeline을 끝낸다', '반복문의 종료 조건은 ret!=TC_ACT_PIPE입니다. PIPE는 행동 목록의 다음 항목으로 이어가는 계약입니다.'),
       ('같은 action이 계속 REPEAT하면 무한 실행되는가?', '제한을 소진하면 OK로 종료한다', '반드시 무한히 반복한다', 'repeat_ttl은 32이며 REPEAT마다 감소합니다. 소진 시 경고 후 OK를 반환하므로 구성 오류에 무제한 시간을 쓰지 않습니다.')],
      [('Chain 실패', 'GOTO_CHAIN에서 goto_chain pointer가 없으면 drop reason을 설정하고 SHOT을 반환합니다. 대상 chain ID라는 정수와 살아 있는 chain 객체의 연결은 별도 조건입니다.'),
       ('제어 흐름을 손으로 추적하기', 'A가 PIPE, B가 OK, C가 SHOT이면 A와 B만 실행합니다. Action 등록 순서표에 반환값과 실제 실행 여부를 적어 보면 분류 성공과 전달 성공의 차이가 보입니다.')])

    lesson('TC Gact·일반 Verdict와 확률 선택', 'gact', 'tcf_gact_act',
      '필터에 일치한 패킷을 통과·폐기하거나 일정 비율로 다른 행동을 선택하는 가장 작은 실행 경로를 공부합니다.',
      'Gact는 설정한 control action을 읽고 CONFIG_GACT_PROB 및 ptype이 있으면 확률 함수로 결과를 바꿉니다. Random mode는 [0,pval) 중 0일 때 대체 행동, deterministic mode는 원자적 packet count가 pval의 배수일 때 대체 행동입니다. 선택한 결과가 SHOT이면 drop 통계를 올립니다.',
      '격리된 namespace에서 tc gact의 pass/drop/pipe와 지원되는 probability mode를 비교합니다. Random rate 1/N은 관측한 매 N개 중 정확히 한 개라는 보장이 아니며 deterministic counter mode와 구분합니다.',
      'tcf_gact_act와 gact_net_rand·gact_determ의 0/나머지 조건을 읽으세요.',
      [('Deterministic pval=4, 증가한 count=8이면 어느 결과인가?', '대체 action이다', '항상 기본 action이다', '8%4=0이므로 gact_determ은 tcfg_paction을 반환합니다. 나머지가 있는 packet은 기본 action입니다.'),
       ('Random mode의 1/4 선택은 연속 4개마다 정확히 하나인가?', '각 추첨의 확률이며 짧은 구간 개수는 달라진다', '모든 4개 묶음에 반드시 하나다', 'get_random_u32_below(4)==0을 검사합니다. 원자적 count의 배수 조건과 다른 선택 원리입니다.')],
      [('설정 검증', '초기화는 probability ptype 범위와 fallback GOTO_CHAIN 금지를 검사합니다. Fast path가 함수 배열을 참조할 수 있는 것은 입력 검증과 연결됩니다.'),
       ('메모리 순서', '확률 함수의 smp_rmb는 초기화의 smp_wmb와 짝을 이룹니다. ptype을 보았을 때 함께 설정된 확률 매개변수를 읽는 순서가 문제이며 단순 난수 계산만 있는 코드가 아닙니다.')])

    lesson('TC BPF Action·반환 Opcode와 기본값', 'bpf', 'tcf_bpf_act',
      '프로그램으로 패킷 처리 결정을 작성해도 커널이 허용한 반환 코드와 context를 따라야 합니다.',
      'BPF action은 ingress에서 MAC 영역을 push해 program을 실행한 후 pull로 복원합니다. 알려진 PIPE/RECLASSIFY/OK/REDIRECT/SHOT은 결과로 사용하며 SHOT은 drop 통계를 올립니다. UNSPEC은 설정한 기본 action을 사용하고, 알려지지 않은 반환은 UNSPEC으로 바꿉니다. Prefetched socket과 timestamp 상태도 조정합니다.',
      '격리된 namespace에서 tc BPF action 프로그램을 연결하고 verifier·helper·context 및 기본 action을 확인합니다. TC classifier 일반 모드의 classid 반환이나 XDP verdict 숫자를 이 action에 그대로 옮기지 않습니다.',
      'tcf_bpf_act의 switch(filter_res)와 TC_ACT_UNSPEC·default 분기를 읽으세요.',
      [('Program이 UNSPEC을 반환하면 이 action은 무엇을 선택하는가?', 'prog->tcf_action 기본 설정', '무조건 packet drop', 'TC_ACT_UNSPEC case는 기본 action을 대입합니다. default의 unknown 반환을 UNSPEC으로 바꾸는 동작과 다릅니다.'),
       ('알려지지 않은 정수 반환을 임의의 tc classid로 쓰는가?', 'UNSPEC으로 변환한다', '그 정수를 classid로 저장한다', '이것은 act_bpf의 verdict 처리입니다. 일반 cls_bpf의 class 선택 branch와 반환 계약이 다릅니다.')],
      [('Socket 수명', 'Prefetched socket이 있고 결과가 OK가 아니면 skb_orphan을 호출합니다. Program verdict는 분류 값뿐 아니라 참조·소유 상태에 영향을 줄 수 있습니다.'),
       ('Header 관점', 'Ingress program 실행 전 push와 후 pull을 쌍으로 읽습니다. Program의 data pointer가 어떤 header부터 시작하는지 알지 못하면 같은 offset으로 다른 byte를 읽게 됩니다.')])

    lesson('TC Connmark·Connection Mark 복원', 'connmark', 'tcf_connmark_act',
      '연결 단위의 정책 표식을 개별 패킷의 scheduler 분류에 가져오려면 두 mark의 저장 위치를 구분해야 합니다.',
      'IPv4/IPv6와 최소 header 길이를 확인하고 skb에 이미 연결된 conntrack이 있으면 그 mark를 skb->mark에 복사합니다. 없으면 packet tuple과 설정 zone으로 conntrack을 찾아 참조를 얻고 복사 후 nf_ct_put합니다. 성공 표식 수에는 overlimit 통계를 재사용하며 lookup 실패도 설정 action으로 나갑니다.',
      '격리된 namespace에서 conntrack mark와 tc connmark·FW classifier를 연결합니다. Mark가 wire header에 자동 전송되는 값은 아니며, zone·namespace·연결 생성 상태와 copy 방향을 확인합니다.',
      'tcf_connmark_act의 nf_ct_get·tuple lookup·skb->mark·nf_ct_put을 읽으세요.',
      [('복사 방향은 어느 쪽인가?', 'connection mark에서 skb mark로', 'skb mark에서 connection mark로', '원본은 skb->mark=READ_ONCE(c->mark)입니다. 패킷 표식을 연결 상태에 저장하는 반대 기능으로 해석하면 정책이 뒤집힙니다.'),
       ('Conntrack lookup이 실패하면 항상 SHOT인가?', '설정된 action을 반환한다', '실패한 모든 lookup은 반드시 drop한다', '실패 branch는 out으로 가며 READ_ONCE(ca->tcf_action)을 반환합니다. 성공 여부와 control verdict는 별도입니다.')],
      [('참조 균형', 'nf_conntrack_find_get은 참조를 얻습니다. Tuple lookup 경로의 nf_ct_put과 이미 skb에 붙어 있던 객체 경로의 차이를 표시하세요.'),
       ('통계의 실제 의미', '이 action은 overlimit counter를 표식 복사 성공 횟수로 사용합니다. 통계 이름만 보고 모든 증가를 대역폭 초과로 설명하면 틀립니다.')])

    lesson('TC CT·추적·Commit·Fragment 소유권', 'ct', 'tcf_ct_act',
      '패킷에 연결 상태·NAT·zone을 붙이는 과정에는 재조립, 상태 확정, 참조 재획득과 소비 여부가 함께 들어갑니다.',
      'Clear는 post_ct를 지우고 연결 참조를 분리합니다. 추적 경로는 L3로 skb 위치를 바꾸고 fragment를 처리한 뒤 zone별 cached/flow-table/conntrack 경로와 NAT를 실행합니다. Commit이면 mark·label을 갱신하고 confirm합니다. Confirm 충돌로 객체가 사라질 수 있어 skb에서 ct를 다시 얻습니다. Fragment 처리로 넘겨진 skb는 CONSUMED를 반환할 수 있습니다.',
      '격리된 namespace에서 tc ct zone·commit·clear와 flower ct_state를 연결해 상태 전이를 기록합니다. Stateless tc nat와 연결 추적 NAT를 구분하고 반환 SHOT·CONSUMED 및 skb를 계속 사용할 수 있는지를 함께 읽습니다.',
      'tcf_ct_act의 clear·cached·commit·confirm 이후 nf_ct_get·out_frag를 읽으세요.',
      [('Confirm 직전의 ct pointer를 무조건 계속 써도 되는가?', 'Confirm 후 skb에서 다시 얻어야 한다', 'Confirm은 객체 수명에 영향을 주지 않는다', '원문 주석은 충돌 해결로 ct가 drop될 수 있어 UAF를 막기 위한 재획득이라고 설명합니다. 상태 확정과 객체 수명을 같이 추적합니다.'),
       ('Fragment 처리가 skb를 가져간 뒤의 CONSUMED는 일반 OK와 같은가?', '호출자가 packet 소유권을 이어 쓰면 안 된다', '언제나 원래 skb를 다시 enqueue해도 된다', 'out_frag는 CONSUMED를 반환합니다. 다음 처리 단계가 skb를 소유하고 있다는 의미를 반환 계약과 함께 확인해야 합니다.')],
      [('Clear 범위', 'Clear는 skb의 연결 관계를 분리하는 경로입니다. 시스템 전체 conntrack table을 비우는 관리 명령으로 설명하지 않습니다.'),
       ('Verdict mask', 'Netfilter 결과의 상위 bit에는 queue/errno 정보가 있을 수 있어 NF_VERDICT_MASK로 action 의미를 판단합니다. 정수 전체를 기본 verdict 번호와 단순 비교하지 않습니다.')])

    lesson('TC CTInfo·DSCP와 Masked Mark 복원', 'ctinfo', 'tcf_ctinfo_act',
      '연결 mark에 보존한 서비스 등급을 packet header나 local mark로 되돌릴 때 bit 범위와 ECN을 보존해야 합니다.',
      'IPv4/IPv6 header를 확보하고 기존 ct 또는 tuple/zone lookup으로 연결을 얻습니다. DSCP mode는 dscpstatemask가 없거나 연결 mark와 일치할 때 갱신합니다. Mask·shift로 DSCP 6bit를 추출해 두 bit 왼쪽으로 옮기고 ECN bits를 보존합니다. CPMARK mode는 connection mark AND cpmarkmask를 skb mark에 대입합니다.',
      '격리된 namespace에서 tc ctinfo의 DSCP mask/shift·state 조건과 cpmark mode를 확인합니다. 서비스 등급 6bit와 ECN 2bit를 분리해 계산하고, 연결 상태가 없거나 header를 writable로 만들지 못할 때 통계를 대조합니다.',
      'tcf_ctinfo_act와 tcf_ctinfo_dscp_set·tcf_ctinfo_cpmark_set을 읽으세요.',
      [('CPMARK가 대상 mask 밖의 기존 skb mark bit를 보존하는가?', '전체 skb mark를 masked connection 값으로 대입한다', '항상 기존 mark와 OR만 한다', 'helper는 skb->mark=ct->mark & cpmarkmask입니다. skbedit의 대상 bit만 교체하는 식과 다릅니다.'),
       ('DSCP 복원은 ECN bit를 새 DSCP 값으로 덮는가?', 'ECN을 보존하고 DSCP를 바꾼다', '서비스 등급 변경 때 ECN은 반드시 0이다', 'newdscp는 ECN mask를 제외하고 change_dsfield에는 ECN 보존 mask를 전달합니다. Traffic class byte의 두 기능을 분리합니다.')],
      [('State 조건', 'DSCP state mask가 설정되어 있으면 ct mark와 AND한 값이 nonzero인 경우만 복원합니다. Connection 존재만으로 모든 packet의 DSCP를 반드시 바꾸는 것은 아닙니다.'),
       ('실패 통계', 'Writable 확보 실패는 stats_dscp_error를 증가시킵니다. 상위 action은 설정 verdict를 반환하므로 수정 실패와 전체 drop을 동일하게 가정하지 않습니다.')])

    lesson('TC Csum·Header 수정 후 Checksum 보정', 'csum', 'tcf_csum_act',
      '패킷 주소·port를 바꾸면 수신자가 검사하는 checksum과 skb의 offload 상태도 일관되게 처리해야 합니다.',
      'Action은 update_flags와 protocol에 따라 IPv4/IPv6 checksum helper를 실행합니다. VLAN은 hardware tag와 payload tag를 구분해 내부 protocol까지 내려가며 payload VLAN을 pull한 횟수를 셉니다. 실패는 SHOT으로 바꾸되 out에서 pull했던 VLAN header를 다시 push합니다. Checksum은 오류 검출이며 암호학적 인증은 아닙니다.',
      '격리된 namespace에서 pedit 뒤에 적절한 tc csum update 종류를 붙이고 packet capture 및 checksum offload 상태를 확인합니다. Local capture의 표시와 실제 wire checksum을 구분하며 checksum 변경 대상을 protocol별로 설정합니다.',
      'tcf_csum_act의 update_flags·again·vlan_hdr_count·drop 후 out을 읽으세요.',
      [('Payload VLAN header를 pull한 뒤 checksum 처리에 실패하면 복원 경로는?', 'drop에서 action을 SHOT으로 바꾸고 out에서 push한다', '실패하면 복원 반복문을 반드시 건너뛴다', 'drop은 goto out으로 이어집니다. 성공뿐 아니라 오류 branch에서도 저장 위치를 복원하는 구조를 추적합니다.'),
       ('Checksum이 맞다는 것은 송신자가 인증되었다는 뜻인가?', '전송 오류 검출과 송신자 인증은 다르다', 'Checksum만으로 위조가 불가능하다', 'Checksum은 키를 사용하는 인증 tag가 아닙니다. Header 편집 후 무결한 형식을 만드는 기능과 보안 인증을 구분합니다.')],
      [('VLAN 표현', '같은 VLAN 의미라도 skb metadata에 hardware tag가 있거나 payload에 header가 있을 수 있습니다. Byte offset 계산 전에 실제 저장 형태를 읽어야 합니다.'),
       ('Flag의 범위', 'Update flag로 필요한 checksum 종류를 선택합니다. Header 수정 action이 모든 transport checksum을 자동으로 보정한다고 가정하지 말고 연결된 helper까지 확인합니다.')])

    lesson('TC Gate·시간 구간의 Packet 허용량', 'gate', 'tcf_gate_act',
      '시간표에 따라 stream을 열고 닫는 정책은 packet마다 현재 gate 상태와 구간 사용량을 일관되게 읽어야 합니다.',
      'Action은 lock 안에서 현재 status를 봅니다. PENDING이면 설정 action을 그대로 반환하고, gate가 닫혔으면 SHOT입니다. max_octets>=0이면 packet 길이를 현재 구간 사용량에 먼저 더하며 max보다 클 때 overlimit 및 drop입니다. Limit과 같은 값은 허용됩니다. 시간표를 갱신하는 timer 경로와 packet 검사 경로는 별도입니다.',
      '격리된 namespace에서 tc gate의 clock·base-time·구간 schedule·maxoctets를 확인합니다. Gate는 닫힌 구간 packet을 이 action 안에서 기다리게 하는 queue가 아니므로 상위 qdisc의 시간 예약과 구분합니다.',
      'tcf_gate_act의 PENDING·GATE_OPEN·current_entry_octets>current_max_octets를 읽으세요.',
      [('현재 800byte, 최대 1000byte에 200byte packet이 오면?', '정확히 1000이므로 이 limit 조건은 허용한다', '최대값과 같아도 항상 초과다', '비교는 >입니다. 다음 1byte를 더하면 1001이 되어 초과하므로 경계값을 직접 계산합니다.'),
       ('Gate가 닫힌 상태에서 이 action은 packet을 timer까지 대기시키는가?', 'SHOT으로 판정한다', '내부 대기 queue에 반드시 저장한다', 'GATE_OPEN이 없으면 drop label로 갑니다. 허용 판정 action과 shaping queue의 역할이 다릅니다.')],
      [('PENDING', 'Schedule이 준비 중인 상태는 닫힌 gate와 별도 bit로 처리하며 설정 action으로 나갑니다. 상태 bit를 하나의 boolean 열림/닫힘으로 축약하면 branch를 놓칩니다.'),
       ('Lock 범위', '현재 구간 octet 누계와 상태를 같은 lock 안에서 검사·갱신합니다. Timer가 구간을 바꾸는 상황과 병행 packet 처리의 일관성을 연결해 읽으세요.')])

    lesson('TC IFE·Metadata TLV의 Encode와 Decode', 'ife', 'tcf_ife_act',
      'Local skb 표식을 다른 처리 지점에 전하려면 metadata를 식별 가능한 wire 형식으로 직렬화하고 길이를 검증해야 합니다.',
      'IFE_ENCODE면 outer Ethernet header·총 metadata 길이·TLV 항목·원본 데이터 형식으로 encode하고, 아니면 decode합니다. Encode는 metadata가 없으면 설정 action으로 나가며 egress MTU 초과나 항목 encode 오류는 SHOT입니다. Decode는 TLV 범위와 끝 위치를 검사하고 metadata type별 ops를 찾습니다. Unknown type은 통계를 올리는 경로와 malformed drop 경로가 다릅니다.',
      '격리된 namespace와 IFE를 이해하는 상대에서 encode/decode 정책을 비교합니다. TLV는 type·length·value라는 직렬화 구조이며 mark/priority 같은 local 정보가 저절로 wire에 실리지 않는다는 점을 확인합니다.',
      'tcf_ife_act·tcf_ife_encode·tcf_ife_decode의 metalist·ifehdr_end를 읽으세요.',
      [('Unknown metadata type이면 malformed TLV와 항상 같은 처리인가?', '알 수 없는 ops 통계와 형식 오류 drop은 구분된다', '둘 다 반드시 같은 unconditional drop이다', 'find_decode_metaid 실패는 overlimit을 증가시키며 계속하는 경로입니다. TLV decode 실패나 끝 위치 불일치는 SHOT입니다.'),
       ('Encode할 metadata 길이가 0이면 반드시 새 outer header를 만드는가?', '설정 action을 반환하고 encode를 생략한다', '항상 빈 TLV packet을 만든다', 'metalen==0 branch는 overlimit 통계 후 return action입니다. Header 추가 비용과 실제 metadata 존재 조건을 연결합니다.')],
      [('TLV 끝 검사', '각 항목을 전체 metadata 끝까지 검사하고 최종 pointer가 정확히 끝인지 다시 봅니다. Length를 신뢰한 pointer 증가만으로 외부 입력 파싱을 끝내지 않습니다.'),
       ('Metadata plugin', 'metalist 항목의 ops->encode와 type별 decode가 역할을 나눕니다. Mark·priority·tcindex의 항목 구현은 IFE container 자체와 별도의 학습 대상입니다.')])

    lesson('TC Mirred·복제·Redirect와 SKB 소유권', 'mirred', 'tcf_mirred_act',
      '패킷 복사본을 보내는 mirror와 원래 흐름을 옮기는 redirect는 buffer 수명과 다음 처리의 책임이 다릅니다.',
      'Mirred는 CPU별 재귀 깊이를 제한하고 blockcast 또는 대상 device 경로를 선택합니다. 대상 전송 helper는 device UP/carrier를 확인합니다. 보통 clone하지만 ingress redirect의 재삽입 가능한 조건에서는 원본을 사용할 수 있습니다. 보낼 skb의 ct를 reset하고 data를 대상의 MAC/network header 기대 위치로 맞춥니다. 원본을 넘긴 redirect는 CONSUMED로 소유권을 표시합니다.',
      '격리된 namespace의 veth 쌍에서 tc mirred mirror/redirect와 ingress/egress 방향을 비교합니다. 같은 skb를 이중 enqueue하지 않도록 clone 여부·CONSUMED를 추적하고 target 상태·재귀 루프·device 수명을 확인합니다.',
      'tcf_mirred_act와 tcf_mirred_to_dev의 nest_level·dont_clone·nf_reset_ct를 읽으세요.',
      [('이 구현은 모든 redirect에서 반드시 새 skb clone을 만드는가?', '조건에 따라 원본 skb를 전달할 수 있다', '원본을 쓰는 branch는 전혀 없다', 'Ingress redirect와 재삽입 가능 verdict 조건이면 dont_clone입니다. 소유권 표시 CONSUMED를 같이 읽어야 합니다.'),
       ('대상 device가 사라졌을 때 action 함수는 반드시 SHOT으로 바꾸는가?', '해당 branch는 overlimit 후 기존 retval로 나간다', '모든 device 오류가 동일한 SHOT branch다', 'tcf_mirred_act의 !dev는 counter 후 dec_nest_level입니다. helper의 down-device redirect 오류가 SHOT이 되는 경로와 구분합니다.')],
      [('기존 Conntrack', 'Forward할 skb에 nf_reset_ct를 호출합니다. 원래 처리 경로에서 얻은 연결 관계를 새 방향에서도 그대로 재사용하는 것이 항상 맞지는 않습니다.'),
       ('복제와 깊은 복사', 'skb_clone은 skb 메타 객체를 복제하고 데이터 공유를 활용할 수 있습니다. Payload 수정 전 writable/COW 확보가 필요한 이유와 clone을 연결합니다.')])

    lesson('TC MPLS Action·Label Stack 조작', 'mpls', 'tcf_mpls_act',
      'MPLS forwarding header를 추가·제거·수정할 때 label stack과 Ethernet/IP header 위치를 함께 관리해야 합니다.',
      'Ingress에서는 MAC header로 위치를 맞추고 configured POP/PUSH/MAC_PUSH/MODIFY/DEC_TTL을 수행합니다. Push는 기존 MPLS 여부 등으로 stack entry를 만들고, modify는 필요한 header가 있는지 확인합니다. MAC_PUSH는 hardware VLAN tag를 실제 내부 header로 옮기는 경로가 있습니다. Helper 실패는 SHOT이며 성공 ingress 경로는 pull로 복원합니다.',
      '격리된 MPLS 실습 namespace에서 tc mpls의 label·protocol·TTL·동작 종류를 확인합니다. Label 값만 바꾸는 것과 label stack을 추가하는 것, Linux routing entry를 만드는 것은 서로 다른 작업입니다.',
      'tcf_mpls_act의 PUSH/MAC_PUSH/MODIFY/DEC_TTL과 VLAN tag 이동을 읽으세요.',
      [('MODIFY 전에 필요한 MPLS header를 확보하지 못하면?', 'drop 통계 후 SHOT', '없는 header를 항상 새로 만들어 수정', 'pskb_may_pull 실패는 drop입니다. Header 존재 확인 없이 packet memory를 읽지 않습니다.'),
       ('MAC_PUSH가 hardware VLAN tag를 항상 metadata에만 남기는가?', '실제 inner tag로 넣고 hw tag를 clear하는 경로가 있다', 'VLAN 표현은 어떤 경우에도 바뀌지 않는다', '__vlan_insert_inner_tag 이후 protocol을 바꾸고 __vlan_hwaccel_clear_tag를 호출합니다. Encapsulation과 저장 표현을 함께 추적합니다.')],
      [('LSE', 'Label stack entry는 label·traffic class·bottom-of-stack·TTL 같은 field를 담습니다. tcf_mpls_get_lse와 skb helper를 이어 읽으며 이미 MPLS인지 여부에 따른 초기화 차이를 확인하세요.'),
       ('Failure 위치', '성공의 ingress pull과 drop 반환 위치는 다릅니다. 이 action은 실패 skb를 계속 성공 경로로 다루는 것이 아니라 SHOT으로 끝내므로 호출자의 verdict 처리까지 연결합니다.')])

    lesson('TC NAT·Stateless Prefix 치환과 Checksum', 'nat', 'tcf_nat_act',
      '연결 table 없이 주소 prefix를 치환하는 구현에서 mask·fragment·transport checksum의 역할을 볼 수 있습니다.',
      'Egress flag면 source, 아니면 destination IPv4 주소를 선택합니다. (old XOR addr) AND mask가 0이면 prefix가 맞으며 new_addr의 mask bit와 원주소의 나머지 bit를 합쳐 치환합니다. IPv4 checksum과 첫 fragment의 TCP/UDP checksum을 보정합니다. ICMP error는 포함된 원래 IP 주소까지 별도 처리합니다. Stateful conntrack NAT와 다른 경로입니다.',
      '격리된 IPv4 namespace에서 tc nat의 prefix·egress 방향을 확인하고 packet capture로 주소와 checksum을 대조합니다. Port 연결 상태나 reply mapping을 자동으로 관리하는 기능으로 오해하지 않고 IPv4·fragment 조건을 명시합니다.',
      'tcf_nat_act의 mask 치환·IP_OFFSET·UDP zero checksum·ICMP error를 읽으세요.',
      [('10.1.2.3의 /24 prefix를 192.0.2.0으로 바꾸면 주소는?', '192.0.2.3', '192.0.2.0', 'new_addr & mask와 addr & ~mask를 합칩니다. /24의 host 8bit인 3을 보존합니다.'),
       ('뒤쪽 IPv4 fragment에서도 TCP header가 있다고 가정하는가?', 'IP_OFFSET 조건으로 transport 처리를 구분한다', '모든 fragment 첫 byte에 TCP header가 있다', 'Fragment offset이 있으면 protocol switch를 0으로 만듭니다. Transport header가 첫 fragment에 있는 저장 구조와 연결합니다.')],
      [('Writable과 COW', '공유 skb data를 바꾸기 전에 skb_try_make_writable을 호출하고 새 ip_hdr pointer를 얻습니다. Header pointer가 메모리 재배치 후에도 그대로라는 가정을 피합니다.'),
       ('원문의 한계', 'ICMP inner checksum 부분에는 Fix up the inner checksums라는 TODO 주석이 있습니다. 해당 branch가 모든 중첩 checksum을 완벽히 고친다고 설명하지 않습니다.')])

    lesson('TC Pedit·Masked Word 수정과 부분 실행', 'pedit', 'tcf_pedit_act',
      'Packet byte를 바꾸는 작업은 header 기준·가변 offset·정렬·mask 의미와 중간 오류 후 상태를 고려해야 합니다.',
      'Pedit는 writable 범위를 확보하고 key들을 순서대로 실행합니다. Header type에서 기준 offset을 얻고 필요하면 byte의 offmask/shift로 추가 offset을 계산합니다. 4byte word를 읽어 SET 또는 ADD 결과를 만들고 (old AND mask) XOR val로 저장합니다. 임시 buffer를 읽었다면 skb_store_bits로 반영합니다. 중간 bad는 overlimit을 증가시키지만 설정 action으로 반환합니다.',
      '격리된 namespace에서 tc pedit extended header mode·offset·mask와 후속 csum을 설정합니다. Mask의 보존 bit 의미를 U32 classifier의 비교 mask와 구분하고, 여러 key가 중간 오류 시 모두 rollback된다고 가정하지 않습니다.',
      'tcf_pedit_act의 offmask·offset%4·SET/ADD·bad와 done을 읽으세요.',
      [('old=0xabcd1234, mask=0xffff0000, SET val=0x00005678 결과는?', '0xabcd5678', '0x00005678', 'old&mask=0xabcd0000에 val을 XOR하면 0xabcd5678입니다. Mask로 선택한 old 부분을 남기는 연산입니다.'),
       ('두 번째 key에서 bad로 가면 첫 수정은 자동 rollback되는가?', '이 함수에는 전체 rollback 경로가 없다', '모든 수정 byte를 반드시 되돌린다', '순서대로 word를 쓰며 bad는 counter 후 done으로 갑니다. 설정 action 반환과 부분 실행을 함께 이해해야 합니다.')],
      [('비선형 Buffer', 'skb_header_pointer가 임시 hdata를 제공하면 수정한 값은 skb_store_bits로 원본에 기록해야 합니다. Stack buffer 변경만으로 packet이 수정되는 것은 아닙니다.'),
       ('Checksum 의무', 'Header word 변경 자체와 checksum 보정은 별도입니다. Pedit 뒤에 무엇을 csum해야 하는지 IP/transport field 및 offload 상태를 보고 결정하세요.')])

    lesson('TC Police·시간 Token과 초과 Verdict', 'police', 'tcf_police_act',
      '대역폭 초과를 판정하는 policing은 부족한 packet을 queue에서 기다리게 하는 shaping과 처리 방식이 다릅니다.',
      'Police는 EWMA·MTU 조건을 확인하고 현재 nanosecond 시간과 이전 시점 차이를 burst 상한까지 보충량으로 사용합니다. Byte-rate는 packet 길이를 전송 시간 비용으로, PPS-rate는 packet 한 개의 시간 비용으로 빼며 peak bucket도 별도 검사합니다. 모든 token이 nonnegative이면 상태를 commit하고 conforming result를 사용합니다. 부족하면 overlimit와 configured action을 반환합니다.',
      '격리된 namespace에서 tc police의 rate/burst/mtu와 conform/exceed action을 비교합니다. Byte와 nanosecond token 단위를 섞지 말고, 초과 verdict가 drop인지 재분류인지 설정을 읽습니다. 이 함수 안에 부족분 대기 queue가 있는 것은 아닙니다.',
      'tcf_police_act의 psched_l2t_ns·psched_pkt2t_ns·toks|ptoks|ppstoks를 읽으세요.',
      [('초과 packet은 이 함수에서 token을 기다리도록 항상 저장되는가?', 'overlimit와 설정 verdict로 나간다', '반드시 내부 대기 queue에 저장한다', 'Token이 부족하면 lock을 풀고 inc_overlimits로 갑니다. Shaping scheduler와 policing action의 처리 계약을 구분합니다.'),
       ('Token 하나가 음수이면 나머지가 충분해도 conform인가?', '모두 nonnegative 조건을 만족하지 못한다', 'Token의 합만 양수면 conform이다', '(toks|ptoks|ppstoks)>=0은 signed 값의 sign bit를 이용해 어느 bucket도 음수가 아닌지 검사합니다. 단순 합계 비교가 아닙니다.')],
      [('초과 상태 Commit', '새 token과 시간은 conforming branch에서 저장합니다. 실패마다 무조건 같은 상태 갱신을 수행하는 구현으로 설명하지 않습니다.'),
       ('Drop 통계', '초과 자체와 drop은 다릅니다. inc_drops에서 ret==SHOT일 때 drop count를 올리므로 conforming result가 SHOT인 구성도 source branch로 확인합니다.')])

    lesson('TC Sample·확률 추출과 PSample Metadata', 'sample', 'tcf_sample_act',
      '모든 traffic을 복제하지 않고 일부 관측 정보를 userspace에 전달하려면 확률·잘라낼 길이·방향 metadata가 필요합니다.',
      'PSample group이 있고 [0,rate) 난수가 0이면 packet sample을 보냅니다. Ingress/egress에 맞게 ifindex를 넣고 ingress의 필요한 MAC header를 잠시 push합니다. RCU로 cookie를 읽어 local buffer에 복사하고 truncate 설정으로 sample 크기를 정합니다. Sample 후 header를 복원하며 원래 흐름의 결과는 설정 action입니다.',
      '격리된 namespace에서 tc sample rate/group/trunc와 psample 수신 도구를 연결합니다. 기대 표본 수와 실제 개수를 비교하되 random sampling의 변동을 허용하고, sample 길이와 원래 packet 길이를 구분합니다.',
      'tcf_sample_act의 psample_group·random==0·trunc_size·push/pull을 읽으세요.',
      [('rate=100에서 1000개 packet의 기대 sample 수는?', '10개이며 실제 수는 변동한다', '정확히 10개로 고정된다', '각 추첨 선택 확률은 1/100이므로 기대값은 1000/100=10입니다. Deterministic 주기 선택이 아닙니다.'),
       ('Truncation은 원래 forwarding packet을 반드시 짧게 만드는가?', 'sample metadata의 전달 길이를 설정한다', '원본 payload를 반드시 잘라 보낸다', 'md.trunc_size를 psample_sample_packet에 넘깁니다. 원본 action 반환과 관측 copy의 범위를 구분합니다.')],
      [('Cookie 수명', 'RCU 안에서 cookie 내용을 local 배열로 복사합니다. 잠금 밖으로 원래 객체의 pointer만 전달하는 것과 내용 복사의 수명 차이를 읽습니다.'),
       ('통계의 대표성', 'Packet 단위 sampling은 byte 단위 분포와 같지 않습니다. 크기가 다른 packet이 섞이면 sampled packet 수에서 byte rate를 추정할 때 가정을 추가해야 합니다.')])

    lesson('TC Simple·Policy 문자열과 Packet Count', 'simple', 'tcf_simp_act',
      '가장 작은 관측 action을 읽으면 packet fast path에서 통계 갱신·출력·lock이 어떻게 연결되는지 알 수 있습니다.',
      'Simple action은 spinlock 안에서 last-use와 byte/packet 통계를 갱신하고 policy 문자열_누적packet수 형식으로 kernel log를 출력합니다. Lock을 풀고 설정 action을 반환합니다. 이것은 packet payload에 문자열을 추가하는 기능이 아니라 처리 경로를 관찰하는 action입니다.',
      '격리된 namespace의 적은 traffic에서 tc simple policy와 kernel log를 비교합니다. 매 packet 출력이 비용을 만들 수 있으므로 작은 동작 관찰에 사용하고 kernel log 접근 권한 및 설정한 control action을 확인합니다.',
      'tcf_simp_act의 spin_lock·bstats_update·pr_info·return을 읽으세요.',
      [('Policy가 hello이고 세 번째 packet이면 source의 출력 예시는?', 'simple: hello_3', '원본 packet payload에 hello를 삽입한다', '원문 주석의 예시와 pr_info 형식입니다. Kernel log 출력과 wire data 수정을 구분합니다.'),
       ('로그를 출력했다는 것이 반드시 packet 통과를 뜻하는가?', '반환은 별도의 설정 action이다', '출력하면 verdict는 언제나 OK다', '끝에서 d->tcf_action을 반환합니다. 관측 동작과 pipeline 제어 결과는 별도입니다.')],
      [('Count 시점', 'bstats_update 이후 packet count를 출력합니다. 갱신 전 값으로 출력하는 것과 차이가 있으므로 첫 packet·누적 값의 의미를 직접 따라가세요.'),
       ('Lock 안의 출력', '이 함수는 통계·문자열 접근과 출력을 lock 안에서 실행합니다. 빠른 packet 경로의 비용을 공부할 때 출력도 수행 작업으로 포함해야 합니다.')])

    lesson('TC SKBEdit·Local Metadata의 Mask 갱신', 'skbedit', 'tcf_skbedit_act',
      'Packet buffer의 priority·queue mapping·mark는 packet header와 구분되는 local 처리 정보입니다.',
      'Flag에 따라 skb priority를 직접 설정하거나 IP DS field를 두 bit 오른쪽으로 옮겨 DSCP를 상속합니다. Queue mapping은 device의 실제 queue 수 조건을 확인합니다. Mark는 기존값에서 mask bit만 지우고 새 mark의 mask bit를 넣어 나머지를 보존합니다. Packet type도 metadata로 갱신하며 header 확보 실패는 SHOT입니다.',
      '격리된 namespace에서 tc skbedit priority/mark/queue_mapping과 qdisc·driver의 소비 위치를 확인합니다. Mark가 네트워크로 전송되는 header라고 가정하지 않고 namespace/device queue capability 및 inherit 조건을 읽습니다.',
      'tcf_skbedit_act의 flags·real_num_tx_queues·mark mask·DS field>>2를 읽으세요.',
      [('old mark=0xaa00, mask=0x00ff, new mark=0x0033이면?', '0xaa33', '0x0033', 'old&~mask로 0xaa00을 보존하고 new&mask=0x33을 OR합니다. CTInfo의 전체 대입과 다른 식입니다.'),
       ('INHERITDSFIELD가 priority에 ECN 2bit를 그대로 포함하는가?', '두 bit shift하여 DSCP를 얻는다', 'DS field 8bit를 그대로 복사한다', 'IPv4/IPv6 DS field>>2입니다. 하위 ECN bit를 제외하고 서비스 등급에 해당하는 값으로 만듭니다.')],
      [('Queue 조건', 'Queue mapping을 설정해도 real_num_tx_queues보다 작은 설정인지 확인합니다. 존재하지 않는 TX queue 번호가 자동으로 새 queue를 만드는 것은 아닙니다.'),
       ('Header와 Metadata', 'skb->mark·priority·pkt_type 변경과 packet bytes 변경을 분리해 표시하세요. 후속 classifier가 무엇을 읽는지에 따라 효과가 달라집니다.')])

    lesson('TC SKBMod·Ethernet 수정과 ECN 표시', 'skbmod', 'tcf_skbmod_act',
      '정해진 Ethernet field 수정과 혼잡 표시를 범용 word 편집보다 명확한 동작 종류로 제공하는 경로입니다.',
      '초기화가 보장한 flag 종류에 따라 DMAC/SMAC/ETYPE 조합, SWAPMAC 또는 ECN을 처리합니다. ECN은 IPv4/IPv6에서만, 다른 수정은 Ethernet device에서만 진행합니다. 필요한 header 길이를 writable로 만든 후 field를 바꿉니다. MAC 교환은 임시 주소를 쓰며 실패는 overlimit 통계 후 SHOT입니다.',
      '격리된 namespace에서 tc skbmod dmac/smac/swapmac/ecn을 비교합니다. Device link type과 IP protocol 조건을 확인하고, ECN action은 source의 INET_ECN_set_ce 및 해당 helper의 ECT 조건까지 이어 읽습니다.',
      'tcf_skbmod_act의 flags 분기·ARPHRD_ETHER·tmpaddr·drop을 읽으세요.',
      [('ECN mode에서 비-IP protocol이면 무조건 drop하는가?', '수정하지 않고 설정 action으로 나간다', '항상 packet을 폐기한다', 'Protocol switch의 default는 out입니다. 적용 불가 skip과 writable 실패의 drop을 구분합니다.'),
       ('두 MAC 주소를 바꿀 때 임시 저장이 필요한 이유는?', '먼저 덮은 주소의 원래 값을 잃지 않기 위해', '항상 주소 길이를 두 배로 늘리기 위해', 'Destination을 tmpaddr에 보존하고 source→destination, tmp→source 순서로 교환합니다. 일반 swap 알고리즘의 실제 사용입니다.')],
      [('형식 검증과 실행', 'Fast path 주석은 init이 허용 flag 조합을 보장한다고 설명합니다. Runtime 분기만 읽지 말고 입력 policy가 만든 불변 조건을 연결합니다.'),
       ('통계 이름', '이 파일의 drop label은 overlimit을 증가시킨 뒤 SHOT을 반환합니다. 다른 action의 drop counter 호출과 같다고 추측하지 않고 실제 counter API를 읽습니다.')])

    lesson('TC Tunnel Key·Metadata Destination의 수명', 'tunnel_key', 'tunnel_key_act',
      'Collect-metadata tunnel에 encapsulation 정보를 전달하는 일과 실제 outer packet header를 만드는 일은 다른 단계입니다.',
      'Action은 RCU params를 읽고 RELEASE면 기존 skb destination을 drop합니다. SET도 기존 destination을 drop한 뒤 설정의 encapsulation metadata destination 참조를 clone하여 skb에 붙입니다. 이 함수는 metadata 관계를 설정하며 실제 tunnel 송신 처리가 이를 소비합니다. 잘못된 내부 action은 경고 후 설정 verdict를 반환합니다.',
      '격리된 namespace에서 metadata tunnel device와 tc tunnel_key set/unset·후속 redirect를 연결합니다. Tunnel endpoint·key·options 설정과 실제 encapsulation 수행 위치를 구분하고 dst 참조의 소유권을 추적합니다.',
      'tunnel_key_act의 skb_dst_drop·dst_clone·skb_dst_set을 읽으세요.',
      [('SET은 기존 destination을 그대로 유지한 채 두 개를 더하는가?', '기존 참조를 drop하고 새 metadata destination을 붙인다', '아무 해제 없이 list에 무한히 추가한다', 'SET case는 skb_dst_drop 후 skb_dst_set(dst_clone(...))입니다. 교체와 참조 증가의 순서를 읽습니다.'),
       ('이 함수가 SET에서 직접 outer UDP header를 작성하는가?', 'Metadata destination을 설정한다', '바로 UDP payload buffer를 조립한다', '본 함수의 작업은 skb dst와 metadata 참조입니다. 실제 tunnel 전송 경로의 encapsulation 단계와 연결해야 합니다.')],
      [('Dst 객체 종류', 'skb destination은 IP route만 담는 고정 구조라는 가정을 버립니다. Metadata destination을 tunnel 처리에 사용하며 소비자가 type과 mode를 해석합니다.'),
       ('참조 확보', 'dst_clone으로 설정 객체의 참조를 확보해 skb에 전달합니다. Action 설정이 교체되는 동안 packet이 사용하는 객체의 수명 문제를 확인하세요.')])

    lesson('TC VLAN Action·Hardware Tag와 Payload Tag', 'vlan', 'tcf_vlan_act',
      'VLAN 의미가 같아도 skb metadata와 packet byte 배열의 저장 형태가 달라 수정 경로가 나뉩니다.',
      'Action은 POP/PUSH/MODIFY 및 Ethernet header POP/PUSH를 수행합니다. MODIFY는 tag가 없으면 no-op입니다. Hardware tag면 값을 읽고 clear하고, payload tag면 pop하여 TCI를 얻습니다. VID는 교체하고 priority는 지정된 경우만 바꾸며 수정한 값을 hwaccel tag로 넣습니다. 성공은 ingress 위치를 복원하고 MAC 길이를 reset하며 helper 실패는 SHOT입니다.',
      '격리된 namespace에서 tc vlan push/pop/modify와 packet capture·offload tag 상태를 비교합니다. VID·priority·DEI bit를 분리하고 source의 no-op 조건 및 tag 표현이 바뀌는지 확인합니다.',
      'tcf_vlan_act의 skb_vlan_tagged·TCI mask·push_prio_exists·hwaccel put을 읽으세요.',
      [('Tag가 없는 packet에 MODIFY를 적용하면?', '수정 없이 out으로 간다', '반드시 새 VLAN tag를 push한다', '원문은 No-op if no vlan tag라고 명시하고 out으로 갑니다. PUSH와 MODIFY는 다른 계약입니다.'),
       ('MODIFY에서 priority를 지정하지 않으면 기존 priority는?', '기존 TCI priority bit를 유지한다', '언제나 0으로 지운다', 'Priority mask 갱신은 tcfv_push_prio_exists 조건 안에 있습니다. VID 교체와 priority 교체를 구분합니다.')],
      [('표현 변환', 'Payload VLAN에서 얻은 TCI도 수정 후 __vlan_hwaccel_put_tag로 넣습니다. 의미 보존과 byte 배열 위치 보존은 같은 요구가 아닙니다.'),
       ('Control과 VLAN 동작', 'p->tcfv_action은 push/pop 같은 편집 종류이고 v->tcf_action은 pipeline verdict입니다. 비슷한 이름의 두 action 값을 같은 enum으로 읽지 않습니다.')])
