# -*- coding: utf-8 -*-
r"""
Created on Thu Aug  9 09:46:55 2018

@author: F. Obersteiner, florian\obersteiner\\kit\edu
"""
import statistics as stat
from cmath import rect, phase
from math import radians, degrees, floor
from datetime import datetime, date

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

from monotonicity import strictly_increasing

###############################################################################


def mean_angle(deg):
    """
    result is degrees between -180 and +180
    """
    return degrees(phase(sum(rect(1, radians(d)) for d in deg)/len(deg)))

###############################################################################


def mean_day_frac(dfr):
    """
    use the mean_angle function to calculate a mean day fraction (0-1).
    the conversion to angle is neccessary since day changes cannot be
        calculated as arithmetic mean.
    """
    deg = [element*360 for element in dfr]
    deg_mean = degrees(phase(sum(rect(1, radians(d)) for d in deg)/len(deg)))
    if deg_mean < 0:  # account for mean degree between -180 and +180
        deg_mean += 360
    return deg_mean/360

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
    cumsum, m_avg = [0], []
    for i, x in enumerate(v, 1):
        cumsum.append(cumsum[i-1] + x)
        if i >= N:
            avg = (cumsum[i] - cumsum[i-N])/N
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
        ip_gaps: interpolate linearly using finite elements of v
    performance: slower by factor of 5-6 compared to np_mvg_avg.
    """
    N, min_periods = int(N), int(min_periods)
    if min_periods < 1:
        min_periods = 1

    df = pd.DataFrame({ 'v' : v })
    df['rollmean'] = df['v'].rolling(int(N), center=True,
                                     min_periods=min_periods).mean()
    if ip_gaps:
        df['ip']  = df['rollmean'].interpolate()
        m_avg = np.array(df['ip'])
    else:
        m_avg = np.array(df['rollmean'])

    return m_avg

###############################################################################


def bin_info_xvar(xvar, dx, to_closest=False, apply_round=True,
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
    output='string', outfmt="%.2f": gives formatted ouput. float is default.
    """
    bin_info = None
    if isinstance(xvar, list):
        if not isinstance(xvar[0], float):
            xvar = list(map(float, xvar))

        s_inc = strictly_increasing(xvar)

        x0, xmin = xvar[0], xvar[0]
        x1, xmax = xvar[-1], xvar[-1]

        if to_closest and dx == 10:
            if apply_round:
                x0, xmin = round(x0), round(xmin)
                x1, xmax = round(x1), round(xmax)
            if (to_closest - (x0 % 10)) < 0:  # x0 greater "to_closest"
                xmin = x0 + (to_closest - (x0 % 10)) + 10
            if (to_closest - (x0 % 10)) > 0:  # x0 smaller "to_closest"
                xmin = x0 + (to_closest - (x0 % 10))
            if (to_closest - (x1 % 10)) < 0:  # x1 greater "to_closest"
                xmax = x1 + (to_closest - (x1 % 10))
            if (to_closest - (x1 % 10)) > 0:  # x1 smaller "to_closest"
                xmax = x1 + (to_closest - (x1 % 10) - 10)

        bin_info = {}
        bin_info['nbins'] = floor((xmax-xmin)/dx) + 1
        bin_info['bins'] = [xmin + i*dx for i in range(bin_info['nbins'])]
        bin_info['bin_vals'] = []
        bin_info['bin_ix'] = []
        bin_info['n_in_bin'] = []

        j_next = 0
        for x in bin_info['bins']:
            bin_val = []
            bin_ix = []
            for j in range(j_next, len(xvar)):
                if xvar[j] >= x-dx/2 and xvar[j] < x+dx/2:
                    bin_val.append(xvar[j])
                    bin_ix.append(j)
                if s_inc and xvar[j] >= x+dx/2:  # exit loop if x is out of bin
                    j_next = j                   # only allowed if xvar is
                    break                        # strictly increasing
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

    binned_var = None
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
                    binned_var['bin_vals'].append(
                        v[(bin_info['bin_ix'][i])[0]:(bin_info['bin_ix'][i])[-1]+1])
                    binned_var['bin_vals'][-1] = (
                        [float(val) for val in binned_var['bin_vals'][-1]])

                    if exclude_noval:  # exclude 'no value'
                        tmp = [val for val in binned_var['bin_vals']
                               [-1] if val != no_val]
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
                                binned_var['bin_median'].append(
                                    stat.median(tmp))
                                binned_var['bin_stddev'].append(
                                    stat.stdev(tmp))
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

###############################################################################


def bin_by_npreduceat(v, nbins):
    bins = np.linspace(0, len(v), nbins+1, True).astype(np.int)
    binned_v = np.add.reduceat(v, bins[:-1]) / np.diff(bins)
    return binned_v

###############################################################################
