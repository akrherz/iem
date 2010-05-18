# Generate R^2 and bias numbers for comparison of MADIS 

import netCDF3
import sys
import mx.DateTime
import numpy
from scipy import stats

def init_obs():
    d = {}
    for id in ["KSUX","KMCW","KMIW","KSPW","KALO","KCID","KDVN","KDBQ",
               "KLWD","KDSM","KAMW","KEST","KOTM", "KBRL"]:
        d[id] = {}
    return d

def print_summary( obs ):
    for stid in obs.keys():
      cnt = len(obs[stid].keys())
      ioc = []
      gsd = []
      for ts in obs[stid].keys():
        if (obs[stid][ts].has_key("gsd_tmpk") and 
            obs[stid][ts].has_key("ioc_tmpk")):
          ioc.append( obs[stid][ts]["ioc_tmpk"] )
          gsd.append( obs[stid][ts]["gsd_tmpk"] )
      (a_s,b_s,r,tt,stderr)=stats.linregress(gsd,ioc)
      print "%s %2i %4.2f" % (stid, cnt, r**2),

      for k in [0,4,6]:
        ioc = []
        gsd = []
        for ts in obs[stid].keys():
          if (obs[stid][ts].has_key("gsd_tmpkqcd") and 
            obs[stid][ts].has_key("ioc_tmpkqcd")):
            ioc.append( obs[stid][ts]["ioc_tmpkqcd"][k] )
            gsd.append( obs[stid][ts]["gsd_tmpkqcd"][k] )
        (a_s,b_s,r,tt,stderr)=stats.linregress(gsd,ioc)
        print "%4.2f" % (r**2),

      ioc = []
      gsd = []
      for ts in obs[stid].keys():
        if (obs[stid][ts].has_key("gsd_dwpk") and 
            obs[stid][ts].has_key("ioc_dwpk")):
          ioc.append( obs[stid][ts]["ioc_dwpk"] )
          gsd.append( obs[stid][ts]["gsd_dwpk"] )
      (a_s,b_s,r,tt,stderr)=stats.linregress(gsd,ioc)
      print "%s %2i %4.2f" % (stid, cnt, r**2),

      for k in [0,4,6]:
        ioc = []
        gsd = []
        for ts in obs[stid].keys():
          if (obs[stid][ts].has_key("gsd_dwpkqcd") and 
            obs[stid][ts].has_key("ioc_dwpkqcd")):
            ioc.append( obs[stid][ts]["ioc_dwpkqcd"][k] )
            gsd.append( obs[stid][ts]["gsd_dwpkqcd"][k] )
        (a_s,b_s,r,tt,stderr)=stats.linregress(gsd,ioc)
        print "%4.2f" % (r**2),


      print

def runner(runts):
    """
    Generate said stats for some requested date...
    """
    obs = init_obs()
    for i in range(24):
      # Coming from iem50
      fp = "/mnt/mesonet/data/madis/metar/%s_%02i00.nc" % (runts.strftime("%Y%m%d"), i)
      ioc_nc = netCDF3.Dataset(fp, 'r')
      sz = ioc_nc.variables["stationName"].shape[0]
      for idx in range(sz):
        stid = ("".join(ioc_nc.variables["stationName"][idx])).strip()
        if stid not in obs.keys():
          continue
        ts = mx.DateTime.gmtime( ioc_nc.variables["timeObs"][idx] )
        obs[stid][ts] = {
           "ioc_tmpk": ioc_nc.variables["temperature"][idx][0],
           "ioc_tmpkqcd": ioc_nc.variables["temperatureQCD"][idx],
           "ioc_dwpkqcd": ioc_nc.variables["dewpointQCD"][idx],
           "ioc_altiqcd": ioc_nc.variables["altimeterQCD"][idx],
        }
      # Local on iem10
      fp = "/mesonet/data/madis/metar/%s_%02i00.nc" % (runts.strftime("%Y%m%d"), i)
      gsd_nc = netCDF3.Dataset(fp, 'r')
      sz = gsd_nc.variables["stationName"].shape[0]
      for idx in range(sz):
        stid = ("".join(gsd_nc.variables["stationName"][idx])).strip()
        if stid not in obs.keys():
          continue
        ts = mx.DateTime.gmtime( gsd_nc.variables["timeObs"][idx] )
        if not obs[stid].has_key( ts ):
          print "GSD Missed Time: %s %s" % (ts, stid)
          continue
        obs[stid][ts]["gsd_tmpk"] = gsd_nc.variables["temperature"][idx][0]
        obs[stid][ts]["gsd_tmpkqcd"] = gsd_nc.variables["temperatureQCD"][idx]
        obs[stid][ts]["gsd_dwpkqcd"] = gsd_nc.variables["dewpointQCD"][idx]
        obs[stid][ts]["gsd_altiqcd"] = gsd_nc.variables["altimeterQCD"][idx]


      gsd_nc.close()
      ioc_nc.close()

    print_summary( obs )

runner( mx.DateTime.gmt() - mx.DateTime.RelativeDateTime(days=1) )
