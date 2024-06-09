"""
Create plots of yearly totals and optionally fit
a linear trendline.  Here is a brief description of some of the
available metrics.
<ul>
    <li><strong>Frost Free Days</strong>: Number of days each year between
    the last spring sub 32F temperature and first fall sub 32F temperature.
    </li>
</ul>

<p>If you plot the DJF period, the year shown is the year of the
December within the three year period.
"""

import datetime

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context
from scipy.stats import linregress

BOOLS = {
    "yes": "Yes, fit linear regression",
    "no": "No, do not plot regression",
}
META = {
    "annual_sum_precip": {
        "title": "Annual Precipitation (rain + melted snow)",
        "ylabel": "Precipitation [inches]",
        "xlabel": "Year",
        "func": "sum(precip)",
        "month_bounds": "",
        "valid_offset": "",
    },
    "annual_avg_temp": {
        "title": "Annual Average Temperature",
        "ylabel": "Temperature [F]",
        "xlabel": "Year",
        "func": "avg((high+low)/2.)",
        "month_bounds": "",
        "valid_offset": "",
    },
    "annual_avg_high": {
        "title": "Annual Average High Temperature",
        "ylabel": "Temperature [F]",
        "xlabel": "Year",
        "func": "avg(high)",
        "month_bounds": "",
        "valid_offset": "",
    },
    "annual_avg_low": {
        "title": "Annual Average Low Temperature",
        "ylabel": "Temperature [F]",
        "xlabel": "Year",
        "func": "avg(low)",
        "month_bounds": "",
        "valid_offset": "",
    },
    "winter_avg_temp": {
        "title": "Winter [DJF] Average Temperature",
        "ylabel": "Temperature [F]",
        "xlabel": "Year",
        "func": "avg((high+low)/2.)",
        "month_bounds": "and month in (12,1,2)",
        "valid_offset": "- '2 month'::interval ",
    },
    "winter_avg_low": {
        "title": "Winter [DJF] Average Low Temperature",
        "ylabel": "Temperature [F]",
        "xlabel": "Year",
        "func": "avg(low)",
        "month_bounds": "and month in (12,1,2)",
        "valid_offset": "- '2 month'::interval ",
    },
    "winter_avg_high": {
        "title": "Winter [DJF] Average High Temperature",
        "ylabel": "Temperature [F]",
        "xlabel": "Year",
        "func": "avg(high)",
        "month_bounds": "and month in (12,1,2)",
        "valid_offset": "- '2 month'::interval ",
    },
    "summer_avg_temp": {
        "title": "Summer [JJA] Average Temperature",
        "ylabel": "Temperature [F]",
        "xlabel": "Year",
        "func": "avg((high+low)/2.)",
        "month_bounds": "and month in (6,7,8)",
        "valid_offset": " ",
    },
    "summer_avg_high": {
        "title": "Summer [JJA] Average High Temperature",
        "ylabel": "Temperature [F]",
        "xlabel": "Year",
        "func": "avg(high)",
        "month_bounds": "and month in (6,7,8)",
        "valid_offset": " ",
    },
    "summer_avg_low": {
        "title": "Summer [JJA] Average Low Temperature",
        "ylabel": "Temperature [F]",
        "xlabel": "Year",
        "func": "avg(low)",
        "month_bounds": "and month in (6,7,8)",
        "valid_offset": " ",
    },
    "summer_avg_era5land_soilm1m_avg": {
        "title": "Summer [JJA] Average ERA5-Land 0-1m Soil Moisture",
        "ylabel": "Soil Moisture [m3/m3]",
        "xlabel": "Year",
        "func": "avg(era5land_soilm1m_avg)",
        "month_bounds": "and month in (6,7,8)",
        "valid_offset": " ",
    },
    "spring_avg_temp": {
        "title": "Spring [MAM] Average Temperature",
        "ylabel": "Temperature [F]",
        "xlabel": "Year",
        "func": "avg((high+low)/2.)",
        "month_bounds": "and month in (3,4,5)",
        "valid_offset": " ",
    },
    "fall_avg_temp": {
        "title": "Fall [SON] Average Temperature",
        "ylabel": "Temperature [F]",
        "xlabel": "Year",
        "func": "avg((high+low)/2.)",
        "month_bounds": "and month in (9,10,11)",
        "valid_offset": " ",
    },
    "frost_free": {
        "title": "Frost Free Days",
        "ylabel": "Days",
        "xlabel": "Year",
        "month_bounds": "",
        "func": "",
        "valid_offset": "",
    },
    "gdd50": {
        "title": "Growing Degree Days (1 May - 1 Oct) (base=50)",
        "ylabel": "GDD Units [F]",
        "xlabel": "Year",
        "func": "sum(gddxx(50, 86, high, low))",
        "month_bounds": "and month in (5,6,7,8,9)",
        "valid_offset": "",
    },
    "hdd65": {
        "title": "Heating Degree Days (1 Oct - 1 May) (base=65)",
        "ylabel": "HDD Units [F]",
        "xlabel": "Year",
        "func": "sum(hdd65(high,low))",
        "month_bounds": "and month in (10,11,12,1,2,3,4)",
        "valid_offset": " - '6 months'::interval ",
    },
}


def yearly_plot(ctx):
    """
    Make a yearly plot of something
    """
    st = ctx["station"][:2]

    if ctx["plot_type"] == "frost_free":
        with get_sqlalchemy_conn("coop") as conn:
            df = pd.read_sql(
                f"""
            select fall.year as yr, fall.s - spring.s as data from
            (select year, max(extract(doy from day)) as s
            from alldata_{st} where station = %s and
            month < 7 and low <= 32 and year >= %s and
            year <= %s GROUP by year) as spring,
            (select year, min(extract(doy from day)) as s
            from alldata_{st} where station = %s and
            month > 7 and low <= 32 and year >= %s and
            year <= %s GROUP by year) as fall
            WHERE spring.year = fall.year ORDER by fall.year ASC
            """,
                conn,
                params=(
                    ctx["station"],
                    ctx["first_year"],
                    ctx["last_year"],
                    ctx["station"],
                    ctx["first_year"],
                    ctx["last_year"],
                ),
            )
    else:
        off = META[ctx["plot_type"]]["valid_offset"]
        func = META[ctx["plot_type"]]["func"]
        bnds = META[ctx["plot_type"]]["month_bounds"]
        with get_sqlalchemy_conn("coop") as conn:
            df = pd.read_sql(
                f"SELECT extract(year from (day {off})) as yr, "
                f"{func} as data "
                f"from alldata_{st} WHERE station = %s {bnds} "
                "GROUP by yr ORDER by yr ASC",
                conn,
                params=(ctx["station"],),
            )
    df = df[(df["yr"] >= ctx["first_year"]) & (df["yr"] <= ctx["last_year"])]
    if df.empty:
        raise NoDataFound("no data found, sorry")

    title = (
        f"{ctx['_sname']}\n"
        f"{META[ctx['plot_type']].get('title', 'TITLE')} "
        f"({df['yr'].min():.0f} - {df['yr'].max():.0f})\n"
    )
    fig, ax = figure_axes(title=title, apctx=ctx)
    ax.plot(df["yr"].values, df["data"].values, "bo-")
    ax.set_xlabel(META[ctx["plot_type"]].get("xlabel", "XLABEL"))
    ax.set_ylabel(META[ctx["plot_type"]].get("ylabel", "YLABEL"))
    ax.set_xlim(ctx["first_year"] - 1, ctx["last_year"] + 1)
    miny = df["data"].min()
    maxy = df["data"].max()
    ax.set_ylim(miny - ((maxy - miny) / 10.0), maxy + ((maxy - miny) / 10.0))
    ax.grid(True)

    if ctx["linregress"] == "yes":
        (slope, intercept, r_value, _p_value, _std_err) = linregress(
            df["yr"].values, df["data"].values
        )
        ax.plot(
            df["yr"].values,
            slope * df["yr"].values + intercept,
            color="#CC6633",
        )
        ax.text(
            ctx["first_year"],
            maxy,
            f"$R^2$={(r_value ** 2):.2f}",
            color="#CC6633",
            bbox=dict(facecolor="white"),
        )

    return fig, df


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    pdict = {}
    for varname, item in META.items():
        pdict[varname] = item["title"]
    today = datetime.date.today()
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATAME",
            label="Select Station:",
            network="IACLIMATE",
        ),
        dict(
            type="select",
            options=pdict,
            default="frost_free",
            label="Which metric to compute",
            name="plot_type",
        ),
        dict(
            type="year",
            default=1951,
            name="first_year",
            label="First Year to Plot",
        ),
        dict(
            type="year",
            default=(today.year - 1),
            name="last_year",
            label="Last Year to Plot",
        ),
        dict(
            type="select",
            options=BOOLS,
            name="linregress",
            default="no",
            label="Plot Regression?",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())

    fig, df = yearly_plot(ctx)

    return fig, df
