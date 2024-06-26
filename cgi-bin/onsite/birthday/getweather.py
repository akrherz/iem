"""Legacy."""

import datetime
from io import StringIO

from pydantic import Field
from pyiem.database import get_dbconn
from pyiem.exceptions import NoDataFound
from pyiem.network import Table as NetworkTable
from pyiem.templates.iem import TEMPLATE
from pyiem.webutil import CGIModel, iemapp

nt = NetworkTable("IACLIMATE", only_online=False)

COOP = get_dbconn("coop")
ccursor = COOP.cursor()


class Schema(CGIModel):
    """See how we are called."""

    city: str = Field(..., description="City Code")
    year: int = Field(..., description="Year")
    month: int = Field(..., description="Month")
    day: int = Field(..., description="Day")


def weather_logic(month, high, low, rain, snow):
    """Do Something."""
    deltaT = high - low

    if 4 < month < 11:  # It is summer
        if deltaT >= 30:
            if rain == 0.00:
                return "Sunny!!"
            return "Mostly sunny w/ Rain!!"
        if deltaT >= 15:
            if rain == 0.00:
                return "Mostly Sunny!!"
            return "Partly Sunny w/ Rain!!"
        if rain == 0.00:
            return "Cloudy!!"
        return "Cloudy and rainy!!"

    if deltaT >= 20:
        if rain == 0.00:
            return "Sunny!!"
        if rain > 0 and snow > 0:
            return "Snowy!!"
        return "Mostly sunny w/ Rain!!"

    if deltaT >= 10:
        if rain == 0.00:
            return "Mostly Sunny!!"
        if rain > 0 and snow > 0:
            return "Snowy!!"
        return "Partly Sunny w/ Rain!!"
    if rain == 0.00:
        return "Cloudy!!"
    if rain > 0 and snow > 0:
        return "Snowy!!"
    return "Cloudy and rainy!!"


def get_values(city, dateStr):
    """Get values."""
    query_str = """SELECT high, low, precip, snow from alldata_ia
    WHERE station = %s and day = %s """
    args = (city, dateStr)
    ccursor.execute(query_str, args)
    if ccursor.rowcount == 0:
        raise NoDataFound("No Data Found.")
    row = ccursor.fetchone()
    rain = round(float(row[2]), 2)
    try:
        snow = round(float(row[3]), 2)
    except Exception:
        snow = 0

    rain = max(rain, 0)
    snow = max(snow, 0)

    return row[0], row[1], str(rain), str(snow)


def get_day(sio, city, ts):
    """Yawn."""
    str_month = ts.strftime("%B")
    year = str(ts.year)
    month = str(ts.month)
    day = str(ts.day)
    dateStr = year + "-" + month + "-" + day
    high, low, rain, snow = get_values(city, dateStr)

    cloud_type = weather_logic(
        int(month),
        int(high),
        int(low),
        round(float(rain), 2),
        round(float(snow), 2),
    )

    sio.write('<div class="col-md-2">')
    sio.write(
        '<img src="/content/date.php?year='
        + year
        + "&month="
        + str_month
        + "&day="
        + day
        + '"><BR>'
    )
    sio.write("<TABLE>")
    sio.write("<TR><TH>HIGH </TH><TD> " + str(high) + "</TD></TR>")
    sio.write("<TR><TH>LOW  </TH><TD> " + str(low) + "</TD></TR>")
    sio.write("<TR><TH>RAIN </TH><TD> " + str(rain) + "</TD></TR>")
    sio.write("<TR><TH>SNOW </TH><TD> " + str(snow) + "</TD></TR>")
    sio.write(
        "<TR><TH colspan='2' NOWRAP><font color='blue'>"
        + cloud_type
        + "</font></TH></TR>"
    )
    sio.write("</TABLE>")
    sio.write("</div>")


def now_get_day(sio, city, ts):
    """Yawn."""
    str_month = ts.strftime("%B")
    year = str(ts.year)
    month = str(ts.month)
    day = str(ts.day)
    dateStr = year + "-" + month + "-" + day
    high, low, rain, snow = get_values(city, dateStr)
    cloud_type = weather_logic(
        int(month),
        int(high),
        int(low),
        round(float(rain), 2),
        round(float(snow), 2),
    )

    sio.write('<div class="col-md-3">')
    sio.write('<font color="BLUE">HAPPY BIRTHDAY!!</font><BR><BR>')
    sio.write(
        '<img src="/content/date.php?year='
        + year
        + "&month="
        + str_month
        + "&day="
        + day
        + '"><BR>'
    )
    sio.write("<TABLE>")
    sio.write("<TR><TH>HIGH </TH><TD> " + str(high) + "</TD></TR>")
    sio.write("<TR><TH>LOW  </TH><TD> " + str(low) + "</TD></TR>")
    sio.write("<TR><TH>RAIN </TH><TD> " + str(rain) + "</TD></TR>")
    sio.write("<TR><TH>SNOW </TH><TD> " + str(snow) + "</TD></TR>")
    sio.write(
        "<TR><TH colspan='2' NOWRAP><font color='blue'>"
        + cloud_type
        + "</font></TH></TR>"
    )
    sio.write("</TABLE>")
    sio.write("</div>")


@iemapp(help=__doc__, schema=Schema)
def application(environ, start_response):
    """Go Main Go."""
    sio = StringIO()
    sio.write('<a href="/onsite/birthday/">Try another date or city</a><BR>')
    start_response("200 OK", [("Content-type", "text/html")])
    ctx = {"title": "Weather on Your Birthday"}

    city = environ["city"].upper()
    if city not in nt.sts:
        raise NoDataFound("Unknown City")

    cityName = nt.sts[city]["name"]
    now = datetime.datetime(environ["year"], environ["month"], environ["day"])
    nowM2 = now + datetime.timedelta(days=-2)
    nowM1 = now + datetime.timedelta(days=-1)
    nowP1 = now + datetime.timedelta(days=1)
    nowP2 = now + datetime.timedelta(days=2)

    sio.write(
        "<BR><h4>Data valid for station: " + cityName + ", Iowa</h4><BR>"
    )

    sio.write('<div class="row">')

    get_day(sio, city, nowM2)

    get_day(sio, city, nowM1)

    now_get_day(sio, city, now)

    get_day(sio, city, nowP1)

    get_day(sio, city, nowP2)

    sio.write("</div>")

    sio.write(
        """
    <BR><BR><P>The weather type listed for each day above in blue is
    <B>not</b> official data.  A rather
    subjective logic scheme is used to guess the weather purely
    for entertainment purposes only.
    """
    )
    ctx["content"] = sio.getvalue()
    return [TEMPLATE.render(ctx).encode("ascii")]
