#	extractMADIS.py
#  Get the latest MADIS numbers from the data file!

import string, mx.DateTime, os, sys
from pyIEM import iemdb, mesonet
i = iemdb.iemdb()
iemaccess = i['iem']
import netCDF3

now = mx.DateTime.gmt() + mx.DateTime.RelativeDateTime(hours=-3)

# IOC Test
if len(sys.argv) == 2:
  fp = "/mnt/mesonet/data/madis/mesonet/%s.nc" % (now.strftime("%Y%m%d_%H00"), )
  table = "current_qc_ioc"
else:
  fp = "/mesonet/data/madis/mesonet/%s.nc" % (now.strftime("%Y%m%d_%H00"), )
  table = "current_qc"

if (not os.path.isfile(fp)):
  sys.exit()

nc = netCDF3.Dataset(fp)


providers = nc.variables["dataProvider"]

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
  if val >  1000000.:
    return 'Null'
  return val


i = 0
found =0
for p in range(len(providers)):
  provider = providers[p]
  if (provider.tostring()[:3] == 'IEM' or provider.tostring()[:5] == 'IADOT' ):
    found = 1
    ts = mx.DateTime.gmtime( nc.variables["observationTime"][i] )

    tmpf = check( mesonet.k2f( nc_tmpk[i] ) )
    dwpf = check( mesonet.k2f( nc_dwpk[i] ) )
    alti = check( (nc_alti[i][0] / 100.0 ) * 0.0295298)
    tmpf_qc_av = figure(nc_tmpk[i], tmpkQCD[i,0])
    tmpf_qc_sc = figure(nc_tmpk[i], tmpkQCD[i,6])
    dwpf_qc_av = figure(nc_dwpk[i], dwpkQCD[i,0])
    dwpf_qc_sc = figure(nc_dwpk[i], dwpkQCD[i,6])
    alti_qc_av = figureAlti(alti, altiQCD[i,0] * 0.0295298 )
    alti_qc_sc = figureAlti(alti, altiQCD[i,6] * 0.0295298 )
    #print id, tmpf, tmpkQCD[i]
    sql = """UPDATE %s SET tmpf = %s, tmpf_qc_av = %s, 
     tmpf_qc_sc = %s, dwpf = %s, dwpf_qc_av = %s, 
     dwpf_qc_sc = %s, alti = %s, alti_qc_av = %s, 
     alti_qc_sc = %s, valid = '%s' WHERE station = '%s' """ % (table, tmpf, 
     tmpf_qc_av, tmpf_qc_sc, dwpf, dwpf_qc_av, 
     dwpf_qc_sc, alti, alti_qc_av, alti_qc_sc, 
     ts.strftime("%Y-%m-%d %H:%M"), (nc.variables["stationId"][i]).tostring()[:5] )
    sql = sql.replace("--", "Null").replace("nan", "Null")
    try:
      iemaccess.query(sql)
    except:
      print sql

  i += 1

nc.close()
