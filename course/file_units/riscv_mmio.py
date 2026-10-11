"""Whole RISC-V MMIO accessor layering."""
ROWS = [dict(
    path='arch/riscv/include/asm/mmio.h',
    title='RISC-V MMIO 전체: raw·relaxed·일반 접근의 계층',
    intro='접근 폭,엔디언 변환,장치 순서와 일반 메모리 순서를 분리해 읽습니다.',
    principle='같은 load/store 명령을 사용해도 주변 변환과 장벽이 다르면 API의 계약이 달라집니다.',
    use='CLINT의 relaxed 시간 읽기와 장치 데이터의 readl/writel을 구별합니다.',
    area='MMIO · 엔디언 · 인라인 asm · 메모리 순서 · pending 상태',
    sections=[
        ('전체 구성', 'GPL-2.0-only·ARM 계열 기반 설명·저작권·guard 뒤 types/fence/mmiowb 헤더를 포함합니다. native-endian raw 함수,unordered cpu 매크로,relaxed 계층,일반 계층으로 구성됩니다. 모든 q 접근은 CONFIG_64BIT 안에서만 정의합니다. 이 파일 자체는32비트에서 q를 분할해 구현하지 않습니다.'),
        ('Raw 쓰기', '__raw_writeb/w/l은 u8/u16/u32 값과 volatile __iomem 주소를 받아 각각 sb/sh/sw를 사용합니다.64비트 q는u64와 sd입니다. asm은 volatile이고 값·주소를 레지스터 입력으로 받지만 이 raw 본문에는 memory clobber와 FENCE가 없습니다. 자기참조 매크로는 제공 여부를 표시합니다.'),
        ('Raw 읽기', '__raw_readb/w/l은 lb/lh/lw로 읽어 각각 u8/u16/u32 변수에 담아 반환하며64비트 q는 ld와u64입니다. 명령의 레지스터 확장 동작과 C 반환 타입의 폭을 구분합니다. 예를 들어 byte의 하위8비트가0xff라면 u8 반환값은255이며 signed -1 반환 함수가 아닙니다. 입력은 const volatile __iomem 포인터입니다.'),
        ('Native와 little-endian 변환', 'raw 주석은 native-endian 접근이라고 명시합니다. readw_cpu/readl_cpu/readq_cpu는 raw 값에 le16/32/64_to_cpu를 적용하고 쓰기는 cpu_to_le16/32/64 뒤 raw를 호출합니다. byte에는 endian 변환이 필요하지 않습니다. __force는 타입 주석 변환이며 그 자체가 바이트 교환 명령이라는 뜻은 아닙니다.'),
        ('Unordered 계층', 'read/write*_cpu 주석은 relaxed보다도 약하며 연속 I/O 영역 접근 사이의 순서도 보장하지 않는다고 설명합니다. _cpu라는 접미사가 일반 RAM 전용 접근이나 자동 full barrier를 의미하지 않습니다. 이 계층은 엔디언 처리와 기본 접근을 조합하며 장치별 protocol을 검사하지 않습니다.'),
        ('Relaxed의 계약과 플랫폼 전제', 'relaxed 주석은 같은 peripheral의 I/O 접근 순서는 따르지만 Normal 메모리와의 순서는 보장하지 않는다고 설명합니다. 플랫폼의 I/O 영역이 channel0에서 strongly ordered라는 전제 때문에 별도 fence가 필요하지 않다고 명시합니다. 이것을 모든 임의 RISC-V 장치 배치의 검증 결과로 확대하지 않습니다.'),
        ('Relaxed hook과 wrapper', '__io_rbr/rar/rbw/raw는 모두 빈 do-while입니다. relaxed 읽기는 앞 hook,cpu 읽기,뒤 hook,저장값 반환 순서이고 쓰기도 앞 hook,cpu 쓰기,뒤 hook입니다. 이 고정 버전에서는 hook이 비어 있으므로 본문이 cpu 접근과 유사해도 문서화된 사용 계약을 함께 읽어야 합니다. FIXME는 asm-generic과 같아졌다고 기록합니다.'),
        ('일반 읽기 장벽', '__io_br은 빈 함수형 매크로이고 __io_ar(v)는 RISCV_FENCE(i,ir)입니다. 일반 readb/w/l/q는 먼저 읽어 __v에 담고 그 뒤 장벽을 실행해 보관한 값을 반환합니다. hook 인자 v는 이 구현의 fence 본문에서 쓰지 않습니다. 주석은 뒤따르는 Normal 읽기와 delay loop에 대한 순서를 설명하며 모든 방향의 full barrier로 과장하지 않습니다.'),
        ('일반 쓰기 장벽과 pending', '__io_bw는 RISCV_FENCE(w,o),__io_aw는 mmiowb_set_pending입니다. 따라서 일반 쓰기는 앞선 Normal 쓰기와 I/O 출력을 순서화하는 fence,실제 쓰기,pending 표시 순서입니다. pending helper를 호출했다고 여기서 직접 장치 readback을 하거나 모든 posted write 완료를 기다린다고 설명하지 않습니다. helper 내부 구현은 별도 헤더의 범위입니다.'),
        ('폭별 API와 적용 범위', '네 계층은8·16·32비트와 구성별64비트를 제공합니다. 장벽 유무와 endian 변환 여부를 접근 폭과 별도로 선택합니다. 이 파일에는 NULL·정렬·범위 검사,장치 소유권 확인,매핑 설치가 없습니다. readq가 존재하는64비트 구성이라는 사실만으로 모든 장치의64비트 bus 원자성이 보장되는 것도 아닙니다.'),
        ('CS 연결과 검증', '타입 폭과 레지스터 확장,하드웨어 접근과 endian 변환,플랫폼 순서 보장과 명시적 fence,compiler 계약과 CPU 계약,지연된 MMIO 동기화 표시를 학습합니다. 원본·구조 검사는 실제 플랫폼의 장치 순서나 모든 실행 문맥을 검증한 것이 아닙니다.')
    ],
    questions=[
        ('readl과 readl_relaxed의 명시적 장벽 차이는?', '일반 readl은 읽기 뒤 fence i,ir을 수행한다', 'relaxed만 읽기 뒤 full fence를 수행한다', '일반 __io_ar은 RISCV_FENCE(i,ir)이고 relaxed 전후 hook은 빈 정의입니다. Normal 메모리 순서 계약도 다릅니다.'),
        ('readl_cpu는 raw와 달리 어떤 변환을 추가하는가?', 'little-endian 값을 CPU 표현으로 변환한다', '가상주소를 물리주소로 번역한다', 'le32_to_cpu를 사용합니다. 주소 매핑이나 페이지 테이블 변환을 수행하는 함수가 아닙니다.'),
        ('일반 writel의 순서는?', 'fence w,o → 쓰기 → mmiowb_set_pending이다', '쓰기 → readback → 무조건 sleep이다', '매크로의 __io_bw,writel_cpu,__io_aw를 확장하면 이 순서입니다. readback이나 sleep은 본문에 없습니다.'),
        ('32비트 구성에서 이 파일 자체가 __raw_readq를 두 readl로 구현하는가?', '아니다. q 정의는 CONFIG_64BIT 안에 있다', '그렇다. 항상 자동 분할한다', '분할64비트 접근은 별도 nonatomic 헤더의 역할과 비교해야 합니다. 이 파일에 없는 fallback을 가정하면 틀립니다.'),
        ('__raw_readb가 하위 byte0xff를 읽으면 C 반환값은?', 'u8 값255이다', '항상 signed 값-1이다', 'lb의 레지스터 확장과 최종 u8 타입을 구분합니다. 함수의 반환 폭과 signedness는 선언에 명시되어 있습니다.')
    ]
)]
