"""Complete kref interface and out-of-line refcount helpers."""
ROWS = []


def add(path, title, intro, principle, use, sections, questions):
    ROWS.append(dict(path=path, title=title, intro=intro, principle=principle,
                     use=use, area='객체 수명 · 참조 계수 · 잠금 · 원자 연산',
                     sections=sections, questions=questions))


add('include/linux/kref.h', 'Kref 전체: 객체에 참조 수와 해제 콜백 연결하기',
    'refcount_t를 감싼 작은 객체 수명 관리 인터페이스입니다. 마지막 참조를 놓는 호출자가 release 콜백을 실행합니다.',
    '소유한 참조와 단순히 관측한 포인터를 구별하고, 마지막 감소와 객체 정리를 연결합니다. 잠금 결합 버전에서는 콜백의 잠금 해제 책임도 함께 설계해야 합니다.',
    'kref_get 전에 객체가 살아 있다는 보장이 필요합니다. get_unless_zero도 이미 해제된 메모리를 읽을 권한을 만들어주지는 않습니다.',
    [('전체 구성', 'GPL-2.0-only·저작권·guard, spinlock.h와 refcount.h 포함, kref 구조체, KREF_INIT, init/read/get/put/put_mutex/put_lock/get_unless_zero와 endif로 구성됩니다. 구조체에는 refcount_t 하나만 있고 객체 크기나 destructor 포인터는 저장하지 않습니다. release는 put 호출마다 인자로 받습니다.'),
     ('초기화와 관측', 'KREF_INIT(n)은 REFCOUNT_INIT(n)을 담는 구조체 초기화식입니다. kref_init은 refcount_set으로1을 저장합니다. kref_read는 refcount_read 결과를 반환할 뿐 참조를 획득하지 않습니다. 읽은 값이 양수여도 다른 CPU의 마지막 put을 막지 않으므로 read 다음 get을 별도 보호 없이 조합하면 안 됩니다.'),
     ('일반 획득', 'kref_get은 refcount_inc를 호출하고 반환값이 없습니다. 이미 유효한 소유권이나 적절한 외부 보호를 바탕으로 참조를 추가하는 용도입니다. 0에서 객체를 되살리는 초기화 함수로 사용하지 않습니다. 포화와 오류 경고 같은 세부 동작은 기반 refcount 구현에서 제공됩니다.'),
     ('일반 put과 콜백', 'kref_put은 refcount_dec_and_test가 참이면 release(kref)를 호출하고1, 아니면0을 반환합니다. 콜백은 필수이며 문서는 kfree를 직접 전달하면 안 된다고 명시합니다. 일반적인 콜백은 container_of로 포함 객체를 찾고 자원 정리 후 할당을 해제합니다. kref가 객체 시작 주소라는 보장도 없고 콜백 인자 형식도 따라야 합니다.'),
     ('반환값과 이후 접근', 'put 반환1은 이번 호출이 마지막 감소에 따라 release를 실행했다는 뜻입니다. 반환0도 객체가 이후 계속 존재한다는 증거가 아닙니다. 다른 소유자가 곧 마지막 참조를 놓을 수 있고 이번 호출자는 자신의 참조를 이미 반납했습니다. 콜백이 메모리 해제를 지연하도록 구현될 수 있으므로 반환1만으로 물리적 해제가 반드시 끝났다고 단정하지 않습니다.'),
     ('잠금 결합 put', 'put_mutex는 refcount_dec_and_mutex_lock, put_lock은 refcount_dec_and_lock 성공 시 release를 호출하고1을 반환합니다. 기반 함수는 성공 시 잠금을 보유한 채 돌아오며 kref wrapper에는 unlock이 없습니다. 따라서 콜백과 주변 정리 절차가 잠금 해제를 책임져야 합니다. 실패 경로의 기반 함수는 잡았던 잠금을 해제하고 돌아오거나 처음부터 잡지 않습니다.'),
     ('조건부 획득과 검색 구조', 'get_unless_zero는 refcount_inc_not_zero 결과를 int로 반환하고 __must_check를 붙입니다. 원문은 검색 구조에서 찾은 객체가 destructor에서 제거되는 경우를 설명합니다. 조회 중 메모리를 안정적으로 유지하고 이 반환값을 검사하면 put 쪽 잠금을 실제 제거 시점으로 미룰 수 있습니다. 0이면 객체 사용을 진행하지 않아야 하며 이 helper 자체가 RCU 읽기 구역을 열거나 목록을 잠그지는 않습니다.'),
     ('CS 연결', '임베디드 구조체와 container_of, 소유권 이전, 마지막 참조와 destructor, 원자적 조건부 획득, 관측과 예약의 차이, 잠금 소유권 계약을 학습합니다. 이 파일에 없는 객체별 destructor나 검색 구조의 안전성까지 자동 보장되는 것은 아닙니다.')],
    [('kref_put이0을 반환하면 직후 객체 필드를 읽어도 되는가?', '그 반환값만으로는 안 된다. 별도의 유효한 참조나 보호가 필요하다', '된다.0은 객체가 계속 살아 있음을 보장한다', '이번 호출은 참조를 반납했습니다. 다른 CPU가 마지막 참조를 놓을 수 있으므로 put의0은 이번 호출이 release를 실행하지 않았다는 사실만 알려줍니다.'),
     ('kref_put_lock의 마지막 참조 release는 어떤 잠금 상태로 실행되는가?', 'spinlock을 보유한 상태이며 wrapper에는 unlock이 없다', 'wrapper가 spinlock을 해제한 뒤 실행한다', 'refcount_dec_and_lock은 성공 시 잠금을 잡은 상태입니다. kref_put_lock은 곧바로 release를 호출하므로 콜백 측 정리 계약에 잠금 해제를 포함해야 합니다.'),
     ('kref_read가1이면 보호 없이 kref_get을 호출해도 되는가?', '아니다. 관측과 획득 사이에 마지막 put이 발생할 수 있다', '그렇다. read가 마지막 참조를 예약한다', 'read는 계수 조회일 뿐 참조 증가가 아닙니다. 객체 메모리 안정성과 획득 절차를 외부 동기화나 적절한 조건부 획득으로 보장해야 합니다.'),
     ('get_unless_zero가0을 반환했는데 포인터가 NULL이 아니라면 사용할 수 있는가?', '아니다. 참조 획득에 실패했으므로 그 결과를 처리해야 한다', '그렇다. 비NULL 포인터이면 획득 결과는 무시해도 된다', '이 함수의 __must_check와 주석은 반환값 검사를 요구합니다. 포인터가 검색되었다는 사실과 사용 가능한 참조를 획득했다는 사실은 다릅니다.')])

add('lib/refcount.c', 'Refcount 외부 구현 전체: 조건부 감소와 마지막 참조의 잠금',
    '포화 경고 처리와 조건부 감소, 마지막 감소를 mutex·spinlock과 결합하는 외부 함수들을 구현합니다.',
    '참조가 여러 개이면 잠금을 생략하고, 마지막 참조 후보일 때만 잠근 뒤 다시 감소 결과를 확인합니다. 참조 수의 산술 결과와 잠금 소유권을 함께 추적해야 합니다.',
    '포화 또는 잘못된0 감소에서 true가 실제 감소를 뜻하지 않는 함수가 있으므로 구현 분기를 확인합니다. 잠금 helper의 성공은 잠금 해제까지 완료했다는 뜻이 아닙니다.',
    [('전체 구성', 'GPL-2.0 표시, mutex/refcount/spinlock/bug 포함, REFCOUNT_WARN 매크로, 포화 경고 함수, dec_if_one, dec_not_one, mutex·spinlock·irqsave 결합 감소 함수가 있고 각각 EXPORT_SYMBOL로 내보냅니다. 기본 inc와 dec_and_test의 구현은 refcount.h에 있어 이 파일에서 새로 정의하지 않습니다.'),
     ('포화 경고의 공통 동작', 'refcount_warn_saturate는 사건 종류를 검사하기 전에 REFCOUNT_SATURATED를 저장합니다. ADD_NOT_ZERO_OVF와 ADD_OVF는 포화·누수, ADD_UAF는0에 더함, SUB_UAF는 감소 언더플로, DEC_LEAK는 일반 감소가0에 도달함을 경고하며 default도 알 수 없는 사건을 경고합니다. REFCOUNT_WARN은 WARN_ONCE에 공통 접두사와 줄바꿈을 붙입니다. 경고 종류를 기록하는 구조체나 메모리 해제 기능은 없습니다.'),
     ('1일 때만 감소', 'refcount_dec_if_one은 지역 val을1로 놓고 atomic_try_cmpxchg_release로1→0을 한 번 시도합니다. 성공 여부를 그대로 반환하며 반복하지 않습니다. 원문은 try-delete 같은 제한된 용도를 설명합니다. 임의 비교 교환 API를 노출하면 안전하지 않은 참조 연산을 만들 수 있어 이 특정 전환을 별도로 제공한다는 설계 의도가 있습니다.'),
     ('1이 아닐 때 감소', 'refcount_dec_not_one은 unsigned val을 읽고 루프를 돌며 먼저 정확히 SATURATED인지, 다음으로1인지 검사합니다. 포화이면 true를 반환하되 값을 바꾸지 않고,1이면 false입니다. 나머지는 new=val-1을 계산해 비교 교환 release로 저장합니다. 경쟁 변경으로 실패하면 atomic_try_cmpxchg가 갱신한 val을 바탕으로 분기부터 재평가합니다.'),
     ('0과 언더플로의 예외', 'val이0이면 unsigned new는 최댓값으로 순환하므로 new>val입니다. 경고 후 true를 반환하고 비교 교환을 하지 않습니다. 이 경로는 refcount_warn_saturate를 호출하지 않아 스스로 포화 값을 저장하지도 않습니다. 따라서 dec_not_one의 true를 모든 입력에서 실제 감소 성공이라고 해석하면 틀립니다. 정상 유효 참조 사용과 잘못된 입력에 대한 방어 동작을 구별합니다.'),
     ('mutex와 마지막 감소', 'dec_and_mutex_lock은 먼저 dec_not_one을 호출합니다. true이면 마지막 감소 후보가 아니므로 false를 반환합니다. false이면 관측상1이었으므로 mutex_lock 후 refcount_dec_and_test를 실행합니다.0에 도달하지 않았으면 mutex_unlock 후 false, 도달했으면 잠금을 보유한 채 true입니다. 마지막 후보 관측만으로 파괴하지 않고 잠금을 잡은 뒤 다시 결과를 확인합니다.'),
     ('잠금을 기다리는 사이의 경쟁', '처음1을 관측한 뒤 잠금을 잡기 전에 다른 적법한 참조 획득이 있으면 최종 감소가0이 아닐 수 있습니다. 이 경우 자신의 참조는 반납하되 마지막 소유자가 아니므로 잠금을 풀고 false입니다. 이 패턴을 적용하려면 객체의 조회·획득·제거가 동일한 수명 및 동기화 계약을 지켜야 합니다. 카운터 helper가 임의의 조회 구조를 자동으로 보호하지 않습니다.'),
     ('spinlock 결합', 'dec_and_lock은 mutex 버전과 같은 분기를 spin_lock/spin_unlock으로 구현합니다. 성공 시 호출자가 spinlock을 계속 보유하므로 정리와 unlock을 이어서 수행해야 합니다. mutex와 spinlock의 실행 문맥 제약은 서로 다르며 같은 제어 흐름이라고 아무 문맥에서나 바꾸어 쓸 수 있는 것은 아닙니다.'),
     ('IRQ 상태까지 전달', 'dec_and_lock_irqsave는 마지막 후보일 때 spin_lock_irqsave(lock,*flags)를 사용합니다. 최종 감소 실패는 spin_unlock_irqrestore로 복원하고 false, 성공은 잠금과 IRQ 차단 상태를 유지한 채 true입니다. 처음 dec_not_one이 true이면 flags를 쓰지도 않습니다. 따라서 false 반환 뒤 무조건 flags를 읽어 restore하는 호출 코드는 잘못입니다. 성공한 호출자가 저장 상태를 사용해 해제·복원합니다.'),
     ('메모리 순서와 책임', '조건부 비교 교환은 release이며 주석은 이전 읽기·쓰기와 이후 파괴 사이의 순서를 설명합니다. 마지막 감소의 세부 acquire 동작은 호출한 refcount_dec_and_test 구현도 함께 확인해야 합니다. 이 파일은 객체를 해제하지 않으며 true를 받은 호출자가 객체별 정리와 필요한 잠금 해제를 수행합니다.'),
     ('CS 연결과 비용', '비교 교환 루프의 재검사, unsigned 언더플로 탐지, 일반 경로의 잠금 회피, 마지막 참조의 직렬화, 성공 시 자원 소유권 전달을 학습합니다. 무경합 함수 본문의 짧은 길이가 최악의 경쟁 시간 상한을 뜻하지 않으며 이 수업의 원본 검사는 경쟁 실행을 전부 검증한 결과가 아닙니다.')],
    [('dec_not_one에 정확히 REFCOUNT_SATURATED가 들어오면?', '값을 유지하고 true를 반환한다', '1을 감소하고 false를 반환한다', '첫 검사에서 곧바로 true로 돌아갑니다. 이 결과를 받은 잠금 결합 helper는 false로 돌아가므로 마지막 참조 정리를 진행하지 않습니다.'),
     ('dec_not_one이0을 읽었을 때 스스로 포화 값으로 바꾸는가?', '아니다. 언더플로를 경고하고 저장 없이 true를 반환한다', '그렇다. 항상 refcount_warn_saturate를 호출한다', 'new=val-1의 unsigned 순환을 new>val로 검출합니다. 해당 분기는 WARN_ONCE 뒤 반환하며 포화 설정 함수나 비교 교환에 도달하지 않습니다.'),
     ('dec_and_mutex_lock의 true 반환 직후 mutex 상태는?', '호출자가 보유하고 있다', '함수에서 이미 해제했다', '잠금 뒤 최종 감소가0이 아닌 실패 경로만 mutex_unlock을 호출합니다. 성공 경로는 잠금을 유지해 호출자가 객체 제거를 직렬화할 수 있게 합니다.'),
     ('irqsave helper가 처음 dec_not_one에서 바로 false로 돌아오면 flags를 사용해 복원해야 하는가?', '아니다. 그 경로에서는 잠금을 잡거나 flags를 저장하지 않았다', '그렇다. 모든 false 반환에 IRQ 복원이 필요하다', '외부 함수의 첫 분기는 dec_not_one이 true일 때 즉시 false 반환입니다. IRQ를 건드리지 않은 경로이므로 초기화되지 않았을 수도 있는 flags를 읽어 복원하면 안 됩니다.'),
     ('dec_not_one의 비교 교환 실패 뒤 기존 val로 계속 계산하는가?', '아니다. 실패한 비교 교환이 갱신한 val로 상태 검사를 다시 한다', '그렇다. 처음 읽은 값은 루프 내내 고정이다', 'atomic_try_cmpxchg는 실패 시 기대값 인자에 현재 관측값을 돌려줍니다. 다음 반복에서 포화·1·언더플로 검사를 다시 해야 경쟁으로 바뀐 상태를 올바르게 처리할 수 있습니다.')])
