# -*- coding: utf-8 -*-
r"""
Created on Mon Nov 11 11:42:23 2019

@author: F. Obersteiner, florian\obersteiner\\kit\edu
"""

from math import sin, cos, sqrt, atan2, radians
from numba import njit

@njit
def calc_latlon_dist(lat, lon):
    """
    calculate a distance along a lat/lon vector
    """
    R = 6373.0 # approximate radius of earth in km
    dist = 0.

    for j in range(lat.shape[0]-1):
        lat0 = radians(lat[j])
        lat1 = radians(lat[j+1])
        lon0 = radians(lon[j])
        lon1 = radians(lon[j+1])

        dlon = lon1 - lon0
        dlat = lat1 - lat0

        a = sin(dlat / 2)**2 + cos(lat0) * cos(lat1) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        dist += R * c

    return dist