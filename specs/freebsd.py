import os
import re

import download
import framework
import gub
import mingw

class Binutils (framework.Binutils):
	pass

class Gcc (mingw.Gcc):
	pass

def get_packages (settings):
	return (
		Binutils (settings).with (version='2.16.1', format='bz2'),
#		Gcc (settings).with (version='4.0.2', mirror=download.gcc, format='bz2'),
		Gcc (settings).with (version='3.4.5', mirror=download.gcc, format='bz2',
				     depends=['binutils']
				     ),
		)

def change_target_packages (packages):
	pass
