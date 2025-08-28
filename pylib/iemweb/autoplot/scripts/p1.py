"""
This app allows the arbitrary comparison of months
against other months.  When the period of months wraps around a new
year, the app attempts to keep this situation straight with Dec and Jan
following each other.  The periods are combined together based on the
year of the beginning month of each period. If there is a metric you
wished to see added to this analysis, please
<a href="/info/contacts.php">let us know</a>!

<p>The five years with the most extreme values are labelled on the chart.
"""

import calendar
from datetime import date, timedelta

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from scipy import stats

from iemweb.autoplot import ARG_STATION

PDICT = {
    "total_precip": "Total Precipitation",
    "avg_temp": "Average Temperature",
    "max_high": "Maximum High Temperature",
    "avg_high": "Average High Temperature",
    "min_high": "Minimum High Temperature",
    "max_low": "Maximum Low Temperature",
    "avg_low": "Average Low Temperature",
    "min_low": "Minimum Low Temperature",
    "avg_range": "Average Daily Temperature Range",
    "days_high_aoa": "Days with High At or Above",
    "avg_rad": "Average Daily Solar Radiation",
    "cdd65": "Cooling Degree Days (base 65)",
    "hdd65": "Heating Degree Days (base 65)",
    "gdd32": "Growing Degree Days (base 32)",
    "gdd41": "Growing Degree Days (base 41)",
    "gdd46": "Growing Degree Days (base 46)",
    "gdd48": "Growing Degree Days (base 48)",
    "gdd50": "Growing Degree Days (base 50)",
    "gdd51": "Growing Degree Days (base 51)",
    "gdd52": "Growing Degree Days (base 52)",
}
PDICT2 = {
    "yes": "Truncate dataset to the start of current month",
    "no": "Do not truncate dataset",
}
# Default is to sum and then divide by number of months
PDICT_AGG_MIN = ["min_high", "min_low"]
PDICT_AGG_MAX = ["max_high", "max_low"]
PDICT_AGG_SUM = [
    "total_precip",
    "cdd65",
    "hdd65",
    "gdd32",
    "gdd41",
    "gdd46",
    "gdd48",
    "gdd50",
    "gdd51",
    "gdd52",
]
PDICT_AGG_SUM_THEN_DIVIDE = [
    "avg_temp",
    "avg_high",
    "avg_low",
    "avg_range",
    "avg_rad",
]


UNITS = {
    "total_precip": "inch",
    "avg_temp": "F",
    "max_high": "F",
    "avg_high": "F",
    "min_high": "F",
    "max_low": "F",
    "avg_low": "F",
    "min_low": "F",
    "avg_range": "F",
    "days_high_aoa": "days",
    "avg_rad": "MJ/d",
    "cdd65": "F",
    "hdd65": "F",
    "gdd32": "F",
    "gdd41": "F",
    "gdd46": "F",
    "gdd48": "F",
    "gdd50": "F",
    "gdd51": "F",
    "gdd52": "F",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    today = date.today()
    yesterday = today - timedelta(days=60)
    desc["arguments"] = [
        ARG_STATION,
        dict(
            type="int",
            name="threshold",
            default="93",
            label="Daily Temperature Threshold (when appropriate)",
        ),
        dict(
            type="month",
            name="month1",
            default=yesterday.month,
            label="Month 1 for Comparison",
        ),
        dict(
            type="int",
            name="num1",
            default=2,
            label="Number of Additional Months for Comparison 1",
        ),
        dict(
            type="select",
            options=PDICT,
            default="total_precip",
            name="var1",
            label="Comparison 1 Variable",
        ),
        dict(
            type="month",
            name="month2",
            default=yesterday.month,
            label="Month 2 for Comparison",
        ),
        dict(
            type="int",
            name="num2",
            default=2,
            label="Number of Additional Months for Comparison 2",
        ),
        dict(
            type="select",
            options=PDICT,
            default="avg_temp",
            name="var2",
            label="Comparison 2 Variable",
        ),
        {
            "type": "year",
            "default": yesterday.year,
            "name": "year",
            "label": "Year to Highlight on the Chart",
        },
        {
            "type": "select",
            "options": PDICT2,
            "default": "yes",
            "name": "truncate",
            "label": "Truncate Dataset",
        },
    ]
    return desc


def compute_months_and_offsets(start, count):
    """Figure out an array of values"""
    months = [start]
    offsets = [0]
    for i in range(1, count):
        nextval = start + i
        if nextval > 12:
            nextval -= 12
            offsets.append(1)
        else:
            offsets.append(0)
        months.append(nextval)

    return months, offsets


def combine(df: pd.DataFrame, months: list, offsets: list) -> pd.DataFrame:
    """Combine the months in the way we need to get one value per year."""

    # We create the yearly dataframe
    yearlydf = df[df["month"] == months[0]].copy().set_index("year")
    for month, offset in zip(months[1:], offsets[1:], strict=True):
        second = df[df["month"] == month].copy()
        if offset == 1:
            second["year"] = second["year"] - 1
        second = second.set_index("year")
        for col in PDICT_AGG_MAX:
            yearlydf[col] = yearlydf[col].combine(second[col], np.maximum)
        for col in PDICT_AGG_MIN:
            yearlydf[col] = yearlydf[col].combine(second[col], np.minimum)
        for col in PDICT_AGG_SUM:
            yearlydf[col] = yearlydf[col] + second[col]
        for col in PDICT_AGG_SUM_THEN_DIVIDE:
            yearlydf[col] = yearlydf[col] + second[col]
    if len(months) > 1:
        for col in PDICT_AGG_SUM_THEN_DIVIDE:
            yearlydf[col] = yearlydf[col] / float(len(months))
    return yearlydf


def plotter(ctx: dict):
    """Go"""
    today = date.today() + timedelta(days=1)
    station = ctx["station"]
    threshold = ctx["threshold"]
    month1 = ctx["month1"]
    varname1 = ctx["var1"]
    num1 = min([12, ctx["num1"]])
    month2 = ctx["month2"]
    varname2 = ctx["var2"]
    num2 = min([12, ctx["num2"]])
    months1, offsets1 = compute_months_and_offsets(month1, num1)
    months2, offsets2 = compute_months_and_offsets(month2, num2)
    # Compute the monthly totals
    endts = today.replace(day=1)
    if ctx["truncate"] == "no":
        endts = today + timedelta(days=1)
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper("""
        SELECT year, month, avg((high+low)/2.) as avg_temp,
        avg(high) as avg_high, min(high) as min_high,
        avg(low) as avg_low, max(low) as max_low,
        sum(precip) as total_precip, max(high) as max_high,
        min(low) as min_low,
        sum(case when high >= :threshold then 1 else 0 end) as days_high_aoa,
        avg(coalesce(merra_srad, hrrr_srad)) as avg_rad,
        avg(high - low) as avg_range,
        sum(cdd(high, low, 65)) as cdd65,
        sum(hdd(high, low, 65)) as hdd65,
        sum(gddxx(32, 86, high, low)) as gdd32,
        sum(gddxx(41, 86, high, low)) as gdd41,
        sum(gddxx(46, 86, high, low)) as gdd46,
        sum(gddxx(48, 86, high, low)) as gdd48,
        sum(gddxx(50, 86, high, low)) as gdd50,
        sum(gddxx(51, 86, high, low)) as gdd51,
        sum(gddxx(52, 86, high, low)) as gdd52
        from alldata WHERE station = :station and day < :sts
        GROUP by year, month ORDER by year, month
        """),
            conn,
            params={
                "threshold": threshold,
                "station": station,
                "sts": endts,
            },
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No Data Found.")

    xdf = combine(df, months1, offsets1)
    ydf = combine(df, months2, offsets2)
    if xdf.empty or ydf.empty:
        raise NoDataFound("Sorry, could not find data.")

    df = pd.DataFrame()
    df[f"{varname1}_1"] = xdf[varname1]
    df[f"{varname2}_2"] = ydf[varname2]
    df = df.dropna()
    xdata = df[f"{varname1}_1"]
    ydata = df[f"{varname2}_2"]
    if xdata.isna().all() or ydata.isna().all():
        raise NoDataFound("No Data Found.")
    title = (
        f"{df.index.min()}-{df.index.max()} {ctx['_sname']}\n"
        "Comparison of Monthly Periods, Quadrant Frequency Labelled"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    ax.scatter(
        xdata,
        ydata,
        marker="s",
        facecolor="b",
        edgecolor="b",
        label=None,
        zorder=3,
    )
    ax.grid(True)

    h_slope, intercept, r_value, _, _ = stats.linregress(
        xdata.to_numpy(), ydata.to_numpy()
    )
    y = h_slope * np.arange(xdata.min(), xdata.max()) + intercept
    ax.plot(
        np.arange(xdata.min(), xdata.max()),
        y,
        lw=2,
        color="r",
        label=f"Slope={h_slope:.2f} R$^2$={r_value**2:.2f}",
    )
    ax.legend(fontsize=10)
    xmonths = ", ".join(str(calendar.month_abbr[x]) for x in months1)
    ymonths = ", ".join(str(calendar.month_abbr[x]) for x in months2)
    t1 = "" if varname1 not in ["days_high_aoa"] else f" {threshold:.0f}"
    t2 = "" if varname2 not in ["days_high_aoa"] else f" {threshold:.0f}"
    x = xdata.mean()
    y = ydata.mean()
    df["zscore"] = ((xdata - x) ** 2 + (ydata - y) ** 2) ** 0.5
    ax.set_xlabel(
        f"{xmonths}\n{PDICT[varname1]}{t1} [{UNITS[varname1]}], Avg: {x:.1f}",
        fontsize=12,
    )
    ax.set_ylabel(
        f"{ymonths}\n{PDICT[varname2]}{t2} [{UNITS[varname2]}], Avg: {y:.1f}",
        fontsize=12,
    )

    box = ax.get_position()
    ax.set_position(
        [box.x0, box.y0 + box.height * 0.05, box.width, box.height * 0.95]
    )
    ax.axhline(y, linestyle="--", color="g")
    ax.axvline(x, linestyle="--", color="g")
    ur = ((xdata >= x) & (ydata >= y)).sum()
    val = ur / float(len(df.index)) * 100.0
    ax.text(
        0.95,
        0.75,
        f"{ur} ({val:.1f}%)",
        color="tan",
        fontsize=24,
        transform=ax.transAxes,
        ha="right",
        zorder=2,
    )
    lr = ((xdata >= x) & (ydata < y)).sum()
    val = lr / float(len(df.index)) * 100.0
    ax.text(
        0.95,
        0.25,
        f"{lr} ({val:.1f}%)",
        color="tan",
        fontsize=24,
        transform=ax.transAxes,
        ha="right",
        zorder=2,
    )
    ll = ((xdata < x) & (ydata < y)).sum()
    val = ll / float(len(df.index)) * 100.0
    ax.text(
        0.05,
        0.25,
        f"{ll} ({val:.1f}%)",
        color="tan",
        fontsize=24,
        transform=ax.transAxes,
        ha="left",
        zorder=2,
    )
    ul = ((xdata < x) & (ydata >= y)).sum()
    val = ul / float(len(df.index)) * 100.0
    ax.text(
        0.05,
        0.75,
        f"{ul} ({val:.1f}%)",
        color="tan",
        fontsize=24,
        transform=ax.transAxes,
        ha="left",
        zorder=2,
    )
    for yr in df.sort_values("zscore", ascending=False).head(5).index:
        ax.text(xdata[yr], ydata[yr], f" {yr}")
    if ctx["year"] in df.index:
        ax.text(xdata[ctx["year"]], ydata[ctx["year"]], f" {ctx['year']}")
        ax.scatter(
            xdata[ctx["year"]],
            ydata[ctx["year"]],
            marker="s",
            facecolor="r",
            edgecolor="r",
            label=None,
            zorder=4,
        )
    return fig, df
