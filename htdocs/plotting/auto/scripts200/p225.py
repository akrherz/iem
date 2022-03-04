"""Heatmap of SPI/Departure values."""
import calendar

from pandas import read_sql
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
import seaborn as sns
from sqlalchemy import text

PDICT = {
    "spi": "Standardized Precipitation Index",
    "pdep": "Precipitation Departure",
}
PDICT2 = {
    "ncei91": "NCEI 1991-2020 Climatology",
    "por": "Period of Record",
}
XTICKS = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """Departure from climatology metrics have an annual signal that
    is a function of the climatology.  This plot shows the distribution of
    departure values.</p>

    <p><strong>SPI</strong> is the standardized precipitation index. This is
    computed by using the NCEI 1991-2020 climatology to provide the average
    accumulation and the observed data to provide the standard deviation.</p>

    <p>The <strong>Minimum Possible</strong> value presented is a function
    of the statistical metric being computed.  For example, if the climatology
    accumation is 2 inches, the max negative departure can only be two
    inches.</p>
    """
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station:",
            network="IACLIMATE",
        ),
        dict(
            type="select",
            name="var",
            default="spi",
            options=PDICT,
            label="Select which metric to plot:",
        ),
        dict(
            type="select",
            name="c",
            default="ncei91",
            options=PDICT2,
            label="Which climatology to use for averages:",
        ),
        dict(
            type="int",
            name="days",
            default=90,
            label="Over how many trailing days to compute the metric?",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    varname = ctx["var"]
    with get_sqlalchemy_conn("coop") as conn:
        df = read_sql(
            text(
                f"""
            WITH climo as (
                select to_char(valid, 'mmdd') as sday, precip from
                ncei_climate91 where station = :ncei
            )
            select a.day, a.sday, a.precip as ob_precip,
            c.precip as climo_precip
            from alldata_{station[:2]} a, climo c where a.station = :station
            and a.sday = c.sday and a.precip is not null
            ORDER by a.day ASC
        """
            ),
            conn,
            params={
                "ncei": ctx["_nt"].sts[station]["ncei91"],
                "station": station,
            },
            index_col="day",
        )
    if df.empty:
        raise NoDataFound("Did not find any observations for station.")
    days = ctx["days"]
    # If POR is selected, use it for the climatology
    if ctx["c"] == "por":
        climo = (
            df[["ob_precip", "sday"]]
            .groupby("sday")
            .mean()
            .rename(columns={"ob_precip": "climo_precip"})
        )
        df = df.drop(columns=["climo_precip"]).join(climo, on="sday")
    # Compute the climatology over the trailing days
    climo = df[["ob_precip", "climo_precip"]].rolling(days).sum()
    df["ob_precip_accum"] = climo["ob_precip"]
    df["climo_precip_accum"] = climo["climo_precip"]
    # Compute the std deviation
    std = (
        df[["ob_precip_accum", "sday"]]
        .groupby("sday")
        .std()
        .rename(columns={"ob_precip_accum": "ob_precip_std"})
    )
    df = df.join(std, on="sday")
    df["pdep"] = df["ob_precip_accum"] - df["climo_precip_accum"]
    df["spi"] = df["pdep"] / df["ob_precip_std"]
    # Create a day of the year int value
    df["doy"] = df.index.map(lambda x: x.timetuple().tm_yday)

    title = (
        f"[{station}] {ctx['_nt'].sts[station]['name']}:: {days} Day "
        f"{PDICT[varname]}\n"
        "Heatmap of values by day of year\n"
        f"Climatology: {PDICT2[ctx['c']]}"
    )

    # Create the seaborn jointplot
    g = sns.JointGrid(data=df, x="doy", y=varname, height=6)
    figure(fig=g.figure, apctx=ctx, title=title)
    # Create an inset legend for the histogram colorbar
    cax = g.figure.add_axes([0.8, 0.65, 0.02, 0.2])

    # Add the joint and marginal histogram plots
    g.plot_joint(
        sns.histplot,
        discrete=(True, False),
        cmap="light:#03012d",
        pmax=0.8,
        cbar=True,
        cbar_ax=cax,
    )
    g.ax_joint.set_xticks(XTICKS)
    g.ax_joint.set_xticklabels(calendar.month_abbr[1:])
    g.ax_joint.set_xlim(0, 390)
    g.ax_joint.axhline(0, color="k")
    g.ax_joint.set_ylabel(PDICT[varname])
    g.ax_joint.set_xlabel("Day of Year")
    if varname == "spi":
        colors = ["#ffff00", "#fcd37f", "#ffaa00", "#e60000", "#730000"]
        for i, spi in enumerate([-0.5, -0.8, -1.3, -1.6, -2]):
            g.ax_joint.axhline(spi, color=colors[i], lw=2, zorder=4)
            g.ax_joint.annotate(
                f"D{i}",
                (0.97, spi),
                xycoords=("axes fraction", "data"),
                va="center",
                zorder=5,
                color="k" if i < 3 else "white",
                bbox=dict(color=colors[i]),
            )
    # Plot a max min line
    ydf = 0 - df[["sday", "climo_precip_accum"]].groupby("sday").min()
    if varname == "spi":
        ydf["min"] = ydf["climo_precip_accum"] / std["ob_precip_std"]
    else:
        ydf["min"] = ydf["climo_precip_accum"]
    g.ax_joint.plot(
        range(366), ydf["min"], color="r", lw=2, label="Minimum Possible"
    )
    g.ax_joint.legend(loc=(0.5, 1.05))

    g.plot_marginals(sns.histplot, element="step", color="#03012d")
    g.ax_marg_x.remove()
    return g.figure, df


if __name__ == "__main__":
    plotter({"var": "spi"})
