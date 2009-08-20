/*
  restrict.c -- override open(2), stat(2), execve(2), etc.  to make
  sure the build system doesn't leak into cross builds.

*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#ifndef __RESTRICT_C__
#define __RESTRICT_C__

static char *executable_name;
static int verbosity = 0;

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
      if (p - path == len && !strncmp (path, name, len))
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
  char *ignore = getenv ("LIBRESTRICT_IGNORE");

  char const *last_found = strrstr (exe_name, cross_suffix);
  if (last_found == NULL)
    last_found = strrstr (exe_name, tools_suffix);
  if (last_found == NULL)
    return NULL;

  if (ignore && is_in_path (ignore, exe_name))
    {
      if (verbosity)
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
  char *verbosity_string = getenv ("LIBRESTRICT_VERBOSE");
  
  if (verbosity_string)
    {
      verbosity = atoi (verbosity_string);
      if (!verbosity)
	verbosity = 1;
    }
  executable_name = get_executable_name ();
  restrict = get_allowed_prefix (executable_name);
  if (restrict)
    {
      char *allow = getenv ("LIBRESTRICT_ALLOW");
      if (verbosity > 1)
	fprintf (stderr, "%s: allow: %s\n", __PRETTY_FUNCTION__, allow);

      add_allowed_file (restrict);
      if (allow)
        add_allowed_path (allow);
      add_allowed_file ("/tmp");
      add_allowed_file ("/dev/null");
      add_allowed_file ("/proc/self");
    }
}

#ifdef TEST_SELF
int
main ()
{
  int i;
  char const *h = "aabbaabba";
  char const *n = "bb";
  char *exe = "/home/hanwen/vc/gub/target/mingw/usr/cross/bin/foo";

  printf ("%s\n", get_executable_name ());
  printf ("strrstr %s %s: %s\n", h,n, strrstr (h, n));
  printf ("allowed for %s : %s\n", exe, get_allowed_prefix (exe));

  puts ("allowed:");
  for (i = 0; i < allowed_count; i++)
    fprintf (stderr, "  %s\n", allowed[i].prefix);
  return 0;
}
#endif

#endif /* __RESTRICT_C__ */
