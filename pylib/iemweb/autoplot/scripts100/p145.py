"""
This chart presents daily timeseries of
soil temperature or moisture.  The dataset contains merged information
from the legacy Iowa State Ag Climate Network and present-day Iowa State
Soil Moisture Network.
"""

import calendar
import datetime

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.network import Table as NetworkTable  # This is needed.
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context

VARS = {
    "tsoil": "4 inch Soil Temperature",
    "vwc12": "12 inch Volumetric Water Content",
    "vwc24": "24 inch Volumetric Water Content",
    "vwc50": "50 inch Volumetric Water Content",
}
XREF = {
    "AEEI4": "A130209",
    "BOOI4": "A130209",
    "CAMI4": "A138019",
    "CHAI4": "A131559",
    "CIRI4": "A131329",
    "CNAI4": "A131299",
    "CRFI4": "A131909",
    "DONI4": "A138019",
    "FRUI4": "A135849",
    "GREI4": "A134759",
    "KNAI4": "A134309",
    "NASI4": "A135879",
    "NWLI4": "A138019",
    "OKLI4": "A134759",
    "SBEI4": "A138019",
    "WMNI4": "A135849",
    "WTPI4": "A135849",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    today = datetime.date.today()
    desc["arguments"] = [
        dict(
            type="networkselect",
            name="station",
            network="ISUSM",
            default="BOOI4",
            label="Select Station:",
        ),
        dict(
            type="select",
            options=VARS,
            default="tsoil",
            name="var",
            label="Which variable to plot:",
        ),
        dict(
            type="year",
            default=today.year,
            min=1988,
            name="year",
            label="Year to Highlight",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    nt = NetworkTable("ISUSM", only_online=False)
    oldnt = NetworkTable("ISUAG", only_online=False)
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    highlightyear = ctx["year"]
    varname = ctx["var"]
    oldstation = XREF.get(station, "A130209")
    with get_sqlalchemy_conn("isuag") as conn:
        df = pd.read_sql(
            """
        WITH legacy as (
            SELECT valid, c30 as tsoil, 'L' as dtype
            from daily where station = %s
            and c30 > -20 and c30 < 40 ORDER by valid ASC
        ), present as (
            SELECT valid, t4_c_avg_qc * 9./5. + 32. as tsoil,
            'C' as dtype, vwc12, vwc24, vwc50
            from sm_daily
            where station = %s and t4_c_avg_qc > -20 and t4_c_avg_qc < 40
            ORDER by valid ASC
        )
        SELECT valid, tsoil, dtype, null as vwc12, null as vwc24, null as vwc50
        from legacy UNION ALL select * from present
        """,
            conn,
            params=(oldstation, station),
            index_col=None,
        )
    df["valid"] = pd.to_datetime(df["valid"])
    df["doy"] = pd.to_numeric(df["valid"].dt.strftime("%j"))
    df["year"] = df["valid"].dt.year

    title = (
        f"ISU AgClimate [{station}] {nt.sts[station]['name']} "
        f"[{df['valid'].min().year}-]\n"
        f"Site {VARS[varname]} Yearly Timeseries"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)

    gdf = df[["doy", varname]].groupby("doy").describe().reset_index()
    # vertical bars for range
    ax.bar(
        gdf["doy"].values,
        gdf[(varname, "max")] - gdf[(varname, "min")],
        bottom=gdf[(varname, "min")],
        color="tan",
        label="Range",
        width=1.05,
    )
    # bands for 25-75% ptile
    ax.bar(
        gdf["doy"].values,
        gdf[(varname, "75%")] - gdf[(varname, "25%")],
        bottom=gdf[(varname, "25%")],
        color="lightgreen",
        label="25-75 Percentile",
        width=1.05,
    )
    # Mean
    ax.plot(
        gdf["doy"].values,
        gdf[(varname, "mean")].values,
        color="k",
        label="Average",
    )

    df2 = df[df["year"] == highlightyear]
    if not df2.empty:
        ax.plot(
            df2["doy"].values,
            df2[varname].values,
            color="red",
            zorder=5,
            label=f"{highlightyear}",
            lw=2.0,
        )

    ax.grid(True)
    if varname == "tsoil":
        ax.set_ylabel(r"Daily Avg Temp $^{\circ}\mathrm{F}$")
        ax.set_xlabel(
            "* pre-2014 data provided by "
            f"[{oldstation}] {oldnt.sts[oldstation]['name']}"
        )
    else:
        ax.set_ylabel("Daily Avg Volumetric Water Content [kg/kg]")
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0, 367)
    if varname != "tsoil":
        ax.set_ylim(0, 1)
    ax.axhline(32, lw=2, color="purple", zorder=4)
    ax.legend(loc="best")

    return fig, df


if __name__ == "__main__":
    plotter({})
