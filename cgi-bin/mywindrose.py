"""
Generate a PNG windrose based on the CGI parameters, called from

    htdocs/sites/dyn_windrose.phtml
    htdocs/sites/windrose.phtml
"""

import datetime
from io import BytesIO
from zoneinfo import ZoneInfo

from pyiem.exceptions import BadWebRequest, IncompleteWebRequest
from pyiem.network import Table as NetworkTable
from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn
from pyiem.webutil import iemapp
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


def guess_network(station):
    """Guess the network identifier."""
    with get_dbconn("mesosite") as dbconn:
        cursor = dbconn.cursor()
        cursor.execute(
            "SELECT network from stations where id = %s and not metasite",
            (station,),
        )
        if cursor.rowcount == 0:
            raise IncompleteWebRequest(
                "Failed to guess network for given station. Please provide "
                "explicit network= to service."
            )
        res = cursor.fetchone()[0]
    return res


def get_station_info(environ):
    """Determine some metadata we need to process this form request."""
    if "station" not in environ:
        raise IncompleteWebRequest("GET parameter station= missing")
    station = environ["station"].upper()
    network = environ.get("network")
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


@iemapp()
def application(environ, start_response):
    """Query out the CGI variables"""
    dpi = int(environ.get("dpi", 100))
    if not 10 < dpi < 1000:
        raise BadWebRequest(f"Invalid dpi of {dpi} specified")
    if "sts" not in environ:
        environ["sts"] = datetime.datetime(1900, 1, 1)
        environ["ets"] = datetime.datetime(2050, 1, 1)
    dbname, network, station = get_station_info(environ)
    if "hour1" in environ and "hourlimit" in environ:
        hours = [
            int(environ["hour1"]),
        ]
    elif (
        "hour1" in environ
        and "hour2" in environ
        and "hourrangelimit" in environ
    ):
        if environ["sts"].hour > environ["ets"].hour:  # over midnight
            hours = list(range(environ["sts"].hour, 24))
            hours.extend(range(0, environ["ets"].hour))
        else:
            if environ["sts"].hour == environ["ets"].hour:
                environ["ets"] += datetime.timedelta(hours=1)
            hours = list(range(environ["sts"].hour, environ["ets"].hour))
    else:
        hours = list(range(0, 24))

    if "units" in environ and environ["units"] in ["mph", "kts", "mps", "kph"]:
        units = environ["units"]
    else:
        units = "mph"

    if "month1" in environ and "monthlimit" in environ:
        months = [
            int(environ["month1"]),
        ]
    else:
        months = list(range(1, 13))

    try:
        nsector = int(environ["nsector"])
    except Exception:
        nsector = 36

    rmax = None
    if "staticrange" in environ:
        val = int(environ["staticrange"])
        rmax = val if (1 < val < 100) else 100

    nt = NetworkTable(network, only_online=False)
    if station not in nt.sts:
        return [
            send_error(environ, "Unknown station identifier", start_response)
        ]
    tzname = nt.sts[station]["tzname"]
    if network != "RAOB":
        # Assign the station time zone to the sts and ets
        environ["sts"] = environ["sts"].replace(tzinfo=ZoneInfo(tzname))
        environ["ets"] = environ["ets"].replace(tzinfo=ZoneInfo(tzname))
    else:
        tzname = "UTC"
    bins = []
    if "bins" in environ:
        bins = [
            float(v) for v in environ.get("bins").split(",") if v.strip() != ""
        ]
        # Ensure that the bins are in ascending order and unique
        bins = sorted(list(set(bins)))
    res = windrose(
        station,
        database=dbname,
        sts=environ["sts"],
        ets=environ["ets"],
        months=months,
        hours=hours,
        units=units,
        nsector=nsector,
        justdata=("justdata" in environ),
        rmax=rmax,
        sname=nt.sts[station]["name"],
        tzname=tzname,
        level=environ.get("level", None),
        limit_by_doy=(environ.get("limit_by_doy") == "1"),
        bins=bins,
        plot_convention=environ.get("conv", "from"),
    )
    if "justdata" in environ:
        # We want text
        start_response("200 OK", [("Content-type", "text/plain")])
        return [res.encode("utf-8")]
    fmt = environ.get("fmt", "png")
    if fmt == "png":
        ct = "image/png"
    elif fmt == "pdf":
        ct = "application/pdf"
    elif fmt == "svg":
        ct = "image/svg+xml"
    else:
        return [send_error(environ, "Invalid fmt set", start_response)]
    start_response("200 OK", [("Content-type", ct)])
    bio = BytesIO()
    res.savefig(bio, format=fmt, dpi=dpi)
    return [bio.getvalue()]
