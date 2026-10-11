"""Whole-file vDSO sequence helpers and architecture update declarations."""
ROWS = [dict(
    path='include/vdso/helpers.h', title='vDSO sequence: 홀수 writer와 재시도 reader',
    intro='읽기 시작·재검사와 쓰기 시작·종료 네 함수의 장벽 위치를 전체 소스로 분석합니다.',
    principle='읽는 동안 자료가 바뀌었는지 sequence로 검출하고, 데이터 접근과 sequence 관측의 순서를 장벽으로 연결합니다.',
    use='공유 시간 데이터의 reader가 잠금을 잡지 않고 불일치한 표본을 버리는 원리를 이해합니다.',
    area='동시성 · sequence counter · 메모리 장벽 · 컴파일러 접근 · 재시도 · writer 직렬화',
    sections=[
        ('파일 전체와 assembly 분기', 'GPL-2.0과 guard 안에서 __ASSEMBLY__가 아닐 때만 barrier/datapage를 include하고 네 static __always_inline 함수를 정의합니다. assembly 문맥에서는 이 C 함수 본문이 노출되지 않습니다. 자체적으로 데이터 저장소나 writer spinlock을 정의하는 헤더는 아닙니다.'),
        ('Read begin의 홀수 검사', 'vdso_read_begin은 READ_ONCE(vd->seq)로 u32 sequence를 읽고 최하위 비트가 1인 동안 cpu_relax하며 반복합니다. 짝수를 얻은 뒤 smp_rmb를 실행하고 그 sequence를 반환합니다. cpu_relax는 scheduler sleep이나 잠금 획득이 아닙니다. writer가 끝나지 않으면 reader가 기다릴 수 있습니다.'),
        ('Read retry의 순서', 'vdso_read_retry는 먼저 smp_rmb를 수행한 뒤 sequence를 READ_ONCE로 다시 읽어 start와 다른지 반환합니다. 반환형은 u32이지만 실제 반환식은 != 비교 결과입니다. 함수가 데이터를 다시 읽어 주지는 않으므로 true이면 호출자가 데이터 취득부터 다시 해야 합니다. 여기서 현재 sequence의 홀짝을 따로 검사하지 않습니다.'),
        ('Writer의 시작', 'vdso_write_begin은 vd[CS_HRES_COARSE].seq와 vd[CS_RAW].seq를 각각 하나 증가시켜 WRITE_ONCE로 저장하고 그 다음 smp_wmb를 실행합니다. 직렬화되고 짝수에서 시작하는 writer 규약 아래 홀수로 바뀌어 갱신 중임을 알립니다. 두 항목을 하나의 원자적 다중 워드 저장으로 갱신하는 것은 아닙니다.'),
        ('Writer의 종료', 'vdso_write_end는 smp_wmb를 먼저 실행한 뒤 같은 두 sequence를 하나씩 증가시킵니다. 데이터 쓰기가 완료 표시보다 앞서도록 연결하고 홀수에서 다시 짝수로 돌아갑니다. 시작과 종료에서 장벽이 증가 연산의 서로 반대쪽에 있는 이유가 중요합니다.'),
        ('WRITE_ONCE와 증가의 차이', '주석은 컴파일러가 sequence 저장을 쪼개 reader가 불일치한 값을 볼 수 있으므로 WRITE_ONCE가 필요하다고 설명합니다. 그러나 실제 식은 기존 seq+1의 저장이며 atomic_fetch_add가 아닙니다. 두 writer의 read-modify-write 경쟁까지 방지하는 writer 직렬화는 호출자 책임입니다.'),
        ('Reader의 예제', 'reader가 start=10을 얻고 자료를 읽는 동안 writer가 11로 시작해 12로 끝내면 retry는 12!=10이므로 참입니다. writer가 아직 11이라도 달라졌으므로 참입니다. writer 없이 여전히 10이면 거짓입니다. 이 규약은 같은 데이터 묶음의 쓰기가 sequence 안에서 이루어진다는 전제를 필요로 합니다.'),
        ('데이터 묶음과 범위', 'read 함수는 인자로 받은 vd 하나의 seq를 관측하고 write 함수는 두 clocksource 묶음을 갱신합니다. 호출자가 임의의 서로 다른 데이터·sequence를 섞어도 자동으로 전역 스냅샷이 되는 것은 아닙니다. u32 sequence가 무한 증가하는 정수인 것도 아니며 이 짧은 코드만으로 임의로 긴 reader 정지와 모든 wrap 시나리오를 증명하지 않습니다.'),
        ('검증 범위', '네 함수의 모든 루프·식·장벽과 전처리 경계를 설명했습니다. 메모리 장벽이 writer lock을 대신한다는 오해, 개별 접근과 원자적 증가의 차이, 재시도하는 reader의 책임을 학습합니다. 실제 아키텍처 메모리 모델별 실행이나 모든 vDSO reader 경로를 검증한 결과는 아닙니다.')
    ],
    questions=[
        ('vdso_read_begin이 홀수 sequence를 보면?', 'cpu_relax하며 짝수를 관측할 때까지 반복한다', '그 값을 바로 반환하고 자료를 정상으로 취급한다', '홀수는 직렬화된 writer의 갱신 중 표시입니다. 짝수를 얻은 뒤 읽기 장벽을 실행합니다.'),
        ('start=10이고 자료를 읽은 뒤 seq=12이면?', 'retry가 참이며 호출자가 다시 읽어야 한다', '짝수이므로 무조건 성공이다', '짝수는 갱신 완료를 뜻할 수 있지만 reader가 읽는 중 갱신이 있었는지는 시작값과 비교해야 합니다.'),
        ('WRITE_ONCE로 seq+1을 저장하면 여러 writer도 자동 직렬화되는가?', '아니다. 원자적 증가나 writer lock이 아니다', '그렇다. WRITE_ONCE가 모든 writer에게 배타적 잠금을 준다', '주석은 저장 tearing 방지를 설명합니다. read-modify-write 전체의 동시성은 별도 규약입니다.'),
        ('vdso_write_end의 장벽 위치는?', 'sequence를 증가시키기 전이다', '두 sequence 증가가 끝난 뒤뿐이다', '이전 데이터 쓰기를 완료 표시보다 앞에 두기 위한 순서입니다. write_begin에서는 증가 뒤에 장벽이 있습니다.')
    ]
), dict(
    path='include/vdso/vsyscall.h', title='vDSO 갱신 선언: 아키텍처 연결과 IRQ flags 전달',
    intro='assembly 제외 조건과 아키텍처 include, begin/end 두 선언을 전체 범위로 읽습니다.',
    principle='공통 갱신 API와 아키텍처별 지원을 연결하되 호출자가 시작·종료 구간과 반환 상태를 정확히 짝지어야 합니다.',
    use='vDSO 데이터를 수정하는 아키텍처 코드가 사용하는 내부 인터페이스를 파악합니다.',
    area='헤더 계층 · 아키텍처 추상화 · 자원 구간 · 인터럽트 상태',
    sections=[
        ('전체 파일', 'GPL-2.0과 __VDSO_VSYSCALL_H guard 안에 __ASSEMBLY__ 제외 조건이 있습니다. C 문맥에서 asm/vdso/vsyscall.h를 포함한 뒤 두 함수만 선언합니다. 자체 데이터 구조나 inline 구현은 없습니다.'),
        ('아키텍처 include', 'asm/vdso/vsyscall.h가 플랫폼별 연결을 제공합니다. 이 공통 파일을 읽었다고 모든 아키텍처 hook의 구현을 읽은 것은 아닙니다. __ASSEMBLY__ 조건은 함수 선언뿐 아니라 해당 include에도 적용됩니다.'),
        ('Begin과 end 시그니처', 'vdso_update_begin은 인자 없이 unsigned long을 반환하고 vdso_update_end는 unsigned long flags를 받아 void입니다. 관련 kernel/time/vsyscall.c의 계약에 따르면 반환값은 저장된 interrupt 상태이며 end에 전달해야 합니다. 임의로 0을 넘기거나 단순 성공 코드로 해석하면 안 됩니다.'),
        ('선언과 동작의 분리', '실제 begin은 writer 잠금·IRQ 보호와 sequence 시작을, end는 sequence 종료·아키텍처 sync·잠금 해제·IRQ 복원을 수행합니다. 이 헤더는 그 함수를 선언할 뿐 자동으로 구간을 열지 않습니다. include guard도 런타임 중첩 호출이나 begin/end 누락을 방지하지 않습니다.')
    ],
    questions=[
        ('vdso_update_begin의 반환값은 무엇으로 사용해야 하는가?', '대응하는 vdso_update_end에 전달할 저장된 IRQ flags로 사용한다', '0이면 실패, 1이면 성공인 bool로만 사용한다', '관련 구현과 함수 선언의 flags 인자가 연결됩니다. 원래 interrupt 상태 복원에 필요한 값입니다.'),
        ('__ASSEMBLY__이면 이 파일에서 아키텍처 vsyscall 헤더를 포함하는가?', '아니다. 그 include도 C 문맥 조건 안에 있다', '그렇다. 함수 선언만 제외하고 include는 항상 실행한다', '조건부 전처리 경계가 include와 두 선언을 모두 둘러쌉니다.')
    ]
)]
