"""Address-space initialization, users and object lifetime teardown."""
ROWS = [
('mm 초기화: 실패한 단계 앞에서 확보한 자원만 되돌리기','mm_init',
 '주소 공간 객체에는 매핑 검색 트리, 여러 잠금, 참조 수, CPU 상태, 통계와 페이지 디렉터리가 함께 있습니다. 구조체 메모리를 얻었다고 바로 사용할 수 없고, 초기화 중간에 실패하면 이미 성공한 자원만 역순으로 정리해야 합니다.',
 'mm_init은 Maple Tree와 외부 mmap_lock 연결,mm_users=1,mm_count=1,seqcount와 목록·잠금·통계를 초기화합니다. AIO·memcg owner·uprobes 등은 설정별 helper로 준비합니다. exe_file은 RCU_INIT_POINTER로 NULL입니다. current->mm이 있으면 허용된 flags를 계승하고 없으면 기본 dump filter와 def_flags0을 씁니다.',
 '실제 자원 확보는 PGD→아키텍처 문맥→CID→CPU별 RSS 계수 순서입니다. RSS 계수 초기화가 실패하면 CID,문맥,PGD,mm 객체를 역순 해제합니다. CID 단계가 실패하면 아직 성공하지 않은 CID를 파괴하는 줄은 건너뛰고 문맥부터 정리합니다. 각 goto label은 성공한 단계의 경계를 나타냅니다.',
 '왜 user namespace 참조를 마지막에 얻나',
 '실패 가능한 네 단계를 모두 지난 뒤 get_user_ns로 namespace 참조를 얻고 lru_gen_init_mm 후 반환합니다. 앞 실패 경로에는 아직 그 참조가 없으므로 put_user_ns도 없습니다. mm_alloc은 allocate_mm 실패면 NULL,성공하면 구조를0으로 지운 뒤 current와 current_user_ns로 mm_init을 호출합니다. dup_mm의 memcpy 경로와 달리 새 mm_alloc은 초기 바탕을0으로 만듭니다. map_count·locked_vm·pinned_vm 및 PGD 바이트 통계를 초기화하고 THP 설정에 따른 pmd_huge_pte도 정리한다는 점에서 단순 refcount 초기화보다 넓은 작업입니다.',
 ('RSS 계수 초기화 실패 시 정리 순서는?','CID→문맥→PGD→mm 객체입니다.','mm 객체부터 해제한 뒤 그 안의 포인터를 읽습니다.','fail_pcpu에서 아래 label로 순차 진행하며 이전에 성공한 자원을 역순으로 되돌립니다.'),
 ('초기 PGD 할당 실패에서도 namespace 참조를 반환하나요?','아닙니다. 그 참조는 아직 얻기 전입니다.','그렇습니다. 인자로 받으면 이미 새 참조를 소유합니다.','인자로 전달받은 포인터와 get_user_ns로 새로 획득한 참조를 구분해야 합니다.')),
('mmput과 mmput_async: 마지막 주소 공간 사용자만 정리 시작','mmput',
 '같은 주소 공간을 여러 스레드가 공유하면 한 스레드가 사용을 마쳤다고 매핑을 모두 없앨 수 없습니다. 참조 감소가 마지막인 호출만 정리를 해야 하며, 정리가 잠들 수 있는지에 따라 직접 실행과 작업 큐 실행을 구분합니다.',
 'mmput은 might_sleep 후 mm_users를 atomic_dec_and_test로 줄여0이 된 호출만 __mmput합니다. __mmput은 사용자가 남았으면 VM_BUG_ON입니다. uprobes,AIO,KSM,khugepaged를 정리하고 exit_mmap,huge zero folio,실행 파일 참조 순으로 정리합니다. mmlist에 연결돼 있으면 전역 잠금 아래 제거하고 binfmt 모듈 참조와 LRU 상태를 내린 뒤 mmdrop합니다.',
 'mm_users가2이면 첫 mmput은1로 줄이고 매핑 정리를 하지 않습니다. 두 번째가0을 만들어 정리를 시작합니다. CONFIG_MMU의 mmput_async도 카운터 감소는 호출 문맥에서 즉시 수행하지만 마지막일 때만 async_put_work를 초기화해 schedule_work합니다. worker는 container_of로 mm을 찾아 __mmput합니다. 함수 반환이 실제 매핑 정리 완료라는 뜻은 아닙니다.',
 '정리 순서가 의존성을 표현하는 곳',
 'khugepaged_exit는 exit_mmap보다 먼저 실행해야 한다는 주석이 있습니다. __mmput은 무조건 구조체부터 free하는 함수가 아니라 주소 공간을 사용하는 여러 하위 계층을 먼저 정리합니다. mmput_async는 헤더에서 원자 문맥 호출도 허용하는 별도 계약으로 설명되며,같은 참조를 동기·비동기 함수 양쪽으로 두 번 반환해서는 안 됩니다. mmget으로 유지한 mm도 개별 매핑의 변경까지 금지하지는 않습니다.',
 ('mm_users2에서 한 번 mmput하면 exit_mmap을 실행하나요?','아닙니다. 아직 사용자가1 남습니다.','그렇습니다. mmput은 항상 매핑을 지웁니다.','atomic_dec_and_test가0이 됐는지를 판정해 마지막 사용자만 정리 경로에 들어갑니다.'),
 ('마지막 mmput_async 반환 시 정리 완료가 보장되나요?','아닙니다. worker 실행을 예약합니다.','그렇습니다. async라는 이름만 다르고 항상 직접 완료합니다.','카운터 감소와 __mmput 실행의 문맥이 나뉘며 완료 대기를 하는 코드는 없습니다.')),
('mm_count의 마지막 참조: 매핑 수명과 구조체 수명 분리','__mmdrop',
 '사용자 매핑이 사라진 뒤에도 커널이 mm_struct 자체를 참조할 수 있습니다. 따라서 주소 공간 사용자의 수와 객체 자체의 수명을 같은 숫자 하나로 처리하면 너무 일찍 구조체를 해제하거나 매핑을 불필요하게 유지할 수 있습니다.',
 'mmget/mmput은 mm_users를,mmgrab/mmdrop은 mm_count를 다룹니다. mmdrop은 mm_count 감소가0일 때 __mmdrop합니다. __mmdrop은 init_mm 해제를 BUG_ON으로 막고 current->mm 여부를 경고합니다. lazy TLB 사용을 정리한 뒤 active_mm 경고를 확인하고 PGD,아키텍처 문맥,MMU notifier 상태를 정리합니다. 이어 check_mm,namespace 참조,PASID,CID,RSS 계수를 정리하고 free_mm합니다.',
 '초기 users1,count1에서 별도 mmgrab을 하면 count2입니다. 마지막 mmput은 users를0으로 만들어 매핑을 정리하고 mmdrop으로 count를1로 낮춥니다. 구조체는 아직 남습니다. 마지막 별도 보유자가 mmdrop해야 count0이 되어 객체를 해제합니다. mmgrab만 유지했다고 사용자 매핑도 남았다고 가정하면 안 됩니다.',
 'lazy TLB와 비동기 마지막 해제',
 'cleanup_lazy_tlbs는 MMU_LAZY_TLB_SHOOTDOWN이 없으면 참조 기반 사용 종료를 전제로 돌아옵니다. 설정이 있으면 mm_cpumask의 CPU들에 동기 호출해 해당 active_mm을 쓰는 커널 태스크를 init_mm으로 전환합니다. 디버그 설정은 전체 CPU 확인도 수행합니다. fork.c의 mmdrop_async는 마지막 mm_count 감소 때 worker에서 __mmdrop하도록 예약하는 별도 helper입니다. 이것은 마지막 mm_users 감소를 처리하는 mmput_async와 출발 카운터부터 다릅니다. mmdrop의 원자 감소는 membarrier에서 요구하는 전체 메모리 barrier와도 연결되므로 단순 비원자 --로 바꿀 수 없습니다.',
 ('mmgrab 참조가 남으면 사용자 매핑도 반드시 살아 있나요?','아닙니다. 객체 자체의 수명과 매핑 수명은 다릅니다.','그렇습니다. mm_count는 항상 mm_users와 같습니다.','mm_users0에서 매핑을 없앤 뒤에도 별도 mm_count 참조로 구조체가 남을 수 있습니다.'),
 ('mmdrop_async와 mmput_async가 줄이는 카운터는 같나요?','아닙니다. 각각 mm_count와 mm_users입니다.','그렇습니다. 둘 다 같은 카운터를 두 번 줄입니다.','작업 큐 사용이라는 공통점보다 어떤 소유권을 반환하는지를 먼저 구별해야 합니다.')),
]

def register(topic,q,detail):
    for title,symbol,why,principle,use,dt,body,qa,qb in ROWS:
        topic(title,'메모리','kernel/fork.c',symbol,why,principle,use,
              '획득한 자원 목록과 두 참조 수를 따로 적고 성공·실패·마지막 반환을 추적하세요.',
              q(title+' · '+qa[0],*qa[1:]),q(title+' · '+qb[0],*qb[1:]),
              details=[detail(dt,body),detail('처음 읽는 용어','PGD는 페이지 테이블의 최상위 디렉터리이고 RSS는 현재 물리 메모리에 상주하는 페이지 사용량을 나타내는 통계입니다. mm_users는 주소 공간 사용자 참조,mm_count는 mm 객체 자체의 참조를 추적합니다. 참조 획득은 모든 데이터가 불변이라는 뜻이 아닙니다. 작업 큐는 정리를 나중 worker 문맥에서 실행하도록 예약하는 장치입니다.'),detail('검토 범위','Linux v6.12 fork.c의 mm 초기화·참조 정리·lazy TLB 정리와 sched/mm.h의 참조 helper를 대조했습니다. fork.c 전체 검토 완료나 실제 CPU 전환·메모리 고갈 시험을 뜻하지 않습니다.')])
