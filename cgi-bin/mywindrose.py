"""
Generate a PNG windrose based on the CGI parameters, called from

    htdocs/sites/dyn_windrose.phtml
    htdocs/sites/windrose.phtml
"""
import datetime
from io import BytesIO
from zoneinfo import ZoneInfo

import numpy
from paste.request import parse_formvars
from pyiem.network import Table as NetworkTable
from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn
from pyiem.windrose_utils import windrose


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
    start_response("200 OK", [("Content-type", ct)])
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


def guess_network(station):
    """Guess the network identifier."""
    with get_dbconn("mesosite") as dbconn:
        cursor = dbconn.cursor()
        cursor.execute(
            "SELECT network from stations where id = %s and not metasite",
            (station,),
        )
        if cursor.rowcount == 0:
            raise ValueError(
                "Failed to guess network for given station. Please provide "
                "explicit network= to service."
            )
        res = cursor.fetchone()[0]
    return res


def get_station_info(form):
    """Determine some metadata we need to process this form request."""
    station = form["station"].upper()
    network = form.get("network")
    if network is None:
        network = guess_network(station)
    dbname = "asos"
    if network in ("KCCI", "KELO", "KIMT"):
        dbname = "snet"
    elif network.find("_RWIS") > 0:
        dbname = "rwis"
    elif network in ("ISUSM", "ISUAG"):
        dbname = "isuag"
    elif network == "RAOB":
        dbname = "postgis"
    elif network.find("_DCP") > 0:
        dbname = "hads"

    return dbname, network, station


def application(environ, start_response):
    """Query out the CGI variables"""
    form = parse_formvars(environ)
    try:
        sts, ets = get_times(form)
        dbname, network, station = get_station_info(form)
    except Exception as exp:
        return [send_error(form, str(exp), start_response)]
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

    try:
        nsector = int(form["nsector"])
    except Exception:
        nsector = 36

    rmax = None
    if "staticrange" in form and form["staticrange"] == "1":
        rmax = 100

    nt = NetworkTable(network, only_online=False)
    tzname = nt.sts[station]["tzname"]
    if network != "RAOB":
        # Assign the station time zone to the sts and ets
        sts = sts.replace(tzinfo=ZoneInfo(tzname))
        ets = ets.replace(tzinfo=ZoneInfo(tzname))
    else:
        tzname = "UTC"
    bins = []
    if "bins" in form:
        bins = [
            float(v) for v in form.get("bins").split(",") if v.strip() != ""
        ]
    res = windrose(
        station,
        database=dbname,
        sts=sts,
        ets=ets,
        months=months,
        hours=hours,
        units=units,
        nsector=nsector,
        justdata=("justdata" in form),
        rmax=rmax,
        sname=nt.sts[station]["name"],
        tzname=tzname,
        level=form.get("level", None),
        limit_by_doy=(form.get("limit_by_doy") == "1"),
        bins=bins,
        plot_convention=form.get("conv", "from"),
    )
    if "justdata" in form:
        # We want text
        start_response("200 OK", [("Content-type", "text/plain")])
        return [res.encode("utf-8")]
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
