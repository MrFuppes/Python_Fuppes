# -*- coding: utf-8 -*-
r"""
Created on Wed Nov 13 12:14:52 2019

@author: F. Obersteiner, florian\obersteiner\\kit\edu
"""
import os
from pathlib import Path as makePath

def find_youngest(path, pattern, n=1):
    """
    find the file that matches a pattern and has the highest modification
    timestamp if there are multiple files that match the pattern.
    input:
        path, string or pathlib.Path, where to look for the file(s)
        pattern, string, pattern to look for in filename
        n, integer, how many to return. defaults to 1
    returns
        filename(s) of youngest file(s), including path.
        None if no file
    """
    assert n >= 1, "n must be greater equal 1."

    path = makePath(path)
    files = [makePath(f) for f in path.glob(pattern) if os.path.isfile(f)]
    sortfiles = sorted(files, key=lambda x: os.path.getmtime(x), reverse=True)

    if sortfiles:
        return sortfiles[:n]
    return None


if __name__ == '__main__':
    path = 'D:/'
    pattern = 'test*txt'
    print(find_youngest(path, pattern, n=4))
