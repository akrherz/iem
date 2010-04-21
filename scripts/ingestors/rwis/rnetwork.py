# Class for parsing a rwis FTP file, all OO
# Daryl Herzmann 01 Apr 2002
# 21 Jun 2002:	I guess this is the location to tie this in with Portfolio
# 24 Jun 2002:	Raise threshold to 90 minutes in order to cut down on the 
#		number of reports, geez
# 16 Jul 2002:	Raise threshold to 4 hours
# 17 Jul 2002:	No longer warn for 1980 obs!
# 19 Jul 2002:	Make sure that the TS format is GMT
# 24 Jul 2002:	The METAR collective should not have redundancy!
#		Don't print Iowa City!
#  5 Aug 2002:	Don't send Grinnell until it gets fixed...
#  6 Aug 2002:	Write out a secondary sao file!
#  3 Dec 2002:	Use mx.DateTime
#		Use python2.2
#		Use tracker lib
#		Grinell was obviously fixed, sigh...
# 12 Aug 2003	Quit email bombing the good folks over at the DOT.  Erm,
#               run a check for now many stations are offline...
# 11 May 2004	Fix a bug in iemaccess 
#  2 May 2005	Threshold down to 1 hour!

import re, mx.DateTime, pg, os
from pyIEM import rob, robSF, tracker, stationTable, mesonet

st = stationTable.stationTable("/mesonet/TABLES/RWIS.stns")

_SITES = 62

class rnetwork:
  now = mx.DateTime.gmt()
  thres = now + mx.DateTime.RelativeDateTime(minutes=-300)
  lowerThres = mx.DateTime.DateTime(1990,1,1,1,1)
  dontmail = 0

  def __init__(self, AT_FILENAME, SF_FILENAME):

    self.stationObs = [None]*_SITES
    fh = open(AT_FILENAME, 'r').readlines()
    for i in range(1, len(fh)):
      thisOb = rob.rob(fh[i])
      if ( thisOb.stationNum != None and thisOb.stationNum < _SITES):
        self.stationObs[thisOb.stationNum] = thisOb

    self.sfObs = [0]*_SITES
    for i in range(_SITES):
      sid = mesonet.RWISconvert[str("%02i" % (i) )]
      self.sfObs[i] = robSF.robSF(i, sid)
    f = open(SF_FILENAME).readlines()
    for line in f[1:]:
      tokens = re.split(",", line)
      id = int(tokens[1])
      if (id < _SITES):
        self.sfObs[id].processLine(line)

    self.dontmail = self.checkOffline('IA_RWIS', 300)


  def doSF(self):

    thres = mx.DateTime.gmt() + mx.DateTime.RelativeDateTime(hours=-1)

    for i in range(_SITES):
      if (self.sfObs[i].gmt_ts > thres):
        fRef = open("/mesonet/data/current/rwis_sf/"+ self.sfObs[i].sid +".dat", "w")
        self.sfObs[i].currentsFile(fRef)
        fRef.close()

  def printer(self):
    for i in range(len(self.stationObs)):
      #try:
      if (self.stationObs[i] != None):
        self.stationObs[i].printMETAR()
        self.stationObs[i].printCDF()
      #except:
      #  print i

  def checkOffline(self, network, thres):
    return 0
    from pyIEM import iemAccess
    iemaccess = iemAccess.iemAccess()
    cnt_offline = 0
    # First, look into the offline database to see how many active tickets
    rs = iemaccess.query("SELECT count(*) as c from offline WHERE \
      network = '%s'" % (network,) ).dictresult()
    if (len(rs) > 0):
        cnt_offline = rs[0]['c']
    if (cnt_offline > 10):
        return 1

    # Okay, pre-emptive check to iemdb to see how many obs are old
    lastts = mx.DateTime.now() - mx.DateTime.RelativeDateTime(minutes=thres)
    rs = iemaccess.query("SELECT count(*) as c from current WHERE \
      network = '%s' and valid < '%s' " % \
      (network, lastts.strftime('%Y-%m-%d %H:%M') ) ).dictresult()
    if (len(rs) > 0):
        cnt_offline = rs[0]['c']

    if (cnt_offline > 10):
        return 1

    return 0


  def genMETAR(self, out):
    metarTime = self.now.strftime("%d%H%M")
  
    out.write("\001\015\015\012001\n")
    out.write("SAUS43 KDMX "+metarTime+"\015\015\012METAR\015\015\012")
    for i in range(len(self.stationObs)):
      if (self.stationObs[i] != None):
        sid =  self.stationObs[i].stationID
        if (self.stationObs[i].gmt_ts > self.thres):
          tracker.checkStation(st, sid, self.stationObs[i], "IA_RWIS", "iarwis", self.dontmail)
          if (sid != "RIOI4" and sid != "ROSI4"):
            self.stationObs[i].printMETAR(out) 
        elif (self.stationObs[i].gmt_ts < self.lowerThres):
          print "Station is reporting 1980!"
        else: # Observation is old!
          if (sid not in ["RZZZ","RPFI4","RCTI4"]):
            tracker.doAlert(st, sid, self.stationObs[i], "IA_RWIS", "iarwis", self.dontmail)

    out.write("\015\015\012\003")

  def genMETAR2(self, out):
    metarTime = self.now.strftime("%d%H%M")

    out.write("\001\015\015\012001\n")
    out.write("SAUS43 KDMX "+metarTime+"\015\015\012METAR\015\015\012")
    for i in range(len(self.stationObs)):
      if (self.stationObs[i] != None):
        sid = self.stationObs[i].stationID
        if (sid == "RIOI4" or sid == "ROSI4"):
          ba = "bah"
        elif (self.stationObs[i].gmt_ts > self.thres):
          self.stationObs[i].printMETAR2(out)

    out.write("\015\015\012\003")

    
  def currentWriteCDF(self):
    for i in range(len(self.stationObs)):
      if (self.stationObs[i] != None):
        fileN = self.stationObs[i].stationID +".dat"
        out = open("/mesonet/data/current/rwis/"+fileN, 'w')
        self.stationObs[i].printCDF(out)
        out.close()

  def currentWriteCDFNWS(self,out):
    for i in range(len(self.stationObs)):
      if (self.stationObs[i] != None):
        sid = self.stationObs[i].stationID
        if (sid != "RIOW"):
          self.stationObs[i].printCDF(out)

  def updateIEMAccess(self):
     from pyIEM import iemAccess
     from pyIEM import iemAccessOb
     basets = mx.DateTime.gmt() - mx.DateTime.RelativeDateTime(hours=2)
     iemaccess = iemAccess.iemAccess()
     for i in range(len(self.stationObs)):
       if (self.stationObs[i] == None):
         continue
       if (self.stationObs[i].gmt_ts < basets):
         continue
       if (self.stationObs[i].error > 0):
         continue
       iem = iemAccessOb.iemAccessOb( self.stationObs[i].stationID )
       iem.setObTimeGMT( self.stationObs[i].gmt_ts )
       if (self.stationObs[i].tmpf != None):
         iem.data['tmpf'] = self.stationObs[i].tmpf
       if (self.stationObs[i].dwpf != None):
         iem.data['dwpf'] = self.stationObs[i].dwpf
       if (self.stationObs[i].drct != None):
         iem.data['drct'] = self.stationObs[i].drct
       if (self.stationObs[i].sknt != None):
         iem.data['sknt'] = self.stationObs[i].sknt
       if (self.stationObs[i].gust != None):
         iem.data['gust'] = self.stationObs[i].gust
       if (self.stationObs[i].vsby != None):
         iem.data['vsby'] = self.stationObs[i].vsby
       if (self.stationObs[i].pDay != None):
         iem.data['pday'] = self.stationObs[i].pDay
       iem.data['tsf0'] = self.sfObs[i].sfdata[0]['tmpf']
       iem.data['tsf1'] = self.sfObs[i].sfdata[1]['tmpf']
       iem.data['tsf2'] = self.sfObs[i].sfdata[2]['tmpf']
       iem.data['tsf3'] = self.sfObs[i].sfdata[3]['tmpf']
       iem.data['scond0'] = self.sfObs[i].sfdata[0]['dry']
       iem.data['scond1'] = self.sfObs[i].sfdata[1]['dry']
       iem.data['scond2'] = self.sfObs[i].sfdata[2]['dry']
       iem.data['scond3'] = self.sfObs[i].sfdata[3]['dry']
       iem.data['rwis_subf'] = self.sfObs[i].subT
       iem.updateDatabase(iemaccess.iemdb)
       del(iem)

#  def writeNWS(self):
#    for i in range(len(self.stationObs)):
#      if (self.stationObs[i] != None):
#        fileN = self.stationObs[i].stationID[-3:] +".dat"
#        if (self.stationObs[i].gmt_ts > self.thres):
#          out = open("/home/mesonet/rwis/NWS/LOCDSMMIS"+fileN, 'w')
#          self.stationObs[i].printMETAR(out)
#          out.close()
#
#          out = open("METAR/METAR_"+ self.stationObs[i].stationID , 'w')
#          self.stationObs[i].printMETAR(out)
#          out.close()
