#!/bin/sh
set -x
cd ~/test/
bin=`basename $1`
rm -rf LilyPond.app
tar xjf $bin
./LilyPond.app/Contents/Resources/bin/lilypond typography-demo.ly
