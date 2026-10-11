"""Complete watchdog fault-injection test source lesson."""
ROWS = [dict(
    path='kernel/time/clocksource-wdtest.c',
    title='Clocksource watchdog 테스트: 읽기 지연과 시각 흔들림 주입',
    intro='두 모의 clocksource, 오류 주입 callback, 재등록과 테스트 스레드 수명을 전체 소스로 분석합니다.',
    principle='감시기의 내성을 검증하려면 측정 지연과 잘못된 시계 값이라는 서로 다른 실패 원인을 의도적으로 만들어야 합니다.',
    use='watchdog의 재시도 한계와 불안정 판정 테스트를 읽고 로그·경고·반환값의 차이를 이해합니다.',
    area='오류 주입 · watchdog · clocksource · 재시도 · kthread · 동시 접근 · 테스트 수명',
    sections=[
        ('전체 파일 지도', 'GPL-2.0+와 저작권 주석, 모듈 이름을 붙이는 pr_fmt, include와 모듈 메타데이터로 시작합니다. holdoff 매개변수, task 포인터, jiffies 모의 시계, ktime 모의 시계와 오류 주입 상태, 재설정 helper, 테스트 스레드, 매개변수 출력·init·빈 cleanup이 전체입니다. KUnit suite가 아니라 별도 kernel thread를 시작하는 테스트 모듈입니다.'),
        ('시작 지연 매개변수', 'holdoff는 CONFIG_TEST_CLOCKSOURCE_WATCHDOG가 built-in이면 10, 아니면 0으로 초기화됩니다. int module_param의 노출 mode는 0444이며 설명상 단위는 초입니다. 테스트 스레드는 holdoff*HZ를 schedule_timeout_uninterruptible에 넘깁니다. 이 파일에는 음수나 비정상적으로 큰 매개변수에 대한 별도 범위 검사가 없습니다.'),
        ('Jiffies 모의 시계 전체 설정', 'wdtest_jiffies_read는 jiffies를 u64로 반환합니다. clocksource의 이름은 wdtest-jiffies, rating=1, uncertainty_margin=TICK_NSEC, mask=32비트, flags=CLOCK_SOURCE_MUST_VERIFY입니다. mult=TICK_NSEC<<JIFFIES_SHIFT, shift=JIFFIES_SHIFT, max_cycles=10입니다. 기본 jiffies 시계와 닮았지만 명시한 uncertainty margin과 검증 플래그를 이 테스트 목적에 맞춰 사용합니다.'),
        ('Ktime 모의 시계 전체 설정', '이름은 wdtest-ktime, rating=300, read=wdtest_ktime_read, mask=64비트입니다. KTIME_FLAGS는 IS_CONTINUOUS, VALID_FOR_HRES, MUST_VERIFY, VERIFY_PERCPU의 OR입니다. mark_unstable callback과 자기 list head 초기화도 지정합니다. mult와 shift를 이 initializer에서 직접 설정하지 않고 이후 1000000kHz로 등록할 때 계산하도록 합니다.'),
        ('읽기 지연 주입', 'wdtest_ktime_read는 READ_ONCE로 남은 지연 횟수를 읽습니다. 0이 아니면 udelay(cs->uncertainty_margin/250)를 호출하고 남은 횟수에서 1을 뺀 값을 WRITE_ONCE로 저장합니다. margin의 단위는 ns이고 udelay의 인자는 us이므로 숫자 변환까지 고려하면 나눗셈 절단을 제외하고 margin의 약 네 배 길이 지연을 주입합니다. 250으로 나눈 ns만큼 지연한다고 읽으면 단위가 틀립니다.'),
        ('읽기 값 흔들림 주입', '그 다음 ktime_get_real_fast_ns를 읽습니다. fuzz가 켜졌으면 static sign을 반전하고 sign*100*NSEC_PER_MSEC를 더합니다. sign의 초기값이 1이므로 첫 fuzz 읽기는 -100ms, 다음은 +100ms 방향입니다. 이것은 의도적인 두 값의 교대 오프셋이며 포함된 prandom 헤더가 있다고 난수 분포를 사용하는 것은 아닙니다.'),
        ('공유 값 접근의 의미', 'ndelays와 fuzz에는 READ_ONCE/WRITE_ONCE를 사용하지만 ndelays의 읽고-감소하고-쓰기 전체가 atomic decrement로 바뀌는 것은 아닙니다. static sign에도 별도 lock이나 atomic 연산이 없습니다. 이 파일의 테스트용 상태를 임의의 동시 callback에서도 정확한 전역 횟수를 보장하는 범용 오류 주입기로 설명하지 않습니다.'),
        ('Unstable callback과 reset', 'wdtest_ktime_cs_mark_unstable은 이름을 포함한 안내 로그만 출력합니다. reset helper는 flags에 UNSTABLE이 있을 때 unregister, flags=KTIME_FLAGS, HZ/10만큼 sleep, 1000000kHz 재등록을 수행합니다. 이미 안정적이면 아무 일도 하지 않습니다. 객체 전체를 memset하거나 sign과 fuzz 상태를 다시 초기화하는 함수는 아닙니다.'),
        ('첫 시험: 명시한 margin 유지', '스레드는 초기 holdoff 뒤 jiffies 모의 시계를 등록하고 uncertainty_margin이 TICK_NSEC와 같은지 WARN_ON_ONCE로 검사합니다. 읽기 두 번 사이 HZ만큼 쉬고 값이 같으면 경고합니다. 끝에서 unregister합니다. 정확히 HZ만큼 카운터가 증가했는지를 검사하는 것이 아니라 단지 두 값이 다른지를 확인합니다.'),
        ('둘째 시험: 자동 margin과 짧은 진행', 'ktime 모의 시계를 1000000kHz로 등록하고 margin이 NSEC_PER_USEC보다 작으면 경고합니다. read, udelay(1), read 뒤 두 값을 로그로 출력하고 time_before(j2,j1+NSEC_PER_USEC)이면 경고합니다. j1/j2는 unsigned long이라 32비트 환경에서는 u64 읽기 결과의 전체 폭을 그대로 보관하지 않습니다. 시간 비교는 해당 long 폭의 time_before 의미를 따릅니다.'),
        ('재시도 한계 순회', 'max_retries는 clocksource_get_max_watchdog_retry에서 얻고 i=0부터 max_retries+1까지 양 끝 포함해 순회합니다. 로그의 설명은 i<=1이면서 i<max_retries이면 추가 문구 없음, 그 외 i<=max_retries이면 expect message, 초과면 expect clock skew입니다. 로그 문구 선택과 실제 상태 assertion은 별도입니다.'),
        ('지연 시험의 판정', '각 i를 ndelays에 저장하고 2*HZ만큼 쉽니다. 남은 ndelays가 0이 아니면 경고하고, i<=max_retries와 UNSTABLE이 아님이 일치하는지 검사합니다. 즉 허용 재시도 이내면 안정, 한 번 초과하면 불안정을 기대합니다. 그 뒤 reset helper를 호출해 필요하면 다음 시험용 시계를 다시 등록합니다.'),
        ('값 흔들림과 CPU별 검사', '지연 주입 순회가 끝나면 fuzz=true로 하고 2*HZ만큼 기다립니다. UNSTABLE이 아니면 경고하고 clocksource_verify_percpu를 호출한 뒤 fuzz=false로 끕니다. 로그는 clock skew와 CPU별 mismatch를 기대한다고 말하지만 이 파일이 그 메시지 문자열을 자동 파싱해 일치 여부를 판단하지는 않습니다. 마지막에 ktime 모의 시계를 unregister하고 Done 로그와 0을 반환합니다.'),
        ('오류를 보고하는 방식', '등록 함수들의 반환값을 테스트 본문과 reset에서 확인하지 않습니다. 실패 판정은 여러 WARN_ON_ONCE와 로그이며 경고가 생겼다고 스레드가 즉시 음수 오류를 반환하는 구조도 아닙니다. 정상 경로 끝의 0만 보고 모든 시험이 통과했다고 해석할 수 없습니다. 모듈 init의 성공과 비동기 테스트 완료도 다른 시점입니다.'),
        ('스레드 생성과 초기화 실패', 'init은 holdoff를 pr_alert로 출력하고 kthread_run(wdtest_func,NULL,"wdtest")을 호출합니다. ERR_PTR이면 PTR_ERR를 반환하고 경고를 출력하며 wdtest_task=NULL로 둡니다. 성공하면 task 포인터를 디버깅용으로 남기고 바로 0을 반환합니다. 테스트가 끝날 때까지 init에서 기다리는 동작은 없습니다.'),
        ('Cleanup의 실제 범위', 'module_exit에 연결한 clocksource_wdtest_cleanup 본문은 비어 있습니다. 이 파일에는 kthread_stop, 완료 대기, kthread_should_stop 검사도 없습니다. 테스트 스레드의 정상 종료가 두 모의 시계를 정리하지만 임의 시점의 종료 요청에 대해 cleanup이 스레드를 중단·join한다고 가정하면 안 됩니다. 수명 관리 코드를 읽을 때 함수 이름보다 본문이 중요합니다.'),
        ('CS와 검증 범위', '모의 장치, 지연과 값 손상이라는 서로 다른 실패 모델, 재시도 경계의 +1 시험, 단위 변환, 비동기 테스트의 결과 수집과 수명 관리를 학습합니다. 소스 전체를 대조한 학습 자료이며 실제 모듈 로드, clocksource 전환 또는 watchdog 경고 발생을 실행 검증한 것은 아닙니다.')
    ],
    questions=[
        ('ndelays 지연과 fuzz 오류 주입의 차이는?', '전자는 callback을 늦추고 후자는 반환 시각을 교대로 바꾼다', '둘 다 동일한 난수 지연만 주입한다', 'udelay는 읽기 경로의 시간 비용을, +/-100ms는 읽은 값의 일관성을 교란합니다. 서로 다른 실패 모델을 검사합니다.'),
        ('uncertainty_margin=1000ns라면 주입 udelay 인자는?', '4us이다', '4ns이다', '1000/250=4를 udelay에 전달합니다. 그 함수의 단위가 마이크로초이므로 4000ns의 지연 요청입니다.'),
        ('재시도 시험은 max_retries까지만 실행하는가?', '아니다. max_retries+1까지 포함한다', '그렇다. 허용 범위를 넘는 사례는 검사하지 않는다', '허용 경계의 마지막 값과 바로 초과하는 값을 함께 검사해 안정/불안정 판정이 바뀌는지 확인합니다.'),
        ('모듈 init이 0이면 테스트 전체가 이미 완료·통과했는가?', '아니다. 스레드 생성 성공 뒤 비동기로 진행된다', '그렇다. kthread_run이 모든 시험 결과를 반환한다', 'init은 생성 성공 후 바로 반환합니다. 본문의 실패는 WARN_ON_ONCE로 보고되므로 반환값만으로 합격을 판단할 수 없습니다.'),
        ('빈 cleanup이 자동으로 테스트 스레드를 join하는가?', '아니다. 본문에 stop이나 대기 처리가 없다', '그렇다. module_exit 등록만으로 임의의 kthread가 자동 종료된다', '스레드 수명 관리는 명시적인 코드를 확인해야 합니다. 이 파일의 정상 스레드 끝 정리와 외부 종료 cleanup은 별개입니다.'),
        ('READ_ONCE와 WRITE_ONCE로 ndelays를 읽고 쓰면 감소 전체가 atomic인가?', '아니다. 읽기와 쓰기 사이 전체를 원자화하지 않는다', '그렇다. 모든 경쟁 읽기에서 정확히 한 번씩 감소한다', '개별 접근을 명시하는 것과 atomic read-modify-write는 다릅니다. 테스트 구현의 전제를 범용 동시성 보장으로 확대하지 않습니다.')
    ]
)]
