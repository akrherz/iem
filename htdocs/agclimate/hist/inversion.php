<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/myview.php";
$t = new MyView();
$t->title = "ISU Soil Moisture Inversion Data Request";

require_once "../../../include/network.php";
$nt = new NetworkTable("ISUSM");
require_once "../../../include/forms.php";
require_once "../../../include/agclimate_boxinc.phtml";

$yselect = yearSelect(2021, 2021, "year1");
$mselect = monthSelect(1, "month1");
$dselect = daySelect(1, "day1");
$yselect2 = yearSelect(2021, date("Y"), "year2");
$mselect2 = monthSelect(date("m"), "month2");
$dselect2 = daySelect(date("d"), "day2");

$sselect = "";
$sites = array("BOOI4", "CAMI4", "CRFI4");
foreach ($nt->table as $key => $val) {
    if (!in_array($key, $sites)) {
        continue;
    }
    $sselect .= sprintf(
        '<div class="form-check">' .
            '<input class="form-check-input" type="checkbox" name="station" value="%s" id="%s"> ' .
            '<label class="form-check-label" for="%s">[%s] %s (%s County) (2021-%s)</label>' .
        '</div>',
        $key,
        $key,
        $key,
        $key,
        $val["name"],
        $val["county"],
        is_null($val["archive_end"]) ? "today" : $val["archive_end"]->format("Y-m-d"),
    );
}

$t->content = <<<EOM
<nav aria-label="breadcrumb">
<ol class="breadcrumb">
<li class="breadcrumb-item"><a href="/agclimate">ISU Soil Moisture Network</a></li>
<li class="breadcrumb-item active" aria-current="page">Inversion Download</li>
</ol>
</nav>

{$box}

<div class="card mb-4">
<div class="card-header">
<h3 class="mb-0">Minute/Hourly Data</h3>
</div>
<div class="card-body">

<p>The ISU Soil Moisture Network includes three sites that attempt to measure
temperature inversions.  This is accomplished by a temperature sensor at heights
of 1.5, 5, and 10 feet above the ground.</p>

<form name='dl' method="GET" action="/cgi-bin/request/isusm.py">
<input type="hidden" name="mode" value="inversion" />

<div class="row">
<div class="col-md-7">

<div class="mb-4">
<h5>Select station(s):</h5>
<p><a href="/sites/networks.php?network=ISUSM">View station metadata</a></p>

{$sselect}
</div>

</div>
<div class="col-md-5">

<div class="mb-4">
<h5>Select the time interval:</h5>
<div class="table-responsive">
<table class="table table-bordered">
<thead class="table-light">
<tr><th></th><th>Year:</th><th>Month:</th><th>Day:</th></tr>
</thead>
<tbody>
<tr><th>Starting On:</th>
<td>{$yselect}</td>
<td>{$mselect}</td>
<td>{$dselect}</td>
</tr>
<tr><th>Ending On:</th>
<td>{$yselect2}</td>
<td>{$mselect2}</td>
<td>{$dselect2}</td>
</tr>
</tbody>
</table>
</div>
</div>

<div class="card mb-4">
<div class="card-header">
<h5 class="mb-0">Options</h5>
</div>
<div class="card-body">

<div class="form-check mb-3">
<input class="form-check-input" type="checkbox" name="todisk" value="yes" id="dd">
<label class="form-check-label" for="dd">Download directly to disk</label>
</div>

<div class="mb-3">
<label for="format" class="form-label"><strong>How should the data be formatted?:</strong></label>
<select name="format" id="format" class="form-select">
<option value="excel">Microsoft Excel (xlsx)</option>
<option value="comma">Comma Delimited Text File</option>
<option value="tab">Tab Delimited Text File</option>
</select>
</div>

<div class="mb-3">
<label for="missing" class="form-label"><strong>How should missing values be represented?:</strong></label>
<select name="missing" id="missing" class="form-select">
<option value="-99">-99</option>
<option value="M">M</option>
<option value="">(blank, empty space)</option>
</select>
</div>

<div class="mb-3">
<label for="tz" class="form-label"><strong>Timezone for Data:</strong></label>
<select name="tz" id="tz" class="form-select">
<option value="America/Chicago">Central Standard/Daylight Time</option>
<option value="UTC">UTC</option>
</select>
</div>

<div class="mb-3">
<h6><strong>Submit your request:</strong></h6>
<div class="d-flex gap-2">
<input type="submit" value="Submit" class="btn btn-primary">
<input type="reset" value="Reset Form" class="btn btn-secondary">
</div>
</div>

</div>
</div>

</div>
</div>

</form>
</div>
</div>

<div class="card">
<div class="card-header">
<h4 class="mb-0">Description of variables in download</h4>
</div>
<div class="card-body">

<dl class="row">
<dt class="col-sm-3">station</dt>
<dd class="col-sm-9">National Weather Service Location Identifier for the
site. This is a five character identifier.</dd>
<dt class="col-sm-3">valid</dt>
<dd class="col-sm-9">Timestamp of the observation</dd>
<dt class="col-sm-3">tair_15</dt>
<dd class="col-sm-9">Air Temperature (F) at 1.5ft above the ground</dd>
<dt class="col-sm-3">tair_5</dt>
<dd class="col-sm-9">Air Temperature (F) at 5ft above the ground</dd>
<dt class="col-sm-3">tair_10</dt>
<dd class="col-sm-9">Air Temperature (F) at 10ft above the ground</dd>
<dt class="col-sm-3">speed</dt>
<dd class="col-sm-9">Wind Speed (mph) at 10ft above the ground</dd>
<dt class="col-sm-3">gust</dt>
<dd class="col-sm-9">Wind Gust (mph) at 10ft above the ground</dd>
</dl>

</div>
</div>

EOM;
$t->render("full.phtml");
