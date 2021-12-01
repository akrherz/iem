"""LSR map by WFO"""
import datetime

import numpy as np
import pandas as pd
from pandas.io.sql import read_sql
import pytz
from pyiem.plot import MapPlot, get_cmap
from pyiem.util import get_autoplot_context, get_dbconn

MDICT = dict(
    [
        ("NONE", "All LSR Types"),
        ("NRS", "All LSR Types except HEAVY RAIN + SNOW"),
        ("H1", "One Inch and Larger Hail "),
        ("CON", "Convective LSRs (Tornado, TStorm Gst/Dmg, Hail)"),
        ("AVALANCHE", "AVALANCHE"),
        ("BLIZZARD", "BLIZZARD"),
        ("COASTAL FLOOD", "COASTAL FLOOD"),
        ("DEBRIS FLOW", "DEBRIS FLOW"),
        ("DENSE FOG", "DENSE FOG"),
        ("DOWNBURST", "DOWNBURST"),
        ("DUST STORM", "DUST STORM"),
        ("EXCESSIVE HEAT", "EXCESSIVE HEAT"),
        ("EXTREME COLD", "EXTREME COLD"),
        ("EXTR WIND CHILL", "EXTR WIND CHILL"),
        ("FLASH FLOOD", "FLASH FLOOD"),
        ("FLOOD", "FLOOD"),
        ("FOG", "FOG"),
        ("FREEZE", "FREEZE"),
        ("FREEZING DRIZZLE", "FREEZING DRIZZLE"),
        ("FREEZING RAIN", "FREEZING RAIN"),
        ("FUNNEL CLOUD", "FUNNEL CLOUD"),
        ("HAIL", "HAIL"),
        ("HEAVY RAIN", "HEAVY RAIN"),
        ("HEAVY SLEET", "HEAVY SLEET"),
        ("HEAVY SNOW", "HEAVY SNOW"),
        ("HIGH ASTR TIDES", "HIGH ASTR TIDES"),
        ("HIGH SURF", "HIGH SURF"),
        ("HIGH SUST WINDS", "HIGH SUST WINDS"),
        ("HURRICANE", "HURRICANE"),
        ("ICE STORM", "ICE STORM"),
        ("LAKESHORE FLOOD", "LAKESHORE FLOOD"),
        ("LIGHTNING", "LIGHTNING"),
        ("LOW ASTR TIDES", "LOW ASTR TIDES"),
        ("MARINE TSTM WIND", "MARINE TSTM WIND"),
        ("NON-TSTM WND DMG", "NON-TSTM WND DMG"),
        ("NON-TSTM WND GST", "NON-TSTM WND GST"),
        ("RAIN", "RAIN"),
        ("RIP CURRENTS", "RIP CURRENTS"),
        ("SLEET", "SLEET"),
        ("SNOW", "SNOW"),
        ("STORM SURGE", "STORM SURGE"),
        ("TORNADO", "TORNADO"),
        ("TROPICAL STORM", "TROPICAL STORM"),
        ("TSTM WND DMG", "TSTM WND DMG"),
        ("TSTM WND GST", "TSTM WND GST"),
        ("WALL CLOUD", "WALL CLOUD"),
        ("WATER SPOUT", "WATER SPOUT"),
        ("WILDFIRE", "WILDFIRE"),
    ]
)
PDICT = dict([("wfo", "By NWS Forecast Office"), ("state", "By State")])
PDICT2 = {
    "count": "Event Count",
    "days": "Days with 1+ Events",
    "count_rank": "Rank of Event Count (1=lowest) Since 2003",
    "count_departure": "Departure from Average of Event Count",
    "count_standard": "Standardized Departure from Average of Event Count",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """This application generates a map displaying the
    number of LSRs issued between a period of your choice by NWS Office. These
    are the preliminary reports and not official totals of events.

    <p><strong>NOTE:</strong> If you choose a period longer than one year,
    only the "count" metric is available.  Sorry.
    """
    today = datetime.date.today() + datetime.timedelta(days=1)
    jan1 = today.replace(month=1, day=1)
    desc["arguments"] = [
        dict(
            type="select",
            name="var",
            default="count",
            options=PDICT2,
            label="Which metric to plot:",
        ),
        dict(
            type="datetime",
            name="sdate",
            default=jan1.strftime("%Y/%m/%d 0000"),
            label="Start Date / Time (UTC, inclusive):",
            min="2006/01/01 0000",
        ),
        dict(
            type="datetime",
            name="edate",
            default=today.strftime("%Y/%m/%d 0000"),
            label="End Date / Time (UTC):",
            min="2006/01/01 0000",
        ),
        dict(
            type="select",
            name="filter",
            default="NONE",
            options=MDICT,
            label="Local Storm Report Type Filter",
        ),
        dict(
            type="select",
            name="by",
            default="wfo",
            label="Aggregate Option:",
            options=PDICT,
        ),
        dict(type="cmap", name="cmap", default="plasma", label="Color Ramp:"),
    ]
    return desc


def get_count_bins(df, varname):
    """Figure out sensible bins."""
    minv = df[varname].min()
    maxv = df[varname].max()
    if varname == "count_rank":
        bins = np.arange(1, maxv + 2)
    elif varname == "count":
        bins = [0, 1, 2, 3, 5, 10, 15, 20, 25, 30, 40, 50, 75, 100, 200]
        if maxv > 5000:
            bins = [
                0,
                5,
                10,
                50,
                100,
                250,
                500,
                750,
                1000,
                1500,
                2000,
                3000,
                5000,
                7500,
                10000,
            ]
        elif maxv > 1000:
            bins = [
                0,
                1,
                5,
                10,
                50,
                100,
                150,
                200,
                250,
                500,
                750,
                1000,
                1250,
                1500,
                2000,
            ]
        elif maxv > 200:
            bins = [
                0,
                1,
                3,
                5,
                10,
                20,
                35,
                50,
                75,
                100,
                150,
                200,
                250,
                500,
                750,
                1000,
            ]
    elif max([abs(minv), abs(maxv)]) > 100:
        bins = [-200, -150, -100, -50, -25, -10, 0, 10, 25, 50, 100, 150, 200]
    elif max([abs(minv), abs(maxv)]) > 10:
        bins = [-100, -50, -25, -10, -5, 0, 5, 10, 25, 50, 100]
    else:
        bins = np.arange(-3, 3.1, 0.5)
    return bins


def plotter(fdict):
    """Go"""
    pgconn = get_dbconn("postgis")
    ctx = get_autoplot_context(fdict, get_description())
    sts = ctx["sdate"].replace(tzinfo=pytz.utc)
    ets = ctx["edate"].replace(tzinfo=pytz.utc)
    varname = ctx["var"]
    by = ctx["by"]
    myfilter = ctx["filter"]
    if myfilter == "NONE":
        tlimiter = ""
    elif myfilter == "NRS":
        tlimiter = " and typetext not in ('HEAVY RAIN', 'SNOW', 'HEAVY SNOW') "
    elif myfilter == "H1":
        tlimiter = " and typetext = 'HAIL' and magnitude >= 1 "
    elif myfilter == "CON":
        tlimiter = (
            " and typetext in ('TORNADO', 'HAIL', 'TSTM WND GST', "
            "'TSTM WND DMG') "
        )
    else:
        tlimiter = f" and typetext = '{myfilter}' "
    cmap = get_cmap(ctx["cmap"])
    extend = "neither"

    if varname == "days":
        df = read_sql(
            f"""
        WITH data as (
            SELECT distinct wfo, state, date(valid)
            from lsrs where valid >= %s and valid < %s {tlimiter}
        )
        SELECT {by}, count(*) from data GROUP by {by}
        """,
            pgconn,
            params=(sts, ets),
            index_col=by,
        )
        df2 = df["count"]
        if df2.max() < 10:
            bins = list(range(1, 11, 1))
        else:
            bins = np.linspace(1, df2.max() + 11, 10, dtype="i")
        units = "Days"
        lformat = "%.0f"
        cmap.set_under("white")
        cmap.set_over("#EEEEEE")

    else:
        if (ets - sts).days > 366:
            raise ValueError("Sorry, only count is available for 365+ days")
        sday = sts.strftime("%m%d")
        eday = ets.strftime("%m%d")
        slimiter = (
            f" (to_char(valid, 'mmdd') >= '{sday}' and "
            f"to_char(valid, 'mmdd') <= '{eday}' ) "
        )
        yearcol = "extract(year from valid)"
        if eday <= sday:
            slimiter = slimiter.replace(" and ", " or ")
            yearcol = (
                f"case when to_char(issue, 'mmdd') <= '{eday}' then "
                "extract(year from issue)::int - 1 else "
                "extract(year from issue) end"
            )
        # Expensive
        df = read_sql(
            f"""
        WITH data as (
            SELECT distinct wfo, {yearcol} as year, state, valid, type,
            magnitude, geom from lsrs
            where {slimiter} {tlimiter}
        )
        SELECT {by}, year, count(*) from data GROUP by {by}, year
        """,
            pgconn,
            index_col=None,
        )
        # Fill out zeros
        idx = pd.MultiIndex.from_product(
            [df[by].unique(), df["year"].unique()],
            names=[by, "year"],
        )
        df = df.set_index([by, "year"]).reindex(idx).fillna(0).reset_index()
        df["rank"] = df.groupby(by)["count"].rank(method="min", ascending=True)
        thisyear = (
            df[df["year"] == sts.year].set_index(by).drop("year", axis=1)
        )
        # Ready to construct final df.
        df = df[[by, "count"]].groupby(by).agg(["mean", "std"]).copy()
        df.columns = ["_".join(a) for a in df.columns.to_flat_index()]
        df[["count", "count_rank"]] = thisyear[["count", "rank"]]
        df["count_departure"] = df["count"] - df["count_mean"]
        df["count_standard"] = df["count_departure"] / df["count_std"]
        bins = get_count_bins(df, varname)
        lformat = "%.0f"
        units = "Count"
        if varname == "count":
            extend = "max"
        elif varname == "count_rank":
            extend = "neither"
            units = "Rank"
        else:
            if varname == "count_standard":
                lformat = "%.1f"
                units = "sigma"
            extend = "both"
        df2 = df[varname]
    # Switch JSJ to SJU in index
    df2.index = df2.index.map(lambda x: x.replace("JSJ", "SJU"))
    mp = MapPlot(
        apctx=ctx,
        sector="nws",
        axisbg="white",
        title=(
            f"Preliminary/Unfiltered Local Storm Report {PDICT2[varname]} "
            f"{PDICT[by]}"
        ),
        subtitle=(
            f"Valid {sts:%d %b %Y %H:%M} - {ets:%d %b %Y %H:%M} UTC, "
            f"type limiter: {MDICT.get(myfilter)}"
        ),
    )
    if by == "wfo":
        mp.fill_cwas(
            df2.to_dict(),
            bins=bins,
            lblformat=lformat,
            cmap=cmap,
            ilabel=True,
            units=units,
            extend=extend,
        )
    else:
        mp.fill_states(
            df2.to_dict(),
            bins=bins,
            lblformat=lformat,
            cmap=cmap,
            ilabel=True,
            units=units,
            extend=extend,
        )

    return mp.fig, df


if __name__ == "__main__":
    plotter({"var": "count_departure", "by": "state"})
