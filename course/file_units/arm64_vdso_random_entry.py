"""Whole-file ARM64 random entry and architecture hooks."""
ROWS = [dict(
    path='arch/arm64/kernel/vdso/vgetrandom.c',
    title='ARM64 vDSO 난수 진입점: FPSIMD 기능 분기와 지원 조회',
    intro='공개 getrandom wrapper의 자료형 선언과 두 실행 경로를 전체 분석합니다.',
    principle='빠른 구현의 하드웨어 지원 여부와 기본 syscall 지원 여부를 구별해야 하며, 기능 조회는 일반 데이터 요청과 다른 계약을 가집니다.',
    use='지원 조회의 특수 인수 조합과 fallback에서 opaque state를 전달하지 않는 이유를 이해합니다.',
    area='CPU 기능 선택 · vDSO ABI · 기능 조회 · syscall fallback · opaque state',
    sections=[
        ('전체 선언과 의존성', 'GPL-2.0 표기 뒤 uapi/asm-generic/errno.h를 포함합니다. typeof(__cvdso_getrandom) __kernel_getrandom으로 공통 함수의 자료형을 이용한 원형을 선언하고 같은 공개 함수 본문을 정의합니다. 관련 Makefile이 공통 구현을 -include로 제공하는 문맥과 함께 읽어야 합니다. typeof 선언이 공통 함수를 이 시점에 실행하는 것은 아닙니다.'),
        ('다섯 인수와 반환형', '__kernel_getrandom은 buffer, size_t len, unsigned int flags, opaque_state, size_t opaque_len을 받고 ssize_t를 반환합니다. 앞 세 인수는 난수 요청, 뒤 두 인수는 vDSO 상태 영역에 관한 인터페이스입니다. 반환값을 bool 성공 여부나 항상 len과 같은 값으로 단순화하지 않습니다.'),
        ('FPSIMD가 지원되는 경로', 'alternative_has_cap_likely(ARM64_HAS_FPSIMD)가 참이면 다섯 인수를 그대로 __cvdso_getrandom에 전달하고 결과를 반환합니다. 이 wrapper 자체에 ChaCha 연산·키 재생성·상태 잠금 구현은 없습니다. FPSIMD 조건은 공통 경로를 선택하는 조건이지 모든 호출이 syscall 없이 성공한다는 보장은 아닙니다.'),
        ('미지원 시 특수 조회 거부', 'FPSIMD 경로를 선택하지 못했을 때 opaque_len==~0UL, buffer==NULL, len==0, flags==0 네 조건이 모두 참이면 -ENOSYS를 반환합니다. 확인한 공통 구현에서 이 조합은 opaque_state에 상태 영역의 크기·mmap 설정 등을 알려주는 조회입니다. wrapper의 이 분기는 조회를 syscall의 빈 요청으로 바꾸지 않고 명시적으로 지원하지 않음을 알립니다. opaque_state가 NULL인지 검사하는 조건은 여기에 없습니다.'),
        ('일반 요청의 syscall 전환', '위 특수 조합이 아니면 getrandom_syscall(buffer,len,flags)를 호출합니다. opaque_state와 opaque_len은 이 호출에 전달하지 않습니다. 따라서 FPSIMD가 없다는 이유만으로 일반 getrandom 요청을 모두 ENOSYS로 끝내는 코드가 아닙니다. 예를 들어 len=0이어도 opaque_len이 sentinel이 아니면 이 wrapper는 일반 fallback을 선택합니다.'),
        ('CS 연결과 검증 범위', '전체 선언·조건·반환 경로를 다뤘습니다. 하드웨어 기능 탐지와 사용자 API 기능 조회, opaque state를 사용하는 빠른 구현과 기본 syscall의 차이가 핵심입니다. 공통 난수 알고리즘 전체는 별도 파일 범위이며 이 학습으로 완료 집계하지 않습니다. 실제 ARM64 FPSIMD 유무별 실행 시험은 수행하지 않았습니다.')
    ],
    questions=[
        ('FPSIMD가 없으면 모든 난수 요청이 -ENOSYS인가?', '아니다. 특수 조회 조합 외에는 getrandom syscall로 전환한다', '그렇다. 이 wrapper는 CPU 기능이 없으면 항상 실패한다', 'ENOSYS는 opaque_len sentinel과 NULL buffer·0 len·0 flags가 모두 맞는 조회 경로입니다. 일반 요청은 앞 세 인수를 syscall helper에 전달합니다.'),
        ('지원 조회를 나타내는 인수 조합은?', 'opaque_len=~0UL, buffer=NULL, len=0, flags=0이다', 'buffer만 NULL이면 나머지 인수와 관계없이 조회이다', '조건은 네 항의 AND입니다. 일반적인 빈 난수 요청과 상태 영역 정보를 묻는 특수 호출을 구분합니다.'),
        ('getrandom_syscall fallback에 opaque_state도 전달하는가?', '아니다. buffer·len·flags 세 인수만 전달한다', '그렇다. 다섯 인수가 그대로 syscall 레지스터에 들어간다', '상태 영역은 vDSO 인터페이스의 확장 부분입니다. wrapper의 fallback 호출 표현을 보면 기본 syscall에 전달하는 인수는 세 개뿐입니다.')
    ]
), dict(
    path='arch/arm64/include/asm/vdso/getrandom.h',
    title='ARM64 난수 hook: SVC ABI와 time namespace의 실제 RNG 페이지',
    intro='난수 syscall helper와 namespace별 공유 데이터 주소 선택을 전체 분석합니다.',
    principle='가상 주소의 첫 페이지가 namespace용으로 바뀌어도 난수 공유 데이터는 실제 vvar 페이지에서 찾아야 합니다.',
    use='x0·x1·x2·x8의 전달 규약과 페이지 단위 포인터 이동을 설명합니다.',
    area='시스템 호출 ABI · shared memory · namespace · 포인터 산술 · 페이지 크기',
    sections=[
        ('전체 구성과 가시성', 'GPL-2.0 include guard 안의 !__ASSEMBLY__ 구역에서 asm/unistd.h, asm/vdso/vsyscall.h, vdso/datapage.h를 포함합니다. getrandom_syscall과 __arch_get_vdso_rng_data 두 always_inline 함수를 정의합니다. 별도 난수 생성 루프나 ChaCha 구현은 없습니다.'),
        ('Syscall 레지스터 연결', 'getrandom_syscall은 buffer를 x0, size_t len을 x1, unsigned int flags를 x2, __NR_getrandom을 x8에 연결합니다. x0의 long ret를 출력으로 받는 asm volatile svc #0에 memory clobber를 지정하고 결과를 ssize_t로 반환합니다. C 문서 주석은 기록한 바이트 수 또는 음수 오류라고 설명합니다. 여기서는 libc errno를 설정하거나 항상 len 바이트가 반환된다고 보장하지 않습니다.'),
        ('메모리 효과와 책임', 'memory clobber는 버퍼에 대한 syscall의 메모리 효과를 컴파일러에 알립니다. 사용자 버퍼의 크기 검사나 flags 해석을 이 helper가 직접 구현한다는 뜻은 아닙니다. 입력 포인터와 길이를 그대로 시스템 호출로 전달하며 opaque state 인수는 없습니다.'),
        ('기본 RNG 데이터 주소', '__arch_get_vdso_rng_data는 기본적으로 &_vdso_rng_data를 const vdso_rng_data *로 반환합니다. 데이터 객체를 읽는 주소를 얻는 함수이며 여기서 키를 생성하거나 generation을 증가시키지 않습니다. 페이지가 이미 유효하게 매핑되어 있다는 호출 문맥이 필요합니다.'),
        ('Time namespace의 두 페이지', '주석은 task가 time namespace에 속하면 VVAR_DATA_PAGE_OFFSET 쪽이 namespace 전용 페이지이고 VVAR_TIMENS_PAGE_OFFSET 쪽이 실제 vvar 페이지라고 설명합니다. RNG 데이터는 실제 페이지에 있으므로 clock namespace용 첫 페이지의 같은 위치를 그대로 읽으면 안 됩니다. 시간 데이터의 namespace 선택과 난수 데이터의 소유 위치는 구별해야 합니다.'),
        ('조건과 주소 계산', 'IS_ENABLED(CONFIG_TIME_NS)와 _vdso_data->clock_mode==VDSO_CLOCKMODE_TIMENS가 모두 참이면 (void *)&_vdso_rng_data + VVAR_TIMENS_PAGE_OFFSET * (1UL << CONFIG_PAGE_SHIFT)를 반환합니다. 포함된 ARM64 정의에서 그 offset은 1이므로 한 페이지 뒤입니다. GNU C의 void 포인터 산술은 여기서 바이트 거리로 사용됩니다. PAGE_SHIFT=12인 예에서는 4096바이트를 더하지만 코드는 페이지 크기를 4096으로 고정하지 않습니다.'),
        ('단락 평가와 검증 범위', '&& 조건은 namespace 설정이 꺼졌을 때 뒤 clock_mode 접근을 평가하지 않는 논리를 갖습니다. 이 파일에 페이지 할당·매핑·namespace 변경 동기화 루프는 없습니다. 전체 함수와 조건·레지스터·주소 계산을 분석했으며 실제 namespace 환경의 난수 syscall과 매핑 실행 시험을 수행한 결과는 아닙니다.')
    ],
    questions=[
        ('getrandom syscall에서 flags와 syscall 번호는 각각 어느 레지스터인가?', 'flags는 x2, 번호는 x8이다', 'flags는 x8, 번호는 x2이다', '앞의 x0와 x1은 buffer와 len입니다. 결과는 x0로 받으며 syscall 번호는 별도 x8에 전달합니다.'),
        ('time namespace 모드에서 RNG getter가 한 페이지 뒤를 반환하는 이유는?', 'RNG 정보가 namespace용 첫 페이지가 아니라 실제 vvar 페이지에 있기 때문이다', '난수 버퍼가 항상 두 페이지 크기여야 하기 때문이다', '이동 대상은 사용자 출력 버퍼가 아니라 공유 RNG 메타데이터 주소입니다. namespace의 페이지 배치 계약을 따릅니다.'),
        ('이 getter가 항상 4096바이트를 더하는가?', '아니다. 조건이 참일 때 CONFIG_PAGE_SHIFT에 따른 페이지 크기를 더한다', '그렇다. 모든 ARM64 빌드에서 상수 4096을 사용한다', '식은 1UL << CONFIG_PAGE_SHIFT이며 기본 경로에서는 아예 주소 이동을 하지 않습니다. 설정과 런타임 모드 조건을 함께 봐야 합니다.')
    ]
)]
