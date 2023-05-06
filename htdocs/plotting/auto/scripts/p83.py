"""period averages around a date"""
import datetime

import numpy as np
import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from scipy import stats

PDICT = {
    "high": "Average High Temperature",
    "low": "Average Low Temperature",
    "precip": "Total Precipitation",
}
UNITS = {"high": r"$^\circ$F", "low": r"$^\circ$F", "precip": "inch"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """This plot compares a period of days prior to
    a specified date to the same number of days after a date.  The specified
    date is not used in either statistical value.  If you select a period that
    includes leap day, there is likely some small ambiguity with the resulting
    plot labels.
    """
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station",
            network="IACLIMATE",
        ),
        dict(
            type="select",
            name="var",
            default="high",
            label="Which Variable:",
            options=PDICT,
        ),
        dict(type="int", name="days", default=45, label="How many days:"),
        dict(type="month", name="month", default="7", label="Select Month:"),
        dict(type="day", name="day", default="15", label="Select Day:"),
        dict(
            type="year",
            name="year",
            default=datetime.date.today().year,
            label="Year to Highlight in Chart",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx["station"]
    varname = ctx["var"]
    month = ctx["month"]
    day = ctx["day"]
    dt = datetime.date(2000, month, day)
    days = ctx["days"]
    year = ctx["year"]
    ctx["before_period"] = "%s-%s" % (
        (dt - datetime.timedelta(days=days)).strftime("%-d %b"),
        (dt - datetime.timedelta(days=1)).strftime("%-d %b"),
    )
    ctx["after_period"] = "%s-%s" % (
        (dt + datetime.timedelta(days=1)).strftime("%-d %b"),
        (dt + datetime.timedelta(days=days)).strftime("%-d %b"),
    )

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            """
        with data as (
            SELECT day, year,
            count(*) OVER
                (ORDER by day ASC ROWS BETWEEN %s PRECEDING AND 1 PRECEDING)
                as cb,
            avg(high) OVER
                (ORDER by day ASC ROWS BETWEEN %s PRECEDING AND 1 PRECEDING)
                as hb,
            avg(low) OVER
                (ORDER by day ASC ROWS BETWEEN %s PRECEDING AND 1 PRECEDING)
                as lb,
            sum(precip) OVER
                (ORDER by day ASC ROWS BETWEEN %s PRECEDING AND 1 PRECEDING)
                as pb,
            count(*) OVER
                (ORDER by day ASC ROWS BETWEEN 1 FOLLOWING AND %s FOLLOWING)
                as ca,
            avg(high) OVER
                (ORDER by day ASC ROWS BETWEEN 1 FOLLOWING AND %s FOLLOWING)
                as ha,
            avg(low)OVER
                (ORDER by day ASC ROWS BETWEEN 1 FOLLOWING AND %s FOLLOWING)
                as la,
            sum(precip) OVER
                (ORDER by day ASC ROWS BETWEEN 1 FOLLOWING AND %s FOLLOWING)
                as pa
            from alldata WHERE station = %s)

        SELECT year, hb as high_before, lb as low_before, pb as precip_before,
        ha as high_after, la as low_after, pa as precip_after from
        data where cb = ca and
        cb = %s and extract(month from day) = %s and extract(day from day) = %s
        """,
            conn,
            params=(
                days,
                days,
                days,
                days,
                days,
                days,
                days,
                days,
                station,
                days,
                month,
                day,
            ),
            index_col="year",
        )
    if df.empty:
        raise NoDataFound("No Data Found.")

    xvals = df[varname + "_before"].values
    yvals = df[varname + "_after"].values
    fig, ax = figure_axes(apctx=ctx)
    ax.scatter(xvals, yvals, zorder=2)
    if year in df.index:
        row = df.loc[year]
        ax.scatter(
            row[varname + "_before"],
            row[varname + "_after"],
            color="r",
            zorder=3,
        )
        ax.text(
            row[varname + "_before"],
            row[varname + "_after"],
            "%s" % (year,),
            ha="right",
            va="bottom",
            color="r",
        )
    msg = (
        f"{ctx['_sname']} :: {PDICT.get(varname)} over {days} days "
        f"prior to and after {dt:%-d %B}"
    )
    tokens = msg.split()
    sz = int(len(tokens) / 2)
    ax.set_title(" ".join(tokens[:sz]) + "\n" + " ".join(tokens[sz:]))

    minv = min([min(xvals), min(yvals)])
    maxv = max([max(xvals), max(yvals)])
    ax.plot([minv - 5, maxv + 5], [minv - 5, maxv + 5], label="x=y", color="b")
    yavg = np.average(yvals)
    xavg = np.average(xvals)
    ax.axhline(yavg, label="After Avg: %.2f" % (yavg,), color="r", lw=2)
    ax.axvline(xavg, label="Before Avg: %.2f" % (xavg,), color="g", lw=2)
    df2 = df[np.logical_and(xvals >= xavg, yvals >= yavg)]
    ax.text(
        0.98,
        0.98,
        "I: %.1f%%" % (len(df2) / float(len(xvals)) * 100.0,),
        transform=ax.transAxes,
        bbox=dict(edgecolor="tan", facecolor="white"),
        va="top",
        ha="right",
        zorder=3,
    )

    df2 = df[np.logical_and(xvals < xavg, yvals < yavg)]
    ax.text(
        0.02,
        0.02,
        "III: %.1f%%" % (len(df2) / float(len(xvals)) * 100.0,),
        transform=ax.transAxes,
        bbox=dict(edgecolor="tan", facecolor="white"),
        zorder=3,
    )

    df2 = df[np.logical_and(xvals >= xavg, yvals < yavg)]
    ax.text(
        0.98,
        0.02,
        "IV: %.1f%%" % (len(df2) / float(len(xvals)) * 100.0,),
        transform=ax.transAxes,
        bbox=dict(edgecolor="tan", facecolor="white"),
        va="bottom",
        ha="right",
        zorder=3,
    )

    df2 = df[np.logical_and(xvals < xavg, yvals >= yavg)]
    ax.text(
        0.02,
        0.98,
        "II: %.1f%%" % (len(df2) / float(len(xvals)) * 100.0,),
        transform=ax.transAxes,
        bbox=dict(edgecolor="tan", facecolor="white"),
        va="top",
        zorder=3,
    )

    ax.set_xlabel(
        "%s %s, Period: %s"
        % (PDICT.get(varname), UNITS.get(varname), ctx["before_period"])
    )
    ax.set_ylabel(
        "%s %s, Period: %s"
        % (PDICT.get(varname), UNITS.get(varname), ctx["after_period"])
    )
    ax.grid(True)
    ax.set_xlim(minv - 5, maxv + 5)
    ax.set_ylim(minv - 5, maxv + 5)

    _, _, r_value, _, _ = stats.linregress(xvals, yvals)
    ax.text(
        0.65,
        0.02,
        "R$^2$=%.2f bias=%.2f" % (r_value**2, yavg - xavg),
        ha="right",
        transform=ax.transAxes,
        bbox=dict(color="white"),
    )

    # Shrink current axis's height by 10% on the bottom
    box = ax.get_position()
    ax.set_position(
        [box.x0, box.y0 + box.height * 0.15, box.width, box.height * 0.85]
    )

    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.1),
        fancybox=True,
        shadow=True,
        ncol=3,
        scatterpoints=1,
        fontsize=12,
    )

    return fig, df


if __name__ == "__main__":
    plotter({})
