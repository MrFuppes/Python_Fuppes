# -*- coding: utf-8 -*-
r"""
Created on Fri May 10 12:04:21 2019

@author: F. Obersteiner, florian\obersteiner\\kit\edu
"""

import re

###############################################################################

def string2num(string, convert=True, signed_int=False, verbose=False):
    """
    check if a string can be converted to integer or floating point number.
    input examples:
        '45', '45.', '3E5', '4E+5', '3E-3', '2.345E+7',
        '-7', '-45.3', '-3.4E3', ' 12 '
    everything else is just a string.
    ! decimal separator is '.' !
    keywords:
        convert -> if True, convert the string to number (if regex match)
                   if False, the function returns the detected type
        signed_int -> if True, differentiate signed and unsigned integers
                      only set True if convert is False
        verbose -> print detailled result to console
    """
    if not isinstance(string, str):
        raise ValueError("input must be of type string.")

    # define regular expressions to look for; ordered according to most
    # frequent input; as well as conversion function
    rdict = {'flt': [r'[+|-]*[0-9]+[.][0-9]*', float],
             'int': [r'[+|-]*[0-9]+', int],
             'flt_e': [r'[+|-]*[.0-9]+[eE]\D*[0-9]+', float]}
    if signed_int:
        rdict['int'] = [r'[+|-][0-9]+', int]
        rdict['uint'] = [r'[0-9]+', int]

    if verbose:
        print(string, '-> ', end='')
        for key, expr in rdict.items():
            result = re.fullmatch(expr[0], string.strip())
            if result:
                print(key, result, expr[1](string), sep='\t', end='')
        print()

    for key, expr in rdict.items(): # iterate expressions...
        result = re.fullmatch(expr[0], string.strip())
        if result:
            result = expr[1](string) if convert else key
            break # will exit iteration if a match is found!

    if not result:
        result = string if convert else 'str'

    return result

###############################################################################

def numstr_fmt(string, typ):
    """
    given a string number and the number type (float, int), detect the number
    format, i.e. decimal places etc. - any input digit is considered to be
    significant unless a float formatted e.g. 5. is presented to the function.
    ! decimal separator is '.' !
    """
    if not all([isinstance(string, str), isinstance(string, str)]):
        raise ValueError("input must be of type string.")

    if typ == 'flt':
        lst = string.strip().split('.')
        if not lst[1]: # trailing zeros are hidden
            result = '{:+g}' if '+' in lst[0] else '{:g}'
        # hidden leading zeros are not checked!
        else:
            result = '{0:+.' if '+' in lst[0] else '{0:.'
            result += str(len(lst[1])) + 'f}'
    elif typ in ('int', 'uint'):
        result = '{:+d}' if '+' in string else '{:d}'
    elif typ == 'flt_e':
        lst = string.strip().split('.')
        if len(lst) == 1: # decimal places
            result = '{:.0E}'
        else:
            lst = lst[1].upper().split('E')
            result = '{:.' + str(len(lst[0])) + 'E}'
        # signed or unsigned if + ?
        # leading zero after E ?
        # upper or lower case E ?
    else:
        result = '{}'

    return result

###############################################################################
###############################################################################

if __name__ == '__main__':

    STRINGS = ['45', '45.', '3E5', '4E+5', '3E-3', '2.345E+7',
               'tesT', 'Test45', '-7', '-45.3', '-3.4E3', ' 12 ']

    for s in STRINGS:
        res = string2num(s, convert=False, signed_int=True,
                         verbose=False)
        print(s, res, type(res))
        fmt = numstr_fmt(s, res)
        res = string2num(s, convert=True)
        print(fmt, fmt.format(res))
