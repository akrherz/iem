"""IEMAccess daily summary ranges"""
import datetime

from pandas.io.sql import read_sql
import matplotlib.dates as mdates
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = {
    "below": "Daily Range Below Emphasis",
    "touches": "Daily Range Touches Emphasis",
    "above": "Daily Range At or Above Emphasis",
}

PDICT2 = {
    "tmpf": "Air Temperature",
    "dwpf": "Dew Point Temperature",
    "feel": "Feels Like Temperature",
    "rh": "Relative Humidity",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    today = datetime.datetime.now()
    desc["data"] = True
    desc[
        "description"
    ] = """This plot presents the range between the min
    and maximum observation of your choice for a given station and a given
    year.  Some of these values are only computed based on hourly reports,
    so they would be represent a true min and max of a continuously observed
    variable."""
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="AMW",
            label="Select Station:",
            network="IA_ASOS",
        ),
        dict(
            type="year", name="year", default=today.year, label="Select Year:"
        ),
        dict(
            type="int",
            name="emphasis",
            default="-99",
            label=(
                "Temperature(&deg;F) or RH(%) Line "
                "of Emphasis (-99 disables):"
            ),
        ),
        dict(
            type="select",
            name="var",
            label="Which variable to plot?",
            default="dwpf",
            options=PDICT2,
        ),
        dict(
            type="select",
            name="opt",
            label="Option for Highlighting",
            default="touches",
            options=PDICT,
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    pgconn = get_dbconn("iem")
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["zstation"]
    year = ctx["year"]
    emphasis = ctx["emphasis"]
    opt = ctx["opt"]
    varname = ctx["var"]

    df = read_sql(
        f"""
        select day, max_{varname}, min_{varname}
        from summary_{year} s JOIN stations t on (s.iemid = t.iemid)
        where t.id = %s and t.network = %s and
        max_{varname} is not null and
        min_{varname} is not null
        ORDER by day ASC
    """,
        pgconn,
        params=(station, ctx["network"]),
        index_col="day",
    )
    if df.empty:
        raise NoDataFound("No Data Found!")
    df["range"] = df["max_" + varname] - df["min_" + varname]

    (fig, ax) = figure(apctx=ctx)
    bars = ax.bar(
        df.index.values,
        df["range"].values,
        ec="g",
        fc="g",
        bottom=df["min_" + varname].values,
        zorder=1,
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-d\n%b"))
    hits = []
    if emphasis > -99:
        for i, mybar in enumerate(bars):
            y = mybar.get_y() + mybar.get_height()
            if (
                (y >= emphasis and opt == "touches")
                or (mybar.get_y() >= emphasis and opt == "above")
                or (y < emphasis and opt == "below")
            ):
                mybar.set_facecolor("r")
                mybar.set_edgecolor("r")
                hits.append(df.index.values[i])
        ax.axhline(emphasis, lw=2, color="k")
        ax.text(
            df.index.values[-1] + datetime.timedelta(days=2),
            emphasis,
            "%s" % (emphasis,),
            ha="left",
            va="center",
        )
    ax.grid(True)
    ax.set_ylabel(
        "%s %s" % (PDICT2[varname], r"$^\circ$F" if varname != "rh" else "%")
    )
    ax.set_title(
        "%s [%s] %s Daily Min/Max %s\nPeriod: %s to %s"
        % (
            ctx["_nt"].sts[station]["name"],
            station,
            year,
            PDICT2[varname],
            df.index.values[0].strftime("%-d %b"),
            df.index.values[-1].strftime("%-d %b"),
        )
    )

    box = ax.get_position()
    ax.set_position(
        [box.x0, box.y0 + box.height * 0.05, box.width, box.height * 0.95]
    )
    ax.set_xlabel(
        ("Days meeting emphasis: %s, first: %s last: %s")
        % (
            len(hits),
            hits[0].strftime("%B %d") if hits else "None",
            hits[-1].strftime("%B %d") if hits else "None",
        )
    )
    delta = datetime.timedelta(days=1)
    ax.set_xlim(df.index.values[0] - delta, df.index.values[-1] + delta)
    return fig, df


if __name__ == "__main__":
    plotter(dict())
