"""
This autoplot intends to show the spatial distribution of the change in
temperature or precipitation climatology over a given period of days. The
climatology is based on the 1991-2020 period from NCEI.
"""

import datetime

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import centered_bins, get_cmap
from pyiem.plot.geoplot import MapPlot
from pyiem.util import get_autoplot_context

PDICT = {
    "high": "High temperature",
    "low": "Low Temperature",
    "precip": "Precipitation",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    today = datetime.date.today()
    threeweeks = today - datetime.timedelta(days=21)
    desc["arguments"] = [
        dict(
            type="csector",
            default="conus",
            name="csector",
            label="Geographical extent to plot:",
        ),
        dict(
            type="date",
            name="date1",
            default=threeweeks.strftime("%Y/%m/%d"),
            label="From Date (ignore year):",
            min="2014/01/01",
            max=f"{today.year + 1}/12/31",
        ),  # Comes back to python as yyyy-mm-dd
        dict(
            type="date",
            name="date2",
            default=today.strftime("%Y/%m/%d"),
            label="To Date (ignore year):",
            min="2014/01/01",
            max=f"{today.year + 1}/12/31",
        ),  # Comes back to python as yyyy-mm-dd
        dict(
            type="select",
            name="varname",
            default="high",
            label="Which metric to plot?",
            options=PDICT,
        ),
        dict(type="cmap", name="cmap", default="RdBu_r", label="Color Ramp:"),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    date1 = ctx["date1"]
    date2 = ctx["date2"]
    if date2 < date1:
        days = int((date1 - date2).days)
    else:
        days = int((date2 - date1).days)
    date1 = date1.replace(year=2000)
    date2 = date2.replace(year=2000)

    varname = ctx["varname"]
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            """
        WITH t2 as (
            SELECT station, high, low, precip from ncei_climate91 WHERE
            valid = %s
        ), t1 as (
            SELECT station, high, low, precip from ncei_climate91 where
            valid = %s
        ), data as (
            SELECT t2.station, t1.high as t1_high, t2.high as t2_high,
            t1.low as t1_low, t2.low as t2_low,
            t1.precip as t1_precip, t2.precip as t2_precip
            from t1 JOIN t2 on
            (t1.station = t2.station)
        )
        SELECT d.station, ST_x(geom) as lon, ST_y(geom) as lat,
        t2_high -  t1_high as high, t2_low - t1_low as low,
        t2_precip - t1_precip as precip from data d JOIN
        stations s on (s.id = d.station) where s.network = 'NCEI91'
        """,
            conn,
            params=(date2, date1),
            index_col="station",
        )
    if df.empty:
        raise NoDataFound("No Data Found.")

    mp = MapPlot(
        apctx=ctx,
        title=(
            f"{days} Day Change in {PDICT[varname]} NCEI 1991-2020 Climatology"
        ),
        subtitle=f"from {date1:%-d %B} to {date2:%-d %B}",
        nocaption=True,
    )
    # Encapsulate most of the data
    rng = df[varname].abs().describe(percentiles=[0.95])["95%"]
    mp.contourf(
        df["lon"].values,
        df["lat"].values,
        df[varname].values,
        centered_bins(rng, bins=10),
        cmap=get_cmap(ctx["cmap"]),
        units="inch" if varname == "precip" else "F",
    )

    return mp.fig, df


if __name__ == "__main__":
    plotter({})
