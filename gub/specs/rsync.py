from gub import tools

class Rsync__tools (tools.AutoBuild):
    source = 'ftp://ftp.samba.org/pub/rsync/src/rsync-3.0.4.tar.gz'
    patches = ['rsync-popt-add-prefix.patch']
    # adding libpopt build depependency not really necessary, as rsync
    # bundles it.
    configure_flags = (tools.AutoBuild.configure_flags
                + ' --with-included-popt'
                + r''' 'CFLAGS=-DPREFIX=\"%(system_prefix)s\"' ''')
