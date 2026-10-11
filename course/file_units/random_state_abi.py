"""Whole-file random UAPI and internal vDSO state definitions."""
ROWS = [dict(
    path='include/vdso/getrandom.h',
    title='vDSO 난수 상태: 출력 배치와 다음 키의 union',
    intro='상태 구조체의 모든 필드와 stackless ChaCha 함수·공개 함수 선언을 분석합니다.',
    principle='비밀 상태와 출력 버퍼를 하나의 저장 영역에 배치하더라도 노출 범위와 동시 접근 계약은 별도로 관리해야 합니다.',
    use='배치 크기를 계산하고 generation·pos·in_use가 담당하는 서로 다른 역할을 설명합니다.',
    area='union · 메모리 배치 · 버퍼링 · 재진입 · 암호 상태 · 함수 계약',
    sections=[
        ('전체 상수와 의존성', 'GPL-2.0 include guard 아래 linux/types.h를 포함하고 CHACHA_KEY_SIZE=32, CHACHA_BLOCK_SIZE=64를 정의합니다. 단위는 뒤 배열과 주석상 바이트입니다. 이 파일에는 실제 ChaCha round 구현이나 syscall 본문이 없습니다.'),
        ('Batch와 key의 연속 배치', 'vgetrandom_state의 anonymous union 안 anonymous struct는 u8 batch[64*3/2]와 u32 key[32/sizeof(u32)]를 가집니다. 따라서 batch는 96바이트, key는 8개 u32로 32바이트입니다. 주석상 batch는 출력으로 소비할 1.5블록이고 key는 다음 배치 생성에 사용할 키입니다. 두 블록의 출력 전체 128바이트를 전부 사용자 난수로 반환하는 구조라고 해석하면 안 됩니다.'),
        ('Union 전체 보기', '다른 union 멤버는 u8 batch_key[64*2]로 128바이트입니다. 동일 저장 공간을 배치와 키로 나누어 보거나 한 번에 두 블록으로 채울 수 있습니다. 96+32+128바이트를 각각 따로 할당하는 구조가 아닙니다. union 내부 표현과 이후 상태 필드를 포함한 전체 sizeof는 구분해야 합니다.'),
        ('Generation과 소비 위치', 'u64 generation은 키 생성 당시 vDSO RNG 데이터의 generation 스냅샷입니다. u8 pos는 batch에서 다음 사용 가능한 바이트의 offset입니다. generation은 소비한 바이트 수가 아니고 pos는 다음 키의 generation 번호가 아닙니다. 어떤 조건에서 다시 seed를 받고 배치를 채우는지는 공통 구현의 책임입니다.'),
        ('재진입 표시의 범위', 'bool in_use는 주석상 같은 스레드의 signal handler가 상태를 재사용할 때의 reentrancy guard입니다. 구조체 필드 선언 자체가 atomic lock을 구현하지 않습니다. 이를 여러 스레드가 동시에 같은 상태를 써도 안전하다는 보장으로 해석하지 않습니다. 전체 구조체 크기는 ABI 정렬과 끝 padding에 영향을 받으므로 128바이트라고 고정하면 안 됩니다.'),
        ('Stackless ChaCha 선언', '__arch_chacha20_blocks_nostack(u8 *dst_bytes, const u32 *key, u32 *counter, size_t nblocks)는 void 외부 함수입니다. 계약은 양수 블록 수에 대해 nonce=0 ChaCha20 출력을 생성하고 dst에 nblocks*64바이트를 기록하며 32바이트 키를 읽고 8바이트 counter를 입력으로 읽어 반환 시 갱신하는 것입니다. 주석은 stack 및 전달된 매개변수 영역 밖에 쓰지 않아 fork된 자식으로 stack 데이터가 새는 위험을 줄이려는 목적을 명시합니다. 선언만으로 구현이 이 계약을 지켰다고 검증한 것은 아닙니다.'),
        ('공개 getrandom 원형', '__vdso_getrandom은 buffer,len,flags,opaque_state,opaque_len 다섯 인수와 ssize_t 반환형을 선언합니다. 주석은 __cvdso_getrandom으로 위임하는 기본 모델을 설명합니다. 아키텍처에 따라 공개 이름과 추가 기능 분기가 다를 수 있으며 확인한 ARM64 진입점은 __kernel_getrandom 이름과 FPSIMD 조건을 사용합니다. 이 원형 하나가 모든 아키텍처에 같은 심볼을 자동 생성하는 것은 아닙니다.'),
        ('CS 연결과 범위', '전체 상수·구조체·필드·함수 선언과 계약을 설명했습니다. union에 의한 공간 공유, 출력 버퍼와 비밀키의 경계, 상태 버전과 재진입의 차이를 학습합니다. 실제 난수 품질·암호 구현·다중 스레드 실행·stackless 어셈블리 준수 검증은 이 파일 분석 범위가 아닙니다.')
    ],
    questions=[
        ('batch와 key의 크기는 각각 얼마인가?', '96바이트와 32바이트이다', '128바이트와 64바이트이다', '블록 64바이트의 1.5배가 batch이고 키 상수는 32바이트입니다. 두 영역을 합친 128바이트를 batch_key로 함께 볼 수 있습니다.'),
        ('batch_key가 추가로 별도 128바이트를 할당하는가?', '아니다. batch와 key를 담은 struct와 union 저장 공간을 공유한다', '그렇다. 상태마다 같은 출력이 별도 복사본으로 두 번 저장된다', 'union은 같은 위치를 다른 멤버 표현으로 보는 구조입니다. 멤버 크기를 모두 더해서 메모리 사용량을 계산하지 않습니다.'),
        ('in_use 필드가 있다는 것만으로 여러 스레드의 공유 상태 접근이 안전한가?', '아니다. 주석은 같은 스레드의 signal 재진입 용도를 설명한다', '그렇다. 모든 bool 필드는 자동 mutex이다', 'bool 선언은 잠금 구현이 아닙니다. 스레드 간 동시 접근 계약은 구현과 외부 동기화를 별도로 확인해야 합니다.'),
        ('stackless ChaCha helper가 갱신하는 counter의 크기는?', '8바이트이다', '키와 같으므로 32바이트이다', '원형의 counter는 u32 포인터이지만 주석 계약은 8바이트 counter입니다. 포인터가 가리키는 단일 원소 폭과 전체 입력·출력 영역 크기를 구분합니다.')
    ]
), dict(
    path='include/uapi/linux/random.h',
    title='난수 UAPI: ioctl 번호·getrandom 플래그·opaque 조회 구조체',
    intro='사용자 공간과 공유하는 모든 명령·플래그·자료형을 분석하고 오래된 주석을 실제 구현과 대조합니다.',
    principle='ABI 상수가 남아 있다고 기능의 과거 의미까지 유지되는 것은 아니며, 버퍼 크기와 entropy 기여량도 서로 다른 값입니다.',
    use='ioctl 방향과 인수 표현, flexible array, 상태 조회 결과의 크기를 읽습니다.',
    area='UAPI · ioctl · flexible array · ABI 유지 · 플래그 · 예약 필드',
    sections=[
        ('전체 구성과 라이선스', 'GPL-2.0 WITH Linux-syscall-note 표기와 _UAPI_LINUX_RANDOM_H guard 아래 linux/types.h, linux/ioctl.h, linux/irqnr.h를 포함합니다. 역사적 주석의 파일 이름은 include/linux/random.h이지만 실제 분석 대상은 include/uapi/linux/random.h입니다. 명령 정의와 자료형을 제공하며 함수 본문은 없습니다.'),
        ('조회·count 명령', 'RNDGETENTCNT는 _IOR(\'R\',0x00,int), RNDADDTOENTCNT는 _IOW(\'R\',0x01,int)입니다. 방향 표기는 사용자 관점의 읽기·쓰기를 구분합니다. 헤더는 count의 추가·감소라고 설명하지만 v6.12 random_ioctl은 음수 ent_count를 -EINVAL로 거부합니다. RNDGETENTCNT 구현은 input_pool.init_bits를 사용자에게 쓰므로 이름만으로 매 순간의 물리적 entropy 양을 정확히 측정한다고 확대하지 않습니다.'),
        ('Pool 명령과 남은 ABI 번호', 'RNDGETPOOL은 _IOR(\'R\',0x02,int[2])이고 헤더 자체에 2.6.9-rc2에서 제거됐다고 적혀 있습니다. 확인한 v6.12 switch에도 처리 case가 없어 기본 -EINVAL입니다. RNDADDENTROPY는 _IOW(\'R\',0x03,int[2])입니다. 숫자 정의의 존재와 현재 지원 여부는 서로 다릅니다. ioctl 전체 숫자의 인코딩은 포함된 아키텍처 ioctl 정의와 연결됩니다.'),
        ('Flexible array 입력', 'rand_pool_info는 int entropy_count, int buf_size, __u32 buf[]입니다. buf는 유연한 배열 멤버로 구조체 뒤에 데이터가 이어집니다. 실제 random_ioctl은 앞 두 int를 읽고 두 번째 값을 byte 길이 len으로 사용해 그 뒤 데이터를 import합니다. __u32 배열 표기만 보고 buf_size가 언제나 u32 원소 개수라고 해석하면 안 됩니다. payload 길이와 entropy 기여량은 다른 필드입니다.'),
        ('초기화 명령의 주석과 현실', 'RNDZAPENTCNT는 _IO(\'R\',0x04), RNDCLEARPOOL은 _IO(\'R\',0x06)입니다. 주석은 count 초기화·pool 초기화라고 설명하지만 v6.12 구현은 두 명령 모두 CAP_SYS_ADMIN 검사 후 효과 없이 0을 반환합니다. 주석의 오래된 동작을 현재 보안 효과로 설명하면 안 됩니다. RNDRESEEDCRNG는 _IO(\'R\',0x07)이며 실제 구현은 권한 검사 후 CRNG가 준비되지 않았으면 -ENODATA, 준비되면 crng_reseed를 호출합니다.'),
        ('권한과 선언의 한계', '헤더의 Superuser only 설명은 실제 구현에서 CAP_SYS_ADMIN 검사로 나타납니다. RNDADDTOENTCNT와 RNDADDENTROPY도 이 검사를 수행합니다. 매크로 정의 자체가 접근을 차단하는 것이 아니라 처리 함수가 권한을 확인합니다. 실제 ioctl을 호출하거나 시스템 RNG 상태를 변경하는 실험은 이 학습에서 수행하지 않았습니다.'),
        ('Getrandom 플래그 전체', 'GRND_NONBLOCK=0x0001은 블록하지 않고 필요한 경우 EAGAIN을 반환하도록 하는 플래그, GRND_RANDOM=0x0002는 이 헤더 주석상 효과 없음, GRND_INSECURE=0x0004는 비암호학적 난수 바이트 반환을 허용하는 플래그입니다. 비트 정의가 모든 조합의 유효성까지 보장하지는 않습니다. 안전한 키 생성을 위해 INSECURE를 무조건 쓰라는 권고가 아닙니다.'),
        ('Opaque 상태 할당 조회 결과', 'vgetrandom_opaque_params는 __u32 size_of_opaque_state, mmap_prot, mmap_flags, reserved[13]으로 총 16개 u32, 64바이트입니다. 앞 필드의 주석 태그는 size_per_opaque_state라고 적혀 있지만 실제 C 멤버 이름은 size_of_opaque_state입니다. 상태 영역 자체가 이 구조체 안에 들어 있는 것이 아니라 그 크기와 mmap 옵션을 알려주는 결과 구조체입니다.'),
        ('예약 영역과 ABI 확장', 'reserved[13]은 미래 사용을 위해 남긴 공간입니다. 조회 결과 구조체의 64바이트 크기와 실제 vgetrandom_state의 sizeof를 혼동하지 않습니다. 공통 구현의 조회 경로는 이 예약 배열을 0으로 채우지만 여기의 선언 자체는 메모리를 초기화하지 않습니다. 헤더만 포함한다고 상태 페이지가 할당되지도 않습니다.'),
        ('CS 연결과 검증 범위', '모든 ioctl 상수 7개, 두 구조체, getrandom 플래그 3개와 주석을 다뤘습니다. ABI 유지와 폐기 기능, 선언과 권한 검사, 바이트 길이와 원소 수의 구별이 핵심입니다. random.c의 관련 ioctl 부분을 교차 확인했지만 그 큰 구현 파일 전체를 완료 집계하지 않습니다.')
    ],
    questions=[
        ('v6.12에서 RNDADDTOENTCNT에 음수 count를 주면 감소 처리하는가?', '아니다. 구현은 -EINVAL로 거부한다', '그렇다. 오래된 헤더 주석대로 항상 감소한다', '선언 주석과 현재 구현을 함께 읽어야 합니다. random_ioctl의 음수 검사가 실제 동작을 결정합니다.'),
        ('RNDCLEARPOOL 성공 반환이 v6.12에서 pool을 지웠다는 증거인가?', '아니다. 권한 검사 후 효과 없이 성공한다', '그렇다. 이름에 CLEAR가 있으므로 반드시 전체 pool을 지운다', '확인한 구현은 RNDZAPENTCNT와 함께 No longer has any effect 경로입니다. 성공 상태와 과거 부작용의 유지 여부는 다릅니다.'),
        ('rand_pool_info의 buf_size는 구현에서 어떤 단위로 쓰이는가?', '뒤 payload의 바이트 길이이다', '뒤 __u32 원소의 개수이다', 'random_ioctl은 두 번째 int를 len으로 읽어 import_ubuf에 바이트 길이로 전달합니다. 포인터의 원소형만으로 길이 단위를 추정하지 않습니다.'),
        ('vgetrandom_opaque_params의 64바이트가 실제 난수 상태 크기인가?', '아니다. 실제 상태 크기는 size_of_opaque_state 필드로 알려준다', '그렇다. 모든 아키텍처 상태는 무조건 64바이트이다', '이 구조체는 크기와 mmap 설정을 담는 조회 결과입니다. 내부 난수 상태 구조체와 역할이 다릅니다.')
    ]
)]
