import glob
import re
import os
#
from gub import context
from gub import target
from gub import loggedos

darwin_sdk_version = '0.4'

class Rewirer (context.RunnableContext):
    def __init__ (self, settings):
        context.RunnableContext.__init__ (self,settings)
        self.ignore_libs = None

    def get_libaries (self, name):
        lib_str = loggedos.read_pipe (
            self.runner.logger,
            self.expand ('%(cross_prefix)s/bin/%(target_architecture)s-otool -L %(name)s',
                         locals ()),
            ignore_errors=True)

        libs = []
        for i in lib_str.split ('\n'):
            m = re.search (r'\s+(.*) \(.*\)', i)
            if not m:
                continue
            if self.ignore_libs.has_key (m.group (1)):
                continue

            libs.append (m.group (1))

        return libs

    def rewire_mach_o_object (self, name, substitutions):
        if not substitutions:
            return
        changes = ' '.join (['-change %s %s' % (o, d)
                             for (o, d) in substitutions])
        self.system (
            '%(cross_prefix)s/bin/%(target_architecture)s-install_name_tool %(changes)s %(name)s ',
              locals ())

    def rewire_mach_o_object_executable_path (self, name):
        orig_libs = ['/usr/lib']

        libs = self.get_libaries (name)
        subs = []
        for i in libs:

            # FIXME: I do not understand this comment
            ## ignore self.
            self.runner.action (os.path.split (i)[1] + ' '
                                + os.path.split (name)[1] + '\n')

            if os.path.split (i)[1] == os.path.split (name)[1]:
                continue

            for o in orig_libs:
                if re.search (o, i):
                    newpath = re.sub (o, '@executable_path/../lib/', i);
                    subs.append ((i, newpath))
                elif i.find (self.expand ('%(targetdir)s')) >= 0:
                    print 'found targetdir in linkage', i
                    raise 'abort'

        self.rewire_mach_o_object (name, subs)

    def rewire_binary_dir (self, dir):
        if not os.path.isdir (dir):
            raise 'Not a directory', dir

        (root, dirs, files) = os.walk (dir).next ()
        files = [os.path.join (root, f) for f in files]

        skip_libs = ['libgcc_s']
        for f in files:
            found_skips = [s for s in  skip_libs if f.find (s) >= 0]
            if found_skips:
                continue

            if os.path.isfile (f):
                self.rewire_mach_o_object_executable_path (f)

    def set_ignore_libs_from_tarball (self, tarball):
        files = loggedos.read_pipe (self.runner.logger,
                                    'tar -tzf %s' % tarball).split ('\n')
        self.set_ignore_libs_from_files (files)

    def set_ignore_libs_from_files (self, files):
        self.ignore_libs = dict ((k.strip ()[1:], True)
             for k in files
             if re.match (r'^\./usr/lib/', k))

    def rewire_root (self, root):
        if self.ignore_libs == None:
            raise 'error: should init with file_manager.'

        self.rewire_binary_dir (root + '/usr/lib')
        for d in glob.glob (root + '/usr/lib/pango/*/modules/'):
            self.rewire_binary_dir (d)

        self.rewire_binary_dir (root + '/usr/bin')

class Package_rewirer:
    def __init__ (self, rewirer, package):
        self.rewirer = rewirer
        self.package = package

    def rewire (self):
        self.rewirer.rewire_root (self.package.install_root ())

def get_cross_build_dependencies (settings):
    return ['cross/gcc']

def strip_build_dep (old_val, what):
    deps = old_val

    for w in what:
        if w in deps:
            deps.remove (w)
    deps.sort ()
    return deps


def strip_dependency_dict (old_val, what):
    d = dict ((k,[p for p in deps if p not in what])
             for (k, deps) in old_val.items ())
    return d

def change_target_package (p):
    from gub import misc
    from gub import cross
    from gub import build
    cross.change_target_package (p)
    p.get_build_dependencies = misc.MethodOverrider (p.get_build_dependencies,
                                                     strip_build_dep,
                                                     (['zlib', 'zlib-devel'],))
    p.get_dependency_dict = misc.MethodOverrider (p.get_dependency_dict,
                                                  strip_dependency_dict,
                                                  (['zlib', 'zlib-devel'],))
    target.change_target_dict (p, {

            ## We get a lot of /usr/lib/ -> @executable_path/../lib/
            ## we need enough space in the header to do these relocs.
            'LDFLAGS': '-Wl,-headerpad_max_install_names ',

            ## UGH: gettext fix for ptrdiff_t
            'CPPFLAGS' : '-DSTDC_HEADERS',
            })

def system (c):
    s = os.system (c)
    if s:
        raise 'barf'

def get_darwin_sdk ():
    def system (s):
        print s
        if os.system (s):
            raise 'barf'

    host = 'maagd'
    version = '0.4'
    darwin_version  = 8

    dest = 'darwin%(darwin_version)d-sdk-%(version)s' % locals ()

    system ('rm -rf %s' % dest)
    os.mkdir (dest)

    src = '/Developer/SDKs/'

    if darwin_version == 7:
        src += 'MacOSX10.3.9.sdk'
    else:
        src += 'MacOSX10.4u.sdk'

    cmd =  ('rsync -a -v %s:%s/ %s/' % (host, src, dest))
    system (cmd)
    system ('chmod -R +w %s' % dest)
    system ('tar cfz %s.tar.gz %s' % (dest, dest))

if __name__== '__main__':
    import sys
    if len (sys.argv) > 1:
        get_darwin_sdk ()

