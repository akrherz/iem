"""Combined frequencies."""
import calendar
import itertools

from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot.use_agg import plt
from pyiem.exceptions import NoDataFound


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc[
        "description"
    ] = """The IEM computes daily summaries of ASOS station
    data based on available station summaries and computed summaries based
    on available hourly data.  This chart presents the frequency combination
    of one or more variables.  Please let us know if you want additional
    fields added to this tool."""
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
            name="max_dwpf_below",
            default=50,
            optional=True,
            label="Daily Maximum Dewpoint Below (threshold F): [optional]",
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
    """ Go """
    pgconn = get_dbconn("iem")
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    params = []
    labels = {"all_hit": "All Combined"}
    if ctx.get("max_rh_below"):
        params.append(
            ("case when max_rh < %.0f " "then 1 else 0 end as rh_hit")
            % (ctx["max_rh_below"],)
        )
        labels["rh_hit"] = "Max RH < %.0f%%" % (ctx["max_rh_below"],)
    if ctx.get("max_tmpf_range"):
        tokens = [int(i) for i in ctx["max_tmpf_range"].split("to")]
        params.append(
            (
                "case when max_tmpf::int >= %s and max_tmpf::int <= %s "
                "then 1 else 0 end as tmpf_hit"
            )
            % (tokens[0], tokens[1])
        )
        labels["tmpf_hit"] = "High Temp %.0fF - %.0fF" % (tokens[0], tokens[1])
    if ctx.get("max_dwpf_below"):
        params.append(
            ("case when max_dwpf < %.0f " "then 1 else 0 end as dwpf_hit")
            % (ctx["max_dwpf_below"],)
        )
        labels["dwpf_hit"] = "Max Dewpoint < %.0fF" % (ctx["max_dwpf_below"],)
    if ctx.get("avg_smph_below"):
        params.append(
            (
                "case when avg_sknt * 1.15 < %.0f "
                "then 1 else 0 end as smph_hit"
            )
            % (ctx["avg_smph_below"],)
        )
        labels["smph_hit"] = "Avg Wind < %.0fMPH" % (ctx["avg_smph_below"],)
    if not params:
        raise NoDataFound("Please select some options for plotting.")
    df = read_sql(
        """
        SELECT """
        + " , ".join(params)
        + """
        , extract(doy from day) as doy
        from summary s JOIN stations t
        ON (s.iemid = t.iemid) WHERE t.id = %s and t.network = %s
    """,
        pgconn,
        params=(station, ctx["network"]),
    )
    if df.empty:
        raise NoDataFound("No Data Found.")

    df["all_hit"] = 1
    for col in df.columns:
        if col == "doy":
            continue
        df.at[df[col] < 1, "all_hit"] = 0
    gdf = df.groupby("doy").mean()

    (fig, ax) = plt.subplots(1, 1)
    colors = itertools.cycle(["r", "g", "b", "c", "m", "y"])
    for col in df.columns:
        if col == "doy":
            continue
        color = "k" if col == "all_hit" else next(colors)
        ax.plot(
            gdf.index.values,
            gdf[col].values * 100.0,
            lw=2,
            label=labels[col],
            color=color,
        )

    ax.legend(ncol=3, loc=(-0.05, -0.21), fontsize=10)
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_position([0.1, 0.2, 0.75, 0.7])
    ax.set_xlim(1, 365)
    ax.set_ylim(-2, 102)
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax.grid(True)
    ax.set_ylabel("Daily Frequency [%]")
    ab = ctx["_nt"].sts[station]["archive_begin"]
    ab = "N/A" if ab is None else ab
    ax.set_title(
        ("%s [%s] (%s-)\nDaily Observed Frequency")
        % (ctx["_nt"].sts[station]["name"], ab.year, station)
    )
    ax2 = ax.twinx()
    ax2.set_ylabel("Daily Frequency [%]")
    ax2.set_ylim(-2, 102)
    ax2.set_position([0.1, 0.2, 0.75, 0.7])
    ax2.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    return fig, gdf


if __name__ == "__main__":
    plotter(dict())
