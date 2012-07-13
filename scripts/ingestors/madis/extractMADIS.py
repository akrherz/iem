#	extractMADIS.py
#  Get the latest MADIS numbers from the data file!

import string
import mx.DateTime
import os
import sys
import iemdb
import mesonet
IEM = iemdb.connect('iem')
icursor = IEM.cursor()
import netCDF4
import numpy

now = mx.DateTime.gmt() + mx.DateTime.RelativeDateTime(hours=-3)
now = mx.DateTime.DateTime(2012, 5, 25, 12, 0)

fp = "/mesonet/data/madis/mesonet/%s.nc" % (now.strftime("%Y%m%d_%H00"), )
table = "current_qc"

if (not os.path.isfile(fp)):
  sys.exit()

nc = netCDF4.Dataset(fp)


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

for p in range(providers.shape[0]):
    provider = providers[p]
    if provider.tostring().replace('\x00','') not in ['IEM', 'IADOT']:
        continue  
    ts = mx.DateTime.gmtime( nc.variables["observationTime"][p] )

    (tmpf, tmpf_qc_av, tmpf_qc_sc) = ('Null', 'Null', 'Null')
    (dwpf, dwpf_qc_av, dwpf_qc_sc) = ('Null', 'Null', 'Null')
    (alti, alti_qc_av, alti_qc_sc) = ('Null', 'Null', 'Null')

    if not numpy.ma.is_masked( nc_tmpk[p] ):
        tmpf = check( mesonet.k2f( nc_tmpk[p] ) )
        tmpf_qc_av = figure(nc_tmpk[p], tmpkQCD[p,0])
        tmpf_qc_sc = figure(nc_tmpk[p], tmpkQCD[p,6])
    if not numpy.ma.is_masked( nc_dwpk[p] ):
        dwpf = check( mesonet.k2f( nc_dwpk[p] ) )
        dwpf_qc_av = figure(nc_dwpk[p], dwpkQCD[p,0])
        dwpf_qc_sc = figure(nc_dwpk[p], dwpkQCD[p,6])
    if not numpy.ma.is_masked( nc_alti[p] ):
        alti = check( (nc_alti[p] / 100.0 ) * 0.0295298)
        alti_qc_av = figureAlti(alti, altiQCD[p,0] * 0.0295298 )
        alti_qc_sc = figureAlti(alti, altiQCD[p,6] * 0.0295298 )
    #print id, tmpf, tmpkQCD[i]
    sql = """UPDATE %s SET tmpf = %s, tmpf_qc_av = %s, 
     tmpf_qc_sc = %s, dwpf = %s, dwpf_qc_av = %s, 
     dwpf_qc_sc = %s, alti = %s, alti_qc_av = %s, 
     alti_qc_sc = %s, valid = '%s' WHERE station = '%s' """ % (table, tmpf, 
     tmpf_qc_av, tmpf_qc_sc, dwpf, dwpf_qc_av, 
     dwpf_qc_sc, alti, alti_qc_av, alti_qc_sc, 
     ts.strftime("%Y-%m-%d %H:%M"), (nc.variables["stationId"][p]).tostring()[:5] )
    sql = sql.replace("--", "Null").replace("nan", "Null")
    try:
        icursor.execute(sql)
    except:
        print sql

nc.close()
