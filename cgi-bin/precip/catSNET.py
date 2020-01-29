"""
Generate web output for precip data
"""
from io import StringIO
import datetime

import psycopg2.extras
from paste.request import parse_formvars
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn

nt = NetworkTable(("KCCI", "KIMIT", "KELO"))
IEM = get_dbconn("iem")
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)


requireHrs = [0] * 25
stData = {}
totp = {}


# Return the Date we will be looking for...
def doHeader(environ, start_response, sio):
    """header please"""
    start_response("200 OK", [("Content-type", "text/html")])
    sio.write(
        """
<html>
<head>
  <title>IEM | Hourly Precip Grid</title>
</head>
<body bgcolor="white">
<a href="/index.php">Iowa Mesonet</a> > 
<a href="/schoolnet/">School Net</a> >
Hourly Precipitation [SNET]
<br>This archive starts on 12 Feb 2002 for KCCI sites and 12 Sept 2002 for
KELO sites.  Data from the previous day is the most current available.

"""
    )
    sio.write('<h3 align="center">Hourly Precip Grid</h3>')
    form = parse_formvars(environ)
    try:
        postDate = form.get("date")
        myTime = datetime.datetime.strptime(postDate, "%Y-%m-%d")
    except Exception:
        myTime = datetime.datetime.now() - datetime.timedelta(days=1)

    sio.write("<table border=1><tr>")
    sio.write(
        '<td>Back: <a href="catSNET.py?date='
        + (myTime - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        + '"> \
        '
        + (myTime - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        + "</a></td>"
    )

    sio.write("<td>Shown: " + myTime.strftime("%d %B %Y") + "</td>")

    sio.write(
        '<td>Forward: <a href="catSNET.py?date='
        + (myTime + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        + '"> \
        '
        + (myTime + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        + "</a></td>"
    )

    sio.write(
        """
<td>Pick: (yyyy-mm-dd)  
<form method="GET" action="catSNET.py">
<input type="text" size="8" name="date">
<input type="submit" value="Submit Date">
</form></td></tr></table>
"""
    )
    return myTime


def setupTable(sio):
    """Do"""
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
  <td class="style0">Mid</td> <td class="style1">1</td> <td class="style2">2</td> 
  <td class="style0">3</td> <td class="style1">4</td> <td class="style2">5</td> 
  <td class="style0">6</td> <td class="style1">7</td> <td class="style2">8</td> 
  <td class="style0">9</td> <td class="style1">10</td> <td class="style2">11</td> 
  <td class="style0">Noon</td> <td class="style2">1</td> <td class="style2">2</td> 
  <td class="style0">3</td> <td class="style1">4</td> <td class="style2">5</td> 
  <td class="style0">6</td> <td class="style1">7</td> <td class="style2">8</td> 
  <td class="style0">9</td> <td class="style1">10</td> <td class="style2">11</td> 
  <th>Tot:</th>
</tr>
"""
    )


def loadstations():
    """Bah"""
    for station in nt.sts:
        stData[station] = ["M"] * 25
        totp[station] = 0


def application(environ, start_response):
    """Go Main Go."""
    sio = StringIO()
    ts = doHeader(environ, start_response, sio)
    loadstations()
    setupTable(sio)

    td = ts.strftime("%Y-%m-%d")
    tm = (ts + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    sqlStr = """
        SELECT extract('hour' from valid) as vhour,
        station, valid, phour from hourly_%s WHERE
        valid > '%s 00:00' and valid <= '%s 00:00'
        and network in ('KCCI','KIMT','KELO')
    """ % (
        ts.year,
        td,
        tm,
    )

    icursor.execute(sqlStr)

    for row in icursor:
        p01i = float(row["phour"])
        vhour = int(row["vhour"])
        if p01i >= 0:  # We should require this timestep
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

    j = 0
    ids = list(nt.sts.keys())
    ids.sort()
    for station in ids:
        j += 1
        sio.write('<tr class="row' + str(j % 5) + '">')
        sio.write("%s%s%s" % ("<td>", nt.sts[station]["name"], "</td>"))
        for i in range(0, 24):
            sio.write('<td class="style' + str(i % 3) + '">')
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
