"""Complete aging proportions with caller epoch and rounding constraints."""
def register(topic,q,detail):
 def lesson(title,path,symbol,why,principle,use,reading,qa,cards):
  topic(title,'동기화',path,symbol,why,principle,use,reading,*(q(*x) for x in qa),details=[detail(*x) for x in cards])
 c='lib/flex_proportions.c';h='include/linux/flex_proportions.h'
 lesson('시간에 따라 감쇠하는 비율·최근 이벤트에 큰 가중치',h,'fprop_global',
  '누적 총합만으로는 오래된 이벤트가 현재 비율을 계속 지배하는 문제를 배웁니다.',
  '전역 events는 감쇠된 전체 분모이고 각 타입의 local events는 분자입니다. 매 기간 과거 값을 절반으로 줄여 최근 이벤트에 상대적으로 큰 가중치를 줍니다. fprop_global은 per-CPU 카운터·unsigned period·seqcount를 가지며 각 local은 자기 period와 raw lock을 가집니다. 파일 주석의 수학적 정규화와 정수 반올림·근사 읽기는 구분합니다.',
  '여러 이벤트 종류의 최근 활동 비중을 추적할 때 사용합니다. lifetime 누적 비율이나 벽시계 시간 자동 측정 API로 읽지 않습니다. caller가 기간 전환 시점을 정의하고 local·global 객체 수명을 관리합니다.',
  '전역·로컬 구조체와 C 파일의 감쇠 합 공식 주석을 연결하세요.',
  [('과거 기간마다 절반 감쇠하는 주된 목적은?','오래된 기록의 영향력을 줄여 최근 변화에 부드럽게 반응하기 위해서다','과거 모든 이벤트를 동일 가중치로 영구 유지하기 위해서다','지수적으로 줄어드는 기록 가중치입니다. 단순 누적 카운터와 다른 비율 모델입니다.'),('기간이 자동으로 벽시계 1초마다 바뀌는가?','아니며 caller가 new_period를 호출해 정의한다','구조체가 타이머를 내장해 항상 자동 실행한다','이 파일에는 자동 주기 타이머가 없습니다. 기간 길이와 호출 정책을 외부에서 선택합니다.')],
  [('수학과 구현','정규화된 이상적 비율 합이 1이라는 주석 공식과 정수 shift·근사 카운터·초기 분모 1의 실제 값 차이를 구분합니다.'),('CPU별 저장','분자·분모 카운터는 CPU별 갱신을 모아 중앙 경쟁을 줄입니다. 비율 계산 기술과 underlying batching 카운터 원리를 연결합니다.')])
 lesson('비율 객체 초기화·분모 1과 실패 전파',c,'fprop_global_init',
  '이벤트가 아직 없는 상태에서도 분모 0을 피하는 초기 상태와 할당 실패를 배웁니다.',
  'global_init은 period=0과 events=1로 시작하고 per-CPU init의 오류를 그대로 반환합니다. 성공하면 sequence를 초기화하고 0을 반환합니다. local_init은 events=0·period=0·raw lock으로 시작합니다. 초기 분모의 가상 1은 zero 이벤트 처리 편의이며 실제 타입 이벤트 하나가 아닙니다.',
  'global과 각 local의 init 반환을 확인한 뒤 사용하고 성공한 객체만 적절히 destroy합니다. 초기 events=1을 분자에 같은 값으로 중복 넣지 않으며 실패한 init 뒤 sequence·lock이 모두 완성됐다고 가정하지 않습니다.',
  'global과 local init의 amount·err 검사·초기화 순서를 읽으세요.',
  [('이벤트 전 초기 분자와 분모 값은?','local 0과 global 1이다','둘 다 1이다','분모 0 처리를 피하려는 가상 기준 1이며 각 타입의 실제 이벤트는 아직 0입니다.'),('per-CPU 할당 init이 실패하면?','해당 오류를 반환하고 이후 정상 초기화를 진행하지 않는다','항상 성공 0을 반환한다','err 검사 뒤 바로 반환합니다. 초기화 실패를 정상 객체 상태로 해석하지 않습니다.')],
  [('local lock','분자 period 반영을 보호하는 local raw lock과 underlying 카운터 내부 lock은 다른 객체입니다.'),('정리','global_destroy·local_destroy는 각 events의 percpu_counter_destroy를 호출합니다. 다른 접근을 끝내는 객체 수명 관리는 caller 책임입니다.')])
 lesson('감쇠 기간 전환·sum 뒤 set 대신 차이 더하기',c,'fprop_new_period',
  '합산과 상태 갱신 사이에 새 이벤트가 들어와도 이를 지우지 않는 감쇠 계산을 배웁니다.',
  '기존 합 E를 읽고 E>1일 때 periods<64면 제거량을 E-(E>>periods)로 계산합니다. 중앙 카운터에는 제거량의 음수를 add해 기존 이벤트만 감쇠합니다. 직접 set(E>>periods)를 하면 sum 이후 들어온 새 이벤트까지 덮어쓸 수 있습니다. periods>=64는 읽었던 E 전체를 제거합니다.',
  'nonnegative periods와 sane signed 이벤트 범위를 사용합니다. 새 이벤트를 현재 구간에 남기는 add 정책과 원래 E에만 적용하는 감쇠를 구분합니다. 기간 전환끼리 병렬 실행되지 않도록 caller가 직렬화해야 합니다.',
  'events 읽기·제거량 변환·음수 add를 추적하세요.',
  [('E=20을 읽은 뒤 새 이벤트 3개,periods=1이면?','읽은 20은 10으로 감쇠하고 새 3을 보존해 13이다','set을 사용해 새 3까지 지우고 10이다','원본은 제거량 10을 add로 뺍니다. 합산 이후의 새 이벤트가 덮어쓰기 때문에 사라지지 않게 합니다.'),('periods가 음수일 때 shift를 그대로 쓰는가?','아니며 nonnegative 기간 계약을 지킨다','음수 shift가 자동으로 과거를 복구한다','기간 인수는 유효한 감쇠 간격이어야 합니다. 음수 shift는 C 연산 계약을 벗어나며 복구 API가 아닙니다.')],
  [('큰 간격','64 이상에서는 E>>periods를 실행하지 않고 읽었던 E를 전부 제거합니다. 폭 밖 shift를 피하는 분기입니다.'),('동시 전환','원본 주석은 기간 전환 병렬 금지를 caller에게 요구합니다. seqcount가 writer끼리 직렬화하는 lock이라고 읽지 않습니다.')])
 lesson('비율 seqcount·기간 writer와 읽기 재시도',c,'fprop_fraction_percpu',
  '분자 감쇠와 분모의 기간이 섞이는 읽기를 재시도로 피하는 기술을 배웁니다.',
  '기간 전환은 preempt_disable_nested와 write_seqcount_begin/end로 sequence 구간을 만듭니다. fraction은 read_seqcount_begin 뒤 local 기간을 반영하고 분자·분모를 읽은 다음 read_seqcount_retry로 기간 변경을 확인해 반복합니다. 이벤트 add 자체는 같은 writer 구간을 만들지 않으므로 모든 이벤트 갱신의 atomic snapshot은 별도 보장하지 않습니다.',
  '이 helper가 제공하는 기간 일관성 범위를 이해하고 writer 직렬화·객체 수명·유효한 context를 외부에서 관리합니다. 재시도 구조를 일반 mutex와 구분하며 reader가 실제 local 반영 lock도 사용할 수 있음을 확인합니다.',
  'new_period의 writer 구간과 fraction의 do/while을 연결하세요.',
  [('분자·분모를 읽는 동안 기간 writer가 실행되면?','sequence 확인으로 읽기를 재시도한다','기존 결과를 무조건 확정해 반환한다','기간의 seqcount 변경을 검출해 다시 local 감쇠와 읽기를 수행합니다.'),('seqcount가 두 기간 writer를 자동 직렬화하는가?','아니며 caller가 병렬 전환을 막아야 한다','writer lock을 자동 할당해 모든 충돌을 막는다','원본 주석의 caller 직렬화 조건을 지킵니다. seqcount 재시도와 writer 상호 배제는 다른 역할입니다.')],
  [('preemption','writer가 홀수 sequence 상태로 멈춰 reader가 계속 재시도하는 상황을 고려하는 실행 context 장치입니다. IRQ·CPU 전역 정지와 같은 의미가 아닙니다.'),('event 갱신','local add와 global add는 별도 단계입니다. seqcount가 모든 event를 감싸지 않는 이유로 근사 읽기의 비율 보정이 필요합니다.')])
 lesson('기간 전환 반환 경계·0 간격과 감쇠 후 빈 상태',c,'fprop_new_period',
  '함수 설명과 실제 분기에서 성공 반환이 어느 시점 상태를 판단하는지 배웁니다.',
  '읽은 events<=1이면 false로 즉시 반환하고 period를 늘리지 않습니다. events>1이면 감쇠·period 갱신 후 true를 반환하며 새 합계를 다시 검사하지 않습니다. periods=0이면 제거량 0·period 증가 0이어도 그 경로는 true입니다. 큰 감쇠로 합이 0이 됐다면 다음 호출의 초기 검사에서 false가 됩니다.',
  'false를 감쇠가 이미 무의미한 상태를 감지하는 신호로 사용하되 true가 감쇠 후 양수 이벤트를 재검증했다는 뜻으로 확대하지 않습니다. caller의 주기 정책은 일반적으로 양수 간격을 선택합니다.',
  '초기 <=1과 끝 return true 사이에 재검사가 없는지 읽으세요.',
  [('events=2에서 periods=64로 한 번 감쇠한 반환은?','그 호출은 true이며 합은 0으로 갈 수 있다','감쇠 뒤 재검사해 반드시 false다','입구에서 2>1이라 실행 경로에 들어가며 끝에서 true를 반환합니다. 감쇠 후 재검사는 없습니다.'),('events>1에서 periods=0은?','제거량·기간 증가는 0이지만 실행 경로는 true다','항상 입구에서 false로 거절한다','0 간격의 식을 그대로 대입해 실제 분기를 읽습니다. 함수가 positive periods 여부를 별도 검사하지 않습니다.')],
  [('초기 기준','events=1의 가상 초기 분모만 남으면 false입니다. 이 호출에서 epoch를 무조건 증가시키는 타이머라고 읽지 않습니다.'),('문서와 분기','반환 설명의 목적을 이해하되 정확한 조건은 실제 입구와 출구로 확인합니다. 후속 검사와 같은 결과를 가정하지 않습니다.')])
 lesson('지연 감쇠·모든 타입 대신 접근한 분자만 갱신',c,'fprop_reflect_period_percpu',
  '많은 이벤트 타입을 매 기간 순회하지 않고 필요한 항목만 나중에 보정하는 기술을 배웁니다.',
  'reflect는 global period와 local period가 같으면 바로 반환합니다. 다르면 local raw lock을 잡고 local period>=관찰 period이면 다른 실행이 이미 반영했다고 판단해 반환합니다. 남은 경우 기간 차이에 맞게 분자 값을 줄이고 local period를 global 관찰값으로 갱신합니다.',
  '타입 이벤트 발생이나 비율 읽기 전에 reflect가 호출되는 연결을 읽습니다. unsigned period wrap 뒤 >= 비교가 무한 epoch를 완전히 처리한다고 가정하지 말고 caller가 지원 기간 범위·수명 정책을 관리합니다.',
  '같음 fast path·잠금 뒤 >= 재검사·period 대입을 읽으세요.',
  [('기간이 이미 같은 local 객체는?','잠금·감쇠 없이 fast return한다','매 호출마다 모든 타입을 절반으로 줄인다','lazy aging은 필요한 기간 차이만 반영합니다. 같은 epoch의 반복 접근이 값을 계속 줄이면 잘못된 감쇠입니다.'),('lock 대기 뒤 period를 다시 확인하는 이유는?','다른 실행이 먼저 감쇠했을 수 있기 때문이다','카운터 주소를 새로 할당하기 위해서다','두 실행이 같은 오래된 period를 보고 기다릴 수 있습니다. 재검사는 같은 기간을 중복 감쇠하는 문제를 피합니다.')],
  [('규모','global 전환은 모든 타입 목록을 순회하지 않습니다. 각 타입이 자기 last period를 기억해 접근 시 차이를 적용합니다.'),('wrap 전제','period는 unsigned int이고 단순 >= 비교를 사용합니다. 장기간 wrap 처리를 무조건 보장하는 별도 sequence 비교 알고리즘을 추가하지 않습니다.')])
 lesson('분자 감쇠의 근사 읽기·작은 값은 sum으로 재확인',c,'fprop_reflect_period_percpu',
  'batch 오차가 작은 분자를 지배할 때 더 정확한 합계를 선택하는 원리를 배웁니다.',
  '기간 차이가 BITS_PER_LONG보다 작으면 중앙 read를 얻고 val<nr_cpu_ids*PROP_BATCH이면 sum으로 다시 읽습니다. 제거와 남길 값의 차이 -val+(val>>gap)를 add_batch로 적용합니다. 큰 값은 근사 중앙값, 작은 값은 오차에 민감하므로 합산을 사용하는 정책입니다.',
  'PROP_BATCH=8*(1+ilog2(nr_cpu_ids))와 오차 경계의 CPU 규모를 계산합니다. nr_cpu_ids는 여기서 사용하는 CPU 번호 범위와 연결되며 online CPU 개수 함수와 같은 값을 항상 가정하지 않습니다.',
  'read→threshold→sum과 shift 차이 add를 읽으세요.',
  [('중앙 read가 오차 threshold보다 작으면?','per-CPU sum으로 다시 읽는다','항상 0으로 즉시 버린다','작은 값은 중앙 오차의 상대 비중이 커질 수 있어 합산으로 확인합니다.'),('nr_cpu_ids=4일 때 PROP_BATCH는?','8*(1+2)=24다','기본 percpu_counter_batch와 항상 같은 32다','ilog2(4)=2이므로 24입니다. 이 비율 local 카운터의 batch 정책과 기본 global batch를 구분합니다.')],
  [('변경 방식','set 대신 읽은 val에서 계산한 차이를 add합니다. 다른 event 갱신을 숫자 대입으로 덮어쓰는 방식과 다릅니다.'),('오차','근사 큰 값 경로는 이상적 모든 분자의 정확한 실수 감쇠와 동일한 값이라고 보장하지 않습니다. 수업은 구현 정책의 정확도·비용을 설명합니다.')])
 lesson('오래된 분자 완전 초기화·long 폭의 감쇠 한계',c,'fprop_reflect_period_percpu',
  '큰 기간 차이에서 폭 밖 shift 대신 분자 상태를 초기화하는 조건을 배웁니다.',
  'gap>=BITS_PER_LONG이면 reflect는 percpu_counter_set(local events,0)을 호출하고 local period를 갱신합니다. 이 구현의 정책 경계는 s64 카운터 폭이라는 일반 추정이 아니라 BITS_PER_LONG입니다. long32 구성은 gap32에서, long64는 gap64에서 이 초기화 경로를 선택합니다.',
  '플랫폼 폭과 큰 간격을 함께 확인하고 너무 오래된 타입의 과거를 버리는 정책으로 이해합니다. long32에서 큰 s64 이벤트가 수학적으로 아직 shift 뒤 남을 수 있어도 이 분기는 실제로 0을 선택합니다.',
  'gap 비교·else set과 마지막 period 대입을 읽으세요.',
  [('long32에서 gap=32의 실제 선택은?','로컬 카운터를 0으로 set한다','반드시 s64 값을 32만큼 shift해 남긴다','조건은 BITS_PER_LONG입니다. 저장형 s64만 보고 해당 플랫폼의 실제 분기를 바꾸어 설명하면 안 됩니다.'),('큰 간격 분기에서 local period는?','관찰한 global period로 갱신된다','항상 과거 period를 유지한다','분자 상태를 0으로 초기화한 뒤 epoch도 반영해야 다음 접근에서 같은 감쇠를 반복하지 않습니다.')],
  [('폭 밖 이동','shift 폭 경계를 우회하는 분기입니다. 매우 큰 gap을 shift 인수로 그대로 전달하지 않습니다.'),('기간 관리','period wrap이나 오래된 객체 접근에 대한 상위 계약과 별도로 이 분기의 폭 조건을 확인합니다.')])
 lesson('이벤트 분자·분모 동시 증가의 두 단계',c,'__fprop_add_percpu',
  '타입별 이벤트와 전체 이벤트를 같은 수량으로 기록하고 먼저 과거를 감쇠하는 방법을 배웁니다.',
  '__add는 local reflect를 먼저 실행하고 local events에 nr를 PROP_BATCH로 더한 다음 global events에 nr를 기본 add로 더합니다. 이벤트 발생 전에 지난 기간을 반영해야 새로운 nr가 과거 이벤트처럼 감쇠되지 않습니다. inc wrapper는 local_irq_save 구간에서 nr=1 호출 후 IRQ 상태를 복원합니다.',
  '지원되는 nonnegative event nr와 산술 범위를 지키고 직접 내부 add를 쓸 때 필요한 context 규약을 확인합니다. 한 event의 local/global 두 갱신이 모든 reader에 동시에 보이는 단일 atomic 트랜잭션이라고 읽지 않습니다.',
  'reflect→local add→global add와 header inc wrapper를 읽으세요.',
  [('local 과거 8이 한 기간 지났고 새 event 2면?','먼저 8을 4로 줄이고 2를 더해 6이다','먼저 10으로 만든 뒤 감쇠해 5다','새 이벤트를 현재 기간에 남기기 위해 reflect를 먼저 실행합니다. 연산 순서가 비율 기록 의미를 바꿉니다.'),('fprop_inc_percpu가 전달하는 nr는?','1이다','현재 online CPU 개수다','편의 wrapper는 한 이벤트를 기록합니다. CPU 수로 이벤트 수량을 자동 곱하는 API가 아닙니다.')],
  [('같은 수량','한 타입 이벤트는 그 타입 분자와 전체 분모에 같은 nr를 더합니다. 전체만 또는 local만 수정하면 비율의 의미가 깨집니다.'),('IRQ wrapper','IRQ save/restore는 현재 CPU 구간의 상태 관리입니다. 모든 CPU 이벤트를 동시에 잠그는 전역 트랜잭션이 아닙니다.')])
 lesson('비율 출력 보정·분모 양수와 1 이하 범위',c,'fprop_fraction_percpu',
  '근사 분자·분모가 잠시 어긋나도 유효한 분수 표현을 반환하는 조건을 배웁니다.',
  'fraction은 positive 중앙 read로 num과 den을 얻습니다. den<=num이면 num>0에서 den=num, 둘 다0이면 den=1로 보정합니다. 따라서 반환 denominator>0과 numerator<=denominator를 유지합니다. 두 unsigned long 출력 포인터에 정수 쌍을 쓰며 부동소수점 비율을 직접 반환하지 않습니다.',
  '출력 포인터를 유효하게 제공하고 0/1·7/7 같은 분수 쌍을 해석합니다. 보정은 유효한 범위 표현을 제공하지만 누락된 per-CPU 값을 모두 합산해 정확한 최근 비율로 복구하는 연산은 아닙니다.',
  'den<=num과 num 0 분기, 두 출력 대입을 읽으세요.',
  [('읽은 num=7,den=5의 출력은?','7/7로 보정한다','7/5를 항상 그대로 반환한다','근사 카운터 오차에서도 비율이 1을 넘지 않게 분모를 분자에 맞춥니다.'),('읽은 num=0,den=0의 출력은?','0/1이다','0/0이다','양수 분모를 만들기 위해 1로 보정합니다. 분수값은 0이고 나눗셈 0 분모를 피합니다.')],
  [('이름과 형식','floating proportions는 변화하는 비율 모델의 이름입니다. 구현이 float·double을 저장하는 것은 아닙니다.'),('폭 전제','s64 읽기를 unsigned long 출력에 전달합니다. 지원 이벤트 규모와 대상 long 폭을 함께 관리해야 값이 잘리는 범위를 피할 수 있습니다.')])
 lesson('최대 비율 예산·1024분율로 남은 이벤트 계산',c,'__fprop_add_percpu_max',
  '특정 타입이 차지할 비율을 고정소수점 제한과 cross multiplication으로 비교하는 방법을 배웁니다.',
  'FPROP_FRAC_SHIFT=10이고 BASE=1024입니다. max_frac<BASE이면 현재 num/den에서 tmp=den*max_frac-num*BASE를 계산합니다. tmp<0은 이미 제한을 넘었다는 뜻이라 반환합니다. 새 nr는 분자와 분모를 같이 늘리므로 남은 예산 조건은 nr*(BASE-max_frac)와 tmp를 비교해야 합니다.',
  '0..BASE의 max_frac와 nonnegative nr, 곱·shift·signed tmp의 sane 범위를 준비합니다. max_frac=BASE는 별도 제한 계산 없이 add하며 분모가 같이 늘어나는 효과를 빠뜨리지 않습니다.',
  '두 cross product와 BASE-max_frac 인자를 읽으세요.',
  [('max_frac=512의 뜻은?','512/1024인 절반 비율이다','512개 이벤트의 고정 개수 제한이다','저장된 수는 고정소수점 비율입니다. 이벤트 개수와 분자·분모 비율을 구분합니다.'),('새 이벤트 제한식에 BASE-max_frac가 있는 이유는?','새 nr가 분자뿐 아니라 전체 분모도 증가시키기 때문이다','분모는 언제나 고정 상수 1024이기 때문이다','(num+nr)/(den+nr)를 제한과 비교해 정리한 식입니다. 분모 변화를 제외한 nr*BASE 비교와 다릅니다.')],
  [('표현 한계','헤더는 ULLONG_MAX>>SHIFT 계열의 이벤트 상한을 경고합니다. 곱·left shift와 signed tmp 변환·div_u64 divisor의 지원 범위를 함께 확인합니다.'),('이미 초과','tmp<0에서는 nr를 0으로 바꿔 계속하는 것이 아니라 그대로 반환합니다. 이 호출에서 reflect·실제 add가 수행되는 경로와 구분합니다.')])
 lesson('최대 비율 포화 반올림·ceil로 인한 한 이벤트 차이',c,'__fprop_add_percpu_max',
  '제한 근처의 정수 이벤트 수를 올림으로 선택하는 실제 정책과 엄밀한 상한 차이를 배웁니다.',
  'tmp가 요청 예산보다 작으면 nr=div_u64(tmp+BASE-max_frac-1,BASE-max_frac)로 올림 나눗셈합니다. 이 ceil 정책은 분수 상한을 한 이벤트 단위로 조금 넘을 수 있어 정확한 실수 상한 floor 제한과 다릅니다. 근사 카운터의 num/den 기반 판단까지 함께 고려해야 합니다.',
  'num=1,den=5,max_frac=341,요청4에서 tmp=681,divisor=683,ceil=1을 계산합니다. 최종2/6은341/1024보다 조금 큽니다. helper를 엄밀한 quota나 완전한 비율 상한 API로 사용하는 가정을 검토합니다.',
  'tmp+divisor-1의 ceil 식과 마지막 __add 호출을 읽으세요.',
  [('tmp=681,divisor=683의 포화 nr는?','ceil 값 1이다','floor 값 0이다','원본은 tmp+divisor-1을 나누는 올림식입니다. 엄밀한 상한 유지에 필요한 floor 식과 다른 정책입니다.'),('이 반올림을 정확한 실수 비율 상한 보장으로 읽는 것은?','근사 읽기와 ceil 정책 때문에 조건을 확인해야 한다','모든 상태에서 한 bit 오차도 없는 상한 보장이다','정수 이벤트 granularity와 근사 카운터를 고려해야 합니다. 원본에서 관찰되는 ceil 정책을 floor 보장으로 바꾸어 설명하지 않습니다.')],
  [('0 예산','tmp=0이고 제한 BASE 미만이면 nr가 0이 될 수 있습니다. __add의 reflect와 zero amount 흐름도 읽습니다.'),('파일 전체','전역·로컬 init/destroy·new period·PROP_BATCH·lazy reflect·event add·fraction·max 제한과 header의 구조체/상수/decl/inc를 열두 수업에서 모두 연결합니다.')])
