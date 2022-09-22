"""Extract MADIS METAR QC information to the database

called from RUN_40_AFTER.sh
"""
import os
import sys
import datetime

import numpy as np
from netCDF4 import chartostring
from pyiem.util import get_dbconn, ncopen, convert_value, logger, utc

LOG = logger()


def figure(val, qcval):
    """Go."""
    if qcval > 1000:
        return None
    tmpf = convert_value(val, "degK", "degF")
    qcval = convert_value(val + qcval, "degK", "degF")
    return float(qcval - tmpf)


def figure_alti(qcval):
    """Go."""
    if qcval > 100000.0:
        return None
    return float(qcval) / 100.0


def check(val):
    """Go."""
    if val > 200000.0:
        return None
    return float(val)


def main():
    """Go Main Go"""
    pgconn = get_dbconn("iem")
    icursor = pgconn.cursor()

    for offset in range(5):
        now = utc() - datetime.timedelta(hours=offset)
        fn = f"/mesonet/data/madis/metar/{now:%Y%m%d_%H}00.nc"
        if os.path.isfile(fn):
            break
    if not os.path.isfile(fn):
        LOG.info("Missing %s", fn)
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
        sid = sid[1:] if sid.startswith("K") else sid
        ts = (
            datetime.datetime(1970, 1, 1)
            + datetime.timedelta(seconds=int(nc.variables["timeObs"][j]))
        ).replace(tzinfo=datetime.timezone.utc)
        (tmpf, tmpf_qc_av, tmpf_qc_sc) = (None, None, None)
        (dwpf, dwpf_qc_av, dwpf_qc_sc) = (None, None, None)
        (alti, alti_qc_av, alti_qc_sc) = (None, None, None)
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
        if (
            not np.ma.is_masked(nc_alti[j])
            and not np.ma.is_masked(altiqcd[j, 0])
            and not np.ma.is_masked(altiqcd[j, 6])
        ):
            alti = check(nc_alti[j] / 100.0 * 0.0295298)
            alti_qc_av = figure_alti(altiqcd[j, 0] * 0.0295298)
            alti_qc_sc = figure_alti(altiqcd[j, 6] * 0.0295298)
        icursor.execute(
            """
            UPDATE current_qc c SET tmpf = %s, tmpf_qc_av = %s,
            tmpf_qc_sc = %s, dwpf = %s, dwpf_qc_av = %s,
            dwpf_qc_sc = %s, alti = %s, alti_qc_av = %s,
            alti_qc_sc = %s, valid = %s FROM stations t WHERE
            c.iemid = t.iemid and t.id = %s and t.network ~* 'ASOS'
            """,
            (
                tmpf,
                tmpf_qc_av,
                tmpf_qc_sc,
                dwpf,
                dwpf_qc_av,
                dwpf_qc_sc,
                alti,
                alti_qc_av,
                alti_qc_sc,
                ts,
                sid,
            ),
        )
        if icursor.rowcount == 0:
            # Data is in SA format :/
            if len(sid) == 4:
                continue
            # Add entry
            LOG.warning("Adding current_qc entry for %s", sid)
            icursor.execute(
                "INSERT into current_qc (iemid) "
                "SELECT iemid from stations where id = %s "
                "and network ~* 'ASOS'",
                (sid,),
            )
            if icursor.rowcount == 0:
                LOG.warning("Unknown station? %s", sid)

    nc.close()
    icursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
