"""Lockdown policy transitions, boot configuration and securityfs input."""
ROWS=[
('Lockdown 단계 비교: 금지 사유를 순서대로 배치하는 이유','lockdown_is_locked_down',
 '커널의 내용을 바꾸지 못하게 하는 제한과 비밀 내용을 읽지 못하게 하는 제한은 목표가 다릅니다. 매번 수십 가지 기능을 개별 검사하는 대신 제한 사유를 정해진 순서로 배치하면 현재 수준과 한 번 비교해 결정할 수 있습니다.',
 'kernel_locked_down은 정적 변수라 초기값0인 NONE입니다. reason enum은 무결성 관련 사유들,INTEGRITY_MAX,기밀성 관련 사유들,CONFIDENTIALITY_MAX 순서입니다. hook은 what>=CONFIDENTIALITY_MAX면 WARN과 EPERM을 반환합니다. 정상 사유는 현재수준>=what일 때 EPERM,그렇지 않으면0입니다. 거부 로그는 사유 문자열이 있을 때 rate limit을 적용해 출력합니다.',
 'INTEGRITY_MAX 상태에서는 그 앞에 있는 DEV_MEM을 거부하지만 뒤에 있는 KCORE는 이 hook에서 허용합니다. CONFIDENTIALITY_MAX 상태에서는 둘 다 거부합니다. 이 파일의0은 이 LSM이 막지 않았다는 뜻이고 다른 보안 검사·파일 권한까지 통과했다는 보장은 아닙니다. 실제 접근 기능은 각 호출자가 올바른 reason으로 hook을 호출해야 제한됩니다.',
 '경계 값과 호출 계약','NONE과 두 MAX는 모드 표시에도 쓰이는 경계 값입니다. 임의 숫자를 외부 사용자 요청에서 직접 reason으로 전달하는 API가 아닙니다. NONE을 검사 사유로 넘기면 현재>=0 비교 때문에 거부될 수 있으므로 정상 기능 사유와 모드값을 혼동하면 안 됩니다. 잘못된 상한 사유 검사는 현재 모드와 무관하게 먼저 수행됩니다.',
 ('integrity에서KCORE 사유는 이 hook만 보면 어떻게 되나요?','허용0입니다.','항상 EPERM입니다.','KCORE는 integrity 경계 뒤의 기밀성 사유이므로 현재수준>=사유가 거짓입니다.'),
 ('hook이0이면 모든 권한 검사를 통과했나요?','아닙니다.이 hook이 거부하지 않았다는 뜻입니다.','그렇습니다.이후 어떤 검사도 거부할 수 없습니다.','다른 LSM과 기능별 권한 판단은 별도입니다.')),
('Lockdown 전이: 같은 단계 재요청도 실패하는 단방향 상태','lock_kernel_down',
 '제한을 설정한 뒤 같은 실행 중에 임의로 낮출 수 있다면 제한 대상이 설정을 되돌려 우회할 수 있습니다. 이 setter는 강화 방향의 변경만 받아들이며 같은 값에 대한 재요청도 성공으로 취급하지 않습니다.',
 'lock_kernel_down은 현재>=요청이면 상태를 바꾸지 않고 EPERM입니다. 요청이 더 클 때만 대입하고 설정 출처를 로그로 남기며0을 반환합니다. early lockdown 매개변수는 integrity와 confidentiality 두 문자열만 받아 이 함수를 호출합니다. NULL이나 다른 문자열은 EINVAL입니다. 다만 인식한 문자열에서는 setter의 반환값을 전파하지 않고0을 반환합니다.',
 'NONE→integrity→confidentiality는 각 단계가 올라가므로 성공합니다. confidentiality→integrity와 integrity→integrity는 EPERM입니다. 커맨드라인 파서에 이미 적용한 단계 문자열을 다시 주면 setter가 거부하더라도 파서는 문자열을 인식했으므로0입니다. 문자열 해석 성공과 실제 상태 변경 성공을 구별해야 합니다.',
 '초기화와 동시성의 범위','lockdown_lsm_init은 FORCE_INTEGRITY 설정을 우선 검사하고 아니면 FORCE_CONFIDENTIALITY를 검사한 뒤 hooks를 등록합니다. early LSM 옵션에 따라 DEFINE_EARLY_LSM 또는 DEFINE_LSM을 사용합니다. 이 setter 자체에는 mutex나 compare-and-swap이 없으므로 비교·대입이 동시 호출까지 원자적으로 단조성을 보장한다고 확대해 말하면 안 됩니다.',
 ('integrity 상태에 다시integrity를 설정하면 setter는?','EPERM이며 상태는 유지됩니다.','0을 반환하며 성공입니다.','현재>=요청이라는 비교에 같은 값도 포함됩니다.'),
 ('인식한 커맨드라인 문자열에서 setter가 실패하면 파서도 같은 오류를 반환하나요?','아닙니다.이 파서는0을 반환합니다.','그렇습니다.모든 오류를 그대로 전달합니다.','호출 결과를 저장하거나 반환하지 않고 마지막return0에 도달합니다.')),
('Lockdown 읽기 파일: 대괄호와 파일 오프셋이 표현하는 상태','lockdown_read',
 '사용자가 현재 보안 모드를 확인하려면 가능한 모드와 선택된 모드를 구별할 수 있어야 합니다. 짧은 문자열을 파일 인터페이스로 제공하더라도 한 번에 전부 읽는다는 가정 없이 읽기 위치를 처리해야 합니다.',
 'read는 NONE,INTEGRITY_MAX,CONFIDENTIALITY_MAX 배열을 순회하고 각 모드의 label을 문자열 버퍼에 붙입니다. 현재와 같은 모드는 대괄호로 감싸고 나머지는 그대로 출력합니다. 마지막 공백을 줄바꿈으로 바꾼 뒤 simple_read_from_buffer에 사용자 버퍼·count·ppos와 문자열 길이를 넘깁니다.',
 '현재integrity라면 none [integrity] confidentiality 뒤에 줄바꿈이 붙습니다. count가5라면 helper는 현재 위치에서 최대5바이트를 전달하고 위치를 진행시킵니다. 다음 read는 이어지는 부분을 읽으며 끝에서는0을 반환합니다. 이 예제는 같은 상태가 유지된다는 가정입니다. 함수는 read 호출마다 표시 문자열을 새로 만듭니다.',
 '문자열 테이블과 고정 버퍼','임시 배열은80바이트이고 이 소스는 고정된 세 label을 sprintf로 붙입니다. security/security.c의 none·integrity·confidentiality 라벨을 함께 대조해야 길이와 출력 형태를 이해할 수 있습니다. 동적으로 임의 길이 라벨을 받아 안전하게 자르는 구현이라고 일반화하면 안 됩니다. 파일은 securityfs에 lockdown 이름과0644 권한으로 생성됩니다.',
 ('현재 모드를 표시하는 기호는?','해당 label의 대괄호입니다.','모든 label의 별표입니다.','현재수준==level 분기에서만[%s] 형태로 출력합니다.'),
 ('첫 read가 문자열 일부만 읽으면 다음 read는 항상 처음부터인가요?','아닙니다.ppos에 따라 이어서 읽습니다.','그렇습니다.문자열을 새로 만들어서 위치도0입니다.','버퍼 재생성과 파일의 읽기 위치는 서로 다른 상태입니다.')),
('Lockdown 쓰기 파일: 개행 제거·NUL 종료·성공 바이트 수','lockdown_write',
 '사용자 버퍼는 커널 문자열처럼 끝에 NUL이 있다고 가정할 수 없습니다. 또 명령줄 도구가 덧붙이는 개행을 그대로 비교하면 정상 모드 이름도 틀린 입력이 됩니다. 입력의 바이트 수와 해석된 문자열 길이를 분리해야 합니다.',
 'memdup_user_nul은 n바이트를 복사하고 종료 NUL을 마련하며 오류 포인터면 그대로 errno를 반환합니다. strlen으로 얻은 문자열 끝의 개행 하나만 제거합니다. 세 모드 label과 strcmp로 정확히 비교하고 일치한 level에 setter를 호출합니다. 마지막에 state를 해제하며 err가 있으면 오류,성공이면 원래n을 반환합니다.',
 'NONE에서 integrity와 개행 한 개를 쓰면 개행을 제외한 이름을 비교해 성공하고 반환값은 개행 포함10바이트입니다. integrity 뒤에 개행 두 개를 쓰면 하나만 제거돼 나머지가 남아 EINVAL입니다. none은 이름으로 인식하지만 초기NONE에서도 같은 단계이므로 setter가 EPERM입니다. 공백이나 대소문자도 자동 정규화하지 않습니다.',
 '중간 NUL과 실제 입력 해석','입력 바이트가 integrity 다음 NUL 다음 다른 문자들이면 strlen과 strcmp는 첫 NUL까지만 봅니다. 이 함수에는 중간 NUL 뒤 데이터의 별도 거부 검사가 없습니다. 전이가 성공하면 반환값은 뒤 데이터를 포함해 전달된 원래n입니다. 따라서 성공 바이트 수만 보고 모든 바이트가 모드 이름 검사에 쓰였다고 판단하면 안 됩니다.',
 ('integrity와 개행1개의 성공 write 반환값은?','10입니다.','9입니다.','비교할 때 개행은 제거하지만 반환은 입력받은 원래n입니다.'),
 ('개행2개를 붙이면 둘 다 자동 제거되나요?','아닙니다.끝의 하나만 제거합니다.','그렇습니다.모든 공백과 개행을 제거합니다.','if 한 번으로 마지막문자 하나를 처리하며 반복 trim은 없습니다.')),
]

def register(topic,q,detail):
 for title,symbol,why,principle,use,dt,body,qa,qb in ROWS:
  topic(title,'격리·보안','security/lockdown/lockdown.c',symbol,why,principle,use,
        '모드·기능별 사유·문자열 인식·실제 상태 전이·파일 반환값을 나누어 추적하세요.',
        q(title+' · '+qa[0],*qa[1:]),q(title+' · '+qb[0],*qb[1:]),
        details=[detail(dt,body),detail('검토 범위','Linux v6.12 lockdown.c 전체와 security.h의 사유 enum,security.c의 label 배열을 대조했습니다. LSM 등록 매크로 내부·모든 기능별 호출부·Secure Boot 연동·실제 보안 모드 변경 실험은 이 파일 해설과 별도 범위입니다. securityfs 생성 오류는 PTR_ERR_OR_ZERO로 초기화 호출자에게 반환됩니다.')])
