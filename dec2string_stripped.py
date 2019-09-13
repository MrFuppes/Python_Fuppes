# -*- coding: utf-8 -*-
r"""
Created on Wed Sep  4 10:10:20 2019

@author: F. Obersteiner, florian\obersteiner\\kit\edu
"""

def dec2str_stripped(num, dec_places=3, strip='right'):
    """
    Parameters
    ----------
    num : float or list of float
        scalar or list of decimal numbers.
    dec_places : int, optional
        number of decimal places to return. defaults to 3.
    strip : string, optional
        what to strip. 'right' (default), 'left' or 'both'.

    Returns
    -------
    list of string.
        numbers formatted as strings according to specification (see kwargs).
    """
    if not isinstance(num, list): # might be scalar or numpy array
        try:
            num = list(num)
        except TypeError: # input was scalar
            num = [num]

    if not isinstance(dec_places, int) or int(dec_places) < 1:
        raise ValueError(f"kwarg dec_places must be integer > 1 (got {dec_places})")

    if strip == 'right':
        return [f"{n:.{str(dec_places)}f}".rstrip('0') for n in num]
    if strip == 'left':
        return [f"{n:.{str(dec_places)}f}".lstrip('0') for n in num]
    if strip == 'both':
        return [f"{n:.{str(dec_places)}f}".strip('0') for n in num]
    raise ValueError(f"kwarg 'strip' must be 'right', 'left' or 'both' (got '{strip}')")


if __name__ == '__main__': # a bit of testing...
    # valid
    NUMBERS = [0.010701]
    print('right:', dec2str_stripped(NUMBERS, dec_places=3, strip='right'))
    print('left:', dec2str_stripped(NUMBERS, dec_places=3, strip='left'))
    print('both:', dec2str_stripped(NUMBERS, dec_places=3, strip='both'))
    NUMBERS = [1.0, 3.44532, 0.12011]
    print('right:', dec2str_stripped(NUMBERS, dec_places=3, strip='right'))
    print('left:', dec2str_stripped(NUMBERS, dec_places=3, strip='left'))
    print('both:', dec2str_stripped(NUMBERS, dec_places=3, strip='both'))
    # invalid
    print('fail:', dec2str_stripped(NUMBERS, dec_places=-3, strip='right'))
    print('fail:', dec2str_stripped(NUMBERS, dec_places=3, strip='fail'))
