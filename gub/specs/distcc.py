from gub import tools

#ugh, use icecc/icecream, *much* less hassle
class Distcc (tools.AutoBuild):
    patches = ['distcc-substitute.patch']
