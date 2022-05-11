"""GDD vs precip departures"""
# pylint: disable=no-member
import datetime
import calendar

from scipy import stats
import pandas as pd
from matplotlib.patches import Circle
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    today = datetime.datetime.now()
    desc["data"] = True
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IA0000",
            label="Select Station",
            network="IACLIMATE",
        ),
        dict(type="month", name="month", default=today.month, label="Month"),
        dict(
            type="year",
            name="year",
            default=today.year,
            label="Year to Highlight",
        ),
        dict(
            type="int",
            default=50,
            name="gddbase",
            label="Growing Degree Day base (F)",
        ),
        dict(
            type="int",
            default=86,
            name="gddceil",
            label="Growing Degree Day ceiling (F)",
        ),
    ]
    desc[
        "description"
    ] = """This plot compares the growing degree day vs
    precipitation
    departure for a given month and station.  The departure is expressed in
    units of standard deviation.  So a value of one would represent an one
    standard deviation departure from long term mean.  The mean and standard
    deviation is computed against the current / period of record climatology.
    The circle represents a line of equal extremity as compared with the year
    of your choosing.  The dots greater than 2.5 sigma from center are
    labelled with the year they represent.
    """
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    month = ctx["month"]
    year = ctx["year"]

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            "SELECT year, sum(precip) as total_precip, "
            "sum(gddxx(%s, %s, high::numeric,low::numeric)) as gdd "
            f"from alldata_{station[:2]} "
            "WHERE station = %s and month = %s GROUP by year",
            conn,
            params=(ctx["gddbase"], ctx["gddceil"], station, month),
            index_col="year",
        )
    if len(df.index) < 3:
        raise NoDataFound("ERROR: No Data Found")

    gstats = df.gdd.describe()
    pstats = df.total_precip.describe()

    df["precip_sigma"] = (df.total_precip - pstats["mean"]) / pstats["std"]
    df["gdd_sigma"] = (df.gdd - gstats["mean"]) / gstats["std"]
    df["distance"] = (df.precip_sigma**2 + df.gdd_sigma**2) ** 0.5

    h_slope, intercept, r_value, _, _ = stats.linregress(
        df["gdd_sigma"], df["precip_sigma"]
    )

    y1 = -4.0 * h_slope + intercept
    y2 = 4.0 * h_slope + intercept
    title = (
        f"{ctx['_sname']} :: For Month of "
        f"{calendar.month_name[month]}\n"
        f"Growing Degree Day (base={ctx['gddbase']}, ceil={ctx['gddceil']}) "
        "+ Precipitation Departure"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    ax.set_position([0.1, 0.12, 0.8, 0.78])

    ax.scatter(df["gdd_sigma"], df["precip_sigma"], label=None)
    ax.plot(
        [-4, 4],
        [y1, y2],
        label=f"Slope={h_slope:.2f} R$^2$={(r_value ** 2):.2f}",
    )
    xmax = df.gdd_sigma.abs().max() + 0.25
    ymax = df.precip_sigma.abs().max() + 0.25
    ax.set_xlim(0 - xmax, xmax)
    ax.set_ylim(0 - ymax, ymax)
    events = df.query(f"distance > 2.5 or year == {year:.0f}")
    for _year, row in events.iterrows():
        ax.text(
            row["gdd_sigma"],
            row["precip_sigma"],
            f" {_year:.0f}",
            va="center",
            color="red" if _year == year else "b",
        )
        if _year == year:
            ax.scatter(
                row["gdd_sigma"],
                row["precip_sigma"],
                color="red",
                zorder=3,
            )

    if year in df.index:
        c = Circle((0, 0), radius=df.loc[year].distance, facecolor="none")
        ax.add_patch(c)
    ax.set_xlabel(
        f"Growing Degree Day (base={ctx['gddbase']}, ceil={ctx['gddceil']}) "
        r"Departure ($\sigma$)"
    )
    ax.set_ylabel(r"Precipitation Departure ($\sigma$)")
    ax.grid(True)
    ax.legend(
        loc="lower right", bbox_to_anchor=(1.05, 0.01), ncol=2, fontsize=10
    )

    return fig, df


if __name__ == "__main__":
    plotter({})
