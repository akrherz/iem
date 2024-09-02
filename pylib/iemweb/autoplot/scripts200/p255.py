"""
This autoplot implemments a simple model known as the leaky bucket model. You
set the depth of the bucket and the assumed rate of loss.  Each day,
the depth of the bucket is calculated by adding the precipitation and
substracting the loss and thresholding the result to a value between
zero and the depth of a bucket.</p>

<p>A life choice this model implementation makes is to evaluate the
precipitation and loss at the end of the day simultaneously.  This
means that a given day's precipitation can be counted as much as the bucket's
depth and loss combined.</p>

<p>If you set the end date to a day of the year before the start date, the
year of the data represents the start year of the period that crosses 1 Jan.
"""

from datetime import date

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context
from sqlalchemy import text

from iemweb.autoplot import ARG_STATION
from iemweb.autoplot.barchart import barchar_with_top10


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        ARG_STATION,
        {
            "type": "sday",
            "default": "0501",
            "name": "sday",
            "label": "Select start date:",
        },
        {
            "type": "sday",
            "default": f"{date.today():%m%d}",
            "name": "eday",
            "label": "Select end date (inclusive):",
        },
        {
            "type": "float",
            "default": 1.0,
            "name": "depth",
            "label": "Depth of the bucket (inch):",
        },
        {
            "type": "float",
            "default": 1.0,
            "name": "init",
            "label": (
                "Initial depth of the bucket (inch), must be less than depth "
                "of bucket:"
            ),
        },
        {
            "type": "float",
            "default": 0.15,
            "name": "loss",
            "label": "Daily rate of loss/leak (inch):",
        },
        {
            "type": "year",
            "default": date.today().year,
            "name": "year",
            "label": "Year to Highlight",
        },
    ]
    return desc


def get_obsdf(ctx):
    """Figure out our observations."""
    limiter = "sday >= :sday and sday <= :eday"
    if ctx["eday"] < ctx["sday"]:
        limiter = "(sday >= :sday or sday <= :eday) "
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text(
                f"""
                SELECT day, year, precip, sday, 0.0 as bucket_depth
                from alldata
                WHERE station = :station and {limiter} ORDER by day ASC
            """
            ),
            conn,
            index_col="day",
            parse_dates=["day"],
            params={
                "station": ctx["station"],
                "sday": ctx["sday"].strftime("%m%d"),
                "eday": ctx["eday"].strftime("%m%d"),
            },
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    # See if we are crossing 1 Jan
    if ctx["eday"] < ctx["sday"]:
        # Subtract 1 year from the year column where sday < eday
        df.loc[df["sday"] <= ctx["eday"].strftime("%m%d"), "year"] = (
            df["year"] - 1
        )
    # Check the first year to see if it starts on our sday
    if df.index[0].strftime("%m%d") != ctx["sday"].strftime("%m%d"):
        df = df[df["year"] > df.index[0].year]
    if df.index[-1].strftime("%m%d") != ctx["eday"].strftime("%m%d"):
        df = df[df["year"] < df.index[-1].year]
    return df


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())

    df = get_obsdf(ctx)

    depth = max(0, min(999, ctx["depth"]))
    loss = max(0, ctx["loss"])
    for _year, gdf in df.groupby("year"):
        bucket = min(ctx["init"], depth)
        for idx, row in gdf.iterrows():
            bucket += row["precip"] - loss
            if bucket < 0:
                bucket = 0
            elif bucket > depth:
                bucket = depth
            df.at[idx, "bucket_depth"] = bucket

    fig = figure(
        title=(
            f"({df.index[0].year}-{df.index[-1].year}) "
            f"[{ctx['sday'].strftime('%b %-d')}-"
            f"{ctx['eday'].strftime('%b %-d')}] "
            f"{ctx['_sname']}:: Leaky Bucket Model"
        ),
        subtitle=(
            f"Bucket Depth: {depth:.2f} inches, "
            f"Loss/Leak: {loss:.2f} inches/day"
        ),
        apctx=ctx,
    )
    # Plot the bucket depth for year of interest
    thisyear = df[df["year"] == ctx["year"]]
    if thisyear.empty:
        raise NoDataFound("No data found for year of interest.")
    # Plot the bucket depth
    ax = fig.add_axes([0.1, 0.7, 0.7, 0.15])
    ax.text(
        0.01,
        1.01,
        f"Year Daily Timeseries: {ctx['year']}",
        transform=ax.transAxes,
        va="bottom",
        ha="left",
    )
    ax.bar(
        thisyear.index.values,
        thisyear["bucket_depth"],
        color="blue",
        width=1.0,
        align="center",
    )
    ax.set_ylabel("Bucket\nDepth [inch]")
    ax.grid(True)
    ax.set_xlim(
        thisyear.index[0] - pd.Timedelta(days=1),
        thisyear.index[-1] + pd.Timedelta(days=1),
    )

    # Plot the number of days the bucket was empty
    yearlyzeros = (
        df[df["bucket_depth"] == 0][["year", "precip"]]
        .groupby("year")
        .count()
        .reindex(range(int(df["year"].min()), int(df["year"].max()) + 1))
        .fillna(0)
    )
    ax = barchar_with_top10(
        fig,
        yearlyzeros,
        "precip",
        color="tan",
        labelformat="%i",
    )
    ax.set_position([0.1, 0.1, 0.7, 0.5])
    ax.set_ylabel("Number of Days")
    ax.grid(True)
    ax.axhline(yearlyzeros["precip"].mean(), color="r", lw=2)
    ax.text(
        0.01,
        1.01,
        f"Days Bucket Empty, mean={yearlyzeros['precip'].mean():.1f} days",
        transform=ax.transAxes,
        va="bottom",
        ha="left",
    )

    return fig, df
