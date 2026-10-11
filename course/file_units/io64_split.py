"""Individually explained low-first and high-first split I/O accessors."""
ROWS = [dict(
    path='include/linux/io-64-nonatomic-lo-hi.h',
    title='64비트 분할 I/O 전체: 낮은 절반부터 접근',
    intro='두32비트 접근으로64비트 값을 만들 때 low-first 순서와 big-endian 주소 배치를 구별합니다.',
    principle='데이터의 상·하위 절반, 메모리 주소 순서, 접근 호출 순서는 서로 다른 축입니다.',
    use='장치가 요구하는 절반별 접근 순서를 확인한 뒤 명시적 helper와 public fallback의 선택을 읽습니다.',
    area='MMIO · 엔디언 · 비원자 접근 · 비트 조합 · 전처리 fallback',
    sections=[
        ('전체 구성', 'GPL-2.0·guard 뒤 io.h와 int-ll64.h를 포함합니다. low-first readq/writeq와 relaxed 네 helper, 각 public fallback, 일반 및 big-endian ioread/iowrite helper 네 개,64비트 public 별칭과 nonatomic 표지를 제공합니다. 실제32비트 accessor의 아키텍처 구현은 포함된 계층의 범위입니다.'),
        ('일반 readq 조합', 'lo_hi_readq는 addr를 u32 포인터 p로 보고 low=readl(p)를 먼저,high=readl(p+1)을 다음에 수행합니다. p+1은4바이트 뒤입니다. low+((u64)high<<32)로 조합하며 high를 먼저64비트로 확장한 뒤 이동합니다. 두 절반의 비트 영역이 겹치지 않으므로 여기서 덧셈은 OR와 같은 결과입니다.'),
        ('일반 writeq 분해', 'lo_hi_writeq는 writel(val,addr) 뒤 writel(val>>32,addr+4)를 호출합니다. 첫32비트 accessor에는 하위32비트가 전달되고 두 번째에는 상위 절반이 전달됩니다. void 포인터에4를 더하는 부분은 커널이 사용하는 GNU C의 바이트 단위 포인터 산술입니다.'),
        ('Relaxed 계열', 'lo_hi_readq_relaxed/writeq_relaxed는 같은 주소·절반 순서를 유지하면서32비트 primitive를 relaxed로 바꿉니다. 이 파일은 별도의 장벽이나 재시도 루프를 추가하지 않습니다. relaxed라는 이름이 두 번의 접근을 한 번의 원자 접근으로 합치는 것은 아닙니다.'),
        ('Readq 이름의 fallback', 'readq/writeq/readq_relaxed/writeq_relaxed가 각각 아직 매크로로 정의되지 않았으면 대응 low-first helper에 연결합니다. 이미 제공된 정의를 강제로 덮어쓰지 않습니다. 따라서 이 헤더를 포함했다는 사실만으로 모든 호출이 반드시 분할 접근이 된다고 단정할 수 없습니다.'),
        ('Ioread/iowrite 일반 계열', 'ioread64_lo_hi는 ioread32(addr) 다음 ioread32(addr+sizeof(u32))를 조합합니다. iowrite64_lo_hi도 같은 주소 순서로 두 절반을 씁니다. 각 함수는 #ifndef로 보호되고 자기참조 매크로를 함께 정의해 제공 여부를 전처리 단계에 알립니다. readl과 ioread32의 구체적 차이는 아키텍처·I/O 구현에 있으므로 이 파일에서 같은 함수라고 정의하지 않습니다.'),
        ('Big-endian도 low-first', 'ioread64be_lo_hi는 low를 addr+4에서 먼저 읽고 high를 addr에서 나중에 읽으며 각 절반에는 ioread32be를 사용합니다. 쓰기도 low를addr+4,high를addr 순서로 iowrite32be합니다. big-endian 배치에서는 상위 절반이 낮은 주소에 있으므로 low-first는 주소가 증가하는 순서가 아닙니다.'),
        ('Public nonatomic 표지', 'ioread64/iowrite64/ioread64be/iowrite64be가 각각 없을 때 해당 low-first helper를 별칭으로 만들고 대응 *_is_nonatomic 매크로를 빈 정의로 제공합니다. 이는 정의 존재로 검사하는 표지이며 정수1 값이나 런타임 변수로 제공하는 것이 아닙니다. 기존 public 정의가 있으면 해당 분기의 표지도 추가되지 않습니다.'),
        ('값의 일관성과 범위', '예를 들어 high=0x11223344,low=0x55667788을 조합하면0x1122334455667788입니다. 그러나 두 읽기 사이에 장치가 값을 바꾸면 서로 다른 시점의 절반이 섞일 수 있습니다. 이 파일에는 snapshot latch를 작동시키거나 high를 다시 확인하는 코드,정렬·주소 검증,잠금이 없습니다. 장치별로 요구하는 순서를 따르는 것과 원자적 snapshot은 구분해야 합니다.')
    ],
    questions=[
        ('ioread64be_lo_hi가 먼저 읽는 주소는?', 'addr+4이다', 'addr이다', 'low-first이고 big-endian의 하위 절반은 높은 주소에 있습니다. 먼저 low를addr+sizeof(u32),다음 high를addr에서 읽습니다.'),
        ('high를32비트 왼쪽 이동하기 전에 u64로 변환하는 이유는?', '64비트 결과의 상위 절반에 배치하기 위해서이다', '메모리에서 high를 다시 읽기 위해서이다', '식은((u64)high<<32)입니다. 타입 확장 후 이동하며 재읽기를 추가하지 않습니다.'),
        ('readq가 이미 매크로로 제공되면 이 헤더가 덮어쓰는가?', '아니다. #ifndef로 기존 정의를 유지한다', '그렇다. 무조건 low-first로 바뀐다', 'fallback 정의의 적용 여부와 명시적 lo_hi_readq helper 호출을 구분해야 합니다.'),
        ('두 읽기 사이 장치 값이 바뀌어도64비트 snapshot이 보장되는가?', '아니다. 절반이 서로 다른 시점일 수 있다', '그렇다. u64 반환형이면 자동 원자적이다', '반환형은 값의 폭이고 장치 접근은 두 번입니다. 원자적 관찰을 위한 장치 프로토콜이나 검증 루프는 이 본문에 없습니다.')
    ]
), dict(
    path='include/linux/io-64-nonatomic-hi-lo.h',
    title='64비트 분할 I/O 전체: 높은 절반부터 접근',
    intro='high-first readq와 ioread 계열을 low-first 구현과 비교합니다.',
    principle='상위 절반을 먼저 접근해야 하는 장치 규약을 코드의 호출 순서로 표현하되64비트 원자성을 별도로 가정하지 않습니다.',
    use='엔디언이 주소 배치를 결정하고 hi-lo가 접근 절반 순서를 결정한다는 점을 예제로 확인합니다.',
    area='I/O 접근 순서 · 엔디언 · 비트 분해 · 구성별 대체 · 데이터 일관성',
    sections=[
        ('전체 구성', 'GPL-2.0·guard·io.h·int-ll64.h 뒤 high-first readq/writeq와 relaxed helper,네 public fallback,네 ioread/iowrite helper,nonatomic public 별칭을 정의합니다. low-first 헤더와 별개의 guard를 쓰며 두 헤더가 제공하는 명시적 helper 이름도 서로 다릅니다.'),
        ('일반 readq', 'hi_lo_readq는 u32 포인터 p+1에서 high를 먼저 읽고 p에서 low를 다음에 읽습니다. 반환식은 low+((u64)high<<32)입니다. 호출 순서가 high-first여도 반환값의 숫자상 비트 배치는 low-first와 동일합니다. 주소만 보면 먼저 높은 주소,그다음 낮은 주소에 접근합니다.'),
        ('일반 writeq', 'hi_lo_writeq는 val>>32를 addr+4에 먼저 writel하고 val을addr에 나중에 writel합니다. 예를 들어0x1122334455667788이면0x11223344를+4,0x55667788을+0 순서로 전달합니다. 장치가 언제 전체 값을 반영하는지까지 이 두 호출만으로 증명하지 않습니다.'),
        ('Relaxed와 기본 이름', 'relaxed 두 helper는 같은 high-first 순서로 readl_relaxed/writel_relaxed를 사용합니다. 네 readq/writeq public 이름은 각 #ifndef에서만 high-first에 연결됩니다. 이미 존재하는 public 정의는 유지하므로 헤더를 포함한 순서와 아키텍처 제공 여부를 함께 확인해야 합니다.'),
        ('Ioread32 기반 helper', 'ioread64_hi_lo는 high=ioread32(addr+4),low=ioread32(addr) 순서입니다. iowrite64_hi_lo도 같은 주소 순서로 상·하위 절반을 씁니다. 각각 #ifndef와 자기참조 매크로가 있어 아키텍처별 제공 여부를 인지합니다. 별도의 메모리 할당이나 매핑 설치는 수행하지 않습니다.'),
        ('Big-endian high-first', 'ioread64be_hi_lo는 high=ioread32be(addr),low=ioread32be(addr+4)로 읽습니다. 쓰기는 high를addr에 먼저,low를addr+4에 다음에 iowrite32be합니다. big-endian에서 상위 절반이 낮은 주소이므로 이 경우는 주소 증가 순서입니다. hi-lo 이름을 주소 감소 순서의 동의어로 쓰면 틀립니다.'),
        ('Nonatomic 별칭', 'ioread64/iowrite64와 be 이름이 아직 없을 때 각각 high-first helper로 정의하고 *_is_nonatomic 표지를 둡니다. 표지는 빈 매크로이며 native64 접근이 이미 있으면 이 fallback이 강제되지 않습니다. 두 순서 헤더를 모두 포함해도 뒤의 public #ifndef가 앞에서 설정한 이름을 덮어쓰지 않습니다.'),
        ('경쟁 읽기 예제', '장치 카운터가0x00000001ffffffff에서0x0000000200000000으로 바뀌는 사이 high를1로 먼저 읽고 low를0으로 나중에 읽으면0x0000000100000000을 조합할 수 있습니다. 이 파일은 재확인 루프가 없으므로 high-first만으로 rollover 일관성이 확보되지 않습니다. 실제 latch 동작이나 권장 순서는 장치 규약에서 결정해야 합니다.'),
        ('CS 연결과 범위', '데이터 유효 폭과 버스 접근 폭, 엔디언과 호출 순서의 분리, 타입 확장 후 비트 이동, fallback과 원자성 표지, 시간에 따른 관찰 불일치를 학습합니다. 본문에 추가 장벽·오류 검사·재시도가 없다는 사실을 확인하며 특정 장치에서의 실행 시험 결과로 제시하지 않습니다.')
    ],
    questions=[
        ('hi_lo_readq와 ioread64be_hi_lo가 첫 번째로 읽는 주소는 각각?', 'addr+4와 addr이다', '둘 다 addr+4이다', '둘 다 high를 먼저 읽지만 일반 배치와 big-endian 배치에서 high의 주소가 다릅니다.'),
        ('high-first는 반환된64비트 숫자의 상하 절반을 교환하는가?', '아니다. low+((u64)high<<32)로 같은 숫자 배치를 만든다', '그렇다. low를 상위32비트에 놓는다', 'hi-lo는 접근 순서입니다. 반환값 조합식은 두 순서 구현에서 동일합니다.'),
        ('예전 high1과 rollover 후 low0을 조합하면?', '0x0000000100000000이다', '반드시0x0000000200000000이다', 'high를 다시 읽지 않으므로 저장해 둔1을 사용합니다. 두 번의 접근에 시간차가 있다는 점이 nonatomic의 핵심입니다.'),
        ('두 순서 헤더를 모두 포함하면 두 번째가 public ioread64를 무조건 바꾸는가?', '아니다. 이미 정의된 이름은 #ifndef로 유지한다', '그렇다. 항상 마지막 헤더가 우선한다', 'public 별칭은 정의가 없을 때만 제공됩니다. 장치별 명시적 helper 선택과 기존 아키텍처 정의를 함께 확인해야 합니다.')
    ]
)]
