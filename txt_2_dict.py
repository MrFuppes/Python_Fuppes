# -*- coding: utf-8 -*-
r"""
Created on Fri Apr 20 11:17:42 2018

@author: F. Obersteiner, florian\obersteiner\\kit\edu
"""
import os

###############################################################################

def txt_2_dict_basic(file, delimiter, *, offset=0):
    """
    most basic csv reader (delimiter-separated text file).
    faster than dict reader from csv package.
    input:
        file - path and filename (string or pathlib.Path)
        delimiter - line separator (string)
        offset - lines to skip at beginning (integer)
    returns:
        dict; keys = values from the first row, values = rest of the csv file.
    """
    with open(file) as csvfile:
        data = csvfile.read().splitlines()
        if offset > 0:
            data = data[offset:]
        for i, l in enumerate(data):
            data[i] = [v for v in l.split(delimiter) if v]
    return {item[0]: list(item[1:]) for item in zip(*data)}

###############################################################################

def txt_2_dict_simple(file, sep=';', colhdr_ix=0, to_float=False,
                      ignore_repeated_sep=False, ignore_colhdr=False,
                      keys_upper=False, preserve_empty=True,
                      skip_empty_lines=False):
    """
    requires input: txt file with column header and values separated by a
        specific separator (delimiter).
    file: full path to txt file.
    sep: value separator (delimiter), e.g. ";" in a csv file.
    colhdr_ix: row index of the column header.
    to_float: set "True" if all values are represented as floating point nbrs.
        otherwise, returned values are of type string.
    ignore_repeated_sep: if set to True, repeated occurances of "sep" are
        ignored during extraction of elements from the file lines.
        Warning: empty fields must then be filled with a no-value indicator!
    keys_upper: convert key name (from column header) to upper-case
    preserve_empty: do not remove empty fields

    RETURNS: dict
        {'file_hdr': list, 'data': dict with key for each col header tag}
    """

    with open(file, "r") as file_obj:
        content = file_obj.readlines()

    if not content:
        raise ValueError(f"no content in {file}")

    result = {'file_hdr': [], 'data': {}, 'src': str(file)}
    if colhdr_ix > 0:
        result['file_hdr'] = [l.strip() for l in content[:colhdr_ix]]

    col_hdr = content[colhdr_ix].strip().rsplit(sep)
    if ignore_repeated_sep:
        col_hdr = [s for s in col_hdr if s != '']
    if ignore_colhdr:
        for i, _ in enumerate(col_hdr):
            col_hdr[i] = f"col_{(i+1):03d}"

    if keys_upper:
        col_hdr = [s.upper() for s in col_hdr]

    for element in col_hdr:
        result['data'][element] = []

    # cut col header...
    if ignore_colhdr:
        colhdr_ix -= 1

    content = content[1+colhdr_ix:]
    for ix, line in enumerate(content):
        if preserve_empty: # only remove linefeed (if first field is empty)
            line = line[:-1] if '\n' in line else line
        else:
            line = line.strip()  # remove surrounding whitespaces
        if skip_empty_lines:
            if line == '': # skip empty lines
                continue

        line = line.rsplit(sep)

        if ignore_repeated_sep:
            line = [s for s in line if s != '']

        if len(line) != len(col_hdr):
            err_msg = f"n elem in line {ix} != n elem in col header ({file})"
            raise ValueError(err_msg)
        else:  # now the actual import to the dict...
            for i, hdr_tag in enumerate(col_hdr):
                if to_float:
                    try:
                        result['data'][hdr_tag].append(float(line[i]))
                    except ValueError:
                        result['data'][hdr_tag].append(None)
                else:
                    result['data'][hdr_tag].append(line[i].strip())

    return result

###############################################################################

# testing
# if __name__ == '__main__':
#     file = 'D:/PROGRAMMING/Python/Python_Testing/TESTDATA/MA_data_processing/testdata/LH_570_MA/MASTDATA/21_06_19/00_09_00.ARI'
#     d = txt_2_dict_simple(file, sep='\t', colhdr_ix=0, to_float=False,
#                           ignore_repeated_sep=True, ignore_colhdr=False,
#                           keys_upper=False, preserve_empty=True)

#     file = 'D:/KIT/Kampagnen/2019_Southtrac/INST/FAIRO-1/L_2/190913_ST09/data/OSCar_19_09_13_smooth_tcorr.txt'
#     d = txt_2_dict_simple(file, sep='\t', colhdr_ix=2, to_float=False,
#                           ignore_repeated_sep=False, ignore_colhdr=False,
#                           keys_upper=False, preserve_empty=True)

#     d = txt_2_dict_simple(file, sep='\t', colhdr_ix=2, to_float=True,
#                           ignore_repeated_sep=False, ignore_colhdr=True,
#                           keys_upper=True, preserve_empty=True)
