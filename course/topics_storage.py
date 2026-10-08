"""Device command lifetimes and parity calculations."""
def register(topic,q,detail):
    topic('NVMe·제출과 완료 큐','저장장치','drivers/nvme/host/pci.c','nvme_submit_cmds',
      '저장장치가 여러 요청을 병렬 처리하려면 CPU의 명령 제출과 장치의 완료 통지를 분리해야 합니다.',
      'NVMe는 submission queue에 명령을 넣고 doorbell로 새 tail을 알립니다. 장치는 처리 결과를 completion queue에 기록하며 command ID로 요청을 찾습니다. 큐 순환과 phase tag로 새 완료를 구분하고 PRP·SGL 등으로 DMA 데이터 위치를 표현합니다.',
      'blk-mq 요청→NVMe 명령 준비→DMA mapping→SQ 복사→doorbell→CQ 처리→unmap·완료를 연결합니다. 요청 timeout·장치 reset 시에도 장치 접근과 객체 수명이 끝났는지 확인합니다.',
      'nvme_submit_cmds의 sq_lock·nvme_sq_copy_cmd·nvme_write_sq_db와 nvme_handle_cqe를 읽으세요.',
      q('SQ에 명령을 복사한 직후 데이터 버퍼를 무조건 해제해도 되는가?','장치 완료·취소 보장 뒤 수명 정리가 필요하다','큐 복사 직후 DMA 데이터는 항상 불필요하다','SQ에는 명령과 데이터 위치가 들어가므로 장치가 나중에 버퍼에 접근합니다. 완료 전에 해제하면 수명 오류가 됩니다.'),
      q('CQ의 command ID가 필요한 이유는?','완료 결과를 해당 요청과 연결한다','모든 요청을 같은 파일로 변환한다','여러 명령이 진행 중이므로 완료 항목에서 어떤 요청을 끝낼지 식별해야 합니다. 완료 순서가 제출 순서와 항상 같은 것은 아닙니다.'),
      details=[detail('Doorbell과 순서','명령 내용을 장치가 볼 수 있게 기록한 뒤 tail 갱신을 알려야 합니다. 장치 접근 가능한 큐 메모리와 MMIO doorbell의 순서 규약을 지킵니다. 큐 인덱스 저장만으로 실제 장치 통지가 되지는 않습니다.'),detail('Phase와 순환','CQ 슬롯을 재사용할 때 phase 값으로 이전 순환의 오래된 항목과 새 완료를 구분합니다. Head의 wrap과 phase 변경을 함께 읽으세요. 단순히 슬롯이 0이 아닌지를 보면 잘못된 완료를 처리할 수 있습니다.')])

    topic('SCSI·명령과 상태','저장장치','drivers/scsi/scsi_lib.c','scsi_queue_rq',
      '블록 요청을 여러 종류의 저장장치에 보내려면 명령 표현·상태·재시도 경계를 공통화해야 합니다.',
      'SCSI 중간 계층은 request를 scsi_cmnd와 CDB로 표현해 host driver의 queuecommand에 전달합니다. 장치 상태·예산·queue 제한을 검사하고 완료의 host·device 상태와 sense 데이터를 해석합니다. Busy로 제출하지 못한 상태와 장치에서 실행 후 오류가 난 상태는 다릅니다.',
      'blk-mq→scsi_queue_rq→queuecommand→완료→sense·재시도 경로를 읽습니다. 재시도 가능 여부와 횟수·timeout을 확인하며 명령 완료의 status를 무조건 성공으로 바꾸지 않습니다.',
      'scsi_queue_rq의 sdev 상태·budget·scsi_cmnd 준비와 host queuecommand 호출을 연결하세요.',
      q('SCSI sense 정보의 역할은?','장치 명령 실패의 원인과 상태를 설명한다','언제나 사용자 파일 내용 자체다','Sense는 오류의 종류와 추가 정보를 전달합니다. 장치 상태와 transport·host 오류를 구분해 처리 정책을 선택합니다.'),
      q('제출 단계에서 Busy가 반환된 요청은 반드시 장치가 이미 실행했는가?','제출 거부와 실행 후 완료를 구분한다','모든 Busy는 성공한 명령이다','큐에 받아들여지지 않은 요청과 받아들인 뒤 오류 완료된 요청은 수명·재시도 규약이 다릅니다.'),
      details=[detail('CDB와 Data','CDB는 읽기·쓰기 등의 동작과 위치를 표현하고 data scatterlist는 실제 버퍼를 나타냅니다. 명령 바이트와 데이터 바이트를 같은 버퍼로 가정하지 않습니다.'),detail('상태와 복구','장치가 offline·blocked인 경우와 정상 running인 경우 제출 조건이 달라집니다. 오류 복구 스레드와 재설정은 진행 중 요청의 수명까지 관리해야 합니다.')])

    topic('ATA·링크와 명령 큐','저장장치','drivers/ata/libata-core.c','ata_qc_issue',
      'SATA 장치의 명령을 동시에 실행할 때 각 명령의 tag와 링크 상태를 관리해야 합니다.',
      'Libata는 ATA 명령을 queued command로 관리합니다. NCQ는 여러 tag의 명령을 진행할 수 있고 sactive 비트맵으로 추적합니다. 비NCQ 경로의 active_tag와 활성 링크 수는 별도이며 protocol에 따라 PIO·DMA 등의 데이터 전송 방식이 달라집니다.',
      'ata_queued_cmd의 tag·hw_tag·taskfile·protocol을 구분합니다. 명령 준비→issue→인터럽트·완료→error handling을 읽고 tag를 재사용하기 전 이전 명령의 수명이 끝났는지 확인합니다.',
      'ata_qc_issue의 ata_is_ncq·sactive·active_tag와 issue 후 오류 경로를 읽으세요.',
      q('NCQ 진행 중 tag 3을 비트맵에 표시하는 값은?','1<<3, 즉 8','항상 3','비트 위치가 tag를 나타내므로 2의 tag승을 사용합니다. 여러 tag는 비트를 OR해 동시에 추적할 수 있습니다.'),
      q('NCQ와 비NCQ의 활성 명령 관리는 완전히 같은 필드만 사용하는가?','sactive와 active_tag 경로를 구분한다','모든 명령은 tag 없는 하나의 bool이다','소스는 protocol을 분기하고 NCQ의 활성 비트 집합과 비NCQ의 단일 active_tag를 다르게 처리합니다.'),
      details=[detail('비트 집합 검산','tag 1과 3이 활성 상태면 sactive=2|8=10입니다. tag 1의 완료는 해당 비트만 지워야 tag 3의 진행 상태를 보존합니다. 비트 검사와 숫자 equality를 혼동하지 않습니다.'),detail('Protocol과 DMA','Taskfile의 protocol은 데이터 전달 경로와 관계됩니다. 명령 큐 등록과 DMA mapping·캐시 동기화는 다른 단계입니다. 장치 오류 후에도 mapping·tag·링크 상태를 정리합니다.')])

    topic('MMC·카드 요청과 블록 전송','저장장치','drivers/mmc/core/core.c','mmc_start_request',
      'SD·eMMC 저장장치는 명령과 데이터·응답을 묶어 호스트 컨트롤러에 전달해야 합니다.',
      'mmc_request는 command·data·stop 등의 상태를 묶습니다. mmc_start_request는 카드 존재·호스트 소유·요청 준비·retune 상태를 확인한 뒤 host operation으로 실행을 넘깁니다. 완료와 응답 오류·data 오류를 구분하며 고속 동작의 타이밍 조정도 필요합니다.',
      'mmc_host→mmc_card→mmc_request와 block driver를 연결합니다. 호스트 claim과 request completion 규약을 따르고 카드 제거·timeout·부분 전송을 처리합니다.',
      'mmc_start_request의 cmd_completion·retune_hold·card_removed·mmc_mrq_prep를 읽으세요.',
      q('명령 응답이 성공이면 데이터 전송 오류도 반드시 없는가?','명령과 데이터 오류를 각각 확인한다','명령 성공이면 모든 data 오류를 무시한다','Command와 data는 별도 상태를 갖습니다. 응답·전송 길이·data error 등을 확인해야 요청 전체 결과를 판단합니다.'),
      q('요청 전에 카드가 제거된 것이 확인되면 가능한 반환은?','-ENOMEDIUM','무조건 전송 성공','mmc_start_request는 카드 제거를 검사하고 -ENOMEDIUM을 반환합니다. 장치 존재가 요청 실행의 전제입니다.'),
      details=[detail('Completion 수명','init_completion은 대기·완료 동기화 상태를 마련합니다. 초기화했다고 장치 명령이 끝난 것은 아닙니다. request와 그 버퍼는 완료·취소가 보장될 때까지 유지합니다.'),detail('Retuning','고속 신호의 타이밍을 맞추는 tuning과 파일시스템 데이터 복구는 서로 다릅니다. 진행 요청 동안 timing 재조정을 안전하게 조절하는 retune hold 규약을 함께 읽으세요.')])

    topic('MTD·Erase Block과 NAND','저장장치','drivers/mtd/nand/raw/nand_base.c','nand_erase_nand',
      'Raw NAND는 페이지 쓰기와 큰 erase block 지우기, bad block·ECC 특성을 직접 관리해야 합니다.',
      'NAND의 page read/write와 block erase는 단위가 다릅니다. 쓰기로 가능한 비트 변화와 erase가 필요한 변화가 구분되며 bad block·오류 정정·OOB 메타데이터가 관련됩니다. MTD는 raw flash 접근을 제공하고 UBI·파일시스템은 그 위에서 배치와 수명을 관리합니다.',
      'MTD 정보를 조회해 erase size·write size·ECC·bad block 조건을 확인합니다. erase 요청의 정렬·길이·보호 범위·실패 주소를 처리합니다. 실제 erase는 학습용 flash 또는 시뮬레이터에서 수행합니다.',
      'nand_erase_nand의 check_offs_len·secured region·장치 lock·block 반복을 읽으세요.',
      q('페이지 4KiB, erase block 256KiB인 NAND에서 한 페이지 변경의 erase 단위는 항상 4KiB인가?','지우기는 별도 256KiB block 단위다','읽기·쓰기·지우기가 모두 4KiB다','읽기·쓰기 페이지 단위와 erase block 단위는 다릅니다. 다른 유효 페이지 보존과 재배치가 필요할 수 있습니다.'),
      q('Bad block을 발견하면 모든 raw NAND 접근에서 무조건 정상 블록처럼 사용해도 되는가?','bad block과 계층의 배치 규약을 처리한다','ECC만 켜면 bad block을 항상 무시한다','ECC의 비트 오류 정정과 사용 불가능 블록 관리는 별도입니다. UBI 등 상위 계층이 대체 배치를 관리할 수 있습니다.'),
      details=[detail('OOB와 ECC','페이지 데이터 밖의 OOB 영역에는 ECC·bad block 표시 등 규약별 정보가 들어갈 수 있습니다. 사용자 임의 데이터를 넣어도 된다고 가정하지 않고 컨트롤러 layout을 확인합니다.'),detail('실패 주소','범위 전체 erase가 중간에 실패하면 앞부분이 이미 지워졌을 수 있습니다. 실패 반환이 전체 작업의 자동 rollback을 의미하지 않습니다. instr의 실패 정보와 이후 복구 정책을 확인합니다.')])

    topic('RAID5·패리티와 복구','저장장치','drivers/md/raid5.c','handle_stripe',
      '여러 장치에 데이터를 나누고 하나의 장애에서도 복원하려면 패리티와 쓰기 일관성을 관리해야 합니다.',
      'RAID5의 한 stripe는 데이터 조각과 XOR parity를 가집니다. 한 조각을 잃으면 나머지 데이터·parity XOR으로 복원합니다. 부분 쓰기는 read-modify-write나 reconstruct-write를 선택하며 장애 중 불완전 갱신의 write hole을 저널 등 정책으로 고려합니다.',
      'md array의 level·장치 수·degraded 상태와 검증·복구 진행을 조회합니다. RAID의 장치 고장 대응과 파일 삭제·손상·백업은 별도입니다. 학습용 loop 장치에서만 생성·장애 주입을 시험합니다.',
      'handle_stripe의 stripe_head·r5dev 상태·parity 계산·읽기와 쓰기 의존성을 읽으세요.',
      q('데이터 0b1010과 0b0110의 XOR parity는?','0b1100','0b1110','각 비트 XOR으로 1010 XOR 0110=1100입니다. 둘째 데이터 손실 시 1100 XOR 1010=0110으로 복원합니다.'),
      q('RAID5 parity 하나로 같은 stripe의 두 데이터 조각 손실을 일반적으로 복원할 수 있는가?','독립 정보가 부족해 보장하지 못한다','장치 수와 관계없이 항상 복원한다','하나의 XOR 방정식에서 미지수 두 개를 일반적으로 결정할 수 없습니다. RAID6는 별도 독립 패리티를 추가합니다.'),
      details=[detail('부분 갱신 공식','기존 D를 Dnew로 바꿀 때 Pnew=Pold XOR Dold XOR Dnew입니다. 다른 데이터 조각 전체를 읽지 않는 대신 기존 데이터와 패리티를 읽습니다. 무엇을 이미 캐시에 가지고 있는지에 따라 비용이 달라집니다.'),detail('Write hole','데이터와 parity의 일부만 저장된 상태에서 전원이 꺼지면 둘의 일관성이 어긋날 수 있습니다. 패리티 수학이 맞다는 것과 여러 장치 쓰기가 장애 중 일관되다는 것은 다른 문제입니다.')])

    topic('RAID6·이중 패리티','저장장치','lib/raid6/algos.c','raid6_select_algo',
      '두 장치의 손실을 복구하려면 같은 XOR 결과를 두 번 보관하는 것보다 독립 정보가 필요합니다.',
      'RAID6는 XOR인 P와 GF(2^8) 가중 합인 Q라는 독립 parity를 사용합니다. 두 손실을 P·Q 방정식으로 해결하며 계수 연산은 일반 정수 실수 계산과 다릅니다. Linux는 지원 SIMD·일반 연산 구현을 검증·측정해 syndrome 생성과 복구 함수를 선택합니다.',
      '알고리즘 선택 코드와 lib/raid6의 generation·recovery를 연결합니다. 두 장애 허용도 rebuild 중 추가 장애·손상·배치 조건까지 고려하며 백업을 대신하지 않습니다.',
      'raid6_select_algo의 gen_best·rec_best와 int.uc의 P XOR·Q 유한체 갱신을 읽으세요.',
      q('P와 똑같은 XOR parity를 복사해 Q로 두면 두 손실에 독립 방정식이 생기는가?','같은 식의 복사이므로 독립 정보가 아니다','복사본이면 언제나 독립이다','두 미지수를 해결하려면 독립 관계가 필요합니다. RAID6 Q는 위치별 유한체 계수를 사용해 P와 다른 관계를 제공합니다.'),
      q('RAID6의 GF(2^8) 덧셈은 일반적으로 어떤 비트 연산인가?','XOR','소수점 나눗셈','이 유한체의 덧셈은 XOR입니다. 곱셈·역원은 정해진 다항식 기반 연산으로 구현하므로 일반 정수 나눗셈으로 대체하지 않습니다.'),
      details=[detail('두 손실의 방정식','모르는 두 데이터 A·B에 대해 P가 A XOR B 관계를, Q가 서로 다른 계수의 가중 합을 줍니다. 알려진 데이터 기여를 제거한 뒤 유한체 연립식을 풀 수 있습니다. 계수가 같으면 독립성이 사라집니다.'),detail('구현 선택의 역할','raid6_select_algo는 parity 원리를 새로 정의하지 않습니다. 같은 결과를 내는 구현 후보의 지원 조건·성능을 확인해 함수를 선택합니다. P·Q의 실제 루프는 각 구현 파일에서 읽습니다.')])

    topic('BFQ·I/O 예산·공정성','저장장치','block/bfq-iosched.c','bfq_dispatch_request',
      '여러 프로세스가 저장장치를 공유할 때 처리량뿐 아니라 각 작업의 서비스 몫과 반응 시간을 조절해야 합니다.',
      'BFQ는 큐에 weight와 I/O budget을 주어 서비스를 배분합니다. 서비스 트리와 가상 시간으로 다음 큐를 선택하고 한 큐의 budget 만료·idle·새 요청에 따라 진행합니다. 공정성의 단위와 장치 병렬성·순차성에 따른 비용을 함께 고려합니다.',
      '장치의 사용 가능한 scheduler를 조회하고 학습 장치에서 처리량·latency·weight 효과를 비교합니다. CPU 스케줄링과 block I/O 스케줄링을 구분하고 모든 NVMe 환경에서 BFQ가 가장 빠르다고 가정하지 않습니다.',
      'bfq_dispatch_request의 in_service_queue·waiting_rq와 내부 budget·service tree를 읽으세요.',
      q('CPU 시간을 공정하게 배분하면 디스크 I/O의 서비스 몫도 자동으로 같아지는가?','CPU와 I/O 스케줄링은 별도 자원이다','어떤 요청 패턴이든 자동 동일하다','CPU 실행 시간과 저장장치 처리 시간·요청량은 다릅니다. I/O 스케줄러와 장치 특성을 따로 관찰합니다.'),
      q('Budget을 가진 큐에서 요청 하나를 제출할 때 추적해야 하는 값은?','서비스 사용량과 남은 budget','항상 파일 이름의 글자 수','Budget은 선택된 큐가 받은 I/O 서비스와 연결됩니다. 요청 크기·weight·큐의 상태가 dispatch 정책에 관련됩니다.'),
      details=[detail('Idle의 절충','한 순차 작업의 다음 요청을 잠시 기다리면 head 이동 등 비용을 줄일 수 있지만 다른 큐의 대기가 늘 수 있습니다. 병렬 장치에서는 다른 효과가 생기므로 idle 정책을 환경과 함께 봅니다.'),detail('Dispatch와 완료','요청을 골라 장치에 제출하는 시점과 장치 완료는 다릅니다. bfqd lock으로 선택 상태를 보호하고 통계를 갱신하지만 요청 완료까지 그 lock을 잡고 기다리는 것은 아닙니다.')])
