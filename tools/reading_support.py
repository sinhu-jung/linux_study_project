"""Vocabulary support and transparent corpus-wide editorial triage.

Length/word matches are review signals, NOT a Korean reading-age measurement.
Never rewrite source code or infer file behavior from its filename.
"""
import re
from collections import Counter
from functools import lru_cache

# Separate aliases with |. English aliases match whole identifiers only.
VOCABULARY = [
 ('Linux', '소스가 공개된 커널의 이름입니다. 이 커널과 여러 도구를 묶은 운영체제를 가리킬 때도 씁니다.'),
 ('errno', '일부 C 라이브러리 함수가 실패 이유를 알려 줄 때 사용하는 오류 번호입니다. 커널 함수의 음수 오류 반환값과 구별하세요.'),
 ('ERR_PTR', 'Linux 커널에서 오류 번호를 포인터 형태로 나타내는 매크로입니다. 정상 메모리 주소처럼 사용하면 안 됩니다.'),
 ('size|크기', '자료가 차지하는 양입니다. 바이트 수인지 원소 수인지 확인해야 합니다.'),
 ('Kconfig', 'Linux를 만들 때 선택할 수 있는 기능과 그 선택 조건을 적는 설정 파일 체계입니다.'),
 ('ASan', '메모리 범위 밖 접근이나 사용이 끝난 공간의 접근 같은 오류를 찾는 검사 도구입니다.'),
 ('UBSan', 'C 등에서 결과를 보장하지 않는 잘못된 연산 일부를 찾아 알리는 검사 도구입니다.'),
 ('sparse', 'Linux 코드의 형식과 주소 공간 표시 같은 규칙을 검사하는 도구입니다. 일반 문장에서는 드문드문하다는 뜻도 있습니다.'),
 ('AND', '두 비트가 모두 1일 때만 결과가 1인 연산입니다. 조건식에서는 두 조건을 모두 만족하는지 묻습니다.'),
 ('Copy-on-Write', '처음에는 자료를 함께 쓰고, 고쳐 쓸 필요가 생기면 따로 복사하는 방식입니다.'),
 ('GFP', 'Linux에서 메모리를 빌릴 때 기다려도 되는지 같은 조건을 나타내는 플래그 계열의 이름입니다.'),
 ('FDT|DTB', '장치 연결과 설정 정보를 정해진 이진 형식으로 담은 디바이스 트리 자료와 관련된 이름입니다.'),
 ('guard', '중복 포함이나 잘못된 접근을 막는 보호 조건 등을 뜻합니다. C 매크로 이름일 때는 실제 정의를 확인하세요.'),
 ('wrapper', '다른 함수를 감싸 호출 방법을 바꾸거나 준비·정리 작업을 더하는 함수입니다.'),
 ('per-CPU', 'CPU마다 별도로 마련한다는 뜻입니다. 함께 쓰는 값인지 CPU별 값인지 구별해야 합니다.'),
 ('ASCII', '영문자와 숫자 등 문자에 번호를 붙이는 문자 표현 규칙입니다.'),
 ('UTF-8', '한글을 포함한 여러 문자를 바이트로 나타내는 규칙입니다. 한 글자가 여러 바이트일 수 있습니다.'),
 ('SMP', '여러 CPU가 메모리를 함께 쓰며 일하는 컴퓨터 구성입니다.'),
 ('acquire|release', '메모리 순서 문맥에서 다른 읽기·쓰기와의 관찰 순서를 맞추는 데 쓰는 규칙입니다. release는 일반 문맥에서 자원 해제도 뜻합니다.'),
 ('runtime', '프로그램이 실제로 실행되는 동안이라는 뜻입니다. 코드를 번역하는 동안과 구별합니다.'),
 ('caller', '현재 함수를 부른 쪽 코드입니다. 결과를 받아 다음 일을 합니다.'),
 ('LKMM', 'Linux 커널의 메모리 접근이 다른 CPU에 어떤 순서로 보일 수 있는지 설명하는 규칙 모델입니다.'),
 ('task', '작업이라는 뜻입니다. 커널에서는 스케줄러가 다루는 실행 단위를 가리키는 문맥도 있습니다.'),
 ('compiler', '소스 코드를 번역하는 프로그램인 컴파일러입니다.'),
 ('allocator', '사용할 메모리 등의 자원을 골라 내주는 관리 코드입니다.'),
 ('data', '프로그램이 읽고 처리하는 자료입니다.'),
 ('property', '장치나 대상에 붙어 있는 속성 정보입니다. 이름과 값으로 나타내기도 합니다.'),
 ('ABI', '번역된 프로그램이나 부품끼리 함수 호출·자료 배치 등을 맞추는 약속입니다.'),
 ('count', '개수나 횟수를 세는 값입니다. 바이트 크기와 같은 단위인지 확인하세요.'),
 ('커널|kernel', '컴퓨터의 중심 관리자. 여러 프로그램이 계산 장치와 메모리, 기기를 나누어 쓰게 합니다.'),
 ('운영체제|OS', '프로그램을 실행하고 컴퓨터의 자원을 관리하는 기본 소프트웨어입니다. Linux가 한 예입니다.'),
 ('오픈소스|open source', '소스 코드를 공개하고 정해진 이용 규칙에 따라 살펴보거나 고쳐 쓸 수 있게 한 소프트웨어입니다.'),
 ('소스|source', '프로그램이 할 일을 사람이 읽을 수 있는 언어로 적은 원본 코드입니다.'),
 ('CPU', '명령을 읽고 계산하는 컴퓨터 장치입니다.'),
 ('메모리|memory', '프로그램이 일하는 동안 값과 명령을 놓는 공간입니다. 보통 전원을 끄면 내용이 사라지는 RAM을 말합니다.'),
 ('주소|address', '메모리나 장치에서 어느 위치인지 가리키는 번호입니다. 인터넷 주소와 메모리 주소는 쓰이는 곳이 다릅니다.'),
 ('프로세스|process', '실행 중인 프로그램 하나입니다. 실행 번호와 작업 상태를 가집니다.'),
 ('스레드|thread', '프로세스 안에서 명령을 실행해 나가는 흐름입니다. 같은 프로세스의 다른 스레드와 메모리를 함께 쓸 수 있습니다.'),
 ('셸|shell', '사용자가 적은 명령을 읽고 프로그램을 실행하는 도구입니다.'),
 ('시스템 호출|syscall', '프로그램이 파일 열기 같은 일을 커널에게 부탁하는 정해진 방법입니다.'),
 ('함수|function', '이름을 붙인 작업 묶음입니다. 필요한 값을 받아 일을 하고 결과를 돌려줄 수 있습니다.'),
 ('호출|call', '함수 등에게 정해진 일을 해 달라고 실행을 요청하는 것입니다.'),
 ('인수|argument', '함수를 부를 때 건네는 값입니다. 더하기 함수에 건네는 두 숫자를 생각해 보세요.'),
 ('반환|return', '함수가 일을 마치고 부른 곳으로 돌아가거나 결과를 돌려주는 것입니다.'),
 ('변수|variable', '값을 기억하고 나중에 사용하기 위해 이름을 붙인 저장 장소입니다.'),
 ('타입|type|형식', '숫자, 문자처럼 어떤 종류의 값을 어떻게 담는지 정한 규칙입니다.'),
 ('포인터|pointer', '다른 값이 놓인 위치를 담는 값입니다. 위치를 안다고 언제나 그곳을 사용해도 되는 것은 아닙니다.'),
 ('역참조|dereference', '포인터가 가리키는 위치에서 실제 값을 읽거나 쓰는 일입니다.'),
 ('NULL', '포인터가 유효한 대상을 가리키지 않는다는 것을 나타내는 값입니다.'),
 ('수명|lifetime', '어떤 값이나 공간을 유효하게 사용할 수 있는 기간입니다.'),
 ('할당|allocation|allocate', '작업에 쓸 메모리 같은 자원을 확보하는 일입니다. 필요한 만큼 빌리는 것으로 생각해 보세요.'),
 ('해제|free|release', '쓰던 자원을 돌려주거나 잡고 있던 연결을 놓는 일입니다. 무엇을 해제하는지 함께 읽어야 합니다.'),
 ('누수|leak', '다 쓴 자원을 돌려주지 않아 사용할 수 있는 자원이 줄어드는 문제입니다.'),
 ('참조|reference', '어떤 대상을 가리키거나 사용하기 위한 연결입니다.'),
 ('참조 수|refcount', '대상을 사용 중인 연결의 개수를 세는 값입니다. 보통 마지막 사용자가 놓을 때 정리합니다.'),
 ('배열|array', '같은 종류의 칸을 연속으로 놓고 번호로 찾는 자료구조입니다.'),
 ('인덱스|index', '배열에서는 칸 번호입니다. 데이터베이스에서는 빨리 찾기 위한 별도 정보를 뜻합니다. 문맥을 확인하세요.'),
 ('연결 리스트|linked list', '각 자료가 다음 자료의 위치를 기억하며 이어진 구조입니다.'),
 ('노드|node', '리스트, 트리, 그래프를 이루는 한 항목이나 점입니다.'),
 ('구조체|struct', '이름과 나이처럼 서로 관련된 여러 값을 하나로 묶은 자료입니다.'),
 ('필드|field', '구조체나 기록 안에 있는 개별 항목입니다.'),
 ('스택|stack', '마지막에 넣은 것을 먼저 꺼내는 구조입니다. 함수의 작업 기록을 보관하는 공간에도 쓰입니다.'),
 ('큐|queue', '먼저 넣은 것을 먼저 꺼내는 줄 같은 구조입니다. 특별한 우선순위 큐는 별도의 순서를 씁니다.'),
 ('버퍼|buffer', '자료를 보내거나 처리하기 전에 잠깐 담아 두는 공간입니다.'),
 ('원형|ring|circular', '마지막 다음에 처음으로 돌아가며 자리를 쓰는 방식입니다.'),
 ('자료구조|data structure', '자료를 어디에 놓고 어떻게 연결해 찾을지 정한 방식입니다.'),
 ('알고리즘|algorithm', '문제를 해결하기 위해 일을 처리하는 순서와 규칙입니다.'),
 ('복잡도|complexity', '자료 수가 늘 때 필요한 시간이나 공간이 어떻게 늘어나는지 나타내는 기준입니다.'),
 ('불변식|invariant', '작업의 정해진 지점마다 계속 지켜야 하는 약속입니다.'),
 ('경계|boundary', '규칙이 달라지는 끝부분입니다. 배열의 첫 칸과 마지막 칸, 빈 상태 등을 확인합니다.'),
 ('해시|hash', '자료에서 정해진 규칙으로 만든 값입니다. 다른 자료가 같은 값을 가질 수도 있습니다.'),
 ('충돌|collision', '서로 다른 자료가 같은 해시값이나 같은 저장 위치를 받는 경우입니다.'),
 ('버킷|bucket', '해시 테이블 등에서 자료를 모아 두는 한 칸 또는 묶음입니다.'),
 ('트리|tree', '자료를 가지처럼 연결한 구조입니다. 보통 시작점인 루트에서 자식 항목들로 내려갑니다.'),
 ('루트|root', '트리의 맨 위 시작점입니다. Linux 사용자 문맥에서는 가장 강한 관리 권한의 계정을 뜻하기도 합니다.'),
 ('힙|heap', '자료구조에서는 최소값이나 최대값을 위에 두는 구조입니다. 메모리 문맥에서는 동적으로 빌리는 공간을 뜻하기도 합니다.'),
 ('정렬|sort', '자료를 크기나 이름처럼 정한 기준의 순서로 놓는 일입니다.'),
 ('정렬|alignment', '메모리 정렬 문맥에서는 주소를 4의 배수처럼 정해진 단위에 맞추는 뜻입니다. 값의 순서 정렬과 구별하세요.'),
 ('탐색|search', '조건에 맞는 자료를 찾아보는 일입니다.'),
 ('BFS', '가까운 단계에 있는 점부터 차례로 넓게 살펴보는 그래프 탐색입니다.'),
 ('DFS', '한 길을 깊게 따라가고 돌아와서 다른 길을 보는 그래프 탐색입니다.'),
 ('재귀|recursion', '함수가 더 작은 문제를 풀기 위해 자기 자신을 다시 부르는 방식입니다. 멈추는 조건이 필요합니다.'),
 ('비트|bit', '0 또는 1 하나를 담는 가장 작은 정보 단위입니다.'),
 ('바이트|byte', '보통 8비트를 묶은 단위입니다. 이 교재의 Linux에서는 8비트입니다.'),
 ('unsigned', '음수 없이 0과 양수를 나타내는 정수 형식입니다.'),
 ('signed', '음수도 나타낼 수 있는 정수 형식입니다.'),
 ('오버플로|overflow', '계산 결과가 그 숫자 형식으로 담을 수 있는 범위를 넘는 일입니다. 형식에 따라 처리 규칙이 다릅니다.'),
 ('XOR', '두 비트가 다르면 1, 같으면 0인 연산입니다. 같은 값을 두 번 XOR하면 원래 값으로 돌아옵니다.'),
 ('시프트|shift', '비트의 자리를 왼쪽이나 오른쪽으로 옮기는 연산입니다. 옮길 수 있는 범위와 형식 규칙을 지켜야 합니다.'),
 ('마스크|mask', '특정 비트만 고르거나 바꾸려고 사용하는 비트 무늬입니다.'),
 ('리틀 엔디언|little-endian', '여러 바이트로 된 수에서 작은 자리 쪽 바이트를 낮은 주소에 먼저 저장하는 규칙입니다.'),
 ('빅 엔디언|big-endian', '여러 바이트로 된 수에서 큰 자리 쪽 바이트를 낮은 주소에 먼저 저장하는 규칙입니다.'),
 ('오프셋|offset', '기준 위치에서 얼마나 떨어졌는지 나타내는 값입니다. 바이트 수인지 칸 수인지 단위를 확인하세요.'),
 ('길이|length', '자료가 얼마나 많은지 나타내는 수입니다. 글자 수와 바이트 수는 다를 수 있습니다.'),
 ('플래그|flag', '켜짐/꺼짐처럼 상태나 선택 사항을 표시하는 값입니다.'),
 ('컴파일|compile', '소스 코드를 컴퓨터가 실행할 수 있는 쪽으로 번역하는 과정입니다.'),
 ('링크|link', '프로그램을 만들 때는 번역한 코드들을 연결하는 일입니다. 파일 이름 문맥에서는 파일을 가리키는 연결을 뜻합니다.'),
 ('헤더|header', 'C에서는 공통 선언 등을 담은 파일입니다. 통신에서는 자료 앞에 붙이는 길이 같은 안내 정보를 뜻합니다.'),
 ('선언|declaration', '함수나 변수의 이름과 종류가 무엇인지 알려 주는 코드입니다.'),
 ('정의|definition', '함수의 실제 작업 내용을 쓰거나 대상을 실제로 마련하는 코드입니다.'),
 ('매크로|macro', '코드를 번역하기 전에 이름을 정해진 코드 조각으로 바꾸는 규칙입니다. 함수와 평가 방식이 다를 수 있습니다.'),
 ('전처리|preprocess', '본격적으로 번역하기 전에 포함 파일이나 매크로, 설정 조건을 처리하는 단계입니다.'),
 ('include', 'C 전처리에서는 다른 파일의 내용을 가져오는 지시입니다.'),
 ('설정|config|configuration', '어떤 기능을 켜고 끌지, 어떤 방식으로 사용할지 정한 선택입니다.'),
 ('Makefile', '어떤 파일을 어떤 순서와 명령으로 빌드할지 적은 파일입니다.'),
 ('빌드|build', '소스 파일을 번역하고 연결해 실행 파일이나 필요한 결과물을 만드는 과정입니다.'),
 ('의존성|dependency', '어떤 일을 하려면 먼저 다른 자료나 기능이 있어야 하는 관계입니다.'),
 ('API', '다른 코드가 어떤 기능을 어떻게 요청할지 정한 사용 약속입니다.'),
 ('콜백|callback', '나중에 정해진 일이 생겼을 때 불러 달라고 건네는 함수입니다.'),
 ('helper', '다른 함수가 일을 처리하도록 돕는 보조 함수라는 뜻으로 자주 씁니다.'),
 ('캐시|cache', '다음에 빨리 쓰려고 값이나 자료를 잠시 보관하는 공간입니다. 원본이 바뀌었는지 확인할 필요가 있습니다.'),
 ('페이지|page', '메모리를 일정한 크기로 나눈 조각입니다. 웹 페이지와는 다른 뜻입니다.'),
 ('TLB', '가상 주소와 실제 메모리 위치의 연결을 빠르게 찾도록 기억하는 작은 저장소입니다.'),
 ('가상|virtual', '프로그램에 보이는 모습과 실제 장치의 배치를 구분해서 제공한다는 뜻입니다.'),
 ('물리|physical', '주소 문맥에서는 실제 메모리나 장치 쪽 위치를 말합니다.'),
 ('매핑|mapping', '한 주소나 번호를 다른 위치와 연결하는 대응 관계입니다.'),
 ('잠금|lock|mutex', '여럿이 함께 쓰는 자료를 규칙에 맞게 다루도록 접근 순서를 조절하는 장치입니다.'),
 ('스핀락|spinlock', '잠금을 얻을 때까지 잠들지 않고 상태를 확인하며 기다리는 방식의 잠금입니다.'),
 ('원자|atomic', '정해진 연산이 다른 참여자에게 중간에 쪼개져 보이지 않도록 다뤄지는 성질입니다. 모든 주변 작업까지 자동으로 안전해지는 것은 아닙니다.'),
 ('동기화|synchronization', '여러 작업이 함께 쓰는 자료와 실행 순서에 관한 약속을 맞추는 일입니다.'),
 ('동시성|concurrency', '여러 작업의 진행이 겹치는 상황입니다. 실제 같은 순간에 실행되는지와는 구별합니다.'),
 ('교착|deadlock', '서로 상대가 가진 자원을 기다려 더 진행하지 못하는 상태입니다.'),
 ('경쟁|race', '여러 작업이 끼어드는 순서에 따라 결과가 달라질 수 있는 상황입니다.'),
 ('RCU', '읽는 작업이 진행되는 동안 옛 자료를 바로 없애지 않고, 안전한 때까지 기다려 정리하는 동기화 방식입니다.'),
 ('배리어|barrier', '메모리 문맥에서는 읽기와 쓰기의 관찰 순서에 필요한 제약을 주는 장치입니다. 모든 일을 멈추는 잠금과는 다릅니다.'),
 ('인터럽트|interrupt|IRQ', '장치 등이 처리할 일이 생겼음을 CPU에 알리는 신호나 그 처리와 관련된 개념입니다.'),
 ('스케줄|schedule|scheduler', '여러 작업 중 누가 언제 계산할 차례인지 정하는 일 또는 담당 부분입니다.'),
 ('드라이버|driver', '운영체제가 특정 장치를 다룰 수 있도록 연결해 주는 코드입니다.'),
 ('장치|device', '디스크, 키보드, 네트워크 카드처럼 컴퓨터에 연결된 기능 부품입니다.'),
 ('레지스터|register', 'CPU나 장치가 값이나 상태를 보관하는 작은 저장 장소입니다. 어느 장치의 것인지 문맥을 보세요.'),
 ('PCI|PCIe', '컴퓨터와 확장 장치를 연결하는 규격 계열입니다. 장치 찾기와 주소 배정 등의 규칙이 있습니다.'),
 ('DMA', '장치가 CPU 대신 메모리와 자료를 주고받는 방식입니다. 주소와 사용 중인 공간의 관리가 필요합니다.'),
 ('IOMMU', '장치가 쓰는 주소를 실제 메모리 주소와 연결하고 접근 범위를 관리하는 하드웨어 기능입니다.'),
 ('MMIO', '메모리 주소처럼 보이는 위치를 읽고 써서 장치와 통신하는 방식입니다. 보통 메모리와 접근 규칙이 다를 수 있습니다.'),
 ('DT|device tree|디바이스 트리', '하드웨어에 어떤 장치가 있고 어떻게 연결됐는지 나타내는 자료 구조입니다.'),
 ('inode', '파일의 종류, 권한, 데이터 위치 같은 정보를 담는 파일 시스템의 관리 항목입니다.'),
 ('디렉터리|directory', '파일 이름들을 모아 다른 파일로 연결하는 폴더입니다.'),
 ('파일 디스크립터|fd', '프로세스가 열린 파일 등의 연결을 구별하는 데 사용하는 작은 정수 번호입니다.'),
 ('권한|permission', '누가 읽기, 쓰기, 실행 같은 일을 해도 되는지 정한 허락입니다.'),
 ('읽기|read', '자료를 가져와 확인하는 일입니다. read 함수의 반환값은 실제로 읽은 양이나 오류를 알려 줍니다.'),
 ('쓰기|write', '자료를 기록하도록 보내는 일입니다. 요청한 양보다 적게 처리되거나 실패할 수도 있습니다.'),
 ('경로|path', '파일 문맥에서는 위치를 적는 이름의 순서입니다. 코드에서는 실행이 지나가는 분기들의 흐름을 뜻하기도 합니다.'),
 ('분기|branch', '조건에 따라 서로 다른 일을 하도록 갈라지는 지점입니다.'),
 ('TCP', '순서 있는 바이트 흐름을 주고받는 통신 규칙입니다. 메시지의 끝은 응용 프로그램이 따로 정합니다.'),
 ('UDP', '묶음 단위로 자료를 보내는 통신 규칙입니다. 도착이나 순서 유지를 스스로 보장하지는 않습니다.'),
 ('패킷|packet', '통신을 위해 나눈 자료 묶음입니다.'),
 ('페이로드|payload', '안내 정보 등을 제외하고 실제 전달하려는 내용입니다.'),
 ('프로토콜|protocol', '자료를 어떤 형식과 순서로 주고받을지 정한 약속입니다.'),
 ('소켓|socket', '프로그램이 통신할 때 사용하는 연결 끝점입니다.'),
 ('타임아웃|timeout', '정해 둔 시간 안에 필요한 일이 끝나거나 답이 오지 않은 상태입니다.'),
 ('멱등|idempotent', '같은 요청을 여러 번 해도 한 번 했을 때와 같은 효과가 나도록 하는 성질입니다.'),
 ('트랜잭션|transaction', '여러 동작을 하나의 논리적인 작업으로 묶어 다루는 방식입니다.'),
 ('정수 승격', 'C가 계산 전에 작은 정수 형식을 int 등으로 바꾸는 규칙입니다. 저장하는 형식과 계산하는 형식이 다를 수 있습니다.'),
 ('단락 평가', '앞의 조건만으로 답을 알면 뒤의 조건은 계산하지 않는 방식입니다. C의 &&와 ||에서 볼 수 있습니다.'),
 ('부작용|side effect', '계산하면서 변수 값을 바꾸는 등 주변 상태도 바꾸는 일입니다. 꼭 나쁜 일이라는 뜻은 아닙니다.'),
 ('정의되지 않은 동작|undefined behavior', '언어가 결과를 보장하지 않는 잘못된 사용입니다. 우연히 잘 실행된 것처럼 보여도 안전하다고 볼 수 없습니다.'),
 ('암호|cipher|encryption', '정해진 키 없이는 내용을 알아보기 어렵게 자료를 바꾸는 기술입니다.'),
 ('키|key', '자료 찾기에서는 이름표 같은 식별 값입니다. 암호에서는 암호 연산에 사용하는 비밀 값 등을 뜻합니다.'),
 ('IV', '암호 연산을 시작할 때 사용하는 초기값입니다. 방식마다 재사용이나 무작위성에 관한 규칙이 다릅니다.'),
 ('counter|카운터', '횟수나 현재 순서를 세는 값입니다.'),
 ('block|블록', '한꺼번에 처리하는 일정한 크기의 자료 묶음입니다. 크기는 사용하는 규칙에 따라 다릅니다.'),
 ('CRC', '자료가 잘못 바뀌었는지 확인하려고 계산하는 검사값입니다. 공격자가 고친 자료까지 막는 암호 인증 수단은 아닙니다.'),
 ('체크섬|checksum', '자료에서 계산한 검사값입니다. 확인할 수 있는 오류 종류와 한계는 계산 방법에 따라 다릅니다.'),
 ('인증|authentication', '사람의 신원이나 메시지가 정해진 발신자의 것인지 확인하는 일입니다. 허락 범위 확인과는 구별합니다.'),
 ('메타데이터|metadata', '자료 자체에 대한 설명 정보입니다. 길이, 종류, 권한 등이 예입니다.'),
 ('인터페이스|interface', '두 부분이 어떻게 연결되고 요청을 주고받는지 정한 사용 방법입니다.'),
 ('fallback', '주된 방법을 쓸 수 없을 때 사용하는 대체 방법입니다. 실제로 대체 코드가 있는지는 확인해야 합니다.'),
 ('stub', '기능의 연결 자리를 마련한 작은 대체 코드입니다. 실제로 무엇을 하는지는 본문을 확인해야 합니다.'),
 ('초기화|initialization', '처음 사용하기 전에 값과 상태를 정해 놓는 일입니다.'),
 ('검증|validation', '정한 조건을 만족하는지 확인하는 일입니다. 모든 상황의 정확성을 자동으로 보장하는 말은 아닙니다.'),
]


def matcher(aliases):
    return re.compile('|'.join(
        r'(?<![A-Za-z0-9_])' + re.escape(a) + r'(?![A-Za-z0-9_])'
        if a.isascii() else re.escape(a) for a in aliases.split('|')), re.I)


PATTERNS = [matcher(a) for a, _ in VOCABULARY]
ALIASES = [a.lower().split('|') for a, _ in VOCABULARY]


@lru_cache(maxsize=None)
def known_token(token):
    return any(p.fullmatch(token) for p in PATTERNS)
FIELDS = ('title', 'intro', 'guide', 'concepts', 'deep_dive', 'reading_support', 'experiment', 'practice', 'questions', 'beginner')
SKIP = {'code', 'command', 'diagram', 'original_explanation', 'original_prompt', 'original_options', 'fingerprint', 'answer', 'review'}


def prose(value, path=''):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from prose(child, f'{path}[{i}]')
    elif isinstance(value, dict):
        for key, child in value.items():
            if key not in SKIP:
                yield from prose(child, f'{path}.{key}')


def support(lessons):
    audit = []
    unknown = Counter()
    glossary = [{'term': a.split('|')[0], 'aliases': a.split('|'), 'meaning': b} for a, b in VOCABULARY]
    for lesson in lessons:
        texts = [(p, t) for key in FIELDS for p, t in prose(lesson.get(key), key)]
        joined = '\n'.join(t for _, t in texts)
        lower = joined.lower()
        # Cheap substring filtering avoids scanning long lessons with every regex.
        terms = [i for i, pattern in enumerate(PATTERNS)
                 if any(a in lower for a in ALIASES[i]) and pattern.search(joined)]
        long_sentences = []
        for path, paragraph in texts:
            for sentence in re.split(r'(?<=[.!?。])\s+|\n', paragraph):
                if len(sentence) > 100:
                    long_sentences.append({'field': path, 'characters': len(sentence), 'text': sentence})
        tokens = set(re.findall(r'\b[A-Za-z][A-Za-z_0-9-]{2,}\b', joined))
        unmatched = sorted(t for t in tokens if not known_token(t))
        unknown.update(unmatched)
        # These can be exact source identifiers, not necessarily missing vocabulary.
        lesson['reading_aid'] = {'terms': terms, 'manual_rewrite': bool(lesson.get('beginner'))}
        audit.append({'id': lesson['id'], 'question_count': len(lesson['questions']),
                      'rewritten_introduction_and_answers': bool(lesson.get('beginner')),
                      'child_comprehension_tested': False,
                      'matched_glossary_entries': len(terms), 'long_sentences': long_sentences,
                      'unclassified_english_or_identifiers': unmatched})
    return glossary, {
        'scope': 'Every currently authored lesson and question; source code excluded from prose length checks.',
        'method': 'Editorial triage: sentences over 100 characters and vocabulary matches. This is not a validated reading-age score.',
        'lessons_checked': len(lessons), 'questions_checked': sum(len(l['questions']) for l in lessons),
        'introductions_and_answer_sets_rewritten': sum(bool(l.get('beginner')) for l in lessons),
        'questions_rewritten': sum(len(l['questions']) for l in lessons if l.get('beginner')),
        'rewritten_lesson_ids': [l['id'] for l in lessons if l.get('beginner')],
        'remaining_lessons_for_individual_rewrite': sum(not l.get('beginner') for l in lessons),
        'child_comprehension_tested': 0,
        'lessons_with_glossary_matches': sum(bool(l['reading_aid']['terms']) for l in lessons),
        'sentences_over_100_characters': sum(len(a['long_sentences']) for a in audit),
        'frequent_unclassified_english_or_identifiers': unknown.most_common(100),
        'lessons': audit,
    }
