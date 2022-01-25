"""Maps of averages"""
import calendar
import datetime

import numpy as np
from pandas.io.sql import read_sql
from pyiem.plot import MapPlot, get_cmap
from pyiem.util import get_autoplot_context, get_dbconnstr
from pyiem.exceptions import NoDataFound
from pyiem.reference import SECTORS_NAME, LATLON
from sqlalchemy import text

PDICT = {
    "state": "State Level Maps (select state)",
}
PDICT.update(SECTORS_NAME)
PDICT2 = {
    "both": "Show both contour and values",
    "values": "Show just the values",
    "contour": "Show just the contour",
}
PDICT3 = dict(
    [
        ("avg_temp", "Average Temperature"),
        ("avg_high", "Average High Temperature"),
        ("avg_low", "Average Low Temperature"),
        ("total_cdd65", "Total Cooling Degree Days (base=65)"),
        ("total_gdd32", "Total Growing Degree Days (base=32)"),
        ("total_gdd41", "Total Growing Degree Days (base=41)"),
        ("total_gdd46", "Total Growing Degree Days (base=46)"),
        ("total_gdd48", "Total Growing Degree Days (base=48)"),
        ("total_gdd50", "Total Growing Degree Days (base=50)"),
        ("total_gdd51", "Total Growing Degree Days (base=51)"),
        ("total_gdd52", "Total Growing Degree Days (base=52)"),
        ("total_hdd65", "Total Heating Degree Days (base=65)"),
        ("total_sdd86", "Total Stress Degree Days (base=86)"),
        ("total_precip", "Total Precipitation"),
    ]
)
PDICT5 = {
    "climate": "Period of Record Climatology",
    "climate51": "1951-Present Climatology",
    "climate71": "1971-Present Climatology",
    "climate81": "1981-Present Climatology",
    "ncdc_climate71": "NCEI 1971-2000 Climatology",
    "ncdc_climate81": "NCEI 1981-2010 Climatology",
    "ncei_climate91": "NCEI 1991-2020 Climatology",
}
UNITS = {"total_precip": "inch"}
PRECISION = {
    "total_precip": 2,
    "total_gdd50": 0,
    "total_gdd32": 0,
    "total_gdd41": 0,
    "total_gdd46": 0,
    "total_gdd48": 0,
    "total_gdd51": 0,
    "total_gdd52": 0,
    "total_cdd65": 0,
    "total_hdd65": 0,
}
MDICT = dict(
    [
        ("all", "No Month/Time Limit"),
        ("spring", "Spring (MAM)"),
        ("mjj", "May/June/July"),
        ("gs", "May thru Sep"),
        ("fall", "Fall (SON)"),
        ("winter", "Winter (DJF)"),
        ("summer", "Summer (JJA)"),
        ("jan", "January"),
        ("feb", "February"),
        ("mar", "March"),
        ("apr", "April"),
        ("may", "May"),
        ("jun", "June"),
        ("jul", "July"),
        ("aug", "August"),
        ("sep", "September"),
        ("oct", "October"),
        ("nov", "November"),
        ("dec", "December"),
    ]
)


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """This application produces map analysis of
    climatological averages.  The IEM maintains a number of different
    climatologies based on period of record and source.  If you pick the NCEI
    Climatology, only basic temperature and precipitation variables are
    available at this time."""
    desc["arguments"] = [
        dict(
            type="select",
            name="month",
            default="all",
            label="Month Limiter",
            options=MDICT,
        ),
        dict(
            type="select",
            name="sector",
            default="state",
            options=PDICT,
            label="Select Map Region",
        ),
        dict(
            type="select",
            name="src",
            default="ncei_climate91",
            options=PDICT5,
            label=(
                "Select Climatology Source to Use "
                "(limits available variables)"
            ),
        ),
        dict(
            type="state",
            name="state",
            default="IA",
            label="Select State to Plot (when appropriate)",
        ),
        dict(
            type="select",
            name="opt",
            options=PDICT2,
            default="both",
            label="Map Plot/Contour View Option",
        ),
        dict(
            type="select",
            name="var",
            options=PDICT3,
            default="total_precip",
            label="Which Variable to Plot",
        ),
        dict(type="cmap", name="cmap", default="jet", label="Color Ramp:"),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    state = ctx["state"][:2]
    varname = ctx["var"]
    sector = ctx["sector"]
    opt = ctx["opt"]
    month = ctx["month"]
    if month == "all":
        months = range(1, 13)
    elif month == "fall":
        months = [9, 10, 11]
    elif month == "winter":
        months = [12, 1, 2]
    elif month == "spring":
        months = [3, 4, 5]
    elif month == "mjj":
        months = [5, 6, 7]
    elif month == "gs":
        months = [5, 6, 7, 8, 9]
    elif month == "summer":
        months = [6, 7, 8]
    else:
        ts = datetime.datetime.strptime("2000-" + month + "-01", "%Y-%b-%d")
        # make sure it is length two for the trick below in SQL
        months = [ts.month]

    if len(months) == 1:
        title = "%s %s" % (calendar.month_name[months[0]], PDICT3[varname])
    else:
        title = "%s" % (MDICT[month],)
    mp = MapPlot(
        apctx=ctx,
        sector=sector,
        state=state,
        axisbg="white",
        title="%s %s for %s" % (PDICT5[ctx["src"]], PDICT3[varname], title),
        nocaption=True,
    )
    bnds = mp.panels[0].get_extent(crs=LATLON)

    joincol = "id"
    if ctx["src"] == "ncdc_climate81":
        joincol = "ncdc81"
    elif ctx["src"] == "ncei_climate91":
        joincol = "ncei91"
    extra = ""
    if not ctx["src"].startswith("ncdc_"):
        extra = """,
        sum(cdd65) as total_cdd65,
        sum(hdd65) as total_hdd65,
        sum(gdd32) as total_gdd32,
        sum(gdd41) as total_gdd41,
        sum(gdd46) as total_gdd46,
        sum(gdd48) as total_gdd48,
        sum(gdd50) as total_gdd50,
        sum(gdd51) as total_gdd51,
        sum(gdd52) as total_gdd52
        """
    df = read_sql(
        text(
            f"""
        WITH mystations as (
            select {joincol} as myid,
            max(ST_x(geom)) as lon, max(ST_y(geom)) as lat from stations
            where network ~* 'CLIMATE' and
            ST_Contains(ST_MakeEnvelope(:b1, :b2, :b3, :b4, 4326), geom)
            GROUP by myid
        )
        SELECT station, extract(month from valid) as month,
        max(lon) as lon, min(lat) as lat,
        sum(precip) as total_precip,
        avg(high) as avg_high,
        avg(low) as avg_low,
        avg((high+low)/2.) as avg_temp {extra} from {ctx["src"]} c
        JOIN mystations t on (c.station = t.myid)
        WHERE extract(month from valid) in :months
        GROUP by station, month
        """
        ),
        get_dbconnstr("coop"),
        params={
            "b1": bnds[0],
            "b2": bnds[2],
            "b3": bnds[1],
            "b4": bnds[3],
            "months": tuple(months),
        },
        index_col=["station", "month"],
    )
    if df.empty:
        raise NoDataFound("No data was found for query, sorry.")

    if len(months) == 1:
        df2 = df
    else:
        if varname.startswith("total"):
            df2 = df.sum(axis=0, level="station")
        else:
            df2 = df.mean(axis=0, level="station")
        df2["lat"] = df["lat"].mean(axis=0, level="station")
        df2["lon"] = df["lon"].mean(axis=0, level="station")
    levels = np.linspace(df2[varname].min(), df2[varname].max(), 10)
    levels = [round(x, PRECISION.get(varname, 1)) for x in levels]
    if opt in ["both", "contour"]:
        mp.contourf(
            df2["lon"].values,
            df2["lat"].values,
            df2[varname].values,
            levels,
            units=UNITS.get(varname, "F"),
            cmap=get_cmap(ctx["cmap"]),
            clip_on=False,
        )
    if sector == "state":
        mp.drawcounties()
    if opt in ["both", "values"]:
        mp.plot_values(
            df2["lon"].values,
            df2["lat"].values,
            df2[varname].values,
            fmt="%%.%if" % (PRECISION.get(varname, 1),),
            labelbuffer=5,
        )

    return mp.fig, df


if __name__ == "__main__":
    plotter(dict(month="gs", var="total_gdd50", src="climate51"))
