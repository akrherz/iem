<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/myview.php";
$t = new MyView();
$t->title = "ISU Soil Moisture Inversion Data Request";

require_once "../../../include/network.php";
$nt = new NetworkTable("ISUSM");
require_once "../../../include/forms.php";
require_once "boxinc.phtml";

$yselect = yearSelect2(2021, 2021, "year1");
$mselect = monthSelect(1, "month1");
$dselect = daySelect2(1, "day1");
$yselect2 = yearSelect2(2021, date("Y"), "year2");
$mselect2 = monthSelect(date("m"), "month2");
$dselect2 = daySelect2(date("d"), "day2");

$sselect = "";
$sites = array("BOOI4", "CAMI4", "CRFI4");
foreach ($nt->table as $key => $val) {
    if (!in_array($key, $sites)) {
        continue;
    }
    $sselect .= sprintf(
        '<br /><input type="checkbox" name="station" value="%s" id="%s"> ' .
            '<label for="%s">[%s] %s (%s County) (2021-%s)</label>',
        $key,
        $key,
        $key,
        $key,
        $val["name"],
        $val["county"],
        is_null($val["archive_end"]) ? "today" : $val["archive_end"]->format("Y-m-d"),
    );
}

$t->content = <<<EOF
 <ol class="breadcrumb">
  <li><a href="/agclimate">ISU Soil Moisture Network</a></li>
  <li class="active">Inversion Download</li>
 </ol>

{$box}

<h3>Minute/Hourly Data:</h3>

<p>The ISU Soil Moisture Network includes three sites that attempt to measure
temperature inversions.  This is accomplished by a temperature sensor at heights
of 1.5, 5, and 10 feet above the ground.</p>

<div class="row">
<div class="col-md-7">

<form name='dl' method="GET" action="/cgi-bin/request/isusm.py">
<input type="hidden" name="mode" value="inversion" />

<h4>Select station(s):</h4>
<a href="/sites/networks.php?network=ISUSM">View station metadata</a><br />

{$sselect}

</div><div class="col-md-5">

<h4>Select the time interval:</h4>
<table>
  <tr><th></th><th>Year:</th><th>Month:</th><th>Day:</th></tr>
  <tr><th>Starting On:</th>
 <td>{$yselect}</td>
 <td>{$mselect}</td>
 <td>{$dselect}</td>
 </tr>
</tr>
<tr><th>Ending On:</th>
 <td>{$yselect2}</td>
 <td>{$mselect2}</td>
 <td>{$dselect2}</td>
</tr>
</table>

<p>
<input type="checkbox" name="todisk" value="yes" id="dd">
<label for="dd">Download directly to disk</label>
</p>

 <p><strong>How should the data be formatted?:</strong> &nbsp; 
<select name="format">
    <option value="excel">Microsoft Excel (xlsx)</option>
    <option value="comma">Comma Delimited Text File</option>
      <option value="tab">Tab Delimited Text File</option>
</select>

<p><strong>How should missing values be represented?:</strong>
<br /> 
<select name="missing">
    <option value="-99">-99</option>
    <option value="M">M</option>
      <option value="">(blank, empty space)</option>
</select>

<p><strong>Timezone for Data:</strong>
<br />
<select name="tz">
    <option value="America/Chicago">Central Standard/Daylight Time</option>
    <option value="UTC">UTC</option>
</select></p>

<p><strong>Submit your request:</strong>
<br />
    <input type="submit" value="Submit">
    <input type="reset">

</form>

</div></div>

<h4>Description of variables in download</h4>

<dl>
<dt>station</dt><dd>National Weather Service Location Identifier for the
site.  this is a five character identifier.</dd>
<dt>valid</dt><dd>Timestamp of the observation/dd>
<dt>tair_15</dt><dd>Air Temperature (F) at 1.5ft above the ground</dd>
<dt>tair_5</dt><dd>Air Temperature (F) at 5ft above the ground</dd>
<dt>tair_10</dt><dd>Air Temperature (F) at 10ft above the ground</dd>
<dt>speed</dt><dd>Wind Speed (mph) at 10ft above the ground</dd>
<dt>gust</dt><dd>Wind Gust (mph) at 10ft above the ground</dd>
</dl>

EOF;
$t->render("full.phtml");
