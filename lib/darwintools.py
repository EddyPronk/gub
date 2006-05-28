import glob
import re
import os

import context
import cross
import download
import gub

darwin_sdk_version = '0.4'
class Odcctools (cross.CrossToolSpec):
    def configure (self):
        cross.CrossToolSpec.configure (self)

        ## remove LD64 support.
        self.file_sub ([('ld64','')],
                       self.builddir () + '/Makefile')

class Darwin_sdk (gub.SdkBuildSpec):
    def __init__ (self, settings):
        gub.SdkBuildSpec.__init__ (self, settings)
        
        os_version = 7
        if settings.platform == 'darwin-x86':
            os_version = 8
            
        name = 'darwin%d-sdk' % os_version
        ball_version = darwin_sdk_version
        format = 'gz'
        mirror = download.hw % locals()
        self.with (version=darwin_sdk_version,
             mirror=mirror, format='gz')

    def patch (self):
        self.system ('''
rm %(srcdir)s/usr/lib/libgcc*
rm %(srcdir)s/usr/lib/libstdc\+\+*
rm %(srcdir)s/usr/lib/libltdl*
rm %(srcdir)s/usr/include/ltdl.h
rm -f %(srcdir)s/usr/lib/gcc/*-apple-darwin*/*/*dylib
rm -rf %(srcdir)s/usr/lib/gcc
''')

        ## ugh, need to have gcc/3.3/machine/limits.h
        ### self.system ('rm -rf %(srcdir)s/usr/include/gcc')
        ##self.system ('rm -rf %(srcdir)s/usr/include/machine/limits.h')

        ## limits.h symlinks into GCC.
        
        pat = self.expand ('%(srcdir)s/usr/lib/*.la')
        for a in glob.glob (pat):
            self.file_sub ([(r' (/usr/lib/.*\.la)', r'%(system_root)s\1')], a)


class Gcc (cross.Gcc):
    def patch (self):
        self.file_sub ([('/usr/bin/libtool', '%(crossprefix)s/bin/%(target_architecture)s-libtool')],
                       '%(srcdir)s/gcc/config/darwin.h')

        self.file_sub ([('--strip-underscores', '--strip-underscore')],
                       "%(srcdir)s/libstdc++-v3/scripts/make_exports.pl")

        if int (self.expand('%(version)s')[2]) < 2:
            self.file_sub ([("nm", "%(tool_prefix)snm ")],
                           "%(srcdir)s/libstdc++-v3/scripts/make_exports.pl")

    def configure_command (self):
        c = cross.Gcc.configure_command (self)
#                c = re.sub ('enable-shared', 'disable-shared', c)
        return c
    

    def configure (self):
        cross.Gcc.configure (self)

    def rewire_gcc_libs (self):
        skip_libs = ['libgcc_s']
        for l in self.locate_files ("%(install_root)s/usr/lib/", '*.dylib'):
            found_skips = [s for s in  skip_libs if l.find (s) >= 0]
            if found_skips:
                continue
            
            id = self.read_pipe ('%(tool_prefix)sotool -L %(l)s', locals ()).split()[1]
            id = os.path.split (id)[1]
            self.system ('%(tool_prefix)sinstall_name_tool -id /usr/lib/%(id)s %(l)s', locals ())
        
    def install (self):
        cross.Gcc.install (self)
        self.rewire_gcc_libs ()

    def get_build_dependencies (self):
        return ['odcctools']
    
class Gcc__darwin (Gcc):
    def configure (self):
        cross.Gcc.configure (self)

    def install (self):
        ## UGH ?
        ## Gcc.install (self)

        cross.Gcc.install (self)
        self.rewire_gcc_libs ()
        
class Rewirer (context.Os_context_wrapper):
    def __init__ (self, settings):
        context.Os_context_wrapper.__init__ (self,settings)
        self.ignore_libs = None

    def get_libaries (self, name):
        lib_str = self.read_pipe ('''
%(crossprefix)s/bin/%(target_architecture)s-otool -L %(name)s
''',
                     locals (), ignore_error=True)

        libs = []
        for l in lib_str.split ('\n'):
            m = re.search (r"\s+(.*) \(.*\)", l)
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
        self.system ('''
%(crossprefix)s/bin/%(target_architecture)s-install_name_tool %(changes)s %(name)s ''',
              locals ())

    def rewire_mach_o_object_executable_path (self, name):
        orig_libs = ['/usr/lib']

        libs = self.get_libaries (name)
        subs = []
        for l in libs:

            ## ignore self.
            print os.path.split (l)[1], os.path.split (name)[1]
            
            if os.path.split (l)[1] == os.path.split (name)[1]:
                continue
            
            for o in orig_libs:
                if re.search (o, l):
                    newpath = re.sub (o, '@executable_path/../lib/', l); 
                    subs.append ((l, newpath))
                elif l.find (self.expand ('%(targetdir)s')) >= 0:
                    print 'found targetdir in linkage', l
                    raise 'abort'

        self.rewire_mach_o_object (name, subs)

    def rewire_binary_dir (self, dir):
        if not os.path.isdir (dir):
            print dir
            raise 'Not a directory'

        (root, dirs, files) = os.walk (dir).next ()
        files = [os.path.join (root, f) for f in files]

        skip_libs = ['libgcc_s']
        for f in files:
            found_skips = [s for s in  skip_libs if f.find (s) >= 0]
            if found_skips:
                continue

            if os.path.isfile (f):
                self.rewire_mach_o_object_executable_path(f)

    def set_ignore_libs (self, file_manager):
        files = file_manager.installed_files ('darwin-sdk')

        d = dict ((k.strip()[1:], True)
             for k in files
             if re.match (r'^\./usr/lib/', k))

        self.ignore_libs = d  

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

def get_cross_packages (settings):
    packages = []
    packages.append (Darwin_sdk (settings))
        
    packages += [Odcctools (settings).with (version='20060413',
                                            mirror=download.opendarwin,
                                            format='bz2')]

    if settings.target_architecture.startswith ("powerpc"):
        packages.append (Gcc (settings).with (version='4.1.0',
                                              mirror=download.gcc_41,
                                              format='bz2'))
    else:
        packages.append (Gcc (settings).with (version='4.2-20060513',
                                              mirror=download.gcc_snap,
                                              format='bz2'))

    return packages

def change_target_packages (packages):
    cross.change_target_packages (packages)
    for p in packages.values ():
        gub.change_target_dict (p, {

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
        
    host  = 'maagd'
    version = '0.4'
    darwin_version  = 8

    dest =        'darwin%(darwin_version)d-sdk-%(version)s' % locals()
    
    system ('rm -rf %s' % dest)
    os.mkdir (dest)
    
    src = '/Developer/SDKs/'

    if darwin_version == 7:
        src += 'MacOSX10.3.9.sdk'
    else:
        src += 'MacOSX10.4u.sdk'
    
    cmd =  ('rsync -a -v %s:%s/ %s/ ' % (host, src, dest))
    system (cmd)
    system ('chmod -R +w %s '  % dest)
    system ('tar cfz %s.tar.gz %s '  % (dest, dest))

if __name__== '__main__':
    import sys
    if len (sys.argv) > 1:
        get_darwin_sdk ()

