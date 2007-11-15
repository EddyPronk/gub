#!/usr/bin/python

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

import fnmatch
import os
import re
import stat
import subprocess
import sys
import time
import traceback
import inspect

from gub import misc
from gub import commands
from gub import logging

class CommandRunner:
    '''Encapsulate OS/File system commands

    This enables proper logging and deferring and checksumming of commands.'''

    def __init__ (self, logger):
        self.logger = logger
        self.fakeroot_cmd = False

    def _execute (self, command):
        return command.execute (self)

    # fixme: should be moved somewhere else.
    def fakeroot (self, s):
        self.fakeroot_cmd = s

    def verbose_flag (self):
        return ''

    def system_one (self, cmd, env, ignore_errors):
        '''Run CMD with environment vars ENV.'''

        # YUK
        if self.fakeroot_cmd:
            cmd = re.sub ('''(^ *|['"();|& ]*)(fakeroot) ''',
                          '\\1%(fakeroot_cmd)s' % self.__dict__, cmd)
            cmd = re.sub ('''(^ *|['"();|& ]*)(chown|rm|tar) ''',
                          '\\1%(fakeroot_cmd)s\\2 ' % self.__dict__, cmd)
        # '
        return self._execute (commands.System (cmd, env=env,
                                               ignore_errors=ignore_errors))

    def log (self, str, logtype):
        return self._execute (commands.Message (str, logtype))

    # fixme: repetitive code.
    def action (self, str):
        self.log (str, 'action')

    def stage (self, str):
        self.log (str, 'stage')

    def error (self, str):
        self.log (str, 'error')

    def info (self, str):
        self.log (str, 'info')

    def command (self, str):
        self.log (str, 'command')

    def debug (self, str):
        self.log (str, 'debug')

    def warning (self, str):
        self.log (str, 'warning')

    def harmless (self, str):
        self.log (str, 'harmless')
    # end fixme

    def system (self, cmd, env={}, ignore_errors=False):
        '''Run os commands, and run multiple lines as multiple commands.'''
        call_env = os.environ.copy ()
        call_env.update (env)

        self.logger.log_env (env)
        for i in cmd.split ('\n'):
            if i:
                self.system_one (i, call_env, ignore_errors)

    def dump (self, *args, **kwargs):
        return self._execute (commands.Dump (*args, **kwargs))

    def file_sub (self, *args, **kwargs):
        return self._execute (commands.Substitute (*args, **kwargs))

    def shadow_tree (self, src, target):
        return self._execute (commands.ShadowTree (src, target))

    def map_locate (self, func, directory, pattern):
        return self._execute (commands.MapLocate (func, directory, pattern))

    def copy (self, src, dest):
        return self._execute (commands.Copy (src, dest))

    def func (self, f, *args):
        return self._execute (commands.Func (f, *args))

    def chmod (self, file, mode):
        return self._execute (commands.Chmod (file, mode))
    
    def first_is_newer (self, first, second):
        return misc.first_is_newer (first, second)

    def pred_if_else (self, predicate, true, false=None):
        return self._execute (commands.Conditional (predicate, true, false))

class DeferredRunner (CommandRunner):
    def __init__ (self, *args):
        CommandRunner.__init__ (self, *args)
        self._deferred_commands = list ()

    def execute_deferred_commands (self):
        commands = self._deferred_commands
        self._deferred_commands = []
        for cmd in commands:
            cmd.execute(self.logger)

        print self._deferred_commands
        assert self._deferred_commands == list ()

    def flush_deferred_commands (self):
        self._deferred_commands = list ()
        
    def checksum (self):
        # we use a visitor pattern, to shield SerializedCommand from
        # the actual type of the checksum (md5 hasher, list, etc.); If
        # we use return values, composite SerializedCommand
        # (eg. Conditional) have to be aware of the type to combine
        # results for their children.

        result = []
        map (lambda x: x.checksum (result.append), self._deferred_commands)
        return '\n'.join (result)

    def _execute (self, command):
        self._deferred_commands.append (command)

    
