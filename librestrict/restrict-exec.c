/*
  restrict-exec.c -- override execve(2) to make sure the build system
  doesn't leak into cross builds.

*/

#include <sys/syscall.h>
#include <unistd.h>

#include "restrict.c"

/*
  Using execve restriction works beautifully, but this would mean that
  we'd need a full build root, eg, tools::busybox *and* a plain
  tools::gcc, tools::g++, etc.

*/
static int
sys_execve (char const *file_name, char *const argv[], char *const envp[])
{
  return syscall (SYS_execve, file_name, argv, envp);
}

int
__execve (char const *file_name, char *const argv[], char *const envp[])
{
  if (verbosity > 1)
    fprintf (stderr, "%s: %s\n", __PRETTY_FUNCTION__, file_name);
  if (!is_allowed (file_name, "execve"))
    abort ();
  return sys_execve (file_name, argv, envp);
}

int execve (char const *file_name, char *const argv[], char *const envp[])  __attribute__ ((alias ("__execve")));
