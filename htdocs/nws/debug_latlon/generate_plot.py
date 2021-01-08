"""Generate a pretty plot, please."""
# stdlib
import os
import json
import tempfile

# third party
from pyiem.plot.use_agg import plt
from pyiem.plot import fitbox
from pyiem.reference import TWITTER_RESOLUTION_INCH
from pyiem.nws.product import str2polygon
from pyiem.util import utc
import geopandas as gpd
import matplotlib.patheffects as PathEffects
from paste.request import parse_formvars


def plot_poly(fig, poly, fields):
    """Add to axes."""
    ax = fig.add_axes([0.15, 0.15, 0.7, 0.7])
    title = fields.get("title", "")[:120]
    title += "\npolygon.is_valid: %s linearring.is_valid: %s" % (
        poly.is_valid,
        poly.exterior.is_valid,
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


def process(fields):
    """Make something pretty."""
    text = fields.get("text")
    text = text.replace("LAT...LON", "").replace("\n", " ")
    poly = str2polygon(text)
    plt.close()
    fig = plt.figure(figsize=TWITTER_RESOLUTION_INCH)

    res = {}
    if poly is not None:
        plot_poly(fig, poly, fields)
        res["geojson"] = gpd.GeoSeries([poly]).__geo_interface__

    fig.text(0.01, 0.01, f"Generated: {utc().strftime('%Y-%m-%dT%H:%M:%SZ')}")
    with tempfile.NamedTemporaryFile() as tmpfd:
        name = os.path.basename(tmpfd.name)
        fig.savefig(f"/var/webtmp/{name}.png")
    plt.close()
    res["imgurl"] = f"/tmp/{name}.png"
    return res


def application(environ, start_response):
    """The App."""
    fields = parse_formvars(environ)
    res = process(fields)
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [json.dumps(res).encode("ascii")]
