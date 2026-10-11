"""Whole fixed-width limits, ABI limits, exported constants and size powers."""
ROWS = []


def add(path, title, intro, principle, use, sections, questions):
    ROWS.append(dict(path=path, title=title, intro=intro, principle=principle,
                     use=use, area='정수 표현 · 상한·ABI·이진 크기 단위',
                     sections=sections, questions=questions))


add('include/linux/limits.h', '커널 정수 한계 전체: 타입 폭에서 최대·최소값 만들기',
    '비트 반전과 타입 변환으로 각 정수형의 표현 한계를 정의합니다.',
    'UAPI 한계와 타입, vDSO 정수 한계를 포함하고 size·물리주소·자원 크기 및 u8/s8부터u64/s64의 경계를 정의합니다.',
    '타입의 최대값은 실제 메모리 용량이나 현재 허용된 자원 한도와 다릅니다. 경계 상수를 사용해도 덧셈·곱셈의 오버플로가 자동으로 방지되지는 않습니다.',
    [('전체 구성', 'SPDX,guard,UAPI limits/types/vdso limits include,크기 관련4개와고정폭 정수 경계 매크로,#endif입니다. 함수나 런타임 계산 저장소는 없습니다.'),
     ('크기와 주소', 'SIZE_MAX는size_t의모든비트를1로만들고 SSIZE_MAX는이를한비트줄여ssize_t로변환합니다. PHYS_ADDR_MAX와RESOURCE_SIZE_MAX는각타입의모든비트가1인값입니다. phys_addr_t와resource_size_t의폭은대상설정을확인해야합니다. 최대표현주소가실제로장착된RAM의끝이라는뜻은아닙니다.'),
     ('고정폭 정수', 'U8_MAX/U16_MAX/U32_MAX는~0U를해당unsigned타입으로변환하고 U64_MAX는~0ULL을사용합니다. S8/S16/S32/S64_MAX는대응unsigned최대값을오른쪽으로한비트이동한뒤signed로변환합니다. MIN은-MAX-1입니다. U32_MIN은별도로0을정의합니다.'),
     ('수치 예제와CS', 'u8의최대값은255,s8의최대127·최소-128입니다. 최소값의절댓값128은s8양수범위에없습니다. 경계값자체의표현과그경계를넘는연산의표현가능성을구분합니다. 값의타입을명시하는캐스트도정수승격과주변식의타입규칙까지없애지는않습니다.')],
    [('PHYS_ADDR_MAX는 현재 RAM의 마지막 실제 주소인가?', '아니다. phys_addr_t의 최대 표현값이다', '그렇다. 부팅 중 메모리 크기를 조회한다', '매크로는 타입에 대한 비트 반전입니다. 장치나 메모리 맵을 조회하지 않습니다.'),
     ('s8 최소값이 -127이 아니라 -128인 이유는?', '정의가 -S8_MAX-1이며 음수 쪽 표현값이 하나 더 있다', '부호 비트가 두 개이기 때문이다', '최대127에 대해 -127-1=-128입니다. 최소값을 같은 signed 타입에서 단순 절댓값으로 바꿀 때 범위를 확인해야 합니다.'),
     ('SIZE_MAX를 사용하면 n+1 오버플로가 자동 검사되는가?', '아니다. 호출자가 범위를 검사해야 한다', '그렇다. 매크로가 예외를 던진다', '상수 정의와 검사 연산은 별개입니다. n이SIZE_MAX이면unsigned n+1은순환할수있습니다.')])

add('include/vdso/limits.h', 'vDSO 정수 한계 전체: long 폭과 포인터 표현의 전제',
    '기본 C 정수 타입의 한계를 공통 헤더에서 정의합니다.',
    'short,int,long,long long의 unsigned최대값과signed최대·최소값을비트식으로만듭니다. UINTPTR_MAX는ULONG_MAX로연결합니다.',
    '고정폭 u32와기본타입unsigned long을혼동하지않습니다. 이헤더의포인터한계별칭은대상커널ABI문맥에서읽어야합니다.',
    [('전체 정의', 'SPDX,guard,USHRT_MAX/SHRT_MAX/SHRT_MIN,INT_MAX/INT_MIN/UINT_MAX,LONG_MAX/LONG_MIN/ULONG_MAX,LLONG_MAX/LLONG_MIN/ULLONG_MAX,UINTPTR_MAX,#endif가전부입니다. 다른헤더include나실행코드는없습니다.'),
     ('접미사와 폭', '~0U,~0UL,~0ULL은각각unsigned int,long,long long폭에서모든비트가1인값입니다. signed최대는unsigned값을한비트이동한뒤캐스트하며최소는-MAX-1입니다. 접미사를무시하고모두동일한32비트계산이라고읽으면안됩니다.'),
     ('ABI 전제', 'UINTPTR_MAX가ULONG_MAX라는정의는포인터와unsigned long표현관례를연결합니다. 호스트Windows의LLP64처럼long과포인터폭이다른환경에그대로적용한결과를대상LinuxABI검증으로주장하지않습니다. 타입폭의최대값과실제사용가능주소도구분합니다.')],
    [('~0UL과 ~0ULL의 계산 타입은?', 'unsigned long과 unsigned long long이다', '둘 다 무조건 unsigned int다', '리터럴접미사가형식을정합니다. 대상ABI에서폭이같더라도C타입순위는구분됩니다.'),
     ('이 파일의 UINTPTR_MAX는 무엇에 연결되는가?', 'ULONG_MAX', '항상 숫자0xffffffff', '고정숫자가아니라unsigned long최대값의별칭입니다. 대상ABI전제를함께확인해야합니다.')])

add('include/uapi/linux/limits.h', 'UAPI 한계 상수 전체: 길이·단위·현재 자원 제한의 구분',
    '이름과 숫자가 나타내는 대상과 단위를 읽고 실제 호출의 제한과 구분합니다.',
    '13개 상수를 정의하며 파일·경로·입력큐·파이프·확장속성·그룹·신호 관련 크기를 제공합니다. 이 파일 자체에는 런타임 조회나 제한 적용 코드가 없습니다.',
    '정의된 상수가 현재 프로세스의 모든 자원 제한이나 모든 파일시스템의 실제 제한을 단독으로 설명한다고 가정하지 않습니다. 호출·파일시스템·설정의 계약을 함께 확인합니다.',
    [('전체 파일', 'SPDX syscall note,guard,NR_OPEN1024,NGROUPS_MAX65536,ARG_MAX131072,LINK_MAX127,MAX_CANON255,MAX_INPUT255,NAME_MAX255,PATH_MAX4096,PIPE_BUF4096,XATTR_NAME_MAX255,XATTR_SIZE_MAX65536,XATTR_LIST_MAX65536,RTSIG_MAX32와#endif입니다.'),
     ('문자열과 입력큐', 'NAME_MAX는파일이름,PATH_MAX는NUL을포함한경로문자수라는주석입니다. MAX_CANON과MAX_INPUT은canonical 입력큐와type-ahead 버퍼에관한상수입니다. 같은255라도서로다른객체의규칙입니다. ARG_MAX의주석은exec 인자와환경의바이트를가리키며실제호출한계의모든계산을이파일에서수행하지는않습니다.'),
     ('파이프와 확장속성', 'PIPE_BUF는파이프원자적쓰기의바이트수라는주석이며총파이프용량이라는뜻이아닙니다. XATTR_NAME_MAX는이름,XATTR_SIZE_MAX는값,XATTR_LIST_MAX는이름목록크기입니다. 이름·값·목록을하나의동일한길이로처리하면안됩니다.'),
     ('자원과CS', 'NR_OPEN,NGROUPS_MAX,LINK_MAX,RTSIG_MAX도각각별도의상수정의입니다. 현재FD제한을NR_OPEN하나로결정하거나상수정의가실제허용값을매번조회한다고해석하지않습니다. ABI에노출된이름,단위,포함상한,실행시정책의차이를학습합니다.')],
    [('PIPE_BUF4096이 파이프 전체 용량을 뜻하는가?', '아니다. 주석은 원자적 쓰기의 크기를 가리킨다', '그렇다. 모든파이프는정확히4096바이트만저장한다', '원자성기준과버퍼총용량은다른개념입니다. 이define만으로총용량을결정할수없습니다.'),
     ('PATH_MAX 주석은 종료 NUL을 포함하는가?', '포함한다', '포함하지않는다', '원문은including nul이라고명시합니다. 문자열내용길이와저장공간을구분해야합니다.'),
     ('XATTR_SIZE_MAX와XATTR_LIST_MAX는 같은 대상을 제한하는가?', '아니다. 속성값과속성이름목록이다', '그렇다. 둘다파일경로길이다', '숫자는둘다65536이지만주석의대상이다릅니다. 단위와대상을같이읽어야합니다.')])

add('include/linux/sizes.h', '크기 상수 전체: 1바이트부터64TiB까지의2의 거듭제곱',
    '메모리 영역 크기를읽기쉬운이름으로표현하는상수모음입니다.',
    'SZ_1부터SZ_512,SZ_1K부터SZ_512K,SZ_1M부터SZ_512M,SZ_1G부터SZ_512G,SZ_1T부터SZ_64T를정의합니다. 각구간은2배씩증가하며K/M/G/T는여기서1024진배율입니다.',
    '단위이름은십진1000진접두사가아닙니다. 상수가크다고그값을받는변수타입이자동으로넓어지거나메모리가확보되는것은아닙니다.',
    [('전체 구성', 'GPL-2.0-only SPDX,파일명주석,guard,linux/const.h include,연속된47개크기매크로,#endif입니다. 값은2^0부터2^46까지모든지수의2의거듭제곱을포함합니다.'),
     ('작은 크기와 타입', 'SZ_1K=0x400=1024,SZ_4K=4096,SZ_1M=1048576입니다. SZ_1G와SZ_2G까지는접미사없는16진리터럴이며C의정수리터럴타입규칙에따릅니다. 특히0x80000000을항상양의signed int로보면안됩니다.'),
     ('큰 크기와 공통 매크로', 'SZ_4G이상은_AC(hex,ULL)로C에서는unsigned long long접미사를붙입니다. 공통const계층은어셈블리에서는접미사를제거합니다. SZ_4G는2^32이므로32비트unsigned에저장하면표현할수없습니다.'),
     ('CS와 사용 전제', '2의거듭제곱크기는메모리정렬·영역계산을표현하기편하지만SZ_4K가모든대상의PAGE_SIZE라는뜻은아닙니다. 상수명은크기를나타내며실제페이지설정·할당·범위검증을수행하지않습니다. 전체표는각이름의이진배율을독립계산해검산할수있습니다.')],
    [('SZ_1K의 값은?', '1024', '1000', '원문0x400은2^10입니다. 이파일의크기접두사는이진배율입니다.'),
     ('SZ_4G를32비트unsigned에정확히저장할수있는가?', '없다.2^32는최대값2^32-1을넘는다', '있다.상수에ULL이붙으면대상변수도자동확장된다', '상수의타입과대입대상의폭은별개입니다. 좁은타입으로변환하면값을보존하지못합니다.'),
     ('SZ_4K가항상커널페이지크기인가?', '아니다.4096이라는크기상수일뿐이다', '그렇다.모든대상의페이지설정을정의한다', '이헤더는페이지설정을읽지않습니다. 타깃의PAGE_SIZE와일치하는지는별도문제입니다.')])
