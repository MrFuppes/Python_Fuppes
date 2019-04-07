r"""
Created on Mon Jul 16 16:01:24 2018

@author: F. Obersteiner, florian\obersteiner\\kit\edu
"""
from datetime import datetime, timedelta, timezone
import numpy as np


###############################################################################


def timestring_2_mdns(timestring, tsfmt="%Y-%m-%d %H:%M:%S.%f", ymd=None):
    """
    convert a time string to seconds since midnight (float).
    UTC prescribed. Cannot be used with time strings that contain tz info.
    ISO-8601 date string format: '%Y-%m-%dT%H:%M:%S%z'.
    ymd: define starting data as list of integers; [year, month, day]
    """
    if (isinstance(timestring, list) or
            isinstance(timestring, (np.ndarray, np.generic))):
        dt = [datetime.strptime(s, tsfmt) for s in timestring]
        dt = [s.replace(tzinfo=timezone.utc) for s in dt]
        if ymd:  # [yyyy,m,d] given, take that as starting point
            t0 = (datetime(year=ymd[0], month=ymd[1], day=ymd[2],
                           hour=0, minute=0, second=0, microsecond=0,
                           tzinfo=timezone.utc))
        else:  # use date from timestring as starting point
            t0 = dt[0].replace(hour=0, minute=0, second=0, microsecond=0)
        return ([(s - t0).total_seconds() for s in dt])
    else:
        dt = datetime.strptime(timestring, tsfmt)
        dt = dt.replace(tzinfo=timezone.utc)
        if ymd:  # [yyyy,m,d] given, take that as starting point
            t0 = (datetime(year=ymd[0], month=ymd[1], day=ymd[2],
                           hour=0, minute=0, second=0, microsecond=0,
                           tzinfo=timezone.utc))
        else:  # use date from timestring as starting point
            t0 = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        return (dt - t0).total_seconds()


###############################################################################


def datetimeobj_2_mdns(dt_obj, ix0_ix_t0=False, t0_set=False):
    """
    convert a python datetime object (or list of datetime objects) to seconds
    after midnight. Year/month/day are not returned.
    Action is independent of time zone (non-aware dt_obj).
    ix0_ix_t0: first entry of dt_obj list contains the starting date.
    t0_set: supply info about starting date as [year, month, day].
    """
    if (isinstance(dt_obj, list) or
            isinstance(dt_obj, (np.ndarray, np.generic))):
        if ix0_ix_t0 or t0_set:
            if ix0_ix_t0:
                t0 = dt_obj[0]
            if t0_set:
                t0 = datetime(t0_set[0], t0_set[1], t0_set[2])
                t0 = t0.replace(tzinfo=timezone.utc)

            result = ([(x-t0.replace(hour=0, minute=0, second=0, microsecond=0))
                       .total_seconds() for x in dt_obj])
        else:
            result = ([(x-x.replace(hour=0, minute=0, second=0, microsecond=0))
                       .total_seconds() for x in dt_obj])
        return result
    else:
        return ((dt_obj -
                 dt_obj.replace(hour=0, minute=0, second=0, microsecond=0))
                .total_seconds())


###############################################################################


def posixts_2_mdns(posixts, ymd=None):
    """
    convert a python/POSIX timestamp (or list) to seconds
        after midnight. Year/month/day are not returned.
    ymd: define starting data as list of integers; [year, month, day]
    (!) input variable must be a UTC timestamp
    """
    if ymd:  # [yyyy,m,d] given, take that as starting point
        t0 = (datetime(year=ymd[0], month=ymd[1], day=ymd[2],
                       hour=0, minute=0, second=0, microsecond=0,
                       tzinfo=timezone.utc))

    if (isinstance(posixts, list) or
            isinstance(posixts, (np.ndarray, np.generic))):
        dt_obj = [datetime.utcfromtimestamp(ts) for ts in posixts]
        dt_obj = [d.replace(tzinfo=timezone.utc) for d in dt_obj]
        if not ymd: # take date of first entry as starting point
            t0 = dt_obj[0].replace(hour=0, minute=0, second=0, microsecond=0)

        return ([(s - t0).total_seconds() for s in dt_obj])

    else:
        dt_obj = datetime.utcfromtimestamp(posixts)
        dt_obj = dt_obj.replace(tzinfo=timezone.utc)
        if not ymd:
            t0 = dt_obj.replace(hour=0, minute=0, second=0, microsecond=0)

        return (dt_obj - t0).total_seconds()


###############################################################################


def mdns_2_datetimeobj(mdns, year, month, day, posix=False,
                       str_fmt=False):
    """
    convert seconds after midnight to python datetime object (single value or
        list) for a given year, month and day.
    (!) UTC is assumed!
    POSIX: if set to True, the corresponding POSIX timestamp is returned.
    STR_FMT: if provided, output is delivered as formatted string. POSIX must
        be False in that case, otherwise STR_FMT is overridden.
    """
    if (isinstance(mdns, list) or isinstance(mdns, (np.ndarray))):
        if not isinstance(mdns[0], float):
            mdns = list(map(float, mdns))
        date_zero = datetime(year=year, month=month, day=day,
                             tzinfo=timezone.utc)
        pytimest = []
        for t in mdns:
            if t/86400 > 1:
                days_off = int(t/86400)
                pytimest.append(date_zero + timedelta(days=days_off,
                                                      seconds=t-86400*days_off))
            else:
                pytimest.append(date_zero + timedelta(seconds=t))

        pytimest = [p.replace(tzinfo=timezone.utc) for p in pytimest]

        if posix:
            pytimest = [x.timestamp() for x in pytimest]

        if not posix and str_fmt:
            if "%f" in str_fmt:
                pytimest = [x.strftime(str_fmt)[:-3] for x in pytimest]
            else:
                pytimest = [x.strftime(str_fmt) for x in pytimest]

    else:
        if mdns/86400 > 1:
            days_off = int(mdns/86400)
            pytimest = (datetime(year=year, month=month, day=day) +
                        timedelta(days=int(mdns/86400), seconds=mdns-86400*days_off))
        else:
            pytimest = (datetime(year=year, month=month, day=day) +
                        timedelta(seconds=mdns))

        pytimest = pytimest.replace(tzinfo=timezone.utc)

        if posix:
            pytimest = pytimest.timestamp()

        if not posix and str_fmt:
            if "%f" in str_fmt:
                pytimest = pytimest.strftime(str_fmt)[:-3]
            else:
                pytimest = pytimest.strftime(str_fmt)

    return pytimest


###############################################################################


def daysSince_2_dtObj(daysSince, day0, tz=timezone.utc):
    """
    convert a floating point number "daysSince" to a datetime object.
    day0: datetime object, from when to count.
    """
    if not day0.tzinfo:
        day0 = day0.replace(tzinfo=tz)

    if (isinstance(daysSince, list) or isinstance(daysSince, (np.ndarray))):
        result = [(day0 + timedelta(days=ds)).replace(tzinfo=tz)
                  for ds in daysSince]
    else:
        result = (day0 + timedelta(days=daysSince)).replace(tzinfo=tz)

    return result


###############################################################################
