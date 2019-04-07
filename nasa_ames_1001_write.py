# -*- coding: utf-8 -*-
r"""
Created on Tue Feb 13 15:17:08 2018

@author: F. Obersteiner, florian\obersteiner\\kit\edu

more info on NASA AMES file format:
    https://espoarchive.nasa.gov/content/Ames_Format_Specification_v20
"""
# missing: check strings / list of strings that each string is terminated correctly

import os

def nasa_ames_1001_write(file_path, na_1001,
                         sep=" ", sep_com=";", sep_data="\t",
                         crlf="\n", overwrite=False, verbose=False):
    """
    writes dictionary 'na_1001' to text file in nasa ames 1001 format.
    +++
    expected keys in na_1001:
    'NLHEAD'
    'FFI'
    'ONAME'
    'ORG'
    'SNAME'
    'MNAME'
    'IVOL'
    'NVOL'
    'DATE'
    'RDATE'
    'DX'
    'XNAME'
    'NV'
    'VSCAL'
    'VMISS'
    'VNAME'
    'NSCOML' - int
    'SCOM' - list with strings, including line feed
    'NNCOML' - int
    'NCOM' - list with strings, including line feed
    'X' - list
    'V' - list with nested list for each dependent variable
    +++
    return value: None -> fail, 1 -> normal write, 2 -> overwrite
    """
    write = None
    # check if directory exists, create if not.
    if os.path.isdir(os.path.dirname(file_path)) == False:
        os.mkdir(os.path.dirname(file_path))

    # check if file exists, act according to overwrite keyword
    if os.path.isfile(file_path) == True:
        if overwrite == False:
            return write # write failed / forbidden
        else:
            write = 2 # overwriting
    else:
        write = 1 # normal writing

    #
    # +++
    # check n variables and comment lines; adjust values if incorrect
    n_vars_def = na_1001['NV']
    n_vars_named = len(na_1001['VNAME'])
    n_vars_data = len(na_1001['V'])
    if n_vars_named != n_vars_data:
        if verbose:
            print("NA error: n vars in V and VNAME not equal, " +
                  str(n_vars_data) + " vs. " + str(n_vars_named) + "!")
        write = None # error case: undefined or missing variables in v

    else:
        d_nvars = n_vars_named-n_vars_def
        if d_nvars != 0:
            if verbose:
                print("NA output: NV corrected!")
            na_1001['NV'] = n_vars_named

        nscoml_is = len(na_1001['SCOM'])
        nscoml_def = na_1001['NSCOML']
        d_nscoml = nscoml_is-nscoml_def
        if d_nscoml != 0:
            if verbose:
                print("NA output: NSCOML corrected!")
            na_1001['NSCOML'] = nscoml_is

        nncoml_is = len(na_1001['NCOM'])
        nncoml_def = na_1001['NNCOML']
        d_nncoml = nncoml_is-nncoml_def
        if d_nncoml != 0:
            if verbose:
                print("NA output: NNCOML corrected!")
            na_1001['NNCOML'] = nncoml_is

        nlhead_def = na_1001['NLHEAD']
        nlhead_is = 14 + n_vars_named + nscoml_is + nncoml_is
        d_nlhead = nlhead_is-nlhead_def
        if d_nlhead != 0:
            if verbose:
                print("NA output: NLHEAD corrected!")
            na_1001['NLHEAD'] = nlhead_is

        #
        # +++
        # begin the actual writing process...

        file_obj = open(file_path, "w", encoding="UTF-8")

        block = str(na_1001['NLHEAD'])+sep+str(na_1001['FFI'])+crlf
        file_obj.write(block)

        block = str(na_1001['ONAME'])+crlf
        file_obj.write(block)

        block = str(na_1001['ORG'])+crlf
        file_obj.write(block)

        block = str(na_1001['SNAME'])+crlf
        file_obj.write(block)

        block = str(na_1001['MNAME'])+crlf
        file_obj.write(block)

        block = str(na_1001['IVOL'])+sep+str(na_1001['NVOL'])+crlf
        file_obj.write(block)

        block = str('%4.4u' % (na_1001['DATE'])[0])+sep+ \
                str('%2.2u' % (na_1001['DATE'])[1])+sep+ \
                str('%2.2u' % (na_1001['DATE'])[2])+sep+ \
                str('%4.4u' % (na_1001['RDATE'])[0])+sep+ \
                str('%2.2u' % (na_1001['RDATE'])[1])+sep+ \
                str('%2.2u' % (na_1001['RDATE'])[2])+crlf # assume "yyyy m d" in list
        file_obj.write(block)

        block = '{:g}'.format(na_1001['DX'])+crlf
        file_obj.write(block)

        block = ""
        for i in range(len(na_1001['XNAME'])): # expects list input
            block = block+(na_1001['XNAME'])[i]+sep_com
        block = block[0:-1]+crlf
        file_obj.write(block)

        n_vars = na_1001['NV'] # get number of variables
        block = str(n_vars)+crlf
        file_obj.write(block)

        line = ""
        for i in range(n_vars):
            line = line+str((na_1001['VSCAL'])[i])+sep
        if line.find("\n") > -1:
            line = line[0:-1]
        else:
            line = line[0:-1]+crlf
        file_obj.write(line)

        line = ""
        for i in range(n_vars):
            line = line+str((na_1001['VMISS'])[i])+sep
        if line.find("\n") > -1:
            line = line[0:-1]
        else:
            line = line[0:-1]+crlf
        file_obj.write(line)

        block = na_1001['VNAME']
        for i in range(n_vars):
            file_obj.write(block[i]+crlf)

        nscoml = na_1001['NSCOML'] # get number of special comment lines
        line = str(nscoml)+crlf
        file_obj.write(line)

        block = na_1001['SCOM']
        for i in range(nscoml):
            file_obj.write(block[i]+crlf)

        nncoml = na_1001['NNCOML'] # get number of normal comment lines
        line = str(nncoml)+crlf
        file_obj.write(line)

        block = na_1001['NCOM']
        for i in range(nncoml):
            file_obj.write(block[i]+crlf)

        nl_data = len(na_1001['X']) # lines of data to write
        for i in range(nl_data):
            line = str((na_1001['X'])[i])+sep_data
            for j in range(n_vars):
                line = line+str((na_1001['V'][j])[i])+sep_data
            if line.find("\n") > -1:
                line = line[0:-1]
            else:
                line = line[0:-1]+crlf
            file_obj.write(line)

        file_obj.close()

    return write
