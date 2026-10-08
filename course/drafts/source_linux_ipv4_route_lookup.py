"""IPv4 route next-hop eligibility and trie backtracking."""
ROWS = [('IPv4 다음 홉 검사: DEAD·LINKDOWN·출력 인터페이스는 다른 조건',
  '네트워크',
  'net/ipv4/fib_trie.c',
  'fib_lookup_good_nhc',
  '목적지 prefix가 맞아도 사용할 수 없는 다음 홉이면 패킷을 내보낼 경로로 선택하면 안 됩니다. 반대로 링크 상태를 무시하라는 검색 정책이 있어도 죽은 경로 표시나 출력 인터페이스 지정까지 모두 '
  '무시하면 잘못된 결과가 됩니다.',
  'fib_lookup_good_nhc는 RTNH_F_DEAD가 있으면 먼저 false입니다. 다음은 ip_ignore_linkdown이 참이고 RTNH_F_LINKDOWN이 있고 검색 flags에 '
  'FIB_LOOKUP_IGNORE_LINKSTATE가 없을 때 false입니다. 마지막으로 요청 flowi4_oif가 0이 아니면서 다음 홉의 nhc_oif와 다르면 false이고, 나머지는 '
  'true입니다. 각 거절 사유가 별도 조건문입니다.',
  'LINKDOWN 표시가 있어도 링크 무시 정책이 꺼져 있거나 검색이 IGNORE_LINKSTATE를 지정하면 그 분기는 통과할 수 있습니다. 그러나 DEAD까지 동시에 있으면 첫 분기에서 이미 '
  'false입니다. 요청 oif=3이고 다음 홉 oif=4이면 링크 상태와 무관하게 false입니다. oif=0이면 특정 출력 인터페이스 제한을 걸지 않습니다.',
  '왜 true가 실제 패킷 전송 성공은 아닌가',
  '이 helper는 후보의 세 가지 조건만 검사합니다. 주소 해석, 이웃 테이블, 실제 장치 큐, 패킷 전송은 이 본문에 없습니다. true는 이 단계에서 적합하다는 의미입니다. 로컬 검색 정책을 '
  '실제 장치 링크를 강제로 올리거나 사라진 장치를 되살리는 기능으로 이해하면 안 됩니다.',
  ('IGNORE_LINKSTATE가 있고 DEAD도 있으면 통과하나요?',
   '아닙니다. DEAD 검사에서 false입니다.',
   '그렇습니다. 모든 경로 상태를 무시합니다.',
   '검색 flag는 LINKDOWN 조건 안에서만 검사하며 앞선 DEAD 거절은 별개입니다.'),
  ('flowi4_oif=0이면 nhc_oif도 반드시 0이어야 하나요?',
   '아닙니다. 출력 인터페이스 불일치 검사를 제한하지 않습니다.',
   '그렇습니다. 두 필드는 항상 같아야 합니다.',
   '불일치 조건은 flp->flowi4_oif가 참인 경우에만 적용합니다.')),
 ('IPv4 trie 검색: 더 긴 prefix 실패 후 되돌아가는 과정',
  '네트워크',
  'net/ipv4/fib_trie.c',
  'fib_table_lookup',
  '목적지 주소에 더 구체적으로 맞는 경로를 먼저 시도하되, 그 후보가 없거나 정책상 사용할 수 없다면 더 넓은 경로를 찾아야 합니다. 압축 trie는 공통 prefix와 여러 비트의 분기를 묶어 '
  '주소마다 거대한 배열을 만드는 비용을 피합니다.',
  'fib_table_lookup은 RCU 읽기 잠금을 가진 호출자를 요구합니다. 목적지 주소를 ntohl로 key로 바꾸고 get_cindex의 XOR와 shift로 자식 인덱스를 구합니다. '
  'index가 1ul<<bits 이상이면 건너뛴 prefix 비트 불일치가 포함된 것으로 처리합니다. leaf 도달 후 alias의 prefix 범위·DSCP·dead·scope와 다음 홉 조건을 '
  '검사합니다. 의미상 쓸 수 없는 후보는 다음 후보 또는 backtrace로 갑니다. backtrace는 cindex가 0이면 부모로 올라가고 그렇지 않으면 cindex &= cindex-1로 최하위 '
  '1비트를 지워 다음 후보 자식을 찾습니다.',
  '되돌아가기 인덱스가 이진수 1100이면 cindex-1=1011이고 AND 결과는 1000입니다. 다음에는 1000&0111=0000입니다. 이것은 모든 인덱스를 하나씩 감소시키는 것과 다릅니다. '
  '0이 되면 부모 후보로 올라가는 경로가 필요합니다. trie 끝까지 후보가 없으면 -EAGAIN이며 곧바로 네트워크 전체에 경로가 없다는 최종 판정으로 확대하면 안 됩니다.',
  '왜 leaf를 찾았어도 검색이 끝나지 않나',
  '같은 leaf에도 alias 목록과 경로 정책이 있습니다. 일부 경로 타입은 fib_props의 음수 오류를 즉시 반환하며, 단순 후보 불일치처럼 항상 다른 경로로 계속 가는 것은 아닙니다. 성공 '
  '시 prefix·prefixlen·next hop·table 등 결과 필드를 쓰고 FIB_LOOKUP_NOREF가 없으면 fib_info 참조 수도 증가시킵니다. 이 flag가 있어도 RCU 호출 '
  '계약이 사라지지 않습니다. prefix 길이는 KEYLENGTH-fa_slen이며 prefix 자체는 htonl로 저장합니다.',
  ('cindex=12에서 cindex &= cindex-1의 결과는?', '8입니다.', '11입니다.', '1100과 1011을 AND하면 1000입니다. 대입은 단순 뺄셈이 아닙니다.'),
  ('leaf에 도착하면 어떤 alias든 바로 성공하나요?',
   '아닙니다. alias 조건과 다음 홉 등 의미 검사가 남습니다.',
   '그렇습니다. 주소 비트만 맞으면 모든 정책을 생략합니다.',
   '본문은 found 뒤 hlist를 순회하며 prefix 범위, DSCP, dead, scope, 경로 타입 및 다음 홉을 검사합니다.'))]

def register(topic,q,detail):
    for title,area,path,symbol,why,principle,use,dt,body,qa,qb in ROWS:
        topic(title,area,path,symbol,why,principle,use,"비트 계산, 경로 정책, 참조 수명을 각각 원문 조건에 맞춰 해석하세요.",q(title+" · "+qa[0],*qa[1:]),q(title+" · "+qb[0],*qb[1:]),details=[detail(dt,body),detail("검토 범위","v6.12 fib_table_lookup 본문과 next-hop helper, get_cindex 정의를 대조했습니다. 실제 네트워크 경로 변경을 수행한 실험은 아닙니다.")])
