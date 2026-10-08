"""Whole lockref header/body contracts, serial-model checks with explicit limits."""
ROWS = [('Lockref 표현·잠금과 count를 같은 CAS 범위에 넣기',
  'include/linux/lockref.h',
  'lockref',
  'lockref는 spinlock과 int count를 한 구조에 둡니다. architecture의 CMPXCHG_LOCKREF 설정,SMP,SPINLOCK_SIZE<=4가 함께 '
  '성립하면 aligned_u64 lock_count와 lock/count 구조가 union으로 겹칩니다.8byte CAS로 lock 상태와 count를 함께 비교해 잠금 없이 '
  '변경하더라도 spinlock을 잡은 것과 양립하는 상태 조건을 확인합니다. 조건이 아니면 실제 spinlock 경로를 사용합니다.',
  '자료 표현과 target의 설정 및 spinlock 크기를 함께 확인합니다. 일반 atomic refcount와 같은 API라고 가정하지 않습니다. int count의 유효 범위와 '
  '객체 수명을 상위 사용자가 보장해야 합니다.',
  [('CAS 최적화 선택에 필요한 조건은?',
    'arch 설정과 SMP 및 작은 spinlock 크기다',
    'count 값이1이면 무조건 선택된다',
    '헤더의 compile-time 조건은 architecture,SMP,SPINLOCK_SIZE입니다. runtime count 값과 다른 선택입니다.'),
   ('union의 lock_count는 무엇과 겹치는가?',
    'lock과 count를 포함한 구조다',
    '별도의 독립 count 사본이다',
    '같은8byte 표현을 두 관점으로 읽습니다. 별도의 count를 동기화하는 알고리즘이 아닙니다.')],
  [('계약과 검수',
    'header전체의 forward 선언과 __lockref_is_dead도 연결해 읽습니다. CAS 모델은8byte 구조 크기를 static assert로 확인했습니다.'),
   ('실행 범위',
    '완전한 원본 header와 lib body를 직렬 spin/CAS/READ_ONCE 상태 모델로 검사했습니다. 실제 동시 실행·architecture atomic '
    '명령·memory ordering의 증명은 아닙니다.')]),
 ('Lockref CAS loop·실패 expected 갱신과100회 한도',
  'lib/lockref.c',
  'CMPXCHG_LOOP',
  'old.lock_count를 읽고 lock 상태가 unlocked인 동안 old를 new로 복사하여 CODE를 수행합니다. try_cmpxchg64_relaxed가 성공하면 '
  'SUCCESS를 실행합니다. 실패하면 expected인 old.lock_count가 실제 관측값으로 갱신되므로 다음 반복이 새로운 count를 기반으로 계산합니다. '
  'retry는100에서 시작하여100번 실패하면 loop를 벗어납니다. 함수별로 이후 fallback 또는 실패를 결정합니다.',
  'CODE와 SUCCESS에 전달된 문장을 실제 함수마다 펼쳐 읽습니다. 실패 때 old가 갱신되는 계약과 재계산을 확인합니다. relaxed CAS를 모든 payload의 '
  'acquire/release 보장으로 설명하지 않습니다.',
  [('CAS 실패 후 다음 계산의 old는?',
    '실패 CAS가 갱신한 관측값이다',
    '최초 snapshot으로 영원히 고정된다',
    'try_cmpxchg의 expected 갱신 계약이 원문 주석에 있습니다. 재시도는 바뀐 상태에서 새값을 다시 만듭니다.'),
   ('100회 실패하면 모든 함수가 같은 fallback을 수행하는가?',
    '아니며 함수별 이후 경로가 다르다',
    '무조건 count를 변경하고 성공한다',
    'macro이후 코드가 다릅니다. put_return은 실패를 반환하고 다른 함수는 spinlock fallback을 가질 수 있습니다.')],
  [('계약과 검수', '모델에서 처음 실패 때 count를3 증가시켜 old 갱신과 재계산 결과14를 확인했습니다.100회 실패 fallback도 따로 검사했습니다.'),
   ('실행 범위',
    '완전한 원본 header와 lib body를 직렬 spin/CAS/READ_ONCE 상태 모델로 검사했습니다. 실제 동시 실행·architecture atomic '
    '명령·memory ordering의 증명은 아닙니다.')]),
 ('Lockref get·이미 보유한 참조의 증가',
  'lib/lockref.c',
  'lockref_get',
  'lockref_get은 CAS CODE에서 new.count++를 수행하고 성공하면 반환합니다. CAS가 불가능하거나 실패 한도를 넘으면 spin_lock 아래 count를 '
  '증가시키고 해제합니다. 원문은 호출자가 이미 참조를 가지고 있어 count가0일 수 없음을 아는 경우에만 유효하다고 설명합니다. 함수는 임의 dead 상태나 overflow를 '
  '안전하게 거절하는 refcount validator가 아닙니다.',
  '이미 보유한 객체 참조를 하나 더 만들 때 사용 조건을 확인합니다. 객체가 해제되지 않을 수명과 int count의 안전한 범위를 유지합니다. 모르는 주소에서 무조건 get을 '
  '호출해 객체를 살아 있게 만들려고 하지 않습니다.',
  [('lockref_get의 기본 호출 전제는?',
    '이미 객체 참조를 보유한다',
    '해제된 객체 주소라도 언제나 안전하다',
    '원문은 count가0일 수 없음을 알고 있어야 한다고 명시합니다. count 변경과 객체 메모리 수명은 별개입니다.'),
   ('CAS 조건이 없으면 get은 어떻게 증가하는가?',
    'spinlock 아래 count를 증가한다',
    '항상 변경 없이 실패한다',
    '이 함수는 일반 spinlock fallback을 제공합니다. 최적화 없음과 API 기능 없음은 다릅니다.')],
  [('계약과 검수', '검사에서는 양수 count만 get에 전달했습니다. overflow나 해제된 객체를 실행하지 않았습니다.'),
   ('실행 범위',
    '완전한 원본 header와 lib body를 직렬 spin/CAS/READ_ONCE 상태 모델로 검사했습니다. 실제 동시 실행·architecture atomic '
    '명령·memory ordering의 증명은 아닙니다.')]),
 ('Lockref get_not_zero·0과 dead를 함께 거절',
  'lib/lockref.c',
  'lockref_get_not_zero',
  'CAS 경로는 old.count<=0이면0을 반환하고 양수에서 성공하면1을 반환합니다. fallback도 spinlock 아래 count>0일 때만 증가시킵니다.0과 음수 dead '
  '상태는 증가하지 않습니다. 반환은 새 count 숫자가 아니라 증가 성공 bool 입니다. 주소와 수명이 유효하다는 전제는 별도로 필요합니다.',
  '아직 살아 있는 양수 참조 집합에서 조건부 참조를 얻는 프로토콜에 사용합니다. 반환1 뒤에만 새 참조를 사용합니다. 실패0을 새 count가0이라는 유일한 뜻으로 해석하지 '
  '않습니다.',
  [('old count=-128의 get_not_zero는?',
    '0을 반환하고 count를 유지한다',
    '-127로 증가하고 성공한다',
    '조건은 old.count<=0입니다. 죽은 음수 상태도0과 함께 거절합니다.'),
   ('성공 반환1은 새 count가1이라는 뜻인가?',
    '아니며 성공 bool이다',
    '반드시 새 count1이다',
    '양수 count를 하나 증가시킨 결과는2 이상일 수 있습니다. 반환은 값 자체가 아닙니다.')],
  [('계약과 검수', '경계 -128,-1,0,1,2,3,10,100을 직렬 참조 상태와 비교했습니다.'),
   ('실행 범위',
    '완전한 원본 header와 lib body를 직렬 spin/CAS/READ_ONCE 상태 모델로 검사했습니다. 실제 동시 실행·architecture atomic '
    '명령·memory ordering의 증명은 아닙니다.')]),
 ('Lockref put_not_zero·마지막 참조를 남기는 감소',
  'lib/lockref.c',
  'lockref_put_not_zero',
  'old.count<=1이면 감소하지 않고0을 반환합니다. count>1이면 하나 감소하고1을 반환합니다. fallback은 spinlock 아래 같은 조건을 검사합니다. 이 '
  'API는 마지막 참조를0으로 만드는 해제 동작을 수행하지 않습니다. dead와0도 변화 없이 실패합니다.',
  '마지막 참조의 처리와 일반 감소를 나누는 상위 프로토콜에서 사용합니다. 실패하면 실제 현재 상태를 맞는 잠금 규약으로 확인합니다.0반환을 이미 감소가 완료됐다는 의미로 사용하지 '
  '않습니다.',
  [('count1의 put_not_zero 결과는?',
    'count1 유지,반환0이다',
    'count0으로 감소,반환1이다',
    '마지막 참조를 남기는 조건부 감소입니다. count<=1을 변경하지 않습니다.'),
   ('이 API가 객체 free까지 실행하는가?',
    '아니며 조건부 count 변경만 한다',
    '항상 마지막 참조를free한다',
    '원문에는 객체 해제 호출이 없습니다. 마지막 처리와 메모리 수명은 상위 규약에서 결정합니다.')],
  [('계약과 검수', 'get_not_zero의 양수 조건과 put_not_zero의1초과 조건을 서로 바꾸어 읽지 않습니다.'),
   ('실행 범위',
    '완전한 원본 header와 lib body를 직렬 spin/CAS/READ_ONCE 상태 모델로 검사했습니다. 실제 동시 실행·architecture atomic '
    '명령·memory ordering의 증명은 아닙니다.')]),
 ('Lockref put_return·새값 또는-1과 CAS 없는 구성',
  'lib/lockref.c',
  'lockref_put_return',
  'CAS CODE는 old.count<=0이면-1을 반환하고 양수이면 new.count를 하나 낮춥니다. 성공하면 new.count를 반환하여 count1에서0으로 내려갈 수도 '
  '있습니다. macro이후는 바로-1이며 spinlock fallback이 없습니다. CAS가 선택되지 않은 구성,lock이 held인 snapshot,100회 실패도-1로 종료될 '
  '수 있어 count가dead였다는 단일 의미로 해석할 수 없습니다.',
  '반환>=0에서만 실제 감소 결과로 처리합니다. -1이면 상위의 적절한 fallback 프로토콜을 사용하고 감소가 있었다고 가정하지 않습니다.0반환이 객체 메모리를 자동 해제한다는 '
  '뜻도 아닙니다.',
  [('CAS 없는 구성에서 put_return의 동작은?',
    '-1을 반환하고 count를 바꾸지 않는다',
    'spinlock fallback으로 항상 감소한다',
    '이 함수에는 fallback body가 없습니다. 다른 lockref 함수와 구분되는 계약입니다.'),
   ('반환-1이 항상 dead count를 증명하는가?',
    '아니며 잠금이나 재시도 한도도 원인이다',
    '음수 count인 경우에만 가능하다',
    'lock 상태나 CAS 실패로 loop를 벗어나도-1입니다. 실패 원인을 하나로 단정하지 않습니다.')],
  [('계약과 검수', 'CAS 있는 모델에서1→0과 locked 실패,100회 실패를 확인했습니다. CAS 없는 모델도-1과 상태 보존을 검사했습니다.'),
   ('실행 범위',
    '완전한 원본 header와 lib body를 직렬 spin/CAS/READ_ONCE 상태 모델로 검사했습니다. 실제 동시 실행·architecture atomic '
    '명령·memory ordering의 증명은 아닙니다.')]),
 ('Lockref put_or_lock·마지막 참조에서 잠금 인계',
  'lib/lockref.c',
  'lockref_put_or_lock',
  'count>1이면 감소 성공1을 반환하고 잠금을 보유하지 않습니다. count<=1이면 CAS loop에서 break한 뒤 spin_lock을 잡습니다. 잠금 아래에도 '
  'count<=1이면 감소 없이0을 반환하면서 lock을 계속 보유합니다. 경쟁으로 count가 커졌으면 감소하고 unlock한 뒤1입니다.0반환 경로는 호출자가 마지막 참조의 상태 '
  '처리를 잠금 아래 이어가는 인계입니다.',
  '반환0이면 count를 무조건0으로 간주하지 말고 잠금 아래 실제 상태와 마지막 처리 규약을 확인합니다. 이후 대응 unlock의 책임을 수행합니다. 반환1이면 이미 해제된 잠금을 '
  '다시 unlock하지 않습니다.',
  [('count1에서 반환0이면 lock 상태는?',
    '호출자가 보유하도록 잠금이 유지된다',
    '항상 해제되어 있다',
    '잠금 아래 count<=1 분기는 unlock 없이 반환합니다. 호출자에게 보호 구간을 넘기는 API입니다.'),
   ('반환0 때 count는 무조건0으로 감소했는가?',
    '아니며 감소 없이 상태를 처리한다',
    '반드시1을0으로 바꾼다',
    '조건 분기는 count를 변경하지 않습니다. 마지막 상태 처리 책임을 인계하는 것과 감소 완료를 구분합니다.')],
  [('계약과 검수', 'fixture는 반환0의 lock held와 count 보존을 확인한 뒤 호출자 역할로 unlock했습니다.'),
   ('실행 범위',
    '완전한 원본 header와 lib body를 직렬 spin/CAS/READ_ONCE 상태 모델로 검사했습니다. 실제 동시 실행·architecture atomic '
    '명령·memory ordering의 증명은 아닙니다.')]),
 ('Lockref mark_dead와 is_dead·음수 sentinel와 잠금 전제',
  'lib/lockref.c',
  'lockref_mark_dead',
  'mark_dead는 assert_spin_locked로 잠금 보유 전제를 확인하고 count=-128로 표시합니다. __lockref_is_dead는 count<0의 bool을 '
  '반환하며 헤더는 신뢰할 결과를 위해 spinlock 아래 호출해야 한다고 설명합니다. dead 표시가 객체 메모리를 직접 free하지는 않습니다. 음수 sentinel와 일반 참조 '
  '수0은 다른 상태입니다.',
  '정해진 수명 종료 프로토콜에서 잠금 아래 dead를 표시하고 조회합니다. dead 뒤의 count 증가 조건을 각 API에서 확인합니다. 잠금 없이 조회한 숫자를 근거로 임의 객체 '
  '접근의 안전성을 판단하지 않습니다.',
  [('mark_dead가 저장하는 sentinel은?', '-128이다', '0이다', '원문은 음수 상태를 dead로 구분합니다.0참조와 같은 값으로 합치지 않습니다.'),
   ('dead 표시만으로 객체 free까지 실행되는가?',
    '아니며 count 표시만 한다',
    '항상 allocator에 즉시free한다',
    '본문은 assertion과 count 대입뿐입니다. 실제 메모리 해제는 다른 수명 단계입니다.')],
  [('계약과 검수', 'mark_dead의 잠금 전제와 __lockref_is_dead의 신뢰 가능한 조회 조건을 함께 읽었습니다.'),
   ('실행 범위',
    '완전한 원본 header와 lib body를 직렬 spin/CAS/READ_ONCE 상태 모델로 검사했습니다. 실제 동시 실행·architecture atomic '
    '명령·memory ordering의 증명은 아닙니다.')]),
 ('Lockref get_not_dead·0참조와 dead의 다른 상태',
  'lib/lockref.c',
  'lockref_get_not_dead',
  'get_not_dead는 old.count<0일 때만 실패하고0은1로 증가시킬 수 있습니다. fallback도 잠금 아래 count>=0을 허용합니다. get_not_zero가0도 '
  '거절하는 것과 차이입니다. 이 API가 해제된 메모리를 부활시키는 것은 아니며 객체가 아직 존재하고 dead 표시 및 마지막 처리와 양립하는 상위 규약 안에서만 의미가 있습니다.',
  '0과 dead를 구분해야 하는 사용 프로토콜에서 선택합니다. 이미 해제된 주소에는 적용하지 않습니다. 반환1로 새 참조를 얻었을 때 대응 감소와 수명 관리 규칙을 지킵니다.',
  [('count0의 get_not_dead는?',
    'count1로 증가하고1을 반환한다',
    'get_not_zero처럼 항상 거절한다',
    '조건은 음수만 제외합니다.0을 허용하는 것이 두 API의 구체적인 차이입니다.'),
   ('이 API로 이미free된 객체 주소를 안전하게 부활시킬 수 있는가?',
    '아니며 유효 객체 수명이 전제다',
    '주소만 있으면 항상 복구된다',
    'count 계약은 접근 가능한 lockref 객체를 전제로 합니다. 이미 해제된 메모리에 대한 안전한 복구 API가 아닙니다.')],
  [('계약과 검수', '직렬 상태 모델에서0허용과 음수 거절을 두 조건부 get API와 나란히 비교했습니다.'),
   ('실행 범위',
    '완전한 원본 header와 lib body를 직렬 spin/CAS/READ_ONCE 상태 모델로 검사했습니다. 실제 동시 실행·architecture atomic '
    '명령·memory ordering의 증명은 아닙니다.')])]

def register(topic,q,detail):
 for title,path,symbol,principle,use,qa,cards in ROWS:
  topic(title,"동기화",path,symbol,"참조 수와 잠금 상태를 함께 관리하는 실제 구현을 읽고,CAS 최적화와 수명 종료 프로토콜의 조건을 배웁니다.",principle,use,"원문의 count 경계,반환값과 잠금 보유 여부를 분기마다 표로 적고 CAS 실패 뒤 경로를 추적하세요.",*(q(*x) for x in qa),details=[detail(*x) for x in cards])
