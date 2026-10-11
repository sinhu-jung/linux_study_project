"""Whole-file minimal clock syscalls when POSIX timers are disabled."""
ROWS = [dict(
    path='kernel/time/posix-stubs.c',
    title='POSIX timer 비활성 경로: 최소 clock syscall과 sleep',
    intro='네 clock 시스템 호출과 네 구형 시간 변형의 지원 범위·namespace·재시작 상태를 분석합니다.',
    principle='기능을 비활성화해도 호환성을 위해 일부 인터페이스는 실제 동작하는 작은 구현으로 유지할 수 있습니다.',
    use='stub이라는 이름만으로 모든 clock 호출이 실패한다고 판단하지 않고 실제 지원 범위를 확인합니다.',
    area='시스템 호출 · 기능 축소 · ABI 호환 · 시간 namespace · 절대·상대 시간 · 재시작',
    sections=[
        ('전체 파일과 선택 조건', 'GPL-2.0과 작성 이력, syscall·timekeeping·namespace·compat 관련 include 뒤 일반 clock_settime/gettime/getres/nanosleep, CONFIG_COMPAT_32BIT_TIME 아래 구형 네 호출이 있습니다. 공통 내부 helper는 do_clock_gettime 하나입니다. Makefile에서 CONFIG_POSIX_TIMERS가 y가 아닐 때 이 파일을 선택합니다. 본문은 전부 ENOSYS를 돌려주는 빈 함수 모음이 아닙니다.'),
        ('보존하는 clock 종류', '주석은 CLOCK_REALTIME과 CLOCK_MONOTONIC의 최소 호환성, systemd 등의 사용을 위한 CLOCK_BOOTTIME을 설명합니다. gettime/getres/nanosleep은 이 세 ID만 받습니다. CPU time, RAW, COARSE, TAI와 alarm clock ID 등 다른 값은 이 구현의 switch에서 EINVAL입니다. 헤더에 상수가 있다는 것과 이 축소 구현이 지원한다는 것은 다릅니다.'),
        ('Clock settime', 'clock_settime은 CLOCK_REALTIME만 허용하며 다른 ID는 사용자 포인터를 읽기 전에 EINVAL입니다. get_timespec64 실패는 EFAULT이고 성공하면 do_sys_settimeofday64(&new_tp,NULL)의 결과를 그대로 반환합니다. 권한과 시각 유효성 등 공통 설정 정책은 위임된 helper에서 처리합니다. monotonic을 직접 설정하거나 timezone 객체를 전달하는 경로는 없습니다.'),
        ('내부 gettime와 namespace', 'do_clock_gettime은 REALTIME에 ktime_get_real_ts64, MONOTONIC에 ktime_get_ts64 후 timens_add_monotonic, BOOTTIME에 ktime_get_boottime_ts64 후 timens_add_boottime을 사용합니다. 이 파일에서 realtime에는 namespace offset을 추가하지 않습니다. 성공은 0, 나머지 ID는 EINVAL입니다.'),
        ('사용자 gettime 출력', 'clock_gettime은 지역 timespec64에 내부 helper 결과를 받은 뒤 put_timespec64로 사용자에게 전달합니다. 지원하지 않는 clock이면 복사 단계 전에 반환하고 복사 실패는 EFAULT입니다. 사용자 버퍼를 내부 timekeeping 함수에 직접 넘기지 않고 커널 표현과 공개 ABI 표현 사이를 분리합니다.'),
        ('Clock getres의 실제 출력 처리', 'clock_getres는 {tv_sec=0,tv_nsec=hrtimer_resolution}을 준비하고 지원하는 세 ID에서 put_timespec64를 호출합니다. 이 경로에는 tp가 NULL인지 확인해 복사를 생략하는 조건이 없습니다. 따라서 지원 ID라도 NULL 출력 포인터가 이 구현에서 자동 성공한다고 가정하면 안 됩니다. 해상도는 고정 TICK_NSEC를 이 파일이 직접 대입하는 것이 아니라 hrtimer_resolution 값입니다.'),
        ('Sleep 입력 순서', 'clock_nanosleep은 먼저 ID를 검사하고, get_timespec64로 요청을 복사한 뒤 timespec64_valid로 비음수 초와 정상 나노초 범위를 확인합니다. 복사 실패는 EFAULT, 유효성 실패는 EINVAL입니다. strict 검사 호출은 없으며 이후 timespec64_to_ktime의 범위 처리에 따라 표현됩니다.'),
        ('Flags의 검사 범위', '이 함수는 flags&TIMER_ABSTIME만 봅니다. 다른 비트가 설정되었는지 검사해 별도 EINVAL을 반환하는 코드는 이 본문에 없습니다. ABSTIME 비트가 있으면 절대 모드, 없으면 상대 모드를 선택합니다. 실제 소스 설명과 일반적인 인터페이스 기대를 구분해야 합니다.'),
        ('절대 시각과 남은 시간', 'ABSTIME이면 rmtp를 NULL로 바꾸어 남은 시간 출력 포인터를 무시합니다. 상대 모드에서는 전달한 rmtp를 유지합니다. texp=timespec64_to_ktime(t) 뒤 절대 모드일 때만 timens_ktime_to_host(which_clock,texp)로 namespace 기준 시각을 host 기준으로 바꿉니다. 상대적인 길이에 namespace offset을 무조건 더하거나 빼는 것은 아닙니다.'),
        ('재시작 상태와 hrtimer 위임', 'current->restart_block.fn을 do_no_restart_syscall로 설정하고 nanosleep.type을 rmtp 유무에 따라 TT_NATIVE 또는 TT_NONE으로 둔 뒤 rmtp 필드를 저장합니다. hrtimer_nanosleep에 texp, ABS/REL 모드와 clock ID를 넘겨 결과를 반환합니다. 이 파일 안에 실제 수면 루프나 signal 재시작 알고리즘이 없으므로 초기 restart fn만 보고 하위 함수의 모든 재시작 동작이 금지된다고 결론 내리지 않습니다.'),
        ('32비트 시간 set/get/getres', 'CONFIG_COMPAT_32BIT_TIME 아래 clock_settime32는 같은 REALTIME 제한 뒤 get_old_timespec32로 복사하여 공통 설정 helper에 위임합니다. clock_gettime32는 같은 do_clock_gettime을 사용하므로 monotonic/boottime namespace 보정도 공유합니다. clock_getres_time32는 같은 해상도 구조체를 put_old_timespec32로 출력하며 역시 NULL 검사 생략 조건이 없습니다.'),
        ('32비트 시간 sleep', 'clock_nanosleep_time32는 ID·복사·유효성·ABSTIME 분기와 host 시각 변환이 일반 경로와 같습니다. 차이는 구형 시간 복사 helper와 restart_block의 TT_COMPAT, compat_rmtp 필드 사용입니다. rmtp가 없거나 절대 모드이면 TT_NONE입니다. old_timespec32 포인터를 native rmtp 필드에 그대로 저장하는 구현이 아닙니다.'),
        ('CS와 검증 범위', '모든 함수와 설정 분기를 소스로 대조했습니다. 축소 기능의 호환성, 사용자 복사 경계, 시간 좌표계와 상대 기간의 차이, ABI별 restart 데이터, 코드에 있는 검사와 없는 검사를 구분하는 법을 학습합니다. 실제 syscall이나 namespace 수면 실험을 실행한 결과는 아닙니다.')
    ],
    questions=[
        ('CONFIG_POSIX_TIMERS=n이면 이 파일의 모든 clock 호출이 ENOSYS인가?', '아니다. 세 clock의 읽기·해상도·sleep 등 최소 기능을 구현한다', '그렇다. stub이라는 이름이면 모든 함수가 비어 있다', '파일 본문에는 timekeeping과 hrtimer에 연결하는 실제 구현이 있습니다. 지원하지 않는 ID에는 EINVAL을 반환합니다.'),
        ('clock_settime이 허용하는 clock ID는?', 'CLOCK_REALTIME만이다', 'MONOTONIC과 BOOTTIME도 직접 설정할 수 있다', 'ID 검사가 첫 단계이며 REALTIME이 아니면 사용자 입력을 읽기 전에 EINVAL입니다.'),
        ('MONOTONIC gettime과 절대 sleep의 namespace 변환 방향은?', '조회는 namespace offset을 반영하고 절대 sleep은 host 기준으로 변환한다', '두 경로 모두 무조건 같은 offset을 더한다', '조회는 timens_add_monotonic, 절대 요청은 timens_ktime_to_host입니다. 상대적인 기간에는 후자 변환을 적용하지 않습니다.'),
        ('ABSTIME 요청에서 rmtp가 주어지면 어떻게 처리하는가?', 'NULL로 바꾸어 남은 시간 출력용으로 사용하지 않는다', '반드시 TT_NATIVE로 등록해 출력한다', '절대 모드 분기가 포인터를 먼저 NULL로 만든 뒤 restart type을 정합니다. 따라서 TT_NONE이 됩니다.'),
        ('이 getres 구현은 tp=NULL이면 복사를 건너뛰는가?', '아니다. 지원 clock에서도 복사 helper를 호출한다', '그렇다. 모든 clock_getres는 항상 같은 NULL 특별 처리를 한다', '이 파일에는 if(tp) 조건이 없습니다. 다른 구현의 동작을 축소 경로에 그대로 가정하지 않습니다.'),
        ('구형 nanosleep의 restart 상태에서 출력 포인터 필드는?', 'compat_rmtp이며 포인터가 있으면 TT_COMPAT이다', 'native rmtp이며 항상 TT_NATIVE이다', '타입과 포인터 필드가 ABI에 맞게 달라집니다. 두 구현의 비슷한 구조 속 차이를 확인해야 합니다.')
    ]
)]
