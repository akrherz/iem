"""
This chart shows the number of VTEC phenomena and
significance combinations issued by a NWS Forecast Office for a given year.
Please note that not all current-day VTEC products were started in 2005,
some came a few years later.  So numbers in 2005 are not directly
comparable to 2015.  Here is a
<a href="http://www.nws.noaa.gov/os/vtec/pdfs/VTEC_explanation6.pdf">handy
chart</a> with more details on VTEC and codes used in this graphic.

<p>Due to the chart's oblong nature, there is no way to control the
image size at this time.
"""

import pandas as pd
from matplotlib.ticker import MaxNLocator
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure, fitbox
from pyiem.util import get_autoplot_context
from sqlalchemy import text


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["defaults"] = {"_r": None}  # disables
    desc["arguments"] = [
        dict(
            type="networkselect",
            name="station",
            network="WFO",
            default="DMX",
            label="Select WFO:",
            all=True,
        )
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"][:4]
    ctx["_nt"].sts["_ALL"] = {"name": "All Offices"}

    params = {"wfo": station}
    sqllim = "wfo = :wfo and " if station != "_ALL" else ""
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            text(
                f"""
            SELECT distinct extract(year from issue) as year,
            phenomena, significance from warnings WHERE
            {sqllim} phenomena is not null and significance is not null
            and issue > '2005-01-01'
            """
            ),
            conn,
            params=params,
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No data was found.")
    df["wfo"] = station
    df["year"] = df["year"].astype("i")
    gdf = df.groupby("year").count()

    title = f"[{station}] NWS {ctx['_nt'].sts[station]['name']}"
    subtitle = (
        "Count of Distinct VTEC Phenomena/Significance - "
        f"{df['year'].min():.0f} to {df['year'].max():.0f}"
    )
    fig = figure(figsize=(10, 14 if station != "_ALL" else 21), apctx=ctx)
    fitbox(fig, title, 0.1, 0.97, 0.97, 0.99)
    fitbox(fig, subtitle, 0.1, 0.97, 0.95, 0.97)
    ax = [None, None]
    ax[0] = fig.add_axes([0.05, 0.75, 0.93, 0.2])
    ax[1] = fig.add_axes([0.05, 0.03, 0.93, 0.68])

    ax[0].bar(
        gdf.index.values, gdf["wfo"], width=0.8, fc="b", ec="b", align="center"
    )
    yoff = gdf["wfo"].max() * 0.05
    for yr, row in gdf.iterrows():
        ax[0].text(
            yr,
            row["wfo"] + yoff,
            row["wfo"],
            ha="center",
            bbox=dict(color="white"),
        )
    ax[0].set_ylim(0, gdf["wfo"].max() * 1.1)
    ax[0].grid()
    ax[0].set_ylabel("Count")
    ax[0].set_xlim(gdf.index.values.min() - 0.5, gdf.index.values.max() + 0.5)
    ax[0].xaxis.set_major_locator(MaxNLocator(integer=True))

    pos = {}
    i = 1
    df = df.sort_values(["phenomena", "significance"])
    for _, row in df.iterrows():
        key = f"{row['phenomena']}.{row['significance']}"
        if key not in pos:
            pos[key] = i
            i += 1
        ax[1].text(
            row["year"],
            pos[key],
            key,
            ha="center",
            va="center",
            fontsize=10,
        )

    ax[1].set_title("VTEC <Phenomena.Significance> Issued by Year")
    ax[1].set_ylim(0, i)
    ax[1].set_yticks([])
    ax[1].grid(True)
    ax[1].set_xlim(gdf.index.values.min() - 0.5, gdf.index.values.max() + 0.5)
    ax[1].xaxis.set_major_locator(MaxNLocator(integer=True))
    return fig, df


if __name__ == "__main__":
    plotter({})
