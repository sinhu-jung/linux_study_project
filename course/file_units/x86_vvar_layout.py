"""Whole-file x86 VVAR layout macros and guarded time includes."""
ROWS = [dict(
    path='arch/x86/include/asm/vvar.h', title='X86 VVAR 배치: 선언·정의·링커 모드의 분리',
    intro='EMIT_VVAR 분기, 배열과 단일 객체 매크로, 고정 offset 두 개와 정리 규칙을 읽습니다.',
    principle='공유 변수의 C 타입 선언과 실제 섹션 배치를 다른 확장 모드로 연결하여 커널·사용자 매핑이 같은 데이터를 가리키게 합니다.',
    use='VVAR 이름 연결과 고정 offset, hidden 참조와 별도 정의의 관계를 이해합니다.',
    area='전처리 · 토큰 결합 · 문자열화 · 링커 스크립트 · 공유 매핑 · 정렬',
    sections=[
        ('파일 전체와 메모리 역할', 'GPL-2.0-only와 설명 주석, guard 뒤 EMIT_VVAR 분기와 일반 C 분기가 있고 끝에 시간 배열·RNG 단일 객체 선언 및 매크로 정리가 있습니다. 주석은 커널 데이터 페이지에 사용자용 추가 read-only 매핑을 제공한다고 설명합니다. 읽기 전용 매핑은 주소를 숨기거나 데이터를 암호화한다는 뜻이 아닙니다.'),
        ('EMIT_VVAR 모드', 'EMIT_VVAR가 정의되어 있으면 DECLARE_VVAR와 DECLARE_VVAR_SINGLE 모두 EMIT_VVAR(name,offset)으로 확장됩니다. type 인자는 이 경로에서 사용하지 않습니다. 주석상 커널 링커 스크립트의 배치와 커널 코드의 offset 값 가져오기에 이용합니다. C extern 선언을 출력하는 모드와 구분해야 합니다.'),
        ('일반 C의 배열 선언', '일반 분기는 extern char __vvar_page를 선언합니다. DECLARE_VVAR는 vvar_와 name을 ##로 결합한 배열, timens_와 name을 결합한 배열 두 개를 각각 CS_BASES 길이의 extern hidden으로 선언합니다. offset 인자는 이 분기의 C 선언에는 들어가지 않습니다. 페이지 안 위치는 다른 배치 문맥과 연결하여 결정합니다.'),
        ('일반 C의 단일 선언과 접근', 'DECLARE_VVAR_SINGLE은 hidden extern vvar_name 단일 객체만 만들며 timens 배열 별칭을 만들지 않습니다. VVAR(name)은 vvar_name, TIMENS(name)은 timens_name을 가리키도록 토큰을 결합합니다. 실제 name이 _vdso_data처럼 밑줄로 시작하므로 결합한 식별자의 밑줄 개수까지 전처리 규칙을 그대로 따릅니다.'),
        ('정의 매크로', 'DEFINE_VVAR(type,name)은 name[CS_BASES]를, DEFINE_VVAR_SINGLE은 단일 name 객체를 정의합니다. 둘 다 section(".vvar_" #name), aligned(16), __visible 속성을 붙입니다. #name은 문자열화이며 여기의 정의 이름은 vvar_ 접두사를 자동으로 붙인 이름이 아닙니다. 선언용 alias와 실제 저장소 정의의 연결은 링커 배치와 함께 읽어야 합니다.'),
        ('시간 배열의 offset', 'DECLARE_VVAR(128,struct vdso_data,_vdso_data)가 명시되어 있습니다. EMIT 모드에서는 이름과 offset을 내보내고 C 모드에서는 시간·namespace 배열의 extern 참조를 선언합니다. 숫자 128은 페이지 안 배치 offset이지 vdso_data 필드 개수나 배열 길이가 아닙니다.'),
        ('RNG 단일 객체의 offset', '_SINGLE_DATA가 정의되지 않았을 때 이를 정의하고 DECLARE_VVAR_SINGLE(640,struct vdso_rng_data,_vdso_rng_data)를 사용합니다. 이 경로는 단일 RNG 객체용이며 CS_BASES개 RNG 배열을 선언하지 않습니다. 안쪽 _SINGLE_DATA 조건과 바깥 파일 guard는 별도 전처리 상태입니다.'),
        ('정리와 경계', '파일 끝에서 DECLARE_VVAR와 DECLARE_VVAR_SINGLE을 undef합니다. 일반 분기의 VVAR/TIMENS/DEFINE 두 매크로는 여기서 undef하지 않습니다. 이 파일은 DEFINE_VVAR를 실제로 호출해 저장소를 만드는 곳이 아니며 주석도 다른 파일이 정의해야 한다고 명시합니다. 모든 설정에서 전체 레이아웃이 고정 크기에 맞는지는 실제 정의와 링커 결과까지 확인해야 합니다.'),
        ('CS와 검증 범위', '매크로의 동일 목록을 서로 다른 출력으로 재사용하는 방법, 선언과 저장소 정의, 섹션 정렬과 페이지 offset, 접근 권한과 심볼 visibility의 차이를 학습합니다. 전체 헤더를 읽었지만 x86 이미지 링크나 사용자 매핑을 실제로 실행 검증한 결과는 아닙니다.')
    ],
    questions=[
        ('EMIT_VVAR 모드에서 DECLARE_VVAR의 type 인자는 사용되는가?', '아니다. name과 offset만 EMIT_VVAR에 넘긴다', '그렇다. 항상 extern C 구조체 선언을 만든다', '이 모드는 링커 배치나 offset 정보 출력용입니다. 같은 매크로 호출도 전처리 문맥에 따라 결과가 달라집니다.'),
        ('일반 DECLARE_VVAR와 SINGLE의 차이는?', '전자는 시간·namespace 배열 둘을, 후자는 vvar 단일 객체만 선언한다', '둘 다 무조건 두 개의 단일 객체를 정의한다', 'extern 선언과 실제 정의를 구분하며 배열 길이 CS_BASES도 확인해야 합니다.'),
        ('DEFINE_VVAR의 aligned(16)은 변수 offset이 항상 16이라는 뜻인가?', '아니다. 정렬 요구이며 명시한 배치 offset과 다르다', '그렇다. 모든 객체가 같은 offset 16에 겹친다', '정렬은 주소의 배수 조건이고 선언 목록의 128·640은 배치 위치입니다.'),
        ('이 헤더는 시간 배열의 저장소를 실제 정의하는가?', '아니다. 정의 매크로를 제공하고 목록에서는 선언 매크로를 사용한다', '그렇다. extern만 있으면 새 저장소가 자동으로 생성된다', '주석도 다른 파일이 DEFINE_VVAR로 정의해야 한다고 설명합니다. 선언·정의·링커 연결을 구분합니다.')
    ]
), dict(
    path='arch/x86/include/asm/vgtod.h', title='X86 VGTOD 헤더: 설정별 include 경계',
    intro='generic gettimeofday 조건과 포함하는 다섯 헤더를 전체 범위로 읽습니다.',
    principle='아키텍처별 include 경계를 설정으로 제한하여 다른 실행 환경에 필요 없는 의존성을 끌어오지 않습니다.',
    use='짧은 연결 헤더도 빌드 구성과 타입·helper 가용성에 영향을 주는 이유를 이해합니다.',
    area='헤더 의존성 · 조건부 컴파일 · 아키텍처 경계 · include guard',
    sections=[
        ('파일 전체', 'GPL-2.0과 guard 안에 CONFIG_GENERIC_GETTIMEOFDAY 조건이 있습니다. 함수·구조체·전역 변수 정의 없이 조건부 include만 제공합니다. 파일을 포함한다고 현재 시각을 읽는 연산이 실행되지는 않습니다.'),
        ('포함 목록', '조건이 참이면 linux/compiler.h, asm/clocksource.h, vdso/datapage.h, vdso/helpers.h, uapi/linux/time.h를 순서대로 포함합니다. compiler 지원, 아키텍처 clocksource, 데이터 배치, sequence helper와 공개 시간 정의를 연결합니다. 각 포함 파일의 전체 내용을 이 짧은 헤더의 직접 구현으로 세지 않습니다.'),
        ('조건의 이유와 비활성 결과', '주석은 ARCH=um이 원하지 않는 헤더를 포함하지 않도록 이 검사가 필요하다고 설명합니다. 실제 전처리 조건은 ARCH 문자열 비교가 아니라 CONFIG_GENERIC_GETTIMEOFDAY입니다. 꺼지면 이 목록은 포함하지 않으며 그 대신 대체 함수나 타입을 정의하는 else도 없습니다.')
    ],
    questions=[
        ('이 파일이 ARCH 문자열을 직접 검사하는가?', '아니다. CONFIG_GENERIC_GETTIMEOFDAY를 검사한다', '그렇다. ARCH가 x86인지 문자열 비교한다', '주석의 목적과 실제 조건식을 구분합니다. ARCH=um 언급은 설계 이유이고 본문은 설정 매크로를 검사합니다.'),
        ('조건이 꺼지면 기본 시간 조회 함수를 제공하는가?', '아니다. 해당 include들을 생략할 뿐이다', '그렇다. 자동으로 fallback 함수 본문을 만든다', 'else나 함수 정의가 없습니다. 의존성 연결과 실행 구현은 다른 역할입니다.')
    ]
)]
