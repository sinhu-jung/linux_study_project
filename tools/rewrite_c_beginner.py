"""Individually authored C introductions. Re-running preserves the original lesson."""
import copy
import json
from pathlib import Path
from lesson_storage import _atomic_text

ROOT = Path(__file__).resolve().parents[1]

# story, meaning, pencil activity, step-by-step guide, questions in original order.
ROWS = {
'01_hello': (
 '연극 대본에는 시작하는 장면이 있지요. 프로그램에도 우리가 작성한 일을 시작하는 자리가 있습니다.',
 '이 예제는 화면에 인사말을 쓰는 작은 C 프로그램입니다. main은 이 예제의 시작 함수입니다. 함수는 이름을 붙인 작업 묶음입니다.',
 '종이에 시작 → 인사말 쓰기 → 끝을 그리세요. 각 칸 아래에 main, printf, return을 적어 보세요.',
 ['#include <stdio.h>는 printf의 사용법을 컴파일러에게 알려 줍니다. 컴파일러는 C 코드를 번역하는 도구입니다.',
  'main의 중괄호 { } 안에 실행할 일을 적습니다. 이 예제의 작업은 위에서 아래로 진행합니다.',
  'printf는 화면 등에 글자를 출력하는 함수입니다. 따옴표 안의 Hello Linux!를 쓰고, \\n을 만나면 다음 줄로 내려갑니다.',
  'return 0은 main을 끝내고 성공했다는 번호 0을 돌려줍니다. 다른 함수에서도 언제나 0이 성공이라는 뜻은 아니므로 사용 약속을 확인해야 합니다.'],
 [('이 예제에서 우리가 적은 작업을 시작하는 함수는 무엇인가요?', ['글자를 쓰는 printf','시작 함수 main','선언을 담은 파일 stdio.h'],
   'main입니다. main 안에서 printf를 불러 인사말을 씁니다. printf는 출력하는 일을 하고, stdio.h는 사용법을 알려 주는 헤더 파일입니다. 두 가지 모두 이 예제의 시작 함수 이름은 아닙니다.'),
  ('printf가 화면에 쓰는 인사말은 무엇인가요?', ['Hello Linux!','return 0','아무 글자도 쓰지 않아요'],
   'Hello Linux!입니다. printf의 따옴표 안에 있는 글자를 확인하세요. 뒤의 \\n은 두 글자를 그대로 쓰라는 뜻이 아니라 줄을 바꾸라는 표시입니다. return 0은 프로그램을 끝내는 코드라서 출력할 인사말이 아닙니다.')]),
'02_variables': (
 '이름표를 붙인 상자에 구슬 세 개를 넣었습니다. 두 개를 더 넣으면 다섯 개가 됩니다.',
 '변수는 값을 기억하는 이름 붙은 자리입니다. 여기서는 count라는 이름의 자리에 정수 3을 넣고, 2를 더한 값을 다시 넣습니다.',
 'count라고 적은 칸에 3을 쓰세요. 옆에서 3+2를 계산한 뒤 칸의 3을 지우고 결과를 적으세요.',
 ['int count = 3은 정수를 담을 count를 만들고 처음 값 3을 넣는 코드입니다. 정수는 0, 1, -1처럼 소수 부분이 없는 수입니다.',
  'count + 2는 현재 기억한 값 3에 2를 더해 5를 계산합니다.',
  '=는 오른쪽 결과를 왼쪽 자리에 저장하라는 뜻입니다. 그래서 count의 값이 5로 바뀝니다. 같은지 물을 때 쓰는 ==와 다릅니다.',
  'printf의 %d 자리에는 count에 담긴 정수가 들어갑니다. 이 예제는 5를 쓰고 줄을 바꿉니다.'],
 [('3을 넣은 count에 count = count + 2를 실행했습니다. 이제 count는 얼마인가요?', ['2','3','5'],
   '5입니다. 먼저 오른쪽에서 현재 값 3에 2를 더합니다. 그 결과 5를 왼쪽 count에 다시 저장합니다. 2는 더한 양이고 3은 바꾸기 전 값입니다.'),
  ('count = count + 2에서 =는 어떤 일을 하나요?', ['두 값이 같은지 물어요','오른쪽 계산 결과를 왼쪽에 넣어요','프로그램을 끝내요'],
   '계산 결과를 저장합니다. 수학의 등호처럼 양쪽이 같다는 주장으로 읽으면 헷갈립니다. C에서 같냐고 묻는 표시는 ==이고, 함수를 끝내는 명령은 return입니다.')]),
'03_if': (
 '비가 오면 우산을 챙기고, 아니면 그냥 나갑니다. 조건을 보고 할 일을 고르는 것이지요.',
 'if는 조건이 맞을 때만 안쪽 코드를 실행합니다. 이 예제는 파일 열기에 실패했다고 가정해 fd에 -1을 넣습니다. 실제 파일을 여는 코드는 아닙니다.',
 'fd=-1 → 0보다 작은가? → 실패 문장 쓰기 → 끝을 그리세요. 끝 다음에 적힌 성공 문장까지 갈 수 있는지 보세요.',
 ['fd는 여기서 실패 여부를 살펴볼 정수 변수입니다. 처음부터 -1을 넣어 실패 상황을 만들어 둡니다.',
  'fd < 0은 fd가 0보다 작냐는 질문입니다. -1은 0보다 작으므로 조건이 참입니다.',
  '조건이 참이면 if의 { } 안을 실행합니다. open failed를 출력한 뒤 return 1을 만납니다.',
  'return은 현재 함수를 끝냅니다. 여기서는 main이 끝나므로 아래쪽 open succeeded 출력까지 가지 않습니다.'],
 [('fd가 -1일 때 화면에 실제로 나오는 글자는 무엇인가요?', ['open succeeded','실패와 성공 문장 둘 다','open failed'],
   'open failed만 나옵니다. -1 < 0이 맞아서 실패 쪽으로 갑니다. 그 안의 return 1에서 끝나므로 성공 문장은 출력하지 않습니다.'),
  ('이 실행에서 return 1 아래에 있는 성공 출력도 실행할까요?', ['아니요','네','두 번 실행해요'],
   '아니요. return 1은 잠시 쉬라는 뜻이 아니라 main을 끝내라는 뜻입니다. 따라서 이 실행에서는 그 아래 출력에 도착하지 않습니다.')]),
'04_array_loop': (
 '사물함 세 칸을 왼쪽부터 차례로 열어 물건을 확인한다고 생각해 보세요.',
 '배열은 같은 종류의 값을 나란히 넣는 칸들입니다. 이 예제의 values에는 10, 20, 30이 들어 있습니다. 칸 번호는 1이 아니라 0부터 시작합니다.',
 '칸 세 개에 10, 20, 30을 쓰고 위에 번호 0, 1, 2를 적으세요. 손가락을 i라고 생각하며 한 칸씩 옮기세요.',
 ['values[0]은 10, values[1]은 20, values[2]는 30입니다. 대괄호 안의 수는 값이 아니라 칸 번호입니다.',
  'i는 지금 읽을 칸 번호를 기억합니다. 처음에는 0입니다.',
  'while (i < 3)은 i가 3보다 작은 동안 같은 작업을 반복하라는 뜻입니다.',
  '한 번 값을 출력할 때마다 i++로 번호를 1 늘립니다. 0, 1, 2번을 읽고 i가 3이 되면 멈춥니다. 3번 칸은 이 배열에 없습니다.'],
 [('10, 20, 30이 든 배열에서 values[1]은 어떤 값인가요?', ['10','20','30'],
   '20입니다. 첫 칸은 0번이라서 10입니다. 1번은 두 번째 칸이므로 20입니다. 30은 2번 칸의 값입니다.'),
  ('i가 0에서 시작해 매번 1씩 늘고, i < 3일 때만 출력합니다. 몇 번 출력하나요?', ['2번','3번','4번'],
   '3번입니다. i=0일 때 10, i=1일 때 20, i=2일 때 30을 출력합니다. 그다음 i=3에서는 조건이 맞지 않아 멈춥니다.')]),
'05_function': (
 '두 숫자를 넣으면 합을 알려 주는 작은 계산 상자를 떠올려 보세요.',
 'add는 두 정수를 더하는 함수입니다. 함수에 값을 건네는 일을 호출, 결과를 돌려주는 일을 반환이라고 합니다.',
 '입력 2와 3 → add → 결과 5를 그리세요. 함수 안에서는 두 입력의 이름을 a와 b로 붙여 보세요.',
 ['int add(int a, int b)는 정수 두 개를 받아 정수 결과를 돌려주는 함수의 모습입니다.',
  'a와 b는 받은 값을 기억하는 이름입니다. 이렇게 함수의 입력을 받는 자리를 매개변수라고 합니다.',
  'add(2, 3)을 부르면 이 호출의 a는 2, b는 3입니다. return a + b가 합인 5를 돌려줍니다.',
  'main은 돌려받은 값을 result에 저장합니다. 그다음 printf로 5를 화면에 씁니다.'],
 [('두 수를 더하는 add에 2와 3을 건네면 어떤 결과를 돌려주나요?', ['2','3','5'],
   '5입니다. a에 받은 2와 b에 받은 3을 더해 2+3=5를 만듭니다. return이 이 합을 부른 곳으로 돌려줍니다. 한 입력만 그대로 돌려주는 함수가 아닙니다.'),
  ('add 함수 안의 a와 b는 무슨 역할인가요?', ['함수가 받은 두 값을 기억해요','파일 이름이에요','반복 횟수만 기억해요'],
   '함수에 건넨 값을 받는 자리입니다. 이 호출에서는 각각 2와 3입니다. 함수마다 입력을 받는 이름과 종류를 정할 수 있습니다. a와 b라는 이름 자체가 파일이나 반복을 뜻하지는 않습니다.')]),
'06_pointer': (
 '친구 집 주소를 쪽지에 적었습니다. 쪽지를 보고 그 집으로 찾아가 물건을 바꿀 수 있지요.',
 '포인터는 값이 있는 메모리 위치를 담습니다. 이 예제에서 p는 value의 위치를 담고, *p는 그 위치의 값을 사용합니다. 쪽지와 집이 다르듯 주소와 값도 다릅니다.',
 'value라는 칸에 7을 쓰세요. p라는 쪽지에서 그 칸으로 화살표를 그리세요. 화살표를 따라가 칸의 7을 9로 고치세요.',
 ['int value = 7은 정수 값 7을 기억합니다.',
  'int *p는 정수의 주소를 담을 포인터 p를 만듭니다. 이 선언에서 *는 포인터라는 표시입니다.',
  '&value는 value가 있는 주소를 얻습니다. p = &value로 그 주소를 p에 넣습니다.',
  '식의 *p는 그 주소의 실제 값을 사용한다는 뜻입니다. *p = 9를 하면 p가 아니라 p가 가리키는 value의 내용이 9로 바뀝니다.'],
 [('p에 &value를 넣었습니다. p가 기억하는 것은 무엇인가요?', ['7이라는 값 자체','value가 있는 주소','함수 이름'],
   'value의 주소입니다. &는 위치를 얻는 표시입니다. value 안에는 7이 있고 p 안에는 그 칸의 위치가 있다는 점을 나누어 보세요.'),
  ('value는 처음에 7입니다. p가 value를 가리킬 때 *p = 9를 실행하면 value를 출력한 결과는?', ['7','9','0'],
   '9입니다. *p는 value와 같은 칸을 사용합니다. 그 칸에 9를 넣었으므로 value를 읽어도 9가 나옵니다. 주소가 9로 바뀐 것은 아닙니다.')]),
'07_struct': (
 '학생 카드에 이름과 출석 번호를 함께 적듯, 관련된 정보를 하나로 묶을 수 있습니다.',
 '구조체는 여러 정보를 묶을 수 있는 C의 자료 형식입니다. 이 예제의 struct File은 position이라는 항목 하나만 가진 연습용 카드입니다. 실제 Linux 파일 구조를 그대로 옮긴 것은 아닙니다.',
 'file이라는 카드 안에 position=0을 쓰세요. p에서 카드로 화살표를 그린 뒤 카드의 position을 4로 고치세요.',
 ['struct File { int position; }은 이런 모양의 카드를 만들겠다는 형식 정의입니다. 안의 개별 항목을 멤버 또는 필드라고 부릅니다.',
  'struct File file = {0}은 실제 카드 하나를 만들고 position을 0으로 시작합니다.',
  'file.position은 카드 자체에서 position을 고릅니다. 점 .은 구조체의 항목을 고르는 표시입니다.',
  'p는 카드의 주소를 담습니다. p->position은 p가 가리키는 카드의 position입니다. (*p).position과 같은 뜻이며, 여기에 4를 넣으면 원래 카드가 바뀝니다.'],
 [('p가 file을 가리킬 때 p->position은 무엇을 고르나요?', ['file 안의 position 항목','p 자체가 놓인 주소','File이라는 글자'],
   'file 안의 position입니다. ->는 포인터를 따라간 뒤 그 구조체 안의 항목을 고릅니다. 포인터가 놓인 주소를 구하거나 글자를 만드는 연산은 아닙니다.'),
  ('처음 position은 0입니다. p->position = 4 다음 file.position을 출력하면 얼마인가요?', ['0','4','7'],
   '4입니다. p가 가리키는 대상이 바로 file입니다. 별도의 복사본을 만든 것이 아니라 원래 file의 항목을 바꿨으므로 0이 남지 않습니다.')]),
'08_function_pointer': (
 '안내 쪽지에 일을 맡길 곳을 적어 두면 나중에 그곳으로 부탁할 수 있습니다.',
 '함수 포인터는 호출할 함수를 가리키는 값입니다. 여기서는 operation에 두 배를 계산하는 twice를 연결합니다.',
 'operation → twice → 입력에 2 곱하기를 그리세요. 3을 보냈을 때 돌아오는 수를 적으세요.',
 ['twice는 받은 value에 2를 곱해 돌려주는 함수입니다. twice(3)은 6입니다.',
  'int (*operation)(int)는 정수 하나를 받아 정수를 돌려주는 함수를 가리키는 포인터 선언입니다. 이름을 둘러싼 (*operation) 괄호에 주의하세요.',
  '= twice는 operation이 twice를 가리키도록 합니다. 다른 종류의 함수를 아무렇게나 연결해도 된다는 뜻은 아닙니다.',
  'operation(3)은 저장해 둔 함수를 호출합니다. 이 예제에서는 twice(3)과 같은 작업을 하므로 printf가 6을 씁니다.'],
 [('operation에 twice를 연결했습니다. operation이 가리키는 함수는?', ['main','printf','twice'],
   'twice입니다. int (*operation)(int) = twice의 오른쪽을 보세요. main은 실행을 시작하는 함수이고 printf는 결과를 출력하는 함수입니다.'),
  ('twice가 입력에 2를 곱할 때 operation(3)의 결과는?', ['3','6','9'],
   '6입니다. operation은 twice를 가리키므로 3을 twice에 건넵니다. 3×2=6을 돌려받습니다. 함수 포인터를 거쳤다고 계산 규칙이 바뀌지는 않습니다.')]),
'09_macro': (
 '행사 준비표에서 의자 수를 매번 적는 대신 의자수라는 이름을 붙여 쓸 수 있습니다.',
 '매크로는 코드를 번역하기 전에 정한 이름을 다른 코드로 바꾸는 규칙입니다. 여기서는 BUFFER_SIZE라는 이름을 256으로 바꿉니다.',
 'char buffer[BUFFER_SIZE]를 적고 BUFFER_SIZE 자리에 256을 넣어 다시 써 보세요.',
 ['#define BUFFER_SIZE 256은 BUFFER_SIZE를 256으로 바꾸라는 전처리 규칙입니다. 실행 중 값을 넣는 변수와는 다릅니다.',
  'char buffer[BUFFER_SIZE]는 여기서 char 256개짜리 배열이 됩니다. char 하나의 크기는 C에서 1바이트입니다.',
  'sizeof(buffer)는 배열 전체가 몇 바이트인지 구합니다. 이 자리의 buffer는 배열이므로 256이 나옵니다.',
  'sizeof의 결과 형식은 크기를 나타내는 size_t입니다. printf의 %zu는 이 형식의 값을 출력하는 표시입니다. 배열 대신 포인터의 sizeof를 재면 결과가 다릅니다.'],
 [('전처리기가 BUFFER_SIZE를 무엇으로 바꾸나요?', ['256','buffer','0'],
   '#define에 적은 256입니다. BUFFER_SIZE는 사람이 알아보기 쉬운 이름이고, 이 예제에서는 실제로 256이라는 코드로 바뀝니다. 배열 이름 buffer로 바꾸는 규칙은 아닙니다.'),
  ('char 256개짜리 배열 buffer 전체의 sizeof는 얼마인가요?', ['1바이트','255바이트','256바이트'],
   '256바이트입니다. char 한 개가 1바이트이고 256개가 있으므로 1×256=256입니다. 마지막 칸 번호 255와 전체 칸 수 256을 구별하세요.')]),
'10_read': (
 '긴 책을 한 번에 베끼지 않고 몇 줄씩 받아 적는 모습을 생각해 보세요. 받은 줄만큼만 옮기고 나머지는 이어서 합니다.',
 '이 프로그램은 파일을 조금씩 읽어 화면 쪽으로 보냅니다. buffer는 잠깐 담는 상자, n은 이번에 받은 양, sent는 그중 이미 보낸 양입니다.',
 '10바이트를 읽었다고 하세요. 첫 write가 4바이트만 보냈다면 남은 양을 계산하세요. 다음 시작은 buffer+4이고 남은 양은 6입니다.',
 ['실행할 때 파일 경로를 주면 그 파일을 씁니다. 경로를 안 주면 /etc/hostname을 읽습니다. argc는 받은 명령줄 항목 수, argv는 그 항목들을 담은 배열입니다.',
  'open(path, O_RDONLY)는 읽기 전용으로 파일을 엽니다. 성공하면 열린 연결의 번호 fd를 받고, 음수면 실패를 알리고 끝냅니다.',
  'buffer는 char 256칸짜리 배열입니다. read는 최대 256바이트를 여기에 넣고 실제 읽은 양 n을 돌려줍니다. 이 일반 파일에서는 n=0이면 끝, n<0이면 오류입니다.',
  '읽은 양이 양수면 sent=0으로 시작합니다. write가 일부만 보낼 수 있으므로 sent<n인 동안 남은 부분을 다시 보냅니다. buffer+sent는 다음 보낼 위치, n-sent는 남은 양입니다.',
  'write가 양수를 돌려주면 보낸 양을 sent에 더합니다. 이 예제는 0이나 음수가 나오면 오류로 처리하고 파일을 닫아 끝냅니다. 자동 재시도를 모두 구현한 예제는 아닙니다.',
  '읽기를 끝낸 뒤에는 read 오류도 확인하고 close로 열린 연결을 닫습니다. ssize_t는 음수 오류와 양수 길이를 담고, size_t는 음수 없는 크기를 담는 형식입니다.'],
 [('이 예제에서 일반 파일을 읽는 read가 0을 돌려줬습니다. 무슨 뜻인가요?', ['읽기 오류예요','파일 끝에 도달했어요','256바이트를 읽었어요'],
   '파일 끝입니다. 이 예제는 0보다 큰 크기를 요청합니다. 양수면 그만큼 읽은 것이고, 0이면 더 읽을 내용이 없으며, -1이면 오류입니다. 0을 256바이트를 받았다는 뜻으로 읽으면 안 됩니다.'),
  ('자료를 보내는 write 주위에 왜 안쪽 while을 두었나요?', ['한 번에 일부만 보낼 수도 있어서','파일을 여러 번 열려고','buffer를 모두 0으로 만들려고'],
   '읽은 자료를 한 번에 전부 보내지 못할 수 있기 때문입니다. 10바이트 중 4바이트를 보내면 sent는 4, 남은 양은 6입니다. 다음 write는 남은 6바이트부터 처리합니다. 안쪽 반복은 파일 열기나 배열 초기화가 아닙니다.')]),
'11_lcm': (
 '4칸씩 뛰는 친구와 6칸씩 뛰는 친구가 출발점 다음에 처음 함께 밟는 칸을 찾아봅시다.',
 '최소공배수는 두 수의 배수 중 가장 작은 양수입니다. 4의 배수 4, 8, 12와 6의 배수 6, 12를 보면 첫 공통 수는 12입니다. 이 커널 함수는 0을 받았을 때의 규칙도 정해 둡니다.',
 '1부터 12까지 쓰세요. 4의 배수에 원, 6의 배수에 세모를 그려 처음 겹치는 수를 찾으세요. 그다음 입력이 0일 때는 코드가 어떤 길로 가는지 보세요.',
 ['lcm은 두 입력 a와 b의 최소공배수를 계산합니다. unsigned long은 음수 없는 정수 형식입니다. 이 교재의 Linux ARM64에서는 64비트입니다.',
  'a && b는 a와 b가 둘 다 0이 아닌지 묻습니다. 하나라도 0이면 이 함수는 0을 반환합니다.',
  'gcd(a, b)는 두 수를 모두 나누어떨어지게 하는 가장 큰 수인 최대공약수입니다. 4와 6의 최대공약수는 2입니다. (a/gcd(a,b))*b로 계산합니다.',
  '먼저 나누면 중간 곱을 줄일 수 있습니다. 하지만 담을 수 있는 범위보다 결과가 너무 크면 정확한 수학 결과를 그대로 저장할 수 없습니다. 이 함수에 별도 범위 검사 코드는 없습니다.',
  'lcm_not_zero는 우선 lcm을 부릅니다. 결과가 0이 아니면 그대로 돌려줍니다. 0이면 b가 0이 아닌지 보고 b 또는 a를 고릅니다. 둘 다 0이면 결과도 0입니다.',
  'b ? : a는 GNU C의 줄여 쓰는 문법입니다. b가 0이 아니면 b, 아니면 a입니다. EXPORT_SYMBOL_GPL은 GPL 호환 커널 모듈이 함수를 사용할 수 있게 내보내는 표시이며 계산식은 아닙니다.'],
 [('4와 6의 최대공약수는 2입니다. lcm(4, 6)은 얼마를 돌려주나요?', ['2','12','24'],
   '12입니다. 코드의 식대로 먼저 4÷2=2, 다음 2×6=12를 계산합니다. 2는 최대공약수이고 24는 나누지 않고 곱한 값입니다. 최소공배수는 12입니다.'),
  ('lcm에 0과 6을 주면 이 코드의 결과는 무엇인가요?', ['0','6','오류로 프로그램을 끝내요'],
   '0입니다. a가 0이므로 a && b가 맞지 않습니다. else 쪽 return 0으로 갑니다. 이 경우에는 나눗셈 식을 실행하지 않으며, 0이 들어왔다고 프로그램을 강제로 끝내지도 않습니다.'),
  ('lcm_not_zero에 0과 6을 주면 최종 결과는 무엇인가요?', ['0','6','12'],
   '6입니다. 먼저 lcm(0,6)은 0이므로 if(l)을 지나칩니다. 마지막 b ? : a에서 b는 6으로 0이 아닙니다. 그래서 b인 6을 돌려줍니다. 앞 문제의 lcm과 이 함수의 마지막 규칙이 다릅니다.')]),
}


def rewrite(rows=ROWS, authoring_source='tools/rewrite_c_beginner.py', additions=None):
    changed = []
    for path in sorted((ROOT/'course/lesson-parts').glob('*.json')):
        lessons = json.loads(path.read_text(encoding='utf-8'))
        touched = False
        for lesson in lessons:
            if lesson['id'] not in rows:
                continue
            original = lesson.setdefault('technical_original', copy.deepcopy(lesson))
            story, meaning, exercise, guide, questions = rows[lesson['id']]
            if len(questions) != len(original['questions']):
                raise ValueError('Question count changed: '+lesson['id'])
            lesson['intro'] = meaning
            lesson['guide'] = guide
            lesson['beginner'] = {'story':story, 'meaning':meaning, 'exercise':exercise}
            if additions and lesson['id'] in additions:
                lesson.update(copy.deepcopy(additions[lesson['id']]))
            lesson['questions'] = []
            for old, (prompt, options, explanation) in zip(original['questions'], questions):
                if len(options) != len(old['options']):
                    raise ValueError('Option count changed')
                lesson['questions'].append(dict(prompt=prompt, options=options,
                    answer=old['answer'], explanation=explanation,
                    original_prompt=old['prompt'], original_options=old['options'],
                    original_explanation=old['explanation']))
            lesson['easy_review'] = {'version':1, 'authoring_source':authoring_source,
                'scope':['intro','guide','questions.prompt','questions.options','questions.explanation'],
                'question_count':len(questions), 'source_code_preserved':True,
                'child_comprehension_tested':False}
            touched = True
            changed.append(lesson['id'])
        if touched:
            _atomic_text(path,json.dumps(lessons,ensure_ascii=False,indent=2)+'\n')
    if set(changed) != set(rows):
        raise ValueError('Missing authored lessons')
    return changed


if __name__ == '__main__':
    print(json.dumps(rewrite(),ensure_ascii=False))
