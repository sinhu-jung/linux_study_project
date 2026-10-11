"""Whole-file kernel version objects, build recipes and LTO note."""
ROWS = [dict(
    path='init/version.c', title='커널 버전 진입 파일: 초기 hostname·배너·weak 정의',
    intro='초기 매개변수 handler와 배너 형식, ELF note, timestamp 구현 포함을 모두 분석합니다.',
    principle='실행 중 바꾸는 초기 데이터와 빌드 때 고정하는 버전 문자열은 다른 경로로 관리됩니다.',
    use='문자열 길이 제한, 전처리 소스 포함, weak 심볼과 export를 구분합니다.',
    area='부팅 매개변수 · 문자열 · 링커 심볼 · 빌드 메타데이터',
    sections=[
        ('포함 파일과 초기 handler', 'GPL-2.0-only 파일은 generated compile 정보와 build-salt,elfnote-lto,export,init,printk,UTS,proc namespace 헤더를 포함합니다. early_hostname은 init_uts_ns.name.nodename 배열 크기와 그보다 하나 작은 maxlen을 구합니다. strscpy에 배열 전체 크기를 전달해 초기 hostname을 복사합니다.'),
        ('잘린 hostname의 처리', 'nodename은 65바이트이므로 일반적인 이 구조에서는 최대 64바이트의 문자열과 종료 공간을 사용합니다. strscpy 반환이 음수면 길이 초과와 잘림을 경고하고 그래도 handler는 0을 반환합니다. 길이 초과를 이유로 여기서 이전 hostname으로 rollback하거나 부팅을 중단하지 않습니다. early_param("hostname",early_hostname)으로 초기 매개변수에 연결되며 문자열 전체의 문자 수와 byte 수를 혼동하지 않습니다.'),
        ('Proc 배너는 형식 문자열', 'linux_proc_banner는 %s version %s, compile 사용자@호스트, 컴파일러, 마지막 %s와 newline으로 구성합니다. 세 %s는 그대로 형식 자리표시자로 남고 LINUX_COMPILE_BY·HOST·COMPILER는 전처리 매크로 문자열을 연결합니다. 이 파일이 선언 위치에서 sprintf를 실행하는 것은 아닙니다. 실제 linux_banner의 고정 문자열과 다릅니다.'),
        ('ELF note와 weak 선언', 'BUILD_SALT와 BUILD_LTO_INFO를 사용해 관련 ELF note를 정의합니다. 이후 init_uts_ns와 linux_banner를 __weak로 선언합니다. 주석은 build version과 timestamp가 빌드 마지막 단계에 확정되어 먼저 weak로, 나중에는 weak 없이 컴파일한다고 설명합니다. C의 weak는 런타임 namespace 권한이나 낮은 메모리 일관성을 뜻하지 않고 링크 심볼 선택과 관련됩니다.'),
        ('C 소스 포함과 export', 'version-timestamp.c를 직접 include하므로 그 정의가 이 번역 단위에도 들어옵니다. 앞 weak 속성을 가진 임시 정의 경로와 별도 최종 컴파일 경로가 연결됩니다. 마지막 EXPORT_SYMBOL_GPL(init_uts_ns)는 초기 namespace 객체를 export하며 이 파일에 linux_banner의 같은 export는 없습니다. 전체 handler·문자열·note·선언·include·export를 검토했습니다. 실제 커널 링크를 실행한 결과는 아닙니다.')
    ], questions=[
        ('hostname이 배열에 비해 길면 early_hostname은?', '잘라 복사한 상태에서 경고하고 0을 반환한다', '반드시 -EINVAL로 부팅을 중단한다', '음수 strscpy 결과는 경고 분기로만 이어지고 마지막 return은 0입니다.'),
        ('linux_proc_banner의 %s는 이 선언에서 대체되는가?', '아니다. 형식 문자열 안에 남는다', '그렇다. C가 자동으로 현재 hostname을 채운다', '인접 문자열 연결과 런타임 서식 처리는 다릅니다. 전처리 compile 매크로만 빌드 문자열로 연결됩니다.'),
        ('version-timestamp.c include의 의미는?', '구현 소스 전체가 이 번역 단위에 포함된다', '함수 원형만 자동 추출한다', 'C의 include는 소스 내용을 가져옵니다. weak 속성의 임시 경로와 별도 컴파일되는 최종 경로를 구분해야 합니다.')
    ]
), dict(
    path='init/version-timestamp.c', title='최종 버전 데이터: 초기 UTS 객체와 고정 배너',
    intro='초기 namespace의 모든 지정 초기화와 커널 배너 문자열의 조합을 분석합니다.',
    principle='정적 객체 초기화는 구조체 필드별 빌드 정보와 실행 중 사용할 참조·소유권 상태를 함께 설정합니다.',
    use='지정 초기화, 생략 필드의 0 초기화, 빌드 문자열 연결을 학습합니다.',
    area='정적 저장 객체 · UTS · 참조 수 · 문자열 연결',
    sections=[
        ('빌드 입력과 객체', 'GPL-2.0-only 파일은 generated compile·utsrelease 헤더, proc namespace,refcount,UTS 헤더를 포함합니다. UTS_VERSION은 이 파일 안에서 직접 정의하지 않으며 Makefile의 강제 include 헤더가 공급합니다. init_uts_ns를 실제 지정 초기화하는 구현입니다.'),
        ('이름 여섯 필드', 'name.sysname=UTS_SYSNAME,nodename=UTS_NODENAME,release=UTS_RELEASE,version=UTS_VERSION,machine=UTS_MACHINE,domainname=UTS_DOMAINNAME입니다. release와 version은 별개입니다. kernel release 식별자와 빌드 회차·설정·timestamp로 구성하는 UTS_VERSION을 같은 값이라고 설명하면 안 됩니다.'),
        ('초기 수명과 소유권', 'ns.count는 REFCOUNT_INIT(2), user_ns는 &init_user_ns, ns.inum은 PROC_UTS_INIT_INO입니다. CONFIG_UTS_NS일 때만 ns.ops=&utsns_operations를 지정합니다. 생략한 정적 객체 필드는 0으로 초기화됩니다. 새 clone UTS 객체의 count=1과 초기 객체의 count=2를 구분합니다.'),
        ('고정 linux_banner', 'linux_banner는 Linux version 다음 UTS_RELEASE, compile 사용자@호스트, LINUX_COMPILER, UTS_VERSION과 newline을 인접 문자열로 연결한 const char 배열입니다. linux_proc_banner와 달리 %s 자리표시자가 없습니다. 실행 중 nodename 변경이 이 배열을 다시 구성하지 않습니다. 두 전역 정의와 전체 include·조건을 검토했으며 실제 빌드 호스트 값은 여기서 임의로 채우지 않습니다.')
    ], questions=[
        ('init_uts_ns의 초기 참조 수는?', '2', '새 clone과 동일하게 1', '이 파일은 REFCOUNT_INIT(2)를 명시합니다. kernel/utsname.c의 create_uts_ns는 새 객체를 1로 시작합니다.'),
        ('UTS_RELEASE와 UTS_VERSION은 같은 필드에 저장되는가?', '아니다. release와 version에 각각 저장된다', '그렇다. 하나의 nodename 배열에 합쳐진다', '지정 초기화에서 별개의 두 필드입니다. 배너에도 각각 다른 위치에 연결됩니다.')
    ]
), dict(
    path='init/Makefile', title='init 빌드 규칙: 객체 구성과 임시·최종 UTS_VERSION',
    intro='부팅 객체 선택부터 버전·timestamp의 변수 평가와 강제 include 규칙까지 전체를 분석합니다.',
    principle='같은 소스를 서로 다른 생성 헤더와 심볼 속성으로 컴파일해 빌드 마지막에 확정되는 정보를 반영할 수 있습니다.',
    use='Kbuild 조건부 목록, 재귀 변수, 대상별 변수와 byte 단위 문자열 제한을 학습합니다.',
    area='Make · Kbuild · 조건부 컴파일 · 생성 헤더 · 재현 빌드 입력',
    sections=[
        ('공통 컴파일과 필수 객체', 'GPL-2.0 Makefile은 ccflags-y에 -fno-function-sections -fno-data-sections를 지정합니다. obj-y의 기본은 main.o,version.o,mounts.o이고 뒤에 init_task.o를 추가합니다. 이 목록만으로 커널 전체 객체 목록을 설명하는 것은 아닙니다.'),
        ('Initrd와 복합 mount 객체', 'CONFIG_BLK_DEV_INITRD가 y가 아니면 noinitramfs.o, y이면 initramfs.o를 해당 설정 변수로 추가합니다. GENERIC_CALIBRATE_DELAY는 calibrate.o를 선택합니다. mounts-y는 do_mounts.o이고 BLK_DEV_RAM에 따라 do_mounts_rd.o, INITRD에 따라 do_mounts_initrd.o를 복합 객체에 추가합니다. obj-y와 mounts-y는 같은 계층의 단순 파일 목록이 아닙니다.'),
        ('SMP와 preemption 표기', 'smp-flag-$(CONFIG_SMP)는 SMP, preempt-flag-$(CONFIG_PREEMPT_BUILD)는 PREEMPT, 이어 DYNAMIC과 RT 설정은 각각 PREEMPT_DYNAMIC·PREEMPT_RT를 대입합니다. 최종 문자열은 smp-flag-y와 preempt-flag-y를 사용합니다. 같은 변수에 여러 활성 대입이 도달하면 뒤 대입이 값을 정하므로 세 preemption 단어를 무조건 모두 이어 붙이는 방식은 아닙니다.'),
        ('사용자 지정과 자동 값', 'build-version과 build-timestamp는 = 형태의 재귀 변수이며 $(or 사용자값,자동값)으로 비어 있지 않은 KBUILD_BUILD_VERSION·TIMESTAMP를 우선합니다. 숫자 0이라는 문자열도 비어 있지 않은 값입니다. 실제 자동 값의 대상별 정의는 뒤 최종 헤더 규칙에 있습니다. 단순히 이 파일을 읽은 시점에 날짜가 한 번 고정되는 := 변수와 다릅니다.'),
        ('UTS_VERSION 생성식', 'filechk_uts_version은 #와 빌드 번호, SMP·preemption 표기, timestamp를 echo로 조합하고 cut -b -64로 앞 64바이트만 남깁니다. 이어 #define UTS_VERSION과 따옴표 문자열을 출력합니다. byte 제한이므로 다바이트 문자 64개를 보장하는 규칙은 아닙니다. 이 제한은 UAPI의 64바이트 문자열 공간과 연결됩니다.'),
        ('임시 헤더와 version.o', '$(obj)/utsversion-tmp.h는 FORCE에 의존하고 filechk,uts_version을 호출합니다. clean-files에 임시 헤더를 추가하며 version.o는 그 헤더에 의존합니다. CFLAGS_version.o는 -include로 임시 헤더를 주입합니다. FORCE 의존성을 생성 헤더 내용이 매번 반드시 달라진다는 보장과 혼동하지 않습니다.'),
        ('최종 헤더와 timestamp 객체', 'include/generated/utsversion.h에는 대상별 build-version-auto=$(shell scripts/build-version), build-timestamp-auto=$(shell LC_ALL=C date)를 지정합니다. 같은 filechk 생성식을 쓰고 FORCE에 의존합니다. version-timestamp.o는 최종 헤더에 의존하고 -include로 주입합니다. 이 파일의 obj-y 목록에 version-timestamp.o를 직접 더하는 문장은 없으므로 최종 링크 전체를 이 Makefile 하나로 증명하지 않습니다. LC_ALL=C는 이 date 호출의 locale 설정이지 모든 빌드 명령의 전역 설정이 아닙니다.')
    ], questions=[
        ('UTS_VERSION의 최대 길이를 제한하는 방법은?', 'cut -b -64로 byte 단위 제한', '문자열 전체를 64개의 Unicode 문자로 재인코딩', '명령 옵션은 -b입니다. byte 수와 문자의 개수는 다를 수 있습니다.'),
        ('KBUILD_BUILD_TIMESTAMP가 비어 있지 않으면?', '자동 date 값보다 우선한다', '항상 무시하고 현재 날짜를 쓴다', '$(or ...)의 첫 비어 있지 않은 인수를 사용합니다. 명시적 빌드 입력을 제공할 수 있습니다.'),
        ('version.o와 version-timestamp.o의 강제 include는 같은가?', '아니다. 각각 임시 헤더와 최종 생성 헤더다', '그렇다. 둘 다 generated/compile.h만 포함한다', 'CFLAGS의 -include가 서로 다른 UTS_VERSION 공급 경로를 지정합니다. 소스 자체 include와 별도입니다.'),
        ('CONFIG_BLK_DEV_INITRD가 y가 아니면 직접 추가되는 객체는?', 'noinitramfs.o', '항상 initramfs.o', 'ifneq 조건의 첫 분기가 noinitramfs.o를 추가합니다. 복합 mounts 객체 구성 조건과 구별합니다.')
    ]
), dict(
    path='include/linux/elfnote-lto.h', title='LTO ELF note: 설정을 숫자 descriptor로 기록하기',
    intro='LTO note type과 설정별 매크로의 전체 정의를 분석합니다.',
    principle='빌드 설정을 ELF 메타데이터에 기록하는 작업과 해당 최적화를 실행하는 작업은 다릅니다.',
    use='전처리 분기, ELF note 이름·type·descriptor를 구분합니다.',
    area='ELF note · LTO · 전처리 · 빌드 메타데이터',
    sections=[
        ('헤더 구성과 note type', 'include guard 안에서 linux/elfnote.h를 포함하고 LINUX_ELFNOTE_LTO_INFO를 0x101로 정의합니다. 이 원본 헤더에는 별도 SPDX 줄이 없습니다. 주된 결과는 함수가 아니라 BUILD_LTO_INFO 매크로입니다.'),
        ('두 설정 분기', 'CONFIG_LTO가 있으면 ELFNOTE32("Linux",0x101,1), 없으면 같은 name·type에 descriptor 0을 쓰도록 정의합니다. 설정이 없을 때 note 전체를 생략하는 매크로가 아닙니다. ELFNOTE32의 의미를 커널 전체가 반드시 32비트로 빌드된다는 뜻으로 해석하지 않습니다.'),
        ('사용과 범위', 'init/version.c에서 BUILD_LTO_INFO를 사용하면 해당 note가 생성되는 연결입니다. 헤더를 포함하는 것만으로 LTO 최적화가 켜지거나 링크 옵션이 바뀌지는 않습니다. type 상수·조건부 정의·include 전체를 검토했으며 실제 ELF 바이너리를 추출해 확인한 것은 아닙니다.')
    ], questions=[
        ('CONFIG_LTO가 없을 때 BUILD_LTO_INFO는?', 'descriptor 0인 Linux note를 정의한다', '아무 코드도 없는 빈 매크로다', 'else 분기에도 ELFNOTE32 호출이 있습니다. 비활성 정보를 명시적으로 기록합니다.'),
        ('LTO note의 type과 descriptor의 역할은?', 'type은 0x101 식별자, descriptor는 설정에 따른 1 또는 0', '둘 다 현재 PID를 저장한다', 'note 종류와 그 종류의 값은 별개입니다. 이 매크로는 최적화를 수행하는 함수가 아닙니다.')
    ]
)]
