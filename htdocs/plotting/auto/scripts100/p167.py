"""Flight category by hour"""
import datetime

import numpy as np
import pytz
import pandas as pd
import matplotlib.colors as mpcolors
from matplotlib.patches import Rectangle
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn, utc
from pyiem.exceptions import NoDataFound


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This chart summarizes Flight Category by hour
    and day of a given month.  In the case of multiple observations for a
    given hour, the worst category is plotted.

<table class="table table-condensed table-bordered">
<thead><tr><th>code</th><th>Label</th><th>Description</th></tr></thead>
<tbody>
<tr><td>Unknown</td><td>Unknown</td><td>No report or missing visibility for
that hour</td></tr>
<tr><td>VFR</td><td>Visual Flight Rules</td><td>
Ceiling &gt; 3000' AGL and visibility &gt; 5 statutes miles (green)</td></tr>
<tr><td>MVFR</td><td>Marginal Visual Flight Rules</td><td>
1000-3000' ceilings and/or 3-5 statute miles, inclusive (blue)</td></tr>
<tr><td>IFR</td><td>Instrument Fight Rules</td><td>
500 - &lt; 1000' ceilings and/or 1 to  &lt; 3 statute miles (red)</td></tr>
<tr><td>LIFR</td><td>Low Instrument Flight Rules</td><td>
&lt; 500' AGL ceilings and/or &lt; 1 mile (magenta)</td></tr>
</tbody>
</table>
</tbody>
</table>
    """
    today = datetime.date.today()
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="DSM",
            label="Select Station:",
            network="IA_ASOS",
        ),
        dict(
            type="month",
            name="month",
            label="Select Month:",
            default=today.month,
        ),
        dict(
            type="year",
            name="year",
            label="Select Year:",
            default=today.year,
            min=1970,
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["zstation"]
    year = ctx["year"]
    month = ctx["month"]

    tzname = ctx["_nt"].sts[station]["tzname"]
    tzinfo = pytz.timezone(tzname)

    # Figure out the 1rst and last of this month in the local time zone
    sts = utc(year, month, 3)
    sts = sts.astimezone(tzinfo).replace(day=1, hour=0, minute=0)
    ets = (sts + datetime.timedelta(days=35)).replace(day=1)
    days = (ets - sts).days
    data = np.zeros((24, days))
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            """
        SELECT valid at time zone %s as ts,
        skyc1, skyc2, skyc3, skyc4, skyl1, skyl2, skyl3, skyl4, vsby
        from alldata where station = %s and valid BETWEEN %s and %s
        and vsby is not null and report_type = 3 ORDER by valid ASC
        """,
            conn,
            params=(tzname, station, sts, ets),
            index_col=None,
        )

    if df.empty:
        raise NoDataFound("No database entries found for station, sorry!")

    # 0 Unknown
    # 1 VFR: Ceiling >3000' AGL and visibility >5 statutes miles (green)
    # 2 MVFR: 1000-3000' and/or 3-5 statute miles, inclusive (blue)
    # 3 IFR: 500 - <1000' and/or 1 to <3 statute miles (red)
    # 4 LIFR: < 500' AGL and/or < 1 mile (magenta)
    lookup = {4: "LIFR", 3: "IFR", 2: "MVFR", 1: "VFR", 0: "UNKNOWN"}
    conds = []
    for _, row in df.iterrows():
        x = row["ts"].day - 1
        y = row["ts"].hour
        level = 100000  # arb high number
        coverages = [row["skyc1"], row["skyc2"], row["skyc3"], row["skyc4"]]
        if "OVC" in coverages:
            idx = coverages.index("OVC")
            level = [row["skyl1"], row["skyl2"], row["skyl3"], row["skyl4"]][
                idx
            ]
        if "BKN" in coverages and level == 10000:
            idx = coverages.index("BKN")
            level = [row["skyl1"], row["skyl2"], row["skyl3"], row["skyl4"]][
                idx
            ]
        if row["vsby"] > 5 and level > 3000:
            val = 1
        elif level < 500 or row["vsby"] < 1:
            val = 4
        elif level < 1000 or row["vsby"] < 3:
            val = 3
        elif level <= 3000 or row["vsby"] <= 5:
            val = 2
        else:
            val = 0
        data[y, x] = max(data[y, x], val)
        conds.append(lookup[val])
        # print row['ts'], y, x, val, data[y, x], level, row['vsby']

    df["flstatus"] = conds
    title = (
        f"{ctx['_sname']}:: {sts:%b %Y} Flight Category\n"
        "based on Hourly METAR Cloud Amount/Level and Visibility Reports"
    )
    (fig, ax) = figure_axes(apctx=ctx, title=title)

    ax.set_facecolor("skyblue")

    colors = ["#EEEEEE", "green", "blue", "red", "magenta"]
    cmap = mpcolors.ListedColormap(colors)
    norm = mpcolors.BoundaryNorm(boundaries=range(6), ncolors=5)
    ax.imshow(
        np.flipud(data),
        aspect="auto",
        extent=[0.5, days + 0.5, -0.5, 23.5],
        cmap=cmap,
        interpolation="nearest",
        norm=norm,
    )
    ax.set_yticks(range(0, 24, 3))
    ax.set_yticklabels(
        ["Mid", "3 AM", "6 AM", "9 AM", "Noon", "3 PM", "6 PM", "9 PM"]
    )
    ax.set_xticks(range(1, days + 1))
    ax.set_ylabel(f"Hour of Local Day ({tzname})")
    ax.set_xlabel(f"Day of {sts:%b %Y}")

    rects = []
    for color in colors:
        rects.append(Rectangle((0, 0), 1, 1, fc=color))

    ax.grid(True)
    # Shrink current axis's height by 10% on the bottom
    box = ax.get_position()
    ax.set_position(
        [box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9]
    )

    ax.legend(
        rects,
        ["Unknown", "VFR", "MVFR", "IFR", "LIFR"],
        loc="upper center",
        fontsize=14,
        bbox_to_anchor=(0.5, -0.09),
        fancybox=True,
        shadow=True,
        ncol=5,
    )

    return fig, df


if __name__ == "__main__":
    plotter(dict(station="DSM", year=2009, month=1, network="IA_ASOS"))
