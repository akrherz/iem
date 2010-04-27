#	extractMADIS.py
#  Get the latest MADIS numbers from the data file!
#  Daryl Herzmann 5 Nov 2002

import string, mx.DateTime, os, re, sys
from pyIEM import iemAccess, mesonet, stationTable
iemaccess = iemAccess.iemAccess()
from Scientific.IO import NetCDF

iemaccess.query("SET TIME ZONE 'GMT'")

#st = stationTable.stationTable("/mesonet/TABLES/iowa.stns")

now = mx.DateTime.gmt() + mx.DateTime.RelativeDateTime(hours=-1)

fp = "/mesonet/data/madis/metar/%s.nc" % (now.strftime("%Y%m%d_%H00"), ) 
if (not os.path.isfile(fp)):
  sys.exit()

nc = NetCDF.NetCDFFile(fp)

ids = nc.variables["stationName"].getValue()
nc_tmpk = nc.variables["temperature"].getValue()
nc_dwpk = nc.variables["dewpoint"].getValue()
nc_alti = nc.variables["altimeter"].getValue()
tmpkQCD = nc.variables["temperatureQCD"].getValue()
dwpkQCD = nc.variables["dewpointQCD"].getValue()
altiQCD = nc.variables["altimeterQCD"].getValue()

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
for sid in ids:
  id = re.sub('\x00', '', sid.tostring())
  #if (st.sts.has_key(id[1:]) and id[0] == "K"):
  if (id[0] == "K"):
    ts = mx.DateTime.gmtime( nc.variables["timeObs"][i] )
    tmpf = check( mesonet.k2f( nc_tmpk[i] ) )
    dwpf = check( mesonet.k2f( nc_dwpk[i] ) )
    alti = check( (nc_alti[i][0] / 100.0 ) * 0.0295298) 
    tmpf_qc_av = figure(nc_tmpk[i][0], tmpkQCD[i][0][0])
    tmpf_qc_sc = figure(nc_tmpk[i][0], tmpkQCD[i][6][0])
    dwpf_qc_av = figure(nc_dwpk[i][0], dwpkQCD[i][0][0])
    dwpf_qc_sc = figure(nc_dwpk[i][0], dwpkQCD[i][6][0])
    alti_qc_av = figureAlti(alti, altiQCD[i][0][0] * 0.0295298 )
    alti_qc_sc = figureAlti(alti, altiQCD[i][6][0] * 0.0295298 )
    #print id, tmpf, tmpkQCD[i]
    sql = "UPDATE current_qc SET tmpf = %s, tmpf_qc_av = %s, \
     tmpf_qc_sc = %s, dwpf = %s, dwpf_qc_av = %s, \
     dwpf_qc_sc = %s, alti = %s, alti_qc_av = %s, \
     alti_qc_sc = %s, valid = '%s' WHERE \
     station = '%s' " % (tmpf, \
     tmpf_qc_av, tmpf_qc_sc, dwpf, dwpf_qc_av, \
     dwpf_qc_sc, alti, alti_qc_av, alti_qc_sc, \
     ts.strftime("%Y-%m-%d %H:%M"), id[1:])
    iemaccess.query(sql)
  i += 1

