from gub import target

class Test (target.AutoBuild):
    source = 'url://host/test-23-1.0.tar.gz'
    def untar (self):
        pass
    dependencies = [
        'system::mf',
        'system::mpost',
        ]
