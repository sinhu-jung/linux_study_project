"""Manually explained original KMSAN compiler context and metadata core."""
ROWS=[]
def row(path,title,symbol,principle,use,*questions):
 ROWS.append((path,title,symbol,principle,use,questions))
T='include/linux/kmsan_types.h'
H='mm/kmsan/kmsan.h'
C='mm/kmsan/core.c'
row(T,'KMSAN compiler ABI·인자와 반환 metadata 저장 공간','kmsan_context_state',
 'kmsan_context_state에는 param_tls, retval_tls, va_arg_tls, va_arg_origin_tls와 param_origin_tls가 각각 800byte 배열로 들어갑니다. 가변 인자의 overflow 크기는 u64, 반환 origin은 u32입니다. 상수 크기는 LLVM MSan 계측 pass에 정의된 값과 맞춰 사용하는 ABI 연결입니다. 임의로 배열 크기를 줄여도 compiler와 runtime이 같은 정보를 전달한다고 가정하면 안 됩니다.',
 '데이터 값의 인자·반환과 그 초기화 metadata 전달 공간을 구별하세요. 매개변수 shadow와 origin, 가변 인자 관련 공간의 역할을 표시합니다. fixture는 배열 크기와 선택 ABI의 구조 크기를 확인하며 실제 LLVM 계측 함수 호출은 실행하지 않습니다.',
 ('param_tls와 retval_tls의 고정 배열 길이는 얼마인가요?','각각 800byte입니다.','각각 PAGE_SIZE입니다.','헤더 상수는 MSan LLVM pass의 값이라고 설명합니다. metadata ABI의 크기이며 페이지 크기와 다릅니다.'),
 ('배열 크기를 임의로 바꿔도 compiler metadata 전달 계약은 유지되나요?','아닙니다. compiler와 runtime ABI를 맞춰야 합니다.','그렇습니다. 단순 성능 설정일 뿐입니다.','계측 pass와 runtime이 같은 공간·크기를 기대합니다. 일반 사용자 buffer와 같은 임의 조절 값이 아닙니다.'))
row(T,'KMSAN 실행 문맥·cstate와 런타임 재귀 상태','kmsan_ctx',
 'kmsan_ctx는 compiler metadata 전달 cstate, int kmsan_in_runtime, unsigned depth를 묶습니다. cstate는 metadata 교환 상태이고 kmsan_in_runtime은 runtime 진입 guard 상태입니다. 이 구조체에 depth 필드가 있다는 사실을 origin chain의 최대 깊이와 같은 값이라고 추측하면 안 됩니다. origin depth는 stack depot handle의 extra bits에 별도로 표현됩니다.',
 '문맥 구조의 필드와 origin handle의 비트를 분리해 그리세요. task별 문맥과 interrupt용 per-CPU 문맥 선택을 다음 수업과 연결합니다. 이 헤더의 depth 사용처 전체는 선언만으로 설명 완료됐다고 처리하지 않습니다.',
 ('compiler metadata 전달을 담는 kmsan_ctx 필드는 무엇인가요?','cstate입니다.','항상 실제 사용자 데이터 page입니다.','구조체는 metadata ABI 상태와 runtime guard를 묶습니다. 실제 대상 buffer를 저장하는 구조가 아닙니다.'),
 ('kmsan_ctx.depth와 origin handle depth가 이 선언만으로 같은 저장소인가요?','아닙니다. origin depth는 별도 extra bits입니다.','그렇습니다. 언제나 같은 메모리를 alias합니다.','자료구조의 필드와 stack depot handle의 압축 비트는 별개입니다. 이름만으로 동일 역할을 추측하지 않습니다.'))
row(H,'KMSAN shadow·origin pointer 쌍과 4byte granularity','shadow_origin_ptr',
 'shadow_origin_ptr는 shadow와 origin 두 void pointer를 함께 반환하는 자료구조입니다. shadow는 byte 단위 초기화 상태를 표현하고 origin은 4byte 단위의 원인 handle과 연결됩니다. 한 데이터 주소에 검사 metadata 두 종류가 붙으며 실제 데이터 pointer와 같은 의미가 아닙니다. 헤더의 META_SHADOW=false, META_ORIGIN=true는 metadata 선택 인자입니다.',
 '데이터 8byte 옆에 shadow 8byte와 두 origin 단위를 그리세요. 반환한 두 pointer의 유효성과 tracked 여부는 실제 lookup 구현에서 확인해야 합니다. 이 헤더의 반환 함수 선언만으로 모든 주소에 metadata가 있다고 가정하지 않습니다.',
 ('KMSAN_ORIGIN_SIZE의 고정 단위는 얼마인가요?','4byte입니다.','모든 origin이 1byte입니다.','내부 헤더의 상수와 core의 modulo·alignment 연산을 연결하세요.'),
 ('META_ORIGIN의 bool 선택 값은 무엇인가요?','true입니다.','false입니다.','두 macro는 metadata lookup의 선택 표식입니다. 실제 데이터의 초기화 여부 bool과 혼동하지 않습니다.'))
row(H,'KMSAN 문맥 선택·task와 interrupt per-CPU','kmsan_get_context',
 'kmsan_get_context는 in_task()이면 current->kmsan_ctx를, 아니면 raw_cpu_ptr(&kmsan_percpu_ctx)를 반환합니다. interrupt에서는 task 문맥을 그대로 쓸 수 없다는 core 주석과 연결됩니다. 문맥을 분리해 compiler 전달 상태와 runtime 재귀 guard가 적절한 실행 범위에 속하도록 합니다. 실제 CPU pinning·interrupt 실행 제어까지 이 helper가 제공하는 것은 아닙니다.',
 'task_mode가 참·거짓인 두 경로를 추적하세요. fixture는 task 객체와 per-CPU 객체의 pointer 선택을 대조하며 실제 CPU 이동이나 interrupt를 발생시키지는 않습니다. current와 per-CPU API는 커널 실행 문맥과 함께 이해합니다.',
 ('in_task가 거짓이면 어느 문맥을 반환하나요?','per-CPU kmsan 문맥입니다.','항상 current task 문맥입니다.','삼항 연산자의 두 결과를 확인하세요. interrupt용 상태와 task용 상태를 구별합니다.'),
 ('helper의 문맥 선택이 실제 interrupt 실행을 발생시키나요?','아닙니다. 현재 실행 문맥에 맞는 상태를 선택합니다.','그렇습니다. IRQ를 강제로 호출합니다.','선택 API와 실행 문맥을 생성·제어하는 동작은 다릅니다. fixture는 명시적인 상태 모델입니다.'))
row(H,'KMSAN 재귀 방지·hook가 자신을 다시 부르는 경우','kmsan_in_runtime',
 'runtime 함수가 계측 코드나 할당·lock 경로를 호출하면 compiler hook가 재귀 진입할 수 있습니다. kmsan_in_runtime은 hardirq 중첩 깊이가 1보다 크거나 NMI이면 true를 반환하고 그 외에는 선택 문맥의 guard 상태를 봅니다. nested IRQ에서 lock 사용으로 문제가 생길 수 있어 보수적으로 빠지는 목적입니다. 일부 non-blocking runtime은 초기화 이벤트 누락을 줄이려고 이 검사를 하지 않는다고 설명합니다.',
 '일반 task, IRQ1, IRQ2, NMI와 guard 켜짐을 표로 비교하세요. true를 detector 전체가 영구 비활성화됐다는 뜻으로 해석하지 않습니다. fixture는 상태 값을 주입하며 실제 nested interrupt나 NMI를 실행하지 않습니다.',
 ('hardirq 깊이 2이면 문맥 guard가 0이어도 in_runtime은 참인가요?','그렇습니다. 중첩 IRQ 조건에서 참입니다.','아닙니다. 항상 guard만 봅니다.','본문은 IRQ 깊이와 NMI를 먼저 확인합니다. 단순 변수 조회 함수가 아닙니다.'),
 ('모든 non-blocking runtime 함수가 이 검사를 반드시 한다고 설명하나요?','아닙니다. 이벤트 누락을 줄이려 하지 않는 경우를 설명합니다.','그렇습니다. 예외가 없습니다.','주석은 보수적 bail out의 부작용과 non-blocking 함수의 별도 처리를 구별합니다.'))
row(H,'KMSAN runtime 진입·후위 증가와 종료 균형','kmsan_enter_runtime',
 'enter_runtime은 ctx->kmsan_in_runtime++의 이전 값이 비영이면 경고합니다. leave_runtime은 --ctx->kmsan_in_runtime의 결과가 비영이면 경고합니다. 정상 한 번 진입은 0→1, 종료는 1→0입니다. 경고 식에도 상태 변경의 부수 효과가 있으므로 단순 검사만 하고 원래 값을 유지한다고 읽으면 안 됩니다.',
 '정상 진입·종료와 중복 진입 두 번·종료 두 번의 상태를 계산하세요. fixture는 실제 원문 증가·감소와 경고 이벤트를 확인했습니다. 경고 recorder는 실제 KMSAN_WARN_ON의 reporting·panic 정책을 모델링하지 않습니다.',
 ('enter의 후위 증가 경고 식이 보는 값은 무엇인가요?','증가 전 값입니다.','항상 증가 후 값입니다.','x++의 값과 변경된 저장 상태를 구별하세요. 첫 정상 진입은 이전0이라 경고하지 않습니다.'),
 ('정상 leave 뒤 guard는 얼마인가요?','0입니다.','언제나 1을 유지합니다.','leave는 전위 감소 후 결과를 검사합니다. 진입·종료 균형이 재귀 방지 상태를 복구합니다.'))
row(H,'KMSAN origin extra bits·depth와 UAF 압축','kmsan_extra_bits',
 'extra bits는 (depth<<1)|uaf로 구성합니다. 최하위 한 bit는 UAF 표시이고 나머지 높은 bit는 chain depth입니다. 복원은 extra&1과 extra>>1입니다. 이 helper 자체가 depth를 최대7로 clamp하지는 않습니다. 실제 stack depot의 extra bit 저장 함수와 caller가 정한 깊이 계약을 함께 읽어야 합니다.',
 'depth3,uaf1이면 7이고 depth7,uaf1이면 15를 계산하세요. fixture는 depth0..7과 두 UAF 값의 roundtrip을 확인했습니다. 임의 큰 depth 전체의 정상 허용을 이 선택 도메인으로 일반화하지 않습니다.',
 ('depth3,uaf1의 extra 값은 얼마인가요?','7입니다.','3입니다.','3<<1은6이며 최하위 UAF bit1을 OR하면7입니다.'),
 ('kmsan_extra_bits 자체가 depth를7로 clamp하나요?','아닙니다. shift와 OR만 수행합니다.','그렇습니다. 내부 min(depth,7)입니다.','본문의 정확한 연산과 stack depot 저장 단계의 별도 제한을 구별합니다.'))
row(H,'KMSAN 비계측 주소 분류·반열린 module·vmalloc 범위','kmsan_internal_is_module_addr',
 'internal module/vmalloc 주소 helper는 u64로 변환한 주소를 시작 이상·끝 미만 범위로 비교합니다. 비계측 버전이므로 runtime이 주소 분류 때문에 다시 hook를 부르는 재귀를 피하려는 목적입니다. 주소가 수치 범위 안이라는 것만으로 실제 mapping이나 pfn의 유효성을 확인하지는 않습니다.',
 'START-1,START,END-1,END의 네 경계를 계산하세요. fixture는 숫자 주소 범위와 뒤 vmalloc page/pfn 경로를 따로 검사했습니다. 실제 module loader·vmalloc page table을 실행하지 않습니다.',
 ('MODULES_END 주소 자체는 module 범위에 포함되나요?','아닙니다. 끝은 미만 비교입니다.','그렇습니다. 양끝 모두 포함됩니다.','>=START와 <END는 반열린 구간입니다. 끝 경계의 비교 연산을 확인하세요.'),
 ('숫자 주소 범위 안이면 실제 pfn 유효성도 확인됐나요?','아닙니다. 후속 page lookup이 별도로 필요합니다.','그렇습니다. 모든 숫자 주소가 mapping되어 있습니다.','분류와 실제 metadata·page 유효성은 다른 단계입니다.'))
row(H,'KMSAN report 계약·연속 구간과 reason','kmsan_report',
 'kmsan_report는 같은 origin을 공유하는 연속 byte 그룹의 off_first와 off_last를 받습니다. 범위 검사에서는 같은 address,size,user_addr,reason으로 여러 그룹을 보고할 수 있습니다. 비교에서 미초기화 값을 사용한 경우 주소를 지정하지 않고 한 번 호출하는 계약도 설명합니다. REASON_ANY, COPY_TO_USER, SUBMIT_URB는 보고의 오류 유형입니다.',
 '한 범위 안의 origin77 구간과 origin88 구간을 따로 그리세요. 전체 요청 주소와 각 보고 offset이 다른 역할임을 확인합니다. 실제 출력과 stack trace 해석은 report.c에서 추가로 공부합니다.',
 ('한 범위에서 서로 다른 origin 그룹을 여러 번 보고할 수 있나요?','그렇습니다. 같은 요청에 다른 offset·origin이 가능합니다.','아닙니다. 요청마다 무조건 한 번입니다.','kernel-doc은 range 검사에서 여러 call이 가능하다고 설명합니다. 그룹화의 단위를 확인합니다.'),
 ('off_last는 보고할 그룹의 어느 위치인가요?','마지막 byte의 offset입니다.','언제나 그룹 byte 수입니다.','매개변수 설명은 last byte to be reported입니다. 길이와 마지막 포함 offset을 구별합니다.'))
row(C,'KMSAN task 생성·문맥 zero와 thread 정보 annotation','kmsan_internal_task_create',
 'task_create는 전달된 task의 kmsan_ctx를 __memset으로 0으로 만들고 current_thread_info()가 가리키는 thread_info 범위를 unchecked unpoison합니다. 새 문맥의 실제 상태 초기화와 thread_info metadata 표시는 서로 다른 동작입니다. task 매개변수의 문맥과 current의 thread_info를 같은 pointer라고 추측하지 않습니다.',
 '대상 task ctx와 current_thread_info 결과에 별도 이름을 붙여 추적하세요. fixture는 ctx의 모든 byte가0인지 확인하고 비추적 thread_info의 unchecked annotation 경로를 실행했습니다. 실제 task fork의 전체 초기화 순서를 검증한 것은 아닙니다.',
 ('task ctx에는 실제 데이터 zero 작업이 있나요?','그렇습니다. __memset입니다.','아닙니다. metadata annotation만 있습니다.','문맥 zero와 thread_info unpoison 두 동작을 구별합니다. 같은 이름의 초기화라고 묶지 않습니다.'),
 ('unpoison하는 thread_info는 어디서 얻나요?','current_thread_info()입니다.','항상 task 인자를 byte로 cast합니다.','함수의 지역 info 초기화를 확인하세요. task ctx와 current 정보의 대상을 구별합니다.'))
row(C,'KMSAN poison 구현·shadow FF와 origin 저장','kmsan_internal_poison_memory',
 'poison_memory는 depth0과 POISON_FREE 여부를 extra bits에 넣고 호출 stack을 저장하여 origin handle을 얻습니다. POISON_CHECK는 checked 여부로 사용합니다. set_shadow_origin에 b=-1과 handle을 전달하므로 실제 shadow byte는 FF로 표시됩니다. 이 FF는 추적용 shadow이며 원래 데이터 buffer를 FF로 덮는다는 뜻이 아닙니다.',
 'poison flag CHECK=1,FREE=2와 extra의 UAF bool을 나눠 계산하세요. fixture는 shadow byte·origin·GFP 전달을 검사했습니다. 실제 free나 allocator의 UAF 재현은 수행하지 않습니다.',
 ('poison에서 FF가 쓰이는 메모리는 무엇인가요?','추적용 shadow입니다.','실제 사용자 buffer 전부입니다.','set_shadow_origin은 metadata lookup 뒤 shadow를 memset합니다. 데이터 주소와 metadata 주소를 구별합니다.'),
 ('POISON_FREE는 extra의 어떤 상태에 반영되나요?','UAF 표시입니다.','항상 depth7입니다.','depth는 처음0이고 FREE flag는 bool UAF 자리로 전달됩니다. bit flag 값2와 bool bit1을 구별합니다.'))
row(C,'KMSAN unpoison 구현·zero shadow와 zero origin 요청','kmsan_internal_unpoison_memory',
 'unpoison은 set_shadow_origin(address,size,0,0,checked)를 호출합니다. shadow는 초기화된 상태0으로 바꾸고 origin0을 요청합니다. 그러나 부분 그룹의 다른 shadow byte가 아직 비영이면 그 그룹의 origin을 무조건 없애면 안 됩니다. 실제 origin 삭제 조건은 공통 set 함수에서 확인해야 합니다.',
 '4byte 그룹 중 첫 byte만 초기화하는 경우와 네 byte 전부 초기화하는 경우를 비교하세요. fixture는 나머지 byte가 poison이면 기존 origin이 남고 그룹 전체가0이면 origin도0이 되는 선택 경로를 확인했습니다.',
 ('unpoison이 공통 함수에 전달하는 b와 origin은 무엇인가요?','0과0입니다.','-1과 새 stack handle입니다.','원문은 initialized shadow와 origin 삭제 요청을 공통 함수로 전달합니다.'),
 ('한 byte만 unpoison하면 같은 그룹의 다른 poison 원인도 무조건 지워야 하나요?','아닙니다. 다른 poison byte의 origin을 유지해야 합니다.','그렇습니다. 그룹 정보는 필요 없습니다.','origin은 4byte 단위입니다. byte 상태와 그룹의 원인 정보를 연결해 읽습니다.'))
row(C,'KMSAN stack 저장·reclaim flag 제거와 비수면','kmsan_save_stack_with_flags',
 'save_stack_with_flags는 최대64개의 stack entry를 얻고 GFP_DIRECT_RECLAIM과 KSWAPD_RECLAIM 비트를 제거한 뒤 stack_depot_save를 호출합니다. 주석은 sleep하지 말라는 목적을 명시합니다. 반환 handle에는 별도 extra bits를 설정합니다. 모든 GFP flag를0으로 만드는 것이 아니라 두 reclaim 비트만 지웁니다.',
 'flags의 각 bit와 &~mask를 펼쳐 보세요. fixture 모델의15에서 두 bit1·2를 제거하면12가 남습니다. 이 숫자는 모델의 명시적 flag 배치이며 실제 모든 kernel GFP 값과 동일하다는 뜻은 아닙니다.',
 ('stack 저장 전 제거하는 것은 모든 GFP flag인가요?','아닙니다. 두 reclaim flag입니다.','그렇습니다. 무조건 flags=0입니다.','본문의 &=~(DIRECT_RECLAIM|KSWAPD_RECLAIM)를 확인하세요. 다른 bit는 남습니다.'),
 ('reclaim flag 제거의 원문 목적은 무엇인가요?','sleep하지 않도록 하기 위해서입니다.','실제 데이터 buffer를 zero하기 위해서입니다.','주석은 Dont sleep입니다. runtime 문맥에서 호출 비용과 수면 가능성을 제한합니다.'))
row(C,'KMSAN metadata memmove·source와 destination 추적 유무','kmsan_internal_memmove_metadata',
 'memmove_metadata는 destination shadow가 없으면 즉시 반환합니다. destination이 추적되지만 source shadow가 없으면 destination을 unchecked unpoison합니다. source가 추적되지 않는 경우에는 그 데이터의 초기화 상태를 metadata로 알 수 없어 이 정책으로 처리합니다. source와 destination 모두 추적되는 일반 경로와 두 early return을 나누어 읽어야 합니다.',
 'dst tracked/src untracked와 dst untracked/src tracked의 방향을 비교하세요. 실제 데이터를 옮기는 copy는 앞에서 수행되어야 합니다. fixture는 두 경로의 shadow·origin 결과를 검사하며 모든 미추적 데이터가 실제 초기화됐다고 증명하지 않습니다.',
 ('destination shadow가 없으면 이 함수는 어떻게 하나요?','즉시 반환합니다.','destination metadata를 새로 할당합니다.','본문 첫 lookup과 return을 확인하세요. 이 함수는 lookup 실패에서 metadata 생성 allocator가 아닙니다.'),
 ('추적 destination에 미추적 source를 복사하면 어떤 정책인가요?','destination을 unpoison합니다.','무조건 destination을 poison합니다.','원문 주석은 src untracked: mark dst initialized입니다. 관찰 정책과 실제 초기화 증명을 구별합니다.'))
row(C,'KMSAN metadata memmove 방향·겹치는 구간 보존','kmsan_internal_memmove_metadata',
 'backwards는 dst>src이며 그때 step=-1,iter=n-1로 끝에서 시작합니다. 아니면 step=1,iter=0입니다. source metadata가 destination 쓰기로 먼저 덮이지 않게 memmove 방향을 따르는 알고리즘입니다. 한 배열 안의 정상 구간에서 byte shadow 결과를 원래 source 스냅샷의 memmove와 비교할 수 있습니다.',
 'src0,dst2,n8과 src2,dst0,n8의 쓰기 순서를 그리세요. fixture는 같은 arena 안의 src/dst0..23와 길이0..23의 shadow 결과를 libc memmove 독립 oracle과 대조했습니다. 모든 별개 객체 pointer 비교·huge n 계약의 증명은 아닙니다.',
 ('dst가 src보다 높으면 shadow는 어느 방향으로 복사하나요?','끝에서 시작하는 역방향입니다.','항상 앞에서 뒤로입니다.','겹치는 source를 덮기 전에 읽기 위해 backwards와 step을 선택합니다.'),
 ('검사용 shadow oracle은 실제 데이터 copy와 무엇을 비교하나요?','초기 shadow 스냅샷의 memmove 결과를 비교합니다.','kernel page allocator 전체를 비교합니다.','finite arena의 byte 상태 이동을 독립 libc 연산과 대조합니다. 실제 kernel copy 경로 전체 실행은 아닙니다.'))
row(C,'KMSAN metadata memmove·주소 offset과 origin index','kmsan_internal_memmove_metadata',
 'src_off와 dst_off는 각 데이터 주소의 mod4입니다. byte iter에 offset을 더해4로 나누면 source/destination origin 그룹 index가 됩니다. destination shadow는 align_down하여 해당4byte 그룹의 다른 byte도 확인합니다. shadow0을 복사한 뒤 그룹 전체가0이면 origin0으로 지우지만 일부 poison이 남으면 origin을 유지합니다.',
 'src 주소 offset1,dst offset3에서 iter0과 iter1의 그룹을 계산하세요. byte별 상태와4byte 원인을 따로 추적합니다. fixture는 shadow 겹침과 선택 origin 유지·삭제를 확인하며 모든 정렬·원인 섞임 경우의 완전 증명은 아닙니다.',
 ('dst_off3,iter1의 origin 그룹 index는 얼마인가요?','(3+1)/4인1입니다.','언제나0입니다.','주소가4byte 경계를 넘으면 다음 origin 그룹으로 이동합니다. byte index와 origin index는 다릅니다.'),
 ('clean shadow byte 하나를 복사하면 그룹 origin을 항상0으로 하나요?','아닙니다. 그룹 shadow 전체가0인지 확인합니다.','그렇습니다. 다른 byte 상태와 무관합니다.','원문은 aligned destination shadow word를 확인합니다. 다른 poison byte의 원인을 보존합니다.'))
row(C,'KMSAN origin 연결 cache·연속 같은 원인의 재사용','kmsan_internal_memmove_metadata',
 'poison shadow를 옮길 때 old_origin을 읽고 직전 prev_old_origin과 같으면 prev_new_origin을 재사용합니다. 다르면 chain_origin을 호출하며 반환0이면 기존 old_origin을 유지합니다. 연속 같은 원인에 매 byte 새 chain을 만들지 않는 cache입니다. 전체 copy에 있는 모든 origin을 hashmap으로 영구 cache하는 형태는 아닙니다.',
 '같은 원인16byte와 중간에 다른 원인이 들어간 구간을 그리세요. fixture는 동일 원인에서 stack 저장·chain 생성이 한 번 일어나고 생성 실패에도 old origin이 남는 선택 경로를 확인했습니다. actual depot dedup 구현은 모델 밖입니다.',
 ('cache가 저장하는 것은 무엇인가요?','직전 old origin과 그 new origin입니다.','모든 lifetime origin의 전역 hash table입니다.','지역 prev_old_origin/prev_new_origin 두 값을 사용합니다. 연속 재사용과 전역 dedup은 다릅니다.'),
 ('chain_origin이0을 반환하면 metadata copy는 원인을 잃나요?','아닙니다. 기존 old origin으로 대체합니다.','그렇습니다. 항상 origin0으로 지웁니다.','본문의 if(!new_origin) new_origin=old_origin을 확인하세요. 실패 fallback으로 정보 손실을 줄입니다.'))
row(C,'KMSAN origin chain·최대7과 반복 padding 원인','kmsan_internal_chain_origin',
 'chain_origin은 id0이면0을 반환하고 extra bits의 depth가7이면 기존 id를 그대로 반환합니다. 미초기화 padding을 가진 구조체가 반복 복사되면 origin chain이 주기적으로 길어질 수 있어 상한을 둡니다. 검사 도구 자체의 추적 비용과 저장량을 제한하는 선택입니다. 조건은 depth==7이며 arbitrary 큰 depth를 이 함수가 무조건 clamp한다고 해석하지 않습니다.',
 'depth6에서 새 chain,depth7에서 기존 handle이라는 분기를 그리세요. UAF bit는 새 extra bits에도 보존합니다. fixture는 정상 depth 도메인의 선택 경로와0을 검사하며 모든 잘못된 handle 입력을 허용한다고 주장하지 않습니다.',
 ('정상 origin depth7이면 새 chain을 저장하나요?','아닙니다. 기존 id를 반환합니다.','그렇습니다. 계속 무한히 늘립니다.','MAX_ORIGIN_DEPTH와 equality 분기를 확인하세요. 반복 복사 비용을 제한하는 원리입니다.'),
 ('상한을 두는 원문 예시는 어떤 데이터인가요?','미초기화 padding을 가진 구조체의 반복 복사입니다.','모든 process 이름입니다.','주석은 uninitialized padding이 여러 번 copied되며 chain이 주기적으로 생기는 상황을 설명합니다.'))
row(C,'KMSAN origin chain 표현·magic·현재 stack·이전 handle','kmsan_internal_chain_origin',
 '새 origin chain의 entries 세 개는 CHAIN_MAGIC_ORIGIN, 현재 저장 stack handle, 이전 id입니다. depth를 하나 늘리고 UAF bit를 보존한 extra를 새 depot handle에 넣습니다. 지역 entries는 비계측 코드가 채웠으므로 계측되는 depot 코드에 넘기기 전에 명시적으로 unpoison하여 거짓 미초기화 보고를 피합니다.',
 '세 entry를 연결 노드처럼 그리세요. data stack과 chain을 구분하는 magic의 역할을 표시합니다. fixture는 전달한 entry 값·수·extra를 기록하며 실제 stack depot hash/dedup·전체 origin 출력은 실행하지 않습니다.',
 ('chain entries의 마지막 값은 무엇인가요?','이전 origin id입니다.','새 데이터 buffer pointer입니다.','세 entry는 magic,현재 stack,이전 id입니다. 이전 원인을 따라갈 연결 정보를 저장합니다.'),
 ('비계측 지역 entries를 왜 unpoison하나요?','계측 depot 코드에 초기화 사실을 알려 거짓 보고를 피합니다.','실제 entries를0으로 다시 지우기 위해서입니다.','비계측 작성은 compiler가 metadata를 자동 전파하지 못합니다. 유효한 값과 metadata annotation을 일치시킵니다.'))
row(C,'KMSAN shadow 설정·추적하지 않는 범위와 checked','kmsan_internal_set_shadow_origin',
 'set_shadow_origin은 연속 metadata 여부를 경고로 확인한 뒤 shadow를 lookup합니다. shadow가 없으면 checked=true일 때 로그와 경고를 남기고 반환하며 checked=false면 조용히 반환합니다. lookup 실패에서 새 shadow를 할당하지 않습니다. checked는 추적되지 않는 범위를 허용하는 annotation 정책과 진단의 차이입니다.',
 '같은 미추적 주소에 checked false와 true를 대입하세요. fixture는 선택 한 페이지 범위에서 로그·경고 유무를 확인했습니다. 경고 이후 처리와 실제 reporting 정책을 모든 입력의 안전한 clamp로 해석하지 않습니다.',
 ('shadow가 없고 checked=false면 새 metadata를 만드나요?','아닙니다. 조용히 반환합니다.','그렇습니다. 전체 page를 할당합니다.','early return을 확인하세요. metadata 생성은 이 함수의 구현 역할이 아닙니다.'),
 ('shadow가 없고 checked=true면 어떤 진단이 있나요?','로그와 경고입니다.','무조건 성공으로 silent 처리합니다.','본문의 pr_err와 KMSAN_WARN_ON(true)를 확인하세요. 선택 모델은 이벤트를 기록했습니다.'))
row(C,'KMSAN origin 설정·정렬 확대와 부분 그룹','kmsan_internal_set_shadow_origin',
 'shadow 범위는 요청 size만큼 memset합니다. origin 주소는 data address를4byte 아래로 정렬하고 앞 pad를 size에 더한 뒤 크기를4byte 단위로 올립니다. 비영 새 origin이면 대상 slot을 덮고 zero origin이면 대응 shadow word가0일 때만 지웁니다. 원문 shadow_start는 lookup 결과의 u32 pointer이며 정렬 확대와 pointer 위치를 함께 읽어야 합니다.',
 '주소 offset3,size2의 origin 대상이 두4byte 그룹인 것을 계산하세요. 선택 실행은 정렬된 start의 poison·부분 unpoison을 확인했습니다. 임의 미정렬 start의 u32 접근과 모든 mapping 동작까지 이 fixture가 증명하지는 않습니다.',
 ('주소offset3,size2는 origin 기준 몇4byte 그룹을 덮나요?','두 그룹입니다.','항상 한 그룹입니다.','앞 pad3을 더하면5byte이고4byte로 올리면8byte입니다. shadow 요청2byte와 origin 범위는 다릅니다.'),
 ('새 origin이 비영이면 기존 slot을 어떤 조건으로 덮나요?','그 origin을 무조건 저장합니다.','그룹 shadow가0일 때만 저장합니다.','조건은 origin || !shadow_start[i]입니다. zero origin 삭제와 비영 origin 저장 조건을 구별합니다.'))
row(C,'KMSAN vmalloc page 조회·주소 분류와 pfn 유효성','kmsan_vmalloc_to_page_or_null',
 'vmalloc_to_page_or_null은 주소가 vmalloc 또는 module 수치 범위인지 먼저 검사합니다. 둘 다 아니면 NULL입니다. 범위 안이면 vmalloc_to_page로 page를 얻고 page_to_pfn의 pfn_valid 여부로 page 또는 NULL을 반환합니다. 수치 분류와 실제 page 유효성 두 단계입니다. vmalloc_to_page가 제공하는 page 계약도 필요한 caller 전제입니다.',
 '일반 arena,vmalloc 시작,module 시작과 invalid pfn의 반환을 비교하세요. fixture는 주소 분류·lookup 호출·pfn 검사 이벤트를 확인하며 실제 page table·module mapping을 만들지 않습니다.',
 ('module과 vmalloc 둘 다 아니면 page lookup을 하나요?','아닙니다. 먼저NULL을 반환합니다.','그렇습니다. 모든 pointer를 lookup합니다.','함수 첫 조건의 두 분류가 모두 거짓이면 early return입니다.'),
 ('주소가 범위 안이어도 pfn이 invalid면 무엇을 반환하나요?','NULL입니다.','무조건 page입니다.','범위 분류 후 pfn_valid를 추가로 확인합니다. 한 조건만 보고 유효성을 단정하지 않습니다.'))
row(C,'KMSAN 범위 검사·페이지 경계에서 chunk 분할','kmsan_internal_check_memory',
 'check_memory는 size0이면 반환하고 나머지는 pos에서 남은 길이와 현재 페이지 끝까지 길이 중 작은 chunk를 선택합니다. 각 chunk shadow를 lookup하여 페이지별로 처리합니다. 요청 시작이 페이지 끝4byte 전이고 size12면 첫 chunk4,다음 chunk8입니다. 여러 페이지가 있어도 origin 그룹 상태는 필요할 때 이어집니다.',
 'PAGE_SIZE-4 시작의12byte를 그리세요. 실제 요청 주소와 pos offset,chunk 주소를 구별합니다. fixture는 정상 연속 metadata의 page-crossing에서 하나의 같은 origin 보고가 끝까지 이어지는 경우를 확인했습니다.',
 ('페이지 끝4byte 전의12byte 요청 첫 chunk 크기는 얼마인가요?','4byte입니다.','12byte 전부입니다.','남은 요청12와 페이지 잔여4 중 min을 선택합니다. 다음 페이지에서8을 처리합니다.'),
 ('size0의 range check는 shadow를 계속 순회하나요?','아닙니다. 먼저 반환합니다.','그렇습니다. 한 페이지를 항상 검사합니다.','본문 첫 if(!size)return을 확인하세요. zero-size 구간의 조기 종료 계약입니다.'))
row(C,'KMSAN 보고 그룹·clean byte에서 끊기는 run','kmsan_internal_check_memory',
 'shadow byte가0이면 현재 poison run이 있었을 때 그 직전 byte까지 보고하고 cur_origin을0,cur_off_start를-1로 초기화합니다. 같은 origin77이라도 offset2가 clean이면0..1과3..3은 별도 run입니다. 연속 구간이라는 조건과 같은 원인이라는 조건 둘 다 있어야 한 보고 그룹입니다.',
 'shadow FF,FF,0,FF와 origin77의 보고를 손으로 계산하세요. fixture는 뒤 origin88 그룹까지 넣어 세 보고의 시작·끝을 확인했습니다. 실제 printk 출력이 아니라 보고 sink에 전달한 구조를 검증했습니다.',
 ('origin77의 poison0..1,clean2,poison3은 한 run인가요?','아닙니다. clean byte에서 두 run으로 끊깁니다.','그렇습니다. origin만 같으면 모두 합칩니다.','함수는 clean shadow에서 현재 run을 보고하고 상태를 초기화합니다. 연속성과 원인을 함께 봅니다.'),
 ('clean offset2를 만나면 앞 run의 마지막 offset은 무엇인가요?','1입니다.','2입니다.','보고는 pos+i-1까지입니다. clean byte 자체는 미초기화 그룹에 포함하지 않습니다.'))
row(C,'KMSAN 보고 그룹·origin 변경과 마지막 flush','kmsan_internal_check_memory',
 'poison byte에서 새 origin이 cur_origin과 다르면 이전 run을 직전 offset까지 보고하고 새 run을 시작합니다. 루프가 끝나면 남은 cur_origin run을 pos-1까지 보고합니다. 각 보고 앞뒤에는 enter_runtime/leave_runtime을 짝지어 출력 경로의 재귀를 막습니다. origin0은 현재 run 없음의 sentinel이므로 poison 원인의 정상 handle 계약을 함께 확인해야 합니다.',
 'origin77의0..3과88의4..7을 분할하고 끝 flush를 계산하세요. fixture는 각 보고 때 guard1,종료 뒤0,원요청 address/size/user/reason 유지까지 확인했습니다. 실제 depot handle0 실패 처리 전 경로 전체는 별도 구현과 연결해 공부합니다.',
 ('origin이 offset4에서77→88로 바뀌면 이전 run 끝은 무엇인가요?','3입니다.','4입니다.','새 byte 앞인 pos+i-1까지 이전 run을 보고하고 새 origin의 run을 시작합니다.'),
 ('마지막 poison run 뒤 clean byte가 없어도 보고되나요?','그렇습니다. 루프 뒤 flush가 있습니다.','아닙니다. 언제나 마지막 run을 버립니다.','마지막 if(cur_origin)에서 pos-1까지 보고합니다. 종료 상태 처리를 놓치지 않습니다.'))
row(C,'KMSAN 미추적 페이지·이전 run 보고와 상태 초기화','kmsan_internal_check_memory',
 'chunk shadow가 없으면 이전 run을 pos-1까지 보고하고 origin 상태를 초기화한 뒤 그 chunk를 건너뜁니다. 미추적 범위의 실제 초기화 여부를 판단하는 대신 추적 가능한 보고 구간을 끊는 동작입니다. 페이지 경계에 같은 원인이 있을 때 추적 연속성을 가정해 미추적 byte까지 한 run으로 늘리지 않습니다.',
 '첫 페이지 마지막4byte가 poison이고 다음 페이지가 미추적인 경우를 그리세요. fixture는 앞4byte만 보고되고 guard가 복구되는 경로를 확인했습니다. metadata 연속성 경고가 다른 계약 위반을 알려도 안전성 증명을 대신하지 않습니다.',
 ('미추적 chunk를 만나면 이전 poison run은 어떻게 하나요?','chunk 앞까지 보고하고 상태를 초기화합니다.','무조건 미추적 chunk 끝까지 늘립니다.','본문은 shadow NULL 분기에서 pos-1까지 보고합니다. 관찰하지 못한 byte를 poison run에 포함하지 않습니다.'),
 ('미추적 page를 건너뛰는 것이 그 데이터가 실제 initialized라는 증명인가요?','아닙니다. 추적 정보가 없는 처리입니다.','그렇습니다. 모든 byte 값을 확인했습니다.','lookup 실패 경로는 데이터 초기화 검사와 다릅니다. detector의 관찰 범위를 구별합니다.'))
row(C,'KMSAN metadata 연속성·data 간격과 shadow·origin 간격','kmsan_metadata_is_contiguous',
 'metadata_is_contiguous는 size0이나 같은 data 페이지의 범위이면 true입니다. 여러 페이지 경로에서는 current shadow와 origin pointer가 각각 next pointer-PAGE_SIZE와 같은지 확인합니다. origin은 handle 단위4byte지만 metadata mapping의 주소 간격 비교는 PAGE_SIZE입니다. source data와 그 두 metadata mapping의 연속성을 구별합니다.',
 '정렬된 두 페이지의 정상 mapping과 다음 metadata를 한 페이지 더 건너뛰는 경우를 비교하세요. fixture는 정상true와 불연속false를 확인했습니다. 임의 미정렬 짧은 경계 범위에 대한 완전 검사라고 일반화하지 않습니다.',
 ('페이지 사이 origin metadata의 pointer 간격 비교는 무엇인가요?','PAGE_SIZE입니다.','항상4byte입니다.','4byte origin 단위와 metadata page mapping의 간격은 다릅니다. 실제 비교식을 읽습니다.'),
 ('size0이면 metadata 연속성 함수는 무엇을 반환하나요?','true입니다.','항상false입니다.','본문은 zero-size를 연속성 검사 불필요한 범위로 처리합니다. actual range check의 조기 반환과 연결합니다.'))
row(C,'KMSAN metadata 연속성·모두 미추적과 혼합 mapping','kmsan_metadata_is_contiguous',
 '첫 shadow가 없으면 all_untracked를 설정합니다. 이때 origin만 있으면 진단으로 가고 뒤 page에도 shadow와 origin이 모두 없어야 같은 미추적 범위로 처리합니다. 추적/미추적이 섞이거나 두 metadata 간격이 다르면 로그와 원인 출력 후 false입니다. shadow 존재와 origin 존재의 일관성은 lookup 계약의 일부입니다.',
 '정렬된 두 페이지에서 둘 다 미추적인 경우와 두 번째만 추적인 경우를 비교하세요. fixture는 두 결과를 대조하며 실제 shadow page allocator의 mapping 불변 조건 전체는 검증하지 않았습니다.',
 ('정렬된 여러 페이지가 전부 shadow·origin 없는 경우는 true일 수 있나요?','그렇습니다. 모두 미추적 범위로 처리합니다.','아닙니다. 항상 metadata가 있어야true입니다.','all_untracked 분기는 연속 추적 범위만이 아니라 모두 없는 경우도 표현합니다.'),
 ('첫 page가 미추적이고 다음 page만 metadata가 있으면 정상 모두 미추적인가요?','아닙니다. 진단 후false입니다.','그렇습니다. 아무 혼합도 허용합니다.','all_untracked 상태에서 next shadow나 origin이 있으면 report로 갑니다.'))
row(C,'KMSAN 연속성 helper의 반복 범위·짧은 경계 접근','kmsan_metadata_is_contiguous',
 '이 고정 구현의 next_addr는 cur_addr+PAGE_SIZE이며 loop 조건은 next_addr<addr+size입니다. 시작이 페이지 끝4byte 전이고 size8이면 same-page shortcut은 통과하지 않지만 next_addr가 요청 끝보다 커서 loop를 실행하지 않고 true가 됩니다. 이 helper의 결과를 임의 불연속 mapping의 모든 경계 검사 증명이라고 확대하면 안 됩니다.',
 '원문의 pointer 증가식과 종료 조건을 실제 주소로 계산하세요. fixture는 이 짧은 경계 입력의 실제 반환도 기록했습니다. 커널의 mapping 전제와 후속 접근을 추가로 읽어야 하며 수업에서 임의 mapping에 대한 보편적 정합성 보장으로 설명하지 않습니다.',
 ('시작PAGE_SIZE-4,size8에서 next_addr 반복은 실행되나요?','아닙니다. next_addr가 요청 끝보다 큽니다.','그렇습니다. 반드시 다음 페이지 시작으로 이동합니다.','증가식은 현재 시작 주소+PAGE_SIZE입니다. 페이지 경계로 align한 다음 주소가 아님을 확인합니다.'),
 ('그 입력에서 true였다는 결과를 모든 불연속 mapping의 검사 보장으로 써도 되나요?','아닙니다. 실제 반복 범위와 mapping 전제를 확인합니다.','그렇습니다. 모든 경계를 exhaustive 검사합니다.','함수 이름만으로 전 범위를 증명하지 않습니다. 선택한 경계의 source 동작과 보편적 보장을 구별합니다.'))
row(H,'KMSAN origin 종류·alloca와 chain magic','kmsan_print_origin',
 '내부 헤더의 ALLOCA_MAGIC_ORIGIN과 CHAIN_MAGIC_ORIGIN은 저장 entry 형식을 구별합니다. report.c 99–123행을 교차 읽으면4entry+alloca magic은 지역 변수 설명과 두 PC를,3entry+chain magic은 현재 stack과 이전 원인 연결을 해석합니다. magic만이 아니라 entry 개수도 조건입니다. 선언한 print_origin은 그 형식에 따른 출력 인터페이스입니다.',
 '지역 변수 origin과 복사 chain을 서로 다른 노드 형태로 그리세요. 이 교차 영역만 읽은 것으로 report.c 전체를 완료하지 않습니다. fixture는 chain entry 생성을 확인하며 alloca 생성·전체 출력 파서를 실행하지 않습니다.',
 ('alloca와 chain 형식 판정은 magic만 비교하나요?','아닙니다. entry 개수도 확인합니다.','그렇습니다. 모든 entry 배열을 같은 형식으로 cast합니다.','교차 읽은 report 조건은4entry/3entry와 magic을 함께 확인합니다. 저장 형식의 계약을 구별합니다.'),
 ('chain origin의 연결 대상은 무엇인가요?','이전 원인과 현재 복사 stack입니다.','항상 실제 사용자 buffer 전체입니다.','core가 만든3entry 구조와 report의 해석을 연결합니다. metadata 원인 연결과 실제 데이터 저장은 다릅니다.'))
row(H,'KMSAN metadata 반환 API·store와 dummy 경로 계약','kmsan_get_shadow_origin_ptr',
 '헤더는 address,size,store를 받아 shadow·origin 쌍을 반환하는 compiler 계측용 API를 선언합니다. shadow.c 82–117행을 교차 읽으면 비활성·미추적 접근에서 store는 별도 dummy_store_page,load는 dummy_load_page로 돌립니다. 주석의 load0은 shadow metadata가 initialized로 해석된다는 뜻이며 실제 데이터 load 값을0으로 바꾸는 기능이 아닙니다.',
 '실제 data 접근과 dummy metadata 접근을 분리해서 그리세요. getter의 size>PAGE_SIZE 경고와 dummy 범위 계약도 읽습니다. 이 fixture는 선언을 컴파일할 뿐 해당 dummy getter 구현을 실행하지 않으며 별도 source 수업으로 이어가야 합니다.',
 ('dummy load가0이라는 설명은 실제 data 값도0으로 바꾼다는 뜻인가요?','아닙니다. 추적용 metadata load의 의미입니다.','그렇습니다. 모든 미추적 buffer 데이터가0입니다.','getter가 반환하는 것은 shadow와 origin pointer입니다. 실제 data pointer와 구별해야 합니다.'),
 ('load와 store dummy metadata 공간은 같은 하나인가요?','아닙니다. 두 별도 page입니다.','그렇습니다. 모든 store가 다음 load 상태를 바꿉니다.','교차 읽은 분기는 dummy_store_page와 dummy_load_page를 구별합니다. 미추적 store가 다른 load를 오염시키지 않도록 합니다.'))
row(H,'KMSAN page metadata 연결·order와 초기 할당 선언','kmsan_setup_meta',
 'kmsan_setup_meta는 data page,shadow page,origin page와 allocation order를 받는 연결 인터페이스입니다. shadow.c 301–310행을 교차 읽으면 1<<order개의 page를 순회하여 metadata page 자체에는 shadow/origin이 없도록 표시하고 data page의 연결을 설정합니다. 헤더는 초기 범위에 metadata를 준비하는 init_alloc_meta_for_range도 선언하며 여기서는 구현 전체를 포함하지 않습니다.',
 'order0의1page와 order2의4page를 계산하세요. metadata page를 다시 계측해 재귀 metadata가 생기는 문제와 연결합니다. 실제 boot allocation·page 구조·allocator 전체는 선언과 이 교차 읽기로 검증 완료되지 않습니다.',
 ('order2의 연결 반복 page 수는 얼마인가요?','4page입니다.','2page입니다.','원문 loop는1<<order입니다. order 값과 page 개수는 다른 단위입니다.'),
 ('shadow와 origin page 자체에도 계속 같은 metadata를 재귀 생성하나요?','아닙니다. metadata page는 no-shadow-origin으로 표시합니다.','그렇습니다. 무한히 추적합니다.','교차 읽은 setup 함수는 metadata page에 set_no_shadow_origin_page를 호출합니다. 추적 대상과 도구 자체 저장 공간을 구별합니다.'))
row(H,'KMSAN internal 함수 계약·비수면 작업과 재귀 검사','kmsan_internal_unpoison_memory',
 '내부 헤더는 internal_ 함수가 매우 단순하고 kmsan_in_runtime 검사를 요구하지 않도록 설계해야 한다고 설명합니다. metadata 표시·복사·원인 연결·task 초기화의 내부 인터페이스와 공개 hook의 guard 정책을 분리합니다. internal이라는 이름이 모든 인자·주소·문맥에서 무조건 안전하다는 의미는 아닙니다. core의 contiguity·lookup·range 계약은 여전히 필요합니다.',
 '공개 hook→internal helper→metadata lookup 경로의 검사 책임을 나눠 쓰세요. 모든 helper에 무조건 guard를 넣는 구현 변경을 하지는 않습니다. fixture는 선택 문맥과 유한 범위만 실행했으며 전체 호출 graph의 lock·수면 계약은 추가 구현을 읽어야 합니다.',
 ('헤더는 internal 함수에 항상 in_runtime 검사를 요구하나요?','아닙니다. 단순하게 설계하여 요구하지 않도록 설명합니다.','그렇습니다. 모든 byte마다 guard를 반복합니다.','내부 인터페이스 주석과 non-blocking runtime 설명을 연결해 읽습니다. 검사 책임은 계층별로 다릅니다.'),
 ('internal이라는 이름이 모든 range 입력의 유효성을 보장하나요?','아닙니다. 각 주소·길이·mapping 계약이 필요합니다.','그렇습니다. 어떤 pointer든 자동 보정합니다.','구현의 lookup과 contiguity 전제를 확인합니다. 이름은 역할을 나타내며 보편적 입력 검증 증명이 아닙니다.'))

def register(topic,q,detail):
 for path,title,symbol,principle,use,questions in ROWS:
  topic(title,'관찰·디버깅',path,symbol,
   '고정 Linux KMSAN의 compiler metadata 문맥·재귀 방지·byte shadow·4byte origin·복사·원인 연결·보고 구간 알고리즘을 실제 원문으로 익힙니다.',principle,use,
   '실제 data와 shadow·origin을 분리하여 그린 뒤 pointer·byte 길이·그룹 index·상태·분기·보고 offset에 한 줄씩 주석을 달아 보세요.',
   *(q(*x) for x in questions),details=[
    detail('원문과 교차 확인','include/linux/kmsan_types.h, mm/kmsan/kmsan.h, mm/kmsan/core.c 전체를 읽고 수업을 작성했습니다. shadow.c 82–117행·124–149행·301–310행과 report.c 99–123행만 getter·origin align-down·page 연결·origin 형식을 교차 확인했으며 해당 두 파일 전체를 완료로 표시하지 않습니다.'),
    detail('선택 실행과 적용 범위','세 원문을 finite data·shadow·origin arena와 context/IRQ/NMI·stackdepot·report recorder 모델에 연결했습니다. 최적화·ASan·UBSan 두 실행에서 각각31,831건이 통과했습니다. 실제 원문 memmove shadow를 독립 libc oracle과 대조하고 선택 cache/fallback·depth·guard·보고 구간·mapping 경계를 확인했습니다. set_shadow_origin은 정렬된 start만 실행했습니다. 실제 kernel allocator·LLVM 계측 ABI 호출·depot dedup·하드웨어 interrupt·모든 미정렬/거대 범위·실제 정보 유출 실행은 이 모델의 검증 범위 밖입니다.')])
