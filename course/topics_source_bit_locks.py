"""Whole bit spinlock/generic lock/instrumentation headers and selected model evidence."""
ROWS = [('Bit spinlock·한 word 안 bit로 표현하는 잠금',
  'include/linux/bit_spinlock.h',
  'bit_spin_lock',
  'bit spinlock은 unsigned long 안의 특정 bit를 잠금 상태로 사용합니다. CONFIG_SMP 또는 DEBUG_SPINLOCK에서 '
  'test_and_set_bit_lock의 이전 bit가0이면 획득하고1이면 기다립니다. 먼저 preempt_disable을 호출하며 획득 뒤에도 비활성 깊이가 유지됩니다. 원문은 '
  '정말 필요한 경우에만 사용하고 일반 spin_lock/unlock이 훨씬 빠르다고 안내합니다.',
  '자료 표현상 하나의 bit에 잠금이 꼭 필요한 경우에만 검토합니다. 유효한 bit와 정렬된 살아 있는 word를 준비하고 같은 객체의 모든 사용자가 같은 잠금 계약을 지키도록 '
  '합니다. 잠금 보유 중 잠드는 호출을 넣지 않습니다.',
  [('이전bit0의 test-and-set은 어떤 결과인가?',
    '새롭게 잠금을 획득한다',
    '이미 다른 사용자가 보유했다는 뜻이다',
    '기존0을1로 바꾸는 성공입니다. 이전 상태의 반환과 새 메모리 상태를 구분합니다.'),
   ('원문은 일반 spin_lock보다 bit lock을 항상 권장하는가?',
    '아니며 꼭 필요할 때만 쓰라고 한다',
    '모든 잠금을 bit lock으로 바꾸라고 한다',
    '원문은 일반 spin_lock과 unlock이 훨씬 빠르다고 명시합니다. 작은 표현 크기를 무조건 성능 우위로 해석하지 않습니다.')],
  [('실제 원문 조건', '여기서 preempt 모델은 thread별 깊이 카운터입니다. 실제 scheduler가 실행된 것은 아닙니다.'),
   ('실행 검사 경계',
    '원본 세 헤더를 명시적인 사용자공간 atomic·preempt·instrumentation 모델과 함께 검사했습니다. 실제 kernel preemption, KCSAN 탐지, '
    'LKMM 또는 모든 architecture의 실행을 증명한 검사는 아닙니다.')]),
 ('Bit lock 경쟁 대기·atomic 시도와 읽기 loop 분리',
  'include/linux/bit_spinlock.h',
  'bit_spin_lock',
  'atomic 획득에 실패하면 preempt_enable로 대기 중 선점 가능성을 되돌립니다. 안쪽 do-while은 cpu_relax 뒤 test_bit 읽기로 bit가 풀릴 '
  '때까지 기다립니다. 그 뒤 다시 preempt_disable하고 atomic 획득을 재시도합니다. 조회가0이어도 다른 CPU가 먼저 획득할 수 있어 조회만으로 성공을 선언하지 '
  '않습니다. 계속 atomic RMW하는 bus 경쟁을 줄이는 구조입니다.',
  '외부 atomic 재시도와 내부 조회 대기를 두 단계로 그립니다. 대기 중의 preempt 변화와 성공 뒤 깊이를 추적합니다. cpu_relax를 잠금 해제나 payload 공개 '
  'barrier로 설명하지 않습니다.',
  [('안쪽 test_bit가0을 보면 바로 잠금 소유자가 되는가?',
    '아니며 atomic 획득을 다시 시도한다',
    '조회 자체가 소유권을 준다',
    '조회와 atomic 변경 사이에 다른 CPU가 들어올 수 있습니다. 바깥 loop의 재시도가 필요합니다.'),
   ('경쟁 대기의 내부에서 계속 atomic RMW만 수행하는가?',
    '아니며 읽기와 cpu_relax로 기다린다',
    '매번 새 word전체를 atomic 저장한다',
    '원문은 덜 비싼 조회로 해제 가능성을 기다리고 나서 획득을 재시도합니다.')],
  [('실제 원문 조건', '네 thread가 선택된 atomic 모델로10만 회 보호 카운터를 갱신했습니다. 실제 hardware의 bus 트래픽 측정은 아닙니다.'),
   ('실행 검사 경계',
    '원본 세 헤더를 명시적인 사용자공간 atomic·preempt·instrumentation 모델과 함께 검사했습니다. 실제 kernel preemption, KCSAN 탐지, '
    'LKMM 또는 모든 architecture의 실행을 증명한 검사는 아닙니다.')]),
 ('Bit trylock·실패에서 preempt 깊이 복구',
  'include/linux/bit_spinlock.h',
  'bit_spin_trylock',
  'trylock은 먼저 preempt_disable합니다. SMP 또는 DEBUG 경로에서 이전 bit가1이면 preempt_enable하고0을 반환합니다. 성공이면 '
  '__acquire annotation 후1을 반환하며 선점 비활성 상태가 유지됩니다. 여기의1은 성공 bool이며 test_and_set_bit_lock의 이전bit0 성공과 반환 '
  '방향이 다릅니다.',
  '반환1일 때만 대응 unlock을 수행합니다. 실패 후에는 호출 전 preempt 깊이로 복구되었는지 계약을 확인합니다. 중첩 호출이 원래 깊이1이면 실패 후에도1일 수 있어 '
  '무조건0이라고 설명하지 않습니다.',
  [('bit_spin_trylock의1은 무엇인가?',
    '획득 성공이다',
    '이전bit1이어서 실패다',
    'wrapper는 원시 이전 bit 결과를 성공 bool로 바꾸어 반환합니다. 두 API의 반환 방향을 구분합니다.'),
   ('원래 깊이1인 상태에서 실패한 trylock 뒤 깊이는?',
    '1로 복구된다',
    '반드시0이 된다',
    'disable로2가 되고 실패의 enable로1이 됩니다. 호출 전 상태 복구와 무조건 선점 활성화를 구분합니다.')],
  [('실제 원문 조건', 'fixture는 성공 깊이1과 그 상태에서 실패한 nested trylock의 깊이1 유지를 검사했습니다.'),
   ('실행 검사 경계',
    '원본 세 헤더를 명시적인 사용자공간 atomic·preempt·instrumentation 모델과 함께 검사했습니다. 실제 kernel preemption, KCSAN 탐지, '
    'LKMM 또는 모든 architecture의 실행을 증명한 검사는 아닙니다.')]),
 ('Bit unlock·release 후 preempt enable와 debug 검사',
  'include/linux/bit_spinlock.h',
  'bit_spin_unlock',
  'DEBUG_SPINLOCK이면 BUG_ON으로 bit가 실제 설정됐는지 검사합니다. SMP 또는 DEBUG이면 clear_bit_unlock이 release의미로 bit를 '
  '지웁니다. 그 뒤 preempt_enable과 __release annotation을 수행합니다. 정상 획득에 대응하는 해제이며 annotation 자체가 CPU 잠금 명령이나 '
  'runtime 검사인 것은 아닙니다.',
  '보호한 데이터의 변경을 마친 후 대응 unlock을 한 번 수행합니다. 미획득 또는 이중 unlock을 정상 사용법으로 만들지 않습니다. release의 데이터 공개 의미와 선점 '
  '활성화의 scheduler 의미를 구분합니다.',
  [('정상 unlock에서 release bit clear는 preempt_enable 전인가?',
    '전이다',
    '항상 enable 뒤다',
    '원문은 bit 해제 후 enable합니다. 데이터 공개와 선점 상태 복구의 순서를 읽습니다.'),
   ('__release annotation 자체가 hardware bit를 지우는가?',
    '아니며 분석용 annotation이다',
    'annotation만으로 실제 lock이 해제된다',
    '실제 bit 변경은 clear_bit_unlock입니다. 정적 분석 표시와 실행 명령의 역할이 다릅니다.')],
  [('실제 원문 조건', '검사에서 정상 해제의 bit 상태와 preempt 깊이 균형을 따로 확인했습니다.'),
   ('실행 검사 경계',
    '원본 세 헤더를 명시적인 사용자공간 atomic·preempt·instrumentation 모델과 함께 검사했습니다. 실제 kernel preemption, KCSAN 탐지, '
    'LKMM 또는 모든 architecture의 실행을 증명한 검사는 아닙니다.')]),
 ('약한 bit unlock·같은 word의 모든 flag 보호 조건',
  'include/linux/bit_spinlock.h',
  '__bit_spin_unlock',
  '__bit_spin_unlock은 debug 확인과 preempt 복구는 유지하되 __clear_bit_unlock을 사용합니다. 원문은 잠금 bit가 나머지 flag도 보호하는 '
  '경우 등에서 쓸 수 있는 non-atomic 형태라고 설명합니다. generic 구현은 word를 읽고 해당 bit를 지운 값을 release store합니다. 읽기와 저장 사이 '
  '다른 bit의 독립 변경이 있으면 그 변경을 덮어쓸 수 있습니다.',
  '같은 word의 모든 수정자가 이 lock을 따라야 하는 전제를 확인합니다. 독립 atomic flag writer가 있다면 약한 전체 word 저장으로 그 값을 보존한다고 '
  '가정하지 않습니다. 일반 clear_bit_unlock과 계약 차이를 명시합니다.',
  [('약한 generic clear의 읽기 뒤 다른 bit가 설정되면 stale store는?',
    '그 변경을 덮어쓸 수 있다',
    'mask 밖 변경은 언제나 보존한다',
    '전체 word의 이전 값에서 계산한 새값을 저장하기 때문입니다. 단일 atomic AND RMW와 다릅니다.'),
   ('약한 unlock을 쓸 때 중요한 같은 word 조건은?',
    '다른 flag 수정도 같은 lock으로 보호된다',
    '다른 flag가 임의로 경쟁 변경돼도 된다',
    '원문은 word 나머지 bit의 보호 조건을 설명합니다. 외부 독립 writer와의 경쟁을 없애야 합니다.')],
  [('실제 원문 조건',
    '교육용 stale-read/store 순서 모델로 바깥 bit 변경 소실을 재현했습니다. 모든 architecture의 약한 구현을 실행한 것은 아닙니다.'),
   ('실행 검사 경계',
    '원본 세 헤더를 명시적인 사용자공간 atomic·preempt·instrumentation 모델과 함께 검사했습니다. 실제 kernel preemption, KCSAN 탐지, '
    'LKMM 또는 모든 architecture의 실행을 증명한 검사는 아닙니다.')]),
 ('Bit is_locked·CONFIG별 진단과 소유권의 차이',
  'include/linux/bit_spinlock.h',
  'bit_spin_is_locked',
  'SMP 또는 DEBUG이면 test_bit로 잠금 bit를 조회합니다. 그 외 PREEMPT_COUNT이면 preempt_count를 반환하고 그것도 없으면1을 반환합니다. 따라서 '
  '이 조회를 모든 CONFIG에서 해당 bit의 실제 상태나 현재 호출자의 소유권으로 해석할 수 없습니다. SMP의 bit 조회도 어느 CPU가 보유했는지 알려주지 않습니다.',
  '진단 경로의 CONFIG 조건을 확인합니다. 조회를 근거로 잠금 없이 보호 데이터를 쓰지 않습니다. preempt_count가 양수인지와 특정 객체의 lock 소유 여부는 다른 '
  '질문으로 다룹니다.',
  [('UP이며 DEBUG와 PREEMPT_COUNT가 없으면 is_locked는?',
    '1을 반환한다',
    '항상 메모리 bit를 읽는다',
    '원문의 마지막 분기는 상수1입니다. 실제 저장 bit 조회와 다른 CONFIG 계약입니다.'),
   ('SMP에서 bit가1이면 현재 thread의 소유임을 증명하는가?',
    '아니며 다른 CPU의 보유일 수도 있다',
    '언제나 호출자 소유다',
    '조회는 bit 상태입니다. 소유자를 기록하는 API가 아니므로 호출자 권한을 대신하지 않습니다.')],
  [('실제 원문 조건', '여섯 CONFIG 조합에서 조회와 preempt 분기를 검사했습니다. UP 분기의 bit 미변경도 확인했습니다.'),
   ('실행 검사 경계',
    '원본 세 헤더를 명시적인 사용자공간 atomic·preempt·instrumentation 모델과 함께 검사했습니다. 실제 kernel preemption, KCSAN 탐지, '
    'LKMM 또는 모든 architecture의 실행을 증명한 검사는 아닙니다.')]),
 ('Generic bit lock acquire·빠른 읽기와 atomic OR',
  'include/asm-generic/bitops/lock.h',
  'arch_test_and_set_bit_lock',
  'BIT_WORD로 word 주소를 이동하고 BIT_MASK로 bit를 선택합니다. 먼저 READ_ONCE 값에 mask가 이미 있으면1을 반환하여 비싼 atomic OR를 '
  '피합니다. 없으면 raw_atomic_long_fetch_or_acquire를 실행하고 old&mask의 bool을 반환합니다. 반환0의 성공 경로에 acquire 계약이 '
  '있습니다. 첫 조회0과 atomic 이전값은 경쟁으로 달라질 수 있습니다.',
  '조회의 fast path와 실제 성공 atomic 경계를 구분합니다. 성공 acquire가 대응 release와 동기화될 때 보호 payload 읽기의 순서를 보장하는 프로토콜로 '
  '사용합니다. READ_ONCE만으로 성공 획득을 주장하지 않습니다.',
  [('첫 READ_ONCE가0이면 atomic OR도 반드시 old0인가?',
    '아니며 사이 경쟁이 가능하다',
    '항상0으로 고정된다',
    '다른 CPU가 그 사이 bit를 설정할 수 있습니다. atomic 연산의 이전값으로 최종 성공을 판정합니다.'),
   ('문서가 성공 acquire를 설명하는 반환값은?',
    '0이다',
    '1이다',
    '원시 bit lock API는 oldbit를 반환합니다. old0 성공과 spin_trylock의 성공1을 구분합니다.')],
  [('실제 원문 조건',
    'generic 원문은 atomic_long_t로 cast해 word 연산에 연결합니다. 검사 모델은 GCC acquire atomic primitive입니다.'),
   ('실행 검사 경계',
    '원본 세 헤더를 명시적인 사용자공간 atomic·preempt·instrumentation 모델과 함께 검사했습니다. 실제 kernel preemption, KCSAN 탐지, '
    'LKMM 또는 모든 architecture의 실행을 증명한 검사는 아닙니다.')]),
 ('Generic clear unlock·원자적 AND NOT release',
  'include/asm-generic/bitops/lock.h',
  'arch_clear_bit_unlock',
  'word 주소를 BIT_WORD만큼 이동한 뒤 raw_atomic_long_fetch_andnot_release에 BIT_MASK를 전달합니다. 하나의 atomic RMW로 대상 '
  'bit만 지우며 같은 word의 다른 bit를 연산 기준상 보존합니다. release의미는 보호구간의 앞선 데이터 변경을 올바른 acquire 획득자에게 공개하는 잠금 프로토콜과 '
  '연결됩니다.',
  '다른 bit도 독립 atomic writer가 변경할 수 있는 word에서는 약한 읽기/저장 대신 이 RMW 계약을 확인합니다. 보호 객체 수명과 같은 lock 사용 규칙도 '
  '지킵니다. release를 모든 뒤쪽 메모리까지 정렬하는 full barrier로 단순화하지 않습니다.',
  [('이 generic clear는 어떤 atomic 산술인가?',
    'mask의 NOT를 AND한다',
    'word전체를 무조건0으로 저장한다',
    '대상 bit를 지우고 다른 bit를 보존하는 atomic AND NOT입니다. 모든 flag 초기화와 다릅니다.'),
   ('release만으로 임의의 다른 lock 조회와 동기화되는가?',
    '아니며 맞는 acquire 프로토콜이 필요하다',
    '어떤 조회든 자동 동기화된다',
    '데이터 공개는 대응하는 동기화 관계에서 해석합니다. 단순 다른 주소의 조회는 그 관계를 만들지 않습니다.')],
  [('실제 원문 조건', '다음 word의 bit70 획득·해제도 검사하여 word 번호와 내부 bit mask 계산을 확인했습니다.'),
   ('실행 검사 경계',
    '원본 세 헤더를 명시적인 사용자공간 atomic·preempt·instrumentation 모델과 함께 검사했습니다. 실제 kernel preemption, KCSAN 탐지, '
    'LKMM 또는 모든 architecture의 실행을 증명한 검사는 아닙니다.')]),
 ('Generic 약한 clear·READ_ONCE 뒤 release store',
  'include/asm-generic/bitops/lock.h',
  'arch___clear_bit_unlock',
  'old=READ_ONCE(*p)로 word를 읽고 old&=~BIT_MASK(nr)로 bit를 지운 뒤 raw_atomic_long_set_release로 전체 word를 '
  '저장합니다. store 자체의 원자성과 read-modify-write 전체의 원자성은 다릅니다. 다른 bit writer가 읽기 이후 값을 바꾸면 old 기반 store가 새값을 '
  '소실시킬 수 있습니다.',
  '이 word의 flag 변경이 같은 lock으로 직렬화되어 있는 경우에만 전제를 검토합니다. 두 atomic primitive가 있다고 전체 복합 동작을 atomic RMW라고 '
  '부르지 않습니다. source와 상위 weak unlock의 사용 조건을 함께 읽습니다.',
  [('atomic read와 atomic store를 나누면 전체 RMW도 atomic인가?',
    '아니며 사이 경쟁이 가능하다',
    'primitive 둘이 atomic이면 항상 전체도 atomic이다',
    '두 동작 사이에 다른 writer가 들어올 수 있습니다. 전체 변화가 하나의 원자적 사건은 아닙니다.'),
   ('generic weak clear의 저장 대상 폭은?',
    '전체 unsigned long word 다',
    '선택 bit 하나만 독립 byte로 저장한다',
    'old에서 mask를 지운 전체 word를 set_release합니다. 다른 bit 소실 조건을 이해하는 근거입니다.')],
  [('실제 원문 조건', '이 설명은 선택된 generic 구현입니다. x86 등 architecture별 약한 구현은 별도 원문을 읽어야 합니다.'),
   ('실행 검사 경계',
    '원본 세 헤더를 명시적인 사용자공간 atomic·preempt·instrumentation 모델과 함께 검사했습니다. 실제 kernel preemption, KCSAN 탐지, '
    'LKMM 또는 모든 architecture의 실행을 증명한 검사는 아닙니다.')]),
 ('XOR unlock과 waiter bit·변경값보다 이전bit7 조회',
  'include/asm-generic/bitops/lock.h',
  'arch_xor_unlock_is_negative_byte',
  'generic helper는 raw_atomic_long_fetch_xor_release(mask,p)로 word를 XOR하고 old&BIT(7)의 bool을 반환합니다. '
  'public 문서는 mask로 낮은 byte bit0..6을 변경하며 bit7은 PG_waiters 표시로 사용한다고 설명합니다. 반환은 이전bit7입니다. word전체의 '
  '부호bit63이나 XOR 뒤 bit7을 읽는 표현이 아닙니다.',
  '낮은 byte의 허용 mask와 folio 상위 프로토콜을 확인합니다. bit7을 waiter 표시로 유지하는 규칙을 지킵니다. 이름의 negative byte를 native '
  'long 음수 검사라고 해석하지 않습니다.',
  [('generic helper가 확인하는 위치는?',
    '이전 word의 bit7이다',
    'long의 bit63이다',
    '본문은 old&BIT(7)입니다. byte의 상위 bit와 machine word의 부호 위치는 다릅니다.'),
   ('public 문서에서 mask로 변경하는 bit 범위는?',
    '낮은 byte의0..6이다',
    '모든63bit를 임의로 변경한다',
    'waiter 표시인 bit7은 별도의 프로토콜 역할입니다. 문서의 허용 사용과 generic 식의 기계적 능력을 구분합니다.')],
  [('실제 원문 조건', '낮은byte0..255 각각의 이전bit7 반환과 XOR 결과를 검사했습니다. architecture override 조건도 원문에 있습니다.'),
   ('실행 검사 경계',
    '원본 세 헤더를 명시적인 사용자공간 atomic·preempt·instrumentation 모델과 함께 검사했습니다. 실제 kernel preemption, KCSAN 탐지, '
    'LKMM 또는 모든 architecture의 실행을 증명한 검사는 아닙니다.')]),
 ('Bit lock instrumentation·접근 위치와 분석 hook',
  'include/asm-generic/bitops/instrumented-lock.h',
  'test_and_set_bit_lock',
  'instrumented test_and_set_bit_lock은 addr+BIT_WORD(nr)의 long 크기 접근을 atomic_read_write hook으로 알리고 arch '
  'helper를 호출합니다. clear는 kcsan_release와 atomic_write hook,약한 clear는 일반 instrument_write hook을 사용합니다. '
  'XOR unlock도 release hook 뒤 atomic_write를 알립니다. hook만으로 잠금 구현이 대체되지 않습니다.',
  '분석 도구에 알리는 접근 종류와 실제 arch 동작을 따로 읽습니다. 이 wrapper의 역할을 sanitizer가 객체 범위와 모든 경쟁을 자동 해결한다는 뜻으로 확대하지 '
  '않습니다. nr의 유효 범위와 실제 word 용량을 여전히 보장합니다.',
  [('약한 clear wrapper의 접근 hook 종류는?',
    'instrument_write다',
    '항상 instrument_atomic_read_write다',
    '원문은 non-atomic RMW 계약에 맞춰 일반 write hook을 사용합니다. 실제 arch 선택과 분석 표시를 구분합니다.'),
   ('접근 hook 실행만으로 실제 lock bit를 획득하는가?',
    '아니며 arch helper가 실제 연산을 한다',
    'hook 하나가 모든 잠금을 대신한다',
    'wrapper는 분석 표시를 호출한 뒤 arch_test_and_set_bit_lock으로 연결합니다. 실행과 instrumentation의 역할이 다릅니다.')],
  [('실제 원문 조건', '검사 모델은 hook 횟수와 주소 크기를 기록합니다. KCSAN의 실제 경쟁 탐지 실행이 아닙니다.'),
   ('실행 검사 경계',
    '원본 세 헤더를 명시적인 사용자공간 atomic·preempt·instrumentation 모델과 함께 검사했습니다. 실제 kernel preemption, KCSAN 탐지, '
    'LKMM 또는 모든 architecture의 실행을 증명한 검사는 아닙니다.')])]

def register(topic,q,detail):
 for title,path,symbol,principle,use,qa,cards in ROWS:
  topic(title,"동기화",path,symbol,"잠금 상태의 bit 연산과 메모리 공개 순서,선점 상태를 실제 소스에서 구분하여 동시성 기술의 사용 조건을 배웁니다.",principle,use,"획득과 해제의 반환 의미 및 CONFIG별 분기,preempt 깊이와 atomic 경계를 순서대로 읽으세요.",*(q(*x) for x in qa),details=[detail(*x) for x in cards])
