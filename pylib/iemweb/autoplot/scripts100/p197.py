"""
This generates a map showing USDA NASS weekly
statistics.  The date you select is rectified back to the latest available
date.  Historical data is linearly interpolated so that departures can be
computed. A complication is that NASS data does not exist before the
season has started or ended. In this situation, hopefully the Right-Thing
is done!
"""

import datetime

import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import get_cmap
from pyiem.plot.geoplot import MapPlot
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from sqlalchemy import text

NASS_CROP_PROGRESS = {
    "corn_poor_verypoor": "Percentage Corn Poor + Very Poor Condition",
    "corn_good_excellent": "Percentage Corn Good + Excellent Condition",
    "corn_harvest": "Percentage Corn Harvested (Grain) Acres",
    "corn_planting": "Percentage Corn Planted Acres",
    "corn_silking": "Percentage Corn Silking Acres",
    "soybeans_planting": "Percentage Soybean Planted Acres",
    "soybeans_harvest": "Percentage Soybean Harvested Acres",
    "soybeans_poor_verypoor": "Percentage Soybean Poor + Very Poor Condition",
    "soybeans_good_excellent": "Percentage Soybean Good + Excellent Condition",
    "soil_short_veryshort": "Percentage Topsoil Moisture Short + Very Short",
}

NASS_CROP_PROGRESS_LOOKUP = {
    "corn_planting": "CORN - PROGRESS, MEASURED IN PCT PLANTED",
    "corn_harvest": "CORN, GRAIN - PROGRESS, MEASURED IN PCT HARVESTED",
    "soybeans_planting": "SOYBEANS - PROGRESS, MEASURED IN PCT PLANTED",
    "soybeans_harvest": "SOYBEANS - PROGRESS, MEASURED IN PCT HARVESTED",
    "corn_silking": "CORN - PROGRESS, MEASURED IN PCT SILKING",
    "corn_poor_verypoor": [
        "CORN - CONDITION, MEASURED IN PCT POOR",
        "CORN - CONDITION, MEASURED IN PCT VERY POOR",
    ],
    "corn_good_excellent": [
        "CORN - CONDITION, MEASURED IN PCT GOOD",
        "CORN - CONDITION, MEASURED IN PCT EXCELLENT",
    ],
    "soybeans_poor_verypoor": [
        "SOYBEANS - CONDITION, MEASURED IN PCT POOR",
        "SOYBEANS - CONDITION, MEASURED IN PCT VERY POOR",
    ],
    "soybeans_good_excellent": [
        "SOYBEANS - CONDITION, MEASURED IN PCT GOOD",
        "SOYBEANS - CONDITION, MEASURED IN PCT EXCELLENT",
    ],
    "soil_short_veryshort": [
        "SOIL, TOPSOIL - MOISTURE, MEASURED IN PCT VERY SHORT",
        "SOIL, TOPSOIL - MOISTURE, MEASURED IN PCT SHORT",
    ],
}
PDICT2 = {
    "avg": "Compare against 10 year average for date",
    "week": "Compare against given number of weeks ago",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"data": True, "cache": 3600, "description": __doc__}
    # Compute a better default for corn planting.
    today = datetime.date.today()
    if today.month < 5 or today.month > 6:
        today = datetime.date(today.year - 1, 5, 15)
    desc["arguments"] = [
        dict(
            type="csector",
            name="csector",
            default="conus",
            label="Select Sector:",
        ),
        dict(
            type="select",
            options=NASS_CROP_PROGRESS,
            default="corn_planting",
            name="var",
            label="Available variables to plot:",
        ),
        dict(
            type="select",
            options=PDICT2,
            default="avg",
            label="What to compare present number against?",
            name="w",
        ),
        dict(
            type="int",
            default=1,
            label="Number of weeks ago to compare against (when appropriate):",
            name="weeks",
        ),
        dict(
            type="date",
            name="date",
            default=today.strftime("%Y/%m/%d"),
            label="Valid Date:",
            min="1981/01/01",
            max=today.strftime("%Y/%m/%d"),
        ),
        dict(type="cmap", name="cmap", default="BrBG", label="Color Ramp:"),
    ]
    return desc


def get_df(ctx):
    """Figure out what data we need to fetch here"""
    date = ctx["date"]
    # Rectify to Sunday
    if date.isoweekday() < 7:
        date = date - datetime.timedelta(days=date.isoweekday())
    varname = ctx["var"]
    params2 = NASS_CROP_PROGRESS_LOOKUP[varname]
    params = {}
    if isinstance(params2, list):
        dlimit = " short_desc = ANY(:dlimit) "
        params["dlimit"] = params2
    else:
        dlimit = " short_desc = :dlimit "
        params["dlimit"] = params2
    # NB aggregate here needed for the multiple parameter short_desc above
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text(
                "select year, week_ending, sum(num_value) as value, "
                f"state_alpha from nass_quickstats where {dlimit} and "
                "num_value is not null "
                "GROUP by year, week_ending, state_alpha "
                "ORDER by state_alpha, week_ending"
            ),
            conn,
            index_col=None,
            params=params,
            parse_dates="week_ending",
        )
    if df.empty:
        raise NoDataFound("No NASS Data was found for query, sorry.")
    data = {}
    # Average at least ten years
    syear = max([1981, date.year - 10])
    eyear = syear + 10
    week_ending_start = date - datetime.timedelta(days=ctx["weeks"] * 7)
    for state, gdf in df.groupby("state_alpha"):
        sdf = gdf.copy().set_index("week_ending")
        # TOO DIFFICULT to know what to do in this case.
        if date.strftime("%Y-%m-%d") not in sdf.index:
            continue
        thisval = sdf.loc[date.strftime("%Y-%m-%d")]["value"]
        # linear interpolate data to get comparables
        newdf = (
            sdf[~sdf.index.duplicated(keep="first")][["year", "value"]]
            .resample("D")
            .interpolate(method="linear")
        )
        # get doy averages
        y10 = newdf[(newdf["year"] >= syear) & (newdf["year"] < eyear)]
        if y10.empty:
            avgval = None
        else:
            doyavgs = y10.groupby(y10.index.strftime("%m%d")).mean(
                numeric_only=True
            )
            if date.strftime("%m%d") in doyavgs.index:
                avgval = doyavgs.at[date.strftime("%m%d"), "value"]
            else:
                avgval = None
        pval = None
        if week_ending_start.strftime("%Y-%m-%d") in sdf.index:
            pval = sdf.loc[week_ending_start.strftime("%Y-%m-%d")]["value"]
        data[state] = {
            "avg": avgval,
            "thisval": thisval,
            f'week{ctx["weeks"]}ago': pval,
        }
    ctx["df"] = pd.DataFrame.from_dict(data, orient="index")
    if ctx["df"].empty:
        raise NoDataFound("No Data Found.")
    ctx["df"] = ctx["df"].dropna(how="all")
    ctx["df"].index.name = "state"
    col = "avg" if ctx["w"] == "avg" else f'week{ctx["weeks"]}ago'
    ctx["df"]["departure"] = ctx["df"]["thisval"] - ctx["df"][col]
    ctx["title"] = f"{date:%-d %b %Y} USDA NASS {NASS_CROP_PROGRESS[varname]}"
    if ctx["w"] == "avg":
        ctx["subtitle"] = (
            f"Top value is {date.year} percentage, bottom value is "
            f"departure from {syear}-{eyear - 1} avg"
        )
    else:
        ctx["subtitle"] = (
            f"Top value is {date.year} percentage, bottom value is "
            f"precentage points change since {week_ending_start:%-d %b %Y}"
        )


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())

    get_df(ctx)
    labels = {}
    data = {}
    for state, row in ctx["df"].iterrows():
        val = row["departure"]
        data[state] = val
        if pd.isna(val):
            if pd.isna(row["avg"]):
                subscript = "M"
            else:
                subscript = f"[-{row['avg']:.0f}]"
                data[state] = 0 - row["avg"]
        else:
            subscript = f"[{'+' if val > 0 else ''}{val:.0f}]"
            subscript = "[0]" if subscript in ["[-0]", "[+0]"] else subscript
        tt = "M" if pd.isna(row["thisval"]) else int(row["thisval"])
        labels[state] = f"{tt}\n{subscript}"

    mp = MapPlot(
        apctx=ctx,
        title=ctx["title"],
        subtitle=ctx["subtitle"],
        nocaption=True,
    )
    levels = range(-40, 41, 10)
    cmap = get_cmap(ctx["cmap"])
    cmap.set_bad("white")
    mp.fill_states(
        data,
        ilabel=True,
        labels=labels,
        bins=levels,
        cmap=cmap,
        units="Percentage Points",
        labelfontsize=16,
        labelbuffer=0,
    )

    return mp.fig, ctx["df"]
