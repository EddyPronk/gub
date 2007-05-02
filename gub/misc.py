# misc utils
import os
import re
import string
import sys
import urllib
 
def join_lines (str):
    return str.replace ('\n', ' ')

def load_module (file_name, name=None):
    if not name:
        import os
        name = os.path.split (os.path.basename (file_name))[0]
    file = open (file_name)
    desc = ('.py', 'U', 1)
    import imp
    return imp.load_module (name, file, file_name, desc)

def load_spec (spec_file_name):
    import os
    # FIXME: should use settings.specdir
    specdir = os.getcwd () + '/gub/specs'
    return load_module ('%(specdir)s/%(spec_file_name)s.py' % locals ())

def bind (function, arg1):
    def bound (*args, **kwargs):
        return function (arg1, *args, **kwargs)
    return bound

def read_pipe (cmd, ignore_errors=False):
    print 'Executing pipe %s' % cmd
    pipe = os.popen (cmd)

    val = pipe.read ()
    if pipe.close () and not ignore_errors:
        raise SystemFailed ("Pipe failed: %s" % cmd)
    
    return val

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
    return re.match ('^(.*?)-([0-9].*(-[0-9]+)?)(\.[a-z]*)?(\.tar\.(bz2|gz)|\.gu[bp])$', s)

def split_ball (s):
    m = is_ball (s)
    if not m:
        return (s, (0, 0), '')
    return (m.group (1), string_to_version (string.join (split_version (m.group (2)), '-')), m.group (6))

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

def bind_method (func, obj):
    return lambda *args: func (obj, *args)


def tar_compression_flag (ball):
    compression_flag = ''
    if ball.endswith ('gub'):
        compression_flag = 'z'
    elif ball.endswith ('gup'):
        compression_flag = 'z'
    elif ball.endswith ('bz2'):
        compression_flag = 'j'
    elif ball.endswith ('gz'):
        compression_flag = 'z'
    return compression_flag


def file_is_newer (f1, f2):
    return (not os.path.exists (f2)
        or os.stat (f1).st_mtime > os.stat (f2).st_mtime)

def find (dir, pattern):
    """
    Find files under DIR match the regex pattern.
    """
    
    if type('') == type(pattern):
        pattern = re.compile (pattern)

    dir = re.sub ( "/*$", '/', dir)
    results = []
    for (root, dirs, files) in os.walk (dir):
        root = root.replace (dir, '')
        files = [os.path.join (root, f) for f in files if pattern.search (f)]
        
        results += files
        
    return results

def download_url (url, dest_dir):
    print 'Downloading', url
    _download_url (url, dest_dir)
    
def _download_url (url, dest_dir, stderr)
    if not os.path.isdir (dest_dir):
        raise Exception ("not a dir", dest_dir)

    bufsize = 1024 * 50
    filename = os.path.split (urllib.splithost (url)[1])[1]

    out_filename = dest_dir + '/' + filename
    try:
        output = open (out_filename, 'w')
        opener = urllib.URLopener ()
        url_stream = opener.open (url)
        while True:
            contents = url_stream.read (bufsize)
            output.write (contents)
            stderr.write ('.')
            stderr.flush ()
            if not contents:
                break
        stderr.write ('\n')
    except:
        os.unlink (out_filename)
        raise
    
def forall (generator):
    v = True
    try:
        while v:
            v = v and generator.next()
    except StopIteration:
        pass

    return v
            
class SystemFailed (Exception):
    pass


def system (cmd, ignore_errors=False):
    #URG, go through oslog
    print 'Executing command %s' % cmd
    stat = os.system (cmd)
    if stat and not ignore_errors:
        raise SystemFailed ('Command failed ' + `stat`)

def file_mod_time (path):
    import stat
    return os.stat (path)[stat.ST_MTIME]


def map_command_dir (dir, command, filter_out=[], extension_filter_out=[]):
    import os
    if not os.path.isdir (dir):
        raise ('warning: no such dir: %(dir)s' % locals ())
    (root, dirs, files) = os.walk (dir).next ()
    for file in files:
        if (os.path.basename (file) not in filter_out
          and (os.path.splitext (file)[1] not in extension_filter_out)):
            system ('%(command)s %(root)s/%(file)s' % locals (),
                    ignore_errors=True)

def ball_basename (ball):
    s = ball
    s = re.sub ('.tgz', '', s)
    s = re.sub ('-src\.tar.*', '', s)
    s = re.sub ('\.tar.*', '', s)
    s = re.sub ('_%\(package_arch\)s.*', '', s)
    s = re.sub ('_%\(version\)s', '-%(version)s', s)
    return s

class MethodOverrider:
    """Override a object method with a function defined outside the
class hierarchy.
    
    Usage:

    def new_func (old_func, arg1, arg2, .. ):
        ..do stuff..
        pass
    
    old = obj.func
    p.func = MethodOverrider (old,
                              new_func,
                              (arg1, arg2, .. ))
    """
    def __init__ (self, old_func, new_func, extra_args=()):
        self.new_func = new_func
        self.old_func = old_func
        self.args = extra_args
    def __call__ (self):
        all_args = (self.old_func (),) + self.args  
        return apply (self.new_func, all_args)

def testme ():
    print forall (x for x in [1, 1])
    
if __name__ =='__main__':
    testme ()

