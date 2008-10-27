from gub import targetbuild

# hmmrg, no libgcrypt.so in here...
class Libgcrypt (targetbuild.AutoBuild):
    source = 'ftp://ftp.gnupg.org/gcrypt/gnupg/gnupg-1.4.9.tar.bz2'
