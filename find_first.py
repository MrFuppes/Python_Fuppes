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
    Inputs:
        arr: numeric numpy 1d array or python list
        val: scalar value
        condition: e.g. 'operator.ge' (operator package)
    Returns:
        index of value matching the condition or None if no match is found.
    """
    if isinstance(arr, list):
        return next((ix for ix, v in enumerate(arr) if condition(v, val)), None)
    result = np.argmax(condition(arr, val))
    return result if condition(arr[result], val) else None


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
