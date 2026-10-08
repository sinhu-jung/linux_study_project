"""Block flush sequencing, ownership, batching and allocation."""
ROWS = [('블록 쓰기 정책: PREFLUSH와 FUA가 필요한 시점은 다르다',
  '저장장치',
  'block/blk-flush.c',
  'blk_insert_flush',
  '휘발성 쓰기 캐시가 있는 장치는 데이터가 아직 비휘발성 매체에 도달하기 전에 쓰기 완료를 보고할 수 있습니다. 이전 쓰기까지 먼저 안전하게 만들 것인지, 이번 쓰기가 완료될 때 안전해야 하는지를 '
  '별도로 표현해야 합니다.',
  'blk_insert_flush는 데이터 sector가 있으면 DATA를 policy에 넣습니다. write cache가 있을 때 PREFLUSH 요청은 사전 flush를, FUA 요청인데 장치가 '
  'FUA를 지원하지 않으면 사후 flush를 추가합니다. driver에 보낼 flags에서 PREFLUSH는 지우고 FUA는 지원하지 않을 때 지웁니다. 회계 의미를 유지하기 위해 REQ_SYNC를 '
  '세웁니다. PREFLUSH는 이번 데이터 전에 이전 완료 쓰기를 밀어내는 의미, FUA는 이번 데이터 완료 시 비휘발성을 요구하는 의미입니다.',
  '데이터+PREFLUSH+FUA, write cache 있음, FUA 미지원이면 PRE→DATA→POST입니다. 같은 요청에서 FUA 지원이면 PRE→DATA이며 DATA에 FUA가 남습니다. '
  'write cache가 없으면 별도 PRE/POST 없이 DATA 정책이 됩니다. 이 본문의 FUA 비트 제거 조건은 supports_fua 자체이므로 정상 장치 기능 설정과 함께 읽어야 합니다.',
  '왜 반환 true를 디스크 저장 성공으로 해석하면 안 되나',
  'policy=0은 request를 성공 완료하고 true, DATA만 있으면 일반 처리를 계속하도록 false입니다. DATA|POST는 flush 상태·완료 callback을 초기화하고 PRE를 '
  '완료 표시한 뒤 data_in_flight를 올리고 false입니다. 나머지는 필요 없는 단계들을 완료 처리해 상태 머신에 넘기고 true입니다. 따라서 true/false는 요청을 이 함수가 '
  '인수했는지의 제어 흐름입니다. 한 bio만 연결돼야 한다는 WARN_ON도 이 특수 완료 절차의 전제입니다.',
  ('캐시 있음,FUA 미지원,데이터와 두 플래그 모두 있으면 순서는?',
   'PREFLUSH→DATA→POSTFLUSH입니다.',
   'PREFLUSH만 하면 이번 데이터도 자동 영속화됩니다.',
   '이전 쓰기와 이번 쓰기의 완료 시점을 따로 보장하려고 데이터 뒤 flush도 필요합니다.'),
  ('반환 false는 저장장치 오류라는 뜻인가요?',
   '아닙니다. 호출자가 request 처리를 계속해야 한다는 뜻입니다.',
   '그렇습니다. false는 항상 I/O 실패입니다.',
   '함수 주석은 consumed 여부를 반환한다고 설명합니다. DATA와 DATA|POST도 false 경로입니다.')),
 ('Flush 상태 머신: 완료 비트의 첫 0이 다음 단계다',
  '저장장치',
  'block/blk-flush.c',
  'blk_flush_complete_seq',
  '필요 없는 단계는 건너뛰고 필요한 단계만 순서대로 실행하려면 진행 상태를 간단히 표현할 수 있어야 합니다. 각 단계를 완료 비트로 표시하면 첫 미완료 비트를 찾아 다음 작업을 정할 수 있습니다.',
  'PRE=1,DATA=2,POST=4,DONE=8이며 ACTIONS=7입니다. blk_rq_init_flush는 seq=0, RQF_FLUSH_SEQ 설정, 원래 end_io 저장, DATA용 '
  'callback 설치를 합니다. complete_seq는 이미 완료된 seq를 다시 완료시키려 하면 BUG_ON이고 새 비트를 OR합니다. 오류가 없으면 blk_flush_cur_seq의 '
  '1<<ffz로 첫0을 찾고, 오류면 DONE으로 갑니다. PRE/POST는 pending 목록에, DATA는 진행 수를 올린 뒤 requeue 목록에, DONE은 복원 후 end_request로 '
  '연결됩니다.',
  'PRE와 DATA만 필요하면 초기에는 ACTIONS & ~policy=4로 POST를 완료 취급합니다. seq=100에서 첫0은 PRE, 완료 후101의 첫0은 DATA, 완료 후111의 첫0은 '
  'DONE입니다. 낮은 세 비트가 모두 1이면 1<<3=8입니다. 숫자 4가 현재 POST 실행 중이라는 뜻이 아니라 이미 건너뛴 단계일 수도 있습니다.',
  '목록·잠금·복원이 필요한 이유',
  '이 함수는 mq_flush_lock을 IRQ를 막고 보유하는 문맥을 요구합니다. 빈 pending에 첫 요청을 넣을 때만 pending_since를 기록합니다. DATA 이동은 별도 '
  'requeue_lock 아래 수행한 뒤 실행을 깨웁니다. DONE은 목록에서 제거하고 bio를 biotail로 되돌리며 있으면 sector도 복원하고 RQF_FLUSH_SEQ를 지운 뒤 원래 '
  'callback을 되돌립니다. 마지막에는 매번 blk_kick_flush로 다음 flush 발행 가능성을 검사합니다.',
  ('seq=0b101에서 다음 단계는?', 'DATA입니다.', 'POST입니다.', '최하위에서 첫0은 bit1이므로 1<<1=2입니다.'),
  ('처리 중 오류가 오면 남은 DATA나 POST도 계속 실행하나요?',
   '이 상태 함수는 DONE으로 이동합니다.',
   '그렇습니다. 오류와 관계없이 모든 단계를 실행합니다.',
   'error가 있으면 seq=REQ_FSEQ_DONE으로 설정합니다.')),
 ('Flush 묶음 발행: 두 목록과 5초 기아 방지 조건',
  '저장장치',
  'block/blk-flush.c',
  'blk_kick_flush',
  '각 요청마다 따로 캐시 flush를 하면 비싼 장치 동작을 반복합니다. 여러 요청을 한 번의 flush로 묶되 새로운 요청이 끝없이 와서 기다리는 요청이 영원히 밀리지 않게 해야 합니다.',
  'blk_kick_flush는 pending_idx와 running_idx가 다르면 이미 flush 진행 중이므로 반환하고 pending이 비어도 반환합니다. DATA가 진행 중이고 '
  'pending_since+5*HZ보다 현재 jiffies가 앞서면 기다립니다. 그 외에는 pending_idx를 XOR1로 바꿔 현재 목록을 실행 묶음으로 분리합니다. 재사용 flush '
  'request를 초기화하고 첫 요청의 ctx/hctx와 scheduler 유무에 맞는 tag를 빌립니다.',
  '처음 두 index가 0이면 목록0에 모입니다. 발행 때 pending=1,running=0이 되어 새 요청은 목록1에 모이고 기존 목록0은 실행 중입니다. DATA가 계속 있어도 5*HZ에 '
  '도달하면 시간 조건은 기다림을 강제하지 않습니다. 다만 이 함수는 timer를 설치하지 않으므로 정확히 5초 순간에 자동 호출된다는 보장은 아닙니다.',
  '발행 준비의 순서와 공유 태그',
  'flush_rq의 op는 FLUSH|PREFLUSH이고 원 요청의 driver·failfast 비트만 추가 전달합니다. RQF_FLUSH_SEQ와 flush_end_io를 설정한 뒤 smp_wmb, '
  'ref=1 순서로 공개합니다. 주석은 다른 경로의 nonzero 참조 증가와 end_io 읽기 순서를 설명합니다. requeue_lock 아래 flush_list에 넣고 실행을 깨웁니다. 스케줄러가 '
  '없으면 tag, 있으면 internal_tag를 빌리는 분기가 다르며 첫 요청과 동시에 같은 태그로 실행하지 않는 계약에 기대고 있습니다.',
  ('DATA가 있으면 pending flush는 언제까지나 기다리나요?',
   '아닙니다. 5*HZ 대기 기준을 넘기면 그 억제 조건을 무시합니다.',
   '그렇습니다. DATA가 완전히 사라져야만 합니다.',
   'DATA 조건과 time_before 조건이 AND여서 둘 다 참일 때만 반환합니다.'),
  ('두 index가 다르면 무엇을 나타내나요?',
   '한 flush 묶음이 이미 진행 중입니다.',
   '목록이 둘 다 반드시 비었습니다.',
   '발행 시 pending index만 토글하고 완료 시 running index를 토글합니다.')),
 ('Flush 완료: 마지막 참조와 묶음 요청의 다음 단계',
  '저장장치',
  'block/blk-flush.c',
  'flush_end_io',
  'flush request는 여러 원 요청을 대신하며 timeout 경로도 완료 callback에 접근할 수 있습니다. callback이 불렸다는 사실만으로 공유된 request의 최종 정리를 '
  '수행하면 수명 경쟁이 생길 수 있습니다.',
  'flush_end_io는 mq_flush_lock 아래 req_ref_put_and_test를 합니다. 마지막 참조가 아니면 rq_status에 error를 보관하고 잠금을 풀어 반환합니다. '
  '마지막이면 flush 통계의 횟수와 경과 ns를 part0에 기록하고 state를 IDLE로 씁니다. 보관 상태가 OK가 아니면 그 오류를 이번 error로 사용하고 저장 상태를 OK로 돌립니다. '
  '스케줄러 유무에 따라 빌린 tag 표시 또는 driver tag/internal_tag를 정리합니다.',
  'running 목록을 선택한 뒤 pending과 running이 같으면 BUG_ON입니다. running_idx를 XOR1로 바꾸고 목록의 각 요청을 안전한 순회로 제거하며 현재 단계가 PRE 또는 '
  'POST인지 확인합니다. 그 단계를 complete_seq에 error와 함께 넘겨 다음 DATA나 DONE으로 진행합니다. 하나의 실제 flush 완료가 여러 원 요청의 진행을 해제할 수 '
  '있습니다.',
  '왜 callback 식별과 통계를 분리해 읽나',
  'is_flush_rq는 end_io가 flush_end_io와 같은지 비교합니다. 단순히 op가 WRITE인지 FLUSH인지 검사하는 함수가 아닙니다. blk_account_io_flush는 '
  'part_stat 잠금 아래 flush 개수와 현재 시각-start_time의 경과를 더합니다. 비마지막 callback은 이 통계와 상태·태그·목록 최종 정리를 건너뜁니다. 이 수업은 원문 참조 '
  '수 프로토콜을 설명하며 임의로 callback을 두 번 불러도 된다는 뜻은 아닙니다.',
  ('마지막 참조가 아니면 통계와 목록 진행까지 하나요?',
   '아닙니다. 상태를 보관하고 조기 반환합니다.',
   '그렇습니다. callback마다 모든 원 요청을 완료합니다.',
   '참조 검사 실패 분기의 return이 최종 정리 앞에 있습니다.'),
  ('is_flush_rq가 검사하는 것은?',
   'end_io callback 주소입니다.',
   '항상 request의 데이터 길이 0 여부입니다.',
   '본문은 rq->end_io == flush_end_io 비교입니다.')),
 ('Flush DATA 완료: 원 bio를 최종 완료까지 보류하기',
  '저장장치',
  'block/blk-flush.c',
  'mq_flush_data_end_io',
  '데이터 쓰기 명령이 끝났어도 FUA를 대신하는 사후 flush가 남았다면 사용자에게 전체 완료를 알려서는 안 됩니다. DATA 단계와 전체 순서 완료를 구별해 원 bio를 마지막까지 이어 갑니다.',
  'mq_flush_data_end_io는 elevator가 있으면 tag가 음수인지 경고하고 driver tag를 반환합니다. mq_flush_lock을 IRQ 상태 저장과 함께 잡고 '
  'data_in_flight를 감소시킵니다. rq_next 재사용이 목록 필드를 손상시켰을 수 있어 queuelist를 다시 초기화합니다. DATA 완료를 complete_seq에 넘긴 뒤 잠금을 '
  '풀고 hctx scheduler를 재시작하며 RQ_END_IO_NONE을 반환합니다.',
  'DATA|POST 요청의 DATA 완료는 진행 수를 1 줄이고 POST pending으로 넘어갈 수 있습니다. POST가 끝나 DONE이 될 때 저장했던 end_io와 bio를 복원해 정상 최종 '
  '완료합니다. 파일의 상단 주석은 RQF_FLUSH_SEQ가 설정된 DATA 완료에서 bio 내용을 갱신하되 제출자 알림을 전체 완료까지 보류하는 계약과 한 bio만 붙는 전제를 설명합니다.',
  '왜 목록을 다시 초기화하나',
  'request의 필드 일부는 처리 단계에 따라 다른 목적으로 재사용됩니다. 이전 queuelist가 아직 정상 연결 상태일 것이라 가정하고 다음 목록에 넣으면 목록 구조를 깨뜨릴 수 있습니다. '
  '원문이 INIT_LIST_HEAD를 호출하는 이유를 단순 장식으로 넘기면 안 됩니다. end_io 반환 RQ_END_IO_NONE은 이 callback 프로토콜의 값이며 사용자 syscall의 성공 '
  '코드와 같은 채널이 아닙니다.',
  ('DATA 완료 후 POST가 남으면 곧바로 제출자에게 전체 완료인가요?',
   '아닙니다. 사후 flush까지 진행해야 합니다.',
   '그렇습니다. 데이터 명령 종료가 전체 영속성 보장입니다.',
   '특수 sequence 완료는 마지막 단계에서 원 bio와 callback을 복원합니다.'),
  ('DATA callback에서 queuelist를 다시 초기화하는 이유는?',
   'rq_next 재사용으로 목록 필드가 변했을 수 있기 때문입니다.',
   '매번 목록의 데이터 내용을 모두 삭제하려고 합니다.',
   '공유 저장 공간의 단계별 용도가 달라 목록 연결 전 구조를 초기화합니다.')),
 ('순수 flush 요청: 빈 bio를 제출하고 완료를 기다리기',
  '저장장치',
  'block/blk-flush.c',
  'blkdev_issue_flush',
  '데이터를 새로 쓰지 않고 이미 장치 캐시에 들어간 쓰기를 비휘발성 저장소로 밀어내고 싶을 수 있습니다. 이 경우 데이터 페이지를 억지로 붙이지 않고 빈 bio에 PREFLUSH 의미를 담습니다.',
  'blkdev_issue_flush는 스택의 bio를 bdev, vector NULL, 개수0, WRITE|PREFLUSH로 초기화하고 submit_bio_wait 결과를 반환합니다. 연결 '
  'helper는 스택 completion을 bi_private에 넣고 완료 callback을 설치하며 REQ_SYNC를 더해 제출한 뒤 blk_wait_io로 기다립니다. 마지막 '
  'bio->bi_status를 errno로 변환해 반환합니다.',
  'write cache가 없는 장치의 빈 flush는 블록 계층에서 실질적 장치 I/O 없이 성공 완료될 수 있습니다. 따라서 성공했다고 항상 물리적인 FLUSH 명령이 발행됐다고 단정하지 않습니다. '
  '반대로 장치 오류가 전달되면 호출자는 반환된 errno를 처리해야 합니다.',
  '왜 파일 전체 fsync를 대신하지 않나',
  '이 helper는 블록 장치에 이미 전달된 쓰기의 캐시 제어 요청입니다. 파일 페이지 캐시의 dirty 데이터를 전부 찾아 쓰거나 파일시스템 메타데이터를 모두 준비하는 단계가 본문에 없습니다. 아직 '
  '장치로 제출하지 않은 dirty 페이지까지 이 호출 하나로 저장됐다고 생각하면 안 됩니다. 동기 대기가 있으므로 잠들 수 있는 적절한 호출 문맥에서 사용해야 합니다.',
  ('bio vector 개수0이면 이 요청은 항상 무의미한가요?',
   '아닙니다. PREFLUSH 자체의 캐시 제어 의미가 있습니다.',
   '그렇습니다. 데이터가 없으면 요청할 동작도 없습니다.',
   '문서는 빈 bio의 PREFLUSH를 순수 flush로 정의합니다.'),
  ('이 함수가 파일의 모든 dirty 페이지를 먼저 찾아 쓰나요?',
   '아닙니다. 본문에는 그런 파일 캐시 순회가 없습니다.',
   '그렇습니다. flush라는 이름이면 fsync 전체입니다.',
   '블록 장치 캐시 제어와 파일시스템 writeback 준비의 범위를 구분합니다.')),
 ('Flush 큐의 수명: 두 번 할당의 실패 정리와 lockdep 분류',
  '저장장치',
  'block/blk-flush.c',
  'blk_alloc_flush_queue',
  'flush 상태 목록과 재사용 request는 별도 메모리입니다. 두 번째 할당이 실패했을 때 첫 번째를 남겨 두면 누수가 생기므로 부분 초기화의 정리 경로가 필요합니다.',
  'blk_alloc_flush_queue는 지정 NUMA node에서 큐를 0으로 할당하고 실패하면 NULL입니다. 잠금을 초기화한 뒤 request 크기+cmd_size를 '
  'cache_line_size 배수로 올려 두 번째 메모리를 할당합니다. 실패하면 큐를 kfree하고 NULL입니다. 성공하면 두 flush 목록을 초기화해 반환합니다. '
  'blk_free_flush_queue는 NULL이면 아무것도 하지 않고 아니면 request와 큐를 차례로 해제합니다.',
  '예시로 request 기본 크기160, cmd_size24, cache line64라면 합184를192로 올립니다. 이는 설명용 숫자이며 실제 struct request 크기는 빌드에 따라 '
  '다릅니다. free 함수는 진행 중 I/O를 기다리거나 목록을 비우지 않으므로 사용이 끝난 수명 계약을 호출자가 보장해야 합니다. cmd_size와 node 및 flags도 유효한 호출 인자를 요구하며 임의의 사용자 입력 크기를 검증하는 파서는 아닙니다.',
  'lockdep 분류 변경이 실제 잠금을 없애는 것은 아니다',
  'blk_mq_hctx_set_fq_lock_class는 해당 flush 잠금에 전달된 lock class key를 지정합니다. 주석은 nvme-loop 같은 중첩 완료 경로에서 서로 다른 인스턴스를 '
  '같은 잠금 종류로 판단하는 문제를 설명합니다. 인스턴스마다 동적 key를 만들고 해제할 때 RCU 동기화가 반복되면 탐색 비용이 커질 수 있어 driver가 분류를 지정할 수 있게 합니다. 이 '
  '호출은 잠금을 획득하거나 실제 재귀 잠금을 안전하게 바꿔 주는 함수가 아닙니다.',
  ('request 할당이 실패하면 먼저 만든 큐는?',
   '해제한 뒤 NULL을 반환합니다.',
   '다음 요청을 위해 누수 상태로 남깁니다.',
   'fail_rq label에서 kfree(fq) 후 fail의 NULL로 진행합니다.'),
  ('lockdep class를 바꾸면 진행 중 I/O 대기나 잠금 획득도 하나요?',
   '아닙니다. 잠금 진단용 분류를 지정합니다.',
   '그렇습니다. class 지정이 spin_lock과 같습니다.',
   '본문은 lockdep_set_class 호출이며 실제 잠금 동작과 다릅니다.'))]

def register(topic,q,detail):
    for title,area,path,symbol,why,principle,use,dt,body,qa,qb in ROWS:
        topic(title,area,path,symbol,why,principle,use,"장치 기능·단계 비트·목록·참조 수와 최종 완료 시점을 함께 추적하세요.",q(title+" · "+qa[0],*qa[1:]),q(title+" · "+qb[0],*qb[1:]),details=[detail(dt,body),detail("큐 선택과 파일 구성","blk_get_flush_queue는 현재 ctx를 REQ_OP_FLUSH 기준으로 blk_mq_map_queue에 매핑한 하드웨어 큐의 fq를 반환합니다. 데이터 명령의 임의 전역 목록 하나를 쓰는 구조가 아닙니다. 파일의 enum은 세 단계 비트와 DONE 및 timeout을 정의하고, 앞쪽 blk_kick_flush 선언은 뒤 정의를 호출하기 위한 선언입니다. SPDX는 GPL-2.0이며 include들은 bio·request·메모리·통계·blk-mq·scheduler API를 연결합니다. 내보내기 매크로는 외부 모듈에서 helper를 연결하도록 하는 선언입니다."),detail("검토 범위","v6.12 block/blk-flush.c와 writeback_cache_control 문서, submit_bio_wait helper를 대조했습니다. 실제 장치 전원 차단이나 영속성 실험을 수행한 결과는 아닙니다.")])
