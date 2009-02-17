/*
  restrict-stat.c -- stat(2), to make sure the build system doesn't
  leak into cross builds.

*/

#include <stddef.h>
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

#ifdef __linux__

/*
  Lifted from glibc-2.3-20070416
*/

#include <errno.h>
#ifndef __set_errno
#define __set_errno(e) (errno = (e))
#endif

#include <kernel-features.h>
#ifdef __x86_64__
#define STAT_IS_KERNEL_STAT 1
#define XSTAT_IS_XSTAT64 1
#define kernel_stat stat
#define __xstat_conv(a, b, c) 0
#else /* !__x86_64__ */
#define stat64 kernel_stat /* FIXME: CONFIG? */
#include <xstatconv.c>
#endif /* !__x86_64__ */


static int sys_xstat (int ver, char const *file_name, struct stat *buf)
{
#ifdef STAT_IS_KERNEL_STAT
  //  if (ver == _STAT_VER_KERNEL)
  if (ver == _STAT_VER_LINUX)
    return syscall (SYS_stat, file_name, buf);

  errno = EINVAL;
  return -1;
#else /* !STAT_IS_KERNEL_STAT */
  (void) ver;
  struct kernel_stat kbuf;
  int result = syscall (SYS_stat, file_name, &kbuf);
  if (result == 0)
    result = __xstat_conv (ver, &kbuf, buf);

  return result;
#endif /* !STAT_IS_KERNEL_STAT */
}

int
__xstat (int ver, char const *file_name, struct stat *buf)
{
  if (verbosity > 1)
    fprintf (stderr, "%s: %s\n", __PRETTY_FUNCTION__, file_name);
  if (!is_allowed (file_name, "xstat"))
    abort ();

  return sys_xstat (ver, file_name, buf);
}

int xstat (int ver, char const *file_name, struct stat *buf)  __attribute__ ((alias ("__xstat")));

#endif /* __linux__ */
