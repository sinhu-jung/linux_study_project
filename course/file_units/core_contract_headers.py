"""Public contracts accompanying the first whole-file utility readings."""
ROWS=[]


def add(path,title,intro,principle,use,sections,questions):
    ROWS.append(dict(path=path,title=title,intro=intro,principle=principle,use=use,
                     area='공개 헤더 · 빌드 구성·호출 계약',sections=sections,questions=questions))


add('include/asm-generic/irq_regs.h','IRQ 프레임 헤더 전체: 새 포인터 설정과 이전 문맥 복구',
    '인터럽트가 중첩될 때 이전 프레임 포인터를 어떻게 복구할 수 있는지 작은 helper 두 개로 배웁니다.',
    'DECLARE_PER_CPU는 CPU별 __irq_regs 포인터 저장소의 선언입니다. get_irq_regs는 __this_cpu_read로 현재 CPU 값을 반환합니다. set_irq_regs는 이전 값을 읽고 새 값을 쓰며 이전 값을 반환합니다.',
    'old=set_irq_regs(new)로 진입하고 종료 시 set_irq_regs(old)로 복원하는 호출 패턴을 이해합니다. helper는 CPU 이동을 막는 잠금이나 프레임의 참조 수 획득을 자체 제공하지 않습니다.',
    [('전체 파일','SPDX·설명·저작권, _ASM_GENERIC_IRQ_REGS_H 가드, percpu.h, 현재 예외 프레임 포인터 설명, per-CPU 선언, get/set inline 정의, 가드 종료가 전체입니다. 실제 fallback 저장소 정의는 lib/irq_regs.c에 있으며 선언은 저장소를 중복 생성하지 않습니다.'),
     ('상태 추적','현재 CPU 포인터가 A일 때 set_irq_regs(B)는 A를 반환하고 저장값을 B로 바꿉니다. 안쪽에서 set_irq_regs(C)는 B를 반환합니다. 안쪽 종료 때 B를 복구하고 바깥 종료 때 A를 복구하면 중첩 순서를 보존합니다. 저장소는 포인터 한 칸이므로 이전 상태를 보관하는 변수는 호출자가 관리합니다.'),
     ('CS 연결과 범위','per-CPU 자료는 CPU 간의 같은 슬롯 충돌을 줄이지만 잘못된 문맥에서 이동하는 호출자를 자동 고정하지 않습니다. __this_cpu_read/write와 프레임의 유효 수명을 호출 문맥에 맞춰 사용해야 합니다. set은 새 프레임 내용을 복사하는 것이 아니라 주소 값을 바꾸는 함수입니다.')],
    [('저장값 A에서 set_irq_regs(B)의 반환값과 새 저장값은?', '반환 A, 저장 B', '반환 B, 저장 A', 'old_regs에 읽은 A를 보관하고 B를 쓴 뒤 old_regs를 반환합니다. 반환값으로 이전 문맥을 복원할 수 있습니다.'),
     ('이 헤더가 이전 프레임 포인터의 스택을 자동 유지하는가?', '아니다. 이전 반환값 보관·복구는 호출자가 한다', '그렇다. set 호출마다 내부 리스트에 누적한다', 'helper 내부에는 연결 리스트나 배열 push가 없습니다. per-CPU 포인터 하나와 지역 변수 old_regs만 사용합니다.')])

add('include/linux/iommu-helper.h','IOMMU 헤더 전체: 범위·페이지 올림·장치 경계',
    '세 수치 helper와 하나의 외부 할당 선언으로 IOMMU 주소 제약을 계산합니다.',
    'iommu_device_max_index는 size+offset과 dma_mask를 비교해 size 또는 dma_mask-offset+1을 반환합니다. iommu_is_span_boundary는 경계 내부 오프셋과 nr을 비교합니다. iommu_num_pages는 첫 페이지 오프셋과 len을 더한 뒤 페이지 크기로 올림 나눗셈합니다.',
    '단위와 산술 범위는 호출자가 맞춰야 합니다. boundary_size와 io_page_size는 해당 비트마스크 계산에 맞는 2의 거듭제곱이어야 하며 0 또는 unsigned 오버플로 입력이 자동으로 안전한 오류가 되지 않습니다.',
    [('헤더 전체','SPDX·가드와 bug/log2/math/types 헤더, 세 inline 함수, iommu_area_alloc 외부 선언, 닫는 가드가 전부입니다. 외부 할당 함수의 구현은 lib/iommu-helper.c에 있습니다. 세 helper는 비트맵 자체를 예약하지 않습니다.'),
     ('최대 인덱스 계산','size=16,offset=8,dma_mask=19이면 24>19라 19-8+1=12입니다. dma_mask는 포함 경계이므로 +1이 등장합니다. offset이 이미 dma_mask보다 큰 경우의 뺄셈 underflow나 size+offset overflow를 이 함수가 일반적으로 검사하지 않으므로 유효 입력 계약이 필요합니다.'),
     ('장치 경계 검사','boundary_size가 2의 거듭제곱인지 BUG_ON으로 확인합니다. shift=(shift+index)&(boundary_size-1)는 경계 안의 위치입니다. boundary=8,index=5,shift=0,nr=3이면 8>8이 거짓이라 끝에 딱 맞습니다. nr=4면 9>8이 참입니다. 경계 위반 bool과 BUG_ON의 잘못된 경계 크기 검사는 다른 실패 방식입니다.'),
     ('페이지 수 계산','페이지 크기 4096,addr=4095,len=2면 첫 페이지 오프셋 4095+2=4097, 올림 나눗셈 결과 2페이지입니다. addr=4096,len=4096은 오프셋 0이고 1페이지입니다. len=0이어도 정렬되지 않은 addr이면 오프셋이 남아 이 식이 1을 반환할 수 있습니다. API의 수식을 읽지 않고 빈 길이는 언제나 0이라고 추측하면 안 됩니다.'),
     ('CS 연결','포함 경계와 반열린 구간, 나눗셈 올림, 2의 거듭제곱 마스크, unsigned 산술이 연결됩니다. 고정 횟수 연산인 helper의 O(1)과 비트맵 할당 검색 전체의 복잡도를 구분합니다.')],
    [('4096바이트 페이지에서 addr=4095,len=2가 덮는 페이지 수는?', '2', '1', '첫 페이지의 마지막 바이트와 다음 페이지의 첫 바이트에 걸칩니다. 오프셋 4095+2=4097을 4096으로 올림 나누면 2입니다.'),
     ('boundary=8,index=5,nr=3,shift=0이면 경계를 넘는가?', '아니다. 끝이 경계에 정확히 맞는다', '그렇다. 같아도 위반이다', '비교는 >이지 >=가 아닙니다. 경계 내부 시작 5에 길이 3을 더한 8은 허용됩니다.'),
     ('iommu_num_pages에서 len=0이면 무조건 0인가?', '아니다. 정렬되지 않은 addr의 오프셋이 식에 남는다', '그렇다. len이 0인지 먼저 반환한다', '별도의 len==0 분기가 없습니다. 실제로 계산하는 값은 (addr & (page_size-1))+len이며 오프셋이 양수면 올림 결과가 1일 수 있습니다.')])

add('include/linux/memregion.h','메모리 영역 헤더 전체: 설정별 stub와 캐시 무효화 계약',
    '빌드 설정이 꺼졌을 때 동일한 이름의 함수가 어떤 오류를 반환하는지 읽습니다.',
    'memregion_info는 target_node와 struct range를 보관합니다. CONFIG_MEMREGION이 있으면 alloc/free 외부 선언, 없으면 alloc=-ENOMEM과 빈 free inline을 제공합니다. CPU 캐시 무효화 기능은 별도 아키텍처 설정으로 선언 또는 실패 stub를 선택합니다.',
    '번호 할당 지원 여부와 캐시 무효화 지원 여부는 다른 설정입니다. cpu_cache_has_invalidate_memregion로 기능 여부를 확인하며 실패를 무시하고 물리 메모리 내용 교체를 안전하다고 가정하지 않습니다.',
    [('전체 파일 구성','SPDX·가드, types/errno/range/bug 헤더, 정보 구조체, 번호 API의 설정 분기, 캐시 유지보수 설명과 설정 분기, 가드 종료가 전체입니다. 구조체의 target_node는 int이고 range는 별도 구조체이며 이 헤더 자체가 영역 데이터를 할당하지 않습니다.'),
     ('번호 API stub','CONFIG_MEMREGION이 없을 때 alloc의 gfp 인자는 사용되지 않고 -ENOMEM이 반환됩니다. free는 아무 동작도 하지 않습니다. 이 경우의 -ENOMEM은 실제 순간 메모리 부족을 측정한 결과라기보다 지원하지 않는 빌드의 정의된 실패 경로입니다.'),
     ('캐시 무효화 설명','장치의 secure erase나 동적 메모리 재구성처럼 CPU 캐시와 물리 메모리 내용이 어긋날 수 있는 상황의 유지보수를 설명합니다. 문서는 이 루틴이 dirty 내용을 writeback할 수도 하지 않을 수도 있다고 명시하므로 영구 저장 flush와 같은 보장으로 읽지 않습니다. res_desc는 IORES_DESC 계열 분류입니다.'),
     ('지원하지 않는 아키텍처','CONFIG_ARCH_HAS_CPU_CACHE_INVALIDATE_MEMREGION이 없으면 has 함수는 false입니다. invalidate stub는 WARN_ON_ONCE에 문자열 리터럴을 전달합니다. 이 문자열 포인터는 참인 조건이므로 해당 호출 지점에서 경고가 한 번 발생할 수 있고 -ENXIO를 반환합니다. 일반 성공 no-op 함수가 아닙니다.'),
     ('CS 연결','조건부 컴파일로 API 표면을 유지하면서 지원 여부를 오류·capability query로 표현하는 패턴입니다. 기능 검출, 오류 전파, CPU 캐시 일관성, 번호 자원과 실제 메모리 자원의 분리를 함께 배웁니다.')],
    [('CONFIG_MEMREGION이 없을 때 memregion_alloc은?', '-ENOMEM을 반환하는 inline stub', '항상 ID 0을 정상 반환', '헤더의 #else 구현이 -ENOMEM을 직접 반환합니다. 호출자는 이 값을 정상 ID로 해석하면 안 됩니다.'),
     ('미지원 아키텍처의 cpu_cache_invalidate_memregion은 성공 no-op인가?', '아니다. 경고 후 -ENXIO를 반환한다', '그렇다. void 함수처럼 아무 오류도 없다', '반환형 int이며 stub 본문에 WARN_ON_ONCE와 return -ENXIO가 있습니다. 지원 여부를 확인하고 오류를 처리해야 합니다.'),
     ('캐시 무효화가 dirty 데이터의 writeback을 항상 보장하는가?', '아니다. 이 헤더의 설명은 writeback할 수도 안 할 수도 있다고 명시한다', '그렇다. invalidate는 항상 영구 저장을 뜻한다', '캐시에서 낡은 데이터를 버리는 목적과 저장 내구성 보장은 다릅니다. 이름만으로 fsync와 같은 계약을 추론하면 안 됩니다.')])

add('include/linux/debug_locks.h','잠금 디버깅 헤더 전체: 원자 교환·경고 매크로·설정별 API',
    '복잡한 매크로를 제어 흐름으로 풀고, 디버깅 설정이 없는 빌드의 동작을 구별합니다.',
    '__debug_locks_off는 xchg로 전역 debug_locks를 0으로 바꾸며 이전값을 반환합니다. DEBUG_LOCKS_WARN_ON은 oops 진행 여부와 조건 c를 검사하고 instrumentation 구간에서 보고 상태를 갱신한 뒤 조건 감지 결과를 반환합니다.',
    '경고 매크로의 반환 1과 실제 WARN 출력은 다릅니다. CONFIG_SMP, CONFIG_DEBUG_LOCKING_API_SELFTESTS, CONFIG_LOCKDEP에 따라 각 API는 실제 호출 또는 no-op로 바뀝니다.',
    [('전체 선언과 helper','SPDX·가드, atomic/cache 헤더, task_struct 전방 선언, 두 __read_mostly 전역의 extern 선언, 원자 교환 inline과 debug_locks_off 외부 선언이 앞부분입니다. xchg는 이전값을 돌려주는 상태 전환이고 debug_locks_silent는 별도 출력 제어 플래그입니다.'),
     ('DEBUG_LOCKS_WARN_ON을 문장으로 읽기','GNU C statement expression 안에서 __ret=0으로 시작합니다. !oops_in_progress가 참이고 c가 참이면 instrumentation_begin, debug_locks_off 검사, 필요 시 WARN, instrumentation_end를 실행하고 __ret=1로 바꿉니다. 마지막 __ret가 매크로 결과입니다. #c는 조건의 소스 표기를 문자열로 만드는 전처리 연산입니다.'),
     ('평가 생략과 보고 조건','oops_in_progress가 참이면 && 단락 평가로 c를 실행하지 않습니다. c가 참이어도 이미 디버깅이 꺼져 있거나 silent라면 WARN이 출력되지 않을 수 있지만 __ret는 1이 됩니다. 따라서 결과는 조건 감지와 연결되며 출력 성공 여부를 뜻하지 않습니다. 인자에 부수 효과를 넣으면 빌드·상태별 실행 차이를 놓치기 쉽습니다.'),
     ('설정별 남은 API 전체','CONFIG_SMP가 없으면 SMP_DEBUG_LOCKS_WARN_ON(c)는 do{}while(0)이라 c도 평가하지 않습니다. SELFTESTS가 없으면 locking_selftest가 no-op입니다. LOCKDEP가 있으면 네 함수 debug_show_all_locks, debug_show_held_locks, debug_check_no_locks_freed, debug_check_no_locks_held를 외부 선언하고, 없으면 같은 역할 이름의 빈 inline을 제공합니다.'),
     ('CS 연결','조건부 컴파일·전처리 문자열화·statement expression·단락 평가·원자 교환을 한 헤더에서 연결합니다. 디버깅 장치를 끄는 동작은 실제 lock의 소유권 해제와 다릅니다. 진단 도구가 없는 빌드에서도 프로그램 동기화가 필요하다는 점은 변하지 않습니다.')],
    [('oops_in_progress가 참이면 DEBUG_LOCKS_WARN_ON(c)의 c는 평가되는가?', '아니다. && 단락 평가로 생략된다', '그렇다. WARN 매크로 인자는 항상 실행된다', '바깥 조건이 !oops_in_progress && unlikely(c)입니다. 왼쪽이 거짓이면 오른쪽을 평가하지 않습니다.'),
     ('c가 참이고 oops가 아니지만 이미 debug_locks가 꺼진 경우 매크로는?', 'WARN 없이도 결과 1을 반환할 수 있다', '반드시 결과 0이다', '__ret=1은 안쪽 WARN 조건 뒤에 있으며 바깥 조건을 통과하면 설정됩니다. 출력 여부와 조건 감지 결과를 구별해야 합니다.'),
     ('CONFIG_SMP가 없는 빌드에서 SMP_DEBUG_LOCKS_WARN_ON(x++)는?', 'no-op라 x++를 평가하지 않는다', '경고는 없지만 x++는 항상 수행한다', '#else 정의는 인자 c를 본문에 쓰지 않는 do{}while(0)입니다. 진단 매크로에 필요한 프로그램 부수 효과를 넣어서는 안 됩니다.')])
