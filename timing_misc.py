# -*- coding: utf-8 -*-
r"""
Created on Thu Dec 20 11:18:46 2018

@author: F. Obersteiner, florian\obersteiner\\kit\edu
"""
import math
from datetime import date

###############################################################################
def print_progressbar(iteration, total,
                      prefix='', suffix='', decimals=1, length=100, fill='█'):
    """
    https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    access: 2018-12-20
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    progBar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, progBar, percent, suffix), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print('\n')
##
## Sample Usage
##
#
#from time import sleep
#
## A List of Items
#items = list(range(0, 57))
#l = len(items)
#
## Initial call to print 0% progress
#printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
#for i, item in enumerate(items):
#    # Do stuff...
#    sleep(0.1)
#    # Update Progress Bar
#    printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)

###############################################################################
def get_DoY(date_ts):
    """
    input: date timestamp (date_ts, datetime object)
    returns: day of year (int)
    use for: general purpose
    """
    return (date(date_ts.year, date_ts.month, date_ts.day) -
            date(date_ts.year, 1, 1)).days

###############################################################################
def get_EoT(date_ts):
    """
    input: date timestamp (date_ts)
    returns: equation of time (float)
    use for: calculation of local solar time
    """
    B = (360/365)*(get_DoY(date_ts)-81)
    return 9.87 * math.sin(2.*B) - 7.53 * math.cos(B) - 1.5 * math.sin(B)

###############################################################################
def get_LSTdayFrac(longitude, tz_offset, EoT, days_delta, time_delta):
    """
    input:
        longitude: -180 to +180 degrees west to east, float
        tz_offset: timezone offset in hours, float
        EoT: equation of time for selected date, float
        days_delta: days since reference date, float
        time_delta: current time as days since reference date, float
    returns:
        local solar time as day fraction (float, 0-1)
    """
    LSTM = 15. * tz_offset # Local Standard Time Meridian
    t_corr = (4. * (longitude - LSTM) + EoT)/60./24. # [d]
    LST_frac = (time_delta + tz_offset/24. - days_delta) + t_corr
    if LST_frac > 1.:
        LST_frac -= math.floor(LST_frac)
    return LST_frac
