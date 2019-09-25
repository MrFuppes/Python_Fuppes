# -*- coding: utf-8 -*-
r"""
Created on Mon Aug 20 11:23:26 2018

@author: F. Obersteiner, florian\obersteiner\\kit\edu
"""

import numpy as np
from numba import njit
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


def mask_repeated_elems(arr):
    """
    use numpy diff to mask repeated (adjacent) element in a numpy 1d array.
    - for small array sizes (<10000), a looped solution with
      numba njit is faster.
    """
    # n_el = arr.shape[0]
    # mask = np.ones(arr.shape).astype(np.bool_)
    # i = 0
    # while i < n_el-1:
    #     if arr[i] == arr[i+1]:
    #         cur = arr[i]
    #         for j in range(i+1, n_el):
    #             i += 1
    #             if cur == arr[j]:
    #                 mask[j] = False
    #             else:
    #                 break
    #     i += 1
    mask = np.ones(arr.shape).astype(np.bool_)
    mask[1:] = np.diff(arr).astype(np.bool_)
    return mask

@njit
def mask_jumps(arr, thrsh, look_ahead, abs_delta=False):
    """
    check the elements of array "arr" if the delta between element and
    following element(s) exceed a threshold "trsh". How many elements to
    look ahead is defined by "look_ahead"
    """
    n_el = arr.shape[0]
    mask = np.ones(arr.shape).astype(np.bool_)
    i = 0
    while i < n_el-1:
        cur, nxt = arr[i], arr[i+1]
        delta_0 = np.absolute(nxt-cur) if abs_delta else nxt-cur
        if delta_0 > thrsh:
            for value in arr[i+1:i+look_ahead+1]:
                delta_1 = np.absolute(value-cur) if abs_delta else value-cur
                if delta_1 > thrsh:
                    mask[i+1] = False
                    i += 1
                else:
                    break
        i += 1
    return mask

def filter_jumps_v2(arr, thrsh, look_ahead,
                    abs_delta=False,
                    vmiss=np.nan,
                    remove_repeated=False,
                    interpol_jumps=False, interpol_kind='linear'):
    """
    wrapper around mask_jumps()
    ! interpolation assumes equidistant spacing of the independent variable of
      which arr depends !
    """
    if not isinstance(arr, np.ndarray):
        raise ValueError("input array must be of class numpy ndarray.")
    if arr.ndim > 1:
        raise ValueError("input array must be numpy 1d array.")
    if not isinstance(look_ahead, int):
        raise ValueError("parameter look_ahead must be an integer.")
    if look_ahead >= arr.shape[0] or look_ahead < 1:
        raise ValueError(f"parameter look_ahead must be >=1 and <{arr.shape[0]}.")

    result = arr.copy() # do not touch the input...
    if not np.isnan(vmiss):
        result[vmiss] = np.nan
    if remove_repeated:
        result[~mask_repeated_elems(result)] = np.nan
    mask = mask_jumps(result, thrsh, look_ahead, abs_delta=abs_delta)
    result[~mask] = np.nan
    if interpol_jumps:
        f_ip = interp1d(np.arange(0, result.shape[0])[mask], result[mask],
                        kind=interpol_kind, fill_value='extrapolate')
        result = f_ip(np.arange(0, result.shape[0]))
        return (result, mask)
    return (result, mask)


###############################################################################


def filter_jumps_np(v, max_delta, no_val=np.nan, use_abs_delta=True,
                    reset_buffer_after=3, remove_doubles=False,
                    # if v is dependent on another variable x (e.g. time),
                    # IF x is not equidistant, do NOT use interpolation:
                    interpol_jumps=False, interpol_kind='linear'):

    len_v = len(v)

    ix_del = np.full(len_v, -1, dtype='int32')  # deletion index
    ix_rem = np.full(len_v, -1, dtype='int32')  # remaining index

    buffer = [False, 0]

    for ix, v_ix in enumerate(v):
        if any([~np.isfinite(v_ix), v_ix == no_val, np.isnan(v_ix)]):
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
