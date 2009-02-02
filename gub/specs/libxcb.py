from gub import target

class Libxcb (target.AutoBuild):
    source = 'http://xcb.freedesktop.org/dist/libxcb-0.9.93.tar.gz'
    #1.1.92 removes libxcb-xlib, which libx11-1.1.15 needs?
    #source = 'http://xcb.freedesktop.org/dist/libxcb-1.1.93.tar.gz'
    '''
xproto.c:3056: error: conflicting types for 'xcb_get_atom_name_name'
/home/janneke/vc/gub/target/linux-64/src/libxcb-1.1.93/src/xproto.h:6867: error: previous declaration of 'xcb_get_atom_name_name' was here
'''
    #source = 'http://xcb.freedesktop.org/dist/libxcb-1.1.91.tar.gz'
    '''
xproto.c: In function 'xcb_configure_window_checked':
xproto.c:2479: error: 'xcb_configure_window_request_t' has no member named 'pad1'
'''
    patches = ['libxcb-1.1.93.patch']
    def get_build_dependencies (self):
        return ['tools::libtool', 'libpthread-stubs-devel', 'libxau-devel', 'xcb-proto-devel']
