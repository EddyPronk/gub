from gub import target

class Unixodbc (target.AutoBuild):
    source = 'http://www.unixodbc.org/unixODBC-2.2.12.tar.gz'
    def configure_commmand (self):
        return (target.AutoBuild.configure_commmand (self)
                + misc.join_lines ('''
--disable-gui
--disable-threads
--disable-readline
--disable-iconv
--disable-stats
--enable-ltdllib
'''))
