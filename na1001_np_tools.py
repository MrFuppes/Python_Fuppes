# -*- coding: utf-8 -*-
r"""
Created on Wed May 29 08:35:12 2019

@author: F. Obersteiner, florian\obersteiner\\kit\edu
"""

import numpy as np

def naDict2npndarr(naDict, selVnames=None,
                   splitVname=';', splitIdx=0,
                   xdtype=np.float, vdtype=np.float,
                   vmiss=np.NaN):
    """
    convert variables from a nasa ames 1001 dictionary stored as string(lists)
    to numpy nd array type.

    Parameters
    ----------
    naDict : nasa ames 1001 data in Python dict.
        ...as returned by nasa_ames_1001_read.
    selVnames : list of string, optional
        VNAMEs to be converted. The default is None.
    splitVname : string, optional
        Where to split entries in VNAME. The default is ';'.
    splitIdx : int, optional
        Which part of split result to use, see splitVname. The default is 0.
    xdtype : data type, optional
        Data type for independent variable X. The default is np.float.
    vdtype : data type, optional
        Data type for dependent variable(s). The default is np.float.
    vmiss : missing value identifier, optional
        The default is np.NaN.

    Returns
    -------
    npDict : dict
        dictionary holding numpy arrays for variables from the nasa ames file.

    """
    npDict = {naDict['XNAME'][0]: np.array(naDict['X'], dtype=xdtype)}

    # convenience: link npDict['x'] to npDict[naDict['XNAME'][0]]
    npDict['x'] = npDict[naDict['XNAME'][0]]

    if not selVnames:
        selVnames = [n.split(splitVname)[0] for n in naDict['VNAME']]

    # for each parameter, find its index in naDict['V']
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

if __name__ == '__main__':
    from nasa_ames_1001_read import nasa_ames_1001_read as na_r
    file = 'D:/PROGRAMMING/Python/Python_Testing/TESTDATA/NA_read/valid.txt'
    naDict = na_r(file)
    npDict = naDict2npndarr(naDict)
