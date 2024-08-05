"""
This plot presents the current streak of days with
a high or low temperature above or at-below the daily average temperature.
You can also plot the number of days since last measurable precipitation
event (trace events are counted as dry).
This plot is based off of NWS CLI sites.
"""

import datetime

import geopandas as gpd
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.network import Table as NetworkTable
from pyiem.plot.geoplot import MapPlot
from pyiem.reference import SECTORS_NAME
from pyiem.util import get_autoplot_context

PDICT = {
    "precip": "Last Measurable Precipitation",
    "low": "Low Temperature",
    "high": "High Temperature",
}
SECTORS = {
    "state": "Select a State",
    "cwa": "Select a NWS Weather Forecast Office",
}
SECTORS.update(SECTORS_NAME)


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__}
    desc["data"] = True
    desc["cache"] = 3600
    desc["arguments"] = [
        dict(
            type="select",
            name="var",
            default="high",
            label="Which parameter:",
            options=PDICT,
        ),
        dict(
            type="date",
            name="sdate",
            default=datetime.date.today().strftime("%Y/%m/%d"),
            label="Start Date:",
            min="2010/01/01",
        ),
        dict(
            type="select",
            name="sector",
            default="conus",
            options=SECTORS,
            label="Select Map Extent",
        ),
        dict(
            type="networkselect",
            name="wfo",
            network="WFO",
            default="DMX",
            label="Select WFO: (used when plotting wfo)",
        ),
        dict(
            type="state",
            name="state",
            default="IA",
            label="Select State: (used when plotting state)",
        ),
    ]
    return desc


def get_data(ctx):
    """Build out our data."""
    ctx["nt"] = NetworkTable("NWSCLI")
    varname = ctx["var"]

    today = ctx["sdate"]
    yesterday = today - datetime.timedelta(days=1)
    d180 = today - datetime.timedelta(days=180)
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            """
        with obs as (
        select station, valid,
        (case when low > low_normal then 1 else 0 end) as low_hit,
        (case when high > high_normal then 1 else 0 end) as high_hit,
        (case when precip > 0.009 then 1 else 0 end) as precip_hit
        from cli_data
        where high is not null
        and high_normal is not null and low is not null and
        low_normal is not null and precip is not null
        and valid > %s and valid <= %s),

        totals as (
        SELECT station,
        max(case when low_hit = 0 then valid else %s end) as last_low_below,
        max(case when low_hit = 1 then valid else %s end) as last_low_above,
        max(case when high_hit = 0 then valid else %s end) as last_high_below,
        max(case when high_hit = 1 then valid else %s end) as last_high_above,
        max(case when precip_hit = 0 then valid else %s end) as last_dry,
        max(case when precip_hit = 1 then valid else %s end) as last_wet,
        count(*) as count from obs GROUP by station)

        SELECT station, last_low_below, last_low_above, last_high_below,
        last_high_above, last_dry, last_wet
        from totals where count > 170
        """,
            conn,
            params=(d180, today, d180, d180, d180, d180, d180, d180),
            index_col="station",
            parse_dates=[
                "last_dry",
                "last_wet",
                "last_low_below",
                "last_low_above",
                "last_high_below",
                "last_high_above",
            ],
        )
    if df.empty:
        raise NoDataFound("No Data Found.")

    df["lat"] = None
    df["lon"] = None
    df["val"] = None
    df["color"] = ""
    df["label"] = ""

    df["precip_days"] = (df["last_dry"] - df["last_wet"]).dt.days
    df["low_days"] = (df["last_low_above"] - df["last_low_below"]).dt.days
    df["high_days"] = (df["last_high_above"] - df["last_high_below"]).dt.days
    # reorder the frame so that the largest values come first
    df = df.reindex(
        df[varname + "_days"].abs().sort_values(ascending=False).index
    )

    for station, row in df.iterrows():
        if station not in ctx["nt"].sts:
            continue
        df.at[station, "lat"] = ctx["nt"].sts[station]["lat"]
        df.at[station, "lon"] = ctx["nt"].sts[station]["lon"]
        if varname == "precip":
            last_wet = row["last_wet"]
            days = 0 if last_wet in [today, yesterday] else row["precip_days"]
        else:
            days = row[varname + "_days"]
        df.at[station, "val"] = days
        df.at[station, "color"] = "#FF0000" if days > 0 else "#0000FF"
        df.at[station, "label"] = station[1:]
    df = df[pd.notnull(df["lon"])]
    ctx["df"] = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df["lon"], df["lat"])
    )
    ctx["subtitle"] = (
        "based on NWS CLI Sites, map approximately "
        f"valid for {today:%-d %b %Y}"
    )


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    get_data(ctx)

    title = (
        f"Consecutive Days with {ctx['var'].capitalize()} "
        "Temp above(+)/below(-) Average"
    )
    if ctx["var"] == "precip":
        title = "Days Since Last Measurable Precipitation"
    mp = MapPlot(
        apctx=ctx,
        sector=ctx["sector"],
        state=ctx["state"],
        cwa=(ctx["wfo"] if len(ctx["wfo"]) == 3 else ctx["wfo"][1:]),
        axisbg="tan",
        statecolor="#EEEEEE",
        title=title,
        subtitle=ctx["subtitle"],
        nocaption=True,
    )
    df2 = ctx["df"][pd.notnull(ctx["df"]["lon"])]
    mp.plot_values(
        df2["lon"].values,
        df2["lat"].values,
        df2["val"].values,
        color=df2["color"].values,
        labels=df2["label"].values,
        labeltextsize=(8 if ctx["sector"] != "state" else 12),
        textsize=(12 if ctx["sector"] != "state" else 16),
        labelbuffer=10,
    )

    return mp.fig, ctx["df"]
