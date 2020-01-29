"""
Generate a PNG windrose based on the CGI parameters, called from

    htdocs/sites/dyn_windrose.phtml
    htdocs/sites/windrose.phtml
"""
from io import BytesIO
import datetime

import numpy
from paste.request import parse_formvars
from pyiem.plot.use_agg import plt
from pyiem.windrose_utils import windrose
from pyiem.network import Table as NetworkTable


def send_error(form, msg, start_response):
    """Abort, abort"""
    fmt = form.get("fmt", "png")
    if fmt == "png":
        ct = "image/png"
    elif fmt == "pdf":
        ct = "application/pdf"
    elif fmt == "svg":
        ct = "image/svg+xml"
    else:
        start_response("200 OK", [("Content-type", "text/plain")])
        return msg.encode("ascii")

    fig, ax = plt.subplots(1, 1)
    ax.text(0.5, 0.5, msg, ha="center")
    start_response("200 OK", [("Content-type", "%s" % (ct,))])
    bio = BytesIO()
    fig.savefig(bio, format=fmt)
    return bio.getvalue()


def get_times(form):
    """get the times of interest"""
    if (
        "year1" in form
        and "year2" in form
        and "month1" in form
        and "month2" in form
        and "day1" in form
        and "day2" in form
        and "hour1" in form
        and "hour2" in form
        and "minute1" in form
        and "minute2" in form
    ):
        sts = datetime.datetime(
            int(form["year1"]),
            int(form["month1"]),
            int(form["day1"]),
            int(form["hour1"]),
            int(form["minute1"]),
        )
        ets = datetime.datetime(
            int(form["year2"]),
            int(form["month2"]),
            int(form["day2"]),
            int(form["hour2"]),
            int(form["minute2"]),
        )
    else:
        sts = datetime.datetime(1900, 1, 1)
        ets = datetime.datetime(2050, 1, 1)

    return sts, ets


def application(environ, start_response):
    """ Query out the CGI variables"""
    form = parse_formvars(environ)
    try:
        sts, ets = get_times(form)
    except Exception:
        return [
            send_error(
                form,
                "Invalid Times Selected, please try again",
                start_response,
            )
        ]

    if "hour1" in form and "hourlimit" in form:
        hours = numpy.array((int(form["hour1"]),))
    elif "hour1" in form and "hour2" in form and "hourrangelimit" in form:
        if sts.hour > ets.hour:  # over midnight
            hours = numpy.arange(sts.hour, 24)
            hours = numpy.append(hours, numpy.arange(0, ets.hour))
        else:
            if sts.hour == ets.hour:
                ets += datetime.timedelta(hours=1)
            hours = numpy.arange(sts.hour, ets.hour)
    else:
        hours = numpy.arange(0, 24)

    if "units" in form and form["units"] in ["mph", "kts", "mps", "kph"]:
        units = form["units"]
    else:
        units = "mph"

    if "month1" in form and "monthlimit" in form:
        months = numpy.array((int(form["month1"]),))
    else:
        months = numpy.arange(1, 13)

    database = "asos"
    if form["network"] in ("KCCI", "KELO", "KIMT"):
        database = "snet"
    elif form["network"] in ("IA_RWIS",):
        database = "rwis"
    elif form["network"] in ("ISUSM",):
        database = "isuag"
    elif form["network"] in ("RAOB",):
        database = "postgis"
    elif form["network"].find("_DCP") > 0:
        database = "hads"

    try:
        nsector = int(form["nsector"])
    except Exception:
        nsector = 36

    rmax = None
    if "staticrange" in form and form["staticrange"] == "1":
        rmax = 100

    nt = NetworkTable(form["network"], only_online=False)
    bins = []
    if "bins" in form:
        bins = [float(v) for v in form.get("bins").split(",")]
        bins.insert(0, 0)
    res = windrose(
        form["station"],
        database=database,
        sts=sts,
        ets=ets,
        months=months,
        hours=hours,
        units=units,
        nsector=nsector,
        justdata=("justdata" in form),
        rmax=rmax,
        sname=nt.sts[form["station"]]["name"],
        level=form.get("level", None),
        bins=bins,
    )
    if "justdata" in form:
        # We want text
        start_response("200 OK", [("Content-type", "text/plain")])
        return [res.encode("ascii")]
    fmt = form.get("fmt", "png")
    if fmt == "png":
        ct = "image/png"
    elif fmt == "pdf":
        ct = "application/pdf"
    elif fmt == "svg":
        ct = "image/svg+xml"
    else:
        return [send_error(form, "Invalid fmt set", start_response)]
    start_response("200 OK", [("Content-type", ct)])
    bio = BytesIO()
    res.savefig(bio, format=fmt, dpi=int(form.get("dpi", 100)))
    return [bio.getvalue()]
