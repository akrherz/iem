# Script to take current SHEF obs and generate a METAR summary
# Daryl Herzmann 19 Mar 2002
# 24 Mar 2005	Basically rewrite

import os, re, mx.DateTime, shapelib, dbflib
from pyIEM import stationTable, tracker, sob, iemAccess
from pyIEM.mesonet import *
from twisted.python import log

badPrecip = [
  "SCOI4", # 70140
  "SBSI4", # 70139
  "SGRI4", # 70127
  "SCEI4", # 47002
  "SLUI4", # 56996
  "SOSI4", # 62514
  "SFCI4", "SNII4",
  "SRSI4", "SNKI4", "SRUM5",'BKGS2', 'LMSM5', 'SDNI4', 'MTMS2', 'MLES2', 'KKAS2', 'CLTS2', 'MTYS2', 'BHHS2', 'PESS2', 'ICSI4', 'WHSS2', 'MOBS2', 'CHAS2', 'RDPS2', 'GETS2', 'ESDS2', 'CLYI4', 'FSNS2', 'WMSM5', 'EPJS2', 'CCES2', 'RRCM5', 'MMSS2', 'LDSS2', "SKWI4","SBLM5"]

log.startLogging( open('snet.log', 'a') )


st = stationTable.stationTable("/mesonet/TABLES/snet.stns")

iem = iemAccess.iemAccess()

now = mx.DateTime.gmt()
lnow = mx.DateTime.now()
sDate = now.strftime("%d%H%M")

# Files we write
SAOFILE = open('snet.sao','w')
CSVFILE = open('snet.csv','w')
KELOCSV = open('kelo.csv','w')
DMXRR5 = open('SUADSMRR5DMX.dat','w')
LOCDSMRR5 = open('LOCDSMRR5DMX.dat','w')
FSDRR5 = open('SUAFSDRR5FSD.dat','w')
BADRR5 = open('kimt_RR5.dat','w')

###
# Two dicts to hold information about precip accumulations
yrCntr = {}
moCntr = {}


#_______________________________________________________________
# writeHeader()
#   - function to simply write the header on the SAO file
#
def writeHeader():
    now = mx.DateTime.gmt()
    sDate = now.strftime("%d%H%M")

    SAOFILE.write("\001\015\015\012001\n")
    SAOFILE.write("SAUS43 KDMX "+sDate+"\015\015\012")
    SAOFILE.write("METAR\015\015\012")
    #DMXRR5.write("\001\015\015\012001\n")
    #DMXRR5.write("SRUS53 KDMX "+sDate+"\015\015\012")
    #DMXRR5.write("RR5DMX\015\015\012")

    now = mx.DateTime.now() + mx.DateTime.RelativeDateTime(minutes=+4)
    sDate = now.strftime("%m%d")
    hour = now.strftime("%H%M")

    DMXRR5.write("\n\n\n.B DMX "+sDate+" C DH"+str(hour)+"/TA/PPH/PPT/PPQ/PCIRP\n")
    DMXRR5.write(":Location ID   TempF / 1h prec / 3h prec / ...\n")
    DMXRR5.write(":                6h prec / pcirp\n")
    DMXRR5.write(":Iowa Environmental Mesonet - KCCI SchoolNet8\n")

    LOCDSMRR5.write("\n\n\n.B DMX "+sDate+" C DH"+str(hour)+"/TA/PCIRP\n")
    LOCDSMRR5.write(":Location ID   TempF / pcirp ...\n")
    LOCDSMRR5.write(":Iowa Environmental Mesonet - KCCI SchoolNet8\n")

    #FSDRR5.write("\n\n\n.B FSD "+sDate+" C DH"+str(hour)+"/TA/PPH/PPT/PPQ/PPD/PCIRP\n")
    FSDRR5.write("\n\n\n.B FSD "+sDate+" C DH"+str(hour)+"/TA/PPH/PPT/PPQ/PCIRP\n")
    FSDRR5.write(":Location ID   TempF / 1h prec / 3h prec / ...\n")
    #FSDRR5.write(":                6h prec / 1d prec / pcirp\n")
    FSDRR5.write(":                6h prec / pcirp\n")
    FSDRR5.write(":Iowa Environmental Mesonet - KELO WeatherNet\n")

 
#_______________________________________________________________
#   loadCounters()
#     - simply loads data from the counter.yr file.
#
def loadCounters():
    o = open("counter.yr").readlines()
    for i in range(len(o)):
      tokens = re.split(" ", o[i])
      sID = tokens[0]
      MOpcpn = tokens[1]
      YRpcpn = tokens[2]
      moCntr[sID] = float(MOpcpn)
      yrCntr[sID] = float(YRpcpn)
    if ( len(o) == 0):
      print "ERROR: counter.yr is null"

#_______________________________________________________________
#   writeCounter()
#     - write the counters back to the counter.yr file
#
def writeCounters():
  o = open("counter.yr","w")
  for key in moCntr.keys():
    MOelem = moCntr[key]
    if (MOelem < 0):
      MOelem = 0
    YRelem = yrCntr[key]
    if (YRelem < 0):
      YRelem = 0
    o.write("%s %.2f %.2f\n" % (key, MOelem, YRelem) )
  o.close()

def doNetwork(network, shefFile, thres):
    # Get Obs
    obs = iem.getNetwork(network)
    # Check to see if we will be alerting for offline stuff
    dontmail = willEmail(network, thres)
    #dontmail = 1
    keys = obs.keys()
    keys.sort()
    for nwsli in keys:
        myOb = sob.sob(obs[nwsli], 'D', iemaccess=iem)
        myOb.doPrec()
        if (myOb.ts < thres):  
            tracker.doAlert(st, myOb.stationID, myOb, network, '%ssnet' % (network.lower(),) , dontmail)
            continue

        tracker.checkStation(st, myOb.stationID, myOb, network, '%ssnet' % (network.lower(),), dontmail)
 

        if (float(myOb.pMonth) < moCntr[nwsli] and float(myOb.pMonth) >= 0):  # Reset Monthly counter
            yrCntr[nwsli] = yrCntr[nwsli] + moCntr[nwsli]
        moCntr[nwsli] = float(myOb.pMonth)
        myOb.pYear = yrCntr[nwsli] 
        if (float(myOb.pMonth) >= 0):
            myOb.pYear = yrCntr[nwsli] + float(myOb.pMonth)

        if badPrecip.__contains__(nwsli):
            myOb.printSHEF_tmp(shefFile, cancelPrecip=1,sname=st.sts[nwsli]['name'])
            if (network == "KCCI"):
                myOb.printPCIRP(LOCDSMRR5, cancelPrecip=1)
        else:
            myOb.printSHEF_tmp(shefFile,sname=st.sts[nwsli]['name'])
            if (network == "KCCI"):
                myOb.printPCIRP(LOCDSMRR5)
        myOb.printD2D(CSVFILE)
        if (network == 'KELO'):
            myOb.printD2D(KELOCSV)
        if network != 'KIMT':
            myOb.printMETAR(SAOFILE)


def closeFiles():
    SAOFILE.write("\015\015\012\003")
    SAOFILE.close()
    DMXRR5.write(".END\n")
    DMXRR5.close()
    LOCDSMRR5.write(".END\n")
    LOCDSMRR5.close()
    FSDRR5.write(".END\n")
    FSDRR5.close()


#
# Check to make sure our email alerts are not excessive
#
def willEmail(network, thres):
    cnt_threshold = 25
    if (network == 'KIMT'):
        cnt_threshold = 10
    cnt_offline = 0
    # First, look into the offline database to see how many active tickets
    rs = iem.query("SELECT count(*) as c from offline WHERE \
      network = '%s' and length(station) = 5" % (network,) ).dictresult()
    if (len(rs) > 0):
        cnt_offline = rs[0]['c']

    log.msg("Portfolio says cnt_offline: %s %s" % (network, cnt_offline,))
    if (cnt_offline > cnt_threshold):
        return 1

    # Okay, pre-emptive check to iemdb to see how many obs are old
    mythres = thres + mx.DateTime.RelativeDateTime(minutes=6)
    rs = iem.query("SELECT count(*) as c from current WHERE \
      network = '%s' and valid < '%s' " % \
      (network, mythres.strftime('%Y-%m-%d %H:%M') ) ).dictresult() 
    if (len(rs) > 0):
        cnt_offline = rs[0]['c']
        log.msg("IEMAccess says cnt_offline: %s, %s, %s" % (network, mythres,cnt_offline,))

    if (cnt_offline > cnt_threshold):
        return 1

    return 0

def Main():
    loadCounters()
    writeHeader()
    now = mx.DateTime.now()
    doNetwork('KCCI', DMXRR5, now - mx.DateTime.RelativeDateTime(minutes=60))
    #DMXRR5.write(":Iowa Environmental Mesonet - KIMT StormNet\n")
    doNetwork('KIMT', BADRR5, now - mx.DateTime.RelativeDateTime(minutes=60))
    doNetwork('KELO', FSDRR5, now - mx.DateTime.RelativeDateTime(minutes=300))


    writeCounters()
    closeFiles()
Main()
