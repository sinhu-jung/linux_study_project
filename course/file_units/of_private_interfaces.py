"""Whole-file OF internal declarations, conditional stubs and ownership contract."""
ROWS = [dict(
    path='drivers/of/of_private.h', title='OF 내부 인터페이스: 구성별 stub과 참조 없는 트리 접근',
    intro='전체 선언,alias 구조체,상수,거래 순회 매크로와 구성별 대체 구현을 분석합니다.',
    principle='지원하지 않는 구성의 stub은 같은 반환값을 사용하지 않으며 내부 조회에는 별도의 수명 보호 계약이 있습니다.',
    use='유연 배열,연결 리스트,잠금·참조 계약과 조건부 인터페이스를 학습합니다.',
    area='장치 트리 · C 인터페이스 · 자료구조 · 동시성 · 구성',
    sections=[
        ('기본 구조와 정렬', 'GPL-2.0+ include guard 헤더이며 FDT_ALIGN_SIZE=8을 정의합니다. alias_prop는 intrusive list_head link,alias 이름 포인터,대상 device_node 포인터,np의 식별과 별개인 정수 id,유연 배열 char stem[]을 갖습니다. 문서상 id는 alias 이름 끝의 번호이고 stem은 번호를 제외한 문자열입니다. stem은 독립 포인터 필드가 아니며 필요한 뒤쪽 저장소는 실제 할당부에서 확보해야 합니다.'),
        ('기본 cell 수와 전역 선언', 'SPARC에서는 root address cell 기본값이 2,나머지는 1이고 size cell 기본값은 항상 1입니다. of_mutex,raw spinlock devtree_lock,aliases_lookup,of_kset은 extern 선언입니다. 이 헤더가 잠금을 실제 획득하거나 저장소를 정의하는 것은 아닙니다. kunit을 전방 선언하고 of_root_kunit_skip도 선언합니다.'),
        ('동적 트리 인터페이스', 'OF_DYNAMIC이면 property_notify,node_release와 changeset apply_entries/apply_notify/revert_entries/revert_notify를 선언합니다. entries 함수의 int *ret_revert 또는 *ret_apply는 주 반환값 외 결과를 전달할 수 있는 형태입니다. 비활성 else에는 property_notify의 0 반환 stub만 있으며 나머지 선언 전체의 대체 구현을 제공하는 것은 아닙니다.'),
        ('플랫폼 알림과 sysfs', 'platform reconfig notifier 등록은 OF_DYNAMIC과 OF_ADDRESS 둘 다 있을 때 선언되고 아니면 빈 inline입니다. OF_KOBJ이면 attached 검사와 속성 add/remove/update,노드 attach/detach를 선언합니다. else에서는 add와 attach가 0,나머지 변경 함수는 빈 동작입니다. of_node_is_attached의 대체 stub은 이 else에 없습니다.'),
        ('Resolver·overlay 잠금·unittest', 'OF_RESOLVE이면 of_resolve_phandles를 선언하고 phandle cache 무효화 함수는 항상 선언합니다. OF_OVERLAY이면 overlay mutex lock/unlock을 선언하고 아니면 빈 inline입니다. unittest_unflatten_overlay_base는 OF_UNITTEST와 OF_OVERLAY 모두 있을 때 __init 선언이며 아니면 빈 stub입니다. 이름에 lock이 있어도 비지원 구성에서는 실제 잠금이 없다는 점이 중요합니다.'),
        ('Unflatten의 할당 callback', '__unflatten_device_tree는 blob,parent dad,결과 node 포인터의 주소,dt_alloc(size,align) 함수 포인터,detached bool을 받고 void *를 반환합니다. 메모리 할당 정책을 callback으로 전달하는 형태입니다. 실제 blob 검증·노드 생성·오류 회수 구현은 이 선언에 없으므로 전체 알고리즘을 여기서 추정하지 않습니다.'),
        ('Live tree 내부 함수 계약', 'General utilities 주석은 두 underscore로 시작하는 함수가 노드 참조를 얻지 않으므로 devtree lock을 보유하거나 detached tree에서만 작업하라고 명시합니다. 이 주석과 함께 prop_dup/free,node_dup,두 path 검색,get/add/remove/update property,detach 등의 선언이 있습니다. 내부 borrowed 접근의 수명을 호출자가 보호해야 한다는 계약이며 자동 참조 획득을 가정하면 안 됩니다.'),
        ('Property 출력 인수와 sysfs 선언', '__of_get_property는 lenp를 통해 길이를 전달할 수 있고 __of_update_property는 struct property **oldprop로 이전 속성을 돌려줄 수 있습니다. sysfs update 선언의 oldprop 단일 포인터와 타입이 다릅니다. __of_sysfs_remove_bin_file도 별도 선언됩니다. double pointer가 모든 객체를 깊은 복사한다는 의미는 아닙니다.'),
        ('Phandle sentinel과 순회', 'OF_PHANDLE_ILLEGAL은 해결되지 않은 경우에 쓰는 0xdeadbeef입니다. for_each_transaction_entry는 te_list를 node 멤버로 정방향 list_for_each_entry하고 reverse 버전은 역방향 순회합니다. 매크로가 거래를 적용·취소하거나 삭제 안전 순회를 자동 보장하는 것은 아닙니다. 실제 반복문 본문과 수명 관리는 호출부 책임입니다.'),
        ('주소·IRQ·DMA 계약', 'bus address/size cell 수 함수와 IRQ imap parent 파서를 선언합니다. bus_dma_region을 전방 선언하고 OF_ADDRESS와 HAS_DMA가 모두 있을 때 DMA range와 DMA parent 함수를 선언합니다. 아니면 of_dma_get_range는 -ENODEV를 반환하며 출력 map을 쓰지 않습니다. 대체 __of_get_dma_parent는 of_get_parent(np)를 호출합니다. 일반적인 내부 함수 주석만으로 이 구체적 wrapper의 반환 참조 의미를 무시하면 안 됩니다.'),
        ('FDT 나머지 선언과 포함 의존', '마지막은 reserved memory scan의 int 반환,init의 void 반환,blob과 node를 받는 device available bool 선언입니다. 헤더에는 직접 include가 없으며 list_head,gfp_t,phandle 등 타입과 helper가 미리 보이는 포함 문맥에 의존합니다. 모든 전방 선언·타입 정의를 자체 제공하는 독립 헤더라고 단정하지 않습니다.'),
        ('전체 범위와 검증', '구조체,상수,전역·함수 선언,각 CONFIG 분기와 모든 stub,두 순회 매크로를 대조했습니다. 0 반환 stub은 실제 sysfs 부착 성공의 증거가 아니고 -ENODEV stub은 map 초기화의 증거가 아닙니다. 실제 구성별 컴파일이나 동적 트리 동시성 실험은 실행하지 않았습니다.')
    ], questions=[
        ('alias_prop의 stem은 별도 할당 포인터인가?', '아니다. 구조체 끝의 유연 배열이다', '그렇다. char *stem으로 선언되어 있다', 'char stem[]은 뒤쪽 저장소 배치를 사용하는 패턴입니다. 포인터 필드와 메모리 레이아웃이 다릅니다.'),
        ('OF_KOBJ 비활성에서 attach stub의 0 반환은 sysfs 노드가 실제 생성되었음을 뜻하는가?', '아니다. stub은 작업 없이 0을 반환한다', '그렇다. 모든 구성에서 kobject_add가 실행된다', '반환값과 실제 부작용을 함께 봐야 합니다. 구성별 대체 함수는 동작을 생략합니다.'),
        ('내부 live tree 조회의 수명 보호 계약은?', 'devtree lock을 보유하거나 detached tree에서 작업한다', '모든 함수가 자동으로 영구 참조를 얻는다', '주석은 두 underscore 내부 함수의 참조 없는 접근을 명시합니다. 실제 wrapper의 별도 호출 계약도 함께 확인해야 합니다.'),
        ('DMA range 비지원 stub이 출력 map을 NULL로 초기화하는가?', '아니다. -ENODEV만 반환한다', '그렇다. 모든 출력 인수를 자동으로 지운다', '본문에는 map 대입이 없습니다. 오류 반환 시 출력값의 유효성을 추정해서는 안 됩니다.'),
        ('거래 reverse 매크로가 rollback까지 수행하는가?', '아니다. 연결 리스트 순회 방향만 바꾼다', '그렇다. 각 거래를 자동 취소한다', '매크로 확장은 list_for_each_entry_reverse입니다. 반복문의 작업은 호출자가 작성합니다.'),
        ('OF_DYNAMIC 비활성 else에 node_release와 모든 changeset 함수 stub이 있는가?', '아니다. property_notify의 0 반환 stub만 있다', '그렇다. 모든 선언을 똑같이 대체한다', '각 CONFIG 블록의 실제 else 내용을 끝까지 읽어야 합니다. 비지원 구성이 항상 같은 API 집합을 노출하지는 않습니다.')
    ]
)]
