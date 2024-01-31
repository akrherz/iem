"""
This application generates a comparison of daily
high and low temperatures between two automated ASOS sites of your
choosing.
"""
import datetime

import matplotlib.dates as mdates
import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn

PDICT = {
    "temp": "High and Low Temperature",
    "dewp": "High and Low Dew Point Temp",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
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
            network="IA_ASOS",
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
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station1 = ctx["zstation1"]
    station2 = ctx["zstation2"]
    sdate = ctx["sdate"]
    edate = ctx["edate"]
    varname = ctx["var"]

    d = "tmpf" if varname == "temp" else "dwpf"
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            f"""
        WITH one as (
            SELECT day, max_{d}, min_{d} from summary s JOIN stations t on
            (s.iemid = t.iemid) WHERE t.id = %s and t.network = %s and
            s.day >= %s and s.day <= %s),

        two as (
            SELECT day, max_{d}, min_{d} from summary s JOIN stations t on
            (s.iemid = t.iemid) WHERE t.id = %s and t.network = %s and
            s.day >= %s and s.day <= %s)

        SELECT one.day as day,
        one.max_{d} as one_high, one.min_{d} as one_low,
        two.max_{d} as two_high, two.min_{d} as two_low
        from one JOIN two on (one.day = two.day) ORDER by day ASC
        """,
            conn,
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

    fig = figure(
        title=(
            f"[{station1}] {ctx['_nt1'].sts[station1]['name']} minus "
            f"[{station2}] {ctx['_nt2'].sts[station2]['name']}"
        ),
        subtitle=(
            f"{PDICT[varname]} Difference: "
            f"{sdate:%-d %b %Y} - {edate:%-d %b %Y}"
        ),
        apctx=ctx,
    )
    ax = fig.subplots(2, 1, sharex=True)

    for i, vname in enumerate(["high", "low"]):
        col = f"{vname}_diff"
        df2 = df[df[col] > 0]
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
            f"{station1} Higher ({freq1:.1f}%)",
            transform=ax[i].transAxes,
            va="top",
            ha="center",
            bbox={"color": "w"},
            color="r",
            fontsize=8,
        )
        ax[i].text(
            0.5,
            0.01,
            f"{station2} Higher ({freq2:.1f}%)",
            transform=ax[i].transAxes,
            va="bottom",
            ha="center",
            bbox={"color": "w"},
            color="b",
            fontsize=8,
        )
        ax[i].text(
            0.95,
            0.99,
            f"Bias: {df[col].mean():.2f}",
            transform=ax[i].transAxes,
            va="top",
            ha="right",
            color="k",
            bbox={"color": "w"},
            fontsize=8,
        )
        ax[i].set_ylabel(
            f"{vname.capitalize()} {varname.capitalize()} Difference "
            r"$^\circ$F"
        )
        rng = df[col].max() - df[col].min()
        ax[i].set_ylim(df[col].min() - 0.2 * rng, df[col].max() + 0.2 * rng)

    return fig, df


if __name__ == "__main__":
    plotter({})
