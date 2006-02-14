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
  --prefix)
    shift
    prefix="$1"
    if test "$prefix" = "" ; then
      echo 'Option --prefix requires argument.'
      exit 1
    fi
    if not test -d  "$prefix"; then
      mkdir -p "$prefix"
    fi
    prefix=`cd $1 ; pwd`"/"
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
wrapscript="${bindir}lilypond-wrapper"
expandargs='"$@"'
dollar='$'
backquote='`'

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
export PYTHONPATH="${prefix}lilypond/usr/share/lilypond/current/python/:${dollar}PYTHONPATH"
me=${backquote}basename ${dollar}0${backquote}
exec "${lilydir}usr/bin/$interp" ${callmain} "${lilydir}usr/bin/${dollar}me" $expandargs
EOF
  chmod +x "$wrapscript.$interp"
done

################
## symlinks to wrappers

(cd ${prefix}/bin/ ;
 for a in abc2ly musicxml2ly convert-ly midi2ly etf2ly lilypond-book mup2ly ; do
   rm -f $a;
   ln -s $wrapscript.python $a;
 done
 for a in lilypond-invoke-editor ; do
   rm -f $a;
   ln -s $wrapscript.guile $a;
 done
 )

## UGH
##
## need to do
##
##  lilypond-invoke-editor
echo Untarring "$me"
tail -c+%(header_length)012d "$0" | tar -C "$lilydir" -x%(tarflag)sf -

cat <<EOF
To uninstall lilypond, do

    rm -r "$wrapscript" "${prefix}lilypond"


EOF

## need this because binary data starts after this.
exit 0
## END of script
