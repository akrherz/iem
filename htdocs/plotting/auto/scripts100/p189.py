"""Min temp after, max temp after, count of days"""
import datetime

from scipy.stats import linregress
from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot.use_agg import plt
from pyiem.exceptions import NoDataFound

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


def yearly_plot(ax, ctx):
    """
    Make a yearly plot of something
    """
    pgconn = get_dbconn("coop", user="nobody")

    if ctx["plot_type"] == "frost_free":
        ctx["st"] = ctx["station"][:2]
        df = read_sql(
            """
        select fall.year as yr, fall.s - spring.s as data from
          (select year, max(extract(doy from day)) as s
           from alldata_%(st)s where station = '%(station)s' and
           month < 7 and low <= 32 and year >= %(first_year)s and
           year <= %(last_year)s GROUP by year) as spring,
          (select year, min(extract(doy from day)) as s
           from alldata_%(st)s where station = '%(station)s' and
           month > 7 and low <= 32 and year >= %(first_year)s and
           year <= %(last_year)s GROUP by year) as fall
         WHERE spring.year = fall.year ORDER by fall.year ASC
        """
            % ctx,
            pgconn,
        )
    else:
        df = read_sql(
            """
        SELECT extract(year from (day %s)) as yr, %s as data
        from alldata_%s WHERE station = '%s'
         %s GROUP by yr ORDER by yr ASC
        """
            % (
                META[ctx["plot_type"]]["valid_offset"],
                META[ctx["plot_type"]]["func"],
                ctx["station"][:2],
                ctx["station"],
                META[ctx["plot_type"]]["month_bounds"],
            ),
            pgconn,
        )
    df = df[(df["yr"] >= ctx["first_year"]) & (df["yr"] <= ctx["last_year"])]
    if df.empty:
        raise NoDataFound("no data found, sorry")

    ax.plot(df["yr"].values, df["data"].values, "bo-")
    ax.set_title(
        ("%s (%s - %s)\nLocation Name: %s")
        % (
            META[ctx["plot_type"]].get("title", "TITLE"),
            ctx["first_year"],
            ctx["last_year"],
            ctx["_nt"].sts[ctx["station"]]["name"],
        )
    )
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
            "$R^2$=%.2f" % (r_value ** 2,),
            color="#CC6633",
        )

    return df


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc[
        "description"
    ] = """Create plots of yearly totals and optionally fit
    a linear trendline.  Here is a brief description of some of the
    available metrics.
    <ul>
     <li><strong>Frost Free Days</strong>: Number of days each year between
     the last spring sub 32F temperature and first fall sub 32F temperature.
     </li>
    </ul>
    """
    pdict = dict()
    for varname in META:
        pdict[varname] = META[varname]["title"]
    today = datetime.date.today()
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IA0200",
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
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())

    fig = plt.figure()
    ax = fig.add_subplot(111)
    # Transparent background for the plot area
    ax.patch.set_alpha(1.0)

    df = yearly_plot(ax, ctx)

    return fig, df


if __name__ == "__main__":
    plotter(dict())
