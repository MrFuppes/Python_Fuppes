# -*- coding: utf-8 -*-
r"""
Created on Fri Apr 20 11:17:42 2018

@author: F. Obersteiner, florian\obersteiner\\kit\edu
"""
import os

###############################################################################


class UserError(Exception):
    """ derive user defined errors from exception class """
    pass


class nVarsError(UserError):
    """
    error raised if number of tags in col header is not equal to the
    number of variables found in a file line.
    """

    def __init__(self, n_vars_hdr, n_vars_line, msg):
        self.n_vars_hdr = n_vars_hdr
        self.n_vars_line = n_vars_line
        self.msg = msg

###############################################################################


def txt_2_dict_simple(file, sep=';', colhdr_ix=0, to_float=False,
                      ignore_repeated_sep=False, ignore_colhdr=False,
                      keys_upper=False, preserve_empty=True):
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
    """
    result = None
    try:
        file_obj = open(file, "r")
    except FileNotFoundError:
        print("file not found: " + str(file))
        return result

    data = file_obj.readlines()
    file_obj.close()

    if data:  # check if file contains stuff...
        if ignore_colhdr:
            testline = (data[colhdr_ix+1]).strip()
            testline = testline.rsplit(sep)
            #testline[-1] = (testline[-1])[0:-1]
            header = testline
            for i in range(len(testline)):
                header[i] = 'col_' + str('%3.3u' % (i+1))
        else:
            # remove surrounding whitespaces
            header = (data[colhdr_ix]).strip()
            header = header.rsplit(sep)
            # header[-1] = (header[-1])[0:-1] # remove line ending

        if ignore_repeated_sep:  # remove superfluous delimiters
            while 1:
                try:
                    header.remove('')
                except ValueError:
                    break

        # number of tags in col hdr defines number of variables!
        n_vars = len(header)

        if keys_upper:
            header = [x.upper() for x in header]

        result = {}
        for element in header:
            result[element] = []

        data = data[1+colhdr_ix:]
        for line in data:
            if line.find('\n') > -1:
                if preserve_empty:
                    line = line[:-1]  # only remove linefeed
                else:
                    line = line.strip()  # remove surrounding whitespaces
                line = line.rsplit(sep)

                if ignore_repeated_sep:  # remove superfluous delimiters
                    while 1:
                        try:
                            line.remove('')
                        except ValueError:
                            break

                if len(line) != n_vars:
                    err_msg = ("n elements error, line skipped (" +
                               os.path.basename(file) + ")")
                    try:
                        raise nVarsError(n_vars, len(line), err_msg)
                    except nVarsError as UserError:
                        print('Exception occured in txt_2_dict: ',
                              UserError.msg)
                else:  # now the actual import to dict...
                    for ix, hdr_tag in enumerate(header):
                        if to_float:
                            try:
                                (result[hdr_tag]).append(float(line[ix]))
                            except ValueError:
                                (result[hdr_tag]).append(None)
                        else:
                            (result[hdr_tag]).append((line[ix]).strip())

    return result

###############################################################################
