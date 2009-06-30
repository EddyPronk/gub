from gub import tools

class T1utils__tools (tools.AutoBuild):
    source = 'http://www.lcdf.org/type/t1utils-1.34.tar.gz'
    patches = ['t1utils-1.34-glibc-compat.patch']

