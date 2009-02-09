from gub import target

class Libsig_xx_ (target.AutoBuild):
    source = 'http://ftp.gnome.org/pub/GNOME/sources/libsigc++/2.0/libsigc++-2.0.17.tar.gz'

'''libtool: compile:  i686-freebsd4-g++ -DHAVE_CONFIG_H -I/home/janneke/vc/gub/target/freebsd-x86/src/libsig++-2.0.17 -I.. -g -O2 -MT signal.lo -MD -MP -MF .deps/signal.Tpo -c /home/janneke/vc/gub/target/freebsd-x86/src/libsig++-2.0.17/sigc++/signal.cc  -fPIC -DPIC -o .libs/signal.o
In file included from /home/janneke/vc/gub/target/freebsd-x86/src/libsig++-2.0.17/sigc++/signal.cc:20:
/home/janneke/vc/gub/target/freebsd-x86/src/libsig++-2.0.17/sigc++/signal.h:1675: error: declaration of 'typedef struct sigc::slot_list<sigc::slot<T_return, sigc::nil, sigc::nil, sigc::nil, sigc::nil, sigc::nil, sigc::nil, sigc::nil> > sigc::signal0<T_return, T_accumulator>::slot_list'
/home/janneke/vc/gub/target/freebsd-x86/src/libsig++-2.0.17/sigc++/signal.h:168: error: changes meaning of 'slot_list' from 'struct sigc::slot_list<sigc::slot<T_return, sigc::nil, sigc::nil, sigc::nil, sigc::nil, sigc::nil, sigc::nil, sigc::nil> >'
'''
class Libsig_xx___freebsd (Libsig_xx_):
    source = 'http://ftp.acc.umu.se/pub/GNOME/sources/libsigc++/2.2/libsigc++-2.2.3.tar.gz'
