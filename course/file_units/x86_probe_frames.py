"""Complete x86 probe register macros and frame encoding header."""
ROWS = [dict(
    path='arch/x86/kernel/kprobes/common.h',
    title='Kprobes 공통 레지스터 매크로: 저장 슬롯과 복원 비대칭',
    intro='레지스터 저장·복원 문자열과 instruction helper 선언, optprobe 비활성 동작을 전체 헤더로 학습합니다.',
    principle='스택 공간을 되돌리는 것과 모든 저장 register를 다시 로드하는 것은 같지 않습니다.',
    use='rethook trampoline과 probe 실행 경로가 pt_regs 모양의 저장 영역을 마련하는 방법을 이해합니다.',
    area='LIFO · 호출 규약 · 레지스터 저장 · 주소 재배치 · 조건부 인터페이스',
    sections=[
        ('전체 구성', 'GPL-2.0, guard와 Kprobes/Optprobes 공통 설명 뒤 asm/frame/insn 헤더를 포함합니다. x86 폭별 SAVE_REGS_STRING과 RESTORE_REGS_STRING, instruction 처리 선언, OPTPROBES 기능 분기가 있습니다. 이 헤더는 문자열 조각을 정의하며 독립 실행 함수의 prologue 전체를 자동으로 만드는 것은 아닙니다.'),
        ('64비트 저장 순서', '먼저 rsp에서 24를 빼 cs, ip, orig_ax 세 슬롯을 건너뜁니다. 이후 rdi,rsi,rdx,rcx,rax,r8,r9,r10,r11,rbx,rbp,r12,r13,r14,r15 순으로 pushq하고 ENCODE_FRAME_POINTER를 실행합니다. 저장 매크로 자체의 SP 변화는 24+15*8=144바이트입니다. 건너뛴 슬롯에 유효한 값을 자동으로 써 넣는 코드가 아니며 flags, sp, ss 등의 바깥 준비는 호출 경로에서 확인해야 합니다.'),
        ('64비트 복원', 'r15부터 rdi까지 위 저장의 역순으로 15개 register를 popq하고 rsp에 24를 더해 세 슬롯을 건너뜁니다. 매크로 자체의 SP 변화는 +144바이트입니다. 그 세 슬롯을 CS나 IP에 실제 load하는 동작은 없습니다. 저장과 복원 사이에 callback이 저장 영역을 수정했다면 pop되는 값은 그 시점의 값입니다.'),
        ('32비트 저장', 'esp에서 16을 빼 cs,ip,orig_ax,gs 슬롯을 마련하고 fs,es,ds,eax,ebp,edi,esi,edx,ecx,ebx 순으로 pushl합니다. 마지막에 frame pointer를 encode합니다. 슬롯 단위의 SP 변화는 16+10*4=56바이트입니다. segment register 슬롯의 모든 상위 비트까지 이 설명만으로 완전히 초기화된다고 보장하지 않습니다.'),
        ('32비트 복원의 차이', '복원은 ebx,ecx,edx,esi,edi,ebp,eax 일곱 개만 popl합니다. 이어 esp에 7*4를 더하여 ds,es,fs,gs,orig_ax,ip,cs 슬롯을 건너뜁니다. 따라서 총 +56바이트로 공간은 회복하지만 저장한 ds/es/fs를 이 매크로에서 다시 pop하지는 않습니다. 정확한 역순 복원이라는 표현을 모든 필드에 일괄 적용하면 틀립니다.'),
        ('Instruction helper 선언', 'can_boost는 insn과 원래 주소를 받아 bool을 반환하고, recover_probed_instruction은 opcode 버퍼와 주소를 받아 unsigned long을 반환합니다. __copy_instruction은 dest/src/real과 insn을 받아 int이며 주석은 RIP-relative instruction 복사 시 displacement 조정을 설명합니다. synthesize_reljump와 relcall은 dest/from/to를 받아 void입니다. 구체적인 instruction 길이, boost 판별표, displacement 계산 본문은 여기 없습니다.'),
        ('Optprobe 구성', 'CONFIG_OPTPROBES이면 setup_detour_execution과 __recover_optprobed_insn을 외부 선언합니다. 없으면 전자는 항상 0, 후자는 입력 addr를 그대로 반환합니다. 후자의 buf는 stub에서 사용되지 않습니다. 0이라는 결과만으로 실제 detour 실행이 이뤄졌다고 말할 수 없습니다. 일반 recover_probed_instruction까지 같은 stub이 되는 것은 아닙니다.'),
        ('CS 연결과 범위', 'LIFO 저장, 예약 슬롯과 초기화의 차이, 구조체 모양을 맞추는 stack 배치, instruction 이동에 따른 상대 주소 보정 필요성을 학습합니다. ENCODE_FRAME_POINTER는 저장 후 BP를 변경하므로 원래 BP의 보존 순서가 중요합니다. 원본 대조는 실제 probe 재진입이나 CPU register 복원의 실행 시험과 구분합니다.')
    ],
    questions=[
        ('32비트 RESTORE_REGS_STRING은 ds/es/fs를 pop하는가?', '아니다. 해당 슬롯들을 addl로 건너뛴다', '그렇다. 저장한 모든 항목을 같은 방식으로 pop한다', '일곱 일반 register만 pop하고 28바이트를 더합니다. 저장 공간 회복과 register load를 구분해야 합니다.'),
        ('64비트 SAVE_REGS_STRING 자체의 SP 변화량은?', '-144바이트이다', '-120바이트이다', '15개 pushq의 120바이트에 예약 슬롯 24바이트를 더합니다. 바깥 trampoline의 push는 이 계산에 포함하지 않습니다.'),
        ('OPTPROBES가 없을 때 __recover_optprobed_insn의 반환은?', '입력 addr 그대로이다', '항상 주소 0이다', 'stub은 return addr입니다. 기능 없는 경로가 무엇을 보존하고 무엇을 생략하는지 본문으로 확인합니다.')
    ]
), dict(
    path='arch/x86/include/asm/frame.h',
    title='x86 프레임 매크로: BP 저장과 pt_regs 포인터 태그',
    intro='C 문자열과 assembly용 프레임 생성, x86 폭별 pt_regs 포인터 인코딩 및 비활성 구성을 해설합니다.',
    principle='정렬 때문에 정상 stack 주소에서 쓰이지 않는 비트 패턴을 unwind용 태그로 활용합니다.',
    use='트램펄린·예외 진입 코드가 일반 frame과 pt_regs frame을 구별하게 하는 방법을 이해합니다.',
    area='태그 포인터 · 정렬 · 프레임 포인터 · 어셈블리 매크로 · 구성별 코드 생성',
    sections=[
        ('전체 범위와 사용 의도', 'GPL-2.0, guard, asm.h 포함 뒤 FRAME_POINTER 및 ASSEMBLY 분기에 따라 macro와 inline helper를 정의합니다. 주석은 호출 가능한 non-leaf assembly 함수가 stack trace 신뢰성을 위해 frame 생성 매크로를 사용해야 한다고 설명합니다. 이 헤더 자체는 실제 unwind 순회나 자동 frame 검증을 수행하지 않습니다.'),
        ('Frame 생성과 종료', 'FRAME_POINTER 활성 시 FRAME_BEGIN은 BP를 push하고 SP를 BP로 옮깁니다. FRAME_END는 BP를 pop합니다. assembly에서는 .macro로, C에서는 인라인 asm에 연결할 문자열로 표현합니다. FRAME_END에는 SP를 BP로 복구하는 mov나 로컬 변수 공간 해제 코드가 없으므로 함수가 자신이 쓴 stack 공간을 적절히 되돌리는 계약이 필요합니다.'),
        ('64비트 encoding', 'assembly ENCODE_FRAME_POINTER는 기본값 0인 ptregs_offset을 받아 rsp+offset+1을 rbp에 넣는 lea입니다. C 문자열 버전은 offset 인자 없이 rsp+1입니다. C helper encode_frame_pointer는 regs를 unsigned long으로 변환하고 1을 더합니다. 주석은 정렬된 pt_regs 주소의 최하위 비트를 표시하여 일반 stack 주소와 구별하는 기법이라고 설명합니다. 이것은 주소 암호화나 접근 권한 검증이 아닙니다.'),
        ('32비트 encoding', 'assembly와 C 문자열은 esp를 ebp로 옮기고 0x7fffffff로 AND합니다. C helper도 regs 정수 주소의 같은 mask를 적용합니다. 주석은 최상위 비트를 지워 일반 kernel stack 주소가 아닌 패턴을 만들고 unwinder에 pt_regs 포인터임을 알린다고 설명합니다. 64비트 방식처럼 1을 더하는 연산이 아닙니다.'),
        ('원래 BP를 먼저 보존', 'encoding은 BP를 바꾸므로 주석은 64비트에서 PUSH_AND_CLEAR_REGS 뒤, 32비트에서 SAVE_ALL 뒤에 사용할 것을 요구합니다. kprobes 공통 저장 매크로도 BP를 저장한 뒤 인코딩하는 순서입니다. 태그된 BP를 만들기 전에 원래 BP를 잃으면 그 저장 register를 정상 복원할 수 없습니다.'),
        ('Frame offset과 비활성', 'FRAME_POINTER이면 FRAME_OFFSET은 __ASM_SEL(4,8)로 32비트에서 4, 64비트에서 8입니다. 없으면 0이고 FRAME_BEGIN/END는 빈 macro입니다. 비활성 assembly ENCODE_FRAME_POINTER는 선택 인자를 받지만 빈 본문이며 C 문자열 macro도 비어 있고 C helper는 0을 반환합니다. 그 0은 실제 regs 주소가 0이라는 측정값이 아니라 기능 없는 경로의 결과입니다.'),
        ('인터페이스 차이와 CS', '활성 32비트 assembly ENCODE_FRAME_POINTER에는 64비트의 선택 offset 인자가 정의되지 않습니다. 유사한 이름이라고 구성별 시그니처를 같게 가정하지 않습니다. 정렬 기반 태그, 데이터 표현과 제어 흐름의 분리, 저장 후 변경이라는 register 보존 규칙, 빈 code generation을 학습합니다. 원본 전체 대조는 모든 assembly 호출 지점이 이 계약을 지키는지 검증한 시험과 구분합니다.')
    ],
    questions=[
        ('64비트 encode_frame_pointer는 정렬된 regs 주소에 무엇을 하는가?', '정수 주소에 1을 더해 낮은 비트를 표시한다', '주소를 1비트 오른쪽으로 이동한다', '본문은 (unsigned long)regs+1입니다. 정렬 전제를 가진 태그 표현이며 암호화가 아닙니다.'),
        ('32비트 encoding 방식은?', '주소와 0x7fffffff를 AND하여 최상위 비트를 지운다', '64비트와 똑같이 주소에 1을 더한다', '폭별 코드가 다릅니다. 두 방식 모두 unwinder가 특별한 frame을 알아보게 하는 표식을 만듭니다.'),
        ('FRAME_END가 모든 로컬 stack 공간을 자동 해제하는가?', '아니다. 본문은 BP를 pop하는 동작이다', '그렇다. SP를 항상 BP로 되돌리는 명령도 포함한다', '함수가 변경한 SP를 맞추는 책임과 저장 BP 복원을 구분해야 합니다. 소스에 없는 epilogue 동작을 추가해 설명하지 않습니다.')
    ]
)]
