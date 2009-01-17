from gub import tools

'''
guile tools breaks with 2.63

    /home/janneke/vc/gub/target/tools/src/guile-release_1-8-5/libguile/srfi-14.c:25:1: error: "_GNU_SOURCE" redefined

and lots of

    configure.in:76: warning: AC_COMPILE_IFELSE was called before AC_USE_SYSTEM_EXTENSIONS
/home/janneke/vc/gub/target/tools/src/autoconf-2.63/lib/autoconf/specific.m4:386: AC_USE_SYSTEM_EXTENSIONS is expanded from...
/home/janneke/vc/gub/target/tools/src/autoconf-2.63/lib/autoconf/specific.m4:459: AC_MINIX is expanded from...
configure.in:76: the top level
configure.in:76: warning: AC_RUN_IFELSE was called before AC_USE_SYSTEM_EXTENSIONS
configure.in:83: warning: AC_CACHE_VAL(lt_prog_compiler_pic_works, ...): suspicious cache-id, must contain _cv_ to be cached

'''

class Autoconf__tools (tools.AutoBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/autoconf/autoconf-2.61.tar.gz'
    #source = 'ftp://ftp.gnu.org/pub/gnu/autoconf/autoconf-2.63.tar.gz'
    def get_build_dependencies (self):
        return ['m4']
    def force_sequential_build (self):
        return True
