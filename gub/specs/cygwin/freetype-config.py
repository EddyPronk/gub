from gub import misc
freetype_config = misc.load_spec ('freetype-config')

class Freetype_config (freetype_config.Freetype_config):
    source = 'url://host/freetype-config-2.3.4.tar.gz'
