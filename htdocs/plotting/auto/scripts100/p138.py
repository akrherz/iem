"""monthly wind speeds"""
import calendar

from pandas.io.sql import read_sql
from metpy.units import units as munits
from metpy.calc import wind_components, wind_direction
from pyiem.plot import figure_axes
from pyiem.util import (
    drct2text,
    get_autoplot_context,
    get_dbconn,
    convert_value,
)
from pyiem.exceptions import NoDataFound

UNITS = {"mph": "miles per hour", "kt": "knots", "mps": "meters per second"}
UNITCONV = {"mph": "miles / hour", "kt": "knot", "mps": "meter / second"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This graph presents monthly average wind speed
    values along with vector-averaged average wind direction."""
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="AMW",
            network="IA_ASOS",
            label="Select Station:",
        ),
        dict(
            type="select",
            name="units",
            default="mph",
            options=UNITS,
            label="Units of Average Wind Speed",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    pgconn = get_dbconn("asos")
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx["zstation"]
    units = ctx["units"]
    df = read_sql(
        """
        select date_trunc('hour', valid at time zone 'UTC') as ts,
        avg(sknt) as sknt, max(drct) as drct from alldata
        WHERE station = %s and sknt is not null and drct is not null
        GROUP by ts
    """,
        pgconn,
        params=(station,),
        index_col=None,
    )
    if df.empty:
        raise NoDataFound("No Data Found.")
    sknt = munits("knot") * df["sknt"].values
    drct = munits("degree") * df["drct"].values
    df["u"], df["v"] = [
        x.to(munits("meter / second")).m for x in wind_components(sknt, drct)
    ]
    df["month"] = df["ts"].dt.month
    grp = df[["month", "u", "v", "sknt"]].groupby("month").mean()
    grp["u_%s" % (units,)] = convert_value(
        grp["u"].values, "meter / second", UNITCONV[units]
    )
    grp["v_%s" % (units,)] = convert_value(
        grp["v"].values, "meter / second", UNITCONV[units]
    )
    grp["sped_%s" % (units,)] = convert_value(
        grp["sknt"].values, "knot", UNITCONV[units]
    )
    grp["drct"] = wind_direction(
        munits("meter / second") * grp["u"].values,
        munits("meter / second") * grp["v"].values,
    ).m
    maxval = grp[f"sped_{units}"].max()
    (fig, ax) = figure_axes(apctx=ctx)
    ax.barh(grp.index.values, grp[f"sped_{units}"].values, align="center")
    ax.set_xlabel(f"Average Wind Speed [{UNITS[units]}]")
    ax.set_yticks(range(1, 13))
    ax.set_yticklabels(calendar.month_abbr[1:])
    ax.grid(True)
    ax.set_xlim(0, maxval * 1.2)
    for mon, row in grp.iterrows():
        ax.text(
            maxval * 1.1,
            mon,
            drct2text(row["drct"]),
            ha="center",
            va="center",
            bbox=dict(color="white"),
        )
        ax.text(
            row["sped_%s" % (units,)] * 0.98,
            mon,
            "%.1f" % (row[f"sped_{units}"],),
            ha="right",
            va="center",
            bbox=dict(color="white", boxstyle="square,pad=0.03"),
        )
    ax.set_ylim(12.5, 0.5)
    ax.set_title(
        (
            "[%s] %s [%s-%s]\nMonthly Average Wind Speed and"
            " Vector Average Direction"
        )
        % (
            station,
            ctx["_nt"].sts[station]["name"],
            df["ts"].min().year,
            df["ts"].max().year,
        )
    )

    return fig, grp


if __name__ == "__main__":
    plotter({})
