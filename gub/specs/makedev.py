from gub import tools

class Makedev__tools (tools.MakeBuild):
    source = 'http://ftp.debian.nl/debian/pool/main/m/makedev/makedev_3.3.8.2.orig.tar.gz'
    patches = ['makedev-fno-stack-protector.patch']
    install_command = '''make %(compile_flags)s DESTDIR=%(install_root)s install'''
