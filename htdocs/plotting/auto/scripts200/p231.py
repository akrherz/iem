"""Change in SPI."""
import datetime

import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import MapPlot, plt
from pyiem.reference import state_names
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """This autoplot produces an infographic for a given state with some
    diagnostics on the weekly change in Standardized Precipitation Index (SPI)
    over a given day interval.  The purpose is to show how a state's SPI values
    have changed over a seven day period.  Changes in SPI drought classfication
    are colorized as green for improvements and red for degradations.

    <p>Caution, this chart does take a number of seconds to generate.
    """
    today = datetime.date.today() - datetime.timedelta(days=1)
    lastweek = today - datetime.timedelta(days=7)
    desc["arguments"] = [
        dict(
            type="date",
            name="from",
            default=f"{lastweek:%Y/%m/%d}",
            label="Evaluate change on this starting date:",
        ),
        dict(
            type="date",
            name="on",
            default=f"{today:%Y/%m/%d}",
            label="Evaluate change on this ending date:",
        ),
        dict(
            type="int",
            name="days",
            default=60,
            label="Compute SPI over how many trailing days",
        ),
        dict(
            type="state",
            name="state",
            default="IA",
            label="Select State:",
        ),
    ]
    return desc


def compute(state, sdate, edate, days):
    """Compute the statistic."""
    # Do we need magic 1 Jan logic?
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            f"""
            WITH obs as (
                SELECT station, day, sday,
                sum(precip) OVER (PARTITION by station ORDER by day ASC
                ROWS between %s PRECEDING AND CURRENT ROW) from
                alldata_{state} WHERE substr(station, 3, 1) not in ('C', 'T')
                and station != '{state}0000'
            ), datum as (
                SELECT * from obs where sday in %s
                ORDER by station ASC, day ASC
            ), agg as (
                select station, sday, avg(sum) as avg_precip,
                stddev(sum) as std_precip, count(*) from datum
                GROUP by station, sday
            ), agg2 as (
                SELECT d.station, d.day, d.sday, d.sum, a.avg_precip,
                a.std_precip from datum d, agg a WHERE d.station = a.station
                and d.sday = a.sday and a.count >= 30 and d.day in %s
                ORDER by d.station ASC, d.day ASC
            )
            select a.*, st_x(t.geom) as lon, st_y(t.geom) as lat
            from agg2 a JOIN stations t on (a.station = t.id) WHERE
            t.network = '{state}CLIMATE'
            """,
            conn,
            params=(
                days - 1,
                (f"{edate:%m%d}", f"{sdate:%m%d}"),
                (sdate, edate),
            ),
            parse_dates=["day"],
        )
    if df.empty:
        raise NoDataFound("Failed to find any data for given date")
    df["depart"] = df["sum"] - df["avg_precip"]
    df["spi"] = df["depart"] / df["std_precip"]
    return df


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    df = compute(ctx["state"], ctx["from"], ctx["on"], ctx["days"])
    startdf = df[df["sday"] == f"{ctx['from']:%m%d}"].set_index("station")
    enddf = df[df["sday"] == f"{ctx['on']:%m%d}"].set_index("station")
    if startdf.empty or enddf.empty:
        raise NoDataFound("No data available for given date.")
    df = startdf.join(enddf, how="inner", lsuffix="_start", rsuffix="_end")
    df = df.sort_values("spi_start", ascending=True)
    df["depart_change"] = df["depart_end"] - df["depart_start"]
    df["spi_change"] = df["spi_end"] - df["spi_start"]
    # D4
    levels = [-100, -2, -1.6, -1.3, -0.8, -0.5, 0.5, 0.8, 1.3, 1.6, 2, 100]
    dd = [-4, -3, -2, -1, -0.1, 0, 0.1, 1, 2, 3, 4]
    dlabels = ["D4", "D3", "D2", "D1", "D0", "-", "W0", "W1", "W2", "W3", "W4"]
    df["d_start"] = pd.cut(df["spi_start"], levels, labels=dd).astype(float)
    df["d_end"] = pd.cut(df["spi_end"], levels, labels=dd).astype(float)
    df["dclass_end"] = pd.cut(df["spi_end"], levels, labels=dlabels).astype(
        str
    )
    df["dclass_start"] = pd.cut(
        df["spi_start"], levels, labels=dlabels
    ).astype(str)
    celltext = (
        df[["dclass_start", "dclass_end", "lat_start"]]
        .groupby(["dclass_start", "dclass_end"])
        .count()
        .reset_index()
        .pivot(index="dclass_start", columns="dclass_end", values="lat_start")
        .reindex(index=dlabels, columns=dlabels)
        .fillna(0)
        .astype(int)
        .astype(str)
        .replace({"0": ""})
        .values.tolist()
    )
    df["d_change"] = df["d_end"] - df["d_start"]
    df["color"] = "black"
    df.loc[df["d_change"] > 0, "color"] = "green"
    df.loc[df["d_change"] < 0, "color"] = "red"
    mp = MapPlot(
        title=(
            f"{state_names[ctx['state']]} {ctx['days']} Day SPI Change "
            f"from {ctx['from']:%-d %b %Y} to {ctx['on']:%-d %b %Y}"
        ),
        subtitle=(
            "Map shows SPI drought classification on end date, "
            "red degradation and green improvement"
        ),
        continentalcolor="white",
        state=ctx["state"],
        axes_position=[0.02, 0.1, 0.6, 0.8],
    )
    mp.draw_usdm(ctx["on"])
    mp.plot_values(
        df["lon_start"],
        df["lat_start"],
        df["dclass_end"].values,
        color=df["color"].values,
        labelbuffer=0,
    )
    mp.fig.text(0.7, 0.87, "Change Vector")
    ax = mp.fig.add_axes([0.7, 0.45, 0.25, 0.40], yticks=[])
    ax.set_xlabel("SPI")
    ax.set_ylabel("Sorted Station by Start SPI")
    yvals = pd.Series(range(len(df.index))) / len(df.index)
    ax.quiver(
        df["spi_start"],
        yvals,
        df["spi_change"],
        [0] * len(df.index),
        color=df["color"],
        scale_units="xy",
        angles="xy",
        scale=1,
        zorder=10,
    )
    colors = ["#ffff00", "#fcd37f", "#ffaa00", "#e60000", "#730000"]
    spis = [-0.5, -0.8, -1.3, -1.6, -2, -10]
    for i, spi in enumerate(spis[:-1]):
        ax.axvspan(spis[i + 1], spi, color=colors[i])
    ax.set_xlim(
        min([df["spi_start"].min(), df["spi_end"].min()]) - 0.1,
        max([df["spi_start"].max(), df["spi_end"].max()]) + 0.1,
    )
    ax.set_ylim(-0.01, 1)

    mp.fig.text(
        0.7, 0.32, f"Station Change Count\nSPI on {ctx['on']:%-d %b %Y}"
    )
    mp.fig.text(0.65, 0.1, f"SPI on {ctx['from']:%-d %b %Y}", rotation=90)
    ax = mp.fig.add_axes(
        [0.7, 0.31, 0.25, 0.1], xticks=[], yticks=[], facecolor="None"
    )
    for x in ax.spines:
        ax.spines[x].set_visible(False)
    cellcolors = []
    for i in range(11):
        t = []
        if i >= 1:
            t.extend([(1, 0.8, 0.8)] * i)
        t.append((1, 1, 1))
        if i < 10:
            t.extend([(0.5, 1, 0.5)] * (11 - i - 1))
        cellcolors.append(t)

    plt.table(
        celltext,
        cellColours=cellcolors,
        rowLabels=dlabels,
        colLabels=dlabels,
    )

    return mp.fig, df


if __name__ == "__main__":
    plotter({})
