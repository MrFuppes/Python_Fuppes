# -*- coding: utf-8 -*-
r"""
Created on Mon Nov 11 11:42:23 2019

@author: F. Obersteiner, florian\obersteiner\\kit\edu
"""

# --- Haversine distance / Numba njit'ed version ---
# --------------------------------------------------
from math import sin, cos, sqrt, atan2, radians
from numba import njit

@njit
def calc_latlon_dist(lat, lon):
    """
    calculate Haversine distance along lat/lon coordinates.
    """
    assert lat.shape[0] == lon.shape[0], "lat/lon must be of same length."
    R = 6373.0 # approximate radius of earth in km
    dist = 0.

    for j in range(lat.shape[0]-1):
        lat0, lat1 = radians(lat[j]), radians(lat[j+1])
        lon0, lon1 = radians(lon[j]), radians(lon[j+1])

        dlon = lon1 - lon0
        dlat = lat1 - lat0

        a = sin(dlat / 2)**2 + cos(lat0) * cos(lat1) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        dist += R * c

    return dist
# --------------------------------------------------
    

# --- geopy geodesic distance ---
# -------------------------------   
from geopy import distance
def calc_latlon_dist_geopy(lat, lon):
    """
    calculate geodesic distance along lat/lon coordinates using geopy module.
    """
    assert lat.shape[0] == lon.shape[0], "lat/lon must be of same length."
    dist = 0.
    for j in range(lat.shape[0]-1):
        dist += distance.geodesic((lat[j], lon[j]), (lat[j+1], lon[j+1]),
                                  ellipsoid='WGS-84').km
    return dist
#--------------------------------
    

if __name__ == '__main__':
    
    import numpy as np
    
    LAT = np.array([52.2296756, 52.406374])
    LON = np.array([21.0122287, 16.9251681])
    d = calc_latlon_dist(LAT, LON)
    assert np.isclose(d, 278.546)
