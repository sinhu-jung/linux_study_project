"""Whole-file namespace filesystem ABI and implementation."""
ROWS = [dict(
    path='include/uapi/linux/nsfs.h',
    title='nsfs 사용자 ABI: namespace ioctl과 mount 정보 구조체',
    intro='전체 ioctl 번호와 반환 방식, 고정 폭 구조체와 버전 크기 계약을 구현과 연결해 분석합니다.',
    principle='ioctl의 인코딩 방향·크기 정보와 실제 인수·반환 계약을 함께 확인해야 합니다.',
    use='UAPI 상수, 정수와 사용자 포인터 인수, 확장 가능한 구조체를 구별합니다.',
    area='UAPI · ioctl · 정수 폭 · ABI 버전 · namespace',
    sections=[
        ('전체 정의', 'GPL-2.0 WITH Linux-syscall-note guard 안에서 ioctl.h와 types.h를 포함합니다. NSIO는 0xb7이며 모든 명령이 이 ioctl type을 사용합니다. 함수 구현이나 syscall wrapper는 없고 명령 매크로 열두 개와 mnt_ns_info 구조체, 초기 공개 크기 상수가 있습니다. _IO·_IOR는 호출이 아니라 명령값을 구성하는 매크로입니다.'),
        ('처음 네 명령', '번호 1 USERNS와 2 PARENT는 관련 namespace의 새 FD를 반환합니다. 번호 3 NSTYPE은 CLONE_NEW 계열 타입 값을 반환합니다. 번호 4 OWNER_UID는 user namespace의 owner UID를 호출자의 user namespace 기준으로 얻습니다. 넷 모두 _IO로 정의되지만 확인한 구현에서 OWNER_UID는 arg를 uid_t 사용자 포인터로 받아 put_user로 저장합니다. _IO라고 모든 명령이 인수나 출력 메모리를 사용하지 않는 것은 아닙니다.'),
        ('Mount ID와 PID 변환', '번호 5 MNTNS_ID는 _IOR(...,__u64)로 mount namespace ID를 얻습니다. 번호 6 PID_FROM,7 TGID_FROM,8 PID_IN,9 TGID_IN은 _IOR(...,int)입니다. FROM은 파일이 나타내는 대상 PID namespace에서 호출자 쪽으로, IN은 호출자 쪽에서 대상 namespace로 변환합니다. TGID 계열은 찾은 task의 thread-group leader ID를 구합니다. 구현은 네 변환 명령의 arg를 숫자 PID로 사용하고 결과도 ioctl 반환값으로 전달하므로 int * 출력 버퍼라고 오해하지 않습니다.'),
        ('Mount 정보 구조체', 'mnt_ns_info는 __u32 size, __u32 nr_mounts, __u64 mnt_ns_id 순서입니다. 초기 공개 구조체 크기는 MNT_NS_INFO_SIZE_VER0=16입니다. size는 커널이 알려주는 정보 크기이며 구현에서 허용하는 사용자 크기는 ioctl 명령의 _IOC_SIZE에서 읽습니다. nr_mounts는 구현이 root mount를 제외해 보고하는 값이고 mnt_ns_id는 namespace seq입니다. 프로세스 PID나 ns_common.inum과 동일한 필드가 아닙니다.'),
        ('확장 가능한 세 명령', 'NS_MNT_GET_INFO·NEXT·PREV는 각각 십진 번호 10·11·12와 struct mnt_ns_info를 사용하는 _IOR입니다. 구현에서 INFO는 사용자 정보 포인터가 필요하고 NEXT/PREV는 NULL 정보 포인터로도 FD만 받을 수 있습니다. NEXT/PREV의 성공 반환은 다음·이전 namespace를 연 새 FD입니다. 헤더 자체에는 순회 권한이나 조회 순서를 정하는 코드가 없으며 lookup 구현 계약을 함께 확인해야 합니다.'),
        ('검토 범위', '모든 명령 번호, 인코딩 자료형, 구조체 필드와 크기 상수를 확인했습니다. 고정된 ioctl 숫자를 호스트의 다른 ABI에서 임의 계산해 Linux의 모든 아키텍처 값이라고 주장하지 않습니다. 실제 동작은 fs/nsfs.c의 dispatch와 copy·FD 반환 경로를 별도 학습 항목으로 연결합니다.')
    ],
    questions=[
        ('NS_GET_OWNER_UID는 _IO이므로 사용자 출력 포인터를 전혀 쓰지 않는가?', '아니다. 구현은 arg를 UID 포인터로 보고 값을 저장한다', '그렇다. 항상 UID를 FD 형태로 반환한다', '명령 인코딩만으로 실제 전달 계약을 결정해서는 안 됩니다. OWNER_UID 구현은 put_user를 사용합니다.'),
        ('PID_FROM_PIDNS와 PID_IN_PIDNS의 방향 차이는?', 'FROM은 대상에서 호출자로, IN은 호출자에서 대상으로 변환한다', '둘 다 항상 현재 task 자신의 PID를 반환한다', 'arg로 주어진 PID의 해석 공간과 반환 ID의 공간이 서로 바뀝니다. 다른 task의 ID도 조회 대상이 될 수 있습니다.'),
        ('mnt_ns_info의 최초 공개 크기와 필드 구성은?', '16바이트, u32 두 개와 u64 하나', '12바이트, u32 세 개', 'size·nr_mounts는 32비트, mnt_ns_id는 64비트이며 헤더에 VER0 크기 16을 명시합니다.'),
        ('NS_MNT_GET_NEXT에서 정보 버퍼 없이 성공하면 얻는 것은?', '관련 namespace를 연 파일 디스크립터', '항상 0 하나', '구현은 NULL uinfo이면 정보 복사만 생략하고 열린 FD를 반환합니다. INFO 명령과 NULL 인수 계약이 다릅니다.')
    ]
), dict(
    path='fs/nsfs.c',
    title='nsfs 구현: 참조를 경로와 FD로 바꾸기·ioctl dispatch',
    intro='파일시스템 초기화, namespace 이름과 경로, 전체 ioctl 분기와 자원 소유권을 분석합니다.',
    principle='참조를 가진 객체를 경로·열린 파일·FD로 바꾸는 각 단계에서 소유권 이전과 실패 정리를 구별해야 합니다.',
    use='가상 파일시스템, callback, 사용자 메모리 복사, RCU, 확장 ioctl의 실제 제어 흐름을 읽습니다.',
    area='VFS · 파일 디스크립터 · 소유권 · ioctl · RCU · ABI 확장',
    sections=[
        ('전체 구성과 파일 작업', 'GPL-2.0 파일은 mount·pseudo_fs·file·fs·proc namespace·PID/user namespace·uaccess 등의 인터페이스와 내부 mount.h,internal.h를 포함합니다. static nsfs_mnt를 보관하며 ns_file_operations는 unlocked_ioctl=ns_ioctl, compat_ioctl=compat_ptr_ioctl 두 항목을 지정합니다. 이 테이블에는 일반 read/write 메서드가 없습니다. namespace 파일을 일반 텍스트 데이터 파일로 읽는 구현이 아닙니다.'),
        ('Dentry 이름과 inode 수명', 'ns_dname은 inode->i_private의 namespace에서 ops->name을 얻어 이름:[inode번호] 형태로 dynamic_dname을 호출합니다. ns_dentry_operations는 always_delete_dentry, ns_dname, stashed_dentry_prune을 연결합니다. nsfs_evict는 clear_inode 후 ns->ops->put으로 namespace 참조를 놓습니다. dentry 이름 생성과 namespace 객체의 마지막 수명 처리는 별도 callback입니다.'),
        ('Task에서 경로 얻기', 'ns_get_path_cb는 callback(private_data)로 참조를 가진 namespace를 얻고 NULL이면 -ENOENT, 있으면 path_from_stashed(&ns->stashed,nsfs_mnt,ns,path)를 호출합니다. task adapter는 ns_ops와 task를 담은 작은 구조체에서 get(task)를 호출하고 ns_get_path는 이 adapter를 공통 함수에 전달합니다. 이 경로는 NULL을 검사하며 ERR_PTR를 별도로 검사하는 코드가 아니므로 callback 계약을 구분해야 합니다.'),
        ('Namespace 열기의 참조 소비', 'open_namespace 문서는 성공·실패와 관계없이 입력 ns 참조를 소비한다고 명시합니다. 먼저 path_from_stashed를 호출하는 이유도 그 계약 때문입니다. path는 __free(path_put)로 정리합니다. 이어 O_CLOEXEC로 미사용 FD를 예약하고 dentry_open을 O_RDONLY,current_cred로 수행합니다. 성공하면 fd_install 후 take_fd로 FD 예약의 소유권을 호출자에게 넘깁니다. 중간 실패는 음수 오류를 반환하며 참조를 호출자가 다시 put하는 계약이 아닙니다.'),
        ('관련 namespace 열기', 'open_related_ns는 get_ns(ns)를 호출하고 ERR_PTR이면 PTR_ERR를 반환하며 아니면 open_namespace에 넘깁니다. 여기에는 NULL 검사가 따로 없습니다. owner나 parent를 얻는 callback과 참조 소비 함수의 계약이 맞아야 합니다. 이 함수만 EXPORT_SYMBOL_GPL로 내보냅니다. 단순 조회와 새 FD 생성이 결합된 작업입니다.'),
        ('Mount 정보 복사', 'copy_ns_info_to_user는 kinfo->size=min(usize,sizeof(*kinfo)), mnt_ns_id=mnt_ns->seq, nr_mounts=READ_ONCE(nr_mounts)를 설정합니다. mount 수가 0이 아닐 때만 1을 빼 root mount를 제외하므로 0에서 unsigned underflow하지 않습니다. copy_to_user가 실패하면 -EFAULT, 성공하면 0입니다. 큰 사용자 구조체의 남은 tail을 여기서 전부 0으로 채우는 코드는 없고 알려진 크기까지만 복사합니다.'),
        ('기본 ioctl: owner·parent·type', '첫 switch는 완전한 ioctl 명령값을 비교합니다. USERNS는 ns_get_owner로 관련 namespace를 엽니다. PARENT는 get_parent가 없으면 -EINVAL이며 있으면 해당 callback으로 엽니다. NSTYPE은 ns->ops->type을 그대로 반환합니다. 이들은 모두 사용자 버퍼를 채우는 동일한 작업이 아닙니다.'),
        ('Owner UID와 mount ID 출력', 'OWNER_UID는 namespace type이 NEWUSER가 아니면 -EINVAL입니다. owner를 from_kuid_munged(current_user_ns(),user_ns->owner)로 호출자 공간에 변환하고 uid_t 사용자 포인터에 put_user합니다. MNTNS_ID는 NEWNS만 허용하고 __u64 mnt_ns->seq를 사용자 포인터에 씁니다. namespace 내부 식별자와 owner의 호출자 기준 UID 표현은 서로 다릅니다.'),
        ('PID 변환의 조회 방향', '네 PID ioctl은 NEWPID인지 검사한 뒤 guard(rcu) 구간에서 처리합니다. IN 계열은 find_task_by_vpid(arg)로 호출자 공간에서 입력 PID를 찾고 FROM 계열은 find_task_by_pid_ns(arg,pid_ns)로 파일 대상 공간에서 찾습니다. arg는 사용자 포인터에서 읽어온 값이 아니라 직접 PID 숫자로 사용합니다. PID 반환은 task_pid, TGID 반환은 task_tgid 계열 helper를 씁니다.'),
        ('PID 변환 결과와 못 찾은 경로', '찾은 task에 대해 FROM은 task_pid_vnr 또는 task_tgid_vnr, IN은 task_pid_nr_ns 또는 task_tgid_nr_ns로 출력 공간의 ID를 얻습니다. 결과가 0이면 -ESRCH로 바꿔 반환합니다. 그러나 task를 처음부터 찾지 못했을 때의 if (!tsk) break는 첫 switch를 벗어나 아래 확장 switch로 진행합니다. ret를 -ESRCH로 초기화했어도 이 네 명령 번호는 그 switch의 default에서 -ENOTTY로 덮입니다. 원본의 이 두 실패 경로를 모두 -ESRCH라고 설명하면 틀립니다. 실제 커널 실행 결과를 측정한 것이 아니라 제어 흐름을 대조한 결론입니다.'),
        ('확장 ioctl dispatch의 범위', '두 번째 switch는 _IOC_NR(ioctl)만 비교하며 크기는 _IOC_SIZE로 별도 읽습니다. 여기에는 _IOC_TYPE 또는 _IOC_DIR를 다시 확인하는 분기가 없습니다. 따라서 전체 명령값을 엄격히 비교하는 앞 switch와 동일한 검증이라고 설명하지 않습니다. 확장 명령이 아닌 경우 default는 -ENOTTY입니다.'),
        ('Mount INFO 검증', 'INFO는 0으로 초기화한 kinfo를 준비하고 사용자 포인터와 명령 크기를 얻습니다. NEWNS가 아니거나 uinfo가 NULL이거나 usize가 VER0 16보다 작으면 -EINVAL입니다. 통과하면 공통 복사 helper를 호출합니다. uinfo->size를 먼저 사용자 메모리에서 읽어 허용 크기를 정하는 방식이 아닙니다. 크기 협상은 ioctl 명령의 인코딩을 사용합니다.'),
        ('이전·다음 mount namespace', 'PREV는 previous=true 후 NEXT와 같은 블록으로 fallthrough합니다. NEWNS와 최소 크기를 검사한 뒤 lookup_prev_mnt_ns 또는 lookup_next_mnt_ns를 호출하고 ERR_PTR를 전달합니다. 조회 순서와 권한의 세부 정책은 lookup helper의 책임이며 이 파일만으로 목록이 단순 연결 리스트라고 추정하지 않습니다. 반환 namespace 참조를 path_from_stashed에 넘겨 path 소유권으로 바꿉니다.'),
        ('순회 FD와 선택적 정보', 'NEXT/PREV는 O_CLOEXEC FD를 예약하고 O_RDONLY로 파일을 엽니다. uinfo가 있으면 정보 복사를 수행하며 실패 시 FD를 설치하기 전에 반환합니다. NULL이면 복사를 생략합니다. 성공 시 fd_install(fd,no_free_ptr(f))로 파일 참조를 FD table에 넘기고 take_fd로 FD를 인계합니다. path와 file의 cleanup, 예약 FD cleanup은 소유권을 넘기지 않은 실패 경로를 관리합니다. 이 블록의 f는 __free(fput)이고 초기값은 NULL입니다.'),
        ('이름 조회의 별칭', 'ns_get_name은 ns_ops->get(task)를 호출하고 없으면 -ENOENT입니다. 있으면 real_ns_name이 존재할 때 그것을, 아니면 name을 사용해 이름:[inum]을 snprintf로 쓴 뒤 put합니다. snprintf 반환값을 그대로 돌려주므로 버퍼에 실제 저장된 길이와 항상 같다고 단정하지 않습니다. 앞 ns_dname과 아래 show_path는 real_ns_name 선택 없이 ops->name을 사용합니다.'),
        ('파일 종류와 식별 비교', 'proc_ns_file은 file->f_op가 &ns_file_operations와 같은지 포인터로 비교합니다. 파일 이름 문자열이 namespace처럼 보이는지 검사하지 않습니다. ns_match는 ns->inum==ino와 nsfs superblock s_dev==dev를 모두 요구합니다. inode 번호 하나가 다른 파일시스템에서도 전역적으로 고유하다고 가정하지 않습니다.'),
        ('Superblock과 inode 초기화', 'nsfs_show_path는 ops->name과 inode->i_ino를 seq_file에 출력하고 0을 반환합니다. nsfs_ops는 simple_statfs, nsfs_evict, nsfs_show_path를 연결합니다. nsfs_init_inode는 i_private=data, i_mode에 S_IRUGO 추가, i_fop=ns_file_operations, i_ino=ns->inum을 설정하고 0입니다. 모드 전체를 새 상수로 덮는 것이 아니라 OR합니다.'),
        ('Stashed 자료와 파일시스템 context', 'nsfs_put_data는 ns->ops->put을 호출하고 nsfs_stashed_ops는 init_inode와 put_data 두 callback을 연결합니다. nsfs_init_fs_context는 init_pseudo(fc,NSFS_MAGIC)가 NULL이면 -ENOMEM, 성공하면 context의 ops,dops와 fc->s_fs_info에 stashed operation을 설정합니다. inode 수명과 path 생성 helper가 namespace 참조를 관리하는 연결점입니다.'),
        ('파일시스템 초기화와 검토 범위', 'file_system_type은 name=nsfs, init_fs_context와 kill_anon_super를 연결합니다. __init nsfs_init은 kern_mount하고 ERR_PTR이면 panic하며 성공 시 superblock flags에서 SB_NOUSER를 지웁니다. 이 파일 안에 register_filesystem 호출이 있다고 가정하지 않습니다. 전체 함수·테이블·ioctl·실패 경로를 대조했으며 실제 ioctl 실행·compat ABI·사용자 메모리 fault 주입을 검증한 것은 아닙니다.')
    ],
    questions=[
        ('open_namespace가 실패하면 입력 ns 참조는 호출자가 다시 put해야 하는가?', '아니다. 성공·실패와 관계없이 소비하는 계약이다', '그렇다. 성공했을 때만 소비한다', '문서와 첫 path_from_stashed 호출의 주석이 명시합니다. 소유권 소비 후 다시 put하면 참조 관리가 어긋날 수 있습니다.'),
        ('nr_mounts가 0이면 정보 복사에서 root를 빼고 어떤 값이 되는가?', '0을 유지한다', 'unsigned 최댓값으로 바뀐다', 'if (kinfo->nr_mounts) 조건이 있으므로 0에서는 감소하지 않습니다.'),
        ('PID ioctl의 arg를 구현은 어떻게 사용하는가?', '직접 PID 숫자로 조회 helper에 전달한다', 'int 사용자 포인터로 보고 get_user한다', '네 PID 변환 블록에는 get_user가 없습니다. _IOR 인코딩과 실제 인수 계약을 함께 읽어야 합니다.'),
        ('PID 조회가 task를 처음부터 찾지 못했을 때 이 소스의 최종 흐름은?', '아래 확장 switch default를 거쳐 -ENOTTY가 된다', '초기 ret=-ESRCH를 즉시 return한다', 'if (!tsk)는 return이 아니라 break입니다. 첫 switch 뒤 다른 switch가 ret를 덮으므로 초기값만 보고 오류를 결론내릴 수 없습니다.'),
        ('Task는 찾았지만 변환된 PID가 0이면?', '-ESRCH로 바꿔 직접 반환한다', '항상 새 namespace FD를 연다', '이 경로는 PID 블록 안에서 if (!ret) ret=-ESRCH 후 return합니다. task를 못 찾는 break 경로와 다릅니다.'),
        ('확장 mount ioctl은 무엇으로 dispatch하는가?', '_IOC_NR의 명령 번호', '항상 전체 ioctl 정수값', '두 번째 switch는 번호만 비교합니다. 이 부분에는 type·direction의 별도 검사가 없습니다.'),
        ('NS_MNT_GET_INFO가 구조체 크기로 사용하는 값은?', 'ioctl 명령에 인코딩된 _IOC_SIZE', '사용자 구조체 size 필드를 먼저 읽은 값', 'usize는 _IOC_SIZE(ioctl)로 얻습니다. kinfo->size는 복사할 크기로 나중에 설정하는 출력 필드입니다.'),
        ('NEXT/PREV에서 정보 copy_to_user가 실패하면 FD가 이미 설치되어 있는가?', '아니다. 설치 전에 오류 반환한다', '그렇다. 실패해도 live FD를 반환한다', '정보 복사 뒤에 fd_install이 있습니다. 중간 실패의 path·file·예약 FD는 cleanup 경로가 관리합니다.'),
        ('ns_get_name과 ns_dname의 이름 선택 차이는?', 'ns_get_name은 real_ns_name이 있으면 우선 사용한다', '둘 다 무조건 inode 번호만 출력한다', 'ns_get_name만 real_ns_name 선택을 합니다. ns_dname과 show_path는 ops->name을 사용합니다.'),
        ('proc_ns_file은 namespace 파일임을 무엇으로 판별하는가?', 'file operation 테이블 포인터 동일성', '파일 경로가 /proc으로 시작하는지 여부', '구현은 file->f_op == &ns_file_operations 한 줄입니다. 경로 문자열 기반 판단이 아닙니다.')
    ]
)]
