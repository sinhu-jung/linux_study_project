"""Whole-file pvclock ABI and x86 conversion helpers."""
ROWS = [dict(
    path='arch/x86/include/asm/pvclock-abi.h',
    title='Pvclock 공유 ABI: 고정 배치와 버전 기반 일관성',
    intro='Xen·KVM과 guest가 공유하는 두 구조체의 모든 필드와 상태 비트를 분석합니다.',
    principle='서로 독립적으로 만들어지는 소프트웨어가 메모리를 공유하려면 자료형 크기, 바이트 배치, 갱신 프로토콜을 함께 고정해야 합니다.',
    use='공유 시계의 필드 배치를 계산하고 갱신 중인 값과 일관된 스냅샷을 구분합니다.',
    area='ABI · packed 구조체 · 공유 메모리 · 버전 카운터 · 시간 표현',
    sections=[
        ('파일 범위와 ABI 계약', 'GPL-2.0 표기와 include guard 안에서 !__ASSEMBLY__일 때 두 구조체와 세 비트 매크로를 제공합니다. 별도 include는 없으므로 u32/u64 등의 자료형은 포함 문맥에 의존합니다. 주석은 Xen과 KVM이 사용하는 hypervisor·guest ABI이므로 구조체를 바꾸면 안 된다고 명시합니다. C 안의 사적인 자료구조처럼 필드를 재배치할 수 없습니다.'),
        ('VCPU 정보의 정확한 배치', 'packed pvclock_vcpu_time_info는 version u32(오프셋 0), pad0 u32(4), tsc_timestamp u64(8), system_time u64(16), tsc_to_system_mul u32(24), tsc_shift s8(28), flags u8(29), pad[2](30)를 갖습니다. 크기는 주석과 필드 합계 모두 32바이트입니다. packed라고 pad0나 pad가 사라지는 것이 아니라 명시적인 ABI 바이트로 남습니다.'),
        ('기준값과 보간 계수', 'tsc_timestamp와 system_time은 마지막 갱신의 TSC와 시스템 시간 기준값입니다. guest는 이후 TSC 차이에 tsc_shift와 tsc_to_system_mul을 적용해 더 세밀한 시스템 시간을 계산할 수 있습니다. tsc_shift는 s8이므로 양수뿐 아니라 음수 이동량도 표현합니다. 구조체는 계산에 필요한 값을 담고 있으며 실제 곱셈이나 shift를 여기서 실행하지 않습니다.'),
        ('Wall clock 기준점', 'packed pvclock_wall_clock은 version, sec, nsec의 u32 세 개로 12바이트입니다. 주석상 system time이 0인 시점, 일반적으로 부팅 시점의 wall clock을 나타냅니다. 현재 wall clock을 얻으려면 시스템 시간을 더해야 합니다. 이 구조체의 sec를 현재 시각이나 s64 초로 그대로 해석하지 않습니다. 두 구조체의 version은 각각 자신의 갱신 프로토콜에 참여합니다.'),
        ('홀수·짝수 버전 프로토콜', 'Hypervisor는 필드를 쓰기 전에 version을 증가시켜 홀수로 만들고 쓰기를 마친 뒤 다시 증가시켜 짝수로 만듭니다. Guest는 읽기 전후 버전을 확인해 갱신과 겹친 스냅샷을 버릴 수 있습니다. 단지 두 번 읽은 값이 같다는 것만으로 충분하지 않고 갱신 중인 홀수 상태도 배제해야 합니다. 실제 접근 순서 장벽과 재시도 helper는 다른 파일에 있습니다.'),
        ('세 플래그와 폐기된 의미', 'PVCLOCK_TSC_STABLE_BIT는 1<<0, PVCLOCK_GUEST_STOPPED는 1<<1, PVCLOCK_COUNTS_FROM_ZERO는 1<<2입니다. 이 헤더는 앞의 두 비트의 동작을 실행하지 않고 이름과 숫자를 제공합니다. 마지막 비트는 ABI를 깨뜨렸고 더 이상 사용할 수 없다고 주석에 명시되어 있습니다. 매크로가 남아 있다는 이유로 새 기능 협상에 사용하면 안 됩니다.'),
        ('CS 연결과 검증 한계', '명시적 padding과 고정 크기는 바이너리 프로토콜을 유지하고 버전은 여러 필드를 하나의 스냅샷으로 읽는 데 쓰입니다. packed는 레이아웃 속성이지 락·원자적 읽기·메모리 장벽을 제공하는 속성이 아닙니다. 전체 선언과 주석을 대조했으며 실제 hypervisor와의 상호 운용 시험을 수행한 것은 아닙니다.')
    ],
    questions=[
        ('pvclock_vcpu_time_info에서 flags의 바이트 오프셋은?', '29이다', '28이다', '24~27은 u32 곱셈 계수이고 28은 s8 tsc_shift입니다. flags는 다음 29번 바이트이며 마지막 두 바이트는 명시적 pad입니다.'),
        ('version을 읽기 전후 모두 7로 관찰하면 그 자체로 안정된 스냅샷인가?', '아니다. 7은 홀수이므로 갱신 중일 수 있다', '그렇다. 전후 숫자가 같으면 홀수 여부는 무관하다', '쓰기 시작 시 홀수, 완료 시 짝수로 바뀝니다. 중간에 writer가 멈춰 있으면 두 번 모두 같은 홀수를 볼 수 있으므로 읽기 프로토콜이 이를 거부해야 합니다.'),
        ('pvclock_wall_clock의 sec와 nsec만으로 현재 wall clock을 얻는가?', '아니다. system time이 0인 기준 시각이므로 현재 system time을 더해야 한다', '그렇다. hypervisor가 항상 현재 wall clock을 그 필드에 직접 기록한다', '헤더 주석은 기준점의 의미를 명시합니다. 기준 시각과 이후 경과 시간의 합으로 현재 시각을 구성하는 모델입니다.'),
        ('PVCLOCK_COUNTS_FROM_ZERO를 새 코드에서 유효 기능 비트로 사용해도 되는가?', '안 된다. ABI를 깨뜨려 더 이상 사용할 수 없다는 주석이 있다', '된다. 매크로가 정의되어 있으면 지원이 보장된다', '식별자 존재와 사용 가능한 계약은 다릅니다. 호환성 이력을 읽고 폐기된 의미를 다시 활성화하지 않아야 합니다.')
    ]
), dict(
    path='arch/x86/include/asm/pvclock.h',
    title='Pvclock helper: 버전 재시도와 64×32 고정소수점 계산',
    intro='공개 선언, 공유 값 읽기, x86별 곱셈 구현, 캐시 정렬, 설정별 stub를 전체 분석합니다.',
    principle='락 없이 여러 필드를 읽을 때는 갱신 감지와 접근 순서가 필요하고, 시간 환산에서는 중간 곱의 폭과 shift 순서가 중요합니다.',
    use='홀수 버전을 별도 spin 없이 거부하는 방법과 32비트 CPU에서 긴 곱을 조합하는 원리를 익힙니다.',
    area='버전 스냅샷 · 메모리 장벽 · 고정소수점 · 다중 정밀도 곱셈 · carry · 캐시 정렬 · 조건부 컴파일',
    sections=[
        ('파일 범위와 외부 선언', 'GPL-2.0 include guard 아래 asm/clocksource.h와 asm/pvclock-abi.h를 포함하고 timespec64를 전방 선언합니다. pvclock_clocksource_read와 read_nowd는 u64, pvclock_read_flags는 u8, pvclock_tsc_khz는 unsigned long을 반환합니다. pvclock_set_flags(u8), read_wallclock(wall, vcpu, timespec64 출력), resume(void), touch_watchdogs(void)는 void입니다. 여기에는 이 함수들의 본문이 없으므로 실제 watchdog 정책이나 시간 단조성 보정을 선언만으로 확정할 수 없습니다.'),
        ('Read begin은 홀수를 기다리지 않는다', 'pvclock_read_begin은 src->version & ~1을 unsigned version에 저장한 뒤 virt_rmb()하고 반환합니다. 끝 비트를 지워 짝수로 만들 뿐 홀수가 사라질 때까지 도는 루프는 없습니다. 장벽은 버전 읽기가 이후 공유 데이터 읽기보다 먼저 수행되도록 하는 프로토콜의 일부입니다. 이 helper 자체가 writer를 멈추거나 공유 구조체를 복사하지 않습니다.'),
        ('Read retry와 홀수 거부', 'pvclock_read_retry는 virt_rmb() 후 저장한 version과 src->version의 불일치를 unlikely로 반환합니다. 처음 원본이 7이면 begin은 6을 반환합니다. 재확인 때 여전히 7이면 6!=7, 쓰기가 완료되어 8이면 6!=8이므로 둘 다 재시도합니다. 안정된 8을 읽고 끝까지 8이면 통과합니다. 일반적인 버전 카운터처럼 읽기 사이 완전한 카운터 순환이 없다는 사용 전제도 필요합니다.'),
        ('Scale 함수와 이동 순서', 'pvclock_scale_delta는 u64 delta, u32 mul_frac, int shift를 받아 u64를 반환합니다. shift<0이면 delta >>= -shift, 그 외에는 delta <<= shift를 먼저 수행하고 그 결과에 32비트 분수 계수를 곱합니다. 수학적으로 이동 후 delta를 d라고 하면 floor(d * mul_frac / 2^32)입니다. 이동 전에 곱하는 식과는 버림이나 오버플로에서 달라질 수 있습니다.'),
        ('범위와 정밀도 계약', '함수에는 shift 범위 검사, saturating shift, 오류 반환이 없습니다. C의 유효한 이동량 범위와 입력 계수 계약을 caller가 충족해야 합니다. 오른쪽 이동은 낮은 비트를 버리고 u64 왼쪽 이동은 넘치는 높은 비트를 보존하지 않습니다. mul_frac=0x80000000은 1/2이므로 delta=100, shift=1이면 먼저 200으로 만든 뒤 100을 반환합니다. shift=-1이면 50의 절반인 25입니다.'),
        ('I386의 두 부분 곱', '__i386__ 경로는 delta의 낮은 32비트 L과 높은 32비트 H를 나눠 사용합니다. 첫 mul은 L*mul_frac를 계산하고 그 높은 32비트를 임시로 보존합니다. 이어 H*mul_frac를 계산한 뒤 보존값을 낮은 결과에 add하고 carry를 높은 결과에 adc합니다. 이는 floor(L*M/2^32)+H*M을 조합한 것으로, 원래 64×32 곱을 32비트 내린 결과와 같습니다.'),
        ('I386 레지스터 제약과 carry', 'product는 =A 출력으로 EDX:EAX 쌍에 연결되고 tmp1·tmp2는 =r 출력입니다. 입력 a는 L, 입력 1은 H, 입력 2는 mul_frac로 출력 레지스터와 연결됩니다. xor로 곱셈 계수용 레지스터를 0으로 만든 뒤 add와 adc를 사용하여 낮은 덧셈에서 발생한 carry를 높은 결과에 더합니다. carry 전파를 빼면 경계값에서 긴 정수 계산이 틀립니다.'),
        ('X86-64의 넓은 곱', '__x86_64__ 경로는 mulq로 RDX:RAX에 넓은 곱을 만들고 shrd $32로 높은 곱과 낮은 곱을 이어 오른쪽 32비트 이동 결과를 얻습니다. 계수는 u64로 변환되어 rm 입력을 사용하고 delta는 출력 lo와 같은 입력 0에 연결됩니다. 단순히 C에서 u64 곱을 먼저 잘라 버리고 >>32하는 식과 달리 필요한 높은 곱 비트를 이용합니다. 두 아키텍처가 아니면 #error implement me!로 빌드를 중단합니다.'),
        ('기준 TSC에서 현재 system time으로', '__pvclock_read_cycles는 delta=tsc-src->tsc_timestamp를 구하고 src->tsc_to_system_mul과 src->tsc_shift로 offset을 계산한 뒤 src->system_time+offset을 반환합니다. 예를 들어 기준 TSC=1000, 입력=1100, 계수=0x80000000, shift=0, 기준 system_time=500이면 550입니다. 이 함수 내부에는 버전 재시도나 stable bit 검사가 없으므로 caller가 스냅샷 계약을 관리해야 합니다.'),
        ('ABI 객체와 캐시 정렬 wrapper', 'pvclock_vsyscall_time_info는 pvclock_vcpu_time_info 하나를 담고 SMP_CACHE_BYTES 정렬을 지정합니다. PVTI_SIZE는 내부 32바이트 구조체가 아니라 wrapper의 sizeof입니다. 정렬에 따른 끝 padding 때문에 두 크기가 다를 수 있습니다. 공유 ABI 객체의 packed 속성과 바깥 객체의 캐시 정렬은 서로 다른 층의 레이아웃 선택입니다.'),
        ('설정에 따른 getter와 setter', 'CONFIG_PARAVIRT_CLOCK이면 pvclock_set_pvti_cpu0_va와 pvclock_get_pvti_cpu0_va를 외부 함수로 선언합니다. 설정이 없으면 getter만 static inline으로 제공하여 NULL을 반환합니다. else에 빈 setter stub는 없습니다. 설정을 끈 빌드에서도 setter가 무조건 사용 가능하다고 가정하면 안 됩니다.'),
        ('CS 연결과 검증 범위', '전체 외부 선언과 네 계산·읽기 helper, wrapper와 설정 분기를 다뤘습니다. 핵심은 읽기 재시도와 쓰기 잠금의 차이, 부분 곱과 carry, fixed-point 스케일, ABI 배치와 캐시 정렬의 구별입니다. 계산 예제는 코드의 식을 따른 예시이며 실제 i386/x86-64 어셈블리 실행이나 hypervisor 경쟁 상황을 시험한 결과는 아닙니다.')
    ],
    questions=[
        ('begin에서 원본 version=7을 보고 retry에서도 7을 보면 결과는?', 'begin이 6을 저장했으므로 retry는 참이다', '두 원본 숫자가 7로 같으므로 retry는 거짓이다', 'begin은 끝 비트를 지웁니다. 따라서 writer가 홀수 상태에서 멈춰 있어도 저장된 짝수와 현재 홀수가 달라져 갱신 중인 자료를 채택하지 않습니다.'),
        ('delta=100, mul_frac=0x80000000, shift=-1이면 scale 결과는?', '25이다', '100이다', '음수 shift는 먼저 100>>1=50을 만듭니다. 계수는 2^31/2^32=1/2이므로 최종 25입니다. shift와 분수 계수 두 단계를 모두 반영해야 합니다.'),
        ('i386에서 낮은 결과에 add한 뒤 높은 결과에 adc하는 이유는?', '낮은 덧셈의 carry를 높은 32비트에 반영하기 위해서다', 'signed 음수 계수를 양수로 바꾸기 위해서다', '두 부분 곱을 합치면 낮은 32비트에서 넘침이 생길 수 있습니다. adc는 carry를 높은 결과에 더하여 64비트 정수의 정확한 합을 구성합니다.'),
        ('__pvclock_read_cycles만 호출하면 일관된 스냅샷이 자동으로 보장되는가?', '아니다. 이 함수에는 버전 검사 루프가 없다', '그렇다. system_time을 읽는 동작이 구조체 전체를 잠근다', '이 helper는 뺄셈·스케일·덧셈만 수행합니다. 여러 공유 필드의 일관성은 바깥의 begin/retry 같은 프로토콜로 확보해야 합니다.'),
        ('PVTI_SIZE를 항상 32로 대체해도 되는가?', '안 된다. 캐시 정렬된 wrapper의 sizeof라 끝 padding을 포함할 수 있다', '된다. 내부 packed 객체가 32바이트면 바깥 객체도 무조건 32바이트이다', '바깥 구조체는 SMP_CACHE_BYTES 정렬을 요구합니다. 배열 원소도 그 정렬을 만족하도록 sizeof에 padding이 포함될 수 있으므로 매크로가 지정한 실제 wrapper 크기를 사용해야 합니다.')
    ]
)]
