# Something to store constants of our effort
import numpy
import math
import mx.DateTime

# Iowa Extents in EPSG:26915
# 202,054 4,470,570 736,852 4,822,687
# Or! 352km by 535km
# So for ~25km, we'd want 23x and 15y
#SOUTH =  40.1356
#WEST  = -96.8732
#NORTH =  43.7538
#EAST  = -89.6463
# Midwest Extents in EPSG:2163
# -312,635 -888,815 1,627,432 498,098
# Or 2,339km by 1,388km 
# So for ~25km, we'd want 94x and 55y
SOUTH = 37.0
WEST = -104.0
NORTH = 49.0
EAST = -80.5

#NX = 24
#NY = 16
NX = 94
NY = 55

DX = (EAST-WEST)/float(NX-1)
DY = (NORTH-SOUTH)/float(NY-1)

XAXIS = numpy.arange(WEST, EAST + DX, DX)
YAXIS = numpy.arange(SOUTH, NORTH + DY -0.01, DY)

def hour_idx(ts):
    """
    Return the netCDF hourly grid index value for this timestamp
    @param ts mx.DateTime object
    @return int index value
    """
    basets = mx.DateTime.DateTime(ts.year,1,1,0,0)
    return int((ts - basets).hours)

def k2f(ar):
    """
    Convert numpy array ar from Kelvin to Fahrenhit
    """
    return (ar - 273.15) * 9.0/5.0 + 32.0

def f2k(ar):
    """
    Convert numpy array ar from Fahrenhit to Kelvin
    """
    return (5.0/9.0 * (ar - 32.00 )) + 273.15

def find_ij(lon, lat):
    """
    Return the i,j grid index for a given lon lat pair
    """
    mindist = 100000
    for j in range(len(YAXIS)):
        for i in range(len(XAXIS)):
            dist = math.sqrt( (XAXIS[i] - lon)**2 + (YAXIS[j] - lat)**2 )
            if dist < mindist:
                mindist = dist
                mini = i
                minj = j

    return mini, minj
