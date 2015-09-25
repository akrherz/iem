"""
 Extract MADIS METAR QC information to the database
"""
import os
import re
import sys
import psycopg2
import netCDF4
import numpy as np
import datetime
import pytz
from pyiem.datatypes import temperature

IEM = psycopg2.connect(database='iem', host='iemdb')
icursor = IEM.cursor()

now = datetime.datetime.utcnow() - datetime.timedelta(hours=3)

fn = "/mesonet/data/madis/metar/%s.nc" % (now.strftime("%Y%m%d_%H00"), )
table = "current_qc"

if not os.path.isfile(fn):
    sys.exit()

nc = netCDF4.Dataset(fn)

ids = nc.variables["stationName"]
nc_tmpk = nc.variables["temperature"]
nc_dwpk = nc.variables["dewpoint"]
nc_alti = nc.variables["altimeter"]
tmpkQCD = nc.variables["temperatureQCD"]
dwpkQCD = nc.variables["dewpointQCD"]
altiQCD = nc.variables["altimeterQCD"]


def figure(val, qcval):
    if qcval > 1000:
        return 'Null'
    tmpf = temperature(val, 'K').value("F")
    qcval = temperature(val + qcval, 'K').value("F")
    return qcval - tmpf


def figureAlti(val, qcval):
    if (qcval > 100000.):
        return 'Null'
    return qcval / 100.0


def check(val):
    if val > 200000.:
        return 'Null'
    return val

found = 0
for j in range(ids.shape[0]):
    sid = ids[j]
    sid = re.sub('\x00', '', sid.tostring())
    if len(sid) < 4:
        continue
    if sid[0] == "K":
        ts = datetime.datetime(1971, 1, 1) + datetime.timedelta(
                                seconds=nc.variables["timeObs"][j])
        ts = ts.replace(tzinfo=pytz.timezone("UTC"))
        (tmpf, tmpf_qc_av, tmpf_qc_sc) = ('Null', 'Null', 'Null')
        (dwpf, dwpf_qc_av, dwpf_qc_sc) = ('Null', 'Null', 'Null')
        (alti, alti_qc_av, alti_qc_sc) = ('Null', 'Null', 'Null')
        if (not np.ma.is_masked(nc_tmpk[j]) and
                not np.ma.is_masked(tmpkQCD[j, 0]) and
                not np.ma.is_masked(tmpkQCD[j, 6])):
            tmpf = check(temperature(nc_tmpk[j], 'K').value('F'))
            tmpf_qc_av = figure(nc_tmpk[j], tmpkQCD[j, 0])
            tmpf_qc_sc = figure(nc_tmpk[j], tmpkQCD[j, 6])
        if (not np.ma.is_masked(nc_dwpk[j]) and
                not np.ma.is_masked(dwpkQCD[j, 0]) and
                not np.ma.is_masked(dwpkQCD[j, 6])):
            dwpf = check(temperature(nc_dwpk[j], 'K').value('F'))
            dwpf_qc_av = figure(nc_dwpk[j], dwpkQCD[j, 0])
            dwpf_qc_sc = figure(nc_dwpk[j], dwpkQCD[j, 6])
        if not np.ma.is_masked(nc_alti[j]):
            alti = check(nc_alti[j] / 100.0 * 0.0295298)
            alti_qc_av = figureAlti(alti, altiQCD[j, 0] * 0.0295298)
            alti_qc_sc = figureAlti(alti, altiQCD[j, 6] * 0.0295298)
        sql = """
            UPDATE %s SET tmpf = %s, tmpf_qc_av = %s,
            tmpf_qc_sc = %s, dwpf = %s, dwpf_qc_av = %s,
            dwpf_qc_sc = %s, alti = %s, alti_qc_av = %s,
            alti_qc_sc = %s, valid = '%s' WHERE
            station = '%s'
            """ % (table, tmpf,
                   tmpf_qc_av, tmpf_qc_sc, dwpf, dwpf_qc_av,
                   dwpf_qc_sc, alti, alti_qc_av, alti_qc_sc,
                   ts.strftime("%Y-%m-%d %H:%M+00"), sid[1:])
        sql = sql.replace("--", "Null").replace("nan", "Null")
        try:
            icursor.execute(sql)
        except:
            print sql

nc.close()
icursor.close()
IEM.commit()
IEM.close()
