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

def f2c(thisf):
    return 5.00/9.00 * (thisf - 32.00)

def c2f(thisc):
    return (9.00/5.00 * thisc) + 32.00

def k2f(thisk):
    return (9.00/5.00 * (thisk - 273.15)) + 32.00

def metar_tmpf(tmpf):
    """
    Convert a temperature in F to something metar wants
    """
    if tmpf is None:
        return 'MM'
    tmpc = f2c( tmpf )
    if tmpc < 0:
        return 'M%02.0f' % (0 - tmpc,)
    return '%02.0f' % (tmpc,)

def metar_tmpf_tgroup(tmpf):
    """
    Convert a temperature in F to something metar wants
    """
    if tmpf is None:
        return '////'
    tmpc = f2c( tmpf )
    if tmpc < 0:
        return '1%03.0f' % (0 - (tmpc*10.0),)
    return '0%03.0f' % ((tmpc*10.0),)