"""mod_wsgi handler for autoplot cache needs"""

import json

from pyiem.database import get_dbconnc
from pyiem.reference import FIGSIZES_NAMES
from pyiem.webutil import iemapp

from iemweb.autoplot import data as autoplot_data
from iemweb.autoplot import import_script


def get_timing(pidx):
    """Return an average plot generation time for this app"""
    pgconn, cursor = get_dbconnc("mesosite")
    cursor.execute(
        "SELECT avg(timing) from autoplot_timing where appid = %s "
        "and valid > (now() - '7 days'::interval)",
        (pidx,),
    )
    timing = cursor.fetchone()["avg"]
    pgconn.close()
    return timing if timing is not None else -1


def generate_html(appdata):
    """Fun to be had here!"""
    html = ""
    for arg in appdata["arguments"]:
        html += f"type: {arg['type']}"
    return html


def do_html(pidx):
    """Generate the HTML interface for this autoplot."""
    response_headers = [("Content-type", "text/html")]
    mod = import_script(pidx)
    # see how we are called, finally
    appdata = mod.get_description()
    html = generate_html(appdata)
    return html, "200 OK", response_headers


def do_json(pidx):
    """Do what needs to be done for JSON requests."""
    status = "200 OK"
    if pidx == 0:
        data = autoplot_data
    else:
        try:
            timing = get_timing(pidx)
        except Exception:
            timing = -1
        mod = import_script(pidx)
        data = mod.get_description()
        defaults = data.pop("defaults", {"_r": "t", "dpi": "100"})
        data["maptable"] = hasattr(mod, "geojson")
        data["highcharts"] = hasattr(mod, "highcharts")
        data["timing[secs]"] = timing

        # Setting to None disables
        if "_r" not in defaults or defaults["_r"] is not None:
            data["arguments"].append(
                dict(
                    type="select",
                    options=FIGSIZES_NAMES,
                    name="_r",
                    default=defaults.get("_r", "t"),
                    label="Image Pixel Size @100 DPI",
                )
            )
        data["arguments"].append(
            dict(
                type="int",
                name="dpi",
                default=defaults.get("dpi", "100"),
                label="Image Resolution (DPI) (50 to 500)",
            )
        )
    output = json.dumps(data)

    response_headers = [("Content-type", "application/json")]
    return output, status, response_headers


@iemapp()
def application(environ, start_response):
    """Our Application!"""
    pidx = int(environ.get("p", 0))
    fmt = environ.get("_fmt", "json")
    if fmt == "html":
        output, status, response_headers = do_html(pidx)
    else:
        output, status, response_headers = do_json(pidx)

    start_response(status, response_headers)
    # json.dumps returns str, we need bytes here
    return [output.encode()]
