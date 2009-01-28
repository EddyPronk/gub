import time
import sys
import os
#
from gub import misc

'''
TODO: if we need more granularity, it's better to look at the stack
trace during a log call (), and have per .py file settings.
'''

default_logger = None
default_logger_interface = None

name_to_loglevel_mapping = {'quiet': 0,
         'error': 0,
         'stage': 0,
         'info': 1,
         'harmless': 2,
         'verbose': 2,
         'warning': 1,
         'command': 3,
         'action': 2,
         'output': 4,
         'debug': 5}

def now ():
    return time.asctime (time.localtime ())


class AbstractCommandLogger:
    """A logger takes care of the mechanics of storing and/or showing
    messages when approppriate.
    """
    def __init__ (self):
        pass
    def verbose_flag (self):
        return ''
    def read_tail (self):
        return 'tail'
    def write_log (self, message, message_level):
        pass
    def log_env (self, env):
        pass
    def write_multilevel_message (self, message_types):
        pass
    
class NullCommandLogger (AbstractCommandLogger):
    pass

class CommandLogger (AbstractCommandLogger):
    def __init__ (self, log_file_name, threshold):

        # only print message under THRESHOLD.
        self.threshold = threshold
        self.log_file = None
        self.log_file_name = log_file_name
        self.relative_log_name = log_file_name

        if log_file_name:
            self.relative_log_name = log_file_name.replace (os.getcwd () + '/', '')
            if default_logger_interface:
                log_name = self.relative_log_name
                default_logger_interface.info ('Log file: %(log_name)s\n' % locals ())
            
            directory = os.path.split (log_file_name)[0]
            if not os.path.isdir (directory):
                os.makedirs (directory)
            self.log_file = open (self.log_file_name, 'a')
        self.start_marker = ' * Starting build: %s\n' %  now ()
        self.write_log_file ('\n\n' + self.start_marker)

    # ugh: the following should not be in the base class.
    def read_tail (self, size=10240, lines=100):
        if self.log_file:
            return misc.read_tail (self.log_file_name, size, lines,
                                   self.start_marker)
        else:
            return '(no log)'

    def dump_tail (self, output):
        tail = '\n'.join (self.read_tail ())
        log_name = self.relative_log_name
        output.write ('Tail of %(log_name)s >>>>>>>>\n%(tail)s\n<<<<<<<< Tail of %(log_name)s\n' % locals ())

    def write_multilevel_message (self, message_types):
        """Given a set of messages display the one fitting with our
        log level."""
        leveled = [(name_to_loglevel_mapping[type], message)
                   for (message, type) in message_types]
        leveled.sort ()
        leveled.reverse ()
        self.write_log_file (leveled[0][1])

        leveled = [msg for (l, msg) in leveled
                   if l <= self.threshold]
        if leveled:
            sys.stderr.write (leveled[0])
            
    def write_log_file (self, message):
        if self.log_file:
            self.log_file.write (message)
            self.log_file.flush ()

    def write_log (self, message, message_type):
        assert type (message_type) == str
        if not message:
            return 0
        message_level = name_to_loglevel_mapping[message_type]
        if message_level <= self.threshold:
            sys.stderr.write (message)

        self.write_log_file (message)

    def verbose_flag (self):
        if self.threshold >= name_to_loglevel_mapping['output']:
            return ' -v'
        return ''

    def log_env (self, env):
        if self.threshold >= name_to_loglevel_mapping['debug']:
            keys = list (env.keys ())
            keys.sort ()
            for k in keys:
                self.write_log ('%s=%s\n' % (k, env[k]), 'debug')
            self.write_log ('export %s\n' % ' '.join (keys), 'debug')

    def show_logfile (self):
        if self.log_file_name:
            sys.stdout.write ('Logfile: %s\n' % self.log_file_name)


class LoggerInterface:
    """LoggerInterface provides syntacic sugar for different types of messages."""
    
    def __init__ (self, logger):
        self.logger = logger
        
    # fixme: repetitive code.
    def action (self, str):
        self.logger.write_log (str, 'action')

    def stage (self, str):
        self.logger.write_log (str, 'stage')

    def error (self, str):
        self.logger.write_log (str, 'error')

    def info (self, str):
        self.logger.write_log (str, 'info')

    def command (self, str):
        self.logger.write_log (str, 'command')

    def debug (self, str):
        self.logger.write_log (str, 'debug')

    def warning (self, str):
        self.logger.write_log (str, 'warning')

    def harmless (self, str):
        self.logger.write_log (str, 'harmless')

    def verbose (self, str):
        self.logger.write_log (str, 'verbose')

    def output (self, str):
        self.logger.write_log (str, 'output')

    def verbose_flag (self):
        return self.logger.verbose_flag ()
    # end fixme

def get_numeric_loglevel (name):
    return name_to_loglevel_mapping[name]

default_logger = None
default_logger_interface = None
action = None
command = None
debug = None
error = None
harmless = None
info = None
stage = None
verbose = None
warning = None

def set_default_log (name, level):
    global default_logger, default_logger_interface
    global action, command, debug, error, harmless, info, stage, verbose, warning
    default_logger = CommandLogger (name, level)
    default_logger_interface = LoggerInterface (default_logger)
    action = default_logger_interface.action
    command = default_logger_interface.command
    debug = default_logger_interface.debug
    error = default_logger_interface.error
    harmless = default_logger_interface.harmless
    info = default_logger_interface.info
    stage = default_logger_interface.stage
    verbose = default_logger_interface.verbose
    warning = default_logger_interface.warning
    return default_logger

# ugh, makeme optional?
set_default_log ('', 0)
