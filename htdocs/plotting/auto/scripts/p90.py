"""UGC/Polygon WWA stats onimbus"""
import datetime

import psycopg2.extras
import numpy as np
import pytz
from rasterstats import zonal_stats
import pandas as pd
from pandas.io.sql import read_sql
from geopandas import read_postgis
from affine import Affine
from pyiem.nws import vtec
from pyiem.reference import state_names, state_bounds, wfo_bounds
from pyiem.plot import get_cmap
from pyiem.plot.geoplot import MapPlot
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = {"cwa": "Plot by NWS Forecast Office", "state": "Plot by State"}
PDICT2 = {
    "yearcount": "Count of Events for Given Year",
    "days": "Days Since Last Issuance",
    "hour": "Most Frequent Issuance Hour of Day",
    "total": "Total Count between Start and End Date",
    "lastyear": "Year of Last Issuance",
    "yearavg": "Yearly Average Count between Start and End Year",
    "periodavg": (
        "Yearly Average Count between Start and End DateTime Bounded by Years"
    ),
    "periodmin": (
        "Yearly Minimum Count between Start and End DateTime Bounded by Years"
    ),
    "periodmax": (
        "Yearly Maximum Count between Start and End DateTime Bounded by Years"
    ),
}
PDICT3 = {
    "yes": "YES: Label Counties/Zones",
    "no": "NO: Do not Label Counties/Zones",
}
PDICT4 = {
    "ugc": "Summarize/Plot by UGC (Counties/Parishes/Zones)",
    "polygon": "Summarize/Plot by Polygon (Storm Based Warnings)",
}
PDICT5 = {
    "yes": "YES: Draw Counties/Parishes",
    "no": "NO: Do Not Draw Counties/Parishes",
}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This application has a considerable and likely
    confusing amount of configuration options.  The biggest source of the
    confusion is the interplay between the statistic chosen and the dates/times
    provided.  This table summarizes that interplay.<br />

    <table>
    <thead><tr><th>Statistic</th><th>Uses</th><th>Application</th></tr></thead>
    <tbody>
    <tr>
    <td>Days Since</td>
    <td>Start/End Date Time</td>
    <td>This plots the number of "days" since the last issuance of a given
    headline between the start and end date times that you provide.  The
    concept of "days" is 24 hour periods.</td>
    </tr>

    <tr>
    <td>Last Year</td>
    <td>Start/End Date Time</td>
    <td>This plots the most recent year of issuance for a given warning type.
    </td>
    </tr>

    <tr>
    <td>Most Frequent Hour</td>
    <td>Start/End Date Time</td>
    <td>This plots only works for UGC summarization. It attempts to plot the
    hour of the day with the most frequent number of events issued. Not that
    for long-fuse warnings, these type of plot is likely ill-defined.</td>
    </tr>

    <tr>
    <td>Total Count</td>
    <td>Start/End Date Time</td>
    <td>This plots the total number of events between the start and end
    date time.</td>
    </tr>

    <tr>
    <td>Year Average</td>
    <td>Start/End Year</td>
    <td>This plots the average number of events between the inclusive start
    and end year. The caveat is that it uses the actual found time domain
    of warnings within those years to compute a yearly average. So if you
    pick a year period between 2005 to 2010 and no warnings were issued in
    2005, it would then use 2006 to 2010 to compute the yearly average.</td>
    </tr>

    <tr>
    <td>Year Count</td>
    <td>Start Year</td>
    <td>This plots the number of events for a given year.  A year is defined
    as the calendar year in US Central Time.</td>
    </tr>

    <tr>
    <td>Yearly Min/Avg/Max Count bounded...</td>
    <td>Start/End Date Time<br />Start/End Year</td>
    <td>This plots the min/avg/max number of events per year between the
    given dates.  For example, you could produce a plot of the average
    number of Tornado Warnings during June.  Please note that only the
    average plot works when summarizing by polygons.</td>
    </tr>

    </table>

    <p>In general, it will produce
    a map of either a single NWS Weather Forecast Office (WFO) or for a
    specified state.  For warning types that are issued with polygons, you
    can optionally plot heatmaps of these products.  Please be careful when
    selecting start and end dates to ensure you are getting the plot you
    want.  There are likely some combinations here that will produce a
    broken image symbol.  If you find such a case, please email us the link
    to this page that shows the broken image!</p>

    <p>Storm Based Warning polygons were not official until 1 October 2007,
    so if you generate plots for years prior to this date, you may notice
    polygons well outside the County Warning Area bounds.  There was no
    enforcement of these unofficial polygons to stay within CWA bounds.</p>

    <p><strong>This app can be very slow</strong>, so please let it grind
    away as sometimes it will take 3-5 minutes to generate a map :("""
    today = datetime.date.today()
    jan1 = today.replace(day=1, month=1)
    desc["arguments"] = [
        dict(
            type="select",
            name="t",
            default="state",
            options=PDICT,
            label="Select plot extent type:",
        ),
        dict(
            type="select",
            name="v",
            default="lastyear",
            options=PDICT2,
            label="Select statistic to plot:",
        ),
        dict(
            type="select",
            name="ilabel",
            default="yes",
            options=PDICT3,
            label="Overlay values on map?",
        ),
        dict(
            type="select",
            name="geo",
            default="ugc",
            options=PDICT4,
            label="Plot by UGC (Counties/Parishes/Zones) or Polygons?",
        ),
        dict(
            type="select",
            name="drawc",
            default="yes",
            options=PDICT5,
            label="Plot County/Parish borders on polygon summary maps?",
        ),
        dict(
            type="year",
            min=1986,
            name="year",
            default=today.year,
            label="Select start year (only for year count/average):",
        ),
        dict(
            type="year",
            min=1986,
            name="year2",
            default=today.year,
            label="Select end year (only for year count/average) (inclusive):",
        ),
        dict(
            type="datetime",
            name="sdate",
            default=jan1.strftime("%Y/%m/%d 0000"),
            label="Start DateTime UTC:",
            min="1986/01/01 0000",
        ),
        dict(
            type="datetime",
            name="edate",
            default=today.strftime("%Y/%m/%d 0000"),
            label="End DateTime UTC:",
            min="1986/01/01 0000",
        ),
        dict(
            type="networkselect",
            name="station",
            network="WFO",
            default="DMX",
            label="Select WFO: (ignored if plotting state)",
        ),
        dict(
            type="state",
            name="state",
            default="IA",
            label="Select State: (ignored if plotting wfo)",
        ),
        dict(
            type="phenomena",
            name="phenomena",
            default="TO",
            label="Select Watch/Warning Phenomena Type:",
        ),
        dict(
            type="significance",
            name="significance",
            default="A",
            label="Select Watch/Warning Significance Level:",
        ),
        dict(type="cmap", name="cmap", default="jet", label="Color Ramp:"),
        dict(
            optional=True,
            name="interval",
            type="float",
            default=1,
            label=(
                "Specify an interval for the colorbar to use instead of "
                "dynamic. (optional)"
            ),
        ),
    ]
    return desc


def do_polygon(ctx):
    """polygon workflow"""
    pgconn = get_dbconn("postgis")
    varname = ctx["v"]
    station = ctx["station"][:4]
    state = ctx["state"]
    phenomena = ctx["phenomena"]
    significance = ctx["significance"]
    t = ctx["t"]
    sdate = ctx["sdate"]
    edate = ctx["edate"]
    year = ctx["year"]
    year2 = ctx["year2"]
    # figure out the start and end timestamps
    if varname in ["total", "days"]:
        sts = sdate
        ets = edate
    elif varname == "hour":
        raise NoDataFound("Sorry, not implemented for polygon summaries.")
    elif varname == "yearcount":
        sts = datetime.datetime(year, 1, 1).replace(tzinfo=pytz.utc)
        ets = datetime.datetime(year, 12, 31, 23, 59).replace(tzinfo=pytz.utc)
    else:
        sts = datetime.datetime(year, 1, 1).replace(tzinfo=pytz.utc)
        ets = datetime.datetime(year2, 12, 31, 23, 59).replace(tzinfo=pytz.utc)
    daylimiter = ""
    if varname.startswith("period"):
        if sdate.strftime("%m%d") > edate.strftime("%m%d"):
            daylimiter = (
                f"(to_char(issue, 'mmdd') >= '{sdate.strftime('%m%d')}' or "
                f"to_char(issue, 'mmdd') < '{edate.strftime('%m%d')}') and "
            )
            (sdate, edate) = (edate, sdate)
        else:
            daylimiter = (
                f"to_char(issue, 'mmdd') >= '{sdate.strftime('%m%d')}' and "
                f"to_char(issue, 'mmdd') < '{edate.strftime('%m%d')}' and "
            )
    # We need to figure out how to get the warnings either by state or by wfo
    if t == "cwa":
        (west, south, east, north) = wfo_bounds[station]
    else:
        (west, south, east, north) = state_bounds[state]
    # buffer by 5 degrees so to hopefully get all polys
    (west, south) = [x - 2 for x in (west, south)]
    (east, north) = [x + 2 for x in (east, north)]
    # create grids
    griddelta = 0.01
    lons = np.arange(west, east, griddelta)
    lats = np.arange(south, north, griddelta)
    YSZ = len(lats)
    XSZ = len(lons)
    lons, lats = np.meshgrid(lons, lats)
    affine = Affine(griddelta, 0.0, west, 0.0, 0 - griddelta, north)
    ones = np.ones((int(YSZ), int(XSZ)))
    counts = np.zeros((int(YSZ), int(XSZ)))
    wfolimiter = ""
    if ctx["t"] == "cwa":
        wfolimiter = " wfo = '%s' and " % (station,)
    # do arbitrary buffer to prevent segfaults?
    df = read_postgis(
        f"""
    SELECT ST_Forcerhr(ST_Buffer(geom, 0.0005)) as geom, issue, expire,
    extract(epoch from %s::timestamptz - issue) / 86400. as days
    from sbw where {wfolimiter} {daylimiter}
    phenomena = %s and status = 'NEW' and significance = %s
    and ST_Within(geom, ST_GeomFromEWKT('SRID=4326;POLYGON((%s %s, %s %s,
    %s %s, %s %s, %s %s))')) and ST_IsValid(geom)
    and issue >= %s and issue <= %s ORDER by issue ASC
    """,
        pgconn,
        params=(
            ets,
            phenomena,
            significance,
            west,
            south,
            west,
            north,
            east,
            north,
            east,
            south,
            west,
            south,
            sts,
            ets,
        ),
        geom_col="geom",
        index_col=None,
    )
    if df.empty:
        raise NoDataFound("No data found for query.")
    zs = zonal_stats(
        df["geom"],
        ones,
        affine=affine,
        nodata=-1,
        all_touched=True,
        raster_out=True,
    )
    for i, z in enumerate(zs):
        aff = z["mini_raster_affine"]
        mywest = aff.c
        mynorth = aff.f
        raster = np.flipud(z["mini_raster_array"])
        x0 = int((mywest - west) / griddelta)
        y1 = int((mynorth - south) / griddelta)
        dy, dx = np.shape(raster)
        x1 = x0 + dx
        y0 = y1 - dy
        if x0 < 0 or x1 >= XSZ or y0 < 0 or y1 >= YSZ:
            # print raster.mask.shape, west, x0, x1, XSZ, north, y0, y1, YSZ
            continue
        if varname == "lastyear":
            counts[y0:y1, x0:x1] = np.where(
                raster.mask, counts[y0:y1, x0:x1], df.iloc[i]["issue"].year
            )
        elif varname == "days":
            counts[y0:y1, x0:x1] = np.where(
                raster.mask, counts[y0:y1, x0:x1], df.iloc[i]["days"]
            )
        else:
            counts[y0:y1, x0:x1] += np.where(raster.mask, 0, 1)
    if np.max(counts) == 0:
        raise NoDataFound("Sorry, no data found for query!")
    # construct the df
    ctx["df"] = pd.DataFrame(
        {"lat": lats.ravel(), "lon": lons.ravel(), "val": counts.ravel()}
    )
    minv = df["issue"].min()
    maxv = df["issue"].max()
    if varname == "lastyear":
        ctx["title"] = "Year of Last"
        if (maxv.year - minv.year) < 3:
            bins = range(int(minv.year) - 4, int(maxv.year) + 2)
        else:
            bins = range(int(minv.year), int(maxv.year) + 2)
        ctx["units"] = "year"
        ctx["subtitle"] = (" between %s and %s UTC") % (
            sdate.strftime("%d %b %Y %H%M"),
            edate.strftime("%d %b %Y %H%M"),
        )
    elif varname == "days":
        ctx["title"] = PDICT2[varname]
        bins = np.linspace(
            max([df["days"].min() - 7, 0]), df["days"].max() + 7, 12, dtype="i"
        )
        counts = np.where(counts < 0.0001, -1, counts)
        ctx["subtitle"] = (" between %s and %s UTC") % (
            sdate.strftime("%d %b %Y %H%M"),
            edate.strftime("%d %b %Y %H%M"),
        )
        ctx["units"] = "days"
        ctx["extend"] = "neither"
    elif varname == "yearcount":
        ctx["title"] = "Count for %s" % (year,)
        ctx["units"] = "count"
    elif varname == "total":
        ctx["title"] = "Total"
        ctx["subtitle"] = (" between %s and %s UTC") % (
            sdate.strftime("%d %b %Y %H%M"),
            edate.strftime("%d %b %Y %H%M"),
        )
        ctx["units"] = "count"
    elif varname == "yearavg":
        ctx["title"] = ("Yearly Avg: %s and %s") % (
            minv.strftime("%d %b %Y"),
            maxv.strftime("%d %b %Y"),
        )
        years = (maxv.year - minv.year) + 1
        counts = counts / years
        ctx["units"] = "count per year"
    elif varname == "periodavg":
        ctx["title"] = ("Yearly %s between %s and %s [%s-%s]") % (
            varname.replace("period", ""),
            sdate.strftime("%d %b"),
            edate.strftime("%d %b"),
            year,
            year2,
        )
        years = (maxv.year - minv.year) + 1
        counts = counts / years
        ctx["units"] = "count per year"
    else:
        raise NoDataFound(
            "Sorry, your select combination is too complex for me!"
        )

    maxv = np.max(counts)
    if varname not in ["lastyear", "days"]:
        if ctx.get("interval") is not None:
            interval = float(ctx["interval"])
            bins = np.arange(0, interval * 10.1, interval)
            bins[0] = 0.01
        elif varname == "total":
            if maxv < 8:
                bins = np.arange(1, 8, 1)
            else:
                bins = np.linspace(1, maxv + 3, 10, dtype="i")
        else:
            for delta in [500, 50, 5, 1, 0.5, 0.25, 0.10, 0.05]:
                bins = np.arange(0, (maxv + 1.0) * 1.05, delta)
                if len(bins) > 8:
                    break
            bins[0] = 0.01
    ctx["bins"] = bins
    ctx["data"] = counts
    ctx["lats"] = lats
    ctx["lons"] = lons


def do_ugc(ctx):
    """Do UGC based logic."""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    varname = ctx["v"]
    station = ctx["station"][:4]
    state = ctx["state"]
    phenomena = ctx["phenomena"]
    significance = ctx["significance"]
    t = ctx["t"]
    sdate = ctx["sdate"]
    edate = ctx["edate"]
    year = ctx["year"]
    year2 = ctx["year2"]
    df = None
    if varname in ["lastyear", "days"]:
        if t == "cwa":
            cursor.execute(
                """
            select ugc, max(issue at time zone 'UTC') from warnings
            WHERE wfo = %s and phenomena = %s and significance = %s and
            issue >= %s and issue < %s
            GROUP by ugc
            """,
                (
                    station if len(station) == 3 else station[1:],
                    phenomena,
                    significance,
                    sdate,
                    edate,
                ),
            )
        else:
            cursor.execute(
                """
            select ugc, max(issue at time zone 'UTC') from warnings
            WHERE substr(ugc, 1, 2) = %s and phenomena = %s
            and significance = %s and issue >= %s and issue < %s
            GROUP by ugc
            """,
                (state, phenomena, significance, sdate, edate),
            )
        rows = []
        data = {}
        for row in cursor:
            days = int(
                (edate - row[1].replace(tzinfo=pytz.UTC)).total_seconds()
                / 86400.0
            )
            rows.append(
                dict(days=days, valid=row[1], year=row[1].year, ugc=row[0])
            )
            data[row[0]] = row[1].year if varname == "lastyear" else days
        ctx["title"] = "%s-%s %s" % (
            sdate.strftime("%-d %b %Y"),
            edate.strftime("%-d %b %Y"),
            "Year of Last" if varname == "lastyear" else PDICT2[varname],
        )
        datavar = "year" if varname == "lastyear" else "days"
    elif varname == "yearcount":
        table = "warnings_%s" % (year,)
        if t == "cwa":
            cursor.execute(
                f"""
            select ugc, count(*) from {table}
            WHERE wfo = %s and phenomena = %s and significance = %s
            GROUP by ugc
            """,
                (
                    station if len(station) == 3 else station[1:],
                    phenomena,
                    significance,
                ),
            )
        else:
            cursor.execute(
                f"""
            select ugc, count(*) from {table}
            WHERE substr(ugc, 1, 2) = %s and phenomena = %s
            and significance = %s GROUP by ugc
            """,
                (state, phenomena, significance),
            )
        rows = []
        data = {}
        for row in cursor:
            rows.append(dict(count=row[1], year=year, ugc=row[0]))
            data[row[0]] = row[1]
        ctx["title"] = "Count for %s" % (year,)
        datavar = "count"
    elif varname == "total":
        if t == "cwa":
            cursor.execute(
                """
            select ugc, count(*), min(issue at time zone 'UTC'),
            max(issue at time zone 'UTC') from warnings
            WHERE wfo = %s and phenomena = %s and significance = %s
            and issue >= %s and issue <= %s
            GROUP by ugc
            """,
                (
                    station if len(station) == 3 else station[1:],
                    phenomena,
                    significance,
                    sdate,
                    edate,
                ),
            )
        else:
            cursor.execute(
                """
            select ugc, count(*), min(issue at time zone 'UTC'),
            max(issue at time zone 'UTC') from warnings
            WHERE substr(ugc, 1, 2) = %s and phenomena = %s
            and significance = %s and issue >= %s and issue < %s
            GROUP by ugc
            """,
                (state, phenomena, significance, sdate, edate),
            )
        rows = []
        data = {}
        for row in cursor:
            rows.append(
                dict(
                    count=row[1],
                    year=year,
                    ugc=row[0],
                    minissue=row[2],
                    maxissue=row[3],
                )
            )
            data[row[0]] = row[1]
        ctx["title"] = "Total"
        ctx["subtitle"] = (" between %s and %s UTC") % (
            sdate.strftime("%d %b %Y %H%M"),
            edate.strftime("%d %b %Y %H%M"),
        )
        datavar = "count"
    elif varname == "hour":
        cursor.execute(
            """
        WITH data as (
        SELECT ugc, issue at time zone tzname as v
        from warnings w JOIN stations t
        ON (w.wfo =
            (case when length(t.id) = 4 then substr(t.id, 1, 3) else t.id end))
        WHERE t.network = 'WFO' and
        phenomena = %s and significance = %s and issue >= %s and issue < %s),
        agg as (
            SELECT ugc, extract(hour from v) as hr, count(*) from data
            GROUP by ugc, hr),
        ranks as (
            SELECT ugc, hr, rank() OVER (PARTITION by ugc ORDER by count DESC)
            from agg)

        SELECT ugc, hr from ranks where rank = 1
        """,
            (phenomena, significance, sdate, edate),
        )
        rows = []
        data = {}
        ctx["labels"] = {}
        midnight = datetime.datetime(2000, 1, 1)
        for row in cursor:
            rows.append(dict(hour=int(row[1]), ugc=row[0]))
            data[row[0]] = row[1]
            ctx["labels"][row[0]] = (
                midnight + datetime.timedelta(hours=row[1])
            ).strftime("%-I %p")
        ctx["title"] = ("Most Freq. Issue Hour: %s and %s") % (
            sdate.strftime("%d %b %Y"),
            edate.strftime("%d %b %Y"),
        )
        datavar = "hour"
    elif varname == "yearavg":
        if t == "cwa":
            cursor.execute(
                """
            select ugc, count(*), min(issue at time zone 'UTC'),
            max(issue at time zone 'UTC') from warnings
            WHERE wfo = %s and phenomena = %s and significance = %s
            and issue >= %s and issue <= %s
            GROUP by ugc
            """,
                (
                    station if len(station) == 3 else station[1:],
                    phenomena,
                    significance,
                    datetime.date(year, 1, 1),
                    datetime.date(year2 + 1, 1, 1),
                ),
            )
        else:
            cursor.execute(
                """
            select ugc, count(*), min(issue at time zone 'UTC'),
            max(issue at time zone 'UTC') from warnings
            WHERE substr(ugc, 1, 2) = %s and phenomena = %s
            and significance = %s and issue >= %s and issue < %s
            GROUP by ugc
            """,
                (
                    state,
                    phenomena,
                    significance,
                    datetime.date(year, 1, 1),
                    datetime.date(year2 + 1, 1, 1),
                ),
            )
        rows = []
        data = {}
        minv = datetime.datetime(2050, 1, 1)
        maxv = datetime.datetime(1986, 1, 1)
        for row in cursor:
            if row[2] < minv:
                minv = row[2]
            if row[3] > maxv:
                maxv = row[3]
            rows.append(
                dict(
                    count=row[1],
                    year=year,
                    ugc=row[0],
                    minissue=row[2],
                    maxissue=row[3],
                )
            )
            data[row[0]] = row[1]
        ctx["title"] = ("Yearly Avg: %s and %s") % (
            minv.strftime("%d %b %Y"),
            maxv.strftime("%d %b %Y"),
        )
        datavar = "count"
    elif varname.startswith("period"):
        if sdate.strftime("%m%d") > edate.strftime("%m%d"):
            daylimiter = (
                f"and (to_char(issue, 'mmdd') >= '{sdate.strftime('%m%d')}' "
                f"or to_char(issue, 'mmdd') < '{edate.strftime('%m%d')}') "
            )
            (sdate, edate) = (edate, sdate)
        else:
            daylimiter = (
                f"and to_char(issue, 'mmdd') >= '{sdate.strftime('%m%d')}' "
                f"and to_char(issue, 'mmdd') < '{edate.strftime('%m%d')}' "
            )
        aggstat = varname.replace("period", "")
        if t == "cwa":
            df = read_sql(
                f"""WITH data as (
            select ugc, extract(year from issue) as year,
            count(*), min(issue at time zone 'UTC') as nv,
            max(issue at time zone 'UTC') as mv from warnings
            WHERE wfo = %s and phenomena = %s and significance = %s
            and issue >= %s and issue <= %s {daylimiter}
            GROUP by ugc, year
            )
            SELECT ugc, sum(count) as total, {aggstat}(count) as datum,
            min(nv) as minvalid, max(mv) as maxvalid, count(*)::int as years
            from data GROUP by ugc
            """,
                pgconn,
                params=(
                    station if len(station) == 3 else station[1:],
                    phenomena,
                    significance,
                    datetime.date(year, 1, 1),
                    datetime.date(year2 + 1, 1, 1),
                ),
                index_col="ugc",
            )
        else:
            df = read_sql(
                f"""WITH data as (
            select ugc, extract(year from issue) as year,
            count(*), min(issue at time zone 'UTC') as nv,
            max(issue at time zone 'UTC') as mv from warnings
            WHERE substr(ugc, 1, 2) = %s and phenomena = %s
            and significance = %s and issue >= %s and issue < %s {daylimiter}
            GROUP by ugc, year
            )
            SELECT ugc, sum(count) as total, {aggstat}(count) as datum,
            min(nv) as minvalid, max(mv) as maxvalid, count(*)::int as years
            from data GROUP by ugc
            """,
                pgconn,
                params=(
                    state,
                    phenomena,
                    significance,
                    datetime.date(year, 1, 1),
                    datetime.date(year2 + 1, 1, 1),
                ),
                index_col="ugc",
            )
        if df.empty:
            raise NoDataFound("No events found for query.")
        df["minvalid"] = pd.to_datetime(df["minvalid"])
        df["maxvalid"] = pd.to_datetime(df["maxvalid"])
        minv = df["minvalid"].min()
        maxv = df["maxvalid"].max()
        ctx["title"] = ("Yearly %s between %s and %s [%s-%s]") % (
            aggstat,
            minv.strftime("%d %b"),
            maxv.strftime("%d %b"),
            minv.year,
            maxv.year,
        )
        datavar = "datum"
        if varname == "periodavg":
            data = df["total"].to_dict()
            datavar = "total"
        elif varname == "periodmin":
            years = maxv.year - minv.year + 1
            df.at[df["years"] != years, "datum"] = 0
            data = df["datum"].to_dict()
        else:
            data = df["datum"].to_dict()

    if df is None and not rows:
        raise NoDataFound("Sorry, no data found for query!")
    if df is None:
        df = pd.DataFrame(rows)
    if varname in ["yearavg", "periodavg"]:
        years = maxv.year - minv.year + 1
        df["average"] = df[datavar] / years
        for key in data:
            data[key] = round(data[key] / float(years), 2)
        maxv = df["average"].max()
        if ctx.get("interval") is not None:
            interval = float(ctx["interval"])
            bins = np.arange(0, interval * 10.1, interval)
            bins[0] = 0.01
        else:
            for delta in [500, 50, 5, 1, 0.5, 0.05]:
                bins = np.arange(0, (maxv + 1.0) * 1.05, delta)
                if len(bins) > 8:
                    break
            if len(bins) > 8:
                bins = bins[:: int(len(bins) / 8.0)]
            bins[0] = 0.01
        ctx["units"] = "count per year"
    elif varname == "hour":
        bins = list(range(0, 25))
        ctx["units"] = "hour of day"
    else:
        bins = list(
            np.arange(np.min(df[datavar][:]), np.max(df[datavar][:]) + 2, 1)
        )
        if len(bins) < 3:
            bins.append(bins[-1] + 1)
        if len(bins) > 8:
            bins = np.linspace(
                np.min(df[datavar][:]),
                np.max(df[datavar][:]) + 2,
                8,
                dtype="i",
            )
        ctx["units"] = "count"
    ctx["bins"] = bins
    ctx["data"] = data
    ctx["df"] = df


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())
    # Covert datetime to UTC
    ctx["sdate"] = ctx["sdate"].replace(tzinfo=pytz.utc)
    ctx["edate"] = ctx["edate"].replace(tzinfo=pytz.utc)
    state = ctx["state"]
    phenomena = ctx["phenomena"]
    significance = ctx["significance"]
    station = ctx["station"][:4]
    t = ctx["t"]
    ilabel = ctx["ilabel"] == "yes"
    geo = ctx["geo"]
    if geo == "ugc":
        do_ugc(ctx)
    elif geo == "polygon":
        do_polygon(ctx)

    subtitle = "based on IEM Archives %s" % (ctx.get("subtitle", ""),)
    if t == "cwa":
        subtitle = "Plotted for %s (%s), %s" % (
            ctx["_nt"].sts[station]["name"],
            station,
            subtitle,
        )
    else:
        subtitle = "Plotted for %s, %s" % (state_names[state], subtitle)
    m = MapPlot(
        sector=("state" if t == "state" else "cwa"),
        state=state,
        cwa=(station if len(station) == 3 else station[1:]),
        axisbg="white",
        title=("%s %s (%s.%s)")
        % (
            ctx["title"],
            vtec.get_ps_string(phenomena, significance),
            phenomena,
            significance,
        ),
        subtitle=subtitle,
        nocaption=True,
        titlefontsize=16,
    )
    cmap = get_cmap(ctx["cmap"])
    cmap.set_under("white")
    cmap.set_over("white")
    if geo == "ugc":
        if ctx["v"] == "hour":
            cl = [
                "Mid",
                "",
                "2 AM",
                "",
                "4 AM",
                "",
                "6 AM",
                "",
                "8 AM",
                "",
                "10 AM",
                "",
                "Noon",
                "",
                "2 PM",
                "",
                "4 PM",
                "",
                "6 PM",
                "",
                "8 PM",
                "",
                "10 PM",
                "",
            ]
            m.fill_ugcs(
                ctx["data"],
                bins=ctx["bins"],
                cmap=cmap,
                ilabel=ilabel,
                labels=ctx["labels"],
                clevstride=2,
                clevlabels=cl,
                labelbuffer=1,  # Texas yall
                extend="neither",
                is_firewx=(phenomena == "FW"),
            )
        else:
            m.fill_ugcs(
                ctx["data"],
                bins=ctx["bins"],
                cmap=cmap,
                ilabel=ilabel,
                labelbuffer=1,  # Texas yall
                is_firewx=(phenomena == "FW"),
            )
    else:
        res = m.pcolormesh(
            ctx["lons"],
            ctx["lats"],
            ctx["data"],
            ctx["bins"],
            cmap=cmap,
            units=ctx["units"],
            extend=ctx.get("extend", "both"),
        )
        # Cut down on SVG et al size
        res.set_rasterized(True)
        if ctx["drawc"] == "yes":
            m.drawcounties()

    return m.fig, ctx["df"]


if __name__ == "__main__":
    fig, _df = plotter(
        dict(
            network="WFO",
            station="GJT",
            geo="ugc",
            drawc="yes",
            state="IA",
            phenomena="WW",
            significance="Y",
            interval=2,
            v="periodavg",
            ilabel="yes",
            t="cwa",
            year=1986,
            year2=2020,
            sdate="2019-11-01 0000",
            edate="2019-02-15 0000",
        )
    )
    fig.savefig("/tmp/test.png")
