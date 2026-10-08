# 첫 실습: 파일 읽기와 시스템 호출

## 목표

사용자 프로그램의 read()가 커널에서 어떤 입력을 받고, 어떤 파일 연산으로 연결되는지 설명하기.

1. 터미널에서 `./tools/lab.sh read`를 실행합니다.
2. strace에서 `/etc/hostname`을 여는 openat, 파일 내용을 읽는 read, 출력하는 write, 자원을 닫는 close를 찾습니다.
3. 동적 로더도 openat/read를 호출합니다. 실습 파일을 연 후의 파일 디스크립터로 구분하세요.
4. 학습 화면에서 `fs/read_write.c`를 엽니다.
5. `SYSCALL_DEFINE3(read`, `ksys_read`, `vfs_read`를 검색해 연결합니다.
6. `include/linux/fs.h`에서 `struct file`, `struct file_operations`를 찾습니다.
7. `read`와 `read_iter` 중 어떤 경로로 내려갈 수 있는지 살펴봅니다. 실제 파일 종류에 따라 호출 경로가 달라집니다.
8. 실습 셸에서 존재하지 않는 파일을 인자로 전달해 오류를 확인합니다.

```bash
./tools/lab.sh shell
cc -Wall -Wextra -g /labs/read_example.c -o /tmp/read-example
strace -e trace=openat,read,write,close /tmp/read-example /does-not-exist
```

## 메모에 남길 질문

- 사용자 공간의 포인터를 커널이 바로 신뢰할 수 없는 이유는?
- 파일 디스크립터와 struct file은 어떻게 연결되는가?
- read의 반환값 0, 양수, 음수는 각각 무엇을 의미하는가?
- 오류가 나면 어떤 경로로 자원을 정리하는가?

사용자 공간의 read()는 오류 시 -1과 errno를 제공하며, 커널 내부에서는 음수 오류 코드를 사용합니다.
