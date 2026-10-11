"""Whole-file x86 CPU query entry and two supporting public headers."""
ROWS = [dict(
    path='arch/x86/entry/vdso/vgetcpu.c',
    title='X86 vDSO getcpu: CPU·NUMA 조회와 무시되는 cache 인수',
    intro='공개 진입점과 weak alias를 전체 분석하고 실제 조회 helper의 역할을 연결합니다.',
    principle='공개 ABI에 남은 인수가 현재 구현에서 사용되지 않을 수 있으며, CPU 위치 조회는 실행 위치를 고정하는 연산이 아닙니다.',
    use='NULL 출력 처리, packed CPU·node 값 분리, 캐시 인수의 실제 사용 여부를 설명합니다.',
    area='CPU affinity · NUMA · vDSO · ABI 호환성 · bit packing · weak alias',
    sections=[
        ('파일 전체', 'GPL-2.0-only와 fast user context getcpu 주석 뒤 linux/kernel.h, linux/getcpu.h, asm/segment.h, vdso/processor.h를 포함합니다. __vdso_getcpu 본문 하나와 getcpu 별칭 선언으로 구성됩니다. 이 파일 자체에 syscall fallback이나 CPU feature 검사 본문은 없습니다.'),
        ('공개 함수와 반환', 'notrace long __vdso_getcpu(unsigned *cpu,unsigned *node,struct getcpu_cache *unused)는 vdso_read_cpunode(cpu,node)를 호출하고 0을 반환합니다. notrace는 추적 계측을 피하려는 함수 표식이며 메모리 접근 안전성을 보증하지 않습니다. 사용하지 않는 세 번째 인수는 이름도 unused이고 본문에서 읽거나 쓰지 않습니다.'),
        ('조회 helper와 명령 선택', '교차 확인한 asm/segment.h의 vdso_read_cpunode는 기본 LSL 명령으로 CPU·node 인코딩 값을 얻고 RDPID 기능이 있으면 대체 명령을 사용합니다. helper가 값을 마스크와 shift로 나누어 출력합니다. 이 부분은 호출 관계를 설명하기 위한 확인이며 큰 segment.h 전체를 함께 완료 처리하지 않습니다.'),
        ('출력 포인터와 조회의 한계', 'helper는 cpu가 NULL이 아니면 CPU 부분을, node가 NULL이 아니면 node 부분을 기록합니다. 둘 다 NULL이어도 wrapper에는 별도 오류 반환 경로가 없습니다. NULL이 아닌 잘못된 주소까지 안전하게 처리한다는 보장은 아니며 이 사용자 공간 코드의 쓰기가 fault를 낼 수 있습니다. 조회 후 scheduler가 task를 이동시키지 못하게 하는 affinity 설정이나 잠금도 없습니다.'),
        ('캐시 ABI와 별칭', 'getcpu는 같은 세 인수·long 반환형의 weak alias로 __vdso_getcpu에 연결됩니다. tcache라는 인수 이름이 붙어도 별도 캐시 관리 본문이 생기지 않습니다. getcpu_cache 헤더의 역사적 캐시 설명을 현재 wrapper가 실제 수행한다고 가정하면 안 됩니다. NULL cache가 CPU 위치를 영구히 고정하는 보장도 아닙니다.'),
        ('CS 연결과 범위', '전체 함수·속성·include·별칭을 대조했습니다. 인터페이스 호환성, 메모리 포인터와 optional 출력, CPU 조회와 실행 위치 고정의 차이가 핵심입니다. 실제 x86 CPU feature별 실행이나 task migration 재현 시험은 수행하지 않았습니다.')
    ],
    questions=[
        ('세 번째 getcpu_cache 인수는 현재 이 wrapper에서 어떻게 사용하는가?', '사용하지 않는다', '매 호출마다 캐시를 업데이트하고 CPU 번호를 저장한다', '본문은 cpu와 node만 helper에 넘깁니다. 선언에 cache 자료형이 남아 있다는 사실과 실제 동작은 구분해야 합니다.'),
        ('node만 필요할 때 cpu=NULL이면 helper는 어떻게 하는가?', 'CPU 출력 쓰기를 생략하고 NULL이 아닌 node에 기록한다', '반드시 두 포인터가 모두 있어야 하므로 wrapper가 -EINVAL을 반환한다', '확인한 helper는 각 포인터를 별도로 검사합니다. wrapper의 정상 반환은 0이며 잘못된 non-NULL 주소의 안전성까지 보장하는 것은 아닙니다.'),
        ('getcpu 호출 뒤 같은 CPU에서 계속 실행됨이 보장되는가?', '아니다. 조회는 affinity 고정이나 migration 금지가 아니다', '그렇다. 성공 반환이 CPU 잠금을 획득한다', '값을 읽는 것과 scheduler의 이후 배치를 제한하는 것은 다른 작업입니다. 이 파일에는 CPU 고정 동작이 없습니다.')
    ]
), dict(
    path='include/linux/getcpu.h',
    title='Getcpu cache 자료형: 고정 크기와 opaque 계약',
    intro='캐시 구조체 전체와 역사적 주석을 현재 getcpu 구현과 구별합니다.',
    principle='내부 필드를 노출하지 않는 고정 크기 저장 영역은 ABI를 유지하면서 구현을 바꿀 수 있게 합니다.',
    use='sizeof에 따른 배열 길이와 사용자 코드가 의존해선 안 되는 내부 표현을 설명합니다.',
    area='Opaque 데이터 · ABI · sizeof · 스레드별 저장 · 호환성',
    sections=[
        ('전체 정의', 'GPL-2.0과 _LINUX_GETCPU_H를 1로 정의하는 guard 아래 getcpu_cache 구조체 하나만 있습니다. 멤버는 unsigned long blob[128 / sizeof(long)]입니다. 별도 include·함수·할당·캐시 갱신 구현은 없습니다.'),
        ('바이트 수와 원소 수', '일반적인 Linux ABI에서 long이 4바이트이면 배열은 32개, 8바이트이면 16개 원소로 멤버 저장 공간은 128바이트입니다. unsigned long도 해당 long과 같은 크기를 사용합니다. 배열 원소 개수 128이라는 선언이 아니며 각 원소를 CPU·node·timestamp 필드로 해석할 정의도 없습니다.'),
        ('주석의 opaque 계약', '주석은 사용자 프로그램이 내부 내용을 참조하지 말아야 하고 향후 바뀔 수 있는 private cache이며 스레드별 저장을 요구한다고 설명합니다. 결과가 짧은 시간 뒤처질 수 있고 NULL로 캐시를 피하라는 설명도 있습니다. 이는 구조체의 역사적 사용 계약이며 헤더 자체가 캐시의 유효성이나 정확도를 검사하지 않습니다.'),
        ('현재 구현과 구별', '확인한 v6.12 x86 __vdso_getcpu는 cache 인수를 무시하고 CPU·node helper를 호출합니다. 따라서 이 주석을 현재 x86에서 cache를 실제 사용하는 증거로 삼으면 안 됩니다. 또한 주석의 정확성 표현을 조회 이후 CPU migration까지 막는 절대 보장으로 확대하지 않습니다. 전체 구조체와 주석을 분석했으며 다른 모든 아키텍처의 캐시 소비를 검증한 것은 아닙니다.')
    ],
    questions=[
        ('sizeof(long)=8일 때 blob 원소 개수는?', '16개이다', '128개이다', '배열 길이는 128/sizeof(long)입니다. 16개의 8바이트 원소가 128바이트를 차지합니다.'),
        ('사용자 프로그램이 blob[0]을 특정 CPU 번호 필드로 사용해도 되는가?', '안 된다. 주석은 내부 표현에 의존하지 말라고 명시한다', '된다. 헤더에 CPU 번호가 첫 원소라고 정의되어 있다', '이 구조체는 opaque 저장 공간으로 설명됩니다. 멤버의 의미를 임의로 고정하면 구현 변경과 호환되지 않습니다.')
    ]
), dict(
    path='include/vdso/processor.h',
    title='vDSO processor 헤더: C 문맥의 아키텍처 정의 전달',
    intro='include guard와 assembly 제외 조건의 전체 동작을 분석합니다.',
    principle='공통 이름의 헤더는 실제 아키텍처 구현으로 의존성을 전달하는 역할을 할 수 있습니다.',
    use='헤더 이름만으로 실행 기능을 추정하지 않고 포함 조건을 읽습니다.',
    area='전처리 · 헤더 의존성 · 아키텍처 추상화',
    sections=[
        ('전체 구조', 'GPL-2.0-only와 저작권 표기 뒤 __VDSO_PROCESSOR_H guard가 있습니다. !__ASSEMBLY__일 때만 asm/vdso/processor.h를 포함합니다. 별도 상수·구조체·함수 본문은 없습니다.'),
        ('C와 assembly 포함 차이', '__ASSEMBLY__가 정의된 문맥에서는 아키텍처 processor 헤더를 이 경로로 포함하지 않습니다. 정의되지 않은 C 문맥에서는 선택된 아키텍처 헤더가 필요한 정의를 제공합니다. 이 조건은 런타임 CPU 모드 검사나 system call 전환이 아닙니다.'),
        ('분석 범위', '이 파일 자체가 CPU 번호를 읽거나 spin 대기 명령을 실행하는 것은 아닙니다. 포함된 헤더의 실제 정의는 아키텍처별로 확인해야 합니다. 전체 guard와 조건·include를 설명했고 포함 대상 전체를 새로 완료 집계하지 않습니다.')
    ],
    questions=[
        ('__ASSEMBLY__가 정의되면 이 헤더가 asm/vdso/processor.h를 포함하는가?', '아니다. 해당 include는 !__ASSEMBLY__ 안에 있다', '그렇다. guard는 모든 조건을 무시하고 포함한다', '외부 include guard와 내부 언어 문맥 조건은 별개입니다. 실제 포함 여부는 두 조건을 따라 결정됩니다.'),
        ('이 파일에 CPU 번호 조회 함수 본문이 있는가?', '없다. 아키텍처 헤더로 의존성을 전달한다', '있다. 이름이 processor이므로 CPU 조회를 반드시 직접 구현한다', '파일 이름보다 실제 내용을 봐야 합니다. 여기에는 조건부 include만 있습니다.')
    ]
)]
