"""Whole-file OF modalias construction and module request ownership."""
ROWS = [dict(
    path='drivers/of/module.c', title='OF 모듈 별칭: 두 번의 길이 계산과 제한된 버퍼 직렬화',
    intro='of_modalias와 of_request_module의 전체 분기·문자열 처리·메모리 수명을 분석합니다.',
    principle='필요한 총 길이와 실제 기록한 길이를 따로 관리해야 잘린 출력에서도 크기를 계산할 수 있습니다.',
    use='문자열 직렬화,버퍼 경계,두 단계 할당과 오류 전파를 학습합니다.',
    area='문자열 알고리즘 · 모듈 로딩 · 메모리 관리 · 장치 트리',
    sections=[
        ('파일과 입력 검사', 'GPL-2.0 파일은 OF,module,slab,string 헤더를 포함합니다. of_modalias는 node,문자 버퍼,ssize_t 길이를 받습니다. len<0 또는 len>0이면서 str=NULL이면 -EINVAL입니다. str=NULL,len=0은 필요한 길이를 질의하는 경로로 허용합니다. 이 함수에는 np=NULL 검사가 없으며 공개 request helper가 별도로 검사합니다.'),
        ('이름과 타입 접두부', '첫 snprintf는 of:N 뒤 %pOFn 노드 이름과 문자 T,device type을 기록합니다. T를 format 문자열에서 pointer 확장 바로 뒤 알파벳으로 붙이지 않고 %c 인수로 전달하는 이유는 %p 확장이 뒤의 영숫자를 소비하기 때문이라는 주석이 있습니다. compatible 데이터와 이름·타입 접두부는 서로 다른 단계입니다.'),
        ('총 길이와 실제 이동', 'snprintf 결과 csize를 tsize에 저장합니다. csize>=len이면 실제 포인터 이동량은 len>0일 때 len-1,아니면 0으로 제한합니다. 이후 남은 len과 str을 갱신합니다. tsize는 잘리지 않았을 때 필요한 문자 수를 유지하며 실제 버퍼에 쓴 길이와 같지 않을 수 있습니다. 종료 NUL을 위한 공간을 남기는 경계 처리입니다.'),
        ('Compatible 반복과 부분 생략', 'of_property_for_each_string으로 compatible 항목을 순회합니다. 각 항목의 기여는 strlen(compat)+1로 앞의 C 한 글자를 포함하며 tsize에는 공간 부족 여부와 무관하게 더합니다. csize>=남은 len이면 해당 항목을 쓰지 않고 continue합니다. 전체 반복을 break하지 않으므로 뒤의 더 짧은 항목은 남은 공간에 들어갈 수 있습니다. 출력은 단순한 연속 접두부 잘림이라고만 설명할 수 없습니다.'),
        ('공백 치환', '공간이 충분한 항목은 snprintf("C%s")로 기록하고 strchr로 공백을 찾아 밑줄로 바꿉니다. 치환 후 포인터를 증가시켜 같은 문자를 반복 검색하지 않습니다. 이 루프는 방금 기록한 compatible 조각부터 수행하며 이름·타입 접두부 전체를 다시 정규화하는 코드가 아닙니다. 탭이나 모든 공백 문자 종류가 아니라 문자 공백 하나를 대상으로 합니다.'),
        ('반환값과 복잡도', '각 성공 기록 뒤 csize만큼 남은 길이를 줄이고 str을 전진합니다. 반환 tsize는 최종 NUL을 제외한 전체 필요 문자 수입니다. compatible 문자열 길이 측정과 출력·공백 검색을 하므로 입력 문자 총량에 비례하는 순회이며 정렬이나 hash table을 사용하지 않습니다. 버퍼 부족을 별도 errno로 반환하지 않고 필요 길이로 표현합니다.'),
        ('두 번 호출하는 요청 helper', 'of_request_module은 np=NULL이면 -ENODEV입니다. 먼저 of_modalias(np,NULL,0)로 길이를 질의하고 음수면 그대로 반환합니다. NUL용으로 size를 1 늘리고 GFP_KERNEL kmalloc에 실패하면 -ENOMEM입니다. 그 뒤 같은 node로 실제 버퍼를 채우고 str[size-1]을 NUL로 설정합니다.'),
        ('요청과 정리의 범위', '두 번째 of_modalias의 반환값은 검사하지 않습니다. 첫 길이 질의와 두 번째 출력 사이를 잠금이나 node snapshot으로 묶는 코드도 이 파일에는 없으므로 외부 변경까지 원자적이라고 주장하지 않습니다. request_module(str)의 결과를 저장하고 버퍼를 kfree한 뒤 결과를 반환합니다. 최종 NUL 보장은 내용이 모두 담겼다는 증명과 다릅니다.'),
        ('전체 검토', '두 함수,입력 오류,초기 접두부,compatible 반복·생략·치환,두 단계 할당과 반환 경로를 모두 대조했습니다. GPL export는 of_request_module에 있습니다. 실제 모듈을 요청하거나 로드하지 않았으며 helper 반환값만으로 특정 driver의 probe 성공까지 보장한다고 설명하지 않습니다.')
    ], questions=[
        ('str=NULL,len=0 호출의 목적은?', '전체 별칭에 필요한 길이를 계산하기 위해서다', '반드시 -EINVAL을 얻기 위해서다', '검사는 양수 길이의 NULL 버퍼와 음수 길이를 거릅니다. 0 길이 질의는 요청 helper에서도 사용합니다.'),
        ('compatible 항목이 남은 버퍼에 안 들어가면 반복을 끝내는가?', '아니다. 그 항목만 건너뛰고 다음 항목을 확인한다', '그렇다. 즉시 break한다', '코드는 continue입니다. 뒤의 짧은 항목이 기록될 수 있어 단순한 prefix truncation과 다릅니다.'),
        ('tsize에 종료 NUL이 포함되는가?', '아니다. 호출자가 1바이트를 추가한다', '그렇다. request helper가 1을 빼서 할당한다', 'size++ 주석이 trailing NUL을 위한 추가 공간이라고 명시합니다.'),
        ('공백 치환이 적용되는 범위는?', '새로 기록한 compatible 조각의 문자 공백', '항상 전체 별칭의 모든 Unicode 공백', 'strchr가 찾는 것은 ASCII 공백 문자이며 시작 포인터는 현재 compatible 출력 위치입니다.'),
        ('두 번째 of_modalias 결과를 of_request_module이 검사하는가?', '아니다. 반환값은 사용하지 않는다', '그렇다. 필요 길이를 다시 확인해 재할당한다', '재할당 루프는 없습니다. 마지막 NUL 설정과 완전한 내용 보장은 구분해야 합니다.'),
        ('request_module 호출 뒤 임시 문자열은?', '반환값을 저장한 후 kfree하고 그 값을 반환한다', '성공일 때만 해제하고 실패 시 항상 남긴다', '호출 결과에 따른 분기 없이 kfree가 실행됩니다. 요청 결과와 버퍼 소유권 정리는 분리됩니다.')
    ]
)]
