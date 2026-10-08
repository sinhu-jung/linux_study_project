"""Whole IRQ return type/header: values, typedef and boolean conversion."""
ROWS = [('IRQ 반환 enum: 세 가지 처리 결과',
  'irqreturn',
  'enum irqreturn은 장치가 처리하지 않은 결과 0, 처리한 결과 1, 등록한 처리 스레드를 깨워 달라는 결과 2를 이름으로 표현합니다. C의 enum은 이 이름에 정수 값을 '
  '부여합니다. 인터럽트 번호나 CPU 모드를 저장하는 자료구조가 아닙니다. 각 장치 handler는 해당 장치의 상태를 확인한 뒤 적절한 결과를 반환합니다.',
  '세 이름을 숫자와 연결하고 no_action 및 __handle_irq_event_percpu의 반환 흐름을 따라가세요. shared IRQ에서는 장치마다 반환한 결과가 OR로 합쳐지므로 '
  '개별 반환과 전체 결과를 구분합니다.',
  ('세 값은 어떤 정보를 표현하나요?',
   '개별 handler의 처리 여부 또는 thread 깨우기 요청입니다.',
   '항상 장치의 IRQ 번호입니다.',
   '정수에 붙인 이름으로 callback의 처리 결과를 전달하는 인터페이스입니다.'),
  ('enum 선언이 실제 IRQ 스레드를 생성하나요?',
   '아닙니다. 결과 값을 정의합니다.',
   '그렇습니다. 선언만으로 스레드가 만들어집니다.',
   '값의 정의와 IRQ 등록·실제 thread 생성·깨우기의 구현은 서로 다른 단계입니다.')),
 ('IRQ_NONE: 처리하지 않은 장치의 결과',
  'IRQ_NONE',
  'IRQ_NONE은 0 << 0이므로 0입니다. 주석은 이 장치의 인터럽트가 아니거나 이 장치가 처리하지 않았다는 의미를 설명합니다. 공유 interrupt에서 한 장치가 NONE을 반환해도 '
  '다른 장치의 handler는 계속 호출됩니다. 전체 결과에 OR하면 기존 처리 bit를 지우지 않습니다.',
  'no_action의 반환과 공유 action 순회에서 retval |= res를 함께 보세요. 다른 장치가 HANDLED를 반환한 뒤 NONE이 나오는 예에서 1 | 0을 계산합니다.',
  ('HANDLED 1에 NONE 0을 OR하면 무엇인가요?', '1입니다.', '항상 마지막 결과 0입니다.', 'bit OR의 항등 원소 0은 이미 누적한 처리 정보를 지우지 않습니다.'),
  ('한 장치의 NONE이 전체 공유 IRQ의 미처리를 확정하나요?',
   '아닙니다. 나머지 handler 결과도 확인해야 합니다.',
   '그렇습니다. 나머지 callback은 생략됩니다.',
   '개별 장치의 판단과 전체 action 목록의 합산 결과를 구분해야 합니다.')),
 ('IRQ_HANDLED: 장치가 처리한 결과',
  'IRQ_HANDLED',
  'IRQ_HANDLED는 1 << 0으로 값 1입니다. 장치가 이 interrupt를 처리했다는 callback 결과입니다. 이 값 자체는 thread 깨우기를 요청하지 않습니다. 실제 '
  'event switch는 IRQ_WAKE_THREAD 값 2를 별도로 검사하므로 성공 의미와 비동기 작업 요청을 구분해야 합니다.',
  '장치의 pending 상태를 확인하고 처리한 뒤 HANDLED를 반환하는 흐름을 그려 보세요. 이 반환만으로 등록 thread_fn이 자동 실행되는 것으로 설명하지 않습니다.',
  ('HANDLED의 값은 얼마인가요?', '1입니다.', '2입니다.', '왼쪽 shift에서 1을 0칸 이동하므로 값은 그대로 1입니다.'),
  ('HANDLED만 반환하면 WAKE_THREAD case에 들어가나요?',
   '아닙니다. switch는 값 2를 검사합니다.',
   '그렇습니다. 성공이면 어떤 thread든 깨웁니다.',
   '처리 성공과 thread 깨우기 요청은 서로 다른 반환 값으로 전달합니다.')),
 ('IRQ_WAKE_THREAD: 등록한 thread_fn의 요청',
  'IRQ_WAKE_THREAD',
  'IRQ_WAKE_THREAD는 1 << 1으로 값 2입니다. hard handler가 등록한 처리 thread를 깨워 달라고 요청하는 결과입니다. 이 값이 task pointer를 담는 '
  '것은 아닙니다. handle.c는 thread_fn 유무를 검사하고 없는 경우 경고합니다. 값 3을 단일 callback에서 반환하면 exact switch case 2와 일치하지 '
  '않습니다.',
  'request_threaded_irq의 공개 prototype에서 handler와 thread_fn을 구분하고 handle.c의 깨우기 흐름을 연결합니다. 실제 등록 함수 전체와 '
  'thread 실행 완료는 별도 소스로 따라갑니다.',
  ('thread_fn 없이 WAKE_THREAD를 반환하면 어떻게 되나요?',
   '누락을 경고하고 thread를 깨우지 않습니다.',
   '자동으로 처리 함수를 새로 생성합니다.',
   '반환 값은 요청이고 처리 callback을 등록하는 계약은 먼저 충족해야 합니다.'),
  ('두 장치의 결과 1과 2를 합친 3은 단일 callback 값 2와 같나요?',
   '아닙니다. OR 합산 값과 exact case는 다릅니다.',
   '그렇습니다. switch는 항상 bit 포함으로 판단합니다.',
   'C switch는 정수 값의 동등성을 검사하며 bitmask 포함 여부를 자동 검사하지 않습니다.')),
 ('irqreturn_t: enum에 붙인 타입 이름',
  'irqreturn_t',
  'typedef enum irqreturn irqreturn_t는 기존 enum 타입에 다른 이름을 붙입니다. 새로운 변수나 메모리를 만드는 선언이 아니고 endian 변환이나 값을 '
  '재계산하는 함수도 아닙니다. IRQ handler의 함수 반환 타입을 간결하게 작성하는 데 사용합니다. enum의 크기를 항상 1 byte로 보장하는 선언은 아닙니다.',
  'irqreturn_t handler(int irq, void *dev_id) 형태에서 반환 타입과 인자를 나눠 읽으세요. typedef 이름으로 callback prototype을 쓰고 '
  'enum 값 NONE, HANDLED, WAKE_THREAD 중 계약에 맞는 결과를 반환합니다.',
  ('typedef 선언만으로 새로운 객체를 할당하나요?',
   '아닙니다. 타입에 별칭을 붙입니다.',
   '그렇습니다. IRQ마다 메모리를 할당합니다.',
   'C의 타입 선언과 실행 시 객체 생성은 다른 작업이며 이 줄에는 할당 호출이 없습니다.'),
  ('이 선언이 enum의 크기를 1 byte로 고정하나요?',
   '아닙니다. 그런 크기 보장은 없습니다.',
   '그렇습니다. typedef는 항상 1 byte입니다.',
   '타입 별칭은 저장 크기를 지정하는 byte 배열이나 packed 표현과 같지 않습니다.')),
 ('IRQ_RETVAL: 참거짓을 처리 결과로 변환',
  'IRQ_RETVAL',
  'IRQ_RETVAL(x)는 조건 연산자 ((x) ? IRQ_HANDLED : IRQ_NONE)입니다. 0이면 NONE 0, 0이 아닌 값이면 HANDLED 1입니다. 음수도 참이며 입력 '
  '2를 넣어도 WAKE_THREAD를 보존하지 않고 HANDLED로 변환합니다. 매크로 본문에는 x가 조건식에 한 번만 있으므로 이 매크로 자체는 인자를 중복 평가하지 않습니다.',
  '장치의 처리 여부를 나타내는 참거짓 값을 결과로 바꿀 때 사용하세요. 실제 원본 header를 포함한 fixture는 -16부터 16까지 입력을 검사합니다. thread 요청 값을 변환하는 '
  '도구로 쓰지 않습니다.',
  ('IRQ_RETVAL(IRQ_WAKE_THREAD)의 결과는 무엇인가요?',
   'IRQ_HANDLED입니다.',
   'IRQ_WAKE_THREAD가 유지됩니다.',
   '입력 값 2는 참이므로 조건 연산자의 HANDLED 분기를 선택합니다.'),
  ('IRQ_RETVAL(-1)의 결과는 무엇인가요?',
   'IRQ_HANDLED입니다.',
   'IRQ_NONE입니다.',
   'C 조건식은 0만 거짓으로 취급하므로 음수 -1도 참이며 결과는 1입니다.'))]

def register(topic,q,detail):
 for title,symbol,principle,use,qa,qb in ROWS:
  topic(title,"장치·드라이버","include/linux/irqreturn.h",symbol,
   "IRQ handler가 장치를 처리했는지, 등록한 thread를 깨울지 전달하는 타입과 상수를 실제 선언 및 event 처리 흐름에 연결합니다.",principle,use,
   "enum의 정수 값, typedef의 타입 별칭, 조건 연산자의 참거짓 변환과 개별 반환·전체 OR 합산의 차이에 주석을 달아보세요.",q(title+' · '+qa[0],*qa[1:]),q(title+' · '+qb[0],*qb[1:]),details=[
    detail("원문 범위","고정 Linux v6.12의 irqreturn.h 21행 전체를 읽고 SPDX·include guard·enum 문서·세 값·typedef·IRQ_RETVAL·guard 종료를 확인했습니다. 앞 수업의 실제 handle.c switch와 OR 합산에 연결합니다."),
    detail("실행 검산","IRQ handle fixture가 변경 없는 원본 header를 포함합니다. 각 O2/ASan·UBSan 빌드에서 enum 값 1건과 -16..16 입력 33건을 확인했습니다. 이는 앞 수업의 563건 안에 포함된 부분집합이며 별도의 새 68건 실행으로 중복 합산하지 않습니다."),
    detail("사용 조건","handler 반환은 공개 enum 계약에 맞춰 작성합니다. IRQ_RETVAL은 참거짓 처리 여부를 변환하며 WAKE_THREAD를 보존하지 않습니다. 실제 thread 생성·스케줄·hardware interrupt는 이 header의 기능이 아닙니다.")])
