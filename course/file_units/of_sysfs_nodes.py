"""Whole-file OF node/property sysfs lifecycle."""
ROWS = [dict(
    path='drivers/of/kobj.c', title='OF sysfs: 속성 파일·이름 충돌·노드 참조 수명',
    intro='노드 상태,속성 읽기와 생성·삭제·갱신,노드 attach/detach 전체를 분석합니다.',
    principle='메모리 객체의 초기화,sysfs 노출,참조 보유는 서로 다른 상태입니다.',
    use='intrusive 구조,부분 읽기,이름 충돌,권한 비트와 부분 실패를 학습합니다.',
    area='sysfs · kobject · 문자열 · 참조 수명 · 오류 처리',
    sections=[
        ('초기화와 부착 상태', 'GPL-2.0 파일은 OF,slab과 내부 OF 헤더를 포함합니다. initialized helper는 node가 nonNULL이고 kobj.state_initialized인지,공개 attached helper는 state_in_sysfs인지 검사합니다. 메모리 객체 초기화와 sysfs 존재를 같은 상태로 보지 않습니다. OF_DYNAMIC 비활성일 때 release는 빈 함수이며 주석은 이 구성에서 노드를 해제하지 않는다고 설명합니다. of_node_ktype은 release callback을 연결합니다.'),
        ('속성의 부분 읽기', 'property_read는 bin_attribute 주소에서 container_of로 property를 얻습니다. memory_read_from_buffer에 출력 buf,count,지역 offset 주소와 pp->value,pp->length를 전달합니다. 속성을 문자열로 다시 포맷하거나 별도 NUL을 붙이는 코드가 아니라 원래 바이트 데이터의 범위 읽기입니다. file과 kobject 인수는 본문에서 사용하지 않습니다.'),
        ('이름 충돌 검색', 'safe_name은 원래 이름으로 sysfs_get_dirent를 호출해 충돌을 확인하고 얻은 kernfs 참조를 sysfs_put합니다. 충돌할 때 이전 임시 이름을 해제하고 orig#1,orig#2처럼 kasprintf로 만듭니다. i<16 제한 때문에 최대 #16을 생성하지만 그 마지막 이름의 부재까지 다시 확인하지는 않습니다. 따라서 항상 유일한 이름을 보장한다고 단정할 수 없습니다.'),
        ('이름 저장소와 실패', '충돌이 없으면 원래 문자열도 kstrdup하여 호출자가 해제할 새 이름을 반환합니다. 충돌 경로는 경고를 출력합니다. 반복 내부 kasprintf 실패를 즉시 검사하는 분기가 없으므로 반복 중 모든 OOM이 안전하게 처리된다고 설명하면 안 됩니다. 최종 NULL 결과의 처리는 호출 지점마다 다릅니다.'),
        ('속성 생성과 security 접두부', 'add_property는 이름이 security-로 시작하는지 strncmp 길이 9로 검사합니다. SYSFS 비활성 또는 of_kset 부재·노드 미부착이면 0으로 끝납니다. bin attr를 초기화하고 safe_name,권한 secure?0400:0444,크기 secure?0:pp->length와 read callback을 설정합니다. 이는 패스워드를 누출하지 말라는 주석의 정책이며 pp->value 자체를 지우는 코드는 아닙니다.'),
        ('속성 생성 오류', 'sysfs_create_bin_file의 rc를 WARN으로 알리고 그대로 반환합니다. add_property에는 safe_name NULL을 별도 -ENOMEM으로 처리하거나 생성 실패 즉시 이름을 kfree하는 분기가 없습니다. 노드 attach 경로의 이름 검사와 동일하다고 추정하면 안 됩니다.'),
        ('속성 삭제의 두 단계', 'remove_bin_file은 SYSFS 비활성이면 반환하고 아니면 sysfs 파일 제거 후 attr.name을 kfree합니다. 일반 remove_property는 of_kset이 있고 노드가 부착된 경우에만 이를 호출합니다. 초기에 아직 sysfs가 준비되지 않으면 of_init에 setup을 미루는 주석이 있습니다. 속성 데이터 객체 자체를 여기서 kfree하는 것은 아닙니다.'),
        ('속성 갱신은 원자적 교체가 아님', 'update_property는 of_kset이 없으면 반환합니다. oldprop가 있으면 제거하고 새 속성을 추가하지만 add의 반환값을 사용하지 않습니다. 기존 속성을 유지한 채 새 파일 생성 성공을 확인하는 transaction이나 rollback은 없습니다. old 제거 전 attached 검사는 이 함수에 직접 없으므로 호출자와 하위 helper 계약도 구분해야 합니다.'),
        ('노드 attach의 이름과 부모', 'attach는 SYSFS 비활성 또는 of_kset 부재이면 0입니다. kobj.kset을 지정하고 parent가 없으면 kset 아래 base의 safe_name을 얻어 parent=NULL로 kobject_add에 전달합니다. parent가 있으면 full_name의 kbasename을 부모 kobject 아래에서 안전한 이름으로 만듭니다. 이름 NULL이면 -ENOMEM이고 kobject_add 뒤에는 임시 이름을 항상 kfree합니다.'),
        ('Attach의 부분 성공과 참조', 'kobject_add 오류는 반환합니다. 성공하면 모든 property를 순회해 add_property하지만 각 반환값은 무시합니다. 이후 of_node_get으로 노드 참조를 보유하고 0을 반환합니다. 따라서 attach의 0이 모든 속성 파일 생성 성공까지 증명하지 않습니다. kobject 생성과 개별 attr 생성은 별도 단계입니다.'),
        ('Detach', 'detach는 먼저 initialized가 아닌 경우 BUG_ON을 실행합니다. of_kset이 없으면 반환합니다. attached이면 모든 속성 파일을 제거하고 kobject_del합니다. 그 뒤 attached 여부와 무관하게 of_node_put합니다. 노드 초기화 확인보다 앞서 안전한 NULL no-op 처리를 하는 함수가 아니며,임의 중복 detach가 참조 수명에 무해하다고 볼 수 없습니다.'),
        ('전체 범위와 검증', '두 상태 helper,조건부 release,kobj type,read,safe_name,네 속성 관리 함수와 attach/detach를 모두 대조했습니다. 이 파일이 자체 잠금으로 모든 동시 갱신을 직렬화하는 코드는 없습니다. 실제 sysfs 파일 접근·OOM·동시 노드 삭제 실험은 실행하지 않았습니다.')
    ], questions=[
        ('state_initialized와 state_in_sysfs가 같은 의미인가?', '아니다. 객체 초기화와 sysfs 노출 상태다', '그렇다. 언제나 같은 필드의 별명이다', '각 helper가 서로 다른 kobject 필드를 확인합니다. 수명 단계와 노출 상태를 구분합니다.'),
        ('safe_name이 #16까지 만들면 그 이름의 유일성도 반드시 확인되는가?', '아니다. 다음 반복의 i<16 조건이 실패해 확인하지 않는다', '그렇다. 제한 없이 고유 이름이 나올 때까지 반복한다', '루프 횟수 제한과 생성·확인 순서를 따라야 합니다. 최대 시도는 성공 보장이 아닙니다.'),
        ('security- 속성의 mode와 attr.size는?', '0400과 0', '0444와 원래 길이', 'secure 조건으로 두 필드를 모두 바꿉니다. 원래 메모리 데이터 자체를 삭제하는 것은 아닙니다.'),
        ('노드 attach가 0이면 모든 속성 생성도 성공했는가?', '그렇게 보장할 수 없다. 속성 추가의 rc를 무시한다', '그렇다. 속성 하나 실패하면 항상 rollback한다', 'kobject_add 오류는 반환하지만 property 순회의 반환값은 사용하지 않습니다.'),
        ('속성 update에서 새 파일 추가 실패 시 기존 파일을 되살리는가?', '아니다. 기존 제거 후 추가하며 rollback이 없다', '그렇다. 자동 원자적 교체다', 'remove와 add 호출만 있고 결과 검사·복원 코드는 없습니다.'),
        ('property_read는 속성을 문자열로 변환하는가?', '아니다. 원래 value 바이트를 부분 읽기한다', '그렇다. 항상 JSON으로 직렬화한다', 'memory_read_from_buffer에 원본 포인터와 길이를 전달합니다. 형식 변환 호출은 없습니다.'),
        ('detach는 미초기화 노드에 대해 조용히 반환하는가?', '아니다. 첫 단계의 BUG_ON 대상이다', '그렇다. 상태 검사를 모두 생략한다', 'of_kset 검사 전에 초기화 불변식을 확인합니다. NULL 입력도 initialized helper에서 false가 됩니다.')
    ]
)]
