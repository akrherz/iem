"""
This plot presents the current streak of days with
a high or low temperature above or at-below the daily average temperature.
You can also plot the number of days since last measurable precipitation
event (trace events are counted as dry).
This plot is based off of NWS CLI sites.
"""

from datetime import date, timedelta
from typing import Annotated

import geopandas as gpd
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.network import Table as NetworkTable
from pyiem.plot.geoplot import MapPlot
from pyiem.reference import SECTORS_NAME

from iemweb.autoplot.description import (
    DateArg,
    NetworkSelectArg,
    PlotDescription,
    SelectArg,
    StateArg,
)
from iemweb.autoplot.params import AutoplotParams

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


class Params(AutoplotParams):
    """Request parameters."""

    var: Annotated[str, SelectArg(label="Which parameter:", options=PDICT)] = (
        "high"
    )
    sdate: Annotated[
        date,
        DateArg(
            label="Start Date:",
            min="2010/01/01",
            default=lambda: date.today().strftime("%Y/%m/%d"),
        ),
    ]
    sector: Annotated[
        str, SelectArg(options=SECTORS, label="Select Map Extent")
    ] = "conus"
    wfo: Annotated[
        str,
        NetworkSelectArg(
            network="WFO", label="Select WFO: (used when plotting wfo)"
        ),
    ] = "DMX"
    state: Annotated[
        str, StateArg(label="Select State: (used when plotting state)")
    ] = "IA"


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True, cache=3600
    )


def get_data(ctx: Params):
    """Build out our data."""
    ctx["nt"] = NetworkTable("NWSCLI")
    varname = ctx.var

    today = ctx.sdate
    yesterday = today - timedelta(days=1)
    d180 = today - timedelta(days=180)
    with get_sqlalchemy_conn("iem", rw=False) as conn:
        df = pd.read_sql(
            sql_helper("""
        with obs as (
        select station, valid,
        (case when low > low_normal then 1 else 0 end) as low_hit,
        (case when high > high_normal then 1 else 0 end) as high_hit,
        (case when precip > 0.009 then 1 else 0 end) as precip_hit
        from cli_data
        where high is not null
        and high_normal is not null and low is not null and
        low_normal is not null and precip is not null
        and valid > :d180 and valid <= :today),

        totals as (
        SELECT station,
        max(case when low_hit = 0 then valid else :d180 end) as last_low_below,
        max(case when low_hit = 1 then valid else :d180 end) as last_low_above,
        max(case when high_hit = 0 then valid else :d180 end)
            as last_high_below,
        max(case when high_hit = 1 then valid else :d180 end)
            as last_high_above,
        max(case when precip_hit = 0 then valid else :d180 end) as last_dry,
        max(case when precip_hit = 1 then valid else :d180 end) as last_wet,
        count(*) as count from obs GROUP by station)

        SELECT station, last_low_below, last_low_above, last_high_below,
        last_high_above, last_dry, last_wet
        from totals where count > 170
        """),
            conn,
            params={
                "d180": d180,
                "today": today,
            },
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
    )  # type: ignore
    ctx["subtitle"] = (
        "based on NWS CLI Sites, map approximately "
        f"valid for {today:%-d %b %Y}"
    )


def plotter(ctx: Params):
    """Go"""
    get_data(ctx)

    title = (
        f"Consecutive Days with {ctx.var.capitalize()} "
        "Temp above(+)/below(-) Average"
    )
    if ctx.var == "precip":
        title = "Days Since Last Measurable Precipitation"
    mp = MapPlot(
        apctx=ctx,
        sector=ctx.sector,
        state=ctx.state,
        cwa=(ctx.wfo if len(ctx.wfo) == 3 else ctx.wfo[1:]),
        axisbg="tan",
        statecolor="#EEEEEE",
        title=title,
        subtitle=ctx["subtitle"],
        nocaption=True,
    )
    df2 = ctx["df"][pd.notnull(ctx["df"]["lon"])]
    mp.plot_values(
        df2["lon"].to_numpy(),
        df2["lat"].to_numpy(),
        df2["val"].to_list(),
        color=df2["color"].to_list(),
        labels=df2["label"].to_list(),
        labeltextsize=(8 if ctx.sector != "state" else 12),
        textsize=(12 if ctx.sector != "state" else 16),
        labelbuffer=10,
    )

    return mp.fig, ctx["df"]
