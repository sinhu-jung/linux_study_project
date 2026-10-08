"""Complete explanations of the small GCD and LCM implementation files."""
def register(topic,q,detail):
    topic('Binary GCD·최하위 Bit와 뺄셈의 최대공약수','라이브러리·알고리즘','lib/math/gcd.c','gcd',
      '정수 비율이나 크기 정규화에 최대공약수가 필요하며 나눗셈 대신 bit와 뺄셈으로 계산하는 방법을 배울 수 있습니다.',
      'GCD는 한 입력이 0이면 다른 입력을 반환합니다. FFS가 효율적인 config에서는 두 수 OR의 trailing zero로 공통 2의 거듭제곱을 기억하고 각 수의 2 인수를 shift로 제거합니다. 홀수끼리 큰 수에서 작은 수를 빼며 같아지면 공통 2 인수를 복원합니다. FFS가 비효율적인 config는 최하위 공통 bit 기준의 shift loop 변형을 사용합니다.',
      'Unsigned long 입력·폭을 확인해 gcd(a,b)를 호출합니다. __ffs는 0에 대한 유효 결과를 보장하는 helper라고 가정하지 않으며 처음 zero 검사와 loop 불변식이 이를 어떻게 피하는지 읽습니다. CONFIG 선택은 runtime if와 다릅니다.',
      'lib/math/gcd.c의 두 #if/#else 구현을 전부 읽고 gcd(24,18) 상태를 종이에 추적하세요.',
      q('gcd(24,18)의 결과와 효율적인 FFS 분기에서 복원할 공통 2 인수는?','결과 6, 공통 인수 2','결과 3, 공통 인수는 버려도 된다','24|18=26의 trailing zero는 1입니다. b는 9, a는 3으로 정규화합니다. 9-3=6을 다시 홀수 3으로 줄여 a=b=3이 되면 3<<1=6을 반환합니다.'),
      q('gcd(0,18)은 __ffs(0)을 실행해 계산하는가?','처음 zero 검사에서 18을 반환한다','항상 0의 trailing zero를 계산한다','r=a|b는 18이고 !a||!b 분기에서 r을 반환합니다. Gcd(0,0)은 같은 규칙으로 0입니다.'),
      details=[detail('효율적인 FFS 분기 전체','r=a|b → 한 입력 zero면 r 반환 → b를 홀수로 shift → b==1이면 r&-r 반환 → loop에서 a를 홀수로 shift → a==1이면 공통 bit 반환 → a==b이면 a<<ffs(r) 반환 → 큰 a를 확보하고 a-=b로 다음 순회입니다. 두 홀수가 다르면 차이는 양수라 다음 ffs 입력 0을 피합니다.'),detail('Loop 정규화 분기 전체','r&=-r로 공통 최하위 bit를 분리합니다. b가 그 bit를 가질 때까지 shift하고 b==r이면 r입니다. A도 같은 방식으로 normalize하고 r·b와 같으면 반환합니다. 큰 a에서 b를 뺀 뒤 shift하고 필요하면 b를 더한 뒤 다시 shift하여 공통 bit 기준의 홀수 상태로 다음 반복을 연결합니다.'),detail('Config와 공개','CONFIG_CPU_NO_EFFICIENT_FFS에 따라 전처리 단계에서 구현 하나를 선택합니다. EXPORT_SYMBOL_GPL(gcd)는 GPL module에 심볼을 공개하는 정보입니다. 두 함수가 runtime에 연달아 실행되는 코드가 아닙니다.'),detail('Unsigned 최하위 Bit','r&-r에서 unsigned -r은 해당 정수 폭의 modulo 연산입니다. 2의 보수 표현에서 가장 낮은 set bit를 분리하지만 signed minimum의 부호 반전과 같은 계약이라고 가져오면 안 됩니다.')])
    topic('LCM·먼저 나누기와 Zero Fallback','라이브러리·알고리즘','lib/math/lcm.c','lcm',
      '두 주기의 공통 반복 간격을 계산하려면 최대공약수·최소공배수 관계와 정수 overflow를 함께 이해해야 합니다.',
      'lcm은 두 입력이 모두 nonzero일 때 (a/gcd(a,b))*b를 반환하고 하나가 0이면 0입니다. 먼저 나누면 a*b를 먼저 계산하는 불필요한 중간 overflow를 줄이지만 최종 곱이 unsigned long 범위를 넘는 문제는 자동 검출하지 않습니다. lcm_not_zero는 lcm 결과가 nonzero이면 그대로, 0이면 b가 nonzero일 때 b, 아니면 a를 반환합니다.',
      '호출자가 입력 범위와 최종 곱의 표현 가능성을 검사합니다. 수학적 LCM(0,b)=0 정책과 not_zero fallback 목적을 구분하고 overflow 결과가 0일 때 fallback도 영향을 받음을 확인합니다.',
      'lib/math/lcm.c의 lcm·lcm_not_zero·b?:a를 전부 읽고 4/6·0/6·0/0을 계산하세요.',
      q('lcm(0,6)과 lcm_not_zero(0,6)은 각각?','0과 6','둘 다 0','lcm은 zero 입력이라 0입니다. not_zero는 그 0 결과를 보고 GNU C b?:a에서 b=6을 반환합니다.'),
      q('a/gcd를 먼저 계산하면 모든 unsigned long overflow가 완전히 사라지는가?','최종 곱의 범위 검사는 여전히 필요하다','나누기 하나로 어떤 큰 결과도 저장된다','최종 수학적 LCM이 표현 범위보다 크면 unsigned 곱은 modulo로 돌아갈 수 있습니다. 이 함수는 checked multiplication 오류 API가 아니므로 caller가 범위를 보장해야 합니다.'),
      details=[detail('LCM 함수 전체','if(a&&b)는 두 값의 zero 여부를 검사합니다. Short-circuit 논리는 bitwise a&b와 다릅니다. 양쪽이 nonzero이면 gcd가 양수인 계산 계약에 따라 나누고 곱합니다. Else는 0 반환입니다.'),detail('Fallback 함수 전체','unsigned long l=lcm(a,b)로 지역 변수를 만들고 if(l)이면 그대로 반환합니다. return(b?:a)는 GNU omitted-middle conditional로 b?b:a의 의미입니다. C++ 문법이 아니라 이 커널이 사용하는 GNU C 확장입니다.'),detail('0·0과 순서','입력 0·0은 두 함수 모두 0입니다. 4·6은 gcd=2, 4/2*6=12입니다. 먼저 곱하는 24/2와 수학적 결과는 같지만 machine 정수의 중간 범위는 다릅니다.'),detail('Include와 Export','gcd.h와 lcm.h는 함수 선언, compiler.h는 compiler helper, export.h는 module 공개 관련 선언입니다. EXPORT_SYMBOL_GPL 두 개는 함수 호출이 아니라 해당 함수의 연결·공개를 위한 정보입니다.')])
