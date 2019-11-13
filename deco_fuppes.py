# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 03:29:04 2019

@author: F. Obersteiner, florian\obersteiner\\kit\edu
"""

import time
import functools
from pathlib import Path

def tic_toc(func):
    """
    print function execution time to console.
    decorator example from https://realpython.com/primer-on-python-decorators/
    """
    @functools.wraps(func)
    def wrapper_tic_toc(*args, **kwargs):
        t0 = time.perf_counter()
        v = func(*args, **kwargs)
        t1 = time.perf_counter()
        print(f"exec. {func.__name__!r} in {(t1-t0):.4e} s")
        return v
    return wrapper_tic_toc


def string2Path(arg_pos=(), kwarg_names=()):
    """
    turn selected arguments / keyword arguments into pathlib.Path objects.
    """
    def check_arg(func):
        if not any((arg_pos, kwarg_names)):
            return func
        @functools.wraps(func)
        def wrapper_checkarg(*args, **kwargs):
            if args and arg_pos:
                args = tuple(Path(a) if i in arg_pos else a for i, a in enumerate(args))
            if func.__kwdefaults__: # requires explicit specification of kwargs by ', *'
                kwargs = {**kwargs, **func.__kwdefaults__} # integrate defaults
            if kwargs and kwarg_names:
                for k, v in kwargs.items():
                    kwargs[k] = Path(v) if k in kwarg_names else v
            return func(*args, **kwargs)
        return wrapper_checkarg
    return check_arg


if __name__ == '__main__':

    # @tic_toc
    # def waste_time(n):
    #     return [i**2 for i in range(n)]

    # a = waste_time(int(1e6))

    @string2Path(arg_pos=(), kwarg_names=('p'))
    def test(*,p='D:/'):
        return p

    print(type(test(p='')))
