"""Top 10 largest"""
import datetime
from collections import OrderedDict

from pandas.io.sql import read_sql
from matplotlib.font_manager import FontProperties
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot.use_agg import plt
from pyiem.exceptions import NoDataFound

MDICT = OrderedDict(
    [
        ("all", "No Month/Time Limit"),
        ("spring", "Spring (MAM)"),
        ("fall", "Fall (SON)"),
        ("winter", "Winter (DJF)"),
        ("summer", "Summer (JJA)"),
        ("jan", "January"),
        ("feb", "February"),
        ("mar", "March"),
        ("apr", "April"),
        ("may", "May"),
        ("jun", "June"),
        ("jul", "July"),
        ("aug", "August"),
        ("sep", "September"),
        ("oct", "October"),
        ("nov", "November"),
        ("dec", "December"),
    ]
)


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This table presents the 10 largest differences
    between the lowest and highest air temperature for a local calendar
    day."""
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="AMW",
            label="Select Station:",
            network="IA_ASOS",
        ),
        dict(
            type="select",
            name="month",
            default="all",
            label="Month Limiter",
            options=MDICT,
        ),
    ]
    return desc


def plotter(fdict):
    """ Go """
    font0 = FontProperties()
    font0.set_family("monospace")
    font0.set_size(16)
    pgconn = get_dbconn("iem")
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["zstation"]
    month = ctx["month"]

    if month == "all":
        months = range(1, 13)
    elif month == "fall":
        months = [9, 10, 11]
    elif month == "winter":
        months = [12, 1, 2]
    elif month == "spring":
        months = [3, 4, 5]
    elif month == "summer":
        months = [6, 7, 8]
    else:
        ts = datetime.datetime.strptime("2000-" + month + "-01", "%Y-%b-%d")
        # make sure it is length two for the trick below in SQL
        months = [ts.month, 999]

    df = read_sql(
        """
        SELECT day as date, max_tmpf as max, min_tmpf as min,
        max_tmpf::int - min_tmpf::int as difference
        from summary s JOIN stations t on (s.iemid = t.iemid)
        where t.id = %s and t.network = %s
        and extract(month from day) in %s
        and max_tmpf is not null and min_tmpf is not null
        ORDER by difference DESC, date DESC LIMIT 10
    """,
        pgconn,
        params=(station, ctx["network"], tuple(months)),
        parse_dates=("date",),
        index_col=None,
    )
    if df.empty:
        raise NoDataFound("No Data Found,")
    df["rank"] = df["difference"].rank(ascending=False, method="min")
    fig = plt.figure(figsize=(5.5, 4))
    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    fig.text(
        0.5,
        0.9,
        (
            "%s [%s] %s-%s\n"
            "Top 10 Local Calendar Day [%s] "
            "Temperature Differences"
        )
        % (
            ctx["_nt"].sts[station]["name"],
            station,
            ab.year,
            datetime.date.today().year,
            month.capitalize(),
        ),
        ha="center",
    )
    fig.text(
        0.1, 0.81, " #  Date         Diff   Low High", fontproperties=font0
    )
    y = 0.74
    for _, row in df.iterrows():
        fig.text(
            0.1,
            y,
            ("%2.0f  %11s   %3.0f   %3.0f  %3.0f")
            % (
                row["rank"],
                row["date"].strftime("%d %b %Y"),
                row["difference"],
                row["min"],
                row["max"],
            ),
            fontproperties=font0,
        )
        y -= 0.07
    return fig, df


if __name__ == "__main__":
    plotter(dict())
