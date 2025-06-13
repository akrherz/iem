<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/myview.php";
require_once "../../../include/network.php";
require_once "../../../include/forms.php";

$t = new MyView();
$t->iem_resource = "ISUSM";
$t->title = "ISU Soil Moisture Minute/Hourly Data Request";

$nt = new NetworkTable("ISUSM");
require_once "boxinc.phtml";

$yselect = yearSelect(2013, 2013, "year1");
$mselect = monthSelect(1, "month1");
$dselect = daySelect(1, "day1");
$yselect2 = yearSelect(2013, date("Y"), "year2");
$mselect2 = monthSelect(date("m"), "month2");
$dselect2 = daySelect(date("d"), "day2");

$sselect = "";
foreach ($nt->table as $key => $val) {
    $sselect .= sprintf(
        '<div class="form-check">' .
            '<input class="form-check-input" type="checkbox" name="station" value="%s" id="%s"> ' .
            '<label class="form-check-label" for="%s">[%s] %s (%s County) (%s-%s)</label>' .
        '</div>',
        $key,
        $key,
        $key,
        $key,
        $val["name"],
        $val["county"],
        is_null($val["archive_begin"]) ? "" : $val["archive_begin"]->format("Y-m-d"),
        is_null($val["archive_end"]) ? "today" : $val["archive_end"]->format("Y-m-d"),
    );
}

$ar = array(
    "tmpf" => "Air Temperature [F]",
    "relh" => "Relative Humidity [%]",
    "solar" => "Solar Radiation [J/m2]",
    "precip" => "Precipitation [inch]",
    "speed" => "Average Wind Speed [mph]",
    "drct" => "Wind Direction [deg]",
    "et" => "Potential Evapotranspiration [inch]",
    "soil04t" => "4 inch Soil Temperature [F]",
    "soil12t" => "12 inch Soil Temperature [F]",
    "soil24t" => "24 inch Soil Temperature [F]",
    "soil50t" => "50 inch Soil Temperature [F]",
    "soil12vwc" => "12 inch Soil Moisture [%]",
    "soil24vwc" => "24 inch Soil Moisture [%]",
    "soil50vwc" => "50 inch Soil Moisture [%]",
    "bp_mb" => "Atmospheric Pressure [mb] (only Ames ISU Hort Farm at 15 minute interval)",
);
$vselect = make_checkboxes("vars", "", $ar);

$ar = array(
    "lwmv_1" => "lwmv_1",
    "lwmv_2" => "lwmv_2",
    "lwmdry_1_tot" => "lwmdry_1_tot",
    "lwmcon_1_tot" => "lwmcon_1_tot",
    "lwmwet_1_tot" => "lwmwet_1_tot",
    "lwmdry_2_tot" => "lwmdry_2_tot",
    "lwmcon_2_tot" => "lwmcon_2_tot",
    "lwmwet_2_tot" => "lwmwet_2_tot",
    "bpres_avg" => "bpres_avg",
);
$vselect2 = make_checkboxes("vars", "", $ar);

$t->content = <<<EOM
<nav aria-label="breadcrumb">
<ol class="breadcrumb">
<li class="breadcrumb-item"><a href="/agclimate">ISU Soil Moisture Network</a></li>
<li class="breadcrumb-item active" aria-current="page">Minute/Hourly Download</li>
</ol>
</nav>

{$box}

<div class="card mb-4">
<div class="card-header">
<h3 class="mb-0">Minute/Hourly Data</h3>
</div>
<div class="card-body">

<p>The present data collection interval from this network is every 15 minutes
for the vineyard sites and every minute for the others. The minute interval
data only started in 2021 though. The default download is to provide the
hourly data.</p>

<p><a href="/cgi-bin/request/isusm.py?help" class="btn btn-info">
<i class="fa fa-file"></i> Backend documentation</a> exists for those
wishing to script against this data service.</p>

<form name='dl' method="GET" action="/cgi-bin/request/isusm.py">
<input type="hidden" name="mode" value="hourly" />

<div class="row">
<div class="col-md-7">

<div class="mb-4">
<h5>Select Time Resolution:</h5>
<select name="timeres" class="form-select">
<option value="hourly" selected="selected">Hourly</option>
<option value="minute">Minute</option>
</select>
</div>

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
<h5 class="mb-0">Variables</h5>
</div>
<div class="card-body">

<div class="mb-3">
<strong>Select from available variables</strong><br />
<small><a href="/agclimate/et.phtml" target="_new">Reference Evapotranspiration (alfalfa)</a></small>
</div>

{$vselect}

<hr>

<div class="mb-3">
<p>The Ames-AEA, Ames-Kitchen, Ames-Hinds, and Jefferson locations have the
<a href="https://www.campbellsci.com/soilvue10">CS SoilVue 10</a> installed,
but the depth of installation varies by site with the first depth at
the Ames-AEA location being at 14 inches.</p>

<div class="form-check mb-3">
<input class="form-check-input" type="checkbox" name="vars" value="sv" id="sv">
<label class="form-check-label" for="sv">All SoilVue Temperature + Moisture Data</label>
</div>

<div class="mb-2"><strong>or</strong> select from the following depths:</div>

<div class="row">
<div class="col-md-4">
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="sv2" id="sv2">
<label class="form-check-label" for="sv2">2 inch</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="sv12" id="sv12">
<label class="form-check-label" for="sv12">12 inch</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="sv20" id="sv20">
<label class="form-check-label" for="sv20">20 inch</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="sv30" id="sv30">
<label class="form-check-label" for="sv30">30 inch</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="sv40" id="sv40">
<label class="form-check-label" for="sv40">40 inch</label>
</div>
</div>

<div class="col-md-4">
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="sv4" id="sv4">
<label class="form-check-label" for="sv4">4 inch</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="sv14" id="sv14">
<label class="form-check-label" for="sv14">14 inch</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="sv24" id="sv24">
<label class="form-check-label" for="sv24">24 inch</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="sv32" id="sv32">
<label class="form-check-label" for="sv32">32 inch</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="sv42" id="sv42">
<label class="form-check-label" for="sv42">42 inch</label>
</div>
</div>

<div class="col-md-4">
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="sv8" id="sv8">
<label class="form-check-label" for="sv8">8 inch</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="sv16" id="sv16">
<label class="form-check-label" for="sv16">16 inch</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="sv28" id="sv28">
<label class="form-check-label" for="sv28">28 inch</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="sv36" id="sv36">
<label class="form-check-label" for="sv36">36 inch</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="sv52" id="sv52">
<label class="form-check-label" for="sv52">52 inch</label>
</div>
</div>
</div>
</div>

<hr>

<div class="mb-3">
<strong>Vineyard Station-only Variables</strong>
{$vselect2}
</div>

{$qcbox}

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
<dd class="col-sm-9">Timestamp of the observation either in CST or CDT</dd>
<dt class="col-sm-3">tmpf</dt>
<dd class="col-sm-9">Air Temperature [F]</dd>
<dt class="col-sm-3">relh</dt>
<dd class="col-sm-9">Relative Humidity [%]</dd>
<dt class="col-sm-3">solar</dt>
<dd class="col-sm-9">Solar Radiation [Joule/m2]</dd>
<dt class="col-sm-3">precip</dt>
<dd class="col-sm-9">One Hour Precipitation [inch]</dd>
<dt class="col-sm-3">speed</dt>
<dd class="col-sm-9">Wind Speed [mph], 10 minute average, 10 ft above ground</dd>
<dt class="col-sm-3">drct</dt>
<dd class="col-sm-9">Wind Direction [degrees North], 10 minute average, 10 ft above ground</dd>
<dt class="col-sm-3">et</dt>
<dd class="col-sm-9">Potential Evapotranspiration (Alfalfa) [inch]</dd>
<dt class="col-sm-3">soil04t</dt>
<dd class="col-sm-9">4 inch Depth Soil Temperature [F]</dd>
<dt class="col-sm-3">soil12t</dt>
<dd class="col-sm-9">12 inch Depth Soil Temperature [F]</dd>
<dt class="col-sm-3">soil24t</dt>
<dd class="col-sm-9">24 inch Depth Soil Temperature [F]</dd>
<dt class="col-sm-3">soil50t</dt>
<dd class="col-sm-9">50 inch Depth Soil Temperature [F]</dd>
<dt class="col-sm-3">soil12vwc</dt>
<dd class="col-sm-9">12 inch Depth Soil Volumetric Water Content [%]</dd>
<dt class="col-sm-3">soil24vwc</dt>
<dd class="col-sm-9">24 inch Depth Soil Volumetric Water Content [%]</dd>
<dt class="col-sm-3">soil50vwc</dt>
<dd class="col-sm-9">50 inch Depth Soil Volumetric Water Content [%]</dd>
</dl>

</div>
</div>

EOM;
$t->render("full.phtml");
