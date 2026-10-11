"""Whole-file x86 random wrapper and syscall/data hooks."""
ROWS = [dict(
    path='arch/x86/entry/vdso/vgetrandom.c',
    title='X86 vDSO getrandom 진입점: C 소스 포함과 weak alias',
    intro='공통 난수 구현 포함, 다섯 인수 전달, 별칭 선언을 전체 분석합니다.',
    principle='함수 이름의 별칭은 별도 구현이나 추가 호출 단계가 아니며 이름이 같아도 다른 API의 인수 계약과 혼동하면 안 됩니다.',
    use='vDSO 확장 인터페이스와 기본 getrandom syscall을 구별합니다.',
    area='번역 단위 · 소스 include · ABI · weak alias · wrapper',
    sections=[
        ('파일 전체와 직접 소스 포함', 'GPL-2.0-only와 저작권 주석 뒤 linux/types.h를 포함하고 상대 경로로 lib/vdso/getrandom.c를 직접 include합니다. 함수 원형만 읽는 것이 아니라 공통 구현 본문을 이 번역 단위에 넣습니다. ARM64 Makefile의 -include 방식과 목적 일부는 같지만 원본에서 표현한 위치는 다릅니다.'),
        ('다섯 인수 wrapper', '__vdso_getrandom은 buffer, len, flags, opaque_state, opaque_len을 __cvdso_getrandom에 그대로 전달하고 ssize_t 결과를 반환합니다. 이 함수 본문에는 CPU 기능 검사·난수 round·상태 재시도·별도 errno 설정이 없습니다. 그 책임을 호출된 공통 구현 및 아키텍처 helper와 구분합니다.'),
        ('Weak alias의 자료형', 'getrandom은 void *, size_t, unsigned int, void *, size_t 다섯 인수와 ssize_t 반환형으로 선언되고 weak, alias("__vdso_getrandom") 속성을 갖습니다. 별도의 중간 함수 본문이 아닙니다. 일반 libc나 기본 syscall의 세 인수 getrandom과 이름만 보고 같은 호출 계약이라고 판단하면 안 됩니다. 여기서는 vDSO 상태 인수 두 개가 추가된 ABI입니다.'),
        ('공개 여부와 범위', 'weak alias 선언과 최종 동적 심볼 공개는 다른 단계이며 링크 스크립트·버전 규칙도 함께 확인해야 합니다. 이 파일 자체에는 별도 설정별 분기나 32비트 대체 구현이 없습니다. 전체 본문과 별칭을 대조했으며 공통 C 파일을 중복 완료 집계하거나 실제 x86 ELF 심볼표 실행 검증을 수행한 것으로 표시하지 않습니다.')
    ],
    questions=[
        ('이 파일의 getrandom weak alias는 인수가 몇 개인가?', 'opaque 상태 인수를 포함해 다섯 개이다', '기본 syscall과 같으므로 세 개이다', '선언은 다섯 인수를 명시합니다. 심볼 이름이 같아도 호출 계약은 선언과 제공 문맥을 확인해야 합니다.'),
        ('공통 getrandom.c include는 함수 선언만 가져오는가?', '아니다. 공통 C 구현 본문을 번역 단위에 넣는다', '그렇다. .c 파일을 include하면 자동으로 헤더만 추출한다', 'C 전처리의 포함은 텍스트 포함입니다. 확장자 때문에 함수 본문을 제외하는 동작은 없습니다.')
    ]
), dict(
    path='arch/x86/include/asm/vdso/getrandom.h',
    title='X86 난수 syscall과 namespace RNG 주소 보정',
    intro='인라인 syscall 제약과 vvar 주소 차이를 이용한 RNG getter를 전체 분석합니다.',
    principle='시스템 호출 ABI는 레지스터 제약으로 표현되며, namespace의 페이지 재배치는 관련 데이터 주소의 차이로 보정할 수 있습니다.',
    use='입력·출력 레지스터와 clobber를 읽고 byte 단위 주소 계산을 설명합니다.',
    area='X86-64 syscall ABI · 인라인 어셈블리 · clobber · namespace · 주소 산술',
    sections=[
        ('전체 구성', 'GPL-2.0 include guard와 !__ASSEMBLY__ 구역에서 asm/unistd.h와 asm/vvar.h를 포함합니다. getrandom_syscall, __vdso_rng_data 매크로, __arch_get_vdso_rng_data로 구성됩니다. 이 헤더 내부에는 CONFIG_X86_32에 따른 int 0x80 fallback 분기가 없습니다. 필요한 vdso_data 자료형과 시간 데이터 매크로 등은 포함 문맥과 함께 봐야 합니다.'),
        ('Syscall 입력과 출력', 'getrandom_syscall(buffer,len,flags)는 long ret를 선언하고 syscall 어셈블리를 사용합니다. =a 출력은 반환 레지스터이고 입력 0은 같은 레지스터에 __NR_getrandom을 넣도록 연결합니다. D는 buffer, S는 len, d는 flags에 대응합니다. x86-64 syscall 문맥에서 각각 RDI, RSI, RDX에 해당하며 syscall 번호와 반환은 RAX를 사용합니다.'),
        ('Clobber와 반환 계약', 'clobber에는 rcx, r11, memory가 명시됩니다. 컴파일러가 그 레지스터와 메모리 효과를 고려하도록 하는 표현이며 그 자체로 사용자 버퍼 크기를 검사하지는 않습니다. ret를 ssize_t로 반환하고 문서 주석은 기록한 바이트 수 또는 음수 오류라고 설명합니다. libc errno를 설정하거나 항상 len을 반환하는 wrapper가 아닙니다. 소스의 asm에는 명시적 volatile 키워드가 없습니다.'),
        ('기본 RNG 데이터 매크로', '__vdso_rng_data는 VVAR(_vdso_rng_data)로 정의됩니다. 기본 getter는 &__vdso_rng_data를 반환합니다. 아키텍처 vvar 심볼 배치를 통해 데이터를 참조하는 것으로, 이 파일에서 RNG 상태 페이지를 할당하거나 키를 생성하지 않습니다.'),
        ('Namespace 조건', 'IS_ENABLED(CONFIG_TIME_NS)와 __vdso_data->clock_mode==VDSO_CLOCKMODE_TIMENS가 모두 참이면 보정한 주소를 반환합니다. 설정이 켜졌다고 모든 task에서 무조건 주소를 바꾸지는 않습니다. 이 조건의 &&는 설정이 거짓일 때 뒤의 모드 접근을 평가하지 않는 논리입니다.'),
        ('주소 차이로 보정', '조건이 참이면 (void *)&__vdso_rng_data에 ((void *)&__timens_vdso_data - (void *)&__vdso_data)를 더합니다. GNU C의 void 포인터 산술 문맥에서 두 시간 데이터 위치의 바이트 차이를 RNG 주소에도 적용합니다. 코드에 4096이나 특정 PAGE_SIZE를 직접 더하는 식은 없습니다. 예를 들어 두 주소 차이가 4096이면 RNG 기준 주소에도 4096을 더하지만 이 예시를 고정 상수로 바꾸어 설명하지 않습니다.'),
        ('구조체 주소와 내용의 차이', '계산은 시간 데이터의 주소 차이를 사용하며 struct vdso_data 내용이나 namespace 시간 offset을 난수 값에 더하는 연산이 아닙니다. 결과는 const vdso_rng_data *이고 실제 generation·ready 확인과 난수 생성은 공통 코드가 담당합니다. 반환 주소를 찾는 과정과 난수 값 생성 과정을 구별해야 합니다.'),
        ('CS 연결과 검증 범위', '모든 함수·매크로·전처리 구역과 어셈블리 피연산자를 설명했습니다. 레지스터 ABI, 컴파일러 clobber 계약, 페이지 배치와 주소 보정이 핵심입니다. 실제 x86 바이너리 실행, time namespace 매핑, syscall 오류 경로를 재현한 시험은 수행하지 않았습니다.')
    ],
    questions=[
        ('getrandom syscall helper에서 flags의 제약은 무엇인가?', 'd이며 x86-64 문맥의 RDX에 대응한다', 'D이며 buffer와 같은 RDI에 전달한다', '대문자 D는 buffer, S는 len, 소문자 d는 flags입니다. 제약 문자의 대소문자와 역할을 구분해야 합니다.'),
        ('RNG 주소 보정에 사용하는 값은?', '두 시간 데이터 심볼 주소의 바이트 차이이다', '시간 namespace의 초 단위 offset이다', '식은 void 포인터끼리의 주소 차이입니다. 데이터 페이지 위치를 옮기는 것이지 시간 값을 난수 데이터에 섞는 연산이 아닙니다.'),
        ('CONFIG_TIME_NS가 켜졌으면 getter가 항상 주소를 보정하는가?', '아니다. clock_mode도 TIMENS여야 한다', '그렇다. 설정 하나만으로 모든 task의 주소가 이동한다', '조건은 설정과 실제 모드 두 항의 AND입니다. 일반 task는 기본 RNG 데이터 주소를 반환합니다.')
    ]
)]
