"""All software Hamming weight functions and multiplier/word branches."""
def register(topic, q, detail):
    def lesson(title, symbol, why, principle, use, reading, qa, cards):
        topic(title, '라이브러리·알고리즘', 'lib/hweight.c', symbol,
              why, principle, use, reading, *(q(*x) for x in qa),
              details=[detail(*x) for x in cards])

    lesson('Software Popcount32·병렬 작은 Counter 합치기', '__sw_hweight32',
        '한32bit 숫자의1bit 개수를 작은 필드별 합으로 계산하는 SWAR 산술 원리를 배웁니다.',
        'W-((w>>1)&0x55555555)는 각2bit 그룹의 set 개수를 만듭니다. 0x33333333 mask와 shift2는 두2bit counter를4bit counter로 합칩니다. Shift4와0x0f0f0f0f는 byte별 개수를 만듭니다. Fast multiplier 분기는0x01010101 곱의 높은 byte에서 전체 합을 얻습니다. 다른 분기는 shift8/16 합과0xff mask로 같은 개수를 구합니다.',
        '입력의 수치 bit 개수를 구할 때 사용하며 숫자 크기·최고 set 위치와 구분합니다. CONFIG_ARCH_HAS_FAST_MULTIPLIER는 선택 산술 구현을 바꿉니다. CPU 고유 popcount instruction과 이 software body의 선택 경로를 함께 확인합니다.',
        'Mask의 반복 bit 패턴과2→4→8bit counter, 곱셈과 shift 합 분기를 읽으세요.',
        [('0b1011의 Hamming weight는?', '3이다', '숫자값11이다', 'Set 위치가 세 개입니다. Popcount는 그 위치의 가중치를 더해 원래 수치11을 구하는 연산이 아닙니다.'),
         ("첫0x55555555 mask가 구분하는 단위는 ?", '서로 겹치지 않는2bit 그룹이다', '32bit 전체를 한 번에 대소 비교한다', 'Mask는 각2bit 그룹의 높은 bit를 shift한 뒤 낮은 자리에서 선택합니다. 빼기로 각 그룹의0..2 개수를 동시에 만듭니다.')],
        [('SWAR', 'SIMD Within A Register는 한 register의 작은 필드를 동시에 처리하는 기법입니다. 여기의 자료는 일반 정수 한 개이며 별도 vector register를 사용한다고 단정하지 않습니다.'),
         ('Unsigned 곱', 'Unsigned32bit 곱은 정해진 폭의 나머지 산술입니다. Byte별 부분합의 상한과 반복 상수를 이용하여 높은 byte에 전체 개수를 모읍니다. 임의 overflow를 무시하는 일반 합산 기법으로 확대하지 않습니다.')])

    lesson('Software Popcount8·16과 낮은 폭의 합', '__sw_hweight16',
        '같은 병렬 bit 개수 계산을8bit와16bit에 맞춰 줄이고 mask의 폭을 이해합니다.',
        'Hweight16은0x5555로2bit counter,0x3333으로4bit counter,0x0f0f로 byte counter를 구합니다. Shift8 합을0xff로 제한하여 반환합니다. Hweight8은0x55와0x33으로 같은 단계를 거친 뒤 shift4 합을0x0f로 제한합니다. 인자는 unsigned int지만 대상 폭은 각각 낮은16bit와8bit입니다.',
        "필요한 폭에 맞는 API를 선택합니다. 일반32bit 전체의 count가 필요하면8/16 variant로 대체하지 않습니다. Mask가 어느 bit를 유지하고 최종 개수가 어느 폭에 들어가는 지 작은 binary 예제로 검산합니다.",
        '두 함수의 mask 폭과 최종 shift, count mask를 비교하세요.',
        [('16bit 값0xffff의 popcount는?', '16이다', '65535이다', '16개의 bit가 모두1입니다. 반환값은 원본 수치65535가 아니라 set 개수16입니다.'),
         ('32bit 값0x100을 hweight8에 주면 대상 낮은8bit의 count는?', '0이다', '전체32bit의1을 반드시 센다', '이 variant의 대상은 낮은8bit입니다. Bit8은 그 폭 밖이므로32bit 전체 count와 구분합니다.')],
        [('최종 Mask', '8bit 집합의 최대 개수8은4bit count 필드에 들어갑니다. 16bit의 최대 개수16은 마지막0xff 범위에 들어갑니다. 데이터 폭과 개수를 저장하는 폭은 다릅니다.'),
         ('C 연산', '>>는 unsigned 수치를 오른쪽으로 이동하고 &는 mask가1인 위치만 남깁니다. 작은 counter를 합칠 때 이웃 그룹의 자료가 섞이지 않도록 하는 mask의 역할을 읽습니다.')])

    lesson('Software Popcount64·Word 폭과 분할 합', '__sw_hweight64',
        '64bit 자료를 native word 폭과 곱셈 비용에 맞춰 두 방식으로 세는 원리를 배웁니다.',
        'BITS_PER_LONG32 분기는 높은32bit와 낮은32bit를 각각 hweight32로 세어 더합니다. 64 분기는64bit 폭의0x5555/0x3333/0x0f 상수로 byte count를 만듭니다. Fast multiplier이면0x0101010101010101 곱을 shift56하여 합을 얻습니다. 다른 분기는 shift8/16/32로 합친 뒤0xff를 반환합니다.',
        '최대 결과64와 반환 unsigned long의 폭을 구분합니다. 두32bit 반쪽은 겹치지 않아 개수를 더할 수 있습니다. Host64에서 BITS_PER_LONG32 분기를 선택한 시험은 분할 산술 검증이며 native32bit ABI 시험과 다르게 표시합니다.',
        'W>>32 cast와 두 count 합,64bit 반복 상수와 최종 분기를 읽으세요.',
        [('64bit 입력의 높은 반쪽에3개, 낮은 반쪽에5개 set이면?', '전체 count8이다', '반쪽 중 더 큰 count5만 반환한다', '32bit 분기는 분리된 두 영역의 개수를 더합니다. 겹치는 원소가 없으므로3+5입니다.'),
         ('Fast multiplier가 꺼진64bit 분기는?', 'Shift8/16/32 합산으로 같은 count를 구한다', '반드시 실패 오류를 반환한다', '원본은 곱셈 없는 대체 산술을 제공합니다. Configuration은 구현을 선택하며 개수 계산의 의미를 바꾸지 않습니다.')],
        [('선택 분기', '32bit long 분기는 hweight32의 fast/nonfast 선택에도 연결됩니다. 전체 조합을 확인할 때 하위 함수의 CONFIG도 포함합니다.'),
         ('동시성 범위', '이 함수는 받은 수치 하나의 bit 개수를 계산합니다. 공유 bitmap의 여러 word를 읽는 snapshot의 일관성이나 atomic update까지 제공하는 함수는 아닙니다.')])
