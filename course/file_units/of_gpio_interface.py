"""Whole-file v6.12 OF GPIO number lookup header."""
ROWS = [dict(
    path='include/linux/of_gpio.h', title='OF GPIO 헤더: 이름 기반 번호 조회와 -ENOSYS stub',
    intro='v6.12 헤더에 실제 남아 있는 단일 조회 API와 포함 의존성을 전체 분석합니다.',
    principle='같은 이름의 API를 비활성 구성에도 제공하면 링크는 가능하지만 기능 수행을 보장하지는 않습니다.',
    use='조건부 컴파일, 인터페이스 호환성, 인덱스와 오류 코드의 구분을 학습합니다.',
    area='GPIO · 장치 트리 · 링크 · 조건부 컴파일',
    sections=[
        ('파일 구성과 의존성', 'SPDX는 GPL-2.0+이며 OF GPIO 도우미라는 설명, MontaVista 저작권과 저자 표기가 있습니다. __LINUX_OF_GPIO_H guard 아래 compiler.h, gpio/driver.h, gpio.h, of.h를 포함하고 device_node를 전방 선언합니다. gpio.h 포함에는 이곳에 있어서는 안 된다는 FIXME 주석이 남아 있지만 실제 include는 존재합니다. FIXME는 코드 제거가 이루어졌다는 뜻이 아닙니다.'),
        ('활성 조회 선언', 'CONFIG_OF_GPIO가 정의되면 of_get_named_gpio(const struct device_node *np, const char *list_name, int index)를 int 반환 외부 함수로 선언합니다. 장치 트리 노드, 속성 목록 이름, 항목 인덱스를 전달하는 형태입니다. 반환값은 GPIO 디스크립터 포인터가 아니며 이 헤더에 플래그 출력 인수나 플래그 열거형은 없습니다. GPIO 요청, 방향 설정, 값 읽기·쓰기도 이 파일의 API 범위가 아닙니다. 구체적인 속성 파싱과 오류 코드의 종류는 구현을 확인해야 합니다.'),
        ('비활성 구현과 링크 목적', 'else 분기에서 errno.h를 포함하고 같은 함수 이름의 static inline을 정의합니다. 두 번째 인수 이름은 propname이지만 타입과 순서는 활성 선언과 같습니다. 본문은 인수를 검사하지 않고 -ENOSYS만 반환합니다. 주석은 드라이버가 GPIO 지원에 엄격하게 의존하지 않아도 링크되게 하려는 목적을 설명합니다. 따라서 호출 코드가 빌드 가능하다는 사실과 조회 기능이 사용 가능하다는 사실을 구분해야 합니다.'),
        ('전체 범위와 타입 계약', 'guard, 라이선스와 주석, 네 include, 전방 선언, CONFIG 조건, 단일 extern과 inline, else의 errno include까지 대조했습니다. index를 int로 선언했다고 범위 검사가 여기서 수행되는 것은 아니며 인수 이름 list_name과 propname의 차이는 함수 호출 규약을 바꾸지 않습니다. 실제 GPIO 번호 조회, 하드웨어 접근 또는 커널 구성별 빌드는 실행하지 않았습니다.')
    ], questions=[
        ('CONFIG_OF_GPIO가 없을 때 of_get_named_gpio가 반환하는 것은?', '-ENOSYS', '유효한 GPIO 번호 0', 'stub은 return -ENOSYS 한 문장입니다. 호출이 가능하도록 인터페이스를 제공하지만 정상 GPIO 조회 결과를 만들지는 않습니다.'),
        ('활성 선언의 list_name과 stub의 propname은 함수 타입을 다르게 만드는가?', '아니다. 같은 위치의 const char * 인수다', '그렇다. 인수 이름이 다르면 호환되지 않는다', 'C 함수의 인수 이름은 타입과 별개입니다. 두 경로 모두 const node 포인터, const char 포인터, int 순서이며 반환 타입은 int입니다.'),
        ('이 v6.12 헤더에 GPIO 플래그 출력 API나 방향 설정 구현이 있는가?', '없다. 이름 기반 GPIO 번호 조회 한 함수만 제공한다', '있다. 모든 GPIO 제어 연산을 inline으로 구현한다', '파일 전체에서 선언·정의하는 함수 이름은 of_get_named_gpio 하나입니다. 과거 버전이나 다른 GPIO 헤더의 기능을 이 파일에 있는 것으로 섞으면 안 됩니다.')
    ]
)]
