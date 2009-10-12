#! /bin/sh
# gub.sh -- handy shorthand to call plain 'gub'
#           put a copy of this in ~/bin/gub and link to ~/bin/gpkg
#
# Corresponding local.make snippet [to avoid rebuilding everything
# due to PATH differences when using old makefile driver:
#
# ifneq ($(findstring xbin:,x$(PATH)),xbin:)
# PATH := bin:$(HOME)/vc/gub/bin:$(PATH)
# endif
#
PATH=bin:~/vc/gub/bin:$PATH $(basename $0) "$@"
