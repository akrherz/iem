"""Deleteme please"""
import math
from functools import reduce

from pyiem import util


def sum(seq):
    """HACK"""
    def add(x, y):
        return x+y
    return reduce(add, seq, 0)


def uv(sped, dir):
    """HACK"""
    dirr = dir * math.pi / 180.00
    s = math.sin(dirr)
    c = math.cos(dirr)
    u = round(- sped * s, 2)
    v = round(- sped * c, 2)
    return u, v


def dir(u, v):
    """HACK"""
    if v == 0:
        v = 0.000000001
    dd = math.atan(u / v)
    ddir = (dd * 180.00) / math.pi

    if u > 0 and v > 0:  # First Quad
        ddir = 180 + ddir
    elif u > 0 and v < 0:  # Second Quad
        ddir = 360 + ddir
    elif u < 0 and v < 0:  # Third Quad
        ddir = ddir
    elif u < 0 and v > 0:  # Fourth Quad
        ddir = 180 + ddir
    return math.fabs(ddir)


class nwnOB:
    """HACK!"""

    def __init__(self, stationID):
        """Constructor"""
        self.stationID = stationID
        self.valid = None
        self.lvalid = None
        self.aSPED = []
        self.sped = None
        self.aDrctTxt = []
        self.aDrct = []
        self.drct = None
        self.drctTxt = None

        self.tmpf = None
        self.maxTMPF = None
        self.minTMPF = None

        self.relh = None
        self.maxRELH = None
        self.minRELH = None
        self.srad = None
        self.maxSRAD = None
        self.minSRAD = None

        self.maxSPED = None
        self.maxSPED_ts = None
        self.maxDrctTxt = None

        self.windGustAlert = None

        self.maxLine = None
        self.minLine = None

    def sinceLastObInMinutes(self):
        """Duration"""
        if self.valid is None or self.lvalid is None:
            return 0
        return int((self.valid - self.lvalid).total_seconds()) / 60

    def setGust(self, newGust):
        # This is some logic to set the maximum wind speed.  A couple of
        # things to note.
        # 1. Sometimes the peak gust will come as an ob and then the MAX
        #    Line will not make it in yet in time for the minute processing
        # 2. The ob that generates the MAX is not gaurenteed to be in the feed
        if self.valid is None:
            return
#        if (self.maxSPED == None):
#            print "Site %s HAS INIT maxSPED: %s" % (self.stationID, newGust)
#            self.maxSPED = newGust
#            self.maxSPED_ts = self.valid
        if self.maxSPED is not None and newGust > self.maxSPED:
            # print "Site %s NEW maxSPED: %s" % (self.stationID, newGust)
            self.maxSPED = newGust
            self.maxSPED_ts = self.valid
        # Value is RESET for the next day!
        if self.maxSPED is not None and newGust < self.maxSPED:
            # print "Site %s RESET maxSPED: %s" % (self.stationID, newGust)
            self.maxSPED = newGust
            self.maxSPED_ts = self.valid
            self.windGustAlert = 0

#        if (self.sped != None and max(self.aSPED) > self.maxSPED):
#            print "Site %s sped has new maxSPED: %s old %s" \
#                % (self.stationID, max(self.aSPED), self.maxSPED)
#            self.maxSPED = max(self.aSPED)
#            self.maxSPED_ts = self.valid

    def avgWinds(self):
        """My wind averager"""
        if not self.aSPED:
            self.sped = None
            self.drct = None
            return
        self.sped = sum(self.aSPED) / len(self.aSPED)
        utot = 0
        vtot = 0
        for i in range(len(self.aSPED)):
            u, v = uv(self.aSPED[i], self.aDrct[i])
            utot += u
            vtot += v
        uavg = utot / len(self.aSPED)
        vavg = vtot / len(self.aSPED)
        self.drct = dir(uavg, vavg)
        self.drctTxt = util.drct2text(self.drct)
