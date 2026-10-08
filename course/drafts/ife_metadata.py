"""IFE container and three independently reviewed metadata modules."""
def register(topic,q,detail):
    topic('IFE TLV·길이·Padding·Byte Order','네트워크','net/ife/ife.c','ife_tlv_meta_decode',
      '구조체를 전송 형식으로 바꾸려면 byte order뿐 아니라 header 포함 길이와 alignment를 검증해야 합니다.',
      'IFE TLV는 network-order u16 type·u16 length와 value입니다. Length는 TLV header를 포함하지만 padding은 포함하지 않습니다. Decode는 최소 header·최소 length·align overflow·전체 metadata 끝을 검사한 뒤 value 길이를 header 제외 값으로 돌려줍니다. Next는 aligned length만큼 이동합니다. Encode는 총 공간의 padding을 0으로 만들고 network-order header와 caller가 변환한 value를 복사합니다.',
      '고정 v6.12의 ife_tlv_meta_encode/decode/next를 연결해 읽고 value 2byte와 4byte의 length 및 allocation 크기를 손으로 계산합니다. Value 자체의 endian 변환 책임은 caller에 있다는 source 주석을 확인하고 외부 length로 pointer를 무조건 이동하지 않습니다.',
      'ife_tlv_meta_decode·__ife_tlv_meta_valid·ife_tlv_meta_next·ife_tlv_meta_encode를 읽으세요.',
      q('Value=2byte, header=4byte, alignment=4이면 TLV length와 공간은?','length=6, aligned 공간=8','length=8, 공간=6','Header 포함 의미 길이는 4+2=6이고 NLA alignment로 8byte를 씁니다. Decoder가 받는 dlen에는 padding이 들어가지 않습니다.'),
      q('Generic TLV encode가 caller의 u32 value를 자동 htonl하는가?','caller가 value를 network order로 준비한다','모든 value를 무조건 u32로 변환한다','Source 주석은 Caller takes care of presenting data in network order입니다. Generic encoder는 dval byte를 복사하며 type별 helper가 변환합니다.'),
      details=[detail('전체 IFE Header','ife_encode는 COW headroom을 확보하고 outer Ethernet header와 metadata 총 길이를 더합니다. ife_decode는 총 길이가 최소 2byte인지 확인하고 pskb_may_pull로 해당 범위를 확보한 뒤 skb 위치를 이동합니다.'),detail('Overflow와 끝 위치','최소 길이만 맞아도 충분하지 않습니다. NLA_ALIGN 결과가 원래 길이보다 작아지는 overflow와 aligned 항목이 container 끝을 넘는지도 검사합니다.'),detail('선언과 Export','ifeheadr의 flexible array는 TLV 시작을 나타내고 meta_tlvhdr는 두 u16 field입니다. 각 helper의 GPL export와 module 선언은 다른 kernel 모듈이 이 직렬화 API를 호출하도록 연결합니다.')])
    topic('IFE SKBMark·32bit 표식 직렬화','트래픽 제어 알고리즘','net/sched/act_meta_mark.c','skbmark_decode',
      'Local packet mark를 IFE field로 전송하고 복원할 때 mark의 의미·폭·network byte order를 명시해야 합니다.',
      'SKBMark plugin은 IFE_META_SKBMARK와 NLA_U32로 등록됩니다. Presence는 skb mark 또는 설정한 metaval을 확인합니다. Encode helper는 override가 있으면 그것을 사용하고 값이 0이면 encode하지 않으며 htonl 후 TLV로 만듭니다. Decode는 network-order u32를 ntohl하여 skb->mark에 전체 대입합니다. Mask merge 기능은 이 decode 함수에 없습니다.',
      '격리된 IFE namespace 실습에서 mark의 allow/use 설정·override·값 0과 수신 mark를 비교합니다. Config의 u32 길이 검증과 수신 TLV 범위 검증을 따로 읽으며 local mark를 그대로 믿을 수 있는 보안 identity로 사용하지 않습니다.',
      'skbmark_encode/decode/check와 ife_skbmark_ops·ife_encode_meta_u32를 읽으세요.',
      q('Mark decode는 기존 mark와 OR해 보존하는가?','ntohl 결과를 전체 대입한다','항상 이전 mark의 모든 bit를 남긴다','skb->mark=ntohl(ifemark)입니다. SKBEdit의 masked 갱신과 별도의 계약입니다.'),
      q('설정 override가 없고 skb mark=0이면 u32 encode helper는?','0을 반환하여 encode하지 않는다','항상 8byte zero TLV를 만든다','ife_encode_meta_u32는 !edata에서 return 0입니다. Presence 계산과 실제 zero override 출력 길이도 함께 확인합니다.'),
      details=[detail('전체 Plugin 파일','encode는 skb mark를 공용 helper로 전달하고 check도 공용 presence helper를 씁니다. Ops는 get·alloc·release·validate와 THIS_MODULE owner를 연결합니다. Init은 register_ife_op, exit은 unregister_ife_op이며 module license·description·alias가 로딩을 연결합니다.'),detail('Validation 경계','설정용 u32 validate helper는 len==sizeof(u32)일 때만 성공합니다. 수신 skbmark_decode는 len을 검사하지 않고 u32를 읽으며 find_decode_metaid도 decode를 직접 호출합니다. Generic TLV 경계 검사가 각 type의 value 폭 4byte까지 자동 보장하는 검사라고 설명하지 않습니다. 설정 검증과 수신 value 검증은 서로 다른 경계입니다.')])
    topic('IFE Priority·정책 값과 U32 Metadata','트래픽 제어 알고리즘','net/sched/act_meta_skbprio.c','skbprio_decode',
      'Priority를 전송하더라도 원격 scheduler가 그 숫자를 어떤 class나 queue로 해석하는지는 별도 정책입니다.',
      'Priority plugin은 skb->priority를 u32 encode/check helper에 전달하고 IFE_META_PRIO·NLA_U32로 등록됩니다. Decode는 network-order 값을 ntohl하여 skb priority에 대입합니다. Config get/alloc은 u32 공용 helper를 사용하며 이 ops에는 release/validate pointer가 직접 없어서 등록 및 metatype 경로의 기본 처리를 따라야 합니다.',
      '격리된 IFE namespace에서 송신 priority와 수신 metadata를 비교하고 수신 qdisc의 priority 해석을 확인합니다. Priority 숫자와 DSCP header·802.1p VLAN priority가 자동으로 동일해지는 것은 아니므로 소비 경로를 이어 읽습니다.',
      'skbprio_check/encode/decode·ife_prio_ops와 register_ife_op 기본 release를 읽으세요.',
      q('Priority를 decode하면 DSCP header도 이 함수에서 직접 바뀌는가?','skb->priority metadata를 대입한다','항상 IPv4 DSCP를 같은 숫자로 쓴다','이 함수는 skb priority만 갱신합니다. DS field 변경을 수행하는 CTInfo나 다른 header action과 구분합니다.'),
      q('Ops에 release가 없으면 register_ife_op는 어떻게 보완하는가?','공용 ife_release_meta_gen을 넣는다','필수적으로 모든 등록을 거부한다','register_ife_op는 release가 NULL이면 기본 release를 설정합니다. Required callback 검사와 optional callback 기본값은 다릅니다.'),
      details=[detail('전체 파일의 연결','check·encode·decode 세 함수가 priority 값과 u32 helper를 연결합니다. Ops의 get·alloc·owner와 metaid·metatype·name·synopsis, module init/exit의 등록·해제 및 alias까지 파일 전체 역할을 따라 읽습니다.'),detail('설정 메모리','공용 alloc은 kmemdup으로 override 값을 복사하고 기본 release는 kfree합니다. Userspace 설정 buffer의 pointer를 영구 보관하는 것과 소유한 복사본의 수명이 다릅니다.')])
    topic('IFE TCIndex·16bit 값과 Padding 분리','트래픽 제어 알고리즘','net/sched/act_meta_skbtcindex.c','skbtcindex_decode',
      '16bit metadata도 4byte alignment를 사용하므로 값의 폭과 wire 공간을 구분하는 작은 사례입니다.',
      'TCIndex plugin은 skb tc_index를 IFE_META_TCINDEX·NLA_U16으로 연결합니다. Encode는 u16 공용 helper에서 htons하고 2byte value를 TLV에 넣습니다. Decode는 u16을 읽어 ntohs하여 tc_index에 대입합니다. Validate는 padding을 포함하지 않은 value 길이 2byte를 요구하지만 presence helper의 총 공간은 header와 padding을 포함해 8byte입니다.',
      '격리된 IFE 실습이나 고정 원본에서 tc_index value 0x1234의 network byte 12 34와 TLV length 6, aligned 공간 8을 계산합니다. skb tc_index라는 metadata와 tc classifier의 classid를 동일한 폭·기능으로 가정하지 않습니다.',
      'skbtcindex_encode/decode/check·ife_skbtcindex_ops·ife_validate_meta_u16을 읽으세요.',
      q('U16 value 검증 len은 padding 포함 4인가?','실제 value 길이 2다','항상 alignment 길이 4다','ife_validate_meta_u16은 sizeof(u16)과 비교하며 주석은 length will not include padding이라고 설명합니다.'),
      q('TCIndex plugin의 NLA_U16과 SKBMark의 NLA_U32가 같은 field 폭인가?','각각 16bit와 32bit다','둘 다 반드시 64bit다','두 ops의 metatype과 공용 helper 종류가 다릅니다. 총 TLV 공간 8byte가 같아도 값의 폭은 다릅니다.'),
      details=[detail('전체 Plugin 파일','encode·decode·check는 u16 helper와 tc_index를 연결합니다. Ops는 u16 get/alloc/validate 및 공용 release와 owner를 지정하고 module init/exit에서 등록/해제합니다. Description·license·module alias는 plugin 검색·로딩 정보를 제공합니다.'),detail('C 읽기','*(u16 *)data는 pointer를 u16 pointer로 해석하여 그 값을 읽습니다. 안전한 호출을 위해 길이·정렬·유효 범위가 앞 단계에서 어떻게 확보되는지 확인해야 하며 임의 byte buffer에 무조건 적용하는 예제로 쓰지 않습니다.')])
