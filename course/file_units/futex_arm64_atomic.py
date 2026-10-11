"""Whole ARM64 bounded exclusive-access futex helpers."""
ROWS = [dict(
    path='arch/arm64/include/asm/futex.h',
    title='ARM64 futex 전체: 배타적 접근 재시도와 경로별 장벽',
    intro='LDXR/STLXR를 이용한32비트 사용자 메모리 산술과 비교 교환을 구현하며 저장 실패 재시도에128회 한도를 둡니다.',
    principle='배타적 저장 실패와 비교 불일치, 사용자 접근 오류를 분리합니다. 같은 함수 안에서도 성공·실패 경로가 통과하는 장벽과 출력 갱신이 다릅니다.',
    use='아키텍처별 futex 계약을 비교하는 수업입니다. 실제 ARM64 커널 실행이나 fault 주입으로 검증한 결과는 아니며 명령·분기·출력 계약을 원문에 대응해 읽습니다.',
    area='ARM64 · 배타적 접근 · 재시도 한도 · 메모리 장벽 · fault',
    sections=[
        ('전체 구성', 'GPL-2.0-only·저작권·guard, futex/uaccess/errno 포함, FUTEX_MAX_LOOPS128, 산술 공통 asm 매크로, 산술 API, 비교 교환 API와 endif입니다. x86의 단일 xchg/xadd 구분 대신 다섯 산술 모두 같은 exclusive 루프를 사용합니다.'),
        ('사용자 주소 준비', '산술 함수는 __uaccess_mask_ptr로 마스킹한 포인터를 준비하고 원래 주소에 access_ok(sizeof(u32))를 검사합니다. cmpxchg는 access_ok 뒤 마스킹합니다. 둘 다 검사 실패면 -EFAULT입니다. 주소 범위 검사가 실제 메모리 접근 성공까지 보증하지 않아 asm의 fault 복구도 필요합니다.'),
        ('산술 루프', '__futex_atomic_op는 loops128을 두고 privileged user access를 활성화합니다. prfm은 저장용 캐시 프리페치 힌트, ldxr는 이전32비트 값을 읽고 전달받은 insn으로 후보를 계산합니다. stlxr는 release 배타적 저장을 시도하며 성공 상태0이면 위치3으로 나갑니다. 실패 상태를 loops에서 빼고 남으면 다시 ldxr부터 시도합니다.'),
        ('재시도 한도와 결과', '배타적 저장 실패가 한도를 소모하면 ret=-EAGAIN입니다. 이는 주소 오류가 아니라 이 시도에서 원자 갱신을 완료하지 못했다는 결과입니다.128이라는 횟수 한도가 정해진 마이크로초 지연을 보장하지는 않습니다. 정상 stlxr 성공은 ret0입니다.'),
        ('산술 장벽과 fault', '산술 매크로의 성공·재시도 소진은 위치3의 dmb ish를 지나고, ldxr/stlxr fault도 예외 테이블상 위치3으로 복귀하며 오류를 ret에 반영합니다. asm 끝에서 privileged user access를 비활성화합니다. 별도 memory clobber는 컴파일러에 메모리 효과를 알리며 CPU 장벽과 같은 층의 기능으로 혼동하지 않습니다.'),
        ('다섯 산술과 출력', 'SET은 mov, ADD는 add, OR는 orr, XOR는 eor이고 ANDN은 ~oparg를 전달한 and입니다. 지원하지 않는 op는 -ENOSYS이며 매크로를 실행하지 않습니다. 함수는 ret0일 때만 *oval=oldval로 이전 값을 전달합니다.32비트 %w 레지스터 연산이며 syscall의 packed 연산 해독이나 비교·깨우기 자체는 여기 없습니다.'),
        ('비교 교환의 비교', 'cmpxchg는 ret0과 loops128로 시작해 ldxr 값에서 oldval을 뺀 tmp가0인지 확인합니다. 불일치하면 위치4로 바로 나가 ret0과 관측값을 반환하므로 접근 성공이 실제 저장 성공과 같지 않습니다. 일치하는 경우만 newval을 stlxr로 저장합니다.'),
        ('비교 교환의 재시도', 'stlxr 실패는 loops를 소모하고 남으면 ldxr부터 재읽어 비교도 다시 합니다. 중간 경쟁으로 값이 달라졌다면 다음 시도에서 불일치로 끝날 수 있습니다. 한도 소진은 -EAGAIN, 정상 저장은0이며 두 경로는 위치3의 dmb ish를 통과합니다.'),
        ('비교 교환의 장벽 차이', 'cmpxchg의 비교 불일치는 위치4로 건너뛰어 dmb ish를 실행하지 않습니다. ldxr/stlxr fault의 예외 복귀점도 위치4입니다. 이는 산술 매크로의 위치3 fault 복귀와 다르므로 두 helper의 모든 반환 경로가 같은 장벽을 거친다고 설명하면 안 됩니다.'),
        ('출력과 접근 구간 종료', 'cmpxchg는 asm 뒤 privileged user access를 비활성화하고 ret0일 때만 *uval을 관측값으로 갱신합니다. fault나 EAGAIN에서 출력은 갱신하지 않습니다. 앞서 본 x86 cmpxchg가 asm fault 후에도 공통 출력 대입을 수행하는 것과 다르므로 공통 호출자는 오류일 때 출력에 의존하지 않는 계약을 유지해야 합니다.'),
        ('CS 연결', 'LL/SC 계열 원자성, compare 실패와 exclusive store 실패의 차이, 유한 재시도, acquire/release와 full barrier의 경로별 위치, 사용자 접근 범위와 실제 fault, 아키텍처 구현별 출력 차이를 학습합니다. 스핀 횟수 제한을 프로그램 전체의 실시간 보증으로 확대하지 않습니다.')
    ],
    questions=[
        ('배타적 저장 실패가128회 한도를 소모하면 반환은?', '-EAGAIN이다', '언제나 -EFAULT이다', 'FUTEX_MAX_LOOPS를 소모하면 asm에서 -EAGAIN을 ret에 넣습니다. 주소 접근 오류와 경합 등에 의한 원자 연산 미완료는 별개입니다.'),
        ('cmpxchg에서 기대값과 읽은 값이 다르면 dmb ish를 거치는가?', '아니다. 위치4로 건너뛴다', '그렇다. 모든 분기가 위치3부터 끝난다', '비교 뒤 cbnz는4f로 갑니다. 저장 성공·재시도 소진의3f 경로와 다르게 명시된 dmb를 통과하지 않습니다.'),
        ('산술 매크로와 cmpxchg의 fault 복귀 위치는 같은가?', '아니다. 산술은3, cmpxchg는4로 지정한다', '그렇다. 예외 테이블은 항상 첫 줄로 되돌린다', '예외 테이블의 레이블이 실제 실행되는 장벽을 바꿉니다. 산술은 dmb 전 위치3, cmpxchg는 dmb 뒤 위치4입니다.'),
        ('access_ok 성공이면 asm 접근의 EFAULT는 불가능한가?', '아니다. 실제 접근에 별도 fault 복구가 있다', '그렇다. 주소 검사가 메모리 페이지를 영구 고정한다', '두 접근 명령 위치에 예외 테이블을 둡니다. 범위 검사와 실제 메모리 접근 성공·수명은 다른 문제입니다.'),
        ('ret가 -EAGAIN이면 *oval 또는 *uval에 새 관측값이 반드시 저장되는가?', '아니다. 출력 갱신은 ret0일 때만 한다', '그렇다. 마지막 ldxr 값은 항상 출력된다', '두 공개 함수 모두 if (!ret) 조건에서만 출력을 대입합니다. 오류를 무시하고 이전 출력 변수를 사용하는 코드는 올바르지 않습니다.')
    ]
)]
