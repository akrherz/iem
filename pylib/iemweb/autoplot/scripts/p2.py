"""
This plot compares monthly summaries for a given month of the year and given
station.  You can pick a year to highlight on the chart and it will also
highlight any years with a combined sigma distance of 2.5.
"""

import calendar
from datetime import datetime

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from scipy import stats

PDICT = {
    "total_precip": "Precipitation (inch)",
    "total_snow": "Snowfall (inch)",
    "gdd": "Growing Degree Days",
    "sdd86": "Stress Degree Days (base=86°F)",
    "avg_high": "Average High Temperature (°F)",
    "avg_low": "Average Low Temperature (°F)",
    "avg_temp": "Average Temperature (°F)",
    "avg_merra_srad": "Average Solar Radiation MERRA (MJ)",
    "avg_era5land_soilt4": "Average Soil Temp ERA5-Land (°C)",
}
REQ_VAR = {
    "total_precip": "precip",
    "total_snow": "snow",
    "gdd": "high",
    "sdd86": "high",
    "avg_high": "high",
    "avg_low": "low",
    "avg_temp": "high",
    "avg_merra_srad": "merra_srad",
    "avg_era5land_soilt4": "era5land_soilt4_avg",
}
PDICT2 = {
    "value": "Value",
    "departure": "Departure from Mean",
    "sigma": "Standard Deviations from the Mean",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    today = datetime.now()
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
            label="Growing Degree Day base (°F)",
        ),
        dict(
            type="int",
            default=86,
            name="gddceil",
            label="Growing Degree Day ceiling (°F)",
        ),
        {
            "type": "select",
            "name": "xvar",
            "label": "X-axis Variable",
            "options": PDICT,
            "default": "gdd",
        },
        {
            "type": "select",
            "name": "xagg",
            "label": "X-axis Statistic",
            "options": PDICT2,
            "default": "sigma",
        },
        {
            "type": "select",
            "name": "yvar",
            "label": "Y-axis Variable",
            "options": PDICT,
            "default": "total_precip",
        },
        {
            "type": "select",
            "name": "yagg",
            "label": "Y-axis Statistic",
            "options": PDICT2,
            "default": "sigma",
        },
        {
            "type": "int",
            "min": 1,
            "max": 31,
            "default": 25,
            "name": "quorum",
            "label": "Days with data for a month to be included in plot.",
        },
    ]
    return desc


def plotter(ctx: dict):
    """Go"""
    station = ctx["station"]
    month = ctx["month"]
    year = ctx["year"]

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper(
                """
    SELECT year, sum(precip) as total_precip, sum(snow) as total_snow,
    sum(gddxx(:gddbase, :gddceil, high::numeric,low::numeric)) as gdd,
    avg(high) as avg_high, avg(low) as avg_low,
    avg(era5land_soilt4_avg) as avg_era5land_soilt4,
    avg(merra_srad) as avg_merra_srad,
    sum(sdd86(high, low)) as sdd86, avg((high+low)/2.) as avg_temp,
    count(*) as days
    from alldata WHERE station = :station and month = :month
    and {reqvar1} is not null and {reqvar2} is not null GROUP by year
            """,
                reqvar1=REQ_VAR[ctx["xvar"]],
                reqvar2=REQ_VAR[ctx["yvar"]],
            ),
            conn,
            params={
                "gddbase": ctx["gddbase"],
                "gddceil": ctx["gddceil"],
                "station": station,
                "month": month,
            },
            index_col="year",
        )
    # Require a quorum
    df = df[df["days"] >= ctx["quorum"]]
    if len(df.index) < 3:
        raise NoDataFound("ERROR: No Data Found")

    # Run statistics for each of the variables
    for varname in PDICT:
        vstats = df[varname].describe()
        df[f"{varname}_sigma"] = (df[varname] - vstats["mean"]) / vstats["std"]
        df[f"{varname}_departure"] = df[varname] - vstats["mean"]

    xvar = (
        ctx["xvar"]
        if ctx["xagg"] == "value"
        else f"{ctx['xvar']}_{ctx['xagg']}"
    )
    yvar = (
        ctx["yvar"]
        if ctx["yagg"] == "value"
        else f"{ctx['yvar']}_{ctx['yagg']}"
    )

    h_slope, intercept, r_value, _, _ = stats.linregress(
        df[xvar].to_numpy(), df[yvar].to_numpy()
    )

    y1 = df[xvar].min() * h_slope + intercept
    y2 = df[xvar].max() * h_slope + intercept
    title = f"{ctx['_sname']} :: For Month of {calendar.month_name[month]}"
    subtitle = (
        f"X: {PDICT[ctx['xvar']]} ({PDICT2[ctx['xagg']]})"
        f" Y: {PDICT[ctx['yvar']]} ({PDICT2[ctx['yagg']]})"
    )
    (fig, ax) = figure_axes(title=title, subtitle=subtitle, apctx=ctx)
    ax.set_position([0.1, 0.12, 0.8, 0.78])

    ax.scatter(df[xvar], df[yvar], label=None)
    ax.plot(
        [df[xvar].min(), df[xvar].max()],
        [y1, y2],
        label=f"Slope={h_slope:.2f} R$^2$={(r_value**2):.2f}",
    )

    # Find interesting values to label
    df["distance"] = (
        df[f"{ctx['xvar'].replace('_sigma', '')}_sigma"] ** 2
        + df[f"{ctx['yvar'].replace('_sigma', '')}_sigma"] ** 2
    ) ** 0.5
    events = df.query(f"distance > 2.5 or year == {year:.0f}")
    for _year, row in events.iterrows():
        ax.annotate(
            f" {_year:.0f}",
            xy=(row[xvar], row[yvar]),
            va="center",
            color="red" if _year == year else "b",
        )
        if _year == year:
            ax.scatter(
                row[xvar],
                row[yvar],
                color="red",
                zorder=3,
            )

    # Ensure the axes are balanced for non-value plots
    if ctx["xagg"] != "value":
        xmax = df[xvar].abs().max() + 0.25
        ax.set_xlim(0 - xmax, xmax)
    if ctx["yagg"] != "value":
        ymax = df[yvar].abs().max() + 0.25
        ax.set_ylim(0 - ymax, ymax)

    ax.set_xlabel(f"{PDICT[ctx['xvar']]} ({PDICT2[ctx['xagg']]})")
    ax.set_ylabel(f"{PDICT[ctx['yvar']]} ({PDICT2[ctx['yagg']]})")
    ax.grid(True)
    ax.legend(loc="best", ncol=2, fontsize=10)

    return fig, df.drop(columns=["distance"])
