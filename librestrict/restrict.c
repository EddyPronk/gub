/*
  restrict.c -- override open(2), so we can be sure the build system
  doesn't leak into cross builds.
 */


#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <regex.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/syscall.h>
#include <unistd.h>

static char *executable_name;

static struct allow_path {
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
add_allowed (char const *p)
{
  if (allowed_count >= allowed_len)
    {
      int newlen = (2*allowed_len+1);
      allowed = realloc (allowed, sizeof (struct allow_path)*newlen);
      allowed_len = newlen;
    }

  allowed[allowed_count].prefix = strdup (p);
  allowed[allowed_count].prefix_len = strlen (p);
  allowed_count ++;
}

/*
  prepend cwd if necessary.  Leaks memory.
 */
static
char const *
expand_path (char const *p)
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
is_allowed (char const *fn, char const *call)
{
  int i;
  char const *fullpath;

  if (allowed_count == 0)
    return 1;

  fullpath = expand_path (fn);
  for (i = 0; i < allowed_count; i++)
    if (0 == strncmp (fullpath, allowed[i].prefix, allowed[i].prefix_len))
      return 1;

  fprintf (stderr, "%s: tried to %s() file %s\nallowed:\n",
	   executable_name, call, fullpath);

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
  // can't add bin/ due to libexec.
  char *cross_suffix = "/root/usr/cross/";
  char const *last_found = strrstr (exe_name, cross_suffix);
  int prefix_len;
  char *allowed_prefix;

  if (last_found == NULL)
    return NULL;

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

      add_allowed (restrict);
      if (allow)
	add_allowed (allow);
      add_allowed ("/tmp");
      add_allowed ("/dev/null");
    }
}

static int
real_open (const char *fn, int flags, int mode)
{
  return syscall (SYS_open, fn, flags, mode);
}


int
__open (const char *fn, int flags, ...)
{
  int rv;
  va_list p;
  va_start (p,flags);

  if (!is_allowed (fn, "open"))
    {
      abort ();
      return -1;
    }

  rv = real_open (fn, flags, va_arg (p, int));

  return rv;
}

int open (const char *fn, int flags, ...) __attribute__ ((alias ("__open")));

#ifdef TEST_SELF
int
main ()
{
  char *exe = "/home/hanwen/vc/gub/target/mingw/usr/cross/bin/foo";
  printf ("%s\n", get_executable_name());

  char const *h = "aabbaabba";
  char const *n = "bb";

  printf ("strrstr %s %s: %s\n", h,n, strrstr (h,n));
  printf ("allowed for %s : %s\n", exe, get_allowed_prefix (exe));
}
#endif
