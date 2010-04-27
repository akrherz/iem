#	extractMADIS.py
#  Get the latest MADIS numbers from the data file!
#  Daryl Herzmann 5 Nov 2002
#  6 Feb 2004	Rework it!

import string, mx.DateTime, os, sys
from pyIEM import iemAccess, mesonet
iemaccess = iemAccess.iemAccess()
from Scientific.IO import NetCDF

now = mx.DateTime.gmt() + mx.DateTime.RelativeDateTime(hours=-1)
 
fp = "/mesonet/data/madis/mesonet/%s.nc" % (now.strftime("%Y%m%d_%H00"), )
if (not os.path.isfile(fp)):
  sys.exit()

nc = NetCDF.NetCDFFile(fp)



#o = open("/mesonet/data/csv/snet_madis.csv", "w")
#o.write("sid,time,tmpf,m_tmpf,dwpf,m_dwpf,alti,m_alti,drct,m_drct,sknt,m_sknt,\n")

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
  if (val >  1000000.):
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
     alti_qc_sc = %s, valid = '%s' WHERE station = '%s' " % (tmpf, \
     tmpf_qc_av, tmpf_qc_sc, dwpf, dwpf_qc_av, \
     dwpf_qc_sc, alti, alti_qc_av, alti_qc_sc, \
     ts.strftime("%Y-%m-%d %H:%M"), (nc.variables["stationId"][i]).tostring()[:5] )
    iemaccess.query(sql)

#    o.write("%s,%s,%5.2f,%5.2f,%5.2f,%5.2f,%5.2f,%5.2f,%3.0f,%5.2f,%5.2f,%5.2f\n" \
#     % (nc.variables["stationId"][i].tostring()[:5], \
#     ts, mesonet.k2f(nc.variables["temperature"][i].toscalar()) ,  \
#     mesonet.k2f(nc.variables["temperature"][i].toscalar() + nc.variables["temperatureQCD"][i].toscalar()), \
#     mesonet.k2f(nc.variables["dewpoint"][i].toscalar()) ,  \
#     mesonet.k2f(nc.variables["dewpoint"][i].toscalar() + nc.variables["dewpointQCD"][i].toscalar()), \
#     (nc.variables["altimeter"][i]).toscalar() / 100, \
#     nc.variables["altimeterQCD"][i].toscalar() / 100, \
#     (nc.variables["windDir"][i]).toscalar(), \
#     nc.variables["windDirQCD"][i].toscalar(), \
#     (nc.variables["windSpeed"][i]).toscalar() * (1/0.5148), \
#     nc.variables["windSpeedQCD"][i].toscalar() * (1/0.5148) ) )

  i += 1

