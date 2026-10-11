"""Whole-file PCI mmap page range validation and mapping."""
ROWS = [dict(
    path='drivers/pci/mmap.c', title='PCI mmap: 페이지 올림·상대 오프셋·주소 범위 검사',
    intro='두 조건부 구현 블록과 VMA 연산 테이블, 매핑·검사 함수 전체를 분석합니다.',
    principle='바이트 범위와 페이지 범위, BAR 상대 위치와 사용자에게 보이는 절대 위치를 구분해야 합니다.',
    use='정수 올림 나눗셈, 반열린 구간, PFN 변환과 실패 전 부분 상태 변경을 학습합니다.',
    area='가상 메모리 · PCI BAR · mmap · 정수 산술 · 페이지 보호',
    sections=[
        ('컴파일 조건과 VMA 테이블', 'GPL-2.0 파일은 kernel,mm,pci와 내부 pci.h를 포함합니다. ARCH_GENERIC_PCI_MMAP_RESOURCE가 정의되면 pci_phys_vm_ops와 pci_mmap_resource_range를 제공합니다. 테이블의 access는 CONFIG_HAVE_IOREMAP_PROT일 때 generic_access_phys이며 그 외에는 해당 멤버 지정이 없습니다. 두 번째 pci_mmap_fits는 SYSFS 또는 PROC_FS 지원과 HAVE_PCI_MMAP 또는 ARCH_GENERIC_PCI_MMAP_RESOURCE의 조합이 모두 참일 때 컴파일됩니다. 두 함수의 조건은 동일하지 않습니다.'),
        ('매핑 길이의 페이지 올림', 'pci_mmap_resource_range는 resource 길이 L에 대해 ((L-1)>>PAGE_SHIFT)+1로 페이지 수를 구합니다. 양수 L에서 페이지 크기로 올림 나누기한 값입니다. vm_pgoff+vma_pages가 이를 넘으면 -EINVAL입니다. 이 함수에는 L=0 선행 검사나 덧셈 오버플로 검사가 없습니다. 뒤쪽 fits 함수의 0 길이 검사를 이 함수에도 있다고 가정하면 안 됩니다. 검사 단위가 페이지이므로 마지막 부분 페이지의 원래 바이트 경계까지 정확히 제한하는 비교는 아닙니다.'),
        ('페이지 보호와 주소 변환', 'write_combine이 참이면 vm_page_prot를 pgprot_writecombine, 아니면 pgprot_device로 바꿉니다. pci_mmap_io이면 pci_iobar_pfn에 pdev,bar,vma를 넘기고 오류를 그대로 반환합니다. 그 외 상태는 resource 시작 주소를 PAGE_SHIFT만큼 내려 얻은 PFN을 vm_pgoff에 더합니다. 보호 속성 변경은 I/O 변환보다 먼저라 그 변환이 실패해도 이전 보호 속성을 복구하는 코드는 없습니다.'),
        ('실제 remap 위임', '주소 변환 뒤 vm_ops를 pci_phys_vm_ops로 설정하고 io_remap_pfn_range에 VMA,vm_start,변환된 vm_pgoff,vm_end-vm_start,vm_page_prot를 전달합니다. 결과를 그대로 반환합니다. 실패 때 이 함수가 vm_pgoff,vm_ops,vm_page_prot를 이전 값으로 되돌리는 코드는 없습니다. PFN 값과 가상 시작 주소 및 바이트 길이는 서로 다른 단위의 인수이며, 이 본문은 매핑 이후의 하드웨어 접근이나 BAR 자원 소유권 검사를 수행하지 않습니다.'),
        ('fits의 빈 자원과 API별 좌표', 'pci_mmap_fits는 resource 길이가 0이면 즉시 0입니다. nr=vma_pages,start=vm_pgoff, size=양수 길이의 페이지 올림을 사용합니다. pci_start는 기본 0이라 일반 경로는 BAR 상대 페이지 좌표로 검사합니다. PCI_MMAP_PROCFS이면 pci_resource_to_user로 사용자 주소의 start/end를 얻고 pci_start를 페이지 단위로 바꿉니다. 반환된 pci_end는 이후 비교에 쓰지 않고 원래 resource 길이로 만든 size를 계속 사용합니다.'),
        ('세 부등식과 산술 전제', 'fits 성공 조건은 start>=pci_start, start<pci_start+size, start+nr<=pci_start+size입니다. 시작은 끝 경계보다 작아야 하지만 요청 끝은 경계와 같아도 됩니다. 조건이 모두 참이면 1, 아니면 0으로 errno를 반환하지 않습니다. nr=0을 별도로 거부하지는 않지만 이 역시 시작점 조건을 만족해야 합니다. pci_start+size와 start+nr의 오버플로 검사, 잘못된 VMA나 자원 번호의 검증은 이 본문에 없습니다.'),
        ('전체 범위와 계산 예', '페이지 크기 4096에서 양수 BAR 길이 5000은 두 페이지입니다. 상대 start=1,nr=1은 페이지 검사에서 끝 2와 같아 허용되고 start=2,nr=0은 시작점이 끝이라 거부됩니다. 두 함수 모두 루프 없는 O(1) 범위 계산이며 실제 remap 비용은 하위 구현의 몫입니다. 테이블과 두 조건부 함수 전체를 대조했으며 실제 사용자 mmap, I/O 매핑이나 커널 빌드는 실행하지 않았습니다.')
    ], questions=[
        ('페이지 크기4096,양수 자원 길이5000일 때 size는?', '2페이지', '1페이지', '((5000-1)>>12)+1=2입니다. 내림이 아니라 양수 길이의 올림 계산이며 마지막 페이지는 일부만 원래 자원 바이트에 속할 수 있습니다.'),
        ('pci_start=0,size=2,start=2,nr=0이면 fits 결과는?', '0', '1', 'start+nr<=2는 참이지만 start<2가 거짓입니다. 세 조건 모두를 만족해야 하므로 빈 요청의 끝점만 보고 성공으로 판단하면 안 됩니다.'),
        ('PROCFS에서 pci_resource_to_user가 준 pci_end가 최종 상한에 직접 쓰이는가?', '아니다. pci_start와 resource 길이로 만든 size를 사용한다', '그렇다. 오직 pci_end를 기준으로 비교한다', 'pci_end는 출력 인수로 전달되지만 이후 읽는 코드는 없습니다. 실제 최종 상한 식은 pci_start+size입니다.'),
        ('pci_iobar_pfn 실패 전에 VMA 보호 속성이 바뀔 수 있는가?', '있다. pgprot 변환이 먼저 실행된다', '없다. 모든 오류 검사를 끝낸 뒤에만 상태를 바꾼다', 'I/O 경로의 오류 반환은 이미 바뀐 vm_page_prot를 복구하지 않습니다. 반환 실패와 완전한 무변경을 동일시하면 안 됩니다.'),
        ('두 함수 모두 자원 길이0을 명시적으로 거부하는가?', '아니다. 명시적 검사 문장은 fits에만 있다', '그렇다. 둘 다 첫 줄에 같은 검사를 한다', 'resource_range는 바로 길이-1 계산을 수행합니다. 호출 계층의 전제를 확인해야 하며 다른 helper의 방어 코드를 복사해 설명하면 안 됩니다.'),
        ('메모리 BAR 매핑에서 vm_pgoff에는 무엇을 더하는가?', 'resource 시작 주소를 페이지 단위로 바꾼 값', 'resource 시작 바이트 주소를 그대로', 'pci_resource_start>>PAGE_SHIFT를 더합니다. PFN/페이지 오프셋과 바이트 주소를 섞으면 단위가 맞지 않습니다.')
    ]
)]
