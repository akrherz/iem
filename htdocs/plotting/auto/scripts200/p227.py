"""
This plot is not meant for interactive use, but a backend for
NWEM plots.
"""
from zoneinfo import ZoneInfo

# third party
import requests
from geopandas import read_postgis
from pyiem.exceptions import NoDataFound
from pyiem.network import Table as NetworkTable
from pyiem.plot.geoplot import MapPlot
from pyiem.reference import LATLON, Z_OVERLAY2, prodDefinitions
from pyiem.util import LOG, get_autoplot_context, get_sqlalchemy_conn
from sqlalchemy import text

TFORMAT = "%b %-d %Y %-I:%M %p %Z"
WFOCONV = {"JSJ": "SJU"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "cache": 3600, "data": True}
    desc["defaults"] = {"_r": "t"}
    desc["arguments"] = [
        dict(
            type="text",
            name="pid",
            default="202302031255-KLWX-FZUS71-MWSLWX-RRA",
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


def get_text(product_id):
    """get the raw text."""
    res = "Text Unavailable, Sorry."
    uri = f"https://mesonet.agron.iastate.edu/api/1/nwstext/{product_id}"
    try:
        req = requests.get(uri, timeout=5)
        if req.status_code == 200:
            res = req.content.decode("ascii", "ignore").replace("\001", "")
            res = "\n".join(text.replace("\r", "").split("\n")[5:])
    except Exception as exp:
        LOG.info(exp)

    return res


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    pid = ctx["pid"][:35]
    segnum = ctx["segnum"]
    nt = NetworkTable("WFO")

    # Compute a population estimate
    popyear = max([int(pid[:4]) - int(pid[:4]) % 5, 2000])
    with get_sqlalchemy_conn("postgis") as conn:
        df = read_postgis(
            text(
                f"""
                with geopop as (
                    select sum(population) as pop from text_products s,
                    gpw{popyear} g WHERE s.product_id = :pid and
                    ST_Contains(s.geom, g.geom)
                )
                SELECT geom, issue, expire,
                coalesce(pop, 0) as pop
                from text_products, geopop where product_id = :pid
                """
            ),
            conn,
            params={"pid": pid, "segnum": segnum},
            index_col=None,
            geom_col="geom",
        )
    if df.empty:
        raise NoDataFound("NWEM Event was not found, sorry.")
    row = df.iloc[0]
    wfo = pid.split("-")[1][1:]
    tzname = nt.sts.get(wfo, {}).get("tzname")
    if tzname is None:
        tzname = nt.sts.get(f"P{wfo}", {}).get("tzname")
        if tzname is None:
            tzname = "UTC"
    tz = ZoneInfo(tzname)
    expire = df["expire"].dt.tz_convert(tz)[0]

    bounds = row["geom"].bounds
    population = row["pop"]
    stextra = " for Polygon" if not row["geom"].is_empty else ""
    pil = pid.split("-")[3][:3]
    label = prodDefinitions.get(pil, "")
    mp = MapPlot(
        apctx=ctx,
        title=(f"{wfo} {label} ({pil}) " f"till {expire.strftime(TFORMAT)}"),
        subtitle=(f"Estimated {popyear} Population{stextra}: {population:,}"),
        sector="spherical_mercator",
        west=bounds[0] - 0.02,
        south=bounds[1] - 0.3,
        east=bounds[2] + (bounds[2] - bounds[0]) + 0.02,
        north=bounds[3] + 0.3,
        nocaption=True,
    )

    # Plot text on the page, hehe
    report = (
        get_text(pid)
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

    if not row["geom"].is_empty:
        mp.panels[0].add_geometries(
            [row["geom"]],
            LATLON,
            facecolor="None",
            edgecolor="k",
            linewidth=4,
            zorder=Z_OVERLAY2,
        )

    mp.drawcounties()
    return mp.fig, df.drop("geom", axis=1)


if __name__ == "__main__":
    plotter({})
