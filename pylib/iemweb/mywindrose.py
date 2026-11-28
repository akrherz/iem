""".. title:: Windrose Plotting/Data Service

Documentation for /cgi-bin/windrose.py
--------------------------------------

This service returns a windrose plot or data table.  There's a lot of options
here to consider, so perhaps some examples are in order.

Example Usage
-------------

Plot a windrose for Ames, IA for the month of June 2021:

https://mesonet.agron.iastate.edu/cgi-bin/mywindrose.py?\
station=AMW&network=IA_ASOS&year1=2021&month1=6&day1=1&\
year2=2021&month2=6&day2=30&hour2=23&fmt=png

Changelog
---------

- **2024-03-25** The backend was migrated to use a pydantic schema, which will
  generate more structured error messages when the user provides invalid input.
- **2024-03-25** The `sts` and `ets` parameters were formalized and
  are timezone aware.

"""

from datetime import timedelta
from io import BytesIO
from typing import Annotated
from zoneinfo import ZoneInfo

from matplotlib.figure import Figure
from pydantic import AwareDatetime, Field, model_validator
from pyiem.database import get_dbconn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.network import Table as NetworkTable
from pyiem.util import utc
from pyiem.web.fields import (
    DAY_OF_MONTH_FIELD,
    HOUR_FIELD,
    MINUTE_FIELD,
    MONTH_FIELD,
    NETWORK_FIELD_OPTIONAL,
    YEAR_FIELD,
)
from pyiem.webutil import CGIModel, iemapp
from pyiem.windrose_utils import windrose


class Schema(CGIModel):
    bins: Annotated[
        str | None, Field(description="Wind Speed Bins separated by comma")
    ] = None
    conv: Annotated[
        str,
        Field(
            description=(
                "Wind Convention, either from (meteorology) "
                "or to (engineering)"
            ),
        ),
    ] = "from"
    dpi: Annotated[
        int, Field(description="Image Dots per inch (DPI)", ge=10, le=1000)
    ] = 100
    ets: Annotated[
        AwareDatetime | None,
        Field(
            description=(
                "End time with timezone included, otherwise "
                "{year,month,day,hour,minute}2 values used"
            ),
        ),
    ] = None
    fmt: Annotated[
        str,
        Field(
            description="Output image format, one of png, pdf, svg",
        ),
    ] = "png"
    hourlimit: Annotated[
        bool,
        Field(
            description="Limit the data to the hour provided",
        ),
    ] = False
    hourrangelimit: Annotated[
        bool,
        Field(
            description="Limit the data to the hour range provided",
        ),
    ] = False
    justdata: Annotated[
        bool,
        Field(
            description="Return data table instead of plot",
        ),
    ] = False
    level: Annotated[
        int | None,
        Field(
            description="In the case of RAOB data, the hPa level to use",
            ge=0,
            le=1050,
        ),
    ] = None
    limit_by_doy: Annotated[
        bool,
        Field(
            description="Limit the data to the day of year range provided",
        ),
    ] = False
    monthlimit: Annotated[
        bool,
        Field(
            description="Limit the data to the start month provided",
        ),
    ] = False
    network: NETWORK_FIELD_OPTIONAL = None
    nsector: Annotated[
        int,
        Field(
            description="Number of sectors to use for windrose plot",
            ge=4,
            le=180,
        ),
    ] = 36
    staticrange: Annotated[
        int | None,
        Field(
            description="Static range for windrose plot",
            ge=1,
            le=100,
        ),
    ] = None
    station: Annotated[str, Field(description="Station Identifier")]
    sts: Annotated[
        AwareDatetime | None,
        Field(
            description=(
                "Start time with timezone included, otherwise "
                "{year,month,day,hour,minute}1 values used"
            ),
        ),
    ] = None
    units: Annotated[
        str,
        Field(
            description="Units to use for speed, one of mph, kts, mps, kph",
            pattern="^(mph|kts|mps|kph)$",
        ),
    ] = "mph"
    year1: YEAR_FIELD = 1946
    month1: MONTH_FIELD = 1
    day1: DAY_OF_MONTH_FIELD = 1
    hour1: HOUR_FIELD = 0
    minute1: MINUTE_FIELD = 0
    year2: YEAR_FIELD = utc().year
    month2: MONTH_FIELD = 1
    day2: DAY_OF_MONTH_FIELD = 1
    hour2: HOUR_FIELD = 0
    minute2: MINUTE_FIELD = 0

    @model_validator(mode="after")
    def validator_raob_request(self):
        """Ensure that level is set if the network is RAOB."""
        if (
            self.network is not None
            and self.network == "RAOB"
            and self.level is None
        ):
            raise ValueError("level is required when network is RAOB")
        return self


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

    fig = Figure()
    ax = fig.add_subplot(1, 1, 1)
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
        row = cursor.fetchone()
        if row is None:
            raise IncompleteWebRequest(
                "Failed to guess network for given station. Please provide "
                "explicit network= to service."
            )
        res = row[0]
    return res


def get_station_info(environ: dict) -> tuple[str, str, str]:
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
        dbname = "raob"
    elif network.find("_DCP") > 0:
        dbname = "hads"

    return dbname, network, station


@iemapp(help=__doc__, parse_times=True, schema=Schema)
def application(environ, start_response):
    """Query out the CGI variables"""
    dbname, network, station = get_station_info(environ)
    nt = NetworkTable(network, only_online=False)
    if station not in nt.sts:
        return [
            send_error(environ, "Unknown station identifier", start_response)
        ]
    tzname = nt.sts[station]["tzname"] if network != "RAOB" else "UTC"
    for key in ["sts", "ets"]:
        if environ[key].tzinfo is None:
            environ[key] = environ[key].replace(tzinfo=ZoneInfo(tzname))

    if environ["hourlimit"]:
        hours = [environ["sts"].hour]
    elif environ["hourrangelimit"]:
        if environ["sts"].hour > environ["ets"].hour:  # over midnight
            hours = list(range(environ["sts"].hour, 24))
            hours.extend(range(environ["ets"].hour))
        else:
            if environ["sts"].hour == environ["ets"].hour:
                environ["ets"] += timedelta(hours=1)
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
        bins = sorted(set(bins))[:6]
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
        return res
    fmt = environ["fmt"]
    if fmt == "png":
        ct = "image/png"
    elif fmt == "pdf":
        ct = "application/pdf"
    elif fmt == "svg":
        ct = "image/svg+xml"
    else:
        return send_error(environ, "Invalid fmt set", start_response)
    bio = BytesIO()
    res.savefig(bio, format=fmt, dpi=environ["dpi"])
    start_response("200 OK", [("Content-type", ct)])
    return bio.getvalue()
