"""Whole generic fixed mapping conversion and setup interface."""
ROWS = [dict(
    path='include/asm-generic/fixmap.h',
    title='공통 fixmap 전체: 역방향 주소와 offset 매핑',
    intro='고정 슬롯의 주소 계산, 경계 검사와 페이지 속성 기본값, 매핑 wrapper를 해설합니다.',
    principle='슬롯 번호는 주소가 아니며 페이지 기반 주소와 페이지 내부 offset을 결합해야 실제 바이트 위치를 얻습니다.',
    use='ARM fixmap.h의 영역·열거형·보호 속성과 이 공통 변환을 함께 읽습니다.',
    area='가상 주소 · 페이지 정렬 · 경계 검사 · 전처리 매크로 · PTE 속성',
    sections=[
        ('파일 구조', 'GPL 안내와 기여 이력, guard, bug.h·mm_types.h 포함 뒤 두 산술 변환을 정의합니다. C 함수·보호 속성·설정 매크로는 비어셈블리 분기 안에 있습니다. FIXADDR_TOP, START, 슬롯 끝, 페이지 크기, __set_fixmap 구현 등은 아키텍처 측 정의에 의존합니다.'),
        ('내려가는 슬롯 주소', '__fix_to_virt(x)는 FIXADDR_TOP-(x<<PAGE_SHIFT)입니다. 슬롯 번호가1 증가하면 주소는 한 페이지 낮아집니다. __virt_to_fix(x)는 x를 PAGE_MASK로 내림 정렬하고 TOP과의 차이를 페이지 단위로 바꿉니다. 페이지 내부 byte offset은 슬롯 번호에 영향을 주지 않습니다. 두 내부 매크로 자체에는 범위 검사가 없습니다.'),
        ('슬롯 검사', 'fix_to_virt는 unsigned int idx를 받는 always_inline 함수입니다. BUILD_BUG_ON으로 idx>=__end_of_fixed_addresses를 검사한 뒤 내부 변환을 반환합니다. 주석의 compile-time allocation 취지에 맞는 빌드 시 검사이며 잘못된 인덱스에 오류 코드를 반환하는 런타임 할당 함수가 아닙니다. 슬롯 번호를 포인터처럼 직접 쓰지 않도록 주소 변환을 구별해야 합니다.'),
        ('주소 검사와 위 경계', 'virt_to_fix는 vaddr>=FIXADDR_TOP 또는 vaddr<FIXADDR_START이면 BUG_ON을 실행합니다. 따라서 이 본문은 START를 허용하고 TOP 자체는 거부합니다. fix_to_virt(0)은 TOP을 계산하지만 그 값을 public virt_to_fix에 넣으면 거부하므로 모든 입력에서 두 public 함수가 대칭 역함수라고 설명하면 틀립니다. 내부 산술식의 역관계와 public 허용 범위를 따로 읽습니다.'),
        ('정상 주소 예제', 'PAGE_SIZE=4096, TOP=T라고 가정하면 슬롯3 주소는 T-12288입니다. 이 페이지의 offset37 주소를 내부 역변환하면 PAGE_MASK가37을 제거해 슬롯3을 얻습니다. public 역변환에는 별도로 START 이상·TOP 미만 조건이 필요합니다. 숫자 계산만으로 실제 매핑이 존재하는지 증명되지는 않습니다.'),
        ('보호 속성 기본값', '아키텍처가 정의하지 않은 NORMAL은 PAGE_KERNEL, NOCACHE는 PAGE_KERNEL_NOCACHE, IO는 PAGE_KERNEL_IO로 둡니다. RO는 아직 없고 PAGE_KERNEL_RO가 존재할 때만 정의합니다. CLEAR 기본값은 __pgprot(0)입니다. 모든 플랫폼에 RO 기본값이 반드시 생긴다고 가정하면 안 되며 기존 ARM 정의들은 유지됩니다.'),
        ('설정과 해제 wrapper', 'set_fixmap이 없으면 __set_fixmap(idx,phys,NORMAL)로, clear_fixmap이 없으면 __set_fixmap(idx,0,CLEAR)로 정의합니다. clear는 일반 보호 속성으로 물리주소0을 매핑하는 요청과 다릅니다. 물리 페이지를 free하는 코드나 슬롯 사용 충돌을 막는 잠금은 이 매크로 본문에 없습니다.'),
        ('Offset 보존', '__set_fixmap_offset은 먼저 __set_fixmap(idx,phys,flags)를 호출하고 fix_to_virt(idx)+(phys&(PAGE_SIZE-1))를 unsigned long 지역 변수에 담아 반환합니다. 주석은 pointer라고 표현하지만 반환식의 C 타입은 여기서 unsigned long입니다. 원래 물리주소의 페이지 내부 offset을 결과 가상 주소에도 보존합니다. 저수준 호출에 넘기기 전에 phys를 이 wrapper가 직접 정렬하는 것은 아닙니다.'),
        ('Offset 예제와 평가 횟수', '4KiB 페이지에서 phys=0x12345이면 보존할 offset은0x345입니다. 반환 주소는 해당 슬롯 시작+0x345입니다. idx와 phys는 __set_fixmap 호출과 이후 계산에 다시 등장하므로 부작용 있는 인자를 항상 한 번만 평가한다고 설명하면 안 됩니다. 여러 페이지를 자동으로 연속 매핑하는 루프도 없습니다.'),
        ('속성별 공개 매크로', 'set_fixmap_offset은 NORMAL, set_fixmap_nocache는 NOCACHE로 일반 설정, set_fixmap_offset_nocache는 offset 보존과 NOCACHE를 조합합니다. set_fixmap_io는 IO 속성으로 설정합니다. 이 파일에는 별도의 set_fixmap_offset_io wrapper 정의가 없으며 주석의 하드웨어 목적과 제공 API를 구별합니다.'),
        ('CS 연결과 범위', '페이지 정렬과 낮은 비트 마스크, 역방향 주소 공간 배치, compile-time 검사와 BUG_ON, fallback 정의, 매크로 다중 평가, 매핑과 할당의 차이를 학습합니다. 실제 PTE 저장·TLB 동기화는 __set_fixmap 구현과 호출 문맥을 추가로 확인해야 하며 이 파일의 해설은 전체 MMU 실행 검증이 아닙니다.')
    ],
    questions=[
        ('슬롯 번호가1 커지면 주소는 어떻게 변하는가?', '한 페이지 낮아진다', '한 페이지 높아진다', '식은 TOP에서 인덱스의 페이지 단위 값을 뺍니다. 일반적인 증가 방향 배열 주소와 반대입니다.'),
        ('virt_to_fix(FIXADDR_TOP)은 이 public 함수에서 허용되는가?', '아니다. >=TOP 검사에 걸린다', '그렇다. fix_to_virt(0)이므로 자동 허용된다', '산술 역관계와 public 경계는 다릅니다. 본문은 TOP 자체도 BUG_ON 대상으로 삼습니다.'),
        ('4KiB 페이지에서 phys=0x12345의 offset 매핑은 무엇을 더하는가?', '슬롯 시작에0x345를 더한다', '슬롯 시작에0x12345 전체를 더한다', 'phys&(PAGE_SIZE-1)은 낮은12비트만 보존합니다. 물리주소 전체를 가상 슬롯 시작에 더하지 않습니다.'),
        ('clear_fixmap이 물리주소0을 정상 페이지 속성으로 매핑하는가?', '아니다. 별도의 CLEAR 속성으로 __set_fixmap을 호출한다', '그렇다. NORMAL 속성은 항상 유지된다', '기본 CLEAR는 __pgprot(0)입니다. 주소 인자0만 보고 일반적인 물리페이지0 매핑으로 해석하면 틀립니다.'),
        ('__set_fixmap_offset의 idx와 phys 인자는 언제나 한 번만 평가되는가?', '아니다. 설정 호출과 주소 계산에 반복 사용된다', '그렇다. 모든 인자가 먼저 지역 변수에 저장된다', '지역 변수는 계산된 반환 주소를 담을 뿐입니다. 인자 자체의 값을 각각 한 번 저장하는 구조가 아니므로 부작용 있는 표현식에 주의해야 합니다.')
    ]
)]
