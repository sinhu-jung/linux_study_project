"""Executable-file reference publication and seccomp inheritance."""
ROWS = [
('실행 파일 참조 바꾸기: 새 참조를 얻고 게시한 뒤 이전 참조 반환','파일시스템','set_mm_exe_file',
 '주소 공간이 기억하는 실행 파일은 /proc의 exe 표시 등에 사용됩니다. 포인터만 새 값으로 덮으면 이전 파일의 참조가 새거나 새 파일이 먼저 해제될 수 있으므로 게시와 참조 소유권 이전의 순서가 필요합니다.',
 'set_mm_exe_file은 기존 포인터를 rcu_dereference_raw로 읽습니다. 새 파일이 있으면 get_file로 참조를 얻고 rcu_assign_pointer로 게시합니다. 이전 파일이 있으면 fput한 뒤0입니다. NULL을 새 값으로 주면 기존 참조만 내려놓는 경로가 됩니다. 이 v6.12 본문에는 실패를 반환하는 분기가 없습니다.',
 '기존 A에서 B로 바꾼다면 B 참조 획득→mm의 포인터를 B로 게시→A 참조 반환 순서입니다. A에서 같은 A로 바꿔도 먼저 획득하고 나중 반환하므로 이 함수의 참조 변화는 상쇄됩니다. 새 값NULL이면 추가 참조 없이 기존 연결을 끊습니다.',
 '왜 이 함수에는 mmap 잠금이 없나',
 '주석의 호출 계약은 마지막 mm 정리처럼 다른 접근자가 없거나,exec에서 새 mm을 아직 공개하기 전처럼 호출자가 동시 갱신을 막는다는 것입니다. RCU 게시 자체가 임의의 동시 쓰기를 직렬화하지는 않습니다. 주석에 새 파일이 있으면 실패할 수 있다는 표현이 있어도 실제 본문은 항상0이므로 이 버전의 구현과 일반 설명을 구별해야 합니다.',
 ('새 값NULL이면 무엇을 하나요?','기존 연결을 NULL로 바꾸고 이전 파일 참조를 반환합니다.','NULL 파일에 get_file을 호출합니다.','get_file은 새 값이 있을 때만 호출되고 기존 fput은 이전 값 유무에 따라 따로 실행됩니다.'),
 ('본문이 반환하는 실패 코드는?','이 버전 본문에는 실패 분기가 없고0을 반환합니다.','새 파일이 있으면 무조건 -ENOMEM입니다.','주석만으로 오류를 만들어 설명하지 말고 실제 return과 호출 경로를 확인해야 합니다.')),
('실행 파일 교체 제한: 경로 비교와 조회 참조의 수명','파일시스템','replace_mm_exe_file',
 '이미 매핑되어 사용하는 이전 실행 파일의 표시를 바꾸는 작업에는 추가 조건이 있습니다. 파일 객체 포인터가 달라도 같은 경로를 나타낼 수 있으므로 VMA의 파일과 이전 실행 파일을 어떤 기준으로 비교하는지 확인해야 합니다.',
 'replace_mm_exe_file은 get_mm_exe_file로 이전 파일 참조를 얻습니다. 있으면 mmap 읽기 잠금 아래 VMA를 순회해 vm_file 없는 것은 건너뛰고 path_equal로 경로가 같으면 -EBUSY입니다. 잠금과 조회 참조를 반환한 뒤 오류면 종료합니다. 통과하면 새 파일을 get_file하고 mmap 쓰기 잠금 아래 현재 exe_file을 다시 읽어 새 포인터를 게시합니다. unlock 뒤 실제로 교체한 이전 파일을 fput합니다.',
 '파일 객체 A와 B의 주소가 달라도 f_path가 같으면 매핑 검사는 busy가 될 수 있습니다. 처음 검사에서 읽은 이전 참조와 쓰기 잠금 안에서 다시 읽은 이전 참조는 역할이 다릅니다. 전자는 검사할 동안의 수명,후자는 실제 교체 대상의 소유권 정리에 사용합니다. 새 파일은 NULL이 아닌 유효한 객체를 전달해야 합니다.',
 'RCU 조회가 반환한 뒤에도 파일을 쓸 수 있는 이유',
 'get_mm_exe_file은 RCU 읽기 구간에서 get_file_rcu를 호출해 참조를 얻습니다. fs/file.c의 helper는 포인터 읽기,0이 아닐 때만 참조 증가,포인터 재확인을 수행하며 바뀌었으면 참조를 반환하고 재시도합니다. get_task_exe_file은 task_lock 아래 mm을 확인하고 PF_KTHREAD이면 제외합니다. 성공 결과는 RCU 구간을 나와도 획득한 참조로 유지되며 사용 뒤 fput이 필요합니다. 검사 읽기 잠금과 교체 쓰기 잠금은 별도 구간이므로 전체를 한 번의 원자적 검사·교체라고 설명하면 안 됩니다.',
 ('VMA 비교는 struct file 포인터 주소만 비교하나요?','아닙니다. path_equal로 f_path를 비교합니다.','그렇습니다. 객체 주소가 다르면 항상 허용됩니다.','원문 비교 인자는 두 파일의 f_path이므로 객체 동일성과 경로 동일성을 구분해야 합니다.'),
 ('get_mm_exe_file 성공 결과를 다 쓴 뒤에는?','fput으로 획득한 파일 참조를 반환합니다.','RCU unlock이 이미 모든 참조를 자동 반환합니다.','RCU 구간과 별도의 file 참조는 다른 수명 보호 수단이므로 반환 책임이 남습니다.')),
('Seccomp 계승: 태스크 복사 후 달라진 보안 상태 다시 맞추기','격리·보안','copy_seccomp',
 '자식 태스크 구조체를 복사한 시점과 보안 상태를 확정하는 시점 사이에 부모의 상태가 바뀔 수 있습니다. 필터 포인터만 계승하고 시스템 호출 검사 표시나 no_new_privs가 예전 상태면 서로 맞지 않는 보안 상태가 만들어집니다.',
 'CONFIG_SECCOMP의 copy_seccomp는 부모 sighand siglock이 잡혀 있음을 assert합니다. get_seccomp_filter로 필터 참조를 확보하고 p->seccomp에 현재 상태를 복사합니다. 부모 no_new_privs가 설정돼 있으면 자식에도 설정합니다. 복사한 mode가 DISABLED가 아니면 자식의 SECCOMP syscall work 표시를 켭니다. 설정이 없는 빌드에서는 본문 동작이 없습니다.',
 '시점1에 태스크를 복사하고 시점2에 부모가 no_new_privs를 켠 뒤 시점3에 siglock 아래 이 함수를 실행했다면 자식에도 다시 설정합니다. 부모가 seccomp mode를 얻은 경우도 실제 복사한 mode를 기준으로 syscall work를 켭니다. 기존 필터의 내용을 다시 작성하거나 새 필터 프로그램을 생성하는 함수는 아닙니다.',
 '왜 자격 증명 mutex와 필터 참조는 별개인가',
 '원문은 자식이 아직 실행 전이어서 exec와 경쟁하지 않으므로 이 경로에서 cred_guard_mutex는 필요하지 않다고 설명합니다. 이는 모든 seccomp 작업에서 그 잠금이 불필요하다는 뜻은 아닙니다. CONFIG_SECCOMP_FILTER의 get_seccomp_filter는 필터가 없으면 반환하고,있으면 refs와 users를 각각 늘립니다. 참조를 공유하는 것과 필터가 적용될 실행 표시를 맞추는 것은 별도로 수행해야 합니다.',
 ('부모 no_new_privs를 다시 확인하는 이유는?','초기 태스크 복사와 siglock 획득 사이에 상태가 바뀔 수 있기 때문입니다.','항상 부모의 보안 제한을 해제하기 위해서입니다.','원문은 필터 상태와 no_new_privs가 함께 맞아야 하므로 설정을 자식에 다시 반영합니다.'),
 ('복사된 mode가 활성 상태면 어떤 표시를 켜나요?','SECCOMP syscall work 표시입니다.','파일 번호표의 close-on-exec 비트입니다.','시스템 호출 경로에서 seccomp 작업이 수행되도록 태스크의 syscall work를 명시적으로 설정합니다.')),
]

def register(topic,q,detail):
    for title,area,symbol,why,principle,use,dt,body,qa,qb in ROWS:
        topic(title,area,'kernel/fork.c',symbol,why,principle,use,
              '참조 획득과 포인터 게시,잠금 구간과 상태 재확인을 따로 추적하세요.',
              q(title+' · '+qa[0],*qa[1:]),q(title+' · '+qb[0],*qb[1:]),
              details=[detail(dt,body),detail('검토 범위','고정 Linux v6.12 fork.c의 실행 파일 참조 및 seccomp 계승과 fs/file.c·kernel/seccomp.c의 관련 helper를 대조했습니다. 각 파일 전체 해설 완료나 실제 보안 경쟁·prctl 실행 검증은 아닙니다.')])
