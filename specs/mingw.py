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

def get_packages (settings):
	return (
		Mingw_runtime (settings).with (version='3.9', mirror=download.sf),
		Regex (settings).with (version='2.3.90-1', mirror=download.lp, format='bz2'),
		)
