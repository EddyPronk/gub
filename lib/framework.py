# latest vanilla packages
#Zlib (settings).with (version='1.2.3', mirror=download.zlib, format='bz2'),
#Expat (settings).with (version='1.95.8', mirror=download.sf),
#Gettext (settings).with (version='0.14.5'),
#Guile (settings).with (version='1.7.2', mirror=download.alpha, format='gz'),

# FIXME: these lists should be merged, somehow,
# linux and mingw use almost the same list (linux does not have libiconv),
# but some classes have __mingw or __linux overrides.

import gub
import cross

def package_fixups (settings, packs, extra_build_deps):

    ## already  done in Cross.py , set_cross_dependencies () ? 
    return

    for p in packs:
        if p.name () == 'lilypond':
            p._downloader = p.cvs
        if (not isinstance (p, gub.Sdk_package)
            and not isinstance (p, cross.Cross_package)
            and not isinstance (p, gub.Binary_package)):
            pass
        ##p.name_build_dependencies += filter (lambda x: x != p.name (),
        ## extra_build_deps)

