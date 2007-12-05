import os
import pickle

from gub import commands

class GupPackage:
    "How to package part of an install_root."

    # This package has its own little expand () function,
    # based on self._dict.
    def __init__ (self, runner):
        self._dict = {}
        self._runner = runner
        self._file_specs = []
        self._dependencies = []
        self._conflicts = []
        
    def set_dict (self, dict, sub_name):
        self._dict = dict.copy ()
        self._dict['sub_name'] = sub_name
        if sub_name:
            sub_name = '-' + sub_name
        s = ('%(name)s' % dict) + sub_name
        self._dict['split_name'] = s
        self._dict['split_ball'] = ('%(packages)s/%(split_name)s%(ball_suffix)s.%(platform)s.gup') % self._dict
        self._dict['split_hdr'] = ('%(packages)s/%(split_name)s%(vc_branch_suffix)s.%(platform)s.hdr') % self._dict
        self._dict['conflicts_string'] = ';'.join (self._conflicts)
        self._dict['dependencies_string'] = ';'.join (self._dependencies)
        self._dict['source_name'] = self.name ()
        if sub_name:
            self._dict['source_name'] = self.name ()[:-len (sub_name)]
        
    def expand (self, s):
        return s % self._dict
    
    def dump_header_file (self):
        hdr = self.expand ('%(split_hdr)s')

        # For easier inspection: dump as sorted list
        as_list = sorted (self._dict.items ())
        self._runner.dump (pickle.dumps (as_list), hdr)
        
    def clean (self):
        base = self.expand ('%(install_root)s')
        for f in self._file_specs:
            if f and f != '/' and f != '.':
                self._runner.system ('rm -rf %(base)s%(f)s ' % locals ())

    def create_tarball (self):
        path = os.path.normpath (self.expand ('%(install_root)s'))
        suffix = self.expand ('%(packaging_suffix_dir)s')
        split_ball = self.expand ('%(split_ball)s')
        self._runner._execute (commands.PackageGlobs (path,
                                                         suffix,
                                                         self._file_specs,
                                                         split_ball))
    def dict (self):
        return self._dict

    def name (self):
        return '%(split_name)s' % self._dict
