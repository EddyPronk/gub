import gup2

def get_cygwin_package (settings, name, dict):
	Package = classobj (name, (gub.Binary_package,), {})
	package = Package (settings)
	package.name_dependencies = []
	package.name_build_dependencies = []
	if dict.has_key ('requires'):
		deps = map (string.strip,
			    re.sub ('\([^\)]*\)', '',
				    dict['requires']).split ())
		cross = [
			'base-passwd', 'bintutils', 
			'gcc', 'gcc-core', 'gcc-g++',
			'gcc-mingw', 'gcc-mingw-core', 'gcc-mingw-g++',
			]
		cycle = ['base-passwd']
		source = [
			'guile-devel',
			'libtool1.5', 'libltdl3',
			'libguile12', 'libguile16',
			 ]
		unneeded = [
			'_update-info-dir',
			'libXft', 'libXft1', 'libXft2',
			'libbz2_1',
			'X-startup-scripts',
			'xorg-x11-bin-lndir',
			]
		blacklist = cross + cycle + source + unneeded
		deps = filter (lambda x: x not in blacklist, deps)
		package.name_dependencies = deps
		package.name_build_dependencies = deps
	package.ball_version = dict['version']
	package.url = (self.mirror + '/'
		       + dict['install'].split ()[0])
	package.format = 'bz2'
	return package

def get_cygwin_packages (package_file):
	dist = 'curr'
	mirror = 'http://gnu.kookel.org/ftp/cygwin'
	
	dists = {'test': [], 'curr': [], 'prev' : []}
	chunks = string.split (open (package_file).read (), '\n\n@ ')
	for i in chunks[1:]:
		lines = string.split (i, '\n')
		name = string.strip (lines[0])
		blacklist = ('binutils', 'gcc', 'guile', 'guile-devel', 'libguile12', 'libguile16', 'libtool', 'litool1.5' , 'libtool-devel', 'libltdl3')
		if name in blacklist:
			continue
		packages = dists['curr']
		records = {
			'sdesc': name,
			'version': '0-0',
			'install': 'urg 0 0',
			}
		j = 1
		while j < len (lines) and string.strip (lines[j]):
			if lines[j][0] == '#':
				j = j + 1
				continue
			elif lines[j][0] == '[':
				packages.append (get_cygwin_package (name, records.copy ()))
				packages = dists[lines[j][1:5]]
				j = j + 1
				continue

			try:
				key, value = map (string.strip,
						  lines[j].split (': ',
								  1))
			except:
				print lines[j], package_file
				raise 'URG'
			if (value.startswith ('"')
			    and value.find ('"', 1) == -1):
				while 1:
					j = j + 1
					value += '\n' + lines[j]
					if lines[j].find ('"') != -1:
						break
			records[key] = value
			j = j + 1
		packages.append (get_package (name, records))

	return dists[dist]


