# -*- coding: utf-8 -*-
r"""
Created on Wed Oct 17 10:09:50 2018

@author: F. Obersteiner, florian\obersteiner\\kit\edu
"""

from math import acos, cos, degrees, radians, sin
from datetime import datetime
from pysolar.solar import get_altitude


###############################################################################


# define triogonometry with degrees
cos2 = lambda x: cos(radians(x))
sin2 = lambda x: sin(radians(x))
acos2 = lambda x: degrees(acos(x))

def sza(UTC=datetime.utcnow(), latitude=52.37, longitude=9.72):
    '''
    Returns the solar zenith angle (in degree)

    UTC         (as datetime.datetime Object)
    longitude   (in degree)
    latitude    (in degree)

    Default values: Hannover, Germany

    Code adapted from https://www.python-forum.de/viewtopic.php?t=21117
    (2018-10-17 8:10 UTC)
    '''

    # parameter
    day_of_year = UTC.timetuple().tm_yday
    leap_year_factor = (-0.375, 0.375, -0.125, 0.125)[UTC.year % 4]
    UTC_min = UTC.hour * 60. + UTC.minute + UTC.second / 60.
    J = 360. / 365. * (day_of_year + leap_year_factor + UTC_min / 1440.)

    # hour angle (using the time equation)
    average_localtime = UTC_min + 4 * longitude
    true_solar_time = (average_localtime + 0.0066 + 7.3525 * cos2(  J +  85.9)
                                                  + 9.9359 * cos2(2*J + 108.9)
                                                  + 0.3387 * cos2(3*J + 105.2))

    hour_angle = 15. * (720. - true_solar_time) / 60.

    # sun declination (using DIN 5034-2)
    declination = (0.3948 - 23.2559 * cos2(  J + 9.1 )
                          -  0.3915 * cos2(2*J + 5.4 )
                          -  0.1764 * cos2(3*J + 26.))

    # solar zenith angle
    return acos2( sin2(latitude) * sin2(declination) +
                  cos2(hour_angle) * cos2(latitude) * cos2(declination) )


###############################################################################


def sza_pysolar(UTC=datetime.utcnow(), latitude=52.37, longitude=9.72):
    """ use get_altitude function from pysolar package to compute SZA """
    return 90.-get_altitude(latitude, longitude, UTC)


###############################################################################
