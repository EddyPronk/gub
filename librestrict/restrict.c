/*
  restrict.c -- override open(2), stat(2), to make sure the build
  system doesn't leak into cross builds.

*/

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <unistd.h>

static char *executable_name;

static struct allow_file_name
{
  char *prefix;
  int prefix_len;
} *allowed;
static int allowed_len;
static int allowed_count;

#if defined (__FreeBSD__)
char const *SELF = "/proc/curproc/file";
#else
char const *SELF = "/proc/self/exe";
#endif

static void
add_allowed_file (char const *name)
{
  if (allowed_count >= allowed_len)
    {
      int newlen = (2*allowed_len+1);
      allowed = realloc (allowed, sizeof (struct allow_file_name)*newlen);
      allowed_len = newlen;
    }

  allowed[allowed_count].prefix = strdup (name);
  allowed[allowed_count].prefix_len = strlen (name);
  allowed_count ++;
}

static void
add_allowed_path (char const *path)
{
  char *p = strchr (path, ':');
  while (p)
    {
      char c = *p;
      *p = '\0';
      add_allowed_file (strdup (path));
      *p = c;
      path = p + 1;
      p = strchr (path, ':');
    }
  add_allowed_file (path);
}

static int
is_in_path (char const *path, char const *name)
{
  char *p = strchr (path, ':');
  int len = strlen (name);
  while (p)
    {
      if (p - path == len && !strncmp (p, name, len))
	return 1;
      path = p + 1;
      p = strchr (path, ':');
    }
  if (!strcmp (path, name))
    return 1;
  return 0;
}

/*
  prepend cwd if necessary.  Leaks memory.
 */
static
char const *
expand_file_name (char const *p)
{
  if (*p == '/')
    return p;
  else
    {
      char s[1024];
      getcwd (s, sizeof (s));
      strncat (s, "/", 1);

      // ugh.
      strcat (s, p);
      return strdup (s);
    }
}

static int
is_allowed (char const *file_name, char const *call)
{
  int i;
  char const *abs_file_name;

  if (allowed_count == 0)
    return 1;

  abs_file_name = expand_file_name (file_name);
  for (i = 0; i < allowed_count; i++)
    if (0 == strncmp (abs_file_name, allowed[i].prefix, allowed[i].prefix_len))
      return 1;

  fprintf (stderr, "%s: tried to %s () file %s\nallowed:\n",
           executable_name, call, abs_file_name);

  for (i = 0; i < allowed_count; i++)
    fprintf (stderr, "  %s\n", allowed[i].prefix);

  return 0;
}

static char *
get_executable_name (void)
{
  int const MAXLEN = 1024;
  char s[MAXLEN+1];
  ssize_t ss = readlink (SELF, s, MAXLEN);
  if (ss < 0)
    {
      fprintf (stderr, "restrict.c: failed reading: %s\n", SELF);
      abort ();
    }
  s[ss] = '\0';

  return strdup (s);
}

static char const *
strrstr (char const *haystack, char const *needle)
{
  char const *p = haystack;
  char const *last_match = NULL;

  while ((p = strstr (p, needle)) != NULL)
    {
      last_match = p;
      p ++;
    }

  return last_match;
}

static char *
get_allowed_prefix (char const *exe_name)
{
  int prefix_len;
  char *allowed_prefix;
  // can't add bin/ due to libexec.
  char *cross_suffix = "/root/usr/cross/";
  char *tools_suffix = "/tools/root/usr/";

  char const *last_found = strrstr (exe_name, cross_suffix);
  if (last_found == NULL)
    last_found = strrstr (exe_name, tools_suffix);
  if (last_found == NULL)
    return NULL;

  char *ignore = getenv ("LIBRESTRICT_IGNORE");
  if (ignore && is_in_path (ignore, exe_name))
    {
      if (getenv ("LIBRESTRICT_VERBOSE"))
	fprintf (stderr, "%s: lifting restrictions for %s\n", __PRETTY_FUNCTION__, exe_name);
      return NULL;
    }

  prefix_len = last_found - exe_name;
  allowed_prefix = malloc (sizeof (char) * (prefix_len + 1));

  strncpy (allowed_prefix, exe_name, prefix_len);
  allowed_prefix[prefix_len] = '\0';

  return allowed_prefix;
}

static void initialize (void) __attribute__ ((constructor));

static
void initialize (void)
{
  char *restrict;

  executable_name = get_executable_name ();
  restrict = get_allowed_prefix (executable_name);
  if (restrict)
    {
      char *allow = getenv ("LIBRESTRICT_ALLOW");

      add_allowed_file (restrict);
      if (allow)
        add_allowed_path (allow);
      add_allowed_file ("/tmp");
      add_allowed_file ("/dev/null");
    }
}

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

  if (getenv ("LIBRESTRICT_VERBOSE"))
    fprintf (stderr, "%s: %s\n", __PRETTY_FUNCTION__, file_name);
  if (!is_allowed (file_name, "open"))
    abort ();

  return sys_open (file_name, flags, va_arg (p, int));
}

int open (char const *file_name, int flags, ...) __attribute__ ((alias ("__open")));

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
  if (getenv ("LIBRESTRICT_VERBOSE"))
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
  if (getenv ("LIBRESTRICT_VERBOSE"))
    fprintf (stderr, "%s: %s\n", __PRETTY_FUNCTION__, file_name);
  if (!is_allowed (file_name, "stat"))
    abort ();

  return sys_oldstat (file_name, buf);
}

int oldstat (char const *file_name, struct stat *buf)  __attribute__ ((alias ("__oldstat")));

int
__stat (char const *file_name, struct stat *buf)
{
  if (getenv ("LIBRESTRICT_VERBOSE"))
    fprintf (stderr, "%s: %s\n", __PRETTY_FUNCTION__, file_name);
  if (!is_allowed (file_name, "stat"))
    abort ();

  return sys_stat (file_name, buf);
}

int stat (char const *file_name, struct stat *buf)  __attribute__ ((alias ("__stat")));

static int sys_ustat (char const *file_name, struct stat *buf)
{
  return syscall (SYS_ustat, file_name, buf);
}

int
__ustat (char const *file_name, struct stat *buf)
{
  if (getenv ("LIBRESTRICT_VERBOSE"))
    fprintf (stderr, "%s: %s\n", __PRETTY_FUNCTION__, file_name);
  if (!is_allowed (file_name, "stat"))
    abort ();

  return sys_ustat (file_name, buf);
}

int ustat (char const *file_name, struct stat *buf)  __attribute__ ((alias ("__ustat")));

int
__xstat (int ver, char const *file_name, struct stat *buf)
{
  if (getenv ("LIBRESTRICT_VERBOSE"))
    fprintf (stderr, "%s: %s\n", __PRETTY_FUNCTION__, file_name);
  if (!is_allowed (file_name, "xstat"))
    abort ();

  return sys_stat (file_name, buf);
}

int xstat (int ver, char const *file_name, struct stat *buf)  __attribute__ ((alias ("__xstat")));

#ifdef TEST_SELF
int
main ()
{
  char *exe = "/home/hanwen/vc/gub/target/mingw/usr/cross/bin/foo";
  printf ("%s\n", get_executable_name ());

  char const *h = "aabbaabba";
  char const *n = "bb";

  printf ("strrstr %s %s: %s\n", h,n, strrstr (h, n));
  printf ("allowed for %s : %s\n", exe, get_allowed_prefix (exe));
  return 0;
}
#endif
