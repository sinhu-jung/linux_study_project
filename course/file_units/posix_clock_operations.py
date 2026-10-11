"""Whole-file private POSIX clock operation table."""
ROWS = [dict(
    path='kernel/time/posix-timers.h',
    title='POSIX clock 연산표: namespace와 timer 재시도 계약',
    intro='k_clock의 모든 callback과 외부 연산표·공통 helper 선언을 읽습니다.',
    principle='서로 다른 clock 구현을 같은 인터페이스로 호출하되 시각 좌표계와 실행 중 timer의 수명은 별도로 처리해야 합니다.',
    use='함수 포인터를 통한 clock별 동작 선택, 현재 namespace 시각과 host 시각의 차이, 재시도 중 재조회 필요성을 이해합니다.',
    area='함수 포인터 · 다형성 · namespace · 수명 관리 · 재시도 · 동기화',
    sections=[
        ('파일 전체와 포함 전제', 'GPL-2.0 표시 뒤 TIMER_RETRY 상수, k_clock 구조체, 다섯 const 연산표 extern과 다섯 공통 함수 선언이 있습니다. 이 파일에는 include guard나 자체 include가 없습니다. clockid_t, timespec64, ktime_t 및 관련 타입을 준비한 내부 문맥에서 포함해야 하며 반복 include를 자동 방지한다고 가정하지 않습니다.'),
        ('재시도 상수', 'TIMER_RETRY는 1입니다. 일반적인 음수 errno와 다른 내부 제어 결과입니다. 관련 posix-timers.c 일부에서 실행 중 timer를 try_to_cancel하지 못하면 set/delete가 이를 반환하고 호출 측은 대기·재조회를 거쳐 재시도합니다. 사용자에게 그대로 성공값 1을 돌려주기 위한 정의라고 해석하면 안 됩니다.'),
        ('해상도·설정·조정 callback', 'clock_getres는 clockid와 timespec64 출력 포인터를 받고 int를 반환합니다. clock_set은 const timespec64 입력, clock_adj는 __kernel_timex 입출력 포인터를 받으며 둘 다 int입니다. 이 연산표는 인터페이스를 정의하지만 모든 clock이 모든 callback을 채우거나 같은 권한·오류 정책을 쓰도록 강제하지 않습니다.'),
        ('두 시각 읽기의 좌표계', 'clock_get_timespec은 int 결과와 timespec64 출력으로 현재 time namespace의 시각을 제공합니다. clock_get_ktime은 ktime_t를 직접 반환하며 주석상 root time namespace의 시각입니다. 반환 형식만 다른 동일한 좌표계 함수라고 바꿔 쓰면 namespace offset이 중복되거나 빠질 수 있습니다.'),
        ('생성과 수면', 'timer_create는 k_itimer 포인터를 받고 int를 반환합니다. nsleep은 clockid, flags, const timespec64 요청 포인터를 받고 int를 반환합니다. 이 시그니처에는 사용자 공간 출력 포인터나 timer ID 인자가 직접 들어 있지 않습니다. syscall 사용자 복사와 clock별 내부 연산의 층을 구분합니다.'),
        ('설정·삭제·조회', 'timer_set은 timer, flags, new_setting과 old_setting 두 itimerspec64 포인터를 받고 int를 반환합니다. timer_del도 int지만 timer_get은 현재 설정을 채우는 void callback입니다. new_setting도 이 시그니처에서는 const가 아니며 이름만 보고 타입 한정자를 추가해 읽지 않습니다. 반환값과 포인터를 통한 출력은 다른 경로입니다.'),
        ('주기 진행과 남은 시간', 'timer_rearm은 timer만 받는 void, timer_forward는 timer와 ktime_t now를 받고 s64, timer_remaining은 같은 인자 형태로 ktime_t를 반환합니다. 재무장, 주기 진행의 결과, 남은 시간 조회를 하나의 callback으로 합치지 않고 나눕니다. 정확한 반환 수치 정책은 각 구현을 더 읽어야 합니다.'),
        ('취소·예약·실행 완료 대기', 'timer_try_to_cancel은 int, timer_arm은 expires와 bool absolute/sigev_none을 받는 void, timer_wait_running은 timer만 받는 void입니다. 취소 시도와 실행 중 callback의 완료 대기는 다른 연산이며, arm은 절대 여부와 알림 없음 여부를 별도 bool로 전달합니다. 모든 callback에서 잠금을 내부적으로 알아서 획득한다는 보장은 이 헤더에 없습니다.'),
        ('재시도와 수명에 대한 구현 대조', '관련 구현의 timer_wait_running helper는 kclock과 timer ID를 먼저 읽고 RCU 보호 뒤 timer lock을 풉니다. callback이 RCU lock을 놓을 수도 있으므로 반환 뒤 원래 timer 포인터를 다시 만지지 말라는 주석이 있으며 ID로 다시 lock_timer합니다. 따라서 재시도 시 timer가 삭제되어 조회되지 않을 가능성을 처리해야 합니다. 구현 일부 대조를 posix-timers.c 전체 학습 완료로 세지 않습니다.'),
        ('외부 clock 연산표 다섯 개', 'clock_posix_cpu, clock_posix_dynamic, clock_process, clock_thread, alarm_clock를 extern const struct k_clock로 선언합니다. 여기에서 실제 callback 주소를 채우거나 clock ID 배열을 생성하지 않습니다. const는 이 인터페이스에서 연산표를 수정하지 않음을 나타내지만 callback이 다루는 timer 상태까지 불변이라는 뜻은 아닙니다.'),
        ('공통 helper 다섯 개', 'posix_timer_queue_signal은 timer를 받아 int입니다. common_timer_get은 timer와 현재 설정 출력의 void, common_timer_set은 timer·flags·새 설정·이전 설정을 받아 int입니다. posix_timer_set_common은 timer와 새 설정의 void이고 common_timer_del은 timer를 받아 int입니다. common_timer_set과 posix_timer_set_common은 이름이 비슷하지만 인자와 반환형이 달라 같은 함수의 별칭이 아닙니다.'),
        ('CS와 검증 범위', '전체 callback과 선언을 설명했습니다. 함수 포인터 연산표를 통한 구현 교체, 좌표계가 다른 시간 조회, 대기 중 객체 삭제와 재조회, 내부 제어 코드와 errno의 차이가 핵심입니다. 전체 POSIX timer 구현이나 실제 namespace·signal·취소 경쟁을 실행 검증한 결과는 아닙니다.')
    ],
    questions=[
        ('clock_get_timespec과 clock_get_ktime은 표현 형식만 다른가?', '아니다. 주석상 현재 namespace와 root namespace라는 차이도 있다', '그렇다. 모든 경우 동일한 기준 시각이다', '헤더가 각각의 좌표계를 명시합니다. 타입 변환만으로 대체하면 namespace offset 처리를 잘못할 수 있습니다.'),
        ('TIMER_RETRY의 값과 용도는?', '1이며 내부 재시도 제어 결과이다', '-EINVAL과 같은 오류 코드이다', '매크로 값은 양수 1입니다. 관련 set/delete 호출 측에서 이를 보고 실행 중 callback을 기다린 뒤 재시도합니다.'),
        ('실행 중 timer를 기다린 뒤 원래 포인터를 무조건 계속 써도 되는가?', '아니다. 관련 구현은 timer ID로 다시 조회하고 잠근다', '그렇다. 기다림은 객체 수명을 항상 영구 보장한다', '대기 과정에 lock과 RCU 보호가 달라질 수 있습니다. timer 삭제 가능성과 재조회 실패를 고려해야 합니다.'),
        ('timer_get callback의 반환형은?', 'void이며 cur_setting 포인터로 값을 채운다', 'ktime_t이며 남은 시간만 직접 반환한다', 'timer_remaining과 다른 인터페이스입니다. 구조체 전체 조회와 단일 남은 시간 값 반환을 구분합니다.'),
        ('이 헤더는 include guard로 반복 포함을 막는가?', '아니다. 원본에는 guard가 없다', '그렇다. 모든 커널 헤더에는 자동으로 guard가 생긴다', '실제 파일은 SPDX 뒤 바로 매크로와 구조체가 시작합니다. 일반적인 관례와 현재 소스의 사실을 구분합니다.')
    ]
)]
