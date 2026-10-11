"""Whole-file OF device API and CONFIG_OF stubs."""
ROWS = [dict(
    path='include/linux/of_device.h', title='OF 장치 인터페이스: 매칭 결과·DMA wrapper·비지원 반환값',
    intro='활성 구성의 선언·inline wrapper와 비활성 stub 전체를 분석합니다.',
    principle='API가 같은 이름을 유지해도 구성에 따라 실제 작업과 반환 의미가 달라질 수 있습니다.',
    use='함수 포인터 테이블 연결,포인터의 불리언 변환,선택 인수와 기능 비활성화를 학습합니다.',
    area='드라이버 모델 · 조건부 컴파일 · DMA · 모듈 별칭 · 인터페이스',
    sections=[
        ('헤더와 타입', 'GPL-2.0 _LINUX_OF_DEVICE_H guard에서 linux/device/driver.h를 포함하고 device,of_device_id,kobj_uevent_env를 전방 선언합니다. CONFIG_OF를 기준으로 활성 선언과 대체 inline을 나눕니다. 이 파일 자체에 매칭 테이블 데이터나 장치 레지스터 접근은 없습니다.'),
        ('매칭 wrapper', 'of_match_device는 matches와 const device를 받아 const of_device_id *를 반환하는 외부 함수입니다. of_driver_match_device는 drv->of_match_table을 넘기고 반환값이 NULL이 아닌지를 int로 반환합니다. 매칭 항목 자체를 돌려주는 것과 참·거짓 판정은 다릅니다. 활성 wrapper가 drv=NULL을 별도로 검사하는 코드는 없습니다.'),
        ('별칭과 uevent', 'of_device_modalias는 device,출력 str,ssize_t len을 받아 ssize_t를 반환하는 선언입니다. of_device_uevent는 const device와 env를 받고 void이며 uevent_modalias는 같은 종류의 인수로 int를 반환합니다. 이 헤더에는 문자열 생성,환경 변수 추가,길이 검사의 실제 구현이 없으므로 상세 동작은 구현 파일에서 확인해야 합니다.'),
        ('DMA의 선택 ID', 'of_dma_configure_id는 device,node,force_dma,const u32 *id를 받아 int를 반환합니다. of_dma_configure wrapper는 앞의 세 인수를 그대로 넘기고 id만 NULL로 지정합니다. NULL은 이 wrapper가 명시적 ID 포인터를 제공하지 않는다는 뜻이며 정수 0을 담은 저장소를 전달하는 것과 다릅니다. DMA 버퍼를 여기서 직접 할당하는 코드는 없습니다.'),
        ('비지원 매칭과 별칭', 'CONFIG_OF 비활성일 때 driver_match는 0,match_device는 NULL입니다. device_modalias와 uevent_modalias는 -ENODEV를 반환하고 출력 문자열이나 env를 수정하는 코드가 없습니다. 일반 uevent는 빈 함수입니다. 모든 비지원 함수가 같은 성공값을 반환한다고 일반화할 수 없습니다.'),
        ('비지원 DMA와 bus ID', '비활성 DMA configure_id와 configure는 둘 다 작업 없이 0을 반환합니다. 이는 호출 흐름에서 오류를 내지 않는 stub이며 OF를 바탕으로 실제 DMA 설정이 수행되었다는 증거는 아닙니다. make_bus_id는 활성일 때 외부 void 선언,비활성일 때 빈 inline입니다.'),
        ('전체 범위와 한계', '매칭 두 API,modalias와 두 uevent API,DMA 두 API,bus ID 함수의 활성·비활성 경로를 모두 대조했습니다. 실행되는 wrapper 본문과 선언만 있는 외부 구현을 구분했습니다. 실제 장치 매칭·DMA 설정·uevent 발생이나 구성별 컴파일 테스트는 실행하지 않았습니다.')
    ], questions=[
        ('of_driver_match_device가 반환하는 것은?', '매칭 포인터가 NULL인지에 따른 int 참·거짓', '항상 매칭 테이블 항목의 주소 자체', '활성 본문은 of_match_device 결과에 !=NULL을 적용합니다. 두 API의 반환 타입과 의미가 다릅니다.'),
        ('ID 없는 DMA wrapper가 하위 함수에 전달하는 id는?', 'NULL', '항상 값 0인 u32 변수의 주소', '코드가 마지막 인수로 NULL을 사용합니다. 선택 인수 부재와 값 0은 구분해야 합니다.'),
        ('OF 비활성에서 modalias와 DMA configure의 반환이 같은가?', '아니다. modalias는 -ENODEV,DMA는 0이다', '그렇다. 둘 다 무조건 -ENODEV다', '구성별 stub을 각 함수 단위로 확인해야 합니다. API마다 호출자에게 전달하는 의미가 다릅니다.'),
        ('비활성 modalias가 str을 빈 문자열로 초기화하는가?', '아니다. 반환문만 있다', '그렇다. 항상 str[0]=0을 실행한다', '출력 인수에 쓰는 코드가 없습니다. 실패 시 출력값이 초기화되었다고 가정하면 안 됩니다.')
    ]
)]
