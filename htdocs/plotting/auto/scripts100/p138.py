"""
This graph presents monthly average wind speed
values along with vector-averaged average wind direction.
"""
import calendar

import pandas as pd
from metpy.calc import wind_components, wind_direction
from metpy.units import units as munits
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import (
    convert_value,
    drct2text,
    get_autoplot_context,
    get_sqlalchemy_conn,
)

UNITS = {"mph": "miles per hour", "kt": "knots", "mps": "meters per second"}
UNITCONV = {"mph": "miles / hour", "kt": "knot", "mps": "meter / second"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
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
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx["zstation"]
    units = ctx["units"]
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            """
            select date_trunc('hour', valid at time zone 'UTC') as ts,
            avg(sknt) as sknt, max(drct) as drct from alldata
            WHERE station = %s and sknt is not null and drct is not null
            GROUP by ts
        """,
            conn,
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
    grp[f"u_{units}"] = convert_value(
        grp["u"].values, "meter / second", UNITCONV[units]
    )
    grp[f"v_{units}"] = convert_value(
        grp["v"].values, "meter / second", UNITCONV[units]
    )
    grp[f"sped_{units}"] = convert_value(
        grp["sknt"].values, "knot", UNITCONV[units]
    )
    grp["drct"] = wind_direction(
        munits("meter / second") * grp["u"].values,
        munits("meter / second") * grp["v"].values,
    ).m
    maxval = grp[f"sped_{units}"].max()
    title = (
        f"{ctx['_sname']} [{df['ts'].min().year}-{df['ts'].max().year}]\n"
        "Monthly Average Wind Speed and Vector Average Direction"
    )
    (fig, ax) = figure_axes(apctx=ctx, title=title)
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
            row[f"sped_{units}"] * 0.98,
            mon,
            "%.1f" % (row[f"sped_{units}"],),
            ha="right",
            va="center",
            bbox=dict(color="white", boxstyle="square,pad=0.03"),
        )
    ax.set_ylim(12.5, 0.5)

    return fig, grp


if __name__ == "__main__":
    plotter({})
