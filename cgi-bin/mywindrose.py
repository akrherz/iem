""".. title:: Windrose Plotting/Data Service

Documentation for /cgi-bin/windrose.py
--------------------------------------

This service returns a windrose plot or data table.  There's a lot of options
here to consider, so perhaps some examples are in order.

Example Usage
-------------

Plot a windrose for Ames, IA for the month of June 2021:

https://mesonet.agron.iastate.edu/cgi-bin/mywindrose.py?station=AMW&network=IA_ASOS&year1=2021&month1=6&day1=1&year2=2021&month2=6&day2=30&hour2=23&fmt=png

Changelog
---------

- `2024-03-25`
    The backend was migrated to use a pydantic schema, which will
    generate more structured error messages when the user provides invalid
    input.
- `2024-03-25`
    The `sts` and `ets` parameters were formalized and are timezone aware.

"""

import datetime
from io import BytesIO
from zoneinfo import ZoneInfo

from pydantic import AwareDatetime, Field
from pyiem.database import get_dbconn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.network import Table as NetworkTable
from pyiem.plot.use_agg import plt
from pyiem.webutil import CGIModel, iemapp
from pyiem.windrose_utils import windrose


class Schema(CGIModel):
    bins: str = Field(None, description="Wind Speed Bins separated by comma")
    conv: str = Field(
        "from",
        description=(
            "Wind Convention, either from (meteorology) or to (engineering)"
        ),
    )
    dpi: int = Field(
        100, description="Image Dots per inch (DPI)", ge=10, le=1000
    )
    ets: AwareDatetime = Field(
        None,
        description=(
            "End time with timezone included, otherwise "
            "{year,month,day,hour,minute}2 values used"
        ),
    )
    fmt: str = Field(
        "png",
        description="Output image format, one of png, pdf, svg",
    )
    hourlimit: bool = Field(
        False,
        description="Limit the data to the hour provided",
    )
    hourrangelimit: bool = Field(
        False,
        description="Limit the data to the hour range provided",
    )
    justdata: bool = Field(
        False,
        description="Return data table instead of plot",
    )
    level: int = Field(
        None,
        description="In the case of RAOB data, the hPa level to use",
        ge=0,
        le=1050,
    )
    limit_by_doy: bool = Field(
        False,
        description="Limit the data to the day of year range provided",
    )
    monthlimit: bool = Field(
        False,
        description="Limit the data to the start month provided",
    )
    network: str = Field(
        None,
        description="Network Identifier, best to provide otherwise guessed",
    )
    nsector: int = Field(
        36,
        description="Number of sectors to use for windrose plot",
        ge=4,
        le=180,
    )
    staticrange: int = Field(
        None,
        description="Static range for windrose plot",
        ge=1,
        le=100,
    )
    station: str = Field(..., description="Station Identifier")
    sts: AwareDatetime = Field(
        None,
        description=(
            "Start time with timezone included, otherwise "
            "{year,month,day,hour,minute}1 values used"
        ),
    )
    units: str = Field(
        "mph",
        description="Units to use for speed, one of mph, kts, mps, kph",
        pattern="^(mph|kts|mps|kph)$",
    )
    year1: int = Field(1900, description="Start Year, if sts not provided")
    month1: int = Field(1, description="Start Month, if sts not provided")
    day1: int = Field(1, description="Start Day, if sts not provided")
    hour1: int = Field(0, description="Start Hour, if sts not provided")
    minute1: int = Field(0, description="Start Minute, if sts not provided")
    year2: int = Field(2050, description="End Year, if ets not provided")
    month2: int = Field(1, description="End Month, if ets not provided")
    day2: int = Field(1, description="End Day, if ets not provided")
    hour2: int = Field(0, description="End Hour, if ets not provided")
    minute2: int = Field(0, description="End Minute, if ets not provided")


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


@iemapp(help=__doc__, parse_times=False, schema=Schema)
def application(environ, start_response):
    """Query out the CGI variables"""
    dbname, network, station = get_station_info(environ)
    nt = NetworkTable(network, only_online=False)
    if station not in nt.sts:
        return [
            send_error(environ, "Unknown station identifier", start_response)
        ]
    tzname = nt.sts[station]["tzname"] if network != "RAOB" else "UTC"
    if environ["sts"] is None:
        environ["sts"] = datetime.datetime(
            int(environ.get("year1", 1900)),
            int(environ.get("month1", 1)),
            int(environ.get("day1", 1)),
            int(environ.get("hour1", 0)),
            int(environ.get("minute1", 0)),
            tzinfo=ZoneInfo(tzname),
        )
        environ["ets"] = datetime.datetime(
            int(environ.get("year2", 2050)),
            int(environ.get("month2", 1)),
            int(environ.get("day2", 1)),
            int(environ.get("hour2", 0)),
            int(environ.get("minute2", 0)),
            tzinfo=ZoneInfo(tzname),
        )
    if environ["hourlimit"]:
        hours = [environ["sts"].hour]
    elif environ["hourrangelimit"]:
        if environ["sts"].hour > environ["ets"].hour:  # over midnight
            hours = list(range(environ["sts"].hour, 24))
            hours.extend(range(environ["ets"].hour))
        else:
            if environ["sts"].hour == environ["ets"].hour:
                environ["ets"] += datetime.timedelta(hours=1)
            hours = list(range(environ["sts"].hour, environ["ets"].hour))
    else:
        hours = list(range(24))

    if environ["monthlimit"]:
        months = [environ["sts"].month]
    else:
        months = list(range(1, 13))

    bins = []
    if environ["bins"] is not None:
        bins = [
            float(v) for v in environ["bins"].split(",") if v.strip() != ""
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
        units=environ["units"],
        nsector=environ["nsector"],
        justdata=environ["justdata"],
        rmax=environ["staticrange"],
        sname=nt.sts[station]["name"],
        tzname=tzname,
        level=environ["level"],
        limit_by_doy=environ["limit_by_doy"],
        bins=bins,
        plot_convention=environ["conv"],
    )
    if environ["justdata"]:
        # We want text
        start_response("200 OK", [("Content-type", "text/plain")])
        return [res.encode("utf-8")]
    fmt = environ["fmt"]
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
    res.savefig(bio, format=fmt, dpi=environ["dpi"])
    return [bio.getvalue()]
