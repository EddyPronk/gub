#!/bin/sh

directory="$HOME/$1"
shift
filename="$1"
shift
testfile="$1"

set -x
if test ! -d $directory; then
  mkdir -p $directory
  if test "$?" != "0"; then
    exit 1;
  fi
fi
cd $directory

rm -rf LilyPond.app
tar xjf $filename
./LilyPond.app/Contents/Resources/bin/lilypond $testfile
