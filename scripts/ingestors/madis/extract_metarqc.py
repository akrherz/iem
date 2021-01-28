"""
 Extract MADIS METAR QC information to the database
"""
import os
import sys
import datetime
import warnings

import numpy as np
import pytz
from netCDF4 import chartostring
from pyiem.util import get_dbconn, ncopen, convert_value

warnings.filterwarnings("ignore", category=DeprecationWarning)


def figure(val, qcval):
    """Go."""
    if qcval > 1000:
        return "Null"
    tmpf = convert_value(val, "degK", "degF")
    qcval = convert_value(val + qcval, "degK", "degF")
    return qcval - tmpf


def figure_alti(qcval):
    """Go."""
    if qcval > 100000.0:
        return "Null"
    return qcval / 100.0


def check(val):
    """Go."""
    if val > 200000.0:
        return "Null"
    return val


def main():
    """Go Main Go"""
    pgconn = get_dbconn("iem")
    icursor = pgconn.cursor()

    now = datetime.datetime.utcnow() - datetime.timedelta(hours=3)

    fn = "/mesonet/data/madis/metar/%s.nc" % (now.strftime("%Y%m%d_%H00"),)
    table = "current_qc"

    if not os.path.isfile(fn):
        sys.exit()

    nc = ncopen(fn)

    ids = chartostring(nc.variables["stationName"][:])
    nc_tmpk = nc.variables["temperature"]
    nc_dwpk = nc.variables["dewpoint"]
    nc_alti = nc.variables["altimeter"]
    tmpkqcd = nc.variables["temperatureQCD"]
    dwpkqcd = nc.variables["dewpointQCD"]
    altiqcd = nc.variables["altimeterQCD"]

    for j in range(ids.shape[0]):
        sid = ids[j]
        if len(sid) < 4:
            continue
        if sid[0] == "K":
            ts = datetime.datetime(1970, 1, 1) + datetime.timedelta(
                seconds=int(nc.variables["timeObs"][j])
            )
            ts = ts.replace(tzinfo=pytz.utc)
            (tmpf, tmpf_qc_av, tmpf_qc_sc) = ("Null", "Null", "Null")
            (dwpf, dwpf_qc_av, dwpf_qc_sc) = ("Null", "Null", "Null")
            (alti, alti_qc_av, alti_qc_sc) = ("Null", "Null", "Null")
            if (
                not np.ma.is_masked(nc_tmpk[j])
                and not np.ma.is_masked(tmpkqcd[j, 0])
                and not np.ma.is_masked(tmpkqcd[j, 6])
            ):
                tmpf = check(convert_value(nc_tmpk[j], "degK", "degF"))
                tmpf_qc_av = figure(nc_tmpk[j], tmpkqcd[j, 0])
                tmpf_qc_sc = figure(nc_tmpk[j], tmpkqcd[j, 6])
            if (
                not np.ma.is_masked(nc_dwpk[j])
                and not np.ma.is_masked(dwpkqcd[j, 0])
                and not np.ma.is_masked(dwpkqcd[j, 6])
            ):
                dwpf = check(convert_value(nc_dwpk[j], "degK", "degF"))
                dwpf_qc_av = figure(nc_dwpk[j], dwpkqcd[j, 0])
                dwpf_qc_sc = figure(nc_dwpk[j], dwpkqcd[j, 6])
            if not np.ma.is_masked(nc_alti[j]):
                alti = check(nc_alti[j] / 100.0 * 0.0295298)
                alti_qc_av = figure_alti(altiqcd[j, 0] * 0.0295298)
                alti_qc_sc = figure_alti(altiqcd[j, 6] * 0.0295298)
            sql = """
                UPDATE %s SET tmpf = %s, tmpf_qc_av = %s,
                tmpf_qc_sc = %s, dwpf = %s, dwpf_qc_av = %s,
                dwpf_qc_sc = %s, alti = %s, alti_qc_av = %s,
                alti_qc_sc = %s, valid = '%s' WHERE
                station = '%s'
                """ % (
                table,
                tmpf,
                tmpf_qc_av,
                tmpf_qc_sc,
                dwpf,
                dwpf_qc_av,
                dwpf_qc_sc,
                alti,
                alti_qc_av,
                alti_qc_sc,
                ts.strftime("%Y-%m-%d %H:%M+00"),
                sid[1:],
            )
            sql = sql.replace("--", "Null").replace("nan", "Null")
            try:
                icursor.execute(sql)
            except Exception as exp:
                print(exp)
                print(sql)

    nc.close()
    icursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
