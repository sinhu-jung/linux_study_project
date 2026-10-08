"""Individual hash/cipher families and asynchronous API execution."""
def register(topic,q,detail):
    topic('SHA-1·80라운드와 보안 한계','암호 알고리즘','lib/crypto/sha1.c','sha1_transform',
      '소스에 남은 해시를 이해할 때 내부 계산과 새 설계에 사용할 보안 성질을 구분해야 합니다.',
      'SHA-1은 512비트 block을 다섯 32비트 state에 반영하며 80 step을 20개씩 다른 함수·상수로 처리합니다. Word schedule은 XOR·rotate로 확장하고 작업 state를 기존 digest에 더합니다. 충돌 저항이 깨진 해시이므로 새 보안 구성에서 안전한 collision-resistant hash로 취급하지 않습니다.',
      '역사적·호환 경로를 분석하며 새 보안 구성은 검토된 최신 규약을 따릅니다. 원시 transform과 init·update·final의 padding·길이 처리를 연결합니다. 해시 길이와 실제 보안 강도는 다릅니다.',
      'sha1_transform의 0..19·20..39·40..59·60..79와 digest 누적을 읽으세요.',
      q('SHA-1의 다섯 32비트 상태 결과 길이는?','20바이트','64바이트','5×32=160비트이고 160/8=20바이트입니다. 입력 block 64바이트와 출력 길이는 다릅니다.'),
      q('소스가 SHA-1을 제공하면 새 보안 설계의 충돌 저항도 자동 충분한가?','구현 존재와 현재 안전한 사용 목적은 구분한다','Kernel에 있으면 모든 목적에 안전하다','호환 지원과 안전한 새 설계는 다른 판단입니다. SHA-1의 충돌 저항 한계를 무시해 서명 digest로 임의 선택하지 않습니다.'),
      details=[detail('20-step 묶음','초기 16word는 입력에서 읽고 뒤 word는 이전 schedule을 조합합니다. 각 20step의 Boolean 함수와 상수는 다릅니다. Loop 수만 따라가고 round macro를 생략하면 실제 계산을 알 수 없습니다.'),detail('해시 보안 성질','Preimage·second preimage·collision resistance는 서로 다른 목표입니다. 알려진 충돌 문제를 단순히 출력 byte 수만 보고 평가하지 않습니다.')])

    topic('MD5·128비트 해시와 충돌 한계','암호 알고리즘','crypto/md5.c','md5_transform',
      '오래된 digest 구현이 어떤 round로 계산되는지와 보안 검증에 쓰면 안 되는 이유를 함께 알아야 합니다.',
      'MD5는 네 32비트 상태와 512비트 block으로 네 묶음 총 64step을 수행합니다. Boolean 함수·입력 word 순서·상수·rotate가 step마다 달라지고 마지막 state를 누적합니다. 충돌 공격이 가능하므로 신뢰 서명·적대적 무결성 검증의 raw hash로 사용하지 않습니다.',
      '기존 형식의 호환·검증 경로를 읽되 새로운 보안 digest에 임의 채택하지 않습니다. Update와 final의 little-endian·길이·padding을 확인합니다. 단순 오류 탐지와 공격자에 대한 인증을 구분합니다.',
      'md5_transform의 F1..F4·MD5STEP과 md5_final을 읽으세요.',
      q('MD5 네 32비트 상태의 digest 크기는?','16바이트','32바이트','4×32=128비트이고 128/8=16바이트입니다. Hash 이름과 출력 bit 수, block 길이를 따로 계산합니다.'),
      q('두 파일 MD5가 같다는 사실만으로 적대적 교체를 안전하게 검증할 수 있는가?','충돌 한계와 신뢰 인증 규약을 고려해야 한다','모든 경우 파일 진위가 증명된다','MD5는 공격자에 대한 충돌 저항을 보장할 수 없습니다. 신뢰 기준·서명·적합한 hash 선택이 필요합니다.'),
      details=[detail('Step macro','MD5STEP은 state에 함수·word·상수를 더해 rotate한 뒤 다른 state를 더합니다. u32 overflow는 modulo 2^32 계산입니다. Input 읽기의 little-endian 규약을 지킵니다.'),detail('Feed-forward','64step의 a·b·c·d를 처음 hash에 더합니다. 단일 block의 작업 결과와 임의 길이 메시지 final digest는 padding까지 포함해야 같아집니다.')])

    topic('MD4·역사적 호환과 충돌 한계','암호 알고리즘','crypto/md4.c','md4_transform',
      '호환 프로토콜의 오래된 해시를 읽을 때 계산을 이해하더라도 안전한 새 설계와 혼동하지 않아야 합니다.',
      'MD4는 네 32비트 상태와 16word 입력으로 세 round 총 48step을 수행합니다. F·G·H와 서로 다른 word 순서·rotate·상수를 적용하고 기존 state에 더합니다. 충돌 등 보안 한계가 심하므로 새로운 암호 인증·비밀번호 보관 구성에 사용하지 않습니다.',
      '기존 호환 경로의 데이터 encoding·padding·digest format을 분석합니다. 구현이 존재한다는 사실을 사용 권장으로 읽지 않습니다. 상위 인증 프로토콜의 전체 공격 경계는 별도로 평가합니다.',
      'md4_transform의 ROUND1·ROUND2·ROUND3와 init·final을 연결하세요.',
      q('MD4의 세 round에 각각 16step이면 전체 step 수는?','48','64','3×16=48입니다. MD5의 네 round 64step과 다른 계산입니다.'),
      q('MD4 구현을 공부했다면 새 password storage를 raw MD4로 만들면 되는가?','학습과 안전한 사용 목적을 구분한다','Kernel 구현이면 모든 password에 적합하다','MD4는 오래된 호환 hash이며 password storage의 느린 KDF·salt·보안 정책을 대체하지 않습니다.'),
      details=[detail('Word 순서','첫 묶음은 순서대로, 이후 묶음은 다른 순서로 입력 word를 사용합니다. 같은 Boolean 함수만 바꿔 세 번 반복하는 loop와 동일하지 않습니다.'),detail('호환의 의미','기존 peer나 저장 형식 때문에 구현이 유지될 수 있습니다. 구현 삭제 여부와 암호학적 안전 판단은 다르며 학습 기록에 제한을 명시합니다.')])

    topic('BLAKE2b·압축과 키 기반 모드','암호 알고리즘','crypto/blake2b_generic.c','blake2b_compress_one_generic',
      '빠른 해시의 내부 state·byte counter·마지막 block 표시와 key 기반 모드를 구분해야 합니다.',
      'BLAKE2b는 128바이트 block을 16개의 64비트 message word로 읽고 16word 작업 state에 12round의 G 혼합을 합니다. Counter와 final flags가 state에 반영되고 output 길이·key length 등의 parameter가 초기화를 구분합니다. 서로 다른 output 길이를 단순히 하나의 digest truncation과 동일시할 수 없습니다.',
      '정해진 blake2b API·출력 길이·key 규약을 사용합니다. 마지막 block 처리와 counter overflow를 확인하고 keyed mode와 unkeyed digest를 구분합니다. 메시지 나눠 update해도 같은 결과가 나오는 규약을 검증합니다.',
      'blake2b_compress_one_generic의 m·v·S->t·S->f와 G round·final을 읽으세요.',
      q('16개의 64비트 message word가 담는 block 크기는?','128바이트','64바이트','16×64=1024비트이고 128바이트입니다. Hash state word 수와 작업 word 수를 구분합니다.'),
      q('마지막 block 표시가 hash 계산과 무관한가?','final flag가 압축 상태에 반영된다','항상 모든 block을 완전히 같게 처리한다','v[14]·v[15]에 S->f가 반영됩니다. 마지막 block 처리 규약과 byte counter를 지켜야 올바른 digest가 나옵니다.'),
      details=[detail('G의 ARX','덧셈·XOR·rotate로 네 작업 word를 섞고 column·diagonal 적용을 반복합니다. Message permutation sigma가 각 round에 사용할 word 순서를 정합니다.'),detail('Parameter 초기화','출력 크기와 key 사용 등을 초기 state에 넣습니다. 따라서 output 길이를 선택하는 규약은 결과 끝을 나중에 자르는 단순 처리와 구분해야 합니다.')])

    topic('SM3·메시지 확장과 압축','암호 알고리즘','crypto/sm3.c','sm3_transform',
      '다른 해시 family의 word schedule과 Boolean 함수 전환을 같은 SHA 이름의 구현으로 혼동하지 않아야 합니다.',
      'SM3는 512비트 block과 여덟 32비트 state로 64step을 계산합니다. P0·P1 permutation·rotate·XOR로 schedule을 만들고 앞 16step과 이후 FF·GG 함수를 다르게 사용합니다. Linux는 W[16] 저장을 재사용하며 작업 결과를 기존 state에 XOR합니다.',
      'sm3 init·update·final을 사용하고 입력 big-endian·길이·padding을 확인합니다. 표준 요구나 프로토콜의 선택을 따르며 SM3라는 digest만으로 메시지 인증이 되었다고 판단하지 않습니다.',
      'sm3_transform의 W1/W2·R1/R2·P0/P1과 마지막 state XOR을 읽으세요.',
      q('SM3의 256비트 digest 길이는?','32바이트','64바이트','256/8=32바이트입니다. 입력 block은 64바이트이며 출력 크기와 다릅니다.'),
      q('SM3의 작업 state 반영이 SHA-256의 덧셈과 항상 같은가?','이 구현은 기존 state에 XOR을 적용한다','해시의 마지막 반영은 모두 동일하다','Algorithm마다 feed-forward가 다릅니다. 소스의 state XOR을 실제 계산대로 설명해야 합니다.'),
      details=[detail('함수 전환','초기 FF·GG는 XOR을 사용하고 후반은 다른 Boolean 관계를 사용합니다. R1·R2의 구간과 rotating constant를 읽어 64step의 차이를 확인합니다.'),detail('P0·P1','Word와 그 회전본을 XOR해 확산합니다. 메시지 schedule과 상태 갱신에서 쓰는 permutation이 다르므로 호출 이름을 확인합니다.')])

    topic('SM4·32라운드 블록 암호','암호 알고리즘','crypto/sm4.c','sm4_crypt_block',
      '128비트 블록이 네 word를 갱신하는 round를 거쳐 출력될 때 key schedule과 데이터 변환을 구분해야 합니다.',
      'SM4는 네 32비트 word로 128비트 block을 표현하고 32round에서 이전 word·round key를 S-box와 선형 변환에 넣습니다. 데이터 선형 변환의 rotate는 2·10·18·24, key 확장은 13·23을 사용합니다. 마지막 네 word는 역순으로 출력하며 decrypt는 round key 순서를 뒤집습니다.',
      '지원 SM4 Crypto API와 모드를 사용합니다. Core block 암호는 nonce·인증·긴 메시지 규약을 제공하지 않습니다. 키 확장·암복호 key 배열·byte order를 확인합니다.',
      'sm4_crypt_block의 i+=4·sm4_round와 x[3-i] 출력, key expansion을 읽으세요.',
      q('소스 loop가 i<32, i+=4이고 각 loop에 round 네 번이면 전체 round는?','32','8','Loop는 여덟 번이고 매번 네 round를 수행해 32입니다. Loop 반복 수와 알고리즘 round 수를 구분합니다.'),
      q('SM4 final word 출력은 입력 상태 x0..x3 순서 그대로인가?','마지막 네 word의 순서를 반대로 내보낸다','언제나 x0부터 그대로다','소스의 put_unaligned_be32(x[3-i])를 확인합니다. Byte order와 word 순서 두 가지를 맞춰야 합니다.'),
      details=[detail('S-box와 L','비선형 S-box로 byte를 바꾼 뒤 word를 여러 rotate와 XOR해 영향을 퍼뜨립니다. Key expansion에서 쓰는 Lprime과 data의 L은 회전 값이 다릅니다.'),detail('모드 연결','SM4 core의 16바이트 변환과 CBC·CTR·AEAD 등 상위 모드의 역할은 다릅니다. 동일한 core를 사용해도 전체 보안 성질이 같지 않습니다.')])

    topic('ARIA·치환과 확산','암호 알고리즘','crypto/aria_generic.c','__aria_crypt',
      '키 길이에 따른 round 수와 번갈아 적용하는 치환 계층을 원본의 word 계산으로 이해해야 합니다.',
      'ARIA는 128비트 block과 128·192·256비트 key를 사용해 12·14·16round를 수행합니다. 두 종류 substitution layer와 diffusion·round key XOR을 번갈아 적용하고 마지막은 일반 diffusion round와 다릅니다. Encrypt·decrypt key schedule 배열을 구분합니다.',
      '지원 ARIA API·key length·모드 규약을 사용하고 raw block을 제품 암호 구성으로 임의 사용하지 않습니다. Generic의 table 구현과 실제 hardware 선택의 성능·부채널 특성을 구분합니다.',
      '__aria_crypt의 rounds·odd/even 치환·끝 출력과 setkey를 읽으세요.',
      q('ARIA 256비트 key의 byte 길이와 round 수는?','32바이트·16round','256바이트·12round','256/8=32바이트이며 ARIA의 해당 key 길이는 16round입니다. AES의 round 수와 혼동하지 않습니다.'),
      q('암·복호에서 같은 context라도 선택할 key 배열은 항상 같은가?','enc_key·dec_key 규약을 구분한다','배열 이름은 무의미하다','Wrapper는 __aria_crypt에 enc_key 또는 dec_key를 넘깁니다. Key schedule 변환과 방향을 맞춰야 결과가 맞습니다.'),
      details=[detail('Odd·Even 계층','치환 함수를 번갈아 적용하며 byte별 S-box와 역 S-box 배치가 달라집니다. Diffusion은 여러 byte를 선형 결합합니다. 함수 이름만 보고 AES round와 동일하게 읽지 않습니다.'),detail('Key expansion','Key length와 회전·중간 key derivation으로 round key를 만듭니다. 원래 key를 매 round 똑같이 XOR하는 방식과 다릅니다.')])

    topic('Camellia·Feistel과 FL','암호 알고리즘','crypto/camellia_generic.c','camellia_encrypt',
      'Feistel round와 추가 FL 변환이 key length별로 어떻게 배치되는지 구분해야 합니다.',
      'Camellia는 128비트 block을 두 절반으로 나누어 F function을 교차 적용합니다. 128비트 key는 18round, 192·256비트는 24round이며 중간 FL·FLinv와 whitening key가 추가됩니다. 소스의 max=24·32는 key table 진행 규약이며 그대로 Feistel round 수가 아닙니다.',
      '지원 Camellia API·key length·상위 모드를 따릅니다. Big-endian word 읽기와 최종 절반 swap을 확인합니다. Feistel cipher라는 공통 이름이 DES와 같은 block·key 규약이라는 뜻은 아닙니다.',
      'camellia_encrypt의 key_length·max와 camellia_do_encrypt의 round 묶음·FL을 읽으세요.',
      q('소스의 max=24를 보고 128비트 Camellia의 Feistel round가 24개라고 해도 되는가?','key table 진행 값과 18round를 구분한다','변수 max는 반드시 round 수다','Whitening·FL 등의 subkey가 포함되는 진행 값입니다. 실제 round 묶음의 계산을 확인해야 합니다.'),
      q('Camellia block 크기 128비트는 몇 바이트인가?','16바이트','24바이트','128/8=16바이트입니다. Key 길이와 block 크기는 별도이며 큰 key를 쓴다고 block도 커지는 것은 아닙니다.'),
      details=[detail('Feistel의 복호화','Round function 자체를 inverse로 만들지 않아도 key 순서를 맞춘 Feistel 역산을 할 수 있습니다. FL·FLinv와 whitening·swap까지 실제 역순 규약을 따라야 합니다.'),detail('Table 최적화','S-box·diffusion을 table word 연산으로 합쳐 구현할 수 있습니다. 개념 함수가 네 개로 나뉘어 있어야 한다는 가정 대신 macro와 key table 인덱스를 확인합니다.')])

    topic('Twofish·키 의존 S-box','암호 알고리즘','crypto/twofish_generic.c','twofish_encrypt',
      '키에 따라 준비되는 lookup과 MDS 혼합, whitening이 암호 core에서 어떻게 연결되는지 알아야 합니다.',
      'Twofish는 128비트 block에 input whitening을 하고 key-dependent S-box·MDS·pseudo-Hadamard 혼합을 포함한 16round를 수행합니다. Generic의 ENCCYCLE은 두 round를 묶어 여덟 번 적용합니다. Output whitening과 최종 word 배치를 포함해야 같은 변환입니다.',
      'Twofish API의 key expansion과 table 준비·암복호 모드 규약을 사용합니다. 실제 key-dependent table과 table lookup의 구현 특성을 검토합니다. Core가 데이터 전체의 인증을 제공한다고 가정하지 않습니다.',
      'twofish_encrypt의 INPACK·ENCCYCLE0..7·OUTUNPACK과 twofish_common의 key setup을 읽으세요.',
      q('Twofish에서 ENCCYCLE 여덟 개가 각각 두 round를 수행하면 전체 round는?','16','8','8×2=16입니다. 소스의 최적화 묶음과 알고리즘 round 단위를 구분합니다.'),
      q('Input whitening이 의미하는 것은?','입력 word에 해당 subkey를 XOR한다','메시지를 모두 0으로 지운다','Whitening은 round 앞뒤의 key mixing입니다. 비밀 데이터 삭제의 zeroization과 다른 의미입니다.'),
      details=[detail('MDS','여러 byte의 변화가 출력 여러 byte에 퍼지도록 유한체 선형 변환을 사용합니다. Key-dependent substitution과 고정 선형 혼합은 역할이 다릅니다.'),detail('Pseudo-Hadamard','두 g 출력의 정수 덧셈 관계로 round 값들을 결합합니다. 유한체 MDS와 modulo word 덧셈은 서로 다른 산술입니다. Key table도 이를 포함해 준비됩니다.')])

    topic('Serpent·Bitslice와 S-box','암호 알고리즘','crypto/serpent_generic.c','__serpent_encrypt',
      '표 lookup 대신 Boolean word 연산으로 많은 S-box bit를 병렬 처리하는 표현을 이해해야 합니다.',
      'Serpent는 128비트 block과 32round에서 key XOR·여덟 S-box의 반복·linear transform을 적용합니다. Bitslice 표현은 여러 bit 위치의 같은 Boolean 계산을 word AND·OR·XOR 등으로 병렬 수행합니다. 마지막 round의 변환과 final key XOR은 일반 round와 구분합니다.',
      '지원 Serpent API와 key length·mode를 따릅니다. r0..r4의 재배치는 S-box 출력 레지스터 역할 변경을 포함하므로 변수 이름 하나를 고정 byte 위치로 해석하지 않습니다.',
      '__serpent_encrypt의 S0..S7·LK·K와 setkey S-box를 읽으세요.',
      q('Bitslice가 주로 활용하는 것은?','word bit 연산으로 여러 S-box 위치를 병렬 계산','모든 byte를 파일로 따로 저장','같은 Boolean 함수를 여러 bit lane에 동시에 적용합니다. Lookup table의 byte index 처리와 다른 구현 방식입니다.'),
      q('Serpent의 S0..S7이 반복되는 이유는?','round에 따른 S-box 선택 규약 때문이다','32round가 모두 같은 입력 key이다','여덟 S-box를 round 순서에 맞춰 반복하고 key·linear 변환을 연결합니다. 함수 이름이 반복돼도 round key와 상태는 다릅니다.'),
      details=[detail('Register 순열','S-box macro 뒤 변수 전달 순서가 바뀌는 최적화가 있습니다. r0 이름을 항상 첫 word라고 가정하기보다 macro의 입출력 의미를 추적합니다.'),detail('Linear transform','Rotate·shift·XOR로 state를 섞습니다. Last round에 적용되는 예외와 마지막 subkey를 함께 읽어야 32round의 정확한 끝을 설명합니다.')])

    topic('DES·Feistel과 짧은 키의 한계','암호 알고리즘','lib/crypto/des.c','des_encrypt',
      '역사적 block cipher의 계산을 공부하더라도 짧은 key와 block의 보안 한계를 함께 알아야 합니다.',
      'DES는 64비트 block을 두 32비트 절반으로 나누어 16 Feistel round를 수행합니다. Expansion·48비트 subkey XOR·S-box·permutation을 사용하며 key의 유효 비밀 bit는 56개입니다. Linux loop는 여덟 번에 두 round씩입니다. DES·3DES의 호환 제공을 안전한 새 사용 권장으로 해석하지 않습니다.',
      '역사적·호환 경로를 분석하고 새로운 설계에서는 검토된 현재 cipher 정책을 따릅니다. DES key byte의 parity·weak key·block size와 3DES EDE 구성의 차이를 확인합니다.',
      'des_encrypt의 IP·i<8 두 ROUND·FP와 key setup을 읽으세요.',
      q('DES loop가 여덟 번이고 ROUND가 두 번이면 전체 round는?','16','8','8×2=16입니다. Initial·final permutation은 round 하나로 세지 않습니다.'),
      q('DES key가 8바이트 형식이면 유효 비밀 key bit가 64개인가?','유효 비밀 bit는 56개다','parity bit도 모두 독립 비밀이다','8바이트의 parity bit를 제외한 key 정보는 56비트입니다. 짧은 key 탐색 한계를 고려해야 합니다.'),
      details=[detail('Feistel 식','Lnew=Rold, Rnew=Lold XOR F(Rold,K) 형태로 진행합니다. F를 inverse하지 않아도 key 역순으로 복호화할 수 있지만 IP·FP·최종 swap 규약은 지켜야 합니다.'),detail('Triple DES','EDE는 여러 DES 연산과 key를 연결한 별도 구성입니다. 더 많은 연산이 현대 목적의 모든 보안·성능 요구를 만족시킨다는 뜻은 아니며 block 크기 한계도 남습니다.')])

    topic('ARC4·순열 상태와 역사적 취약성','암호 알고리즘','lib/crypto/arc4.c','arc4_crypt',
      '오래된 stream cipher가 상태를 갱신하는 방식을 이해하면서 현재 안전한 사용과 구분해야 합니다.',
      'ARC4는 256entry 순열 S와 두 index를 관리합니다. Key scheduling이 S를 섞고 생성 단계는 index 갱신·swap 뒤 선택한 S byte를 plaintext와 XOR합니다. Keystream의 편향과 protocol 취약성 때문에 새로운 안전한 암호 구성에 사용하지 않습니다.',
      '역사적 호환 코드의 state·key setup·stream 지속을 분석합니다. 새로운 key·nonce·인증 요구는 검토된 현대 프로토콜을 따릅니다. 동일 keystream 반복을 피한다는 조건만으로 ARC4의 모든 취약성이 해결되지는 않습니다.',
      'arc4_setkey와 arc4_crypt의 x·y·S swap·out XOR·state 저장을 읽으세요.',
      q('ARC4에서 S의 entry 수와 index wrap 범위는?','256개·0..255','32개·0..31','&0xff는 하위 8비트로 index를 제한해 0부터255를 표현합니다. 배열의 각 entry와 CPU u32 저장 폭은 구분합니다.'),
      q('ARC4의 nonce 반복만 피하면 새로운 암호 설계에 언제나 안전한가?','편향 등 알고리즘·프로토콜 한계도 남는다','어떤 오래된 cipher도 반복만 없으면 안전하다','키스트림 편향 등 별도 보안 한계가 있습니다. 호환 소스를 이해하는 것과 새 사용 권장 여부는 다릅니다.'),
      details=[detail('KSA와 PRGA','KSA는 key byte로 초기 순열을 섞는 단계이고 PRGA는 매 byte마다 상태를 갱신해 stream을 만드는 단계입니다. 매 update마다 KSA를 새로 시작하면 stream continuity가 달라집니다.'),detail('State 수명','같은 context로 나누어 처리한 출력은 state x·y·S를 이어갑니다. 암복호 양쪽의 같은 stream 위치가 맞아야 합니다. State를 복제한 재사용은 별도 keystream 중복 위험을 만듭니다.')])

    topic('Streebog·러시아 해시 압축','암호 알고리즘','crypto/streebog_generic.c','streebog_g',
      '다른 표준 해시에서 block count와 메시지 합계가 final 계산에 어떻게 들어가는지 구분해야 합니다.',
      'Streebog는 512비트 block과 LPS 변환·12round의 E 구조를 사용하는 g_N 압축을 수행합니다. N은 처리 bit 수, Sigma는 메시지 block의 modulo 2^512 합을 추적합니다. Final에 이 두 값을 반영하며 256·512bit 모드의 초기 상태와 출력 규약이 다릅니다.',
      '지원 streebog256·512 API의 init·update·final을 따릅니다. 데이터 byte order·padding·N·Sigma를 확인하고 단순히 긴 모드 결과를 잘라 다른 모드라고 설명하지 않습니다.',
      'streebog_g·streebog_stage2·stage3의 xlps·N·Sigma 업데이트를 읽으세요.',
      q('Streebog-512 digest의 byte 길이는?','64바이트','512바이트','512/8=64바이트입니다. Block 길이도 64바이트지만 입력 처리와 출력 의미는 다릅니다.'),
      q('Streebog의 N과 Sigma는 같은 누적값인가?','처리 길이와 block 합계라는 별도 값이다','둘 다 항상 같은 digest다','길이 누적 N과 데이터 합 Sigma를 분리해 final 압축에 넣습니다. 값의 역할과 modulo 덧셈을 구분합니다.'),
      details=[detail('LPS','비선형 byte 치환 S·byte 순열 P·선형 변환 L을 결합합니다. Table을 활용해 합칠 수 있어 소스 함수 이름과 표준 개념의 경계를 확인합니다.'),detail('G의 결합','E의 계산 결과를 기존 h와 메시지 m에 XOR해 새 h를 만듭니다. 다른 hash의 feed-forward 덧셈을 그대로 복사해서 설명하지 않습니다.')])

    topic('AF_ALG·사용자 공간 Crypto Socket','암호 알고리즘','crypto/af_alg.c','alg_bind',
      '사용자 프로그램이 kernel Crypto API를 이용할 때 socket의 종류와 작업 상태를 구분해야 합니다.',
      'AF_ALG parent socket은 type·algorithm을 bind하고 key 등의 설정을 준비합니다. Accept한 operation socket에 sendmsg·control message로 IV·동작·AAD 등을 전달하고 결과를 읽습니다. Hash·skcipher·AEAD의 길이·buffer·오류 규약은 다릅니다. Kernel 구현 선택이 모든 사용자 library보다 빠르다는 보장은 없습니다.',
      'socket(AF_ALG)→bind(sockaddr_alg)→key 설정→accept→operation 입력→결과 읽기를 지원 규약에 맞춥니다. Partial send/read·AEAD 인증 실패·descriptor 수명을 처리합니다.',
      'alg_bind의 address 길이·salg_type/name·flags와 algif_* 파일 operation을 읽으세요.',
      q('AF_ALG parent bind와 accept한 operation socket은 같은 상태 역할인가?','알고리즘 설정과 개별 작업 경계를 구분한다','accept는 항상 네트워크 원격 연결이다','AF_ALG는 원격 TCP 서버가 아닙니다. Parent의 algorithm 상태를 operation socket에 연결해 작업을 수행하는 규약입니다.'),
      q('AF_ALG AEAD read가 인증 실패를 반환해도 buffer를 정상 plaintext로 쓰는가?','실패를 처리하고 정상 output으로 사용하지 않는다','read를 호출했으면 언제나 인증 성공이다','암호 계산과 tag 검증의 완료를 확인해야 합니다. Kernel 경로라는 이유로 오류를 무시할 수 없습니다.'),
      details=[detail('Control 메시지','IV·암복호 방향·AAD 길이를 표현하는 ancillary data 규약이 있습니다. 임의 struct를 payload 앞에 붙이는 것과 다르며 각 algif의 지원을 확인합니다.'),detail('비용의 경계','사용자↔kernel 전환·buffer 전달·request 준비 비용이 추가됩니다. Hardware 가속이나 복사 경로와 입력 크기를 함께 측정해 선택합니다.')])

    topic('Crypto Engine·비동기 하드웨어 요청 큐','암호 알고리즘','crypto/crypto_engine.c','crypto_pump_requests',
      '암호 hardware가 한 번에 처리할 요청 수가 제한되면 대기·완료·backlog 수명을 공통화해야 합니다.',
      'Crypto engine은 async request queue에서 다음 작업을 고르고 hardware 준비·실행·완료를 driver operation에 연결합니다. cur_req·busy·idling·retry 지원 상태를 관리합니다. 제출 성공·backlog 통지·최종 completion은 서로 다른 경계입니다.',
      'Driver에서 engine 등록·전송·finalize·종료 규약을 따릅니다. Callback에 전달되는 status와 요청 buffer 수명을 맞추고 lock 보유 중 잠들 수 있는 provider 작업을 실행하지 않는 경로를 확인합니다.',
      'crypto_pump_requests의 queue_lock·cur_req·idling·kworker와 finalize_request를 읽으세요.',
      q('비동기 crypto 요청을 queue에 넣으면 buffer를 바로 해제해도 되는가?','최종 completion까지 유지해야 한다','제출 함수 반환이면 device 접근이 끝났다','Queue 대기와 hardware 실행이 남을 수 있습니다. 완료·취소를 보장한 뒤 mapping과 buffer를 정리합니다.'),
      q('backlog 통지와 최종 요청 completion은 같은가?','진행 상태와 최종 완료를 구분한다','모든 callback 호출은 최종 성공이다','Async Crypto API의 status 규약을 확인해야 합니다. 진행 통지 후에도 최종 callback이 올 수 있어 중복 해제를 피합니다.'),
      details=[detail('Lock 밖의 작업','Queue 상태를 보호하는 spinlock과 hardware 준비의 실행 문맥을 구분합니다. 긴 작업이나 잠들기 가능 작업을 lock 안에 무조건 넣지 않습니다.'),detail('Retry와 Idle','장치가 busy이면 요청을 다시 배치하거나 다음 worker를 기다릴 수 있습니다. Idle 전환과 새 요청 경쟁을 처리해야 작업이 영원히 queue에 남지 않습니다.')])

    topic('Cryptd·암호 작업을 Worker로','암호 알고리즘','crypto/cryptd.c','cryptd_enqueue_request',
      '동기 software 암호 작업을 비동기 요청 인터페이스에 연결할 때 worker·CPU queue·callback이 필요합니다.',
      'Cryptd는 CPU별 queue에 요청을 넣고 workqueue에서 실제 child algorithm을 호출한 뒤 callback합니다. Wrapper context와 request callback을 보관·복구하며 backlog 상태도 처리합니다. 비동기 wrapper가 암호 수학 자체를 변경하거나 hardware 가속을 자동 제공하는 것은 아닙니다.',
      'Crypto API의 cryptd wrapper 선택과 child 구현을 확인합니다. 요청·buffer·transform 수명을 completion까지 유지하고 실패·backlog 규약을 처리합니다. Software offload 비용과 병렬성을 실제로 측정합니다.',
      'cryptd_enqueue_request의 per-CPU queue·schedule_work와 cryptd_queue_worker 실제 정의를 읽으세요.',
      q('Cryptd가 AES를 worker에서 실행하면 AES ciphertext 수학이 바뀌는가?','실행 문맥을 바꾸며 같은 algorithm 계약을 따른다','worker마다 임의 cipher를 새로 만든다','Wrapper는 작업 실행과 완료 방식을 연결합니다. Child cipher의 key·IV·메시지 의미는 보존되어야 합니다.'),
      q('Cryptd queue에 넣은 요청 수명은 언제까지 유지해야 하는가?','worker 처리와 최종 callback이 끝날 때까지','enqueue 직후 무조건 해제','대기 중 요청·worker가 buffer를 참조할 수 있습니다. 비동기 수명과 wrapper transform의 참조를 함께 관리합니다.'),
      details=[detail('CPU별 Queue','alloc_percpu로 마련한 queue는 경쟁을 나누지만 CPU 이동·work 실행 위치 규약이 있습니다. Per-CPU라는 이름만으로 어떤 문맥에서도 고정 CPU가 보장되는 것은 아닙니다.'),detail('Callback 복구','Wrapper가 자기 완료 처리를 끼워 넣고 원래 caller callback과 data를 유지할 수 있습니다. 최종 완료의 주체와 status·수명 정리를 정확히 이어야 합니다.')])
