"""Close to average!"""
import calendar

import numpy as np
from pandas.io.sql import read_sql
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = {"high": "High temperature", "low": "Low Temperature"}


def smooth(x, window_len=11, window="hanning"):
    """Smoother"""
    if window_len < 3:
        return x

    s = np.r_[x[window_len - 1 : 0 : -1], x, x[-1:-window_len:-1]]
    if window == "flat":  # moving average
        w = np.ones(window_len, "d")
    else:
        w = eval("np." + window + "(window_len)")

    y = np.convolve(w / w.sum(), s, mode="valid")
    return y


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = dict()
    desc["data"] = True
    desc[
        "description"
    ] = """This plot displays the frequency of a daily high
    or low temperature being within a certain bounds of the long term NCEI
    climatology for the location."""
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IA0200",
            label="Select Station:",
            network="IACLIMATE",
        ),
        dict(
            type="int",
            name="min",
            default="-5",
            label="Lower Bound (F) of Temperature Range",
        ),
        dict(
            type="int",
            name="max",
            default="5",
            label="Upper Bound (F) of Temperature Range",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    pgconn = get_dbconn("coop")
    ctx = get_autoplot_context(fdict, get_description())
    minv = ctx["min"]
    maxv = ctx["max"]
    if minv > maxv:
        temp = minv
        minv = maxv
        maxv = temp
    station = ctx["station"]
    table = "alldata_%s" % (station[:2],)

    df = read_sql(
        f"""
    WITH climate as (
        SELECT to_char(valid, 'mmdd') as sday, high, low from
        ncei_climate91 where station = %s
    )
    SELECT extract(doy from day) as doy, count(*),
    SUM(case when a.high >= (c.high + %s) and a.high < (c.high + %s)
            then 1 else 0 end) as high_count,
    SUM(case when a.low >= (c.low + %s) and a.low < (c.low + %s)
            then 1 else 0 end) as low_count
    FROM {table} a JOIN climate c on (a.sday = c.sday)
    WHERE a.sday != '0229' and station = %s GROUP by doy ORDER by doy ASC
    """,
        pgconn,
        params=(
            ctx["_nt"].sts[station]["ncei91"],
            minv,
            maxv,
            minv,
            maxv,
            station,
        ),
        index_col="doy",
    )
    if df.empty:
        raise NoDataFound("No Data Found.")

    df["high_freq"] = df["high_count"] / df["count"] * 100.0
    df["low_freq"] = df["low_count"] / df["count"] * 100.0
    hvals = smooth(df["high_freq"].values, 7, "flat")
    lvals = smooth(df["low_freq"].values, 7, "flat")
    title = (
        "%s [%s]\nFreq of Temp between "
        r"%s$^\circ$F and %s$^\circ$F of NCEI-81 Average"
    ) % (ctx["station"], ctx["_nt"].sts[ctx["station"]]["name"], minv, maxv)
    (fig, ax) = figure_axes(title=title)

    ax.plot(df.index.values, hvals[3:-3], color="r", label="High", zorder=1)
    ax.plot(df.index.values, lvals[3:-3], color="b", label="Low", zorder=1)
    ax.axhline(50, lw=2, color="green", zorder=2)
    ax.set_ylabel("Percentage of Years [%]")
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.legend(loc="best")
    ax.set_xlabel("* seven day smoother applied")
    ax.set_xlim(1, 367)
    ax.set_ylim(0, 100)
    ax.grid(True)
    return fig, df


if __name__ == "__main__":
    plotter(dict())
