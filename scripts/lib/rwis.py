# Class for RWIS obs

import mx.DateTime, re, os
from pyIEM import mesonet

ERROR_VAL = "32767"

RWISconvert = {
'00' : 'RDAI4', '01' : 'RALI4', '02' : 'RTNI4', '03' : 'RTOI4', '04' : 'RAMI4', '05' : 'RAKI4', '06' : 'RAVI4', '07' : 'RBUI4', '08' : 'RCAI4', '09' : 'RCDI4', '10' : 'RCII4', '11' : 'RCNI4', '12' : 'RCBI4', '13' : 'RCEI4', '14' : 'RDVI4', '15' : 'RDCI4', '16' : 'RDSI4', '17' : 'RDMI4', '18' : 'RDEI4', '19' : 'RDWI4', '20' : 'RDBI4', '21' : 'RFDI4', '22' : 'RGRI4', '23' : 'RIAI4', '24' : 'RIOI4', '25' : 'RJFI4', '26' : 'RLEI4', '27' : 'RMNI4', '28' : 'RMQI4', '29' : 'RMTI4', '30' : 'RMCI4', '31' : 'RMVI4', '32' : 'RMPI4', '33' : 'RNHI4', '34' : 'RONI4', '35' : 'ROSI4', '36' : 'ROTI4', '37' : 'RPLI4', '38' : 'RROI4', '39' : 'RSDI4', '40' : 'RSGI4', '41' : 'RSCI4', '42' : 'RSPI4', '43' : 'RSLI4', '44' : 'RTPI4', '45' : 'RURI4', '46' : 'RWLI4', '47' : 'RWII4', '48' : 'RWBI4', '49' : 'RHAI4', '50' : 'RSBI4', '51' : 'RIGI4', '52' : 'RCRI4', '53' : 'RCFI4', '54' : 'RSYI4',
'55' : 'RBFI4', '56' : 'RDYI4', '57' : 'RTMI4', '58' : 'RPFI4', '59' : 'RCTI4',
'60' : 'RDNI4', '61' : 'RQCI4', '62' : 'RSMI4',
}

RWISconvert2 = {
'00': 'XADA',   '01': 'XALG',   '02': 'XATN',   '03': 'XALT',
'04': 'XAME',   '05': 'XANK',   '06': 'XAVO',   '07': 'XBUR',
'08': 'XCAR',   '09': 'XCDR',   '10': 'XCID',   '11': 'XCEN',
'12': 'XCOU',   '13': 'XCRE',   '14': 'XDAV',   '15': 'XDEC',
'16': 'XDSM',   '17': 'XDES',   '18': 'XDST',   '19': 'XDEW',
'20': 'XDUB',   '21': 'XFOD',   '22': 'XGRI',   '23': 'XIAC',
'24': 'XIOW',   '25': 'XJEF',   '26': 'XLEO',   '27': 'XMAN',
'28': 'XMAQ',   '29': 'XMAR',   '30': 'XMCW',   '31': 'XMIS',
'32': 'XMOU',   '33': 'XNEW',   '34': 'XONA',   '35': 'XOSC',
'36': 'XOTT',   '37': 'XPEL',   '38': 'XRED',   '39': 'XSID',
'40': 'XSIG',   '41': 'XSIO',   '42': 'XSPE',   '43': 'XSTO',
'44': 'XTIP',   '45': 'XURB',   '46': 'XWAT',   '47': 'XWIL',
'48': 'XWBG',   '49': 'XHAN',   '50': 'XSBI',   '51': 'XIGI',
'52': 'XCRI',   '53': 'XCFI',   '54': 'XSYI',   '55': 'XBFI',
'56': 'XDYI',   '57': 'XTMI',   '58': 'XPFI',   '59': 'XCTI',
'60': 'XDNI',   '61': 'XQCI',   '62': 'XSMI'
}


class RWISOb(object):

  def __init__(self):
    self.tmpf       = None
    self.tmpc       = None
    self.dwpf       = None
    self.dwpc       = None
    self.sknt       = None
    self.drct       = None
    self.pDay       = None
    self.gmt_ts     = None
    self.windkmh    = None
    self.windGkmh   = None
    self.ts         = None
    self.stationNum = None
    self.stationID  = None
    self.metarID    = None
    self.gust       = None
    self.vsby       = None
    self.error      = 0
    self.subT = -99
    self.sfdata = [0]*4
    for i in range(4):
      self.sfdata[i] = {"dry": -99, "tmpc": -99, "tmpf": -99}

  def add_sfdata(self, dict):
    sensorid = int(dict["Senid"])
    self.stationNum = int( dict["Rpuid"] )
    self.stationID = RWISconvert["%02i" % (self.stationNum) ]
    self.metarID = RWISconvert2["%02i" % (self.stationNum) ]
    self.parseTime( dict["DtTm"] )

    ttempf = dict["sftemp"]
    tsub = dict["subsftemp"]
    self.sfdata[sensorid]["dry"] = dict["sfcond"]

    if (len(ttempf) > 0 and ttempf != ERROR_VAL):
      self.sfdata[sensorid]["tmpf"] =round(mesonet.c2f( float( ttempf) / 100.00),2)

    if (len(tsub) > 0 and tsub != ERROR_VAL):
      self.subT = round(mesonet.c2f( float(tsub) / 100.00 ),2)

  def add_atdata(self, dict):
    self.stationNum = int( dict["Rpuid"] )
    self.stationID = RWISconvert["%02i" % (self.stationNum) ]
    self.metarID = RWISconvert2["%02i" % (self.stationNum) ]

    self.parseTime( dict["DtTm"] )
    # Air Temperature
    if dict["AirTemp"] not in ['', ERROR_VAL]:
      self.tmpc = float(dict['AirTemp']) / 100.0
      self.tmpf = round( mesonet.c2f(self.tmpc), 1)
    # Dewpoint
    if dict["Dewpoint"] not in ['', ERROR_VAL]:
      self.dwpc = float(dict['Dewpoint']) / 100.0
      self.dwpf = round( mesonet.c2f(self.dwpc), 1)
    # Wind Speed
    if dict["SpdAvg"] not in ['', '255']:
      self.sknt = float(dict['SpdAvg']) * 0.53995
    # Wind Gust
    if dict["SpdGust"] not in ['', '255']:
      self.gust = float(dict['SpdGust']) * 0.53995
    # Wind Direction
    if dict["DirMin"] not in ['', ERROR_VAL]:
      self.drct = int(dict['DirMin'])
    # Today precipitation
    if dict["PcAccum"] not in ['', ERROR_VAL, '-1']:
      self.pDay = float(dict['PcAccum']) * 0.00098425  # Convert to inches
    # Visibility
    if dict["Visibility"] not in ['', ERROR_VAL, '-1']:
      self.vsby = float(dict['Visibility']) / 1609.344  # meters to miles
    
    if self.gust and self.gust >= 50:
      self.windAlert()


  def windAlert(self):
    if self.stationID in ('RBFI4','RTMI4','RWII4','RDNI4'):
      return
    from pyIEM import stationTable, iemdb
    st = stationTable.stationTable("/mesonet/TABLES/RWIS.stns")
    gmtNow = mx.DateTime.gmt()
    stname = st.sts[self.stationID]["name"]
    mf = """At %s, a wind gust of %.1f knots was recorded at the %s RWIS station"""
    mailStr = mf % (self.ts.strftime("%d %b %Y - %I:%M %p"), self.gust, stname)

    fp = "/tmp/%s.%s" % (self.ts.strftime("%Y%m%d%H%M"), self.stationID)
    if (os.path.isfile(fp)):
      print "SKIP", self.stationID
      return
    o = open(fp, 'w')
    o.write(" ")
    o.close()

    if ( int(gmtNow - self.gmt_ts) < (30*60) ): # 30 minutes
      os.system("echo '"+mailStr+"' | mail -s 'RWIS OB' -c akrherz@iastate.edu iarwis-alert@mesonet.agron.iastate.edu")

    else:
      cmd = "echo '"+mailStr+"' | mail -s 'RWIS OB [NO ALERT]' akrherz@iastate.edu"
      os.system(cmd)

    

  def parseTime(self, inStr):
    if self.ts is not None:
        return
    self.gmt_ts = mx.DateTime.strptime(inStr, "%m/%d/%y %H:%M")
    self.ts = self.gmt_ts.localtime()

  def METARtemp(self, inStr):
    f_temp = float(inStr)
    i_temp = int( round(f_temp,0) )
    f1_temp = int( round(f_temp *10,0) )
    if (i_temp < 0):
      i_temp = 0 - i_temp
      m_temp = "M"+str( "%02i" % (i_temp) )
    else:
      m_temp = str( "%02i" % (i_temp) )

    if (f1_temp < 0):
      t_temp = "1"+str( "%03i" % (0 - f1_temp) )
    else:
      t_temp = "0"+str( "%03i" % (f1_temp) )
      
    return m_temp, t_temp

  def metar_wind(self):
    """
    Return a string for METAR wind information
    """
    if self.sknt is None or self.drct is None:
      return ""
    s = ""
    d5 = self.drct
    if str(d5)[-1] == "5":
      d5 -= 5
    s += "%03i%02i" % (d5, self.sknt)
    if self.gust is not None:
      s += "G%02i" % (self.gust,)
    s += "KT"
    return s
    

  def printMETAR(self, out):

    windTxt = self.metar_wind()

    tempTxt = ""
    t_tempTxt = ""
    if self.tmpc is not None and self.dwpc is not None:
      m_tmpc, t_tmpc = self.METARtemp(self.tmpc)
      m_dwpc, t_dwpc = self.METARtemp(self.dwpc)
      tempTxt = "%s/%s" % (m_tmpc, m_dwpc)
      t_tempTxt = "T%s%s " % (t_tmpc, t_dwpc)
  #  print tempTxt, t_tempTxt
    
    out.write("%s %s %s %s RMK AO2 %s%s\015\015\012" % (self.stationID[:4],
      self.gmt_ts.strftime("%d%H%MZ"), windTxt, tempTxt, t_tempTxt, "=") ) 

  def printMETAR2(self, out):

    windTxt = self.metar_wind()

    tempTxt = ""
    t_tempTxt = ""
    if (self.tmpc != None and self.dwpc != None):
      m_tmpc, t_tmpc = self.METARtemp(self.tmpc)
      m_dwpc, t_dwpc = self.METARtemp(self.dwpc)
      tempTxt = "%s/%s" % (m_tmpc, m_dwpc)
      t_tempTxt = "T%s%s " % (t_tmpc, t_dwpc)
  #  print tempTxt, t_tempTxt

    out.write("%s %s %s %s RMK AO2 %s%s\015\015\012" % (self.metarID,
      self.gmt_ts.strftime("%d%H%MZ"), windTxt, tempTxt, t_tempTxt, "=") ) 

  def printCDF(self, out):
    tmpf = self.tmpf
    if (tmpf == None):
      tmpf = ""
    dwpf = self.dwpf
    if (dwpf == None):
      dwpf = ""
    drct = self.drct
    if (drct == None):
      drct = ""
    gust = self.gust
    if (gust == None):
      gust = ""
    sknt = self.sknt
    if (sknt == None):
      sknt = ""
    out.write("%s,%s,%s,%s,%s,%s,%s,%s\n" % \
     (self.stationID, self.gmt_ts, tmpf, dwpf, \
      drct, sknt, self.pDay, gust))
