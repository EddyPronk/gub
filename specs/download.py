def gtk ():
	return 'ftp://ftp.gtk.org/pub/gtk/v%(gtk_version)s/%(name)s-%(version)s.tar.%(format)s'

def gnu ():
	# base = 'ftp://dl.xs4all.nl/pub/mirror/gnu'
	base = 'ftp://sunsite.dk/pub/gnu'
	return base + '/%(name)s/%(name)s-%(version)s.tar.%(format)s'

def freetype ():
	return 'ftp://sunsite.cnlab-switch.ch/mirror/freetype/freetype2/%(name)s-%(version)s.tar.%(format)s'

def fontconfig ():
	return 'http://www.fontconfig.org/release/%(name)s-%(version)s.tar.%(format)s'

def hw ():
	return 'http://lilypond.org/~hanwen/%(name)s-%(version)s.tar.%(format)s'

def opendarwin ():
	return 'http://www.opendarwin.org/downloads/%(name)s-%(version)s.tar.%(format)s'
