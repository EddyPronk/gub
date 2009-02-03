#! /bin/sh

# FIXME: copy from lilypond-sharhead, lilypond stuff commented-out

me="$0"
root="$HOME"
doc=no
extract=no
interactive=yes

if test `id -u` = "0"; then
    root=/usr/local
fi

while test -n "$1";
do
    case "$1" in
	--help)
	    cat <<EOF
$me - install %(pretty_name)s tarball
Options
  --batch             no interaction
  --doc               [attempt to] download and install documentation
  --prefix PREFIX     install into PREFIX/%(name)s (default: ${root})
  --help              this help
  --tarball           extract tar file for archive
EOF
	    exit 0
	    ;;
	--tarball)
	    extract=yes
	    ;;
	--prefix*)
	    root=`echo "$1" | sed -e 's/.*=//g' -e 's/--prefix//g'`
	    if test -z "${root}"; then
		shift
		root="$1"
	    fi
	    if test -z "${root}"; then
		echo 'Option --prefix requires argument.'
		exit 1
	    fi
	    if test ! -d "${root}"; then
		mkdir -p "${root}"
	    fi
	    root=`cd ${root}; pwd`
	    ;;
	--batch)
	    interactive=no
	    ;;
	--doc*)
	    doc=yes
	    ;;
	*)
	    echo Unknown option: $1
	    exit 2
	    ;;
    esac
    shift
done


cat <<EOF

%(name)s installer for version %(version)s release %(release)s.
Use --help for help

EOF

if test "$extract" = "yes"; then
    echo "extracting %(base_file)s"
    tail -c+%(header_length)012d $0 > %(base_file)s
    exit 0
fi

if test "$interactive" = "yes"; then
    cat <<EOF

You are about to install %(pretty_name)s in ${root}/%(name)s
A script in ${root}/bin will be created as a shortcut.

Press ^C to abort, or Enter to proceed.
EOF
    read junk
fi


prefix="${root}/%(name)s"
bindir="${root}/bin"
binwrapscript="${bindir}/%(name)s"
uninstall_script="${bindir}/uninstall-%(name)s"
expandargs='"$@"'
dollar='$'
backquote='`'
binaries=%(name)s
EOF=EOF

if test -d "${prefix}"; then
    echo "Directory ${prefix} already exists."
    echo "Remove old %(name)s installations before installing this one."
    if test -x "$uninstall_script"; then
	echo "Run $uninstall_script to uninstall previous version."
    fi
    exit 1
fi

for d in "${prefix}" "${bindir}"; do
    if test ! -d "$d"; then
	echo Making "$d"
	mkdir -p "$d"
    fi
done


################
## Wrappers

echo Creating script $binwrapscript

## LD_LIBRARY_PATH is necessary for ao. FreeBSD.
rm -f "$binwrapscript" > /dev/null 2>&1
##lily##cat <<EOF > "$binwrapscript"
##lily###! /bin/sh
##lily##INSTALLER_PREFIX=${dollar}{prefix}/usr
##lily##me=${backquote}basename ${dollar}0${backquote}
##lily##export LD_LIBRARY_PATH="${dollar}{INSTALLER_PREFIX}/lib"
##lily##exec "${dollar}{INSTALLER_PREFIX}/bin/${dollar}me" $expandargs
##lily##EOF

cat <<EOF > "$binwrapscript"
#! /bin/sh
# relocate script for [gtk+ programs like] inkscape

INSTALLER_PREFIX=${prefix}/usr
ENV=${dollar}HOME/.inkscape.env

cat > ${dollar}ENV <<${dollar}EOF
INSTALLER_PREFIX=${prefix}/usr
if test -d ${dollar}INSTALLER_PREFIX/lib/gtk-2.0/2.10.0/loaders; then
    export GDK_PIXBUF_MODULEDIR=${dollar}INSTALLER_PREFIX/lib/gtk-2.0/2.10.0/loaders
    export GDK_PIXBUF_MODULE_FILE=${dollar}INSTALLER_PREFIX/etc/gtk-2.0/gdk-pixbuf.loaders
fi
export LD_LIBRARY_PATH="${dollar}{INSTALLER_PREFIX}/lib"
${dollar}EOF

for file in ${dollar}INSTALLER_PREFIX/etc/relocate/*.reloc; do
    sed -e 's/^set\(\|file\|dir\) /export /' ${dollar}file \\
	| while read line; do
	echo ${dollar}line >> ${dollar}ENV
    done
done

. ${dollar}ENV

if test -d "${dollar}GDK_PIXBUF_MODULEDIR" -a ! -f "${dollar}GDK_PIXBUF_MODULE_FILE"; then
    ${dollar}INSTALLER_PREFIX/bin/gdk-pixbuf-query-loaders > ${dollar}GDK_PIXBUF_MODULE_FILE
fi

me=${backquote}basename ${dollar}0${backquote}
exec "${dollar}{INSTALLER_PREFIX}/bin/${dollar}me" $expandargs
EOF

chmod +x "$binwrapscript"


#####################
### LilyPond wrappers

##lily##wrapscript="${bindir}/%(name)s-wrapper"

##lily##for interp in python guile; do
##lily##    echo "Creating script $wrapscript.$interp"
##lily##
##lily##    if test "$interp" = "guile"; then
##lily##	callmain="-e main"
##lily##    else
##lily##	callmain=""
##lily##    fi
##lily##
##lily##    rm -f "$wrapscript.$interp" > /dev/null 2>&1
##lily##    cat <<EOF > "$wrapscript.$interp"
##lily###!/bin/sh
##lily##export PYTHONPATH="${prefix}/usr/lib/lilypond/current/python:${prefix}/usr/share/lilypond/current/python:${dollar}PYTHONPATH"
##lily##export GUILE_LOAD_PATH="${prefix}/usr/share/lilypond/current"
##lily##export LD_LIBRARY_PATH="${prefix}/usr/lib:${dollar}LD_LIBRARY_PATH"
##lily##me=${backquote}basename ${dollar}0${backquote}
##lily##exec "${prefix}/usr/bin/$interp" ${callmain} "${prefix}/usr/bin/${dollar}me" $expandargs
##lily##EOF
##lily##    chmod +x "$wrapscript.$interp"
##lily##done
##lily##
#######################
## symlinks to wrappers

##lily##(cd ${bindir};
##lily##    for a in abc2ly musicxml2ly convert-ly midi2ly etf2ly lilypond-book mup2ly; do
##lily##	rm -f $a;
##lily##	ln -s $wrapscript.python $a;
##lily##	binaries="$binaries $a"
##lily##    done
##lily##    for a in lilypond-invoke-editor; do
##lily##	rm -f $a;
##lily##	ln -s $wrapscript.guile $a;
##lily##	binaries="$binaries $a"
##lily##    done
##lily##)

###################
## uninstall script

echo Creating script $uninstall_script
cat <<EOF > $uninstall_script
#! /bin/sh

quiet=no
while test -n "${dollar}1";
do
    case "${dollar}1" in
	--help)
	    cat <<BLA
options
  --help    this help
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
if test "${dollar}quiet" = "no"; then
    echo "About to remove a %(name)s installation from ${prefix}"
    echo "Press ^C to abort, Enter to proceed"
    read junk
fi

for binary in ${binaries}; do
    rm ${bindir}/${dollar}binary
done
rm -f $wrapscript.guile $wrapscript.python
rm -rf ${prefix}
rm $uninstall_script
EOF
chmod +x $uninstall_script

echo Untarring "$me"
tail -c+%(header_length)012d "$0" | tar -C "${prefix}" %(_z)s -xf -

documentation="http://%(name)s.org/doc"

##lily##mirror="http://lilypond.org/download"
##lily##doc_url_base="$mirror/binaries/documentation"
##lily##if test "$doc" = yes; then
##lily##    documentation="file://${prefix}/usr/share/doc/lilypond/html/index.html
##lily##    file://${prefix}/usr/share/info/dir"
##lily##    docball=`echo $me | sed -e 's/[.][^.]\+[.]sh/.documentation.tar.bz2/'`
##lily##    doc_url="$doc_url_base/$docball"
##lily##    if ! test -e $docball; then
##lily##	echo "No ./$docball found, downloading."
##lily##	wget $doc_url
##lily##    fi
##lily##    if test -e $docball; then
##lily##	echo Untarring "$docball"
##lily##	tar -C ${prefix}/usr -xjf $docball
##lily##    fi
##lily##fi

cat <<EOF
To uninstall %(name)s, run

    ${root}/bin/uninstall-%(name)s

For license and warranty information, consult

    ${prefix}/license/README

Full documentation can be found at

    $documentation

EOF

## need this because binary data starts after this.
exit 0
## END of script
