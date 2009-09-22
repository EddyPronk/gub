from gub import target

class Base_passwd (target.AutoBuild):
    source = 'ftp://ftp.nl.debian.org/debian/pool/main/b/base-passwd/base-passwd_3.5.11.tar.gz'
    srcdir_build_broken = True
    def get_subpackage_names (self):
        return ['']
