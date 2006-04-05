#!/bin/sh
set -x
mkdir -p $HOME/test-gub/ \
 && cd $HOME/test-gub \
 && rm -rf bin/ lilypond \
 && ash $1 --batch --prefix `pwd` \
 && bin/lilypond /tmp/typography-demo.ly


