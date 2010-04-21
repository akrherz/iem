#!/mesonet/python/bin/python
# Generate web output for precip data
# Daryl Herzmann 06 Mar 2003
#  7 Mar 2003:	Do some more cleanups

import pg, mx.DateTime, cgi
from pyIEM import stationTable, iemdb
i = iemdb.iemdb()
mydb = i["iem"]
st = stationTable.stationTable("/mesonet/TABLES/snet.stns")

requireHrs = [0]*25
stData = {}
totp = {}

# Return the Date we will be looking for...
def doHeader():
  print 'Content-type: text/html \n\n'
  print """
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
  print '<h3 align="center">Hourly Precip Grid</h3>'
  form = cgi.FormContent()
  try:
    postDate = form["date"][0]
    myTime = mx.DateTime.strptime(postDate, "%Y-%m-%d")
  except:
    myTime = mx.DateTime.now() + mx.DateTime.RelativeDateTime(days=-1)

  print '<table border=1><tr>'
  print '<td>Back: <a href="catSNET.py?date='+ (myTime - 1 ).strftime("%Y-%m-%d") +'"> \
    '+ (myTime - 1 ).strftime("%Y-%m-%d") +'</a></td>'
 
  print '<td>Shown: '+ myTime.strftime("%d %B %Y") +'</td>'

  print '<td>Forward: <a href="catSNET.py?date='+ (myTime + 1 ).strftime("%Y-%m-%d") +'"> \
    '+ (myTime + 1 ).strftime("%Y-%m-%d") +'</a></td>'

  print """
<td>Pick: (yyyy-mm-dd)  
<form method="GET" action="catSNET.py">
<input type="text" size="8" name="date">
<input type="submit" value="Submit Date">
</form></td></tr></table>
"""
  return myTime

def setupTable():
  print """
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
def loadstations():
  for station in st.ids:
    stData[station] = ["M"]*25
    totp[station] = 0

def Main():
  ts = doHeader()
  loadstations()
  setupTable()

  sqlDate = ts.strftime("%Y-%m-%d")
  td = ts.strftime("%Y-%m-%d")
  tm = (ts + 1).strftime("%Y-%m-%d")

   ##
   #  Hack, since postgres won't index date(valid)
  sqlStr = """SELECT extract('hour' from valid) as vhour, 
    station, valid, phour from hourly_%s WHERE 
    valid > '%s 00:00' and valid <= '%s 00:00'
    and network in ('KCCI','KIMT','KELO')""" % (ts.year, td, tm)


  rs = ""
  try:
    rs = mydb.query(sqlStr).dictresult()
  except:
    print "<p>Error: No data for that year"

  for i in range(len(rs)):
    p01i = float(rs[i]["phour"])
    vhour = int(rs[i]["vhour"])
#    if (vhour == 0):
#      vhour = 24
    if (p01i >= 0):  # We should require this timestep
      requireHrs[ vhour ] = 1
      try:
        stData[ rs[i]["station"] ][ vhour ]  = round(p01i,2)
      except KeyError:
        continue
    else:
      try:
        stData[ rs[i]["station"] ][ vhour ]  = "&nbsp;"
      except KeyError:
        continue

  for j in range(len(st.ids)):
    station = st.ids[j]
    print "<tr class=\"row"+ str(j % 5) +"\">",
    print "%s%s%s" % ("<td>", st.sts[station]['name'], "</td>") ,
    for i in range(0,24):
      print "<td class=\"style"+ str(i % 3) +"\">",
      print "%s%s " % ( stData[station][i], "</td>") ,
      try:
        totp[station] = totp[station] + stData[station][i]
      except:
        continue
    print "%s%s%s" % ("<td>", totp[station], "</td>") ,
    print "%s%s%s" % ("<td>", station, "</td>") ,
    print "</tr>"

  print """
</table>

<p>Precipitation values are shown for the hour in which they are valid.  For
example, the value in the 1AM column is precipitation accumulation from 1 AM 
till 2 AM.
"""
Main()
