# -*- coding: utf-8 -*-
r"""
Created on Fri Aug 30 15:52:01 2019

@author: F. Obersteiner, florian\obersteiner\\kit\edu
"""

import operator
import numpy as np

def find_fist_elem(arr, val, condition):
    """
    Find the first element in arr that gives (arr[ix] condition val) == True.
    Makes use of next function to stop iteration after condition is met.
    Inputs:
        arr: nummeric numpy 1d array
        val: scalar value
        condition: e.g. 'operator.ge' (operator package)
    Returns:
        (index, value) tuple or None if no match is found.
    """
    sel_ix = next((ix for ix, v in np.ndenumerate(arr) if condition(v, val)), None)
    if sel_ix:
        return (sel_ix[0], arr[sel_ix[0]])
    return None

if __name__ == '__main__':
    # a bit of testing...
    A = np.arange(0, 5000, 0.1)
    X = 2500
    C = operator.ge
    print(find_fist_elem(A, X, C))

    C = operator.gt
    print(find_fist_elem(A, X, C))

    C = operator.le
    print(find_fist_elem(A[::-1], X, C))

    C = operator.lt
    print(find_fist_elem(A[::-1], X, C))

    X = 9000
    C = operator.eq
    print(find_fist_elem(A, X, C))

    A = [i/10 for i in range(50000)]
    X = 2500
    print(find_fist_elem(A, X, C))
