"""Classifier precedence and socket-parser bounds."""
def register(topic,q,detail):
    title='주소 문자 분류: 구분자 우선순위와 파서의 길이 문턱'
    topic(title,'네트워크','net/core/utils.c','xdigit2bin',
          '숫자를 읽는 상태 기계는 문자 값뿐 아니라 그 문자가 숫자·콜론·점·끝 중 무엇인지 알아야 합니다. 값과 종류를 한 정수의 서로 다른 비트에 담으면 허용 집합과 AND해서 다음 행동을 고를 수 있습니다.',
          'xdigit2bin은 지정 delim과 같은 문자 또는 NUL을 먼저 DELIM으로 반환합니다. 다음 콜론은 COLON_MASK,점은 DOT입니다. hex_to_bin 결과가0 이상이면 그 값과 XDIGIT을 합치고10 미만일 때 DIGIT도 더합니다. 나머지 문자는 delim=-1이면 DELIM,그 외에는 UNKNOWN입니다. 따라서 같은 문자라도 구분자 설정에 따라 의미가 달라집니다.',
          '문자 a는16진수 값10과 XDIGIT을 갖지만 DIGIT은 없어 IPv4 숫자로는 거절됩니다. 문자7은 두 숫자 분류를 모두 갖습니다. delim을 콜론으로 지정했다면 콜론 분기보다 앞의 DELIM 분기에 잡힙니다. IN6PTON_NULL은 입력 NUL 문자 분류가 아니라 시작·끝 상태에 쓰는 별도 비트이며 입력 NUL 자체는 DELIM입니다.',
          'inet4_pton은 strlen(src)>INET_ADDRSTRLEN이면 -EINVAL,inet6_pton은 INET6_ADDRSTRLEN 초과이면 -EINVAL입니다. 같으면 이 길이 검사 자체는 통과하되 실제 파서 성공이 여전히 필요합니다. inet_pton_with_scope의 지원하지 않는 family는 pr_err 후 초기값 -EINVAL을 반환합니다.',
          q(title+' · delim이 콜론일 때 콜론은 어떤 분류인가요?',
            '먼저 검사하는 DELIM입니다.','항상 COLON_MASK입니다.',
            '문자 자체 분기보다 지정 구분자 비교가 먼저이므로 조건 순서가 결과를 결정합니다.'),
          q(title+' · 문자열 길이 제한 통과가 올바른 주소의 증명인가요?',
            '아닙니다. 이후 실제 주소 파싱도 성공해야 합니다.','그렇습니다. 길이만 맞으면 숫자와 구분자는 무관합니다.',
            'wrapper의 길이 조기 거절과 in4/in6_pton의 문법·범위 판정은 별도의 단계입니다.'),
          details=[detail('분류 비트와 상태 비트의 역할',
                          'XDIGIT=0x00010000,DIGIT=0x00020000은 낮은 숫자 값과 분리됩니다. COLON_1·COLON_2·COLON_1_2는 한 콜론·두 번째 콜론·압축 가능성을 나타내는 상태에 사용합니다. state와 입력 분류가 겹치지 않으면 실패하므로 비트마스크는 단순 주소 값이 아니라 문법의 다음 선택지를 담습니다. 이 파일의 includes와 EXPORT_SYMBOL은 네트워크·문자열·바이트 순서 helper 및 외부 모듈 연결을 제공하며 자체 주소 처리 단계를 추가하지 않습니다.'),
                   detail('검토 범위',
                          'Linux v6.12 net/core/utils.c의 분류 상수·xdigit2bin·inet4_pton·inet6_pton·inet_pton_with_scope 경계를 원문에 대조했습니다. 전체 문자열 소비 여부는 앞선 주소 파싱 수업과 함께 읽어야 하며 실제 네트워크 실행 시험은 아닙니다.')])
