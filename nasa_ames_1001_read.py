# -*- coding: utf-8 -*-
r"""
Created on Mon Feb 12 09:32:32 2018

@author: F. Obersteiner, florian\obersteiner\\kit\edu

more info on NASA AMES file format:
    https://espoarchive.nasa.gov/content/Ames_Format_Specification_v20
"""
import os
from pathlib import Path as makePath

def nasa_ames_1001_read(file_path, sep=" ", sep_com=";", sep_data="\t",
                        auto_nncoml=True, strip_lines=True,
                        remove_doubleseps=False,
                        vscale_vmiss_vertical=False):
    """
    Function input:
        file_path: path to file

    Function config:
        sep=" ": general string separator, e.g. space
        sep_com=";": string separater used exclusively in comment block
        sep_data="\t": string separator used exclusively in data block
        auto_nncoml=True: automatically determine number of lines in normal
                          comment block
        strip_lines=True: remove whitespaces from all file lines
        remove_doubleseps=False: remove repeated occurances of general
                                 separator
        vscale_vmiss_vertical=False: set to True if VSCALE and VMISS parameters
                                     are arranged vertically over multiple
                                     lines (1 entry per line) instead of in one
                                     line each (e.g. for DLR Bahamas files)

    Function output:
        na_1001: dictionary with keys according to NASA AMES 1001 file
                 specification
    """
    try:
        file_path.is_file()
    except AttributeError: # file path is not provided as path object; convert
        file_path = makePath(file_path)

    if not os.path.isfile(file_path): # check if file exists
        raise FileExistsError(str(file_path) + "\n    does not exist.")
        na_1001 = None # return None if not
    else:
        with open(file_path, "r", encoding="UTF-8") as file_obj:
            data = file_obj.readlines() # read file content to string list

        if strip_lines:
            for ix, line in enumerate(data):
                data[ix] = line.strip()

        if remove_doubleseps:
            for ix, line in enumerate(data):
                while sep+sep in line:
                    line = line.replace(sep+sep, sep)
                data[ix] = line

        na_1001 = {'NLHEAD': None,
                   'FFI': None,
                   'ONAME': None,
                   'ORG': None,
                   'SNAME': None,
                   'MNAME': None,
                   'IVOL': None,
                   'NVOL': None,
                   'DATE': None,
                   'RDATE': None,
                   'DX': None,
                   'XNAME': None,
                   'NV': None,
                   'VSCAL': None,
                   'VMISS': None,
                   'VNAME': None,
                   'NSCOML': None,
                   'SCOM': None,
                   'NNCOML': None,
                   'NCOM': None,
                   'X': None,
                   'V': None}

        #nlhead = int((data[0].partition(sep))[0])
        nlhead = int((data[0].partition(sep))[0])
        na_1001['NLHEAD'] = nlhead
        na_1001['FFI'] = int((data[0].partition(sep))[-1])
        if na_1001['FFI'] != 1001:
            raise(ValueError("file format identifier not equal to 1001!"))
            return None

        header = data[0:nlhead]
        data = data[nlhead:]
        # warning case: data does not contain any values?

        na_1001['ONAME'] = header[1]
        na_1001['ORG'] = header[2]
        na_1001['SNAME'] = header[3]
        na_1001['MNAME'] = header[4]

        na_1001['IVOL'] = int((header[5].partition(sep))[0])
        na_1001['NVOL'] = int((header[5].partition(sep))[2])

        try:
            na_1001['DATE'] = list(map(int, (header[6].rsplit(sep=sep))[0:3]))
        except ValueError:
            na_1001['DATE'] = [9999,99,99]

        try:
            na_1001['RDATE'] = list(map(int, (header[6].rsplit(sep=sep))[3:6]))
        except ValueError:
            na_1001['RDATE'] = [9999,99,99]

        na_1001['DX'] = float(header[7]) # dx=0 means non-uniform independent variable.
        na_1001['XNAME'] = header[8].rsplit(sep=sep_com) # [0] is type, [1] is description, [2] is unit.
        n_vars = int(header[9])
        na_1001['NV'] = n_vars

        if vscale_vmiss_vertical:
            offset = n_vars*2
            na_1001['VSCAL'] = header[10:10+n_vars]
            na_1001['VMISS'] = header[10+n_vars:10+n_vars*2]
        else:
            offset = 2
            na_1001['VSCAL'] = header[10].rsplit(sep=sep) # attention: scaling factors imported as strings.
            na_1001['VMISS'] = header[11].rsplit(sep=sep)
            # warning cases: vscal or vmiss or vname must have number of elements equal to nv.

        na_1001['VNAME'] = header[10+offset:10+n_vars+offset]

        nscoml = int(header[10+n_vars+offset])
        na_1001['NSCOML'] = nscoml
        if nscoml > 0: # read special comment if nscoml>0
            na_1001['SCOM'] = header[n_vars+11+offset:n_vars+nscoml+11+offset]
        else:
            na_1001['SCOM'] = ""

        # error case: nscoml not equal n elements in list na_1001['SCOM']

        # read normal comment if nncoml>0
        if auto_nncoml is True:
            nncoml = nlhead-(n_vars+nscoml+12+offset)
        else:
            nncoml = int(header[n_vars+nscoml+11+offset])

        na_1001['NNCOML'] = nncoml
        if nncoml > 0:
            na_1001['NCOM'] = header[n_vars+nscoml+12+offset:n_vars+nscoml+nncoml+12+offset]
        else:
            na_1001['NCOM'] = ""


        # done with header, continue with variables.
        var_x = [] # holds independent variable
        var_v = []
        for j in range(n_vars):
            var_v.append([]) # holds one list for each variable

        for i in range(len(data)):
            line = (data[i].rsplit(sep=sep_data))
            if len(line) == n_vars+1:
                var_x.append(line[0])
                for j in range(n_vars):
                    var_v[j].append(line[j+1])
            else:
                print("na read -> skipped data block line", i)

        na_1001['X'] = var_x
        na_1001['V'] = var_v

    return na_1001
