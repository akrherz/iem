"""SPS Event Plotting Engine, not used from UI."""

# third party
import pytz
from geopandas import read_postgis
from pyiem.network import Table as NetworkTable
from pyiem.plot.geoplot import MapPlot
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound
from pyiem.reference import Z_OVERLAY2, LATLON


TFORMAT = "%b %-d %Y %-I:%M %p %Z"
UNITS = {
    "max_hail_size": "inch",
    "max_wind_gust": "MPH",
}
WFOCONV = {"JSJ": "SJU"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["cache"] = 3600
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
            label="IEM generated up to 35 char product identifier:",
        ),
        dict(
            type="int",
            default=0,
            name="segnum",
            label="Product Segment Number (starts at 0):",
        ),
    ]
    return desc


def proxy(mp):
    """TODO removeme once pyiem updates"""
    if hasattr(mp, "panels"):
        return mp.panels[0]
    return mp.ax


def plotter(fdict):
    """Go"""
    pgconn = get_dbconn("postgis")
    ctx = get_autoplot_context(fdict, get_description())
    pid = ctx["pid"][:35]
    segnum = ctx["segnum"]
    nt = NetworkTable("WFO")

    df = read_postgis(
        "SELECT geom, ugcs, wfo, issue, expire, landspout, waterspout, "
        "max_hail_size, max_wind_gust, product, segmentnum "
        f"from sps_{pid[:4]} where product_id = %s",
        pgconn,
        params=(pid,),
        index_col=None,
        geom_col="geom",
    )
    if df.empty:
        raise NoDataFound("SPS Event was not found, sorry.")
    df2 = df[df["segmentnum"] == segnum]
    if df2.empty:
        raise NoDataFound("SPS Event Segment was not found, sorry.")
    row = df2.iloc[0]
    wfo = row["wfo"]
    tzname = nt.sts.get(wfo, {}).get("tzname")
    if tzname is None:
        tzname = nt.sts.get(f"P{wfo}", {}).get("tzname")
        if tzname is None:
            tzname = "UTC"
    tz = pytz.timezone(tzname)
    expire = df["expire"].dt.tz_convert(tz)[0]

    if row["geom"].is_empty:
        # Need to go looking for UGCs to compute the bounds
        ugcdf = read_postgis(
            "SELECT simple_geom, ugc from ugcs where wfo = %s and ugc in %s "
            "and end_ts is null",
            pgconn,
            params=(WFOCONV.get(wfo, wfo), tuple(row["ugcs"])),
            geom_col="simple_geom",
        )
        bounds = ugcdf["simple_geom"].total_bounds
    else:
        bounds = row["geom"].bounds
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
        twitter=True,
    )
    # Hackish
    mp.sector = "cwa"
    mp.cwa = wfo

    # Plot text on the page, hehe
    report = (
        row["product"]
        .split("$$")[segnum]
        .replace("\r", "")
        .replace("\003", "")
        .replace("\001", "")
        .replace("$$", "  ")
    )
    pos = report.find("...")
    if pos == -1:
        pos = 0
    report = report[pos : report.find("LAT...LON")]
    mp.fig.text(
        0.5,
        0.85,
        report.strip(),
        bbox=dict(fc="white", ec="k"),
        va="top",
    )

    # Tags
    msg = []
    for col in "landspout waterspout max_hail_size max_wind_gust".split():
        val = row[col]
        if val is None:
            continue
        msg.append(f"{col.replace('_', ' ')}: {val} {UNITS.get(col)}")
    if msg:
        mp.ax.text(
            0.01,
            0.95,
            "\n".join(msg),
            transform=mp.ax.transAxes,
            bbox=dict(color="white"),
            va="top",
            zorder=Z_OVERLAY2 + 100,
        )

    ugcs = {k: 1 for k in row["ugcs"]}
    if not row["geom"].is_empty:
        proxy(mp).add_geometries(
            [row["geom"]],
            LATLON,
            facecolor="None",
            edgecolor="k",
            linewidth=4,
            zorder=Z_OVERLAY2,
        )
    else:
        mp.fill_ugcs(
            ugcs,
            ec="r",
            fc="None",
            lw=2,
            nocbar=True,
            plotmissing=False,
            zorder=Z_OVERLAY2 - 1,
        )
    prod = "N0Q" if df["issue"][0].year > 2010 else "N0R"
    radtime = mp.overlay_nexrad(df["issue"][0].to_pydatetime(), product=prod)
    if radtime is not None:
        mp.fig.text(
            0.65,
            0.02,
            f"RADAR Valid: {radtime.astimezone(tz).strftime(TFORMAT)}",
            ha="center",
        )
    mp.drawcities()
    mp.drawcounties()
    return mp.fig, df.drop("geom", axis=1)


if __name__ == "__main__":
    plotter({"pid": "202001111306-TJSJ-WWCA82-SPSSJU", "segnum": 0})
