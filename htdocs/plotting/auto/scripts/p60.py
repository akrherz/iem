"""Hourly temperature frequencies."""
import datetime
import calendar

import numpy as np
import pandas as pd
import matplotlib.colors as mpcolors
from pyiem.plot import get_cmap
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound

PDICT = {"above": "At or Above Threshold", "below": "Below Threshold"}
PDICT2 = {
    "tmpf": "Air Temperature",
    "dwpf": "Dew Point Temp",
    "feel": "Feels Like Temp",
    "relh": "Relative Humidity",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This plot presents the hourly frequency of having
    a certain temperature above or below a given threshold.  Values are
    partitioned by week of the year to smooth out some of the day to day
    variation.

    <p><strong>Updated 29 Nov 2021</strong>: This plot was updated to always
    plot any non-zero frequency.  Any zeros are defaulted to a white color.
    """
    desc["data"] = True
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="DSM",
            network="IA_ASOS",
            label="Select Station:",
        ),
        dict(
            type="select",
            name="var",
            default="tmpf",
            options=PDICT2,
            label="Which Variable:",
        ),
        dict(
            type="int",
            name="threshold",
            default=32,
            label="Threshold (Temperature in F, RH in %)",
        ),
        dict(
            type="select",
            name="direction",
            default="below",
            label="Threshold direction:",
            options=PDICT,
        ),
        dict(
            optional=True,
            type="date",
            name="sdate",
            default="1900/01/01",
            label="Inclusive Start Local Date (optional):",
        ),
        dict(
            optional=True,
            type="date",
            name="edate",
            default=datetime.date.today().strftime("%Y/%m/%d"),
            label="Exclusive End Local Date (optional):",
        ),
        dict(type="cmap", name="cmap", default="jet", label="Color Ramp:"),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["zstation"]
    threshold = ctx["threshold"]
    direction = ctx["direction"]
    varname = ctx["var"]

    mydir = "<" if direction == "below" else ">="
    timelimiter = ""
    if station not in ctx["_nt"].sts:
        raise NoDataFound("Unknown station metadata.")
    tzname = ctx["_nt"].sts[station]["tzname"]
    if ctx.get("sdate"):
        timelimiter += (
            f" and valid at time zone '{tzname}' >= '{ctx['sdate']}'"
        )
    if ctx.get("edate"):
        timelimiter += f" and valid at time zone '{tzname}' < '{ctx['edate']}'"
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            f"""
            WITH data as (
                SELECT extract(week from valid) as week,
                extract(hour from (valid + '10 minutes'::interval)
                at time zone %s) as hour, {varname} as d,
                valid at time zone %s as local_valid from alldata where
                station = %s and {varname} between -70 and 140 {timelimiter}
            )
            SELECT week::int, hour::int,
            sum(case when d {mydir} %s then 1 else 0 end),
            count(*),
            min(local_valid)::date as min_valid,
            max(local_valid)::date as max_valid
            from data GROUP by week, hour
            """,
            conn,
            params=(tzname, tzname, station, threshold),
            index_col=None,
        )
    data = np.ones((24, 53), "f") * -1
    df["freq[%]"] = df["sum"] / df["count"] * 100.0
    for _, row in df.iterrows():
        data[int(row["hour"]), int(row["week"]) - 1] = row["freq[%]"]
    data = np.ma.masked_where(data <= 0, data)
    sts = datetime.datetime(2012, 1, 1)
    xticks = []
    for i in range(1, 13):
        ts = sts.replace(month=i)
        xticks.append(float(ts.strftime("%j")) / 7.0)

    units = r"$^\circ$F" if varname != "relh" else "%"
    title = (
        f"{ctx['_nt'].sts[station]['name']} [{station}]\n"
        f"Hourly {PDICT2[varname]} {PDICT[direction]} {threshold}{units} "
        f"({df['min_valid'].min():%-d %b %Y}-"
        f"{df['max_valid'].max():%-d %b %Y})"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    cmap = get_cmap(ctx["cmap"])
    cmap.set_bad("white")
    bins = np.arange(0, 101, 5, dtype="f")
    norm = mpcolors.BoundaryNorm(bins, cmap.N)
    res = ax.imshow(
        data,
        interpolation="nearest",
        aspect="auto",
        extent=[0, 53, 24, 0],
        cmap=cmap,
        norm=norm,
    )
    fig.colorbar(res, label="%", extend="neither")
    ax.grid(True, zorder=11)
    ax.set_xticks(xticks)
    ax.set_ylabel(f"{ctx['_nt'].sts[station]['tzname']} Timezone")
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0, 53)
    ax.set_ylim(0, 24)
    ax.set_yticks([0, 4, 8, 12, 16, 20, 24])
    ax.set_yticklabels(
        ["12 AM", "4 AM", "8 AM", "Noon", "4 PM", "8 PM", "Mid"]
    )

    return fig, df


if __name__ == "__main__":
    plotter({})
