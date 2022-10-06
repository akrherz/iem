<?php
require_once "../../../config/settings.inc.php";

require_once "../../../include/myview.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/imagemaps.php";
require_once "../../../include/forms.php";

$t = new MyView();

$t->title = "Download TallTowers 1 minute aggregate data";

$y1select = yearSelect2(2016, date("Y"), "year1");
$y2select = yearSelect2(2016, date("Y"), "year2");

$m1select = monthSelect2(1, "month1");
$m2select = monthSelect2(date("m"), "month2");

$d1select = daySelect2(1, "day1");
$d2select = daySelect2(date("d"), "day2");

$h1select = hourSelect(0, "hour1");
$h2select = hourSelect(0, "hour2");

$ar = array(
    "Etc/UTC" => "Coordinated Universal Time (UTC)",
    "America/Chicago" => "America/Chicago (CST/CDT)",
);

$tzselect = make_select("tz", "Etc/UTC", $ar);

$t->content = <<<EOF

<ol class="breadcrumb">
 <li><a href="/projects/iao/">IEM Iowa Atmospheric Observatory Homepage</a></li>
 <li class="active">One minute aggregate data</li>
</ol>

<p>This interface provides a download of one minute aggregates of available
one second data from the "analog" sensors found on the Tall Towers.</p>

<h4>Citation</h4>

<p>Acknowledgement is made to Iowa State University use of data from the ISU 
Tall-Tower Network, which is funded by grants from the Iowa Power Fund and
National Science Foundation Iowa EPSCoR grant #1101284 and National
Science Foundation grant #1701278.</p>

<form method="GET" action="/cgi-bin/request/talltowers.py" target="_blank">

<div class="row"><div class="col-md-6">

<h4>1) Select tower(s):</h4>

<select name="station" size="2" MULTIPLE>
  <option value="ETTI4">ETTI4 - Hamilton County - Tall Towers</option>
  <option value="MCAI4">MCAI4 - Story County - Tall Towers</option>
</select>

<h4>2) Select Time Zone of Observations:</h4>

{$tzselect}

<h4>3) Specific Date Range:</h4>

<p>Due to processing constraints, up to 31 days of data is only allowed per
request.</p>

<table class="table table-condensed">
<tr><th>Start Date:</th><td>{$y1select} {$m1select} {$d1select} {$h1select}</td></tr>
<tr><th>End Date:</th><td>{$y2select} {$m2select} {$d2select} {$h2select}</td></tr>
</table>

<h4>4) Select sensor height(s) on tower</h4>

<select name="z" size="6" multiple>
    <option value="5">5m (16ft)</option>
    <option value="10">10m (33ft)</option>
    <option value="20">20m (66ft)</option>
    <option value="40">40m (131ft)</option>
    <option value="80">80m (263ft)</option>
    <option value="120">120m (394ft)</option>
</select>

</div><div class="col-md-6">

<h4>5) Select available variables</h4>

<select name="var" size="7" multiple>
    <option value="airtc">Air Temperature [C]</option>
    <option value="rh">Relative Humidity [%]</option>
    <option value="ws_s">Wind Speed (South Boom) [m/s]</option>
    <option value="winddir_s">Wind Direction (South Boom) [deg]</option>
    <option value="ws_nw">Wind Speed (WNW Boom) [m/s]</option>
    <option value="winddir_nw">Wind Direction (WNW Boom) [deg]</option>
    <option value="bp">Air Pressure (10m and 80m only) [mb]</option>
</select>

<h4>6) Select statistical aggregates</h4>

<select name="agg" size="7" multiple>
    <option value="avg">Mean</option>
    <!-- Unsure how yet <option value="median">Median</option> -->
    <option value="std">Standard Deviation</option>
    <option value="mad">Mean Absolute Deviation</option>
    <option value="max">Max</option>
    <option value="min">Min</option>
    <option value="count">Count</option>
</select>

<h4>7) Select Output Resolution</h4>

<select name="window">
    <option value="1">1 Minute</option>
    <option value="5">5 Minute</option>
    <option value="10">10 Minute</option>
    <option value="15">15 Minute</option>
    <option value="20">20 Minute</option>
    <option value="30">30 Minute</option>
    <option value="60">60 Minute</option>
</select>


<h4>8) Download Options:</h4>
        
<p><strong>Data Format:</strong> 
<select name="format">
    <option value="comma">Comma Delimited</option>
    <option value="excel">Excel (.xlsx)</option>
    <option value="tdf">Tab Delimited</option>
</select></p>

<h4>9) Finally, process request</h4>

  <input type="submit" value="Get Data">
  <input type="reset">

</div></div><!-- ./row -->

 </form>

<br /><br />

EOF;
$t->render('single.phtml');
