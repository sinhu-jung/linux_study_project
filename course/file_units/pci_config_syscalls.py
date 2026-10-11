"""Whole-file PCI config read/write syscall checks and user-copy errors."""
ROWS = [dict(
    path='drivers/pci/syscall.c', title='PCI 설정 syscall: 권한·접근 폭·오류 출력의 비대칭',
    intro='다섯 인수 read/write 시스템 호출의 모든 분기와 참조 정리를 분석합니다.',
    principle='하드웨어 접근 실패와 사용자 메모리 복사 실패는 다른 오류이며 실패 출력도 별도 부수 효과입니다.',
    use='권한 검사 순서, 사용자 포인터, 타입별 접근,오류 정규화와 참조 카운트를 학습합니다.',
    area='시스템 호출 · PCI · 권한 · 사용자 메모리 · 오류 처리',
    sections=[
        ('인터페이스와 장치 조회', 'GPL-2.0 파일은 errno,pci,security,syscalls,uaccess와 내부 pci.h를 포함합니다. 두 SYSCALL_DEFINE5는 unsigned long bus,dfn,off,len과 void __user *buf를 받습니다. 두 호출 모두 pci_get_domain_bus_and_slot(0,bus,dfn)으로 도메인0에서 찾으며 별도 domain 인수가 없습니다. 획득한 장치 참조는 사용 후 pci_dev_put으로 내려놓습니다. offset 정렬과 설정 공간 범위의 상세 검증은 하위 pci_user_* 함수에서 확인해야 하며 이 파일에는 별도 비교문이 없습니다.'),
        ('read의 권한·장치·폭 순서', 'read는 err=-EPERM,dev=NULL로 시작하고 CAP_SYS_ADMIN이 없으면 error로 갑니다. 그다음 err=-ENODEV로 설정해 장치를 찾고 없으면 같은 경로입니다. len1,2,4에서 각각 byte,word,dword 읽기를 호출하며 다른 값은 -EINVAL입니다. 읽기 결과가0이 아니면 어떤 하위 오류든 -EIO로 바꿔 error로 갑니다. 길이 검사는 권한과 장치 조회 뒤에 있으므로 여러 조건이 동시에 틀리면 먼저 검사한 조건의 오류가 우선합니다.'),
        ('read의 정상 사용자 복사', '설정 읽기가 성공하면 len에 맞는 u8/u16/u32 __user 포인터로 buf를 캐스팅해 put_user를 호출합니다. 그 결과를 err에 담고 dev put 후 반환합니다. 따라서 하드웨어 읽기는 성공했어도 사용자 복사가 실패하면 그 복사 오류를 반환합니다. 이 실패는 앞의 error 레이블로 돌아가지 않으므로 자동으로 all-ones 출력을 다시 시도하지 않습니다.'),
        ('read의 실패 출력', 'error 레이블은 len1,2,4에 대해서만 각 폭의 put_user(-1)을 시도해0xff,0xffff,0xffffffff 표현을 씁니다. 역사적 XFree86 호환 이유를 주석이 설명합니다. 여기서는 put_user 반환값을 검사하지 않고 기존 err를 보존합니다. 권한 실패도 이 경로에 도달해 유효 폭이면 출력 쓰기를 시도하며,지원하지 않는 len이면 출력 쓰기 자체가 없습니다. 실패 시 반드시 all-ones가 실제 저장된다고 보장할 수는 없습니다.'),
        ('write의 추가 정책 검사', 'write는 !capable(CAP_SYS_ADMIN) 또는 security_locked_down(LOCKDOWN_PCI_ACCESS)가 참이면 즉시 -EPERM입니다. 논리 OR의 단락 평가로 capability가 없으면 뒤 lockdown 호출은 실행되지 않습니다. read에는 이 파일 기준으로 명시적 lockdown 검사가 없습니다. write는 장치가 없으면 -ENODEV로 즉시 반환하며 권한·장치 실패 때 사용자 buf에 쓰는 경로가 없습니다.'),
        ('write의 사용자 입력과 하드웨어 오류', 'len1,2,4에 맞춰 먼저 get_user로 로컬 byte/word/dword를 채웁니다. 복사 오류면 break하여 하드웨어 쓰기를 생략하고 그 오류를 보존합니다. 복사가 성공하면 대응 pci_user_write_config_*를 호출하고0 아닌 결과는 -EIO로 정규화합니다. 다른 len은 -EINVAL입니다. switch 뒤 공통 pci_dev_put과 return이 있어 장치를 찾은 이후의 모든 분기에서 참조를 정리합니다. 버퍼 내용을 되돌리거나 하드웨어 쓰기를 재시도하는 코드가 아닙니다.'),
        ('전체 범위와 실행 한계', '두 시스템 호출,세 폭의 정상·실패 복사,권한 검사,장치 참조와 역사적 주석 전체를 대조했습니다. 접근 폭은 len 값1/2/4이며 임의 길이 배열을 반복 복사하는 루프가 없습니다. 사용자 포인터 직접 역참조 대신 get_user/put_user를 사용하는 경계를 학습합니다. 실제 권한 변경,PCI 설정 쓰기나 시스템 호출 실행은 수행하지 않았습니다.')
    ], questions=[
        ('read 권한이 없고 len=4이면 error 경로가 출력 쓰기를 시도하는가?', '그렇다. put_user(-1)을 시도하되 원래 -EPERM을 반환한다', '아니다. 모든 권한 실패는 error 레이블을 건너뛴다', 'read는 권한 실패를 공통 error로 보냅니다. 출력 저장 성공 여부와 무관하게 기존 err를 보존하는 구조입니다.'),
        ('read 실패 출력의 put_user가 다시 실패하면 반환 오류는?', '기존 권한·장치·설정 접근 오류가 유지된다', '언제나 새 사용자 복사 오류로 교체된다', 'error 레이블의 put_user 반환값은 사용하지 않습니다. 정상 읽기 뒤 복사 경로가 반환값을 저장하는 것과 비대칭입니다.'),
        ('write에서 get_user가 실패해도 PCI 설정 쓰기를 시도하는가?', '아니다. 해당 case에서 break한다', '그렇다. 초기화되지 않은 값을 무조건 쓴다', '각 접근 폭에서 get_user 결과를 먼저 검사합니다. 오류면 하드웨어 쓰기 전에 빠져나가고 공통 참조 해제를 거칩니다.'),
        ('write와 read가 이 파일에서 같은 lockdown 검사를 하는가?', '아니다. 명시적 LOCKDOWN_PCI_ACCESS 검사는 write에 있다', '그렇다. 두 함수 첫 줄에 같은 호출이 있다', '둘 다 capability를 요구하지만 write의 조건에는 추가 보안 훅이 있습니다. 다른 계층의 정책까지 같거나 다르다고 확대하지 않고 이 파일의 명시적 동작을 구분해야 합니다.'),
        ('len=8이 허용되는가?', '아니다. 두 함수 모두 지원 폭은1,2,4다', '그렇다. u64 경로로 자동 분기한다', 'switch에8 case가 없으며 default는 -EINVAL입니다. unsigned long len 타입이 넓다는 사실과 지원하는 접근 폭은 별개입니다.'),
        ('이 호출로 별도 인수를 통해 도메인3을 선택할 수 있는가?', '없다. 장치 조회에 도메인0을 고정 전달한다', '있다. dfn 상위 비트를 항상 도메인으로 해석한다', '본문의 pci_get_domain_bus_and_slot 첫 인수는0입니다. 이 파일에는 별도 도메인 추출 코드가 없습니다.')
    ]
)]
