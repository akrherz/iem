"""Avg dew point at temperature."""
import datetime

from pandas.io.sql import read_sql
from metpy.units import units
import metpy.calc as mcalc
from pyiem.util import get_autoplot_context, get_dbconnstr
from pyiem.plot import figure_axes
from pyiem.exceptions import NoDataFound
from sqlalchemy import text

MDICT = dict(
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
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This plot displays the average dew point at
    a given air temperature along with the envelope between the 5th and 95th
    percentile.  The average dew point is computed by taking the
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
    """Go"""
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
        ts = datetime.datetime.strptime(f"2000-{month}-01", "%Y-%b-%d")
        # make sure it is length two for the trick below in SQL
        months = [ts.month, 999]

    df = read_sql(
        text(
            """
        SELECT tmpf::int as tmpf, dwpf, relh,
        coalesce(mslp, alti * 33.8639, 1013.25) as slp
        from alldata where station = :station
        and drct is not null and dwpf is not null and dwpf <= tmpf
        and relh is not null
        and extract(month from valid) in :months
        and report_type = 2
    """
        ),
        get_dbconnstr("asos"),
        params={
            "station": station,
            "months": tuple(months),
        },
    )
    if df.empty:
        raise NoDataFound("No Data Found.")
    # Cull any low ob count data points
    counts = df.groupby("tmpf").count()
    drops = []
    for tmpf, row in counts.iterrows():
        if row["slp"] < 6:
            drops.append(tmpf)
    # Convert sea level pressure to station pressure
    df["pressure"] = mcalc.add_height_to_pressure(
        df["slp"].values * units("millibars"),
        ctx["_nt"].sts[station]["elevation"] * units("m"),
    ).to(units("millibar"))
    # compute mixing ratio
    df["mixingratio"] = mcalc.mixing_ratio_from_relative_humidity(
        df["pressure"].values * units("millibars"),
        df["tmpf"].values * units("degF"),
        df["relh"].values * units("percent"),
    )
    # compute pressure
    df["vapor_pressure"] = mcalc.vapor_pressure(
        df["pressure"].values * units("millibars"),
        df["mixingratio"].values * units("kg/kg"),
    ).to(units("kPa"))

    qtiles = df.groupby("tmpf").quantile([0.05, 0.25, 0.5, 0.75, 0.95]).copy()
    qtiles = qtiles.reset_index()
    # Remove low counts
    qtiles = qtiles[~qtiles["tmpf"].isin(drops)]
    # compute dewpoint now
    qtiles["dwpf"] = (
        mcalc.dewpoint(qtiles["vapor_pressure"].values * units("kPa"))
        .to(units("degF"))
        .m
    )
    # compute RH again
    qtiles["relh"] = (
        mcalc.relative_humidity_from_dewpoint(
            qtiles["tmpf"].values * units("degF"),
            qtiles["dwpf"].values * units("degF"),
        )
        * 100.0
    )

    (fig, ax) = figure_axes(apctx=ctx)
    means = qtiles[qtiles["level_1"] == 0.5]
    for l0, l1, color in zip(
        [0.05, 0.25], [0.95, 0.75], ["lightgreen", "violet"]
    ):
        ax.fill_between(
            qtiles[qtiles["level_1"] == l0]["tmpf"].values,
            qtiles[qtiles["level_1"] == l0]["dwpf"].values,
            qtiles[qtiles["level_1"] == l1]["dwpf"].values,
            color=color,
            label="%.0f-%.0f %%tile" % (l0 * 100, l1 * 100),
        )
    ax.plot(
        means["tmpf"].values, means["dwpf"].values, c="blue", lw=3, label="Avg"
    )
    ax.grid(True, zorder=11)
    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    ax.set_title(
        (
            "%s [%s]\nDew Point Distribution by Air Temperature (month=%s) "
            "(%s-%s), n=%.0f\n"
            "(must have 6+ hourly observations at the given temperature)"
        )
        % (
            ctx["_nt"].sts[station]["name"],
            station,
            month.upper(),
            ab.year,
            datetime.datetime.now().year,
            len(df.index),
        ),
        size=10,
    )

    xmin, xmax = means["tmpf"].min() - 2, means["tmpf"].max() + 2
    ax.plot([xmin, xmax], [xmin, xmax], color="tan", lw=1.5)
    ax.legend(loc=4, ncol=3)
    ax.set_ylabel("Dew Point [F]")
    y2 = ax.twinx()
    y2.plot(means["tmpf"].values, means["relh"].values, color="k")
    y2.set_ylabel("Relative Humidity [%] (black line)")
    y2.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    y2.set_ylim(0, 100)
    ax.set_ylim(xmin, xmax)
    ax.set_xlim(xmin, xmax)
    ax.set_xlabel(r"Air Temperature $^\circ$F")

    return fig, means[["tmpf", "dwpf", "relh"]]


if __name__ == "__main__":
    plotter(dict(month="nov"))
