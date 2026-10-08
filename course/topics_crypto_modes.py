"""Mode equations and hashing internals, authored against v6.12."""
def register(topic,q,detail):
    topic('HMAC·내부·외부 키 패드','암호 알고리즘','crypto/hmac.c','hmac_setkey',
      '메시지 인증에는 비밀 키를 포함한 정해진 해시 구성이 필요하며 단순 접두사 해시와 구분해야 합니다.',
      'HMAC은 H((K0 XOR opad)||H((K0 XOR ipad)||M))을 계산합니다. K0는 block size에 맞게 정규화한 키이며 긴 키는 먼저 hash하고 짧은 부분은 0으로 채웁니다. 내부·외부 패드 상수는 0x36·0x5c입니다. Linux는 패드까지 처리한 hash 상태를 export해 반복 작업을 줄입니다.',
      'hmac(sha256) 같은 지원 Crypto API를 사용하고 키·tag 길이·검증 규약을 따릅니다. 메시지를 숨기는 암호화와 MAC의 변조 검출을 구분합니다. raw hash에 임의로 키를 붙여 대체하지 않습니다.',
      'hmac_setkey의 keylen>bs·zero fill·ipad/opad XOR·export와 hmac_final의 외부 hash를 읽으세요.',
      q('SHA-256 block size가 64바이트인데 HMAC 키가 100바이트라면 첫 처리는?','키를 SHA-256으로 hash해 정규화한다','100바이트 중 뒤 36바이트를 버린다','긴 키는 hash한 digest로 줄인 뒤 block size에 맞게 0 padding합니다. 단순 truncation은 HMAC 규약이 아닙니다.'),
      q('HMAC에서 내부 해시 결과 뒤에 수행하는 것은?','외부 패드 상태에서 내부 digest를 hash한다','평문을 그대로 tag로 반환한다','hmac_final은 내부 final 뒤 opad 상태를 import하고 그 digest를 finup합니다. 두 단계의 keyed 구성이 핵심입니다.'),
      details=[detail('패드와 저장 상태','Setkey는 ipad·opad byte를 만든 다음 각 pad를 처리한 hash 상태를 export합니다. 이후 pads에 저장된 내용은 준비된 hash state이므로 단순히 원래 pad byte 배열로만 읽으면 틀립니다.'),detail('Tag 검증','수신자는 같은 key·메시지 규약으로 tag를 계산해 정해진 길이로 비교합니다. 비교 시간과 실패 데이터 처리를 확인해야 하며 key가 없는 checksum과 역할이 다릅니다.')])

    topic('CMAC·블록 암호 기반 인증','암호 알고리즘','crypto/cmac.c','crypto_cmac_digest_final',
      '고정 길이 블록 암호를 임의 길이 메시지의 인증값 계산에 사용하려면 마지막 블록 처리 규약이 필요합니다.',
      'CMAC은 CBC 형태로 누적하며 E_K(0)에서 유한체 두 배 연산으로 subkey K1·K2를 만듭니다. 마지막 블록이 완전하면 K1, 불완전하면 1 bit와 0 padding 후 K2를 XOR해 암호화합니다. 키가 필요한 MAC이며 내용 암호화 모드와 다릅니다.',
      'cmac(aes) 등의 검토된 API를 사용하고 빈 메시지·완전 마지막 블록·부분 마지막 블록을 구분해 시험합니다. 임의 CBC 결과 마지막 블록을 그대로 MAC으로 삼지 않습니다.',
      'crypto_cmac_digest_setkey의 0 block·gfmask와 final의 len·0x80·offset을 읽으세요.',
      q('AES-CMAC에서 마지막 블록이 불완전하면 어떤 처리를 하는가?','0x80과 0 padding 후 두 번째 subkey를 사용한다','미완성 바이트를 무시한다','ctx->len!=bs 경로가 0x80을 붙이고 0으로 채우며 consts offset을 다음 subkey로 바꿉니다.'),
      q('CMAC subkey 생성에서 유한체 두 배는 일반 실수 2배인가?','shift와 모듈러스 환원 XOR이다','항상 소수점 곱셈이다','128비트 블록에서 넘친 bit에 따라 환원 상수를 XOR합니다. 소스의 gfmask=0x87을 확인하세요.'),
      details=[detail('Subkey의 이유','완전한 끝과 padding을 추가한 끝을 서로 구분합니다. 같은 블록 암호를 써도 message 길이·마지막 형식을 반영하는 인증 규약이 필요합니다.'),detail('Streaming의 끝','Update는 마지막 완전 블록도 final에서 판단하도록 유지할 수 있습니다. 매 update의 끝을 메시지 끝으로 가정해 subkey를 적용하면 나눠 호출했을 때 결과가 달라집니다.')])

    topic('CBC·이전 암호문과 XOR 연결','암호 알고리즘','crypto/cbc.c','crypto_cbc_encrypt_segment',
      '여러 블록을 암호화할 때 이전 암호문을 다음 블록 계산에 넣는 연결 방식을 이해해야 합니다.',
      'CBC 암호화는 C_i=E_K(P_i XOR C_(i-1))이며 C_0은 IV입니다. 복호화는 P_i=D_K(C_i) XOR C_(i-1)입니다. Padding·IV의 안전 규약·인증은 별도이며 raw kernel CBC는 임의 메시지 길이의 padding을 자동 정의하지 않습니다.',
      '프로토콜이 정한 IV·padding·MAC 규약을 따릅니다. 암호문만으로 인증이 생기지 않으며 복호화 오류가 padding oracle로 드러나지 않도록 설계합니다. 새 구성을 임의로 만들지 않습니다.',
      'crypto_cbc_encrypt_segment의 iv XOR→encrypt→dst를 iv로 복사하는 순서를 읽으세요.',
      q('CBC 두 번째 블록 암호화에 XOR되는 값은?','첫 번째 암호문 C1','언제나 최초 평문 P1','연결 상태는 이전 암호문입니다. 첫 블록만 IV를 사용하고 이후 생성한 ciphertext를 다음 IV 상태로 이어갑니다.'),
      q('CBC kernel 함수가 바이트 길이에 관계없이 PKCS#7 padding을 자동 제공하는가?','블록 길이와 상위 padding 규약을 확인한다','모든 CBC API가 언제나 같은 padding을 넣는다','소스는 완전 블록을 처리하고 남은 길이를 반환합니다. 상위 규약의 padding과 오류 처리는 별도입니다.'),
      details=[detail('In-place 복호화','dst와 src가 같으면 다음 XOR에 필요한 이전 ciphertext가 덮어써질 수 있습니다. 별도 임시 상태와 역순 처리 등 실제 inplace 구현을 봅니다.'),detail('오류 전파와 인증','CBC의 ciphertext 변경은 plaintext에 영향을 주지만 자동 tag 검증이 아닙니다. 변조 검출과 안전한 오류 처리를 별도 프로토콜에서 정의해야 합니다.')])

    topic('CTR·카운터 암호와 XOR','암호 알고리즘','crypto/ctr.c','crypto_ctr_crypt_segment',
      '블록 암호로 키스트림을 만들면 마지막 부분 블록까지 XOR로 처리할 수 있지만 중복 관리가 필요합니다.',
      'CTR은 S_i=E_K(counter_i)를 만들고 C_i=P_i XOR S_i로 처리합니다. 복호화도 같은 XOR입니다. Counter는 정해진 배치와 증가 규약을 따르며 같은 키 아래 counter block이 반복되면 keystream이 재사용됩니다. 인증은 별도입니다.',
      '전체 nonce·counter 공간과 증가·넘침·메시지 간 중복을 관리합니다. 구현의 IV 갱신 규약을 확인하고 검토된 인증 구성을 함께 사용합니다. Partial tail은 keystream 필요한 바이트만 XOR합니다.',
      'crypto_ctr_crypt_segment와 crypt_final의 encrypt_one·crypto_xor·crypto_inc를 읽으세요.',
      q('CTR 복호화가 주로 쓰는 블록 암호 연산은?','counter의 암호화 E_K','ciphertext 자체의 블록 복호화만','counter를 암호화한 동일 keystream으로 XOR합니다. CTR의 복호화라는 상위 동작과 내부 블록 cipher encrypt를 구분합니다.'),
      q('키가 같고 counter block도 반복되면 두 ciphertext XOR에서 무엇이 남는가?','두 plaintext의 XOR','항상 비밀과 무관한 0','C1 XOR C2=(P1 XOR S) XOR (P2 XOR S)=P1 XOR P2입니다. 중복 금지 규약이 핵심입니다.'),
      details=[detail('부분 블록','16바이트 cipher의 마지막 데이터가 5바이트여도 counter 한 블록을 암호화하고 앞 5바이트만 XOR할 수 있습니다. Cipher의 블록 크기와 메시지 padding 필요는 같은 조건이 아닙니다.'),detail('Counter 배치','일반 CTR의 block 증가와 RFC3686의 nonce·IV·counter 구성을 구분합니다. 두 wrapper의 key·IV 규약을 바꾸어 사용하면 서로 다른 keystream이 됩니다.')])

    topic('ECB·블록 독립과 패턴 노출','암호 알고리즘','crypto/ecb.c','crypto_ecb_crypt',
      '소스에 있는 단순 암호 모드의 동작과 보안 한계를 알아야 잘못된 적용을 피할 수 있습니다.',
      'ECB는 각 완전 블록 C_i=E_K(P_i)를 독립 계산합니다. 같은 키에서 같은 평문 블록은 같은 암호문 블록이 되어 반복 패턴이 드러납니다. IV·블록 간 연결·인증을 제공하지 않으며 generic wrapper는 불완전 final 길이를 거부합니다.',
      '알고리즘 코어 시험과 특정 규약의 내부 블록 변환을 이해하는 용도로 읽습니다. 일반 파일·이미지·메시지의 비밀성 모드로 임의 선택하지 않습니다. 검토된 목적별 모드를 사용합니다.',
      'crypto_ecb_crypt의 bsize 반복과 nbytes&&final의 -EINVAL을 읽으세요.',
      q('ECB에서 동일 키로 같은 16바이트 블록 두 개를 암호화하면 결과는?','동일한 암호문 블록 두 개','항상 서로 완전히 다른 블록','각 블록에 같은 deterministic 변환을 적용하므로 반복이 그대로 관찰됩니다. 전체 메시지의 구조가 노출될 수 있습니다.'),
      q('블록 크기 16인데 final의 남은 길이가 3이면 이 wrapper는 어떻게 처리하는가?','-EINVAL 오류','3바이트를 항상 자동 padding','crypto_ecb_crypt는 nbytes&&final이면 -EINVAL입니다. Padding 규약을 자동으로 만들어 주지 않습니다.'),
      details=[detail('Block loop','src·dst를 bsize씩 증가시키며 같은 fn을 호출합니다. 이전 블록이나 위치가 다음 암호에 들어가지 않는 점을 CBC·CTR과 비교하세요.'),detail('보안 목표','강한 AES core도 잘못된 모드 선택을 해결하지 않습니다. 블록 단위의 원시 변환과 전체 데이터의 비밀성·무결성 목표를 분리해 설계합니다.')])

    topic('CCM·카운터와 CBC-MAC','암호 알고리즘','crypto/ccm.c','crypto_ccm_encrypt',
      '암호화와 인증을 정해진 길이·nonce·AAD 규약으로 결합한 또 다른 AEAD 구성을 이해해야 합니다.',
      'CCM은 CBC-MAC으로 형식화한 nonce·메시지 길이·AAD·plaintext를 인증하고 CTR로 데이터와 인증값을 보호합니다. Nonce 길이는 메시지 길이를 담는 L과 연결되며 tag 길이는 허용된 범위와 형식을 따릅니다. GCM과 같은 AEAD 목적이어도 계산은 다릅니다.',
      'ccm(aes) API의 IV 형식·tag 길이·AAD·메시지 길이 한계를 따릅니다. Nonce 중복을 피하고 복호화 인증 실패를 오류로 처리합니다. Linux의 IV[0] 형식과 프로토콜의 nonce byte 배열을 구분합니다.',
      'format_input·set_msg_len·crypto_ccm_auth·CTR 요청·tag 복사를 읽으세요.',
      q('CCM 인증의 주요 MAC 구성은?','CBC-MAC','GHASH가 항상 같은 방식으로 들어감','CCM은 CBC-MAC과 CTR을 결합합니다. GCM의 GHASH와 다른 인증 계산이므로 같은 내부 함수라고 가정하지 않습니다.'),
      q('CCM에서 nonce 길이와 표현 가능한 메시지 길이는 관련이 없는가?','L 길이 필드와 nonce 배치가 연결된다','어떤 nonce든 무한한 길이를 표현한다','Block 안의 nonce와 메시지 길이 필드 배치를 맞춰야 합니다. set_msg_len은 허용 길이와 넘침을 검사합니다.'),
      details=[detail('B0 형식','초기 블록은 AAD 존재·tag 길이·L flags, nonce와 message length를 담습니다. 인증 입력이 raw plaintext만인 단순 CBC loop가 아닙니다.'),detail('Tag와 완료','MAC 계산과 CTR 요청 뒤 tag를 destination 끝에 복사합니다. 비동기 완료와 즉시 오류를 구분하며 검증 실패 출력은 정상 plaintext로 사용하지 않습니다.')])

    topic('GHASH·GF(2^128)의 인증 계산','암호 알고리즘','crypto/ghash-generic.c','ghash_update',
      'GCM에서 메시지 블록들이 인증 누적값에 어떤 수학 연산으로 반영되는지 알아야 합니다.',
      'GHASH는 128비트 블록 X_i마다 Y_i=(Y_(i-1) XOR X_i)·H를 GF(2^128)에서 계산합니다. 곱셈은 polynomial 곱과 정해진 환원이며 정수 곱이 아닙니다. GCM은 H·nonce·AAD·암호문 길이·tag 보호를 추가하므로 GHASH 단독을 범용 암호 해시나 MAC으로 쓰지 않습니다.',
      '검토된 GCM 구성 안에서 GHASH의 key·입력 형식과 padding·length를 따릅니다. Generic의 lookup table·constant-time 성질과 실제 선택 구현을 확인합니다.',
      'ghash_update의 16바이트 XOR→gf128mul_4k_lle와 부분 buffer를 읽으세요.',
      q('GHASH의 field 덧셈에 대응하는 연산은?','XOR','일반 carry 덧셈','GF(2)의 계수 덧셈이므로 각 bit의 합은 XOR입니다. 곱셈과 환원도 일반 정수 연산과 다릅니다.'),
      q('GHASH만 호출해 만든 16바이트를 어떤 메시지의 안전한 독립 MAC으로 써도 되는가?','정해진 암호 모드의 전체 규약이 필요하다','모든 상황에서 GCM tag와 같다','GCM은 GHASH 결과의 보호와 nonce·AAD·길이를 포함합니다. 누적 계산 하나를 전체 인증 구성과 동일시하지 않습니다.'),
      details=[detail('부분 Update','한 호출에 5바이트, 다음에 11바이트가 와도 같은 16바이트 블록을 완성해야 합니다. bytes와 buffer가 미완성 길이를 관리하며 완전 블록이 되면 field 곱셈을 수행합니다.'),detail('표현 순서','표현의 bit·byte 순서와 gf128mul helper 규약이 일치해야 합니다. Big-endian 문자열을 일반 CPU 정수로 곧바로 곱해도 같은 계산이 되는 것은 아닙니다.')])

    topic('POLYVAL·Little-endian 유한체 인증','암호 알고리즘','crypto/polyval-generic.c','polyval_update_non4k',
      '서로 비슷한 유한체 해시도 모듈러스와 표현 규약이 달라서 그대로 바꾸어 쓸 수 없습니다.',
      'POLYVAL은 GHASH와 다른 field 표현·모듈러스로 블록을 누적합니다. v6.12 generic은 byte reverse와 GHASH field 변환을 이용해 계산하며 HCTR2에서 사용됩니다. 원본은 generic이 constant-time이 아니고 실사용용이 아님을 명시합니다. 단독 암호 해시로 사용하지 않습니다.',
      '검토된 모드가 요구하는 key 표현과 실제 하드웨어 구현 선택을 확인합니다. Non4k fallback과 generic lookup table 경로를 구분합니다. 단순 byte reverse만으로 모든 key·곱셈 규약이 자동 맞는 것은 아닙니다.',
      'copy_and_reverse·polyval_mul_non4k·polyval_update_non4k와 파일 첫 warning을 읽으세요.',
      q('polyval_update_non4k가 polyval-generic의 유일한 실제 update loop인가?','원본 주석은 hardware fallback과 generic 4k 경로를 구분한다','이름이 같으므로 모든 구현이 이 루프만 쓴다','Non4k 함수는 SIMD 불가 등의 fallback을 위한 별도 경로입니다. Generic은 4k lookup table을 사용한다고 주석이 설명합니다.'),
      q('이 generic 구현을 constant-time 실사용 코드라고 설명해도 되는가?','원본은 constant-time이 아니라고 경고한다','모든 kernel crypto 코드는 자동 constant-time이다','파일의 warning을 따라 generic 구현의 한계를 설명해야 합니다. 알고리즘과 특정 구현의 부채널 특성은 다릅니다.'),
      details=[detail('변환의 역할','Bytes를 뒤집고 field의 x 연산 등을 적용해 GHASH 곱셈 subroutine을 활용합니다. 입력 표현과 key의 Montgomery 형식 가정까지 맞춰야 POLYVAL 계산이 됩니다.'),detail('암호 모드의 일부','HCTR2나 정의된 AEAD 구성의 universal hash 단계입니다. 키·길이·전체 구성 없이 이 함수만 사용해 메시지 진위를 보장한다고 말하지 않습니다.')])

    topic('SHA-3·Keccak Sponge','암호 알고리즘','crypto/sha3_generic.c','crypto_sha3_init',
      'SHA-2의 블록 압축과 다른 sponge 구조가 입력을 흡수하고 고정 digest를 만드는 과정을 알아야 합니다.',
      'SHA-3는 25개의 64비트 lane인 1600비트 상태를 rate·capacity로 나눕니다. Input을 rate 부분에 XOR하고 Keccak-f의 24 round를 수행한 뒤 digest를 출력합니다. SHA3-256은 capacity 512비트·rate 1088비트이며 SHAKE와 domain padding·출력 규약이 다릅니다.',
      'sha3-256 등 정해진 API를 사용하고 init·update·final, digest 길이·padding을 따릅니다. 같은 Keccak permutation이라고 SHAKE·raw Keccak·SHA-3 결과가 같다고 가정하지 않습니다.',
      'crypto_sha3_init의 rsiz=200-2*digest_size와 final의 0x06·0x80, keccakf round를 읽으세요.',
      q('SHA3-256의 digest 32바이트라면 소스식의 rate 바이트 수는?','136바이트','168바이트','200-2×32=136바이트, 즉 1088비트입니다. 나머지 64바이트가 capacity에 대응합니다.'),
      q('SHA-3와 SHAKE가 같은 permutation을 쓰면 final output 규약도 동일한가?','domain padding과 출력 규약을 구분한다','어떤 길이든 동일 digest다','Permutation의 공유와 전체 hash 구성의 동일성은 다릅니다. Domain separation과 squeeze 길이가 결과의 의미를 정합니다.'),
      details=[detail('Round의 단계','Theta는 열 parity로 확산하고 Rho·Pi는 rotate·위치 변경, Chi는 비선형 변환, Iota는 round constant를 반영합니다. 5×5 lane 배치와 little-endian 입력을 확인합니다.'),detail('Absorb와 Squeeze','Rate 영역에 입력을 XOR해 permutation하는 단계가 absorb입니다. Padding을 포함한 마지막 입력 뒤 필요한 출력 lane을 내보냅니다. 더 긴 출력 규약은 추가 permutation과 domain 정의가 필요합니다.')])

    topic('SHA-512·64비트 압축 함수','암호 알고리즘','crypto/sha512_generic.c','sha512_transform',
      '큰 word를 사용하는 해시의 block·round·길이 표현이 SHA-256과 어떻게 다른지 이해해야 합니다.',
      'SHA-512는 1024비트 block과 여덟 64비트 상태를 사용해 80 round를 수행합니다. 입력 16word의 message schedule을 확장하며 rotate·Ch·Maj·modulo 2^64 덧셈을 사용합니다. 소스의 W[16]은 80word를 동시에 보관하지 않고 ring 형태로 재사용합니다.',
      'sha512 API의 init·update·final을 사용하고 SHA-384·SHA-512/256 등 다른 initial state·출력 규약과 구분합니다. Digest가 길다고 password storage에 raw hash만 사용해도 되는 것은 아닙니다.',
      'sha512_transform의 W[I&15]·i<80·state feed-forward를 읽으세요.',
      q('SHA-512 한 block과 digest의 바이트 수는?','128바이트 block·64바이트 digest','64바이트 block·128바이트 digest','1024/8=128바이트이고 512/8=64바이트입니다. 입력 처리 단위와 출력 길이를 구분합니다.'),
      q('W[16] 배열이면 SHA-512 round가 16개뿐인가?','Ring 재사용으로 80 round의 schedule을 계산한다','배열 크기가 언제나 round 수다','BLEND_OP의 I&15가 저장 슬롯을 재사용합니다. 실제 loop는 i<80이고 여덟 round씩 진행합니다.'),
      details=[detail('Schedule 재사용','새 W를 만들 때 필요한 이전 위치를 modulo 16으로 참조합니다. 덮어쓸 슬롯의 기존 값도 식의 일부이므로 계산 순서가 중요합니다. Array 크기와 알고리즘의 전체 word 개수를 혼동하지 않습니다.'),detail('Feed-forward와 Padding','작업 상태 a…h를 원래 state에 더해 다음 block의 상태를 만듭니다. Final은 padding과 원래 길이를 반영합니다. 단순히 첫 block의 loop만 돌리면 임의 길이 메시지 hash가 완성되지 않습니다.')])
