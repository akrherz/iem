"""
This plot displays the average dew point at
a given wind direction.  The average dew point is computed by taking the
observations of mixing ratio, averaging those, and then back computing
the dew point temperature.  With that averaged dew point temperature a
relative humidity value is computed.
"""
import datetime

import matplotlib.ticker as mticker
import metpy.calc as mcalc
import pandas as pd
from metpy.units import units
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from sqlalchemy import text

MDICT = {
    "all": "No Month/Time Limit",
    "spring": "Spring (MAM)",
    "fall": "Fall (SON)",
    "winter": "Winter (DJF)",
    "summer": "Summer (JJA)",
    "jan": "January",
    "feb": "February",
    "mar": "March",
    "apr": "April",
    "may": "May",
    "jun": "June",
    "jul": "July",
    "aug": "August",
    "sep": "September",
    "oct": "October",
    "nov": "November",
    "dec": "December",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
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
        months = list(range(1, 13))
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
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            text(
                """
            SELECT drct::int as t, dwpf, tmpf, relh,
            coalesce(mslp, alti * 33.8639, 1013.25) as slp
            from alldata where station = :station
            and drct is not null and dwpf is not null and dwpf <= tmpf
            and sknt >= 3 and drct::int % 10 = 0
            and extract(month from valid) = ANY(:months)
            and report_type = 3
        """
            ),
            conn,
            params={
                "station": station,
                "months": months,
            },
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
        df["pressure"].values * units("millibars"),
        df["tmpf"].values * units("degF"),
        df["relh"].values * units("percent"),
    )
    # compute pressure
    df["vapor_pressure"] = mcalc.vapor_pressure(
        df["pressure"].values * units("millibars"),
        df["mixingratio"].values * units("kg/kg"),
    ).to(units("kPa"))

    ptiles = (
        df[["dwpf", "t"]]
        .groupby("t")
        .quantile([0, 0.05, 0.25, 0.75, 0.95, 1])
        .reset_index()
        .rename(columns={"level_1": "ptile"})
    )
    means = df[["vapor_pressure", "t"]].groupby("t").mean().copy()
    # compute dewpoint now
    means["dwpf"] = (
        mcalc.dewpoint(means["vapor_pressure"].values * units("kPa"))
        .to(units("degF"))
        .m
    )

    (fig, ax) = figure_axes(apctx=ctx)
    ymax = ptiles[ptiles["ptile"] == 1]
    ymin = ptiles[ptiles["ptile"] == 0]
    ax.fill_between(
        ymin["t"].values,
        ymin["dwpf"].values,
        ymax["dwpf"].values,
        ec="brown",
        fc="tan",
        label="Range",
        step="mid",
    )
    ymax2 = ptiles[ptiles["ptile"] == 0.95]
    ymin2 = ptiles[ptiles["ptile"] == 0.05]
    ax.fill_between(
        ymin2["t"].values,
        ymin2["dwpf"].values,
        ymax2["dwpf"].values,
        ec="blue",
        fc="lightblue",
        label="5th - 95th",
        step="mid",
    )
    ymax2 = ptiles[ptiles["ptile"] == 0.75]
    ymin2 = ptiles[ptiles["ptile"] == 0.25]
    ax.fill_between(
        ymin2["t"].values,
        ymin2["dwpf"].values,
        ymax2["dwpf"].values,
        label="25th - 75th",
        ec="red",
        fc="pink",
        step="mid",
    )
    ax.plot(
        means.index.values,
        means["dwpf"].values,
        color="k",
        lw=3,
        label="Mean",
        drawstyle="steps-mid",
    )
    ax.legend(ncol=4)
    ax.grid(True, zorder=11)
    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    titles = [
        f"{ctx['_sname']}:: ",
        f"Average Dew Point by Wind Direction (month={month.upper()}) "
        f"({max([1973, ab.year])}-{datetime.datetime.now().year})",
        "(must have 3+ hourly obs >= 3 knots at given direction)",
    ]
    ax.set_title("\n".join(titles), size=10)

    ax.set_ylabel("Dew Point [F]")
    ax.set_ylim(ymin["dwpf"].min() - 10, ymax["dwpf"].max() + 10)
    ax.yaxis.set_major_locator(mticker.MultipleLocator(5))
    ax.set_xlim(-5, 365)
    ax.set_xticks([0, 45, 90, 135, 180, 225, 270, 315, 360])
    ax.set_xticklabels(["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"])
    ax.set_xlabel("Wind Direction")

    return fig, means


if __name__ == "__main__":
    plotter({})
