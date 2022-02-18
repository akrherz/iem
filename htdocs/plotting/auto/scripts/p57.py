"""monthly temp record / climatology."""
import datetime
import calendar

import pandas as pd
import numpy as np
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound

PDICT = {
    "avg_temp": "Average Daily Temperature",
    "avg_high_temp": "Average High Temperature",
    "avg_low_temp": "Average Low Temperature",
    "rain_days": "Days with Measurable Precipitation",
    "total_precip": "Total Precipitation",
}
PDICT2 = {"min": "Minimum", "mean": "Climatology", "max": "Maximum"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """This plot displays the monthly records or climatology for
    a station of your choice.  The current month for the current day is not
    considered for the analysis, except for total precipitation."""
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            network="IACLIMATE",
            label="Select Station:",
        ),
        dict(
            type="select",
            options=PDICT,
            name="varname",
            default="avg_temp",
            label="Variable to Plot",
        ),
        dict(
            type="select",
            options=PDICT2,
            name="agg",
            default="max",
            label="Aggregate Option",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx["station"]
    varname = ctx["varname"]
    agg = ctx["agg"]

    lastday = datetime.date.today()
    if varname == "total_precip" and agg == "max":
        lastday += datetime.timedelta(days=1)
    else:
        lastday = lastday.replace(day=1)
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            f"""SELECT year, month, avg((high+low)/2.) as avg_temp,
        avg(high) as avg_high_temp, avg(low) as avg_low_temp,
        sum(precip) as total_precip,
        sum(case when precip > 0.005 then 1 else 0 end) as rain_days
        from alldata_{station[:2]} where station = %s and day < %s
        GROUP by year, month
        """,
            conn,
            params=(station, lastday),
        )
    if df.empty:
        raise NoDataFound("No Data Found.")

    resdf = pd.DataFrame(
        dict(monthname=pd.Series(calendar.month_abbr[1:], index=range(1, 13))),
        index=pd.Series(range(1, 13), name="month"),
    )
    for _varname in PDICT:
        for _agg in [min, max]:
            df2 = df[[_varname, "month", "year"]]
            df2 = df2[
                df[_varname] == df.groupby("month")[_varname].transform(_agg)
            ].copy()
            df2 = df2.rename(
                columns={
                    "year": f"{_agg.__name__}_{_varname}_year",
                    _varname: f"{_agg.__name__}_{_varname}",
                },
            ).set_index("month")
            resdf = resdf.join(df2)
        # Special for mean operation
        df2 = (
            df[[_varname, "month"]]
            .groupby("month")
            .mean()
            .rename(columns={_varname: f"mean_{_varname}"})
        )
        resdf = resdf.join(df2)

    # The above can end up with duplicates
    resdf = resdf.groupby(level=0)
    resdf = resdf.last()
    col = f"{agg}_{varname}"
    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown Station Metadata.")
    title = (
        f"[{station}] {ctx['_nt'].sts[station]['name']}\n"
        f"{PDICT2[agg]} {PDICT[varname]} [{ab.year}-{lastday.year}]"
    )
    if col == "mean_total_precip":
        title += (
            f" {resdf['mean_total_precip'].sum():.2f} inches over "
            f"{resdf['mean_rain_days'].sum():.0f} days"
        )
    (fig, ax) = figure_axes(title=title, apctx=ctx)

    offset = 0.2 if col == "mean_total_precip" else 0
    ax.bar(
        np.arange(1, 13) - offset,
        resdf[col],
        fc="pink",
        align="center",
        width=0.4 if col == "mean_total_precip" else 0.8,
    )
    for month, row in resdf.iterrows():
        yearcol = f"{col}_year"
        if np.isnan(row[col]):
            continue
        yearlabel = "" if yearcol not in resdf.columns else f"\n{row[yearcol]}"
        ax.text(
            month - offset,
            row[col],
            f"{row[col]:.2f}{yearlabel}",
            ha="center",
            va="bottom",
            bbox={"color": "white", "boxstyle": "square,pad=0"},
        )
    if col == "mean_total_precip":
        ax2 = ax.twinx()
        bars = ax2.bar(
            np.arange(1, 13) + 0.2, resdf["mean_rain_days"], width=0.4
        )
        for mybar in bars:
            ax2.text(
                mybar.get_x() + 0.2,
                mybar.get_height() + 0.2,
                f"{mybar.get_height():.1f}",
                ha="center",
                bbox={"color": "white", "boxstyle": "square,pad=0.1"},
            )
        ax2.set_ylabel("Measurable Precip Days")
    ax.set_xlim(0.5, 12.5)
    ax.set_ylim(top=resdf[col].max() * 1.2)
    ylabel = r"Temperature $^\circ$F"
    if varname in ["total_precip"]:
        ylabel = "Precipitation [inch]"
    ax.set_ylabel(ylabel)
    ax.grid(True)
    ax.set_xticks(np.arange(1, 13))
    ax.set_xticklabels(calendar.month_abbr[1:])

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width, box.height * 0.95])

    return fig, resdf


if __name__ == "__main__":
    plotter({"agg": "mean", "varname": "total_precip"})
