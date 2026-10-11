"""Whole-file generic vDSO random state machine and fallback handling."""
ROWS = [dict(
    path='lib/vdso/getrandom.c',
    title='vDSO 난수 구현: 배치 소비·키 교체·generation 재시도',
    intro='복사 후 삭제 helper와 공통 난수 함수 전체의 분기·상태 변화를 분석합니다.',
    principle='빠른 난수 구현은 바이트 생성뿐 아니라 키 수명, fork·메모리 소실, 재진입, 커널 재생성과의 동기화를 함께 관리해야 합니다.',
    use='호출의 정상·재시도·fallback 흐름을 추적하고 출력 배치와 다음 키가 갱신되는 시점을 설명합니다.',
    area='상태 기계 · 버퍼링 · 메모리 순서 · 재진입 · 키 삭제 · fork · syscall fallback',
    sections=[
        ('전체 의존성과 페이지 정의', 'GPL-2.0 아래 array_size·minmax, vDSO datapage·getrandom·unaligned, 아키텍처 getrandom, UAPI mman·random을 포함합니다. 기존 PAGE_SIZE와 PAGE_MASK를 undef하고 CONFIG_PAGE_SHIFT 기반으로 다시 정의합니다. 페이지 크기를 항상 4096으로 가정하지 않습니다. 함수는 사용자 공간에서 실행되는 vDSO 구현이며 커널의 사용자 메모리 복사 helper를 여기서 사용하지 않습니다.'),
        ('복사와 삭제 매크로', 'MEMCPY_AND_ZERO_SRC(type,dst,src,len)는 len이 type 크기 이상인 동안 unaligned getter와 setter로 값을 복사한 뒤 같은 source 위치를 0으로 덮습니다. dst와 src를 type 크기만큼 전진시키고 len을 감소시킵니다. 인수 변수를 실제로 변경하는 do-while 매크로이므로 일반적인 값 인수 함수처럼 해석하지 않습니다. 임의 겹치는 영역에 대한 memmove 계약은 없습니다.'),
        ('복사 helper의 크기별 경로', 'memcpy_and_zero_src는 효율적인 unaligned 접근 설정이 있으면 64BIT일 때 u64, 이어 u32·u16 순서로 처리하고 마지막에 항상 u8로 남은 바이트를 처리합니다. 설정이 없으면 처음부터 u8 경로입니다. 복사한 난수 배치 바이트를 남겨두지 않으려는 동작이지 모든 state 필드를 한 번에 삭제하는 함수가 아닙니다.'),
        ('입력과 로컬 상태', '__cvdso_getrandom_data는 rng_info와 buffer,len,flags,opaque_state,opaque_len을 받습니다. ret는 min(len, INT_MAX & PAGE_MASK)로 정한 빠른 경로의 최대 반환 길이입니다. orig_buffer·orig_len은 처음 요청을 보존하고 have_retried는 false, 8바이트 counter는 0으로 시작합니다. 뒤 fallback은 줄어든 len이 아니라 원래 요청을 사용합니다.'),
        ('특수 상태 조회가 먼저다', 'opaque_len==~0UL, buffer==NULL, len==0, flags==0이면 opaque_state를 vgetrandom_opaque_params로 보아 sizeof(state), PROT_READ|PROT_WRITE, MAP_DROPPABLE|MAP_ANONYMOUS를 기록하고 reserved를 모두 0으로 채운 뒤 0을 반환합니다. 이 조회는 일반 상태의 페이지 경계·크기 검사보다 먼저입니다. opaque_state가 유효한 쓰기 가능한 조회 결과 주소인지는 호출 계약에 속하며 여기서 NULL 검사를 하지 않습니다.'),
        ('페이지 경계와 상태 할당 계약', '일반 경로는 페이지 내 주소 offset+sizeof(state)가 PAGE_SIZE보다 크면 -EFAULT를 직접 반환합니다. opaque_len이 아니라 실제 상태 크기로 검사합니다. 주석은 페이지가 언제든 0으로 바뀔 수 있으므로 state가 페이지를 걸치면 안 된다고 설명합니다. 호출자는 조회된 mmap 설정으로 할당해야 하고 외부 잠금이 없다면 스레드별 상태를 사용해야 합니다.'),
        ('Fallback 전 검사 순서', '알려진 세 GRND 비트 외의 flags가 있으면 syscall로 갑니다. 이어 opaque_len이 sizeof(state)와 다르거나 rng_info->is_ready가 false여도 fallback입니다. 그 다음에야 len==0이면 0을 반환합니다. 커널 RNG 초기화 전에는 빈 요청도 flags에 따라 블록하거나 오류가 필요할 수 있어 이 순서가 중요합니다. 이 flags 검사는 미지 비트를 거르는 것이지 모든 비트 조합을 별도 분석하는 switch가 아닙니다.'),
        ('재진입 guard', 'READ_ONCE(state->in_use)가 true이면 state를 건드리지 않는 syscall로 갑니다. false이면 WRITE_ONCE로 true를 기록합니다. 주석은 같은 스레드의 signal 재진입 보호이며 여러 CPU에 대한 원자적 잠금이 아니라고 명시합니다. false를 읽은 뒤 true를 쓰기 전에 signal이 오더라도 handler가 완료된 다음 원래 실행으로 돌아오는 순서를 전제로 합니다. 이를 다중 스레드 공유 허용으로 확대하지 않습니다.'),
        ('Generation 확인과 키 교체 필요', 'retry_generation 라벨에서 항상 rng_info->generation을 READ_ONCE로 읽습니다. state->generation과 다르면 커널 재생성 일정에 맞추어 키를 다시 받습니다. 단지 로컬 current_generation을 계속 재사용하는 방식이 아니며, 커널 공유 generation이 상태 키의 수명과 연결됩니다.'),
        ('Generation을 먼저 쓰는 이유', 'state->generation에 current_generation을 먼저 WRITE_ONCE하고 smp_rmb를 수행한 뒤 syscall로 키를 받습니다. 주석은 fork 시 부모·자식이 같은 키와 generation 조합을 유효하다고 보게 되는 일을 피하기 위한 순서라고 설명합니다. barrier는 random.c의 generation release 게시와 짝을 이룹니다. 이 설명은 원본 프로토콜의 의도이며 이 파일 단독으로 fork 안전성을 실행 검증한 결과는 아닙니다.'),
        ('키를 받는 syscall과 실패', 'getrandom_syscall(state->key,sizeof(state->key),0)가 정확히 키 크기 32를 반환해야 합니다. flags는 원래 요청값이 아니라 0입니다. 오류뿐 아니라 짧은 결과도 실패로 취급하여 generation=0으로 무효화한 뒤 in_use=false를 마지막 상태 쓰기로 하고 원래 요청의 syscall로 전환합니다. 성공하면 pos를 batch 크기 96으로 두어 기존 배치를 소비하지 않고 새 키로 채우게 합니다.'),
        ('배치에서 먼저 소비', 'len=ret로 제한한 뒤 more_batch에서 batch_len=min(96-pos,len)을 계산합니다. 남은 배치가 있으면 memcpy_and_zero_src로 출력에 복사하면서 지우고 pos·buffer를 전진시키며 len을 줄입니다. state는 올바른 내부 상태라는 계약 아래 사용되며 pos<=96을 별도 검증하는 분기는 없습니다. 임의 변조한 state를 안전하게 파싱하는 함수는 아닙니다.'),
        ('완료 직전 generation 재확인', 'len이 0이 되면 compiler barrier 뒤 state->generation과 rng_info->generation을 다시 READ_ONCE로 비교합니다. 로컬 current_generation 대신 state를 다시 읽어 fork·메모리 압력에 의한 상태 소실과 커널 reseed를 감지하려는 구성입니다. 주석상 커널 generation은 0이 되지 않으므로 0으로 지워진 상태도 불일치로 드러납니다.'),
        ('한 번의 전체 재시도', '완료 검사에서 불일치가 처음이면 have_retried=true, buffer=orig_buffer로 복구하고 retry_generation으로 갑니다. 그곳을 거쳐 len도 ret로 다시 설정되므로 앞서 쓴 출력 범위를 다시 생성합니다. counter는 함수 진입 때 초기화한 변수이며 이 라벨에서 명시적으로 0으로 재설정하지 않습니다. 두 번째 불일치라면 in_use=false 후 syscall로 가므로 무한 generation 재시도를 피합니다.'),
        ('정상 반환의 마지막 상태 접근', 'generation이 일치하면 더는 state를 읽거나 쓰지 않을 시점에 in_use=false로 바꾸고 ret를 반환합니다. 동기화 대상인 전역 generation 자체를 이 함수가 증가시키는 것은 아닙니다. 이미 복사한 바이트를 소비하는 동안 state의 비밀 정보를 줄이려는 흐름과 재진입 guard 해제 순서를 함께 읽어야 합니다.'),
        ('큰 요청은 완전한 블록을 직접 출력', '배치 소비 후에도 len이 남으면 nblocks=len/64를 계산합니다. 양수이면 __arch_chacha20_blocks_nostack로 사용자 buffer에 완전한 블록들을 직접 생성하고 buffer·len을 조정합니다. 매 바이트를 반드시 96바이트 배치를 거쳐서만 출력하는 것은 아닙니다. 같은 호출의 counter가 이 생성과 뒤의 키 교체 생성에 이어 사용됩니다.'),
        ('두 블록 refill과 key erasure', 'BUILD_BUG_ON은 batch_key 크기가 64의 배수가 아닌 빌드를 거부합니다. 이어 두 블록 128바이트를 batch_key에 생성하여 앞 96바이트 batch와 뒤 32바이트 key를 함께 덮습니다. pos=0으로 만들고 more_batch로 돌아갑니다. 직접 출력만으로 남은 len이 이미 0이어도 이 refill을 거쳐 다음 키를 교체합니다. 복사된 배치 삭제와 키 덮어쓰기는 주석이 설명하는 forward secrecy를 위한 설계 요소이며 독립적인 암호 안전성 증명은 아닙니다.'),
        ('요청 길이 예시', '배치가 비어 있고 len=70이면 64바이트 한 블록을 출력에 직접 쓰고 128바이트 refill 뒤 새 batch에서 6바이트를 복사·삭제합니다. 완료 시 pos=6이고 나머지 90바이트 batch를 다음 호출에 쓸 수 있습니다. len=64이면 직접 한 블록을 쓰고도 refill을 수행하여 새 키와 batch를 준비한 뒤 완료 검사로 갑니다.'),
        ('Fallback과 최종 wrapper', 'fallback_syscall은 getrandom_syscall(orig_buffer,orig_len,flags)를 반환합니다. 앞서 부분 출력이나 재시도가 있어도 남은 부분만 요청하지 않고 원래 시작 주소와 길이를 전달합니다. 마지막 __cvdso_getrandom은 __arch_get_vdso_rng_data로 공유 RNG 정보를 얻고 다섯 인수를 data 함수로 위임합니다. 전체 매크로·helper·분기·라벨을 설명했으며 실제 mmap 소실, signal, fork 및 암호 출력의 실행 검증은 수행하지 않았습니다.')
    ],
    questions=[
        ('왜 len==0 검사가 RNG ready 확인보다 뒤인가?', '초기화 전에는 빈 요청도 flags에 따른 블록·오류 처리가 필요할 수 있기 때문이다', '빈 요청이면 언제나 RNG 상태와 관계없이 즉시 성공하기 때문이다', '원본 주석이 순서를 명시합니다. 준비되지 않았다면 먼저 syscall이 커널 정책을 처리하게 합니다.'),
        ('상태가 페이지 경계를 넘으면 어떤 경로인가?', '-EFAULT를 직접 반환한다', '크기만 맞으면 무조건 빠른 경로를 계속한다', '페이지 내 offset+sizeof(state)를 검사합니다. 페이지 단위로 상태 메모리가 지워질 수 있다는 할당 계약 때문에 경계를 걸치면 안 됩니다.'),
        ('키 갱신 syscall이 16바이트만 반환하면 성공인가?', '아니다. 32바이트 전체가 아니면 generation을 무효화하고 fallback한다', '그렇다. 반환이 양수이면 남은 키를 그대로 써도 된다', '조건은 반환값과 sizeof(key)의 정확한 일치입니다. 짧은 읽기도 유효한 키 갱신으로 인정하지 않습니다.'),
        ('완료 검사에서 generation이 연속 두 번 바뀌면?', '한 번 재시도 후 두 번째에는 syscall로 전환한다', '일치할 때까지 횟수 제한 없이 계속 재시도한다', 'have_retried가 한 번의 전체 재생성을 제한합니다. 메모리 압력이나 강제 reseed 경쟁 때문에 영원히 도는 상황을 피합니다.'),
        ('배치가 비어 있고 70바이트 요청이면 일반적인 출력 분할은?', '64바이트를 직접 생성하고 refill한 batch에서 6바이트를 복사한다', '70바이트 전부를 기존 빈 batch에서 읽는다', '완전한 블록은 직접 출력하고 남은 부분은 새 배치로 처리합니다. 새 key도 같은 refill에서 교체됩니다.'),
        ('직접 64바이트를 생성하여 len이 0이 되면 refill을 건너뛰는가?', '아니다. 키를 덮는 refill 후 more_batch의 완료 검사로 간다', '그렇다. len이 0이면 키를 그대로 둔 채 즉시 반환한다', '직접 블록 생성 아래에는 조건 없이 batch_key refill이 있습니다. 다음 키를 교체하는 동작까지 추적해야 합니다.'),
        ('Fallback은 이미 쓴 부분 뒤의 나머지 길이만 요청하는가?', '아니다. orig_buffer와 orig_len을 사용한다', '그렇다. 항상 현재 buffer와 남은 len만 전달한다', '원래 요청을 로컬 변수에 보존한 이유가 여기에 있습니다. 상태 처리 중 변경된 포인터와 길이를 그대로 fallback에 쓰지 않습니다.'),
        ('memcpy_and_zero_src가 하는 추가 작업은?', '복사한 source 바이트를 0으로 덮는다', '목적지를 0으로 덮고 원본은 보존한다', '출력 바이트를 사용자 buffer로 옮긴 다음 소비한 내부 batch 부분을 지워 상태에 남는 과거 출력을 줄입니다.')
    ]
)]
