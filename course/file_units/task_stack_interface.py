"""Whole task kernel-stack positioning and lifetime header."""
ROWS = [dict(
    path='include/linux/sched/task_stack.h',
    title='Task kernel stack: 위치·참조 수명·끝 표식',
    intro='thread_info 배치에 따른 스택 계산, 수명 보호, 주소 범위 판별과 끝 표식 검사를 전체 헤더로 학습합니다.',
    principle='스택 주소를 얻는 것, 스택 수명을 보호하는 것, 주소가 범위 안인지 검사하는 것은 서로 다른 작업입니다.',
    use='다른 task의 stack trace를 읽는 코드와 스택 손상 진단을 이해합니다.',
    area='객체 수명 · 참조 카운트 · 포인터 산술 · 메모리 배치 · 경계 표식',
    sections=[
        ('전체 구성', 'GPL-2.0, guard와 sched/magic/refcount/kasan include 뒤 thread_info 배치별 helper, get/put, accounting 선언, magic 검사, 주소 판별, 디버그 사용량 및 kstack_end가 있습니다. 실제 stack 메모리 할당·해제나 task 스케줄링을 구현하는 파일은 아닙니다.'),
        ('Thread info가 task 안에 있는 구성', 'THREAD_INFO_IN_TASK이면 task_stack_page는 task->stack을 반환하는 always-inline입니다. 주석은 종료할 수 있는 다른 task에 대해 이 포인터만 얻으면 밑에서 해제될 수 있으므로 try_get_task_stack을 사용하라고 합니다. setup_thread_stack은 빈 do/while 매크로이며 인자를 본문에서 사용하지 않습니다. 스택 내용을 복사하거나 실제 할당하는 동작이 없습니다.'),
        ('끝 표식 주소와 성장 방향', 'THREAD_INFO_IN_TASK에서 위로 자라는 stack이면 stack+THREAD_SIZE를 unsigned long 포인터로 바꾸고 한 칸 뺀 주소를 반환합니다. 따라서 THREAD_SIZE-1바이트 주소가 아니라 마지막 unsigned long 자리입니다. 아래로 자라는 경우에는 stack 시작을 반환합니다. end_of_stack은 현재 실행의 stack pointer를 읽는 함수가 아닙니다.'),
        ('Thread info가 stack에 있는 기본 경로', 'THREAD_INFO_IN_TASK가 아니며 __HAVE_THREAD_FUNCTIONS도 없으면 기본 task_stack_page 매크로를 제공합니다. setup_thread_stack은 기존 task의 thread_info 구조체를 새 task의 것에 복사한 뒤 그 task 필드를 새 task 포인터로 고칩니다. 전체 kernel stack 복사가 아닙니다. 위로 자라면 thread_info 기준 THREAD_SIZE 끝의 마지막 long, 아래로 자라면 thread_info 구조체 바로 다음을 end_of_stack으로 사용합니다. 아키텍처가 thread 함수를 제공하는 구성에서는 이 기본 정의를 건너뜁니다.'),
        ('Try get과 put의 구성별 차이', 'THREAD_INFO_IN_TASK이면 refcount_inc_not_zero(&stack_refcount)가 성공해야 주소를 반환하고 아니면 NULL입니다. 이미 0인 참조를 되살리지 않는 획득 패턴입니다. put_task_stack은 외부 함수 선언으로 실제 감소·해제 코드는 여기 없습니다. 다른 구성의 try_get은 주소를 바로 반환하고 put은 빈 함수입니다. 모든 구성에서 같은 refcount 연산이 일어난다고 설명하면 틀립니다.'),
        ('끝 magic의 의미', 'task_stack_end_corrupted는 end_of_stack이 가리키는 unsigned long을 읽어 STACK_END_MAGIC과 다른지 비교합니다. set_task_stack_end_magic은 외부 선언입니다. 끝 표식이 달라졌다는 검출과 전체 stack의 모든 바이트가 정상이라는 증명은 다릅니다. 이 매크로는 NULL이나 stack 수명을 별도로 검사하지 않습니다.'),
        ('현재 stack 안의 주소', 'object_is_on_stack은 current의 stack 시작을 얻고 obj에 kasan_reset_tag를 적용한 뒤 [stack,stack+THREAD_SIZE) 안인지 검사합니다. 끝 주소는 포함하지 않습니다. 객체 크기를 받지 않으므로 큰 객체 전체가 범위 안에 들어가는지 증명하지 않으며, 시작 주소만 검사합니다. 다른 task나 모든 IRQ stack을 열거하는 함수도 아닙니다. void 포인터 산술은 커널의 컴파일 환경에서 사용하는 표현입니다.'),
        ('Accounting과 디버그 선언', 'exit_task_stack_account와 thread_stack_cache_init은 외부 함수 선언으로 제공됩니다. DEBUG_STACK_USAGE이면 stack_not_used가 외부 구현으로 연결되고 아니면 0을 반환하는 inline입니다. 이 0을 실제 미사용 바이트가 없다는 측정 결과로 단정하면 안 됩니다. 기능 미포함 때문에 측정을 하지 않은 경우입니다.'),
        ('Kstack end의 산술 판별', '__HAVE_ARCH_KSTACK_END가 없으면 kstack_end는 !( (addr+sizeof(void*)-1) & (THREAD_SIZE-sizeof(void*)) )를 반환합니다. 주석은 일부 APM BIOS의 stack 비정렬을 고려한다고 설명합니다. 주소를 상수 경계와 비교하는 형태이지 특정 task의 stack 포인터나 magic을 읽는 검사가 아닙니다. 따라서 참이라는 사실만으로 유효하게 할당된 stack 주소라고 보장하지 않습니다. 포인터 폭과 THREAD_SIZE가 산술 의미를 결정합니다.'),
        ('CS 연결과 검증 범위', '메타데이터를 객체 안 또는 할당 영역 안에 두는 배치 차이, 참조 0의 객체 부활 방지, 경계 표식에 의한 제한적 손상 감지, 반열린 주소 범위와 객체 전체 범위의 차이를 학습합니다. 주소 획득·pin·실행 정지는 같은 작업이 아니며 이 헤더를 읽었다고 task 경쟁이나 아키텍처 stack 경계를 실행 시험한 것은 아닙니다.')
    ],
    questions=[
        ('task_stack_page로 다른 task의 주소를 얻으면 종료 경쟁에서도 수명이 보호되는가?', '아니다. 관련 구성에서는 try_get_task_stack으로 참조를 얻어야 한다', '그렇다. 포인터 반환은 항상 참조 증가를 포함한다', 'task_stack_page 본문은 주소 반환뿐입니다. 헤더 주석은 다른 task가 종료할 수 있으면 try_get을 사용하라고 명시합니다.'),
        ('위로 자라는 stack의 end_of_stack이 가리키는 곳은?', '할당 끝의 마지막 unsigned long 자리이다', '항상 할당 끝에서 1바이트 앞이다', 'unsigned long 포인터로 변환한 뒤 1을 빼므로 sizeof(unsigned long)만큼 이동합니다. 포인터 산술의 단위를 확인해야 합니다.'),
        ('object_is_on_stack이 참이면 객체 전체가 stack에 들어가는가?', '그렇게 보장하지 않는다. 전달된 주소 하나만 검사한다', '그렇다. 객체 크기를 자동으로 알아내 검사한다', '크기 인자가 없으며 tagged 주소를 정리한 뒤 범위 비교만 합니다. 객체 끝을 검사하는 코드가 없습니다.'),
        ('DEBUG_STACK_USAGE가 없을 때 stack_not_used의 0은 실제 사용량 측정인가?', '아니다. 비활성 stub의 고정 반환값이다', '그렇다. 모든 stack이 완전히 사용되었다는 뜻이다', '조건부 컴파일로 외부 측정 함수 대신 return 0이 선택됩니다. 기능 유무를 결과의 단위와 함께 해석해야 합니다.')
    ]
)]
