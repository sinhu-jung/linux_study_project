"""Individually authored lessons from whole lib/bitmap-str.c; pending integration."""
def register(topic, q, detail):
    def lesson(title, symbol, why, principle, use, reading, qa, cards):
        topic(title, '자료구조·알고리즘', 'lib/bitmap-str.c', symbol,
              why, principle, use, reading, *(q(*x) for x in qa),
              details=[detail(*x) for x in cards])

    lesson('Bitmap 사용자 입력·복사와 Parser 수명', 'bitmap_parse_user',
        '사용자 공간의 주소를 커널 parser가 바로 읽지 않고 안전하게 복사한 뒤 해석하는 경계를 배웁니다.',
        'bitmap_parse_user와 bitmap_parselist_user는 memdup_user_nul로 ulen byte를 복사하고 마지막 NUL 공간을 확보합니다. ERR_PTR이면 PTR_ERR를 즉시 반환합니다. 성공한 복사본은 hex 또는 list parser에 전달하고 parser 성공·실패와 관계없이 kfree합니다. Hex wrapper의 UINT_MAX는 실제 할당 길이가 아니라 이미 NUL 종료된 입력을 끝까지 읽는 parser 계약입니다.',
        '사용자 입력 길이는 byte 단위이며 목적 bitmap의 nmaskbits는 bit 단위입니다. 복사 실패와 문법 오류를 나눠 처리합니다. Parser 오류가 목적 배열의 원상 복구를 보장하지 않으므로 실패 결과를 적용하지 않습니다.',
        '복사→IS_ERR→parser→kfree의 두 wrapper를 비교하세요.',
        [('Hex User wrapper에서 복사 성공 후 parser가 실패하면?', '복사본을 kfree하고 parser 오류를 반환한다', '복사본을 반환해 caller가 반드시 해제한다', '두 wrapper 모두 parser 반환값을 ret에 저장하고 복사본을 해제합니다. Parser 실패도 해제 경로를 지납니다.'),
         ("Ulen32와 nmaskbits32의 단위는 같은 가?", '각각 입력 byte 수와 목적 bit 수이다', '둘 다 사용자 문자열의 문자 개수이다', 'Ulen은 복사 길이입니다. Nmaskbits는 bitmap의 유효 bit 수로서 문법과 결과 범위 검사에 사용됩니다.')],
        [('포인터 오류 표현', 'ERR_PTR은 음수 오류를 포인터 값으로 표현하는 커널 관례입니다. 성공 객체와 구분한 후 PTR_ERR로 정수 오류를 꺼냅니다. 실제 잘못된 사용자 주소 접근 처리는 memdup_user_nul의 별도 구현입니다.'),
         ('종료 문자', '복사 helper가 추가한 NUL은 길이 제한 안에 NUL이 없는 사용자 입력도 종료시킵니다. 앞쪽 NUL이나 newline에서 parser가 멈추면 뒤쪽 byte는 해석하지 않습니다.')])

    lesson('Bitmap Page 출력·남은 공간과 실제 길이', 'bitmap_print_to_pagebuf',
        'Sysfs의 한 page 출력 규약과 문자열 길이 제한을 bitmap 형식 선택에 연결합니다.',
        'len은 PAGE_SIZE-offset_in_page(buf)입니다. List이면 %*pbl, hex이면 %*pb에 nmaskbits와 maskp를 넘기고 newline을 붙입니다. Scnprintf는 저장한 문자 수를 NUL 제외하고 반환합니다. Page 중간 주소라면 전체 page 크기 대신 그 주소 이후 남은 공간만 사용할 수 있습니다.',
        'Page 경계에 맞는 저장공간 안의 buf를 제공하고 출력이 남은 공간에 들어갈지 확인합니다. 반환값을 잘려 나오기 전 전체 문자열의 요구 길이로 해석하지 않습니다. 큰 bitmap의 전체 출력에는 offset/count를 가진 별도 API를 고려합니다.',
        'offset_in_page, 두 format, nmaskbits가 field width로 전달되는 부분을 읽으세요.',
        [('4096byte page의 offset4000에서 남은 출력 공간은?', '96byte이다', '4096byte를 다시 사용할 수 있다', '원본은 page 크기에서 현재 주소의 page offset을 뺍니다. NUL도 이 남은 공간 안에 저장해야 합니다.'),
         ("이 helper 반환 길이에 마지막 NUL이 포함되는 가?", "포함되지 않는 다", '언제나 NUL까지 더한 길이이다', 'Scnprintf는 실제 저장한 문자 수를 반환합니다. Newline은 저장되면 포함되지만 종료 NUL은 포함되지 않습니다.')],
        [('형식 구분', 'List는 0,2-4 같은 decimal 위치와 연속 구간입니다. Hex는 32bit 단위 숫자를 높은 쪽부터 표시합니다. 같은 bit 집합을 표현하지만 두 parser가 받는 문법은 다릅니다.'),
         ('잘림과 성공', '남은 공간보다 출력이 길면 저장한 부분만 반환합니다. 숫자·구간 중간이 잘린 문자열을 완전한 bitmap 표현으로 저장하거나 다시 parse하지 않습니다.')])

    lesson('Bitmap Bin Attribute·문자열 Byte Slice', 'bitmap_print_to_buf',
        '한 page보다 큰 출력에 offset과 count를 적용하는 원리와 매 호출의 전체 문자열 생성 비용을 배웁니다.',
        '공통 helper는 kasprintf로 newline과 NUL을 가진 전체 bitmap 문자열을 할당합니다. 실패하면 ENOMEM입니다. Memory_read_from_buffer에는 strlen(data)+1을 길이로 넘겨 종료 NUL도 읽을 수 있게 하고, off에서 count byte까지 복사한 뒤 전체 문자열을 해제합니다. 두 공개 wrapper는 list bool만 달리 전달합니다.',
        'Off와 count는 출력 문자열의 byte 단위입니다. Bit 범위를 선택하는 인자가 아닙니다. 조각을 합칠 때 off를 순서대로 증가시키고 첫 읽기부터 마지막 읽기까지 bitmap을 유지합니다. 각 호출이 전체 문자열을 다시 만드는 비용도 고려합니다.',
        '전체 할당→byte 복사→해제와 두 wrapper의 bool 인자를 읽으세요.',
        [('문자열이 0,10\\n이면 off2,count2의 조각은?', '10이다', 'Bitmap의 bit2와 bit3의 상태이다', "문자 위치 0은 0, 위치 1은 comma, 위치 2·3은 1·0입니다. Off/count는 문자 자료를 자르는 byte 위치입니다."),
         ('복사 길이를 strlen(data)+1로 넘기는 이유는?', '종료 NUL도 읽기 가능한 자료에 포함한다', 'Bitmap의 마지막 bit를 추가로 출력한다', '전체 자료 크기에 NUL 한 byte를 포함합니다. 이 API의 반환과 일반 scnprintf의 NUL 제외 반환을 혼동하지 않습니다.')],
        [('시간과 공간', '원본 주석은 전체를 여러 count 조각으로 읽을 때 O(nbits²/count), 임시 메모리를 O(nbits)로 설명합니다. 각 조각마다 전체 문자열을 다시 생성하기 때문입니다. 일반 snprintf를 대체하는 범용 빠른 출력 함수로 쓰지 않습니다.'),
         ('조각의 문법', 'List 조각은 구간 중간에서 잘릴 수 있어 독립된 bitmap 목록이 아닙니다. 예를 들어 10-12를 10-과 12로 나눠 각각 parse하면 전체와 같지 않습니다. 고정 snapshot의 조각을 순서대로 합친 뒤 해석합니다.')])

    lesson('Bitmap Region·반복 구간과 마지막 부분 그룹', 'bitmap_set_region',
        '위치 목록에 반복적인 선택 패턴을 표현하고 구조체의 필드를 실제 bit 변경으로 연결합니다.',
        'Region은 start/end의 inclusive 범위, 그룹 간격 group_len, 각 그룹의 사용 길이 off, 전체 nbits를 갖습니다. Bitmap_set_region은 start부터 group_len씩 증가하며 min(end-start+1,off) bit를 set합니다. 마지막 그룹은 범위의 남은 길이에 맞춰 줄어듭니다. 이 setter 자체는 문법·범위 검사를 수행하지 않습니다.',
        '상위 parser의 check_region이 통과한 region과 충분한 저장 배열을 사용합니다. Off는 여기에서 그룹의 사용 길이이며 출력 slice의 byte offset과 다릅니다. 실제 허용 크기와 start의 unsigned 증가 조건을 유지합니다.',
        'struct region의 다섯 필드와 inclusive 길이+1, min, loop 증가를 읽으세요.',
        [("범위 9-20에서 used4/group10이면 어떤 bit가 켜지는 가?", "9-12와 19-20이다", "9-12와 19-22이다", "첫 그룹은 9부터 4bit입니다. 다음 그룹은 19부터지만 end20까지 2bit만 남아 min이 길이를 줄입니다."),
         ('Region의 off는 출력 문자열의 byte offset인가?', '그룹마다 사용하는 bit 길이이다', '언제나 출력 byte의 시작 위치이다', '서로 다른 helper의 같은 이름을 문맥으로 구분합니다. Region setter는 off를 bitmap_set의 길이 계산에 씁니다.')],
        [('압축된 표현', "0-1023:2/256은 0,1,256,257,512,513,768,769를 선택합니다. 모든 위치를 문자열에 나열하지 않아도 반복 패턴을 표현할 수 있습니다."),
         ('부분 그룹', 'End는 포함되는 마지막 위치입니다. 남은 길이는 end-start+1이고 off0은 각 그룹에서 아무 bit도 쓰지 않는 패턴입니다. Group_len0은 별도 검사에서 금지됩니다.')])

    lesson('Bitmap Region 검사·문법과 범위 오류', 'bitmap_check_region',
        '사용자가 지정한 반복 구간의 논리 조건과 목적 bitmap의 크기 조건을 별도 오류로 처리합니다.',
        'Start>end, group_len0, off>group_len이면 EINVAL입니다. 그다음 end>=nbits이면 ERANGE입니다. 조건을 통과하면 setter가 진행합니다. Bit 위치의 최대값은 nbits-1이므로 end==nbits도 초과입니다. 두 조건이 동시에 틀리면 앞에서 검사한 EINVAL이 먼저 반환됩니다.',
        "반환값 0인 경우만 해당 region을 적용합니다. Off0은 원본 검사가 허용하지만 그룹 길이 0은 loop가 진행하지 않으므로 금지합니다. 전체 parser가 앞서 적용한 다른 region을 자동 되돌리는 지와 이 검사 결과는 별개입니다.",
        "첫 if의 세 조건,두 번째 if의 >=,마지막 0을 읽으세요.",
        [('Nbits64에서 end64를 지정하면?', 'ERANGE이다', "최대 위치 64이므로 정상이다", "64bit의 유효 위치는 0부터 63입니다. 원본은 end>=nbits를 초과로 봅니다."),
         ("Used0/group4는 검사에서 허용되는 가?", '허용된다', 'Off도 반드시 양수여야 하므로 EINVAL이다', "금지 조건은 group_len0과 off>group_len입니다. Off0은 금지하지 않고 setter에서 매 그룹 길이 0으로 처리됩니다.")],
        [('검사 순서', '잘못된 시작·끝 관계가 있고 end도 크기를 넘으면 EINVAL 분기가 먼저입니다. 오류 이름을 입력에서 가능한 모든 문제의 목록으로 읽지 않고 최초 실패 조건과 연결합니다.'),
         ('크기 전제', 'Nmaskbits는 int에서 region의 unsigned nbits로 들어갑니다. 음수 크기를 유효한 작은 bitmap으로 취급하는 방어 함수가 아닙니다. Caller는 유효한 크기와 저장 공간을 제공해야 합니다.')])

    lesson('Bitmap 숫자 Token·N과 Decimal Overflow', 'bitmap_getnum',
        '동적으로 변하는 최대 위치와 명시적인 decimal 정수를 같은 parser에서 다루는 방법을 배웁니다.',
        '첫 문자가 대문자 N이면 lastbit를 저장하고 한 문자 뒤를 반환합니다. 나머지는 _parse_integer의 base10을 사용합니다. 숫자가 없으면 EINVAL, overflow flag나 unsigned int로 값이 줄어드는 경우는 EOVERFLOW입니다. 성공하면 숫자 뒤 포인터를 반환하여 상위 문법 parser가 구분자를 검사합니다.',
        'N은 현재 nmaskbits-1에 대응하므로 bitmap 크기가 바뀌면 뜻도 바뀝니다. 소문자 n이나 +, hex prefix를 자동 받아들이는 문법으로 확대하지 않습니다. 숫자 폭 오류와 실제 bit 범위 오류는 후속 검사와 구분합니다.',
        'N branch,base10,len flag,n과 unsigned cast 비교를 읽으세요.',
        [('Nbits128인 목록에서 N의 값은?', '127이다', '128이다', 'Bitmap_parse_region이 lastbit=nbits-1을 계산해 전달합니다. N은 bit 개수가 아니라 마지막 위치입니다.'),
         ("4294967296을 32bit unsigned int token으로 읽으면?", 'EOVERFLOW이다', "자동으로 0으로 줄여 성공한다", 'U64 decimal parsing이 성공해도 n과 (unsigned int)n이 다르면 폭 초과 오류입니다. Truncation을 성공 값으로 사용하지 않습니다.')],
        [('두 단계 범위', '숫자가 unsigned int에 들어가더라도 목적 bitmap의 nbits보다 클 수 있습니다. Getnum의 숫자 표현 검사를 통과한 후 check_region이 bit 위치 범위를 판단합니다.'),
         ('포인터와 오류', '성공의 반환 포인터는 다음 문법 위치이고 실패는 ERR_PTR입니다. Caller는 dereference하기 전에 IS_ERR를 확인합니다. 숫자 길이와 오류 flag를 같은 len에 저장하는 하위 parser 관례도 읽습니다.')])

    lesson('Bitmap 구분자·Forward Reverse와 Newline 종료', 'bitmap_find_region',
        "공백과 comma를 건너뛰는 방향별 탐색이 목록과 hex 입력 해석에 어떻게 쓰이는 지 배웁니다.",
        'End_of_str은 NUL 또는 newline, __end_of_region은 isspace 또는 comma입니다. End_of_region은 둘을 합칩니다. Forward finder는 공백·comma를 건너뛰고 종료 문자이면 NULL을 반환합니다. Reverse finder는 start<=end인 동안 끝의 공백·comma를 뒤로 건너뜁니다. 상위 hex parser는 먼저 첫 newline 이전까지만 reverse 탐색 범위로 정합니다.',
        '문자 분류와 입력 경계는 실제 호출 경로를 따라 봅니다. List의 leading region finder에서 newline은 whitespace로 먼저 소비될 수 있지만 숫자 뒤 문법 위치의 newline은 종료 문자입니다. 모든 newline이 항상 같은 단계에서 멈춘다고 단순화하지 않습니다.',
        '두 종료 predicate와 forward skip 순서,reverse의 경계 조건을 비교하세요.',
        [("Hex 입력 1\\n2는 어느 부분을 해석하는 가?", "첫 newline 앞의 1이다", "Newline을 무시하고 12라는 hex 숫자가 된다", 'Bitmap_parse는 strnchrnul로 첫 newline 위치를 먼저 정하고 그 앞에서 역방향 chunk를 읽습니다.'),
         ('List의 시작에 있는 comma와 space는?', '다음 region을 찾는 동안 건너뛴다', '항상 첫 문자 오류로 반환한다', 'Forward finder의 __end_of_region 반복은 comma와 isspace 문자를 허용합니다. 빈 separator 묶음이 즉시 오류가 되지 않습니다.')],
        [('Newline의 문맥', '숫자 뒤 newline은 no_pattern 경로에서 NULL을 반환해 종료할 수 있습니다. 반면 finder가 시작할 때 newline을 만나면 isspace가 먼저 소비합니다. Leading newline과 이미 완성된 region 뒤 newline을 구분합니다.'),
         ('C 경계 모델', 'Reverse 코드에는 시작 앞 위치까지 내려간 pointer를 비교하는 경로가 있습니다. 커널의 실제 저수준 표현을 host 실험으로 확인하더라도 모든 표준 C 환경에서 임의 객체 경계를 넘는 pointer 계산이 허용된다는 증명으로 쓰지 않습니다.')])

    lesson('Bitmap List 문법·All Range와 반복 Pattern', 'bitmap_parse_region',
        '단일 위치·범위·전체 집합·반복 선택을 한 상태 흐름으로 해석하는 원리를 배웁니다.',
        "Parser는 대소문자 무관한 all의 앞 3문자를 인식하거나 decimal/N start를 읽습니다. 단일 위치면 end=start, 범위면 hyphen 뒤 end입니다. Pattern이 없으면 off와 group_len을 end+1로 놓아 한 번에 범위를 채웁니다. Colon 패턴은 off/group_len 순으로 숫자를 읽고 slash를 요구합니다. 숫자를 읽은 뒤 separator와 남은 문법의 확인 위치를 따라야 합니다.",
        '문법 start-end:used/group에 맞춰 입력합니다. All도 반복 pattern을 붙일 수 있습니다. All 뒤 임의 접미사를 자동 무시하는 표현이 아닙니다. 이 함수는 오류 포인터·다음 위치·종료 NULL을 반환하며 실제 범위 적용은 상위 함수가 합니다.',
        'all→check_pattern,label no_end/no_pattern,colon와 slash를 읽으세요.',
        [("All:1/4를 16bit bitmap에 적용하면?", '{0,4,8,12}이다', '{0,1,2,3}이다', 'All은 start0,end15로 바뀌고 used1/group4가 네 그룹에서 첫 bit를 선택합니다.'),
         ("단일 위치 5에 pattern이 없을 때 end는?", '5로 설정된다', 'Nmaskbits 전체로 설정된다', 'No_end label은 r->end=r->start를 수행합니다. All이나 명시적 범위와 달리 한 위치만 선택합니다.')],
        [('기본 그룹', "End+1을 off와 group_len에 넣으면 시작이 0이 아닌 범위에서 도 첫 bitmap_set이 남은 전체 범위를 채웁니다. Step이 충분히 커서 다음 시작은 end를 넘습니다. 유효 nmaskbits 범위라는 전제를 유지합니다."),
         ('문법 실패', 'Start 다음 hyphen이나 separator가 아니거나, range 다음 colon이 아닌 문자가 있거나, used 다음 slash가 없으면 EINVAL입니다. Getnum의 숫자 오류도 그대로 전달합니다.')])

    lesson('Bitmap List 적용·실패 뒤 부분 결과', 'bitmap_parselist',
        '입력 전체를 먼저 검증하지 않는 순차 parser의 상태 변경과 오류 처리 방법을 배웁니다.',
        "Bitmap_parselist는 시작할 때 목적 유효 bit를 zero합니다. 각 region에 대해 finder→parse_region→check_region→set_region을 반복합니다. 앞의 정상 region은 즉시 적용되고 뒤 region이 실패해도 그 변경을 rollback하지 않습니다. 따라서 성공 0만 전체 입력을 유효한 결과로 판단할 수 있습니다.",
        '기존 설정을 실패 시 유지하려면 caller가 별도 임시 bitmap에 parse하고 성공 후 교체합니다. 같은 목적 배열에 직접 parse한 뒤 오류만 무시하면 일부 입력이 반영된 상태를 사용하게 됩니다. 성공 결과도 공유 객체에 공개할 때 별도 동기화를 사용합니다.',
        "최초 zero와 반복 안의 set 위치,오류 return 앞에 undo가 없는 지 읽으세요.",
        [("8bit 목적에 1,9를 parse하면 실패 뒤 유효 bit는?", '앞서 적용한 bit1이 남을 수 있다', '입력 전 bitmap을 무조건 복원한다', '처음 zero 뒤 region1을 set하고 region9의 end>=8 검사에서 ERANGE입니다. 이미 적용한 bit1을 지우는 rollback은 없습니다.'),
         ("잘못된 입력에서 도 기존 설정을 유지하려면?", '임시 bitmap에 parse하고 성공할 때 교체한다', '같은 목적에 parse하고 오류를 무시한다', '임시 결과를 사용하면 실패 중간 상태가 기존 설정을 덮지 않습니다. 교체 시 공유 상태의 별도 동기화 계약도 지켜야 합니다.')],
        [('빈 입력', '빈 문자열이나 separator만 있는 입력은 목적을 zero한 뒤 finder가 종료를 확인하여 성공합니다. 기존 bitmap을 보존하는 no-op 요청이 아니라 빈 집합 결과입니다.'),
         ('중복과 순서', "같은 위치를 여러 region에서 set해도 bit는 1입니다. 정상 region의 순서는 집합 결과에 영향을 주지 않을 수 있지만 오류가 섞이면 먼저 적용된 region의 부분 상태가 남는 순서 차이가 생깁니다.")])

    lesson('Bitmap Hex Chunk·역방향 Nibble과32bit 폭', 'bitmap_get_x32_reverse',
        "Hex 문자열의 오른쪽 자리부터 4bit씩 누적하여 32bit 숫자 하나를 만드는 원리를 배웁니다.",
        "Helper는 end의 hex digit을 hex_to_bin으로 변환하여 ret의 i 위치에 OR하고 i를 4씩 늘립니다. Start에 닿거나 separator면 해당 숫자를 완료합니다. 최대 8digit 뒤에도 추가 hex digit이 있으면 EOVERFLOW입니다. 잘못된 digit은 EINVAL입니다. 성공한 chunk만 *num에 저장하고 다음 reverse 위치를 반환합니다.",
        "Comma/공백으로 구분된 각 chunk는 32bit 폭입니다. 값을 작게 만드는 leading zero가 있어도 9digit chunk는 허용되지 않습니다. 0x prefix는 이 helper의 문법이 아닙니다. 마지막 성공 저장과 오류 전의 지역 ret를 구분합니다.",
        'i+=4,hex_to_bin,error before*num,8digit 뒤 추가 digit 검사를 읽으세요.',
        [("Hex chunk12ab의 낮은 4bit는?", "b의 숫자값 11이다", "첫 문자 1이다", '오른쪽 끝부터 읽어 ret의 i0부터 넣습니다. 왼쪽 문자는 더 높은 자리의 nibble이 됩니다.'),
         ("000000001이라는 9digit chunk는?", 'EOVERFLOW이다', "값 1이므로 길이와 관계없이 성공한다", "원본은 8digit 뒤의 추가 hex 문자로 폭 초과를 판단합니다. Leading zero도 digit 폭 제한에서 제외하지 않습니다.")],
        [('오류 전 저장', "Ret은 지역변수이고 out label에서 만 *num을 씁니다. 현재 chunk 내부에서 잘못된 문자를 만나면 해당 chunk는 저장하지 않지만 상위 parser가 앞서 처리한 다른 chunk는 이미 저장되어 있을 수 있습니다."),
         ('Shift 폭', "Nibble은 0..15이고 i는 0..28입니다. 상위 bit의 표현은 커널 정수 연산 조건과 함께 읽습니다. Host 검증에서 는 선택한 컴파일 옵션·ABI를 명시하고 표준 C의 모든 signed shift 조건을 보장한다고 주장하지 않습니다.")])

    lesson('Bitmap Hex Parser·낮은 Chunk와 Endian 배치', 'bitmap_parse',
        '사람이 읽는 높은 자리 우선 문자열을 native bitmap의 낮은 위치부터 저장하는 알고리즘을 배웁니다.',
        "Bitmap_parse는 buflen 또는 첫 NUL/newline까지의 끝을 정하고 오른쪽 chunk부터 읽습니다. 오른쪽은 bit0..31,그 왼쪽은 bit32..63입니다. 목적을 u32 배열로 보고 일반 경로는 chunk index에 저장합니다. CONFIG_64BIT와 big-endian이 함께 선택되면 chunk^1을 사용해 unsigned long 안의 낮은 32bit 수치 위치에 맞춥니다.",
        "Nmaskbits에 맞는 unsigned long 저장 공간을 제공하고 32bit chunk 단위 문법을 사용합니다. 이 입력은 arbitrary wire byte 배열이 아니라 hex 숫자 문자열입니다. Big-endian 경로를 little-endian host에서 CONFIG 이름만 바꿔 동일하게 실행 검증했다고 주장하지 않습니다.",
        'BITS_TO_U32,chunks--,u32 cast,chunk^1의 CONFIG 조건을 읽으세요.',
        [("64bit bitmap에 1,5를 hex parse하면 set 위치는?", '{0,2,32}이다', '{0,2,4}이다', "오른쪽 5는 낮은 32bit의 bit0과 2이고 왼쪽 1은 다음 32bit의 bit32입니다. Comma는 문자열 숫자를 단순 이어 붙이는 표시가 아닙니다."),
         ('64bit big-endian의 chunk^1은 왜 필요한가?', "Long 안의 낮은 32bit 수치 위치를 맞춘다", "집합의 bit 번호를 전부 역순으로 뒤집는 다", 'Native unsigned long의 메모리 내 u32 반쪽 순서에 맞춘 index 조정입니다. 각 chunk 숫자의 bit 자체를 역순 변환하지 않습니다.')],
        [('허용 separator', "원본 문법은 1,,5와 ,44처럼 빈 comma 구간과 공백을 허용합니다. Empty chunk가 32bit zero word를 별도로 추가하는 것이 아니라 finder가 separator를 건너뛰어 실제 숫자 chunk만 셉니다."),
         ('제한된 buffer', 'Buflen은 byte 경계이고 NUL/newline이 더 앞에 있으면 거기까지 읽습니다. UINT_MAX를 쓰는 경로는 종료된 입력이라는 계약이 있어야 하며 실제 읽을 수 없는 임의 공간을 허용하는 옵션이 아닙니다.')])

    lesson('Bitmap Hex 완료 검사·미사용 Chunk와 부분 오류', 'bitmap_parse',
        "Hex 입력의 32bit 경계와 마지막 부분 word에서 초과 bit를 검출하는 방법을 배웁니다.",
        "입력 chunk가 목적 BITS_TO_U32 개수를 넘으면 EOVERFLOW입니다. 읽은 chunk보다 목적이 더 크면 unset_bit부터 nmaskbits까지 clear합니다. 마지막 부분 32bit까지 읽었다면 nmaskbits 이상에서 set bit를 찾아 하나라도 있으면 EOVERFLOW입니다. 이 parser는 처음에 전체 목적을 zero하지 않으며 실패하면 먼저 저장한 낮은 chunk가 남을 수 있습니다.",
        '오류 결과를 적용하지 않고 필요하면 임시 bitmap에 parse합니다. 유효 영역의 결과와 저장 word의 unused tail을 나눠 봅니다. 성공 시 의미 없는 모든 저장 tail bit가 언제나 zero된다는 계약으로 확대하지 않습니다.',
        'unset_bit 계산,bitmap_clear 경로,find_next_bit의 초과 영역,초기 zero가 없는 점을 읽으세요.',
        [('5bit 목적에 hex20을 parse하면?', 'Bit5가 유효 범위를 넘어 EOVERFLOW이다', "값을 자동으로 낮은 5bit로 잘라 성공한다", "20 hex는 32decimal이고 bit5를 set합니다. 원본은 마지막 부분 chunk에서 nmaskbits 이상의 set bit를 검사해 오류를 반환합니다."),
         ("64bit 목적에 bad!,1을 넣고 뒤 chunk에서 실패하면?", "오른쪽에서 먼저 저장한 낮은 1이 남을 수 있다", '처음 상태를 자동으로 되돌린다', "오른쪽 1을 먼저 저장하고 왼쪽 잘못된 chunk를 만나 실패합니다. 함수에는 전체 transactional rollback이 없습니다.")],
        [('빈 Hex 입력', '실제 chunk가 없으면 unset_bit0이고 유효 nmaskbits 영역을 clear해 빈 집합으로 성공합니다. Nbits0과 불필요한 자료가 있는 입력의 분기까지 같은 결과로 일반화하지 않습니다.'),
         ('List와 비교', 'List parser는 시작부터 목적 유효 영역을 zero하고 왼쪽 region부터 set합니다. Hex parser는 오른쪽 chunk부터 쓰고 성공 후 남은 유효 영역을 정리합니다. 둘 다 실패 시 완전한 설정 복원을 제공하지 않습니다.')])
