"""Additional device frameworks and virtualization lifetimes."""
def register(topic,q,detail):
    topic('CXL·메모리와 장치 프로토콜','주변장치','drivers/cxl/core/region.c','cxl_region_alloc',
      'CPU와 확장 장치의 메모리 자원을 연결하려면 주소 해석·region·장치 의존성을 관리해야 합니다.',
      'CXL은 CXL.io·cache·mem 프로토콜 역할을 나누며 Linux의 region은 host 주소 범위와 장치 decoder 경로를 연결합니다. Interleave는 여러 장치에 주소를 배분하는 규칙입니다. PCIe 장치라는 사실만으로 모든 CXL 프로토콜과 일반 RAM 사용이 가능한 것은 아닙니다.',
      '지원 장치의 topology·decoder·region·memory 상태를 조회합니다. Region 생성과 memory online을 구분하고 장치 제거·오류·보존 자원의 조건을 확인합니다. 실제 메모리 재구성은 학습 환경에서 수행합니다.',
      'cxl_region_alloc의 parent·device 초기화와 decoder·region attach 경로를 읽으세요.',
      q('CXL region 객체가 생성되면 모든 메모리가 즉시 일반 RAM으로 online된 것인가?','주소 연결과 memory 사용 상태를 구분한다','객체 하나면 모든 단계가 끝난다','Decoder·region 구성과 메모리 등록·online은 별도입니다. 실제 사용하는 주소 범위와 allocator 상태를 확인해야 합니다.'),
      q('Interleave가 정하는 것 중 하나는?','주소 조각을 여러 대상 장치에 배분하는 규칙','파일 암호 키를 무조건 바꾸는 것','Ways와 granularity 등은 주소가 어느 target으로 가는지 결정합니다. CPU 가상 주소의 페이지 테이블과는 다른 주소 해석 단계입니다.'),
      details=[detail('Decoder 경로','Host의 root decoder에서 switch·endpoint decoder까지 주소 범위와 target이 맞아야 합니다. Region의 한 객체를 할당했다고 하드웨어 경로 전체가 구성되는 것은 아닙니다.'),detail('Device 수명','device_initialize와 parent 설정 뒤 등록·참조·release가 연결됩니다. 할당 실패 시 memregion id도 정리해야 재시도에서 식별자 자원이 누수되지 않습니다.')])

    topic('Remoteproc·보조 프로세서 관리','주변장치','drivers/remoteproc/remoteproc_core.c','rproc_boot',
      'SoC의 DSP·MCU 같은 별도 프로세서를 Linux가 시작하려면 firmware·메모리·통신 자원을 준비해야 합니다.',
      'Remoteproc은 firmware를 읽고 지원 형식을 해석해 carveout·resource table·virtio 등 자원을 준비한 뒤 platform operation으로 보조 CPU를 시작합니다. Boot 요청 참조와 실제 power 상태·crash 복구는 구분되며 임의 firmware를 무검증 실행하는 API가 아닙니다.',
      '등록된 remoteproc 상태와 firmware 이름을 조회하고 학습 장치에서 boot·shutdown 수명 규약을 따릅니다. Shared memory·IOMMU·interrupt·resource table과 신뢰 경계를 확인합니다.',
      'rproc_boot의 mutex·power 참조·firmware 요청과 platform start를 연결하세요.',
      q('Firmware 파일을 읽었다면 보조 프로세서 부팅의 모든 준비가 끝났는가?','메모리·자원·platform start까지 준비해야 한다','읽기 성공 순간 어떤 CPU든 실행한다','파일 로딩과 resource table·carveout·장치 시작은 다른 단계입니다. 실패한 준비 자원을 역순으로 정리해야 합니다.'),
      q('여러 소비자의 boot 요청과 shutdown을 관리할 때 필요한 것은?','참조와 실제 실행 상태의 균형','마지막 호출 이름만 보관','다른 사용자가 실행 중인 보조 CPU를 한 소비자가 종료하지 않도록 boot 사용 참조와 power 상태를 관리합니다.'),
      details=[detail('Resource table','Firmware가 요청하는 shared memory·virtio 장치 등의 정보를 host가 읽어 자원을 연결합니다. 자원 주소와 크기를 실제 platform 제약에 맞춰 검증해야 합니다.'),detail('Crash 경계','보조 CPU가 죽어도 Linux의 모든 task가 같은 방식으로 죽는 것은 아닙니다. 통신 endpoint·진행 요청·재부팅 정책을 관리해 stale shared memory나 대기자를 처리합니다.')])

    topic('RPMsg·보조 프로세서와 메시지','주변장치','drivers/rpmsg/rpmsg_core.c','rpmsg_send',
      '서로 다른 프로세서가 shared transport 위에서 메시지를 주고받을 때 목적지와 버퍼 수명을 관리해야 합니다.',
      'RPMsg는 endpoint 주소와 callback을 통해 메시지 전달을 추상화합니다. Transport는 virtio 등으로 버퍼·통지를 제공할 수 있습니다. rpmsg_send는 endpoint operation을 호출하며 전송 가능한 버퍼 부족·길이·종료 상태 등의 오류를 처리해야 합니다.',
      '채널·endpoint·송수신 callback과 payload 규약을 정합니다. Blocking send와 trysend의 문맥·반환을 구분하고 remote 입력의 길이·형식을 검증합니다. 신뢰하지 않는 firmware 메시지를 kernel pointer로 해석하지 않습니다.',
      'rpmsg_send의 endpoint·ops 검사와 transport send, endpoint destroy를 연결하세요.',
      q('Endpoint가 없거나 send operation이 없으면 무조건 성공하는가?','-EINVAL·-ENXIO 등 오류를 처리한다','보조 CPU가 자동으로 endpoint를 만든다','래퍼는 ept와 ops->send를 확인합니다. 수신 경로 존재와 전송 기능 지원은 별도 조건입니다.'),
      q('보조 CPU가 보낸 payload 길이를 믿고 구조체로 읽어도 되는가?','길이·형식·권한을 검증해야 한다','shared memory이므로 항상 신뢰된다','별도 실행 주체의 입력은 손상되거나 악의적일 수 있습니다. 버퍼 범위와 프로토콜 조건을 확인합니다.'),
      details=[detail('Endpoint 주소','Endpoint는 로컬·원격 목적지와 callback을 묶습니다. Linux task PID와 RPMsg 주소는 같은 이름 공간이 아닙니다. Message demultiplexing과 사용자 요청 식별을 구분합니다.'),detail('Buffer 부족','가용 송신 버퍼가 없으면 잠들 수 있는 send와 즉시 실패하는 trysend의 규약이 다릅니다. Interrupt·atomic 문맥에서 잠들 수 있는 API를 호출하지 않도록 합니다.')])

    topic('PTP·하드웨어 시계 동기화','주변장치','drivers/ptp/ptp_clock.c','ptp_clock_register',
      '정확한 네트워크 시간 측정에는 OS 호출 지연과 장치 timestamp·clock 조정을 구분해야 합니다.',
      'PTP clock framework는 hardware clock의 시간 조회·설정·주파수 조정·이벤트를 노출합니다. PTP 프로토콜의 timestamp 교환과 servo가 offset·지연을 추정하고 PHC를 조정합니다. Clock 등록 API 자체가 모든 장치 시간을 자동 동기화하는 것은 아닙니다.',
      '/dev/ptpN과 지원 clock info를 조회하고 ptp4l·phc2sys 등의 역할을 구분합니다. Hardware timestamp 지원·네트워크 지연 비대칭·동기화 상태를 확인합니다.',
      'ptp_clock_register의 info capabilities·이벤트 queue·device 등록과 driver adjfine를 연결하세요.',
      q('PTP clock을 등록하기만 하면 원격 clock과 자동으로 정확히 동기화되는가?','프로토콜 교환과 servo·정책이 별도다','등록 순간 모든 시간이 같아진다','Framework는 clock operation을 제공합니다. timestamp 교환·지연 추정·clock 조정 루프가 필요합니다.'),
      q('송수신 timestamp를 장치에서 측정하는 목적 중 하나는?','소프트웨어 경로의 가변 지연 영향을 줄인다','어떤 네트워크 비대칭도 완전히 없앤다','Hardware timestamp는 관찰 위치를 wire에 가깝게 하지만 네트워크 지연과 비대칭 문제까지 자동 제거하지 않습니다.'),
      details=[detail('Offset와 Delay','왕복 시간 교환에서 경로 지연을 추정해 clock 차이를 계산합니다. 양방향 지연이 다르면 대칭 가정의 오차가 생깁니다. 측정값과 가정을 함께 설명해야 합니다.'),detail('PHC와 시스템 시간','PHC와 CLOCK_REALTIME은 별도 clock일 수 있습니다. 어느 clock을 기준으로 다른 clock을 조정하는지 설정하고 timestamp가 어느 기준인지 확인합니다.')])

    topic('IIO·센서 버퍼와 Trigger','주변장치','drivers/iio/industrialio-buffer.c','iio_push_to_buffers',
      '센서의 여러 채널을 일정 시점에 수집하려면 샘플 형식·buffer·trigger를 연결해야 합니다.',
      'IIO는 센서 channel과 raw·scale·offset, scan element와 buffer를 제공합니다. Trigger는 측정 시점을 만들고 driver는 스캔 형식에 맞는 샘플을 buffer에 넣습니다. Channel 선택·endianness·정렬·timestamp에 따라 사용자 해석이 달라집니다.',
      '/sys/bus/iio/devices의 channel·scan_elements·buffer 설정을 조회합니다. enable 전에 실제 scan layout을 확인하고 raw 값에 scale·offset 규약을 적용합니다. Trigger 이벤트와 샘플 완료를 같은 시점으로 무조건 취급하지 않습니다.',
      'iio_push_to_buffers의 buffer_list 순회와 iio_push_to_buffer, scan type을 연결하세요.',
      q('raw=100, offset=-10, scale=0.5라는 단순 (raw+offset)×scale 규약이면 값은?','45','50','(100-10)×0.5=45입니다. 실제 장치의 변환식·단위·signed 형식을 먼저 확인해야 합니다.'),
      q('IIO scan buffer를 읽을 때 모든 채널을 같은 고정 int 배열로 가정해도 되는가?','scan type·순서·정렬·timestamp를 확인한다','모든 센서가 언제나 같은 배열이다','선택한 채널과 보관 비트·유효 비트·endianness·정렬이 레이아웃을 정합니다. 잘못 해석하면 측정값이 틀립니다.'),
      details=[detail('List와 다중 Buffer','iio_push_to_buffers는 연결된 buffer를 순회합니다. 각 buffer의 수명과 push 오류를 확인해야 하며 한 곳의 실패가 어떻게 반환되는지 읽습니다.'),detail('Trigger와 완료','하드웨어 interrupt·timer 등 trigger가 수집 작업을 시작할 수 있습니다. 변환 지연과 timestamp를 어디서 기록했는지에 따라 시간 의미가 달라집니다.')])

    topic('Watchdog·응답 감시와 Reset','주변장치','drivers/watchdog/watchdog_dev.c','watchdog_ping',
      '시스템이 멈췄을 때 소프트웨어 자체의 복구가 불가능할 수 있어 외부 감시 타이머가 필요합니다.',
      'Watchdog은 일정 시간 안에 keepalive가 없으면 reset 등의 동작을 합니다. Core는 사용자 keepalive와 hardware ping 주기를 관리합니다. Window 제한·timeout·pretimeout·nowayout 같은 정책이 있으며 ping 성공만으로 모든 서비스의 건강이 보장되지는 않습니다.',
      '장치 정보와 지원 timeout·정지 가능 여부를 조회합니다. 실제 활성화는 reset될 수 있는 학습 VM·장치에서만 수행하고 daemon이 무엇을 건강 조건으로 보는지 정합니다.',
      'watchdog_ping의 hw_running·last_keepalive와 worker의 hardware ping을 읽으세요.',
      q('시스템이 계속 ping을 보내면 모든 앱의 기능이 정상이라는 증명인가?','ping 가능성과 서비스 건강은 별도다','모든 저장·통신 결과가 올바르다','잘못된 앱 상태에서도 daemon만 살아 있을 수 있습니다. 어떤 건강 검사를 통과해야 keepalive할지 설계해야 합니다.'),
      q('nowayout 장치에서 watchdog을 열고 닫으면 언제나 즉시 멈추는가?','중지 정책과 장치 지원을 확인해야 한다','닫는 순간 모든 watchdog이 반드시 중지한다','Watchdog의 stop·magic close·nowayout 규약은 다릅니다. 무심코 시험하면 timeout 뒤 reset될 수 있습니다.'),
      details=[detail('사용자와 Hardware 주기','사용자 요청의 timeout과 hardware가 허용하는 ping 간격은 다를 수 있습니다. Core worker가 실제 ping을 조정하므로 last_keepalive와 last_hw_keepalive의 의미를 구분합니다.'),detail('Pretimeout','최종 reset 전에 경고 interrupt 등의 동작을 지원할 수 있습니다. 로그·dump 기회를 주지만 멈춘 시스템이 반드시 저장 작업에 성공한다는 보장은 아닙니다.')])

    topic('LED Framework·밝기와 Trigger','주변장치','drivers/leds/led-core.c','led_set_brightness',
      'LED를 여러 장치에서 같은 방식으로 제어하고 이벤트와 깜박임을 연결하려면 공통 수명·문맥 규약이 필요합니다.',
      'LED class는 brightness·max_brightness·trigger를 제공합니다. Software blink의 timer와 brightness 변경이 겹칠 때 상태·workqueue를 조정합니다. 잠들 수 있는 provider와 atomic 문맥의 요청은 다른 실행 경로를 필요로 합니다.',
      '/sys/class/leds의 brightness·max_brightness·trigger를 조회합니다. Trigger가 제어 중이면 수동 값과 충돌할 수 있어 ownership을 확인합니다. 실제 밝기 값과 물리 광량이 선형이라고 가정하지 않습니다.',
      'led_set_brightness의 LED_BLINK_SW·LED_BLINK_DISABLE·set_brightness_work를 읽으세요.',
      q('Interrupt 문맥에서 잠들 수 있는 LED provider를 직접 호출하면 항상 안전한가?','workqueue 등 문맥에 맞는 경로가 필요하다','작은 LED이므로 lock·sleep 제약이 없다','하드웨어 제어가 bus I/O로 잠들 수 있습니다. Brightness 요청의 문맥과 provider operation을 맞춰야 합니다.'),
      q('LED trigger가 활성 상태면 brightness 파일의 숫자만으로 모든 이후 밝기를 결정하는가?','trigger·blink 상태도 확인해야 한다','숫자 저장이 모든 이벤트를 영구 차단한다','Trigger가 상태를 갱신할 수 있습니다. 제어 주체와 blink 종료 규약을 구분해야 관찰 결과를 이해합니다.'),
      details=[detail('Timer와 Work','Software blink timer는 켜짐·꺼짐 전환을 만듭니다. 잠들 수 있는 실제 변경은 work로 넘길 수 있어 timer 종료와 queued work 정리를 같이 관리합니다.'),detail('Disable 경쟁','밝기 0 요청이 blink 해제와 겹칠 수 있습니다. Work flag와 callback 수명을 맞춰 이미 종료한 LED 객체에 작업이 접근하지 않도록 합니다.')])

    topic('PWM·주기와 Duty Cycle','주변장치','drivers/pwm/core.c','pwm_apply_might_sleep',
      '반복 신호의 주기와 켜져 있는 시간을 조절하면 LED·fan·motor 등의 동작을 제어할 수 있습니다.',
      'PWM state는 period·duty_cycle·polarity·enabled를 묶습니다. Duty ratio=duty/period이고 frequency=1/period입니다. Provider의 해상도와 clock 때문에 요청과 실제 신호가 다를 수 있으며 apply_might_sleep은 잠들 수 있는 문맥을 요구합니다.',
      '장치가 사용하는 PWM의 단위·polarity·enable 상태를 확인합니다. 적합한 문맥에서 state를 적용하고 오류와 실제 지원 값을 확인합니다. Motor 등 실제 하드웨어 제어는 안전한 학습 회로에서 합니다.',
      'pwm_apply_might_sleep의 might_sleep과 pwm_state 검증·provider apply를 읽으세요.',
      q('period 1000ns, duty 250ns라면 duty ratio와 주파수는?','25%·1MHz','250%·1Hz','250/1000=0.25이고 1000ns=1µs이므로 1/1µs=1MHz입니다. 단위 변환을 먼저 해야 합니다.'),
      q('pwm_apply_might_sleep을 spinlock을 잡은 atomic 문맥에서 무조건 사용해도 되는가?','잠들 수 있는 API의 문맥 제약을 지킨다','PWM 함수는 모두 atomic이다','Provider가 mutex·bus 작업으로 잠들 수 있습니다. API 이름과 might_sleep 검사가 문맥 요구를 드러냅니다.'),
      details=[detail('Polarity','Normal과 inversed는 active 신호의 방향을 바꿉니다. Duty 숫자만으로 핀의 high 시간을 단정하지 말고 polarity와 provider 규약을 확인합니다.'),detail('State 일괄 적용','period와 duty를 분리해서 바꾸면 중간에 유효하지 않은 조합이 생길 수 있습니다. State를 묶어 검증하고 provider가 지원하는 원자적 전환·오차를 확인합니다.')])

    topic('Counter·하드웨어 계수기','주변장치','drivers/counter/counter-core.c','counter_add',
      '펄스나 회전 위치를 셀 때 signal·count·해석 방식을 공통 인터페이스로 표현해야 합니다.',
      'Counter framework는 signal 입력과 count, synapse의 연결·action·function을 표현합니다. Quadrature 같은 방식은 두 신호의 위상과 edge를 해석합니다. 장치별 width·overflow·enable·event를 관리하며 등록이 실제 측정 시작과 같지는 않습니다.',
      '/sys/bus/counter의 count·function·signal·extension을 조회합니다. 단위·방향·overflow·지원 action을 확인하고 장치 이벤트와 사용자 읽기 사이의 수명을 맞춥니다.',
      'counter_add의 sysfs·chrdev 등록과 driver count_read·function 규약을 연결하세요.',
      q('16비트 unsigned counter가 65535 다음에 자연 wrap하면 값은?','0','65536을 16비트에 그대로 보관','16비트 범위는 0부터 65535입니다. 실제 provider의 saturate·wrap·overflow event 정책은 별도로 확인합니다.'),
      q('Quadrature 해석에서 두 입력 신호의 위상이 필요한 이유는?','edge 순서로 방향과 이동을 해석할 수 있어서','항상 두 전압을 더하기 위해','A·B의 전환 순서가 방향 정보를 줍니다. Function과 action 설정이 한 펄스를 몇 count로 볼지 정합니다.'),
      details=[detail('Synapse','신호를 count 해석과 연결하는 synapse는 단순 값 저장소가 아닙니다. rising·falling·both edge 같은 action과 function이 측정 의미를 정합니다.'),detail('등록 실패 정리','sysfs와 chrdev 등록 중 일부가 실패하면 이미 마련한 부분을 제거해야 합니다. Counter 객체와 parent device의 참조 수명도 실제 하드웨어 접근보다 오래 유지되어야 합니다.')])

    topic('VFIO·장치 할당·격리','가상화','drivers/vfio/group.c','vfio_group_ioctl_get_device_fd',
      '사용자 공간이나 VM에 장치를 맡기려면 MMIO·interrupt·DMA를 허용된 자원으로 격리해야 합니다.',
      'VFIO는 장치 영역·IRQ·DMA mapping 등의 사용자 인터페이스를 제공합니다. IOMMU group은 하드웨어의 격리 경계와 관련되고 iommufd는 I/O 주소 공간 관리에 사용될 수 있습니다. Device FD를 얻는 것만으로 장치의 모든 DMA가 자동 안전한 상태가 되지는 않습니다.',
      '장치 group·driver binding·IOMMU 지원을 확인하고 학습용 장치를 할당합니다. Device FD·DMA address mapping·interrupt 설정·reset·종료 수명을 맞춥니다. 실제 host 필수 장치를 해제하지 않습니다.',
      'vfio_group_ioctl_get_device_fd의 이름·group 상태·device file 준비와 IOMMU 연결을 읽으세요.',
      q('같은 IOMMU group의 장치를 무조건 서로 독립적인 격리 대상으로 볼 수 있는가?','실제 하드웨어 격리 경계를 확인해야 한다','그룹 번호만 같아도 완전 독립이다','그룹은 서로 분리하기 어려운 장치의 격리 단위와 관련됩니다. 안전한 소유와 DMA 경계를 group 조건에 맞춰야 합니다.'),
      q('사용자에게 MMIO 접근을 주는 것과 DMA 메모리 격리는 같은 작업인가?','CPU 영역 접근과 IOMMU DMA mapping은 별도다','MMIO가 열리면 모든 메모리 보호가 완료다','장치가 접근하는 주소 공간은 CPU load/store와 다릅니다. DMA mapping과 장치 수명을 별도로 관리해야 합니다.'),
      details=[detail('API 경로 변화','v6.12의 group device FD 경로는 drivers/vfio/group.c에 있습니다. iommufd 경로와 기존 container/group 경로를 구분하고 실제 사용한 interface의 규약을 따릅니다.'),detail('Reset과 해제','진행 DMA가 끝나기 전에 mapping을 없애거나 사용자 메모리를 해제하면 위험합니다. 장치 정지·reset·IRQ·mapping·FD 수명 순서를 맞춰야 안전한 소유 전환이 됩니다.')])

    topic('Vhost·호스트의 가상 장치 처리','가상화','drivers/vhost/vhost.c','vhost_get_vq_desc',
      'VM의 virtio 요청을 host에서 처리할 때 guest가 준 descriptor와 주소를 검증해야 합니다.',
      'Vhost는 guest의 virtqueue를 host backend가 처리하도록 합니다. Descriptor chain의 주소·길이·NEXT·WRITE·간접 테이블을 확인하고 guest memory를 허용 mapping으로 변환합니다. Guest 제공 값은 신뢰 입력이 아니므로 순환·범위·chain 길이·I/O 방향을 검사해야 합니다.',
      'virtqueue 구조와 avail·used index, memory table·IOTLB 설정을 연결합니다. Backend 종료와 worker·eventfd·guest mapping 수명을 맞춥니다. Vhost 사용과 guest 기능 정답은 별도 검증입니다.',
      'vhost_get_vq_desc의 avail index·descriptor chain·iov_size·방향 검사를 읽으세요.',
      q('guest descriptor가 자기 자신을 NEXT로 가리키면 무조건 끝없이 따라가도 되는가?','chain 개수·순환·범위를 검사해야 한다','guest 입력은 항상 올바르다','악의적 또는 손상된 chain은 host를 멈추거나 범위를 넘길 수 있습니다. Queue size와 chain 제한이 안전 조건입니다.'),
      q('Virtio descriptor의 WRITE 방향은 누구 기준으로 읽어야 하는가?','장치가 해당 buffer에 쓰는지의 규약으로 구분한다','항상 host 파일의 권한 문자열이다','Descriptor는 장치가 읽을 out buffer와 쓸 in buffer를 구분합니다. 잘못된 방향으로 mapping하면 데이터와 보안 계약이 깨집니다.'),
      details=[detail('Ring wrap','16비트 index의 wrap을 고려해 가용 항목 수를 계산합니다. 일반 signed 뺄셈과 무제한 증가를 가정하지 않습니다. Avail·used publication의 메모리 순서도 필요합니다.'),detail('Iovec 변환','Guest 주소가 host의 유효한 사용자 포인터라는 보장은 없습니다. 허용 메모리 범위로 변환하고 한 descriptor가 여러 iovec으로 나뉠 수 있어 출력 배열 용량도 검사합니다.')])

    topic('VSOCK·호스트와 게스트 통신','가상화','net/vmw_vsock/af_vsock.c','vsock_create',
      '가상 머신과 호스트가 별도 IP 설정 없이 socket 형태로 통신할 수 있는 주소 체계가 필요할 수 있습니다.',
      'AF_VSOCK은 CID와 port로 endpoint를 식별하며 지원 transport가 host·guest 연결을 구현합니다. Socket 종류와 transport 기능, 신뢰 경계·권한·연결 수명은 별도입니다. CID는 IP 주소나 Linux PID와 같은 식별자가 아닙니다.',
      '지원 virtio-vsock 등의 환경에서 AF_VSOCK socket·bind·listen·connect 규약을 따릅니다. CID·port·transport 지원과 접근 정책을 확인하고 host 입력을 검증합니다. 모든 VM에서 같은 기능이 제공되는 것은 아닙니다.',
      'vsock_create의 protocol·socket type 검사와 transport 선택·vsock_sock 초기화를 읽으세요.',
      q('VSOCK endpoint를 기본적으로 식별하는 쌍은?','CID와 port','IPv6 주소와 inode 크기','CID는 통신 context를, port는 그 안의 endpoint를 식별합니다. IP 주소 계열과 다른 socket 주소 형식입니다.'),
      q('Host와 guest 사이라는 이유만으로 payload를 무검증 신뢰해도 되는가?','별도 주체의 입력으로 검증한다','가상화 통신이면 모두 같은 권한이다','Host·guest는 서로 다른 신뢰 영역일 수 있습니다. 주소 연결 기능과 프로토콜 인증·입력 검증은 다른 문제입니다.'),
      details=[detail('Transport 차이','Virtio·VMCI 등 transport의 구현과 지원 socket type은 다를 수 있습니다. AF_VSOCK이라는 추상 주소만 보고 모든 기능을 같다고 가정하지 않습니다.'),detail('연결과 수명','Stream의 연결·종료와 datagram의 전달 규약은 다릅니다. Guest reset과 transport 종료 때 대기자·buffer·socket error를 어떻게 처리하는지 읽으세요.')])

    topic('SCX·BPF 스케줄링 확장','스케줄링','kernel/sched/ext.c','scx_ops_enable',
      '스케줄링 정책을 실험하려면 task 선택의 핵심 경계를 유지하면서 정책을 확장할 수 있어야 합니다.',
      'Sched_ext는 BPF sched_ext_ops로 task enqueue·dispatch 등의 정책을 확장합니다. Dispatch queue가 task를 CPU 실행으로 연결하며 core는 task 수명과 progress·오류 감시를 관리합니다. 정책 장애나 정지 상황의 fallback은 사용자가 임의 정책을 무제약 실행한다는 의미와 다릅니다.',
      'v6.12의 CONFIG_SCHED_CLASS_EXT·BPF 지원과 tools/sched_ext 예제를 확인합니다. VM에서 load·활성 상태·오류·fallback을 관찰하고 정책별 latency·처리량·공정성을 비교합니다.',
      'scx_ops_enable의 호환 조건·mutex·task iteration과 DSQ dispatch·disable 경로를 읽으세요.',
      q('BPF 스케줄러 정책을 등록하면 task 수명·진행 보장 검사가 필요 없어지는가?','core의 불변식과 오류·fallback 경계가 필요하다','어떤 정책도 CPU를 무한히 독점해도 안전하다','확장 정책은 커널 task 관리와 연동합니다. Progress·오류·종료에 대한 안전 경계가 유지되어야 합니다.'),
      q('Dispatch queue가 주로 연결하는 것은?','대기 task와 실행 CPU 선택','항상 TCP packet의 암호 키','DSQ는 task를 dispatch하는 스케줄링 경로의 큐입니다. 네트워크 송신 큐와 이름이 비슷해도 역할이 다릅니다.'),
      details=[detail('Ops와 Core','BPF callback은 정책 결정을 제공하고 core는 enqueue 상태·task 소유·CPU 실행 규약을 유지합니다. Callback 하나의 반환만 읽으면 정책 종료·task 이동의 전체 수명을 놓칩니다.'),detail('버전 고정','Sched_ext의 API와 예제는 변화할 수 있으므로 이 교재는 v6.12 원본을 기준으로 합니다. 이후 버전의 callback signature나 기능을 그대로 적용하지 말고 현재 tree의 tools/sched_ext와 함께 확인합니다.')])
