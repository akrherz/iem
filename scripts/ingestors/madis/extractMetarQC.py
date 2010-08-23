#	extractMADIS.py
#  Get the latest MADIS numbers from the data file!
#  Daryl Herzmann 5 Nov 2002

import string, mx.DateTime, os, re, sys
from pyIEM import iemdb, mesonet, stationTable
i = iemdb.iemdb()
iemaccess = i['iem']
import netCDF3
import numpy

iemaccess.query("SET TIME ZONE 'GMT'")

#st = stationTable.stationTable("/mesonet/TABLES/iowa.stns")

now = mx.DateTime.gmt() + mx.DateTime.RelativeDateTime(hours=-3)

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

found =0
for j in range(ids.shape[0]):
  sid = ids[j]
  id = re.sub('\x00', '', sid.tostring())
  if (id[0] == "K"):
    ts = mx.DateTime.gmtime( nc.variables["timeObs"][j] )
    (tmpf, tmpf_qc_av, tmpf_qc_sc) = ('Null', 'Null', 'Null')
    (dwpf, dwpf_qc_av, dwpf_qc_sc) = ('Null', 'Null', 'Null')
    (alti, alti_qc_av, alti_qc_sc) = ('Null', 'Null', 'Null')
    if not numpy.ma.is_masked( nc_tmpk[j] ):
      tmpf = mesonet.k2f( nc_tmpk[j] )
      tmpf_qc_av = figure(nc_tmpk[j], tmpkQCD[j,0])
      tmpf_qc_sc = figure(nc_tmpk[j], tmpkQCD[j,6])
    if not numpy.ma.is_masked( nc_dwpk[j] ):
      dwpf = mesonet.k2f( nc_dwpk[j] )
      dwpf_qc_av = figure(nc_dwpk[j], dwpkQCD[j,0])
      dwpf_qc_sc = figure(nc_dwpk[j], dwpkQCD[j,6])
    if not numpy.ma.is_masked( nc_alti[j] ):
      alti = check( (nc_alti[j][0] / 100.0 ) * 0.0295298)
      alti_qc_av = figureAlti(alti, altiQCD[j,0] * 0.0295298 )
      alti_qc_sc = figureAlti(alti, altiQCD[j,6] * 0.0295298 )
    sql = """UPDATE %s SET tmpf = %s, tmpf_qc_av = %s, 
     tmpf_qc_sc = %s, dwpf = %s, dwpf_qc_av = %s, 
     dwpf_qc_sc = %s, alti = %s, alti_qc_av = %s, 
     alti_qc_sc = %s, valid = '%s' WHERE 
     station = '%s' """ % (table, tmpf, 
     tmpf_qc_av, tmpf_qc_sc, dwpf, dwpf_qc_av, 
     dwpf_qc_sc, alti, alti_qc_av, alti_qc_sc, 
     ts.strftime("%Y-%m-%d %H:%M"), id[1:])
    sql = sql.replace("--", "Null").replace("nan", "Null")
    try:
      iemaccess.query(sql)
    except:
      print sql

nc.close()
