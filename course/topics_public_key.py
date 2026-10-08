"""Public key calculations and deterministic key material generation."""
def register(topic,q,detail):
    topic('RSA·모듈러 거듭제곱과 Padding','암호 알고리즘','crypto/rsa.c','_rsa_enc',
      '공개 키의 계산을 이해하되 수학적 원시 연산과 실제 안전한 암호·서명 구성을 구분해야 합니다.',
      'RSA는 n=pq와 공개 지수 e, 비밀 지수 d로 m^e mod n과 c^d mod n을 계산합니다. Linux private 경로는 CRT로 p·q에서 계산한 값을 결합합니다. Raw modular exponentiation은 메시지 encoding·padding·서명 digest 규약이 없는 원시 연산입니다.',
      '검토된 프로토콜의 RSA padding·키 크기·서명 정책을 사용합니다. rsa와 pkcs1pad wrapper의 역할을 구분하고 범위·형식·검증 실패를 처리합니다. 작은 toy 숫자는 계산 설명용이며 실제 key로 사용할 수 없습니다.',
      '_rsa_enc의 payload 검사·mpi_powm과 _rsa_dec_crt의 m1·m2·qinv 결합을 읽으세요.',
      q('학습 모형 n=33,e=3,m=4에서 m^e mod n은?','31','64','4^3=64이고 64 mod 33=31입니다. 이 작은 key는 실제 구현의 안전한 key 크기 조건을 만족하지 않는 계산 예입니다.'),
      q('Raw RSA 연산이 성공하면 임의 메시지의 안전한 암호화·서명이 완성되는가?','padding·encoding·정책의 전체 구성이 필요하다','거듭제곱만으로 어떤 목적도 안전하다','원시 RSA는 deterministic하고 구조가 있어 적합한 padding·검증 규약이 필요합니다. Kernel wrapper와 실제 프로토콜을 연결해야 합니다.'),
      details=[detail('CRT 식','m1=c^dP mod p, m2=c^dQ mod q, h=(m1-m2)qInv mod p, m=m2+qh로 계산합니다. 큰 n 한 번의 계산을 작은 두 모듈러 계산으로 나누는 기법입니다. MPI는 CPU word 하나에 들어가지 않는 큰 정수를 관리합니다.'),detail('범위 검사','이 v6.12 원시 구현은 입력을 1<x<n-1로 보수적으로 제한합니다. 표준의 더 넓은 수학적 범위 설명과 실제 소스의 payload 계약을 구분해야 합니다.')])

    topic('Diffie-Hellman·공유 비밀','암호 알고리즘','crypto/dh.c','dh_compute_value',
      '서로 비밀 지수를 보내지 않고 같은 비밀값을 계산하는 키 합의의 원리를 알아야 합니다.',
      'DH는 공개 p·g에서 A=g^a mod p와 B=g^b mod p를 교환합니다. B^a=A^b=g^(ab) mod p로 같은 값을 얻습니다. Group·공개 값 검증과 인증·KDF가 필요하며 키 합의만으로 상대의 신원이나 메시지 인증이 보장되지는 않습니다.',
      '검토된 group·비밀 난수·peer validation을 사용하고 공유 결과를 적합한 KDF로 session key에 연결합니다. Linux kpp 요청에서 src가 없으면 public 생성, 있으면 peer 값으로 공유 계산하는 경로를 구분합니다.',
      'dh_compute_value의 req->src·ctx->g·dh_is_pubkey_valid·_compute_val을 읽으세요.',
      q('DH에서 A=g^a, B=g^b를 교환하면 같은 값을 만드는 식은?','B^a=A^b mod p','A+B가 항상 비밀','거듭제곱 지수가 곱으로 합쳐져 g^(ab) mod p를 양쪽이 계산합니다. 공개 값만 보내고 a·b는 비밀로 유지합니다.'),
      q('인증 없는 DH 교환만으로 중간자 공격을 항상 막는가?','상대 인증과 transcript 규약이 별도 필요하다','공유 비밀이면 상대 신원이 자동 보장된다','중간자가 양쪽과 각각 합의할 수 있습니다. 서명·인증된 프로토콜과 KDF를 연결해야 실제 session 의미가 생깁니다.'),
      details=[detail('작은 계산 예','p=23,g=5,a=6,b=15이면 A=8,B=19이며 19^6 mod23=8^15 mod23=2입니다. 작은 수는 원리 설명용입니다. 실제로는 안전한 group 크기와 비밀 지수 조건을 사용합니다.'),detail('Peer 검증','수신 정수가 올바른 범위와 group 조건을 만족하는지 검사합니다. 임의 값을 그대로 거듭제곱하면 작은 subgroup 등 공격 조건이 생길 수 있습니다. 결과 encoding 길이도 맞춥니다.')])

    topic('ECDH·타원곡선 공유 비밀','암호 알고리즘','crypto/ecdh.c','ecdh_compute_value',
      '타원곡선 점의 scalar 곱으로 공유 값을 계산할 때 점·정수·직렬화 길이를 구분해야 합니다.',
      'ECDH는 base point G의 A=aG와 B=bG를 교환해 aB=bA=abG를 계산합니다. Scalar 곱은 점 덧셈·두 배 연산의 반복이며 좌표의 일반 곱셈이 아닙니다. Curve·peer point 검증·공유 값 처리·KDF·인증이 필요합니다.',
      '정해진 curve와 key serialization·peer validation을 따릅니다. Linux generic NIST 경로의 좌표 두 개와 byte 순서·ndigits를 확인합니다. 공유 결과를 raw 애플리케이션 key로 임의 사용하지 않습니다.',
      'ecdh_compute_value의 public_key_sz=2*nbytes와 ecc_shared_secret·공개 생성 경로를 읽으세요.',
      q('Generic ECDH public key의 x·y가 각각 32바이트라면 두 좌표 데이터 길이는?','64바이트','32바이트','2×32=64바이트입니다. 이 kernel 요청 규약과 SEC1의 prefix 포함 encoding은 다른 표현일 수 있어 그대로 혼용하지 않습니다.'),
      q('Scalar a와 point B를 곱한다는 것은 x·y에 정수 a를 일반 곱하는가?','곡선의 점 연산으로 scalar multiplication한다','각 좌표에 a만 곱하면 된다','곡선의 group law에 따른 반복 점 덧셈·두 배입니다. 일반 좌표 곱셈은 유효한 ECDH 결과를 만들지 않습니다.'),
      details=[detail('점 검증','좌표가 field 범위와 curve 식·규약을 만족하는지 확인합니다. 입력 길이 성공만으로 올바른 점이 아닙니다. 특정 curve의 order·cofactor 규약도 따라야 합니다.'),detail('오류와 비밀 정리','Public buffer·shared secret buffer 할당과 source 복사 실패를 처리합니다. 비밀 메모리 정리와 request completion까지 연결해야 계산 함수 호출 뒤의 수명 오류를 피합니다.')])

    topic('ECDSA·서명과 일회성 Scalar','암호 알고리즘','crypto/ecdsa.c','_ecdsa_verify',
      '공개 키로 서명을 검사하는 계산과 서명 생성에서 일회성 scalar가 필요한 이유를 이해해야 합니다.',
      'ECDSA 검증은 0<r,s<n을 검사하고 w=s^-1 mod n, u1=hash*w, u2=r*w를 구해 R=u1G+u2Q의 x를 r와 비교합니다. 생성의 k 재사용은 비밀 key를 노출할 수 있습니다. 이 v6.12 파일의 검증 구현을 임의 서명 생성 API로 설명하지 않습니다.',
      '지원 curve·digest truncation·ASN.1 r/s parsing·신뢰 public key를 확인합니다. 서명 생성은 검토된 nonce 규약을 사용합니다. 검증 오류와 서명자의 신뢰 정책은 별도입니다.',
      '_ecdsa_verify의 r/s 범위·vli_mod_inv·Shamir multiplication·최종 x 비교를 읽으세요.',
      q('ECDSA에서 r=0 또는 s=0이면 이 검증 경로는 허용하는가?','-EBADMSG로 거부한다','0이면 가장 강한 서명이다','코드는 0<r,s<n 조건을 확인합니다. 형식이 읽혔다고 수학적 범위가 유효한 것은 아닙니다.'),
      q('서명 생성의 같은 k를 다른 메시지에 반복 사용해도 안전한가?','비밀 key 노출 위험이 생긴다','어떤 nonce라도 반복이 항상 안전하다','s=k^-1(hash+r*d) 관계에서 같은 k의 여러 식이 비밀 d를 추론하게 할 수 있습니다. 검토된 일회성·결정적 nonce 규약을 따릅니다.'),
      details=[detail('검증의 두 Modulus','곡선 좌표의 field modulus p와 scalar order n은 역할이 다릅니다. r/s 범위와 역원은 n 기준이며 점 연산의 좌표는 curve field 기준입니다. 서로 같은 정수로 가정하면 계산이 틀립니다.'),detail('Shamir 기법','u1G와 u2Q를 따로 전부 계산하는 대신 함께 진행해 연산을 줄일 수 있습니다. ecc_point_mult_shamir를 통해 두 scalar와 두 point가 어떻게 연결되는지 읽습니다.')])

    topic('Curve25519·Montgomery Ladder','암호 알고리즘','lib/crypto/curve25519-fiat32.c','curve25519_generic',
      '32바이트 key 교환의 내부는 byte 배열뿐 아니라 field·scalar·조건부 교환의 수학 규약입니다.',
      'Curve25519 generic은 scalar를 clamp하고 Montgomery ladder로 u-coordinate의 scalar multiplication을 계산합니다. 두 후보 점의 X/Z를 유지하며 bit마다 조건부 swap·doubling·differential addition을 합니다. Field는 2^255−19이며 직렬화·all-zero shared result 처리와 인증은 상위 규약에 따릅니다.',
      '검토된 X25519 프로토콜의 key·peer·KDF·zero 결과 규약을 사용합니다. Curve 함수 성공과 peer 인증을 구분합니다. 생성된 fiat32 산술 코드의 불변식과 proof 범위를 소스 주석 그대로 확인합니다.',
      'curve25519_generic의 clamp·pos loop·swap·field invert와 상위 curve25519 API를 읽으세요.',
      q('Curve25519 generic에서 scalar 배열은 몇 바이트인가?','32바이트','255바이트','소스는 e[32]에 scalar를 복사해 clamp합니다. Field bit 수와 encoding byte 길이는 다른 단위입니다.'),
      q('Montgomery ladder에서 사용하는 field modulus는?','2^255−19','2^256','곡선 이름의 255는 field와 관련되며 산술은 2^255−19 아래에서 환원합니다. CPU word의 자연 overflow만으로 같은 계산이 되지 않습니다.'),
      details=[detail('Clamp','Scalar의 하위 세 bit를 지우고 최상 byte의 최고 bit를 지우며 다음 bit를 설정하는 규약을 따릅니다. 이 설정은 임의의 난수 byte 배열을 그대로 scalar로 해석하는 것과 다릅니다.'),detail('Proof의 경계','파일 주석은 ladder 수학 증명의 전제와 byte decoding 등 포함하지 않은 부분을 구분합니다. Formal proof라는 말만 보고 모든 호출 규약·부채널·통합이 무제약 안전하다고 주장하지 않습니다.')])

    topic('DRBG·상태·Reseed·예측 저항','암호 알고리즘','crypto/drbg.c','drbg_generate',
      '보안 난수는 초기 entropy로 시작해 내부 상태를 갱신하며 출력하므로 seed·재시드 경계를 알아야 합니다.',
      'Deterministic random bit generator는 내부 state와 hash·HMAC·cipher 등 구성을 통해 출력·상태 갱신을 합니다. 초기화 전 생성은 거부하며 요청 크기·추가 입력·reseed 한계를 확인합니다. 결정적 계산에서 보안성이 생기는 전제는 충분한 seed entropy와 안전한 상태 관리입니다.',
      'Kernel randomness의 상위 API와 DRBG 구현 선택을 구분합니다. 검토된 초기화·reseed·prediction resistance·오류 규약을 따릅니다. 시간·PID만으로 seed를 만들어 보안 난수라고 부르지 않습니다.',
      'drbg_generate의 core·buflen·max_request·addtl·reseed 조건을 읽으세요.',
      q('DRBG가 deterministic이면 같은 seed와 같은 입력 순서에서 출력은 달라야 하는가?','같은 상태·입력 규약이면 같은 계산을 한다','항상 비결정적으로 달라진다','알고리즘은 결정적입니다. 보안 전제는 공격자가 seed와 내부 상태를 알지 못하고 충분한 entropy가 제공되는 것입니다.'),
      q('초기 seeded core가 없는 상태에서도 생성 요청을 성공으로 취급하는가?','소스는 -EINVAL로 거부한다','출력 buffer가 있으면 항상 성공한다','drbg_generate는 drbg->core를 확인합니다. Buffer 유효성과 안전한 초기 상태 준비는 별도 조건입니다.'),
      details=[detail('Generate와 Reseed','상태에서 출력을 만든 뒤 내부를 갱신합니다. Reseed는 새 entropy를 넣는 단계이며 additional input의 존재만으로 entropy 공급이 같아지는 것은 아닙니다.'),detail('상태 유출','현재 state가 유출됐을 때 이전·이후 출력 보호 성질은 구성과 갱신·reseed에 따릅니다. 단순 PRNG와 검토된 DRBG의 상태 관리 규약을 구분합니다.')])

    topic('KDF·SP800-108 Counter Mode','암호 알고리즘','crypto/kdf_sp800108.c','crypto_kdf108_ctr_generate',
      '하나의 비밀 재료에서 목적이 다른 여러 key를 만들 때 구분된 context와 길이를 반영해야 합니다.',
      'Counter-mode KDF는 PRF key를 설정하고 counter i와 정해진 info를 MAC해 필요한 출력을 이어 붙입니다. Linux 함수는 big-endian 32비트 counter를 1부터 사용하고 info의 여러 kvec을 순서대로 반영합니다. Label·context·출력 bit 길이 등의 info 형식은 호출 규약에 맞게 준비해야 합니다.',
      '검토된 KDF 프로토콜의 info encoding·PRF·key·길이를 따릅니다. 서로 다른 용도는 domain context로 구분합니다. 이 함수가 임의 password를 강한 key로 만드는 느린 password KDF와 같다고 가정하지 않습니다.',
      'crypto_kdf108_ctr_generate의 counter·info_nvec·digest length·마지막 부분 복사를 읽으세요.',
      q('PRF 출력 32바이트에서 80바이트를 만들면 몇 번 출력과 마지막 몇 바이트가 필요한가?','3번·마지막 16바이트','2번·마지막 32바이트','32+32+16=80입니다. 마지막 digest 전체를 만든 뒤 필요한 앞부분만 복사합니다.'),
      q('Counter KDF에서 서로 다른 key 용도를 같은 info로 무조건 파생해도 되는가?','프로토콜의 domain 구분을 반영한다','용도와 context는 항상 무의미하다','같은 key·counter·info는 같은 출력을 만듭니다. 용도별 label·context 규약으로 key 사용을 구분해야 합니다.'),
      details=[detail('Info는 호출자 계약','함수는 kvec을 순서대로 hash update합니다. Label·separator·context·length를 모두 자동 조립하는 API라고 설명하면 틀립니다. 호출자가 해당 표준 구성의 직렬화를 맞춥니다.'),detail('부분 실패','생성 중 오류가 나면 어떤 출력 byte가 쓰였는지와 원래 목적의 key 생성 실패를 구분합니다. 임시 digest·실패 출력의 비밀 정리 규약도 확인합니다.')])

    topic('AES Key Wrap·키 포장과 무결성','암호 알고리즘','crypto/keywrap.c','crypto_kw_encrypt',
      '다른 key를 저장·전달할 때 key 재료의 포장 형식과 복원 검증을 정해진 규약으로 처리해야 합니다.',
      'AES-KW는 64비트 A와 R 조각을 128비트 block으로 암호화하고 counter t를 A에 XOR하는 여섯 순회를 수행합니다. Unwrap은 역순 계산 후 A의 상수 형식을 확인합니다. v6.12 wrapper는 마지막 A를 req->iv로 전달하므로 dst의 R만 저장하면 전체 포장 구성이 아닙니다.',
      'kw(aes)의 최소 두 semiblock·8바이트 배수와 IV/A 전달 규약을 따릅니다. 전체 형식은 추가 64비트 A를 포함하고 오류·검증 실패를 처리합니다. 임의 데이터의 일반 AEAD와 목적을 구분합니다.',
      'crypto_kw_encrypt의 A=0xa6…·i<6·t++·req->iv 복사와 decrypt 검증을 읽으세요.',
      q('16바이트 key 재료의 표준 KW 포장에 추가 A 8바이트를 포함하면 길이는?','24바이트','16바이트','R 데이터 16바이트와 A 8바이트를 함께 보존해야 합니다. 이 kernel API는 A를 req->iv에 별도로 전달합니다.'),
      q('Kernel KW encrypt 후 dst의 R만 남기고 req->iv의 A를 버려도 완전한 결과인가?','A도 포장 규약에 맞춰 보존해야 한다','항상 A는 무의미하다','소스는 마지막 A를 caller가 가져가도록 req->iv에 복사합니다. API buffer 배치와 표준 포장 바이트열을 구분해야 합니다.'),
      details=[detail('6×n 순회','n개 8바이트 R을 여섯 번 돌면서 A||R을 AES에 넣고 A에 t를 반영합니다. 16바이트 R이면 n=2이므로 12번 block 암호 연산입니다.'),detail('Unwrap 검증','역산한 A가 정해진 초기 상수와 일치하는지 검증합니다. 복호화 계산을 수행했다는 사실과 유효한 wrapped key가 나왔다는 판단은 다릅니다.')])

    topic('Adiantum·넓은 블록 암호화','암호 알고리즘','crypto/adiantum.c','adiantum_crypt',
      'AES 가속이 없는 환경의 길이 보존 저장 암호에서는 넓은 데이터 단위에 맞춘 구성이 쓰일 수 있습니다.',
      'Adiantum은 왼쪽 bulk와 마지막 16바이트를 나누고 tweak·NHPoly1305 hash·XChaCha stream·블록 cipher를 결합합니다. 첫 hash를 오른쪽에 modulo 2^128 덧셈하고 block 변환·bulk stream 처리·끝 hash로 길이를 보존합니다. Wide-block 비밀성 구성 자체가 인증 tag를 제공하는 것은 아닙니다.',
      '검토된 저장 암호 정책의 tweak·key·최소 길이·지원 조합을 따릅니다. xchacha12/20·AES 등 구성 이름과 kernel selection을 확인합니다. Network AEAD의 nonce·tag 규약으로 임의 대체하지 않습니다.',
      'adiantum_crypt의 bulk_len·첫 hash·rbuf·stream 요청과 끝 hash를 읽으세요.',
      q('길이 4096바이트에서 마지막 16바이트를 빼면 bulk_len은?','4080바이트','4096바이트','4096-16=4080입니다. Bulk와 오른쪽 block이 서로 다른 계산 단계에 들어갑니다.'),
      q('Adiantum wide-block encryption 자체가 GCM 같은 인증 tag를 추가하는가?','길이 보존 암호와 인증은 구분한다','모든 결과 끝에 16바이트 tag를 추가한다','저장 암호의 길이 보존과 AEAD 무결성은 다른 성질입니다. Tweak·hash가 있어도 자동 tag가 생기지 않습니다.'),
      details=[detail('Adder와 XOR 차이','소스 주석의 P_R+H는 128비트 정수 modulo 덧셈을 뜻합니다. HCTR2의 XOR식과 같은 연산이라고 바꾸어 설명하면 틀립니다. 자료 표현 le128도 확인합니다.'),detail('비동기 Bulk','Stream 처리 뒤 callback에서 나머지 hash·오른쪽 결과를 완성할 수 있습니다. 첫 요청 함수 반환과 전체 output completion을 구분해야 buffer 수명이 맞습니다.')])

    topic('HCTR2·길이 보존과 Universal Hash','암호 알고리즘','crypto/hctr2.c','hctr2_crypt',
      '블록 위치와 전체 단위의 내용을 결합해 같은 길이의 저장 암호를 구성하는 과정을 알아야 합니다.',
      'HCTR2는 첫 16바이트 M과 나머지 N을 나누어 MM=M XOR H(T||N)을 계산하고 UU=E(MM), S=MM XOR UU XOR L로 XCTR bulk 변환을 준비합니다. 변환된 bulk의 hash를 첫 block에 반영합니다. POLYVAL·XCTR·block cipher의 합성으로 인증 tag 없는 길이 보존 암호를 만듭니다.',
      'hctr2의 tweak·key 파생·최소 한 block·실제 알고리즘 구성 규약을 따릅니다. 암호화와 복호화는 첫 block cipher 방향이 다르지만 bulk XCTR는 동일 keystream 변환을 활용합니다.',
      'hctr2_crypt의 first_block·hash_tweak·digest XOR·xctr_iv와 hctr2_finish를 읽으세요.',
      q('HCTR2 첫 block 암호화와 bulk XOR 변환은 같은 역할인가?','첫 block cipher와 XCTR bulk를 구분한다','모든 byte를 같은 AES 한 번에 넣는다','첫 block에서 hash와 block 변환으로 bulk용 S를 만들고 나머지를 XCTR로 처리합니다. 두 영역의 계산을 연결해야 합니다.'),
      q('15바이트 요청을 이 hctr2_crypt에 넣으면 어떻게 되는가?','최소 16바이트 검사로 -EINVAL','항상 16바이트를 읽어 성공한다','req->cryptlen<BLOCKCIPHER_BLOCK_SIZE를 거부합니다. Buffer 밖을 읽기 전에 최소 길이 전제를 확인합니다.'),
      details=[detail('Encrypt와 Decrypt','enc일 때 E, 아닐 때 D로 첫 block을 바꾸고 MM·UU 역할을 맞춥니다. XCTR의 암·복호는 같은 XOR stream 경로이므로 내부 encrypt API 호출이 복호화 오류를 뜻하지 않습니다.'),detail('Tweak와 Length','Hash 입력의 tweak·length 규약과 key에서 만드는 L을 포함해야 전체 합성이 맞습니다. 임의 hash와 counter mode를 비슷하게 붙이면 동일한 HCTR2가 되지 않습니다.')])
