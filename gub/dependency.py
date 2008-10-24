import new
import os

from gub import cross
from gub import logging
from gub import misc
from gub import repository
from gub import targetbuild
from gub import toolsbuild

def get_build_from_file (platform, file_name, name):
    gub_name = file_name.replace (os.getcwd () + '/', '')
    logging.info ('reading spec: %(gub_name)s\n' % locals ())
    module = misc.load_module (file_name, name)
    # cross/gcc.py:Gcc will be called: cross/Gcc.py,
    # to distinguish from specs/gcc.py:Gcc.py
    base = os.path.basename (name)
    class_name = ((base[0].upper () + base[1:])
                  .replace ('-', '_')
                  .replace ('++', '_xx_')
                  .replace ('+', '_x_')
                  + ('-' + platform).replace ('-', '__'))
    logging.debug ('LOOKING FOR: %(class_name)s\n' % locals ())
    return misc.most_significant_in_dict (module.__dict__, class_name, '__')

def get_build_class (settings, flavour, name):
    cls = get_build_from_module (settings, name)
    if not cls:
        logging.harmless ('making spec:  %(name)s\n' % locals ())
        cls = get_build_without_module (flavour, name)
    return cls

def get_build_from_module (settings, name):
    file = get_build_module (settings, name)
    if file:
        return get_build_from_file (settings.platform, file, name)
    return None

def get_build_module (settings, name):
    file_base = name + '.py'
    for dir in (os.path.join (settings.specdir, settings.platform),
                os.path.join (settings.specdir, settings.os),
                settings.specdir):
        file_name = os.path.join (dir, file_base)
        if os.path.exists (file_name):
            return file_name
    return None

def get_build_without_module (flavour, name):
    '''Direct dependency build feature

    * gub http://ftp.gnu.org/pub/gnu/tar/tar-1.18.tar.gz
    WIP:
    * gub git://git.kernel.org/pub/scm/git/git
    * bzr:http://bazaar.launchpad.net/~yaffut/yaffut/yaffut.bzr
    * must remove specs/git.py for now to get this to work
    * git.py overrides repository and branch settings'''
    
    cls = new.classobj (name, (flavour,), {})
    cls.__module__ = name
    return cls

class Dependency:
    def __init__ (self, settings, name, url=None):

        # FIXME: document what is accepted here, and what not.
        
        self.settings = settings
        self._name = name

        if misc.is_ball (name):
            # huh ? name_from_url vs. name_from_ball?
            self._name = misc.name_from_url (name)
            
        self._cls = self._flavour = None
        self._url = url

    def _create_build (self):
        dir = os.path.join (self.settings.downloads, self.name ())
        branch = self.settings.__dict__.get ('%(_name)s_branch' % self.__dict__,
                                             self.build_class ().branch)
        source = self.url ()
        if not isinstance (source, repository.Repository):
            source = repository.get_repository_proxy (dir, source, branch, '')
        return self.build_class () (self.settings, source)

    def build_class (self):
        if not self._cls:
            self._cls = get_build_class (self.settings, self.flavour (),
                                         self.name ())
        return self._cls

    def flavour (self):
        if not self._flavour:
            self._flavour = targetbuild.TargetBuild
            if self.settings.platform == 'tools':
                self._flavour = toolsbuild.ToolsBuild
        return self._flavour
    
    def url (self):
        if not self._url:
            self._url = self.build_class ().source
        if not self._url:
            logging.warning ('no source specified in class:' + self.build_class ().__name__ + '\n')
        if not self._url:
            self._url = self.settings.dependency_url (self.name ())
        if not self._url:
            raise 'No URL for:' + self._name
        if type (self._url) == str:
            try:
                self._url = self._url % self.settings.__dict__
            except Exception, e:
                print 'URL:', self._url
                raise e
            x, parameters = misc.dissect_url (self._url)
            if parameters.get ('patch'):
                self._cls.patches = parameters['patch']
        return self._url
    def name (self):
        return self._name
    def build (self):
        b = self._create_build ()
        if not self.settings.platform == 'tools':
            cross.get_cross_module (self.settings).change_target_package (b)
        return b
