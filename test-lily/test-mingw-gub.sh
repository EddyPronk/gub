#!/bin/sh

set -x

cd test
UNINS="/cygdrive/c/Program Files/LilyPond/uninstall.exe"

if test -x "$UNINS"; then
  "$UNINS" /S
  sleep 30s
fi


chmod +x $1
$1 /S

/cygdrive/c/Program\ Files/LilyPond/usr/bin/lilypond.exe --verbose typography-demo.ly

status="$?"


cachefile=`/cygdrive/c/Program\ Files/LilyPond/usr/etc/fonts/local.conf|sed 's!<cache>!!g' | sed 's!</cache>!!g'`

if test ! -s $cachefile ; then
	status="1"
	echo "$cachefile has zero length"
fi 

exit $status


