"""Architecture replacement of the nofault read-address policy."""
def register(topic,q,detail):
    title='x86 nofault 주소 문턱: 사용자 영역·vsyscall·정규 주소'
    topic(title,'CPU·아키텍처','arch/x86/mm/maccess.c','copy_from_kernel_nofault_allowed',
          '공통 메모리 읽기의 기본 weak 허용 함수는 true지만 CPU별 주소 배치에는 접근을 시도하기 전에 걸러야 할 영역이 있습니다. 특히 높은 주소라는 이유만으로 모든 위치가 일반 커널 메모리는 아닙니다.',
          '64비트 x86 구현은 vaddr<TASK_SIZE_MAX+PAGE_SIZE이면 false로 사용자 공간과 guard page를 제외합니다. 다음으로 vsyscall 주소를 거절합니다. 그 뒤 초기 부팅에서 x86_virt_bits가 아직0이면 true이고, 초기화됐으면 __is_canonical_address 결과를 반환합니다. 32비트 구성은 주소가 TASK_SIZE_MAX 이상인지 비교하는 별도 본문을 사용합니다.',
          '설명용 경계 T와 페이지 크기 P에서 T+P-1은 첫 검사로 거절되지만 T+P는 그 검사만 통과합니다. 이후 vsyscall과 정규 주소 검사는 여전히 남습니다. 초기 부팅의 true도 앞의 두 거절 조건을 지난 경우에만 적용되므로 모든 사용자 주소를 무조건 허용하는 분기가 아닙니다.',
          '함수 인자에 size가 있어도 이 x86 본문은 size를 사용하지 않습니다. 시작 주소의 정책 검사가 전체 범위의 매핑·읽기 가능성·유효 수명을 보장하지 않으며, 후속 복사에서 실패할 수 있습니다.',
          q(title+' · 초기 부팅에서는 사용자 영역도 무조건 허용되나요?',
            '아닙니다. 먼저 사용자 영역과 vsyscall을 거절합니다.',
            '그렇습니다. x86_virt_bits가0이면 모든 앞 검사를 건너뜁니다.',
            'true를 반환하는 초기 부팅 분기는 두 조기 거절 검사 뒤에 있으므로 코드 순서를 보존해야 합니다.'),
          q(title+' · 이 구현이 size만큼의 끝 주소도 검사하나요?',
            '아닙니다. size는 이 본문에서 사용하지 않습니다.',
            '그렇습니다. 인자에 size가 있으면 항상 전체 구간을 검사합니다.',
            '실제 판단식은 시작 vaddr와 CPU 주소 규칙만 쓰므로 인자 이름만으로 범위 검증을 추론하면 안 됩니다.'),
          details=[detail('정규 주소란 무엇인가',
                          '64비트 레지스터를 쓴다고 가상 주소의64비트를 모두 주소로 사용하는 것은 아닙니다. CPU가 사용하는 가상 주소 비트 수에 맞는 위쪽 비트 형태를 정규 주소라고 합니다. 이 함수는 고정된48비트 상수로 단정하지 않고 boot_cpu_data.x86_virt_bits를 helper에 넘깁니다. 정규 형태라도 실제 페이지 테이블 매핑이 있다는 뜻은 아닙니다.'),
                   detail('검토 범위',
                          '고정 Linux v6.12 arch/x86/mm/maccess.c의 두 설정별 구현과 공통 mm/maccess.c의 -ERANGE 연결을 대조했습니다. 실제 잘못된 주소 접근이나 초기 부팅 예외를 실행한 실험은 아닙니다. 공통 weak 구현을 x86이 대체하는 연결까지 설명한 수업입니다.')])
