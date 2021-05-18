"""mod_wsgi handler for autoplot cache needs"""
import sys
import importlib
import os
import json

from paste.request import parse_formvars
from pyiem.util import get_dbconn

BASEDIR, WSGI_FILENAME = os.path.split(__file__)


def get_timing(pidx):
    """Return an average plot generation time for this app"""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    cursor.execute(
        "SELECT avg(timing) from autoplot_timing where appid = %s "
        "and valid > (now() - '7 days'::interval)",
        (pidx,),
    )
    timing = cursor.fetchone()[0]
    return timing if timing is not None else -1


def generate_html(appdata):
    """Fun to be had here!"""
    html = ""
    for arg in appdata["arguments"]:
        html += "type: %s" % (arg["type"],)
    return html


def do_html(pidx):
    """Generate the HTML interface for this autoplot."""
    response_headers = [("Content-type", "text/html")]
    name = get_script_name(pidx)
    if not os.path.isfile(name):
        sys.stderr.write("autoplot/meta 404 %s\n" % (name,))
        status = "404 Not Found"
        output = ""
        return output.encode(), status, response_headers
    loader = importlib.machinery.SourceFileLoader(f"p{pidx}", name)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    # see how we are called, finally
    appdata = mod.get_description()
    html = generate_html(appdata)
    return html, "200 OK", response_headers


def get_script_name(pidx):
    """Return where this script resides, so we can load it!"""
    suffix = ""
    if pidx >= 200:
        suffix = "200"
    elif pidx >= 100:
        suffix = "100"
    return f"{BASEDIR}/scripts{suffix}/p{pidx}.py"


def do_json(pidx):
    """Do what needs to be done for JSON requests."""
    status = "200 OK"
    if pidx == 0:
        name = f"{BASEDIR}/scripts/__init__.py"
        loader = importlib.machinery.SourceFileLoader("scripts", name)
        spec = importlib.util.spec_from_loader(loader.name, loader)
        mod = importlib.util.module_from_spec(spec)
        loader.exec_module(mod)
        data = mod.data
    else:
        name = get_script_name(pidx)
        if not os.path.isfile(name):
            sys.stderr.write("autoplot/meta 404 %s\n" % (name,))
            status = "404 Not Found"
            output = ""
            response_headers = [
                ("Content-type", "application/json"),
                ("Content-Length", str(len(output))),
            ]
            return output, status, response_headers
        try:
            timing = get_timing(pidx)
        except Exception:
            timing = -1
        loader = importlib.machinery.SourceFileLoader(f"p{pidx}", name)
        spec = importlib.util.spec_from_loader(loader.name, loader)
        mod = importlib.util.module_from_spec(spec)
        loader.exec_module(mod)
        data = mod.get_description()
        data["maptable"] = hasattr(mod, "geojson")
        data["highcharts"] = hasattr(mod, "highcharts")
        data["report"] = hasattr(mod, "report")
        data["timing[secs]"] = timing

        # Defaults
        data["arguments"].append(
            dict(
                type="int",
                name="dpi",
                default="100",
                label="Image Resolution (DPI)",
            )
        )
    output = json.dumps(data)

    response_headers = [("Content-type", "application/json")]
    return output, status, response_headers


def application(environ, start_response):
    """Our Application!"""
    fields = parse_formvars(environ)
    pidx = int(fields.get("p", 0))
    fmt = fields.get("_fmt", "json")
    if fmt == "html":
        output, status, response_headers = do_html(pidx)
    else:
        output, status, response_headers = do_json(pidx)

    start_response(status, response_headers)
    # json.dumps returns str, we need bytes here
    return [output.encode()]


# from paste.exceptions.errormiddleware import ErrorMiddleware
# application = ErrorMiddleware(application, debug=True)
