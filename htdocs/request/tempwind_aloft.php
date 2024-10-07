<?php
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
require_once "../../include/imagemaps.php";
require_once "../../include/forms.php";
require_once "../../include/iemprop.php";
require_once "../../include/database.inc.php";

define("IEM_APPID", 30);
$t = new MyView();
$t->iemss = True;
$t->title = "Temps and Winds Aloft (FD) Data Download";

$bogus = 0;
$y1select = yearSelect2(2004, date("Y"), "year1");
$m1select = monthSelect(1, "month1");
$d1select = daySelect2(1, "day1");

$y2select = yearSelect2(2004, date("Y"), "year2");
$m2select = monthSelect(date("m"), "month2");
$d2select = daySelect2(date("d"), "day2");

$pgconn = iemdb("asos");
$sql = <<<EOM
with data as (
    select distinct station from alldata_tempwind_aloft WHERE
    ftime > (now() - '5 days'::interval)
    )
select station, name from data d LEFT JOIN stations t on
((case when substr(d.station, 1, 1) = 'K' then substr(d.station, 2, 3)
 else d.station end) = t.id) ORDER by station ASC
EOM;
$rs = pg_query($pgconn, $sql);
$sids = Array();
for ($i = 0; $row = pg_fetch_array($rs); $i++) {
    $name = is_null($row["name"]) ? "((Unknown))": $row["name"];
    $sids[$row["station"]] = $name;
}
$sselect = make_select("station", "KDSM", $sids, '', '', FALSE, TRUE);

$t->content = <<<EOF
<ol class="breadcrumb">
 <li><a href="/nws/">NWS Mainpage</a></li>
 <li class="active">Download Temps and Winds Aloft (FD) Data</li>
</ol>

<p>This page allows for download of raw data found within products like this:
<a href="/wx/afos/p.php?pil=FD1US1">FD1US1</a>.  They contain
near term forecasts of temperatures and wind speed aloft.  More details on the 
product can be found with the <a href="https://weather.gov/directives/sym/pd01008012curr.pdf">NWS Directive 10-812</a>.</p>

<p><a href="/cgi-bin/request/tempwind_aloft.py?help" class="btn btn-default">
<i class="fa fa-file"></i> Backend documentation</a> exists for those wishing to script against this
service. The archive dates back to 23 September 2004.</p>

<p><strong>Related:</strong>
<a class="btn btn-primary" href="/request/gis/cwas.phtml">CWSU Center Weather Advisories</a>
<a class="btn btn-primary" href="/request/gis/awc_gairmets.phtml">Graphical AIRMETs</a>
<a class="btn btn-primary" href="/request/gis/pireps.php">PIREPs</a>
<a class="btn btn-primary" href="/request/gis/awc_sigmets.phtml">SIGMETs</a>
</p>

<form method="GET" action="/cgi-bin/request/tempwind_aloft.py" name="dl" target="_blank">

<div class="row">
<div class="col-md-6">

<p><h3>1. Select Station:</h3><br>
{$sselect}

<p><strong>Returned Columns</strong>

<table>
<thead><tr><th>column</th><th>Description</th></tr></thead>
<tbody>
<tr><td>obtime</td><td>The timestamp within the FD product by which the forecast
is said to be based off.</td></tr>
<tr><td>ftime</td><td>The timestamp the values are valid for / forecast timestamp</td></tr>
<tr><td>tmpc#####</td><td>Air Temperature (&deg;C) at given altitude</td></tr> 
<tr><td>sknt#####</td><td>Wind Speed (kts) at given altitude</td></tr> 
<tr><td>drct#####</td><td>Wind Direction (&deg;) at given altitude</td></tr> 
</tbody>
</table>
</p>

</div>
<div class="col-md-6">

<h3>2. Timezone of Observations:</h3>
<i>The timestamps used in the downloaded files will be set in the
timezone you specify.</i>
<SELECT name="tz">
    <option value="UTC">UTC Time</option>
    <option value="America/New_York">Eastern Time</option>
    <option value="America/Chicago">Central Time</option>
    <option value="America/Denver">Mountain Time</option>
    <option value="America/Los_Angeles">Western Time</option>
</SELECT>

<h3>3. Select Start/End Time:</h3><br>
<i>This limits the data returned for forecast times between the start
and end date.</i>
<table class="table table-condensed">
<thead>
  <tr>
    <td></td>
    <th>Year</th><th>Month</th><th>Day</th>
  </tr>
</thead>
<tbody>
  <tr>
    <th>Start:</th>
    <td>{$y1select}</td><td>{$m1select}</td><td>{$d1select}</td>
  </tr>

  <tr>
    <th>End:</th>
    <td>{$y2select}</td><td>{$m2select}</td><td>{$d2select}</td>
  </tr>
</tbody>
</table>

<h3>4. Data Format:</h3>
<select name="format">
    <option value="csv">Comma</option>
    <option value="excel">Excel</option>
</select>

<h3>Submit Form:</h3><br>
<input type="submit" value="Process Data Request">
<input type="reset">

</div></div>

</form>

EOF;
$t->render('full.phtml');
