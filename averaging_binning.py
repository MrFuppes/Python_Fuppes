# -*- coding: utf-8 -*-
r"""
Created on Thu Aug  9 09:46:55 2018

@author: F. Obersteiner, florian\obersteiner\\kit\edu
"""
import statistics as stat
from cmath import rect, phase
from math import radians, degrees, floor
from datetime import datetime, date
from copy import deepcopy

import numpy as np
import numba as nu
import pandas as pd
from scipy.interpolate import interp1d

from monotonicity import strictly_increasing


###############################################################################


def mean_angle(deg):
    """
    - if input parameter deg contains NaN or is a numpy masked array, missing
      values will be removed before the calculation.
    - result is degrees between -180 and +180
    """
    if np.ma.isMaskedArray(deg):
        deg = deg.data
    elif isinstance(deg, np.ndarray):
        deg = deg[np.isfinite(deg)]

    if len(deg) == 0:
        return np.nan
    elif len(deg) == 1:
        return deg[0]

    return degrees(phase(sum(rect(1, radians(d)) for d in deg)/len(deg)))


###############################################################################


@nu.njit
def mean_angle_numba(deg):
    """
    - numba compatible version of mean_angle()
    - input must be numpy array of type float!
    """
    deg = deg[np.isfinite(deg)]
    if len(deg) == 0:
        return np.nan
    elif len(deg) == 1:
        return deg[0]

    result = 0
    for d in deg:
        result += rect(1, radians(d))
    return degrees(phase(result/len(deg)))


###############################################################################


def mean_day_frac(dfr, use_numba=True):
    """
    - use the mean_angle function to calculate a mean day fraction (0-1).
      the conversion to angle is necessary since day changes cannot be
      calculated as arithmetic mean.
    - dfr: day fraction, 0-1
    - if input parameter dfr contains NaN or is a numpy masked array, missing
      values will be removed before the calculation.
    """
    if np.ma.isMaskedArray(dfr):
        dfr = dfr.data
    elif isinstance(dfr, np.ndarray):
        dfr = dfr[np.isfinite(dfr)]
    else:
        dfr = np.array(dfr, dtype='float64')
        dfr = dfr[np.isfinite(dfr)]

    if len(dfr) == 0:
        return np.nan
    elif len(dfr) == 1:
        return dfr[0]

    if use_numba:
        deg_mean = mean_angle_numba(dfr*360)
    else:
        deg_mean = mean_angle(dfr*360)

    if deg_mean < 0: # account for mean degree between -180 and +180
        deg_mean += 360

    return deg_mean/360


###############################################################################


def mask_repeated(a, N):
    """
    given an array a that consists of sections of repeated elements, mask
    those elements in a section that repeat more than N times
    ex:
        a = [1,1,1,1,2,2,2]
        N = 3
        --> mask = [True,True,True,False,True,True,True]
    returns:
        boolean mask

    on SO:
        https://stackoverflow.com/a/58482894/10197418
    """
    mask = np.empty(a.size, np.bool_)
    mask[:N] = True
    np.not_equal(a[N:], a[:-N], out=mask[N:])
    return mask


###############################################################################


@nu.njit
def mask_repeated_nb(arr, n):
    """
    numba version of mask_repeated().
    on SO:
        https://stackoverflow.com/a/58492855/10197418
    """
    mask = np.ones(arr.shape, np.bool_)
    current = arr[0]
    count = 0
    for idx, item in enumerate(arr):
        if item == current:
            count += 1
        else:
            current = item
            count = 1
        mask[idx] = count <= n
    return mask


###############################################################################


def bin_time(t, binwidth, *, t_binned=None):
    """
    bin a time vector to an arbitrary bin width.
    inputs:
        t : time vector, increasing monotonically, np nd array, 1D.
        binwidth: bin width in units of t, scalar.
                  e.g. unit of t is seconds --> binwidth = 30 == 30s bin width.
        t_binned: supply a np 1D array to predefine bin centres.
                  must match with binwidth.
    """
    if np.any(t_binned):
        if not np.isclose(np.unique(np.diff(t_binned))[0], binwidth):
            raise ValueError('Incorrect binwidth in t_binned.')
    else:
        n_bins = np.ceil((t[-1]-t[0]) / binwidth)
        t_binned = (np.linspace(t[0], t[0]+n_bins*binwidth,
                               num=n_bins, endpoint=False) + binwidth//2)
    # determine bins:
    bins = np.searchsorted(t_binned-binwidth/2, t, side='right')

    # limit the maximum number of elements per bin:
    max_n_per_bin = int(binwidth // np.median(np.diff(t)))
    m = mask_repeated(bins, max_n_per_bin)

    # do not allow preceeding bins (0):
    m[bins == 0] = False

    n_per_bin = np.unique(bins, return_counts=True)[1]
    n_per_bin_masked = np.unique(bins[m], return_counts=True)[1]
    cut_first = 0 in bins
    cut_last = n_per_bin_masked[-1] != max_n_per_bin
    if cut_last:
        t_binned = t_binned[:-1]

    return {'t_binned': t_binned,
            'bins': bins,
            'n_per_bin': n_per_bin,
            'n_per_bin_masked': n_per_bin_masked,
            'mask': m,
            'cut_first': cut_first,
            'cut_last': cut_last}


###############################################################################


def bin_time_10s(t, force_t_range=True):
    """
    numpy version of binning the time axis to 10s intervals around 5;
        lower boundary included, upper boundary excluded (0. <= 5. < 10.)
    input: np.ndarray (time vector, increasing monotonically)
    returns: dict with binned time axis and bins,
        as returned by np.searchsorted()
    force_t_range: set to True to enforce bins to fall within range of t
    """
    if not isinstance(t, np.ndarray):
        raise TypeError('Please pass np.ndarray to function.')

    if t.ndim != 1:
        raise TypeError('Please pass 1D array to function.')

    from monotonicity import strict_inc_np
    if not strict_inc_np(t):
        raise ValueError('Input must be strictly increasing.')

    tmin, tmax = np.floor(t[0]), np.floor(t[-1])
    t_binned = np.arange((tmin-tmin%10)+5, (tmax-tmax%10)+6, 10)

    bins = np.searchsorted(t_binned-5, t, side='right')

    t_binned = t_binned[np.bincount(bins-1).astype(np.bool_)]

    cut_first, cut_last = False, False
    if force_t_range:
        if t_binned[0] < t[0]:
            t_binned = t_binned[1:]
            cut_first = True
        if t_binned[-1] > t[-1]:
            t_binned = t_binned[:-1]
            cut_last = True

    return {'t_binned': t_binned, 'bins': bins,
            'cut_first': cut_first, 'cut_last': cut_last}


###############################################################################


@nu.njit
def get_npnanmean(v):
    return np.nanmean(v)

def bin_y_of_t(v, bin_info,
                  vmiss=np.nan,
                  return_type='arit_mean',
                  use_numba=True):
    """
    use 'bins' output of function "bin_time" or "bin_time_10s"
        to bin a variable 'v' that depends on a variable t.
    """
    if not isinstance(v, np.ndarray):
        raise TypeError('Please pass np.ndarray to function.')

    if not any([v.dtype == np.dtype(t) for t in ('int16', 'int32', 'int64',
                                                 'float16', 'float32', 'float64')]):
        raise TypeError('Please pass valid dtype, int or float.')

    if 'mask' in bin_info.keys():
        mask = bin_info['mask']
    else:
        mask = np.ones(v.shape).astype(np.bool_)

    _v = deepcopy(v)

    if any([_v.dtype == np.dtype(t) for t in ('int16', 'int32', 'int64')]):
        _v = np.ma.array(_v) # use a masked array if type is int (NaN not supported)
        _v.mask = ~mask
        _v[_v==vmiss] = np.ma.masked

    else:
        _v[_v==vmiss] = np.nan
        _v[~mask] = np.nan

    v_binned = []
    v_dtype = _v.dtype
    vd_bins = bin_info['bins']

    if return_type == 'arit_mean':
        if use_numba:
            v_binned = [get_npnanmean(_v[vd_bins == bin_no]) for bin_no in np.unique(vd_bins)]
        else:
            v_binned = [np.nanmean(_v[vd_bins == bin_no]) for bin_no in np.unique(vd_bins)]
    elif return_type == 'mean_day_frac':
        if use_numba:
            v_binned = [mean_day_frac(_v[vd_bins == bin_no]) for bin_no in np.unique(vd_bins)]
        else:
            v_binned = [mean_day_frac(_v[vd_bins == bin_no], use_numba=False) for bin_no in np.unique(vd_bins)]
    elif return_type == 'mean_angle':
        if use_numba:
            v_binned = [mean_angle_numba(_v[vd_bins == bin_no]) for bin_no in np.unique(vd_bins)]
        else:
            v_binned = [mean_angle(_v[vd_bins == bin_no]) for bin_no in np.unique(vd_bins)]


    if any([v_dtype == np.dtype(t) for t in ('float16', 'float32', 'float64')]):
        result = np.array(v_binned)
    else:
        result =  np.rint(v_binned).astype(v_dtype)

    if bin_info['cut_first']:
        result = result[1:]
    if bin_info['cut_last']:
        result = result[:-1]

    return result


###############################################################################


def bin_info_xvar(xvar, dx,
                  to_closest=False, apply_round=True,
                  output='float', outfmt="%.2f"):
    """
    calculate bins for a given input vector "xvar".
    returns dictionary with bins and additional info like indices.
    dx: specifies the difference between each bin, i.e. the bin size.
    to_closest: if set to a number, the bin middle will be the closest decimal
        number (10^1 digit), e.g. to_closest = 5 will result in every bin
        ending with ...5.0 only works if dx is 10.
    apply_round: (only if to_closest is set) round xmin/xmax before calculating
        the bins.
    output='string', outfmt="%.2f": gives formatted output. float is default.
    """
    if not isinstance(xvar, list):
        raise ValueError("xvar must be a list")

    if not isinstance(xvar[0], float):
        xvar = list(map(float, xvar))

    # s_inc = strictly_increasing(xvar)
    if not strictly_increasing(xvar):
        raise ValueError("xvar must be strictly increasing")

    x0, xmin = xvar[0], xvar[0]
    x1, xmax = xvar[-1], xvar[-1]

    if to_closest and dx == 10:
        if apply_round:
            x0, xmin = round(x0), round(xmin)
            x1, xmax = round(x1), round(xmax)
        if (to_closest - (x0 % dx)) < 0:  # x0 greater "to_closest"
            xmin = x0 + (to_closest - (x0 % dx)) + dx
        if (to_closest - (x0 % dx)) > 0:  # x0 smaller "to_closest"
            xmin = x0 + (to_closest - (x0 % dx))
        if (to_closest - (x1 % dx)) < 0:  # x1 greater "to_closest"
            xmax = x1 + (to_closest - (x1 % dx))
        if (to_closest - (x1 % dx)) > 0:  # x1 smaller "to_closest"
            xmax = x1 + (to_closest - (x1 % dx) - dx)

    bin_info = {}
    bin_info['nbins'] = floor((xmax-xmin)/dx) + 1
    bin_info['bins'] = [xmin + i*dx for i in range(bin_info['nbins'])]
    bin_info['bin_vals'] = []
    bin_info['bin_ix'] = []
    bin_info['n_in_bin'] = []

    j_next = 0
    for x in bin_info['bins']:
        bin_val, bin_ix = [], []
        lowerlim, upperlim = x-dx/2, x+dx/2
        for j in range(j_next, len(xvar)):
            if xvar[j] >=lowerlim and xvar[j] < upperlim:
                bin_val.append(xvar[j])
                bin_ix.append(j)
            else:
                j_next = j
                break
        bin_info['bin_vals'].append(bin_val)
        bin_info['bin_ix'].append(bin_ix)
        bin_info['n_in_bin'].append(len(bin_ix))

    if output == 'string':
        bin_info['bins'] = (
            [outfmt % element for element in bin_info['bins']])

    return bin_info


###############################################################################


def bin_yvar(v, bin_info,
             no_val=999999,
             v_is_dayfrac=False,
             v_is_deg=False,
             calc_stat=True,
             output='float', outfmt="%.2f",
             exclude_noval=False):
    """
    apply bin_info_xvar output to bin a variable.
    """
    if isinstance(v, list) and isinstance(bin_info, dict):
        binned_var = {}
        binned_var['bin_vals'] = []
        binned_var['bin_mean'] = []
        binned_var['bin_median'] = []
        binned_var['bin_stddev'] = []

        for i in range(bin_info['nbins']):
            if bin_info['bin_vals'][i]:  # bin contains values
                if len(bin_info['bin_ix'][i]) == 1:  # bin contains only 1 value
                    binned_var['bin_vals'].append(
                        float(v[bin_info['bin_ix'][i][0]]))
                    binned_var['bin_mean'].append(binned_var['bin_vals'][-1])
                    binned_var['bin_median'].append(no_val)
                    binned_var['bin_stddev'].append(no_val)
                else:  # bin contains more than one value
                    binned_var['bin_vals'].append(v[bin_info['bin_ix'][i][0]:bin_info['bin_ix'][i][-1]+1])
                    binned_var['bin_vals'][-1] = (
                        [float(val) for val in binned_var['bin_vals'][-1]])

                    if exclude_noval:  # exclude 'no value'
                        tmp = [val for val in binned_var['bin_vals'][-1] if val != no_val]
                    else:
                        tmp = binned_var['bin_vals'][-1]

                    if calc_stat:
                        if not len(tmp) > 1:
                            binned_var['bin_mean'].append(no_val)
                            binned_var['bin_median'].append(no_val)
                            binned_var['bin_stddev'].append(no_val)
                        else:
                            if not v_is_dayfrac and not v_is_deg:
                                binned_var['bin_mean'].append(stat.mean(tmp))
                                binned_var['bin_median'].append(stat.median(tmp))
                                binned_var['bin_stddev'].append(stat.stdev(tmp))
                            if v_is_dayfrac:
                                binned_var['bin_mean'].append(
                                    mean_day_frac(tmp))
                                binned_var['bin_median'].append(no_val)
                                binned_var['bin_stddev'].append(no_val)
                            if v_is_deg:
                                binned_var['bin_mean'].append(mean_angle(tmp))
                                binned_var['bin_median'].append(no_val)
                                binned_var['bin_stddev'].append(no_val)
                    else:
                        binned_var['bin_mean'].append(no_val)
                        binned_var['bin_median'].append(no_val)
                        binned_var['bin_stddev'].append(no_val)
            else:
                binned_var['bin_vals'].append([no_val])
                binned_var['bin_mean'].append(no_val)
                binned_var['bin_median'].append(no_val)
                binned_var['bin_stddev'].append(no_val)

        if output == 'string':
            if exclude_noval:
                binned_var['bin_mean'] = (
                    [outfmt % element if element != no_val else str(int(element))
                     for element in binned_var['bin_mean']])
            else:
                binned_var['bin_mean'] = (
                    [outfmt % element for element in binned_var['bin_mean']])

        return binned_var

    else:
        raise TypeError


###############################################################################


def bin_by_npreduceat(v: np.ndarray, nbins: int,
                      ignore_nan=True):
    """
    1D binning with numpy.add.reduceat.
    ignores NaN or INF by default (finite elements only).
    if ignore_nan is set to False, the whole bin will be NaN if 1 or more NaNs
        fall within the bin.
    """
    if not isinstance(v, np.ndarray):
        v = np.array(v)

    bins = np.linspace(0, v.size, nbins+1, True).astype(np.int)

    if ignore_nan:
        mask = np.isfinite(v)
        vn = np.where(~mask, 0, v)
        with np.errstate(invalid='ignore'):
            out = np.add.reduceat(vn, bins[:-1])/np.add.reduceat(mask, bins[:-1])
    else:
        out = np.add.reduceat(v, bins[:-1])/np.diff(bins)

    return out


###############################################################################


def get_list_blmean(vector, bl_sz, edges='cut_both', output='float',
                    outfmt="%.2f"):
    """
    calculate an "averaged" vector by taking the mean from a fixed number of
        elements per block.
    """

    if isinstance(vector, list):
        mod = len(vector) % bl_sz
        if edges == 'cut_both':
            ix0 = floor(mod/2)
            ix1 = len(vector) - (mod - floor(mod/2))
        if edges == 'cut_beg':
            ix0 = mod-1
            ix1 = -1
        if edges == 'cut_end':
            ix0 = 0
            ix1 = mod * -1

        vector = vector[ix0:ix1]

        if isinstance(vector[0], date):
            result = []
            tlist = vector[0:bl_sz]
            tmp = sum(map(datetime.timestamp, tlist))/bl_sz
            result.append(datetime.fromtimestamp(tmp))
            for i in range(1, int(len(vector)/bl_sz)):
                tlist = vector[bl_sz*i:bl_sz*(i+1)]
                tmean = sum(map(datetime.timestamp, tlist))/bl_sz
                tmean = datetime.fromtimestamp(tmean)
                result.append(tmean)
        else:
            try:
                vector = [float(element) for element in vector]
            except ValueError:
                result = None
            else:
                result = [sum(vector[0:bl_sz])/bl_sz]
                for i in range(1, int(len(vector)/bl_sz)):
                    result.append(sum(vector[bl_sz*i:bl_sz*(i+1)])/bl_sz)

                if output == 'string':
                    result = [outfmt % element for element in result]

                if output == 'int':
                    result = [int(element) for element in result]

        return result


###############################################################################


def moving_avg(v, N):
    """
    simple moving average
    """
    s, m_avg = [0], []
    for i, x in enumerate(v, 1):
        s.append(s[i-1] + x)
        if i >= N:
            avg = (s[i] - s[i-N])/N
            m_avg.append(avg)
    return m_avg


###############################################################################


def np_mvg_avg(v, N, ip_ovr_nan=False, mode='same', edges='expand'):
    """
    moving average based on numpy convolution function.
        ip_ovr_nan: interpolate linearly using finite elements of v
        edges='expand': in case of mode='same', convolution gives false results
                        ("running-in effect") at edges. account for this by
                        simply expanding the Nth value to the edges.
    performance: faster by factor of 5-6 compared to pd_mvg_avg.
    """
    N = int(N)

    if ip_ovr_nan:
        x = np.linspace(0, len(v)-1, num=len(v))
        fip = interp1d(x[np.isfinite(v)], v[np.isfinite(v)], kind='linear',
                       bounds_error=False, fill_value='extrapolate')
        v = fip(x)

    m_avg = np.convolve(v, np.ones((N,))/N, mode=mode)

    if edges=='expand':
        m_avg[:N-1], m_avg[-N-1:] = m_avg[N], m_avg[-N]

    return m_avg


###############################################################################


def pd_mvg_avg(v, N, ip_gaps=False, min_periods=1):
    """
    moving average for numpy vector using pandas dataframe rolling function.
        NOTE: automatically skips NaN (forms averages over windows with <N),
              unless minimum number of values in window is exceeded.
        min_periods: minimum number of values in averaging window.
        ip_gaps: interpolate linearly using finite elements of v.
    """
    N, min_periods = int(N), int(min_periods)

    min_periods = 1 if min_periods < 1 else min_periods

    df = pd.DataFrame({ 'v' : v })
    df['rollmean'] = df['v'].rolling(int(N), center=True,
                                     min_periods=min_periods).mean()
    if ip_gaps:
        df['ip']  = df['rollmean'].interpolate()
        return np.array(df['ip'])

    return np.array(df['rollmean'])


###############################################################################
