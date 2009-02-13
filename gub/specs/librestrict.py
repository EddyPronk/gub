import os
#
from gub import tools
from gub import misc

class Librestrict__tools (tools.MakeBuild):
    source = 'url://host/librestrict-1.9a.tar.gz'
    def librestrict_flavours (self):
        return list (sorted (os.environ.get ('LIBRESTRICT',
                                             'open').replace (':', ' ').split (' ')))
    def flavours (self):
        return ['exec', 'open', 'stat']
    def name (self):
        return 'librestrict-' + '-'.join (self.librestrict_flavours ())
    def get_conflict_dict (self):
        return {'': ['librestrict',
                     'librestrict-exec',
                     'librestrict-exec-open',
                     'librestrict-exec-open-stat',
                     'librestrict-exec-stat',
                     'librestrict-open',
                     'librestrict-open-stat',
                     'librestrict-stat',
                     ]}
    def shadow (self):
        self.system ('rm -rf %(builddir)s')
        self.shadow_tree ('%(gubdir)s/librestrict', '%(builddir)s')
    def makeflags (self):
        return 'prefix=%(system_prefix)s'
    def LD_PRELOAD (self):
        return ''

class Librestrict_nomake__tools (Librestrict__tools):
    def compile_command (self):
        # URG, must *not* have U __stack_chk_fail@@GLIBC_2.4
        # because glibc-[core-]2.3 will not install with LD_PRELOAD
        CFLAGS = '-fno-stack-protector'
        compile = 'gcc -W -Wall %(CFLAGS)s -fPIC -shared -o lib%(name)s.so %(name)s.c'
        sources = ' '.join (['restrict-%s.c' % name for name in self.librestrict_flavours ()])
        b = 'cd %(builddir)s && '
        command = b + 'cat %(sources)s > restrict-all.c\n' % locals ()
        def updated (d, e):
            c = d.copy ()
            c.update (e)
            return c
        for f in self.flavours () + ['all']:
            name = 'restrict-' + f
            command += (b
                        + compile % locals ()
                        + ' || '
                        + compile % updated (locals (), {'CFLAGS':''})
                        + '\n')
        command += b + 'mv librestrict-all.so librestrict.so'
        return command
    def install_command (self):
        return (misc.join_lines ('''
mkdir -p %(install_root)s/%(system_prefix)s/lib
&& cp -p librestrict*.so %(install_root)s/%(system_prefix)s/lib
'''))

Librestrict__tools = Librestrict_nomake__tools
