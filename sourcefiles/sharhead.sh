#!/bin/sh

me="$0"
prefix="$HOME/"
interactive=yes
extract=no

if test `whoami` = "root"; then
  prefix=/usr/local/
fi


while test "$1" != ""; 
do
  case "$1" in
  --help)
      cat <<EOF
$me - install LilyPond tarball
Options 
  --prefix PREFIX     install into PREFIX/lilypond/ (default: $prefix)
  --batch             no interaction
  --tarball           extract tar file for archive
  --help              this help 
EOF
    exit 0
    ;;
  --tarball)
    extract=yes    
    ;;
  --prefix*)
    
    prefix=`echo "$1" | sed 's/.*=//g' | sed 's/--prefix//g'`
    if test "$prefix" = "" ; then
      shift
      prefix="$1"
    fi

    if test "$prefix" = "" ; then
      echo 'Option --prefix requires argument.'
      exit 1
    fi
    if test ! -d  "$prefix"; then
      mkdir -p "$prefix"
    fi
    prefix=`cd $prefix ; pwd`"/"
    ;;
  --batch)
    interactive=no 
    ;;

  *)
    echo Unknown option: $1
    exit 2
    ;;
  esac
  shift 
done


cat<<EOF

LilyPond installer for %(hello)s.
Use --help for help

EOF

if test "$extract" = "yes"; then
  echo "extracting %(base_orig_file)s"
  tail -c+%(header_length)012d $0 > %(base_orig_file)s
  exit 0
fi


if test "$interactive" = "yes" ; then
  cat <<EOF

You're about to install lilypond in ${prefix}lilypond/ 
A script in ${prefix}bin/ will be created as a shortcut. 

Press ^C to abort, or Enter to proceed 
EOF
  read junk
fi


lilydir="${prefix}lilypond/"
bindir="${prefix}bin/"
binwrapscript="${bindir}lilypond"
uninstall_script=${bindir}uninstall-lilypond

wrapscript="${bindir}lilypond-wrapper"
expandargs='"$@"'
dollar='$'
backquote='`'

if test -d  "$lilydir"; then
  echo "Directory $lilydir already exists. "
  echo "Remove old lilypond installations before installing this one."
  if test -x "$uninstall_script"; then 
    echo "Run $uninstall_script to uninstall previous version"   
  fi
  exit 1
fi

for d in "${lilydir}" "${bindir}"; do
  if test ! -d  "$d"; then
    echo Making "$d" 
    mkdir -p "$d"
  fi
done

################
## Wrappers


echo Creating script $binwrapscript


## LD_LIBRARY_PATH is necessary for ao. FreeBSD.
rm -f "$binwrapscript" > /dev/null 2>&1
cat<<EOF > "$binwrapscript"
#!/bin/sh
me=${backquote}basename ${dollar}0${backquote}
export LD_LIBRARY_PATH="${lilydir}usr/lib/"
exec "$prefix/lilypond/usr/bin/${dollar}me" $expandargs
EOF
chmod +x "$binwrapscript"

for interp in python guile ; do
  echo "Creating script $wrapscript.$interp"

  if test "$interp" = "guile"; then
    callmain="-e main"
  else
    callmain=""
  fi
  
  rm -f "$wrapscript.$interp" > /dev/null 2>&1
  cat<<EOF > "$wrapscript.$interp"
#!/bin/sh
export PYTHONPATH="${prefix}lilypond/usr/lib/lilypond/current/python/:${prefix}lilypond/usr/share/lilypond/current/python/:${dollar}PYTHONPATH"
export GUILE_LOAD_PATH="${prefix}lilypond/usr/share/lilypond/current/"
export LD_LIBRARY_PATH="${lilydir}usr/lib/:${dollar}LD_LIBRARY_PATH"
me=${backquote}basename ${dollar}0${backquote}
exec "${lilydir}usr/bin/$interp" ${callmain} "${lilydir}usr/bin/${dollar}me" $expandargs
EOF
  chmod +x "$wrapscript.$interp"
done

################
## symlinks to wrappers

(cd ${bindir} ;
 for a in abc2ly musicxml2ly convert-ly midi2ly etf2ly lilypond-book mup2ly ; do
   rm -f $a;
   ln -s $wrapscript.python $a;
 done
 for a in lilypond-invoke-editor ; do
   rm -f $a;
   ln -s $wrapscript.guile $a;
 done
 )


################
## uninstall script

echo Creating script $uninstall_script
cat <<EOF > $uninstall_script
#!/bin/sh

quiet=no
while test "${dollar}1" != ""; 
do
  case "${dollar}1" in
  --help)
    cat <<BLA
options
  --help    this screen
  --quiet   do not ask for confirmation
BLA
   exit 0
   ;;
  --quiet)
    quiet=yes
    ;;
  esac
  shift
done
if test "${dollar}quiet" = "no" ; then
  echo "About to remove a lilypond installation from ${prefix}lilypond"
  echo "Press ^C to abort"
  read junk
fi

for binary in abc2ly musicxml2ly convert-ly midi2ly etf2ly lilypond-book mup2ly lilypond-invoke-editor lilypond  ; do
  rm ${bindir}/${dollar}binary
done
rm $wrapscript.guile  $wrapscript.python
rm -rf ${prefix}lilypond
rm $uninstall_script
EOF
chmod +x $uninstall_script


## UGH
##
## need to do
##
##  lilypond-invoke-editor
echo Untarring "$me"
tail -c+%(header_length)012d "$0" | tar -C "$lilydir" -x%(tarflag)sf -

cat <<EOF
To uninstall lilypond, run 

    ${prefix}/bin/uninstall-lilypond

EOF

## need this because binary data starts after this.
exit 0
## END of script
