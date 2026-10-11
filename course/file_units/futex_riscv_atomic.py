"""Whole RISC-V futex architecture helper implementation."""
ROWS = [dict(
    path='arch/riscv/include/asm/futex.h',
    title='RISC-V futex 전체: AMO 산술과 LR/SC 비교 교환',
    intro='다섯 원자 산술은 AMO로, 비교 교환은 LR/SC 반복으로 처리하는 사용자 메모리 helper입니다.',
    principle='명령이 제공하는 원자성·순서와 사용자 접근 오류 처리를 함께 읽습니다. 산술 출력과 비교 교환 출력의 오류 경로 계약도 서로 다릅니다.',
    use='x86·ARM64·generic 구현과 비교하는 수업입니다. 이 파일의 코드 독해가 RISC-V 하드웨어에서의 실행 검증을 뜻하지는 않습니다.',
    area='RISC-V · AMO · LR/SC · 예외 복구 · 사용자 접근',
    sections=[
        ('전체 구성', 'GPL-2.0·저작권·guard, futex/uaccess/errno/asm/asm-extable 포함, 비MMU 접근 helper 대체, 공통 AMO 매크로, 산술 함수, cmpxchg 함수와 endif입니다. 파일에는 별도의 동적 할당이나 futex 대기 큐 처리가 없습니다.'),
        ('MMU별 접근 구간', 'CONFIG_MMU가 없으면 __enable_user_access와 __disable_user_access를 빈 do-while0 매크로로 정의합니다. MMU 구성에서의 실제 helper 정의는 포함된 접근 코드에서 옵니다. 빈 정의라고 예외 테이블이나 access_ok 코드까지 이 파일에서 제거하는 것은 아닙니다.'),
        ('공통 AMO 매크로', '__futex_atomic_op는 user access를 열고 지정한 한 명령을 실행한 뒤 닫습니다. ret는 입출력 레지스터, oldval은 early-clobber 출력, 사용자 메모리는 +m이며 memory clobber가 있습니다. 명령 위치1에서 fault가 나면 예외 테이블은 위치2로 복귀하고 ret에 오류를 반영합니다.'),
        ('입력 범위와 다섯 연산', '산술 함수는 access_ok(uaddr,sizeof(u32)) 실패 시 -EFAULT입니다. SET은 amoswap.w.aqrl, ADD는 amoadd, OR는 amoor, XOR는 amoxor이며 ANDN은 ~oparg를 인자로 전달한 amoand입니다. 모두32비트 word AMO이고 aqrl 표기를 사용합니다. 논리 연산도 x86처럼 CAS 루프를 작성하지 않고 직접 AMO로 이전 값을 얻습니다.'),
        ('산술 결과', 'ret0으로 시작하며 미지원 op는 -ENOSYS입니다. 명령 오류가 없을 때만 *oval=oldval을 기록합니다. 이 helper는 packed FUTEX_OP를 해독하거나 비교 조건에 따라 깨우지 않고 지정된 연산과 이전 값 반환만 담당합니다.'),
        ('LR/SC 비교 교환', 'cmpxchg는 access_ok 후 user access를 열고 lr.w.aqrl로 val을 읽습니다. 기대 oldval과 다르면 위치3으로 끝나고 같으면 sc.w.aqrl로 newval을 저장합니다. sc 상태가0이 아니면 위치1로 돌아가 다시 읽고 비교합니다. 이 파일에는 ARM64의128회 같은 명시적 재시도 카운터가 없습니다.'),
        ('정상 비교 실패와 접근 실패', '비교가 달라 종료되어도 ret0이고 val이 관측값입니다. 실제 교체 성공은 관측값과 기대값의 일치로 판단해야 합니다. lr과 sc 각각의 예외 테이블은 위치3으로 보내며 오류 ret를 전달합니다. 실패한 sc의 재시도와 사용자 메모리 fault는 다른 경로입니다.'),
        ('출력 대입의 주의', 'cmpxchg는 접근 구간을 닫은 뒤 ret 검사 없이 *uval=val을 대입합니다. 초기 access_ok 실패는 그 대입 전에 돌아가지만 asm fault는 공통 대입을 거칩니다. 따라서 오류 반환에서 uval이 유효한 관측값이거나 이전 값을 보존한다고 기대하면 안 됩니다. 산술 함수의 if(!ret) 출력과 차이가 있습니다.'),
        ('순서와 표현', 'AMO 및 LR/SC 문자열은 .w와 .aqrl을 명시합니다. 명령의 메모리 순서, C asm의 memory clobber, 사용자 접근 허용, 예외 복구는 각각의 역할이 있으므로 한 기능으로 묶어 설명하지 않습니다. 저장 시도 상태를 담는 tmp는 uintptr_t이고 실제 futex 데이터는 u32라 주소 폭과 데이터 폭을 구분합니다.'),
        ('CS 연결과 범위', '직접 AMO와 합성 CAS, exclusive store 재시도, 이전 값 반환, 사용자 접근 실패의 출력 계약, 아키텍처별 fallback과 MMU 조건을 학습합니다. 재시도 한도가 본문에 없다는 사실은 시스템 전체의 무한 대기 또는 진행 보장을 단독으로 증명하지 않습니다.')
    ],
    questions=[
        ('RISC-V OR 원자 연산도 x86처럼 CAS 루프를 사용하는가?', '아니다. amoor.w.aqrl을 사용한다', '그렇다. 모든 아키텍처의 논리 연산은 같은 CAS 루프다', '이 구현은 다섯 산술을 각각 AMO 명령에 대응합니다. 공통 API라도 ISA가 제공하는 원자 명령에 따라 본문이 달라집니다.'),
        ('sc.w가 실패하면 다음 단계는?', 'lr.w부터 다시 읽고 기대값 비교를 반복한다', '기대값을 무시하고 일반 저장으로 덮어쓴다', 'bnez tmp,1b가 재시도 경로입니다. 그 사이 값이 바뀌면 다음 비교가 불일치로 끝날 수도 있습니다.'),
        ('이 LR/SC 루프에128회 제한이 있는가?', '없다. 본문에 명시적 반복 카운터가 없다', '있다. ARM64와 같은 FUTEX_MAX_LOOPS를 사용한다', '원문에는 FUTEX_MAX_LOOPS나 감소 카운터가 없습니다. 다른 아키텍처에서 본 제한을 그대로 옮기면 안 됩니다.'),
        ('cmpxchg asm fault 때 uval은 반드시 원래 값을 유지하는가?', '아니다. 오류 여부와 무관한 공통 대입이 있다', '그렇다. 모든 출력은 if(!ret)로 보호된다', 'if(!ret)는 산술 함수에 있고 cmpxchg는 접근 종료 뒤 *uval=val을 수행합니다. 오류 반환일 때 관측값에 의존하지 않아야 합니다.'),
        ('CONFIG_MMU가 없으면 무엇이 빈 매크로가 되는가?', '사용자 접근 enable/disable helper이다', 'futex 함수 전체가 사라진다', '조건부 정의는 두 접근 helper에 한정됩니다. 나머지 AMO·LR/SC·예외 테이블·함수 본문은 계속 존재합니다.')
    ]
)]
