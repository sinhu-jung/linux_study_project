"""Whole UAPI errno definitions and architecture dispatch header."""
ROWS = []


def add(path, title, intro, principle, use, sections, questions):
    ROWS.append(dict(path=path, title=title, intro=intro, principle=principle,
                     use=use, area='UAPI · 오류 분류·ABI·전처리 별칭',
                     sections=sections, questions=questions))


add('include/uapi/linux/errno.h', '오류 UAPI 진입 헤더 전체: 아키텍처 정의에 위임하기',
    '한 줄의 include가 실제 오류 번호 선택을 다른 계층에 위임합니다.',
    '고정 원문 전체는 #include <asm/errno.h> 한 줄입니다. asm-generic/errno.h를 직접 포함하는 파일이 아닙니다.',
    '현재 타깃의 asm include 검색 경로를 따라 번호 정의를 확인합니다. 저장소의 generic 번호가 모든 아키텍처의 실제 번호라고 단정하지 않습니다.',
    [('전체 내용', '파일 자체에는 include guard,SPDX 줄,함수,상수 정의가 없습니다. 실제 원문에 없는 관례적 문구를 있다고 설명하지 않습니다.'),
     ('전처리 의존성', 'asm/errno.h는 아키텍처별 include 구성에 의해 선택됩니다. 사용자는 linux/errno.h라는 공통 이름을 사용해도 안쪽 정의는 타깃에 따라 달라질 수 있습니다.'),
     ('CS 연결', '공통 인터페이스와 플랫폼별 구현을 분리하는 예입니다. 오류 번호를 저장 형식이나 외부 프로토콜에 쓰려면 어떤 ABI의 값인지 구분해야 합니다. 이 헤더 자체는 번호를 번역하거나 실행 시 플랫폼을 탐지하지 않습니다.')],
    [('이 파일이 직접 포함하는 것은?', 'asm/errno.h', 'asm-generic/errno.h', '원문은 asm/errno.h 한 줄입니다. generic 정의 사용 여부는 선택된 아키텍처 헤더를 따라가야 합니다.'),
     ('공통 include 이름만으로 모든 타깃의 오류 번호가 같다고 할 수 있는가?', '없다. 실제 아키텍처 정의를 확인해야 한다', '있다. include 이름이 같으면 숫자도 자동 통일된다', '공통 진입점과 최종 숫자 정의 위치는 별개입니다. 전처리 검색 경로가 중요합니다.')])

add('include/uapi/asm-generic/errno-base.h', '기본 오류 번호 전체: 1부터34까지의 실패 분류',
    '기본 오류를 권한·객체·자원·I/O·수치 문제로 구분해 읽습니다.',
    'EPERM1부터ERANGE34까지 양의 정수 매크로34개를 정의합니다. 주석은 오류의 짧은 의미이며 어떤 함수가 언제 반환하는지는 사용처의 계약을 읽어야 합니다.',
    '매크로 정의는 오류 검출 코드나 스레드별 errno 저장소 자체가 아닙니다. 실패를 어떻게 반환하는지는 커널 함수·시스템 호출·라이브러리 인터페이스마다 구분합니다.',
    [('전체 파일', 'SPDX syscall note,guard,34개 define과 의미 주석,#endif로 구성됩니다. 다른 헤더 include나 함수·배열은 없습니다. 이 generic 파일에서는 번호1..34가 연속입니다.'),
     ('1부터10: 권한과 기본 객체', 'EPERM1은 허용되지 않는 동작,ENOENT2는 없는 파일·디렉터리,ESRCH3은 없는 프로세스,EINTR4는 인터럽트된 호출,EIO5는I/O오류,ENXIO6은없는장치·주소,E2BIG7은인자목록과다,ENOEXEC8은실행형식오류,EBADF9는잘못된파일번호,ECHILD10은자식프로세스없음입니다. 이름이 비슷해도 대상 객체와 실패 원인이 다릅니다.'),
     ('11부터18: 재시도·메모리·접근', 'EAGAIN11은다시시도,ENOMEM12는메모리부족,EACCES13은접근거부,EFAULT14는잘못된주소,ENOTBLK15는블록장치필요,EBUSY16은사용중,EEXIST17은이미존재,EXDEV18은장치경계를넘는연결을뜻합니다. 재시도 가능성을 말하는 이름만으로 무조건 즉시 반복하는 정책을 만들지 않습니다.'),
     ('19부터26: 장치·디렉터리·파일 제한', 'ENODEV19는장치없음,ENOTDIR20은디렉터리아님,EISDIR21은디렉터리임,EINVAL22는잘못된인자,ENFILE23은시스템파일테이블한도,EMFILE24는너무많은열린파일,ENOTTY25는역사적 Not a typewriter 주석,ETXTBSY26은실행텍스트사용중입니다. ENFILE과EMFILE을 같은 자원 한도로 혼동하지 않고 호출 문맥을 확인합니다.'),
     ('27부터34: 크기·저장소·수치 범위', 'EFBIG27은파일크기과다,ENOSPC28은장치공간없음,ESPIPE29는허용되지않는seek,EROFS30은읽기전용파일시스템,EMLINK31은링크과다,EPIPE32는끊어진파이프,EDOM33은수학적입력정의역문제,ERANGE34는결과표현범위문제입니다. 정의역과표현가능범위는 구분되는 개념입니다.'),
     ('ABI와 제어 흐름', '상수 이름은의미를드러내며매직넘버보다호출코드를읽기쉽게합니다. 이 파일에 -EIO 같은 음수 매크로는 없고 EIO=5가 있습니다. 호출자가 부호를 붙이는 관례와 매크로의 실제 값을 분리해서 확인합니다.')],
    [('EDOM과ERANGE의 차이는?', '입력 정의역 문제와 결과 표현 범위 문제다', '둘 다 디렉터리가 없다는 같은 오류다', '주석은EDOM을수학함수정의역,ERANGE를결과표현불가로구분합니다. 입력과출력범위는서로다른실패원인입니다.'),
     ('이 파일에서 EIO 매크로의 값은?', '양수5', '음수-5', '정의는 EIO5입니다. 커널 코드의 return -EIO는그양수상수에단항마이너스를적용한별도표현식입니다.'),
     ('ENOTDIR와EISDIR는 같은 조건인가?', '아니다. 디렉터리가 필요한데 아닌 경우와 디렉터리여서 맞지 않는 경우를 구분한다', '그렇다. 두이름이같은번호의별칭이다', '각각20과21의다른번호이며주석도반대의상황을표현합니다.'),
     ('이 헤더가 오류 발생 시 자동으로재시도하는가?', '아니다. 정수상수만정의한다', '그렇다. EAGAIN 정의가재시도루프를실행한다', '전처리define은실행가능한오류처리정책이아닙니다. 정책은호출자코드에있습니다.')])

add('include/uapi/asm-generic/errno.h', '확장 오류 번호 전체: 별칭·네트워크·복구 상태',
    '기본 오류를 포함하고 네트워크·IPC·파일시스템·키·복구 오류를 확장합니다.',
    'errno-base.h를 포함하고35..133 구간의정의와 EWOULDBLOCK/EDEADLOCK 별칭을 제공합니다.41과58에는별도숫자정의가없습니다.',
    '이 파일의 번호는generic 정의입니다. 오류 이름의간단주석을모든시스템호출의완전한반환조건으로확장하지않습니다.',
    [('전체 구조와 첫 구간', 'SPDX syscall note,guard,base include,상수·주석,#endif입니다.35 EDEADLK는교착위험,36 ENAMETOOLONG은이름길이,37 ENOLCK는레코드잠금부족,38 ENOSYS는없는시스템호출번호,39 ENOTEMPTY는비어있지않은디렉터리,40 ELOOP는심볼릭링크순회과다입니다.'),
     ('ENOSYS 특별 주석과 별칭', '주석은없는시스템호출의진입경로에서-ENOSYS를반환하므로실제존재하는시스템호출의실패와구분하도록구현에서이값사용을삼가라고설명합니다. 이는이파일의설계지침이며모든호출의실제반환을자동강제하는검사는아닙니다. EWOULDBLOCK=EAGAIN,EDEADLOCK=EDEADLK로정의되어이generic환경에서는같은번호입니다.'),
     ('42부터58: IPC와 오래된장치상태', 'ENOMSG42,EIDRM43은메시지없음과식별자제거입니다. ECHRNG44,EL2NSYNC45,EL3HLT46,EL3RST47,ELNRNG48,EUNATCH49,ENOCSI50,EL2HLT51은채널·계층·프로토콜부착상태를구분합니다. EBADE52,EBADR53,EXFULL54,ENOANO55,EBADRQC56,EBADSLT57은교환·요청·자원식별오류입니다.58의새번호는없고EDEADLOCK별칭이이어집니다.'),
     ('59부터74: stream과통신', 'EBFONT59는폰트형식,ENOSTR60는stream아님,ENODATA61는자료없음,ETIME62는타이머만료,ENOSR63은stream자원부족입니다. ENONET64,ENOPKG65,EREMOTE66,ENOLINK67,EADV68,ESRMNT69,ECOMM70,EPROTO71,EMULTIHOP72,EDOTDOT73,EBADMSG74는네트워크·패키지·원격객체·링크·광고·마운트·통신·프로토콜·다중홉·RFS·메시지형식의서로다른상태입니다. 역사적인이름도ABI정의로남아있습니다.'),
     ('75부터87: 표현·라이브러리·문자', 'EOVERFLOW75는자료형범위초과,ENOTUNIQ76는이름비고유,EBADFD77는FD상태,EREMCHG78은원격주소변경입니다. ELIBACC79,ELIBBAD80,ELIBSCN81,ELIBMAX82,ELIBEXEC83은공유라이브러리접근·손상·형식·개수·실행문제입니다. EILSEQ84는잘못된바이트열,ERESTART85는호출재시작관련번호,ESTRPIPE86은stream pipe, EUSERS87은사용자과다입니다. ERESTART85를커널내부ERESTARTSYS512와같은상수로보지않습니다.'),
     ('88부터99: socket의유형과주소', 'ENOTSOCK88,EDESTADDRREQ89,EMSGSIZE90,EPROTOTYPE91,ENOPROTOOPT92,EPROTONOSUPPORT93,ESOCKTNOSUPPORT94,EOPNOTSUPP95,EPFNOSUPPORT96,EAFNOSUPPORT97,EADDRINUSE98,EADDRNOTAVAIL99입니다. 각각socket여부,목적주소필요,메시지크기,프로토콜타입·옵션·지원,소켓타입지원,동작지원,프로토콜family·주소family지원,주소사용중·주소할당불가를구분합니다.'),
     ('100부터115: 연결의상태와진행', 'ENETDOWN100,ENETUNREACH101,ENETRESET102,ECONNABORTED103,ECONNRESET104,ENOBUFS105,EISCONN106,ENOTCONN107,ESHUTDOWN108,ETOOMANYREFS109,ETIMEDOUT110,ECONNREFUSED111,EHOSTDOWN112,EHOSTUNREACH113,EALREADY114,EINPROGRESS115입니다. 네트워크/호스트도달불가와연결거부,시간초과,진행중은다른관찰입니다. 이번호만으로특정장애원인을단정하지말고호출문맥을확인합니다.'),
     ('116부터129: 파일·매체·키', 'ESTALE116은오래된핸들,EUCLEAN117은구조정리필요,ENOTNAM118/ENAVAIL119/EISNAM120은XENIX관련상태,EREMOTEIO121은원격I/O,EDQUOT122는할당량초과입니다. ENOMEDIUM123,EMEDIUMTYPE124,ECANCELED125,ENOKEY126,EKEYEXPIRED127,EKEYREVOKED128,EKEYREJECTED129는매체없음·유형·취소·키없음·만료·폐기·거부를구분합니다.'),
     ('130부터133와CS', 'EOWNERDEAD130,ENOTRECOVERABLE131은robust mutex관련복구상태이며 ERFKILL132는무선차단,EHWPOISON133은하드웨어메모리오류입니다. 소유자종료를발견한것과상태를복구할수없는것은같지않습니다. 이헤더는상태이름을제공하지만복구절차를직접실행하지않습니다. ABI번호,별칭,실패분류,상태기계를연결해학습합니다.')],
    [('EWOULDBLOCK과EAGAIN은 이generic파일에서?', '같은번호다', '항상서로다른번호다', 'EWOULDBLOCK이EAGAIN으로정의됩니다. 다만generic한파일의사실을모든외부플랫폼으로일반화하지않습니다.'),
     ('EADDRINUSE와EADDRNOTAVAIL의구분은?', '주소가이미사용중인지,요청주소를할당할수없는지다', '둘다메모리부족만뜻한다', '각각98과99로분리되어있습니다. 실제원인은호출의바인딩·주소문맥과함께해석해야합니다.'),
     ('EOWNERDEAD와ENOTRECOVERABLE을동일하게처리해도되는가?', '아니다. 소유자종료발견과복구불가상태를구분해야한다', '된다. 같은번호의별칭이다', '130과131의별도정의입니다. 실제복구절차는robust mutex API계약을따라야합니다.'),
     ('이파일의ERESTART85가ERESTARTSYS512와같은가?', '아니다. 다른계층의서로다른상수다', '그렇다. 이름이비슷하므로값도같다', 'ERESTART는이UAPI헤더의85이고ERESTARTSYS는커널내부헤더의512입니다. 이름과번호·사용처를함께대조합니다.')])
