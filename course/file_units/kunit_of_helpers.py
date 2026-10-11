"""Whole-file DeviceTree test helper interface and implementation."""
ROWS = [dict(
    path='include/kunit/of.h', title='KUnit 장치 트리 인터페이스: 구성별 skip과 내장 overlay 주소',
    intro='조건부 선언·stub과 내장 DTBO 적용 매크로,문서 예제 전체를 분석합니다.',
    principle='지원하지 않는 구성의 테스트 건너뛰기와 정상 API 반환은 다른 제어 흐름입니다.',
    use='전처리 조건,토큰 결합,링커 심볼과 길이 계산을 학습합니다.',
    area='장치 트리 · 조건부 컴파일 · 링킹 · 테스트 제어 흐름',
    sections=[
        ('헤더와 노드 참조 API', 'GPL-2.0 guard 안에 test.h를 포함하고 device_node를 전방 선언합니다. CONFIG_OF가 정의되면 of_node_put_kunit을 선언하며 없으면 inline stub이 kunit_skip(test,"requires CONFIG_OF")를 호출합니다. 단순한 no-op 정리 함수로 대체하는 것이 아니라 해당 테스트를 skip하는 동작입니다.'),
        ('Overlay 지원의 세 조건', 'overlay FDT helper 선언에는 CONFIG_OF,CONFIG_OF_OVERLAY,CONFIG_OF_EARLY_FLATTREE가 모두 정의되어야 합니다. 그 밖에는 필요한 세 구성을 설명하는 kunit_skip을 호출하고 코드상 -EINVAL 반환을 둡니다. skip이 정상 테스트 실행을 중단하는 계약과,본문에 형식상 반환문이 존재하는 것을 구분합니다. CONFIG_OF 하나만 켰다고 지원된다고 볼 수 없습니다.'),
        ('주소 구간 helper', '__of_overlay_apply_kunit은 u8 *begin,const u8 *end를 받고 지역 int unused를 선언합니다. end-begin 길이와 &unused를 of_overlay_fdt_apply_kunit에 전달합니다. 자체적으로 begin/end 순서,범위 또는 u32 길이 변환의 초과를 검사하지 않습니다. 유효한 내장 데이터 구간을 공급하는 호출자 계약에 의존합니다.'),
        ('내장 심볼과 매크로', 'of_overlay_apply_kunit은 GNU statement expression으로 extern uint8_t __dtbo_NAME_begin[]와 end[]를 선언하고 helper 호출 결과를 값으로 제공합니다. ##로 overlay_name 토큰을 심볼에 결합합니다. 실행 중 파일 경로를 열거나 문자열 이름을 검색하는 코드가 아닙니다. 실제 바이트는 빌드·링크 과정에서 포함되어야 합니다.'),
        ('문서의 빌드와 테스트 예제', '문서는 scripts/Makefile.lib의 cmd_dt_S_dtbo 규칙으로 만든 overlay_name.dtbo.o를 테스트 object와 함께 빌드하라고 설명합니다. 예제는 kunit_overlay_test 토큰으로 적용하고 이름 test-kunit인 노드를 검색해 유효성을 EXPECT한 뒤 of_node_put으로 참조를 반환합니다. 노드 조회 참조 반환과 overlay 자체의 자동 제거는 다른 정리 작업입니다.'),
        ('전체 범위', '두 조건부 API,두 비지원 stub,주소 구간 helper,내장 overlay 매크로와 예제를 모두 대조했습니다. 문서의 단순한 CONFIG_OF_OVERLAY 설명보다 실제 세 조건 분기가 정확한 지원 조건입니다. DTBO 빌드나 실제 overlay 적용은 실행하지 않았습니다.')
    ], questions=[
        ('CONFIG_OF만 있으면 FDT overlay helper가 지원되는가?', '아니다. OVERLAY와 EARLY_FLATTREE도 필요하다', '그렇다. 나머지 조건은 검사하지 않는다', '전처리 조건은 세 defined 검사의 AND입니다. 문서 요약과 실제 분기를 함께 확인해야 합니다.'),
        ('of_overlay_apply_kunit의 이름 인수는 실행 시 파일 경로 문자열인가?', '아니다. 내장 심볼 이름에 결합되는 토큰이다', '그렇다. 매 호출마다 파일을 연다', '##가 begin/end extern 심볼을 구성합니다. 파일 I/O 호출은 없습니다.'),
        ('내장 overlay 길이는 어떻게 구하는가?', 'end 주소에서 begin 주소를 뺀다', '노드 개수를 세어 4를 곱한다', 'u8 주소 구간의 길이를 전달합니다. 순서나 u32 범위 초과 검사는 helper 자체에 없습니다.'),
        ('OF 비지원 stub은 단순히 성공 반환하는가?', '아니다. kunit_skip을 호출한다', '그렇다. 모든 테스트를 성공 처리한다', '지원 부재의 skip과 성공은 다른 테스트 상태입니다. 정리 함수를 빈 동작으로 대체하는 것과도 다릅니다.')
    ]
), dict(
    path='drivers/of/of_kunit_helpers.c', title='KUnit OF 구현: overlay ID 복사와 노드 참조 정리 예약',
    intro='root skip,overlay 적용·제거와 노드 put 예약의 모든 경로를 분석합니다.',
    principle='나중에 실행할 cleanup은 호출자의 지역 변수 주소가 아닌 유효한 저장소를 참조해야 합니다.',
    use='지연 실행의 context 수명,실패 보상과 참조 이전을 학습합니다.',
    area='장치 트리 · 수명 관리 · 오류 회수 · callback · 테스트',
    sections=[
        ('파일과 root skip', 'GPL-2.0 파일은 OF,OF FDT,KUnit OF/test/resource 및 of_private.h를 포함합니다. of_root_kunit_skip은 ARM64와 ACPI가 모두 enabled이고 of_root가 없을 때만 kunit_skip합니다. 모든 아키텍처의 root 부재를 무조건 거르는 함수가 아닙니다. GPL export됩니다.'),
        ('Overlay 조건과 제거 callback', 'overlay 구현은 CONFIG_OF_OVERLAY와 CONFIG_OF_EARLY_FLATTREE가 정의될 때 포함됩니다. exit callback은 void *context를 of_overlay_remove에 넘깁니다. context는 정수 ID 자체를 포인터로 바꾼 값이 아니라 ID를 담은 int 저장소의 주소입니다. remove의 결과값은 검사하지 않습니다.'),
        ('적용 전 저장소 확보', 'apply helper는 root skip을 먼저 수행하고 kunit_kmalloc으로 int 크기의 copy_id 저장소를 준비합니다. 실패하면 -ENOMEM입니다. 이어 of_overlay_fdt_apply에 원래 blob,size,호출자의 ovcs_id와 마지막 NULL을 전달합니다. 적용 오류면 같은 ret을 반환하며 copy_id는 managed allocation으로 남아 테스트 정리 때 회수됩니다.'),
        ('ID 복사와 지연 정리', '적용 성공 후 *copy_id=*ovcs_id로 복사하고 add_action_or_reset에 제거 callback과 copy_id를 전달합니다. 헤더 wrapper의 지역 unused 같은 단명 변수를 cleanup이 직접 참조하지 않도록 별도 저장소를 둡니다. copy_id allocation보다 action이 나중에 등록되므로 정상 역순 cleanup은 overlay 제거 후 ID 저장소 해제입니다.'),
        ('Action 등록 실패와 관찰 범위', 'or_reset 실패 시 overlay 제거 callback이 즉시 실행되고 등록 오류가 반환됩니다. callback이 쓰는 ID 복사본과 호출자가 받은 ovcs_id는 별개이므로 제거 과정의 ID 변경이 호출자 변수에 자동 반영되는 것은 아닙니다. 원래 apply 실패 분기에는 이 helper 자체의 remove 호출이 없으므로 하위 API의 부분 실패 복구까지 완전하다고 여기서 주장하지 않습니다.'),
        ('노드 put의 예약', 'KUNIT_DEFINE_ACTION_WRAPPER가 of_node_put을 void *action으로 감쌉니다. of_node_put_kunit은 kunit_add_action을 호출하여 테스트 종료에 put을 예약합니다. node get을 추가로 호출하지 않으므로 호출자가 넘긴 기존 참조의 반환을 맡기는 방식입니다. 함수 이름과 달리 정상 호출 순간 즉시 put하지 않습니다.'),
        ('노드 예약 실패의 차이', '노드 helper는 add_action_or_reset이 아닌 add_action을 씁니다. 등록 실패 시 KUNIT_FAIL로 실패를 기록하지만 이 분기에서 of_node_put을 실행하지 않습니다. 따라서 overlay helper처럼 예약 실패 때 자동 역연산이 실행된다고 설명하면 안 됩니다. 반환 타입은 void라 호출자가 errno를 받는 형태도 아닙니다.'),
        ('전체 범위와 메타데이터', 'root skip,조건부 overlay exit/apply,노드 action wrapper와 put helper,세 GPL export 및 GPL license와 description을 대조했습니다. 이 파일은 노드를 검색하거나 overlay blob을 생성하지 않습니다. 실제 OF 동적 변경·참조 누수·오류 주입 테스트를 실행한 것은 아닙니다.')
    ], questions=[
        ('root가 없으면 모든 구성에서 skip하는가?', '아니다. ARM64와 ACPI 조건도 모두 필요하다', '그렇다. 다른 조건은 없다', 'if는 세 조건의 AND입니다. 함수의 짧은 문서 요약보다 본문의 조건을 정확히 읽어야 합니다.'),
        ('overlay ID를 별도 copy_id에 복사하는 이유는?', 'cleanup까지 유효한 ID 저장소를 확보하려고', 'overlay의 모든 노드를 깊은 복사하려고', '할당 크기는 int 하나입니다. 호출자의 지역 ID 변수 수명과 지연 callback의 수명을 분리합니다.'),
        ('정상 cleanup에서 ID 저장소 해제와 overlay 제거 중 무엇이 먼저인가?', 'overlay 제거', 'ID 저장소 해제', 'allocation 후 action을 등록하므로 역순 cleanup이 context 저장소를 callback 실행 동안 유지합니다.'),
        ('of_node_put_kunit은 노드 참조를 하나 더 get하는가?', '아니다. 기존 참조의 put을 예약한다', '그렇다. get과 put을 반드시 즉시 한 번씩 실행한다', '본문에는 get 호출이 없습니다. 새로운 참조 생성과 기존 참조 반환 책임 이전을 구분합니다.'),
        ('노드 put action 예약 실패 시 즉시 put이 실행되는가?', '아니다. 실패 기록만 있고 put 호출은 없다', '그렇다. or_reset이 항상 실행된다', '노드 helper는 일반 add_action을 사용합니다. overlay helper의 or_reset과 대비하여 각 오류 경로를 읽어야 합니다.')
    ]
)]
