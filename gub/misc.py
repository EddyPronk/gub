# misc utils
import os
import re
import string
import sys
import urllib2
import stat
import imp
import traceback
import fnmatch

def join_lines (str):
    return str.replace ('\n', ' ')

def load_module (file_name, name=None):
    if not name:
        name = os.path.split (os.path.basename (file_name))[0]
    file = open (file_name)
    desc = ('.py', 'U', 1)
    return imp.load_module (name, file, file_name, desc)

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

def read_pipe (cmd, ignore_errors=False, verbose=True):
    if verbose:
        sys.stderr.write ('Executing pipe %(cmd)s\n' % locals ())
    pipe = os.popen (cmd)
    val = pipe.read ()
    if pipe.close () and not ignore_errors:
        raise SystemFailed ('Pipe failed: %(cmd)s' % locals ())
    return val

def read_file (file):
    return open (file).read ()

def grok_sh_variables_str (str):
    dict = {}
    for i in str.split ('\n'):
        m = re.search ('^([^ =]+) *=\s*(.*)$', i)
        if m:
            k = m.group (1)
            s = m.group (2)
            dict[k] = s
    return dict


def grok_sh_variables (file):
    return grok_sh_variables_str (open (file).read ())

def itoa (x):
    if type (x) == int:
        return "%d" % x
    return x

def version_to_string (t):
    return '%s-%s' % (string.join (map (itoa, t[:-1]), '.'), t[-1])

def split_version (s):
    m = re.match ('^(([0-9].*)-([0-9]+))$', s)
    if m:
        return m.group (2), m.group (3)
    return s, '0'

def string_to_version (s):
    s = re.sub ('([^0-9][^0-9]*)', ' \\1 ', s)
    s = re.sub ('[ _.-][ _.-]*', ' ', s)
    s = s.strip ()
    def atoi (x):
        if re.match ('^[0-9]+$', x):
            return int (x)
        return x
    return tuple (map (atoi, (string.split (s, ' '))))

def is_ball (s):
    # FIXME: do this properly, by identifying different flavours:
    # .deb, tar.gz, cygwin -[build].tar.bz2 etc and have simple
    # named rules for them.
    return re.match ('^(.*?)[-_]([0-9].*(-[0-9]+)?)([._][a-z]+[0-9]*)?(\.tar\.(bz2|gz)|\.gu[bp]|\.deb|\.tgz)$', s)

def split_ball (s):
    p = s.rfind ('/')
    if p >= 0:
        s = s[p+1:]
    m = is_ball (s)
    if not m:
        return (s, (0, 0), '')
    return (m.group (1), string_to_version (string.join (split_version (m.group (2)), '-')), m.group (6))

def name_from_url (url):
    name = os.path.basename (url)
    if is_ball (name):
        name, version_tuple, format = split_ball (name)
    return name

def list_append (lists):
    return reduce (lambda x,y: x+y, lists, [])

def uniq (list):
    u = []
    done = {}
    for e in list:
        if done.has_key (e):
            continue

        done[e] = 1
        u.append (e)

    return u

def intersect (l1, l2):
    return [l for l in l1 if l in l2]

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

def find (dir, test):
    dir = re.sub ( "/*$", '/', dir)
    result = []
    for (root, dirs, files) in os.walk (dir):
        result += test (root, dirs, files)
    return result

def find_files (dir, pattern):
    '''
    Return list of files under DIR matching the regex pattern.
    '''
    if type ('') == type (pattern):
        pattern = re.compile (pattern)
    def test (root, dirs, files):
        #HMM?
        root = root.replace (dir, '')
        return [os.path.join (root, f) for f in files if pattern.search (f)]
    return find (dir, test)
        
def find_dirs (dir, pattern):
    '''
    Return list of dirs under DIR matching the regex pattern.
    '''
    if type ('') == type (pattern):
        pattern = re.compile (pattern)
    def test (root, dirs, files):
        return [os.path.join (root, d) for d in dirs if pattern.search (d)]
    return find (dir, test)

def rewrite_url (url, mirror):
    '''Return new url on MIRROR, using file name from URL.

Assume that files are stored in a directory of their own base name, eg

    lilypond/lilypond-1.2.3.tar.gz
'''
    file = os.path.basename (url)
    base = split_ball (file)[0]
    return os.path.join (mirror, base, file)

# FIXME: read settings.rc, local, fallback should be a user-definable list
def download_url (url, dest_dir,
                  local='file://%(HOME)s/vc/gub/downloads' % os.environ,
                  fallback=['http://lilypond.org/download/gub-sources'],
                  log=sys.stderr.write):
    for i in lst (local) + [url] + lst (fallback):
        if not is_ball (os.path.basename (i)):
            i = rewrite_url (url, i)
        e = _download_url (i, dest_dir, log)
        if not e:
            return
    raise e

def _download_url (url, dest_dir, log=sys.stderr.write):
    try:
        log ('downloading %(url)s -> %(dest_dir)s\n' % locals ())
        size = __download_url (url, dest_dir, log)
        log ('done (%(size)s)\n' % locals ())
    except Exception, e:
        log ('download failed: ' + exception_string (e) + '\n')
        return e
    return None

def __download_url (url, dest_dir, log=sys.stderr.write):
    if not os.path.isdir (dest_dir):
        raise Exception ("not a dir", dest_dir)
    bufsize = 1024 * 50
    # what's this, just basename?
    # filename = os.path.split (urllib.splithost (url)[1])[1]
    file_name = os.path.basename (url)
    size = 0
    dest = os.path.join (dest_dir, file_name)
    try:
        output = open (dest, 'w')
        url_stream = urllib2.urlopen (url)
        while True:
            contents = url_stream.read (bufsize)
            size += bufsize
            output.write (contents)
            log ('.')
            sys.stderr.flush ()
            if not contents:
                break
        log ('\n')
    except Exception, e:
        os.unlink (dest)
        raise e
    return size

def forall (generator):
    v = True
    try:
        while v:
            v = v and generator.next ()
    except StopIteration:
        pass
    return v

def exception_string (exception=Exception ('no message')):
    return traceback.format_exc (None)

class SystemFailed (Exception):
    pass


def system (cmd, ignore_errors=False):
    #URG, go through oslog
    print 'Executing command %s' % cmd
    stat = os.system (cmd)
    if stat and not ignore_errors:
        raise SystemFailed ('Command failed (' + `stat/256` + '): ' + cmd)

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
        raise ('warning: no such dir: %(dir)s' % locals ())
    (root, dirs, files) = os.walk (dir).next ()
    for file in files:
        if predicate (os.path.join (root, file)):
            os_commands.system ('%(command)s %(root)s/%(file)s' % locals (),
                                ignore_errors=True)

def map_dir (func, dir):
    if not os.path.isdir (dir):
        raise ('warning: no such dir: %(dir)s' % locals ())
    (root, dirs, files) = os.walk (dir).next ()
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
    '''
Efficiently read tail of a file, return list of full lines.

Typical used for reading tail of a log file.  Read a maximum of
SIZE, return a maximum line count of LINES, truncate everything
before MARKER.
'''
    f = open (file)
    f.seek (0, 2)
    length = f.tell ()
    f.seek (- min (length, size), 1)
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
    def __init__ (self, old_func, new_func, extra_args=()):
        self.new_func = new_func
        self.old_func = old_func
        self.args = extra_args
    def __call__ (self):
        all_args = (self.old_func (),) + self.args  
        return apply (self.new_func, all_args)

def list_find (lst, a):
    if a in lst:
        return lst.index (a)
    return -1

def list_insert (lst, idx, a):
    if type (a) == type (list ()):
        lst = lst[:idx] + a + lst[idx:]
    else:
        lst.insert (idx, a)
    return lst

def list_insert_before (lst, target, a):
    return list_insert (lst, list_find (lst, target), a)

def most_significant_in_dict (d, name, sep):
    '''Return most significant variable from DICT

NAME is less significant when it contains less bits sepated by SEP.'''
    v = None
    while name:
        if d.has_key (name):
            v = d[name]
            break
        name = name[:max (name.rfind (sep), 0)]
    return v

def dissect_url (url):
    s = url.replace ('?', '&')
    lst = s.split ('&')
    def dict (tuple_lst):
        '''allow multiple values to be appended into a list'''
        d = {}
        for k, v in tuple_lst:
            if not k in d.keys ():
                d[k] = v
            else:
                if type (d[k]) == type (''):
                    # FIXME: list constructor barfs for strings?
                    # d[k] = list (d[k])
                    d[k] = [d[k]]
                d[k].append (v)
        return d
    return lst[0], dict (map (lambda x: x.split ('='), lst[1:]))

def list_or_tuple (x):
    return type (x) == type (list ()) or type (x) == type (tuple ())

def appy_or_map (f, x):
    if list_or_tuple (x):
        return map (f, x)
    return [f (x)]

def lst (x):
    if not list_or_tuple (x):
        return [x]
    return x

def list_remove (lst, x):
    if not list_or_tuple (x):
        lst.remove (x)
    else:
        lst = filter (lambda i: i not in x, lst)
    return lst

def get_from_parents (cls, key):
    base = cls.__name__
    p = base.find ('__')
    if p >= 0:
        base = base[:p]
    for i in cls.__bases__:
        if not base in i.__name__:
            # multiple inheritance, a base class like UnixBuild
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

def dump_file (str, name, mode='w', permissions=None):
    if not type (mode) == type (''):
        print 'MODE:', mode
        print 'STR:', str
        print 'NAME:', name
        assert type (mode) == type ('')

    dir = os.path.split (name)[0]
    if not os.path.exists (dir):
        os.makedirs (dir)

    f = open (name, mode)
    f.write (str)
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

def test ():
    print forall (x for x in [1, 1])
    print dissect_url ('git://anongit.freedesktop.org/git/fontconfig?revision=1234')
    print dissect_url ('http://lilypond.org/foo-123.tar.gz&patch=a&patch=b')
    print rewrite_url ('ftp://foo.com/pub/foo/foo-123.tar.gz',
                       'http://lilypond.org/downloads')

if __name__ =='__main__':
    test ()
