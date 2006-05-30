#!/bin/sh

directory="$HOME/$1"
shift
filename="$1"
shift
testfile="$1" 


set -x

cd $directory

UNINS="/cygdrive/c/Program Files/LilyPond/uninstall.exe"

if test -x "$UNINS"; then
  "$UNINS" /S
  sleep 30s
fi


chmod +x $filename
$filename /S

/cygdrive/c/Program\ Files/LilyPond/usr/bin/lilypond.exe --verbose $testfile

status="$?"


cachefile=`cat "/cygdrive/c/Program Files/LilyPond/usr/etc/fonts/local.conf" | grep cache | sed 's!<cache>!!g' | sed 's!</cache>!!g' | sed 's!~!'$HOME'!g' `

if test ! -s "$cachefile" ; then
	status="1"
	echo "$cachefile has zero length"
fi 

exit $status


