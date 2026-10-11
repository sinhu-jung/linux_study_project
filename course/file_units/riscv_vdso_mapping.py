"""Whole-file RISC-V vDSO mapping setup and fault paths."""
ROWS = [dict(
    path='arch/riscv/kernel/vdso.c',
    title='RISC-V vDSO 매핑: 부팅 초기화·VVAR fault·namespace 교체',
    intro='커널이 vDSO 코드 이미지와 시간 데이터 페이지를 프로세스에 연결하는 전체 구현을 분석합니다.',
    principle='가상 주소 영역을 예약하는 작업과 실제 페이지를 fault 시 연결하는 작업은 분리할 수 있습니다.',
    use='VMA 권한, PFN 매핑, ELF 이미지 경계, 초기화 수명과 오류 경로를 연결해서 읽습니다.',
    area='가상 메모리 · demand paging · ELF · PFN · VMA · 시간 네임스페이스',
    sections=[
        ('전체 구성과 두 enum', 'GPL-2.0-only 파일은 ELF·메모리 관리·할당·실행 파일·오류·페이지·vDSO·time namespace·datapage·vsyscall 헤더를 포함합니다. vvar_pages는 DATA=0,TIMENS=1,NR=2이고 rv_vdso_map은 VVAR=0,VDSO=1입니다. 두 enum의 숫자가 겹쳐도 하나는 데이터 영역 안의 페이지 offset, 다른 하나는 mapping descriptor 배열의 index입니다. VVAR_SIZE는 두 페이지 크기입니다.'),
        ('공유 데이터와 이미지 메타데이터', 'static union vdso_data_store는 __page_aligned_data에 놓이고 전역 vdso_data 포인터가 그 data 배열을 가리킵니다. __vdso_info는 name, 코드 시작·끝, 코드 페이지 수, 데이터와 코드의 vm_special_mapping 포인터를 묶습니다. native 정보와 CONFIG_COMPAT일 때 compat 정보가 있습니다. 메타데이터의 name은 이 파일에서 mapping 이름으로 읽히지 않고 실제 표시 이름은 descriptor의 [vvar]·[vdso]입니다.'),
        ('코드 이동 callback', 'vdso_mremap은 current->mm->context.vdso를 new_vma->vm_start로 갱신하고 0을 반환합니다. sm 인수는 본문에서 사용하지 않습니다. 이 함수에 코드 복사, ELF 재링크, 새로운 VVAR 위치 설정은 없습니다. 이동된 코드 주소를 mm 문맥에 기록하는 책임만 읽어야 합니다.'),
        ('부팅 이미지 검증과 페이지 수', '__vdso_init은 코드 시작의 4바이트가 ELF magic과 다르면 panic합니다. 전체 ELF 섹션이나 ABI를 파싱하는 검증은 아닙니다. 페이지 수는 (end-start)>>PAGE_SHIFT로 계산하며 올림 함수가 아닙니다. 앞서 이미지 생성 단계에서 경계를 페이지에 맞춘다는 계약에 의존합니다. PAGE_SIZE=4096, 이미지 경계 차이=8192라면 코드 페이지는 2개입니다.'),
        ('페이지 포인터 배열 구성', 'kcalloc(vdso_pages,sizeof(struct page *),GFP_KERNEL)로 포인터 배열을 할당하고 실패하면 panic합니다. sym_to_pfn(code_start)에서 시작해 pfn_to_page(pfn+i)를 배열에 넣은 뒤 cm->pages에 연결합니다. 여기서 각 코드 페이지를 새로 할당하거나 이미지를 사용자별로 복사하는 것은 아닙니다. 초기화 루프 시간과 포인터 배열 공간은 코드 페이지 수에 비례합니다.'),
        ('Namespace 데이터 접근과 교체', 'CONFIG_TIME_NS의 arch_get_vdso_data는 전달된 vvar_page를 struct vdso_data 포인터로 cast해 반환합니다. vdso_join_timens는 task->mm에 VMA iterator를 만들고 mmap_read_lock 아래 전체 VMA를 순회합니다. native dm과 일치하면 zap_vma_pages를 호출하고 COMPAT이면 compat dm도 검사합니다. ns 인수를 직접 읽거나 여기서 새 페이지를 매핑하지 않습니다. 기존 페이지 매핑을 지워 이후 fault가 새 namespace 데이터를 찾게 하는 설계입니다. VMA 자체를 삭제하는 코드와 구분합니다.'),
        ('첫 VVAR 페이지의 fault', 'vvar_fault는 find_timens_vvar_page(vma)를 먼저 호출합니다. vmf->pgoff가 DATA=0이면 namespace 페이지가 있을 때 page_to_pfn(timens_page), 없으면 sym_to_pfn(vdso_data)를 선택합니다. 따라서 같은 사용자 가상 offset이 프로세스의 namespace 상태에 따라 다른 실제 페이지를 가리킵니다. 선택 후 vmf_insert_pfn(vma,vmf->address,pfn)의 반환값을 그대로 전달합니다.'),
        ('둘째 VVAR 페이지와 SIGBUS', 'CONFIG_TIME_NS일 때 TIMENS=1 분기가 존재합니다. namespace 페이지가 없으면 VM_FAULT_SIGBUS이고, 있으면 오히려 실제 host vdso_data의 PFN을 연결합니다. namespace에서 첫 페이지는 보정 데이터, 둘째 페이지는 host 시간입니다. TIME_NS가 없으면 이 case 자체가 없고 나머지 offset과 함께 default SIGBUS로 갑니다. 두 페이지 크기의 VMA를 예약했다는 사실은 모든 페이지 접근이 성공한다는 뜻이 아닙니다.'),
        ('Native·compat descriptor와 보호 수명', 'rv_vdso_maps와 compat용 배열은 각각 [vvar]에 fault callback, [vdso]에 mremap callback을 지정합니다. native info는 vdso_start/end, compat info는 compat_vdso_start/end와 각 배열을 참조합니다. 두 ABI가 callback을 공유하더라도 descriptor와 코드 이미지 경계는 별개입니다. 배열과 정보에 __ro_after_init가 붙으며 초기화 중 cm->pages와 vdso_pages를 채웁니다. vdso_init은 native, 조건부 compat 순서로 초기화하고 0을 반환하며 arch_initcall로 등록됩니다.'),
        ('추가 매핑의 크기와 주소 확보', '__setup_additional_pages는 BUILD_BUG_ON(VVAR_NR_PAGES != __VVAR_PAGES)로 헤더의 페이지 수 계약을 빌드 때 검사합니다. text_len은 페이지 수를 다시 byte로 바꾸고 mapping_len=text_len+VVAR_SIZE입니다. get_unmapped_area(NULL,0,mapping_len,0,0)로 연속 주소 영역을 찾습니다. 이 호출 자체가 두 special mapping을 설치하는 것은 아닙니다. 오류값이면 ERR_PTR로 바꿔 공통 실패 처리로 갑니다.'),
        ('데이터와 코드의 실제 권한', '먼저 시작 주소에 VVAR_SIZE를 VM_READ|VM_MAYREAD|VM_PFNMAP으로 설치합니다. 성공하면 VVAR_SIZE만큼 더한 코드 주소를 mm->context.vdso에 기록하고 text_len을 VM_READ|VM_EXEC|VM_MAYREAD|VM_MAYWRITE|VM_MAYEXEC으로 설치합니다. VM_MAYWRITE가 있어도 현재 권한의 VM_WRITE는 없습니다. 코드의 현재 읽기·실행 권한과 변경 가능성 비트를 구분해야 합니다. 데이터 영역은 코드 바로 앞에 있습니다.'),
        ('부분 성공과 오류 처리', '어느 설치가 실패해도 up_fail은 context.vdso를 NULL로 바꾸고 PTR_ERR(ret)를 반환합니다. 코드 매핑 실패 전에 데이터 매핑이 이미 성공했을 수 있지만 이 helper에는 그것을 명시적으로 제거하는 rollback 호출이 없습니다. 따라서 이 함수 하나가 모든 부분 설치를 원상복구한다고 설명하면 안 됩니다. bprm과 uses_interp는 인수로 전달되지만 본문에서는 사용하지 않습니다.'),
        ('실행 파일 진입 wrapper와 잠금', 'arch_setup_additional_pages와 CONFIG_COMPAT의 compat_arch_setup_additional_pages는 current->mm에서 mmap_write_lock_killable을 얻습니다. 잠금 획득이 중단되면 -EINTR로 즉시 반환합니다. 획득 후 각각 native·compat info로 공통 helper를 호출하고 성공·실패 모두 mmap_write_unlock 뒤 ret를 반환합니다. namespace 교체 순회의 read lock과 새 VMA 설치의 write lock을 혼동하지 않습니다.'),
        ('주소 계산 예제와 검토 범위', '4KiB 페이지에서 코드가 2페이지이고 get_unmapped_area 결과가 B이면 전체 요청은 16KiB, 데이터 VMA는 [B,B+8192), 코드 VMA는 [B+8192,B+16384), context.vdso는 B+8192입니다. 페이지 크기는 예제의 가정이며 구현은 PAGE_SHIFT를 사용합니다. 모든 함수·descriptor·설정 분기와 실패 경로를 대조했으며 실제 RISC-V 커널 부팅이나 fault·mremap 실행을 검증한 것은 아닙니다.')
    ],
    questions=[
        ('__vdso_init의 ELF 검증 범위는?', '시작 4바이트 magic 비교', '모든 ELF section과 relocation의 완전한 검증', 'memcmp는 4바이트만 비교합니다. panic 메시지의 valid ELF 표현을 전체 형식 검증으로 확대하면 안 됩니다.'),
        ('vdso_pagelist 구성에서 새로 할당하는 것은?', '기존 코드 페이지들을 가리킬 struct page 포인터 배열', '프로세스별 vDSO 코드의 완전한 복사본', 'kcalloc 대상은 포인터 배열이며 각 원소는 기존 연속 PFN을 pfn_to_page로 바꾼 값입니다.'),
        ('Namespace 프로세스에서 VVAR offset 0과 1은 각각 무엇인가?', 'namespace 보정 페이지와 host 시간 페이지', 'host 시간 페이지와 namespace 보정 페이지', 'fault 분기는 offset 0에서 timens_page를 선택하고 offset 1에서는 실제 vdso_data를 선택합니다.'),
        ('Namespace 페이지가 없는 경우 VVAR 둘째 페이지를 접근하면?', '해당 fault 경로가 VM_FAULT_SIGBUS를 반환한다', '첫 페이지와 같은 host 데이터를 자동으로 복제한다', 'TIME_NS가 있으면 !timens_page 검사에서 실패하고 없으면 case 자체가 없어 default로 실패합니다.'),
        ('vdso_join_timens가 기존 페이지를 zap하는 이유는?', '다음 fault에서 현재 namespace에 맞는 페이지를 다시 연결하기 위해서다', '모든 vDSO 코드 이미지를 디스크에서 다시 읽기 위해서다', '순회 대상은 데이터 special mapping입니다. VMA를 유지하면서 기존 페이지 매핑을 지우며 코드 재로딩 로직은 없습니다.'),
        ('코드 VMA에 VM_MAYWRITE가 있다는 것은 현재 쓰기 가능한가?', '아니다. 현재 권한에는 VM_WRITE가 없다', '그렇다. VM_MAYWRITE와 VM_WRITE는 같은 비트다', '설치 플래그는 READ와 EXEC 및 MAY 계열입니다. 현재 허용 권한과 잠재적 권한 비트를 구분합니다.'),
        ('코드 mapping 설치가 실패하면 공통 helper가 반드시 하는 작업은?', 'context.vdso를 NULL로 바꾸고 오류값을 반환한다', '이미 성공한 VVAR VMA를 명시적으로 unmap한 뒤 성공을 반환한다', 'up_fail에는 NULL 대입과 PTR_ERR 반환만 있습니다. 외부 정리 계약을 이 함수 안의 rollback으로 꾸며서는 안 됩니다.'),
        ('4KiB 페이지, 코드 2페이지, 영역 시작 B일 때 context.vdso는?', 'B+8192', 'B+4096', 'VVAR_NR_PAGES는 2이므로 코드 앞에 8KiB를 둡니다. 한 데이터 페이지가 실제 매핑될 수 있다는 사실과 예약 영역 크기는 별개입니다.'),
        ('mmap_write_lock_killable이 실패하면 wrapper는?', '-EINTR를 반환하고 공통 설치 helper를 호출하지 않는다', '잠금 없이 설치를 계속한다', '잠금 검사 바로 아래에 즉시 반환이 있습니다. 획득한 경우에만 helper 실행 뒤 unlock합니다.')
    ]
)]
