"""Separate sharing choices for descriptors, signal actions and thread groups."""
ROWS = [
('CLONE_FILES: 파일 번호표 공유와 열린 파일 객체 공유의 차이','copy_files',
 '파일 번호3은 파일 그 자체가 아니라 태스크가 가진 번호표의 한 칸입니다. 부모와 자식이 번호표 전체를 공유하는 경우와 각자 번호표를 가지되 같은 열린 파일 객체를 가리키는 경우를 구분해야 닫기와 새 번호 배정의 영향을 이해할 수 있습니다.',
 'copy_files는 current->files가 없으면0입니다. no_files이면 자식 files를 NULL로 하고0입니다. CLONE_FILES이면 기존 files count를 늘리고 기존에 복사된 포인터를 유지합니다. 그 외에는 dup_fd(oldf,NULL)를 호출하고 오류 포인터면 PTR_ERR을 반환하며 성공하면 자식 files를 새 객체로 바꿉니다.',
 '공유 경로에서는 양쪽이 같은 번호표를 보므로 한쪽의 번호표 변경이 같은 객체에 반영됩니다. 복제 경로에서는 표가 다르지만 dup_fd는 각 비NULL struct file에 get_file하고 같은 포인터를 넣습니다. 따라서 표 복제를 디스크 파일 내용이나 열린 파일 객체의 완전한 복제로 생각하면 안 됩니다.',
 '복제 도중 원래 표가 커질 수 있는 이유',
 'dup_fd는 원래 file_lock을 잡아 크기를 확인하지만 새 배열을 할당할 때 잠금을 풉니다. 다시 잡은 뒤 원래 표 포인터와 크기를 재조회하며 필요하면 반복합니다. 비트맵에 예약됐지만 file 포인터가 아직 NULL인 칸은 자식에서 사용 가능하도록 open 비트를 지웁니다. 남은 포인터 배열은0으로 지우고 새 fdt를 게시합니다. 이 수업은 해당 helper의 연결 범위를 읽은 것이며 fs/file.c 전체 구현 검토는 아닙니다.',
 ('CLONE_FILES 없는 표 복제는 struct file도 새로 만드나요?','아닙니다. 기존 file 참조를 늘려 같은 객체를 가리킵니다.','그렇습니다. 모든 열린 파일을 처음부터 다시 엽니다.','dup_fd의 get_file과 포인터 저장을 보면 표와 그 표가 가리키는 객체의 복제가 다른 수준임을 알 수 있습니다.'),
 ('no_files와 CLONE_FILES가 함께 주어지면 이 helper의 첫 선택은?','no_files 분기에서 자식 files를 NULL로 합니다.','CLONE_FILES 분기로 곧바로 참조를 늘립니다.','부모 files가 있는 경우 no_files 검사가 CLONE_FILES 검사보다 앞에 있어 먼저 반환합니다.')),
('시그널 처리표 복제: SIG_IGN 보존과 마지막 참조 정리','copy_sighand',
 '시그널 번호별 처리 방식은 같은 프로세스 안의 여러 스레드가 함께 볼 수 있습니다. 처리표를 공유할지 복사할지와 이미 무시하기로 한 시그널을 계속 무시할지는 서로 다른 선택입니다.',
 'CLONE_SIGHAND이면 현재 sighand의 refcount만 늘리고0입니다. 복제 경로는 slab에서 새 객체를 얻어 자식 포인터에 넣으며 실패하면 -ENOMEM입니다. count1을 설정하고 부모 siglock을 IRQ 비활성화와 함께 잡아 action 배열을 복사합니다. CLONE_CLEAR_SIGHAND이면 flush_signal_handlers(tsk,0)을 호출합니다.',
 '부모의 두 시그널이 사용자 handler H와 SIG_IGN이라면 CLEAR 뒤 각각 SIG_DFL과 SIG_IGN입니다. 그러나 SIG_IGN의 부가 설정까지 모두 보존하는 것은 아닙니다. flush helper는 모든 항목의 flags를0으로 하고 mask를 비우며 해당 아키텍처의 restorer도 NULL로 합니다.',
 '공유 조건과 해제 조건',
 'copy_process는 CLONE_SIGHAND에 CLONE_VM이 없으면 거절합니다. clone3 인자 검사는 SIGHAND와 CLEAR_SIGHAND를 함께 지정하는 것도 거절합니다. __cleanup_sighand는 마지막 refcount일 때 signalfd_cleanup 후 slab 객체를 반환합니다. 캐시가 SLAB_TYPESAFE_BY_RCU여서 여기서 별도 grace period 대기 없이 반환할 수 있다는 원문 계약이지 모든 RCU 포인터를 즉시 free해도 된다는 뜻은 아닙니다.',
 ('CLEAR일 때 SIG_IGN 항목의 flags도 유지되나요?','아닙니다. handler는 IGN이지만 flags는0으로 지웁니다.','그렇습니다. IGN 항목의 모든 필드는 그대로입니다.','flush_signal_handlers에서 handler 조건과 flags/mask 초기화의 적용 범위가 서로 다릅니다.'),
 ('sighand 참조가2에서1이 되면 slab 객체를 해제하나요?','아닙니다. 마지막 참조일 때만 해제합니다.','그렇습니다. cleanup 호출마다 같은 객체를 free합니다.','refcount_dec_and_test가0인지 확인한 뒤 signalfd 정리와 slab 반환을 수행합니다.')),
('signal_struct 초기화: 처리 함수 표와 스레드 그룹 상태 분리','copy_signal',
 '시그널 처리 함수들의 배열과 스레드 그룹의 대기열·타이머·자원 제한은 역할이 다릅니다. 둘 다 signal이라는 말이 붙지만 각각 다른 구조와 공유 조건을 가지므로 하나의 복사라고 합쳐 생각하면 안 됩니다.',
 'copy_signal은 CLONE_THREAD이면0으로 돌아와 기존 그룹 상태를 사용합니다. 그 외에는 signal_cachep에서0으로 초기화한 객체를 얻고 실패면 -ENOMEM입니다. nr_threads,quick_threads,live,sigcnt를1로 시작하고 그룹 head와 첫 태스크 node를 서로 연결합니다. 자식 종료 대기열,shared_pending,multiprocess 목록,통계 잠금과 이전 CPU 시간을 초기화합니다.',
 '새 그룹의 스레드는 처음1개지만 부모 그룹이 가진 pending 시그널 목록을 그대로 memcpy하지 않습니다. 새 shared_pending을 초기화합니다. 반면 rlim 배열은 부모 group_leader의 task_lock 아래 복사하며 oom_score_adj와 최소값도 계승합니다. 어떤 상태는 새로 만들고 어떤 정책은 물려받는지 분리해서 읽어야 합니다.',
 '타이머와 자격 증명 관련 잠금 연결',
 'POSIX_TIMERS 설정에서는 타이머 목록과 CLOCK_MONOTONIC 상대 hrtimer를 초기화하고 it_real_fn을 지정합니다. CPU 타이머 그룹은 복사한 RLIMIT_CPU의 rlim_cur를 READ_ONCE로 읽어 준비합니다. tty audit과 scheduler autogroup 연결 후 cred_guard_mutex와 exec_update_lock을 초기화합니다. CLONE_THREAD가 SIGHAND를 요구하고 SIGHAND가 VM 공유를 요구하는 상위 검사가 있으므로 이 helper의 조기 반환만으로 임의 플래그 조합이 유효하다고 생각하면 안 됩니다.',
 ('새 그룹은 부모의 shared_pending을 통째로 복사하나요?','아닙니다. 새 pending 상태를 초기화합니다.','그렇습니다. signal_struct 전체를 memcpy합니다.','본문은 zalloc 이후 init_sigpending을 호출하며 복사하는 rlim 배열과 구분합니다.'),
 ('copy_signal의 공유 조기 반환 조건은?','CLONE_THREAD입니다.','CLONE_FILES입니다.','파일 번호표 공유와 스레드 그룹 공유는 독립된 helper와 플래그가 판단합니다.')),
]

def register(topic,q,detail):
    for title,symbol,why,principle,use,dt,body,qa,qb in ROWS:
        topic(title,'프로세스','kernel/fork.c',symbol,why,principle,use,
              '공유하는 표와 표가 가리키는 객체, 새 상태와 계승하는 정책을 구분하세요.',
              q(title+' · '+qa[0],*qa[1:]),q(title+' · '+qb[0],*qb[1:]),
              details=[detail(dt,body),detail('검토 범위','Linux v6.12 fork.c의 파일·시그널 복제와 플래그 검사,fs/file.c dup_fd 및 signal.c flush_signal_handlers를 대조했습니다. 세 파일 전체 해설 완료나 실제 clone·시그널 경쟁 실행을 주장하지 않습니다.')])
