"""Complete generic barrier definitions, including configuration branches."""
ROWS = [dict(
    path='include/asm-generic/barrier.h',
    title='공통 장벽 전체: 기본 구현과 SMP·가상화의 차이',
    intro='아키텍처 정의를 조합하는 공통 장벽 계층과 조건부 읽기 API를 해설합니다.',
    principle='이 헤더는 하드웨어 명령 하나가 아니라 아키텍처 재정의, 구성 조건, 계측을 결합하는 API 계층입니다.',
    use='RISC-V와 LoongArch 장벽에서 마지막에 포함한 공통 정의를 따라 실제 공개 API가 어떻게 선택되는지 확인합니다.',
    area='메모리 모델 · 조건부 컴파일 · 가상화 · 제어 의존성 · 영속 메모리',
    sections=[
        ('파일 구성과 적용 범위', 'GPL-2.0-or-later와 저작권, guard, 비어셈블리 조건 안에 compiler.h, kcsan-checks.h, rwonce.h를 포함합니다. nop이 없으면 volatile asm nop을 제공합니다. 단순 아키텍처나 새 포트의 출발점이라는 주석이 있으며 모든 하드웨어에서 compiler barrier만으로 충분하다는 보증은 아닙니다.'),
        ('아키텍처 계측 래퍼', '__mb/__rmb/__wmb가 정의되면 공개 mb/rmb/wmb는 각각 kcsan 계측 후 내부 장벽을 호출합니다. __dma_mb/__dma_rmb/__dma_wmb도 같은 방식입니다. 이 첫 래퍼들은 내부 이름의 존재를 #ifdef로 검사하며 뒤의 기본 구현과 조건 형태가 다릅니다. KCSAN 호출 자체를 하드웨어 장벽 명령으로 간주하지 않습니다.'),
        ('기본 장벽의 계층', '공개 mb가 없으면 barrier(), rmb와 wmb가 없으면 mb로 정의합니다. dma_mb/rmb/wmb는 대응 일반 장벽으로 내려갑니다. 주석은 장치와 통신할 때 UP에서도 CPU 순서가 필요하다고 명시합니다. 따라서 SMP가 아니란 이유만으로 장치 접근의 순서 문제가 없어지는 것은 아닙니다.'),
        ('내부 SMP 기본값', '__smp_mb/rmb/wmb가 없으면 mb/rmb/wmb를 사용합니다. 이후 공개 smp_*는 CONFIG_SMP일 때 KCSAN 계측과 이 내부 정의를 묶고 비SMP일 때 compiler barrier로 기본 정의합니다. 각 공개 정의는 #ifndef로 보호되므로 이미 제공된 아키텍처 정의를 유지합니다.'),
        ('저장 후 장벽', '__smp_store_mb의 기본값은 WRITE_ONCE(var,value) 뒤 __smp_mb입니다. var는 저장 대상 lvalue로 포인터를 역참조하는 형태의 API와 구별합니다. __smp_mb__before_atomic과 after_atomic의 기본값도 __smp_mb입니다. 이 매크로들은 앞뒤 원자 연산을 직접 수행하지 않습니다.'),
        ('내부 release/acquire', '__smp_store_release는 atomic type 정적 검사, __smp_mb, WRITE_ONCE 순서입니다. __smp_load_acquire는 READ_ONCE 값을 한정자를 제거한 scalar 지역 변수에 담고 타입 검사와 __smp_mb 뒤 원래 타입으로 반환합니다. 이 보수적인 기본 구현은 각 아키텍처가 더 좁은 장벽으로 바꿀 수 있습니다.'),
        ('SMP 공개 래퍼', 'SMP에서 smp_store_mb와 원자 연산 전후 장벽은 kcsan_mb를 먼저 호출합니다. smp_store_release는 kcsan_release 후 내부 release를, smp_load_acquire는 내부 acquire를 그대로 사용합니다. 모든 래퍼가 동일한 KCSAN 함수를 호출한다고 일반화하지 않습니다.'),
        ('비SMP 저장과 읽기', '비SMP 기본 smp_store_mb는 WRITE_ONCE 뒤 barrier입니다. before/after_atomic은 barrier이며 release 저장은 barrier 뒤 WRITE_ONCE입니다. acquire 읽기는 READ_ONCE 뒤 barrier 후 보관한 값을 반환합니다. 이 비SMP 공개 release/acquire 본문에는 내부 기본값의 compiletime_assert_atomic_type 호출이 없습니다. compiler 순서 제약도 남으므로 빈 연산이라고 부르면 틀립니다.'),
        ('가상 머신 장벽', 'virt_mb/rmb/wmb, virt_store_mb, virt_mb__before/after_atomic, virt_store_release/load_acquire는 CONFIG_SMP 분기 밖에서 내부 __smp 계열을 사용합니다. 단일 CPU 게스트도 SMP 호스트와 통신할 수 있기 때문입니다. 게스트의 smp_mb가 compiler barrier가 된다고 virt_mb도 같은 것으로 축소되는 것은 아닙니다.'),
        ('제어 의존성 뒤 acquire', 'smp_acquire__after_ctrl_dep의 기본값은 smp_rmb입니다. 주석은 제어 의존성이 LOAD→STORE를 제공하고 추가 RMB가 LOAD→LOAD를 제공해 함께 acquire 방향을 형성한다고 설명합니다. 유효한 제어 의존성이 있다는 전제 없이 임의의 if문과 rmb를 모든 통신의 증명으로 사용하면 안 됩니다. 읽기 추측을 하지 않는 아키텍처는 이를 barrier로 바꿀 수 있습니다.'),
        ('조건부 relaxed 읽기', 'smp_cond_load_relaxed는 ptr을 __PTR에 보관하고 루프에서 READ_ONCE 값을 VAL에 넣어 cond_expr를 검사합니다. 참이면 종료하고 아니면 cpu_relax 후 반복합니다. C lambda 대신 사전에 이름 붙인 VAL을 조건에서 사용합니다. 최종 관찰값을 반환하며 추가 순서 보장이나 timeout은 없습니다.'),
        ('조건부 acquire 읽기', 'smp_cond_load_acquire는 relaxed 조건부 읽기의 반환값을 _val에 담은 뒤 smp_acquire__after_ctrl_dep를 수행하고 값을 반환합니다. 매 반복마다 full barrier를 실행하는 본문이 아닙니다. 앞서 읽은 RISC-V의 relaxed 재정의도 이 공통 acquire 래퍼와 조합될 수 있습니다.'),
        ('영속 메모리 장벽', 'pmem_wmb의 기본값은 wmb입니다. 주석의 계약은 앞선 명령에 의해 영속 저장소로 쓰이는 수정이 뒤의 데이터 접근·전송 전에 영속 저장소를 갱신하게 하는 순서입니다. 이 매크로만 호출하면 모든 더러운 cache line을 자동으로 flush하거나 파일을 fsync한다는 설명은 원문에 없습니다. 필요한 영속화 명령과 아키텍처 구현을 함께 검토해야 합니다.'),
        ('Write combining 경계', 'io_stop_wc는 앞뒤 write-combining 접근이 병합되는 것을 제한하려는 인터페이스입니다. 주석은 병합 대기가 성능에 나쁜 경우를 설명하지만 공통 기본값은 빈 do-while 문입니다. 모든 플랫폼에서 CPU fence나 강제 flush 명령을 생성한다고 주장할 수 없습니다.'),
        ('주소 공간 전환 뒤 장벽', 'smp_mb__after_switch_mm의 기본값은 smp_mb입니다. switch_mm 자체가 암묵적인 smp_mb를 보장하는 아키텍처가 재정의할 수 있다는 주석입니다. 이 매크로는 주소 공간 전환이나 TLB 무효화를 직접 실행하지 않습니다.'),
        ('CS 연결과 검증 범위', '선택적 오버라이드, 구성별 코드 생성, wrapper 계층, 부분 순서와 제어 의존성, CPU와 compiler 계층, 가상화 통신, 영속성의 구분을 학습합니다. 소스 대응·구조 검사는 모든 아키텍처나 모든 경쟁 실행을 시험한 것이 아닙니다.')
    ],
    questions=[
        ('비SMP 게스트에서 virt_mb도 항상 compiler barrier로 축소되는가?', '아니다. virt_mb는 내부 __smp_mb를 사용한다', '그렇다. 공개 smp_mb와 같은 분기 안이다', 'virt 계열은 CONFIG_SMP 분기 밖입니다. SMP 호스트와 통신하는 게스트의 요구를 위해 내부 장벽과 KCSAN 계측을 사용합니다.'),
        ('공통 __smp_store_mb(var,value)의 순서는?', '저장 후 내부 full 장벽이다', '장벽만 있고 저장은 없다', 'WRITE_ONCE(var,value); __smp_mb()입니다. release 저장의 장벽 앞·저장 뒤 순서와 구별해야 합니다.'),
        ('공통 조건부 acquire 읽기는 매 반복에 __smp_mb를 호출하는가?', '아니다. relaxed 대기 뒤 제어 의존성 후 장벽을 호출한다', '그렇다. 반복문 본문 첫 문장이 __smp_mb이다', 'relaxed 결과를 저장하고 smp_acquire__after_ctrl_dep를 호출합니다. 기본 후속 장벽은 smp_rmb이며 아키텍처가 재정의할 수 있습니다.'),
        ('VAL이9이고 조건 VAL>=7이 참이면 조건부 읽기의 반환값은?', '9이다', '조건식의 참을 뜻하는1이다', '종료 판단과 반환 데이터는 다릅니다. 마지막 관찰값 VAL을 원래 대상 타입으로 변환해 반환합니다.'),
        ('공통 io_stop_wc의 본문은?', '빈 do-while 문이다', '항상 모든 cache line을 flush한다', '인터페이스의 목적에 대한 주석과 실제 공통 기본 구현을 구별해야 합니다. 하드웨어 동작은 아키텍처 재정의 여부를 확인해야 합니다.'),
        ('pmem_wmb만으로 임의의 dirty cache line 전체를 영속화한다고 설명해도 되는가?', '안 된다. 앞선 영속화 동작과 순서 계약을 함께 봐야 한다', '된다. 공통 wmb가 모든 저장 장치를 fsync한다', '공통 매핑은 wmb이며 파일 동기화나 cache flush 순회를 구현하지 않습니다. 영속화 대상 수정과 앞선 명령이라는 계약의 전제가 중요합니다.'),
        ('비SMP의 smp_store_release 기본 본문에 타입 정적 검사 호출이 있는가?', '없다. barrier 뒤 WRITE_ONCE이다', '있다. 내부 __smp_store_release를 그대로 호출한다', '비SMP 공개 매크로는 별도 본문입니다. 내부 기본 매크로의 타입 검사까지 자동으로 물려받는다고 추측하지 말고 분기별 정의를 읽어야 합니다.')
    ]
)]
