"""Whole-file Hyper-V clocksource timer interface and page read protocol."""
ROWS = [dict(
    path='include/clocksource/hyperv_timer.h',
    title='Hyper-V 시계 페이지: sequence 검증과 128비트 곱의 상위 절반',
    intro='타이머 인터페이스 선언, 공유 페이지 읽기 함수, 설정을 끈 경우의 모든 stub를 분석합니다.',
    principle='공유 변환 계수가 바뀌면 측정값을 다시 읽어야 하며, 버전 값의 의미는 각 프로토콜에 따라 다릅니다.',
    use='Hyper-V 시계 읽기의 성공·실패와 출력값 유효 범위를 설명하고 고정소수점 환산에서 중간 곱의 폭을 이해합니다.',
    area='가상화 · 공유 메모리 · READ_ONCE · 읽기 장벽 · 버전 재시도 · 고정소수점 · 조건부 인터페이스',
    sections=[
        ('파일 전체와 상수', 'GPL-2.0 표기와 include guard 아래 linux/clocksource.h, linux/math64.h, asm/hyperv-tlfs.h를 포함합니다. HV_MAX_MAX_DELTA_TICKS는 0xffffffff, HV_MIN_DELTA_TICKS는 1입니다. 이름의 MAX_MAX도 원본 그대로입니다. 이 상수는 tick 범위이며 헤더 자체에서 나노초로 환산하거나 입력을 그 범위로 clamp하지 않습니다.'),
        ('설정을 켠 경우의 외부 인터페이스', 'CONFIG_HYPERV_TIMER에서 asm/hyperv_timer.h를 포함합니다. VMbus용 선언은 int hv_stimer_alloc(bool have_percpu_irqs), int hv_stimer_cleanup(unsigned int cpu), void legacy_init(cpu, sint), legacy_cleanup(cpu), global_cleanup(void), stimer0_isr(void)입니다. 이어 void hv_init_clocksource, hv_remap_tsc_clocksource와 unsigned long hv_get_tsc_pfn, ms_hyperv_tsc_page *hv_get_tsc_page를 선언합니다. 이 파일에 이 함수들의 구현이나 자원 수명 관리 본문은 없습니다.'),
        ('페이지 읽기 함수의 계약', 'hv_read_tsc_page_tsc는 const 페이지 포인터와 u64 출력 포인터 cur_tsc·time을 받고 bool을 반환하는 always_inline 함수입니다. const 포인터는 이 함수가 페이지를 수정하지 않는다는 뜻이며 hypervisor가 페이지를 갱신하지 않는다는 뜻이 아닙니다. 함수는 NULL 포인터를 검사하지 않습니다. 실패를 시간값 0이나 -1로 표시하는 대신 bool로 구분합니다.'),
        ('Sequence 0은 실패', '루프 처음에 READ_ONCE로 tsc_sequence를 u32 sequence에 읽습니다. 0이면 즉시 false를 반환합니다. 주석은 옛 TLFS 문서에서 특별 값을 -1로 잘못 적었지만 여기의 올바른 값은 0이라고 설명합니다. 이 코드는 sequence의 홀수·짝수를 검사하지 않습니다. pvclock의 홀수 쓰기 중 프로토콜을 그대로 가져와 해석하면 안 됩니다.'),
        ('데이터 전후의 장벽', '0이 아닌 sequence를 읽은 뒤 smp_rmb를 수행하고 tsc_scale과 tsc_offset을 각각 READ_ONCE로 읽습니다. 이어 hv_get_raw_timer 결과를 *cur_tsc에 저장하고 다시 smp_rmb를 수행합니다. 두 장벽은 첫 sequence 읽기·공유 계수 읽기·마지막 sequence 읽기의 순서를 유지하는 데 쓰입니다. READ_ONCE만으로 여러 필드가 하나의 원자적 스냅샷이 되는 것은 아닙니다.'),
        ('다시 읽기와 재시도', '마지막 READ_ONCE(tsc_sequence)가 처음 sequence와 다르면 do 루프 전체를 반복합니다. 새 시도에서는 계수뿐 아니라 raw timer도 다시 읽습니다. 버전이 유지되면 loop를 빠져나와 계산합니다. 재시도 횟수 상한이나 잠금 획득은 이 함수에 없습니다. 비교 후 hypervisor가 새 갱신을 시작해도 이미 로컬로 읽은 계수를 사용하며, 계산 과정에서 페이지 필드를 다시 직접 참조하지 않습니다.'),
        ('시간 환산과 중간 곱', '*time = mul_u64_u64_shr(*cur_tsc, scale, 64) + offset입니다. 수학적으로 unsigned 64×64 곱의 상위 64비트에 offset을 더하는 환산입니다. 예를 들어 raw=100, scale=2^63, offset=7이면 floor(100*2^63/2^64)+7=57입니다. C의 단순 u64 곱으로 중간값을 잘라 버린 뒤 64비트 shift하는 식과 동등하게 취급하면 안 됩니다. offset은 함수 내부에서 u64로 보관하며 덧셈에 별도 포화 처리나 오류 검사는 없습니다.'),
        ('실패 시 출력의 유효성', 'time 출력은 성공 스냅샷을 얻은 뒤에만 기록됩니다. 첫 sequence가 0이면 두 출력 모두 이 함수에서 변경하지 않습니다. 그러나 한 차례 읽기 후 sequence 변경으로 재시도하다 0을 만나면 cur_tsc는 이전 시도 값으로 이미 변경되었을 수 있습니다. false를 받았는데 cur_tsc나 이전 time 값으로 정상 결과를 만들어서는 안 됩니다.'),
        ('설정을 끈 경우의 stub 전체', 'CONFIG_HYPERV_TIMER가 없으면 hv_get_tsc_pfn은 0, hv_get_tsc_page는 NULL, hv_read_tsc_page_tsc는 출력에 쓰지 않고 false를 반환합니다. hv_stimer_cleanup은 0이며 legacy_init·legacy_cleanup·global_cleanup·stimer0_isr는 빈 void 함수입니다. 반면 hv_stimer_alloc, hv_init_clocksource, hv_remap_tsc_clocksource의 stub는 없습니다. 설정을 끄면 모든 선언이 대칭적인 빈 함수로 제공된다고 가정하면 안 됩니다.'),
        ('CS 연결과 검증 범위', '모든 상수·외부 선언·읽기 함수·설정별 stub를 다뤘습니다. 버전은 락 없이 일관된 계수를 읽는 도구이고 bool은 실패와 숫자 0을 분리합니다. 큰 곱의 상위 절반을 쓰는 고정소수점 계산과 실패 시 부분 출력 변경도 핵심입니다. 원본 대조와 식의 분석이며 실제 Hyper-V guest 실행이나 문서 최신판의 규격 검증을 수행한 것은 아닙니다.')
    ],
    questions=[
        ('hv_read_tsc_page_tsc가 즉시 false를 반환하는 sequence 값은?', '0이다', '모든 홀수 값이다', '본문은 if (!sequence)를 검사합니다. 홀수·짝수 쓰기 표시를 사용하는 pvclock과 다른 프로토콜이므로 버전이라는 이름만으로 조건을 동일시하면 안 됩니다.'),
        ('raw=100, scale=2^63, offset=7일 때 반환 시간은?', '57이다', '107이다', '곱을 64비트 오른쪽으로 이동하는 것은 scale/2^64를 적용하는 것입니다. 이 계수는 1/2이므로 50에 offset 7을 더합니다.'),
        ('false를 반환했다면 cur_tsc는 항상 호출 전 값인가?', '아니다. 앞선 재시도에서 기록한 값이 남아 있을 수 있다', '그렇다. 실패하는 모든 경로가 출력을 원상복구한다', 'cur_tsc 쓰기는 최종 sequence 확인보다 앞에 있습니다. 이후 재시도에서 sequence=0을 만나면 false로 끝나지만 이미 쓴 값을 복구하지 않습니다.'),
        ('CONFIG_HYPERV_TIMER가 꺼졌을 때 hv_stimer_alloc의 빈 stub도 제공되는가?', '아니다. 이 헤더의 else에는 해당 stub가 없다', '그렇다. cleanup과 alloc 모두 항상 0을 반환한다', 'cleanup에는 int 반환 stub가 있지만 alloc에는 없습니다. 각 설정 분기의 실제 선언 목록을 확인해야 합니다.'),
        ('READ_ONCE로 scale과 offset을 각각 읽으면 버전 재검사를 생략할 수 있는가?', '아니다. 서로 다른 갱신의 두 값이 섞였는지 sequence로 확인해야 한다', '그렇다. READ_ONCE가 페이지 전체에 쓰기 잠금을 건다', 'READ_ONCE는 여러 필드를 함께 잠그는 연산이 아닙니다. 전후 sequence와 장벽, 필요 시 재시도가 스냅샷 프로토콜을 구성합니다.')
    ]
)]
