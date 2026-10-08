"""Code transformation, energy control and diagnostic mechanisms."""
def register(topic,q,detail):
    topic('BPF JIT·검증된 바이트코드를 머신 코드로','빌드·초기화','arch/x86/net/bpf_jit_comp.c','bpf_int_jit_compile',
      'BPF 프로그램을 매번 해석하는 대신 CPU 명령으로 실행하면 반복 처리 비용을 줄일 수 있습니다.',
      'JIT는 BPF 명령·레지스터·분기를 대상 ISA로 번역합니다. 분기 길이와 주소를 계산하기 위해 여러 pass를 수행하고 생성한 코드를 실행 가능 상태로 준비합니다. Verifier가 허용한 프로그램이어도 JIT 구현은 그 의미와 보안 조건을 정확하게 보존해야 합니다.',
      '지원 아키텍처의 JIT 설정을 조회하고 bpftool로 xlated와 jited 결과를 비교합니다. Verifier 실패와 JIT 실패를 구분하며 생성 코드의 주소·상수 blinding·실행 메모리 정책을 확인합니다.',
      'bpf_int_jit_compile의 addrs·pass·proglen·image와 do_jit를 연결하세요.',
      q('BPF Verifier와 JIT의 역할은 같은가?','허용성 검증과 머신 코드 번역을 구분한다','둘 다 단순 문자열 검색만 한다','Verifier는 프로그램의 안전한 실행 조건을 검사하고 JIT는 의미를 보존해 CPU 코드로 옮깁니다. 두 구현 모두 올바른 경계가 필요합니다.'),
      q('분기 명령 길이가 배치에 영향을 주면 JIT에 무엇이 필요한가?','주소·길이를 안정화하는 여러 pass','모든 분기를 임의 주소로 연결','번역 길이가 달라지면 이후 명령의 주소도 달라집니다. 반복 계산과 최종 검증으로 올바른 타깃을 맞춥니다.'),
      details=[detail('레지스터 매핑','BPF의 논리 레지스터를 x86 레지스터·스택에 대응합니다. 호출 규약·보존 레지스터·helper 호출과 반환값을 맞춰야 합니다. 명령 하나씩 비슷한 연산으로 바꾸기만 하면 충분하지 않습니다.'),detail('실행 메모리','생성 중 쓰기 가능한 메모리와 실행할 코드의 보호 규약을 구분합니다. 실패하면 준비한 image·주소 배열·보조 상태를 정리하고 잘못된 일부 코드를 실행하지 않아야 합니다.')])

    topic('Rust·커널 수명과 안전 추상화','언어·확장','rust/kernel/types.rs','pub struct ARef',
      '커널 객체의 참조 수명과 해제를 타입으로 표현하면 실수하기 쉬운 수명 관리를 일부 자동화할 수 있습니다.',
      'Rust 커널 추상화의 ARef는 AlwaysRefCounted 객체의 소유 참조를 표현합니다. Clone은 참조를 늘리고 Drop은 줄이며 Deref는 접근을 제공합니다. Unsafe trait 구현과 C FFI 경계는 실제 객체 수명·불변식을 보장해야 하므로 Rust 타입만으로 커널 전체가 자동 안전해지지는 않습니다.',
      '지원 CONFIG_RUST·toolchain·문서를 확인하고 safe API와 unsafe 구현의 계약을 구분합니다. 빌린 &T와 소유 참조 ARef<T>, raw pointer를 다르게 읽습니다. Linux v6.12의 Rust 지원 범위를 이후 버전과 혼동하지 않습니다.',
      'ARef의 Clone·Deref·Drop과 AlwaysRefCounted의 inc_ref·dec_ref 계약을 연결하세요.',
      q('ARef의 Clone과 Drop이 참조 수명에서 수행해야 하는 것은?','Clone은 참조 증가, Drop은 참조 감소','둘 다 객체를 무조건 즉시 삭제','소유 참조 복사와 해제는 refcount 계약을 따릅니다. 마지막 참조가 끝나는 실제 객체 정리는 구현의 불변식에 연결됩니다.'),
      q('Rust의 unsafe 경계를 보면 어떤 판단이 필요한가?','구현이 요구하는 수명·동시성 불변식을 확인한다','unsafe라는 단어만 있으면 아무 검사가 필요 없다','Unsafe는 안전 조건을 사람이 추가로 보장해야 하는 경계입니다. 안전한 외부 API를 제공하려면 내부 계약이 정확해야 합니다.'),
      details=[detail('빌림과 소유','&T는 허용된 수명 동안 객체를 빌립니다. ARef<T>는 refcount로 소유 참조를 유지합니다. raw pointer의 존재만으로 객체가 살아 있다는 증거가 생기지 않습니다. C 객체와 연결할 때 이 차이가 핵심입니다.'),detail('Drop과 실패 경로','RAII는 scope 종료·오류 반환 때 정리를 연결하지만 장치 비동기 작업의 완료까지 자동 결정하지 않습니다. 작업이 객체를 계속 참조한다면 그 작업 수명 동안 별도 참조가 유지되어야 합니다.')])

    topic('Livepatch·실행 중 함수 교체','빌드·초기화','kernel/livepatch/core.c','klp_enable_patch',
      '커널을 재부팅하지 않고 일부 함수를 바꾸려면 실행 중인 작업과 상태의 일관성을 유지해야 합니다.',
      'Livepatch는 기존 함수 호출을 새 구현으로 전환하며 task별 transition으로 안전한 경계를 관리합니다. 대상 모듈·함수·아키텍처 지원·호환 상태를 확인해야 합니다. 임의의 전역 자료구조 레이아웃 변경을 실행 중 함수 교체만으로 안전하게 해결할 수는 없습니다.',
      '지원 커널의 livepatch module과 sysfs 상태를 확인합니다. 패치 전환·적용 실패·대상 모듈 수명·복귀 가능성을 검토하고 격리된 VM에서 시험합니다. 패치 적용 시작과 모든 task 전환 완료를 구분합니다.',
      'klp_enable_patch의 module 검사·object 준비와 transition 상태를 읽으세요.',
      q('Livepatch 적용 시작이 즉시 모든 task의 안전한 전환 완료와 같은가?','task별 전환 상태와 완료를 확인해야 한다','함수 주소만 바꾸면 항상 모두 완료다','실행 중 stack과 함수 의미의 일관성을 관리해야 합니다. Transition이 끝났는지 별도 상태를 확인합니다.'),
      q('Livepatch로 임의의 객체 메모리 레이아웃 변경을 항상 해결할 수 있는가?','이미 존재하는 상태와 호환성 설계가 필요하다','함수 교체면 어떤 layout 변경도 자동 안전하다','기존 객체의 상태·호출 중 문맥은 남아 있습니다. 새 구현이 기존 상태를 올바르게 해석하도록 별도 설계해야 합니다.'),
      details=[detail('함수 전환과 Task','옛 함수와 새 함수가 상태를 다르게 해석한다면 중간 실행에서 섞이면 안 됩니다. Stack 검사와 일관성 모델로 각 task의 적용 경계를 정합니다.'),detail('대상 수명','klp_object와 klp_func는 대상과 대체 함수를 설명합니다. 모듈 unload·symbol 해석·패치 module 참조를 함께 관리해야 실행할 주소가 사라지지 않습니다.')])

    topic('Static Key·분기 비용 조절','빌드·초기화','kernel/jump_label.c','static_key_slow_inc_cpuslocked',
      '거의 바뀌지 않는 기능 상태를 hot path에서 매번 변수로 읽는 비용을 줄이고 싶을 수 있습니다.',
      'Static key는 jump label 위치의 명령을 바꿔 비활성 경로를 NOP 등으로 처리합니다. 상태 변경은 느린 patch 경로에서 수행하고 참조·CPU·코드 변경 동기화를 맞춥니다. 각 실행에서 변수 검사 비용을 줄이는 대신 상태 변경 비용과 제약이 생깁니다.',
      'DEFINE_STATIC_KEY와 static_branch 규약을 따릅니다. 활성화 참조 증가·감소를 균형 있게 관리하고 잠금 문맥·CPU hotplug 제약을 확인합니다. 수시로 바뀌는 값의 범용 비교를 대신하는 기법으로 쓰지 않습니다.',
      'static_key_slow_inc_cpuslocked의 fast_inc·jump_label_mutex·진행 중 상태를 읽으세요.',
      q('Static key의 주된 절충은?','자주 실행하는 분기 비용을 줄이고 상태 변경 비용을 감수한다','모든 상태 변경이 무료다','코드를 바꾸는 느린 경로와 hot path의 빠른 실행을 구분합니다. 드물게 바뀌는 기능에 특히 적합합니다.'),
      q('enable 참조를 증가시켰다면 대응 감소를 무시해도 되는가?','수명과 enable 참조를 균형 있게 관리한다','참조는 아무 의미가 없다','여러 사용자의 활성 요구를 추적하므로 불균형은 기능 상태와 수명을 잘못 유지할 수 있습니다.'),
      details=[detail('Code patch','분기 위치를 기록한 테이블에서 NOP·jump를 안전하게 바꿉니다. 데이터 bool 하나를 저장하는 것과 달리 실행 중 CPU가 명령을 관찰하는 규약이 필요합니다.'),detail('Concurrent 변경','동시에 inc·dec하는 호출은 patch 완료와 상태를 맞춰야 합니다. 진행 중 enabled 상태와 mutex가 왜 있는지 보세요. CPU 관련 lock을 보유해야 하는 API 이름도 계약의 일부입니다.')])

    topic('Static Call·간접 호출 최적화','빌드·초기화','kernel/static_call_inline.c','__static_call_update',
      '여러 구현 중 하나로 드물게 바뀌는 호출을 hot path에서 함수 포인터로 매번 처리하는 비용을 줄일 수 있습니다.',
      'Static call은 등록된 호출 지점이나 trampoline을 수정해 선택 함수를 직접 호출하는 형태를 활용합니다. 대상 변경은 patch 동기화와 모듈 수명 조건을 지켜야 합니다. Static key의 분기 선택과 static call의 호출 대상 선택은 다른 목적입니다.',
      'DEFINE_STATIC_CALL·static_call·static_call_update API와 해당 아키텍처 지원을 확인합니다. 대상 함수의 signature와 객체 수명, CPU 실행과 코드 갱신 경계를 맞춥니다.',
      '__static_call_update의 key·tramp·func와 module site 갱신을 읽으세요.',
      q('Static key와 static call이 주로 바꾸는 것은?','분기 상태와 호출 대상을 각각 바꾼다','둘 다 파일 권한만 바꾼다','Static key는 feature 분기, static call은 지정 함수로의 호출을 최적화하는 경로입니다. API와 계약을 구분합니다.'),
      q('호출 대상을 바꿀 때 함수 signature가 맞지 않아도 주소만 유효하면 되는가?','호출 규약과 signature를 맞춰야 한다','어떤 함수든 안전하게 호출된다','인수와 반환값·호출 규약이 맞아야 합니다. 실행 주소의 존재만으로 타입·수명 계약이 충족되지 않습니다.'),
      details=[detail('Call site와 Trampoline','지원 방식에 따라 직접 call site와 trampoline의 변환이 관련됩니다. 어느 곳을 바꾸는지와 fallback을 확인해야 간접 호출 비용이 어디서 줄어드는지 이해합니다.'),detail('모듈과 동기화','대상이 module에 있으면 unload 중 호출 방지가 필요합니다. 주소 변경·실행 중 코드 patch·모듈 참조의 규약은 서로 연결되지만 같은 작업은 아닙니다.')])

    topic('Clock Framework·주파수 트리','전원','drivers/clk/clk.c','clk_set_rate',
      '장치 동작 주파수는 부모 클록과 divider·PLL 관계를 통해 결정되어 의존성을 관리해야 합니다.',
      'Common clock framework는 부모·자식 clock tree와 provider 연산을 관리합니다. 요청 rate를 하드웨어 가능한 값으로 협상하고 parent 변경·분주·전환을 적용합니다. prepare와 enable은 문맥·동기화 규약이 다르며 여러 소비자의 요구가 공유될 수 있습니다.',
      '장치가 얻은 clk의 prepare_enable·set_rate·disable_unprepare 등 수명을 맞춥니다. 요구한 rate와 실제 clk_get_rate 결과를 구분하고 독점·notifier·provider 오류를 처리합니다.',
      'clk_set_rate의 prepare lock과 clk_core_set_rate_nolock·exclusive_count를 읽으세요.',
      q('100MHz를 요청하면 하드웨어가 언제나 정확히 100MHz를 만드는가?','가능한 rate와 실제 반환·조회 값을 확인한다','모든 divider가 어떤 실수값도 지원한다','PLL·divider가 허용하는 값과 parent 제약이 있습니다. 요청값과 실제 설정은 다를 수 있습니다.'),
      q('여러 장치가 같은 parent clock을 공유할 때 rate 변경은 누구에게 영향을 줄 수 있는가?','그 parent를 사용하는 다른 장치','항상 호출자 한 객체에만 국한된다','Clock tree의 부모 rate는 자식 출력에 영향을 줍니다. 요구 협상과 exclusive·notifier 규약이 필요합니다.'),
      details=[detail('Divider 계산','단순 모델에서 parent=400MHz, divider=4이면 출력=100MHz입니다. Divider를 8로 바꾸면 50MHz입니다. 실제 provider는 정수 제약·rounding·PLL lock 시간까지 처리합니다.'),detail('Enable의 수명','Clock을 켰다는 참조가 여러 사용자에서 겹칠 수 있습니다. 한 장치의 종료가 다른 사용자의 clock을 끄지 않도록 count·수명 규약을 지킵니다.')])

    topic('Regulator·전압과 공급 의존','전원','drivers/regulator/core.c','regulator_enable',
      '장치 전원은 여러 소비자가 공유하거나 다른 공급에 의존하므로 단순 GPIO 한 번으로 관리되지 않을 수 있습니다.',
      'Regulator framework는 전압·전류 제약과 공급 의존·사용자 참조를 관리합니다. Enable은 상위 공급과 provider 상태를 맞추고 disable은 실제 사용 중인 다른 소비자를 고려합니다. 전압 변경·settling 시간·enable 상태는 서로 다른 조건입니다.',
      'regulator_get·전압 범위 요청·enable·disable·put 수명을 따릅니다. 공급 트리와 공유 사용자 제약을 확인하고 오류·deferred probe를 처리합니다. 임의 전압 변경을 실제 하드웨어에서 실험하지 않습니다.',
      'regulator_enable의 dependent lock과 _regulator_enable의 supply·use_count를 연결하세요.',
      q('공유 regulator를 한 소비자가 disable하면 언제나 즉시 물리 전원이 꺼져야 하는가?','다른 사용자의 참조와 제약을 고려한다','다른 장치 상태는 모두 무시한다','Framework는 공유 수명과 의존성을 관리합니다. 소비자 요청과 실제 provider enable 상태의 관계를 구분합니다.'),
      q('지원 전압 범위 밖의 요청도 무조건 적용하는 것이 옳은가?','소비자·provider 제약과 반환 오류를 확인한다','요청 숫자면 언제나 안전하다','공급 가능한 범위와 장치 요구가 겹쳐야 합니다. 전압은 기능·안전 제약이 있으므로 무검증 숫자 적용이 아닙니다.'),
      details=[detail('Dependency 잠금','상위 supply를 포함한 여러 regulator lock을 획득할 때 순서와 교착 회피가 필요합니다. ww_acquire_ctx와 dependent lock은 전압 계산 함수와 다른 동시성 역할을 합니다.'),detail('Probe와 전원 준비','공급 provider가 아직 준비되지 않으면 probe를 미뤄야 할 수 있습니다. Device tree 연결과 수명 해제, 실패 뒤 disable 균형을 함께 읽으세요.')])

    topic('Devfreq·장치 동작 주파수','전원','drivers/devfreq/devfreq.c','devfreq_update_target',
      'CPU 외 장치도 작업량에 맞춰 주파수와 전압을 조절하면 성능과 소비 전력을 조절할 수 있습니다.',
      'Devfreq governor는 장치 상태를 보고 목표 rate를 고르고 framework는 최소·최대와 QoS·thermal 제약에 맞춥니다. Provider target이 지원 OPP로 전환합니다. 요청값·허용 범위·실제 상태를 구분하며 CPU의 cpufreq와 별도 장치 인터페이스입니다.',
      '지원 장치의 devfreq sysfs에서 governor·주파수·상태를 조회합니다. 바뀐 처리량·지연·전력·온도를 함께 관찰하고 장치 OPP와 전압 전환 규약을 따릅니다.',
      'devfreq_update_target의 governor get_target_freq→range→target 흐름을 읽으세요.',
      q('governor가 고른 rate가 최대 제약을 넘으면 그대로 무조건 적용하는가?','허용 범위와 실제 OPP 조건을 맞춘다','제약은 항상 무시된다','목표 선택 뒤 min·max 범위를 확인합니다. 소비자 QoS와 thermal 한계 등이 실제 적용에 영향을 줍니다.'),
      q('주파수를 낮추면 모든 작업의 총 에너지가 항상 줄어드는가?','실행 시간·전압·대기 전력을 함께 평가한다','주파수 숫자만 낮으면 반드시 최소 에너지다','시간이 늘어나는 비용과 voltage·동적 전력·idle 특성을 함께 봐야 합니다. 성능과 에너지 관계는 환경에 따라 달라집니다.'),
      details=[detail('OPP','Operating performance point는 가능한 주파수·전압 등의 조합입니다. 임의 rate를 요청해도 provider는 지원 조합을 찾아야 합니다. 전압과 clock 전환 순서가 안정성에 관련됩니다.'),detail('Lock의 역할','update_target은 devfreq lock이 잡힌 조건을 요구합니다. governor 부재·target 실패를 처리하고 상태 통계가 실제 성공한 전환과 일치하게 관리합니다.')])

    topic('Thermal·온도와 Cooling Policy','전원','drivers/thermal/thermal_core.c','thermal_zone_device_update',
      '온도가 높아지면 센서 관찰과 냉각 장치 제어를 연결해 기능과 하드웨어 상태를 보호해야 합니다.',
      'Thermal zone은 온도·trip point를 관리하고 governor는 cooling device의 state를 조절합니다. Trip과 hysteresis가 경계 근처의 반복 전환을 줄입니다. Cooling은 fan뿐 아니라 CPU·장치 성능 제한일 수 있으며 센서 오류도 처리해야 합니다.',
      '/sys/class/thermal의 zone·trip·cooling state를 조회합니다. 센서 단위와 실제 device 연결을 확인하고 안전 한계를 임의로 낮추거나 끄지 않습니다. 온도 지연과 sampling 간격을 함께 봅니다.',
      'thermal_zone_device_update의 zone 생존 검사·lock과 trip crossing·governor를 연결하세요.',
      q('80도에서 냉각 시작, hysteresis 5도 모델이면 종료 기준을 어디에 둘 수 있는가?','75도 아래','같은 80도에서 매번 켜고 끄기','Hysteresis는 켜기·끄기 경계를 나눠 진동을 줄입니다. 실제 trip 종류와 provider의 구현 규약도 확인합니다.'),
      q('Cooling device는 반드시 선풍기·fan만 뜻하는가?','성능 제한 등 열을 줄이는 여러 장치일 수 있다','항상 fan 모터 하나다','Frequency throttling도 냉각 역할을 할 수 있습니다. state 숫자의 의미는 각 cooling provider에 따라 다릅니다.'),
      details=[detail('정책과 센서','온도 읽기 provider와 trip 기준, governor의 제어, cooling device의 실제 동작은 별도 계층입니다. 센서 값 하나의 변경이 곧 특정 fan duty를 의미하지 않습니다.'),detail('단위와 지연','많은 thermal 인터페이스는 밀리섭씨를 사용하므로 80000은 80도입니다. 단위·센서 오차·응답 지연을 확인해야 단순 숫자 비교로 잘못 제어하지 않습니다.')])

    topic('Power Suspend·시스템 상태 전환','전원','kernel/power/suspend.c','suspend_devices_and_enter',
      '저전력 상태에 들어갈 때 모든 장치의 진행 작업과 깨우기 경로를 일관된 순서로 관리해야 합니다.',
      'Suspend는 task·장치·platform 단계를 순서대로 정지하고 선택한 sleep state에 들어간 뒤 반대 순서로 복귀합니다. Suspend-to-idle과 platform sleep의 지원·유지 상태는 다릅니다. 중간 실패나 wakeup 발생 때 이미 정지한 장치를 복구하는 경로가 필요합니다.',
      '/sys/power/state와 mem_sleep을 조회하고 학습 VM에서 지원 상태를 확인합니다. 실제 전환 전 저장 작업을 정리하고 장치 wakeup source·driver callback 순서를 살핍니다.',
      'suspend_devices_and_enter의 sleep_state_supported·platform begin·dpm suspend·resume를 읽으세요.',
      q('Suspend 중 한 장치가 실패하면 이미 멈춘 다른 장치도 무조건 그대로 두는가?','진행 단계에 맞춰 복구·resume해야 한다','실패한 장치만 없애면 된다','시스템을 사용 가능한 상태로 돌려놓으려면 성공한 단계와 역순 정리를 맞춰야 합니다. 오류 경로가 필수입니다.'),
      q('Suspend-to-idle과 모든 platform sleep state의 지원은 같은가?','시스템별 지원과 의미를 구분한다','어떤 장치에서도 항상 동일하다','sleep_state_supported 등 검사가 있습니다. 장치·firmware·platform의 실제 지원과 유지 상태가 다릅니다.'),
      details=[detail('장치 의존 순서','소비 장치가 공급·bus보다 먼저 안전하게 멈추고 복귀 때 필요한 공급이 먼저 준비되어야 합니다. Driver callback 목록과 device dependency는 전원 경로의 자료구조입니다.'),detail('Wakeup 경쟁','정지 단계 도중 새 wakeup 이벤트가 들어올 수 있습니다. 잠들기 조건을 다시 확인하고 즉시 복귀하는 경로를 지원해야 이벤트를 잃지 않습니다.')])

    topic('Hibernation·메모리 이미지와 복원','전원','kernel/power/hibernate.c','hibernate',
      'RAM 내용을 전원 차단 뒤에도 되살리려면 실행 상태를 저장 이미지로 만들고 안전하게 복구해야 합니다.',
      'Hibernation은 task와 장치를 조정하고 메모리 snapshot을 저장한 뒤 시스템을 끕니다. 다음 부팅의 resume 경로가 이미지를 읽어 실행 상태를 복원합니다. 이미지 크기·저장 위치·압축·암호화·커널 호환과 저장 중인 시스템 상태를 함께 고려합니다.',
      '지원과 resume 장치·공간을 확인하고 학습 환경에서 저장·복귀 흐름을 봅니다. Hibernation 이미지는 메모리의 비밀 정보를 포함할 수 있어 저장 보호 정책을 따릅니다. 단순 파일 복사와 동일한 백업으로 취급하지 않습니다.',
      'hibernate의 availability·compression·snapshot·image write와 resume 경로를 읽으세요.',
      q('Hibernation과 일반 suspend의 핵심 차이 중 하나는?','전원 차단 후 복원할 메모리 이미지를 저장한다','둘 다 RAM 내용을 무조건 버린다','Hibernation은 저장장치 이미지에 상태를 남겨 복원합니다. Suspend의 상태 유지 방식과 플랫폼 지원은 별도입니다.'),
      q('Hibernation 이미지에 보안상 중요한 것이 들어갈 수 있는가?','메모리에 있던 비밀 데이터가 포함될 수 있다','이미지는 항상 공개해도 되는 빈 데이터다','실행 메모리 snapshot에는 키·자격 증명 등 정보가 있을 수 있습니다. 저장·접근·암호화 정책을 확인해야 합니다.'),
      details=[detail('Snapshot 시점','쓰기 중인 장치와 task를 조정하지 않으면 이미지가 일관된 순간을 나타내지 못할 수 있습니다. Snapshot 준비·저장·복귀 중 커널의 구분을 읽습니다.'),detail('실패와 재개','이미지 저장에 실패하면 중단한 task·device를 복구해야 합니다. 저장 성공의 전원 종료 경로와 실패의 일반 실행 재개 경로는 다르므로 return 하나로 설명하지 않습니다.')])

    topic('PSI·자원 지연 계측','관찰·디버깅','kernel/sched/psi.c','psi_task_change',
      '자원 사용률만으로는 작업이 CPU·메모리·I/O를 기다려 얼마나 지연되는지 알기 어렵습니다.',
      'Pressure stall information은 task의 자원 대기 상태 변화와 시간을 집계합니다. some은 적어도 일부 작업이 지연된 시간, full은 해당 집계 범위의 모든 비idle 작업이 동시에 지연된 상태와 연결됩니다. CPU full의 전역·cgroup 지원 의미와 버전 차이는 별도로 확인합니다.',
      '/proc/pressure/{cpu,memory,io}와 cgroup pressure를 조회합니다. avg10·avg60·avg300과 total의 단위를 확인하고 사용률·queue·latency와 함께 해석합니다. Pressure만으로 원인 프로세스를 확정하지 않습니다.',
      'psi_task_change의 flags 변화·CPU별 group 갱신·parent 순회를 읽으세요.',
      q('CPU 사용률과 PSI 대기 시간은 같은 수치인가?','실행 자원 사용과 기다림을 구분한다','항상 같은 퍼센트다','CPU를 실제 사용하는 시간과 작업이 자원을 기다리는 시간은 다릅니다. 사용률이 낮아도 I/O나 메모리 대기가 높을 수 있습니다.'),
      q('PSI group의 parent를 갱신하는 이유는?','하위 task의 상태를 상위 집계 범위에도 반영한다','항상 모든 PID를 바꾸기 위해','cgroup 계층의 압력 집계가 연결되어야 상위 범위도 자식 작업의 지연을 관찰할 수 있습니다.'),
      details=[detail('상태 전환과 시간','Task 상태 bit의 set·clear 시점과 이전 상태에서 보낸 시간을 집계합니다. 단순 대기 task 개수를 한 번 세는 것만으로 누적 지연 시간 지표가 나오지 않습니다.'),detail('지표의 해석','some과 full은 같은 조건이 아니므로 수치 차이가 의미를 갖습니다. 전체 시스템과 제한된 cgroup 범위를 구분하고 지원되지 않는 지표를 0이라고 해석하지 않습니다.')])

    topic('Kdump·별도 커널로 장애 조사','관찰·디버깅','kernel/crash_core.c','__crash_kexec',
      '커널이 치명적 장애를 일으키면 원래 상태로 저장 작업을 신뢰하기 어려워 별도 환경이 필요합니다.',
      'Kdump는 미리 예약한 crash memory와 로드한 capture kernel을 사용합니다. Panic 등 경로에서 레지스터·crash 정보를 준비하고 capture kernel로 전환해 vmcore를 저장합니다. 별도 커널이 원래 메모리를 분석하므로 예약·로딩·저장 경로 준비가 모두 필요합니다.',
      'crashkernel 설정과 capture kernel 로딩 상태를 조회합니다. 실제 crash 주입은 격리 VM에서만 수행하고 dump 저장 공간·driver·분석 도구를 준비합니다. 비밀 정보가 포함된 dump의 접근을 관리합니다.',
      '__crash_kexec의 kexec_crash_image·crash setup·machine_crash_shutdown을 읽으세요.',
      q('Panic 때 처음부터 정상 커널 상태로 dump 준비를 모두 시작하면 충분한가?','capture kernel과 예약·저장 경로를 미리 준비해야 한다','어떤 panic에서도 사전 준비 없이 항상 저장된다','장애 상태에서 일반 커널 서비스를 신뢰하기 어렵습니다. 미리 마련한 이미지·예약 메모리·장치 경로가 필요합니다.'),
      q('vmcore가 일반 로그보다 더 민감할 수 있는 이유는?','장애 당시 메모리와 비밀 상태가 포함될 수 있다','항상 빈 텍스트 파일이기 때문','메모리 dump는 키·사용자 데이터·커널 상태 등을 담을 수 있습니다. 저장·분석 접근의 수명과 정책을 관리합니다.'),
      details=[detail('원본과 Capture','Capture kernel은 장애 커널 메모리를 분석 대상처럼 읽습니다. 정상 reboot로 모든 메모리를 초기화하는 흐름과 다릅니다. 보호 예약 영역의 역할을 먼저 확인합니다.'),detail('실패 조건','Crash 이미지가 없거나 진입 조건을 만족하지 않으면 capture 전환이 되지 않을 수 있습니다. 이미지 로드 성공과 실제 장치로 dump 저장 성공도 별도 검증입니다.')])

    topic('KCOV·코드 실행 경로 수집','관찰·디버깅','kernel/kcov.c','__sanitizer_cov_trace_pc',
      '입력별로 커널의 어떤 경로를 실행했는지 기록하면 새로운 경로를 찾는 fuzzing에 활용할 수 있습니다.',
      'KCOV instrumentation은 실행한 지점의 PC 또는 비교 정보를 task의 coverage buffer에 기록합니다. Buffer 첫 word의 개수와 뒤 항목을 관리하며 모드·task 문맥·용량을 확인합니다. 수집된 coverage는 기능 정답이나 모든 동시 실행 경로를 증명하지 않습니다.',
      '지원 CONFIG_KCOV와 debugfs 장치에서 buffer 설정·mmap·활성화·대상 호출·비활성화를 따릅니다. 일반 task 모드와 remote coverage 규약을 구분하고 실험 입력과 수집 범위를 기록합니다.',
      '__sanitizer_cov_trace_pc의 mode·area[0]·size 검사와 PC 기록 순서를 읽으세요.',
      q('KCOV에서 새 PC가 하나 더 수집되면 해당 기능이 정확하다는 증명인가?','새 경로의 실행 증거이고 기능 검증은 별도다','수집 순간 모든 결과가 정답이다','Coverage는 실행 범위 정보를 제공합니다. 결과·오류·불변식과 안전성은 별도로 검사해야 합니다.'),
      q('coverage buffer 용량 검사를 생략하면 어떤 문제가 생기는가?','기록 과정 자체가 buffer 범위를 넘을 수 있다','PC는 숫자라서 용량이 필요 없다','PC 항목도 메모리를 차지합니다. pos와 kcov_size 검사로 도구 자체의 범위 오류를 막아야 합니다.'),
      details=[detail('PC 정규화','canonicalize_ip는 수집 주소의 표현을 맞춥니다. 같은 실행 위치를 비교할 때 주소 배치와 수집 규약을 고려해야 합니다. 주소 숫자 자체가 사용자 기능 이름은 아닙니다.'),detail('Coverage guided fuzzing','입력을 바꿔 새로운 경로를 수집한 사례를 보존하며 탐색합니다. 무작정 모든 입력을 같은 횟수 반복하는 것보다 새로운 분기·오류 경로를 찾는 정보가 중요합니다.')])

    topic('KCSAN·경쟁 접근 탐지','관찰·디버깅','kernel/kcsan/core.c','__kcsan_check_access',
      '동시에 실행하는 메모리 접근의 일부 경쟁은 일반 기능 검사에서 드러나지 않아 전용 관찰이 필요합니다.',
      'KCSAN은 계측된 접근을 샘플링하고 software watchpoint로 겹치는 접근을 찾아 race를 보고합니다. 접근 크기·읽기/쓰기·원자 표시·동기화 관계가 관련됩니다. 샘플 기반 탐지이므로 보고가 없다는 사실이 모든 데이터 경쟁 부재를 증명하지 않습니다.',
      '지원 CONFIG_KCSAN 학습 커널에서 경쟁 workload를 실행하고 보고의 두 접근·stack·객체 수명을 분석합니다. READ_ONCE·atomic·lock 사용을 단순 경고 숨김이 아니라 실제 규약에 맞게 검토합니다.',
      '__kcsan_check_access→check_access와 watchpoint·barrier 처리 코드를 읽으세요.',
      q('KCSAN 실행에서 보고가 없으면 모든 race가 없다는 증명인가?','샘플링과 실행 범위의 한계가 있다','어떤 경로도 경쟁하지 않음이 증명된다','실행하지 않은 경로와 샘플에서 놓친 접근이 있을 수 있습니다. 보고 없음과 정적 완전성은 다른 주장입니다.'),
      q('보고된 경쟁을 해결할 때 우선 확인할 정보는?','두 접근의 객체·쓰기 여부·동기화·수명','경고 줄의 색깔만','같은 객체에 겹친 접근과 적절한 동기화가 있는지 분석해야 합니다. 단순 주석 추가로 실제 race가 사라지지 않습니다.'),
      details=[detail('Watchpoint 원리','선택된 접근의 주소·크기·종류를 추적하는 동안 다른 접근과 겹치는지 관찰합니다. 모든 하드웨어 주소에 watchpoint를 영구 설치하는 방식은 아닙니다.'),detail('경쟁과 정답','같은 위치를 쓰더라도 lock·atomic 등의 올바른 계약이 있을 수 있습니다. 반대로 READ_ONCE 하나만 붙여 복합 상태의 논리 일관성이 자동 보장되지는 않습니다.')])

    topic('Error Injection·실패 경로 검증','관찰·디버깅','lib/fault-inject.c','should_fail',
      '메모리 할당·I/O가 성공하는 경로만 실행하면 실제 운영에서 드문 오류 처리의 누수와 상태 손상을 놓칠 수 있습니다.',
      'Fault injection은 설정한 probability·interval·times·task 조건에 따라 특정 연산을 실패시킵니다. 호출자는 원래 가능한 오류처럼 정리·rollback·재시도 경로를 수행해야 합니다. 실패 주입의 범위와 실제 하드웨어 오류의 모든 성질은 같지 않습니다.',
      '학습 VM에서 failslab·fail_page_alloc 등의 대상과 조건을 제한해 시험합니다. 실패 후 참조·lock·메모리·진도 상태를 확인하고 설정을 복구합니다. 공유 시스템에서 광범위하게 주입하지 않습니다.',
      'should_fail→should_fail_ex의 interval·probability·space·times 조건을 읽으세요.',
      q('두 자원을 얻다가 두 번째가 실패하면 첫 번째 자원은 어떻게 해야 하는가?','실패 계약에 맞게 첫 자원을 해제하거나 일관되게 유지한다','실패했으니 앞 자원은 자동으로 사라진다','이미 성공한 획득은 별도입니다. 오류 경로에서 대응 해제와 상태 rollback을 수행해야 누수·부분 상태가 남지 않습니다.'),
      q('확률적 실패 주입 한 번이 모든 오류 경로 실행을 보장하는가?','조건·실행 기록으로 실제 실패 경로를 확인해야 한다','설정만 있으면 모든 경로가 검사된다','주입 조건에 맞지 않거나 확률상 성공할 수 있습니다. 어느 연산이 실패했고 어떤 정리 경로가 실행됐는지 기록합니다.'),
      details=[detail('재현성','확률뿐 아니라 interval·times·task filter를 사용해 대상과 횟수를 좁힙니다. 입력과 실패 지점을 남겨 동일한 상태에서 오류 처리를 다시 검토할 수 있게 합니다.'),detail('Rollback 검증','실패 반환값만 확인하는 것으로 끝내지 않고 참조 수·열린 객체·lock 상태·다음 재시도의 동작을 봅니다. 실패 뒤 다시 정상 경로가 성공해야 남은 상태 손상을 찾을 수 있습니다.')])
