"""1 minute precip during severe weather."""
from datetime import timedelta

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context, get_dbconn, utc
from pyiem.plot import figure_axes
from pyiem.exceptions import NoDataFound


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = dict()
    desc["data"] = True
    desc[
        "description"
    ] = """Using available one minute precipitation data from an ASOS, this
    data is merged with an archive of Severe Thunderstorm and Tornado
    Warnings.  Precipitation totals are then computed during the warnings
    and within one hour of the warning.

    <p>This app is slow to load, please be patient!
    """
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="DSM",
            network="IA_ASOS",
            label="Select Station (not all have 1 minute, sorry):",
        ),
    ]
    return desc


def get_data(meta):
    """Fetch Data."""
    obsdf = read_sql(
        "SELECT valid, precip, extract(year from valid)::int as year, "
        "extract(doy from valid)::int as doy "
        "from alldata_1minute "
        "where station = %s and valid > %s and precip > 0 and precip < 0.2 "
        "ORDER by valid ASC",
        get_dbconn("asos1min"),
        params=(meta["id"], utc(2002, 1, 1)),
        index_col="valid",
    )
    obsdf["inwarn"] = False
    obsdf["nearwarn"] = False

    warndf = read_sql(
        "SELECT issue, expire from sbw WHERE issue > '2002-01-01' and "
        "phenomena in ('TO', 'SV') and significance = 'W' and status = 'NEW' "
        "and ST_Contains(geom, "
        "GeomFromEWKT('SRID=4326;POINT(%s %s)')) "
        "ORDER by issue ASC",
        get_dbconn("postgis"),
        params=(meta["lon"], meta["lat"]),
        index_col=None,
    )
    td = timedelta(hours=1)
    for _, row in warndf.iterrows():
        obsdf.loc[row["issue"] : row["expire"], "inwarn"] = True
        obsdf.loc[row["issue"] - td : row["expire"] + td, "nearwarn"] = True

    # Yearly precips
    df = obsdf.groupby("year").sum().copy()

    # Warn only
    df["in"] = obsdf[obsdf["inwarn"]].groupby("year").sum()["precip"]
    # Near warn, but not in
    df["near"] = (
        obsdf[(obsdf["nearwarn"] & ~obsdf["inwarn"])]
        .groupby("year")
        .sum()["precip"]
    )
    df = df.fillna(0)
    df["out"] = df["precip"] - df["in"] - df["near"]
    return obsdf, df


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    meta = ctx["_nt"].sts[ctx["zstation"]]
    if "HAS1MIN" not in meta["attributes"]:
        raise NoDataFound("Sorry, the IEM has no one-minute data for station.")
    obsdf, df = get_data(meta)
    title = (
        f"[{ctx['zstation']}] {meta['name']} Yearly "
        f"Airport Precipitation [{df.index.min():.0f}-{df.index.max():.0f}]\n"
        "Contribution during, near, and outside of TOR or SVR warning "
        "using one minute interval precipitation"
    )
    x = df.index.astype(int).tolist()

    fig, ax = figure_axes(title=title)
    width = 0.45
    height = 0.36
    ax.set_position([0.05, 0.54, width, height])
    ax.set_ylabel("Yearly Precip [inch]")
    ax.bar(x, df["in"], fc="r")
    ax.bar(x, df["near"], bottom=df["in"], fc="b")
    ax.bar(
        x,
        df["out"],
        bottom=(df["in"] + df["near"]),
        fc="g",
    )
    ax.set_xticks(range(df.index.min(), df.index.max() + 1, 4))
    ax.grid(True)

    ax = fig.add_axes([0.05, 0.09, width, height])
    ax.set_ylabel("Percentage [%]")
    ax.set_ylim(0, 100)

    df["in_per"] = df["in"] / df["precip"] * 100.0
    p = df["in"].sum() / df["precip"].sum() * 100.0
    ax.bar(x, df["in_per"], fc="r", label=f"During {p:.1f}%")

    df["near_per"] = df["near"] / df["precip"] * 100.0
    p = df["near"].sum() / df["precip"].sum() * 100.0
    ax.bar(
        x,
        df["near_per"],
        bottom=df["in_per"],
        fc="b",
        label=f"+/- 1 hour {p:.1f}%",
    )

    df["out_per"] = df["out"] / df["precip"] * 100.0
    p = df["out"].sum() / df["precip"].sum() * 100.0
    ax.bar(
        x,
        df["out_per"],
        bottom=(df["in_per"] + df["near_per"]),
        fc="g",
        label=f"Outside {p:.1f}%",
    )

    ax.legend(ncol=3, loc=(0.03, 1.03))
    ax.grid(True)
    ax.set_xticks(range(df.index.min(), df.index.max() + 1, 4))
    ax.set_xlabel("Yearly precip may have missing data")

    ax = fig.add_axes([0.58, 0.5, 0.37, 0.31])
    idx = pd.MultiIndex.from_product([obsdf["precip"].unique(), [True, False]])
    gdf = (
        obsdf[["precip", "inwarn", "year"]]
        .groupby(["precip", "inwarn"])
        .count()
        .reindex(idx)
        .fillna(0)
        .transpose()
    )
    x = []
    y = []
    for val in [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10]:
        if (val, True) in gdf.columns:
            x.append(val)
            hit = gdf[(val, True)].iloc[0]
            miss = gdf[(val, False)].iloc[0]
            freq = hit / float(hit + miss) * 100.0
            y.append(freq)
            ax.text(
                val,
                freq + 5,
                f"{freq:.0f}%",
                ha="center",
                bbox=dict(color="white", boxstyle="square,pad=0"),
                va="bottom",
            )

    ax.bar(x, y, width=0.01)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Frequency [%]")
    ax.set_title(
        "Frequency that given minute precipitation total\n"
        "coincided with SVR or TOR warning"
    )
    ax.grid(True)

    return fig, df


if __name__ == "__main__":
    plotter(
        {
            "network": "PA_ASOS",
            "zstation": "RDG",
        }
    )
