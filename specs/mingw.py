import download
import gub
import os
import re

# FIXME: compile using mingw-runtime-src ?
class Mingw_runtime (gub.Target_package):
	def set_download (self, mirror=download.gnu, format='gz', download=gub.Target_package.wget):
		gub.Target_package.set_download (self, mirror, format, download)
		self.url = re.sub ('mingw-runtime/', 'mingw/', self.url)
		gub.Target_package.wget (self)
		
	def untar (self):
		self.system ("rm -rf  %(srcdir)s %(builddir)s")
		self.system ('mkdir -p %(srcdir)s/root')
		file = self.settings.downloaddir + '/' + self.file_name ()
		flags = '-zxf'
		cmd = 'tar %(flags)s %(file)s -C %(srcdir)s/root'
		self.system (cmd, locals ())

		self.dump ('%(srcdir)s/configure', '''
cat > Makefile <<EOF
default:
	@echo done
all: default
install:
	mkdir -p %(installdir)s
	tar -C %(srcdir)s/root -cf- . | tar -C %(installdir)s -xvf-
	mkdir -p %(installdir)s/bin
	-cp /cygwin/usr/bin/cygcheck.exe %(installdir)s/bin
EOF
''')
		os.chmod ('%(srcdir)s/configure' % self.package_dict (), 0755)


class Regex (gub.Target_package):
	pass

class Gs (gub.Target_package):
	def untar (self):
		self.system ("rm -rf  %(srcdir)s %(builddir)s")
		self.system ('mkdir -p %(srcdir)s/root')
		tarball = self.settings.downloaddir + '/' + self.file_name ()
		if not os.path.exists (tarball):
			return
		flags = download.untar_flags (tarball)
		cmd = 'tar %(flags)s %(tarball)s -C %(srcdir)s/root'
		self.system (cmd, locals ())
		# FIXME: weird packaging
		self.system ('cd %(srcdir)s && mv root/gs-%(version)s/* .')
		installroot = os.path.dirname (self.installdir ())
		gs_prefix = '/usr/share/gs'
		self.dump ('%(srcdir)s/configure', '''
cat > Makefile <<EOF
default:
	@echo done
all: default
install:
	mkdir -p %(installdir)s
	tar -C %(srcdir)s -cf- bin | tar -C %(installdir)s -xvf-
	mkdir -p %(installroot)s/%(gs_prefix)s
	tar -C %(srcdir)s -cf- fonts lib Resource | tar -C %(installroot)s/%(gs_prefix)s -xvf-
	fc-cache %(installroot)s/%(gs_prefix)s/fonts
	mkdir -p %(installdir)s/share/doc/gs/html
	tar -C %(srcdir)s/doc -cf- --exclude='[A-Z]*[A-Z]' . | tar -C %(installdir)s/share/doc/gs/html -xvf-
	tar -C %(srcdir)s/doc -cf- --exclude='*.htm*' . | tar -C %(installdir)s/share/doc/gs/html -xvf-
EOF
''', env=locals ())
		os.chmod ('%(srcdir)s/configure' % self.package_dict (), 0755)


def get_packages (settings):
	return (
		Mingw_runtime (settings).with (version='3.9', mirror=download.sf),
		Regex (settings).with (version='2.3.90-1', mirror=download.lp, format='bz2'),
		Gs (settings).with (version='8.15-1', mirror=download.lp, format='bz2'),
		)

