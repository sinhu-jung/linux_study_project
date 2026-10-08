"""Individual explanation of lib/find_bit.c macros and all function variants."""
def register(topic, q, detail):
    def lesson(title, symbol, why, principle, use, reading, qa, cards):
        topic(title, '자료구조·알고리즘', 'lib/find_bit.c', symbol,
              why, principle, use, reading, *(q(*x) for x in qa),
              details=[detail(*x) for x in cards])

    lesson('Bit Search First·비어 있는 Word 건너뛰기', '_find_first_bit',
        'Bit 집합의 첫 원소를 한 bit씩 전부 조사하지 않고 word 단위로 건너뛰는 탐색 원리를 배웁니다.',
        "FIND_FIRST_BIT는 idx0부터 각 word의 FETCH를 읽습니다. 값이 0이면 그 word 전체를 건너뛰고 비 zero이면 __ffs로 가장 낮은 set bit 위치를 구합니다. 결과는 idx*BITS_PER_LONG에 더하고 size와 min하여 유효 영역 밖 tail을 종료값으로 바꿉니다. First zero variant는 FETCH를 ~addr[idx]로 바꿔 같은 구조에서 0bit를 찾습니다.",
        "유효 size와 충분한 저장 word를 제공하고 결과<size일 때만 실제 위치로 사용합니다. __ffs를 0에서 호출하지 않도록 val 검사와 함께 읽습니다. Architecture/header가 다른 구현을 선택할 수 있어 generic lib body와 실제 빌드 경로를 구분합니다.",
        "FIND_FIRST_BIT의 FETCH,비 zero 검사,__ffs,min과 zero wrapper를 읽으세요.",
        [("첫 word가 0이고 두 번째 word의 bit3이 set이면 64bit long에서 결과는 ?", '67이다', '3이다', "Idx1의 시작 위치 64에 word 내부 3을 더합니다. 첫 word의 64개 0bit를 개별 원소로 반환하지 않습니다."),
         ("유효 size65인데 저장 bit70만 set이면 첫 탐색 결과는 ?", 'Size65이다', '70을 유효 위치로 반환한다', "발견한 위치 70을 min으로 size65에 제한합니다. Result<size 검사에서 발견되지 않은 것으로 판단합니다.")],
        [('Word와 Instruction', '__ffs는 한 word 안의 첫 set bit입니다. 실제 CPU instruction 또는 architecture helper 선택은 별도 구현입니다. Word search loop와 그 primitive의 역할을 나누어 봅니다.'),
         ('빈 크기', "Size0이면 loop가 실행되지 않고 0을 반환합니다. 반환 0이 bit0의 발견을 뜻하는 것이 아니라 size와 같은 종료값입니다.")])

    lesson('Bit First 교집합·FETCH 식으로 필터 결합', '_find_first_and_and_bit',
        '여러 조건을 만족하는 첫 후보를 임시 bitmap 없이 결합된 word 식으로 찾는 원리를 배웁니다.',
        "First AND는 addr1[idx]&addr2[idx], first AND AND는 세 word의 AND를 FIND_FIRST_BIT의 FETCH로 넣습니다. 공통 조건을 만족하는 bit가 없는 word는 건너뛰고 첫 비 zero 결합 word에서 낮은 bit를 찾습니다. MUNGE의 nop은 숫자 표현을 바꾸지 않음을 뜻합니다.",
        '같은 size의 입력 집합을 주고 result<size인지 검사합니다. 함수는 입력을 수정하거나 결과 집합을 저장하지 않습니다. 동시 writer가 있으면 여러 입력 word를 한 시점의 snapshot으로 읽는 원자성을 외부 규약으로 보장합니다.',
        '두 wrapper의 결합 식과 같은 FIND_FIRST_BIT 호출을 비교하세요.',
        [('A={1,5},B={3,5},C={1,5}의 first AND AND는?', '5이다', "첫 입력의 1이다", "세 조건 모두에 포함된 위치 5만 결합 식에서 set입니다. 한 입력에만 있는 낮은 위치는 제외됩니다."),
         ("교집합 첫 탐색에 별도 결과 bitmap allocation이 있는 가?", '없고 word 식을 직접 평가한다', '항상 전체 임시 bitmap을 먼저 할당한다', '각 wrapper는 FETCH 식만 전달합니다. 원본에는 임시 배열 생성이나 allocator 호출이 없습니다.')],
        [('Predicate 재사용', '일반 first와 결합 first는 loop가 같고 후보 word 식만 다릅니다. 매크로가 caller의 local idx를 참조하는 이유를 실제 확장 문맥과 연결합니다.'),
         ('조기 종료', '낮은 word에서 공통 bit를 찾으면 높은 word를 읽을 필요가 없습니다. 최악에는 전체 저장 word를 방문하므로 항상 상수 시간이라고 보지 않습니다.')])

    lesson('Bit Next·시작 Word Mask와 유효 끝', '_find_next_bit',
        '지정된 bit 위치 이상에서 다음 원소를 찾으며 이전 부분을 제외하는 word mask를 배웁니다.',
        "FIND_NEXT_BIT는 start>=size이면 size를 바로 반환합니다. 시작 word의 BITMAP_FIRST_WORD_MASK로 start보다 낮은 bit를 제외하고 비 zero가 될 때까지 다음 word의 FETCH를 읽습니다. 첫 word 이후에는 최초 mask를 재사용하지 않습니다. 비 zero 후보의 __ffs 위치를 size에 제한합니다. Next zero는 FETCH를 반전하여 0bit를 찾습니다.",
        'Start는 포함되는 검색 시작점입니다. 이미 발견한 bit 다음을 찾으려면 안전한 범위에서 이전 위치+1을 넘깁니다. Size 밖 반환을 실제 bit로 접근하지 않습니다. 저장 배열의 unused tail은 발견 위치 제한과 함께 해석합니다.',
        'Start 선검사,첫 mask,for의 초기식과 갱신식,다음 word 경계를 읽으세요.',
        [('Set 위치{2,7},start7의 next는?', '7이다', "항상 7을 건너뛰어종료한다", '검색 offset은 포함되는 시작점입니다. 이전 원소를 건너뛰는 동작은 caller가+1을 전달할 때 생깁니다.'),
         ("Start가 size와같으면 word를 먼저 읽는 가?", "읽지않고 size로종료한다", "마지막 word를 무조건읽는 다", '매크로 앞의 start>=sz 조건은 FETCH 이전에 out으로 이동합니다. 범위 밖 시작점은 즉시 종료합니다.')],
        [('두 Loop 식', '초기 tmp는 FETCH&mask이고 갱신 tmp는 FETCH입니다. 첫 word만 시작 이전을 지우고 다음 word는 모든 bit가 검색 대상이기 때문입니다.'),
         ('Generic와 Inline', 'Header의 작은 상수 size 경로와 architecture 정의는 이 generic 함수를 우회할 수 있습니다. 이 파일의 #ifndef 조건을 실제 빌드 선택으로 읽습니다.')])

    lesson('Bit Next 결합·AND ANDNOT OR 후보', '_find_next_andnot_bit',
        '여러 집합 조건의 다음 후보를 찾을 때 교집합·차집합·합집합 식의 방향을 이해합니다.',
        'Next AND는 A&B, ANDNOT은 A&~B, OR는 A|B를 FIND_NEXT_BIT에 전달합니다. 시작 위치 제한과 종료값은 같은 매크로가 처리합니다. 차집합은 첫 입력에 있으면서 두 번째에는 없는 위치를 찾으며 순서를 바꾸면 후보 집합이 달라집니다.',
        '원하는 조건에 맞는 식과 인자 순서를 선택하고 세 variant 모두 반환<size를 확인합니다. Boolean bitmap 생성과 달리 위치 하나만 반환합니다. Input의 수명과 동시 수정 조건을 caller에서 유지합니다.',
        '각 wrapper의 FETCH 식과 동일한 start 전달을 읽으세요.',
        [('A={1,4},B={4,6},start0의 next ANDNOT(A,B)는?', '1이다', '6이다', "A&~B는 A의 1만남깁니다. B에만 있는 6은 A의 차집합 후보가 아닙니다."),
         ("동일 입력의 next OR는 무엇을 찾는 가?", "둘중하나에있는 다음위치이다", "두 입력모두에있는 위치만찾는 다", "OR는 A|B입니다. 두 조건동시충족은 AND이며합집합과다릅니다.")],
        [('결과 종류', "Next는 원소 번호를 찾습니다. 집합이 비었는 지 bool만 반환하는 intersects와도, 전체 차집합 배열을 저장하는 bitmap_andnot과도 반환 계약이 다릅니다."),
         ('처리 비용', '조건 결합은 word 식 안에서 수행하며 임시 bitmap을 만들지 않습니다. Start 이후 word를 차례로 읽으므로 검색 거리에 따라 비용이 달라집니다.')])

    lesson('Bit Nth·Popcount로 순번 Word 찾기', '__find_nth_bit',
        '집합의 n번째 원소를 bit 번호가 아니라 set bit의 순번으로 찾는 rank 선택 알고리즘을 배웁니다.',
        'FIND_NTH_BIT는 각 완전한 word의 hweight_long을 세어 남은 순번 nr에서 뺍니다. Word의 set 개수가 nr보다 크면 그 word에서 fns(tmp,nr)로 순번 위치를 찾습니다. 마지막 부분 word는 유효 mask를 적용합니다. Fns는 낮은 set bit를 word&=word-1로 제거한 뒤 원하는 낮은 위치를 반환합니다.',
        "순번은 0부터 시작합니다. Header의 n>=size 선검사와 generic 내부의 호출 전제를 함께 읽습니다. 후보가 없을 때는 결과>=size로 판정하며 내부 반환이 항상 정확히 size라고 가정하지 않습니다. __find_nth_bit의 0크기 등을 상위 guard 없이 임의 직접 호출하지 않습니다.",
        'Word weight,nr 감소,found label,부분 word mask와 fns helper를 읽으세요.',
        [("집합{3,20,80}의순번 1은?", '20이다', "Bit번호 1이다", "순번 0은 3,순번 1은 20입니다. Nth의 n은 bit 위치가아니라정렬된 set 위치목록의순번입니다."),
         ("Nth에서 존재하지 않는 순번의 결과검사는?", "결과가 size미만인지확인한다", "결과가 size와정확히같을 때만실패이다", "Header문서는>=size 종료를 설명합니다. Genericbody의 word기준계산은 size보다큰종료값을 만들수도있습니다.")],
        [('Popcount 건너뛰기', "한 word에 5개 원소가 있고 남은 순번이 7이면 그 word를 건너뛰고 순번 2로 다음 word를 봅니다. Word 안의 개별 원소를 전부 출력할 필요가 없습니다."),
         ('경계의 차이', '완전한 마지막 word를 다 지나가거나 부분 word에 후보가 없으면 fns의 BITS_PER_LONG 종료값이 더해질 수 있습니다. 해당 값으로 배열을 인덱싱하지 않고 유효 범위 검사로 성공을 구분합니다.')])

    lesson('Bit Nth 필터·교집합 순번과 차집합', '__find_nth_and_andnot_bit',
        '원래 집합의 순번과 조건으로 거른 집합의 순번이 다르다는 점을 word 표현으로 배웁니다.',
        'Nth AND는 A&B, ANDNOT은 A&~B, AND ANDNOT은 A&B&~C를 FIND_NTH_BIT에 넘깁니다. Weight와 fns는 필터가 적용된 word를 기준으로 계산합니다. 따라서 n번째는 첫 입력의 n번째를 찾은 뒤 조건을 검사하는 방식이 아니라 모든 조건을 만족한 위치만 센 순번입니다.',
        "필터 인자의 방향과 0-based순번을 맞춥니다. Result<size인 경우만 유효 위치입니다. Input 변경을 자동 막는 함수가 아니므로 여러 조건의 snapshot이 필요하면 별도 보호를 사용합니다.",
        '세 FETCH 결합과 같은 weight/fns 흐름을 읽으세요.',
        [("A={1,3,5},B={3,5},C={3}의 AND ANDNOT순번 0은?", '5이다', "A의 첫 위치 1이다", "A&B는 3,5이고 C를 제외하면 5입니다. 필터 후집합의 첫 원소를 세므로 5를 반환합니다."),
         ("Nth AND의 weight는 어떤값을 세는 가?", "각 word의 A&B에있는 setbit이다", "A의 모든 setbit만세고 B는 끝에서 검사한다", "FETCH가결합된 word를 만듭니다. Hweight와남은 순번의감소모두그결합값을 기준으로 합니다.")],
        [('임시 배열 없음', '필터 word를 local tmp로 읽고 직접 weight와 순번을 구합니다. 전체 필터 bitmap의 allocation이나 저장은 없습니다.'),
         ('순번의 변화', '앞쪽 후보 하나가 필터에서 빠지면 그 뒤의 선택 순번이 바뀝니다. 실제 CPU 번호를 고르는 cpumask_nth 계열과 연결할 때 번호와 순번을 구분합니다.')])

    lesson('Bit Last·뒤에서 탐색과 마지막 Mask', '_find_last_bit',
        '가장 높은 set 위치를 찾을 때 tail을 먼저 제외하고 word를 거꾸로 방문하는 원리를 배웁니다.',
        "Size가 0이 아니면 마지막 word index=(size-1)/BITS_PER_LONG을 계산합니다. BITMAP_LAST_WORD_MASK로 마지막 word의 유효 bit만 남기고 비 zero이면 __fls로 높은 위치를 반환합니다. 다음 낮은 word에서 는 val=~0UL로 전체 word를 허용합니다. 끝까지 없거나 size0이면 size입니다.",
        'Result<size를 검사한 뒤 위치를 사용합니다. Last는 집합의 개수나 저장 word의 마지막 index가 아닙니다. Size0 branch가 size-1의 unsigned 감소와 잘못된 마지막 배열 접근을 막는 순서를 확인합니다.',
        'Size guard,마지막 index,초기 tail mask,__fls,idx--조건을 읽으세요.',
        [("65bit집합의저장 bit64와 70이 set이면 last는?", '64이다', '70이다', "초기 mask는 두 번째 word의 bit0만허용합니다. 저장 tail의 bit70은 유효집합의마지막 원소가아닙니다."),
         ("Size0일때마지막 word를 읽는 가?", "읽지않고 0을 반환한다", "Size-1word를 계산해반드시읽는 다", "Size 조건안에서 만 index를 계산합니다. 빈유효영역은 0이라는 종료값으로 반환됩니다.")],
        [('정방향과 역방향', 'First는 낮은 word부터__ffs,Last는 높은 word부터__fls를 사용합니다. 찾으려는 위치의 방향에 따라 loop와 한 word primitive를 함께 바꿉니다.'),
         ('종료 조건', "Do while의 idx--는 word0도 처리한 뒤 끝납니다. 이후 감소한 unsigned 값으로 새 배열 접근을 수행하지 않는 제어 흐름을 같이 읽습니다.")])

    lesson('Bit Clump8·발견 위치를8bit 경계로', 'find_next_clump8',
        "단일 bit를 찾은 뒤 주변 8bit 묶음의 위치와 값을 함께 반환하는 자료 접근 원리를 배웁니다.",
        "Find_next_clump8은 offset이상에서 next set bit를 먼저 찾습니다. 종료값이면 clump를 쓰지 않고 size를 반환합니다. 발견 위치는 round_down(offset,8)로 묶음 시작에 맞추고 bitmap_get_value8로 전체 8bit를 읽습니다. 그 시작 위치는 요청 offset보다 낮을 수 있고 마지막 부분 묶음의 unusedtail을 이 body가 별도 mask하지 않습니다.",
        "반환값<size인 경우 clump가 갱신되었다고 판단합니다. 충분한 저장 word를 제공하고 마지막 8bit의유효범위를 caller가해석합니다. 다음 묶음은 현재묶음시작+8처럼상위 iterator계약을 따라진행합니다.",
        "Next 탐색,조기 return,round_down과 8bit read 순서를 읽으세요.",
        [("Offset5에서 bit7을 찾으면 clump시작은?", '0이다', '7이다', "7을 8의배수로내림하면 0입니다. 반환은 단일발견 bit가아니라그 bit가포함된 8bit묶음의 시작입니다."),
         ("Setbit가없으면기존 clump변수는?", "이 body에서 변경하지 않는 다", "반드시 0으로 덮어쓴다", "Offset==size 분기는*clump 대입이전에 return합니다. Caller는 종료값을 확인하지 않고이전값을 새결과로사용하면 안됩니다.")],
        [('부분 Tail', "유효 size10에서 bit9가 set이면 묶음시작 8이고실제 read는 8bit입니다. Bit10..15는 유효집합밖이지만 read 값에들어갈 수있으므로 사용목적의 mask 조건을 확인합니다."),
         ('형식 읽기', "Bitmap_get_value8은 header의 bitmap_read(map,start,8)로정의됩니다. 구조체필드의 bytepointer를 그대로 읽는 것이아니라 nativebitmap의수치 bit 위치에서 값을 얻습니다.")])

    lesson('Bit LE 탐색·Byte Swap과시작Mask 변환', '_find_next_bit_le',
        'Big-endian CPU에서 little-endian으로 저장된 bitmap을 같은 논리 bit 번호로 탐색하는 원리를 배웁니다.',
        "__BIG_ENDIAN에서 LE variant는 MUNGE에 swab을 넣습니다. First zero는~addr word를 읽고 swap한값에서__ffs를 구합니다. Next set/zero는 시작 mask도 swab한뒤 native읽기 word와 AND하고결과를 다시 swab하여논리위치를 구합니다. 저장 byte 순서와 bit번호정의의차이를 양쪽 mask와후처리에서 맞춥니다.",
        "Nativebitmap과 LE 저장 bitmap의 표현을 구분하여맞는 API를 사용합니다. Little-endianhost에서 byte-swapped수치 word로분기를 시험하는 것은 산술모의검증이며 nativebig-endianABI실행으로 표시하지 않습니다. Architecture별 headeroverride도함께확인합니다.",
        "__BIG_ENDIAN 조건,세 LEwrapper,MUNGE가 mask와 tmp에적용되는 곳을 읽으세요.",
        [("LE next에서 swap은 찾은 word에만적용되는 가?", "시작 wordmask에도적용된다", "Mask는 어떤표현에서 나같으므로절대변환하지 않는 다", "FIND_NEXT_BIT는 MUNGE(BITMAP_FIRST_WORD_MASK(start))로저장표현에맞는 mask를 만들고 MUNGE(tmp)로논리검색표현을 복원합니다."),
         ("LE variant가바꾸는 것은?", "저장 byte 표현과논리검색 word의연결이다", "Setbit집합의 원소순서를 임의로랜덤화한다", "Swab은 host와 LE의 byte 순서차이를 맞춥니다. 유효 bit번호의의미를 임의로바꾸는 연산이아닙니다.")],
        [('원본 조건', "LEbody는 big-endian 선택에서 만정의되고각함수의#ifndef도 architectureoverride를 허용합니다. 모든 machine에서 항상별도 LEbody가 같이실행된다고설명하지 않습니다."),
         ('0값 전제', "Swap은 word가 0인지여부를 바꾸지않습니다. Generic매크로가 FETCH의비 zero를 검사한뒤__ffs(MUNGE(val))를 실행하는 조건이 LE후처리에서 도유지됩니다.")])
