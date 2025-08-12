<?php
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
require_once "../../include/forms.php";
require_once "../../include/iemprop.php";
require_once "../../include/database.inc.php";

define("IEM_APPID", 139);
$t = new MyView();
$t->iemss = True;
$t->title = "Terminal Aerodome Forecast (TAF) Data Download";

$bogus = 0;
$y1select = yearSelect(1996, date("Y"), "year1");
$m1select = monthSelect(1, "month1");
$d1select = daySelect(1, "day1");
$min1select = minuteSelect(0, "minute1");
$hour1select = hourSelect(0, "hour1");

$y2select = yearSelect(1996, date("Y"), "year2");
$m2select = monthSelect(date("m"), "month2");
$d2select = daySelect(date("d"), "day2");
$min2select = minuteSelect(0, "minute2");
$hour2select = hourSelect(0, "hour2");

$t->headextra = <<<EOM
<link rel="stylesheet" type="text/css" href="taf.css">
EOM;
$t->content = <<<EOM
<nav aria-label="breadcrumb" class="mb-3">
  <ol class="breadcrumb">
    <li class="breadcrumb-item"><a href="/nws/">NWS Mainpage</a></li>
    <li class="breadcrumb-item active" aria-current="page">Download TAF data</li>
  </ol>
</nav>

<p>The IEM attempts a high fidelity processing and archival of Terminal
Aerodome Forecasts (TAF)s.  This page allows an atomic data download of the
processed data.  If you are wishing to download the raw NWS text TAF data,
try looking <a href="/wx/afos/p.php?pil=TAFDSM">here</a> as a starting point.</p>

<p><a href="/cgi-bin/request/taf.py?help" class="btn btn-secondary"><i class="fa fa-file"></i> Backend documentation</a>
exists for those wishing to script against this service. The TAF archive dates back to 1 January 1996.</p>

<p><strong>Related:</strong>
<a class="btn btn-primary" href="/request/gis/cwas.phtml">CWSU Center Weather Advisories</a>
<a class="btn btn-primary" href="/request/gis/awc_gairmets.phtml">Graphical AIRMETs</a>
<a class="btn btn-primary" href="/request/gis/pireps.php">PIREPs</a>
<a class="btn btn-primary" href="/request/gis/awc_sigmets.phtml">SIGMETs</a>
<a class="btn btn-primary" href="/request/tempwind_aloft.php">Temp/Winds Aloft</a>
</p>

<form method="GET" action="/cgi-bin/request/taf.py" name="dl" target="_blank">
<div class="form2url"></div>

<div class="row">
<div class="col-md-6">

<p><h3>1. Select Station:</h3><br>
<br />
<div id="iemss" data-network="TAF" data-name="station" data-supports-all="0"></div>

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
<i>This defines the time domain to look for TAFs <strong>issued</strong>
within.</i>
<table class="table table-sm">
<thead>
  <tr>
    <td></td>
    <th>Year</th><th>Month</th><th>Day</th><th>Hour</th><th>Minute</th>
  </tr>
</thead>
<tbody>
  <tr>
    <th>Start:</th>
    <td>{$y1select}</td><td>{$m1select}</td><td>{$d1select}</td>
    <td>{$hour1select}</td><td>{$min1select}</td>
  </tr>

  <tr>
    <th>End:</th>
    <td>{$y2select}</td><td>{$m2select}</td><td>{$d2select}</td>
    <td>{$hour2select}</td><td>{$min2select}</td>
  </tr>
</tbody>
</table>

<h3>4. Data Format:</h3>
<select name="fmt">
    <option value="comma">Comma</option>
    <option value="excel">Excel</option>
</select>

<h3>5. Filter to last TAF per station:</h3>
<input type="checkbox" name="last" value="1" id="last">
<label for="last">Only include the last TAF for each station</label>

<h3>Submit Form:</h3><br>
<input type="submit" value="Process Data Request">
<input type="reset">

<p><strong>Data Columns</strong>
<table class="table table-striped">
<thead><tr><th>Name</th><th>Description</th></tr></thead>
<tbody>
<tr><th>station</th><td>4 character station identifier</td></tr>
<tr><th>valid</th><td>TAF issuance timestamp</td></tr>
<tr><th>fx_valid</th><td>Forecast Timestamp</td></tr>
<tr><th>raw</th><td>Raw TAF string for this forecast time</td></tr>
<tr><th>fx_end_valid</th><td>Forecast timestamp end time (when set).</td></tr>
<tr><th>sknt</th><td>Wind Speed (kts)</td></tr>
<tr><th>drct</th><td>Wind Direction (deg)</td></tr>
<tr><th>gust</th><td>Wind Gust (kts)</td></tr>
<tr><th>visibility</th><td>Horizontal Visibility (miles). <strong>Note</strong> 
Greater than 6 miles is encoded as 6.01</td></tr>
<tr><th>skyc</th><td>Sky Coverages</td></tr>
<tr><th>skyl</th><td>Sky Coverage Levels (feet)</td></tr>
<tr><th>ws_drct</th><td>Wind Shift Direction (deg)</td></tr>
<tr><th>ws_sknt</th><td>Wind Shift Wind Speed (kts)</td></tr>
<tr><th>product_id</th><td>IEM NWS Text Product Identifier</td></tr>
<tr><th>ftype</th><td>Forecast Type: Observation, "FM" Forecast,
 "BECMG" Becoming, "PROB30" Probability 30, "PROB40" Probability 40, or
 "TEMPO" Temporary</td></tr>
</tbody>
</table>

</div></div>

</form>

EOM;
$t->render('full.phtml');
