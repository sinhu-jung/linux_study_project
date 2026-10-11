"""Whole x86 futex inline assembly implementation."""
ROWS = [dict(
    path='arch/x86/include/asm/futex.h',
    title='X86 futex 원자 접근 전체: 명령별 이전 값과 fault 복구',
    intro='x86 명령과 예외 테이블을 이용해 사용자 공간32비트 futex의 원자 산술 및 비교 교환을 수행합니다.',
    principle='SET·ADD는 이전 값을 반환하는 단일 명령, 논리 연산은 비교 교환 루프로 구현합니다. 사용자 접근 오류와 비교 불일치는 서로 다른 결과입니다.',
    use='inline assembly의 입력·출력 제약, 예외 경로와 사용자 접근 구간을 함께 읽습니다. 이 수업은 소스 독해이며 실제 fault 주입이나 x86 커널 실행 시험은 아닙니다.',
    area='x86 어셈블리 · 원자 RMW · 예외 테이블 · 사용자 메모리',
    sections=[
        ('전체 구성', 'GPL-2.0·guard와 __KERNEL__ 조건, futex/uaccess 및 asm/errno/processor/smap 포함, unsafe_atomic_op1/op2 매크로, arch_futex_atomic_op_inuser, futex_atomic_cmpxchg_inatomic과 endif로 구성됩니다. 사용자 공간 프로그램에 직접 노출할 실행 helper가 아니라 커널 내부 아키텍처 구현입니다.'),
        ('단일 명령 helper', 'unsafe_atomic_op1은 oldval 레지스터를 oparg 입력과 묶고 ret를0으로 초기화한 asm을 실행합니다. 지정 메모리는 +m으로 읽기·쓰기를 표시합니다. 명령 위치1에서 fault가 나면 예외 테이블이 위치2로 보내며 ret 레지스터에 EFAULT 오류를 반영하는 타입을 지정합니다. ret가 있으면 인자의 label로 이동하고 아니면 *oval에 이전 값을 씁니다.'),
        ('비교 교환 루프 helper', 'unsafe_atomic_op2는 사용자 값을 accumulator oldval에 읽고 복사한 tem에 논리 연산을 적용한 뒤 LOCK cmpxchgl로 저장을 시도합니다. 실패하면 cmpxchg가 갱신한 oldval을 바탕으로 위치2에서 후보를 다시 계산합니다. 처음 mov 위치와 cmpxchg 위치에 각각 fault 복구 항목을 둡니다. 성공했을 때의 이전 값을 반환하므로 첫 읽기가 항상 최종 oldval인 것은 아닙니다.'),
        ('레지스터 제약의 역할', 'op2의 oldval은 accumulator 제약, oldval/ret/tem은 early-clobber 출력 제약을 사용합니다. 입력 oparg가 아직 필요한 동안 출력이 덮어써 버리는 잘못된 레지스터 공유를 피하기 위한 계약으로 읽습니다. 어셈블리 문자열만 보고 C 컴파일러와의 입력·출력 약속을 생략하면 정확한 동작을 설명하기 어렵습니다.'),
        ('접근 구간과 연산 선택', 'arch_futex_atomic_op_inuser는 user_access_begin으로 uaddr의 u32 접근 구간을 열고 실패하면 즉시 -EFAULT입니다. SET은 메모리 xchgl, ADD는 LOCK xaddl을 op1로 실행합니다. OR/XOR는 op2, ANDN은 ~oparg를 전달한 andl의 op2입니다. SET의 메모리 xchg가 명시 LOCK_PREFIX 없이도 원자 교환인 x86 명령 의미와 ADD의 prefix를 구분합니다.'),
        ('산술 오류와 닫기', '미지원 op는 user_access_end 후 -ENOSYS입니다. 정상은 end 후0, asm fault의 Efault label도 end 후 -EFAULT입니다. 매크로는 fault일 때 *oval을 쓰기 전에 이동하므로 산술 helper 오류에서 출력이 유효하다고 가정하지 않습니다. begin이 실패한 경우에는 열리지 않은 구간을 다시 닫지 않습니다.'),
        ('단일 cmpxchg', 'futex_atomic_cmpxchg_inatomic은 ret0, 접근 begin, LOCK cmpxchgl 한 번, 접근 end, *uval=oldval, ret 반환 순서입니다. oldval 입력을 accumulator 출력에 묶고 newval은 다른 레지스터 인자로 전달합니다. 비교가 다르면 현재 관측값이 accumulator에 남고 저장은 하지 않지만 ret는 접근 오류가 없으면0입니다.'),
        ('출력과 오류 경로 차이', 'cmpxchg의 begin 실패는 즉시 돌아가 *uval을 쓰지 않습니다. 그러나 asm 위치에서 fault가 나면 ret가 오류인 채 공통 경로를 거쳐 *uval 대입까지 수행합니다. 산술 helper처럼 모든 오류에서 출력이 그대로 보존된다는 설명은 틀립니다. 오류 반환일 때 그 출력에 성공 관측값 의미를 부여하지 않습니다.'),
        ('컴파일러·CPU·접근 보호', 'cmpxchg asm에는 memory clobber도 명시되어 있습니다. LOCK 명령의 CPU 원자성, asm 제약이 컴파일러에 전달하는 효과, user_access_begin/end의 접근 문맥, fault 복구 테이블은 각기 다른 책임입니다. generic UP의 preempt_disable 기반 read/write와 같은 구현으로 설명하지 않습니다.'),
        ('CS 연결과 범위', '원자 교환·fetch-add·CAS 재시도, 기대값의 실패 갱신, 재계산 루프, 예외 fixup, 출력 인자 유효성, 아키텍처와 컴파일러 계약을 학습합니다. 헤더에 없는 syscall 연산 해독·대기자 깨우기·페이지 fault 전체 정책까지 검증한 것으로 세지 않습니다.')
    ],
    questions=[
        ('논리 OR 구현에서 cmpxchg 실패 후 왜 연산 후보를 다시 계산하는가?', '현재 메모리 관측값이 oldval로 갱신되었기 때문이다', '실패해도 oldval은 첫 읽기값으로 영원히 고정되기 때문이다', 'cmpxchg 실패는 accumulator에 현재값을 돌려줍니다. 위치2에서 그 값을 tem에 복사해 새 OR 결과를 만들고 다시 시도합니다.'),
        ('ANDN은 어떤 입력으로 andl을 실행하는가?', 'oparg의 비트 보수를 전달한다', '원래 oparg를 그대로 전달해 일반 AND를 한다', '호출은 unsafe_atomic_op2의 인자로 ~oparg를 줍니다. 명령 이름만 보면 AND지만 인자 변환으로 AND-not 의미를 만듭니다.'),
        ('단일 cmpxchg의 반환0은 반드시 newval 저장을 뜻하는가?', '아니다. 관측값과 기대값을 비교해야 한다', '그렇다. 비교 불일치는 항상 -EFAULT이다', 'ret는 접근 오류를 나타냅니다. 비교 불일치도 ret0일 수 있고 *uval로 반환한 관측값을 사용해 실제 교환 여부를 판단해야 합니다.'),
        ('단일 cmpxchg에서 asm fault가 나면 *uval은 반드시 보존되는가?', '아니다. 공통 경로의 대입이 실행되므로 오류 시 출력에 의존하지 않는다', '그렇다. 모든 오류가 대입 전에 즉시 반환한다', 'begin 실패와 asm fault 경로가 다릅니다. asm 뒤에는 end와 *uval 대입이 있고 마지막에 ret를 반환합니다.'),
        ('SET과 ADD의 이전 값 획득은 모두 CAS 루프인가?', '아니다. 각각 xchg와 xadd 단일 명령 helper를 사용한다', '그렇다. 다섯 연산 모두 동일한 CAS 반복이다', 'op1은 SET·ADD, op2는 OR·ANDN·XOR입니다. 명령이 직접 이전 값을 돌려주는지에 따라 구현이 달라집니다.')
    ]
)]
