#!/usr/bin/env python3

import inspect
import pprint

__version__ = '0.2.0'

def p(*args, **kwargs):
    _print(1, *args, **kwargs)

def pp(*args, **kwargs):
    _pprint(1, *args, **kwargs)

def pv():
    _pprint_vars(1)


def _print(frame_depth, *args, **kwargs):
    frame = inspect.stack()[frame_depth + 1][0]
        
    try:
        # If the calling frame is inside a class (deduced based on the presence 
        # of a 'self' variable), name the logger after that class.  Otherwise 
        # if the calling frame is inside a function, name the logger after that 
        # function.  Otherwise name it after the module of the calling scope.

        self = frame.f_locals.get('self')
        function = inspect.getframeinfo(frame).function
        module = frame.f_globals['__name__']

        if self is not None:
            name = '.'.join([
                    self.__class__.__module__,
                    self.__class__.__name__,
                    function,
            ]) + '()'

        elif function != '<module>':
            name = '.'.join([module, function]) + '()'

        else:
            name = module

        if args or kwargs:
            print(name + '\n', *args, **kwargs)
        else:
            print(name)

    finally:
        # Failing to explicitly delete the frame can lead to long-lived 
        # reference cycles.
        del frame

def _pprint(frame_depth, *args, **kwargs):
    _print(frame_depth + 1, pprint.pformat(*args, **kwargs))

def _pprint_vars(frame_depth):
    frame = inspect.stack()[frame_depth + 1][0]
    _pprint(frame_depth + 1, frame.f_locals)

