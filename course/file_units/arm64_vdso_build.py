"""Whole-file native ARM64 vDSO build rules."""
ROWS = [dict(
    path='arch/arm64/kernel/vdso/Makefile',
    title='ARM64 vDSO 빌드: 전용 옵션과 ELF·offset 산출물',
    intro='객체 목록부터 링크·검사·strip·offset 헤더 생성까지 전체 빌드 규칙을 분석합니다.',
    principle='사용자 공간에 매핑할 커널 제공 코드에는 일반 커널 객체와 다른 컴파일 계약과 별도의 산출물 검사가 필요합니다.',
    use='GNU make의 타깃·의존성·변수 범위를 읽고 디버그 이미지와 배포 이미지의 관계를 설명합니다.',
    area='Kbuild · GNU make · 컴파일 옵션 · ELF linking · 심볼 바인딩 · 생성 헤더 · 증분 빌드',
    sections=[
        ('전체 객체와 공통 규칙', 'GPL-2.0과 AArch64 vDSO 빌드 주석 뒤 lib/vdso/Makefile을 포함합니다. obj-vdso는 vgettimeofday.o, note.o, sigreturn.o, vgetrandom.o, vgetrandom-chacha.o 다섯 개입니다. targets에 이 목록과 vdso.so·vdso.so.dbg를 먼저 저장한 뒤 obj-vdso에 $(obj)/ 접두어를 붙입니다. := 즉시 확장 때문에 targets에 저장한 목록과 나중의 경로 포함 목록을 구분해야 합니다.'),
        ('BTI와 링크 옵션', 'CONFIG_ARM64_BTI_KERNEL에 따라 btildflags-y에 -z force-bti를 넣습니다. ldflags-y는 -shared, -soname=linux-vdso.so.1, -Bsymbolic, --build-id=sha1, -n과 해당 BTI 옵션입니다. 공유 ELF의 이름과 내부 심볼 바인딩·식별자·링크 배치를 지정하는 옵션이며 소스 함수의 인수 ABI를 바꾸는 선언은 아닙니다. build-id의 sha1 선택을 코드 서명의 진위 검증으로 해석하지 않습니다.'),
        ('Bsymbolic과 orphan 정책', '주석은 -Bsymbolic을 ARM·compat와의 일관성 및 향후 공개 함수 내부 호출에 대비해 넣었다고 설명합니다. 공유 객체 안의 정의에 내부 참조를 바인딩하는 링크 선택입니다. CONFIG_LD_ORPHAN_WARN이 정의되면 --orphan-handling=$(CONFIG_LD_ORPHAN_WARN_LEVEL)을 추가합니다. 실제 동작 수준은 설정값에 따르므로 항상 오류로 중단한다고 단정하지 않습니다.'),
        ('디렉터리 공통 C 옵션', 'ccflags-y는 -fno-common, -fno-builtin, -fno-stack-protector, -ffixed-x18과 DISABLE_BRANCH_PROFILING·BUILD_VDSO 정의를 제공합니다. builtin 치환·스택 보호 코드 삽입·x18 할당 등에 대한 컴파일 계약입니다. kernel에서 가져온 코드라고 일반 커널의 모든 계측 옵션을 그대로 허용하는 구성이 아닙니다. 이 변수의 적용 범위와 아래 특정 객체 옵션을 구별해야 합니다.'),
        ('제거할 옵션과 대상', 'CC_FLAGS_REMOVE_VDSO에는 FTRACE, -Os, SCS, RANDSTRUCT, GCC plugin, LTO, CFI 관련 플래그 변수와 -Wmissing-prototypes·-Wmissing-declarations가 나열됩니다. 주석은 마지막 두 경고를 제거하여 CONFIG_WERROR 빌드를 가능하게 한다고 설명합니다. CFLAGS_REMOVE_vgettimeofday.o와 CFLAGS_REMOVE_vgetrandom.o만 이 목록을 사용합니다. 모든 객체에 똑같은 제거 변수가 지정됐다고 확대해서 읽지 않습니다.'),
        ('추가할 옵션과 소스 강제 포함', 'CC_FLAGS_ADD_VDSO는 -O2 -mcmodel=tiny -fasynchronous-unwind-tables이며 두 C 객체의 CFLAGS에 적용합니다. c-gettimeofday-y와 c-getrandom-y가 비어 있지 않으면 각각 -include를 추가합니다. 따라서 wrapper 소스에 공통 C 구현의 include가 직접 없어도 컴파일 문맥에 들어올 수 있습니다. unwind 테이블 생성 옵션과 최종 링커의 .eh_frame discard 정책은 서로 다른 단계입니다.'),
        ('링커 스크립트 전처리', 'targets에 vdso.lds를 추가하고 CPPFLAGS_vdso.lds에 -P -C -U$(ARCH)를 줍니다. -P는 전처리 줄 표시 억제, -C는 주석 보존, -U는 해당 이름 매크로 해제입니다. 이 파일이 직접 vdso.lds.S 전체를 문자열로 생성하는 것은 아니며 Kbuild 전처리 규칙과 함께 작동합니다.'),
        ('Dbg 링크와 의존성 순서', 'ldflags-y 마지막에 -T를 추가합니다. vdso.so.dbg의 첫 prerequisite는 vdso.lds이고 뒤에 경로가 붙은 다섯 객체와 FORCE가 옵니다. 주석은 .lds가 반드시 첫 번째여야 한다고 강조합니다. 공유 링크 명령과 -T의 스크립트 입력이 맞물리는 순서이므로 목록을 무심코 바꾸면 안 됩니다. recipe는 if_changed,vdsold_and_vdso_check를 호출합니다.'),
        ('FORCE와 증분 빌드', 'FORCE prerequisite가 있어도 본문은 Kbuild의 if_changed를 호출합니다. 따라서 이 텍스트만 보고 매번 무조건 새 ELF로 링크한다고 결론내리면 안 됩니다. 실제 변경 판단은 명령과 의존성을 다루는 Kbuild helper의 계약과 함께 봐야 합니다. 이 파일에 그 helper 구현 자체는 없습니다.'),
        ('Strip 산출물', '$(obj)/%.so 패턴 타깃에 OBJCOPYFLAGS := -S를 타깃별로 설정합니다. 같은 stem의 %.so.dbg와 FORCE에 의존하여 if_changed,objcopy를 호출합니다. 소스에서 다시 컴파일하는 것이 아니라 dbg 이미지를 바탕으로 strip한 .so를 만드는 경로입니다. dbg 파일을 삭제한다는 recipe는 없습니다.'),
        ('Offset 헤더 생성 경로', 'gen-vdsosym은 $(src)/gen_vdso_offsets.sh입니다. cmd_vdsosym은 $(NM) $< 출력에서 helper로 VDSO_ 심볼을 변환하고 LC_ALL=C sort 결과를 $@로 저장합니다. include/generated/vdso-offsets.h는 vdso.so.dbg와 FORCE에 의존하며 $<는 첫 의존성인 dbg ELF입니다. strip한 .so를 입력으로 쓰는 경로가 아닙니다.'),
        ('링크 후 검사와 해석 한계', 'quiet_cmd_vdsold_and_vdso_check는 LD와 타깃을 표시하고 실제 명령은 $(cmd_ld); $(cmd_vdso_check)입니다. 원본의 구분자는 &&가 아니라 세미콜론이므로 이 식만으로 링크 실패 시 검사를 반드시 건너뛴다고 주장할 수 없습니다. 공통 검사 명령은 재배치 출력 필터이며 전체 셸 오류 처리와 Kbuild 실행 문맥도 확인해야 합니다. 이 학습에서는 링크나 검사 recipe를 실제 실행하지 않았습니다.'),
        ('전체 범위와 CS 연결', '모든 변수·조건부·타깃·패턴 규칙·실행 명령을 설명했습니다. 공통 코드의 강제 포함, 객체별 계측 제거, ELF 생성·strip·offset 추출의 의존성 그래프가 핵심입니다. 원본에 근거한 빌드 구조 분석이며 native ARM64 컴파일 성공이나 최종 ELF 권한·심볼 검증을 대신하지 않습니다.')
    ],
    questions=[
        ('vdso-offsets.h를 생성할 때 NM의 입력은?', 'vdso.so.dbg이다', 'strip한 vdso.so이다', '생성 헤더 타깃의 첫 의존성은 dbg ELF이며 명령의 $<가 이를 가리킵니다. strip 산출물은 별도 경로입니다.'),
        ('왜 vdso.so.dbg 의존성에서 vdso.lds가 맨 앞인가?', '링크 플래그 끝의 -T와 연결되는 스크립트 입력 순서를 맞추기 위해서다', '가장 작은 파일부터 정렬하면 빌드가 빨라지기 때문이다', '원본 주석이 .lds has to be first를 명시합니다. 의존성의 순서가 공유 링크 명령 구성에 참여하므로 단순 표시 순서가 아닙니다.'),
        ('wrapper C 소스에 공통 gettimeofday.c include가 없어도 구현을 가져오는 방식은?', '조건부 CFLAGS의 -include이다', '런타임에 gettimeofday.c를 파일로 읽어 실행한다', '공통 Makefile이 선택한 경로를 컴파일러의 강제 포함 옵션으로 전달합니다. 빌드 시 번역 단위 구성입니다.'),
        ('CFLAGS_REMOVE 목록이 이 파일의 모든 객체에 동일하게 지정되는가?', '아니다. 명시적으로 vgettimeofday.o와 vgetrandom.o에 연결된다', '그렇다. 변수 이름이 VDSO이면 자동으로 모든 객체에 적용된다', '목록 변수와 이를 참조하는 객체별 변수는 별개입니다. 실제 연결 대상을 확인해야 합니다.'),
        ('FORCE 의존성만 보고 매 실행마다 링크한다고 확정할 수 있는가?', '아니다. recipe의 if_changed 판단도 함께 봐야 한다', '그렇다. if_changed는 이름뿐이고 무조건 링크한다', 'FORCE와 Kbuild의 변경 판단 helper는 함께 쓰입니다. 이 파일만으로 helper의 판단을 제거해서 해석하면 안 됩니다.')
    ]
)]
