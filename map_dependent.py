# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 14:29:36 2020

@author: F. Obersteiner, f/obersteiner//kit/edu
"""
import numpy as np



def map_dependent(xref, xcmp, vcmp, vmiss=np.nan):
    """
    Map a variable "vcmp" depending on variable "xcmp" to an independent
        variable "xref".

    Parameters
    ----------
    xref : np.ndarray, 1D
        reference / independent variable.
    xcmp : np.ndarray, 1D
        independent variable of vcmp.
    vcmp : np.ndarray, 1D
        dependent variable of xcmp.

    Returns
    -------
    vmap : np.ndarray, 1D
        vcmp mapped to xref.

    """
    # which element of xref has a corresponding element in xcmp?
    m = np.in1d(xref, xcmp)

    # prepare output
    vmap = np.empty(xref.shape, dtype=vcmp.dtype)
    # insert NaN where xref has NO corresponding element
    vmap[~m] = vmiss

    # where corresponding elements exist, insert those from vcmp
    vmap[m] = np.take(vcmp, np.nonzero(np.in1d(xcmp, xref)))[0]

    return vmap



if __name__ == '__main__':
    # first missing
    xref = np.array([1,2,3], dtype=np.int)
    xcmp = np.array([2,3,4], dtype=np.int)
    vcmp = np.array([1,2,3], dtype=np.float)
    tgt = np.array([np.nan,1,2], dtype=np.float)

    test = map_dependent(xref, xcmp, vcmp)
    print(tgt, test, sep='\n')

    # last missing
    xref = np.array([1,2,3], dtype=np.int)
    xcmp = np.array([0,1,2], dtype=np.int)
    vcmp = np.array([1,2,3], dtype=np.float)
    tgt = np.array([2,3,np.nan], dtype=np.float)

    test = map_dependent(xref, xcmp, vcmp)
    print(tgt, test, sep='\n')

    # gap
    xref = np.array([1,2,3,4], dtype=np.int)
    xcmp = np.array([1,4,5,6], dtype=np.int)
    vcmp = np.array([1,2,3,4], dtype=np.float)
    tgt = np.array([1,np.nan,np.nan,2], dtype=np.float)

    test = map_dependent(xref, xcmp, vcmp)
    print(tgt, test, sep='\n')

    # missing elements in cmp
    xref = np.array([1,2,3,4], dtype=np.int)
    xcmp = np.array([1,4,5], dtype=np.int)
    vcmp = np.array([1,2,3], dtype=np.float)
    tgt = np.array([1,np.nan,np.nan,2], dtype=np.float)

    test = map_dependent(xref, xcmp, vcmp)
    print(tgt, test, sep='\n')

    # missing elements in ref
    xref = np.array([1,2,3], dtype=np.int)
    xcmp = np.array([1,4,5,6], dtype=np.int)
    vcmp = np.array([1,2,3,4], dtype=np.float)
    tgt = np.array([1,np.nan,np.nan], dtype=np.float)

    test = map_dependent(xref, xcmp, vcmp)
    print(tgt, test, sep='\n')
