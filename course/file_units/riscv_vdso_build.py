"""Whole-file RISC-V vDSO compilation, linking, and symbol filtering."""
ROWS = [dict(
    path='arch/riscv/kernel/vdso/Makefile',
    title='RISC-V vDSO 빌드: 객체 선택·임시 ELF·심볼 지역화',
    intro='Makefile 전체에서 객체 목록과 이미지·offset 생성의 의존성을 추적합니다.',
    principle='검사 도구를 include하는 것과 실제 빌드 명령에서 호출하는 것은 다르며, 단계별 심볼 정책도 함께 읽어야 합니다.',
    use='64비트 시간 객체 조건, objcopy 필터, 링크 후 단계의 성공 연결을 설명합니다.',
    area='Kbuild · GNU make · ELF linking · objcopy · 의존성 그래프 · 셸 종료 상태',
    sections=[
        ('전체 목록과 조건', 'GPL-2.0-only와 arch/tile에서 복사했다는 이력 뒤 lib/vdso/Makefile을 포함합니다. vdso-syms는 rt_sigreturn으로 시작하고 CONFIG_64BIT일 때만 vgettimeofday를 추가합니다. getcpu·flush_icache·hwprobe·sys_hwprobe는 이어 조건 없이 추가합니다. 이름은 파일 stem 목록이며 모든 항목이 같은 형태의 공개 함수 이름이라는 뜻은 아닙니다.'),
        ('객체와 경로 변환', 'obj-vdso는 patsubst로 각 stem에 .o를 붙이고 note.o를 더한 값입니다. targets에 객체와 vdso.so·vdso.so.dbg·vdso.lds를 저장한 뒤 obj-vdso 앞에 $(obj)/ 경로를 붙입니다. obj-y에는 이미지 포함용 vdso.o를 추가합니다. note.o가 명시적인 vdso-syms 항목 없이도 링크 목록에 들어가는 점을 구분합니다.'),
        ('C 컴파일 옵션', 'ccflags-y는 -fno-stack-protector, DISABLE_BRANCH_PROFILING, -fno-builtin입니다. c-gettimeofday-y가 비어 있지 않으면 vgettimeofday.o에 -fPIC과 공통 C 소스의 -include를 추가합니다. hwprobe.o에도 -fPIC을 줍니다. 두 객체의 CFLAGS_REMOVE는 FTRACE와 SCS 플래그를 제거합니다. 여기에는 ARM64 Makefile의 모든 추가·제거 옵션이 동일하게 나열되어 있지 않습니다.'),
        ('링커 스크립트 조건', 'CPPFLAGS_vdso.lds에는 -P -C -U$(ARCH)를 줍니다. vdso-syms에 vgettimeofday가 있으면 -DHAS_VGETTIMEOFDAY를 추가하여 링커의 시간 함수 export 조건과 연결합니다. 이 매크로는 실제 객체 선택 목록을 filter한 결과에 따라 생깁니다. 실행 시 CPU가 함수 목록을 고르는 방식이 아닙니다.'),
        ('이미지 포함 의존성', 'vdso.o는 vdso.so에 명시적으로 의존합니다. 앞서 확인한 vdso.S가 .incbin으로 그 이미지를 포함하므로 준비되지 않은 이미지를 사용하는 것을 피하는 빌드 연결입니다. 이 의존성 자체가 사용자 프로세스에 vDSO를 매핑하는 동작은 아닙니다.'),
        ('Dbg ELF 링크와 옵션', 'vdso.so.dbg는 vdso.lds, 객체 목록, FORCE 순서로 의존하며 if_changed,vdsold를 호출합니다. 주석은 .lds가 첫 번째여야 한다고 명시합니다. 타깃 LDFLAGS는 -shared, soname linux-vdso.so.1, sha1 build-id, --hash-style=both, --eh-frame-hdr입니다. SysV·GNU hash와 unwind header 생성 선택을 링크 스크립트의 관련 섹션과 함께 읽습니다. build-id는 서명 검증 자체가 아닙니다.'),
        ('임시 ELF와 objcopy 단계', 'cmd_vdsold는 LD에 -T와 FORCE를 제외한 prerequisite 목록을 주고 $@.tmp를 만듭니다. 성공하면 objcopy로 각 vdso-syms stem에 -G __vdso_접두어를 붙인 목록을 적용해 $@를 만들고 성공하면 임시 파일을 지웁니다. -G는 지정 이름들을 global로 남기는 심볼 지역화 정책이며 실제 이름과 version script를 함께 봐야 합니다. 예컨대 vgettimeofday는 세 시간 함수의 파일 stem이므로 이 변환 목록만으로 최종 동적 export가 세 이름과 일대일 대응한다고 단정하지 않습니다.'),
        ('셸 성공 연결과 strip', '세 링크 후 단계는 &&로 연결되어 앞 단계가 실패하면 뒤 단계를 실행하지 않습니다. rm은 여기서 생성한 임시 산출물 정리입니다. 별도의 %.so 타깃은 %.so.dbg를 입력으로 OBJCOPYFLAGS=-S와 if_changed,objcopy를 사용합니다. dbg 링크 단계의 -G 심볼 처리와 최종 .so의 strip 단계를 혼동하지 않습니다. 이 학습 작업에서는 이 recipe나 삭제 명령을 실행하지 않았습니다.'),
        ('Offset 헤더 생성', 'cmd_vdsosym은 NM의 $< 출력 → gen_vdso_offsets.sh → LC_ALL=C sort → $@ 저장입니다. include/generated/vdso-offsets.h의 첫 의존성은 vdso.so.dbg이며 FORCE와 if_changed를 함께 사용합니다. 따라서 추출 입력은 strip 전 dbg ELF입니다. FORCE만 보고 매번 무조건 동일 산출물을 다시 생성한다고 해석하지 않습니다.'),
        ('포함한 검사와 실제 호출의 차이', '처음 주석은 공통 Makefile을 built vdso 검사에 사용한다고 설명하지만 이 파일의 cmd_vdsold에는 cmd_vdso_check 호출이 없습니다. 공통 검사 명령이 정의되어 있다는 사실만으로 이 링크 recipe가 그것을 실행했다고 주장하면 안 됩니다. 외부 호출 여부는 다른 빌드 문맥을 추가로 확인해야 하며 여기서는 이 파일 안의 실행 경로만 분석합니다.'),
        ('범위와 CS 연결', '모든 변수·설정·타깃·명령과 주석을 다뤘습니다. 입력 목록을 여러 생성 규칙으로 바꾸는 make 함수, ELF 링크와 심볼 정책, 검사 정의와 실행의 차이가 핵심입니다. 실제 RISC-V 빌드나 nm·readelf로 최종 심볼과 재배치를 검증한 결과는 아닙니다.')
    ],
    questions=[
        ('vgettimeofday 객체를 목록에 넣는 실제 조건은?', 'CONFIG_64BIT가 정의된 경우이다', 'CONFIG_TIME_NS만 켜져 있으면 된다', 'vdso-syms 구성의 ifdef를 확인해야 합니다. namespace 데이터 여부와 시간 객체 빌드 조건은 다른 설정입니다.'),
        ('왜 vdso.o가 vdso.so에 의존하는가?', 'vdso.S가 만들어진 ELF를 incbin으로 포함하기 때문이다', 'vdso.o가 실행 중 인터넷에서 공유 라이브러리를 받기 때문이다', '이미지 포함 어셈블리와 산출물의 빌드 순서를 연결합니다. runtime 다운로드나 매핑과 다른 단계입니다.'),
        ('cmd_vdsold에서 objcopy가 실패하면 뒤 rm이 실행되는가?', '아니다. && 연결이므로 뒤 단계로 가지 않는다', '그렇다. 세미콜론으로 무조건 이어 실행한다', '원본은 LD && OBJCOPY && rm입니다. 성공 연결과 무조건 순차 실행의 차이를 읽어야 합니다.'),
        ('공통 Makefile include만으로 이 파일의 링크 recipe가 vdso_check를 호출한다고 증명되는가?', '아니다. cmd_vdsold에 해당 호출이 없다', '그렇다. 변수 정의는 언제나 즉시 실행된다', '명령 변수의 정의와 실제 recipe에서의 참조는 다릅니다. 주석만으로 검사 실행을 확정하면 안 됩니다.')
    ]
)]
