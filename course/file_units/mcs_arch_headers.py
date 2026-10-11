"""Whole MCS architecture customization headers."""
ROWS = []


def add(path, title, intro, principle, use, sections, questions):
    ROWS.append(dict(path=path, title=title, intro=intro, principle=principle,
                     use=use, area='아키텍처 추상화 · 메모리 장벽 · 이벤트 대기 · MCS',
                     sections=sections, questions=questions))


add('arch/arm/include/asm/mcs_spinlock.h', 'ARM MCS 대기 헤더 전체: WFE와 이벤트 알림',
    'ARM의 SMP 구성에서 MCS 경합 대기와 인계를 아키텍처별 매크로로 대체합니다.',
    '플래그의 acquire/release 순서와 CPU 이벤트 대기·알림을 결합합니다. 이벤트에서 깨어났다는 사실만으로 소유권을 인정하지 않고 플래그를 다시 읽습니다.',
    '이 파일은 ARM용이며 ARM64 파일이라고 부르지 않습니다. 실제 큐 연결은 generic MCS 구현이 담당하고 여기서는 경합 플래그 대기와 인계만 바꿉니다.',
    [('전체 구성', 'GPL-2.0과 guard 안에 CONFIG_SMP 분기, asm/spinlock.h 포함, arch_mcs_spin_lock_contended와 unlock_contended 두 매크로가 전부입니다. SMP가 아니면 이 파일에서 두 매크로를 정의하지 않으므로 포함 측 generic fallback과 연결해 읽어야 합니다.'),
     ('대기 전 장벽', 'lock_contended는 먼저 smp_mb를 실행합니다. 주석은 WFE에 들어가기 전에 앞선 저장이 관측되도록 하기 위한 것이라고 설명합니다. 이 단계와 반복 안의 acquire 읽기는 목적이 다르므로 acquire 하나만 있으면 앞선 장벽이 불필요하다고 임의로 결론 내리지 않습니다.'),
     ('플래그와 WFE 루프', 'smp_load_acquire(lock)가0인 동안 wfe를 실행하고 다시 검사합니다. 처음부터1이면 WFE 없이 통과합니다. WFE는 커널 태스크를 대기 큐에 넣어 schedule하는 함수와 다르며, 이벤트 발생이 곧 플래그 참이라는 뜻도 아닙니다. 실제 획득 판정은 acquire 읽기 결과입니다.'),
     ('인계와 알림', 'unlock_contended는 smp_store_release(lock,1) 뒤 dsb_sev를 호출합니다. 데이터 순서를 가진 플래그 저장과 이벤트 알림을 함께 제공하는 구조입니다. 이 헤더에는 dsb_sev 자체의 본문이 없으므로 그 내부 명령 나열까지 여기에서 직접 검증했다고 주장하지 않습니다.'),
     ('generic 연결과 CS', 'generic MCS 헤더는 아키텍처 매크로가 없을 때만 기본 대기·인계 구현을 정의합니다. 이 파일은 큐 꼬리 교환이나 next 연결 알고리즘을 복제하지 않고 필요한 부분만 대체합니다. 조건 재검사, acquire/release, 장벽과 알림의 분리, 빌드 설정에 따른 fallback을 학습합니다. ARM에서 실제 실행한 검증은 아닙니다.')],
    [('WFE에서 돌아왔으면 잠금을 획득한 것인가?', '아니다. acquire로 읽은 플래그가 참인지 다시 확인한다', '그렇다. 이벤트는 언제나 자신의 잠금 인계만 의미한다', 'while 조건이 smp_load_acquire 결과를 재검사합니다. 알림과 조건 만족은 다른 사실이므로 깨어남만으로 임계구역에 들어가지 않습니다.'),
     ('인계 매크로의 순서는?', 'release로1 저장 후 dsb_sev 호출', '이벤트를 먼저 보내고 플래그 저장은 생략', '원문은 smp_store_release 다음 dsb_sev입니다. 플래그 상태와 이벤트 통지를 결합하며 후속 대기자가 플래그를 확인하도록 합니다.'),
     ('CONFIG_SMP가 꺼져도 이 파일이 동일한 경합 매크로를 정의하는가?', '아니다. 정의 전체가 CONFIG_SMP 안에 있다', '그렇다. SMP 분기는 주석에만 있다', '비SMP에서는 이 헤더의 override가 없어 generic MCS의 ifndef fallback을 함께 봐야 합니다.')])

add('include/asm-generic/mcs_spinlock.h', 'Generic MCS 아키텍처 헤더 전체: 기본 구현을 선택하는 빈 확장 지점',
    '아키텍처가 대기·인계 매크로를 대체할 수 있음을 문서화하는 최소 헤더입니다.',
    '구현을 정의하지 않는 것도 의도된 인터페이스입니다. 포함 측이 매크로 존재 여부를 검사해 기본 구현을 제공하므로 빈 헤더가 잠금 기능 부재를 뜻하지 않습니다.',
    '실행 코드는 kernel/locking/mcs_spinlock.h의 fallback과 함께 확인합니다. 주석의 과거 경로와 현재 파일 위치를 구별합니다.',
    [('전체 구성', 'include guard와 주석만 있고 구조체·함수·실행 매크로 정의는 없습니다. 주석은 arch_mcs_spin_lock_contended(l), arch_mcs_spin_unlock_contended(l) 두 확장 이름을 열거합니다. 이 파일 자체에는 SPDX 행이 없습니다.'),
     ('기본값 선택', '아키텍처에서 이 기본 헤더를 선택하면 두 이름을 미리 정의하지 않습니다. kernel/locking/mcs_spinlock.h의 ifndef 블록이 acquire 대기와 release 저장의 기본 구현을 제공합니다. 이 관계를 헤더만 보고 MCS가 비활성화되었다고 해석하면 안 됩니다.'),
     ('주석 참조 경로', '주석은 kernel/locking/mcs_spinlock.c를 가리키지만 이 버전에서 읽은 generic 구조체와 inline 알고리즘의 파일은 kernel/locking/mcs_spinlock.h입니다. 독자는 현재 트리의 실제 경로를 따라야 하며 존재하지 않는 참조 파일까지 작성 완료로 세지 않습니다.'),
     ('CS 연결', '아키텍처별 override와 generic fallback, 전처리 매크로의 존재 여부를 이용한 기능 선택, 문서 링크와 현재 구현 위치의 대조를 학습합니다. 파일이 짧아도 빌드 구조에서 맡는 역할은 별도 설명할 수 있습니다.')],
    [('이 헤더에 lock 함수가 없으면 MCS 잠금도 구현되지 않는가?', '아니다. 포함 측 generic 헤더가 기본 구현을 제공한다', '그렇다. 이 헤더를 쓰는 아키텍처는 MCS를 사용할 수 없다', '이 파일은 확장 지점만 남깁니다. kernel/locking/mcs_spinlock.h가 매크로 미정의 조건에서 실제 fallback을 정의합니다.'),
     ('주석의 mcs_spinlock.c 경로를 현재 구현 위치로 그대로 믿어도 되는가?', '아니다. 현재 트리에서 실제 mcs_spinlock.h 구현을 확인해야 한다', '그렇다. 주석의 모든 파일 링크는 자동 갱신된다', '문서화된 참조도 코드 이동 뒤 오래될 수 있습니다. 존재하는 원본 파일을 대조하는 것이 학습 범위와 구현 근거를 정확하게 유지하는 방법입니다.')])
