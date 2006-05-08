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

if test -x bin/uninstall-lilypond; then
  bin/uninstall-lilypond --quiet
  if test "$?" != "0"; then
    exit 1;
  fi  
fi

sh $filename --batch --prefix `pwd`
if test "$?" != "0"; then
    exit 1;
fi  

bin/lilypond $testfile


