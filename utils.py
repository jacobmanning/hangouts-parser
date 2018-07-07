'''
Simple logging helper functions
'''

from __future__ import print_function

class __LoggingParameters:
    pass

__module = __LoggingParameters()
__module.min_log_level = 0
__module.log_levels = {
        'DEBUG': 0,
        'INFO': 1,
        'WARN': 2,
        'ERROR': 3,
    }

def set_log_level(level):
    '''
    Sets the minimum log level that should be output
    '''

    if level in __module.log_levels.values():
        __module.min_log_level = level
    else:
        LOG_ERROR('logging.py: Requested log level unsupported')

def LOG(level, msg):
    '''
    Backbone logging function
    '''

    # Check if level is one of the defaults
    if level in __module.log_levels.keys():
        # Check if the requested log level is greater than or equal to
        # the minimum logging level
        if __module.log_levels[level] >= __module.min_log_level:
            print('[', level, ']: ', msg)
    else:
        # If the level is not a default level, always print it
        print('[', level, ']: ', msg)

def LOG_ERROR(msg):
    LOG('ERROR', msg)

def LOG_WARN(msg):
    LOG('WARN', msg)

def LOG_INFO(msg):
    LOG('INFO', msg)

def LOG_DEBUG(msg):
    LOG('DEBUG', msg)
