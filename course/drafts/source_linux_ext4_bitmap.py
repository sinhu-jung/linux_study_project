"""All five functions of fs/ext4/bitmap.c, Linux v6.12."""
ROWS = [('ext4 비트맵: 1비트 상태에서 빈 자원 수 계산하기',
  '파일시스템',
  'fs/ext4/bitmap.c',
  'ext4_count_free',
  '한 자원의 사용 여부만 필요할 때 주소나 큰 정수를 저장할 이유는 없습니다. 1비트로 사용 중과 비어 있음을 표시하면 조밀한 고정 범위의 자원 상태를 작게 저장할 수 있습니다. 8192개 상태는 '
  '1024바이트이며 4바이트 정수 배열의 32768바이트보다 작습니다.',
  'ext4_count_free는 numchars*BITS_PER_BYTE에서 memweight(bitmap,numchars)를 뺍니다. memweight는 지정된 메모리 구간에서 켜진 비트 수입니다. '
  '따라서 전체 비트에서 1인 비트를 빼 0인 비트 수를 구합니다. 이 helper는 비트를 바꾸거나 자원을 할당하지 않습니다. 입력 길이도 검사하지 않으므로 호출자가 유효한 버퍼와 범위를 제공해야 '
  '합니다.',
  '두 바이트가 00001111과 10000000이면 전체 16비트 중 켜진 비트는 4+1=5개이고 반환값은 11입니다. inode 비트맵은 inode 테이블 항목의 사용 상태를 나타냅니다. 블록 '
  '비트맵을 해석할 때는 bigalloc의 cluster 단위 등 파일시스템 형식도 확인해야 하며 이 함수는 의미를 모르는 일반 비트 수 계산입니다.',
  '왜 빈 비트 수만으로 파일시스템 전체 여유 공간을 확정하지 않나',
  '함수는 지정된 바이트 안의 0을 전부 셉니다. 그룹 밖 패딩, 예약 메타데이터, 초기화 상태를 스스로 구별하지 않습니다. 원문 문서도 BLOCK_UNINIT일 때 0처럼 취급되는 상태와 실제 '
  '메타데이터 점유가 다를 수 있다고 설명합니다. 따라서 정상 범위와 초기화 계약을 갖춘 호출자가 이 결과를 사용해야 합니다. 파일의 SPDX GPL-2.0 표시와 저작권 주석은 라이선스 정보이고 '
  'include들은 buffer_head 및 ext4 형식·helper 선언을 가져오는 구성입니다.',
  ('두 바이트에 1비트가 총 5개이면 ext4_count_free 결과는?', '11입니다.', '5입니다.', '전체 2×8=16에서 사용 표시 5개를 뺍니다.'),
  ('이 함수가 반환한 빈 비트 하나를 자동으로 예약하나요?',
   '아닙니다. 읽고 개수만 계산합니다.',
   '그렇습니다. 반환과 함께 사용 비트를 세웁니다.',
   '본문에는 비트 변경이 없으므로 실제 할당과 잠금은 별도 경로입니다.')),
 ('ext4 inode 비트맵 체크섬: 16비트와 32비트 비교의 차이',
  '파일시스템',
  'fs/ext4/bitmap.c',
  'ext4_inode_bitmap_csum_verify',
  '디스크에서 읽은 비트맵이 손상되면 이미 사용 중인 inode를 비어 있다고 오해할 수 있습니다. 저장된 체크섬과 현재 데이터로 계산한 체크섬을 비교해 손상을 탐지하되 디스크 형식이 저장할 수 있는 '
  '체크섬 폭에 맞춰야 합니다.',
  'ext4_inode_bitmap_csum_verify는 metadata_csum 기능이 없으면 1을 반환합니다. 기능이 있으면 INODES_PER_GROUP>>3 바이트에 대해 '
  's_csum_seed로 ext4_chksum을 계산합니다. 저장된 low16은 le16_to_cpu로 읽습니다. descriptor 크기가 high 필드 끝 위치 이상이면 high16을 읽어 '
  '16비트 왼쪽으로 옮겨 합칩니다. 그렇지 않으면 계산 결과를 0xFFFF로 마스킹합니다. 마지막 반환은 provided==calculated입니다.',
  '계산 결과가 0x1234ABCD이고 짧은 descriptor에 low=0xABCD이면 비교는 통과합니다. 긴 descriptor라면 high=0x1234도 필요합니다. high=0x5678이면 '
  '0x5678ABCD와 비교하므로 실패합니다. INODES_PER_GROUP=8192인 정상 형식이면 계산 범위는 1024바이트입니다.',
  '왜 반환 1이 언제나 체크섬 검증 실시를 뜻하지 않나',
  '기능이 꺼져 있으면 데이터를 해시하지 않고 바로 1입니다. 또한 체크섬 일치는 손상 가능성을 줄이는 검사이지 서로 다른 모든 데이터가 절대 같은 값이 될 수 없다는 수학적 보장은 아닙니다. 이 '
  '함수는 오류를 탐지할 뿐 손상된 비트맵을 복구하거나 inode를 할당하지 않습니다. low/high가 little-endian 형식이므로 CPU 형식 변환을 빼면 다른 바이트 순서의 CPU에서 잘못 '
  '비교할 수 있습니다.',
  ('metadata_csum이 없을 때 1을 반환하면 실제 계산을 했나요?',
   '아닙니다. 기능 검사에서 조기 반환했습니다.',
   '그렇습니다. 항상 모든 데이터를 계산했습니다.',
   '계산 호출은 기능 검사 뒤에 있습니다.'),
  ('짧은 descriptor에서 계산 결과 0x1234ABCD와 비교하는 값은?',
   '하위 16비트 0xABCD입니다.',
   '상위 16비트 0x1234입니다.',
   'calculated &= 0xFFFF는 상위 부분을 지웁니다.')),
 ('ext4 체크섬 저장: cluster 범위와 메모리 갱신의 책임',
  '파일시스템',
  'fs/ext4/bitmap.c',
  'ext4_block_bitmap_csum_set',
  '비트맵 내용을 바꾼 뒤 체크섬도 새 내용에 맞춰야 다음 검사가 이전 데이터의 체크섬과 비교하지 않습니다. 다만 체크섬 필드를 메모리에서 바꾸는 것과 디스크에 안전하게 기록하는 것은 별도 작업입니다.',
  'ext4_block_bitmap_csum_set은 CLUSTERS_PER_GROUP/8 바이트를 사용합니다. metadata_csum이 없으면 아무 필드도 쓰지 않습니다. 있으면 seed로 계산한 '
  '값의 low16을 cpu_to_le16으로 저장하고 descriptor가 high 필드를 포함하면 high16도 저장합니다. inode setter는 같은 구조이지만 '
  'INODES_PER_GROUP>>3 범위와 inode 체크섬 필드를 사용합니다. block verifier도 cluster 범위로 계산하며 low/high 결합 또는 16비트 마스킹 후 일치를 '
  '검사합니다.',
  '계산값 0x1234ABCD이면 low 필드의 숫자 값은 0xABCD, high 필드는 0x1234입니다. 디스크 little-endian 바이트로 low는 CD AB, high는 34 12입니다. '
  '짧은 descriptor이면 high를 쓰지 않습니다. CLUSTERS_PER_GROUP=32768이면 계산 구간은 4096바이트입니다. bigalloc에서는 cluster 하나에 여러 블록이 '
  '들어갈 수 있어 블록 수와 cluster 수를 무조건 같다고 할 수 없습니다.',
  '왜 이 함수만 호출해서 디스크 갱신을 끝낼 수 없나',
  'setter는 전달받은 gdp 필드에 대입할 뿐 journal 처리, 버퍼 dirty 표시, I/O 제출, flush를 실행하지 않습니다. 호출자는 비트맵 변경과 descriptor 갱신의 잠금 및 '
  '영속성 계약을 별도로 지켜야 합니다. ext4_chksum helper는 준비된 체크섬 드라이버의 4바이트 문맥에 seed를 넣고 update를 실행한 결과를 돌려줍니다. 이 파일이 직접 전체 '
  '체크섬 알고리즘이나 저널을 구현하는 것은 아닙니다.',
  ('block 비트맵 체크섬의 길이 기준은?',
   '그룹당 cluster 수를 8로 나눈 바이트 수입니다.',
   '항상 그룹당 inode 수입니다.',
   'block 함수의 sz는 EXT4_CLUSTERS_PER_GROUP/8이고 inode 함수와 다릅니다.'),
  ('csum_set 반환 뒤 디스크 쓰기까지 완료됐나요?',
   '아닙니다. 메모리의 체크섬 필드를 갱신했습니다.',
   '그렇습니다. setter가 journal commit까지 합니다.',
   '이 본문에는 I/O나 journal commit 호출이 없습니다.'))]

def register(topic,q,detail):
    for title,area,path,symbol,why,principle,use,dt,body,qa,qb in ROWS:
        topic(title,area,path,symbol,why,principle,use,"상태 비트, byte 길이, 체크섬 폭과 디스크 기록의 책임을 나눠 계산하세요.",q(title+" · "+qa[0],*qa[1:]),q(title+" · "+qb[0],*qb[1:]),details=[detail(dt,body),detail("검토 범위","fs/ext4/bitmap.c 전체와 ext4.h의 필드 끝 위치 및 ext4_chksum, bitmaps 문서를 대조했습니다. 실제 파일시스템 손상·복구 실험을 실행한 결과는 아닙니다.")])
