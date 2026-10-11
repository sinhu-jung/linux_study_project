"""Whole-file clock helpers and SKB resource ownership."""
ROWS = [dict(
    path='include/kunit/skbuff.h', title='KUnit SKB 관리: padding과 논리적 길이, 오류 시 소유권',
    intro='해제 action,zero allocation helper와 조기 해제 helper 전체를 분석합니다.',
    principle='버퍼 용량과 유효 데이터 길이는 다르며,실패한 하위 함수가 이미 객체를 해제할 수 있습니다.',
    use='short circuit,오류 보상,미사용 인수와 패킷 버퍼 수명을 학습합니다.',
    area='네트워크 버퍼 · 메모리 소유권 · callback · API 계약',
    sections=[
        ('구성과 action', 'GPL-2.0 guard 안에서 KUnit resource와 linux/skbuff.h를 포함합니다. static kunit_action_kfree_skb는 void *를 sk_buff *로 변환하여 kfree_skb를 호출합니다. 테스트 cleanup API와 패킷 버퍼 해제 함수의 인수 타입을 연결하는 adapter입니다.'),
        ('실제 할당 flags', 'kunit_zalloc_skb는 test,int len,gfp_t gfp를 받지만 alloc_skb(len,GFP_KERNEL)을 호출합니다. gfp 인수는 본문에서 사용하지 않으며 문서도 GFP_KERNEL 할당이라고 설명합니다. 따라서 GFP_ATOMIC을 인수로 전달했다고 비수면 할당이 보장되지 않습니다. len의 음수를 별도로 검사하는 코드도 없습니다.'),
        ('Padding과 길이', '할당 후 skb_pad(res,len)을 호출해 padding 영역을 0으로 채웁니다. 교차 확인한 __skb_pad는 data+skb->len에서 memset하고 논리적 len을 늘리는 skb_put을 호출하지 않습니다. 따라서 이 helper를 len바이트 payload를 추가하는 함수라고 설명하면 안 됩니다. 용량 확보·영역 초기화와 유효 데이터 길이 갱신을 구분합니다.'),
        ('두 실패 경로의 소유권', '!res || skb_pad(res,len)은 단락 평가이므로 할당 실패 시 padding을 호출하지 않습니다. skb_pad 실패는 NULL을 반환하는데 하위 helper가 free_on_error=true로 SKB를 해제하므로 여기서 다시 kfree_skb를 하지 않습니다. 이어 add_action_or_reset 실패는 action이 즉시 해제하고 NULL을 반환합니다. 성공 시에만 관리되는 res를 반환합니다.'),
        ('조기 해제', 'kunit_kfree_skb는 skb=NULL이면 바로 반환하고 그 밖에는 동일 action과 skb 포인터로 kunit_release_action을 호출합니다. 직접 kfree_skb만 호출하는 방식과 달리 예약된 action을 소비하여 테스트 종료 때 같은 등록이 다시 실행되지 않게 합니다. 이 API는 해당 test에서 관리하는 SKB에 사용해야 하며 일반 미등록 SKB까지 무조건 해제한다고 가정하면 안 됩니다.'),
        ('범위와 한계', 'SPDX,guard,include,action,두 inline helper와 문서를 모두 대조했습니다. padding의 오류 해제와 길이 동작을 다른 소스에서 교차 확인했지만 그 파일 전체를 완료로 세지 않습니다. 실제 네트워크 송신이나 할당 실패 주입을 실행하지 않았습니다.')
    ], questions=[
        ('gfp=GFP_ATOMIC을 넘기면 실제 alloc_skb도 그 값을 쓰는가?', '아니다. 본문은 GFP_KERNEL을 고정 사용한다', '그렇다. 모든 gfp 인수가 자동 전달된다', '인수 이름과 실제 호출 인수를 따로 확인해야 합니다. 이 버전에서 gfp는 미사용입니다.'),
        ('skb_pad 실패 뒤 helper가 다시 kfree_skb하지 않는 이유는?', 'skb_pad가 오류 시 이미 SKB를 해제하기 때문이다', '실패한 SKB를 영구적으로 보관하기 때문이다', 'skb_pad는 __skb_pad의 free_on_error를 true로 지정합니다. 소유권을 잃은 포인터를 다시 해제하면 안 됩니다.'),
        ('Zero padding을 하면 논리적 payload 길이도 len만큼 늘어나는가?', '아니다. padding과 skb_put에 의한 길이 증가는 다르다', '그렇다. 모든 memset이 skb->len을 자동 변경한다', '하위 구현은 data+현재 길이에 0을 쓰며 길이 증가 명령이 없습니다.'),
        ('관리 SKB의 조기 해제에 release_action을 쓰는 이유는?', '예약된 cleanup을 실행하고 해당 등록의 재실행을 막기 위해서다', '패킷을 네트워크로 즉시 전송하기 위해서다', '직접 해제만 하면 남은 cleanup 등록과 충돌할 수 있습니다. 이 helper는 자원 관리 계층을 통해 정리합니다.')
    ]
), dict(
    path='include/kunit/clk.h', title='KUnit 클록 API 선언: consumer와 provider 작업 구분',
    intro='전방 선언과 일곱 API 선언 전체를 분석합니다.',
    principle='클록 소비자 핸들 획득,활성화,하드웨어 등록은 서로 다른 작업입니다.',
    use='포인터 반환과 상태 반환,opaque type,장치 트리 경로를 구분합니다.',
    area='클록 · C 인터페이스 · 자원 수명',
    sections=[
        ('헤더와 타입', 'GPL-2.0 _CLK_KUNIT_H guard 안에 clk,clk_hw,device,device_node,kunit 다섯 구조체를 전방 선언합니다. include나 구조체 본문은 없으며 포인터로만 사용하는 타입의 내부 정의를 요구하지 않는 인터페이스입니다.'),
        ('네 consumer 반환 선언', 'clk_get_kunit은 device와 con_id,of_clk_get_kunit은 device_node와 index,clk_hw_get_clk_kunit은 hw와 con_id로 clk *를 반환합니다. clk_hw_get_clk_prepared_enabled_kunit도 hw와 con_id를 받아 획득과 준비·활성화를 합칩니다. 모든 함수는 test 문맥을 받습니다.'),
        ('세 상태 반환 선언', 'clk_prepare_enable_kunit은 clk *를 활성화하는 int 반환 함수입니다. clk_hw_register_kunit은 device와 hw,of_clk_hw_register_kunit은 device_node와 hw로 provider 하드웨어 등록을 수행하는 int 반환 선언입니다. 헤더에는 unregister helper나 비활성 CONFIG stub이 없으며 실제 cleanup 계약은 구현에서 확인합니다.'),
        ('검토 범위', 'guard,다섯 전방 선언과 일곱 함수 선언을 모두 확인했습니다. 포인터 반환형만으로 NULL 실패와 ERR_PTR 실패를 구분할 수 없으므로 구현 강의와 함께 읽어야 합니다. 이 헤더는 직접 클록 속도를 계산하거나 하드웨어 레지스터를 쓰지 않습니다.')
    ], questions=[
        ('clk_hw_register_kunit의 반환 타입은?', 'int', 'struct clk *', 'provider 등록의 상태를 반환합니다. 소비자 핸들을 얻는 네 함수와 구분합니다.'),
        ('of_clk_get_kunit이 받는 식별 입력은?', 'device_node와 index', 'device와 con_id만', '장치 트리 clocks 항목을 선택하는 인터페이스와 일반 device consumer 인터페이스가 별도 선언입니다.')
    ]
), dict(
    path='drivers/clk/clk_kunit_helpers.c', title='KUnit 클록 구현: 역순 cleanup과 부분 성공의 수명',
    intro='일곱 공개 helper,공통 get helper와 세 action wrapper를 전체 분석합니다.',
    principle='획득·활성화·등록에 대응하는 역연산을 예약하고 예약 실패 시 즉시 보상합니다.',
    use='오류 포인터 전파,단계별 소유권,cleanup 순서와 부분 rollback을 학습합니다.',
    area='클록 프레임워크 · 자원 관리 · 오류 처리 · callback',
    sections=[
        ('구성과 prepare enable', 'GPL-2.0 파일은 clk,clk-provider,err,kernel,slab과 KUnit clk/resource를 포함합니다. disable_unprepare wrapper를 정의하고 prepare_enable helper는 clk_prepare_enable 오류를 즉시 반환합니다. 성공한 경우에만 add_action_or_reset으로 역연산을 예약하고 그 결과를 반환합니다. 예약 실패 시 활성화를 즉시 되돌립니다.'),
        ('공통 get 처리', 'clk_put wrapper와 __clk_get_kunit은 세 획득 경로를 공유합니다. IS_ERR(clk)이면 입력 오류 포인터를 그대로 반환합니다. 그 밖에는 put action을 예약하고 실패하면 이미 reset으로 put한 뒤 ERR_PTR(ret)를 반환합니다. NULL을 IS_ERR_OR_NULL로 별도 거르는 구현은 아니므로 모든 포인터 형태를 임의로 동일 취급하지 않습니다.'),
        ('세 입력 경로', 'clk_get_kunit은 clk_get(dev,con_id),of_clk_get_kunit은 of_clk_get(np,index),clk_hw_get_clk_kunit은 clk_hw_get_clk(hw,con_id)를 호출해 결과를 공통 helper에 전달합니다. 문서상 성공 consumer는 테스트 종료 때 clk_put합니다. 세 함수가 같은 lookup 인수를 쓰는 것은 아닙니다.'),
        ('획득과 활성화의 조합', 'prepared_enabled helper는 managed hw_get을 먼저 실행하고 IS_ERR이면 반환합니다. 이어 managed prepare_enable을 호출해 오류면 ERR_PTR,성공이면 clk를 반환합니다. 정상 등록 순서는 put action 다음 disable_unprepare action이므로 역순 cleanup은 disable_unprepare 후 put입니다.'),
        ('부분 실패의 정확한 의미', '조합 helper의 활성화 단계가 실패해도 이미 등록된 put action을 여기서 즉시 release하는 코드는 없습니다. consumer 참조는 테스트 cleanup에 남습니다. 활성화 성공 뒤 그 cleanup 예약만 실패했다면 or_reset은 disable_unprepare를 즉시 실행하고 put은 나중에 실행됩니다. 실패하면 모든 이전 단계가 즉시 원상 복귀된다고 단순화하면 안 됩니다.'),
        ('Provider 등록 두 경로', 'clk_hw_unregister wrapper를 공유하며 clk_hw_register_kunit은 clk_hw_register(dev,hw),of_clk_hw_register_kunit은 of_clk_hw_register(node,hw)를 호출합니다. 각각 원래 등록 오류는 즉시 반환하고 성공 시 unregister action의 add_action_or_reset 결과를 반환합니다. hw 구조체 자체를 별도 할당하거나 kfree하는 코드는 없으므로 저장소 수명은 호출자도 고려해야 합니다.'),
        ('범위와 메타데이터', '일곱 공개 함수는 모두 EXPORT_SYMBOL_GPL입니다. MODULE_LICENSE는 GPL이고 description은 provider와 consumer용 KUnit helper입니다. 세 wrapper,공통 helper,일곱 함수와 문서를 모두 대조했습니다. 실제 클록 하드웨어 enable이나 OOM 실험은 하지 않았으며 주파수 계산·parent 선택 알고리즘은 이 파일에 없습니다.')
    ], questions=[
        ('정상 조합 helper의 테스트 종료 cleanup 순서는?', 'disable_unprepare 다음 put', 'put 다음 disable_unprepare', 'put을 먼저 예약하고 활성화 해제를 나중에 예약하므로 역순으로 실행됩니다.'),
        ('__clk_get_kunit에 ERR_PTR가 들어오면?', '그 포인터를 그대로 반환하고 action을 등록하지 않는다', '그 오류 주소를 무조건 clk_put한다', 'IS_ERR 조기 반환이 잘못된 핸들을 cleanup에 등록하는 것을 피합니다.'),
        ('get 성공 후 prepare 단계 실패 시 consumer 참조를 즉시 put하는가?', '아니다. 이미 등록된 테스트 cleanup에 남는다', '그렇다. 이 조합 함수가 직접 clk_put을 호출한다', '오류 분기는 ERR_PTR(ret) 반환뿐입니다. 즉시 rollback과 나중 cleanup을 구분해야 합니다.'),
        ('Provider 등록 성공 후 cleanup 예약 실패 시?', 'or_reset이 즉시 unregister하고 오류를 반환한다', '등록 상태를 유지하면서 0을 반환한다', '등록 성공 자체만으로 helper 전체 성공은 아닙니다. 역연산 예약도 성공해야 합니다.'),
        ('이 구현이 호출자 hw 구조체의 메모리까지 직접 kfree하는가?', '아니다. unregister action을 예약한다', '그렇다. 모든 hw는 여기서 kzalloc하고 kfree한다', 'registration 수명과 객체 저장소 소유권은 별개입니다. hw allocation/free 코드는 없습니다.')
    ]
)]
