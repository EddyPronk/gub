
def untar_flags (tarball):
	flags = ''
	if tarball.endswith ('.tar.gz') or tarball.endswith ('.tgz'):
		flags = '-xzf'
	elif tarball.endswith ('.tar.bz2'):
		flags = '-jxf'
	elif tarball.endswith ('.tar'):
		flags = '-xf'
	return flags

def gtk ():
	return 'ftp://ftp.gtk.org/pub/gtk/v%(gtk_version)s/%(name)s-%(version)s.tar.%(format)s'

def gnu ():
	# FIXME: find complete GNU mirror
	# base = 'ftp://dl.xs4all.nl/pub/mirror/gnu'
	# base = 'ftp://sunsite.dk/pub/gnu'
	base = 'ftp://ftp.gnu.org/pub/gnu'
	return base + '/%(name)s/%(name)s-%(version)s.tar.%(format)s'

def gcc ():
	base = 'ftp://ftp.gnu.org/pub/gnu'
	return base + '/%(name)s/%(name)s-%(version)s/%(name)s-%(version)s.tar.%(format)s'

def alpha ():
	base = 'ftp://alpha.gnu.org/pub/gnu'
	return base + '/%(name)s/%(name)s-%(version)s.tar.%(format)s'

def freetype ():
	return 'ftp://sunsite.cnlab-switch.ch/mirror/freetype/freetype2/%(name)s-%(version)s.tar.%(format)s'

def fontconfig ():
	return 'http://www.fontconfig.org/release/%(name)s-%(version)s.tar.%(format)s'

def hw ():
	return 'http://lilypond.org/~hanwen/%(name)s-%(version)s.tar.%(format)s'

def opendarwin ():
	return 'http://www.opendarwin.org/downloads/%(name)s-%(version)s.tar.%(format)s'

def sf ():
	# mesh is broken today
	#return 'http://mesh.dl.sourceforge.net/sourceforge/%(name)s/%(name)s-%(version)s.tar.%(format)s'
	return 'http://surfnet.dl.sourceforge.net/sourceforge/%(name)s/%(name)s-%(version)s.tar.%(format)s'

def mingw ():
        return 'http://surfnet.dl.sourceforge.net/sourceforge/mingw/%(name)s-%(version)s.tar.%(format)s'

def lp ():
	return 'http://lilypond.org/mingw/uploads/%(name)s/%(name)s-%(version)s-src.tar.%(format)s'

def zlib ():
	return 'http://www.zlib.net/%(name)s-%(version)s.tar.%(format)s'

def sourceforge ():
	return sf ()

def sourceforge_homepage ():
	return 'http://%(name)s.sourceforge.net/%(name)s-%(version)s.tar.%(format)s'

def python ():
	return 'http://python.org/ftp/python/%(version)s/%(name)s-%(version)s.tar.%(format)s' 

def cygwin ():
	return 'ftp://ftp.sunsite.dk/pub/cygwin/release/%(name)s/%(name)s-%(version)s-1.tar.%(format)s'
