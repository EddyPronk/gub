"""
    Copyright (c) 2005--2007
    Jan Nieuwenhuizen <janneke@gnu.org>
    Han-Wen Nienhuys <hanwen@xs4all.nl>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2, or (at your option)
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""

import difflib
import pickle
import os
import sys
#
from gub import cross
from gub import build
from gub import misc
from gub import gup
from gub import logging
from gub import runner

def checksum_diff (a, b):
    return '\n'.join(difflib.context_diff (a.split ('\n'),
                                           b.split ('\n')))

# FIXME s/spec/build/, but we also have two definitions of package/pkg
# here: sub packages and name of global package under build

#FIXME: split spec_* into SpecBuiler?
class BuildRunner:
    def __init__ (self, manager, settings, specs):
        self.manager = manager
        self.settings = settings
        self.specs = specs

        # spec name -> string
        self.checksums = {}

        PATH = os.environ['PATH']
        ## cross_prefix is also necessary for building cross packages, such as GCC
        os.environ['PATH'] = self.settings.expand ('%(cross_prefix)s/bin:' + PATH,
                                                   locals ())

        ## UGH -> double work, see cross.change_target_packages () ?
        sdk_pkgs = [p for p in self.specs.values ()
                    if isinstance (p, build.SdkBuild)]
        cross_pkgs = [p for p in self.specs.values ()
                      if isinstance (p, cross.CrossToolsBuild)]

        extra_build_deps = [p.name () for p in sdk_pkgs + cross_pkgs]
        gup.add_packages_to_manager (self.manager, self.settings, self.specs)

    def calculate_checksums (self):
        logging.stage ('calculating checksums\n')
        for (name, spec) in self.specs.items ():
            logger = logging.NullCommandLogger ()

            command_runner = runner.DeferredRunner (logger)
            spec.connect_command_runner (command_runner)
            spec.build ()
            spec.connect_command_runner (None)

            self.checksums[name] = command_runner.checksum ()
 
    # FIXME: move to gup.py or to build.py?
    def spec_checksums_fail_reason (self, spec):
        # need to read package header to read checksum_file.  since
        # checksum is per buildspec, only need to inspect one package.
        pkg = spec.get_packages ()[0]    
        name = pkg.name ()
        pkg_dict = self.manager.package_dict (name)

        try:
            build_checksum_ondisk = open (pkg_dict['checksum_file']).read ()
        except IOError:
            build_checksum_ondisk = '0000'

	# fixme: spec.build_checksum () should be method.
        reason = ''
        if spec.source_checksum () != pkg_dict['source_checksum']:
            reason = 'source %s -> %s (memory)' % (spec.source_checksum (), pkg_dict['source_checksum'])

        if reason == '' and self.checksums[spec.name ()] != build_checksum_ondisk:
            reason = 'build diff %s' % checksum_diff(self.checksums[spec.name ()], build_checksum_ondisk)

        hdr = pkg.expand ('%(split_hdr)s')
        if reason == '' and not os.path.exists (hdr):
            reason = 'hdr missing'
            
        if reason == '':
            hdr_dict = dict(pickle.load (open (hdr)))
            if spec.source_checksum () != hdr_dict['source_checksum']:
                reason = 'source %s -> %s (disk)' % (spec.source_checksum (), hdr_dict['source_checksum'])

        # we don't use cross package checksums, otherwise we have to
        # rebuild everything for every cross package change.
        return reason

    # FIXME: this should be in gpkg/gup.py otherwise it's impossible
    # to install packages in a conflict situation manually
    def spec_conflict_resolution (self, spec, pkg):
        pkg_name = pkg.name ()
        install_candidate = pkg
        subname = ''
        if spec.name () != pkg_name:
            subname = pkg_name.split ('-')[-1]
        if spec.get_conflict_dict ().has_key (subname):
            for c in spec.get_conflict_dict ()[subname]:
                if self.manager.is_installed (c):
                    print '%(c)s conflicts with %(pkg_name)s' % locals ()
                    conflict_source = self.manager.source_name (c)
                    # FIXME: implicit provides: foo-* provides foo-core,
                    # should implement explicit provides
                    if conflict_source + '-core' == pkg_name:
                        print ('  non-core %(conflict_source)s already installed'
                               % locals ())
                        print ('    skipping request to install %(pkg_name)s'
                               % locals ())
                        install_candidate = None
                        continue
                    self.manager.uninstall_package (c)
        return install_candidate

    def pkg_install (self, spec, pkg):
        if not self.manager.is_installed (pkg.name ()):
            install_candidate = self.spec_conflict_resolution (spec, pkg)
            if install_candidate:
                self.manager.unregister_package_dict (install_candidate.name ())
                self.manager.register_package_dict (install_candidate.dict ())
                self.manager.install_package (install_candidate.name ())

    def spec_install (self, spec):
        for pkg in spec.get_packages ():
            self.pkg_install (spec, pkg)

    def spec_build (self, specname):
        spec = self.specs[specname]
        
        all_installed = True
        for p in spec.get_packages ():
            all_installed = (all_installed
                             and self.manager.is_installed (p.name ()))
        if all_installed:
            return

        # ugh, dupe
        checksum_fail_reason = self.spec_checksums_fail_reason (spec)
            
        is_installable = misc.forall (self.manager.is_installable (p.name ())
                                      for p in spec.get_packages ())

        logger = logging.default_logger

        if (not is_installable or checksum_fail_reason):

            logger.write_log (checksum_fail_reason, 'info')

            deferred_runner = runner.DeferredRunner (logger)
            spec.connect_command_runner (deferred_runner)
            spec.runner.stage ('building package: %s\n' % specname)
            spec.build ()
            spec.connect_command_runner (None)
            
            deferred_runner.execute_deferred_commands ()

            file (spec.expand ('%(checksum_file)s'), 'w').write (self.checksums[specname])

        logger.write_log (' *** Stage: %s (%s, %s)\n'
                           % ('pkg_install', spec.name (),
                              self.settings.platform), 'stage')
        self.spec_install (spec)

    def uninstall_outdated_spec (self, spec_name):
	spec = self.specs[spec_name]
	# ugh, dupe
	checksum_ok = '' == self.spec_checksums_fail_reason (self.specs[spec_name])
	for pkg in spec.get_packages ():
	    if (self.manager.is_installed (pkg.name ())
		and (not self.manager.is_installable (pkg.name ())
		     or not checksum_ok)):
		self.manager.uninstall_package (pkg.name ())

    def uninstall_outdated_specs (self, deps):
        for spec_name in reversed (deps):
            self.uninstall_outdated_spec (spec_name)

    def build_source_packages (self, names):
        deps = filter (self.specs.has_key, names)

        self.uninstall_outdated_specs (deps)
        for spec_name in deps:
            self.spec_build (spec_name)

def main ():
    boe

if __name__ == '__main__':
    main ()
