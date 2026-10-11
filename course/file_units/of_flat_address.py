"""Whole-file early flattened DeviceTree address translation."""
ROWS = [dict(
    path='drivers/of/fdt_address.c', title='초기 FDT 주소 변환: ranges 구간 탐색과 부모 버스 순회',
    intro='셀 개수 결정,범위 매칭,주소 재인코딩과 루트까지의 반복 변환 전체를 분석합니다.',
    principle='각 버스의 자식 주소를 부모 주소로 변환하는 단계를 합성하여 CPU 물리 주소를 얻습니다.',
    use='반개구간 검색,엔디언 변환,트리 높이와 순회 비용,경계 검사를 학습합니다.',
    area='장치 트리 · 주소 공간 · 배열 파싱 · 트리 순회 · 정수 연산',
    sections=[
        ('구성과 제한', 'SPDX는 GPL-2.0+이며 pr_fmt는 OF: fdt: 접두부입니다. kernel,libfdt,OF,OF FDT,sizes를 포함합니다. OF_MAX_ADDR_CELLS는 4이고 OF_CHECK_COUNTS는 address cell 수가 1~4이며 size cell 수가 양수인지 확인합니다. size cell 수의 상한까지 검사하는 식은 아닙니다.'),
        ('Debug와 bus callback', 'DEBUG이면 of_dump_addr가 cell들을 8자리 hex로 출력하고 아니면 빈 함수입니다. debug 출력은 cell에 별도 endian 변환을 하지 않습니다. of_bus는 count_cells,map,translate 함수 포인터를 갖습니다. 현재 of_busses 배열에는 generic default 항목 하나만 있고 별도 PCI 등 bus 매칭 분기는 없습니다. 함수와 배열은 초기화 영역 annotation을 사용합니다.'),
        ('셀 개수 결정', 'default_count_cells는 부모 offset의 #address-cells와 #size-cells를 fdt_getprop으로 읽습니다. 출력 포인터가 nonNULL인 항목만 처리하고 속성이 있으면 be32_to_cpup,없으면 dt_root_addr_cells 또는 dt_root_size_cells를 사용합니다. 임의 조상을 반복 검색하는 함수는 아니며 속성 바이트 길이도 여기서 검사하지 않습니다.'),
        ('Ranges 한 항목의 배치', 'default_map은 range 앞 na cell을 자식 기준 주소 cp,na+pna 뒤 ns cell을 크기 s로 읽고 입력 addr를 da로 읽습니다. 부모 기준 주소 pna cell은 이 매칭 함수가 직접 더하지 않습니다. da<cp 또는 da>=cp+s면 OF_BAD_ADDR,범위 안이면 da-cp offset을 반환합니다. 포함 시작·제외 끝인 반개구간 검사이며 cp+s overflow를 별도 검사하지 않습니다.'),
        ('부모 주소 재인코딩', 'default_translate는 addr를 u64로 읽고 na*4 바이트를 0으로 지운 뒤 offset을 더합니다. na>1이면 끝에서 두 번째 cell에 상위 32비트,마지막 cell에 하위 32비트를 cpu_to_fdt32로 기록합니다. 최대 네 cell 배열을 허용해도 계산값은 u64이며 상위 두 cell까지 임의 정밀도로 보존하는 것은 아닙니다. na=1일 때는 하위 32비트만 기록합니다.'),
        ('Ranges 부재와 빈 속성', 'translate_one은 지정 rprop를 읽고 속성이 없으면 1로 실패합니다. 속성은 있지만 길이가 0이면 입력 주소 자체를 offset으로 잡고 부모 주소 버퍼를 0으로 만든 뒤 translate를 호출해 1:1 변환합니다. 속성 부재와 빈 속성은 여기서 같은 의미가 아닙니다.'),
        ('선형 ranges 검색', '길이가 양수이면 바이트 길이를 4로 나누고 rone=na+pna+ns cell 단위로 완전한 항목만 순회합니다. bus->map이 처음 OF_BAD_ADDR가 아닌 offset을 반환하면 멈춥니다. 없으면 1입니다. 매칭되면 range+na의 부모 기준 주소 pna cell을 addr에 복사하고 pbus->translate로 offset을 더합니다. 나머지 바이트나 불완전한 끝 항목을 별도 오류로 보고하는 검사는 없습니다.'),
        ('입력 reg와 최초 부모', 'fdt_translate_address는 result=OF_BAD_ADDR로 시작합니다. reg가 없으면 오류 로그 후 종료하고 부모 offset이 음수여도 실패합니다. 최초 bus는 배열의 0번입니다. 부모의 cell 수를 확인한 뒤 reg에서 na*4 바이트를 지역 addr[4]에 복사합니다. fdt_getprop이 돌려준 len을 복사 전 최소 길이 확인에 사용하지 않습니다. 첫 주소를 처리하며 reg index 인수는 없습니다.'),
        ('루트까지 반복', '루프는 현재 parent를 node_offset으로 옮기고 다시 부모를 찾습니다. 결과가 음수이면 루트에 도달했다고 간주하여 현재 addr를 u64로 읽고 종료합니다. 구체적인 음수 오류 종류를 구별하지 않는 코드입니다. 새 부모가 있으면 pna,pns를 얻고 검사 후 현재 bus 노드의 ranges로 한 단계 변환합니다.'),
        ('상태 갱신과 실패', '한 단계 변환이 성공하면 na=pna,ns=pns,bus=pbus로 바꾸고 반복합니다. cell 수 오류나 translate_one 실패는 break하며 초기 result=OF_BAD_ADDR가 남습니다. size-cells=0을 통과할 수 없다는 주석은 CPU 물리 주소로 해석 가능한 값이 아니라고 보는 이 구현의 관례라고 설명합니다. 이 함수는 트리 자체를 수정하지 않고 지역 주소 배열만 갱신합니다.'),
        ('공개 wrapper와 복잡도', 'of_flat_dt_translate_address는 unsigned long node를 받아 initial_boot_params와 함께 내부 함수에 전달합니다. blob을 복제하거나 unflatten하는 작업은 없습니다. 경로 높이가 h이고 각 층 ranges 수가 r이라면 범위 탐색은 대략 O(h*r)이며 실제로는 층별 항목 수의 합에 비례합니다. 첫 매칭 항목을 고르므로 겹치는 ranges의 순서도 영향을 줄 수 있습니다.'),
        ('전체 범위와 한계', '매크로,debug 두 구성,bus 타입과 배열,세 default callback,한 단계 변환,전체 경로 변환,공개 wrapper를 모두 확인했습니다. cell 개수 검사가 reg 최소 길이·모든 산술 overflow·모든 FDT 오류를 검증한다는 뜻은 아닙니다. 실제 DTB 변환이나 아키텍처 부팅 실험은 수행하지 않았습니다.')
    ], questions=[
        ('ranges가 없는 경우와 길이 0인 경우는 같은가?', '아니다. 부재는 실패,빈 속성은 1:1 변환이다', '그렇다. 둘 다 항상 성공한다', '포인터 NULL과 rlen==0 분기가 다릅니다. 데이터 부재와 빈 데이터의 의미를 구분합니다.'),
        ('자식 주소 0x1200,범위 시작 0x1000,부모 시작 0x8000이고 범위 안이면 변환 결과는?', '0x8200', '0x9200', 'map은 0x200 offset을 반환하고 translate는 부모 기준 0x8000에 이를 더합니다. 자식 전체 주소를 그대로 더하지 않습니다.'),
        ('addr 배열이 네 cell이면 계산도 128비트 정밀도로 유지되는가?', '아니다. 계산은 u64이며 끝의 두 cell에 재기록한다', '그렇다. 모든 cell을 그대로 더한다', 'of_read_number 결과와 a,offset은 u64입니다. 버퍼 용량과 산술 정밀도를 구분해야 합니다.'),
        ('reg 길이를 얻은 뒤 na*4 이상의 크기인지 검사하는가?', '아니다. 이 함수의 복사 전에는 해당 검사가 없다', '그렇다. len 비교가 필수 분기로 구현되어 있다', 'len은 fdt_getprop의 출력으로 받지만 memcpy 전에 사용되지 않습니다. 개수 검사와 속성 길이 검사는 다릅니다.'),
        ('겹치는 ranges가 여러 개 매칭되면 어느 것을 선택하는가?', '순회 중 첫 매칭 항목', '항상 가장 작은 범위를 정렬해 선택', '선형 순회가 성공 offset에서 break합니다. 정렬이나 최소 범위 선택은 없습니다.'),
        ('기본 cell 수 속성이 없으면 어떤 값을 사용하는가?', 'dt_root_addr_cells와 dt_root_size_cells', '항상 address=4,size=0', 'default_count_cells의 fallback은 전역 root 값입니다. 임의 조상을 재귀 검색하는 코드가 아닙니다.'),
        ('size-cells=0인 중간 버스를 통과할 수 있는가?', '이 구현에서는 count 검사에 실패한다', '항상 빈 ranges처럼 1:1로 통과한다', 'OF_CHECK_COUNTS는 ns>0을 요구합니다. 빈 ranges 분기와 cell 수 검사를 혼동하지 않습니다.')
    ]
)]
