/*
  restrict-stat.c -- stat(2), to make sure the build system doesn't
  leak into cross builds.

*/

#include <sys/stat.h>
#include <sys/syscall.h>

#include "restrict.c"

static int sys_stat (char const *file_name, struct stat *buf)
{
  return syscall (SYS_stat, file_name, buf);
}

static int sys_lstat (char const *file_name, struct stat *buf)
{
  return syscall (SYS_lstat, file_name, buf);
}

int
__lstat (char const *file_name, struct stat *buf)
{
  if (verbosity > 1)
    fprintf (stderr, "%s: %s\n", __PRETTY_FUNCTION__, file_name);
  if (!is_allowed (file_name, "stat"))
    abort ();

  return sys_lstat (file_name, buf);
}

int lstat (char const *file_name, struct stat *buf)  __attribute__ ((alias ("__lstat")));

static int sys_oldstat (char const *file_name, struct stat *buf)
{
  return syscall (SYS_stat, file_name, buf);
}

int
__oldstat (char const *file_name, struct stat *buf)
{
  if (verbosity > 1)
    fprintf (stderr, "%s: %s\n", __PRETTY_FUNCTION__, file_name);
  if (!is_allowed (file_name, "stat"))
    abort ();

  return sys_oldstat (file_name, buf);
}

int oldstat (char const *file_name, struct stat *buf)  __attribute__ ((alias ("__oldstat")));

int
__stat (char const *file_name, struct stat *buf)
{
  if (verbosity > 1)
    fprintf (stderr, "%s: %s\n", __PRETTY_FUNCTION__, file_name);
  if (!is_allowed (file_name, "stat"))
    abort ();

  return sys_stat (file_name, buf);
}

int stat (char const *file_name, struct stat *buf)  __attribute__ ((alias ("__stat")));

#ifdef SYS_ustat
static int sys_ustat (char const *file_name, struct stat *buf)
{
  return syscall (SYS_ustat, file_name, buf);
}

int
__ustat (char const *file_name, struct stat *buf)
{
  if (verbosity > 1)
    fprintf (stderr, "%s: %s\n", __PRETTY_FUNCTION__, file_name);
  if (!is_allowed (file_name, "stat"))
    abort ();

  return sys_ustat (file_name, buf);
}

int ustat (char const *file_name, struct stat *buf)  __attribute__ ((alias ("__ustat")));
#endif /* SYS_ustat */

int
__xstat (int ver, char const *file_name, struct stat *buf)
{
  if (verbosity > 1)
    fprintf (stderr, "%s: %s\n", __PRETTY_FUNCTION__, file_name);
  if (!is_allowed (file_name, "xstat"))
    abort ();

  return sys_stat (file_name, buf);
}

int xstat (int ver, char const *file_name, struct stat *buf)  __attribute__ ((alias ("__xstat")));
