"""Whole-file final vmlinux link orchestration."""
ROWS = [dict(
    path='scripts/link-vmlinux.sh', title='vmlinux 링크: kallsyms 반복·BTF 추출·최종 검증',
    intro='전체 helper와 실행 순서를 따라 커널 최종 ELF가 만들어지는 과정을 분석합니다.',
    principle='심볼 테이블을 이미지에 추가하면 주소와 크기가 달라질 수 있어 생성·재링크·검증을 반복해야 합니다.',
    use='링커 archive 선택, 생성 객체 의존성, ELF 메타데이터와 반복 수렴 검사를 학습합니다.',
    area='링커 · ELF · kallsyms · BTF · 빌드 의존성 · shell 오류 처리',
    sections=[
        ('시작과 설정 검사', '#!/bin/sh, GPL-2.0 스크립트는 set -e를 사용하고 세 인수를 LD,KBUILD_LDFLAGS,LDFLAGS_vmlinux에 저장합니다. is_enabled는 auto.conf에서 ^이름=y 패턴을 grep합니다. 끝 앵커는 없으므로 일반 문자열 검증기라기보다 생성된 설정 파일의 형식을 전제로 합니다. info는 고정 폭 상태 표시를 printf합니다.'),
        ('주요 링크 입력 선택', 'vmlinux_link는 첫 인수를 출력명으로 받고 shift합니다. LTO_CLANG 또는 X86_KERNEL_IBT이면 이미 준비한 vmlinux.o를 쓰고 libs를 비워 느린 처리를 반복하지 않습니다. 아니면 vmlinux.a와 KBUILD_VMLINUX_LIBS를 사용합니다. MODULES이면 .vmlinux.export.o를 추가하고 언제나 init/version-timestamp.o를 추가합니다. 최종 버전 객체가 실제 링크 입력에 들어오는 지점입니다.'),
        ('UML과 일반 linker', 'SRCARCH=um이면 CC를 linker driver로 사용하고 wl=-Wl,를 통해 linker 옵션을 전달하며 CFLAGS_vmlinux와 -lutil -lrt -lpthread를 씁니다. 다른 아키텍처는 LD와 KBUILD_LDFLAGS·LDFLAGS_vmlinux를 사용합니다. linker script 경로는 objtree/KBUILD_LDS입니다. 모든 플랫폼이 같은 명령 실행 파일을 사용하지 않습니다.'),
        ('Archive와 부가 옵션', 'strip_debug가 비어 있지 않으면 --strip-debug, VMLINUX_MAP이면 출력명.map을 만드는 -Map을 추가합니다. objs는 --whole-archive 구간으로, libs는 --start-group 구간으로 링크합니다. 전자는 객체 포함을 강제하고 후자는 archive 사이 참조 해결을 위한 그룹입니다. 이후 kallsymso,btf_vmlinux_bin_o,플랫폼 libs를 추가합니다. 하나의 archive 목록처럼 해석하지 않습니다.'),
        ('BTF 생성과 추출', 'gen_btf는 입력 이미지에 PAHOLE -J를 실행하며 LLVM_OBJCOPY 환경 변수로 OBJCOPY를 제공합니다. 이어 objcopy로 .BTF만 남기고 alloc,readonly 플래그와 --strip-all을 적용해 입력명.btf.o를 만듭니다. 주석은 __start_BTF·__stop_BTF도 제거해 linker script에서 다시 정의하도록 설명합니다. objcopy stderr를 숨기지만 명령 오류가 자동으로 성공으로 바뀌는 것은 아닙니다.'),
        ('ELF 종류의 바이트 수정', 'BTF 객체를 최종 링크 입력으로 쓰기 위해 ELF e_type 위치인 offset 16에 ET_REL의 두 바이트를 씁니다. CPU_BIG_ENDIAN이면 0,1이고 아니면 1,0입니다. printf와 dd bs=1,seek=16,conv=notrunc를 사용하므로 파일 나머지를 잘라내지 않습니다. 이후 전역 btf_vmlinux_bin_o를 결과 경로로 설정합니다. ELF 전체 endian을 변환하는 작업이 아닙니다.'),
        ('Kallsyms 객체 생성', 'kallsyms helper는 KALLSYMS_ALL이면 --all-symbols, ABSOLUTE_PERCPU이면 --absolute-percpu를 더합니다. scripts/kallsyms에 입력 심볼 파일을 전달해 두 번째 인수.S를 만들고 CC에 전처리·어셈블리 플래그를 전달해 .o로 컴파일합니다. 마지막 kallsymso를 그 객체로 갱신합니다. 여기서 생성기를 구현하는 것이 아니라 별도 도구를 호출합니다.'),
        ('Map 생성과 helper 연결', 'mksysmap은 NM -n 출력에 scripts/mksysmap sed 필터를 적용해 지정 파일에 저장합니다. sysmap_and_kallsyms는 이미지.syms를 만들고 그 파일에서 이미지.kallsyms.o를 생성하며 kallsyms_sysmap을 마지막 map 경로로 설정합니다. sorttable은 objtree/scripts/sorttable을 실행합니다. set -e만으로 pipeline 앞 NM 실패까지 항상 검출한다고 단정하지 않습니다. pipefail 설정은 없습니다.'),
        ('상세 출력과 clean', 'KBUILD_VERBOSE에 1이 포함되면 set -x입니다. 첫 인수가 clean이면 cleanup이 .btf.*,System.map,vmlinux,vmlinux.map을 rm -f하고 0으로 끝납니다. 전체 .tmp_vmlinux 파일을 이 함수에서 모두 지우는 것은 아닙니다. 정상 경로는 Makefile.build로 init/version-timestamp.o를 먼저 빌드하고 BTF·kallsyms·strip 변수를 비웁니다.'),
        ('최초 임시 링크', 'KALLSYMS이면 빈 .tmp_vmlinux.kallsyms0.syms를 만들고 dummy kallsyms 객체를 생성합니다. KALLSYMS 또는 DEBUG_INFO_BTF 중 하나가 켜지면 .tmp_vmlinux1을 링크합니다. BTF가 없을 때만 이 첫 링크에서 debug를 제거합니다. BTF는 DWARF 정보를 필요로 하므로 같은 제거 정책을 적용할 수 없습니다.'),
        ('BTF 조건부 호출의 한계', 'BTF이면 if ! gen_btf .tmp_vmlinux1 조건에서 실패 메시지와 설정 비활성화 제안을 출력하고 exit 1합니다. 그러나 shell 함수가 조건식으로 호출되는 경우 내부 set -e 동작의 예외를 고려해야 합니다. gen_btf 내부 각 도구 실패마다 명시적으로 return을 하는 코드는 아니므로 모든 중간 실패를 이 if가 반드시 잡는다고 확대하지 않습니다. 실제 오류 주입 실행은 하지 않았습니다.'),
        ('두 차례의 심볼 산출과 크기 비교', 'KALLSYMS 경로는 strip_debug=1로 둔 뒤 첫 임시 이미지에서 심볼 객체를 만들고 file-size.sh로 size1을 얻습니다. 그 객체를 넣어 .tmp_vmlinux2를 링크하고 다시 심볼 객체를 만들어 size2를 얻습니다. 심볼 데이터의 추가 자체가 이미지 배치를 바꾸므로 처음 주소만 넣고 끝내지 않습니다. 비교하는 것은 생성 객체 파일 크기이며 심볼 주소 배열의 직접 동등 비교가 아닙니다.'),
        ('추가 pass와 수렴의 한계', 'size1과 size2가 다르거나 KALLSYMS_EXTRA_PASS가 비어 있지 않으면 세 번째 임시 링크와 심볼 생성을 수행합니다. 변수 값이 0이라는 문자열이어도 비어 있지 않으므로 추가 pass 조건입니다. 크기 확장으로 branch stub이 생겨 다시 심볼 수가 늘 수 있다는 주석이 있습니다. 변화가 없어질 때까지 무한 반복하는 알고리즘이 아니라 최대 한 번의 조건부 추가 pass입니다.'),
        ('최종 링크 후 처리', 'strip_debug를 비우고 vmlinux를 링크합니다. BTF이면 RESOLVE_BTFIDS로 ID를 채우고 최종 System.map을 생성합니다. BUILDTIME_TABLE_SORT이면 sorttable을 호출하며 실패를 진단하고 종료합니다. 순서는 최종 링크→BTF ID→map→조건부 정렬입니다. 임시 링크의 debug 제거 설정을 그대로 최종 링크에 남기지 않습니다.'),
        ('최종 map 비교와 의존 파일', 'KALLSYMS이면 cmp -s로 최종 System.map과 마지막 kallsyms_sysmap을 비교합니다. 다르면 inconsistent 진단과 EXTRA_PASS 제안을 출력하고 exit 1합니다. 같은 크기였다는 조건만으로 성공을 보증하지 않고 실제 map을 비교합니다. 끝에서 vmlinux: 스크립트경로를 .vmlinux.d에 기록해 fixdep에 제공합니다. 전체 흐름을 대조했으며 실제 커널 빌드·링크를 실행한 것은 아닙니다.')
    ], questions=[
        ('LTO_CLANG 또는 X86_KERNEL_IBT일 때 주요 입력은?', 'vmlinux.o', '항상 vmlinux.a만', '이 경로는 이미 준비된 객체를 사용해 느린 링크 작업 반복을 피합니다. libs도 비웁니다.'),
        ('init/version-timestamp.o는 어느 링크 경로에 추가되는가?', 'vmlinux_link에서 항상 objs에 추가된다', 'BTF가 켜졌을 때만 추가된다', 'MODULES 조건 밖에 추가 문장이 있습니다. 최종 빌드 버전의 강한 정의를 연결하는 경로입니다.'),
        ('BTF의 첫 임시 링크에서 debug를 유지하는 이유는?', 'DWARF에서 BTF를 생성하기 위해서다', 'System.map은 항상 DWARF만 읽기 때문이다', 'gen_btf의 pahole 작업이 DWARF를 입력으로 사용합니다. nm 기반 map 생성과 구분합니다.'),
        ('ET_REL 수정은 파일 전체를 다시 쓰는가?', '아니다. offset 16의 두 바이트를 notrunc로 갱신한다', '그렇다. 모든 ELF section을 byte swap한다', 'dd는 bs=1,seek=16이며 e_type 값만 기록합니다. 대상 endian에 맞는 두 바이트를 선택합니다.'),
        ('KALLSYMS_EXTRA_PASS=0이면 추가 pass가 꺼지는가?', '아니다. 비어 있지 않아 추가 pass 조건이다', '그렇다. 숫자 0 여부를 산술 검사한다', '조건은 -n 문자열 검사입니다. 주석의 =1 예제와 실제 조건을 구분합니다.'),
        ('두 kallsyms 객체 크기가 같으면 마지막 map 검사를 생략하는가?', '아니다. KALLSYMS이면 최종 map을 비교한다', '그렇다. 같은 크기는 모든 주소 일치를 보장한다', '추가 pass 선택과 최종 주소 목록 검증은 다른 단계입니다.'),
        ('심볼 배치가 계속 달라지면 자동으로 무한 재링크하는가?', '아니다. 조건부 세 번째 pass 뒤 최종 비교로 실패할 수 있다', '그렇다. while 루프가 반드시 수렴할 때까지 반복한다', '실제 코드에 무한 수렴 루프는 없습니다. 제한된 pass와 사후 검증으로 구성됩니다.'),
        ('최종 단계에서 생성하는 .vmlinux.d의 목적은?', 'fixdep용 스크립트 의존성 기록', '새 사용자 namespace 생성', '마지막 echo는 vmlinux가 실행 스크립트에 의존함을 기록합니다. ELF 내용과 별개인 빌드 메타데이터입니다.')
    ]
)]
