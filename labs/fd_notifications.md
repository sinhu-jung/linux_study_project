# fd 알림 실습

이 예제는 Linux 사용자 프로그램입니다. Windows에서는 WSL Linux에서 실행합니다.
학습실 화면은 Windows Python으로 실행할 수 있지만 Linux 전용 system call 실습은 Linux kernel이 필요합니다.
macOS에서는 학습실의 Docker Linux 환경을 이용할 수 있습니다.

Ubuntu/Debian에서 C 컴파일러가 준비되어 있다면 프로젝트 폴더에서:

```sh
cc -std=c11 -Wall -Wextra -Werror labs/fd_notifications.c -o /tmp/fd-notifications
/tmp/fd-notifications
```

`cc`가 없다면 Ubuntu/Debian의 `build-essential` 패키지를 설치합니다.
예제는 자기 프로세스에 SIGUSR1을 보내며 외부 프로세스를 제어하지 않습니다.

예상 출력:

```text
eventfd accumulated: 5
eventfd empty: EAGAIN
eventfd semaphore first: 1
eventfd semaphore second: 1
signalfd: SIGUSR1, record bytes=128
timerfd one-shot expirations: 1
All notification contracts observed.
```

## 먼저 예측하기

1. 일반 eventfd에 2와 3을 write한 뒤 두 번 read하면 각각 어떻게 될까요?
2. EFD_SEMAPHORE의 초기값을 3으로 바꾸면 성공하는 read 횟수와 각 값은?
3. signalfd record buffer를 64byte로 줄이면 왜 EINVAL일까요?
4. poll이 readable을 반환했을 때 counter나 signal이 이미 소비되었을까요?
5. timer의 10ms는 프로그램이 정확히 10ms 시점에 실행된다는 보장일까요?

<details><summary>답지 보기</summary>

1. 첫 read는 5를 읽고 counter를 0으로 만듭니다. 두 번째 NONBLOCK read는 EAGAIN입니다.
2. 세 번 성공하며 각각 1입니다. 초기 counter를 한 번에 반환하는 일반 mode와 다릅니다.
3. Signalfd의 최소 단위는 128byte record입니다. 완전 record를 담을 공간이 필요합니다.
4. Poll은 준비 상태 조회입니다. 실제 소비는 read가 합니다. 여러 소비자가 있으면 poll 이후 상태가 바뀔 수도 있습니다.
5. Timer 만료와 task의 scheduling은 다릅니다. 실행은 늦을 수 있으며 one-shot counter는 만료 1회입니다.

</details>

## 코드와 커널 연결

`eventfd_read`, `signalfd_read_iter`, `timerfd_read_iter`는 모두 file operation이지만 읽는 데이터와 소모 규칙이 다릅니다.
세 API를 단순한 같은 숫자 queue로 생각하지 마세요. `struct pollfd`의 `fd`는 감시 대상,
`events`는 원하는 준비 조건, `revents`는 kernel이 알려준 결과입니다.
`&value`는 주소, `sizeof(value)`는 byte 크기, `errno`는 실패 원인입니다.
`PRIu64`는 uint64_t를 올바른 형식으로 출력하기 위한 macro입니다.
