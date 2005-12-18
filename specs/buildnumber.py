import os
import pickle

BUILD_PICKLE = '/build-number.pickle'
def get_build_db (build_db_name):
	if not os.path.exists (build_db_name):
		pickle.dump({},open (build_db_name,'w'))
		
	db = pickle.load (open (build_db_name)) 
	return db

def get_build_number (pkg):
	db = get_build_db(pkg.settings.topdir + BUILD_PICKLE)
	
	if not db.has_key (pkg.name ()):
		return 1

	bn = db[pkg.name ()]
	
	gubname ='%(gub_uploads)s/%(name)s-%(version)s-%(bn)s.%(target_architecture)s.gub'
	gubname = pkg.expand_string (gubname, locals ())
	
	if os.path.exists (gubname):
		return bn
	else:
		return bn + 1

def write_build_number (pkg):
	db = get_build_db(pkg.settings.topdir + BUILD_PICKLE)
	db[pkg.name ()] = pkg.build ()
	pickle.dump (db, open (build_db_name, 'w'))

