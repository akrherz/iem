# Something to collect the SNET obs from IEM Access...
# Daryl Herzmann 21 Oct 2004
# 26 May 2005	Port over the 

from pyIEM import iemAccess, iemAccessNetwork, mesonet, iemAccessDatabase
import sys, time, pickle, os, mx.DateTime
from pyIEM import stationTable

gmt = mx.DateTime.gmt()
tstr = gmt.strftime("%Y%m%d%H%M")

now = mx.DateTime.now()

try:
  iemdb = iemAccessDatabase.iemAccessDatabase()
except:
  if (mx.DateTime.now().minute == 20):
    print "DATABASE FAIL"
  sys.exit(0)

st = stationTable.stationTable("/mesonet/TABLES/snet.stns")
st.sts["SMAI4"]["name"] = "M-town"
st.sts["SBZI4"]["name"] = "Zoo"
st.sts["SMSI4"]["name"] = "Barnum"
st.sts["STQI4"]["name"] = "Tama"


def altiTxt(d):
  if d == "":
    return "S"
  if d < 0:
    return "F"
  if d > 0:
    return "R"
  return "S"

def computeOthers(d):
  r = {}
  # Need something to compute other values needed for output
  for sid in d.keys():
    ob = d[sid]
    ob["ticks"] = int(ob["ts"])
    ob["relh"] = mesonet.relh(ob["tmpf"], ob["dwpf"])
    if (ob["relh"] == "M"):
      ob["relh"] = -99
    ob["sped"] = ob["sknt"] * 1.17
    ob["feel"] = mesonet.feelslike(ob["tmpf"], ob["relh"], ob["sped"])
    ob["altiTend"] = altiTxt(ob["alti_15m"])
    ob["drctTxt"] = mesonet.drct2dirTxt(ob["drct"])
    if (ob["max_drct"] == None):
      ob["max_drct"] = 0
    ob["max_drctTxt"] = mesonet.drct2dirTxt(ob["max_drct"])
    ob["20gu"] = 0
    ob["gmph"] = ob["gust"] * 1.17
    ob["max_sped"] = ob["max_gust"] * 1.17
    ob["gtim"] = "0000"
    ob["gtim2"] = "12:00 AM"
    if (ob["max_gust_ts"] != None):
      ob["gtim"] = ob["max_gust_ts"].strftime("%H%M")
      ob["gtim2"] = ob["max_gust_ts"].strftime("%-I:%M %p")
    r[sid] = ob
  return r

def main():
  kcci = iemAccessNetwork.iemAccessNetwork("KCCI")
  kelo = iemAccessNetwork.iemAccessNetwork("KELO")
  kimt = iemAccessNetwork.iemAccessNetwork("KIMT")
  kcci.getObs(iemdb)
  kelo.getObs(iemdb)
  kimt.getObs(iemdb)
  kcci.getTrend15(iemdb)
  kelo.getTrend15(iemdb)
  kimt.getTrend15(iemdb)
  kcci.getPrecipTotals(iemdb)
  kelo.getPrecipTotals(iemdb)
  kimt.getPrecipTotals(iemdb)
  kcci.data = computeOthers(kcci.data)
  kelo.data = computeOthers(kelo.data)
  kimt.data = computeOthers(kimt.data)

  # Ugly, but necessary
  of = open('kcci.dat', 'w')
  of.write("sid,ts,tmpf,dwpf,relh,feel,alti,altiTend,drctTxt,sped,sknt,drct,20gu,gmph,gtim,pday,pmonth,tmpf_min,tmpf_max,max_sknt,drct_max,max_sped,max_drctTxt,max_srad,\n")
  for sid in kcci.data.keys():
    try:
      of.write("%(station)s,%(ticks)s,%(tmpf).0f,%(dwpf).0f,%(relh).0f,%(feel).0f,%(pres).2f,%(altiTend)s,%(drctTxt)s,%(sped).0f,%(sknt).0f,%(drct).0f,%(20gu).0f,%(gmph).0f,%(gtim)s,%(pday).2f,%(pmonth).2f,%(min_tmpf).0f,%(max_tmpf).0f,%(max_gust).0f,%(max_drct).0f,%(max_sped).0f,%(max_drctTxt)s,%(max_srad).0f,\n" % kcci.data[sid] )
    except:
      print kcci.data[sid]
      print sys.excepthook(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2] )
      sys.exc_traceback = None

  of.close()
  #si, se = os.popen4("/home/ldm/bin/pqinsert kcci.dat")
  si, se = os.popen4("/home/ldm/bin/pqinsert -p 'data c %s csv/kcci.dat bogus dat' kcci.dat"%(tstr,) )
  e = se.read()
  if (se != None and len(e) > 0):
    print "pqinsert ERROR: %s" % (e,)
  os.remove("kcci.dat")

  of = open('kcci2.dat', 'w')
  of.write("sid,ts,tmpf,dwpf,relh,feel,alti,altiTend,drctTxt,sped,sknt,drct,20gu,gmph,gtim,pday,pmonth,tmpf_min,tmpf_max,max_sknt,drct_max,max_sped,max_drctTxt,srad,max_srad,online,\n")
  for sid in kcci.data.keys():
    kcci.data[sid]['online'] = 1
    if ((now - kcci.data[sid]['ts']) > 3600):
      kcci.data[sid]['online'] = 0
    try:
      of.write("%(station)s,%(ticks).0f,%(tmpf).0f,%(dwpf).0f,%(relh).0f,%(feel).0f,%(pres).2f,%(altiTend)s,%(drctTxt)s,%(sped).0f,%(sknt).0f,%(drct).0f,%(20gu).0f,%(gmph).0f,%(gtim)s,%(pday).2f,%(pmonth).2f,%(min_tmpf).0f,%(max_tmpf).0f,%(max_sknt).0f,%(max_drct).0f,%(max_sped).0f,%(max_drctTxt)s,%(srad).0f,%(max_srad).0f,%(online)s,\n" % kcci.data[sid] )
    except:
      print kcci.data[sid]
      print sys.excepthook(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2] )
      sys.exc_traceback = None

  of.close()
  si, se = os.popen4("/home/ldm/bin/pqinsert -p 'data c %s csv/kcci2.dat bogus dat' kcci2.dat"%(tstr,))
  os.remove("kcci2.dat")

  of = open('kelo.dat', 'w')
  of.write("sid,ts,tmpf,dwpf,relh,feel,alti,altiTend,drctTxt,sped,sknt,drct,20gu,gmph,gtim,pday,pmonth,tmpf_min,tmpf_max,max_sknt,drct_max,max_sped,max_drctTxt,srad,max_srad,\n")
  for sid in kelo.data.keys():
    try:
      of.write("%(station)s,%(ticks).0f,%(tmpf).0f,%(dwpf).0f,%(relh).0f,%(feel).0f,%(pres).2f,%(altiTend)s,%(drctTxt)s,%(sped).0f,%(sknt).0f,%(drct).0f,%(20gu).0f,%(gmph).0f,%(gtim)s,%(pday).2f,%(pmonth).2f,%(min_tmpf).0f,%(max_tmpf).0f,%(max_sknt).0f,%(max_drct).0f,%(max_sped).0f,%(max_drctTxt)s,%(srad).0f,%(max_srad).0f,\n" % kelo.data[sid] )
    except:
      print kelo.data[sid]
      print sys.excepthook(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2] )
      sys.exc_traceback = None

  of.close()
  #si, se = os.popen4("/home/ldm/bin/pqinsert kelo.dat")
  si, se = os.popen4("/home/ldm/bin/pqinsert -p 'data c %s csv/kelo.dat bogus dat' kelo.dat"%(tstr,) )
  os.remove("kelo.dat")

  of = open('kimt.dat', 'w')
  of.write("sid,ts,tmpf,dwpf,relh,feel,alti,altiTend,drctTxt,sped,sknt,drct,20gu,gmph,gtim,pday,pmonth,tmpf_min,tmpf_max,max_sknt,drct_max,max_sped,max_drctTxt,srad,max_srad,\n")
  for sid in kimt.data.keys():
    try:
      of.write("%(station)s,%(ticks).0f,%(tmpf).0f,%(dwpf).0f,%(relh).0f,%(feel).0f,%(pres).2f,%(altiTend)s,%(drctTxt)s,%(sped).0f,%(sknt).0f,%(drct).0f,%(20gu).0f,%(gmph).0f,%(gtim)s,%(pday).2f,%(pmonth).2f,%(min_tmpf).0f,%(max_tmpf).0f,%(max_sknt).0f,%(max_drct).0f,%(max_sped).0f,%(max_drctTxt)s,%(srad).0f,%(max_srad).0f,\n" % kimt.data[sid] )
    except:
      #print kimt.data[sid]
      #print sys.excepthook(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2] )
      sys.exc_traceback = None

  of.close()
  #si, se = os.popen4("/home/ldm/bin/pqinsert kimt.dat")
  si, se = os.popen4("/home/ldm/bin/pqinsert -p 'data c %s csv/kimt.dat bogus dat' kimt.dat"%(tstr,) )
  os.remove("kimt.dat")

  # Do KCCI stuff in WXC format
  of = open('wxc_snet8.txt', 'w')
  of.write("""Weather Central 001d0300 Surface Data
  24
   5 Station
  52 CityName
  20 CityShort
   2 State
   7 Lat
   8 Lon
   2 Day
   4 Hour
   4 AirTemp
   4 AirDewp
   4 Feels Like
   4 Wind Direction Degrees
   4 Wind Direction Text
   4 Wind Speed
   4 Today Max Temp
   4 Today Min Temp
   4 Today Max Wind Gust MPH
   6 Today Precip
   6 Month Precip
   8 Time of Today Gust
   6 Last 2 Day Precip
   6 Last 3 Day Precip
   6 Last 7 Day Precip
   6 Last 14 Day Precip
""")

  for sid in kcci.data.keys():
    try:
      of.write("%5s %-52s %-20.20s %2s %7.2f %8.2f %2s %4s %4.0f %4.0f %4.0f %4.0f %4s %4.0f %4.0f %4.0f %4.0f %6.2f %6.2f %8s %6.2f %6.2f %6.2f %6.2f\n" % \
      (sid, st.sts[sid]['name'], st.sts[sid]['name'], 'IA', \
       st.sts[sid]['lat'], st.sts[sid]['lon'], \
   kcci.data[sid]['ts'].day, kcci.data[sid]['gts'].hour, \
   kcci.data[sid]['tmpf'], kcci.data[sid]['dwpf'], kcci.data[sid]['feel'],\
   kcci.data[sid]['drct'], kcci.data[sid]['drctTxt'], kcci.data[sid]['sknt'], kcci.data[sid]['max_tmpf'],\
   kcci.data[sid]['min_tmpf'], kcci.data[sid]['max_sped'],\
   kcci.data[sid]['pday'], kcci.data[sid]['pmonth'], kcci.data[sid]['gtim2'],\
   kcci.data[sid]['p2day'], kcci.data[sid]['p3day'], kcci.data[sid]['p7day'], kcci.data[sid]['p14day']) )

    except:
      print kcci.data[sid]
      print sys.excepthook(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2] )
      sys.exc_traceback = None
  si, se = os.popen4("/home/ldm/bin/pqinsert wxc_snet8.txt")
  os.remove("wxc_snet8.txt")

main()
