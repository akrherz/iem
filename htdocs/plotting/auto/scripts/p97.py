"""
This application plots an analysis of station
data for a period of your choice.  Spatially aggregated values like those
for climate districts and statewide averages are not included.  The IEM
computed climatologies are based on simple daily averages of observations.

<p><strong>Updated 7 Feb 2024:</strong> When plotting snowfall, the application
requires a 90% observation coverage for the period of interest.  The issue is
that the IEM currently does not estimate snowfall, like it does for high, low,
and precipitation.
"""

import datetime

import geopandas as gpd
import numpy as np
import pandas as pd
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import MapPlot, centered_bins, get_cmap, pretty_bins
from pyiem.reference import wfo_bounds
from pyiem.util import get_autoplot_context, logger
from sqlalchemy import text

LOG = logger()
PDICT = {
    "sector": "Plot by Sector / State",
    "wfo": "Plot by NWS Weather Forecast Office (WFO)",
}
NCEI_BAD = (
    "cgdd_sum gdd_depart gdd_percent cdd65_depart hdd65_depart "
    "csdd86_sum sdd86_depart sdd86_percent"
).split()
PDICT2 = {
    "max_high_temp": "Maximum High Temperature",
    "avg_high_temp": "Average High Temperature",
    "avg_high_depart": "Average High Temperature Departure",
    "avg_temp_depart": "Average Temperature Departure",
    "avg_temp": "Average Temperature",
    "min_low_temp": "Minimum Low Temperature",
    "avg_low_temp": "Average Low Temperature",
    "avg_low_depart": "Average Low Temperature Departure",
    "gdd_sum": "Growing Degree Days ($base/$ceil) Total",
    "cgdd_sum": "Growing Degree Days ($base/$ceil) Climatology",
    "gdd_depart": "Growing Degree Days ($base/$ceil) Departure",
    "gdd_percent": "Growing Degree Days ($base/$ceil) Percent of Average",
    "cdd65_sum": "Cooling Degree Days (base 65)",
    "cdd65_depart": "Cooling Degree Days Departure (base 65)",
    "hdd65_sum": "Heating Degree Days (base 65)",
    "hdd65_depart": "Heating Degree Days Departure (base 65)",
    "precip_max": "Precipitation Daily Maximum",
    "precip_depart": "Precipitation Departure",
    "precip_percent": "Precipitation Percent of Average",
    "precip_sum": "Precipitation Total",
    "snow_depart": "Snowfall Departure",
    "snow_percent": "Snowfall Percent of Average",
    "snow_sum": "Snowfall Total",
    "sdd86_sum": "Stress Degree Days (86F) Total",
    "csdd86_sum": "Stress Degree Days (86F) Climatology",
    "sdd86_depart": "Stress Degree Days (86F) Departure",
    "sdd86_percent": "Stress Degree Days (86F) Percent of Average",
}
PDICT4 = {
    "yes": "Yes, overlay Drought Monitor",
    "no": "No, do not overlay Drought Monitor",
}
UNITS = {
    "min_low_temp": "F",
    "avg_low_temp": "F",
    "avg_low_depart": "F",
    "avg_high_temp": "F",
    "avg_high_depart": "F",
    "cgdd_sum": "F",
    "gdd_depart": "F",
    "gdd_percent": "%",
    "gdd_sum": "F",
    "csdd86_sum": "F",
    "sdd86_depart": "F",
    "sdd86_percent": "%",
    "sdd86_sum": "F",
    "cdd65_sum": "F",
    "hdd65_sum": "F",
    "cdd65_depart": "F",
    "hdd65_depart": "F",
    "avg_temp_depart": "F",
    "avg_temp": "F",
    "precip_max": "inch",
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
    "ncei_climate91": "NCEI Climatology 1991-2020",
}
GDD_KNOWN_BASES = [32, 41, 46, 48, 50, 51, 52]


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
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
        {
            "type": "text",
            "name": "bins",
            "default": "0 0.25 0.5 0.75 1",
            "optional": True,
            "label": "Hard-code plot bins (space separated) [optional]:",
        },
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
            label=(
                "Which Climatology to Use?<br />Note that NCEI 1991-2020 "
                "climatology only works with some base plot variables."
            ),
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
    xmin, ymin, xmax, ymax = wfo_bounds[wfo]
    # buffer by a "county" or two
    xmin -= 0.5
    ymin -= 0.5
    xmax += 0.5
    ymax += 0.5
    pgconn = get_dbconn("mesosite")
    tables = []
    cursor = pgconn.cursor()
    cursor.execute(
        "SELECT distinct substr(id, 1, 2) from stations where "
        "network ~* 'CLIMATE' and ST_Contains("
        "ST_MakeEnvelope(%s, %s, %s, %s, 4326), geom)",
        (xmin, ymin, xmax, ymax),
    )
    for row in cursor:
        tables.append(f"alldata_{row[0].lower()}")
    return tables, [xmin, ymin, xmax, ymax]


def replace_gdd_climo(ctx, df, table, date1, date2):
    """Here we are, incredible pain."""
    # Short circuit if we are not doing departures
    if ctx["var"] in ["gdd_sum", "sdd_sum"]:
        return df
    d1 = date1.strftime("%m%d")
    d2 = date2.strftime("%m%d")
    daylimit = f"sday >= '{d1}' and sday <= '{d2}'"
    if d1 > d2:
        daylimit = f"sday >= '{d2}' or sday <= '{d1}'"
    if (date2 - date1) > datetime.timedelta(days=365):
        daylimit = ""
    with get_sqlalchemy_conn("coop") as conn:
        climo = pd.read_sql(
            f"""WITH obs as (
                SELECT station, sday, avg(gddxx(%s, %s, high, low)) as datum
                from {table} GROUP by station, sday)
            select station, sum(datum) as gdd from obs
            WHERE {daylimit} GROUP by station ORDER by station
            """,
            conn,
            params=(ctx["gddbase"], ctx["gddceil"]),
            index_col="station",
        )
    climo.loc[climo["gdd"] == 0, "gdd"] = 1
    df["cgdd_sum"] = climo["gdd"]
    df["gdd_percent"] = df["gdd_sum"] / df["cgdd_sum"] * 100.0
    df["gdd_depart"] = df["gdd_sum"] - df["cgdd_sum"]
    return df


def build_climate_sql(ctx, table):
    """figure out how to get climatology..."""
    gddclimocol = "0"
    if ctx["gddbase"] in GDD_KNOWN_BASES:
        gddclimocol = f"gdd{ctx['gddbase']}"
    stjoin = "id"
    if ctx["ct"] == "ncei_climate91":
        stjoin = "ncei91"
    netlimiter = "t.network ~* 'CLIMATE'"
    if table != "alldata":
        netlimiter = f"t.network = '{table[-2:].upper()}CLIMATE'"

    sql = f"""
    SELECT t.id as station, to_char(valid, 'mmdd') as sday, precip, high,
    low, {gddclimocol} as gdd, cdd65, hdd65, snow, sdd86
    from {ctx['ct']} c, stations t WHERE c.station = t.{stjoin} and
    {netlimiter} """

    return sql


def get_data(ctx):
    """Compute the data needed for this app."""
    cull = cull_to_list(ctx["cull"])
    date1 = ctx["date1"]
    date2 = min([ctx["date2"], datetime.date.today()])
    sector = ctx["sector"]
    table = f"alldata_{sector}" if len(sector) == 2 else "alldata"
    tables = [table]
    dfs = []
    wfo_limiter = ""
    if sector == "iailin":
        tables = ["alldata_ia", "alldata_il", "alldata_in"]
    elif sector == "midwest":
        tables = [
            f"alldata_{x}"
            for x in "nd mn wi mi sd ne ia il in oh ks mo ky".split()
        ]
    if ctx["d"] == "wfo":
        tables, bnds = compute_tables_wfo(ctx["wfo"])
        wfo_limiter = (
            f" and ST_Contains(St_MakeEnvelope({bnds[0]}, {bnds[1]}, "
            f"{bnds[2]}, {bnds[3]}, 4326), geom) "
        )
    if "alldata" in tables or len(tables) > 9:
        if ctx["gddbase"] not in GDD_KNOWN_BASES:
            raise NoDataFound(f"GDD Base must be {','.join(GDD_KNOWN_BASES)}")
        ctx["gddceil"] = 86
    params = {
        "gddbase": ctx["gddbase"],
        "gddceil": ctx["gddceil"],
        "date1": date1,
        "date2": date2,
        "cull": cull,
    }
    with get_sqlalchemy_conn("coop") as conn:
        for table in tables:
            LOG.info("Starting %s table query", table)
            df = gpd.read_postgis(
                text(
                    f"""
                WITH obs as (
                    SELECT station,
                    gddxx(:gddbase, :gddceil, high, low) as gdd,
                    cdd(high, low, 65) as cdd65, hdd(high, low, 65) as hdd65,
                    case when high > 86 then high - 86 else 0 end as sdd86,
                    sday, high, low, precip, snow,
                    (high + low)/2. as avg_temp
                    from {table} WHERE
                    day >= :date1 and day <= :date2 and
                    substr(station, 3, 1) not in ('C', 'K', 'D') and
                    substr(station, 3, 4) != '0000'
                    and not (station = ANY(:cull))),
                climo as ({build_climate_sql(ctx, table)}),
                combo as (
                    SELECT o.station, o.precip - c.precip as precip_diff,
                    o.precip as precip, c.precip as cprecip,
                    o.avg_temp, o.cdd65, o.hdd65,
                    o.high - c.high as high_diff,
                    o.low - c.low as low_diff,
                    o.high, o.low, o.gdd, c.gdd as cgdd,
                    o.sdd86, c.sdd86 as csdd86,
                    o.gdd - c.gdd as gdd_diff,
                    o.cdd65 - c.cdd65 as cdd65_diff,
                    o.hdd65 - c.hdd65 as hdd65_diff,
                    o.sdd86 - c.sdd86 as sdd86_diff,
                    o.avg_temp - (c.high + c.low)/2. as temp_diff,
                    o.snow as snow, c.snow as csnow,
                    o.snow - c.snow as snow_diff
                    from obs o JOIN climo c ON
                    (o.station = c.station and o.sday = c.sday)),
                agg as (
                    SELECT station, count(*) as obs,
                    avg(avg_temp) as avg_temp,
                    max(precip) as precip_max,
                    sum(precip_diff) as precip_depart,
                    sum(precip) / greatest(sum(cprecip), 0.0001) * 100.
                        as precip_percent,
                    sum(snow_diff) as snow_depart,
                    sum(snow) / greatest(sum(csnow), 0.0001) * 100.
                        as snow_percent,
                    sum(precip) as precip, sum(cprecip) as cprecip,
                    sum(snow) as snow, sum(csnow) as csnow,
                    avg(high) as avg_high_temp,
                    avg(high_diff) as avg_high_depart,
                    avg(low_diff) as avg_low_depart,
                    avg(low) as avg_low_temp,
                    max(high) as max_high_temp,
                    min(low) as min_low_temp, sum(gdd_diff) as gdd_depart,
                    sum(gdd) / greatest(1, sum(cgdd)) * 100. as gdd_percent,
                    sum(sdd86_diff) as sdd86_depart,
                    sum(sdd86) / greatest(1, sum(csdd86)) * 100.
                        as sdd86_percent,
                    avg(temp_diff) as avg_temp_depart, sum(gdd) as gdd_sum,
                    sum(cgdd) as cgdd_sum,
                    sum(sdd86) as sdd86_sum,
                    sum(csdd86) as csdd86_sum,
                    sum(cdd65) as cdd65_sum,
                    sum(hdd65) as hdd65_sum,
                    sum(cdd65_diff) as cdd65_depart,
                    sum(hdd65_diff) as hdd65_depart,
                    sum(case when snow is not null then 1 else 0 end)
                        as snow_quorum
                    from combo GROUP by station)

                SELECT d.station, t.name, t.wfo,
                avg_temp,
                precip as precip_sum,
                cprecip as cprecip_sum,
                precip_max,
                precip_depart,
                precip_percent,
                snow as snow_sum,
                csnow as csnow_sum,
                snow_depart,
                snow_percent,
                avg_high_depart,
                avg_low_depart,
                min_low_temp,
                avg_temp_depart,
                gdd_depart,
                gdd_sum,
                gdd_percent,
                cgdd_sum,
                sdd86_depart,
                sdd86_sum,
                sdd86_percent,
                csdd86_sum,
                max_high_temp,
                avg_high_temp,
                avg_low_temp,
                cdd65_sum, hdd65_sum, cdd65_depart, hdd65_depart,
                ST_x(t.geom) as lon, ST_y(t.geom) as lat,
                t.geom, obs, snow_quorum
                from agg d JOIN stations t on (d.station = t.id)
                WHERE t.network ~* 'CLIMATE' and t.online {wfo_limiter}
                """
                ),
                conn,
                params=params,
                index_col="station",
                geom_col="geom",
            )
            LOG.info("Finshing %s table query", table)
        if ctx["gddbase"] not in GDD_KNOWN_BASES or ctx["gddceil"] != 86:
            # We need to compute our own GDD Climatology, Le Sigh
            df = replace_gdd_climo(ctx, df, table, date1, date2)
        dfs.append(df)
    df = pd.concat(dfs)
    if df.empty:
        raise NoDataFound("No Data Found.")
    # Drop any entries with NaN
    df = df[~pd.isna(df[ctx["var"]])]
    if df.empty:
        raise NoDataFound("All data found to be missing.")
    # Require 90% quorum
    df = df[df["obs"] > (df["obs"].max() * 0.9)]
    return df.reindex(df[ctx["var"]].abs().sort_values(ascending=False).index)


def geojson(fdict):
    """Generate a GeoDataFrame ready for geojson."""
    ctx = get_autoplot_context(fdict, get_description())
    return (get_data(ctx).drop(["lat", "lon"], axis=1)), ctx["var"]


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description(), rectify_dates=True)
    if ctx["var"] in NCEI_BAD and ctx["ct"].startswith("ncei"):
        raise NoDataFound("Combo of NCEI Climatology + GDDs does not work!")
    df = get_data(ctx)
    sector = ctx["sector"]
    date1 = ctx["date1"]
    date2 = min([ctx["date2"], datetime.date.today()])
    varname = ctx["var"]

    datefmt = "%-d %b %Y" if varname != "cgdd_sum" else "%-d %b"
    subtitle = ""
    if (
        varname.find("gdd") > -1
        and (ctx["gddbase"] not in GDD_KNOWN_BASES or ctx["gddceil"] != 86)
        and varname != "gdd_sum"
    ):
        subtitle = "Period of Record Climatology is used for custom GDD"
    elif varname.find("depart") > -1:
        subtitle = (
            f"{date1.year} is compared with 19{ctx['ct'][-2:]}-"
            f"{datetime.date.today().year - 1} Climatology to "
            "compute departures"
        )
        if ctx["ct"] == "ncei_climate91":
            subtitle = (
                f"{date1.year} is compared with NCEI 1991-2020 Climatology to "
                "compute departures"
            )
    elif varname.startswith("c"):
        subtitle = (
            "Climatology is based on data from "
            f"19{ctx['ct'][-2:]}-{datetime.date.today().year - 1}"
        )
        if ctx["ct"] == "ncei_climate91":
            subtitle = (
                "Climatology of NCEI 1991-2020 is used to compute departures"
            )
    if ctx["d"] == "sector":
        state = sector
        sector = "state" if len(sector) == 2 else sector
        cwa = None
    else:
        sector = "cwa"
        cwa = ctx["wfo"]
        state = None
    # This causes grief
    ctx.pop("csector", None)
    _gt = (
        PDICT2[varname]
        .replace("$base", str(ctx["gddbase"]))
        .replace("$ceil", str(ctx["gddceil"]))
    )
    mp = MapPlot(
        apctx=ctx,
        sector=sector,
        state=state,
        cwa=cwa,
        axisbg="white",
        title=(
            f"{date1.strftime(datefmt)} thru {date2.strftime(datefmt)} {_gt} "
            f"[{UNITS.get(varname)}]"
        ),
        subtitle=subtitle,
        nocaption=True,
    )
    fmt = "%.2f"
    cmap = get_cmap(ctx["cmap"])
    extend = "both"
    if varname in [
        "precip_depart",
        "avg_temp_depart",
        "gdd_depart",
        "snow_depart",
    ]:
        # encapsulte most of the data
        rng = df[varname].abs().describe(percentiles=[0.95])["95%"]
        clevels = centered_bins(rng)
        if varname == "gdd_depart":
            fmt = "%.0f"
    elif varname in ["precip_max", "precip_sum", "snow_sum"]:
        ptiles = df[varname].abs().describe(percentiles=[0.05, 0.95])
        minval = 0 if ptiles["5%"] < 1 else ptiles["5%"]
        clevels = pretty_bins(minval, ptiles["95%"])
        extend = "max"
        if varname == "snow_sum":
            fmt = "%.1f"
    elif varname.endswith("_percent"):
        clevels = np.array([10, 25, 50, 75, 100, 125, 150, 175, 200])
        fmt = "%.0f"
    else:
        clevels = pretty_bins(df[varname].min(), df[varname].max())
        fmt = "%.0f"
        extend = "neither"
    if ctx.get("bins"):
        clevels = [float(x) for x in ctx["bins"].split()]
    cmap.set_bad("white")
    if ctx["p"] == "contour" and len(clevels) > 1:
        mp.contourf(
            df["lon"].values,
            df["lat"].values,
            df[varname].values,
            clevels,
            cmap=cmap,
            units=UNITS.get(varname),
            extend=extend,
        )

    if ctx["c"] == "yes":
        df2 = df
        if ctx["d"] == "wfo":
            df2 = df[df["wfo"] == ctx["wfo"]]
        mp.plot_values(
            df2["lon"].values,
            df2["lat"].values,
            df2[varname].values,
            fmt=fmt,
            labelbuffer=5,
        )
    if state is not None or sector == "iailin" or ctx["d"] == "wfo":
        if sector not in [
            "conus",
        ]:
            mp.drawcounties()
    if ctx["usdm"] == "yes":
        mp.draw_usdm(date2, filled=False, hatched=True)

    return mp.fig, df.round(2)


if __name__ == "__main__":
    plotter({})
