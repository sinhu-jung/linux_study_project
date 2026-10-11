"""Whole-file PROM tree construction, property copying and architecture branches."""
ROWS = [dict(
    path='drivers/of/pdt.c', title='PROM 트리 생성: 속성 연결 리스트와 자식·형제 재귀',
    intro='펌웨어 callback으로 노드와 속성을 읽어 커널 트리를 구성하는 전체 경로를 분석합니다.',
    principle='부모·첫 자식·다음 형제 표현은 임의 개수의 자식을 가진 트리를 연결 구조로 나타냅니다.',
    use='깊이 우선 탐색,속성 리스트,초기 할당,callback 계약과 문자열 경계를 학습합니다.',
    area='장치 트리 · 재귀 · 연결 리스트 · 펌웨어 · 초기 메모리',
    sections=[
        ('구성과 아키텍처 분기', 'GPL-2.0+ 파일은 kernel,module,errno,mutex,slab,OF,OF PDT를 포함하고 PROM ops 포인터를 __initdata로 보관합니다. SPARC에서는 초기 unique_id counter를 노드·속성에 대입 후 증가하고 full name은 build_path_component로 만듭니다. 비SPARC에서는 unique ID와 irq_trans_init이 빈 inline이며 별도 이름 생성기를 사용합니다.'),
        ('비SPARC 이름 생성', '256바이트 지역 path에 pkg2path를 요청하여 반환이 0이면 kbasename을 복제합니다. 즉 해당 경로에서 저장하는 full_name은 전체 경로 문자열이 아니라 마지막 구성요소입니다. 실패하면 name 속성을 얻어 len+16바이트를 할당하고 name@unknownN을 sprintf한 뒤 오류 로그를 남깁니다. failsafe_id는 정적 counter이며 name 부재나 할당 실패를 명시적으로 거르는 분기는 없습니다.'),
        ('속성 객체와 재사용', 'build_one_prop는 property 뒤에 이름용 32바이트를 붙여 초기 할당하고 p->name을 p+1로 둡니다. static tmp가 있으면 해당 전체 영역을 0으로 지워 재사용합니다. 새 할당 경로에서만 unique ID를 부여하며 재사용 경로에서는 다시 부여하지 않습니다. 속성 열거 종료 때 얻은 객체를 다음 호출에 재활용하는 방식입니다.'),
        ('특수 속성 경로', 'special_name이 있으면 strcpy로 이름을 복사하고 special_len만큼 값을 할당·복사합니다. property list는 먼저 .node라는 특수 속성을 만들고 phandle node의 메모리 표현을 sizeof(node)만큼 복사합니다. 이 경로에 별도 endian 변환이나 항상 NUL을 붙이는 명령은 없습니다. 이름 저장소가 32바이트라는 전제와 복사 함수의 경계는 구분해야 합니다.'),
        ('일반 속성 열거와 값', 'nextprop 오류는 tmp=p로 보관하고 NULL을 반환합니다. 그 밖에는 getproplen이 0 이하이면 p->length=0으로 둡니다. 양수면 length+1을 할당하고 getproperty를 호출합니다. 반환 len이 0 이하일 때만 length를 0으로 바꾸며 양수의 짧은 읽기에 맞춰 length를 줄이지는 않습니다. 끝에는 p->value[p->length]=NUL을 기록합니다.'),
        ('속성 리스트 구성', 'build_prop_list는 .node를 head와 tail로 두고 첫 일반 속성을 추가합니다. 이후 tail->name을 prev로 넘겨 다음 속성을 구하면서 next 링크를 잇습니다. NULL에서 멈추며 순서를 다시 정렬하거나 hash table에 넣지 않습니다. 특수 속성 생성 실패를 검사하는 별도 분기도 없습니다.'),
        ('단일 name 조회 helper', 'get_one_property는 기본 반환 문자열을 <NULL>로 두고 길이가 양수이면 정확히 len바이트를 할당해 값을 읽습니다. 이 helper는 일반 속성 생성과 달리 len+1 할당이나 끝 NUL 추가를 하지 않으며 getproperty 결과 오류도 반환 포인터 변경에 사용하지 않습니다. 따라서 두 경로의 문자열 보장 조건을 같다고 설명하면 안 됩니다.'),
        ('노드 생성 순서', 'create_node는 phandle이 0이면 NULL입니다. 그 외에는 초기 할당,of_node_init,unique ID,부모 링크,name 읽기,phandle 저장,속성 리스트,full_name 생성,irq_trans_init 순서로 진행합니다. 할당 실패를 일반 errno로 전파하는 루프가 아니라 초기 allocator 및 펌웨어 callback 계약에 의존하는 코드입니다.'),
        ('트리의 자식·형제 표현', 'build_tree는 한 부모의 첫 node에서 시작해 형제들을 while로 순회합니다. 이전 형제의 sibling을 새 dp에 연결하고 첫 dp를 ret로 기억합니다. 각 dp의 child는 getchild(node)로 재귀 생성한 결과입니다. 그 자식 서브트리 처리를 마친 뒤 getsibling으로 넘어가므로 깊이 우선 구성입니다. 명시적 순환 검출이나 재귀 깊이 제한은 없습니다.'),
        ('공개 초기화와 root', 'kernel_tree_alloc은 size만 prom_early_alloc에 전달하고 align 인수는 사용하지 않습니다. build_devicetree는 ops가 NULL이면 BUG_ON하고 전역 ops를 저장합니다. root를 만든 뒤 full_name을 /로 대입하고 자식 트리를 구성합니다. root_node=0에서 create_node가 NULL을 반환하는 경우를 여기서 추가 검사하지 않습니다. 마지막 of_alias_scan에 allocator를 넘겨 chosen과 aliases 연결을 준비합니다.'),
        ('전체 범위와 검증', '아키텍처 두 분기,속성 생성·리스트·단일 조회,노드·트리 생성,allocator adapter와 공개 초기화를 모두 대조했습니다. 정상 비순환 트리는 노드·속성 수에 따른 순회를 수행하고 재귀 스택은 높이에 영향을 받습니다. 펌웨어 동작이나 초기 allocator의 실제 부팅 검증은 실행하지 않았습니다.')
    ], questions=[
        ('build_tree에서 자식과 형제는 어떻게 처리되는가?', '자식은 재귀,형제는 반복문으로 처리한다', '둘 다 전역 hash table만 조회한다', 'child를 재귀 결과로 지정하고 sibling을 이전 형제에 연결합니다. 첫 자식·다음 형제 표현입니다.'),
        ('비SPARC pkg2path 성공 시 full_name에 무엇을 복제하는가?', 'path의 kbasename', '항상 전체 path의 모든 문자', '이름 생성기가 kbasename을 호출합니다. 필드 이름만 보고 저장 형태를 추정하지 않습니다.'),
        ('getproperty가 양수이지만 요청보다 짧은 길이를 반환하면 일반 속성 length를 그 값으로 줄이는가?', '아니다. len<=0일 때만 0으로 바꾼다', '그렇다. 언제나 실제 반환 길이로 갱신한다', '대입 조건을 실제 코드대로 읽어야 합니다. 최종 NUL 위치도 p->length를 사용합니다.'),
        ('단일 name 조회 helper가 항상 추가 NUL 바이트를 쓰는가?', '아니다. 길이 그대로 할당하고 별도 NUL 기록이 없다', '그렇다. 일반 속성 helper와 완전히 같다', '비슷한 조회 함수라도 할당 크기와 종료 처리가 다릅니다.'),
        ('속성 tmp 재사용에서 SPARC unique ID를 새로 부여하는가?', '아니다. memset 후 재사용하며 ID 부여는 새 할당 쪽에 있다', '그렇다. 모든 경로에서 counter를 증가한다', '분기별 쓰기 위치를 추적해야 합니다. 메모리 재사용과 ID 부여는 별개입니다.'),
        ('kernel_tree_alloc이 align을 별도 적용하는가?', '아니다. size만 초기 allocator에 전달한다', '그렇다. align만큼 주소를 직접 반올림한다', 'adapter 본문은 prom_early_alloc(size) 반환뿐입니다. 하위 allocator 보장은 별도 계약입니다.')
    ]
)]
