"""Whole-file OF DMA controller/router API and disabled configuration forms."""
ROWS = [dict(
    path='include/linux/of_dma.h', title='OF DMA 계약: 채널 변환과 라우팅,오류 포인터와 NULL',
    intro='두 자료구조,컨트롤러·라우터 등록과 채널 조회 API의 모든 구성 분기를 분석합니다.',
    principle='callback의 부재,채널 검색 실패,기능 미지원 오류는 같은 포인터 값으로 표현되지 않을 수 있습니다.',
    use='intrusive 리스트,함수 포인터,opaque context와 조건부 매크로를 학습합니다.',
    area='DMA engine · 장치 트리 · callback · 오류 표현 · 구성',
    sections=[
        ('헤더와 컨트롤러 구조', 'GPL-2.0 guard 안에서 of.h와 dmaengine.h를 포함합니다. of_dma는 컨트롤러 목록용 list_head,of_node,채널 변환 callback,route 할당 callback,dma_router 포인터,void *of_dma_data를 갖습니다. 리스트 링크를 객체 내부에 두는 intrusive 구조이며 이 선언만으로 컨트롤러를 목록에 추가하지는 않습니다.'),
        ('두 callback의 반환 타입', 'of_dma_xlate는 of_phandle_args와 of_dma를 받아 dma_chan *를 반환합니다. of_dma_route_allocate는 같은 형태의 인수로 void *를 반환합니다. route 문맥과 실제 DMA channel을 동일 타입 객체로 보아서는 안 됩니다. of_dma_data는 구현별 데이터를 담는 포인터이며 헤더는 그 메모리를 직접 할당하지 않습니다.'),
        ('필터 정보', 'of_dma_filter_info는 dma_cap_mask_t dma_cap과 dma_filter_fn filter_fn을 묶습니다. capability 집합과 선택 callback을 함께 전달할 수 있는 구조입니다. 실제 마스크 연산이나 필터 검색 루프는 이 파일에 없으며 각 비트의 의미는 dmaengine 정의와 구현에서 확인해야 합니다.'),
        ('활성 등록 인터페이스', 'CONFIG_DMA_OF이면 controller_register는 node,xlate callback,data를 받아 int를 반환하고 controller_free는 node를 받습니다. router_register는 node,route callback,dma_router를 받습니다. router_free는 별도 함수 본문이 아니라 controller_free 이름으로 치환하는 매크로입니다. 양쪽 구성 모두 같은 alias를 제공합니다.'),
        ('활성 채널 조회', 'request_slave_channel은 node와 name으로 dma_chan *를 반환하는 외부 선언입니다. simple_xlate와 xlate_by_chan_id는 dma_spec,ofdma를 받는 채널 변환 함수 선언입니다. 이 헤더만으로 채널 선택 알고리즘,phandle 인수 개수 검사나 성공 시 참조 소유권의 세부 내용을 확정할 수 없습니다.'),
        ('비활성 등록과 요청', 'CONFIG_DMA_OF 비활성에서 controller_register와 router_register는 -ENODEV,controller_free는 빈 동작입니다. request_slave_channel은 NULL이 아니라 ERR_PTR(-ENODEV)를 반환합니다. 따라서 결과를 NULL로만 확인해 유효 채널처럼 역참조하면 안 됩니다. 어떤 API의 포인터 실패 표현인지 구분해야 합니다.'),
        ('비활성 변환의 서로 다른 형태', 'simple_xlate는 호출 가능한 inline 함수로 남아 NULL을 반환합니다. 반면 xlate_by_chan_id는 함수가 아니라 NULL 매크로로 정의됩니다. callback 필드에 이 이름을 넣으면 부재 포인터가 되며 비활성 구성에서 이를 직접 함수처럼 호출할 수 있다고 가정하면 안 됩니다.'),
        ('전체 범위와 검증', 'guard,include,두 구조체,활성 선언과 모든 비활성 stub·alias를 대조했습니다. DMA controller 등록이나 채널 요청은 실제 전송을 수행하는 것과도 별개입니다. 실제 하드웨어 라우팅·DMA 전송·구성별 컴파일 실험은 하지 않았습니다.')
    ], questions=[
        ('비활성 request_slave_channel의 반환은?', 'ERR_PTR(-ENODEV)', '항상 NULL', '오류 포인터를 사용하므로 단순 NULL 검사만으로 실패를 분류할 수 없습니다.'),
        ('비활성 xlate_by_chan_id는 어떤 형태인가?', 'NULL로 정의된 매크로', '항상 호출 가능한 빈 함수', 'simple_xlate의 NULL 반환 inline과 다릅니다. callback 부재 표현과 함수의 반환값을 구분합니다.'),
        ('router_free는 별도 구현 함수인가?', '아니다. controller_free로 치환되는 이름이다', '그렇다. 이 헤더에 독립 해제 알고리즘이 있다', '두 구성 모두 #define alias를 사용합니다. 호출 인터페이스 이름과 실제 구현 이름은 다를 수 있습니다.'),
        ('route_allocate와 xlate의 반환 타입은 같은가?', '아니다. void *와 dma_chan *다', '그렇다. 둘 다 int 상태값이다', '같은 인수 형태라도 반환 대상의 의미는 다릅니다. 자료구조의 함수 포인터 선언을 정확히 읽어야 합니다.')
    ]
)]
