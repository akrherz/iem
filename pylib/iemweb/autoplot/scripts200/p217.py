"""
This plot is not meant for interactive use, but a backend for SPS plots. A more
approachable frontend is to visit the <a href="/wx/afos/list.phtml">NWS Text
by WFO</a> page and click on the SPS product you are interested in.
"""

from zoneinfo import ZoneInfo

import httpx
from geopandas import read_postgis
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.network import Table as NetworkTable
from pyiem.plot.geoplot import MapPlot
from pyiem.reference import LATLON, Z_OVERLAY2
from pyiem.util import LOG, get_autoplot_context
from sqlalchemy import text

TFORMAT = "%b %-d %Y %-I:%M %p %Z"
UNITS = {
    "max_hail_size": "inch",
    "max_wind_gust": "MPH",
}
WFOCONV = {"JSJ": "SJU"}
PDICT3 = {
    "on": "Overlay NEXRAD Mosaic",
    "auto": "Let autoplot decide when to include NEXRAD overlay",
    "off": "No NEXRAD Mosaic Please",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 3600}
    desc["defaults"] = {"_r": "t"}
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
        {
            "type": "select",
            "name": "n",
            "default": "auto",
            "label": "Should a NEXRAD Mosaic by overlain:",
            "options": PDICT3,
        },
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    pid = ctx["pid"][:35]
    if len(pid) < 30 or not pid[0].isdigit():
        raise NoDataFound("Invalid pid provided.")
    segnum = ctx["segnum"]
    nt = NetworkTable("WFO")

    # Compute a population estimate
    popyear = max([int(pid[:4]) - int(pid[:4]) % 5, 2000])
    with get_sqlalchemy_conn("postgis") as conn:
        df = read_postgis(
            text(
                f"""
                with geopop as (
                    select sum(population) as pop from sps_{pid[:4]} s,
                    gpw{popyear} g WHERE s.product_id = :pid and
                    ST_Contains(s.geom, g.geom) and segmentnum = :segnum
                )
                SELECT geom, ugcs, wfo, issue, expire, landspout, waterspout,
                max_hail_size, max_wind_gust, segmentnum,
                coalesce(pop, 0) as pop
                from sps_{pid[:4]}, geopop where product_id = :pid
                and segmentnum = :segnum
                """
            ),
            conn,
            params={"pid": pid, "segnum": segnum},
            index_col=None,
            geom_col="geom",
        )
    if df.empty:
        raise NoDataFound("SPS Event was not found, sorry.")
    row = df.iloc[0]
    wfo = row["wfo"]
    tzname = nt.sts.get(wfo, {}).get("tzname")
    if tzname is None:
        tzname = nt.sts.get(f"P{wfo}", {}).get("tzname")
        if tzname is None:
            tzname = "UTC"
    tz = ZoneInfo(tzname)
    expire = df["expire"].dt.tz_convert(tz)[0]
    is_fwx = False
    if row["geom"].is_empty:
        # Need to go looking for UGCs to compute the bounds
        # Can a SPS be issued for Fire Weather zones? source = 'fz'
        with get_sqlalchemy_conn("postgis") as conn:
            for source in ["z", "fz", "mz"]:
                ugcdf = read_postgis(
                    text(
                        f"""
                        SELECT simple_geom, ugc, gpw_population_{popyear}
                        as pop from ugcs where wfo = :wfo and ugc = ANY(:ugcs)
                        and (end_ts is null or end_ts > :expire) and
                        source = :source
                        """
                    ),
                    conn,
                    params={
                        "wfo": WFOCONV.get(wfo, wfo),
                        "ugcs": row["ugcs"],
                        "expire": expire,
                        "source": source,
                    },
                    geom_col="simple_geom",
                )
                if not ugcdf.empty:
                    if source == "fz":
                        is_fwx = True
                    break
            if ugcdf.empty:
                raise NoDataFound("No UGCs found for this SPS, sorry.")
        bounds = ugcdf["simple_geom"].total_bounds
        population = ugcdf["pop"].sum()
    else:
        bounds = row["geom"].bounds
        population = row["pop"]
    pp = "Missing" if population <= 0 else f"{population:,}"
    stextra = " for Polygon" if not row["geom"].is_empty else ""
    mp = MapPlot(
        apctx=ctx,
        title=(
            f"{wfo} Special Weather Statement (SPS) "
            f"till {expire.strftime(TFORMAT)}"
        ),
        subtitle=(f"Estimated {popyear} Population{stextra}: {pp}"),
        sector="spherical_mercator",
        west=bounds[0] - 0.02,
        south=bounds[1] - 0.3,
        east=bounds[2] + (bounds[2] - bounds[0]) + 0.02,
        north=bounds[3] + 0.3,
        nocaption=True,
    )
    # Hackish
    mp.sector = "cwa"
    mp.cwa = wfo

    # Plot text on the page, hehe
    try:
        with httpx.Client() as client:
            resp = client.get(
                f"http://mesonet.agron.iastate.edu/api/1/nwstext/{pid}",
                timeout=10,
            )
        resp.raise_for_status()
        report = resp.text
    except Exception as exp:
        LOG.exception(exp)
        report = ""
    report = (
        report.split("$$")[segnum]
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
        mp.panels[0].add_geometries(
            [row["geom"]],
            LATLON,
            facecolor="None",
            edgecolor="k",
            linewidth=4,
            zorder=Z_OVERLAY2,
        )
    else:
        # disable RADAR if auto and since we have no polygon
        if ctx["n"] == "auto":
            ctx["n"] = "off"
        mp.fill_ugcs(
            ugcs,
            ec="r",
            fc="None",
            lw=2,
            draw_colorbar=False,
            plotmissing=False,
            zorder=Z_OVERLAY2 - 1,
            is_firewx=is_fwx,
        )
    if ctx["n"] != "off":
        prod = "N0Q" if df["issue"][0].year > 2010 else "N0R"
        radtime = mp.overlay_nexrad(
            df["issue"][0].to_pydatetime(), product=prod
        )
        if radtime is not None:
            mp.fig.text(
                0.65,
                0.02,
                f"RADAR Valid: {radtime.astimezone(tz).strftime(TFORMAT)}",
                ha="center",
            )
    mp.drawcounties()
    return mp.fig, df.drop(columns=["geom"])
