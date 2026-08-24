"""
This autoplot combines the USDA NASS county yield estimates with
summarized weather variables from a single weather station.  The
county that the weather station resides in is used for the comparison.</p>

<p>If you select a statewide areal averaged weather station, you will get the
statewide yield estimates and not an individual county.  Unfortunately, there
is nothing analogous for the climate/crop district weather values as those
values are mostly missing within USDA NASS.</p>

<p>
The eight right hand side sub-plots will contain a simple linear fit and
Pearson correlation coefficient between the weather variable and the yield
departure from the selected trendline.  An info box appears above each plot
denoting the correlation coefficient, p-value and number of samples
(read years) plotted.
If the p-value is less than 0.05, the box will be shaded in wheat color and
likely implies a statistically significant relationship.
</p>
"""

import matplotlib.colors as mpcolors
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.colorbar import ColorbarBase
from matplotlib.ticker import MaxNLocator
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure, get_cmap, pretty_bins
from pyiem.reference import state_names
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression

from iemweb.autoplot import ARG_STATION

PDICT = {
    "corn": "Corn Grain",
    "soybeans": "Soybeans",
}
PDICT2 = {
    "trail10": "Trailing 10 year average",
    "linear": "Linear Regression",
    "mean": "Long Term Mean",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "nass": True}
    desc["arguments"] = [
        {
            "type": "select",
            "options": PDICT,
            "default": "corn",
            "name": "crop",
            "label": "Select Crop",
        },
        ARG_STATION,
        {
            "type": "sday",
            "default": "0501",
            "name": "sdate",
            "label": "Select inclusive start day of the year",
        },
        {
            "type": "sday",
            "default": "0930",
            "name": "edate",
            "label": "Select inclusive end day of the year",
        },
        {
            "type": "select",
            "options": PDICT2,
            "label": "From which metric to compute yield departure.",
            "default": "trail10",
            "name": "how",
        },
        {
            "type": "cmap",
            "name": "cmap",
            "default": "RdYlGn",
            "label": "Color Ramp:",
        },
    ]
    return desc


def get_obsdf(ctx: dict):
    """Figure out our observations."""
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper(
                """
                SELECT year, sum(precip) as sum_precip,
                sum(gddxx(50, 86, high, low)) as gdd5086,
                sum(sdd86(high, low)) as sdd86,
                avg(low) as avg_low,
                sum(case when low >= 70 then 1 else 0 end) as days_low_a70,
                sum(case when low < 60 then 1 else 0 end) as days_low_b60,
                avg(merra_srad) as avg_merra_srad,
                avg(era5land_srad) as avg_era5land_srad,
                sum(case when precip > 0.005 then 1 else 0 end) as precip_days
                from alldata
                WHERE station = :station and sday >= :sts and
                sday <= :ets GROUP by year ORDER by year ASC
            """
            ),
            conn,
            index_col="year",
            params={
                "station": ctx["station"],
                "sts": ctx["sdate"].strftime("%m%d"),
                "ets": ctx["edate"].strftime("%m%d"),
            },
        )
    return df


def get_countyname(ugc: str) -> str:
    """Get name"""
    with get_sqlalchemy_conn("postgis") as conn:
        res = conn.execute(
            sql_helper("""
            SELECT name from ugcs where ugc = :ugc and end_ts is null
            """),
            {"ugc": ugc},
        )
        row = res.mappings().fetchone()
    return f"(({ugc}))" if row is None else row["name"]


def bling(df: pd.DataFrame, ax: Axes, col: str, dcol: str):
    """Common addition of data to the subplot."""
    hasdf = df[[col, dcol, "symbol", "color"]].dropna()
    for marker, gdf in hasdf.groupby("symbol"):
        # This is used back in main plotting func
        label = f"{gdf.index.values[0]:.0f} [{gdf[dcol].values[0]:.1f}]"
        ax.scatter(
            gdf[col].to_numpy(),
            gdf[dcol].to_numpy(),
            facecolor=gdf["color"].to_list(),
            marker=marker,
            edgecolor="None" if len(gdf.index) > 1 else "k",
            zorder=5 if marker != "o" else 3,
            label=None if len(gdf.index) > 1 else label,
        )
    ax.grid(True)

    # Ensure the yaxis is consistent between all subplots, use inbound df
    stats = df[dcol].describe()
    rng = stats["max"] - stats["min"]
    ax.set_ylim(stats["min"] - rng * 0.15, stats["max"] + rng * 0.15)

    # Simple indication of linear relationship strength/significance
    r, pvalue = pearsonr(hasdf[col].to_numpy(), hasdf[dcol].to_numpy())
    slope, intercept = np.polyfit(
        hasdf[col].to_numpy(), hasdf[dcol].to_numpy(), 1
    )
    xs = np.array(ax.get_xlim())
    ax.plot(xs, slope * xs + intercept, color="k", lw=1, zorder=6)
    ax.text(
        0.02,
        1.02,
        f"r={r:.2f} p={pvalue:.2f} n={len(hasdf.index)}",
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=8,
        bbox={
            "boxstyle": "round",
            "facecolor": "white" if pvalue > 0.05 else "wheat",
            "alpha": 0.8,
        },
    )


def get_nass(ctx: dict) -> pd.DataFrame:
    """Get NASS."""
    county = ctx["_nt"].sts[ctx["station"]]["ugc_county"]
    ccol = "state_alpha || 'C' || county_ansi"
    agg_level_desc = "COUNTY"
    if ctx["station"].endswith("0000"):
        ccol = "state_alpha"
        county = ctx["station"][:2]
        agg_level_desc = "STATE"
    with get_sqlalchemy_conn("coop") as conn:
        # sometimes we have dups :/
        ut = {"corn": "GRAIN", "soybeans": "ALL UTILIZATION PRACTICES"}[
            ctx["crop"]
        ]
        df = pd.read_sql(
            sql_helper(
                """
                select year, avg(num_value) as num_value from
                nass_quickstats where {ccol} = :c
                and statisticcat_desc = 'YIELD' and commodity_desc = :cr and
                util_practice_desc = :ut and
                agg_level_desc = :agl GROUP by year ORDER by year ASC
            """,
                ccol=ccol,
            ),
            conn,
            params={
                "c": county,
                "cr": ctx["crop"].upper(),
                "ut": ut,
                "agl": agg_level_desc,
            },
            index_col="year",
        )
    if df.empty:
        raise NoDataFound("Could not find any data, sorry.")
    return df


def plotter(ctx: dict):
    """Go"""
    county = ctx["_nt"].sts[ctx["station"]]["ugc_county"]
    countyname = get_countyname(county)
    if ctx["station"].endswith("0000"):
        county = ctx["station"][:2]
        countyname = state_names[county]
    obsdf = get_obsdf(ctx)
    df = get_nass(ctx)

    xaxis = df.index.values

    df["trail10"] = df["num_value"].rolling(10, min_periods=1).mean()
    linear_regressor = LinearRegression()
    linear_regressor.fit(
        xaxis.reshape(-1, 1), df["num_value"].values.reshape(-1, 1)
    )
    df["linear"] = linear_regressor.predict(xaxis.reshape(-1, 1))
    df["mean"] = df["num_value"].mean()
    for col in PDICT2:
        df[f"{col}_departure"] = df["num_value"] - df[col]
    for col in obsdf.columns:
        df[col] = obsdf[col]

    dcol = f"{ctx['how']}_departure"
    deltas = df[dcol].to_numpy()
    extent = df[dcol].abs().max()
    if extent == 0:
        raise NoDataFound("No departures found, cannot make a plot.")
    bins = pretty_bins(0 - extent, extent)
    cmap = get_cmap(ctx["cmap"])
    norm = mpcolors.BoundaryNorm(bins, cmap.N)
    df["color"] = list(cmap(norm(deltas)))
    colors = df["color"].values
    fig = figure(
        title=f"({ctx['sdate']:%-d %b}-{ctx['edate']:%-d %b}) {ctx['_sname']}",
        subtitle=(
            f"USDA NASS {PDICT[ctx['crop']]} "
            f"Yield Estimates for {countyname} ({county}), "
            f"Departures Against Trendline: {PDICT2[ctx['how']]}"
        ),
    )
    mainax_width = 0.4
    mainax_height = 0.3
    ax = fig.add_axes((0.06, 0.55, mainax_width, mainax_height))
    ax.bar(xaxis, df["num_value"].values, color=colors)
    ax.plot(
        xaxis, df["trail10"].values, lw=2, color="k", label="10y Trailing Ave"
    )
    ax.plot(xaxis, df["mean"].values, lw=2, color="b", label="Mean")
    ax.plot(xaxis, df["linear"].values, lw=2, color="r", label="Linear")
    ax.set_ylabel("Yield [bu/ac]")
    ax.legend(ncol=3, loc=(0, 1))
    ax.grid(True)

    ax = fig.add_axes((0.06, 0.2, mainax_width, mainax_height))
    ax.bar(xaxis, deltas, color=colors)
    ax.set_ylabel("Departure [bu/ac]")
    ax.grid(True)

    df["symbol"] = "o"
    sortdf = df.sort_values(dcol, ascending=True)
    df.at[sortdf.index.values[0], "symbol"] = "*"
    df.at[sortdf.index.values[1], "symbol"] = ">"
    df.at[sortdf.index.values[2], "symbol"] = "<"
    df.at[sortdf.index.values[-1], "symbol"] = "s"
    df.at[sortdf.index.values[-2], "symbol"] = "v"
    df.at[sortdf.index.values[-3], "symbol"] = "^"

    # Wx Comparisons
    anchorx = 0.54
    anchory = 0.08
    width = 0.16
    height = 0.12
    pad = 0.05
    xpad = 0.04
    ax = fig.add_axes((anchorx, anchory, width, height))
    bling(df, ax, "sum_precip", dcol)
    ax.axvline(df["sum_precip"].mean())
    ax.set_ylabel("Departure [bu/ac]")
    ax.set_xlabel("Precipitation [inch]")
    ax.legend(ncol=3, loc=(-2.75, 0))
    fig.text(0.46, 0.06, "Legend for Top 3/Bottom 3 Years ->", ha="right")

    ax2 = fig.add_axes((anchorx, anchory + height + 2 * pad, width, height))
    bling(df, ax2, "gdd5086", dcol)
    ax2.axvline(df["gdd5086"].mean())
    ax2.set_ylabel("Departure [bu/ac]")
    ax2.set_xlabel("GDD (50, 86) [F]")

    ax3 = fig.add_axes((anchorx + width + xpad, anchory, width, height))
    bling(df, ax3, "sdd86", dcol)
    ax3.axvline(df["sdd86"].mean())
    ax3.set_xlabel("SDD (86) [F]")

    ax4 = fig.add_axes(
        (anchorx + width + xpad, anchory + height + 2 * pad, width, height)
    )
    bling(df, ax4, "avg_low", dcol)
    ax4.axvline(df["avg_low"].mean())
    ax4.set_xlabel("Avg Daily Low [F]")

    ax5 = fig.add_axes(
        (anchorx, anchory + 2 * height + 4 * pad, width, height)
    )
    bling(df, ax5, "days_low_a70", dcol)
    ax5.axvline(df["days_low_a70"].mean())
    ax5.set_xlabel("Days Low >= 70°F")
    ax5.set_ylabel("Departure [bu/ac]")

    ax6 = fig.add_axes(
        (anchorx + width + xpad, anchory + 2 * height + 4 * pad, width, height)
    )
    bling(df, ax6, "days_low_b60", dcol)
    ax6.axvline(df["days_low_b60"].mean())
    ax6.set_xlabel("Days Low < 60°F")

    ax7 = fig.add_axes(
        (anchorx, anchory + 3 * height + 6 * pad, width, height)
    )
    bling(df, ax7, "avg_era5land_srad", dcol)
    ax7.axvline(df["avg_era5land_srad"].mean())
    ax7.set_xlabel(r"ERA5-Land Solar Rad MJ$d^{-1}$")
    ax7.set_ylabel("Departure [bu/ac]")

    ax8 = fig.add_axes(
        (anchorx + width + xpad, anchory + 3 * height + 6 * pad, width, height)
    )
    bling(df, ax8, "precip_days", dcol)
    ax8.axvline(df["precip_days"].mean())
    ax8.set_xlabel("Days Measurable Precip")
    ax8.xaxis.set_major_locator(MaxNLocator(5, integer=True))

    cax = fig.add_axes(
        [0.93, 0.1, 0.01, 0.73], frameon=False, yticks=[], xticks=[]
    )
    cb = ColorbarBase(cax, norm=norm, cmap=cmap)
    cb.set_ticks(bins)

    return fig, df
