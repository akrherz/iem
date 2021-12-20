"""Storm Motion 2D Histogram."""
import datetime

from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context, get_dbconn, convert_value
from pyiem.exceptions import NoDataFound
import seaborn as sns


PDICT = dict(
    (
        ("TO", "Tornado Warning"),
        ("SV", "Severe Thunderstorm Warning"),
        ("_A", "Severe Tstorm + Tornado Warning"),
        ("EW", "Extreme Wind"),
        ("FA", "Flood Advisory/Warning"),
        ("FF", "Flash Flood Warning"),
        ("MA", "Marine Warning"),
        ("SQ", "Snow Squall"),
    )
)
PDICT2 = {
    "NEW": "at Issuance",
    "ANY": "at Issuance or Update",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["cache"] = 600
    desc[
        "description"
    ] = """Some of the warnings that the National Weather
    Service issues includes a storm motion vector.  This application
    plots the speed vs direction of the vector and includes a kernel density
    estimate (KDE) overlay.  You can optionally pick a date to highlight on the
    chart.  This date is a central time zone date.
    """
    today = datetime.date.today()
    desc["arguments"] = [
        dict(
            type="date",
            name="date",
            default=today.strftime("%Y/%m/%d"),
            label="Optional Date to Highlight on Map:",
            min="2007/07/16",
            max=today.strftime("%Y/%m/%d"),
            optional=True,
        ),
        dict(
            type="networkselect",
            name="wfo",
            default="DMX",
            label="Select Forecast Office:",
            network="WFO",
        ),
        dict(
            type="select",
            name="p",
            default="TO",
            options=PDICT,
            label="Warning Type:",
        ),
        dict(
            type="select",
            name="limit",
            default="NEW",
            options=PDICT2,
            label="Include only issuance or also updated (SVS, etc):",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    phenomena = ctx["p"]
    date = ctx.get("date")
    wfo = ctx["wfo"]
    pgconn = get_dbconn("postgis")
    ps = [phenomena]
    if phenomena == "_A":
        ps = ["TO", "SV"]
    statuslimit = "status = 'NEW'"
    title = "at Issuance"
    if ctx["limit"] == "ANY":
        title = "at Issuance or Update"
        statuslimit = "status != 'CAN'"
    df = read_sql(
        "SELECT issue at time zone 'America/Chicago' as issue, "
        "tml_direction, tml_sknt from sbw WHERE phenomena in %s and "
        f"wfo = %s and {statuslimit} and tml_direction is not null and "
        "tml_sknt is not null ORDER by issue",
        pgconn,
        params=(tuple(ps), wfo),
    )
    if df.empty:
        raise NoDataFound("No Data Found.")
    plotdf = df
    if date is not None:
        plotdf = df[df["issue"].dt.date != date]

    g = sns.jointplot(
        x=plotdf["tml_direction"].values,
        y=convert_value(plotdf["tml_sknt"], "knot", "mile / hour"),
        s=40,
        zorder=1,
        color="tan",
        xlim=(0, 360),
    ).plot_joint(sns.kdeplot, n_levels=6)
    g.ax_joint.set_xlabel("Storm Motion From Direction")
    g.ax_joint.set_ylabel("Storm Speed [MPH]")
    g.ax_joint.set_xticks(range(0, 361, 45))
    g.ax_joint.set_xticklabels("N NE E SE S SW W NW N".split())
    if date:
        df2 = df[df["issue"].dt.date == date]
        g.ax_joint.scatter(
            df2["tml_direction"],
            convert_value(df2["tml_sknt"], "knot", "mile / hour"),
            marker="+",
            color="r",
            s=50,
            label=date.strftime("%b %-d, %Y"),
            zorder=2,
        )
        g.ax_joint.legend(loc="best")
    g.ax_joint.grid()
    g.ax_marg_x.set_title(
        f"NWS {ctx['_nt'].sts[wfo]['name']}\n"
        f"{PDICT[phenomena]} Storm Motion {title}\n"
        f"{len(df.index)} events ploted between "
        f"{df['issue'].min().date():%b %-d, %Y} and "
        f"{df['issue'].max().date():%b %-d, %Y}"
    )
    g.fig.subplots_adjust(top=0.9, bottom=0.1, left=0.1)
    return g.fig, df


if __name__ == "__main__":
    plotter({})
