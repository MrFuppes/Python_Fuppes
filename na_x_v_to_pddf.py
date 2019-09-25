# -*- coding: utf-8 -*-
r"""
Created on Sun Sep  8 13:16:16 2019

@author: F. Obersteiner, florian\obersteiner\\kit\edu
"""

import pandas as pd
import numpy as np

from nasa_ames_1001_read import nasa_ames_1001_read as na_r
from timeconversions import mdns_2_datetimeobj as mdns2dt

def get_pddf_from_na1001(file_path,
                         sep=" ", sep_data="\t", sep_com=";",
                         vscale_vmiss_vertical=False,
                         dtype=np.float64,
                         add_datetime=False):
    """
    WHAT?
        wrapper for nasa_ames_1001_read() that just returns a pandas DataFrame
    ASSUMES:
        last line of NCOM contains names of parameters (delimited by sep_data)

    Parameters
    ----------
    file_path : string or pathlib Path
        path with filename to NASA AMES 1001 formatted text file.
    sep : string, optional
        general delimiter. The default is " ".
    sep_data : string, optional
        delimiter to use in data block. The default is "\t".
    sep_com : TYPE, optional
        delimiter to use in commet block. The default is ";".
    vscale_vmiss_vertical : boolean, optional
        see description in nasa_ames_1001_read(). The default is False.
    dtpye : numpy array data type, optional
        data type to use for conversion to DataFrame. The default is np.float64.
    add_datetime: boolean, optional
        derive a datetime object for each row. The default is False.

    Returns
    -------
    Pandas DataFrame
        dataframe with a column for X and one for each parameter in V.

    """

    na_dct = na_r(file_path,
                  sep=sep, sep_data=sep_data, sep_com=sep_com,
                  auto_nncoml=True,
                  strip_lines=True,
                  vscale_vmiss_vertical=False,
                  vmiss_to_None=True)

    # keys = na_dct['NCOM'][-1].split(sep_data)
    keys = [n.split()[0] for n in na_dct['VNAME']]

    # converting to np.array before conversion to pd.df is more efficient:
    values = [np.array(na_dct['X'], dtype=dtype)]

    # check scaling factors:
    if all(s == '1' for s in na_dct['VSCAL']):
        for v_n in na_dct['V']:
            values.append(np.array(v_n, dtype=dtype))
    else:
        vscal = [float(s) for s in na_dct['VSCAL']]
        for i, v_n in enumerate(na_dct['V']):
            values.append(np.array(v_n, dtype=dtype)*vscal[i])

    if add_datetime:
        keys = ['DateTime'] + keys
        dt = mdns2dt(na_dct['X'], year=na_dct['DATE'][0],
                     month=na_dct['DATE'][1], day=na_dct['DATE'][2])
        values = [dt] + values

    return pd.DataFrame.from_dict(dict(zip(keys, values)))

if __name__ == '__main__':
    file_path = 'D:/PROGRAMMING/Python/Python_Testing/TESTDATA/NA_read/valid.txt'

    df = get_pddf_from_na1001(file_path, sep_com='\t')
    print(df.info())
