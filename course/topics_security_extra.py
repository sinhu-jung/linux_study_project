"""Privilege boundaries, measured boot and speculative execution."""
def register(topic,q,detail):
    topic('Landlock·앱이 스스로 적용하는 접근 제한','격리·보안','security/landlock/syscalls.c','SYSCALL_DEFINE2(landlock_restrict_self,',
      '앱이 자신의 권한을 필요한 범위로 좁혀 오류나 침해 이후 접근 가능한 자원을 줄일 수 있어야 합니다.',
      'Landlock은 ruleset을 만들고 허용 규칙을 추가한 뒤 현재 스레드에 domain을 적용합니다. 처리하도록 지정한 접근 종류에 대해 규칙의 허용을 검사합니다. 기존 제한과 새 제한을 겹치면 권한을 더 좁히며 이미 다른 보안 검사에서 거부된 접근을 허용하지 않습니다.',
      'ABI 버전을 조회해 지원 권한 비트를 선택하고 create_ruleset→add_rule→restrict_self 순서로 적용합니다. 필요한 no_new_privs 또는 권한 조건을 따르고 적용 이후 불가역적인 자기 제한을 고려해 학습용 프로세스로 시험합니다.',
      'landlock_restrict_self의 flags 검사·ruleset 참조·credential 교체와 merge를 읽으세요.',
      q('Landlock ruleset을 두 겹 적용하면 이전에 거부된 접근을 새 규칙이 되살리는가?','제한은 겹쳐 적용되어 권한을 넓히지 않는다','새 규칙이 모든 이전 제한을 삭제한다','보안 domain의 계층은 추가 제한으로 작동합니다. 다른 LSM·DAC 검사도 함께 만족해야 합니다.'),
      q('새 커널의 모든 권한 비트를 오래된 커널에 무조건 넘겨도 되는가?','ABI 지원 조회와 오류 처리가 필요하다','모든 비트가 언제나 동일하게 지원된다','지원 버전에 맞게 handled access를 설정해야 합니다. 없는 기능을 성공했다고 가정하면 sandbox가 기대와 다르게 됩니다.'),
      details=[detail('Handled와 Allowed','어떤 접근 종류를 제한할지 ruleset에 지정하고 대상 객체의 allowed access를 규칙에 넣습니다. 두 집합의 역할을 구분해야 제한하지 않은 권한과 제한했지만 허용하지 않은 권한의 차이를 이해합니다.'),detail('Credential과 수명','새 domain은 credential의 보안 상태로 적용됩니다. ruleset FD 참조와 새 credential 준비·오류 시 정리는 별도입니다. 한 스레드에 적용한 정책이 이미 실행 중인 모든 다른 스레드에 자동 적용된다고 가정하지 않습니다.')])

    topic('Yama·Ptrace 접근 정책','격리·보안','security/yama/yama_lsm.c','yama_ptrace_access_check',
      '디버거의 다른 프로세스 메모리 접근은 강한 권한이므로 같은 사용자라는 조건만으로 충분하지 않을 수 있습니다.',
      'Yama는 ptrace_scope 정책으로 추가 ptrace 제한을 적용합니다. relational 모드는 부모·자손 관계나 지정 예외·관련 capability를 확인합니다. capability 필요 모드와 attach 금지 모드는 서로 다르며 Yama 허용이 기본 자격 검사 전체를 대체하지 않습니다.',
      'Linux에서 /proc/sys/kernel/yama/ptrace_scope를 조회합니다. PR_SET_PTRACER 예외와 프로세스 관계를 확인하며 사용자 namespace의 capability 범위를 구분합니다. 보안을 낮추는 전역 설정 대신 학습용 프로세스 관계로 관찰합니다.',
      'PTRACE_MODE_ATTACH와 scope switch, task_is_descendant·ptracer_exception_found를 읽으세요.',
      q('Yama에서 ptrace 접근을 허용하면 다른 모든 기본 권한 검사도 생략되는가?','추가 보안 검사이므로 다른 조건도 만족해야 한다','Yama 하나가 모든 검사를 대신한다','LSM 추가 정책의 허용은 다른 보안 조건의 거부를 무효화하지 않습니다. 여러 검사 경계를 함께 봅니다.'),
      q('Relational 정책이 확인하는 조건 중 하나는?','추적자와 대상의 관계 또는 허용 예외','파일 이름 길이가 짝수인지','코드는 task_is_descendant와 ptracer_exception_found, 관련 namespace capability를 검사합니다. 단순 PID 숫자 크기 비교가 아닙니다.'),
      details=[detail('관계 자료구조','프로세스 parent 연결과 예외 목록을 읽을 때 대상의 생존 여부와 RCU 수명을 고려합니다. PID만 저장하면 종료·재사용으로 다른 프로세스를 혼동할 수 있습니다.'),detail('Attach의 범위','mode가 실제 attach형 접근인지에 따라 정책 검사가 달라집니다. 모든 /proc 조회를 같은 ptrace attach로 설명하면 안 됩니다. 호출자의 구체적인 검사 경로를 따라갑니다.')])

    topic('TPM·측정과 신뢰 루트','격리·보안','drivers/char/tpm/tpm2-cmd.c','tpm2_pcr_extend',
      '부팅 중 무엇을 실행했는지 누적 측정을 남겨 나중에 신뢰한 상태와 비교할 수 있어야 합니다.',
      'TPM의 PCR extend는 기존 PCR과 새 측정 digest를 연결해 해시한 값으로 갱신합니다. 순서가 결과에 반영되며 임의 값 덮어쓰기와 다릅니다. 측정 이벤트 로그·PCR·서명된 quote와 검증자의 정책을 연결해야 원격 검증 의미가 생깁니다.',
      'TPM 도구로 PCR과 event log를 조회하고 bank의 해시 알고리즘과 정책을 확인합니다. 측정했다고 실행을 차단한 것은 아니므로 Secure Boot의 서명 강제와 구분합니다. 실제 PCR 변경·키 정책 변경은 학습용 환경에서 수행합니다.',
      'tpm2_pcr_extend의 command buffer·digest 목록·인증 session·전송 결과를 읽으세요.',
      q('PCR extend는 새 측정값으로 기존 PCR을 단순 덮어쓰는가?','기존 값과 새 digest를 해시해 누적한다','기존 측정은 항상 삭제한다','단순화한 규칙은 PCRnew=H(PCRold||digest)입니다. 순서를 포함해 측정 경로를 누적하는 구조입니다.'),
      q('Measured Boot의 기록이 그 자체로 서명 안 된 코드를 항상 실행 차단하는가?','측정과 실행 허용 정책은 구분된다','기록 기능만 있으면 항상 차단한다','측정은 무엇이 실행됐는지의 증거와 연결됩니다. Secure Boot 등 실행 검증 정책은 별도 경계입니다.'),
      details=[detail('PCR과 Event log','PCR은 누적 요약이고 event log는 각 측정 항목을 설명합니다. 로그를 재생해 계산한 PCR을 quote의 값과 대조해야 누적 요약의 의미를 확인할 수 있습니다.'),detail('Quote의 Freshness','검증자는 nonce 등을 통해 옛 quote 재사용을 구분하고 TPM 키의 신뢰와 정책을 확인합니다. 해시가 같다는 사실만으로 보고서의 출처와 최신성이 확보되지는 않습니다.')])

    topic('Secure Boot·서명 검증과 로딩 경계','격리·보안','kernel/module/signing.c','mod_verify_sig',
      '실행되는 커널과 모듈이 신뢰한 서명 정책을 만족하는지 확인하려면 검증 경계를 나누어 봐야 합니다.',
      'Firmware의 부팅 이미지 검증과 Linux의 모듈 서명 검증은 별도 단계입니다. mod_verify_sig는 모듈 끝의 서명 형식·길이를 확인하고 PKCS#7 서명을 신뢰 keyring에 따라 검증합니다. 서명 존재·암호학적 유효성·키의 신뢰·강제 정책은 각각 다른 조건입니다.',
      'Secure Boot 상태와 module signature enforcement·keyring 설정을 함께 확인합니다. 자기 모듈의 서명 절차는 학습 VM의 신뢰 키 정책으로 시험합니다. 서명된 코드가 기능적으로 안전하거나 버그가 없다는 뜻으로 해석하지 않습니다.',
      'mod_verify_sig의 길이 검사·mod_check_sig·verify_pkcs7_signature와 모듈 로더 강제 정책을 연결하세요.',
      q('파일에 서명 바이트가 붙어 있기만 하면 신뢰한 모듈인가?','형식·서명 유효성·신뢰 키·정책 검사가 필요하다','붙은 서명은 언제나 신뢰된다','올바른 서명도 신뢰하지 않은 키의 것일 수 있습니다. 검증 결과와 실행 정책을 모두 확인해야 합니다.'),
      q('펌웨어 부팅 검증과 mod_verify_sig가 검사하는 대상은 같은가?','부팅 이미지와 실행 중 모듈이라는 별도 경계다','두 함수가 모두 같은 BIOS 설정만 검사한다','모듈 검증은 Linux 로더의 별도 단계입니다. 부팅 체인의 어느 구성요소가 무엇을 신뢰하는지 구분합니다.'),
      details=[detail('길이와 Endianness','모듈 끝의 module_signature에서 sig_len을 big-endian 값으로 읽습니다. 전체 길이보다 큰 서명 길이나 손상 형식을 거부해야 검증 범위가 안전합니다.'),detail('서명과 코드 품질','서명은 정해진 키가 특정 바이트를 승인했다는 성질과 연결됩니다. 메모리 안전·설계 오류·악의적 기능을 자동 증명하지 않습니다. 키 관리와 코드 검토는 다른 책임입니다.')])

    topic('KASLR·커널 주소 랜덤화','격리·보안','arch/x86/boot/compressed/kaslr.c','choose_random_location',
      '커널의 고정 주소를 전제로 하는 공격의 성공을 어렵게 하려면 부팅 때 배치를 달리할 수 있습니다.',
      'KASLR은 부팅 중 허용된 물리·가상 배치 후보에서 무작위 위치를 고릅니다. 커널·initrd·부팅 자료 등 피해야 할 범위와 정렬·크기를 확인합니다. 주소 무작위화는 버그 수정이나 주소 정보 유출 방지를 대신하지 않으며 엔트로피와 후보 수에 한계가 있습니다.',
      '지원 CONFIG_RANDOMIZE_BASE와 부팅 옵션을 확인합니다. nokaslr은 이 경로를 비활성화합니다. 디버깅 시 실제 배치를 고려하며 런타임 주소를 공개 자료에 무심코 노출하지 않습니다.',
      'choose_random_location의 nokaslr·mem_avoid_init·물리 후보·가상 위치 선택을 읽으세요.',
      q('KASLR이 켜지면 메모리 손상 버그 자체가 없어지는가?','주소 예측을 어렵게 할 뿐 버그는 별도다','모든 overflow를 자동 제거한다','주소 배치를 달리하는 방어와 잘못된 메모리 접근을 수정하는 것은 다른 작업입니다. 정보 유출도 방어를 약화시킬 수 있습니다.'),
      q('충분히 큰 빈 공간이면 정렬과 예약 범위를 무시하고 커널을 놓을 수 있는가?','크기·정렬·피해야 할 범위를 모두 만족해야 한다','무작위이므로 모든 주소가 가능하다','무작위 선택도 유효한 후보 안에서 수행됩니다. 예약 자료와 겹치면 부팅 데이터가 손상됩니다.'),
      details=[detail('후보와 엔트로피','후보가 N개라면 균등 선택의 최대 위치 엔트로피는 log2(N)입니다. 실제 입력 엔트로피·정렬·제약이 이를 줄일 수 있습니다. 임의 64비트 주소 전체가 후보인 것은 아닙니다.'),detail('물리·가상 배치','압축 해제의 물리 출력 위치와 실행할 가상 위치는 역할이 다릅니다. 함수 인수 output과 virt_addr를 구분해야 재배치·매핑의 다음 단계를 이해합니다.')])

    topic('Speculation·실행 예측과 완화','격리·보안','arch/x86/kernel/cpu/bugs.c','cpu_select_mitigations',
      'CPU가 예측해 실행한 명령의 결과가 폐기되어도 캐시 같은 흔적이 남아 정보가 드러날 수 있습니다.',
      '추측 실행은 분기나 의존 결과를 기다리는 동안 작업을 진행합니다. 잘못된 예측의 건축적 결과는 되돌려도 미세구조 상태가 관찰될 수 있습니다. 완화는 CPU 특성·microcode·설정에 따라 fence·IBRS·retpoline·상태 정리 등의 서로 다른 기법을 선택합니다.',
      '/sys/devices/system/cpu/vulnerabilities에서 환경의 상태를 조회하고 신뢰 경계·성능을 함께 고려합니다. 하나의 barrier가 모든 Spectre 계열 문제를 해결한다고 가정하지 않습니다. 보안 옵션을 낮추는 시험은 격리 환경에서 합니다.',
      'cpu_select_mitigations의 CPU feature 확인과 spectre_v1·v2 등 별도 선택 함수를 읽으세요.',
      q('예측 실패로 명령 결과가 폐기되면 모든 캐시 흔적도 반드시 사라지는가?','미세구조 흔적이 남을 수 있다','모든 상태가 완전히 원상 복구된다','추측 실행 공격은 건축적 결과와 관찰 가능한 캐시 등 상태의 차이를 이용합니다. 단순 프로그램 결과 검사로 충분하지 않습니다.'),
      q('모든 CPU와 취약점에 같은 완화 하나를 적용하면 충분한가?','특성과 취약점별로 지원·정책을 선택한다','어떤 CPU든 retpoline 하나면 모두 해결된다','소스는 여러 완화 선택을 나눠 수행합니다. 취약점과 하드웨어 지원·microcode·신뢰 경계가 다릅니다.'),
      details=[detail('Spectre 유형 구분','Bounds-check bypass와 branch target injection은 공격의 예측 경계가 다릅니다. 배열 범위 검사 뒤의 의존과 간접 분기 타깃 예측을 서로 바꿔 설명하지 않습니다.'),detail('관찰의 시간','캐시 hit와 miss의 지연 차이를 통계적으로 관찰할 수 있습니다. 건축적으로 반환된 데이터가 없더라도 타이밍이 비밀과 연관되면 문제가 됩니다. 완화의 성능 비용과 보안 조건을 같이 평가합니다.')])
