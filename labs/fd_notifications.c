/* Linux/WSL 실습: 세 종류의 알림을 같은 poll/read 인터페이스로 읽습니다.
 * 커널 원본을 그대로 복사한 파일이 아니라 사용법을 보여주는 사용자 C 예제입니다.
 * Eventfd: 누적 숫자, Signalfd: signal record, Timerfd: timer 만료 횟수.
 */
#define _GNU_SOURCE
#include <errno.h>
#include <inttypes.h>
#include <poll.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/eventfd.h>
#include <sys/signalfd.h>
#include <sys/timerfd.h>
#include <unistd.h>

static void fail(const char *operation)
{
    perror(operation);
    exit(EXIT_FAILURE); /* 프로세스 종료 시 남아 있는 fd도 OS가 정리합니다. */
}

/* &value는 value의 주소, sizeof(value)는 저장된 byte 수입니다. */
static void write_number(int fd, uint64_t value)
{
    ssize_t n;
    do { n = write(fd, &value, sizeof(value)); } while (n < 0 && errno == EINTR);
    if (n != (ssize_t)sizeof(value)) {
        if (n >= 0) errno = EIO;
        fail("write u64");
    }
}

static uint64_t read_number(int fd)
{
    uint64_t value;
    ssize_t n;
    do { n = read(fd, &value, sizeof(value)); } while (n < 0 && errno == EINTR);
    if (n != (ssize_t)sizeof(value)) {
        if (n >= 0) errno = EIO;
        fail("read u64");
    }
    return value;
}

static void wait_readable(int fd)
{
    /* .fd 등은 구조체 field 이름입니다. poll은 데이터를 소비하지 않습니다. */
    struct pollfd entry = { .fd = fd, .events = POLLIN };
    int n;
    do { n = poll(&entry, 1, 3000); } while (n < 0 && errno == EINTR);
    if (n < 0) fail("poll");
    if (!n || !(entry.revents & POLLIN)) {
        fprintf(stderr, "readiness timeout/error: 0x%x\n", entry.revents);
        exit(EXIT_FAILURE);
    }
}

static void require_number(const char *name, uint64_t actual, uint64_t expected)
{
    printf("%s: %" PRIu64 "\n", name, actual);
    if (actual != expected) {
        fprintf(stderr, "expected %" PRIu64 "\n", expected);
        exit(EXIT_FAILURE);
    }
}

int main(void)
{
    int event = eventfd(0, EFD_CLOEXEC | EFD_NONBLOCK);
    if (event < 0) fail("eventfd");
    write_number(event, 2);
    write_number(event, 3);
    wait_readable(event);
    require_number("eventfd accumulated", read_number(event), 5);

    uint64_t ignored;
    ssize_t empty;
    do { empty = read(event, &ignored, sizeof(ignored)); }
    while (empty < 0 && errno == EINTR);
    if (empty != -1 || errno != EAGAIN) {
        fprintf(stderr, "empty nonblocking eventfd must return EAGAIN\n");
        return EXIT_FAILURE;
    }
    puts("eventfd empty: EAGAIN");
    close(event);

    int semaphore = eventfd(2, EFD_SEMAPHORE | EFD_CLOEXEC | EFD_NONBLOCK);
    if (semaphore < 0) fail("eventfd semaphore");
    require_number("eventfd semaphore first", read_number(semaphore), 1);
    require_number("eventfd semaphore second", read_number(semaphore), 1);
    close(semaphore);

    /* 먼저 signal을 block해야 일반 handler/default 동작 대신 fd로 소비합니다.
     * 이 예제는 thread 하나만 있습니다. 여러 thread에서는 각 mask를 고려합니다.
     */
    sigset_t mask, previous;
    sigemptyset(&mask);
    sigaddset(&mask, SIGUSR1);
    if (sigprocmask(SIG_BLOCK, &mask, &previous) < 0) fail("sigprocmask");
    int signals = signalfd(-1, &mask, SFD_CLOEXEC | SFD_NONBLOCK);
    if (signals < 0) fail("signalfd");
    if (kill(getpid(), SIGUSR1) < 0) fail("kill self");
    wait_readable(signals);
    struct signalfd_siginfo info;
    ssize_t n;
    do { n = read(signals, &info, sizeof(info)); } while (n < 0 && errno == EINTR);
    if (n != (ssize_t)sizeof(info)) {
        if (n >= 0) errno = EIO;
        fail("read signal record");
    }
    if (info.ssi_signo != SIGUSR1 || info.ssi_pid != (uint32_t)getpid()) {
        fprintf(stderr, "unexpected signal record\n");
        return EXIT_FAILURE;
    }
    printf("signalfd: SIGUSR1, record bytes=%zu\n", sizeof(info));
    close(signals);
    if (sigprocmask(SIG_SETMASK, &previous, NULL) < 0) fail("restore mask");

    int timer = timerfd_create(CLOCK_MONOTONIC, TFD_CLOEXEC | TFD_NONBLOCK);
    if (timer < 0) fail("timerfd_create");
    /* One-shot 10ms입니다. 정확한 userspace 실행 시각을 보장하지 않습니다. */
    struct itimerspec setting = { .it_value = { .tv_sec = 0, .tv_nsec = 10000000 } };
    if (timerfd_settime(timer, 0, &setting, NULL) < 0) fail("timerfd_settime");
    wait_readable(timer);
    require_number("timerfd one-shot expirations", read_number(timer), 1);
    close(timer);
    puts("All notification contracts observed.");
    return EXIT_SUCCESS;
}
