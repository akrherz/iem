"""Period differences"""

import pandas as pd
from pyiem.plot import MapPlot, centered_bins, get_cmap
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.reference import SECTORS_NAME

PDICT = {"state": "State Level Maps (select state)"}
PDICT.update(SECTORS_NAME)
PDICT2 = {
    "both": "Show both contour and values",
    "values": "Show just the values",
    "contour": "Show just the contour",
}
PDICT3 = {
    "season": "Number of Days in Growing Season",
    "spring": "Date of Last Spring Freeze",
    "fall": "Date of First Fall Freeze",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """This map produces an analysis of change in
    the number of days for the growing season."""
    desc["arguments"] = [
        dict(
            type="select",
            name="sector",
            default="state",
            options=PDICT,
            label="Select Map Region",
        ),
        dict(
            type="state",
            name="state",
            default="IA",
            label="Select State to Plot (when appropriate)",
        ),
        dict(
            type="select",
            name="opt",
            options=PDICT2,
            default="both",
            label="Map Plot/Contour View Option",
        ),
        dict(
            type="select",
            name="var",
            options=PDICT3,
            default="season",
            label="Variable to Plot",
        ),
        dict(
            type="year",
            name="p1syear",
            default=1951,
            label="Start Year (inclusive) of Period One:",
        ),
        dict(
            type="year",
            name="p1eyear",
            default=1980,
            label="End Year (inclusive) of Period One:",
        ),
        dict(
            type="year",
            name="p2syear",
            default=1981,
            label="Start Year (inclusive) of Period Two:",
        ),
        dict(
            type="year",
            name="p2eyear",
            default=2010,
            label="End Year (inclusive) of Period Two:",
        ),
        dict(type="cmap", name="cmap", default="seismic", label="Color Ramp:"),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    state = ctx["state"][:2]
    sector = ctx["sector"]
    opt = ctx["opt"]
    p1syear = ctx["p1syear"]
    p1eyear = ctx["p1eyear"]
    p2syear = ctx["p2syear"]
    p2eyear = ctx["p2eyear"]
    varname = ctx["var"]

    table = "alldata"
    if sector == "state":
        table = f"alldata_{state}"
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            f"""
        WITH season1 as (
            SELECT station, year,
            min(case when month > 7 and low < 32 then
                extract(doy from day) else 366 end) as first_freeze,
            max(case when month < 7 and low < 32 then
                extract(doy from day) else 0 end) as last_freeze
            from {table} WHERE
            year >= %s and year <= %s GROUP by station, year),
        season2 as (
            SELECT station, year,
            min(case when month > 7 and low < 32 then
                extract(doy from day) else 366 end) as first_freeze,
            max(case when month < 7 and low < 32 then
                extract(doy from day) else 0 end) as last_freeze
            from {table} WHERE
            year >= %s and year <= %s GROUP by station, year),
        agg as (
            SELECT p1.station, avg(p1.first_freeze) as p1_first_fall,
            avg(p1.last_freeze) as p1_last_spring,
            avg(p2.first_freeze) as p2_first_fall,
            avg(p2.last_freeze) as p2_last_spring
            from season1 as p1 JOIN season2 as p2 on (p1.station = p2.station)
            GROUP by p1.station)

        SELECT station, ST_X(geom) as lon, ST_Y(geom) as lat,
        d.* from agg d JOIN stations t ON (d.station = t.id)
        WHERE t.network ~* 'CLIMATE'
        and substr(station, 3, 1) != 'C' and substr(station, 3, 4) != '0000'
        """,
            conn,
            params=[p1syear, p1eyear, p2syear, p2eyear],
            index_col="station",
        )
    if df.empty:
        raise NoDataFound("No Data Found")
    df["p1_season"] = df["p1_first_fall"] - df["p1_last_spring"]
    df["p2_season"] = df["p2_first_fall"] - df["p2_last_spring"]
    df["season_delta"] = df["p2_season"] - df["p1_season"]
    df["spring_delta"] = df["p2_last_spring"] - df["p1_last_spring"]
    df["fall_delta"] = df["p2_first_fall"] - df["p1_first_fall"]
    # Reindex so that most extreme values are first
    df = df.reindex(
        df[varname + "_delta"].abs().sort_values(ascending=False).index
    )

    title = PDICT3[varname]
    mp = MapPlot(
        apctx=ctx,
        sector=sector,
        state=state,
        axisbg="white",
        title=(
            f"{p2syear:.0f}-{p2eyear:.0f} minus {p1syear:.0f}-"
            f"{p1eyear:.0f} {title} Difference"
        ),
        subtitle="based on IEM Archives",
        titlefontsize=14,
    )
    # Create 9 levels centered on zero
    abval = df[varname + "_delta"].abs().max()
    levels = centered_bins(abval)
    if opt in ["both", "contour"]:
        mp.contourf(
            df["lon"].values,
            df["lat"].values,
            df[varname + "_delta"].values,
            levels,
            cmap=get_cmap(ctx["cmap"]),
            units="days",
        )
    if sector == "state":
        mp.drawcounties()
    if opt in ["both", "values"]:
        mp.plot_values(
            df["lon"].values,
            df["lat"].values,
            df[f"{varname}_delta"].values,
            fmt="%.1f",
            labelbuffer=5,
        )

    return mp.fig, df


if __name__ == "__main__":
    plotter(dict(over="annual"))
