"""Storm Motion 2D Histogram."""
import datetime
from collections import OrderedDict

from pandas.io.sql import read_sql
from pyiem.datatypes import speed
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = OrderedDict(
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


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc["cache"] = 600
    desc[
        "description"
    ] = """Some of the warnings that the National Weather
    Service issues includes a storm motion vector.  This application
    plots the speed vs direction of the vector and includes a kernel density
    estimate (KDE) overlay.
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
    ]
    return desc


def plotter(fdict):
    """ Go """
    import seaborn as sns

    ctx = get_autoplot_context(fdict, get_description())
    phenomena = ctx["p"]
    date = ctx.get("date")
    wfo = ctx["wfo"]
    pgconn = get_dbconn("postgis")
    ps = [phenomena]
    if phenomena == "_A":
        ps = ["TO", "SV"]
    df = read_sql(
        """
        SELECT issue at time zone 'UTC' as issue,
        tml_direction, tml_sknt from sbw
        WHERE phenomena in %s and wfo = %s and status = 'NEW' and
        tml_direction is not null and tml_sknt is not null ORDER by issue
    """,
        pgconn,
        params=(tuple(ps), wfo),
    )
    if df.empty:
        raise NoDataFound("No Data Found.")

    g = sns.jointplot(
        df["tml_direction"],
        speed(df["tml_sknt"], "KT").value("MPH"),
        s=40,
        stat_func=None,
        zorder=1,
        color="tan",
    ).plot_joint(sns.kdeplot, n_levels=6)
    g.ax_joint.set_xlabel("Storm Motion From Direction")
    g.ax_joint.set_ylabel("Storm Speed [MPH]")
    g.ax_joint.set_xticks(range(0, 361, 45))
    g.ax_joint.set_xticklabels(
        ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"]
    )
    if date:
        df2 = df[df["issue"].dt.date == date]
        g.ax_joint.scatter(
            df2["tml_direction"],
            speed(df2["tml_sknt"], "KT").value("MPH"),
            color="r",
            s=50,
            label=date.strftime("%b %-d, %Y"),
            zorder=2,
        )
    g.ax_joint.legend()
    g.ax_joint.grid()
    g.ax_marg_x.set_title(
        ("NWS %s\n%s Storm Motion\n" "%s warnings ploted between %s and %s")
        % (
            ctx["_nt"].sts[wfo]["name"],
            PDICT[phenomena],
            len(df.index),
            df["issue"].min().date().strftime("%b %-d, %Y"),
            df["issue"].max().date().strftime("%b %-d, %Y"),
        )
    )
    g.fig.subplots_adjust(top=0.9)
    return g.fig, df


if __name__ == "__main__":
    plotter(dict())
