"""Whole-file C and assembler ELF note generation macros."""
ROWS = [dict(
    path='include/linux/elfnote.h',
    title='ELF note 생성 매크로: 크기·정렬·이름 공간과 고유 심볼',
    intro='C와 어셈블리의 모든 note 생성 매크로를 분석하고 실제 바이너리 필드와 연결합니다.',
    principle='바이너리 메타데이터의 실제 길이와 저장 시 정렬 padding은 다르며, 전처리 매크로는 그 계약을 언어별로 구성합니다.',
    use='ELF note 레이아웃을 계산하고 매크로 인수·고유 이름·description 자료형의 제약을 설명합니다.',
    area='ELF · 바이너리 형식 · 정렬 · 전처리 · 토큰 결합 · 어셈블리 지역 라벨 · 정적 객체',
    sections=[
        ('파일 범위와 note 모델', 'GPL-2.0 include guard 뒤 주석은 note를 name, type, desc 세 부분으로 설명합니다. type의 이름 공간은 name에 속하므로 서로 다른 name에서 같은 정수 type을 써도 같은 의미라고 볼 수 없습니다. name은 .note.NAME 섹션 이름에 적합해야 합니다. 최종 vmlinux에서 note를 묶어 PT_NOTE로 제공한다는 일반 설명과 vDSO 같은 개별 링커 스크립트의 출력 섹션 이름은 구분해야 합니다.'),
        ('두 언어 분기', '#ifdef __ASSEMBLER__에서는 어셈블러 지시문으로, else에서는 uapi/linux/elf.h의 자료형을 사용하는 C 정적 객체로 생성합니다. 두 분기의 ELFNOTE 인수 개수와 표현 방식은 다릅니다. asm은 name,type,desc 세 인수이고 C는 size,name,type,desc 네 인수입니다. C 전용 ELFNOTE32·ELFNOTE64 wrapper도 제공합니다.'),
        ('어셈블리 시작과 헤더', 'ELFNOTE_START(name,type,flags)는 .pushsection .note.name,flags,@note 후 .balign 4를 수행합니다. 세 .long으로 namesz=2f-1f, descsz=4484f-3f, type을 기록합니다. 1f·2f·3f·4484f는 앞으로 나올 숫자 지역 라벨을 참조하는 어셈블리 표기입니다. 이 값들은 runtime 포인터 계산이 아니라 어셈블할 때 정해지는 거리입니다.'),
        ('이름과 padding의 경계', '라벨 1에서 .asciz #name으로 이름과 NUL을 기록하고 라벨 2에서 .balign 4를 수행한 뒤 라벨 3에서 description이 시작합니다. 따라서 2f-1f는 NUL을 포함하지만 이름 뒤 정렬 padding은 포함하지 않습니다. Linux의 이름 길이는 6바이트이고 4바이트 경계까지 2바이트를 추가로 채울 수 있습니다. namesz를 그 padded 크기인 8로 기록하는 구조가 아닙니다.'),
        ('끝 라벨과 섹션 복구', 'ELFNOTE_END는 4484 라벨을 description 직후에 둔 뒤 .balign 4, .popsection을 수행합니다. descsz도 description 자체의 길이이며 끝 padding을 제외합니다. pushsection/popsection은 note 생성 전의 섹션 문맥을 복구하기 위한 쌍입니다. 매크로가 남은 모든 어셈블리 내용을 note 섹션으로 바꾸는 것은 아닙니다.'),
        ('어셈블리 편의 wrapper와 오래된 예시', 'asm ELFNOTE(name,type,desc)는 START의 flags를 "a"로 고정하고 desc를 그대로 내보낸 뒤 END를 호출합니다. 실제 정의는 세 인수입니다. 앞 주석의 ELFNOTE(XYZCo,42,.asciz,"forty-two") 같은 네 인수 예시는 현재 정의와 맞지 않습니다. 현재 호출 형태는 ELFNOTE(XYZCo,42,.asciz "forty-two")처럼 지시문과 피연산자를 세 번째 인수로 함께 넘기는 방식입니다. 주석 예시보다 실제 정의를 기준으로 읽어야 합니다.'),
        ('C 객체의 형태', '_ELFNOTE(size,name,unique,type,desc)는 static const 익명 구조체 객체를 선언합니다. 첫 필드는 struct elf##size##_note _nhdr, 다음은 unsigned char _name[sizeof(name)], 마지막은 typeof(desc) _desc입니다. 이름은 문자열 리터럴이어야 하며 description은 값으로 전달합니다. 포인터를 전달하면 가리킨 데이터 전체를 자동 직렬화하는 것이 아니라 그 포인터 자료형과 크기를 반영하므로 사용 목적에 맞는 값을 제공해야 합니다.'),
        ('C 초기화와 정렬', '헤더 초기값은 sizeof(name), sizeof(desc), type이며 뒤에 name과 desc를 초기화합니다. _name과 _desc, 객체 자체에 aligned(sizeof(Elf##size##_Word))를 지정합니다. 확인한 UAPI에서 Elf32_Word와 Elf64_Word는 모두 u32이므로 두 경우 이 정렬 인수는 4입니다. ELFNOTE64라고 note 헤더 필드가 각각 8바이트가 되는 것은 아닙니다. 두 note 헤더는 32비트 크기 필드 세 개를 사용합니다.'),
        ('객체 속성과 섹션', '객체에는 __used와 section(".note." name), aligned, unused 속성이 붙습니다. 사용되지 않는 정적 객체라는 이유로 컴파일러가 생략하는 문제와 경고를 다루고 note 섹션으로 배치하려는 구성입니다. __used를 최종 링크의 모든 discard·garbage collection 정책을 무조건 무효화하는 보장으로 설명하면 안 됩니다. 최종 보존은 링크 규칙과 함께 확인해야 합니다.'),
        ('행 번호로 고유 이름 만들기', '_ELFNOTE_PASTE(a,b)는 a##b이고 객체 이름은 _ELFNOTE_PASTE(_note_,unique)로 생성합니다. C ELFNOTE는 __LINE__을 unique에 전달하여 _note_행번호 이름을 만듭니다. 매크로 계층을 통해 행 번호를 확장한 뒤 결합합니다. 주석은 한 줄에 하나의 note만 정의하라고 명시합니다. 같은 범위의 한 줄에 두 정의를 넣으면 같은 이름이 되어 충돌할 수 있습니다.'),
        ('레이아웃 계산 예시', '어셈블리에서 name=Linux, description=.long 값 하나라면 헤더 12바이트, 이름 6바이트, 이름 padding 2바이트, description 4바이트로 한 note가 24바이트를 차지합니다. 기록되는 namesz는 6, descsz는 4입니다. 저장 공간 전체 크기와 내부 길이 필드를 혼동하면 다음 note 위치를 계산할 때 오류가 생깁니다.'),
        ('Wrapper와 검증 범위', 'ELFNOTE32와 ELFNOTE64는 각각 size=32·64를 C ELFNOTE에 전달합니다. 전체 매크로·분기·주석의 제약을 다뤘으며 포함된 UAPI 전체를 함께 완료 집계하지 않습니다. 예제는 원본 레이아웃을 따른 계산이고 실제 객체 파일 생성·다른 ABI에서의 compiler layout·readelf 출력까지 검증한 결과는 아닙니다.')
    ],
    questions=[
        ('이름 Linux를 .asciz로 넣을 때 namesz에 기록되는 값은?', '6이다. NUL은 포함하고 뒤 정렬 padding은 제외한다', '8이다. 4바이트 정렬 padding까지 이름 길이에 포함한다', '이름 끝 라벨 2는 .balign보다 앞입니다. 따라서 Linux의 5글자와 NUL만 거리 계산에 들어갑니다.'),
        ('ELFNOTE64의 note 헤더가 24바이트인 이유를 설명하라는 주장은 맞는가?', '아니다. 이 코드의 Elf64_Word도 u32라 세 필드 헤더는 12바이트이다', '맞다. 이름에 64가 있으므로 각 필드는 무조건 8바이트이다', 'ELF 클래스와 개별 필드 폭은 별개입니다. UAPI의 Elf64_Nhdr는 Elf64_Word 세 개이고 그 Word는 32비트입니다.'),
        ('C에서 같은 줄에 note 두 개를 정의하면 어떤 문제가 가능한가?', '__LINE__ 기반 객체 이름이 같아 충돌할 수 있다', '두 note가 자동으로 하나의 description으로 합쳐진다', '고유 이름은 전역 카운터가 아니라 행 번호를 이용합니다. 헤더 주석도 한 줄에 하나만 정의하라고 명시합니다.'),
        ('asm ELFNOTE의 실제 매크로 정의는 인수가 몇 개인가?', 'name, type, desc 세 개이다', 'name, type, desctype, descdata 네 개이다', '주석에 오래된 네 인수 예시가 있지만 실제 정의는 세 인수입니다. 지시문과 데이터는 세 번째 인수에 함께 넣어야 합니다.'),
        ('동일 type=42를 서로 다른 name에서 쓰면 반드시 같은 의미인가?', '아니다. type은 name별 이름 공간 안에서 해석된다', '그렇다. ELF note의 type 번호는 모든 name에 걸쳐 동일 의미이다', '주석은 FooCo의 42와 BarProj의 42를 구별합니다. 소비자는 note의 이름과 type을 함께 해석해야 합니다.')
    ]
)]
