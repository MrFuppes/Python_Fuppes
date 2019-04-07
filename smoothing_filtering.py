# -*- coding: utf-8 -*-
r"""
Created on Mon Aug 20 11:23:26 2018

@author: F. Obersteiner, florian\obersteiner\\kit\edu
"""

import numpy as np
from scipy.interpolate import interp1d

###############################################################################


def filter_jumps_simple(v, max_delta, no_val=-1, add_v1=None, add_v2=None,
                        delete_vals=False, use_abs_delta=True):

    max_delta = abs(max_delta)

    result = {'filtered': None,
              'ix_del': [],
              'ix_rem': [],
              'add_v1': add_v1,
              'add_v2': add_v2}

    for ix, v_ix in enumerate(v):
        if ix == 0:
            buffer = v_ix
            result['ix_rem'].append(ix)
            continue

        if use_abs_delta:
            delta = abs(v_ix-buffer)
        else:
            delta = v_ix-buffer

        if delta > max_delta or delta < 0.:
            v[ix] = no_val
            result['ix_del'].append(ix)
        else:
            buffer = v_ix
            result['ix_rem'].append(ix)

    if delete_vals:
        result['filtered'] = [element for element in v if element != no_val]

    if delete_vals and add_v1:
        result['add_v1'] = []
        for ix in result['ix_rem']:
            result['add_v1'].append(add_v1[ix])

    if delete_vals and add_v2:
        result['add_v2'] = []
        for ix in result['ix_rem']:
            result['add_v2'].append(add_v2[ix])

    return result


###############################################################################


def filter_jumps_np(v, max_delta, no_val=np.nan, use_abs_delta=True,
                    reset_buffer_after=3, remove_doubles=False,
                    interpol_jumps=False, interpol_kind='linear'):

    len_v = len(v)

    ix_del = np.full(len(v), -1, dtype='int32')  # deletion index
    ix_rem = np.full(len(v), -1, dtype='int32')  # remaining index

    buffer = [False, 0]

    for ix, v_ix in enumerate(v):
        if not np.isfinite(v_ix) or v_ix == no_val:
            ix_rem[ix] = ix
            continue  # skip line if value is np.nan

        if not buffer[0]:
            buffer[0] = v_ix
            ix_rem[ix] = ix
            continue  # fill buffer if not done so yet

        if use_abs_delta:
            delta = abs(v_ix-buffer[0])
        else:
            delta = v_ix-buffer[0]

        if delta > max_delta:  # jump found!
            v[ix] = no_val
            ix_del[ix] = ix
            buffer[1] += 1
            if reset_buffer_after:
                if buffer[1] == reset_buffer_after:
                    buffer = [v_ix, 0]
        else:  # no jump,...
            buffer[0] = v_ix
            if remove_doubles:  # check for double values...
                if delta == 0.:  # double found!
                    v[ix] = no_val
                    ix_del[ix] = ix
                else:  # no double
                    ix_rem[ix] = ix
            else:
                ix_rem[ix] = ix

    w_valid = np.where(ix_del != -1)
    ix_del = ix_del[w_valid]

    w_valid = np.where(ix_rem != -1)
    ix_rem = ix_rem[w_valid]

    if interpol_jumps:
        tmp_x = (np.arange(0, len_v))[ix_rem]
        tmp_y = v[ix_rem]
        f_ip = interp1d(tmp_x, tmp_y,
                        kind=interpol_kind, fill_value='extrapolate')
        filtered = f_ip(np.arange(0, len_v))
    else:
        w_valid = np.where(v != no_val)
        filtered = v[w_valid]

    return {'filtered': filtered,
            'ix_del': ix_del,
            'ix_rem': ix_rem}


###############################################################################


def del_at_edge(v, n_cut, add=2, out_len='same'):
    """
    assume v to be a 1D array which contains blocks of NaNs.
    returns: v with "more NaNs", i.e. range of NaN-blocks is extended by n_cut.
    """

    tf = np.isfinite(v)*1.

    mask = np.convolve(tf, np.ones((int(n_cut+add),))/int(n_cut+add),
                       mode=out_len)

    if tf[0] > 0.9:
        mask[0] = 1.
    if tf[-1] > 0.9:
        mask[-1] = 1.

    mask[np.where(mask < 0.999)] = np.nan

    return v * mask


###############################################################################
