"""SPS Event Plotting Engine, not used from UI."""

# third party
import pytz
from geopandas import read_postgis
from pyiem.network import Table as NetworkTable
from pyiem.plot.geoplot import MapPlot
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound
from pyiem.reference import Z_OVERLAY2
import cartopy.crs as ccrs


TFORMAT = "%b %-d %Y %-I:%M %p %Z"


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["cache"] = 300
    desc["data"] = True
    desc[
        "description"
    ] = """This plot is not meant for interactive use, but a backend for
    SPS plots.
    """
    desc["arguments"] = [
        dict(
            type="text",
            name="pid",
            default="202012300005-KDVN-WWUS83-SPSDVN",
            label="IEM Generated 32-character Product Identifier:",
        ),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("postgis")
    ctx = get_autoplot_context(fdict, get_description())
    pid = ctx["pid"][:32]
    nt = NetworkTable("WFO")

    df = read_postgis(
        "SELECT geom, ugcs, wfo, issue, expire, landspout, waterspout, "
        f"max_hail_size, max_wind_gust, product from sps_{pid[:4]} "
        "where product_id = %s LIMIT 1",
        pgconn,
        params=(pid,),
        index_col=None,
        geom_col="geom",
    )
    if df.empty:
        raise NoDataFound("SPS Event was not found, sorry.")
    wfo = df["wfo"].values[0]
    tz = pytz.timezone(nt.sts[wfo]["tzname"])
    expire = df["expire"].dt.tz_convert(tz)[0]

    bounds = df["geom"].total_bounds

    mp = MapPlot(
        title=(
            f"{wfo} Special Weather Statement (SPS) "
            f"till {expire.strftime(TFORMAT)}"
        ),
        sector="custom",
        west=bounds[0] - 0.02,
        south=bounds[1] - 0.3,
        east=bounds[2] + (bounds[2] - bounds[0]) + 0.02,
        north=bounds[3] + 0.3,
        nocaption=True,
        twitter=True,
    )
    # Hackish
    mp.sector = "cwa"
    mp.cwa = wfo

    # Plot text on the page, hehe
    report = df["product"].values[0].replace("\r", "").replace("\003", "")
    report = report[report.find("...") : report.find("LAT...LON")]
    mp.fig.text(
        0.5,
        0.85,
        report.strip(),
        bbox=dict(fc="white", ec="k"),
        va="top",
    )

    # Tags
    msg = ""
    for col in "landspout waterspout max_hail_size max_wind_gust".split():
        val = df[col].values[0]
        if val is None:
            continue
        msg += f"{col}: {val}\n"
    if msg != "":
        mp.ax.text(
            0.01,
            0.95,
            msg,
            transform=mp.ax.transAxes,
            bbox=dict(color="white"),
        )

    ugcs = {k: 1 for k in df["ugcs"].values[0]}
    cugcs = {k: "None" for k in df["ugcs"].values[0]}
    mp.fill_ugcs(
        ugcs,
        color=cugcs,
        nocbar=True,
        plotmissing=False,
    )
    poly = df.iloc[0]["geom"]
    mp.ax.add_geometries(
        [poly],
        ccrs.PlateCarree(),
        facecolor="None",
        edgecolor="k",
        linewidth=4,
        zorder=Z_OVERLAY2,
    )
    radtime = mp.overlay_nexrad(df["issue"][0].to_pydatetime())
    mp.fig.text(
        0.5,
        0.02,
        "RADAR Valid: %s" % (radtime.astimezone(tz).strftime(TFORMAT),),
        ha="center",
    )
    mp.drawcities()
    mp.drawcounties()
    return mp.fig, df.drop("geom", axis=1)


if __name__ == "__main__":
    plotter({})
