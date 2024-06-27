"""Map of NEXRAD Level III Latencies over NOAAPort or Realtime-ness.

<p>This autoplot has two modes of operation attempting to address two distinct
data availability questions.</p>

<ol>
  <li><i>Realtime-ness:</i> This is a measure of the difference between a given
  timestamp and the most receipt receipt of a Level III N0B product.  Due
  to VCP timing, a value below 10 minutes doesn't have much meaning.</li>
  <li><i>Latency:</i> This is a measure of the difference between a given
  timestamp and the WMO header timestamp of the N0B product.</li>
</ol>

<p>The backend database only contains
three days worth of data, so this app only runs over a very small interval of
time.  In general, the precision of this estimate is +/- a minute or so.</p>

<p>An intended usage of this autoplot is to embed it into a dashboard.  Here's
the HTML example to make this magic happen. The plot has 3 minutes of caching
to keep from overloading the server with refresh requests.</p>

<pre>
&lt;img src="%BASE%/mode:realtime.png" alt="Realtime-ness" &gt;
&lt;img src="%BASE%/mode:latency.png" alt="Latency" &gt;
</pre>

<p>Note: If a RADAR has been offline for 12 or more hours, it will not
appear plotted on this map.
"""

import datetime

import pandas as pd
from matplotlib.colors import BoundaryNorm, ListedColormap
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.network import Table as NetworkTable
from pyiem.plot.geoplot import MapPlot
from pyiem.util import get_autoplot_context, utc
from sqlalchemy import text

PDICT = {"realtime": "Realtime-ness", "latency": "Latency"}


def get_description():
    """Return a dict describing how to call this plotter"""
    uri = "https://mesonet.agron.iastate.edu/plotting/auto/plot/254"
    return {
        "description": __doc__.replace("%BASE%", uri),
        "data": True,
        "cache": 180,
        "arguments": [
            {
                "type": "select",
                "name": "mode",
                "default": "latency",
                "options": PDICT,
                "label": "Select Plot Mode:",
            },
            {
                "type": "int",
                "name": "offset",
                "default": 0,
                "label": (
                    "Prior number of minutes from now to produce map for "
                    "(lt 1440*2 minutes)"
                ),
            },
        ],
    }


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    ts = utc() - datetime.timedelta(minutes=ctx["offset"])
    nt = NetworkTable("NEXRAD")
    with get_sqlalchemy_conn("id3b") as conn:
        latency = pd.read_sql(
            text("""
            with data as (
            select substr(awips_id, 4, 3) as nexrad,
            entered_at, wmo_valid_at, entered_at - wmo_valid_at as latency,
            :ts - wmo_valid_at as realtime,
            rank() OVER (PARTITION by substr(awips_id, 4, 3)
                 ORDER by wmo_valid_at desc) from ldm_product_log where
            valid_at < :ts and valid_at > :ts2 and
            substr(awips_id, 1, 3) = 'N0B')
            select * from data where rank = 1
            """),
            conn,
            params={"ts": ts, "ts2": ts - pd.Timedelta("12 hours")},
        )
    if latency.empty:
        raise NoDataFound("No Data Found.")
    latency = latency.drop(columns=["rank"]).sort_values(
        ctx["mode"], ascending=True
    )
    latency["latency"] = latency["latency"].dt.total_seconds() / 60.0
    latency["realtime"] = latency["realtime"].dt.total_seconds() / 60.0
    latency["lon"] = latency["nexrad"].apply(lambda x: nt.sts[x]["lon"])
    latency["lat"] = latency["nexrad"].apply(lambda x: nt.sts[x]["lat"])
    for col in ["latency", "realtime"]:
        latency.loc[latency[col] < 0][col] = 0
    mp = MapPlot(
        sector="nws",
        title=f"IEM Estimated NEXRAD III {PDICT[ctx['mode']]} over NOAAPort",
        subtitle=f"{ts:%H%MZ %d %b %Y} Based on NOAAPort N0B receipt.",
        apctx=ctx,
        nocaption=True,
    )
    colors = [
        "darkgreen",
        "mediumseagreen",
        "lightgreen",
        "orange",
    ]
    cmap = ListedColormap(colors)
    cmap.set_under("white")
    cmap.set_over("red")
    levels = [0, 5, 15, 30, 60]
    if ctx["mode"] == "realtime":
        levels = [0, 10, 15, 20, 60]
    norm = BoundaryNorm(levels, cmap.N)
    latency["color"] = [cmap(norm(x)) for x in latency[ctx["mode"]].values]

    mp.plot_values(
        latency["lon"].to_list(),
        latency["lat"].to_list(),
        latency["nexrad"].to_list(),
        fmt="%s",
        color="white",
        backgroundcolor=latency["color"].to_list(),
        textoutlinewidth=0,
        labelbuffer=0,
        textsize=10,
    )
    mp.draw_colorbar(
        levels,
        cmap,
        norm,
        spacing="proportional",
        title=f"{PDICT[ctx['mode']]} Minutes",
        extend="max",
    )

    return mp.fig, latency.drop(columns=["color"])
