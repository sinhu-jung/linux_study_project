"""Complete ORC register codes and packed entry format."""
ROWS = [dict(
    path='arch/x86/include/asm/orc_types.h',
    title='ORC 메타데이터 형식: 이전 프레임을 찾는 압축 규칙',
    intro='ORC 레지스터 코드와 frame 종류, 부호 있는 offset 및 endian별 bitfield 구조를 전체 헤더로 학습합니다.',
    principle='이 자료는 저장된 stack 자체가 아니라 특정 코드 위치에서 이전 프레임을 복원하는 규칙입니다.',
    use='ORC 테이블 생성 도구와 커널 unwinder가 공유하는 데이터 계약을 이해합니다.',
    area='메타데이터 · 프레임 복원 · 압축 표현 · 비트 필드 · 엔디언 · ABI',
    sections=[
        ('전체 구성과 목적', 'GPL-2.0-or-later, 저작권, guard와 types/compiler include 뒤 ORC_REG 및 ORC_TYPE 상수가 있습니다. C 부분에서는 byteorder.h를 포함하고 packed orc_entry를 정의합니다. 주석은 DWARF CFI를 크게 단순화하여 커널 unwinder가 이전 SP/BP와 때로 entry regs를 쉽게 찾게 하는 형식이라고 설명합니다. 하나의 entry는 하나 이상의 코드 위치에 대응하며 실제 명령어 주소 필드는 이 구조체에 없습니다.'),
        ('이전 SP와 CFA', 'ORC_REG_PREV_SP=1은 호출자가 현재 함수를 호출하기 전의 SP, 즉 DWARF의 CFA에 해당한다고 주석이 정의합니다. 함수 이름이나 반환 주소 값 그 자체가 아닙니다. ORC_REG_UNDEFINED=0은 주석상 해당 register 값이 현재 frame에서 바뀌지 않았음을 표현합니다. 이 설명을 모든 소비 코드의 모든 입력 조합에서 무조건 성공한다는 뜻으로 확대하지 않습니다.'),
        ('기본 레지스터 코드 전체', 'DX=2, DI=3, BP=4, SP=5, R10=6, R13=7, BP_INDIRECT=8, SP_INDIRECT=9입니다. REG_MAX=15는 4비트 표현의 상한이며 10~14에 이 헤더가 각각 이름을 정의한 것은 아닙니다. 주석은 SP/BP를 이전 SP의 기반으로, PREV_SP/UNDEFINED를 이전 BP의 기반으로 자주 사용하고 나머지는 entry 코드나 정렬된 stack의 특수 경우에 필요하다고 설명합니다. 실제 간접 참조 연산은 소비 구현에서 확인해야 합니다.'),
        ('Frame 종류와 register 코드의 구분', 'TYPE_UNDEFINED=0, END_OF_STACK=1, CALL=2, REGS=3, REGS_PARTIAL=4입니다. register 코드와 type은 별개의 필드이므로 숫자 1이 같아도 PREV_SP와 END_OF_STACK의 의미는 다릅니다. signal은 type의 일부 상수가 아니라 별도의 1비트 필드입니다. 이 헤더에는 각 종류를 처리하는 switch나 unwind 종료 본문은 없습니다.'),
        ('부호 있는 offset', 'sp_offset과 bp_offset은 s16입니다. 16비트 부호 있는 값으로 음수 변위도 표현하며 표현 범위는 -32768~32767입니다. stack pointer 전체 주소를 16비트에 저장한다는 뜻이 아닙니다. 기준 register와 offset을 함께 해석하는 규칙이며 부호를 없애고 unsigned로 읽으면 음수 변위 의미가 달라집니다.'),
        ('Little endian bitfield', 'LITTLE_ENDIAN_BITFIELD이면 sp_reg 4비트, bp_reg 4비트, type 3비트, signal 1비트 순서로 선언합니다. 두 register 코드가 같은 8비트 폭 안에 들어가고 type과 signal은 별도의 작은 필드입니다. 각 필드의 폭과 상수의 정의 범위를 구분해야 합니다. type 3비트는 0~7을 표현할 수 있지만 이 파일에서 이름 붙인 type은 0~4입니다.'),
        ('Big endian bitfield', 'BIG_ENDIAN_BITFIELD이면 bp_reg, sp_reg 순서로 각각 4비트를 두고 unused 4비트, signal 1비트, type 3비트를 선언합니다. endian에 따라 선언 순서와 padding 표현을 조정하는 데이터 계약입니다. little endian 쪽에 unused 멤버 선언이 없다는 차이도 있습니다. 임의의 호스트 C bitfield 배치가 항상 동일하다고 가정해 파일을 역직렬화하지 않습니다.'),
        ('Packed와 assembly 경계', '구조체에 __packed를 붙여 compiler의 일반 정렬 padding을 억제하는 형식입니다. 좁은 저장 형식이라고 모든 주소에서 넓은 타입으로 직접 읽어도 된다는 뜻은 아닙니다. __ASSEMBLY__이면 byteorder include와 struct 정의는 제외되지만 앞의 상수 정의는 남습니다. assembly 소비자와 C 소비자가 같은 코드 번호를 공유하도록 분리한 구조입니다.'),
        ('CS 연결과 검증 범위', '실행 코드와 복원 메타데이터를 분리하는 설계, 값 대신 계산 규칙을 저장하는 공간 절약, signed offset, 별개 코드 공간, endian에 따른 bitfield 배치를 학습합니다. 전체 헤더 대조는 objtool이 모든 entry를 올바르게 생성하거나 unwinder가 모든 예외 상태를 복원한다는 실행 검증과는 구분합니다.')
    ],
    questions=[
        ('ORC_REG_PREV_SP는 무엇을 나타내는가?', '호출자가 현재 함수를 호출하기 전의 SP에 해당하는 CFA이다', '현재 함수의 반환 명령어 주소이다', '주석이 이전 frame의 주소를 호출 전 caller SP로 정의합니다. 실행 주소와 stack 위치는 별개의 값입니다.'),
        ('sp_offset이 s16이라는 사실은 stack 주소도 16비트라는 뜻인가?', '아니다. 기준 register에 대한 부호 있는 변위를 저장한다', '그렇다. 전체 kernel stack 주소를 16비트로 잘라 쓴다', '압축된 것은 복원 규칙의 offset입니다. register 코드와 함께 해석하며 음수도 의미가 있습니다.'),
        ('ORC_REG_MAX=15이면 0~15 모두의 register 이름이 정의되어 있는가?', '아니다. 이 헤더에는 10~14의 이름이 없다', '그렇다. 16개 실제 CPU register가 연속으로 모두 정의된다', '필드가 표현할 수 있는 범위와 현재 정의한 코드 집합은 다릅니다. MAX 상수만 보고 없는 의미를 추가하지 않습니다.'),
        ('assembly에서 이 헤더를 사용할 때 struct orc_entry도 그대로 보이는가?', '아니다. 구조체는 __ASSEMBLY__가 아닐 때만 정의된다', '그렇다. C 구조체를 assembly가 자동으로 해석한다', '상수와 C 자료형 영역이 분리되어 있습니다. assembly는 앞부분의 코드 번호를 공유할 수 있습니다.')
    ]
)]
