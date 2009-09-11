from gub import tools

class Perl_xml_parser (tools.CpanBuild):
    source = 'http://search.cpan.org/CPAN/authors/id/M/MS/MSERGEANT/XML-Parser-2.36.tar.gz'
    def _get_build_dependencies (self):
        return ['expat']
