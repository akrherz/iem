"""
This application produces map analysis of
climatological averages.  The IEM maintains a number of different
climatologies based on period of record and source.  If you pick the NCEI
Climatology, only basic temperature and precipitation variables are
available at this time.

<p>If you select a period of dates with the end date prior to the start
date, the logic then has the period cross the 1 January boundary.  For
example, a period between Dec 15 and Jan 15 will be computed.</p>
"""

import calendar
import datetime

import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import MapPlot, get_cmap, pretty_bins
from pyiem.reference import LATLON, SECTORS_NAME, Z_OVERLAY2
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from sqlalchemy import text

PDICT = {
    "state": "State Level Maps (select state)",
}
PDICT.update(SECTORS_NAME)
PDICT2 = {
    "both": "Show both contour and values",
    "values": "Show just the values",
    "contour": "Show just the filled contour",
}
PDICT3 = {
    "avg_temp": "Average Temperature",
    "avg_high": "Average High Temperature",
    "avg_low": "Average Low Temperature",
    "total_cdd65": "Total Cooling Degree Days (base=65)",
    "total_gdd32": "Total Growing Degree Days (base=32)",
    "total_gdd41": "Total Growing Degree Days (base=41)",
    "total_gdd46": "Total Growing Degree Days (base=46)",
    "total_gdd48": "Total Growing Degree Days (base=48)",
    "total_gdd50": "Total Growing Degree Days (base=50)",
    "total_gdd51": "Total Growing Degree Days (base=51)",
    "total_gdd52": "Total Growing Degree Days (base=52)",
    "total_hdd65": "Total Heating Degree Days (base=65)",
    "total_sdd86": "Total Stress Degree Days (base=86)",
    "total_precip": "Total Precipitation",
}
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
MDICT = {
    "all": "No Month/Time Limit",
    "spring": "Spring (MAM)",
    "mjj": "May/June/July",
    "gs": "May thru Sep",
    "fall": "Fall (SON)",
    "winter": "Winter (DJF)",
    "summer": "Summer (JJA)",
    "jan": "January",
    "feb": "February",
    "mar": "March",
    "apr": "April",
    "may": "May",
    "jun": "June",
    "jul": "July",
    "aug": "August",
    "sep": "September",
    "oct": "October",
    "nov": "November",
    "dec": "December",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        dict(
            type="select",
            name="month",
            default="all",
            label="Month Limiter",
            options=MDICT,
        ),
        dict(
            type="sday",
            default="0101",
            name="sdate",
            optional=True,
            label="Start Date of Inclusive Period (optional)",
        ),
        dict(
            type="sday",
            default="1231",
            name="edate",
            optional=True,
            label="End Date of Inclusive Period (optional)",
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
        months = list(range(1, 13))
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
        ts = datetime.datetime.strptime(f"2000-{month}-01", "%Y-%b-%d")
        # make sure it is length two for the trick below in SQL
        months = [ts.month]

    if len(months) == 1:
        title = calendar.month_name[months[0]]
    else:
        title = MDICT[month]
    params = {}
    dtlimiter = "extract(month from valid) = ANY(:months)"
    if ctx.get("sdate") is not None and ctx.get("edate") is not None:
        if ctx["sdate"] > ctx["edate"]:
            dtlimiter = "(valid >= :sdate or valid <= :edate)"
        else:
            dtlimiter = "valid >= :sdate and valid <= :edate"
        params["sdate"] = ctx["sdate"]
        params["edate"] = ctx["edate"]
        title = f"{ctx['sdate']:%b %-d} thru {ctx['edate']:%b %d}"

    mp = MapPlot(
        apctx=ctx,
        sector=sector,
        state=state,
        axisbg="white",
        title=f"{PDICT5[ctx['src']]} {PDICT3[varname]} for {title}",
        nocaption=True,
    )
    bnds = mp.panels[0].get_extent(crs=LATLON)
    params.update(
        {
            "b1": bnds[0],
            "b2": bnds[2],
            "b3": bnds[1],
            "b4": bnds[3],
            "months": months,
        }
    )

    joincol = "id"
    if ctx["src"] == "ncdc_climate81":
        joincol = "ncdc81"
    elif ctx["src"] == "ncei_climate91":
        joincol = "ncei91"
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text(
                f"""
            WITH mystations as (
                select {joincol} as myid, max(state) as state,
                max(ST_x(geom)) as lon, max(ST_y(geom)) as lat from stations
                where network ~* 'CLIMATE' and
                ST_Contains(ST_MakeEnvelope(:b1, :b2, :b3, :b4, 4326), geom)
                GROUP by myid
            )
            SELECT station, max(state) as state,
            max(lon) as lon, min(lat) as lat,
            sum(precip) as total_precip,
            avg(high) as avg_high,
            avg(low) as avg_low,
            avg((high+low)/2.) as avg_temp,
            sum(sdd86) as total_sdd86,
            sum(cdd65) as total_cdd65,
            sum(hdd65) as total_hdd65,
            sum(gdd32) as total_gdd32,
            sum(gdd41) as total_gdd41,
            sum(gdd46) as total_gdd46,
            sum(gdd48) as total_gdd48,
            sum(gdd50) as total_gdd50,
            sum(gdd51) as total_gdd51,
            sum(gdd52) as total_gdd52 from {ctx["src"]} c
            JOIN mystations t on (c.station = t.myid)
            WHERE {dtlimiter}
            GROUP by station
            """
            ),
            conn,
            params=params,
            index_col="station",
        )
    if df.empty:
        raise NoDataFound("No data was found for query, sorry.")
    df = df[pd.notna(df[varname])]
    if df.empty:
        raise NoDataFound("No data was found for query, sorry.")
    levels = pretty_bins(df[varname].min(), df[varname].max(), 10)
    if opt in ["both", "contour"]:
        mp.contourf(
            df["lon"].values,
            df["lat"].values,
            df[varname].values,
            levels,
            units=UNITS.get(varname, "F"),
            cmap=get_cmap(ctx["cmap"]),
            extend="neither",
            clip_on=False,
        )
        # Manual clipping sector
        mp.draw_mask(None if sector == "state" else "conus")
    if sector == "state":
        df = df[df["state"] == state]
        mp.drawcounties()
    if opt in ["both", "values"]:
        mp.plot_values(
            df["lon"].values,
            df["lat"].values,
            df[varname].values,
            fmt=f"%.{PRECISION.get(varname, 1)}f",
            labelbuffer=5,
            zorder=Z_OVERLAY2 + 3,  # FIXME in pyIEM someday
        )

    return mp.fig, df


if __name__ == "__main__":
    plotter({})
