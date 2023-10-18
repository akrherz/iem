"""Generate a pretty plot, please."""
# stdlib
import json
import os
import tempfile

import geopandas as gpd
import matplotlib.patheffects as PathEffects
from pyiem.exceptions import IncompleteWebRequest
from pyiem.nws.product import str2polygon
from pyiem.plot import fitbox
from pyiem.plot.use_agg import plt
from pyiem.reference import TWITTER_RESOLUTION_INCH
from pyiem.util import utc
from pyiem.webutil import iemapp


def plot_poly(fig, poly, environ):
    """Add to axes."""
    ax = fig.add_axes([0.15, 0.15, 0.7, 0.7])
    title = environ.get("title", "")[:120]
    title += (
        f"\npolygon.is_valid: {poly.is_valid} "
        f"linearring.is_valid: {poly.exterior.is_valid}"
    )
    fitbox(fig, title, 0.15, 0.9, 0.9, 0.95)

    X, Y = poly.exterior.xy
    for i in range(len(X) - 1):
        ax.arrow(
            X[i],
            Y[i],
            X[i + 1] - X[i],
            Y[i + 1] - Y[i],
            head_width=0.006,
            width=0.001,
            length_includes_head=True,
            color="skyblue",
        )
        txt = ax.text(
            X[i],
            Y[i],
            str(i + 1),
            va="center",
            ha="center",
            color="red",
            fontsize=20,
        )
        txt.set_path_effects(
            [PathEffects.withStroke(linewidth=2, foreground="white")]
        )
    ax.set_xlim(min(X) - 0.02, max(X) + 0.02)
    ax.set_ylim(min(Y) - 0.02, max(Y) + 0.02)
    ax.set_ylabel(r"Latitude [$^\circ$N]", fontsize=18)
    ax.set_xlabel(r"Longitude [$^\circ$E]", fontsize=18)
    ax.grid(True)
    for tick in ax.get_xticklabels():
        tick.set_rotation(45)


def process(environ):
    """Make something pretty."""
    text = environ.get("text")
    if text is None:
        raise IncompleteWebRequest("GET text= parameter is missing")
    text = text.replace("LAT...LON", "").replace("\n", " ")
    # Add extra whitespace to account for upstream issues
    poly = str2polygon(text + " \n")
    plt.close()
    fig = plt.figure(figsize=TWITTER_RESOLUTION_INCH)

    res = {}
    if poly is not None:
        plot_poly(fig, poly, environ)
        res["geojson"] = gpd.GeoSeries([poly]).__geo_interface__

    fig.text(0.01, 0.01, f"Generated: {utc().strftime('%Y-%m-%dT%H:%M:%SZ')}")
    with tempfile.NamedTemporaryFile() as tmpfd:
        name = os.path.basename(tmpfd.name)
        fig.savefig(f"/var/webtmp/{name}.png")
    plt.close()
    res["imgurl"] = f"/tmp/{name}.png"
    return res


@iemapp()
def application(environ, start_response):
    """The App."""
    res = process(environ)
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [json.dumps(res).encode("ascii")]
