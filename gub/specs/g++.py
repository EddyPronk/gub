from gub import system

class G_xx_ (system.Configure):
    def __init__ (self, settings, source):
        system.Configure.__init__ (self, settings, source)
    def description (self):
        return 'GNU C++ compiler; 4.x is strongly recommended'
