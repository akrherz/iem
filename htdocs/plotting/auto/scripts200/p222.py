"""
Using available one minute precipitation data from an ASOS, this
data is merged with an archive of polygon based warnings.
Precipitation totals are then computed during the warnings that spatially
cover the observation point and within one hour of the warning.

<p>This app is slow to load, please be patient!
"""
from datetime import timedelta

import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn, utc
from sqlalchemy import text

PDICT = {
    "svrtor": "Severe Thunderstorm + Tornado Warnings",
    "ffw": "Flash Flood Warnings",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="DSM",
            network="IA_ASOS",
            label="Select Station (not all have 1 minute, sorry):",
        ),
        dict(
            type="select",
            options=PDICT,
            name="w",
            label="Select warning type(s) to accumulate precipitation during",
            default="svrtor",
        ),
    ]
    return desc


def get_data(ctx, meta):
    """Fetch Data."""
    with get_sqlalchemy_conn("asos1min") as conn:
        obsdf = pd.read_sql(
            "SELECT valid, precip, extract(year from valid)::int as year, "
            "extract(doy from valid)::int as doy "
            "from alldata_1minute where station = %s and valid > %s and "
            "precip > 0 and precip < 0.2 ORDER by valid ASC",
            conn,
            params=(meta["id"], utc(2002, 1, 1)),
            index_col="valid",
        )
    if obsdf.empty:
        raise NoDataFound("Failed to find any one-minute data, sorry.")
    obsdf["inwarn"] = False
    obsdf["nearwarn"] = False
    phenomenas = ["TO", "SV"]
    if ctx["w"] == "ffw":
        phenomenas = [
            "FF",
        ]
    with get_sqlalchemy_conn("postgis") as conn:
        warndf = pd.read_sql(
            text(
                """
            SELECT issue, expire from sbw WHERE issue > '2002-01-01' and
            phenomena = ANY(:ph) and significance = 'W' and
            status = 'NEW' and ST_Contains(geom,
            ST_Point(:lon, :lat, 4326))
            ORDER by issue ASC
            """
            ),
            conn,
            params={"ph": phenomenas, "lon": meta["lon"], "lat": meta["lat"]},
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
    obsdf, df = get_data(ctx, meta)
    label = "TOR or SVR"
    if ctx["w"] == "ffw":
        label = "Flash Flood"
    title = (
        f"[{ctx['zstation']}] {meta['name']} Yearly "
        f"Airport Precipitation [{df.index.min():.0f}-{df.index.max():.0f}]\n"
        f"Contribution during, near, and outside of {label} warning "
        "using one minute interval precipitation"
    )
    x = df.index.astype(int).tolist()

    fig, ax = figure_axes(title=title, apctx=ctx)
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
        f"coincided with {label} warning"
    )
    ax.grid(True)

    return fig, df


if __name__ == "__main__":
    plotter({})
