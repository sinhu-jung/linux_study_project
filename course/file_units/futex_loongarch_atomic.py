"""Whole LoongArch futex architecture helpers."""
ROWS = [dict(
    path='arch/loongarch/include/asm/futex.h',
    title='LoongArch futex 전체: LL/SC 상태값과 페이지 fault 제어',
    intro='LL/SC 반복을 통해 사용자 futex의 산술과 비교 교환을 수행하는 LoongArch 구현입니다.',
    principle='조건부 저장의 상태값 해석은 ISA마다 다릅니다. LoongArch의 sc.w 결과0은 재시도이며, 주소 검사·페이지 fault 제어·출력 대입은 함수별로 따로 확인해야 합니다.',
    use='앞서 본 RISC-V·ARM64와 분기 방향을 비교합니다. 다른 아키텍처의 오류 경로나 장벽을 그대로 복사해 설명하지 않습니다.',
    area='LoongArch · LL/SC · fault 제어 · 예외 테이블 · 장벽',
    sections=[
        ('전체 구성', 'GPL-2.0·저작권·guard, futex/uaccess/asm-extable/barrier/errno 포함, 공통 산술 asm 매크로, 산술 API, 비교 교환 API와 endif입니다. futex 대기 큐나 packed op 해독 구현은 없습니다.'),
        ('산술의 LL/SC', '매크로는 ll.w로 oldval을 읽고 지정 insn으로 $t0에 후보를 만든 뒤 sc.w로 저장을 시도합니다. sc.w가 $t0에 돌려준 상태가0이면 beqz로 처음부터 반복합니다. RISC-V sc의 비0 재시도와 분기 방향이 다릅니다. 명시적인 반복 횟수 제한은 없습니다.'),
        ('asm 제약과 오류', 'ret는 입력0과 연결된 출력, oldval은 early-clobber이며 uaddr는 ZC 메모리 제약의 읽기·쓰기 인자로 연결됩니다. memory와 t0를 clobber로 알립니다. ll.w와 sc.w에 각각 예외 테이블을 두고 fault 시 위치3으로 돌아가 ret에 오류를 반영합니다. C 출력 변수 초기값만으로 fault 이후 유효 데이터를 보증하지 않습니다.'),
        ('다섯 산술 선택', 'SET은 move, ADD는 add.w, OR는 or, XOR는 xor입니다. ANDN은 ~oparg를 넘겨 and로 구현합니다. 모두 동일 LL/SC 반복을 사용하며 성공하면 이전 값을 전달합니다. 미지원 op는 -ENOSYS이고 원자 명령을 실행하지 않습니다.'),
        ('산술의 페이지 fault 제어', 'arch_futex_atomic_op_inuser는 switch 전에 pagefault_disable, 뒤에 pagefault_enable을 호출합니다. 이 함수 본문에는 별도 access_ok 검사가 없습니다. 이것을 임의 사용자 주소 접근이 항상 안전하다는 뜻으로 해석하지 않고 호출 측 검증과 uaccess 예외 계약도 확인해야 합니다. pagefault_disable은 모든 메모리 접근이 반드시 성공한다는 보증이 아닙니다.'),
        ('산술 출력', '페이지 fault 제어 구간을 닫은 뒤 ret0인 경우에만 *oval=oldval을 기록합니다. -ENOSYS와 접근 오류에서는 새 출력을 쓰지 않습니다. compare·wake 단계가 이 산술 helper 안에서 함께 수행되는 것은 아닙니다.'),
        ('비교 교환', 'cmpxchg는 먼저 access_ok(sizeof(u32))를 검사하고 실패면 -EFAULT입니다. ll.w로 읽은 val이 기대 oldval과 다르면 위치3으로 끝납니다. 같으면 newval을 t0에 옮겨 sc.w, 저장 실패0이면 다시 ll.w부터 비교까지 반복합니다. 접근 성공 ret0과 실제 값 교체 여부를 관측값으로 나누어 판단해야 합니다.'),
        ('공통 종료 장벽', 'cmpxchg의 정상 저장·비교 불일치·fault 복귀는 모두 위치3 뒤 __WEAK_LLSC_MB를 지나도록 작성되어 있습니다. 같은 트리의 barrier.h에서 이 매크로는 CONFIG_SMP일 때 dbar0x700 문자열이고 아니면 빈 줄입니다. 산술 매크로에는 이 명시적 종료 매크로가 없으므로 두 본문이 동일하다고 설명하지 않습니다.'),
        ('접근·출력 계약 차이', 'cmpxchg 함수 자체에는 pagefault_disable/enable 호출이 없고, asm 종료 뒤 ret와 무관하게 *uval=val을 기록합니다. 초기 access_ok 실패만 이 대입 전에 돌아갑니다. 산술 helper의 조건부 출력과 차이가 있어 오류 반환에서 관측값 유효성이나 보존을 가정하면 안 됩니다. 외부 호출 문맥의 fault 제어는 별도입니다.'),
        ('CS 연결과 검증 범위', 'ISA별 조건부 저장 성공값, LL/SC 후보 재계산, 예외 복귀와 장벽 위치, 페이지 fault 제어와 주소 검사의 구분, 출력 계약을 학습합니다. 코드를 대조한 수업이며 실제 LoongArch 하드웨어에서 실행하거나 오류를 주입한 검증은 아닙니다.')
    ],
    questions=[
        ('이 구현의 sc.w 결과가0이면?', '저장 실패로 ll.w부터 재시도한다', '저장 성공으로 즉시 반환한다', '원문은 beqz $t0,1b입니다. RISC-V sc의 실패 판정 방향과 반대이므로 다른 ISA에서 본 규칙을 기계적으로 적용하면 안 됩니다.'),
        ('산술 helper와 cmpxchg 모두 내부에서 pagefault_disable을 호출하는가?', '아니다. 이 파일에서는 산술 helper에만 그 쌍이 있다', '그렇다. 함수 이름에 inatomic이면 자동 호출된다', 'cmpxchg 본문은 access_ok와 asm·출력 대입이며 pagefault 제어 쌍은 없습니다. 호출자의 외부 보호와 내부 본문을 구분합니다.'),
        ('비교 불일치도 cmpxchg의 __WEAK_LLSC_MB 지점을 통과하는가?', '그렇다. 분기가 위치3으로 간다', '아니다. 모든 비교 불일치가 장벽 뒤로 건너뛴다', 'bne의 목적지는3f이고 그 다음에 장벽 매크로가 있습니다. ARM64에서 본 다른 레이블 구조와 구분해야 합니다.'),
        ('cmpxchg 오류에서 uval은 항상 보존되는가?', '아니다. asm fault 후 공통 대입이 실행된다', '그렇다. if(!ret) 조건이 모든 출력을 감싼다', 'if(!ret)는 산술 helper 출력에 있습니다. cmpxchg는 ret 검사 없이 *uval=val이므로 오류에서 그 값을 성공 관측값으로 사용하면 안 됩니다.')
    ]
)]
