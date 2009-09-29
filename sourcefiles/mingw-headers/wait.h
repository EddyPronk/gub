#ifndef SYS_WAIT_H
#define SYS_WAIT_H

#include <errno.h>
#if 0
//badly breaks with flex.
#include <winsock2.h>
#else

#define htons(a) ((((unsigned short)(a) & 0xff00) >> 8) | (((unsigned short)(a) & 0x00ff) << 8))
#define htonl(a) ((((unsigned)(a) & 0xff000000) >> 24) | (((unsigned)(a) & 0x00ff0000) >> 8) | (((unsigned)(a) & 0x0000ff00) << 8) | (((unsigned)(a) & 0x000000ff) << 24))
#define ntohs htons
#define ntohl htohl
#endif

#define WIFEXITED(x) 1
#define WIFSIGNALED(x) 0
#define WEXITSTATUS(x) ((x) & 0xff)
#define WTERMSIG(x) SIGTERM

static inline int waitpid (pid_t pid, int *status, unsigned options)
{
  if (options == 0)
    return _cwait (status, pid, 0);
  errno = EINVAL;
  return -1;
}

#define wait(status) waitpid (-1, status, 0)

static inline int fork (void)
{
  errno = ENOSYS;
  return -1;
}

static int pipe(int filedes[2])
{
  errno = ENOSYS;
  return -1;
}
  
#endif /* SYS_WAIT_H */
