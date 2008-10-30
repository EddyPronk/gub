from gub import target

# hmmrg, no libgcrypt.so in here...
class Libgcrypt (target.AutoBuild):
    source = 'ftp://ftp.gnupg.org/gcrypt/gnupg/gnupg-1.4.9.tar.bz2'
