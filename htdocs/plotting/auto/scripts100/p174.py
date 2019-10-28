"""comparison"""
import datetime
from collections import OrderedDict

from pandas.io.sql import read_sql
import matplotlib.dates as mdates
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = OrderedDict(
    (
        ("temp", "High and Low Temperature"),
        ("dewp", "High and Low Dew Point Temp"),
    )
)


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This application generates a comparison of daily
    high and low temperatures between two automated ASOS sites of your
    choosing."""
    edate = datetime.date.today()
    sdate = edate - datetime.timedelta(days=90)
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation1",
            default="DSM",
            network="IA_ASOS",
            label="Select Station 1:",
        ),
        dict(
            type="zstation",
            name="zstation2",
            default="IKV",
            network="AWOS",
            label="Select Station 2:",
        ),
        dict(
            type="select",
            options=PDICT,
            name="var",
            default="temp",
            label="Select variable to plot comparison of",
        ),
        dict(
            type="date",
            name="sdate",
            default=sdate.strftime("%Y/%m/%d"),
            label="Start Date:",
        ),
        dict(
            type="date",
            name="edate",
            default=edate.strftime("%Y/%m/%d"),
            label="End Date:",
        ),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("iem")
    ctx = get_autoplot_context(fdict, get_description())
    station1 = ctx["zstation1"]
    station2 = ctx["zstation2"]
    sdate = ctx["sdate"]
    edate = ctx["edate"]
    varname = ctx["var"]

    d = "tmpf" if varname == "temp" else "dwpf"
    df = read_sql(
        """
    WITH one as (
        SELECT day, max_"""
        + d
        + """, min_"""
        + d
        + """
        from summary s JOIN stations t on
        (s.iemid = t.iemid) WHERE t.id = %s and t.network = %s and
        s.day >= %s and s.day <= %s),

    two as (
        SELECT day, max_"""
        + d
        + """, min_"""
        + d
        + """
        from summary s JOIN stations t on
        (s.iemid = t.iemid) WHERE t.id = %s and t.network = %s and
        s.day >= %s and s.day <= %s)

    SELECT one.day as day,
    one.max_"""
        + d
        + """ as one_high, one.min_"""
        + d
        + """ as one_low,
    two.max_"""
        + d
        + """ as two_high, two.min_"""
        + d
        + """ as two_low
    from one JOIN two on (one.day = two.day) ORDER by day ASC
    """,
        pgconn,
        params=(
            station1,
            ctx["network1"],
            sdate,
            edate,
            station2,
            ctx["network2"],
            sdate,
            edate,
        ),
        index_col="day",
    )
    if df.empty:
        raise NoDataFound("No data found for this comparison")
    df["high_diff"] = df["one_high"] - df["two_high"]
    df["low_diff"] = df["one_low"] - df["two_low"]

    (fig, ax) = plt.subplots(2, 1, sharex=True)

    ax[0].set_title(
        ("[%s] %s minus [%s] %s\n" "%s Difference: %s - %s")
        % (
            station1,
            ctx["_nt1"].sts[station1]["name"],
            station2,
            ctx["_nt2"].sts[station2]["name"],
            PDICT[varname],
            sdate.strftime("%-d %b %Y"),
            edate.strftime("%-d %b %Y"),
        )
    )

    for i, vname in enumerate(["high", "low"]):
        col = "%s_diff" % (vname,)
        df2 = df[df[col] > 0]
        if df2.empty:
            continue
        freq1 = len(df2.index) / float(len(df.index)) * 100.0
        ax[i].bar(df2.index.values, df2[col].values, fc="r", ec="r")
        df2 = df[df[col] < 0]
        freq2 = len(df2.index) / float(len(df.index)) * 100.0
        ax[i].bar(df2.index.values, df2[col].values, fc="b", ec="b")
        ax[i].xaxis.set_major_formatter(mdates.DateFormatter("%-d %b\n%Y"))
        ax[i].grid(True)
        ax[i].text(
            0.5,
            0.95,
            "%s Higher (%.1f%%)" % (station1, freq1),
            transform=ax[i].transAxes,
            va="top",
            ha="center",
            color="r",
            fontsize=8,
        )
        ax[i].text(
            0.5,
            0.01,
            "%s Higher (%.1f%%)" % (station2, freq2),
            transform=ax[i].transAxes,
            va="bottom",
            ha="center",
            color="b",
            fontsize=8,
        )
        ax[i].text(
            0.95,
            0.99,
            "Bias: %.2f" % (df[col].mean(),),
            transform=ax[i].transAxes,
            va="top",
            ha="right",
            color="k",
            fontsize=8,
        )
        ax[i].set_ylabel(
            (r"%s %s Difference $^\circ$F")
            % (vname.capitalize(), varname.capitalize())
        )
        y0 = min([df[col].min(), -1])
        y1 = max([df[col].max(), 1])
        ax[i].set_ylim(y0 * 1.2, y1 * 1.2)

    return fig, df


if __name__ == "__main__":
    plotter(dict())
