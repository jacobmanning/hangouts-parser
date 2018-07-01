'''
Simple logging helper functions
'''

_UTILS_MIN_LOG_LEVEL_PRIVATE = 0
_UTILS_LOG_LEVELS_PRIVATE = {
        'DEBUG': 0,
        'INFO': 1,
        'WARN': 2,
        'ERROR': 3,
    }

def set_log_level(level):
    '''
    Sets the minimum log level that should be output
    '''

    global _UTILS_MIN_LOG_LEVEL_PRIVATE
    global _UTILS_LOG_LEVELS_PRIVATE

    if level in _UTILS_LOG_LEVELS_PRIVATE.values():
        _UTILS_MIN_LOG_LEVEL_PRIVATE = level
    else:
        LOG_ERROR('utils.py: Requested log level unsupported')

def LOG(level, msg):
    '''
    Backbone logging function
    '''

    global _UTILS_MIN_LOG_LEVEL_PRIVATE
    global _UTILS_LOG_LEVELS_PRIVATE

    # Check if level is one of the defaults
    if level in _UTILS_LOG_LEVELS_PRIVATE.keys():
        # Check if the requested log level is greater than or equal to
        # the minimum logging level
        if _UTILS_LOG_LEVELS_PRIVATE[level] >= _UTILS_MIN_LOG_LEVEL_PRIVATE:
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
