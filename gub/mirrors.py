gtk = 'ftp://ftp.gtk.org/pub/gtk/v%(gtk_version)s/%(name)s-%(version)s.tar.%(format)s'
gnome_213 ='http://ftp.gnome.org/pub/GNOME/platform/2.13/2.13.90/sources/%(name)s-%(version)s.tar.%(format)s'

gnome_214 ='http://ftp.gnome.org/pub/GNOME/platform/2.14/2.14.3/sources/%(name)s-%(version)s.tar.%(format)s'

gnome_216 ='http://ftp.gnome.org/pub/GNOME/platform/2.16/2.16.2/sources/%(name)s-%(version)s.tar.%(format)s'

gnome_218 ='http://ftp.gnome.org/pub/GNOME/platform/2.18/2.18.1/sources/%(name)s-%(version)s.tar.%(format)s'

gnubase = 'ftp://ftp.gnu.org/pub/gnu'
    # FIXME: find complete GNU mirror
    # base = 'ftp://dl.xs4all.nl/pub/mirror/gnu'
    # base = 'ftp://sunsite.dk/pub/gnu'
gnu = gnubase + '/%(name)s/%(name)s-%(version)s.tar.%(format)s'

gcc = gnubase + '/%(name)s/%(name)s-%(version)s/%(name)s-%(version)s.tar.%(format)s'
glibc = gnubase + '/glibc/%(name)s-%(version)s.tar.%(format)s'
alphabase = 'ftp://alpha.gnu.org/pub/gnu'
alpha = alphabase + '/%(name)s/%(name)s-%(version)s.tar.%(format)s'

nongnu_savannah = 'http://download.savannah.nongnu.org/releases/%(name)s/%(name)s-%(version)s.tar.%(format)s'
nongnu          = 'ftp://ftp.gnu.org/pub/gnu/non-gnu/%(name)s/%(name)s-%(version)s.tar.%(format)s'

freetype = 'http://download.savannah.gnu.org/releases/freetype/%(name)s-%(version)s.tar.%(format)s'

fontconfig = 'http://www.fontconfig.org/release/%(name)s-%(version)s.tar.%(format)s'

lilypondorg = 'http://lilypond.org/download/gub-sources/%(name)s-%(version)s.tar.%(format)s'
lilypondorg_deb = 'http://lilypond.org/download/gub-sources/%(name)s_%(version)s_%%(package_arch)s.%(format)s'

jantien = 'http://www.xs4all.nl/~jantien/%(name)s-%(version)s.tar.%(format)s'

opendarwin = 'http://www.opendarwin.org/downloads/%(name)s-%(version)s.tar.%(format)s'
# mesh is broken today
#'http://mesh.dl.sourceforge.net/sourceforge/%(name)s/%(name)s-%(version)s.tar.%(format)s'

sf = 'http://surfnet.dl.sourceforge.net/sourceforge/%(name)s/%(name)s-%(version)s.tar.%(format)s'

libpng = 'http://surfnet.dl.sourceforge.net/sourceforge/%(name)s/%(name)s-%(version)s-config.tar.%(format)s'

mingw = 'http://surfnet.dl.sourceforge.net/sourceforge/mingw/%(name)s-%(version)s.tar.%(format)s'

lp = 'http://lilypond.org/mingw/uploads/%(name)s/%(name)s-%(version)s-src.tar.%(format)s'

zlib = 'http://www.zlib.net/%(name)s-%(version)s.tar.%(format)s'

sourceforge = sf

sourceforge_homepage = 'http://%(name)s.sourceforge.net/%(name)s-%(version)s.tar.%(format)s'

fondu = 'http://%(name)s.sourceforge.net/%(name)s_src-%(version)s.tgz'

python = 'http://python.org/ftp/python/%(version)s/Python-%(version)s.tar.%(format)s' 

cygwin_bin = 'http://mirrors.kernel.org/sourceware/cygwin/release/%(name)s/%(name)s-%(version)s.tar.%(format)s'

# FIXME: s/nl/%(gps-location)s/
linux_2_4 = 'http://www.nl.kernel.org/pub/linux/kernel/v2.4/linux-%(version)s.tar.%(format)s'
linux_2_5 = 'http://www.nl.kernel.org/pub/linux/kernel/v2.5/linux-%(version)s.tar.%(format)s'
linux_2_6 = 'http://www.nl.kernel.org/pub/linux/kernel/v2.6/linux-%(version)s.tar.%(format)s'

cygwin = 'http://mirrors.kernel.org/sourceware/cygwin/release/%(name)s/%(name)s-%(version)s-src.tar.%(format)s'

cygwin_gcc = 'http://mirrors.kernel.org/sourceware/cygwin/release/gcc/%(name)s/%(name)s-%(version)s-src.tar.%(format)s'

# FIXME:  %(version)s should probably be %(version)s for download,
# to include possible '-xyz' version part.
cups = 'http://ftp.easysw.com/pub/%(name)s/%(version)s/espgs-%(version)s-source.tar.%(format)s'
jpeg = 'ftp://ftp.uu.net/graphics/jpeg/jpegsrc.v6b.tar.gz'

freebsd_ports = 'ftp://ftp.uk.freebsd.org/pub/FreeBSD/ports/local-distfiles/lioux/%(name)s-%(version)s.tar.%(format)s'

freedesktop = 'http://%(name)s.freedesktop.org/releases/%(name)s-%(version)s.tar.%(format)s'

glibc_deb = 'http://ftp.debian.org/debian/pool/main/g/glibc/%(name)s_%(version)s_%%(package_arch)s.%(format)s'

lkh_deb = 'http://ftp.debian.org/debian/pool/main/l/linux-kernel-headers/%(name)s_%(version)s_%%(package_arch)s.%(format)s'

libdbi_deb = 'http://ftp.debian.org/debian/pool/main/libd/libdbi/%(name)s_%(version)s_%%(package_arch)s.%(format)s'

gcc_41 = 'ftp://ftp.fu-berlin.de/unix/languages/gcc/releases/gcc-%(version)s/gcc-%(version)s.tar.bz2'
gcc_snap = 'ftp://ftp.fu-berlin.de/unix/languages/gcc/snapshots/%(version)s/gcc-%(version)s.tar.bz2'

boost_1_33_1 = 'http://surfnet.dl.sourceforge.net/sourceforge/boost/boost_1_33_1.tar.%(format)s'

gnucvs =  ':pserver:anoncvs@cvs.sv.gnu.org:/cvsroot/%(name)s'

redhat_snapshots = 'ftp://sources.redhat.com/pub/%(name)s/snapshots/%(name)s-%(version)s.tar.%(format)s'

#glibc_2_3_snapshots = redhat_snapshots
glibc_2_3_snapshots = lilypondorg

berlios = 'http://download.berlios.de/%(name)s/%(name)s-%(version)s.tar.%(format)s'

xerces_c = 'http://apache.cs.uu.nl/dist/xml/%(name)s/source/%(name)s-src_%(version)s.tar.%(format)s'


def with_template (
    mirror=gnu,
    version='',
    strip_components=1,
    format='gz',
    name='',
    ball_version=''):
    if not ball_version and version:
        ball_version = version
    url = mirror % locals ()
    if strip_components != 1:
        url += '&strip_components=%(strip_components)s'
    # update helper
    print "%(name)s.py:\n    source = '%(url)s'" % locals ()
    return url

with_tarball = with_template
