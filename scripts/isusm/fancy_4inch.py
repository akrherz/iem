"""Pretty Four Inch Depth Iowa Plots

Called from run_plots.sh
"""

import os
from datetime import date, datetime, timedelta

import click
import numpy as np
import pandas as pd
import pygrib
import requests
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.network import Table
from pyiem.plot import MapPlot, get_cmap
from pyiem.tracker import loadqc
from pyiem.util import c2f, convert_value, logger
from scipy.signal import convolve2d

LOG = logger()


def get_idx(lons, lats, lon, lat):
    """Return the grid points closest to this point"""
    dist = ((lons - lon) ** 2 + (lats - lat) ** 2) ** 0.5
    return np.unravel_index(dist.argmin(), dist.shape)


def get_grib(valid: datetime, fhour: int):
    """Find the desired grib within the grib messages"""
    idxfn = (
        "https://noaa-rrfs-ops-pds.s3.amazonaws.com/"
        f"rrfs.{valid:%Y%m%d}/{valid:%H}/"
        f"rrfs.t{valid:%H}z.2dfld.13km.f{fhour:03.0f}.na.grib2.idx"
    )
    resp = requests.get(idxfn, timeout=60)
    if resp.status_code != 200:
        LOG.info("Download %s failed, returning None", idxfn)
        return None

    offsets = []
    for line in resp.text.splitlines():
        tokens = line.split(":")
        if offsets:
            offsets.append(int(tokens[1]) - 1)
            break
        if ":TSOIL:0.01-0.01 m below ground" in line:
            offsets.append(int(tokens[1]))

    if len(offsets) < 2:
        LOG.info("Failed to parse offsets from %s", idxfn)
        return None

    gribfn = idxfn.removesuffix(".idx")
    resp = requests.get(
        gribfn,
        headers={"Range": f"bytes={offsets[0]}-{offsets[1]}"},
        timeout=60,
    )
    if resp.status_code != 206:
        LOG.info("Download %s failed, returning None", gribfn)
        return None

    with open("tmp.grib", "wb") as fh:
        fh.write(resp.content)
    with pygrib.open("tmp.grib") as grbs:  # type: ignore
        g = grbs[1]
    os.unlink("tmp.grib")
    return g


def do_rrfs(valid: date):
    """Compute county level estimates based on RRFS data"""
    # run 6z to 6z, close enough
    model_runtime = datetime(valid.year, valid.month, valid.day, 6)
    lats = None
    lons = None
    count = 0
    grib = None
    data = None
    for fhour in [6, 12, 18, 24]:
        grib = get_grib(model_runtime, fhour)
        if grib is None:
            continue
        if lats is None:
            lats, lons = grib.latlons()
            LOG.info("lons ranges %s to %s", lons.min(), lons.max())
            data = np.zeros(np.shape(lats))
        values = grib.values.filled(np.nan)
        LOG.info(
            "Fhour %s ranges from %s to %s",
            fhour,
            np.nanmin(values),
            np.nanmax(values),
        )
        data += values
        count += 1
    if count < 2 or data is None:
        LOG.warning("Failed to find RRFS data for %s", valid)
        return None, None, None
    LOG.info("Found %s grib files", count)
    result = data / float(count)
    LOG.info(
        "Resulting grid ranges from %s to %s",
        np.nanmin(result),
        np.nanmax(result),
    )
    return lons, lats, data / float(count)


def sampler(xaxis, yaxis, vals, x, y):
    """This is a hack"""
    i = 0
    while xaxis[i] < x:
        i += 1
    j = 0
    while yaxis[j] < y:
        j += 1
    return vals[i, j]


@click.command()
@click.option("--days", type=int, required=True)
def main(days: int):
    """Go Main Go"""
    nt = Table("ISUSM")
    qdict = loadqc()
    ts = date.today() - timedelta(days=days)
    hlons, hlats, hvals = do_rrfs(ts)
    if hlons is None:
        LOG.warning("Exiting as no RRFS data found for %s", ts)
        return
    rrfs: np.ndarray = convert_value(hvals, "degK", "degF")
    window = np.ones((3, 3))
    rrfs = convolve2d(
        rrfs, window / window.sum(), mode="same", boundary="symm"
    )

    # Query out the data
    with get_sqlalchemy_conn("isuag", rw=False) as conn:
        df = pd.read_sql(
            sql_helper("""
            WITH ranges as (
                select station, count(*), min(t4_c_avg_qc),
                max(t4_c_avg_qc) from sm_hourly WHERE
                valid >= :sts and valid < :ets and t4_c_avg_qc > -40
                and t4_c_avg_qc < 50 GROUP by station
            )
            SELECT d.station, d.t4_c_avg_qc,
            r.max as hourly_max_c, r.min as hourly_min_c, r.count
            from sm_daily d JOIN ranges r on (d.station = r.station)
            where valid = :sts and t4_c_avg_qc > -40 and r.count > 19
        """),
            conn,
            params={"sts": ts, "ets": ts + timedelta(days=1)},
            index_col="station",
        )
    if df.empty:
        LOG.info("No data found for %s", ts)
        return
    for col, newcol in zip(
        ["t4_c_avg_qc", "hourly_min_c", "hourly_max_c"],
        ["ob", "min", "max"],
        strict=False,
    ):
        df[newcol] = c2f(df[col].values)
        df = df.drop(columns=col)

    df["ticket"] = False
    for stid in df.index:
        df.loc[stid, "ticket"] = qdict.get(stid, {}).get("soil4", False)
        x, y = get_idx(  # skipcq
            hlons, hlats, nt.sts[stid]["lon"], nt.sts[stid]["lat"]
        )
        df.loc[stid, "rrfs"] = rrfs[x, y]
        df.loc[stid, "lat"] = nt.sts[stid]["lat"]
        df.loc[stid, "lon"] = nt.sts[stid]["lon"]
    df = df[~df["ticket"]]
    df["diff"] = df["ob"] - df["rrfs"]
    bias = df["diff"].mean()
    rrfs = rrfs + bias
    LOG.info("NAM bias correction of: %.2fF applied", bias)
    # apply nam bias to sampled data
    df["rrfs"] += bias
    df["diff"] = df["ob"] - df["rrfs"]
    # we are going to require data be within 1 SD of sampled or 5 deg
    std = max(5.0, df["rrfs"].std())
    for station in df[df["diff"].abs() > std].index.values:
        LOG.info(
            "%s QC'd %s out std: %.2f, ob:%.1f nam:%.1f",
            ts.strftime("%Y%m%d"),
            station,
            std,
            df.loc[station, "ob"],
            df.loc[station, "rrfs"],
        )
        df = df.drop(station)

    # Query out centroids of counties...
    with get_sqlalchemy_conn("postgis", rw=False) as conn:
        cdf = pd.read_sql(
            """SELECT ST_x(ST_centroid(the_geom)) as lon,
            ST_y(ST_centroid(the_geom)) as lat
            from uscounties WHERE state_name = 'Iowa'
        """,
            conn,
            index_col=None,
        )
    nam_vals = []
    for row in cdf.itertuples():
        x, y = get_idx(hlons, hlats, row.lon, row.lat)
        nam_vals.append(float(rrfs[x, y]))
    cdf["nam"] = nam_vals

    mp = MapPlot(
        sector="iowa",
        title=f"{ts:%b %d, %Y} Avg [(Hi+Lo)/2] Daily 4 inch Depth Soil Temp",
        subtitle=(
            "County est. based on bias adj. "
            "NWS RRFS Model (black numbers), "
            "ISUSM network observations (red numbers)"
        ),
    )
    LOG.info("Raw %s to %s", np.nanmin(rrfs), np.nanmax(rrfs))
    mp.pcolormesh(
        hlons,
        hlats,
        rrfs,
        np.arange(10, 101, 5),
        cmap=get_cmap("jet"),
        units="°F",
    )
    mp.plot_values(
        df["lon"],
        df["lat"],
        df["ob"].to_numpy(),
        fmt="%.0f",
        color="r",
        labelbuffer=5,
    )
    mp.plot_values(
        cdf["lon"],
        cdf["lat"],
        cdf["nam"].to_numpy(),
        fmt="%.0f",
        textsize=11,
        labelbuffer=5,
    )
    mp.drawcounties()
    routes = "a" if days >= 4 else "ac"
    pqstr = (
        f"plot {routes} {ts:%Y%m%d}0000 soilt_day{days}.png "
        "isuag_county_4inch_soil.png png"
    )
    mp.postprocess(pqstr=pqstr)
    mp.close()


if __name__ == "__main__":
    main()
