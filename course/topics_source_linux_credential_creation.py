"""Exec/fork/kernel credential creation and focused setters."""
ROWS = [('exec 자격 준비: effective ID 복사와 keyring 참조 정리',
  '격리·보안',
  'kernel/cred.c',
  'prepare_exec_creds',
  '프로그램 교체 때 이전 실행 문맥의 모든 keyring을 그대로 들고 가면 새 프로그램의 자격 준비 규칙과 맞지 않을 수 있습니다. 일반 자격 복사 위에 exec 전용 정리를 더하는 단계가 '
  '필요합니다.',
  'prepare_exec_creds의 호출자는 cred_guard_mutex를 보유해야 합니다. prepare_creds가 실패하면 그 NULL을 그대로 반환합니다. CONFIG_KEYS에서는 새 '
  '복사본의 thread_keyring과 process_keyring 참조를 각각 key_put하고 NULL로 만듭니다. session_keyring은 이 함수에서 지우지 않습니다. 이어 suid와 '
  'fsuid를 euid에, sgid와 fsgid를 egid에 맞춥니다. 반환은 아직 commit되지 않은 new입니다.',
  '복사본의 euid=1000, suid=2000, fsuid=3000이면 이 단계 후 suid=fsuid=1000입니다. uid 자체를 이 함수가 1000으로 덮는 것은 아닙니다. '
  'process_keyring=NULL은 여기서 새 keyring 객체를 즉시 할당했다는 뜻도 아닙니다.',
  '왜 이 단계가 exec 전체 권한 판정은 아닌가',
  '실행 파일의 특성이나 LSM에 따른 이후 자격 변경과 최종 commit은 다른 실행 경로에 있습니다. 이 helper만으로 setuid 실행의 모든 결과를 예측하면 안 됩니다. 참조를 put하는 '
  '대상은 prepare_creds가 획득한 새 복사본의 소유 참조이므로 이전 공유 객체를 직접 수정하는 것과 구별합니다.',
  ('euid=1000,fsuid=3000인 복사본은 이 단계 후 어떻게 되나요?',
   'fsuid=1000이 됩니다.',
   'euid=3000이 됩니다.',
   '대입 방향은 new->suid = new->fsuid = new->euid입니다.'),
  ('process_keyring을 NULL로 만들면 새 keyring 할당도 완료됐나요?',
   '아닙니다. 기존 참조를 놓고 포인터를 비웠습니다.',
   '그렇습니다. NULL은 새 객체의 주소입니다.',
   '본문에는 이 keyring을 생성하는 호출이 없습니다.')),
 ('fork 자격 복제: 공유 조건과 새 namespace의 실패 정리',
  '격리·보안',
  'kernel/cred.c',
  'copy_creds',
  '자격이 같은 스레드마다 객체를 복제하면 메모리와 참조 관리 비용이 늘지만 thread keyring이나 user namespace가 달라야 할 때는 같은 객체를 그대로 쓸 수 없습니다. 공유 가능한 '
  '경우와 분리해야 하는 경우를 조건으로 나눕니다.',
  'copy_creds는 요청 key 캐시 설정에서 자식의 cached_requested_key를 NULL로 만듭니다. CLONE_THREAD이고 CONFIG_KEYS에서 기존 '
  'thread_keyring이 없으면 get_cred_many(...,2)로 두 자식 포인터용 참조를 얻고 process ucounts를 올려 0입니다. 그 밖에는 prepare_creds를 하며 '
  '실패는 -ENOMEM입니다. CLONE_NEWUSER이면 create_user_ns와 set_cred_ucounts를 차례로 실행하고 음수면 new를 put하고 그 오류를 반환합니다.',
  '새 객체 경로에서 기존 thread_keyring은 참조를 놓고 NULL로 만든 뒤 CLONE_THREAD이면 설치 helper를 호출합니다. 스레드가 아니면 process_keyring도 참조를 '
  '놓고 NULL입니다. 마지막 p->cred와 p->real_cred는 get_cred(new)로 참조 하나를 더 얻어 같은 객체를 가리키며 새 process ucounts를 올립니다. 준비 시 참조 '
  '1과 추가 참조 1이 두 포인터를 담당합니다.',
  '왜 호출된 helper가 실패할 수 있는지까지 확인하나',
  '이 v6.12의 copy_creds는 install_thread_keyring_to_cred(new)의 반환값을 검사하지 않습니다. 연결 helper는 keyring_alloc 실패 시 음수를 '
  '반환할 수 있으므로 이 호출이 있다고 해서 thread keyring 생성 성공을 보장한다고 써서는 안 됩니다. create_user_ns와 ucounts의 ret<0 검사와는 처리 방식이 '
  '다릅니다. CLONE 플래그 조합의 적법성 검증 전체도 이 함수가 혼자 하는 것은 아닙니다.',
  ('공유 경로에서 자식 포인터용으로 몇 참조를 추가하나요?',
   '두 개입니다.',
   '주소가 같으므로 하나입니다.',
   'get_cred_many의 인자가 2이며 real_cred와 cred의 소유 참조입니다.'),
  ('이 버전은 thread keyring 설치 helper의 오류를 ret<0으로 검사하나요?',
   '아닙니다. 이 호출의 반환값은 확인하지 않습니다.',
   '그렇습니다. 모든 호출 오류를 같은 goto로 처리합니다.',
   '원문은 install 호출만 있고 반환값 대입이나 분기가 없습니다.')),
 ('커널 작업용 자격: daemon 기준 복사와 NULL 거절',
  '격리·보안',
  'kernel/cred.c',
  'prepare_kernel_cred',
  '커널 서비스가 다른 작업을 대신할 때 기준이 되는 자격을 명확히 선택해야 합니다. 함수 이름에 kernel이 있다는 이유만으로 언제나 같은 권한을 생성한다고 생각하면 호출 계약을 놓칩니다.',
  'prepare_kernel_cred는 daemon이 NULL이면 WARN_ON_ONCE 후 NULL입니다. slab 할당 실패도 NULL입니다. get_task_cred(daemon)으로 기준 '
  '자격을 참조한 뒤 구조체를 복사하고 non_rcu=0,usage=1로 설정합니다. user·namespace·group 참조를 얻고 CONFIG_KEYS의 네 keyring/auth 포인터는 '
  'NULL, jit_keyring은 thread 기본값으로 둡니다. security 포인터는 보안 설정에서 NULL로 초기화합니다. ucounts 참조와 security_prepare_creds가 '
  '성공하면 old를 put하고 new를 반환합니다.',
  'ucounts나 보안 준비 실패이면 new와 old를 각각 put한 뒤 NULL입니다. CONFIG_KEYS에서 key 포인터를 NULL로 대입하는 것은 복사본이 그 old key들에 대한 참조를 '
  '새로 얻지 않으므로 정리 시 이전 key 참조를 잘못 내려놓지 않게 하는 의미도 있습니다. 반환된 new는 아직 current의 자격으로 설치되지 않았습니다.',
  '왜 prepare_kernel_cred(NULL)을 다른 버전 기억으로 설명하면 안 되나',
  '현재 고정 v6.12는 명시적으로 NULL을 거절합니다. 기준을 init_task로 선택하는 것과 NULL을 전달하는 것은 다릅니다. 다른 daemon을 쓰면 그 자격을 기준으로 복사하므로 항상 '
  'root 자격이 된다고 단정하지 않습니다. 호출자는 입력 task의 수명과 새 자격의 사용·반환 책임도 지켜야 합니다.',
  ('v6.12에서 daemon=NULL이면 init_task로 자동 대체하나요?',
   '아닙니다. 경고 후 NULL을 반환합니다.',
   '그렇습니다. NULL은 항상 root 자격을 뜻합니다.',
   '함수 첫 조건은 WARN_ON_ONCE(!daemon)이며 바로 반환합니다.'),
  ('보안 준비가 실패하면 기준 old 참조도 정리하나요?',
   '그렇습니다. new와 old를 모두 put합니다.',
   '아닙니다. old는 성공 때만 정리합니다.',
   'error label에 put_cred(new), put_cred(old)가 함께 있습니다.')),
 ('파일 접근 자격 비교: ID·그룹 수·배열 순서로 정렬하기',
  '격리·보안',
  'kernel/cred.c',
  'cred_fscmp',
  '일부 파일 접근 문맥에서 두 자격이 같은 UID/GID/보조 그룹 조건을 갖는지 비교해야 합니다. 정렬 가능한 비교 결과를 얻으려면 무엇을 먼저 비교할지 고정해야 합니다.',
  'cred_fscmp는 객체 주소가 같으면 0입니다. 다르면 fsuid, fsgid 순서로 작으면 -1, 크면 1입니다. 이후 group_info 주소가 같으면 0, 한쪽 NULL이면 NULL 쪽이 '
  '작습니다. 둘 다 있으면 ngroups 수를 먼저 비교하고 같을 때 gid 배열을 앞에서부터 비교합니다. 끝까지 같으면 0입니다. 결과는 임의적이지만 안정적인 비교 순서이지 권한의 크기 등급이 '
  '아닙니다.',
  'fsuid와 fsgid가 같고 A 그룹=[100], B 그룹=[1,2]이면 그룹 수 1<2로 A가 먼저라 -1입니다. 첫 그룹 값 100이 1보다 크다는 사실은 이 경우까지 비교하지 않습니다. 둘 '
  '다 길이 2라면 처음 다른 gid 값이 순서를 결정합니다.',
  '왜 0이 모든 보안 문맥까지 동일하다는 뜻은 아닌가',
  '이 함수는 cap_permitted, LSM security, namespace 등 모든 cred 필드를 비교하지 않습니다. 주석의 범위는 mode/uid/gid 기반 파일 접근에 필요한 '
  'fsuid·fsgid·보조 그룹입니다. 또한 그룹 배열을 여기서 정렬하거나 중복 제거하지 않습니다. 호출자가 제공한 정상 group_info 배열을 주어진 순서대로 비교합니다.',
  ('그룹 수가 다르면 그룹 원소부터 비교하나요?',
   '아닙니다. 그룹 수로 먼저 순서를 결정합니다.',
   '그렇습니다. 첫 gid가 언제나 우선입니다.',
   'ngroups 비교가 for 루프보다 앞에 있습니다.'),
  ('cred_fscmp가 0이면 capability와 LSM 정보도 모두 같나요?',
   '그런 보장은 없습니다. 해당 필드를 비교하지 않습니다.',
   '그렇습니다. struct cred 전체를 memcmp합니다.',
   '실제 비교 필드는 fsuid,fsgid와 group_info뿐입니다.')),
 ('사용량 계정 교체: 새 참조 확보 뒤 이전 것을 놓기',
  '격리·보안',
  'kernel/cred.c',
  'set_cred_ucounts',
  'UID나 user namespace를 바꾸면 프로세스 수 등의 사용량을 연결할 계정도 맞춰야 합니다. 먼저 이전 계정을 해제하고 새 계정을 구하면 실패 시 유효한 연결을 잃으므로 확보·교체·해제의 '
  '순서가 필요합니다.',
  'set_cred_ucounts는 old_ucounts의 namespace와 uid가 new의 user_ns·uid와 같으면 바로 0입니다. 원문 주석은 alloc_ucounts의 표 검색이 잠금을 '
  '사용하므로 이 빠른 경로가 필요하다고 설명합니다. 다르면 새 계정을 할당/획득하고 실패하면 -EAGAIN입니다. 성공한 뒤 new->ucounts를 바꾸고 이전 참조를 put한 후 0입니다.',
  '기존 계정 A와 새 UID의 계정 B가 다를 때 B 확보 실패이면 new->ucounts는 여전히 A입니다. B를 얻으면 B로 교체한 뒤 A 참조를 놓습니다. 이 helper는 new->uid나 '
  'new->user_ns를 직접 바꾸지 않고 이미 수정된 값에 계정 포인터를 맞춥니다.',
  '왜 blank cred에 바로 쓰면 안 되나',
  '본문은 old_ucounts->ns와 uid를 곧바로 읽으며 NULL 검사하지 않습니다. 유효한 이전 ucounts가 있는 준비된 객체라는 전제가 필요합니다. 할당 실패 결과가 -ENOMEM일 '
  '것이라고 이름만 보고 추정해서도 안 됩니다. 이 함수가 반환하는 값은 명시적으로 -EAGAIN입니다. process count 자체의 증가·감소 호출은 commit/copy 등 별도 경로에 '
  '있습니다.',
  ('새 계정 확보가 실패하면 이전 포인터는?', '바뀌지 않습니다.', '먼저 NULL로 비워집니다.', '대입과 old put은 새 계정 확보 성공 뒤에만 실행됩니다.'),
  ('alloc_ucounts가 실패했을 때 이 함수의 반환은?', '-EAGAIN입니다.', '무조건 -ENOMEM입니다.', '소스의 조기 반환 상수를 그대로 확인해야 합니다.')),
 ('LSM 자격 설정: 문자열 변환과 부분 변경 후 실패',
  '격리·보안',
  'kernel/cred.c',
  'set_create_files_as',
  '일반 UID/GID와 LSM 보안 문맥은 서로 다른 검사 요소입니다. 둘을 함께 준비하는 helper라도 오류 반환 시 어디까지 바뀌었는지 알아야 안전하게 취소하거나 다시 준비할 수 있습니다.',
  'set_create_files_as는 inode의 uid나 gid가 유효하지 않으면 -EINVAL이고 필드를 바꾸지 않습니다. 유효하면 new의 fsuid와 fsgid에 inode 값을 먼저 '
  '복사하고 security_kernel_create_files_as의 결과를 반환합니다. set_security_override는 security_kernel_act_as를 호출해 결과를 전달합니다. '
  'from_ctx 변형은 strlen 길이로 security_secctx_to_secid를 호출하며 음수면 바로 반환하고 아니면 얻은 secid로 set_security_override를 호출합니다.',
  'LSM의 create-files hook이 오류를 반환해도 앞에서 대입한 fsuid·fsgid는 자동으로 원래 값으로 돌아가지 않습니다. 아직 공개하지 않은 new를 abort하거나 적절히 정리해야 '
  '합니다. 문자열→secid 변환 자체가 실패한 경우에는 act_as까지 호출하지 않습니다.',
  '왜 실제 파일 생성과 현재 task 교체가 아닌가',
  '이 함수들은 전달받은 수정 가능한 자격 객체의 속성을 준비합니다. 파일 생성 syscall을 실행하거나 current->cred를 여기서 바꾸는 함수가 아닙니다. secctx는 strlen이 읽을 '
  '수 있는 NUL 종료 문자열이어야 합니다. 오류를 반환한다는 사실만으로 모든 이전 대입을 롤백했다고 추정하지 않는 습관이 중요합니다.',
  ('create-files 보안 hook이 실패하면 fsuid/fsgid 대입도 자동 취소되나요?',
   '아닙니다. 이 함수에는 되돌리는 코드가 없습니다.',
   '그렇습니다. 음수 반환은 모든 대입을 취소합니다.',
   '두 필드 대입 후 hook을 직접 반환하므로 앞선 변경이 남습니다.'),
  ('secctx 변환이 음수이면 act_as를 호출하나요?',
   '아닙니다. 그 오류를 먼저 반환합니다.',
   '그렇습니다. 실패한 secid도 항상 사용합니다.',
   'ret<0 분기가 후속 호출을 막습니다.'))]

ROWS += [('빈 자격 증명과 초기 자격: 0으로 채우기와 root 설정은 다르다',
  '격리·보안',
  'kernel/cred.c',
  'cred_alloc_blank',
  '나중에 채울 객체를 미리 확보하는 것과 현재 자격을 복사하는 것은 다른 목적입니다. 또 메모리의 모든 비트를 0으로 만드는 것만으로 필요한 참조와 권한 문맥이 완성되는 것은 아닙니다.',
  'cred_alloc_blank는 cred_jar에서 zalloc하고 실패하면 NULL입니다. usage를 1로 만들고 security_cred_alloc_blank를 호출합니다. 보안 준비가 음수면 '
  'abort_creds 후 NULL, 아니면 새 객체를 반환합니다. user·group·namespace 참조를 여기서 현재 자격에서 복사하지 않습니다. cred_init은 cred 구조체용 slab '
  'cache를 만들며 cache-line 정렬, cache 생성 실패 시 panic, memcg 회계 플래그를 지정합니다. SLAB_ACCOUNT는 CONFIG_MEMCG가 없으면 사용하지 않는 '
  '플래그가 됩니다.',
  'blank에서 필드가 0이라는 사실을 prepare_creds와 같은 사용 가능한 복사본이라는 뜻으로 읽으면 안 됩니다. 예를 들어 set_cred_ucounts는 기존 ucounts를 바로 '
  '역참조하므로 blank 객체에 아무 준비 없이 호출하는 전제가 맞지 않습니다. cache 생성의 SLAB_PANIC도 개별 cred 할당의 모든 실패가 panic이라는 뜻은 아닙니다. alloc '
  '함수들은 NULL을 검사합니다.',
  '초기 정적 객체와 파일 구성까지 읽기',
  'init_cred는 usage=4, uid/gid와 saved/effective/filesystem ID들을 GLOBAL_ROOT로 명시합니다. securebits 기본값은 0이며 '
  'inheritable capability는 빈 집합, permitted·effective·bounding은 전체 집합입니다. user는 INIT_USER, namespace는 '
  'init_user_ns, group은 init_groups, 계정은 init_ucounts입니다. 명시하지 않은 정적 필드는 C 규칙상 0으로 초기화됩니다. init_groups usage=2는 '
  '원문 주석에 init_task용 하나와 해제 방지용 하나라고 설명됩니다. kdebug의 활성 #else 매크로는 if(0)의 no_printk여서 일반 실행 로그를 출력하지 않습니다. pr_fmt는 '
  'CRED 접두사를 지정하고 EXPORT_SYMBOL들은 helper를 모듈에서 연결할 수 있게 합니다. include들은 자격·slab·task·key·보안·ID와 알림 선언을 제공하며 SPDX는 '
  'GPL-2.0-or-later입니다.',
  ('blank 할당은 현재 task의 자격을 memcpy하나요?',
   '아닙니다. 0으로 채운 객체와 보안 준비를 제공합니다.',
   '그렇습니다. prepare_creds와 본문이 같습니다.',
   'zalloc 뒤 usage 설정과 보안 hook이 있으며 current 자격 복사는 없습니다.'),
  ('SLAB_PANIC이면 cred_alloc_blank의 NULL 검사는 의미가 없나요?',
   '아닙니다. cache 생성 실패 정책과 개별 객체 할당 실패는 다릅니다.',
   '그렇습니다. 모든 객체 할당은 절대 실패하지 않습니다.',
   'cred_init의 cache 플래그와 zalloc의 실패 반환 경로를 구분해야 합니다.'))]

def register(topic,q,detail):
    for title,area,path,symbol,why,principle,use,dt,body,qa,qb in ROWS:
        topic(title,area,path,symbol,why,principle,use,"복사·공유·임시 변경의 참조 책임과 오류 이후 상태를 구분하세요.",q(title+" · "+qa[0],*qa[1:]),q(title+" · "+qb[0],*qb[1:]),details=[detail(dt,body),detail("검토 범위","Linux v6.12 kernel/cred.c 및 thread keyring 설치 helper 본문을 대조했습니다. 실제 자격 변경이나 keyring 실패를 실행한 검증은 아닙니다.")])
