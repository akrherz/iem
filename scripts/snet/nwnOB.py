
import math

def sum(seq):
	def add(x,y): return x+y
	return reduce(add, seq, 0)

def uv(sped, dir):
  dirr = dir * math.pi / 180.00
  s = math.sin(dirr)
  c = math.cos(dirr)
  u = round(- sped * s, 2)
  v = round(- sped * c, 2)
  return u, v

def dir(u,v):
  if (v == 0):
    v = 0.000000001
  dd = math.atan(u / v)
  ddir = (dd * 180.00) / math.pi
 
  if (u > 0 and v > 0 ): # First Quad
    ddir = 180 + ddir
  elif (u > 0 and v < 0 ): # Second Quad
    ddir = 360 + ddir
  elif (u < 0 and v < 0 ): # Third Quad
    ddir = ddir
  elif (u < 0 and v > 0 ): # Fourth Quad
    ddir = 180 + ddir
                                                                                
  return math.fabs(ddir)

def drct2dirTxt(dir):
  dir = int(dir)
  if (dir >= 350 or dir < 13):
    return "N"
  elif (dir >= 13 and dir < 35):
    return "NNE"
  elif (dir >= 35 and dir < 57):
    return "NE"
  elif (dir >= 57 and dir < 80):
    return "ENE"
  elif (dir >= 80 and dir < 102):
    return "E"
  elif (dir >= 102 and dir < 127):
    return "ESE"
  elif (dir >= 127 and dir < 143):
    return "SE"
  elif (dir >= 143 and dir < 166):
    return "SSE"
  elif (dir >= 166 and dir < 190):
    return "S"
  elif (dir >= 190 and dir < 215):
    return "SSW"
  elif (dir >= 215 and dir < 237):
    return "SW"
  elif (dir >= 237 and dir < 260):
    return "WSW"
  elif (dir >= 260 and dir < 281):
    return "W"
  elif (dir >= 281 and dir < 304):
    return "WNW"
  elif (dir >= 304 and dir < 324):
    return "NW"
  elif (dir >= 324 and dir < 350):
    return "NNW"


class nwnOB:

	def __init__(self, stationID):
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
		if (self.valid == None or self.lvalid == None):
			return 0
		return int(self.valid - self.lvalid) / 60
		
	#________________________________________________________________
	def setGust(self, newGust):
# This is some logic to set the maximum wind speed.  A couple of
# things to note.
#		1. Sometimes the peak gust will come as an ob and then the MAX
#			Line will not make it in yet in time for the minute processing
#		2. The ob that generates the MAX is not gaurenteed to be in the feed

		if (self.valid == None):
			return 
#		if (self.maxSPED == None):
#			print "Site %s HAS INIT maxSPED: %s" % (self.stationID, newGust)
#			self.maxSPED = newGust
#			self.maxSPED_ts = self.valid
		if (newGust > self.maxSPED):
			#print "Site %s NEW maxSPED: %s" % (self.stationID, newGust)
			self.maxSPED = newGust
			self.maxSPED_ts = self.valid
		# Value is RESET for the next day!
		if (newGust < self.maxSPED):
			#print "Site %s RESET maxSPED: %s" % (self.stationID, newGust)
			self.maxSPED = newGust
			self.maxSPED_ts = self.valid
			self.windGustAlert = 0

#		if (self.sped != None and max(self.aSPED) > self.maxSPED):
#			print "Site %s sped has new maxSPED: %s old %s" \
#				% (self.stationID, max(self.aSPED), self.maxSPED)
#			self.maxSPED = max(self.aSPED)
#			self.maxSPED_ts = self.valid

	def avgWinds(self):
		if (len(self.aSPED) == 0):
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
		self.drctTxt = drct2dirTxt(self.drct)

