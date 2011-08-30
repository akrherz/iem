# Library of help functions
import math

def uv(sped,dir):
    """
    Compute the u and v components of the wind 
    @param wind speed in whatever units
    @param dir wind direction with zero as north
    @return u and v components
    """
    dirr = dir * math.pi / 180.00
    s = math.sin(dirr)
    c = math.cos(dirr)
    u = round(- sped * s, 2)
    v = round(- sped * c, 2)
    return u, v


def c2f(thisc):
    return (9.00/5.00 * float(thisc)) + 32.00

def k2f(thisk):
    return (9.00/5.00 * (float(thisk) - 273.15)) + 32.00