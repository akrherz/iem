#	extractMADIS.py
#  Get the latest MADIS numbers from the data file!
#  Daryl Herzmann 5 Nov 2002

import string, mx.DateTime, os, re, sys
from pyIEM import iemdb, mesonet, stationTable
i = iemdb.iemdb()
iemaccess = i['iem']
import netCDF3

iemaccess.query("SET TIME ZONE 'GMT'")

#st = stationTable.stationTable("/mesonet/TABLES/iowa.stns")

now = mx.DateTime.gmt() + mx.DateTime.RelativeDateTime(hours=-1)

# IOC Test
if len(sys.argv) == 2:
  fp = "/mnt/mesonet/data/madis/metar/%s.nc" % (now.strftime("%Y%m%d_%H00"), )
  table = "current_qc_ioc"
else:
  fp = "/mesonet/data/madis/metar/%s.nc" % (now.strftime("%Y%m%d_%H00"), )
  table = "current_qc"


if (not os.path.isfile(fp)):
  sys.exit()

nc = netCDF3.Dataset(fp)

ids = nc.variables["stationName"]
nc_tmpk = nc.variables["temperature"]
nc_dwpk = nc.variables["dewpoint"]
nc_alti = nc.variables["altimeter"]
tmpkQCD = nc.variables["temperatureQCD"]
dwpkQCD = nc.variables["dewpointQCD"]
altiQCD = nc.variables["altimeterQCD"]

def figure(val, qcval):
  if (qcval > 1000):
    return 'Null'
  return mesonet.k2f(val + qcval) -  mesonet.k2f(val)

def figureAlti(val, qcval):
  if (qcval > 100000.):
    return 'Null'
  return qcval / 100.0 

def check(val):
  if (val >  1000000.):
    return 'Null'
  return val

i = 0
found =0
for j in range(len(ids)):
  sid = ids[j]
  id = re.sub('\x00', '', sid.tostring())
  if (id[0] == "K"):
    ts = mx.DateTime.gmtime( nc.variables["timeObs"][i] )
    tmpf = check( mesonet.k2f( nc_tmpk[i] ) )
    dwpf = check( mesonet.k2f( nc_dwpk[i] ) )
    alti = check( (nc_alti[i][0] / 100.0 ) * 0.0295298) 
    tmpf_qc_av = figure(nc_tmpk[i], tmpkQCD[i,0])
    tmpf_qc_sc = figure(nc_tmpk[i], tmpkQCD[i,6])
    dwpf_qc_av = figure(nc_dwpk[i], dwpkQCD[i,0])
    dwpf_qc_sc = figure(nc_dwpk[i], dwpkQCD[i,6])
    alti_qc_av = figureAlti(alti, altiQCD[i,0] * 0.0295298 )
    alti_qc_sc = figureAlti(alti, altiQCD[i,6] * 0.0295298 )
    sql = """UPDATE %s SET tmpf = %s, tmpf_qc_av = %s, 
     tmpf_qc_sc = %s, dwpf = %s, dwpf_qc_av = %s, 
     dwpf_qc_sc = %s, alti = %s, alti_qc_av = %s, 
     alti_qc_sc = %s, valid = '%s' WHERE 
     station = '%s' """ % (table, tmpf, 
     tmpf_qc_av, tmpf_qc_sc, dwpf, dwpf_qc_av, 
     dwpf_qc_sc, alti, alti_qc_av, alti_qc_sc, 
     ts.strftime("%Y-%m-%d %H:%M"), id[1:])
    
    iemaccess.query(sql)
  i += 1

nc.close()
