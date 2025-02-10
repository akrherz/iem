"""Pretty Four Inch Depth Iowa Plots

Called from run_plots.sh
"""

from datetime import date, datetime, timedelta

import click
import numpy as np
import pandas as pd
import pygrib
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.network import Table
from pyiem.plot import MapPlot, get_cmap
from pyiem.tracker import loadqc
from pyiem.util import archive_fetch, c2f, convert_value, logger
from scipy.signal import convolve2d

LOG = logger()


def get_idx(lons, lats, lon, lat):
    """Return the grid points closest to this point"""
    dist = ((lons - lon) ** 2 + (lats - lat) ** 2) ** 0.5
    return np.unravel_index(dist.argmin(), dist.shape)


def get_grib(now, fhour):
    """Find the desired grib within the grib messages"""
    ppath = now.strftime(
        f"%Y/%m/%d/model/nam/%H/nam.t%Hz.conusnest.hiresf0{fhour}.tm00.grib2"
    )
    with archive_fetch(ppath) as gribfn:
        if gribfn is None:
            LOG.warning("NAM missing: %s", ppath)
            return None
        grbs = pygrib.open(gribfn)
        try:
            gs = grbs.select(shortName="st")
        except ValueError:
            LOG.warning("failed to find st in %s", gribfn)
            return None
        for g in gs:
            if str(g).find("levels 0.0-0.1 m") > 0:
                return g
    return None


def do_nam(valid):
    """Compute county level estimates based on NAM data"""
    # run 6z to 6z, close enough
    now = datetime(valid.year, valid.month, valid.day, 6)
    lats = None
    lons = None
    count = 0
    grib = None
    for offset in [0, 6, 12, 18]:
        runtime = now + timedelta(hours=offset)
        for fhour in range(6):
            grib = get_grib(runtime, fhour)
            if grib is None:
                continue
            if lats is None:
                lats, lons = grib.latlons()
                data = np.zeros(np.shape(lats))
    if grib is None or lats is None:
        LOG.warning("Failed to find NAM data for %s", valid)
        return None, None, None
    data += grib.values
    count += 1
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
    hlons, hlats, hvals = do_nam(ts)
    if hlons is None:
        return
    nam = convert_value(hvals, "degK", "degF")
    window = np.ones((3, 3))
    nam = convolve2d(nam, window / window.sum(), mode="same", boundary="symm")

    # Query out the data
    with get_sqlalchemy_conn("isuag") as conn:
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
    ):
        df[newcol] = c2f(df[col].values)
        df = df.drop(columns=col)

    df["ticket"] = False
    for stid in df.index:
        df.at[stid, "ticket"] = qdict.get(stid, {}).get("soil4", False)
        x, y = get_idx(  # skipcq
            hlons, hlats, nt.sts[stid]["lon"], nt.sts[stid]["lat"]
        )
        df.at[stid, "nam"] = nam[x, y]
        df.at[stid, "lat"] = nt.sts[stid]["lat"]
        df.at[stid, "lon"] = nt.sts[stid]["lon"]
    df = df[~df["ticket"]]
    df["diff"] = df["ob"] - df["nam"]
    bias = df["diff"].mean()
    nam = nam + bias
    LOG.info("NAM bias correction of: %.2fF applied", bias)
    # apply nam bias to sampled data
    df["nam"] += bias
    df["diff"] = df["ob"] - df["nam"]
    # we are going to require data be within 1 SD of sampled or 5 deg
    std = max(5.0, df["nam"].std())
    for station in df[df["diff"].abs() > std].index.values:
        LOG.info(
            "%s QC'd %s out std: %.2f, ob:%.1f nam:%.1f",
            ts.strftime("%Y%m%d"),
            station,
            std,
            df.at[station, "ob"],
            df.at[station, "nam"],
        )
        df = df.drop(station)

    # Query out centroids of counties...
    with get_sqlalchemy_conn("postgis") as conn:
        cdf = pd.read_sql(
            """SELECT ST_x(ST_centroid(the_geom)) as lon,
            ST_y(ST_centroid(the_geom)) as lat
            from uscounties WHERE state_name = 'Iowa'
        """,
            conn,
            index_col=None,
        )
    for i, row in cdf.iterrows():
        x, y = get_idx(hlons, hlats, row["lon"], row["lat"])  # skipcq
        cdf.at[i, "nam"] = nam[x, y]

    mp = MapPlot(
        sector="iowa",
        title=f"{ts:%b %d, %Y} Avg [(Hi+Lo)/2] Daily 4 inch Depth Soil Temp",
        subtitle=(
            "County est. based on bias adj. "
            "NWS NAM Model (black numbers), "
            "ISUSM network observations (red numbers)"
        ),
    )
    mp.pcolormesh(
        hlons,
        hlats,
        nam,
        np.arange(10, 101, 5),
        cmap=get_cmap("jet"),
        units=r"$^\circ$F",
    )
    mp.plot_values(
        df["lon"],
        df["lat"],
        df["ob"].values,
        fmt="%.0f",
        color="r",
        labelbuffer=5,
    )
    mp.plot_values(
        cdf["lon"],
        cdf["lat"],
        cdf["nam"].values,
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
