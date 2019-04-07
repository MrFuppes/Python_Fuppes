# -*- coding: utf-8 -*-
r"""
Created on Tue Aug  7 17:19:19 2018

@author / adapted from:

 https://stackoverflow.com/questions/4983258/python-how-to-check-list-monotonicity
 2018-08-07 15:20 UTC

"""
def strictly_increasing(L):
    return all(x<y for x, y in zip(L, L[1:]))

def strictly_decreasing(L):
    return all(x>y for x, y in zip(L, L[1:]))

def non_increasing(L):
    return all(x>=y for x, y in zip(L, L[1:]))

def non_decreasing(L):
    return all(x<=y for x, y in zip(L, L[1:]))
