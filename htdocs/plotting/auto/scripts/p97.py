"""map of climodat departures"""
import datetime
from collections import OrderedDict

import numpy as np
import pandas as pd
from pandas.io.sql import read_sql
import geopandas as gpd
from pyiem.plot import MapPlot, get_cmap
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = {
    "sector": "Plot by Sector / State",
    "wfo": "Plot by NWS Weather Forecast Office (WFO)",
}
PDICT2 = OrderedDict(
    [
        ("max_high_temp", "Maximum High Temperature"),
        ("avg_high_temp", "Average High Temperature"),
        ("avg_temp_depart", "Average Temperature Departure"),
        ("avg_temp", "Average Temperature"),
        ("min_low_temp", "Minimum Low Temperature"),
        ("avg_low_temp", "Average Low Temperature"),
        ("gdd_sum", "Growing Degree Days ($base/$ceil) Total"),
        ("cgdd_sum", "Growing Degree Days ($base/$ceil) Climatology"),
        ("gdd_depart", "Growing Degree Days ($base/$ceil) Departure"),
        (
            "gdd_percent",
            "Growing Degree Days ($base/$ceil) Percent of Average",
        ),
        ("cdd65_sum", "Cooling Degree Days (base 65)"),
        ("cdd65_depart", "Cooling Degree Days Departure (base 65)"),
        ("hdd65_sum", "Heating Degree Days (base 65)"),
        ("hdd65_depart", "Heating Degree Days Departure (base 65)"),
        ("precip_depart", "Precipitation Departure"),
        ("precip_percent", "Precipitation Percent of Average"),
        ("precip_sum", "Precipitation Total"),
        ("snow_depart", "Snowfall Departure"),
        ("snow_percent", "Snowfall Percent of Average"),
        ("snow_sum", "Snowfall Total"),
    ]
)
PDICT4 = {
    "yes": "Yes, overlay Drought Monitor",
    "no": "No, do not overlay Drought Monitor",
}
UNITS = {
    "min_low_temp": "F",
    "avg_low_temp": "F",
    "avg_high_temp": "F",
    "gdd_depart": "F",
    "gdd_percet": "%",
    "gdd_sum": "F",
    "cdd_sum": "F",
    "hdd_sum": "F",
    "cdd_depart": "F",
    "hdd_depart": "F",
    "cgdd_sum": "F",
    "avg_temp_depart": "F",
    "avg_temp": "F",
    "precip_depart": "inch",
    "precip_sum": "inch",
    "precip_percent": "%",
    "snow_depart": "inch",
    "snow_sum": "inch",
    "snow_percent": "%",
}
PDICT3 = {
    "contour": "Contour the data",
    "text": "Plot just values without contours",
}
PDICT5 = {"yes": "Label Station Values", "no": "Do Not Label Station Values"}
PDICT6 = {
    "climate51": "IEM Climatology 1951-present",
    "climate71": "IEM Climatology 1971-present",
    "climate81": "IEM Climatology 1981-present",
}
GDD_KNOWN_BASES = [32, 41, 46, 48, 50, 51, 52]


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc[
        "description"
    ] = """This application plots an analysis of station
    data for a period of your choice.  Spatially aggregated values like those
    for climate districts and statewide averages are not included.  For this
    application, climatology is based on averaged observations for the
    climatology period you pick.
    """
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    desc["arguments"] = [
        dict(
            type="select",
            options=PDICT,
            default="sector",
            label="Select spatial domain type to plot:",
            name="d",
        ),
        dict(
            type="csector", name="sector", default="IA", label="Plot Sector:"
        ),
        dict(
            type="networkselect",
            default="DMX",
            network="WFO",
            label="NWS WFO to plot (when selected above for domain):",
            name="wfo",
        ),
        dict(
            type="select",
            name="var",
            default="precip_depart",
            label="Which Variable to Plot:",
            options=PDICT2,
        ),
        dict(
            type="int",
            default=50,
            name="gddbase",
            label=(
                "Growing Degree Day base(F)<br />if you choose a sector "
                "covering more than 10 states, you are limited to values of "
                "32, 41, 46, 48, 50, 51, 52 (long story why)"
            ),
        ),
        dict(
            type="int",
            default=86,
            name="gddceil",
            label=(
                "Growing Degree Day ceiling(F)<br />if you choose a sector "
                "covering more than 10 states, thist must be 86 "
                "(long story why)"
            ),
        ),
        dict(
            type="date",
            name="date1",
            default=(today - datetime.timedelta(days=30)).strftime("%Y/%m/%d"),
            label="Start Date:",
            min="1893/01/01",
        ),
        dict(
            type="select",
            name="usdm",
            default="no",
            label="Overlay Drought Monitor",
            options=PDICT4,
        ),
        dict(
            type="date",
            name="date2",
            default=today.strftime("%Y/%m/%d"),
            label="End Date (inclusive):",
            min="1893/01/01",
        ),
        dict(
            type="select",
            name="p",
            default="contour",
            label="Data Presentation Options",
            options=PDICT3,
        ),
        dict(type="cmap", name="cmap", default="RdYlBu", label="Color Ramp:"),
        dict(
            type="select",
            options=PDICT5,
            default="yes",
            name="c",
            label="Label Values?",
        ),
        dict(
            type="select",
            options=PDICT6,
            label="Which IEM Computed Climatology to Use",
            default="climate51",
            name="ct",
        ),
        dict(
            type="text",
            name="cull",
            default="",
            label=(
                "Space or comma separated IEM stations ids (ST####) to cull "
                "from the plot."
            ),
        ),
    ]
    return desc


def cull_to_list(vals):
    """Convert to a list for culling."""
    res = ["ZZZZZZ"]
    vals = vals.replace(",", " ")
    for val in vals.strip().split():
        res.append(val.upper()[:6])
    return res


def compute_tables_wfo(wfo):
    """Figure out which WFOs we need."""
    pgconn = get_dbconn("postgis")
    tables = []
    cursor = pgconn.cursor()
    cursor.execute(
        "SELECT distinct substr(ugc, 1, 2) from ugcs where substr(ugc, 3, 1) "
        "= 'C' and end_ts is null and wfo = %s",
        (wfo,),
    )
    for row in cursor:
        tables.append(f"alldata_{row[0].lower()}")
    return tables


def replace_gdd_climo(ctx, pgconn, df, table, date1, date2):
    """Here we are, incredible pain."""
    d1 = date1.strftime("%m%d")
    d2 = date2.strftime("%m%d")
    daylimit = f"sday >= '{d1}' and sday <= '{d2}'"
    if d1 > d2:
        daylimit = f"sday >= '{d2}' or sday <= '{d1}'"
    if (date2 - date1) > datetime.timedelta(days=365):
        daylimit = ""

    climo = read_sql(
        f"""WITH obs as (
            SELECT station, sday, avg(gddxx(%s, %s, high, low)) as datum from
            {table} GROUP by station, sday)
        select station, sum(datum) as gdd from obs
        WHERE {daylimit} GROUP by station ORDER by station
        """,
        pgconn,
        params=(ctx["gddbase"], ctx["gddceil"]),
        index_col="station",
    )
    climo.loc[climo["gdd"] == 0, "gdd"] = 1
    df["cgdd_sum"] = climo["gdd"]
    df["gdd_percent"] = df["gdd_sum"] / df["cgdd_sum"] * 100.0
    df["gdd_depart"] = df["gdd_sum"] - df["cgdd_sum"]
    return df


def get_data(ctx):
    """Compute the data needed for this app."""
    cull = cull_to_list(ctx["cull"])
    date1 = ctx["date1"]
    date2 = min([ctx["date2"], datetime.date.today()])
    pgconn = get_dbconn("coop")
    sector = ctx["sector"]
    table = "alldata_%s" % (sector,) if len(sector) == 2 else "alldata"
    tables = [table]
    dfs = []
    wfo_limiter = ""
    if sector == "iailin":
        tables = ["alldata_ia", "alldata_il", "alldata_in"]
    if ctx["d"] == "wfo":
        tables = compute_tables_wfo(ctx["wfo"])
        wfo_limiter = f" and t.wfo = '{ctx['wfo']}'"
    if "alldata" in tables or len(tables) > 9:
        if ctx["gddbase"] not in GDD_KNOWN_BASES:
            raise NoDataFound(f"GDD Base must be {','.join(GDD_KNOWN_BASES)}")
        ctx["gddceil"] = 86
    gddclimocol = "0"
    if ctx["gddbase"] in GDD_KNOWN_BASES:
        gddclimocol = f"gdd{ctx['gddbase']}"
    for table in tables:
        df = gpd.read_postgis(
            f"""
        WITH obs as (
            SELECT station, gddxx(%s, %s, high, low) as gdd,
            cdd(high, low, 65) as cdd65, hdd(high, low, 65) as hdd65,
            sday, high, low, precip, snow,
            (high + low)/2. as avg_temp
            from {table} WHERE
            day >= %s and day <= %s and
            substr(station, 3, 1) != 'C' and substr(station, 3, 4) != '0000'
            and station not in %s),
        climo as (
            SELECT station, to_char(valid, 'mmdd') as sday, precip, high, low,
            {gddclimocol} as gdd, cdd65, hdd65, snow
            from {ctx['ct']}),
        combo as (
            SELECT o.station, o.precip - c.precip as precip_diff,
            o.precip as precip, c.precip as cprecip,
            o.avg_temp, o.cdd65, o.hdd65,
            o.high, o.low, o.gdd, c.gdd as cgdd,
            o.gdd - c.gdd as gdd_diff,
            o.cdd65 - c.cdd65 as cdd_diff,
            o.hdd65 - c.hdd65 as hdd_diff,
            o.avg_temp - (c.high + c.low)/2. as temp_diff,
            o.snow as snow, c.snow as csnow,
            o.snow - c.snow as snow_diff
            from obs o JOIN climo c ON
            (o.station = c.station and o.sday = c.sday)),
        agg as (
            SELECT station,
            avg(avg_temp) as avg_temp,
            sum(precip_diff) as precip_depart,
            sum(precip) / greatest(sum(cprecip), 0.0001) * 100.
                as precip_percent,
            sum(snow_diff) as snow_depart,
            sum(snow) / greatest(sum(csnow), 0.0001) * 100. as snow_percent,
            sum(precip) as precip, sum(cprecip) as cprecip,
            sum(snow) as snow, sum(csnow) as csnow,
            avg(high) as avg_high_temp,
            avg(low) as avg_low_temp,
            max(high) as max_high_temp,
            min(low) as min_low_temp, sum(gdd_diff) as gdd_depart,
            sum(gdd) / greatest(1, sum(cgdd)) * 100. as gdd_percent,
            avg(temp_diff) as avg_temp_depart, sum(gdd) as gdd_sum,
            sum(cgdd) as cgdd_sum,
            sum(cdd65) as cdd_sum,
            sum(hdd65) as hdd_sum,
            sum(cdd_diff) as cdd_depart,
            sum(hdd_diff) as hdd_depart
            from combo GROUP by station)

        SELECT d.station, t.name, t.wfo,
        avg_temp,
        precip as precip_sum,
        cprecip as cprecip_sum,
        precip_depart,
        precip_percent,
        snow as snow_sum,
        csnow as csnow_sum,
        snow_depart,
        snow_percent,
        min_low_temp,
        avg_temp_depart,
        gdd_depart,
        gdd_sum,
        gdd_percent,
        cgdd_sum,
        max_high_temp,
        avg_high_temp,
        avg_low_temp,
        cdd_sum, hdd_sum, cdd_depart, hdd_depart,
        ST_x(t.geom) as lon, ST_y(t.geom) as lat,
        t.geom
        from agg d JOIN stations t on (d.station = t.id)
        WHERE t.network ~* 'CLIMATE' and t.online {wfo_limiter}
        """,
            pgconn,
            params=(
                ctx["gddbase"],
                ctx["gddceil"],
                date1,
                date2,
                tuple(cull),
            ),
            index_col="station",
            geom_col="geom",
        )
        if ctx["gddbase"] not in GDD_KNOWN_BASES or ctx["gddceil"] != 86:
            # We need to compute our own GDD Climatology, Le Sigh
            df = replace_gdd_climo(ctx, pgconn, df, table, date1, date2)
        dfs.append(df)
    df = pd.concat(dfs)
    if df.empty:
        raise NoDataFound("No Data Found.")
    return df.reindex(df[ctx["var"]].abs().sort_values(ascending=False).index)


def geojson(fdict):
    """Generate a GeoDataFrame ready for geojson."""
    ctx = get_autoplot_context(fdict, get_description())
    return (get_data(ctx).drop(["lat", "lon"], axis=1)), ctx["var"]


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())
    df = get_data(ctx)
    sector = ctx["sector"]
    date1 = ctx["date1"]
    date2 = min([ctx["date2"], datetime.date.today()])
    varname = ctx["var"]

    datefmt = "%-d %b %Y" if varname != "cgdd_sum" else "%-d %b"
    subtitle = ""
    if varname.find("gdd") > -1 and (
        ctx["gddbase"] not in GDD_KNOWN_BASES or ctx["gddceil"] != 86
    ):
        subtitle = "Period of Record Climatology is used for custom GDD"
    elif varname.find("depart") > -1:
        subtitle = (
            "%s is compared with 19%s-%s Climatology to compute departures"
        ) % (date1.year, ctx["ct"][-2:], datetime.date.today().year - 1)
    elif varname.startswith("c"):
        subtitle = ("Climatology is based on data from 19%s-%s") % (
            ctx["ct"][-2:],
            datetime.date.today().year - 1,
        )
    if ctx["d"] == "sector":
        state = sector
        sector = "state" if len(sector) == 2 else sector
        cwa = None
    else:
        sector = "cwa"
        cwa = ctx["wfo"]
        state = None
    mp = MapPlot(
        sector=sector,
        state=state,
        cwa=cwa,
        axisbg="white",
        title="%s thru %s %s [%s]"
        % (
            date1.strftime(datefmt),
            date2.strftime(datefmt),
            (
                PDICT2.get(varname)
                .replace("$base", str(ctx["gddbase"]))
                .replace("$ceil", str(ctx["gddceil"]))
            ),
            UNITS.get(varname),
        ),
        subtitle=subtitle,
        twitter=True,
    )
    fmt = "%.2f"
    cmap = get_cmap(ctx["cmap"])
    if varname in [
        "precip_depart",
        "avg_temp_depart",
        "gdd_depart",
        "snow_depart",
    ]:
        rng = df[varname].abs().describe(percentiles=[0.95])["95%"]
        clevels = np.linspace(
            0 - rng, rng, 7, dtype="i" if varname == "gdd_depart" else "f"
        )
        if varname == "gdd_depart":
            fmt = "%.0f"
    elif varname in ["precip_sum", "snow_sum"]:
        rng = df[varname].abs().describe(percentiles=[0.95])["95%"]
        clevels = np.linspace(0, rng, 7)
        cmap.set_under("white")
        cmap.set_over("black")
    elif varname.endswith("_percent"):
        clevels = np.array([10, 25, 50, 75, 100, 125, 150, 175, 200])
        fmt = "%.0f"
    else:
        minv = df[varname].min() - 5
        maxv = df[varname].max() + 5
        clevels = np.linspace(minv, maxv, 6, dtype="i")
        fmt = "%.0f"
    clevlabels = [fmt % x for x in clevels]
    cmap.set_bad("white")
    if ctx["p"] == "contour":
        mp.contourf(
            df["lon"].values,
            df["lat"].values,
            df[varname].values,
            clevels,
            clevlabels=clevlabels,
            cmap=cmap,
            units=UNITS.get(varname),
        )
    if ctx["c"] == "yes":
        mp.plot_values(
            df["lon"].values,
            df["lat"].values,
            df[varname].values,
            fmt=fmt,
            labelbuffer=5,
        )
    if state is not None or sector == "iailin" or ctx["d"] == "wfo":
        if sector != "conus":
            mp.drawcounties()
    if ctx["usdm"] == "yes":
        mp.draw_usdm(date2, filled=False, hatched=True)

    return mp.fig, df.round(2)


if __name__ == "__main__":
    plotter(dict(wfo="DVN", d="wfo", ct="climate81", var="gdd", gddbase=49))
