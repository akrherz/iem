"""
This plot presents the yearly first or last date
of a given high or low temperature along with the number of days that
year above/below the threshold along with the cumulative distribution
function for the first date!  When you select a low temperature option,
the season displayed in the chart and available download spreadsheet
represents the start year of the winter season.  Rewording, the year 2016
would represent the period of 1 July 2016 to 30 Jun 2017.
"""

from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure

from iemweb.autoplot import ARG_STATION

PDICT = {
    "last_high_above": "Last Date At or Above (High Temperature)",
    "last_high_below": "Last Date Below (High Temperature)",
    "first_high_above": "First Date At or Above (High Temperature)",
    "first_high_below": "First Date Below (High Temperature)",
    "first_low_above": "First Date At or Above (Low Temperature)",
    "first_low_below": "First Date Below (Low Temperature)",
    "last_low_above": "Last Date At or Above(Low Temperature)",
    "last_low_below": "Last Date Below (Low Temperature)",
}
PDICT2 = {
    "calendar": "Compute over Calendar Year",
    "winter": "Compute over Winter Season",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    thisyear = date.today().year
    desc["arguments"] = [
        ARG_STATION,
        dict(
            type="int",
            name="threshold",
            default="90",
            label="Enter Threshold:",
        ),
        dict(
            type="select",
            name="which",
            default="last_high_above",
            label="Date Option:",
            options=PDICT,
        ),
        dict(
            type="select",
            name="season",
            default="calendar",
            label="How to split the year:",
            options=PDICT2,
        ),
        dict(
            type="year",
            name="year",
            default=thisyear,
            max=(thisyear + 1),
            label="Year to Highlight in Chart:",
        ),
    ]
    return desc


def plotter(ctx: dict):
    """Go"""
    station = ctx["station"]
    threshold = ctx["threshold"]
    season = ctx["season"]
    (extrenum, varname, direction) = ctx["which"].split("_")
    year = ctx["year"]

    op = ">=" if direction == "above" else "<"
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper(
                """
            with data as (
                SELECT extract(year from day + ':months months'::interval)
                    as season,
                high, low, day from alldata WHERE station = :station
                and day >= '1893-01-01'),
            agg1 as (
                SELECT season - :soff as season,
                count(*) as obs,
                min(case when {varname} {op} :thresh then day else null end)
                    as nday,
                max(case when {varname} {op} :thresh then day else null end)
                    as xday,
                sum(case when {varname} {op} :thresh then 1 else 0 end)
                    as count
                from data GROUP by season)
        SELECT season::int, count, obs, nday,
        extract(doy from nday) as nday_doy,
        xday, extract(doy from xday) as xday_doy from agg1
        ORDER by season ASC
        """,
                op=op,
                varname=varname,
            ),
            conn,
            params={
                "months": 6 if season == "winter" else 0,
                "station": station,
                "soff": 1 if season == "winter" else 0,
                "thresh": threshold,
            },
            index_col="season",
        )
    # We need to do some magic to julian dates straight
    if season == "winter":
        # drop the first row
        df = df.drop(df.index.values[0])
        df.loc[df["nday_doy"] < 183, "nday_doy"] += 365.0
        df.loc[df["xday_doy"] < 183, "xday_doy"] += 365.0
    # Set NaN where we did not meet conditions
    zeros = df[df["count"] == 0].index.values
    col = "xday_doy" if extrenum == "last" else "nday_doy"
    df2 = df[df["count"] > 0]
    if df2.empty:
        raise NoDataFound("No data found.")
    tl = PDICT[f"{extrenum}_{varname}_{direction}"]
    title = (
        f"{ctx['_sname']} :: {extrenum.capitalize()} Date and Days\n"
        f"{tl} {threshold}"
        "°F"
    )
    fig = figure(title=title, apctx=ctx)
    # Main plot gets 75% of vertical space
    ax_box = fig.add_axes((0.1, 0.32, 0.65, 0.05), frameon=False)
    ax = fig.add_axes((0.1, 0.37, 0.65, 0.53))
    ax3 = fig.add_axes((0.1, 0.1, 0.65, 0.15))

    # The present year value may be so low that it destorts the plot
    lastval = df2.iloc[-1]["count"]
    minval = df2[df2["count"] > lastval]["count"].min()
    pltdf = df2
    if lastval < 10 and (minval - lastval) > 30:
        pltdf = df2[df2["count"] > lastval]
    ax.scatter(pltdf[col], pltdf["count"])

    # Calculate y-axis limits first based on data
    ymin = pltdf["count"].min()
    ymax = pltdf["count"].max()
    yrange = ymax - ymin

    boxprops = dict(color="blue", alpha=0.7)
    whiskerprops = dict(color="blue", alpha=0.7)
    medianprops = dict(color="red")

    # Create boxplot at the bottom of the plot
    ax_box.boxplot(
        pltdf[col],
        positions=[0.5],
        widths=[0.5],
        orientation="vertical",
        patch_artist=True,
        boxprops=boxprops,
        whiskerprops=whiskerprops,
        medianprops=medianprops,
        showfliers=False,
        flierprops=dict(marker="o", markerfacecolor="blue", alpha=0.5),
    )
    ax_box.set_yticks([])
    ax_box.set_ylim(0.2, 0.8)

    ax.set_ylim(ymin - 3, ymax + yrange * 0.05)

    # Add stats annotation using date formatting
    q1_date = datetime(2000, 1, 1) + timedelta(
        days=int(np.percentile(pltdf[col], 25))
    )
    med_date = datetime(2000, 1, 1) + timedelta(
        days=int(np.percentile(pltdf[col], 50))
    )
    q3_date = datetime(2000, 1, 1) + timedelta(
        days=int(np.percentile(pltdf[col], 75))
    )

    # Function to calculate text box height based on number of lines
    def get_text_height(text):
        return 0.04 + (text.count("\n") * 0.02)  # Base height + line spacing

    # Start position for first box
    current_y = 0.9
    current_x = 0.78

    # Place earliest dates at top
    label = f"Earliest {'Last' if extrenum == 'last' else 'First'} Dates"
    lcol = col.split("_")[0]
    for _, row in df.sort_values(col, ascending=True).head(10).iterrows():
        if row[lcol] is None:
            continue
        label += f"\n{row[lcol]:%d %b %Y}"
    earliest_height = get_text_height(label)
    fig.text(
        current_x,
        current_y,
        label,
        ha="left",
        va="top",
        bbox=dict(
            facecolor="#F0F0F0", edgecolor="gray", boxstyle="round,pad=0.5"
        ),
    )

    # Calculate next position with padding
    current_y -= earliest_height + 0.05  # Add padding between boxes

    # Place statistics
    stats_text = (
        "Distribution Statistics\n"
        f"Q1: {q1_date:%d %b}\n"
        f"Median: {med_date:%d %b}\n"
        f"Q3: {q3_date:%d %b}"
    )
    stats_height = get_text_height(stats_text)
    fig.text(
        current_x,
        current_y,
        stats_text,
        ha="left",
        va="top",
        bbox=dict(
            facecolor="#F0F0F0", edgecolor="gray", boxstyle="round,pad=0.5"
        ),
    )

    # Calculate next position
    current_y -= stats_height + 0.05

    # Place threshold info
    zeros_str = (
        "[" + ",".join(str(z) for z in zeros) + "]" if len(zeros) < 4 else ""
    )
    thresh_text = (
        "Threshold Statistics\n"
        f"{len(zeros)} year(s) failed threshold {zeros_str}\n"
        f"Avg Count: {df2['count'].mean():.1f} days"
    )
    thresh_height = get_text_height(thresh_text)
    fig.text(
        current_x,
        current_y,
        thresh_text,
        ha="left",
        va="top",
        bbox=dict(
            facecolor="#F0F0F0", edgecolor="gray", boxstyle="round,pad=0.5"
        ),
    )

    # Calculate next position
    current_y -= thresh_height + 0.05

    # Place latest dates at bottom
    label = f"Latest {'Last' if extrenum == 'last' else 'First'} Dates"
    for _, row in df.sort_values(col, ascending=False).head(10).iterrows():
        if row[lcol] is None:
            continue
        label += f"\n{row[lcol]:%d %b %Y}"
    fig.text(
        current_x,
        current_y,
        label,
        ha="left",
        va="top",
        bbox=dict(
            facecolor="#F0F0F0", edgecolor="gray", boxstyle="round,pad=0.5"
        ),
    )

    ax.grid(True)
    ax.grid(True, zorder=1, alpha=0.5)
    ax.set_axisbelow(True)
    ax_box.set_xlabel(
        ("Date of %s Occurrence%s")
        % (
            extrenum.capitalize(),
            (
                ", Year of December for Winter Season"
                if season == "winter"
                else ""
            ),
        )
    )
    ax.set_ylabel(
        ("Days with %s %s %s°F")
        % (
            varname.capitalize(),
            "At or Above" if direction == "above" else "Below",
            threshold,
        )
    )

    # Add the CDF plot in lower subplot
    sortvals = np.sort(np.array(df2[col].values))
    yvals = np.arange(len(sortvals)) / float(len(sortvals))
    ax3.plot(sortvals, yvals * 100.0, color="r")
    ax3.set_ylabel("Accum. Freq [%]", color="r")
    ax3.tick_params(axis="y", colors="r")

    # Set up coordinated gridlines for CDF plot
    ax3.set_yticks([0, 25, 50, 75, 100])
    ax3.grid(True, axis="y", linestyle="--", alpha=0.3, color="red")
    ax3.grid(True, axis="x", alpha=0.3)

    # Align x-axis ticks between plots
    xticks = []
    xticklabels = []
    for i in np.arange(df2[col].min() - 5, df2[col].max() + 5, 1):
        ts = datetime(2000, 1, 1) + timedelta(days=i)
        if ts.day == 1:
            xticks.append(i)
            xticklabels.append(ts.strftime("%-d %b"))

    for _ax in [ax, ax_box, ax3]:
        _ax.set_xlim(df2[col].min() - 10, df2[col].max() + 10)
        _ax.set_xticks(xticks)
        _ax.set_xticklabels(xticklabels)
    # hide the x-axis labels on the main ax plot
    ax.set_xticklabels([])
    ax3.set_ylim(-0.1, 100)

    if year in df2.index:
        df3 = df2.loc[year]
        if df3["count"] >= minval:
            ax.scatter(df3[col], df3["count"], zorder=5, color="r")
            ax.text(df3[col], df3["count"] + 1, f"{year}", zorder=5, color="r")
            ax.axhline(df3["count"])
        else:
            fig.text(
                0.04,
                0.05,
                f"{year} value of {df3['count']} day(s) not shown",
            )
        ax.axvline(df3[col])
        ax.annotate(
            str(year),
            (df3[col], 0.79),
            xycoords=("data", "axes fraction"),
            color="b",
            rotation=90,
            va="top",
        )

    idx = df2[col].idxmax()
    if idx != year:
        ax.text(
            df2.at[idx, col] + 1,
            df2.at[idx, "count"],
            f"{idx}",
            ha="left",
        )
    idx = df2[col].idxmin()
    if idx != year:
        ax.text(
            df2.at[idx, col] - 1,
            df2.at[idx, "count"],
            f"{idx}",
            va="bottom",
        )
    idx = df2["count"].idxmax()
    if idx != year:
        ax.text(
            df2.at[idx, col] + 1,
            df2.at[idx, "count"],
            f"{idx}",
            va="bottom",
        )

    return fig, df
