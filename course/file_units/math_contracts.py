"""Whole arithmetic header and its constant/UAPI include chain."""
ROWS = []


def add(path, title, intro, principle, use, sections, questions):
    ROWS.append(dict(path=path, title=title, intro=intro, principle=principle,
                     use=use, area='정수 타입 · 전처리·ABI·고정소수점',
                     sections=sections, questions=questions))


add('include/linux/math.h', '수학 헤더 전체: 반올림·분수·절댓값의 타입 계약',
    '계산식이 짧아도 인자 평가 횟수, 정수 승격, 폭, 부호가 결과를 바꿀 수 있습니다.',
    '이 헤더는 정렬·나눗셈 반올림 매크로, 분수 구조체, mult_frac, abs/abs_diff, reciprocal_scale과 거듭제곱·제곱근 선언을 모읍니다.',
    '각 매크로의 전제 조건을 따로 확인합니다. 모든 API가 임의 부호·0 제수·오버플로·부수효과 있는 인자를 안전하게 처리한다는 공통 규약은 없습니다.',
    [('전체 구성과 의존성', 'include guard 안에 types.h, asm/div64.h, uapi/linux/kernel.h가 있습니다. types는 정수형, div64는 do_div, UAPI 연결은 __KERNEL_DIV_ROUND_UP 같은 상수를 제공합니다. GNU typeof, statement expression, builtin_choose_expr 등을 사용하므로 순수 ISO C만의 표현식 모음이 아닙니다.'),
     ('2의 거듭제곱 배수', '__round_mask는 y-1을 x 타입으로 변환합니다. round_up은 ((x-1)|mask)+1, round_down은 x&~mask입니다. y는 양의2의 거듭제곱이어야 합니다. x=13,y=8이면 각각16과8입니다. mask의 폭을 x에 맞추는 것은 ~mask가 상위 비트를 잘못 제거하지 않도록 하는 장치입니다. 표현 범위를 넘는 결과까지 검출하지는 않습니다.'),
     ('일반 배수 올림·내림', 'roundup은 y를 지역 변수에 저장하고 (x+y-1)/y*y를 계산합니다. rounddown은 x를 저장하여 x-x%y를 반환합니다. 비음수13과 배수6이면18과12입니다. 제수0은 허용되지 않으며 x+y-1도 넘칠 수 있습니다. 음수의 C 나눗셈은0 방향 절단이므로 이름만 보고 수학적 바닥 함수라고 가정하지 않습니다.'),
     ('나눗셈 결과의 올림', 'DIV_ROUND_UP은 UAPI의 __KERNEL_DIV_ROUND_UP 별칭입니다. DIV_ROUND_DOWN_ULL은 ll을 unsigned long long 임시 변수에 저장하고 do_div로 몫을 구합니다. DIV_ROUND_UP_ULL은 ll+d-1을 만든 뒤 같은 경로를 씁니다. d 표현식은 여러 곳에 등장하므로 부수효과 없는 값을 전달해야 합니다. SECTOR_T 버전은 BITS_PER_LONG==32이면 ULL 경로, 아니면 일반 경로입니다.'),
     ('가장 가까운 정수', 'DIV_ROUND_CLOSEST는 인자의 부호 타입과 값의 부호 관계에 따라 d/2를 더하거나 빼고 나눕니다. 표현 가능한 signed 예제5/2는3, -5/2는-3으로 정확히 중간이면0에서 먼 쪽입니다. 음수와 unsigned 제수를 섞는 등 주석이 배제한 경우에는 적용하지 않습니다. ULL 버전은 unsigned 분자와32비트 제수 계약이며 덧셈 오버플로를 자동 검출하지 않습니다.'),
     ('분수 데이터 타입과 계산', '__STRUCT_FRACT로 s8,u8,s16,u16,s32,u32 각각 numerator/denominator 구조체를 만든 뒤 생성 매크로를 undef합니다. 분모가0인지 검사하거나 약분하지 않는 저장 형식입니다. mult_frac는 x=q*d+r로 나누어 q*n+r*n/d를 계산합니다. x=10,n=3,d=4이면 q=2,r=2이므로7입니다. 불필요한 x*n 중간값은 줄이지만 q*n 또는 r*n까지 무조건 안전한 것은 아닙니다.'),
     ('sector_div의 효과', 'sector_div(a,b)는 do_div(a,b) 별칭입니다. 몫을 반환하는 일반 함수처럼 읽지 않습니다. do_div 계약에 따라 a를 몫으로 변경하고 표현식 값으로 나머지를 얻습니다. 실제 아키텍처 구현은 포함된 div64 헤더에서 확인해야 합니다.'),
     ('abs와 abs_diff', 'abs는 builtin 타입 선택을 통해 unsigned도 대응 signed로 변환한 뒤 부호를 검사합니다. plain char는 signed char처럼 해석하지만 반환형은 char로 보존합니다. 표현할 수 없는 최소 signed int/long의 양수값까지 만들어주는 API가 아닙니다. abs_diff는 두 지역 변수 주소 비교로 타입 불일치 진단을 유도하고 큰 값에서 작은 값을 뺍니다. signed 타입의 양끝 차이는 넘칠 수 있고 같은 값의 차이는0이므로 주석의 positive를 항상 엄격한 양수라고 읽으면 안 됩니다.'),
     ('reciprocal_scale', '(u64)val*ep_ro의 상위32비트를 취해 floor(val*ep_ro/2^32)를 반환합니다. ep_ro>0이면0 이상 ep_ro 미만이며 나머지 연산이 아닙니다. val=2^31,ep_ro=10이면5입니다. ep_ro=0이면0이 반환되지만 빈 배열에 유효한 인덱스가 생기는 것은 아닙니다.'),
     ('마지막 선언과 폭 분기', 'int_pow는 u64 밑과 unsigned 지수, int_sqrt는 unsigned long을 사용합니다. BITS_PER_LONG<64이면 int_sqrt64 외부 선언이고 그 외에는 int_sqrt(x)를 u32로 반환하는 인라인 함수입니다. 선언을 읽는 것과 각 구현 파일을 읽는 것은 다른 범위의 학습입니다.')],
    [('13을6의 배수로 올릴 때 적절한 API와 값은?', 'roundup(13,6),18', 'round_up(13,6),항상18', 'round_up의 비트 마스크 공식은2의 거듭제곱 배수 전용입니다. 임의 양의 배수에는 roundup의 나눗셈 공식을 사용합니다.'),
     ('mult_frac(10,3,4)의 값은?', '7', '6', '몫2에3을 곱한6과 나머지2*3/4의 정수 몫1을 더합니다. x/d를 먼저 계산한 뒤 나머지를 버리는 식과 다릅니다.'),
     ('DIV_ROUND_CLOSEST(-5,2)는 안전한 signed 예제에서?', '-3', '-2', '부호가 다르므로 d/2를 빼서(-5-1)/2=-3으로 계산합니다. 정확한 중간은0에서 먼 정수입니다.'),
     ('reciprocal_scale(2^31,10)은?', '5', '8', '2^31*10을2^32로 나눈 값은5입니다. 2^31%10인8과 다릅니다.'),
     ('abs_diff가 signed 타입의 모든 차이 오버플로를 막는가?', '아니다. 큰 값에서 작은 값을 빼도 표현 범위를 넘을 수 있다', '그렇다. 부호 순서만 맞추면 항상 안전하다', 'INT_MAX-INT_MIN의 수학적 결과는 int의 양수 범위를 넘습니다. 비교 방향과 결과 표현 가능성은 별개입니다.'),
     ('분수 구조체 생성이 분모0을 막는가?', '아니다. 두 정수 필드를 정의할 뿐이다', '그렇다. 생성 매크로가 분모를 자동 검사한다', '구조체 선언에는 생성자나 조건 검사 코드가 없습니다. 데이터 형식과 유효성 검증은 구분해야 합니다.')])

add('include/uapi/linux/const.h', 'UAPI 상수 전체: C·어셈블리 분기와 타입 접미사',
    '같은 상수를 C와 어셈블리에서 공유하기 위한 전처리 설계입니다.',
    'C에서는 _AC가 토큰 붙이기로 UL/ULL 접미사를 만들고 _AT가 캐스트합니다. __ASSEMBLY__에서는 접미사와 타입 캐스트를 제거하고 값 표현식을 남깁니다.',
    '비트 번호·정렬 배수·나눗셈 제수는 호출자가 유효 범위로 제공해야 합니다. 이름이 상수 매크로라고 해서 인자가 한 번만 평가되거나 모든 식이 허용되지는 않습니다.',
    [('파일 전체와 타입 생성', 'SPDX syscall note, guard, 설명, assembly/C 분기, _UL/_ULL, _BITUL/_BITULL, C 전용 _BIT128, 정렬과 올림 나눗셈 매크로로 끝납니다. 두 단계 _AC→__AC는 접미사를 붙이기 전에 인자 매크로 확장이 가능하도록 합니다. _UL에는 일반 산술식보다 접미사를 붙일 수 있는 리터럴 형태가 필요합니다.'),
     ('비트 상수', '_BITUL(x)는1UL<<x, _BITULL(x)는1ULL<<x입니다. 음수 시프트나 타입 폭 이상 시프트는 유효하지 않습니다. _BIT128은1을 unsigned __int128로 먼저 변환한 다음 시프트하고 어셈블리 분기에는 정의하지 않습니다. 해당 C 확장을 지원하는 컴파일러가 필요합니다.'),
     ('정렬', '__ALIGN_KERNEL(x,a)는 x 타입의 a-1 마스크를 만들어 ((x+mask)&~mask)를 계산합니다. 양의2의 거듭제곱 배수와 표현 가능한 합이 전제입니다. x=13,a=8이면(13+7)&~7=16입니다. mask 표현식은 반복되므로 부수효과를 피해야 합니다.'),
     ('올림 나눗셈', '__KERNEL_DIV_ROUND_UP(n,d)는(n+d-1)/d입니다. 비음수10,d=3이면4입니다. d는 두 번 나타나고0 제수와 덧셈 오버플로를 검사하지 않습니다. 이 파일에 assembly 분기가 있다고 typeof를 쓰는 정렬 매크로까지 모두 어셈블리 문법으로 바뀌는 것은 아닙니다.')],
    [('__ASSEMBLY__에서 _AT(T,X)는?', 'X만 남는다', 'C 타입 캐스트((T)(X))가 남는다', '어셈블러에서 C 타입 문법을 제거하기 위한 분기입니다. C 분기에서만 명시적 캐스트를 만듭니다.'),
     ('_BIT128이 어셈블리에서도 정의되는가?', '아니다. !defined(__ASSEMBLY__) 조건 안에 있다', '그렇다. 모든 비트 매크로가 항상 동일하다', '128비트 C 타입 캐스트를 사용하는 별도 조건부 매크로입니다. _BITUL과 정의 범위가 다릅니다.'),
     ('__KERNEL_DIV_ROUND_UP에 d++를 전달해도 한 번만 증가하는가?', '보장되지 않는다. d가 두 번 등장한다', '그렇다. 매크로가 임시 변수에 저장한다', '원문(n+d-1)/d에는 임시 변수 저장이 없습니다. 여러 평가 및 순서 문제를 피하려면 부수효과 없는 제수를 사용합니다.')])

add('include/uapi/linux/kernel.h', 'UAPI kernel 헤더 전체: 선언 없이 연결하는 포함 계층',
    '이름이 넓은 헤더도 실제로는 두 헤더를 연결하는 역할만 할 수 있습니다.',
    '_UAPI_LINUX_KERNEL_H guard 안에서 linux/sysinfo.h와 linux/const.h를 포함합니다.',
    '사용자 공간에 노출되는 sysinfo 구조체와 공통 상수 매크로의 연결점입니다. 이 파일 자체에 시스템 호출 구현은 없습니다.',
    [('전체 내용', 'SPDX GPL-2.0 WITH Linux-syscall-note, include guard, 두 include, #endif가 전부입니다. 함수 본문·별도 데이터·추가 매크로 정의는 없습니다.'),
     ('포함 경로의 의미', '저장소에서 이 파일은 include/uapi 아래에 있지만 include 문자열은 linux/sysinfo.h입니다. 내보낸 UAPI 헤더 집합과 include 검색 경로의 문맥을 고려해야 하며 존재하지 않는 include/linux/sysinfo.h를 임의로 가정하면 안 됩니다.'),
     ('CS와 책임 분리', '구조체 메모리 배치 정의와 실제 시스템 정보 수집은 별개입니다. guard는 같은 번역 단위의 중복 포함을 제어하며 프로세스 간 공유 메모리나 런타임 잠금이 아닙니다.')],
    [('이 파일이 sysinfo 시스템 호출을 구현하는가?', '아니다. 관련 헤더를 포함하는 연결 파일이다', '그렇다. 시스템 정보를 읽는 함수 본문이 있다', '실제 원문에는 두 include만 있고 함수 본문이 없습니다.'),
     ('include guard는 런타임 동시 접근 잠금인가?', '아니다. 전처리 단계의 중복 포함 제어다', '그렇다. 동시에 두 스레드가 접근하지 못하게 한다', 'guard는 #ifndef/#define으로 처리됩니다. 실행 시 잠금 객체를 생성하지 않습니다.')])

add('include/uapi/linux/sysinfo.h', 'sysinfo ABI 전체: 고정소수점 부하와 메모리 단위',
    '구조체 필드의 숫자를 해석할 때 단위·폭·패딩을 함께 봅니다.',
    'SI_LOAD_SHIFT=16과 struct sysinfo를 정의합니다. uptime,3개 loads, RAM/swap 값, procs/pad, high memory 값,mem_unit,호환 패딩으로 구성됩니다.',
    '메모리 필드는 mem_unit 바이트 단위를 고려해 해석합니다. ABI 타입 폭과 구조체 정렬을 무시하고 파일 바이트를 고정 오프셋으로 읽으면 안 됩니다.',
    [('시간과 부하', 'uptime은 __kernel_long_t이고 주석의 단위는 부팅 후 초입니다. loads[3]은1·5·15분 부하 평균이며 SI_LOAD_SHIFT16의 고정소수점입니다. kernel/sys.c의 get_avenrun 호출도 이 시프트에 맞춥니다. 예컨대65536은1.0이며 CPU 사용률65536%라는 의미가 아닙니다.'),
     ('메모리 필드 전체', 'totalram,freeram,sharedram,bufferram,totalswap,freeswap,totalhigh,freehigh는 __kernel_ulong_t입니다. mem_unit은 __u32 바이트 단위입니다. 값100과 단위4096이면409600바이트로 해석하되 곱셈을 담을 충분히 넓은 타입이 필요합니다. freeram을 모든 회수 가능한 캐시까지 포함한 현대 MemAvailable과 자동으로 동일시하지 않습니다.'),
     ('개수와 ABI 패딩', 'procs는 __u16이고 헤더 주석은 current processes라고 표현합니다. 고정 버전 kernel/sys.c는 nr_threads를 대입하므로 프로세스 그룹 수만 센다는 해석은 피합니다. pad는 m68k용 명시 패딩이며 _f 크기는20-2*sizeof(__kernel_ulong_t)-sizeof(__u32)입니다. ulong4바이트이면8,8바이트이면0이지만 이것만으로 전체 sizeof나 필드 오프셋이 결정되지는 않습니다.'),
     ('파일 범위와 호환성', 'SPDX syscall note, guard, types include,상수,구조체가 전부입니다. 이 헤더는 통계를 수집하거나 검증하지 않습니다. 필드 순서·타입·패딩을 바꾸는 일은 단순 이름 변경과 달리 커널/사용자 공간 ABI에 영향을 줄 수 있습니다.')],
    [('loads 값65536을 SI_LOAD_SHIFT16으로 해석하면?', '1.0', '65536퍼센트', '고정소수점 소수부16비트이므로65536/2^16=1입니다. 부하 평균은 CPU 사용률 백분율과 다릅니다.'),
     ('totalram100,mem_unit4096이면 바이트 수는?', '409600', '100', '메모리 값에 단위 바이트 수를 곱합니다. 단위가 항상1이라고 가정하면 잘못 읽을 수 있습니다.'),
     ('_f 패딩 길이가 같으면 모든 ABI의 구조체 크기도 같은가?', '아니다. 타입 폭과 정렬 및 다른 필드 배치도 고려해야 한다', '그렇다. _f만으로 전체 크기를 결정한다', '명시 패딩 외에 타입 크기·정렬이 구조체 배치를 결정합니다. 특정 호스트의 sizeof를 모든 대상에 일반화하지 않습니다.')])

add('include/vdso/const.h', 'vDSO 상수 헤더 전체: 공통 UAPI 위의 짧은 별칭',
    '같은 상수 규칙을 여러 계층에서 재사용하는 포함 구조입니다.',
    'uapi/linux/const.h를 포함하고 UL(x)를 _UL(x),ULL(x)를 _ULL(x)로 연결합니다.',
    'UL/ULL은 산술 값을 런타임 변환하는 함수가 아니라 전처리 상수 표현을 만드는 매크로입니다. 실제 C·어셈블리 분기는 포함한 UAPI 헤더에 있습니다.',
    [('전체 파일', 'SPDX GPL-2.0, __VDSO_CONST_H guard,단일 include,별칭2개,#endif가 전부입니다. 함수나 가변 전역 상태는 없습니다.'),
     ('위임 관계', 'UL(1)은 C 문맥에서 _UL과 _AC를 거쳐1UL 상수를 만듭니다. 어셈블리 문맥에서는 UAPI의 분기에 따라 접미사가 제거됩니다. 이 파일이 별도의 또 다른 비트 연산 알고리즘을 구현하지는 않습니다.'),
     ('타입과 사용 제한', 'unsigned long과 unsigned long long은 구분되는 C 타입입니다. 두 타입의 폭이 같을 수 있어도 타입 자체가 같아지는 것은 아닙니다. 접미사 붙이기 매크로에는 일반 변수나 임의 산술식을 전달하는 용도로 해석하지 않습니다.')],
    [('UL과 ULL의 C 타입은 항상 같은가?', '아니다. 각각 unsigned long과 unsigned long long이다', '그렇다. 둘 다 unsigned이므로 같은 타입이다', '부호가 같아도 정수 타입의 순위와 폭은 별개입니다. 구체 ABI에서는 폭이 같을 수도 있습니다.'),
     ('C·어셈블리 분기를 이 파일이 직접 정의하는가?', '아니다. 포함한 UAPI const 헤더에 위임한다', '그렇다. 이 파일 안에 __ASSEMBLY__ 분기가 있다', '원문은 include와 UL/ULL 별칭뿐입니다. 실제 분기 위치까지 추적해야 파일별 책임을 구분할 수 있습니다.')])

add('include/linux/const.h', '커널 상수 헤더 전체: vDSO 공통 정의로의 연결',
    '작은 wrapper 헤더의 역할을 실제 내용 그대로 파악합니다.',
    '_LINUX_CONST_H guard 안에 vdso/const.h를 포함하는 것이 전부입니다.',
    'linux/const.h를 포함하는 커널 코드는 vDSO 계층을 통해 UAPI의 상수 정의를 사용합니다. 이 파일에 정의가 없다고 전체 포함 결과에도 없다고 판단하면 안 됩니다.',
    [('원문 전체', '이 고정 버전 파일은 guard,빈 줄,vdso/const.h include,#endif로 이루어집니다. 파일 자체에는 SPDX 줄도 없습니다. 다른 헤더의 내용이나 주석을 이 파일에 존재한다고 옮겨 적지 않습니다.'),
     ('포함 그래프', 'include/linux/const.h → include/vdso/const.h → include/uapi/linux/const.h 순으로 이어집니다. UL/ULL 별칭은 중간 계층, _AC 등의 구현은 UAPI 계층에 있습니다.'),
     ('CS 연결', '간접 포함은 API 재사용과 의존성 추적의 예입니다. 컴파일 오류를 조사할 때 호출 지점만 검색하지 말고 매크로가 정의되는 실제 파일까지 추적합니다. include guard는 이 wrapper의 중복 처리만 제어합니다.')],
    [('이 파일의 직접 include 대상은?', 'vdso/const.h', 'uapi/linux/sysinfo.h', '원문은 vdso/const.h 하나를 포함합니다. UAPI const는 그 다음 포함 단계입니다.'),
     ('_AC 매크로 본문이 이 파일에 직접 있는가?', '없다. 포함 계층을 따라 UAPI const에서 찾는다', '있다. wrapper가 전부 복제한다', '정의를 복제하지 않고 공통 헤더를 포함하는 구조입니다. 직접 정의 위치와 사용 가능 범위를 구분합니다.')])
