"""
The IEM computes daily summaries of ASOS station
data based on available station summaries and computed summaries based
on available hourly data.  This chart presents the frequency combination
of one or more variables.  Please let us know if you want additional
fields added to this tool.
"""

import calendar
import itertools

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        dict(
            type="zstation",
            name="station",
            default="DSM",
            label="Select Station",
            network="IA_ASOS",
        ),
        dict(
            type="int",
            name="max_tmpf_above",
            default=90,
            optional=True,
            label="Daily Max Temperature Above (threshold F): [optional]",
        ),
        dict(
            type="int",
            name="min_tmpf_below",
            default=70,
            optional=True,
            label="Daily Min Temperature Below (threshold F): [optional]",
        ),
        dict(
            type="int",
            name="max_feel_above",
            default=90,
            optional=True,
            label="Daily Max Feels Like Temp Above (threshold F): [optional]",
        ),
        dict(
            type="int",
            name="min_feel_below",
            default=0,
            optional=True,
            label="Daily Min Feels Like Temp Below (threshold F): [optional]",
        ),
        dict(
            type="int",
            name="max_dwpf_below",
            default=50,
            optional=True,
            label="Daily Maximum Dewpoint Below (threshold F): [optional]",
        ),
        dict(
            type="int",
            name="max_dwpf_above",
            default=70,
            optional=True,
            label="Daily Maximum Dewpoint Above (threshold F): [optional]",
        ),
        dict(
            type="int",
            name="max_rh_below",
            default=50,
            optional=True,
            label="Daily Maximum Relative Humidity Below (%): [optional]",
        ),
        dict(
            type="int",
            name="avg_smph_below",
            default=10,
            optional=True,
            label="Daily Average Wind Speed Below (threshold MPH): [optional]",
        ),
        {
            "type": "int",
            "name": "max_gust_above",
            "default": 50,
            "optional": True,
            "label": "Daily Max Wind Gust Above (threshold MPH): [optional]",
        },
        dict(
            type="text",
            name="max_tmpf_range",
            default="70 to 79",
            optional=True,
            label="Daily Max Temperature Inclusive Range (deg F): [optional]",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    params = []
    labels = {"all_hit": "All Combined"}
    for ez in (
        "max_rh_below max_feel_above min_feel_below max_dwpf_below "
        "max_tmpf_above max_dwpf_above min_tmpf_below"
    ).split():
        val = ctx.get(ez)
        if val is None:
            continue
        col, op = ez.rsplit("_", 1)
        units = "%" if col.endswith("rh") else "F"
        op = ">=" if op == "above" else "<"
        params.append(
            f"case when {col} {op} {val:.0f} then 1 else 0 end as {ez}_hit"
        )
        labels[f"{ez}_hit"] = f"{col} {op} {val:.0f} {units}"
    if ctx.get("max_tmpf_range"):
        tokens = [int(i) for i in ctx["max_tmpf_range"].split("to")]
        params.append(
            f"case when max_tmpf::int >= {tokens[0]} and "
            f"max_tmpf::int <= {tokens[1]} then 1 else 0 end as tmpf_hit"
        )
        labels["tmpf_hit"] = f"High Temp {tokens[0]:.0f}F - {tokens[1]:.0f}F"
    if ctx.get("avg_smph_below"):
        params.append(
            f"case when avg_sknt * 1.15 < {ctx['avg_smph_below']:.0f} "
            "then 1 else 0 end as smph_hit"
        )
        labels["smph_hit"] = f"Avg Wind < {ctx['avg_smph_below']:.0f}MPH"
    if ctx.get("max_gust_above"):
        params.append(
            f"case when max_gust * 1.15 > {ctx['max_gust_above']:.0f} "
            "then 1 else 0 end as gust_hit"
        )
        labels["gust_hit"] = f"Wind Gust > {ctx['max_gust_above']:.0f}MPH"
    if not params:
        raise NoDataFound("Please select some options for plotting.")
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            f"SELECT {' , '.join(params)}, extract(doy from day) as doy "
            "from summary s JOIN stations t "
            "ON (s.iemid = t.iemid) WHERE t.id = %s and t.network = %s",
            conn,
            params=(station, ctx["network"]),
        )
    if df.empty:
        raise NoDataFound("No Data Found.")

    df["all_hit"] = 1
    for col in df.columns:
        if col == "doy":
            continue
        df.loc[df[col] < 1, "all_hit"] = 0
    gdf = df.groupby("doy").mean()

    ab = ctx["_nt"].sts[station]["archive_begin"]
    ab = "N/A" if ab is None else ab
    title = f"{ctx['_sname']} ({ab.year}-)\n" "Daily Observed Frequency"
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    colors = itertools.cycle(["r", "g", "b", "c", "m", "y"])
    for col in df.columns:
        if col == "doy":
            continue
        try:
            color = "k" if col == "all_hit" else next(colors)
        except StopIteration:
            color = "k"
        ax.plot(
            gdf.index.values,
            gdf[col].values * 100.0,
            lw=2,
            label=labels[col],
            color=color,
        )

    ax.legend(ncol=3, loc=(-0.05, -0.21), fontsize=14)
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_position([0.1, 0.2, 0.75, 0.7])
    ax.set_xlim(1, 365)
    ax.set_ylim(-2, 102)
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax.grid(True)
    ax.set_ylabel("Daily Frequency [%]")
    ax2 = ax.twinx()
    ax2.set_ylabel("Daily Frequency [%]")
    ax2.set_ylim(-2, 102)
    ax2.set_position([0.1, 0.2, 0.75, 0.7])
    ax2.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    return fig, gdf


if __name__ == "__main__":
    plotter({})
