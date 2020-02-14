# -*- coding: utf-8 -*-
r"""
Created on Mon Feb 12 09:32:32 2018

@author: F. Obersteiner, florian\obersteiner\\kit\edu

more info on NASA AMES file format:
    https://espoarchive.nasa.gov/content/Ames_Format_Specification_v20
"""
import os
from pathlib import Path as makePath
from datetime import date


def check_lt128(file):
    """
    Check if all bytes of a file are less than decimal 128.
    Returns True for an ASCII encoded text file.
    """
    with open(file, 'rb') as f:
        content = f.read()
    return all(b<128 for b in content)


def nasa_ames_1001_read(file_path, sep=" ", sep_com=";", sep_data="\t",
                        auto_nncoml=True,
                        strip_lines=True,
                        remove_doubleseps=False,
                        vscale_vmiss_vertical=False,
                        vmiss_to_None=False,
                        ensure_ascii=True):
    """
    read NASA AMES 1001 formatted text file. expected encoding is ASCII.
    args:
        file_path: path to file
    kwargs:
        sep=" ": general string separator, e.g. space
        sep_com=";": string separator used exclusively in comment block
        sep_data="\t": string separator used exclusively in data block
        auto_nncoml=True: automatically determine number of lines in normal
                          comment block
        strip_lines=True: remove whitespaces from all file lines
        remove_doubleseps=False: remove repeated occurrences of general
                                 separator
        vscale_vmiss_vertical=False: set to True if VSCALE and VMISS parameters
                                     are arranged vertically over multiple
                                     lines (1 entry per line) instead of in one
                                     line each (e.g. for DLR Bahamas files)
        vmiss_to_None: set True if missing values should be replaced with None.
        ensure_ascii: check if all bytes in the specified file are < 128.

    returns:
        na_1001: dictionary with keys according to NASA AMES 1001 file
                 specification
    """
    try:
        file_path.is_file()
    except AttributeError: # file path is not provided as path object; convert
        file_path = makePath(file_path)

    if not os.path.isfile(file_path): # check if file exists
        raise FileExistsError(str(file_path) + "\n    does not exist.")
    else:
        if ensure_ascii:
            if not check_lt128(file_path):
                raise TypeError(f"non-ASCII character found in {str(file_path)}")

        with open(file_path, "r", encoding="ASCII") as file_obj:
            data = file_obj.readlines() # read file content to string list

        if strip_lines:
            for i, line in enumerate(data):
                data[i] = line.strip()

        if remove_doubleseps:
            for i, line in enumerate(data):
                while sep+sep in line:
                    line = line.replace(sep+sep, sep)
                data[i] = line

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

        tmp = list(map(int, data[0].split()))
        assert len(tmp) == 2, f"invalid format in {data[0]} (line 1)"
        assert tmp[1] == 1001, f"invalid FFI in {data[0]} (line 1)"

        nlhead = tmp[0]
        na_1001['NLHEAD'] = nlhead
        na_1001['FFI'] = tmp[1]

        header = data[0:nlhead]
        data = data[nlhead:]

        # test case: no data ->
        assert data, "no data found."

        na_1001['ONAME'] = header[1]
        na_1001['ORG'] = header[2]
        na_1001['SNAME'] = header[3]
        na_1001['MNAME'] = header[4]

        tmp = list(map(int, header[5].split()))
        assert len(tmp) ==2, f"invalid format {header[5]} (line 6)"
        na_1001['IVOL'], na_1001['NVOL'] = tmp[0], tmp[1]

        tmp = list(map(int, header[6].split()))
        assert len(tmp) == 6, f"invalid format {header[6]} (line 7)"
        # check for valid date in line 7 (yyyy mm dd)
        date(*tmp[:3]), date(*tmp[3:6])
        na_1001['DATE'], na_1001['RDATE'] = tmp[:3], tmp[3:6]

        na_1001['DX'] = float(header[7]) # dx=0 means non-uniform independent variable.
        na_1001['XNAME'] = header[8].rsplit(sep=sep_com)
        # CARIBIC: [0] is type, [1] is description, [2] is unit.

        n_vars = int(header[9])
        na_1001['NV'] = n_vars

        if vscale_vmiss_vertical:
            offset = n_vars*2
            na_1001['VSCAL'] = header[10:10+n_vars]
            na_1001['VMISS'] = header[10+n_vars:10+n_vars*2]
        else:
            offset = 2
            na_1001['VSCAL'] = header[10].split()
            na_1001['VMISS'] = header[11].split()
        # test case:
        msg = "vscal, vmiss and vname must have equal number of elements"
        assert n_vars == len(na_1001['VSCAL']) == len(na_1001['VMISS']), msg

        na_1001['VNAME'] = header[10+offset:10+n_vars+offset]

        nscoml = int(header[10+n_vars+offset])
        na_1001['NSCOML'] = nscoml
        if nscoml > 0: # read special comment if nscoml>0
            na_1001['SCOM'] = header[n_vars+11+offset:n_vars+nscoml+11+offset]
        else:
            na_1001['SCOM'] = ""
        # test case:
        msg = "nscoml not equal n elements in list na_1001['SCOM']"
        assert nscoml == len(na_1001['SCOM']), msg

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
        # test case:
        msg = "nncoml not equal n elements in list na_1001['NCOM']"
        assert nncoml == len(na_1001['NCOM']), msg
        # test case
        msg = "nlhead must be equal to nncoml + nscoml + n_vars + 14"
        assert nncoml+nscoml+n_vars+14 == nlhead, msg

        # done with header, continue with variables.
        na_1001['X'] = [] # holds independent variable
        na_1001['V'] = [[] for _ in range(n_vars)] # list for each dependent variable

        for ix, line in enumerate(data):
            l = line.rsplit(sep=sep_data)
            assert len(l) == n_vars+1, f'invalid number of parameters in line {ix+nlhead}'
            na_1001['X'].append(l[0])
            if vmiss_to_None:
                for j in range(n_vars):
                    na_1001['V'][j].append(l[j+1] if l[j+1] != na_1001['VMISS'][j] else None)
            else:
                for j in range(n_vars):
                    na_1001['V'][j].append(l[j+1])

    return na_1001
