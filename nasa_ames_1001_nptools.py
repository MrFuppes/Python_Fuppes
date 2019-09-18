# -*- coding: utf-8 -*-
r"""
Created on Wed May 29 08:35:12 2019

@author: F. Obersteiner, florian\obersteiner\\kit\edu
"""

import numpy as np

def naDict2npndarr(naDict, selVnames,
                   splitVname=';', splitIdx=0,
                   xdtype='float32', vdtype='float64',
                   vmiss=np.NaN):
    """
    convert variables from a nasa ames 1001 dictionary stored as string(lists)
    to numpy nd array type.
    - X is always added.
    - V / variables are selected based on the list supplied as selVnames.
    - each variable is selected based on the index of its VNAME.
    Keywords:
        splitVname: split the vname string and only use the entry at splitIdx
                    of the list resulting from split.
        xdtype, vdtype: representation of x and v
                        (vtype equal for all extracted parameters).
        vmiss: replace the missing value as defined in the nasa ames dict with
               default numpy NaN type. Set to a boolean value to skip.
    """
    npDict = {'x': np.array(naDict['X'], dtype=xdtype)}

    for parm in selVnames:
        if splitVname:
            ix = [l.split(splitVname)[splitIdx] for l in naDict['VNAME']].index(parm)
        else:
            ix = naDict['VNAME'].index(parm)
        npDict[parm] = np.array(naDict['V'][ix], dtype=vdtype)

        # check vmiss: make sure that vmiss=0 also works by checking for type
        # boolean. Might be a bit confusing since vmiss=True would also result
        # in keeping the original values.
        if not isinstance(vmiss, bool):
            npDict[parm][np.where(npDict[parm] == float(naDict['VMISS'][ix]))] = vmiss

    return npDict
