"""Min temp after, max temp after, count of days"""
import calendar
import datetime

import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn

PDICT = {
    "spring": "Min Temp after first Spring Temp above",
    "fall": "Max Temp after first Fall Temp below",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """This plot presents the yearly minimum temperature
    after the first spring temperature above a given value or the maximum
    temperature after the first fall temperature below a given value.  The
    terms spring and fall are simply representing the first half and second
    half of the year respectively.  So for example using the default plot
    options, this chart displays the maximum high temperature after the first
    fall season sub 32 low temperature and then the number of days that the
    high reached 60+ degrees until the end of each year.
    """
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
            options=PDICT,
            default="fall",
            label="Which metric to compute",
            name="var",
        ),
        dict(
            type="int",
            name="thres",
            default=32,
            label="Temperature Threshold (F) for initial date of exceedence",
        ),
        dict(
            type="int",
            name="thres2",
            default=60,
            label="Temperature Threshold (F) to count days above/below",
        ),
        dict(
            type="year",
            default=today.year,
            name="year",
            label="Year to Highlight in Chart",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    varname = ctx["var"]
    thres = ctx["thres"]
    thres2 = ctx["thres2"]
    table = f"alldata_{station[:2]}"
    if varname == "fall":
        sql = f"""
        WITH doy as (
            SELECT year, min(day) from {table} WHERE station = %s
            and low < %s and month > 6 GROUP by year),
        agg as (
            SELECT a.year, max(high) as peak_value,
            sum(case when high >= %s then 1 else 0 end) as count_days
            from {table} a, doy d
            WHERE a.station = %s and a.year = d.year and a.day > d.min
            GROUP by a.year)

        SELECT d.year, d.min as date, extract(doy from d.min) as day_of_year,
        a.peak_value, a.count_days
        from doy d JOIN agg a on (d.year = a.year) ORDER by d.year"""
        title = ("Max high after first sub %.0f low, days over %.0f") % (
            thres,
            thres2,
        )
        ctx["ax1_ylabel"] = r"Max High Temperature $^\circ$F"
        ctx["ax2_xlabel"] = "Date of First Sub %.0f Low" % (thres,)
    else:
        sql = f"""
        WITH doy as (
            SELECT year, min(day) from {table} WHERE station = %s
            and high >= %s and month < 6 GROUP by year),
        agg as (
            SELECT a.year, min(low) as peak_value,
            sum(case when low < %s then 1 else 0 end) as count_days
            from {table} a, doy d
            WHERE a.station = %s and a.year = d.year and a.day > d.min
            and a.month < 6
            GROUP by a.year)

        SELECT d.year, d.min as date, extract(doy from d.min) as day_of_year,
        a.peak_value, a.count_days
        from doy d JOIN agg a on (d.year = a.year) ORDER by d.year"""
        title = (
            f"Min low after first {thres:.0f}+ high, "
            f"days below {thres2:.0f} till 1 Jun"
        )
        ctx["ax1_ylabel"] = r"Min Low Temperature $^\circ$F"
        ctx["ax2_xlabel"] = f"Date of First {thres:.0f} High"
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql,
            conn,
            params=(station, thres, thres2, station),
            index_col="year",
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    df2 = None
    if ctx["year"] in df.index:
        df2 = df.loc[ctx["year"]]
    title = (
        f"{ctx['_sname']} :: {PDICT[varname]}\n"
        f"{title} ({df.index.min():.0f}-{df.index.max():.0f})"
    )
    fig = figure(apctx=ctx, title=title)
    (ax, ax2, ax3) = fig.subplots(3, 1)
    ax.set_position([0.1, 0.61, 0.85, 0.22])
    ax2.set_position([0.1, 0.33, 0.85, 0.22])
    ax3.set_position([0.1, 0.08, 0.85, 0.22])

    ax.bar(df.index.values, df["peak_value"], zorder=1)
    if df2 is not None:
        ax.bar(ctx["year"], df2["peak_value"], color="red", zorder=2)
    ax.grid(True)
    ax.set_xlim(df.index.min() - 1, df.index.max() + 1)
    ax.set_ylim(df["peak_value"].min() - 5, df["peak_value"].max() + 5)
    ax.set_ylabel(ctx["ax1_ylabel"])

    ax2.scatter(df["day_of_year"].values, df["peak_value"], zorder=1)
    if df2 is not None:
        ax2.scatter(
            df2["day_of_year"], df2["peak_value"], color="red", zorder=2
        )
    ax2.grid(True)
    ax2.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax2.set_xticklabels(calendar.month_abbr[1:])
    ax2.set_xlim(df["day_of_year"].min() - 10, df["day_of_year"].max() + 10)
    ax2.set_ylabel(ctx["ax1_ylabel"])
    ax2.set_xlabel(ctx["ax2_xlabel"])

    ax3.bar(df.index.values, df["count_days"], zorder=1)
    if df2 is not None:
        ax3.bar(ctx["year"], df2["count_days"], zorder=2, color="red")
    ax3.grid(True)
    tt = "above" if varname == "fall" else "below"
    tt2 = "High" if varname == "fall" else "low"
    ax3.set_ylabel(f"Days {tt} {thres2:.0f}F for {tt2}")
    ax3.set_xlim(df.index.min() - 1, df.index.max() + 1)
    ax3.axhline(df["count_days"].mean())
    ax3.text(
        df.index.max() + 1,
        df["count_days"].mean(),
        "Avg:\n%.1f" % (df["count_days"].mean(),),
    )
    val = f"{df2['count_days']:.0f}" if df2 is not None else "M"
    ax3.set_xlabel(
        f"{len(df[df['count_days'] == 0].index):.0f} years with 0 days, "
        f"{ctx['year']} = {val}"
    )

    return fig, df


if __name__ == "__main__":
    plotter({})
