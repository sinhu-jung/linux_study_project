"""Whole-file PCI ROM decode, image scanning and mapping lifetimes."""
ROWS = [dict(
    path='drivers/pci/rom.c', title='PCI ROM 접근: 이미지 사슬·길이 제한·매핑 복구',
    intro='ROM enable/disable, 이미지 길이 탐색, map/unmap의 모든 경로를 분석합니다.',
    principle='반환 길이를 창 크기로 제한하는 것과 각 메모리 읽기 전에 범위를 검증하는 것은 다른 보장입니다.',
    use='바이너리 형식의 오프셋, 블록 단위 길이, 반복 종료 조건과 부분 자원 정리를 학습합니다.',
    area='PCI ROM · 바이너리 파싱 · MMIO · 자원 수명 · 경계 검사',
    sections=[
        ('ROM 디코딩 활성화', 'GPL-2.0 파일은 kernel,export,pci,slab과 내부 pci.h를 포함합니다. pci_enable_rom은 ROM resource flags가 0이면 -1, ROM_SHADOW이면 하드웨어를 건드리지 않고 0입니다. 그 외에는 pcibios_resource_to_bus로 버스 주소를 얻고 ROM BAR를 읽어 PCI_ROM_ADDRESS_MASK 비트를 지운 뒤 region.start와 ENABLE을 OR해서 씁니다. 단순 enable 비트 변경뿐 아니라 비활성 시 주소를 0으로 읽는 장치를 위해 주소도 갱신합니다. 설정 공간 read/write의 반환 오류는 검사하지 않습니다.'),
        ('디코딩 비활성화', 'pci_disable_rom은 SHADOW이면 반환하고 나머지는 ROM BAR를 읽어 ENABLE 비트만 지운 뒤 씁니다. enable과 달리 flags 전체가 0인지 선행 검사하지 않습니다. 두 함수는 GPL export입니다. 주석은 ROM과 MMIO가 디코더를 공유하는 장치에서는 ROM 활성화가 다른 자원 접근에 영향을 줄 수 있다고 설명합니다. RAM shadow와 실제 ROM 디코딩 제어를 구분해야 합니다.'),
        ('이미지 서명과 데이터 구조 오프셋', 'pci_get_rom_size는 image=rom에서 do 루프를 시작합니다. readw(image)가 0xAA55가 아니면 로그 후 멈춥니다. image+24에서 읽은 16비트 값을 현재 image에 더해 pds를 구하고 readl(pds)가 PCIR의 수치 표현 0x52494350인지 검사합니다. 이들은 MMIO 접근자 readw/readl/readb를 사용하며 일반 문자열 비교가 아닙니다. 첫 서명이나 첫 PCIR 검사가 실패하면 image가 전진하지 않아 반환 길이는 0입니다.'),
        ('512바이트 길이와 종료 조건', 'pds+21의 0x80 비트를 last_image로, pds+16의 16비트를 length로 읽고 image를 length*512만큼 이동합니다. 새 image가 rom+size 이상이면 멈춥니다. 마지막 이미지가 아니면 새 위치의 0xAA55를 미리 확인하고 없으면 종료합니다. 루프 지속 조건은 length가 0이 아니며 last_image가 거짓인 경우입니다. 길이 0은 다음 반복을 막지만 그 전에 !last_image 블록의 readw는 실행될 수 있습니다. 마지막 표식과 0 길이, 창 끝, 잘못된 다음 서명은 서로 다른 종료 원인입니다.'),
        ('길이 제한과 읽기 경계의 차이', '최종 결과는 min(image-rom,size)이므로 창보다 큰 길이를 반환하지 않습니다. 그러나 첫 readw, image+24의 읽기, pds 서명과 필드 읽기 전에 각각 창 경계를 검증하는 코드는 없습니다. 포인터를 전진시킨 뒤의 검사만으로 모든 잘못된 내부 오프셋의 읽기가 안전하다고 주장해서는 안 됩니다. 이미 정상 처리한 이미지 뒤에서 새 이미지가 잘못되면 그 전까지의 양수 길이를 반환할 수 있어 모든 부분 오류가 전체 실패 0으로 바뀌는 것도 아닙니다.'),
        ('ROM 주소 할당과 매핑', 'pci_map_rom은 resource에 parent가 없을 때 pci_assign_resource를 시도하고 실패하면 NULL입니다. 이 조기 실패에는 *size 쓰기가 없습니다. 그다음 resource 시작과 길이를 얻어 *size에 창 길이를 쓰고 0이면 NULL입니다. ROM enable 실패도 NULL이며 성공하면 전체 창을 ioremap합니다. 매핑 후 실제 이미지 길이로 *size를 갱신하고 0이면 invalid_rom 경로, 양수이면 rom을 반환합니다. 반환 size는 최종적으로 스캔한 길이이고 초기 창 크기와 같다고 보장되지 않습니다.'),
        ('실패와 unmap의 복구 범위', 'invalid_rom은 iounmap한 뒤 공통 오류 경로로 내려갑니다. ioremap 실패는 unmap 없이 그 공통 경로로 갑니다. resource flags에 ROM_ENABLE이 없을 때만 pci_disable_rom을 호출하고 NULL을 반환합니다. 정상 pci_unmap_rom도 iounmap 후 같은 조건으로 disable합니다. 이전 하드웨어 BAR 값을 별도로 저장해 그대로 복원하는 방식은 아니며 resource flag를 기준으로 동작합니다. 앞서 성공한 pci_assign_resource를 이 함수가 실패 때 해제하는 코드도 없습니다.'),
        ('전체 범위와 계산 예', '다섯 함수의 본문과 모든 export, 실패 레이블을 대조했습니다. 두 이미지 길이가 2블록과 3블록이고 창이 충분하면 누적 길이는 2560바이트입니다. 양수 길이 이미지마다 전진하는 스캔은 방문 이미지 수에 선형이며 추가 상태는 일정합니다. 실제 ROM MMIO 읽기, 손상 이미지 실행이나 커널 빌드는 수행하지 않았습니다. 이 코드는 ROM을 매핑·읽는 경로이며 ROM 코드를 실행하는 본문은 아닙니다.')
    ], questions=[
        ('ROM enable이 단순히 ENABLE 비트만 세우는가?', '아니다. 버스 주소를 계산해 BAR 주소 필드도 갱신한다', '그렇다. 주소 관련 비트는 전혀 다루지 않는다', '비활성 BAR가 주소0으로 읽히는 장치를 고려해 기존 주소 마스크를 지우고 region.start를 OR합니다. 주석의 짧은 설명보다 본문을 확인해야 합니다.'),
        ('두 이미지 length가 2와 3이고 창이 충분하면 총 길이는?', '2560바이트', '5바이트', 'length 단위는 512바이트이므로 (2+3)*512=2560입니다. 필드 값 자체와 바이트 길이를 구분해야 합니다.'),
        ('min으로 최종 길이를 제한하므로 모든 pds 읽기 전에 경계가 검증되는가?', '아니다. 내부 오프셋별 선행 검사는 없다', '그렇다. 반환값 제한이 모든 읽기를 자동 보호한다', 'pds는 image+24에서 얻은 값으로 계산한 뒤 바로 읽습니다. 최종 길이의 상한 보장과 접근 위치 검증은 별개입니다.'),
        ('첫 이미지 서명이 잘못되면 map_rom은 어떤 경로로 가는가?', '스캔 길이0이 되어 unmap 후 조건부 disable하고 NULL을 반환한다', '서명을 무시하고 전체 창을 정상 ROM으로 반환한다', '첫 위치에서 image가 전진하지 않아 크기는0입니다. map 함수는 이를 invalid_rom으로 처리합니다.'),
        ('주소 할당이 실패한 map_rom이 *size를 반드시 0으로 만드는가?', '아니다. 그 실패는 size 대입보다 앞에 있다', '그렇다. 모든 실패 경로가 출력값을0으로 초기화한다', '출력값은 resource 길이를 읽는 단계에서 처음 쓰입니다. NULL 반환만으로 size가 어떤 값인지 일괄 가정하면 안 됩니다.'),
        ('unmap_rom은 ROM_ENABLE 플래그가 있더라도 항상 disable하는가?', '아니다. 해당 플래그가 없을 때만 disable을 호출한다', '그렇다. 플래그와 무관하게 항상 디코딩을 끈다', '코드는 !(res->flags & IORESOURCE_ROM_ENABLE) 조건을 사용합니다. 또한 disable 자체는 SHADOW에서 무동작입니다.'),
        ('뒤쪽 이미지의 서명이 잘못되면 이전에 처리한 길이도 무조건 버리는가?', '아니다. 이미 전진한 누적 길이를 반환할 수 있다', '그렇다. 어떤 서명 오류든 반드시 전체 길이0이다', '반환값은 별도 오류 변수가 아니라 image-rom입니다. 오류가 어느 위치에서 발생했는지에 따라 반환 길이가 다릅니다.')
    ]
)]
