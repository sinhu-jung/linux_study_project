"""Whole-file legacy and modern time ABI declarations."""
ROWS = [dict(
    path='include/vdso/time32.h', title='고정 32비트 시간 표현: 초와 소수 단위 구분',
    intro='old_time32_t와 두 구조체의 모든 필드를 읽습니다.',
    principle='초의 표현 폭과 소수 부분의 단위는 서로 독립적인 ABI 속성입니다.',
    use='호환성 코드에서 timeval과 timespec을 혼동하거나 32비트 초를 새 인터페이스로 사용하는 일을 피합니다.',
    area='ABI · 고정 폭 정수 · 2038년 경계 · 단위 변환',
    sections=[
        ('파일 전체와 포함 전제', 'GPL-2.0 표시와 guard 안에 typedef 하나와 구조체 두 개가 전부입니다. 별도 include가 없으므로 s32가 이미 정의된 문맥에서 포함해야 합니다. 함수나 값 검사, 변환 매크로는 없습니다.'),
        ('초의 표현 폭', 'old_time32_t는 s32의 별칭입니다. 64비트 커널에서 사용하더라도 이 자료형의 초 필드는 32비트 signed입니다. Unix epoch 기준 절대 시각으로 쓰면 최대 양수 초 이후의 시각을 같은 양수 범위에 저장할 수 없는 2038년 문제가 생깁니다. 이 파일 자체가 epoch를 더하거나 래핑을 추적하지는 않습니다.'),
        ('두 구조체의 차이', 'old_timespec32는 old_time32_t tv_sec와 s32 tv_nsec를 가지며 소수 단위는 나노초입니다. old_timeval32는 같은 초 자료형과 s32 tv_usec를 가지며 소수 단위는 마이크로초입니다. 필드 개수와 폭이 비슷해도 같은 바이트를 그대로 다른 구조체로 해석하면 단위가 1000배 달라집니다.'),
        ('폭과 유효성은 별개', 'tv_nsec와 tv_usec가 s32라는 것만으로 각각 0..999999999와 0..999999 범위를 자동 보장하지 않습니다. 선언에는 검사나 정규화 코드가 없습니다. 값의 의미와 허용 범위는 이 자료를 받는 API가 확인해야 합니다.')
    ],
    questions=[
        ('64비트 커널에서 old_time32_t의 폭은?', '여전히 signed 32비트이다', '자동으로 signed 64비트가 된다', 'typedef 대상이 s32이므로 호스트의 long 폭과 무관합니다. 호환 ABI를 보존하기 위한 표현입니다.'),
        ('old_timespec32의 tv_nsec=1000을 old_timeval32의 tv_usec=1000으로 그대로 옮기면 같은 시간인가?', '아니다. 1마이크로초와 1000마이크로초로 다르다', '그렇다. 두 필드가 s32이므로 같은 의미이다', '정수의 비트 폭은 단위를 결정하지 않습니다. 나노초에서 마이크로초로 변환할 때는 1000으로 나누어야 합니다.')
    ]
), dict(
    path='include/linux/time32.h', title='구형 시간 호환 계층: timer, utime, timex 구조체와 변환 선언',
    intro='2038년 한계를 가진 인터페이스의 전체 자료형과 사용자 메모리 변환 경계를 분석합니다.',
    principle='호환 ABI는 기존 표현을 유지하고 커널 내부 계산에는 더 넓은 표현으로 옮기는 경계가 필요합니다.',
    use='old_* 구조체가 남아 있는 이유와 새 코드에서 대체 자료형을 선택해야 하는 이유를 이해합니다.',
    area='호환성 · ABI · 2038년 문제 · 사용자 메모리 · 예약 공간',
    sections=[
        ('전체 파일의 의도', 'guard와 주석은 32비트 아키텍처의 구형 time_t가 2038년에 넘치는 인터페이스이며 새 코드는 time64_t/timespec64를 써야 한다고 설명합니다. 사용되지 않게 된 구형 인터페이스는 제거하라는 지침도 있습니다. time64.h, timex.h, vdso/time32.h를 포함하며 이 파일에는 실제 변환 함수 본문이 없습니다.'),
        ('구형 timer와 파일 시각', 'old_itimerspec32는 old_timespec32 두 개를 it_interval과 it_value로 보관합니다. old_utimbuf32는 old_time32_t actime과 modtime을 가집니다. 후자는 접근 시각과 수정 시각을 초 단위로 담는 형태이며 나노초 필드가 없습니다. 구조체 선언만으로 timer를 실행하거나 파일 시각을 변경하지 않습니다.'),
        ('Old timex의 기본 필드', 'old_timex32의 modes만 u32이고 offset, freq, maxerror, esterror, status, constant, precision, tolerance는 s32입니다. time은 old_timeval32로 들어갑니다. 이 폭은 호환 레이아웃의 일부이며 상태나 조정 단위의 모든 정책이 이 파일 안에 정의된 것은 아닙니다. 필드 이름을 근거로 freq를 곧바로 정수 Hz로 단정하지 않습니다.'),
        ('Old timex의 나머지 필드', 'time 뒤에는 tick, ppsfreq, jitter, shift, stabil, jitcnt, calcnt, errcnt, stbcnt, tai가 모두 s32로 이어집니다. 끝에는 이름 없는 s32:32 비트필드가 열한 개 있습니다. 이들은 접근 가능한 새 상태 변수 이름이 아니라 레이아웃에 공간을 남기는 선언입니다. 저장 공간이 존재한다고 자동으로 0으로 초기화되는 것은 아닙니다.'),
        ('Timespec과 timer 복사 선언', 'get_old_timespec32는 timespec64 출력 포인터와 const void __user 입력을, put_old_timespec32는 const timespec64 입력과 void __user 출력을 받습니다. itimerspec 버전은 old_itimerspec32 __user 포인터와 itimerspec64 포인터를 명시합니다. 반환형은 int입니다. __user는 사용자 주소 공간 경계를 나타내며 단순한 커널 포인터 대입으로 대체할 수 있는 계약이 아닙니다.'),
        ('Timex 변환 선언의 인자 순서', '__kernel_timex를 전방 선언한 뒤 get_old_timex32는 커널 결과 포인터를 먼저, 구형 사용자 입력 포인터를 나중에 받습니다. put_old_timex32는 구형 사용자 출력 포인터를 먼저, const 커널 입력 포인터를 나중에 받습니다. timespec put과 인자 순서가 동일하다고 외우지 말고 각 시그니처를 확인합니다. 구체적인 overflow나 복사 오류 처리는 본문을 별도로 읽어야 합니다.'),
        ('나노초에서 구형 timeval로', 'ns_to_kernel_old_timeval은 s64 나노초를 받아 __kernel_old_timeval을 값으로 반환하는 외부 선언입니다. 반환형은 old_timeval32가 아닙니다. 이름에 old가 공통으로 들어가더라도 고정 32비트 구조체와 아키텍처의 구형 커널 long 기반 표현을 같은 타입으로 취급하지 않습니다.'),
        ('학습 경계', '이 파일 전체는 자료형과 함수 선언의 호환 계층입니다. 선언된 함수 구현의 동작까지 작성 완료로 세지 않습니다. CS 핵심은 오래된 ABI 보존, 내부 표현으로의 변환, 타입·단위와 함수 인자 순서, 미래 입력 범위를 고려한 인터페이스 설계입니다.')
    ],
    questions=[
        ('새 코드가 구형 time32 인터페이스를 기본 선택으로 사용해야 하는가?', '아니다. 주석은 time64_t와 timespec64 기반 대체 인터페이스를 지시한다', '그렇다. 호환성이 있으므로 모든 새 코드에 권장한다', '호환 구조체가 남아 있는 것과 신규 사용 권장은 다릅니다. 주석은 사용이 사라진 구형 인터페이스의 제거까지 언급합니다.'),
        ('old_timex32의 끝에 있는 이름 없는 s32:32 선언은 몇 개인가?', '열한 개이다', '한 개이며 32바이트 배열이다', '원본은 4개, 4개, 3개로 선언합니다. 비트필드 폭과 배열 길이를 혼동하지 않아야 합니다.'),
        ('put_old_timex32에서 첫 인자는 무엇인가?', '구형 사용자 공간 출력 구조체 포인터이다', 'const 커널 __kernel_timex 입력 포인터이다', 'get/put 이름만 보고 다른 변환 함수의 인자 순서를 추정하지 않습니다. 선언은 old_timex32 __user *를 첫 번째로 둡니다.'),
        ('ns_to_kernel_old_timeval의 반환형은 old_timeval32인가?', '아니다. __kernel_old_timeval이다', '그렇다. old라는 이름이 붙은 timeval은 모두 같다', '고정 32비트 구조체와 __kernel_long_t 기반 구형 구조체는 별개입니다. 실제 typedef와 ABI를 확인해야 합니다.')
    ]
), dict(
    path='include/uapi/linux/time_types.h', title='공개 시간 자료형: 새 timespec과 구형·소켓 timeval',
    intro='새 시간 ABI와 구형 시간 ABI의 여섯 구조체를 필드 단위로 비교합니다.',
    principle='구조체의 이름이나 총 크기보다 각 필드의 폭과 단위를 명확하게 정의하는 것이 ABI의 핵심입니다.',
    use='커널 내부 timespec64를 사용자 메모리의 __kernel_timespec과 그대로 같은 것으로 취급하지 않습니다.',
    area='UAPI · 고정 폭 자료형 · ABI 레이아웃 · 단위 · 하위 호환',
    sections=[
        ('파일 전체와 라이선스', 'GPL-2.0 WITH Linux-syscall-note 표시, guard, linux/types.h include 뒤 여섯 구조체가 정의됩니다. 값 변환이나 유효성 검사 함수는 없습니다. 사용자 공간과 경계에서 사용할 형태를 정의하는 파일입니다.'),
        ('새 timespec과 timer', '__kernel_timespec은 __kernel_time64_t tv_sec와 long long tv_nsec입니다. __kernel_itimerspec은 이 구조체 두 개를 it_interval과 it_value로 가집니다. 내부 timespec64는 tv_nsec가 long이므로 특히 long이 32비트인 환경에서 같은 필드 폭이라고 가정하면 안 됩니다.'),
        ('구형 timeval의 제한', '__kernel_old_timeval은 __kernel_long_t tv_sec와 tv_usec입니다. 주석은 전통적으로 timeval로 기간을 전달하던 구조체에 내장하기 위한 구형 형태이며 새 사용자를 추가하지 말라고 합니다. 초와 마이크로초를 담으며 이름의 old만으로 항상 32비트라고 단정하지 않습니다.'),
        ('매크로를 이용한 대체 지점', '__kernel_old_timeval 구조체 정의는 같은 이름의 매크로가 없을 때만 포함됩니다. 전처리기 ifndef는 기존 struct 태그를 검색하는 기능이 아닙니다. 다른 문맥에서 제공한 매크로 기반 대체를 허용하는 구조이며 일반 C 태그와 매크로 이름 공간을 구분해야 합니다.'),
        ('구형 timespec과 interval timer', '__kernel_old_timespec은 __kernel_old_time_t tv_sec와 long tv_nsec를 가집니다. __kernel_old_itimerval은 __kernel_old_timeval 두 개를 it_interval과 it_value로 가집니다. itimerspec과 itimerval은 필드 이름이 비슷하지만 하위 구조의 단위가 나노초와 마이크로초로 다릅니다.'),
        ('소켓 timeval', '__kernel_sock_timeval은 __s64 tv_sec와 __s64 tv_usec입니다. 고정 signed 64비트 필드를 쓰지만 소수 필드 단위는 여전히 마이크로초입니다. 새 timespec과 비슷한 폭이라고 단위를 나노초로 바꾸어 해석하면 안 됩니다.'),
        ('구조체와 정책의 차이', '이 파일은 소수 필드의 음수나 범위 초과를 막지 않고 패딩 초기화나 사용자 복사도 실행하지 않습니다. 실제 syscall 또는 드라이버가 필요한 유효성·변환 정책을 적용합니다. 구조체 선언 검토를 모든 아키텍처 ABI 크기와 정렬의 실측으로 과장하지 않습니다.')
    ],
    questions=[
        ('__kernel_timespec의 tv_nsec 자료형은?', 'long long이다', '언제나 커널 내부와 같은 long이다', '내부 timespec64와 공개 ABI 구조체는 별개입니다. 특히 32비트 long 환경에서는 필드 폭 차이가 중요합니다.'),
        ('__kernel_sock_timeval의 tv_usec 단위는?', '마이크로초이다', '필드가 64비트이므로 나노초이다', '자료형의 폭과 단위는 독립적입니다. 소켓 구조체는 두 __s64 필드를 쓰지만 소수 단위는 usec입니다.'),
        ('#ifndef __kernel_old_timeval은 무엇을 검사하는가?', '같은 이름의 전처리 매크로 정의 여부이다', 'C 컴파일러에 해당 구조체 태그가 등록되었는지이다', '전처리기는 C 타입 정보를 검색하지 않습니다. 조건부 대체 지점을 이해할 때 두 이름 공간을 구분해야 합니다.')
    ]
), dict(
    path='include/uapi/linux/time.h', title='공개 시간 헤더: 구형 구조체, timer 종류, clock ID',
    intro='조건부 구조체 정의와 모든 clock·timer 상수를 원본 값에 따라 읽습니다.',
    principle='ABI 식별자는 구현이 사라져도 함부로 재사용할 수 없으며 숫자 ID와 비트 집합을 구분해야 합니다.',
    use='시간 헤더에서 선언한 형식과 실제 지원되는 clock 기능을 혼동하지 않습니다.',
    area='UAPI · 조건부 컴파일 · 식별자 안정성 · 호환성 · 단위',
    sections=[
        ('전체 구성', 'GPL-2.0 WITH Linux-syscall-note, guard, types/time_types include 뒤 사용자 공간용 구형 구조체 네 개, timezone, interval timer ID, clock ID와 관련 상수, TIMER_ABSTIME이 있습니다. 실제 clock 조회나 timer 생성 함수 구현은 없습니다.'),
        ('사용자 공간 조건부 정의', '__KERNEL__이 정의되지 않았을 때 timespec, timeval, itimerspec, itimerval을 정의합니다. timespec만 추가로 _STRUCT_TIMESPEC guard를 확인하고 정의 후 그 매크로를 설정합니다. 커널 빌드에서 같은 구형 태그를 그대로 노출하는 구조가 아닙니다. 이 UAPI 헤더를 사용자 libc time.h와 아무 고려 없이 함께 include해도 된다는 보장은 아닙니다.'),
        ('구형 구조체 전체 필드', 'timespec은 __kernel_old_time_t tv_sec와 long tv_nsec, timeval은 __kernel_old_time_t tv_sec와 __kernel_suseconds_t tv_usec입니다. itimerspec은 timespec의 it_interval과 it_value, itimerval은 timeval의 같은 두 필드를 가집니다. period/interval과 expiration/current value라는 주석을 가지며 나노초와 마이크로초 단위를 구분합니다.'),
        ('Timezone 구조체', 'timezone은 int tz_minuteswest와 tz_dsttime을 가집니다. 전자는 Greenwich 서쪽 방향의 분, 후자는 DST 보정 종류라고 주석에 설명됩니다. 지역 이름이나 역사적인 시간대 전환 규칙을 저장하는 구조가 아닙니다. 이 정의는 __KERNEL__ 조건문 밖에 있습니다.'),
        ('Interval timer ID', 'ITIMER_REAL=0, ITIMER_VIRTUAL=1, ITIMER_PROF=2입니다. 이 파일은 식별자만 정의합니다. 구체적 시간 계수 방식, 신호 종류, syscall 동작은 구현과 해당 인터페이스 자료를 별도로 확인해야 합니다. clock ID와 같은 숫자가 있어도 같은 식별자 공간이라고 대입하지 않습니다.'),
        ('Clock ID 0부터 6', 'CLOCK_REALTIME=0, CLOCK_MONOTONIC=1, CLOCK_PROCESS_CPUTIME_ID=2, CLOCK_THREAD_CPUTIME_ID=3, CLOCK_MONOTONIC_RAW=4, CLOCK_REALTIME_COARSE=5, CLOCK_MONOTONIC_COARSE=6입니다. 이름은 서로 다른 시계 종류를 구별하는 ID이며 이 헤더 자체가 각 시계의 분해능이나 하드웨어 제공 여부를 보증하지 않습니다.'),
        ('Clock ID 7부터 11과 예약', 'CLOCK_BOOTTIME=7, CLOCK_REALTIME_ALARM=8, CLOCK_BOOTTIME_ALARM=9, CLOCK_SGI_CYCLE=10, CLOCK_TAI=11입니다. 특히 SGI_CYCLE은 드라이버가 제거되었지만 ID를 placeholder로 남기며 재사용하지 말라는 주석이 있습니다. 정의가 남았다는 이유로 해당 clock이 동작한다고 가정하면 안 됩니다.'),
        ('상한과 마스크 이름', 'MAX_CLOCKS=16이며 여기서 정의한 clock ID가 연속 16개 존재한다는 뜻은 아닙니다. CLOCKS_MASK는 CLOCK_REALTIME|CLOCK_MONOTONIC이므로 실제 값은 1이고 CLOCKS_MONO도 CLOCK_MONOTONIC입니다. CLOCKS_MASK를 모든 clock ID에 대해 1<<ID를 합친 지원 비트맵이라고 읽으면 원본 식과 다릅니다.'),
        ('절대 시각 플래그', 'TIMER_ABSTIME=0x01을 POSIX interval timer 설정 관련 플래그로 정의합니다. 실제 호출이 플래그를 어떻게 처리하고 어느 clock에서 허용하는지는 해당 구현 책임입니다. 헤더 상수 하나가 모든 timeout 인자를 절대 시각으로 바꾸는 것은 아닙니다.'),
        ('CS와 검증 경계', '조건부 공개 범위, long 기반 구형 ABI, ID 재사용 금지, 매크로 이름과 실제 식의 차이가 핵심입니다. 전체 상수와 선언을 학습하지만 연결된 syscall 전체 구현을 이 파일 완료에 포함하지 않습니다.')
    ],
    questions=[
        ('CLOCK_SGI_CYCLE 상수가 남아 있으면 드라이버도 반드시 존재하는가?', '아니다. 제거된 드라이버의 ID를 재사용하지 않도록 남긴 것이다', '그렇다. 상수 정의가 있으면 모든 커널에서 호출이 성공한다', '본문 주석은 드라이버 제거와 placeholder 유지 이유를 명시합니다. 공개 ABI 번호의 수명은 구현 기능의 수명과 다를 수 있습니다.'),
        ('CLOCKS_MASK의 이 파일 내 실제 값은?', '1이다', '모든 clock ID 비트를 켠 65535이다', '식은 0|1입니다. 이름만 보고 지원 시계 전체의 비트 집합이라고 추정하지 않습니다.'),
        ('구형 timespec 정의를 둘러싼 추가 guard는?', '_STRUCT_TIMESPEC이다', '모든 구조체마다 자동으로 생성되는 C 태그 검사이다', '__KERNEL__ 조건 밖의 전처리 처리와 별도로 timespec에는 명시적인 매크로 guard가 있습니다. C 타입 검사를 대신하는 일반 기능은 아닙니다.'),
        ('MAX_CLOCKS=16이면 이 헤더에 clock ID 16개가 정의되어 있는가?', '아니다. 상한과 실제 나열된 ID 수는 다르다', '그렇다. 0부터 15까지 모두 이름이 정의되어 있다', '이 파일은 0부터 11까지의 이름을 나열하며 그중 10은 placeholder입니다. 상한 숫자로 기능 목록을 추측하지 않습니다.')
    ]
)]
