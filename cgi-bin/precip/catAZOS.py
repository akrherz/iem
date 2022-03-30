"""
IEM_APPID = 79
"""
from io import StringIO
import datetime

import psycopg2.extras
from paste.request import parse_formvars
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn

nt = NetworkTable("IA_ASOS")
IEM = get_dbconn("iem")
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

requireHrs = [0] * 25
stData = {}
totp = {}


def doHeader(environ, start_response, sio):
    """get going."""
    start_response("200 OK", [("Content-type", "text/html")])
    sio.write(
        """
<html>
<head>
  <title>IEM | Hourly Precip Grid</title>
</head>
<body bgcolor="white">
<a href="/index.php">Iowa Mesonet</a> &gt;
<a href="/climate/">Climatology</a> &gt;
Hourly Precipitation [IA_ASOS]

"""
    )
    sio.write('<h3 align="center">Hourly Precip [inches] Grid</h3>')
    form = parse_formvars(environ)
    try:
        postDate = form.get("date")
        myTime = datetime.datetime.strptime(postDate, "%Y-%m-%d")
    except Exception:
        myTime = datetime.datetime.now()

    sio.write("<table border=1><tr>")
    sio.write(
        '<td>Back: <a href="catAZOS.py?date='
        + (myTime - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        + '"> \
    '
        + (myTime - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        + "</a></td>"
    )

    sio.write("<td>Shown: " + myTime.strftime("%d %B %Y") + "</td>")

    sio.write(
        '<td>Forward: <a href="catAZOS.py?date='
        + (myTime + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        + '"> \
    '
        + (myTime + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        + "</a></td>"
    )

    sio.write(
        """
<td>Pick: (yyyy-mm-dd)  
<form method="GET" action="catAZOS.py">
<input type="text" size="8" name="date">
<input type="submit" value="Submit Date">
</form></td></tr></table>
"""
    )
    return myTime


def setupTable(sio):
    """make table."""
    sio.write(
        """
<style language="css">
td.style1{
  background-color: #EEEEEE;
}
td.style2{
  background-color: #ffefe1;
}
td.style0{
  background-color: #c6e3ff;
}
tr.row1{
  border-bottom: 4pt;
  border-top: 4pt;
  border-right: 4pt;
  border-left: 4pt;
  background-color: #dddddd;
}
table.main{
  font-size: 8pt;
  font-face: arial sans-serif;
}
</style>
<table width="100%" class="main">
<tr>
  <th rowspan="2">Station</th>
  <th colspan="11">Morning (AM)</th>
  <td></td>
  <th colspan="12">Afternoon/Evening (PM)</th>
  <td></td>
   <th rowspan="2">Station</th>
</tr>
<tr>
  <td class="style1">Mid</td> <td class="style2">1</td> <td class="style0">2</td> 
  <td class="style1">3</td> <td class="style2">4</td> <td class="style0">5</td> 
  <td class="style1">6</td> <td class="style2">7</td> <td class="style0">8</td> 
  <td class="style1">9</td> <td class="style2">10</td> <td class="style0">11</td> 
  <td class="style1">Noon</td> <td class="style2">1</td> <td class="style0">2</td> 
  <td class="style1">3</td> <td class="style2">4</td> <td class="style0">5</td> 
  <td class="style1">6</td> <td class="style2">7</td> <td class="style0">8</td> 
  <td class="style1">9</td> <td class="style2">10</td> <td class="style0">11</td> 
  <th>Tot:</th>
</tr>
"""
    )


def loadstations():
    """load stations"""
    for station in nt.sts:
        stData[station] = ["M"] * 24
        totp[station] = 0


def application(environ, start_response):
    """Go Main Go"""
    sio = StringIO()
    ts = doHeader(environ, start_response, sio)
    loadstations()
    setupTable(sio)

    icursor.execute(
        "SELECT extract('hour' from valid) as vhour, t.id as station, "
        f"valid, phour from hourly_{ts.year} h JOIN stations t on "
        "(h.iemid = t.iemid) WHERE "
        "valid >= %s and valid < %s and t.network = 'IA_ASOS'",
        (ts, ts + datetime.timedelta(hours=24)),
    )
    for row in icursor:
        p01i = float(row["phour"])
        vhour = int(row["vhour"])
        if p01i > 0:  # We should require this timestep
            requireHrs[vhour] = 1
            try:
                stData[row["station"]][vhour] = round(p01i, 2)
            except KeyError:
                continue
        else:
            try:
                stData[row["station"]][vhour] = "&nbsp;"
            except KeyError:
                continue

    if ts < datetime.datetime(2006, 6, 1):
        stData["MXO"] = ["M"] * 24
    if ts < datetime.datetime(2007, 6, 1):
        stData["IIB"] = ["M"] * 24
        stData["VTI"] = ["M"] * 24
        stData["MPZ"] = ["M"] * 24
        stData["PEA"] = ["M"] * 24
        stData["IFA"] = ["M"] * 24
        stData["TVK"] = ["M"] * 24

    j = 0
    ids = list(nt.sts.keys())
    ids.sort()
    for station in ids:
        j += 1
        sio.write('<tr class="row' + str(j % 5) + '">')
        sio.write("%s%s%s" % ("<td>", station, "</td>"))
        for i in range(24):
            sio.write('<td class="style' + str((i + 1) % 3) + '">')
            sio.write("%s%s " % (stData[station][i], "</td>"))
            try:
                totp[station] = totp[station] + stData[station][i]
            except Exception:
                continue
        sio.write("%s%s%s" % ("<td>", totp[station], "</td>"))
        sio.write("%s%s%s" % ("<td>", station, "</td>"))
        sio.write("</tr>")

    sio.write(
        """
</table>

<p>Precipitation values are shown for the hour in which they are valid.  For
example, the value in the 1AM column is precipitation accumulation from 1 AM
till 2 AM.
"""
    )
    return [sio.getvalue().encode("ascii")]
