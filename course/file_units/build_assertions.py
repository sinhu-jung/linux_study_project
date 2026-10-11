"""Complete build-time assertion interface."""
ROWS = [dict(
    path='include/linux/build_bug.h',
    title='빌드 검사 전체: 상수 불변식을 컴파일 오류로 만들기',
    intro='실행 중 잘못된 상태를 발견하기 전에 타입·배치·상수의 전제를 검사합니다.',
    principle='BUILD_BUG_ON 계열은 참이면 실패하는 조건을,static_assert는 참이어야 하는 조건을 표현합니다. 값0을 만드는 검사,표현식 유효성만 확인하는 검사,구조체 오프셋 검사도 제공합니다.',
    use='런타임 입력 검증이나 복구 코드를 대체하지 않습니다. 각 매크로가 요구하는 상수식·컴파일러 분석 조건을 구분하고 기대한 실패가 실제로 컴파일에서 발생하는지 확인합니다.',
    area='컴파일 시 검증 · 상수식·구조체 ABI',
    sections=[
        ('파일 전체', 'SPDX,guard,compiler.h 포함 후 BUILD_BUG_ON_ZERO,2의 거듭제곱 검사2종,INVALID,MSG,ON,무조건 BUILD_BUG,static_assert wrapper,ASSERT_STRUCT_OFFSET을 정의합니다. 함수 본문이나 가변 전역 상태는 없습니다.'),
        ('값을 갖는 검사', '일반 BUILD_BUG_ON_ZERO(e)는 익명 구조체 비트필드의 폭을 -!!e로 만듭니다. e가참이면 음수 폭으로 컴파일 오류가 나고 거짓이면 이 GNU C 표현에서 int형0을 얻어 초기화 식 등에 더할 수 있습니다. __CHECKER__에서는 별도 분기로 단순0을 정의하므로 같은 강제 검사 경로가 아닙니다.'),
        ('2의 거듭제곱과0', 'n&(n-1)은 양의2의 거듭제곱에서0이 됩니다. 공개 BUILD_BUG_ON_NOT_POWER_OF_2는 n==0도 검사하지만 내부 __BUILD_BUG_ON_NOT_POWER_OF_2는 비트식만 검사하므로0을 배제하지 않습니다. 내부 helper와 공개 전제를 구분합니다.'),
        ('평가하지 않는 표현식 검사', 'BUILD_BUG_ON_INVALID(e)는 sizeof((__force long)e)를 void로 버립니다. 표현식의 형식이 유효한지는 컴파일러가 확인하지만 이 고정 long 타입 sizeof의 피연산자는 실행되지 않습니다. x++를 넣어도 x 증가를 실행하는 런타임 검사가 아닙니다.'),
        ('조건과 진단 메시지', 'BUILD_BUG_ON_MSG(cond,msg)는 compiletime_assert(!cond,msg)에 위임합니다. BUILD_BUG_ON은 조건을 문자열로 포함한 기본 메시지를 붙이고 BUILD_BUG는 조건1을 전달합니다. BUILD_BUG는 컴파일러가 제거해야 하는 경로가 남는지 확인하는 용도도 있어 단순 실행 시 panic 함수와 다릅니다.'),
        ('static_assert', 'C11 _Static_assert wrapper이며 메시지를 생략하면 조건의 문자열을 사용합니다. 전역 영역에서도 사용할 수 있지만 정수 상수식이 필요합니다. __builtin_constant_p가 참으로 보는 식이라고 모두 정수 상수식인 것은 아닙니다. BUILD_BUG_ON과 실패 조건의 방향이 반대입니다.'),
        ('구조체 오프셋', 'ASSERT_STRUCT_OFFSET은 offsetof(type,field)가 예상 오프셋과 다른지 BUILD_BUG_ON_MSG로 검사합니다. 필드가 같은 이름이어도 패딩·순서·타입 변화로 ABI 위치가 달라지는 것을 감지할 수 있습니다. 예상값은 검증하려는 대상 ABI에서 정해야 합니다.'),
        ('검증 범위', '정상 식의 컴파일 성공만 보는 것으로 충분하지 않습니다. 거짓 static_assert,참 BUILD_BUG_ON_ZERO,0과3의 거듭제곱 검사 등 실패해야 하는 사례의 컴파일 거부도 확인합니다. 의존성 compiletime_assert를 대체한 사용자 공간 검사는 실제 커널 컴파일러 전체 동작 검증과 구분합니다.')],
    questions=[
        ('BUILD_BUG_ON과 static_assert의 실패 조건은?', '각각 조건이 참일 때와 거짓일 때다', '둘 다 조건이 참이면 실패한다', 'BUILD_BUG_ON은 금지 상태를,static_assert는 유지할 불변식을 표현합니다. 조건의 방향을 반대로 쓰면 정상 코드를 거부합니다.'),
        ('내부 __BUILD_BUG_ON_NOT_POWER_OF_2는0을 배제하는가?', '아니다. 공개 버전에 별도 n==0 검사가 있다', '그렇다. 비트식 하나로0도 반드시 거부한다', '0&(0-1)은0이어서 비트식만으로는0이 통과합니다. 공개 매크로가 추가 조건을 둡니다.'),
        ('BUILD_BUG_ON_INVALID(x++)가 x를 증가시키는가?', '아니다. 형식만 검사하고 sizeof 안의 식을 실행하지 않는다', '그렇다. 매크로 호출마다 증가한다', 'long으로 변환한 표현식의 sizeof는 런타임 부수효과를 수행하지 않습니다.'),
        ('ASSERT_STRUCT_OFFSET은 무엇을 확인하는가?', '지정 필드가 예상 바이트 오프셋에 있는지', '구조체가 힙에 할당되었는지', 'offsetof와 상수 예상 위치를 비교합니다. 할당이나 객체 수명 상태는 검사하지 않습니다.')])]
