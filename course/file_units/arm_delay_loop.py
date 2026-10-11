"""Whole ARM assembly loop delay, including carry arithmetic."""
ROWS = [dict(
    path='arch/arm/lib/delay-loop.S',
    title='ARM 지연 루프 전체: UMULL과 carry 기반 횟수 계산',
    intro='마이크로초 변환,64비트 곱의 상·하위 word와 조건 플래그를 이용하는 대기 루프를 해설합니다.',
    principle='어셈블리 주석의 요약과 실제 carry 전달 식을 구분하고 활성 명령만 실행 흐름에 포함합니다.',
    use='앞서 delay.h와 delay.c에서 선언·선택한 __loop 계열의 실제 본문을 연결합니다.',
    area='ARM 어셈블리 · 곱셈 상하위 word · carry · 조건 분기 · 고정소수점',
    sections=[
        ('파일 구성', 'GPL-2.0-only와 저작권,linkage/cfi_types/assembler/delay 헤더 뒤 CONFIG_ARCH_RPC에서 .arch armv4를 지정합니다. text 섹션의 두 literal,세 typed function과 비활성 전처리 블록이 전부입니다. SYM_TYPED_FUNC_START와 END는 함수 경계·메타데이터 표현이며 각 매크로의 세부 구현까지 이 파일에 있는 것은 아닙니다.'),
        ('Literal의 차이', '.LC0의 .word는 loops_per_jiffy 심벌 주소를 담고 .LC1은 UDELAY_MULT 상수를 담습니다. 그래서 변환 함수는 .LC1에서 배율을 한 번 읽지만 const 함수는 .LC0에서 주소를 읽고 [r2]를 다시 읽어 실제 보정값을 얻습니다. 주소와 해당 주소의 값이라는 간접 참조 단계를 구별합니다.'),
        ('마이크로초 입력', '__loop_udelay는 r0의 usecs에 UDELAY_MULT를 mul로 곱해 r0에 두고 __loop_const_udelay로 b 분기합니다. 별도 bl 호출이 아니므로 새 복귀 주소를 만들지 않습니다. 주석의 r0<=2000,HZ<=1000 전제와32비트 곱의 범위를 함께 읽어야 하며 본문은 초과 입력을 검사하지 않습니다.'),
        ('64비트 곱', '__loop_const_udelay는 loops_per_jiffy를 r2에 읽고 umull r1,r0,r2,r0로 unsigned64비트 곱을 만듭니다. 하위32비트는 r1,상위32비트는 r0입니다. 원래 입력 r0가 연산 후 상위 word로 바뀌므로 레지스터 이름에 고정된 의미를 붙이지 않습니다.'),
        ('Carry 생성', 'adds r1,r1,#0xffffffff는 하위 word L에32비트 최대값을 더합니다. L=0이면 결과0xffffffff,carry0이고 L이0이 아니면 L-1,carry1입니다. 따라서 다음 명령이 받는 carry는 L의 최상위 비트가 아니라 L!=0이라는 조건입니다.'),
        ('실제 횟수 식과 주석', 'adcs r0,r0,r0는 상위 word H를 두 배로 하고 위 carry를 더합니다.32비트 wrap을 제외한 실제 값은2H+(L!=0)입니다. 주석은 rounding up과31비트 이동으로 요약하지만 모든64비트 곱에 대한 정확한 ceil(P/2^31) 식과는 다릅니다. 예를 들어 H=0,L=0x80000001이면 명령 결과1이고 수학적 ceil(P/2^31)은2입니다. 주석을 그대로 일반 산술 등식으로 바꾸지 않고 명령 동작을 기준으로 설명합니다.'),
        ('영과 꼬리 분기', 'adcs가 설정한 zero 조건에서 reteq lr로 복귀합니다. 그렇지 않으면 __loop_delay로 b 분기합니다. 보정 곱에서 나온 값이0인 경로를 즉시 끝내고 실제 count가 있으면 루프로 넘기는 구조입니다. 이 구현은 타이머 counter를 읽지 않습니다.'),
        ('활성 지연 루프', '.align 3 뒤 __loop_delay는 subs r0,r0,#1, bhi 자기 자신, ret lr입니다. unsigned higher 조건은 carry1이면서 zero0일 때 참입니다. 양수 n은 감소 결과가0이 될 때까지 반복하고 직접 입력0도 첫 뺄셈에서 borrow가 생겨 분기하지 않습니다.0에서 wrap된0xffffffff만 보고 매우 긴 루프에 들어간다고 판단하면 틀립니다.'),
        ('비활성 코드와 시간', '#if 0 안의 여러 retls/subs 쌍은 현재 빌드의 실행 명령이 아닙니다. 이를 loop unrolling이 실제 적용된 것으로 세지 않습니다. 활성 루프의 count를 CPU cycle 수와 일대일로 동일시할 수도 없으며 캐시·분기·CPU 속도와 보정값이 실제 시간에 영향을 줍니다.'),
        ('CS 연결과 범위', 'literal pool,주소와 값의 간접 참조,tail branch,64비트 곱과32비트 레지스터 쌍,carry/zero 기반 제어,주석과 명령의 교차 확인을 학습합니다. 소스와 산술 추적은 실제 ARM 하드웨어의 지연 정확도를 측정한 검증이 아닙니다.')
    ],
    questions=[
        ('UMULL 뒤 곱의 하위32비트는 어디에 있는가?', 'r1이다', 'r0이다', 'umull r1,r0,...에서 첫 목적지가 low,두 번째가 high입니다. 입력 때 r0가 가진 의미와 결과 때 의미를 구분해야 합니다.'),
        ('하위 word가0일 때 adds에 의해 다음 adcs로 전달되는 carry는?', '0이다', '1이다', '0+0xffffffff는32비트 범위를 넘지 않습니다. 하위 word가1 이상일 때 합이 넘쳐 carry1이 됩니다.'),
        ('H=0,L=0x80000001의 두 산술 명령 결과는?', '1이다', '항상 수학적 올림 결과2이다', 'L이0이 아니므로 carry1이고 adcs는2*0+1입니다. 주석의31비트 이동 설명을 모든 값에 대한 정확한 ceil 식으로 일반화하지 않습니다.'),
        ('__loop_delay에 직접0을 전달하면 wrap 때문에 긴 반복을 하는가?', '아니다. 첫 subs의 borrow 때문에 bhi가 성립하지 않는다', '그렇다.0xffffffff번을 반드시 반복한다', 'bhi는 결과가0이 아닌지만 보는 분기가 아닙니다. carry와 zero 조건을 모두 확인해야 합니다.'),
        ('#if 0 안의 반복된 subs/retls는 실행되는가?', '아니다. 현재 전처리에서 제외된다', '그렇다. 활성 루프가 매번 모두 실행한다', '활성 본문은 바깥 subs,bhi,ret입니다. 보존된 비활성 코드를 실행 횟수 계산에 포함하면 틀립니다.')
    ]
)]
