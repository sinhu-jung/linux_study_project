"""Whole-file PROM callback contracts and tree builder interface."""
ROWS = [dict(
    path='include/linux/of_pdt.h', title='PROM callback 계약: 속성 열거·크기 조회·트리 이동',
    intro='여섯 함수 포인터와 초기 할당·트리 생성 선언 전체를 분석합니다.',
    principle='같은 callback 테이블 안에서도 성공값과 끝 표시의 의미는 함수마다 다릅니다.',
    use='함수 포인터 기반 추상화,버퍼 계약,반환값과 출력 인수의 구분을 학습합니다.',
    area='펌웨어 · C 인터페이스 · 자료구조 · 오류 표현',
    sections=[
        ('헤더와 callback 추상화', 'GPL-2.0+ _LINUX_OF_PDT_H guard 안에 of_pdt_ops 구조체를 정의합니다. 주석은 PROM 호출을 대체 가능한 operations로 표현한다고 설명합니다. 여섯 함수 포인터에 구현을 제공하면 공통 트리 생성 코드가 아키텍처별 펌웨어 호출을 직접 알 필요를 줄일 수 있습니다. 이 헤더 자체에는 callback 구현이나 기본 테이블이 없습니다.'),
        ('속성 열거', 'nextprop는 node,prev,buf를 받고 성공 시 0입니다. prev=NULL이면 첫 속성을 반환하며 버퍼는 32바이트여야 한다는 주석이 있습니다. 시그니처에는 별도 bufsize 인수가 없으므로 호출자와 구현이 고정 크기 계약을 맞춰야 합니다. 이전 속성 이름을 통해 다음 속성을 찾는 방식이며 배열 인덱스 인수를 받지 않습니다.'),
        ('길이와 값 조회', 'getproplen은 node와 속성 이름,getproperty는 여기에 buf와 bufsize를 더 받습니다. 둘 다 성공 시 속성 길이,오류 시 -1이라는 문서 계약입니다. nextprop의 성공값 0과 다릅니다. 길이 0의 속성까지 음수 오류와 같은 것으로 간주하면 API 의미를 잃습니다. 이 헤더는 getproperty가 언제나 추가 NUL을 기록한다고 명시하지 않습니다.'),
        ('트리 이동', 'getchild(parent)와 getsibling(node)은 phandle을 반환하며 자식 또는 형제가 없으면 0이라는 규칙입니다. 커널 device_node *를 직접 반환하는 인터페이스가 아닙니다. 공통 생성기는 이 핸들을 다시 조회하여 부모·자식·형제 포인터로 표현되는 커널 객체를 구성합니다.'),
        ('패키지 경로와 출력 길이', 'pkg2path는 node,buf,const int buflen,int *len을 받습니다. 성공은 0이며 len을 경로 바이트 수로 채운다는 주석입니다. 함수 반환값을 경로 길이라고 해석하면 안 됩니다. buflen은 전달값인 정수이고 len은 호출자 저장소를 갱신할 출력 포인터입니다. 실제 경로 생성·잘림 정책은 callback 구현에서 확인해야 합니다.'),
        ('두 외부 함수와 포함 문맥', 'prom_early_alloc은 unsigned long size를 받아 void *를 반환하며 별도 alignment 인수는 없습니다. of_pdt_build_devicetree는 root phandle과 ops 포인터를 받고 void입니다. 헤더는 phandle 타입을 정의하거나 다른 헤더를 include하지 않으므로 올바른 선행 포함 문맥에 의존합니다. guard,주석,구조체와 두 선언 전체를 대조했으며 실제 PROM 호출 실험은 하지 않았습니다.')
    ], questions=[
        ('nextprop와 getproplen의 성공 반환 의미가 같은가?', '아니다. 전자는 0,후자는 속성 길이다', '그렇다. 둘 다 항상 속성 길이를 반환한다', '테이블에 함께 있는 함수라도 각 주석의 반환 계약을 따로 읽어야 합니다.'),
        ('getchild와 getsibling에서 더 이상 노드가 없다는 표시는?', 'phandle 값 0', '항상 ERR_PTR(-ENOENT)', '반환형은 phandle이며 주석이 종료값 0을 명시합니다. 커널 포인터 오류 관례를 임의로 적용하면 안 됩니다.'),
        ('pkg2path는 경로 길이를 어디에 전달하는가?', 'int *len 출력 인수', '성공 반환값에만', '성공 반환값은 0이고 경로 바이트 수는 출력 저장소에 기록합니다.'),
        ('nextprop 호출에서 버퍼 크기 계약은?', '32바이트 버퍼를 제공한다', 'bufsize 인수로 매번 아무 크기나 전달한다', '해당 callback에는 크기 인수가 없습니다. getproperty와 pkg2path의 시그니처와 구분합니다.')
    ]
)]
