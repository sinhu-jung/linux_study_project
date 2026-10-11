"""Complete exported futex constants and ABI layouts."""
ROWS = [dict(
    path='include/uapi/linux/futex.h',
    title='Futex UAPI 전체: 명령·크기 인코딩·목록과 원자 연산 필드',
    intro='사용자 공간과 커널이 공유하는 futex 명령 번호, 플래그, 벡터 대기 및 robust 목록 레이아웃을 정의합니다.',
    principle='같은 정수라도 명령, 옵션 비트, 크기 필드, 소유자 상태는 서로 다른 인코딩입니다. 상수의 존재와 syscall의 실제 지원·검증을 구분해야 합니다.',
    use='실제 값을 대조하고 비트 패킹을 계산하는 수업입니다. 헤더는 전체 syscall 의미나 오류 처리 구현을 제공하지 않습니다.',
    area='시스템 호출 ABI · 비트 필드 · 구조체 정렬 · 원자 연산',
    sections=[
        ('전체 구성', 'GPL-2.0 WITH Linux-syscall-note와 guard, compiler/types 포함, 기존 futex 명령·옵션·PRIVATE 조합, futex2 크기와 플래그, waitv 구조체, robust 목록 구조체·상태·제한, bitset 상수, WAKE_OP 연산·비교·패킹 매크로가 전부입니다. syscall 구현 함수 본문은 없습니다.'),
        ('명령 번호 전체', 'WAIT0, WAKE1, FD2, REQUEUE3, CMP_REQUEUE4, WAKE_OP5, LOCK_PI6, UNLOCK_PI7, TRYLOCK_PI8, WAIT_BITSET9, WAKE_BITSET10, WAIT_REQUEUE_PI11, CMP_REQUEUE_PI12, LOCK_PI2는13입니다. 번호가 정의되어 있다고 모든 명령이 현재 모든 구성에서 정상 지원된다는 뜻은 아니며 실제 syscall dispatch와 검증을 확인해야 합니다.'),
        ('기존 옵션과 마스크', 'PRIVATE_FLAG128과 CLOCK_REALTIME256을 명령에 결합합니다. CMD_MASK는 두 비트의 OR를 반전한 값으로 명령을 분리하는 데 사용합니다. 이는 모든 알 수 없는 비트를 지우거나 지원 여부를 확인하는 유효성 검증 함수가 아닙니다. REALTIME 옵션이 모든 명령에서 허용된다고 이 상수만으로 결론 내리지 않습니다.'),
        ('PRIVATE 별칭', 'WAIT/WAKE, 두 REQUEUE, WAKE_OP, LOCK_PI/PI2, UNLOCK_PI, TRYLOCK_PI, 두 BITSET, WAIT_REQUEUE_PI/CMP_REQUEUE_PI의 PRIVATE 이름은 원래 명령과128을 OR합니다. 별도 알고리즘 번호를 연속해서 새로 매기는 것이 아닙니다. 예를 들어 WAIT_PRIVATE는128, WAKE_PRIVATE는129입니다.'),
        ('Futex2 크기는 선택 필드', 'SIZE_U8=0, U16=1, U32=2, U64=3이며 SIZE_MASK=3입니다. 하위2비트는 네 크기 중 하나를 선택하는 인코딩이므로 독립적인 크기 옵션처럼 OR하면 안 됩니다. NUMA=4, PRIVATE=128이고 중간 비트 일부는 주석으로 비워 둡니다. 정의가 있다는 사실만으로 각 크기의 실제 syscall 지원까지 증명되지 않습니다.'),
        ('과거 이름과 벡터 한계', 'FUTEX_32는 FUTEX2_SIZE_U32의 별칭이고 주석은 historical accident와 do not use를 표시합니다. FUTEX_WAITV_MAX는128로 벡터 대기 배열의 최대 원소 수를 나타냅니다. 이 제한은 아래 robust 목록 순회2048과 서로 다른 대상입니다.'),
        ('벡터 대기 ABI', 'futex_waitv는 __u64 val과 uaddr, __u32 flags와 __reserved를 순서대로 가집니다. val은 기대값, uaddr은 사용자 주소를 담는 정수 필드이며 reserved는 정렬 보존을 위한 예약 멤버로0이어야 합니다. 필드가64비트라는 이유만으로 그 주소가 가리키는 futex word도 반드시64비트라고 해석하지 않습니다.'),
        ('Robust 항목과 head', 'robust_list는 __user next 포인터 하나입니다. 사용자는 별도 역방향 링크를 둘 수 있어도 커널이 요구하는 것은 forward link입니다. robust_list_head는 list, long futex_offset, list_op_pending입니다. offset으로 항목과 futex 필드 사이의 위치를 전달하며 빈 head는 자기 자신으로 연결됩니다. syscall ABI이므로 필드 배치 변경은 일반 내부 구조체 변경과 다릅니다.'),
        ('Pending과 소유 확인', '주석은 pending 설정, 획득, 목록 연결, pending 해제의 순서로 중간 종료에 대응한다고 설명합니다. 아직 연결되지 않은 잠금을 찾을 수 있게 하되 실제 소유 TID도 확인합니다. 헤더 주석은 개요이고 현재 pending 특수 경로·PI 처리는 구현에서 따로 읽어야 합니다.'),
        ('Robust 상태와 제한', 'WAITERS0x80000000, OWNER_DIED0x40000000, TID_MASK0x3fffffff입니다. 두 상태 비트를 제외한 하위30비트가 TID입니다. ROBUST_LIST_LIMIT2048은 의도적인 순환 목록 등에 대한 순회 제한이며 예약한 잠금 객체 전체 수의 일반 메모리 할당 한도와 같지 않습니다.'),
        ('Bitset와 WAKE_OP 종류', 'BITSET_MATCH_ANY는0xffffffff로 모든 비트 일치를 허용하는 마스크입니다. WAKE_OP용 연산 SET0, ADD1, OR2, ANDN3, XOR4가 있고 ANDN은 인자의 보수를 AND하는 연산입니다. OPARG_SHIFT8은 인자 대신1<<OPARG를 쓰게 하는 연산 옵션이며 연산 종류와 함께 해석합니다.'),
        ('비교는 이전 값 기준', '비교 코드 EQ0, NE1, LT2, LE3, GT4, GE5가 있습니다. 설명은 UADDR2의 oldval을 얻어 원자적으로 갱신하고 oldval과 CMPARG 비교에 따라 UADDR2를 깨우는 조건을 나타냅니다. 갱신된 값과 비교한다고 읽으면 ADD 등의 조건 결과가 달라집니다. 이 주석은 syscall의 모든 깨우기 인자를 열거하는 완전한 실행 명세는 아닙니다.'),
        ('32비트 패킹', 'FUTEX_OP는 op 하위4비트를28부터, cmp 하위4비트를24부터, oparg 하위12비트를12부터, cmparg 하위12비트를0부터 배치합니다. 마스크로 초과 비트를 버리므로 인자 범위 오류를 자동 경고하지 않습니다. 예를 들어 ADD1,oparg3,EQ0,cmparg2는0x10003002입니다. 부호 확장과 허용 연산 검사는 해석하는 커널 구현의 역할입니다.'),
        ('CS 연결과 범위', '안정된 외부 ABI, 포인터 폭과 데이터 폭 분리, 예약 필드, enum 같은 크기 인코딩과 독립 플래그의 차이, 원자 read-modify-write의 old value 비교, 필드 패킹을 학습합니다. 상수 정의만으로 지원 하드웨어·syscall의 모든 동작을 검증했다고 주장하지 않습니다.')
    ],
    questions=[
        ('FUTEX2_SIZE_U16과 U32를 OR하면 두 크기를 동시에 요청하는가?', '아니다.1|2=3으로 U64 인코딩이 된다', '그렇다. 크기는 모두 독립 비트 플래그다', '크기는 하위2비트의 선택 필드입니다. 주석도 순수 플래그가 아니라고 설명하므로 OR 조합을 일반 옵션처럼 해석하면 안 됩니다.'),
        ('futex_waitv의 __reserved는 어떤 값이어야 하는가?', '0이다', '임의의 사용자 포인터를 넣는다', 'kernel-doc은 정렬 보존을 위한 예약 필드이며0이어야 한다고 명시합니다. 향후 ABI 확장을 위한 공간을 사용자 용도로 재해석하지 않습니다.'),
        ('FUTEX_WAITV_MAX와 ROBUST_LIST_LIMIT은 각각?', '128과2048이다', '둘 다 백만 개다', '벡터 대기 배열과 robust 목록 종료 순회는 서로 다른 대상입니다. 오래된 문서 수치를 현재 UAPI 상수와 혼동하지 않습니다.'),
        ('WAKE_OP의 CMP는 갱신 전후 중 어떤 값과 비교하는가?', '갱신 전 oldval이다', '갱신 후 값만 비교한다', '헤더의 의사 코드는 oldval을 저장하고 연산 후에도 oldval CMP CMPARG로 조건을 검사합니다. ADD나 XOR 후 값으로 비교하면 다른 의미가 됩니다.'),
        ('FUTEX_OP(ADD,3,EQ,2)의 패킹 값은?', '0x10003002이다', '0x13000002이다', 'op1은 bit28,cmp0은 bit24,oparg3은 bit12,cmparg2는 하위12비트에 놓입니다. 필드 위치를 직접 계산해야 합니다.'),
        ('명령 상수가 정의되어 있으면 현재 syscall 지원도 확정되는가?', '아니다. dispatch와 허용 플래그·설정 검증을 따로 봐야 한다', '그렇다. 헤더에 이름이 있으면 모든 구성에서 성공한다', 'UAPI 정의에는 호환성을 위해 남는 값과 실제 지원 범위가 다를 수 있습니다. 선언 존재와 실행 가능성은 서로 다른 근거를 요구합니다.')
    ]
)]
