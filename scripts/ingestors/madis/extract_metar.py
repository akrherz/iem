"""Extract MADIS METAR information.

called from RUN_20MIN.sh
"""
import datetime
import os
from subprocess import PIPE, Popen

import numpy as np
import pandas as pd
import xarray as xr
from pyiem.util import (
    convert_value,
    get_dbconn,
    get_sqlalchemy_conn,
    logger,
    utc,
)

LOG = logger()


def zerocheck(val):
    """Prevent database overflows."""
    return 0 if np.isclose(val, 0) else val


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


def process_metars(metars):
    """Send these through the ingest..."""
    LOG.info("Sending %s metars through ingest", len(metars))
    collective = f"000 \r\r\nSAUS99 KISU {utc():%d%H%M}\r\r\nMETAR\r\r\n"
    collective += "\r\r\n".join(metars)
    collective += "\r\r\n\003"
    # Send this to metar_parser.py
    cmd = [
        "python",
        "/home/meteor_ldm/pyWWA/parsers/metar_parser.py",
        "-x",
        "-l",
    ]
    with Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE) as proc:
        proc.communicate(collective.encode("utf-8"))


def main():
    """Go Main Go."""
    # Find most recent two files
    fns = []
    for offset in range(5):
        now = utc() - datetime.timedelta(hours=offset)
        for j in range(300, -1, -1):
            fn = f"/mesonet/data/madis/metar/{now:%Y%m%d_%H}00_{j}.nc"
            if os.path.isfile(fn):
                fns.append(fn)
                break
        if len(fns) == 2:
            break
    if not fns:
        LOG.warning("No MADIS metar netcdf files found!")
    for fn in fns:
        metars = workflow(fn)
        if metars:
            process_metars(metars)


def workflow(fn):
    """Run for given netcdf filename."""
    pgconn = get_dbconn("iem")
    icursor = pgconn.cursor()
    # Load up current data for ASOS networks
    with get_sqlalchemy_conn("iem") as conn:
        currentdf = pd.read_sql(
            "SELECT id, valid, t.iemid from current c JOIN stations t on "
            "(c.iemid = t.iemid) WHERE t.network ~* 'ASOS'",
            conn,
            index_col="id",
        )
        LOG.info("Found %s current ASOS entries", len(currentdf.index))

    ds = xr.open_dataset(fn)
    valid = pd.to_datetime(ds["timeObs"]).tz_localize(datetime.timezone.utc)
    ids = ds["stationName"].values
    nc_tmpk = ds["temperature"].values
    nc_dwpk = ds["dewpoint"].values
    nc_alti = ds["altimeter"].values
    tmpkqcd = ds["temperatureQCD"].values
    dwpkqcd = ds["dewpointQCD"].values
    altiqcd = ds["altimeterQCD"].values
    metars = []
    for idx, rawid in enumerate(ids):
        rawid = rawid.decode("ascii")
        if len(rawid) != 4:
            continue

        sid = rawid[1:] if rawid.startswith("K") else rawid
        ts = valid[idx]
        if sid not in currentdf.index or ts > currentdf.at[sid, "valid"]:
            # MADIS has newer data than noaaport METAR ingest :/
            metar = (
                ds["rawMETAR"][idx]
                .values.tobytes()
                .decode("ascii")
                .rstrip("\x00")
            )
            # Can't process until we get SA support in pyIEM
            if metar.find(" SA ") > -1:
                continue
            metars.append(f"{metar}=")
            continue
        (tmpf, tmpf_qc_av, tmpf_qc_sc) = (None, None, None)
        (dwpf, dwpf_qc_av, dwpf_qc_sc) = (None, None, None)
        (alti, alti_qc_av, alti_qc_sc) = (None, None, None)
        if (
            not np.ma.is_masked(nc_tmpk[idx])
            and not np.ma.is_masked(tmpkqcd[idx, 0])
            and not np.ma.is_masked(tmpkqcd[idx, 6])
        ):
            tmpf = check(convert_value(nc_tmpk[idx], "degK", "degF"))
            tmpf_qc_av = figure(nc_tmpk[idx], tmpkqcd[idx, 0])
            tmpf_qc_sc = figure(nc_tmpk[idx], tmpkqcd[idx, 6])
        if (
            not np.ma.is_masked(nc_dwpk[idx])
            and not np.ma.is_masked(dwpkqcd[idx, 0])
            and not np.ma.is_masked(dwpkqcd[idx, 6])
        ):
            dwpf = check(convert_value(nc_dwpk[idx], "degK", "degF"))
            dwpf_qc_av = figure(nc_dwpk[idx], dwpkqcd[idx, 0])
            dwpf_qc_sc = figure(nc_dwpk[idx], dwpkqcd[idx, 6])
        if (
            not np.ma.is_masked(nc_alti[idx])
            and not np.ma.is_masked(altiqcd[idx, 0])
            and not np.ma.is_masked(altiqcd[idx, 6])
        ):
            alti = check(nc_alti[idx] / 100.0 * 0.0295298)
            alti_qc_av = figure_alti(altiqcd[idx, 0] * 0.0295298)
            alti_qc_sc = figure_alti(altiqcd[idx, 6] * 0.0295298)
        icursor.execute(
            """
            UPDATE current_qc SET tmpf = %s, tmpf_qc_av = %s,
            tmpf_qc_sc = %s, dwpf = %s, dwpf_qc_av = %s,
            dwpf_qc_sc = %s, alti = %s, alti_qc_av = %s,
            alti_qc_sc = %s, valid = %s WHERE iemid = %s
            """,
            (
                tmpf,
                zerocheck(tmpf_qc_av),
                zerocheck(tmpf_qc_sc),
                dwpf,
                zerocheck(dwpf_qc_av),
                zerocheck(dwpf_qc_sc),
                alti,
                zerocheck(alti_qc_av),
                zerocheck(alti_qc_sc),
                ts,
                currentdf.at[sid, "iemid"],
            ),
        )
        if icursor.rowcount == 0:
            # Data is in SA format :/
            if len(sid) == 4:
                continue
            # Add entry
            LOG.warning("Adding current_qc entry for %s", sid)
            icursor.execute(
                "INSERT into current_qc (iemid) VALUES (%s)",
                (currentdf.at[sid, "iemid"],),
            )

    ds.close()
    icursor.close()
    pgconn.commit()
    pgconn.close()
    return metars


if __name__ == "__main__":
    main()
