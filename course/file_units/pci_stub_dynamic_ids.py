"""Whole-file PCI stub dynamic ID parsing and module lifecycle."""
ROWS = [dict(
    path='drivers/pci/pci-stub.c', title='PCI stub: 동적 ID 파싱과 부분 실패를 허용하는 등록',
    intro='모듈 매개변수, 드라이버 정의, probe와 init/exit 전체를 분석합니다.',
    principle='파싱에 성공한 필드 수와 입력 전체의 유효성은 다르며 개별 항목 실패가 모듈 등록 실패와 같지는 않습니다.',
    use='구분자 파싱, 기본값, 콜백 등록, 부분 성공과 초기화 데이터 수명을 학습합니다.',
    area='PCI · 드라이버 · 문자열 파싱 · 모듈 수명 · 오류 처리',
    sections=[
        ('파일 목적과 사용 예의 범위', 'GPL-2.0의 stub 드라이버는 PCI 장치를 예약하기 위한 코드입니다. 주석은 new_id에 ID를 추가하고 기존 드라이버에서 unbind한 뒤 pci-stub에 bind하는 sysfs 예를 제시합니다. 이는 사용 설명이며 이 소스의 init이 해당 예의 쉘 명령을 실행하거나 기존 드라이버를 직접 unbind하는 것은 아닙니다. include는 module.h와 pci.h입니다.'),
        ('매개변수 저장소와 문법', 'ids는 1024바이트 char 배열이며 __initdata입니다. module_param_string으로 같은 버퍼와 sizeof(ids),권한0을 지정합니다. 설명은 vendor:device 뒤에 subvendor,subdevice,class,class_mask를 차례로 생략할 수 있고 여러 항목은 쉼표로 나눈다고 합니다. 권한0은 이 매개변수를 일반 sysfs 매개변수 파일로 노출하는 읽기 권한이 아닙니다. 별도 driver new_id 인터페이스와 모듈 초기 ids 버퍼를 구분해야 합니다.'),
        ('드라이버 정의와 probe', 'stub_driver는 이름 pci-stub,id_table=NULL,probe=pci_stub_probe,driver_managed_dma=true입니다. 고정 ID 테이블 대신 동적 ID만 사용한다는 주석이 있습니다. probe는 claimed by stub 로그를 출력하고 0을 반환할 뿐 BAR 요청이나 인터럽트 등록, DMA 전송을 수행하지 않습니다. driver_managed_dma 플래그의 설정과 실제 DMA 작업 수행은 다른 사실입니다.'),
        ('등록 후 문자열 분리', 'init은 pci_register_driver를 먼저 호출하고 실패하면 그 오류를 반환합니다. 등록 성공 후 ids[0]이 NUL이면 즉시 0입니다. 그 외에는 p=ids에서 strsep(&p,",")로 항목을 얻습니다. strsep은 버퍼의 구분자를 NUL로 바꾸며 다음 위치를 갱신하는 방식이고, 길이0인 항목은 continue로 무시합니다. 선행·연속·마지막 쉼표로 생긴 빈 항목을 별도의 오류로 처리하지 않습니다.'),
        ('필드 기본값과 느슨한 수용 조건', '매 항목에서 subvendor/subdevice는 PCI_ANY_ID,class/class_mask는 0으로 초기화하고 vendor/device는 sscanf의 첫 두 변환 결과로 채웁니다. 여섯 %x 변환을 시도해 fields<2이면 경고 후 건너뜁니다. 그 이상이면 수용하므로 여섯 필드 모두를 요구하지 않습니다. %n이나 끝 포인터로 남은 문자열을 검사하지 않으므로 두 값 뒤의 잘못된 꼬리도 변환 개수가2이면 수용될 수 있습니다. 읽히지 않은 선택 필드는 각 항목의 기본값을 유지합니다.'),
        ('동적 ID 추가와 부분 성공', '수용한 필드를 로그로 표시하고 pci_add_dynid에 driver와 여섯 필드,마지막 driver_data=0을 전달합니다. 추가 실패는 경고만 하고 다음 항목으로 진행합니다. 루프가 끝나면 rc에 마지막 오류가 남아 있어도 0을 반환합니다. 따라서 등록 성공 후 모든 항목이 잘못되거나 동적 추가가 실패해도 모듈 초기화는 성공할 수 있습니다. 앞서 추가한 ID를 이 함수가 항목 오류 때문에 롤백하는 코드는 없습니다.'),
        ('종료와 전체 검토', 'exit는 pci_unregister_driver 한 번을 호출합니다. module_init/module_exit 연결과 VM device assignment 설명,GPL 라이선스,작성자 메타데이터까지 대조했습니다. 직접 구현된 함수는 probe,init,exit 세 개입니다. 드라이버 코어의 매칭·바인딩과 동적 ID 메모리 관리는 외부 호출의 구현 범위이며 실제 장치 unbind/bind나 모듈 로드는 실행하지 않았습니다.')
    ], questions=[
        ('ids가 빈 문자열이면 드라이버 등록도 생략하는가?', '아니다. 등록 성공을 확인한 뒤 빈 문자열 검사를 한다', '그렇다. 빈 문자열이면 register_driver를 호출하지 않는다', '등록 호출이 ids 검사보다 앞에 있습니다. 초기 ID가 없는 상태로 등록된 드라이버와 아예 미등록 상태는 다릅니다.'),
        ('vendor와 device만 읽으면 subsystem과 class 필터는 어떤 값인가?', 'subsystem 둘은 ANY,class와 class_mask는0이다', '모든 생략 필드는 직전 항목의 값을 재사용한다', '기본값 선언이 while 본문 안에 있으므로 각 항목마다 새로 초기화됩니다. 이전 항목의 선택 필드가 다음 항목에 남지 않습니다.'),
        ('입력 1234:5678:zz는 반드시 전체 거부되는가?', '아니다. 앞 두 변환이 성공하면 fields=2로 수용될 수 있다', '그렇다. 문자열 전체를 엄격하게 검증한다', '허용 기준은 fields>=2이고 남은 입력 검사는 없습니다. 최소 필드 파싱과 전체 문법 검증은 별개입니다.'),
        ('pci_add_dynid 실패가 init의 최종 실패 반환으로 이어지는가?', '아니다. 경고 후 계속하고 마지막에는0을 반환한다', '그렇다. 즉시 드라이버를 해제하고 오류를 반환한다', '등록 자체 실패만 초기에 반환합니다. 개별 ID 추가 실패 경로에는 unregister나 오류 반환이 없습니다.'),
        ('stub probe가 PCI 하드웨어를 적극적으로 초기화하는가?', '아니다. 로그를 출력하고0을 반환한다', '그렇다. BAR와 IRQ를 항상 할당한다', '본문에는 pci_info와 return만 있습니다. 성공 probe로 드라이버가 바인딩되는 것과 장치의 BAR·IRQ·DMA를 설정하는 것은 구분해야 합니다.')
    ]
)]
