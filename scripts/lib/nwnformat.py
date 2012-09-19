# Class library for the NWN Baron format
#  OO is fun!
#  Daryl Herzmann 16 May 2003
# 18 Nov 2003	Fix a very stupid error in parseLineRT :(
#  5 Jan 2004	Forgot what a pleasure temperatures below zero are.  For 
#		whatever reason, the values from some KELO sites are reported
#		differently "0-5F".  This is not good
# 21 Oct 2004	Support wind averaging

# A 058  09:23 05/16/03 ESE 08MPH 050K 460F 057F 088% 30.02R 00.01"D 02.79"M 00.00"R
# H 025   Max  05/16/03 SE  08MPH 057K 460F 057F 100% 30.04" 00.00"D 03.55"M 00.00"R
# K 072   Min  05/16/03 NE  00MPH 000K 075F 048F 083% 30.02" 00.00"D 02.53"M 00.00"R

import mx.DateTime
import re
import math
import traceback
import mesonet

def uv(sped, drct2):
  #print "SPED:", sped, type(sped), "DRCT2:", drct2, type(drct2)
  dirr = drct2 * math.pi / 180.00
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

  return int(math.fabs(ddir))


class nwnformat:

  def __init__(self, do_avg_winds=True):
    self.error = 0
    self.do_avg_winds = do_avg_winds

    self.sid = None
    self.ts = None
    self.avg_sknt = None
    self.avg_drct = None
    self.drct = None
    self.drctTxt = None
    self.avg_drctTxt = None
    self.sped = None
    self.rad = 0
    self.insideTemp = 460
    self.tmpf = None
    self.humid = None
    self.pres = None
    self.presTend = None
    self.pDay = 0.00
    self.pMonth = 0.00
    self.pRate = 0.00
    self.dwpf = None
    self.feel = None

    self.nhumid = 0
    self.xhumid = 0

    self.npres = 0
    self.xpres = 0

    self.xtmpf = None
    self.ntmpf = None
    self.xsped = None
    self.xdrct = None
    self.xdrctTxt = None
    self.xsrad = None

    self.strMaxLine = None
    self.strMinLine = None

    self.aSknt = []
    self.aDrct = []

  def avgWinds(self):
    if (len(self.aSknt) == 0):
      self.sped = None
      self.drct = None
      return
    self.avg_sknt = int(float(sum(self.aSknt)) / float(len(self.aSknt)))
    utot = 0
    vtot = 0
    for i in range(len(self.aSknt)):
      u, v = uv(self.aSknt[i], self.aDrct[i])
      if (self.aSknt[i] > self.xsped):
        self.xsped = self.aSknt[i] * 1.150
        self.xdrct = self.aDrct[i]
        self.xdrctTxt = mesonet.drct2dirTxt(self.aDrct[i])
      utot += u
      vtot += v
    uavg = utot / len(self.aSknt)
    vavg = vtot / len(self.aSknt)
    self.avg_drct = dir(uavg, vavg)
    self.avg_drctTxt = mesonet.drct2dirTxt(self.avg_drct)

    self.aSknt = []
    self.aDrct = []


  def parseLineRT(self, tokens):
    if (self.ts == None):
      self.ts = mx.DateTime.now()

    if (len(tokens) != 14):
      return
    lineType = tokens[2]
    if (lineType == "Max"):
       self.parseMaxLineRT(tokens)
    elif (lineType == "Min"):
       self.parseMinLineRT(tokens)
    else:
       self.ts = mx.DateTime.now()
       self.parseCurrentLineRT(tokens)


  def parseMaxLineRT(self, tokens):
    maxline = "found"
    self.xdrct = mesonet.txt2drct[tokens[4]]
    self.xdrctTxt = tokens[4]
    if (len(tokens[5]) >= 5):
      t = re.findall("([0-9]+)(MPH|KTS)", tokens[5])[0]
      if (t[1] == "MPH"):
        self.xsped = int(t[0])
      else:
        sknt = int(t[0])
        self.xsped = round( sknt * 1.1507, 0)

    if (len(tokens[6]) == 4):
      self.xsrad = int(re.findall("([0-9][0-9][0-9])[F,K]", tokens[6])[0]) * 10

    if (len(tokens[8]) == 4 or len(tokens[8]) == 3):
      if (tokens[8][0] == "0"):
        tokens[8] = tokens[8][1:] 
      self.xtmpf = int(tokens[8][:-1])

  def parseMinLineRT(self, tokens):
    if (len(tokens[8]) == 4 or len(tokens[8]) == 3):
      if (tokens[8][0] == "0"):
        tokens[8] = tokens[8][1:] 
      self.ntmpf = int(tokens[8][:-1])

  def parseCurrentLineRT(self, tokens):
    # ['M', '057', '09:57', '09/04/03', 'ESE', '01MPH', '058K', '460F', '065F', '070%', '30.34R', '00.00"D', '00.00"M', '00.00"R']
    # Don't forget about this lovely one!
    # ['M', '057', '09:57', '09/04/03', 'ESE', '01MPH', '058K', '460F', '0-5F', '070%', '30.34R', '00.00"D', '00.00"M', '00.00"R']
    if (len(tokens[8]) == 4 or len(tokens[8]) == 3):
      if (tokens[8][0] == "0"):
        tokens[8] = tokens[8][1:] 
      self.tmpf = int(tokens[8][:-1])

    self.drct = mesonet.txt2drct[tokens[4]]
    self.drctTxt = tokens[4]
    if (self.do_avg_winds):
      self.aDrct.append( int(self.drct) )

    if (len(tokens[5]) >= 5):
      t = re.findall("([0-9]+)(MPH|KTS)", tokens[5])[0]
      if (t[1] == "MPH"):
        self.sped = int(t[0])
        self.sknt = round( float(self.sped) *  0.868976, 0)
      else:
        self.sknt = int(t[0])
        self.sped = round( self.sknt / 0.868976, 0)
      #if (self.sid == 619):
      #  print self.sknt, self.sped
      if (self.do_avg_winds):
        self.aSknt.append(self.sknt)

    if (len(tokens[6]) == 4):
      self.rad = int(re.findall("([0-9][0-9][0-9])[F,K]", tokens[6])[0]) * 10

    if (len(tokens[9]) == 4):
      self.humid = int(re.findall("([0-9][0-9][0-9])%", tokens[9])[0]) 

    if (len(tokens[10]) == 6):
      self.pres = re.findall("(.*).", tokens[10])[0]

    if (len(tokens[11]) == 7):
      self.pDay = re.findall("(.*)\"D", tokens[11])[0]

    if (len(tokens[12]) == 7):
      self.pMonth = re.findall("(.*)\"M", tokens[12])[0]

    if (self.tmpf > -50 and self.tmpf < 120 and 
        self.humid > 5 and self.humid < 100.1):
        self.dwpf = mesonet.dwpf(self.tmpf, self.humid)
        self.feel = mesonet.feelslike(self.tmpf, self.humid, self.sped)
    else:
        self.dwpf = None
        self.feel = None

  def currentLine(self):
    try:
      return "%s %03i  %5s %8s %-3s %02iMPH %03iK %03iF %03iF %03i%s %05.2f%s %05.2f\"D %05.2f\"M %05.2f\"R\015\012" % ("A", self.sid, self.ts.strftime("%H:%M"), \
        self.ts.strftime("%m/%d/%y"), self.drctTxt, self.sped, self.rad, \
        self.insideTemp, self.tmpf, self.humid, "%", self.pres, self.presTend, self.pDay, self.pMonth, self.pRate)
    except:
      print "A", self.sid, self.ts.strftime("%H:%M"), \
        self.ts.strftime("%m/%d/%y"), self.drctTxt, self.sped, self.rad, \
        self.insideTemp, self.tmpf, self.humid, "%", self.pres, self.presTend, self.pDay, self.pMonth, self.pRate

  def maxLine(self):
    try:
      return "%s %03i  %5s %8s %-3s %02iMPH %03iK %03iF %03iF %03i%s %05.2f%s %05.2f\"D %05.2f\"M %05.2f\"R\015\012" % ("A", self.sid, "Max ", \
        self.ts.strftime("%m/%d/%y"), "N", self.xsped, self.rad, \
        self.insideTemp, self.xtmpf, self.xhumid, "%", self.xpres, self.presTend, 0, 0, 0)
    except:
      print "A", self.sid, "Max ", \
        self.ts.strftime("%m/%d/%y"), self.drctTxt, self.sped, self.rad, \
        self.insideTemp, self.xtmpf, self.xhumid, "%", self.xpres, self.presTend, self.pDay, self.pMonth, self.pRate
     

  def minLine(self):
    try:
      return "%s %03i  %5s %8s %-3s %02iMPH %03iK %03iF %03iF %03i%s %05.2f\" %05.2f\"D %05.2f\"M %05.2f\"R\015\012" % ("A", self.sid, "Min ", \
        self.ts.strftime("%m/%d/%y"), self.drctTxt, 0, 0, \
        self.insideTemp, self.ntmpf, self.nhumid, "%", self.npres, 0, 0, 0)
    except:
      print "A", self.sid, "Min ", \
        self.ts.strftime("%m/%d/%y"), self.drctTxt, 0, 0, \
        self.insideTemp, self.ntmpf, self.nhumid, "%", self.npres, 0, 0, 0
 

  def setPMonth(self, newval):
    if (newval != "NA"):
      self.pMonth = float(newval)

  def setTS(self, newval):
    try:
      if len(newval) == 17:
        self.ts = mx.DateTime.strptime(newval, "%m/%d/%y %H:%M:%S")
      else:
        self.ts = mx.DateTime.strptime(newval, "%m/%d/%y %I:%M:%S %p")
    except:
      traceback.print_exc()
      self.error = 100
      return
    now = mx.DateTime.now()
    if ((now - self.ts) > 7200):
      self.error = 101

  def parseWind(self, newval):
    tokens = re.split("-", newval)
    if (len(tokens) != 2):
      return
    if (tokens[0] != "Missing"):
      self.drctTxt = tokens[0]
    if (tokens[1] == "Missing"):
      return
    try:
      self.sped = int(tokens[1])   
    except ValueError:
      traceback.print_exc()

  def setRad(self, newval):
    if (newval != "NA"):
      self.rad = newval

  def parsePDay(self, newval):
    if (newval == "Missing"):
      self.pDay = 0.00
    else:
      self.pDay = float(newval)

  # Make sure that nothing bad is going on here....
  def sanityCheck(self):
    if (self.xsped == None or self.xsped < 0):
      self.xsped = 0
      self.xdrct = -99
    if (self.pres == None or self.pres < 0):
      self.pres = 0
    if (self.pDay == None or self.pDay < 0):
      self.pDay = 0
    if (self.humid == None or self.humid < 0 or self.humid > 100):
      self.humid = 0
    if (self.tmpf == None or self.tmpf < -100 or self.tmpf > 150):
      self.tmpf = 460
    if (self.ntmpf == None or self.ntmpf < -100 or self.ntmpf > 150):
      self.ntmpf = 460
    if (self.xtmpf == None or self.xtmpf < -100 or self.xtmpf > 150):
      self.xtmpf = 460
    if (self.sped == None or self.sped < 0 or self.sped > 300):
      self.sped = 0
    if (self.avg_sknt == None or self.avg_sknt < 0 or self.avg_sknt > 300):
      self.avg_sknt = 0
    if (self.avg_drct == None or self.avg_drct < 0 or self.avg_drct > 360):
      self.avg_drct = 0
    if (self.xsrad == None or self.xsrad < 0 or self.xsrad > 10000):
      self.xsrad = 0
