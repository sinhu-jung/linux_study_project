"""Whole-file reserved-memory types, callback declarations and configuration stubs."""
ROWS = [dict(
    path='include/linux/of_reserved_mem.h', title='OF 예약 메모리 계약: 물리 구간과 장치 연결 callback',
    intro='두 구조체,초기화 함수 타입,선언 매크로와 모든 구성별 API를 분석합니다.',
    principle='물리 메모리 구간의 기술과 개별 장치에 그 구간을 연결하는 동작은 별도 계층입니다.',
    use='callback 테이블,opaque private data,선택 인덱스와 오류 반환을 학습합니다.',
    area='예약 메모리 · DMA · 장치 트리 · C 자료구조 · 구성',
    sections=[
        ('헤더와 예약 구간', 'GPL-2.0 guard에서 device.h와 of.h를 포함합니다. reserved_mem은 name,fdt_node,ops,phys_addr_t base와 size,void *priv를 보관합니다. base와 size는 물리 주소·크기 표현이며 priv는 구현별 문맥 포인터입니다. size가 있다는 이유로 구조체 뒤에 그 크기의 메모리가 자동 할당되는 것은 아닙니다. of_phandle_args와 reserved_mem_ops는 전방 선언됩니다.'),
        ('장치 callback과 초기화 타입', 'reserved_mem_ops는 rmem과 device를 받는 int device_init과 void device_release 함수 포인터를 갖습니다. reservedmem_of_init_fn은 rmem 하나를 받고 int를 반환하는 별도 함수 포인터 타입입니다. 예약 구간 자체의 초기화 callback과 장치별 연결 callback의 시그니처를 구분해야 합니다.'),
        ('구간 선언 매크로', 'CONFIG_OF_RESERVED_MEM이면 RESERVEDMEM_OF_DECLARE는 _OF_DECLARE에 reservedmem,name,compat,init과 reservedmem_of_init_fn을 전달합니다. 비활성일 때도 매크로를 단순 삭제하지 않고 같은 인수로 _OF_DECLARE_STUB를 사용합니다. 실제 링커 section이나 stub 확장 내용은 of.h에서 정의되므로 이 파일의 전달 코드만으로 상세 배치를 단정하지 않습니다.'),
        ('활성 API', 'init_by_idx는 device,node,정수 idx를 받고 init_by_name은 device,node,문자열 name을 받으며 둘 다 int입니다. device_release는 device만 받는 void 선언입니다. lookup은 device_node에서 reserved_mem *를 반환합니다. 이 헤더에는 검색 알고리즘,할당 또는 매핑 실행 본문이 없고 구현은 외부에 있습니다.'),
        ('비지원 구성', '비활성 inline 두 초기화 함수는 -ENOSYS를 반환합니다. release는 빈 함수,lookup은 NULL입니다. 앞서 다른 OF helper에서 보았던 -ENODEV와 같다고 추정하면 안 됩니다. 지원이 없는 상태를 성공값 0으로 숨기는 초기화 stub도 아닙니다.'),
        ('첫 구간 wrapper', 'of_reserved_mem_device_init은 CONFIG 분기 밖의 공통 inline입니다. dev,dev->of_node,0을 init_by_idx로 넘깁니다. 문서는 장치 노드의 memory-region 첫 항목에 따라 DMA-mapping operations를 연결한다고 설명합니다. 모든 memory-region 항목을 반복하는 함수가 아니며 dev=NULL을 별도로 방어하지 않습니다.'),
        ('범위와 한계', '구조체,callback typedef,선언 매크로의 두 구성,네 API와 공통 wrapper를 모두 대조했습니다. 비활성에서도 wrapper는 같은 호출을 하므로 하위 stub의 -ENOSYS가 전달됩니다. 실제 메모리 예약·DMA 접근·장치 해제 실험은 하지 않았습니다.')
    ], questions=[
        ('공통 device_init wrapper가 선택하는 구간 인덱스는?', '0', '모든 인덱스를 자동 순회한다', '호출 인수에 0이 고정되어 있습니다. memory-region 전체를 반복하는 코드가 아닙니다.'),
        ('예약 구간 초기화와 장치 초기화 callback의 인수가 같은가?', '아니다. 전자는 rmem 하나,후자는 rmem과 device다', '그렇다. 둘 다 void 인수다', 'reservedmem_of_init_fn과 reserved_mem_ops.device_init의 선언을 구분합니다.'),
        ('OF_RESERVED_MEM 비활성에서 init_by_name의 반환은?', '-ENOSYS', '항상 0', '해당 stub이 지원 부재 오류를 반환합니다. 다른 OF API의 -ENODEV와 혼동하지 않습니다.'),
        ('reserved_mem의 size 필드만 설정하면 메모리가 할당되는가?', '아니다. 구간을 기술하는 필드다', '그렇다. 구조체 대입이 자동으로 DMA 메모리를 할당한다', '자료 표현과 실행 동작을 구분해야 합니다. 헤더에 allocation 본문은 없습니다.')
    ]
)]
