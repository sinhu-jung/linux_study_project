"""Whole-file RISC-V CPU query and time architecture hooks."""
ROWS = [dict(
    path='arch/riscv/kernel/vdso/getcpu.S',
    title='RISC-V vDSO getcpu: syscall을 호출하는 공개 진입점',
    intro='짧은 어셈블리 전체와 CFI 범위를 분석합니다.',
    principle='vDSO라는 위치가 항상 커널 진입 없는 처리를 보장하는 것은 아닙니다.',
    use='a7 syscall 번호와 인수·반환 레지스터를 변경하는 범위를 구별합니다.',
    area='RISC-V ABI · ecall · vDSO · CFI · 함수 경계',
    sections=[
        ('전체 구조', 'GPL-2.0-only와 SiFive 저작권 뒤 linux/linkage.h와 asm/unistd.h를 포함하고 .text로 이동합니다. 주석의 인터페이스는 int __vdso_getcpu(unsigned *cpu,unsigned *node,void *unused)입니다. SYM_FUNC_START와 SYM_FUNC_END가 심볼 범위를 정의합니다.'),
        ('세 실제 명령', 'li a7,__NR_getcpu로 시스템 호출 번호를 넣고 ecall을 실행한 뒤 ret로 호출자에게 돌아갑니다. 주석은 현재로서는 syscall만 수행한다고 명시합니다. x86의 LSL/RDPID 조회처럼 이 파일에서 CPU·node 값을 직접 추출하는 코드가 아닙니다.'),
        ('인수와 결과의 전달', '본문은 인수를 다시 복사하거나 출력 포인터를 역참조하지 않습니다. RISC-V 호출 문맥에서 전달된 cpu·node 인수를 syscall이 사용하며 반환값을 별도로 검사·변환하지 않고 반환합니다. libc errno를 설정하거나 무조건 성공값 0으로 바꾸는 코드도 없습니다. 세 번째 인수는 주석상 unused입니다.'),
        ('활성 CFI와 범위', '.cfi_startproc와 .cfi_endproc는 여기서 활성 어셈블러 지시문입니다. ARM64 sigreturn 파일의 주석 처리된 CFI와 다릅니다. 함수 경계 메타데이터가 있다고 이 파일이 임의 시그널 프레임을 직접 복원하는 것은 아닙니다. 전체 코드와 주석을 대조했으며 실제 RISC-V syscall 실행 시험은 하지 않았습니다.')
    ],
    questions=[
        ('이 RISC-V __vdso_getcpu는 커널 진입 없이 CPU 번호를 직접 읽는가?', '아니다. __NR_getcpu를 넣고 ecall한다', '그렇다. vDSO 함수는 정의상 syscall을 절대 사용하지 않는다', '주석과 실제 세 명령이 syscall 경로임을 보여줍니다. vDSO의 존재와 모든 요청의 빠른 사용자 공간 처리는 별개입니다.'),
        ('syscall 번호를 넣는 레지스터는?', 'a7이다', 'a0이다', 'li a7,__NR_getcpu가 번호를 지정합니다. 본문은 결과를 별도로 0으로 바꾸지 않고 ret로 돌아갑니다.')
    ]
), dict(
    path='arch/riscv/include/asm/vdso/gettimeofday.h',
    title='RISC-V vDSO 시간 hook: ecall fallback과 CSR_TIME',
    intro='설정별 세 syscall helper와 카운터·공유 데이터 getter를 전체 분석합니다.',
    principle='아키텍처별 시간 인터페이스는 syscall ABI, 빌드 기능, 카운터 읽기의 실행 문맥을 함께 고려해야 합니다.',
    use='설정 조건의 실제 범위와 인수 레지스터, 순서 보장에 관한 원본 주석의 한계를 설명합니다.',
    area='RISC-V · CSR · ecall · 조건부 컴파일 · namespace · 메모리 순서',
    sections=[
        ('전체 포함과 조건', 'GPL-2.0 include guard와 !__ASSEMBLY__ 아래 asm/barrier.h, asm/unistd.h, asm/csr.h, uapi/linux/time.h를 포함합니다. CONFIG_GENERIC_TIME_VSYSCALL 안에 VDSO_HAS_CLOCK_GETRES=1과 세 fallback 함수를 둡니다. 주석은 32비트 환경의 generic time vsyscall과 구형 시간 syscall 부족을 이유로 설명하지만 실제 전처리 조건은 CONFIG_64BIT가 아니라 이 기능 설정입니다.'),
        ('Gettimeofday fallback', '__kernel_old_timeval 포인터는 a0, timezone 포인터는 a1, __NR_gettimeofday는 a7에 연결합니다. asm volatile ecall의 결과를 a0의 long ret로 받고 int로 반환합니다. memory clobber가 있으며 buffer 복사나 NULL 처리 정책을 별도로 구현하지 않습니다. 반환값을 libc errno로 포장하는 코드도 없습니다.'),
        ('Clock_gettime fallback', 'clockid_t를 a0, __kernel_timespec 포인터를 a1, __NR_clock_gettime를 a7에 놓고 ecall합니다. long ret를 long으로 반환합니다. type과 포인터는 이 함수의 호출 계약이며 실제 clock ID별 지원 판단은 커널 처리와 공통 코드에 속합니다.'),
        ('Clock_getres fallback', 'a0의 clockid_t, a1의 __kernel_timespec 포인터 배치는 같고 번호는 __NR_clock_getres입니다. ret 변수는 long, 함수 반환형은 int입니다. 세 helper는 모두 memory clobber를 쓰지만 그 표현이 하드웨어 fence 명령 자체는 아닙니다. 이 파일에 clock_gettime32_fallback 같은 별도 구형 wrapper는 없습니다.'),
        ('조건부 밖의 카운터 함수', '__arch_get_hw_counter(s32 clock_mode,const vdso_data *vd)는 CONFIG_GENERIC_TIME_VSYSCALL 블록 바깥에 있으며 csr_read(CSR_TIME)을 반환합니다. clock_mode와 vd는 본문에서 사용하지 않습니다. NONE을 0이나 U64_MAX로 별도 변환하는 분기도 없습니다. 함수 반환형은 u64지만 이 한 줄을 보고 모든 빌드의 native CSR 폭과 읽기 구현까지 동일하다고 일반화하지 않습니다.'),
        ('Fence가 없는 이유에 관한 주석', '원본 주석은 CSR_TIME을 얻기 위해 M-mode로 trap하는 문맥을 설명하며 다른 아키텍처와 달리 csr_read 주변에 fence를 넣지 않았다고 말합니다. 실제 본문에도 별도 fence 호출은 없습니다. 이 역사적 설명을 모든 RISC-V 구현과 가상화 환경에서 TIME 읽기가 언제나 같은 trap 경로를 따른다는 보편적 명제로 확대하지 않습니다. 정확한 CSR 접근과 실행 환경은 관련 구현을 더 확인해야 합니다.'),
        ('공유 시간 데이터 getter', '__arch_get_vdso_data는 _vdso_data를 반환합니다. CONFIG_TIME_NS 아래 __arch_get_timens_vdso_data는 vd를 사용하지 않고 _timens_data를 반환합니다. 이 함수들은 주소를 제공하며 페이지를 할당하거나 namespace offset을 직접 더하지 않습니다. 설정이 꺼진 경우의 namespace getter stub는 이 파일에 없습니다.'),
        ('CS 연결과 전체 범위', '세 syscall helper, 두 getter, 카운터 함수, 기능 매크로와 모든 전처리 구역을 다뤘습니다. a0·a1·a7 호출 계약, 기능 설정과 아키텍처 비트 폭의 구별, 카운터 값과 시간 환산의 분리가 핵심입니다. 실제 RISC-V 하드웨어나 에뮬레이터 실행 검증은 수행하지 않았습니다.')
    ],
    questions=[
        ('세 시간 fallback의 실제 빌드 조건은?', 'CONFIG_GENERIC_TIME_VSYSCALL이다', '조건 없이 모든 32비트·64비트 빌드에 정의된다', '원본은 해당 기능 설정으로 함수들을 감쌉니다. 주석의 32비트 설명과 실제 #ifdef 이름을 구분해야 합니다.'),
        ('__arch_get_hw_counter가 clock_mode==NONE이면 별도로 반환하는 오류 값은?', '그런 분기가 없다. 본문은 CSR_TIME 읽기만 반환한다', '항상 U64_MAX이다', 'x86의 다른 구현을 그대로 대입해서는 안 됩니다. 이 함수에서는 clock_mode와 vd 인수를 사용하지 않습니다.'),
        ('clock_gettime fallback의 출력 포인터와 syscall 번호는 어디에 있는가?', '출력 포인터는 a1, 번호는 a7이다', '출력 포인터는 a7, 번호는 a1이다', 'a0은 clock ID와 반환값에 사용됩니다. register 변수의 명시적 연결을 읽어 호출 규약을 파악합니다.'),
        ('namespace getter가 직접 시간 offset을 더하는가?', '아니다. _timens_data 주소를 반환한다', '그렇다. vd의 초·나노초를 즉시 변경한다', '본문은 주소 반환뿐입니다. 공유 데이터 접근과 실제 시간 계산은 별개의 책임입니다.')
    ]
)]
