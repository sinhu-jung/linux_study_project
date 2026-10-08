"""Whole watchpoint encoding, internal interface, and permissive policy headers."""
ROWS=[]
def row(path,title,symbol,principle,use,*questions):
    ROWS.append((path,title,symbol,principle,use,questions))
E='kernel/kcsan/encoding.h'
H='kernel/kcsan/kcsan.h'
P='kernel/kcsan/permissive.h'
row(E,'KCSAN watchpoint 크기 예산·페이지와 인접 슬롯','check_encodable',
 'SLOT_RANGE는 PAGE_SIZE이며 MAX_ENCODABLE_SIZE는 SLOT_RANGE*(1+KCSAN_CHECK_ADJACENT)입니다. 고정 내부 헤더의 ADJACENT=1이므로 최대 유용 길이는 두 페이지입니다. 한 접근에서 양쪽 인접 슬롯까지 확인하는 NUM_SLOTS=3과 크기 상한인 두 페이지를 같은 숫자로 읽으면 안 됩니다. 페이지 크기와 watchpoint 슬롯 수는 별도 설정입니다.',
 'PAGE_SIZE=4096이면 최대 8192byte, 65536이면 131072byte를 계산하세요. 슬롯의 검사 범위와 실제 접근 길이 인코딩 예산을 따로 표시합니다. 선택 fixture의 페이지 값은 구성 모델이며 두 실제 kernel page 빌드를 실행한 증거는 아닙니다.',
 ('PAGE_SIZE=4096, ADJACENT=1이면 최대 인코딩 길이는 얼마인가요?','8192byte입니다.','검사 슬롯이 3개라서 12288byte입니다.','MAX_ENCODABLE_SIZE의 식은 1+ADJACENT입니다. NUM_SLOTS의 1+2*ADJACENT와 구별합니다.'),
 ('고정 NUM_SLOTS와 최대 길이의 페이지 배수는 같은가요?','아닙니다. 각각 3과 2입니다.','그렇습니다. 항상 둘 다 3입니다.','인접 슬롯 양쪽 확인 개수와 길이 인코딩 상한의 목적이 다릅니다.'))
row(E,'KCSAN 비트 압축·write·size·주소의 분할','encode_watchpoint',
 'watchpoint는 long 한 값에 최상위 write 비트, 그 아래 size 비트, 나머지 낮은 주소 비트를 합칩니다. size 폭은 bits_per(MAX_ENCODABLE_SIZE)입니다. 64비트·4KiB 페이지 모델에서는 최대 8192를 표현할 14비트가 필요하므로 주소는 64-1-14=49비트입니다. 최대값 8192가 포함되므로 단순 log2 값 13만 쓰면 부족합니다.',
 'write 1비트와 size 14비트, address 49비트를 상자로 그리세요. shift와 OR, mask의 역할을 하나씩 주석으로 답해 보세요. 선택 fixture는 원문 encode/decode와 mask를 사용하며 실제 32비트 long 구성까지 검증하지 않았습니다.',
 ('8192까지 포함하는 크기 표현에 필요한 비트 수는 얼마인가요?','14비트입니다.','13비트입니다.','13비트는 최대 8191입니다. bits_per는 상한 값 자체를 저장할 수 있어야 합니다.'),
 ('64비트·4KiB 모델의 남은 주소 비트는 얼마인가요?','49비트입니다.','64비트 전부입니다.','최상위 write 1비트와 size 14비트를 제외하면 주소에 49비트가 남습니다.'))
row(E,'KCSAN 압축 mask·겹치지 않는 필드와 정적 검사','decode_watchpoint',
 'WRITE_MASK는 최상위 한 비트, SIZE_MASK는 그 아래 크기 구간, ADDR_MASK는 최하위 주소 구간입니다. static_assert는 주소 mask가 (1UL<<주소폭)-1과 같고 세 mask의 XOR가 ~0UL과 같음을 확인합니다. 코드의 GENMASK 구간을 함께 읽어 필드의 분할을 확인해야 합니다. XOR 하나만으로 임의 세 mask가 모두 서로 배타적이라고 증명한다고 일반화하지 않습니다.',
 '세 mask를 이진수로 그려 교집합 0과 전체 범위 덮음을 따로 확인하세요. 선택 fixture는 실제 식의 static_assert와 write/size, address/size 교집합도 검사했습니다. 컴파일 시 구조 확인과 실행 중 접근 안전성은 별개입니다.',
 ('ADDR_MASK는 어떤 비트 구간인가요?','주소폭만큼의 최하위 비트입니다.','언제나 최상위 write 비트입니다.','GENMASK(주소폭-1,0)의 두 끝을 확인하세요. field의 역할과 위치를 연결합니다.'),
 ('정적 mask 검사가 실제 대상 메모리 접근의 유효성도 증명하나요?','아닙니다. 인코딩 필드 구조 검사입니다.','그렇습니다. 모든 pointer가 안전해집니다.','static_assert는 컴파일 시 상수의 관계를 확인합니다. 실제 pointer 수명·주소·범위는 다른 계약입니다.'))
row(E,'KCSAN 인코딩 가능 조건·NULL 근처와 크기 상한','check_encodable',
 'check_encodable은 addr>=PAGE_SIZE와 size<=MAX_ENCODABLE_SIZE를 확인합니다. 낮은 주소는 표현 자체는 가능하더라도 KCSAN 내부의 NULL 근처 역참조 사고를 피하려 제외한다고 주석에 설명합니다. 함수가 모든 주소의 매핑·수명을 검증하는 것은 아닙니다. size=0을 이 helper가 거부하지 않는다는 점도 전체 호출 경로와 구별해야 합니다.',
 'PAGE_SIZE-1과 PAGE_SIZE, 최대 길이와 최대+1을 비교하세요. core.c의 check_access 718–731행을 대조하면 size=0을 앞서 반환합니다. 이 교차 확인은 core.c 전체의 해설 완성 기록이 아닙니다.',
 ('이 helper의 낮은 주소 허용 경계는 무엇인가요?','addr>=PAGE_SIZE입니다.','addr가 0이면 항상 허용합니다.','본문의 >= 비교를 확인하세요. NULL 근처를 피한다는 주석의 목적과 연결합니다.'),
 ('size=0이 helper에서 허용된다는 사실을 실제 KCSAN 검사 실행으로 해석하나요?','아닙니다. core check_access는 size=0이면 먼저 반환합니다.','그렇습니다. 반드시 watchpoint를 설치합니다.','부분 helper와 전체 caller의 조건을 구별합니다. 관련 core 영역을 원문으로 교차 확인했습니다.'))
row(E,'KCSAN 주소 압축 충돌·상위 비트와 보고 필터','encode_watchpoint',
 'encode_watchpoint는 addr&ADDR_MASK를 저장하므로 상위 주소 비트는 사라집니다. 낮은 주소 비트가 같은 서로 다른 pointer는 같은 압축 주소가 될 수 있습니다. 원문은 실제 false positive가 보이려면 압축 주소가 같은 접근끼리 race하고 같은 슬롯에도 매핑되어야 한다고 설명합니다. 마지막 보고 단계에서 원주소의 불일치를 걸러내는 경로도 있다고 안내합니다.',
 '선택 모델에서 low와 low+(1UL<<주소폭)의 encoding이 같은 예를 계산하세요. 압축 값의 동등성, 슬롯 충돌, 실제 접근 충돌과 보고 필터를 네 단계로 나눕니다. fixture는 report.c 필터 엔진까지 실행하지 않습니다.',
 ('상위 비트만 다른 주소가 같은 encoding 주소가 될 수 있나요?','그렇습니다. 낮은 주소 mask만 저장합니다.','아닙니다. 주소 64비트를 모두 저장합니다.','주소 필드가 write와 size 비트 때문에 줄어듭니다. 선택 모델에서 실제 동일 인코딩을 확인했습니다.'),
 ('압축 주소가 같으면 그것만으로 실제 race 보고가 확정되나요?','아닙니다. 슬롯·접근 충돌·보고 필터도 고려합니다.','그렇습니다. 다른 조건은 없습니다.','헤더의 false positive 설명은 추가 조건과 report logic의 필터를 명시합니다.'))
row(E,'KCSAN watchpoint sentinel·0과 1의 상태 구분','decode_watchpoint',
 'INVALID_WATCHPOINT는 0, CONSUMED_WATCHPOINT는 1입니다. decode는 두 값을 먼저 거부하고 출력 인자에 값을 쓰지 않은 채 false를 반환합니다. 일반 encoded access와 슬롯의 비활성·소비 상태를 한 long 공간에 같이 표현한 것입니다. 정상 caller의 size>0 조건과 구별하여 임의 zero-size encoding을 일반 접근으로 다루지 않습니다.',
 '출력 addr,size,is_write를 미리 정한 값으로 채우고 sentinel decode가 그대로 두는지 확인하세요. decode의 bool 반환을 확인한 뒤에만 출력값을 사용합니다. fixture는 size=0·잘린 주소 0의 예약 값 충돌을 경계 예로 기록했습니다.',
 ('CONSUMED_WATCHPOINT의 예약 값은 무엇인가요?','1입니다.','언제나 최대 양의 long입니다.','헤더의 두 상수는 0과 1입니다. 일반 접근 정보와 슬롯 상태를 구별합니다.'),
 ('sentinel decode가 false이면 출력 인자도 새로 채워졌나요?','아닙니다. 원래 값이 남습니다.','그렇습니다. 항상 모두 0으로 지웁니다.','false 반환은 출력 대입 전에 발생합니다. 반환을 무시하고 미초기화 출력값을 읽지 않습니다.'))
row(E,'KCSAN decode·unsigned 변환과 write bit 복원','decode_watchpoint',
 'write bit는 long의 최상위에 있어 encoded long이 음수로 보일 수 있습니다. decode는 unsigned long으로 변환한 뒤 mask와 shift를 적용하여 주소·크기·쓰기 여부를 복원합니다. is_write는 !!로 bool화합니다. 결과 주소는 원래 full pointer가 아니라 addr_masked입니다. signed 값의 외형과 bit field의 의미를 구별해야 합니다.',
 'read와 write encoding을 같은 주소·크기로 만들어 세 출력값을 비교하세요. fixture는 선택한 크기·주소·write 조합의 roundtrip을 확인했습니다. 복원된 masked 주소를 실제 객체 pointer로 역참조하는 사용은 이 함수의 목적이 아닙니다.',
 ('decode가 복원하는 주소는 full pointer인가요?','아닙니다. masked 주소입니다.','그렇습니다. 버린 상위 비트를 자동 복구합니다.','출력 이름 자체가 addr_masked입니다. mask로 버린 정보는 이 값만으로 되살릴 수 없습니다.'),
 ('write 표시의 bool화를 위해 사용하는 연산은 무엇인가요?','!!입니다.','항상 포인터 역참조입니다.','비트 AND 결과를 두 번 부정하면 0 또는 1의 bool 값으로 정규화됩니다.'))
row(E,'KCSAN 페이지 기반 슬롯·나눗셈과 나머지 충돌','watchpoint_slot',
 'watchpoint_slot은 (addr/PAGE_SIZE)%CONFIG_KCSAN_NUM_WATCHPOINTS입니다. 같은 페이지 안의 주소는 같은 슬롯이고 슬롯 수만큼 페이지가 떨어진 주소도 충돌합니다. 일반 byte hash의 무작위 분산이 아니라 페이지 번호 기반의 제한된 테이블 선택입니다. NUM_WATCHPOINTS는 전체 슬롯 설정이며 한 접근에서 검사할 NUM_SLOTS=3과 다릅니다.',
 '4KiB 페이지와 64슬롯이면 주소를 페이지 번호로 바꾼 뒤 mod64를 계산하세요. fixture는 10,000페이지의 선택과 슬롯 수 주기를 확인했습니다. 같은 슬롯이라고 실제 byte 범위가 겹친다고 결론 내리지 않습니다.',
 ('동일 페이지 안의 두 주소는 같은 슬롯인가요?','그렇습니다. 먼저 페이지 번호로 나눕니다.','아닙니다. 마지막 byte마다 다른 슬롯입니다.','정수 나눗셈은 페이지 내부 offset을 버립니다. 그 뒤 슬롯 수로 나머지를 계산합니다.'),
 ('슬롯 수만큼 페이지가 떨어진 주소도 충돌하나요?','그렇습니다. mod 주기가 있습니다.','아닙니다. 모든 주소는 고유 슬롯입니다.','유한 테이블에 주소를 매핑하므로 충돌은 정상입니다. 뒤의 범위 검사를 따로 수행해야 합니다.'))
row(E,'KCSAN 접근 겹침·닫힌 byte 구간의 교차','matching_access',
 'matching_access는 end=addr+size-1로 두 닫힌 byte 구간의 끝을 만들고 addr1<=end2와 addr2<=end1을 모두 확인합니다. [100,103]과 [104,107]은 붙어 있어도 안 겹치고 [100,103]과 [103,106]은 한 byte 겹칩니다. 정상 비영 길이와 주소 연산의 유효 범위가 전제입니다. unsigned wrap이나 size=0을 일반 빈 구간 판정으로 기대하지 않습니다.',
 '반열린 [addr,addr+size) 표기와 원문의 닫힌 끝을 서로 변환해 보세요. fixture는 작은 비영 구간 전 조합을 각 byte의 동일성이라는 독립 oracle과 대조했습니다. zero-size 주입에서는 helper가 true일 수도 있어 caller의 앞단 제외가 중요합니다.',
 ('주소100 크기4와 주소104 크기4는 겹치나요?','아닙니다. 끝103과 시작104는 분리됩니다.','그렇습니다. 이웃하면 항상 겹칩니다.','각 byte 범위를 적으면 [100,103]과 [104,107]입니다. 경계 포함 여부를 확인합니다.'),
 ('size=0에도 이 helper가 항상 false를 반환하나요?','아닙니다. caller가 먼저 제외하는 계약을 확인합니다.','그렇습니다. 내부에 size==0 분기가 있습니다.','본문은 unsigned addr+size-1입니다. 일반 빈 구간 수학과 자동으로 같지 않습니다.'))
row(H,'KCSAN 인접 탐색·세 슬롯과 write 방향 필터','kcsan_report_set_info',
 '내부 헤더는 ADJACENT=1과 NUM_SLOTS=3을 정의합니다. core.c 114–144행의 find_watchpoint는 설정 슬롯 수가 세 개 이상인지 BUILD_BUG_ON으로 확인하고 세 후보를 읽습니다. decode 실패를 건너뛰고 expect_write인데 watchpoint가 read이면 건너뛴 뒤 범위 겹침을 확인합니다. 슬롯 선택·상태·접근 방향·범위가 순서대로 좁히는 조건입니다.',
 '이 수업의 원문 anchor는 보고 인터페이스이며 상세 탐색은 지정한 core 영역 교차 설명입니다. 그 영역만 읽은 것으로 core 전체를 완료 처리하지 않습니다. 구조·조건을 추적하며 fixture의 슬롯 함수 검사와 실제 concurrent 탐색 실행을 구별합니다.',
 ('고정 내부 헤더의 한 접근 후보 슬롯 수는 얼마인가요?','3입니다.','전체 슬롯 수와 항상 동일합니다.','NUM_SLOTS는 1+2*ADJACENT입니다. CONFIG_NUM_WATCHPOINTS와 다른 상수입니다.'),
 ('교차 읽은 find_watchpoint에서 expect_write인데 read watchpoint이면 어떻게 하나요?','그 후보를 건너뜁니다.','무조건 race로 보고합니다.','decode 뒤 방향 필터가 있습니다. 그 뒤에야 matching_access를 수행합니다.'))
row(H,'KCSAN 통계·현재 사용량과 누적 설치량','kcsan_report_set_info',
 'kcsan_counter_id에는 현재 사용 중 watchpoint, 누적 설치 watchpoint, data race, assertion 실패, capacity 부족, report 경쟁, writer 미상, 인코딩 불가, 인코딩 false positive의 아홉 항목이 있습니다. COUNT는 배열 길이를 위한 끝 값입니다. extern atomic_long_t 배열로 노출하고 debugfs에 표시하며 slow path에서만 변경하라고 주석에 설명합니다.',
 '현재 사용량과 누적 설치량을 구별해 지표가 감소할 수 있는지 설명하세요. 통계 갱신 비용이 fast path에 불필요하게 들어가지 않도록 하는 원리를 읽습니다. 이 헤더는 선언만 제공하므로 실제 counter 갱신 지점은 core 구현에서 추가로 확인합니다.',
 ('USED와 SETUP counter의 주요 차이는 무엇인가요?','현재 사용량과 누적 설치량입니다.','둘 다 현재 byte 크기입니다.','enum 각 주석은 currently in use와 total number set up을 구별합니다.'),
 ('원문은 통계 counter 변경을 어느 경로에 제한하라고 하나요?','slow path입니다.','모든 fast-path byte 접근마다 무조건 합니다.','주석은 should only be modified in slow-paths입니다. 검사 hot path의 비용과 연결해 읽습니다.'))
row(H,'KCSAN 보고 통계·assert 두 건과 경쟁 한 건','kcsan_report_known_origin',
 'ASSERT_FAILURES는 충돌한 두 ASSERT 접근이면 양쪽 모두 셀 수 있습니다. REPORT_RACES는 watchpoint를 확인하는 thread끼리 경쟁하여 하나만 보고되는 경우를 기록합니다. NO_CAPACITY와 UNENCODABLE은 서로 다른 실패 원인이고 ENCODING_FALSE_POSITIVES는 압축 때문에 맞지 않는 접근이 watchpoint를 건드린 경우입니다. 숫자를 모두 고유 bug 개수로 합산하면 잘못 읽을 수 있습니다.',
 'counter별로 무엇을 세는지 단위를 적으세요. assertion 이벤트, 보고 경쟁, 설치 실패와 실제 race 보고를 분리합니다. 원문 주석의 의미를 설명하며 실제 보고·중복 제거 실행은 이 헤더 fixture에 포함하지 않습니다.',
 ('두 ASSERT 접근이 충돌하면 assertion counter는 반드시 한 건인가요?','아닙니다. 양쪽 모두 셀 수 있습니다.','그렇습니다. 모든 counter는 고유 bug 수입니다.','ASSERT_FAILURES 주석은 both will be counted라고 명시합니다. counter 단위를 확인해야 합니다.'),
 ('NO_CAPACITY와 UNENCODABLE은 같은 원인인가요?','아닙니다. 빈 슬롯 부족과 인코딩 불가입니다.','그렇습니다. 모두 주소0만 뜻합니다.','서로 다른 enum과 설명입니다. 설치 자원 부족과 표현 가능한 접근 범위를 구별합니다.'))
row(H,'KCSAN 값 변화 tri-state·관찰 없음과 보고 금지','kcsan_report_known_origin',
 'kcsan_value_change는 MAYBE, FALSE, TRUE의 세 상태입니다. MAYBE는 변화를 관찰하지 않았어도 보고 설정에 따라 race 보고가 가능하고 FALSE는 변화가 없으며 보고가 부적절한 상태, TRUE는 실제 변화가 관찰되어 보고해야 하는 상태입니다. 단순 changed bool 하나로 MAYBE와 FALSE를 합치면 보고 정책의 구분을 잃습니다.',
 '값 변화 관찰과 보고 적합성을 두 축으로 그리세요. fixture는 enum 상수의 0·1·2를 확인하지만 보고 정책 엔진을 실행하지 않았습니다. enum 값의 수치 자체를 오류 심각도 순서라고 해석하지 않습니다.',
 ('MAYBE와 FALSE는 같은 보고 정책인가요?','아닙니다. MAYBE는 설정에 따라 보고 가능하고 FALSE는 부적절합니다.','그렇습니다. 둘 다 무조건 보고 금지입니다.','각 enum 주석은 변화 미관찰이라는 공통점 외에 보고 적합성의 차이를 설명합니다.'),
 ('TRUE는 어떤 관찰 상태인가요?','값의 변화가 관찰됐습니다.','변화 관찰 여부를 모릅니다.','TRUE 주석은 observed to change입니다. 단순 enum 번호가 아닌 의미를 읽습니다.'))
row(H,'KCSAN 보고 전달·소비 thread와 보고 thread','kcsan_report_set_info',
 'kcsan_report_set_info는 watchpoint를 hit하고 consumed로 바꾼 thread가 자기 접근 정보를 남기는 인터페이스이며 이 단계에서 아직 report를 출력하지 않습니다. 설치한 thread가 소비 사실을 관찰하면 known_origin을 호출하여 상대 thread가 남긴 정보와 자기 정보를 합쳐 보고합니다. 함수 두 개로 정보 전달 단계와 출력 단계의 역할을 나눕니다.',
 '설치 thread A와 충돌 thread B의 시간축을 그리고 B의 set_info와 A의 known_origin을 연결하세요. ip, size, access_type, watchpoint_idx의 역할을 표시합니다. 선언의 계약을 설명하며 실제 report 동기화 알고리즘은 report.c에서 따로 읽어야 합니다.',
 ('set_info 호출이 곧바로 전체 report를 출력하나요?','아닙니다. 상대 보고 thread가 소비할 정보를 남깁니다.','그렇습니다. 항상 즉시 full report입니다.','헤더 주석은 No report is printed yet라고 명시합니다. 전달과 출력 단계를 구별합니다.'),
 ('known_origin은 어떤 thread 역할에서 호출하나요?','자기가 설치한 watchpoint가 소비됐음을 관찰한 thread입니다.','언제나 init task 하나뿐입니다.','설치 thread가 상대의 set_info 정보를 이용해 full report를 만든다는 계약입니다.'))
row(H,'KCSAN unknown origin·값 변화와 놓친 writer','kcsan_report_unknown_origin',
 'unknown_origin은 다른 racing thread를 관찰하지 못했지만 stall 전후 데이터 값이 달라진 경우를 보고하는 인터페이스입니다. writer의 위치를 모른다는 뜻이지 값이 바뀌지 않았다는 뜻은 아닙니다. old,new,mask를 전달해 관찰한 변화 정보를 남깁니다. known origin과 unknown origin을 한 보고 형태로 합치면 확인된 정보의 범위를 놓칩니다.',
 'writer 위치 정보가 없는 경우와 두 접근 위치가 알려진 경우를 비교하세요. 선택 fixture는 이 함수의 prototype을 컴파일할 뿐 stall이나 실제 writer sampling을 실행하지 않습니다. 보고 원리의 계약과 실험 범위를 함께 읽습니다.',
 ('unknown origin은 old와 new가 같다는 의미인가요?','아닙니다. 값은 달라졌지만 writer thread를 관찰하지 못했습니다.','그렇습니다. 값 변화도 전혀 모릅니다.','주석은 data value before and after stall differs라고 설명합니다. unknown은 writer의 origin입니다.'),
 ('이 보고 인터페이스에 mask도 전달되나요?','그렇습니다. old,new와 함께 mask를 받습니다.','아닙니다. 숫자 하나만 받습니다.','실제 prototype을 확인하세요. 관찰한 값과 관심 비트를 보고 단계에 전달합니다.'))
row(H,'KCSAN 내부 상태·전역 활성화·지연과 IRQ trace','kcsan_save_irqtrace',
 '내부 헤더는 전역 kcsan_enabled, task와 interrupt 문맥의 udelay 변수, IRQ trace save/restore 인터페이스를 선언합니다. 실제 CPU IRQ enable 상태와 KCSAN이 더럽힌 IRQ flags state trace를 복구하는 목적을 구별해야 합니다. kcsan_skip_report_debugfs는 함수 주소가 속한 symbol의 보고 제외 여부를 판단하며 offset은 무시한다고 설명합니다.',
 '전역 enable과 앞 수업의 현재 문맥 disable을 구별하세요. task/interrupt 지연 설정과 trace 보존 역할을 표시합니다. 보고 필터의 단위를 함수 내부 instruction 하나로 단정하지 않습니다. 구현은 선언 밖에서 추가로 공부합니다.',
 ('전역 kcsan_enabled와 현재 문맥 disable은 같은 범위인가요?','아닙니다. 전역 상태와 현재 문맥을 구별합니다.','그렇습니다. 모두 현재 변수 하나만 뜻합니다.','헤더는 globally enable/disable이라고 설명합니다. 앞 수업의 current context API와 범위가 다릅니다.'),
 ('debugfs skip_report 선언은 함수 symbol의 offset을 구별한다고 하나요?','아닙니다. offset은 무시한다고 합니다.','그렇습니다. 모든 instruction마다 다른 정책입니다.','주석은 function symbol that maps to func_addr와 offsets are ignored라고 명시합니다.'))
row(P,'KCSAN permissive 정책·무시가 안전성 증명은 아니다','kcsan_ignore_address',
 'permissive.h는 흔한 data-racy 접근 종류의 보고를 생략하는 정책을 core와 분리해 감사하기 쉽게 둡니다. CONFIG_KCSAN_PERMISSIVE가 꺼지면 ignore 함수는 false입니다. 켜지면 address 정책은 정확히 &current->flags 접근을 생략합니다. 모든 task의 flags나 같은 값의 다른 변수까지 포함하는 규칙은 아닙니다. 파일 첫 주석은 이 규칙들이 race의 일반 안전성을 뜻하지 않는다고 강조합니다.',
 '현재 task의 정확한 pointer와 다른 변수 pointer를 비교하세요. 보고 잡음을 줄이는 정책과 올바른 동기화의 증명을 구별합니다. fixture의 current는 명시적인 task 모델이며 실제 스케줄링 task 전환은 실행하지 않습니다.',
 ('주소 정책은 모든 task의 flags를 이름으로 찾아 생략하나요?','아닙니다. 정확히 &current->flags와 pointer를 비교합니다.','그렇습니다. 모든 flags라는 변수입니다.','본문은 pointer equality입니다. 필드 이름이나 값 비교가 아닙니다.'),
 ('permissive 규칙으로 보고가 생략되면 race가 일반적으로 안전한가요?','아닙니다. 원문은 그런 의미가 아니라고 명시합니다.','그렇습니다. lock이 필요 없다는 증명입니다.','파일 첫 경고는 none of the rules imply generally safe라고 합니다. 탐지 정책과 안전성은 다릅니다.'))
row(P,'KCSAN permissive 대상·plain read와 word 길이','kcsan_ignore_data_race',
 '데이터 변화 정책은 type이 0인 plain read와 size<=sizeof(long)에만 적용됩니다. WRITE나 ATOMIC, ASSERT 등 비트가 하나라도 있으면 type이 비영이므로 false를 반환합니다. 복합 read-write race도 계속 보고하려는 목적입니다. 부수적인 size=0 입력은 helper 식의 범위에 들지만 실제 check_access 앞단의 비영 길이 계약과 구별합니다.',
 'type0과 type1·3·4·8을 비교하고 word 길이와 word+1을 대입하세요. 함수의 early return을 순서대로 추적합니다. 선택 fixture는 8개 type과 5개 길이의 도메인을 검사했습니다.',
 ('type=WRITE인 접근에도 permissive 값 변화 생략 규칙을 적용하나요?','아닙니다. type이 비영이면 먼저 false입니다.','그렇습니다. 모든 write를 생략합니다.','본문의 if(type || size>sizeof(long)) 조건을 먼저 확인하세요. plain read만 대상입니다.'),
 ('길이가 sizeof(long)+1이면 한 비트 변화여도 생략하나요?','아닙니다. 크기 조건에서 제외됩니다.','그렇습니다. diff만 보면 됩니다.','크기와 type 제한이 popcount 조건보다 먼저입니다. 한 조건만 보고 결론 내리지 않습니다.'))
row(P,'KCSAN permissive popcount·정확히 한 비트 변화','kcsan_ignore_data_race',
 'hweight64(diff)==1이면 한 비트가 바뀐 패턴을 고려합니다. 주석의 no more than one이라는 설명만 보고 변화0도 무조건 무시한다고 추측하면 안 됩니다. 실제 조건은 정확히 1입니다. diff는 함수 인자로 받으므로 caller의 old/new와 일치하는 변화량 전달도 중요합니다. 선택 oracle은 old^new를 일관되게 전달하고 독립 bit 순회로 popcount를 계산합니다.',
 'diff=0,1,2,3의 켜진 bit 개수를 직접 세세요. CONFIG와 type·size 필터를 통과한 뒤 이 조건에 들어갑니다. fixture는 old0..63,diff0..255 조합을 대조하며 모든 u64 입력의 exhaustive 증명은 아닙니다.',
 ('diff=0이면 정확한 함수 조건상 한 비트 변화 생략인가요?','아닙니다. hweight64가 0입니다.','그렇습니다. <=1을 검사합니다.','실제 비교 연산은 ==1입니다. 주석 설명과 분기의 정확한 조건을 함께 읽습니다.'),
 ('diff=3의 popcount는 얼마인가요?','2입니다.','1입니다.','3은 이진수 11입니다. 숫자의 크기와 켜진 비트 개수는 다른 기준입니다.'))
row(P,'KCSAN permissive bool 예외·0↔1은 계속 보고','kcsan_ignore_data_race',
 '한 비트 변화여도 old 또는 new가 0이고 diff==1이면 일반 bool처럼 보이므로 무시하지 않습니다. 메모리 순서 요구가 흥미로운 경우가 많다고 원문에 설명합니다. 0→1과 1→0은 보고 대상에 남지만 2→3은 두 값이 비영이라 생략될 수 있고 0→2는 diff=2라 bool 예외에 해당하지 않습니다. 모두 CONFIG·type·size 조건을 통과한 경우의 정책입니다.',
 'old,new,diff 표에 네 예를 대입해 !old||!new와 diff==1을 각각 계산하세요. 정책이 안 보고한다고 변화가 안전하다고 해석하지 않습니다. 실제 동기화 원리는 release/acquire 등의 별도 계약으로 판단합니다.',
 ('permissive에서 plain read의 0→1 한 비트 변화는 무시하나요?','아닙니다. bool 예외로 보고 대상에 남습니다.','그렇습니다. 한 비트면 모두 무시합니다.','old가0이고 diff가1이므로 예외 조건이 참입니다. 다른 type·size 제한도 먼저 확인합니다.'),
 ('정상 필터를 통과한 0→2는 bool 예외에 해당하나요?','아닙니다. diff가2라 한 비트 생략이 가능합니다.','그렇습니다. 0이 있으면 항상 예외입니다.','예외는 0 여부와 diff==1을 함께 요구합니다. diff의 값과 popcount를 구별하세요.'))

def register(topic,q,detail):
 for path,title,symbol,principle,use,questions in ROWS:
  topic(title,'관찰·디버깅',path,symbol,
   '고정 커널 KCSAN의 실제 watchpoint 압축·슬롯 선택·범위 판정·보고 인터페이스·생략 정책을 읽어 자료구조와 알고리즘의 원리 및 조건을 배웁니다.',principle,use,
   '주소·길이·type의 변화, 비트 분할, 슬롯 번호, 상태 예약값과 보고 조건을 계산하고 원문에 한 줄씩 주석을 달아 보세요.',
   *(q(*x) for x in questions),details=[
    detail('원문 범위','encoding.h 102행, kcsan.h 142행, permissive.h 94행 전체를 읽었습니다. core.c 114–144행과 718–731행만 호출 조건을 교차 확인했으며 core.c와 report.c 전체를 이 수업으로 완료 처리하지 않습니다.'),
    detail('선택 실행','64비트 long, 4KiB·64KiB 페이지와 3·64슬롯, permissive off/on의 8개 모델 구성에서 원문 세 헤더를 컴파일했습니다. 최적화·ASan·UBSan 각 실행은 인코딩 roundtrip·예약값·슬롯 주기·독립 byte 겹침 oracle·독립 bit-count 정책 oracle을 검사합니다. 실제 sampling race·concurrent watchpoint 설치·보고 필터·IRQ trace·native32bit를 실행한 증거는 아닙니다.')])
