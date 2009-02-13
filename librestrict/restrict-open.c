/*
  restrict-open.c -- override open(2), to make sure the build system
  doesn't leak into cross builds.

*/

#include <stdarg.h>
#include <sys/syscall.h>

#include "restrict.c"

static int
sys_open (char const *file_name, int flags, int mode)
{
  return syscall (SYS_open, file_name, flags, mode);
}

int
__open (char const *file_name, int flags, ...)
{
  va_list p;
  va_start (p, flags);

  if (verbosity > 1)
    fprintf (stderr, "%s: %s\n", __PRETTY_FUNCTION__, file_name);
  if (!is_allowed (file_name, "open"))
    abort ();

  return sys_open (file_name, flags, va_arg (p, int));
}

int open (char const *file_name, int flags, ...) __attribute__ ((alias ("__open")));
