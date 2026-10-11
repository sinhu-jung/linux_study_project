"""Whole LoongArch barrier and nospec mask header."""
ROWS = [dict(
    path='arch/loongarch/include/asm/barrier.h',
    title='LoongArch 장벽 전체: DBAR 힌트와 크기별 저장 순서',
    intro='완료·순서 장벽, acquire/release, 저장 후 장벽과 투기 인덱스 마스크를 정의합니다.',
    principle='장벽의 앞뒤 접근 종류를 비트로 표현하고 필요한 순서만 선택합니다. 컴파일러 장벽, CPU 장벽, 안전한 인덱스 마스크는 서로 다른 기능입니다.',
    use='앞서 futex에서 본 dbar0x700을 일반 full barrier와 구분해 읽습니다. 실제 LoongArch 실행 시험이 아닌 원본 기반 해설입니다.',
    area='메모리 모델 · DBAR · acquire/release · 비트 마스크 · 원자 저장',
    sections=[
        ('전체 구성', 'GPL-2.0·저작권·guard, 힌트 인코딩 주석, DBAR와 여덟 상수, completion/ordering alias, SMP·LLSC·atomic 주변 장벽, nospec mask, acquire/release/store_mb와 generic barrier 포함으로 끝납니다. 뒤의 generic 헤더가 제공하는 전체 API를 이 파일 하나의 구현으로 세지 않습니다.'),
        ('힌트 비트', 'bit4는0이면 completion,1이면 ordering입니다. bit3/2는 앞선 read/write, bit1/0은 뒤따르는 read/write에 대한 적용 여부이며0이 참,1이 제외입니다. 일반적인 enable bit와 반대라 비트를 세우면 더 많은 접근을 막는다고 단순 추측하면 틀립니다.'),
        ('상수와 DBAR', 'crwrw=00000, cr_r_=00101, c_w_w=01010이며 ordering 대응은10000,10101,11010입니다. acquire용 or_rw는10100, release용 orw_w는10010입니다. DBAR는 즉시값 I 제약의 dbar와 memory clobber를 사용해 CPU 명령과 컴파일러 순서 계약을 연결합니다.'),
        ('공개 별칭의 차이', 'mb/rmb/wmb는 c_sync/c_rsync/c_wsync의 completion 계열이고 iob/wbflush도 c_sync입니다. __smp_mb/rmb/wmb는 o_sync/o_rsync/o_wsync ordering 계열입니다. 이 이름들을 모두 같은 비트패턴의 장벽으로 설명하지 않습니다.'),
        ('LLSC 전용 힌트', '__WEAK_LLSC_MB는 SMP에서 dbar0x700 문자열, 비SMP에서는 빈 줄입니다. 주석은0x700을 같은 주소의 read-after-read 장벽으로 설명합니다. futex의 이 매크로를 모든 앞뒤 읽기·쓰기의 일반 full barrier로 과장하지 않습니다.'),
        ('원자 연산 주변', '__smp_mb__before_atomic과 after_atomic은 barrier()로 정의됩니다. 본문상 컴파일러 장벽이며 여기서 추가 DBAR를 발행하지 않습니다. 이것만 보고 원자 연산 자체의 하드웨어 순서가 없다고 결론 내리지 않고 관련 원자 구현과 함께 판단해야 합니다.'),
        ('인덱스 마스크', 'array_index_mask_nospec는 unsigned sltu로 index<size의0/1을 만들고 long이4바이트면 sub.w,8바이트면 sub.d로0에서 빼 마스크를 만듭니다. 조건 참이면 모든 비트1,거짓이면0입니다. 이 함수는 배열을 읽거나 예외를 발생시키는 것이 아니라 호출자가 인덱스와 결합할 마스크를 반환합니다.'),
        ('Acquire와 release 위치', '__smp_load_acquire는 READ_ONCE로 값을 읽고 atomic type 정적 검사와 ldacq_mb 뒤 저장해 둔 값을 반환합니다. __smp_store_release는 타입 검사, strel_mb, WRITE_ONCE 순서입니다. acquire 장벽은 읽기 뒤, release 장벽은 쓰기 앞이라는 위치가 각 방향의 순서 요구와 연결됩니다.'),
        ('Store_mb 입력 표현', '__smp_store_mb의 p는 저장 대상 lvalue입니다. typeof(p) 값을 union에 담고 char 표현을 통해 크기별 값을 얻습니다. switch(sizeof(p))를 사용하므로 p를 포인터 인자라고 오인하면 안 됩니다. 여기서는 전달값을 대상 타입으로 변환해 한 번 저장할 준비를 합니다.'),
        ('크기별 저장 경로', '1·2바이트는 volatile 정수 저장 뒤 __smp_mb입니다.4·8바이트는 각각 amswap_db.w/d로 교환하고 이전 값은 tmp에 받아 버립니다. 매크로에는 그 밖의 크기에 대한 default 저장이나 런타임 오류 분기가 없으므로 임의 크기 구조체를 지원한다고 주장하면 안 됩니다.'),
        ('CS 연결과 범위', '비트 인코딩의 역논리, completion과 ordering, acquire/release 방향성, branchless mask, 타입 폭별 구현 선택, compiler와 CPU 계약을 학습합니다. 이 코드만으로 모든 장치 메모리나 투기 공격 시나리오에 대한 안전성을 증명한 것은 아닙니다.')
    ],
    questions=[
        ('힌트의 앞선 read 적용 bit3이0이면?', '그 read에 장벽을 적용한다', '그 read를 제외한다', '주석은0:true,1:false라고 명시합니다. bit4의 종류 선택과 나머지 접근 제외 비트의 의미를 구분해야 합니다.'),
        ('index가 size와 같으면 nospec mask는?', '0이다', '모든 비트1이다', 'sltu는 엄격한 unsigned less-than입니다. 같을 때0이고0에서0을 빼므로0 마스크입니다.'),
        ('__smp_load_acquire의 ldacq_mb는 읽기 전후 중 어디인가?', 'READ_ONCE 뒤이다', 'READ_ONCE 전에만 있다', '읽은 값을 지역 변수에 담고 타입 검사·장벽을 수행한 후 반환합니다. release 저장은 반대로 장벽을 저장 전에 둡니다.'),
        ('1바이트 store_mb도 amswap_db.d를 쓰는가?', '아니다. volatile1바이트 저장 뒤 SMP 장벽이다', '그렇다. 모든 크기를8바이트 교환으로 바꾼다', 'switch에서1·2는 저장+장벽,4·8은 대응 폭 amswap_db 명령입니다. 인접 바이트까지 교환하는 일반화는 원문과 다릅니다.'),
        ('dbar0x700은 이 문서 주석상 무엇을 위한가?', '같은 주소의 read-after-read 순서이다', '모든 I/O를 영구히 중단하는 명령이다', 'LLSC 전용 힌트 설명을 일반 c_sync나 o_sync의 전체 의미와 혼동하지 않아야 합니다.')
    ]
)]
