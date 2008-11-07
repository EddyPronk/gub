from gub import tools

class Rsync__tools (tools.AutoBuild):
    source = 'ftp://ftp.samba.org/pub/rsync/src/rsync-3.0.4.tar.gz'
    # adding libpopt build depependency not really necessary, as rsync
    # bundles it.
