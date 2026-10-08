# Linux 소스 학습실

**Linux와 Windows에서 브라우저로 사용하는 OS 원리·기술·자료구조 학습 환경**입니다. macOS에서도 실행할 수 있습니다.

짧은 파일 읽기 → 직접 주석 달기 → 문제 풀기 → 다음 파일 순서로 공부합니다.
기본 화면은 **OS 원리·기술 3455단계, 6911문제**입니다. 필요한 문법은 별도의 **C 기초 11단계**에서 보충할 수 있습니다. 두 과정의 진도는 독립적으로 저장됩니다.

**Linux 전체를 연결해서 읽기:** 부팅·초기화 → 프로세스·스케줄링 → 메모리 → 파일시스템·저장장치 → 네트워크·IPC → 동기화·보안 → 장치·전원·시간 → 가상화·아키텍처·빌드 순으로 분야를 살펴보세요. 자료구조 수업은 해당 기능에서 사용하는 이유와 함께 연결해서 읽습니다. 분야별 검색은 [기술 교재](http://127.0.0.1:8765/knowledge), 순서 잠금 없이 해설과 문제를 읽으려면 [오프라인 전체 교재](course/syllabus.md)를 사용합니다. 학습실의 기존 단계별 진도와 직접 작성한 주석은 유지됩니다.

최근 추가한 `os3047`–`os3057`은 프로세스·메모리·파일시스템·네트워크·보안·저장장치·IPC·가상화에 걸친 11개 수업입니다. 숫자 계산, 실패 조건, 잠금과 객체 수명까지 설명하며 문제 22개와 풀이를 포함합니다. 전체 Linux의 모든 구현에 대한 해설 작성은 진행 중입니다.

**설명이 어려울 때 읽는 순서:** 앞쪽 150개 핵심 수업에는 **쉽게 풀어 읽기 · 이유와 숫자 예시**가 있습니다. 예를 들어 XArray 수업에서는 왜 빈 배열 칸도 공간을 쓰는지, `1000001칸 × 8바이트 = 8000008바이트`가 되는 이유, 두 칸짜리 배열과의 차이, XArray의 관리 비용까지 순서대로 설명합니다.

전체 3455개 OS 수업에는 **29개 분야의 공통 기초**와 **본문에 나온 용어 풀이**를 연결했습니다. 51개 용어 묶음 중 해당 수업에 실제 등장하는 표현을 골라 표시합니다. 포인터·NULL·희소·캐시·RCU·수명 같은 말은 항목을 펼치면 뜻과 예시를 읽을 수 있습니다. 공통 기초와 용어 해설은 반복해서 참고하는 자료이며, 모든 심화 수업을 개별적으로 다시 쓴 것으로 세지는 않습니다. 같은 설명은 오프라인 교재에도 포함됩니다.

## 1. 필요한 프로그램

학습 화면에는 **Python 3.9 이상과 Git**만 필요합니다. Docker, C 컴파일러, 추가 pip 패키지는 필요하지 않습니다.
최초 소스 다운로드에는 인터넷 연결이 필요하고, 다운로드 후에는 로컬에서 학습할 수 있습니다.

### Windows

1. [Python 공식 설치 안내](https://docs.python.org/3/using/windows.html)를 따라 Python을 설치합니다.
2. [Git 공식 다운로드](https://git-scm.com/downloads/win)에서 Git for Windows를 설치합니다. 터미널에서도 Git을 사용할 수 있는 PATH 옵션을 선택합니다.
3. 설치 후 새 PowerShell 창을 열어 확인합니다.

```powershell
py -3 --version
git --version
```

`py` 명령이 없고 `python --version`이 정상 동작해도 실행할 수 있습니다.

### Linux — Ubuntu / Debian

```bash
sudo apt update
sudo apt install python3 git
python3 --version
git --version
```

다른 배포판에서는 해당 패키지 관리자로 Python 3.9 이상과 Git을 설치하세요.

### macOS

Python 3.9 이상과 Git이 필요합니다. 이미 사용 중인 이 Mac은 제공된 Python 런타임과 Homebrew Git도 자동으로 찾습니다.
다른 컴퓨터에서는 [Python](https://www.python.org/downloads/)과 [Git](https://git-scm.com/downloads/mac)을 설치하세요. Codex 설치는 필수가 아닙니다.

## 2. 학습 폴더 가져오기

이 `linux-study` 폴더를 원하는 컴퓨터에 복사합니다. 실행 파일 하나만 복사하지 말고 `tools/`, `course/`, `labs/`를 포함한 폴더를 옮기세요.

- `linux/`까지 복사하면 소스를 다시 다운로드하지 않습니다. 숨김 폴더인 `linux/.git/`도 포함해야 합니다.
- `linux/`를 제외해도 됩니다. 첫 실행 때 공식 Linux v6.12 소스를 자동 다운로드합니다.
- 기존 진도를 이어가려면 서버를 종료한 뒤 `data/progress.sqlite3`도 함께 복사합니다.
- Docker 이미지와 볼륨은 다른 컴퓨터로 자동 복사되지 않습니다. 학습 화면에는 필요하지 않습니다.

설치 위치는 자유롭습니다. 예를 들어 Windows에서는 `C:\study\linux-study`, Linux에서는 `~/linux-study`에 둘 수 있습니다.

## 3. 실행하기

### Windows — PowerShell

학습 폴더로 이동한 뒤 실행합니다. 아래 경로는 실제 복사 위치로 바꾸세요.

```powershell
cd C:\study\linux-study
.\start-study.bat
```

파일 탐색기에서 `start-study.bat`를 더블클릭해도 됩니다. 오류 메시지를 확인하려면 PowerShell에서 실행하세요.
Python으로 직접 실행할 수도 있습니다.

```powershell
py -3 -X utf8 .\start-study.py
```

### Linux

```bash
cd ~/linux-study
bash start-study.sh
```

직접 실행하려면:

```bash
python3 -X utf8 start-study.py
```

### macOS

```bash
cd /Users/hankyung/project/linux-study
bash start-study.sh
```

`start-study.command` 더블클릭 또는 `./start-study.command`도 가능합니다. 다른 Mac에서는 실제 폴더 위치로 이동하세요.

### 공통

처음 실행하면 소스가 없는 경우 자동 다운로드합니다. 완료될 때까지 기다린 다음 브라우저에서 **[http://127.0.0.1:8765](http://127.0.0.1:8765)**를 엽니다.

- 실행한 터미널을 열어둡니다. 서버 종료는 **Ctrl+C**입니다.
- 이미 같은 학습 서버가 실행 중이면 접속 주소를 안내합니다.
- 다른 프로그램이 포트를 사용하면 아래처럼 다른 포트로 실행하세요.

Windows:

```powershell
.\start-study.bat --port 8766
```

Linux / macOS:

```bash
bash start-study.sh --port 8766
```

이 경우 접속 주소는 `http://127.0.0.1:8766`입니다. 주소의 `127.0.0.1`은 현재 컴퓨터를 뜻합니다.

소스만 미리 준비하려면 실행 명령 뒤에 `--setup-only`를 붙입니다.

## 4. OS 원리와 기술을 공부하는 방법

1. **왜 필요한가 → 어떤 원리로 동작하는가 → 어디에 쓰는가**를 읽습니다.
2. 조건을 선택하고 **다음 한 단계**로 원리 모델을 따라가며 결과를 예측합니다.
3. **기술을 사용하고 관찰하는 방법**에서 Linux 명령 또는 원본 탐색 방법과 결과 해석을 확인합니다.
4. 실제 커널의 짧은 발췌와 필요한 C 문법 설명을 읽습니다.
5. **직접 주석 달아보기**를 펼치고 코드 옆에 `//` 주석으로 이해한 내용을 적습니다.
6. 확인 문제의 답을 고르고 **정답 확인**을 누릅니다.
7. 막히면 **답지 보기**로 정답 해설과 주석을 단 예제를 확인합니다.
8. 모든 문제를 맞히면 **다음 파일로** 버튼이 열립니다.

답지만 열어서는 다음 단계가 열리지 않습니다. 문제의 답을 직접 선택해야 합니다.
주석과 선택한 답은 자동 저장되며, **저장됨** 표시를 확인하세요. 주석 내용 자체는 자동 채점하지 않습니다.
주석은 학습용 사본에 저장되며 원본을 수정하거나 실행하지 않습니다.
완료한 파일은 다시 볼 수 있고 서버를 재시작해도 진도가 유지됩니다.

OS 과정의 첫 16단계는 다음과 같습니다. 이어지는 3439개 수업의 전체 분야와 교재는 5절에 정리했습니다.

| 단계 | 원리·자료구조·기술 |
| --- | --- |
| 1–3 | 부팅, 시스템 호출과 권한 경계, 프로세스·태스크 상태 |
| 4–6 | 원형 이중 연결 리스트, EEVDF, augmented 레드블랙 트리 |
| 7–9 | 가상 주소·페이지 테이블·TLB·폴트, 버디, SLUB |
| 10–12 | VFS·함수 포인터, 페이지 캐시·writeback, mutex·spinlock·원자성·데드락 |
| 13–16 | 인터럽트·후속 처리, 패킷·TCP/UDP, 파이프·IPC, Copy-on-Write |

각 단계에 실제 Linux v6.12 원본 경로와 행 번호, 직접 주석을 다는 공간, 문제와 답지가 있습니다. 큰 파일은 특정 함수의 일부를 발췌하고 **커널 원본 전체와 앞뒤 문맥 보기**로 전체 파일에 연결합니다.
원리 모델은 조건별 상태 전이를 설명하는 학습용 모델이며 실제 커널 실행이나 전체 알고리즘 재현은 아닙니다. Linux 관찰 명령의 출력은 실행 환경·권한·설정에 따라 달라질 수 있습니다.

필요하면 왼쪽 **학습 과정**에서 C 기초 보충으로 전환하세요. C 과정은 다음과 같습니다.

| 단계 | 내용 |
| --- | --- |
| 1 | 프로그램 시작과 출력 |
| 2 | 변수 |
| 3 | 조건문 |
| 4 | 배열과 반복문 |
| 5 | 함수와 반환값 |
| 6 | 포인터 |
| 7 | 구조체와 `->` |
| 8 | 함수 포인터 |
| 9 | 매크로 |
| 10 | 파일 읽기 프로그램 |
| 11 | 실제 커널 원본 `lib/math/lcm.c` |

**전체 커널 소스 탐색** 링크는 `/explorer` 화면으로 연결됩니다. 이 화면에서는 86,680개 파일을 탐색하고 코드 문자열을 검색할 수 있습니다.
탐색 화면의 파일별 메모는 **진도·메모 저장** 버튼으로 수동 저장합니다. 입문 과정의 자동 저장과 다릅니다.

## 5. 분야별 기술 교재

[기술 교재](http://127.0.0.1:8765/knowledge)의 기본 검색 대상은 **해설·문제·답지가 있는 3455개 수업**입니다. RCU, XArray, Maple Tree, DMA, io_uring, KVM, ALSA 등의 키워드와 분야 필터로 찾을 수 있습니다. 학습실에서는 앞 단계를 완료해야 다음 단계가 열립니다.

수업마다 필요한 이유, 동작 원리, 사용 조건, 실제 소스 발췌, 관찰 방법, 조건별 풀이, 확인 문제와 답지가 있습니다. 추가 수업의 조건별 예측·풀이는 실제 커널 실행이나 전체 알고리즘 시뮬레이션이 아닌 설명용 예제입니다.

전체 해설과 문제·답지는 브라우저 없이 **[course/syllabus.md](course/syllabus.md)**에서도 읽을 수 있습니다. 분야·수업 목록은 **[course/coverage.json](course/coverage.json)**에 기록합니다.

| 분야 | 수업 수 |
| --- | ---: |
| OS 시작 | 16 |
| 자료구조 | 26 |
| 알고리즘 | 5 |
| 프로세스 | 42 |
| 스케줄링 | 21 |
| 동기화 | 339 |
| 비동기 처리 | 11 |
| 시간 | 89 |
| 메모리 | 124 |
| 파일시스템 | 116 |
| I/O | 34 |
| 네트워크 | 99 |
| 격리·보안 | 62 |
| 장치·드라이버 | 832 |
| 전원 | 37 |
| 가상화 | 17 |
| 관찰·디버깅 | 383 |
| 빌드·초기화 | 58 |
| CPU·아키텍처 | 239 |
| IPC | 14 |
| 저장장치 | 30 |
| 주변장치 | 26 |
| 암호 알고리즘 | 69 |
| 전송 알고리즘 | 8 |
| 언어·확장 | 7 |
| 자료구조·알고리즘 | 89 |
| 장치와 하드웨어 | 42 |
| 라이브러리·알고리즘 | 556 |
| 트래픽 제어 알고리즘 | 64 |

작성 목표는 고정된 Linux v6.12의 기술·자료구조·알고리즘을 원리·사용 조건·문제·풀이까지 채우는 것입니다. 현재 학습실에는 OS 3455개 수업과 6911개 문제·풀이를 반영했습니다. 현재 이름을 붙인 계획 3305개는 모두 수업에 연결됐습니다. 이 계획 목록이 전체 Linux 구현 목록은 아니며 미검토 파일과 의미 검토 작업은 별도로 남아 있습니다. 작성된 각 수업에 개념 설명·사용 관찰·문제·정답·풀이가 있습니다. 다만 이것은 Linux 전체 86680개 파일의 모든 구현과 세부 기술을 빠짐없이 의미 검토했다는 뜻은 아닙니다. 파일 전체 검토는 `course/source-audit.json`에서 증거를 기준으로 따로 추적하며, 현재 전체 검토가 기록된 파일은 377개입니다. 원문 검색은 해설로 세지 않습니다.

최근 추가한 `os2888`–`os2902`는 인터럽트 재전달·CPU 이동·레거시 IRQ 탐색의 15개 수업과 30개 문제입니다. `kernel/irq/resend.c`, `migration.c`, `autoprobe.c`의 전체 구현을 읽고 정상 경로뿐 아니라 중복 요청·없는 부모·문맥 제한·설정별 대체 구현·잠금·마스킹 복원·재시도·종료 정리를 설명했습니다. “왜 필요한가”는 중복 목록 연결의 위험, CPU 집합의 교집합 계산, 기존 마스킹을 보존해야 하는 이유 같은 구체적인 사례로 풉니다. 학습실에서는 기존 순서 뒤에 이어지며, [오프라인 전체 교재](course/syllabus.md)에서 단원 번호로 바로 찾을 수도 있습니다. 검토 기록은 `data/irq-replay-migration-probe-review.json`에 있습니다.

`os2903`–`os2927`에는 CPU 오프라인·온라인 시 IRQ 이동과 시스템 절전·깨우기·복귀를 다루는 25개 수업과 50개 문제를 추가했습니다. `kernel/irq/cpuhotplug.c`와 `kernel/irq/pm.c` 전체 17개 함수를 읽고, 요청/실제 CPU 집합·벡터 부족 재시도·관리형 IRQ 중단과 복원·공유 action 정책·깨우기 재무장·중첩 disable 횟수·조기 복원 필터를 설명합니다. 조건이 달라질 때의 집합 계산과 상태 변화는 각 수업의 예제와 풀이에서 확인할 수 있습니다. 원문 대조 기록은 `data/irq-hotplug-pm-review.json`입니다.

`os2928`–`os2951`은 미처리 IRQ 감지·복구 폴링과 IRQ debugfs의 24개 수업, 48개 문제입니다. `kernel/irq/spurious.c`와 `kernel/irq/debugfs.c` 전체 22개 함수를 읽고 지연된 스레드 결과 분석, 시간 간격과 엄격한 임계값, 복구 성공 보정, 원자 폴러 진입, 타이머, 상태 이름 표, 부모 계층 재귀, 파일 연산, 입력 접두어 비교와 문자열 수명을 설명합니다. 원문에 없는 성공 보장이나 자동 오류 복구를 덧붙이지 않고, 경계값·실패·생략 경로를 풀이에 포함했습니다. 검토 기록은 `data/irq-spurious-debugfs-review.json`입니다.

`os2952`–`os2968`에는 장치 수명에 연결된 IRQ 자원 관리와 다중 큐 affinity 구성의 17개 수업, 34개 문제를 추가했습니다. `kernel/irq/devres.c`와 `kernel/irq/affinity.c` 전체 15개 함수를 읽고 준비·획득·공개·실패 정리, IRQ와 cookie 식별, 양수 성공 코드, 역순 해제, 오류 포인터, 앞뒤 예약 벡터, 세트별 CPU mask 복사, 기본 mask와 관리 비트 차이 및 가능한 CPU 수 기반 계산을 설명합니다. 원문 대조 기록은 `data/irq-devres-affinity-review.json`입니다.

`os2969`–`os2993`은 `kernel/irq/irqdomain.c`의 1–863행을 다루는 25개 수업과 50개 문제입니다. 펌웨어 식별 노드, 이름 소유권, 생성·공개·제거, 검색 콜백, 전역 기본 domain, 선형 배열과 radix tree 역매핑, 연결 실패 정리와 기존 매핑 재사용을 설명합니다. **이 파일은 아직 전체 검토 완료가 아닙니다.** 후속 수업에서 864–1253행을 추가했으며 현재 파일 끝까지 구간별 수업을 작성했으며 전체 정의·설정 분기와 수업의 누락 대조 검토가 남아 있습니다. 진행 기록은 `course/source_reviews.json`의 `in_progress` 항목과 `data/irq-domain-base-review.json`에서 확인할 수 있습니다.

`os2994`–`os3007`은 같은 파일의 864–1253행을 다루는 14개 수업과 28개 문제입니다. 펌웨어 셀 변환, 트리거 충돌과 기존 연결 재사용, 계층별 할당 경로, 매핑 조회·처분, RCU 읽기 구간, 번호 할당 힌트, 부분 초기화를 설명합니다. 출력 값이 실패 때 남는 이유와 잠금 범위, 배열 길이 계약을 예제로 풀었습니다. 이 구간의 기록은 `data/irq-domain-fwspec-review.json`에 있으며 파일 전체 완료로 세지 않습니다.

`os3008`–`os3015`는 같은 파일의 1254–1445행을 다루는 8개 수업과 16개 문제입니다. 부모 domain 생성, 단계별 역매핑, 실행 동기화, 부모 데이터 공유와 해제, 단절 표식과 사슬 검증을 설명합니다. 해제 전에 다음 주소를 읽는 이유와 잘못된 표식 배치를 거절하는 이유를 예제로 풀었습니다. 기록은 `data/irq-domain-chain-review.json`에 있으며 후속 수업에서 1446–1603행을 추가했으며 남은 구간은 후속 기록에서 계속 추적합니다.

`os3016`–`os3023`은 1446–1603행의 부모 데이터 할당·검색·설정과 계층 콜백을 다루는 8개 수업·16개 문제입니다. 부분 실패의 정리 범위, 포인터 비교, 필드와 역매핑의 차이, 오류 전파와 콜백 호출 단위를 설명합니다. 검토 기록은 `data/irq-domain-setup-review.json`에 있습니다.

`os3024`–`os3027`은 1604–1713행의 주 할당·실패 정리·root mutex·이동 후 역매핑 복구를 다루는 4개 수업·8개 문제입니다. 자원 확보와 활성화를 나누는 이유, 모든 trim 후 매핑을 공개하는 순서, 재사용 descriptor의 실패 시 수명을 설명합니다. 기록은 `data/irq-domain-alloc-review.json`이며 후속 수업에 이어 현재는 파일 끝까지 구간별 작성 후 전체 누락 대조 검토를 남겨 두었습니다.

`os3028`–`os3032`는 1714–1866행의 계층 push/pop을 다루는 5개 수업·10개 문제입니다. handler 등록 전후의 호출 계약, 얕은 구조체 복사, 실패 복원, 주소 이동에 따른 역매핑 수정과 부모 보존 순서를 설명합니다. 기록은 `data/irq-domain-pushpop-review.json`에 있습니다.

`os3033`–`os3038`은 1867–2004행의 범위 해제·부모 자원 위임·활성화/비활성화를 다루는 6개 수업·12개 문제입니다. 부모 우선 활성화와 자식 우선 비활성화, 실패 시 부모 rollback, reserve와 활성 비트의 관계를 예제로 설명합니다. 기록은 `data/irq-domain-lifecycle-review.json`이며 2005–2135행은 후속 수업에서 다룹니다.

`os3039`–`os3044`는 2005–2135행의 설정별 대체 구현과 debugfs를 다루는 6개 수업·12개 문제입니다. 비계층 검색·설정의 차이, 진단 필드와 부모 출력, 기본 domain 선택, 파일 생성·삭제를 설명합니다. `data/irq-domain-tail-review.json`에 기록했으며 전체 정의·분기와 기존 수업을 대조하기 전까지 파일 전체 검토 상태는 `in_progress`로 유지합니다.

검색 대상을 바꾸면 고정 커널의 전체 추적 파일 **86,680개**, `Documentation/` 파일 **10,122개**, 문서 제목·절 제목 **33,698개**도 탐색할 수 있습니다. 문서 수에는 일반 설명 문서 4,909개, YAML 장치 바인딩 규격 4,380개, 보조 파일이 포함됩니다. 제목에는 번역·중복이 있습니다.

첫 실행 때 `data/knowledge.json`을 자동 생성합니다. 필요하면 다음 명령으로 다시 만들 수 있습니다.

```bash
# Linux / macOS (Python과 Git이 PATH에 있을 때)
python3 tools/index_knowledge.py
```

```powershell
# Windows
py -3 -X utf8 .\tools\index_knowledge.py
```

## 6. 파일과 진도 보관

| 경로 | 용도 |
| --- | --- |
| `start-study.py` | 운영체제 공통 실행과 소스 준비 |
| `start-study.bat` | Windows 실행 |
| `start-study.sh` | Linux / macOS 실행 |
| `start-study.command` | macOS 더블클릭 실행 |
| `course/files/` | 작은 C 학습 예제 |
| `course/lessons.json` | 두 과정의 원리, 사용법, 모델, 문제, 답지 |
| `course/topics.py` | 추가 134개 수업의 주제별 해설·문제 원고 |
| `course/syllabus.md` | OS 3455개 수업 전체 해설·문제·답지 |
| `course/coverage.json` | 29개 분야와 수업 작성 명세 |
| `tools/build_curriculum.py` | 원고와 고정 원본을 연결해 교재 재생성 |
| `course/reading_support.py` | 분야 기초·용어 풀이와 핵심 150개 수업의 인과관계 예시 |
| `data/knowledge.json` | 전체 파일·문서 제목 색인, 자동 재생성 가능 |
| `tests/review_course.py` | 원본·진도·내용 구조·누락 검수 |
| `data/review-report.json` | 검수 결과와 한계 |
| `tools/` | 학습 서버와 화면 |
| `linux/.git/` | 공식 커널 전체 소스 원본 |
| `data/progress.sqlite3` | 주석, 선택한 답, 완료 단계, 탐색 메모 |
| `labs/`, `notes/` | 실습 예제와 노트 |

진도를 백업하려면 서버를 종료한 뒤 `data/progress.sqlite3`를 복사하세요. 다른 컴퓨터에서도 같은 위치에 넣으면 이어서 공부할 수 있습니다.
컴퓨터 간 진도는 자동 동기화되지 않습니다.

소스 버전은 **Linux v6.12**, 기준 커밋은 `adc218676eef25575469234709c2d87185ca223a`입니다.
학습을 위한 고정 버전입니다. 전체 파일은 포함하지만 과거 전체 커밋 이력은 받지 않습니다.
Windows와 Mac의 파일 이름 대소문자 충돌을 피하려고 일반 체크아웃을 만들지 않고 Git 원본에서 파일을 읽습니다. `linux/`가 비어 보이고 `.git`만 있어도 정상입니다.

## 7. 선택 사항: C 실행과 커널 빌드

아래는 학습 화면과 별도인 Linux 실습입니다. 입문 문제를 풀 때는 설치할 필요가 없습니다.

- Linux: Docker의 Linux 컨테이너 환경이 필요합니다.
- Windows: [WSL 공식 설치 안내](https://learn.microsoft.com/en-us/windows/wsl/install)에 따라 WSL2 Ubuntu를 준비하고 Docker Desktop의 WSL 통합을 활성화합니다. 아래 명령은 **WSL의 Bash 터미널**에서 실행하세요.
- macOS: Docker Desktop을 실행합니다.

Windows에서 폴더를 `C:\study\linux-study`에 두었다면 WSL 경로는 `/mnt/c/study/linux-study`입니다.
WSL 안에서 `python3`, `git`, `docker` 명령이 사용 가능해야 합니다.

새 컴퓨터에서 Docker 실습 환경 준비:

```bash
cd /실제/학습폴더
bash start-study.sh --setup-only
bash tools/lab.sh image
bash tools/lab.sh init
```

실습 명령:

```bash
bash tools/lab.sh read   # 예제를 컴파일하고 strace로 호출 확인
bash tools/lab.sh shell  # Linux 실습 셸
bash tools/lab.sh build  # ARM64 커널 빌드
bash tools/lab.sh boot   # QEMU 부팅
```

이미지 이름은 `linux-study:v6.12`, 볼륨 이름은 `linux-study-v612`입니다.
소스는 볼륨의 `/work/linux`, 빌드 결과는 `/work/build`, 실습 파일은 `/labs`에 있습니다.
`read`는 Docker 호스트 커널에서 실행되고, `boot`는 직접 빌드한 커널을 QEMU에서 실행합니다.
QEMU 종료는 **Ctrl+A를 누른 다음 X**입니다.

현재 QEMU 실습은 ARM64 기준으로 검증했습니다. x86_64 컴퓨터에서 빌드할 경우 ARM64 컴파일 자체는 LLVM을 사용하지만, 부팅용 BusyBox도 ARM64 실행 파일이어야 합니다. x86_64용 컨테이너에서 생성한 BusyBox를 그대로 넣으면 부팅 실습은 실패합니다. 학습 화면과 입문 과정은 CPU 아키텍처와 무관하게 실행됩니다.

`init`은 소스를 다시 풀고 커널 설정을 초기화하므로 직접 수정한 소스를 덮어쓸 수 있습니다. 초기 설치 때만 사용하세요.
기본 설정은 최소 ARM64 커널입니다. 네트워크와 다른 드라이버를 공부할 때 필요한 설정을 추가해야 합니다.
넓은 기본 설정은 `bash tools/lab.sh defconfig`, 최소 설정 복원은 `bash tools/lab.sh configure`입니다. 바꾼 뒤 다시 빌드하세요.

## 8. 문제가 생기면

- **Python을 찾을 수 없음:** Python 설치 후 터미널을 다시 엽니다. `python --version` 또는 `py -3 --version`으로 확인하세요.
- **Git을 찾을 수 없음:** Git 설치 후 터미널을 다시 열고 `git --version`을 확인하세요.
- **소스 다운로드 실패:** 인터넷 연결을 확인하세요. 실패한 `linux` 폴더는 내용을 확인하고 다른 이름으로 옮긴 후 재실행하세요. 실행 프로그램은 기존 파일을 자동 삭제하지 않습니다.
- **`linux` 폴더의 버전이 다름:** 기존 폴더를 다른 이름으로 보존한 후 다시 실행하면 학습 기준 소스를 다운로드합니다.
- **화면이 안 열림:** 터미널에 서버 시작 메시지가 있는지 확인하고 표시된 포트로 접속하세요. HTML 파일을 직접 더블클릭해서 열면 API가 동작하지 않습니다.
- **`Address already in use`:** 같은 학습 서버라면 브라우저로 바로 접속합니다. 다른 프로그램이면 `--port 8766`을 사용하세요.
- **스크립트 실행 권한 오류:** Linux에서는 `bash start-study.sh`로 실행하세요.
- **주석이 안 보임:** 동일한 `data/progress.sqlite3`를 사용 중인지 확인하세요.

실행할 Python 또는 Git을 직접 지정할 수도 있습니다. `STUDY_PYTHON`은 Python 실행 파일 경로, `STUDY_GIT`은 Git 실행 파일 경로입니다.

Linux / macOS:

```bash
STUDY_PYTHON=/실제/python3 STUDY_GIT=/실제/git bash start-study.sh
```

Windows PowerShell:

```powershell
$env:STUDY_PYTHON = 'C:\실제\python.exe'
$env:STUDY_GIT = 'C:\실제\git.exe'
.\start-study.bat
```

개별 원본 함수의 실행 예제와 compiler 명령은 [원본 검증 사용법](data/source_checks/README.md)에 있습니다. Linux 또는 Windows의 WSL에서 예측한 답을 실제 C 함수 결과와 비교할 수 있습니다. 학습 화면을 쓰는 데 C compiler는 필요하지 않습니다.

## 9. 검수와 검증 범위

macOS에서 실행했고, Linux 컨테이너에서도 공통 실행 파일·소스 조회·입문 과정·검색을 확인했습니다.
Windows용 실행 파일과 운영체제 공통 코드를 추가했지만, 현재 Windows 컴퓨터에서 직접 실행한 검증은 하지 못했습니다.


전체 검수 실행기는 현재 교재와 검사 코드의 해시를 기록하고 기본으로 **101회** 검사합니다. 회차마다 다른 한글 주석·선택 답·잘못된 입력을 사용합니다. 현재 버전의 완료 회차는 `data/review-report.json`과 `data/reviews/<버전 해시>/ledger.json`에서 확인하세요. 실행 중 교재가 바뀌면 해당 버전의 검사 기록을 섞지 않고 중단합니다.
검수는 학습자 진도 대신 임시 데이터베이스를 사용합니다. 자동 검사 횟수와 전체 기술의 내용 완성은 별도로 확인합니다.

```bash
python3 tools/review_rounds.py
```

```powershell
py -3 -X utf8 .\tools\review_rounds.py
```

Mac에서는 OS/C 과정 전환과 원리 모델 단계를 브라우저에서 확인했고, Linux 컨테이너에서는 새 과정·검색·지식 목록을 별도로 확인했습니다. 상세 결과는 `data/review-report.json`, 버전별 회차 기록은 `data/reviews/`에 있습니다.

## 전체 해설 작성 진행 관리

`course/planned_topics.json`에 추가 주제를 기록하고 `python3 tools/audit_coverage.py`로 `course/requirements.json`과 `data/coverage-audit.json`을 갱신합니다. 실제 학습 화면에 반영한 수업과 다음 반영을 위해 작성한 초안은 구분합니다. 추가 누락은 원본과 문서를 검토하면서 계속 등록하고 해설·문제·풀이를 작성합니다.

`course/source-audit.json`은 고정 버전의 모든 86,680개 경로를 추적합니다. `linked`는 수업에서 원본을 참조했다는 뜻입니다. 파일 전체의 의미 검토는 `course/source_reviews.json`의 SHA·판정·증거가 있어야 기록됩니다. 따라서 파일 검색과 원본 연결을 작성된 해설로 계산하지 않습니다.

## 선택 실습: fd 알림의 실제 사용법

`labs/fd_notifications.c`는 주석이 있는 작은 사용자 C 예제입니다. Eventfd의 누적 counter와 semaphore mode, Signalfd의 128byte signal record, Timerfd의 만료 횟수를 직접 읽습니다. 예측 문제와 접어 둔 답지는 `labs/fd_notifications.md`에 있습니다.

Linux 또는 Windows의 WSL에서 C 컴파일러를 사용해 실행합니다. 학습실 화면 실행에는 C 컴파일러가 필요하지 않습니다.

```sh
cc -std=c11 -Wall -Wextra -Werror labs/fd_notifications.c -o /tmp/fd-notifications
/tmp/fd-notifications
```

프로젝트의 Docker Linux 이미지가 이미 준비되어 있다면 macOS에서도 실행할 수 있습니다.

```sh
docker run --rm -v "$PWD/labs:/labs:ro" linux-study:v6.12 bash -c 'cc -std=c11 -Wall -Wextra -Werror /labs/fd_notifications.c -o /tmp/fd-notifications && /tmp/fd-notifications'
```

이 예제는 Ubuntu Linux 컨테이너에서 경고 없이 컴파일하고 모든 예상 출력을 확인했습니다.

### 원자 연산과 생성기 추가 검증 기록

추가 작성 중인 원문 기반 수업은 별도 후보에서 확인한 뒤 공개 과정에 통합합니다. 현재 공개 수업 수와 추가 후보의 수업 수는 다를 수 있습니다. 주석과 채점 진도는 통합 전후에 비교해 보존합니다.

- `data/source_checks/source-atomic64-harness-manifest.json`: generic atomic64 원문 전체를 잠금·IRQ 모델에 연결했습니다. 캐시라인 64·128바이트와 최적화·ASan·UBSan 네 구성에서 각각 560,034건, 4스레드의 40,000개 중복 없는 fetch 이전 값을 확인했습니다.
- `data/source_checks/source-atomic-long-harness-manifest.json`: 원문 85개 atomic_long wrapper의 반환·저장·expected 갱신 820건이 최적화와 ASan·UBSan에서 각각 통과했습니다. 실행은 native64이며 메모리 순서 계약은 고정 원문 문서와 대조합니다.
- `data/source_checks/source-atomic-generator-manifest.json`: 명세·타입·인자·순서 변형·템플릿 우선순위와 실제 shell 변수 문맥 81건을 macOS·Linux에서 각각 확인하고 long 헤더 전체를 재현했습니다.
- `data/source_checks/source-atomic-pipeline-manifest.json`: 원문 세 generator와 상위 pipeline을 macOS·Linux의 임시 복사에서 실행하여 계측·long·arch fallback 헤더의 전체 내용과 마지막 해시 행이 고정 원문과 일치함을 확인했습니다.
- `data/source_checks/source-atomic-instrument-harness-manifest.json`: 전체 계측 wrapper 255개를 컴파일하고 선택 33개 API 사례·여섯 generic try 매크로를 반복 실행했습니다. hook 순서·주소·폭·실패 경로·expected 갱신·ordinary 포인터 평가 306,000건이 최적화와 ASan·UBSan에서 각각 통과했습니다.

각 실행은 manifest에 기록한 모델과 입력 범위의 검사입니다. 실제 커널의 KASAN·KCSAN 탐지, 모든 CPU·ABI·LKMM·모든 스케줄의 진행성 검사와 구별합니다. 코드 생성 일치만으로 생성된 헤더의 모든 개념에 해설이 완성되었다고 판정하지 않습니다. 작성한 해설·문제·풀이와 원문 검토 범위를 각각 기록하며 전체 내용의 작성은 계속 진행 중입니다.

### 접근 검사·watchpoint·초기화 추적 수업의 실습

[원본 검증 사용법](data/source_checks/README.md)의 `run-sanitizer-checks.py --sanitize` 명령은 접근 검사 인터페이스, KCSAN 주소 압축·겹침·보고 정책, KMSAN shadow·origin·페이지 연결·compiler hook·전송 경계·오류 보고·부팅 초기화·공개 API를 68개 빌드로 재현합니다. Linux 컨테이너에서 README의 명령 그대로 통과했으며 기록은 `data/source_checks/sanitizer-runner-verification.json`에 있습니다. Windows에서는 이 선택 C 실습을 WSL에서 실행합니다. 브라우저 학습실은 위의 Windows 실행법을 사용하세요.

새 수업에는 주소와 길이·접근 방향, 실제 데이터와 metadata, 원자 접근 표시와 실제 동기화, 부분 복사와 초기화 상태, 같은 원인의 보고 구간, 성공·실패 경로의 자원 정리를 각각 설명하는 문제와 답지를 넣었습니다. 원문에서 관찰한 오류 경로와 문서·구현의 차이도 풀이에서 구별합니다. 실습 명령은 저장한 학습 주석과 진도를 변경하지 않습니다.

스택·프레임·hash 실습은 `python3 data/source_checks/run-stack-checks.py --sanitize`로 실행합니다. 공통 스택 수집·arm64 프레임 범위·Stack depot·Jenkins hash의 유한 모델 62빌드를 Linux에서 재현했습니다. Kconfig 설정 원리는 `python3 data/source_checks/verify-kmsan-kconfig-model.py`로 검사합니다. 실제 kernel boot·모듈 빌드·전체 동시성 검증 범위는 각 manifest와 [원본 검증 사용법](data/source_checks/README.md)에 구분했습니다.


IRQ domain 대조 보강: `os3045`–`os3046`은 debugfs 비활성 빌드의 빈 helper와 실제 삭제 wrapper를 2개 수업·4개 문제로 설명합니다. `data/irq-domain-reconciliation-review.json`에 보강 기록을, `data/irq-domain-definition-inventory.json`에 설정별 정의와 수업 후보의 대조 목록을 기록합니다. 후보 연결은 설명 완성의 자동 증명이 아니며 전체 의미 검토는 아직 진행 중입니다.

보조 함수 대조 기록: `data/irq-domain-helper-review.json`은 이름 생성·최종 해제·simple/legacy wrapper 5개 정의의 본문 검토를 기록합니다. 이름 할당 예제와 실패 시 필드 변화를 보강했고, 먼저 작성한 7개 단원의 오래된 미작성 구간 안내를 현재의 전체 대조 검토 상태로 수정했습니다.

보조 함수 추가 대조: `data/irq-domain-helper-review-2.json`은 기본 domain 조회·역매핑 삭제·연결 wrapper·OF 셀 변환 5개 정의를 기록합니다. 4개 수업의 포인터 수명과 검사 범위를 보강했습니다. 정의별 수동 본문 대조는 누적 10개이며, 함수 호출 대상의 전체 구현이나 파일 전체 완료를 뜻하지 않습니다.

보조 함수 대조 완료 범위: `data/irq-domain-helper-review-3.json`에 부모 해제·비활성화·설정별 대체 구현 등 7개 정의의 분기 대조를 추가했습니다. 독립 원문 시작점 없이 다른 수업에 묶여 있던 17개 정의는 본문 대조를 마쳤습니다. 나머지 69개 정의의 최종 분기 대조와 표·전역 객체 검토는 남아 있습니다. 교재 내용은 이 검토에서 변경하지 않았으며 이전 회귀 검사와 동일한 버전임을 해시로 확인했습니다.

생성 경로 대조: `data/irq-domain-creation-review.json`에 fwnode·이름 선택·domain 생성 6개 정의를 기록했습니다. `os2969`에서 첫 멤버 fwnode의 주소를 바깥 객체와 다르다고 설명한 오류를 바로잡았습니다. 현재 최종 본문 대조는 23/86개이며 나머지 63개와 표·전역 객체 검토가 남아 있습니다.

공개·제거 경로 대조: `data/irq-domain-publication-review.json`에 공개, descriptor 준비, instantiate, 제거, bus token 변경의 6개 정의를 대조한 근거를 기록했습니다. 경고 후 계속 진행, 조건부 정리, 실패 시 token 미복원까지 기존 수업에 반영돼 있음을 확인했습니다. 최종 정의 대조는 29/86개이며 57개가 남아 있습니다. 교재는 변경하지 않았고 기존 회귀 검사 버전과 해시가 일치합니다.

검색·연결 대조: `data/irq-domain-mapping-review.json`에 8개 정의를 기록했습니다. 검색 콜백의 비0 판정, signed 반복 개수, setter의 NULL 인자와 내부 저장값 차이를 3개 수업에 명확히 반영했습니다. 최종 본문 대조는 37/86개이며 49개와 표·전역 객체 검토가 남아 있습니다.

펌웨어 매핑 대조: `data/irq-domain-firmware-reconciliation.json`에 직접·일반 매핑, firmware 변환·복사, 기존 트리거 비교, 계층/MSI 분기, OF wrapper와 처분 등 8개 정의의 분기 검토를 기록했습니다. 최종 정의 대조는 45/86개이며 41개가 남아 있습니다. 교재 변경 없이 기존 회귀 검사와 동일한 버전임을 확인했습니다.

조회·계층 데이터 대조: `data/irq-domain-chain-reconciliation.json`에 14개 정의를 기록했습니다. setter의 NULL 인자와 저장값 차이, trim의 유효 descriptor 전제를 보강했습니다. 최종 정의 대조는 59/86개이며 27개와 표·전역 객체 검토가 남아 있습니다.


전체 Linux 확장 방식: `data/linux-wide-coverage-plan.json`에 최상위 소스 영역별 현황과 순환 작성 순서를 기록했습니다. 특정 IRQ 파일의 반복 검토보다 프로세스·메모리·파일시스템·네트워크·보안·I/O·가상화·아키텍처 등 전체 영역의 실제 해설 보강을 우선합니다. `os3047`–`os3052`는 다섯 영역에 걸친 6개 수업·12개 문제로, 상태 공유·OOM 점수·파일시스템 등록과 RCU 해제·IPv4 변환·낮은 주소 정책을 다룹니다. 전체 구현 완료와는 구분합니다.

저장장치·IPC·가상화 보강: `os3053`–`os3057`에 큐 제한값 갱신, IPC 권한 비트 계산, 식별자 재사용과 세대 검사, KVM 참조 수명, 게스트 프레임 번호 트리의 5개 수업·10개 문제를 추가했습니다. 앞의 다섯 영역과 합쳐 이번 확장은 8개 분야·11개 수업·22개 문제입니다. 각 수업은 필요성 → 원리 → 숫자·상태 예제 → API 사용 조건 → 오류와 주의점 → 문제·풀이로 읽을 수 있습니다. 검토 기록은 `data/linux-cross-subsystems-review.json`입니다.

연속 작성 `os3058`–`os3076`: 스케줄러 깨움과 상태 관찰, io_uring 참조, initcall, Rust 오류, 페이지 캐시 조회·생성·접근 기록, 파일 권한, 장치 이름, IPv4 체크섬, 타임아웃·밀리초 대기, 런타임 PM, 깨움 이벤트 경쟁, 시스템 절전 요청의 19개 수업·38개 문제를 추가했습니다. 원문 검토 및 검수 증거는 `data/linux-execution-cache-power-review.json`에 기록합니다. 이후 작성도 전체 완료 조건을 충족할 때까지 계속합니다.

연속 작성 `os3077`–`os3097`: SysV 메시지 할당·복사·해제, capability와 파일 자격, eventfd, x86-64·arm64·RISC-V syscall, 블록 요청 및 BIO 수명, 패킷 버퍼 공유·복사의 21개 수업·42개 문제를 추가했습니다. 검토 기록은 `data/linux-ipc-syscall-block-packets-review.json`입니다. `io_uring/refs.h`는 파일 전체의 참조 모드·각 helper·검사 매크로·헤더 구성을 3개 수업과 대조한 근거를 기록했습니다. 전체 Linux 해설 목표는 활성 상태로 이어갑니다.

`os3098`–`os3102`는 부팅 전용 메모리 수명, 사용자 init 선택, fd 예약·파일 연결, cgroup 공통 조상 권한과 임시 자격 복원을 다루는 5개 수업·10개 문제입니다. 실패 시 어떤 자원을 반환하는지와 조건별 실행 순서를 풀이합니다. 검토 기록: `data/linux-boot-vfs-cgroup-review.json`.

`os3103`–`os3117`은 TCP RTT·편차·RTO·pacing, mempool 예약 및 반환, 가중 가상 시간·EEVDF deadline·실행 회계, exec의 되돌릴 수 없는 경계, 장치 probe 및 DMA 매핑의 15개 수업·30개 문제입니다. 단위·배율·자원 소유와 실패 정리를 수치 및 상태 예제로 풀이했습니다. 검토 기록: `data/linux-timing-memory-exec-review.json`.

`os3118`–`os3125`는 Rust와 C의 오류·포인터 변환, 오류 정보의 축약, 파일 열기 정책, 부모 dentry 참조, writeback 대기의 8개 수업·16개 문제입니다. NULL 포인터와 성공 결과의 차이, 참조 수명과 부모 관계 안정성의 차이, 대기 완료와 영속성의 차이를 설명합니다. 검토 기록: `data/linux-rust-vfs-writeback-review.json`.

`os3126`–`os3131`은 모듈 로딩의 inode 해시·대기 알림·신호 경쟁·권한 검사, Kconfig의 n/m/y 논리·캐시·문자열 및 숫자 비교를 다루는 6개 수업·12개 문제입니다. 검토 기록: `data/linux-modules-kconfig-review.json`.

`os3132`–`os3136`은 folio 참조 수·회수의 두 번째 기회·dirty 판정, IPv4 next-hop 조건·trie 되돌아가기를 다루는 5개 수업·10개 문제입니다. 검토 기록: `data/linux-reclaim-routing-review.json`.

`os3137`–`os3139`는 ext4 비트맵의 빈 비트 수, inode·block 체크섬 검사와 저장을 다루는 3개 수업·6개 문제입니다. `fs/ext4/bitmap.c` 전체 99줄과 다섯 함수의 의미 검토 근거를 기록했습니다. 검토 기록: `data/linux-ext4-bitmap-review.json`.

`os3140`–`os3146`은 ext4 디렉터리 해시의 문자열 부호·패딩·TEA·half-MD4·버전·casefold와 x86 분산 CPUID 탐지를 다루는 7개 수업·14개 문제입니다. `fs/ext4/hash.c` 전체 323줄의 검토 근거를 기록했습니다. 검토 기록: `data/linux-hash-cpuid-review.json`.

`os3147`–`os3152`는 자격 증명 준비·commit·override/revert·namespace 권한 관계·RCU 해제·다른 task 참조 획득의 6개 수업·12개 문제입니다. 검토 기록: `data/linux-credential-lifecycle-review.json`.

`os3153`–`os3159`는 exec·fork·커널 작업용 자격 생성, 파일 접근 자격 비교, 사용량 계정 교체, LSM 설정, 빈 객체와 초기 자격의 7개 수업·14개 문제입니다. `kernel/cred.c` 전체 734줄을 기존 수명 수업과 함께 대조했습니다. 검토 기록: `data/linux-credential-creation-review.json`.

`os3160`–`os3166`은 PREFLUSH/FUA 정책, 단계 비트, 두 목록의 묶음 발행, 참조 기반 완료, DATA 완료 보류, 순수 flush, 큐 수명의 7개 수업·14개 문제입니다. `block/blk-flush.c` 전체 538줄의 검토 근거를 기록했습니다. 검토 기록: `data/linux-flush-sequence-review.json`.

`os3167`–`os3176`은 notifier의 우선순위·중단·복구·atomic/blocking/raw/SRCU·die 이벤트와 클래스 반복·검색의 10개 수업·20개 문제입니다. `kernel/notifier.c` 전체 610줄을 대조했습니다. 검토 기록: `data/linux-notifier-class-review.json`.

`os3177`–`os3184`는 클래스 sysfs·등록·생성/해제·interface·호환 링크·등록 조회와 devm action 등록/제거/실행의 8개 수업·16개 문제입니다. `drivers/base/class.c` 전체 672줄을 기존 순회 수업과 함께 대조했습니다. 검토 기록: `data/linux-class-devm-review.json`.

`os3185`–`os3192`는 devres 할당·검색·그룹 경계·역순 반환과 관리 메모리 재할당의 8개 수업·16개 문제입니다. 관리 기록과 실제 자원의 수명, 잠금 안팎의 작업, 실패 복구를 설명합니다. 검토 기록: `data/linux-devres-groups-memory-review.json`.

`os3193`–`os3199`는 관리 문자열·서식 출력·페이지·CPU별 메모리와 IPv4/IPv6 주소 파싱·범위 선택의 7개 수업·14개 문제입니다. `drivers/base/devres.c` 전체 1,236줄의 구현을 14개 심화 수업에 연결해 검토했고 주소 표기와 바이트 순서 예제도 확인했습니다. 검토 기록: `data/linux-devm-inet-review.json`.

`os3200`–`os3204`는 체크섬의 증분 갱신·IPv6 차이 배열·미리 계산한 차이·ANY 주소·공유 네트워크 경고 제한의 5개 수업·10개 문제입니다. 분기별 수정 대상과 직접 경고/억제 요약 출력을 구별합니다. 검토 기록: `data/linux-inet-checksum-review.json`.

`os3205`–`os3210`는 주소 문자 분류·nofault 복사/문자열·x86 주소 허용의 6개 수업·12개 문제입니다. 부분 출력과 반환 길이, 설정별 검사 순서를 원문과 대조했습니다. 검토 기록: `data/linux-nofault-classifier-review.json`.

`os3211`–`os3219`는 스왑 슬롯 캐시·주소 공간 접근/복제/분리·vfork 완료 대기의 9개 수업·18개 문제입니다. 문턱과 잠금,참조 수명,실패 복구를 원문과 대조했습니다. 검토 기록: `data/linux-swap-fork-mm-review.json`.

`os3220`–`os3225`는 mm 초기화·두 참조 수·마지막 정리와 파일/시그널 공유의 6개 수업·12개 문제입니다. 검토 기록: `data/linux-mm-lifetime-sharing-review.json`.

`os3226`–`os3232`는 실행 파일 참조·seccomp 계승과 파일시스템 동기화의 7개 수업·14개 문제입니다. 검토 기록: `data/linux-exe-seccomp-sync-review.json`.

`os3233`–`os3240`는 NAPI 예약·완료·예산·비활성화와 CPU 분산·backlog·flow limit의 8개 수업·16개 문제입니다. 검토 기록: `data/linux-napi-rps-review.json`.

`os3241`–`os3248`은 x86 예외 테이블·레지스터 복구·Zeropad·MSR·FPU·초기 부팅·FRED·세그먼트 복구의 8개 수업·16개 문제입니다. 원문 전체 대조와 검수 기록: `data/linux-x86-fixups-review.json`.

`os3249`–`os3254`는 장치 깨우기 IRQ의 소유권·전용 스레드·초기 활성화·reverse 순서·시스템 깨우기 설정의 6개 수업·12개 문제입니다. 상태 비트와 실패 복구 예제를 포함하며 검토 기록은 `data/linux-wakeirq-review.json`입니다.

`os3255`–`os3265`는 discard·0 채우기·secure erase와 UTS namespace의 11개 수업·22개 문제입니다. 바이트·섹터 정렬,부분 완료·중단·fallback,이름 격리·참조·권한·생성 회계를 풀어 설명합니다. 고정 원문의 실패 정리 경로까지 대조했으며 검토 기록은 `data/linux-block-uts-review.json`입니다.

`os3266`–`os3280`은 IPC namespace와 타이머 장치의 15개 수업·30개 문제입니다. 지연 파괴·희소 번호 해제·생성 회계,시간 변환·재시도·CPU별 교체·주파수 변경·sysfs 실패 경로를 다룹니다. 두 원문 파일 전체 검토 기록: `data/linux-ipc-clockevent-review.json`, `data/linux-clockevent-lifecycle-review.json`.

`os3281`–`os3294`는 PID namespace·오디오 PCM DMA 버퍼의 14개 수업·28개 문제입니다. 계층별 번호·참조·종료 대기·복원 커서,버퍼 회계·축소 재시도·proc 교체·runtime 재사용·소유권 해제를 풀었습니다. 원문 전체 검토와 검수 기록: `data/linux-pid-pcm-review.json`.

`os3295`–`os3310`은 장치 cgroup 권한·eventfd의 16개 수업·32개 문제입니다. 예외 목록 의미·범위 매칭·부모 검증·전파 실패,FD와 context 수명·poll 순서·카운터 상한·복사 실패 후 상태를 다룹니다. 원문 전체 검토와 검수 기록: `data/linux-device-eventfd-review.json`.

`os3311`–`os3324`는 signalfd·timerfd의 14개 수업·28개 문제입니다. 신호 선택 마스크·레코드 변환·부분 읽기,타이머 주기 누적·시계 변경 취소·재설정 경쟁·조회 부수 효과를 설명합니다. 검수 기록: `data/linux-signal-timerfd-review.json`.

`os3325`–`os3334`는 madvise 주소 검사·잠금·VMA 순회·부분 적용·원격 조언과 WILLNEED·HugeTLB 범위·POPULATE·REMOVE의 10개 수업·20개 문제입니다. 검수 기록: `data/linux-madvise-dispatch-review.json`.

`os3335`–`os3344`는 COLD·PAGEOUT·FREE 회수 경로,큰 folio 분할·TLB·swap 회계·swap-in·익명 이름·오류 주입·봉인 검사의 10개 수업·20개 문제입니다. 앞 묶음과 합쳐 `mm/madvise.c` 1,548줄의 검토 근거를 기록했습니다. 검수 기록: `data/linux-madvise-reclaim-review.json`.

`os3345`–`os3361`은 IPv4 ICMP의 17개 수업·34개 문제입니다. 전송량 제한·재진입·checksum 조립·오류 재귀 방지·수신 검증·원본 protocol 오류 전달·echo/probe·확장 객체·route/XFRM·NAT·초기화를 설명합니다. `net/ipv4/icmp.c` 1,529줄의 검토 근거와 검수 기록: `data/linux-icmp-review.json`.

`os3362`–`os3371`은 KVM IRQFD·IOEVENTFD의 10개 수업·20개 문제입니다. 알림 방향·route snapshot·resampler ACK·등록 경쟁·종료 순서·I/O 매칭·충돌·fast bus 등록과 실패 정리를 설명합니다. `virt/kvm/eventfd.c` 1,013줄의 검토 근거와 검수 기록: `data/linux-kvm-eventfd-review.json`.

`os3372`–`os3382`는 CPU deadline 최대 힙과 autogroup의 11개 수업·22개 문제입니다. 역색인·heapify·후보 재검증·그룹 참조·스레드 이동·nice 가중치와 실패 상태를 설명합니다. `cpudeadline.c` 295줄과 `autogroup.c` 290줄의 검토 근거: `data/linux-scheduler-groups-review.json`.

`os3383`–`os3390`는 PM QoS의 8개 수업·16개 문제입니다. 제약 집계·알림 순서·공유 flags 삭제·요청 수명·지연 파일의 바이너리/문자열 분기·주파수 상하한을 설명합니다. `kernel/power/qos.c` 683줄의 검토 근거: `data/linux-pm-qos-review.json`.

`os3391`–`os3399`는 regcache 공통 구현의 9개 수업·18개 문제입니다. 기본값 소유권·HW 읽기 대안·캐시 모드·reset 정보·전체/구간 동기화·오류 반환·값 표현·raw 묶음을 설명합니다. `regcache.c` 849줄의 검토 근거: `data/linux-regcache-review.json`.

`os3400`–`os3406`는 Flat·Maple 레지스터 캐시의 7개 수업·14개 문제입니다. 희소 배열의 공간 낭비·존재 여부·구간 병합·분할 삭제·동기화와 실패 경로를 설명합니다. 두 파일 전체 대조 기록: `data/linux-regcache-backends-review.json`.

`os3407`–`os3413`는 Rbtree 레지스터 캐시의 7개 수업·14개 문제입니다. 구간 탐색·존재 비트·거리 기반 확장·초기 할당·동기화·무효화·통계의 의미를 설명합니다. 원문 558줄 검토 기록: `data/linux-regcache-rbtree-review.json`.

`os3414`–`os3417`는 Lockdown의 4개 수업·8개 문제입니다. 사유별 제한 판정·단방향 모드 변경·파일 읽기 위치·입력 개행과 NUL 처리를 설명합니다. 원문 173줄 검토 기록: `data/linux-lockdown-review.json`.

`os3418`–`os3434`는 파일 객체 수명과 계층별 페이지 회계의 17개 수업·34개 문제입니다. 할당·참조·지연 해제·실패 복구·한도 변경·보호 예산 배분을 설명합니다. 두 파일 전체 검토 기록: `data/linux-file-page-counters-review.json`.

`os3435`–`os3446`는 task_work와 경로 문자열의 12개 수업·24개 문제입니다. 등록·취소·종료 경쟁, 뒤에서 채우는 버퍼, 이름 변경 재시도, 마운트 경계와 getcwd 반환값을 설명합니다. 두 파일 검토 기록: `data/linux-taskwork-path-review.json`.

`os3447`–`os3455`는 블록 I/O 태그의 9개 수업·18개 문제입니다. 예약 번호·공정성·대기 경쟁·요청 참조·순회·완료 대기·초기화·깊이 변경·고유 태그를 설명합니다. 원문 684줄 검토 기록: `data/linux-blk-mq-tag-review.json`.
