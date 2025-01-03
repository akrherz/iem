"""..title:: Tool to debug NWS LAT...LON polygons

Simple tool to help debug NWS LAT...LON polygons.

Changelog
---------

- 2025-01-03: Updated to use pydantic for input validation

Example Requests
----------------

The urlencoding here is a bit ugly, but alas.

https://mesonet.agron.iastate.edu/nws/debug_latlon/generate_plot.py?\
text=LAT...LON%203920%208402%203920%208400%203918%208400%203918%208402%20%0A\
&title=Test

"""

# stdlib
import json
import os
import tempfile

import geopandas as gpd
import matplotlib.patheffects as PathEffects
from matplotlib.figure import Figure
from pydantic import Field
from pyiem.nws.product import str2polygon
from pyiem.plot import fitbox
from pyiem.plot.use_agg import plt
from pyiem.reference import ISO8601, TWITTER_RESOLUTION_INCH
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """See how we are called."""

    text: str = Field(..., description="The text to parse", min_length=1)
    title: str = Field(None, description="Optional title for the plot")


def plot_poly(fig: Figure, poly, environ):
    """Add to axes."""
    ax = fig.add_axes((0.15, 0.15, 0.7, 0.7))
    title = environ["title"] if environ["title"] else "No Title Provided"
    title = title[:120]
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
    text = text.replace("LAT...LON", "").replace("\n", " ")
    # Add extra whitespace to account for upstream issues
    poly = str2polygon(text + " \n")
    plt.close()
    fig = plt.figure(figsize=TWITTER_RESOLUTION_INCH)

    res = {}
    if poly is not None:
        plot_poly(fig, poly, environ)
        res["geojson"] = gpd.GeoSeries([poly]).__geo_interface__

    fig.text(0.01, 0.01, f"Generated: {utc().strftime(ISO8601)}")
    with tempfile.NamedTemporaryFile() as tmpfd:
        name = os.path.basename(tmpfd.name)
        fig.savefig(f"/var/webtmp/{name}.png")
    plt.close()
    res["imgurl"] = f"/tmp/{name}.png"
    return res


@iemapp(help=__doc__, schema=Schema)
def application(environ, start_response):
    """The App."""
    res = process(environ)
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return json.dumps(res)
