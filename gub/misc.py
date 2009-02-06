import fnmatch
import imp
import os
import re
import stat
import subprocess
import sys
import traceback
import urllib2
#
from gub.syntax import printf, function_get_class, function_set_class, next
from gub import octal

def join_lines (str):
    return str.replace ('\n', ' ')

modules = {}

def preserve_cwd (function):
   def decorator (*args, **kwargs):
      cwd = os.getcwd ()
      result = function (*args, **kwargs)
      os.chdir (cwd)
      return result
   return decorator

@preserve_cwd
def symlink_in_dir (src, dest):
    dir = os.path.dirname (src)
    base = os.path.basename (src)
    dest = os.path.basename (dest)
    os.chdir (dir)
    os.symlink (base, dest)

def load_module (file_name, name=None):
    if not name:
        name = os.path.split (os.path.basename (file_name))[0]
    key = name + '::' + file_name
    if key not in modules:
        file = open (file_name)
        desc = ('.py', 'U', 1)
        modules[key] = imp.load_module (name, file, file_name, desc)
    return modules[key]

def load_spec (spec_file_name):
    # FIXME: should use settings.specdir
    specdir = os.getcwd () + '/gub/specs'
    return load_module ('%(specdir)s/%(spec_file_name)s.py' % locals ())

def bind (function, arg1):
    def bound (*args, **kwargs):
        return function (arg1, *args, **kwargs)
    return bound

def bind_method (func, obj):
    return lambda *args: func (obj, *args)

def xread_pipe (cmd, ignore_errors=False):
    pipe = os.popen (cmd)
    val = pipe.read ()
    if pipe.close () and not ignore_errors:
        raise SystemFailed ('Pipe failed: %(cmd)s' % locals ())
    return val

def read_pipe (cmd, ignore_errors=False, env=os.environ, logger=sys.stderr):
    proc = subprocess.Popen (cmd, bufsize=0, shell=True, env=env,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             close_fds=True)
    
    line = proc.stdout.readline ()
    result = line
    while line:
        line = proc.stdout.readline ()
        result += line

    if proc.returncode == None:
        # process has not terminated yet, but it's not producing output;
        # this means it's failing, wait for that.
        proc.poll ()
    if proc.returncode:
        m = 'read_pipe failed: %(cmd)s\n' % locals ()
        logger.write (m)
        if not ignore_errors:
            raise SystemFailed (m)
    if sys.version.startswith ('2'):
        return result
    else:
        return result.decode (sys.stdout.encoding)

def read_file (file):
    return open (file).read ()

def grok_sh_variables_str (str):
    dict = {}
    for i in str.split ('\n'):
        m = re.search ('^([^ =]+) *=\s*(.*)$', i)
        if m:
            k, s  = m.groups ()
            dict[k] = s
    return dict

def grok_sh_variables (file):
    return grok_sh_variables_str (open (file).read ())

def version_to_string (t):
    return '%s-%s' % ('.'.join (map (string, t[:-1])), t[-1])

def split_version (s):
    m = re.match ('^(([0-9].*)-([0-9]+))$', s)
    if m:
        return m.group (2), m.group (3)
    return (s, '0')

def string_to_version (s):
    s = re.sub ('([^0-9][^0-9]*)', ' \\1 ', s)
    s = re.sub ('[ _.-][ _.-]*', ' ', s)
    s = s.strip ()
    def atoi (x):
        if re.match ('^[0-9]+$', x):
            return int (x)
        return x
    return tuple (map (atoi, (s.split (' '))))

def is_ball (s):
    # FIXME: do this properly, by identifying different flavours:
    # .deb, tar.gz, cygwin -[build].tar.bz2 etc and have simple
    # named rules for them.
    return re.match ('^(.*?)[-_]([0-9].*(-[0-9]+)?)([._][a-z]+[0-9]*)?(\.tar\.(bz2|gz)|\.gu[bp]|\.deb|\.tgz|\.zip)$', s)

def split_ball (s):
    p = s.rfind ('/')
    if p >= 0:
        s = s[p+1:]
    m = is_ball (s)
    if not m:
        return (s, (0, 0), '')
    return (m.group (1), string_to_version ('-'.join (split_version (m.group (2)))), m.group (6))

def name_from_url (url):
    url, params = dissect_url (url)
    name = os.path.basename (url)
    if is_ball (name):
        name, version_tuple, format = split_ball (name)
    return name

def list_append (lists):
    return reduce (lambda x,y: x+y, lists, [])

def uniq (lst):
    u = []
    done = {}
    for e in lst:
        if e not in done:
            done[e] = 1
            u.append (e)
    return u

def compression_flag (ball):
    if (ball.endswith ('gub')
        or ball.endswith ('gup')
        or ball.endswith ('gz')
        or ball.endswith ('tgz')):
        return ' -z'
    elif ball.endswith ('bz2'):
        return ' -j'
    return ''

def first_is_newer (f1, f2):
    return (not os.path.exists (f2)
        or os.stat (f1).st_mtime > os.stat (f2).st_mtime)

def delinkify (file_name):
    first = True
    for component in file_name.split ('/'):
        if first:
            file_name = ''
            first = False
        file_name += '/' + component
        while os.path.islink (file_name):
            file_name = os.readlink (file_name)
    return file_name

def path_find (path, name):
    if type (path) == type (''):
        path = path.split (':')
    for dir in path:
        file_name = os.path.join (dir, name)
        if os.path.isfile (file_name):
            return file_name
    return None

def _find (dir, test_root_dir_files):
    dir = re.sub ( "/*$", '/', dir)
    result = []
    for (root, dirs, files) in os.walk (dir):
        result += test_root_dir_files (root, dirs, files)
    return result

def find (dir, test):
    '''
    Return list of files and directories under DIR with TEST (FILE) == TRUE
    '''
    def test_root_dir_files (root, dirs, files):
        return ([os.path.join (root, d) for d in dirs if test (d)]
                + [os.path.join (root, f) for f in files if test (f)])
    return _find (dir, test_root_dir_files)

def find_only_files_or_dirs (dir, file_test, file_or_dir_test):
    if type (file_test) == type (''):
        file_test = re.compile (file_test)
    def match (f):
        return test.search (f)
    if type (file_test) != type (match):
        file_test = match
    def test (f):
        return file_test (f) and file_or_dir_test (f)
    return find (dir, test)
        
def find_files (dir, test='.*'):
    ''' Return list of files under DIR matching the regex FILE_TEST
    or for which FILE_TEST (f) == TRUE
    '''
    return find_only_files_or_dirs (dir, test, lambda x: not os.path.isdir (x))

def find_dirs (dir, test='.*'):
    ''' Return list of dirs under DIR matching the regex FILE_TEST
    or for which FILE_TEST (f) == TRUE
    '''
    return find_only_files_or_dirs (dir, test, lambda x: os.path.isdir (x))
        
def rewrite_url (url, mirror):
    '''Return new url on MIRROR, using file name from URL.

    Assume that files are stored in a directory of their own base name, eg

    lilypond/lilypond-1.2.3.tar.gz
    '''
    
    file = os.path.basename (url)
    base = split_ball (file)[0]
    return os.path.join (mirror, base, file)

# FIXME: read settings.rc, local, fallback should be a user-definable list
def download_url (original_url, dest_dir,
                  local=[],
                  cache=[os.environ.get ('GUB_DOWNLOAD_CACHE', '')],
                  fallback=['http://lilypond.org/download/gub-sources'],
                  progress=sys.stderr.write):

    assert type (local) == list
    assert type (fallback) == list

    candidate_urls = []
    for url in local + cache + [original_url] + fallback:
        if not url:
            continue
        if os.path.exists (url):
            url = 'file://' + url
        if url == original_url:
            candidate_urls.append (url)
        if not is_ball (os.path.basename (url)):
            candidate_urls.append (rewrite_url (original_url, url))

    result = 'no valid urls'
    for url in candidate_urls:
        result = _download_url (url, dest_dir, progress)
        if type (result) == type (0):
            return
    raise Exception ('Download failed', result)

def _download_url (url, dest_dir, progress=None):
    progress ('downloading %(url)s -> %(dest_dir)s\n' % locals ())
    if not os.path.isdir (dest_dir):
        raise Exception ('not a dir', dest_dir)

    try:
        url_stream = urllib2.urlopen (url)
    except:
        t, v, b = sys.exc_info ()
        if ((t == OSError and url.startswith ('file:'))
            or ((t == IOError or t == urllib2.HTTPError)
                and (url.startswith ('ftp:') or url.startswith ('http:')))):
            return v
        raise

    size = 0
    bufsize = 1024 * 50
    output = None
    tmpfile = dest_dir + '/.partial-download-' + str (os.getpid ())
    while True:
        contents = url_stream.read (bufsize)
        if not contents:
            break
        size += len (contents)
        if not output:
            output = open (tmpfile, 'wb')
        output.write (contents)
        if progress:
            progress ('.')
        sys.stderr.flush ()

    if progress:
        progress ('\n')

    file_name = os.path.basename (url)
    if size:
        os.rename (tmpfile, os.path.join (dest_dir, file_name))
        if progress:
            progress ('done (%(size)s)\n' % locals ())
    else:
        os.unlink (tmpfile)
        if progress:
            progress ('failed\n')

    return size

def forall (generator):
    v = True
    try:
        while v:
            v = v and next (generator)
    except StopIteration:
        pass
    return v

def exception_string (exception=Exception ('no message')):
    return traceback.format_exc (None)

class SystemFailed (Exception):
    pass

def file_mod_time (path):
    return os.stat (path)[stat.ST_MTIME]

def binary_strip_p (filter_out=[], extension_filter_out=[]):
    def predicate (file):
        return (os.path.basename (file) not in filter_out
                and (os.path.splitext (file)[1] not in extension_filter_out)
                and not get_interpreter (file))
    return predicate

# Move to Os_commands?
def map_command_dir (os_commands, dir, command, predicate):
    if not os.path.isdir (dir):
        raise Exception ('warning: no such dir: %(dir)s' % locals ())
    (root, dirs, files) = next (os.walk (dir))
    for file in files:
        if predicate (os.path.join (root, file)):
            os_commands.system ('%(command)s %(root)s/%(file)s' % locals (),
                                ignore_errors=True)

def map_dir (func, dir):
    if not os.path.isdir (dir):
        raise Exception ('warning: no such dir: %(dir)s' % locals ())
    (root, dirs, files) = next (os.walk (dir))
    for file in files:
        func (root, file)

def ball_basename (ball):
    s = ball
    s = re.sub ('.tgz', '', s)
    s = re.sub ('-src\.tar.*', '', s)
    s = re.sub ('\.tar.*', '', s)
    s = re.sub ('_%\(package_arch\)s.*', '', s)
    s = re.sub ('_%\(version\)s', '-%(version)s', s)
    return s

def get_interpreter (file):
    s = open (file).readline (200)
    if s.startswith ('#!'):
        return s
    return None

def read_tail (file, size=10240, lines=100, marker=None):
    '''Efficiently read tail of a file, return list of full lines.

    Typical used for reading tail of a log file.  Read a maximum of
    SIZE, return a maximum line count of LINES, truncate everything
    before MARKER.
    '''
    f = open (file)
    f.seek (0, 2)
    length = f.tell ()
    if sys.version.startswith ('2'):
        #PYTHON3 BUG?
        f.seek (- min (length, size), 1)
    else:
        f.seek (max (length - size, 0), 0)
    s = f.read ()
    if marker:
        p = s.find (marker)
        if p >= 0:
            s = s[p:]
    return s.split ('\n')[-lines:]

class MethodOverrider:
    '''Override a object method with a function defined outside the
class hierarchy.
    
    Usage:

    def new_func (old_func, arg1, arg2, .. ):
        ..do stuff..
        pass
    
    old = obj.func
    p.func = MethodOverrider (old,
                              new_func,
                              (arg1, arg2, .. ))
    '''
    def __init__ (self, old_func, new_func, extra_args=tuple ()):
        self.new_func = new_func
        self.old_func = old_func
        self.args = extra_args
        self.dict = dict ()
        function_set_class (self, function_get_class (old_func))
    def __call__ (self):
        all_args = (self.old_func (),) + self.args  
        return self.new_func (*all_args)

def list_insert (lst, idx, a):
    if type (a) == type (list ()):
        lst = lst[:idx] + a + lst[idx:]
    else:
        lst.insert (idx, a)
    return lst

def list_insert_before (lst, target, a):
    return list_insert (lst, lst.index (target), a)

def most_significant_in_dict (d, name, sep):
    '''Return most significant variable from DICT

    NAME is less significant when it contains less bits sepated by SEP.'''
    
    v = None
    while name:
        if name in d:
            v = d[name]
            break
        name = name[:max (name.rfind (sep), 0)]
    return v

def dissect_url (url):
    """Strip and parse query part of a URL.

    Returns (stripped url, query-dict).  The values of the query-dict
    are lists of strings."""
    
    s = url.replace ('?', '&')
    lst = s.split ('&')
    def dict (tuple_lst):
        d = {}
        for k, v in tuple_lst:
            d[k] = d.get (k, []) + [v]
        return d
    
    return lst[0], dict ([x.split ('=') for x in lst[1:]])

def get_from_parents (cls, key):
    base = cls.__name__
    p = base.find ('__')
    if p >= 0:
        base = base[:p]
    for i in cls.__bases__:
        if not base in i.__name__:
            # multiple inheritance, a base class like AutoBuild
            # can come earlier that Python without __tools,
            # so continue rather than break
            continue
        if i.__dict__.get (key):
            return i.__dict__.get (key)
    return None


def file_sub (re_pairs, name, must_succeed=False, use_re=True, to_name=None):
    s = open (name).read ()
    t = s
    for frm, to in re_pairs:
        new_text = ''
        if use_re:
            new_text = re.sub (re.compile (frm, re.MULTILINE), to, t)
        else:
            new_text = t.replace (frm, to)

        if (t == new_text and must_succeed):
            raise Exception ('nothing changed!')
        else:
            if must_succeed and type (must_succeed) == type (0):
                must_succeed -= 1
        t = new_text

    if s != t or (to_name and name != to_name):
        stat_info = os.stat (name)
        mode = stat.S_IMODE (stat_info[stat.ST_MODE])

        if not to_name:
            try:
                os.unlink (name + '~')
            except OSError:
                pass
            os.rename (name, name + '~')
            to_name = name
        h = open (to_name, 'w')
        h.write (t)
        h.close ()
        os.chmod (to_name, mode)

def dump_file (content, name, mode='w', permissions=None):
    assert type (mode) == str
    if 'b' in mode:
        assert type (content) == bytes
    else:
        assert type (content) == str

    dir = os.path.split (name)[0]
    if not os.path.exists (dir):
        os.makedirs (dir)

    f = open (name, mode)
    f.write (content)
    f.close ()

    if permissions:
        os.chmod (name, permissions)

def locate_files (directory, pattern,
                  include_dirs=True, include_files=True):
    if not directory or not pattern:
        directory = os.path.dirname (directory + pattern)
        pattern = os.path.basename (directory + pattern)
    directory = re.sub ( "/*$", '/', directory)
    results = list ()
    for (root, dirs, files) in os.walk (directory):
        relative_results = list ()
        if include_dirs:
            relative_results += dirs
        if include_files:
            relative_results += files
        results += [os.path.join (root, f)
                    for f in (fnmatch.filter (relative_results, pattern))]
    return results

def shadow (src, target):
    '''Symlink files from SRC in TARGET recursively'''
    target = os.path.abspath (target)
    src = os.path.abspath (src)
    os.makedirs (target)
    (root, dirs, files) = next (os.walk (src))
    for f in files:
        os.symlink (os.path.join (root, f), os.path.join (target, f))
    for d in dirs:
        shadow (os.path.join (root, d), os.path.join (target, d))

def with_platform (s, platform):
    if '::' in s:
        return s
    return platform + '::' + s

def platform_adder (platform):
    def f (name):
        return with_platform (name, platform)
    return f

def split_platform (u, platform=None):
    if '::' in u:
        return u.split ('::')
    return platform, u

def append_path (elt):
    if elt:
        return ':' + elt
    return ''

def intersect (a, b):
    return [e for e in a + b if e in a and e in b]

def list_in (sub, lst):
    missing = [e for e in sub if e not in lst]
    return not missing

class Url:
    def __init__ (self, url):
        self.url, self.params = dissect_url (url)
        m = re.match ('((([^+]+)[+])?([^:]+))://((([^/:]+):)?(([^/]+)@))?([^:/]*)(:([0-9]+))?:?(.+)?', self.url)
        self.full_protocol = m.group (1)
        self.protocol = m.group (3)
        self.helper_protocol = m.group (4)
        self.user = m.group (7)
        self.password = m.group (9)
        self.port = m.group (11)
        self.host = m.group (10)
        if not self.host:
            self.host = 'localhost'
        self.dir = m.group (13)
    def __repr__ (self):
        return '<Url:' + self.__dict__.__repr__ () + '>'

def dump_python_config (self):
    dir = self.expand ('%(install_prefix)s%(cross_dir)s/bin')
    self.system ('mkdir -p %(dir)s' % locals ())
    python_config = '%(dir)s/python-config' % locals ()
    self.file_sub ([
         ('@PREFIX@', self.expand ('%(system_prefix)s')),
         # FIXME: better use %(tools_prefix)s/bin/python?
         # using GUB's python may mean using python3 to run
         # python-config, while we are building python2.4.
         ## ('@PYTHON_FOR_BUILD@', sys.executable),
         ('@PYTHON_FOR_BUILD@', self.expand ('%(tools_prefix)s/bin/python')),
         ('@PYTHON_VERSION@', self.expand ('%(version)s')),
         ('@EXTRA_LDFLAGS@', ''),],
         '%(sourcefiledir)s/python-config.py.in',
         to_name=python_config)
    self.chmod (python_config, octal.o755)

def test ():
    printf (forall (x for x in [1, 1]))
    printf (dissect_url ('git://anongit.freedesktop.org/git/fontconfig?revision=1234'))
    printf (dissect_url ('http://lilypond.org/foo-123.tar.gz&patch=a&patch=b'))
    printf (rewrite_url ('ftp://foo.com/pub/foo/foo-123.tar.gz', 'http://lilypond.org/downloads'))

if __name__ =='__main__':
    test ()
