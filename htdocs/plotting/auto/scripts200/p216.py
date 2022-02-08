"""Consec days"""
import datetime

import numpy as np
import pandas as pd
from matplotlib.font_manager import FontProperties
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_dbconn

PDICT = {
    "above": "Temperature At or Above (AOA) Threshold",
    "below": "Temperature Below Threshold",
}
PDICT2 = {"high": "High Temperature", "low": "Low Temperature"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """This chart presents the longest daily streaks of having some
    temperature threshold meet."""
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station:",
            network="IACLIMATE",
        ),
        dict(
            type="select",
            name="var",
            default="high",
            options=PDICT2,
            label="Select which daily variable",
        ),
        dict(
            type="select",
            name="dir",
            default="below",
            options=PDICT,
            label="Select temperature direction",
        ),
        dict(
            type="int",
            name="threshold",
            default="32",
            label="Temperature Threshold (F):",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor()
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    threshold = ctx["threshold"]
    varname = ctx["var"]
    mydir = ctx["dir"]

    op = np.greater_equal if mydir == "above" else np.less
    cursor.execute(
        f"""
        select day, {varname},
        case when month > 6 then year + 1 else year end
        from alldata_{station[:2]} where station = %s and {varname} is not null
        ORDER by day ASC
    """,
        (station,),
    )
    if cursor.rowcount == 0:
        raise NoDataFound("Did not find any observations for station.")
    rows = []
    startdate = None
    running = 0
    for row in cursor:
        if op(row[1], threshold):
            if running == 0:
                startdate = row[0]
            running += 1
            continue
        if running == 0:
            continue
        rows.append(
            {
                "days": running,
                "season": row[0].year if mydir == "above" else row[2],
                "startdate": startdate,
                "enddate": row[0] - datetime.timedelta(days=1),
            }
        )
        running = 0
    if running > 0:
        rows.append(
            {
                "days": running,
                "season": row[0].year if mydir == "above" else row[2],
                "startdate": startdate,
                "enddate": row[0],
            }
        )
    if not rows:
        raise NoDataFound("Failed to find any streaks for given threshold.")
    df = pd.DataFrame(rows)

    label = "AOA" if mydir == "above" else "below"
    label2 = "Year" if mydir == "above" else "Season"
    title = r"[%s] %s %s Max Consec Days with %s %s %s$^\circ$F" % (
        station,
        ctx["_nt"].sts[station]["name"],
        label2,
        varname.capitalize(),
        label,
        threshold,
    )
    fig = figure(title=title, apctx=ctx)
    ax = fig.add_axes([0.1, 0.1, 0.5, 0.8])
    ax.set_ylabel(f"Max Streak by {label2} [days]")
    ax.grid(True)
    gdf = df.groupby("season").max()
    ax.bar(gdf.index.values, gdf["days"].values, width=1)
    val = gdf["days"].mean()
    ax.axhline(val, lw=2, color="r")
    ax.text(
        gdf.index.values[-1] + 2,
        val,
        f"Avg: {val:.1f}",
        color="r",
        bbox=dict(color="white"),
    )
    ax.set_xlabel(label2)

    # List out longest
    monofont = FontProperties(family="monospace", size=14)
    y = 0.84
    fig.text(
        0.65,
        y,
        "Top 20 Events\nStart Date  End Date     Days",
        fontproperties=monofont,
    )
    y -= 0.045
    fmt = "%b %-2d %Y"
    for _, row in (
        df.sort_values(by="days", ascending=False).head(20).iterrows()
    ):
        fig.text(
            0.65,
            y,
            "%s %s  %3i"
            % (
                row["startdate"].strftime(fmt),
                row["enddate"].strftime(fmt),
                row["days"],
            ),
            fontproperties=monofont,
        )
        y -= 0.034

    return fig, df


if __name__ == "__main__":
    plotter({})
