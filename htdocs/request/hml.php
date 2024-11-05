<?php
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
require_once "../../include/imagemaps.php";
require_once "../../include/forms.php";
require_once "../../include/iemprop.php";
require_once "../../include/database.inc.php";

define("IEM_APPID", 164);
$t = new MyView();
$t->iemss = True;
$t->title = "Hydrological Markup Language (HML) Processed Data Download";

$bogus = 0;
$y1select = yearSelect2(2012, date("Y"), "year1");
$m1select = monthSelect(1, "month1");
$d1select = daySelect2(1, "day1");

$y2select = yearSelect2(2012, date("Y"), "year2");
$m2select = monthSelect(date("m"), "month2");
$d2select = daySelect2(date("d"), "day2");

$t->content = <<<EOF
<ol class="breadcrumb">
 <li><a href="/nws/">NWS Mainpage</a></li>
 <li class="active">Download HML Processed data</li>
</ol>

<p>The IEM attempts a high fidelity processing and archival of river gauge
observations and forecasts found within the NWS HML Products.</p>

<p><a href="/cgi-bin/request/hml.py?help" class="btn btn-default"><i class="fa fa-file"></i> Backend documentation</a>
exists for those wishing to script against this service. The HML archive dates back to 2012.</p>

<form method="GET" action="/cgi-bin/request/hml.py" name="dl" target="_blank">

<div class="row">
<div class="col-md-6">

<p>
<h3>1. Enter NWSLI Station Identifier:</h3>
At this time, the IEM website does not have a map selection tool to pick from
HML sites.  So you are stuck having to know the 5 character NWSLI identifier,
sorry.
<br /><input type="text" name="station" size="7" maxlength="5">
</p>

<p>
<h3>2. Select Data Type:</h3>
<input type="radio" name="kind" value="obs" checked id="obs">
<label for="obs">Observations</label>
<br />
<input type="radio" name="kind" value="forecasts" id="forecasts">
<label for="forecasts">Forecasts</label>: Note that you can only request
forecast data for a single UTC year at a time.
</p>

</div>
<div class="col-md-6">

<h3>3. Timezone of Observations:</h3>
<i>The timestamps used in the downloaded file will be set in the
timezone you specify.</i>
<SELECT name="tz">
    <option value="UTC">UTC Time</option>
    <option value="America/New_York">Eastern Time</option>
    <option value="America/Chicago">Central Time</option>
    <option value="America/Denver">Mountain Time</option>
    <option value="America/Los_Angeles">Western Time</option>
</SELECT>

<h3>4. Select Start/End Time:</h3><br>
<i>The end date is not inclusive.</i>
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

<h3>5. Data Format:</h3>
<select name="fmt">
    <option value="csv">Comma</option>
    <option value="excel">Excel</option>
</select>

<h3>Submit Form:</h3><br>
<input type="submit" value="Process Data Request">
<input type="reset">

<p><strong>Observation Data Columns</strong>
<table class="table table-striped">
<thead><tr><th>Name</th><th>Description</th></tr></thead>
<tbody>
<tr><th>station</th><td>5 character station identifier</td></tr>
<tr><th>valid[timezone]</th><td>Timestamp of observation</td></tr>
<tr><th><code>Label for Values</code></th><td>Primary</td></tr>
<tr><th><code>Label for Values</code></th><td>Secondary</td></tr>
</tbody>
</table></p>

<p><strong>Observation Data Columns</strong>
<table class="table table-striped">
<thead><tr><th>Name</th><th>Description</th></tr></thead>
<tbody>
<tr><th>station</th><td>5 character station identifier</td></tr>
<tr><th>issued[timezone]</th><td>Timestamp of forecast issuance</td></tr>
<tr><th>primaryname</th><td>Label for the primary forecast value</td></tr>
<tr><th>primaryunits</th><td>Units for the primary forecast value</td></tr>
<tr><th>secondaryname</th><td>Label for the secondary forecast value</td></tr>
<tr><th>secondaryunits</th><td>Units for the secondary forecast value</td></tr>
<tr><th>forecast_valid[timezone]</th><td>Timestamp of forecast valid</td></tr>
<tr><th>primary_value</th><td>Primary forecast value</td></tr>
<tr><th>secondary_value</th><td>Secondary forecast value</td></tr>
</tbody>
</table></p>


</div></div>

</form>

EOF;
$t->render('full.phtml');
