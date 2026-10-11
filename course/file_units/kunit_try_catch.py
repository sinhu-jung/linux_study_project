"""Whole-file KUnit try/catch interface, initialization and worker execution."""
ROWS = [dict(
    path='include/kunit/try-catch.h', title='KUnit try/catch 계약: assertion의 전제와 중단',
    intro='실패 가능한 테스트 callback의 문맥·결과·중단 인터페이스 전체를 분석합니다.',
    principle='전제가 깨진 테스트는 후속 검증을 계속하는 대신 제어 흐름을 종료하고 복구 경로로 이동할 수 있습니다.',
    use='함수 포인터, opaque context, 상태 객체와 noreturn 선언을 학습합니다.',
    area='테스트 설계 · 제어 흐름 · callback · 상태 표현',
    sections=[
        ('타입과 상태', 'GPL-2.0 guard에서 linux/types.h를 포함하고 kunit을 전방 선언합니다. kunit_try_catch_func_t는 void *를 받고 void를 반환하는 함수 포인터입니다. 구조체의 내부 필드는 test,int try_result,try와 catch callback,void *context입니다. 두 callback에 같은 형태의 사용자 문맥을 전달할 수 있습니다.'),
        ('Assertion의 논리', '문서는 assertion을 테스트의 전제,expectation을 만족해야 하는 결론으로 설명합니다. 전제가 틀리면 후속 검증을 계속해도 의미가 없으므로 throw로 try를 중단합니다. 단순히 모든 검증 실패를 동일한 흐름으로 처리하는 설계가 아닙니다. 이 헤더는 architecture independent 인터페이스를 제공하며 구체적인 worker 구현은 별도입니다.'),
        ('Run과 throw 선언', 'run은 상태 객체와 context를 받고 void를 반환합니다. throw는 __noreturn void로 선언되어 호출 지점 이후로 정상 복귀하지 않는 계약입니다. C++ exception 문법이나 setjmp 저장소는 여기에 없습니다. catch 호출을 구현하는 것은 run 쪽이므로 이 선언만 보고 같은 스택에서 catch가 실행된다고 추론할 수 없습니다.'),
        ('결과 조회와 범위', 'get_result는 try_result를 그대로 읽어 int를 반환하는 inline 함수입니다. 값을 초기화·정규화하거나 참조를 획득하거나 잠금을 잡지 않습니다. 실행 완료 및 동기화 시점은 호출부 계약을 따라야 합니다. 문서·구조체·callback typedef·두 선언·조회 helper와 guard 전체를 검토했습니다.')
    ], questions=[
        ('Assertion 전제가 깨졌을 때 try를 중단하는 이유는?', '그 전제를 필요로 하는 후속 검증의 의미가 사라지기 때문이다', '모든 expectation도 반드시 프로세스를 종료해야 하기 때문이다', '문서는 전제와 결론을 구분합니다. assertion은 중단하며 expectation 일반을 같은 제어 흐름으로 가정하지 않습니다.'),
        ('get_result가 하는 일은?', 'try_result 필드를 그대로 반환한다', '테스트를 실행하고 결과를 0으로 초기화한다', '실행은 run,조회는 get_result입니다. 이 inline 함수에는 동기화나 초기화도 없습니다.'),
        ('throw의 __noreturn은 무엇을 뜻하는가?', '정상적으로 호출 다음 명령으로 돌아오지 않는 계약이다', '반환값이 항상 음수라는 뜻이다', '반환 타입은 void입니다. noreturn은 반환값이 아닌 제어 흐름에 관한 선언입니다.')
    ]
), dict(
    path='lib/kunit/try-catch-impl.h', title='KUnit try/catch 초기화: callback 연결과 실행 상태의 경계',
    intro='내부 초기화 helper의 모든 대입과 초기화하지 않는 필드를 확인합니다.',
    principle='이름이 init인 함수라도 객체의 모든 필드를 초기화하는지는 실제 본문으로 확인해야 합니다.',
    use='객체 초기화 범위와 이후 실행 단계의 책임을 구분합니다.',
    area='초기화 · 함수 포인터 · API 계약',
    sections=[
        ('헤더 구성', 'GPL-2.0 내부 헤더는 _KUNIT_TRY_CATCH_IMPL_H guard,공개 kunit/try-catch.h와 linux/types.h include,struct kunit 전방 선언으로 구성됩니다. 주석상 테스트와 내부 구현이 공유하는 인터페이스입니다.'),
        ('대입 세 개', 'static inline kunit_try_catch_init은 상태 객체,test,try,catch를 받습니다. 본문은 try_catch->test=test,try_catch->try=try,try_catch->catch=catch 세 대입입니다. callback을 즉시 실행하거나 worker를 생성하지 않습니다.'),
        ('미초기화 필드와 책임', 'try_result와 context는 이 helper에서 설정하지 않습니다. 별도로 확인한 run이 실행 시작 때 context와 결과를 설정합니다. init 직후 get_result를 호출해 무조건 0을 기대하면 안 됩니다. NULL callback 검사나 실패 반환도 없고 반환 타입은 void입니다. 선언과 전체 본문을 대조했습니다.')
    ], questions=[
        ('init 호출만으로 try_result=0이 보장되는가?', '아니다. 이 helper는 그 필드를 쓰지 않는다', '그렇다. 구조체의 모든 바이트를 지운다', '대입은 test,try,catch 세 필드뿐입니다. 함수 이름보다 실제 쓰기 집합이 초기화 범위를 결정합니다.'),
        ('init은 try callback을 언제 호출하는가?', '여기서는 호출하지 않고 주소만 저장한다', 'catch를 실행한 직후 호출한다', '함수 포인터 대입과 간접 호출은 다른 동작입니다. 테스트 실행은 run의 책임입니다.')
    ]
), dict(
    path='lib/kunit/try-catch.c', title='KUnit 중단 실행기: kthread·completion·오류 상태 전이',
    intro='worker 생성부터 종료 대기, 명시적 throw와 fault·timeout 처리까지 파일 전체를 분석합니다.',
    principle='worker 종료와 테스트의 논리적 결과를 별도로 표현하고 종료 동기화 후 복구 callback을 호출합니다.',
    use='completion, task 참조, sentinel 오류값, 협력적 스레드 중단과 timeout의 한계를 학습합니다.',
    area='동시성 · 상태 머신 · 오류 처리 · 스레드 수명 · 타임아웃',
    sections=[
        ('구성과 명시적 throw', 'GPL-2.0 파일은 test,completion,kernel,kthread,sched/task와 내부 초기화 헤더를 포함합니다. kunit_try_catch_throw는 try_result=-EFAULT를 기록하고 kthread_exit(0)으로 현재 worker를 종료하며 GPL export됩니다. kthread 종료 코드 0과 try_result의 -EFAULT는 다른 상태 저장 경로입니다. throw 안에서 catch를 직접 호출하지 않습니다.'),
        ('Worker adapter의 sentinel', 'adapter는 void *data를 try_catch로 해석하고 try_result=-EINTR를 먼저 저장한 뒤 try(context)를 호출합니다. callback이 정상 반환한 후 여전히 -EINTR이면 0으로 바꿉니다. callback이 다른 결과를 썼다면 그대로 유지합니다. 중간에 종료되어 후처리가 실행되지 않으면 sentinel이 남아 fault 경로를 구분하는 데 쓰입니다. adapter 자체의 정상 반환은 0입니다.'),
        ('고정 timeout', 'timeout helper는 300*msecs_to_jiffies(MSEC_PER_SEC)를 반환해 5분 대기를 설정합니다. 긴 주석은 테스트 크기별 timeout 등을 미래 논의로 적지만 현재 크기 분류별 분기는 없습니다. 시간 단위 milliseconds에서 jiffies로 변환하는 것과 실제 wait가 반환하는 잔여 ticks를 구분해야 합니다.'),
        ('실행 준비와 생성 실패', 'run은 상태의 test를 지역 변수로 가져오고 context를 저장하고 try_result=0으로 초기화합니다. kthread_create에 adapter,상태 포인터와 고정 이름을 전달합니다. IS_ERR이면 PTR_ERR를 결과에 저장하고 catch(context)를 호출한 뒤 바로 반환합니다. 이 경로에는 task 참조 획득이나 worker wakeup이 없으며 아래 공통 오류 로그 분기에도 도달하지 않습니다.'),
        ('Task 참조와 completion 주소', '생성 성공 후 get_task_struct로 참조를 보유합니다. 주석은 task->vfork_done이 내부 kthread->exited를 가리키며 종료 시 NULL로 바뀌므로 task_done 지역 변수에 주소를 복사한다고 설명합니다. 이 복사를 한 뒤 wake_up_process로 시작합니다. 종료 이후 task->vfork_done을 다시 읽어 기다리는 순서가 아닙니다.'),
        ('대기와 timeout 후 stop', 'wait_for_completion_timeout(task_done,timeout)의 결과를 time_remaining에 저장합니다. 0이면 try_result=-ETIMEDOUT로 쓰고 kthread_stop을 호출합니다. stop의 반환값을 결과에 대입하지 않습니다. kthread_stop은 임의의 코드를 강제로 없애는 기능이 아니므로 try가 영원히 반환하지 않는 상황에서 5분이 run의 엄격한 상한이라고 설명할 수 없습니다. timeout은 대기 만료 후 stop을 요청하는 분기입니다.'),
        ('참조 반환과 결과 확인', '대기 및 필요한 stop 뒤 put_task_struct하고 try_result를 exit_code로 복사합니다. 0이면 catch 없이 반환합니다. worker가 정상 반환했는지와 모든 assertion·expectation의 종합 성공 여부는 다른 계층일 수 있으므로 이 0을 전체 테스트 성공의 유일한 지표라고 단정하지 않습니다.'),
        ('명시적 중단의 정규화', 'exit_code=-EFAULT이면 try_result를 0으로 바꾼 후 마지막 catch를 호출합니다. 따라서 catch가 결과를 조회할 때 원래 throw sentinel 대신 0을 봅니다. throw는 의도된 제어 흐름이고 실행기 자체의 예외 오류로 남기지 않는 처리입니다. 별도 테스트 실패 상태까지 이 코드가 성공으로 되돌리는 것은 아닙니다.'),
        ('Fault와 timeout 로그', 'exit_code=-EINTR이면 test->last_seen.file 존재 여부에 따라 마지막 파일·줄을 포함한 try faulted 또는 짧은 메시지를 기록합니다. -ETIMEDOUT이면 try timed out을 기록합니다. 그 밖의 nonzero는 Unknown error와 정수 코드를 기록합니다. 이들 분기는 결과를 0으로 바꾸지 않고 catch(context)로 이어집니다.'),
        ('실행 문맥과 동시성 한계', 'try는 새 kthread에서 실행되고 catch는 run을 호출한 경로에서 실행됩니다. 지역 context 자체를 복제하거나 참조 카운팅하지 않으므로 실행 및 복구가 끝날 때까지 저장소가 유효해야 합니다. timeout 직후 worker도 결과를 변경할 수 있는 경계까지 별도 원자적 상태 머신으로 막는 코드는 없습니다. completion 종료 동기화와 임의 동시 쓰기 안전성을 혼동하지 않습니다.'),
        ('전체 흐름 검토', 'throw,adapter,timeout helper,run의 생성 오류·정상 종료·명시적 중단·fault·timeout·기타 오류와 두 GPL export를 모두 대조했습니다. C++ stack unwinding이나 일반 객체 destructor 실행을 구현하는 코드가 아닙니다. 실제 커널 스레드 fault와 5분 대기 실험을 실행하지 않았으며 내용 검증은 고정 소스 분석입니다.')
    ], questions=[
        ('throw는 catch를 어디서 직접 호출하는가?', 'throw 안에서는 호출하지 않는다. run이 종료 결과를 보고 호출한다', 'kthread_exit 다음 줄에서 호출한다', 'throw는 -EFAULT 저장 후 noreturn 종료입니다. catch 실행은 run의 공통 오류 처리 끝에 있습니다.'),
        ('try가 정상 반환하고 결과가 여전히 -EINTR이면?', 'adapter가 0으로 바꾼다', '무조건 timeout으로 바꾼다', '진입 전 -EINTR는 미완료 sentinel이며 정상 반환 후 동일할 때만 지웁니다. 다른 오류값은 보존합니다.'),
        ('kthread_create가 실패한 경우 결과와 복구는?', 'PTR_ERR를 저장하고 catch를 호출해 반환한다', 'wake_up_process를 호출한 뒤 정상 성공으로 처리한다', 'IS_ERR 분기는 생성된 task를 가정하지 않고 즉시 복구합니다. 공통 하단 로그 분기와도 다릅니다.'),
        ('vfork_done 주소를 wakeup 전에 복사하는 이유는?', '종료 시 task의 필드가 NULL로 바뀌므로 기다릴 completion 주소를 보존하려고', 'completion 내용을 문자열로 출력하려고', '소스 주석이 내부 kthread->exited와 필드 변경을 설명합니다. 주소 보존과 task 참조 획득이 함께 나타납니다.'),
        ('throw 뒤 catch에서 try_result를 읽으면 일반적으로 어떤 값인가?', 'run이 정규화한 0이다', '항상 -EFAULT가 그대로다', 'exit_code 지역 변수는 -EFAULT지만 저장 필드는 catch 전 0으로 변경됩니다. 지역 snapshot과 객체 상태를 구분합니다.'),
        ('5분 timeout이 있으면 어떤 try 코드도 정확히 5분 안에 run에서 벗어나는가?', '그렇게 보장할 수 없다. 만료 후 kthread_stop도 종료를 기다릴 수 있다', '그렇다. kthread_stop이 즉시 모든 명령을 강제 제거한다', '대기 timeout과 worker의 협력적 종료는 별개입니다. 원본 코드의 stop 호출을 강제 kill로 해석하면 안 됩니다.'),
        ('정상 exit_code=0이면 catch가 실행되는가?', '아니다. catch 호출 전에 return한다', '그렇다. 모든 종료 경로에서 무조건 호출한다', '생성 실패와 nonzero 결과에서는 catch를 호출하지만 정상 0은 조기 반환합니다. 따라서 catch를 모든 경우의 finally로 보아서는 안 됩니다.')
    ]
)]
