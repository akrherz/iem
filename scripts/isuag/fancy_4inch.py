"""Pretty Four Inch Depth Iowa Plots"""
# stdlib
import datetime
import sys
import os

# thirdparty
from pandas.io.sql import read_sql
import numpy as np
from scipy.signal import convolve2d
import pygrib
from pyiem.plot import MapPlot, get_cmap
from pyiem.datatypes import temperature
from pyiem.tracker import loadqc
from pyiem.network import Table
from pyiem.util import get_dbconn, logger

LOG = logger()


def get_idx(lons, lats, lon, lat):
    """ Return the grid points closest to this point """
    dist = ((lons - lon) ** 2 + (lats - lat) ** 2) ** 0.5
    return np.unravel_index(dist.argmin(), dist.shape)


def get_grib(now, fhour):
    """Find the desired grib within the grib messages"""
    gribfn = now.strftime(
        (
            "/mesonet/ARCHIVE/data/%Y/%m/%d/model/nam/"
            "%H/nam.t%Hz.conusnest.hiresf0" + str(fhour) + ".tm00.grib2"
        )
    )
    if not os.path.isfile(gribfn):
        LOG.info("NAM missing: %s", gribfn)
        return None
    grbs = pygrib.open(gribfn)
    try:
        gs = grbs.select(shortName="st")
    except ValueError:
        LOG.info("failed to find st in %s", gribfn)
        return None
    for g in gs:
        if str(g).find("levels 0.0-0.1 m") > 0:
            return g


def do_nam(valid):
    """Compute county level estimates based on NAM data"""
    # run 6z to 6z, close enough
    now = datetime.datetime(valid.year, valid.month, valid.day, 6)
    lats = None
    lons = None
    count = 0
    grib = None
    for offset in [0, 6, 12, 18]:
        runtime = now + datetime.timedelta(hours=offset)
        for fhour in range(6):
            grib = get_grib(runtime, fhour)
            if grib is None:
                continue
            if lats is None:
                lats, lons = grib.latlons()
                data = np.zeros(np.shape(lats))
    if grib is None or lats is None:
        LOG.info("Failed to find NAM data for %s", valid)
        return
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


def main(argv):
    """Go Main Go"""
    nt = Table("ISUSM")
    qdict = loadqc()

    idbconn = get_dbconn("isuag", user="nobody")
    pdbconn = get_dbconn("postgis", user="nobody")

    day_ago = int(argv[1])
    ts = datetime.date.today() - datetime.timedelta(days=day_ago)
    hlons, hlats, hvals = do_nam(ts)
    nam = temperature(hvals, "K").value("F")
    window = np.ones((3, 3))
    nam = convolve2d(nam, window / window.sum(), mode="same", boundary="symm")

    # mp = MapPlot(sector='midwest')
    # mp.pcolormesh(hlons, hlats, nam,
    #              range(20, 90, 5))
    # mp.postprocess(filename='test.png')
    # sys.exit()

    # Query out the data
    df = read_sql(
        """
        WITH ranges as (
            select station, count(*), min(tsoil_c_avg_qc),
            max(tsoil_c_avg_qc) from sm_hourly WHERE
            valid >= %s and valid < %s and tsoil_c_avg_qc > -40
            and tsoil_c_avg_qc < 50 GROUP by station
        )
        SELECT d.station, d.tsoil_c_avg_qc,
        r.max as hourly_max_c, r.min as hourly_min_c, r.count
         from sm_daily d JOIN ranges r on (d.station = r.station)
        where valid = %s and tsoil_c_avg_qc > -40 and r.count > 19
    """,
        idbconn,
        params=(ts, ts + datetime.timedelta(days=1), ts),
        index_col="station",
    )
    for col, newcol in zip(
        ["tsoil_c_avg_qc", "hourly_min_c", "hourly_max_c"],
        ["ob", "min", "max"],
    ):
        df[newcol] = temperature(df[col].values, "C").value("F")
        df.drop(col, axis=1, inplace=True)

    for stid, row in df.iterrows():
        df.at[stid, "ticket"] = qdict.get(stid, {}).get("soil4", False)
        x, y = get_idx(hlons, hlats, nt.sts[stid]["lon"], nt.sts[stid]["lat"])
        df.at[stid, "nam"] = nam[x, y]
        df.at[stid, "lat"] = nt.sts[stid]["lat"]
        df.at[stid, "lon"] = nt.sts[stid]["lon"]
    # ticket is an object type from above
    df = df[~df["ticket"].astype("bool")]
    df["diff"] = df["ob"] - df["nam"]
    bias = df["diff"].mean()
    nam = nam + bias
    LOG.info("NAM bias correction of: %.2fF applied", bias)
    # apply nam bias to sampled data
    df["nam"] += bias
    df["diff"] = df["ob"] - df["nam"]
    # we are going to require data be within 1 SD of sampled or 5 deg
    std = 5.0 if df["nam"].std() < 5.0 else df["nam"].std()
    for station in df[df["diff"].abs() > std].index.values:
        LOG.info(
            "%s QC'd %s out std: %.2f, ob:%.1f nam:%.1f",
            ts.strftime("%Y%m%d"),
            station,
            std,
            df.at[station, "ob"],
            df.at[station, "nam"],
        )
        df.drop(station, inplace=True)

    # Query out centroids of counties...
    cdf = read_sql(
        """SELECT ST_x(ST_centroid(the_geom)) as lon,
        ST_y(ST_centroid(the_geom)) as lat
        from uscounties WHERE state_name = 'Iowa'
    """,
        pdbconn,
        index_col=None,
    )
    for i, row in cdf.iterrows():
        x, y = get_idx(hlons, hlats, row["lon"], row["lat"])
        cdf.at[i, "nam"] = nam[x, y]

    mp = MapPlot(
        sector="iowa",
        title=("Average 4 inch Depth Soil Temperatures for %s")
        % (ts.strftime("%b %d, %Y"),),
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
        df["lon"], df["lat"], df["ob"], fmt="%.0f", color="r", labelbuffer=5
    )
    mp.plot_values(
        cdf["lon"],
        cdf["lat"],
        cdf["nam"],
        fmt="%.0f",
        textsize=11,
        labelbuffer=5,
    )
    mp.drawcounties()
    routes = "a" if day_ago >= 4 else "ac"
    pqstr = (
        "plot %s %s0000 soilt_day%s.png isuag_county_4inch_soil.png png"
    ) % (routes, ts.strftime("%Y%m%d"), day_ago)
    mp.postprocess(pqstr=pqstr)
    mp.close()


if __name__ == "__main__":
    main(sys.argv)
