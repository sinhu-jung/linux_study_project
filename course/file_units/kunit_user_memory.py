"""Whole-file user mapping ownership and conditional test symbol visibility."""
ROWS = [dict(
    path='lib/kunit/user_alloc.c', title='KUnit 사용자 매핑: mm 연결·주소 반환·정리 문맥',
    intro='주소 공간 준비부터 vm_mmap,메타데이터 할당과 cleanup까지 전체 경로를 분석합니다.',
    principle='사용자 가상 주소,커널 메타데이터 포인터,오류를 담은 정수는 서로 다른 값의 종류입니다.',
    use='주소 공간 수명,실패 보상,정수 오류 인코딩과 실행 문맥을 학습합니다.',
    area='가상 메모리 · 오류 표현 · 자원 소유권 · 커널 스레드',
    sections=[
        ('자료구조와 파일 구성', 'GPL-2.0 파일은 KUnit resource/test와 kthread/mm를 포함합니다. mmap_resource는 unsigned long addr와 size_t size만 보관하며 mm 포인터를 소유하지 않습니다. mmap_params는 file,addr,len,prot,flag,offset 여섯 인수를 저장합니다. 실제 매핑 바이트를 복제하는 구조체가 아니라 매핑 요청과 결과의 메타데이터입니다.'),
        ('기존 mm와 MMU 조건', 'attach_mm은 current->mm가 있으면 바로 0을 반환합니다. 없을 때 CONFIG_MMU가 비활성이면 -EINVAL입니다. 따라서 비MMU 조건이 함수의 모든 경로보다 먼저 검사되는 것은 아닙니다. 주석은 arch_pick_mmap_layout이 MMU 시스템에서만 적절하다고 설명합니다.'),
        ('새 주소 공간 연결', 'mm_alloc 실패는 -ENOMEM입니다. 성공 시 mm->task_size=TASK_SIZE를 설정하고 현재 signal의 RLIMIT_STACK을 arch_pick_mmap_layout에 넘긴 뒤 kthread_use_mm(mm)으로 연결합니다. 이 파일은 여기서 mmput이나 kthread_unuse_mm을 호출하지 않습니다. 주석상 process 종료 때 정리되는 수명에 의존하므로 일반적인 kmalloc/즉시 kfree 쌍과 다릅니다.'),
        ('매핑 결과의 실제 검사', 'mmap_init은 먼저 attach_mm 오류를 반환하고 size=p->len,addr=vm_mmap(...)를 저장합니다. 검사식은 !vres.addr뿐입니다. 교차 확인한 mm/util.c의 vm_mmap은 offset 정렬 위반 등에 -EINVAL을 unsigned long으로 반환할 수 있습니다. 이 nonzero 오류 인코딩은 현재 검사에 걸리지 않으므로 주소 0이 아닌 모든 결과를 성공 주소라고 설명하면 안 됩니다. IS_ERR_VALUE 검사는 여기에 없습니다.'),
        ('메타데이터 복제 실패의 보상', '주소가 0이 아니면 kmemdup으로 지역 vres를 복제해 res->data에 저장합니다. 실패하면 vm_munmap(addr,size)를 호출하고 -ENOMEM을 반환합니다. munmap의 반환값은 검사하지 않습니다. 이 rollback은 현재 실행 문맥에서 수행하며,이전에 attach한 mm 자체를 되돌리는 코드는 없습니다. 앞선 mmap 오류 인코딩이 걸러지지 않은 경우에도 이 분기에 같은 값이 전달될 수 있습니다.'),
        ('Cleanup이 munmap하지 않는 이유', 'free callback은 res->data를 얻어 kfree하고 data=NULL로 둡니다. 주석은 테스트 감시 프로세스에서 실행될 때 테스트의 mm는 이미 해체되었으므로 vm_munmap은 필요 없다고 설명합니다. 감시 문맥의 current mm에 테스트 주소를 무조건 munmap하는 코드를 추가하는 것으로 이해하면 안 됩니다. 이 설명은 해당 테스트 실행 수명에 의존하며 모든 임의 호출 문맥의 안전성을 증명하지 않습니다.'),
        ('공개 함수와 반환 계약', 'kunit_vm_mmap은 여섯 입력을 지역 params에 채우고 kunit_alloc_resource에 init/free,GFP_KERNEL,&params를 전달합니다. 반환 data인 vres가 있으면 vres->addr,없으면 0을 반환합니다. 따라서 mm 준비나 메타데이터 실패는 0으로 합쳐지지만 vm_mmap의 nonzero 오류값은 메타데이터 할당 성공 시 그대로 나올 수 있습니다. 반환 타입은 unsigned long이며 resource 포인터가 아닙니다.'),
        ('Export와 검토 범위', '공개 helper는 EXPORT_SYMBOL_GPL이고 파일 끝은 MODULE_IMPORT_NS(EXPORTED_FOR_KUNIT_TESTING)입니다. 두 구조체,attach/init/free/public 함수,export와 namespace import를 모두 검토했습니다. 교차 확인한 mm/util.c와 test.h 일부는 이 파일 완료에 포함하지 않습니다. 실제 커널 매핑·OOM·task 종료 실험은 실행하지 않았습니다.')
    ], questions=[
        ('vm_mmap 결과가 0이 아니면 이 파일에서 오류 검사가 모두 끝났는가?', '아니다. unsigned long으로 인코딩된 음수 errno도 nonzero다', '그렇다. 모든 실패는 반드시 주소 0으로 나온다', 'mm/util.c의 정렬 오류는 -EINVAL입니다. !addr만으로는 해당 오류 범위를 구별하지 못합니다.'),
        ('mmap_resource가 저장하는 것은?', '주소와 길이 메타데이터', '매핑한 모든 사용자 메모리의 복사본', '구조체에는 addr,size 두 필드뿐입니다. kmemdup 대상도 이 작은 구조체입니다.'),
        ('kmemdup 실패 시 수행하는 보상은?', 'vm_munmap을 호출한 뒤 -ENOMEM을 반환한다', '매핑을 유지하고 성공을 반환한다', '메타데이터를 추적할 수 없으면 현재 매핑을 회수하려고 시도합니다. munmap 결과를 검사하는 코드는 없습니다.'),
        ('free callback이 vm_munmap을 생략하는 주석상 이유는?', '감시 프로세스에서 cleanup할 때 테스트 mm가 이미 해체되었기 때문이다', '모든 사용자 매핑이 커널 시작부터 영구적이기 때문이다', '주소 공간의 수명과 cleanup 실행 문맥을 함께 봅니다. 이 callback은 추적 메타데이터만 해제합니다.'),
        ('current->mm가 이미 있으면 attach_mm은?', '새 mm를 만들지 않고 0을 반환한다', '기존 mm를 무조건 해제하고 새로 만든다', '첫 조건이 조기 반환입니다. CONFIG_MMU 검사도 그 이후에 있습니다.'),
        ('public 함수가 반환하는 것은?', 'vres에 저장된 unsigned long 주소 값 또는 wrapper 실패 시 0', '추가 참조를 가진 kunit_resource 포인터', 'kunit_alloc_resource는 data를 돌려주고 public helper는 그 안의 addr를 추출합니다. 두 반환 단계를 구분합니다.')
    ]
), dict(
    path='include/kunit/visibility.h', title='KUnit 조건부 심볼 공개: C linkage와 모듈 namespace',
    intro='두 매크로의 활성·비활성 확장과 namespace 계약을 전체 분석합니다.',
    principle='번역 단위 내부 linkage와 모듈 심볼 export는 서로 다른 공개 범위입니다.',
    use='전처리 조건,static,심볼 export와 namespace import를 구분합니다.',
    area='C linkage · 모듈 연결 · 조건부 컴파일 · 테스트 접근성',
    sections=[
        ('활성 구성', 'GPL-2.0 guard 안에서 IS_ENABLED(CONFIG_KUNIT)이면 VISIBLE_IF_KUNIT은 빈 토큰으로 확장됩니다. 즉 원래 정의에 static을 추가하지 않습니다. 이것만으로 모든 심볼이 자동 export되거나 함수가 실행되는 것은 아닙니다.'),
        ('Export와 import', '활성일 때 EXPORT_SYMBOL_IF_KUNIT(symbol)은 EXPORT_SYMBOL_NS(symbol,EXPORTED_FOR_KUNIT_TESTING)로 확장됩니다. 문서는 이를 사용하는 테스트 파일에 MODULE_IMPORT_NS(EXPORTED_FOR_KUNIT_TESTING)가 필요하다고 설명합니다. 이 매크로는 EXPORT_SYMBOL_GPL이 아니라 EXPORT_SYMBOL_NS를 선택합니다. namespace는 C++ namespace 블록과 다른 모듈 심볼 분류입니다.'),
        ('비활성 구성', 'else에서 VISIBLE_IF_KUNIT은 static,EXPORT_SYMBOL_IF_KUNIT(symbol)은 빈 토큰이 됩니다. 테스트 전용 외부 공개를 줄이되 함수 본문을 자동 삭제하는 매크로는 아닙니다. 실제 사용 위치가 올바른 정의 문맥이어야 합니다. 헤더 자체에는 include가 없으므로 IS_ENABLED와 export 매크로가 보이는 문맥도 필요합니다.'),
        ('전체 범위', 'SPDX,guard,설명 주석,두 구성의 매크로 네 정의를 모두 대조했습니다. 모듈 로딩 실험이나 생성 object의 심볼 테이블 검사를 실행한 것은 아니며 전처리 확장과 선언상 공개 범위를 설명합니다.')
    ], questions=[
        ('KUnit 비활성일 때 VISIBLE_IF_KUNIT은 무엇인가?', 'static', 'extern', '전처리 else 분기에 static이 명시되어 번역 단위 내부 linkage를 구성합니다.'),
        ('활성일 때 VISIBLE_IF_KUNIT만 붙이면 모듈 export까지 자동 수행되는가?', '아니다. export는 별도 매크로다', '그렇다. 빈 확장이 심볼 테이블을 자동 생성한다', 'VISIBLE은 빈 토큰이고 EXPORT_SYMBOL_IF_KUNIT이 별도 namespace export를 담당합니다. C linkage와 모듈 공개를 구분합니다.'),
        ('테스트가 해당 export namespace를 쓰려면 문서상 필요한 선언은?', 'MODULE_IMPORT_NS(EXPORTED_FOR_KUNIT_TESTING)', '임의의 C++ namespace 블록', '헤더 주석이 정확한 namespace import를 요구합니다. 런타임 함수 호출이 아니라 모듈 연결 메타데이터입니다.')
    ]
)]
