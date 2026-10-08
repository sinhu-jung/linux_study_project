"""Flat register cache: address indexing, sparse cost and absence semantics."""
ROWS = [
('Flat Regcache의 공간 낭비: 사용한2칸 때문에100만 칸을 만드는 이유', 'regcache_flat_init',
 '배열은 번호로 바로 접근할 수 있지만 가장 큰 번호까지 모든 칸을 마련해야 합니다. 실제 레지스터가 몇 개뿐이어도 주소 간격이 크면 사용하지 않는 칸이 대부분의 메모리를 차지합니다. 희소하다는 말은 바로 이런 빈 번호가 많은 상태를 뜻합니다.',
 'flat_init은 map이 있고 stride_order가 음수가 아니며 max_register가 지정됐는지 검사합니다. max_register를 regcache_get_index_by_order로 변환한 값에1을 더한 개수만큼 unsigned int 배열을 kcalloc합니다. helper는 reg>>reg_stride_order입니다. 이후 기본값 목록을 순회해 해당 index에 값을 대입합니다.',
 'stride1,max_register=1000000,unsigned int4바이트를 가정하면1000001칸이라4000004바이트가 필요합니다. 실제 사용하는 주소가0과1000000 두 개면 유효 값8바이트를 위해 나머지3999996바이트도 확보합니다. 사용하지 않는 항목을0으로 초기화해도 그 메모리는 여전히 할당돼 있습니다. 반면 촘촘한 주소0..255라면1024바이트로 직접 접근할 수 있어 배열의 장점이 큽니다.',
 '주소 간격 압축과 한계',
 'stride4이고 order2이면 주소12의 index는3입니다. max_register12이면4칸만 할당합니다. 그러나 사용하지 않는 큰 주소 구간 자체를 제거하는 압축은 아닙니다. 값의 실제 val_bits가8이어도 이 backend는 unsigned int 칸을 사용합니다. 할당 실패는 ENOMEM,설정 조건 실패는 EINVAL입니다. 이 구현의 read/write에는 주소 범위·정렬 검사와 배열 확대가 없으므로 상위 regmap 계약이 필요합니다.',
 ('주소0과1000000만 사용·stride1·4바이트 칸이면 할당량은?', '4000004바이트입니다.', '사용하는 값 두 개의8바이트뿐입니다.', '배열의 직접 인덱싱을 위해0부터최대 index까지 모든 칸을 확보합니다.'),
 ('안 쓰는 칸을0으로 초기화하면 그 칸의 메모리는 반환되나요?', '아닙니다.할당된 칸에0이 들어 있을 뿐입니다.', '그렇습니다.0 값은 자동으로 저장 공간을 사용하지 않습니다.', '값의 내용과 메모리 할당 여부는 서로 다른 상태입니다.')),
('Flat Regcache의 읽기0: 없는 항목과 실제 값0을 구별하지 않는다', 'regcache_flat_read',
 '캐시에서 값0을 읽었다고 그 레지스터를 실제로 읽어 저장한 적이 있다는 뜻은 아닐 수 있습니다. 값 배열만 두고 항목 존재 여부를 따로 저장하지 않으면 초기화된0과 실제0이 같은 표현이 됩니다.',
 'flat_read는 cache[index]를 출력하고0을 반환하며 flat_write는 같은 칸에 값을 대입하고0입니다. 초기 배열은 kcalloc으로0이므로 기본값 목록에 없고 아직 쓰지 않은 유효 범위 칸도0을 읽습니다. 별도 present bitmap이나 ENOENT 분기가 없습니다. exit는 배열을 kfree하고 map->cache=NULL로 바꿔0입니다.',
 '주소0..3의 배열에서 기본값으로주소1=7만 주면[0,7,0,0]입니다. backend가주소2를 읽으면 값0과 성공0을 받습니다. 주소2가 실제 장치에서0이라는 측정 결과는 아닙니다. 다음에주소2=9를 쓰면[0,7,9,0]이 되고 읽기는9입니다. volatile·주소 허용성은 공통 regmap/regcache 층의 조건과 함께 봐야 합니다.',
 '생략된 Ops가 만드는 공통 동작',
 'flat ops에는 init·exit·read·write만 있고 sync·drop은 없습니다. 따라서 공통 전체·구간 동기화는 default_sync를 사용하고 drop_region은 drop callback이 없어 EINVAL입니다. 단순 배열이라는 자료구조 선택이 항목 부재 표현과 삭제 기능의 계약에도 영향을 줍니다. O(1) 직접 접근이라는 장점과 희소 공간 낭비·존재 여부 구분 부재를 함께 평가해야 합니다.',
 ('초기값을 넣지 않은 유효 칸을 읽으면 backend가 ENOENT를 내나요?', '아닙니다.초기0을 읽고 성공을 반환합니다.', '그렇습니다.값0이면 무조건 없는 항목 오류입니다.', '존재 표시 없이 값만 저장하므로 초기0과 저장한0이 구분되지 않습니다.'),
 ('flat ops에 drop이 없으면 공통 drop_region은?', 'EINVAL을 반환합니다.', '자동으로 전체 배열을0으로 만듭니다.', '공통 wrapper가 지원 callback 유무를 검사하며 없는 기능을 임의로 대체하지 않습니다.')),
]

def register(topic,q,detail):
    for title,symbol,why,principle,use,dt,body,qa,qb in ROWS:
        topic(title,'장치·드라이버','drivers/base/regmap/regcache-flat.c',symbol,why,principle,use,
              '최대 주소·실사용 개수·배열 칸 수·초기0·항목 존재 여부를 각각 계산하세요.',
              q(title+' · '+qa[0],*qa[1:]),q(title+' · '+qb[0],*qb[1:]),
              details=[detail(dt,body),detail('검토 범위','Linux v6.12 regcache-flat.c 전체와 internal.h의 shift 인덱스 helper,공통 regcache의 sync/drop 선택을 대조했습니다. 실제 장치 접근·할당 실패 시험이나 상위 regmap 전체 검증은 별도 범위입니다.')])
