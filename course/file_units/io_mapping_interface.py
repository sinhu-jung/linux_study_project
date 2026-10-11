"""Whole io_mapping abstraction and both configuration implementations."""
ROWS = [dict(
    path='include/linux/io-mapping.h',
    title='I/O 매핑 객체 전체: 페이지별 매핑과 전체 영역 재사용',
    intro='같은 API가 구성에 따라 페이지를 동적으로 매핑하거나 이미 매핑된 전체 영역의 주소를 반환하는 구조를 해설합니다.',
    principle='객체 수명,임시 주소 수명,실행 문맥 제약을 구분해 각 init/map/unmap/fini 쌍을 사용합니다.',
    use='정규 ioremap과 local page mapping을 감싸는 인터페이스를 자료구조 관점에서 읽습니다.',
    area='자원 수명 · 전략별 구현 · WC 메모리 · 선점과 migration · 오류 정리',
    sections=[
        ('구조체와 파일 경계', 'GPL-2.0-only·저작권·guard와 타입/할당/버그/I/O/페이지 헤더 뒤 io_mapping을 정의합니다. base는 resource_size_t,size는 unsigned long,prot는 pgprot_t,iomem은 __iomem 포인터입니다. 두 구성별 inline 구현 뒤 공통 create/free와 사용자 매핑 함수 선언이 이어집니다.'),
        ('동적 페이지 매핑 구성', 'CONFIG_HAVE_ATOMIC_IOMAP에서는 pfn.h와 asm/iomap.h를 포함합니다. 주석은 작은 가상 주소 공간에서 큰 I/O 객체 전체를 매핑하기 어려워 fixmap으로 페이지를 동적으로 매핑한다고 설명합니다. 이 구성의 init_wc는 iomap_create_wc(base,size,&prot)가 실패하면 NULL,성공하면 base/size/prot를 저장합니다. iomem 필드를 초기화하는 본문은 없습니다.'),
        ('동적 구성의 종료', 'io_mapping_fini는 iomap_free(base,size)에 위임합니다. 구조체 자체의 kfree는 여기서 하지 않습니다. 호출자가 소유한 구조체에 init/fini를 쓰는 경우와 공통 create/free로 구조체까지 할당·반환하는 경우를 구분합니다.'),
        ('Atomic 페이지 매핑', '동적 구성의 map_atomic_wc는 offset>=size를 BUG_ON으로 검사하고 base+offset을 물리주소로 만듭니다. 비RT는 preempt_disable,RT는 migrate_disable을 호출하고 pagefault_disable 뒤 PHYS_PFN과 prot로 __iomap_local_pfn_prot를 호출합니다. 이 wrapper는 페이지 내부 offset을 반환 주소에 다시 더하지 않으므로 임의 byte offset을 자동 보존하는 API로 설명하면 틀립니다.'),
        ('Atomic 해제 순서', 'unmap_atomic은 kunmap_local_indexed를 먼저 호출하고 pagefault_enable 뒤 비RT는 preempt_enable,RT는 migrate_enable을 호출합니다. 이름의 atomic이 장치64비트 접근 원자성이나 공유 데이터 잠금을 뜻하는 것은 아닙니다. 매핑·해제의 문맥 상태 변경을 맞춰 사용해야 합니다.'),
        ('Local 매핑 차이', '동적 map_local_wc도 offset 경계와 PFN 변환 후 local helper를 사용하지만 wrapper 본문에 preempt/migrate/pagefault disable 호출은 없습니다. unmap_local은 local unmap만 호출합니다. 하위 helper의 내부 계약은 별도로 확인해야 하며 wrapper 수준 차이를 유지합니다.'),
        ('일반 범위 매핑', '동적 구성의 map_wc는 offset>=mapping->size만 직접 검사하고 ioremap_wc(base+offset,요청 size)를 호출합니다. offset+요청 size가 객체 끝 이내인지까지 이 본문이 검사하지는 않습니다. 일반 unmap은 iounmap이며 임시 local 주소용 unmap과 혼용하면 안 됩니다.'),
        ('전체 영역 매핑 구성', 'HAVE_ATOMIC_IOMAP이 없으면 init_wc에서 전체 base,size를 ioremap_wc해 iomem에 저장합니다. 실패하면 NULL,성공하면 base/size와 pgprot_writecombine(PAGE_KERNEL)를 저장합니다. fini는 iomem을 iounmap합니다. 주소 공간 비용과 페이지별 매핑 비용의 선택이 구성에 따라 달라집니다.'),
        ('전체 영역의 map/unmap', '이 구성의 map_wc는 mapping->iomem+offset을 반환하며 요청 size를 사용하지 않고 offset BUG_ON도 없습니다. 일반 unmap은 빈 함수입니다. 이는 객체 전체 매핑이 살아 있기 때문이며 mapping_free 뒤에도 반환 주소를 계속 써도 된다는 의미는 아닙니다.'),
        ('전체 영역의 atomic/local wrapper', 'atomic wrapper는 여전히 비RT 선점 또는RT migration과 pagefault를 막은 뒤 map_wc에 PAGE_SIZE를 전달합니다. 해제는 빈 일반 unmap 후 상태를 복원합니다. local wrapper는 map_wc와 일반 unmap만 사용합니다. 하위 unmap이 no-op이어도 atomic wrapper의 상태 복원까지 생략되는 것은 아닙니다.'),
        ('공통 객체 생성과 실패 정리', 'create_wc는 GFP_KERNEL로 구조체를 kmalloc합니다. 할당 실패면 NULL,init 실패면 구조체를 kfree하고 NULL입니다. 성공하면 객체를 반환합니다. free는 fini 후 kfree 순서이며 NULL 입력을 무조건 허용하는 별도 분기가 없습니다. 단지 free라는 이름만으로 kfree(NULL)의 계약과 같다고 가정하면 안 됩니다.'),
        ('사용자 매핑 선언', 'io_mapping_map_user는 iomap,VMA,사용자 주소,pfn,size를 받아 int를 반환하는 선언입니다. 사용자 PTE 설정,범위·권한 검증의 본문은 여기 없습니다. 선언을 포함했다는 사실로 사용자 공간 접근이 이미 열리는 것은 아닙니다.'),
        ('CS 연결과 검증 범위', '객체와 매핑의 이중 수명,부분 매핑과 전체 매핑의 비용,전처리 전략 선택,문맥 상태의 짝,경계 검사 범위,실패 cleanup을 학습합니다. 두 구성의 코드 대조는 실제 MMU나 장치 WC 동작을 실행 검증한 것은 아닙니다.')
    ],
    questions=[
        ('HAVE_ATOMIC_IOMAP이 없는 map_wc는 무엇을 반환하는가?', '기존 iomem에 offset을 더한 주소이다', '매번 새 ioremap_wc로 만든 주소이다', '전체 매핑은 init에서 이미 만들었습니다. 이 분기 map의 size 인자는 사용되지 않으며 unmap도 빈 함수입니다.'),
        ('PREEMPT_RT atomic wrapper가 사용하는 CPU 이동 제약은?', 'migrate_disable과 migrate_enable이다', '항상 preempt_disable과 preempt_enable이다', 'IS_ENABLED(CONFIG_PREEMPT_RT)에 따라 분기합니다. pagefault 상태 변경은 두 경우 모두 수행합니다.'),
        ('동적 map_wc가 offset+요청 size 전체 경계를 직접 검사하는가?', '아니다. 직접 검사는 offset>=mapping->size뿐이다', '그렇다. 항상 전체 범위를 엄격히 검사한다', 'ioremap_wc 호출 전에 있는 BUG_ON의 범위를 정확히 읽어야 합니다. 호출자 범위 계약을 본문에 없는 검사로 대신 설명하지 않습니다.'),
        ('create_wc에서 구조체 할당 후 init이 실패하면?', '구조체를 kfree하고 NULL을 반환한다', '미초기화 구조체를 성공으로 반환한다', '공통 생성 함수에 명시적인 실패 정리 분기가 있습니다. 성공 init 뒤에만 객체를 반환합니다.'),
        ('일반 unmap이 빈 분기에서 atomic unmap도 아무것도 하지 않는가?', '아니다. pagefault와 선점 또는 migration 상태를 복원한다', '그렇다. wrapper 전체가 빈 함수이다', '기존 전체 매핑 해제는 없지만 실행 문맥 변경을 맞춰 되돌리는 코드는 남아 있습니다.')
    ]
)]
