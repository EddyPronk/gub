#
from gub import context
from gub import misc
from gub import target
from gub.specs import lilypond
from gub import versiondb

class LilyPond_doc (target.AutoBuild):
    source = lilypond.LilyPond.source
    never_install = 'True'
    def __init__ (self, settings, source):
        target.AutoBuild.__init__ (self, settings, source)
        source.version = misc.bind_method (lilypond.LilyPond.version_from_VERSION, source)
        source.is_tracking = misc.bind_method (lambda x: True, source)
        source.is_downloaded = misc.bind_method (lambda x: True, source)
        source.update_workdir = misc.bind_method (lambda x: True, source)
    def _get_build_dependencies (self):
        return [self.settings.build_platform + '::lilypond',
                'tools::netpbm',
                'tools::imagemagick',
                'tools::rsync', # ugh, we depend on *rsync* !?
                #'tools::texlive',
                ]
    def get_subpackage_names (self):
        return ['']
    def stages (self):
        return ['compile', 'install', 'package']
    def builddir (self):
        #URWGSGSEWNG
        return '%(allbuilddir)s/lilypond%(ball_suffix)s'
    def srcdir (self):
        #URWGSGSEWNG
        return '%(allsrcdir)s/lilypond%(ball_suffix)s'
    def makeflags (self):
        return misc.join_lines ('''
CROSS=no
DOCUMENTATION=yes
WEB_TARGETS="offline online"
TARGET_PYTHON=/usr/bin/python
''')
    @context.subst_method
    def build_number (self):
        # FIXME, get from versions.db?
        ##return '1'
        ## urg, can't expand here
        ## vdb = versiondb.VersionDataBase (self.expand ('%(uploads)s/lilypond.versions'))
        vdb = versiondb.VersionDataBase ('uploads/lilypond.versions')
        vdb.get_binaries_from_url ('http://lilypond.org/download/')
        vdb.write ()
        return str (vdb.get_next_build_number (misc.string_to_version (self.version ())))
    @context.subst_method
    def doc_ball (self):
        return '%(uploads)s/lilypond-%(version)s-%(build_number)s.documentation.tar.bz2'
    @context.subst_method
    def web_ball (self):
        return '%(uploads)s/lilypond-%(version)s-%(build_number)s.webdoc.tar.bz2'
    @context.subst_method
    def doc_limits (self):
        if '64' in self.settings.build_platform:
            return 'ulimit -m 512000 && ulimit -d 512000 && ulimit -v 1024000 '
        return 'ulimit -m 256000 && ulimit -d 256000 && ulimit -v 384000 '
    @context.subst_method
    def doc_relocation (self):
        return misc.join_lines ('''
LILYPOND_EXTERNAL_BINARY=%(system_prefix)s/bin/lilypond
PATH=%(tools_prefix)s/bin:%(system_prefix)s/bin:$PATH
GS_LIB=%(system_prefix)s/share/ghostscript/*/lib
MALLOC_CHECK_=2
LD_LIBRARY_PATH=%(tools_prefix)s/lib:%(system_prefix)s/lib:${LD_LIBRARY_PATH-/foe}
''')
    def force_sequential_build (self):
        '''
Writing snippets...
All snippets are up to date...lilypond-book.py (GNU LilyPond) 2.12.3
Traceback (most recent call last):
  File "/home/janneke/vc/gub/target/linux-64/src/lilypond-git.sv.gnu.org--lilypo
nd.git-master/scripts/lilypond-book.py", line 2107, in ?
    main ()
  File "/home/janneke/vc/gub/target/linux-64/src/lilypond-git.sv.gnu.org--lilypo
nd.git-master/scripts/lilypond-book.py", line 2089, in main
    chunks = do_file (files[0])
  File "/home/janneke/vc/gub/target/linux-64/src/lilypond-git.sv.gnu.org--lilypo
nd.git-master/scripts/lilypond-book.py", line 1993, in do_file
    do_process_cmd (chunks, input_fullname, global_options)
  File "/home/janneke/vc/gub/target/linux-64/src/lilypond-git.sv.gnu.org--lilypo
nd.git-master/scripts/lilypond-book.py", line 1844, in do_process_cmd
    options.output_dir)
  File "/home/janneke/vc/gub/target/linux-64/src/lilypond-git.sv.gnu.org--lilypo
nd.git-master/scripts/lilypond-book.py", line 1278, in link_all_output_files
    os.makedirs (dst_path)
  File "/home/janneke/vc/gub/target/tools/root/usr/lib/python2.4/os.py", line 15
9, in makedirs
    mkdir(name, mode)
OSError: [Errno 17] File exists: '/home/janneke/vc/gub/target/linux-64/build/lil
ypond-git.sv.gnu.org--lilypond.git-master/Documentation/user/out/6a'
'''
        return True
    def compile_command (self):
        return ('%(doc_limits)s '
                '&& %(doc_relocation)s '
                + target.AutoBuild.compile_command (self)
                + ' do-top-doc all doc web')
    def install_flags (self):
        return (self.makeflags ()
                + 'prefix= '
                + 'infodir=/share/info '
                + 'DESTDIR=%(install_root)s '
                + 'mandir=/share/man ')
    def install_command (self):
        return ('%(doc_limits)s '
                '&& %(doc_relocation)s '
                + target.AutoBuild.install_command (self)
                .replace (' install', ' web-install install-help2man')
                + self.install_flags ())
    def install (self):
        target.AutoBuild.install (self) 
        self.system ('''
cp -f sourcefiles/dir %(install_root)s/share/info/dir
cd %(install_root)s/share/info && %(doc_relocation)s install-info --info-dir=. lilypond.info
tar -C %(install_root)s -cjf %(doc_ball)s .
tar --exclude '*.signature' -C %(builddir)s/out-www/online-root -cjf %(web_ball)s .
''')


Lilypond_doc = LilyPond_doc
