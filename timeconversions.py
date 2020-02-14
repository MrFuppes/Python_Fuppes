r"""
Created on Mon Jul 16 16:01:24 2018

@author: F. Obersteiner, florian\obersteiner\\kit\edu
"""
from datetime import datetime, timedelta, timezone
import numpy as np


### HELPERS ###################################################################


def to_list(parm, is_scalar=False):
    """
    convert input "parm" to a Python list.
    if "parm" is a scalar, return value "is_scalar" will be True.
    """
    if isinstance(parm, str): # check this first: don't call list() on a string
        parm, is_scalar = [parm], True
    elif not isinstance(parm, (list, np.ndarray)):
        try:
            parm = list(parm) # call list() first in case parm is np.ndarray
        except TypeError: # will e.g. raised if parm is a float
            parm = [parm]
        is_scalar = True
    return parm, is_scalar


### MAIN FUNCTIONS ############################################################


def timestring_2_mdns(timestring,
                      tsfmt: str = "%Y-%m-%d %H:%M:%S.%f",
                      ymd: tuple = None):
    """
    convert a UTC timestring to seconds since midnight (float).
    (!) timestring is assumed to be in UTC / %z is ignored (!)

    Parameters
    ----------
    timestring : str, list of str or np.ndarray with dtype str.
        timestamp given as string.
    tsfmt : str, optional
        timestring format. The default is "%Y-%m-%d %H:%M:%S.%f".
    ymd : tuple, optional
        starting date as tuple of integers; (year, month, day).
        The default is None.

    Returns
    -------
    float; scalar or list of float
        seconds since midnight for the given timestring(s).

    """
    timestring, ret_scalar = to_list(timestring)

    dt = [datetime.strptime(s, tsfmt) for s in timestring]
    dt = [s.replace(tzinfo=timezone.utc) for s in dt]
    if ymd:  # [yyyy,m,d] given, take that as starting point
        t0 = (datetime(year=ymd[0], month=ymd[1], day=ymd[2],
                       hour=0, minute=0, second=0, microsecond=0,
                       tzinfo=timezone.utc))
    else:  # use date from timestring as starting point
        t0 = dt[0].replace(hour=0, minute=0, second=0, microsecond=0)

    mdns = [(s - t0).total_seconds() for s in dt]

    return mdns[0] if ret_scalar else mdns


###############################################################################


def datetimeobj_2_mdns(dt_obj,
                       ix0_ix_t0: bool = False,
                       t0_set: tuple = False):
    """
    convert a Python datetime object (or list/array of ...) to seconds
    after midnight.

    Parameters
    ----------
    dt_obj : datetime object or list/array of datetime objects
        the datetime to be converted to seconds after midnigt.
    ix0_ix_t0 : bool, optional
        first entry of dt_obj list/array defines start date.
        The default is False.
    t0_set : tuple of int, optional
        custom start date given as (year, month, day). The default is False.

    Returns
    -------
    float; scalar or list of float
        seconds after midnight for the given datetime object(s).

    """
    dt_obj, ret_scalar = to_list(dt_obj)

    if t0_set:
        t0 = datetime(t0_set[0], t0_set[1], t0_set[2], tzinfo=dt_obj[0].tzinfo)
    elif ix0_ix_t0:
        t0 = dt_obj[0]

    if ix0_ix_t0 or t0_set:
        result = ([(x-t0.replace(hour=0, minute=0, second=0, microsecond=0))
                   .total_seconds() for x in dt_obj])
    else:
        result = ([(x-x.replace(hour=0, minute=0, second=0, microsecond=0))
                   .total_seconds() for x in dt_obj])

    return result[0] if ret_scalar else result


###############################################################################


def posixts_2_mdns(posixts,
                   ymd: tuple = None):
    """
    convert a POSIX timestamp (or list/array of ...) to seconds after midnight.
    (!) posixts is assumed to be a UTC timestamp (!)

    Parameters
    ----------
    posixts : float, list of float or np.ndarray with dtype float.
        the posix timestamp to be converted to seconds after midnight.
    ymd : tuple of int, optional
        define starting data as tuple of integers (year, month, day).
        The default is None, which means the reference date is the day of the
        timestamp.

    Returns
    -------
    float; scalar or list of float
        seconds after midnight for the given POSIX timestamp(s).

    """
    posixts, ret_scalar = to_list(posixts)

    if ymd:  # [yyyy,m,d] given, take that as starting point
        t0 = (datetime(year=ymd[0], month=ymd[1], day=ymd[2],
                       hour=0, minute=0, second=0, microsecond=0,
                       tzinfo=timezone.utc))

    dt_obj = [datetime.utcfromtimestamp(ts) for ts in posixts]
    dt_obj = [d.replace(tzinfo=timezone.utc) for d in dt_obj]
    if not ymd: # take date of first entry as starting point
        t0 = dt_obj[0].replace(hour=0, minute=0, second=0, microsecond=0)
    ts = [(s - t0).total_seconds() for s in dt_obj]

    return ts[0] if ret_scalar else ts


###############################################################################


def mdns_2_datetimeobj(mdns,
                       ref_date,
                       posix: bool = False,
                       str_fmt: str = False):
    """
    convert seconds after midnight (or list/array of ...) to datetime object.

    Parameters
    ----------
    mdns : float, list of float or np.ndarray with dtype float.
        the seconds after midnight to be converted to datetime object(s).
    ref_date : tuple of int (year, month, day) or datetime object
        date that mdns refers to.
    posix : bool, optional
        return POSIX timestamp(s). The default is False.
    str_fmt : str, optional
        Format for datetime.strftime, e.g. "%Y-%m-%d %H:%M:%S.%f"
        If provided, output is delivered as formatted string. POSIX must
            be False in that case, or STR_FMT is overridden (evaluated last).
        The default is False.

    Returns
    -------
    datetime object or float (POSIX timestamp)
        ...for the given seconds after midnight.

    """
    mdns, ret_scalar = to_list(mdns)

    if not isinstance(mdns[0], (float, np.float32, np.float64)):
        mdns = list(map(float, mdns))

    if isinstance(ref_date, (tuple, list)):
        ref_date = datetime(*ref_date)
    tz = ref_date.tzinfo

    posix_ts = []
    for t in mdns:
        days_off = t//86400
        dt_obj = ref_date + timedelta(days=days_off, seconds=t-86400*days_off)
        posix_ts.append(dt_obj.replace(tzinfo=tz))

    if posix:
        posix_ts = [x.timestamp() for x in posix_ts]
    elif str_fmt:
        offset = -3 if str_fmt.endswith("%f") else None
        posix_ts = [x.strftime(str_fmt)[:offset] for x in posix_ts]

    return posix_ts[0] if ret_scalar else posix_ts


###############################################################################


def daysSince_2_dtObj(daysSince, day0, tz=timezone.utc):
    """
    convert a floating point number "daysSince" to a datetime object.
    day0: datetime object, from when to count.
    """
    if not day0.tzinfo: # assume UTC by default
        day0 = day0.replace(tzinfo=tz)

    if isinstance(daysSince, (list, np.ndarray)):
        return [(day0 + timedelta(days=ds)).replace(tzinfo=tz) for ds in daysSince]
    return (day0 + timedelta(days=daysSince)).replace(tzinfo=tz)


###############################################################################


def timestring_2_utcts(timestring,
                       tsfmt: str = "%Y-%m-%d %H:%M:%S.%f"):
    """
    convert a non-localized timestring to utc timestamp.
    """
    t = datetime.strptime(timestring, tsfmt)
    return t.replace(tzinfo=timezone.utc).timestamp()


###############################################################################
