"""Whole-file cyclecounter API and timecounter implementation lessons."""
ROWS = [dict(
    path='include/linux/timecounter.h',
    title='Cyclecounter와 timecounter: 하드웨어 tick과 나노초 상태 분리',
    intro='두 구조체, 마스크 매크로, 두 inline 함수와 세 공개 함수의 계약을 읽습니다.',
    principle='하드웨어 관측은 cyclecounter로 추상화하고, 경과 시간과 소수 나노초의 누적 상태는 timecounter가 보관합니다.',
    use='장치 시계의 tick을 기준 시각이 있는 나노초 값으로 바꾸는 드라이버 코드를 이해합니다.',
    area='운영체제 · 시간 측정 · 고정 소수점 · 모듈러 산술 · 하드웨어 추상화',
    sections=[
        ('전체 선언 구조', 'GPL-2.0-or-later 표시와 clocksource.h에서 옮겨 왔다는 주석, guard와 types include 뒤 CYCLECOUNTER_MASK, 두 구조체, 두 inline 함수, init/read/cyc2time 선언이 있습니다. 이 헤더가 특정 하드웨어를 초기화하거나 타이머 인터럽트를 등록하지는 않습니다.'),
        ('하드웨어 폭 마스크', 'CYCLECOUNTER_MASK(bits)는 bits<64이면 (1ULL<<bits)-1, 아니면 u64로 변환한 -1을 반환합니다. 예를 들어 8비트는 255, 64비트는 모든 비트가 1입니다. 조건식 덕분에 bits=64에서 1ULL<<64를 평가하지 않습니다. bits=0은 0이고, 음수 등 잘못된 폭을 검사하는 함수는 아닙니다. bits 인자가 여러 번 나타나므로 부작용 있는 표현식을 피합니다.'),
        ('Cyclecounter의 네 필드', 'read는 const cyclecounter 포인터를 받아 u64 tick을 반환하는 callback입니다. mask는 하드웨어 카운터 폭의 하위 비트 마스크, mult는 나노초 변환의 분자, shift는 2의 거듭제곱 분모의 지수입니다. cyclecounter 자체에는 직전 tick이나 누적 시간이 없어 상태 없는 접근 추상화입니다. 특정 read callback의 잠금 규칙은 구현자와 사용자가 정합니다.'),
        ('Timecounter의 다섯 필드', 'cc는 기반 cyclecounter, cycle_last는 마지막 관측 tick, nsec는 누적 나노초, mask는 frac를 보관할 하위 비트 마스크, frac는 누적된 소수 나노초입니다. cc->mask와 tc->mask는 역할이 다릅니다. 전자는 하드웨어 래핑 계산이고 후자는 고정 소수점 나머지입니다.'),
        ('소수점 보존 변환', 'cyclecounter_cyc2ns는 ns=cycles*mult+*frac를 계산하고 *frac=ns&mask를 저장한 뒤 ns>>shift를 반환합니다. mask가 shift에 맞는 하위 비트 마스크라는 전제에서 몫은 정수 나노초, 나머지는 다음 호출로 넘길 소수 단위입니다. 예를 들어 mult=3, shift=2, mask=3에서 한 tick씩 네 번 변환하면 반환값은 0,1,1,1이며 합계 3ns입니다. 매번 소수 부분을 버리면 모두 0이 됩니다.'),
        ('정수 산술의 전제', '계산 중간값은 u64이고 포화 연산이나 overflow 검사가 없습니다. mult/shift 선택과 한 번에 변환하는 cycles 범위는 호출자가 보장해야 합니다. shift는 u32라는 이유만으로 임의의 큰 값도 유효하지 않습니다. 구현의 1ULL<<shift와 우측 shift에 맞는 범위가 필요합니다. 이 표현은 부동 소수점이 아니라 정수 고정 소수점입니다.'),
        ('시각 보정', 'timecounter_adjtime는 tc->nsec += delta 한 줄입니다. s64 delta가 음수면 일반적인 범위에서 시각을 뒤로 옮길 수 있습니다. u64 nsec와의 연산은 unsigned 모듈러 산술이므로 0 아래로 내리면 포화하지 않고 래핑할 수 있습니다. cycle_last나 frac를 재설정하지 않으며 자체 잠금도 없습니다. 따라서 nsec가 증가한다는 구조체 설명을 수동 보정까지 금지한 단조성 보장으로 읽지 않습니다.'),
        ('초기화와 읽기 계약', 'init은 준비된 cc와 임의의 시작 나노초 시각을 연결합니다. read는 시작값에 경과 나노초를 더한 시각을 돌려줍니다. 하드웨어 초기화, 동시 접근의 직렬화, 하드웨어가 한 주기를 도는 것보다 자주 읽는 일은 사용자 책임입니다. 나노초 u64의 약 585년 범위는 하드웨어를 585년 동안 읽지 않아도 된다는 뜻이 아닙니다.'),
        ('과거 tick 변환 계약', 'cyc2time는 저장된 기준 시각 주변의 tick을 같은 시간축으로 변환하며 과거 tick도 지원합니다. 헤더는 mask+1 주기의 반주기 이내 범위를 설명합니다. 주기의 정확한 절반 떨어진 점은 과거와 미래를 구분할 수 없으며 구현은 뒤쪽으로 해석합니다. 긴 시간 전에 저장한 tick은 이 API만으로 어느 회전의 값인지 복원할 수 없습니다.'),
        ('검증과 학습 연결', '전체 API의 역할과 실제 구현과 연결되는 호출 조건을 설명합니다. 하드웨어 주파수 보정이나 실제 장치 정확도를 측정한 자료는 아닙니다. 두 종류의 마스크, 나머지 누적을 통한 정밀도 유지, epoch 선택, 단조 증가와 시간 보정의 차이를 학습합니다.')
    ],
    questions=[
        ('cc->mask와 tc->mask는 같은 의미인가?', '아니다. 하드웨어 폭과 소수점 나머지 폭을 각각 나타낸다', '그렇다. 모두 장치 레지스터의 비트 수만 나타낸다', 'tick 차이에는 cc->mask를, 변환 후 frac 저장에는 tc->mask를 사용합니다. 구체적인 값이 우연히 같더라도 역할은 다릅니다.'),
        ('mult=3, shift=2에서 frac를 보존하며 한 tick을 네 번 변환한 나노초 합은?', '3ns이다', '0ns이다', '3/4ns를 네 번 더하는 고정 소수점 누적입니다. 나머지가 3,2,1,0으로 이어지며 정수 반환값은 0,1,1,1입니다.'),
        ('timecounter_adjtime는 frac와 마지막 tick도 초기화하는가?', '아니다. nsec에 delta만 더한다', '그렇다. 하드웨어를 다시 읽어 전부 초기화한다', 'inline 본문은 nsec += delta 한 줄입니다. 다른 상태를 바꾸지 않으며 음수 보정과 unsigned 경계 처리는 사용자가 이해해야 합니다.'),
        ('64비트 나노초 범위가 길면 하드웨어 카운터를 오랫동안 읽지 않아도 되는가?', '아니다. 하드웨어 래핑 주기보다 자주 읽어야 한다', '그렇다. 585년마다 읽어도 모든 tick을 복원한다', '누적 결과의 폭과 샘플링 가능한 간격은 다릅니다. 여러 하드웨어 회전을 놓치면 마스크 차이만으로 회전 수를 알 수 없습니다.')
    ]
), dict(
    path='kernel/time/timecounter.c',
    title='Timecounter 구현: 경과 tick 누적과 과거 시각 환산',
    intro='초기화, 증분 읽기, 역방향 고정 소수점 계산과 반주기 판정을 전체 구현으로 따라갑니다.',
    principle='경과 시간 누적은 앞으로 흐르는 모듈러 차이를 사용하고, 별도 tick 환산은 기준점에서 가까운 방향을 선택합니다.',
    use='타임스탬프 변환이 현재 누적 시계를 변경하는지, 반주기 경계에서 어느 방향을 선택하는지 판단합니다.',
    area='모듈러 거리 · 고정 소수점 · 샘플링 · 시간 기준점 · 상태 변경',
    sections=[
        ('전체 파일과 공개 범위', '라이선스와 clocksource 기반 주석, export/timecounter include 뒤 init, 내부 read_delta, read, 내부 cc_cyc2ns_backwards, cyc2time가 있습니다. init/read/cyc2time 세 함수는 EXPORT_SYMBOL_GPL입니다. 내부 두 helper는 static이며 별도 공개 API가 아닙니다.'),
        ('초기화 순서', 'init은 cc를 저장하고 cc->read(cc)로 현재 tick을 cycle_last에 기록하며 nsec를 start_tstamp로 설정합니다. frac mask는 (1ULL<<shift)-1이고 frac는 0입니다. 하드웨어 callback을 호출할 준비와 유효한 shift가 필요합니다. 포인터 유효성이나 shift 범위를 검사해 오류를 반환하는 함수는 아닙니다.'),
        ('증분 읽기', 'read_delta는 현재 tick을 한 번 읽고 (cycle_now-cycle_last)&cc->mask로 차이를 구합니다. 이 차이를 cyclecounter_cyc2ns로 변환하면서 tc->frac를 갱신하고 cycle_last를 새 값으로 바꾼 뒤 나노초 증분을 반환합니다. 따라서 시간 읽기 자체가 누적 상태를 변경합니다.'),
        ('래핑 예제와 샘플링 조건', '8비트 카운터에서 cycle_last=250, 현재=5이면 차이는 11 tick입니다. 그러나 정확히 256 tick이 지나 같은 값으로 돌아오면 차이는 0이므로 한 주기 전체를 놓치면 복원할 수 없습니다. helper의 한 번 이상 래핑하지 말라는 주석만 느슨하게 읽지 말고 헤더의 주기보다 자주 읽으라는 조건을 적용해야 합니다. 관측 사이에 수치상 경계 통과가 한 번 있더라도 경과량이 한 주기 이상이면 모호합니다.'),
        ('첫 호출 주석과 실제 코드', 'read_delta 주석에는 첫 호출이 추적을 초기화하고 결과가 정의되지 않는다는 설명이 남아 있습니다. 실제 코드는 첫 호출 여부를 검사하지 않습니다. timecounter_init이 이미 cycle_last, nsec, frac를 초기화하므로 올바른 init 뒤 첫 read는 그 사이의 경과량을 계산합니다. 초기화 없이 호출해도 알아서 초기화된다고 설명하면 안 됩니다.'),
        ('누적 시각 읽기', 'timecounter_read는 read_delta의 나노초 증분에 기존 tc->nsec를 더하고 그 결과를 tc->nsec에 저장하여 반환합니다. 별도 clock epoch를 생성하거나 시스템 wall clock을 자동 동기화하지 않습니다. 현재 epoch는 init의 시작값과 이후 보정이 정합니다. 동시 호출에 대한 lock은 여기 없습니다.'),
        ('역방향 변환 helper', 'cc_cyc2ns_backwards는 ((cycles*mult)-frac)>>shift를 반환합니다. 앞으로 변환할 때 frac를 더하는 것과 달리 기준점의 소수 잔여를 빼서 역방향 거리 계산에 반영합니다. frac는 값으로 전달되어 갱신되지 않습니다. mask 매개변수는 선언되어 있지만 본문에서 사용하지 않습니다. u64 곱셈과 뺄셈에 별도 overflow/underflow 검사는 없습니다.'),
        ('과거와 미래 선택', 'cyc2time는 (cycle_tstamp-cycle_last)&cc->mask를 delta로 구합니다. delta>cc->mask/2이면 과거로 보고 반대 방향 차이를 계산해 역방향 변환값을 nsec에서 뺍니다. 아니면 앞으로 변환한 값을 더합니다. mask=255이면 delta 0..127은 미래, 128..255는 과거입니다. 정확히 반주기 128은 과거 쪽입니다.'),
        ('구체적인 시각 환산', 'mask=255, cycle_last=250, nsec=1000, mult=1, shift=0, frac=0을 가정합니다. timestamp=5이면 앞으로 11 tick이므로 1011ns, timestamp=245이면 앞으로의 차이가 251이라 과거로 판단하여 995ns입니다. timestamp=122는 정확히 반주기 128 떨어져 있으므로 이 구현은 872ns를 선택합니다. 실제로 미래 128 tick이었는지는 값만으로 구분할 수 없습니다.'),
        ('환산은 상태를 진행시키지 않음', 'cyc2time의 tc 포인터는 const이고 nsec와 frac를 지역 변수로 복사합니다. 앞으로 변환할 때도 지역 frac 주소만 넘깁니다. cycle_last, tc->nsec, tc->frac를 바꾸거나 하드웨어 read를 새로 호출하지 않습니다. 따라서 반복 환산이 read를 대신하여 하드웨어 래핑을 추적해 주지는 않습니다.'),
        ('설계의 구분과 검증 범위', 'read_delta의 정방향 추적은 경과량이 한 주기 미만이라는 조건이고, cyc2time의 과거/미래 판정은 기준점 주변 반주기라는 더 좁은 조건입니다. 둘을 같은 제한으로 외우지 않습니다. 실제 소스 전체와 정수 예제를 대조한 학습 자료이며 물리 장치의 드리프트나 SMP 동시 실행을 검증한 결과는 아닙니다.')
    ],
    questions=[
        ('8비트 카운터가 250에서 5가 되었을 때 추적 가능한 경과 tick은?', '한 주기 미만 경과 전제에서 11이다', '언제나 정확히 261이다', '모듈러 차이는 11입니다. 267 등 여러 회전이 포함된 실제 경과량도 같은 관측을 만들 수 있으므로 읽기 간격 조건이 필수입니다.'),
        ('init 뒤 첫 read의 반환값은 무조건 정의되지 않는가?', '아니다. 초기화 시점 이후 경과량을 시작값에 더한다', '그렇다. 첫 read는 무조건 버려야 한다', '내부 helper의 오래된 주석과 달리 실제 init이 cycle_last와 frac를 준비합니다. 첫 호출을 따로 처리하는 분기는 없습니다.'),
        ('mask=255에서 cyc2time의 정방향 delta가 128이면 어느 방향인가?', '과거 방향이다', '미래 방향이다', '판정은 delta>mask/2이고 정수 나눗셈 결과는 127입니다. 따라서 128은 과거로 처리되며 정확히 반주기는 본질적으로 방향이 모호합니다.'),
        ('cyc2time를 자주 호출하면 timecounter_read 없이 래핑 추적 상태가 갱신되는가?', '아니다. 저장된 상태를 읽어 환산할 뿐이다', '그렇다. 매번 cycle_last를 새 tick으로 옮긴다', 'tc는 const이며 변환용 frac도 지역 복사입니다. 하드웨어 read도 없으므로 누적 상태를 진행시키려면 read가 필요합니다.'),
        ('역방향 helper의 mask 인자는 실제 계산에 사용되는가?', '아니다. 이 버전의 본문에서는 사용하지 않는다', '그렇다. 반환값을 반드시 mask와 AND한다', '실제 식은 ((cycles*mult)-frac)>>shift입니다. 함수 시그니처만 보고 정방향 함수와 같은 나머지 갱신을 추정하면 안 됩니다.')
    ]
)]
