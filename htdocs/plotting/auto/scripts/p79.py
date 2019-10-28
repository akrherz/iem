"""Average dew point by wind direction."""
import datetime
from collections import OrderedDict

from pandas.io.sql import read_sql
from metpy.units import units
import metpy.calc as mcalc
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
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
    ] = """This plot displays the average dew point at
    a given wind direction.  The average dew point is computed by taking the
    observations of mixing ratio, averaging those, and then back computing
    the dew point temperature.  With that averaged dew point temperature a
    relative humidity value is computed."""
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="DSM",
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
    pgconn = get_dbconn("asos")
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
        SELECT drct::int as t, dwpf, tmpf, relh,
        coalesce(mslp, alti * 33.8639, 1013.25) as slp
        from alldata where station = %s
        and drct is not null and dwpf is not null and dwpf <= tmpf
        and sknt > 3 and drct::int %% 10 = 0
        and extract(month from valid) in %s
        and report_type = 2
    """,
        pgconn,
        params=(station, tuple(months)),
    )
    if df.empty:
        raise NoDataFound("No Data Found.")
    # Convert sea level pressure to station pressure
    df["pressure"] = mcalc.add_height_to_pressure(
        df["slp"].values * units("millibars"),
        ctx["_nt"].sts[station]["elevation"] * units("m"),
    ).to(units("millibar"))
    # compute mixing ratio
    df["mixingratio"] = mcalc.mixing_ratio_from_relative_humidity(
        df["relh"].values * units("percent"),
        df["tmpf"].values * units("degF"),
        df["pressure"].values * units("millibars"),
    )
    # compute pressure
    df["vapor_pressure"] = mcalc.vapor_pressure(
        df["pressure"].values * units("millibars"),
        df["mixingratio"].values * units("kg/kg"),
    ).to(units("kPa"))

    means = df.groupby("t").mean().copy()
    # compute dewpoint now
    means["dwpf"] = (
        mcalc.dewpoint(means["vapor_pressure"].values * units("kPa"))
        .to(units("degF"))
        .m
    )

    (fig, ax) = plt.subplots(1, 1)
    ax.bar(
        means.index.values,
        means["dwpf"].values,
        ec="green",
        fc="green",
        width=10,
        align="center",
    )
    ax.grid(True, zorder=11)
    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    ax.set_title(
        (
            "%s [%s]\nAverage Dew Point by Wind Direction (month=%s) "
            "(%s-%s)\n"
            "(must have 3+ hourly obs > 3 knots at given direction)"
        )
        % (
            ctx["_nt"].sts[station]["name"],
            station,
            month.upper(),
            max([1973, ab.year]),
            datetime.datetime.now().year,
        ),
        size=10,
    )

    ax.set_ylabel("Dew Point [F]")
    ax.set_ylim(means["dwpf"].min() - 5, means["dwpf"].max() + 5)
    ax.set_xlim(-5, 365)
    ax.set_xticks([0, 45, 90, 135, 180, 225, 270, 315, 360])
    ax.set_xticklabels(["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"])
    ax.set_xlabel("Wind Direction")

    return fig, means["dwpf"]


if __name__ == "__main__":
    plotter(dict())
