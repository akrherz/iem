"""Map of NASS Progress Data"""
import datetime
from collections import OrderedDict

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.plot.geoplot import MapPlot
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = OrderedDict(
    (
        ("corn_poor_verypoor", "Percentage Corn Poor + Very Poor Condition"),
        ("corn_good_excellent", "Percentage Corn Good + Excellent Condition"),
        ("corn_planting", "Percentage Corn Planted Acres"),
        ("corn_silking", "Percentage Corn Silking Acres"),
        ("soybeans_planting", "Percentage Soybean Planted Acres"),
    )
)
LOOKUP = {
    "corn_planting": [
        "CORN",
        "PROGRESS",
        "PCT PLANTED",
        "ALL UTILIZATION PRACTICES",
    ],
    "soybeans_planting": [
        "SOYBEANS",
        "PROGRESS",
        "PCT PLANTED",
        "ALL UTILIZATION PRACTICES",
    ],
    "corn_silking": [
        "CORN",
        "PROGRESS",
        "PCT SILKING",
        "ALL UTILIZATION PRACTICES",
    ],
    "corn_poor_verypoor": [
        "CORN",
        "CONDITION",
        ["PCT POOR", "PCT VERY POOR"],
        "ALL UTILIZATION PRACTICES",
    ],
    "corn_good_excellent": [
        "CORN",
        "CONDITION",
        ["PCT GOOD", "PCT EXCELLENT"],
        "ALL UTILIZATION PRACTICES",
    ],
}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc["cache"] = 3600
    desc["nass"] = True
    desc[
        "description"
    ] = """This generates a map showing USDA NASS weekly
    statistics.  The date you select is rectified back to the latest available
    date.  Historical data is linearly interpolated so that departures can be
    computed. A complication is that NASS data does not exist before the
    season has started or ended. In this situation, hopefully the Right-Thing
    is done!"""
    today = datetime.date.today()
    desc["arguments"] = [
        dict(
            type="select",
            options=PDICT,
            default="corn_silking",
            name="var",
            label="Available variables to plot:",
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
    pgconn = get_dbconn("coop")
    params = LOOKUP[varname]
    if isinstance(params[2], list):
        dlimit = " unit_desc in %s" % (str(tuple(params[2])))
    else:
        dlimit = " unit_desc = '%s' " % (params[2],)
    df = read_sql(
        """
        select year, week_ending,
        sum(num_value) as value, state_alpha from nass_quickstats
        where commodity_desc = %s and statisticcat_desc = %s
        and """
        + dlimit
        + """ and
        util_practice_desc = %s
        and num_value is not null
        GROUP by year, week_ending, state_alpha
        ORDER by state_alpha, week_ending
    """,
        pgconn,
        params=(params[0], params[1], params[3]),
        index_col=None,
    )
    if df.empty:
        raise NoDataFound("No NASS Data was found for query, sorry.")
    df["week_ending"] = pd.to_datetime(df["week_ending"])
    data = {}
    # Average atleast ten years
    syear = max([1981, date.year - 10])
    eyear = syear + 10
    for state, gdf in df.groupby("state_alpha"):
        sdf = gdf.copy()
        sdf.set_index("week_ending", inplace=True)
        # TOO DIFFICULT to know what to do in this case.
        if date.strftime("%Y-%m-%d") not in sdf.index:
            continue
        thisval = sdf.loc[date.strftime("%Y-%m-%d")]["value"]
        # linear interpolate data to get comparables
        newdf = sdf.resample("D").interpolate(method="linear")
        # get doy averages
        y10 = newdf[(newdf["year"] >= syear) & (newdf["year"] < eyear)]
        if y10.empty:
            avgval = None
        else:
            doyavgs = y10.groupby(y10.index.strftime("%m%d")).mean()
            if date.strftime("%m%d") in doyavgs.index:
                avgval = doyavgs.at[date.strftime("%m%d"), "value"]
            else:
                avgval = None
        data[state] = {"avg": avgval, "thisval": thisval}
    ctx["df"] = pd.DataFrame.from_dict(data, orient="index")
    if ctx["df"].empty:
        raise NoDataFound("No Data Found.")
    ctx["df"].dropna(how="all", inplace=True)
    ctx["df"].index.name = "state"
    ctx["df"]["departure"] = ctx["df"]["thisval"] - ctx["df"]["avg"]
    ctx["title"] = "%s USDA NASS %s" % (
        date.strftime("%-d %B %Y"),
        PDICT[varname],
    )
    ctx["subtitle"] = (
        "Top value is %i percentage, bottom value is "
        "departure from %i-%i avg" % (date.year, syear, eyear - 1)
    )


def plotter(fdict):
    """ Go """
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
                subscript = "[-%.0f]" % (row["avg"],)
                data[state] = 0 - row["avg"]
        else:
            subscript = "[%s%.0f]" % ("+" if val > 0 else "", val)
            subscript = "[0]" if subscript in ["[-0]", "[+0]"] else subscript
        labels[state] = "%s\n%s" % (
            "M" if pd.isna(row["thisval"]) else int(row["thisval"]),
            subscript,
        )

    mp = MapPlot(sector="conus", title=ctx["title"], subtitle=ctx["subtitle"])
    levels = range(-40, 41, 10)
    cmap = plt.get_cmap(ctx["cmap"])
    cmap.set_bad("white")
    mp.fill_states(
        data,
        ilabel=True,
        labels=labels,
        bins=levels,
        cmap=cmap,
        units="Absolute %",
        labelfontsize=16,
    )

    return mp.fig, ctx["df"]


if __name__ == "__main__":
    plotter(dict())
