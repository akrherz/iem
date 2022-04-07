<?php 
require_once "../../../config/settings.inc.php";

require_once "../../../include/myview.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/imagemaps.php";
require_once "../../../include/forms.php";

$t = new MyView();

$t->title = "Download Surface Station data";

$y1select = yearSelect2(2016, date("Y"), "year1"); 
$y2select = yearSelect2(2016, date("Y"), "year2"); 

$m1select = monthSelect2(1, "month1"); 
$m2select = monthSelect2(date("m"), "month2"); 

$d1select = daySelect2(1, "day1"); 
$d2select = daySelect2(date("d"), "day2");

$h1select = hourSelect(0, "hour1");
$h2select = hourSelect(0, "hour2");

$ar = Array(
	"Etc/UTC" => "Coordinated Universal Time (UTC)",
    "America/Chicago" => "America/Chicago (CST/CDT)",
);

$tzselect = make_select("tz", "Etc/UTC", $ar);
		
$t->content = <<<EOF

<ol class="breadcrumb">
 <li><a href="/projects/iao/">IEM Iowa Atmospheric Observatory Homepage</a></li>
 <li class="active">Surface Station data</li>
</ol>

<p>This interface provides a download of ten-minute data from the surface met
station at the ISU Tall Towers facility.</p>

<h4>Citation</h4>

<p>Acknowledgement is made to Iowa State University use of sodar data funded
by the National Science Foundation (grant #1701278).</p>

<form method="GET" action="/cgi-bin/request/iao_surface.py" target="_blank">

<div class="row"><div class="col-md-6">

<h4>1) Select Time Zone of Observations:</h4>

{$tzselect}

<h4>2) Specific Date Range:</h4>

<table class="table table-condensed">
<tr><th>Start Date:</th><td>{$y1select} {$m1select} {$d1select} {$h1select}</td></tr>
<tr><th>End Date:</th><td>{$y2select} {$m2select} {$d2select} {$h2select}</td></tr>
</table>

<h4>4) Select surface station variables</h4>

<select name="var" size="7" multiple>
    <option value="airtc">Air Temperature [C] (2m only)</option>
    <option value="rh">Relative Humidity [%] (2m only)</option>
    <option value="bp">Air Pressure [mb] (2 m only)</option>
    <option value="winddir">Wind Direction [deg]</option>
    <option value="ws">Horizontal Wind Speed [m/s]</option>
    <option value="ws_vert">Vertical Wind Speed [m/s]</option>
    <option value="q">Measurement Signal Quality</option>
    <option value="tb">Turbulence (non dimensional)</option>
    <option value="tbq">Turbulence Quality</option>
    <option value="tbi">Turbulence Intensity</option>
    <option value="pcpn">Precipitation [mm]</option>
</select>

</div><div class="col-md-6">

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


<h4>5) Data Format:</h4>
		
<p>
<select name="format">
	<option value="comma">Comma Delimited</option>
	<option value="excel">Excel (.xlsx)</option>
	<option value="tdf">Tab Delimited</option>
</select></p>

<h4>6) Finally, process request</h4>

  <input type="submit" value="Get Data">
  <input type="reset">

</div></div><!-- ./row -->

 </form>

<br /><br />

EOF;
$t->render('single.phtml');
