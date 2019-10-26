#!/usr/bin/env python
"""
IEM_APPID = 79
"""
import cgi
import datetime
import psycopg2.extras
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, ssw

nt = NetworkTable(("AWOS", "IA_ASOS"))
IEM = get_dbconn("iem")
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

requireHrs = [0] * 25
stData = {}
totp = {}


def doHeader():
    ssw("Content-type: text/html \n\n")
    ssw(
        """
<html>
<head>
  <title>IEM | Hourly Precip Grid</title>
</head>
<body bgcolor="white">
<a href="/index.php">Iowa Mesonet</a> &gt;
<a href="/climate/">Climatology</a> &gt;
Hourly Precipitation [ASOS/AWOS]

"""
    )
    ssw('<h3 align="center">Hourly Precip [inches] Grid</h3>')
    form = cgi.FieldStorage()
    try:
        postDate = form.getfirst("date")
        myTime = datetime.datetime.strptime(postDate, "%Y-%m-%d")
    except Exception:
        myTime = datetime.datetime.now()

    ssw("<table border=1><tr>")
    ssw(
        '<td>Back: <a href="catAZOS.py?date='
        + (myTime - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        + '"> \
    '
        + (myTime - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        + "</a></td>"
    )

    ssw("<td>Shown: " + myTime.strftime("%d %B %Y") + "</td>")

    ssw(
        '<td>Forward: <a href="catAZOS.py?date='
        + (myTime + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        + '"> \
    '
        + (myTime + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        + "</a></td>"
    )

    ssw(
        """
<td>Pick: (yyyy-mm-dd)  
<form method="GET" action="catAZOS.py">
<input type="text" size="8" name="date">
<input type="submit" value="Submit Date">
</form></td></tr></table>
"""
    )
    return myTime


def setupTable():
    ssw(
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


def main():
    """Go Main Go"""
    ts = doHeader()
    loadstations()
    setupTable()

    td = ts.strftime("%Y-%m-%d")
    tm = (ts + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    ##
    #  Hack, since postgres won't index date(valid)

    sql = """
        SELECT extract('hour' from valid) as vhour, 
        station, valid, phour from hourly_%s WHERE 
        valid >= '%s 00:00' and valid < '%s 00:00'
        and network in ('AWOS','IA_ASOS')
    """ % (
        ts.year,
        td,
        tm,
    )

    icursor.execute(sql)
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
        ssw('<tr class="row' + str(j % 5) + '">')
        ssw("%s%s%s" % ("<td>", station, "</td>"))
        for i in range(24):
            ssw('<td class="style' + str((i + 1) % 3) + '">')
            ssw("%s%s " % (stData[station][i], "</td>"))
            try:
                totp[station] = totp[station] + stData[station][i]
            except Exception:
                continue
        ssw("%s%s%s" % ("<td>", totp[station], "</td>"))
        ssw("%s%s%s" % ("<td>", station, "</td>"))
        ssw("</tr>")

    ssw(
        """
</table>

<p>Precipitation values are shown for the hour in which they are valid.  For
example, the value in the 1AM column is precipitation accumulation from 1 AM
till 2 AM.
"""
    )


if __name__ == "__main__":
    main()
