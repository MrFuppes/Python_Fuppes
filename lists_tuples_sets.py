# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 10:36:14 2020

@author: F. Obersteiner, f/obersteiner//kit/edu
"""
#------------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------------
def list_chng_elem_index(l, element, new_index):
    """
    change the index of an element in a list.
    ! modifies the list in-place !
    see https://stackoverflow.com/a/3173159/10197418
    """
    if new_index >= len(l) or new_index < 0:
        raise IndexError("new index is out of range")

    if element in l:
        l.insert(new_index, l.pop(l.index(element)))
#------------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------------
def set_compare(a, b):
    """
    Compare two iterables a and b. set() is used for comparison, so only
    unique elements will be considered.

    Parameters
    ----------
    a : iterable
    b : iterable

    Returns
    -------
    tuple with 3 elements:
        (what is only in a (not in b),
         what is only in b (not in a),
         what is common in a and b)
    """
    a, b = set(a), set(b)
    return (a-b, b-a, a.intersection(b))
#------------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------------
