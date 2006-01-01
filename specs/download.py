
def untar_flags (tarball):
	flags = ''
	if tarball.endswith ('.tar.gz') or tarball.endswith ('.tgz'):
		flags = '-xzf'
	elif tarball.endswith ('.tar.bz2'):
		flags = '-jxf'
	elif tarball.endswith ('.tar'):
		flags = '-xf'
	return flags

gtk = 'ftp://ftp.gtk.org/pub/gtk/v%(gtk_version)s/%(name)s-%(ball_version)s.tar.%(format)s'

gnubase = 'ftp://ftp.gnu.org/pub/gnu'
	# FIXME: find complete GNU mirror
	# base = 'ftp://dl.xs4all.nl/pub/mirror/gnu'
	# base = 'ftp://sunsite.dk/pub/gnu'
gnu = gnubase + '/%(name)s/%(name)s-%(ball_version)s.tar.%(format)s'

gcc = gnubase + '/%(name)s/%(name)s-%(ball_version)s/%(name)s-%(ball_version)s.tar.%(format)s'
alphabase = 'ftp://alpha.gnu.org/pub/gnu'
alpha = alphabase + '/%(name)s/%(name)s-%(ball_version)s.tar.%(format)s'

nongnu_savannah = 'http://download.savannah.nongnu.org/releases/%(name)s/%(name)s-%(ball_version)s.tar.%(format)s'

freetype = 'ftp://sunsite.cnlab-switch.ch/mirror/freetype/freetype2/%(name)s-%(ball_version)s.tar.%(format)s'

nongnu = 'http://download.savannah.nongnu.org/releases/%(name)s/%(name)s-%(ball_version)s.tar.%(format)s'

fontconfig = 'http://www.fontconfig.org/release/%(name)s-%(ball_version)s.tar.%(format)s'

hw = 'http://lilypond.org/~hanwen/%(name)s-%(ball_version)s.tar.%(format)s'

jantien = 'http://www.xs4all.nl/~jantien/%(name)s-%(ball_version)s.tar.%(format)s'

opendarwin = 'http://www.opendarwin.org/downloads/%(name)s-%(ball_version)s.tar.%(format)s'
# mesh is broken today
#'http://mesh.dl.sourceforge.net/sourceforge/%(name)s/%(name)s-%(ball_version)s.tar.%(format)s'

sf = 'http://surfnet.dl.sourceforge.net/sourceforge/%(name)s/%(name)s-%(ball_version)s.tar.%(format)s'

libpng = 'http://surfnet.dl.sourceforge.net/sourceforge/%(name)s/%(name)s-%(ball_version)s-config.tar.%(format)s'

mingw = 'http://surfnet.dl.sourceforge.net/sourceforge/mingw/%(name)s-%(ball_version)s.tar.%(format)s'

lp = 'http://lilypond.org/mingw/uploads/%(name)s/%(name)s-%(ball_version)s-src.tar.%(format)s'

zlib = 'http://www.zlib.net/%(name)s-%(ball_version)s.tar.%(format)s'

sourceforge = sf

sourceforge_homepage = 'http://%(name)s.sourceforge.net/%(name)s-%(ball_version)s.tar.%(format)s'

python = 'http://python.org/ftp/python/%(ball_version)s/Python-%(ball_version)s.tar.%(format)s' 

cygwin = 'ftp://ftp.sunsite.dk/pub/cygwin/release/%(name)s/%(name)s-%(ball_version)s.tar.%(format)s'

cups = 'http://ftp.easysw.com/pub/%(name)s/%(version)s/espgs-%(version)s-source.tar.%(format)s'
jpeg = 'ftp://ftp.uu.net/graphics/jpeg/jpegsrc.v6b.tar.gz'

freebsd_ports = 'ftp://ftp.uk.freebsd.org/pub/FreeBSD/ports/local-distfiles/lioux/%(name)s-%(version)s.tar.%(format)s'

