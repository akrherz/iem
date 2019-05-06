<?php 
require_once "../../../config/settings.inc.php";
require_once "../../../include/myview.php";
require_once "../../../include/forms.php";
require_once "../../../include/imagemaps.php";
define("IEM_APPID", 111);

$t = new MyView();
$t->thispage = "archive-pireps";
$t->title = "Download PIREPs";
$content = <<<EOF
<h3>Archived Pilot Reports (PIREPs)</h3>

<p>The IEM attempts to process a feed of Pilot Reports (PIREPs). This
processing is done via the <a href="https://github.com/akrherz/pyIEM/blob/master/pyiem/nws/products/pirep.py">PyIEM Library</a>.
Sadly, there is not strict coherence to a format specification and so a 
number of reports are simply unparsable.  This archive should not be
considered 'complete'.</p>

<div class="alert alert-info">
 <i class="fa fa-warning"></i> The PIREP parsing library that decodes the location information into a latitude
 and longitude is crude.  It does not properly account for magnetic north and may
 also have errors with VOR baseline locations.  This download interface provides
 the raw undecoded PIREP reports, so users that have more sophisticated location
 calculators are encouraged to process them for yourself.
</div>

<p>Due to filesize and speed, you can only request up to 120 days of data
at a time!</p>

<form method="GET" action="/cgi-bin/request/gis/pireps.py">
<h4>Select time interval</h4>
<i>(Times are in UTC.)</i>
<table class="table">
<thead><tr><th colspan="6">Time Interval</th>
		<th>Format</th></tr></thead>
<tr>
	<th></th>
    <th>Year</th><th>Month</th><th>Day</th>
    <th>Hour</th><th>Minute</th>
    <td rowspan="3"><select name="fmt">
		<option value="shp">ESRI Shapefile</option>
		<option value="csv">Comma Delimited</option>
		</select></td>
</tr>

<tr>
EOF;
$content .= "
    <th>Start:</th>
    <td>
     ". yearSelect2(2015, date("Y"), "year1") ."
    </td>
    <td>
     ". monthSelect2(0,"month1") ."
    </td>
    <td>
     ". daySelect2(0, "day1") ."
    </td>
    <td>
     ". gmtHourSelect(0, "hour1") ."
    </td>
    <td>
     ". minuteSelect(0, "minute1") ."
    </td>
  </tr>

  <tr>
    <th>End:</th>
    <td>
     ". yearSelect2(2015, date("Y"), "year2") ."
    </td>
    <td>
     ". monthSelect2(0,"month2") ."
    </td>
    <td>
     ". daySelect2(0, "day2") ."
    </td>
    <td>
     ". gmtHourSelect(0, "hour2") ."
    </td>
    <td>
     ". minuteSelect(0, "minute2") ."
    </td>
  </tr>
</table>";

$content .= <<<EOF
<p><input type="submit" value="Giveme data right now!">
</form>

<h4>Shapefile DBF schema:</h4>
<pre>
Field 0: Type=C/String, Title='VALID', Timestamp in UTC
Field 1: Type=C/String, Title='URGENT', Was this an urgent PIREP
Field 2: Type=C/String, Title='AIRCRAFT', Reported Aircraft type
Field 3: Type=C/String, Title='REPORT', The PIREP Report
Field 4: Type=N/Double, Title='LAT', Latitude
Field 5: Type=N/Double, Title='LON', Longitude 
</pre>

<h4>Archive notes:</h4>
<ul>
 <li>Archive starts 20 Jan 2015</li>
 </ul>
EOF;
$t->content = $content;
$t->render('single.phtml');
?>