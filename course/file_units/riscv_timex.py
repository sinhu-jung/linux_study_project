"""Whole RISC-V timer access interface and split-counter retry."""
ROWS = [dict(
    path='arch/riscv/include/asm/timex.h',
    title='RISC-V 시간 읽기 전체: high-low-high 재검사',
    intro='실행 모드별 카운터 접근과32비트에서64비트 시간을 조합하는 재시도 알고리즘을 해설합니다.',
    principle='변하는64비트 값을32비트 두 번으로 읽을 때 상위 절반을 다시 확인해 rollover로 섞인 값을 버립니다.',
    use='RISC-V delay.c의 get_cycles와 일반64비트 I/O 분할 읽기의 차이를 비교합니다.',
    area='시간 카운터 · CSR · MMIO · rollover · 낙관적 재시도 · 타입 폭',
    sections=[
        ('파일 전체 구성', 'GPL-2.0-only·저작권·guard와 csr.h 포함 뒤 cycles_t를 unsigned long으로 정의합니다. M-mode와 그 밖의 모드별 읽기,구성별 get_cycles64,현재 timer 출력 helper까지 제공합니다. cycles라는 이름만 보고 CPU core cycle 명령을 읽는다고 추측하지 말고 실제 TIME 또는 CLINT 접근을 봐야 합니다.'),
        ('M-mode64비트', 'CONFIG_RISCV_M_MODE이면 clint.h를 포함합니다.64비트 get_cycles는 clint_time_val에 readq_relaxed를 수행하고 cycles_t를 반환합니다. 이 함수에는 포인터 NULL 검사가 없으며 장치 주소 초기화와 접근 가능성은 호출 문맥의 전제입니다. relaxed 읽기를 별도의 full memory barrier로 설명하지 않습니다.'),
        ('M-mode32비트', '비64비트 get_cycles는 clint_time_val을 u32 포인터로 보아 낮은 word를 readl_relaxed로 읽습니다. get_cycles_hi는 그 포인터+1,즉4바이트 뒤의 상위 word를 읽습니다. 두 함수의 자기참조 매크로는 전처리에서 제공 여부를 표시합니다. 각 함수 자체는64비트 snapshot을 만들지 않습니다.'),
        ('초기 entropy 경로와 주석 차이', 'M-mode random_get_entropy는 clint_time_val이 NULL이면 random_get_entropy_fallback을 호출하고 아니면 get_cycles를 반환합니다. 바로 위 주석은 fallback이 없어0을 반환한다고 말하지만 실제 본문은 fallback 호출입니다. 이 불일치를 명시하며 해당 fallback의 반환값이나 엔트로피 품질을 여기서0 또는 암호학적 보장으로 단정하지 않습니다.'),
        ('다른 실행 모드', 'M-mode가 아니면 get_cycles는 csr_read(CSR_TIME),get_cycles_hi는 csr_read(CSR_TIMEH)를 사용합니다. 각 함수 이름의 자기참조 매크로도 정의합니다. 이 소스에 보이는 CSR 선택과 실제 하드웨어 구현·가상화 처리를 구분하며 CSR 명령 자체의 구현은 csr.h 범위입니다.'),
        ('64비트 조합 API', 'CONFIG_64BIT의 get_cycles64는 get_cycles 결과를 그대로 반환합니다. 비64비트에서는 hi를 먼저,lo를 다음에 읽고 상위 word를 다시 읽어 hi와 다르면 do-while 전체를 재시도합니다. 같으면((u64)hi<<32)|lo를 반환합니다. 상위값 변화를 감지했다가 lo만 다시 읽는 방식이 아닙니다.'),
        ('Rollover 예제', '첫 high가1이고 low를 읽기 전에 카운터가0x00000001ffffffff에서0x0000000200000000으로 넘어갔다면 low는0,두 번째 high는2입니다.1!=2이므로 혼합값0x0000000100000000을 반환하지 않고 재시도합니다. 장치별 일반 hi-lo I/O helper에 없었던 검증 단계가 이 시간 읽기에 있습니다.'),
        ('성립 조건과 반환값', '같은 high를 두 번 관찰하는 동안 정상 증가 counter의 low를 얻는다는 전제에 의존합니다. counter가 임의로 재설정되거나 전체 폭을 여러 번 순환하는 상황까지 무조건 증명하는 알고리즘은 아닙니다. 반환은 관찰했던 시점의 값이며 반환 순간의 최신값을 계속 재조회하지 않습니다. 반복 횟수의 고정 상한이나 timeout도 없습니다.'),
        ('현재 timer helper', 'ARCH_HAS_READ_CURRENT_TIMER를 정의하고 read_current_timer는 *timer_val=get_cycles 후0을 반환합니다.32비트에서는 get_cycles64가 아닌 낮은 word 경로를 사용합니다. 출력 포인터 유효성 검사나 M-mode의 NULL CLINT 검사가 여기서 추가되는 것은 아닙니다. entropy 함수의 방어 분기를 모든 읽기 API에 적용했다고 설명하면 틀립니다.'),
        ('CS 연결과 검증 범위', 'MMIO와 CSR 인터페이스,word 폭,분할 카운터의 낙관적 일관성 검사,rollover,전처리 기능 표시,주석과 구현 대조를 학습합니다. 이 자료는 실제 RISC-V 타이머 접근·가상화·엔트로피 품질을 실행 검증한 것이 아닙니다.')
    ],
    questions=[
        ('32비트 get_cycles64의 읽기 순서는?', 'high,low,high 확인이며 불일치하면 반복한다', 'low,high 한 번씩만 읽는다', 'do-while 조건에서 상위 word를 다시 읽습니다. 다르면 첫 high와 low 읽기부터 반복합니다.'),
        ('high1,low0,재검사 high2이면 반환하는가?', '아니다. rollover 가능성이 있어 다시 읽는다', '그렇다.0x0000000100000000을 반환한다', '첫 high와 마지막 high가 달라 조건이 참이므로 루프를 반복합니다. 두 시점의 절반이 섞인 결과를 버리는 예입니다.'),
        ('M-mode entropy 함수가 NULL CLINT에서 실제로 하는 것은?', 'random_get_entropy_fallback 호출이다', '본문에서 상수0을 직접 반환한다', '주석과 본문이 다릅니다. 실제 동작은 fallback 호출이며 그 내부 결과를 이 파일만으로 단정할 수 없습니다.'),
        ('32비트 read_current_timer가 get_cycles64를 호출하는가?', '아니다. get_cycles 값을 unsigned long 출력에 쓴다', '그렇다. 항상64비트를 조합한다', '본문은 *timer_val=get_cycles()입니다.64비트 일관성 helper와 기존 word 크기 인터페이스를 구별해야 합니다.'),
        ('get_cycles라는 이름만으로 CPU core cycle 수를 읽는다고 해석해도 되는가?', '안 된다. 이 파일은 TIME CSR 또는 CLINT 시간 값을 읽는다', '된다. 이름이 하드웨어 소스를 확정한다', '구현의 CSR_TIME과 clint_time_val을 확인해야 합니다. delay의 주파수 변환과 함께 실제 단위를 읽는 것이 중요합니다.')
    ]
)]
