"""Open-policy gates, parent dentry references and writeback waiting."""
ROWS = [
('파일 열기 정책: 종류·권한·append-only·NOATIME의 순서','파일시스템','fs/namei.c','may_open',
 '읽기·쓰기 권한 비트가 맞아도 디렉터리를 쓰기 파일처럼 열거나 append-only 파일을 잘라 쓰면 안 됩니다. VFS는 대상 종류와 요청 플래그의 조합까지 검사해 열기 정책을 맞춥니다.',
 'may_open은 inode가 없으면 -ENOENT, 이 단계에 남은 symlink는 -ELOOP입니다. 디렉터리 쓰기는 -EISDIR, 실행 요청은 -EACCES입니다. 블록·문자 장치는 may_open_dev를 검사하고 FIFO·socket과 함께 실행 요청을 거절하며 이 함수의 로컬 flag에서 O_TRUNC를 지웁니다. 일반 파일의 실행은 noexec 정책을 검사합니다. 이어 MAY_OPEN|acc_mode로 inode_permission을 확인합니다. append-only inode의 쓰기는 O_APPEND가 필요하고 O_TRUNC는 거절합니다. O_NOATIME은 소유자 또는 적절한 capability 조건이 필요합니다.',
 'append-only 일반 파일을 O_WRONLY만으로 열면 -EPERM, O_WRONLY|O_APPEND면 그 조건을 통과하지만 앞선 종류·권한 검사도 별도로 필요합니다. 디렉터리 쓰기는 일반 inode_permission 호출보다 앞에서 거절됩니다. 이것은 경로 탐색 전체가 아니라 이미 얻은 path에 대한 열기 허용 검사입니다.',
 '왜 로컬 flag 변경과 호출자 플래그 변경을 구별하나',
 'flag는 값으로 전달된 int입니다. 이 함수에서 flag &= ~O_TRUNC를 해도 호출자의 원래 변수나 file 객체를 자동으로 바꾸지 않습니다. 이 함수의 뒤 검사에서 사용할 로컬 해석을 조절합니다. 함수 자체가 파일 내용을 truncate하지도 않습니다. 또 may_open의 디렉터리 MAY_EXEC 거절을 모든 경로 탐색의 디렉터리 검색 권한이 금지된다는 의미로 확대하면 안 됩니다. 연산 종류와 호출 경계를 지켜 해석해야 합니다.',
 ('may_open이 O_TRUNC를 지우면 실제 파일 내용도 잘라낸 것인가요?', '아닙니다. 로컬 플래그 해석을 바꾼 것입니다.', '그렇습니다. 비트 하나를 지우면 디스크 파일 길이도 0이 됩니다.', '본문에는 데이터 길이 변경 호출이 없습니다. 정책 검사와 실제 truncate 경로는 구분됩니다.'),
 ('append-only 파일의 쓰기 열기에 O_APPEND가 없으면?', '-EPERM입니다.', '일반 쓰기 권한만 있으면 이 조건도 무조건 통과합니다.', 'IS_APPEND 조건 안에서 쓰기 모드이면서 O_APPEND가 없으면 조기 오류를 반환합니다.')),
('부모 dentry 참조: 읽은 부모가 아직 같은지 확인하기','파일시스템','fs/dcache.c','dget_parent',
 '디렉터리 엔트리의 부모 포인터는 이름 변경이나 이동과 경쟁할 수 있습니다. 포인터를 한 번 읽었다는 것과 현재 부모로서 유효한 참조를 얻었다는 것은 다른 조건입니다.',
 'dget_parent는 먼저 RCU 구간에서 d_seq를 읽고 READ_ONCE로 부모를 얻어 lockref_get_not_zero를 시도합니다. RCU를 나간 뒤 참조를 얻었고 sequence 재검사도 통과하면 부모를 반환합니다. 참조를 얻었으나 sequence가 바뀌었으면 dput합니다. 느린 경로는 RCU 안에서 부모를 읽고 그 부모의 d_lock을 잡아 여전히 같은 부모인지 검사합니다. 다르면 잠금과 RCU를 풀고 반복합니다. 같으면 RCU를 나가고 참조 수가 0이 아님을 확인해 증가시킨 뒤 unlock하고 반환합니다.',
 '처음 읽은 부모 A의 참조를 얻는 동안 부모가 B로 바뀌면 빠른 경로의 sequence 재검사에서 A를 그대로 반환하지 않습니다. A 참조를 내려놓고 느린 경로로 갑니다. 반환된 부모는 참조를 얻은 객체이므로 사용 후 dput할 책임이 있습니다. 함수가 반환된 뒤 부모 관계 자체가 영원히 고정된다는 뜻은 아닙니다.',
 '왜 부모 잠금 뒤에도 다시 비교하나',
 '락을 잡으러 가는 동안 dentry->d_parent가 바뀔 수 있어 현재 잡은 A의 잠금이 지금 부모 B의 상태를 보호한다고 단정할 수 없습니다. 잠금 아래 포인터를 다시 비교하고 다르면 처음부터 다시 잡습니다. RCU는 읽는 중 객체 수명, lockref는 반환할 참조, sequence는 낙관적 조회의 변경 감지라는 서로 다른 역할을 맡습니다. 입력 dentry 자체의 유효성은 호출자가 보장해야 합니다.',
 ('빠른 경로에서 부모 참조는 얻었지만 sequence가 바뀌었으면?', '그 참조를 dput하고 다른 경로로 다시 확인합니다.', '참조가 있으므로 반드시 현재 부모라고 반환합니다.', '객체의 생존과 부모 관계의 동일성은 다릅니다. 실제 조건을 두 단계로 검사합니다.'),
 ('느린 경로에서 부모를 읽은 후 d_lock을 잡으면 재비교는 불필요한가요?', '아닙니다. 잠금 획득 전 부모가 바뀔 수 있습니다.', '그렇습니다. 읽었던 주소의 잠금은 항상 현재 부모 잠금입니다.', 'ret != dentry->d_parent이면 unlock·RCU 해제 후 repeat합니다.')),
('Writeback 대기: 완료 관찰·신호·다시 시작되는 쓰기','메모리','mm/page-writeback.c','folio_wait_writeback',
 '캐시의 내용을 저장장치에 쓰는 동안 같은 내용을 바꿔도 되는지는 사용 경로와 장치 계약에 달려 있습니다. 진행 중 writeback이 끝나기를 기다리는 동작을 새 쓰기를 시작하거나 영구 저장 성공을 검증하는 동작과 구분해야 합니다.',
 'folio_wait_writeback은 PG_writeback 상태를 반복 검사하고 켜져 있으면 trace 후 folio_wait_bit로 기다립니다. killable 변형은 대기 helper가 신호로 중단되면 -EINTR, 쓰기 상태가 없으면 0입니다. folio_wait_stable은 mapping_stable_writes 조건이 참일 때만 일반 writeback 대기를 호출합니다. 이 함수들은 잠들 수 있는 프로세스 문맥에서 스핀 잠금을 보유하지 않고, 호출자가 folio 참조를 보유한 상태로 사용해야 한다는 원문 계약이 있습니다.',
 '처음부터 writeback 표시가 없으면 일반 대기는 루프를 실행하지 않고 끝납니다. 대기에서 깨어나도 while로 상태를 다시 검사합니다. folio를 잠그지 않았다면 현재 쓰기가 끝난 뒤 새 writeback이 시작될 수 있으므로 반환을 이후 모든 쓰기 활동이 없다는 영구 보장으로 읽으면 안 됩니다.',
 '왜 이 반환이 fsync 성공과 같지 않나',
 '여기서 기다리는 것은 특정 folio의 writeback 상태입니다. 파일 전체의 모든 dirty 데이터, 메타데이터, 저장장치 캐시 flush, 오류 수집까지 처리하는 fsync 전체 구현이 아닙니다. killable 함수의 0도 이 대기가 신호 오류 없이 끝났다는 결과이며 저장장치 오류가 전혀 없다는 보장은 별도 경로에서 확인해야 합니다. 안정적 내용이 필요한 mapping인지 확인하는 stable wrapper도 모든 folio에 무조건 대기를 거는 함수가 아닙니다.',
 ('killable 대기의 0이면 파일 전체 fsync 성공을 뜻하나요?', '아닙니다. 해당 writeback 대기와 파일 전체 영속성은 범위가 다릅니다.', '그렇습니다. 0이면 모든 디스크 데이터가 영구 저장됐습니다.', '본문은 상태 bit 대기이며 파일 전체 flush 및 오류 집계 호출이 없습니다.'),
 ('folio_wait_stable은 모든 mapping에서 무조건 기다리나요?', '아닙니다. mapping_stable_writes가 참인 경우에만 호출합니다.', '그렇습니다. stable이라는 이름이면 항상 강제 대기입니다.', 'wrapper의 if 조건이 대기 필요성을 결정합니다. 실제 writeback 진행 여부는 내부 대기 루프가 추가로 확인합니다.')),
]

def register(topic,q,detail):
    for title,area,path,symbol,why,principle,use,dt,body,qa,qb in ROWS:
        topic(title,area,path,symbol,why,principle,use,
              '권한 검사와 실제 파일 변경, 포인터 생존과 관계 안정성, writeback 대기와 영속성 확인을 구별해 읽으세요.',
              q(title+' · '+qa[0],*qa[1:]),q(title+' · '+qb[0],*qb[1:]),
              details=[detail(dt,body),detail('검토 범위','Linux v6.12의 명시한 함수와 연결 helper의 계약을 읽었습니다. 실제 rename 경쟁·writeback·장치 오류를 실행 검증한 결과는 아닙니다.')])
