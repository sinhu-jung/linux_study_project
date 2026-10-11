"""Whole-file proc namespace directory and symbolic-link implementation."""
ROWS = [dict(
    path='fs/proc/namespaces.c',
    title='/proc namespace 항목: 디렉터리 탐색·readlink·경로 전환',
    intro='namespace 항목 목록, inode 생성, 디렉터리 lookup·readdir와 링크 접근의 모든 경로를 분석합니다.',
    principle='심볼릭 링크의 표시 문자열을 읽는 작업과 실제 대상 경로로 이동하는 작업은 서로 다른 VFS 연산입니다.',
    use='함수 테이블, 배열 탐색, 재개 가능한 디렉터리 순회, 권한 검사와 task 참조 수명을 연결합니다.',
    area='procfs · VFS · 디렉터리 커서 · 선형 탐색 · 권한 검사 · 참조 수명',
    sections=[
        ('전체 구성과 namespace 목록', 'GPL-2.0 파일은 proc·nsproxy·ptrace·namei·file·각 namespace 인터페이스와 internal.h를 포함합니다. ns_entries는 operation 테이블 포인터 배열입니다. 설정에 따라 net,uts,ipc,pid,pid_for_children,user,항상 mount,조건부 cgroup,time,time_for_children 순서로 구성됩니다. TIME_NS에는 두 항목, PID_NS에도 두 항목이 들어갑니다. mount 항목이 항상 있어 배열이 빈 경우를 따로 처리하지 않습니다.'),
        ('Link follow의 준비 조건', 'proc_ns_get_link는 inode의 PROC_I(inode)->ns_ops를 얻습니다. dentry가 NULL이면 ERR_PTR(-ECHILD)로 반환해 그 문맥에서 직접 진행하지 않습니다. 이후 get_proc_task가 실패하면 -EACCES입니다. -ECHILD를 대상 프로세스에 자식이 없다는 업무 의미로 해석하면 안 됩니다. VFS 링크 조회 문맥의 반환입니다. delayed_call 인수 done은 본문에서 사용하지 않습니다.'),
        ('Link follow의 권한과 경로 전환', 'task를 얻으면 ptrace_may_access(task,PTRACE_MODE_READ_FSCREDS)를 검사하고 거부 시 기본 error=-EACCES를 반환합니다. 통과하면 ns_get_path로 실제 namespace 경로를 얻고 오류이면 끝냅니다. 성공하면 nd_jump_link(&ns_path)로 경로 탐색 대상을 바꿉니다. 마지막에 task 참조를 놓고 ERR_PTR(error)를 반환하므로 error=0이면 NULL입니다. 문자열 버퍼를 만들어 반환하는 링크 구현이 아닙니다.'),
        ('Readlink의 표시 문자열', 'proc_ns_readlink는 inode의 ns_ops와 task를 얻고 없으면 -EACCES입니다. 같은 READ_FSCREDS 권한 검사 뒤 50바이트 지역 name 배열로 ns_get_name을 호출합니다. 음수가 아니면 readlink_copy(buffer,buflen,name) 결과를 반환합니다. 모든 task 획득 후 경로에서 put_task_struct를 수행합니다. 사용자 buffer에 임의로 50바이트를 모두 복사하는 것이 아니라 readlink_copy가 buflen을 받습니다.'),
        ('링크 inode 작업 테이블', 'proc_ns_link_inode_operations는 readlink, get_link, proc_setattr을 연결합니다. readlink는 표시 이름을 사용자 공간에 복사하고 get_link는 실제 nsfs 경로로 이동합니다. 둘 다 이 파일에서 ptrace 접근을 검사합니다. 반면 링크의 모드에 읽기 비트가 있다는 사실만으로 권한 검사를 생략하지 않습니다.'),
        ('Namespace 항목 inode 생성', 'proc_ns_instantiate는 ptr를 proc_ns_operations 포인터로 해석하고 proc_pid_make_inode에 S_IFLNK|S_IRWXUGO를 전달합니다. 실패하면 ERR_PTR(-ENOENT)이며 이 함수에서 -ENOMEM으로 바꾸지 않습니다. 성공하면 inode i_op와 proc_inode ns_ops를 지정하고 pid_update_inode를 호출합니다. 이어 pid_dentry_operations를 연결하고 d_splice_alias 결과를 반환합니다. 여기서 namespace별 새 객체를 clone하는 것은 아닙니다.'),
        ('Readdir 시작과 dot 항목', 'proc_ns_dir_readdir는 file inode에서 task를 얻고 없으면 -ENOENT입니다. 먼저 dir_emit_dots로 점 항목을 내보냅니다. 더 내보낼 수 없으면 task를 놓고 0을 반환합니다. ctx->pos가 2+항목 수 이상이어도 종료합니다. namespace 배열의 첫 index는 ctx->pos-2이며 앞 두 위치가 dot 항목에 대응합니다. 커서를 배열 index로 그대로 쓰지 않습니다.'),
        ('Readdir 재개와 성공 시 전진', 'entry부터 마지막 원소까지 proc_fill_cache에 ops->name,strlen,instantiate callback,task,ops를 전달합니다. false면 break하고 이 반복의 ctx->pos를 증가시키지 않습니다. 성공했을 때만 pos와 entry를 각각 증가시키므로 버퍼가 가득 찬 뒤 다음 호출에서 같은 항목부터 재개할 수 있습니다. 정상 종료 반환은 0이며 실제 디렉터리 항목 전달은 ctx를 통해 일어납니다. 항목 수에 비례하는 순회입니다.'),
        ('디렉터리 파일 작업', 'proc_ns_dir_operations는 generic_read_dir, iterate_shared=proc_ns_dir_readdir, generic_file_llseek를 연결합니다. 링크 inode의 readlink 테이블과 별개입니다. 디렉터리에서 namespace 목록을 나열하는 연산과 특정 항목을 따라가는 연산을 같은 callback이라고 설명하면 안 됩니다.'),
        ('이름 lookup의 선형 탐색', 'proc_ns_dir_lookup는 task를 얻고 기본 결과를 ERR_PTR(-ENOENT)로 둡니다. ns_entries 끝 바로 다음 포인터까지 선형 탐색하면서 strlen(name)==dentry 이름 길이를 먼저 확인하고 memcmp로 해당 길이의 바이트를 비교합니다. 정확히 일치하면 instantiate를 호출하고 task 참조를 놓습니다. 이름 길이가 다른 접두어를 같은 namespace로 취급하지 않습니다. flags 인수는 본문에서 사용하지 않습니다.'),
        ('설정별 항목과 오류·권한 위치', 'lookup은 배열에 없는 이름이나 없는 task이면 -ENOENT입니다. readdir도 task 부재는 -ENOENT지만 link follow와 readlink의 task 부재는 -EACCES입니다. lookup과 readdir 본문에는 앞 링크 함수의 ptrace_may_access 호출이 없으며 실제 링크 접근에서 검사합니다. 이를 디렉터리의 모든 외부 접근 제어가 없다는 주장으로 확대하지 않습니다. 더 넓은 procfs/VFS 정책은 다른 코드에도 있습니다.'),
        ('최종 inode 작업과 검토 범위', 'proc_ns_dir_inode_operations는 lookup, pid_getattr, proc_setattr을 연결합니다. 파일 전체의 배열·세 작업 테이블·링크 함수·instantiate·디렉터리 순회·lookup을 모두 대조했습니다. 배열 탐색은 작은 설정 의존 목록에 대한 선형 알고리즘이며 해시 테이블이 아닙니다. 실제 procfs 접근 권한 조합이나 디렉터리 버퍼 크기별 실행을 테스트한 것은 아닙니다.')
    ],
    questions=[
        ('설정과 관계없이 ns_entries에 들어가는 항목은?', 'mount namespace operation', '항상 모든 열 개 항목', 'mntns_operations는 #ifdef 밖에 있습니다. 다른 항목은 CONFIG에 따라 달라지고 PID·시간 설정은 각각 두 항목을 추가합니다.'),
        ('proc_ns_get_link에서 dentry가 NULL일 때 반환은?', 'ERR_PTR(-ECHILD)', '대상 task를 새로 fork한 결과', '즉시 오류 포인터를 반환하는 VFS 문맥 처리입니다. errno 이름을 프로세스 생성 동작으로 오해하면 안 됩니다.'),
        ('Get_link와 readlink의 핵심 차이는?', '전자는 namespace 경로로 이동하고 후자는 표시 문자열을 복사한다', '둘 다 같은 문자열 포인터를 그대로 반환한다', 'get_link는 ns_get_path와 nd_jump_link, readlink는 ns_get_name과 readlink_copy를 사용합니다.'),
        ('두 링크 접근 함수의 ptrace 모드는?', 'PTRACE_MODE_READ_FSCREDS', 'PTRACE_MODE_READ_REALCREDS', '소스는 FSCREDS를 사용합니다. 앞서 pidfd setns 대상 검증의 REALCREDS와 같은 상수라고 혼동하면 안 됩니다.'),
        ('ctx->pos=3이면 namespace 배열의 어느 index부터 시작하는가?', '1', '3', '앞 두 위치는 dot 항목이므로 entry=ns_entries+(pos-2)입니다. 3-2=1입니다.'),
        ('proc_fill_cache가 false이면 이 반복에서 커서를 증가시키는가?', '아니다. break하여 해당 위치를 유지한다', '그렇다. 실패한 항목을 영구히 건너뛴다', 'ctx->pos++는 성공한 호출 뒤에 있습니다. 재개 가능한 순회에서 빠뜨리는 항목이 생기지 않도록 제어 흐름을 읽습니다.'),
        ('lookup이 이름 길이를 먼저 비교하는 이유는?', '같은 길이의 정확한 이름만 memcmp로 비교하기 위해서다', '항목 이름을 해시값으로 바꾸기 위해서다', '길이 확인과 바이트 비교를 결합한 선형 탐색입니다. 접두어 일치나 해시 기반 조회가 아닙니다.'),
        ('proc_pid_make_inode 실패를 instantiate는 무엇으로 반환하는가?', '-ENOENT 오류 포인터', '항상 -ENOMEM 정수', '실제 코드는 ERR_PTR(-ENOENT)입니다. 내부 할당이 관련되더라도 함수의 반환 오류를 추정으로 바꾸면 안 됩니다.')
    ]
)]
